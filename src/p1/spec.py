"""The specification space S.

A specification is the tuple of defensible analytic choices that a competent
analyst must fix before a circuit can be discovered and a claim derived:

    s = (a, d, m, tau, P, r)

Every reported number must be traceable to a config, a seed, and an environment
hash. `Specification.spec_id` is the config half of that: a deterministic,
machine-independent identifier derived from the specification's own content.

No torch dependency. The grid must be enumerable and testable without a GPU.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from itertools import product
from typing import Iterator, Mapping, Sequence

__all__ = [
    "AUTO_CIRCUIT_ABLATIONS",
    "METRICS",
    "GRANULARITIES",
    "Specification",
    "enumerate_grid",
    "grid_size",
]


# --------------------------------------------------------------------------
# Verified axis levels
# --------------------------------------------------------------------------

#: The seven members of ``auto_circuit.types.AblationType`` in auto-circuit
#: 1.0.1, transcribed verbatim from the enum. VERIFIED 2026-08-03 by reading
#: ``auto_circuit/types.py`` in the released wheel.
#:
#: Note what is absent. Gaussian-noise ablation (Meng et al., 2022) and optimal
#: ablation (arXiv:2409.09951) are both named in the literature and neither is
#: implemented here. The operator axis is therefore defined as "what the
#: reference implementation ships", which is the position the paper defends.
#:
#: Note also that five of the seven are mean variants. "Mean ablation" is not
#: one choice. arXiv:2407.08734 section 3.1.3 names "an additional choice in the
#: size of the mean ablation dataset" and does not cross it. P1 does.
AUTO_CIRCUIT_ABLATIONS: tuple[str, ...] = (
    "RESAMPLE",
    "ZERO",
    "TOKENWISE_MEAN_CLEAN",
    "TOKENWISE_MEAN_CORRUPT",
    "TOKENWISE_MEAN_CLEAN_AND_CORRUPT",
    "BATCH_TOKENWISE_MEAN",
    "BATCH_ALL_TOK_MEAN",
)

#: Faithfulness metrics. The first two are auto-circuit native and are used
#: verbatim. The last two are ERASER-style and are implemented in `src/p1` as an
#: additive extension that never edits the instrument; they are reported as an
#: extension in the paper.
#:
#: Justification for crossing this axis at all, which the brief did not supply:
#: arXiv:2407.08734 section 3.2 declines to cross it and calls the choice "in
#: general free", and Annex IV section 4 separately requires "a description of
#: the appropriateness of the performance metrics for the specific AI system".
METRICS: tuple[str, ...] = (
    "logit_diff",
    "kl_div",
    "sufficiency",
    "comprehensiveness",
)

#: Edge-level is the confirmatory grid. Node-level is a reported contrast, not a
#: second grid. See docs/DESIGN-DELTAS.md D8.
GRANULARITIES: tuple[str, ...] = ("edge", "node")


# --------------------------------------------------------------------------
# Specification
# --------------------------------------------------------------------------


@dataclass(frozen=True, order=True)
class Specification:
    """One point in S.

    Field order is the canonical order and is load-bearing: it determines the
    sort order of the specification curve and the byte string hashed for
    ``spec_id``. Do not reorder fields after a pre-registration is locked.
    """

    ablation: str
    corruption: str
    metric: str
    threshold: float
    prompt_variant: str
    seed: int
    granularity: str = "edge"

    def __post_init__(self) -> None:
        if self.ablation not in AUTO_CIRCUIT_ABLATIONS:
            raise ValueError(
                f"unknown ablation {self.ablation!r}; auto-circuit 1.0.1 ships "
                f"{AUTO_CIRCUIT_ABLATIONS}"
            )
        if self.metric not in METRICS:
            raise ValueError(f"unknown metric {self.metric!r}; expected one of {METRICS}")
        if self.granularity not in GRANULARITIES:
            raise ValueError(
                f"unknown granularity {self.granularity!r}; expected one of {GRANULARITIES}"
            )
        if self.seed < 0:
            raise ValueError(f"seed must be non-negative, got {self.seed}")

    def canonical(self) -> str:
        """Canonical JSON encoding. Sorted keys, no whitespace, fixed separators."""
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    @property
    def spec_id(self) -> str:
        """Deterministic 16-hex-character identifier.

        SHA-256 of the canonical encoding, truncated. Deliberately **not**
        Python's built-in ``hash``: that is salted per process by default, so
        the same specification would produce different ids on different runs and
        every results filename would become unreproducible. A pinned regression
        test asserts one known literal value so that any future change to the
        field set or the encoding is caught rather than silently renaming every
        result on disk.
        """
        return hashlib.sha256(self.canonical().encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# Grid
# --------------------------------------------------------------------------


def enumerate_grid(axes: Mapping[str, Sequence]) -> Iterator[Specification]:
    """Enumerate the fully crossed grid in deterministic order.

    ``axes`` maps each ``Specification`` field name to its levels. Order of
    iteration follows the canonical field order, so the enumeration is stable
    across runs and machines and can be resumed by index.

    The grid is fully crossed by design. If pruning becomes necessary on
    feasibility grounds, it must be a documented fractional factorial fixed in
    the pre-registration, not a filter applied here. Arbitrary pruning is itself
    a researcher degree of freedom.
    """
    fields = [
        "ablation",
        "corruption",
        "metric",
        "threshold",
        "prompt_variant",
        "seed",
        "granularity",
    ]
    missing = [f for f in fields if f not in axes]
    if missing:
        raise ValueError(f"axes missing required fields: {missing}")
    unknown = [k for k in axes if k not in fields]
    if unknown:
        raise ValueError(f"axes has unknown fields: {unknown}")
    for f in fields:
        if len(axes[f]) == 0:
            raise ValueError(f"axis {f!r} has no levels")

    for combo in product(*(axes[f] for f in fields)):
        yield Specification(**dict(zip(fields, combo)))


def grid_size(axes: Mapping[str, Sequence]) -> int:
    """Size of the fully crossed grid, without materialising it."""
    n = 1
    for levels in axes.values():
        n *= len(levels)
    return n
