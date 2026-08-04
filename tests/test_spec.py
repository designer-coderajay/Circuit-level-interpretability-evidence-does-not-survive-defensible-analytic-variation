"""Tests for the specification space.

The load-bearing test here is ``test_spec_id_is_pinned_to_a_known_value``. Every
results file on disk will be named by ``spec_id``. If the field set or the
encoding ever changes, every result silently becomes unmatchable to its config,
which breaks the requirement that each reported number be traceable to a config,
a seed, and an environment hash. The pinned literal turns that silent failure
into a loud one.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from p1.spec import (
    AUTO_CIRCUIT_ABLATIONS,
    GRANULARITIES,
    METRICS,
    Specification,
    enumerate_grid,
    grid_size,
)

CANONICAL_SPEC = dict(
    ablation="RESAMPLE",
    corruption="abc",
    metric="logit_diff",
    threshold=0.05,
    prompt_variant="base",
    seed=0,
    granularity="edge",
)


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


# --------------------------------------------------------------------------
# spec_id determinism
# --------------------------------------------------------------------------


def test_spec_id_is_pinned_to_a_known_value():
    """Regression pin. Changing fields or encoding must fail loudly here."""
    assert Specification(**CANONICAL_SPEC).spec_id == "e1fead883f6cdea2"


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
    assert outs == {"e1fead883f6cdea2"}, outs


def test_spec_id_is_sensitive_to_every_field():
    base = Specification(**CANONICAL_SPEC)
    variants = [
        {"ablation": "ZERO"},
        {"corruption": "other"},
        {"metric": "kl_div"},
        {"threshold": 0.06},
        {"prompt_variant": "variant_b"},
        {"seed": 1},
        {"granularity": "node"},
    ]
    for v in variants:
        other = Specification(**{**CANONICAL_SPEC, **v})
        assert other.spec_id != base.spec_id, f"spec_id blind to {list(v)[0]}"


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
        {"ablation": "MEAN"},          # not an auto-circuit enum member
        {"ablation": "OPTIMAL"},       # real technique, not in this instrument
        {"metric": "f1"},              # not in the decided metric set
        {"granularity": "source"},     # not a level
        {"seed": -1},
    ],
)
def test_invalid_values_are_rejected(bad):
    with pytest.raises(ValueError):
        Specification(**{**CANONICAL_SPEC, **bad})


# --------------------------------------------------------------------------
# Grid
# --------------------------------------------------------------------------


AXES = {
    "ablation": AUTO_CIRCUIT_ABLATIONS,      # 7
    "corruption": ["c1", "c2", "c3"],        # 3, levels TBD
    "metric": METRICS,                       # 4
    "threshold": [0.02, 0.05, 0.10],         # 3, levels TBD
    "prompt_variant": ["p1", "p2", "p3"],    # 3, levels TBD
    "seed": [0, 1, 2, 3, 4],                 # 5
    "granularity": ["edge"],                 # confirmatory grid only
}


def test_confirmatory_grid_is_3780():
    # 7 x 3 x 4 x 3 x 3 x 5 x 1. The brief said 2,160 on four operators.
    assert grid_size(AXES) == 3780
    assert 7 * 3 * 4 * 3 * 3 * 5 * 1 == 3780


def test_enumeration_matches_declared_size():
    assert len(list(enumerate_grid(AXES))) == grid_size(AXES)


def test_all_spec_ids_are_distinct():
    ids = [s.spec_id for s in enumerate_grid(AXES)]
    assert len(set(ids)) == len(ids), "spec_id collision in the confirmatory grid"


def test_enumeration_order_is_deterministic():
    a = [s.spec_id for s in enumerate_grid(AXES)]
    b = [s.spec_id for s in enumerate_grid(AXES)]
    assert a == b


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
    seed_only = {**AXES, "ablation": ("RESAMPLE",), "corruption": ["c1"],
                 "metric": ("logit_diff",), "threshold": [0.05],
                 "prompt_variant": ["p1"]}
    specs = list(enumerate_grid(seed_only))
    assert len(specs) == 5
    assert {s.seed for s in specs} == {0, 1, 2, 3, 4}
    full_ids = {s.spec_id for s in enumerate_grid(AXES)}
    assert {s.spec_id for s in specs} <= full_ids
