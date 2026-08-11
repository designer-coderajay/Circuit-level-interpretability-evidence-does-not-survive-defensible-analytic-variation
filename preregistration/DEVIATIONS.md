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
