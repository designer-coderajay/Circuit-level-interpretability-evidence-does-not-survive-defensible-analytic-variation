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
