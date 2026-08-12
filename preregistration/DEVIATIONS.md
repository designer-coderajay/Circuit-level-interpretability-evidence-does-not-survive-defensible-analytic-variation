# Deviations from the pre-registered plan

**Append-only from the moment `prereg-p1-confirmatory` is tagged.** Every entry
is dated, states what changed, why, and whether it was decided before or after
the affected result was seen. Entries are never edited or removed.

An empty file after the sweep would be a claim that nothing surprising happened,
which is rarely true. A populated one is not an admission of failure; an
undocumented change is.

---

## Pre-lock disclosures

These predate the tag and are therefore not deviations in the strict sense. They
are recorded here as well as in `PLAN.md` so that a reader who opens only this
file still finds them.

### 2026-08-06. Six confirmatory cells were run and inspected before the lock

`scripts/sweep.py` was validated on a six-cell slice of `configs/sweep.yaml`,
run in two batches so that the per-cell resume could be shown to skip completed
cells. Four recovery curves from one cell and a per-`(metric, tau)` discard count
across the six were inspected.

**No parameter was changed as a result.** The edge-count ladder, `tau` levels,
metric set, recovery convention, discard rule and `phi` constants were all
committed before the slice ran and are unchanged after it.

`results/sweep/` was deleted before the tag and all 1,540 cells rerun after it,
so no reported figure predates the pre-registration.

Full disclosure, including the observed curves and the three properties noted at
the time: `preregistration/PLAN.md` section 11b.

---

## Post-lock deviations

### 2026-08-06T18:06:10Z. Locked with the environment pin outstanding

`prereg-p1-confirmatory` was tagged at `b800f5f9985ff9009a2daf74e73b74ada7a42268`
while `requirements-sweep.lock.txt` was still uncommitted. It had been generated
on the Colab runtime but never downloaded into the repository, and the commit
that was meant to carry it reported `nothing staged; working tree clean`. The
omission was not noticed until after the tag was pushed.

**The tag is not moved.** A tag that moves is not a timestamp, and the value of
this one is precisely that it cannot be rewritten. The environment file is added
in a commit after the tag and this entry records why.

**Substance versus bookkeeping.** What the pre-registration requires is that
every reported number be traceable to a pinned environment. No confirmatory
number exists yet: the six-cell validation slice was deleted before the lock and
the sweep had not started. The pin is committed **before the sweep launches**, so
every reported figure is still traceable to a recorded environment. What went
wrong is the ordering of two commits, not the provenance of any result.

Anyone auditing this should check that the commit adding
`requirements-sweep.lock.txt` predates the earliest manifest under
`results/sweep/`. If it does not, this entry is insufficient and the sweep should
be rerun.

### 2026-08-07. `clean_corrupt` was not passed conditionally; 100 of every 220 cells failed

**What happened.** `scripts/sweep.py` called `mask_gradient_prune_scores` without
supplying `clean_corrupt`, so it took the function's default of `"corrupt"`.
`auto_circuit/utils/ablation_activations.py` asserts

    assert (clean_corrupt is not None) == (ablation_type in batch_specific_ablation)

with `batch_specific_ablation = [RESAMPLE, BATCH_TOKENWISE_MEAN,
BATCH_ALL_TOK_MEAN]`. For the other four operators the argument must be `None`,
and the assertion carries no message, so the failure surfaced only as a bare
`AssertionError` in the cell manifests.

**Scale.** Per discovery objective, 120 of 220 cells succeeded and 100 failed.
The first run reached 1,075 attempted cells with 574 marked `ok`, which matches
that split to within one cell.

**The fix.** `clean_corrupt="corrupt"` is passed for the three operators that
accept it and `None` for the other four.

**Why this is a bug fix and not a design change.** `PLAN.md` fixes
`clean_corrupt` at `"corrupt"` **where the analyst has a choice**. For the
remaining four operators the instrument permits no choice, so nothing about the
pre-registered specification space moves. The grid is still 18,480
specifications over 1,540 discovery cells, and the 5/2 corruption-dependency
split is unchanged: `TOKENWISE_MEAN_CORRUPT` and
`TOKENWISE_MEAN_CLEAN_AND_CORRUPT` read the corrupt distribution through their
own `corrupt_dataset` property rather than through this argument.

**Effect on results already banked.** None. The 574 completed cells are all
`RESAMPLE`, `BATCH_TOKENWISE_MEAN` or `BATCH_ALL_TOK_MEAN`, which received
`"corrupt"` before the fix and receive `"corrupt"` after it. They are not rerun.
The failed cells carry `status: failed`, the runner skips only `status: ok`, so
they are retried automatically.

**How it was missed.** The constraint is documented in DESIGN-DELTAS D18, written
on 2026-08-04 by the same author who then wrote the runner on 2026-08-06 without
acting on it. No test covered it, because every unit test of the specification
space runs without torch and the assertion lives inside the instrument. The
seam was untested, which is the same failure mode as the five defects recorded in
RESEARCH_LOG for 2026-08-06.

