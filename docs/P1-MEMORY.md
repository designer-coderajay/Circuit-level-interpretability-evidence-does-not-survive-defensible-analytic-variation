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

## Open decisions blocking pre-registration

See `docs/DESIGN-DELTAS.md` for the full statement of each.

- **D3** Grid is **3,780** (7 x 3 x 4 x 3 x 3 x 5, edge-level). Feasibility
  **unmeasured**. Metric-relative tau means the sweep needs one prune-score
  ranking per discovery configuration, not 3,780 independent discoveries, which
  is a large saving. That is INFERRED from the API and not yet verified by
  running it.
- **D4** Functional-equivalence arm: the interchange protocol is still unread.
  Granularity is now resolved (D8). Pull the protocol from the UKPLab repo.
- **D7** The brief's positioning sentence is unsupported and must not be used.
- **D10** Articles 11, 13(3)(d) and 14 unread. 13(3)(d) and 14 define "facilitate
  the interpretation of the outputs", the phrase phi is now built on. Read before
  phi is implemented.
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
- Not built: the sweep harness, the claim map `phi`, the interchange-intervention
  arm, the specification curve, the variance decomposition.

## Standing hazards

- **Never compute a p-value across specifications.** They are a designed grid,
  not a sample. Use the random-circuit null multiverse for joint inference.
- **`phi` must be deterministic code, never an LLM.** Generating claim text with
  a model would add LLM variance on top of circuit variance with no way to
  separate them.
- **Report three granularities of `phi`.** A reviewer will say the flip rate was
  tuned. The three-granularity stability result is the answer.
- **The random-circuit baseline is not optional.** H3 has no meaning without it.
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
