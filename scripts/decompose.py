"""Variance decomposition, stage 3. Two arms, per DEVIATIONS 2026-08-11.

Arm A, pre-registered. REML with one variance component per axis, corruption
nested within ablation, response `log10(selected circuit size in edges)`. Fixed
by PLAN.md section 6 for the estimator and by the DEVIATIONS entry for the
response. **Decomposes structure, not claims.** It does not explain `F` and must
not be reported as if it does.

Arm B, declared deviation. Claim-level decomposition using the within-group flip
rate defined in the same DEVIATIONS entry:

    F_fixed(A)  = F_within({A})                  residual flip once A is standardised
    F_alone(A)  = F_within(all axes except A)    flip driven by A by itself
    ratio       = F_alone(seed) / F_fixed(seed)  seed against analytic choice

Both arms bootstrap over specifications, B = 10,000, seed 0, never over pairs.
One resample index per replicate is shared across every statistic so the
replicates are mutually comparable.

Run:
    python3 scripts/decompose.py --results results/sweep --out results/analysis
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p1.decompose import GroupedLabels  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyse import (  # noqa: E402
    AXES,
    BOOTSTRAP_SEED,
    N_BOOT,
    PRIMARY_GRANULARITY,
    PRIMARY_MAP,
    load_records,
)


def build_groupings(records: list[dict]) -> dict[str, list[tuple]]:
    """One grouping per reported quantity, plus the trivial pooled grouping."""
    groupings: dict[str, list[tuple]] = {"pooled": [("all",)] * len(records)}
    for axis in AXES:
        groupings[f"fixed/{axis}"] = [(r[axis],) for r in records]
        others = tuple(a for a in AXES if a != axis)
        groupings[f"alone/{axis}"] = [tuple(r[a] for a in others) for r in records]
    return groupings


def arm_b(records: list[dict]) -> dict:
    labels = [r["claims"][PRIMARY_GRANULARITY][PRIMARY_MAP] for r in records]
    grouped = {
        name: GroupedLabels(labels, groups)
        for name, groups in build_groupings(records).items()
    }

    observed = {}
    for name, g in grouped.items():
        try:
            observed[name] = g.flip_rate()
        except ZeroDivisionError:
            observed[name] = None

    names = [n for n, v in observed.items() if v is not None]
    n = len(records)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    reps = {name: np.empty(N_BOOT) for name in names}
    ratio_reps = np.empty(N_BOOT)
    degenerate = 0

    for b in range(N_BOOT):
        idx = rng.integers(0, n, size=n)
        try:
            for name in names:
                reps[name][b] = grouped[name].flip_rate(idx)
            fixed_seed = reps["fixed/seed"][b]
            ratio_reps[b] = (
                reps["alone/seed"][b] / fixed_seed if fixed_seed > 0 else np.nan
            )
        except ZeroDivisionError:
            degenerate += 1
            for name in names:
                reps[name][b] = np.nan
            ratio_reps[b] = np.nan

    def interval(arr: np.ndarray, observed_value: float | None = None) -> dict:
        """Interval plus the diagnostics that say whether it may be quoted.

        The pre-registered bootstrap resamples specifications and retains
        self-pairs, documented in `p1.multiverse`. For the pooled outcome that is
        an O(1/N) effect at N = 7,561. For a within-group statistic it is
        O(1/n_g), and the `alone` family has mean group size near two, where it
        dominates and deflates the replicate distribution.

        `bias` makes that visible instead of leaving it for a reader to find. An
        interval whose distance from the observed value is a large fraction of
        its own width is not quotable, and the report says so rather than
        printing it unqualified.
        """
        finite = arr[np.isfinite(arr)]
        lo, hi = np.percentile(finite, [2.5, 97.5])
        out = {
            "ci95_low": float(lo),
            "ci95_high": float(hi),
            "n_finite": int(finite.size),
            "bootstrap_mean": float(finite.mean()),
        }
        if observed_value is not None:
            bias = float(finite.mean()) - observed_value
            width = hi - lo
            out["bias"] = bias
            out["bias_over_width"] = float(bias / width) if width > 0 else None
            out["interval_quotable"] = bool(lo <= observed_value <= hi)
        return out

    out: dict = {
        "definition": "preregistration/DEVIATIONS.md 2026-08-11",
        "status": "declared deviation, not pre-registered",
        "n_specifications": n,
        "bootstrap": {
            "n_boot": N_BOOT,
            "seed": BOOTSTRAP_SEED,
            "resampling_unit": "specification",
            "degenerate_replicates": degenerate,
        },
        "pooled_F": observed["pooled"],
        "by_axis": {},
    }
    for axis in AXES:
        entry = {}
        for kind in ("fixed", "alone"):
            key = f"{kind}/{axis}"
            if observed[key] is None:
                entry[kind] = None
                continue
            entry[kind] = {
                "observed": observed[key],
                "n_groups": grouped[key].n_groups,
                "mean_group_size": n / grouped[key].n_groups,
                **interval(reps[key], observed[key]),
            }
        out["by_axis"][axis] = entry

    ratio_obs = (
        observed["alone/seed"] / observed["fixed/seed"]
        if observed["fixed/seed"]
        else None
    )
    out["headline_seed_ratio"] = {
        "definition": "F_alone(seed) / F_fixed(seed)",
        "observed": ratio_obs,
        **interval(ratio_reps, ratio_obs),
    }
    return out


def arm_a(records: list[dict]) -> dict:
    """REML variance components on log10(selected edges). Structural, not claims."""
    try:
        import pandas as pd
        from statsmodels.regression.mixed_linear_model import MixedLM
    except ImportError as exc:
        return {"status": f"not run: {exc}"}

    df = pd.DataFrame(
        {
            **{a: [str(r[a]) for r in records] for a in AXES},
            "y": [np.log10(r["edges"]) for r in records],
            "one": 1,
        }
    )

    vc = {
        "objective": "0 + C(discovery_objective)",
        "ablation": "0 + C(ablation)",
        # nested, per PLAN.md section 4: corruption is meaningful only inside an
        # ablation operator, and two operators carry the n/a sentinel.
        "corruption_in_ablation": "0 + C(ablation):C(corruption)",
        "metric": "0 + C(metric)",
        "threshold": "0 + C(threshold)",
        "prompt_variant": "0 + C(prompt_variant)",
        "seed": "0 + C(seed)",
    }

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MixedLM.from_formula("y ~ 1", groups="one", vc_formula=vc, data=df)
        fit = model.fit(reml=True)

    comps = {k: float(v) for k, v in fit.vcomp_dict.items()} if hasattr(
        fit, "vcomp_dict"
    ) else dict(zip(vc.keys(), (float(v) for v in fit.vcomp)))
    residual = float(fit.scale)
    total = sum(comps.values()) + residual

    return {
        "status": "pre-registered estimator, REML",
        "response": "log10(selected circuit size in edges)",
        "caveat": "decomposes structure, not claims; does not explain F",
        "n": len(df),
        "components": comps,
        "residual": residual,
        "share_of_total": {k: v / total for k, v in comps.items()}
        | {"residual": residual / total},
        "converged": bool(fit.converged),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--config", type=Path, default=Path("configs/sweep.yaml"))
    ap.add_argument("--out", type=Path, default=Path("results/analysis"))
    args = ap.parse_args()

    axes = yaml.safe_load(args.config.read_text())["axes"]
    records, _ = load_records(args.results, axes)

    report = {
        "stage": 3,
        "plan": "preregistration/PLAN.md section 6",
        "arm_b_claim_level": arm_b(records),
        "arm_a_structural_reml": arm_a(records),
    }

    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / "stage3_decomposition.json"
    dest.write_text(json.dumps(report, indent=2, sort_keys=True, default=str))

    b = report["arm_b_claim_level"]
    print(f"pooled F {b['pooled_F']:.4f}   n = {b['n_specifications']:,}\n")
    print(f"{'axis':<22}{'F_fixed':>9}{'F_alone':>9}{'grp':>7}   removes    CI")
    for axis, e in b["by_axis"].items():
        fx = e["fixed"]["observed"] if e["fixed"] else float("nan")
        al = e["alone"]["observed"] if e["alone"] else float("nan")
        gs = e["alone"]["mean_group_size"] if e["alone"] else float("nan")
        ok = "ok" if e["alone"] and e["alone"]["interval_quotable"] else "BIASED"
        print(
            f"{axis:<22}{fx:>9.4f}{al:>9.4f}{gs:>7.1f}   "
            f"{b['pooled_F'] - fx:>+.4f}   alone {ok}"
        )
    r = b["headline_seed_ratio"]
    print(
        f"\nseed / analytic ratio  {r['observed']:.4f}  "
        f"[{r['ci95_low']:.4f}, {r['ci95_high']:.4f}]"
    )
    print(f"written {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
