"""Constants the manuscripts assert about this repository must stay true.

A paper claiming "the test suite is N tests" states a fact about the tree it
ships with. That number goes stale the moment anyone adds a test, and nothing
catches it, because the number audit in `analysis/check_manuscript_numbers.py`
can only check a manuscript figure against a source value it was given. If the
source value is itself a hand-typed constant, the audit confirms the paper
agrees with a stale constant and reports a pass.

That is exactly what happened: `paper/manuscript.md` claimed 319 tests through
a run that reported 157 of 157 numbers matched, because 319 was registered as a
source value. The registered constant is now checked against the real count
here, which closes the loop.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "analysis" / "check_manuscript_numbers.py"


def _declared_n_tests() -> int:
    """`N_TESTS` as written in the checker, read without importing it.

    Importing would run the whole audit, which needs the analysis JSON and the
    sweep export. Reading the assignment keeps this test cheap and independent.
    """
    match = re.search(r"^N_TESTS\s*=\s*(\d+)", CHECKER.read_text(), re.M)
    assert match, f"no N_TESTS assignment in {CHECKER.relative_to(REPO)}"
    return int(match.group(1))


def _collected() -> int:
    """Tests pytest collects under `tests/`, counted by pytest itself.

    `--collect-only` does not execute anything, so this does not recurse.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q",
         "-p", "no:cacheprovider"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    counts = re.findall(r"^tests/\S+\.py: (\d+)$", proc.stdout, re.M)
    assert counts, f"could not parse pytest collection output:\n{proc.stdout[-2000:]}"
    return sum(int(c) for c in counts)


def test_declared_test_count_matches_reality() -> None:
    declared, actual = _declared_n_tests(), _collected()
    assert declared == actual, (
        f"N_TESTS in {CHECKER.relative_to(REPO)} says {declared}, pytest collects "
        f"{actual}. Set it to {actual}, then re-run "
        f"`python3 analysis/check_manuscript_numbers.py` and update any manuscript "
        f"that states the old number."
    )
