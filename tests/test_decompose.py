"""Tests for the claim-level decomposition.

The load-bearing test is `test_single_group_reduces_to_pooled_flip_rate`. The
definition in DEVIATIONS claims the family reduces to the primary outcome when
the grouping is trivial. That claim is asserted here against the independent
implementation in `p1.multiverse`, not against a rederivation of the same
formula, because a test written from the same derivation as the code tests
nothing.
"""

from __future__ import annotations

import random

import numpy as np
import pytest

from p1.decompose import GroupedLabels, encode, within_flip_rate
from p1.multiverse import flip_rate, flip_rate_bruteforce


def test_single_group_reduces_to_pooled_flip_rate():
    rng = random.Random(0)
    for _ in range(200):
        n = rng.randint(2, 60)
        labels = [rng.choice("abcde") for _ in range(n)]
        assert within_flip_rate(labels, ["only"] * n) == pytest.approx(
            flip_rate(labels)
        )


def test_single_group_matches_bruteforce_pairwise_definition():
    rng = random.Random(1)
    for _ in range(50):
        n = rng.randint(2, 25)
        labels = [rng.choice("xyz") for _ in range(n)]
        assert within_flip_rate(labels, [0] * n) == pytest.approx(
            flip_rate_bruteforce(labels)
        )


def test_perfect_grouping_gives_zero():
    labels = ["a", "a", "b", "b", "c", "c"]
    groups = ["g1", "g1", "g2", "g2", "g3", "g3"]
    assert within_flip_rate(labels, groups) == 0.0


def test_grouping_orthogonal_to_label_gives_one():
    labels = ["a", "b", "a", "b"]
    groups = ["g1", "g1", "g2", "g2"]
    assert within_flip_rate(labels, groups) == 1.0


def test_pairs_are_weighted_equally_not_groups():
    """A large group must not be given the same weight as a small one.

    Group `big` holds four specifications, six pairs, all concordant. Group
    `small` holds two, one pair, discordant. Pair weighting gives 1/7. A mean of
    per-group rates would give (0 + 1) / 2 = 0.5, which is the bug this guards.
    """
    labels = ["a", "a", "a", "a", "x", "y"]
    groups = ["big"] * 4 + ["small"] * 2
    assert within_flip_rate(labels, groups) == pytest.approx(1.0 / 7.0)


def test_all_singleton_groups_raises_rather_than_returning_zero():
    """No within-group pair exists, so the quantity is undefined.

    Returning 0.0 would read as perfect stability, which is the opposite of what
    an empty pair population means.
    """
    with pytest.raises(ZeroDivisionError, match="no within-group pairs"):
        within_flip_rate(["a", "b", "c"], ["g1", "g2", "g3"])


def test_resampling_index_matches_materialised_relabelling():
    rng = np.random.default_rng(7)
    labels = [rng.choice(list("abcd")) for _ in range(200)]
    groups = [rng.choice(list("PQR")) for _ in range(200)]
    g = GroupedLabels(labels, groups)
    idx = rng.integers(0, 200, size=200)
    expected = within_flip_rate([labels[i] for i in idx], [groups[i] for i in idx])
    assert g.flip_rate(idx) == pytest.approx(expected)


def test_encode_is_stable_and_contiguous():
    codes, n = encode(["b", "a", "b", "c", "a"])
    assert n == 3
    assert list(codes) == [0, 1, 0, 2, 1]


def test_length_mismatch_raises():
    with pytest.raises(ValueError, match="differ in length"):
        within_flip_rate(["a", "b"], ["g"])


def test_too_few_specifications_raises():
    with pytest.raises(ValueError, match="at least 2"):
        within_flip_rate(["a"], ["g"])
