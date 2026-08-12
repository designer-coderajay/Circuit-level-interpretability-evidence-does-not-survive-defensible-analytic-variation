# Explanation Multiplicity: Circuit-Level Interpretability Evidence Does Not Survive Defensible Analytic Variation

Ajay Pravin Mahale

Draft, 2026-08-12. Every number traces to `results/analysis/*.json` and is
independently recomputed by `analysis/verify_all_claims.py`, 36 checks, 0
failures. Citations marked with a dagger are not yet verified and must not
survive to submission.

---

## Abstract

The EU AI Act requires providers of high-risk systems to file technical
documentation describing how the system reaches its decisions. Mechanistic
interpretability is the obvious source of such evidence, and circuit discovery is
its most developed instrument. We ask whether that evidence survives the
condition under which it would be relied upon: two competent analysts, the same
system, the same tool, different defensible settings.

We pre-registered a crossed grid of seven analytic axes, all levels taken from
published implementations, and mapped each discovered circuit through a
deterministic claim map to a structured Annex IV statement. Across 15,840
pre-registered specifications on GPT-2 small and the indirect object
identification task, of which 7,561 produced a claim, the derived statement flips
across 73.2% of specification pairs (95% CI 0.725 to 0.738) and the modal claim
commands 41.1% of the space. The evidence fails a filability criterion
at every tolerance a conformity assessment body would plausibly accept.

Standardising the single most influential choice, the evaluation metric, leaves
the flip rate at 59.4%. Removing circuit size from the claim entirely and holding
it fixed leaves 27.1% (95% CI 0.255 to 0.286), still above the pre-registered
threshold. The circuits underlying these claims are structurally near-disjoint,
median pairwise Jaccard overlap 4%, and functionally uncorrelated at Cohen's
kappa 0.015, so the instability is not one mechanism described in different words.

We report a filability criterion as a standalone protocol, and we report that one
of the seven documented discovery objectives does not execute at all on the
library's own canonical task. The study covers one model and one task, and whether
the conclusion holds at scale is untested.

---

## 1. Introduction

An audit means two auditors reach the same conclusion. That is not a definition
borrowed from machine learning; it is what makes an audit worth commissioning.

Regulation (EU) 2024/1689 requires providers of high-risk AI systems to file
technical documentation. Annex IV point 2(b) asks for "the general logic of the
AI system and of the algorithms". Point 2(e) asks for "an assessment of the
technical measures needed to facilitate the interpretation of the outputs".
Article 86(1) gives a person subject to certain automated decisions the right to
"clear and meaningful explanations of the role of the AI system in the
decision-making procedure and the main elements of the decision taken". These
are quoted from the consolidated text as amended by Regulation (EU) 2026/1744,
read 2026-08-11.

Mechanistic interpretability offers to supply the technical content. Circuit
discovery, in particular, produces a subgraph said to explain a behaviour, and it
is the part of the field with mature tooling. If a provider files a circuit-level
account of why its system behaved as it did, the filing is only worth anything if
a second analyst, given the same system and the same tool, would file something
compatible.

Two results make that doubtful before any experiment. Méloux et al. show that
mechanistic explanations are not identifiable: for a given behaviour, under the
field's own criteria, a unique explanation need not exist [ICLR 2025]. Miller,
Chughtai and Saunders show that circuit faithfulness scores are highly sensitive
to seemingly insignificant changes in ablation methodology, and conclude that
faithfulness scores reflect the researcher's methodological choices as well as the
circuit [CoLM 2024]. Lan et al. observe that two papers have reached conflicting
conclusions about the same behaviour, with a third finding both partly correct and
incomparable, and call for auditing standards so that findings can be certified in
safety-critical settings [ACL 2026].

What nobody has done is connect them to the filing.

We measure how far a regulatory claim moves across the space of defensible
analytic specifications, and attach a decision rule a standards body could use. We do not propose a better circuit discovery
method, and we do not argue that interpretability is worthless. We argue that the
evidence, as currently produced, does not meet the standard that filing it
presumes.

---

## 2. What this paper is not claiming

