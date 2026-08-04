# Design deltas: brief versus verified reality

Open decisions where the P1 brief differs from what the instrument actually
provides, or from what has been learned since the brief was written. Nothing
here is silently resolved. Each delta needs an explicit call from Ajay before
the pre-registration is locked.

Epistemic tags: **VERIFIED** means fetched or read from source this session.
**RECALLED** means from training, unverified. **INFERRED** means reasoning.

Last updated 2026-08-03.

---

## D1. The ablation dimension is larger than the brief assumes

**Status: open. Blocks grid definition.**

The brief specifies `a in {zero, mean, resample, optimal}`, four options.

**VERIFIED** by reading `auto_circuit/types.py` in auto-circuit 1.0.1, the
`AblationType` enum provides seven, quoted verbatim:

```
RESAMPLE                        use the corresponding activation from the corrupt forward pass
ZERO                            a vector of zeros
TOKENWISE_MEAN_CLEAN            token-wise mean of clean input over the dataset
TOKENWISE_MEAN_CORRUPT          token-wise mean of corrupt input over the dataset
TOKENWISE_MEAN_CLEAN_AND_CORRUPT  token-wise mean of both over the dataset
BATCH_TOKENWISE_MEAN            token-wise mean over the current batch
BATCH_ALL_TOK_MEAN              mean over all tokens in the current batch
```

Two consequences.

1. "Mean ablation" is not one choice. It is five, and **which mean** is itself
   an undocumented researcher degree of freedom. This strengthens P1 rather
   than complicating it: the operator dimension is larger than the field
   treats it as being, and that is a reportable finding on its own.

2. **Optimal ablation is not in auto-circuit.** It is a separate contribution
   (arXiv:2409.09951, VERIFIED to exist with matching abstract). Including it
   means either importing its authors' code as a second instrument or
   implementing it inside the harness. The latter conflicts with the standing
   rule against modifying a published instrument under test.

**Decision needed.** Pick one:

- (a) Use all seven auto-circuit operators, drop optimal ablation, and state in
  the paper that the operator space is defined as what the reference
  implementation ships. Cleanest defensibility.
- (b) Seven plus optimal ablation via the original authors' code, reported as a
  clearly separated arm so the "verbatim instrument" claim stays intact.
- (c) Collapse the five means to a documented subset and pre-register the
  collapse rule. Reduces the grid, but the collapse is itself a researcher
  degree of freedom and must be justified.

**Recommendation (INFERRED):** (a) for the confirmatory analysis, with (b) as a
labelled robustness arm if compute allows.

---

## D2. The faithfulness metrics do not line up

**Status: open. Blocks grid definition and the claim map.**

The brief specifies `m in {sufficiency, comprehensiveness, F1, logit-difference
recovery}`.

**VERIFIED** by reading `auto_circuit/metrics/prune_metrics/prune_metrics.py`,
the shipped registry includes: Clean KL Div, Corrupt KL Div, Answer Logit,
Wrong Answer Logit, Answer Prob, Answer Logprob, Logit Diff, and further
entries beyond the section read.

Logit-difference recovery maps onto Logit Diff. **Sufficiency and
comprehensiveness are ERASER-style metrics and are not in this registry.**
Their F1 combination therefore is not either.

This matters more than it looks. Sufficiency and comprehensiveness are the
metrics carried over from prior work in this programme, and arXiv:2308.14272
(VERIFIED) shows both can be inflated without changing predictions or
explanations. Using them is defensible, but they must be implemented outside
auto-circuit and reported as an extension, not as instrument output.

**Decision needed.** Pick one:

- (a) Confirmatory grid uses auto-circuit's native metrics only. Sufficiency
  and comprehensiveness appear in a separate, clearly labelled arm.
- (b) Implement ERASER metrics in `src/p1/` as a documented extension layer
  that never edits auto-circuit, and include them in the main grid.
- (c) Drop sufficiency and comprehensiveness from P1 entirely.

**Recommendation (INFERRED):** (b), because the sufficiency-versus-adequacy gap
is a thread running through the whole programme and dropping it costs
continuity. The extension layer must be additive only.

---

## D3. Grid arithmetic

