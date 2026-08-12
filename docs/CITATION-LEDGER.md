# Citation ledger, Paper 1

Append-only. Never rewrite a row; add a dated correction row instead.

`State` is one of `VERIFIED`, `RECALLED`, `DISPUTED`, `NOT FOUND`.

**VERIFIED** means the record was fetched in a working session and the fetched
page confirmed every field written here. Recall is not evidence, however
confident. Re-verify before submission: a verification older than the last
substantive edit to the section citing it does not count.

**Verifying a record is not verifying a claim.** A row marked `VERIFIED` below
establishes that the paper exists with that title, those authors, and that
venue. It does not establish that any finding attributed to it is accurate.
Findings must be confirmed against the PDF and recorded separately in the
Claims table.

---

## Records

Verified 2026-08-03 by fetching `https://arxiv.org/abs/<ID>`.

| ID | Title as fetched | Authors | Venue | Date | State | Notes |
|---|---|---|---|---|---|---|
| 2407.08734 | Transformer Circuit Faithfulness Metrics are not Robust | Joseph Miller, Bilal Chughtai, William Saunders | CoLM 2024, per Comments field | Submitted 11 Jul 2024, v1 only | VERIFIED | Closest prior work. Ships `github.com/UFO-101/auto-circuit`. **Title differs between arXiv and the venue of record**: the project BibTeX gives *Transformer Circuit Evaluation Metrics Are Not Robust*, COLM 2024, oral spotlight. Cite the COLM title. See DESIGN-DELTAS D6. |
| 2409.09951 | Optimal Ablation for Interpretability | not captured | NeurIPS 2024 per brief, **venue not verified** | not captured | VERIFIED (abstract matches) | Abstract confirms the optimal-ablation method and its use for circuit discovery. Author list and venue still need fetching before citing. |
| 2502.20914 | Everything, Everywhere, All at Once: Is Mechanistic Interpretability Identifiable? | Méloux et al., **full list not verified** | ICLR 2025, **not verified** | not captured | VERIFIED (ID and title, via arxiv.org URLs in search) | Resolves the brief's name-only "Méloux et al. 2025". Foundational for the non-identifiability premise. Fetch the abs page and complete this row before citing. |
| 2504.13151 | MIB: A Mechanistic Interpretability Benchmark | Aaron Mueller, Atticus Geiger, Sarah Wiegreffe, Dana Arad, and 19 others incl. David Bau, Yonatan Belinkov | ICML 2025, per Comments field | Submitted 17 Apr 2025, v2 9 Jun 2025 | VERIFIED | Reports attribution and mask-optimisation methods best on circuit localisation. Relevant to instrument choice. |
| 2501.16496 | Open Problems in Mechanistic Interpretability | Lee Sharkey, Bilal Chughtai, Joshua Batson, and 26 others incl. Conmy, Nanda, Bau, Geiger, Geva, Tegmark | none stated | Submitted 27 Jan 2025, v1 | VERIFIED | Review. Use for framing, not for a specific empirical claim. |
| 2308.14272 | Goodhart's Law Applies to NLP's Explanation Benchmarks | Jennifer Hsia, Danish Pruthi, Aarti Singh, Zachary C. Lipton | none stated | Submitted 28 Aug 2023, v1 | VERIFIED | Sufficiency and comprehensiveness can be inflated without changing predictions or explanations. Directly relevant to D2. |
| 2510.00845 | Mechanistic Interpretability as Statistical Estimation: A Variance Analysis | not captured | not captured | not captured | VERIFIED (ID and title) | Served as PDF, no metadata extracted. A v2 title seen in search adds "of EAP-IG". Confirm which version to cite. Second-closest prior work. |
| 2606.06267 | Many Circuits, One Mechanism: Input Variation and Evaluation Granularity in Circuit Discovery | Alireza Bayat Makou, Jingcheng Niu, Subhabrata Dutta, Iryna Gurevych (UKP Lab, TU Darmstadt) | not captured | Submitted 4 Jun 2026 | VERIFIED (ID, title, authors) | **The paper that most threatens P1.** Findings are RECALLED from search summaries only. Read in full before relying on anything. See DESIGN-DELTAS D4. |
| 2606.00033 | Make Mechanistic Interpretability Auditable: A Call to Develop Guidelines via Continuous Collaborative Reviewing | not captured | not captured | not captured | VERIFIED (ID and title) | P1 answers this call. Say so explicitly in the paper. |
| 2512.13907 | Assessing High-Risk AI Systems under the EU AI Act: From Legal Requirements to Technical Verification | Alessio Buscemi, Tom Deckenbrunnen, Fahria Kabir, Kateryna Mishchenko, Nishat Mowla | none stated | Submitted 15 Dec 2025, v3 3 Apr 2026 | VERIFIED | Maps AI Act requirements to verification activities. Cite v3. |

