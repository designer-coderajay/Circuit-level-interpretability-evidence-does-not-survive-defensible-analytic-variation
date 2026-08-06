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
    "SIZE_BIN_CANDIDATES",
    "SIZE_BIN_MIN_MARGIN_DEX",
    "SIZE_BIN_CASCADE",
    "SIZE_BIN_NAMES",
    "SIZE_BIN_MIN_PER_BIN",
    "select_size_bins",
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
#: catches everything above the last bound.
#:
#: **PLACEHOLDER, pending calibration 3. Not yet frozen.** These values are
#: whatever `select_size_bins` returns from the measured node-count curve, and
#: they are written here by hand only once that pilot has run. Until then they
#: exist so the module imports and the unit tests have something to exercise.
#:
#: **Two superseded justifications, recorded rather than deleted**, because the
#: second is the only error on this project so far that reached both the
#: pre-registration and the test suite.
#:
#: The original values, 2% and 10%, predated `EDGE_COUNT_LADDER`. Against the
#: 32,491-edge graph they put six of the ten rungs into `sparse`.
#:
#: They were then re-anchored to 1% and 8% with the justification that no ladder
#: rung sits within 20% of a boundary. **That justification was computed against
#: the wrong quantity.** `phi` does not operate on edges. `features_from_circuit`
#: takes nodes, `components_from_nodes` maps them to `(layer, head)` pairs, and
#: `n_components_full_model` counts heads plus MLPs: 156 for GPT-2 small. So
#: `size_class` is `len(nodes touched) / 156`, and the map from a ladder rung to
#: the node count its edges touch is empirical, not analytic. The unit tests
#: written alongside encoded the same mistake and would have kept passing while
#: checking nothing relevant.
#:
#: The correct bounds are therefore measured, not reasoned, by the rule in
#: `select_size_bins`. See `preregistration/CALIBRATION.md` section 3.
DEFAULT_SIZE_BINS: tuple[tuple[float, str], ...] = (
    (0.01, "sparse"),
    (0.08, "moderate"),
    (1.01, "distributed"),
)

#: Candidate bin bounds for `select_size_bins`, as size fractions on a
#: **log-spaced** grid: 0.05 dex from 1/156 (one component) up to the whole
#: model. Declared here so the search cannot be widened once the curve is seen.
#:
#: Log spacing rather than linear because the quantity being binned is
#: compressed at the top. The number of distinct nodes a circuit touches
#: saturates: by the upper rungs of the edge-count ladder a circuit reaches most
#: of the 156 components, so consecutive rungs differ by very little. A linear
#: candidate grid is far too coarse where the data actually lives.
SIZE_BIN_CANDIDATES: tuple[float, ...] = tuple(
    round(10.0 ** (-2.2 + 0.05 * i), 6) for i in range(45)
)

#: Minimum separation between any observed size fraction and any bin bound,
#: **in log10 units**. 0.08 dex is a factor of about 1.20, so this preserves the
#: original intent of "no rung within 20% of a bound" while measuring it on the
#: scale the bins are chosen on.
SIZE_BIN_MIN_MARGIN_DEX: float = 0.08

#: Minimum number of ladder rungs that must land in each bin, so that no bin is
#: decorative.
SIZE_BIN_MIN_PER_BIN: int = 2

#: Bin counts attempted, in order. **The cascade is part of the rule.** Three
#: classes are preferred; two are accepted if three cannot be separated; only if
#: neither works is `size_class` degenerate.
#:
#: The cascade exists because the first version of this rule attempted three bins
#: and nothing else, and stress-testing it against plausible saturating curves
#: showed it would return degenerate in most of them. That would have been a
#: pre-commitment to losing MEDIUM granularity for a structural reason rather
#: than a test of whether the claim map can separate circuits. Revised
#: 2026-08-06, before any measurement was run.
SIZE_BIN_CASCADE: tuple[int, ...] = (3, 2)

