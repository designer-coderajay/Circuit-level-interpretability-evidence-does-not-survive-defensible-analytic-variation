"""Every number in a manuscript must exist in the source JSON or be derivable.

Mechanical, not editorial. It extracts numeric tokens from each manuscript and
matches them against a set built from `results/analysis/*.json`, the realised
grid, and closed-form quantities. Anything unmatched is printed for a human to
justify or delete. Its purpose is to make "no fabricated numbers" checkable
rather than promised.

Run:
    python3 analysis/check_manuscript_numbers.py [path ...]

With no argument it audits every live manuscript in `LIVE`. `paper/arxiv` is
not audited by default: it is frozen at the submitted v1, so flagging figures
that have since moved on would be noise rather than signal. Pass its path
explicitly to check it.

Two defects this file carried until 2026-09-21, both found by running it rather
than reading it:

  it audited `paper/manuscript.md` and nothing else, so the IASEAI submission
  had never been checked at all

  it ended in `sys.exit(0)`, so it reported unmatched tokens and still exited
  clean. A check that cannot fail is not a check. It now exits 1.

LaTeX needs its own handling before tokenising. `32{,}491` is one number to a
reader and two tokens to a naive regex, and a stripped `%` comment is not paper
content. Both are normalised in `_plain` below.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

#: Manuscripts audited when no path is given.
LIVE = ('paper/manuscript.md', 'paper/iaseai/main.tex')

#: Tests collected by `python3 -m pytest tests/ --collect-only -q`. Asserted
#: against the real count by `tests/test_manuscript_constants.py`, so it cannot
#: go stale without a test failing. It did go stale once, undetected, because
#: the audit was checking the manuscript against this constant and nothing was
#: checking the constant.
N_TESTS = 368

A = Path('results/analysis')
src: dict[float, list[str]] = {}
def add(v, label):
    """Register a source value at every rounding a manuscript might print.

    The JSON holds full precision, 0.731611; prose prints 0.7316, 0.732 or 73.2.
    Matching only the stored value would flag every correctly rounded figure, so
    each value is registered at 0 to 4 decimal places, and as a percentage.

    Both rounding conventions are registered. Python's `round` is round-half-even,
    so it turns 3780.5 into 3780, while prose and every typesetting convention
    write 3,781. Registering only the former flags a correctly rounded number as
    unmatched, which is how this was found on 2026-09-21."""
    try: f = float(v)
    except (TypeError, ValueError): return

    def half_up(x, dp):
        from decimal import Decimal, ROUND_HALF_UP
        q = Decimal(1).scaleb(-dp)
        return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))

    for dp in range(5):
        for x, tag in ((f, label), (f * 100, 'pct ' + label)):
            src.setdefault(round(x, dp), []).append(tag)
            src.setdefault(half_up(x, dp), []).append(tag)

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
    (5000,'ladder rung'), (39,'verification checks'),
    (N_TESTS,'tests collected'), (0.5227,'discard rate'), (52.3,'discard rate pct'),
]: add(v, why)

# Claim-class counts and per-size counts are computed from the sweep, not stored
# in the analysis JSON, so register them from the same source the tables use.
import sys as _sys, yaml as _yaml
from collections import Counter as _Counter
_sys.path.insert(0, 'src'); _sys.path.insert(0, 'scripts')
from analyse import load_records as _lr, PRIMARY_GRANULARITY as _PG, PRIMARY_MAP as _PM
_recs, _ = _lr(Path('results/sweep'), _yaml.safe_load(open('configs/sweep.yaml'))['axes'])
_lab = [r['claims'][_PG][_PM] for r in _recs]
_cnt = _Counter(_lab)
for _c, _n in _cnt.items():
    add(_n, 'claim class count')
    add(_n / len(_lab), 'claim class share')
_sizes = _Counter(r['edges'] for r in _recs)
for _k, _n in _sizes.items():
    add(_k, 'ladder rung'); add(_n, 'specs at size')
# Aggregates and derived arithmetic used in the prose, each justified in the log.
add(sum(_n for _k, _n in _sizes.items() if _k >= 5000), 'specs contributing no flips')
add(1 + 12 * 13, 'non-terminal sources feeding the output')
for _band in ('early', 'late', 'middle'):
    _s = sum(_n for _c, _n in _cnt.items() if _band in _c)
    add(_s, f'{_band} band total'); add(_s / len(_lab), f'{_band} band share')

# The attainable maximum of F, and the observed F as a share of it. Computed,
# not registered as a constant: the constant that used to sit here was 0.8889,
# the asymptotic bound, and the audit passed the paper's corrected 0.8890 only
# because one of its rounding registrations happened to collide with it. A
# number check that matches the right figure for the wrong reason is worse than
# no check, because it reports a pass.
from p1.multiverse import max_flip_rate as _mfr
_ceiling = _mfr(len(_lab), len(_cnt))
add(_ceiling, 'attainable maximum of F at the realised N and k')
add(1 - 1 / len(_cnt), 'asymptotic bound 1-1/k, stated as a limit not a ceiling')
add(_cnt.most_common(1)[0][1] / len(_lab), 'modal share')
for _o in (0.7316, 0.731611):
    add(_o / _ceiling, 'observed F as a share of its attainable maximum')

# The pre-registered second-model grid. Counted from the config the run will
# take, not typed, so the paper and the launch cannot disagree.
from p1.spec import enumerate_grid as _eg
_rep = _yaml.safe_load(open('configs/replication_pythia.yaml'))['axes']
_rep_specs = list(_eg(_rep))
add(len(_rep_specs), 'replication specifications')
add(len({(s.discovery_objective, s.ablation, s.corruption, s.prompt_variant, s.seed)
         for s in _rep_specs}), 'replication discovery cells')

def _plain(path: Path) -> str:
    """Manuscript text with everything that is not a numeric claim removed.

    DOIs, arXiv ids, section numbers, years, CELEX and article references are
    each verifiable elsewhere and are not results.

    LaTeX sources need two normalisations first, and skipping either produces
    false positives that swamp the real ones. On 2026-09-21 the IASEAI paper
    reported 47 unmatched tokens; every one was an artefact of their absence:

      `%` starts a comment. Drafting notes are not paper content.
      `32{,}491` is the LaTeX thousands separator. Tokenised naively it is two
      numbers, `32` and `491`, neither of which matches anything.
    """
    text = path.read_text()

    if path.suffix == '.tex':
        text = re.sub(r'(?<!\\)%.*', ' ', text)     # comments, but not \%
        text = re.sub(r'\{,\}', ',', text)          # thousands separator
        text = re.sub(r'\\%', '%', text)            # escaped percent sign
        text = re.sub(r'\\(cite|ref|label|eqref|citet|citep)\{[^}]*\}', ' ', text)
        text = re.sub(r'\\begin\{tabular\}\{[^}]*\}', ' ', text)

    # Software versions are facts about the environment, not results, and they
    # must not be matched against the source set. When the Infrastructure
    # paragraph was added on 2026-09-22 it introduced eight numeric tokens
    # (6.6, 3.12, 1.0, 2.18, 2.11, 1.26, 1.16, 0.14) and the audit reported all
    # eight as matched. Every one was a coincidental collision with a rounded
    # result. A pass for the wrong reason is the failure mode this whole file
    # exists to prevent, so the versions are stripped by name.
    text = re.sub(
        r'\b(?:auto-circuit|transformer-lens|torch|numpy|scipy|statsmodels|'
        r'Python|Linux|CUDA|cu)[\s-]*v?\d+(?:\.\d+)*(?:\+\S+)?',
        ' ', text, flags=re.I)

    text = re.sub(r'doi:\S+|10\.\d{4}/\S+', ' ', text)
    text = re.sub(r'arXiv:\d{4}\.\d{4,5}(v\d)?', ' ', text)
    text = re.sub(r'CELEX \S+|\(EU\) \d+/\d+', ' ', text)
    text = re.sub(r'^#+ \d+(\.\d+)*', ' ', text, flags=re.M)
    # `[ ~]` matters: LaTeX writes `Article~86(1)` with a non-breaking space and
    # markdown writes `Article 86(1)`. Matching only the tilde leaves 86 loose.
    text = re.sub(r'Annex[ ~]IV[^.]{0,40}|Article[ ~]\d+\(?\d*\)?\(?[a-z]?\)?', ' ', text)
    text = re.sub(r'(CoLM|ICLR|ICML|NeurIPS|ACL|IASEAI) ?\d{4}', ' ', text)
    text = re.sub(r'95% CI|B = [\d,]+', ' ', text)  # interval label and bootstrap size
    text = re.sub(r'thebibliography\}\{\d+\}', ' ', text)  # label width, not a claim
    text = re.sub(r'\b(19|20)\d{2}\b', ' ', text)
    return text


def audit(path: Path) -> list[str]:
    tokens = re.findall(r'(?<![\w.])\d{1,3}(?:,\d{3})*(?:\.\d+)?(?![\w])', _plain(path))
    unmatched = []
    for t in tokens:
        v = float(t.replace(',', ''))
        if round(v, 4) in src or round(v, 2) in src or round(v, 0) in src: continue
        # allow small integers used as section numbers and counts
        if v == int(v) and v <= 20: continue
        unmatched.append(t)

    print(f"\n{path}")
    print(f"  numeric tokens checked : {len(tokens)}")
    print(f"  matched to source      : {len(tokens) - len(unmatched)}")
    print(f"  UNMATCHED              : {len(unmatched)}")
    for t in sorted(set(unmatched), key=lambda x: float(x.replace(',', ''))):
        print("     ", t)
    return unmatched


paths = [Path(a) for a in sys.argv[1:]] or [Path(p) for p in LIVE]
missing = [p for p in paths if not p.exists()]
if missing:
    sys.exit(f"no such manuscript: {', '.join(str(p) for p in missing)}")

total = sum(len(audit(p)) for p in paths)
print(f"\n{'PASS' if total == 0 else 'FAIL'}  {total} unmatched across {len(paths)} manuscript(s)")
sys.exit(1 if total else 0)