## Surfaced during verification, not yet in the brief

| ID | Title | Relevance | State |
|---|---|---|---|
| 2602.16823 | Formal Mechanistic Interpretability: Automated Circuit Discovery with Provable Guarantees | If circuit discovery admits provable robustness guarantees, P1 must address why instability persists in practice. Potential threat. | RECALLED, seen only as a search hit. Fetch. |
| 2607.19317 | CircuitKIT: Circuit Discovery, Evaluation, and Application Toolkit for Mechanistic Interpretability | Candidate second instrument if implementation choice becomes a grid dimension. | RECALLED, seen only as a search hit. Fetch. |
| 2604.09628 | Assessing Model-Agnostic XAI Methods against EU AI Act Explainability Requirements | Nearest work on the regulatory side. Model-agnostic XAI rather than circuits, and not about instability, so it is related work rather than a threat. | RECALLED, seen only as a search hit. Fetch. |

## Resolved from the instrument's own source, 2026-08-04

Extracted by grepping arXiv links out of auto-circuit 1.0.1's docstrings. This is
strong provenance: these are the identifiers the instrument's own authors attach
to the algorithms P1 runs.

| ID | Title | Authors | Date | State | Notes |
|---|---|---|---|---|---|
| 2211.00593 | Interpretability in the Wild: a Circuit for Indirect Object Identification in GPT-2 small | Kevin Wang, Alexandre Variengien, Arthur Conmy, Buck Shlegeris, Jacob Steinhardt | Submitted **1 Nov 2022**, v1 only | VERIFIED, abs page fetched | Resolves the brief's name-only "Wang et al., IOI circuit". **Year discrepancy: arXiv is 2022; auto-circuit cites "(2022)"; 2407.08734 prose cites "(2023)", presumably the ICLR version.** Pick one convention and state it. **Contains a published 7-class head-role taxonomy over 26 attention heads**, see below. |
| 2304.14997 | Towards Automated Circuit Discovery for Mechanistic Interpretability | Conmy et al., full list not yet fetched | 2023 | VERIFIED (ID and title from auto-circuit `ACDC.py` docstring) | Resolves "Conmy et al., ACDC". Fetch the abs page to complete authors before citing. |
| 2305.00586 | not yet fetched | Hanna et al. | 2023 | RECALLED (ID from auto-circuit docstring) | The greater-than task. Relevant if a second task is added. |
| 1703.01365 | not yet fetched | Sundararajan et al. | 2017 | RECALLED (ID from `mask_gradient.py` docstring) | Integrated Gradients. **Cite this for the IEG levels of the discovery-objective axis.** |
| 1712.01312 | not yet fetched | Louizos et al. | 2017 | RECALLED (ID from auto-circuit docstring) | L0 regularisation, underlies subnetwork probing. |
| 2104.03514 | not yet fetched | Cao et al. | 2021 | RECALLED (ID from auto-circuit docstring) | Not yet placed. |
| 2310.10348 | not yet identified | unknown | unknown | **SUPERSEDED, see the correction table below** | Bare URL in auto-circuit source with no citation text. **Resolved later the same day**: it is *Attribution Patching Outperforms Automated Circuit Discovery*, Syed, Rager and Conmy. |

### A finding for phi

Wang et al. 2211.00593 abstract, verbatim: "Our explanation encompasses **26
attention heads grouped into 7 main classes**". That is a **published head-role
taxonomy for IOI**, which is exactly what `phi`'s role categorisation needed and
which was previously flagged as requiring a published source rather than
invention. Extract the 7 class names from the paper and use them as the
pre-registered role mapping, cited to Wang et al.

Also verbatim: they evaluate using "three quantitative criteria -- **faithfulness,
completeness and minimality**". P1 uses faithfulness only. If a reviewer asks why
not the other two, the answer is that they are properties of a single circuit
against a ground truth, whereas P1 measures agreement *between* circuits. Worth
one sentence.

## The last four name-only references, resolved 2026-08-04

