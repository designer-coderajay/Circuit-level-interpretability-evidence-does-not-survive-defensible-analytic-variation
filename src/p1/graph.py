"""The edge namespace, reconstructed from names rather than from the model.

Stage 4 needs a size-matched random-circuit null drawn from the *same* edge
population the discovered circuits came from. The sweep banked only the top
10,000 edges per cell, whose union covers 26,888 of 32,491 edges, 82.8%. Drawing
a "random" circuit from that union would draw from edges some objective already
ranked highly, which is not a null.

So the population is reconstructed combinatorially and checked against the
instrument's own count. For GPT-2 small with 12 blocks and 12 heads:

    block b attention receives from 1 + 13b sources, at three input slots each
    (Q, K, V), for 3 * 12 * (1 + 13b) edges
    MLP b receives from those sources plus its own block's 12 heads
    Resid End receives from all 157 non-terminal sources

    sum over b, plus Resid End = 32,491

which is the number `auto-circuit` reports. That agreement is the verification:
the count is not fitted to the target, it falls out of the ordering.

Node naming is transcribed from what the sweep wrote, not guessed:
`A9.9`, `MLP 3`, `Resid Start`, `Resid End`, and destination slots `A11.10.Q`.
`layer` follows `p1.features.block_index`, which was itself verified against
`transformer_lens_utils.py`: block `b` has attention at `2b + 1` and MLP at
`2b + 2`, with Resid Start at 0.

Nothing here imports torch or auto-circuit. The null must be reproducible on the
analysis machine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "Node",
    "parse_node",
    "enumerate_edges",
    "nodes_from_edge_names",
]

_ATTN = re.compile(r"^A(\d+)\.(\d+)(?:\.([QKV]))?$")
_MLP = re.compile(r"^MLP (\d+)$")


@dataclass(frozen=True)
class Node:
    """Minimal stand-in satisfying `p1.features.NodeLike`.

    `head_idx is None` marks an MLP or a residual terminal, which is the same
    convention `components_from_nodes` already relies on, including its dropping
    of terminals by name prefix.
    """

    name: str
    layer: int
    head_idx: int | None


def parse_node(name: str) -> Node:
    """Name to node. Destination slot suffixes .Q/.K/.V collapse to the head."""
    if name == "Resid Start":
        return Node(name, 0, None)
    if name == "Resid End":
        return Node(name, 25, None)
    m = _ATTN.match(name)
    if m:
        block, head = int(m.group(1)), int(m.group(2))
        return Node(name, 2 * block + 1, head)
    m = _MLP.match(name)
    if m:
        block = int(m.group(1))
        return Node(name, 2 * block + 2, None)
    raise ValueError(f"unrecognised node name: {name!r}")


def enumerate_edges(
    n_blocks: int = 12, n_heads: int = 12, parallel_mlp: bool = False
) -> tuple[str, ...]:
    """Every edge name in the patchable graph, in a deterministic order.

    `parallel_mlp` selects the GPT-NeoX residual layout, in which MLP `b` reads
    the residual stream *before* block `b`'s attention writes to it, so it does
    not receive that block's heads. GPT-2 is sequential and is the default.

    The flag exists because the P1 harness was written against GPT-2 small and
    the second-model replication uses Pythia-160m, which has the same block and
    head counts but not the same edge namespace. Defaulting to False keeps every
    committed GPT-2 number byte-identical.

    VERIFIED 2026-08-12 on a Colab CPU runtime, `auto-circuit` 1.0.1: Pythia-160m
    under `patchable_model(factorized=True, separate_qkv=True)` reports 32,347
    edges against GPT-2 small's 32,491. The 144-edge deficit is `n_blocks *
    n_heads`, and every absent edge has the form `A{b}.{h}->MLP {b}`. The count
    is predicted by the ordering below, not fitted to the observation.
    """
    edges: list[str] = []
    sources: list[str] = ["Resid Start"]
    for b in range(n_blocks):
        heads = [f"A{b}.{h}" for h in range(n_heads)]
        for h in heads:
            for slot in ("Q", "K", "V"):
                edges.extend(f"{s}->{h}.{slot}" for s in sources)
        if parallel_mlp:
            edges.extend(f"{s}->MLP {b}" for s in sources)
            sources.extend(heads)
        else:
            sources.extend(heads)
            edges.extend(f"{s}->MLP {b}" for s in sources)
        sources.append(f"MLP {b}")
    edges.extend(f"{s}->Resid End" for s in sources)
    return tuple(edges)


def nodes_from_edge_names(edge_names) -> list[Node]:
    """Endpoints of each edge, flattened, exactly as `scripts/sweep.py` did.

    The sweep built `nodes = [n for e in order[:k] for n in (e.src, e.dest)]`.
    Duplicates are kept because `components_from_nodes` returns a frozenset and
    deduplicates downstream. Reproducing the flattening rather than tidying it is
    the point: the null must traverse the identical path.
    """
    out: list[Node] = []
    for name in edge_names:
        src, _, dest = name.partition("->")
        out.append(parse_node(src))
        out.append(parse_node(dest))
    return out
