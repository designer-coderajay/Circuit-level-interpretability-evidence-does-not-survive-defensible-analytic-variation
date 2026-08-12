# P1 pre-registration: second-model replication on Pythia-160m

Written 2026-08-12. **Locked before any discovery cell runs**, per rule 6.

This is a sibling to `PLAN.md`, not a replacement. `PLAN.md` and its
`prereg-p1-confirmatory` tag are untouched. Where this document is silent, the
confirmatory plan governs.

Read `RESEARCH_LOG.md` from the 2026-08-12 entry for the transfer probe and
Gate P, whose results are inputs to this plan and are stated here as such.

---

## 0. Why this exists

The confirmatory paper measures one model on one task and says so in its
abstract. That is the objection a reviewer will raise first and it is the one
the paper cannot answer from its own data.

This plan does not ask a new question. It asks the confirmatory question again on
a second model, and it is designed so that either answer is reportable.

---

## 1. What is already known, and what it is not

Three facts are established before this plan is written. They are stated so that
nothing below can be presented later as though it were discovered by the
replication.

| | result | epistemic state |
|---|---|---|
| Edge namespace | Pythia-160m has 32,347 edges against GPT-2 small's 32,491. Deficit is `n_blocks * n_heads`, all of form `A{b}.{h}->MLP {b}`, because GPT-NeoX reads the residual stream once for attention and MLP together | **VERIFIED** 2026-08-12, `auto-circuit` 1.0.1 |
| Tokenizer | No IOI name in `p1.prompts.EXAMPLE_NAMES` splits into multiple tokens | **VERIFIED** 2026-08-12 |
| Task performance | Gate P passed: IO preferred on 0.961 of 128 clean ABBA prompts, mean logit difference +3.5158 against GPT-2 small's +3.0061 on the same prompts, a ratio of 1.1696 | **VERIFIED** 2026-08-12 |

**Gate P establishes that Pythia-160m performs IOI. It establishes nothing about
whether it does so with an IOI-like circuit.** This plan measures specification
instability on a second model. It does not measure mechanism equivalence across
models, and no sentence in the resulting paper may imply that it does.

The component population is unchanged at `12 * 12 + 12 = 156`, so `phi` is the
same deterministic code operating on the same space. **The claim map is not a
second instrument.** That is the single fact that makes this a replication rather
than a new study.

---

## 2. The question

Does the finding that a derived Annex IV claim is unstable across defensible
analytic specifications hold on a second model of a different architecture
family?

---

## 3. Grid

Every axis level is identical to `PLAN.md` section 4 except `seed` and `model`.
Nothing is added. Nothing is redefined.

| axis | levels | count | note |
|---|---|---|---|
| `discovery_objective` | as `configs/sweep.yaml` | 7 | includes `LOGIT_MSE_GRAD_PRUNE_ALGO`, see 3.2 |
| `ablation` x `corruption` | nested, as `configs/sweep.yaml` | 22 | corruption nested within ablation, not crossed |
| `prompt_variant` | ABBA, BABA | 2 | |
| `seed` | 0, 1, 2 | **3** | **reduced from 5, see 3.1** |
| **discovery cells** | | **924** | 7 x 22 x 2 x 3 |
| `metric` | logit_diff, kl_div, sufficiency, comprehensiveness | 4 | applied post hoc, no GPU cost |
| `threshold` | 0.05, 0.10, 0.20 | 3 | applied post hoc, no GPU cost |
| `granularity` | edge | 1 | node-level is a reported contrast, as before |
| **specifications** | | **11,088 nominal** | 924 x 12 |

Expected working cells 792, expected specifications 9,504, both **arithmetic, not
prediction**, on the basis that the `LOGIT_MSE` arm contributes 132 cells that are
expected to fail.

### 3.1 Why seeds and not another axis

The reduction had to come from somewhere: the full grid is about 26 hours at
GPT-2 costs and this is the second multi-day run this week.

Seed is the only axis whose depth can be reduced without changing what `F` means.
Reducing any axis to a single level removes it from the specification space, and
`F` computed over six axes is not comparable to `F` computed over seven. Three
levels keeps the axis and keeps a seed variance component estimable, though with
less precision than five.

**What this costs, stated plainly.** The seed variance component from this run
will be noisier than the confirmatory one and must be reported with that caveat
attached. It is a secondary quantity and is not the primary outcome.

**What was considered and rejected.** Dropping `INTEGRATED_EDGE_GRADS` would save
47 percent of the runtime for one of seven objective levels, because IEG-50 costs
about 199 s per cell against EAP's 45 s. It is also the only non-EAP method in the
grid. Removing it would make the objective axis six variants of one attribution
family, which is precisely the axis the paper's argument leans on. Rejected.

**Seed semantics, restated because it is easy to misread.** The seed selects
which prompts are sampled. It is evaluation-set variability, not
nondeterminism. The paper says so already and the replication does not change it.

### 3.2 Why `LOGIT_MSE` is included despite not executing

On GPT-2 small this arm did not execute at all and 220 of 1,540 cells were
discarded. It fails fast, so including it costs an estimated 132 x 3 s, under
seven minutes.