| Was | Now | State | Notes |
|---|---|---|---|
| "Nanda et al., attribution patching" | **arXiv:2310.10348**, *Attribution Patching Outperforms Automated Circuit Discovery*, **Aaquib Syed, Can Rager, Arthur Conmy**. NeurIPS 2023 ATTRIB Workshop. Submitted 16 Oct 2023, v2 20 Nov 2023 | **VERIFIED**, abs page fetched | **The brief's attribution was wrong.** The citable paper is Syed, Rager and Conmy, not Nanda. Nanda's attribution patching is a blog post, citable as such but not a peer-reviewed paper. **Correct this before writing.** This also resolves the bare `2310.10348` URL found in auto-circuit's source. Abstract, verbatim: the method requires "just two forward passes and a backward pass", which is the reason P1's measured EAP discovery is 9.3 s. |
| "Steegen et al., multiverse analysis" | Steegen, S., Tuerlinckx, F., Gelman, A., and Vanpaemel, W. (2016). *Increasing Transparency Through a Multiverse Analysis*. **Perspectives on Psychological Science, 11(5), 702-712.** DOI **10.1177/1745691616658637** | **RECALLED-plus**: title, authors, venue, volume, pages and DOI all agree across a Sage journal page, Semantic Scholar and Gelman's own posted copy, but the DOI has **not been resolved directly**. Resolve `doi.org/10.1177/1745691616658637` before the bibliography is final. | Method provenance for the whole multiverse design. |
| "Simmons et al., researcher degrees of freedom" | Simmons, J. P., Nelson, L. D., and Simonsohn, U. (2011). *False-Positive Psychology: Undisclosed Flexibility in Data Collection and Analysis Allows Presenting Anything as Significant*. **Psychological Science, 22(11), 1359-1366.** DOI **10.1177/0956797611417632**, PMID 22006061 | **RECALLED-plus**, same caveat | The origin of "researcher degrees of freedom". |
| "Simonsohn et al., specification curve analysis" | Simonsohn, U., Simmons, J. P., and Nelson, L. D. (2020). *Specification Curve Analysis*. **Nature Human Behaviour, 4(11), 1208-1214.** DOI **10.1038/s41562-020-0912-z** | **RECALLED-plus**, same caveat. **A Publisher Correction exists**, DOI 10.1038/s41562-020-00974-w. Check whether it affects anything P1 relies on. | Figure 1 and the joint-inference procedure. |

**Author-order note.** The same three people appear in both 2011 and 2020 in
different orders: Simmons, Nelson and Simonsohn in 2011; Simonsohn, Simmons and
Nelson in 2020. Getting this backwards is a small error that signals the
bibliography was not checked. It is right above.

**`RECALLED-plus` is a new state and it is deliberately not `VERIFIED`.** These
are journal articles, not arXiv preprints, and the fields above come from search
results and publisher landing pages rather than from resolving the DOI. The
agreement across independent sources is strong, but the standing rule says
verified means fetched. **Resolve all three DOIs before the bibliography is
final.**

**All six name-only references from the brief are now resolved to identifiers.**
None is yet at full `VERIFIED` except 2310.10348, 2211.00593 and 2304.14997.


## Still name-only, must be resolved to identifiers before citing

All **RECALLED**, none verified.

| Reference | Needed for | Status |
|---|---|---|
| Wang et al., IOI circuit | Primary task. Cited in almost every sentence about IOI. | Resolve to arXiv ID and fetch. |
| Conmy et al., ACDC | Discovery algorithm shipped in auto-circuit. | Resolve and fetch. |
| Nanda et al., attribution patching | Discovery algorithm shipped in auto-circuit. | Resolve and fetch. |
| Steegen et al., multiverse analysis | Method provenance for the whole design. | Resolve and fetch. |
| Simmons et al., researcher degrees of freedom | Framing. | Resolve and fetch. |
| Simonsohn et al., specification curve analysis | Figure 1 and the joint-inference procedure. | Resolve and fetch. |
| Mueller et al. 2026, non-identifiability | Brief lists this separately from Méloux. May be 2504.13151 misattributed, or a distinct 2026 work. | Ambiguous. Resolve before citing. |

## Primary legal text

Regulation (EU) 2024/1689. **Read 2026-08-03 from the AI Act Service Desk**
(`ai-act-service-desk.ec.europa.eu`), an official Commission site run by DG
CNECT which states it reproduces the official version of 13 June 2024:
**Annex III, Annex IV, Articles 13, 14, 86.** Still unread: **Article 11**.
All strings are from a Commission rendering, **not the Official Journal**, and
must be cross-checked against the OJ before entering the manuscript.

Superseded note: Read the regulation itself from EUR-Lex, not summaries and not
artificialintelligenceact.eu, before writing any sentence that characterises
what Annex IV requires. The entire regulatory premise of P1 rests on this.

## Claims table

Separate from records. A claim enters here only after being located in the
source PDF.

