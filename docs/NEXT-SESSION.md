# Next session: v2, the Pythia-160m replication

Written 2026-08-13, after v1 went to arXiv. Everything below is blocked on one
thing only: **a GPU**. No design decisions remain open.

## State

**v1 submitted.** arXiv `submit/7948759`, status `submitted`, primary `cs.AI`.
12 pages, 1 figure, 7 tables, 15 references. Repository is now public.

**The replication is pre-registered and the harness is verified.** What is left
is compute and analysis, not design.

| | |
|---|---|
| plan | `preregistration/PLAN-REPLICATION.md`, tag `prereg-p1-replication` |
| config | `configs/replication_pythia.yaml`, 924 cells, 11,088 specifications |
| harness | VERIFIED end to end on Pythia-160m: `1/1 ok`, 8 of 12 specs produced a claim |
| budget | 15.5 h measured, cut line 23.5 h |

## Do this first

1. **Cross-list the arXiv paper** once announced: `cs.LG` and `cs.CY`, from the
   Cross list action on your account page.
2. **Delete `submit/7942283`**, a stale incomplete draft.
3. **Copy `requirements-confirmatory.lock.txt` into the repo.** 719 lines, still
   only on Drive. It has been on this list since 08-11 and it cost a session on
   08-12 when a fresh Colab image needed the pins rederived.

## Running the grid

Six cells. Repo is public now, so the clone needs no token.

**CELL 1**
```python
!pip install -q auto-circuit==1.0.1 transformer-lens==2.18.0
!pip install -q "numpy==1.26.4" "pandas==2.2.3"
```
Then **Runtime > Restart session.** Mandatory: numpy changed under a kernel that
already imported it.

**CELL 2**
```python
from google.colab import drive
drive.mount('/content/drive')
%cd /content
!rm -rf /content/p1
!git clone --depth 1 https://github.com/designer-coderajay/p1-circuit-multiverse.git /content/p1
%cd /content/p1
!git log --oneline -1
!nvidia-smi --query-gpu=name --format=csv,noheader
```

**CELL 3**
```python
%cd /content/p1
!python3 scripts/sweep.py --config configs/replication_pythia.yaml --dry-run
```
Expect `specifications 11,088`, `discovery cells 924`, and `already complete`
climbing across sessions.

**CELL 4**
```python
%cd /content/p1
!python3 scripts/sweep.py --config configs/replication_pythia.yaml \
    --out /content/drive/MyDrive/p1_replication/results
```

**CELL 5**, progress, safe in a separate cell at any time
```python
import json, pathlib
R = pathlib.Path('/content/drive/MyDrive/p1_replication/results')
m = [json.loads(p.read_text()) for p in R.glob('*/manifest.json')]
ok = sum(x.get('status') == 'ok' for x in m)
print(f"cells {len(m):>4} of 924   ok {ok}   failed {len(m)-ok}")
```

### Two things that must be checked, not assumed

**The first line of output must read `device Tesla T4` or better.** On
2026-08-13 Colab silently allocated a CPU runtime and a single cell took 9m05s
against about 50 s. At CPU speed the grid is 138 h. If it says `device cpu`, stop
immediately.

**Nothing from a CPU run may enter the results tree.** The confirmatory sweep has
a single environment fingerprint across all 1,320 cells, verified rather than
asserted, and that property is worth keeping.

### Budget checkpoints, from the locked plan section 8

Measured per cell on a T4: EAP 42.3 s, IEG-50 209.2 s, evaluation 36.5 s.

- **Checkpoint 1**, after 20 cells, all EAP. Extrapolated total above **23.5 h**
  means cut seeds from three to two. That is the only pre-registered cut.
- **Checkpoint 2**, on reaching `INTEGRATED_EDGE_GRADS`, which runs last. The
  4.4x IEG-to-EAP ratio is assumed from GPT-2, not measured here.
- Either cut goes in `DEVIATIONS.md` with the measured rate that triggered it.
- **No other axis may be pruned, and seeds may not go below two.**

Free-tier Colab reclaimed the runtime after about 1 h 40 m on 08-13, not the
advertised 3 h 50 m. Expect several reconnects. Resume is per cell and writes to
Drive, so each drop costs the cell in flight.

