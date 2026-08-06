# P1 calibration protocol

**Status: RULE FIXED, PILOT NOT YET RUN.** This document must be committed
before either pilot below is executed. If the commit timestamp on this file is
not earlier than the manifest timestamps in `results/calib-*/`, the calibration
is not a calibration and both pilots must be discarded and rerun.

Two quantities feed the pre-registration but are not themselves scientific
results: the discovery dataset size, and the GPU speedup factor. Both are
currently guesses. This document fixes how each is measured and what rule is
applied to the answer, in advance, so that neither becomes a researcher degree
of freedom inside a paper about researcher degrees of freedom.

**Neither pilot's output may enter the confirmatory grid.** Every manifest
written under `results/calib-*/` carries `confirmatory: false`. The circuits
produced are used to compute one calibration statistic each and are then
discarded.

---

## Calibration 1: discovery dataset size (`n_prompts`)

### Why this is not a budget question

The plan reports seed variance separately from analytic-choice variance and
calls the ratio a headline number. Seed variance has two sources that the
design cannot separate after the fact:

1. sampling noise, which is variation in the prompts drawn, and
2. genuine instability of discovery under a fixed analytic specification.

Only the second is of interest. The first is an artifact of dataset size and
shrinks as `n` grows. At small `n` the headline ratio is inflated by a quantity
that has nothing to do with the paper's claim, and the correct reviewer response
is that the reported instability is small-sample noise.

`n_prompts` is therefore a **validity constraint, not a cost knob**, and it is
chosen by measurement.

### What is known now

**VERIFIED 2026-08-05** from `auto_circuit/data.py`:
`load_datasets_from_json` defaults to `train_test_size = (128, 128)` and
`batch_size = 32`. The instrument's own default is **128 discovery prompts**.

`configs/smoke.yaml` uses `n_prompts: 32` split half and half, so **16**
discovery prompts, one eighth of the default. That value was chosen to make a
timing measurement fast and has no scientific standing.

### Design

Everything except seed and `n` is held fixed at the cheapest defensible setting,
because the quantity being measured is seed-driven variation and nothing else.

| Held fixed | Value | Why |
|---|---|---|
| discovery objective | `LOGIT_DIFF_GRAD_PRUNE_ALGO` | canonical EAP, the cheapest of the seven |
| ablation | `RESAMPLE` | library default and corruption-dependent |
| `clean_corrupt` | `"corrupt"` | fixed by the 2026-08-05 decision |
| prompt variant | ABBA | first level of the confirmed pair |
| granularity | edge | the confirmatory granularity |

| Varied | Levels |
|---|---|
| `n` (discovery prompts) | 16, 32, 64, 128 |
| seed | 0 to 7, eight levels |

Eight seeds rather than the grid's five: pairs grow quadratically, so eight gives
28 pairwise comparisons against ten, and at EAP prices the extra seeds are
minutes. Seeds 0 to 4 coincide with the confirmatory grid's seeds. That is
acceptable because no calibration circuit is retained and no calibration number
enters any claim, but it is recorded here rather than left to be noticed later.

Seed controls the prompt sample drawn by `p1.prompts.generate_ioi_dataset`. That
is the sampling noise this pilot exists to measure.

### The statistic

For each `n`, take the 8 discovered circuits, truncate each to its top **500
edges by prune score**, and compute the mean pairwise Jaccard similarity over all
28 pairs:

    J_seed(n) = mean over pairs (i,j) of  |C_i ∩ C_j| / |C_i ∪ C_j|

**The truncation is absolute, at k = 500, and this is a calibration-only
convention.** It is not the confirmatory metric-relative `tau` rule. Absolute `k`
is used here precisely because the metric axis is not varied in this pilot, so a
metric-relative cut would introduce a dependence the pilot cannot resolve. Using
a different convention for calibration than for the confirmatory grid is stated
openly rather than hidden; 500 is the largest edge count in
`configs/smoke.yaml`'s ladder, so it is not a new number introduced here.

`J_seed(n)` is expected to increase in `n` as sampling noise falls.

### The decision rule, fixed now

Let the ladder be `n in {16, 32, 64, 128}`.

