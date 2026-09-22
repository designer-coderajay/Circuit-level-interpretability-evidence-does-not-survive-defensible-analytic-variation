"""Metric-relative tau: turning a faithfulness curve into a circuit.

`tau` is metric-relative, so `C(s)` is "the smallest circuit recovering
`(1 - tau)` of metric `m` on the full model". Two things have to be pinned down
before that sentence picks out a circuit, and both are researcher degrees of
freedom of exactly the kind this paper is about.

**What "recovering" means.** Fixed 2026-08-06 by Ajay as normalised gap closing:

    recovery(C) = (m(C) - m(empty)) / (m(full) - m(empty))

where `m(empty)` is the fully ablated model and `m(full)` the unablated one. One
convention for all four metrics.

The alternative, a plain ratio `m(C) / m(full)`, fails for `kl_div`: the KL
between the full model and itself is zero, so the ratio is undefined and the
metric would need its own convention. Two conventions inside one axis would mean
a claim shift across metrics was partly a shift across normalisations, which is
the confound the metric axis exists to avoid.

Gap closing also handles metric direction without special cases. For `kl_div`,
lower is better and `m(full) = 0`, so the formula reduces to
`1 - KL(C) / KL(empty)`, which increases as the circuit approaches the full
model. No per-metric sign handling, and therefore no per-metric bug.

**Where the circuit is located.** The upward ladder scan, fixed 2026-08-05 and
implemented in `select_rung`. See `p1.spec.EDGE_COUNT_LADDER`.

No torch here. The metric values arrive as scalars from the runner; everything
that decides which circuit `C(s)` is stays pure and testable on any machine.
"""

from __future__ import annotations

from typing import Sequence

__all__ = ["DegenerateMetric", "normalised_recovery", "select_rung"]


class DegenerateMetric(ValueError):
    """The metric does not distinguish the full model from the empty one.

    Raised rather than returned so it cannot be mistaken for a recovery value.
    A run that triggers this is **discarded** under PLAN.md section 7, and the
    discard is reported per axis level rather than repaired.
    """


def normalised_recovery(m_circuit: float, m_empty: float, m_full: float) -> float:
    """Fraction of the empty-to-full gap that the circuit closes.

    Not clipped to [0, 1]. A circuit can overshoot the full model on a noisy
    metric, and a circuit can be worse than the empty model. Clipping would hide
    both, and the second is a signal that something is wrong with the run rather
    than a value to be tidied away. The ladder scan handles values above 1
    correctly without needing them bounded.

    Raises:
        DegenerateMetric: if the full and empty models score identically, so the
            metric carries no information on this item and no threshold on it
            can select a circuit.
    """
    denom = m_full - m_empty
    if denom == 0:
        raise DegenerateMetric(
            f"metric does not separate the full model from the empty one "
            f"(both {m_full}); no recovery threshold can select a circuit"
        )
    return (m_circuit - m_empty) / denom


def select_rung(
    recoveries: Sequence[float],
    ladder: Sequence[int],
    tau: float,
) -> int | None:
    """The smallest ladder rung whose recovery reaches `1 - tau`.

    Args:
        recoveries: One recovery value per rung, in the same order as `ladder`.
        ladder: Ascending edge counts, `p1.spec.EDGE_COUNT_LADDER`.
        tau: In (0, 1). The circuit must recover `1 - tau` of the gap.

    Returns:
        The selected edge count, or **`None` if no rung reaches the threshold**,
        in which case the specification is discarded under PLAN.md section 7. It
        is not repaired, and it is not silently given the largest rung: a
        specification that needs more than 10,000 edges to recover `(1 - tau)` is
        not an explanation.

    **Upward scan, first rung that qualifies.** Recovery is not guaranteed
    monotone in edge count, and an upward scan is well defined either way. This
    is why bisection was rejected: it assumes a monotonicity the faithfulness
    curve does not guarantee. See PLAN.md section 4.
    """
    if len(recoveries) != len(ladder):
        raise ValueError(
            f"{len(recoveries)} recovery values for {len(ladder)} rungs; they "
            f"must correspond one to one and in the same order"
        )
    if not 0.0 < tau < 1.0:
        raise ValueError(f"tau must lie in (0, 1), got {tau}")
    if list(ladder) != sorted(ladder):
        raise ValueError("ladder must be ascending; the scan relies on its order")

    target = 1.0 - tau
    for rung, rec in zip(ladder, recoveries, strict=True):
        if rec >= target:
            return rung
    return None
