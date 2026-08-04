"""Tests for the P1 multiverse statistics.

These exist so that the mathematics in the paper is demonstrated rather than
asserted. The central test is ``test_flip_rate_closed_form_equals_bruteforce``,
which establishes numerically that the O(N) counts identity used everywhere in
the analysis equals the O(N^2) definition of the flip rate.
"""

from __future__ import annotations

import math
from collections import Counter
from itertools import combinations

import numpy as np
import pytest

from p1.multiverse import (
    bootstrap_over_specifications,
    flip_rate,
    flip_rate_bruteforce,
    is_filable,
    jaccard_distance,
    jaccard_similarity,
    mean_jaccard,
    modal_share,
    pairwise_jaccard_similarities,
)

# --------------------------------------------------------------------------
# Jaccard
# --------------------------------------------------------------------------


def test_jaccard_identical_sets_is_one():
    assert jaccard_similarity({1, 2, 3}, {1, 2, 3}) == 1.0


def test_jaccard_disjoint_sets_is_zero():
    assert jaccard_similarity({1, 2}, {3, 4}) == 0.0


def test_jaccard_known_value():
    # |a & b| = 2, |a | b| = 4
    assert jaccard_similarity({1, 2, 3}, {2, 3, 4}) == pytest.approx(2 / 4)


def test_jaccard_two_empty_circuits_treated_as_identical():
    # Documented convention. An empty circuit is reachable at a strict size
    # threshold, and NaN here would silently poison J_bar.
    assert jaccard_similarity(set(), set()) == 1.0


def test_jaccard_one_empty_one_not_is_zero():
    assert jaccard_similarity(set(), {1}) == 0.0


def test_jaccard_is_symmetric():
    rng = np.random.default_rng(11)
    for _ in range(200):
        a = set(rng.integers(0, 20, size=int(rng.integers(0, 12))).tolist())
        b = set(rng.integers(0, 20, size=int(rng.integers(0, 12))).tolist())
        assert jaccard_similarity(a, b) == pytest.approx(jaccard_similarity(b, a))


def test_jaccard_is_bounded():
    rng = np.random.default_rng(12)
    for _ in range(300):
        a = set(rng.integers(0, 30, size=int(rng.integers(0, 15))).tolist())
        b = set(rng.integers(0, 30, size=int(rng.integers(0, 15))).tolist())
        j = jaccard_similarity(a, b)
        assert 0.0 <= j <= 1.0
        assert jaccard_distance(a, b) == pytest.approx(1.0 - j)


def test_jaccard_triangle_inequality_holds_for_distance():
    # Jaccard distance is a proper metric. If this ever fails, the overlap code
    # is wrong, not the mathematics.
    rng = np.random.default_rng(13)
    for _ in range(300):
        a = set(rng.integers(0, 12, size=int(rng.integers(1, 8))).tolist())
        b = set(rng.integers(0, 12, size=int(rng.integers(1, 8))).tolist())
        c = set(rng.integers(0, 12, size=int(rng.integers(1, 8))).tolist())
        ab = jaccard_distance(a, b)
        bc = jaccard_distance(b, c)
        ac = jaccard_distance(a, c)
        assert ac <= ab + bc + 1e-12


def test_pairwise_count_is_n_choose_2():
    circuits = [{i} for i in range(9)]
    assert len(pairwise_jaccard_similarities(circuits)) == math.comb(9, 2)


def test_mean_jaccard_matches_manual_average():
    circuits = [{1, 2}, {2, 3}, {1, 2, 3}]
    expected = np.mean(
        [
            jaccard_similarity(circuits[i], circuits[j])
            for i, j in combinations(range(3), 2)
        ]
    )
    assert mean_jaccard(circuits) == pytest.approx(expected)


def test_pairwise_requires_two_circuits():
    with pytest.raises(ValueError):
        pairwise_jaccard_similarities([{1}])


# --------------------------------------------------------------------------
# Flip rate: the central identity
# --------------------------------------------------------------------------


def test_flip_rate_closed_form_equals_bruteforce():
    """The load-bearing test.

    Establishes F = 1 - sum_c n_c(n_c - 1) / (N(N - 1)) numerically against the
    O(N^2) pairwise definition, across varied N and varied numbers of claim
    classes, including the degenerate all-identical and all-distinct cases.
    """
    rng = np.random.default_rng(20260803)
    for _ in range(2000):
        n = int(rng.integers(2, 60))
        n_classes = int(rng.integers(1, 12))
        labels = rng.integers(0, n_classes, size=n).tolist()
        assert flip_rate(labels) == pytest.approx(
            flip_rate_bruteforce(labels), abs=1e-12
        )


def test_flip_rate_is_zero_when_all_specifications_agree():
    assert flip_rate(["claim-A"] * 25) == 0.0


def test_flip_rate_is_one_when_all_specifications_differ():
    assert flip_rate(list(range(25))) == 1.0