Stated early because each of these is a reading the results do not support, and
two of them are readings we held ourselves before the decompositions were run.

We are not claiming that discovered circuits are no better than random. At fixed
circuit size they are more stable than a size-matched random null, 0.275 against
0.423. They carry information.

Nor that filings differ where mechanisms do not. Mechanisms differ a great deal:
functional instability is 0.397 pooled and 0.478 at the smallest circuits.

Nor that discovery samples one mechanism and dresses it differently. Cohen's
kappa of 0.015 says the circuits are functionally uncorrelated.

Nor that random seeds are the problem. The seed here selects which prompts are
sampled, so it is evaluation-set variability rather than nondeterminism.

And nothing at all about scale. One model, one task.

---

## 3. Formalism

A *specification* is a tuple of analytic choices,

    s = (o, a, d, m, tau, P, r, g)

with `o` the discovery objective, `a` the ablation operator, `d` the corruption
distribution, `m` the evaluation metric, `tau` the size threshold, `P` the prompt
variant, `r` the seed, and `g` the granularity. Every level of every axis is taken
from a published implementation; none was invented for this study.

Circuit discovery returns `C(s)`, a subset of the model's edge set `E`. For GPT-2
small under the factorised graph with separate query, key and value inputs,
`|E| = 32,491`, which we confirm both from the instrument and from a closed-form
count over the computation order. The circuit touches a set of components drawn
from 144 attention heads and 12 MLPs, so 156 in total.

*Circuit instability.* For two specifications,

    D(s_i, s_j) = 1 - |C_i ∩ C_j| / |C_i ∪ C_j|

and `J_bar` is the mean Jaccard similarity over unordered pairs.

*Claim instability.* Let `phi` map a circuit to a structured Annex IV statement.
The flip rate is the probability that two distinct specifications yield different
statements,

    F = 1 - [ sum_c n_c (n_c - 1) ] / [ N (N - 1) ]

where `n_c` counts specifications yielding claim class `c`. This is the unbiased
Gini-Simpson form; it is the probability that two draws without replacement
differ, and it is unit-tested against the brute-force pairwise definition.

The modal share is `pi* = max_c n_c / N`.

*Filability.* Evidence is *filable at tolerance alpha* if and only if
`pi* >= 1 - alpha`. This is the deliverable: a criterion a standards body can
write into a procedure, with a number attached.

Note the ceiling. `F <= 1 - 1/k` for `k` claim classes, so a reported flip rate
must be read against the number of classes the map can produce.

---

## 4. The claim map

`phi` is the most attackable choice in the paper, so it is fixed in the
pre-registration, implemented as deterministic code, and published.

It is not generated by a language model. Doing so would measure model variance
on top of circuit variance with no way to separate them.

Two addressees, following the regulation rather than convenience.
`phi_overseer` is built on Annex IV 2(e) and 3 with Article 14(4)(c), and keyed on
the dominant layer band, then the size class, then the ranked input segment.
`phi_affected` is built on Article 86(1) and leads with the input segment, because the
right is owed to the person the decision is about. Three granularities are nested
by construction, so a claim at a finer granularity refines rather than contradicts
the coarser one.

A reviewer will say the size
bins were chosen to produce the reported flip rate. They were returned by a
committed calibration rule from a measured curve, not chosen. Varying every
threshold by a factor of four in either direction moves `F` between 0.70 and 0.77,
and the committed bins are not a maximum: halving every threshold gives 0.745
against the committed 0.732. Removing the size term from the claim entirely still
gives 0.573.

---

## 5. Method

*Model and task.* GPT-2 small on indirect object identification. The choice is
not an apology. The non-identifiability and faithfulness literature this paper
extends works at this scale, comparability is the point, and the edge count is
what makes a size-matched random baseline meaningful.

*Grid.* Seven objectives, seven ablation operators, four corruption
distributions nested within the five operators that read them, four metrics, three
thresholds, two prompt variants, five seeds. 1,540 discovery cells and 18,480
specifications as pre-registered.

*Pre-registration.* The analysis plan was committed and tagged before the
confirmatory sweep began, with both abstracts drafted in advance so that neither
direction could be written up as a surprise.

