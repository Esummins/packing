# A141 — the LANE test with polygon cores: what it proves, and how it is certified

## 0. Discipline

* READ-ONLY on every campaign and on A118/A132/A135/A140. `lanelib.py` (A118), `polycore.py`
  (A132) and `caselp.py` (A57) are imported, never written; A140's `results/t1_polycore.json`
  is the corpus. Every A141 file is new, under `attempts/A141-polycore-lane/**`, plus the named
  lines in `docs/`.
* ≤ 2 python processes, BelowNormal, BLAS pinned to one thread (`blas1` imported before numpy in
  every entry point); `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes.
* Every interval prune is in the KEEP direction: the reachable set is only ever ENLARGED, which
  is the sound direction for an UPPER bound on `LANE` and for the `M` exclusions.

## 1. The leaf (A118 §1, unchanged in logic)

For a corner cell `C` of a k0 node with conditioned squares `h_0 … h_{k-1}` in parameter boxes
`B_0 … B_{k-1}`:

    R'(C) := { poses (c, θ) : Q(c,θ) ⊆ [0, s0]²,  int Q(c,θ) ∩ int C ≠ ∅,
               int Q(c,θ) ∩ K'(B_j) = ∅ for every j }
    LANE_K'(C) := max # of pairwise interior-disjoint unit squares with poses in R'(C)
    M(C)       := # of conditioned squares that can meet int C

> **LEAF.** `LANE_K'(C) + M(C) ≤ 1` ⟹ `C` is met by ≤ 1 square of the family ⟹ K0-FREE
> (`teleport_packing` / `k0free_kill`) ⟹ the cell is DEAD.

`K'(B) = ⋂_{(c,θ) ∈ B} Q(c,θ)` is A132's polygon core, strictly bigger than A96's axis-aligned
`K(a)` that A118 used. Nothing else changes.

## 2. The frame: at s0, with the WIDENED corner box

A118 pulled the count back to side `m` in the corner frame. A141 stays at `s0`, where A140's
certified `K'` live, and pays Lemma K0-WIDEN instead (`k0_route.md` §4.1):

    Q meets int B_c(m)  ⟹  Δ_λ Q meets int B_c^w(s0),   w = (λ_max − 1)(1 + 1/√2) = 0.02550919…

so counting meeters of the WIDENED corner box `C_w = [s0 − 1 − w, s0]²` (at TR; the three D4
images elsewhere) on the dilated family `F = Δ_λ P` bounds the meeters of `B_c(m)` on `P`, which
is what `k0free_kill` consumes. `C_w` is what every A141 cover uses. (Running the same covers
with `w = 0` changes no verdict in the corpus; the widened form is the sound one.)

**Container tightening.** A conditioned square is admissible, so its centre satisfies
`h(θ) ≤ c ≤ s0 − h(θ)` with `h = (|cos|+|sin|)/2 ≥ min_cs/2` over the box's tilt range. Every
hypothesis box is therefore replaced by its container hull (`polylane.container_hull`) before
`K'` is built — a sound tightening that makes the polygon cores strictly bigger. On
`s3_far_BL389484_TR018470` it moves box 0's `y0` from `0.5` to `0.558156…` and is exactly what
turns A140's near-miss `depth_poly(K'(h0), K'(h1)) = −0.0128` into an overlap of `+0.0435`.

## 3. The discharge is ONE RATIONAL POINT, not a polygon

For a box `b` of a pose cover and a conditioned box `B_j`, it suffices to exhibit one rational
point `w` with

  (i)  `w ∈ Q(c,θ)` for every `(c,θ) ∈ b`      — `polycore.vertex_ok(w, b)`, exact in ℚ
  (ii) `w ∈ Q(c,θ)` for every `(c,θ) ∈ B_j`    — `polycore.vertex_ok(w, B_j)`, exact in ℚ

Then a square with pose in `b` and the conditioned square `h_j` share `w`, so by
`Zones.core_meet_same_square` (A135 `PolyCoreT5.shared_point_same_square`) they are THE SAME
square — impossible for a free square, and impossible for a second conditioned square `i ≠ j`.
**`K'` never enters the certificate**; it is only where the search for `w` looks, and even that
is optional: `polylane.best_shared_point` maximises

    f(w) = min( m(w, b), m(w, B_j) ),    m(w, B) = ½ − max_{(c,θ) ∈ B} |R(−θ)(w − c)|_∞ ,

