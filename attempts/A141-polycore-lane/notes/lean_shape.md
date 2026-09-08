# A141 T1(d) — the Lean shape of the K′ lane leaf

## The composition

    corner cell met by ≤ 1 square  →  K0-FREE  →  k1_00's monotone kill  →  dead on W

is already Lean, end to end, for the *hypothesis* the leaf supplies:

| step | Lean object | file | status |
|---|---|---|---|
| teleport the single meeter into the corner slot | `teleport_packing` | `Selection.lean` (C.CC2) | THEOREM |
| corner box interior-met by ≤ 1 square ⇒ False on `[lo, hi)` | `k0free_kill` | `Slide.lean` 117 | THEOREM (needs `hK1` = K0-O1) |
| k1_00's monotone kill on the window | `SlabKill {⟨c,0,0⟩} 3.82 ŝ` | `Composition.lean` `slabKill_of_tree` | **OPEN dependency** (k1_00's tree, `k0_route.md` §3) |

`k0free_kill`'s hypothesis is literally

    hfree : ∀ j, j ≠ i₀ → Disjoint (interior (cornerBox m 1 c)) (interior (z j).set)

— the UNWIDENED corner box, at side `m`. A141 delivers it in three named pieces.

## Piece 1 — the discharge, already proved

`PolyCoreT5.shared_point_same_square` (A135, THEOREM):

    hw : StrictlyInside B w → hw' : StrictlyInside B' w →
    (∃ q, InPBox B q ∧ Q i = q.set) → (∃ q, InPBox B' q ∧ Q j = q.set) → i = j

with `StrictlyInside` supplied by `checkVertexInPBox` (THEOREM `checkVertexInPBox_sound`) plus
`InteriorFromMargin` (`[C]`, the closed-vs-interior bridge A63 closed for the square core; the
emitter's positive margin is what pays for it — A141 stores `margin_box` and `margin_cond` on
every leaf, both `> 10⁻⁷`).

Each cover leaf is one application: `B` = the leaf box, `B'` = conditioned box `j`, `w` = the
leaf's rational point. `i` is the free square, `j` the conditioned one, so `i = j` is the
contradiction. **No new leaf lemma.**

## Piece 2 — the cover, a decidable check (ONE new obligation)

    LaneCoverOK : PBox → Rect → List PBox → List Leaf → Bool

replaying the certificate: the leaf paths form a full binary tree over the root (decidable on
`List String`), each leaf box is recomputed by the same split rule, and each leaf is discharged
by one of three decidable tests —

* `boxOutsideContainer` : `x1 < min_cs/2 ∨ …` — needs `min_cs` bounds, which `LocalCertT`'s
  `cosT_anti` / `sinT_mono` already give in `t`-form;
* `boxMissesRect` : one axis of the axis-aligned cell separates for every pose — the same
  `|cos|+|sin| ≤ max_cs` bound;
* `checkVertexInPBox` twice — Piece 1.

**The one new obligation** is the soundness statement of the whole check:

    LaneCoverSound : ∀ (root : PBox) (C : Rect) (Bs : List PBox) (L : List Leaf),
      LaneCoverOK root C Bs L = true →
      ∀ (q : PSq), InPBox root q → Q(q) ⊆ container → interior Q(q) ∩ interior C ≠ ∅ →
      ∃ j ∈ Bs, "q's square is the square of B_j"

i.e. *every* corner-meeting pose in the root window belongs to a conditioned square. Its proof is
three lines of case analysis on the leaf the pose falls in (which exists because the paths tile
the root) plus Piece 1 — the only genuinely new content is the tiling lemma
`path_cover_complete`, a statement about `List String`, provable by induction with no geometry.

The `LANE ≤ 1` variant additionally needs A118's octagon pair bound

    NoSeparatingAxis : maxDist B B' < 1/2 + 1/2 * minCS (Δθ) → ∀ q ∈ B, q' ∈ B', interiors meet

which is the SAME separating-axis obligation `ParamNoFam.TCLeaf` and `Band.lean` are blocked on
(A135 §5 (c)) — not new, but not yet discharged. **A141's twelve-cell kills use only the
`LANE = 0` and the pair form, which do not need it**; the two `LANE ≤ 1` kills in the corpus do.

## Piece 3 — Lemma K0-WIDEN, at the boundary of the frame (statement, not yet Lean)

A141 counts meeters of `B_c^w(s0)` on the dilated family. To feed `k0free_kill` at side `m`:

    K0Widen : ∀ P m (hm : m ∈ [3.82, ŝ]) (Q ∈ P) (c : corner),
      interior Q ∩ interior (cornerBox m 1 c) ≠ ∅ →
      interior (Δ_λ Q) ∩ interior (cornerBoxW s0 (1 + w) c) ≠ ∅,   w = (λ_max − 1)(1 + 1/√2)

This is `k0_route.md` §4.1, proved in prose (two lines: the witness point translates by
`(λ−1)c_Q`, and `c_Q < 1 + h(θ) ≤ 1 + √2/2` because `Q` meets the box). `Δ_λ P` being a packing at
`s0` is Lemma B.0, already consumed everywhere in the lab. In Lean this is one lemma over
`shiftCfg`-style arithmetic; nothing about the polygon core touches it.

## Roster

* NEW and load-bearing: `LaneCoverSound` (with `path_cover_complete`), `K0Widen`.
* NEW only for the `LANE ≤ 1` form: `NoSeparatingAxis` (= the standing `TCLeaf` obligation).
* REUSED, proved: `shared_point_same_square`, `checkVertexInPBox_sound`, `biaffine_bound`,
  `abs_proj_le_half`, `teleport_packing`, `k0free_kill`.
* REUSED, `[C]`: `InteriorFromMargin`.
* OPEN dependency, unchanged: K0-O1 (k1_00's tree).

## The pair form is even shorter

`polycore_pair_v1` with a single leaf is literally `shared_point_same_square` applied once:
`B` = conditioned box `i`, `B'` = conditioned box `j`, `w` the stored point, and the node's own
hypothesis `i ≠ j` closes it. It needs neither `LaneCoverSound` nor `K0Widen` nor K0-O1 — it is a
(C) leaf, unconditional. `s3_far_BL389484_TR018470` dies this way.
