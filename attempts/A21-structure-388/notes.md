# A21-structure-388 — structure theorems for all packings with side <= 3.88 (above Trump's s* = 3.8771)

Owner: LP postdoc (rigorous LP computation). 2026-08-20. Status: **running**.

## 0. The frame (PI pivot): certified coverage lemmas ABOVE the optimum are structure theorems

s' = 3.877083590022814 (Trump's side). We work at s = 3.88 = 97/25 > s'. Packings of 11 unit squares at side
3.88 EXIST (Trump's, scaled up trivially), so no measure certificate can kill the root: tau*(3.88) >= 11.
What the case-LP machinery still proves are NO-branch lemmas: structure theorems satisfied by EVERY packing
with side <= 3.88 — in particular by Trump's own packing and by any hypothetical better one.

**Bridge lemma (A13 §1 restated for s > s').** Let mu = sum w_i delta_{p_i} be a measure on [0,s]^2 with
mu(total) < 11, and let F be a family of placements (here: NO-families = zones Z x theta-interval-sets) such that
mu(Q) >= 1 for every closed unit square Q subset [0,s]^2 (any orientation) whose placement is NOT in F.
Then every packing of 11 unit squares with pairwise disjoint interiors in a square of side s'' <= s has a square
whose placement lies in F.
Proof. Scale the packing by s/s'' >= 1 into [0,s]^2 and shrink each scaled square about its centre to a unit
square: 11 pairwise disjoint CLOSED unit squares in [0,s]^2 (if s'' = s the squares are only interior-disjoint;
shrinking by an arbitrarily small factor and using that mu(Q) >= 1 holds for the closed limit — the verifier
checks CLOSED squares and the covered predicate is closed under the limit — handles this case: formally, apply
the certificate at side s/(1+eps) images and let eps -> 0; every strictly-shrunk square stays non-exempt or
enters F, and F is closed). If none of the 11 placements were in F, each square would have mu-mass >= 1 and
mu(total) >= 11, contradiction. QED
Remark (closedness): all our F are CLOSED sets in (centre, theta) (closed zones x closed theta intervals), and
the scaling map is continuous, so the eps -> 0 limit argument is sound; more simply, for s'' < s (the case of
interest — s'' = s'+delta < 3.88 for the optimality programme) the squares are strictly shrunk and pairwise
disjoint as closed sets, exactly as in Theorem 1's proof (docs/results.md), no limit needed. For s'' = s the
statement holds for interior-disjoint packings by the limit argument; we only ever USE s'' <= 3.877x < 3.88.
Note the scaling REDUCES the squares' size but PRESERVES centres' relative position (centre c -> c*s/s'') and
orientations; "a square in zone Z" is a statement about the SCALED packing in [0,s]^2. For the optimality
programme this is the right normalisation: all statements below are about packings rescaled to the 3.88 frame.

The certificate semantics, the exempt tests, the exact verifier (verify_case.py) and the robustness margins
(weights x1.03, EPS_GEO 3e-3, EPS_ZONE/EPS_CORE 2e-3, EPS_TH 0.3 deg) are IDENTICAL to A13/A14 — only the
reading changes: at s < ceiling(~3.83) a certified NO-branch was one branch of a proof of s(11) >= s; at
s = 3.88 > s' it is an unconditional structure theorem about all (near-optimal and optimal) packings.

Zones (A13 make_zones(3.88, 0.6), centre domain [0.5, 3.38]^2):
corner0 = [0.5,1.1]^2, corner1 = [2.78,3.38]x[0.5,1.1], corner2 = [2.78,3.38]^2, corner3 = [0.5,1.1]x[2.78,3.38];
side0 (left) = [0.5,1.1]x[1.1,2.78], side1 (bottom) = [1.1,2.78]x[0.5,1.1], side2 (right) = [2.78,3.38]x[1.1,2.78],
side3 (top) = [1.1,2.78]x[2.78,3.38].
Orientation families: zone = the whole centre domain [0.5,3.38]^2, theta-interval set = complement of the
angle box Theta_B being tested; "some square has theta in the family" == "not all 11 orientations in Theta_B".

## 1. Nodes run (s = 3.88, budget 11, A14 oracle v3, alternating pruned LPs)

(appended as results come in)
### Round 1 (exploratory, 900 s, EPS_GEO 1e-4, warm from A07/A14 results at 3.84-3.85)

| tag | hypothesis (family F; theorem = "some square in F") | sym | tau | mm / mc | slack | verdict |
|---|---|---|---|---|---|---|
| corners4 | NO(all 4 corner zones) | D4 | 9.768 | 0.90 / 1.04 | -1.23 | DEAD -> certify (corner occupancy) |
| sides4 | NO(all 4 side zones) | D4 | 8.393 | 0.95 / 1.01 | -2.61 | DEAD -> certify (side-zone occupancy) |
| corner0 | NO(corner zone 0 only) | C1 | 10.719 (unconv, mm 0.68) | 0.68 / 1.05 | -0.28 | inconclusive at 900 s -> longer run (corner0_b) |
| th_a | F = [0,10]u[35,55]u[80,90] deg (Theta_B = [10,35]u[55,80]) | D4 | 10.867 (unconv, mm 0.87) | 0.87 / 1.03 | -0.13 | marginal -> continuation / widened F |
| th_b | F = [10,80] (Theta_B = [0,10]u[80,90], near-upright class) | D4 | **11.000 conv, mc 1.000** | 1.00 / 1.00 | 0.00 | **ALIVE**: weight-11 fractional packing, all orientations within 10 deg of upright |
| th_b_lit | F = [10,90] (Theta_B = [0,10] literal, A10's box) | C1 | **11.000 conv, mc 1.000** | 1.00 / 1.00 | 0.00 | **ALIVE** at 3.88 (A10: dead at 3.87) -> crossing s_B([0,10]) in (3.87, 3.88] |
| th_c | F = [5,43]u[47,85] (Theta_B = [0,5]u[43,47]u[85,90]) | D4 | 10.985 (unconv, rising) | 0.97 / 1.005 | -0.015 | effectively ALIVE -> no theorem; see 43-deg interpolation below |

Notes on the alive boxes:
* th_b blocking structure (converged dual, coverage <= 1 + 1e-7): 4 corner uprights weight 1/2 (doubled orbit),
  8 wall uprights 1/4 + wall near-uprights 0.5 deg 1/4, interior: 8-fold 10/80-deg pinwheel at (1.43-2.45)^2 1/4
  and 0.5/89.5-deg interior placements 1/8 -- the A12-style locally-integral 1/4-structure transplanted to the
  near-upright class. The LP cannot exclude "all 11 squares within 10 deg of upright" at 3.88 (no such packing is
  known below 4; this is the LP integrality gap, not a packing).
* th_b_lit: same story for the literal one-sided box [0,10] (converged nu = 11): between 3.87 (A10: tau 10.50,
  dead) and 3.88 the box LP's fractional packing appears. So 3.88 is JUST past the last s where near-upright
  can be killed by the plain box LP.
* th_c (PI's "generic tilt" target): the +-2 window around the diagonal cannot die at 3.88 for a REAL reason:
  on the Trump one-parameter family (tilt theta, 6+5 structure) s(theta) interpolates 3.8771 (40.18 deg) ->
  3.8856 (45 deg); at theta ~ 43 deg s(theta) ~ 3.880 <= 3.88, so Theta_B = [0,5]u[43,47]u[85,90] admits genuine
  (near-)packings. The PI's literal window [0,5]u[40,50]u[85,90] needs no LP at all: Trump's own packing
  (orientations {0, 40.18} subset [0,5]u[40,50], side 3.8771 < 3.88) makes it alive -- the suggested
  "generic tilt at 3.88" theorem is FALSE as stated. Tightened variant tested next: Theta_B = [0,5]u[44,46]u[85,90]
  (s(44) ~ 3.882 > 3.88 on the family), tag th_c2.

### Round 2 (certifications + refinements)

* **corners4 CERTIFIED** (`certs_wip/thm1_corner_occupancy.json` + `.report.json`, exact verify_case.py PASS,
  s = 97/25, depth 56): 3e-3 re-solve tau = 9.942, round 0 FAIL (43 holes), one witness-feedback re-solve
  (tau 10.253, conv) -> round 1 PASS. 1093 atoms, total 1320137/125000 = 10.561096 < 11 (margin 0.44).
* **sides4 CERTIFIED** (`certs_wip/thm2_side_occupancy.json` + `.report.json`, PASS first attempt):
  3e-3 re-solve tau = 8.490, 836 atoms, total 2186329/250000 = 8.745316 < 11 (margin 2.25).
* corner0 (NO corner zone 0 only): 900+1800+1800 s continuations: tau 10.719 -> 10.770 -> (corner0_c pending),
  unconverged (mm 0.79), rising. Already above the certifiability ceiling (~10.75 raw at 1e-4 given the
  3e-3 + scale overhead): the PER-CORNER occupancy theorem is NOT certifiable at 3.88 by this method.
  Blocking structure: the LP concentrates weight ~0.42-0.67 on the other three corners plus wall uprights --
  a fractional configuration avoiding corner 0 at cost only ~0.2-0.3 below the root.
* side0 (NO side zone 0 only): tau = 10.519 after 1800 s (mm 0.75, stable over the last 400 s), slack -0.48.
  Certification attempt with auto-scale running (certify_side0).
* th_c2/th_c3 (tightened diagonal windows [44,46] / upright [0,2]): tau = 10.914 / 10.924, both unconverged
  with mm 0.95-0.96 -- the plateau ~10.92 persists as the windows shrink (blocked by 0.32-weight corner
  uprights + window continuum mass, NOT by the 43-deg family): no generic-tilt window certificate at 3.88
  down to +-1 deg. (Exact {0,45} would have margin ~0.31 by A10's table, but a measure-zero angle set is
  not a useful structure statement.)

## 2. STRUCTURE THEOREMS (all packings of 11 unit squares with side <= 3.88, rescaled to [0, 97/25]^2)

Every statement below is about ANY packing of 11 unit squares with pairwise disjoint interiors in a square of
side s'' <= 97/25 = 3.88, after the scale-by-97/(25 s'') normalisation of the bridge lemma (§0). Since
s' = 3.8770835900... < 3.88, the family of such packings is NON-EMPTY (it contains Trump's packing and any
hypothetical better-than-Trump packing): the theorems are non-vacuous structure facts about all near-optimal
packings. "Orientation" theta of a square is its tilt mod 90 deg; t = tan(theta/2). Zones are CLOSED; the
exact rational data (zones, t-intervals, atoms, weights) are in the certificates.

**Theorem A21.1 (corner occupancy; `certs_wip/thm1_corner_occupancy.json`, exact verifier PASS).**
Every such packing has a square whose centre lies in one of the four closed corner zones
[1/2,11/10]^2, [139/50,169/50]x[1/2,11/10], [139/50,169/50]^2, [1/2,11/10]x[139/50,169/50]
(i.e. within 0.6 of a corner of the admissible-centre square; up to the D4 symmetry: SOME corner zone is
occupied). Certificate: 1093 atoms, total mass 1320137/125000 = 10.561096 < 11; verifier: 343,272 boxes,
max depth 27 (cap 56), all non-exempt boxes covered; margins EPS_GEO 3e-3 (LP), weights x1.03.

**Theorem A21.2 (side-zone occupancy; `certs_wip/thm2_side_occupancy.json`, exact verifier PASS).**
Every such packing has a square whose centre lies in one of the four closed side zones
[1/2,11/10]x[11/10,139/50] (left), [11/10,139/50]x[1/2,11/10] (bottom), [139/50,169/50]x[11/10,139/50]
(right), [11/10,139/50]x[139/50,169/50] (top). Certificate: 836 atoms, total 2186329/250000 = 8.745316 < 11
(margin 2.25 -- the strongest of the four); verifier: 341,404 boxes, max depth 31.

Corollary (A21.1 + A21.2). Every such packing has a square centred in a corner zone AND a square centred in
a side zone; when the two centres differ these are two distinct pinned squares (the zones are disjoint except
for shared boundary edges, so only a centre lying exactly on a shared edge could witness both).

(Theorem A21.3, orientation: status pending -- see §3.)

## 3. What does NOT hold / could not be certified at 3.88 (as important as the theorems)

* **Per-corner occupancy is NOT provable by this method at 3.88** (and is plausibly false as an LP statement):
  NO(corner zone 0 only) has LP value 10.719 -> 10.770 -> 10.856 over 900+1800+1800 s (C1, unconverged,
  monotonically rising, mm 0.82): it will end within ~0.15 of the budget 11 or cross it. The blocking
  near-solution loads the other three corners (weights 0.42-0.67) and the walls -- coverage can be bought
  there at ~0.85-0.9 mass per unit weight. So "all four corner zones occupied" (4 squares pinned) is NOT
  in the LP's reach; only the D4-symmetric disjunction (A21.1) is.
* **Per-side occupancy**: NO(side zone 0 only) = 10.519 raw (1e-4, stable last 400 s), 10.60-10.68 at 3e-3.
  Certification attempted (auto-scale, ~2.6% margin): rounds 0-2 FAILED with recurring holes; retry running.
  [status updated below]
* **Near-upright orientation box is ALIVE at 3.88** (it was dead at 3.87, A10): both Theta_B = [0,10] (literal,
  C1) and [0,10]u[80,90] (D4) converge to tau = 11.000 with maxcov = 1.000: a weight-11 fractional packing all
  within 10 deg of upright exists at 3.88 (structure: 1/2-corner uprights, 1/4 wall uprights, interior 10/80 deg
  pinwheel + 0.5 deg near-uprights -- the A12 quarter-structure transplanted to the near-upright class).
  So the crossing of the near-upright box is s_B([0,10]) in (3.87, 3.88] -- the box LP loses its last
  orientation-restricted kill just below Trump's side. No near-upright-only PACKING is known below side 4;
  this is the LP integrality gap, not a packing.
* **No "generic tilt" theorem at 3.88**: the PI's window [0,5]u[40,50]u[85,90] is alive for a trivial reason --
  it contains Trump's own orientation set {0, 40.18} and Trump's packing fits in 3.88. Excluding theta*:
  [0,5]u[43,47]: tau = 10.985 (the Trump 6+5 family interpolated to tilt ~43 deg needs only ~3.880 <= 3.88);
  [0,5]u[44,46]: 10.914; [0,2]u[44,46]: 10.924 -- a stable plateau ~10.92 carried by 0.32-weight corner
  uprights + window mass, ~0.08 above certifiability. Exact {0,45} would die (A10: tau = 10.686 at 3.88) but a
  measure-zero angle set is not a structure theorem. CONCLUSION: above s', "the packing must use a tilt away
  from 0/45" is false in the LP relaxation for any window >= +-1 deg.
* Theta_B = [10,35]u[55,80] (no near-axis, no near-diagonal squares): tau = 10.867 after 980 s (rising from
  10.79; true value ~10.95): dead-but-not-certifiably at the +-10 window. The +-15 window (Theta_B =
  [15,30]u[60,75]) has tau = 10.644 raw and IS in certification range; certification running.
  [status updated below]
