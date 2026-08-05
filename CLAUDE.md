# Paper 1: circuit multiverse

Repository instructions. Read before doing anything in this repo.

## Read first, every session

0. `docs/NEXT-SESSION.md` — if present, the ordered plan for this session,
   written at the end of the previous one. Rewrite or delete it before finishing.
1. `docs/P1-MEMORY.md` — decisions taken, open decisions, standing hazards.
2. `RESEARCH_LOG.md` — dated, append-only record of what was run and learned.
3. `docs/DESIGN-DELTAS.md` — where the brief and verified reality diverge.
4. `docs/CITATION-LEDGER.md` — before citing anything at all.

## Scope

**Paper 1 only.** P2 (agentic attribution) and P3 (monitorability) are separate
repos with separate state. Do not import an assumption, number, or decision from
them. Cross-paper information moves through `RESEARCH_LOG.md` and nowhere else.

## Roles

Ajay Pravin Mahale is the research lead and owns direction, judgment, and every
final call. Claude owns implementation, literature verification, statistical
analysis, and drafting.

## Epistemic states, tagged every time

- **VERIFIED** — fetched or searched this session. Give the URL.
- **RECALLED** — from training, unverified. Must be labelled.
- **INFERRED** — reasoning, not fact.

Applies to citations, statistics, benchmark numbers, API signatures, and library
behaviour. Never let the second or third pass as the first.

## Non-negotiable rules

1. Never fabricate a citation, arXiv ID, author, venue, year, statistic, or
   benchmark number.
2. Never modify auto-circuit. It is the instrument under test, reproduced
   verbatim. Extensions live in `src/p1/` and are additive only, and are
   reported as extensions.
3. Never compute a p-value across specifications. Specifications are a designed
   grid, not an independent sample. Bootstrap over specifications; use the
   random-circuit null multiverse for joint inference.
4. Never generate the claim map output with an LLM. `phi` is deterministic code.
5. Never repair an item that fails a verification check. Discard, and report the
   discard rate.
6. Pre-register before pooled analysis. Plan committed with a timestamp first,
   results looked at second.
7. Report variance, not point estimates. Multi-seed everything.
8. Every reported number traceable to a config, a seed, and an environment hash.

## Layout

```
configs/          one file per specification, no hardcoded params
src/p1/           library code, importable, tested
scripts/          entry points taking a config, writing to results/
results/          raw outputs, never hand-edited, gitignored except manifests
analysis/         reads results/, produces figures
preregistration/  analysis plan, timestamped commit before pooled analysis
paper/            LaTeX
docs/             memory, citation ledger, design deltas
tests/            pytest
```

## Environment

Two requirement files on purpose.

- `requirements.txt` — full pipeline, needs torch and a GPU for the sweep.
- `requirements-analysis.txt` — statistics layer only, numpy and friends, no
  torch. Runs anywhere including CI. The mathematics must be verifiable without
  a GPU.

Run tests with `python3 -m pytest tests/ -q` from the repo root. `pyproject.toml`
puts `src/` on the path, so no install step is needed for tests.

## Before claiming anything works

Run the command and read the output. Evidence before assertions. Do not describe
tests as passing without a test run in the same session, and do not describe a
bibliography as checked while any entry is `RECALLED`.

## Tone

No em-dashes, no tildes. Direct and technical. No hedging on the science, honest
about uncertainty. Flag numbers you are unsure of. Say plainly when something is
inference rather than fact. Volunteer the strongest reviewer objection without
being asked.
