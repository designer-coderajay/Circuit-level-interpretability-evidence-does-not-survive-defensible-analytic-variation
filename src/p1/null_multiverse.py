"""Size-matched random circuits for the null multiverse, PLAN.md section 6.

The slow path, `p1.graph.nodes_from_edge_names` into
`p1.features.features_from_circuit`, is the one verified against the sweep,
7,561 of 7,561 exact. It costs about 107 s per null multiverse, which makes a
distribution over a thousand of them a thirty-hour job on CPU.

This module vectorises exactly one step: mapping edge indices to the set of
components they touch. Everything downstream, `CircuitFeatures`, `layer_band`,
`size_class`, `phi_overseer`, is the identical code the sweep ran. The
vectorised mapping is not trusted on inspection; `components_equal_slow_path`
asserts it against the verified path and is called from the tests.

Why the mapping can be vectorised safely. `components_from_nodes` is a pure
function of each node considered alone: name prefix decides whether it is a
residual terminal to drop, `head_idx` decides attention or MLP, and
`block_index(layer)` decides the block. Nothing depends on which other nodes are
present, so precomputing one component id per edge endpoint and taking the
unique set is the same operation, done once instead of per circuit.
"""

from __future__ import annotations

import numpy as np

from p1.claim_map import CircuitFeatures, Component, phi_overseer
from p1.features import components_from_nodes
from p1.graph import enumerate_edges, parse_node

__all__ = [
    "EdgeComponentIndex",
    "components_equal_slow_path",
]

#: Sentinel for an endpoint that maps to no component, i.e. a residual terminal.
DROPPED = -1


class EdgeComponentIndex:
    """Precomputed edge endpoint to component mapping over the full namespace."""

    def __init__(
        self, n_blocks: int = 12, n_heads: int = 12, parallel_mlp: bool = False
    ):
        """`parallel_mlp` selects the GPT-NeoX edge namespace. See `p1.graph`.

        The null draws from the edge population, so it is the one place in the
        analysis layer that has to know which architecture produced the circuits.
        The component population is identical either way, which is why nothing
        downstream of `_component_id` changes.
        """
        self.edges = enumerate_edges(n_blocks, n_heads, parallel_mlp=parallel_mlp)
        self.n_blocks = n_blocks
        self.n_heads = n_heads
        self.parallel_mlp = parallel_mlp
        self.n_components_full_model = n_blocks * n_heads + n_blocks

        # Component id space: attention head (b, h) -> b * n_heads + h,
        # MLP b -> n_blocks * n_heads + b. Dense and contiguous, so `np.unique`
        # on ids is enough and no dictionary is needed in the hot loop.
        self.components: list[Component] = [
            Component(layer=b, index=h, kind="attn")
            for b in range(n_blocks)
            for h in range(n_heads)
        ] + [Component(layer=b, index=0, kind="mlp") for b in range(n_blocks)]

        table = np.full((len(self.edges), 2), DROPPED, dtype=np.int32)
        for i, name in enumerate(self.edges):
            src, _, dest = name.partition("->")
            table[i, 0] = self._component_id(src)
            table[i, 1] = self._component_id(dest)
        self.table = table
        self._claim_cache: dict[bytes, tuple[str, ...]] = {}

    def _component_id(self, node_name: str) -> int:
        node = parse_node(node_name)
        # Reuse the instrument-facing mapping rather than reimplementing it, so
        # the terminal-dropping rule can only be defined in one place.
        comps = components_from_nodes([node])
        if not comps:
            return DROPPED
        (c,) = comps
        if c.kind == "attn":
            return c.layer * self.n_heads + c.index
        return self.n_blocks * self.n_heads + c.layer

    def component_ids(self, edge_idx: np.ndarray) -> np.ndarray:
        """Sorted distinct component ids touched by these edges.

        `bincount` over the 157-value id space, rather than `unique`, which
        sorts. At k = 10,000 that is 20,000 elements sorted per circuit against a
        fixed-width count, and the null draws 7,561 circuits per replicate.
        """
        counts = np.bincount(
            self.table[edge_idx].ravel() + 1, minlength=self.n_components_full_model + 1
        )
        return np.flatnonzero(counts[1:])

    def features(self, edge_idx: np.ndarray) -> CircuitFeatures:
        """CircuitFeatures for a circuit given as edge indices.

        `position_mass` is left empty. `phi_overseer` uses it only at FINE, and
        the null cannot reach FINE because the sweep never wrote the attention
        cache. Callers must not ask this for FINE or for `phi_affected`.
        """
        return self._features_from_ids(self.component_ids(edge_idx))

    def _features_from_ids(self, ids: np.ndarray) -> CircuitFeatures:
        return CircuitFeatures(
            components=frozenset(self.components[i] for i in ids),
            n_layers=self.n_blocks,
            n_components_full_model=self.n_components_full_model,
        )

    def claims(self, edge_idx: np.ndarray, granularities) -> tuple[str, ...]:
        """Claims for a circuit, memoised on the set of components it touches.

        `phi_overseer` at COARSE and MEDIUM is a pure function of the component
        set, so two circuits touching the same components must produce the same
        claim. Caching on that set is not an approximation.

        It pays because the size distribution is bimodal: 2,067 of 7,561
        specifications select 10,000 edges, and a 10,000-edge random circuit
        almost always touches all 156 components. Those all collapse to one entry.
        """
        ids = self.component_ids(edge_idx)
        key = ids.tobytes()
        hit = self._claim_cache.get(key)
        if hit is None:
            feats = self._features_from_ids(ids)
            hit = tuple(phi_overseer(feats, g) for g in granularities)
            self._claim_cache[key] = hit
        return hit

    def sample(self, k: int, rng: np.random.Generator) -> np.ndarray:
        """k distinct edges drawn uniformly from the full namespace."""
        if not 0 < k <= len(self.edges):
            raise ValueError(f"k must be in 1..{len(self.edges)}, got {k}")
        return rng.choice(len(self.edges), size=k, replace=False)


def components_equal_slow_path(
    index: EdgeComponentIndex, edge_idx: np.ndarray
) -> bool:
    """Assert the vectorised mapping against the path verified on the sweep."""
    from p1.graph import nodes_from_edge_names

    names = [index.edges[i] for i in edge_idx]
    slow = components_from_nodes(nodes_from_edge_names(names))
    return index.features(edge_idx).components == slow
