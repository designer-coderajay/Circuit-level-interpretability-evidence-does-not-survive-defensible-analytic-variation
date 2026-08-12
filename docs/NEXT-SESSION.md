# Next session

Written 2026-08-12 after the Pythia-160m transfer probe. Read
`RESEARCH_LOG.md` from the 2026-08-12 entry down; it has the probe result, Gate P
and the thresholds as committed.

## State

**The paper is finished and submittable as it stands.** 12 pages, 7 tables, 1
figure, 15 references all cited and resolving, 347 of 347 numbers traced to
`results/analysis/*.json`, 36 of 36 claim checks, 321 tests, 0 LaTeX errors.
Nothing below is required to submit. All of it is to answer one reviewer
objection: one model, one task.

**Second-model transfer is established.** Three conditions, all met:

| condition | result |
|---|---|
| edge namespace | 32,347 against 32,491. Deficit is `n_blocks * n_heads`, all `A{b}.{h}->MLP {b}`. `parallel_mlp` flag committed at `0cd6856` |
| tokenizer | no IOI name splits under Pythia's tokenizer |
| task performance | Gate P passed: IO preferred 0.961, mean logit diff 117% of GPT-2 small |

## Housekeeping before anything else

1. **Clear the git locks** if not already done. `.git/HEAD.lock`,
   `.git/index.lock`, `.git/objects/*/tmp_obj_*`. Left by a commit run through
   the Cowork sandbox mount, which cannot unlink inside `.git`. Do not run git
   write operations through that mount.

2. **Copy `requirements-confirmatory.lock.txt` into the repo.** 719 lines, still
   only on Drive. It is the exact environment all 1,540 confirmatory cells ran
   in. It has been on the non-blocking list since 08-11 and it cost time on
   08-12 when a fresh Colab image needed the pins rederived. It is blocking now.

   The rebuild that worked, for reference:
   `auto-circuit==1.0.1 transformer-lens==2.18.0`, then
   `numpy==1.26.4 pandas==2.2.3`, then restart the runtime. Colab's current pandas
   is a numpy-2 build and pip no longer downgrades it alongside numpy.

## The one rule that governs this session

**No discovery cell runs until the reduced grid is pre-registered.** Rule 6. The
plan is committed with a timestamp first, results are looked at second.

## Do these in order

### 1. Redo the grid arithmetic from `configs/sweep.yaml`

The earlier "252 cells, about 18 hours" estimate is **not trustworthy and must
not be reused.** Two time estimates were wrong this week, both by extrapolating
from an inner loop rather than timing something end to end.

The correction that matters: **metric and threshold are applied post hoc to
banked rankings.** That is how 1,540 discovery cells became 18,480
specifications. They cost nothing in GPU time. Discovery cost is

    objectives x ablation-corruption x prompt_variant x seed

so seeds are the cheap lever and every axis that enters discovery is expensive.
`LOGIT_MSE_GRAD_PRUNE_ALGO` does not execute and contributes nothing, so six
objectives, not seven. IEG-50 runs at roughly 200 s against EAP's 45 s on an L4,
measured for GPT-2 small; Pythia-160m is 1.3x the parameters and the scaling is
**INFERRED, not measured**. Time one cell end to end before committing a budget.

### 2. Decide the grid. Research lead's call, not the implementer's

The live question is how far seeds drop. Reducing an axis to a single level
removes it from the space, which changes what `F` means and makes the replication
`F` non-comparable to the headline 0.7316. That is a design consequence, not a
budget one, and it should be decided knowingly rather than fall out of a runtime
target.

Both outcomes must be writeable before the run. Rule 6 of the programme brief:
draft both abstracts. If Pythia's `F` is comparable, the finding generalises
across architecture family. If it is much lower, the paper reports that circuit
multiplicity is model-dependent, which is a result and not a failure. If only one
direction is writeable, the grid is wrong.

### 3. Pre-register, then run

Use the `preregistration` skill. The plan must fix, before any cell runs: the
grid, the seeds, the dataset size and whether it is re-calibrated or inherited
from GPT-2 (inherited needs a `DEVIATIONS.md` entry), the primary outcome, and
what counts as replication rather than refutation.

`n_prompts: 256` was selected for GPT-2 by the committed calibration rule.
Re-running that rule for Pythia costs time. Inheriting it is defensible and must
be declared, not assumed.

### 4. Only then, fold into the paper

The replication is a section, not a rewrite. The abstract's scale limitation
softens from "one model and one task" to whatever was actually shown, and not one
word further.

## What the replication must not be written as

It measures specification instability on a second model. It does **not** measure
mechanism equivalence across models. Gate P establishes that Pythia-160m performs
IOI. It establishes nothing about whether it does so with an IOI-like circuit,
and no sentence should imply otherwise.

## Still open, still non-blocking

- Seam smoke test over every axis level. Seven defects have lived in the P1 to
  auto-circuit seam; none was caught by the torch-free suite.
- EMS cross-check on the balanced five-operator block.
- FINE and `phi_affected` null, needs an attention cache the sweep never wrote.
- Annex III point 2, the one provision of ten not re-checked against the
  consolidated text.
- `scripts/repair.py` reloads every `result.json` before its skip check.

## The rule that earned its place this week

A constraint written in a design document is not a constraint enforced by
anything. The 32,347 figure lives in an assertion in `tests/test_graph.py`, not
in a comment, because that is the only version of it that fails when it is
violated.