| Claim | Attributed to | Located in source | Verified on |
|---|---|---|---|
| "discovery algorithms sample from an equivalence class of valid subgraphs rather than recovering a unique mechanism" | 2606.06267 | Abstract, quoted verbatim | 2026-08-03 |
| "structural differences between circuits are not sufficient evidence for distinct mechanisms" | 2606.06267 | Abstract, quoted verbatim | 2026-08-03 |
| "a core shared across most bands recovers at least 99% of circuit performance" | 2606.06267 | Abstract, quoted verbatim | 2026-08-03 |
| "source-level evaluation inflates apparent faithfulness, while edge-level evaluation reveals the many-to-one mapping from structure to function" | 2606.06267 | Abstract, quoted verbatim | 2026-08-03 |
| 75 circuits, Literal Sequence Copying, four frequency bands plus control, five Pythia models 70M to 1.4B | 2606.06267 | Abstract, quoted verbatim | 2026-08-03 |
| "We focus on Mean and Resample Ablations in this work." | 2407.08734 | Section 3.1.3, quoted verbatim | 2026-08-03 |
| "In this work we will focus on the metrics used by the respective authors of the circuits that we study, but note these choices are also in general free." | 2407.08734 | Section 3.2, quoted verbatim | 2026-08-03 |
| Mean ablation carries "an additional choice in the size of the mean ablation dataset" | 2407.08734 | Section 3.1.3, quoted verbatim | 2026-08-03 |
| The IOI circuit "is specified as an edge-level circuit, but Wang et al. (2023) evaluate its faithfulness via a node-wise ablation methodology" | 2407.08734 | Section 4, quoted verbatim | 2026-08-03 |
| Section 3.1 enumerates five ablation-methodology dimensions | 2407.08734 | Section headings 3.1.1 to 3.1.5 | 2026-08-03 |
| Neither paper contains any regulatory, conformity, audit, or technical-documentation analysis | 2407.08734 and 2606.06267 | Zero-hit term counts over full fetched text | 2026-08-03 |
| "the general logic of the AI system and of the algorithms" (design specifications frame) | Reg (EU) 2024/1689 Annex IV 2(b) | AI Act Service Desk, quoted verbatim | 2026-08-03 |
| "an assessment of the technical measures needed to facilitate the interpretation of the outputs" | Annex IV 2(e) | AI Act Service Desk, verbatim | 2026-08-03 |
| "the technical measures put in place to facilitate the interpretation of the outputs" | Annex IV 3 and Article 13(3)(d) | AI Act Service Desk, verbatim, appears in both | 2026-08-03 |
| "A description of the appropriateness of the performance metrics for the specific AI system" | Annex IV 4 | AI Act Service Desk, verbatim | 2026-08-03 |
| "to correctly interpret the high-risk AI system's output, taking into account, for example, the interpretation tools and methods available" | Article 14(4)(c) | AI Act Service Desk, verbatim | 2026-08-03 |
| automation bias named as a thing oversight must guard against | Article 14(4)(b) | AI Act Service Desk, verbatim | 2026-08-03 |
| "clear and meaningful explanations of the role of the AI system in the decision-making procedure and the main elements of the decision taken", owed by the deployer | Article 86(1) | AI Act Service Desk, verbatim | 2026-08-03 |
| Article 86 is subsidiary: applies "only to the extent that the right ... is not otherwise provided for under Union law" | Article 86(3) | AI Act Service Desk, verbatim | 2026-08-03 |
| Creditworthiness evaluation is high-risk, fraud detection excluded | Annex III point 5(b) | AI Act Service Desk, verbatim | 2026-08-03 |
| Article 86's excluded point 2 is critical infrastructure, not credit | Annex III point 2 | AI Act Service Desk, verbatim | 2026-08-03 |

**Not yet located in source.** The interchange-intervention protocol, 2606.06267
section 5.3.2. The HTML fetch truncated before the body of section 5. Their
released code at `github.com/UKPLab/arxiv2026-phantom-specialization` is the
better source for reproducing it verbatim.

## Amending instrument, added 2026-08-08

**Regulation (EU) 2026/1744**, Digital Omnibus on AI, of 8 July 2026, amending
Regulation (EU) 2024/1689 and Regulations (EU) 2018/1139 and (EU) 2023/1230.
OJ L, 24 July 2026. In force 27 July 2026.

| item | state | note |
|---|---|---|
| Existence, ELI, OJ date, date of the act | **VERIFIED 2026-08-08** | EUR-Lex ELI record, `https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng` |
| Annex III deferral, 2 Aug 2026 to 2 Dec 2027 | **VERIFIED, secondary** | Convergent independent legal commentary. Not read in the OJ. |
| Annex I deferral to 2 Aug 2028 | **VERIFIED, secondary** | Same basis. |
| Operative text of the amendments | **UNREAD** | Two EUR-Lex fetches returned an empty body 2026-08-08. Needs a browser. |

