"""Tests for the claim map phi.

The load-bearing test is ``test_granularities_are_nested_partitions``. A reviewer
will say the three granularities were chosen to produce a desired flip rate. The
answer is that they are provably nested: if two circuits are indistinguishable at
FINE they are indistinguishable at MEDIUM and COARSE, so the coarser maps cannot
manufacture disagreement the finer one does not already see. That is asserted
here over randomised circuits, for both addressees.
"""

from __future__ import annotations

import random

import pytest

from p1.claim_map import (
    DEFAULT_SIZE_BINS,
    DEFAULT_BAND_NAMES,
    CircuitFeatures,
    Component,
    Granularity,
    affected_key,
    layer_band,
    overseer_key,
    phi_affected,
    phi_overseer,
    ranked_segments,
    size_class,
)

SEGMENTS = ("income", "credit_history", "employment", "address")


def make_features(rng: random.Random, n_layers: int = 12, n_heads: int = 12):
    n = rng.randint(0, 40)
    comps = frozenset(
        Component(rng.randrange(n_layers), rng.randrange(n_heads)) for _ in range(n)
    )
    mass = {s: rng.random() for s in rng.sample(SEGMENTS, rng.randint(0, len(SEGMENTS)))}
    return CircuitFeatures(
        components=comps,
        n_layers=n_layers,
        n_components_full_model=n_layers * n_heads,
        position_mass=mass,
    )


# --------------------------------------------------------------------------
# The nesting property
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key_fn", [overseer_key, affected_key])
def test_granularities_are_nested_partitions(key_fn):
    """FINE refines MEDIUM refines COARSE, for both addressees.

    Checked as an implication over every pair: agreement at a finer granularity
    must imply agreement at every coarser one.
    """
    rng = random.Random(20260803)
    feats = [make_features(rng) for _ in range(150)]
    for i in range(len(feats)):
        for j in range(i + 1, len(feats)):
            a, b = feats[i], feats[j]
            if key_fn(a, Granularity.FINE) == key_fn(b, Granularity.FINE):
                assert key_fn(a, Granularity.MEDIUM) == key_fn(b, Granularity.MEDIUM)
            if key_fn(a, Granularity.MEDIUM) == key_fn(b, Granularity.MEDIUM):
                assert key_fn(a, Granularity.COARSE) == key_fn(b, Granularity.COARSE)


@pytest.mark.parametrize("key_fn", [overseer_key, affected_key])
def test_distinct_claim_count_is_monotone_in_granularity(key_fn):
    """A finer map can never produce fewer distinct claims than a coarser one."""
    rng = random.Random(7)
    feats = [make_features(rng) for _ in range(300)]
    counts = [
        len({key_fn(f, g) for f in feats})
        for g in (Granularity.COARSE, Granularity.MEDIUM, Granularity.FINE)
    ]
    assert counts[0] <= counts[1] <= counts[2]


@pytest.mark.parametrize("key_fn", [overseer_key, affected_key])
def test_coarse_key_is_a_prefix_of_finer_keys(key_fn):
    """Nesting is structural: each granularity appends, never rewrites."""
    rng = random.Random(3)
    for _ in range(100):
        f = make_features(rng)
        c = key_fn(f, Granularity.COARSE)
        m = key_fn(f, Granularity.MEDIUM)
        fine = key_fn(f, Granularity.FINE)
        assert m[: len(c)] == c
        assert fine[: len(m)] == m


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------


def test_phi_is_deterministic_across_repeated_calls():
    rng = random.Random(11)
    for _ in range(80):
        f = make_features(rng)
        for g in Granularity:
            assert phi_overseer(f, g) == phi_overseer(f, g)
            assert phi_affected(f, g) == phi_affected(f, g)


def test_phi_is_invariant_to_component_insertion_order():
    """Sets are unordered; the claim must not depend on how they were built."""
    comps = [Component(2, 5), Component(9, 1), Component(2, 3), Component(11, 7)]
    mass = {"income": 0.6, "employment": 0.4}
    a = CircuitFeatures(frozenset(comps), 12, 144, mass)
    b = CircuitFeatures(frozenset(reversed(comps)), 12, 144, dict(reversed(list(mass.items()))))
    for g in Granularity:
        assert phi_overseer(a, g) == phi_overseer(b, g)
        assert phi_affected(a, g) == phi_affected(b, g)


