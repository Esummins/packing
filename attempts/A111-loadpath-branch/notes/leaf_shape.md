# A111 — the sound leaf shape for a load-path YES kill, and what has to be verified exactly

## The leaf (Lean-shaped)

Fix a class C (five pinned slot cells with A57's slack half-width h = δ/√2, δ = 1e-2), a shadow G
with its box squares Bx(G, C) = (load-bearing free squares) ∪ (anchors: the shadow's slot squares
that carry a loaded contact with a load-bearing square and are NOT pins of C), and radii (r, ρ).

```
theorem loadpath_yes_dead
    (s : ℝ) (hs : 3.82 ≤ s) (hs0 : s ≤ 969271/250000)
    (P : Fin 11 → Pose) (hP : IsPacking s P)
    -- the class hypothesis, exactly A57's pin cores
    (hpin : ∀ p ∈ pins C, ∃ i, P i ∈ PinBox p s h)
    -- the YES hypothesis, one box per conditioned square
    (hbox : ∃ σ : Bx(G,C) ↪ Fin 11, ∀ n, P (σ n) ∈ F n)
  : False
```

`PinBox p s h = {(x,y,θ) : |x − (α_p + β_p s)| ≤ h, |y − (γ_p + δ_p s)| ≤ h, θ = 0}` (β, δ ∈ {0,1});
`F n = [c_n ± r] × [θ_n ± ρ]` with (c_n, θ_n) the shadow's own pose. Note that only the pins and
the boxed squares appear: the other squares of P are dropped, which only weakens the hypothesis, so
the leaf is a valid node cut wherever the node's hypothesis implies `hpin` and `hbox`.

## What has to be verified exactly (the four obligations)

**O1 — the selection census.** For each unordered pair (m, n) of conditioned squares (boxes and
pins) and each of the eight signed selections (edge normal a ∈ {e₁(θ_m), e₂(θ_m), e₁(θ_n), e₂(θ_n)},
sign σ ∈ {±1}), decide whether

  sup { σ (c_n − c_m)·a − 1/2 − (|a·e₁(θ_n)| + |a·e₂(θ_n)|)/2 : poses in F_m × F_n, s ∈ [3.82, s0] } < 0 .

This is one polynomial inequality in (cos θ, sin θ) at the interval endpoints and the box corners,
`nlinarith`-sized, and it is *decidable by interval arithmetic*: A111's `a111lib.IV` /
`iv_gap_axis`, with `w_range` giving the exact envelope of |cos| + |sin| on an interval. Outcome
per pair: FORCED (one surviving selection — the row is valid), AMBIGUOUS (≥ 2 — case split, or drop
the row), IMPOSSIBLE (0 — that cell of the case tree is already closed).

**O2 — the tilt subdivision.** A finite list of tilt cells covering ∏_n [θ_n ± ρ], produced by
bisection. Each cell is a hypothesis refinement, so the list must be checked to COVER the product
(a `Finset.sum`-style interval cover; trivial for a bisection tree).

**O3 — the affine relaxation, per cell.** For every FORCED (or case-split) pair row, the valid
affine inequality

  σ (c_n − c_m)·a(θ_m^mid) + R_{mn} Δ_m ≥ 1/2 + w_min /2 ,

with |a(θ) − a(θ^mid)| ≤ Δ_m (chord bound, |da/dθ| = 1), R_{mn} = the interval max of |c_n − c_m|
over the boxes, w_min = the exact cell minimum of |cos(θ_m − θ_n)| + |sin(θ_m − θ_n)|; plus the
containment rows x ≥ h_min, s − x ≥ h_min with h_min the exact cell MINIMUM of (|cos| + |sin|)/2
(the minimum, not the maximum: the maximum would over-constrain and prove nothing). Each is a
one-line consequence of the trigonometric bound.

**O4 — one Farkas certificate per cell.** Rational multipliers y ≥ 0 with yᵀA = 0 on the variable
block and yᵀb < 0: a single `linarith` per cell. **The Farkas vector IS the load path** — by Lemma
GRAIN-LP its support is the balanced contact-force system of the chain, so the object A110 named is
exactly the object this leaf has to exhibit.

## Composition

* The leaf is a `ClassKilledAt`-shaped clause on a sub-hypothesis, consumed the way SLOT-CROWD's
  row and GRAIN-ROW are (`slot_crowds.md` §8, `grain_flood.md` §4.3): it removes the YES cell of a
  branch, and the NO cells (one per box, each a `caselp.NoFam`) must die at the node LP.
* The whole branch is sound only if the YES and NO sides use the SAME boxes, in the SAME frame.
  A111 maps the shadow's boxes into a node's frame with the inverse of A107's `struct_op` (a D4
  isometry of the container, so an axis-aligned box maps to an axis-aligned box), and the boxes are
  anchored at the shadow's own coordinates, which sit at the shadow's side s\* rather than the
  node's s0 — a frame slack of |s\* − s0| = 0.0097 (S02) / 0.0085 (S07) that the radius must absorb.
