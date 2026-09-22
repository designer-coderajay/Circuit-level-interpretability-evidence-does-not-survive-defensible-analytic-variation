"""The paper's numbers must be reproducible from the committed tree alone.

`results/sweep` is 389 MB and gitignored, so a clone carries the 1,540 manifests
and no per-cell output. On 2026-09-21 a clean-clone run showed that **all four**
analysis entry points failed there: every one of them read `results/sweep`
directly, so only the test suite ran for anyone but the author. For a paper
arguing that interpretability evidence is not reproducible enough to file, that
was the wrong gap to leave open.

The fix is `results/analysis/specifications.json.gz`, a 0.14 MB derived export,
plus two raw-preferred accessors in `scripts/analyse.py`. These tests defend
both halves of that fix:

  1. no analysis script may reach per-cell output except through those two
     accessors, since a new direct read would silently reintroduce the gap
  2. the committed export must be self-consistent and must actually be what the
     accessors return when no raw output is present

What these tests do not check is numerical agreement between the export and the
raw sweep. That needs the 389 MB and cannot run in CI. It was verified by
running all four scripts against both sources on 2026-09-21: every stdout was
identical and the figure PNG was byte-identical. See `RESEARCH_LOG.md`.
"""

from __future__ import annotations

import ast
import gzip
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ANALYSIS = sorted((REPO / "analysis").glob("*.py"))
EXPORT = REPO / "results" / "analysis" / "specifications.json.gz"

sys.path.insert(0, str(REPO / "scripts"))

#: The only two functions permitted to touch per-cell sweep output. Both prefer
#: the raw directory and fall back to the export, so a script that goes through
#: either one works from a clone. Anything else that opens a `result.json` or a
#: `.npz` does not.
ACCESSORS = ("load_records", "sweep_facts")

#: Naming a per-cell artefact in an analysis script means reading it directly.
#: `export_records.py` is exempt: producing the export is its entire purpose,
#: and it is never on the path a reader runs.
FORBIDDEN = ("result.json", ".npz", "top_edges")


def _string_constants(tree: ast.AST) -> list[str]:
    return [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


@pytest.mark.parametrize("path", ANALYSIS, ids=lambda p: p.name)
def test_no_analysis_script_reads_per_cell_output_directly(path: Path) -> None:
    """Per-cell output is reachable only through the two fallback-aware accessors."""
    if path.name == "export_records.py":
        pytest.skip("produces the export; reads raw output by definition")

    tree = ast.parse(path.read_text())
    found = sorted({s for s in _string_constants(tree) for f in FORBIDDEN if f in s})
    assert not found, (
        f"{path.name} names per-cell sweep artefacts {found}. Read them through "
        f"{' or '.join(ACCESSORS)} in scripts/analyse.py instead, so the script "
        f"still runs from a clone with no results/sweep."
    )


def test_export_is_committed() -> None:
    """A clone must carry the export, or nothing downstream runs.

    Existing on disk is not enough, and checking only that is how this nearly
    shipped broken. `.gitignore` excludes `results/**` and re-admits
    `results/analysis/*.json`, which does **not** match `.json.gz`. The export
    was therefore ignored: `git add -A` skipped it without a word, the commit
    looked clean, and every clone would have failed on the first analysis
    script. So ask git, not the filesystem.
    """
    assert EXPORT.exists(), f"{EXPORT.relative_to(REPO)} is missing"

    rel = str(EXPORT.relative_to(REPO))
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", rel],
        cwd=REPO, capture_output=True, timeout=30, check=False,
    )
    if ignored.returncode == 128:
        pytest.skip("git unavailable; cannot check tracking")
    assert ignored.returncode == 1, (
        f"{rel} is matched by .gitignore, so it will never be committed and no "
        f"clone will be able to run the analysis. Add a negation for it."
    )


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(gzip.decompress(EXPORT.read_bytes()))


def test_export_is_internally_consistent(payload: dict) -> None:
    assert payload["schema"] == 2
    records = payload["records"]
    assert payload["n_records"] == len(records)

    # Claim codes are indices into the string table, in range and all used.
    strings = payload["claim_strings"]
    used = {i for r in records for maps in r["claims"].values() for i in maps.values()}
    assert used <= set(range(len(strings)))
    assert used == set(range(len(strings))), "string table has entries no record refers to"

    derived = payload["derived"]
    assert derived["n_edges"]["value"] == 32491
    assert derived["n_edges"]["cells"] > 0

    # One (band, fraction) pair per kept specification, which is what the
    # bin-sensitivity table re-bins.
    pairs = derived["bin_pairs"]
    assert len(pairs) == len(records)
    bands = derived["bands"]
    for band, fraction in pairs:
        assert 0 <= band < len(bands)
        assert 0.0 < fraction <= 1.0


def test_accessors_return_the_export_when_no_raw_output_exists(tmp_path: Path, payload: dict) -> None:
    """The fallback fires on an absent directory and reproduces the export."""
    from analyse import AXES, load_records, sweep_facts

    absent = tmp_path / "no-such-sweep"

    facts = sweep_facts(absent)
    assert facts["n_edges"] == payload["derived"]["n_edges"]["value"]
    assert facts["n_cells"] == payload["derived"]["n_edges"]["cells"]
    assert len(facts["bin_pairs"]) == len(payload["derived"]["bin_pairs"])

    records, meta = load_records(absent, axes={})
    assert len(records) == payload["n_records"]
    assert meta["audit"]["specifications_with_claims"] == len(records)
    for axis in AXES:
        assert axis in records[0], f"record is missing the {axis} axis"


def test_fallback_does_not_fire_when_raw_output_is_present(tmp_path: Path) -> None:
    """Raw output always wins, so an author with the data never reads the export.

    Built as a one-cell sweep whose single value differs from the committed
    export, so reading the export instead of the directory is detectable.
    """
    from analyse import sweep_facts

    cell = tmp_path / "sweep" / "abc123"
    cell.mkdir(parents=True)
    (cell / "result.json").write_text(
        json.dumps({"n_edges": 7, "top_edges": [], "specifications": {}})
    )

    facts = sweep_facts(tmp_path / "sweep")
    assert facts["n_edges"] == 7, "read the committed export instead of the raw directory"
    assert facts["n_cells"] == 1
    assert facts["bin_pairs"] == []


def test_disagreeing_cells_raise_rather_than_sampling_one(tmp_path: Path) -> None:
    """The edge count is checked across every cell, not sampled from the first.

    Before 2026-09-21 this check opened one `result.json` and trusted it. A
    single cell instrumented against a different graph would have passed.
    """
    from analyse import sweep_facts

    root = tmp_path / "sweep"
    for name, n in (("a", 32491), ("b", 32347)):
        cell = root / name
        cell.mkdir(parents=True)
        (cell / "result.json").write_text(
            json.dumps({"n_edges": n, "top_edges": [], "specifications": {}})
        )

    with pytest.raises(ValueError, match="disagree on the instrumented edge count"):
        sweep_facts(root)