which is CONCAVE in `w` (½ minus a max of absolute affine forms), by a shrinking grid. `m` is
evaluated exactly: `c` enters affinely so a corner of the centre rectangle attains the max
(Lean `PolyCoreT5.biaffine_bound`) and the `θ`-max of `|d·e(θ)|` is at an endpoint or at
`θ = arg d (mod 90°)` (`lanelib._max_abs_proj`). `vertex_ok` re-decides the same statement in ℚ
over `[t_lo(θ0), t_hi(θ1)]`, an OUTWARD-rounded superset of the box's tilt range.

## 4. The three prunes and the cover

A cover box is discharged by exactly one of

* **container** — every pose leaves `[0, s0]²` (`x1 < min_cs/2`, …);
* **misses_cell** — one axis (the cell's own, the cell being axis-aligned) separates the square
  from `int C_w` for every pose of the box;
* **witness** — §3.

Undischarged boxes are bisected (widest of `x`, `y`, `θ/60`) and the split is recorded as a bit
path, so the leaves are the leaves of ONE full binary tree rooted at the pose window: their boxes
tile the root exactly, which is what makes "finite cover" checkable (`check141.complete_prefix_code`).

* `LANE_K' = 0` ⟺ every leaf is discharged.
* `LANE_K' ≤ 1` ⟸ the cover is COMPLETE and every pair of surviving leaves (the diagonal
  included) is certified always-overlapping by A118 §1.2(ii): the coarse screen
  `max|d| < ½ + ½ min_Δ(|cos Δ| + |sin Δ|)` first, then for the survivors the SHARP per-normal
  bound `max_{d, θ} |n(θ)·d| < ½ + ½ min_Δ(|cos Δ| + |sin Δ|)` (`lanelib.pair_always_overlap`),
  so no separating axis exists for any pose pair — two free squares reaching `C` would have to
  overlap. The checker re-implements both.
* Otherwise UNDECIDED (never a kill). A sampled interior-disjoint pair inside `R'(C)` reports
  `LANE ≥ 2` with two explicit witnesses.

`M(C)`: conditioned square `j` is EXCLUDED when the same cover, run over `B_j` itself with `skip
= j` (a witness against `j` itself would be vacuous), discharges every box — i.e. every
admissible pose of `B_j` that meets `int C_w` shares a point with some OTHER conditioned box.
`M` is the number not excluded.

## 5. The pair contradiction (a by-product of the same machinery)

`polylane.pair_incompatible(B_i, B_j)`: cover `B_i` and discharge every sub-box by the container
prune or by a point shared with EVERY pose of `B_j`. Success means squares `i` and `j` must
coincide — the node's hypothesis is contradictory and the cell is DEAD outright, a (C) leaf, not
a teleport leaf. This is strictly stronger than

* A140 T1(iii)'s `K'(B_i)` vs `K'(B_j)` test (which compares the two intersections over the WHOLE
  boxes), because a sub-box of `B_i` has a much fatter polygon core; and
* A118's full-box octagon pair test `lanelib.pair_always_overlap`, because the container prune
  removes the corner of `B_i` where a separating axis exists.

On `s3_far_BL389484_TR018470` the pair `(h0, h1)` needs **one leaf and one rational point**.

## 6. Confirmation

Every certified verdict is re-sampled: poses drawn uniformly from the centre window × [0°, 90°),
kept when they lie in the container and meet `int C_w`, then tested against every `K'` by exact
polygon–square SAT. A `LANE = 0` verdict requires zero free poses among ≥ 10⁴ corner-meeting
draws; a `LANE ≥ 2` verdict carries a realised interior-disjoint pair.

## 7. What A141 does NOT claim

* The leaf is CONDITIONAL on k1_00's tree, exactly as A118's k0 rows are (`k0_route.md` §3,
  K0-O1) — a K0-FREE kill is a kill only once k1_00 closes.
* A `LANE ≤ 1` kill on a cell whose hypothesis is already contradictory (§5) is vacuous, not
  independent evidence; the records flag both.
