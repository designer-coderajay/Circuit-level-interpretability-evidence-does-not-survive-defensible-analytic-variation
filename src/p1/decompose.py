"""Within-group flip rates, the claim-level decomposition of arm B.

Definitions are fixed in `preregistration/DEVIATIONS.md`, 2026-08-11, and were
committed before any value was computed. Nothing here chooses anything.

For a set of grouping axes ``G``:

    F_within(G) = 1 - [ sum_g sum_c n_gc (n_gc - 1) ] / [ sum_g n_g (n_g - 1) ]

With ``G`` empty this reduces to the pooled flip rate of `p1.multiverse
.flip_rate`, which is asserted by test rather than assumed.

Why this shape. The pooled `F` counts every unordered pair once. Conditioning on
a group restricts the pair population to pairs sharing that group, and the ratio
of sums, not a mean of per-group rates, keeps every pair weighted equally. A mean
of per-group rates would give a two-specification group the same weight as a
two-hundred one.

The implementation is integer counting on label codes, so it is exact. No
floating point enters before the final division.
"""

from __future__ import annotations

from collections.abc import Hashable, Sequence

import numpy as np

__all__ = [
    "GroupedLabels",
    "encode",
    "within_flip_rate",
]


class GroupedLabels:
    """Integer-coded labels and group keys, prepared once and resampled cheaply.

    Bootstrapping recomputes the same statistic ten thousand times. Encoding the
    labels and groups once turns each replicate into a single ``bincount``, which
    is what makes ``B = 10,000`` over eight axes tractable on a laptop.
    """

    def __init__(self, labels: Sequence[Hashable], groups: Sequence[Hashable]):
        if len(labels) != len(groups):
            raise ValueError(
                f"labels and groups differ in length: {len(labels)} vs {len(groups)}"
            )
        if len(labels) < 2:
            raise ValueError(f"need at least 2 specifications, got {len(labels)}")
        self.label_code, self.n_labels = encode(labels)
        self.group_code, self.n_groups = encode(groups)
        self.combined = self.group_code * self.n_labels + self.label_code
        self.size = self.n_groups * self.n_labels

    def flip_rate(self, index: np.ndarray | None = None) -> float:
        codes = self.combined if index is None else self.combined[index]
        counts = np.bincount(codes, minlength=self.size).reshape(
            self.n_groups, self.n_labels
        )
        return _rate_from_counts(counts)


def encode(values: Sequence[Hashable]) -> tuple[np.ndarray, int]:
    """Map hashables to contiguous integer codes. Order is insertion order."""
    lookup: dict[Hashable, int] = {}
    codes = np.empty(len(values), dtype=np.int64)
    for i, v in enumerate(values):
        code = lookup.get(v)
        if code is None:
            code = len(lookup)
            lookup[v] = code
        codes[i] = code
    return codes, len(lookup)


def _rate_from_counts(counts: np.ndarray) -> float:
    """counts is (n_groups, n_labels) of specification counts."""
    per_group = counts.sum(axis=1)
    concordant = int((counts * (counts - 1)).sum())
    total = int((per_group * (per_group - 1)).sum())
    if total == 0:
        raise ZeroDivisionError(
            "no within-group pairs: every group holds at most one specification, "
            "so a within-group flip rate is undefined for this grouping"
        )
    return 1.0 - concordant / total


def within_flip_rate(
    labels: Sequence[Hashable], groups: Sequence[Hashable]
) -> float:
    """F_within for one grouping. Convenience wrapper over GroupedLabels."""
    return GroupedLabels(labels, groups).flip_rate()
