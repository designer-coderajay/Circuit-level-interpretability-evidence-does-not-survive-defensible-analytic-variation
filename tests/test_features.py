"""Tests for the auto-circuit to CircuitFeatures seam.

The load-bearing test is ``test_last_block_lands_in_the_late_band``. auto-circuit
counts each transformer block as two layers, so a component in GPT-2 small's
final block carries `layer == 22` or `23`, not `11`. Feeding that straight into a
claim map that assumes twelve layers would put every real component in the
"early" band and corrupt every claim in the sweep without raising anything.

These tests use a stub node rather than importing auto-circuit, so the contract
is exercised without torch. That is deliberate: the conversion logic must be
verifiable on any machine. It is not a substitute for running the real library,
which is still outstanding.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from p1.claim_map import CircuitFeatures, Component, Granularity, layer_band, phi_overseer
from p1.features import (
    AC_LAYERS_PER_BLOCK,
    block_index,
    components_from_nodes,
    features_from_circuit,
    normalise_position_mass,
)


@dataclass(frozen=True)
class StubNode:
    """Mirrors the fields of `auto_circuit.types.Node` this code depends on."""

    layer: int
    head_idx: int | None = None
    name: str = "stub"
    module_name: str = "stub.module"


GPT2_SMALL_BLOCKS = 12
GPT2_SMALL_HEADS = 12


# --------------------------------------------------------------------------
# The layer convention
# --------------------------------------------------------------------------


def test_auto_circuit_counts_two_layers_per_block():
    assert AC_LAYERS_PER_BLOCK == 2


@pytest.mark.parametrize(
    "ac_layer,expected_block",
    # VERIFIED from factorized_src_nodes / factorized_dest_nodes: the layer
    # counter starts on Resid Start at 0, so block b has attention at 2b+1 and
    # its MLP at 2b+2. Layer 0 is a terminal and is not a component.
    [(1, 0), (2, 0), (3, 1), (4, 1), (23, 11), (24, 11)],
)
def test_block_index_conversion(ac_layer, expected_block):
    assert block_index(ac_layer) == expected_block


def test_mlp_is_not_pushed_into_the_next_block():
    """The off-by-one found on 2026-08-06, pinned.

    Under the previous `ac_layer // 2` the MLP of block b landed in block b + 1,
    silently shifting layer_band for every claim containing an MLP, and the MLP
    of the final block landed outside the valid range entirely.
    """
    for b in range(12):
        assert block_index(2 * b + 1) == b, f"attention of block {b}"
        assert block_index(2 * b + 2) == b, f"MLP of block {b}"


def test_layer_zero_is_rejected_as_a_terminal():
    with pytest.raises(ValueError, match="Resid Start"):
        block_index(0)


def test_last_block_lands_in_the_late_band():
    """Regression guard against a reintroduced factor of two.

    A node in GPT-2 small's final transformer block has auto-circuit layer 22 or
    23. After conversion it must be block 11 of 12, which is the late band. If a
    future edit drops the conversion, this fails loudly instead of the sweep
    quietly reporting that every circuit is early-layer.
    """
    for ac_layer in (23, 24):
        f = features_from_circuit(
            [StubNode(layer=ac_layer, head_idx=3)],
            n_blocks=GPT2_SMALL_BLOCKS,
            n_heads_per_block=GPT2_SMALL_HEADS,
        )
        assert layer_band(f) == "late", f"ac_layer {ac_layer} misbanded"
        assert "late" in phi_overseer(f, Granularity.COARSE)


def test_first_block_lands_in_the_early_band():
    f = features_from_circuit(
        [StubNode(layer=1, head_idx=0), StubNode(layer=2, head_idx=None)],
        n_blocks=GPT2_SMALL_BLOCKS,
        n_heads_per_block=GPT2_SMALL_HEADS,
    )
    assert layer_band(f) == "early"


def test_mixing_conventions_raises_rather_than_miscomputing():
    """The unconverted path must fail, not silently produce a wrong claim.

    Constructing a CircuitFeatures with a raw auto-circuit layer index while
    declaring twelve layers is the exact mistake this module exists to prevent.
    CircuitFeatures validation is the safety net and must catch it.
    """
    with pytest.raises(ValueError, match="outside"):
        CircuitFeatures(
            components=frozenset({Component(layer=23, index=3)}),
            n_layers=GPT2_SMALL_BLOCKS,
            n_components_full_model=144,
        )


def test_block_index_rejects_negative_layer():
    with pytest.raises(ValueError):
        block_index(-1)


def test_residual_terminals_are_dropped_not_mapped():
    """Resid Start and Resid End carry head_idx None but are not MLPs.

    They appear in essentially every circuit and say nothing about which parts
    of the model mattered. Before 2026-08-06 they were mapped as MLPs, and
    Resid End at layer 2*n_blocks+1 produced a block index outside the valid
    range, which CircuitFeatures would have rejected mid-sweep.
    """
    nodes = [
        StubNode(layer=0, head_idx=None, name="Resid Start"),
        StubNode(layer=25, head_idx=None, name="Resid End"),
        StubNode(layer=1, head_idx=3, name="A0.3"),
    ]
    comps = components_from_nodes(nodes)
    assert comps == frozenset({Component(layer=0, index=3, kind="attn")})


def test_a_circuit_of_terminals_only_is_empty_not_an_error():
    nodes = [
        StubNode(layer=0, head_idx=None, name="Resid Start"),
        StubNode(layer=25, head_idx=None, name="Resid End"),
    ]
    assert components_from_nodes(nodes) == frozenset()


def test_block_index_rejects_bad_layers_per_block():
    with pytest.raises(ValueError):
        block_index(4, layers_per_block=0)


# --------------------------------------------------------------------------
# Node conversion
# --------------------------------------------------------------------------


def test_mlp_and_head_zero_of_the_same_block_do_not_collide():
    """An MLP node has head_idx None. It must not be confused with head 0."""
    comps = components_from_nodes(
        [StubNode(layer=5, head_idx=0), StubNode(layer=6, head_idx=None)]
    )
    assert len(comps) == 2
    assert Component(layer=2, index=0, kind="attn") in comps
    assert Component(layer=2, index=0, kind="mlp") in comps


def test_duplicate_nodes_collapse():
    comps = components_from_nodes([StubNode(layer=5, head_idx=1)] * 5)
    assert len(comps) == 1


def test_conversion_is_order_independent():
    a = components_from_nodes([StubNode(3, 1), StubNode(9, 4), StubNode(1, 7)])
    b = components_from_nodes([StubNode(1, 7), StubNode(3, 1), StubNode(9, 4)])
    assert a == b


def test_empty_node_set_gives_empty_circuit():
    f = features_from_circuit([], n_blocks=12, n_heads_per_block=12)
    assert len(f.components) == 0
    assert isinstance(phi_overseer(f, Granularity.FINE), str)


# --------------------------------------------------------------------------
# Attribution mass
# --------------------------------------------------------------------------


def test_position_mass_is_normalised():
    f = features_from_circuit(
        [StubNode(1, 0)],
        n_blocks=12,
        n_heads_per_block=12,
        position_mass={"income": 3.0, "employment": 1.0},
    )
    assert sum(f.position_mass.values()) == pytest.approx(1.0)
    assert f.position_mass["income"] == pytest.approx(0.75)


def test_normalisation_preserves_rank_and_therefore_the_claim():
    raw = {"a": 9.0, "b": 3.0, "c": 1.0}
    norm = normalise_position_mass(raw)
    assert sorted(raw, key=raw.get, reverse=True) == sorted(norm, key=norm.get, reverse=True)


def test_zero_and_empty_mass_yield_empty_not_nan():
    assert normalise_position_mass({}) == {}
    assert normalise_position_mass({"a": 0.0, "b": 0.0}) == {}


def test_negative_mass_is_rejected_downstream():
    with pytest.raises(ValueError, match="negative"):
        features_from_circuit(
            [StubNode(1, 0)], 12, 12, position_mass={"income": -1.0, "other": 5.0}
        )


# --------------------------------------------------------------------------
# The size denominator is a pre-registration decision
# --------------------------------------------------------------------------


def test_full_model_count_includes_mlps_by_default():
    f = features_from_circuit([StubNode(1, 0)], n_blocks=12, n_heads_per_block=12)
    assert f.n_components_full_model == 12 * 12 + 12




def test_invalid_model_shape_is_rejected():
    with pytest.raises(ValueError):
        features_from_circuit([], n_blocks=0, n_heads_per_block=12)
    with pytest.raises(ValueError):
        features_from_circuit([], n_blocks=12, n_heads_per_block=0)
