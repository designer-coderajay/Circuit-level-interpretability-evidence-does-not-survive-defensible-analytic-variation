"""Emit every manuscript table as LaTeX rows, straight from stored results.

No number in the paper is typed by hand. This script is the only path from
`results/analysis/*.json` to a table body, so a transcription error is not
possible without the checker catching it.
"""
import json, sys, yaml
from collections import Counter
from pathlib import Path
sys.path.insert(0,'src'); sys.path.insert(0,'scripts')
from analyse import load_records, PRIMARY_GRANULARITY, PRIMARY_MAP
from p1.multiverse import flip_rate

A = Path('results/analysis')
out = []
axes = yaml.safe_load(open('configs/sweep.yaml'))['axes']
recs,_ = load_records(Path('results/sweep'), axes)
lab = [r['claims'][PRIMARY_GRANULARITY][PRIMARY_MAP] for r in recs]
N = len(lab); cnt = Counter(lab)

out.append("% ---- TABLE: claim class shares ----")
for i,(c,n) in enumerate(cnt.most_common(),1):
    band = c.split('components in the ')[-1].split(' of the model')[0] if 'components in the ' in c else '?'
    size = 'sparse' if 'sparse' in c else ('moderate' if 'moderate' in c else ('distributed' if 'distributed' in c else '?'))
    out.append(f"{i} & {band} & {size} & {n:,} & {n/N:.4f} \\\\")

sz = json.load(open(A/'stage4_null_by_size.json'))['by_granularity']
out.append("\n% ---- TABLE: by circuit size, MEDIUM ----")
for r in sz['MEDIUM']['by_size']:
    out.append(f"{r['size']:,} & {r['n_specifications']:,} & {r['discovered_F']:.4f} & "
               f"{r['discovered_classes']} & {r['null_F_median']:.4f} & {r['null_classes_median']:.0f} \\\\")
f = sz['MEDIUM']['with_size_held_fixed']; b = sz['MEDIUM']['size_fixed_bootstrap']
out.append(f"% size-fixed MEDIUM: disc {f['discovered_F']:.4f} CI [{b['ci95_low']:.4f},{b['ci95_high']:.4f}] null {f['null_F_median']:.4f}")
fc = sz['COARSE']['with_size_held_fixed']; bc = sz['COARSE']['size_fixed_bootstrap']
out.append(f"% size-fixed COARSE: disc {fc['discovered_F']:.4f} CI [{bc['ci95_low']:.4f},{bc['ci95_high']:.4f}] null {fc['null_F_median']:.4f}")

out.append("\n% ---- TABLE: granularity x addressee ----")
s1 = json.load(open(A/'stage1_claims.json'))['outcomes']
for k in ['affected/COARSE','affected/MEDIUM','affected/FINE','overseer/COARSE','overseer/MEDIUM','overseer/FINE']:
    o = s1[k]; a,g = k.split('/')
    out.append(f"{a} & {g} & {o['n_distinct_claims']} & {o['flip_rate']:.4f} & {o['modal_share']:.4f} & no \\\\")

out.append("\n% ---- TABLE: discard by metric ----")
d = json.load(open(A/'stage1_claims.json'))['discard_rate_by_axis_level']['metric']
for m,v in sorted(d.items(), key=lambda x: x[1]['rate']):
    out.append(f"{m.replace('_',' ')} & {v['kept']:,} & {v['discarded']:,} & {v['rate']:.3f} \\\\")

out.append("\n% ---- FACTS ----")
h4 = json.load(open(A/'h4.json'))
j  = json.load(open(A/'stage2_jbar.json'))
out.append(f"% J_bar {j['J_bar']:.4f} CI [{j['J_bar_ci95'][0]:.4f},{j['J_bar_ci95'][1]:.4f}]")
out.append(f"% D quantiles {j['pairwise_D_quantiles']}")
out.append(f"% H4 agreement {h4['agreement_rate']:.4f} kappa {h4['cohens_kappa']:.4f} gap {h4['gap']:.4f} CI {h4['gap_ci95']}")
out.append(f"% pooled F {flip_rate(lab):.4f} classes {len(cnt)} N {N:,}")
a = json.load(open(A/'stage3_decomposition.json'))['arm_a_structural_reml']
out.append(f"% REML shares {{k: round(v,4) for k,v in a['share_of_total'].items()}}")
out.append("% REML " + str({k: round(v,4) for k,v in a['share_of_total'].items()}))
print("\n".join(out))

# ---- bin sensitivity, regenerated so the table is not typed by hand ----
from p1.graph import nodes_from_edge_names
from p1.features import features_from_circuit
from p1.claim_map import layer_band, DEFAULT_SIZE_BINS, DEFAULT_BAND_NAMES
import glob
pairs=[]
for f in glob.glob('results/sweep/*/result.json'):
    d=json.load(open(f)); top=d['top_edges']; cache={}
    for e in d['specifications'].values():
        if e.get('status')!='ok': continue
        k=e['edges']
        if k not in cache:
            ft=features_from_circuit(nodes_from_edge_names(top[:k]),n_blocks=12,n_heads_per_block=12)
            cache[k]=(layer_band(ft,DEFAULT_BAND_NAMES), len(ft.components)/156.0)
        pairs.append(cache[k])
def FB(bins):
    return flip_rate([(b,next(n for t,n in bins if fr<t)) for b,fr in pairs])
base=[(t,n) for t,n in DEFAULT_SIZE_BINS]
print("\n% ---- TABLE: bin sensitivity ----")
print(f"committed bins & {FB(base):.4f} \\\\")
for m in (0.5,0.8,0.9,1.1,1.25,1.5,2.0):
    b=[(min(t*m,1.01) if n!='distributed' else 1.01,n) for t,n in base]
    print(f"all thresholds $\\times$ {m:g} & {FB(b):.4f} \\\\")
print(f"equal thirds & {FB([(1/3,'a'),(2/3,'b'),(1.01,'c')]):.4f} \\\\")
print(f"deciles & {FB([(i/10,str(i)) for i in range(1,10)]+[(1.01,'10')]):.4f} \\\\")
print(f"no size term (COARSE) & {FB([(1.01,'x')]):.4f} \\\\")
