"""Tests for prompt set generation, the P axis of the specification space.

Two things must hold or the whole grid is compromised. Generation must be exactly
reproducible from a seed, because the prompt set is part of the specification and
a number produced from an irreproducible prompt set is untraceable. And the
corrupt distribution must genuinely be ABC, three distinct names with no correct
completion, because if a corrupt prompt accidentally admits the clean answer the
patching signal is contaminated in a way no downstream test would catch.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p1.prompts import (
    EXAMPLE_NAMES,
    EXAMPLE_TEMPLATES,
    generate_ioi_dataset,
    write_dataset_json,
)


# --------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------


def test_generation_is_deterministic_given_a_seed():
    a = generate_ioi_dataset(40, seed=7)
    b = generate_ioi_dataset(40, seed=7)
    assert a == b


def test_different_seeds_give_different_sets():
    a = generate_ioi_dataset(40, seed=1)
    b = generate_ioi_dataset(40, seed=2)
    assert a["prompts"] != b["prompts"]


def test_order_changes_the_prompts():
    a = generate_ioi_dataset(20, seed=3, order="ABBA")
    b = generate_ioi_dataset(20, seed=3, order="BABA")
    assert a["prompts"] != b["prompts"]


def test_requested_count_is_honoured():
    assert len(generate_ioi_dataset(17, seed=0)["prompts"]) == 17


# --------------------------------------------------------------------------
# The IOI structure
# --------------------------------------------------------------------------


def test_clean_answer_appears_once_and_distractor_twice():
    """The answer is the indirect object: the name that appears exactly once."""
    ds = generate_ioi_dataset(60, seed=11)
    for p in ds["prompts"]:
        answer = p["answers"][0].strip()
        wrong = p["wrong_answers"][0].strip()
        assert p["clean"].count(answer) == 1, p["clean"]
        assert p["clean"].count(wrong) == 2, p["clean"]


def test_answer_and_distractor_are_different_names():
    ds = generate_ioi_dataset(60, seed=12)
    for p in ds["prompts"]:
        assert p["answers"][0] != p["wrong_answers"][0]


def test_answers_carry_a_leading_space():
    """GPT-2 byte-level BPE: the answer token is ' John', not 'John'."""
    ds = generate_ioi_dataset(10, seed=4)
    for p in ds["prompts"]:
        assert p["answers"][0].startswith(" ")
        assert p["wrong_answers"][0].startswith(" ")


def test_corrupt_uses_three_distinct_names():
    """ABC distribution. Three independent names, so no completion is correct."""
    ds = generate_ioi_dataset(80, seed=13)
    for p in ds["prompts"]:
        present = [n for n in EXAMPLE_NAMES if n in p["corrupt"]]
        assert len(present) == 3, f"expected 3 distinct names, got {present}"
        for n in present:
            assert p["corrupt"].count(n) == 1, f"{n} repeats in corrupt: {p['corrupt']}"


def test_clean_and_corrupt_differ():
    ds = generate_ioi_dataset(50, seed=14)
    for p in ds["prompts"]:
        assert p["clean"] != p["corrupt"]


def test_prompts_end_at_the_answer_slot():
    """The next token must be the answer, so the prompt ends with 'to'."""
    ds = generate_ioi_dataset(30, seed=15)
    for p in ds["prompts"]:
        assert p["clean"].rstrip().endswith("to")
        assert p["corrupt"].rstrip().endswith("to")


# --------------------------------------------------------------------------
# auto-circuit schema conformance
# --------------------------------------------------------------------------


def test_top_level_keys_match_the_loader_schema():
    """The schema block, not the prose, is what load_datasets_from_json parses.

    `seq_labels` is deliberately ABSENT, and its removal on 2026-08-06 is the
    point of this test. It was a seven-entry positional list, but prompts
    tokenise to 15 to 20 tokens across three templates of differing length and
    names tokenise to differing token counts, so no positional map could ever
    have described a prompt. Segments are now resolved per prompt from
    `p1_roles` by character span. If `seq_labels` ever comes back, something has
    reintroduced a contract the data cannot satisfy.
    """
    ds = generate_ioi_dataset(5, seed=0)
    assert "prompts" in ds
    assert "seq_labels" not in ds
    assert "p1_roles" in ds
    assert len(ds["p1_roles"]) == len(ds["prompts"])


def test_roles_are_recorded_for_every_prompt():
    ds = generate_ioi_dataset(8, seed=0)
    for roles in ds["p1_roles"]:
        assert set(roles) == {"IO", "S1", "S2", "place", "object"}
        assert roles["S1"] == roles["S2"], "S1 and S2 are the same name"
        assert roles["IO"] != roles["S1"]


def test_recorded_roles_resolve_against_the_clean_prompt():
    """End to end: the roles a dataset records must label its own prompts."""
    from p1.attribution import token_role_labels

    ds = generate_ioi_dataset(8, seed=3)
    for prompt, roles in zip(ds["prompts"], ds["p1_roles"]):
        clean = prompt["clean"]
        # Stand in for a tokeniser by splitting into characters: the only
        # contract token_role_labels requires is that the pieces concatenate
        # back to the prompt.
        labels = token_role_labels(list(clean), clean, roles)
        assert len(labels) == len(clean)
        assert labels.count("IO") == len(roles["IO"])
        assert labels.count("S1") == len(roles["S1"])
        assert labels.count("S2") == len(roles["S2"])


def test_name_occurrence_counts_are_validated():
    """A name appearing inside another word would claim the wrong span.

    Roles resolve by occurrence order in the prompt string, so if a name also
    occurs inside the place or object, the span for IO or S1 lands on the wrong
    characters and `phi_affected` attributes the decision to the wrong segment.
    Silent, and wrong in a way no downstream test would notice.

    Constructed to be deterministic rather than to rely on the sampler drawing
    the colliding name: every name here is a substring of the only place, so the
    collision fires on the first prompt whichever pair is drawn.
    """
    with pytest.raises(ValueError, match="must occur exactly"):
        generate_ioi_dataset(
            4,
            seed=0,
            names=("John", "Johns", "Johnst", "Johnsto"),
            places=("Johnstown",),
        )


def test_prompt_keys_are_clean_and_corrupt_not_clean_prompt():
    """Guards against the docstring prose that says clean_prompt/corrupt_prompt."""
    p = generate_ioi_dataset(1, seed=0)["prompts"][0]
    assert set(p) == {"clean", "corrupt", "answers", "wrong_answers"}
    assert "clean_prompt" not in p


def test_answers_are_lists_not_tuples_after_serialisation():
    p = generate_ioi_dataset(1, seed=0)["prompts"][0]
    assert isinstance(p["answers"], list)
    assert isinstance(p["wrong_answers"], list)


def test_round_trips_through_json(tmp_path: Path):
    ds = generate_ioi_dataset(25, seed=8)
    path = write_dataset_json(ds, tmp_path / "sets" / "ioi.json")
    assert path.exists()
    assert json.loads(path.read_text()) == ds


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs,match",
    [
        ({"n_prompts": 0}, "n_prompts"),
        ({"order": "AABB"}, "order"),
        ({"names": ("A", "B")}, "at least 4"),
        ({"names": ("A", "B", "C", "A")}, "distinct"),
        ({"templates": ()}, "non-empty"),
        ({"templates": ("{first} and {second} went",)}, "missing"),
    ],
)
def test_invalid_inputs_are_rejected(kwargs, match):
    base = dict(n_prompts=5, seed=0)
    base.update(kwargs)
    with pytest.raises(ValueError, match=match):
        generate_ioi_dataset(**base)


def test_write_rejects_a_dataset_without_prompts(tmp_path: Path):
    with pytest.raises(ValueError, match="prompts"):
        write_dataset_json({"seq_labels": []}, tmp_path / "bad.json")


def test_example_templates_are_well_formed():
    for t in EXAMPLE_TEMPLATES:
        for slot in ("{first}", "{second}", "{third}", "{place}", "{object}"):
            assert slot in t


# --------------------------------------------------------------------------
# The four corruption constructions, arXiv:2211.00593
# --------------------------------------------------------------------------
#
# These tests validate the implementation against the SOURCE PAPER'S OWN
# description of what each transformation does to the token and position
# signals, not against the derivation used to write the code. Wang et al.
# Figure 9 crosses a token signal in {original, random, S<->IO inverted} with a
# position signal in {original, inverted}, and Figure 10 states which cell each
# named transformation occupies. If a future edit changes a construction, the
# signal properties break and this fails loudly rather than silently altering a
# quarter of the corruption axis.

import random as _random
from collections import Counter as _Counter

from p1.prompts import _clean_slots, corrupt_slots

_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]


def _io_signal(slots):
    """(position, token) of the name occurring exactly once, or (None, None)."""
    counts = _Counter(slots)
    unique = [n for n in slots if counts[n] == 1]
    if len(unique) != 1:
        return (None, None)
    return (slots.index(unique[0]), unique[0])


@pytest.mark.parametrize("order", ["ABBA", "BABA"])
def test_abc_destroys_the_duplicate_structure(order):
    """Verbatim: "sentences no longer have a single plausible IO"."""
    slots = corrupt_slots("Alice", "Bob", order, "ABC", _random.Random(1), _NAMES)
    assert len(set(slots)) == 3, "ABC must use three mutually distinct names"
    assert _io_signal(slots) == (None, None), "ABC must leave no unique IO"


@pytest.mark.parametrize("order", ["ABBA", "BABA"])
def test_random_name_flip_keeps_position_and_randomises_token(order):
    """Figure 10 left: "same position signal, random token signal"."""
    a, b = "Alice", "Bob"
    clean_pos, clean_tok = _io_signal(_clean_slots(a, b, order))
    slots = corrupt_slots(a, b, order, "RANDOM_NAME_FLIP", _random.Random(1), _NAMES)
    pos, tok = _io_signal(slots)
    assert pos == clean_pos, "position signal must be preserved"
    assert tok not in (a, b), "token signal must be unrelated to the clean names"
    assert _Counter(slots).most_common(1)[0][1] == 2, "duplicate structure preserved"


@pytest.mark.parametrize("order", ["ABBA", "BABA"])
def test_io_s1_flip_inverts_position_and_keeps_token(order):
    """Verbatim: "correct token signals ... but inverted positional signals"."""
    a, b = "Alice", "Bob"
    clean_pos, clean_tok = _io_signal(_clean_slots(a, b, order))
    slots = corrupt_slots(a, b, order, "IO_S1_FLIP", _random.Random(1), _NAMES)
    pos, tok = _io_signal(slots)
    assert pos != clean_pos, "position signal must be inverted"
    assert tok == clean_tok, "token signal must be unchanged"
    assert set(slots) == {a, b}, "names must be held fixed"


@pytest.mark.parametrize("order", ["ABBA", "BABA"])
def test_io_from_s2_inverts_both_signals(order):
    """Verbatim: "both token signals and positional signals are inverted".

    Also checks the paper's own description of the result: "we make IO become
    the subject of the sentence and S the indirect object". The original IO must
    end up as the repeated name, and the original S as the single one.
    """
    a, b = "Alice", "Bob"
    clean_pos, clean_tok = _io_signal(_clean_slots(a, b, order))
    slots = corrupt_slots(a, b, order, "IO_FROM_S2", _random.Random(1), _NAMES)
    pos, tok = _io_signal(slots)
    assert pos != clean_pos, "position signal must be inverted"
    assert tok != clean_tok and tok in (a, b), "token signal must be inverted, not random"
    assert tok == b, "the original S must become the indirect object"
    assert _Counter(slots)[a] == 2, "the original IO must become the repeated subject"


@pytest.mark.parametrize("order", ["ABBA", "BABA"])
def test_the_three_structured_corruptions_occupy_distinct_signal_cells(order):
    """No two of them may land in the same cell of Wang's 3x2 table."""
    a, b = "Alice", "Bob"
    cells = set()
    for corr in ("RANDOM_NAME_FLIP", "IO_S1_FLIP", "IO_FROM_S2"):
        slots = corrupt_slots(a, b, order, corr, _random.Random(1), _NAMES)
        pos, tok = _io_signal(slots)
        clean_pos, clean_tok = _io_signal(_clean_slots(a, b, order))
        cells.add((pos == clean_pos, tok == clean_tok, tok in (a, b)))
    assert len(cells) == 3, f"corruptions collapsed onto the same signal cell: {cells}"