## When the grid completes

**Do not compute `F` before it does.** Cells run in objective order, so a partial
`F` is an `F` over a non-random slice of the axis the paper leans on hardest.

Then, in order:

1. `scripts/analyse.py` against `results/replication_pythia`, mirroring the
   confirmatory run.
2. `scripts/jbar.py` and the null multiverse with `parallel_mlp=True`. The null
   must draw from Pythia's 32,347 edges, not GPT-2's 32,491.
3. Evaluate the replication criteria in `PLAN-REPLICATION.md` section 5.1: `F >
   0.20` with the CI lower bound above it, filability failing at all three
   tolerances, and both holding at COARSE and MEDIUM.
4. Check the three conditions in section 5.3 that would make the comparison
   uninterpretable: claim yield below 20 percent, a different class count moving
   the `1 - 1/k` ceiling, any objective beyond `LOGIT_MSE` failing to execute.
   **Report `F` as a fraction of its ceiling alongside the raw value regardless.**
5. Write the section. Both abstracts are already drafted in section 7 of the
   plan. Use whichever the data selects, and do not soften the other.

**The GPT-2 versus Pythia comparison is descriptive and carries no p-value.** The
two grids share the claim map, the task, the templates and six of seven axes.
Rule 3.

## Page budget for v2

v1 is 12 pages and you asked for 10 to 12. A replication section is roughly 1.5
pages, so something gives. Likeliest candidates: compress the multiverse-methods
paragraph in related work, move one of the seven tables to an appendix. Decide
after the result is in, when its actual size is known.

## Known gaps, in the order they will bite

- **The seam smoke test still does not exist.** Five defects reached a launched
  run on 08-12 and 08-13, all in the P1 to auto-circuit seam.
  `tests/test_scripts_static.py` now catches unresolved names, which is the cheap
  half. A 49-cell run over every objective by ablation would catch the rest, at
  about four minutes of GPU time.
- **`check_manuscript_numbers.py` reads `paper/manuscript.md`, not
  `paper/arxiv/main.tex`.** The file that went to arXiv was never covered by it
  until it was run manually with LaTeX normalisation on 08-13: 321 of 323, the
  two misses being `924` and `343`, both verified directly. **Point the checker at
  the tex before v2 ships.**
- **The GPT-2 effect of the 08-13 attribution change is NOT VERIFIED.** The new
  path should produce an identical token sequence on GPT-2, but that has not been
  run. No confirmatory number changes, because those are banked. If the
  confirmatory sweep is ever re-run, check this first.
- EMS cross-check on the balanced five-operator block.
- FINE and `phi_affected` null, which needs an attention cache the sweep never wrote.
- Annex III point 2, the one provision of ten not re-checked against the
  consolidated text.

## The scale question, and the one promising lead

The paper's remaining limitation after v2 is scale: both models are around 150M
parameters. Edge count grows roughly with blocks squared times heads, so GPT-2
medium is 7.1x the graph and Pythia-2.8b is 49x. Those are closed.

**Pythia-1b is the exception, if its shape is what I think.** Deep and narrow at
16 blocks by 8 heads gives 27,673 edges, *fewer* than GPT-2 small, for a model 6x
larger. Three caveats, in order of how badly they could sink it: the runtime
estimate scales only edge count and inherits a kernel-launch-bound finding
measured at 124M and 160M, which may not hold at 1B; VRAM is unmeasured, peak was
3.7 GB at 160M; and **the 16 by 8 shape is RECALLED, not verified.** If it is 16
by 16 the number roughly quadruples and the lead evaporates.

One CPU probe settles it, the same way Pythia-160m was settled on 08-12. Worth
doing before anyone writes a limitations paragraph claiming scale is out of reach.

## The rule that earned its place this week

Five defects in two days, every one in code the torch-free suite cannot execute,
and two of them were assumptions about library behaviour stated as fact. The
tokenizer probe on 08-12 passed because it called `to_tokens`; the loader calls
the raw tokenizer. **A probe that does not call the same function the instrument
calls is not a probe of the instrument.**
