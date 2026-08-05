# Next session plan, written 2026-08-05 night

Read `CLAUDE.md`, `docs/P1-MEMORY.md`, `RESEARCH_LOG.md` first, as always. This
file is the ordered plan for the session on 2026-08-06 and is deleted or
rewritten at the end of it. It is not a decision record; decisions live in
P1-MEMORY.

**State at close of 2026-08-05.** HEAD `e0391d7` plus the log appends, pushed to
`origin/main`. 182 tests passing. Gates 1 and 2 passed. Grid fixed at 14,280
specifications from 1,190 discovery cells, subject to step 1 below. Sweep budget
measured: 19.4 h on L4, 25.7 h on T4. Gate 3 is 2026-08-16.

---

## The critical path

Steps 1 to 3 must complete in order before step 4 can start. Step 5 runs in
parallel with step 4 and does not depend on it.

### Step 1. Settle the corruption levels. Claude, about 90 minutes. BLOCKING.

The only remaining item with an unknown answer.

Fetch as PDF, not ar5iv, which returned an unusable render on 08-05:

- arXiv:2211.00593, Wang et al., for the definition of the corrupted distribution
- arXiv:2304.14997, Conmy et al. ACDC, for how it constructs corrupted datasets
- arXiv:2407.08734 section 3.1, which surveys ablation methodology and is the
  closest prior work

Read how each constructs its corrupt prompts. **One construction is known to be
standard, the ABC distribution: the same templates filled with three
independently sampled names. That is currently RECALLED from a search summary,
not VERIFIED from the paper, and must be verified before it enters the plan.**

**The fork, and it is a real one.** Every other axis in this grid meets the
standard that each level cites a published implementation. If only ABC can be
sourced, forcing three levels means inventing two, which reproduces exactly the
weakness that got the third prompt variant dropped.

- **Three levels sourced** -> axis stays as built, grid remains 14,280.
- **Fewer than three sourced** -> corruption becomes a fixed recorded choice
  rather than a crossed axis, the same treatment `clean_corrupt` received.
  Grid drops to **5,880 specifications from 490 discovery cells**, sweep drops to
  roughly **11 h on L4**.

The nesting machinery in `src/p1/spec.py` costs nothing if the axis collapses; it
simply stops firing. No code change is required either way beyond the config.

Do not resolve this by picking two plausible-sounding constructions. That is the
failure mode this project has avoided five times.

### Step 2. Three sign-offs. Ajay, five minutes. BLOCKING.

Claude presents these as a single question. Recommendations, all open to veto:

| Item | Recommendation | Rationale |
|---|---|---|
| `tau` levels | 0.05, 0.10, 0.20 | Spans strict to permissive; 0.10 is the modal choice in the faithfulness literature. Three levels keep the metric axis meaningful without tripling anything, since `tau` is a post-hoc cut. |
| H4 threshold | gap > 0.10 | Symmetric in spirit with the H2 rule at 0.20; a ten-point gap between structural and functional instability is the smallest that would survive a reviewer asking whether it is noise. Judgement call, defended as one. |
| `phi` constants | Freeze `DEFAULT_SIZE_BINS`, `DEFAULT_BAND_NAMES`, segment labels at current values | All are PROVISIONAL in code. They must be frozen before the lock because they determine every claim. Freezing the current values is the neutral choice; changing them after seeing results would be unforgivable. |

### Step 3. Lock. Claude drives, Ajay confirms. Thirty minutes. BLOCKING.

1. Apply steps 1 and 2 to `preregistration/PLAN.md`. Remove every remaining
   `[CONFIRM]`.
2. Regenerate the grid arithmetic and confirm `grid_size` matches the plan.
3. Full test run. Read the output, do not assume.
4. `git tag -a prereg-p1-confirmatory`, push the tag.
5. Record hash and UTC timestamp in `RESEARCH_LOG.md`.
6. File the embargoed OSF registration. Record the DOI.
7. `preregistration/DEVIATIONS.md` becomes append-only from this moment.

