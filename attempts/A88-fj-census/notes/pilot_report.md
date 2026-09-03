# A88 T3 COST-PILOT  --  pricing H1 by CONTACT STRUCTURE

**Verdict up front.** Per-structure the route is CHEAP: triage 13.6 ms, FJ tier ~50 ms median and it CLOSES on 0.9533 of census survivors. It still loses to A85 by ~3 orders of magnitude, and it loses on the CENSUS SIZE N alone: at N = 1e11 the TRIAGE ALONE costs 3.8e+05 CPU-h against A85's 3,200-7,000. For the whole route to fit in 7,000 CPU-h at N = 1e11 the per-structure cost would have to be 0.00025 s (0.25 microseconds). The dominant multiplier is **N**, not the per-structure price.

**Nothing in this file is a certificate or a verdict about s(11).** Every number is a COST measurement. The interval engine used (`code/p88_iv.py`) is float interval arithmetic with an outward pad of `8.9e-16 * max|endpoint|` per operation (~18x the 0.5 ulp rounding error of one IEEE-754 double op), cross-checked against t3lib's rigorous `mpmath.iv` `row_value` to **1.2e-14** on every row of every structure. Row-activity zero tests carry an absolute slack ZTOL = 1e-12. A real certificate would use the mpmath path throughout and cost more per box; the pilot measures the SHAPE of the cost.

## 0. What a per-structure certificate is here

For a support structure H (graph + wall masks + contact-type decoration + tilt-class order) the claim is: *no Fritz-John point of the enclosing-side function with active set contained in H and `s <= s-hat_hi = 3.877084`*. FJ multipliers live only on H, so the claim is LOCAL TO THE LOADED CORE: squares in no row of H are dropped along with their feasibility rows. Dropping constraints can only enlarge the FJ set, so this is a sound weakening. The certificate box is the CORE box: `cx, cy` per loaded square (wall-tightened as A31 `lib0._box`), ONE tilt variable per TILT CLASS (pinned classes fixed exactly, at 0 or at pi/2), and `s in [3.82, 3.877084]`.

Two notes on the vocabulary. (i) Tilts are **not** folded mod pi/2: folding a theta of pi/2 down to 0 rotates that square's corner and edge labels and silently rewrites every row of H that mentions it, so a square recorded at pi/2 is kept as its own pinned class. (ii) The census emits only the EQUALITY rows; the t3lib DOMINANCE rows that make a sep row equal true SAT separation are determined by `(o, e, p, kstar)` and are rebuilt here as `g >= 0` SIDE CONDITIONS (56 per census structure on average). Their sign convention is validated in the selftest: every rebuilt dominance row is strictly positive at every realising point (min **3.80e-04** over all 21 A87/Trump points). They are load-bearing  --  see the leaf shares below.

Inputs: 720 census-sample structures (620 main `F0+K0-1+K0-3` + 100 `K0-1 dropped`), the 19 A87 genuine-FJ structures (6 of them LOOSE mid-drain probes, not certified FJ), and Trump. Every census record's `m` and `chi` were re-derived here and agree.

## 1. Tier 1  --  triage

T1a is bookkeeping (m, k_H, chi = m - (3 k_H + 1), rigid-possible flag chi >= 0). **Only 2 of 720 census structures are rigid-possible** (chi >= 0); the census is overwhelmingly FLEXIBLE, so the FJ tier is almost entirely the Farkas/Gordan branch, not the Krawczyk branch.

T1b is the realisability LP:

