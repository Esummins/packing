# A161 — the CHORD-LIMITED LANE leaf: statement, soundness, certificate, checker, Lean

Written 2026-09-08 (A161, Opus). Nothing here is deployed into a frozen verifier: this is a
GEOMETRIC leaf on the A57/A60 node tree, in the same status as A141's lane kills and A131's clip
kills — a kill certificate plus an independent checker, pending Lean.

Notation as A144: `s` is the container side, the nodes run at `s0 = 969271/250000 = 3.877084`,
`t = tan(theta/2)`, and `t_lo/t_hi` are A57 `caselp`'s OUTWARD-rounded rational bounds, so every box
statement below is about a tilt range CONTAINING the box's own.

---

## 0. What the leaf is for

At a node of a pinned class `S` (k5_11, k5_16, trump5: five pins plus `L` conditioned squares) the
lane leaf of A118/A141 kills the node when a USABLE slot cell can be met by at most one non-pin
square. Its two counters are

* `LANE_K'(C)` — how many pairwise interior-disjoint FREE squares can meet `int C` while avoiding
  every hypothesis core `K'(B_j)`;
* `M(C)` — how many conditioned squares can meet `int C`.

On `k5_16_interior_Y0842 / BL(1,0)` both counters are 1, so `LANE + M = 2` and the leaf stalls. The
PI's reading of the page is a REFINEMENT of the LANE counter, not a new lemma:

> "you can only put one core in the bottom slot by chord sum, and no cores outside that slot can
> reach BL(1,0)."

"One core in the bottom slot **by chord sum**" is A144's guard row. "No cores outside that slot can
reach it" is the lane cover restricted to the complement. The leaf below is the conjunction.

---

## 1. The leaf, exactly

### Setting

Let `N` be a node of a pinned class `S` with hypothesis boxes `B_0, ..., B_{m-1}` (`m = 5 + L`: the
five class pins and the `L` conditioned squares), budget `n - m`, side range `[m_lo, s0]`. Let
`p = (i, j)` be a USABLE slot of `S` at corner `c` — usable meaning the extension class
`T = S u {p}` is certified dead on a window containing `[m_lo, s0]` (A56/A61/A114 scoreboard) — and
WALL-ADJACENT, meaning `j = 0` (the cell touches the frame's bottom wall) or `i = 0` (left wall).
Work in the cell's corner frame at side `s0`, on A118's hulled boxes (`lane.cframe_boxes`), so

    C  =  [i, i+1] x [j, j+1] ,        the slot cell, closed,
    l  :  y = y_L  with 0 < y_L < 1    (a bottom-row cell; `x = x_L` for a left-column cell).

### The three counters

    (1)   rhs(l)   :=  s0  -  SUM_{j<m} minchord(B_j, l)                       [A144 LINE-2]
          beta     :=  floor( rhs(l) )                                         [the BAND cap]

    (2)   BAND     :=  { poses (c, theta) : |l n Q(c, theta)|  >=  1 }
          LANE_out :=  max # of pairwise interior-disjoint unit squares, none of them a hypothesis
                       square, whose poses all lie in
                          R'_out(C) := { pose : Q c [0,s0]^2, int Q n int C != 0,
                                                int Q n int K'(B_j) = 0 for every j,
                                                pose NOT in BAND }

    (3)   M        :=  # of conditioned squares (the non-pin hypothesis squares) that can meet
                       `int C` from their own box

### LEMMA CL (chord-limited lane)

