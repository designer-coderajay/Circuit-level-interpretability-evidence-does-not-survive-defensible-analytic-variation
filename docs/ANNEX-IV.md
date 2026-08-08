# Annex IV: what the regulation actually requires

Source and epistemic status
---------------------------

Retrieved 2026-08-03 from the **AI Act Service Desk**,
`https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-4`, an official
European Commission site managed by Directorate-General for Communications
Networks, Content and Technology. The page states that its text is the
"Artificial Intelligence Act (Regulation (EU) 2024/1689), Official version of
13 June 2024".

**Epistemic state: VERIFIED from an official Commission source, but this is a
Commission rendering, not the Official Journal text itself.** EUR-Lex does not
serve the consolidated text to a plain HTTP fetch; three URL forms returned
empty or page chrome only. **Before any wording from this file is quoted in the
manuscript, cross-check the exact string against the OJ.**

**Article 11 has not been read.** A fetch timed out. Annex IV's chapeau
references Article 11(1), and Article 11 governs the obligation to draw up and
maintain the documentation. Read it before writing the regulatory section.

---

## The finding: P1 has been aiming at the wrong paragraph

The brief targets "a structured Annex IV section 2 / section 3 statement". That
is approximately right and precisely wrong, and the difference matters because a
reviewer with legal training will catch it.

### What section 2(b) actually says

> "the design specifications of the system, namely **the general logic of the AI
> system and of the algorithms**; the key design choices including the rationale
> and assumptions made, including with regard to persons or groups of persons in
> respect of who, the system is intended to be used; the main classification
> choices; what the system is designed to optimise for, and the relevance of the
> different parameters; the description of the expected output and output
> quality of the system; the decisions about any possible trade-off made
> regarding the technical solutions adopted to comply with the requirements set
> out in Chapter III, Section 2"

"The general logic of the AI system and of the algorithms" is there, and it is
the phrase P1's premise has been resting on. But read the frame: this is
**design specifications**. It asks the provider to describe what they
*designed*, their *rationale*, their *assumptions*, their *design choices*. It is
an account of ex ante intent.

**A discovered circuit is not a design specification.** It is a post-hoc
description of mechanism recovered by analysis. The objection writes itself:
Annex IV section 2(b) asks what you intended to build, and nothing in it
requires, contemplates, or would be satisfied by a mechanistic circuit.

If P1 rests on 2(b) alone, that objection is fatal and correct.

### Where interpretability evidence actually lands

Two paragraphs, and they are the real hooks.

**Section 2(e):**

> "assessment of the human oversight measures needed in accordance with Article
> 14, including **an assessment of the technical measures needed to facilitate
> the interpretation of the outputs of AI systems by the deployers**, in
> accordance with Article 13(3), point (d)"

**Section 3:**

> "Detailed information about the monitoring, functioning and control of the AI
> system, in particular with regard to: ... the human oversight measures needed
> in accordance with Article 14, including **the technical measures put in place
> to facilitate the interpretation of the outputs** of AI systems by the
> deployers; specifications on input data, as appropriate"

The same concept appears twice, in two tenses. Section 2(e) is an assessment of
the measures *needed*. Section 3 is the measures *put in place*. That pairing is
exactly where an interpretability artefact is filed, and it is about
interpreting outputs, which is what a circuit purports to do.

**This is a stronger hook than 2(b), and it is legally accurate.** Retarget the
claim map accordingly.

### The paragraph nobody noticed

**Section 4, in full:**

> "A description of the appropriateness of the performance metrics for the
> specific AI system"

Annex IV contains a standalone requirement to justify **metric
appropriateness**. P1's specification space includes a metric dimension. If the
filed claim changes when the metric changes, then section 4 is not a formality:
it is a load-bearing justification whose adequacy nobody has ever measured.

This was not in the brief and it should be in the paper.

### The framing gift in section 7

> "A list of the harmonised standards applied in full or in part ...; **where no
> such harmonised standards have been applied, a detailed description of the
> solutions adopted** to meet the requirements set out in Chapter III, Section 2"

There is no harmonised standard for mechanistic interpretability evidence. The
filability criterion, `pi_star >= 1 - alpha`, is precisely the kind of object a
harmonised standard would specify. Section 7 is the slot P1's deliverable fits
into. Say so.

---

## The chapeau, and the objection it creates

> "The technical documentation referred to in Article 11(1) shall contain **at
> least** the following information, **as applicable to the relevant AI system**"

Two qualifiers.

- **"at least"** helps P1. The list is a floor, not a ceiling, so filing
  interpretability evidence is permitted even where not compelled.
