# P1 timeline

Source of truth for schedule. Update the day something slips, not at the end of
the week. Original brief schedule is preserved at the bottom so drift is visible.

Today: **3 August 2026.** Phase 1 active.

---

## Phases

| # | Phase | Dates | Status | Exit condition |
|---|---|---|---|---|
| 0 | Setup | 3 Aug | **done** | Repo scaffolded, citations verified, statistics core tested, commit `e3ae067` |
| 1 | Read and decide | 3 to 9 Aug | **active** | 2606.06267, 2407.08734, and Annex IV all read in full. D1 and D2 resolved. |
| 2 | Harness and smoke | 7 to 13 Aug | pending | auto-circuit integrated, `phi` implemented at three granularities, per-run cost measured |
| 3 | Pre-register | 12 to 16 Aug | pending | Grid frozen, both abstracts drafted, plan committed and tagged on a public remote |
| 4 | Sweep | 16 to 28 Aug | pending | Main grid, random baseline, and interchange arm complete on rented GPU |
| 5 | Analysis and red team | 28 Aug to 2 Sept | pending | Specification curve, bootstrap CIs, variance decomposition, `p1-red-team` run and answered |
| 6 | Write | 2 to 10 Sept | pending | arXiv 10 Sept |
| 7 | FAccT 2027 | October | pending | Submission, 14 pages excluding references |

Phases 1 and 2 overlap deliberately. Reading gates the design decisions; the
harness can be built against the parts that are already settled.

## Binding gates

**Gate 1, 9 August. Kill gate.**
Does 2407.08734 or 2606.06267 already propagate instability to a downstream
claim? If either does, drop or reframe P1 the same day. This is the whole
novelty argument and it rests on two papers nobody in this project has read in
full.

**Gate 2, 11 August. Feasibility measured.**
The smoke config must produce a real per-run wall clock and peak memory. The
brief's claim that 2,160 runs fit on a single 24GB GPU has nothing behind it.

- If the measured cost fits the 16 to 28 Aug window, proceed with the full grid.
- If it does not, cut the grid using a documented fractional factorial **before**
  Gate 3. Pruning after the pre-registration is locked is a deviation; pruning
  before it is a design decision.

**Gate 3, 16 August. Pre-registration locked.**
Commit hash and UTC timestamp recorded, tag pushed to a public remote. No pooled
result may be looked at before this. Non-negotiable.

## Critical path

Gate 2 is the decision point that determines whether 10 September survives.
Everything upstream of it is reading and building; everything downstream is
committed. The grid size is the only real lever, and it can only be pulled
before Gate 3.

## Known schedule risk

- **Slack is thin.** Five working days between the end of analysis and the arXiv
  date. One failed sweep consumes all of it.
- **The functional-equivalence arm was not in the original plan.** It was added
  3 Aug in response to 2606.06267. It adds interchange-intervention compute to
  Phase 4 and design work to Phase 2, and neither has been costed.
- **Grid may be 3,780 rather than 2,160** if all seven auto-circuit ablation
  operators are used. See `docs/DESIGN-DELTAS.md` D1.
- **Reading load in Phase 1 is heavy.** 2606.06267 alone is 90 pages with 53
  figures, and the regulation is primary legal text.

## Where to run what

| Work | Machine | Why |
|---|---|---|
| Code, tests, git, writing | VS Code on the Mac | Repo lives here. Statistics layer needs no GPU. |
| Smoke config, first timing | Mac, CPU | Slow but sufficient to get an order of magnitude before renting. |
| Full sweep, interchange arm | Rented CUDA GPU, VS Code Remote-SSH | **VERIFIED 2026-08-03:** auto-circuit 1.0.1 contains a single device line, `"cuda" if t.cuda.is_available() else "cpu"`, and zero MPS references. On Apple Silicon it falls back to CPU. Adding MPS support would mean editing `tasks.py`, which is the instrument under test and must not be modified. |
| Figures from committed results | Notebook in `analysis/` | Notebooks read `results/`. They never produce them. |

## Original brief schedule, for drift comparison

| Dates | Work |
|---|---|
| 3 to 10 Aug | Harness build |
| 10 to 24 Aug | Full specification sweep |
| 24 to 31 Aug | Pre-register, then analyse |
| 1 to 10 Sept | Write, arXiv 10 Sept |
| Oct | FAccT submission |

**Drift so far:** the brief put pre-registration after the sweep. That ordering
is wrong under standing rule 3 and has been corrected: the plan locks on 16 Aug,
before the sweep starts. The sweep window moved from 10 to 24 Aug to 16 to 28
Aug to make room for reading and for the feasibility measurement.