def test_flip_rate_bounded_and_matches_gini_simpson():
    """F is the unbiased Gini-Simpson index of the claim distribution.

    Cross-checks the counts identity against the p-hat form
    F = 1 - (N * sum_c p_c^2 - 1) / (N - 1), which is the version quoted in the
    paper. Two algebraically distinct expressions, so agreement is evidence the
    algebra in the manuscript is right.
    """
    rng = np.random.default_rng(7)
    for _ in range(500):
        n = int(rng.integers(2, 80))
        labels = rng.integers(0, int(rng.integers(1, 10)), size=n).tolist()
        counts = Counter(labels)
        p = np.array([c / n for c in counts.values()])
        via_p_hat = 1.0 - (n * float((p**2).sum()) - 1.0) / (n - 1)
        f = flip_rate(labels)
        assert 0.0 <= f <= 1.0
        assert f == pytest.approx(via_p_hat, abs=1e-10)


def test_flip_rate_two_class_analytic_case():
    # N = 4, counts 2 and 2. Agreeing unordered pairs = C(2,2 choose 2) * 2 = 2.
    # Total pairs = 6. F = 1 - 2/6 = 2/3.
    assert flip_rate(["a", "a", "b", "b"]) == pytest.approx(2 / 3)


def test_flip_rate_requires_two_specifications():
    with pytest.raises(ValueError):
        flip_rate(["only-one"])


def test_flip_rate_is_permutation_invariant():
    rng = np.random.default_rng(3)
    labels = rng.integers(0, 5, size=40).tolist()
    shuffled = labels[:]
    rng.shuffle(shuffled)
    assert flip_rate(labels) == pytest.approx(flip_rate(shuffled))


# --------------------------------------------------------------------------
# Modal share and filability
# --------------------------------------------------------------------------


def test_modal_share_all_agree_is_one():
    assert modal_share(["x"] * 10) == 1.0


def test_modal_share_all_distinct_is_one_over_n():
    assert modal_share(list(range(8))) == pytest.approx(1 / 8)


def test_modal_share_known_value():
    assert modal_share(["a", "a", "a", "b"]) == pytest.approx(0.75)


def test_filability_boundary_is_inclusive():
    # pi_star = 0.75 exactly, alpha = 0.25, so 1 - alpha = 0.75. Filable.
    labels = ["a", "a", "a", "b"]
    assert modal_share(labels) == pytest.approx(0.75)
    assert is_filable(labels, alpha=0.25) is True
    assert is_filable(labels, alpha=0.24) is False


def test_filability_rejects_out_of_range_alpha():
    with pytest.raises(ValueError):
        is_filable(["a", "b"], alpha=1.5)


def test_perfect_agreement_is_filable_at_zero_tolerance():
    assert is_filable(["a"] * 12, alpha=0.0) is True


# --------------------------------------------------------------------------
# Bootstrap
# --------------------------------------------------------------------------


def test_bootstrap_observed_matches_direct_computation():
    labels = ["a"] * 30 + ["b"] * 20
    res = bootstrap_over_specifications(labels, flip_rate, n_boot=200, seed=1)
    assert res.observed == pytest.approx(flip_rate(labels))


def test_bootstrap_is_deterministic_given_seed():
    labels = ["a"] * 15 + ["b"] * 10 + ["c"] * 5
    a = bootstrap_over_specifications(labels, flip_rate, n_boot=300, seed=42)
    b = bootstrap_over_specifications(labels, flip_rate, n_boot=300, seed=42)
    np.testing.assert_array_equal(a.replicates, b.replicates)


def test_bootstrap_different_seeds_differ():
    labels = ["a"] * 15 + ["b"] * 10 + ["c"] * 5
    a = bootstrap_over_specifications(labels, flip_rate, n_boot=300, seed=1)
    b = bootstrap_over_specifications(labels, flip_rate, n_boot=300, seed=2)
    assert not np.array_equal(a.replicates, b.replicates)


def test_bootstrap_replicate_count():
    labels = ["a", "b"] * 10
    res = bootstrap_over_specifications(labels, flip_rate, n_boot=137, seed=0)
    assert len(res) == 137


def test_bootstrap_interval_brackets_observed_for_symmetric_case():
    labels = ["a"] * 40 + ["b"] * 40
    res = bootstrap_over_specifications(labels, flip_rate, n_boot=3000, seed=5)
    lo, hi = res.percentile_interval(0.95)
    assert lo <= res.observed <= hi


def test_bootstrap_degenerate_case_has_zero_variance():
    # Every specification yields the same claim, so every resample does too.
    labels = ["same"] * 30
    res = bootstrap_over_specifications(labels, flip_rate, n_boot=200, seed=0)
    assert res.observed == 0.0
    assert np.allclose(res.replicates, 0.0)