- **"as applicable to the relevant AI system"** hurts P1, and must be addressed
  head-on. A provider can argue circuit-level interpretability is simply not
  applicable to their system. P1's answer has to be that sections 2(e) and 3 are
  not optional for a high-risk system with a human-oversight requirement under
  Article 14, and that *something* must be filed to satisfy them. The paper is
  then about the evidential quality of whatever is filed, not about compelling a
  particular technique.

---

## Verdict on the premise

**The regulatory premise SURVIVES, with a correction that strengthens it.**

Annex IV does require a description of system logic, and separately requires
technical measures to facilitate interpretation of outputs, and separately
requires a justification of metric appropriateness. All three are places where
an unstable analytic result becomes an unstable regulatory filing.

**What must change:**

1. Retarget the claim map from section 2(b) to **sections 2(e) and 3**. State
   2(b) as context, not as the hook.
2. Add **section 4** on metric appropriateness. It is the cleanest possible
   justification for the metric dimension of the specification space and it was
   missed entirely.
3. Frame the filability criterion against **section 7**, the harmonised
   standards gap.
4. Answer **"as applicable"** explicitly. Do not let a reviewer raise it first.

## Outstanding

- Read Article 11 in full.
- Read Article 13(3)(d) and Article 14, both cross-referenced from 2(e) and 3.
  The phrase "facilitate the interpretation of the outputs" is defined by that
  cross-reference, and the claim map should use the regulation's own vocabulary.
- Cross-check every string quoted above against the Official Journal text before
  it enters the manuscript.

---

# The regulatory chain, completed 2026-08-03

Articles 13 and 14 retrieved in full from the AI Act Service Desk, same source
and same epistemic caveat as Annex IV above: official Commission rendering of
the 13 June 2024 version, **not the Official Journal text**. Cross-check before
quoting in the manuscript.

## The chain, all four links verified

**Article 13(1).** An outcome obligation on the system itself:

> "High-risk AI systems shall be designed and developed in such a way as to
> ensure that their operation is **sufficiently transparent to enable deployers
> to interpret a system's output and use it appropriately**."

**Article 13(3)(d).** What the instructions for use must contain:

> "the human oversight measures referred to in Article 14, **including the
> technical measures put in place to facilitate the interpretation of the
> outputs** of the high-risk AI systems by the deployers"

**Article 14(4)(c).** The operative standard, and the sentence `phi` should be
built on:

> "to **correctly interpret** the high-risk AI system's output, **taking into
> account, for example, the interpretation tools and methods available**"

**Annex IV 2(e) and 3.** The same object entering the technical documentation,
in two tenses: the measures *needed*, and the measures *put in place*.

The identical phrase therefore appears in **three** operative places: Article
13(3)(d), Annex IV 2(e), and Annex IV 3. It is not an incidental mention.

## Why 14(4)(c) is the right target for phi

Three things in that one sentence.

1. **"correctly interpret."** The standard is *correctness*, not availability.
   Supplying an explanation is not the requirement; supplying one that supports
   correct interpretation is. An explanation that is one arbitrary member of an
   equivalence class of functionally equivalent subgraphs does not obviously
   meet a correctness standard, and that is exactly what P1 measures.

2. **"the interpretation tools and methods available."** The regulation
   explicitly contemplates interpretation *tools and methods*. Circuit discovery
   is such a method. This is a more direct hook than Annex IV 2(b)'s "general
   logic", and unlike 2(b) it is not framed as a design specification.

3. **The beneficiary is a natural person under Article 14(4)**, "natural persons
   to whom human oversight is assigned". Not an auditor, not a researcher. The
   standard is whether a human overseer can correctly interpret an output given
   the available tools.

**The filability criterion should be restated in this vocabulary.**
`pi_star >= 1 - alpha` is a criterion for when an interpretation method supports
*correct* interpretation rather than merely *available* interpretation. That is
the regulation's own distinction, and stating it that way is far stronger than
inventing a new one.

## The automation-bias argument, which is new

**Article 14(4)(b):**

> "to remain aware of the possible tendency of automatically relying or
> over-relying on the output produced by a high-risk AI system (**automation
> bias**), in particular for high-risk AI systems used to provide information or
> recommendations for decisions to be taken by natural persons"

This is a fundamental-rights argument, not an evidential one, and it was not in
the brief. An explanation that is unstable across analytic choices but presented
with the authority of a mechanistic circuit could **increase** over-reliance
rather than reduce it. The regulation names automation bias as a thing oversight
must guard against. P1's programme thesis, that confidence does not track
faithfulness, lands directly here.

Worth a paragraph in the discussion. Do not overclaim it: P1 measures claim
instability, it does not measure deployer behaviour.

