# Audit of the 3 August brief against what was built

Every claim in `paper-1-circuit-multiverse.md` checked against committed code,
committed results, and fetched sources. The brief was the design; this records
where the design and the executed work diverge, so no sentence written from the
brief enters the paper uncorrected.

**Status key.** HOLDS, MOVED, DROPPED, WRONG.

---

## Formalism, section 4

| Brief | Reality | Status |
|---|---|---|
| `s = (a, d, m, tau, P, r)`, six fields | Eight: `(discovery_objective, ablation, corruption, metric, threshold, prompt_variant, seed, granularity)` | **MOVED** |
| `a in {zero, mean, resample, optimal}` | Seven members of `auto_circuit.types.AblationType`. **`optimal` is not one of them.** Optimal ablation is 2409.09951's method, not in the instrument. | **WRONG** |
| `m in {sufficiency, comprehensiveness, F1, logit-difference recovery}` | `{logit_diff, kl_div, sufficiency, comprehensiveness}`. **`F1` was dropped, `kl_div` added.** | **MOVED** |
| `C(s) subset of H`, "a set of attention heads" | Edge-level. `C(s)` is a subset of 32,491 edges. Components are 156, being 144 heads plus 12 MLPs. Node-level was never run. | **MOVED** |
| Discovery objective absent from the tuple | Seven objectives became the first axis, and one of them turned out not to execute | **MOVED** |

**The mathematics checks out.** `J_bar = 2/(|S|(|S|-1)) sum_{i<j} J_ij` is correctly
normalised: there are `|S|(|S|-1)/2` unordered pairs. `D = 1 - J` is consistent.
`F = Pr_{i != j}[phi_i != phi_j]` over ordered distinct pairs equals the unbiased
Gini-Simpson estimator `1 - sum_c n_c(n_c-1) / (N(N-1))` implemented in
`p1.multiverse.flip_rate`, which is unit-tested against the brute-force pairwise
definition. **The brief's estimator and the implementation agree.**

Filability, `pi* >= 1 - alpha`, matches `p1.multiverse.is_filable` exactly.

---

## Hypotheses, section 3

| Brief | Final | Status |
|---|---|---|
| H1: overlap substantially below 1 | **P0**, relabelled, and demoted to a premise that is reported, not tested | MOVED |
| H2: claim flips on a non-trivial fraction | H2, threshold fixed at `F > 0.20` with the CI lower bound above it | HOLDS |
| H3: instability **not** separated from random | Tested and **rejected**: separated. But the pooled direction is a size artefact and reverses when size is held fixed. | **MOVED** |
| (absent) | **H4** added: `F - (1 - agreement_rate) > 0.10` | ADDED |

**The brief's reading of H3 no longer applies.** It says "if H3 holds, filed
evidence carries little more information than chance". H3 was rejected: discovered
circuits are more stable than size-matched random ones at fixed size, 0.2746
against 0.4230. The evidence carries information. It is still not filable.

---

## Experimental setup, section 6

| Brief | Reality | Status |
|---|---|---|
| GPT-2 small, Pythia-410M, Pythia-1.4B, plus a modern 1 to 2B model | **GPT-2 small only** | **DROPPED** |
| IOI plus a second task | **IOI only** | **DROPPED** |
| BFSI credit underwriting applied arm | **Not run** | **DROPPED** |
| 4 x 3 x 4 x 3 x 3 x 5 = 2,160 runs | 1,540 discovery cells, 18,480 specifications pre-registered; **1,320 and 15,840 realised**; 7,561 produced a claim | **MOVED** |
| "Feasible on a single 24GB GPU" | Run on an L4, 24GB, peak 3,651 MB. Feasible, and the estimate was right. | HOLDS |

**Three scope reductions the paper must state plainly.** The multi-model
replication, the second task, and the applied credit arm were all designed and
none was run. The scale limitation the brief anticipated is therefore larger than
the brief anticipated: not "GPT-2 is small" but "one model, one task".

---

## Claim map, section 5

| Brief | Reality | Status |
|---|---|---|
| Tuple of (dominant layer band, dominant head-role category, top-k attended positions) | `overseer_key` is `(layer_band)` at COARSE, `+ size_class` at MEDIUM, `+ ranked_segments` at FINE. **Head-role category was replaced by size class.** | **MOVED** |
| Report under three granularities | Done, and all six addressee-granularity cells agree qualitatively | HOLDS |
| "A reviewer will say you tuned phi" | Answered by measurement: `F` ranges 0.70 to 0.77 across binnings differing by 4x, and the committed bins are **not** a maximum | HOLDS, strengthened |
| Do not use an LLM for claim text | Honoured. `phi` is deterministic code. | HOLDS |