* No certificate here is a `case-lp-certificate-v1`; the frozen verifiers are untouched. What is
  emitted is a `polycore_lane_v1` / `polycore_pair_v1` file plus `check141.py`, whose exact step
  is A132's `vertex_ok` = Lean `checkVertexInPBox`.

## 8. The PI's two extensions (same machinery, added after the k0 corner pass)

### 8.1 Usable slots of the pinned classes (`code/t4_slots.py`, `code/t2_a5760.py`)

**The slot rule.** A cell `p` of class `S` is USABLE iff it is an unclipped completable slot whose
EXTENSION class `T = S ∪ {p}` is certified dead on a window CONTAINING the node's side range.
Read from `attempts/A56-sparametric/results/scoreboard.json` (A56 + A61 + A114): every extension
below is FULL on the CLOSED window `[191/50, 969271/250000]`, so every listed slot is usable at
every node of A57/A60 —

| class | usable slots → extension |
|---|---|
| k5_11 | BL(1,1)→k6_18, BR(0,1)→k6_20, TL(1,0)→k6_20, TR(0,0)→k6_23 |
| k5_16 | BL(1,0)→k6_23, BR(0,1)→k6_29, BR(1,0)→k6_27, TR(0,1)→k6_30, TR(1,0)→k6_28, TL(1,0)→k6_27 |
| trump5 | BL(0,2)→k6_07, BL(1,1)→k6_19, BR(0,1)→k6_21, TR(0,1)→k6_22, TR(1,0)→k6_24, TL(0,0)→k6_23 |

The leaf is A118's unchanged: SLOT-CROWD gives ≥ 2 NON-PIN squares meeting the slot cell, so
`LANE_K′(p) + M(p) ≤ 1` is a contradiction and the node is dead (equivalently: the single meeter
snaps into the exact slot and the packing lands in the dead extension class). The pins are
obstacles only — they are not counted in `M`. Two things change from A118: the conditioned
obstacle is `K′(B)`, and the PIN obstacle is A135's EXACT pin core `K′` of the pin's own zero-tilt
box (half-side `1/2 − δ/√2` at A57's m-hulled pins, the FULL unit square at A60's exact ones)
rather than `pinguard`'s `a = 0.48999997`. Frame: A118's — the original packing at side `m` in the
cell's corner frame, boxes hulled over `m ∈ [m_lo, s0]` by `lane.cframe_boxes` (imported
read-only). Lemma CONT is dropped, which only enlarges `R′(C)`, so the bound stays sound.
Caveat A118-O1 stands: a LANE kill excludes class-`S` packings with EXACT pins, not the
`δ = 10⁻²` slack family.

### 8.2 The JOINT count on a near-miss (`polylane.lane_corner_split`, `code/t5_split.py`)

`LANE_K′ = 1, M = 1` is not a kill only because the two counts are separate. Split the conditioned
box `B_j` into a complete binary subdivision; the actual square is in exactly one piece, and on
each piece `B_k` the ORDINARY leaf runs with `K′(B_k)` (strictly bigger than `K′(B_j)`):
`box_misses_cell(B_k)` ⇒ `m_k = 0` and `LANE_k ≤ 1` suffices; otherwise `m_k = 1` and the piece
needs `LANE_k = 0`. Every piece closing means the cell is singly met in every realisation. Sound,
and it is the same leaf `N` times — the only new Lean content is a second `path_cover_complete`
over `B_j`.

**It does not fire on this corpus, and 28 of the 44 near-misses PROVE it cannot.**
`results/t5_twocrowd.json` exhibits, for 28 of the 44 near-miss corners, an explicit
interior-disjoint pair (one free square, one pose of the conditioned square) BOTH meeting the
widened corner cell — the leaf's hypothesis is genuinely realisable there, so no refinement of any
kind can kill those corners. Of the remaining 16, a deep cover (`code/t5_deep.py`,
`max_open = 9000`) certifies `LANE = 0` on ONE (`node_161` TR — a new kill), and the joint split
on the first of the rest (`l1_159` TR, 291 pieces to depth 11, 554 s) leaves 218 pieces open.
Conclusion: the near-miss population is a real 2-crowd population, not a counting artefact.