def test_bootstrap_works_on_circuits_for_mean_jaccard():
    rng = np.random.default_rng(99)
    circuits = [
        frozenset(rng.integers(0, 40, size=8).tolist()) for _ in range(25)
    ]
    res = bootstrap_over_specifications(circuits, mean_jaccard, n_boot=200, seed=3)
    assert res.observed == pytest.approx(mean_jaccard(circuits))
    lo, hi = res.percentile_interval(0.95)
    assert 0.0 <= lo <= hi <= 1.0


def test_bootstrap_resamples_specifications_not_pairs():
    """Structural guarantee, via a case where the two designs are separable.

    Take three pairwise-disjoint circuits. Every one of the three pairs has
    J = 0, so the pair list is [0, 0, 0]. A bootstrap that resampled PAIRS could
    therefore only ever produce a mean of exactly 0, with zero variance.

    Resampling SPECIFICATIONS can draw the same circuit more than once, which
    introduces self-pairs at J = 1. The achievable means are then exactly
    {0, 1/3, 1}: all three distinct gives 0, a duplicate gives 1/3, and a triple
    gives 1. Observing any strictly positive replicate is therefore proof that
    specifications are the resampling unit.
    """
    circuits = [frozenset({1}), frozenset({2}), frozenset({3})]
    res = bootstrap_over_specifications(circuits, mean_jaccard, n_boot=500, seed=8)

    assert res.observed == 0.0
    assert res.replicates.max() > 0.0, "all replicates zero: pairs may be the unit"

    achievable = {0.0, 1 / 3, 1.0}
    for v in res.replicates:
        assert any(
            abs(v - x) < 1e-9 for x in achievable
        ), f"replicate {v} outside the achievable set {achievable}"
    # All three outcomes should appear over 500 draws.
    observed_values = {round(float(v), 9) for v in res.replicates}
    assert len(observed_values) == 3


def test_bootstrap_rejects_too_few_specifications():
    with pytest.raises(ValueError):
        bootstrap_over_specifications(["a"], flip_rate, n_boot=10, seed=0)


def test_bootstrap_rejects_nonpositive_n_boot():
    with pytest.raises(ValueError):
        bootstrap_over_specifications(["a", "b"], flip_rate, n_boot=0, seed=0)


def test_percentile_interval_rejects_bad_level():
    res = bootstrap_over_specifications(["a", "b"], flip_rate, n_boot=10, seed=0)
    with pytest.raises(ValueError):
        res.percentile_interval(1.0)


# --------------------------------------------------------------------------
# Analytic random-Jaccard reference
# --------------------------------------------------------------------------


def test_expected_random_jaccard_matches_simulation():
    """The closed form must track a Monte Carlo estimate.

    It is a ratio of expectations rather than an expectation of the ratio, so
    agreement is expected to be close but not exact. This pins how close, so a
    future edit that breaks the formula fails rather than drifting.
    """
    from p1.multiverse import expected_random_jaccard

    rng = np.random.default_rng(2026)
    for n, k in [(500, 50), (1000, 100), (2000, 40), (144, 12)]:
        sims = []
        for _ in range(400):
            a = set(rng.choice(n, size=k, replace=False).tolist())
            b = set(rng.choice(n, size=k, replace=False).tolist())
            sims.append(jaccard_similarity(a, b))
        empirical = float(np.mean(sims))
        analytic = expected_random_jaccard(k, n)
        assert abs(analytic - empirical) < 0.02, (
            f"n={n} k={k}: analytic {analytic:.4f} vs empirical {empirical:.4f}"
        )


def test_expected_random_jaccard_boundaries():
    from p1.multiverse import expected_random_jaccard

    assert expected_random_jaccard(0, 100) == 0.0          # empty circuits
    assert expected_random_jaccard(100, 100) == 1.0        # both are the universe
    # Sparse circuits overlap barely at all by chance, which is why a low observed
    # Jaccard is not by itself evidence of instability.
    assert expected_random_jaccard(10, 10_000) < 0.001


def test_expected_random_jaccard_is_monotone_in_k():
    from p1.multiverse import expected_random_jaccard

    vals = [expected_random_jaccard(k, 1000) for k in range(1, 500, 25)]
    assert all(x < y for x, y in zip(vals, vals[1:]))


@pytest.mark.parametrize("k,n", [(-1, 10), (5, 0), (11, 10)])
def test_expected_random_jaccard_rejects_invalid(k, n):
    from p1.multiverse import expected_random_jaccard

    with pytest.raises(ValueError):
        expected_random_jaccard(k, n)


def test_their_reported_calibration_is_reproducible_in_shape():
    """Sanity-check the regime their 4-27x figure lives in.

    32,491 edges is P1's own measured GPT-2 small edge count from the Gate 2 run.
    A circuit of a few hundred edges has a random Jaccard near zero, so any
    observed overlap above a few percent is already far above chance. This is
    the reason H3 is stated at the CLAIM level and not at the circuit level.
    """
    from p1.multiverse import expected_random_jaccard

    n_edges = 32_491
    for k in (100, 500, 2000):
        assert expected_random_jaccard(k, n_edges) < 0.04
