"""Tests for metric-relative tau.

These two functions decide which circuit `C(s)` is, and therefore which claim
every specification emits. The load-bearing properties are that the recovery
convention is direction-agnostic, so a divergence metric needs no special case
and cannot acquire a sign bug, and that a specification with no qualifying rung
is discarded rather than quietly handed the largest one.
"""

from __future__ import annotations

import pytest

from p1.metrics import DegenerateMetric, normalised_recovery, select_rung
from p1.spec import EDGE_COUNT_LADDER

LADDER = list(EDGE_COUNT_LADDER)


# --------------------------------------------------------------------------
# The recovery convention
# --------------------------------------------------------------------------


def test_empty_circuit_recovers_nothing_and_full_recovers_everything():
    assert normalised_recovery(2.0, 2.0, 10.0) == 0.0
    assert normalised_recovery(10.0, 2.0, 10.0) == 1.0


def test_halfway_is_one_half():
    assert normalised_recovery(6.0, 2.0, 10.0) == pytest.approx(0.5)


def test_a_divergence_metric_needs_no_special_case():
    """kl_div is zero at the full model and large at the empty one.

    Gap closing must still increase as the circuit approaches the full model.
    This is the property that makes one convention safe for all four metrics: a
    plain ratio to the full model would divide by zero here, and a per-metric
    convention is where sign bugs live.
    """
    kl_empty, kl_full = 8.0, 0.0
    worse = normalised_recovery(6.0, kl_empty, kl_full)
    better = normalised_recovery(1.0, kl_empty, kl_full)
    assert 0.0 < worse < better < 1.0
    assert normalised_recovery(0.0, kl_empty, kl_full) == 1.0


def test_recovery_is_not_clipped():
    """Overshoot and undershoot are real and must stay visible."""
    assert normalised_recovery(12.0, 2.0, 10.0) > 1.0
    assert normalised_recovery(0.0, 2.0, 10.0) < 0.0


def test_a_metric_that_cannot_separate_full_from_empty_is_degenerate():
    with pytest.raises(DegenerateMetric):
        normalised_recovery(5.0, 5.0, 5.0)


# --------------------------------------------------------------------------
# The ladder scan
# --------------------------------------------------------------------------


def test_selects_the_smallest_qualifying_rung():
    recs = [0.1, 0.3, 0.5, 0.7, 0.85, 0.93, 0.97, 0.99, 1.0, 1.0]
    assert select_rung(recs, LADDER, tau=0.20) == 200   # first rec >= 0.80
    assert select_rung(recs, LADDER, tau=0.10) == 500   # first rec >= 0.90
    assert select_rung(recs, LADDER, tau=0.05) == 1000  # first rec >= 0.95


def test_no_qualifying_rung_returns_none_rather_than_the_largest():
    """A specification needing more than the top rung is discarded, not fudged."""
    recs = [0.1] * len(LADDER)
    assert select_rung(recs, LADDER, tau=0.05) is None


def test_scan_is_upward_and_survives_a_non_monotone_curve():
    """Recovery is not guaranteed monotone; the first qualifying rung still wins.

    This is why bisection was rejected. A binary search on this curve could
    return 5000 while an upward scan correctly returns 50.
    """
    recs = [0.2, 0.4, 0.96, 0.55, 0.60, 0.70, 0.80, 0.90, 0.97, 0.99]
    assert select_rung(recs, LADDER, tau=0.05) == 50


def test_exact_threshold_qualifies():
    recs = [0.0] * 9 + [0.95]
    assert select_rung(recs, LADDER, tau=0.05) == LADDER[-1]


def test_tau_must_be_a_proportion_not_an_edge_count():
    recs = [1.0] * len(LADDER)
    for bad in (500, 0.0, 1.0, -0.1):
        with pytest.raises(ValueError, match="tau"):
            select_rung(recs, LADDER, tau=bad)


def test_mismatched_lengths_are_rejected():
    with pytest.raises(ValueError, match="one to one"):
        select_rung([0.9, 0.9], LADDER, tau=0.10)


def test_descending_ladder_is_rejected():
    recs = [0.9] * len(LADDER)
    with pytest.raises(ValueError, match="ascending"):
        select_rung(recs, list(reversed(LADDER)), tau=0.10)


# --------------------------------------------------------------------------
# The two together, on the pre-registered tau levels
# --------------------------------------------------------------------------


def test_stricter_tau_never_selects_a_smaller_circuit():
    """Monotonicity in tau is a property of the rule and must hold on any curve."""
    recs = [0.05, 0.22, 0.48, 0.66, 0.79, 0.88, 0.94, 0.97, 0.99, 1.0]
    picks = [select_rung(recs, LADDER, tau=t) for t in (0.20, 0.10, 0.05)]
    assert all(p is not None for p in picks)
    assert picks[0] <= picks[1] <= picks[2]


def test_recovery_and_selection_compose_on_a_divergence_metric():
    kl_empty, kl_full = 8.0, 0.0
    kls = [7.6, 6.4, 4.8, 3.2, 2.0, 1.2, 0.6, 0.24, 0.08, 0.0]
    recs = [normalised_recovery(k, kl_empty, kl_full) for k in kls]
    # recoveries: .05 .20 .40 .60 .75 .85 .925 .97 .99 1.0
    assert select_rung(recs, LADDER, tau=0.20) == 500    # first rec >= 0.80
    assert select_rung(recs, LADDER, tau=0.05) == 2000   # first rec >= 0.95
