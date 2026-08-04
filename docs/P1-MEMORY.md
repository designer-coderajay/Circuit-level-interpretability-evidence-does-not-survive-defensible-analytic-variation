# P1 memory

**Scope: Paper 1 only.** Nothing about P2 (agentic attribution) or P3
(monitorability) belongs in this file, and no assumption, number, or decision
from those papers may be imported here. Cross-paper information moves only
through `RESEARCH_LOG.md`.

This file exists because chat sessions do not remember across weeks. Read it at
the start of every session. Update it the day something is decided, not later.

---

## What P1 argues

Circuits are formally non-identifiable, and circuit faithfulness is sensitive to
the ablation operator. The EU AI Act requires technical documentation describing
how a high-risk system reaches its decisions. Nobody has connected these. If the
explanation filed as conformity evidence changes when a different competent
analyst runs the same tool with different defensible settings, the filing
carries no evidential weight. An audit means two auditors reach the same
conclusion.

P1 measures how far an Annex IV claim moves across the space of defensible
analytic specifications, and whether that movement is distinguishable from a
random baseline.

## Where the paper sits in the programme

P1 is the circuit-level instance of one claim made at three levels: the evidence
used to certify that an AI system is explainable does not survive contact with
the conditions under which it would need to be relied upon. P1 ships first.
Target arXiv 10 September 2026, FAccT 2027 in October.

