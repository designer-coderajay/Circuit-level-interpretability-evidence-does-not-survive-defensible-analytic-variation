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

__all__ = [
    "MASS_TOLERANCE",
    "OTHER_ROLE",
    "mean_segment_mass",
    "segment_mass",
    "split_leading_bos",
    "token_role_labels",
]

#: Label for tokens belonging to no named role: the template's connective words,
#: punctuation, and the leading token. Kept as a real label rather than dropped,
#: so the mass sums over the whole sequence and a circuit that attends mostly to
#: template scaffolding is visible rather than silently renormalised away.
OTHER_ROLE: str = "other"


def split_leading_bos(str_tokens, bos_token):
    """Count leading BOS tokens and return them separately from the body.

    Counted, never assumed. On 2026-08-12 `scripts/sweep.py` stripped exactly one
    leading token on the assumption that transformer-lens had prepended a BOS.
    It had not: `to_str_tokens(..., prepend_bos=True)` honours
    `tokenizer.add_bos_token`, which `p1.prompts.align_answer_tokenisation`
    clears on tokenizers that would otherwise double it. The strip therefore ate
    a content token and every cell in the replication run failed on the
    reconstruction check in `token_role_labels`.

    Zero, one and two leading BOS tokens are all reachable configurations:
    zero when the tokenizer inserts none and nothing prepends, one in the normal
    case, two when a string-prepended BOS meets a tokenizer that inserts its own.

    Args:
        str_tokens: Tokenised text as strings, in order.
        bos_token: The tokenizer's BOS string.

    Returns:
        `(n_bos, body)`, where `body` is everything after the leading BOS run.
    """
    n = 0
    while n < len(str_tokens) and str_tokens[n] == bos_token:
        n += 1
    return n, list(str_tokens[n:])


def token_role_labels(
    str_tokens: Sequence[str],
    prompt: str,
    roles: Mapping[str, str],
) -> list[str]:
    """One role label per token, by character span rather than by position.

    Positional labels cannot work on this task and an earlier version of this
    module assumed they could. The three templates have different token counts,
    names tokenise to different numbers of tokens, and the repeated name occupies
    two separate spans. A single positional label list is wrong three ways over.

    Roles are matched by **occurrence order in the prompt string**, which is what
    makes S1 and S2 separable: `S` appears twice and the first occurrence is S1.
    `roles` maps a role name to the literal substring, and the same substring may
    appear under two role names, as `S1` and `S2` both do.

    Aggregating by role rather than position follows arXiv:2211.00593 Figure 10,
    which plots attention over IO, S and S2. It is the same precedent already
    cited for the attribution method itself.

    Args:
        str_tokens: The tokenised prompt as strings, in order. Their
            concatenation must equal `prompt`; that is asserted, because a
            tokeniser that strips or normalises would silently misalign every
            span.
        prompt: The clean prompt text.
        roles: Role name to literal substring. Roles are resolved in sorted order
            of their first occurrence, so `S1` before `S2` regardless of dict
            order.

    Returns:
        One label per token. Tokens overlapping no role get `OTHER_ROLE`.
    """
    joined = "".join(str_tokens)
    if joined != prompt:
        raise ValueError(
            "tokens do not reconstruct the prompt, so character spans cannot be "
            f"aligned; got {joined!r} against {prompt!r}"
        )

    # Character span per role, consuming occurrences left to right so a repeated
    # substring resolves to distinct spans.
    spans: list[tuple[int, int, str]] = []
    cursor: dict[str, int] = {}
    for role in sorted(roles):
        needle = roles[role]
        if not needle:
            raise ValueError(f"role {role!r} has an empty substring")
        start = prompt.find(needle, cursor.get(needle, 0))
        if start < 0:
            raise ValueError(f"role {role!r} substring {needle!r} not found in prompt")
        cursor[needle] = start + len(needle)
        spans.append((start, start + len(needle), role))

    labels: list[str] = []
    pos = 0
    for tok in str_tokens:
        lo, hi = pos, pos + len(tok)
        pos = hi
        hit = OTHER_ROLE
        for s, e, role in spans:
            if lo < e and hi > s:  # any character overlap
                hit = role
                break
        labels.append(hit)
    return labels


def mean_segment_mass(masses: Sequence[Mapping[str, float]]) -> dict[str, float]:
    """Average several per-prompt masses into one.

    Role labels vary per prompt, because token spans do, so the mass is computed
    per prompt and averaged here rather than being computed once over a shared
    label list. A prompt contributing an empty mass still counts in the
    denominator: dropping it would silently reweight toward prompts where the
    circuit happened to attend somewhere nameable.
    """
    if not masses:
        return {}
    acc: dict[str, float] = defaultdict(float)
    for m in masses:
        for label, v in m.items():
            acc[label] += v / len(masses)
    total = sum(acc.values())
    if total <= 0:
        return {}
    return {label: acc[label] / total for label in sorted(acc)}

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
        for label, value in zip(seq_labels, row, strict=True):
            acc[label] += value / n_heads

    total = sum(acc.values())
    if total <= 0:
        # Every head attended nowhere, which a softmax cannot produce but a
        # sliced or masked tensor can. Treated as absence, not as an error, for
        # the same reason the empty circuit is: it is reachable inside a sweep
        # and must map to something.
        return {}

    return {label: acc[label] / total for label in sorted(acc)}