*If `rhs(l) < 0` the node is DEAD outright (A144's guard row is violated). Otherwise*

    #{ non-pin squares of the packing that meet int C }   <=   beta + LANE_out + M .

*And if `beta + LANE_out + M <= 1`, the node is DEAD.*

**Proof.** Let `P` be a packing of `n` unit squares in `[0, m]^2`, `m in [m_lo, s0]`, satisfying the
node's hypothesis, and let `X` be the set of its non-pin squares meeting `int C`. Split
`X = X_H u X_band u X_out`:

* `X_H` — the conditioned squares in `X`. Each is one of the `L` conditioned squares and it meets
  `int C`, so `|X_H| <= M` by the definition of `M`.
* `X_band` — the free (non-hypothesis) squares in `X` whose pose is in `BAND`. Every square of `P`
  lies in `[0,m]^2 c [0,s0]^2` and the squares have pairwise disjoint interiors, so LINE-1 gives
  `SUM_{Q in P} |l n Q| <= s0`. The `m` hypothesis squares are DISTINCT squares of `P` (A57's T23
  pairwise-disjoint-cores gate) with poses in their own boxes, so
  `|l n Q_j| >= minchord(B_j, l)`; subtracting, the free squares satisfy
  `SUM_{free Q} |l n Q| <= rhs(l)`. Each member of `X_band` contributes `>= 1`, so
  `|X_band| <= rhs(l)`, hence `|X_band| <= floor(rhs(l)) = beta`.
* `X_out` — the free squares in `X` not in `BAND`. Each has its pose in `R'_out(C)`: it is inside
  the container, meets `int C`, is not in `BAND`, and is interior-disjoint from `K'(B_j) c Q_j` for
  every `j` because it is interior-disjoint from `Q_j` itself. They are pairwise interior-disjoint,
  so `|X_out| <= LANE_out`.

Adding, `|X| <= beta + LANE_out + M`. For the kill: SLOT-CROWD (A94/A109, the form A141's `t4`
uses) says that at a usable slot of a class-`S` packing at least TWO non-pin squares meet `int C`
— otherwise the single meeter can be snapped into the exact slot and the packing lies in the class
`T = S u {p}`, certified dead on the node's whole side window. So `|X| >= 2`, contradicting
`|X| <= 1`. ∎

Two remarks on what is and is not new.

* Nothing in the proof is new mathematics: it is LINE-1/LINE-2 plus the same disjointness count
  A118's leaf makes, applied to a PARTITION of the meeters instead of to all of them. The content is
  that the partition is chosen so that BOTH halves are cheap: the band half is capped by one linear
  inequality (no cover at all), and the outside half is what the cover was already good at.
* The `beta` cap does NOT require the band squares to meet `C`. That is a deliberate loss — the row
  is global along `l` — and it is why placing `l` inside the wall row of pins matters: two pin
  chords of exactly 1 already spend `2` of `s0 = 3.877084`, leaving `1.877084`, so `beta = 1`
  unconditionally, and `beta = 0` as soon as some conditioned box also crosses `l` with
  `minchord >= 0.877085`.

### The band, in closed form (what makes the prune free)

`chord = min(A, B)` with `A = 1/max(|cos|,|sin|) >= 1` always, so

    chord >= 1   <=>   B >= 1   <=>   |v|  <=  (C+S)/2 - C S  =  f(y),   y = C + S in [1, sqrt2],
    f(y) = (y + 1 - y^2)/2 ,   f DECREASING on [1, sqrt2],  f(1) = 1/2, f(sqrt2) = (sqrt2-1)/2.

So over a parameter box, `BAND` holds for EVERY pose iff `max |v| <= f(cs_max)`, where `max |v|` is
attained at a corner of the centre rectangle and `cs_max` is the maximum of `|cos|+|sin|` over the
tilt bin (`sqrt2` if 45 deg is in the outward-rounded bin, else the larger endpoint). Both sides are
exact rationals, and an UPPER bound of `cs_max` gives a LOWER bound of `f`: conservative.
`code/chordlane.py: band_ok`; cross-checked against A144's independent five-point
`minchord_box(...) >= 1` on every box it is called on in T1's self-test.

### One geometric consequence worth recording (why `y_L` is pushed to the wall row's top)

Every container-admissible unit square has `c_y >= h(theta)` and `h >= 1/2`, so
`c_y + h >= 2h >= 1 > y_L`: **no square of the packing lies entirely below a wall guard line with
`y_L < 1`.** Hence every meeter of a bottom-row cell either crosses `l` (chord `> 0`) or lies
entirely above it (`c_y - h >= y_L`), and the second case forces `c_y - h in [y_L, 1)` because the
square must still dip into `C`. Pushing `y_L` up to the top of the wall-row pin cores
(`y_L < 1 - (pin box half-width)`) shrinks that window to the pin box's own width, which is what
makes `LANE_out = 0` reachable at all. It is also the reason the sweep in `line_candidates` is
densest just below 1.

---

## 2. The new exact primitive the leaf needed: full SAT over a parameter box

A141's `box_misses_cell(b, C)` separates only along the CELL's two normals, using the box's
bounding half-width `hmax = cs_max/2`:

    b.x0 - hmax >= X1   or   b.x1 + hmax <= X0   or   b.y0 - hmax >= Y1   or   b.y1 + hmax <= Y0 .

For a conditioned box whose square clears the cell along one of its OWN edge normals this test is
false for every sub-box at every depth — the bound `hmax` is the square's bounding-box radius, not
its support radius along the true separating direction. `k5_16_interior_Y0842`'s `H`
(`x in [2.218056, 2.357813]`, `y in [1.519271, 1.659028]`, `theta in [53.130, 64.011] deg`) is
exactly that case against `C = [1,2] x [0,1]`, which is why A141 recorded `M = 1` there
("`excluded: false, by: cover`" — a budget failure, not a geometric fact).

`box_misses_cell_exact(b, C)` runs the complete separating-axis test over the box. For a candidate
axis `w` the square's support radius is exactly `1/2` when `w` is one of its own edge normals
(`w_0(theta) = (cos, sin)`, `w_1(theta) = (-sin, cos)`) and `h(theta) <= cs_max/2` when `w` is a
cell normal. With `D = {centres} (-) C` the Minkowski difference rectangle, the axis separates at
EVERY pose iff

    min over d in D, theta in bin  of  <d, w(theta)>   >=   radius ,

and the inner minimum over `D` is attained at one of `D`'s four corners. For `w_0`,
`<d, w_0(theta)> = R cos(theta - phi)` is unimodal with its MAXIMUM at `phi`, so its minimum over a
tilt interval is at an ENDPOINT unless the interval contains `phi + 180 deg`; with
`theta in [0, 90]` that needs `phi in [-180, -90]`, i.e. `d_x <= 0` and `d_y <= 0`, and in that one
case the conservative rational bound `-(|d_x| + |d_y|) <= -R` is returned (a third-quadrant offset
never separates, so nothing is lost). `w_1` reduces to `w_0` by `<d, w_1(theta)> = <R(-90) d,
w_0(theta)>`. Everything is a Fraction evaluated at the two rational endpoints
`t_lo(th0), t_hi(th1)` — the same two-endpoint discipline as A144's `minchord_box`.

This primitive is sound, subsumes A141's test, and is what turns `M = 1` into `M = 0` on the nodes
where the conditioned square is merely NEAR the cell. It is used in BOTH covers (the outside lane
and the `M` exclusion).

---

## 3. The certificate: `chord_limited_lane_v1`

`certs/cl_<nid>__<slot>.json`, SHA-256 recorded in `results/*.jsonl`.

```jsonc
{
  "leaf": "chord_limited_lane_v1",
  "claim": "beta + LANE_out + M <= 1 contradicts SLOT-CROWD ...",
  "s": "969271/250000",
  "nid": "...", "src": "A57", "cls": "k5_16", "level": 1,
  "slot": "BL(1,0)", "corner": "BL", "ij": [1, 0], "cell": [1.0, 2.0, 0.0, 1.0],
  "cell_kind": "usable_slot",
  "extension": "k6_23",
  "extension_window": "[191/50, 969271/250000] FULL (A56/A61/A114 scoreboard)",
  "frame": "A118 lane.cframe_boxes: ... hulled over m in [m_lo, s0]", "m_lo": 3.82,
  "n_pins": 5, "cond_index": [5],
  "hyp_boxes": [[x0,x1,y0,y1,th0,th1], ...],            // the frame boxes, pins first
  "guardline": {
    "orient": "h", "off": "993/1000",                   // exact rational, 0 < off < 1
    "rhs": "...", "beta": 1,                            // rhs = s0 - SUM minchord; beta = floor
    "minchords": [{"j":0,"minchord":"1","V":...,"method":"degenerate-tilt"}, ...],
    "band_rule": "chord >= 1  <=>  |v| <= (y + 1 - y^2)/2 at y = cs_max"
  },
  "lane_out": {"value": 0, "root": [...], "leaves": [{"path","box","why",...}], "open": []},
  "M":        {"value": 0, "detail": [{"j":5,"excluded":true,"by":"cover","cert":[leaves]}]},
  "total": 1,
  "sample_line": {"drawn":..,"meeting":..,"band":..,"outside":..,"outside_free":0, ...},
  "split_rule": "widest of (x, y, theta/60), deterministic (A141 polylane.split_box)"
}
```

Leaf `why` values and the data each carries:

| `why` | data | what the checker re-derives |
|---|---|---|
| `container` | — | every pose of the box leaves `[0,s0]^2` (`h(theta) >= cs_min/2`) |
| `misses_cell` | `axis`, `margin`, `radius` | the named axis separates over the whole box, exactly |
| `band` | `V`, `thr`, `cs_max` | `max|v| <= f(cs_max)`, so every pose has chord `>= 1` |
| `witness` | `j`, `w = [x, y]` | `w in Q(pose)` for every pose of the leaf box AND of `B_j` (A132 `vertex_ok` twice) |

Nothing else is trusted: `rhs`, `beta`, every `minchord`, every margin and the final arithmetic are
recomputed by the checker from `hyp_boxes` and `guardline.off` alone.

---

## 4. The independent checker `code/checkcl.py`

Extends A141's `check141.py` (C1–C6) and A144's guard-row re-derivation (G1). It shares with the
emitter only A132's `vertex_ok` (the trusted primitive whose Lean counterpart
`PolyCoreT5.checkVertexInPBox` is proved sound) and `caselp.Box`/`t_lo`/`t_hi`; the chord formula,
the five-point minimum, the SAT margins, the band threshold, the split rule, cover completeness and
the arithmetic are re-implemented here from the spec.

    D1  hyp_boxes contain the frame boxes recomputed from the node record (A118's hull), and every
        box is inside the container hull;
    D2  0 < guardline.off < 1 and the offset is an exact rational;
    D3  minchord(B_j, l) recomputed by the five-point rule; HARD REJECT if the certificate's value
        exceeds it; rhs* = s0 - SUM (recomputed), REJECT if rhs > rhs*; beta = floor(min(rhs, rhs*));
    D4  the lane_out leaf paths form a COMPLETE prefix code over the declared root, and the box
        recomputed from each path by the split rule equals the stored box (A141 C2);
    D5  every lane_out leaf's `why` holds by its own exact test (table above), the `band` rows
        included;
    D6  if lane_out.value = 1: every pair of OPEN boxes (diagonal included) always overlaps; if 0:
        the open list is empty;
    D7  each excluded conditioned square's cover is a complete cover of its own box with the same
        leaf checks, `skip = j`, and NO `band` rows (a band pose still meets the cell);
    D8  beta + lane_out.value + M.value <= 1, and the slot is in the class's usable table with a
        FULL extension window covering [m_lo, s0].

Cross-check built into T1: `band_ok` is compared against A144's independent `minchord_box(...) >= 1`
on every box, and `box_misses_cell_exact` against 6 x 10^4 sampled poses per box (a box declared
excluded must have ZERO sampled meeting poses).

---

## 5. Lean shape

The leaf composes four things, three of which already have statements.

**Reused, unchanged.**

| what | where | statement |
|---|---|---|
| `chord_sum_le_side` | A144 spec sec 5 | chords of an interior-disjoint family in `[0,s]^2` on an axis-parallel line sum to `<= s` |
| `minchord_of_box` | A144 spec sec 5 | `checkMinChordBox a B l m = true -> forall pose in B, m <= chordLen a pose l` |
| `shared_point_same_square` | A135 `PolyCoreT5` | a rational point in every pose of two boxes forces the two squares to be the same |
| `checkVertexInPBox_sound` | A135 | the exact `Bool` vertex-in-all-poses checker |
| the lane leaf | A118/A141 (`teleport_packing`, `k0free_kill`; SLOT-CROWD for the pinned classes) | a usable slot met by `<= 1` non-pin square is dead |

**Two new `Bool` checkers with soundness lemmas** (same style: numerics by `decide`, mathematics in
a short proof).

```lean
/-- BAND over a box: `max |v| <= (y + 1 - y^2)/2` at `y = cs_max`. -/
def checkBandBox (B : ParamBox) (l : GuardLine) : Bool := ...

theorem checkBandBox_sound (B : ParamBox) (l : GuardLine) (h : checkBandBox B l = true) :
    ∀ c θ, InBox B c θ → (1 : ℝ) ≤ chordLen (1/2) c θ l
-- route: chordLen_eq (A144) + `chord >= 1 <=> B >= 1 <=> |v| <= f(y)` + `f` antitone on [1,√2]
--        + `y_range_of_tilt` (A144's supporting lemma, reused verbatim).

/-- Full SAT over a box: one of the 8 (axis, sign) pairs separates at every pose. -/
def checkBoxMissesRect (B : ParamBox) (R : Rect) : Bool := ...

theorem checkBoxMissesRect_sound (B : ParamBox) (R : Rect) (h : checkBoxMissesRect B R = true) :
    ∀ c θ, InBox B c θ → interior (Q (1/2) c θ) ∩ interior R.toSet = ∅
-- route: `separating_axis_of_convex` (Mathlib: two convex sets with a separating functional have
--        disjoint interiors — only the EASY direction is needed, SAT completeness is not),
--        `support_unitSquare` (support radius 1/2 along its own edge normals, h θ along e_x/e_y),
--        `minkowski_diff_corner` (a linear form on a rectangle is minimised at a vertex — A135's
--        `biaffine_bound` gives this), and `proj_min_endpoint`: min of `R cos(θ - φ)` over an
--        interval not containing `φ + π` is at an endpoint (this is A144's
--        `chord_B_endpoint_min` argument in a different dress).
```

**One new glue obligation** — the leaf itself, and it is the only genuinely new statement:

```lean
theorem chord_limited_slot_crowd
    {n : ℕ} (s : ℝ) (P : Packing n s) (S : PinnedClass) (hP : P.satisfies S.hyp)
    (p : Slot) (hu : S.Usable p) (hw : p.WallAdjacent)
    (l : GuardLine) (hl : l.IsWallLine p)
    (beta lane M : ℕ)
    (hbeta : (beta : ℝ) + 1 > s - ∑ j, minchordVal (S.hyp.box j) l)   -- beta = ⌊rhs⌋
    (hband : ∀ Q ∈ P.free, 1 ≤ chordLen (1/2) Q l → Q ∈ P.bandOn l)   -- definitional
    (hlane : LaneOutBound P S p l lane)                               -- the cover's conclusion
    (hM    : CondMeetBound P S p M)                                   -- the M cover's conclusion
    (htot  : beta + lane + M ≤ 1) :
    False
```

Its proof is sec 1's four-line count: partition `X`, bound the three parts by
`chord_sum_le_side` + `minchord_of_box` (band), the lane cover (outside), the `M` cover, then apply
the existing SLOT-CROWD lemma to get `2 <= |X| <= 1`. **Roster: 2 `Bool` checkers, 2 soundness
theorems, 1 glue theorem, 3 supporting lemmas (two of which are A144's, reused), 0 new axioms.**
The leaf adds no analytic content beyond A144's chord algebra and Mathlib's separating-functional
direction.

---

## 5b. The inherited caveat (A118-O1), unchanged

Every kill here is a kill of the **exact-pin class-`S`** family, exactly as A118's and A141's are:
the pin boxes in the chord row and in the lane cover are the `m`-hulled EXACT pin positions
`slot_j(m)` with a zero-width tilt bin. A57's LP leaves exclude more (the whole `delta = 10^-2`
slack-pin family at `s0`, `lemmas.md` T23 / Lemma B'), and the composition A57 needs is unaffected —
the tree covers the conditioned square's box, every class-`S` image lands in some leaf, and a
chord-limited-lane leaf is empty of class-`S` images — but **a leaf killed here must not be re-used
for the broader slack statement.** For the slack form the row would need slack pin chords (each pin's
box widened by `7.07e-3`, which lowers its `minchord` from an exact 1 to `1 - O(10^-2)` and so does
NOT change `beta` at the two-pin walls, since `floor(3.877084 - 2 + 0.015) = 1` still) AND the
extension class killed in slack form. Recording the arithmetic here because it says the caveat is
cheap to lift on the `beta` side and expensive only on the extension side.

Also inherited: `K0-O1` does **not** apply (that is the k0/k1_00 dependency; the pinned classes use
SLOT-CROWD, whose extension classes are all certified FULL on the closed window), and A159's C8
guard applies in its OUTSIDE form — one exact free outside pose retires the cell, two
interior-disjoint ones retire it as a two-crowd.

## 6. The n-general form

Nothing above mentions `n = 11`, `s0`, or `k5`. For any `n`, any container side `s`, and any class
with `k` pinned squares in a wall row: a wall guard line placed inside that row collects an exact
chord of 1 from each pinned square in the row, so the free band budget along that wall is
`s - (#row pins) - SUM(conditioned minchords)`, and the number of free squares that can CROSS the
line — equivalently, sit in the wall row — is capped by its floor. For `k` pins in the bottom row
this is the length-charging sibling of A121's `st4` stack reading and of A94/A109's SLOT-CROWD
occupancy rows: SLOT-CROWD charges the cell, the guard row charges the line, and this leaf is the
statement that the two charges apply to complementary halves of the same meeter set and therefore
ADD. The general slogan: *a wall row of pins prices the wall lane, and a slot in that lane can then
hold only as many squares as the leftover length allows — everything else must reach the slot from
above, which is a lane-cover question in a strictly smaller pose window.*
