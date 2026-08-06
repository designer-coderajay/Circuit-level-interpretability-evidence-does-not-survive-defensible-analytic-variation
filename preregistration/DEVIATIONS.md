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

*(none yet)*
