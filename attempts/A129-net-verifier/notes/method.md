# A129 — the net-orientation verifier: what Burns–Massaccesi actually do, and the lab's version

## 0. The paper (found, and it is not what the brief assumed)

There is **no arXiv paper**. Burns–Massaccesi (August 2026) is a pair of blog posts on the n = 17
square-packing problem:

* Sam Burns, *The n=17 Square Packing Problem* (sam-burns.com, series, Aug 2026) — the original
  idea and the first certificates (a bound near 4.4811, later 4.4452 quoted as the provable state
  of the art);
* Gustavo Massaccesi, *Another Better Lower Bound for n=17 Square Packing*
  (`gus-massa.blogspot.com/2026/08/another-better-lower-bound-for-n17.html`, 2026-08) — the LP-tuned
  version, `L = 45058/10000`, 168 weighted points on a 29 × 29 grid inside an empty margin
  `M = 15513/10000`, `WEIGHT_SCALE = 576`, total weight ≈ 16.9166 < 17.

**Their construction is a MEASURE certificate — the same object as this lab's A08/A33 certificates
and as every A57 leaf certificate.** Weighted points; the claim "every unit square placed in the
container carries weight ≥ 1"; total weight < n; contradiction. Their contribution is not a new
kind of certificate but a new **verifier** for it:

* a finite net of **181 orientations**, `k = 0..180`, `t_k = T·k/180` with `T = 207107/500000`
  (so the net is uniform in the half-angle tangent `t = tan(θ/2)` on `[0, tan(π/8)]`, using the
  D4 symmetry of their configuration to halve `[0, π/4]`), and `c_k = (1-t_k²)/(1+t_k²)`,
  `s_k = 2t_k/(1+t_k²)`;
* an **"almost-unit" square** of side `B = 9973/10000 = 0.9973` tested instead of the unit square,
  justified by `contain = B·(1 + D) < 1` with `D = T/KMAX` a bound on the tangent of the angular
  gap;
* per orientation, an **exact 2-D translation sweep**: rotate the points and the feasible-centre
  region into the `(U,V)` frame where the test square is axis-aligned, collect the event
  coordinates from the region boundary and from every point's translation box, build a 2-D
  difference array, take two integer cumulative sums, and read off the minimum weight over the
  feasible centres. All predicates rational; numpy only for the integer difference array.

So "translation sweeps" is a **minimum-weight sweep over the centre plane at a fixed orientation**,
not a sweep over separating-axis selections. There is no LP and there are no Farkas witnesses in
their method, and none in this one: the brief's guess that the object would be "a finite disjunction
of rational linear systems, each checked by Farkas" was based on the assumption that the lab's kills
are box trees over positions and tilts. They are not — every A57 PASS leaf is a
`case-measure-certificate-v1`, i.e. the very object Burns–Massaccesi's verifier consumes. That is
what makes the experiment sharp, and it is why the A129 verifier is a sweep, not an LP.

**What the lab's version differs in** (all three are needed to replay A57 at all):

1. **the shrink is sharp, not the `1+D` bound.** `B_j = (1+m²)/(1+2m-m²)` with
   `m = max |tan((θ-θ_k)/2)|` over the cell is exactly `1/(cos δ + sin δ)` — the lab's `σ(δ)`,
   the CORE lemma's constant (Lemma N1). Burns–Massaccesi's `B(1+D) < 1` is the same inequality
   loosened by `sin δ ≤ tan δ`.
2. **the net is adaptive.** Cells that fail are bisected in `t`; the net ends up as fine as the
   geometry demands and no finer. Their net is uniform, which is affordable only because their
   certificate is unconditional and their container has D4 symmetry.
3. **conditional certificates.** A57's leaves carry hypotheses — cores and NO-families — and the
   exemption clause is decided for the **unit** square uniformly over the whole net cell, never for
   the shrunk square (Lemma N3). This is the single change without which the method cannot replay
   a single A57 kill; see §4.

## 1. Lemma N1 (the σ inclusion) — the whole of the shrink

> Let `θ_k` be fixed and let `δ ≥ 0`. For every `θ` with `|θ - θ_k| ≤ δ < π/4` and every point `p`,
> the closed square of side `σ(δ) = 1/(cos δ + sin δ)` with centre `p` and edge direction `θ_k` is
> contained in the closed unit square with centre `p` and edge direction `θ`.

*Proof.* Both squares are centrally symmetric about `p`, so containment is equivalent to the
inequality of support functions in the two edge-normal directions of the outer square. Write
`ε = θ - θ_k`. A square of side `B`, centred at the origin, rotated by `ε` relative to a frame, has
support `(B/2)(|cos ε| + |sin ε|)` in each axis direction of that frame. The unit square's support is
`1/2`. So containment holds iff `B(|cos ε| + |sin ε|) ≤ 1`, and `|ε| ≤ δ < π/4` gives
`|cos ε| + |sin ε| = cos|ε| + sin|ε| ≤ cos δ + sin δ`, since `u ↦ cos u + sin u` is increasing on
`[0, π/4]`. Taking `B = σ(δ)` finishes. ∎

