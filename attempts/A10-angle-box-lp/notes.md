# A10-angle-box-lp — orientation-restricted measure LP: sizing the angle-box branch-and-bound

Owner: LP agent 2 (postdoc, LP / rigorous numerics). 2026-08-18. Status: **done** (numerical sizing study +
one rigorous restricted certificate). Process died once mid-way; everything below was re-run from disk.

Goal (I-U4/I-L7, A09 §4c): compute τ*_B(s) = min μ([0,s]²) s.t. μ(Q) ≥ 1 for every closed unit square Q ⊂ [0,s]²
with orientation θ(Q) ∈ Θ_B, for angle boxes Θ_B; τ*_B(s) < 11 kills the box ("no packing with all 11 orientations
in Θ_B has side ≤ s"; same shrink-and-scale proof as Theorem 1, orientations are preserved). Deliverable: the
crossing s_B(δ) (τ*_B = 11) for the Trump box Θ_B(δ) = [0,δ] ∪ [θ*−δ, θ*+δ], θ* = 40.18193729°, δ = 10°, 5°, 2°, 1°;
far boxes; campaign-size estimate and verdict.

**TL;DR.** (i) The restricted LP is calibrated: {0°} crosses 11 exactly at s = 4, {0°,45°} in (3.885, 3.886] =
Stromquist's 2+4√2/3 = 3.88562. (ii) Trump box: τ*_B(s) sits at 10.3–10.8 and then JUMPS to exactly 11 (a weight-11
fractional packing inside the box appears): s_B(10°) ≤ 3.84, s_B(5°) ∈ (3.84, 3.85), s_B(2°) ∈ (3.86, 3.865),
s_B(1°) ∈ (3.87, 3.874], s_B(0.5°) ∈ (3.87, 3.876], s_B(0.25°) ≤ 3.876; i.e. s* − s_B(δ) ≈ 0.006·δ[°] down to the
resolution floor (EPS_GEO = 1e-4 ⇒ ≈ 8e-4 in s) → the restricted LP IS tight at the optimum as δ → 0. A rigorous restricted certificate for
[0°,2°] ∪ [38.18°,42.18°] at s = 3.85 PASSES the exact verifier. (iii) BUT the box LP is NOT tight away from Trump:
boxes "uprights + moderate tilts 20°–36°" (e.g. [0,2]∪[32,36], [0,10]∪[20,30], [0,5]∪[25,35]∪[38,43]) are ALIVE at
3.85 and 3.87 with τ*_B = 11.000 exactly, through 4-fold-symmetric fractional structures (weights 1/4, 1/2), although
no packing is known there below 3.89. Such boxes never die under refinement by the pure box LP ⇒ a box B&B needs a
second killer (counts/case splits, clique cuts, core-MILP) for a whole band of angle space, and the multiset count
at the resolution needed for the Trump neighbourhood (δ ≈ 1° at s = 3.87) is ~10^7–10^10 before pruning.
Verdict: pure box-LP campaign NOT viable at 3.85–3.87 as a stand-alone; viable as the cheap first-level killer inside
a case-LP (I-L6) tree. Details in §6.

## 1. Code: `lp_measure_box.py` (modified copy of A07's `lp_measure2.py`)

- `--theta_box "0-10,30.18-50.18"` (degrees; bare number = single orientation), `--alpha a1,a2,...` class weight per
  interval (row RHS = α of the interval containing θ; max if several). Only rows/row search are restricted; atoms free.
