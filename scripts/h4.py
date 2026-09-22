"""H4: filings differ where mechanisms do not.

PLAN.md section 2 states H4 as

    F - (1 - agreement_rate) > 0.10

with `F` the claim flip rate, the primary outcome, and `agreement_rate` the
per-example functional agreement between two circuits, defined in DESIGN-DELTAS
D4 and reproduced verbatim in `p1.agreement`. Threshold 0.10 fixed 2026-08-06 and
not revisited.

Read plainly: **how much more do the filings disagree than the mechanisms do.**
If two circuits behave the same on every example but the claims derived from them
differ, the difference is manufactured by the analysis and the claim map, not
found in the model. That gap is the quantity.

The same pair population as `F`. Both terms range over unordered pairs of the
7,561 specifications that produced a claim, each pair counted once. Anything else
would compare two different things and call the difference a finding.

**This also answers red-team objection F1.** 2606.06267 report that structurally
distinct circuits can implement the same computation, and P1's circuits are
structurally near-disjoint at `J_bar = 0.1396`. Without a functional measurement
the paper could not tell "the evidence is unstable" from "these circuits do the
same thing and the claim map is reading noise". `1 - agreement_rate` is that
measurement. **A high agreement rate does not weaken the paper; it sharpens it**,
because a claim that flips while behaviour does not is a claim about the analyst
rather than about the model.

Cohen's kappa is reported alongside, and it matters. Raw agreement is inflated
when both circuits are mostly correct, which on IOI they are. Reporting agreement
alone would overstate functional equivalence, which is the direction that
flatters this argument, so it is the direction to be most careful about.

Efficiency, matching `scripts/jbar.py`. Verdicts depend on `(discovery cell,
selected rung)`, so 7,561 specifications share 3,218 distinct verdict vectors of
128 booleans. Pairwise agreement over distinct vectors is two matrix products,
and specification-level means follow by multiplicity weighting. Exact, not
sampled.

Run:
    python3 scripts/h4.py --results results/sweep --repair results/repair
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyse import PRIMARY_GRANULARITY, PRIMARY_MAP, load_records  # noqa: E402
from p1.agreement import agreement_rate, cohens_kappa  # noqa: E402
from p1.multiverse import flip_rate  # noqa: E402

N_BOOT = 10_000
BOOTSTRAP_SEED = 0
H4_THRESHOLD = 0.10


def load_verdicts(repair: Path, records: list[dict], results: Path):
    """One verdict vector per specification, deduplicated by (cell, rung).

    Returns the distinct vectors, their multiplicities, and the claim labels
    aligned to the same distinct index, so `F` and the agreement terms are
    computed over one pair population rather than two.
    """
    cell_of: dict[str, str] = {}
    for cell in sorted(p for p in results.iterdir() if p.is_dir()):
        man = json.loads((cell / "manifest.json").read_text())
        if man.get("status") != "ok":
            continue
        payload = json.loads((cell / "result.json").read_text())
        for spec_id in payload["specifications"]:
            cell_of[spec_id] = cell.name

    cache: dict[str, dict] = {}
    seen: dict[tuple[str, int], int] = {}
    vectors: list[np.ndarray] = []
    counts: list[int] = []
    labels: list[str] = []
    missing = 0

    for r in records:
        cell = cell_of[r["spec_id"]]
        if cell not in cache:
            path = repair / cell / "verdicts.json"
            if not path.exists():
                missing += 1
                continue
            cache[cell] = json.loads(path.read_text())
        blob = cache[cell]
        if blob.get("status") != "ok":
            missing += 1
            continue
        key = (cell, r["edges"])
        idx = seen.get(key)
        if idx is None:
            v = blob["verdicts"][str(r["edges"])]
            vec = np.array([bool(v[str(i)]) for i in range(len(v))], dtype=bool)
            idx = len(vectors)
            seen[key] = idx
            vectors.append(vec)
            counts.append(0)
            labels.append(r["claims"][PRIMARY_GRANULARITY][PRIMARY_MAP])
        counts[idx] += 1

    return (
        np.array(vectors),
        np.array(counts, dtype=np.float64),
        labels,
        missing,
    )


def pair_matrices(V: np.ndarray):
    """Agreement and kappa between every pair of distinct verdict vectors."""
    n_ex = V.shape[1]
    A = V.astype(np.float32)
    B = (~V).astype(np.float32)
    p_o = (A @ A.T + B @ B.T) / n_ex          # observed agreement
    pos = A.mean(axis=1)                       # marginal positive rate
    p_e = np.outer(pos, pos) + np.outer(1 - pos, 1 - pos)
    with np.errstate(divide="ignore", invalid="ignore"):
        kappa = (p_o - p_e) / (1.0 - p_e)
    # Upstream returns exactly 1.0 when p_e == 1.0. Reproduced, not corrected.
    kappa = np.where(np.isclose(p_e, 1.0), 1.0, kappa)
    return p_o.astype(np.float64), kappa.astype(np.float64)


def weighted_pair_mean(M: np.ndarray, w: np.ndarray) -> float:
    """Mean of M over unordered specification pairs, diagonal excluded."""
    total = float(w @ (M @ w))
    n = float(w.sum())
    return (total - n) / (n * (n - 1.0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--repair", type=Path, default=Path("results/repair"))
    ap.add_argument("--config", type=Path, default=Path("configs/sweep.yaml"))
    ap.add_argument("--out", type=Path, default=Path("results/analysis"))
    args = ap.parse_args()

    import yaml

    axes = yaml.safe_load(args.config.read_text())["axes"]
    records, _ = load_records(args.results, axes)
    V, w, labels, missing = load_verdicts(args.repair, records, args.results)
    n = float(w.sum())
    print(f"specifications {int(n):,}  distinct verdict vectors {len(V):,}  "
          f"missing {missing}  examples {V.shape[1]}")

    # Spot-check the vectorised matrices against the verbatim scalar functions.
    p_o, kappa = pair_matrices(V)
    rng = np.random.default_rng(0)
    for _ in range(8):
        i, j = rng.integers(0, len(V), size=2)
        a = {k: bool(x) for k, x in enumerate(V[i])}
        b = {k: bool(x) for k, x in enumerate(V[j])}
        assert abs(p_o[i, j] - agreement_rate(a, b)) < 1e-6, (i, j)
        assert abs(kappa[i, j] - cohens_kappa(a, b)) < 1e-6, (i, j)
    print("  vectorised agreement and kappa match p1.agreement on 8 sampled pairs")

    F = flip_rate([lab for lab, c in zip(labels, w.astype(int), strict=True) for _ in range(c)])
    agreement = weighted_pair_mean(p_o, w)
    kappa_mean = weighted_pair_mean(kappa, w)
    functional_instability = 1.0 - agreement
    gap = F - functional_instability

    boot_rng = np.random.default_rng(BOOTSTRAP_SEED)
    reps = np.empty(N_BOOT)
    block = 500
    for start in range(0, N_BOOT, block):
        size = min(block, N_BOOT - start)
        W = boot_rng.multinomial(int(n), w / n, size=size).astype(np.float32).T
        tot = np.einsum("ij,ij->j", W, p_o.astype(np.float32) @ W)
        agree_b = (tot - n) / (n * (n - 1.0))
        reps[start:start + size] = F - (1.0 - agree_b)
    lo, hi = np.percentile(reps, [2.5, 97.5])

    report = {
        "hypothesis": "H4: filings differ where mechanisms do not",
        "rule": f"F - (1 - agreement_rate) > {H4_THRESHOLD}",
        "n_specifications": int(n),
        "n_distinct_verdict_vectors": int(len(V)),
        "n_examples": int(V.shape[1]),
        "specifications_without_verdicts": missing,
        "F": F,
        "agreement_rate": agreement,
        "cohens_kappa": kappa_mean,
        "functional_instability": functional_instability,
        "gap": gap,
        "gap_ci95": [float(lo), float(hi)],
        "threshold": H4_THRESHOLD,
        "supported": bool(gap > H4_THRESHOLD),
        "ci_lower_above_threshold": bool(lo > H4_THRESHOLD),
        "bootstrap": {"n_boot": N_BOOT, "seed": BOOTSTRAP_SEED,
                      "resampling_unit": "specification",
                      "note": "F held fixed; agreement resampled"},
    }
    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / "h4.json"
    dest.write_text(json.dumps(report, indent=2, sort_keys=True, default=str))

    print(f"\nF (claim instability)        {F:.4f}")
    print(f"agreement rate               {agreement:.4f}")
    print(f"Cohen's kappa                {kappa_mean:.4f}")
    print(f"functional instability       {functional_instability:.4f}")
    print(f"gap                          {gap:.4f}   95% CI [{lo:.4f}, {hi:.4f}]")
    print(f"threshold                    {H4_THRESHOLD}")
    print(f"\nH4 {'SUPPORTED' if gap > H4_THRESHOLD else 'NOT SUPPORTED'}")
    print(f"written {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