*Statistics.* No p-value is computed across specifications anywhere;
specifications are a designed grid, not an independent sample. Uncertainty comes
from a nonparametric bootstrap that resamples specifications, never pairs, at
B = 10,000, because `F` and `J_bar` are U-statistics over pairs and pairs sharing
a specification are dependent. Intervals quantify uncertainty given the grid and
license nothing beyond it.

Two exclusions, both with criteria fixed before any circuit was seen.

One discovery objective, `LOGIT_MSE_GRAD_PRUNE_ALGO`, does not execute. All 220 of
its cells raise `RuntimeError: Found dtype Long but expected Float` from a mean
squared error computed against an integral target, inside the library's own code.
We verified by digest that the failure set is exactly that arm. We did not repair
it: the library is the instrument under test and is reproduced verbatim. The
realised grid is therefore six objectives, 1,320 cells, 15,840 specifications.

The metric-relative threshold rule admits no circuit for 8,279 of 15,840 specifications, a
discard rate of 52.3%, distributed unevenly across metrics:
comprehensiveness 0.3%, kl_div 63.0%, logit_diff 67.9%, sufficiency 77.9%. This
was disclosed before the lock. The consequence is that the surviving pool is 52%
comprehensiveness against 25% by design, and we report the composition rather than
smoothing it.

---

## 6. Results

### 6.1 Circuits are almost disjoint

`J_bar = 0.1396` (95% CI 0.1377 to 0.1418), computed exactly over all 28,580,580
specification pairs rather than sampled.

The distribution says more than the mean. The median pair of circuits shares 4% of its edges. Only 1% of pairs exceed a Jaccard of 0.8. At the median circuit
size of 200 edges the analytic random line gives 0.0031, so observed overlap is
about 45 times chance, consistent with the range prior work reports. Beating
chance at this scale is not evidence of much: a 500-edge circuit has an expected
random overlap of 0.008.

### 6.2 The claim flips on three quarters of pairs

`F = 0.7316` (95% CI 0.7247 to 0.7380) against a pre-registered threshold of
0.20 with the interval lower bound required to clear it. It clears by more than
three times.

`pi* = 0.4109`. Not filable at any pre-registered tolerance: 0.411 against requirements of 0.95,
0.90 and 0.80.

The two most common claims, at 41.1% and 28.5% of the space, attribute the same
model's behaviour on the same task to early layers and to late layers.
They are not different emphases. They contradict.

All six addressee-granularity combinations reject filability. The coarsest
statement available to an affected person is a two-class claim and it still flips
on 39.5% of pairs.

Figure 1 shows the specification curve. The width of the modal step is `pi*`.

### 6.3 No analytic axis rescues the filing

| axis standardised | residual `F` | 95% CI | removes |
|---|---|---|---|
| **evaluation metric** | 0.5939 | 0.5803 to 0.6063 | 0.1377 |
| ablation operator | 0.7014 | 0.6939 to 0.7075 | 0.0302 |
| discovery objective | 0.7018 | 0.6938 to 0.7084 | 0.0298 |
| threshold `tau` | 0.7070 | 0.6981 to 0.7149 | 0.0246 |
| corruption | 0.7092 | 0.7008 to 0.7166 | 0.0224 |
| prompt variant | 0.7232 | 0.7157 to 0.7300 | 0.0084 |
| seed | 0.7307 | 0.7234 to 0.7368 | 0.0009 |

The metric is the largest single lever and it is not enough. Standardising it
completely, which is more than a conformity procedure could demand, leaves
`F = 0.594`.

**Structure and claim are governed by different axes.** A variance decomposition
on the log selected circuit size attributes 78.8% to the ablation-corruption
interaction and 0.7% to the metric, which is the largest driver of claim
variance. A standards body reading the structural decomposition would standardise
the ablation operator and fix almost none of the filing instability.

### 6.4 The result under maximum pressure

Strip every trace of circuit size from the claim, so the statement is the dominant
layer band alone, and hold circuit size fixed:

**`F = 0.2706` (95% CI 0.2550 to 0.2859).**

