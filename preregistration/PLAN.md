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
| **H2** *(primary)* | The derived Annex IV claim flips across a non-trivial fraction of specification pairs | `F` = pairwise flip rate | `F > 0.20`, with the 95% bootstrap CI lower bound above 0.20. **Confirmed by Ajay 2026-08-05.** |
| **H3** | Claim instability for discovered circuits is not clearly separated from size-matched random circuits | overlap of the `F` distributions, discovered versus random null multiverse | **not separated** if the 95% CIs overlap; **separated** if the discovered median lies outside the random 95% CI |
| **H4** | Filings differ where mechanisms do not | gap between structural and functional instability | `F − (1 − agreement_rate) > 0.10` **[CONFIRM]** |

**The 0.20 threshold on H2 is a judgement call and the paper must defend it as
one.** It is not derived from anything. The defensible reading is that one flip
in five specification pairs means two competent analysts filing the same system
disagree often enough that the filing cannot be relied on by a third party. A
reviewer is entitled to disagree with the number; the pre-registration's job is
to fix it before the data are seen, not to make it principled. `F` is reported
with its full bootstrap distribution regardless of which side of 0.20 it lands
on, and the filability criterion at three tolerances is reported alongside it so
the conclusion does not rest on a single cut point.

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

Confirmatory grid, edge-level. Crossed except for the corruption axis, which is
nested within the ablation operator for the reason given below.

| Axis | Levels | n |
|---|---|---|
| discovery objective | 6 EAP variants + IEG-50, from auto-circuit's named `PruneAlgo` constants | 7 |
| ablation operator | all seven `auto_circuit.types.AblationType` members | 7 |
| corruption distribution | **nested within ablation**: 4 levels for the 5 corruption-dependent operators, 1 for the other 2 | 4 / 1 |
| evaluation metric | logit_diff, kl_div, sufficiency, comprehensiveness | 4 |
| threshold `tau` | **[CONFIRM]** levels not yet fixed | 3 |
| prompt variant | ABBA, BABA, both verbatim in 2407.08734 section 4 | 2 |
| seed | 0, 1, 2, 3, 4 | 5 |

**Corruption is nested, not crossed. Decision by Ajay, 2026-08-05.** VERIFIED
from `auto_circuit/utils/ablation_activations.py`: `ZERO` zeros the source output
regardless of input and forces `input_batch = batch.clean`, and
`TOKENWISE_MEAN_CLEAN` reads the clean dataset only. Crossing those two operators
against three corruption levels produces three identical specifications. Under
the previous fully crossed design that was 5,040 exact duplicates, 19% of the
grid. A multiverse whose specifications are not distinct specifications
misrepresents itself, and the specification curve would plot three identical
points where one specification exists. The degeneracy is reported in the paper as
a small finding about the instrument. See DESIGN-DELTAS D18.

Ablation-by-corruption cells: `5 x 4 + 2 x 1 = 22`.

**The four corruption levels, fixed 2026-08-06.** All four are transcribed from
arXiv:2211.00593, VERIFIED by fetching the PDF, so each level cites a published
construction rather than being invented to fill an axis.

| Level | Source | Verbatim |
|---|---|---|
| `ABC` | section 3 | "instead of using two names (IO and S) it used three unrelated random names (A, B and C). In pABC, sentences no longer have a single plausible IO, but the grammatical structures from the pIOI templates are preserved." |
| `RANDOM_NAME_FLIP` | appendix A | "we replace the names from a given sentence with random names, but we keep the same position for all names. Moreover, each occurrence of a name in the original sentence is replaced by the same random name." |
| `IO_S1_FLIP` | appendix A | "we swap the position of IO and S1. The output of S-inhibition heads will contain correct token signals ... but inverted positional signals" |
| `IO_FROM_S2` | appendix A | "we make IO become the subject of the sentence and S the indirect object. In this dataset, both token signals and positional signals are inverted." |

`ABC` is the distribution the source uses for all knockouts and is the de facto
default in the circuit-discovery literature. The other three come from appendix A,
where the authors state: "We constructed six datasets by combining three
transformations of the original pIOI distribution."

