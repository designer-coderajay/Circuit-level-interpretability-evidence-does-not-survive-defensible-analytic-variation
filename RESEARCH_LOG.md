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

---

## 2026-08-03 (checkpoint) — Annex IV read started, not finished

Session ended mid-task. Resume from here.

**State.** Committed through `2b53115`. 35 tests passing. Gate 1 passed.
Hypothesis structure revised (P0 / H2 / H3 / H4, see DESIGN-DELTAS D9).
Edge-level fixed as the confirmatory grid (D8).

**In progress: Regulation (EU) 2024/1689, Article 11 and Annex IV.**

EUR-Lex does not serve the legal text to a plain HTTP fetch. Three URL forms
were tried and all returned either empty or page chrome only:

    https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689
    https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689
    https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32024R1689

The ELI form `https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng` returns the
page shell with correct metadata (document date 2024-06-13, entry into force
2025-08-02, CELEX 32024R1689) but no body. The document is client-rendered.

A browser session was opened on the CELEX HTML URL and the text extraction was
not completed. **Resume by extracting the page text in the browser**, not by
retrying the plain fetch.

**What must be answered from the primary text, before any drafting.**

1. What exactly does Annex IV require in the description of the system? Quote
   the operative wording verbatim. The paper currently assumes it asks for a
   description of the logic that a discovered circuit could serve as evidence
   for. That assumption is **unverified** and it carries the whole regulatory
   premise.
2. Does Article 11 or Annex IV say anything about the form, reproducibility, or
   evidential standard of that description? If it does, the filability criterion
   should be stated in the regulation's own vocabulary rather than invented.
3. Which Annex IV paragraph numbers does the claim map target? The brief says
   "Annex IV sections 2 and 3" and that numbering is unverified.
4. Is a mechanistic circuit even an admissible form of that description, or does
   Annex IV ask for something a circuit diagram does not answer? If the latter,
   the propagation argument needs rebuilding and that is a same-day reframe.

**Do not** cite artificialintelligenceact.eu or any summary for these. Primary
text only. The AI Act Service Desk at ai-act-service-desk.ec.europa.eu is an
official Commission source and is acceptable as a cross-check, but the operative
quotes must come from the Official Journal text.

**Other open items, unchanged.**

- D1 and D2 still open. The evidence to close both is now in the log: 2407.08734
  names four ablation values and crossed two, and declined to cross metrics at
  all. Those two quotes make the ablation and metric axes defensible.
- Interchange protocol still unread. Better source is the released code at
  `github.com/UKPLab/arxiv2026-phantom-specialization`, not the paper prose.
- Feasibility still unmeasured. Gate 2 has not been approached.

---

## 2026-08-03 (Phase 1 cont.) — Annex IV read. Premise survives, target moves.

Annex IV retrieved in full from the AI Act Service Desk,
`ai-act-service-desk.ec.europa.eu/en/ai-act/annex-4`, an official Commission
site run by DG CNECT which states it reproduces the official version of
13 June 2024. EUR-Lex would not serve the text to a plain fetch and a browser
extraction failed on a dropped connection. **This is a Commission rendering, not
the OJ text.** Cross-check every quoted string against the OJ before it enters
the manuscript. Full analysis in `docs/ANNEX-IV.md`.

**Verdict: the regulatory premise survives.** Annex IV does require a
description of system logic. But P1 has been aiming at the wrong paragraph.

Section 2(b) contains "the general logic of the AI system and of the
algorithms", which is the phrase the premise rested on. Read in frame, 2(b) is
about **design specifications**: what the provider designed, their rationale,
their assumptions, their design choices. A discovered circuit is not a design
specification. Resting on 2(b) alone invites a correct and fatal objection.

The real hooks are **2(e)** and **3**, which carry the same concept in two
tenses: "an assessment of the technical measures **needed** to facilitate the
interpretation of the outputs" and "the technical measures **put in place** to
facilitate the interpretation of the outputs". That is where an interpretability
artefact is actually filed, and it is about interpreting outputs, which is what
a circuit purports to do.

**Section 4 was missed entirely by the brief**: "A description of the
appropriateness of the performance metrics for the specific AI system." A
standalone requirement to justify metric appropriateness. P1's specification
space has a metric dimension. If the filed claim moves when the metric moves,
section 4 is load-bearing and its adequacy has never been measured. This is the
cleanest available justification for the metric axis.

**Section 7** gives the framing slot: where no harmonised standard has been
applied, a detailed description of the solutions adopted is required. There is
no harmonised standard for mechanistic interpretability evidence, and the
filability criterion is exactly what such a standard would specify.

**The chapeau creates one objection that must be answered in the paper**, not
left to a reviewer: the documentation is required "as applicable to the relevant
AI system". A provider can argue circuit-level interpretability is not
applicable. The answer is that 2(e) and 3 are not optional for a high-risk
system carrying an Article 14 human-oversight requirement, so something must be
filed, and P1 is about the evidential quality of whatever is filed rather than
about compelling a particular technique.

### Required changes

1. Retarget the claim map from 2(b) to **2(e) and 3**. Keep 2(b) as context.
2. Add **section 4**, metric appropriateness, to the paper.
3. Frame the filability criterion against **section 7**.
4. Answer "as applicable" head-on.

### Still outstanding

- **Article 11 unread.** Fetch timed out. It governs the obligation to draw up
  and maintain the documentation and is referenced by the Annex IV chapeau.
- **Article 13(3)(d) and Article 14 unread.** Both are cross-referenced from
  2(e) and 3, and they define "facilitate the interpretation of the outputs".
  The claim map should use the regulation's own vocabulary, so these are needed
  before phi is designed.
- OJ cross-check of all quoted strings.

### Repository is local only

`git remote -v` returns empty. Five commits, 316K in `.git/`, branch `master`,
nothing pushed anywhere. **A public remote is required before Gate 3 on 16 Aug**,
because a pre-registration timestamp attested only by a local clock is not
evidence. Decision on remote and attestation route still open.

### Decisions (Ajay, 2026-08-03)

**Claim map retargeted.** `phi` maps a circuit to a statement under **Annex IV
2(e) and 3**, the technical measures to facilitate interpretation of outputs.
Section 2(b) becomes context, not the hook, because it is a design-specification
requirement and a discovered circuit is not a design specification. **Section 4,
metric appropriateness, becomes a second claim target** and is the justification
for the metric axis of the specification space. See `docs/ANNEX-IV.md`.

**Remote and attestation.** Private GitHub repo now for backup and history.
Embargoed OSF registration at Gate 3 for an independent, third-party-attested
timestamp with a DOI and no disclosure. Both made public at arXiv on 10 Sept.
OSF is the norm in the multiverse and specification-curve literature P1 borrows
from, so it is idiomatic for the venue as well as sufficient for the claim.

---

## 2026-08-03 (Phase 1 cont.) — D1 and D2 closed, D12 opened

**D1 closed (Ajay).** Confirmatory grid uses **all seven auto-circuit ablation
operators** verbatim. Optimal ablation and Gaussian noise are dropped; neither
is implemented by the instrument. Five of the seven are mean variants, and
2407.08734 section 3.1.3 names the mean-dataset-size choice without crossing it,
so P1 quantifies a degree of freedom the closest prior work flagged and left
unmeasured.