**Status: open, follows from D1 and D2.**

The brief's grid is 4 operators x 3 corruptions x 4 metrics x 3 thresholds x 3
prompt variants x 5 seeds. **VERIFIED by arithmetic:** that is 2,160.

Under D1(a) with seven operators and the same other dimensions the grid is
7 x 3 x 4 x 3 x 3 x 5 = **3,780**.

**Not yet established:** whether either figure is achievable in the 10 to 24
August window on a single 24GB GPU. The brief asserts feasibility; no timing
measurement exists. Do not repeat the feasibility claim in the paper or in
planning until the smoke config has produced a measured per-run cost. That
measurement is the first thing the harness should produce.

If pruning proves necessary, the pruning rule must be a documented fractional
factorial fixed in the pre-registration. Arbitrary pruning is a researcher
degree of freedom and a reviewer will say so.

---

## D4. Functional-equivalence arm, added 2026-08-03

**Status: accepted by Ajay. Needs design.**

arXiv:2606.06267, *Many Circuits, One Mechanism: Input Variation and Evaluation
Granularity in Circuit Discovery* (Bayat Makou, Niu, Dutta, Gurevych, UKP Lab
TU Darmstadt). **VERIFIED** that the ID resolves to this title and these
authors. Reported findings below are **RECALLED from search summaries, not from
reading the paper**, and must be confirmed against the PDF before any of them
is cited or relied on:

- structurally distinct circuits implementing the same computation, termed
  "phantom specialization";
- a shared core recovering at least 99% of circuit performance;
- source-level evaluation inflating apparent faithfulness relative to
  edge-level evaluation;
- 75 circuits from Literal Sequence Copying across frequency bands in five
  Pythia models, 70M to 1.4B.

**Why this is load-bearing.** P1's claim map is structural. If structural
difference does not imply functional difference, then a high flip rate does not
by itself demonstrate that the evidence is unstable in a way that matters, and
H1 and H2 do not support the conclusion as originally framed.

**The adopted response.** Add an interchange-intervention arm. For circuit
pairs with low Jaccard overlap, test whether the circuits are functionally
interchangeable. Report three quantities: structural instability, functional
instability, and the gap between them. The gap is the contribution: Annex IV
regulates the structural description while the safety-relevant property is
functional, and a conformity assessment body reading a filing cannot tell which
it has been given.

**Open sub-decisions.**

- Which interchange protocol. It should be theirs, reproduced verbatim, not a
  variant. Requires reading the paper's method section.
- Whether the edge-level versus source-level granularity finding forces P1 to
  run both granularities rather than treating edge-level as a secondary variant.
- Whether phantom specialization changes the random-circuit baseline. If random
  circuits are also often functionally equivalent to discovered ones, that is
  a much stronger H3 result and needs to be anticipated in the pre-registration
  rather than discovered later.

**Action:** read 2606.06267 in full before locking the pre-registration.

---

## D5. Compute placement

**Status: resolved 2026-08-03.**

Development sandbox is 4 CPU cores, 3GB RAM, no GPU, aarch64. **VERIFIED** by
inspection. The sweep cannot run there.

Resolution: harness built and unit-tested in the sandbox against small configs,
full sweep on a rented GPU. All code written device-agnostic. The statistics
layer has no torch dependency and runs anywhere, which is why
`requirements-analysis.txt` exists separately.

---

## D6. Citation title discrepancy for the closest prior work

**Status: resolved, recorded so it is not rediscovered.**

arXiv:2407.08734 carries the title *Transformer Circuit Faithfulness Metrics
are not Robust* on the arXiv abstract page. The BibTeX entry in the project's
own README gives the COLM 2024 title as *Transformer Circuit Evaluation Metrics
Are Not Robust*. Both **VERIFIED** this session from arxiv.org and from the
GitHub README respectively.

Cite the COLM version of record with the COLM title. Note the arXiv title in
the ledger so a reader chasing the arXiv ID is not confused.

---

## D7. The brief's positioning sentence is unsupported

**Status: open. Blocks the abstract and the related-work framing.**

The brief says of 2407.08734: "they establish that one dimension matters; you
measure the crossed space."

