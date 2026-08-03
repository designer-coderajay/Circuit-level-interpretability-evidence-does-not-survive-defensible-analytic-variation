# P1 research log

Dated, append-only. Never edit a past entry; append a correction.

Anything that would need to be remembered in November goes here the day it
happens. The chat sessions will not remember. Cross-paper information travels
through this file and nowhere else.

---

## 2026-08-03 — Setup, verification, and one design change

**Ran.** Environment audit, citation re-verification, novelty search, repo
scaffold, core statistics module with tests.

### Environment

Development sandbox is 4 CPU cores, 3GB RAM, no GPU, aarch64, Python 3.10.12.
VERIFIED by inspection. The sweep cannot run here. Harness builds and tests
here; the sweep runs on a rented GPU.

auto-circuit 1.0.1 VERIFIED on PyPI, requires Python >=3.10,<4.0. Wheel
downloaded and its source read directly.

### Citations

All nine arXiv IDs in the brief re-verified by fetching `arxiv.org/abs/<ID>`.
All nine resolve to the stated titles. Details and remaining gaps in
`docs/CITATION-LEDGER.md`.

Two things the brief got materially right and one it got loose:

- 2407.08734 confirmed as Miller, Chughtai, Saunders, CoLM 2024. It ships
  `github.com/UFO-101/auto-circuit`, which the brief did not mention and which
  changes the build plan.
- The brief's name-only "Méloux et al. 2025" resolves to **2502.20914**,
  *Everything, Everywhere, All at Once: Is Mechanistic Interpretability
  Identifiable?* This is the foundation of P1's non-identifiability premise and
  it was previously uncited by ID.
- Six references remain name-only and unverified: Wang (IOI), Conmy (ACDC),
  Nanda (attribution patching), Steegen (multiverse), Simmons (researcher
  degrees of freedom), Simonsohn (specification curve). None may be cited until
  resolved to identifiers and fetched.

### Novelty

Searched for prior work connecting multiverse or specification-curve analysis to
EU AI Act conformity claims. **Found none.** The novelty claim survives this
pass. Nearest regulatory-side work is 2604.09628 on model-agnostic XAI against
AI Act requirements, which is related work rather than a threat.

Three papers surfaced that were not in the brief and need fetching: 2602.16823
(provable circuit-discovery guarantees, potential threat), 2607.19317
(CircuitKIT), 2604.09628.

### The design change

**2606.06267**, *Many Circuits, One Mechanism* (Bayat Makou, Niu, Dutta,
Gurevych, UKP Lab TU Darmstadt, submitted 4 Jun 2026). ID, title, and authors
VERIFIED. Reported findings RECALLED from search summaries only, not yet read.

Per those summaries it reports "phantom specialization": structurally distinct
circuits implementing the same computation, with a shared core recovering at
least 99% of circuit performance.

This threatens P1 directly. P1's claim map is structural. If structural
difference does not imply functional difference, a high flip rate does not
establish that the filed evidence is unstable in a way that matters, and H1 and
H2 do not support the conclusion as originally framed.

**Decision (Ajay, 2026-08-03): add a functional-equivalence arm.** For circuit
pairs with low Jaccard overlap, run interchange interventions to test functional
equivalence. Report structural instability, functional instability, and the gap
between them. The gap becomes the contribution: Annex IV regulates the
structural description while the safety-relevant property is functional, and a
conformity assessment body reading a filing cannot tell which it has been given.
This goes in the abstract, not section 7.

### Other decisions

- Instrument is auto-circuit 1.0.1 verbatim. Never modified. Extensions live in
  `src/p1/` and are additive and separately reported.
- glassbox-mech-interp is not the primary instrument. Testing one's own tool
  invites the objection that the instability is the implementation.

### Built

`src/p1/multiverse.py` and `tests/test_multiverse.py`. 35 tests, all passing,
verified by running `python3 -m pytest tests/ -q` in this session.

The load-bearing test establishes numerically that the O(N) closed form

    F = 1 - sum_c n_c(n_c - 1) / (N(N - 1))

equals the O(N^2) pairwise definition of the flip rate, across 2,000 randomised
cases. A second test cross-checks it against the Gini-Simpson form quoted in the
paper, which is algebraically distinct, so agreement is evidence the manuscript
algebra is right. Boundary cases at F = 0 and F = 1 are asserted separately.