## Article 14(3): when the measures must exist

> "The oversight measures ... shall be ensured through either one or both of the
> following types of measures: (a) measures identified and built, when
> technically feasible, into the high-risk AI system by the provider **before it
> is placed on the market** ...; (b) measures identified by the provider
> **before placing the high-risk AI system on the market** ... and that are
> appropriate to be implemented by the deployer."

The technical measures must be fixed *before* market placement. A provider
cannot defer the choice of interpretation method, which means the analytic
choices P1 varies are made once, in advance, by one analyst, and then filed.
That is precisely the situation in which specification instability matters and
is not detectable from the filing.

## Newly surfaced, unread

**Article 86, "Right to explanation of individual decision-making."** Seen in
the table of contents, not read. If it creates an individual right to an
explanation of a specific decision, it is a fourth and possibly stronger hook,
and it changes who the explanation is for. **Read before drafting.**

**Article 11** remains unread. Two fetch attempts, one timeout.

**Article 13(3)(b)(ii)** ties to the metric thread: "the level of accuracy,
**including its metrics**, robustness and cybersecurity referred to in Article
15 against which the high-risk AI system has been tested and validated". Pairs
with Annex IV 4 on metric appropriateness.

**Article 13(3)(b)(iv)**: "the technical capabilities and characteristics of the
high-risk AI system **to provide information that is relevant to explain its
output**".

## Consequence for phi, to be settled in the pre-registration

`phi` maps a circuit to a statement of the form the regulation asks for: a
technical measure available to a human overseer for correctly interpreting an
output. The three granularities (coarse, medium, fine) should be granularities
of *that* statement, not of an arbitrary structural tuple. Drafting the actual
sentence templates is the next design task and it is now unblocked.

---

# Article 86 and the closed loop, 2026-08-03

**Article 86(1), verbatim:**

> "Any affected person subject to a decision which is taken by **the deployer**
> on the basis of the output from a high-risk AI system listed in Annex III,
> with the exception of systems listed under point 2 thereof, and which produces
> legal effects or similarly significantly affects that person in a way that they
> consider to have an adverse impact on their health, safety or fundamental
> rights **shall have the right to obtain from the deployer clear and meaningful
> explanations of the role of the AI system in the decision-making procedure and
> the main elements of the decision taken**."

## Why this is the strongest hook, and why it changes the paper

**The duty falls on the deployer. The deployer only has what the provider gave
them.** Article 13 requires the provider to supply instructions for use, and
13(3)(d) requires those to include "the technical measures put in place to
facilitate the interpretation of the outputs". The deployer cannot manufacture
an explanation the provider did not enable.

The loop is therefore closed, and every link is verified:

1. The **provider** picks one interpretation method, that is, one specification
   `s` from `S`, at some point before market placement (Article 14(3)).
2. The provider files the resulting claim in the technical documentation
   (Annex IV 2(e) and 3) and supplies it to the deployer (Article 13(3)(d)).
3. The **deployer** must enable overseers to "correctly interpret" the output
   (Article 14(4)(c)) using what they were given.
4. An **affected person** has a right to "clear and meaningful explanations"
   from that deployer (Article 86(1)).

**So an arbitrary analytic choice, made once by one analyst inside the provider,
propagates to an individual's right to an explanation of a decision about them.**
If `phi(C(s))` moves across `S`, the explanation an affected person receives
depends on a researcher degree of freedom they will never see, were never told
about, and cannot contest.

That is a far stronger claim than "the evidence is unstable", it is squarely a
FAccT argument, and it is available only to someone who has connected the
interpretability literature to the regulatory text.

**Two qualitative standards, not availability standards.** Article 14(4)(c) says
"correctly interpret". Article 86(1) says "clear and meaningful". Neither is
satisfied by merely producing an artefact. The filability criterion speaks to
exactly this gap.

## Scope limits, which must be stated honestly in the paper

Do not overclaim Article 86. Four limits, all in the text:

1. **Annex III systems only**, and expressly "with the exception of systems
   listed under point 2 thereof". What Annex III point 2 covers is **not yet
   verified** and must be checked.
2. Only decisions producing **legal effects or similarly significantly
   affecting** the person, and only where they consider there to be an adverse
   impact on health, safety, or fundamental rights.
3. **86(2):** disapplied where Union or national law provides exceptions or
   restrictions.
4. **86(3):** applies "only to the extent that the right referred to in
   paragraph 1 is **not otherwise provided for under Union law**." Article 86 is
   subsidiary. A reviewer with legal training will immediately think of GDPR
   Article 22 and the automated-decision-making provisions. **Address this
   explicitly**; do not let it be raised first.

