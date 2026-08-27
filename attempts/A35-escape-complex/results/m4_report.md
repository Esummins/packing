# A35 / M4 — escape cascade tree from Trump's jam

Code: `code/m4_geom.py` (fast float64 row/SAT engine), `code/m4_cascade.py`
(predictor–corrector follower + event/branch/termination logic),
`code/m4_wedge.py`, `code/m4_analyze.py`. Reuses `code/strata_lib.py` and the
A22 certificate. Data: `results/m4_cascade*.json`, `results/m4_queues*.json`,
`results/m4_wedge.json`, `results/m4_rejams.json`. Runtime 5 min total, single
process (budget was 3 h; the measurement is cheap).

**Everything here is `[NUM]`** — float64 path following. Rigour is M2's job. The
one place where the float result is *strong enough to be promoted* is the wedge
constant in §1, and it is stated so that M2 can certify it directly.

Self-consistency of the float engine: at z-hat all 38 rows evaluate to
≤ 4.4e-16, the float Jacobian agrees with `strata_lib`'s `[IV]` Jacobian
midpoint to 3.9e-16, and the float SAT gaps reproduce M1's `[IV]` gap table
((6,7) 0.024875, (8,9) 0.024875, (3,4) 0.032558, (7,10) 0.118783, …) exactly.

---

## 1. HEADLINE — the 81-survivor work queue has **no escape routes at all**

The brief's work queue is M1's 81 survivors. Before following anything, the
first-order escape cone of each was computed:

> `C(B) = { v ∈ ker A_M : A_B v ≥ 0 }`, M = retained rows.

**All 81 have `C(B) = {0}`.** The LP `max Σ_b (∇g_b·v)` s.t. `A_B v ≥ 0`,
`|coeffs| ≤ 1` returns optimum **exactly 0** for every one of the 81. Since
`rank A = 34`, `A_M v = 0` and `A_B v = 0` force `v = 0`, so the optimum being 0
means the cone is trivial.

Consequence: a curve `z(t)` with `g_M(z(t)) = 0` has `ż ∈ ker A_M`, hence some
broken row satisfies `g_b(z(t)) = t (∇g_b·ż) + O(t²) < 0` — infeasible. **Every
one of the 81 closed strata meets a neighbourhood of z-hat in {z-hat} only.**
They are "WEDGE-EMPTY", the same conclusion as M1's `(E)` empty-stratum
certificate but reached by one LP instead of a rank-34 minor.

Quantitatively (`results/m4_wedge.json`), the **wedge strength**

> `w(B) = min over unit v ∈ ker A_M of max_{b∈B} ( −∇g_b·v )`

is uniformly large — there is no near-degenerate case:

| | value |
|---|---|
| n wedged | **81 / 81** |
| min w(B) | **0.577354** (= 1/√3 to 6 digits; B = {1,8,9,21,22,26}) |
| median w(B) | 0.816497 (= √(2/3)) |
| max w(B) | 0.816497 |
| dof split | 72 strata dof 1, 9 strata dof 2 |

Identical under the repaired row basis of §5 (min 0.577353). **This is the M4
headline and it is promotable**: M2 only needs `w(B) > 0` in interval arithmetic
plus a curvature bound `H̄` on the stratum to conclude `g_b < 0` for
`0 < t < 2w(B)/H̄` — a rigorous `(E)`-type certificate for all 81, with a
margin of 0.577 rather than a numerical hair.

Structural reading: rows 8,9 = `W2c1[y=0]`, `W2c1[x=s]` are the *two orthogonal
wall rows of the same corner* of square 2; rows 21,22 = `W5c2[x=s]`,
`W5c2[y=s]` likewise for square 5. The 1-dof mechanism slides that corner along
the container corner, so one clearance opens exactly as fast as the other
closes (rates ±0.8165). Every one of the 81 is a decoration of one of these two
seeds (M1 §6), so the whole survivor list dies of the same corner geometry.

**M1's 81 → 0.** Adding the wedge test to M1's four kill-tests empties the
escape complex at the linearization. M1 tabulated wedging at k=1/2/3 but did not
apply it as a kill-test in the synthesis; the two k=2 survivors {8,9}, {21,22}
are exactly 2 of M1's 18 wedged k=2 strata.

---

## 2. What was measured instead