**Nothing confirmatory runs before the tag is pushed.**

### Step 4. Build the runner and launch. Claude builds, Ajay runs. Two hours.

`scripts/sweep.py`, taking a config, with:

- per-cell manifest keyed by `spec_id`, skip if `status: ok` on restart
- `torch.cuda.get_device_name` recorded in every cell manifest
- prune scores written per discovery cell, `(metric, tau)` cuts applied post-hoc
  against `EDGE_COUNT_LADDER`
- discard path per section 7, including the no-rung-meets-criterion case
- `confirmatory: true` in the config, asserted by the script

**Validate on a slice before launching the full sweep.** Ten cells, check resume
works by killing and restarting, then launch.

Colab cell, one self-contained block, starting from `%cd /content` so it is
idempotent, and reinstalling because a runtime-type change rebuilds the VM:

```python
%cd /content
!pip install -q auto-circuit==1.0.1 transformer-lens==2.18.0
!rm -rf "paper 1" && tar xzf p1.tar.gz 2>/dev/null
%cd "/content/paper 1"
!python3 -c "import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Card: **L4 if the compute-unit balance covers 20 hours, T4 if tight.** Do not
spend units on A100 or H100; the workload is bound by kernel launch and Python
overhead, not arithmetic, so it does not scale with GPU class. L4 measured only
1.33x the T4.

**Results must be copied off Colab before the session ends.** The VM is
ephemeral. Mount Drive or download `results/` at intervals.

### Step 5. Start the manuscript. Runs in parallel with step 4.

Only results-independent sections. All of these must be written before results
are seen anyway, so this is not a compromise to fill time.

- Regulatory section. The material is in `docs/ANNEX-IV.md` and is the strongest
  part of the paper: Annex IV 2(e) and 3, section 4 on metric appropriateness,
  section 7 on the harmonised standards gap, and the Article 86 propagation.
- Related work. Positioning is fixed: P1 differentiates on the propagation to a
  regulatory claim and the filability criterion, **not** on crossing a space.
  See DESIGN-DELTAS D7, which found the brief's positioning sentence false.
- Formalism and method. The specification space, `phi`, the filability criterion,
  the statistical treatment.
- Limitations. Already substantial and all owned: seed agreement of only 0.81 at
  the instrument's own default dataset size, the ladder quantisation, the
  confounded IEG-1000 comparison, `clean_corrupt` fixed rather than crossed, the
  mean-dataset-size axis not separable from discovery data.

**Open positioning decision for Ajay**, which shapes the introduction: lead with
the regulatory framing or the methodological one. The regulatory framing is the
novelty and the reason Gate 1 passed; the methodological framing is what a FAccT
audience reads first. Genuinely Ajay's call.

---

## Do not do

- Do not run anything confirmatory before the tag is pushed.
- Do not pick corruption levels that cannot be cited.
- Do not touch the `phi` constants after they are frozen.
- Do not write a results section. **The results do not exist.** `F`, `pi_star`,
  `J_bar`, the variance components and the interchange numbers all require the
  sweep. Anything written about them before then is fiction.
- Do not trust an unmeasured factor. Five were wrong on 08-05 alone: 12x reuse
  measured 4.62x, 51x IEG measured 25.8x, 20x GPU measured 7x, L4 predicted 2 to
  3x measured 1.33x, and `n_prompts` was missing from the design entirely.

## Standing risk

The largest unmeasured quantity is now the **claim-level** behaviour of `phi`.
Everything measured so far is circuit-level. If `phi` is near-constant across
real circuits then `F` is near zero and H2 fails; if it almost always differs
then `F` is near one and the claim map is too fine to mean anything. Both are
publishable per PLAN.md section 8, but the shape of the paper differs a lot.

The eight calibration circuits at n=128 in `results/calib-nprompts/` would give a
first signal cheaply. **A rule for that pilot must be written and committed
before it runs**, same discipline as the `n_prompts` calibration. Raised with
Ajay on 08-05 and not yet decided.