**VERIFIED false.** Section 3.1 of that paper surveys five ablation-methodology
dimensions: 3.1.1 circuit granularity, 3.1.2 ablation component type and
associated model views, 3.1.3 ablation value, 3.1.4 token positions, 3.1.5
ablation direction and testing circuits.

Do not write the crossed-space claim as the differentiator. **P1's
differentiation is the propagation to a regulatory claim and the filability
criterion, and nothing else.** That differentiation is strong and verified: both
2407.08734 and 2606.06267 score zero on every regulatory and conformity term
tested.

Two quotable gaps do survive and should be used instead.

- On metrics, verbatim from section 3.2: "In this work we will focus on the
  metrics used by the respective authors of the circuits that we study, but note
  these choices are also in general free." They did not cross the metric
  dimension. This is a documented gap P1 fills, and it is a stronger
  justification for the metric axis than the brief supplied.
- On ablation values, verbatim from section 3.1.3: "We focus on Mean and
  Resample Ablations in this work." Two of the four values they name.

---

## D8. Evaluation granularity

**Status: resolved 2026-08-03.**

The brief treats the edge-level run as a secondary variant. 2606.06267 reports,
verbatim from its abstract, that "source-level evaluation inflates apparent
faithfulness, while edge-level evaluation reveals the many-to-one mapping from
structure to function", and its section 6.2 carries the heading "Edge-level
evaluation should be the primary metric."

**Decision (Ajay, 2026-08-03): edge-level is the confirmatory grid. Node-level
is a reported contrast, not a second grid.**

Rationale beyond deference to their prescription: the difference between the two
is itself a researcher degree of freedom with a documented instance. Verbatim
from 2407.08734 section 4, the IOI circuit "is specified as an edge-level
circuit, but Wang et al. (2023) evaluate its faithfulness via a node-wise
ablation methodology". Both are defensible in the published literature, so the
size of the claim shift attributable purely to granularity is a clean secondary
result rather than a robustness footnote.

---

## D9. Hypothesis structure, revised

**Status: resolved 2026-08-03. Supersedes the hypothesis list in the brief.**

2606.06267 establishes, verbatim, that "discovery algorithms sample from an
equivalence class of valid subgraphs rather than recovering a unique mechanism"
and that "structural differences between circuits are not sufficient evidence
for distinct mechanisms".

**Decision (Ajay, 2026-08-03): demote H1 to a measured premise and lead the
paper with the claim-level result.**

| Label | Statement | Role |
|---|---|---|
| **P0** (was H1) | Expected pairwise circuit overlap across specifications is substantially below 1 | **Premise, not a contribution.** Cite 2606.06267, replicate on the analytic-specification axis, report in one figure. |
| **H2** | The derived Annex IV claim flips across a non-trivial fraction of specification pairs | **Primary hypothesis.** Lead with this. |
| **H3** | Claim instability for discovered circuits is not clearly separated from size-matched random circuits | Unchanged. The random-circuit null multiverse is the inferential backbone. |
| **H4** (new) | The gap between structural and functional instability is non-trivial: filings differ where mechanisms do not | From the functional-equivalence arm. This is the sentence that answers 2606.06267 rather than being answered by it. |

Labels H2 and H3 keep their original numbers so that earlier research-log
entries remain readable. P0 and H4 are new labels.

**Consequence for the abstract.** State plainly, in the abstract and not in
section 7, that structural multiplicity is already established, and that the
contribution is what that multiplicity does to a regulatory filing. Reviewers
forgive an owned limitation and punish a hidden one.

---

## D12. The metric axis conflates discovery objective with evaluation metric

**Status: OPEN and blocking. Found 2026-08-03 while encoding the grid.**

**VERIFIED** from auto-circuit 1.0.1 source signatures:

| Function | Objective parameters | Levels |
|---|---|---|
| `acdc_prune_scores` | `faithfulness_target: Literal["kl_div", "mse"]` | 2 |
| `mask_gradient_prune_scores` | `grad_function: Literal["logit","prob","logprob","logit_exp"]` x `answer_function: Literal["avg_diff","avg_val","mse"]` | 12 |
| `edge_attribution_patching_prune_scores` | `answer_diff: bool` | 2 |
| `subnetwork_probing_prune_scores` | none in signature head | - |
| `activation_magnitude_prune_scores` | none | - |
| `random_prune_scores` | none | - (H3 baseline) |