With Q1 empty the cascade was run on the strata that actually carry escape
routes (needed anyway for theory.md's `(C)` chaining and for the alarm check):

| queue | definition | n |
|---|---|---|
| Q1 | M1's 81 survivors | 81 → **0 routes** |
| Q2 | all k=1 strata with non-trivial escape cone | 18 of 38 |
| Q3 | all k=2 strata with non-trivial escape cone | 541 of 703 |
| Q4 | k=3 sample, wedge-tested | 500 kept of 1104 movable / 1200 sampled (8436 total) |

Q2 = 18 and Q3 = 541 = 388 (dof 1) + 153 (dof 2) reproduce M1's movable counts
exactly. Movable fraction by codimension: k=1 **0.474**, k=2 **0.770**,
k=3 **0.920** (sample).

Root rays: the cone LP returns *vertices* (boundary rays with some gap rate 0),
so random positive mixtures are added to reach the cone's relative interior;
rays whose zero-rate rows leave a gap closed at first order are **refined** —
those rows go back into the maintained set, which is the honest statement that
such a route lives on a *smaller* stratum. Result:

* **860 of 1140 strata have an empty cone interior** (81 Q1 + 779 others): they
  contribute no route of their own, only routes of lower strata. Route identity
  therefore collapses hard: 2227 root routes carry only **283 distinct effective
  break sets** (18 with |B|=1, 180 with |B|=2, 85 with |B|=3), 7.9 rays each.

Two passes were run, both with the full termination taxonomy:

* **pass A** — the brief's spec, MARGIN at `s_hat + 1e-3`.
* **pass B** — MARGIN disabled, routes run to the travel cap 0.05, so that
  cascade events can actually be observed.

and both were run twice, on A22's 38 rows and on the repaired basis of §5. The
repaired-basis numbers are the meaningful ones and are quoted below.

---

## 3. Cascade tree — sizes, branching, depth, terminations

### pass A (MARGIN = s_hat + 1e-3), repaired basis

| | |
|---|---|
| root routes | 2227 |
| total segments | 2227 |
| **events (E1/E2/E4)** | **0** |
| branching factor | **0** (no route reaches an event) |
| depth distribution | depth 0: 2227 |
| MARGIN | **2116** (95.0 %) |
| BLOCKED (true overlap / containment) | 105 |
| WEDGE (E3) | 6 |
| median arclength to MARGIN | 0.0107 (max 0.0284) |
| median ‖z−z-hat‖_∞ at MARGIN | 0.0054 (max 0.0237) |
| median steps to MARGIN | 4 (max 7) |
| median arclength to first `s_hat+1e-4` crossing | **0.0015** |

> **G3 is discharged in the strongest possible way: under the stopping rule the
> theory actually uses, the cascade has depth 0. Every route leaves the basin
> ceiling before any contact event fires.** A `(C)` chain from z-hat to the ridge
> is ONE segment, not a tree — the first gained contact is still ~5× further
> along the arc (§4) than the point where `s ≥ s_hat + 1e-3`.

### pass B (MARGIN disabled, run to travel 0.05), repaired basis

| | |
|---|---|
| root routes | 2259 |
| total segments | 2464 |
| leaves | 1364 |
| depth distribution | 0: 2259, 1: 204, 2: 1 |
| E1 (gained contact) | 1093 |
| E2 (broken row re-closes) | 7 |
| E3 (wedge) | 3 |
| E4 (rank change on route) | **0** |
| events per route | 0: 1364, 1: 1100 (mean 0.446) |
| branching factor at events | mean **0.182**, max **3**; hist {0: 1027, 1: 115, 2: 31, 3: 13} |
| TRAVEL | 1229 |
| BLOCKED | 86 |
| PROJFAIL (step control gave up) | 46 |
| WEDGE | 3 |
| median travel at TRAVEL stop | 0.0514, median arclength 0.0944 |

Why the branching factor is **below 1**: at an E1 the gap is *closing*, so the
"keep it broken" child is never admissible (`E1_graze` fired **0** times). The
"maintain the new contact" child is admissible in only 154 of 1093 events; in
**921** the new contact *wedges* the route (no continuation direction with the
contact maintained) and in **18** it drives dof to 0. So the escape complex,
followed from z-hat, is a set of near-paths that mostly die at the first gained
contact, not a branching tree.

---

## 4. E1 gained contacts — M1's Lipschitz table holds

E1 pairs observed, over 1093 events on 2464 segments:

| pair | (3,4) | (6,7) | (8,9) | (7,10) | anything else |
|---|---|---|---|---|---|
| E1 count | 640 | 384 | 69 | 0 | **0** |

**Zero E1 events outside M1's candidate list** `{(6,7),(8,9),(3,4),(7,10)}`
(`n_offlist_E1 = 0` in both bases, both passes). (7,10), gap 0.1188, is never
reached inside travel 0.05 — consistent with the Lipschitz bound. No new
corner–wall contact ever fired, as M1 predicted (all 156 inactive combos ≥ 0.5486).

E1 arclength distribution: 10th pct 0.041, median **0.075**, max 0.159 — i.e.
the first gained contact sits at ~7× the arclength at which pass A already
terminates.

**But: a pair the row system does not know about.** Squares 1 and 3 (both
upright, centres (1.5,0.5) and (0.5,1.5)) **touch corner-to-corner at (1,1)**:
SAT gap = 0 at z-hat (`[IV]` enclosure ±4.7e-61), and this pair is **not among
A22's 13 contact pairs / 38 rows**. M1's "nearest non-contact pair 0.024875" is
therefore the nearest *positive* gap; the true nearest is 0. It is a genuine
active constraint: it blocks 37–43 routes outright ("BLOCKED (overlap,1,3)") and
re-closes as an E1 on 3 routes after having opened. Corner–corner contact makes
the SAT gap non-smooth there, which is presumably why A22 curated it out; for
the escape complex it must be in the menu.

---

## 5. Two defects in the A22 row basis, exposed by route following

**(a) The two `dist` rows are not contact descriptions.** Rows 36, 37 are
`D0-1`, `D0-3` = `|c_i−c_j|² − 1 ≥ 0` for the flush upright pairs (0,1) and
(0,3). Holding such a row at 0 pins the *centre distance* at 1, which does not
pin the contact: as soon as either square rotates the squares interpenetrate
while the row still reads 0. Measured on A22's rows as written, this kills
**911 of 2255 routes (40 %)** at arclength ~1e-8 —
`BLOCKED (overlap,0,1)` 469, `BLOCKED (overlap,0,3)` 442.

Replacing rows 36, 37 by the **true SAT contact row** (value = the pair's SAT
gap; gradient = the gradient of the (owner, edge, corner) row realising it)
repairs it: the same run gives 105 BLOCKED instead of 911, 2116 MARGIN instead
of 1344. The repaired 38-row system still has `rank A = 34` at z-hat
(σ_min 0.1159 vs 0.1266), and §1's wedge verdict is unchanged. Both runs are
kept in the results (`m4_cascade*.json` vs `m4_cascade_repaired*.json`).

This does **not** affect A22's value certificate (a weaker valid inequality only
enlarges the feasible set, so `s ≥ s_hat` is still sound). It affects the
*stratification*: any `(C)` continuation certificate that maintains `D0-1` or
`D0-3` as a stratum equality is following a curve that leaves the feasible set
immediately. M2/M3 should use the SAT form for these two pairs.

