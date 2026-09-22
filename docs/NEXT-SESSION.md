# Next session

Written 2026-09-22 at the end of the verification and code-quality audit.

## Committed and pushed

The audit landed as `71c67d4` and is on the renamed remote. Nothing is
outstanding from it except this file and `RESEARCH_LOG.md`, which were updated
after the commit:

```
git add -A && git commit -m "log: gitignore near-miss and clone verification" && git push
```

## State

Verified this session, all from a run rather than a reading:

| | |
|---|---|
| test suite | 367 passed, 1 skipped, 368 collected |
| claim verifier | 39 checks, 0 failures |
| number audit | 157/157 on `manuscript.md`, 336/336 on `iaseai/main.tex` |
| clone reproducibility | all four analysis scripts, output identical to raw, figure byte-identical |
| committed analysis JSON | all seven regenerate byte-identically from raw sweep |
| coverage on `src/p1` | 98%, `multiverse.py` at 100% |

See `RESEARCH_LOG.md`, 2026-09-21/22, for the six defects and their fixes. Five
were in the verification apparatus, not the paper.

## Open, in priority order for the 26 September handover

1. ~~Compile and measure the page count.~~ **Done 2026-09-22: 9 pages of 10**,
   0 errors, 0 overfull boxes, 0 undefined citations. Three tables that
   overflowed the column are fixed. Room to spare; no cuts needed.
2. ~~Verify the Annex IV and Article 86 quotations.~~ **Done 2026-09-22: all
   nine verbatim against `CELEX:02024R1689-20260727`**, and Regulation (EU)
   2026/1744 confirmed real and not touching the provisions relied on. The Act
   is now actually cited, which it was not.
3. **Related Work has no regulatory or compliance scholarship.** Flagged at the
   reviewer pass and still open. Needs verified citations, ledger entries first.
4. **Fill the AAAI Reproducibility Checklist**, `paper/iaseai/ReproducibilityChecklist.tex`.
   The answers are now unusually strong: say plainly that every analysis output
   is reproducible from the committed tree with no raw data.
5. **Email the Program Chairs** about archival versus non-archival under rule 3.1,
   given the arXiv preprint. Rule 3.5 allows it and 3.6 needs the Statement of
   Contributions.

## Blocked on a GPU

The 924-cell Pythia-160m grid. Plan `preregistration/PLAN-REPLICATION.md`, tag
`prereg-p1-replication`, config `configs/replication_pythia.yaml`. Harness
verified end to end. Nothing about it is open except compute.

## Standing hazard, learned twice this session

A verification script that has never been run against the artefact it claims to
cover is not evidence. Both the clone gap and the IASEAI number gap were
invisible to inspection and obvious within one command. Before trusting any
check here, confirm what file it actually opens.
