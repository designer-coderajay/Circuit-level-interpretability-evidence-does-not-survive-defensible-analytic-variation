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
    "CORRUPTION_LEVELS",
    "CORRUPTION_NOT_APPLICABLE",
    "DISCOVERY_OBJECTIVES",
    "DISCOVERY_OBJECTIVE_PARAMS",
    "METRIC_SPECS",
    "EDGE_COUNT_LADDER",
    "FIELDS",
    "IEG_1000_OBJECTIVE",
    "METRICS",
    "GRANULARITIES",
    "Specification",
    "ablation_corruption_cells",
    "discovery_cells",
    "_DISCOVERY_FIELDS",
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

#: How each metric is computed. Fixed 2026-08-06 by Ajay.
#:
#: `patch_type` is load-bearing and getting it backwards silently inverts every
#: faithfulness number. VERIFIED: `TREE_PATCH` ablates the edges **not** in the
#: circuit, so the circuit is retained; `EDGE_PATCH` is the complement and
#: ablates the circuit itself.
#:
#: **Why the split is on logits versus probability.** `logit_diff` and
#: `sufficiency` both ask whether the retained circuit reproduces the model, so
#: computed the same way they would be the identical function and the axis would
#: have four labels and three levels. auto-circuit's native metrics work on raw
#: logits; ERASER's sufficiency and comprehensiveness are defined on predicted
#: probability. Splitting there gives four genuinely distinct functions and keeps
#: the native pair and the ERASER pair cleanly separated.
#:
#: **Sufficiency and comprehensiveness are adaptations, not reproductions**, and
#: the paper says so. ERASER uses the predicted-class probability; this uses the
#: answer-minus-wrong-answer probability difference, because that is the quantity
#: the IOI task is defined on and the one auto-circuit's shipped measurement
#: functions expose.
#:
#: Anchors for `normalised_recovery` come from the same pass: `k = 0` is the
#: empty circuit and `k = n_edges` the full one. Under `TREE_PATCH` that runs
#: fully-ablated to clean; under `EDGE_PATCH` clean to fully-ablated. Gap closing
#: therefore yields 1 for "behaves like the full circuit" in both directions,
#: with no per-metric sign handling.
METRIC_SPECS: Mapping[str, Mapping[str, str | None]] = {
    "logit_diff": {"patch": "TREE_PATCH", "measure": "answer_diff", "prob_func": "logits"},
    "kl_div": {"patch": "TREE_PATCH", "measure": "kl_div", "prob_func": None},
    "sufficiency": {"patch": "TREE_PATCH", "measure": "answer_diff", "prob_func": "softmax"},
    "comprehensiveness": {"patch": "EDGE_PATCH", "measure": "answer_diff", "prob_func": "softmax"},
}

#: The call parameters behind each named `PruneAlgo` constant. VERIFIED
#: 2026-08-05 by reading `auto_circuit/prune_algos/prune_algos.py`.
#:
#: Transcribed rather than imported so that the sweep does not silently follow a
#: library change: if a future auto-circuit alters one of these constants, the
#: grid would change underneath a locked pre-registration with nothing raising.
#: A test asserts these match the installed library.
DISCOVERY_OBJECTIVE_PARAMS: Mapping[str, Mapping[str, object]] = {
    "PROB_GRAD_PRUNE_ALGO": {
        "grad_function": "prob", "answer_function": "avg_val", "mask_val": 0.0},
    "LOGIT_EXP_GRAD_PRUNE_ALGO": {
        "grad_function": "logit_exp", "answer_function": "avg_val", "mask_val": 0.0},
    "LOGPROB_GRAD_PRUNE_ALGO": {
        "grad_function": "logprob", "answer_function": "avg_val", "mask_val": 0.0},
    "LOGPROB_DIFF_GRAD_PRUNE_ALGO": {
        "grad_function": "logprob", "answer_function": "avg_diff", "mask_val": 0.0},
    "LOGIT_DIFF_GRAD_PRUNE_ALGO": {
        "grad_function": "logit", "answer_function": "avg_diff", "mask_val": 0.0},
    "LOGIT_MSE_GRAD_PRUNE_ALGO": {
        "grad_function": "logit", "answer_function": "mse", "mask_val": 0.0},
    "INTEGRATED_EDGE_GRADS_PRUNE_ALGO": {
        "grad_function": "logit", "answer_function": "avg_val",
        "integrated_grad_samples": 50},
    "INTEGRATED_EDGE_GRADS_LOGIT_DIFF_PRUNE_ALGO": {
        "grad_function": "logit", "answer_function": "avg_diff",
        "integrated_grad_samples": 1000},
}