**(b) Selection/dominance flips are real and near.** With the unrepaired basis a
route reached a configuration where the maintained rows all read 0 while pair
(0,1) had SAT gap **−0.026** — the A22 edge selection was no longer the SAT
witness. This is theory.md's G5 and it bit at travel ≈ 0.052, i.e. just outside
the brief's cap. Routes are now monitored on all 55 true SAT gaps, which is what
found it.

---

## 6. ALARM CHECK — **GREEN**

> `min over every route, every step, of (σ − s_hat) = **0.0** exactly`
> (both bases, both passes; 0 alarms at tolerance `s_hat − 1e-12`).

Supporting statements, all over the full 2227 + 2464 segment set:

* no segment ever has `σ < σ(its own start)` (`n_segments_s_below_own_start = 0`);
* no segment ever has a negative `dσ/dτ` at any step (`n_any_negative_dsdtau = 0`);
* the minimum observed `dσ/dτ` at a route start is **+0.00325**, the maximum
  +0.356.

Two candidate alarms appeared in an intermediate run and were **both traced to
follower bugs, not to geometry**: a Gauss-Newton corrector was allowed to make
an excursion of 0.078 from a predictor step of 0.0015, jumping the route onto a
different (infeasible) branch on which squares 0 and 1 overlapped by 0.026 and
broken row 13 sat at −0.0215. Fixes now in the code: the corrector displacement
is capped at `2h`, branch re-projections may not move the point by more than
1e-5, and **all 55 pair SAT gaps** (not just the non-contact ones) are monitored
for true overlap. After the fixes: 0 alarms, and the two configurations are
correctly rejected as infeasible. Worth recording as a methodology note for M2:
a value certificate that trusts a maintained-row residual without a true-SAT
check can be fooled exactly this way.

