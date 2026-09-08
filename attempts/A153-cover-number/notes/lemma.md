# A153 T1 — Lemma CN, Leaf CN, Lemma TC: the statements, the Lean shape, the certificate

## 1. Lemma CN (separation of centres)

**Lemma CN.** Let `Q₁, Q₂ ⊂ ℝ²` be unit squares (any centres, any tilts) with `int Q₁ ∩ int Q₂ = ∅`,
with centres `c₁, c₂`. Then `|c₁ − c₂| ≥ 1`.

*Proof.* A unit square `Q` with centre `c` contains the open disk `B(c, ½)`: the distance from `c`
to each of the four side lines is exactly `½`, and `Q` is the intersection of the four closed
half-planes those lines bound, so every point at distance `< ½` from `c` is in the interior of all
four, i.e. in `int Q`. Suppose `|c₁ − c₂| < 1` and put `m = (c₁ + c₂)/2`. Then `|m − c₁| =
|m − c₂| = |c₁ − c₂|/2 < ½`, so `m ∈ B(c₁, ½) ∩ B(c₂, ½) ⊆ int Q₁ ∩ int Q₂` — contradiction. ∎

The lemma is *n*-general and tilt-free: it says nothing about the container, the pins or the
hypothesis, only that unit squares that do not overlap keep their centres a unit apart. It is the
`d ≥ 1` half of the classical "unit squares ⟹ centres 1-separated ⟹ ½-disks packed" chain that
A148's disk bound already uses in its area form; A153 uses the *combinatorial* form instead.

## 2. Leaf CN (the kill)

**Leaf CN.** Let a node have `budget` unit squares still to place, and let `F_out ⊆ ℝ²` be any set
that contains the centre of every unit square that could still be placed. If

    F_out ⊆ S₁ ∪ … ∪ S_k     with   diam(S_i) < 1   for every i,

then the node can place at most `k` further squares. In particular `k < budget` KILLS the node,
with no LP.

*Proof.* The centres `c₁, …, c_budget` lie in `F_out`, hence each lies in some `S_i`. Two centres in
the same `S_i` are at distance `≤ diam(S_i) < 1`, contradicting Lemma CN. So the map
`centre ↦ (an index i with the centre in S_i)` is injective, and `budget ≤ k`. ∎

`F_out` is instantiated by **A148's certified outer approximation of the feasible-centre region**:
the union of the grid cells that are *not* BLOCKED, where a cell is BLOCKED when

    max over the 36 sampled tilts of  clearance(cell centre, t)  <  −margin,
    margin = pitch·√2/2 + (√2/2)·(½ tilt step),
    clearance(c,t) = min( container clearance of Q(c,t) , min_j −depth(K_j, Q(c,t)) )

and `clearance` is 1-Lipschitz in the centre and (√2/2)-Lipschitz in the tilt. A BLOCKED cell
therefore contains no admissible centre at any tilt, so `F_out = ¬BLOCKED` really does contain every
placeable centre. (This obligation — call it **REGION-OUTER** — is exactly the one A148's green /
white drawing already carries; Leaf CN makes it load-bearing, and the A153 checker re-verifies it
from scratch on every cell the cover does not contain.)

## 3. Which pieces — squares, not disks

Pieces are **axis-aligned squares of side `d`**, admissible iff

    diam = d·√2 < 1   ⟺   2 d² < 1,

an exact rational test on `d`. Disks of diameter `< 1` are the other natural family, but they buy
nothing here and cost more:

* `F_out` is a finite union of axis-aligned grid cells, so "cell ⊆ piece" is four rational
  comparisons for a square and a quadratic test on four corners for a disk;
* the largest axis-aligned square inside a disk of diameter `< 1` has side `< 1/√2`, i.e. exactly
  the admissible square — so a disk cover of a union of cells is never better than the square cover
  by more than boundary effects;
* a square tiles, a disk does not, so squares also give the clean *area* lower bound
  `k ≥ area(F_out)/d²`.

**So: axis-aligned squares of side `d` with `2d² < 1`.** Concretely, A148's grid is `n = 194` cells
of pitch `p = s₀/n = 969271/48500000`, and a piece is taken to be a `K × K` block of cells with `K`
maximal subject to `2(Kp)² < 1`: `K = 35`, side `6784897/9700000 = 0.699473918 ≤ 0.7` — the PI's
side-0.7 squares — and `2·side² = 0.978... < 1` exactly. Anchoring pieces to the grid loses
nothing: a piece is only useful through the cells it *contains*, and sliding a side-`Kp` square to
the nearest grid position never drops a fully-contained cell.

## 4. The certificate

`attempts/A153-cover-number/certs/<node>.cover.json`:

| field | meaning |
|---|---|
| `s0`, `grid.pitch`, `grid.n` | the container and grid as exact rationals (`n·pitch = s₀`) |
| `grid.ntilt`, `grid.margin` | the tilt sample and the Lipschitz margin, with its formula |
| `piece.K`, `piece.side`, `piece.diam2_num/den` | the piece side as a rational and the exact `2·side² < 1` |
| `obstacles`, `obstacle_names` | the exact pin cores and `K′(H)` polygons, as drawn |
| `pieces[]` | one entry per covering square: `i0, j0` and the four rational corners |
| `cover`, `lb`, `budget` | the cover number, the lower bound that proves it minimal, the budget |
| `sample` | 10⁴ centres drawn in `F_out`, each confirmed feasible on 360 tilts, each required inside a piece |

## 5. The independent checker