**D2 closed (Ajay).** ERASER sufficiency and comprehensiveness are implemented
in `src/p1` as an additive extension that never edits auto-circuit, and enter
the main grid alongside native metrics. Justification: 2407.08734 section 3.2
declines to cross the metric dimension and calls the choice "in general free",
and Annex IV section 4 requires "a description of the appropriateness of the
performance metrics for the specific AI system".

**Built.** `src/p1/spec.py` and `tests/test_spec.py`. 59 tests total, all
passing, verified by running the suite in this session.

`Specification.spec_id` is a truncated SHA-256 of a canonical JSON encoding,
deliberately not Python's built-in `hash`, which is salted per process and would
give different ids in the sweep run and the analysis run. A test spawns fresh
interpreters under three `PYTHONHASHSEED` values and asserts the id is
unchanged, and a second test pins one known literal so any change to the field
set or encoding fails loudly instead of silently renaming every result on disk.

**D12 opened, blocking.** Encoding the grid exposed that the metric axis
conflates the discovery objective with the evaluation metric. Verified from
source: ACDC takes `faithfulness_target` restricted to kl_div and mse;
mask_gradient exposes twelve objective combinations; the `prune_metrics`
registry is separate and post-hoc. An evaluation metric does not change `C(s)`,
so it cannot change `phi(C(s))`, so as specified the metric axis would produce
zero claim variation at four times the compute. Unless `tau` is defined relative
to a metric, in which case it does. Full statement in `docs/DESIGN-DELTAS.md`
D12. The 3,780 grid figure and `METRICS` in `src/p1/spec.py` are provisional
until this is resolved.

**D12 closed (Ajay, 2026-08-03): metric-relative tau.**

`tau` is defined as **the smallest circuit recovering `(1 - tau)` of metric `m`
measured on the full model**. Consequences:

- `(m, tau)` jointly select the cut point on the prune-score ranking, so `m`
  genuinely changes `C(s)` and the metric axis is live rather than inert.
- All four metrics stay in the grid. The confirmatory grid remains 3,780.
- The definition matches how a provider would actually justify a filing under
  Annex IV section 4, because the metric is what defines when the circuit is
  good enough to file.

**This definition must be stated in the pre-registration verbatim.** It is a
researcher degree of freedom in its own right: absolute `tau` (a fixed edge
count) is equally defensible and appears in the literature, and choosing between
them changes whether the metric axis carries variance at all. Report the choice
and its rationale in the paper rather than letting a reviewer discover it.

**Consequence for the harness.** Circuit discovery must produce a prune-score
ranking once per `(algorithm, a, d, P, r)`, after which the `(m, tau)` cut is
cheap post-hoc selection on that ranking. The sweep therefore does **not** need
3,780 independent discovery runs. It needs one ranking per discovery
configuration, with the metric and threshold applied afterwards. This is a large
saving and the smoke config must measure the ranking cost, not the full-grid
cost. INFERRED from the auto-circuit API structure, **not yet verified by
running it.** Verify before relying on it for the schedule.

---

## 2026-08-03 (Phase 1 cont.) — Articles 13 and 14 read. phi is unblocked.

Both retrieved in full from the AI Act Service Desk, same official Commission
source and same caveat: a Commission rendering, not the OJ text. Full analysis
appended to `docs/ANNEX-IV.md`.

**The chain is complete and it is a four-link chain, all verified:**

Article 13(1), the system must be "sufficiently transparent to enable deployers
to interpret a system's output" -> Article 13(3)(d), instructions for use must
contain "the technical measures put in place to facilitate the interpretation of
the outputs" -> Article 14(4)(c), overseers must be enabled "to correctly
interpret the high-risk AI system's output, taking into account, for example,
the interpretation tools and methods available" -> Annex IV 2(e) and 3, the same
object entering the technical documentation in two tenses.

The identical phrase appears in three operative places. It is not incidental.

**Article 14(4)(c) is the sentence phi should be built on.** Three reasons. The
standard is "correctly interpret", correctness rather than availability. It
explicitly names "the interpretation tools and methods available", which is
where circuit discovery sits, and unlike Annex IV 2(b) it is not framed as a
design specification. And the beneficiary is a natural person assigned human
oversight, not an auditor.

**Restate the filability criterion in this vocabulary.** `pi_star >= 1 - alpha`
becomes a criterion for when an interpretation method supports *correct*
interpretation rather than merely *available* interpretation. That is the
regulation's own distinction and it is much stronger than inventing one.

**New argument, not in the brief.** Article 14(4)(b) names **automation bias**
explicitly, as something oversight must guard against, "in particular for
high-risk AI systems used to provide information or recommendations for
decisions to be taken by natural persons". An unstable explanation carrying the
authority of a mechanistic circuit could increase over-reliance rather than
reduce it. This connects P1 to the programme thesis that confidence does not
track faithfulness. Worth a discussion paragraph, but do not overclaim: P1
measures claim instability, not deployer behaviour.

**Article 14(3)** requires the oversight measures to be identified before the
system is placed on the market. The analytic choices P1 varies are therefore
made once, in advance, by one analyst, and then filed. That is exactly the
situation in which specification instability matters and is invisible in the
filing.

**Newly surfaced and unread: Article 86, "Right to explanation of individual
decision-making."** Seen in the table of contents only. If it creates an
individual right to an explanation of a specific decision, it is a fourth and
possibly stronger hook and it changes who the explanation is for. Read before
drafting. **Article 11 still unread**, two attempts, one timeout.

**D10 is now partially closed.** Articles 13 and 14 read; 11 and 86 outstanding.
phi is unblocked for design: the three granularities should be granularities of
the regulation's own statement form, not of an arbitrary structural tuple.
Drafting the sentence templates is the next design task.

---

## 2026-08-03 (Phase 1 cont.) — Article 86 read. The loop closes.

Retrieved in full, same Commission source and same caveat. Analysis appended to
`docs/ANNEX-IV.md`.

**Article 86(1) puts the explanation duty on the deployer**, who can only pass on
what the provider supplied under Article 13(3)(d). That closes a four-link loop,
every link now verified:

provider picks one specification s before market placement (Art 14(3)) -> files
the claim in the technical documentation (Annex IV 2(e), 3) and supplies it to
the deployer (Art 13(3)(d)) -> deployer must enable overseers to "correctly
interpret" (Art 14(4)(c)) -> affected person has a right to "clear and meaningful
explanations" from that deployer (Art 86(1)).

**An arbitrary analytic choice made once inside the provider propagates to an
individual's right to an explanation of a decision about them.** If phi(C(s))
moves across S, the explanation an affected person receives depends on a
researcher degree of freedom they never see and cannot contest. That is a much
stronger claim than instability, and it is a FAccT-shaped argument.

**Two qualitative standards now in hand**, neither satisfied by merely producing
an artefact: "correctly interpret" (14(4)(c)) and "clear and meaningful"
(86(1)). The filability criterion speaks to exactly that gap.

**Scope limits that must be stated, not buried.** Annex III systems only and
expressly not point 2 of Annex III, which is **unverified**; only decisions with
legal effects or similarly significant effect; disapplied by Union or national
law exceptions under 86(2); and **subsidiary under 86(3)**, applying only where
the right is not otherwise provided under Union law. A legally trained reviewer
will raise GDPR Article 22 immediately. Address it first.

