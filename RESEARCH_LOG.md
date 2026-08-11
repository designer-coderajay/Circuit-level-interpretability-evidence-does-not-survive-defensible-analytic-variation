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

---

## 2026-08-04 — phi's role taxonomy closed. Published, not invented.

The role dimension of the claim map was flagged on 2026-08-03 as needing a
published taxonomy rather than one P1 devised. **It is now supplied, and from
inside the instrument.**

`auto_circuit/metrics/official_circuits/circuits/ioi_official.py` ships
`IOI_CIRCUIT`, a dict of head roles with exact `(layer, head)` coordinates. Its
own header states it is based on `acdc/ioi/utils.py` from
ArthurConmy/Automatic-Circuit-Discovery, which transcribes Wang et al.,
arXiv:2211.00593.

**Provenance chain: Wang et al. -> ACDC repo -> auto-circuit -> P1.** Every link
is a published or shipped artefact. Nothing is invented.

Transcribed verbatim into `p1.claim_map.IOI_HEAD_ROLES`, with commented-out heads
excluded exactly as the instrument excludes them:

| role | n |
|---|---|
| name mover | 3 |
| backup name mover | 8 |
| negative | 2 |
| s2 inhibition | 4 |
| induction | 4 |
| duplicate token | 3 |
| previous token | 2 |
| **total** | **26 across 7 classes** |

**Independent cross-check.** Wang et al.'s abstract says "26 attention heads
grouped into 7 main classes". The transcription reproduces **both counts
exactly**. A test asserts both, so an edit that drops or adds a head fails loudly
rather than silently changing every role-bearing claim.

**Two design choices recorded rather than left implicit.**

`unclassified` is a first-class role, not a discard. Circuit discovery routinely
returns heads outside the published 26, and dropping them would bias every
role-based claim toward the taxonomy. A circuit that is mostly unclassified is
**reported as unclassified**, which is a real and reportable outcome.

Ties break toward the named role, using the instrument's own class ordering,
which its source annotates "by importance". `unclassified` loses every tie.

**Not wired into the claim keys.** `dominant_role` is available but the existing
COARSE / MEDIUM / FINE keys are unchanged, so the nesting property is untouched.
Whether the role enters a granularity is a pre-registration decision for Ajay.

**165 tests, all passing.**

---

## 2026-08-05. Backup closed; four pre-registration decisions taken; one design
## move withdrawn on a source check

### Backup

`origin` now exists: `https://github.com/designer-coderajay/p1-circuit-multiverse`,
private, `main` at `751573f`, 171 objects, 130 KiB. SSH was not configured on the
machine (`Permission denied (publickey)`), so HTTPS with browser auth was used.

Before pushing, `git gc --prune=now` removed 44 orphaned `tmp_obj_*` objects,
228 KB, left behind by the Spotlight index-lock collisions logged on 08-04.
`git fsck --no-progress` printed nothing afterwards. Branch renamed `master` to
`main` in the same operation; the only reference to `master` in the repo is a
historical line in this log, which is append-only and was not edited.

The pre-registration checklist item "private remote exists and history is
pushed" is now satisfied, which was a hard precondition for locking.

### Four decisions, all by Ajay

1. **Corruption is nested within ablation, not crossed.** D18 option (a).
2. **`clean_corrupt` fixed at `"corrupt"`**, recorded in the plan as a fixed
   choice and named in the limitations.
3. **Prompt variant = ABBA, BABA.** Two levels, both verbatim in 2407.08734
   section 4.
4. **H2 rule: `F > 0.20` with the 95% bootstrap CI lower bound above 0.20.**

Grid consequence, exact:

    ablation x corruption cells   5 x 3 + 2 x 1 = 17
    discovery cells               7 x 17 x 2 x 5 = 1,190
    specifications                1,190 x 4 x 3 = 14,280

Down from 2,205 and 26,460. Both fall to 54.0%.

Statistical consequence: the design is unbalanced, so **REML replaces the
closed-form EMS estimator** as the primary variance-components method. The five
corruption-dependent operators form a balanced sub-block where EMS still runs, so
it is retained there as an independent cross-check on the REML fit. This is a
real cost of the nesting decision and is recorded as one rather than glossed.

### Withdrawn: the mean-ablation dataset-size axis

Proposed on 08-04 as a replacement for the degenerate corruption axis. Checked
against source today and it does not survive.

`mask_gradient_prune_scores(model, dataloader, ...)` takes a single
`PromptDataLoader`. That same object is passed to `batch_src_ablations`, which
computes the ablation values, and is also the iterable in the
`for batch in dataloader` gradient loop, which is the discovery data. One
dataset, two uses. Varying the size of the set the ablation mean is taken over
necessarily varies the set discovery runs on. The two cannot be separated without
modifying the instrument, which is forbidden.

**This is the second time in this project a design move that read well died on a
source check.** The first was the 12x reuse saving, which measured at 4.62x. The
pattern is the same in both cases: an inference about the instrument's behaviour
was treated as a property of the instrument. Recording it here rather than
quietly deleting it, because the recurrence is the useful part.

### A cost figure I should not have written

Gate 2 measured EAP discovery at 9.301 s and marginal evaluation at 1.581 s per
cut. It did **not** measure IEG. `mask_gradient_prune_scores` loops over
`range(integrated_grad_samples + 1)`, each iteration a full pass over the
dataloader with a backward pass, so IEG-50 does 51 passes where EAP does 1.

The 57-hour confirmatory figure and the 814-hour IEG-1000 figure both rest on
that unmeasured factor. **Both are withdrawn from the plan.** No total-hours
number appears in `preregistration/PLAN.md` until the measurement exists.

`configs/smoke-ieg.yaml` added. It is byte-identical to `configs/smoke.yaml`
except that `mask_val: 0.0` is replaced by `integrated_grad_samples: 50`, so the
two `discovery_s` values are directly comparable. `scripts/smoke.py` needed no
change: it already reads both parameters with `.get`, which returns `None` for
the absent one, satisfying the library's XOR assertion.

### Still blocking the lock

- The three corruption **levels** themselves. Nesting settled the design, not the
  levels. Each needs a published implementation to cite.
- H4 threshold, `tau` levels, and the `phi` constants (`DEFAULT_SIZE_BINS`,
  `DEFAULT_BAND_NAMES`, segment labels), all still PROVISIONAL in code.
- The IEG-50 measurement above.

### 2026-08-05, later. IEG-50 discovery cost measured, n = 2

    run 1   discovery_s 241.396   tqdm 4.70 s/it   battery 20%, on battery
    run 2   discovery_s 237.751   tqdm 4.64 s/it   battery 22%, charging
    mean    239.574               spread 1.5%

The two runs are genuinely independent processes: `import_s` fell from 13.191 to
6.635 on a warm filesystem cache, which is the expected signature and rules out
the paste duplication that made an earlier n=1 look like n=2.

**The low-battery throttling hypothesis is not supported.** Run 2 was on mains
and was 1.5% faster, which is within run-to-run noise for a CPU job of this
length. The measurement is not an artifact of power state.

Decomposition, with `f` the one-off setup and `f + kp` the k-sample discovery:

    p = (239.574 - 9.301) / 50 = 4.6055 s per integrated-gradient sample
    f = 9.301 - 4.6055          = 4.6955 s

Independently cross-checked against tqdm's own reported rate, mean 4.67 s/it
against a predicted 4.606, agreeing to 1.4%. Two unrelated instruments.

**IEG-50 is 25.8x EAP, not the 51x inferred on 08-04.** The inference treated
every pass as equal and ignored that `batch_src_ablations` runs once; `f` and `p`
happen to be nearly equal at 32 prompts, so EAP's single measured time is roughly
half setup. Third correction of an inference by measurement on this project.

Sweep budget for the confirmed 1,190-cell grid, at 32 prompts, CPU:

    EAP discovery        1,020 cells x   9.301 s =  2.64 h
    IEG-50 discovery       170 cells x 239.574 s = 11.31 h
    evaluation, 10 cuts  1,190 cells x  15.81 s  =  5.23 h
    IEG-1000 slice           5 cells x 4,614.8 s =  6.41 h
                                                  --------
                                                    25.6 h

`evaluation_per_cut_s` is held at the conservative 1.581 from the EAP run;
the two IEG runs returned 1.309 and 1.166.

**Remaining weak link: EAP discovery is still n = 1.** It is 2.64 h of 25.6, so
its uncertainty is not budget-critical, but it should be repeated before the lock
for consistency with the multi-seed rule.

**`n_prompts` is the dominant unfixed variable and was never on the CONFIRM
list.** Every figure above is at 32, a smoke-test size. The per-sample cost is a
pass over the dataloader, so cost scales roughly linearly: at 128 prompts this is
100 h and D5's rented-GPU decision comes back into play. Added as a blocking
pre-registration item.

### 2026-08-05. `n_prompts` found missing; calibration rule fixed before measurement

**VERIFIED** from `auto_circuit/data.py`: `load_datasets_from_json` defaults to
`train_test_size = (128, 128)`, `batch_size = 32`. The instrument's default is
**128 discovery prompts**. `configs/smoke.yaml` uses 16, a value chosen to make a
timing run fast and carrying no scientific standing.

`n_prompts` had never appeared on the CONFIRM list. That was an omission and it
was the largest lever in the design, for a reason that is not about cost.

Seed variance has two sources the design cannot separate after the fact: sampling
noise, and genuine instability of discovery under a fixed specification. Only the
second is of interest. The first shrinks with `n`. The plan's headline is the
ratio of seed variance to analytic-choice variance, so at small `n` that headline
is inflated by a quantity unrelated to the paper's claim, and the correct reviewer
response is that the reported instability is small-sample noise. **`n_prompts` is
a validity constraint, not a budget knob.**

Cost consequence, scaling measured `f` and `p` by 8:

    16 discovery prompts   ~  25.6 h CPU
    128 (library default)  ~ 204   h CPU

204 CPU-hours does not fit before 16 August, so at the default the sweep needs a
GPU, and D17's 20x speedup is an unmeasured guess. That guess is now a schedule
dependency rather than a nicety.

**Decisions (Ajay, 2026-08-05): calibrate `n_prompts` rather than pick it, and
measure the GPU factor before committing to it.**

`preregistration/CALIBRATION.md` written and committed **before either pilot
runs**, which is the only property that makes this a calibration rather than
tuning. It fixes:

- the design: EAP only, RESAMPLE, ABBA, edge-level, 8 seeds, `n` in {16,32,64,128}
- the statistic: mean pairwise Jaccard over 28 seed pairs at an absolute top-500
  cut, stated openly as a calibration-only convention distinct from the
  confirmatory metric-relative `tau`
- the rule: smallest `n` with `J_seed(2n) - J_seed(n) < 0.05`, defaulting to 128
  if the curve has not flattened
- the prohibition: `n` may not be lowered because the resulting budget is
  inconvenient. If the rule returns 128 and 128 does not fit, the schedule or the
  compute changes, not the rule.
- the GPU protocol: both existing smoke configs run **unchanged** on a rented
  CUDA device, so the ratio is a device comparison and not a setup comparison

Estimated cost of calibration 1: about 19 minutes CPU.

**Why measure the GPU factor at all.** Two inferences on this project have now
been corrected by measurement: 12x reuse measured at 4.62x, and 51x IEG measured
at 25.8x. Two for two. There is no basis for treating the third as different.

### 2026-08-05. Calibration 1 result, and the GPU factor measured

**Calibration 1: `n_prompts` = 128 discovery prompts, 256 total.**

    n     J_seed    delta to next
    16    0.5678    +0.0709
    32    0.6386    +0.1042
    64    0.7428    +0.0660
    128   0.8089    -

