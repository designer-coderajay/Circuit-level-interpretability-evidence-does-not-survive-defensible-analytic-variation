"""Input-segment attribution for `phi_affected`.

`phi_affected` targets Article 86(1), the affected person's right to an
explanation of a decision about them, and it needs to say which part of the
*input* drove the output. That requires a `position_mass`: a distribution over
labelled input segments. Nothing computed one until 2026-08-06, so
`phi_affected` would have emitted a single constant claim across the whole grid
and reported a flip rate of exactly zero as an artifact of a missing function.

Method, fixed in `preregistration/CALIBRATION.md` section 3b: **mean attention
probability over labelled input segments, at the final query position, uniform
across the attention heads in the circuit.**

Precedent, and why this is cited rather than invented: arXiv:2211.00593 Figure 10
plots "Average attention probability of Name Mover Heads" across the IO, S and S2
positions. Attention over labelled segments is the source paper's own way of
saying where a circuit looks.

**The objection, owned rather than hidden.** Attention is contested as an
explanation (Jain and Wallace 2019; Wiegreffe and Pinter 2019). P1 builds the
affected-person claim on it and says so in the paper, including that an
alternative attribution method would be a further axis this work does not cross.

No torch here on purpose. The tensor extraction lives in the runner; everything
that decides a claim is pure, deterministic and testable on a machine with no
GPU, which is the same separation the statistics layer already follows.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence

__all__ = ["segment_mass", "MASS_TOLERANCE"]

#: Attention rows are softmax outputs and should sum to 1. Floating point and
#: any upstream slicing make exact equality wrong to demand, so rows are checked
#: against this tolerance and normalised rather than rejected.
MASS_TOLERANCE: float = 1e-3


def segment_mass(
    rows: Sequence[Sequence[float]],
    seq_labels: Sequence[str],
) -> dict[str, float]:
    """Attribution mass over labelled input segments.

    Args:
        rows: One row per attention head **in the circuit**, each the head's
            attention distribution over key positions at the final query
            position, already averaged over the clean prompts. Shape
            ``[n_heads_in_circuit, n_key]``. An empty sequence is legitimate: a
            circuit can contain no attention heads, and the caller must not
            fabricate one.
        seq_labels: One label per key position. Repeated labels are summed, so
            a segment spanning several tokens accumulates their mass. This is
            why `p1.prompts.generate_ioi_dataset` emits `seq_labels` and why the
            claim map reads the same list: one source, no drift.

    Returns:
        A mapping from segment label to mass, summing to 1. **An empty mapping
        when `rows` is empty**, which `phi_affected` renders as a stated absence.
        That is a legitimate state and not a discard.

    Weighting across heads is **uniform**, fixed in the pre-registration. Prune
    score weighting is defensible and is deliberately not used: scores live on
    different scales across the discovery-objective axis, because the gradient is
    taken through logit, prob, logprob or logit_exp, so a score-weighted mass
    would not be comparable across that axis. Uniform is scale-free.

    The function is deterministic and order-independent: rows are averaged, and
    labels are accumulated into a dict then emitted in sorted order, so neither
    head ordering nor dict insertion order can reach a claim.
    """
    if not seq_labels:
        raise ValueError("seq_labels must be non-empty")

    rows = [list(r) for r in rows]
    if not rows:
        return {}

    n_key = len(seq_labels)
    for i, row in enumerate(rows):
        if len(row) != n_key:
            raise ValueError(
                f"row {i} has {len(row)} key positions but there are "
                f"{n_key} seq_labels; the labels and the attention rows must "
                f"describe the same sequence"
            )
        if any(v < 0 for v in row):
            raise ValueError(f"row {i} contains a negative attention probability")

    # Uniform mean across heads, then accumulate by label.
    n_heads = len(rows)
    acc: dict[str, float] = defaultdict(float)
    for row in rows:
        for label, value in zip(seq_labels, row):
            acc[label] += value / n_heads

    total = sum(acc.values())
    if total <= 0:
        # Every head attended nowhere, which a softmax cannot produce but a
        # sliced or masked tensor can. Treated as absence, not as an error, for
        # the same reason the empty circuit is: it is reachable inside a sweep
        # and must map to something.
        return {}

    return {label: acc[label] / total for label in sorted(acc)}