## Decisions taken

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-03 | Instrument is **auto-circuit 1.0.1, verbatim** | It is the library released with arXiv:2407.08734, the paper P1 differentiates from. Using it unmodified removes the "you built a weak tool and then showed it wobbles" objection and satisfies the rule against modifying a published instrument under test. |
| 2026-08-03 | **Add the functional-equivalence arm** | arXiv:2606.06267 reports that structurally distinct circuits can implement the same computation. Without an interchange-intervention arm, a high flip rate does not license P1's conclusion. With it, the structural-versus-functional gap becomes the contribution. |
| 2026-08-03 | Build in sandbox, **sweep on rented GPU** | Development environment has no GPU. Code is device-agnostic; the statistics layer has no torch dependency. |
| 2026-08-03 | glassbox-mech-interp is **not** the primary instrument | P1 tests whether interpretability evidence is stable. Testing Ajay's own tool invites the objection that the instability is his implementation. It may appear as one specification among several. |
| 2026-08-03 | Dev on Mac in VS Code, **sweep on a rented CUDA box**, no Colab | auto-circuit has one device line, `"cuda" if t.cuda.is_available() else "cpu"`, and no MPS support. VERIFIED from source. Apple Silicon falls back to CPU, and adding MPS would mean editing the instrument under test. Colab's ephemeral filesystem makes an environment hash meaningless. |
| 2026-08-03 | **H1 demoted to premise; lead with the claim-level result** | 2606.06267 establishes that discovery samples from an equivalence class of valid subgraphs. Circuit multiplicity is no longer a contribution. The contribution is what that multiplicity does to an Annex IV filing. See DESIGN-DELTAS D9. |
| 2026-08-03 | **Edge-level is the confirmatory grid**, node-level a contrast | Their section 6.2: source-level evaluation inflates apparent faithfulness. The granularity choice is itself a documented researcher degree of freedom. See DESIGN-DELTAS D8. |
| 2026-08-03 | Gate 1 **passed**, P1 proceeds | Zero regulatory, conformity, audit, or technical-documentation content in either 2407.08734 or 2606.06267. The propagation and the filability criterion are unclaimed. |
| 2026-08-03 | **Claim map retargets to Annex IV 2(e) and 3; section 4 added as a second target** | 2(b) is a design-specification requirement and a discovered circuit is not a design specification. 2(e) and 3 carry "technical measures to facilitate the interpretation of the outputs", which is where an interpretability artefact is actually filed. Section 4 requires justifying metric appropriateness and is the cleanest justification for the metric axis. See docs/ANNEX-IV.md. |
| 2026-08-03 | **Private GitHub now, embargoed OSF registration at Gate 3**, both public at arXiv | The repo had no backup and no remote. A pre-registration timestamp attested only by a local clock is not evidence. OSF gives a DOI and a third-party timestamp under embargo, and is idiomatic for the methods literature P1 borrows from. |
| 2026-08-03 | **D1 closed: all seven auto-circuit ablation operators** | Optimal ablation and Gaussian noise are not in the instrument. Five of seven are mean variants, and 2407.08734 flags the mean-dataset-size choice without crossing it. |
| 2026-08-03 | **D2 closed: ERASER sufficiency and comprehensiveness enter the main grid** as an additive extension in `src/p1` | 2407.08734 declines to cross the metric dimension and calls the choice "in general free". Annex IV section 4 requires a description of metric appropriateness. |
| 2026-08-03 | **D12 closed: tau is metric-relative** | tau is the smallest circuit recovering (1 - tau) of metric m on the full model. Without this the evaluation metric never changes C and the metric axis would carry zero claim variance at four times the cost. Must be stated verbatim in the pre-registration; absolute tau is equally defensible. |
| 2026-08-03 | **Annex III VERIFIED: credit is 5(b), Article 86's excluded point 2 is critical infrastructure** | The BFSI applied arm is fully inside Article 86 and all four regulatory links bind on it. Describe it as creditworthiness evaluation, never fraud detection, which 5(b) carves out. |
| 2026-08-03 | **phi is two claim maps**: `phi_overseer` (Annex IV 2(e)/3 with Art 14(4)(c)) and `phi_affected` (Art 86(1)) | Two addressees, two legal standards, "correctly interpret" versus "clear and meaningful". phi is post-hoc deterministic code so six maps cost zero GPU time, and a divergence between the two flip rates is itself a finding. |
| 2026-08-03 | **D14 closed: `mask_gradient` is the primary discovery algorithm**, ACDC a contrast | Only `mask_gradient` and `subnetwork_probing` accept `ablation_type`. ACDC hardcodes corrupt-batch resample, so under ACDC the ablation axis touches evaluation only. MIB independently reports attribution and mask-optimisation methods best on circuit localisation. |
| 2026-08-04 | **GATE 2 PASSED.** discovery 9.301s, evaluation-per-cut 1.581s, ratio 5.88 (CPU, gpt2, 32 prompts) | Reuse architecture confirmed. Full EAP grid is **2.47 h CPU** versus 11.43 h naive, a **4.62x** saving. The 12x inferred on 08-03 was wrong: evaluation is 67% of cost, not near-free. |
| 2026-08-04 | **D15 resolved: discovery-objective axis = auto-circuit's eight named PruneAlgo constants**, not a synthetic 4x3 grid | They are named, shipped and used by the instrument's authors, so "cite a published implementation per level" holds by construction. Also catches EAP vs IEG, which is the mask_val/IG XOR and not a grad_function value. |
| 2026-08-04 | **D3 closed: confirmatory grid = 6 EAP + IEG-50 fully crossed (26,460 specs); IEG-1000 as a pre-registered seed-only slice** | ~70 h CPU total. IEG-1000 fully crossed would be 814 h. The slice answers "is 50 IG samples enough" at 1.5% of the cost, and the reduction rule is fixed before any pooled result is seen. |
| 2026-08-04 | **D4 closed: interchange protocol extracted from their code.** IIA machinery adopted as a cited **adaptation**, not a reproduction | They vary input statistics; P1 varies analytic specification. Pairing logic differs, IIA transfers. Cheaper `agreement_rate` + `cohens_kappa` runs across the full grid; expensive IIA on a pre-registered low-Jaccard subset. Their `j_rand = k/(2N-k)` adopted and implemented. |
| 2026-08-05 | **Backup closed. Private GitHub live**, `origin/main` at `751573f`, 171 objects | The repo existed on one laptop with no remote. Also cleaned 44 orphaned `tmp_obj_*` objects left by the Spotlight index-lock collisions; `git fsck` clean. Branch renamed `master` to `main` at the same time, cheapest moment it will ever be. |
| 2026-08-05 | **D18 closed: corruption is NESTED within ablation, not crossed** | Two of seven operators ignore corruption, so crossing produced 5,040 exact duplicates, 19% of the grid. The bias on `F` was negligible, 2.16e-05; the objection is methodological. A multiverse whose specifications are not distinct misrepresents itself. Cost: design is unbalanced, so REML replaces the closed-form EMS estimator, with EMS kept as a cross-check on the balanced five-operator block. |
| 2026-08-05 | **`clean_corrupt` fixed at `"corrupt"`, recorded not crossed** | A real undeclared degree of freedom for three of seven operators. Fixing it avoids a second nesting level. Stated in the pre-registration as a fixed choice and named in the limitations, so it is not left implicit. |
| 2026-08-05 | **Prompt variant = 2 levels, ABBA and BABA** | Both verbatim in 2407.08734 section 4, so each level cites a published implementation, the standard every other axis meets. The third level was never sourced and would have been the first thing a reviewer attacked. |
| 2026-08-05 | **H2 decision rule fixed: `F > 0.20` with the 95% bootstrap CI lower bound above it** | A judgement call, defended in the paper as one rather than dressed up as principled. `F` is reported with its full bootstrap distribution either way, and filability at three tolerances is reported alongside so the conclusion does not rest on one cut point. |
| 2026-08-05 | **Grid: 14,280 specifications from 1,190 discovery cells** | 54.0% of the previous 26,460 / 2,205 on both counts. Corruption nesting removes 420 duplicate discovery cells; dropping the unsourced third prompt variant removes a third of the remainder. |
| 2026-08-05 | **Mean-ablation dataset-size axis WITHDRAWN** | VERIFIED false as implementable. `mask_gradient_prune_scores` takes one `dataloader` and passes it both to `batch_src_ablations` and to the gradient loop, so the ablation-mean dataset and the discovery dataset are the same object. Separating them means modifying the instrument. Second time an attractive design move died on a source check. |
| 2026-08-05 | **All cost figures withheld from the plan until IEG-50 is measured** | Gate 2 measured EAP discovery only. IEG-50 runs `integrated_grad_samples + 1` full passes, so it plausibly dominates the budget while being one objective of seven. The 814-hour and 57-hour figures both rested on that unmeasured factor and are withdrawn. `configs/smoke-ieg.yaml` measures it. |