**The applied arm gains weight.** Creditworthiness assessment is **RECALLED, not
verified** to fall under Annex III. Verify the point number, and verify it is not
the excluded point 2, before describing the applied arm. If it holds, the BFSI
prototype becomes the case where all four links bind at once.

**New design question for phi.** There are now two candidate addressees with
different standards: a human overseer at the deployer under 14(4)(c), and an
affected person under 86(1). They are different documents and will not share a
flip rate. Whether phi targets one or both as separate claim maps is the next
decision.

**D10 status.** Articles 13, 14, 86 read. **Article 11 still unread**, three
attempts, one timeout. Annex III unread and now needed.

---

## 2026-08-03 (Phase 1 cont.) — Annex III verified. The applied arm binds.

Retrieved in full, same Commission source and caveat.

**Annex III point 5(b), verbatim:** "AI systems intended to be used to evaluate
the creditworthiness of natural persons or establish their credit score, with
the exception of AI systems used for the purpose of detecting financial fraud."

**Annex III point 2, verbatim** (the point Article 86 expressly excludes):
"Critical infrastructure: AI systems intended to be used as safety components in
the management and operation of critical digital infrastructure, road traffic,
or in the supply of water, gas, heating or electricity."

**Result: the BFSI credit underwriting applied arm is fully inside Article 86.**
Credit sits at 5(b), it is not the excluded point 2, and a credit refusal plainly
produces legal effects. All four links of the chain bind on the applied arm
simultaneously. This was RECALLED yesterday and is now VERIFIED.

**One framing constraint.** 5(b) carves out fraud detection. The prototype must
be described as creditworthiness evaluation and never as fraud detection, or the
Annex III classification fails and Article 86 does not apply.

The applied arm is therefore no longer an illustration. It is the case where
provider choice, technical documentation, deployer oversight, and an individual's
right to an explanation all meet.

**Decision (Ajay, 2026-08-03): phi is two claim maps, not one.**

- `phi_overseer`, targeting Annex IV 2(e) and 3 read with Article 14(4)(c).
  Addressee is a human overseer at the deployer. Standard: "correctly interpret
  ... taking into account, for example, the interpretation tools and methods
  available".
- `phi_affected`, targeting Article 86(1). Addressee is the person the decision
  is about. Standard: "clear and meaningful explanations of the role of the AI
  system in the decision-making procedure and the main elements of the decision
  taken".

Each is reported at three granularities, so six deterministic maps in total.

**Why this costs nothing.** `phi` is deterministic code applied post-hoc to
circuits that have already been discovered. Six maps over the same 3,780
circuits add zero GPU time. The cost is implementation and reporting surface
only.

**Why it is more than a free extra.** If the two flip rates diverge, that is
itself a finding: the same circuit set would support a stable technical filing
while producing an unstable individual explanation, or the reverse. Either
direction is publishable and neither is available to a single-map design.

**Reporting discipline.** Six maps is a large surface for the "you tuned phi"
objection. Both maps must be fixed in the pre-registration before any pooled
result is seen, and the qualitative conclusion must be shown stable across all
three granularities for each addressee. If it is not, say so.

---

## 2026-08-03 (Phase 2 begins) — phi implemented and tested

**Built.** `src/p1/claim_map.py` and `tests/test_claim_map.py`. **79 tests total,
all passing**, verified by running the suite in this session (35 multiverse, 24
spec, 20 claim map).

**Design.** Three properties enforced by construction rather than by intention.

1. **Deterministic.** Pure functions over a frozen `CircuitFeatures` record. No
   model, no randomness, no LLM anywhere in the path.
2. **Nested granularities.** COARSE, MEDIUM and FINE are built by *appending*
   fields to a tuple key, so each partition provably refines the previous one.
   The reviewer objection "you chose granularities that produced the flip rate
   you wanted" is answered structurally: a test asserts over 150 randomised
   circuits that agreement at FINE implies agreement at MEDIUM implies agreement
   at COARSE, for **both** addressees, and a second asserts the coarser key is
   literally a prefix of the finer one.
3. **Pre-registerable.** Every threshold is a named argument with a default.
   `DEFAULT_SIZE_BINS` and `DEFAULT_BAND_NAMES` are marked PROVISIONAL and must
   be fixed in the pre-registration before any pooled result is seen.

**The two maps are genuinely different functions, not one dressed twice.**

- `phi_overseer` is **component-facing**: layer band, then subgraph size, then
  attended segment. It answers Article 14(4)(c), addressed to a person assigned
  human oversight.
- `phi_affected` is **input-facing**: dominant input segment first, then how much
  of the model was involved, then the runner-up segment. It answers Article
  86(1), addressed to the person the decision is about, who is owed "the main
  elements of the decision taken" and not a list of attention heads.

A test asserts the separation directly: for a circuit whose attribution is
dominated by an income field, the affected-person claim names income and the
overseer claim does not.

**Separation of concerns.** `CircuitFeatures` is the only thing phi sees.
Populating it needs the model and belongs in the harness. This keeps phi pure,
GPU-free, and testable now, and it means the six claim maps cost zero sweep time
because they are applied post-hoc to circuits already discovered.

**Tie-breaking is deterministic and documented.** Layer-band ties resolve to the
earliest band; segment ties resolve by label ascending. Without this the claim
would depend on set iteration order, which would be a silent reproducibility
defect rather than a loud one.

**Empty circuits map to a claim rather than raising.** An empty circuit is
reachable at a strict threshold, and raising inside a 3,780-cell sweep would be
worse than recording a stated absence.

### Still to build before the harness runs

- The feature extractor that turns an auto-circuit output into `CircuitFeatures`.
  Needs the model, so it is GPU-side.
- **Segment definitions per task.** `position_mass` keys are pre-registered input
  segments: application fields for the credit arm, template slots for IOI. These
  are not yet defined and are part of the pre-registration.
- Size bins and band boundaries are PROVISIONAL and must be frozen at Gate 3.

---

## 2026-08-03 (Phase 2) — Feature extractor built. D14 opened.

**Built.** `src/p1/features.py` and `tests/test_features.py`. **103 tests total,
all passing** (35 multiverse, 24 spec, 20 claim map, 24 features).

**The layer trap.** auto-circuit's `Node.layer` is not the transformer block
index. Quoted verbatim from `auto_circuit/types.py`: "Transformer blocks count as
2 layers (one for the attention layer and one for the MLP layer)". GPT-2 small
therefore exposes about 24 auto-circuit layers, not 12. Feeding that straight
into a claim map assuming twelve would have placed every real component in the
"early" band and corrupted every claim in the sweep, silently. `features.py`
makes the conversion explicit and a regression test asserts that a component in
the final block lands in the "late" band. A second test confirms the mixed
convention raises rather than miscomputing, because `CircuitFeatures` validation
catches an out-of-range layer.

**D14 opened, blocking.** Only two of ten discovery algorithms accept
`ablation_type`. ACDC accepts none and hardcodes corrupt-batch resample at
`ACDC.py` lines 96 to 97. `run_circuits` does accept it, so under ACDC the
ablation operator acts on **evaluation only**, not on the prune-score ranking.

**Consequence, and a retroactive vindication of D12.** Metric-relative `tau`
means the cut point is chosen by evaluating the metric under a given ablation, so
`(a, m, tau)` jointly select `C` and the ablation axis stays live. **Under
absolute `tau` with ACDC, both the ablation and metric axes would have been
inert and the grid would have collapsed from 3,780 to 45 distinct circuits.**

