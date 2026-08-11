# P1 findings, 2026-08-11

Everything measured, with every caveat that survived attack. This is the source
for the results section. Where a pooled figure and its decomposition disagree,
**both appear here and both go in the paper.**

Nothing below is a summary of a summary. Every number traces to a committed
script, a config, a seed and an environment fingerprint.

---

## What was run

| | |
|---|---|
| grid | 6 discovery objectives x 22 ablation-corruption x 2 prompt variants x 5 seeds |
| discovery cells | 1,320 completed of 1,540 pre-registered |
| specifications | 15,840 pre-registered, **7,561 produced a claim** |
| model, task | GPT-2 small, IOI, 32,491 edges, 156 components |
| environment | one fingerprint across the whole sweep, verified from the archive |
| code | commit `5371629`, recovered by blob-hash, 22 of 22 files identical |

**Two exclusions, both with criteria fixed before any circuit was seen.**

`LOGIT_MSE_GRAD_PRUNE_ALGO` does not execute. All 220 of its cells raise
`RuntimeError: Found dtype Long but expected Float` from `mse_loss` against an
integral target, inside auto-circuit's own `mask_gradient.py`. Verified by digest
that the failure set is exactly that arm. **One of seven documented, publicly
exported discovery objectives cannot be run on the library's own canonical task.**

52.3% of specifications were discarded by the metric-relative `tau` rule, and
non-uniformly: comprehensiveness 0.3%, kl_div 63.0%, logit_diff 67.9%,
sufficiency 77.9%. Disclosed before the lock in PLAN.md 11b. The surviving pool
is 52% comprehensiveness against 25% by design.

---

## The four pre-registered outcomes

### P0. Circuits are almost disjoint. Premise, not tested.

`J_bar = 0.1396` [0.1377, 0.1418], exact over all 28,580,580 specification pairs.

The distribution matters more than the mean. **The median pair of circuits shares
4% of its edges.** Only 1% of pairs reach `J > 0.8`. At the median circuit size of
200 edges the analytic random line gives `J_rand = 0.0031`, so observed overlap is
about 45x chance, inside the 4x to 27x band the prior literature reports.

### H2. Confirmed. The claim flips on three quarters of pairs.

`F = 0.7316` [0.7247, 0.7380], threshold `F > 0.20` with the interval lower bound
above 0.20. The bound is 0.7247.

`pi* = 0.4109`. **Not filable at any pre-registered tolerance**: 0.411 against
requirements of 0.95, 0.90 and 0.80.

The two most common claims, 41.1% and 28.5% of specifications, attribute the same
model's behaviour on the same task to **early layers** and to **late layers**.
They contradict.

All six addressee-granularity cells reject filability. `phi_affected` at COARSE
is a two-class claim, the crudest statement available to an affected person, and
it still flips on **39.5%** of pairs.

### H3. Rejected, and the direction is not what it appears.

Pooled: discovered 0.7316 [0.7247, 0.7380] against a size-matched random null at
0.6774 [0.6734, 0.6810], `R = 1,000`. Intervals disjoint, so separated by the
pre-registered rule.

**The pooled direction is an artefact of the size distribution and the paper says
so.** The null is degenerate above 1,000 edges, where a uniform draw touches all
156 components and can produce only one claim. With size held fixed the ordering
reverses: discovered 0.2746 against null 0.4230 at MEDIUM, 0.2706 against 0.3822
at COARSE.

**Discovered circuits are more stable than random ones once the comparison is
fair.** They carry real information. They are not stable enough to file.

### H4. Supported, and the supporting gap does not survive decomposition.

`F - (1 - agreement_rate) = 0.3344` [0.3297, 0.3394], threshold 0.10.

`agreement_rate = 0.6028`, functional instability 0.3972.

**Cohen's kappa is 0.0146.** The 60% agreement is almost entirely marginal
accuracy, not shared behaviour. Kappa stays between 0.016 and 0.047 at every
circuit size while raw agreement climbs 0.52 to 0.92, tracking accuracy 0.51 to
0.95.

Within size, the gap **fails the 0.10 threshold at 6 of 10 sizes and is negative
at 5**. At both ends of the range the mechanisms differ more than the filings do.
The pooled figure is carried by the 500 to 2,000 edge band alone.

---

## Which analytic choice to standardise, and what it buys

