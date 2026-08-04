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


def block_index(ac_layer: int, layers_per_block: int = AC_LAYERS_PER_BLOCK) -> int:
    """Convert an auto-circuit layer index to a transformer block index."""
    if ac_layer < 0:
        raise ValueError(f"auto-circuit layer must be non-negative, got {ac_layer}")
    if layers_per_block < 1:
        raise ValueError(f"layers_per_block must be at least 1, got {layers_per_block}")
    return ac_layer // layers_per_block


def components_from_nodes(
    nodes: Iterable[NodeLike],
    layers_per_block: int = AC_LAYERS_PER_BLOCK,
) -> frozenset[Component]:
    """Map auto-circuit nodes to `Component`s indexed by transformer block.

    A node with `head_idx is None` is treated as an MLP block and given
    `kind="mlp"` with `index=0`, so attention head 0 and the MLP of the same
    block never collide.
    """
    out: set[Component] = set()
    for n in nodes:
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
    counts is a pre-registration decision, not an implementation detail. The
    default counts every attention head plus one MLP per block. Setting
    `include_mlps_in_full_count=False` counts heads only. Whichever is chosen
    must be fixed before the sweep, because changing it shifts every size class
    and therefore every MEDIUM and FINE claim.
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