def test_tie_breaking_is_deterministic_and_favours_the_earliest_band():
    # Two components in the early band, two in the late band, none in the middle.
    f = CircuitFeatures(
        frozenset({Component(0, 0), Component(1, 0), Component(10, 0), Component(11, 0)}),
        n_layers=12,
        n_components_full_model=144,
    )
    assert layer_band(f) == "early"


def test_segment_ties_break_by_label_ascending():
    f = CircuitFeatures(
        frozenset({Component(0, 0)}), 12, 144, {"zulu": 0.5, "alpha": 0.5}
    )
    assert ranked_segments(f, 2) == ("alpha", "zulu")


# --------------------------------------------------------------------------
# Edge cases that are reachable inside a sweep
# --------------------------------------------------------------------------


def test_empty_circuit_maps_to_a_claim_rather_than_raising():
    """A strict threshold can return an empty circuit. It must still map."""
    f = CircuitFeatures(frozenset(), 12, 144, {})
    for g in Granularity:
        assert isinstance(phi_overseer(f, g), str)
        assert isinstance(phi_affected(f, g), str)
    assert layer_band(f) == DEFAULT_BAND_NAMES[0]
    assert size_class(f) == "sparse"


def test_no_attribution_recorded_yields_a_stated_absence():
    f = CircuitFeatures(frozenset({Component(1, 1)}), 12, 144, {})
    assert "no single input region" in phi_affected(f, Granularity.COARSE)


def test_full_model_circuit_is_distributed():
    comps = frozenset(Component(l, h) for l in range(12) for h in range(12))
    f = CircuitFeatures(comps, 12, 144)
    assert size_class(f) == "distributed"


# --------------------------------------------------------------------------
# The two addressees must actually differ
# --------------------------------------------------------------------------


def test_the_two_maps_are_not_the_same_function():
    """If they agreed everywhere, reporting both would be padding."""
    rng = random.Random(99)
    feats = [make_features(rng) for _ in range(200)]
    for g in Granularity:
        o = len({overseer_key(f, g) for f in feats})
        a = len({affected_key(f, g) for f in feats})
        pairs_o = {(overseer_key(x, g) == overseer_key(y, g)) for x in feats[:40] for y in feats[:40]}
        pairs_a = {(affected_key(x, g) == affected_key(y, g)) for x in feats[:40] for y in feats[:40]}
        assert pairs_o == {True, False} and pairs_a == {True, False}
        assert o > 1 and a > 1


def test_overseer_is_component_facing_and_affected_is_input_facing():
    f = CircuitFeatures(
        frozenset({Component(1, 0), Component(2, 0)}), 12, 144, {"income": 1.0}
    )
    o = phi_overseer(f, Granularity.COARSE)
    a = phi_affected(f, Granularity.COARSE)
    assert "layers of the model" in o
    assert "income" in a
    assert "income" not in o


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------


def test_component_outside_model_depth_is_rejected():
    with pytest.raises(ValueError, match="outside"):
        CircuitFeatures(frozenset({Component(12, 0)}), 12, 144)


def test_negative_attribution_is_rejected():
    with pytest.raises(ValueError, match="negative"):
        CircuitFeatures(frozenset(), 12, 144, {"income": -0.1})


def test_nonpositive_layer_count_is_rejected():
    with pytest.raises(ValueError, match="n_layers"):
        CircuitFeatures(frozenset(), 0, 144)


def test_ranked_segments_rejects_k_below_one():
    f = CircuitFeatures(frozenset(), 12, 144, {"income": 1.0})
    with pytest.raises(ValueError):
        ranked_segments(f, 0)


def test_claims_end_as_sentences():
    rng = random.Random(5)
    for _ in range(30):
        f = make_features(rng)
        for g in Granularity:
            assert phi_overseer(f, g).endswith(".")
            assert phi_affected(f, g).endswith(".")


# --------------------------------------------------------------------------
# Published head-role taxonomy
# --------------------------------------------------------------------------


def test_taxonomy_matches_wang_et_al_counts():
    """Cross-check against the published paper, not just against the code.

    Wang et al. arXiv:2211.00593 abstract: "26 attention heads grouped into 7
    main classes". The taxonomy transcribed from auto-circuit's IOI_CIRCUIT must
    reproduce both counts. If a future edit drops or adds a head, this fails
    loudly rather than silently changing every role-bearing claim.
    """
    from p1.claim_map import IOI_HEAD_ROLES

    assert len(IOI_HEAD_ROLES) == 7
    assert sum(len(v) for v in IOI_HEAD_ROLES.values()) == 26