**A finding falls out of this.** The field treats choice of ablation as a single
degree of freedom. Whether it acts on discovery or only on evaluation depends on
the algorithm, and no paper appears to say so. Free to report, and it sharpens
the multiverse argument.

**Torch could not be installed in the sandbox.** The 155MB aarch64 CPU wheel
stalled mid-download after several minutes. Gate 2 must be measured on Ajay's
Mac, which is the right place anyway since the environment hash that goes in the
paper should come from a machine that will be used again.

**D14 closed (Ajay, 2026-08-03): `mask_gradient` is primary, ACDC is a contrast.**

`mask_gradient_prune_scores` takes `ablation_type` directly, so all seven
operators act on the prune-score ranking and the ablation axis is live at
discovery rather than only through the tau cut. Independently supported by MIB
(2504.13151, VERIFIED), which reports attribution and mask-optimisation methods
performing best on circuit localisation.

ACDC runs as a labelled contrast, not a second grid. Reporting both lets the
paper state, with source evidence, that the same nominal degree of freedom acts
on discovery under one algorithm and only on evaluation under another. No paper
appears to say this and it costs one extra arm.

**Open sub-decision.** `mask_gradient_prune_scores` also exposes
`grad_function` with four levels and `answer_function` with three, twelve
combinations in total. These are discovery objectives, distinct from the
evaluation metric axis already in the grid. Whether any of them enter the
confirmatory grid, are fixed at a pre-registered default, or form a separate
robustness arm is **not yet decided** and must be settled before Gate 3.

---

## 2026-08-03 (Phase 2 cont.) — Manifest, prompt generator, smoke runner

**Built.** `src/p1/manifest.py`, `src/p1/prompts.py`, `scripts/smoke.py`,
rewritten `configs/smoke.yaml`, and their tests. **147 tests total, all
passing**: 35 multiverse, 24 spec, 20 claim map, 24 features, 22 manifest,
22 prompts.

### Three findings from the auto-circuit source, all VERIFIED

**1. The wheel ships no datasets.** `find . -name "*.json"` over the installed
package returns zero files. `Task._dataset_name` resolves through
`repo_path_to_abs_path`, which computes
`Path(__file__).parent.parent.parent / "datasets/..."`; on a pip install that
points inside `site-packages`, where no `datasets/` exists. **The bundled
`IOI_COMPONENT_CIRCUIT_TASK` and friends cannot load without cloning the GitHub
repo.**

Not a blocker, and arguably a clarification. Prompt variant is a **grid
dimension**, so P1 must control and seed-reproduce its own prompt sets whatever
happens. `src/p1/prompts.py` generates them and writes auto-circuit's own JSON
schema, so the instrument is still consumed verbatim through its documented
public entry point `load_datasets_from_json`.

**2. A documentation discrepancy in `load_datasets_from_json`.** The docstring
prose says the file holds dictionaries with keys `"clean_prompt"` and
`"corrupt_prompt"`. The JSON schema block in the same docstring says `"clean"`
and `"corrupt"`, nested under a top-level `"prompts"` list. The schema block is
what the loader parses. A test pins the correct form so this cannot be
reintroduced.

The schema also has `seq_labels`, which is the natural source of the segment
labels `phi_affected` reads. Generating both in one place stops them drifting.

**3. `PatchType` may make the D2 extension layer unnecessary.** Verbatim from
`types.py`: `EDGE_PATCH` "Patch the edges in the circuit", `TREE_PATCH` "Patch
the edges <u>not</u> in the circuit". So TREE_PATCH keeps the circuit and ablates
everything else, which is **sufficiency**; EDGE_PATCH destroys the circuit, which
is **comprehensiveness**. If that mapping holds under test, the ERASER metrics
come from the instrument verbatim rather than from an additive extension, which
is strictly better for the verbatim-instrument claim. **INFERRED from the
docstrings, not yet verified by running.** Revisit D2 once measured.

### Gate 2 is now a script

`scripts/smoke.py` produces two numbers and deliberately nothing else:
`discovery_s`, the cost of one prune-score ranking, and
`evaluation_per_cut_s`, the marginal cost of evaluating that ranking at one more
`(m, tau)` cut. **Report them separately, never their sum.** The ratio is what
decides whether the sweep needs one ranking per
`(ablation, corruption, prompt, seed)` cell, roughly 315 discoveries, or 3,780
independent ones.

It writes a `Manifest` whether or not the run succeeds, because a failed run is a
fact about the environment and losing it is worse than recording it. Imports of
torch and auto-circuit are late so `--help` works on a machine without them,
which was verified in the sandbox.

**Two traps handled explicitly in the runner.** `ru_maxrss` is kilobytes on Linux
and **bytes** on macOS, so an unguarded read reports a 1000x error in the memory
figure on Ajay's machine. And TREE_PATCH versus EDGE_PATCH being the wrong way
round would silently invert every faithfulness number rather than raising.

**Status of `scripts/smoke.py` and `src/p1/features.py`: written against source
read from the wheel, NOT YET EXECUTED.** Torch could not be installed in the
sandbox; the 155MB aarch64 CPU wheel stalled mid-download. Treat the first run as
a debugging session and only trust the second.

### Provenance note on the prompt templates

The templates in `src/p1/prompts.py` are **P1's own**, written to the structure
described in 2407.08734 section 4: fifteen templates involving two people, the
token to predict being the indirect object, ABBA or BABA order, ABC corrupt
distribution. They are **not** transcribed from Wang et al. and must not be
presented as such. If exact replication of the published IOI set is wanted, take
the templates from that work's own release and record it in the ledger.

---

## 2026-08-04 — Gate 2 attempt 1: FAILED on a dependency break. Diagnosed.

**Ran** `scripts/smoke.py` on Ajay's Mac. `status: failed`, `import_s 54.388`,
`peak_rss_mb 309.2`. The manifest captured the failure with the full environment,
which is what it was built for.

**Environment as recorded:** macOS-26.5.2, arm64, Python 3.11.9, torch 2.13.0,
transformer-lens **3.6.0**, auto-circuit 1.0.1.

**Root cause, from the captured traceback:**

    File ".../auto_circuit/data.py", line 14, in <module>
      from transformer_lens.past_key_value_caching import HookedTransformerKeyValueCache
    ModuleNotFoundError: No module named 'transformer_lens.past_key_value_caching'

**auto-circuit 1.0.1 declares `transformer-lens>=1.13.0` with no upper bound.**
transformer-lens 3.x removed that module. pip resolved 3.6.0 and the instrument
cannot import.

**Boundary established by inspecting wheels, VERIFIED 2026-08-04:**

| transformer-lens | `past_key_value_caching` present |
|---|---|
| 1.17.0, 2.11.0, 2.15.4, 2.17.0, **2.18.0** | yes |
| **3.0.0**, 3.6.0 | **no** |

So **2.18.0 is the last compatible version**. `requirements.txt` now hard-pins
it, with the reasoning inline so nobody relaxes it back to a range.

