# A165 — the CASCADE case tree on `l1_104`: the tree, what forces each step, and where the chain breaks

Written 2026-09-08 (A165, Opus engineer).  Figure: [`../figs/cascade_l1_104.svg`](../figs/cascade_l1_104.svg)
(A148 panel style, one panel per case).  Record: [`../results/cascade165.jsonl`](../results/cascade165.jsonl).
Independent checker: [`../code/check165.py`](../code/check165.py), result
`../results/check165_l1_104_d8.json`.  Canary: §1 — read it first.

Nothing here is deployed into a frozen verifier.  Every geometric step is a certificate plus an
independent re-derivation, in the same status as A141's lane kills, A161's chord-limited lane and
A131's clip kills.  Every LP leaf is A150's driver (`lp150.solve_one`) on A135's certified EXACT
axis cores, so the FROZEN `verify_case.py` (untouched) is what certifies a kill.

---

## 0. The objects, and where each is proved

| tag | statement | source |
|---|---|---|
| **(R1)** | K0-FREE / K0-BLOCKED dichotomy: either some widened corner box of `F = Δ_λ P` is met by ≤ 1 square (teleport, dead for `m < ŝ`, a Trump image at `ŝ`) or every one is met by ≥ 2 | `docs/proofs/k0_route.md` §3, §4.2 (`teleport_packing`, `k0free_kill`) — conditional on `k1_00`'s tree (obligation **K0-O1**) |
| **(R2)** | Lemma K0-WIDEN: `Q` meets `int B_c(m)` ⟹ `Δ_λ Q` meets `int B_c^w(s0)`, pad `w = (λ_max − 1)(1 + 1/√2) = 0.025510074…` | `k0_route.md` §4.1 |
| **(R6)** | no unit square meets two widened corner boxes: `s0 − 2(1 + w) − √2 = +0.41185029 > 0`, so the four corner crowds are pairwise disjoint sets of squares | A150 `notes/composition.md` §1 |
| **(M0)** | `M(c) = 0` (the cell's conditioned square `H` cannot meet `int B_c^w`) ⟹ all the corner meeters are FREE squares | A161 `chordlane.box_misses_cell_exact` (full SAT over the parameter box, exact in ℚ) — strictly stronger than A141's `box_misses_cell` |
| **(COV)** | a complete binary cover of the corner pose window, every box discharged by *container* / *misses-cell* / *shared rational point with `H`* or kept OPEN | A141 `polylane.lane_cover`; discharge = A132 `vertex_ok` = Lean `checkVertexInPBox` |
| **(OVL)** | two cover boxes that ALWAYS overlap cannot hold two interior-disjoint squares | A118 §1.2(ii) (`lanelib.pair_always_overlap`) |
| **(PAIR)** | one rational point inside every pose of both boxes ⟹ the two squares are the SAME square ⟹ the case is contradictory | A141 §3/§5 (`polylane.pair_incompatible`, Lean `shared_point_same_square`) |
| **(ROW)** | chords of an interior-disjoint family on an axis-parallel line sum to `≤ s0`; each box contributes `≥ minchord(B, l)` | A144 LINE-1/LINE-2 (`guardline.minchord_box`, exact five-point rule) |
| **(TOP)** | for `y_L > s0 − 1` **no** admissible square lies entirely above `y = y_L` (`c_y ≤ s0 − h`, `c_y − h ≥ y_L` ⟹ `2h ≤ s0 − y_L < 1 ≤ 2h`); at `y_L = s0 − 1 − w` the exception needs tilt within **1.4809°** of an axis | proved in `cas165.top_row_facts`, re-derived in `check165.c8` |
| **(AREA)** | `|U(node)| ≤ m² − 11`; charge against `B0 = s0² − 11 = 4.031780343` | A89 Lemma ID (`tilt_floor_k0.md` §7) via A164 `geo164.uncoverable` |
| **(LP)** | the multi-box case-LP at budget `11 − #boxes`, exact cores, `verify_case.py` | A150 `lp150.py` |

---

## 1. CANARY — `l1_153` (the Trump-image cell): **PASS at every step run**

`l1_153` is `k0_00` level-1 cell whose box `x ∈ [2.5674485, 2.67226625]`, `y ∈ [2.357813, 2.46263075]`,
tilt `[45°, 60°]` contains square 9 of the D4 image `g4` of Trump at `s0`
(`class84.trump_scaled` + `symmetry`), pose `(2.623834103, 2.436508962, 49.81806271°)`.  A real
11-family reaches this cell, so **every** forced step of the cascade must accept it.

| step | what the canary shows | verdict |
|---|---|---|
| (R1) K0-BLOCKED | image `g4` meets the **widened** corner boxes with **BL 3, BR 2, TR 2, TL 2** meeters; on the **plain** unit corner boxes only **BL 1, BR 2, TR 1, TL 1**.  So the `K0-WIDEN` pad is exactly what makes three of the four corners doubly met — the brief's premise, confirmed | **PASS** — K0-BLOCKED holds for the one family that exists, and only because of the pad |
| (COV) the four covers | every real FREE meeter of every corner is located inside an OPEN box of that corner's cover (BL 3/3, BR 2/2, TR 1/1, TL 2/2; **0 unlocated**) | **PASS** — no cover step discards the real family |
| (M0) | `M(TR) = 1`: `H` itself (Trump's square 9) meets `int B_TR^w`, penetrating **0.4769** past the cell's `x0` and **0.2895** past its `y0` — not a boundary artefact.  A141's cover and A161's exact SAT **agree** | **PASS, and it is the discriminating fact** (below) |
| case family at TR | with `M(TR) = 1` the TR crowd may be `{H, one free meeter}`; the real family lands in the **mixed** case `{H, cover box 25}` (free meeter = square 5 at `(3.377084, 3.377084, 0°)`, the corner-flush square), and that case survives (OVL) and (PAIR) | **PASS** |
| leaf LP on the canary's own case | 2 boxes `{H, box 25}`, budget `11 − 2 = 9`: **τ = 9.000000000249, η = +2.5·10⁻¹⁰** — not a kill | **PASS — the canary is ALIVE** |
| (ROW) the four-wall row product | every real (case at `c1`, case at `c2`) of image `g4` survives every wall row: top 1/1, right 1/1, bottom 3/3, left 3/3 | **PASS** |
| (LP) the SPREAD leaf — the only leaf that kills | `{H}` + the four real free corner meeters, budget 6: **τ = 6.7348, η = +0.7348, ALIVE** | **PASS** — the leaf that kills 4 of 4 `l1_104` tuples at η = −1.0 does not touch the real family |

**The discriminating fact, stated plainly.**  The cascade's step (a) — *"both TR meeters are FREE
squares"* — is not a general truth; it is the consequence of `M(TR) = 0`.  A161's exact SAT proves
`M(c) = 0` at **all four** corners of `l1_104` (A141's coarser `box_misses_cell` could only prove it
at three), and proves `M(TR) = 1` at `l1_153`.  So the cascade *is* cell-specific in exactly the way
the PI hoped, and the canary is not killed because its `H` is itself a corner meeter.  Had the
cascade been coded with A141's coarse `M` it would have been *weaker*, not unsound; had it been
coded assuming `M = 0` everywhere it would have killed `l1_153`, and that is the step to watch.

---

## 2. The tree on `l1_104`

`H`: `x ∈ [2.46263075, 2.5674485]`, `y ∈ [2.1481775, 2.25299525]`, tilt `[30°, 45°]`; A115 record
`l1_104_plain_warm.t4.lp.json`, **τ = 10.000000 against budget 10, converged, minmass 1.000** — the
plain one-box LP has exactly zero slack.

### C0 — root
`ALIVE`.  Every case below is a child of `K0-BLOCKED`; the `K0-FREE` sibling is the (T) teleport
leaf of (R1), dead once `k1_00` closes (K0-O1).

### C1 — the structure, forced
* (R6) gap `+0.41185029` ⟹ the four corner crowds are disjoint.
* **`M(c) = 0` at all four corners** (A161 exact SAT; A141's cover agrees at BL/BR/TL and is
  inconclusive at TR).  So `H` is not a corner meeter.
* Hence **`11 = 8 corner meeters + H + exactly 2 further squares`**, and every corner is a
  *two-FREE-meeter* crowd.  This is the strongest structural statement A165 gets, and it is what
  makes each corner's branching a **pair** of cover boxes rather than a single one.

### C2 — the TR branching (the cascade's step (a))
Cover of the widened TR pose window at split depth 8 (deterministic bisection, widest of
`x, y, θ/60`; the leaf paths are a **complete prefix code**, Kraft sum exactly 1 — checked):

| corner | cover boxes OPEN | unordered pairs | after (OVL) | after (PAIR) | **cases** |
|---|---|---|---|---|---|
| **TR** | **82** | 3 403 | 522 | −22 | **500** |
| TL | 238 | 28 441 | 7 417 | −367 | 7 050 |
| BL | 248 | 30 876 | 8 606 | −412 | 8 194 |
| BR | 191 | 18 336 | 4 096 | −217 | 3 879 |

**The PI's premise is real and measured**: TR's cover is 3× smaller than the other three corners
and its pair count 14–16× smaller, because `H` sits on the TR diagonal and its A132 polygon core
`K'(H)` (area 0.655248, 40 certified vertices) blocks the approach.  Independent confirmation: of
35 402 drawn admissible poses that meet `int C_TR^w`, **25 157 (71 %) share a rational point with
`H`** — every one of them located in the cover's `witness` leaf and re-verified to contain that
leaf's point (checker C9).  This asymmetry is the whole content of "the cell is about the TR corner".

**And the PI's picture of the pair is right.**  Classifying each of the 82 TR cover boxes by which
wall it approaches along (`code/tree165.py: classify`): **55 TOP-side, 27 RIGHT-side, 0 diagonal**;
and of the 500 cases

| pair class | count | share |
|---|---|---|
| RIGHT + TOP (one meeter up the right wall past `H`, one along the top wall) | **434** | **86.8 %** |
| TOP + TOP | 66 | 13.2 % |
| RIGHT + RIGHT | 0 | 0 % |

i.e. the cascade's "a deep meeter up-right of `H` and a shallow meeter up-left of `H` poking into
`TR(0,0)` along the top wall" is the shape of 87 % of the branching, and the other 13 % is two
top-wall meeters.  Nothing sits on the diagonal.

### C3 — the top-wall chord row (the cascade's step (b)) — **a real bound on 37 % of the cases, never a kill**
Row over 24 exact rational lines per wall, all 500 TR cases (`results/geom_l1_104_d8_TR.jsonl`),
`rhs(l) = s0 − minchord(H, l) − minchord(TR_a, l) − minchord(TR_b, l)`:

| wall | min rhs | median | max | cases with rhs ≤ 1.9 (β = 1) | kills |
|---|---|---|---|---|---|
| **top** | 1.6740 | 1.9396 | 2.7963 | **220 of 500** | 0 |
| right | 1.6477 | 2.5232 | 2.7947 | 17 of 500 | 0 |
| bottom / left | 3.8771 | 3.8771 | 3.8771 | 0 | 0 |

**185 of the 500 cases have BOTH TR meeter boxes carrying a certified chord `≥ 1` on the best top
line**, giving exactly the PI's `rhs = s0 − 2 = 1.8771`, `β = ⌊rhs⌋ = 1`: *at most ONE further
square of the family fully crosses the top strip*.  On the other 315 cases one of the two meeters is
a shallow crosser and the row only gives `β = 2`.  `minchord(H, ·) = 0` on every top and right line
(`H` cannot be *guaranteed* to reach them from its box).  So step (b) is real, exact and certified —
on 37 % of the branching — and it is a bound, never a contradiction: 0 of 500 row kills at 3 boxes.

### C4 — the four-wall chord-row product (the cascade's step (c)) — **where the chain breaks**
(ROW) applied to each wall with the two crowds that wall can see — `top`: (TR, TL); `right`:
(TR, BR); `bottom`: (BL, BR); `left`: (BL, TL) — with 32 exact rational lines per wall.  All five
squares in a row are distinct by (R6) and `M = 0`, so the row is sound.

| wall | crowds | combos | killed | share | max violation |
|---|---|---|---|---|---|
| top | TR × TL | 500 × 7 050 | 144 277 | **4.09 %** | +0.5427 |
| right | TR × BR | 500 × 3 879 | 8 714 | 0.45 % | +0.7515 |
| bottom | BL × BR | 8 194 × 3 879 | 155 631 | 0.49 % | +0.5381 |
| left | BL × TL | 8 194 × 7 050 | 301 920 | 0.52 % | +0.5426 |

Four-cycle contraction (`TR —top— TL —left— BL —bottom— BR —right— TR`, a transfer-matrix product
exactly as in A150 §4): **1.0584·10¹⁴ surviving four-tuples of 1.1204·10¹⁴ = 94.5 %.**

**Why it breaks, precisely.**  Step (c) needs the TL corner's *second* meeter to be charged by the
top row.  It is not: a TL meeter must reach `y > s0 − 1 − w`, and by (TOP) it therefore **crosses**
every guard line `y = y_L > s0 − 1` — but its **chord** there may be arbitrarily small (a tilted
square dipping a single corner across the line).  So "`β = 1`, hence at most one more square fully
crosses the top strip" is TRUE and is **not** in contradiction with "TL carries two meeters": the
second TL meeter is a *shallow* crosser and costs the row `≈ 0`.  4.09 % of (TR, TL) case pairs are
the ones where both TL meeters happen to be band poses; those die, the rest do not.

### C5 — the LP-free area leaf — 20× short
`|U|` at 3 boxes `{H, TR_a, TR_b}`, raster pitch 0.02 × 30 tilts (A164 `geo164.uncoverable`,
certified inner approximation): **0.189–0.203** against `B0 = 4.031780`.  **No kill, and not close**
— the wastage leaf is a factor of 20 short at this conditioning depth.  This agrees with A164, which
LANDED while A165 was running (`done-negative`, 0 kills over all 71 alive gallery nodes): on
`l1_104` its `|U| = 0.129` at pitch 0.01 × 36 tilts, all of it in the east wedge between `K'(H)` and
`x = s0` — *the PI's location is right and the count is not* — and `|U|` only reaches the budget at
9–10 conditioned boxes, i.e. with 1–2 free squares left, where the LP is already cheap.  So the
cascade cannot borrow an area charge to fix step (c): A164 has measured that the charge does not
exist at the depth the cascade needs it.

### C6 — the leaf LP at the cascade's own nodes
`{H, TR_a, TR_b}`, budget `11 − 3 = 8`, exact cores, 120 s cap:

| case | τ | η | converged | verdict |
|---|---|---|---|---|
| `TR(0,71)` | 7.999999999999810 | −1.9·10⁻¹³ | no (cap) | ALIVE, zero slack |
| `TR(2,71)` | 8.000000000000000 | 0.0 | no (cap) | ALIVE, zero slack |

(the full sample is `results/lp3_l1_104_d8_TR.jsonl`; the run was stopped by this attempt's own
`PAUSE` sentinel after the third case.)  **Two cores at ONE corner plus `H` buy no slack at all** —
τ sits exactly at the budget, the same place the root sits.  This reproduces A143/A150's
measurement (one core at BL: η −0.044; two cores at BL: η −0.083; **four cores at four corners:
η −1.0 … −6.0**): the LP responds to cores that are *spread*, not to cores that are *stacked at one
corner*, and the cascade stacks them.

### C7 — the leaf LP at the SPREAD hypothesis: `{H}` + ONE meeter per corner, budget 6
This is A150's four-corner product with the cell's own `H` added, and it is the only leaf in A165
that kills.  Random tuples from the depth-8 covers (`results/lp5_l1_104_d8_spread.jsonl`):

| tuple | τ | η | converged | frozen `verify_case.py` | CPU-s |
|---|---|---|---|---|---|
| `spread00` (TR 4, TL 15, BL 55, BR 18) | 5.000000 | **−1.0000** | yes | FAIL | 73.0 |
| `spread01` (126, 59, 22, 109) | 5.000000 | **−1.0000** | yes | **PASS** | 14.9 |
| `spread02` (228, 172, 40, 148) | 5.000000 | **−1.0000** | yes | FAIL | 59.1 |
| `spread03` | 5.000000 | **−1.0000** | yes | FAIL | 171.0 |

**4 of 4 converged kills at η = −1.0000 exactly, one certified by the FROZEN verifier**, against
A150's 63 % kill rate without `H`.  Exact-core half-sides: `a(H) = 0.3804`, `a(corner) ≈ 0.300`.
The three FAILs are the lab's standard "LP-dead, certificate pending" — they need the A13/A14
separation loop with more rounds, not a different core (A150 §5 measured the same failure mode and
showed it is not a margin problem).

**The canary at the same leaf.**  `l1_153`'s own five-box spread node — the four real free corner
meeters of Trump's image `g4` plus `H` — gives **τ = 6.7348, η = +0.7348: ALIVE**
(`results/lp5_l1_153_d8_spread.jsonl`).  So the leaf that kills every `l1_104` tuple tested does not
touch the tuple the one existing family reaches, exactly as A150's Trump tuple came out at η = +1.08.

### C8 — the coarseness ladder: where the spread LP stops deciding
The spread leaf is a **cover** of K0-BLOCKED (each corner has at least one meeter, so choosing one
box per corner covers every K0-BLOCKED packing), so its price is `∏_c N_c · t`.  Measured on
`l1_104` (`results/lp5_l1_104_d*_spread.jsonl`):

| split depth | cover boxes (TR, TL, BL, BR) | `a` at a corner | product | η measured | kills |
|---|---|---|---|---|---|
| 3 | 6, 8, 8, 8 | 0.048 | 3 072 | +1.0, +3.0, +2.5, +2.0 | **0 of 4** |
| 4 | 12, 16, 16, 16 | 0.054–0.083 | 49 152 | +1.0, +2.0 | **0 of 2** |
| 8 | 82, 238, 248, 191 | 0.300 | 9.24·10⁸ | **−1.0 ×4** | **4 of 4** |

The crossover is A150's exactly: the LP decides at `a ≈ 0.3` and is silent at `a ≤ 0.08`, and the
cover that reaches `a ≈ 0.3` has ~10² boxes per corner.  **The cheap covers do not decide and the
deciding cover is 10⁹ nodes.**

---

## 3. Verdict on `l1_104`

**`l1_104` SURVIVES A165.  The cascade is sound at every step and it does not close.**  The chain
breaks at step (c), for a reason that is a statement about the geometry and not about effort: a
corner's second meeter is not forced into the wall band, so the chord row cannot charge it.

The cascade's residue, priced:

| route | leaves | per-node LP | price |
|---|---|---|---|
| A165 as built: pairs at all four corners (8 cores + H, budget 2) | **1.06·10¹⁴** | — | absurd |
| one meeter per corner + `H` (5 boxes, budget 6) — A150's product for *this* cell | `82 · 238 · 248 · 191 = 9.24·10⁸` (no D4 quotient: the cell breaks the symmetry) | ≥ 8.7 s measured best, 240 s cap on alive nodes | **≥ 2.2·10⁶ CPU-h** |
| A150's own four-corner product (no `H`), for reference | 1.90·10⁸ D4 orbits | same | ≥ 4.6·10⁵ CPU-h |
| the interior-first `k0_00` tree, for reference | — | — | 9 400–12 000 CPU-h (`docs/budget.md` k0 row) |

So the cascade is **two to three orders of magnitude worse than the tree it was meant to shortcut**,
for the same reason A150 was: the corner crowd space at the resolution where the LP decides is
6-dimensional per corner, and there is no counting leaf that collapses it.

**What would change the verdict.**  A leaf that charges a *shallow* corner meeter.  The row charges
length along a line; a shallow meeter has a small chord but a *large* footprint in the corner
**cell**.  The natural candidate is A161's Lemma CL read the other way round — `LANE_out`, the
number of pairwise-disjoint NON-band squares that can meet a widened corner box.  Measured here:
`LANE_out(TR) ≥ 2` on `l1_104` (A141 already records `LANE_K′ ≥ 2` at all four corners of this
cell), so `β + LANE_out + M = 1 + 2 + 0 = 3 ≥ 2` and the CL leaf stalls too.  The missing lemma is
an *area* or *occupancy* charge on the corner box that a shallow meeter cannot dodge; A164's `|U|`
is the right shape and is 20× too weak.

---

## 4. What generalises (n-general, no `n = 11` and no `s0`)

1. **The `M(c)` upgrade is free and belongs everywhere.**  Replacing A141's `box_misses_cell` by
   A161's `box_misses_cell_exact` in the k0 corner pass turns `M(TR)` from *undecided* to **0** on
   `l1_104` — i.e. it upgrades the corner crowd from "two squares, one of which may be the
   conditioned one" to "two FREE squares", which is what makes any corner-pair branching legitimate.
   This is one line in A141's `cond_can_meet`, costs nothing, and should be re-run over the whole
   k0 corner corpus and over A57/A60's slot pass (A161 already reports the same upgrade turning
   `M = 1` into `M = 0` on pinned nodes).
2. **The four-wall chord-row product is a cheap, sound, composable leaf** for any class with
   crowded corners: the constraint lives on the EDGES of the four-corner cycle, so the survivor
   count is a transfer-matrix contraction and never needs the product enumerated (A150 §4's
   bookkeeping, A144's row as the edge predicate).  Measured value on a k0 cell: 4–5 % of the
   product.  Worth running wherever a product cover is being counted; not worth building a tree on.
2b. **(TOP), the wall-strip fact**, is `n`-general and worth stating once: *no admissible unit
   square lies entirely beyond a wall guard line placed within `1` of that wall* (`c_y ≤ s − h`,
   `h ≥ 1/2`).  Hence every square that reaches into the wall strip crosses the line, which is what
   makes a wall row a **complete** charge on the strip's occupants — and, read negatively, it is
   also why the row is weak: crossing is forced but a chord `≥ 1` is not.
3. **"Stacked cores buy nothing; spread cores buy a unit of η."**  A143 (1 core at one corner:
   −0.044), A143 (2 cores at one corner: −0.083), A165 (2 cores at one corner + an interior core:
   **0.000**), A150 (4 cores at 4 corners: −1.0 … −6.0).  The LP's dual is a covering measure on the
   container; cores that overlap each other's exclusion shadow are nearly redundant.  **Rule for
   every future k0/k5 node: spend the conditioning budget on cores that are pairwise far apart, and
   never on a second core at a corner that already has one.**
4. **The cascade shape itself is reusable, and its break-point is a named gap.**  "Corner doubly met
   ⟹ two boxes ⟹ wall row ⟹ next corner doubly met ⟹ …" is exactly the right shape; what it needs
   to close is a leaf that charges a **shallow** meeter (large cell footprint, small chord).  Naming
   that gap is the useful output: it is the same gap that stalls A161's Lemma CL on
   `k5_16_interior_Y0842/BL(1,0)` and the 28 of 44 A141 near-misses with realised two-crowd
   witnesses.

---

## 4b. Sample lines of `results/cascade165.jsonl` (644 case lines: 528 for `l1_104`, 116 for `l1_153`)

A live level-1 case — note the classification: `TR_a` comes up the RIGHT wall (depth 1.113 into the
cell, tilt 78.75–90°), `TR_b` along the TOP wall (depth 0.14 in `x`, 1.22 in `y`, tilt 22.5–33.75°),
which is the PI's "deep meeter / shallow meeter" pair:

```json
{"node":"l1_104/C2/TR(0,71)","level":1,
 "roles":{"H":[2.46263075,2.5674485,2.1481775,2.25299525,30.0,45.0],
          "TR_a":[3.2230069,3.377084,3.0689298,3.377084,78.75,90.0],
          "TR_b":[2.1444671,2.2985443,3.0689298,3.377084,22.5,33.75]},
 "budget":8,
 "forced_by":["K0-BLOCKED at TR with M(TR) = 0 (A161 exact SAT)","A141 cover box 0 and 71"],
 "verdict":"ALIVE(LP)",
 "evidence":{"tau":7.99999999999981,"eta":-1.9e-13,"converged":false,"wall_s":126.7,
             "row_min_rhs":1.7946918898,"rows":{"top":1.7946918898,"right":2.5174518650,
                                                "bottom":3.877084,"left":3.877084}},
 "classify":{"TR_a":{"side":"RIGHT","depth_x":1.1134,"depth_y":1.1134,"tilt":[78.75,90.0],
                     "minchord_top":0.0},
             "TR_b":{"side":"TOP","depth_x":0.1405,"depth_y":1.2190,"tilt":[22.5,33.75],
                     "minchord_top":0.3614}}}
```

A dead level-2 case — the chord row on one exact rational top-wall line, five boxes
(`H` + the TR pair + the TL pair), four of them carrying a chord above 1.10:

```json
{"node":"l1_104/C3/top-[17, 72]-[126, 188]","level":2,"budget":6,
 "forced_by":["A144 LINE-1 on the top wall line 291373/100000"],
 "verdict":"DEAD(C, chord row A144 LINE-1)",
 "evidence":{"row":{"off":"291373/100000","orient":"h",
   "minchords_f":[0.0,1.1038139901,1.1038139901,1.1038139901,1.1083047070],
   "rhs":"-36417475801595738308895295677853/67108864000000000000000000000000",
   "rhs_f":-0.5426626772,"beta":-1},"exact_rhs_negative":true}}
```

`0.0 + 1.1038·3 + 1.1083 = 4.4197 > s0 = 3.877084`: five interior-disjoint squares cannot all carry
those chords on one line, so the case is contradictory with no LP.

---

## 5. Files

| file | what |
|---|---|
| `code/cas165.py` | the library: node loading, widened corner cells, (TOP) facts, the chord row, the meeter cover, the two pair prunes, the exact `box_misses_cell` wrapper |
| `code/cascade165.py` | stages `cover` / `pairs` / `geom` / `lp3` |
| `code/rowprod165.py` | the four-wall chord-row product and its transfer-matrix contraction |
| `code/lp5165.py` | the leaf LP at `spread` (one meeter per corner + `H`) and `stack` (a pair at each of two corners) hypotheses |
| `code/certs165.py` | emits the `cascade_Mzero_v1`, `cascade_cover_v1` and `cascade_row_v1` certificates and the SHA-256 manifest |
| `code/trump165.py` | the Trump witness for the canary |
| `code/tree165.py` | assembles `results/cascade165.jsonl` |
| `code/fig165.py` | the A148-style panel figure |
| `code/check165.py` | the INDEPENDENT checker (C1–C9) |
| `code/probe165.py` | the T0 measurement probe |
| `results/` | `cover_*`, `pairs_*`, `geom_*`, `rowprod_*`, `lp3_*`, `lp5_*`, `cascade165.jsonl`, `check165_*` |
| `certs/` | the chord-row `(C)`-leaf certificates and the LP certificates emitted by `lp150.certify` |