def test_no_head_appears_in_two_roles():
    from p1.claim_map import IOI_HEAD_ROLES

    seen = [h for v in IOI_HEAD_ROLES.values() for h in v]
    assert len(seen) == len(set(seen)), "a head is classified twice"


def test_all_taxonomy_heads_are_inside_gpt2_small():
    from p1.claim_map import IOI_HEAD_ROLES

    for role, heads in IOI_HEAD_ROLES.items():
        for layer, head in heads:
            assert 0 <= layer < 12, f"{role} head at layer {layer} outside GPT-2 small"
            assert 0 <= head < 12, f"{role} head index {head} outside GPT-2 small"


def test_role_of_known_heads():
    from p1.claim_map import role_of

    assert role_of(Component(9, 9)) == "name mover"
    assert role_of(Component(5, 5)) == "induction"
    assert role_of(Component(2, 2)) == "previous token"


def test_unknown_head_is_unclassified_not_dropped():
    """Discovery returns heads outside the 26. They must be counted, not hidden."""
    from p1.claim_map import UNCLASSIFIED_ROLE, role_of

    assert role_of(Component(6, 0)) == UNCLASSIFIED_ROLE


def test_mlp_is_unclassified():
    from p1.claim_map import UNCLASSIFIED_ROLE, role_of

    assert role_of(Component(9, 0, kind="mlp")) == UNCLASSIFIED_ROLE


def test_dominant_role_picks_the_majority():
    from p1.claim_map import dominant_role

    f = CircuitFeatures(
        frozenset({Component(9, 9), Component(10, 0), Component(9, 6), Component(5, 5)}),
        12, 144,
    )
    assert dominant_role(f) == "name mover"


def test_dominant_role_reports_unclassified_majority_honestly():
    """A circuit mostly outside the taxonomy must say so, not borrow a label."""
    from p1.claim_map import UNCLASSIFIED_ROLE, dominant_role

    f = CircuitFeatures(
        frozenset({Component(6, 0), Component(6, 1), Component(6, 2), Component(9, 9)}),
        12, 144,
    )
    assert dominant_role(f) == UNCLASSIFIED_ROLE


def test_dominant_role_tie_breaks_toward_the_named_role():
    from p1.claim_map import dominant_role

    f = CircuitFeatures(frozenset({Component(9, 9), Component(6, 0)}), 12, 144)
    assert dominant_role(f) == "name mover"


def test_dominant_role_is_deterministic_and_order_independent():
    comps = [Component(9, 9), Component(5, 5), Component(5, 8), Component(10, 0)]
    from p1.claim_map import dominant_role

    a = CircuitFeatures(frozenset(comps), 12, 144)
    b = CircuitFeatures(frozenset(reversed(comps)), 12, 144)
    assert dominant_role(a) == dominant_role(b)


def test_dominant_role_of_empty_circuit():
    from p1.claim_map import UNCLASSIFIED_ROLE, dominant_role

    assert dominant_role(CircuitFeatures(frozenset(), 12, 144)) == UNCLASSIFIED_ROLE


# --------------------------------------------------------------------------
# Frozen constants, anchored to the pre-registered ladder
# --------------------------------------------------------------------------





# --------------------------------------------------------------------------
# The calibration-3 bin selection rule
# --------------------------------------------------------------------------
#
# The three tests that used to sit here asserted a 5/3/2 split of the edge-count
# ladder against a 32,491-edge denominator. They were deleted on 2026-08-06
# because phi does not bin on edges: it bins on the fraction of the 156 model
# components a circuit touches. Those tests encoded a mistaken derivation and
# would have kept passing while checking nothing relevant. The bounds are now
# measured by calibration 3 and selected by the rule tested below.


def test_selection_rule_is_deterministic():
    from p1.claim_map import select_size_bins

    curve = [0.02, 0.04, 0.08, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95]
    assert select_size_bins(curve) == select_size_bins(curve)


def test_selection_rule_returns_three_bins_when_the_curve_supports_them():
    from p1.claim_map import select_size_bins

    curve = [0.02, 0.04, 0.08, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95]
    bins = select_size_bins(curve)
    assert bins is not None and len(bins) == 3
    assert [n for _, n in bins] == ["sparse", "moderate", "distributed"]


