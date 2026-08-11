"""Repair run: per-example verdicts for H4, plus the attention cache.

**UNTESTED AS WRITTEN.** It was authored on a machine with no torch and no GPU,
so every assumption about the auto-circuit API is unverified. `--probe` exists
for exactly that reason and must pass on one cell before the full run is
launched. Do not skip it to save ten minutes; the alternative is discovering an
attribute name is wrong an hour into a GPU session.

Constraints fixed in `preregistration/DEVIATIONS.md`, 2026-08-11, before this
existed:

1. Discovery is **not** repeated. `top_edges` is read from the banked
   `result.json` and prune scores are synthesised to reproduce that exact
   ranking, so the circuits under test are the ones already reported.
2. Only the **recorded selected rung** per specification is evaluated. No new
   rung is introduced and the `tau` rule is not re-run.
3. auto-circuit is **not modified**. `run_circuits` is called verbatim; the
   per-example reduction happens in P1 code afterwards.
4. Output goes to a **separate directory**. No banked result is overwritten.
5. If the banked circuits cannot be reproduced exactly, H4 is reported as not
   computed rather than computed on approximations.

**Reproducing the ranking rather than the scores.** `ranked_edges` sorts by
`(-abs(score), str(edge))`. Assigning score `N - rank` to the r-th banked edge
gives strictly decreasing, all-distinct magnitudes, so the name tie-break never
fires and the induced order is exactly the banked one. The scores themselves are
meaningless; only the order they induce is used, and only the top-k selection
depends on it.

**`correct` is defined here and nowhere else.** For IOI, a circuit gets an
example right when it assigns a higher logit to the indirect-object token than
to the subject token, which is the standard IOI success criterion and is the sign
of the answer difference the sweep already measured in aggregate. Fixed before
the run. Upstream's `preds` shape, `{example_index: bool}`, is preserved so
`p1.agreement` applies unchanged.

**The gate.** For every cell the recomputed mean answer difference at the
selected rung is compared against the banked `metric_curves` value. Agreement
proves the per-example numbers decompose the figure already reported. Cells that
disagree are written with `status: "mismatch"` and excluded, and the mismatch
rate is reported.

Run:
    python3 scripts/repair.py --probe --results results/sweep
    python3 scripts/repair.py --results results/sweep --out results/repair
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

#: Agreement tolerance between the recomputed and banked metric value.
#: Loose enough for float32 nondeterminism across GPU runs, tight enough that a
#: different circuit could not pass.
MATCH_ATOL = 1e-3


def load_cells(results: Path):
    """Banked cells that completed, with their circuits and selected rungs."""
    for cell in sorted(p for p in results.iterdir() if p.is_dir()):
        man_path = cell / "manifest.json"
        if not man_path.exists():
            continue
        man = json.loads(man_path.read_text())
        if man.get("status") != "ok":
            continue
        payload = json.loads((cell / "result.json").read_text())
        rungs = sorted(
            {
                e["edges"]
                for e in payload["specifications"].values()
                if e.get("status") == "ok"
            }
        )
        if not rungs:
            continue
        yield cell, man, payload, rungs


def synthesise_prune_scores(pmodel, top_edges, torch):
    """Prune scores whose induced ranking is exactly `top_edges`.

    Every edge not in `top_edges` gets score 0. Edges in it get `N - rank`, so
    magnitudes are distinct and strictly decreasing and `ranked_edges` reproduces
    the banked order without reaching its name tie-break.
    """
    by_name = {str(e): e for e in pmodel.edges}
    missing = [n for n in top_edges if n not in by_name]
    if missing:
        raise KeyError(
            f"{len(missing)} banked edge names are not in the model graph, "
            f"first: {missing[:3]}. The edge naming has changed and the repair "
            f"cannot proceed."
        )

    ps = {
        dest.module_name: torch.zeros_like(dest.patch_mask)
        for dest in pmodel.dest_wrappers
    }
    n = len(top_edges)
    for rank, name in enumerate(top_edges):
        edge = by_name[name]
        ps[edge.dest.module_name][edge.patch_idx] = float(n - rank)
    return ps


def probe(results: Path) -> int:
    """Validate every API assumption on one cell. Cheap, and mandatory."""
    import torch as t
    from auto_circuit.experiment_utils import load_tl_model
    from auto_circuit.utils.graph_utils import patchable_model

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from sweep import ranked_edges  # the sweep's own ordering, reused verbatim

    cell, man, payload, rungs = next(load_cells(results))
    print(f"probe cell      {cell.name}")
    print(f"selected rungs  {rungs}")

    # `load_tl_model`, not `HookedTransformer.from_pretrained`. The first probe
    # used the latter and hit `assert model.cfg.use_attn_result` inside
    # `factorized_src_nodes`: auto-circuit needs per-head outputs, split QKV
    # inputs and MLP input hooks, and its own loader sets them. Using the sweep's
    # exact loader is also correctness, not convenience, since a differently
    # configured model would give a different graph.
    model = load_tl_model("gpt2", t.device("cpu"))
    pmodel = patchable_model(
        model,
        factorized=True,
        slice_output="last_seq",
        separate_qkv=True,
        device=t.device("cpu"),
    )
    print(f"model edges     {len(pmodel.edges):,}")

    edge = next(iter(pmodel.edges))
    for attr in ("dest", "patch_idx", "prune_score"):
        print(f"  Edge.{attr:<12} {'present' if hasattr(edge, attr) else 'MISSING'}")
    print(f"  Edge.dest.module_name  {getattr(edge.dest, 'module_name', 'MISSING')}")

    top = payload["top_edges"]
    names = {str(e) for e in pmodel.edges}
    unknown = [n for n in top if n not in names]
    print(f"banked names in graph   {len(top) - len(unknown):,}/{len(top):,}")
    if unknown:
        print(f"  UNKNOWN: {unknown[:3]}")
        return 1

    ps = synthesise_prune_scores(pmodel, top, t)
    order = [str(e) for e in ranked_edges(pmodel, ps)]
    ok = order[: len(top)] == top
    print(f"ranking reproduced      {'YES' if ok else 'NO'}")
    if not ok:
        first = next(i for i, (a, b) in enumerate(zip(order, top)) if a != b)
        print(f"  first divergence at rank {first}: {order[first]!r} vs {top[first]!r}")
        return 1

    print("\nprobe passed. The banked ranking is reproducible without rerunning "
          "discovery, so the repair run evaluates the circuits already reported.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--out", type=Path, default=Path("results/repair"))
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()

    if args.probe:
        return probe(args.results)

    raise SystemExit(
        "Full repair run not yet enabled. Run --probe first and paste the "
        "output; the evaluation loop is written against whatever the probe "
        "confirms, not against assumptions made without a GPU."
    )


if __name__ == "__main__":
    raise SystemExit(main())