TL 2.18.0 on Python >= 3.9 requires `torch>=2.6` (satisfied, 2.13.0) and
`transformers>=4.57`. The installed transformers is **5.14.0**, which satisfies
the floor but is a major version ahead of what TL 2.18.0 was released against.
**Residual risk, not yet tested.** If TL 2.18.0 fails against transformers 5.x,
transformers must be pinned too.

**What this vindicates.** The same unbounded-range problem was flagged on
2026-08-03 when pip resolved `pandas>=2.0` to pandas 3.0.5. It has now caused a
real failure. Every dependency that can change a number or an import path gets a
hard pin, and the lock file is the record.

**What worked.** The manifest wrote on failure, recorded the exact environment,
and preserved the traceback. Diagnosis took one file read rather than a
re-run. That design decision paid for itself on the first failure.

**Still unmeasured: `discovery_s` and `evaluation_per_cut_s`.** Gate 2 remains
open. The run got as far as importing and no further.

---

## 2026-08-04 — Gate 2 attempt 2: dependency fixed, failed later. Two findings.

`transformer-lens==2.18.0` resolved the import break. The run reached much
further before failing.

**Timings from attempt 2:** `import_s 15.254` (cached, down from 54.4),
`model_load_s 3.743`, `data_build_s 0.026`, `patchable_model_s 0.0`,
`peak_rss_mb 1084.8`. **GPT-2 loaded, P1's generated prompts were accepted by
`load_datasets_from_json`, and the dataset built in 26ms.** The prompt generator
and the schema conformance tests were correct.

**Failure, from the captured traceback:**

    File ".../auto_circuit/utils/graph_utils.py", line 163, in graph_edges
      assert separate_qkv is not None, "separate_qkv must be specified for LLM"

**Finding 1, the trivial one.** `patchable_model` requires `separate_qkv` for any
`HookedTransformer`; it has no usable default. Set to `True`, which pairs with
`use_split_qkv_input=True`; `transformer_lens_utils.py` line 76 asserts exactly
that pairing.

**Finding 2, the one that matters.** auto-circuit exports its own model
preparation, `load_tl_model` in `auto_circuit/experiment_utils.py`. Verbatim, it
does:

    from_pretrained(name, device=device, fold_ln=True,
                    center_writing_weights=True, center_unembed=True)
    cfg.use_attn_result = True
    cfg.use_attn_in = True
    cfg.use_split_qkv_input = True
    cfg.use_hook_mlp_in = True
    model.eval()
    for param in model.parameters(): param.requires_grad = False

`tasks.py` lines 173 to 176 do the same. **The smoke script had been hand-rolling
this and was missing `fold_ln`, `center_writing_weights`, `center_unembed`,
`use_attn_in`, `eval()`, and `requires_grad=False`.**

The first three are not cosmetic. They rewrite the weights into an equivalent
but numerically different parameterisation. A hand-rolled preparation missing
them produces a different model and therefore **different circuits**, and nothing
raises. That is the exact failure mode the "reproduce the instrument verbatim"
rule exists to prevent, and it nearly entered through the door marked model
loading rather than the one marked algorithm.

**Rule sharpened, applies to the whole sweep harness: reproducing the instrument
verbatim includes reproducing how it prepares its input.** Call `load_tl_model`,
never a copy of it.

**Environment note.** Pinning transformer-lens 2.18.0 pulled numpy down to
1.26.4 and pandas to 2.0.3, and pip warned that jax and jaxlib want numpy>=2.0.
jax arrives via `tracr-pypi`, an auto-circuit dependency used only for its tracr
models, which P1 does not use. Harmless for now; record it so the warning is not
rediscovered. The sweep environment and the analysis environment now genuinely
differ in numpy major version, which is precisely why two requirement files
exist.

**Gate 2 still open.** `discovery_s` and `evaluation_per_cut_s` remain
unmeasured. Attempt 3 pending.

---

## 2026-08-04 — Gate 2 attempt 3: patchable_model works. D15 resolved.

`separate_qkv=True` and `load_tl_model` fixed the previous failure.
**`patchable_model` succeeded in 0.066s.** Timings: `import_s 6.324` (warm),
`model_load_s 3.483`, `data_build_s 0.017`, `patchable_model_s 0.066`,
`peak_rss_mb 1063.4`. Device correctly detected as cpu, and the manifest carried
the standing warning that a CPU figure is an upper bound.

**New failure, from the captured traceback:**

    File ".../auto_circuit/prune_algos/mask_gradient.py", line 62
      assert (mask_val is not None) ^ (integrated_grad_samples is not None)
    AssertionError

Exactly one of `mask_val` and `integrated_grad_samples` must be set. Passing
neither raises a bare AssertionError with no message. Both now flow from the
config, and `configs/smoke.yaml` sets `mask_val: 0.0`.

**D15 resolved, and much better than the open question implied.** auto-circuit
ships **eight named `PruneAlgo` constants** built on `mask_gradient_prune_scores`.
Full table in `docs/DESIGN-DELTAS.md`. The smoke config now reproduces
`LOGIT_DIFF_GRAD_PRUNE_ALGO`, short name **"EAP"**, exactly:
`grad_function=logit`, `answer_function=avg_diff`, `mask_val=0.0`.

**The discovery-objective axis should be those eight, not a synthetic 4 x 3
crossing.** They are named, shipped, and used by the instrument's authors, so the
"cite a published implementation for each level" criterion holds by construction,
whereas a synthetic crossing would include combinations nobody has run. It is the
same principle that forced `load_tl_model` over a hand-rolled copy, now applied
to the discovery axis.

It also catches a degree of freedom a synthetic grid would miss entirely. EAP
versus IEG is not a `grad_function` value; it is the mask_val / IG XOR. And IEG
appears at **50 and 1000 samples**, the same algorithm at two costs.
arXiv:2510.00845, the second-closest prior work, is a variance analysis of
EAP-IG, so this axis is already live in the literature.

**Cost warning for Gate 2.** IEG at 1000 samples is roughly 1000
forward/backward passes against 1 for EAP. If all eight levels enter the grid the
two IEG levels will dominate the budget. Measure EAP and IEG separately before
the pre-registration fixes the level set.

**Pattern across three attempts.** Every failure so far has been a missing
required argument that auto-circuit asserts on rather than defaults, and each
assertion has pointed at a real design decision P1 had left implicit:
`separate_qkv` at the edge/node question, model preparation at the verbatim rule,
and now the mask_val XOR at the EAP/IEG axis. The instrument is forcing the
specification space to be stated explicitly, which is what the paper is about.

**Gate 2 still open.** `discovery_s` and `evaluation_per_cut_s` unmeasured.
Attempt 4 pending.

---

## 2026-08-04 — GATE 2 PASSED. First measured numbers. One inference corrected.

`scripts/smoke.py` completed with `status: ok` on attempt 4. The feasibility
claim is no longer an assertion.

### Measured, CPU, gpt2, 32 prompts, 32,491 edges

| Quantity | Value |
|---|---|
| `discovery_s`, one prune-score ranking (EAP) | **9.301** |
| `evaluation_per_cut_s`, one extra `(m, tau)` cut | **1.581** |
| `evaluation_s`, 5 cuts | 7.907 |
| `discovery_to_eval_ratio` | **5.88** |
| `peak_rss_mb` | 2,433.8 |
| `import_s` warm / `model_load_s` / `patchable_model_s` | 6.47 / 3.462 / 0.069 |

