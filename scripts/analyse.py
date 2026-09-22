"""Pooled confirmatory analysis, stage 1: the claim-based outcomes.

Implements `preregistration/PLAN.md` sections 3, 6 and 7 for every outcome that
is computable from the banked sweep without further GPU work. Nothing here makes
an analytic choice that the plan does not already fix. Where the plan is silent
the script raises rather than guessing.

Scope of this stage, and what is deliberately absent:

  in   primary F, phi_overseer at MEDIUM, bootstrap over specifications
  in   secondary F for phi_affected, and both maps at COARSE and FINE
  in   pi_star and filability at alpha in {0.05, 0.10, 0.20}
  in   discard rate per axis level, per plan section 7
  out  J_bar and the pairwise D distribution: circuit-level, stage 2
  out  variance decomposition by axis: REML, stage 3
  out  the random-circuit null multiverse: stage 4
  out  H4, which needs per-example verdicts the sweep did not record.
       See preregistration/DEVIATIONS.md, 2026-08-11.

Run:
    python3 scripts/analyse.py --results results/sweep --out results/analysis

No torch. Runs on requirements-analysis.txt.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p1.multiverse import (  # noqa: E402
    bootstrap_over_specifications,
    flip_rate,
    is_filable,
    modal_share,
)

#: Fixed by PLAN.md section 3. The primary outcome is exactly one number.
PRIMARY_MAP = "overseer"
PRIMARY_GRANULARITY = "MEDIUM"

#: PLAN.md section 6. Not tunable here; changing either is a deviation.
N_BOOT = 10_000
BOOTSTRAP_SEED = 0

#: PLAN.md section 3.
ALPHAS = (0.05, 0.10, 0.20)

AXES = (
    "discovery_objective",
    "ablation",
    "corruption",
    "metric",
    "threshold",
    "prompt_variant",
    "seed",
)


#: Committed derived artefact. See `analysis/export_records.py`.
EXPORT = (
    Path(__file__).resolve().parents[1] / "results" / "analysis" / "specifications.json.gz"
)

#: Node count of the instrumented graph, 12 heads + 1 MLP per block.
N_COMPONENTS = 12 * 12 + 12


def _cached_payload() -> dict | None:
    """Read the committed export, or None when it is absent."""
    import gzip

    if not EXPORT.exists():
        return None
    return json.loads(gzip.decompress(EXPORT.read_bytes()))


def _load_exported_records() -> tuple[list[dict], dict] | None:
    """Fall back to the committed export when the raw sweep output is absent.

    `results/sweep` is 389 MB and gitignored, so a clone has the manifests but
    not the per-cell `result.json`. Without this fallback none of the four
    analysis entry points runs for anyone but the author, which is a poor
    property for a paper about reproducible evidence. See
    `analysis/export_records.py`.

    **Raw output always wins.** This is consulted only when the raw directory is
    missing or holds no cells, so an author with the data reads the source and
    never this file. Returns None when the export is absent too, so the caller
    raises its own error rather than this one masking it.
    """
    payload = _cached_payload()
    if payload is None:
        return None
    strings = payload["claim_strings"]
    records = [
        {
            **{k: v for k, v in r.items() if k != "claims"},
            "claims": {
                g: {m: strings[i] for m, i in maps.items()}
                for g, maps in r["claims"].items()
            },
        }
        for r in payload["records"]
    ]
    audit = dict(payload["audit"])
    if "discards" in audit:
        audit["discards"] = Counter(
            {tuple(json.loads(k)): v for k, v in audit["discards"].items()}
        )
    return records, audit


def sweep_facts(results_dir: Path) -> dict:
    """Per-cell facts that `load_records` does not carry, raw preferred.

    Two paper tables need fields from the raw per-cell output that a record does
    not hold:

      `n_edges`     the edge count the instrument itself reports, checked here
                    across every cell rather than sampled from one.
      `bin_pairs`   one (layer band, component fraction) pair per kept
                    specification. `tab:bins` re-bins the fraction under eight
                    alternative bin edges, so the pair is the correct cut point
                    between what is measured and what the table varies. The
                    upstream `top_edges` list is far too large to commit and is
                    not needed once the pair is known.

    Same contract as `load_records`: computed from `results_dir` when it holds
    output, read from the committed export when it does not.

    Pairs are emitted in sorted-cell order so the export is deterministic. Order
    does not affect any consumer, because `flip_rate` is a function of the label
    counts alone.
    """
    cells = sorted(results_dir.glob("*/result.json")) if results_dir.exists() else []

    if not cells:
        payload = _cached_payload()
        if payload is None:
            raise FileNotFoundError(
                f"no per-cell output under {results_dir}, and no export at "
                f"{EXPORT}. Run scripts/sweep.py, or regenerate the export with "
                f"analysis/export_records.py."
            )
        derived = payload["derived"]
        bands = derived["bands"]
        return {
            "n_edges": derived["n_edges"]["value"],
            "n_cells": derived["n_edges"]["cells"],
            "bin_pairs": [(bands[b], f) for b, f in derived["bin_pairs"]],
        }

    from p1.claim_map import DEFAULT_BAND_NAMES, layer_band
    from p1.features import features_from_circuit
    from p1.graph import nodes_from_edge_names

    reported: Counter = Counter()
    pairs: list[tuple[str, float]] = []

    for path in cells:
        payload = json.loads(path.read_text())
        reported[payload["n_edges"]] += 1
        top = payload["top_edges"]
        cache: dict[int, tuple[str, float]] = {}
        for entry in payload["specifications"].values():
            if entry.get("status") != "ok":
                continue
            k = entry["edges"]
            if k not in cache:
                features = features_from_circuit(
                    nodes_from_edge_names(top[:k]), n_blocks=12, n_heads_per_block=12
                )
                cache[k] = (
                    layer_band(features, DEFAULT_BAND_NAMES),
                    len(features.components) / N_COMPONENTS,
                )
            pairs.append(cache[k])

    if len(reported) != 1:
        raise ValueError(f"cells disagree on the instrumented edge count: {dict(reported)}")
    (value, n_cells), = reported.items()
    return {"n_edges": value, "n_cells": n_cells, "bin_pairs": pairs}


def load_records(results_dir: Path, axes: dict) -> tuple[list[dict], dict]:
    """One record per specification that produced a claim, plus a cell audit.

    A cell contributes nothing unless its manifest reports `status: ok`, and a
    specification contributes nothing unless its own status is `ok`. Discards are
    counted, never repaired, per PLAN.md section 7.

    When the raw sweep output is not present, falls back to the committed
    export so that the analysis remains runnable from a clone.
    """
    from p1.spec import enumerate_grid

    if not results_dir.exists() or not any(
        (c / "result.json").exists() for c in results_dir.iterdir() if c.is_dir()
    ):
        cached = _load_exported_records()
        if cached is not None:
            return cached

    spec_index = {s.spec_id: s for s in enumerate_grid(axes)}

    records: list[dict] = []
    cells_ok = cells_failed = 0
    discards: Counter = Counter()

    for cell in sorted(p for p in results_dir.iterdir() if p.is_dir()):
        man_path = cell / "manifest.json"
        if not man_path.exists():
            raise FileNotFoundError(f"cell without manifest: {cell}")
        if json.loads(man_path.read_text()).get("status") != "ok":
            cells_failed += 1
            continue
        cells_ok += 1

        payload = json.loads((cell / "result.json").read_text())
        for spec_id, entry in payload["specifications"].items():
            spec = spec_index.get(spec_id)
            if spec is None:
                raise KeyError(f"{spec_id} in results is not in the grid")
            axis_values = {a: getattr(spec, a) for a in AXES}
            if entry.get("status") != "ok":
                for axis, value in axis_values.items():
                    discards[(axis, value)] += 1
                continue
            records.append(
                {
                    "spec_id": spec_id,
                    "edges": entry["edges"],
                    "claims": entry["claims"],
                    **axis_values,
                }
            )

    audit = {
        "cells_ok": cells_ok,
        "cells_failed": cells_failed,
        "specifications_with_claims": len(records),
        "specifications_discarded": sum(
            n for (axis, _), n in discards.items() if axis == "metric"
        ),
    }
    return records, {"audit": audit, "discards": discards}


def discard_table(discards: Counter, records: list[dict]) -> dict:
    """Discard rate per axis level. PLAN.md section 7 requires it per level."""
    kept: Counter = Counter()
    for r in records:
        for axis in AXES:
            kept[(axis, r[axis])] += 1

    out: dict = defaultdict(dict)
    for axis in AXES:
        levels = {lvl for (a, lvl) in list(discards) + list(kept) if a == axis}
        for lvl in sorted(levels, key=str):
            d = discards[(axis, lvl)]
            k = kept[(axis, lvl)]
            total = d + k
            out[axis][str(lvl)] = {
                "kept": k,
                "discarded": d,
                "rate": (d / total) if total else None,
            }
    return dict(out)


def labels_for(records: list[dict], addressee: str, granularity: str) -> list[str]:
    return [r["claims"][granularity][addressee] for r in records]


def summarise(labels: list[str], *, bootstrap: bool) -> dict:
    """F, pi_star and filability for one (addressee, granularity) pair."""
    counts = Counter(labels)
    result = {
        "n_specifications": len(labels),
        "n_distinct_claims": len(counts),
        "flip_rate": flip_rate(labels),
        "modal_share": modal_share(labels),
        "filable": {str(a): is_filable(labels, a) for a in ALPHAS},
        "top_claims": [
            {"count": n, "share": n / len(labels), "claim": c}
            for c, n in counts.most_common(5)
        ],
    }
    if bootstrap:
        boot = bootstrap_over_specifications(
            labels, flip_rate, n_boot=N_BOOT, seed=BOOTSTRAP_SEED
        )
        lo, hi = boot.percentile_interval(0.95)
        result["bootstrap"] = {
            "n_boot": N_BOOT,
            "seed": BOOTSTRAP_SEED,
            "observed": boot.observed,
            "ci95_low": lo,
            "ci95_high": hi,
            "resampling_unit": "specification",
        }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--config", type=Path, default=Path("configs/sweep.yaml"))
    ap.add_argument("--out", type=Path, default=Path("results/analysis"))
    args = ap.parse_args()

    axes = yaml.safe_load(args.config.read_text())["axes"]
    records, meta = load_records(args.results, axes)
    if not records:
        raise SystemExit("no specifications with claims; nothing to pool")

    report: dict = {
        "plan": "preregistration/PLAN.md",
        "stage": 1,
        "primary_outcome": f"flip_rate of phi_{PRIMARY_MAP} at {PRIMARY_GRANULARITY}",
        "audit": meta["audit"],
        "discard_rate_by_axis_level": discard_table(meta["discards"], records),
        "outcomes": {},
    }

    for addressee in ("overseer", "affected"):
        for gran in ("COARSE", "MEDIUM", "FINE"):
            primary = addressee == PRIMARY_MAP and gran == PRIMARY_GRANULARITY
            report["outcomes"][f"{addressee}/{gran}"] = {
                "primary": primary,
                **summarise(labels_for(records, addressee, gran), bootstrap=primary),
            }

    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / "stage1_claims.json"
    dest.write_text(json.dumps(report, indent=2, sort_keys=True, default=str))

    p = report["outcomes"][f"{PRIMARY_MAP}/{PRIMARY_GRANULARITY}"]
    b = p["bootstrap"]
    print(f"specifications pooled  {p['n_specifications']:>8,}")
    print(f"distinct claims        {p['n_distinct_claims']:>8,}")
    print(f"PRIMARY  F             {b['observed']:>8.4f}")
    print(f"         95% CI        [{b['ci95_low']:.4f}, {b['ci95_high']:.4f}]")
    print(f"         pi_star       {p['modal_share']:>8.4f}")
    print(f"written                {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