#: Class names by bin count.
SIZE_BIN_NAMES: Mapping[int, tuple[str, ...]] = {
    3: ("sparse", "moderate", "distributed"),
    2: ("compact", "distributed"),
}


def _best_bounds(
    log_fracs: Sequence[float],
    log_candidates: Sequence[float],
    n_bounds: int,
    min_margin_dex: float,
    min_per_bin: int,
) -> tuple[float, ...] | None:
    """Best `n_bounds` bounds in log space, or None if the constraints fail.

    Exhaustive over the declared candidate grid. `n_bounds` is at most 2 here, so
    the search is at most 45 choose 2 and needs no cleverness.
    """
    from itertools import combinations

    best: tuple[float, tuple[float, ...]] | None = None
    for combo in combinations(range(len(log_candidates)), n_bounds):
        bounds = tuple(log_candidates[i] for i in combo)
        counts = [0] * (n_bounds + 1)
        for f in log_fracs:
            idx = sum(1 for b in bounds if f >= b)
            counts[idx] += 1
        if any(c < min_per_bin for c in counts):
            continue
        margin = min(abs(f - b) for f in log_fracs for b in bounds)
        if margin <= min_margin_dex:
            continue
        if best is None or margin > best[0] or (margin == best[0] and bounds < best[1]):
            best = (margin, bounds)
    return None if best is None else best[1]


def select_size_bins(
    fracs: Sequence[float],
    candidates: Sequence[float] = SIZE_BIN_CANDIDATES,
    min_margin_dex: float = SIZE_BIN_MIN_MARGIN_DEX,
    min_per_bin: int = SIZE_BIN_MIN_PER_BIN,
    cascade: Sequence[int] = SIZE_BIN_CASCADE,
) -> tuple[tuple[float, str], ...] | None:
    """The calibration-3 rule, as code rather than as a judgement.

    `fracs` are the observed size fractions, one per rung of
    `p1.spec.EDGE_COUNT_LADDER`: the mean number of distinct nodes the top-k
    edges touch, divided by `n_components_full_model`.

    Returns the selected bins, or **`None` if no candidate pair satisfies the
    constraints**, in which case `size_class` cannot separate the ladder and
    MEDIUM granularity is reported as degenerate. That is a finding about the
    claim map, stated in the abstract, and not a licence to relax the
    constraints.

    The rule, fixed in `preregistration/CALIBRATION.md` before the pilot ran:
    among all bound pairs drawn from `candidates` such that every bin holds at
    least `min_per_bin` rungs and no rung lies within `min_margin` of any bound,
    choose the pair maximising the minimum relative distance from any rung to any
    bound; break ties toward the smaller first bound.

    Written as an optimisation over a declared candidate set precisely so that it
    cannot be steered once the numbers are known. It is deterministic given
    `fracs`, and a test asserts that.

    Bins are chosen in **log10 space**, because the node count saturates: by the
    upper ladder rungs a circuit touches most of the model, so consecutive rungs
    differ by very little on a linear scale. The margin is therefore expressed in
    dex, and the returned bounds are ordinary fractions so `size_class` needs no
    change.
    """
    import math

    if not fracs:
        raise ValueError("fracs must be non-empty")
    if any(f <= 0 for f in fracs):
        raise ValueError("size fractions must be positive to be binned in log space")

    log_fracs = [math.log10(f) for f in fracs]
    log_candidates = [math.log10(c) for c in candidates]

    for n_bins in cascade:
        names = SIZE_BIN_NAMES[n_bins]
        bounds = _best_bounds(
            log_fracs, log_candidates, n_bins - 1, min_margin_dex, min_per_bin
        )
        if bounds is None:
            continue
        out = [(10.0**b, names[i]) for i, b in enumerate(bounds)]
        out.append((1.01, names[-1]))
        return tuple(out)

    return None


#: Layer bands as equal thirds of depth. **FROZEN 2026-08-06 by Ajay.**
#: Equal thirds is the neutral choice and requires no justification beyond
#: stating it; any unequal split would need one.
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
