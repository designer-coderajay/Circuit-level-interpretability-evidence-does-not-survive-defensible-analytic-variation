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
    "CORRUPTION_DEPENDENT_ABLATIONS",
    "CORRUPTION_NOT_APPLICABLE",
    "DISCOVERY_OBJECTIVES",
    "IEG_1000_OBJECTIVE",
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
#: one choice.
#:
#: arXiv:2407.08734 section 3.1.3 additionally names "an additional choice in the
#: size of the mean ablation dataset" and does not cross it. **P1 does not cross
#: it either, and an earlier version of this docstring wrongly said it did.**
#: VERIFIED 2026-08-05 from ``auto_circuit/prune_algos/mask_gradient.py``: the
#: function takes a single ``dataloader`` and passes that same object both to
#: ``batch_src_ablations``, which builds the ablation values, and to the
#: ``for batch in dataloader`` gradient loop, which is the discovery data.
#: Varying the size of one varies the other. The axis is not separable without
#: modifying the instrument, so it is out of scope. See DESIGN-DELTAS D18.
AUTO_CIRCUIT_ABLATIONS: tuple[str, ...] = (
    "RESAMPLE",
    "ZERO",
    "TOKENWISE_MEAN_CLEAN",
    "TOKENWISE_MEAN_CORRUPT",
    "TOKENWISE_MEAN_CLEAN_AND_CORRUPT",
    "BATCH_TOKENWISE_MEAN",
    "BATCH_ALL_TOK_MEAN",
)

#: Sentinel recorded in ``Specification.corruption`` when the chosen ablation
#: operator does not read the corrupt distribution at all. It is deliberately not
#: one of the real corruption levels: silently reusing level zero would make a
#: non-applicable cell indistinguishable from a real one in ``spec_id`` and on
#: the specification curve.
CORRUPTION_NOT_APPLICABLE: str = "n/a"

#: The five ablation operators that read the corrupt distribution, **given that
#: `clean_corrupt` is fixed at "corrupt"**. VERIFIED 2026-08-05 from
#: ``auto_circuit/utils/ablation_activations.py`` and ``auto_circuit/types.py``.
#:
#: The two absentees are the whole of D18. ``ZERO`` sets ``out = t.zeros_like(out)``
#: and forces ``input_batch = batch.clean``; ``TOKENWISE_MEAN_CLEAN`` reads the
#: clean dataset only. Crossing either against three corruption levels yields
#: three identical specifications, which is why corruption is nested inside this
#: axis rather than crossed with it.
#:
#: The conditional matters. ``BATCH_TOKENWISE_MEAN`` and ``BATCH_ALL_TOK_MEAN``
#: are corruption-dependent only because ``clean_corrupt`` is fixed at
#: ``"corrupt"``. Under ``"clean"`` they would join the two absentees and the
#: nesting structure would change. If that fix is ever revisited, this set must
#: be recomputed, not edited by hand.
CORRUPTION_DEPENDENT_ABLATIONS: frozenset[str] = frozenset(
    {
        "RESAMPLE",
        "TOKENWISE_MEAN_CORRUPT",
        "TOKENWISE_MEAN_CLEAN_AND_CORRUPT",
        "BATCH_TOKENWISE_MEAN",
        "BATCH_ALL_TOK_MEAN",
    }
)

#: The confirmatory discovery-objective axis: auto-circuit's own named
#: ``PruneAlgo`` module-level constants, referenced by constant name so that each
#: level cites a published implementation by construction rather than by
#: assertion. VERIFIED 2026-08-05 from
#: ``auto_circuit/prune_algos/prune_algos.py``.
#:
#: Six of the seven set ``mask_val=0.0``, which the library's own docstring notes
#: is exactly equivalent to edge attribution patching. The seventh sets
#: ``integrated_grad_samples=50``. Constructing a synthetic grad_function x
#: answer_function grid instead was considered and rejected: see DESIGN-DELTAS
#: D15.
DISCOVERY_OBJECTIVES: tuple[str, ...] = (
    "PROB_GRAD_PRUNE_ALGO",  # prob     / avg_val  / mask_val=0.0
    "LOGIT_EXP_GRAD_PRUNE_ALGO",  # logit_exp/ avg_val  / mask_val=0.0
    "LOGPROB_GRAD_PRUNE_ALGO",  # logprob  / avg_val  / mask_val=0.0
    "LOGPROB_DIFF_GRAD_PRUNE_ALGO",  # logprob  / avg_diff / mask_val=0.0
    "LOGIT_DIFF_GRAD_PRUNE_ALGO",  # logit    / avg_diff / mask_val=0.0  (canonical EAP)
    "LOGIT_MSE_GRAD_PRUNE_ALGO",  # logit    / mse      / mask_val=0.0
    "INTEGRATED_EDGE_GRADS_PRUNE_ALGO",  # logit / avg_val / integrated_grad_samples=50
)

#: The reduced arm. Reported separately and never pooled with the confirmatory
#: grid.
#:
#: **This comparison is confounded and the paper must say so.** VERIFIED
#: 2026-08-05: ``INTEGRATED_EDGE_GRADS_PRUNE_ALGO`` is
#: ``answer_function="avg_val", integrated_grad_samples=50`` and
#: ``INTEGRATED_EDGE_GRADS_LOGIT_DIFF_PRUNE_ALGO`` is
#: ``answer_function="avg_diff", integrated_grad_samples=1000``. They differ in
#: two parameters, not one, so a difference between them **cannot be attributed
#: to the integrated-gradient sample count**. The slice compares two shipped IEG
#: configurations and nothing finer. Isolating sample count would require a
#: synthetic constant that the library does not ship, which D15 rules out.
IEG_1000_OBJECTIVE: str = "INTEGRATED_EDGE_GRADS_LOGIT_DIFF_PRUNE_ALGO"

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