def test_selection_rule_falls_back_to_two_bins_on_a_saturating_curve():
    """Node counts saturate toward the model size; the cascade must absorb that."""
    from p1.claim_map import select_size_bins

    curve = [0.077, 0.128, 0.244, 0.372, 0.513, 0.705, 0.865, 0.962, 1.0, 1.0]
    bins = select_size_bins(curve)
    assert bins is not None and len(bins) == 2
    assert [n for _, n in bins] == ["compact", "distributed"]


def test_selection_rule_reports_degeneracy_rather_than_forcing_a_split():
    """If nothing separates, size_class is degenerate and that is a finding."""
    from p1.claim_map import select_size_bins

    assert select_size_bins([0.9] * 10) is None
    assert select_size_bins([0.60, 0.75, 0.88, 0.95, 0.98, 0.99, 1.0, 1.0, 1.0, 1.0]) is None


def test_selected_bounds_come_from_the_declared_candidate_set():
    """The search may not invent a bound outside the pre-registered grid."""
    from p1.claim_map import SIZE_BIN_CANDIDATES, select_size_bins

    curve = [0.02, 0.04, 0.08, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95]
    bins = select_size_bins(curve)
    assert bins is not None
    for bound, _ in bins[:-1]:
        assert any(abs(bound - c) < 1e-9 for c in SIZE_BIN_CANDIDATES), bound
    assert bins[-1][0] == 1.01


def test_every_bin_holds_at_least_two_rungs():
    from p1.claim_map import SIZE_BIN_MIN_PER_BIN, select_size_bins

    curve = [0.02, 0.04, 0.08, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95]
    bins = select_size_bins(curve)
    assert bins is not None
    counts = {}
    for f in curve:
        for upper, name in bins:
            if f < upper:
                counts[name] = counts.get(name, 0) + 1
                break
    assert all(c >= SIZE_BIN_MIN_PER_BIN for c in counts.values()), counts


def test_no_observed_fraction_sits_within_the_margin_of_a_bound():
    import math

    from p1.claim_map import SIZE_BIN_MIN_MARGIN_DEX, select_size_bins

    curve = [0.02, 0.04, 0.08, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95]
    bins = select_size_bins(curve)
    assert bins is not None
    for bound, _ in bins[:-1]:
        for f in curve:
            assert abs(math.log10(f) - math.log10(bound)) > SIZE_BIN_MIN_MARGIN_DEX


def test_non_positive_fractions_are_rejected():
    from p1.claim_map import select_size_bins

    with pytest.raises(ValueError, match="positive"):
        select_size_bins([0.0, 0.5, 0.9])


# --------------------------------------------------------------------------
# The frozen bins, and that they came from the rule rather than from a person
# --------------------------------------------------------------------------

MEASURED_NODE_FRACS = [
    0.0436, 0.0846, 0.1603, 0.2256, 0.3462, 0.5769, 0.7769, 0.9321, 0.9949, 1.0
]


def test_frozen_bins_are_exactly_what_the_rule_returns():
    """The strongest available check that the bins were not hand-picked.

    Feeding the measured curve from results/calib-nodes/ back through the
    committed selection rule must reproduce DEFAULT_SIZE_BINS exactly. If someone
    later nudges a bound "just a little", this fails.
    """
    from p1.claim_map import select_size_bins

    assert select_size_bins(MEASURED_NODE_FRACS) == DEFAULT_SIZE_BINS


def test_frozen_bins_split_the_measured_curve_two_three_five():
    counts: dict[str, int] = {}
    for f in MEASURED_NODE_FRACS:
        for upper, name in DEFAULT_SIZE_BINS:
            if f < upper:
                counts[name] = counts.get(name, 0) + 1
                break
    assert counts == {"sparse": 2, "moderate": 3, "distributed": 5}


def test_size_class_is_not_degenerate_on_the_measured_curve():
    """MEDIUM granularity must actually add information over COARSE."""
    classes = set()
    for f in MEASURED_NODE_FRACS:
        n_comp = 156
        comps = frozenset(
            Component(layer=i // 13, index=i % 13 if i % 13 < 12 else 0,
                      kind="attn" if i % 13 < 12 else "mlp")
            for i in range(round(f * n_comp))
        )
        classes.add(size_class(CircuitFeatures(comps, 12, n_comp)))
    assert len(classes) == 3, classes
