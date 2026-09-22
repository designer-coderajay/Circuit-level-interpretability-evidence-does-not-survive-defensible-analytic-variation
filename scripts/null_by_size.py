"""Exploratory diagnostic: where does the null's stability come from?

**Not pre-registered. Not a hypothesis test. No decision depends on it.**

Stage 4 found the discovered multiverse less stable than the size-matched random
null. The obvious objection is that the null is degenerate at large circuit
sizes: a uniform draw of 10,000 edges from 32,491 almost certainly touches all
156 components, so those draws collapse to one claim by construction and depress
null `F`. 2,067 of 7,561 specifications sit at that size.

This script does not re-specify the null. It reports, per circuit size, the flip
rate within that size for the discovered multiverse and for the null, using the
same `F_within` machinery as stage 3 and the same claim map. A reader can then
see exactly which sizes carry the separation.

If the separation holds only where the null is degenerate, the paper says so.

Run:
    python3 scripts/null_by_size.py --out results/analysis
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from null_multiverse import NULL_GRANULARITIES, _replicate_rng  # noqa: E402
from p1.decompose import within_flip_rate  # noqa: E402
from p1.decompose import GroupedLabels  # noqa: E402
from p1.multiverse import flip_rate  # noqa: E402
from p1.null_multiverse import EdgeComponentIndex  # noqa: E402

#: Fewer than stage 4's 1,000. This is descriptive, so the cost of a wide
#: interval is a wider description, not a wrong decision.
R_DIAG = 60


def _bootstrap_within(labels, sizes) -> dict:
    """Bootstrap F_within(size), resampling specifications, B = 10,000, seed 0.

    Valid here where it was not for stage 3's `alone` family: the smallest size
    group holds 199 specifications, so the self-pair inflation is order 1/199.
    `bias` is reported anyway rather than argued away.
    """
    g = GroupedLabels(labels, sizes)
    rng = np.random.default_rng(0)
    n = len(labels)
    reps = np.empty(10_000)
    for b in range(10_000):
        reps[b] = g.flip_rate(rng.integers(0, n, size=n))
    lo, hi = np.percentile(reps, [2.5, 97.5])
    observed = g.flip_rate()
    return {
        "observed": observed,
        "ci95_low": float(lo),
        "ci95_high": float(hi),
        "bias": float(reps.mean()) - observed,
        "interval_quotable": bool(lo <= observed <= hi),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("results/analysis"))
    args = ap.parse_args()

    cached = json.loads((args.out / "stage4_inputs.json").read_text())
    sizes = cached["sizes"]
    names = [g.name for g in NULL_GRANULARITIES]

    index = EdgeComponentIndex()
    null_labels = {n: np.empty((R_DIAG, len(sizes)), dtype=object) for n in names}
    for r in range(R_DIAG):
        rng = _replicate_rng(r)
        for i, k in enumerate(sizes):
            got = index.claims(index.sample(k, rng), NULL_GRANULARITIES)
            for n, claim in zip(names, got, strict=True):
                null_labels[n][r, i] = claim

    ladder = sorted(set(sizes))
    per_gran = {}
    for n in names:
        discovered = cached["labels"][n]
        rows = []
        for k in ladder:
            idx = [i for i, s in enumerate(sizes) if s == k]
            if len(idx) < 2:
                continue
            d_labels = [discovered[i] for i in idx]
            n_vals = [
                flip_rate([null_labels[n][r, i] for i in idx]) for r in range(R_DIAG)
            ]
            rows.append(
                {
                    "size": k,
                    "n_specifications": len(idx),
                    "discovered_F": flip_rate(d_labels),
                    "discovered_classes": len(set(d_labels)),
                    "null_F_median": float(np.median(n_vals)),
                    "null_F_ci95": [
                        float(np.percentile(n_vals, 2.5)),
                        float(np.percentile(n_vals, 97.5)),
                    ],
                    "null_classes_median": float(
                        np.median(
                            [len({null_labels[n][r, i] for i in idx}) for r in range(R_DIAG)]
                        )
                    ),
                }
            )
        per_gran[n] = {
            "by_size": rows,
            "with_size_held_fixed": {
                "discovered_F": within_flip_rate(discovered, sizes),
                "null_F_median": float(
                    np.median(
                        [
                            within_flip_rate(list(null_labels[n][r]), sizes)
                            for r in range(R_DIAG)
                        ]
                    )
                ),
            },
            "pooled_discovered_F": flip_rate(discovered),
            "size_fixed_bootstrap": _bootstrap_within(discovered, sizes),
        }

    report = {
        "status": "EXPLORATORY, not pre-registered, no decision depends on it",
        "purpose": "locate the source of instability across circuit size",
        "R": R_DIAG,
        "by_granularity": per_gran,
    }
    dest = args.out / "stage4_null_by_size.json"
    dest.write_text(json.dumps(report, indent=2, sort_keys=True, default=str))

    for n in names:
        g = per_gran[n]
        print(f"\n=== {n} ===")
        print(f"{'size':>7}{'n':>7}{'disc F':>9}{'null F':>9}{'d cls':>7}{'n cls':>7}")
        for r in g["by_size"]:
            print(
                f"{r['size']:>7,}{r['n_specifications']:>7,}{r['discovered_F']:>9.4f}"
                f"{r['null_F_median']:>9.4f}{r['discovered_classes']:>7}"
                f"{r['null_classes_median']:>7.0f}"
            )
        f = g["with_size_held_fixed"]
        print(
            f"  pooled discovered {g['pooled_discovered_F']:.4f}"
            f"   size fixed: discovered {f['discovered_F']:.4f}"
            f"  null {f['null_F_median']:.4f}"
        )
    print(f"\nwritten {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
