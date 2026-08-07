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
