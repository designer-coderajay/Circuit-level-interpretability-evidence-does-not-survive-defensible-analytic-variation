#!/usr/bin/env python3
"""The confirmatory sweep.

One prune-score ranking per discovery cell, then the `(metric, tau)` cut applied
post-hoc to that ranking. That is the reuse architecture measured at Gate 2 and
it is why 18,480 specifications cost 1,540 discoveries rather than 18,480.

**Resume is the results directory.** Each cell writes its own manifest keyed by
`discovery_id`, and a cell whose manifest already reports `status: ok` is
skipped. There is no separate state file to corrupt when a Colab session dies
mid-write, which it will: the sweep is about thirty hours and a session is not.

**Every cell records its device.** Colab allocates whatever GPU is free, and a
confirmatory grid spread across a mix of cards has several environment hashes for
one result. Cells that ran on a non-modal device are discarded and rerun by
`analysis/`, and the device distribution is reported.

Ordering is the enumeration order of `p1.spec.enumerate_grid`, which is stable
across runs and machines, so a restart resumes rather than reshuffles.

Usage:
    python3 scripts/sweep.py --config configs/sweep.yaml
    python3 scripts/sweep.py --config configs/sweep.yaml --limit 10   # slice
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def peak_rss_mb() -> float:
    import resource

    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw / (1024 * 1024) if sys.platform == "darwin" else raw / 1024


def peak_vram_mb():
    try:
        import torch as t

        if not t.cuda.is_available():
            return None
        return round(t.cuda.max_memory_allocated() / (1024 * 1024), 1)
    except Exception:  # noqa: BLE001
        return None


def ranked_edges(pmodel, prune_scores):
    """Every edge by descending |prune score|, ties broken by name.

    Deterministic ordering is load-bearing. Without the name tie-break, two runs
    of the identical specification could return different top-k sets purely from
    set iteration order, and that would surface as instability the paper would
    then have to explain.
    """
    scored = [
        (abs(float(e.prune_score(prune_scores))), str(e), e) for e in pmodel.edges
    ]
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [e for _, _, e in scored]


def attention_rows_for(model, prompts, roles_list, device):
    """Per-head attention over role-labelled tokens, at the final query position.

    Returned as `{(block, head): [row_per_prompt]}` plus the per-prompt role
    labels. Computed on the **clean** prompts only, so it depends on nothing but
    `(prompt_variant, seed)` and is cached across every cell that shares those.
    Ten computations for the whole sweep rather than 1,540.

    BOS is prepended by the loader and is not part of the prompt string, so it is
    stripped before span matching and labelled `other`.

    **The prompt is built exactly as `load_datasets_from_json` builds it**, by
    string-concatenating `tokenizer.bos_token`, rather than by asking
    transformer-lens to prepend. Two reasons, both learned the hard way on
    2026-08-12.

    First, `to_str_tokens(prompt, prepend_bos=True)` **honours
    `tokenizer.add_bos_token`**. `p1.prompts.align_answer_tokenisation` clears
    that flag on tokenizers that would otherwise double the BOS, and doing so
    silently switched off prepending here too, so `str_toks[0]` became a real
    content token and `token_role_labels` raised on the reconstruction check.
    That check earned its place.

    Second, the model is being asked about the same token sequence discovery ran
    on. Prepending the way the loader does is the only way to guarantee that.

    The number of leading BOS tokens is then **counted, not assumed**, so this
    holds whether the tokenizer inserts one itself or not.
    """
    import torch as t

    from p1.attribution import OTHER_ROLE, split_leading_bos, token_role_labels

    per_prompt_labels: list[list[str]] = []
    rows: dict[tuple[int, int], list[list[float]]] = defaultdict(list)

    tok = model.tokenizer
    bos_tok = tok.bos_token

    for prompt, roles in zip(prompts, roles_list):
        # Tokenise with the raw tokenizer, exactly as `load_datasets_from_json`
        # does, rather than through transformer-lens.
        #
        # VERIFIED 2026-08-13, both branches, on Pythia-160m with
        # `add_bos_token` cleared:
        #   to_str_tokens(prompt, prepend_bos=True)      -> ['Then', ...]  no BOS
        #   to_str_tokens(bos + prompt, prepend_bos=False) -> ['Then', ...]  BOS stripped
        # transformer-lens declines to add one, and strips a string-prepended
        # one. Neither branch yields the sequence the loader feeds the model, so
        # the library's BOS handling is bypassed rather than negotiated with.
        ids = tok(bos_tok + prompt)["input_ids"]
        str_toks = [tok.decode([i]) for i in ids]

        n_bos, body = split_leading_bos(str_toks, bos_tok)
        if n_bos == 0:
            raise RuntimeError(
                "expected at least one leading BOS token after prepending "
                f"{bos_tok!r}; got {str_toks[:3]!r}"
            )

        labels = [OTHER_ROLE] * n_bos + token_role_labels(body, prompt, roles)
        per_prompt_labels.append(labels)

        toks = model.to_tokens(text, prepend_bos=False).to(device)
        with t.inference_mode():
            _, cache = model.run_with_cache(
                toks, names_filter=lambda n: n.endswith("hook_pattern")
            )
        for block in range(model.cfg.n_layers):
            pattern = cache["pattern", block]  # [batch, head, query, key]
            last = pattern[0, :, -1, :].float().cpu().tolist()
            for head in range(model.cfg.n_heads):
                rows[(block, head)].append(last[head])
        del cache
    return rows, per_prompt_labels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--limit", type=int, default=None,
                    help="stop after N cells; for slice validation only")
    ap.add_argument("--dry-run", action="store_true",
                    help="enumerate and report the plan without running anything")
    args = ap.parse_args()

    import yaml

    cfg = yaml.safe_load(args.config.read_text())
    if cfg.get("confirmatory") is not True:
        raise SystemExit("refusing to run: the sweep config must set `confirmatory: true`")

    out_dir = args.out or (REPO / cfg["output"]["dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    from p1.spec import (
        CORRUPTION_NOT_APPLICABLE,
        DISCOVERY_OBJECTIVE_PARAMS,
        EDGE_COUNT_LADDER,
        METRIC_SPECS,
        discovery_cells,
        enumerate_grid,
        grid_size,
    )

    axes = {k: tuple(v) for k, v in cfg["axes"].items()}
    specs = list(enumerate_grid(axes))
    by_cell: dict[str, list] = defaultdict(list)
    for s in specs:
        by_cell[s.discovery_id].append(s)
    cell_order = list(dict.fromkeys(s.discovery_id for s in specs))

    print(f"specifications  {grid_size(axes):>8,}")
    print(f"discovery cells {discovery_cells(axes):>8,}")
    assert len(cell_order) == discovery_cells(axes), "enumerator and closed form disagree"

    done = {
        c for c in cell_order
        if (out_dir / c / "manifest.json").exists()
        and json.loads((out_dir / c / "manifest.json").read_text()).get("status") == "ok"
    }
    todo = [c for c in cell_order if c not in done]
    if args.limit is not None:
        todo = todo[: args.limit]
    print(f"already complete {len(done):>7,}")
    print(f"to run           {len(todo):>7,}")
    if args.dry_run:
        return 0
    if not todo:
        print("nothing to do")
        return 0

    import torch as t
    from auto_circuit.data import load_datasets_from_json
    from auto_circuit.experiment_utils import load_tl_model
    from auto_circuit.metrics.prune_metrics.answer_diff import measure_answer_diff
    from auto_circuit.metrics.prune_metrics.kl_div import measure_kl_div
    from auto_circuit.prune import run_circuits
    from auto_circuit.prune_algos.mask_gradient import mask_gradient_prune_scores
    from auto_circuit.types import AblationType, PatchType
    from auto_circuit.utils.graph_utils import patchable_model

    from p1.attribution import mean_segment_mass, segment_mass
    from p1.claim_map import Granularity, phi_affected, phi_overseer
    from p1.features import components_from_nodes, features_from_circuit
    from p1.manifest import Manifest
    from p1.metrics import DegenerateMetric, normalised_recovery, select_rung
    from p1.prompts import (
        align_answer_tokenisation,
        generate_ioi_dataset,
        write_dataset_json,
    )

    dev = cfg["model"]["device"]
    if dev == "auto":
        dev = "cuda" if t.cuda.is_available() else "cpu"
    device = t.device(dev)
    gpu = t.cuda.get_device_name(0) if dev == "cuda" else "cpu"
    print(f"device           {gpu}")

    model = load_tl_model(cfg["model"]["name"], device)

    # `load_datasets_from_json` tokenises answers with the raw HuggingFace
    # tokenizer and requires exactly one token per answer, and it prepends BOS to
    # prompts as a string before tokenising. A tokenizer that inserts BOS itself
    # therefore produces three-dimensional answers and doubled BOS on every
    # prompt. On GPT-2 this is a no-op and `changed` is False.
    #
    # Keyed on the measured token width, not on `add_bos_token`, which reads True
    # on both tokenizers and so does not explain the difference. See
    # `p1.prompts.align_answer_tokenisation` and DEVIATIONS 2026-08-12.
    align = align_answer_tokenisation(model)
    print(f"answer tokens    {align['max_width_before']} -> "
          f"{align['max_width_after']}   tokenizer adjusted: {align['changed']}")

    pmodel = patchable_model(
        model, factorized=True, slice_output="last_seq",
        separate_qkv=True, device=device,
    )
    n_edges = len(pmodel.edges)
    shape = cfg["model_shape"]
    counts = [0] + list(EDGE_COUNT_LADDER) + [n_edges]
    n_disc = cfg["task"]["n_prompts"] // 2

    attn_cache: dict[tuple[str, int], tuple] = {}
    stats = Counter()
    t_start = time.perf_counter()

    for i, cell_id in enumerate(todo, 1):
        cell_specs = by_cell[cell_id]
        head = cell_specs[0]
        cell_dir = out_dir / cell_id
        cell_dir.mkdir(parents=True, exist_ok=True)
        timings: dict[str, float] = {}
        notes = [f"device={dev}", f"gpu={gpu}", f"n_edges={n_edges}",
                 f"tokenizer_bos_adjusted={align['changed']}"]
        status = "ok"
        payload: dict = {}

        try:
            t0 = time.perf_counter()
            # `ZERO` and `TOKENWISE_MEAN_CLEAN` never read the corrupt
            # distribution, so their specifications carry the
            # CORRUPTION_NOT_APPLICABLE sentinel rather than a real level. The
            # dataset generator only accepts real levels, so the sentinel is
            # resolved here to ABC.
            #
            # **The choice cannot affect the result, and that is provable rather
            # than hoped.** VERIFIED from `ablation_activations.py`: `ZERO` sets
            # `out = t.zeros_like(out)` and forces `input_batch = batch.clean`;
            # `TOKENWISE_MEAN_CLEAN` reads `clean_dataset` only. Neither ever
            # touches `batch.corrupt`, so any corruption level yields an
            # identical circuit. ABC is used because it is the canonical default.
            #
            # This is the whole reason the sentinel exists: crossing these two
            # operators against four corruption levels would emit four identical
            # specifications. See DESIGN-DELTAS D18 and DEVIATIONS entry 3.
            corruption = head.corruption
            if corruption == CORRUPTION_NOT_APPLICABLE:
                corruption = "ABC"
            ds = generate_ioi_dataset(
                n_prompts=cfg["task"]["n_prompts"], seed=head.seed,
                order=head.prompt_variant, corruption=corruption,
            )
            ds_path = write_dataset_json(ds, cell_dir / "prompts.json")
            train_loader, test_loader = load_datasets_from_json(
                model=model, path=ds_path, device=device,
                batch_size=cfg["task"]["batch_size"],
                train_test_size=(n_disc, n_disc), random_seed=head.seed,
            )
            timings["data_s"] = round(time.perf_counter() - t0, 3)

            # The invariant that broke on 2026-08-12, asserted where it is cheap
            # to read rather than left to surface as a bare AssertionError deep
            # inside `indices_vals`. `answers` must be two-dimensional, matching
            # the sliced logits; a third dimension means answers tokenised to
            # more than one token. See DEVIATIONS 2026-08-12.
            probe_batch = next(iter(train_loader))
            if probe_batch.answers.ndim != 2:
                raise RuntimeError(
                    "answers must be 2-D to match the sliced logits; got shape "
                    f"{tuple(probe_batch.answers.shape)}. Answer strings are "
                    "tokenising to more than one token."
                )
            del probe_batch

            # ---- discovery -------------------------------------------------
            params = dict(DISCOVERY_OBJECTIVE_PARAMS[head.discovery_objective])

            # `clean_corrupt` is not free for every operator, and the library
            # enforces that with a bare assertion. VERIFIED from
            # `auto_circuit/utils/ablation_activations.py`:
            #
            #   assert (clean_corrupt is not None)
            #          == (ablation_type in batch_specific_ablation)
            #
            # with `batch_specific_ablation = [RESAMPLE, BATCH_TOKENWISE_MEAN,
            # BATCH_ALL_TOK_MEAN]`. Those three take the value; the other four
            # must receive `None` or the call dies with an AssertionError
            # carrying no message.
            #
            # `mask_gradient_prune_scores` defaults it to "corrupt", so passing
            # nothing fails for four of the seven operators. That is what killed
            # 100 of every 220 cells on the first attempt.
            #
            # This is not a design change. PLAN.md fixes `clean_corrupt` at
            # "corrupt" **where the analyst has a choice**, and for the other
            # four the instrument allows no choice at all. The five
            # corruption-dependent operators are unaffected: TOKENWISE_MEAN_CORRUPT
            # and TOKENWISE_MEAN_CLEAN_AND_CORRUPT read the corrupt distribution
            # via their own `corrupt_dataset` property, not via this argument.
            # See DESIGN-DELTAS D18 and DEVIATIONS entry 2.
            takes_clean_corrupt = head.ablation in (
                "RESAMPLE", "BATCH_TOKENWISE_MEAN", "BATCH_ALL_TOK_MEAN",
            )
            t0 = time.perf_counter()
            ps = mask_gradient_prune_scores(
                model=pmodel, dataloader=train_loader, official_edges=None,
                grad_function=params["grad_function"],
                answer_function=params["answer_function"],
                ablation_type=AblationType[head.ablation],
                clean_corrupt="corrupt" if takes_clean_corrupt else None,
                mask_val=params.get("mask_val"),
                integrated_grad_samples=params.get("integrated_grad_samples"),
            )
            timings["discovery_s"] = round(time.perf_counter() - t0, 3)
            order = ranked_edges(pmodel, ps)

            # ---- evaluation: two passes, both needed ------------------------
            # TREE_PATCH ablates the edges NOT in the circuit, so the circuit is
            # retained. EDGE_PATCH is the complement. Getting these the wrong way
            # round silently inverts every faithfulness number.
            t0 = time.perf_counter()
            outs = {}
            for patch_name in ("TREE_PATCH", "EDGE_PATCH"):
                outs[patch_name] = run_circuits(
                    model=pmodel, dataloader=test_loader,
                    test_edge_counts=counts, prune_scores=ps,
                    patch_type=PatchType[patch_name],
                    ablation_type=AblationType[head.ablation],
                )
            timings["evaluation_s"] = round(time.perf_counter() - t0, 3)

            # ---- metric curves and recoveries ------------------------------
            curves: dict[str, dict[int, float]] = {}
            for metric, mspec in METRIC_SPECS.items():
                co = outs[mspec["patch"]]
                if mspec["measure"] == "kl_div":
                    meas = measure_kl_div(pmodel, test_loader, co, compare_to_clean=True)
                else:
                    meas = measure_answer_diff(
                        pmodel, test_loader, co, prob_func=mspec["prob_func"]
                    )
                curves[metric] = {int(k): float(v) for k, v in meas}

            recoveries: dict[str, dict[int, float]] = {}
            degenerate: list[str] = []
            for metric, curve in curves.items():
                try:
                    recoveries[metric] = {
                        k: normalised_recovery(curve[k], curve[0], curve[n_edges])
                        for k in EDGE_COUNT_LADDER
                    }
                except DegenerateMetric as exc:
                    degenerate.append(f"{metric}: {exc}")

            # ---- attention, cached per (prompt_variant, seed) ---------------
            key = (head.prompt_variant, head.seed)
            if key not in attn_cache:
                t0 = time.perf_counter()
                clean = [p["clean"] for p in ds["prompts"]]
                attn_cache[key] = attention_rows_for(
                    model, clean, ds["p1_roles"], device
                )
                timings["attention_s"] = round(time.perf_counter() - t0, 3)
            attn_rows, prompt_labels = attn_cache[key]

            # ---- one claim per specification -------------------------------
            per_spec = {}
            for s in cell_specs:
                if s.metric in degenerate or s.metric not in recoveries:
                    per_spec[s.spec_id] = {"status": "discarded",
                                           "reason": "degenerate metric"}
                    stats["discarded_metric"] += 1
                    continue
                recs = [recoveries[s.metric][k] for k in EDGE_COUNT_LADDER]
                k = select_rung(recs, list(EDGE_COUNT_LADDER), s.threshold)
                if k is None:
                    per_spec[s.spec_id] = {"status": "discarded",
                                           "reason": "no rung reached 1 - tau"}
                    stats["discarded_no_rung"] += 1
                    continue

                nodes = [n for e in order[:k] for n in (e.src, e.dest)]
                comps = components_from_nodes(nodes)
                heads_in = [(c.layer, c.index) for c in comps if c.kind == "attn"]
                masses = [
                    segment_mass([attn_rows[h][p] for h in heads_in if h in attn_rows],
                                 prompt_labels[p])
                    for p in range(len(prompt_labels))
                ]
                feats = features_from_circuit(
                    nodes, n_blocks=shape["n_blocks"],
                    n_heads_per_block=shape["n_heads_per_block"],
                    position_mass=mean_segment_mass(masses),
                )
                per_spec[s.spec_id] = {
                    "status": "ok",
                    "edges": k,
                    "n_components": len(comps),
                    "claims": {
                        g.name: {
                            "overseer": phi_overseer(feats, g),
                            "affected": phi_affected(feats, g),
                        }
                        for g in Granularity
                    },
                }
                stats["ok"] += 1

            payload = {
                "discovery_id": cell_id,
                "discovery_key": list(head.discovery_key),
                "n_edges": n_edges,
                "metric_curves": {m: {str(k): v for k, v in c.items()}
                                  for m, c in curves.items()},
                "recoveries": {m: {str(k): v for k, v in r.items()}
                               for m, r in recoveries.items()},
                "degenerate_metrics": degenerate,
                "specifications": per_spec,
                "top_edges": [str(e) for e in order[:max(EDGE_COUNT_LADDER)]],
            }

        except Exception as exc:  # noqa: BLE001
            status = "failed"
            notes.append(f"{type(exc).__name__}: {exc}")
            stats["failed_cells"] += 1

        man = Manifest(
            kind="sweep", spec_id=cell_id, config=cfg,
            seeds={"specification": head.seed},
            timings_s=timings, peak_rss_mb=round(peak_rss_mb(), 1),
            peak_vram_mb=peak_vram_mb(), notes=" | ".join(notes), status=status,
        )
        man.write(cell_dir / "manifest.json")
        if payload:
            (cell_dir / "result.json").write_text(json.dumps(payload, sort_keys=True))

        if i % 10 == 0 or i == len(todo):
            el = time.perf_counter() - t_start
            rate = el / i
            print(f"  {i:>5}/{len(todo)}  {status:<7} "
                  f"elapsed {el/3600:5.2f}h  eta {(len(todo)-i)*rate/3600:5.2f}h")

    print()
    for k, v in sorted(stats.items()):
        print(f"  {k:<22} {v:,}")
    print(f"  {'wall_clock_h':<22} {(time.perf_counter()-t_start)/3600:.2f}")
    return 0 if not stats["failed_cells"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