### 2026-08-07. The corruption sentinel was passed to the dataset generator

**What happened.** `ZERO` and `TOKENWISE_MEAN_CLEAN` never read the corrupt
distribution, so their specifications carry `CORRUPTION_NOT_APPLICABLE`, the
string `"n/a"`, rather than a real level. `scripts/sweep.py` passed that value
straight into `generate_ioi_dataset`, which accepts only the four sourced levels
and raises. Every cell for those two operators failed, 20 per discovery
objective, 140 across the grid.

**The fix.** The sentinel is resolved to `ABC` at the point of dataset
generation.

**Why the choice cannot affect any result.** VERIFIED from
`auto_circuit/utils/ablation_activations.py`: `ZERO` sets
`out = t.zeros_like(out)` and forces `input_batch = batch.clean`;
`TOKENWISE_MEAN_CLEAN` reads `clean_dataset` only. Neither ever touches
`batch.corrupt`. The corrupt prompts are generated and then never read, so every
corruption level yields a bit-identical circuit for these two operators. `ABC` is
used because it is the canonical default.

This is the same fact that motivates the nesting in the first place: crossing
these operators against four corruption levels would emit four identical
specifications. See DESIGN-DELTAS D18.

**Not a design change.** No axis, level, constant or rule moves. The grid remains
18,480 specifications over 1,540 discovery cells.

**Effect on results already banked.** None. No cell for either operator has ever
completed, so there is nothing to invalidate. They are retried automatically.

### 2026-08-08. Post-lock entry 1 was wrong. The pin predates the tag, and it is stale

**What entry 1 claimed.** That `requirements-sweep.lock.txt` was uncommitted when
`prereg-p1-confirmatory` was tagged, having been generated on the Colab runtime
and never downloaded, and that the commit meant to carry it reported `nothing
staged; working tree clean`.

**What git says.** VERIFIED 2026-08-08 from `git log -- requirements-sweep.lock.txt`,
which returns exactly one commit:

    054f18a  2026-08-04T20:34:51+02:00  GATE 2 PASSED

That is two days **before** the tag at `b800f5f`, 2026-08-06T20:05:55+02:00. The
file was in the repository the whole time. Commit `2f2430a`, the one that claimed
to add it, changed only `RESEARCH_LOG.md` and `preregistration/DEVIATIONS.md`,
VERIFIED from `git show --stat`. It reported a clean tree because there was
nothing left to add. That message was read as absence when it meant presence.

**Entry 1 is not edited.** This file is append-only. An entry documenting a
deviation that did not occur is itself part of the record, and removing it would
be the second error.

**Consequence for the audit instruction.** Entry 1 told an auditor to check that
the pin commit predates the earliest manifest and to rerun the sweep if it does
not. It predates it by two days. The check passes. The instruction stands; its
premise was wrong, and wrong in the safe direction.

**The real problem, which entry 1 obscured.** The committed lock does not
describe the runtime executing the confirmatory sweep.

| | lock file | sweep runtime |
|---|---|---|
| `transformer-lens` | `3.6.0` | `2.18.0` |
| `torch` | `2.13.0` | not verified today |

The `transformer-lens` figure for the runtime is VERIFIED: the Colab cell
executed on 2026-08-08 installs `transformer-lens==2.18.0` by explicit pin. The
runtime `torch` version is **not verified this session**; an earlier session
recorded `2.11.0+cu128` for the same install path, which is RECALLED from a
screenshot and has not been re-checked.

The lock was captured on 2026-08-04 against a Colab image that has since moved,
and the `transformer-lens` pin was tightened after it was written. It is an
accurate record of the **Gate 2 measurement environment** and not of the
confirmatory sweep.

**Why no reported number is unprovenanced regardless.** Rule 8 is satisfied by
the manifests, not by this file. `src/p1/manifest.py` records `environment`, a
fingerprint over Python version, platform, machine and the installed versions of
`auto-circuit`, `torch`, `transformer-lens`, `numpy`, `scipy` and `statsmodels`,
together with `commit` carrying a `-dirty` suffix when the tree is not clean.
`scripts/sweep.py` writes one manifest per discovery cell. Every figure therefore
carries the versions that produced it **per cell**, and cells run on different
images are separable by `environment_hash` rather than silently pooled.

**Action.** `requirements-sweep.lock.txt` is left exactly as committed, because
regenerating it now would destroy the record of the Gate 2 environment that
several measured costs in `CALIBRATION.md` depend on. A second file,
`requirements-confirmatory.lock.txt`, is captured from the sweep runtime and
committed when the sweep ends. If the pooled manifests carry more than one
`environment_hash`, the count and the split across cells are reported in the
paper rather than collapsed.