Separately, `auto_circuit/metrics/prune_metrics/prune_metrics.py` holds an
**evaluation** registry: Clean KL Div, Corrupt KL Div, Answer Logit, Wrong
Answer Logit, Answer Prob, Answer Logprob, Logit Diff.

**The problem.** The brief's `m in {sufficiency, comprehensiveness, F1,
logit-difference recovery}` treats these as one axis. They are two.

- A **discovery objective** selects edges. It changes `C(s)`.
- An **evaluation metric** is applied to an already-ranked circuit. It does not
  change `C(s)`.

`phi` maps circuits to claims. Therefore an evaluation metric cannot change
`phi(C(s))`. As currently specified the metric axis would contribute **exactly
zero claim variation** while multiplying the sweep by four. The defect would
have been invisible until after 3,780 runs.

**The exception, and the real decision.** If `tau` is defined **relative to a
metric**, for example "the smallest circuit recovering 90 percent of metric m",
then `(m, tau)` jointly choose the cut point on the prune-score ranking, and `m`
does change `C`. If `tau` is **absolute**, for example "top 200 edges", it does
not. Both conventions appear in the published literature, so this is a genuine
researcher degree of freedom and it must be chosen and pre-registered, not left
implicit.

**Note the upside.** The discovery-objective space is larger and less documented
than the ablation space. `mask_gradient` alone exposes twelve objective
combinations, and MIB (2504.13151, VERIFIED) reports attribution and mask
optimisation methods performing best on circuit localisation, so it is a
mainstream and defensible choice rather than an exotic one. Nobody has crossed
this space. It is a stronger axis than the one the brief specified.

**Decision required before the grid is fixed.** Options are set out for Ajay.
Until this is resolved, `METRICS` in `src/p1/spec.py` and the 3,780 figure are
provisional.

---

## D14. The ablation operator does not reach discovery under ACDC

**Status: OPEN and blocking. Found 2026-08-03 while writing the smoke script.**

**VERIFIED** by grepping `ablation_type` across `auto_circuit/prune_algos/` in
auto-circuit 1.0.1:

| Algorithm | `ablation_type` references | Ablation reaches discovery? |
|---|---|---|
| `mask_gradient` | 3, `ablation_type: AblationType = RESAMPLE` in signature | **Yes** |
| `subnetwork_probing` | 4 | **Yes** |
| `ACDC` | **0** | **No** |
| `edge_attribution_patching` | 0 | No |
| `activation_magnitude`, `ground_truth`, `parameter_integrated_gradients`, `circuit_probing`, `random_edges` | 0 | No |

ACDC hardcodes its internal patching. From `ACDC.py` lines 96 to 97, verbatim:

```
patch_outs_tensor = src_ablations(model, corrupt_batch)
src_outs_tensor  = src_ablations(model, clean_batch)
```

That is corrupt-batch resample ablation, fixed. Separately, `run_circuits` in
`prune.py` does take `ablation_type: AblationType = AblationType.RESAMPLE`, so
the operator enters at **evaluation**.

**The problem.** Under ACDC the seven-operator ablation axis does not change the
prune-score ranking at all. It changes only how a circuit is scored afterwards.
This is the same structural defect as D12, one level up.

**What rescues it, and why D12 now matters more than it looked.** Because `tau`
is metric-relative, the cut point on the ranking is chosen by evaluating the
metric under a given `ablation_type`. So `(a, m, tau)` jointly select `C`, and
the ablation axis stays live even under ACDC. **With absolute `tau`, under ACDC,
both the ablation and metric axes would have been inert and the grid would have
collapsed from 3,780 to 45 distinct circuits.** The D12 decision was load-bearing
for far more than the metric axis.

**The reportable finding hiding in here.** The field treats "choice of ablation"
as one degree of freedom. It is not. Whether it acts on discovery or only on
evaluation depends on which algorithm you run, and no paper says so. That is a
contribution in its own right and it costs nothing extra to report.

**Decision required.** Which discovery algorithm is primary. Options are set out
for Ajay. Note that MIB (2504.13151, VERIFIED) reports attribution and mask
optimisation methods performing best on circuit localisation, which is
independent support for the mask-gradient family.

---

## D15 resolved. Use auto-circuit's eight named algorithms, not a synthetic grid

**VERIFIED 2026-08-04** by parsing `auto_circuit/prune_algos/prune_algos.py`.
auto-circuit ships **eight named `PruneAlgo` constants** built on
`mask_gradient_prune_scores`:

| Constant | Short name | grad | answer | mode |
|---|---|---|---|---|
| `LOGIT_DIFF_GRAD_PRUNE_ALGO` | EAP | logit | avg_diff | mask_val=0.0 |
| `PROB_GRAD_PRUNE_ALGO` | EAP (Prob) | prob | avg_val | mask_val=0.0 |
| `LOGIT_EXP_GRAD_PRUNE_ALGO` | EAP (Answer Logit) | logit_exp | avg_val | mask_val=0.0 |
| `LOGPROB_GRAD_PRUNE_ALGO` | EAP (Answer Logprob) | logprob | avg_val | mask_val=0.0 |
| `LOGPROB_DIFF_GRAD_PRUNE_ALGO` | EAP (Logprob Diff) | logprob | avg_diff | mask_val=0.0 |
| `LOGIT_MSE_GRAD_PRUNE_ALGO` | EAP (MSE) | logit | mse | mask_val=0.0 |
| `INTEGRATED_EDGE_GRADS_PRUNE_ALGO` | IEG (Answer Logit) | logit | avg_val | IG samples=50 |
| `INTEGRATED_EDGE_GRADS_LOGIT_DIFF_PRUNE_ALGO` | IEG | logit | avg_diff | IG samples=1000 |

**Recommendation: the discovery-objective axis is these eight, not a synthetic
4 x 3 = 12 crossing of `grad_function` and `answer_function`.**

Three reasons.

1. **The inclusion criterion is satisfied by construction.** The brief requires
   citing a published implementation for every level of every axis. These eight
   *are* the published implementation: named, shipped, and used by the
   instrument's own authors. A synthetic crossing would include combinations
   nobody has ever run, which a reviewer would rightly call arbitrary.
2. **It is the verbatim-instrument rule applied to the discovery axis.** Same
   principle that forced `load_tl_model` over a hand-rolled copy.
3. **It captures a degree of freedom the synthetic grid would miss.** The EAP
   versus IEG split is not a `grad_function` value at all: it is the
   `mask_val` / `integrated_grad_samples` XOR, and IEG appears at **50 and 1000
   samples**, the same algorithm at two costs. arXiv:2510.00845, the
   second-closest prior work, is a variance analysis of EAP-IG specifically, so
   this axis is live in the literature.

**Cost note.** IEG at 1000 samples is roughly 1000 forward/backward passes
against 1 for EAP. If all eight enter the grid, the two IEG levels will dominate
the sweep budget. Gate 2 should measure EAP and IEG separately before the
pre-registration fixes the level set.

**Also VERIFIED:** `mask_gradient.py` line 62 asserts
`(mask_val is not None) XOR (integrated_grad_samples is not None)`. Exactly one
must be set; passing neither raises a bare `AssertionError` with no message.

---

## D4 resolved. The interchange protocol, and what P1 can and cannot reuse

Source: `UKPLab/arxiv2026-phantom-specialization`, Apache 2.0, cloned to
`.external/phantom-spec` (gitignored). All quotations below are **VERIFIED
verbatim from their code**, 2026-08-04.

### Their protocol, from `05_Phase_Targeted/13_activation_patching.ipynb`

```python
@dataclass
class InterchangePair:
    base_ids: t.Tensor          # (1, seq_len) with BOS prepended
    source_ids: t.Tensor
    base_target_id: int
    source_target_id: int