* with the tilt classes confined to interval bins every row of H is INTERVAL-LINEAR in the centres and s;
* each coefficient interval is split as midpoint +- radius and the radius part bounded by its worst case over the centre box, so `|row - (sum ac_i v_i + Kc)| <= sum r_i Vmax_i + Krad =: E` with `Vmax_i = max(|lo_i|, |hi_i|)` over that variable's box range;
* the equality `row = 0` is RELAXED to the two linear inequalities `sum ac_i v_i + Kc <= E` and `-(sum ac_i v_i + Kc) <= E`. Every genuine realisation with tilts in the bins satisfies both, so this is a sound OUTER relaxation: LP infeasibility really does mean H has no realisation in that tilt bin, and it can never kill a realisable structure;
* rebuilt dominance rows enter one-sided (`upper end of the relaxed value >= 0`); containment uses the one-sided sound bounds `v + A_hi >= 0` and `v + A_lo <= s`;
* the LP actually solved is the margin form `max t` with `t` added to every relaxed row, so HiGHS always returns a dual; `t* < -1e-9` is the KILL and `|t*|` the margin. Tilt classes are bisected (<= 3 levels, <= 64 leaves; leaves inconsistent with the strict class order are pruned for free). KILL iff every leaf is infeasible.
* **KILL TYPE**: each killing run is repeated with `s in [1, 5]` instead of `[3.82, 3.877084]`, which also widens the wall-tightened centre boxes. Still infeasible => CONTAINMENT-type (unrealisable at any side, A59's diagnosis); feasible => S-HAT-type (the kill uses the side bound  --  new work).

| set | n | KILL | kill frac (1 sigma) | CONTAINMENT | S-HAT | survivor frac (1 sigma) | ms mean | ms p95 | chi>=0 |
|---|---|---|---|---|---|---|---|---|---|
| A87 | 19 | 8 | 0.4211 [0.3145, 0.5355] | 0 | 8 | 0.5789 [0.4645, 0.6855] | 10.4 | 18.9 | 9 |
| census | 620 | 131 | 0.2113 [0.1954, 0.2281] | 130 | 1 | 0.7887 [0.7719, 0.8046] | 13.5 | 26.4 | 2 |
| k0drop | 100 | 31 | 0.3100 [0.2658, 0.3579] | 30 | 1 | 0.6900 [0.6421, 0.7342] | 14.1 | 30.1 | 0 |
| trump | 2 | 0 | 0.0000 [0.0000, 0.3333] | 0 | 0 | 1.0000 [0.6667, 1.0000] | 8.7 | 8.7 | 2 |
| **CENSUS (census+k0drop)** | 720 | 162 | 0.2250 [0.2098, 0.2409] | 160 | 2 | 0.7750 [0.7591, 0.7902] | 13.6 | 26.4 | 2 |

**Kill type by bracket (census population):** CONTAINMENT 0.2222 [0.2071, 0.2381]; S-HAT 0.0028. **Survivor fraction 0.7750 [0.7591, 0.7902].**

Farkas dual mass by row family over the killing leaves (`box_s` = the s-hat side bound, `box_centre` = the wall-tightened centre box; both enter as VARIABLE bounds rather than rows): `{"box_centre": 0.645, "box_s": 0.0, "contain_hi": 0.0, "contain_lo": 0.0, "sep": 0.355, "wall": 0.0}`.

No exact-rational Farkas certificate was produced for the pilot; the LP dual residual is recorded per killing leaf in `results/pilot88_triage.jsonl`. On A54/A59 experience a rational certificate would multiply the triage cost by ~2-5x  --  which changes nothing below, since the triage alone already loses by ~2 orders of magnitude at N = 1e11.

### Sanity on the (b) structures  --  the required check

The A87 structures are REALISED (genuine k0 FJ points at sigma 3.8868-4.0, all above s-hat). T1b must not kill them with the side bound dropped, and it does not: all 8 kills among them are S-HAT-type (exactly the sigma = 4.0 family, whose realisations all sit above s-hat), never CONTAINMENT-type. **No containment-type kill of a realised structure occurred  --  the bug signature did not fire.** Trump survives T1.

## 2. Tier 2  --  the FJ tier

Branch and bound over the core box. Leaf tests in order: HC4 / interval Gauss-Seidel propagation on the interval-linear rows (the linear form depends only on the tilt bins, so it is built once per box and reused across sweeps); a-structure (`0 not in [g_r](B)`); a-ineq (a rebuilt dominance side row provably negative); a-sigma (`sigma_min(B) > s-hat_hi`, using `sigma >= every loaded corner coordinate`); F (Gordan/Farkas over the box with the row set FIXED by H, so there is NO selection menu and A87's menu explosion does not arise); K (Krawczyk on D independent rows picked by pivoted QR at the box midpoint, rigid-possible only); otherwise bisect the widest coordinate relative to its initial range, with a x1.5 preference for tilt classes.

### The 20-structure pilot table

| tag | set | k_H | m | chi | D | d_H | ratt | boxes | s | ms/box | stop | depth | open | log10 remaining vol | min max-width | F LPs | F fired | K tries | roots |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| o006 | A87 | 11 | 39 | 5 | 31 | 2 | 0 | 20000 | 32.18 | 1.61 | box_cap | 53 | 29 | -84.3 | 0.360 | 10014 | 0 | 0 | 0 |
| o000 | A87 | 11 | 41 | 7 | 27 | 2 | 0 | 20000 | 36.01 | 1.80 | box_cap | 39 | 23 | -74.6 | 0.360 | 10011 | 0 | 0 | 0 |
| o002 | A87 | 11 | 41 | 7 | 31 | 2 | 0 | 20000 | 36.37 | 1.82 | box_cap | 42 | 29 | -61.3 | 0.719 | 10014 | 0 | 0 | 0 |
| o004 | A87 | 11 | 40 | 6 | 30 | 2 | 0 | 20000 | 34.00 | 1.70 | box_cap | 37 | 27 | -51.8 | 0.719 | 10013 | 0 | 0 | 0 |
| o003 | A87 | 11 | 42 | 8 | 31 | 1 | 0 | 20000 | 33.11 | 1.66 | box_cap | 43 | 21 | -73.7 | 0.719 | 10010 | 0 | 0 | 0 |
| o011 | A87 | 11 | 41 | 7 | 31 | 2 | 0 | 20000 | 32.29 | 1.61 | box_cap | 45 | 31 | -71.6 | 0.719 | 10015 | 0 | 0 | 0 |
| o012 | A87 | 10 | 29 | -2 | 24 | 7 | 1 | 20000 | 28.46 | 1.42 | box_cap | 47 | 33 | -58.6 | 0.360 | 10016 | 0 | 0 | 0 |
| o018 | A87 | 10 | 34 | 3 | 30 | 0 | 1 | 20000 | 32.97 | 1.65 | box_cap | 48 | 35 | -46.6 | 0.943 | 10017 | 0 | 0 | 0 |
| o025 | A87 | 11 | 31 | -3 | 25 | 6 | 0 | 20000 | 29.97 | 1.50 | box_cap | 50 | 41 | -81.2 | 0.360 | 10020 | 0 | 0 | 0 |
| o026 | A87 | 11 | 31 | -3 | 25 | 4 | 0 | 20000 | 28.57 | 1.43 | box_cap | 48 | 41 | -81.2 | 0.360 | 10020 | 0 | 0 | 0 |
| o028 | A87 | 11 | 34 | 0 | 25 | 3 | 0 | 20000 | 28.54 | 1.43 | box_cap | 34 | 25 | -17.9 | 0.719 | 10012 | 0 | 0 | 0 |
| trump_1e-09 | trump | 11 | 42 | 8 | 24 | 0 | 0 | 20000 | 31.17 | 1.56 | box_cap | 36 | 25 | -93.9 | 0.360 | 10012 | 0 | 0 | 0 |
| trump_1e-06 | trump | 11 | 42 | 8 | 24 | 0 | 0 | 20000 | 31.52 | 1.58 | box_cap | 36 | 25 | -93.9 | 0.360 | 10012 | 0 | 0 | 0 |
| census_00217 | census | 11 | 26 | -8 | 32 | None | None | 29 | 0.04 | 1.46 | complete | 6 | 0 | EMPTY | 2.877 | 14 | 0 | 0 | 0 |
| census_00140 | census | 11 | 26 | -8 | 31 | None | None | 33 | 0.04 | 1.36 | complete | 6 | 0 | EMPTY | 2.877 | 16 | 0 | 0 | 0 |
| census_00161 | census | 11 | 28 | -6 | 30 | None | None | 23 | 0.03 | 1.50 | complete | 6 | 0 | EMPTY | 2.877 | 11 | 0 | 0 | 0 |
| k0drop_00620 | k0drop | 11 | 26 | -8 | 31 | None | None | 39 | 0.05 | 1.37 | complete | 5 | 0 | EMPTY | 2.877 | 19 | 0 | 0 | 0 |
| k0drop_00709 | k0drop | 11 | 24 | -10 | 32 | None | None | 31 | 0.04 | 1.26 | complete | 6 | 0 | EMPTY | 2.877 | 15 | 0 | 0 | 0 |
| census_00467 | census | 11 | 29 | -5 | 31 | None | None | 31 | 0.05 | 1.72 | complete | 7 | 0 | EMPTY | 2.877 | 15 | 0 | 0 | 0 |
| census_00403 | census | 11 | 29 | -5 | 33 | None | None | 37 | 0.06 | 1.51 | complete | 8 | 0 | EMPTY | 2.877 | 18 | 0 | 0 | 0 |

The split is total and it is the point of the whole pilot:

* the **7 CENSUS structures COMPLETE**  --  stack empty, zero surviving boxes, zero roots  --  in 23-39 boxes and 0.035-0.056 s. The certificate "no FJ point with support in H and s <= s-hat" is DISCHARGED for each;
* the **13 A87/Trump structures never complete** (all hit the 20,000 box cap at ~30 s). That is the CORRECT behaviour, not a failure: those structures CONTAIN a genuine FJ point, so there is nothing to discharge and no certificate to have. For those the right output is to IDENTIFY the point, which is what the canary below shows Krawczyk doing.

**Two-tier kill rate on the census population:** T1 kills 0.2250, and the FJ tier then closes 0.9533 of the T1 survivors, so the pipeline discharges about 96.4% of census structures and leaves ~3.6% open. The open residue is what a real run would still owe a proof for.

Leaf-verdict shares over the tier-2 set: `{"hc4": 0.9398, "a_struct": 0.0598, "a_ineq": 0.0005}`.

### Cost calibration (larger sample)

Seven completing structures is too thin a base for `c_FJ`, so the FJ tier was also timed on a uniform subsample of **150** census T1 survivors with a 20 s cap each (`results/pilot88_fj_calib.jsonl`). This is a per-structure COST MEASUREMENT, not a run of the exclusions at scale  --  total wall time 149 s.

| quantity | value |
|---|---|
| COMPLETE | 143 / 150 = 0.9533 [0.9329, 0.9678] (1 sigma) |
| seconds, completing structures | mean 0.0640, median 0.0498, p95 0.1649, max 0.2319 |
| boxes, completing structures | mean 43, median 33, p95 111, max 167 |
| seconds, ALL (CENSORED at the 20 s cap) | mean 0.9944  --  this is a LOWER BOUND, the 7 capped structures were still running |
| rigid-possible (chi >= 0) in the sample | 0 / 150 |
| chi of the capped structures | [-8, -7, -6, -6, -7, -2, -9] |

Leaf-kill shares over the calibration set: `{"a_ineq": 0.6669, "hc4": 0.1884, "a_struct": 0.0922, "F": 0.0525}`. The rebuilt DOMINANCE side conditions carry two thirds of all kills; without them the tier would not close at all.

### Does F fire? YES  --  but rarely, and only where it is needed

A87 found Gordan never fires over configuration cells and blamed the selection MENU. With the row set FIXED by H there is no menu, and F DOES fire: **2050** firings over the calibration set, 5.25% of all leaf kills  --  but concentrated on **4 of 150** structures, and those are among the hard ones. On the 20-structure pilot table F fired 0 times in 130294 box LPs (the completing census structures close on a-structure and a-ineq before F is reached; the A87/Trump structures contain genuine FJ points, where F CANNOT fire by definition).

The LP itself was validated with controls: on a positive control (one square pinned in the SW corner, rows `q_0` on `x=0` and on `y=0`) it returns t = 1.0; adding the `x=s`/`y=s` rows correctly returns 0. Note this box test is the BOX VERSION of the point-wise NNLS/Gordan descent direction in A87 `fjpolish87`  --  the same test lifted to a box.

### K is essentially never reached by the search

Krawczyk was attempted **0** times across the tier-2 set: the branch and bound never drove a box below the Krawczyk basin width (0.05) within the cap on the structures that do not close, and the ones that do close never need it. Where Krawczyk CAN be run (the canary descent) it works perfectly. The obstruction is reaching a small enough box, not the test.

### The volume metric saturates  --  use the log-space one

"Discharged volume fraction" is not usable here: HC4 contracts the root box to ~1e-60..1e-94 of its volume on the FIRST sweep (the realisation set of H has positive codimension), so the discharged fraction is 1.0 in double precision from box 1. The table therefore reports `log10` of the REMAINING volume, computed in log space over the open boxes; `EMPTY` means the stack emptied and the search is complete.

### HC4 ablation (measured on 2 structures, ON vs OFF)

| tag | HC4 | boxes | s | log10 discharged frac |
|---|---|---|---|---|
| o006 | True | 2000 | 3.2 | 0.00 |
| o006 | False | 2000 | 2.7 | -0.06 |
| o000 | True | 2000 | 3.2 | 0.00 |
| o000 | False | 2000 | 2.8 | -0.27 |

HC4 is what makes the search do anything at all: without it the discharged volume fraction stays at ~0.5-0.9 (the box barely moves); with it the root box collapses onto the realisation variety immediately, and it costs nothing measurable in ms/box.

### What limits the FJ tier  --  EXTRAPOLATED

Deep probes (no box cap, 120-300 s) were run on the structures that do NOT close, to size the obstruction. Fitting `log2(boxes visited at depth d)` against `d` gives the branching per level; the depth needed is `n_wide * log2(W_max / 0.05)` with `n_wide` the number of core coordinates HC4 leaves wider than the Krawczyk basin at the root.

| tag | boxes | s | n_wide | halvings/coord | depth needed | log2 branch/level | min max-width reached |
|---|---|---|---|---|---|---|---|
| census_00293 | 68261 | 110 | 32 | 5.85 | 187 | 0.708 | 1.439 |
| census_00428 | 65961 | 110 | 30 | 5.85 | 175 | 0.890 | 1.877 |
| o025 | 85048 | 110 | 18 | 5.85 | 105 | 0.719 | 0.360 |
| trump_1e-06 | 75306 | 110 | 16 | 5.85 | 94 | 0.340 | 0.360 |

MEASURED: 1.9e5 boxes on Trump's support in 300 s took the widest core coordinate only from 2.877 to 0.25 (3.5 halvings) and the maximum depth plateaued at 36. EXTRAPOLATED: the depth needed is ~94-187 in a tree branching at 2^0.34..2^0.89 per level, i.e. 1e9..1e50 boxes. But this is the cost of NOT closing a structure that genuinely holds an FJ point  --  the certificate is FALSE there and no amount of box budget will change that. **For the structures where the certificate is TRUE (the census), the tier closes in ~40 boxes.**

## 3. The Trump canary (A76 Lemma K)

Method: descend the branch and bound always into the child that CONTAINS z-hat, running every leaf test on the way. If any test ever discharges that box the test is unsound.

* **no test ever excluded z-hat: True;**
* at depth 100 the epsilon-inflated Krawczyk test CONTRACTED and certified exactly one root. (Plain Krawczyk pins at ratio ~1.03 forever: bisecting around a root leaves the root on the box boundary and K straddles it. One Newton step from the midpoint plus a retest on an inflated box around the candidate is the standard remedy and is what the pilot uses.)
* refined root box max width **4.44e-15**, Krawczyk ratio **0.250**, cond **15.5** (well conditioned);
* the root's s-enclosure is **[3.877083590022812, 3.877083590022816]**  --  width 3.6e-15  --  which CONTAINS s-hat = 3.877083590022814 (True); s-hat minus the root midpoint = 0.

This is exactly the required output: **one isolated root at s = s-hat, Krawczyk contracts. Krawczyk IDENTIFIES z-hat, it never excludes it. THE CANARY PASSES.**

Controls: the same descent was run on all 19 A87 structures with the s window widened to cover their sigma and the row-activity slack set to each structure's own extraction tolerance. **No CERTIFIED-FJ (tight, tol 1e-6) structure was ever excluded.** The only exclusion was `o018`  --  LOOSE, not certified FJ, extraction tol 1e-4  --  at box scale ~1e-4, i.e. at its own row-activity slack, where the EXACT row system genuinely has no root. The flexible structures end at the depth cap without isolation, as they must: with m < D there is no square subsystem and the root set is positive-dimensional.

## 4. Cost model

```
total = N * c_triage  +  N * f_surv * c_FJ
```

All three factors MEASURED on the census population:

| factor | value |
|---|---|
| `c_triage` | 0.0136 s/structure (mean; p95 26.4 ms) |
| `f_surv` | 0.7750, 1 sigma [0.7591, 0.7902] |
| `c_FJ` | 0.9944 s/structure (mean over the calibration sample, CENSORED at the 20 s cap, so a LOWER bound); median of the 0.9533 that close: 0.04978 s |
| per structure | 0.7842 s (mean) / 0.05218 s (median-optimistic) |

| N | log10 triage CPU-h | log10 FJ CPU-h | log10 total CPU-h | x A85 upper (7,000) | log10 ratio |
|---|---|---|---|---|---|
| 1e11 (Level-0 graphs) | 5.58 | 7.33 | 7.34 | 3.11e+03 | 3.5 |
| 1e18 (decorated per-graph fan-out) | 12.58 | 14.33 | 14.34 | 3.11e+10 | 10.5 |
| 1e29 (decorated total) | 23.58 | 25.33 | 25.34 | 3.11e+21 | 21.5 |

**Break-even.** The route beats A85's 7,000 CPU-h only if the census has at most **N = 3.21e+07** structures. With the triage alone (c_FJ = 0, an unreachable idealisation) the ceiling is **N = 1.85e+09**. Both sit below the smallest census figure on the table (1e11 Level-0 graphs) by 3.5 and 1.7 orders of magnitude respectively, and 21 orders below the decorated total (1e29).

**A85 baseline** (attempts/A85-k0-route/notes/pilot_report.md, results/pilot_summary85.json): the tree pilot ran 12 of 26 planned budget-10 nodes  --  6 PASS, 5 FAIL, 1 refused  --  for `lp_seconds_total = 10363` and `cert_seconds_total = 5813`, i.e. ~1,350 s per node (~860 s LP + ~485 s cert), with per-node cost collapsing 3-4 corners deep: the S3 node `s3_near_BL619642_TR023305` cost 63.0 s LP + 4.3 s cert, and the S4 node needed only 8.7 s of cert time. Headline for the whole tree: **3,200-7,000 CPU-h**.

## 5. Findings

1. **On the CENSUS the triage kill is CONTAINMENT-type, not S-HAT.** 0.2250 of census structures are killed by T1b, and 0.9877 of those kills survive the side bound being dropped to `s <= 5`  --  i.e. T1b is mostly re-deriving A59's containment diagnosis, NOT doing new work with s-hat. Only 2 census kill in 720 used the side bound. (On the A87 set every kill is S-HAT-type, but that set is not the population: those structures are realised, at sigma above s-hat, so the side bound is the only thing that can kill them.) **The s-hat bound is nearly free at Tier 1.**
2. **Yes, F fires on fixed-structure boxes  --  where A87's menu version never did.** 2050 firings, 5.25% of leaf kills, on 4 of 150 calibration structures. It is not the workhorse (that is the rebuilt dominance side conditions at 67% and a-structure at 9%), but the menu really was part of A87's problem, and removing it recovers a working Gordan test.
3. **What limits the FJ tier is neither d_H nor hinge conditioning  --  it is whether the certificate is TRUE.** 0.9533 of census survivors close in ~33 boxes / ~50 ms. The ones that do not close are exactly the ones containing a genuine FJ point (Trump, the A87 realised points) plus 7 of 150 census stragglers, all with chi <= -2. Where the search must grind, the obstruction is box count set by the core dimension D = 24-34 (HC4 pins 5-15 coordinates then stalls, leaving 16-19 wide ones each needing ~5.9 halvings); hinge conditioning is fine (Krawczyk cond ~15 on Trump) and d_H on its own predicts nothing.
4. **The census is essentially all FLEXIBLE.** Only 2 of 720 census structures have chi >= 0. Any plan that leans on Krawczyk (A76's cheap rigid-grain discharge) applies to a vanishing share of the population; the route lives or dies on the flexible branch.
5. **HC4 and the rebuilt dominance rows are the two load-bearing pieces, and both are cheap.** Turning HC4 off leaves the box essentially uncontracted; dropping the dominance side conditions removes two thirds of all leaf kills. Neither costs measurable time. A future version should also propagate onto the TILT variables, which the current HC4 does not touch (the interval-linear form treats tilts as constants).
6. **The verdict is the census size.** Per structure this route is about 0.78 s all-in  --  genuinely cheap, and much cheaper than the 0.81 s/cell A87 measured for configuration cells. It still loses to A85 by 3 orders of magnitude at N = 1e11 and by 21 at N = 1e29, because N is 3-21 orders above the 3.2e+07 break-even. The dominant multiplier is **N**. Per the brief's own decision rule (win at <= 1e6, lose at >= 1e12), **H1-by-structure LOSES, and it loses on the count, not the price.**

## 6. Measured vs extrapolated

**MEASURED**: every triage number and bracket; the kill-type split; every tier-2 box count, wall time, ms/box, leaf histogram, depth, open-stack size and remaining-volume figure; the whole 150-structure cost calibration; the HC4 ablation; the entire canary including the root's s-enclosure; the Farkas positive/negative controls; the dominance-convention validation; the p88_iv-vs-mpmath agreement.

**EXTRAPOLATED**: boxes-to-completion and depth-needed for the structures that do NOT close (from the depth-branching fit); the total CPU-h at N = 1e11 / 1e18 / 1e29 (linear in N from the measured per-structure cost, with `c_FJ` a censored LOWER bound); the ~2-5x factor for an exact-rational Farkas certificate (quoted from A54/A59, not measured here).

**CAVEATS.** (i) The census sample carries A59's orbit-weight caveat, measured by the census chore at +3.3%%; the fractions here are over LABELLED draws. (ii) `c_FJ` is censored at the 20 s cap, so the mean is a lower bound  --  the true mean is larger and the verdict only gets stronger. (iii) The 6 lowest A87 structures are LOOSE probes, not certified FJ points, and are used only as near-rigid cost probes. (iv) Float intervals, not a certificate.

