# P1 pre-registration: analysis plan

**Status: DRAFT. Not locked.** This document is not a pre-registration until it
is committed, tagged, and the tag pushed to a public remote, with the hash and
UTC timestamp recorded in `RESEARCH_LOG.md`. See "Locking" at the end.

**No pooled result from the confirmatory grid has been inspected.** The only
execution to date is the Gate 2 smoke configuration, which is a timing
measurement on 32 prompts, is marked in `configs/smoke.yaml` as excluded from
any confirmatory analysis, and produced no claim, flip rate, or overlap figure.

Items marked **[CONFIRM]** need Ajay's explicit sign-off before locking.

---

## 1. Question

Circuit discovery samples from an equivalence class of valid subgraphs
(arXiv:2606.06267). The EU AI Act requires a provider to file a description of
the technical measures that facilitate interpretation of a high-risk system's
outputs (Annex IV 2(e) and 3, Article 13(3)(d)), which a human overseer must be
able to use to "correctly interpret" an output (Article 14(4)(c)), and which
ultimately backs an affected person's right to a "clear and meaningful"
explanation of a decision about them (Article 86(1)).

**If the filed description changes when a different competent analyst runs the
same tool with different defensible settings, the filing does not support the
conformity claim made on it.** This plan measures how far that description moves
across the space of defensible analytic specifications, and whether the movement
exceeds a size-matched random baseline.

## 2. Hypotheses

Labels P0 and H4 are new; H2 and H3 retain their original numbers so earlier
research-log entries remain readable. See `docs/DESIGN-DELTAS.md` D9.

| | Statement | Decision quantity | Threshold |
|---|---|---|---|
| **P0** | Expected pairwise circuit overlap across specifications is below 1 | `J_bar` with 95% bootstrap CI | **Premise, not tested.** Reported for calibration and cited to 2606.06267. |
| **H2** *(primary)* | The derived Annex IV claim flips across a non-trivial fraction of specification pairs | `F` = pairwise flip rate | `F > 0.20` **[CONFIRM]**, with the 95% bootstrap CI lower bound above 0.20 |
| **H3** | Claim instability for discovered circuits is not clearly separated from size-matched random circuits | overlap of the `F` distributions, discovered versus random null multiverse | **not separated** if the 95% CIs overlap; **separated** if the discovered median lies outside the random 95% CI |
| **H4** | Filings differ where mechanisms do not | gap between structural and functional instability | `F − (1 − agreement_rate) > 0.10` **[CONFIRM]** |

**Expected outcome to state now, before seeing results.** At the *circuit* level
the random null is almost certainly clearly separated: 2606.06267 report observed
Jaccard 4 to 27 times random, and at P1's measured 32,491 edges a 500-edge
circuit has `J_rand = 0.008`, so any observed overlap above roughly one percent
already exceeds chance. **H3 is stated about the claim and not about circuit
overlap, and that distinction is the substance of the hypothesis.** If H3 is
tested at the circuit level it will fail, and that failure would not bear on the
regulatory argument.

## 3. Primary outcome

**Exactly one.** `F`, the pairwise flip rate of `phi_overseer` at MEDIUM
granularity, over the confirmatory grid.

    F = 1 - [ sum_c n_c (n_c - 1) ] / [ N (N - 1) ]

where `n_c` counts specifications yielding claim class `c` and `N` is the number
of specifications. Implemented as `p1.multiverse.flip_rate`; the identity is
unit-tested against the O(N^2) pairwise definition over 2,000 randomised cases
and cross-checked against the Gini-Simpson form.

**Secondary, all explicitly secondary:** `F` for `phi_affected`; `F` at COARSE
and FINE for both maps; `pi_star` and filability at `alpha` in {0.05, 0.10,
0.20}; `J_bar` and the full distribution of pairwise `D`; agreement rate and
Cohen's kappa; IIA on the interchange subset; variance components by axis.

## 4. Specification space

Confirmatory grid, edge-level, fully crossed:

| Axis | Levels | n |
|---|---|---|
| discovery objective | 6 EAP variants + IEG-50, from auto-circuit's named `PruneAlgo` constants | 7 |
| ablation operator | all seven `auto_circuit.types.AblationType` members | 7 |
| corruption distribution | **[CONFIRM]** levels not yet fixed | 3 |
| evaluation metric | logit_diff, kl_div, sufficiency, comprehensiveness | 4 |
| threshold `tau` | **[CONFIRM]** levels not yet fixed | 3 |
| prompt variant | **[CONFIRM]** levels not yet fixed | 3 |
| seed | 0, 1, 2, 3, 4 | 5 |

**Total 26,460 specifications**, obtained from 2,205 prune-score rankings, since
`tau` is metric-relative and the `(metric, tau)` cut is post-hoc on an existing
ranking.

**`tau` is metric-relative**, defined verbatim as: *the smallest circuit
recovering `(1 − tau)` of metric `m` measured on the full model.* Absolute `tau`
(a fixed edge count) is equally defensible and appears in the literature. The
choice is recorded because it is load-bearing: under absolute `tau` with ACDC,
both the ablation and metric axes would carry zero claim variance.

**Reduced arm, pre-registered here and not later.** IEG-1000 runs on a seed-only
slice: one ablation operator, one corruption, one prompt variant, five seeds,
five discoveries. Fully crossing it would cost roughly 814 CPU-hours against
about 13 for the slice. The slice tests whether IG sample count changes the
claim; it is reported separately and never pooled with the confirmatory grid.

