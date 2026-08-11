"""Tests for the reconstructed edge namespace.

These are unit tests. The verification that actually matters is the integration
replay recorded in RESEARCH_LOG for 2026-08-11: rebuilding every banked claim
from `top_edges` on CPU and comparing against what the GPU sweep wrote, 7,561 of
7,561 exact on COARSE, MEDIUM and component count. That check has a ground truth
this module did not produce, which is the only kind of check that can catch a
shared misunderstanding between code and its tests.

What is asserted here is the part the replay cannot reach: the edges no circuit
ever selected. The replay only ever sees the 26,888 edges that appear in some
top-10,000 ranking, and the null must draw from all 32,491.
"""

from __future__ import annotations

import pytest

from p1.features import block_index
from p1.graph import Node, enumerate_edges, nodes_from_edge_names, parse_node


def test_edge_count_matches_the_instrument():
    """32,491 is what auto-circuit reports for GPT-2 small, in every manifest.

    This is not a fitted constant. It falls out of the ordering: three input
    slots per attention head, MLPs seeing their own block's heads, Resid End
    seeing everything.
    """
    assert len(enumerate_edges()) == 32_491


def test_edges_are_distinct():
    edges = enumerate_edges()
    assert len(set(edges)) == len(edges)


def test_no_edge_points_backwards():
    """Every source must precede its destination in computation order."""
    for name in enumerate_edges():
        src, _, dest = name.partition("->")
        assert parse_node(src).layer < parse_node(dest).layer, name


def test_residual_terminals_are_only_ever_source_or_sink():
    for name in enumerate_edges():
        src, _, dest = name.partition("->")
        assert dest != "Resid Start"
        assert src != "Resid End"


@pytest.mark.parametrize(
    "name,layer,head",
    [
        ("Resid Start", 0, None),
        ("A0.0", 1, 0),
        ("MLP 0", 2, None),
        ("A9.9", 19, 9),
        ("MLP 11", 24, None),
        ("Resid End", 25, None),
    ],
)
def test_parse_node_layers(name, layer, head):
    n = parse_node(name)
    assert n == Node(name, layer, head)


def test_destination_slot_suffix_collapses_to_the_head():
    """`A11.10.Q` is an input slot of head A11.10, not a separate component."""
    assert parse_node("A11.10.Q").layer == parse_node("A11.10").layer
    assert parse_node("A11.10.Q").head_idx == 10


def test_layers_agree_with_block_index():
    """The layer convention must match `p1.features`, which was verified against
    `transformer_lens_utils.py`. If either moves, this fails."""
    for b in range(12):
        assert block_index(parse_node(f"A{b}.0").layer) == b
        assert block_index(parse_node(f"MLP {b}").layer) == b


def test_nodes_from_edge_names_keeps_both_endpoints_and_order():
    nodes = nodes_from_edge_names(["Resid Start->MLP 0", "A9.9->Resid End"])
    assert [n.name for n in nodes] == [
        "Resid Start",
        "MLP 0",
        "A9.9",
        "Resid End",
    ]


def test_duplicates_are_not_removed():
    """`scripts/sweep.py` flattened endpoints without deduplicating and relied on
    `components_from_nodes` returning a frozenset. Tidying that here would make
    the null traverse a different path from the sweep."""
    nodes = nodes_from_edge_names(["Resid Start->MLP 0", "Resid Start->MLP 1"])
    assert sum(n.name == "Resid Start" for n in nodes) == 2


def test_unknown_name_raises():
    with pytest.raises(ValueError, match="unrecognised node name"):
        parse_node("A9")