**Consequence for every row in the table below.** The AI Act Service Desk states
it reproduces the official version of **13 June 2024**. All strings below were
read from it on 2026-08-03 and are therefore **pre-Omnibus**. Whether any of the
ten provisions P1 relies on were amended is **UNKNOWN**, not "unchanged". None of
them may enter the manuscript until checked against consolidated CELEX
`02024R1689-20260727`.

### Re-verified against the Official Journal consolidated text, 2026-08-11

**VERIFIED** against CELEX `02024R1689-20260727`, the AI Act consolidated as
amended by Regulation (EU) 2026/1744, read in a browser at
`https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02024R1689-20260727`.
Plain fetch returns an empty body; the document is 390,645 characters and
`get_page_text` truncates at 50 KB, so the check was made by querying the loaded
DOM directly.

**Method, so it can be repeated.** EUR-Lex marks consolidated text with `▼M1`
for passages introduced by the first amending act and `▼B` for surviving base
text. The document carries **70** such markers, so the Omnibus is not cosmetic.
For each quoted string the nearest preceding marker was located.

| provision | quoted string present | block |
|---|---|---|
| Annex IV 2(b) | yes | **▼B** |
| Annex IV 2(e) | yes | **▼B** |
| Annex IV 3 and Article 13(3)(d) | yes | **▼B** |
| Annex IV 4 | yes | **▼B** |
| Article 14(4)(b) | yes | **▼B** |
| Article 14(4)(c) | yes | **▼B** |
| Article 86(1) | yes | **▼B** |
| Article 86(3) | yes | **▼B** |
| Annex III 5(b) | yes | **▼B** |

**Every provision P1 depends on survives the Digital Omnibus verbatim.** None sits
inside an amended block. The concern raised on 2026-08-08, that the strings were
read from a Commission rendering of the 13 June 2024 text and might have been
superseded, is answered: they were not superseded.

`phi_overseer` is built on Annex IV 2(e) and 3 with Article 14(4)(c);
`phi_affected` on Article 86(1). **None of those moved, so no addressee constant
changes and no re-run of `phi` is needed.**

**One row not re-checked.** Annex III point 2, critical infrastructure, cited only
to establish that Article 86's excluded point is not the credit point. Nine of ten
verified; this is the tenth and it is outstanding.

**Provenance for the manuscript.** Cite the Official Journal consolidated text at
this CELEX identifier, not the AI Act Service Desk. The Service Desk states it
reproduces the version of 13 June 2024, which for these nine provisions turns out
to be the same text, but that is a fact established here rather than an
assumption a reader should be asked to share.

### 2606.06267 upgraded from RECALLED to VERIFIED, 2026-08-11

The ledger recorded this as "**The paper that most threatens P1.** Findings are
RECALLED from search summaries only." That state is now closed.

**VERIFIED 2026-08-11** from the authors' own replication repository,
`github.com/UKPLab/arxiv2026-phantom-specialization`, Apache-2.0, whose README
reproduces the abstract and whose structure matches what DESIGN-DELTAS D4
describes.

Confirmed as stated: authors Bayat Makou, Niu, Dutta and Gurevych, UKP Lab, TU
Darmstadt, 2026. Literal Sequence Copying across four token-frequency bands in
five Pythia models, 70M to 1.4B, **75 circuits**. Findings: band-specific edges
transfer across bands, a shared core recovers at least 99% of circuit
performance, and causal interchange interventions show internal representations
are interchangeable across bands.

**The sentence P1 must engage with, quoted from their abstract:** repeated
extractions within the same band "suggest that discovery algorithms sample from
an equivalence class of valid subgraphs rather than recovering a unique
mechanism".

**Citation state.** The README says a preprint "will be made available on arXiv;
please check back here for the final citation once it is posted", and their own
BibTeX carries `note = {arXiv preprint, link to be added}`. **So the arXiv
identifier 2606.06267 is not confirmed by the authors' own artifact.** The work,
authors, venue and findings are verified; the identifier is not. Cite the
repository and the author list, and resolve the arXiv ID before the bibliography
is final. Do not print 2606.06267 until it resolves.

**Their code is now read, not recalled.** `05_Phase_Targeted/per_example_agreement.py`
was fetched and `agreement_rate` and `cohens_kappa` are transcribed character for
character into `src/p1/agreement.py`, which closes the "Not yet located in source"
entry for the interchange protocol's cheap measures. The expensive
interchange-intervention protocol in their section 5.3.2 remains unread.

