#!/usr/bin/env python3
"""Calibration 3: measure the rung-to-node-count curve, then select size bins.

`C(s)` is always a rung of `EDGE_COUNT_LADDER`, so `size_class` is in effect a
function of which rung was selected. But `phi` bins on the fraction of the 156
model components a circuit touches, not on edges, and the map from a rung to the
node count its edges touch is empirical. The bins cannot be reasoned out. An
earlier attempt to reason them out anchored to the edge count instead of the node
count, reached both the pre-registration and the test suite, and would have kept
passing while checking nothing.

The selection rule is `p1.claim_map.select_size_bins`, committed before this ran.
This script measures the curve, applies the rule, and prints the result. It does
not decide anything.

**It also prints a sanity table of real nodes.** Two bugs were found in the
auto-circuit seam on 2026-08-06, an off-by-one in `block_index` and the residual
terminals being mapped as MLPs, and both passed their unit tests because the
tests were written from the same derivation as the code. Stubs cannot catch that.
The table is the check against the library's actual nodes.

Outputs are not confirmatory. The manifest carries `confirmatory: false` and the
circuits are used for one statistic and then discarded.

Usage:
    python3 scripts/calibrate_nodes.py --config configs/calib-nodes.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean, pstdev

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def peak_rss_mb() -> float:
    import resource

    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw / (1024 * 1024) if sys.platform == "darwin" else raw / 1024


def ranked_edges(pmodel, prune_scores):
    """Every edge, ordered by descending |prune score|, deterministically.

    Ties are broken by edge name so the ordering does not depend on set iteration
    order. Without that, two runs of the identical specification could return
    different top-k sets purely from hashing, which would show up as instability
    the paper would then have to explain.
    """
    scored = []
    for edge in pmodel.edges:
        scored.append((abs(float(edge.prune_score(prune_scores))), str(edge), edge))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [e for _, _, e in scored]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    import yaml

    cfg = yaml.safe_load(args.config.read_text())
    if cfg.get("confirmatory") is not False:
        raise SystemExit("refusing to run: config must set `confirmatory: false`")

    out_dir = args.out or (REPO / cfg["output"]["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    timings: dict[str, float] = {}
    notes: list[str] = []
    status = "ok"
    results: dict = {}

    t0 = time.perf_counter()
    import torch as t
    from auto_circuit.data import load_datasets_from_json
    from auto_circuit.experiment_utils import load_tl_model
    from auto_circuit.prune_algos.mask_gradient import mask_gradient_prune_scores
    from auto_circuit.types import AblationType
    from auto_circuit.utils.graph_utils import patchable_model

    from p1.claim_map import select_size_bins
    from p1.features import components_from_nodes
    from p1.manifest import Manifest
    from p1.prompts import generate_ioi_dataset, write_dataset_json
    from p1.spec import EDGE_COUNT_LADDER

    timings["import_s"] = round(time.perf_counter() - t0, 3)

    dev = cfg["model"]["device"]
    if dev == "auto":
        dev = "cuda" if t.cuda.is_available() else "cpu"
    device = t.device(dev)
    notes.append(f"device={dev}")
    if dev == "cuda":
        notes.append(f"gpu={t.cuda.get_device_name(0)}")

    shape = cfg["model_shape"]
    n_blocks = int(shape["n_blocks"])
    n_heads = int(shape["n_heads_per_block"])
    n_full = n_blocks * n_heads + n_blocks

    calib = cfg["calibration"]
    seeds = list(calib["seeds"])
    ladder = list(EDGE_COUNT_LADDER)

    try:
        t0 = time.perf_counter()
        model = load_tl_model(cfg["model"]["name"], device)
        timings["model_load_s"] = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        pmodel = patchable_model(
            model,
            factorized=True,
            slice_output="last_seq",
            separate_qkv=True,
            device=device,
        )
        timings["patchable_model_s"] = round(time.perf_counter() - t0, 3)
        notes.append(f"n_edges={len(pmodel.edges)}")

        spec = cfg["specification"]
        n_disc = cfg["task"]["n_prompts"] // 2
        per_seed: dict[int, list[int]] = {}
        sanity_printed = False

        for seed in seeds:
            t_seed = time.perf_counter()
            ds = generate_ioi_dataset(
                n_prompts=cfg["task"]["n_prompts"],
                seed=seed,
                order=cfg["task"]["order"],
                corruption=cfg["task"]["corruption"],
            )
            ds_path = write_dataset_json(ds, out_dir / f"prompts_s{seed}.json")
            train_loader, _ = load_datasets_from_json(
                model=model,
                path=ds_path,
                device=device,
                batch_size=cfg["task"]["batch_size"],
                train_test_size=(n_disc, n_disc),
                random_seed=seed,
            )
            ps = mask_gradient_prune_scores(
                model=pmodel,
                dataloader=train_loader,
                official_edges=None,
                grad_function=spec["grad_function"],
                answer_function=spec["answer_function"],
                ablation_type=AblationType[spec["ablation"]],
                mask_val=spec.get("mask_val"),
                integrated_grad_samples=spec.get("integrated_grad_samples"),
            )
            order = ranked_edges(pmodel, ps)

            if not sanity_printed:
                rows = int(calib.get("sanity_rows", 20))
                print("\n=== sanity: top edges as the seam maps them ===")
                print(f"{'src':<22}{'L':>4}{'h':>4}  ->  {'dest':<22}{'L':>4}{'h':>4}"
                      f"   {'components'}")
                for e in order[:rows]:
                    comps = sorted(components_from_nodes([e.src, e.dest]))
                    cs = " ".join(f"{c.kind[0]}{c.layer}.{c.index}" for c in comps)
                    print(
                        f"{e.src.name:<22}{e.src.layer:>4}"
                        f"{'-' if e.src.head_idx is None else e.src.head_idx:>4}"
                        f"  ->  {e.dest.name:<22}{e.dest.layer:>4}"
                        f"{'-' if e.dest.head_idx is None else e.dest.head_idx:>4}"
                        f"   {cs}"
                    )
                print()
                sanity_printed = True

            counts = []
            for k in ladder:
                nodes = []
                for e in order[:k]:
                    nodes.append(e.src)
                    nodes.append(e.dest)
                comps = components_from_nodes(nodes)
                for c in comps:
                    if not 0 <= c.layer < n_blocks:
                        raise RuntimeError(
                            f"component {c} outside [0, {n_blocks}); the "
                            f"auto-circuit seam is wrong, not the data"
                        )
                counts.append(len(comps))
            per_seed[seed] = counts
            timings[f"seed_{seed}_s"] = round(time.perf_counter() - t_seed, 3)

        curve = []
        for i, k in enumerate(ladder):
            vals = [per_seed[s][i] for s in seeds]
            curve.append(
                {
                    "rung": k,
                    "nodes_mean": round(mean(vals), 3),
                    "nodes_sd": round(pstdev(vals), 3) if len(vals) > 1 else 0.0,
                    "nodes_min": min(vals),
                    "nodes_max": max(vals),
                    "frac_mean": round(mean(vals) / n_full, 6),
                }
            )

        fracs = [c["frac_mean"] for c in curve]
        bins = select_size_bins(fracs)

        results = {
            "n_components_full_model": n_full,
            "ladder": ladder,
            "curve": curve,
            "per_seed_counts": {str(s): per_seed[s] for s in seeds},
            "selected_bins": None if bins is None else [[b, n] for b, n in bins],
            "degenerate": bins is None,
        }
        if bins is None:
            notes.append(
                "size_class is DEGENERATE: neither 3 nor 2 bins separates the "
                "ladder under the committed constraints. Report in the abstract."
            )

    except Exception as exc:  # noqa: BLE001
        status = "failed"
        notes.append(f"{type(exc).__name__}: {exc}")

    man = Manifest(
        kind="calib-nodes",
        spec_id="calib-nodes",
        config=cfg,
        seeds={"first": min(seeds)},
        timings_s=timings,
        peak_rss_mb=round(peak_rss_mb(), 1),
        notes=" | ".join(notes),
        status=status,
    )
    man_path = man.write(out_dir / "manifest.json")
    (out_dir / "curve.json").write_text(json.dumps(results, indent=2, sort_keys=True))

    print(f"status: {status}")
    for k, v in sorted(timings.items()):
        print(f"  {k:28s} {v}")
    if status == "ok":
        print()
        print(f"  {'rung':>6} {'nodes':>12} {'sd':>7} {'frac':>8}")
        for c in results["curve"]:
            print(
                f"  {c['rung']:>6} {c['nodes_mean']:>12.1f} {c['nodes_sd']:>7.2f}"
                f" {c['frac_mean']:>8.4f}"
            )
        print()
        if results["degenerate"]:
            print("  SELECTED: none. size_class is degenerate.")
        else:
            print(f"  SELECTED BINS ({len(results['selected_bins'])}):")
            for b, n in results["selected_bins"]:
                print(f"    {n:<14} up to {b:.6g}")
    if notes:
        print()
        for n in notes:
            print(f"  note: {n}")
    print(f"manifest: {man_path}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
