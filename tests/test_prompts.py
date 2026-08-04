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
    """The schema block, not the prose, is what load_datasets_from_json parses."""
    ds = generate_ioi_dataset(5, seed=0)
    assert "prompts" in ds
    assert "seq_labels" in ds


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