Environment hash `555feab0909e71c0`, commit recorded in the manifest. macOS,
arm64, Python 3.11.9, torch 2.13.0, transformer-lens 2.18.0, auto-circuit 1.0.1.

### The reuse architecture is confirmed, and the saving is 4.62x, not 12x

Discovery costs 5.88 evaluation cuts, so reusing one ranking across the
`(metric, tau)` cuts is clearly worth doing. But **the 12x figure inferred on
2026-08-03 was wrong** and is corrected here.

    grid                       3,780 specifications
    discovery cells            315   (ablation x corruption x prompt x seed)
    (metric x tau) cuts reused 12    per ranking

    REUSE  315 x 9.301 + 3,780 x 1.581 =  8,906 s =  2.47 h
    NAIVE  3,780 x (9.301 + 1.581)     = 41,134 s = 11.43 h
    SAVING 4.62x

**The earlier inference implicitly treated evaluation as near-free. It is not.**
At 12 cuts per ranking, evaluation is **67% of total cost** and discovery only
33%. The bottleneck is the opposite of what was assumed. Any future optimisation
effort belongs on `run_circuits`, not on discovery.

Recorded as a correction rather than an edit: the 2026-08-03 entry stands as
written and this supersedes it.

### The real budget risk is IEG, not the grid size

If the discovery-objective axis adopts auto-circuit's eight named algorithms
(D15), two of them are integrated gradients:

| Level | One discovery | All 315 cells |
|---|---|---|
| EAP (`mask_val=0.0`) | 9.3 s | 0.8 h |
| IEG-50 | ~7.8 min | ~41 h |
| IEG-1000 | ~2.6 h | **~814 h** |

IEG-1000 is roughly 1,000 forward/backward passes against 1 for EAP. **On CPU it
is not merely expensive, it is infeasible: 814 hours is 34 days for a single
axis level.** Even a 20x GPU speedup leaves ~40 hours for that level alone.

**This is a pre-registration decision, not an optimisation.** Either IEG enters
as a reduced arm on a subset of cells, with the reduction rule pre-registered, or
it is excluded and the exclusion is stated and justified. Do not discover this
mid-sweep.

### Caveats on the numbers, stated so they are not over-read

1. **CPU, not GPU.** auto-circuit has no MPS support, so this is an upper bound.
   The GPU figure is unmeasured and the ratio, not the absolute time, is the
   transferable quantity.
2. **32 prompts only**, 16 train and 16 test. Cost scales roughly with prompt
   count for both stages. A realistic sweep at 256 prompts is plausibly 8x these
   numbers, so ~20 h CPU for the EAP-only grid.
3. **One `(grad, answer)` configuration.** Only EAP was timed. IEG is projected
   by multiplying sample count, which is an estimate and not a measurement.
4. **peak RSS 2.4 GB** at 32 prompts with 32,491 edges. Memory scales with
   prompts and edges, so the 24GB GPU headroom needs its own check before the
   real prompt count is fixed.

### Verdict

**Gate 2 passes for the EAP-only grid.** 2.47 h CPU, and materially less on GPU,
fits the 16 to 28 August window with room. **Gate 2 does not pass for a grid
containing IEG-1000** and that level needs an explicit pre-registered decision.

D3 is closed on the arithmetic and reopened as a scoping question about IEG.

### D3 closed (Ajay, 2026-08-04): IEG scoping fixed

The discovery-objective axis adopts auto-circuit's eight named algorithms (D15),
which makes IEG-1000 the single most expensive object in the design. Resolved as:

| Arm | Levels | Design | Discoveries | CPU |
|---|---|---|---|---|
| Confirmatory | 6 EAP + IEG-50 | fully crossed | 7x315 = 2,205 | ~57 h |
| IEG-1000 | 1 | **seed-only slice**: one ablation, one corruption, one prompt variant, five seeds | 5 | ~13 h |

Total ~70 h CPU, comfortably inside the 16 to 28 August window even with no GPU,
and far less on one.

**Why a seed-only slice rather than exclusion.** IEG-50 versus IEG-1000 differs
only in integrated-gradient sample count, so it is a precision choice rather than
a conceptual one. But it is still a researcher degree of freedom, and a reviewer
can reasonably ask whether 50 samples suffices. The seed-only slice answers that
question with evidence at 1.5% of the full cost. **The reduction rule is fixed
now, before any pooled result is seen, so it is a design decision and not a
deviation.** Record it verbatim in the pre-registration.

**Grid arithmetic, computed from the measured 9.301 s and 1.581 s:**

    per discovery-objective level   315 discoveries, 3,780 specifications
    confirmatory (7 levels)         26,460 specs   45.6 h disc + 11.6 h eval
    IEG-1000 seed-only slice         5 discoveries ~12.9 h
    TOTAL                                          ~70 h CPU

**Unmeasured and load-bearing: the CPU to GPU speedup.** Every GPU figure quoted
so far assumes 20x, which is a guess. **Measure it with one smoke run on the
rented box before committing to the sweep window.** At 5x the confirmatory arm is
11 h rather than 3 h, which is still fine; the assumption only became dangerous
for the full-IEG option, which is no longer being taken.

### Gate 2 verdict, final

**PASSED.** Feasibility is now measured rather than asserted, the grid is scoped,
and the reuse architecture is confirmed with a corrected 4.62x saving. D3 is
closed on both arithmetic and scope.

---

## 2026-08-04 — D4 progress: UKPLab repo README read. Three findings.

`github.com/UKPLab/arxiv2026-phantom-specialization` README fetched and
**VERIFIED**. The abstract matches the arXiv version already in the citation
ledger word for word, which independently confirms the quotes recorded on
2026-08-03.

### Finding 1: they use the same instrument

Verbatim from their Third-party resources section:

> "**Circuit discovery.** `auto-circuit` provides the ACDC / EAP implementations
> and patching utilities used throughout."

**P1 and 2606.06267 run on the same library.** That is a strong comparability
claim and should be stated in the paper: the structural-versus-functional gap P1
measures is measured with the same instrument that established the phantom
specialization result P1 builds on. It also means their interchange protocol is
expressible in auto-circuit primitives P1 already uses.

### Finding 2: a compute calibration that retroactively validates D14

Verbatim: "End-to-end reproduction takes on the order of **700 GPU-hours on
A100-class GPUs** (around 290 hours for the Pareto sweep and 450 hours for
circuit discovery)."

They produce **75 circuits for 450 GPU-hours of discovery**, roughly 6 GPU-hours
per circuit, using **ACDC** across five Pythia models from 70M to 1.4B.

P1's measured EAP discovery is **9.3 seconds** on CPU for GPT-2 small. The gap is
explained by three compounding choices: ACDC iteratively prunes with many forward
passes where EAP needs one backward pass; their models run up to 1.4B against
GPT-2 small's 124M; and they sweep thresholds by Pareto analysis where P1's `tau`
is metric-relative and computed post-hoc on an existing ranking.

**This is independent evidence that the D14 choice of `mask_gradient` over ACDC
as primary was load-bearing for feasibility, not merely a correctness argument
about `ablation_type`.** Had P1 taken ACDC, the sweep would plausibly be in their
cost regime rather than in tens of CPU-hours. Record this comparison in the paper:
it is a concrete, cited number showing why the design is runnable.

### Finding 3: they also run a random baseline

