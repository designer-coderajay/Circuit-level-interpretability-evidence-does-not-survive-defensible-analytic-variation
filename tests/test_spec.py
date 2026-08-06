"""Tests for the specification space.

Two load-bearing tests here.

``test_spec_id_is_pinned_to_a_known_value``. Every results file on disk is named
by ``spec_id``. If the field set or the encoding changes, every result silently
becomes unmatchable to its config, breaking the requirement that each reported
number be traceable to a config, a seed, and an environment hash. The pinned
literal turns that silent failure into a loud one.

``test_no_duplicate_specifications_in_the_grid``. Two of the seven ablation
operators ignore the corrupt distribution, so a fully crossed grid contained
5,040 exact duplicates, 19% of it. Corruption is now nested within ablation and
the invariant is enforced on the dataclass itself, so a duplicate is
unconstructible rather than merely unemitted. See DESIGN-DELTAS D18.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from p1.spec import (
    AUTO_CIRCUIT_ABLATIONS,
    CORRUPTION_DEPENDENT_ABLATIONS,
    CORRUPTION_LEVELS,
    CORRUPTION_NOT_APPLICABLE,
    DISCOVERY_OBJECTIVES,
    EDGE_COUNT_LADDER,
    GRANULARITIES,
    IEG_1000_OBJECTIVE,
    METRICS,
    Specification,
    ablation_corruption_cells,
    discovery_cells,
    enumerate_grid,
    grid_size,
)

CANONICAL_SPEC = dict(
    discovery_objective="LOGIT_DIFF_GRAD_PRUNE_ALGO",
    ablation="RESAMPLE",
    corruption="ABC",
    metric="logit_diff",
    threshold=0.05,
    prompt_variant="ABBA",
    seed=0,
    granularity="edge",
)

PINNED_SPEC_ID = "80c4f62c924f1f99"


# --------------------------------------------------------------------------
# Axis levels
# --------------------------------------------------------------------------


def test_seven_ablation_operators_not_four():
    # The brief assumed four. auto-circuit 1.0.1 ships seven.
    assert len(AUTO_CIRCUIT_ABLATIONS) == 7


def test_five_of_the_seven_ablations_are_mean_variants():
    # "Mean ablation" is not one choice. This is the operator finding.
    means = [a for a in AUTO_CIRCUIT_ABLATIONS if "MEAN" in a]
    assert len(means) == 5


def test_ablation_names_are_unique():
    assert len(set(AUTO_CIRCUIT_ABLATIONS)) == len(AUTO_CIRCUIT_ABLATIONS)


def test_absent_operators_are_absent():
    # Gaussian noise and optimal ablation are named in the literature and are
    # not implemented by auto-circuit. If either ever appears here without a
    # separate arm, the verbatim-instrument claim has been broken.
    joined = " ".join(AUTO_CIRCUIT_ABLATIONS).upper()
    assert "GAUSSIAN" not in joined
    assert "OPTIMAL" not in joined


def test_metric_axis_has_four_levels():
    assert len(METRICS) == 4
    assert set(METRICS) == {"logit_diff", "kl_div", "sufficiency", "comprehensiveness"}


def test_edge_is_the_first_granularity():
    # Edge-level is the confirmatory grid; the default must reflect that.
    assert GRANULARITIES[0] == "edge"
    assert Specification(**CANONICAL_SPEC).granularity == "edge"


def test_seven_confirmatory_discovery_objectives():
    """Six EAP variants plus IEG-50. IEG-1000 is the reduced arm, not a level."""
    assert len(DISCOVERY_OBJECTIVES) == 7
    assert IEG_1000_OBJECTIVE not in DISCOVERY_OBJECTIVES


def test_five_of_seven_ablations_read_the_corrupt_distribution():
    """The 5/2 split is the whole of D18 and drives the nesting arithmetic."""
    assert len(CORRUPTION_DEPENDENT_ABLATIONS) == 5
    assert CORRUPTION_DEPENDENT_ABLATIONS <= set(AUTO_CIRCUIT_ABLATIONS)
    independent = set(AUTO_CIRCUIT_ABLATIONS) - CORRUPTION_DEPENDENT_ABLATIONS
    assert independent == {"ZERO", "TOKENWISE_MEAN_CLEAN"}


def test_edge_count_ladder_is_ascending_and_below_the_full_model():
    """The top rung must sit below 32,491 or the criterion is trivially met."""
    assert list(EDGE_COUNT_LADDER) == sorted(EDGE_COUNT_LADDER)
    assert len(set(EDGE_COUNT_LADDER)) == len(EDGE_COUNT_LADDER)
    assert EDGE_COUNT_LADDER[0] > 0
    assert EDGE_COUNT_LADDER[-1] < 32491, (
        "including the full model as a rung makes the tau criterion trivially "
        "satisfiable and converts a discard into a meaningless whole-model claim"
    )


# --------------------------------------------------------------------------
# The nesting invariant
# --------------------------------------------------------------------------


def test_corruption_independent_ablation_rejects_a_real_corruption_level():
    for ablation in ("ZERO", "TOKENWISE_MEAN_CLEAN"):
        with pytest.raises(ValueError, match="nested"):
            Specification(**{**CANONICAL_SPEC, "ablation": ablation, "corruption": "ABC"})


def test_corruption_dependent_ablation_rejects_the_sentinel():
    with pytest.raises(ValueError, match="real level"):
        Specification(**{**CANONICAL_SPEC, "corruption": CORRUPTION_NOT_APPLICABLE})


def test_sentinel_may_not_be_supplied_as_a_corruption_level():
    axes = {**AXES, "corruption": [CORRUPTION_NOT_APPLICABLE, "ABC"]}
    with pytest.raises(ValueError, match="sentinel"):
        list(enumerate_grid(axes))


def test_threshold_must_be_metric_relative_not_an_edge_count():
    """An absolute tau is a different pre-registered convention. See D12."""
    for bad in (500, 1.0, 0.0, -0.1):
        with pytest.raises(ValueError, match="metric-relative"):
            Specification(**{**CANONICAL_SPEC, "threshold": bad})


# --------------------------------------------------------------------------
# spec_id determinism
# --------------------------------------------------------------------------


def test_spec_id_is_pinned_to_a_known_value():
    """Regression pin. Changing fields or encoding must fail loudly here.

    Repinned 2026-08-05 when ``discovery_objective`` was added and the threshold
    became metric-relative-only. The previous value was ``e1fead883f6cdea2`` on a
    seven-field specification with no discovery objective. That change was
    deliberate and is recorded in RESEARCH_LOG.md; after the pre-registration is
    locked this literal must not move again.
    """
    assert Specification(**CANONICAL_SPEC).spec_id == PINNED_SPEC_ID


def test_spec_id_is_stable_across_processes():
    """Guards against Python's salted built-in hash being used by mistake.

    ``hash()`` is randomised per process unless PYTHONHASHSEED is fixed, so a
    spec_id built on it would differ between the sweep run and the analysis run.
    This spawns a fresh interpreter with a different hash seed and checks the id
    is unchanged.
    """
    code = (
        "import sys; sys.path.insert(0, 'src');"
        "from p1.spec import Specification;"
        f"print(Specification(**{CANONICAL_SPEC!r}).spec_id)"
    )
    outs = set()
    for seed in ("0", "1", "12345"):
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            env={"PYTHONHASHSEED": seed, "PATH": "/usr/bin:/bin:/usr/local/bin"},
        )
        assert r.returncode == 0, r.stderr
        outs.add(r.stdout.strip())
    assert outs == {PINNED_SPEC_ID}, outs


def test_spec_id_is_sensitive_to_every_field():
    base = Specification(**CANONICAL_SPEC)
    variants = [
        {"discovery_objective": "PROB_GRAD_PRUNE_ALGO"},
        {"ablation": "TOKENWISE_MEAN_CORRUPT"},
        {"corruption": "RANDOM_NAME_FLIP"},
        {"metric": "kl_div"},
        {"threshold": 0.06},
        {"prompt_variant": "BABA"},
        {"seed": 1},
        {"granularity": "node"},
    ]
    for v in variants:
        other = Specification(**{**CANONICAL_SPEC, **v})
        assert other.spec_id != base.spec_id, f"spec_id blind to {list(v)[0]}"


def test_spec_id_distinguishes_a_nested_cell_from_a_crossed_one():
    """A non-applicable corruption must not collide with a real level.

    This is why the sentinel exists rather than silently reusing level zero.
    """
    nested = Specification(
        **{**CANONICAL_SPEC, "ablation": "ZERO", "corruption": CORRUPTION_NOT_APPLICABLE}
    )
    crossed = Specification(**{**CANONICAL_SPEC, "ablation": "TOKENWISE_MEAN_CORRUPT"})
    assert nested.spec_id != crossed.spec_id


def test_canonical_encoding_is_key_sorted_and_compact():
    c = Specification(**CANONICAL_SPEC).canonical()
    assert " " not in c
    assert c.index('"ablation"') < c.index('"corruption"') < c.index('"granularity"')


def test_equal_specs_have_equal_ids():
    a = Specification(**CANONICAL_SPEC)
    b = Specification(**CANONICAL_SPEC)
    assert a == b and a.spec_id == b.spec_id


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad",
    [
        {"ablation": "MEAN"},                    # not an auto-circuit enum member
        {"ablation": "OPTIMAL"},                 # real technique, not in this instrument
        {"metric": "f1"},                        # not in the decided metric set
        {"granularity": "source"},               # not a level
        {"seed": -1},
        {"discovery_objective": "EAP"},          # short name, not the constant name
        {"discovery_objective": "ACDC_PRUNE_ALGO"},  # real constant, wrong algorithm
    ],
)
def test_invalid_values_are_rejected(bad):
    with pytest.raises(ValueError):
        Specification(**{**CANONICAL_SPEC, **bad})


# --------------------------------------------------------------------------
# Grid
# --------------------------------------------------------------------------


AXES = {
    "discovery_objective": DISCOVERY_OBJECTIVES,   # 7
    "ablation": AUTO_CIRCUIT_ABLATIONS,            # 7, corruption nested inside
    "corruption": CORRUPTION_LEVELS,               # 4, fixed 2026-08-06
    "metric": METRICS,                             # 4
    "threshold": [0.05, 0.10, 0.20],               # 3, levels still [CONFIRM]
    "prompt_variant": ["ABBA", "BABA"],            # 2, fixed 2026-08-05
    "seed": [0, 1, 2, 3, 4],                       # 5
    "granularity": ["edge"],                       # confirmatory grid only
}


def test_four_corruption_levels_all_from_one_primary_source():
    """Each level cites a construction in arXiv:2211.00593. See spec.py."""
    assert len(CORRUPTION_LEVELS) == 4
    assert CORRUPTION_LEVELS[0] == "ABC", "ABC is the default and leads the axis"
    assert set(CORRUPTION_LEVELS) == {
        "ABC", "RANDOM_NAME_FLIP", "IO_S1_FLIP", "IO_FROM_S2"
    }


def test_the_tautology_control_pair_is_present():
    """ABC and RANDOM_NAME_FLIP are the pre-registered secondary comparison.

    Both are "replace the names with random names", differing only in whether the
    duplicate-name structure survives, so a flip confined to this pair cannot be
    dismissed as a consequence of choosing counterfactuals known to differ. If
    either level is ever removed, the secondary outcome in PLAN.md section 3
    becomes uncomputable and this fails loudly.
    """
    assert {"ABC", "RANDOM_NAME_FLIP"} <= set(CORRUPTION_LEVELS)


def test_ablation_corruption_cells_is_twentytwo():
    # 5 corruption-dependent operators x 4 levels, plus 2 that get one cell each.
    assert ablation_corruption_cells(AXES) == 22
    assert 5 * 4 + 2 * 1 == 22


def test_discovery_cells_is_1540():
    """What the sweep budget scales with. tau is applied post-hoc to a ranking."""
    assert discovery_cells(AXES) == 1540
    assert 7 * 22 * 2 * 5 * 1 == 1540


def test_confirmatory_grid_is_18480():
    assert grid_size(AXES) == 18480
    assert 1540 * 4 * 3 == 18480


def test_nesting_removed_exactly_the_duplicate_cells():
    """The fully crossed design would have been 28 ablation-corruption cells.

    Six of those 28 were duplicates: two operators that ignore corruption, each
    crossed against four levels, giving four identical cells where one exists.
    """
    fully_crossed = len(AXES["ablation"]) * len(AXES["corruption"])
    assert fully_crossed == 28
    assert fully_crossed - ablation_corruption_cells(AXES) == 6
    assert 2 * (4 - 1) == 6


def test_enumeration_matches_declared_size():
    assert len(list(enumerate_grid(AXES))) == grid_size(AXES)


def test_no_duplicate_specifications_in_the_grid():
    """The D18 regression. A multiverse of non-distinct points is not a multiverse."""
    specs = list(enumerate_grid(AXES))
    assert len(set(specs)) == len(specs), "duplicate Specification in the grid"


def test_all_spec_ids_are_distinct():
    ids = [s.spec_id for s in enumerate_grid(AXES)]
    assert len(set(ids)) == len(ids), "spec_id collision in the confirmatory grid"


def test_corruption_independent_cells_carry_the_sentinel():
    for s in enumerate_grid(AXES):
        if s.ablation in CORRUPTION_DEPENDENT_ABLATIONS:
            assert s.corruption in AXES["corruption"]
        else:
            assert s.corruption == CORRUPTION_NOT_APPLICABLE


def test_enumeration_order_is_deterministic():
    a = [s.spec_id for s in enumerate_grid(AXES)]
    b = [s.spec_id for s in enumerate_grid(AXES)]
    assert a == b


def test_enumeration_is_resumable_by_index():
    """The sweep restarts after a dropped Colab session and must not reshuffle."""
    full = [s.spec_id for s in enumerate_grid(AXES)]
    resumed = [s.spec_id for i, s in enumerate(enumerate_grid(AXES)) if i >= 9000]
    assert resumed == full[9000:]


def test_grid_rejects_missing_axis():
    axes = {k: v for k, v in AXES.items() if k != "seed"}
    with pytest.raises(ValueError, match="missing"):
        list(enumerate_grid(axes))


def test_grid_rejects_unknown_axis():
    with pytest.raises(ValueError, match="unknown"):
        list(enumerate_grid({**AXES, "temperature": [1.0]}))


def test_grid_rejects_empty_axis():
    with pytest.raises(ValueError, match="no levels"):
        list(enumerate_grid({**AXES, "seed": []}))


def test_seed_only_slice_isolates_sampling_noise():
    """The seed-only arm must be a clean slice of the same grid.

    Reporting the ratio of seed variance to analytic-choice variance is a
    headline number, so the seed-only specifications have to be the identical
    construction with one axis varying, not a separately built set.
    """
    seed_only = {
        **AXES,
        "discovery_objective": ("LOGIT_DIFF_GRAD_PRUNE_ALGO",),
        "ablation": ("RESAMPLE",),
        "corruption": ["ABC"],
        "metric": ("logit_diff",),
        "threshold": [0.05],
        "prompt_variant": ["ABBA"],
    }
    specs = list(enumerate_grid(seed_only))
    assert len(specs) == 5
    assert {s.seed for s in specs} == {0, 1, 2, 3, 4}
    full_ids = {s.spec_id for s in enumerate_grid(AXES)}
    assert {s.spec_id for s in specs} <= full_ids


def test_ieg_1000_arm_is_a_seed_only_slice_outside_the_confirmatory_grid():
    """The reduced arm is reported separately and never pooled."""
    arm = {
        **AXES,
        "discovery_objective": (IEG_1000_OBJECTIVE,),
        "ablation": ("RESAMPLE",),
        "corruption": ["ABC"],
        "metric": ("logit_diff",),
        "threshold": [0.05],
        "prompt_variant": ["ABBA"],
    }
    specs = list(enumerate_grid(arm))
    assert len(specs) == 5
    full_ids = {s.spec_id for s in enumerate_grid(AXES)}
    assert not ({s.spec_id for s in specs} & full_ids), (
        "IEG-1000 specifications must not collide with the confirmatory grid"
    )
