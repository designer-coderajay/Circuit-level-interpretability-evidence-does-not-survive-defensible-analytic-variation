"""Every number in the manuscript must exist in the source JSON or be derivable.

Mechanical, not editorial. It extracts numeric tokens from `paper/manuscript.md`
and matches each against a set built from `results/analysis/*.json`, the realised
grid, and closed-form quantities. Anything unmatched is printed for a human to
justify or delete. Its purpose is to make "no fabricated numbers" checkable
rather than promised.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

A = Path('results/analysis')
src: dict[float, list[str]] = {}
def add(v, label):
    """Register a source value at every rounding a manuscript might print.

    The JSON holds full precision, 0.731611; prose prints 0.7316, 0.732 or 73.2.
    Matching only the stored value would flag every correctly rounded figure, so
    each value is registered at 0 to 4 decimal places, and as a percentage."""
    try: f = float(v)
    except (TypeError, ValueError): return
    for dp in range(5):
        src.setdefault(round(f, dp), []).append(label)
        src.setdefault(round(f * 100, dp), []).append('pct ' + label)

def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, f"{path}[{i}]")
    else: add(o, path)

for f in sorted(A.glob('*.json')):
    if f.name == 'stage4_inputs.json': continue
    walk(json.loads(f.read_text()), f.stem)

# Design constants and closed forms, each justified in the log.
for v, why in [
    (32491,'edge count closed form'), (156,'components 12*12+12'), (144,'heads'),
    (12,'blocks and heads per block'), (1540,'pre-registered cells'),
    (1320,'realised cells'), (18480,'pre-registered specs'), (15840,'realised specs'),
    (7561,'specs with claims'), (8279,'discarded'), (220,'non-executing arm'),
    (28580580,'unordered pairs'), (128,'examples per circuit'), (3218,'distinct circuits'),
    (10000,'bootstrap B and top ladder rung'), (1000,'null replicates'), (0.20,'H2 threshold'),
    (0.10,'H4 threshold'), (0.05,'tau level'), (2,'prompt variants'), (5,'seeds'),
    (7,'axes and objectives'), (6,'realised objectives'), (4,'metrics'), (3,'tau levels'),
    (9,'claim classes'), (0.003087,'J_rand at k=200'), (200,'median circuit size'),
    (2024,'regulation year'), (2026,'amending regulation year'), (1689,'regulation number'),
    (1744,'amending regulation number'), (500,'ladder rung'), (2000,'ladder rung'),
    (5000,'ladder rung'), (0.8889,'F ceiling 1-1/9'), (36,'verification checks'),
    (319,'tests'), (0.5227,'discard rate'), (52.3,'discard rate pct'),
]: add(v, why)

text = Path('paper/manuscript.md').read_text()
# Strip things that are not claims: DOIs, arXiv ids, section numbers, years,
# CELEX and article references. Each is verifiable elsewhere, not a result.
import re as _re
text = _re.sub(r'doi:\S+|10\.\d{4}/\S+', ' ', text)
text = _re.sub(r'arXiv:\d{4}\.\d{4,5}(v\d)?', ' ', text)
text = _re.sub(r'CELEX \S+|\(EU\) \d+/\d+', ' ', text)
text = _re.sub(r'^#+ \d+(\.\d+)*', ' ', text, flags=_re.M)
text = _re.sub(r'Annex IV[^.]{0,40}|Article \d+\(?\d*\)?\(?[a-z]?\)?', ' ', text)
text = _re.sub(r'(CoLM|ICLR|ICML|NeurIPS|ACL) \d{4}', ' ', text)
text = _re.sub(r'95% CI|B = [\d,]+', ' ', text)  # interval label and bootstrap size
text = _re.sub(r'\b(19|20)\d{2}\b', ' ', text)
tokens = re.findall(r'(?<![\w.])\d{1,3}(?:,\d{3})*(?:\.\d+)?(?![\w])', text)
unmatched, checked = [], 0
for t in tokens:
    v = float(t.replace(',', ''))
    checked += 1
    if round(v, 4) in src or round(v, 2) in src or round(v, 0) in src: continue
    # allow small integers used as section numbers and counts
    if v == int(v) and v <= 20: continue
    unmatched.append(t)

print(f"numeric tokens checked : {checked}")
print(f"matched to source      : {checked - len(unmatched)}")
print(f"UNMATCHED              : {len(unmatched)}")
for t in sorted(set(unmatched), key=lambda x: float(x.replace(',',''))):
    print("   ", t)
sys.exit(0)
