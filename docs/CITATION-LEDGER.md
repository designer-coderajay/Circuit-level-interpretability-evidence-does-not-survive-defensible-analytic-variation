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

Regulation (EU) 2024/1689, Article 11 and Annex IV. **Not yet read in this
project.** Read the regulation itself from EUR-Lex, not summaries and not
artificialintelligenceact.eu, before writing any sentence that characterises
what Annex IV requires. The entire regulatory premise of P1 rests on this.

## Claims table

Separate from records. A claim enters here only after being located in the
source PDF.

| Claim | Attributed to | Located in source | Verified on |
|---|---|---|---|
| _(empty)_ | | | |
