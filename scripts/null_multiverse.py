"""Stage 4. The size-matched random-circuit null, and H3.

PLAN.md section 6 for the null, section 2 for the decision rule. `R` and the seed
are fixed in DEVIATIONS 2026-08-11, before any null value existed.

H3, verbatim from the plan: claim instability for discovered circuits is **not
separated** from size-matched random circuits if the 95% CIs overlap, and
**separated** if the discovered median lies outside the random 95% CI.

Section 2 also states the expectation, recorded before results: at the *circuit*
level the null is almost certainly separated, since a 500-edge circuit has
`J_rand = 0.008`. H3 is deliberately stated about the **claim**, not about
circuit overlap, and that distinction is the substance of the hypothesis. A
result showing separation at the claim level does not weaken the paper; it says
the claim carries information that random circuits do not, which the regulatory
argument needs to be true.

Run:
    python3 scripts/null_multiverse.py --results results/sweep --out results/analysis
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyse import (  # noqa: E402
    BOOTSTRAP_SEED,
    N_BOOT,
    PRIMARY_GRANULARITY,
    PRIMARY_MAP,
    load_records,
)
from p1.claim_map import Granularity, phi_overseer  # noqa: E402
from p1.multiverse import bootstrap_over_specifications, flip_rate, modal_share  # noqa: E402
from p1.null_multiverse import EdgeComponentIndex  # noqa: E402

#: Fixed in DEVIATIONS 2026-08-11. Not tunable from the command line on purpose.
R_NULL = 1_000
NULL_SEED = 0

#: The null cannot reach FINE: `position_mass` was never written to disk.
NULL_GRANULARITIES = (Granularity.COARSE, Granularity.MEDIUM)


def null_distribution(sizes: list[int], granularity: Granularity) -> dict:
    index = EdgeComponentIndex()
    rng = np.random.default_rng(NULL_SEED)
    f_vals = np.empty(R_NULL)
    pi_vals = np.empty(R_NULL)
    for r in range(R_NULL):
        labels = [
            phi_overseer(index.features(index.sample(k, rng)), granularity)
            for k in sizes
        ]
        f_vals[r] = flip_rate(labels)
        pi_vals[r] = modal_share(labels)
    lo, hi = np.percentile(f_vals, [2.5, 97.5])
    return {
        "R": R_NULL,
        "seed": NULL_SEED,
        "F_median": float(np.median(f_vals)),
        "F_mean": float(f_vals.mean()),
        "F_ci95_low": float(lo),
        "F_ci95_high": float(hi),
        "F_min": float(f_vals.min()),
        "F_max": float(f_vals.max()),
        "pi_star_median": float(np.median(pi_vals)),
    }


def decide_h3(discovered: dict, null: dict) -> dict:
    """The pre-registered rule, applied without reinterpretation."""
    d_lo, d_hi = discovered["ci95_low"], discovered["ci95_high"]
    n_lo, n_hi = null["F_ci95_low"], null["F_ci95_high"]
    cis_overlap = not (d_hi < n_lo or n_hi < d_lo)
    median_outside = not (n_lo <= discovered["median"] <= n_hi)
    return {
        "rule": "not separated if the 95% CIs overlap; separated if the "
        "discovered median lies outside the random 95% CI",
        "discovered_median": discovered["median"],
        "discovered_ci95": [d_lo, d_hi],
        "null_ci95": [n_lo, n_hi],
        "cis_overlap": bool(cis_overlap),
        "discovered_median_outside_null_ci": bool(median_outside),
        "verdict": "separated" if median_outside and not cis_overlap else (
            "not separated" if cis_overlap else "ambiguous: median outside but CIs overlap"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--config", type=Path, default=Path("configs/sweep.yaml"))
    ap.add_argument("--out", type=Path, default=Path("results/analysis"))
    args = ap.parse_args()

    axes = yaml.safe_load(args.config.read_text())["axes"]
    records, _ = load_records(args.results, axes)
    sizes = [int(r["edges"]) for r in records]

    report: dict = {
        "stage": 4,
        "plan": "preregistration/PLAN.md sections 2 and 6",
        "constants": "preregistration/DEVIATIONS.md 2026-08-11",
        "n_specifications": len(sizes),
        "scope_limitation": (
            "phi_overseer COARSE and MEDIUM only; FINE and phi_affected need "
            "position_mass, which the sweep never wrote to disk"
        ),
        "by_granularity": {},
    }

    for g in NULL_GRANULARITIES:
        labels = [r["claims"][g.name][PRIMARY_MAP] for r in records]
        boot = bootstrap_over_specifications(
            labels, flip_rate, n_boot=N_BOOT, seed=BOOTSTRAP_SEED
        )
        lo, hi = boot.percentile_interval(0.95)
        discovered = {
            "F": boot.observed,
            "median": float(np.median(boot.replicates)),
            "ci95_low": lo,
            "ci95_high": hi,
            "pi_star": modal_share(labels),
        }
        null = null_distribution(sizes, g)
        entry = {"discovered": discovered, "null": null}
        if g.name == PRIMARY_GRANULARITY:
            entry["h3"] = decide_h3(discovered, null)
            entry["primary"] = True
        report["by_granularity"][g.name] = entry

    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / "stage4_null.json"
    dest.write_text(json.dumps(report, indent=2, sort_keys=True, default=str))

    for name, e in report["by_granularity"].items():
        d, n = e["discovered"], e["null"]
        print(f"\n{name}{'  (PRIMARY)' if e.get('primary') else ''}")
        print(f"  discovered  F {d['F']:.4f}  CI [{d['ci95_low']:.4f}, {d['ci95_high']:.4f}]"
              f"  pi* {d['pi_star']:.4f}")
        print(f"  null        F {n['F_median']:.4f}  CI [{n['F_ci95_low']:.4f}, "
              f"{n['F_ci95_high']:.4f}]  pi* {n['pi_star_median']:.4f}")
        if "h3" in e:
            h = e["h3"]
            print(f"  H3 verdict  {h['verdict'].upper()}"
                  f"   (CIs overlap: {h['cis_overlap']})")
    print(f"\nwritten {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
