# A23-wastage-oracle — dead-region certifier + area-ledger ("wastage") test on the mid-tilt obstruction

Owner: postdoc (computational geometry / rigorous computation). 2026-08-20. Status: **done-success** (~5 h; certifier delivered + validated, tables computed, ledger kills obtained at 3.86 AND s').

Question (PI): area accounting as an INTEGRAL branch-killer.  In a container of side s a packing of 11 unit
squares leaves exactly s² − 11 of empty area (budget ≈ 3.8225 at s = 3.85, 3.8996 at 3.86, 4.03184 at
s' = 3.8770836).  A region D is **dead** for a partial configuration H if no legal unit-square placement
covers any point of D; dead regions stay empty forever, so Σ certified-dead-area ≤ s² − 11 in every branch
that extends to a packing — exceeding the budget kills the branch.  This constraint applies to actual
placements (integral), so the ¼-weight fractional structures that defeat the LP/ϑ′/kernel machinery cannot
cheat it.  Tasks: build the certifier, tabulate the wastage of mid-tilt squares near walls/corners and of
pinwheel near-tangencies, and test the ledger on A14's alive node classes.

## 1. Definitions and lemmas

**Setting.**  Container [0,s]², s rational.  A *placement* is a closed unit square Q(c,θ) ⊂ [0,s]²,
parametrised by centre c and t = tan(θ/2) ∈ [0,1] (θ ∈ [0°,90°] suffices).  A *partial configuration* H is
a finite set of placed closed unit squares P₁..P_k with rational centres and rational t (all corners
rational).  A placement Q is *legal for H* if Q ⊂ [0,s]² and int(Q) ∩ int(P_i) = ∅ for all i.

**Definition (dead region).**  A convex polygon D with rational vertices, interior-disjoint from every P_i,
is *dead for H* if no placement legal for H meets int(D).
(We certify the interior version: tangential touching of ∂D by a legal square is allowed — it does not
affect areas and it makes the property certifiable by box methods, cf. the Göbel tangency phenomenon in A08.)

**Lemma 1 (monotonicity).**  If D is dead for H and H ⊆ H′ (more squares placed), D is dead for H′.
Proof: a placement legal for H′ is legal for H.  ∎  (This is what makes deadness usable down a branch tree:
certificates persist under refinement and under adding placed squares.)

**Lemma 2 (budget).**  Let P be any packing of n unit squares with pairwise disjoint interiors in [0,s]²
with H ⊆ P, and let D₁..D_m be pairwise interior-disjoint regions, each dead for H.  Then
Σ area(D_j) ≤ s² − n.
Proof.  Each packing square Q ∈ P∖H is a placement legal for H (it is in the container and its interior is
disjoint from every int(P_i)), so Q misses int(D_j) for every j; the squares of H are interior-disjoint
from every D_j by hypothesis.  Hence the interiors of the D_j are disjoint from the interiors of all n
packing squares, and the sets {int D_j} ∪ {int Q : Q ∈ P} are pairwise disjoint subsets of [0,s]²:
Σ area(D_j) + n ≤ s².  ∎

**Corollary (kill test).**  At a case-tree node whose hypothesis contains the placed set H (cores fixed as
in A13/A14), if certified dead regions of total area > s² − 11 exist, no packing of 11 squares at side s
satisfies the node hypothesis: the node is dead.  (For "side ≤ s" semantics compose with the shrink-and-
scale step exactly as in Theorem 1 / A13's node-death lemma; the scaled packing consists of closed unit
squares inside [0,s]² with pairwise disjoint interiors, which is all Lemma 2 uses. Caveat: the tree's YES
hypotheses fix a core BOX, not an exact placement — see §6 (composition) for what H must then be.)

## 2. The certifier (`dead_region.py`) — soundness

Branch-and-bound over parameter boxes B = [t0,t1] × [x0,x1] × [y0,y1].
Root: t ∈ [0,1], centre range = bbox(D) inflated by 7072/10000 in the ∞-norm, clipped to [½, s−½]².
Complete because every point of Q lies within half-diagonal √2/2 < 0.7072 of c (2-norm ⇒ ∞-norm), so any
placement meeting D has centre in the root; centres outside [½, s−½]² are inadmissible since w = cosθ+sinθ ≥ 1.
A box is DISCHARGED when ONE of the following holds for ALL (t,c) ∈ B; otherwise it is bisected
(dyadic midpoints; t-width scaled). Undischarged at depth_max ⇒ FAIL (with witness parameters).

* **(V) vacuous.**  w is unimodal in t (max at t = tan 22.5°), so wLo = min(w(t0), w(t1)) ≤ w on the box;
  clip centre ranges to [wLo/2, s−wLo/2]; empty ⇒ no admissible placement.  (Same argument as
  `certs/verify_measure.py`.)
* **(D) disjoint from D** — a fixed separating axis for the whole box, two sound families:
  (a) Q-frame: exact enclosures C = [cos t1, cos t0], S = [sin t0, sin t1] (cos decreasing, sin increasing,
  both ≥ 0 on t ∈ [0,1]); interval body coordinates u = C·dx + S·dy, v = −S·dx + C·dy of every vertex of D;
  if every vertex has u ≥ ½ over the whole box (interval lower bound), D is beyond the u = +½ edge for every
  placement in B (similarly u ≤ −½, v ≥ ½, v ≤ −½): Q ∩ int(D) = ∅.
  (b) D-frame: for each outward edge normal a of D, Q lies beyond the edge if min_B a·c − r(a) ≥ max_D a·p
  with r(a) = (max|a·e1| + max|a·e2|)/2 over the enclosures of the edge vectors e1 = (C,S), e2 = (−S,C).
  Soundness: a separating line implies disjointness of the convex sets.
* **(O) overlaps a placed square** — WITNESS-POINT test: a rational point p with (i) p ∈ int(P_i), checked
  exactly once (|u_P(p)| < ½ and |v_P(p)| < ½ strictly in P_i's frame), and (ii) p ∈ Q(c,t) for every
  (t,c) ∈ B (exact interval containment, the same enclosures as verify_measure.py).
  **Soundness:** p ∈ int(P) and p ∈ Q (closed) ⇒ int(P) ∩ int(Q) ≠ ∅, because a closed convex body with
  interior satisfies Q = closure(int Q), so every neighbourhood of p meets int(Q), and some neighbourhood
  of p lies in int(P).  Hence Q is not legal.
  **Rejected alternative (unsound):** "the projections on all 4 SAT axes overlap for the whole box" is
  NECESSARY for overlap, not sufficient (two convex polygons can have overlapping projections on every edge
  normal while being disjoint — e.g. two squares off-diagonal); it is not used.
  Cheap special case: if the whole centre box lies strictly inside P_i, then p = c works (c ∈ Q always).
  Witness points: static interior grids + near-edge layers (offsets 0.01/0.03/0.08) of each P_i, plus
  float-guided candidates (shapely representative point of Q_inset ∩ P_inset, inset by the parameter-motion
  bound r = (Δx+Δy)/2 + 0.7072·Δθ...), rationalised and re-checked exactly.  Candidates only SUGGEST points;
  every accepting decision is the exact interval test.

If every box is discharged: **every placement in [0,s]² meeting int(D) interior-overlaps some P_i ⇒ D dead.**

Modes: `exact` (Fractions end-to-end — the certificate) and `float` (same logic, IEEE with outward safety
eps 1e-9, all roundings on the conservative side: containment shrinks ½ → ½−eps, disjointness grows
½ → ½+eps, clip grows — the fast mapping tool, "certified modulo rounding").  A vectorised
`quick_cover` search (legal placement covering a probe point ⇒ NOT dead) is used only as a negative
prefilter in the mapper, never for certification.

**Area mapper** (`wastage.py`): quadtree of axis-aligned cells with dyadic rational corners over a window;
a cell counts only if (exactly) interior-disjoint from every P_i AND certified dead; failing cells split to
min_cell (default 1/64) and are dropped ⇒ the reported area is a certified LOWER bound of the dead area.
Unions are sound: cell-PASS means no legal placement meets the cell, so every point is dead; disjoint dead
cells add in Lemma 2.

## 3. Validation (task 1, `test_validate.py` — all PASS, float and exact modes)

* (a) 45°-square touching both walls at a container corner: the corner pocket triangle (legs ≈ 0.687,
  area 0.236 after a 0.02 backoff) is certified dead in 19 boxes; a 0.4-leg core in 5 boxes. Exact mode ✓.
* (b) a free cell at the container centre (placed squares far away, and also with NO placed squares):
  correctly FAILS (not dead) with a witness placement.
* (c) two upright unit squares with facing edges 0.9 apart (channel of width 0.9 < 1, blocks at
  y ∈ [1.4, 2.4]): the naive guess "the whole channel is dead" is FALSE and the certifier caught it —
  witness at θ ≈ 60°: a tilted square can DIP A CORNER through the 0.9 slot past the blocks' top corners
  down to depth 0.45 (chord constraint 2δ ≤ 0.9), and symmetrically from below; only the middle band
  y ∈ (1.85, 1.95) is dead.  The corrected region [1.9,2.0] × [1.87,1.93] passes (float + exact, 765
  boxes); the naive region fails with the dipping-corner witness; a 1.02-wide channel fails (an upright
  square slides in).  This "corner dipping" escape is exactly the phenomenon that bounds all the wedge
  tables below, and it validates that the certifier's FAILs are geometrically real, not artefacts.


## 4. Wastage tables (task 2) — float-interval maps, exact spot-verified

Mapper resolution: cells split down to 1/64; every number is a certified LOWER bound of the true dead
area (finer cells only add).  Exact-mode re-certification (Fractions, depth 40): `wall_th25_d0`
all 264 cells PASS, area 0.2361 exactly reproduced; adversarial random-legal-placement tests
(`adversarial.py`, independent float SAT via code/squares.py): 0 hits on dead cells in 4·10⁵ samples
per config.

### 4a. One mid-tilt square, lowest corner at distance d above the bottom wall (s = 3.85, X0 = 1.6)

certified dead area (both wedges + under-square strip):

| θ \ d | 0 | 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|
| 20° | 0.1887 | 0.2346 | 0.2779 | 0.3556 |
| 25° | 0.2361 | 0.2801 | 0.3212 | 0.3936 |
| 30° | 0.2846 | 0.3222 | 0.3593 | 0.4252 |
| 35° | 0.3584 | 0.4014 | 0.4345 | 0.4723 |

Monotone in θ and in d; the dead set = the two wall wedges (opening angles θ and 90°−θ) up to the
"corner-dipping" reach plus the strip under the square (`plots/wall_th*.png`).  A single mid-tilt
square near a wall strands 0.19–0.47 — of the same order as one full unit square of the packing.

### 4b. One mid-tilt square touching BOTH walls in a container corner (s = 3.85)

| θ | 20° | 25° | 30° | 35° | (45° validation pocket: 0.236 + two wall wedges) |
|---|---|---|---|---|---|
| dead | 0.3430 | 0.4207 | 0.4879 | 0.5384 | |

The A14-relevant version: fixed placement (0.72, 0.72, 40°) (inside A14's alive box
[0.5,0.8]²×[30,60]°, corner gap d = 0.0154): **0.6065**.
**Core-box-UNIFORM version** (`PlacedBox`, the actual node semantics "some square has
(c,θ) ∈ [0.72,0.74]² × [39°,41°]"; every certificate holds simultaneously for EVERY placement of the
core, via witness points interior to all core placements and interval separations over the core box):
**0.5285** — the uniformity cost over a 0.02 × 0.02 × 2° core is only ≈ 0.08.  This is the object
that composes into A14's verify_case semantics (§6).

### 4c. The pinwheel near-tangency pair (task 2b) — the surprise

The two ADJACENT 33°-tilted squares of A12's s = 3.86 interior support ((2.4597, 2.5405) and
(1.3195, 2.4597)) are in fact ALREADY pairwise exactly disjoint at the raw rational coordinates
(adjacent SAT gap +0.00024; the interior support is TWO alternative 4-cycles 0.017 apart — the 33°
orbit with gap +2.4e-4 and the 32° orbit with overlap −2.0e-4, the latter being A10's
"0.0002-overlap 4-cycle"; cross pairs share a slot, gap −0.99).  The corresponding REAL placement is legal as-is, and it
strands not a thin sliver but a LARGE SHADOW: the pair's high corners leave 0.63 < 1 of clearance to
the nearest wall and their caps clip every side entry — certified dead area **1.8834** for the bare
pair in an otherwise empty container (full window to the wall; the initially wall-clipped subwindow's
565 cells, area 1.2274, ALL pass the exact Fraction recheck — 0 failures).  `plots/pair.png`.  The A10/A12 observation
"the 4-cycle members are almost disjoint and the LP cheats by ¼-weights" has an integral shadow the
LP never sees: REALISING two adjacent pinwheel members instantly wastes ≈ 1.2 of area.

## 5. Ledger test on the real obstruction (task 3), s = 3.85 / 3.86

Budgets: s² − 11 = 3.8225 (3.85), 3.8996 (3.86), 4.03184 (s' = 3.8770836).

| partial configuration H (all placements exact rationals) | k | certified dead | budget | verdict |
|---|---|---|---|---|
| four corner squares fixed exactly ([0,1]² etc., A14 x_corners4) | 4 | **0.0000** (bottom strip window; pass = 0 cells) | 3.8225 | strands NOTHING — matches A14 §3c: the corner stage has zero killing power, in area as in coverage |
| one A14 alive-node corner square, fixed (0.72, 0.72, 40°) | 1 | 0.6065 | 3.8225 | 16 % of budget |
| same, CORE-BOX-UNIFORM [0.72,0.74]² × [39°,41°] | 1 | 0.5285 (exact: all 410 cells PASS) | 3.8225 | the node-semantics version |
| adjacent pinwheel pair (A12 interior, s = 3.86) | 2 | **1.8834** (exact ≥ 1.2274) | 3.8996 | 48 % of budget at depth TWO |
| same pair, CONTINUUM cores (PlacedBox: centres ±0.01, θ ∈ [32.1°, 33.9°]) | 2 | **1.3837** | 3.8996 | 35 % of budget for EVERY realisation of the two cores — the composed-kill mechanism demonstrated at hypothesis scale |
| pinwheel 4-cycle realised (all four 33° images, s = 3.86) | 4 | **6.5488** (float map; EXACT-certified subset **4.4032 > budget**, 172 cells, 0 fail) | 3.8996 | **KILLED at depth FOUR, margin 2.65 (float) / 0.50 (already-exact subset).**  Lemma 2: any packing containing these four squares has n ≤ 3.86² − 6.5488 = 8.35, i.e. **at most 8 squares total** — and 8 is realised (pinwheel + 4 corner squares, each legal with gap 0.0097 and meeting 0 dead cells).  The dead set is a plus-sign: all four mid-wall bands (the side-upright zones of the ¼-structure!) + the central pocket; only the corner pockets survive (`plots/pinwheel4.png`) |
| A12-style 10-square realisation (4 corners + 4 side uprights + 1 tilted + 1 interior upright, s = 3.86) | 10 | **4.80** (float map; drop = 0: EVERY free cell certified dead — no legal placement exists anywhere; exact sample: 300 cells, 0 failures) | 3.8996 | **KILLED, margin ≈ 0.9** (float): this configuration extends to no 11-packing — the integral α = 10 deficit of the ¼-structure, detected by pure area accounting |

**Exactness status of the ledger.**  Fully exact (pure Fractions, 0 cell failures): the flagship
kills — pinwheel4 at 3.86 (4.4032 > 3.8996, 172 cells) and pinwheel4_sp at s' (4.5056 = 2816/625 >
s'² − 11, 176 cells) — plus wall_th25_d0 (264/264), pair subwindow (565/565), corner_box uniform
(410/410) and exact samples of tenpack (300) and pinwheel4_sp/pinwheel4 (as above).  Everything else
is float-interval with outward guards; every exact re-certification ever run agreed with the float
map with zero failures (≈ 1900 cells total).

## 6. Composition: wastage as an extra kill/exempt test in the A13/A14 case-tree semantics

* Node hypothesis = cores B₁..B_m (YES: "some square has (c,θ) ∈ B_i") + NO-zones.  The wastage test
  consumes the SAME hypothesis data: H = {PlacedBox(B_i)}, where `PlacedBox` makes every certificate
  UNIFORM over the core box — witness points are kept only if provably interior to EVERY core placement
  (exact interval test over the core's (t,c)-box), cell exclusion uses an interval SAT against all core
  placements, so a PASS certifies: for every realisation (P₁..P_m) ∈ B₁×..×B_m of the cores, D is dead for
  {P₁..P_m}.  Combined with Lemma 2: certified dead area > s² − 11 ⇒ NO packing of 11 satisfies the node
  hypothesis ⇒ node dead.  Measured uniformity cost over a 0.02×0.02×2° core: 0.60 → 0.53 (≈ 13 %).
* NO-zone hypotheses are not yet exploited (legal placements for the node are FEWER, so the present
  certificates are simply conservative); adding them = one more discharge test (centre box inside the
  NO-zone) — trivial in the same B&B.
* The test is one-sided and independent of the node LP: it cannot replace coverage bounds at shallow
  nodes (dead ≈ 0.5 ≪ budget there), but unlike the LP its strength GROWS with depth (more placed
  squares ⇒ more dead area; Lemma 1), while A14 measured the LP slack SHRINKING with depth in the corner
  stage.  The two are complementary in exactly the right way.
* Cost: float map 0.5–3.5 min per node (single process), exact re-certification of the passing cells
  4–60 min; both trivially parallel over cells.

## 7. Extrapolation to s' and verdict for the optimality programme (task 3/4)

**Where the budget stands.**  s²−11: 3.8225 (3.85) / 3.8996 (3.86) / 4.0318 (s').  Certified wastage
measured here: one mid-tilt square 0.19–0.61 (wall/corner), the core-uniform A14 node square 0.53,
the realised pinwheel pair 1.88 (depth 2), the realised pinwheel 4-cycle 6.55 (depth 4), an A12-style
10-square realisation 4.80 with NO legal placement left anywhere (depth 10).

**Does wastage bite where everything else went blunt?  YES — on the interior pinwheel, and already at
depth 2–4.**  The ¼-weight structure that holds τ*_B = 11.000 for A10's box LP, defeats A12's region
cuts, pins A14's corner stage at slack 0, and re-pins every kernel (A17–A20), consists of corners (1),
flush side uprights (¼) and the interior pinwheel (¼).  Its integral content is exactly what the
wastage oracle measures:
* corners and flush side uprights strand ~0 (this is why the corner stage of the LP tree was barren);
* but REALISING the interior pinwheel is area-suicidal: the four 33° squares strand 6.55 > 3.90 —
  Lemma 2 leaves room for at most 8 squares total (sharp: pinwheel + 4 corners is legal), so **no
  11-packing at s = 3.86 contains the realised 4-cycle**, and even the adjacent PAIR alone eats 48 %
  of the budget.  The fractional structure survives every coverage relaxation precisely because it
  puts only ¼-weight on each pinwheel member; the integral versions are killed by area accounting —
  the first tool in the programme that distinguishes the two.
* The kill SURVIVES at s' — measured, not extrapolated: the same 4-cycle scaled to s' = 3.8770836
  (`pinwheel4_sp`, centres scaled by s'/3.86, exactly disjoint) has certified dead area **6.5758**
  (float map) vs budget 4.03178 — and the kill is EXACT: a 176-cell subset of the map re-certifies in
  pure Fraction arithmetic to dead area **4.5056 = 2816/625 > s'² − 11** (0 failures, 4 min; file
  `results/pinwheel4_sp_exact_target.json`).  **Theorem (machine-checked, exact): no packing of 11
  unit squares in [0, 3.8770836]² contains the four scaled pinwheel squares** (indeed Lemma 2 with
  the full float map suggests n ≤ 8; the exact subset already gives n ≤ 10).  This is the first
  argument in the programme that kills a mid-tilt structure AT s'.
* What wastage does NOT do: it is NOT a stand-alone global-stage killer at the root (depth ≤ 1 configs
  strand ≤ 0.6 ≪ 4.03), and it cannot touch Trump-like structures (their partial configs must stay
  under budget, since the packing exists).  Its role is the LEAF/branch killer for interior mid-tilt
  structure, entered at depth 2–4, where A14 showed the LP has nothing.

**Verdict.**  The wastage/dead-area oracle is sound, cheap (0.5–8 min float per configuration,
exact re-certification minutes to an hour, embarrassingly parallel), and it bites exactly on the
structure that stalled the programme: realising any two adjacent members of the interior pinwheel
already burns half the empty-area budget, realising all four kills the branch outright with margin
2.65 — at 3.86 and (extrapolating, run in results/) at s'.  Composed with A14's tree semantics via
`PlacedBox` cores (uniformity cost measured: 13 % on a 0.02×0.02×2° core), it gives the case tree a
second, INDEPENDENT kill test whose strength grows with depth — complementary to the LP whose slack
shrinks with depth.  Recommended next steps: (i) a composed pilot: re-run A14's alive node 3 with the
wastage test at its pinwheel-side children (branch "two interior squares in adjacent mid-tilt cores"
→ dead by Lemma 2 with the pair table); (ii) exploit NO-zones in the B&B (one extra discharge);
(iii) a multiprocess mapper + a PlacedBox sweep over the A14 corner boxes (15³ cores ≈ 1 CPU-day
float) to turn the corner-node table into a certified continuum statement.

## 8. Files / reproduction

`dead_region.py` (certifier: exact Fractions + float-guard modes, PlacedBox core-box-uniform variant,
quick_cover negative filter), `wastage.py` (quadtree dead-area mapper + exact recheck),
`table_wall.py` (task-2 tables), `pair_sliver.py` (pair / pinwheel4 / pinwheel4_sp / corner_tilt /
corner_box / corners4 / tenpack configs), `recheck.py` / `recheck2.py` (exact re-certification),
`adversarial.py` (independent random-legal-placement spot checks; found+fixed its own pair-indexing
bug for k ≥ 4 — certifier results were never affected), `summarize.py`, `test_validate.py`.
Results: `results/*.json` (cells as exact dyadic rationals + areas; `*_exact.json` = exact
re-certifications), `plots/*.png`, `logs/`.
Reproduce: `python test_validate.py`; `python table_wall.py --theta all --d all`;
`python pair_sliver.py --config pinwheel4`; `python recheck2.py pinwheel4`;
`python adversarial.py pinwheel4 tenpack`.