def test_corrupt_slots_rejects_an_unknown_construction():
    with pytest.raises(ValueError, match="unknown corruption"):
        corrupt_slots("Alice", "Bob", "ABBA", "SHUFFLE", _random.Random(1), _NAMES)


def test_generate_ioi_dataset_accepts_every_corruption_level():
    from p1.spec import CORRUPTION_LEVELS

    for corr in CORRUPTION_LEVELS:
        ds = generate_ioi_dataset(n_prompts=8, seed=0, corruption=corr)
        assert len(ds["prompts"]) == 8
        for p in ds["prompts"]:
            assert p["clean"] != p["corrupt"], f"{corr} produced an identity corruption"


def test_corruption_changes_the_dataset():
    """Four levels must not silently collapse to the same prompts."""
    from p1.spec import CORRUPTION_LEVELS

    seen = {}
    for corr in CORRUPTION_LEVELS:
        ds = generate_ioi_dataset(n_prompts=16, seed=0, corruption=corr)
        seen[corr] = tuple(p["corrupt"] for p in ds["prompts"])
    assert len(set(seen.values())) == len(CORRUPTION_LEVELS), (
        "two corruption levels produced identical corrupt prompts"
    )


# --- align_answer_tokenisation -------------------------------------------
#
# Fakes rather than real tokenizers, so these run in the torch-free environment.
# The behaviour being modelled is VERIFIED on the real thing, 2026-08-12: GPT-2
# yields one token per answer, Pythia-160m yields two until `add_bos_token` is
# cleared, and both report the flag as True beforehand.


