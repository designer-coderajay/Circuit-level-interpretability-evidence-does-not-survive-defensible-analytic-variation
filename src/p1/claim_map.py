"""The claim map phi.

`phi` maps a discovered circuit to a structured regulatory statement. It is the
single most attackable choice in the paper, so three properties are enforced by
construction rather than by good intentions:

1. **Deterministic.** Pure functions over a frozen feature record. No model, no
   randomness, no LLM. Generating claim text with a language model would layer
   LLM variance on top of circuit variance with no way to separate them.
2. **Nested granularities.** COARSE, MEDIUM, and FINE are built by *appending*
   fields to a tuple, so the partition each induces provably refines the one
   before it. A reviewer saying "you picked granularities that gave the flip
   rate you wanted" is answered by the nesting property, which is unit-tested.
3. **Pre-registerable.** Every threshold is an explicit argument with a named
   default. Nothing is buried in a magic number inside a branch.

Two addressees, because the regulation names two, with different standards.

`phi_overseer` targets Annex IV 2(e) and 3 read with Article 14(4)(c). The
addressee is a natural person assigned human oversight at the deployer, and the
standard is to "correctly interpret the high-risk AI system's output, taking
into account, for example, the interpretation tools and methods available". The
statement is therefore **component-facing**: what the interpretation tool reports
about the model.

`phi_affected` targets Article 86(1). The addressee is the person the decision is
about, and the standard is "clear and meaningful explanations of the role of the
AI system in the decision-making procedure and the main elements of the decision
taken". The statement is therefore **input-facing**: which parts of their own
case drove the output. An affected person is not owed a list of attention heads.

That difference is deliberate and is the reason both maps are reported. If their
flip rates diverge, the same circuits support a stable technical filing while
producing an unstable individual explanation, or the reverse. Either direction
is a finding.

All regulatory wording quoted in the templates is from the AI Act Service Desk
rendering and **must be cross-checked against the Official Journal** before the
manuscript is submitted. See docs/ANNEX-IV.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence

__all__ = [
    "Granularity",
    "Component",
    "CircuitFeatures",
    "DEFAULT_SIZE_BINS",
    "DEFAULT_BAND_NAMES",
    "IOI_HEAD_ROLES",
    "IOI_ROLE_ORDER",
    "role_of",
    "dominant_role",
    "layer_band",
    "size_class",
    "ranked_segments",
    "overseer_key",
    "affected_key",
    "phi_overseer",
    "phi_affected",
]


class Granularity(Enum):
    """Nested by construction. See module docstring."""

    COARSE = 1
    MEDIUM = 2
    FINE = 3


@dataclass(frozen=True, order=True)
class Component:
    """One model component. `index` is the head index, or 0 for an MLP block."""

    layer: int
    index: int
    kind: str = "attn"


@dataclass(frozen=True)
class CircuitFeatures:
    """Everything phi is allowed to see.

    Separating this from the circuit itself keeps phi pure and testable without a
    GPU. Populating it requires the model and belongs in the harness.

    `position_mass` maps a **pre-registered** input segment label to that
    segment's share of attribution. For the credit arm the segments are fields of
    the application; for IOI they are template slots. Segment definitions are
    part of the pre-registration, not of this module.
    """

    components: frozenset[Component]
    n_layers: int
    n_components_full_model: int
    position_mass: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.n_layers <= 0:
            raise ValueError(f"n_layers must be positive, got {self.n_layers}")
        if self.n_components_full_model <= 0:
            raise ValueError(
                f"n_components_full_model must be positive, got "
                f"{self.n_components_full_model}"
            )
        for c in self.components:
            if not 0 <= c.layer < self.n_layers:
                raise ValueError(f"component layer {c.layer} outside [0, {self.n_layers})")
        for label, mass in self.position_mass.items():
            if mass < 0:
                raise ValueError(f"negative attribution mass for {label!r}: {mass}")


# --------------------------------------------------------------------------
# Binning. Every threshold here is pre-registered, not tuned.
# --------------------------------------------------------------------------

#: Upper bounds, exclusive, on |C| / n_components_full_model. The final class
#: catches everything above the last bound. PROVISIONAL: these numbers must be
#: fixed in the pre-registration before any pooled result is inspected.
DEFAULT_SIZE_BINS: tuple[tuple[float, str], ...] = (
    (0.02, "sparse"),
    (0.10, "moderate"),
    (1.01, "distributed"),
)

#: Layer bands as equal thirds of depth. PROVISIONAL, pre-register before use.
DEFAULT_BAND_NAMES: tuple[str, ...] = ("early", "middle", "late")


# --------------------------------------------------------------------------
# Head-role taxonomy. Published, not invented.
# --------------------------------------------------------------------------

#: The IOI head-role taxonomy, transcribed **verbatim** from `IOI_CIRCUIT` in
#: `auto_circuit/metrics/official_circuits/circuits/ioi_official.py` of
#: auto-circuit 1.0.1, with commented-out heads excluded exactly as the
#: instrument excludes them.
#:
#: **Provenance chain, and why it matters.** That file's own header states it is
#: based on `acdc/ioi/utils.py` from ArthurConmy/Automatic-Circuit-Discovery,
#: which transcribes the taxonomy from Wang et al., arXiv:2211.00593. So this is
#: the published taxonomy, carried into the instrument P1 runs, rather than a
#: categorisation P1 devised. The role dimension of the claim map was previously
#: flagged as needing a published source; this is it.
#:
#: **Independent cross-check, VERIFIED 2026-08-04.** Wang et al.'s abstract says
#: "26 attention heads grouped into 7 main classes". This dict contains exactly
#: 26 heads across exactly 7 classes. A test asserts both counts, so a future
#: edit that drops or adds a head fails loudly rather than silently changing
#: every role-bearing claim.
#:
#: Coordinates are `(layer, head)` with layer as the **transformer block index**
#: for GPT-2 small, not auto-circuit's doubled layer index. See `p1.features`.
IOI_HEAD_ROLES: Mapping[str, tuple[tuple[int, int], ...]] = {
    "name mover": ((9, 9), (10, 0), (9, 6)),
    "backup name mover": ((10, 10), (10, 6), (10, 2), (10, 1), (11, 2), (9, 7), (9, 0), (11, 9)),
    "negative": ((10, 7), (11, 10)),
    "s2 inhibition": ((7, 3), (7, 9), (8, 6), (8, 10)),
    "induction": ((5, 5), (5, 8), (5, 9), (6, 9)),
    "duplicate token": ((0, 1), (0, 10), (3, 0)),
    "previous token": ((2, 2), (4, 11)),
}

#: Canonical order, used for deterministic tie-breaking. Follows the order in
#: the instrument's dict, which the source annotates "by importance".
IOI_ROLE_ORDER: tuple[str, ...] = tuple(IOI_HEAD_ROLES)

#: Label for a component that the published taxonomy does not name. Circuit
#: discovery routinely returns heads outside the 26, and silently dropping them
#: would bias every role-based claim toward the taxonomy.
UNCLASSIFIED_ROLE = "unclassified"


def role_of(
    component: Component,
    taxonomy: Mapping[str, tuple[tuple[int, int], ...]] = IOI_HEAD_ROLES,
) -> str:
    """Published role of a component, or `unclassified`.

    MLPs are always `unclassified`: the taxonomy covers attention heads only.
    """
    if component.kind != "attn":
        return UNCLASSIFIED_ROLE
    for role in taxonomy:
        if (component.layer, component.index) in taxonomy[role]:
            return role
    return UNCLASSIFIED_ROLE


def dominant_role(
    features: CircuitFeatures,
    taxonomy: Mapping[str, tuple[tuple[int, int], ...]] = IOI_HEAD_ROLES,
    order: Sequence[str] = IOI_ROLE_ORDER,
) -> str:
    """Most common published role among a circuit's components.

    `unclassified` participates in the count rather than being discarded, so a
    circuit consisting mostly of heads outside the published taxonomy is
    reported as such instead of being mislabelled by its minority of named
    heads. That is a real possible outcome and hiding it would be a defect.

    Ties break by `order`, which is the instrument's own ordering, annotated
    there as "by importance". `unclassified` loses every tie it is in, so a
    named role is preferred when counts are equal.
    """
    counts: dict[str, int] = {}
    for c in features.components:
        r = role_of(c, taxonomy)
        counts[r] = counts.get(r, 0) + 1
    if not counts:
        return UNCLASSIFIED_ROLE
    best = max(counts.values())
    tied = [r for r, n in counts.items() if n == best]
    for r in order:
        if r in tied:
            return r
    return UNCLASSIFIED_ROLE


def layer_band(
    features: CircuitFeatures,
    band_names: Sequence[str] = DEFAULT_BAND_NAMES,
) -> str:
    """Dominant layer band by component count.

    Depth is split into `len(band_names)` contiguous equal bands. **Ties are
    broken toward the earliest band**, deterministically and by design, so that
    the result never depends on set iteration order. An empty circuit returns
    the first band name; the empty circuit is reachable at a strict threshold and
    must map to something rather than raising inside a sweep.
    """
    if not band_names:
        raise ValueError("band_names must be non-empty")
    n_bands = len(band_names)
    counts = [0] * n_bands
    for c in features.components:
        idx = min(c.layer * n_bands // features.n_layers, n_bands - 1)
        counts[idx] += 1
    best = max(counts)
    return band_names[counts.index(best)]  # index() returns the first maximum


def size_class(
    features: CircuitFeatures,
    bins: Sequence[tuple[float, str]] = DEFAULT_SIZE_BINS,
) -> str:
    """Circuit size as a fraction of the full model, binned."""
    if not bins:
        raise ValueError("bins must be non-empty")
    frac = len(features.components) / features.n_components_full_model
    for upper, name in bins:
        if frac < upper:
            return name
    return bins[-1][1]


def ranked_segments(features: CircuitFeatures, k: int = 1) -> tuple[str, ...]:
    """Top-k input segments by attribution mass, descending.

    Ties break by segment label ascending, so the ordering never depends on dict
    insertion order. Returns fewer than k entries if fewer segments exist, and an
    empty tuple if no attribution was recorded.
    """
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    ordered = sorted(features.position_mass.items(), key=lambda kv: (-kv[1], kv[0]))
    return tuple(label for label, _ in ordered[:k])


# --------------------------------------------------------------------------
# Claim keys. Nesting lives here and nowhere else.
# --------------------------------------------------------------------------


def overseer_key(features: CircuitFeatures, g: Granularity, **kw) -> tuple:
    """Equivalence key for phi_overseer. Strictly nested across granularities."""
    key = (layer_band(features, kw.get("band_names", DEFAULT_BAND_NAMES)),)
    if g.value >= Granularity.MEDIUM.value:
        key += (size_class(features, kw.get("bins", DEFAULT_SIZE_BINS)),)
    if g.value >= Granularity.FINE.value:
        key += (ranked_segments(features, 1),)
    return key


def affected_key(features: CircuitFeatures, g: Granularity, **kw) -> tuple:
    """Equivalence key for phi_affected. Strictly nested across granularities.

    Leads with the input segment, because Article 86(1) is owed to the person the
    decision is about and speaks of "the main elements of the decision taken",
    not of model internals.
    """
    key = (ranked_segments(features, 1),)
    if g.value >= Granularity.MEDIUM.value:
        key += (size_class(features, kw.get("bins", DEFAULT_SIZE_BINS)),)
    if g.value >= Granularity.FINE.value:
        key += (ranked_segments(features, 2),)
    return key


# --------------------------------------------------------------------------
# Templates. Closed set, no free text.
# --------------------------------------------------------------------------


def _segments_phrase(segs: tuple[str, ...]) -> str:
    if not segs:
        return "no single input region"
    if len(segs) == 1:
        return segs[0]
    return " and ".join((", ".join(segs[:-1]), segs[-1]))


def phi_overseer(features: CircuitFeatures, g: Granularity, **kw) -> str:
    """Annex IV 2(e) and 3, read with Article 14(4)(c). Addressee: the overseer."""
    key = overseer_key(features, g, **kw)
    head = (
        "Technical measure for interpreting outputs: the system's response is "
        f"attributable principally to components in the {key[0]} layers of the model"
    )
    if g.value >= Granularity.MEDIUM.value:
        head += f", forming a {key[1]} subgraph"
    if g.value >= Granularity.FINE.value:
        head += f", attending principally to {_segments_phrase(key[2])}"
    return head + "."


def phi_affected(features: CircuitFeatures, g: Granularity, **kw) -> str:
    """Article 86(1). Addressee: the person the decision is about."""
    key = affected_key(features, g, **kw)
    head = (
        "The system's output in this case was driven principally by "
        f"{_segments_phrase(key[0])}"
    )
    if g.value >= Granularity.MEDIUM.value:
        head += f", through a {key[1]} portion of the model's processing"
    if g.value >= Granularity.FINE.value:
        head += f"; the next most influential element was {_segments_phrase(key[2][1:])}"
    return head + "."
