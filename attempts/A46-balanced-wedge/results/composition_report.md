# A46 / W2 — the balanced-wedge table and the flush-free budget composition

Agent W2 (Opus), 2026-08-29. Repo `C:\Users\esumm\code\packing`.
Deliverables: `results/atlas_mismatch_audit.json`, `results/w_wc_table.json`,
`results/w_ce_cc_pilot.json`, `results/composition.json`, `results/canaries.json`,
this file. Code: `code/{a46_lib,task1_audit,task2_wc,task2_assemble,task3_compose,
task4_pilot,task4_assemble,task6_canaries,clip_util}.py` plus the A45 harness
(`a45_lib.py`, `dead_region.py`, `atlas_lib.py`, `wastage.py`, `exactify.py`,
`canary.py`) **copied verbatim**; nothing in A23/A25/A29/A37/A44/A45 was modified.

Constants: `s0 = 969271/250000 = 3.877084` exactly,
`B0 = s0^2 - 11 = 251986271441/62500000000 = 4.031780343056` exactly.

---

## 0. Headline

| | |
|---|---|
| smallest mismatch a **loaded** contact of a genuine critical point actually uses | **1.029 deg** (CE, family A37-NEW-0, forced row) |
| smallest over all atlas contacts | **0.196 deg** (CE, family 01, unloadable) |
| smallest **loaded WC** tilt | 33.896 deg |
| `w_WC` table | **11/11 bins EXACT** (869/869 tiles pass in Fractions, 0 failures) |
| `max w_WC` | **453/2048 = 0.221191** at phi in (40,45] |
| interior contacts | CE <= **0.007080** (exact); CC <= **0.070557** (exact), 0 when aligned |
| minimal flush-free profile, best case (delta_0 = 45) | **0.583** vs B0 = 4.032 — **short by x6.9** |
| richest profile allowed by the counting lemmas (11 loaded squares) | **2.014** — short by x2.0 |
| absolute maximum conceivable (12 WC + 23 interior, all maximal) | **4.277** (x1.06 B0) — the *only* fire zone |
| canaries (Trump + 12 atlas families) | **ALL PASS** (Trump 0.4849 <= 4.0318) |

**Verdict. No delta_0 fires for any minimal profile — the shortfall is x2 to x7 and
is not closable by table refinement. The fire zone is a five-point corner of the
count lattice requiring 12 wall contacts AND >= 20 sharp-wedge corner-corner
contacts, which no genuine critical point comes close to.** The composed theorem
W1(delta_0) AND W2(delta_0) does not close at n = 11, and task 1 independently
refutes W1's premise empirically.

---

## 1. Task 1 — the atlas mismatch audit (the empirical W1 verdict)

`results/atlas_mismatch_audit.json`. **FLOAT-ONLY** (the A37 atlas stores theta in
radians, so cos/sin are transcendental and no exact statement is available). All 12
genuine entries (1 RIGID, 9 VALLEY, 2 VALLEY-MARGINAL) — the same set A44 used —
were re-extracted geometrically (SAT, TOL = 1e-6) and every contact classified
WF / WC / FL / CE / CC. Loadability comes from re-running A44's lambda_0 = 1 FJ LP
on the family's physical rows (`eval_atlas.lp_block`, expanded-row fallback):
`forced` = lambda_min > 1e-7, `loadable` = lambda_max > 1e-7.