Residual `F` once each axis is standardised. All intervals valid, bias below
0.0006, group sizes 1,512 to 2,520.

| axis standardised | residual `F` | 95% CI | removes |
|---|---|---|---|
| **metric** | **0.5939** | [0.5803, 0.6063] | +0.1377 |
| ablation | 0.7014 | [0.6939, 0.7075] | +0.0302 |
| discovery objective | 0.7018 | [0.6938, 0.7084] | +0.0298 |
| threshold `tau` | 0.7070 | [0.6981, 0.7149] | +0.0246 |
| corruption | 0.7092 | [0.7008, 0.7166] | +0.0224 |
| prompt variant | 0.7232 | [0.7157, 0.7300] | +0.0084 |
| seed | 0.7307 | [0.7234, 0.7368] | +0.0009 |

**The evaluation metric is the largest single lever and it is not enough.**
Standardising it completely, more than a standards body could demand, leaves
`F = 0.594`, three times the threshold. No axis rescues filability.

**Structure and claim are governed by different axes.** REML on `log10(selected
edges)` attributes 78.8% of structural variance to the ablation-corruption
interaction and **0.7% to the metric**, which is the largest driver of claim
variance. A standards body reading the structural decomposition would standardise
the ablation operator and fix almost none of the filing instability.

---

## The result under maximum pressure

Strip every trace of circuit size from the claim, `phi_overseer` at COARSE is
`layer_band` alone, and hold size fixed:

**`F = 0.2706` [0.2550, 0.2859].**

The interval lower bound is 0.2550, above the pre-registered 0.20. Where in the
model the behaviour is attributed still flips on 27% of specification pairs when
nothing about circuit size can contribute.

**Robustness of the claim map.** `F` across binnings differing by a factor of
four ranges 0.70 to 0.77. The committed bins give 0.7316 and are **not** a
maximum: halving every threshold gives 0.7448. The bins were returned by
`select_size_bins` from a measured curve under a committed calibration rule, not
chosen.

---

## What the paper must not claim

1. **Not** that random circuits give more reproducible filings than discovered
   ones. True pooled, false at fixed size, and the pooled version is a size
   artefact.
2. **Not** that filings differ where mechanisms do not, without qualification.
   Mechanisms differ substantially: functional instability 0.40 pooled, 0.48 at
   the smallest sizes.
3. **Not** that the circuits are functionally equivalent. Kappa 0.02 says the
   opposite, and this is what refutes the phantom-specialization reading rather
   than conceding it.
4. **Not** that `seed` means re-run noise. It selects which prompts are sampled,
   so it is evaluation-set variability, not nondeterminism.
5. **Not** anything about scale. One model, one task.

## The claim the data does support

Across 15,840 pre-registered specifications built from published implementations,
of which 7,561 produced a claim, the Annex IV interpretability statement derived
from a discovered circuit flips across **73%** of specification pairs and the
modal claim commands **41%** of the space, failing a filability criterion at every
tolerance a conformity assessment body would plausibly accept. Standardising the
single most influential analytic choice leaves the flip rate at **59%**. Removing
circuit size from the claim entirely and holding it fixed leaves **27%**, with the
interval clear of the pre-registered threshold. The circuits underlying these
claims are structurally near-disjoint, median pairwise overlap **4%**, and
functionally uncorrelated, Cohen's kappa **0.02**, so the instability is not an
artefact of one mechanism being described in different words.

---

## The methodological finding, which is not in the pre-registration

**Circuit size is not an axis of this design. It is an outcome of the `tau`
rule.** It has now distorted three separate pooled quantities: `F` itself, the
direction of the H3 null comparison, and the sign of the H4 gap. Fixing it drops
`F` from 0.7316 to 0.2746, a larger reduction than standardising any
pre-registered axis.

Any pooled statistic in a multiverse whose specifications select objects of
different sizes must be reported with its within-size decomposition. This belongs
in methods as a general point, not as three caveats attached to three results.

---

## Open before submission

- Every citation ledger entry to `VERIFIED`. Several remain `RECALLED`, and
  2606.06267's arXiv identifier is **not confirmed by the authors' own artifact**.
- Scale limitation stated in the abstract.
- EMS cross-check on the balanced five-operator block.
- The FINE and `phi_affected` null, which needs an attention cache the sweep
  never wrote.
- Annex III point 2, the one provision of ten not re-checked against the
  consolidated text.
