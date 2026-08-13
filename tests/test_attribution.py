"""Tests for input-segment attribution.

`phi_affected` is half the claim map and it reads `position_mass`. Until
2026-08-06 nothing produced one, so every specification would have emitted the
same claim and the flip rate would have been exactly zero as an artifact. These
tests pin the properties that make the mass a usable input to a claim: it must
be deterministic, order-independent, normalised, and it must render absence as
absence rather than as a fabricated distribution.
"""

from __future__ import annotations

import pytest

from p1.attribution import segment_mass
from p1.claim_map import CircuitFeatures, Component, Granularity, phi_affected

LABELS = ["prefix", "name_first", "name_second", "place", "subject", "object", "final"]


def _uniform(n: int) -> list[float]:
    return [1.0 / n] * n


# --------------------------------------------------------------------------
# Absence
# --------------------------------------------------------------------------


def test_no_attention_heads_yields_empty_mass_not_a_fabricated_one():
    """A circuit can contain no attention heads. That must not invent a mass."""
    assert segment_mass([], LABELS) == {}


def test_empty_mass_renders_as_a_stated_absence():
    f = CircuitFeatures(frozenset({Component(1, 1)}), 12, 156, segment_mass([], LABELS))
    assert "no single input region" in phi_affected(f, Granularity.COARSE)


def test_all_zero_attention_is_absence_not_an_error():
    """A masked or sliced tensor can produce this; it is reachable in a sweep."""
    assert segment_mass([[0.0] * len(LABELS)], LABELS) == {}


# --------------------------------------------------------------------------
# Normalisation and accumulation
# --------------------------------------------------------------------------


def test_mass_sums_to_one():
    rows = [_uniform(len(LABELS)), [0.5, 0.5, 0, 0, 0, 0, 0]]
    m = segment_mass(rows, LABELS)
    assert abs(sum(m.values()) - 1.0) < 1e-12


def test_repeated_labels_accumulate():
    """A segment spanning several tokens must collect all of their mass."""
    labels = ["a", "a", "b"]
    m = segment_mass([[0.25, 0.25, 0.5]], labels)
    assert abs(m["a"] - 0.5) < 1e-12
    assert abs(m["b"] - 0.5) < 1e-12


def test_heads_are_weighted_uniformly_not_by_magnitude():
    """Two heads, one attending everywhere to 'x', one everywhere to 'y'.

    Uniform weighting must split the mass evenly regardless of how the rows are
    scaled relative to each other, which is the property that makes the mass
    comparable across the discovery-objective axis.
    """
    labels = ["x", "y"]
    m = segment_mass([[1.0, 0.0], [0.0, 1.0]], labels)
    assert abs(m["x"] - 0.5) < 1e-12 and abs(m["y"] - 0.5) < 1e-12


def test_a_single_head_dominating_one_segment_is_reflected():
    labels = ["x", "y"]
    m = segment_mass([[0.9, 0.1], [0.8, 0.2]], labels)
    assert m["x"] > m["y"]


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------


def test_head_order_does_not_change_the_mass():
    rows = [[0.7, 0.2, 0.1], [0.1, 0.1, 0.8], [0.3, 0.3, 0.4]]
    labels = ["a", "b", "c"]
    assert segment_mass(rows, labels) == segment_mass(list(reversed(rows)), labels)


def test_output_key_order_is_sorted_and_stable():
    labels = ["zulu", "alpha", "mike"]
    m = segment_mass([[0.2, 0.5, 0.3]], labels)
    assert list(m) == sorted(labels)


def test_repeated_calls_agree_exactly():
    rows = [[0.1, 0.2, 0.7], [0.4, 0.4, 0.2]]
    labels = ["a", "b", "c"]
    assert segment_mass(rows, labels) == segment_mass(rows, labels)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------


def test_row_length_must_match_the_label_count():
    with pytest.raises(ValueError, match="same sequence"):
        segment_mass([[0.5, 0.5]], LABELS)


def test_negative_attention_is_rejected():
    with pytest.raises(ValueError, match="negative"):
        segment_mass([[-0.1, 1.1] + [0.0] * (len(LABELS) - 2)], LABELS)