> **Choose the smallest `n` in the ladder such that
> `J_seed(2n) - J_seed(n) < 0.05`.**
>
> That is: choose the first point at which doubling the discovery data buys less
> than 0.05 of mean pairwise Jaccard.
>
> **If no `n` in {16, 32, 64} satisfies the rule, `n_prompts` is set to 128, the
> instrument's default**, and the paper states that the seed-agreement curve had
> not flattened by the largest size tested. That is a limitation to own in the
> abstract, not a result to bury.

The threshold 0.05 is a judgement call and the paper defends it as one. It is
fixed here, before the pilot runs, which is the only property that matters.

**No other rule may be applied to this pilot's output.** In particular, `n` may
not be lowered because the resulting budget is inconvenient. If the rule returns
128 and 128 does not fit the schedule, the response is to change the schedule or
the compute, not the rule.

### Reporting

`J_seed(n)` is reported for all four `n` as a four-point curve in the paper,
whichever value the rule selects, together with the selected `n` and the rule as
stated above. A reader must be able to see the curve the decision was made on.

### Cost

EAP discovery scales roughly linearly in discovery prompts. From the measured
`f = 4.696 s` and `p = 4.606 s` at 16 prompts:

    8 seeds x (16 + 32 + 64 + 128 prompts) ~ 8 x 139.5 s ~ 19 minutes CPU

Cheap enough that not running it would be indefensible.

---

## Calibration 2: GPU speedup factor

### Why

DESIGN-DELTAS D17 records a 20x GPU speedup as an unmeasured guess. The sweep
budget depends on it, and if `n_prompts` comes back at 128 the sweep does not fit
on CPU inside the submission window, so the factor moves from a nicety to a
schedule dependency.

An unmeasured 20x in a locked pre-registration is the same class of error as the
51x IEG factor that measured at 25.8x, and the 12x reuse factor that measured at
4.62x. **Two for two.** There is no reason to expect the third to be different.

### Protocol

Rent one hour on a single CUDA device and run both existing configs **unchanged**:

    python3 scripts/smoke.py --config configs/smoke.yaml
    python3 scripts/smoke.py --config configs/smoke-ieg.yaml

Unchanged is the whole point. The CPU numbers were produced by these exact files,
so the ratio is a clean device comparison and not a comparison of two setups.

Record from each run: `discovery_s`, `evaluation_per_cut_s`, `peak_rss_mb`, and
the environment hash. The speedup factor is the ratio of `discovery_s` on the two
devices, reported separately for EAP and IEG-50 because they have different
compute profiles.

### What this also produces

The environment hash and package set of the machine the sweep will actually run
on. The pre-registration requires every reported number to be traceable to a
config, a seed, and an environment hash, and the sweep box's hash cannot be
recorded before the sweep box exists.

### The rule

The measured factor replaces the guess in D17 and in the budget. **No sweep is
launched and no plan is locked against an unmeasured speedup.** If the measured
factor makes the schedule infeasible, the response is the pre-registered
fractional reduction rule in `PLAN.md` section 4, never ad hoc pruning.

---

## Order of operations

1. Commit this file. Record the hash and UTC timestamp in `RESEARCH_LOG.md`.
2. Run calibration 1. Apply the rule. Record `J_seed` for all four `n`.
3. Run calibration 2 on rented GPU. Record both ratios and the environment hash.
4. Write the selected `n_prompts` and the measured speedup into `PLAN.md`.
5. Resolve the remaining `[CONFIRM]` items.
6. Lock, tag, push, file the embargoed OSF registration.

Steps 2 and 3 are independent and may run in either order.

---

## Calibration 3: the domain of `size_class`

**RULE FIXED 2026-08-06, PILOT NOT YET RUN.** Same condition as above: this
section must be committed before `results/calib-nodes/` exists.

### The error this corrects

On 2026-08-06 `DEFAULT_SIZE_BINS` was re-anchored to `EDGE_COUNT_LADDER` against
the 32,491-edge graph, with the justification that no ladder rung sits within 20%
of a bin boundary. **That justification was computed against the wrong
quantity.** `phi` does not operate on edges. `features_from_circuit` takes nodes,
`components_from_nodes` maps them to `(layer, head)` pairs, and
`n_components_full_model` counts attention heads plus MLPs, which is **156** for
GPT-2 small. `size_class` is therefore `len(nodes touched) / 156`, and the map
from a ladder rung to the number of nodes its edges touch is empirical, not
analytic.