`code/check153.py <cert>` re-derives, with its own separating-axis code (test T-A pins it against
A132's `poly_square_depth` to 9e-16, but nothing in the checker calls it):

1. `n·pitch = s₀` — the grid is the container;
2. every piece is a `side × side` axis-aligned square on the grid, and `2·side² < 1` in exact
   rationals;
3. `margin ≥ pitch·√2/2 + (√2/2)(π/2/ntilt)/2`;
4. the obstacle polygons are rebuilt from the node's own record through A132 `polycore.build` and
   A135 `exactcore.exact_a` (the trusted base) and must match vertex for vertex;
5. **every grid cell not contained in a piece has max-over-tilts clearance `< −margin`** — the only
   direction that matters, since an uncovered cell must be provably empty;
6. `#pieces < budget`;
7. the sample line is re-drawn and re-tested here.

`code/test153.py` is the checker's own test suite: T-A (SAT agreement), T-B (Lemma CN on 2·10⁴
random near pairs), T-C (a certificate for a node that does **not** die fails *only* the count
check), T-D (dropping one piece is caught as "466 uncovered cells not certified blocked"), T-E (a
piece of side 1 is refused). All five pass.

## 6. Lean shape

Core Lean 4, no Mathlib, same integer-at-a-common-denominator idiom as
`lean/PackingCert/PackingCert/Geometry.lean`.

```lean
/-- A covering piece: the axis-aligned square [x0, x0+side] × [y0, y0+side], in units of 1/D. -/
structure Piece where
  x0 : Int
  y0 : Int

structure CoverCert where
  D      : Int              -- common denominator
  cell   : Int              -- grid pitch, in units of 1/D
  side   : Int              -- piece side,  in units of 1/D
  openC  : List (Int × Int) -- the cells NOT certified blocked: cell (i,j) = [i·cell,(i+1)·cell]²
  pieces : List Piece
  budget : Nat

/-- (a) the pieces have diameter < 1 -/
def admissible (c : CoverCert) : Bool := 2 * c.side * c.side < c.D * c.D

/-- (b) every open cell sits inside one piece -/
def covers (c : CoverCert) : Bool :=
  c.openC.all fun ij =>
    c.pieces.any fun p =>
      p.x0 ≤ ij.1 * c.cell ∧ (ij.1 + 1) * c.cell ≤ p.x0 + c.side ∧
      p.y0 ≤ ij.2 * c.cell ∧ (ij.2 + 1) * c.cell ≤ p.y0 + c.side

/-- (c) the count -/
def kills (c : CoverCert) : Bool := c.pieces.length < c.budget

def check (c : CoverCert) : Bool := admissible c && covers c && kills c
```

Two theorems carry the mathematics; everything else in the leaf is `decide`.

```lean
theorem centre_sep {Q₁ Q₂ : UnitSquare}
    (h : Disjoint (interior Q₁.set) (interior Q₂.set)) :
    (1 : ℝ) ≤ dist Q₁.centre Q₂.centre
-- from  ball Q.centre (1/2) ⊆ interior Q.set  (elementary: four half-planes at distance 1/2)

theorem cover_bound {F : Set (ℝ × ℝ)} {S : Fin k → Set (ℝ × ℝ)}
    (hd : ∀ i, Metric.diam (S i) < 1) (hcov : F ⊆ ⋃ i, S i)
    {m : ℕ} {c : Fin m → ℝ × ℝ} (hc : ∀ a, c a ∈ F)
    (hsep : ∀ a b, a ≠ b → (1 : ℝ) ≤ dist (c a) (c b)) :
    m ≤ k
-- pigeonhole (Finset.exists_ne_map_eq_of_card_lt_of_maps_to) on  a ↦ (some i with c a ∈ S i)
```

and the bridge from the JSON to `F`:

```lean
theorem cert_kills (c : CoverCert) (h : check c = true)
    (hF : feasibleCentres node ⊆ cells c.openC) :        -- REGION-OUTER, the analytic input
    ¬ Placeable node c.budget
```

**Axiom cost.** `centre_sep` and `cover_bound` are both Mathlib-level and add **no** axiom.
`hF` (REGION-OUTER) is the one analytic input; it is *already* the obligation behind A148's white
region and behind the disk bound in `docs/budget.md`, so Leaf CN adds **zero new axioms** to the
count in A62's formal statement — it re-uses REGION-OUTER and adds one decidable `check`.

## 7. Lemma TC (conditional: the tilt-coherent branch)

**Lemma TC.** If two interior-disjoint unit squares have the **same** tilt `t`, then their centre
difference `Δ` satisfies `‖Δ‖_∞ ≥ 1` in the frame rotated by `t`.

*Proof.* In that frame both are axis-aligned unit squares `c_i + [−½,½]²`; if both `|Δ_u| < 1` and
`|Δ_v| < 1` the two open squares meet. ∎

**Leaf TC.** Under the hypothesis "every remaining square has tilt `t`", pieces may be squares of
side `< 1` **in the `t`-frame** — 1/√2 times bigger in side, so about half as many per axis and a
quarter as many overall. If `t` is known only to lie in a window of half-width `δ` around `t₀`, a
square of side `d` in the `t₀`-frame has width `d(cos δ + sin δ) ≤ d(1 + δ)` in every frame of the
window, so

    d (1 + δ) < 1

is a sufficient (and rational, given a rational bound on `δ`) admissibility test for the whole
window. With a rational frame direction `(a, b)`, `q = a² + b²`, a piece is
`{p : |(p − c)·(a,b)| ≤ H, |(p − c)·(−b,a)| ≤ H}` — side `2H/√q` — and the exact test is
`4H²(1 + δ)² < q`.

**Leaf TC is CONDITIONAL**: it is sound only on a branch of the region tree on which every
not-yet-placed square is known to share a tilt (the S02 grain). On such a branch the sound number is
`max over t in the window of cover_t`, or the single window-robust cover above; the per-`t` minimum
is a *best case*, not a kill.