Mismatch conventions (the lead's corrected taxonomy is used throughout):
CE delta = dist(theta_a - theta_b, 90 Z) in (0,45]; WC delta = tilt = dist(theta, 90 Z);
CC reported by relative angle **and** by free-wedge angles.

| family | class | s | CE loaded min delta | WC loaded min | type counts (non-rattler) |
|---|---|---|---|---|---|
| 0 | RIGID | 3.877084 | 40.182 | 40.182 | WF 9, WC 2, FL 7, CE 6, CC 1 |
| 1 | VALLEY | 3.885618 | 45.000 | — | WF 8, WC 2, FL 7, CE 6 |
| 2 | VALLEY | 3.885618 | 45.000 | — | WF 8, WC 1, FL 7, CE 5 |
| 6 | VALLEY | 3.886746 | 41.565 | 41.565 | WF 10, WC 1, FL 7, CE 5, CC 1 |
| 13 | VALLEY | 3.897231 | 33.896 | 33.896 | WF 6, WC 3, FL 7, CE 3, CC 1 |
| 14 | VALLEY | 3.897231 | 33.896 | 33.896 | same as 13 |
| 27 | VALLEY-MARGINAL | 3.925149 | LP infeasible | — | WF 9, WC 1, FL 3, CE 8 |
| 31 | VALLEY | 3.936964 | **2.272** | 42.062 | WF 8, WC 2, FL 4, CE 7 |
| A37-NEW-0 | VALLEY | 3.902674 | **1.029** | 43.677 | WF 8, WC 1, FL 4, CE 9, CC 1 |
| A37-NEW-1 | VALLEY-MARGINAL | 3.912232 | LP infeasible | — | WF 9, FL 3, CE 8, CC 1 |
| A37-NEW-2 | VALLEY | 3.924402 | 22.422 | 38.441 | WF 7, WC 2, FL 5, CE 5, CC 1 |
| A37-NEW-3 | VALLEY | 3.925470 | **7.106** | 41.325 | WF 9, WC 1, FL 4, CE 7 |

GLOBAL minima: **CE loaded 1.029 deg, CE all 0.196 deg, WC loaded 33.896 deg,
CC always exactly 0** (all 7 atlas CC contacts are the ALIGNED diagonal type,
free wedges exactly 90/90 — the lead's zero-charge class, confirmed).

**Empirical verdict on W1.** Genuine critical points *do* realise near-flush loaded
corner-on-edge contacts: family A37-NEW-0 carries a **forced** CE row at delta =
1.029 deg, family 31 one at 2.272 deg, and A37-NEW-3 one at 7.106 deg. Any
delta_0 above ~1 deg is refuted by measurement; the largest delta_0 not yet
contradicted by a *loaded* contact is 1.029 deg, and by *any* contact 0.196 deg.
This is consistent with (and independent of) the lead's local refutation via the
bridge/brace mechanisms. Consistency check passed: for all 72 CE contacts the
corner-tilt-mod-90 equals the relative-angle mismatch.

Caveat: the two VALLEY-MARGINAL families have an infeasible lambda_0 = 1 LP
(A44's expected behaviour), so their contacts are `unknown`, not `loaded`. Their
smallest CE mismatches (3.628 and 3.449 deg) are excluded from the "loaded"
minima above; including them would not change the verdict.

---

## 2. Task 2 — the certified `w_WC(phi)` table

`results/w_wc_table.json`. Frame: A45's WC frame — big container S = 20, square
corner at p = (10,0) on the bottom wall, tilt phi D4-reduced to (0,45], Lemma-P'
wall-mode margins asserted on every run, `PlacedBox` bin-uniform over **nsub = 4**
tilt sub-boxes with outward-rounded rational (cos,sin) hulls. **No moat, no
rho_min clip**: the full dead region is mapped over the window
`x in [10 - 13/8, 10 + 13/8], y in [0, 5/4]` (both >= the brief's 1.6 / 1.2),
quadtree `cell0 = 1/8` down to `min_cell = 1/64`, undecided tiles dropped.
Lemma-K discipline: only tiles inside `slab(wall, along-wall bbox of the square)`
= `[10 - min sin phi, 10 + min cos phi] x [0, min(cos+sin)]` are kept
(`a45_lib.keeper_wc` verbatim), which is what makes each entry
container-independent and along-wall composable.

**Every entry is exact.** The identical tile lists were re-certified in pure
Fraction arithmetic (`a45_lib.recert_exact`, depth 34, 200k boxes):
**869/869 tiles pass, 0 failures**, ~15 s per bin.

| phi bin (deg) | w_WC (exact) | float | tiles | status |
|---|---|---|---|---|
| (0.5, 1] | 0 | 0.000000 | 0 | exact (vacuous — no tile certifies at 1/64) |
| (1, 2] | 5/4096 | 0.001221 | 5 | exact |
| (2, 5] | 35/4096 | 0.008545 | 32 | exact |
| (5, 10] | 115/4096 | 0.028076 | 37 | exact |
| (10, 15] | 265/4096 | 0.064697 | 70 | exact |
| (15, 20] | 105/1024 | 0.102539 | 84 | exact |
| (20, 25] | 141/1024 | 0.137695 | 102 | exact |
| (25, 30] | 691/4096 | 0.168701 | 115 | exact |
| (30, 35] | 799/4096 | 0.195068 | 136 | exact |
| (35, 40] | 435/2048 | 0.212402 | 141 | exact |
| (40, 45] | **453/2048** | **0.221191** | 147 | exact |

Cross-reference: A23 notes 4a (s = 3.85, X0 = 1.6, single tilt, no bin uniformity,
no Lemma K) gives 0.1887 at 20 deg and 0.3584 at 35 deg. Our (20,25] = 0.1377 and
(30,35] = 0.1951 are the bin-uniform, plane-mode, slab-restricted lower bounds of
the same object; the gap is the uniformity cost plus the 1/64 resolution floor.

**Radial profile** (exact area of the certified tiles within sup-distance r of p;
tiles clipped exactly). This is the input the disjointification needs:

| phi bin | r=1/8 | 1/4 | 1/2 | 3/4 | 1 | 8/5 |
|---|---|---|---|---|---|---|
| (1,2] | 0 | 0 | 0 | 0 | 0.00122 | 0.00122 |
| (2,5] | 0 | 0 | 0.00049 | 0.00439 | 0.00854 | 0.00854 |
| (5,10] | 0.00024 | 0.00024 | 0.00537 | 0.01611 | 0.02808 | 0.02808 |
| (10,15] | 0.00464 | 0.00635 | 0.01929 | 0.04346 | 0.06470 | 0.06470 |
| (15,20] | 0.00977 | 0.01904 | 0.04004 | 0.07812 | 0.10254 | 0.10254 |
| (20,25] | 0.00903 | 0.03467 | 0.06543 | 0.11768 | 0.13770 | 0.13770 |
| (25,30] | 0.00830 | 0.04443 | 0.09424 | 0.16211 | 0.16870 | 0.16870 |
| (30,35] | 0.00757 | 0.04443 | 0.12671 | 0.19458 | 0.19507 | 0.19507 |
| (35,40] | 0.00684 | 0.04297 | 0.15967 | 0.21240 | 0.21240 | 0.21240 |
| (40,45] | 0.00659 | 0.04077 | 0.18628 | 0.22119 | 0.22119 | 0.22119 |

**Every entry is entirely contained in the sup-ball of radius 1 about the contact
point** (radius 3/4 for phi > 30). Two WC contacts on the same wall whose contact
points are >= 2 apart therefore have automatically disjoint regions.

**Lemma-K costs nothing here.** The same three bins re-mapped with the keeper
disabled (`code/task4_pilot.py --what probe`, `work/wc_probe.json`) give
*identical* areas 0.221191 / 0.137695 / 0.008545. The whole plane-dead region in
this window already lies inside the square's own wall slab, so the container-
independence discipline is free — unlike A45, where the moat cost a factor ~8.

---

## 3. Task 4 — the CE / CC pilot

`results/w_ce_cc_pilot.json`. A45's CE frame (a's corner at p = (10,10); b upright
with top edge on y = 10; slide u), A45's CC frame (a = [10,11]^2, b's cone
[delta, delta+90]); **full window** `B_inf(p, 5/4)` (>= the brief's 1.2), Lemma-K
keeper = `conv(guaranteed subset of a cup b)` (`a45_lib.keeper_hull` verbatim),
nsub = 6 (CE also nsub_u = 4, so 24 sub-boxes per bin), middle slide bin
u in [-1/4, 1/4], cell0 = 1/8, min_cell = 1/64.

| entry | parameter | area | status |
|---|---|---|---|
| CE (2,5] | mismatch 2-5 deg | 0 | float |
| CE (18,21] | mismatch 18-21 deg | 13/4096 = 0.003174 | float |
| CE (39,42] | mismatch 39-42 deg | **29/4096 = 0.007080** | **exact** (0/20 fail) |
| CC delta (177,180] | free wedge 87-90 (ALIGNED) | 0 | float |
| CC delta (170,177] | free wedge 80-87 | 0 | float |
| CC delta (160,170] | free wedge 70-80 | 15/4096 = 0.003662 | float |
| CC delta (135,145] | free wedge 45-55 | 115/2048 = 0.056152 | **exact** (0/44 fail) |
| CC delta (110,120] | free wedge 20-30 | **289/4096 = 0.070557** | **exact** (0/58 fail) |

**Convention correction (recorded).** For CC the governing parameter is **not**
the relative angle mod 90 but the **sharp free-wedge angle** `min(delta-90,
270-delta)`: bins CC(160,170] and CC(110,120] have the *same* mismatch (20 deg)
and areas differing by 19x. The A46 CC table is therefore indexed by wedge angle.
The aligned diagonal CC (wedge 90/90) certifies **exactly 0**, confirming the
lead's zero-charge class and A45's structural CC result from the other direction.

**Magnitude verdict.** The lead's estimate that interior contacts charge only
~0.01-0.04 is confirmed and improved for CE (<= 0.0071, i.e. **31x smaller** than
one maximal wall wedge). It is *not* right for sharp-wedge CC, which reaches
0.0706 — still 3.1x smaller than a wall wedge, but it is the only interior number
that can reach the fire zone (section 5).

---

## 4. Task 5 — the disjointification actually used

`code/clip_util.py`. All arithmetic exact Fractions.

**(a) Same wall (Voronoi truncation).** Let WC contacts on one wall have
along-wall coordinates `X_1 < ... < X_r`. Truncate contact i's region to the
along-wall interval `[(X_{i-1}+X_i)/2, (X_i+X_{i+1})/2]` (half-gaps; the two ends
run to the container corners). Voronoi cells of distinct points are disjoint, so
the truncated regions are pairwise interior-disjoint; truncation only removes
area, so each truncated area is still a certified lower bound.
`clip_util.clip_x(cells, px, x_lo, x_hi)` computes the truncated area exactly from
the task-2 tile list; `wall_profile_sum` does the whole wall.

Applied to the strongest bin (40,45] on a wall of length s0, with r contacts
evenly spread over `[0, s0]` (the spread that maximises the untruncated sum):

| r | truncated total | untruncated |
|---|---|---|
| 1 | 0.221191 | 0.221191 |
| 2 | 0.442383 | 0.442383 |
| 3 | 0.663574 | 0.663574 |
| 4 | 0.884294 | 0.884766 |
| 5 | **0.931738** | 1.105957 |
| 6 | 0.782910 | 1.327148 |

Truncation is inert up to r = 3 (spacing 1.939 exceeds twice the 3/4 reach), and
saturates at 0.9317 per wall. Under the wall-incidence cap N1 <= 12 the best
distribution is (3,3,3,3), total **2.654297 = 12 x 453/2048** — i.e. at N1 <= 12
the along-wall crowding is *not* the binding constraint.

**(b) Different walls.** Every kept tile is within `5/4` of its own wall (window
cap; in fact within `min(cos+sin) <= sqrt 2`). *Opposite* walls: the two slabs are
disjoint because `2 x 5/4 = 5/2 < s0 = 3.877`. *Adjacent* walls: the two slabs
meet exactly in the `5/4 x 5/4` container-corner box. Two sound handlings are
implemented:
  * `corner_overlap(...)` returns the area each region places inside the shared
    corner box; deducting `min` of the two, once per container corner, restores
    disjointness (a **deduction, labelled**, never an assumption);
  * `diagonal_split_area(...)` keeps only the part of each region on its own side
    of the corner box's diagonal, making adjacent-wall regions exactly disjoint
    with no deduction (tile-wise, conservative).
The section-5 caps above use **no** deduction, so they are upper bounds — the
correct direction for the "maximum conceivable" argument. For the *lower*-bound
direction (does a given profile fire) the deduction must be applied; in every
profile of section 5 the wall contacts are far enough apart that it vanishes.

Worked check on Trump: his two WC contacts are on *adjacent* walls (top wall at
x = 1.5957, right wall at y = 1.8771); each is >= 2.0 from the shared top-right
corner, hence >= 1.25 clear of the corner box, so both regions are used whole and
the corner deduction is 0.

---

## 5. Task 3 — the composition verdict

### (a) Honest minimum contact counts of a flush-free loaded core

Flush-free means: every wall contact is WC (a corner on the wall with tilt in
(0,45]; tilt 0 with a corner on the wall would be a WF flush) and every
square-square contact is CE or CC (a corner on an edge with mismatch exactly 0
mod 90 and the contact point in the edge interior is *automatically* a flush
segment contact). So in the support graph H **every edge carries exactly one row**,
and H-degree = number of incident H-edges.

Ingredients, proved lemmas only:
* **L1** (`docs/proofs/structure_lemmas.md`): every loaded square has H-degree >= 2.
* **L6**: `lambda_0 > 0` forces, per binding axis, ONE connected component of H
  touching both of that axis's walls; span count at s0 gives `>= 3` loaded squares
  and `>= 2` wall contacts per binding axis. (The `lambda_0 = 0` branch is a global
  compression self-stress and is a separate branch, not covered here — GAP.)
* **L7**: on a binding axis both extreme containment rows are active.
* **L2**: degree-2 chains are admissible as flagged **thin** branches.
* **L11** (A44 `notes/theory.md`, proved on the non-thin branch): with no flush
  rows, every loaded square has H-degree >= 3; handshake `2 E_pp + E_pw >= 3 k_H`.
* **L5(b)**: no square touches two opposite walls; adjacent (corner square) is fine.
* **L4** (planarity): `E <= 3(k+4) - 6`.

Minimisation. Thin branch: the 3-square chain A-B-C with A on `W_left`, C on
`W_right` gives every square degree exactly 2 — **4 contacts, 2 WC + 2 interior**.
That is the true minimum; 17 is not assumed anywhere. Non-thin branch: minimise
`E = E_pp + E_pw` subject to `2 E_pp + E_pw >= 3 k_H`, `E_pp <= C(k_H,2)`,
`E_pw >= 2` (or 4 if both axes bind):

| k_H | 1 axis: min E | (E_pw, E_pp) | 2 axes: min E | (E_pw, E_pp) |
|---|---|---|---|---|
| 3 | **6** | (3, 3) | **7** | (4, 3) |
| 4 | 7 | (2, 5) | 8 | (4, 4) |
| 5 | 9 | (2, 7) | 10 | (4, 6) |
| 6 | 10 | (2, 8) | 11 | (4, 7) |
| 11 (all loaded) | 20 | (2, 18) | 20 | (4, 16) |

So the honest non-thin minimum is **6 contacts (3 WC + 3 interior)** at k_H = 3.

### (b) Certified budget sums, per profile and per delta_0

Wall contacts priced at `w_WC` of the *lowest bin still admitted* when every tilt
is >= delta_0; interior contacts priced at the maximum measured interior value
(0.070557, the sharp-wedge CC — the most generous choice). `B0 = 4.0318`.

| profile | n_WC | n_int | d0=1 | 2 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| THIN-1AXIS | 2 | 2 | 0.141 | 0.144 | 0.158 | 0.197 | 0.271 | 0.346 | 0.417 | 0.479 | 0.531 | 0.566 | 0.583 |
| THIN-2AXES | 4 | 2 | 0.141 | 0.146 | 0.175 | 0.253 | 0.400 | 0.551 | 0.692 | 0.816 | 0.921 | 0.991 | 1.026 |
| NONTHIN k_H=3 | 3 | 3 | 0.212 | 0.215 | 0.237 | 0.296 | 0.406 | 0.519 | 0.625 | 0.718 | 0.797 | 0.849 | 0.875 |
| NONTHIN k_H=4 | 2 | 5 | 0.353 | 0.355 | 0.370 | 0.409 | 0.482 | 0.558 | 0.628 | 0.690 | 0.743 | 0.778 | 0.795 |
| NONTHIN k_H=5 | 2 | 7 | 0.494 | 0.496 | 0.511 | 0.550 | 0.623 | 0.699 | 0.769 | 0.831 | 0.884 | 0.919 | 0.936 |
| NONTHIN k_H=3, 2 axes | 4 | 3 | 0.212 | 0.217 | 0.246 | 0.324 | 0.470 | 0.622 | 0.762 | 0.886 | 0.992 | 1.061 | 1.096 |
| NONTHIN k_H=11 (all loaded) | 4 | 16 | 1.129 | 1.134 | 1.163 | 1.241 | 1.388 | 1.539 | 1.680 | 1.804 | 1.909 | 1.979 | 2.014 |

(`w_WC` used: d0=1 -> 0 [bin (0.5,1]], 2 -> 0.001221, 5 -> 0.008545, 10 -> 0.028076,
15 -> 0.064697, 20 -> 0.102539, 25 -> 0.137695, 30 -> 0.168701, 35 -> 0.195068,
40 -> 0.212402, 45 -> 0.221191.)

**Nothing fires.** At the most favourable possible threshold delta_0 = 45 (i.e.
every corner contact forced to the maximal 45-deg mismatch — far beyond anything
W1 could ever prove) the shortfall factors against B0 are:

| profile | sum at d0=45 | shortfall |
|---|---|---|
| THIN-1AXIS | 0.583 | **x6.91** |
| NONTHIN k_H=4 | 0.795 | x5.07 |
| NONTHIN k_H=3 | 0.875 | x4.61 |
| NONTHIN k_H=5 | 0.936 | x4.31 |
| THIN-2AXES | 1.026 | x3.93 |
| NONTHIN k_H=3, 2 axes | 1.096 | x3.68 |
| NONTHIN k_H=11 (all loaded) | 2.014 | **x2.00** |

### (c) The maximum conceivable

Caps used: `N1 <= 12` wall incidences (A45 sect. 9), total contacts `<= 3k+2 = 35`
(A31 L4a) at k = 11, hence `<= 23` interior contacts.

| interior model | wall model | total | vs B0 |
|---|---|---|---|
| CE only (<= 0.007080) | 12 x max w_WC | 2.8171 | 0.699 — **inert** |
| CE only | best N1-capped Voronoi distribution (3,3,3,3) | 2.8171 | 0.699 — **inert** |
| CE only | 4 x unconstrained per-wall cap (violates N1) | 3.8898 | 0.965 — inert |
| worst interior (0.070557 sharp-wedge CC) | 12 x max w_WC | **4.2771** | **1.061 — FIRES** |
| worst interior | best N1-capped Voronoi (3,3,3,3) | 4.2771 | 1.061 — FIRES |
| worst interior | 4 x unconstrained per-wall cap (violates N1) | 5.3498 | 1.327 — FIRES |

**If every interior contact is a CE, no flush-free profile can ever exceed B0 —
the maximum conceivable is 2.817 = 0.70 B0.** That is a table-independent ceiling
of exactly A45's Ceiling-2 type, one order of magnitude less severe but still
binding: a CE-only flush-free structure is unkillable by any dead-area argument
built from these per-contact certificates.

### (d) The fire zone, exactly

`{(n_WC, n_int) : n_WC * 0.221191 + n_int * 0.070557 > 4.031780}` intersected with
`n_WC <= 12`, `n_WC + n_int <= 35` is exactly **five points**:

| n_WC | n_int | sum |
|---|---|---|
| 11 | 23 | 4.0559 |
| 12 | 20 | 4.0654 |
| 12 | 21 | 4.1360 |
| 12 | 22 | 4.2065 |
| 12 | 23 | 4.2771 |

Every one of them requires simultaneously: (i) the wall-incidence count at or
within one of its absolute maximum, (ii) **every** wall contact at tilt in
(40,45], and (iii) **at least 20** interior contacts that are all corner-corner
with sharp free wedge in (20,30]. For comparison, across the whole genuine atlas
the maximum wall-contact count is 3 and the maximum CC count is 1 (and every
realised CC is aligned, i.e. worth exactly 0). Trump has 2 WC and 1 aligned CC.
The fire zone is therefore a fantasy corner of the count lattice, not a structure
class; and reaching it would in any case require 20+ CC regions of extent ~1 to be
pairwise disjoint inside 4.03 of free area, which is self-defeating.

**Answer to the brief's question "the smallest delta_0 for which minimal profiles
die": there is none.** Not at delta_0 = 45, not with any refinement of the table
that respects the measured intrinsic dead areas (section 2's no-keeper probe shows
the table is already at the intrinsic maximum in this window). The honest expected
answer stands: *no delta_0 suffices for minimal profiles; the fire zone is
wall-rich (in fact wall-maximal AND CC-maximal) profiles only.*

---

## 6. Task 6 — canaries (`results/canaries.json`) — ALL PASS

Two pricing models: `table` (A45's min-over-covering-bins convention; uncovered
parameters priced 0) and `upper` (every CE priced at the maximum measured CE and
every CC at the maximum measured CC, regardless of its own parameter — the
stronger test). Both ignore disjointness between regions, which can only
overstate. A violation would be a soundness bug.

**Trump** (exact Fraction extraction, `canary.py` verbatim, A43 TOL = 1e-6):
25 contacts — WF 9, WC 2, FL 7, CE 6, CC 1. Both WC contacts at tilt 40.1819 deg
(bin (40,45]), all six CE at mismatch 40.1819 deg, the CC aligned (wedge 90).

    sum(table) = 0.484863    sum(upper) = 0.555420    B0 = 4.031780    PASS / PASS
    (2 x 0.221191 + 6 x 0.007080 + 0)      capture 12.0% of the budget

**Atlas valleys at their own s** (float extraction; budget `s^2 - 11`):

| family | s | budget | table | upper | |
|---|---|---|---|---|---|
| 0 (RIGID) | 3.877084 | 4.0318 | 0.4849 | 0.5554 | PASS |
| 1 | 3.885618 | 4.0980 | 0.4424 | 0.4849 | PASS |
| 2 | 3.885618 | 4.0980 | 0.2212 | 0.2566 | PASS |
| 6 | 3.886746 | 4.1068 | 0.2566 | 0.3271 | PASS |
| 13 | 3.897231 | 4.1884 | 0.5852 | 0.6770 | PASS |
| 14 | 3.897231 | 4.1884 | 0.5852 | 0.6770 | PASS |
| 27 | 3.925149 | 4.4068 | 0.2637 | 0.2778 | PASS |
| 31 | 3.936964 | 4.4997 | 0.4424 | 0.4919 | PASS |
| A37-NEW-0 | 3.902674 | 4.2309 | 0.2283 | 0.3555 | PASS |
| A37-NEW-1 | 3.912232 | 4.3056 | 0.0103 | 0.1272 | PASS |
| A37-NEW-2 | 3.924402 | 4.4009 | 0.4248 | 0.5308 | PASS |
| A37-NEW-3 | 3.925470 | 4.4093 | 0.2637 | 0.2708 | PASS |

Maximum realised capture anywhere: **14.0%** of the budget (families 13/14). The
table is sound and it is between 7x and 100x too weak to kill a real structure —
but note that this is ~**280x** stronger per contact than A45's charge table
(0.221 vs 6.26e-4), so the loss is entirely in the count, not in the certificate.

---

## 7. Gap list (everything float-only, every dropped class, every judgment call)

**Float-only (never entering a shipped verdict):**
1. The *entire* task-1 atlas audit — the A37 atlas stores theta in radians.
   Contact classification, mismatch values, and loadability (A44's LP is float
   scipy/HiGHS with `LP_TOL = 1e-7`, `RANK_TOL = 1e-9`) are all float64. The
   W1 empirical verdict is a **measurement**, not a theorem.
2. Task-4 CE bins (2,5] and (18,21], and CC bins (177,180], (170,177], (160,170]
   — float mode. CE (39,42], CC (135,145], CC (110,120] are exact.
3. Atlas canary rows in section 6 (float extraction). Trump's row is exact.
4. The `quick_cover` screening and the failed quadtree splits inside the float
   maps — search only; every shipped tile was re-derived in Fractions.

**Dropped tile classes (all lower the number, all sound):**
5. Tiles that reach `min_cell = 1/64` without certifying (`n_drop`, 0-1452 per
   bin). At small phi this is the whole story: bin (0.5,1] certifies **0** because
   the true dead strip under a 1-deg-tilted square is thinner than 1/64. A finer
   `min_cell` would raise the small-phi entries — it cannot change the verdict
   (their true area is ~sin phi / 2 <= 0.009 at 1 deg).
6. Tiles outside the Lemma-K keeper (`n_key`). Measured cost: **zero** in this
   window (section 2's no-keeper probe).
7. Tiles overlapping the hypothesis square (`n_occ`) — correctly excluded, dead
   area must be empty area.
8. The window itself: the maps stop at sup-radius 13/8 (WC) and 5/4 (CE/CC).
   Measured irrelevant for WC (every entry is contained in the sup-ball of radius
   1); **not** verified for CE/CC, where far-field dead area may exist outside
   `conv(a cup b)` and is dropped by Lemma K. Since the composition's binding
   constraint is the wall term, this only makes the interior numbers pessimistic —
   which weakens the fire zone, not the "nothing fires" verdict. **GAP-A46-W2-1.**

**Convention / judgment calls:**
9. Window sizes rounded *outward* to dyadic-compatible values: 13/8 = 1.625 for
   the brief's 1.6, and 5/4 = 1.25 for the brief's 1.2. Larger window, so sound.
10. `nsub = 4` for WC (the brief asks >= 4); nsub = 6 (+ nsub_u = 4) for CE/CC as
    in A45. Coarser sub-binning only weakens.
11. CE slide bin taken as u in [-1/4, 1/4] ("the middle slide bin"), i.e. the
    union of A45's two central u-bins, covered by nsub_u = 4 sub-boxes.
12. **CC is indexed by sharp free-wedge angle, not by mismatch mod 90.** This
    departs from the brief's wording and is forced by the data (section 3).
13. The `delta_0` sweep prices a wall contact at the lowest bin whose *upper*
    endpoint is >= delta_0. E.g. delta_0 = 40 admits bin (35,40] and is priced
    0.212402, not 0.221191. Conservative and correct.
14. `N1 <= 12` is quoted from A45 sect. 9 (citing A31); it was **not**
    re-derived here. `3k+2 = 35` from A31 L4a, likewise quoted.
15. The per-wall Voronoi caps use contact points evenly spread over `[0, s0]` and
    the strongest bin for all r contacts. This maximises the untruncated sum; it
    is not a proof that no other placement does better, so the number 0.9317 is an
    *empirical* maximum over that one-parameter family. It is not load-bearing:
    at `N1 <= 12` the binding cap is `12 x max w_WC`, which needs no truncation
    argument at all. **GAP-A46-W2-2.**
16. Adjacent-wall corner overlap is handled by an *implemented but unexercised*
    deduction/diagonal-split (section 4); in every profile evaluated the wall
    contacts are far enough apart that it is 0. For a hypothetical fire-zone
    structure with 3 contacts per wall it would have to be applied and would only
    lower the sum. **GAP-A46-W2-3.**
17. The `lambda_0 = 0` branch of L6 (a global compression self-stress) is not
    covered by the profile enumeration; L6 gives no wall contacts there, so the
    wall term could be 0 and the composition is vacuous on that branch.
    **GAP-A46-W2-4** (inherited from the structure-lemmas ledger).
18. The minimum-count derivation assumes only L1/L2/L5b/L6/L7/L11 + planarity. It
    does **not** check that the minimal profiles are geometrically realisable at
    s0 — they need not be; they are used as *lower* bounds on the contact count,
    which is the direction the argument needs.

**Not done (levers, not gaps):**
19. Finer `min_cell` (1/128, 1/256) on the small-phi bins.
20. A full CE/CC sweep on a fine grid (only 3 CE + 5 CC pilot bins exist).
21. Multi-square hypotheses (an interface + its wall, A23 4b's corner
    configuration certified 0.34-0.54 for ONE square touching two walls — roughly
    2.4x the single-wall wedge, and a genuinely different, stronger primitive that
    A46 did not table). **This is the one direction that could move the numbers.**
