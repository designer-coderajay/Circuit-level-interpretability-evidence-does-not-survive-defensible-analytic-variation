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


def generate_ioi_dataset(
    n_prompts: int,
    seed: int,
    order: Order = "ABBA",
    templates: Sequence[str] = EXAMPLE_TEMPLATES,
    names: Sequence[str] = EXAMPLE_NAMES,
    places: Sequence[str] = EXAMPLE_PLACES,
    objects: Sequence[str] = EXAMPLE_OBJECTS,
) -> dict:
    """Build an auto-circuit dataset dict. Deterministic given `seed`.

    Clean prompts follow the IOI structure: two names appear, one of them twice,
    and the answer is the name that appeared once, the indirect object.

    Corrupt prompts follow the ABC distribution: three **independently sampled,
    mutually distinct** names, so no correct completion is defined. That is the
    point of the corrupt distribution and a test asserts the distinctness.

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
        clean = _fill(template, a, b, b, place, obj, order)

        # Corrupt: three independent, mutually distinct names. No correct answer.
        c1, c2, c3 = rng.sample(list(names), 3)
        corrupt = _fill(template, c1, c2, c3, place, obj, order)

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
