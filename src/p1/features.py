"""Turning an auto-circuit result into `CircuitFeatures`.

This is the seam between the instrument and the claim map. auto-circuit is never
modified; this module reads its output and nothing else.

THE LAYER CONVENTION TRAP
-------------------------

auto-circuit's `Node.layer` is **not** the transformer block index. From
`auto_circuit/types.py`, quoted verbatim:

    "layer: The layer of the model that the node is in. Transformer blocks count
     as 2 layers (one for the attention layer and one for the MLP layer) because
     we want to connect nodes in the attention layer to nodes in the subsequent
     MLP layer."

So GPT-2 small, which has 12 transformer blocks, exposes roughly 24 auto-circuit
layers. Passing `Node.layer` straight into a claim map that assumes 12 would put
every real component in the "early" band and silently corrupt every claim in the
sweep, with no error raised anywhere.

This module therefore refuses to guess. `AC_LAYERS_PER_BLOCK` is stated as a
constant, the conversion is explicit, and a regression test asserts that a
component in the last transformer block lands in the "late" band rather than the
first. That test exists specifically to catch a factor-of-two reintroduced by a
future edit.

**Status: written against the auto-circuit source, NOT yet executed against the
library.** The sandbox has no torch. Every function here must be exercised on
real auto-circuit output before any number it produces enters the paper.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Protocol, Sequence

from p1.claim_map import CircuitFeatures, Component

__all__ = [
    "AC_LAYERS_PER_BLOCK",
    "NodeLike",
    "block_index",
    "components_from_nodes",
    "features_from_circuit",
    "normalise_position_mass",
]

#: auto-circuit counts an attention sublayer and an MLP sublayer as two separate
#: layers. VERIFIED 2026-08-03 from the `Node.layer` docstring in
#: `auto_circuit/types.py` of auto-circuit 1.0.1.
AC_LAYERS_PER_BLOCK = 2


class NodeLike(Protocol):
    """The part of `auto_circuit.types.Node` this module depends on.

    Structural typing on purpose: it lets the conversion be unit-tested without
    importing torch, and it documents exactly which fields are relied upon, so a
    change in the instrument surfaces as a contract failure rather than as a
    wrong number.
    """

    name: str
    module_name: str
    layer: int
    head_idx: int | None


#: Node names that are graph terminals rather than model components. They carry
#: no information about which parts of the model mattered, they appear in
#: essentially every circuit, and their layer indices fall outside the block
#: range by construction. **Excluded, not mapped.**
RESID_TERMINAL_PREFIX = "Resid"


def block_index(ac_layer: int, layers_per_block: int = AC_LAYERS_PER_BLOCK) -> int:
    """Convert an auto-circuit layer index to a transformer block index.

    **Corrected 2026-08-06. The previous `ac_layer // layers_per_block` was wrong
    for MLPs and for both residual terminals.**

    VERIFIED from `auto_circuit/model_utils/transformer_lens_utils.py`,
    `factorized_src_nodes` and `factorized_dest_nodes`. The layer counter is a
    plain `count()` that begins on the residual terminal, not on block 0:

        Resid Start          layer 0
        block b attention    layer 2b + 1
        block b MLP          layer 2b + 2
        Resid End            layer 2 * n_blocks + 1

    So for GPT-2 small: attention layers 1, 3, ..., 23; MLP layers 2, 4, ..., 24;
    Resid End at 25. Under the old formula the MLP of block b landed in block
    b + 1, silently shifting `layer_band` for every claim containing an MLP, and
    the MLP of the last block plus Resid End both mapped to block 12, outside
    `[0, 12)`, which `CircuitFeatures` would have rejected.

    `(ac_layer - 1) // layers_per_block` is correct for both component kinds:
    attention `2b+1` gives `b`, MLP `2b+2` gives `b`.

    Terminals are not passed here at all; see `components_from_nodes`.

    Assumes `parallel_attn_mlp` is False, which is the case for GPT-2 and is what
    the confirmatory grid uses. Under `parallel_attn_mlp` the MLP shares the
    attention layer and this mapping would need revisiting.
    """
    if ac_layer < 1:
        raise ValueError(
            f"auto-circuit layer must be at least 1 for a model component; got "
            f"{ac_layer}. Layer 0 is the Resid Start terminal, which is not a "
            f"component and must be filtered before conversion."
        )
    if layers_per_block < 1:
        raise ValueError(f"layers_per_block must be at least 1, got {layers_per_block}")
    return (ac_layer - 1) // layers_per_block


def components_from_nodes(
    nodes: Iterable[NodeLike],
    layers_per_block: int = AC_LAYERS_PER_BLOCK,
) -> frozenset[Component]:
    """Map auto-circuit nodes to `Component`s indexed by transformer block.

    A node with `head_idx is None` is an MLP and is given `kind="mlp"` with
    `index=0`, so attention head 0 and the MLP of the same block never collide.

    **Residual terminals are dropped.** `Resid Start` and `Resid End` also carry
    `head_idx is None`, so before 2026-08-06 they were being mapped as if they
    were MLPs. They are not model components: they are the graph's input and
    output, they appear in essentially every circuit, and they say nothing about
    which parts of the model mattered. Including them would have added a constant
    to every claim and, for `Resid End` at layer `2 * n_blocks + 1`, produced a
    block index outside the valid range.

    Terminals are identified by name rather than by layer arithmetic, so a change
    in the instrument's numbering surfaces as an unmapped node rather than as a
    plausible wrong answer.
    """
    out: set[Component] = set()
    for n in nodes:
        if getattr(n, "name", "").startswith(RESID_TERMINAL_PREFIX):
            continue
        blk = block_index(n.layer, layers_per_block)
        head = getattr(n, "head_idx", None)
        if head is None:
            out.add(Component(layer=blk, index=0, kind="mlp"))
        else:
            out.add(Component(layer=blk, index=int(head), kind="attn"))
    return frozenset(out)


def normalise_position_mass(raw: Mapping[str, float]) -> dict[str, float]:
    """Normalise attribution mass to sum to 1, dropping nothing.

    Claim maps compare segments by rank, so normalisation does not change any
    claim. It is done anyway because the recorded numbers go into `results/` and
    an unnormalised mass is not comparable across specifications.

    An all-zero or empty input is returned as an empty mapping rather than
    producing NaNs. An empty mapping is a legitimate state, and the claim map
    renders it as a stated absence.
    """
    total = sum(raw.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in raw.items()}


def features_from_circuit(
    nodes: Iterable[NodeLike],
    n_blocks: int,
    n_heads_per_block: int,
    position_mass: Mapping[str, float] | None = None,
    layers_per_block: int = AC_LAYERS_PER_BLOCK,
    include_mlps_in_full_count: bool = True,
) -> CircuitFeatures:
    """Build a `CircuitFeatures` from an auto-circuit node set.

    `n_components_full_model` is the denominator for the size class, so what it
    counts is a pre-registration decision, not an implementation detail.

    **Fixed at `include_mlps_in_full_count=True` on 2026-08-06, and the choice is
    forced rather than a judgement.** `components_from_nodes` emits Components
    with `kind="mlp"` when the circuit contains an MLP node, so MLPs can appear
    in the numerator. A denominator that counted attention heads only could
    therefore yield a size fraction above 1, and `size_class` would fall through
    every bin to the last. The numerator and denominator must count the same
    population. For GPT-2 small that is 12 x 12 heads plus 12 MLPs = **156**.
    """
    if n_blocks <= 0:
        raise ValueError(f"n_blocks must be positive, got {n_blocks}")
    if n_heads_per_block <= 0:
        raise ValueError(f"n_heads_per_block must be positive, got {n_heads_per_block}")

    full = n_blocks * n_heads_per_block
    if include_mlps_in_full_count:
        full += n_blocks

    return CircuitFeatures(
        components=components_from_nodes(nodes, layers_per_block),
        n_layers=n_blocks,
        n_components_full_model=full,
        position_mass=normalise_position_mass(position_mass or {}),
    )
