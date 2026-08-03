# Paper 1: Explanation Multiplicity and the Instability of Conformity Claims

Circuits are formally non-identifiable, and circuit faithfulness is sensitive to
the choice of ablation operator. The EU AI Act requires technical documentation
describing how a high-risk system reaches its decisions. If the explanation filed
as conformity evidence changes when a different competent analyst runs the same
tool with different defensible settings, the filing carries no evidential weight.
An audit means two auditors reach the same conclusion.

This repository measures how far an Annex IV claim moves across the space of
defensible analytic specifications, and whether that movement is distinguishable
from a size-matched random baseline.

## Status

Setup. No experimental results exist. See `RESEARCH_LOG.md`.

## Start here

- `CLAUDE.md` operating rules for this repo
- `docs/P1-MEMORY.md` decisions taken and open
- `docs/DESIGN-DELTAS.md` where the original brief and verified reality diverge
- `docs/CITATION-LEDGER.md` what has actually been verified
- `RESEARCH_LOG.md` dated, append-only

## Instrument

`auto-circuit` 1.0.1, the library released with the closest prior work
(arXiv:2407.08734, CoLM 2024). **Reproduced verbatim and never modified.** Any
extension lives in `src/p1/`, is additive only, and is reported separately.

## Tests

```bash
pip install -r requirements-analysis.txt
python3 -m pytest tests/ -q
```

The statistics layer has no torch dependency and needs no GPU, so the
mathematics is verifiable independently of the circuit pipeline.

## Licence and citation

Not yet set.