* A96's parametric verifier `verify_param.py` refuses NO-families (`nofams unsupported`), so the NO
  side is a FIXED-SIDE object: one certificate per side of A57's four-side slack-core grid.

---

# Addendum (A111 second pass) — the leaf that the data actually favours

The LP leaf above is sound but its certified radius is tiny (T1: the fixed-tilt LP certifies only
while r < s\* − s0, i.e. 0.0097 for S02 and 0.0085 for S07 — smaller than A57's own L3 box). Two
LP-FREE tests, both already in the A57/A96 tool-chain, kill a much larger share of the same YES
cells, and their Lean shape is a two-line `nlinarith` rather than a Farkas certificate.

## Leaf CORE-MEET (A57 `pinguard.classify` contradictory case, A96 tight core)

For a box B let K(B) be A96's tight common inscribed core: the axis-of-B-aligned square of half-side
a = (1/2 − h·M_c)/M_t centred at B's centre, contained in EVERY unit square whose pose lies in B.

```
theorem core_meet_kill (B₁ B₂ : Box) (hposedisj : ∀ p, ¬(p ∈ B₁ ∧ p ∈ B₂))
    (hmeet : (K B₁ ∩ K B₂).Nonempty)
    (P : Fin 11 → Pose) (hP : IsPacking s P)
    (h₁ : ∃ i, P i ∈ B₁) (h₂ : ∃ j, P j ∈ B₂) : False
```

Proof: `hposedisj` forces i ≠ j; `K Bₖ ⊆ Q(P k)` by the core lemma; `hmeet` gives a common point of
Q(P i) and Q(P j), contradicting `IsPacking`. The only computation is `cores_meet`, a separating-axis
test on two rotated squares — exact in ℚ, and it is *the same predicate A57 already discharges 583
times on the deployed cover*, so no new obligation enters the TCB.

## Leaf TC (tilt coupling)

```
theorem tilt_coupling (Q₁ Q₂ : UnitSquare) (hdisj : interior Q₁ ∩ interior Q₂ = ∅) :
    dist Q₁.centre Q₂.centre ≥ (1 + |cos Δθ| + |sin Δθ|) / 2      -- Δθ reduced to [0°, 45°]
```

with Δθ = the tilt difference reduced mod 90°. The minimum is the face-to-face placement: the
separation along Q₁'s edge normal is at least 1/2 + w(Δθ)/2 where w = |cos| + |sin| is Q₂'s support
half-width in that direction. Contrapositive form: centre distance c forces |Δθ| ≤ D(c) where
(1 + cos D + sin D)/2 = c. A box pair with max centre distance < (1 + w(Δθ_min))/2 is empty.

Δθ_min over two tilt intervals is an endpoint evaluation of a piecewise-linear function with minima
at the multiples of 90° (`octagon.tilt_dev_min`); the max centre distance is a corner evaluation.

## Where each leaf applies

| | fires on | certified radius | cost |
|---|---|---|---|
| GRAIN-LP (Farkas) | box-vs-box **at a side** | r < s\* − s0 only | LP + B&B, minutes |
| CORE-MEET / TC | box-vs-box **pairwise**, side-blind | see T1 octagon table | microseconds |

The two are complementary and the split is structural, not accidental:

**CORE-MEET and TC are side-blind.** They see only pairs of boxes; the container side enters only
through where the class pins sit. The S02/S07 YES kill is a *side* statement — the chain forces
s ≥ s\* > s0, with every pair of squares still strictly disjoint — so a pairwise-overlap test can
never carry it, at any radius. T1's octagon run confirms this directly: at the node's own side s0
the test kills NOTHING, at any (r, ρ), with the minimum core gap strictly POSITIVE and increasing in
r (+0.0138 at r = 0.0087 up to +0.22 at r = 0.2). That is genuine room, not a weak bound.

**Where they do fire is against the node's own conditioned bin**, which is a different pair: the bin
is somewhere else in the container, and it collides with a load-path box outright. That is the free
kill, and it is the productive one (`results/t3_logickills.json`).

## Figure

`results/free_kill.svg` (geometry-checked, `code/fig_freekill.py`) draws both halves of the split on
node `k5_11_interior_Y0246` at A57's level-1 half-widths (r = 0.0699, ρ = 4.87°):

* LEFT — the node's own conditioned bin against load-path box f1: the two tight cores overlap, and
  400 sampled pose pairs have worst SAT gap **−0.6782** (every pair deeply overlapping). The YES
  cell is empty with no LP.
* RIGHT — the same shadow's load-path boxes and anchors against the class pins at s0: **every** core
  pair is apart, closest pair BR(0,1) vs pin BR(0,0) at **+0.1063**. Note the closest pair is an
  anchor against a pin, not two load-path squares — the chain itself is nowhere near self-collision,
  which is the geometric content of "the kill is a statement about the side".

Checks written into `results/trump_loadpath.json` under `free_kill_figure`: every drawn core sits
inside every unit square of its own tilt branch with margin +0.00416.