`LSC_circuits/lsc_random_baseline.py` sits alongside `lsc_acdc_circuit.py`. P1's
H3 random-circuit null multiverse is therefore methodologically aligned with the
paper it answers, which is worth one sentence in related work.

### What is still not obtained

**The interchange-intervention protocol itself.** The README places the analysis
in a five-phase pipeline; interchange interventions are section 5.3.2 of the
paper and most plausibly live in `03_Phase_Representational/` or
`05_Phase_Targeted/`, described as "Targeted experiments (cross-band transfer,
ablations, etc.)". The GitHub tree API and HTML listing both returned empty to a
plain fetch, so the file cannot be located remotely.

**Resolution: clone the repo.** It is Apache 2.0 and this is the right move
regardless, because reproducing the protocol verbatim requires their code rather
than a description of it.

    git clone https://github.com/UKPLab/arxiv2026-phantom-specialization.git \
      /tmp/phantom-spec
    grep -rl "interchange" /tmp/phantom-spec --include=*.py --include=*.ipynb

Do **not** reimplement from the paper prose. The instrument-verbatim rule applies
to a protocol P1 is reproducing exactly as much as it applies to auto-circuit,
and the `load_tl_model` incident on 2026-08-04 showed how a plausible hand-rolled
version silently diverges.

**D4 remains open.** It is the last non-writing blocker before Gate 3.

---

## 2026-08-04 — D4 RESOLVED. Interchange protocol extracted from their code.

Cloned `UKPLab/arxiv2026-phantom-specialization` (Apache 2.0) to
`.external/phantom-spec`, gitignored. Full analysis in `docs/DESIGN-DELTAS.md`
under D4. Everything below is VERIFIED verbatim from their source.

**The protocol.** `05_Phase_Targeted/13_activation_patching.ipynb` implements
`compute_interchange_metrics`. Cache source activations at a hook, run the base
input with them patched in, and measure **IIA**, the fraction of pairs where the
patched base now predicts the source's target token, plus a logit difference.
Constants: `N_PAIRS = 100`, `EVAL_SEED = 123`, `batch_size = 50`.

**P1 cannot reproduce it verbatim, and must say so.** They vary input statistics
with the analysis fixed. P1 varies analytic specification with the input fixed.
The IIA machinery transfers; the pairing logic does not. Report it as a cited
adaptation, not a reproduction. Claiming otherwise would be false and is exactly
what the instrument-verbatim rule is meant to prevent.

**A cheaper measure found alongside it.** `per_example_agreement.py` compares
circuits by per-example correct/incorrect verdicts using `agreement_rate` and
`cohens_kappa`. It needs no patching and is computable from `run_circuits` output
the sweep already produces. **Plan: agreement and kappa across the full grid,
expensive IIA reserved for a pre-registered subset of low-Jaccard pairs.**

**Random-Jaccard closed form adopted.** Their
`jaccard_calibration.py` uses `j_rand = k / (2N - k)`. Implemented as
`p1.multiverse.expected_random_jaccard` with a Monte Carlo agreement test to
within 0.02 and pinned boundaries. **156 tests total, all passing.**

**A warning that falls out of it.** Their reported calibration is "Observed
Jaccard is 4-27x higher than random". At P1's measured scale, GPT-2 small with
32,491 edges, a 500-edge circuit has `J_rand = 0.008`. **Any observed overlap
above roughly one percent is already far above chance, so H3 should be expected
to fail if stated about circuit overlap.** H3 is stated about the claim, and the
distinction is the substance of the hypothesis rather than a phrasing detail:
circuits can be statistically far from random while the claims derived from them
are not. Say so in advance in the pre-registration, and keep the two levels
rigorously separate in the manuscript.

**D4 closed.** The last non-writing blocker before Gate 3 is cleared.

---

## 2026-08-04 — Pre-registration DRAFTED (not locked)

`preregistration/PLAN.md` written, and `preregistration/DEVIATIONS.md` created
empty. **The plan is not a pre-registration until it is committed, tagged, and
the tag pushed to a public remote**, with hash and UTC timestamp in this log.

**Ordering satisfied.** Pipeline built and unit-tested (156 tests). Validated on
the Gate 2 smoke configuration, which is 32 prompts, is marked in
`configs/smoke.yaml` as excluded from any confirmatory analysis, and produced a
timing only: no claim, no flip rate, no overlap figure. **No pooled result from
the confirmatory grid has been inspected by anyone.**

**Contents.** Hypotheses P0, H2 primary, H3, H4, each with a decision quantity.
One primary outcome, `F` for `phi_overseer` at MEDIUM, with the estimator written
as a formula. The 26,460-specification grid from 2,205 rankings. Metric-relative
`tau` stated verbatim with the absolute alternative acknowledged. Six claim maps
with the nesting property. Bootstrap resampling specifications with B = 10,000.
Random null multiverse for joint inference. Variance decomposition by axis. The
exclusion rule, with discards written as manifests so the rate is computable from
`results/` rather than remembered. **Both abstracts drafted**, per standing rule
6. Kill criteria. What would falsify the claim.

**One thing recorded deliberately in advance.** The plan states, before any
result is seen, that H3 is expected to *fail* if tested at the circuit level,
because 2606.06267 report observed Jaccard 4 to 27 times random and at P1's
measured 32,491 edges a 500-edge circuit has `J_rand = 0.008`. H3 is stated about
the claim. Writing that expectation down now is what stops it becoming a
post-hoc rescue later.

**Seven items marked [CONFIRM] and blocking the lock.** H2 and H4 numeric
thresholds; the corruption, `tau`, and prompt-variant level sets, none of which
are yet fixed; and `phi`'s size bins, band names, and per-task segment labels,
all still PROVISIONAL in code. These are the last design decisions in the paper.

**Also blocking:** the private GitHub remote does not exist yet, so there is
nowhere to push a tag, and a pre-registration timestamp attested only by a local
clock is not evidence.

**Spotlight was the git lock culprit.** `lsof` showed `com.apple` PID 75678
holding `.git/index.lock`, indexing the 139MB cloned repo under `.external/`.
Fixed with `.external/.metadata_never_index`. Recorded because it will recur on
any machine that clones a large upstream repo inside the working tree.

**Housekeeping, 2026-08-04.** The cloned UKPLab repo under `.external/` caused
repeated `.git/index.lock` collisions. `lsof` identified the holder as
`com.apple` PID 75678, i.e. Spotlight indexing 139MB of newly appeared files
inside the working tree. `.metadata_never_index` did not help once indexing had
already begun.

**Resolution: move the clone out of the repository tree entirely.** Everything
P1 needs from it is already extracted and quoted verbatim in
`docs/DESIGN-DELTAS.md` under D4: the `compute_interchange_metrics` procedure and
its constants, the `agreement_rate` and `cohens_kappa` definitions, and the
`j_rand = k / (2N - k)` calibration formula. The clone is no longer a dependency.

**General rule, worth keeping.** Do not clone large upstream repositories inside
a working tree that git and a desktop indexer both watch. Read them, extract what
is needed into the log with provenance, and delete. A cloned repo is a transient
research input, not a project artefact.

---

## 2026-08-04 — D18 opened while grounding corruption levels. Blocks the lock.

Started fixing the three unfixed axis level sets and found that the corruption
axis is **degenerate for two of the seven ablation operators**. VERIFIED from
`ablation_activations.py` and the `corrupt_dataset` property in `types.py`.