**Contrast arms, reported separately, never pooled:** node-level granularity;
ACDC as an alternative discovery algorithm.

## 5. Claim maps

Two addressees, three nested granularities each, six deterministic maps.
`p1.claim_map`, pure functions, no model and no language model anywhere in the
path.

- `phi_overseer` targets Annex IV 2(e) and 3 read with Article 14(4)(c).
- `phi_affected` targets Article 86(1).

**Nesting is structural**, not asserted: each granularity appends a field to a
tuple key, so FINE refines MEDIUM refines COARSE. Unit-tested over randomised
circuits for both maps. This is the answer to "you chose granularities that gave
the flip rate you wanted".

**Frozen at lock:** `DEFAULT_SIZE_BINS`, `DEFAULT_BAND_NAMES`, and the per-task
input segment labels used as `position_mass` keys **[CONFIRM]**, all currently
marked PROVISIONAL in code.

## 6. Statistical treatment

**No p-value is computed across specifications anywhere.** Specifications are a
designed grid, not an independent sample. `N = 26,460` is a grid size and will
not appear in any inferential statement.

- **Uncertainty.** Nonparametric bootstrap **resampling specifications, never
  pairs**, `B = 10,000`, seed 0. `J_bar` and `F` are U-statistics over pairs;
  pairs share specifications, so resampling pairs understates variance. A test
  asserts the resampling unit structurally. Intervals quantify uncertainty
  **given the grid** and do not license inference beyond it.
- **Joint inference.** The size-matched random-circuit null multiverse, pushed
  through the identical pipeline and the identical claim maps. Compare full
  distributions of `F`, `J_bar`, `pi_star`. Analytic reference line
  `J_rand = k / (2N − k)`, adopted from 2606.06267's own calibration script.
- **Variance decomposition.** Crossed random-effects model, one component per
  axis, EMS estimator on the balanced grid with REML as robustness. Negative
  components reported raw and truncated, never silently truncated.
- **Seed variance reported separately** from analytic-choice variance. The ratio
  is a headline number.
- **Figure 1** is the specification curve: effects sorted ascending with a
  bootstrap band, a dot matrix of active choices below, and the null multiverse
  overlaid rather than described.

## 7. Exclusions

Fixed in advance. **Discard means discard.** No failing item is repaired.

A run is discarded if: discovery raises; `run_circuits` raises; the metric-relative
`tau` rule admits no circuit within the tested edge counts; or peak memory
exceeds the device. **The discard rate is reported per axis level.** A manifest
with `status: "discarded"` is written for every discard, so the rate is
computable from `results/` rather than remembered.

## 8. Both abstracts, drafted before running

**If H2 holds.** We measure how far a filed EU AI Act Annex IV interpretability
claim moves across defensible analytic specifications. Across 26,460
specifications built from published implementations, the claim derived from a
discovered circuit flips across [F] of specification pairs, and the modal claim
commands only [pi_star] of the space. Filed interpretability evidence therefore
fails a filability criterion at any tolerance a conformity assessment body would
plausibly accept. Because Article 86 places the explanation duty on a deployer
who can only pass on what the provider supplied, an analytic choice made once
inside the provider propagates to an individual's right to an explanation of a
decision about them.

**If H2 fails.** Across 26,460 specifications the claim derived from a discovered
circuit flips across only [F] of pairs, and the modal claim commands [pi_star].
Circuit-level interpretability evidence is therefore substantially more stable
under analytic variation than the non-identifiability literature would predict,
and it satisfies a filability criterion at tolerance [alpha]. We give the
criterion as a standalone protocol so that a standards body can apply it, and we
report which analytic axis carries the residual variance so that it can be
standardised first.

**Both are publishable.** If only one were, the design would be wrong.

## 9. Kill criteria

- Prior work already propagates instability to a downstream regulatory claim:
  drop or reframe. **Checked 2026-08-04, not triggered.**
- Grid cannot complete in the window at measured cost: cut by the pre-registered
  fractional rule, never by ad hoc pruning.
- `phi` granularities give qualitatively different conclusions: report that the
  conclusion is granularity-dependent. That is a finding, not a failure.

## 10. What would falsify the claim

`F` near zero with `pi_star` near one at all three granularities, for both
addressees, with the random null clearly separated. That would show filed
interpretability evidence is stable under analytic variation and the regulatory
concern is unfounded.

## 11. Locking

    git add preregistration/
    git commit -m "prereg: lock analysis plan for P1 confirmatory grid"
    git rev-parse HEAD
    date -u +"%Y-%m-%dT%H:%M:%SZ"
    git tag -a prereg-p1-confirmatory -m "locked <timestamp>"
    git push origin prereg-p1-confirmatory

Then file the embargoed OSF registration for a third-party timestamp and DOI,
and record hash, timestamp, and DOI in `RESEARCH_LOG.md`.

`preregistration/DEVIATIONS.md` is append-only from the moment of locking.

## 12. Before locking, checklist

- [ ] Every **[CONFIRM]** resolved: H2 and H4 thresholds; corruption, `tau`, and
      prompt-variant levels; `phi` size bins, band names, and segment labels
- [ ] Environment pinned and hash recorded (`requirements-sweep.lock.txt`)
- [ ] Private GitHub remote exists and history is pushed
- [ ] No pooled confirmatory result seen by anyone
- [ ] Both abstracts drafted — done, section 8