Running it on a second model distinguishes a library-level failure from a
model-level one. If it fails identically on Pythia-160m, the paper's observation
about instrument maturity is a two-model observation instead of an anecdote. If
it executes on Pythia-160m, that is more interesting still and is reported.

**Pre-committed either way.** The discard rate is reported per axis level, and
the discarded cells are excluded from `F` exactly as in the confirmatory run.

### 3.3 Dataset size: inherited, not re-calibrated

`n_prompts: 256`, `batch_size: 8`, 128 discovery prompts. Identical to the
confirmatory run.

This value was selected for GPT-2 small by the committed calibration rule in
`CALIBRATION.md`. **It is inherited here rather than re-derived, and that is a
deviation, not a neutral choice.** Re-running calibration on Pythia-160m would
cost a session and would make the two runs differ on a second dimension, which
would confound a difference in `F` with a difference in evaluation-set size.
Holding it fixed is the choice that keeps the comparison interpretable.

Recorded in `DEVIATIONS.md` at lock time. If the claim yield diverges sharply
from the confirmatory 47.7 percent, the inherited size is the first suspect and
is named as such in section 8.

---

## 4. Primary outcome

**Exactly one, and it is the same quantity as the confirmatory run.**

`F_pythia`, the pairwise flip rate of `phi_overseer` at MEDIUM granularity over
the grid in section 3.

    F = 1 - [ sum_c n_c (n_c - 1) ] / [ N (N - 1) ]

Same implementation, `p1.multiverse.flip_rate`. Same unit tests. No new code
enters the outcome path.

**Secondary, all explicitly secondary:** `F` for `phi_affected`; `F` at COARSE and
FINE; `pi_star` and filability at `alpha` in {0.05, 0.10, 0.20}; `J_bar` and the
pairwise `D` distribution; agreement rate and Cohen's kappa; discard rate per axis
level; variance components by axis; the within-size decomposition of every pooled
figure.

**The within-size decomposition is not optional.** Circuit size is an outcome of
the `tau` rule rather than an axis, and on GPT-2 it distorted three separate
pooled quantities including the sign of one. Every pooled figure from this run is
reported with its within-size counterpart or it is not reported.

---

## 5. What counts as replication. Fixed now

This is the part that must be written before the data are seen, because it is the
part that is easiest to rationalise afterwards.

### 5.1 Primary criterion: the regulatory conclusion transfers

**Replicated** if all three hold:

1. `F_pythia > 0.20` with the 95 percent bootstrap CI lower bound above 0.20.
   This is H2's threshold from `PLAN.md`, unchanged, and it is a judgement call
   there and here.
2. Filability fails at all three tolerances, that is `pi_star_pythia < 0.80`.
3. The conclusion is not granularity-dependent in a way that reverses it: 1 and 2
   hold at COARSE and MEDIUM both.

**Not replicated** if any fails. That outcome is reported as a finding about
model dependence, not buried.

### 5.2 Secondary, descriptive only: how close are the two numbers

`|F_pythia - F_gpt2|` and whether the two bootstrap intervals overlap, reported
as a comparison of two distributions.

**This is not a hypothesis test and no p-value is computed for it.** Both numbers
come from designed grids, not from samples of a population, and the grids are not
independent of each other: they share the claim map, the task, the prompt
templates and six of seven axes. An interval overlap here is a description of two
estimates, not evidence about a difference. Rule 3.

Reference value, fixed and quoted from committed results:
`F_gpt2 = 0.7316`, 95 percent CI [0.7247, 0.7380]; `pi_star_gpt2 = 0.4109`.

### 5.3 What would make the comparison uninterpretable

Named now so that it is a pre-specified caveat rather than a post hoc excuse.

- **Claim yield collapses.** If working specifications producing a claim fall
  below 20 percent, against the confirmatory 47.7 percent, the `tau` rule is not
  admitting circuits on this model and `F` is computed over a small and
  self-selected subset. Report the yield prominently and treat `F` as provisional.
- **Class count differs sharply.** `F <= 1 - 1/k` for `k` claim classes. If
  Pythia produces materially fewer classes than GPT-2's nine, the ceiling moves
  and the raw `F` values are not on the same scale. **Report `F` as a fraction of
  its ceiling alongside the raw value in every case, not only if this triggers.**
- **Discovery fails broadly.** If any objective beyond `LOGIT_MSE` fails to
  execute, the grid is not the grid that was pre-registered. Report which, and the
  rate, before reporting `F`.

---

## 6. Statistical treatment

Identical to `PLAN.md` section 6. Restated only where the second model changes
something.

- **No p-value across specifications.** `N = 11,088` is a grid size and does not
  enter any inferential statement. This applies to the replication comparison in
  5.2 as well.
- **Bootstrap resamples specifications, never pairs.** `B = 10,000`, seed 0.
- **Null multiverse uses the parallel namespace.**
  `EdgeComponentIndex(parallel_mlp=True)`, 32,347 edges. Drawing the null from
  GPT-2's 32,491 would put 144 edges in the null that no Pythia circuit could
  contain. Committed at `0cd6856` with a test.