---

## Statistics, section 8

| Brief | Reality | Status |
|---|---|---|
| No naive p-values across the multiverse | Honoured. None computed anywhere. | HOLDS |
| Bootstrap CIs over specifications | Honoured, B = 10,000, seed 0, resampling specifications not pairs | HOLDS |
| Variance decomposition by choice dimension | **The brief, and the pre-registration after it, named an estimator without a response variable.** REML cannot take a categorical claim. Resolved by running both a structural REML and a declared claim-level decomposition. | **WRONG** |
| Specification curve as Figure 1 | **Not produced.** Owed. | OUTSTANDING |
| Seed variance reported separately, ratio a headline | Done, but `seed` varies the sampled prompts, not nondeterminism, so the headline must be worded accordingly | MOVED |

---

## Citations, section 11

The brief marks nine identifiers "Verified in search (IDs confirmed)". **Search
confirmation is not verification.** Under the project's own rule a citation is
verified only when the primary record has been fetched and every field confirmed.

Fetched and confirmed this session:

| ID | Field | Brief | Fetched | Note |
|---|---|---|---|---|
| 2407.08734 | title | *Transformer Circuit Faithfulness Metrics Are Not Robust* | *Transformer Circuit Faithfulness Metrics are not Robust* | **Case drift.** Use the fetched form. |
| 2407.08734 | authors | not stated | Joseph Miller, Bilal Chughtai, William Saunders | recorded |
| 2407.08734 | venue | COLM 2024 | Comments field reads **CoLM 2024** | **Spelling.** Use CoLM. |
| 2407.08734 | date | not stated | submitted 11 Jul 2024, v1 only | recorded |
| 2409.09951 | abstract | *Optimal Ablation for Interpretability* | abstract fetched and matches, proposing "optimal ablation (OA)" | title and authors **not yet confirmed** |

**Not yet fetched, and therefore not citable:** 2510.00845, 2606.00033,
2501.16496, 2504.13151, 2512.13907, 2308.14272.

**2606.06267 is a special case and the most serious.** Its authors, venue,
findings and code were verified from their own replication repository. But their
README states the preprint "will be made available on arXiv; please check back
here for the final citation once it is posted", and their BibTeX carries
`note = {arXiv preprint, link to be added}`. **The identifier 2606.06267 is not
confirmed by the authors' own artifact and must not be printed until it
resolves.**

Also unresolved from the brief's own "CHECK BEFORE CITING" list: Meloux et al.,
Mueller et al., Wang et al. (IOI), Conmy et al. (ACDC), Nanda et al. (attribution
patching), Steegen et al., Simmons et al., Simonsohn et al.

---

## Positioning, section 10

The brief's differentiation from 2407.08734 **holds and is now sharper.** They
establish that faithfulness metrics are sensitive to ablation methodology. This
work crosses seven axes and propagates the result to a regulatory claim with a
filability criterion.

The brief's advice to lead with the claim-flip result rather than circuit
instability **is correct and is now better supported**, because circuit
instability at `J_bar = 0.1396` is close to what the prior literature already
reports, whereas the claim-level result and the filability criterion are new.

**One addition the brief could not have known.** 2606.06267 argues discovery
samples from an equivalence class of valid subgraphs. That is the strongest
available objection to this paper, and it is answered rather than deflected:
Cohen's kappa of 0.0146 shows the circuits are functionally uncorrelated, so they
are not one mechanism in different clothes.

---

## Kill criteria, section 15

- "If 2407.08734 already includes a downstream-claim analysis, drop or reframe."
  **Checked 2026-08-04, not triggered.** Zero regulatory, conformity or audit
  terms in that paper.
- "If circuits turn out highly stable, publish that." Not triggered. `J_bar` is
  0.1396 and `F` is 0.7316.

---

## What the paper inherits from the brief unchanged

The research question, the filability criterion as the deliverable, the
instruction to publish the mapping code, the refusal to use an LLM for claim
text, the refusal to compute p-values across specifications, and the requirement
to report three granularities. All held under execution, and the last two were
tested rather than assumed.
