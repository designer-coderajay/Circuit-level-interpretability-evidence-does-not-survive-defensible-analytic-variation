"""Stage 2. `J_bar` and the pairwise `D` distribution, PLAN.md P0.

P0 is a **premise, not a tested hypothesis**: expected pairwise circuit overlap
across specifications, reported for calibration against 2606.06267 and against
the analytic random line `J_rand = k / (2N - k)` adopted from their calibration
script. No decision depends on it.

Two structural facts make an exact computation cheap enough to avoid sampling
pairs, which the plan's "full distribution of pairwise D" would not tolerate.

1. **Circuits repeat.** A circuit is fixed by `(discovery cell, selected rung)`,
   and 7,561 specifications share only 3,218 distinct circuits. Pairs of
   specifications holding the same circuit have `J = 1` exactly, so the 28.6M
   specification pairs reduce to 5.2M distinct-circuit pairs plus a closed form.
2. **Sets are dense bitmaps.** 32,491 edges is 508 machine words. Python's
   arbitrary-precision `int` gives `&` and `.bit_count()` in C, so an
   intersection costs microseconds and no per-element Python loop is needed.

`J_bar` over specification pairs, with `M` the distinct-circuit similarity matrix
carrying 1 on its diagonal and `w` the multiplicities:

    sum over ordered i != j of J  =  w' M w  -  N
    J_bar                          = (w' M w - N) / (N (N - 1))

The subtraction removes the N self-pairs a specification forms with itself, which
`w' M w` counts and the U-statistic does not.

Bootstrap over specifications, B = 10,000, seed 0, as section 6 fixes. Resampling
specifications is exactly a multinomial redraw of `w`, and every replicate is one
matrix-vector product, so the whole bootstrap is a single BLAS call per block.

Run:
    python3 scripts/jbar.py --results results/sweep --out results/analysis
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from p1.graph import enumerate_edges  # noqa: E402
from p1.multiverse import expected_random_jaccard, jaccard_similarity  # noqa: E402

N_BOOT = 10_000
BOOTSTRAP_SEED = 0


def build_circuits(results: Path, cache: Path) -> tuple[list[int], np.ndarray, np.ndarray]:
    """Distinct circuits as bitmasks, their multiplicities, and their sizes."""
    if cache.exists():
        store = np.load(cache, allow_pickle=True)
        return list(store["masks"]), store["w"], store["k"]

    edge_id = {name: i for i, name in enumerate(enumerate_edges())}
    seen: dict[tuple[str, int], int] = {}
    masks: list[int] = []
    counts: list[int] = []
    sizes: list[int] = []

    for cell in sorted(p for p in results.iterdir() if p.is_dir()):
        man = json.loads((cell / "manifest.json").read_text())
        if man.get("status") != "ok":
            continue
        payload = json.loads((cell / "result.json").read_text())
        top = payload["top_edges"]
        # Selected rungs nest, so each extends the previous mask rather than
        # rebuilding it. A cell selecting 10, 500 and 10,000 edges costs 10,000
        # bit sets in total, not 10,510.
        rungs = sorted(
            {e["edges"] for e in payload["specifications"].values()
             if e.get("status") == "ok"}
        )
        by_k: dict[int, int] = {}
        prefix_mask = 0
        built = 0
        for k in rungs:
            for name in top[built:k]:
                prefix_mask |= 1 << edge_id[name]
            built = k
            by_k[k] = prefix_mask

        for e in payload["specifications"].values():
            if e.get("status") != "ok":
                continue
            key = (cell.name, e["edges"])
            idx = seen.get(key)
            if idx is None:
                idx = len(masks)
                seen[key] = idx
                masks.append(by_k[e["edges"]])
                counts.append(0)
                sizes.append(e["edges"])
            counts[idx] += 1

    w = np.array(counts, dtype=np.float64)
    k = np.array(sizes, dtype=np.int64)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache, masks=np.array(masks, dtype=object), w=w, k=k)
    return masks, w, k


def similarity_matrix(
    masks: list[int], sizes: np.ndarray, cache: Path, budget_s: float
) -> np.ndarray | None:
    """Upper-triangular Jaccard matrix, filled in resumable row blocks."""
    import time

    d = len(masks)
    if cache.exists():
        store = np.load(cache)
        M, done = store["M"], int(store["done"])
    else:
        M, done = np.eye(d, dtype=np.float32), 0

    started = time.time()
    while done < d and time.time() - started < budget_s:
        a = masks[done]
        ka = int(sizes[done])
        row = M[done]
        for b in range(done + 1, d):
            inter = (a & masks[b]).bit_count()
            row[b] = inter / (ka + int(sizes[b]) - inter)
        M[done, :done] = M[:done, done]
        done += 1

    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache, M=M, done=done)
    print(f"  similarity rows {done}/{d}")
    if done < d:
        return None
    M = np.maximum(M, M.T)
    return M


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--out", type=Path, default=Path("results/analysis"))
    ap.add_argument("--budget-seconds", type=float, default=85.0)
    args = ap.parse_args()

    masks, w, k = build_circuits(args.results, args.out / "stage2_circuits.npz")
    d = len(masks)
    n = float(w.sum())
    print(f"  distinct circuits {d:,}  specifications {int(n):,}")

    # The bitmask intersection is an optimisation, so it is checked against the
    # set-based definition in `p1.multiverse` rather than trusted. Cheap: a
    # handful of pairs, decoded back to edge-index sets.
    check_rng = np.random.default_rng(0)
    for _ in range(12):
        a, b = check_rng.integers(0, d, size=2)
        if a == b:
            continue
        set_a = {i for i in range(32_491) if masks[a] >> i & 1}
        set_b = {i for i in range(32_491) if masks[b] >> i & 1}
        inter = (masks[a] & masks[b]).bit_count()
        fast = inter / (int(k[a]) + int(k[b]) - inter)
        assert abs(fast - jaccard_similarity(set_a, set_b)) < 1e-12, (a, b)
    print("  bitmask Jaccard agrees with p1.multiverse on 12 sampled pairs")

    M = similarity_matrix(masks, k, args.out / "stage2_M.npz", args.budget_seconds)
    if M is None:
        print("\nnot finished; rerun the same command to resume")
        return 0

    def jbar(weights: np.ndarray) -> float:
        total = float(weights @ (M @ weights))
        m = float(weights.sum())
        return (total - m) / (m * (m - 1.0))

    observed = jbar(w)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    reps = np.empty(N_BOOT)
    block = 1_000
    for start in range(0, N_BOOT, block):
        size = min(block, N_BOOT - start)
        W = rng.multinomial(int(n), w / n, size=size).astype(np.float32).T
        totals = np.einsum("ij,ij->j", W, M @ W)
        reps[start : start + size] = (totals - n) / (n * (n - 1.0))
    lo, hi = np.percentile(reps, [2.5, 97.5])

    # Full distribution of pairwise D over specification pairs, exactly weighted.
    pair_w = np.outer(w, w).astype(np.float64)
    np.fill_diagonal(pair_w, w * (w - 1.0))
    flat_d = (1.0 - M.astype(np.float64)).ravel()
    flat_w = pair_w.ravel()
    order = np.argsort(flat_d)
    flat_d, flat_w = flat_d[order], flat_w[order]
    cum = np.cumsum(flat_w)
    quantiles = {
        str(q): float(flat_d[np.searchsorted(cum, q * cum[-1])])
        for q in (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
    }

    report = {
        "stage": 2,
        "outcome": "P0, premise not tested; PLAN.md sections 2 and 6",
        "n_specifications": int(n),
        "n_distinct_circuits": d,
        "J_bar": observed,
        "J_bar_ci95": [float(lo), float(hi)],
        "J_bar_bootstrap": {
            "n_boot": N_BOOT,
            "seed": BOOTSTRAP_SEED,
            "resampling_unit": "specification",
            "mean": float(reps.mean()),
            "bias": float(reps.mean()) - observed,
        },
        "pairwise_D_quantiles": quantiles,
        "analytic_random_line": {
            str(int(kk)): expected_random_jaccard(int(kk), 32_491)
            for kk in sorted(set(k.tolist()))
        },
        "median_circuit_size": int(np.median(k)),
    }
    dest = args.out / "stage2_jbar.json"
    dest.write_text(json.dumps(report, indent=2, sort_keys=True, default=str))

    print(f"\nJ_bar {observed:.4f}   95% CI [{lo:.4f}, {hi:.4f}]")
    print("pairwise D quantiles: " + "  ".join(
        f"{q}={v:.3f}" for q, v in quantiles.items()))
    print(f"written {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