```

`compute_interchange_metrics(model, pairs, hook_name, position, batch_size=50)`,
decorated `@t.no_grad()`, does exactly four things, quoted from its docstring:

> 1. Cache source activations at hook_name
> 2. Run base input with patched source activations
> 3. Check if prediction matches source target (IIA)
> 4. Compute logit difference: logit[source_target] - logit[base_target]

Mechanically: `model.run_with_cache(s_ids, prepend_bos=False,
names_filter=[hook_name])` to grab the source activation, then
`model.run_with_hooks(b_ids, prepend_bos=False, fwd_hooks=[(hook_name, hook_fn)])`
to run the base with it patched in. Attention is detected by
`is_attn = "hook_z" in hook_name`.

**The headline metric is IIA, interchange intervention accuracy**: the fraction
of pairs where the patched base input now predicts the **source's** target token.
If patching a component's representation makes the model produce the other
condition's answer, that representation carries the causally relevant content.

Constants, verbatim: `N_PAIRS = 100` per condition, `EVAL_SEED = 123`,
`batch_size = 50`, pairs drawn by `np.random.default_rng(seed).permutation`.

### The distinction P1 must state plainly

**P1 cannot reproduce this protocol verbatim, because the thing being varied is
different.** They vary **input statistics** with the task and the analysis held
fixed, and ask whether representations are interchangeable across frequency
bands. P1 varies **analytic specification** with the input held fixed, and asks
whether two circuits recovered under different defensible settings are
functionally equivalent.

The IIA machinery transfers directly. The pairing logic does not: their pairs are
(base example, source example) across bands, whereas P1's comparison is between
two circuits over the same examples.

**This must be reported as an adaptation, not a reproduction.** Claiming verbatim
reproduction here would be false, and the distinction is exactly the sort of thing
the instrument-verbatim rule exists to keep honest. Cite their protocol, state the
adaptation, and justify it.

### The cheaper measure P1 should also take

`05_Phase_Targeted/per_example_agreement.py` supplies a second, far cheaper
functional-equivalence measure that needs no patching at all:

```python
def agreement_rate(preds_a, preds_b):    # fraction of examples where both agree
def cohens_kappa(preds_a, preds_b):      # chance-corrected agreement
```

Two circuits are compared by their per-example correct/incorrect verdicts.
**Cohen's kappa matters here**: raw agreement is inflated when both circuits are
mostly correct, which they will be. Report both.

This is attractive for P1 because it is computable from the
`run_circuits` output already produced by the sweep, at no extra forward passes.
**Recommendation: run agreement and kappa across the full grid, and reserve the
expensive IIA interchange arm for a pre-registered subset of low-Jaccard pairs.**

### The random-Jaccard closed form, now adopted and implemented

From `05_Phase_Targeted/jaccard_calibration.py`, verbatim:

```python
j_rand = k / (2 * N - k)
```

with `k = mean_circuit_edges`, `N = total_possible_edges`. Implemented as
`p1.multiverse.expected_random_jaccard`, with a test checking it against Monte
Carlo simulation to within 0.02 and pinning the boundary cases. Using their
formula keeps P1's random reference commensurable with the paper it answers.

**It is a ratio of expectations, not an expectation of a ratio**, so it is an
approximation and a reference line only. It does **not** replace the sampled
random-circuit null multiverse that H3 is actually tested against.

### Their calibration, and what it implies for H3

Verbatim from the same file:

> "Observed Jaccard is 4-27x higher than random -> circuits share far more edges
> than chance"

> "Within-between gap is 2-5% of observed Jaccard -> modest relative to shared
> structure"

Applying their formula at P1's own measured scale, GPT-2 small with **32,491
edges** from the Gate 2 run:

| circuit size | `J_rand` |
|---|---|
| 100 edges | 0.0015 |
| 500 edges | 0.0078 |
| 2,000 edges | 0.0318 |
| 5,000 edges | 0.0834 |

**Any observed Jaccard above about one percent is already far above chance.**

**Consequence, and it is a warning.** At the structural level the random null is
almost certainly clearly separated, so **H3 should be expected to fail if stated
about circuit overlap.** H3 is stated about the **claim**, and that is not an
accident of phrasing but the substance of the hypothesis: circuits can be
statistically far from random while the *claims derived from them* are not.
Keep the two levels rigorously distinct in the manuscript, and say in advance
that structural separation from the null is expected.