**The objection this axis invites, and the pre-registered answer.** The same
appendix reports that these transformations carry systematically different
information: logit difference is approximated by `2.31*S_pos + 0.99*S_tok` with
7% mean error. A reviewer will therefore say that a claim shift across
known-different counterfactuals is close to tautological.

**Secondary outcome, pre-registered here.** `F` is additionally reported for the
`ABC` versus `RANDOM_NAME_FLIP` pair alone. Both are "replace the names with
random names" and differ only in whether the duplicate-name structure survives.
An analyst choosing between them would not believe they were making a substantive
choice, so a flip confined to that pair cannot be dismissed as tautological. This
is a post-hoc partition of the same runs and costs no additional compute. It is
fixed now, before any result is seen, precisely so it cannot be introduced later
as a rescue.

`IO_FROM_S2` produces a valid IOI sentence with a different answer rather than a
degraded one. This is mechanically sound: `mask_gradient_prune_scores` scores
`model(batch.clean)` against `batch.answers`, and the corrupt prompt supplies
ablation activations only, so the corrupt prompt's own answer never enters any
metric. It is nonetheless a substantively different kind of counterfactual and is
described as one, not folded in silently.

**`clean_corrupt` is fixed at `"corrupt"`. Decision by Ajay, 2026-08-05.**
VERIFIED from the `mask_gradient_prune_scores` signature, where it is an explicit
parameter defaulting to `"corrupt"`, and from the `batch_src_ablations` assertion
that requires it for `RESAMPLE`, `BATCH_TOKENWISE_MEAN` and `BATCH_ALL_TOK_MEAN`.
It is a real researcher degree of freedom applying to three of seven operators.
P1 does not cross it. It is recorded here as a fixed choice rather than left
implicit, and named in the limitations as an axis the paper did not cross.

**Withdrawn: the mean-ablation dataset-size axis.** It was proposed as a
replacement for the corruption axis on the grounds that 2407.08734 flags the
choice without crossing it. VERIFIED false as implementable:
`mask_gradient_prune_scores` takes a single `dataloader` and passes the same
object to `batch_src_ablations` and to the gradient loop, so the dataset the
ablation mean is computed over and the dataset discovery runs on are the same
object. Varying one varies the other. Separating them requires modifying the
instrument, which is forbidden. The axis is not available and is not in the grid.

**Grid arithmetic.**

    discovery cells   7 objectives x 22 ablation-corruption x 2 prompt x 5 seed
                    = 1,540
    specifications    1,540 x 4 metrics x 3 tau
                    = 18,480

`tau` is metric-relative, so the `(metric, tau)` cut is post-hoc on an existing
ranking and does not require a new discovery. This is the reuse architecture
measured at Gate 2.

History of this figure, so the arithmetic is auditable. The grid was 26,460
specifications from 2,205 discovery cells before the nesting and prompt-variant
decisions of 2026-08-05, which took it to 14,280 from 1,190. Fixing the
corruption axis at four sourced levels on 2026-08-06 raised it to 18,480 from
1,540. Net against the original: 70% of the specifications and 70% of the
discovery cells, with every remaining specification distinct and every axis level
citing a published implementation.

**`n_prompts` = 256 total, 128 discovery. Selected 2026-08-05 by the committed
calibration rule, not chosen.** The seed-agreement curve was
`J_seed` = 0.5678, 0.6386, 0.7428, 0.8089 at `n` = 16, 32, 64, 128, with deltas
+0.0709, +0.1042, +0.0660. No delta fell below the pre-committed 0.05, so the
curve had not flattened and the rule fell back to the largest size tested, which
is also auto-circuit's own default. **The paper states in the abstract that
sampling stability was not reached at the instrument's default dataset size.**
Two runs of the identical specification differing only in prompt sample agree on
81% of a 500-edge circuit, so seed is a comparison arm in this design, not a
nuisance term. Full protocol and the non-monotonicity of the deltas:
`preregistration/CALIBRATION.md`.

**Original statement of the problem, retained:**
It was absent from every earlier draft of this plan, which was an omission: it is
the largest single lever on both the sweep budget and the validity of the
headline seed-variance ratio. VERIFIED 2026-08-05, `auto_circuit.data`
defaults to `train_test_size = (128, 128)`, so the instrument's own default is
128 discovery prompts against the 16 used in the smoke configs. The selection
rule is fixed in `preregistration/CALIBRATION.md`, committed before the pilot
runs. Whatever that rule returns is what goes here, including if it returns a
value the schedule cannot afford.