def test_empty_labels_are_rejected():
    with pytest.raises(ValueError, match="seq_labels"):
        segment_mass([[1.0]], [])


# --------------------------------------------------------------------------
# End to end into a claim
# --------------------------------------------------------------------------


def test_mass_flows_into_a_distinguishing_affected_claim():
    """The point of the whole module: different attention gives different claims.

    If this fails, phi_affected is constant across the grid and its flip rate is
    an artifact rather than a finding.
    """
    labels = ["income", "credit_history", "employment"]
    a = CircuitFeatures(
        frozenset({Component(1, 0)}), 12, 156, segment_mass([[0.8, 0.1, 0.1]], labels)
    )
    b = CircuitFeatures(
        frozenset({Component(1, 0)}), 12, 156, segment_mass([[0.1, 0.1, 0.8]], labels)
    )
    assert phi_affected(a, Granularity.COARSE) != phi_affected(b, Granularity.COARSE)
    assert "income" in phi_affected(a, Granularity.COARSE)
    assert "employment" in phi_affected(b, Granularity.COARSE)


# --------------------------------------------------------------------------
# Role labels: segments by character span, not by token position
# --------------------------------------------------------------------------
#
# An earlier version of this module assumed a single positional seq_labels list
# could describe every prompt. It cannot: the three templates have different
# token counts, names tokenise to different numbers of tokens, and the repeated
# name occupies two spans. Aggregating by role follows arXiv:2211.00593 Fig 10.

from p1.attribution import OTHER_ROLE, mean_segment_mass, token_role_labels

PROMPT = "When Mary and John went to the store, John gave the apple to"
# Deliberately uneven, as a real tokeniser is: some words split, some do not.
TOKENS = ["When", " Mary", " and", " John", " went", " to", " the", " st", "ore",
          ",", " John", " gave", " the", " app", "le", " to"]
ROLES = {"IO": "Mary", "S1": "John", "S2": "John", "place": "store", "object": "apple"}


def test_labels_align_with_roles_not_positions():
    labels = token_role_labels(TOKENS, PROMPT, ROLES)
    assert len(labels) == len(TOKENS)
    assert labels[TOKENS.index(" Mary")] == "IO"
    assert labels[3] == "S1"      # first " John"
    assert labels[10] == "S2"     # second " John"


def test_a_multi_token_role_gets_every_one_of_its_tokens():
    """'store' splits into ' st' + 'ore'; both must carry the role."""
    labels = token_role_labels(TOKENS, PROMPT, ROLES)
    assert labels[7] == "place" and labels[8] == "place"
    assert labels[13] == "object" and labels[14] == "object"


def test_the_repeated_name_resolves_to_two_distinct_roles():
    """S1 and S2 are the same string. Occurrence order is what separates them."""
    labels = token_role_labels(TOKENS, PROMPT, ROLES)
    assert labels.count("S1") == 1
    assert labels.count("S2") == 1


def test_template_scaffolding_is_labelled_rather_than_dropped():
    labels = token_role_labels(TOKENS, PROMPT, ROLES)
    assert labels[0] == OTHER_ROLE
    assert OTHER_ROLE in labels


def test_tokens_that_do_not_reconstruct_the_prompt_are_rejected():
    """A normalising tokeniser would misalign every span silently."""
    with pytest.raises(ValueError, match="reconstruct"):
        token_role_labels(["When", " Mary"], PROMPT, ROLES)


def test_a_role_absent_from_the_prompt_is_rejected():
    with pytest.raises(ValueError, match="not found"):
        token_role_labels(TOKENS, PROMPT, {**ROLES, "IO": "Zebediah"})


def test_labels_work_on_a_second_template_of_different_length():
    """The whole point: no shared positional map is needed."""
    p2 = "After Bob and Sue arrived at the park, Sue passed the ball to"
    toks = ["After", " Bob", " and", " Sue", " arrived", " at", " the", " park",
            ",", " Sue", " passed", " the", " ball", " to"]
    roles = {"IO": "Bob", "S1": "Sue", "S2": "Sue", "place": "park", "object": "ball"}
    labels = token_role_labels(toks, p2, roles)
    assert labels[1] == "IO" and labels[3] == "S1" and labels[9] == "S2"
    assert len(labels) != len(TOKENS)


