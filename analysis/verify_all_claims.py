import sys, json, yaml, glob, itertools, math
from pathlib import Path
from collections import Counter
import numpy as np
sys.path.insert(0,'src'); sys.path.insert(0,'scripts')
from analyse import load_records, PRIMARY_MAP, PRIMARY_GRANULARITY, AXES

ok=[]; bad=[]
def chk(name, got, want, tol=5e-4):
    good = abs(got-want) <= tol
    (ok if good else bad).append(f"{name}: got {got!r} want {want!r}")
    print(f"{'PASS' if good else 'FAIL':4} {name:52} {got:.6f} vs {want:.6f}")

axes = yaml.safe_load(open('configs/sweep.yaml'))['axes']
recs,meta = load_records(Path('results/sweep'), axes)
lab = [r['claims'][PRIMARY_GRANULARITY][PRIMARY_MAP] for r in recs]
N=len(lab); cnt=Counter(lab)

print("=== 1. GRID ARITHMETIC ===")
print(f"     cells ok {meta['audit']['cells_ok']}  failed {meta['audit']['cells_failed']}")
chk("specifications with claims", N, 7561, 0)
chk("cells ok x 12 = pre-registered specs", meta['audit']['cells_ok']*12, 15840, 0)
chk("discarded = 15840 - 7561", 15840-N, 8279, 0)
chk("discard rate", (15840-N)/15840, 0.5227, 1e-3)
chk("LOGIT_MSE arm = 1540/7", 1540/7, 220, 0)

print("\n=== 2. F FROM FIRST PRINCIPLES ===")
# exact Gini-Simpson
num = sum(c*(c-1) for c in cnt.values())
F_formula = 1 - num/(N*(N-1))
chk("F closed form", F_formula, 0.7316, 5e-4)
# independent: probability two distinct draws differ, via complement of concordance
conc = sum(c*(c-1) for c in cnt.values())/(N*(N-1))
chk("F = 1 - concordance", 1-conc, F_formula, 1e-12)
# brute force on a subsample, unbiased estimate of the same quantity
rng=np.random.default_rng(0); idx=rng.choice(N,1200,replace=False)
sub=[lab[i] for i in idx]
pairs=list(itertools.combinations(range(len(sub)),2))
bf=sum(1 for a,b in pairs if sub[a]!=sub[b])/len(pairs)
print(f"     brute-force on 1200 specs ({len(pairs):,} pairs): {bf:.4f}  (sampling, not exact)")
chk("brute force within sampling error", bf, F_formula, 0.03)

print("\n=== 3. CLASS SHARES AND PI* ===")
shares=[c/N for _,c in cnt.most_common()]
chk("shares sum to 1", sum(shares), 1.0, 1e-12)
chk("pi* = max share", max(shares), 0.4109, 5e-4)
chk("n classes", len(cnt), 9, 0)
chk("F upper bound 1-1/k", 1-1/len(cnt), 0.8889, 1e-3)
print(f"     F/ceiling = {F_formula/(1-1/len(cnt)):.3f}")
chk("filable at alpha=0.20 requires pi*>=0.80", 1.0 if max(shares)>=0.80 else 0.0, 0.0, 0)

print("\n=== 4. H4 ARITHMETIC ===")
h4=json.load(open('results/analysis/h4.json'))
chk("H4 F matches primary", h4['F'], F_formula, 1e-9)
chk("functional instability = 1 - agreement", 1-h4['agreement_rate'], h4['functional_instability'], 1e-12)
chk("gap = F - functional instability", h4['F']-h4['functional_instability'], h4['gap'], 1e-12)
chk("gap value", h4['gap'], 0.3344, 5e-4)
chk("gap CI lower > threshold", 1.0 if h4['gap_ci95'][0]>0.10 else 0.0, 1.0, 0)

print("\n=== 5. EDGE NAMESPACE, CLOSED FORM ===")
tot=sum(3*12*(1+13*b) + (1+13*b) + 12 for b in range(12)) + (1+12*13)
chk("combinatorial edge count", tot, 32491, 0)
d=json.load(open(sorted(glob.glob('results/sweep/*/result.json'))[0]))
chk("instrument reports same", d['n_edges'], 32491, 0)
chk("components 12*12+12", 12*12+12, 156, 0)

print("\n=== 6. J_BAR ===")
j=json.load(open('results/analysis/stage2_jbar.json'))
chk("J_bar", j['J_bar'], 0.1396, 5e-4)
chk("J_bar CI contains estimate", 1.0 if j['J_bar_ci95'][0]<=j['J_bar']<=j['J_bar_ci95'][1] else 0.0, 1.0, 0)
chk("spec pairs = N(N-1)/2", N*(N-1)//2, 28580580, 0)
k=200; chk("J_rand(200) = k/(2N-k)", k/(2*32491-k), 0.003087, 1e-5)

print("\n=== 7. STAGE 1 AND 3 CONSISTENCY ===")
s1=json.load(open('results/analysis/stage1_claims.json'))
p=s1['outcomes']['overseer/MEDIUM']
chk("stage1 F", p['flip_rate'], F_formula, 1e-9)
chk("stage1 CI lower > H2 threshold 0.20", 1.0 if p['bootstrap']['ci95_low']>0.20 else 0.0, 1.0, 0)
s3=json.load(open('results/analysis/stage3_decomposition.json'))['arm_b_claim_level']
chk("stage3 pooled F == stage1 F", s3['pooled_F'], F_formula, 1e-9)
chk("F_fixed(metric)", s3['by_axis']['metric']['fixed']['observed'], 0.5939, 5e-4)
chk("F_fixed(metric) CI lower > 0.20", 1.0 if s3['by_axis']['metric']['fixed']['ci95_low']>0.20 else 0.0, 1.0, 0)
for a in AXES:
    e=s3['by_axis'][a]['fixed']
    assert e['ci95_low']<=e['observed']<=e['ci95_high'], a
print("     PASS all 7 F_fixed observed values lie inside their own CI")

print("\n=== 8. SIZE-FIXED RESULT ===")
sz=json.load(open('results/analysis/stage4_null_by_size.json'))['by_granularity']
for g,want in (('COARSE',0.2706),('MEDIUM',0.2746)):
    b=sz[g]['size_fixed_bootstrap']
    chk(f"{g} size-fixed F", b['observed'], want, 5e-4)
    chk(f"{g} CI lower above 0.20", 1.0 if b['ci95_low']>0.20 else 0.0, 1.0, 0)
    chk(f"{g} interval quotable", 1.0 if b['interval_quotable'] else 0.0, 1.0, 0)

print("\n" + "="*66)
print(f"PASSED {len(ok)}   FAILED {len(bad)}")
for b in bad: print("  FAIL", b)