## Open decisions blocking pre-registration

See `docs/DESIGN-DELTAS.md` for the full statement of each.

- **D17** The CPU to GPU speedup is **unmeasured**. Every GPU figure quoted so
  far assumes 20x, which is a guess. Run one smoke config on the rented box
  before committing to the sweep window.
- **D7** The brief's positioning sentence is unsupported and must not be used.
- **D16** `PatchType.TREE_PATCH` may give ERASER sufficiency and `EDGE_PATCH`
  comprehensiveness directly, which would remove the need for the D2 extension
  layer and strengthen the verbatim-instrument claim. INFERRED from docstrings,
  verify by running, then revisit D2.
- **D10** Mostly closed. **Read: Annex III, Annex IV, Articles 13, 14, 86.**
  phi is unblocked and targets two addressees. **Article 11 still unread**, four
  attempts, one timeout. Article 11 governs the documentation obligation itself.
- **D13** Article 86(3) makes the right subsidiary to other Union law. **GDPR
  Article 22 collision must be addressed in the paper**, not left to a reviewer.
- **D11** All Annex IV strings came from a Commission rendering, not the Official
  Journal. Cross-check against the OJ before any of them enters the manuscript.

## What is built

- `src/p1/multiverse.py`: Jaccard overlap, flip rate `F`, modal share `pi_star`,
  filability, and a bootstrap that resamples specifications rather than pairs.
  numpy only, no GPU, runs anywhere.