*Exact form used in the code.* With `u = tan(ε/2)`, `cos ε + sin|ε| = (1 - u² + 2|u|)/(1 + u²)`,
which is increasing in `|u|` on `[0, √2 - 1)` (its derivative vanishes at `u = √2 - 1`). The half-angle
tangent of `θ - θ_k` is `(t - t_k)/(1 + t·t_k)`, monotone in `t`, so the maximum of `|u|` over a
`t`-cell is attained at an endpoint. Hence `m = max(|u(t_0)|, |u(t_1)|)` and

    B = (1 + m²) / (1 + 2m - m²)

is an exact rational, equal to `σ(δ)`. `netcheck.py` re-derives `m` and `B` from the cell and
re-checks `B·(1 - m² + 2m)/(1 + m²) ≤ 1` as an exact rational inequality, independently of what the
certificate claims.

## 2. Lemma N2 (the reduction) — stated n-general

> Let `μ = Σ w_i δ_{p_i}` be a finite non-negative atomic measure on `[0,s]²` with total mass
> `M < b`. Let `E` be any set of "exempt" closed unit squares. Suppose `[0,1]` (in `t = tan(θ/2)`,
> which parametrises `θ ∈ [0, π/2]`, and `Q(c,θ) = Q(c, θ+π/2)`) is partitioned into finitely many
> cells `C_j = [t_j, t_{j+1}]`, and for each cell let `θ_k(j)` be its net orientation, `B_j` the
> constant of Lemma N1 for the cell's angular half-width, and
> `P_j = [h_j, s - h_j]²` with `h_j = min_{t ∈ C_j} (cos θ + sin θ)/2`.
> If for every `j` and every `p ∈ P_j` either
>   (a) `μ(S_j(p)) ≥ 1`, where `S_j(p)` is the closed `B_j`-square at `p` with direction `θ_k(j)`, or
>   (b) every unit square `Q(p, θ)` with `θ ∈ C_j` lies in `E`,
> then every closed unit square `Q ⊆ [0,s]²` not in `E` has `μ(Q) ≥ 1`; hence no `b` pairwise
> interior-disjoint closed unit squares that avoid `E` fit in `[0,s]²`, and (with `E = ∅`, `b = n`)
> `s(n) ≥ s`.

*Proof.* Let `Q = Q(p,θ) ⊆ [0,s]²` with `Q ∉ E`. Reduce `θ` mod `π/2` into `[0, π/2]`; let `j` be a
cell containing the corresponding `t`. `Q ⊆ [0,s]²` forces `h(θ) ≤ p ≤ s - h(θ)` coordinatewise with
`h(θ) = (cos θ + sin θ)/2 ≥ h_j`, so `p ∈ P_j`. Alternative (b) is impossible, because `Q ∉ E`. So
(a) holds, and by Lemma N1 `S_j(p) ⊆ Q`, whence `μ(Q) ≥ μ(S_j(p)) ≥ 1`. The packing conclusion is
the lab's standard bridge (verify_case.py's header): `b` pairwise interior-disjoint closed unit
squares at side `s' < s`, rescaled by `s/s'` and shrunk back about their centres, are pairwise
**disjoint** closed unit squares in `[0,s]²`, so `M = μ([0,s]²) ≥ Σ_squares μ(Q) ≥ b`, contradicting
`M < b`. ∎

Nothing in N1 or N2 mentions `n = 11`, the container's symmetry, or the stratification: the
reduction is n-general and holds for any container `[0,s]²`, any `b`, and any exemption set `E`
closed under "contains a smaller concentric square" — see N3.

## 3. Lemma N3 (the exemption clause) — the change that makes the method work at all

The A57 hypotheses give `E` explicitly: `Q ∈ E` iff `Q` meets some core `K_r` (a rational square:
centre `(k_x,k_y)`, direction `θ_m`, half-side `a`), or `Q`'s centre and tilt lie in a NO-family.

> For a cell `C_j` and a centre `p`: if the closed unit square `Q(p,θ)` meets `K_r` for **every**
> `θ ∈ C_j`, then alternative (b) of Lemma N2 holds at `p` and `p` may be skipped, whatever the
> shrunk square `S_j(p)` does.

This is immediate, but the naive alternative — "skip `p` when `S_j(p)` meets `K_r`" — is what a
straight port of Burns–Massaccesi gives, and it is *catastrophically* worse. `S_j(p) ⊆ Q(p,θ)`, so
`S_j` meets the core only on a strictly smaller set: the exempt region loses a rim of width
`Θ(1 - B_j)` all the way round every core. The LP that produced the certificate had no reason to
put any mass on that rim (it is inside the exempt region, where the certificate makes no claim), so
the rim is typically **mass-free**, and the verifier fails there at *every* refinement level — the
rim shrinks but never empties. Measured on `k5_11_interior_NO` (3 atoms, 5 cores): with the naive
exemption the live minimum is exactly `0` at every level from 1 to 16; with Lemma N3 the same
certificate is reproduced at 364 net orientations.

