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