# --------------------------------------------------------------------------
# Averaging across prompts
# --------------------------------------------------------------------------


def test_mean_of_one_mass_is_itself():
    m = {"IO": 0.6, "S2": 0.4}
    assert mean_segment_mass([m]) == pytest.approx(m)


def test_mean_across_prompts_is_normalised():
    out = mean_segment_mass([{"IO": 1.0}, {"S2": 1.0}])
    assert out == pytest.approx({"IO": 0.5, "S2": 0.5})


def test_a_prompt_with_empty_mass_still_counts_in_the_denominator():
    """Dropping it would reweight toward prompts that happened to attend somewhere."""
    out = mean_segment_mass([{"IO": 1.0}, {}])
    assert out == pytest.approx({"IO": 1.0})
    assert mean_segment_mass([]) == {}


def test_role_labels_feed_segment_mass_end_to_end():
    labels = token_role_labels(TOKENS, PROMPT, ROLES)
    rows = [[0.0] * len(TOKENS) for _ in range(2)]
    rows[0][1] = 1.0            # head 0 attends entirely to the IO name
    rows[1][10] = 1.0           # head 1 attends entirely to S2
    mass = segment_mass(rows, labels)
    # Zero-mass roles are retained deliberately: "attended nowhere" and "segment
    # absent" must stay distinguishable, so the mass covers every role present
    # in the sequence rather than only the ones that scored.
    assert mass["IO"] == pytest.approx(0.5)
    assert mass["S2"] == pytest.approx(0.5)
    assert set(mass) == {"IO", "S1", "S2", "place", "object", OTHER_ROLE}
    assert all(mass[r] == 0.0 for r in ("S1", "place", "object", OTHER_ROLE))


# --- split_leading_bos ----------------------------------------------------
#
# Extracted from scripts/sweep.py on 2026-08-12 because the logic it replaces
# was untestable there (the module imports torch) and shipped a wrong
# assumption that failed 924 of 924 cells.


def test_no_leading_bos_is_reported_not_silently_stripped():
    """The configuration that broke the replication run.

    `to_str_tokens(prompt, prepend_bos=True)` honours `tokenizer.add_bos_token`,
    so clearing that flag switches off prepending. The old code stripped
    `str_tokens[0]` regardless and ate the word "Then".
    """
    from p1.attribution import split_leading_bos

    toks = ["Then", " James", " and", " David"]
    n, body = split_leading_bos(toks, "<|endoftext|>")
    assert n == 0
    assert body == toks


def test_one_leading_bos():
    from p1.attribution import split_leading_bos

    toks = ["<|endoftext|>", "Then", " James"]
    n, body = split_leading_bos(toks, "<|endoftext|>")
    assert n == 1
    assert body == ["Then", " James"]


def test_two_leading_bos():
    """Reachable: a string-prepended BOS meeting a tokenizer that adds its own.

    VERIFIED on Pythia-160m 2026-08-12 before the tokenizer was aligned:
    clean prompts began [0, 0, 5872] against GPT-2's single [50256, ...].
    """
    from p1.attribution import split_leading_bos

    toks = ["<|endoftext|>", "<|endoftext|>", "Then", " James"]
    n, body = split_leading_bos(toks, "<|endoftext|>")
    assert n == 2
    assert body == ["Then", " James"]


def test_body_reconstructs_the_prompt_after_the_split():
    """The property the caller actually depends on, asserted directly."""
    from p1.attribution import split_leading_bos, token_role_labels

    prompt = "Then James and David were at the office, and David handed the book to"
    toks = ["<|endoftext|>", "Then", " James", " and", " David",
            " were at the office, and", " David", " handed the book to"]
    n, body = split_leading_bos(toks, "<|endoftext|>")
    assert "".join(body) == prompt
    # And the reconstruction check downstream now passes rather than raising.
    labels = token_role_labels(body, prompt, {"IO": "James", "S1": "David", "S2": "David"})
    assert len(labels) == len(body)


def test_split_does_not_consume_an_all_bos_sequence_incorrectly():
    from p1.attribution import split_leading_bos

    n, body = split_leading_bos(["<|endoftext|>", "<|endoftext|>"], "<|endoftext|>")
    assert n == 2
    assert body == []