**Compute, measured.** All figures below are from runs of the committed configs,
not from scaling arguments. Sweep host is **Colab Pro on a Tesla T4**, resolving
DESIGN-DELTAS D5 and D17.

At 128 discovery prompts on a T4, `configs/smoke-ieg-128.yaml` measured IEG-50
discovery at **229.142 s**, evaluation at **1.756 s per cut**, and peak VRAM at
**3,651 MB against the card's 15,360 MB**, so memory is not the binding
constraint and `batch_size` remains free rather than pinned by the hardware.

Card comparison, both configs run unchanged on each device:

| | T4 | L4 |
|---|---|---|
| IEG-50 discovery, 128 prompts | 229.1 s | 172.3 s |
| evaluation per cut | 1.756 s | 1.333 s |
| peak VRAM | 3,651.4 MB | 3,651.4 MB |

**The workload does not scale with GPU class.** The L4 is only 1.33x the T4, and
VRAM is byte-identical. GPT-2 small is 124M parameters and `patchable_model` runs
many small hooked operations per pass, so cost is bound by kernel launch and
Python overhead rather than arithmetic throughput. INFERRED consequence, not
measured: A100 and H100 would give a similar 1.3 to 1.5x at several times the
compute cost. Sweep runs on **L4**.

| | cells | each | total |
|---|---|---|---|
| EAP discovery | 1,320 | ~8.05 s *(inferred)* | 2.95 h |
| IEG-50 discovery | 220 | 172.3 s *(measured)* | 10.53 h |
| evaluation, 10 rungs | 1,540 | 13.3 s *(measured)* | 5.70 h |
| IEG-1000 slice | 5 | ~3,293 s *(inferred)* | 4.57 h |
| **total** | | | **≈ 23.8 h** |

Discovery cost is linear in dataset size, verified: 8× the prompts gave 8.00× the
time. The measured device factor against CPU is about **7×**, not the 20× D17
guessed.

**Resume, because 25.7 h exceeds a Colab session.** Each discovery cell writes
its own manifest and prune-score file keyed by `spec_id`; the runner skips any
cell whose manifest exists with `status: ok`. The results directory is the
checkpoint, so there is no separate state file to corrupt mid-write. Every cell
manifest records `torch.cuda.get_device_name`. **Cells that ran on a device other
than the modal one are discarded and rerun**, and the device distribution is
reported. Per-cell recorded and verified homogeneity is stronger evidence than a
single asserted environment hash, not weaker, and it is the condition on which
running a confirmatory sweep on ephemeral infrastructure is defensible at all.

**`tau` is metric-relative**, defined verbatim as: *the smallest circuit
recovering `(1 − tau)` of metric `m` measured on the full model.* Absolute `tau`
(a fixed edge count) is equally defensible and appears in the literature. The
choice is recorded because it is load-bearing: under absolute `tau` with ACDC,
both the ablation and metric axes would carry zero claim variance.

**How the circuit is located, fixed 2026-08-05.** The definition above was
incomplete in every earlier draft: it named the criterion but not the search.
Different search procedures return different circuits for the same `tau`, and a
different circuit is a different claim, so the procedure is part of the
specification and is fixed here.

`C(s)` is **the smallest rung of the following fixed ladder** at which the
criterion is met, scanning upward:

    EDGE_COUNT_LADDER = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]

Ten rungs, roughly logarithmic, against a full graph of 32,491 edges on GPT-2
small at the confirmatory `patchable_model` settings.

Three properties of this choice, stated so they are not discovered later.

- **It is quantised, and it overshoots.** The located circuit is the smallest
  *rung* meeting the criterion, not the smallest circuit. The metric value at the
  rung below is computed as part of the same sweep and is retained, so the size
  of the overshoot is recoverable at analysis time at zero additional compute.
- **It is sound under non-monotonicity.** Metric recovery is not guaranteed
  monotone in edge count. An upward scan of a fixed ladder takes the first rung
  that meets the criterion regardless, which is well defined either way. Bisection
  was considered and rejected for exactly this reason: it assumes monotonicity it
  cannot rely on, and it costs more evaluations than ten rungs, not fewer.