No delta fell below the committed 0.05, so the curve had not flattened and the
rule fell back to the largest size tested. Selection applied by the script, not
by a human reading the table.

Three observations beyond the selection.

**The deltas are non-monotone.** J_seed rises smoothly but its increments do not:
+0.0709, +0.1042, +0.0660. With 28 pairs per point that puts the sampling error
on each delta at roughly plus or minus 0.03, which is the same order as the 0.05
threshold. The decision is not close, every delta clears the threshold and the
smallest margin is 0.016, so the conclusion is robust to noise of that size. But
the paper reports the deltas, not only the selection, so a reader can see this.

**J_seed at 128 is 0.8089.** Two runs of the identical analytic specification,
differing only in the prompt sample, agree on 81% of a 500-edge circuit. Seed is
not a nuisance term in this design, it is a comparison arm, and analytic-choice
instability must be read against that floor.

**The curve is still climbing at auto-circuit's own default.** That is a
reportable fact about the instrument, not only about P1's design.

Caveat recorded: the calibration statistic is circuit-level Jaccard, not
claim-level flip rate. Claim-level would be the quantity that actually matters,
but it requires the phi constants, which are still PROVISIONAL. Circuit-level is
the conservative proxy and is stated as such.

**Calibration 2: GPU factor measured on Tesla T4.**

    component            Mac CPU     T4        factor
    EAP discovery          9.301     1.339     6.95x
    IEG-50 discovery     239.574    28.638     8.37x
    evaluation per cut     1.581     0.227     6.97x

**D17's 20x guess is wrong. The measured factor is about 7x.** IEG benefits more
than EAP, which is consistent with 51 passes keeping the device busier than 1.

**Fourth inference corrected by measurement on this project**, after 12x reuse to
4.62x, 51x IEG to 25.8x, and `n_prompts` being absent from the design entirely.
The base rate is now high enough that any unmeasured factor in this project
should be treated as unreliable by default.

Environment delta for the comparison: instrument versions identical on both
sides, transformer-lens 2.18.0 and auto-circuit 1.0.1. Only torch differs,
2.13.0 on the Mac against 2.11.0+cu128 on Colab. The ratio is therefore close to
a clean device comparison, with a two-minor-version torch delta as the residual
confound.

Sweep budget at 128 discovery prompts, applying the measured factors:

    EAP discovery      14.8 h / 6.95 =  2.1 h
    IEG-50 discovery   63.5 h / 8.37 =  7.6 h
    evaluation         40.7 h / 6.97 =  5.8 h
    IEG-1000 slice     35.9 h / 8.37 =  4.3 h
                                       ------
                                       ~20 h on a T4

Conservative in the right direction: the factors were measured at 16 discovery
prompts and GPU utilisation improves with batch size, so the real total should be
lower.

**Consequence for D5.** Twenty hours makes Colab Pro viable, which was not
expected. Two conditions if that route is taken: the sweep checkpoints per cell
so a dropped session resumes rather than restarts, and every cell manifest
records `torch.cuda.get_device_name`, with any cell on a different device
discarded and rerun. Done that way the audit trail is stronger than a single
asserted environment hash on a rented box, not weaker.

**Open, and it can still force a rental: VRAM is unmeasured.** `peak_rss_mb` is
host resident set size. The 2.8 GB reported on the T4 says nothing about the 15 GB
card. `peak_vram_mb` added to `Manifest` and instrumented in `scripts/smoke.py`;
`configs/smoke-ieg-128.yaml` added to measure it at the selected dataset size.

### 2026-08-05. VRAM measured; sweep host resolved; two design gaps closed

`configs/smoke-ieg-128.yaml` on a Tesla T4, 128 discovery prompts:

    discovery_s            229.142
    evaluation_per_cut_s     1.756
    peak_rss_mb           2,763.0     (host, uninformative for this question)
    peak_vram_mb          3,651.4     of 15,360 available

**24% of the card. The T4 is not the constraint.** The ablation cache is keyed by
batch and holds source outputs for the whole dataset, so it scales with total
prompts rather than with batch size; raising `batch_size` from 8 to auto-circuit's
default of 32 adds transient activation memory only. `batch_size` therefore stays
a free parameter rather than one pinned by hardware.

**D5 and D17 both resolved. Sweep host is Colab Pro, no rental.**

Scaling verified rather than assumed: IEG-50 discovery was 28.638 s at 16
discovery prompts and 229.142 s at 128, a ratio of 8.00 for an 8x data increase.
Linear.

Budget on measured numbers, 25.7 h. Higher than the 20 h quoted an hour earlier,
which had applied 16-prompt device factors to CPU-at-128 figures. Measuring the
thing directly moved it up by a third, in the direction that matters.

### Two gaps the budget arithmetic surfaced

**1. `tau` named a criterion but never a search.** The plan defined `C(s)` as the
smallest circuit recovering `(1 - tau)` of metric `m`, and never said how that
circuit is located on the ranking. A coarse ladder and a bisection return
different circuits for the same `tau`, and a different circuit is a different
claim. An undeclared researcher degree of freedom inside the definition of the
paper's central object, in a paper about undeclared researcher degrees of freedom.

**Decision (Ajay): fixed logarithmic ladder**, `[10, 20, 50, 100, 200, 500, 1000,
2000, 5000, 10000]`, `C(s)` = smallest rung meeting the criterion on an upward
scan.

Bisection was rejected on soundness, not cost: metric recovery is not guaranteed
monotone in edge count, and bisection assumes a monotonicity it cannot rely on.
An upward ladder scan is well defined either way. Bisection would also have cost
about 15 evaluations against the ladder's 10.

The top rung sits deliberately below the 32,491-edge full model. A specification
needing more than 10,000 edges to recover `(1 - tau)` is **discarded** under
section 7 rather than handed a degenerate whole-model circuit. Including the full
model as a rung would make the criterion trivially satisfiable and convert a
failure into a meaningless claim.

The ladder quantises, so the located circuit overshoots the true minimum. The
metric value at the rung below is computed in the same sweep and retained, so the
overshoot is recoverable at analysis time at zero additional compute. Noted as an
option rather than a commitment.

**2. 25.7 h exceeds a Colab session.** Resume is mandatory, not good practice.

**Decision (Ajay): per-cell manifest, skip if `status: ok`.** The results
directory is the checkpoint; no separate state file to corrupt mid-write. Every
cell manifest records `torch.cuda.get_device_name`, cells that ran on a
non-modal device are discarded and rerun, and the device distribution is
reported.

That last condition is what makes running a confirmatory sweep on ephemeral
infrastructure defensible. Per-cell recorded and verified device homogeneity is
more evidence than a single asserted environment hash on a rented box, not less.

### 2026-08-05. spec.py drift closed; duplicates are now unconstructible

`src/p1/spec.py` had fallen behind four decisions. It enumerated a fully crossed
grid, had no discovery-objective axis, no edge-count ladder, and a docstring
claiming P1 crosses the mean-ablation dataset size, which had been withdrawn
that morning. Closed.

**Changes.**

- `Specification` gains `discovery_objective` as the first canonical field.
- `EDGE_COUNT_LADDER` added: `(10, 20, 50, 100, 200, 500, 1000, 2000, 5000,
  10000)`. Top rung deliberately below the 32,491-edge full model.
- `threshold` is validated to lie strictly in (0, 1). An absolute edge count now
  raises, so the metric-relative convention cannot be silently violated.
- `enumerate_grid` nests corruption within ablation, inserting
  `CORRUPTION_NOT_APPLICABLE` for the two independent operators.
- `ablation_corruption_cells` and `discovery_cells` added. The latter is the
  number the sweep budget scales with and was previously computed by hand in
  prose, which is how it drifted.
- `grid_size` is now a closed form asserted equal to the materialised
  enumeration, so the two cannot diverge.

**The design decision worth recording.** The nesting invariant is enforced in
`Specification.__post_init__`, not only in the enumerator. Pairing `ZERO` or
`TOKENWISE_MEAN_CLEAN` with a real corruption level raises, and pairing a
corruption-dependent operator with the sentinel raises. A duplicate specification
is therefore **unconstructible**, not merely unemitted. If a future script builds
specifications some other way, D18 cannot silently return.

**Verified by running, this session:**

    ablation x corruption cells   17
    discovery cells            1,190
    specifications            14,280
    unique spec_ids           14,280      duplicates 0

All three match `preregistration/PLAN.md` exactly.

**The pin moved, deliberately.** `spec_id` for the canonical specification was
`e1fead883f6cdea2` on the old seven-field object and is now
`1831d8ce1a1673a0`. Adding a field changes every id on disk, which is exactly
what the pinned regression test exists to make loud. Nothing had been written
under the old ids except smoke and calibration output, all of which is
non-confirmatory. **After the lock this literal must not move again.**

Test count 165 to 182.

### 2026-08-05, late. Card comparison: the workload does not scale with GPU class

Both smoke configs run unchanged on T4 and on L4.

    component                       T4        L4      gain
    EAP discovery, 16 prompts      1.339     1.195    1.12x
    IEG-50 discovery, 128 prompts  229.142   172.307  1.33x
    evaluation per cut, 128        1.756     1.333    1.32x
    peak VRAM, 128 prompts         3651.4    3651.4   identical

**L4 is 1.33x the T4 on the heavy path, not the 2 to 3x predicted. Fifth
inference corrected by measurement today.**

The explanation matters more than the number. GPT-2 small is 124M parameters and
`patchable_model` runs many small hooked operations per forward pass, so the
workload is bound by kernel launch and Python overhead rather than by arithmetic
throughput. **It does not scale with GPU class.** INFERRED consequence: A100 and
H100 would also deliver roughly 1.3 to 1.5x while consuming compute units several
times faster. Not measured. Three minutes would settle it if the question is ever
load-bearing; it currently is not.

Peak VRAM is byte-identical across the two cards, which says allocation is
deterministic and 3,651 MB is a property of the workload, not of the device.
Useful: it means the memory headroom conclusion transfers to any card.

Budget: **19.4 h on L4 against 25.7 h on T4.** One fewer session, not a
transformation. Either card is defensible; the choice turns on compute-unit
balance, which is Ajay's to check. Both need identical checkpointing.

Also recorded: installing auto-circuit downgrades Colab's numpy from 2.x to
1.26.4 and emits a wall of dependency conflicts against unrelated preinstalled
packages. None touch anything P1 imports. The environment fingerprint in each
manifest records what actually loaded, so this is noise rather than a
reproducibility problem, but it is written down so nobody investigates it twice.

**Two failed runs preceded these**, both `status: failed` with `peak_vram_mb 0.0`
and `import_s` under 5 s. Cause in both cases: changing Colab runtime type
rebuilds the VM, and the `pip install` cell was not re-run. The failure signature
is distinctive and worth recognising: a fast import failure with zero VRAM.
Mitigation adopted: one self-contained cell that installs, extracts, verifies
CUDA, and runs, starting from `%cd /content` so it is idempotent.

---

## 2026-08-06. Corruption levels resolved from the primary source

`preregistration/CALIBRATION.md` step 1 executed. arXiv:2211.00593 fetched as
PDF; ar5iv had returned an unusable render on 08-05. **Four published
constructions found, not the one I feared, and all in a single source.**

Verbatim, VERIFIED this session.

Section 3, the distribution used for all knockouts:

> "instead of using two names (IO and S) it used three unrelated random names
> (A, B and C). In pABC, sentences no longer have a single plausible IO, but the
> grammatical structures from the pIOI templates are preserved."

