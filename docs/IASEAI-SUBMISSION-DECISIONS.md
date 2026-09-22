# IASEAI'27 submission decisions

Rules verified 2026-09-22 from the official
[2027 Paper Submission Guide](https://docs.google.com/document/d/e/2PACX-1vR_hLJSEv5WZF66P2HPg8zvezNttnaHvuekFJGdam3gYBMJu57ma2iKeXJKl_DHF4oCuJZ7CLc-IE3d/pub),
linked from <https://www.iaseai.org/our-programs/iaseai27>. Quotations below are
verbatim.

## Dates

- Submission portal **opens 18 September, closes 2 October**.
- Decisions communicated **20 November 2026**.
- Main conference **9-10 February 2027**, workshops 11-12 February.
- All authors were asked to hold an OpenReview account **prior to 18 September**.

## The decision that is not really open

**3.1** states: "Archival submissions must contain substantial, original, and
unpublished material. At least 50% of the technical content (methods, analyses,
findings) must be new compared to any prior publication by the authors."

Our own Statement of Contributions says: "All quantitative results presented
here appeared in it." What is new is interpretive: the Annex IV reading, the use
of point 4, and the implications for a conformity procedure.

If the arXiv preprint counts as a prior publication for 3.1, the paper does not
clear the 50% technical-content bar and **archival is not available to us**. The
honest route is then non-archival, which 3.1 permits: "Non-archival submissions
may be based on previously published work, but: Prior publication must be
disclosed to the Program Chairs at submission."

## The genuine ambiguity, which is what to ask

**3.5** states: "Online Preprints. Allowed before or during review (e.g., arXiv,
SSRN, institutional repositories). Must not be linked or mentioned in the
submission."

3.5 permits preprints and does not describe them as prior publication. 3.1 sets
the novelty bar against "any prior publication by the authors". Whether an arXiv
preprint is a prior publication for 3.1 purposes is not stated anywhere in the
guide, and the two rules point in opposite directions.

At most ML venues a preprint is not treated as prior publication. If that holds
here, archival is available and the 50% bar does not bite. We should not assume
it. Ask.

## Two further items that need a decision, not a question

**3.7** states: "Virtual presentation options will not be available. The author
submitting will be the author invited to attend and present if approved.
Archival: At least one author must register for, attend, and present the paper
at the IASEAI Conference for it to be included in its proceedings."

So the submitting author is committing to attend in person on 9-10 February
2027. Who submits is therefore a deliberate choice, not an administrative one.

**3.2** states: "Archival track: Not allowed to be under review at any other
archival venue (journal, conference) while in review for IASEAI. Non-archival
track: May be under review elsewhere if disclosed to the Program Chairs."

Relevant if a journal version of P1 is planned during November to February.

## Compliance status of the current draft

| Rule | Requirement | Status |
|---|---|---|
| 3.3 | Double-anonymous | No author name, affiliation, repo URL, preprint link or acknowledgments in the printed text. `\author{}` and `\affiliations{}` empty |
| 3.5 | Preprint not linked or mentioned | No occurrence of the arXiv id or URL in the printed text |
| 3.6 | Statement of Contributions | Present, situates the work against "earlier preliminary work" without naming venue or authors |
| Format | AAAI, 10 pages | 9 pages, 0 LaTeX errors, 0 overfull boxes, 0 undefined citations |
| Checklist | Reproducibility Checklist | 31 of 31 answered, compiles standalone at 2 pages |

Note that 3.6 requires the Statement of Contributions to situate the work
against earlier versions "without naming venues or authors". Ours does. But it
also says plainly that all quantitative results are prior, which is what makes
the 3.1 question live. That sentence is correct and should not be softened.