- **The top rung is deliberately below the full model.** If a specification needs
  more than 10,000 edges, about 31% of the graph, to recover `(1 − tau)` of the
  metric, that is not an explanation, and the run is **discarded** under section 7
  rather than being handed a degenerate whole-model circuit. Including 32,491 as a
  rung would make the criterion trivially satisfiable and would silently convert
  a failure into a meaningless claim. The discard rate is reported per axis level.

**Reduced arm, pre-registered here and not later.** IEG-1000 runs on a seed-only
slice: one ablation operator, one corruption, one prompt variant, five seeds,
five discoveries. The slice tests whether IG sample count changes the claim; it
is reported separately and never pooled with the confirmatory grid. **The cost
ratio quoted in the earlier draft, 814 CPU-hours against 13, rested on the
unmeasured IEG discovery cost and is withdrawn pending the `smoke-ieg`
measurement.** The reduction rule itself is fixed here regardless of what that
measurement returns, so that it cannot be tuned after the fact.

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
designed grid, not an independent sample. `N = 14,280` is a grid size and will
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
- **Variance decomposition.** Random-effects model, one component per axis, with
  corruption nested within ablation. **The design is unbalanced, so REML is the
  primary estimator, not the closed-form EMS estimator the earlier draft
  specified.** This is a direct consequence of the nesting decision and is
  recorded as such. The five corruption-dependent operators form a balanced
  sub-block, and EMS is computed there as an independent cross-check on the REML
  fit; agreement between the two on that block is reported. Negative components
  reported raw and truncated, never silently truncated.
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
claim moves across defensible analytic specifications. Across 14,280
specifications built from published implementations, the claim derived from a
discovered circuit flips across [F] of specification pairs, and the modal claim
commands only [pi_star] of the space. Filed interpretability evidence therefore
fails a filability criterion at any tolerance a conformity assessment body would
plausibly accept. Because Article 86 places the explanation duty on a deployer
who can only pass on what the provider supplied, an analytic choice made once
inside the provider propagates to an individual's right to an explanation of a
decision about them.

**If H2 fails.** Across 14,280 specifications the claim derived from a discovered
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

- [x] H2 decision rule fixed — `F > 0.20`, CI lower bound above it, 2026-08-05
- [x] Corruption axis treatment fixed — nested within ablation, 2026-08-05
- [x] `clean_corrupt` fixed at `"corrupt"` and recorded, 2026-08-05
- [x] Prompt-variant levels fixed — ABBA, BABA, 2026-08-05
- [x] Private GitHub remote exists and history is pushed — `origin/main` at
      `751573f`, 2026-08-05
- [x] IEG-50 discovery cost measured, n = 2, mean 239.574 s, spread 1.5%,
      2026-08-05. 25.8x EAP, not the 51x inferred
- [x] `CALIBRATION.md` rule committed before either pilot runs
- [ ] Remaining **[CONFIRM]**: H4 threshold; the three corruption **levels**
      themselves, each needing a published implementation to cite; `tau` levels;
      `phi` size bins, band names, and segment labels
- [x] `n_prompts` selected by the calibration rule: 256 total, 128 discovery,
      curve reported, 2026-08-05
- [x] GPU factor measured on Tesla T4, ~7x not 20x; D17's guess replaced
- [x] VRAM measured at the selected size, 3,651 of 15,360 MB; T4 is sufficient
      and D5's rented-box decision is withdrawn
- [x] `tau` search procedure fixed: smallest rung of a 10-step edge-count ladder
- [x] Resume design fixed: per-cell manifest, skip if `status: ok`, device
      recorded per cell and homogeneity enforced
- [ ] `src/p1/spec.py` implements the nesting and carries a
      `discovery_objective` field; pinned `spec_id` regression value updated
- [ ] Section 4's IEG-1000 wording corrected: the slice compares two shipped
      configurations, it does **not** isolate IG sample count
- [ ] Environment pinned and hash recorded (`requirements-sweep.lock.txt`)
- [ ] No pooled confirmatory result seen by anyone
- [x] Both abstracts drafted — section 8