The constants may or may not be adequate. The reasoning behind them was not, and
the unit tests written alongside encoded the same mistake, so they would have
continued to pass while checking nothing relevant.

### Design

One discovery, at the confirmatory settings, using the cheapest objective:
`LOGIT_DIFF_GRAD_PRUNE_ALGO`, `RESAMPLE`, `ABC`, ABBA, seed 0, 128 discovery
prompts. For each rung of `EDGE_COUNT_LADDER`, take the top-k edges by absolute
prune score and count the **distinct nodes** they touch, via
`components_from_nodes`.

Repeated over the five confirmatory seeds so the curve carries variance rather
than being a single draw. Cost is five EAP discoveries, about one minute on an L4.

### The decision rule, fixed now

Let `n(k)` be the mean distinct node count at rung `k`, and `f(k) = n(k) / 156`.

> **Choose the two bin bounds so that the ten rungs split as evenly as the curve
> permits, subject to: no rung's `f(k)` lies within 20% of a bound, and each bin
> contains at least two rungs.**
>
> Among all bound pairs satisfying those constraints, choose the one maximising
> the minimum relative distance from any rung to any bound. Ties broken toward
> the pair with the smaller first bound.
>
> **If no bound pair satisfies the constraints**, `size_class` cannot separate
> the ladder and MEDIUM granularity is reported as degenerate for the edge-level
> grid. That is a finding about the claim map, stated in the abstract, not a
> reason to relax the constraints.

This is deterministic given the curve. It is written as an optimisation over
candidate bounds rather than a judgement so that it cannot be steered.

Candidate bounds are drawn from a fixed set: every value of the form `m * 10^-e`
for `m` in 1 to 9 and `e` in 1 to 3, plus 1.01 as the fixed upper sentinel.

### Reporting

The `n(k)` curve is reported in the paper with its seed variance, alongside the
selected bounds and the rule above, whatever it returns.

---

## Calibration 3b: `position_mass` is a method, not a measurement

Recorded here rather than in a calibration because it is a design decision taken
on 2026-08-06 by Ajay, not a quantity to be measured. It is in this file because
it must be fixed before any confirmatory run, like everything else here.

`phi_affected` requires `position_mass` and nothing computed it. Left as-is it
would have emitted one constant claim across all 18,480 specifications, giving a
flip rate of exactly zero as an artifact of a missing function rather than as a
result.

**Method: mean attention probability over labelled input segments.**

Precedent: arXiv:2211.00593 Figure 10 plots "Average attention probability of
Name Mover Heads" across the IO, S and S2 positions. Attention over labelled
segments is the source paper's own way of describing where a circuit looks, so
this is cited rather than invented.

Fixed choices, each of which is a researcher degree of freedom and is therefore
recorded rather than left implicit:

| Choice | Fixed as | Why |
|---|---|---|
| query position | the final token | The position at which the prediction is made, and the one Figure 10 uses |
| which components | attention heads in the circuit; MLPs excluded | MLPs have no attention distribution |
| weighting across heads | **uniform** | Prune-score weighting would make the mass depend on score magnitudes, which live on different scales across the discovery-objective axis (logit, prob, logprob, logit_exp gradients). Uniform is scale-free and therefore comparable across that axis. Score weighting is defensible and is **not** used. |
| averaging | mean over the clean prompts | |
| segment labels | `seq_labels` from `p1.prompts.generate_ioi_dataset` | Single source, so the claim map and the dataset cannot drift |

A circuit containing no attention heads yields an empty mass, which
`phi_affected` renders as a stated absence. That is a legitimate state and is not
a discard.

**The objection to own in the paper, not to hide.** Attention is contested as an
explanation (Jain and Wallace 2019; Wiegreffe and Pinter 2019). P1 uses it to
construct the affected-person claim and must say so plainly, including that an
alternative attribution method would be an additional axis this paper does not
cross.
