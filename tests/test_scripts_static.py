"""Static checks over `scripts/`, which the test suite cannot import.

Every entry point in `scripts/` imports torch, so none of it is reachable from
the torch-free suite. On 2026-08-13 that let a dangling variable reference ship:
`attention_rows_for` was edited to build its tokens differently, and a later line
still referred to `text`, a name the edit had deleted. It ran a full minute of
GPU work per cell before raising `NameError`.

These tests parse the source instead of importing it. They cannot check
behaviour, and they are not a substitute for the seam smoke test that still does
not exist. They catch the one class of defect that costs a GPU session to
discover and a linter to prevent.
"""

from __future__ import annotations

import ast
import builtins
from pathlib import Path

import pytest

SCRIPTS = sorted((Path(__file__).resolve().parents[1] / "scripts").glob("*.py"))

#: Module dunders are always bound at import time and are not in `dir(builtins)`.
MODULE_DUNDERS = frozenset(
    {"__file__", "__name__", "__doc__", "__spec__", "__package__", "__loader__"}
)


def _module_level_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(a.asname or a.name.split(".")[0] for a in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                names.update(n.id for n in ast.walk(t) if isinstance(n, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _unresolved(fn: ast.AST, module_names: set[str]) -> list[str]:
    bound, used = set(module_names), set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name):
            (bound if isinstance(node.ctx, ast.Store) else used).add(node.id)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            bound.update(a.asname or a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # A nested def binds its own name in the enclosing scope. Missing
            # this was the checker's own first false positive.
            bound.add(node.name)
        elif isinstance(node, ast.Global) or isinstance(node, ast.Nonlocal):
            bound.update(node.names)
        elif isinstance(node, (ast.comprehension,)):
            bound.update(n.id for n in ast.walk(node.target)
                         if isinstance(n, ast.Name))
    return sorted(used - bound - set(dir(builtins)) - MODULE_DUNDERS)


@pytest.mark.parametrize("path", SCRIPTS, ids=lambda p: p.name)
def test_no_unresolved_names_in_scripts(path: Path):
    """Every name read in a function is bound somewhere reachable.

    Conservative by construction: module-level names count as bound, so this
    cannot flag a legitimate global. It flags exactly what it caught, a name
    that exists nowhere.
    """
    tree = ast.parse(path.read_text(), filename=str(path))
    module_names = _module_level_names(tree)

    # Top-level functions only. A nested function is walked as part of its
    # parent, so its closure variables are correctly seen as bound; checking it
    # again in isolation reports every closure variable as unresolved, which was
    # the checker's second false positive.
    problems: dict[str, list[str]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bad = _unresolved(node, module_names)
            if bad:
                problems[node.name] = bad

    assert not problems, f"{path.name}: unresolved names {problems}"


def test_the_check_would_have_caught_the_2026_08_13_defect():
    """A regression test for the test, using the actual shape of the bug."""
    src = (
        "def f(model, prompt):\n"
        "    ids = tok(prompt)\n"
        "    return model.to_tokens(text)\n"   # `text` was deleted by an edit
    )
    tree = ast.parse(src)
    fn = tree.body[0]
    bad = _unresolved(fn, _module_level_names(tree))
    assert "text" in bad