### 2026-08-11. LOGIT_MSE_GRAD_PRUNE_ALGO does not execute. 220 of 1,540 cells discarded

**What happened.** Every cell of one discovery objective failed, and no cell of
any other objective failed. The sweep ended at 1,320 `ok` and 220 `failed`.

**VERIFIED, not sampled.** The 220 failed `discovery_id`s were listed from the
results directory, sorted, and hashed. The digest is
`ec06e045141548b6ad3186f31ec64247`, identical to the digest computed
independently over the 220 ids that `enumerate_grid(configs/sweep.yaml)` assigns
to `LOGIT_MSE_GRAD_PRUNE_ALGO`. The failure set is exactly that arm and contains
nothing else.

**The error, verbatim from every one of the 220 manifests:**

```
device=cuda | gpu=NVIDIA L4 | n_edges=32491 |
RuntimeError: Found dtype Long but expected Float
```

The manifests record `timings_s: {"data_s": 0.714}` and no `discovery_s`, so the
failure is inside discovery, before any prune score exists.

**Cause: INFERRED, pending source read.** The same objective has been emitting a
shape warning from `auto_circuit/prune_algos/mask_gradient.py:105`, at
`loss = t.nn.functional.mse_loss(token_vals, batch.answers)`, recorded in
DESIGN-DELTAS D19. `batch.answers` carries token ids, which are integral. MSE
against an integral target raises this error in the backward pass. That is
consistent with every observation but the source line has not been read at the
installed version, so it is inference. Upgrade to VERIFIED by reading
`mask_gradient.py` in the sweep environment and recording the dtype directly.

**Decision: discard, not repair.** Rule 5. Rule 2 forbids modifying auto-circuit,
which is the instrument under test and is reproduced verbatim. Casting the target
would substitute a corrected instrument for the shipped one and hand a reviewer a
free rejection.

**Effect on the grid.**

| | pre-registered | realised |
|---|---|---|
| discovery objectives | 7 | 6 |
| discovery cells | 1,540 | 1,320 |
| specifications | 18,480 | 15,840 |

Discard rate **220/1,540 = 14.29% of cells**, and the same fraction of
specifications, being exactly one of seven objectives.

**Why the exclusion cannot bias any result.** The criterion is non-execution,
raised by the instrument itself, and it was determined before any circuit from
that arm existed. No output from the arm was inspected, because none was ever
produced. This is not a data-dependent exclusion and cannot move the
specification curve toward any conclusion.

**Effect on the pre-registered analysis.** The objective axis drops from seven
levels to six. The H1 to H4 decision rules, the `tau` levels, the metric set, the
recovery convention, the discard rule and the `phi` constants are all unchanged.
Two items need attention at analysis time and are flagged rather than resolved
here:

1. Variance decomposition over the objective axis now has six levels. The reduced
   degrees of freedom are reported, and the REML fit is refitted on the realised
   design rather than the planned one.
2. The random-circuit null multiverse must be sized to the realised 1,320 cells,
   not the planned 1,540.

**Where it is reported.** Decided by Ajay, 2026-08-11: **methods** states the
discard rate and the reason; **discussion** raises it as an observation about
instrument maturity. It does not go in the abstract.

**How it was missed.** The seam smoke test that would have caught it in four
minutes, proposed in RESEARCH_LOG on 2026-08-07 after the fifth and sixth defects
of the same shape, was still unwritten when the sweep launched. This is the
seventh.

### 2026-08-11. Manifests record `commit: UNKNOWN`. Code identity recovered by argument, not by record

**What happened.** All 1,540 manifests carry `"commit": "UNKNOWN"`.
`src/p1/manifest.py` documents that `git_commit()` returns `"UNKNOWN"` when git is
unavailable rather than raising. The sweep ran on Colab VMs populated from an
uploaded tarball rather than a clone, so there was no `.git` directory to read.

Rule 8 requires every reported number to be traceable to a config, a seed and an
environment hash. Config, seed and environment are present and clean. **The
commit is not recorded.**

**Verified independently from the results archive, 2026-08-11**, by reading all
1,540 manifests out of the downloaded `p1_sweep` folder rather than trusting the
Colab session:

| check | result |
|---|---|
| manifests read without error | 1,540 of 1,540 |
| `status: ok` | 1,320 |
| `status: failed` | 220 |
| md5 of sorted failed `discovery_id`s | `ec06e045141548b6ad3186f31ec64247`, matching the digest computed from `enumerate_grid` for `LOGIT_MSE_GRAD_PRUNE_ALGO` |
| distinct environment fingerprints | **1** |
| distinct configs | **1**, byte-identical to `configs/sweep.yaml` at HEAD |

The single environment, across three VM recycles and three days:

```
python 3.12.13 | Linux-6.6.122+-x86_64-with-glibc2.35 | x86_64
auto-circuit 1.0.1 | torch 2.11.0+cu128 | transformer-lens 2.18.0
numpy 1.26.4 | scipy 1.16.3 | statsmodels 0.14.6
```

**No cross-image pooling question arises.** Every cell in the sweep ran in the
same environment, and that is a record, not an assumption.

**Code identity: INFERRED, argued rather than read.** `git diff --stat
5371629..HEAD -- src scripts configs preregistration/PLAN.md` is empty. The three
commits after `5371629` are `d494ff6`, `c8f2d3c` and `d5e76fc`, all markdown only.
The repository's code has therefore not moved since `5371629`, which is the
commit the sweep ran.

**The limit of that argument, stated plainly.** It establishes that the
repository did not change. It does **not** establish that the tarball uploaded to
Colab was packed from a clean tree at `5371629`. Uncommitted edits at packing time
would be invisible to this check, and `git status` was not recorded at the moment
of packing. The config match is real evidence against that, since the manifests'
config is byte-identical to the committed one, but it covers `configs/` only and
not `src/` or `scripts/`.

**How to close it.** If `p1.tar.gz` still exists on the research lead's machine,
compare its `src/` and `scripts/` against git's tree at `5371629`. A match
upgrades this to VERIFIED in a later append. If the tarball is gone, the claim
stays INFERRED and the manuscript states the commit as `5371629` citing this
entry.

**Not rerun.** A rerun costs three days and would not produce a better commit
record unless the runner changes, which is the real fix.

**Fix owed, and it transfers to P2 and P3.** `scripts/sweep.py` should refuse to
start when `git_commit()` returns `UNKNOWN`, unless an explicit flag is passed,
and the flag should itself be recorded in the manifest. A provenance field that
silently degrades to a placeholder string is worse than one that stops the run.
This is the same failure as post-lock entry 1: a placeholder read as a fact.

#### Closed 2026-08-11. Code identity upgraded from INFERRED to VERIFIED

`p1.tar.gz`, the archive uploaded to Colab, was recovered and compared file by
file against git's tree at `5371629` using git blob hashing, which is content
addressed and therefore exact.

| scope | files | identical | differ | missing |
|---|---|---|---|---|
| `src/`, `scripts/`, `configs/`, `pyproject.toml`, `preregistration/PLAN.md` | 22 | **22** | 0 | 0 |

**Every file that could affect a result is byte-identical to the committed tree.**
The concern raised in the entry above, that uncommitted edits at packing time
would be invisible, is answered: there were none.

The archive additionally holds 18 macOS AppleDouble sidecars (`._spec.py` and
similar), artefacts of `tar` on macOS. They carry resource-fork metadata, no code,
and cannot be imported by Python, since `._spec` is not a valid module name. They
are noted for completeness and have no bearing on any result.

**The sweep ran commit `5371629`.** Reported as such in the manuscript, with this
entry cited for how it was established, because the manifests themselves record
`UNKNOWN` and a reader is entitled to know that the commit was recovered rather
than logged.

The fix owed to `scripts/sweep.py`, refusing to start on an `UNKNOWN` commit
without an explicit recorded flag, still stands for P2 and P3. Recovering
provenance after the fact worked here only because the archive happened to
survive.

### 2026-08-11. H4 is not computable from the banked sweep. Per-example verdicts were never written

**What the plan requires.** PLAN.md section 2 states H4 as
`F - (1 - agreement_rate) > 0.10`. `agreement_rate` is defined in DESIGN-DELTAS
D4 and in RESEARCH_LOG for 2026-08-04, adopted from
`05_Phase_Targeted/per_example_agreement.py` in the 2606.06267 release:

```python
def agreement_rate(preds_a, preds_b):    # fraction of examples where both agree
def cohens_kappa(preds_a, preds_b):      # chance-corrected agreement
```

Two circuits are compared by their **per-example correct/incorrect verdicts**. The
design note says this is computable "from the `run_circuits` output already
produced by the sweep, at no extra forward passes".

**It is not, because the sweep did not keep that output.** VERIFIED 2026-08-11 by
reading `result.json`. Each cell records `metric_curves`, a single scalar per
edge-count rung per metric, being the batch mean returned by
`measure_answer_diff`. **Per-example values are reduced to a mean inside the
measurement call and never written.** There are no `preds_a` and `preds_b` to
compare, for any pair, anywhere in the results directory.

**Scope.** H4 and the secondary outcomes "agreement rate and Cohen's kappa" in
PLAN.md section 3. **The primary outcome is unaffected.** `F` is computed from
claim strings, which are present for all 15,840 specifications. P0, H2 and H3 are
likewise unaffected.

**How it was missed.** The same failure mode recorded three times already in this
project: a design document asserted a property of the runner, and nothing checked
that the runner had it. D4 said the data would be there; the runner was written
two days later by the same author and reduced it away.

