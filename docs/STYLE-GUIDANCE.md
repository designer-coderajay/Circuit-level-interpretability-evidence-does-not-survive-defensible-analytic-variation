# Drafting standards for the IASEAI'27 paper

Two links from the call with Lukas Galke, both fetched and read on 2026-09-24:

- <https://cs.stanford.edu/people/widom/paper-writing.html>
- <https://www.asd-ste100.org/>

Recorded here because the guidance existed only in the call. Guidance nobody can
check later is the same class of problem as an unverified citation.

An earlier version of this file checked the paper against a **recollection** of
these standards. The findings below are checked against the sources themselves,
which changed two conclusions.

---

## 1. Widom, "Tips for Writing Technical Papers"

### The five-paragraph Introduction: exact conformance

Widom, verbatim: "the Introduction should consist of five paragraphs answering
the following five questions", then "a final paragraph or subsection: 'Summary
of Contributions'... in bullet form, mentioning in which sections they can be
found."

Our Introduction is **five paragraphs plus a Contributions list**, and the list
does cite sections.

| Widom's question | Our paragraph |
|---|---|
| 1. What is the problem? | P1 "An audit means two auditors reach the same conclusion." |
| 2. Why is it interesting and important? | P2 The documentation duty and the Article 86 right |
| 3. Why is it hard? | P3 "choices that the literature does not settle... Each choice has published defenders." |
| 4. Why hasn't it been solved before? | P4 "The pieces of this argument exist separately... What has not been done is to connect those results to the filing." |
| 5. Key components, results, and specific limitations | P5 "We do that... flips across 73.2%... The study covers one model and one task." |
| Summary of Contributions, with sections | P6, bullets citing Interpreting Annex IV, The Filability Protocol, Results, Limitations |

Widom asks for limitations inside question 5. Ours are there, and in the
Abstract, rather than held back to a Limitations section.

### One clear violation

Widom on the Abstract: "The material in the abstract should not be repeated
later word for word in the paper."

The Abstract's opening sentence and the Introduction's second paragraph share
about eighteen near-identical words:

> **Abstract:** The EU AI Act requires providers of high-risk systems to file
> technical documentation describing how the system reaches its decisions.

> **Introduction P2:** The EU AI Act \citep{aiact2024} requires providers of
> high-risk AI systems to file technical documentation describing how their
> systems reach decisions, and it gives a person subject to certain automated
> decisions a right to an explanation...

A fix that keeps the Abstract untouched and varies the Introduction:

> Two duties in the Act bear on this. A provider of a high-risk system must file
> technical documentation of how the system reaches decisions, and a person
> subject to certain automated decisions has a right to an explanation of the
> main elements of that decision.

Not applied. It is a wording change in the paper's most important paragraph and
belongs to the lead author.

### Not a violation, though it looked like one

The 73.2% result appears in the Abstract, the Introduction and the Conclusions.
That reads like repetition, but Widom explicitly permits it: "In some cases it's
possible to now make the original claims more concrete, e.g., by referring to
quantitative performance results." His prohibition is on a Conclusions paragraph
that *simply* repeats. Ours adds new framing ("The finding is not that
discovered circuits are meaningless"). This is fine as it stands.

### Widom's pet peeves

| Rule | Status |
|---|---|
| No "etc." unless remaining items are obvious | 0 occurrences |
| Never "for various reasons" | 0 occurrences |
| Avoid nonreferential "this", "that", "these" | 5 instances of "This is/matters/shows" opening a sentence. Each has the previous sentence as its antecedent, so each is readable. Judgement call, not clearly wrong |
| Citations complete and consistent, not copied BibTeX | All 18 entries verified to Crossref, arXiv or publisher record. See `CITATION-LEDGER.md` |
| Tables at top of page or column | All seven use `[t]` |
| Acknowledgements: do not forget them | **Deliberately absent.** IASEAI rule 3.3 requires their removal for double-anonymous review. The venue rule wins; restore on acceptance |

---

## 2. ASD-STE100

**What could not be verified.** The site describes the standard but does not
publish it. The Writing Rules (Part 1) and the Dictionary of controlled
vocabulary (Part 2) are only in the specification itself, currently Issue 8,
April 2021. So conformance to the literal rule set is **unverified**, and any
claim that the paper "follows ASD-STE100" would overstate what was checked.

What the site does state, and what follows from it:

- STE was built for **aircraft maintenance documentation**, to be read by people
  whose first language is not English. It is not a standard for research papers.
  Applied literally its Dictionary would reject much of our necessary
  vocabulary, so the sensible reading of the advice is the principle behind it:
  short sentences, one idea each, one word for one meaning.
- STE specifies **American spelling**. Our paper is consistently British
  (behaviour, analyse, optimise, characterises, standardising), with no mixed
  usage. "rigorous" is identical in both varieties. This is a deliberate
  divergence from the literal spec and not an inconsistency; neither AAAI nor
  IASEAI requires American spelling.

Measured against the principles, over 355 narrative sentences excluding tables,
figures and preamble:

| Measure | Value |
|---|---|
| Mean sentence length | 16.0 words |
| Median | 14 words |
| Over 25 words | 51 of 355, 14% |
| Over 35 words | 19 of 355, several of which are list items flattened by the measuring script rather than real sentences |

The Abstract is the clearest example of the principle: 247 words in 15
sentences, including "Annex~IV names no method." at five words, "We give a
criterion." at four, and "We then measure it." at four.

**One sentence does not conform.** The Abstract's results sentence is 52 words
and carries five ideas: grid size, model, task, provenance of the axis levels,
flip rate with interval, and modal share.

Current:

> Across 15,840 pre-registered specifications on GPT-2 small and the indirect
> object identification task, with every axis level drawn from a published
> implementation, the derived Annex IV statement flips across 73.2% of
> specification pairs (95% CI 0.725 to 0.738) and the modal claim commands 41.1%
> of the space.

A conforming split, 28 / 9 / 9 words:

> Across 15,840 pre-registered specifications on GPT-2 small and the indirect
> object identification task, the derived Annex IV statement flips across 73.2%
> of specification pairs (95% CI 0.725 to 0.738). Every axis level is drawn from
> a published implementation. The modal claim commands 41.1% of the space.

Not applied, for the same reason as above.

---

## 3. House rules

| Rule | Status |
|---|---|
| No em-dashes | 0 unicode em-dashes, 0 LaTeX `---` |
| No tildes in prose | 29 tildes, every one a LaTeX non-breaking space (`Annex~IV`, `Table~\ref{}`) |
| Lead on the criterion, not the negative result | The title does this |

The single `--` outside a numeric range is `Gini--Simpson`, correct LaTeX for a
compound proper name.

---

## Summary

Widom is followed closely, including the five-paragraph structure most papers
ignore. One clear violation, the Abstract-to-Introduction overlap, with a fix
above. ASD-STE100 is followed in principle and cannot be checked against the
literal specification, which is not public; the paper diverges from it knowingly
on spelling.

Two proposed edits are left unapplied because both are wording changes in the
Abstract and Introduction. Raise them with Lukas.
