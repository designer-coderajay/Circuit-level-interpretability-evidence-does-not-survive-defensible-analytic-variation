"""Functional agreement between two circuits, reproduced verbatim.

Source: `LSC_circuit_analysis/05_Phase_Targeted/per_example_agreement.py` in
`github.com/UKPLab/arxiv2026-phantom-specialization`, the replication code for
Bayat Makou, Niu, Dutta and Gurevych (2026), *Many Circuits, One Mechanism*.
Apache-2.0. Fetched and read 2026-08-11.

**The two functions below are transcribed character for character.** They are the
instrument for H4 and for the functional-equivalence check the red team named as
the paper's most serious open objection, so reproducing rather than improving
them is the whole point. Their quirks are theirs:

- `agreement_rate` asserts the two prediction dicts have identical key sets and
  raises rather than intersecting them.
- `cohens_kappa` computes expected agreement from marginal positive rates and
  returns exactly 1.0 when `p_e == 1.0`, which is the degenerate case where both
  circuits are right on everything or wrong on everything. That convention is
  theirs and is not second-guessed here.

Anything P1 adds lives below the marked boundary and is additive only.

`preds` is `{example_index: bool}`, where the bool is whether the circuit got
that example right. P1's repair run writes the same shape as their
`per_example_eval` JSON so the adaptation stays legible.

**Adaptation, not reproduction, and the distinction matters.** They pair circuits
extracted under different *input statistics* with the analysis fixed. P1 pairs
circuits extracted under different *analytic specifications* with the input
fixed. The pairing logic differs; only these two measures transfer. See
DESIGN-DELTAS D4.
"""

from __future__ import annotations

from collections.abc import Mapping

__all__ = ["agreement_rate", "cohens_kappa", "pairwise_agreement"]


# --------------------------------------------------------------------------
# Verbatim from per_example_agreement.py. Do not edit.
# --------------------------------------------------------------------------


def agreement_rate(preds_a, preds_b):
    assert set(preds_a.keys()) == set(preds_b.keys())
    agree = sum(1 for i in preds_a if preds_a[i] == preds_b[i])
    return agree / len(preds_a)


def cohens_kappa(preds_a, preds_b):
    n = len(preds_a)
    agree = sum(1 for i in preds_a if preds_a[i] == preds_b[i])
    p_o = agree / n
    # Marginal frequencies
    a_pos = sum(1 for v in preds_a.values() if v) / n
    b_pos = sum(1 for v in preds_b.values() if v) / n
    p_e = a_pos * b_pos + (1 - a_pos) * (1 - b_pos)
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1 - p_e)


# --------------------------------------------------------------------------
# P1 additions below. Additive only; nothing above is called differently.
# --------------------------------------------------------------------------


def pairwise_agreement(
    predictions: Mapping[str, Mapping[int, bool]],
) -> dict[str, float]:
    """Mean agreement and kappa over all unordered pairs of specifications.

    `predictions` maps a specification id to its per-example verdicts. H4 needs
    `1 - agreement_rate` as the functional instability to set against `F`, the
    claim instability, so the mean is over the same pair population `F` uses:
    every unordered pair once, each weighted equally.

    Kappa is reported alongside because raw agreement is inflated when both
    circuits are mostly correct, which on IOI they will be. Reporting only
    agreement would overstate functional equivalence, which is the direction
    that would flatter this paper's argument.
    """
    keys = list(predictions)
    if len(keys) < 2:
        raise ValueError(f"need at least 2 specifications, got {len(keys)}")

    agreements: list[float] = []
    kappas: list[float] = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = predictions[keys[i]], predictions[keys[j]]
            agreements.append(agreement_rate(a, b))
            kappas.append(cohens_kappa(a, b))

    n = len(agreements)
    return {
        "n_pairs": n,
        "mean_agreement": sum(agreements) / n,
        "mean_kappa": sum(kappas) / n,
        "functional_instability": 1.0 - sum(agreements) / n,
    }