**What a fix costs, INFERRED not measured.** Discovery does not need repeating:
`top_edges`, the 10,000 ranked edges, is stored per cell, so prune scores are
already banked. A repair run would evaluate only the **selected** rung per
specification and emit per-example verdicts. Verdicts depend on
`(discovery cell, rung)` alone, not on `metric` or `tau` except through rung
selection, so the distinct work is roughly 1,320 cells times a handful of rungs,
against the 80 circuit evaluations per cell the full sweep performed. Order of
one to two hours on an L4 rather than the fifteen the original evaluation took.
This estimate is inference from the recorded timings and is not measured.

**Decision required from the research lead.** Recorded here as open on
2026-08-11, resolution to be appended:

1. **Repair run.** Emit per-example verdicts for selected rungs and compute H4 as
   pre-registered. Preferred on the merits, since it keeps a pre-registered
   hypothesis testable.
2. **Report H4 as not computed**, stating why, and drop it from the results.
   Honest but weak: a hypothesis dropped after the fact invites the reading that
   it was dropped because of what it would have shown, even though nothing about
   it has been seen.
3. **Substitute an equivalence measure computable from banked aggregates.**
   **Not recommended and arguably disqualifying.** Choosing a measurement after
   seeing which measurements are available is precisely the analytic freedom this
   paper exists to document. Doing it in this paper would be indefensible.

**No substitution is made in the interim.** `scripts/analyse.py` stage 1 computes
the primary outcome and the claim-based secondaries and explicitly excludes H4,
with this entry cited in its docstring.

#### Resolved 2026-08-11. Option 1, repair run

Ajay's decision, taken before any H4 quantity was computed or seen: **emit the
per-example verdicts in a repair run and test H4 as pre-registered.**

Constraints on that run, fixed here so they precede it:

1. **Discovery is not repeated.** `top_edges` is read from the banked
   `result.json`. No prune score is recomputed, so the circuits under test are
   bit-identical to the ones already reported.
2. **Only the selected rung is evaluated**, the rung already recorded in each
   specification's `edges` field. No new rung is introduced and the `tau` rule is
   not re-run.
3. **auto-circuit is untouched.** The verdict is read from the existing
   measurement path; `agreement_rate` and `cohens_kappa` are reproduced verbatim
   from `05_Phase_Targeted/per_example_agreement.py` and live in `src/p1/`.
4. **The repair run writes to a separate directory** and does not overwrite any
   banked result. Its manifests carry their own environment fingerprint, which is
   expected to differ from the sweep's and must be reported if it does.
5. **H4's threshold, 0.10, is not revisited.** It was fixed on 2026-08-06 and this
   entry does not reopen it.

If the repair run cannot reproduce the recorded circuits exactly, H4 is reported
as not computed rather than computed on approximations, and this entry is
appended to say so.

### 2026-08-11. The variance decomposition names an estimator but never its response

**Found before any decomposition was computed.** No variance-components code
exists in `src/` or `tests/`, and no decomposition output has been produced. This
entry is written first so that its timestamp precedes any number.

**What the plan fixes.** PLAN.md section 6: "Random-effects model, one component
per axis, with corruption nested within ablation. The design is unbalanced, so
REML is the primary estimator... The five corruption-dependent operators form a
balanced sub-block, and EMS is computed there as an independent cross-check."
Section 3 lists "variance components by axis" as a secondary outcome. Section 6
adds "Seed variance reported separately from analytic-choice variance. The ratio
is a headline number."

**What it never fixes: the response variable.** VERIFIED 2026-08-11 by searching
PLAN.md, DESIGN-DELTAS, RESEARCH_LOG and P1-MEMORY. The estimator is specified in
four places and the quantity it decomposes in none.