The interval lower bound is above the pre-registered threshold. Where in the model
the behaviour is attributed still flips on 27% of pairs when nothing about size
can contribute.

### 6.5 The random baseline, and why its pooled direction misleads

Pooled, the discovered multiverse is *less* stable than a size-matched random null
drawn from the full 32,491-edge population: 0.7316 against 0.6774, intervals
disjoint.

We do not report that as a finding. It is an artefact of the size distribution. The null is degenerate above 1,000 edges, where a uniform draw
touches all 156 components and can produce only one claim. With size held fixed
the ordering reverses: discovered 0.2746 against null 0.4230.

Discovered circuits are more stable than random ones once the comparison is fair.
They are still not stable enough to file.

### 6.6 Filings differ more than mechanisms, over part of the range

Per-example functional agreement between circuits is 0.6028, so functional
instability is 0.3972, and the gap to the claim flip rate is 0.3344 (95% CI
0.3297 to 0.3394) against a pre-registered threshold of 0.10.

Cohen's kappa is 0.0146. The 60% raw agreement is almost entirely explained by
both circuits being right about the same fraction of examples, not the same
examples. Kappa stays between 0.016 and 0.047 at every circuit size while raw
agreement climbs from 0.52 to 0.92, tracking accuracy from 0.51 to 0.95.

The gap does not survive holding size fixed. It fails the 0.10 threshold at 6
of 10 sizes and is negative at 5. At both ends of the range the mechanisms differ
more than the filings do. The pooled figure is carried by the 500 to 2,000 edge
band alone. We report the pooled result because it was pre-registered, and the
decomposition beside it because the pooled result alone would mislead.

---

## 7. Limitations

*One model, one task.* Larger models have more components, so both the layer
band and the size class have more room, and the direction of the effect on `F` is
not obvious. A multi-model replication and a second task were designed and not
run.

*Circuit size is an outcome, not an axis.* It is chosen by the threshold rule,
and it has distorted three separate pooled quantities: `F` itself, the direction
of the null comparison, and the sign of the functional gap. Fixing it drops `F`
from 0.732 to 0.275, a larger reduction than standardising any pre-registered
axis. We take this to be a general hazard for multiverse designs whose
specifications select objects of different sizes, and we report every pooled
statistic with its within-size decomposition.

*The multiverse is as wide as the library, not as wide as the literature.*
Optimal ablation, for instance, is a defensible operator that the instrument does
not implement, so it never entered the space.

*The discard rate is high and uneven.* 52.3%, and the surviving pool is metric
imbalanced. The threshold rule was fixed in advance and no failing item was
repaired, but the composition is a property of the reported set and we state it
rather than adjust for it.

*The bootstrap is invalid for one reported family.* Where the conditioning
groups hold only two to five specifications, retained self-pairs dominate and the
intervals are not usable; those quantities are reported as point estimates with
the diagnostic attached. We did not construct a bias-corrected estimator after
seeing the naive intervals disagree, because choosing an estimator in response to
a result is the behaviour this paper documents.

---

## 8. Discussion

*What a standards body could do tomorrow.* Adopt the filability criterion.
Require that a filed interpretability claim be accompanied by the specification
that produced it, and by the modal share of the claim over a declared
specification space. A filing that cannot state its own `pi*` has not been
audited; it has been asserted.

*What standardising one axis buys.* Less than it appears. The metric is the
biggest lever and removes 0.138 of a 0.732 flip rate. There is no single knob.

*On the instrument.* One of seven documented, publicly exported discovery
objectives does not run on the library's own canonical task. We report this as a
discard with its rate, and as an observation about the maturity of the tooling
that regulatory evidence is expected to rest on. It is not the paper's headline,
and it should not be read as criticism of a library whose authors are among those
calling for the field to address exactly this.

*On the phantom specialization reading.* If circuit discovery merely sampled
from an equivalence class of behaviourally identical subgraphs, a flip rate over
claims would be measuring which member was sampled. The functional measurement
rules that out here: kappa 0.015 across every scale tested. The circuits differ
structurally and behave differently, and the claims differ more than either.

