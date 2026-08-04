"""Tests for the run manifest.

The manifest is the mechanism behind standing rule 8: every reported number
traceable to a config, a seed, and an environment hash. Two properties matter
most and are both tested here. The environment fingerprint must exclude anything
that varies between equivalent runs, or the hash is a timestamp and cannot
support a reproducibility claim. And a dirty working tree must be visible in the
commit field, because recording a bare commit hash for a number produced from
uncommitted code asserts something false.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from p1.manifest import (
    PACKAGES_OF_RECORD,
    Manifest,
    canonical_hash,
    environment_fingerprint,
    environment_hash,
)


def make(**kw) -> Manifest:
    base = dict(
        kind="smoke",
        spec_id="e1fead883f6cdea2",
        config={"model": "gpt2", "task": "ioi"},
        seeds={"data": 42, "torch": 0},
    )
    base.update(kw)
    return Manifest(**base)


# --------------------------------------------------------------------------
# Environment fingerprint
# --------------------------------------------------------------------------


def test_fingerprint_is_stable_across_calls():
    """If this drifts, the environment hash is noise and rule 8 is unmet."""
    assert environment_fingerprint() == environment_fingerprint()
    assert environment_hash() == environment_hash()


def test_fingerprint_excludes_time_and_host():
    fp = environment_fingerprint()
    joined = " ".join(fp.keys()).lower()
    for forbidden in ("time", "date", "host", "cwd", "user", "pid"):
        assert forbidden not in joined, f"fingerprint leaks {forbidden}"


def test_every_package_of_record_appears_even_when_absent():
    """A missing package is a fact about the run, not a gap to be skipped."""
    fp = environment_fingerprint()
    for pkg in PACKAGES_OF_RECORD:
        assert f"pkg:{pkg}" in fp


def test_absent_package_is_recorded_as_absent_not_omitted():
    fp = environment_fingerprint(("definitely-not-a-real-package-xyz",))
    assert fp["pkg:definitely-not-a-real-package-xyz"] == "ABSENT"


def test_fingerprint_change_changes_the_hash():
    a = canonical_hash(environment_fingerprint())
    b = canonical_hash({**environment_fingerprint(), "pkg:torch": "999.0.0"})
    assert a != b


# --------------------------------------------------------------------------
# Canonical hashing
# --------------------------------------------------------------------------


def test_canonical_hash_is_key_order_independent():
    assert canonical_hash({"a": 1, "b": 2}) == canonical_hash({"b": 2, "a": 1})


def test_canonical_hash_distinguishes_values():
    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})


def test_canonical_hash_is_sixteen_hex_chars():
    h = canonical_hash({"a": 1})
    assert len(h) == 16 and all(c in "0123456789abcdef" for c in h)


# --------------------------------------------------------------------------
# The reproducibility triple
# --------------------------------------------------------------------------


def test_reproducibility_key_has_three_parts():
    assert len(make().reproducibility_key) == 3


def test_same_inputs_give_the_same_key():
    assert make().reproducibility_key == make().reproducibility_key


@pytest.mark.parametrize(
    "change",
    [{"config": {"model": "gpt2-medium", "task": "ioi"}}, {"seeds": {"data": 1, "torch": 0}}],
)
def test_changing_config_or_seeds_changes_the_key(change):
    assert make().reproducibility_key != make(**change).reproducibility_key


def test_timings_do_not_affect_the_reproducibility_key():
    """Wall clock is a property of the machine, not of the result."""
    a = make(timings_s={"discovery": 12.0})
    b = make(timings_s={"discovery": 480.0})
    assert a.reproducibility_key == b.reproducibility_key


# --------------------------------------------------------------------------
# Dirty trees must be visible
# --------------------------------------------------------------------------


def test_dirty_commit_is_not_reproducible():
    assert make(commit="abc123-dirty").is_reproducible_from_commit() is False


def test_unknown_commit_is_not_reproducible():
    assert make(commit="UNKNOWN").is_reproducible_from_commit() is False
    assert make(commit="").is_reproducible_from_commit() is False


def test_clean_commit_is_reproducible():
    assert make(commit="a" * 40).is_reproducible_from_commit() is True


# --------------------------------------------------------------------------
# Failure is recorded, not silently dropped
# --------------------------------------------------------------------------


def test_failed_and_discarded_are_valid_statuses():
    """Discard rates must be reportable, so discards need a manifest too."""
    for s in ("ok", "failed", "discarded"):
        assert make(status=s).status == s


def test_invalid_status_is_rejected():
    with pytest.raises(ValueError, match="status"):
        make(status="probably_fine")


def test_empty_kind_is_rejected():
    with pytest.raises(ValueError, match="kind"):
        make(kind="")


# --------------------------------------------------------------------------
# Round trip
# --------------------------------------------------------------------------


def test_write_then_read_round_trips(tmp_path: Path):
    m = make(timings_s={"discovery": 3.5}, peak_rss_mb=812.0, notes="cpu run")
    p = m.write(tmp_path / "nested" / "manifest.json")
    assert p.exists()
    back = Manifest.read(p)
    assert back.reproducibility_key == m.reproducibility_key
    assert back.timings_s["discovery"] == 3.5
    assert back.peak_rss_mb == 812.0


def test_written_json_is_valid_and_sorted(tmp_path: Path):
    p = make().write(tmp_path / "m.json")
    text = p.read_text()
    data = json.loads(text)
    assert data["kind"] == "smoke"
    keys = [k for k in data]
    assert keys == sorted(keys), "manifest keys must be sorted for byte-comparability"


def test_two_manifests_of_the_same_run_are_byte_identical_except_timestamp(tmp_path):
    a = json.loads(make(created_utc="X").write(tmp_path / "a.json").read_text())
    b = json.loads(make(created_utc="X").write(tmp_path / "b.json").read_text())
    assert a == b
