"""Run manifests: the machinery behind "every number is traceable".

Standing rule 8 says every reported figure must be reproducible from a config, a
seed, and an environment hash. That is easy to write in a protocol and easy to
lose in practice, because the losing looks like nothing at all: a results file
with no record of which library versions produced it.

A `Manifest` is written next to every result. It records what was run, on what,
with which seeds, how long it took, and what the environment was, and it is
content-addressed so two manifests can be compared byte for byte.

No torch import. This module must work on the analysis machine as well as the
sweep machine, and it must never be the reason an environment cannot be
reconstructed.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

__all__ = [
    "PACKAGES_OF_RECORD",
    "Manifest",
    "canonical_hash",
    "environment_fingerprint",
    "environment_hash",
    "git_commit",
]

#: Packages whose versions materially change results. Anything here that is
#: missing is recorded as missing rather than skipped, because "torch absent" is
#: itself a fact about the run that produced a number.
PACKAGES_OF_RECORD: tuple[str, ...] = (
    "auto-circuit",
    "torch",
    "transformer-lens",
    "numpy",
    "scipy",
    "statsmodels",
)


def _version(pkg: str) -> str:
    try:
        from importlib.metadata import version

        return version(pkg)
    except Exception:  # noqa: BLE001
        # Deliberately broad. This records provenance for a run that may have
        # cost an hour of GPU time; it must never be the thing that kills it.
        # A package that cannot be resolved for any reason is reported as
        # ABSENT, which is a fact about the environment and is what the
        # fingerprint is for. Narrowing this to PackageNotFoundError would let
        # an importlib failure propagate into the sweep.
        return "ABSENT"


def environment_fingerprint(
    packages: tuple[str, ...] = PACKAGES_OF_RECORD,
) -> dict[str, str]:
    """Everything about the machine that could change a number.

    Deliberately excludes wall-clock time, hostname, and working directory. Two
    runs on equivalent machines must fingerprint identically, otherwise the hash
    is a timestamp with extra steps and cannot be used to assert reproducibility.
    """
    fp = {
        "python": platform.python_version(),
        "platform": platform.platform(terse=True),
        "machine": platform.machine(),
    }
    for pkg in packages:
        fp[f"pkg:{pkg}"] = _version(pkg)
    return fp


def canonical_hash(obj: Any) -> str:
    """SHA-256 over a canonical JSON encoding. 16 hex characters.

    Not Python's `hash`, which is salted per process. See `p1.spec.spec_id` for
    the same reasoning and the same failure mode being guarded against.
    """
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def environment_hash(packages: tuple[str, ...] = PACKAGES_OF_RECORD) -> str:
    return canonical_hash(environment_fingerprint(packages))


def git_commit(repo: Path | None = None) -> str:
    """Current commit, with a `-dirty` suffix if the tree has uncommitted changes.

    The suffix matters. A number produced from a dirty tree is not reproducible
    from a commit hash, and recording the bare hash would assert otherwise.
    Returns "UNKNOWN" when git is unavailable rather than raising, because a
    manifest that fails to write is worse than one with a gap in it.
    """
    cwd = str(repo) if repo else None
    try:
        h = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=cwd, timeout=10, check=False,
        )
        if h.returncode != 0:
            return "UNKNOWN"
        commit = h.stdout.strip()
        st = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=cwd, timeout=10, check=False,
        )
        return commit + ("-dirty" if st.stdout.strip() else "")
    except Exception:  # noqa: BLE001
        # Deliberately broad, for the same reason as `_version`. Every one of
        # the 1,540 banked manifests carries UNKNOWN here, because the sweep ran
        # in Colab from an unpacked tarball with no `.git`. That is recorded as
        # a design delta rather than repaired: the environment fingerprint and
        # the config hash, not the commit, are what tie a result to its inputs.
        return "UNKNOWN"


@dataclass(frozen=True)
class Manifest:
    """One record per result file. Written even when the run fails."""

    kind: str
    spec_id: str
    config: Mapping[str, Any]
    seeds: Mapping[str, int]
    timings_s: Mapping[str, float] = field(default_factory=dict)
    peak_rss_mb: float | None = None
    #: Peak CUDA memory in MB, `None` on CPU. Distinct from `peak_rss_mb`, which
    #: is HOST resident set size and says nothing about whether a run fits in
    #: VRAM. Conflating the two is how a sweep gets sized for a GPU it will OOM
    #: on: the T4 measurement on 2026-08-05 reported 2.8 GB RSS on a 15 GB card
    #: while the actual device usage was unmeasured.
    peak_vram_mb: float | None = None
    notes: str = ""
    status: str = "ok"
    environment: Mapping[str, str] = field(default_factory=environment_fingerprint)
    commit: str = field(default_factory=git_commit)
    created_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __post_init__(self) -> None:
        if self.status not in {"ok", "failed", "discarded"}:
            raise ValueError(
                f"status must be ok, failed, or discarded, got {self.status!r}"
            )
        if not self.kind:
            raise ValueError("kind must be non-empty")

    @property
    def environment_hash(self) -> str:
        return canonical_hash(dict(self.environment))

    @property
    def reproducibility_key(self) -> tuple[str, str, str]:
        """The triple standing rule 8 requires: config, seeds, environment."""
        return (
            canonical_hash(dict(self.config)),
            canonical_hash(dict(self.seeds)),
            self.environment_hash,
        )

    def is_reproducible_from_commit(self) -> bool:
        """False if the tree was dirty or git was unavailable when this was written."""
        return self.commit not in {"UNKNOWN", ""} and not self.commit.endswith("-dirty")

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2, default=str)

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path

    @classmethod
    def read(cls, path: Path) -> "Manifest":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))