The predicate used is verbatim the frozen verifier's `core_exempt_frac`: a lower bound
`g_inf ≤ |cos(θ-θ_m)| + |sin(θ-θ_m)|` valid over the whole `t`-cell, then the four separating-axis
tests `|proj_e(p-k)| ≤ a + g_inf/2` on the core's axes and `|proj_f(p-k)| ≤ 1/2 + a·g_inf` on the
square's axes (with the `f`-projections taken over the cell's cos/sin enclosure). Each is a maximum
of linear functions of `p`, so the exempt set is **convex in `p`**, and testing the four corners of a
rectangle of centres decides the whole rectangle. Likewise a NO-family box is convex in `p`, and the
family's `t`-interval must contain the whole net cell.

## 4. Lemma N4 (the sweep is exact)

Fix a cell. In the rotated frame `u = cos θ_k·x + sin θ_k·y`, `v = -sin θ_k·x + cos θ_k·y`, the mass
of `S_j` centred at `(U,V)` is

    M(U,V) = Σ_i w_i · 1[ |u_i - U| ≤ B/2 ] · 1[ |v_i - V| ≤ B/2 ],

a finite sum of indicators of **closed** axis-aligned boxes. Consequences used by the code:

* `M` is constant on the interior of every cell of the arrangement cut by the `2N` coordinates
  `u_i ± B/2` (and the same in `v`). **Subdividing a grid cell can therefore never raise its mass** —
  bisection in `(U,V)` is only ever useful to resolve the exempt region and the admissible region.
  With no hypotheses (`E = ∅`) the correct bisection depth is `0`, and `netverify.py` sets it there.
* Each summand is upper semicontinuous and, at a point on the boundary of its own box, is `≥` its
  value at every nearby point; summing, `M(x) ≥ M(y)` for all `y` in a small neighbourhood of any
  `x` on a cell boundary. So the infimum of `M` over any set is attained in the **interior** of some
  arrangement cell, and evaluating one representative per cell is exact, not a sample.
* The evaluation itself is a 2-D difference array plus two integer cumulative sums, with the weights
  put over a common denominator `WD`; the comparison is the integer `mass ≥ NEED = ⌈(1+margin)·WD⌉`.
  `int32` is used when the total integer mass is below `2³⁰` (every partial sum is bounded by the
  total, the weights being non-negative), `int64` otherwise. No floating point enters any decision.
* Admissibility: the rectangle of centres and the square `P_j` are two convex rectangles, one
  axis-aligned and one at `θ_k`; by the separating-axis theorem their four edge normals `x, y, U, V`
  decide whether they meet in positive area, and strict overlap on all four is exactly that. `O(1)`,
  exact.

`P_j` is a **superset** of the admissible centres of any single `θ ∈ C_j` (it uses the smallest
half-width over the cell), so checking it is sound; it is the only conservatism in the reduction
besides the shrink itself.

## 5. The certificate and the independent checker

`netverify.py --emit` writes `net-orientation-certificate-v1`: the source certificate's atoms,
weights, total, hypotheses and budget; the net's `t`-cells as exact rationals (the adaptive net is
non-uniform, so the cells are listed); the σ rule; the margin; the ladder of refinements tried with
their walls; and, on failure, explicit witnesses (a net orientation, a rectangle of centres, and the
exact rational mass there).

`netcheck.py` re-decides the same claim by a different algorithm:

| | netverify.py | netcheck.py |
|---|---|---|
| mass | event sweep + 2-D difference array + cumulative sums, numpy integers | 2-D **branch and bound**; a rectangle is covered when the atoms whose translation boxes contain the *whole* rectangle already reach `1`; pure `Fraction` |
| exemption | own re-implementation (`core_exempt_point`), float pre-filter + exact confirm | the **frozen** `verify_case.core_exempt_frac` / `nofam_exempt`, imported read-only, on the `(x,y)` outer box of the rotated rectangle |
| admissibility | separating-axis, exact | separating-axis, exact |
| σ | computed | **re-derived** and re-checked as a rational inequality |
| tiling | produced | checked: first cell starts at `0`, last ends at `1`, consecutive cells abut, none empty |
| floats | pre-filter only | none at all |
| numpy | yes | no |

A `CHECKED` verdict from `netcheck.py` therefore rests on: the arithmetic of `fractions`, the frozen
exemption predicates (already Lean-backed, `known_results.md` 16), and Lemmas N1–N4 above.

## 6. Where this leaves A19

Untouched, as the brief says. A19's obstruction is about what a *measure* can prove; N1–N4 change
only how one decides that a given measure has the property it claims. Burns–Massaccesi are on the
same side of that obstruction — their certificate is a measure, so their n = 17 route is bounded by
exactly the same ceiling.