**What this does to P1's positioning, stated plainly.** They vary input
statistics with the analysis fixed and conclude structure does not imply
mechanism. P1 varies analytic specification with the input fixed and asks what
reaches a regulatory filing. Their result makes P1's premise more likely, not
less, and it also supplies the strongest objection to P1: if discovery samples
from an equivalence class, a flip rate over claims may be measuring which member
was sampled rather than any disagreement about the model. **P1 cannot answer that
without the functional-equivalence measurement**, which is exactly what the
repair run produces.

## Full verification pass, 2026-08-11

Every row below fetched from `arxiv.org/abs/<ID>` this session and compared field
by field. Discrepancies against the 3 August brief are recorded, not silently
corrected.

| ID | Exact title as fetched | Authors | Venue | Date | State |
|---|---|---|---|---|---|
| 2407.08734 | Transformer Circuit Faithfulness Metrics are not Robust | Joseph Miller, Bilal Chughtai, William Saunders | **CoLM 2024** (Comments) | v1, 11 Jul 2024 | **VERIFIED** |
| 2606.00033 | Make Mechanistic Interpretability Auditable: A Call to Develop Guidelines via Continuous Collaborative Reviewing | Michael Lan, Narmeen Fatimah Oozeer, Chaithanya Bandi, Philip Quirke, Austin Meek, Fazl Barez, Amirali Abdullah | **Accepted at ACL 2026 main conference** (Comments) | v1, 24 Apr 2026 | **VERIFIED** |
| 2501.16496 | Open Problems in Mechanistic Interpretability | Lee Sharkey, Bilal Chughtai, Joshua Batson, Jack Lindsey, Jeff Wu, Lucius Bushnaq, Nicholas Goldowsky-Dill, Stefan Heimersheim, Alejandro Ortega, Joseph Bloom, Stella Biderman, Adria Garriga-Alonso, Arthur Conmy, Neel Nanda, Jessica Rumbelow, Martin Wattenberg, Nandi Schoots, Joseph Miller, Eric J. Michaud, Stephen Casper, Max Tegmark, William Saunders, David Bau, Eric Todd, Atticus Geiger, Mor Geva, Jesse Hoogland, Daniel Murfet, Tom McGrath | none in Comments | v1, 27 Jan 2025 | **VERIFIED** |
| 2510.00845 | Mechanistic Interpretability as Statistical Estimation: A Variance Analysis | **not captured** | not captured | not captured | **PARTIAL** |

### Discrepancies against the brief

1. **2407.08734 title.** Brief: *"...Metrics Are Not Robust"*. Fetched:
   *"...Metrics are not Robust"*. Use the fetched form.
2. **2407.08734 venue.** Brief: "COLM 2024". Comments field: **"CoLM 2024
   Conference Paper"**. Use CoLM.
3. **2606.00033 venue.** Brief gave none. **Accepted at ACL 2026 main
   conference.** Cite the venue.
4. **2510.00845.** The abs URL served a PDF with no machine-readable text. The
   title is confirmed from page metadata; **authors, venue and date are not**.
   Remains PARTIAL and is not citable with an author list until refetched.

### What 2606.00033 does for this paper's framing

Its abstract states, verbatim, that "two papers found conflicting conclusions for
the same behavior, and a third study revealed that both were partially correct
but incomparable due to methodological inconsistencies", and calls for auditing
standards so MI findings can be certified in safety-critical settings.

**That is this paper's premise stated by a different group, and it is a call this
work answers with a measurement rather than a proposal.** The brief flagged it as
"you are answering this call, say so". Confirmed, and now with a venue.

### Overlap worth noting in related work

Joseph Miller, Bilal Chughtai and William Saunders are authors of 2407.08734, the
instrument's paper. Chughtai, Miller and Saunders also appear on 2501.16496, the
open-problems review, alongside Conmy and Nanda. **The people who built the tool
this paper stress-tests are also among those calling for the field to address its
methodological instability.** That is a supportive framing, not an adversarial
one, and the paper should say so.

| 2504.13151 | MIB: A Mechanistic Interpretability Benchmark | Aaron Mueller, Atticus Geiger, Sarah Wiegreffe, Dana Arad, Ivan Arcuschin, Adam Belfki, Yik Siu Chan, Jaden Fiotto-Kaufman, Tal Haklay, Michael Hanna, Jing Huang, Rohan Gupta, Yaniv Nikankin, Hadas Orgad, Nikhil Prakash, Anja Reusch, Aruna Sankaranarayanan, Shun Shao, Alessandro Stolfo, Martin Tutek, Amir Zur, David Bau, Yonatan Belinkov | **Accepted to ICML 2025** | v1 17 Apr 2025, **v2 9 Jun 2025** | **VERIFIED** |

