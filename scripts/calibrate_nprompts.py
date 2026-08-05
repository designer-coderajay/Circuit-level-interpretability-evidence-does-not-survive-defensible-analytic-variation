#!/usr/bin/env python3
"""Calibration 1: select `n_prompts` by the rule committed in CALIBRATION.md.

The question this answers is not "how much can we afford". Seed variance has two
sources the design cannot separate after the fact: sampling noise, which shrinks
with dataset size, and genuine instability of discovery under a fixed analytic
specification. Only the second is of interest to the paper. Run the confirmatory
grid at smoke size and the headline seed-versus-analytic variance ratio is
inflated by a quantity that has nothing to do with the claim.

So this measures, for each candidate dataset size, how much two runs of the
identical specification agree when only the prompt sample differs, and picks the
smallest size at which doubling the data stops buying agreement.

**The rule is fixed in preregistration/CALIBRATION.md and was committed before
this script was run. Nothing here may deviate from it.** In particular `n` is
never lowered because the resulting budget is inconvenient.

Outputs are not confirmatory. Every manifest carries `confirmatory: false` and
`kind="calib-nprompts"`, and no circuit produced here is retained.

Usage:
    python3 scripts/calibrate_nprompts.py --config configs/calib-nprompts.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def peak_rss_mb() -> float:
    """Peak RSS in MB. macOS reports ru_maxrss in bytes, Linux in kilobytes."""
    import resource

    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw / (1024 * 1024) if sys.platform == "darwin" else raw / 1024


def circuit_from_prune_scores(prune_scores, top_k: int) -> frozenset:
    """The top `top_k` edges as a set of (module_name, flat_index) pairs.

    Uses auto-circuit's own `prune_scores_threshold` rather than a hand-rolled
    top-k, so the cut matches how the instrument itself selects edges. Ties at
    the threshold can yield slightly more than `top_k` edges; the realised size
    is returned and reported rather than silently trimmed, because trimming would
    be a tie-break rule this pilot has not pre-registered.
    """
    import torch as t
    from auto_circuit.utils.tensor_ops import prune_scores_threshold

    thresh = prune_scores_threshold(prune_scores, top_k)
    edges = set()
    for name in sorted(prune_scores.keys()):  # sorted: determinism
        flat = prune_scores[name].flatten().abs()
        for idx in t.nonzero(flat >= thresh, as_tuple=False).flatten().tolist():
            edges.add((name, int(idx)))
    return frozenset(edges)


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

    calib = cfg["calibration"]
    sizes = list(calib["discovery_prompts"])
    seeds = list(calib["seeds"])
    top_k = int(calib["top_k_edges"])
    flatten = float(calib["flatten_threshold"])

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

    from p1.manifest import Manifest
    from p1.multiverse import jaccard_similarity
    from p1.prompts import generate_ioi_dataset, write_dataset_json

    timings["import_s"] = round(time.perf_counter() - t0, 3)

    dev = cfg["model"]["device"]
    if dev == "auto":
        dev = "cuda" if t.cuda.is_available() else "cpu"
    device = t.device(dev)

    try:
        t0 = time.perf_counter()
        # load_tl_model, not a hand-rolled HookedTransformer.from_pretrained. It
        # sets fold_ln, center_writing_weights and center_unembed, which rewrite
        # the weights. A hand-rolled loader produces different circuits with
        # nothing raising. Reproducing the instrument includes reproducing how it
        # prepares its input.
        model = load_tl_model(cfg["model"]["name"], device)
        timings["model_load_s"] = round(time.perf_counter() - t0, 3)

        # Data-independent, so built once and reused across all 32 discoveries.
        t0 = time.perf_counter()
        pmodel = patchable_model(
            model,
            factorized=True,
            slice_output="last_seq",
            separate_qkv=True,
            device=device,
        )
        timings["patchable_model_s"] = round(time.perf_counter() - t0, 3)

        spec = cfg["specification"]
        j_seed: dict[int, float] = {}

        for n in sizes:
            circuits: dict[int, frozenset] = {}
            sizes_seen: list[int] = []
            t_size = time.perf_counter()

            for seed in seeds:
                # Total dataset is 2n, split evenly. Discovery runs on train.
                ds = generate_ioi_dataset(
                    n_prompts=2 * n, seed=seed, order=cfg["task"]["order"]
                )
                ds_path = write_dataset_json(ds, out_dir / f"prompts_n{n}_s{seed}.json")
                # Raw model, not pmodel: this matches scripts/smoke.py, which
                # loads data before wrapping. The model is used here only for
                # tokenisation, but diverging from the established call pattern
                # is exactly the kind of silent difference that produced the
                # hand-rolled-loader bug on 08-04.
                train_loader, _ = load_datasets_from_json(
                    model=model,
                    path=ds_path,
                    device=device,
                    batch_size=cfg["task"]["batch_size"],
                    train_test_size=(n, n),
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
                c = circuit_from_prune_scores(ps, top_k)
                circuits[seed] = c
                sizes_seen.append(len(c))

            pairs = list(combinations(seeds, 2))
            sims = [jaccard_similarity(circuits[a], circuits[b]) for a, b in pairs]
            j_seed[n] = sum(sims) / len(sims)

            results[str(n)] = {
                "j_seed_mean": round(j_seed[n], 6),
                "j_seed_min": round(min(sims), 6),
                "j_seed_max": round(max(sims), 6),
                "n_pairs": len(pairs),
                "realised_circuit_sizes": sizes_seen,
                "requested_top_k": top_k,
            }
            timings[f"size_{n}_s"] = round(time.perf_counter() - t_size, 3)

            if any(s != top_k for s in sizes_seen):
                notes.append(
                    f"n={n}: realised circuit sizes {sorted(set(sizes_seen))} "
                    f"differ from requested top_k={top_k} (threshold ties)"
                )

        # ------------------------------------------------------------------
        # The committed rule. Do not edit.
        #   smallest n with J_seed(2n) - J_seed(n) < flatten_threshold,
        #   else the largest n in the ladder.
        # ------------------------------------------------------------------
        selected = None
        for i, n in enumerate(sizes[:-1]):
            delta = j_seed[sizes[i + 1]] - j_seed[n]
            results[str(n)]["delta_to_next"] = round(delta, 6)
            if selected is None and delta < flatten:
                selected = n
        flattened = selected is not None
        if selected is None:
            selected = sizes[-1]
            notes.append(
                f"curve had not flattened by n={sizes[-1]}; rule falls back to the "
                f"largest size tested. State this as a limitation in the abstract."
            )

        results["rule"] = {
            "statement": "smallest n with J_seed(2n) - J_seed(n) < flatten_threshold",
            "flatten_threshold": flatten,
            "curve_flattened": flattened,
            "selected_n_discovery_prompts": selected,
            "selected_n_prompts_total": 2 * selected,
        }

    except Exception as exc:  # noqa: BLE001
        status = "failed"
        notes.append(f"{type(exc).__name__}: {exc}")

    man = Manifest(
        kind="calib-nprompts",
        spec_id="calib-nprompts",
        config=cfg,
        seeds={"calibration_seeds": min(seeds)},
        timings_s=timings,
        peak_rss_mb=round(peak_rss_mb(), 1),
        notes=" | ".join(notes),
        status=status,
    )
    man_path = man.write(out_dir / "manifest.json")
    (out_dir / "j_seed.json").write_text(json.dumps(results, indent=2, sort_keys=True))

    print(f"status: {status}")
    for k, v in sorted(timings.items()):
        print(f"  {k:28s} {v}")
    if status == "ok":
        print()
        print("  n      J_seed    delta to next")
        for n in sizes:
            d = results[str(n)].get("delta_to_next")
            d_s = f"{d:+.4f}" if d is not None else "     -"
            print(f"  {n:<6d} {results[str(n)]['j_seed_mean']:.4f}    {d_s}")
        r = results["rule"]
        print()
        print(f"  curve flattened:   {r['curve_flattened']}")
        print(f"  SELECTED n_prompts: {r['selected_n_prompts_total']} total, "
              f"{r['selected_n_discovery_prompts']} discovery")
    if notes:
        print()
        for note in notes:
            print(f"  note: {note}")
    print(f"manifest: {man_path}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
