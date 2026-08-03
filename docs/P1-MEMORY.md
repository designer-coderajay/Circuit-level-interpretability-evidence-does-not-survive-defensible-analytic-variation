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

## Open decisions blocking pre-registration

See `docs/DESIGN-DELTAS.md` for the full statement of each.

- **D1** Ablation dimension: auto-circuit ships seven operators, not the brief's
  four, and optimal ablation is not among them.
- **D2** Metrics: sufficiency and comprehensiveness are not in auto-circuit's
  registry and would need an additive extension layer.
- **D3** Grid size: 2,160 under the brief, 3,780 under D1(a). Feasibility in the
  10 to 24 August window is **unmeasured**. Do not repeat the brief's
  feasibility claim until the smoke config produces a timing number.
- **D4** Functional-equivalence arm: the interchange protocol is still unread.
  Granularity is now resolved (D8). Pull the protocol from the UKPLab repo.
- **D7** The brief's positioning sentence is unsupported and must not be used.

## What is built

- `src/p1/multiverse.py`: Jaccard overlap, flip rate `F`, modal share `pi_star`,
  filability, and a bootstrap that resamples specifications rather than pairs.
  numpy only, no GPU, runs anywhere.
- `tests/test_multiverse.py`: 35 tests, all passing as of 2026-08-03. The
  load-bearing one asserts the closed-form flip rate equals the brute-force
  pairwise definition across 2,000 randomised cases, and a second cross-checks
  it against the Gini-Simpson form quoted in the paper.
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
