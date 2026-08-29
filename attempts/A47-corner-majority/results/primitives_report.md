# A47 leg (b) — the I-L18 CORNER and SIDE primitive tables

Agent B (Opus), 2026-08-29. Work confined to `attempts/A47-corner-majority/`; the A45/A46/A23 harness (`a45_lib`, `dead_region`, `wastage`, `atlas_lib`, `exactify`, `clip_util`, `canary`) copied VERBATIM into `code/`; nothing outside A47 touched (A29 included). Ships `results/primitives_{corner,side}.json`, `pair_pilot.json`, `primitive_canaries.json`, this file; per-entry checkpoints in `work/{corner,side}/`. `s0 = 969271/250000`, `B0 = s0^2 - 11 = 4.031780343056`.

## 1. Conventions
* **Frame**: the REAL container `[0,s0]^2` (not A45's plane-mode S=20 box). Reference corner = origin, reference wall = `x=0`; container containment is part of every certificate, so these primitives are container-specific and the four corners/walls are related by the exact D4 symmetry (which the canary uses).
* **Hypothesis**: ONE unit square, centre in a rational position cell, tilt in a degree bin, **placement-uniform** (`PlacedBox`, A14/A25 core-box semantics) — every certificate holds for EVERY placement of (cell x bin). `nsub >= 4` tilt sub-boxes with OUTWARD-rounded rational (cos,sin) hulls.
* **Keeper**: a tile counts iff it is in the window, interior-disjoint from EVERY placement (exact interval SAT), and certified dead on EVERY retained sub-box. Quadtree `cell0 = 1/8` down to `min_cell = 1/64`; undecided tiles DROPPED, so every number is a certified LOWER bound.
* **Exactness**: float map (outward eps) for SEARCH only; the identical shipped tile list re-certified in pure Fractions — **0 failures out of 7049 corner + 250 side tiles**.
* **Zones**: A21's zones are stated in the 3.88-normalised frame; mapping to s0 scales centres by `s0/(97/25) = 0.999249` toward the corner, so the position boxes are ENLARGED to contain the mapped zones: corner `[49/100,11/10]^2`, side `[49/100,11/10] x [109/100,139/50]`.

## 2. TABLE (i) CORNER — 54 entries, 5 INFEASIBLE, 0 tile failures, window `[0,13/8]^2`
Each cell is `theta-value / delta-value`: `theta` = actual tilt in [0,45]; `delta = dist(theta, 90 Z)` (derived exactly, sect. 3 — this is the one a consumer that only knows the mismatch may use).

| cx x cy \ bin (deg) | [0,1] | (1,5] | (5,15] | (15,30] | (30,40] | (40,45] |
|---|---|---|---|---|---|---|
| [.49,.7] x [.49,.7] | **0 / 0** | .0012/.0002 | .0479/.0107 | .1770/.0703 | .4050/.2961 | **INF** |
| [.49,.7] x [.7,.9] | .1753/.1748 | .1653/.1538 | .1697/.1177 | .2249/.1013 | .3140/.2188 | **INF** |
| [.49,.7] x [.9,1.1] | .3472/.3462 | .3350/.3215 | .3477/.2881 | .4153/.2930 | .5032/.4023 | **INF** |
| [.7,.9] x [.49,.7] | .1748/.1748 | .1729/.1538 | .1846/.1177 | .2227/.1013 | .3145/.2188 | **INF** |
| [.7,.9] x [.7,.9] | .3899/.3887 | .3716/.3396 | .3218/.2351 | .2505/.1177 | .2522/.1797 | .2947/.2695 |
| [.7,.9] x [.9,1.1] | .6016/.6006 | .5801/.5449 | .5310/.4380 | .4568/.3313 | .4502/.3835 | .4937/.4702 |
| [.9,1.1] x [.49,.7] | .3462/.3462 | .3420/.3215 | .3540/.2881 | .4146/.2930 | .5005/.4023 | **INF** |
| [.9,1.1] x [.7,.9] | .6021/.6006 | .5786/.5449 | .5232/.4380 | .4641/.3313 | .4614/.3835 | .4949/.4702 |
| [.9,1.1] x [.9,1.1] | .8540/.8523 | .8245/.7861 | .7717/.6799 | .7117/.5867 | .7004/.6277 | .7310/.7104 |

**theta-table min 0, max 0.8540; delta-table min 0, max 0.8523.** Exact Fractions, per-entry feasibility records and radial profiles are in `primitives_corner.json`.

**Near-flush entry `[0,1] deg x [49/100,7/10]^2` (`C_x0_x0_b0_1`, load-bearing) = EXACTLY 0** — zero tiles, zero at every radius, in both indexings. A near-upright square wedged into the corner cell strands nothing at 1/64 resolution: the corner primitive does NOT fire on it. It fires only once the square is pushed off the corner (`x0 x x1` at 0 deg already gives 0.175) or tilted (`x0 x x0` reaches 0.405 at (30,40]).

Cross-check vs A23-4b (0.34-0.61 at s = 3.85, single tilt, corner-touching square): our corner-touching cell `x0 x x0` gives **0.405** at (30,40] and 0.177 at (15,30] — inside / just below that band, the difference being bin-uniformity over a 0.21x0.21 cell and a 10-15 deg bin. Mid-position `x1 x x1` = 0.25-0.39, `x2 x x2` = 0.70-0.85. Radial (sup-distance from the corner): `C_x1_x1_b40_45` 0.2947 total with 0.1958 inside r = 1/2; `C_x2_x2_b40_45` 0.7310 with 0.2500 inside 1/2 and 0.6699 inside 5/4.

## 3. Feasibility structure (geometry, not failure) and the delta derivation
A placement needs `cx, cy >= w(theta)/2`, `w = cos+sin`. Over a tilt sub-box `w >= wlo = min(w(t0),w(t1))`, so the centre box may be shrunk to `[max(x0,wlo/2), x1] x [max(y0,wlo/2), y1]` WITHOUT excluding any realisable placement; an empty shrunk box is vacuous and is dropped.
* **INFEASIBLE (5 entries)**: every entry with a `[49/100,7/10]` cell on either axis in bin `(40,45]`. `w(40 deg)/2 = 0.7047 > 0.7`: a square tilted >= 40 deg cannot sit within 0.7 of a wall. **Near-corner cells force near-upright tilt** — the structure the composition has to respect.
* **PARTIAL (31 entries)**: every `[49/100,7/10]` cell (its lower edge is always clipped up to `wlo/2 >= 1/2`), plus bin `(30,40]` where the sub-bin `(37.5,40]` drops entirely, plus `(30,40]`/`(40,45]` on `[7/10,9/10]` cells (clipped, no sub-bin dropped).
* The zone enlargement `[1/2,..] -> [49/100,..]` is **vacuous for the corner table** — the feasibility clip already forces `cx, cy >= 1/2`. It is NOT vacuous on the side table's `cy` axis, where it was applied.
* **delta-table**: `delta in [a,b]` is the UNION of the theta-components `[a,b]` and `[90-b,90-a]`; a tile is dead for the union iff dead for both. `sigma:(x,y)->(y,x)` maps `(A,B,theta)` to `(B,A,90-theta)`, so the second component's dead set is the reflection of entry `(iy,ix,ib)`'s, and the delta-table is their EXACT rectangle-by-rectangle intersection. This is why all NINE cells were computed: the brief's "6 + fill by diagonal symmetry" is unavailable at fixed theta-bin, because sigma flips the bin.

## 4. TABLE (ii) SIDE (left wall) — 63 entries, 0 tile failures. **The side primitive is essentially inert.**
The brief's coarse `cy` cells (0.71 and 0.98 tall) certify **exactly 0 everywhere**: over so tall a centre range no tile is dead for every placement. The table was therefore REFINED to 7 `cy` cells of height 0.21-0.25 (window `[0,13/8] x [cy_cell +- 13/8]` cap container; the coarse cells are then derived EXACTLY as intersections of the refined dead sets — all 0). Even refined, only 5 of 63 entries are nonzero:

| entry | cx cell | cy cell | tilt bin | area | area with x <= 5/4 |
|---|---|---|---|---|---|
| S_x2_c6_s0_1 | [.9,1.1] | 2.54-2.78 | [0,1] | **0.1253** | 0.1180 |
| S_x2_c6_s1_15 | [.9,1.1] | 2.54-2.78 | (1,15] | 0.0719 | 0.0711 |
| S_x2_c0_s0_1 | [.9,1.1] | 1.09-1.30 | [0,1] | 0.0583 | 0.0498 |
| S_x2_c0_s1_15 | [.9,1.1] | 1.09-1.30 | (1,15] | 0.0471 | 0.0388 |
| S_x2_c6_s15_45 | [.9,1.1] | 2.54-2.78 | (15,45] | 0.0102 | 0.0102 |

All five sit at the EXTREME `cy` cells (nearest the container corners, where the window catches corner structure) and at the far `cx` cell. Every entry with `cx <= 0.9` is 0, and every entry with `cy` in the interior of the wall is 0. **min over `cy` cells = 0 for all 9 (cx, tilt-bin) pairs**, so a "square somewhere in the side zone" premise buys the composition NOTHING at this hypothesis width. Radial: all the mass sits at `x` in `(1, 13/8]` — nothing at all within `x <= 1`.

## 5. Pair-in-corner pilot (task iii) — FLOAT ONLY, essentially vacuous
`pair_pilot.json`. Square a in `[7/10,9/10]^2` tilt (30,45]; square b in `[7/4,39/20]^2` (diagonal offset 21/20) tilt (30,45] INDEPENDENTLY; 9 PlacedBox pairs (nsub = 3 each); window `[0,5/2]^2`. The offset 21/20 is the smallest for which every placement pair is provably interior-disjoint (worst SAT slack +0.0487); the true corner-to-corner tangency offset ~0.72 would put OVERLAPPING configurations inside the hypothesis and make the primitive meaningless. **Float area = 5/512 = 0.00977** (16 tiles, all beyond r = 1; the 8000-call work budget was hit). Below the brief's 1.0 threshold, so no exact recertification was run. Compare A23-4c's 1.3837 for a pinwheel pair with `+-0.01` centre cores and a 1.8-deg tilt range — 20x tighter in position, 8x in tilt. **At A21-zone hypothesis width the pair primitive carries nothing; it pays only at core boxes an order of magnitude smaller.**

## 6. Canaries (`primitive_canaries.json`) — **ALL PASS**
Every square is mapped by all 8 elements of D4; an image fires if its centre lies in the reference corner / side zone and its reduced tilt is <= 45 deg. Each (square, corner) and (square, wall) incidence is charged ONCE (min over qualifying images). Overlap between corner and side windows of the same wall is IGNORED, which can only overstate.
* **Trump** (s = s0 exactly; EXACT Fraction extraction, `canary.py` verbatim, A43 TOL 1e-6): **8 instances fire** — 3 corner (squares 0, 2, 5) + 5 side — and **every one prices exactly 0**, so `sum = 0 <= B0 = 4.0318`. PASS. Consistency check as demanded: all three corner-zone squares are wall-flush uprights (`theta = 0`, two WF contacts each) landing in `C_x0_x0_b0_1`, whose certified value is exactly 0. Trump strands nothing in his corner cells and the table charges nothing — **consistent, and independent evidence that the near-flush zero is real geometry rather than a resolution artefact.** His two 40.18-deg squares fire in side bins that are also 0.
* **12 genuine A37 atlas families at their own s** (FLOAT extraction, 8 instances each): sums 0.0000-0.5798 against budgets 4.03-4.50; maximum capture **13.8%** (families 13/14). All PASS.

## 7. Gap list
**Float-only** (never inside a shipped number): (1) the quadtree search, `quick_cover` screening and all failed splits — every shipped tile was re-derived in Fractions; (2) the **entire pair pilot**, whose work budget was also hit; (3) the atlas canary rows (A37 stores theta in radians) — Trump's row is exact.
**Dropped tile classes** (all lower the numbers, all sound): (4) tiles undecided at `min_cell = 1/64` (up to ~2400 per corner entry) — a finer `min_cell` would raise every entry, most sharply the small-tilt ones, and could in principle lift the near-flush 0; (5) tiles not interior-disjoint from some placement of the hypothesis — correct (dead area must be empty area), but with a 0.2-wide centre cell the union of placements is large and this is the DOMINANT loss; (6) the window (`13/8`): the corner radial profiles show the mass well inside, so it is not binding there, but the side entries put ALL their mass at `x` near `13/8`, so the side window IS binding — **GAP-A47b-1**; (7) the side `work_budget = 5000` certifier calls per entry, overflow dropped.
**Judgment calls**: (8) `nsub` = 4 per bin, raised so that no sub-bin exceeds 3 deg (corner) / 5 deg (side); coarser sub-binning only weakens. (9) Position sub-splitting was tested (2x2 on `x1 x x1 x (15,30]`): +2.5% area for 2.4x the cost — NOT used. (10) The side `cy` axis was refined to 7 cells; the brief's 2 coarse cells are derived exactly and are all 0. (11) Corner and side regions of the same wall overlap; the canary sums them anyway (overstating direction), but for the composition A46's `clip_util` adjacent-wall deduction must be applied — NOT exercised here — **GAP-A47b-2**. (12) The atlas canaries sit at `s > s0`, where the s0 certificate is not a valid lower bound (a bigger container has a SMALLER dead set); pricing them with the s0 table OVERSTATES, so a PASS there is a strictly stronger test but not a certified statement. (13) The consumer must use the delta-table or apply sigma itself — using the theta-table on a square whose tilt exceeds 45 deg without the sigma coordinate swap would be WRONG. (14) These are per-square primitives only: nothing here bounds how MANY squares can occupy the zones, and nothing here makes distinct zone regions disjoint (sect. 4 of A46 owns that).
