"""Prompt set generation: the P axis of the specification space.

Why this exists rather than using auto-circuit's bundled tasks
--------------------------------------------------------------

**VERIFIED 2026-08-03:** the `auto-circuit` PyPI wheel ships **zero** JSON files.
`Task._dataset_name` is resolved by `repo_path_to_abs_path`, which computes
`Path(__file__).parent.parent.parent / "datasets/..."`. On a pip install that
resolves inside `site-packages`, where no `datasets/` directory exists. The
bundled `IOI_COMPONENT_CIRCUIT_TASK` and friends therefore cannot load without
cloning the GitHub repository.

That is not a problem, because P1 needs its own prompt sets regardless: prompt
variant is a **grid dimension**, so the sets have to be P1-controlled and
seed-reproducible. This module generates them and writes auto-circuit's own JSON
schema, so the instrument is still consumed verbatim through its documented
public entry point `load_datasets_from_json`.

A documentation discrepancy worth knowing
-----------------------------------------

The `load_datasets_from_json` docstring prose says the file holds dictionaries
with keys `"clean_prompt"` and `"corrupt_prompt"`. The JSON schema block in the
same docstring says `"clean"` and `"corrupt"`, nested under a top-level
`"prompts"` list. **The schema block is what the loader parses.** This module
emits the schema-block form.

Provenance of the templates
---------------------------

The templates below are **P1's own**, written to the structure described in
arXiv:2407.08734 section 4: fifteen sentence templates involving two people,
where the token to predict is the indirect object, filled in ABBA or BABA order,
with an ABC corrupt distribution using three independently sampled names.

They are **not** transcribed from Wang et al. and must not be presented as such.
If exact replication of the published IOI dataset is wanted, take the templates
from that work's own release and record the provenance in the citation ledger.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

__all__ = [
    "Order",
    "EXAMPLE_TEMPLATES",
    "EXAMPLE_NAMES",
    "EXAMPLE_PLACES",
    "EXAMPLE_OBJECTS",
    "PromptPair",
    "generate_ioi_dataset",
    "write_dataset_json",
]

Order = Literal["ABBA", "BABA"]

#: P1's own templates. See the module docstring on provenance. Every template
#: must contain {A}, {B}, {PLACE}, {OBJECT} and end with the indirect-object slot
#: so the next token is the answer.
EXAMPLE_TEMPLATES: tuple[str, ...] = (
    "When {first} and {second} went to the {place}, {third} gave the {object} to",
    "Then {first} and {second} were at the {place}, and {third} handed the {object} to",
    "After {first} and {second} arrived at the {place}, {third} passed the {object} to",
)

EXAMPLE_NAMES: tuple[str, ...] = (
    "John", "Mary", "Tom", "Sarah", "James", "Anna",
    "Robert", "Emma", "David", "Laura", "Michael", "Sophie",
)

EXAMPLE_PLACES: tuple[str, ...] = ("store", "garden", "station", "office")
EXAMPLE_OBJECTS: tuple[str, ...] = ("book", "drink", "letter", "key")


@dataclass(frozen=True)
class PromptPair:
    """One clean/corrupt pair with its answers."""

    clean: str
    corrupt: str
    answers: tuple[str, ...]
    wrong_answers: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "clean": self.clean,
            "corrupt": self.corrupt,
            "answers": list(self.answers),
            "wrong_answers": list(self.wrong_answers),
        }


def _fill(template: str, a: str, b: str, third: str, place: str, obj: str, order: Order) -> str:
    first, second = (a, b) if order == "ABBA" else (b, a)
    return template.format(first=first, second=second, third=third, place=place, object=obj)


def _fill_slots(template: str, slots: tuple[str, str, str], place: str, obj: str) -> str:
    """Fill the three name slots directly, bypassing the order logic in `_fill`.

    The corruption transformations rearrange slots in ways that are not
    expressible as an (a, b, order) triple, so they are built at slot level.
    """
    s1, s2, s3 = slots
    return template.format(first=s1, second=s2, third=s3, place=place, object=obj)


def _clean_slots(a: str, b: str, order: Order) -> tuple[str, str, str]:
    """Clean slot layout. ABBA is (IO, S1, S2); BABA is (S1, IO, S2).

    In both, `a` occurs once and is the answer, and `b` occurs twice.
    """
    return (a, b, b) if order == "ABBA" else (b, a, b)


def _other_order(order: Order) -> Order:
    return "BABA" if order == "ABBA" else "ABBA"


def corrupt_slots(
    a: str,
    b: str,
    order: Order,
    corruption: str,
    rng: random.Random,
    names: Sequence[str],
) -> tuple[str, str, str]:
    """The four corruption constructions, all from arXiv:2211.00593.

    Derivations, so a future reader can check them rather than trust them.
    Wang et al.'s Figure 9 crosses a token signal in {original, random,
    S<->IO inverted} with a position signal in {original, inverted}. Token
    inversion is swapping the S and IO names; position inversion is the
    IO<->S1 flip, which on this template scheme is exactly the ABBA/BABA
    toggle with names held fixed.

    ``ABC`` (section 3). Three independently sampled, mutually distinct names,
    so the duplicate structure is destroyed and no IO is defined. Verbatim:
    "sentences no longer have a single plausible IO, but the grammatical
    structures from the pIOI templates are preserved."

    ``RANDOM_NAME_FLIP`` (appendix A). Clean layout, fresh names. Verbatim:
    "we keep the same position for all names ... each occurrence of a name in
    the original sentence is replaced by the same random name."
    Token signal random, position signal original.

    ``IO_S1_FLIP`` (appendix A). Names held, order toggled. Verbatim: "we swap
    the position of IO and S1 ... correct token signals ... but inverted
    positional signals."

    ``IO_FROM_S2`` (appendix A). Names swapped AND order toggled, which is both
    transformations composed, matching "both token signals and positional
    signals are inverted". On ABBA this maps (a, b, b) to (a, b, a), in which
    `a`, the original IO, is now the repeated subject and `b`, the original S,
    appears once as the indirect object. That is the paper's own description:
    "we make IO become the subject of the sentence and S the indirect object."

    Only ``ABC`` leaves the corrupt prompt without a well-defined IO. The other
    three are valid IOI sentences. This does not affect any metric: the corrupt
    prompt supplies ablation activations only, and faithfulness is scored on the
    clean prompt against the shared answers.
    """
    if corruption == "ABC":
        c1, c2, c3 = rng.sample(list(names), 3)
        return (c1, c2, c3)
    if corruption == "RANDOM_NAME_FLIP":
        pool = [n for n in names if n not in (a, b)]
        if len(pool) < 2:
            raise ValueError(
                f"RANDOM_NAME_FLIP needs 2 names distinct from {a!r} and {b!r}; "
                f"only {len(pool)} available"
            )
        a2, b2 = rng.sample(pool, 2)
        return _clean_slots(a2, b2, order)
    if corruption == "IO_S1_FLIP":
        return _clean_slots(a, b, _other_order(order))
    if corruption == "IO_FROM_S2":
        return _clean_slots(b, a, _other_order(order))
    raise ValueError(
        f"unknown corruption {corruption!r}; expected one of "
        f"ABC, RANDOM_NAME_FLIP, IO_S1_FLIP, IO_FROM_S2"
    )


def generate_ioi_dataset(
    n_prompts: int,
    seed: int,
    order: Order = "ABBA",
    corruption: str = "ABC",
    templates: Sequence[str] = EXAMPLE_TEMPLATES,
    names: Sequence[str] = EXAMPLE_NAMES,
    places: Sequence[str] = EXAMPLE_PLACES,
    objects: Sequence[str] = EXAMPLE_OBJECTS,
) -> dict:
    """Build an auto-circuit dataset dict. Deterministic given `seed`.

    Clean prompts follow the IOI structure: two names appear, one of them twice,
    and the answer is the name that appeared once, the indirect object.

    Corrupt prompts follow one of the four constructions in `corrupt_slots`, all
    taken from arXiv:2211.00593. `ABC` is the default and the de facto standard:
    three independently sampled, mutually distinct names, so no correct
    completion is defined. The other three preserve the duplicate structure and
    are valid IOI sentences; see `corrupt_slots` for the derivation of each and
    for why that does not affect any metric.

    `seq_labels` is emitted because auto-circuit accepts it and because it is the
    natural source of the segment labels that `phi_affected` reads. Keeping the
    two in one place stops them drifting apart.
    """
    if n_prompts < 1:
        raise ValueError(f"n_prompts must be at least 1, got {n_prompts}")
    if order not in ("ABBA", "BABA"):
        raise ValueError(f"order must be ABBA or BABA, got {order!r}")
    if len(names) < 4:
        raise ValueError(f"need at least 4 distinct names, got {len(names)}")
    if len(set(names)) != len(names):
        raise ValueError("names must be distinct")
    if not templates:
        raise ValueError("templates must be non-empty")
    for t in templates:
        for slot in ("{first}", "{second}", "{third}", "{place}", "{object}"):
            if slot not in t:
                raise ValueError(f"template missing {slot}: {t!r}")

    rng = random.Random(seed)
    pairs: list[PromptPair] = []
    for _ in range(n_prompts):
        template = rng.choice(templates)
        place = rng.choice(places)
        obj = rng.choice(objects)

        a, b = rng.sample(list(names), 2)
        # Clean: A and B appear, B repeats as the subject, so A is the answer.
        clean = _fill_slots(template, _clean_slots(a, b, order), place, obj)

        corrupt = _fill_slots(
            template, corrupt_slots(a, b, order, corruption, rng, names), place, obj
        )

        pairs.append(
            PromptPair(
                clean=clean,
                corrupt=corrupt,
                answers=(" " + a,),
                wrong_answers=(" " + b,),
            )
        )

    return {
        "seq_labels": [
            "prefix", "name_first", "name_second", "place", "subject", "object", "final",
        ],
        "prompts": [p.as_dict() for p in pairs],
    }


def write_dataset_json(dataset: dict, path: Path) -> Path:
    """Write the dataset, sorted and indented so diffs are readable."""
    if "prompts" not in dataset:
        raise ValueError("dataset must contain a 'prompts' key")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dataset, indent=2, sort_keys=True), encoding="utf-8")
    return path
