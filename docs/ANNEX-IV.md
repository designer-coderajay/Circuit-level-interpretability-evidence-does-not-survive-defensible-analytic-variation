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