**Why that is not a technicality.** The plan's own language is "claim variance",
at section 4 ("both the ablation and metric axes would carry zero claim
variance") and section 11b ("will carry little claim variance"). The claim is
**categorical**, nine classes at MEDIUM. REML and EMS are Gaussian
variance-components estimators for a continuous response. **The named estimator
cannot take the named quantity.** The plan specifies a method that does not apply
to the outcome it was written about.

**No default is safe.** Choosing the response now, with `F = 0.7316` already
known, is precisely the analytic freedom this paper documents. Any choice must be
made explicitly by the research lead, recorded here, and made without any
decomposition having been seen. What protects it is that no decomposition of any
kind has been computed.

**The options, stated neutrally.**

1. **REML on a continuous pipeline quantity fixed by the design**, such as the
   selected circuit size in edges, or normalised recovery at the selected rung.
   Keeps the pre-registered estimator exactly. Decomposes **structural**
   variation, not claim variation, so it does not answer which axis drives `F`,
   and the paper must not imply that it does.

2. **A claim-level decomposition appropriate to a categorical response**, for
   example the flip rate computed within each axis level and compared with the
   pooled `F`, bootstrapped over specifications. Answers the question the paper
   actually asks. **Departs from the named estimator**, so REML and the EMS
   cross-check are not run and the deviation is on the record.

3. **Both**, with 1 reported as the pre-registered decomposition of structure and
   2 as a declared deviation answering the claim-level question. Costs the most
   and concedes the most, in that it states plainly that the pre-registration
   specified an inapplicable method.

**Consequence for the paper if unresolved.** Section 6's headline seed-variance
ratio and section 8's promise to "report which analytic axis carries the residual
variance so that it can be standardised first" both become unreportable. The
second appears in the drafted abstract for the stable outcome and would have to
be struck.

#### Resolved 2026-08-11. Option 3, both arms. Definitions fixed here, before computation

Ajay's decision. Two decompositions are reported. **Every definition below is
committed before any decomposition value has been computed**, which is the only
thing that makes a choice taken after `F` was known defensible at all.

**Arm A, pre-registered estimator, structural response.**

REML with one component per axis, corruption nested within ablation, plus the EMS
cross-check on the balanced five-operator block, exactly as PLAN.md section 6
fixes. Response: **`log10` of the selected circuit size in edges.**

Why that response and not normalised recovery. Recovery at the selected rung is
**censored by the selection rule**: `select_rung` returns the smallest rung whose
recovery is at least `1 - tau`, so the recorded value is bounded below by
construction and its distribution is a truncation artefact, not a measurement.
Decomposing it would decompose the selection rule. Circuit size carries no such
censoring. `log10` because `EDGE_COUNT_LADDER` is log spaced and because
`select_size_bins`, committed under calibration 3, already works in log space, so
this introduces no new scale choice.

**This arm decomposes structure, not claims.** The paper must not present it as
explaining `F`, and any sentence implying it does is wrong.

**Arm B, declared deviation, claim response.**

For a set of axes `G`, define the within-group flip rate over the pair population
that shares `G`:

    F_within(G) = 1 - [ sum_g sum_c n_{g,c}(n_{g,c} - 1) ] / [ sum_g n_g(n_g - 1) ]

where `g` indexes groups formed by the levels of `G`, `c` indexes claim classes,
`n_{g,c}` counts specifications in group `g` with claim `c`, and `n_g` is the
group size. With `G` empty this reduces exactly to the pooled `F` of PLAN.md
section 3, so the family is consistent with the primary outcome by construction.

Two per-axis quantities, for each axis `A`:

- **`F_fixed(A) = F_within({A})`.** The residual flip rate once `A` is
  standardised. **This is the quantity PLAN.md section 8 asks for** when it
  promises to report which axis to standardise first: the axis with the lowest
  `F_fixed` is the one whose standardisation buys the most.
- **`F_alone(A) = F_within(all axes except A)`.** The flip rate among pairs that
  differ only in `A`. How much that axis moves the claim by itself.

**Headline ratio, PLAN.md section 6's "seed variance reported separately from
analytic-choice variance".**

    ratio = F_alone(seed) / F_fixed(seed)

Numerator: pairs identical in every analytic choice, differing only in random
seed. Denominator: pairs sharing a seed, differing only in analytic choices. A
ratio near 1 means re-running the same analysis is as unstable as choosing a
different one, and the regulatory argument weakens sharply. A ratio near 0 means
the instability is analytic, which is the paper's claim.

**Uncertainty.** Bootstrap over specifications, `B = 10,000`, seed 0, per PLAN.md
section 6. Never over pairs. The resampling unit does not change between the
primary outcome and this decomposition.

**Reporting.** Arm A is labelled pre-registered. Arm B is labelled a deviation,
with this entry cited. Neither is presented as the other, and the paper states
that the pre-registration named an estimator its own outcome could not take.

### 2026-08-11. The pre-registered bootstrap is not valid for the `alone` family

**What was found.** Running arm B, every `F_alone` observed value fell **outside**
its own 95% interval, while every `F_fixed` value fell inside. Not a coding
error: the two families use identical code and differ only in grouping.

**Cause, VERIFIED by measurement.** Mean group size:

| family | mean group size | bias of bootstrap mean | interval usable |
|---|---|---|---|
| `fixed` | 1,512 to 2,520 | -0.0002 to -0.0006 | yes |
| `alone` | 1.7 to 4.5 | large and negative | **no** |

The pre-registered bootstrap resamples specifications with replacement and
**retains self-pairs**, a choice documented and defended in `p1.multiverse
.bootstrap_over_specifications`. A specification drawn twice pairs with itself,
always concordantly, which deflates a flip rate. At `N = 7,561` that is an
`O(1/N)` effect and invisible. Within a group of two it is `O(1/n_g)` and
dominant.

A cluster bootstrap resampling groups rather than specifications was tried as a
diagnostic, `B = 2,000`: it moved the `alone/seed` interval from
`[0.1619, 0.1884]` to `[0.1753, 0.2209]` against an observed 0.2249. Closer,
still excluding it, because duplicating a whole group reintroduces self-pairs.
**The problem is the pair population under any with-replacement scheme at small
`n_g`, not the resampling unit.**

**Decision, and it is the conservative one.** `F_alone` and the headline seed
ratio are reported as **point estimates with no interval**. The report records
`mean_group_size`, `bootstrap_mean`, `bias` and a boolean `interval_quotable` for
every statistic, so the judgement is in the artifact and not only in prose.

**No bias-corrected estimator is introduced.** Constructing one now, after seeing
that the naive intervals disagree with the point estimates, would be an analytic
choice made in response to a result. That is the behaviour this paper documents,
and the correct move is to report less rather than to invent an estimator that
happens to fix the number.

**What survives, and it is the part that matters.** PLAN.md section 8 promises to
"report which analytic axis carries the residual variance so that it can be
standardised first". That question is answered by `F_fixed`, whose intervals are
valid, whose bias is under 0.0006 on every axis, and whose group sizes are in the
thousands. The unquotable family is the complementary view, not the promised one.

### 2026-08-11. The null multiverse: two constants the plan left open, fixed before running

**Written before any null value was computed.** No null multiverse has been
generated at the time of this entry.

PLAN.md section 6 fixes the null as "the size-matched random-circuit null
multiverse, pushed through the identical pipeline and the identical claim maps"
and H3 as separated when "the discovered median lies outside the random 95% CI".
It does not fix how many null multiverses are drawn, nor the seed.

**Fixed here.** `R = 1,000` independent null multiverses, seed 0. One null
multiverse assigns to every kept specification a circuit of **that
specification's own recorded edge count**, drawn uniformly without replacement
from the full 32,491-edge namespace, and computes `F` over the 7,561 resulting
claims exactly as the primary outcome is computed. Measured cost 1.6 s per
multiverse, so `R = 1,000` is 27 minutes and no accuracy is traded for time.

**The edge population is the full namespace, not the observed union.** The banked
`top_edges` cover 26,888 of 32,491 edges. Sampling from that union would sample
from edges some discovery objective already ranked in its top ten thousand, which
would make the null a function of the thing it is supposed to be a null for.
`p1.graph.enumerate_edges` reconstructs all 32,491 combinatorially and the count
agrees with what the instrument reports in every manifest.

**Scope, and it is a real limitation.** The null is computed for `phi_overseer`
at COARSE and MEDIUM only. `overseer_key` reaches `position_mass` only at FINE,
and `affected_key` uses it at every granularity. `position_mass` came from
attention cached during the sweep and never written to disk, so it cannot be
recovered for a random circuit without rerunning the model. **The primary outcome
is `phi_overseer` at MEDIUM, so H3 is decided as pre-registered.** H3 is not
decided for `phi_affected` or for FINE, and the paper states that rather than
reporting one map and letting a reader assume both.

**Optimisation, and how it is prevented from becoming a deviation.** Generating
1,000 multiverses through the verified path costs 107 s each, thirty hours in
total. `p1.null_multiverse` vectorises exactly one step, mapping edge endpoints
to components, and leaves `CircuitFeatures`, `layer_band`, `size_class` and
`phi_overseer` untouched. The vectorised mapping is asserted equal to the
verified path in `tests/test_null_multiverse.py` across circuit sizes 1 to
32,491 and on an adversarial MLP-only circuit. **A faster path that is not
bit-identical to the verified one would be a different experiment.**

#### Refinement 2026-08-11, before any null value existed: per-replicate streams

The analysis sandbox terminates a process when its parent shell exits, so the
27-minute run cannot be issued as one call and cannot be backgrounded. The script
is therefore resumable: it fills the null distribution under a wall-clock budget,
saves progress, and continues on the next invocation.

Resumption forces one change to how "seed 0" is realised. A single shared
generator makes replicate `r` depend on every replicate before it, so a run
interrupted at 600 could not resume without redrawing all 600. Replicate `r`
instead draws from `numpy.random.default_rng([NULL_SEED, r])`, an independent
stream per replicate.

**This changes which specific circuits are drawn, and it is recorded for that
reason.** It does not change `R`, the seed constant, the sampling distribution,
the edge population or the statistic. The result is now identical whether the
1,000 replicates run in one pass or in ten, which it was not before.

Fixed before any null value was computed. No null distribution had been produced
when this was written.

#### 2026-08-11. Repair run: `correct` defined, and the reproduction gate

Fixed before the repair run exists. No verdict has been computed.

**`correct`, per example.** A circuit gets an IOI example right when it assigns a
higher logit to the indirect-object token than to the subject token. This is the
standard IOI success criterion and it is the sign of the answer difference the
sweep already measured in aggregate, so the per-example verdicts decompose a
quantity already reported rather than introducing a new one. Upstream's shape,
`{example_index: bool}`, is preserved so `p1.agreement` applies unchanged.

**Discovery is not rerun; the ranking is reproduced.** `ranked_edges` sorts by
`(-abs(score), str(edge))`. Assigning score `N - rank` to the r-th banked edge
gives distinct, strictly decreasing magnitudes, so the name tie-break never fires
and the induced order is exactly the banked one. Only the order is used, and only
top-k selection depends on it. This makes the circuits under test bit-identical
to the ones already reported, at zero discovery cost.

**The gate, satisfying constraint 5.** For every cell the recomputed mean answer
difference at the selected rung is compared against the banked `metric_curves`
value, tolerance 1e-3 for float32 nondeterminism across GPU runs. Agreement
proves the per-example numbers decompose the banked figure. Cells that disagree
are written `status: "mismatch"`, excluded from H4, and their rate reported. If
the mismatch rate is material, **H4 is reported as not computed**, per the
constraint fixed on 2026-08-11.

**Written blind, and gated accordingly.** `scripts/repair.py` was authored with
no torch and no GPU available, so every auto-circuit API assumption in it is
unverified. It ships with `--probe`, which validates the Edge attributes, checks
that all 10,000 banked edge names exist in the model graph, and asserts that the
synthesised scores reproduce the banked ranking exactly. **The evaluation loop is
deliberately not written until the probe passes.** Writing it against untested
assumptions and discovering an attribute name is wrong an hour into a GPU session
is the failure mode this project has already paid for seven times.

#### Gate result 2026-08-11: 0 mismatches in 1,317 cells

The repair run reached 1,317 of 1,320 cells before being stopped, and the final
three were completed on resume.

    grep -l '"status": "mismatch"' p1_repair/*/verdicts.json | wc -l   ->   0

**Not one cell failed the reproduction gate.** At every selected rung, the mean
answer difference recomputed from synthesised prune scores matched the banked
`metric_curves` value within 1e-3, and on the cell inspected individually it
matched to all six printed decimals.

Constraint 5, fixed on 2026-08-11 before the run existed, said H4 would be
reported as not computed if the banked circuits could not be reproduced exactly.
**That condition is met with nothing to discount.** The per-example verdicts
decompose figures already reported rather than describing some neighbouring
circuit.

This also settles the ordering question the run was gated on: discovery was never
repeated, so the circuits carrying the verdicts are the same objects that
produced `F = 0.7316`, not a re-derivation of them.

**What it unblocks.** H4 becomes computable as pre-registered, using
`agreement_rate` and `cohens_kappa` reproduced verbatim in `src/p1/agreement.py`.
The functional-equivalence measurement that red-team objection F1 demanded now
exists, so the phantom-specialization reading can be tested rather than conceded.

### 2026-08-11. Figure 1: the pre-registered form does not apply to a categorical outcome

**Decided before the figure was drawn.** No version of it existed when this was
written.

PLAN.md section 6 fixes Figure 1 as "the specification curve: effects sorted
ascending with a bootstrap band, a dot matrix of active choices below, and the
null multiverse overlaid rather than described", following Simonsohn, Simmons and
Nelson, *Specification curve analysis*, Nature Human Behaviour 4(11), 1208-1214,
2020, verified by DOI 2026-08-11.

**That form assumes a continuous effect estimate per specification.** P1's outcome
is a claim class, one of nine at MEDIUM. There is nothing to sort ascending and no
band to draw around it. The pre-registration specified a figure its own outcome
cannot support, which is the same defect as the variance decomposition naming an
estimator without a response.

**Adopted, by Ajay's delegation, 2026-08-11.** Specifications are ordered by claim
class, classes ranked by frequency, ties broken by selected circuit size. The
upper panel plots the claim class of each specification against its rank, so the
curve is a staircase whose step widths are the class shares. The lower panel is
the dot matrix the plan asks for: one row per axis level, marked where that level
is active. The null multiverse is overlaid as its own class-share staircase.

**What the reader gets, and it is what the plan wanted.** The width of the modal
step is `pi*` read off the axis. The number of steps is the number of distinct
filings the same system supports. The dot matrix shows which analytic choices sit
under each step. A standards body can look at it and see how much of the space
agrees.

**Rejected alternatives, recorded so the choice is auditable.** Plotting
`log10(selected edges)` as the effect keeps the pre-registered form exactly but
charts structure rather than claims, and this paper has already shown those are
governed by different axes. Plotting a per-specification indicator of agreement
with the modal claim gives a binary strip with no meaningful ascending order.

**Reported as a deviation**, with the pre-registered wording quoted beside it, so
a reader can see both what was promised and what was drawn.
