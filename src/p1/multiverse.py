"""Core multiverse statistics for Paper 1.

Dependency-light on purpose: numpy only. The statistics layer must be runnable
and testable on any machine, including CI and machines with no GPU, so that the
mathematics can be verified independently of the circuit-discovery pipeline.

Definitions follow the P1 formalism.

    Specification      s = (a, d, m, tau, P, r) in S
    Circuit            C(s), a set of components
    Jaccard distance   D(s_i, s_j) = 1 - |C_i & C_j| / |C_i | C_j|
    Mean Jaccard       J_bar, mean similarity over unordered pairs
    Claim map          phi: 2^H -> Phi
    Flip rate          F = Pr_{i != j}[phi(C_i) != phi(C_j)]
    Modal claim share  pi_star = max_c (count_c / N)
    Filability         evidence is filable at tolerance alpha iff pi_star >= 1 - alpha

Nothing here computes a p-value across specifications. Specifications are a
designed grid, not an independent sample. See the multiverse-stats skill.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Sequence

import numpy as np

__all__ = [
    "jaccard_similarity",
    "jaccard_distance",
    "pairwise_jaccard_similarities",
    "mean_jaccard",
    "flip_rate",
    "flip_rate_bruteforce",
    "modal_share",
    "is_filable",
    "bootstrap_over_specifications",
    "BootstrapResult",
]


# --------------------------------------------------------------------------
# Set overlap
# --------------------------------------------------------------------------


def jaccard_similarity(a: Iterable[Hashable], b: Iterable[Hashable]) -> float:
    """Jaccard similarity |a & b| / |a | b|.

    Convention: two empty circuits are treated as identical, J = 1.0. The
    quantity is otherwise undefined at 0/0. This convention is stated in the
    pre-registration because an empty circuit is a reachable outcome at a
    strict size threshold, and silently returning NaN would propagate into
    J_bar.
    """
    sa, sb = set(a), set(b)
    union = len(sa | sb)
    if union == 0:
        return 1.0
    return len(sa & sb) / union


def jaccard_distance(a: Iterable[Hashable], b: Iterable[Hashable]) -> float:
    """D = 1 - J. Bounded in [0, 1]."""
    return 1.0 - jaccard_similarity(a, b)


def pairwise_jaccard_similarities(
    circuits: Sequence[Iterable[Hashable]],
) -> np.ndarray:
    """Flat array of J over all unordered pairs i < j. Length N(N-1)/2.

    Report the full distribution of these values. A mean alone hides bimodality,
    which is exactly the shape a reviewer will ask about.
    """
    sets = [set(c) for c in circuits]
    n = len(sets)
    if n < 2:
        raise ValueError(f"need at least 2 circuits to form a pair, got {n}")
    return np.array(
        [jaccard_similarity(sets[i], sets[j]) for i, j in combinations(range(n), 2)],
        dtype=float,
    )


def mean_jaccard(circuits: Sequence[Iterable[Hashable]]) -> float:
    """J_bar, the mean pairwise Jaccard similarity.

    This is a U-statistic. Pairs share specifications and are therefore
    dependent. Any resampling must resample specifications, never pairs.
    """
    return float(pairwise_jaccard_similarities(circuits).mean())


# --------------------------------------------------------------------------
# Claim instability
# --------------------------------------------------------------------------


def flip_rate(labels: Sequence[Hashable]) -> float:
    """F, the probability that two distinct specifications disagree.

    Closed form over class counts, exact and O(N):

        F = 1 - sum_c n_c (n_c - 1) / (N (N - 1))

    This is the unbiased Gini-Simpson diversity index of the claim
    distribution. It equals ``flip_rate_bruteforce`` exactly; that equivalence
    is asserted as a property test rather than claimed in prose.

    Integer arithmetic throughout the numerator and denominator, so there is no
    accumulated floating point error before the single final division.
    """
    n = len(labels)
    if n < 2:
        raise ValueError(f"need at least 2 specifications to form a pair, got {n}")
    counts = Counter(labels)
    agreeing_ordered = sum(c * (c - 1) for c in counts.values())
    total_ordered = n * (n - 1)
    return 1.0 - agreeing_ordered / total_ordered


def flip_rate_bruteforce(labels: Sequence[Hashable]) -> float:
    """O(N^2) reference implementation of F. Used only to test ``flip_rate``."""
    n = len(labels)
    if n < 2:
        raise ValueError(f"need at least 2 specifications to form a pair, got {n}")
    pairs = list(combinations(range(n), 2))
    disagreements = sum(1 for i, j in pairs if labels[i] != labels[j])
    return disagreements / len(pairs)


def modal_share(labels: Sequence[Hashable]) -> float:
    """pi_star, the share of specifications yielding the single most common claim."""
    n = len(labels)
    if n == 0:
        raise ValueError("no specifications")
    return max(Counter(labels).values()) / n


def is_filable(labels: Sequence[Hashable], alpha: float) -> bool:
    """Filability criterion: evidence is filable at tolerance alpha iff pi_star >= 1 - alpha.

    alpha is the tolerance a standards body would write into a procedure. This
    is the deliverable that converts a negative finding into a usable criterion,
    so it must be computed from the claim distribution and never eyeballed.
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be in [0, 1], got {alpha}")
    return modal_share(labels) >= 1.0 - alpha


# --------------------------------------------------------------------------
# Bootstrap: resample specifications, never pairs
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class BootstrapResult:
    """Point estimate on the observed grid plus the bootstrap distribution."""

    observed: float
    replicates: np.ndarray
    seed: int

    def percentile_interval(self, level: float = 0.95) -> tuple[float, float]:
        if not 0.0 < level < 1.0:
            raise ValueError(f"level must be in (0, 1), got {level}")
        tail = (1.0 - level) / 2.0
        lo, hi = np.percentile(self.replicates, [100 * tail, 100 * (1 - tail)])
        return float(lo), float(hi)

    def __len__(self) -> int:
        return len(self.replicates)


def bootstrap_over_specifications(
    items: Sequence,
    statistic,
    n_boot: int = 10_000,
    seed: int = 0,
) -> BootstrapResult:
    """Nonparametric bootstrap that resamples SPECIFICATIONS.

    ``items`` is one entry per specification: a circuit for J_bar, a claim label
    for F or pi_star. ``statistic`` maps a sequence of items to a float.

    Why specifications and not pairs. J_bar and F are U-statistics over pairs.
    Pairs sharing a specification are dependent, so resampling the pair list
    directly understates the variance. Resampling specifications propagates the
    dependence correctly, because a specification drawn twice carries all of its
    pairs with it.

    A specification drawn twice also contributes a self-pair with distance 0.
    That is the standard nonparametric bootstrap for U-statistics and it is
    retained deliberately; dropping those pairs would bias J_bar downward and F
    upward.

    What this does and does not license. The interval quantifies uncertainty
    GIVEN the grid. It does not support inference to specifications outside the
    grid. State that in the paper.
    """
    n = len(items)
    if n < 2:
        raise ValueError(f"need at least 2 specifications, got {n}")
    if n_boot < 1:
        raise ValueError(f"n_boot must be positive, got {n_boot}")

    rng = np.random.default_rng(seed)
    observed = float(statistic(items))

    replicates = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        replicates[b] = float(statistic([items[i] for i in idx]))

    return BootstrapResult(observed=observed, replicates=replicates, seed=seed)