- **Analytic random-Jaccard line** `J_rand = k / (2N - k)` uses `N = 32,347`.
- **Variance components.** REML primary, unbalanced design, as before. The seed
  component is estimated from three levels and is reported with that stated.

---

## 7. Both abstracts, drafted before running

**If the replication holds.** We repeat the specification multiverse on
Pythia-160m, a model of a different architecture family that performs the same
task, holding the claim map, the task and six of seven axes fixed. The derived
Annex IV claim flips across [F_pythia] of specification pairs and the modal claim
commands [pi_star_pythia] of the space, against [F_gpt2] and [pi_star_gpt2] on
GPT-2 small. Filed interpretability evidence fails the filability criterion on
both models at every tolerance tested. The instability is therefore not a
property of one model.

**If the replication fails.** On Pythia-160m the derived claim flips across only
[F_pythia] of specification pairs and the modal claim commands
[pi_star_pythia], satisfying the filability criterion at tolerance [alpha] where
the same grid on GPT-2 small fails it at every tolerance. **Circuit-level
explanation multiplicity is therefore model-dependent**, which narrows the
regulatory concern rather than dissolving it: a conformity procedure cannot know
in advance which model it is dealing with, so the criterion is still needed, and
we report which axis carries the difference so that the mechanism of the
divergence is visible rather than asserted.

**Both are publishable, and the second is the more interesting paper.** If only
one were writeable, the design would be wrong.

---

## 8. Kill criteria. Binding

- **Gate P.** Already passed. Had it failed, this plan would not exist and the
  attempt would have been reported.
- **Budget overrun.** The 15.7 h estimate is INFERRED from GPT-2 per-cell costs
  and the plan's own finding that cost is bound by kernel launch and Python
  overhead rather than parameter count.

  **The first cells of the run are the timing measurement.** Resume is per cell,
  so a separate timing run would discard work for no gain, and the manifests
  record `timings_s` per cell regardless. The check is made against wall clock and
  cell count, not against any claim output.

  **Checkpoint 1**, after the first 20 cells, all EAP: if the extrapolated total
  exceeds 23.5 h, that is 1.5x the estimate, stop and cut seeds from three to
  two. That is the pre-registered fractional rule here. **No ad hoc pruning of any
  other axis, and no reduction below two seeds.**

  **Checkpoint 2**, on reaching the first `INTEGRATED_EDGE_GRADS` cells, which run
  last in config order: re-extrapolate, because IEG-50 is about 4.4x an EAP cell
  on GPT-2 and that ratio is assumed, not measured, on this model. The same 1.5x
  rule applies. Cutting at this point discards the third seed's cells and keeps
  seeds 0 and 1 complete, which the grid ordering permits.

  Either cut is recorded in `DEVIATIONS.md` with the measured rate that triggered
  it.
- **Broad discovery failure.** More than two objectives failing to execute means
  the harness has not transferred and the run stops. Report as attempted.
- **Granularity divergence.** If COARSE and MEDIUM give opposite answers on 5.1,
  report that the conclusion is granularity-dependent on this model. That is a
  finding, not a failure, and it is also a finding about the claim map that
  belongs in the paper's limitations.

---

## 9. What would falsify the paper's claim

`F_pythia` near zero with `pi_star_pythia` near one at both COARSE and MEDIUM,
for both addressees, with the random null clearly separated.

That would show that the GPT-2 result is an artefact of one model and that
circuit-level evidence can be stable under analytic variation. The paper would
then report explanation multiplicity as model-dependent and would have to retitle.

---

## 10. Locking

- This file is committed with a timestamp before any discovery cell runs.
- Tag `prereg-p1-replication`.
- `configs/replication_pythia.yaml` is committed in the same commit. No parameter
  in it may change afterwards without a `DEVIATIONS.md` entry.
- **No discovery cell runs before this commit.** The run starts after it, and the
  budget checkpoints in section 8 read wall clock and cell count only.
- Pooled analysis happens once the grid is complete. `F`, `pi_star`, `J_bar` and
  the agreement figures are not computed on a partial grid, because a partial
  grid is ordered by objective and a partial `F` would be an `F` over a
  non-random subset of the objective axis.

## 11. Disclosure: what was seen before this lock

Stated so it cannot be presented later as a discovery.

**Run before the lock:** the transfer probe, 2 CPU forward-graph constructions;
Gate P, 256 CPU forward passes on 128 prompts across two models. No circuit
discovery. No ablation. No claim map evaluation. No `F`, `pi_star`, `J_bar` or
agreement figure exists for Pythia-160m at lock time.

**Inspected:** edge count, block and head counts, tokenizer behaviour on ten
names, and the two logit-difference summaries in section 1.

**Changed as a result:** `enumerate_edges` gained a `parallel_mlp` flag;
`EdgeComponentIndex` gained the same flag; two tests were added. All additive,
all defaulting to the GPT-2 behaviour, none touching `auto-circuit`, none in the
outcome path.

**Not changed as a result:** the grid, the claim map, the primary outcome, the
thresholds in section 5, the statistical treatment.