---

## 9. Reproducibility

Every reported number traces to a config, a seed and an environment fingerprint.
The confirmatory sweep ran under a single environment across all 1,320 cells,
verified from the results archive rather than asserted. The analysis layer runs
without a GPU. `analysis/verify_all_claims.py` recomputes every headline quantity
from raw results and asserts against what is reported: 36 checks, 0 failures. The
test suite is 319 tests.

Deviations from the pre-registration are recorded in an append-only file, with
their dates and whether each was decided before or after the affected result was
seen.

---

## References

*Verified.*

Miller, J., Chughtai, B., and Saunders, W. Transformer Circuit Faithfulness
Metrics are not Robust. CoLM 2024. arXiv:2407.08734.

Méloux, M., Maniu, S., Portet, F., and Peyrard, M. Everything, Everywhere, All at
Once: Is Mechanistic Interpretability Identifiable? ICLR 2025. arXiv:2502.20914.

Méloux, M., Portet, F., and Peyrard, M. Mechanistic Interpretability as
Statistical Estimation: A Variance Analysis. arXiv:2510.00845v4.

Lan, M., Oozeer, N. F., Bandi, C., Quirke, P., Meek, A., Barez, F., and Abdullah,
A. Make Mechanistic Interpretability Auditable: A Call to Develop Guidelines via
Continuous Collaborative Reviewing. ACL 2026 main conference. arXiv:2606.00033.

Sharkey, L., Chughtai, B., Batson, J., et al. Open Problems in Mechanistic
Interpretability. arXiv:2501.16496.

Mueller, A., Geiger, A., Wiegreffe, S., et al. MIB: A Mechanistic Interpretability
Benchmark. ICML 2025. arXiv:2504.13151v2.

Wang, K., Variengien, A., Conmy, A., Shlegeris, B., and Steinhardt, J.
Interpretability in the Wild: a Circuit for Indirect Object Identification in
GPT-2 small. arXiv:2211.00593.

Conmy, A., Mavor-Parker, A. N., Lynch, A., Heimersheim, S., and Garriga-Alonso, A.
Towards Automated Circuit Discovery for Mechanistic Interpretability. NeurIPS 2023
Spotlight. arXiv:2304.14997v4.

Syed, A., Rager, C., and Conmy, A. Attribution Patching Outperforms Automated
Circuit Discovery. NeurIPS 2023 ATTRIB Workshop. arXiv:2310.10348v2.

Li, M., and Janson, L. Optimal ablation for interpretability. arXiv:2409.09951.

Hsia, J., Pruthi, D., Singh, A., and Lipton, Z. C. Goodhart's Law Applies to NLP's
Explanation Benchmarks. arXiv:2308.14272.

Buscemi, A., Deckenbrunnen, T., Kabir, F., Mishchenko, K., and Mowla, N. Assessing
High-Risk AI Systems under the EU AI Act: From Legal Requirements to Technical
Verification. arXiv:2512.13907v3.

Simonsohn, U., Simmons, J. P., and Nelson, L. D. Specification curve analysis.
Nature Human Behaviour 4(11), 1208-1214, 2020. doi:10.1038/s41562-020-0912-z.
See also Publisher Correction, doi:10.1038/s41562-020-00974-w.

Steegen, S., Tuerlinckx, F., Gelman, A., and Vanpaemel, W. Increasing Transparency
Through a Multiverse Analysis. Perspectives on Psychological Science, 2016.
doi:10.1177/1745691616658637.

Regulation (EU) 2024/1689, consolidated as amended by Regulation (EU) 2026/1744.
CELEX 02024R1689-20260727.

*Not verified. These must not survive to submission.*

† Simmons, J. P., Nelson, L. D., and Simonsohn, U. False-Positive Psychology.
doi:10.1177/0956797611417632. Two fetch attempts blocked.

† Bayat Makou, A., Niu, J., Dutta, S., and Gurevych, I. Many Circuits, One
Mechanism. Authors, findings and code verified from the replication repository;
**the arXiv identifier is contradicted by the authors' own BibTeX** and must be
resolved or the citation given as the repository.