### "Mueller et al. 2026, non-identifiability" is resolved and DISPUTED

The ledger carried this as ambiguous, possibly `2504.13151` misattributed.
**Confirmed misattributed.** Aaron Mueller is first author of `2504.13151`, which
is **MIB: A Mechanistic Interpretability Benchmark**, ICML **2025**, not a 2026
paper and not about non-identifiability. It is a benchmark for comparing
circuit-localisation and causal-variable-localisation methods.

**Action.** Delete "Mueller et al. 2026 on non-identifiability" from the
bibliography. If a non-identifiability claim is to be attributed, it must be
resolved to a real identifier and fetched. **Do not cite it.**

MIB remains worth citing on its own terms: it establishes that the field needed
standardised evaluation before methods could be compared, which is adjacent to
this paper's argument that they cannot yet be certified.

Note also that **Michael Hanna** appears on MIB and is the author associated with
the greater-than task, ledger entry `2305.00586`, still RECALLED.

### 2510.00845 refetch, 2026-08-11: v2 title confirmed unchanged, authors still not obtainable

Fetched `arxiv.org/abs/2510.00845` and `arxiv.org/abs/2510.00845v2`. **Both serve
`Content-Type: application/pdf` with no machine-readable text.** Page metadata
returns the same title for both:

> Mechanistic Interpretability as Statistical Estimation: A Variance Analysis

**This contradicts the earlier ledger note** that a v2 title "adds *of EAP-IG*".
That note came from a search snippet, not a fetch, and the fetch does not support
it. The note is superseded, not deleted, per the append-only rule.

**State: PARTIAL.** Title verified twice, from two URLs. **Author list, venue and
date remain unobtained**, and two fetch routes have now failed. Under the
project's rule this may not enter a bibliography with an author list.

**Do not route around this with a search snippet.** If the authors are needed,
open the abs page in a browser, which is the same remedy that worked for EUR-Lex.

### Remaining gaps as of 2026-08-11

| item | state | what is missing |
|---|---|---|
| 2510.00845 | PARTIAL | authors, venue, date |
| 2409.09951 | PARTIAL | authors, venue; abstract confirms the method |
| 2606.06267 | DISPUTED identifier | authors and findings verified from their repo; **the arXiv ID is contradicted by the authors' own BibTeX** |
| Mueller et al. 2026 | **DELETE** | misattribution of 2504.13151 |
| Wang et al., IOI | RECALLED | no identifier resolved |
| Conmy et al., ACDC | RECALLED | no identifier resolved |
| Nanda et al., attribution patching | RECALLED | no identifier resolved |
| Meloux et al. | RECALLED | no identifier resolved |
| Steegen, Simmons, Simonsohn | RECALLED-plus | DOIs agree across three sources each, none resolved directly |

**Verified and citable today:** 2407.08734, 2606.00033, 2501.16496, 2504.13151,
2308.14272, 2512.13907. **Six.**

**Not citable today: nine.** The bibliography is not closed and the manuscript's
related-work section cannot be written from it.

## Browser pass, 2026-08-11. Two PARTIALs closed, one RECALLED resolved to a peer-reviewed paper

The abs pages were read in a browser after two plain fetches served an unparseable
PDF. Fields taken from the page DOM, not from search snippets.

| ID | Exact title as fetched | Authors | Venue | Date | State |
|---|---|---|---|---|---|
| 2510.00845 | Mechanistic Interpretability as Statistical Estimation: A Variance Analysis | Maxime Meloux, Francois Portet, Maxime Peyrard | none stated | v1 1 Oct 2025, **last revised 28 May 2026, v4** | **VERIFIED** |
| 2502.20914 | Everything, Everywhere, All at Once: Is Mechanistic Interpretability Identifiable? | Maxime Meloux, Silviu Maniu, Francois Portet, Maxime Peyrard | **ICLR 2025**, journal-ref field | Submitted 28 Feb 2025 | **VERIFIED** |

### "Meloux et al. 2025 on non-identifiability" is resolved

The brief carried this in its "CHECK BEFORE CITING" list, seen only through
secondary citation. It is `2502.20914`, and the arXiv record carries a
**journal-ref naming ICLR 2025**, so it is peer reviewed, not a preprint.

