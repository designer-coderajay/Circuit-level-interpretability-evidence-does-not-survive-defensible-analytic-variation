"""Tests for the size-matched random-circuit null.

The important one is `test_vectorised_mapping_matches_verified_slow_path`. The
slow path is the one replayed against the sweep at 7,561 of 7,561, so agreeing
with it is agreeing with the instrument, transitively. Everything else here is a
guard on the parts that replay cannot exercise.
"""

from __future__ import annotations

import numpy as np
import pytest

from p1.claim_map import Component, Granularity, phi_overseer
from p1.features import components_from_nodes
from p1.graph import nodes_from_edge_names
from p1.null_multiverse import DROPPED, EdgeComponentIndex, components_equal_slow_path


@pytest.fixture(scope="module")
def index() -> EdgeComponentIndex:
    return EdgeComponentIndex()


@pytest.mark.parametrize("k", [1, 2, 7, 40, 300, 2_000, 10_000, 32_491])
def test_vectorised_mapping_matches_verified_slow_path(index, k):
    rng = np.random.default_rng(k)
    for _ in range(5):
        assert components_equal_slow_path(index, index.sample(k, rng))


def test_full_circuit_touches_every_component(index):
    """All 32,491 edges must reach all 144 heads and all 12 MLPs."""
    feats = index.features(np.arange(len(index.edges)))
    assert len(feats.components) == 156
    assert feats.n_components_full_model == 156


def test_residual_terminals_are_dropped(index):
    """`Resid Start->MLP 0` touches one component, not two."""
    i = index.edges.index("Resid Start->MLP 0")
    feats = index.features(np.array([i]))
    assert feats.components == frozenset({Component(layer=0, index=0, kind="mlp")})


def test_terminal_endpoints_map_to_the_sentinel(index):
    i = index.edges.index("A9.9->Resid End")
    assert DROPPED in set(index.table[i])


def test_sample_returns_distinct_edges(index):
    rng = np.random.default_rng(0)
    idx = index.sample(5_000, rng)
    assert len(set(idx.tolist())) == 5_000


def test_sample_rejects_impossible_sizes(index):
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError, match="k must be in"):
        index.sample(0, rng)
    with pytest.raises(ValueError, match="k must be in"):
        index.sample(32_492, rng)


def test_sampling_is_reproducible_from_the_seed(index):
    a = index.sample(1_000, np.random.default_rng(7))
    b = index.sample(1_000, np.random.default_rng(7))
    assert np.array_equal(a, b)


def test_claim_is_producible_at_coarse_and_medium(index):
    """The null is only defined for the granularities that ignore position_mass."""
    feats = index.features(index.sample(500, np.random.default_rng(1)))
    for g in (Granularity.COARSE, Granularity.MEDIUM):
        assert isinstance(phi_overseer(feats, g), str)


def test_component_ids_are_dense_and_cover_the_model(index):
    ids = {i for i in index.table.ravel().tolist() if i != DROPPED}
    assert ids == set(range(156))


def test_slow_path_agreement_holds_for_an_adversarial_all_mlp_circuit(index):
    """MLP-only circuits exercise the head_idx-is-None branch on both paths."""
    idx = np.array(
        [i for i, e in enumerate(index.edges) if e.endswith("->MLP 5")][:20]
    )
    fast = index.features(idx).components
    slow = components_from_nodes(
        nodes_from_edge_names([index.edges[i] for i in idx])
    )
    assert fast == slow


def test_memoised_claims_match_uncached_phi(index):
    """The cache keys on the component set. If that key were wrong, two circuits
    with different claims could collide and the null would be silently wrong."""
    rng = np.random.default_rng(11)
    grans = (Granularity.COARSE, Granularity.MEDIUM)
    for k in (10, 50, 500, 5_000, 10_000, 32_491):
        for _ in range(4):
            idx = index.sample(k, rng)
            feats = index.features(idx)
            assert index.claims(idx, grans) == tuple(
                phi_overseer(feats, g) for g in grans
            )


def test_component_ids_match_the_unique_based_definition(index):
    """`bincount` replaced `unique`; they must agree, including on emptiness."""
    rng = np.random.default_rng(3)
    for k in (1, 9, 100, 4_000, 32_491):
        idx = index.sample(k, rng)
        want = np.unique(index.table[idx].ravel())
        want = want[want != DROPPED]
        assert np.array_equal(index.component_ids(idx), want)


def test_edge_component_index_accepts_parallel_mlp():
    """The null must draw from the namespace the circuits actually came from.

    Component population is architecture-independent, so only the edge table
    changes. Asserted separately so a regression says which half moved.
    """
    from p1.null_multiverse import EdgeComponentIndex

    seq = EdgeComponentIndex()
    par = EdgeComponentIndex(parallel_mlp=True)

    assert len(seq.edges) == 32_491
    assert len(par.edges) == 32_347
    assert par.table.shape[0] == 32_347

    # Same components, same ids, same full-model denominator.
    assert par.n_components_full_model == seq.n_components_full_model == 156
    assert par.components == seq.components

    # Default unchanged, because every committed GPT-2 number depends on it.
    assert EdgeComponentIndex().parallel_mlp is False
