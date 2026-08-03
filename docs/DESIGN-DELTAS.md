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
