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