#: Edge-level is the confirmatory grid. Node-level is a reported contrast, not a
#: second grid. See docs/DESIGN-DELTAS.md D8.
GRANULARITIES: tuple[str, ...] = ("edge", "node")

#: The corruption axis. Four levels, all transcribed from arXiv:2211.00593,
#: VERIFIED 2026-08-06 by fetching the PDF and quoting verbatim. Decision by
#: Ajay, 2026-08-06.
#:
#: Each level cites a published construction, which is the standard every axis in
#: this grid meets. Definitions, verbatim from the source:
#:
#: - ``ABC``            section 3: "instead of using two names (IO and S) it used
#:                      three unrelated random names (A, B and C). In pABC,
#:                      sentences no longer have a single plausible IO, but the
#:                      grammatical structures from the pIOI templates are
#:                      preserved." This is the distribution the paper uses for
#:                      all knockouts, and the de facto default.
#: - ``RANDOM_NAME_FLIP`` appendix A: "we replace the names from a given sentence
#:                      with random names, but we keep the same position for all
#:                      names. Moreover, each occurrence of a name in the original
#:                      sentence is replaced by the same random name."
#: - ``IO_S1_FLIP``     appendix A: "we swap the position of IO and S1. The output
#:                      of S-inhibition heads will contain correct token signals
#:                      ... but inverted positional signals".
#: - ``IO_FROM_S2``     appendix A: "we make IO become the subject of the sentence
#:                      and S the indirect object. In this dataset, both token
#:                      signals and positional signals are inverted."
#:
#: **The source quantifies that these carry different information**, reporting
#: that logit difference is approximated by ``2.31*S_pos + 0.99*S_tok`` with 7%
#: mean error. That is not a defect of the axis but it must be handled in the
#: paper: a reviewer will say a claim shift across known-different counterfactuals
#: is tautological. The answer is the pairwise decomposition described in
#: preregistration/PLAN.md section 3, which isolates the ABC versus
#: RANDOM_NAME_FLIP pair. Those two are both "replace the names with random
#: names" and differ only in whether the duplicate-name structure survives, so an
#: analyst choosing between them would not believe they were making a substantive
#: choice. A flip across that pair alone cannot be dismissed as tautological.
#:
#: Note on ``IO_FROM_S2``: it produces a valid IOI sentence with a different
#: answer rather than a degraded one. This does not break anything mechanically,
#: because `mask_gradient_prune_scores` scores `model(batch.clean)` against
#: `batch.answers` and the corrupt prompt supplies ablation activations only. It
#: is a substantively different kind of counterfactual and is described as such.
CORRUPTION_LEVELS: tuple[str, ...] = (
    "ABC",
    "RANDOM_NAME_FLIP",
    "IO_S1_FLIP",
    "IO_FROM_S2",
)

#: Where `C(s)` is located on the prune-score ranking. Fixed 2026-08-05.
#:
#: `tau` is metric-relative, so the criterion is "recovers `(1 - tau)` of metric
#: `m` on the full model". The criterion alone does not determine a circuit: a
#: coarse ladder and a bisection return different circuits for the same `tau`,
#: and a different circuit is a different claim. `C(s)` is therefore defined as
#: **the smallest rung of this ladder meeting the criterion, scanning upward**.
#:
#: Bisection was rejected on soundness rather than cost. Metric recovery is not
#: guaranteed monotone in edge count; an upward ladder scan is well defined
#: either way, and bisection is not. It would also cost about 15 evaluations
#: against this ladder's 10.
#:
#: The top rung is deliberately below the 32,491-edge full model. A specification
#: needing more than 10,000 edges, roughly 31% of the graph, to recover
#: `(1 - tau)` is DISCARDED rather than handed a degenerate whole-model circuit.
#: Adding 32,491 as a rung would make the criterion trivially satisfiable and
#: silently convert a failure into a meaningless claim.
EDGE_COUNT_LADDER: tuple[int, ...] = (
    10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000,
)


# --------------------------------------------------------------------------
# Specification
# --------------------------------------------------------------------------


#: Fields that require a forward pass. Metric and threshold are excluded: the
#: `(metric, tau)` cut is post-hoc on an existing ranking.
_DISCOVERY_FIELDS: tuple[str, ...] = (
    "discovery_objective",
    "ablation",
    "corruption",
    "prompt_variant",
    "seed",
    "granularity",
)


