# A166 — method: the nearest-corner sub-tree, the cover it needs to be sound, and every stage's exact statement

Companions: `docs/proofs/k0_route.md` §§3, 4.1–4.4 (K0-FREE, K0-WIDEN, K0-BLOCKED, K0-D4, K0-PAIR),
`attempts/A143-corner-first-k0/notes/composition.md` (the one-corner root, its (R1)–(R5), the pair
chain P2/P1/P1s, and §4's Trump reading), `attempts/A150-four-corner-product/notes/composition.md`
(the four-corner product, (R6), the LP-slack measurement this is compared with),
`attempts/A155-exact-cell-corner-band/` (the pad-parametrised cover, `cells155.py`),
`attempts/A131-pin-clip/` (the clip), `attempts/A158-slot-split/notes/addendum_b.md` (the mutual-clip
rule and the exact-1 accounting), `attempts/A132-polygon-core/` (`K'`),
`attempts/A135-polycore-verifier/` (the exact axis core), `attempts/A161-chord-lane/`
(`box_misses_cell_exact`), `attempts/A141-polycore-lane/` and `attempts/A159-k0-nearmiss-joint/`
(the TR near-miss corners and `B_meet`), `docs/shadows/k0v4/` (the eleven pages).

---

## 1. The metric, and the one-line surprise

For a cell whose conditioned box is `B_H = [x0,x1] x [y0,y1] x [th0,th1]`, put
`z_H = ((x0+x1)/2, (y0+y1)/2)`. The **nearest corner** is `argmin_c |z_H - p_c|` over the four
container corner POINTS `p_BL = (0,0)`, `p_BR = (s0,0)`, `p_TR = (s0,s0)`, `p_TL = (0,s0)` (ties would
break BL < BR < TR < TL; none occurs — the smallest margin to the runner-up is 0.042 on
`l2_p65_101`). The tilt window plays no part.

> **[M] The nearest corner is `TR` for all eleven cells, with `d` from 1.8536 to 2.3943 — and for 117
> of the 119 remaining open k0_00 cells.**

This is not an accident, and for A38's cover it is a one-line **[T]**:

> **Lemma A166-0.** A38's level-1 cover (`attempts/A38-root-power/notes/design.md`) is the 8 x 8 grid
> on the D4 **fundamental triangle** `T = { s0/2 <= y <= x <= s0/2 + 0.8385421 }` (upper triangle,
> 36 position cells x 6 tilt windows = 216 nodes). For any `z = (x, y)` with `y >= s0/2`,
>
>     |z - p_BR|^2 - |z - p_TR|^2 = y^2 - (s0 - y)^2 = s0 (2y - s0) >= 0 ,
>
> and symmetrically `|z - p_TL| >= |z - p_TR|` because `x >= y >= s0/2`, and `|z - p_BL| >= |z - p_TR|`
> because both coordinates are `>= s0/2`. So `TR` is the nearest corner of every point of `T`, with
> equality against `BR` only on the edge `y = s0/2`; every cell's box CENTRE has `y >= s0/2 + 0.0524`,
> so the argmin is strict. ∎

So the "per-cell nearest corner" of the brief is ONE corner for the whole interior tree: A166's
sub-tree is the **same** sub-tree at every node, the corner never has to be chosen, and it is exactly
the corner A141/A159 found at NEAR-MISS on five of the eleven (`TR(0,0)`). The two exceptions in the
pool (`s1cor_near_b178`, `s2_near_046_619`, nearest corner `BL`) are A85 corner-seed records, not A38
level-1 cells.

## 2. The cover of a node, and why it needs two branches

Node hypothesis: `F` is an 11-square packing in `[0, s0]^2` (the dilate `Δ_λ P` of a window packing),
some square `H` of `F` has pose in `B_H`, and — Lemma K0-BLOCKED (`k0_route.md` §4.2) — two DISTINCT
squares `Q_1 != Q_2` of `F` meet `int B_TR^w`, the corner box widened by the K0-WIDEN pad
`w` (`w = w_max = 0.0255101` for the whole window, `w = 0` at the fixed side `s0`). Each `Q_i` has a
pose in the corner reach set `R_TR^w`, which A143 (R3) covers by the **216 cells** = 6 x 6 positions
on `Z(w) = [1/2, a_w + sqrt2/2]^2` x 6 tilt windows of 15 deg, each clipped against the container and
against "the square meets `[0, a_w]^2`" (A155's `cells155`, pad a parameter).

**The transpose quotient of A143/A150 is NOT applied.** It quotients by the corner's stabiliser in
D4, which fixes `TR` but MOVES `B_H`; with `H` fixed the node is not symmetric, so the pair cover runs
over all `216·217/2 = 23 436` unordered pairs (`A = B` included as a cover element; (P2) always kills
it).

Classify each cover cell `X` (pulled to global coordinates through A150's rotation frames):

| verdict | statement proved | consequence |
|---|---|---|
| `DEAD_R` | A161 `box_misses_cell_exact(X, B_TR^w)`: EVERY pose of `X` gives a square whose interior misses `int B_TR^w` | `X` hosts no meeter at all |
| `DEAD_H2` | `maxdist(R_H, R_X) < 1` and `X ∩ B_H = ∅` as parameter boxes | every square in `X` overlaps every square in `B_H`, so it IS `H`; but it cannot be `H` — (C) |
| `DEAD_H1` | `K'(B_H)` meets `K'(X)` (A132 exact polygon cores) and `X ∩ B_H = ∅` | same |
| `DEAD_CLIP` | A131's clip of `X` against the largest axis-aligned square inscribed in `K'(B_H)` about `B_H`'s midpoint (A158's rule) empties `X`, and `X ∩ B_H = ∅` | same |
| `DEGENERATE_*` | the same three tests fire but `X ∩ B_H != ∅` | a square with a pose in `X` IS `H` — `X` survives only in the degenerate branch |
| `ALIVE` | none of the above | `X` may host a corner meeter distinct from `H` |

`maxdist(R_H, R_X)` is exact: for rectangles the largest `|p-q|` is `hypot(max|dx|, max|dy|)` with the
two maxima taken independently over the corner combinations. Two unit squares with disjoint interiors
have centre distance `>= 1` (any separating direction `n` gives `|d.n| >= h_1(n) + h_2(n) >= 1`), and
two unit squares of a packing that overlap are the SAME square — that is what turns `H2`/`H1`/`CLIP`
from "contradiction" into "identification", and it is the step that makes the two-branch cover
necessary.

**Then exactly two kinds of child exist, and together they are a COVER:**

* **(a) budget 8.** `Q_1, Q_2` both `!= H`. Neither can lie in a `DEGENERATE` cell (that would force
  it to be `H`) nor in a `DEAD` cell, so both lie in `ALIVE` cells and the unordered pair survives
  A143's pair chain re-run on the CLIPPED boxes. Hypothesis `[B_H, X_1^clip, X_2^clip]`, three
  distinct squares, budget `11 − 3 = 8`.
* **(b) budget 9, DEGENERATE.** One of them IS `H`. Then `H` meets `int B_TR^w` — decided exactly by
  A161's `box_misses_cell_exact(B_H, B_TR^w)` — and the other, `Q != H`, lies in an `ALIVE` cell.
  Hypothesis `[B_H^meet, X^clip]`, two distinct squares, budget `11 − 2 = 9`, where `B_H^meet` is the
  bounding box of the sub-boxes of `B_H` (4 x 4 x 4) that are not certified to miss the corner box —
  A159's `B_meet`, with A161's stronger exact test in place of A141's.

> **A166's first correction to the brief. The brief's "3-box node at budget 8" alone is NOT a cover,
> and taking it for one would have produced an UNSOUND kill of `l1_153` (see `notes/canary.md`): the
> Trump image that realises `l1_153` has `H` ITSELF as one of its two widened TR meeters. `K0-FREE`
> is dead by teleport, but "the corner is doubly met" does not say that both meeters are different
> from the conditioned square.**

If (b) is impossible — `H` certified to miss the widened corner box — then (a) alone is the whole
cover, and an EMPTY (a) is a (C) leaf: the node dies with no LP and no certificate. That is the whole
mechanism A166 buys, and §4's table says on which cells it is available.

### 2a. The pair stage, on the clipped boxes — and the ORDER, which matters

The coordinator's reinforcement (2026-09-08, from the PI's review of A165): *every pair box must be
clipped against `K'(H)` and against the other pair box's exact core (A158's mutual clip, per tilt
sub-bin) BEFORE the pair leaf, any chord/lane test, any figure and any LP; a box all of whose poses meet
`K'(H)` is empty and the case dies.* **A166 does this, and the run reported here is the version that
does it in that order** (`--nsub_clip 4`, mutual clip first):

1. `K'(H)` clip of every cover box, per tilt sub-bin (`nsub = 4`), A131's machinery with A158's
   inscribed-axis-core rule — a box the clip empties is `DEAD_CLIP` (or `DEGENERATE_CLIP` if it could
   BE `H`), i.e. the case dies, exactly as asked;
2. then, per pair, the MUTUAL clip (each box against the other's core, per tilt sub-bin), and the
   surviving boxes are rebuilt (`K'` and the four sub-bin `K'`s recomputed on the clipped boxes);
3. only then the pair leaf `(P2)/(P1)/(P1s)`, the reach test again, the exact-core budget gate, the
   figures and the LP — every one of them on the mutually clipped boxes.

The earlier ordering (mutual clip last, `nsub = 1`) is kept in `results/v1/` for comparison: putting the
mutual clip first and refining it to 4 sub-bins moves `MUT` from 1 to 8 pair kills on `l1_071` and from
0 to 10 on `l1_104`, empties one further cover box on `l1_124` and one on `l1_158`, and lowers the
survivor counts by 1–5 per cell. It changes no verdict. Kept fractions per box per cell are recorded in
each `survivors166_*.json` (`kept_H_clip`, `kept_mutual`, and the per-pair `kept_frac` list) and
summarised in `notes/tables.md`.

**Figures.** `code/draw166.py` follows the same instruction: `K'` of each box is drawn SOLID as the
box's core, and the pose union (the centre box) is a thin dashed outline only, with the legend saying it
is not feasible space.

### 2b. The pair stage, stated

A143's chain, unchanged in statement, run on the clipped boxes (hence strictly stronger than
A143/A155's version): `(P2)` `maxdist(X_1^clip, X_2^clip) < 1`; `(P1)` `K'(X_1^clip)` meets
`K'(X_2^clip)`; `(P1s)` A131's per-tilt-sub-bin refinement at `nsub = 4` — every surviving sub-pair
contradictory. Then two additions:

* `(MUT)` A158's **mutual clip**: each clipped corner box clipped against the other's inscribed axis
  core (the two corner squares are distinct by K0-BLOCKED, so this is a plain discard), followed by
  A161's reach test again on the result.
* `(DIST)` the **budget gate — and it is an UNDECIDED, not a kill**: the three EXACT axis cores `K(B_H)`, `K(X_1)`, `K(X_2)` (A135
  `exact_a`) must be pairwise interior-disjoint, or the frozen certificate's bridge does not give
  three DISTINCT witnesses at budget 8. This is checked by A166's own exact rational SAT over the
  four edge normals (`geo166.cores_disjoint_exact`) — **not** by
  `exactcore.cores_pairwise_disjoint`, whose `x`/`y`-only comparison is written for axis-aligned pin
  cores and is not a sound disjointness test for the tilted cores here. (Worth recording: A150's
  four-corner LP and A158b's seven-box gate both used that function on tilted cores.)

  **`DIST` is the one stage that is not a kill.** A pair whose cores are not certifiably disjoint is
  *undecided* — it cannot be run at budget 8 in the frozen schema, and A166 removes it from the
  survivor list, so it must be counted separately and re-decided (by splitting the boxes, or as a
  budget-9 sub-case) before any node containing one is called dead. Measured: `DIST` fires on
  **3 pairs in total** over the eleven at the window pad (`l1_104` 1, `l2_p65_101` 2) and **0 at
  pad 0**; both cells keep 139 and 237 other survivors, so no verdict in this attempt depends on it.
  These are float/exact boundary cases: `K(B) ⊆ K'(B)`, so `K(X_1)` meeting `K(X_2)` would have
  triggered `(P1)` first, hence the failure must be between `K(B_H)` and a `K(X_i)` whose `K'` float
  depth against `K'(B_H)` came out `≤ 0` by a hair.

## 3. Lemma A166-1 — the nearest-corner squeeze, and why it is not the mechanism

Working in `TR`'s local frame, if `Q_1 != Q_2` both meet `int B_TR^w` and NEITHER is `H`, then
`z_{Q_i} in Z(w)`, `|z_{Q_i} − z_H| >= 1` and `|z_{Q_1} − z_{Q_2}| >= 1`; since `z_H in R_H`, both lie
in

    S*(R_H) := { p in Z(w) : max over the four corners v of R_H of |p − v| >= 1 } ,

so `diam S*(R_H) < 1` forces `H` itself to be a meeter. `p -> max_v |p − v|` is convex, so its
supremum over a grid square is at a corner; covering `Z(w)` by an exact rational `n x n` grid, marking
a square when the max over its four corners is `>= 1`, and taking the hull diameter of the marked
squares' corners gives a SOUND upper bound (`code/squeeze166.py`).

**[M] Measured (`results/squeeze166.json`, `n = 160`): the squeeze fires on 1 of 22 (cell, pad)
pairs — `l1_124` at pad 0, bound 0.7255 — and nowhere at the window pad, where the bounds run
1.2764 … 1.7432.** The reason is geometric and worth recording so nobody re-derives it: `Z(w)` is
1.2326 wide at the window pad, so `Z(w) \ B(z_H, 1)` generally has TWO components (near two opposite
corners of `Z`) whose separation exceeds 1. The pointwise squeeze that a hand calculation suggests
(0.59 for `l1_153`) is an artefact of looking at one component.

**The box-level cover in §2 is the sharper instrument, and it is what fires**, because `K'` (a
polygon) is a far stronger obstacle than a centre-distance bound: on `l1_153` the cell at local
`(5,0)` survives `H2` at `maxdist = 1.1075` and dies on `H1` at `K'` depth `1.09e-3`.

## 4. What the geometry is worth (pad `w_max`, the window)

`results/subtree166_wmax.jsonl`, `results/survivors166_wmax_*.json`. The shared pair census
(A143's chain on the 23 436 unordered pairs of the unclipped cover, computed once per pad because the
local cover and the tests are frame-independent) is

| pad | pairs | (P2) | (P1) | (P1s) | alive |
|---|---|---|---|---|---|
| `w_max` | 23 436 | 15 764 | 2 616 | 812 | **4 244** |
| `w0` | 23 436 | 16 372 | 2 609 | 809 | **3 646** |

(A143/A150/A155 report the same census on the 11 772 TRANSPOSE-CANONICAL pairs: 2 134 alive at
`w_max`, 1 833 at `w0`. The numbers here are the un-quotiented ones, as §2 requires.)

> **[M] A free 26 % improvement to A143/A150/A155's corner cover, independent of `H` and of the corner.**
> A155's `clip_box` (the reach clip A143 uses) leaves all 216 cells non-empty at both pads, because it
> separates the square from the corner box only along the corner box's own two normals, via
> `h(theta) = (cos + sin)/2`. A161's `box_misses_cell_exact` — the same test plus the SQUARE's two edge
> normals, every bound an exact Fraction — certifies that **16 of the 216 cells contain no pose that
> meets the corner box at all**, at BOTH pads and identically:
>
>     (3,5,5) (4,5,2) (4,5,3) (4,5,4) (4,5,5) (5,3,0) (5,4,0) (5,4,1) (5,4,2) (5,4,3)
>     (5,5,0) (5,5,1) (5,5,2) (5,5,3) (5,5,4) (5,5,5)
>
> i.e. the far-corner block of the zone at the tilts where the square cannot stretch far enough. That
> removes **1 118 of the 4 244 alive pair cells at `w_max` (26 %) and 970 of 3 646 at `w0` (27 %)** for
> free, before `H` enters at all. A143/A150/A155's censuses should be read as 3 126 / 2 676.

Then per cell, at `w_max`:

| cell | `d(z_H, TR)` | DEAD_R | DEAD_H2 | DEAD_H1 | DEAD_CLIP | DEGEN | ALIVE | pairs alive in A143's chain | after A166's stages |
|---|---|---|---|---|---|---|---|---|---|
| `l1_158` | 1.8536 | 16 | 182 | 9 | 1 | 6 | **2** | 0 | **0** |
| `l1_159` | 1.8536 | 16 | 182 | 8 | 0 | 6 | **4** | 0 | **0** |
| `l1_124` | 1.9262 | 16 | 160 | 20 | 1 | 12 | **7** | 0 | **0** |
| `l1_153` | 1.9319 | 16 | 161 | 15 | 5 | 3 | **16** | 0 | **0** |
| `l1_148` | 2.0127 | 16 | 137 | 22 | 1 | 5 | **35** | 25 | **25** |
| `l2_p114_001` | 2.0387 | 16 | 160 | 25 | 0 | 2 | **13** | 17 | **16** |
| `l1_104` | 2.1600 | 16 | 106 | 24 | 0 | 4 | **66** | 160 | **139** |
| `l2_p74_001` | 2.2646 | 16 | 94 | 35 | 1 | 0 | **70** | 67 | **60** |
| `l1_071` | 2.3075 | 16 | 86 | 20 | 0 | 0 | **94** | 388 | **371** |
| `l2_p65_111` | 2.3526 | 16 | 80 | 32 | 0 | 0 | **88** | 202 | **178** |
| `l2_p65_101` | 2.3943 | 16 | 74 | 25 | 4 | 0 | **97** | 260 | **237** |

Two readings.

1. **The cut is enormous and, on the eleven, monotone in `d(z_H, TR)`** (it is NOT monotone over the
   whole pool — `node_192` at `d = 1.8654` keeps 10 pair cells and `node_191` at `d = 1.9489` keeps 20,
   so what matters is WHERE in the zone `z_H` sits, not only how far). The generic corner-first pair root has
   4 244 live pair cells; conditioning on `H` leaves 0 … 371, i.e. a factor `11` to `∞`. The whole
   effect is `H2`/`H1`: 99–191 of the 216 cover cells (46–88 %) cannot hold a corner meeter distinct
   from `H` at all, because they are within reach of `H`'s own square.
2. **And it is exactly anti-correlated with the availability of the (C) leaf.** The four cells whose
   budget-8 branch is EMPTY are the four nearest the corner — and those are precisely the cells whose
   `H` CAN meet the widened corner box, so branch (b) survives and the (C) leaf is not available.
   The six cells where `H` provably misses the corner box (so branch (a) is the whole cover and an
   empty (a) would kill the node outright) all have `d >= 2.01` and 25–371 surviving pair cells.

`H`'s reach, decided exactly by A161's `box_misses_cell_exact(B_H, B_TR^w)`:

| `H` can meet `int B_TR^w` | cells |
|---|---|
| **no** (certified miss; branch (b) impossible; budget-8 cover COMPLETE) | `l1_071`, `l1_104`, `l1_148`, `l2_p65_101`, `l2_p65_111`, `l2_p74_001` |
| **yes** | `l1_124`, `l1_153`, `l1_158`, `l1_159`, `l2_p114_001` |

The "yes" list is A141/A159's five TR NEAR-MISS cells, reproduced from a different direction, and the
"no" list is A141's `M = 0` reading turned into a proof: A141/A148 record `TR(0,0): M 0?` for those
six (`docs/shadows/k0v4/review_k0v4.csv`, `lane_bounds`), a sampled 0 with a question mark; A161's
full separating-axis test over the parameter box **certifies** it. (A159 §6c reported
`n_miss_pieces = 0` on its near-miss classes with A141's weaker `box_misses_cell`, which separates
only along the cell's own normals; the six here are decided on the SQUARE's normals, which is exactly
the gap A161 was built to close.)

## 5. The consequence for a DEAD verdict

    cell DEAD  <=>  (every budget-8 pair cell dead)  AND  ( H certified to miss int B_TR^w
                                                            OR every budget-9 degenerate node dead ).

So of the eleven:

* four (`l1_124`, `l1_153`, `l1_158`, `l1_159`) now carry **only** a budget-9, two-core hypothesis
  with `H` pinned to `B_H^meet` and the partner pinned to one of 3–20 cover cells — a strictly
  stronger node than A115's, and the strongest statement A166 gets on them without an LP: *if either
  of the two TR meeters is not `H`, the node is contradictory*;
* six carry a complete budget-8 cover with 25–371 pair cells and need the LP;
* `l2_p114_001` needs both branches (16 pair cells at budget 8, plus branch (b)).

## 5b. One rounding detail, audited (`code/clipaudit166.py`)

A131's `pinclip.clip_node` takes the pin core's half-side as a RATIONAL. The first version of
`geo166.clip_against_core` produced it with `Fraction(str(a)).limit_denominator(1e9)`, which can round
**up** by ~1e-9; a pin core larger than the square inscribed in `K'(B_H)` would let A131's octagon claim
an overlap that need not happen — an unsound clip. (The overshoot is far inside A132's own
`shrink = 1e-6` inward offset of `K'`, so no recorded verdict can be wrong, but that is a margin
argument, not a proof.) The code now FLOORS the half-side onto a 1e-12 grid, and the audit re-runs
every clip with the floored value:

* **emptiness changes: 0 of 505 clips at `w_max` and 0 of 513 at `w0`** — so no `DEAD_CLIP` /
  `DEGENERATE_CLIP` verdict moves;
* clipped boxes shift by at most **3.906e-12**, always OUTWARD (the floored pin removes less), i.e.
  every recorded clipped box is a SUBSET of the sound one by ≤ 4e-12.

A subset hypothesis is a problem only for a KILL, and **A166 banks none**: the one converged budget-8
kill has a FAILing certificate and is recorded as "LP-dead, certificate pending". Moreover the four
cells whose budget-8 branch is EMPTY — the attempt's headline geometric result — have `P2 = P1 = P1s =
MUT = DIST = 0` at the pair stage, so their emptiness comes entirely from the unclipped cover (A143's
own chain) and the cell-level `R`/`H2`/`H1` stages, none of which uses the clip at all. The ~66
post-clip pair deaths over the other seven cells can only ever ADD survivors when corrected, and those
cells are ALIVE either way.

## 5a. The independent checker

`code/check166.py` shares nothing with the emitter: its own cover derivation from the definition of
`Z(w)` and the clip, its own separating-axis test written from support functions (no `polycore`, no
`caselp`, no `chordlane`, no `pinclip`), its own sampling. It reads only the emitter's result files and
re-decides each claim. `results/check166_wmax.json`, log `logs/check166_wmax.log`:

| check | what it re-decides | result |
|---|---|---|
| C1 | the cover: drawn container-admissible poses that meet `int B_TR^w` must land in a cover cell whose CLIPPED box contains them | 20 000 drawn, **2 109 meeting poses, 0 misses** |
| C2 | every `DEAD_R` cell: no drawn pose of it meets `int B_TR^w` | 16 cells x 4 800 poses per cell, **0 bad** |
| C3 | every `DEAD_H2`/`DEGENERATE_H2`: `maxdist` recomputed by brute force over the 16 corner pairs, then drawn pose PAIRS must always overlap | 74–188 cells, 4 213–9 639 pairs per cell, **0 bad, 0 maxdist disagreements** |
| C4 | every `DEAD_H1`/`DEGENERATE_H1`: drawn pose pairs must always overlap | 8–35 cells, 633–3 572 pairs, **0 bad** |
| C5 | every `DEAD_CLIP`: no drawn pose of the cell is free of `H` | 0–4 cells, up to 1 200 poses, **0 bad** |
| C6 | the survivors: search for a REALISED triple (`h in B_H`, `q_1, q_2` in the two cells, all in the container, pairwise interior-disjoint, both `q_i` meeting `int B_TR^w`) | hits on `l1_071` 5/40, `l2_p65_101` 6/40, `l2_p65_111` 6/40 pair cells, and 1/8 degenerate cells of `l1_124` — so those survivors are not artefacts; 0 hits elsewhere is evidence, never a kill |
| C7 | contradiction guard: any realised configuration inside a cell the emitter called DEAD fails the run loudly | **no failure** |
| C8 | the Trump canary on all eight images (see `notes/canary.md`) | pass |

### The drawn → tested → hits line for the headline, without the cover

`code/sampleline166.py`, `results/sampleline166_wmax.json`, `logs/sampleline166.log`. The claim being
tested is the one the four EMPTY-branch cells rest on — *`H` in `B_H` plus TWO squares other than `H`
meeting `int B_TR^w` is impossible* — and it is tested on POSES, not on the cover: `h` drawn uniformly
in `B_H`, `q_1, q_2` drawn uniformly over `Z(w) × [0, 90°)` and kept only when admissible and meeting
the corner box, with A166's own from-scratch SAT. 40 000 draws per cell:

| cell | branch (a) | H admissible | candidate triples reached | hits |
|---|---|---|---|---|
| `l1_124` | empty | 40 000 | **0** | 0 |
| `l1_153` | empty | 40 000 | **4** | 0 |
| `l1_158` | empty | 40 000 | **0** | 0 |
| `l1_159` | empty | 40 000 | **0** | 0 |
| `l1_071` (control) | 371 cells | 40 000 | **4 112** | 0 |
| `l2_p65_101` (control) | 237 cells | 40 000 | **7 834** | 0 |

"Candidate triples reached" counts the draws that got as far as a corner meeter interior-disjoint from
`H`, so it measures the supply the claim denies: it is **three orders of magnitude thinner** on the four
empty cells than on the two controls. (The `hits` column is 0 everywhere because a uniform draw of TWO
mutually interior-disjoint meeters is rare even where they exist; the controls' survivors ARE realisable
— check C6 above found explicit triples on 5 of 40 and 6 of 40 of their pair cells by searching inside
the cells.) `REFUTED = False`: a single hit on an empty-branch cell would have withdrawn the headline.

**`ALL_OK = True` at BOTH pads** (`results/check166_wmax.json`, `results/check166_w0.json`; at `w0` the
cover draw keeps 1 973 meeting poses with 0 misses and every stage is again 0 bad). The one thing the
checker cannot do is re-derive `K'` (it would have to
re-implement A132's certified polygon construction), so the `H1` and `P1` verdicts are corroborated by
sampling rather than re-proved; every other verdict is re-decided from scratch.

## 6. Files

`code/cells166.py` (the eleven, the metric, the frames, the pad-parametrised cover),
`geo166.py` (the stages and the exact core SAT), `subtree166.py` (T1 driver),
`squeeze166.py` (Lemma A166-1), `pick166.py` (the cover plan and the LP node list),
`lp166.py` (T2), `canary166.py` (T3), `check166.py` (the independent checker),
`trump166.py` (the Trump match and the quadrant census), `draw166.py` (the pages),
`report166.py` (the tables), `run166.ps1` (the two LP shards).
