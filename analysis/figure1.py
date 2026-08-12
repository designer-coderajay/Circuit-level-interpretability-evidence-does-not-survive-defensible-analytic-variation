"""Figure 1. The specification curve, adapted for a categorical outcome.

Form fixed in `preregistration/DEVIATIONS.md`, 2026-08-11, before any version of
this figure existed. The pre-registered form assumes a continuous effect per
specification and P1's outcome is a claim class, so the adaptation is declared as
a deviation rather than presented as the plan's figure.

Upper panel: claim class against specification rank, classes ordered by
frequency. The curve is a staircase; the width of each step is that class's share
of the specification space, so the modal step's width is `pi*` read off the axis.
The null multiverse is overlaid as its own staircase.

Lower panel: the dot matrix the plan asks for. One row per axis level, marked
where that level is active, in the same specification order as above.

Run:
    python3 analysis/figure1.py --out paper/figures
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from analyse import AXES, PRIMARY_GRANULARITY, PRIMARY_MAP, load_records  # noqa: E402
from p1.multiverse import flip_rate, modal_share  # noqa: E402

AXIS_LABEL = {
    "discovery_objective": "objective",
    "ablation": "ablation",
    "corruption": "corruption",
    "metric": "metric",
    "threshold": "tau",
    "prompt_variant": "prompt",
    "seed": "seed",
}


def short(level: str) -> str:
    """Axis level names are long; the dot matrix needs them short but honest."""
    s = str(level)
    s = s.replace("_GRAD_PRUNE_ALGO", "").replace("_PRUNE_ALGO", "")
    s = s.replace("TOKENWISE_MEAN_", "TW_").replace("BATCH_", "B_")
    return s if len(s) <= 18 else s[:17] + "."


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=Path("results/sweep"))
    ap.add_argument("--config", type=Path, default=Path("configs/sweep.yaml"))
    ap.add_argument("--analysis", type=Path, default=Path("results/analysis"))
    ap.add_argument("--out", type=Path, default=Path("paper/figures"))
    args = ap.parse_args()

    axes_cfg = yaml.safe_load(args.config.read_text())["axes"]
    records, _ = load_records(args.results, axes_cfg)
    labels = [r["claims"][PRIMARY_GRANULARITY][PRIMARY_MAP] for r in records]

    counts = Counter(labels)
    rank = {c: i for i, (c, _) in enumerate(counts.most_common())}
    order = sorted(
        range(len(records)),
        key=lambda i: (rank[labels[i]], records[i]["edges"]),
    )
    y = np.array([rank[labels[i]] for i in order])
    n = len(order)

    F = flip_rate(labels)
    pi = modal_share(labels)

    # Null staircase, from the same claim map, for overlay.
    null_path = args.analysis / "stage4_null.json"
    null_y = None
    if null_path.exists():
        null = json.loads(null_path.read_text())["by_granularity"][PRIMARY_GRANULARITY]
        null_pi = null["null"]["pi_star_median"]
        # The null's class shares are not stored per class, only pi*. Draw the
        # modal share as a single reference step rather than inventing a curve.
        null_y = null_pi

    fig = plt.figure(figsize=(9.5, 8.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.05, 1.95], hspace=0.06)

    ax = fig.add_subplot(gs[0])
    ax.step(np.arange(n), y, where="post", lw=1.6, color="#1f2933")
    ax.fill_between(np.arange(n), y, step="post", alpha=0.10, color="#1f2933")
    modal_n = counts.most_common(1)[0][1]
    ax.axvspan(0, modal_n, alpha=0.13, color="#c05621", lw=0)
    ax.text(modal_n * 0.5, len(counts) - 0.55,
            f"modal claim\n$\\pi^*$ = {pi:.3f}", ha="center", va="top", fontsize=9)
    if null_y is not None:
        ax.axvline(null_y * n, ls="--", lw=1.2, color="#2b6cb0")
        ax.text(null_y * n + n * 0.01, 0.15,
                f"null modal share {null_y:.3f}", fontsize=8, color="#2b6cb0")
    ax.set_ylabel("claim class, ranked by frequency")
    ax.set_yticks(range(len(counts)))
    ax.set_xlim(0, n)
    ax.set_ylim(-0.4, len(counts) - 0.4)
    ax.set_xticklabels([])
    ax.set_title(
        f"Annex IV claim across {n:,} specifications   "
        f"F = {F:.4f}   {len(counts)} distinct claims",
        fontsize=11, loc="left",
    )
    ax.grid(axis="y", alpha=0.25, lw=0.5)

    # Dot matrix.
    rows: list[tuple[str, str]] = []
    for a in AXES:
        for lvl in sorted({str(r[a]) for r in records}, key=str):
            rows.append((a, lvl))
    mat = np.zeros((len(rows), n), dtype=np.uint8)
    for col, i in enumerate(order):
        for r_i, (a, lvl) in enumerate(rows):
            if str(records[i][a]) == lvl:
                mat[r_i, col] = 1

    ax2 = fig.add_subplot(gs[1], sharex=ax)
    ax2.imshow(mat, aspect="auto", cmap="Greys", interpolation="nearest",
               extent=(0, n, len(rows) - 0.5, -0.5), vmin=0, vmax=1.4)
    ax2.set_yticks(range(len(rows)))
    ax2.set_yticklabels([f"{AXIS_LABEL[a]}: {short(l)}" for a, l in rows], fontsize=6.5)
    boundary = 0
    for a in AXES[:-1]:
        boundary += len({str(r[a]) for r in records})
        ax2.axhline(boundary - 0.5, color="white", lw=1.6)
    ax2.set_xlabel("specifications, ordered by claim class then circuit size")

    args.out.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(args.out / f"figure1_specification_curve.{ext}",
                    bbox_inches="tight", dpi=200)
    print(f"specifications {n:,}  classes {len(counts)}  F {F:.4f}  pi* {pi:.4f}")
    print("class shares:", [round(c / n, 4) for _, c in counts.most_common()])
    print(f"written {args.out}/figure1_specification_curve.pdf and .png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