One test failed on first run. The implementation was correct; the test's
reasoning was wrong. With three pairwise-disjoint singleton circuits the
achievable bootstrap means are exactly {0, 1/3, 1}, which I had wrongly assumed
would be off-lattice. Replaced with a valid discriminator: with disjoint
circuits every pair has J = 0, so pair-resampling could only ever return 0,
while specification-resampling returns positive values. Recorded because it is
the kind of error that would otherwise recur.

### Deltas from the brief, all open

Full statements in `docs/DESIGN-DELTAS.md`.

- **D1** auto-circuit ships seven ablation operators, not four. "Mean" is five
  distinct operators, and which mean is an undocumented researcher degree of
  freedom. Optimal ablation is not in auto-circuit at all.
- **D2** Sufficiency and comprehensiveness are not in auto-circuit's metric
  registry. They are ERASER-style metrics and would need an additive extension.
- **D3** Grid is 2,160 under the brief, 3,780 under seven operators. Arithmetic
  verified. **Feasibility on one 24GB GPU in the 10 to 24 August window is
  unmeasured.** The brief asserts it; nothing supports it. Do not repeat the
  claim until the smoke config produces a timing number.
- **D6** 2407.08734 has different titles on arXiv and at CoLM. Cite the CoLM one.

### Next

1. Read 2606.06267 in full. It gates the pre-registration and could move a kill
   gate.
2. Read 2407.08734 in full. Kill criterion: if it already contains a
   downstream-claim analysis, drop or reframe.
3. Read Regulation (EU) 2024/1689 Article 11 and Annex IV from EUR-Lex. The
   whole regulatory premise rests on text nobody in this project has read yet.
4. Resolve D1 and D2 with Ajay.
5. Build the smoke config and measure per-run cost. Until that number exists,
   the schedule is unfounded.

---

## 2026-08-03 (later) — Device support verified, timeline written

**VERIFIED** by grepping auto-circuit 1.0.1 source: the library contains exactly
one device-selection line,

    auto_circuit/tasks.py:157   device_str = "cuda" if t.cuda.is_available() else "cpu"

and **zero references to MPS**. Consequence: on Apple Silicon,
`torch.cuda.is_available()` is False and the library runs on CPU. The M-series
GPU is not used.

This is not fixable within the rules. Adding MPS support means editing
`tasks.py`, which is part of the instrument under test. Rule 2 forbids it.

**Consequence for tooling.** The Mac is the development machine: code, tests,
git, writing, and a first order-of-magnitude timing on CPU. The sweep runs on a
rented CUDA box over VS Code Remote-SSH. Google Colab is rejected for the sweep:
ephemeral filesystem and session timeouts make an environment hash meaningless
and a multi-hour resumable job fragile, which breaks rule 8.

**Notebooks are scoped to `analysis/` only.** They read committed `results/` and
produce figures. A number that first appears in a notebook cannot be traced to a
config, a seed, and an environment hash, so no notebook may produce a result
that enters the paper.

**Written.** `docs/TIMELINE.md`, with phases, three binding gates, critical path,
and a drift comparison against the brief's schedule.

**Correction to the brief's schedule, recorded as drift.** The brief scheduled
pre-registration for 24 to 31 Aug, after the 10 to 24 Aug sweep. That ordering
violates standing rule 3. Corrected: the plan locks 16 Aug, before the sweep.

---

## 2026-08-03 (Phase 1) — Gate 1 PASSED. H1 must be demoted.

Read 2407.08734 and 2606.06267 from the arXiv HTML. Both abstracts and section
structures VERIFIED verbatim. Body sections of 2606.06267 past section 3 were not
in the fetched portion and remain unread.

### Gate 1 verdict: PASS. Neither paper performs a downstream-claim analysis.

Term counts over the full fetched text of each paper:

| Term | 2407.08734 | 2606.06267 |
|---|---|---|
| regulat / AI Act / complian | 0 | 0 |
| audit / conformity | 0 | 0 |
| technical documentation | 0 | 0 |
| stakeholder / legal / certif / polic | 0 | 0 |
| multiverse / specification curve | not checked | 0 |
| researcher degrees of freedom | not checked | 0 |
| filab | not checked | 0 |

