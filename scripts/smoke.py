#!/usr/bin/env python3
"""Gate 2: measure what one specification actually costs.

The brief asserts that the sweep fits on a single 24GB GPU inside the 10 to 24
August window. Nothing supports that. This script replaces the assertion with two
measured numbers, and it is deliberately the only thing it does.

**The two numbers, and why they are separate.**

1. `discovery_s` -- time to produce one prune-score ranking with
   `mask_gradient_prune_scores`.
2. `evaluation_s` -- time to evaluate that ranking at several edge counts with
   `run_circuits`.

Metric-relative `tau` means the `(m, tau)` cut is chosen by evaluating a metric
on an existing ranking. If `evaluation_s` per edge count is small relative to
`discovery_s`, the sweep needs one ranking per `(ablation, corruption, prompt,
seed)` rather than 3,780 independent discoveries, which is roughly a 12x saving.
**That reuse is currently an inference from the API, not a measurement.** This
script is what turns it into one, so report both numbers, never their sum.

**Status: NOT YET EXECUTED.** Written against auto-circuit 1.0.1 source read
directly from the wheel. The development sandbox has no torch. Treat the first
run as a debugging session, not as a measurement, and only trust the second.

Usage:
    python3 scripts/smoke.py --config configs/smoke.yaml
"""

from __future__ import annotations

import argparse
import platform
import resource
import sys
import time
import traceback
from contextlib import contextmanager
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402

from p1.manifest import Manifest  # noqa: E402
from p1.prompts import generate_ioi_dataset, write_dataset_json  # noqa: E402


def peak_vram_mb() -> float | None:
    """Peak CUDA allocation in MB, or None if this run was not on a GPU.

    Imported lazily and guarded, because this script must still run `--help` and
    the CPU path on a machine with no torch build at all.
    """
    try:
        import torch as _t

        if not _t.cuda.is_available():
            return None
        return round(_t.cuda.max_memory_allocated() / (1024 * 1024), 1)
    except Exception:  # noqa: BLE001
        return None


def peak_rss_mb() -> float:
    """Peak resident set size in MB.

    `ru_maxrss` is kilobytes on Linux and **bytes** on macOS. Getting this wrong
    reports a 1000x error in the memory figure, which is exactly the kind of
    number that would end up in a paper unchallenged.
    """
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw / (1024 * 1024) if platform.system() == "Darwin" else raw / 1024