Its abstract states the question directly: "for a given behavior, and under MI's
criteria, does a unique explanation exist?", drawing the analogy to identifiability
in statistics, and distinguishing "where-then-what" from "what-then-where"
strategies.

**This is the foundational citation for P1's premise and it is now verified at a
top venue.** The paper's opening sentence, that circuits are formally
non-identifiable, rests on this and may now be written.

### Correction to cite v4, not v1

`2510.00845` was last revised **28 May 2026** and is at **v4**. The earlier ledger
note guessing at a v2 title containing "of EAP-IG" is superseded: the fetched
title is unchanged across versions and no such suffix exists in the record. Cite
v4 and state the version, since a variance analysis may have changed between
revisions.

### Same group, three relevant papers

Meloux, Portet and Peyrard appear on `2502.20914` (identifiability, ICLR 2025),
`2510.00845` (variance, v4) and `2512.18792` (*The Dead Salmons of AI
Interpretability*, 21 Dec 2025, not yet fetched). **One group is building the
statistical critique of MI that this paper extends into the regulatory setting.**
Related work should treat them as a programme, not three unrelated citations.

### Running count

**Verified and citable: eight.** 2407.08734, 2606.00033, 2501.16496, 2504.13151,
2308.14272, 2512.13907, 2510.00845, 2502.20914.

**Still open: six.** 2409.09951 (authors, venue), 2606.06267 (identifier disputed
by its own authors), Wang et al. IOI, Conmy et al. ACDC, Nanda et al. attribution
patching, and the Steegen/Simmons/Simonsohn trio at RECALLED-plus.

**Deleted: one.** Mueller et al. 2026 on non-identifiability, a misattribution of
2504.13151.

## Foundational MI references resolved, 2026-08-11. One more misattribution found.

Read from the abs page DOM in a browser.

| ID | Exact title as fetched | Authors | Venue | Date | State |
|---|---|---|---|---|---|
| 2211.00593 | Interpretability in the Wild: a Circuit for Indirect Object Identification in GPT-2 small | Kevin Wang, Alexandre Variengien, Arthur Conmy, Buck Shlegeris, Jacob Steinhardt | **none on the arXiv record** | Submitted 1 Nov 2022, v1 | **VERIFIED** |
| 2304.14997 | Towards Automated Circuit Discovery for Mechanistic Interpretability | Arthur Conmy, Augustine N. Mavor-Parker, Aengus Lynch, Stefan Heimersheim, Adria Garriga-Alonso | **NeurIPS 2023 Spotlight** (Comments) | v1 28 Apr 2023, **v4 28 Oct 2023** | **VERIFIED** |
| 2310.10348 | Attribution Patching Outperforms Automated Circuit Discovery | **Aaquib Syed, Can Rager, Arthur Conmy** | **NeurIPS 2023 ATTRIB Workshop** (Comments) | v1 16 Oct 2023, **v2 20 Nov 2023** | **VERIFIED** |

### "Nanda et al., attribution patching" is a misattribution. Second of the session.

The brief lists attribution patching under **Nanda et al.** The paper is
**Syed, Rager and Conmy**, `2310.10348`. Neel Nanda is not an author.

**This one is load-bearing.** Edge attribution patching is the method behind six
of this paper's seven discovery objectives, so it is cited in the methods section,
not just in related work. Attributing the field's EAP paper to the wrong authors
in a paper that stress-tests EAP would be a bad look on top of being wrong.

Neel Nanda is associated with attribution patching through earlier informal
writing. If that lineage is worth stating, it needs its own verified source and
must not be folded into the citation for `2310.10348`.

### 2211.00593 carries no venue on the arXiv record

No Comments field and no journal-ref. It is widely cited as ICLR 2023, but **the
arXiv record does not say so and this ledger does not assert it.** If the venue
is wanted, verify it against OpenReview and add a dated row. Otherwise cite the
arXiv record alone.

This paper already carries weight in the project beyond related work: the four
corruption levels of the corruption axis were transcribed from its section 3 and
appendix A, so it is a methods citation.

### Running count

**Verified and citable: eleven.** 2407.08734, 2606.00033, 2501.16496, 2504.13151,
2308.14272, 2512.13907, 2510.00845, 2502.20914, 2211.00593, 2304.14997,
2310.10348.

**Still open: four.** 2409.09951 (authors, venue), 2606.06267 (identifier
disputed by its own authors), and the Steegen/Simmons/Simonsohn trio at
RECALLED-plus.

**Deleted: two.** "Mueller et al. 2026 on non-identifiability", a misattribution
of 2504.13151. "Nanda et al., attribution patching", a misattribution of
2310.10348.
