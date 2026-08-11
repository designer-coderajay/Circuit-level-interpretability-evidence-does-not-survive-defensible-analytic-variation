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


def evaluate_cell(pmodel, model, cell, payload, rungs, device, torch, batch_size=8):
    """Per-example verdicts at the recorded rungs, plus the reproduction gate.

    The dataset is **not regenerated**. The sweep wrote `prompts.json` into every
    cell and it is read back, so the examples are the same objects rather than
    the same recipe. One fewer thing that can silently drift.
    """
    from auto_circuit.data import load_datasets_from_json
    from auto_circuit.metrics.prune_metrics.answer_diff import measure_answer_diff
    from auto_circuit.prune import run_circuits
    from auto_circuit.types import AblationType, PatchType

    _, ablation, _, _, seed, _ = payload["discovery_key"]
    _, test_loader = load_datasets_from_json(
        model=model,
        path=cell / "prompts.json",
        device=device,
        batch_size=batch_size,
        train_test_size=(128, 128),
        random_seed=seed,
    )

    ps = synthesise_prune_scores(pmodel, payload["top_edges"], torch)
    outs = run_circuits(
        model=pmodel,
        dataloader=test_loader,
        test_edge_counts=list(rungs),
        prune_scores=ps,
        patch_type=PatchType.TREE_PATCH,
        ablation_type=AblationType[ablation],
    )

    # Gate: the instrument's own reduction, compared against what was banked.
    recomputed = {int(k): float(v)
                  for k, v in measure_answer_diff(pmodel, test_loader, outs,
                                                  prob_func="logits")}
    banked = {int(k): float(v) for k, v in payload["metric_curves"]["logit_diff"].items()}
    gate = {
        int(k): {"recomputed": recomputed[k], "banked": banked.get(k),
                 "match": banked.get(k) is not None
                 and abs(recomputed[k] - banked[k]) <= MATCH_ATOL}
        for k in rungs if k in recomputed
    }

    # Per-example verdicts. `correct` is the sign of the answer difference, per
    # DEVIATIONS 2026-08-11: IO logit above subject logit.
    verdicts: dict[int, dict[int, bool]] = {int(k): {} for k in rungs}
    for k in rungs:
        idx = 0
        for batch in test_loader:
            logits = outs[k][batch.key]
            if logits.ndim == 3:
                logits = logits[:, -1, :]
            ans = batch.answers if torch.is_tensor(batch.answers) else \
                torch.stack(list(batch.answers))
            wrong = batch.wrong_answers if torch.is_tensor(batch.wrong_answers) else \
                torch.stack(list(batch.wrong_answers))
            a = logits.gather(1, ans.to(logits.device)).squeeze(1)
            w = logits.gather(1, wrong.to(logits.device)).squeeze(1)
            for correct in (a > w).tolist():
                verdicts[int(k)][idx] = bool(correct)
                idx += 1
    return verdicts, gate


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--out", type=Path, default=Path("results/repair"))
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--one-cell", action="store_true",
                    help="evaluate a single cell and print the gate, before committing GPU time")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    if args.probe:
        return probe(args.results)

    import torch as t
    from auto_circuit.experiment_utils import load_tl_model
    from auto_circuit.utils.graph_utils import patchable_model

    device = t.device("cuda" if t.cuda.is_available() else "cpu")
    print(f"device {device}")
    model = load_tl_model("gpt2", device)
    pmodel = patchable_model(model, factorized=True, slice_output="last_seq",
                             separate_qkv=True, device=device)

    args.out.mkdir(parents=True, exist_ok=True)
    done = mismatched = failed = 0
    for cell, man, payload, rungs in load_cells(args.results):
        dest = args.out / cell.name
        if (dest / "verdicts.json").exists():
            done += 1
            continue
        try:
            verdicts, gate = evaluate_cell(pmodel, model, cell, payload, rungs,
                                           device, t)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  {cell.name} FAILED {type(exc).__name__}: {exc}")
            if args.one_cell:
                raise
            continue

        ok = all(g["match"] for g in gate.values())
        mismatched += not ok
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "verdicts.json").write_text(json.dumps({
            "status": "ok" if ok else "mismatch",
            "discovery_key": payload["discovery_key"],
            "gate": gate,
            "verdicts": {str(k): v for k, v in verdicts.items()},
        }, sort_keys=True))
        done += 1

        if args.one_cell:
            print(f"\ncell {cell.name}  rungs {list(rungs)}")
            for k, g in gate.items():
                print(f"  rung {k:>6}  recomputed {g['recomputed']:+.6f}  "
                      f"banked {g['banked']:+.6f}  match {g['match']}")
            n = len(next(iter(verdicts.values())))
            print(f"  examples per rung {n}")
            print("\nGATE PASSED" if ok else "\nGATE FAILED")
            return 0 if ok else 1
        if args.limit and done >= args.limit:
            break
        if done % 50 == 0:
            print(f"  {done} cells, {mismatched} mismatched, {failed} failed")

    print(f"\ndone {done}  mismatched {mismatched}  failed {failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