Appendix A, "Disentangling token and positional signal in the output of
S-Inhibition heads": *"We constructed six datasets by combining three
transformations of the original pIOI distribution."*

> "Random name flip: we replace the names from a given sentence with random
> names, but we keep the same position for all names. Moreover, each occurrence
> of a name in the original sentence is replaced by the same random name."

> "IO<->S1 flip: we swap the position of IO and S1. The output of S-inhibition
> heads will contain correct token signals ... but inverted positional signals"

> "IO<-S2 replacement: we make IO become the subject of the sentence and S the
> indirect object. In this dataset, both token signals and positional signals are
> inverted."

**Decision (Ajay, 2026-08-06): all four levels.**

### The objection this axis invites, and the answer fixed before results

The same appendix reports that these transformations carry systematically
different information: logit difference is approximated by
`2.31*S_pos + 0.99*S_tok` with 7% mean error. A reviewer will therefore say a
claim shift across counterfactuals the source paper proved are different is close
to tautological, and they will be partly right.

**Secondary outcome pre-registered in response:** `F` is additionally reported for
the `ABC` versus `RANDOM_NAME_FLIP` pair alone. Both are "replace the names with
random names" and differ only in whether the duplicate-name structure survives, so
an analyst choosing between them would not believe they were making a substantive
choice. A flip confined to that pair cannot be dismissed as tautological. Post-hoc
partition of the same runs, zero additional compute, fixed now precisely so it
cannot be introduced later as a rescue.

### Two corrections of my own, made before the decision was acted on

**Arithmetic.** I quoted 17,850 specifications for the four-level option. Wrong.
Correct: `5*4 + 2*1 = 22` ablation-corruption cells, `7*22*2*5 = 1,540` discovery
cells, **18,480 specifications**. Verified against `enumerate_grid`, zero
duplicates.

**An objection I overstated.** I said `IO_FROM_S2` breaks the shared `answers`
field because it changes the correct answer. It does not. VERIFIED from
`mask_gradient_prune_scores`: the metric is computed on `model(batch.clean)`
against `batch.answers`, and the corrupt prompt supplies ablation activations
only, so its own answer never enters. What remains true is that `IO_FROM_S2`
yields a valid IOI sentence with a different answer rather than a degraded one,
which is a substantively different kind of counterfactual and is described as one.

### Grid and budget

    ablation x corruption cells   22
    discovery cells            1,540
    specifications            18,480      unique spec_ids 18,480, duplicates 0

L4 budget 23.76 h, from measured per-cell costs.

### Code

`CORRUPTION_LEVELS` added to `src/p1/spec.py` with the verbatim provenance of
each level in the docstring. `Specification` now validates corruption against
that closed set: an unvalidated free-form string means a typo silently produces a
different `spec_id` and an orphaned results file, which is the failure the pinned
test exists to prevent.

**The pin moved again, deliberately, second time in two days.**
`1831d8ce1a1673a0` to `80c4f62c924f1f99`. Both moves are pre-lock and recorded.
After the lock it freezes.

### 2026-08-06. Corruption transformations implemented and validated against the source

`src/p1/prompts.py` generated only ABC. Three of the four levels had no
implementation, which would have blocked the sweep.

**One construction was genuinely ambiguous from the prose and I did not guess
it.** "We make IO become the subject of the sentence and S the indirect object"
is compatible with several slot layouts, and two of the three I derived first
contradicted the paper's own statement that both signals are inverted.

Resolved from **Figure 9's row labels** rather than the prose. The table crosses
a token signal in {original, random, **S<->IO inverted**} with a position signal
in {original, inverted}. So token inversion means swapping the S and IO names,
and position inversion is the IO<->S1 flip, which on this template scheme is
exactly the ABBA/BABA toggle with names held fixed. `IO<-S2 replacement` is both
composed.

