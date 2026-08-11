# Next session

Written 2026-08-11 at the end of the analysis phase. Read `docs/FINDINGS.md`
first; it is the complete result and the source for the results section.

## State

**The science is finished.** All four pre-registered outcomes are settled, the
red team is run and answered, and every number traces to a committed script, a
config, a seed and a single environment fingerprint.

| | outcome | status |
|---|---|---|
| P0 | `J_bar` = 0.1396 [0.1377, 0.1418] | reported, premise holds |
| H2 | `F` = 0.7316 [0.7247, 0.7380] | **confirmed** |
| H3 | pooled separated; direction is a size artefact | **rejected, both readings reported** |
| H4 | gap 0.3344 [0.3297, 0.3394]; kappa 0.0146 | **supported, with the within-size reversal reported** |

**What is not finished is the bibliography**, and it is the only thing blocking
the manuscript.

## Do these in order

### 1. Close the bibliography. Blocking.

Six entries are VERIFIED and citable: `2407.08734`, `2606.00033`, `2501.16496`,
`2504.13151`, `2308.14272`, `2512.13907`.

Nine are not. See the "Remaining gaps" table at the end of
`docs/CITATION-LEDGER.md`. The work, in order of risk:

- **Delete "Mueller et al. 2026 on non-identifiability."** It is a misattribution
  of `2504.13151`, which is MIB, ICML 2025, a benchmark paper. This is the one
  that would have ended the paper.
- **`2606.06267`.** Authors, venue and findings verified from their own
  replication repository, but their BibTeX carries `note = {arXiv preprint, link
  to be added}`, so **the identifier is not confirmed by the authors**. Either it
  has resolved since, or cite the repository and author list without the ID.
- **`2510.00845` and `2409.09951`.** Both PARTIAL. Two fetch routes failed for
  the first. Use a browser on the abs pages, as was done for EUR-Lex.
- **Seven name-only references.** Wang (IOI), Conmy (ACDC), Nanda (attribution
  patching), Meloux, Steegen, Simmons, Simonsohn. Resolve each to an identifier
  and fetch it. Steegen, Simmons and Simonsohn are RECALLED-plus: their DOIs
  agree across three independent sources but have never been resolved directly.

### 2. Figure 1, the specification curve

Pre-registered in PLAN.md section 6 and never produced. Needs a decision first:
the outcome is categorical, so "effects sorted ascending" has no direct reading.
The defensible version sorts specifications by claim class, colours the band by
class, and puts the dot matrix of active choices beneath. Decide, record the
decision, then draw.

### 3. Write the manuscript

`docs/FINDINGS.md` has every number and, more importantly, a list of five things
the paper **must not claim**. `docs/BRIEF-AUDIT.md` records where the 3 August
design and the executed work diverge, so no sentence written from the brief goes
in uncorrected.

Structural points that are settled and should not be relitigated:

- Lead with the claim-flip result, not circuit instability. Circuit instability
  at `J_bar` = 0.1396 is close to what the prior literature already reports.
- Report every pooled figure with its within-size decomposition. Circuit size is
  an outcome of the `tau` rule, not an axis, and it has distorted three separate
  pooled quantities.
- Scale limitation in the abstract, not section 7. One model, one task.
- The `LOGIT_MSE` arm goes in methods as a discard with its rate, and in
  discussion as an observation about instrument maturity. Not the abstract.
- Apply the humanizer skill before finalising.

## Open engineering, none of it blocking

- The seam smoke test over every axis level. Seven defects have lived in the P1
  to auto-circuit seam and none was caught by the torch-free test suite.
- `requirements-confirmatory.lock.txt`, 719 lines, still on Drive, not in the repo.
- EMS cross-check on the balanced five-operator block.
- FINE and `phi_affected` null, which needs an attention cache the sweep never wrote.
- Annex III point 2, the one provision of ten not re-checked against the
  consolidated text.
- `scripts/repair.py` reloads every `result.json` before its skip check, so
  resuming is slower than it needs to be.

## The rule that earned its place this week

A constraint written in a design document is not a constraint enforced by
anything. Seven defects, a dead `.gitignore` negation that meant no manifest was
ever tracked, an estimator named without a response variable, and a citation that
would have been fabricated all survived because they were written down and never
checked. **The commit that records a constraint should add the thing that fails
when it is violated.**