**Ascent-rate consistency (theory.md (A) Consequence 1).** On the unrepaired
basis, over 2255 depth-0 routes, the observed first-step `dσ/dτ` matches the
predicted `e_s·v` from the kernel to

> max |obs − pred| = **1.67e-4**, median 5.8e-5

(finite-difference error at h = 1.5e-3, i.e. consistent to the order of the
scheme). k=1 rates land in M1's tabulated range [0.04276, 0.12145]. On the
repaired basis the median agreement is the same (5.8e-5) but 437 of 2227 routes
disagree by > 1e-3 (max 0.136): the `sat` row's gradient at a *flush* contact is
a subgradient choice among tied witnesses, so the kernel prediction is
selection-dependent. That is G5 again, now quantified: **the flush-contact tie
moves the predicted ascent rate by up to 0.14**, which any per-segment `(C)`
multiplier bound must accommodate.

---

## 7. New jams found

`results/m4_rejams.json`. 34 re-jam hits (dof → 0 when a gained contact is
maintained), **7 distinct σ values**, all strictly above s_hat:

| σ | σ − s_hat | travel_∞ | gained pair | active rows / rank | e_s in active cone? | nearest A04 family |
|---|---|---|---|---|---|---|
| 3.879775005 | +0.002691 | 0.0141 | (6,7) | 45 / 34 | **no** | Δ 2.7e-3 |
| 3.882635049 | +0.005551 | 0.0175 | (6,7) | 45 / 34 | **no** | Δ 3.0e-3 |
| 3.882917535 | +0.005834 | 0.0296 | (6,7) | 45 / 34 | **no** | Δ 2.7e-3 |
| 3.884196077 | +0.007112 | 0.0180 | (6,7) | 45 / 34 | **no** | Δ 1.4e-3 |
| 3.886746029 | +0.009662 | 0.0326 | (3,4) | 45 / 34 | **no** | **Δ 3.5e-12 — exact hit** |
| 3.888413478 | +0.011330 | 0.0343 | (3,4) | 37 / 34 | **no** | Δ 4.0e-4 |
| 3.895928754 | +0.018845 | 0.0504 | (6,7) | 45 / 34 | **no** | Δ 1.3e-3 |

Method: the active set is rebuilt *geometrically* at the point (all 176
corner–wall clearances and all 55 SAT gaps at tolerance 1e-7), and — for menu
completeness at flush ties — **every** (owner, edge, corner) row realising an
active pair gap is included, not just one witness. Then
`A_act^T λ = e_s, λ ≥ 0` is solved.

* All 7 are genuinely rank-34 (rigid) with 14–15 active pairs.
* **In none of them is `e_s` in the cone of the active gradients**, even with the
  full tie menu. So all 7 are locally rigid configurations that are **not local
  minima of σ**: theory.md `(C)(b)`'s "refute" branch fires, not the "genuine new
  critical point" branch. The cascade's re-jam branch produced **zero new jams**
  in this sense.
* σ = 3.886746029 coincides with an A04 catalogued family's `s_min`
  (3.8867460) to **3.5e-12**, and shares its 41.565° tilt angle — but the upright
  count differs (6 here vs 7 in the catalogue entry), so it is a σ-coincidence /
  relabelled variant, not a verified configuration match. Flagged, not claimed.
* The other 6 σ values match no A04 family (nearest 4.0e-4 to 3.0e-3) —
  consistent with their not being minimisers, since A04's search only catalogues
  local optima.

---

## 8. Tree-size estimate for full certification

Under the brief's stopping rule (MARGIN at `s_hat + 1e-3`) the measured cost is

> **routes × segments = 1 segment per route**, mean arclength 0.011,
> median 4 corrector steps, and 7.9 rays per distinct effective stratum.

Route count needed to cover codimension ≤ K, using the measured movable
fractions and the ray statistics:

| k | strata C(38,k) | movable frac (measured) | movable strata | distinct effective strata contributing | routes ≈ 7.9 × |
|---|---|---|---|---|---|
| 1 | 38 | 0.474 | 18 | 18 | 142 |
| 2 | 703 | 0.770 | 541 | 180 | 1 420 |
| 3 | 8 436 | 0.920 (sample) | ~7 760 | 85 seen from a 500-stratum sample; ≥ 1 000 extrapolated | ~8 000 |
| ≤ 6 | 2.8e6 | → 1 | ~2.8e6 | unknown | ~2e7 upper bound |

