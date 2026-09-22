#!/usr/bin/env python3
"""Export the per-specification records so the analysis runs from a clone.

Why this exists
---------------

`results/sweep` holds 389 MB of raw per-cell output and is correctly gitignored.
Only the 1,540 `manifest.json` files are tracked. But **every** analysis entry
point reaches the raw output through `analyse.load_records`:

    analysis/verify_all_claims.py        the 36 checks
    analysis/emit_tables.py              every table in the paper
    analysis/check_manuscript_numbers.py the number audit
    analysis/figure1.py                  the specification curve

So from a clean clone a reader could run the test suite and nothing else. For a
paper whose argument is that interpretability evidence is not reproducible
enough to file, that was the wrong gap to leave open.

This script writes what those four scripts read, and nothing more, to a single
committed file: the records `load_records` returns, plus the two per-cell facts
`sweep_facts` supplies. Measured 2026-09-21: 2.78 MB of JSON compresses to
0.14 MB, because the claim field takes only 38 distinct strings across 7,561
specifications and is dictionary-encoded here.

It deliberately does **not** carry the per-cell `top_edges` ranking, which is
the bulk of the raw output. `tab:bins` needs only the (layer band, component
fraction) pair derived from it, so the export cuts there and the table still
recomputes every bin edge it reports.

**This is a derived artefact, not a new source of truth.** It is produced from
`results/sweep` by this script and must be regenerated whenever the sweep is.
`analyse.load_records` prefers the raw output whenever it is present and falls
back to this file only when it is not, so an author with the raw data never
reads it.

Run:
    python3 analysis/export_records.py
"""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

OUT = REPO / "results" / "analysis" / "specifications.json.gz"
SCHEMA = 2


def build(results: Path, config: Path) -> dict:
    from analyse import load_records, sweep_facts

    axes = yaml.safe_load(config.read_text())["axes"]
    records, meta = load_records(results, axes)
    facts = sweep_facts(results)

    # Dictionary-encode the claim strings. 38 distinct values over 7,561
    # specifications, each appearing in six (granularity, addressee) slots.
    strings: list[str] = []
    index: dict[str, int] = {}

    def code(s: str) -> int:
        if s not in index:
            index[s] = len(strings)
            strings.append(s)
        return index[s]

    out = []
    for r in records:
        out.append(
            {
                **{k: v for k, v in r.items() if k != "claims"},
                "claims": {
                    g: {m: code(s) for m, s in maps.items()}
                    for g, maps in r["claims"].items()
                },
            }
        )

    # `discards` is a Counter keyed by (axis, level) tuples, which JSON cannot
    # represent as keys. Levels are not all strings: seeds are ints and
    # thresholds floats, so a string join loses the type. Each key is stored as
    # a JSON-encoded list, which round-trips the types exactly.
    audit = dict(meta)
    if "discards" in audit:
        audit["discards"] = {
            json.dumps(list(k)): v
            for k, v in sorted(audit["discards"].items(), key=lambda kv: str(kv[0]))
        }

    # `tab:bins` re-bins a component fraction that is itself computed from the
    # per-cell `top_edges` list. That list is far too large to commit, so the
    # export cuts below it: the (band, fraction) pair is banked and every bin
    # edge in the table is still recomputed from it at table time.
    band_index: dict[str, int] = {}
    band_names: list[str] = []
    bin_pairs = []
    for band, fraction in facts["bin_pairs"]:
        if band not in band_index:
            band_index[band] = len(band_names)
            band_names.append(band)
        bin_pairs.append([band_index[band], fraction])

    return {
        "schema": SCHEMA,
        "source": f"{results.relative_to(REPO)}, derived artefact",
        "n_records": len(out),
        "audit": audit,
        "claim_strings": strings,
        "records": out,
        "derived": {
            "n_edges": {"value": facts["n_edges"], "cells": facts["n_cells"]},
            "bands": band_names,
            "bin_pairs": bin_pairs,
        },
    }


def main() -> int:
    payload = build(REPO / "results" / "sweep", REPO / "configs" / "sweep.yaml")
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(gzip.compress(blob, 9))
    print(f"records        {payload['n_records']:,}")
    print(f"claim strings  {len(payload['claim_strings'])}")
    print(f"bin pairs      {len(payload['derived']['bin_pairs']):,}")
    print(f"n_edges        {payload['derived']['n_edges']['value']:,} "
          f"across {payload['derived']['n_edges']['cells']:,} cells")
    print(f"uncompressed   {len(blob) / 1e6:.2f} MB")
    print(f"written        {OUT.relative_to(REPO)}  {OUT.stat().st_size / 1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