Writing ABBA as `(IO, S1, S2)` and BABA as `(S1, IO, S2)`:

    clean ABBA        (a, b, b)
    RANDOM_NAME_FLIP  (a', b', b')   fresh names, layout held
    IO_S1_FLIP        (b, a, b)      names held, order toggled
    IO_FROM_S2        (a, b, a)      names swapped, order toggled

`(a, b, a)` reads exactly as the paper describes: `a`, the original IO, is now
the repeated subject; `b`, the original S, now appears once as the indirect
object.

**Validated against the paper, not against the derivation.** Measured signal
content of the generated prompts, both template orders:

    ABC                no unique IO                     matches "no single plausible IO"
    RANDOM_NAME_FLIP   pos original, tok random         matches Figure 10 left
    IO_S1_FLIP         pos INVERTED, tok original       matches appendix A
    IO_FROM_S2         pos INVERTED, tok INVERTED       matches appendix A

The tests assert these signal properties rather than the slot layouts, so they
check the implementation against the source paper's claims rather than against my
reasoning. A future edit that changes a construction fails loudly instead of
silently altering a quarter of the corruption axis.

`corrupt_slots` is additive in `src/p1/`; the instrument is untouched. Test count
184 to 197.

### 2026-08-06. Last three sign-offs. The plan has no open decisions.

**Decisions (Ajay, 2026-08-06):**

- `tau` levels **0.05, 0.10, 0.20**. 0.10 is the modal choice in the faithfulness
  literature, 0.05 the strictest in common use, 0.20 permissive enough to yield
  small circuits. Three levels cost no additional discovery, since `tau` is a
  post-hoc cut on an existing ranking.
- H4 threshold **gap > 0.10**. Half the H2 threshold, on the reasoning that a gap
  is a difference of two rates and therefore noisier than either. Judgement call,
  defended as one, with the full bootstrap distribution reported either way.
- `phi` constants **frozen**, with the size bins re-anchored first.

### The phi size bins were nearly a silent design defect

`C(s)` is always a rung of `EDGE_COUNT_LADDER`, so `size_class` is in effect a
function of which rung was selected. The bins at 2% and 10% predated the ladder
and put **six of the ten rungs into `sparse`**:

    10, 20, 50, 100, 200, 500   all below 2% of 32,491 edges

Had discovered circuits clustered below 500 edges, which is entirely plausible for
IOI, `size_class` would have taken one value across the whole grid. MEDIUM
granularity would have collapsed onto COARSE, the nested claim map would have lost
a level, and the loss would have been invisible until after the sweep.

**This is D12 again**: a design feature that would have carried zero variance at
full cost. Found by checking the constants against the ladder rather than by
signing them off.

Re-anchored to **1% and 8%**, splitting the ladder 5 / 3 / 2:

    sparse       10, 20, 50, 100, 200      up to 0.62%
    moderate     500, 1000, 2000           1.54% to 6.16%
    distributed  5000, 10000               15.4% to 30.8%

No rung sits within 20% of a boundary. Both properties are unit-tested against
`EDGE_COUNT_LADDER`, so changing either the bins or the ladder without rechecking
the other now fails loudly. **These constants must not move again.**

### IEG-1000 wording corrected

Section 4 said the slice tests whether IG sample count changes the claim. It
cannot. `INTEGRATED_EDGE_GRADS_PRUNE_ALGO` is `avg_val` at 50 samples and
`INTEGRATED_EDGE_GRADS_LOGIT_DIFF_PRUNE_ALGO` is `avg_diff` at 1000, so the
comparison is confounded across two parameters. The slice compares two published
configurations and nothing finer, and the plan now says so.

### State

**No `[CONFIRM]` markers remain. No PROVISIONAL constants remain.** 200 tests
passing. One blocking checklist item left: `requirements-sweep.lock.txt`, which
requires the Colab runtime that will execute the sweep and is therefore produced
immediately before launch.

### 2026-08-06. Two defects found while starting the sweep runner, one of them mine

Neither would have raised. Both would have surfaced only after the sweep.

**1. `position_mass` had no producer.** `features_from_circuit` accepts it as an
optional argument and nothing in the codebase computed one.
`normalise_position_mass({})` returns `{}`, and `phi_affected` renders an empty
mass as "no single input region". So **`phi_affected` would have emitted one
constant claim across all 18,480 specifications and reported a flip rate of
exactly zero** as an artifact of a missing function rather than as a result.

That is the Article 86(1) map, the affected-person right to an explanation. It is
the part of the regulatory argument no prior work touches and the reason the
two-addressee design was chosen on 08-03.

**Decision (Ajay, 2026-08-06): mean attention probability over labelled input
segments, in the confirmatory grid.**

Precedent rather than invention: arXiv:2211.00593 Figure 10 plots "Average
attention probability of Name Mover Heads" across the IO, S and S2 positions.
Attention over labelled segments is the source paper's own way of describing
where a circuit looks.

Fixed choices, all recorded in CALIBRATION.md 3b rather than left implicit: final
query position; attention heads in the circuit only; **uniform** weighting across
heads; mean over clean prompts; `seq_labels` as the single label source.

Uniform weighting is load-bearing and not laziness. Prune scores live on
different scales across the discovery-objective axis, since the gradient is taken
through logit, prob, logprob or logit_exp, so a score-weighted mass would not be
comparable along that axis. Uniform is scale-free.

Owned in the paper: attention is contested as an explanation (Jain and Wallace
2019; Wiegreffe and Pinter 2019), and an alternative attribution method is a
further axis this work does not cross.

`src/p1/attribution.py` added, torch-free by design so everything that decides a
claim stays testable without a GPU. The tensor extraction lives in the runner.

**2. I anchored the size bins to the wrong denominator, and the tests encoded the
error.**

Earlier today I re-anchored `DEFAULT_SIZE_BINS` to `EDGE_COUNT_LADDER` against
the 32,491-edge graph and wrote tests asserting a 5/3/2 split with no rung within
20% of a boundary.

**`phi` does not operate on edges.** `features_from_circuit` takes nodes,
`components_from_nodes` maps them to `(layer, head)` pairs, and
`n_components_full_model` counts heads plus MLPs: **156** for GPT-2 small.
`size_class` is `len(nodes touched) / 156`, and the map from a ladder rung to the
node count its edges touch is empirical, not analytic.

The constants may or may not be adequate; the justification was computed against
a quantity `size_class` never sees. Worse, the unit tests written alongside
encoded the same mistake, so **they would have kept passing while checking
nothing relevant**. That is the first time on this project an error of mine
reached both the plan and the test suite.

Calibration 3 written into CALIBRATION.md: measure the rung-to-node-count curve
over five seeds, then select bounds by a deterministic optimisation over a fixed
candidate set, with a stated fallback if no bounds can separate the ladder.
Rule committed before the measurement, as with `n_prompts`.

**Also caught, unresolved:** `features_from_circuit(include_mlps_in_full_count)`
carries a docstring saying it must be fixed before the sweep because it shifts
every size class. It is not yet in the pre-registration.

Test count 197 to 214.

### 2026-08-06. The size-bin rule was revised before it ran, and why that matters

Calibration 3's first draft attempted three bins on a linear scale and nothing
else. Before running it I stress-tested `select_size_bins` against plausible
node-count curves. **It returned "degenerate" in most of them**, and for a
structural reason rather than a bug: the node count saturates. By the upper rungs
of the edge-count ladder a circuit already touches most of the 156 components, so
consecutive rungs differ by very little and no bound can sit clear of them.

A rule that is near-certain to fail is not a test. It is a pre-commitment to
losing MEDIUM granularity dressed up as a measurement, which is the opposite of
the both-outcomes-publishable principle the whole protocol rests on.

**Decision (Ajay, 2026-08-06): bin on log node count, with a cascade.**

Revised rule: bins chosen in log10 space; bin count cascades 3 then 2; minimum
separation 0.08 dex, a factor of about 1.20, preserving the original "no rung
within 20% of a bound" intent on the scale the bins are actually chosen on;
candidate grid 45 log-spaced values at 0.05 dex. Class names `sparse / moderate /
distributed` at three bins, `compact / distributed` at two. Degenerate only if
neither admits a solution.

**The revision is legitimate only because it precedes the measurement.** Nothing
had been run and nothing committed. The identical change after seeing the curve
would not be defensible, and the distinction is the entire content of
pre-registration.

Behaviour on synthetic curves, checked before committing:

    geometric, well spread     -> 3 bins
    saturating, plausible      -> 2 bins  (cascade absorbs it)
    hard saturation            -> None    (degenerate, correctly)
    all identical              -> None    (degenerate, correctly)

`DEFAULT_SIZE_BINS` is now marked **PLACEHOLDER, pending calibration 3**, not
frozen. Its docstring records both superseded justifications rather than deleting
them, because the second is the only error on this project that reached the
pre-registration and the test suite together.

**Three stale tests deleted.** `test_size_bins_split_the_edge_count_ladder_five_three_two`,
`test_no_ladder_rung_sits_near_a_size_bin_boundary` and
`test_frozen_constants_have_their_pinned_values` all asserted the edge-based
derivation. They passed, and they checked nothing relevant. Replaced by eight
tests of the selection rule itself, including both degenerate cases.

Also fixed: `include_mlps_in_full_count` is now **forced, not chosen**.
`components_from_nodes` can emit MLP Components, so they appear in the numerator;
a denominator counting attention heads only could yield a fraction above 1 and
`size_class` would fall through every bin. Numerator and denominator must count
the same population. 156 for GPT-2 small.

Test count 214 to 219.

### 2026-08-06. An off-by-one in the node mapping that would have corrupted every claim

Found while writing the node-count pilot, by reading how auto-circuit actually
numbers layers rather than trusting the docstring I had summarised from.

**VERIFIED** from `auto_circuit/model_utils/transformer_lens_utils.py`,
`factorized_src_nodes` and `factorized_dest_nodes`. The layer counter is a plain
`count()` that **begins on the residual terminal, not on block 0**:

    Resid Start          layer 0
    block b attention    layer 2b + 1
    block b MLP          layer 2b + 2
    Resid End            layer 2 * n_blocks + 1

For GPT-2 small: attention at 1, 3, ..., 23; MLPs at 2, 4, ..., 24; Resid End 25.

`block_index` used `ac_layer // 2`. Consequences:

- **Attention was correct.** Layer 2b+1 // 2 = b.
- **Every MLP landed one block too late.** Layer 2b+2 // 2 = b+1. Silent, and it
  would have shifted `layer_band` for every claim containing an MLP.
- **The final MLP and Resid End both mapped to block 12**, outside `[0, 12)`.
  `CircuitFeatures` would have raised, so the sweep would have died rather than
  lied, but only after the first circuit.

Corrected to `(ac_layer - 1) // 2`, which is right for both kinds: attention
`2b+1` gives `b`, MLP `2b+2` gives `b`.

**Separately, the residual terminals were being mapped as MLPs.** They carry
`head_idx is None`, so `components_from_nodes` treated them as MLP blocks. They
are not model components: they are the graph's input and output, they appear in
essentially every circuit, and including them would have added a constant to
every claim. Now dropped by name, so a change in the instrument's numbering
surfaces as an unmapped node rather than as a plausible wrong answer.

**The existing tests encoded the bug.** `test_block_index_conversion`
parametrised `(0,0), (2,1), (22,11)` and passed. All three are wrong under the
verified layout. This is the second time today a test has been found asserting my
reasoning rather than the instrument's behaviour, and the pattern is now clear
enough to state: **a test written from the same derivation as the code tests
nothing.** The fix in both cases was to derive the expectation from the source
rather than from the implementation.

Also removed: two tests exercising `include_mlps_in_full_count=False`, a branch
that is now forced True for consistency between numerator and denominator.

Added: a rung-by-rung pin that attention and MLP of every block b map to b, an
explicit rejection of layer 0 as a terminal, and two tests that terminals are
dropped rather than mapped.

Test count 219 to 221.

**Note on `parallel_attn_mlp`.** The corrected mapping assumes it is False, which
holds for GPT-2 and for the confirmatory grid. Under `parallel_attn_mlp` the MLP
shares the attention layer and the mapping would need revisiting. Recorded in the
docstring so a future model change surfaces it.

### 2026-08-06. Calibration 3 run. Size bins measured and frozen.

`configs/calib-nodes.yaml` on an L4, five seeds, 128 discovery prompts, EAP.

    rung     nodes    sd     frac      selected class
      10       6.8   0.40   0.0436     sparse
      20      13.2   0.40   0.0846     sparse
      50      25.0   0.63   0.1603     moderate
     100      35.2   0.98   0.2256     moderate
     200      54.0   0.63   0.3462     moderate
     500      90.0   1.79   0.5769     distributed
    1000     121.2   2.79   0.7769     distributed
    2000     145.4   1.62   0.9321     distributed
    5000     155.2   0.40   0.9949     distributed
   10000     156.0   0.00   1.0000     distributed

`select_size_bins` returned **three bins**, split 2 / 3 / 5, bounds 0.112202 and
0.446684, minimum margin 0.111 dex against a required 0.08. The cascade to two
bins was not needed. Seed variance is at most 2.8 nodes, so the curve is stable
and the selection is not a coin flip.

`DEFAULT_SIZE_BINS` frozen at those values. A test feeds the measured curve back
through the committed rule and asserts it reproduces the frozen constant exactly,
so a later hand-nudge of a bound fails loudly.

### The sanity table did its job, and validated more than the seam

The table prints the top edges with their raw auto-circuit nodes beside the
`Component`s the seam maps them to. auto-circuit names nodes `A{block}.{head}`
and `MLP {block}`, so the names are an **independent check on the mapping**:

    A9.9    layer 19  ->  a9.9      correct
    A10.7   layer 21  ->  a10.7     correct
    MLP 0   layer 2   ->  m0.0      correct; the old // 2 gave block 1
    MLP 4   layer 10  ->  m4.0      correct; the old // 2 gave block 5
    A11.10  layer 23  ->  a11.10    correct

Resid Start and Resid End appear as edge endpoints and never in the components
column. The terminal filter works.

**The top edges are Wang et al.'s IOI circuit.** A9.9, A9.6, A10.0 are name
movers; A10.7 and A11.10 the negative heads; A10.6, A10.10, A11.2 backup name
movers; A8.10 S2-inhibition; A3.0 duplicate-token; A5.9 induction. Nineteen of
the top twenty edges touch heads in the published taxonomy. EAP is recovering the
known circuit, which is end-to-end evidence that prompts, corruption, discovery
and ranking are all doing what they should. This belongs in the paper as a
validation figure.

### A finding that is not about the bins

**A 500-edge circuit, 1.5% of the graph, already touches 58% of the model's
components, and by 10,000 edges it touches all 156.** Sparsity in edges is not
sparsity in components. Circuit sizes in this literature are almost always
reported as edge counts, and that framing makes circuits look far more localised
than they are at the component level. Worth a paragraph.

### One bug in my own rule, caught by its own test

`select_size_bins` returned `10 ** log10(candidate)`, which does not round-trip:
0.112202 came back as 0.11220199999999998. A bound nobody declared. Fixed by
returning the declared candidate by index rather than reconstructing it. Found
because the test asserted equality with the frozen constant rather than
approximate equality, which is the right strictness for a pre-registered number.

Test count 221 to 224.

### 2026-08-06. The metric layer did not exist either

Found while starting `sweep.py`. `METRICS` in `spec.py` names four metrics and
its docstring says sufficiency and comprehensiveness are "implemented in
`src/p1` as an additive extension". **No such extension existed.** `grep` found
no function computing any of the four.

Worse than the `position_mass` gap: without a metric layer, metric-relative
`tau` cannot be applied at all, so `C(s)` is undefined and the sweep cannot run.
A hard blocker rather than a degradation.

### Two consequences

**1. The budget was wrong by 5.7 h.** `TREE_PATCH` ablates the edges NOT in the
circuit, keeping the circuit, and measures sufficiency. `EDGE_PATCH` is the
complement and gives comprehensiveness. `logit_diff` and `kl_div` come off the
`TREE_PATCH` pass, but comprehensiveness needs the complement, so evaluation is
**two passes per discovery cell**. 11.40 h rather than 5.70. Sweep total
23.8 h to **29.5 h on an L4**.

Note that this was written in a comment in `smoke.py` on 08-04 and I still built
a budget that assumed one pass. Reading one's own notes is apparently also a
verification step.

**2. "Recovering (1 - tau) of metric m" does not parse the same way for all
four.** `kl_div` is a divergence and is zero at the full model, so a ratio to the
full model is undefined.

**Decision (Ajay, 2026-08-06): normalised gap closing, one convention for all
four.**

    recovery(C) = (m(C) - m(empty)) / (m(full) - m(empty))

Two properties make this the right choice rather than merely a workable one.
It is defined for a divergence, because the empty circuit anchors the scale. And
it is **direction-agnostic**: for `kl_div` it reduces to `1 - KL(C)/KL(empty)`,
which increases as the circuit approaches the full model, so no metric needs a
sign flip and therefore no metric can acquire a sign bug. A per-metric convention
is exactly where that class of bug lives.

Recovery is deliberately **not clipped**. Overshoot and undershoot are real, and
clipping would hide a run that is worse than the empty circuit, which is a signal
rather than an untidiness. A metric that scores the full and empty models
identically raises `DegenerateMetric` and the run is discarded, not repaired.

`src/p1/metrics.py` added: `normalised_recovery` and `select_rung`, both pure,
14 tests. Together with `attribution.py` this keeps every function that decides
what `C(s)` is or what claim it maps to verifiable without a GPU.

**One error of mine, in the test rather than the code.** I asserted that a KL
curve would select rungs 1000 and 5000; the arithmetic gives 500 and 2000. Caught
on the first run. Worth recording only because the failure mode was the good one:
the test disagreed with the implementation and the implementation was right.

Test count 224 to 238.

### 2026-08-06. Fifth gap: the segment labels never aligned with tokens

Found while writing `sweep.py`. `generate_ioi_dataset` emits seven `seq_labels`
as if they were token positions. They are not, and cannot be, in three
independent ways:

- prompts tokenise to roughly 15 to 20 tokens, not 7, so `segment_mass` would
  have raised on its own length check on the first cell;
- the three templates have different token counts, so no single positional map
  covers them;
- names tokenise to different numbers of tokens, so positions shift per prompt
  even within one template.

**This one is mine twice over.** I wrote `attribution.py` against a label
contract the dataset never satisfied, and I did it hours after writing the
docstring that claimed `seq_labels` was "the natural source of the segment labels
that `phi_affected` reads".

Two pieces of evidence pointed the same way. auto-circuit stores its own IOI
datasets **per template**, `ioi_{template}_template_{idx}_prompts.json`, because
position-sensitive analysis needs fixed structure. And arXiv:2211.00593 Figure
10, the precedent already cited for this whole method, aggregates attention over
**IO, S and S2**, which are roles, not positions.

**Decision (Ajay, 2026-08-06): aggregate by role, not position.**

`token_role_labels` added: labels each token by **character-span overlap** with
the role's substring in the prompt. Roles are resolved in occurrence order, which
is what separates S1 from S2 when both are the same name. It asserts that the
tokens reconstruct the prompt exactly, because a normalising tokeniser would
misalign every span silently.

`mean_segment_mass` added: role labels vary per prompt, so the mass is computed
per prompt and averaged, rather than computed once against a shared label list.
A prompt contributing an empty mass still counts in the denominator; dropping it
would reweight toward prompts where the circuit happened to attend somewhere
nameable.

Zero-mass roles are **retained**. "Attended nowhere" and "segment absent" must
stay distinguishable, and collapsing them would let a claim silently change
meaning.

Still outstanding for the runner: `generate_ioi_dataset` must record the role
substrings per prompt, and the seven-entry `seq_labels` must go.

Test count 252 to 263.

### The pattern in today's five gaps

`position_mass` had no producer. `block_index` was off by one. Residual
terminals were mapped as MLPs. The metric layer did not exist. Segment labels
never aligned with tokens.

Every one sat in the seam between P1's code and the instrument, or between two
P1 modules written on different days. None was in the statistics, the claim map's
logic, or the specification space, which are the parts with dense unit tests
written against properties rather than against implementations.

**The seams were the untested surface, and writing the runner is what walked
them.** That is worth stating in the paper's limitations: the analysis pipeline
for a multiverse study is itself a specification space, and its own defects are
not visible to the tests that check its components.

### 2026-08-06. Roles recorded per prompt; the seq_labels contract removed

`generate_ioi_dataset` now emits a top-level `p1_roles` list parallel to
`prompts`, mapping `IO`, `S1`, `S2`, `place` and `object` to their literal
substrings in the **clean** prompt. Clean rather than corrupt, because
`position_mass` is computed from attention on the clean prompt.

**`seq_labels` is gone**, and its removal is now pinned by a test that asserts
its absence and states why. A seven-entry positional list could never have
described a prompt that tokenises to 15 to 20 tokens across three templates of
differing length. Keeping a wrong thing because a loader tolerates it is worse
than removing it.

Verified end to end on real generated prompts:

    Then James and David were at the office, and David handed the book to
         IO:James  S1:David      place:office  S2:David      object:book

`S1` and `S2` are the same name and separate correctly by occurrence order,
which is the property the whole role-span approach rests on.

### A validation added because the failure would have been silent

Roles resolve by occurrence order in the prompt string. If a name also occurs
inside the place or object, the span for `IO` or `S1` lands on the wrong
characters and `phi_affected` attributes the decision to the wrong segment. No
downstream test would notice: the mass would still normalise, the claim would
still render, and it would simply be wrong.

`generate_ioi_dataset` now asserts the IO name occurs exactly once and the
subject name exactly twice in each clean prompt, and raises with the offending
prompt otherwise.

**The test for it had to be rewritten to be deterministic.** My first version
supplied colliding names and relied on the sampler drawing one of them, which
passes or fails by luck. Replaced with a construction where every name is a
substring of the only place, so the collision fires on the first prompt whichever
pair is drawn. A flaky test for a silent failure mode is worse than no test.

Test count 263 to 266. `sweep.py` now has every dependency it needs.

---

## 2026-08-06. Sweep validated. Slice inspected. Disclosure written.

### The runner works

`scripts/sweep.py` validated on an L4. Two cells, then four more; the second run
reported `already complete 2` and skipped them. **Resume is proven on real
output**, which was the whole point of the exercise: a dropped Colab session now
costs the cell in flight, not the sweep.

Correction to my own instruction: I told Ajay `--limit 4` should "run only two
more". Wrong. `--limit` means run N cells, not reach N total. With 2 done it
correctly took the next 4, and 48 specifications = 4 cells x 12 confirms it. The
code was right and my description of it was not.

Timing: 45 s per EAP cell. Extrapolated, 1,320 EAP at 45 s plus 220 IEG at
~200 s is **about 29 h**, against the plan's 29.5. The budget holds.

### The discard rate is 29% and it is not a bug

    comprehensiveness  0.84 at rung 10, 0.98 by rung 100
    kl_div             ~0 to rung 500, 0.95 at rung 5000
    logit_diff         ~0 to rung 1000, 0.86 at rung 10000, never 0.90
    sufficiency        ~0 to rung 1000, 0.85 at rung 10000, never 0.90

Ablating the top ten edges destroys 84% of the effect, because those edges are
the name movers writing to the output. Reconstructing the behaviour from a
retained circuit needs thousands. **Necessity is cheap, sufficiency is
expensive**, which is well documented in this literature. The numbers are
behaving correctly and the pre-registered discard rule is doing exactly what it
was written to do.

Discards fall entirely on `logit_diff` and `sufficiency` at strict `tau`.
`sufficiency` discards 6/6 at both 0.05 and 0.10.

### The part that mattered more than the numbers

The checklist line "no pooled confirmatory result seen by anyone" is now
**consumed**. Validating the runner required executing confirmatory cells, and
executing them without looking at the output would have defeated the purpose.

That is defensible. What would not be defensible is quietly adjusting the ladder,
the `tau` levels or the metric set now that the discard structure is visible.
Three things are plainly suboptimal in the current design and every one of them
must stand:

- `sufficiency` contributes nothing at two of three `tau` levels, so 2 of every
  12 specification slots are structurally empty;
- `comprehensiveness` saturates at the first rung and will carry little claim
  variance;
- `logit_diff` and `sufficiency` track each other closely, so the metric axis may
  have three effective dimensions rather than four.

**Nothing was changed.** All three are recorded in `PLAN.md` section 11b as
observations made before the lock, which converts them from things we might later
claim to have anticipated into things we admit we saw early.

`PLAN.md` section 11b written as a full disclosure: what ran, what was inspected,
the curves verbatim, what was not changed, and the timestamp ordering that lets a
reviewer check the claim against the repository history. `DEVIATIONS.md`
populated with the same disclosure so a reader who opens only that file still
finds it.

`results/sweep/` is deleted before the tag and all 1,540 cells rerun after it.
The slice cost five minutes and buys the statement that no reported figure
predates the pre-registration.

### On the suggested finding

The necessity/sufficiency asymmetry, if it survives 1,540 cells across all seven
objectives, is the paper's thesis in miniature: the same circuit is necessary and
not sufficient depending on which metric a provider files. **It is not a result
yet** and the manuscript will not call it one until the full grid has run.

---

## 2026-08-06T18:06:10Z. LOCKED.

    tag     prereg-p1-confirmatory
    commit  b800f5f9985ff9009a2daf74e73b74ada7a42268
    time    2026-08-06T18:06:10Z
    remote  github.com/designer-coderajay/p1-circuit-multiverse

`preregistration/DEVIATIONS.md` is append-only from this moment.

The plan carries 18,480 specifications over 1,540 discovery cells, every axis
level citing a published implementation, every constant either transcribed from
the instrument or selected by a rule committed before the measurement that fed
it, and a measured budget of about 29 h on an L4.

### One thing went wrong at the lock itself

`requirements-sweep.lock.txt` was never committed. It was generated on the Colab
runtime and never downloaded, and the commit meant to carry it reported "nothing
staged; working tree clean". The tag was pushed with the pre-registration's one
unchecked item still unchecked.

**The tag is not being moved.** A tag that moves is not a timestamp. The
environment file goes in afterwards and the first post-lock entry in
DEVIATIONS.md records why, with the audit test stated: the commit adding the lock
file must predate the earliest manifest under `results/sweep/`, or the sweep is
invalid and must be rerun.

No confirmatory number exists yet, so nothing is contaminated. The defect is the
ordering of two commits, not the provenance of a result. Recording it anyway,
because a deviations file that is empty after a lock is usually a file nobody is
being honest in.

### Where the project stands

Gate 1 passed. Gate 2 passed. Gate 3, the lock, done on 2026-08-06 against a
deadline of 2026-08-16: **ten days early**.

Five defects were found in the two days before the lock, all of them in seams
rather than in components, all of them by writing the runner rather than by
reading the code: `position_mass` had no producer, `block_index` was off by one,
the residual terminals were mapped as MLPs, the metric layer did not exist, and
the segment labels never aligned with tokens. Every one would have surfaced only
after burning sweep time.

Six inferences of mine were corrected by measurement across the project: 12x
reuse measured 4.62x, 51x IEG measured 25.8x, 20x GPU measured 7x, L4 predicted
2 to 3x measured 1.33x, `n_prompts` was absent from the design entirely, and the
size bins were anchored to the wrong denominator. That last one reached both the
pre-registration and the test suite before it was caught.

**The lesson worth carrying to P2 and P3:** a test written from the same
derivation as the code tests nothing. Both mapping bugs were found by deriving
the expectation from the instrument's own source and its own naming, not from my
reasoning about it.

---

## 2026-08-07. The sweep was failing 45% of cells. Cause found, fixed, resumed.

Overnight run reached 1,075 attempted cells with **574 `ok`**. The rest carried
`status: failed` with a bare `AssertionError` and no message.

**Cause.** `mask_gradient_prune_scores` defaults `clean_corrupt="corrupt"`, and
`batch_src_ablations` asserts that the argument is non-None **only** for
`RESAMPLE`, `BATCH_TOKENWISE_MEAN` and `BATCH_ALL_TOK_MEAN`. The other four
operators require `None`. `sweep.py` never passed the argument, so four of seven
operators died on every cell.

The arithmetic confirms it exactly: 120 of 220 cells per objective succeed,
four objectives complete plus part of a fifth gives 1,075 attempted and 575 `ok`
against the observed 574.

**Not a Drive problem.** 178 GB free. Checking that first cost thirty seconds and
avoided a day of chasing quotas.

**The fix** is conditional: `"corrupt"` for the three operators that accept it,
`None` for the four that do not.

**Not a design change.** `PLAN.md` fixes `clean_corrupt` at `"corrupt"` *where
the analyst has a choice*; for the other four the instrument allows none. Grid
unchanged at 18,480 over 1,540. The 5/2 corruption-dependency split is unchanged,
because `TOKENWISE_MEAN_CORRUPT` and `TOKENWISE_MEAN_CLEAN_AND_CORRUPT` read the
corrupt distribution through their own `corrupt_dataset` property, not through
this argument.

**No completed work is lost.** The 574 banked cells are all operators that
received `"corrupt"` before the fix and still do. Failed cells are retried
automatically because the runner skips only `status: ok`.

### The uncomfortable part

**This constraint is written down in DESIGN-DELTAS D18, dated 2026-08-04, by me.
I then wrote the runner on 08-06 without acting on it.**

That is the sixth defect in this seam, and it is the same shape as the other
five: the specification space, the claim map and the statistics are covered by
227 tests that run without torch, and every one of these bugs lives in the strip
of code where P1 meets the instrument, which none of those tests can reach.

Two lessons, both worth carrying to P2 and P3.

1. **A constraint recorded in a design document is not a constraint enforced by
   anything.** D18 named this precisely and it still shipped. Findings that
   constrain implementation need to become assertions or tests at the moment they
   are found, not notes to be honoured later by the same person who wrote them.
2. **The seam needs a smoke test that exercises every axis level once.** Seven
   objectives times seven ablations is 49 discovery calls at EAP prices, about
   four minutes, and it would have caught this before the sweep rather than 1,075
   cells into it. That test does not exist and should.

## 2026-08-08. Sweep resumed at 1,100 cells. Two record corrections.

### Run state

Colab VM recycled overnight. Repo re-uploaded and extracted, `auto-circuit==1.0.1`
and `transformer-lens==2.18.0` reinstalled, L4 confirmed. The Drive output folder
had lost its `(1)` suffix, which Drive reassigns once the colliding name is freed,
so the launch path is `/content/drive/MyDrive/p1_sweep` with no suffix.

Resumed 2026-08-08T07:17:45Z. `already complete 1,100`, `to run 440`. Overnight
progress before the VM died: 758 to 1,100.

Remaining time is **INFERRED**, not measured. Objectives run in config order and
IEG-50 is last, so of the 440 outstanding roughly 220 are EAP at about 45 s and
220 are IEG-50 at about 200 s. That is close to 15 h, with the second half far
slower than the first. The slowdown is expected and is not a fault signal.

### Correction 1. The environment pin was never missing

DEVIATIONS post-lock entry 1, written 2026-08-06, records that
`requirements-sweep.lock.txt` was uncommitted at tag time. VERIFIED false today
from `git log -- requirements-sweep.lock.txt`: single commit `054f18a`,
2026-08-04T20:34:51+02:00, two days before the tag. The commit that claimed to
add it touched only two markdown files.

The failure was one of reading, not of process. `nothing staged; working tree
clean` was interpreted as the file being absent when it meant the file was
already present. **That is the fourth time in this project a diagnosis has been
made from a summary line without checking the state it summarised**, and it is
the same shape as the tarball episode, where `Saving p1.tar.gz to p1.tar (1).gz`
sat visible in the output through three failed cycles.

The rule that follows: **a claim about repository state is checked with a command
against the repository, never inferred from what a previous command printed.**

### Correction 2. The stale pin, which is the problem that actually matters

The committed lock records `transformer-lens==3.6.0` and `torch==2.13.0`. The
sweep runs `transformer-lens==2.18.0`, VERIFIED from the executed install
command. Today's torch is unverified. The lock describes the Gate 2 environment
of 2026-08-04, not the confirmatory runtime.

This is survivable only because provenance was never resting on that file.
`src/p1/manifest.py` fingerprints python, platform, machine and six package
versions per cell and stamps the git commit with a `-dirty` suffix, and
`scripts/sweep.py` writes one manifest per discovery cell. Cells from different
images remain separable by `environment_hash` instead of pooling silently.

Design note worth carrying to P2 and P3: **the per-artifact fingerprint saved
this, and the repository-level lock file did not.** A lock file records what one
machine had on one day. A manifest records what produced this number. When the
two disagree, the manifest is the evidence and the lock is documentation.

The lock is left unmodified so the Gate 2 costs in `CALIBRATION.md` keep their
environment. `requirements-confirmatory.lock.txt` is captured from the sweep
runtime at the end of the run.

### Instrument observation, DESIGN-DELTAS D19

`LOGIT_MSE_GRAD_PRUNE_ALGO` emits a broadcasting `UserWarning` from
`auto_circuit/prune_algos/mask_gradient.py:105` on every discovery batch:
`mse_loss` receives operands of different shape and broadcasts rather than
raising. Not fixed, per rule 2. 220 of 1,540 cells. Reported as an observed
property of a published, exported, defensible analytic choice, and reported
whichever way its circuits fall on the specification curve.

### Still owed

- Seam smoke test over every axis level. Six defects have now lived in this seam
  and none was caught by the 266 tests, which cannot import torch.
- `requirements-confirmatory.lock.txt` at end of run.
- EU AI Act date correction: Annex III high-risk obligations deferred from
  2 August 2026 to 2 December 2027 by Regulation (EU) 2026/1744. `docs/ANNEX-IV.md`
  and `preregistration/PLAN.md` still carry the old framing.
- Results-independent manuscript sections.

## 2026-08-11. Sweep complete. Six arms of seven.

### Result

1,320 `ok`, 220 `failed`, every cell terminal. The failed set is exactly
`LOGIT_MSE_GRAD_PRUNE_ALGO`, **VERIFIED** by digest rather than sampled: the 220
failed `discovery_id`s, sorted and hashed, give
`ec06e045141548b6ad3186f31ec64247`, matching the digest computed independently
from `enumerate_grid(configs/sweep.yaml)` over that objective's 220 ids.

Realised grid: **6 objectives, 1,320 discovery cells, 15,840 specifications.**
Discard rate 14.29%. Recorded in DEVIATIONS, 2026-08-11 entry.

Error, identical in all 220: `RuntimeError: Found dtype Long but expected Float`,
raised inside discovery, `data_s` present and `discovery_s` absent. Cause is
INFERRED to be the integral `batch.answers` reaching `mse_loss`, the same call
that has been emitting the D19 shape warning throughout. Not verified until the
installed source is read.

Ajay's call: methods carries the rate and reason, discussion carries the
observation about instrument maturity, abstract does not carry it.

### The seventh defect in the same seam

The count now reads: `position_mass` had no producer, `block_index` off by one,
residual terminals mapped as MLPs, the metric layer absent, segment labels never
aligned to tokens, `clean_corrupt` passed unconditionally, the corruption
sentinel passed to the generator, and now an objective that cannot run at all.

**Every one lived where P1 meets auto-circuit. None was reachable by the 266
tests, because those tests run without torch by design.**

The remedy was written down on 2026-08-07: a smoke test crossing every axis level
once, seven objectives by seven ablations, about four minutes at EAP prices. It
was not written, and the sweep launched without it. Had it existed, this arm would
have failed in minute three rather than after three days of wall clock.

**This is now the single highest-value piece of engineering left in the project,
and it transfers directly to P2 and P3.** The lesson is not "test more". It is
that a test written from the same derivation as the code tests nothing, and that
the only tests which have ever caught anything here are the ones that execute the
instrument.

### Cost accounting, honestly

Three days of wall clock produced 1,320 usable cells and one finding. Of the
elapsed time, the fraction lost to environment plumbing rather than computation
was large: VM recycles, a Drive folder renamed by Drive itself, a tarball upload
that silently wrote to a different filename, and a deletion caused by an
instruction I gave. The compute was never the bottleneck.

### Next

- Verify the dtype cause from installed source before any manuscript sentence.
- Capture `requirements-confirmatory.lock.txt` from the sweep runtime.
- Write the seam smoke test.
- Pre-registered pooled analysis, refitted on the realised 6-level design, with
  the random-circuit null sized to 1,320 rather than 1,540.

### 2026-08-11, later. No manifest had ever been committed

Copying the results in exposed a `.gitignore` defect present since the file was
written. The block read:

```
results/**
!results/.gitkeep
!results/**/manifest.json
```

`results/**` excludes the directories, and git does not descend into an excluded
directory, so a negation for a file inside it can never fire. **Both negations
were dead.** `git ls-files results/` returned exactly one entry, `.gitkeep`. The
manifests from the smoke runs, the calibration pilots and the confirmatory sweep
were all silently untracked.

Fixed by adding `!results/**/` above the file negations, which re-includes the
directories so git descends. VERIFIED with `git check-ignore -v`: `manifest.json`
now matches the negation, `result.json` still matches `results/**`.

**This is the same failure as post-lock DEVIATIONS entry 1 and as D18 shipping
into the runner.** A comment in a config file stating an intention is not the
intention being enforced. The comment said "keep the tree, not the contents" and
the file kept neither. Nothing checked, so nothing complained, and the audit trail
the whole provenance argument depends on did not exist.

Rule that follows, and it is the third time this rule has been written here in
five days: **when a document records a constraint, the same commit must add the
thing that fails when the constraint is violated.** For this one, the check is
`git ls-files results/ | grep -c manifest.json` in CI.

## 2026-08-11. Primary outcome, stage 1. H2 confirmed.

Script committed at `04f8df2` before it produced a number. Plan locked
2026-08-06 at `b800f5f`, tagged `prereg-p1-confirmatory`. Run took 20 s on CPU.

### Primary

`F`, pairwise flip rate of `phi_overseer` at MEDIUM over the confirmatory grid:

```
F        0.7316
95% CI   [0.7247, 0.7380]   bootstrap over specifications, B = 10,000, seed 0
pi*      0.4109
classes  9
n        7,561 specifications
```

**H2 is confirmed.** The rule was `F > 0.20` with the CI lower bound above 0.20.
The lower bound is 0.7247, three and a half times the threshold. Filability fails
at every pre-registered tolerance: `pi* = 0.411` against requirements of 0.95,
0.90 and 0.80.

The two most common claims, 41.1% and 28.5% of specifications, attribute the same
model's behaviour on the same task to **early layers** and to **late layers**
respectively. They are not different emphases of one account. They contradict.

### All six map and granularity combinations

| outcome | n | classes | F | pi* |
|---|---|---|---|---|
| affected COARSE | 7,561 | 2 | 0.3950 | 0.7291 |
| affected MEDIUM | 7,561 | 4 | 0.6597 | 0.4875 |
| affected FINE | 7,561 | 8 | 0.6744 | 0.4786 |
| overseer COARSE | 7,561 | 3 | 0.5733 | 0.4788 |
| **overseer MEDIUM** | 7,561 | 9 | **0.7316** | 0.4109 |
| overseer FINE | 7,561 | 12 | 0.7681 | 0.4109 |

Monotone in granularity, as it must be, since granularities are nested by
construction. Nothing filable at any tolerance in any cell.

**The COARSE rows matter more than the primary for robustness.** `affected` at
COARSE is a two-class claim, the crudest statement the map can make to an
affected person, and it still flips on 39.5% of specification pairs. The result
is not an artefact of fine-grained claim language.

`F` is bounded above by `1 - 1/k` for `k` classes, so the ceiling at MEDIUM is
0.889. The observed 0.7316 is 82% of that ceiling. State the bound in the paper;
a reader is entitled to know `F` is not near 1 by construction.

### The discard rate, and the objection it creates

8,279 of 15,840 specifications discarded, **52.3%**, under the pre-registered
`tau` rule. Strongly non-uniform by metric:

| metric | kept | discarded | rate |
|---|---|---|---|
| comprehensiveness | 3,947 | 13 | 0.003 |
| kl_div | 1,467 | 2,493 | 0.630 |
| logit_diff | 1,270 | 2,690 | 0.679 |
| sufficiency | 877 | 3,083 | 0.779 |

By ablation, `ZERO` and `BATCH_ALL_TOK_MEAN` discard at 0.75, `RESAMPLE` at 0.19.
By objective the spread is narrow, 0.488 to 0.572.

**This was disclosed before the lock.** PLAN.md section 11b records from the
six-cell slice that comprehensiveness reaches 0.84 at rung 10 and 0.98 by rung
100 while sufficiency never reaches 0.90 within 10,000 edges. The pattern is the
one anticipated, at grid scale. It is not a post-hoc discovery and must not be
presented as one.

**The consequence is real and goes in the paper, not a footnote.** The surviving
pool is 52% comprehensiveness against 25% by design. `F` is therefore computed
over a metric-imbalanced set.

**Strongest reviewer objection, stated before anyone raises it:** that `F` is
driven by pooling across metrics which ask different questions, so a
sufficiency-selected and a comprehensiveness-selected circuit differing is not
instability but four separate questions.

Two answers, and the paper needs both. First, Annex IV point 4 requires the filer
to justify "the appropriateness of the performance metrics for the specific AI
system", so the regulation itself treats the metric as a choice the filer makes
and defends. Two filers choosing defensibly produce contradictory Annex IV 2(e)
statements, which is the claim. Second, the answer is empirical and is already
pre-registered: the variance decomposition by axis. **It is not computed yet.**
Until it is, how much of `F` the metric axis carries is unknown, and the paper
claims nothing about it.

### Not yet done

`J_bar` and pairwise `D` (stage 2), variance decomposition (stage 3), the
random-circuit null multiverse and therefore H3 (stage 4), H4 pending the repair
run.

## 2026-08-11. Stage 3. No axis rescues filability.

Definitions committed at `c8e0051` before any value was computed.

### The result that answers the obvious objection

The objection to `F = 0.7316` is that it pools across evaluation metrics which
ask different questions. Arm B answers it directly.

| axis standardised | residual `F` | 95% CI | removes |
|---|---|---|---|
| **metric** | **0.5939** | [0.5803, 0.6063] | +0.1377 |
| ablation | 0.7014 | [0.6939, 0.7075] | +0.0302 |
| discovery objective | 0.7018 | [0.6938, 0.7084] | +0.0298 |
| threshold `tau` | 0.7070 | [0.6981, 0.7149] | +0.0246 |
| corruption | 0.7092 | [0.7008, 0.7166] | +0.0224 |
| prompt variant | 0.7232 | [0.7157, 0.7300] | +0.0084 |
| seed | 0.7307 | [0.7234, 0.7368] | +0.0009 |

**The metric is the largest single lever and it is not enough.** Standardising it
completely, which is the most a standards body could demand of that axis, leaves
`F = 0.594`, still three times H2's threshold and still nowhere near filable at
any tolerance. Every other axis removes 0.03 or less. There is no axis whose
standardisation makes the filing reliable.

That is a stronger result than the pooled `F`. It converts "the evidence is
unstable" into "and here is what fixing the biggest cause buys you, which is not
enough".

All seven intervals are valid: group sizes 1,512 to 2,520, bootstrap bias below
0.0006 on every axis.

### `F_alone`, point estimates only

Flip rate among pairs differing in one axis alone. **No intervals: the
pre-registered bootstrap is invalid here, see DEVIATIONS 2026-08-11.**

    metric 0.6375 | ablation 0.4476 | objective 0.4092 | corruption 0.4049
    prompt 0.3319 | seed 0.2249 | threshold 0.1057

### Seed, and what the axis actually varies

`F_alone(seed) = 0.2249`, ratio to analytic instability 0.3078, both point
estimates only.

**`seed` is not re-run noise and the paper must not call it that.** VERIFIED from
`scripts/sweep.py` lines 236 and 243: the seed is passed to
`generate_ioi_dataset(n_prompts=..., seed=head.seed)` and to
`train_test_size(..., random_seed=head.seed)`. It selects **which prompts are
sampled** and how they are split. Seed variation is therefore sampling
variability of the evaluation set, not nondeterminism of a fixed computation.

That reading is the honest one and it is also the less convenient one: a reviewer
who assumed "seed" meant re-running the same analysis would read 0.2249 as
alarming. It means a different draw from the same task distribution moves the
claim on 22% of pairs, which is a statement about the task, not about determinism.

### Arm A, REML on `log10(selected edges)`, converged

Structural variance shares: corruption within ablation 0.788, residual 0.115,
ablation 0.044, threshold 0.041, metric 0.007, objective 0.003, seed 0.0007,
prompt variant 0.0007.

**Structure and claim disagree, and the disagreement is the interesting part.**
The metric accounts for 0.7% of the variance in circuit *size* and is the single
largest driver of variance in the *claim*. The ablation-corruption interaction
accounts for 79% of size and 3% of claim flipping. **How big the circuit is and
what you are entitled to say about it are governed by different axes.** A
standards body that standardised the ablation operator, the obvious target if you
look at structure, would fix almost none of the filing instability.

State plainly that arm A is the pre-registered estimator on a structural response
and does not explain `F`. Its value is precisely that it disagrees.

### Still owed

EMS cross-check on the balanced five-operator block, `J_bar` and pairwise `D`
(stage 2), the random-circuit null and H3 (stage 4), H4 pending the repair run.

## 2026-08-11. The claim map replays exactly on CPU. Stage 4 is unblocked.

Stage 4 needs a size-matched random-circuit null drawn from the same edge
population as the discovered circuits, pushed through the identical pipeline and
the identical claim map. Two things had to be established first.

### The edge population is reconstructible without the model

The banked `top_edges` union covers **26,888 of 32,491 edges, 82.8%**. Sampling a
"random" circuit from that union would sample from edges some objective already
ranked in its top ten thousand, which is not a null.

`src/p1/graph.py` reconstructs the full population from the graph ordering: three
input slots per attention head, MLPs additionally seeing their own block's heads,
Resid End seeing all 157 non-terminal sources.

    sum over b of [ 3*12*(1+13b) + (1+13b) + 12 ] + 157  =  32,491

**VERIFIED**: 32,491 enumerated, all distinct, and all 26,888 observed edges are
members with zero left over. The count is not fitted to the target; it falls out
of the ordering, and the agreement with what the instrument reports in every
manifest is the check.

### The reconstruction reproduces the sweep exactly

`scripts/sweep.py` built features as
`nodes = [n for e in order[:k] for n in (e.src, e.dest)]`, then
`components_from_nodes`, then `features_from_circuit`. `p1.graph` reproduces that
from edge **names** alone, with no torch and no auto-circuit.

Replayed over every banked specification, comparing against what the GPU wrote:

| quantity | agreement |
|---|---|
| `phi_overseer` COARSE | **7,561 / 7,561** |
| `phi_overseer` MEDIUM | **7,561 / 7,561** |
| component count | **7,561 / 7,561** |

Zero mismatches. This verifies the node parser, the layer-to-block mapping, the
terminal-dropping rule, `layer_band` and `size_class` together, against a ground
truth produced by different code on different hardware. It is also independent
evidence for the paper's claim that `phi` is deterministic, which until now
rested on the assertion that it is written as deterministic code.

**It is not a test I wrote passing a test I wrote.** The comparison target came
out of the sweep on an L4 three days earlier.

### The limitation this exposes, and it is not small

`overseer_key` needs `layer_band` at COARSE and additionally `size_class` at
MEDIUM. Neither touches `position_mass`. **FINE adds `ranked_segments`, and
`affected_key` leads with it at every granularity.** `position_mass` came from
attention cached per `(prompt_variant, seed)` during the sweep, and **that cache
was never written to disk.**

So the null multiverse is computable for `phi_overseer` at COARSE and MEDIUM, and
not for FINE or for `phi_affected` at any granularity, without rerunning the
model.

**The primary outcome is `phi_overseer` at MEDIUM, so H3 is testable as
pre-registered.** The secondary claim-map cells are not, and the paper says so
rather than quietly reporting H3 for one map and letting a reader assume both.

This is the second consequence of the same omission that broke H4: the sweep
recorded conclusions and discarded the intermediates they were computed from. If
the H4 repair run happens, it should write the attention cache as well, which
costs nothing extra once the model is loaded.

## 2026-08-11. Stage 4. H3 separated, and in the opposite direction.

R = 1,000 null multiverses, seed 0, definitions committed at `6e17c58` before any
null value existed.

| granularity | discovered `F` | 95% CI | null `F` | null 95% CI | verdict |
|---|---|---|---|---|---|
| COARSE | 0.5733 | [0.5684, 0.5780] | 0.4829 | [0.4751, 0.4912] | separated |
| **MEDIUM (primary)** | **0.7316** | [0.7247, 0.7380] | **0.6774** | [0.6734, 0.6810] | **separated** |

The intervals do not overlap at either granularity and the discovered median lies
outside the null interval, so by the pre-registered rule **H3 is rejected: claim
instability is clearly separated from the size-matched random null.**

### The direction is the finding

The separation runs the wrong way for interpretability. **Discovered circuits
produce *less* stable claims than random circuits of the same size.** Modal share
tells the same story: 0.4109 for discovered against 0.5244 for the null at
MEDIUM. A randomly drawn circuit yields a more reproducible Annex IV statement
than one produced by a published discovery algorithm.

PLAN.md section 2 recorded the expectation that a circuit-level test would
separate trivially, since a 500-edge circuit has `J_rand = 0.008`, and stated H3
about the claim precisely to avoid that. The claim-level test did separate, but
the anticipated reading was "discovered circuits carry information random ones do
not". They do carry different information. It is less consistent information.

### Why, mechanically, and it is not mysterious

`overseer_key` at MEDIUM is `(layer_band, size_class)`. A uniform random draw of
`k` edges spreads across the model, so its layer band is near-constant across
draws at a given `k`, and its size class is a near-deterministic function of `k`.
Discovery does the opposite: it concentrates edges, and *where* it concentrates
depends on the objective and the ablation operator. The concentration that makes
a circuit interpretable is exactly what makes the resulting claim specification
dependent.

**That is the paper's thesis stated in a null comparison rather than asserted.**

### The strongest objection, and it needs answering before submission

At `k = 10,000`, which is 2,067 of the 7,561 specifications, a uniform random
circuit almost certainly touches all 156 components. Those draws collapse to one
claim by construction, which depresses null `F`. A reviewer will say the null is
degenerate at large `k` and that the comparison is therefore unfair.

The answer cannot be to re-specify the null after seeing this. What the paper
should do is **report the null's claim distribution by circuit size** as a
descriptive diagnostic, labelled exploratory, and let a reader see exactly where
the null's stability comes from. If the separation survives only at small `k`,
say so.

Not yet computed. It is a limitation, not a result, until it is.

### Scope, restated so it is not overlooked

The null covers `phi_overseer` at COARSE and MEDIUM. FINE and `phi_affected` need
`position_mass`, which the sweep never wrote. **H3 is decided for the primary
outcome only**, and the paper says so rather than reporting one map and letting a
reader assume both.

## 2026-08-11. The size diagnostic reverses the direction of H3's reading.

Exploratory, not pre-registered, no decision depends on it. Run because the
obvious reviewer objection to stage 4 was that the null is degenerate at large
circuit sizes. **The objection is correct, and it matters more than expected.**

### Flip rate within each circuit size, MEDIUM, R = 60

| size | n specs | discovered `F` | null `F` | discovered classes | null classes |
|---|---|---|---|---|---|
| 10 | 2,492 | 0.4543 | **0.7331** | 3 | 6 |
| 20 | 489 | 0.3380 | **0.6622** | 4 | 3 |
| 50 | 519 | 0.4639 | **0.7310** | 3 | 6 |
| 100 | 242 | 0.5792 | 0.6584 | 3 | 3 |
| 200 | 199 | 0.5122 | 0.6366 | 4 | 3 |
| 500 | 236 | **0.4258** | 0.1421 | 3 | 3 |
| 1,000 | 380 | **0.5133** | 0.0000 | 3 | 1 |
| 2,000 | 312 | **0.5714** | 0.0000 | 3 | 1 |
| 5,000 | 625 | 0.0000 | 0.0000 | 1 | 1 |
| 10,000 | 2,067 | 0.0000 | 0.0000 | 1 | 1 |

**With size held fixed: discovered 0.2746, null 0.4230.**

### What this does to the stage 4 conclusion

The pre-registered comparison stands exactly as computed and is not revised: at
MEDIUM, pooled discovered `F = 0.7316` against null `0.6774`, intervals disjoint,
H3 rejected. That is what the plan specified and it is what the plan gets.

**But the direction of the pooled result is an artefact of the size
distribution.** Once size is held fixed the ordering reverses, and it reverses by
a wide margin. The null is *more* unstable than discovery at every size from 10
to 200 edges, and degenerate from 1,000 upward where a uniform draw touches all
156 components and can only produce one claim.

The pooled figures compare a discovered multiverse whose instability is spread
across sizes against a null whose instability is concentrated at small sizes and
zero at large ones. Those are not the same comparison.

**The honest report is both numbers, with the diagnostic table, and a statement
that the pooled null comparison is uninformative about the direction.** Reporting
only the pooled result would state something the data does not support. Reporting
only the within-size result would discard a pre-registered outcome because it
became inconvenient. Neither is acceptable.

### A second thing this exposes, and it is not small

At 5,000 and 10,000 edges the **discovered** multiverse also collapses to a
single class, `F = 0`. That is 2,692 of 7,561 specifications, **36%**,
contributing no flips at all. All of the primary outcome's instability comes from
circuits of 2,000 edges or fewer.

And fixing size alone drops discovered `F` from 0.7316 to 0.2746, a larger drop
than standardising any pre-registered axis, including the metric at 0.5939.
**Circuit size is not an axis of the design; it is an outcome of the `tau` rule.**
So the largest single driver of claim instability is the selection rule choosing
different rungs, not any analytic choice the design varies.

That is a real result and it is uncomfortable, because `size_class` is one of the
two fields in the MEDIUM key. The check that keeps it from being circular is
COARSE, which is `layer_band` alone with no size term: `F = 0.5733` pooled. Layer
attribution flips on 57% of pairs with no size component in the claim at all. The
finding survives, but the paper must show that check rather than assert it.

### Owed before write-up

`F_within(size)` at COARSE, to state the layer-only instability at fixed size.
Not computed. Until it is, the sentence "the finding survives with size held
fixed" is INFERRED from the COARSE pooled figure, not measured.

## 2026-08-11. The number that decides the paper: COARSE with size held fixed.

Exploratory, and the most hostile test the data allows. `phi_overseer` at COARSE
is `layer_band` alone, with **no size term in the claim**, evaluated **within
each circuit size**. Any instability left cannot be an artefact of the `tau` rule
selecting different rungs, because size is constant, and cannot be circular,
because size is not in the key.

| granularity | pooled `F` | size held fixed | 95% CI | bias |
|---|---|---|---|---|
| **COARSE** | 0.5733 | **0.2706** | **[0.2550, 0.2859]** | -0.00018 |
| MEDIUM | 0.7316 | 0.2746 | [0.2589, 0.2901] | -0.00019 |

Bootstrap over specifications, B = 10,000, seed 0. Valid here where it was not
for stage 3's `alone` family: the smallest size group holds 199 specifications,
so self-pair inflation is order 1/199 and the measured bias is 0.0002.

**The CI lower bound is 0.2550, above H2's threshold of 0.20.**

Strip every trace of circuit size from the claim, hold size constant, and where
in the model the behaviour is attributed still flips on **27% of specification
pairs**, with the interval clear of the pre-registered threshold. The finding is
not a selection-rule artefact.

### And discovery does beat the null once the comparison is fair

At fixed size, discovered 0.2706 against null 0.3822 at COARSE, 0.2746 against
0.4230 at MEDIUM. **Discovered circuits are more stable than size-matched random
ones.** They carry real information. They are simply not stable enough to file.

That is a better paper than "no better than random". It concedes that circuit
discovery works, and shows that working is not sufficient for the evidentiary
standard Annex IV assumes.

### The spine, as it now stands

1. Pooled `F = 0.7316` [0.7247, 0.7380]. **H2 confirmed**, threshold 0.20.
2. Standardising the metric, the largest axis lever, leaves `F = 0.5939`. No
   axis rescues filability.
3. Much of the pooled figure is circuit-size variation, and **size is not an axis
   of the design**; it is an outcome of the `tau` rule. Fixing it drops `F` to
   0.2746, a larger drop than any pre-registered axis.
4. Remove size from the claim entirely and hold it fixed: `F = 0.2706`
   [0.2550, 0.2859]. Still above threshold.
5. **H3 rejected** on the pre-registered pooled comparison, but the direction of
   that comparison is a size artefact and the paper reports both readings.
6. At fixed size discovery beats the null, so the instability is not noise.

Every one of 2 through 6 weakens the headline of 1, and each is reported. A
paper that reported only 1 would be making a claim its own data does not support.

### Still owed

`J_bar` and pairwise `D` for P0 (stage 2), the EMS cross-check on the balanced
five-operator block, H4 pending the repair run, and the FINE and `phi_affected`
null which needs the attention cache the sweep never wrote.

## 2026-08-11. Stage 2. P0: circuits are almost disjoint, claims are not.

Exact over all 28,580,580 specification pairs, not sampled. 7,561 specifications
hold 3,218 distinct circuits, so the pair space collapses to 5,176,153
distinct-circuit pairs plus a closed form for the identical ones. Sets are held
as 32,491-bit Python ints, whose `&` and `.bit_count()` run in C; the bitmask
Jaccard is checked against `p1.multiverse.jaccard_similarity` on sampled pairs
rather than trusted.

```
J_bar   0.1396   95% CI [0.1377, 0.1418]   bootstrap over specifications, B=10,000, seed 0
```

**P0 holds emphatically.** Expected pairwise overlap is 0.14, nowhere near 1.

### The distribution, which says more than the mean

| quantile of pairwise `D` | value |
|---|---|
| 1% | 0.196 |
| 5% | 0.470 |
| 25% | 0.788 |
| **50%** | **0.960** |
| 75% | 0.998 |
| 95% | 0.999 |

**The median pair of circuits shares 4% of its edges.** Half of all specification
pairs are, to a first approximation, disjoint objects. Only 1% of pairs reach
`J > 0.8`.

Against chance: median circuit size is 200 edges, and the analytic line adopted
from 2606.06267, `J_rand = k / (2N - k)`, gives 0.0031 there. So `J_bar` sits
about 45x random, comfortably inside the 4x to 27x band they report, and far
enough above chance that the earlier warning stands: at this scale any overlap
above roughly one percent already beats chance, so "better than random" is not
evidence of anything.

### The tension this creates, and it favours the paper

Circuits from different defensible specifications are nearly disjoint, `J_bar` =
0.14. Yet with size held fixed their COARSE claims agree on 73% of pairs,
`F` = 0.2706.

**`phi` compresses enormously.** It maps a 32,491-dimensional object to 3 classes
at COARSE and 9 at MEDIUM. Two circuits sharing 4% of their edges can and often
do produce the same sentence.

That means **`F` is a conservative floor on disagreement, not a ceiling.** The
filing language hides most of the underlying divergence, and the instability that
survives compression is the part a regulator would actually see. A reviewer
tempted to argue `F` is inflated by a fine-grained claim map has the relationship
backwards, and the number to put in front of them is this one: the objects agree
on 4% of their content and the sentences still disagree a quarter of the time.

### Status of the pre-registered outcomes

| | outcome | status |
|---|---|---|
| P0 | `J_bar` = 0.1396 [0.1377, 0.1418] | reported, premise holds |
| H2 | `F` = 0.7316 [0.7247, 0.7380] > 0.20 | **confirmed** |
| H3 | pooled separated; direction is a size artefact | **rejected, both readings reported** |
| H4 | not computable from the sweep | awaiting repair run |

Still owed: the EMS cross-check on the balanced five-operator block, H4, and the
FINE and `phi_affected` null.

## 2026-08-11. H4 supported as pre-registered. Kappa says why that is not the whole story.

Repair run complete, 1,317 cells, 0 mismatched, 0 failed, 0 specifications
without verdicts. 128 examples per circuit, 3,218 distinct verdict vectors.

### The pre-registered result

```
F (claim instability)     0.7316
agreement rate            0.6028
functional instability    0.3972
gap                       0.3344   95% CI [0.3297, 0.3394]
threshold                 0.10
```

**H4 is supported.** The interval lower bound is 0.3297, more than three times the
threshold fixed on 2026-08-06.

### Cohen's kappa is 0.0146, and it changes the reading

Raw agreement of 0.60 sounds like partial functional equivalence. Kappa says it is
not. **0.0146 is chance-level agreement.** The 60% is almost entirely explained by
both circuits being right about the same fraction of the time, not by them being
right about the same examples.

Kappa by circuit size, with mean accuracy alongside:

| size | circuits | mean accuracy | agreement | kappa |
|---|---|---|---|---|
| 10 | 890 | 0.510 | 0.5223 | 0.0438 |
| 20 | 255 | 0.494 | 0.5139 | 0.0316 |
| 50 | 250 | 0.552 | 0.5201 | 0.0303 |
| 100 | 133 | 0.562 | 0.5316 | 0.0467 |
| 200 | 100 | 0.610 | 0.5577 | 0.0351 |
| 500 | 113 | 0.765 | 0.7041 | 0.0295 |
| 1,000 | 158 | 0.846 | 0.7816 | 0.0324 |
| 2,000 | 165 | 0.877 | 0.8179 | 0.0263 |
| 5,000 | 345 | 0.921 | 0.8563 | 0.0157 |
| 10,000 | 809 | 0.947 | 0.9179 | 0.0228 |

**Kappa sits between 0.016 and 0.047 at every size.** Agreement climbs from 0.52
to 0.92 purely because accuracy climbs from 0.51 to 0.95. Two circuits from
different specifications agree about *which* examples they get right at chance,
at every scale.

**This refutes the phantom-specialization objection rather than conceding it.**
Red-team F1 held that P1's flip rate might be measuring which member of an
equivalence class the discovery algorithm sampled. If that were so, circuits would
be functionally interchangeable. They are not. They are structurally near-disjoint
at `J_bar = 0.1396` **and** functionally uncorrelated at kappa 0.02. Whatever P1
is measuring, it is not one mechanism wearing different clothes.

### The within-size check, which the pooled gap does not survive

Same trap as H3. Third time in this project that pooling across circuit size has
manufactured an effect.

| size | `F` | functional instability | gap |
|---|---|---|---|
| 10 | 0.4543 | 0.4777 | **-0.0235** |
| 20 | 0.3380 | 0.4861 | **-0.1480** |
| 50 | 0.4639 | 0.4799 | **-0.0160** |
| 100 | 0.5792 | 0.4684 | +0.1109 |
| 200 | 0.5122 | 0.4423 | -0.0301 below threshold at +0.0699 |
| 500 | 0.4258 | 0.2959 | +0.1299 |
| 1,000 | 0.5133 | 0.2184 | +0.2950 |
| 2,000 | 0.5714 | 0.1821 | +0.3894 |
| 5,000 | 0.0000 | 0.1437 | **-0.1437** |
| 10,000 | 0.0000 | 0.0821 | **-0.0821** |

**The gap fails the 0.10 threshold at 6 of 10 sizes and is negative at 5.** At
both ends of the size range the mechanisms differ *more* than the filings do,
which is the reverse of H4's statement. The pooled 0.3344 is carried entirely by
the middle band, 500 to 2,000 edges.

### What the paper must therefore say

1. **H4 is supported on the pre-registered quantity.** That is not withdrawn and
   the rule was fixed before any verdict existed.
2. **The supporting gap does not survive holding circuit size fixed**, and the
   per-size table is reported next to it, not in an appendix.
3. **"Filings differ where mechanisms do not" is too strong.** The mechanisms
   differ a great deal: functional instability is 0.40 pooled and 0.48 at the
   smallest sizes. The defensible sentence is that filings differ *more* than
   mechanisms across part of the size range, and less at the extremes.
4. **The strongest claim the data supports is the kappa result**, and it is not
   the pre-registered one: circuit behaviour is uncorrelated across defensible
   specifications at every scale tested.

### The methodological point this has now earned

Circuit size is not an axis of the design. It is an outcome of the `tau` rule.
It has now distorted three separate pooled quantities: `F` itself, the direction
of the H3 null comparison, and the sign of the H4 gap. **Any pooled statistic in
this design must be reported with its within-size decomposition.** That belongs in
the methods section as a general finding about multiverse designs whose
specifications select objects of different sizes, not as a caveat on three results.
