"""Tests for the reproduced agreement measures.

These pin the upstream behaviour, including the parts that look like defects.
If a future edit "fixes" the mismatched-keys assertion or the `p_e == 1.0`
convention, these fail, which is the intent: the measures are the instrument for
H4 and are reproduced, not improved.
"""

from __future__ import annotations

import pytest

from p1.agreement import agreement_rate, cohens_kappa, pairwise_agreement


def test_agreement_rate_perfect_and_total_disagreement():
    a = {0: True, 1: False, 2: True}
    assert agreement_rate(a, a) == 1.0
    assert agreement_rate(a, {k: not v for k, v in a.items()}) == 0.0


def test_agreement_rate_counts_both_wrong_as_agreement():
    """Two circuits failing the same example agree about it. Upstream counts it."""
    assert agreement_rate({0: False, 1: True}, {0: False, 1: False}) == 0.5


def test_agreement_rate_raises_on_mismatched_keys():
    """Upstream asserts rather than intersecting. Reproduced deliberately."""
    with pytest.raises(AssertionError):
        agreement_rate({0: True}, {1: True})


def test_kappa_is_zero_at_chance():
    """Independent predictors with the same marginal give kappa near 0."""
    a = {i: i % 2 == 0 for i in range(100)}
    b = {i: i % 4 < 2 for i in range(100)}
    assert abs(cohens_kappa(a, b)) < 1e-9


def test_kappa_returns_one_when_expected_agreement_is_certain():
    """Both circuits right on everything: p_e == 1.0, upstream returns 1.0."""
    a = {i: True for i in range(10)}
    assert cohens_kappa(a, dict(a)) == 1.0


def test_kappa_penalises_agreement_that_chance_explains():
    """Raw agreement 0.9 but both almost always correct: kappa must be far lower."""
    a = {i: i != 0 for i in range(10)}
    b = {i: i != 1 for i in range(10)}
    assert agreement_rate(a, b) == 0.8
    assert cohens_kappa(a, b) < agreement_rate(a, b)


def test_kappa_can_go_negative():
    a = {0: True, 1: True, 2: False, 3: False}
    b = {0: False, 1: False, 2: True, 3: True}
    assert cohens_kappa(a, b) < 0


def test_pairwise_agreement_shape_and_complement():
    preds = {
        "s1": {0: True, 1: True},
        "s2": {0: True, 1: False},
        "s3": {0: False, 1: False},
    }
    out = pairwise_agreement(preds)
    assert out["n_pairs"] == 3
    assert out["functional_instability"] == pytest.approx(1 - out["mean_agreement"])


def test_pairwise_agreement_needs_two_specifications():
    with pytest.raises(ValueError, match="at least 2"):
        pairwise_agreement({"only": {0: True}})