- `tests/test_multiverse.py`: 35 tests, all passing as of 2026-08-03. The
  load-bearing one asserts the closed-form flip rate equals the brute-force
  pairwise definition across 2,000 randomised cases, and a second cross-checks
  it against the Gini-Simpson form quoted in the paper.
- `src/p1/spec.py` and `tests/test_spec.py`: the specification space, grid
  enumeration, and a machine-independent `spec_id` (truncated SHA-256 of a
  canonical encoding, pinned by regression test, verified stable across
  PYTHONHASHSEED values). **59 tests total, all passing 2026-08-03.**
- `src/p1/claim_map.py` and `tests/test_claim_map.py`: **phi**, both addressees,
  three nested granularities. Deterministic, no LLM, thresholds all named
  arguments. The nesting property (FINE refines MEDIUM refines COARSE) is
  unit-tested over randomised circuits for both maps, which is the structural
  answer to "you tuned phi". **79 tests total, all passing 2026-08-03.**
- `src/p1/features.py` and `tests/test_features.py`: the auto-circuit to
  `CircuitFeatures` seam. Handles the layer-convention trap, auto-circuit counts
  each transformer block as **two** layers, with a regression test asserting a
  final-block component lands in the "late" band. **Written against the source,
  NOT yet executed against the library.**
- `src/p1/manifest.py`: run manifests. Environment fingerprint excluding time
  and host, content-addressed hashes, dirty-tree detection, and the
  config/seed/environment triple standing rule 8 requires. Written even on
  failure so discards stay reportable.
- `src/p1/prompts.py`: prompt set generation, the P axis. **The auto-circuit
  wheel ships no datasets**, so P1 supplies its own in auto-circuit's schema via
  `load_datasets_from_json`. Templates are P1's own, not Wang et al.'s.
- `scripts/smoke.py` and `configs/smoke.yaml`: Gate 2. Produces `discovery_s`
  and `evaluation_per_cut_s` separately. **NOT YET EXECUTED**, no torch in the
  sandbox.
- **147 tests total, all passing 2026-08-03.**
- Not built: the full sweep harness, the interchange-intervention arm, the
  specification curve, the variance decomposition.
- **Pre-registration must freeze:** `DEFAULT_SIZE_BINS`, `DEFAULT_BAND_NAMES`,
  and the per-task input segment definitions used as `position_mass` keys. All
  three are currently PROVISIONAL.

## Standing hazards

- **Never compute a p-value across specifications.** They are a designed grid,
  not a sample. Use the random-circuit null multiverse for joint inference.
- **`phi` must be deterministic code, never an LLM.** Generating claim text with
  a model would add LLM variance on top of circuit variance with no way to
  separate them.
- **Report three granularities of `phi`.** A reviewer will say the flip rate was
  tuned. The three-granularity stability result is the answer.
- **The random-circuit baseline is not optional.** H3 has no meaning without it.
- **Expect H3 to FAIL at the circuit level.** Their calibration puts observed
  Jaccard 4-27x above random, and at 32,491 edges a 500-edge circuit has
  `J_rand = 0.008`. H3 is about the CLAIM, not circuit overlap. Keep the two
  levels separate and state the expectation in the pre-registration.
- **Feasibility is unmeasured.** The 2,160-runs-on-one-24GB-GPU claim came from
  the brief with no timing behind it.

## Both outcomes must stay writeable

If circuits turn out highly stable across the crossed space, that is the
positive result and it is publishable. Draft both abstracts before running the
pooled analysis. If only one direction is writeable, the design is wrong.

## Kill criteria

- If 2407.08734 on full reading already contains a downstream-claim analysis,
  drop or reframe.
- If 2606.06267 on full reading already propagates structural instability to a
  downstream claim, reassess novelty the same day.

Kill gates are binding. When one fails, stop and reallocate that day.