@dataclass(frozen=True, order=True)
class Specification:
    """One point in S.

    Field order is the canonical order and is load-bearing: it determines the
    sort order of the specification curve and the byte string hashed for
    ``spec_id``. Do not reorder fields after a pre-registration is locked.
    """

    discovery_objective: str
    ablation: str
    corruption: str
    metric: str
    threshold: float
    prompt_variant: str
    seed: int
    granularity: str = "edge"

    def __post_init__(self) -> None:
        allowed_objectives = DISCOVERY_OBJECTIVES + (IEG_1000_OBJECTIVE,)
        if self.discovery_objective not in allowed_objectives:
            raise ValueError(
                f"unknown discovery objective {self.discovery_objective!r}; "
                f"expected a named auto-circuit PruneAlgo constant from "
                f"{allowed_objectives}"
            )
        if self.ablation not in AUTO_CIRCUIT_ABLATIONS:
            raise ValueError(
                f"unknown ablation {self.ablation!r}; auto-circuit 1.0.1 ships "
                f"{AUTO_CIRCUIT_ABLATIONS}"
            )

        # Corruption is a closed set now that the levels are sourced. An
        # unvalidated free-form string means a typo silently produces a different
        # spec_id and therefore an orphaned results file, which is the same
        # failure mode the pinned regression test exists to prevent.
        if self.corruption not in CORRUPTION_LEVELS + (CORRUPTION_NOT_APPLICABLE,):
            raise ValueError(
                f"unknown corruption {self.corruption!r}; expected one of "
                f"{CORRUPTION_LEVELS} or {CORRUPTION_NOT_APPLICABLE!r}. Each "
                f"level must cite a published construction; see spec.py."
            )

        # The nesting invariant, enforced on the object rather than only in the
        # enumerator. Two of the seven operators ignore the corrupt distribution
        # entirely, so a specification that pairs one of them with a real
        # corruption level is not a distinct specification, it is a duplicate
        # wearing a label. Making that unconstructible is what guarantees the
        # multiverse contains no duplicates, regardless of how it was built.
        # See DESIGN-DELTAS D18.
        depends = self.ablation in CORRUPTION_DEPENDENT_ABLATIONS
        if depends and self.corruption == CORRUPTION_NOT_APPLICABLE:
            raise ValueError(
                f"ablation {self.ablation!r} reads the corrupt distribution, so "
                f"corruption must be a real level, not {CORRUPTION_NOT_APPLICABLE!r}"
            )
        if not depends and self.corruption != CORRUPTION_NOT_APPLICABLE:
            raise ValueError(
                f"ablation {self.ablation!r} ignores the corrupt distribution, so "
                f"corruption must be {CORRUPTION_NOT_APPLICABLE!r}, got "
                f"{self.corruption!r}. Crossing them would create duplicate "
                f"specifications; corruption is nested within ablation."
            )

        if self.metric not in METRICS:
            raise ValueError(f"unknown metric {self.metric!r}; expected one of {METRICS}")
        if not 0.0 < self.threshold < 1.0:
            raise ValueError(
                f"threshold is metric-relative and must lie in (0, 1), got "
                f"{self.threshold}. An absolute edge count is a different "
                f"convention and is not what this grid pre-registered."
            )
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

    @property
    def discovery_key(self) -> tuple:
        """The fields that require a forward pass, in canonical order.

        `tau` is metric-relative and the `(metric, tau)` cut is applied post-hoc
        to an existing prune-score ranking, so two specifications differing only
        in metric or threshold share a discovery. That is the reuse architecture
        measured at Gate 2, and it is why the sweep costs 1,540 discoveries
        rather than 18,480.
        """
        return (
            self.discovery_objective,
            self.ablation,
            self.corruption,
            self.prompt_variant,
            self.seed,
            self.granularity,
        )

    @property
    def discovery_id(self) -> str:
        """Deterministic 16-hex identifier for the discovery cell.

        The sweep writes one manifest and one ranking per `discovery_id` and
        skips any cell whose manifest already reports `status: ok`. The results
        directory is therefore the checkpoint, with no separate state file that
        could be corrupted by a session dying mid-write.

        Built the same way as `spec_id`: SHA-256 of a canonical JSON encoding,
        never Python's salted `hash`, so a cell computed in one Colab session
        matches the same cell in the next one.
        """
        payload = json.dumps(
            dict(zip(_DISCOVERY_FIELDS, self.discovery_key)),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# Grid
# --------------------------------------------------------------------------


FIELDS: tuple[str, ...] = (
    "discovery_objective",
    "ablation",
    "corruption",
    "metric",
    "threshold",
    "prompt_variant",
    "seed",
    "granularity",
)


def _validate_axes(axes: Mapping[str, Sequence]) -> None:
    missing = [f for f in FIELDS if f not in axes]
    if missing:
        raise ValueError(f"axes missing required fields: {missing}")
    unknown = [k for k in axes if k not in FIELDS]
    if unknown:
        raise ValueError(f"axes has unknown fields: {unknown}")
    for f in FIELDS:
        if len(axes[f]) == 0:
            raise ValueError(f"axis {f!r} has no levels")
    if CORRUPTION_NOT_APPLICABLE in axes["corruption"]:
        raise ValueError(
            f"{CORRUPTION_NOT_APPLICABLE!r} is a sentinel inserted by the "
            f"enumerator for corruption-independent ablations. It is not a level "
            f"and must not appear in the corruption axis."
        )


def enumerate_grid(axes: Mapping[str, Sequence]) -> Iterator[Specification]:
    """Enumerate the grid in deterministic canonical-field order.

    ``axes`` maps each ``Specification`` field name to its levels.

    **Crossed on every axis except corruption, which is nested within ablation.**
    The five operators that read the corrupt distribution get every corruption
    level; the two that ignore it get the ``CORRUPTION_NOT_APPLICABLE`` sentinel
    exactly once. Crossing them instead would emit three identical
    specifications, 19% of the previous grid, which misrepresents the multiverse
    and would plot three coincident points on the specification curve. See
    DESIGN-DELTAS D18.

    The sentinel is used rather than silently reusing the first corruption level,
    so that a non-applicable cell is distinguishable from a real one in
    ``spec_id`` and in every figure.

    Iteration follows the canonical field order, so the enumeration is stable
    across runs and machines and can be resumed by index. Ablation precedes
    corruption in that order, which is what makes the nesting expressible without
    breaking stability.

    Beyond the nesting, the grid is fully crossed by design. If pruning becomes
    necessary on feasibility grounds, it must be the documented fractional
    factorial fixed in the pre-registration, not a filter applied here. Arbitrary
    pruning is itself a researcher degree of freedom.
    """
    _validate_axes(axes)
    for objective in axes["discovery_objective"]:
        for ablation in axes["ablation"]:
            corruptions = (
                tuple(axes["corruption"])
                if ablation in CORRUPTION_DEPENDENT_ABLATIONS
                else (CORRUPTION_NOT_APPLICABLE,)
            )
            for corruption in corruptions:
                for combo in product(
                    axes["metric"],
                    axes["threshold"],
                    axes["prompt_variant"],
                    axes["seed"],
                    axes["granularity"],
                ):
                    metric, threshold, prompt_variant, seed, granularity = combo
                    yield Specification(
                        discovery_objective=objective,
                        ablation=ablation,
                        corruption=corruption,
                        metric=metric,
                        threshold=threshold,
                        prompt_variant=prompt_variant,
                        seed=seed,
                        granularity=granularity,
                    )


def ablation_corruption_cells(axes: Mapping[str, Sequence]) -> int:
    """Number of distinct (ablation, corruption) pairs under the nesting."""
    _validate_axes(axes)
    dependent = sum(1 for a in axes["ablation"] if a in CORRUPTION_DEPENDENT_ABLATIONS)
    independent = len(axes["ablation"]) - dependent
    return dependent * len(axes["corruption"]) + independent


def discovery_cells(axes: Mapping[str, Sequence]) -> int:
    """Number of prune-score rankings the grid requires.

    This, not ``grid_size``, is what the sweep budget scales with. ``tau`` is
    metric-relative, so the ``(metric, tau)`` cut is applied post-hoc to an
    existing ranking and costs an evaluation, not a discovery.
    """
    _validate_axes(axes)
    return (
        len(axes["discovery_objective"])
        * ablation_corruption_cells(axes)
        * len(axes["prompt_variant"])
        * len(axes["seed"])
        * len(axes["granularity"])
    )


def grid_size(axes: Mapping[str, Sequence]) -> int:
    """Size of the nested grid, without materialising it.

    Computed analytically and asserted equal to ``len(list(enumerate_grid(...)))``
    in the tests, so the closed form and the enumerator cannot drift apart.
    """
    _validate_axes(axes)
    return (
        len(axes["discovery_objective"])
        * ablation_corruption_cells(axes)
        * len(axes["metric"])
        * len(axes["threshold"])
        * len(axes["prompt_variant"])
        * len(axes["seed"])
        * len(axes["granularity"])
    )
