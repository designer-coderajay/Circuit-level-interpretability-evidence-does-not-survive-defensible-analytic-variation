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


def load_records(results_dir: Path, axes: dict) -> tuple[list[dict], dict]:
    """One record per specification that produced a claim, plus a cell audit.

    A cell contributes nothing unless its manifest reports `status: ok`, and a
    specification contributes nothing unless its own status is `ok`. Discards are
    counted, never repaired, per PLAN.md section 7.
    """
    from p1.spec import enumerate_grid

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