- Symmetry `--sym auto|D4|C4`. D4 (A07's 8-point orbits, θ ∈ [0,45°], centres in the quadrant [s/2,s]²) is only WLOG
  when Θ_B is closed under θ ↦ 90°−θ (reflections map orientation class θ to 90°−θ; rotations by 90° fix classes);
  then the box is folded onto [0,45°]. Otherwise C4 (4-point orbits = rotations only, θ ∈ [0,90°), same quadrant,
  packing images weight y/4; column oracle samples the C4 quadrant). `auto` = D4 iff reflection-closed (90° ≡ 0°).
  All Trump/far/mid boxes below are EXACT boxes run with C4 (no reflected copies added).
- `Model.add_row` rejects any placement with θ ∉ Θ_B or centre outside the admissible range for this s.
- **Row oracle = exact per-θ arrangement search** (`RowOracle.exact_theta`) instead of A07's histogram scan on a
  c-grid: for fixed θ the mass μ(Q(c,θ)) is piecewise constant on the cells of the arrangement of the lines
  u = U_x ± (½−ε), v = U_y ± (½−ε) (atoms U in the frame rotated by −θ); a 2-D difference array + prefix sums gives every
  cell mass exactly (O(K²) memory, K = atoms with w > 0), cells with mass < α meeting the admissible domain are sampled
  (centre + 4 corners, clipped) and evaluated exactly; then A07's pattern-search refine (θ clamped to its interval)
  and a "fine" pass with θ-step 0.125°.  WHY: with the c-grid oracle the sanity run {0°,45°} at s = 3.89 gave τ = 10.756
  although ν* ≥ 11 (Stromquist's packing at 3.8856 fits with gaps ≈ 0.004); the LP measure had holes of mass 0.66 at
  the packing's upright squares lying in slivers of centre-space width ≈ 0.004 between atom event lines — invisible to a
  0.02 grid (A07 met the same phenomenon as verifier holes). Such misses bias every crossing s_B UPWARD, i.e. would
  fake tightness. With the exact oracle the same run gives τ = 11.000 (converged, 94 s).
- **Row pruning** `--prune 2` (default): rows non-binding (slack > 0, dual 0) for 2 consecutive solves are deleted
  (they can be regenerated). At 12k rows only ~1000 were binding; cold LP 58 s (IPM 120 s), binding-only 0.8 s;
  iteration time fell from ~90 s to ~8–15 s. Side effect: the joint loop oscillates (rows deleted/re-added),
  so "minmass" rarely reaches 1 in 900 s; τ itself is stable to ~1e-3 over the last 20 iterations in all runs.
- Warm start `--warm result.json` (expands D4/C4 images), `--state` resume, `--col_stop_iter 0` row-only phase.
- `run_batch.py jobs.json --procs k` job runner (skips finished/started jobs); `summarize.py [--plot]` →
  `results/summary.json`, `results/summary_table.md`, `results/crossings.json`, `plots/tau_trump_box.png`;
  `make_cert_box.py` restricted certificate; `verify_measure_restricted.py` = COPY of A08's verifier + `--theta-range`.

Reading the tables: "conv" = row AND column oracles found nothing (rare with pruning); "11.000 (ν=11)" = the dual found
a fractional packing of weight ≥ 11 with pointwise coverage ≤ 1 + 1e-6 (maxcov 1.000) ⇒ τ*_B(s) ≥ 11 up to oracle
tolerance whatever the primal status ⇒ box ALIVE. Values 10.x with maxcov 1.02–1.10 / minmass 0.85–0.99 are neither
bounds; the row-only continuations (`_ro`, columns frozen) give primal-feasible-up-to-minmass values that are upper
bounds for their atom set (and the certificate in §7 makes one of them rigorous).

## 2. Sanity checks (task 1)

| Θ_B | s | τ*_B | status | note |
|---|---|---|---|---|
| {0°} | 3.90 | 9.000 | conv | 9 atoms {1,2,3}² |
| {0°} | 4.05 | 16.000 | conv | crossing of 11 exactly at s = 4 (jump 9 → 16) ✓ |
| {0°,45°} (D4) | 3.88 | 10.686 | 600 s, minmass 0.993, maxcov 1.06 | < 11 |
| {0°,45°} | 3.885 | 10.692 | 600 s, minmass 0.987, maxcov 1.10 | < 11 |
| {0°,45°} | 3.886 | 11.000 (ν=11) | conv, 136 s | ≥ 11 |
| {0°,45°} | 3.89 | 11.000 (ν=11) | conv, 94 s | ≥ 11 |

⇒ {0°,45°} crossing in (3.885, 3.886] — Stromquist's Theorem 3 value 2+4√2/3 = 3.8856181 ✓ (τ jumps to exactly 11 as
soon as the 6+5 packing fits, as at s(10) in A07; below it the LP value is ~10.69, i.e. Stromquist's bound is a
fractional-cover bound with slack ~0.3 below the threshold).

## 3. Trump box (task 2): Θ_B(δ) = [0°,δ] ∪ [θ*−δ, θ*+δ], exact box, C4, joint runs 900 s (+ `_ro` row-only 600 s)

τ*_B(s) (joint value / row-only value where run):

| δ | 3.83 | 3.84 | 3.85 | 3.86 | 3.865 | 3.87 | 3.874 | 3.876 | 3.877 | crossing s_B(δ) | s* − s_B(δ) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10° | – | **11.000 (ν=11)** | 11.000 (ν=11) | (≥11) | | (≥11) | | | (≥11) | ≤ 3.84 (global ceiling 3.83) | ≥ 0.037 |
| 5° | 10.51 | 10.56 | **11.000 (ν=11, conv)** | 11.000 (ν=11) | | (≥11) | | | (≥11) | (3.84, 3.85) | 0.027–0.037 |
| 2° | – | 10.35 | 10.57 / 10.597 | 10.64 / 10.684 | **11.000 (ν=11)** | 11.0007 (ν=11) | | | 11.04 | (3.86, 3.865) | 0.012–0.017 |
| 1° | – | 10.31 | 10.54 / 10.560 | 10.60 / 10.632 | | 10.76 / **10.792** (ro, minmass 0.997) | 11.000 (maxcov 1.013) | **11.000 (ν=11, conv)** | 11.008 | (3.87, 3.874] | 0.003–0.007 |
| 0.5° | | | | | | 10.68 | | **11.000 (ν=11, conv, 250 s)** | | (3.87, 3.876] | 0.001–0.007 |
| 0.25° | | | | | | | | **11.000 (ν=11, conv, 60 s)** | | ≤ 3.876 | ≤ 0.001 (= floor) |

(≥11): implied by monotonicity in s (τ*_B non-decreasing) or by the box containing a box already at 11.
Caveat at s = 3.877: EPS_GEO = 1e-4 shrinks LP squares to side 1−2e-4, so the LP at s "sees" s·(1+2e-4);
3.877·1.0002 = 3.8778 > s* = 3.8770836, hence at 3.877 Trump's own packing is dual-feasible and every box ∋ {0,θ*}
is trivially ≥ 11; 3.876·1.0002 = 3.87678 < s* is still a genuine test. The floor of resolution near s* is ≈ 8e-4.

Shape: for every δ the value hovers at 10.3–10.8 (slope ≈ 20/unit s, like the global τ*) and then jumps to exactly
11 at s_B(δ), where a weight-11 fractional packing with orientations in the box appears; the "packing" that appears
uses tilts at the LOWER end of the tilted interval (30.7° for δ=10, 35.18° for δ=5 at 3.85) — the same
"uprights + 30–35° tilt" structure that saturates the global LP (A07 §5). Empirically **s* − s_B(δ) ≈ 0.006·δ**
(δ=5: 0.03; δ=2: ~0.014; δ=1: ~0.005; δ ≤ 0.5: below the 1e-3 resolution floor set by EPS_GEO) ⇒ s_B(δ) → s* as
δ → 0: the restricted LP is tight at the optimum in the same sense as the global LP at s(10) — but only in a
neighbourhood of Trump's angles: for the box to die at s_t one needs δ ≲ (s* − s_t)/0.006. Plot: `plots/tau_trump_box.png`.

Robustness of these numbers: values at 10.3–10.8 are joint-LP values with maxcov 1.02–1.07 and minmass 0.87–0.94;
the row-only continuations move them by ≤ +0.05 (10.572 → 10.597, 10.642 → 10.684, 10.540 → 10.560, 10.600 → 10.632),
so "< 11" is safe by ≥ 0.2 in every dead cell (δ=1 at 3.87: row-only 10.792 with minmass 0.997 ⇒ τ*_B ≤ 10.83 for that
atom set); the "≥ 11" cells marked ν=11 are dual-certified to oracle tolerance (maxcov 1.000); the 3.874/δ=1 cell has
maxcov 1.013 (dual scaled by 1/1.013 only gives ≥ 10.86) — "probably alive".

## 4. Counts-weighted variant (task 3)

Box δ=2 with counts (n_0, n_θ) = (6, 5): rows of class c get RHS α_c, normalised 6α_0 + 5α_θ = 11 (the LP is homogeneous
in α, so this is WLOG); box dead iff τ*_B(α) < 11.

| box, counts | s | α_0 | α_θ | τ*_B(α) | unweighted τ*_B | note |
|---|---|---|---|---|---|---|
| Trump δ=2, (6,5) | 3.86 | 0.8 | 1.24 | 12.16 | 10.68 | worse |
| Trump δ=2, (6,5) | 3.87 | 0.9 | 1.12 | 11.21 | 11.0007 | worse |
| Trump δ=2, (6,5) | 3.87 | 1.1 | 0.88 | 11.66 (conv, 30 s) | 11.0007 | worse: uprights expensive ⇒ corner/edge upright structure pays more |
| mid [0,2]∪[32,36], (6,5) | 3.85 | 0.8 | 1.24 | 12.17 | 11.000 | worse (the dual re-optimises to a tilt-heavier fractional structure) |
| mid [0,2]∪[32,36], (6,5) | 3.85 | 0.9 | 1.12 | 11.18 | 11.000 | worse |
| mid [0,2]∪[32,36], (6,5) | 3.87 | 0.8 | 1.24 | not run (pattern clear) | 11.000 | |

τ*_B(α) is the value of an LP minimisation as a function of its RHS, hence CONVEX in α; on the segment
6α_0 + 5α_θ = 11 the minimum is at/near α = (1,1) in every case tested. **Counts do not help** for balanced boxes:
the dual simply moves to a fractional structure matching the weights (uprights are cheap coverage, tilted squares
expensive, or vice versa). They can only help for boxes whose counts are far from what the fractional packing wants
(e.g. a box with 2 uprights and 9 tilted), which is not where the difficulty lies.

## 5. Far boxes (task 4), 600–900 s each

| Θ_B | 3.85 | 3.87 | 3.90 / 3.95 | verdict |
|---|---|---|---|---|
| [0,10] (all near-upright) | 9.333 (conv) | 10.500 (conv) | 11.000 / 11.000 (ν=11) | dead ≤ 3.87, alive at 3.90 (LP not tight there: no small-tilt packing < 4 is known) |
| [10,35] (no uprights) | 10.43 | 10.64 | | dead |
| [0,10] ∪ [20,30] | **11.000 (ν=11, conv, 211 s)** | **11.000 (ν=11, conv, 246 s)** | | ALIVE — mid-tilt fractional structure |
| [0,10] ∪ [40,45] | 10.55 | 10.86 | | dead (consistent with Trump δ=2) |
| [30,45] | 9.87 | 10.06 | | dead |
| [0,5] ∪ [25,35] ∪ [38,43] (3 classes) | **11.0005 (ν=11)** | 11.07 | | ALIVE via [25,35] |
| mid [0,2] ∪ [32,36] | **11.000 (ν=11, conv, 181 s)** | **11.000 (ν=11)** | | ALIVE |
| mid [0,1] ∪ [34.5,35.5] | **11.000 (ν=11, conv, 50 s)** | **11.000 (ν=11, conv, 45 s)** | | ALIVE at half-width 0.5° |
| mid [0,2] ∪ [29,31] | **11.000 (ν=11, conv, 55 s)** | **11.000 (ν=11, conv, 70 s)** | | ALIVE |
| mid [0,1] ∪ [31,33] | **11.000 (ν=11, conv, 70 s)** | **11.000 (ν=11, conv, 80 s)** | | ALIVE at half-width 0.5–1° |

The alive far/mid boxes all carry the same weight-11 fractional structure (e.g. [0,10]∪[20,30] at 3.85: 4 corner
uprights weight 1, 4 mid-edge uprights ½, the 4 rotations of a 30°-square at (2.46,2.53) with weight ½ each,
and three C4-orbits of near-upright squares near the centre with weight ¼ each: 4+2+2+3 = 11). This is the
"continuum/odd-cycle" integrality gap of A07 §5 in its cleanest form: 4-fold symmetric quarter/half weights that no
integral packing can realise. **The box LP has no leverage on these boxes: refining the box does not remove the
structure** (it lives at a single tilt ~30–35° plus uprights), so at s_t = 3.85 (and 3.87) the LP-only B&B never
kills the band "≥ 4–6 near-uprights + a tilt in ≈ [20°, 36°]". Boxes with tilts ≥ 38° (Trump side) or without
uprights die easily.

## 6. Campaign size (task 5)

Ingredients measured here: (a) per-box LP cost: 3–15 min for a fresh box (600–900 s wall to a stable value, 8–15 s
per iteration after pruning; ~2–3 min when the box is alive, because a weight-11 packing is found early);
(b) Trump neighbourhood: a box containing 0° and θ* dies at s_t iff its half-width δ ≲ (s* − s_t)/0.006, i.e.
δ ≲ 4.5° at 3.85, δ ≲ 1.2° at 3.87, δ ≲ 0.17° at s* − 1e-3 (and EPS_GEO already blurs 8e-4 in s there);
(c) the mid-tilt band (uprights + one tilt anywhere in ≈ [20°, 36°]) is unkillable by the box LP at 3.85–3.87 down to
half-width 0.5° (all six mid boxes: τ = 11.000 exactly, converged in 45–250 s), and counts do not help (§4).

Box count. Boxes are multisets of 11 intervals of width w (mod reflection): C(90/w + 10, 11)/2 ≈ 3.8·10⁴ (w = 10°),
1.1·10⁷ (5°), 6·10¹⁰ (2°), 7·10¹³ (1°). Union-monotonicity (Θ ⊂ Θ' ⇒ τ*_Θ ≤ τ*_Θ') lets one kill all multisets
supported in a dead union at once (2^(90/w) unions: 512 at 10°, 2.6·10⁵ at 5°), and count weights kill unbalanced
multisets inside alive unions; but every multiset whose union meets both a near-upright class and the mid-tilt band
[20°,36°] is alive for the LP at 3.85–3.87 regardless of resolution, and their number is ≥ C(90/w + 10 − k, 11 − k)
for the k ≥ 5–6 fixed squares, i.e. ≥ 10⁶ at 5° and ≥ 10⁹ at 2°, and each needs an LP (≥ 3 min) or a different
argument. Even the Trump neighbourhood alone at s_t = 3.87 needs w ≈ 1° ⇒ the 6+5 multiset {[0,1]×6, [39.7,40.7]×5}
plus its neighbours: the refinement tree from a 10° root to 1° boxes around Trump has ~42 children per level for the
6+5 split (Π(n_c+1)) and 4 levels ⇒ ~10³ LPs — that part is fine (a day on 6 cores). The order of magnitude of the
whole campaign is therefore set by the mid-tilt band, not by Trump: **≥ 10⁶–10⁷ boxes at 3.85 and unbounded (LP
never terminates on that band) unless a second killer is added**; with a second killer that disposes of the band
(count-weighted families / case-LP / clique cuts against the ¼-weight 4-cycles), the remaining tree is ~10³–10⁴
LPs ≈ days on 20 cores. Verdict: **10⁷-class (not viable) as a pure box-LP campaign; 10³–10⁴-class (viable) as the
first-level oracle of a case-LP tree that also branches on where the 30–35° squares sit.** The right next step is
therefore I-L6 (case-LP) with orientation boxes as one of its branching dimensions, and clique/region cuts against the
4-fold fractional structure (A07's advisor remark (b): at most k centres in a region) — not a pure angle B&B.

## 7. Restricted certificate (task 6) — DONE, PASS

`certs_wip/box_cert_3.85_d2.json` (768 atoms = C4 images of the 192 orbits of the row-only run
`results/trump_d2_s3.85_ro.json`, atoms rounded to 1e-6, weights ×1.03 rounded up, total 68221/6250 = 10.91536 < 11,
s = 77/20, `theta_box` = 0–2° ∪ 38.181937–42.181937°), built by `make_cert_box.py`.
Verified by `verify_measure_restricted.py` (COPY of A08's `certs/verify_measure.py` + `--theta-range`; boxes whose
t = tan(θ/2)-interval is disjoint from the range are skipped, boxes partially inside are kept, range widened by 1e-9
— sound because it only ever checks more placements):
`PASS (RESTRICTED) ... no packing of 11 unit squares with ALL orientations in 0-2,38.181937-42.181937 deg has side
<= 77/20`, 3,362,984 boxes, max depth 44, 158 s (2 jobs), first attempt (no witness round needed).
**This proves only: no packing with all orientations in [0°,2°] ∪ [θ*−2°, θ*+2°] has side ≤ 3.85 — NOT s(11) ≥ 3.85.**
Sanity of the tool: A07's global 3.80 certificate with `--theta-range 0-2,38.18-42.18` PASSes with 1.36M boxes (vs 5.8M
unrestricted). Log: `logs/verify_box_cert_3.85_d2.log`.

## 8. Files

`lp_measure_box.py`, `run_batch.py`, `jobs_batch*.json`, `summarize.py`, `make_cert_box.py`,
`verify_measure_restricted.py`, `results/*.json` (+ `_state.json` checkpoints; `results/old_noprune/` = batch 1
without row pruning), `results/summary.json`, `results/summary_table.md`, `results/crossings.json`, `logs/`,
`plots/tau_trump_box.png`, `certs_wip/box_cert_3.85_d2.json`.
Reproduce: `python lp_measure_box.py --s 3.85 --theta_box "0-2,38.181937-42.181937" --time_limit 900 --fine --out r.json`;
`python lp_measure_box.py --s 3.85 --theta_box ... --state r_state.json --col_stop_iter 0 --fine --prune 0 --out r_ro.json`;
`python make_cert_box.py r_ro.json 77/20 1.03 c.json`; `python verify_measure_restricted.py c.json --jobs 4 --theta-range "0-2,38.181937-42.181937"`.