## Why the applied arm now matters more

The brief's applied arm is a BFSI credit underwriting prototype. Creditworthiness
assessment is **believed** to fall under Annex III, which would place it squarely
inside Article 86, and a credit decision plainly produces legal effects.

**RECALLED, not verified:** the specific Annex III point covering creditworthiness
assessment. Verify the point number against Annex III before the applied arm is
described in the paper, and verify simultaneously that it is not the excluded
point 2.

If it holds, the applied arm stops being an illustration and becomes the case
where all four links bind at once.

## Consequence for phi

`phi` now has two candidate addressees, and they are different documents with
different standards:

- **Annex IV 2(e) and 3, read with Article 14(4)(c).** Addressee is a human
  overseer at the deployer. Standard: "correctly interpret ... taking into
  account the interpretation tools and methods available".
- **Article 86(1).** Addressee is the affected person. Standard: "clear and
  meaningful explanations of the role of the AI system in the decision-making
  procedure and the main elements of the decision taken".

These are not the same sentence and they will not have the same flip rate.
Whether `phi` targets one, or both as separate claim maps, is the next design
decision.

# The Digital Omnibus, and what it does to this chain, 2026-08-08

## The instrument

Regulation (EU) 2026/1744 of 8 July 2026, the **Digital Omnibus on AI**, amends
Regulation (EU) 2024/1689. Published in OJ L on 24 July 2026, in force
27 July 2026. **VERIFIED 2026-08-08** from the EUR-Lex ELI record.

- Primary text: `https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng`
- AI Act consolidated as amended: CELEX `02024R1689-20260727`

## The dates

**VERIFIED 2026-08-08 from convergent independent legal commentary, NOT from the
operative text.** Two fetches of the EUR-Lex HTML returned an empty body; the
site renders client-side and the document is large. Reading it needs a browser.

| provision | was | now |
|---|---|---|
| Annex III standalone high-risk obligations | 2 August 2026 | **2 December 2027** |
| Annex I high-risk embedded in regulated products | 2 August 2027 | 2 August 2028 |
| Article 50 transparency | unchanged | unchanged |
| Article 50(2) watermarking, systems on market at 2 Aug 2026 | 2 August 2026 | 2 December 2026 |
| Article 4 AI literacy | unchanged | unchanged |

Several independent law firm commentaries agree on the first two rows.
Convergence across independent secondary sources is weaker evidence than the
Official Journal and is recorded here as such, not laundered into a fact.

## What this does to P1's motivation: changes the tense, not the force

Under the original calendar the Annex IV conformity regime for Annex III 5(b)
credit systems applied from **2 August 2026**, six days before this was written.
A paper arguing the evidence base is unstable would have been arguing about a
filing obligation already live.

Under the Omnibus it applies from **2 December 2027**, sixteen months out. The
standards, guidance and notified-body practice that will decide what counts as
adequate interpretability evidence are being drafted **now**. A result showing
that circuit evidence does not survive defensible analytic variation is more
useful before that practice hardens than after.

Write this as timing, not urgency. Reviewers punish manufactured urgency, and
the honest version is the stronger one.

## The problem this uncovered, which is not about dates

The AI Act Service Desk states that it reproduces **the official version of
13 June 2024**. Every verbatim string in `docs/CITATION-LEDGER.md` was read from
it on 2026-08-03. **That is the pre-Omnibus text.**

The ten provisions P1's claim map depends on, Annex IV 2(b), 2(e), 3 and 4,
Article 13(3)(d), 14(4)(b), 14(4)(c), 86(1) and 86(3), and Annex III 5(b), have
therefore **not** been checked against the consolidated text as amended. Whether
the Omnibus touched any of them is **UNKNOWN**. It is not "unchanged". The
instrument is titled a simplification measure, which is precisely the sort that
trims documentation requirements.

`phi_overseer` is defined against Annex IV 2(e) and 3 together with Article
14(4)(c). `phi_affected` is defined against Article 86(1). If any of those moved,
the addressees move with them.

**This does not touch the sweep.** The sweep measures circuits, not law. `phi` is
deterministic code applied to circuits after the fact, so a change in the mapping
is a re-run of `phi` over banked results, not a re-run of 1,540 discovery cells.
The exposure is confined to the mapping and to every sentence in the manuscript
that characterises the regulation.

## Action, before any manuscript sentence characterises the regulation

1. Read CELEX `02024R1689-20260727` from EUR-Lex, the consolidated version dated
   27 July 2026, in a browser.
2. Re-verify all ten strings against it.
3. Record any that moved, and re-derive `phi`'s addressee constants if so.
4. Cite the Official Journal, never the Service Desk.