class _FakeTokenizer:
    """Minimal stand-in. `add_bos_token` prepends a BOS id, as Pythia's does."""

    def __init__(self, add_bos_token: bool, honours_flag: bool = True,
                 width: int = 1):
        self.add_bos_token = add_bos_token
        self._honours_flag = honours_flag
        self._width = width

    def __call__(self, text: str):
        ids = list(range(self._width))
        if self.add_bos_token and self._honours_flag:
            ids = [0] + ids
        return {"input_ids": ids}


class _FakeModel:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer


def test_alignment_is_a_no_op_when_answers_are_already_single_tokens():
    """The GPT-2 case. Every confirmatory number depends on nothing happening.

    Note the flag is True here and is still not touched, because the condition
    is the measured width and not the flag.
    """
    from p1.prompts import align_answer_tokenisation

    tok = _FakeTokenizer(add_bos_token=True, honours_flag=False)
    info = align_answer_tokenisation(_FakeModel(tok), names=("John", "Mary"))

    assert info["changed"] is False
    assert info["max_width_before"] == 1
    assert tok.add_bos_token is True


def test_alignment_clears_the_flag_when_a_bos_is_being_prepended():
    """The Pythia case: two tokens becomes one, and the flag is cleared."""
    from p1.prompts import align_answer_tokenisation

    tok = _FakeTokenizer(add_bos_token=True)
    info = align_answer_tokenisation(_FakeModel(tok), names=("John", "Mary"))

    assert info["changed"] is True
    assert info["max_width_before"] == 2
    assert info["max_width_after"] == 1
    assert tok.add_bos_token is False


def test_alignment_raises_loudly_when_a_name_is_genuinely_multi_token():
    """A model whose tokenizer splits the names cannot run this dataset.

    It must say so here rather than 32,000 edges later as a bare AssertionError
    inside the instrument, which is what actually happened on 2026-08-12.
    """
    import pytest

    from p1.prompts import align_answer_tokenisation

    tok = _FakeTokenizer(add_bos_token=False, width=2)
    with pytest.raises(RuntimeError, match="exactly one token"):
        align_answer_tokenisation(_FakeModel(tok), names=("John", "Mary"))


def test_alignment_defaults_to_the_p1_name_set():
    from p1.prompts import EXAMPLE_NAMES, align_answer_tokenisation

    tok = _FakeTokenizer(add_bos_token=True)
    info = align_answer_tokenisation(_FakeModel(tok))
    assert info["n_names"] == len(EXAMPLE_NAMES)