The regulatory propagation and the filability criterion are untouched by both.
**The kill criterion is not triggered. P1 proceeds.**

### But the paper must be repositioned, and H1 demoted

From the 2606.06267 abstract, VERIFIED verbatim:

> "Repeated extractions within the same frequency band further suggest that
> discovery algorithms sample from an equivalence class of valid subgraphs
> rather than recovering a unique mechanism."

> "Our results show that structural differences between circuits are not
> sufficient evidence for distinct mechanisms, and that exposing this requires
> edge-level evaluation and cross-condition transfer tests."

Also verified: 75 circuits, Literal Sequence Copying, four token-frequency bands
plus a control, five Pythia models 70M to 1.4B; "a core shared across most bands
recovers at least 99% of circuit performance"; "source-level evaluation inflates
apparent faithfulness, while edge-level evaluation reveals the many-to-one
mapping from structure to function". Code released at
https://github.com/UKPLab/arxiv2026-phantom-specialization

Three consequences.

1. **H1 is no longer a contribution.** That circuit discovery returns one of
   many valid subgraphs is now established in print. P1 can still measure it on
   a new axis, analytic specification rather than input statistics, but must
   present it as replication and premise, not as a finding.

2. **The inference from structural instability to "the evidence is worthless"
   is explicitly refuted in the literature.** P1 cannot make that inference.
   Any draft that does hands a reviewer the sentence above.

3. **Edge-level evaluation must be primary, not a secondary variant.** The brief
   treats the edge-level run as an extra. Their result says source-level
   inflates apparent faithfulness.

### Why this makes P1 stronger

Their finding is P1's premise, not P1's competitor. If circuit discovery samples
from an equivalence class of functionally equivalent subgraphs, then Annex IV
asks a provider to file one arbitrary member of that class as *the* description
of the system's logic. That is a sharper regulatory claim than instability, and
it is not available to anyone who has not connected the two literatures.

### 2407.08734, what was actually verified

Section 3.1 enumerates **five** ablation-methodology dimensions, not one:
3.1.1 circuit granularity, 3.1.2 ablation component type and model views,
3.1.3 ablation value, 3.1.4 token positions, 3.1.5 ablation direction.

Ablation values named in 3.1.3: zero, Gaussian noise on token embeddings,
resample, and mean. Verbatim: **"We focus on Mean and Resample Ablations in this
work."** So two of four were crossed. Mean ablation carries a further hidden
choice, verbatim: "an additional choice in the size of the mean ablation
dataset". Zero and Gaussian noise are noted to "take the model significantly out
of distribution, producing noisy outputs".

Section 3.2, on metrics, verbatim: **"In this work we will focus on the metrics
used by the respective authors of the circuits that we study, but note these
choices are also in general free."** They did not cross the metric dimension at
all. This is a documented, quotable gap that P1 fills.

Useful IOI grounding, verbatim: the IOI circuit "is specified as an edge-level
circuit, but Wang et al. (2023) evaluate its faithfulness via a node-wise
ablation methodology". Clean distribution is 15 sentence templates in ABBA or
BABA order; corrupt is the ABC distribution. Wang et al.'s faithfulness metric
is logit difference recovered.

Author-year pairs now confirmed from a primary bibliography, still needing
arXiv IDs: Wang et al. 2023 (IOI), Conmy et al. 2023 (ACDC), Meng et al. 2022,
Vig et al. 2020, Zhang and Nanda 2024, Hanna et al. 2023, Heimersheim and
Janiak 2023, Olsson et al. 2022, Cammarata et al. 2021, Makelov et al. 2023.

### New delta

**D7. The brief's positioning sentence is unsupported.** The brief says of
2407.08734: "they establish that one dimension matters; you measure the crossed
space." They survey five dimensions. P1's differentiation is the regulatory
propagation and the filability criterion, and nothing else. Do not write the
crossed-space claim as the differentiator.

### Not obtained

The interchange-intervention protocol in section 5.3.2 of 2606.06267. The HTML
fetch truncated before the body of section 5. Their released code is the better
source for reproducing the protocol verbatim.

### Next

1. Ajay decides the repositioning and the fate of H1.
2. Pull the interchange protocol from the UKPLab repo.
3. Read Annex IV from EUR-Lex. Still unread, still load-bearing.