**But the route-based cost model is the wrong one, and M4's own result says so.**
The 81 strata that the FJ program actually has to certify (M1's cone-alive,
non-empty survivors) need **no routes at all** — §1 kills them with one LP each
plus a curvature bound, at a wedge margin of 0.577. The correct M2 cost estimate
for the local program is therefore

> **81 wedge certificates + 143 empty-stratum certificates = 224 certificates**,
> not a cascade tree.

Route following remains needed only for the *ridge handoff* (theory.md G1): it
takes ‖z − z-hat‖_∞ ≈ 0.005 and ~4 Newton steps to leave the `s_hat + 1e-3`
ceiling along any escape, and the collar is reached before the escape complex
has a chance to branch.

---

## 9. Gaps / caveats (honest list)

* **G-1 (biggest).** Everything is `[NUM]` float64. The wedge constant of §1 is
  a *point* statement at z-hat with float gradients; M2 must (i) re-evaluate the
  kernel and the rates in interval arithmetic and (ii) supply a curvature bound
  `H̄` along the stratum to turn `w(B) > 0` into a finite-`t` exclusion. Nothing
  in §1 is rigorous yet, but nothing in it is delicate either (margin 0.577,
  smallest retained singular value 0.113).
* **G-2.** Rank/dof along a route is a float SVD verdict at `RANK_TOL = 1e-8`
  relative. E4 (rank change on a route) fired **0** times in 2464 segments,
  which is reassuring but is itself `[NUM]`.
* **G-3.** The k=3 queue is a 1200-of-8436 sample, and k ≥ 4 was not followed at
  all; the §8 extrapolation beyond k=3 is arithmetic, not measurement.
* **G-4.** The gained-contact row used when a contact is maintained is the *single*
  SAT-witness (owner, edge, corner). At a tie this is one of several valid rows;
  §6 measures the resulting ascent-rate ambiguity at up to 0.14. The `(C)`
  segments must carry the full tie menu (theory.md G5), which M4 did only in the
  §7 re-jam post-analysis.
* **G-5.** 46 PROJFAIL segments (1.9 %) in pass B: the step controller could not
  find a step satisfying both the corrector-residual and the
  corrector-displacement guard. These are unresolved route ends, not
  terminations; they cluster at travel ≈ 0.029.
* **G-6.** The (1,3) corner–corner contact is monitored but not *stratified*:
  routes are blocked when it closes, and no child is spawned that maintains it.
  A complete escape complex needs it as a (non-smooth) contact node.
* **G-7.** Branching was explored depth-first to depth ≤ 6 with dedupe by
  (effective break set, gained rows, direction hash rounded to 1e-4); a coarser
  or finer hash would change the segment count, though not the depth-0 result of
  §3 (which has no branching at all).
* **G-8.** Terminations SLACK and DEPTH never fired; the taxonomy is therefore
  only partially exercised.

---

## Files

* `attempts/A35-escape-complex/code/m4_geom.py` — float64 rows, gradients,
  vectorised 55-pair SAT gaps with witnesses, 176 containment clearances,
  the `sat` pseudo-row.
* `attempts/A35-escape-complex/code/m4_cascade.py` — queues, wedge test,
  Newton projection, adaptive follower, event scan + bisection, branching,
  termination taxonomy, checkpointing. `M4_REPAIR_DIST=1` swaps the two `dist`
  rows for SAT rows.
* `attempts/A35-escape-complex/code/m4_wedge.py` — wedge strengths of the 81.
* `attempts/A35-escape-complex/code/m4_analyze.py` — re-jam active-set rebuild,
  full-menu cone test, A04 comparison.
* `attempts/A35-escape-complex/results/m4_cascade.json`,
  `m4_cascade_eventsurvey.json` — A22 basis, pass A / pass B.
* `attempts/A35-escape-complex/results/m4_cascade_repaired.json`,
  `m4_cascade_repaired_eventsurvey.json` — repaired basis, pass A / pass B.
* `attempts/A35-escape-complex/results/m4_queues.json`,
  `m4_queues_repaired.json` — the wedge survey of the 81 and the Q2/Q3/Q4 lists.
* `attempts/A35-escape-complex/results/m4_wedge.json` — §1's table.
* `attempts/A35-escape-complex/results/m4_rejams.json` — §7's table with
  configurations.
* `attempts/A35-escape-complex/results/m4_run.log`, `m4_run_repaired.log`.