@contextmanager
def timed(store: dict, key: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        store[key] = round(time.perf_counter() - t0, 3)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=REPO / "configs" / "smoke.yaml")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    cfg = yaml.safe_load(args.config.read_text())
    out_dir = args.out or (REPO / cfg["output"]["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    timings: dict[str, float] = {}
    notes: list[str] = []
    status = "ok"

    try:
        # Imports are late so that --help works on a machine without torch.
        with timed(timings, "import_s"):
            import torch as t

            from auto_circuit.data import load_datasets_from_json
            from auto_circuit.experiment_utils import load_tl_model
            from auto_circuit.prune import run_circuits
            from auto_circuit.prune_algos.mask_gradient import mask_gradient_prune_scores
            from auto_circuit.types import AblationType, PatchType
            from auto_circuit.utils.graph_utils import patchable_model

        dev = cfg["model"].get("device", "auto")
        if dev == "auto":
            dev = "cuda" if t.cuda.is_available() else "cpu"
        notes.append(f"device={dev}")
        if dev == "cpu":
            notes.append(
                "CPU run. auto-circuit has no MPS support (single device line, "
                "'cuda' if available else 'cpu'), so Apple Silicon lands here. "
                "Treat the timing as an upper bound, not as the GPU figure."
            )

        t.manual_seed(cfg["specification"]["seed"])

        # VRAM is the constraint that decides which card the sweep can run on,
        # and `peak_rss_mb` does not measure it. Reset here so the figure covers
        # model load, patching and discovery, which is the whole allocation
        # profile a sweep cell would see.
        if dev == "cuda":
            t.cuda.reset_peak_memory_stats()

        # Use auto-circuit's OWN model preparation, never a hand-rolled copy.
        # `load_tl_model` sets fold_ln, center_writing_weights, center_unembed,
        # use_attn_result, use_attn_in, use_split_qkv_input, use_hook_mlp_in,
        # eval mode, and requires_grad=False. The first three rewrite the
        # weights. A hand-rolled preparation that omits them yields a
        # numerically different model and therefore different circuits, with
        # nothing raising. Reproducing the instrument verbatim includes
        # reproducing how it prepares its input.
        with timed(timings, "model_load_s"):
            model = load_tl_model(cfg["model"]["name"], t.device(dev))

        # P1 supplies its own prompts: prompt variant is a grid dimension, and the
        # auto-circuit wheel ships no datasets. See src/p1/prompts.py.
        with timed(timings, "data_build_s"):
            ds = generate_ioi_dataset(
                n_prompts=cfg["task"]["n_prompts"],
                seed=cfg["specification"]["seed"],
                order=cfg["task"].get("order", "ABBA"),
            )
            ds_path = write_dataset_json(ds, out_dir / "prompts.json")
            train_loader, test_loader = load_datasets_from_json(
                model=model,
                path=ds_path,
                device=t.device(dev),
                batch_size=cfg["task"].get("batch_size", 8),
                train_test_size=(
                    cfg["task"]["n_prompts"] // 2,
                    cfg["task"]["n_prompts"] // 2,
                ),
                random_seed=cfg["specification"]["seed"],
                return_seq_length=False,
                shuffle=True,
            )

        with timed(timings, "patchable_model_s"):
            pmodel = patchable_model(
                model,
                factorized=True,          # edge-level. See DESIGN-DELTAS D8.
                slice_output="last_seq",
                # Required for any HookedTransformer: graph_utils.py line 163
                # asserts it is not None. True means separate edges into Q, K and
                # V, which is what load_tl_model's use_split_qkv_input=True sets
                # up, and transformer_lens_utils.py line 76 asserts that pairing.
                separate_qkv=True,
                device=t.device(dev),
            )
        notes.append(f"n_edges={len(pmodel.edges)}")

        # ---- Number 1: one prune-score ranking -----------------------------
        with timed(timings, "discovery_s"):
            prune_scores = mask_gradient_prune_scores(
                model=pmodel,
                dataloader=train_loader,
                official_edges=None,
                grad_function=cfg["specification"]["grad_function"],
                answer_function=cfg["specification"]["answer_function"],
                ablation_type=AblationType[cfg["specification"]["ablation"]],
                # Exactly one of these must be set: mask_gradient.py line 62
                # asserts (mask_val is None) XOR (integrated_grad_samples is
                # None). mask_val=0.0 is gradient at the clean point, which is
                # EAP. integrated_grad_samples gives integrated gradients, IEG.
                mask_val=cfg["specification"].get("mask_val"),
                integrated_grad_samples=cfg["specification"].get(
                    "integrated_grad_samples"
                ),
            )

        # ---- Number 2: evaluating that ranking at several cut points -------
        # TREE_PATCH ablates edges NOT in the circuit, so the circuit is kept and
        # what is measured is sufficiency. EDGE_PATCH is the complement and gives
        # comprehensiveness. Getting these the wrong way round silently inverts
        # every faithfulness number.
        edge_counts = list(cfg["specification"]["test_edge_counts"])
        with timed(timings, "evaluation_s"):
            _ = run_circuits(
                model=pmodel,
                dataloader=test_loader,
                test_edge_counts=edge_counts,
                prune_scores=prune_scores,
                patch_type=PatchType.TREE_PATCH,
                ablation_type=AblationType[cfg["specification"]["ablation"]],
            )
        timings["evaluation_per_cut_s"] = round(
            timings["evaluation_s"] / max(len(edge_counts), 1), 3
        )

        # The Gate 2 quantity: is reuse worth it?
        if timings["evaluation_per_cut_s"] > 0:
            timings["discovery_to_eval_ratio"] = round(
                timings["discovery_s"] / timings["evaluation_per_cut_s"], 2
            )

    except Exception:
        status = "failed"
        notes.append("TRACEBACK:\n" + traceback.format_exc())

    # A manifest is written whether or not the run succeeded. A failed run is a
    # fact about the environment and must be recorded, not lost.
    man = Manifest(
        kind="smoke",
        spec_id="smoke",
        config=cfg,
        seeds={"specification": cfg["specification"]["seed"]},
        timings_s=timings,
        peak_rss_mb=round(peak_rss_mb(), 1),
        peak_vram_mb=peak_vram_mb(),
        notes=" | ".join(notes),
        status=status,
    )
    path = man.write(out_dir / "manifest.json")

    print(f"status: {status}")
    for k, v in sorted(timings.items()):
        print(f"  {k:28s} {v}")
    print(f"  {'peak_rss_mb':28s} {man.peak_rss_mb}")
    print(f"  {'peak_vram_mb':28s} {man.peak_vram_mb}")
    print(f"manifest: {path}")
    if status == "ok":
        print(
            "\nGate 2: multiply discovery_s by the number of "
            "(ablation, corruption, prompt, seed) cells, NOT by 3780, "
            "then add evaluation_per_cut_s times the number of (metric, tau) cuts."
        )
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