**ZERO** produces `t.zeros_like(out)` and has its input forced to `batch.clean`.
**TOKENWISE_MEAN_CLEAN** is `clean_dataset` only. Neither reads the corrupt
distribution, so crossing them against three corruption levels yields three
identical specifications.

Computed exactly: **5,040 of 26,460 specifications are exact duplicates, 19% of
the grid**, and **420 of 2,205 discoveries are wasted, 19% of the sweep budget**,
about 65 minutes of CPU.

**The bias on `F` is 2.16e-05, negligible.** The problem is methodological rather
than numerical: a multiverse whose specifications are not distinct
specifications misrepresents itself, and the specification curve would plot three
identical points where one specification exists.

Recommendation is to **nest corruption within ablation**, cross it only for the
five corruption-dependent operators, and switch the variance decomposition from
the closed-form EMS estimator to REML because the design is then unbalanced.
Full statement and alternatives in `docs/DESIGN-DELTAS.md` D18.

**A second finding alongside it.** `clean_corrupt` must be supplied for RESAMPLE,
BATCH_TOKENWISE_MEAN and BATCH_ALL_TOK_MEAN; the assert makes it mandatory and
there is no default at that layer, though `mask_gradient_prune_scores` defaults
it to `"corrupt"`. **P1's specification space does not contain this axis.** It is
an undocumented researcher degree of freedom affecting three of seven operators,
and it is exactly the kind of choice the paper is about. Add it, or fix it at
`"corrupt"` and record the choice. Do not leave it implicit.

**Why this matters more than its size.** Both findings were invisible from the
brief, from the paper, and from the API signatures. They surfaced only from
reading how the ablation values are actually computed. The pattern across this
whole session holds: every axis P1 assumed was simple turned out to have
structure inside it, and each time the structure was a researcher degree of
freedom nobody had written down. That is the paper's thesis reproducing itself
in its own construction, and it belongs in the discussion.

**Workflow, 2026-08-04.** The `.git/index.lock` collisions continued after the
`.external/` clone was deleted, so the clone was not the only cause. The repo
lives under `~/Desktop`, which Spotlight indexes, and is normally open in an
editor with git integration; both take the index lock periodically. When one
holds it as a git command starts, git aborts and **leaves the lock file behind**,
so every subsequent commit fails until it is removed by hand.

Added `scripts/commit.sh`, which checks for a real running git process, clears
any stale lock, then stages and commits. Chasing the root cause further is not a
good use of research time. Recorded so the next person does not rediscover it.

---

## 2026-08-04 — Citation ledger: two of six name-only references resolved

Grepped arXiv links out of auto-circuit 1.0.1's own docstrings. **This is the
strongest available provenance**: these are the identifiers the instrument's
authors attach to the algorithms P1 runs.

**Resolved:**

- `Wang et al., IOI` = **2211.00593**, *Interpretability in the Wild: a Circuit
  for Indirect Object Identification in GPT-2 small*, Kevin Wang, Alexandre
  Variengien, Arthur Conmy, Buck Shlegeris, Jacob Steinhardt. Abs page fetched,
  fully VERIFIED.
- `Conmy et al., ACDC` = **2304.14997**, *Towards Automated Circuit Discovery for
  Mechanistic Interpretability*, from the `ACDC.py` docstring. ID and title
  verified; authors still to fetch.

Also captured, all RECALLED from docstrings and needing fetch: Hanna et al. 2023
= 2305.00586 (greater-than task), Sundararajan et al. 2017 = 1703.01365
(Integrated Gradients, **cite for the IEG axis levels**), Louizos et al. 2017 =
1712.01312, Cao et al. 2021 = 2104.03514, and a bare 2310.10348 with no citation
text that could not be identified.

**A year discrepancy to settle.** Wang et al. is **2022** on arXiv. auto-circuit
cites "(2022)"; 2407.08734's prose cites "(2023)", presumably the ICLR version.
Same class of problem as D6. Pick a convention and apply it consistently.

**A finding for phi.** Wang et al.'s abstract, verbatim: "Our explanation
encompasses **26 attention heads grouped into 7 main classes**." That is a
**published head-role taxonomy for IOI**. `phi`'s role categorisation was
previously flagged as needing a published source rather than an invented one, and
this supplies it. Extract the seven class names and use them as the
pre-registered role mapping, cited to Wang et al.

Also from the same abstract: they evaluate with "faithfulness, completeness and
minimality". P1 uses faithfulness only. The answer to a reviewer is that
completeness and minimality assess a single circuit against a ground truth,
whereas P1 measures agreement *between* circuits. One sentence in the paper.

**Still name-only and blocking the manuscript:** Nanda (attribution patching),
Steegen (multiverse), Simmons (researcher degrees of freedom), Simonsohn
(specification curve). The last three are the method provenance for the entire
design, so they are not optional.

---

## 2026-08-04 — All six name-only references resolved. One attribution corrected.

**Nanda attribution patching = arXiv:2310.10348**, *Attribution Patching
Outperforms Automated Circuit Discovery*, **Syed, Rager and Conmy**, NeurIPS 2023
ATTRIB Workshop. Abs page fetched, VERIFIED.

**The brief's attribution was wrong.** The citable paper is Syed, Rager and
Conmy. Neel Nanda's attribution patching is a blog post, citable as a blog post
but not as a peer-reviewed paper. Correct this before writing; attributing a
paper to the wrong authors is the kind of error a reviewer treats as evidence the
bibliography was not checked.

This also identifies the bare `2310.10348` URL found earlier in auto-circuit's
source, which had no citation text attached. Both loose ends were the same paper.

Its abstract, verbatim, explains P1's own cost profile: the method requires
"just two forward passes and a backward pass". That is why measured EAP discovery
is 9.3 seconds where their ACDC run is roughly 6 GPU-hours per circuit.

**The three methods papers, all located:**

- Steegen, Tuerlinckx, Gelman and Vanpaemel (2016), *Increasing Transparency
  Through a Multiverse Analysis*, Perspectives on Psychological Science 11(5)
  702-712, DOI 10.1177/1745691616658637.
- Simmons, Nelson and Simonsohn (2011), *False-Positive Psychology*,
  Psychological Science 22(11) 1359-1366, DOI 10.1177/0956797611417632.
- Simonsohn, Simmons and Nelson (2020), *Specification Curve Analysis*, Nature
  Human Behaviour 4(11) 1208-1214, DOI 10.1038/s41562-020-0912-z. **A Publisher
  Correction exists at 10.1038/s41562-020-00974-w**; check whether it touches
  anything P1 relies on.

**Marked `RECALLED-plus`, deliberately not `VERIFIED`.** These are journal
articles and the fields come from publisher landing pages and search results, not
from resolving the DOIs directly. Agreement across independent sources is strong,
but the standing rule says verified means fetched. **Resolve all three DOIs before
the bibliography is final.**

**Author-order trap recorded.** The same three authors appear in both 2011 and
2020 in different orders: Simmons, Nelson, Simonsohn in 2011; Simonsohn, Simmons,
Nelson in 2020.

**All six name-only references from the brief are now resolved to identifiers.**
The bibliography has stopped being a blocker, though three DOI resolutions and
several author-list fetches remain before submission.
