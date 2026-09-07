# A117 T2 — Lemma TC as a certified leaf

## What TC says

**Lemma TC (tilt coherence; `docs/known_results.md` 26c, PI 2026-09-06).**  Two interior-disjoint
closed unit squares with centre distance `c` and tilt difference `D` reduced mod 90° satisfy

    (1 + cos D + sin D) / 2  ≤  c .

It is exact and elementary: `w(D) = |cos D| + |sin D|` is a unit square's support half-width in the
direction of the other square's edge normal, interior-disjointness gives a separating axis, and on
an edge normal the centre separation is at least `1/2 + w(D)/2`.  The minimum over directions is the
face-to-face placement, `(1 + w(D))/2`, attained at `D = 0` with value 1 and rising to
`(1 + √2)/2 = 1.2071` at `D = 45°`.

**The leaf.**  For two conditioned bins `B₁, B₂` (centre box × tilt interval each), TC gives the
sufficient condition

    max centre distance over the centre boxes  <  (1 + cos D_min + sin D_min) / 2

with `D_min` the **minimum** tilt difference over the two tilt intervals.  A fire means no packing
has one square with its pose in `B₁` and a *different* square with its pose in `B₂`.  It is
one-sided: a pair it does not kill is undecided.

## The exact check (`code/tcleaf.py`)

Everything is `fractions.Fraction` except `cos D_min` and `sin D_min`:

* **Tilt intervals normalised to `[0, 90]`** first (`theta_branches`), and the domain
  `0 ≤ th0 ≤ th1 ≤ 90` is **asserted** on every branch — this is A111 bug (ii), where a negative
  tilt interval produced by a D4 reflection was fed to a bound stated only on `[0, 90]`.  A bin
  whose interval straddles a multiple of 90 becomes **two** bins, and the leaf fires only if it
  fires for **every** branch pair.  `TCDomainError` is raised rather than a wrong answer returned.
* **`D_min` exactly** (`tilt_dev_min`): `d` ranges over `[th0₁ − th1₂, th1₁ − th0₂]`; if the range
  is ≥ 90° wide, or contains a multiple of 90°, the tilts can agree and `D_min = 0`; otherwise the
  reduced difference `f(d) = min(d mod 90, 90 − d mod 90)` is a tent function and its minimum is at
  an endpoint.  All comparisons and the floor-mod are on Fractions.
* **`c_max` exactly** (`centre_dist_max_sq`): `dx = max(x1₁ − x0₂, x1₂ − x0₁, 0)`, likewise `dy`,
  and the **squared** maximum `dx² + dy²` is kept, so no square root is ever taken.
* **`(1 + cos D + sin D)/2` bounded from BELOW** (`need_lower`): `D·π/180 ∈ [x_lo, x_hi]` with `π`
  enclosed by a 50-digit *truncation* (`PI_LO < π < PI_HI`, exactly).  `cos` decreases and `sin`
  increases on `[0, π/2]`, so evaluating `cos` at `x_hi` and `sin` at `x_lo` is valid for the whole
  enclosure; each is a truncated alternating Taylor series ending on a subtracted term, hence a
  rigorous lower bound (the terms decrease since `x ≤ π/4 < 1`).  Measured against `math`, the
  bound is tight to `≤ 2.3·10⁻¹⁶` on the values that occur.
* **The decision** is then `c_max² < need_lo²` between two exact rationals.  Both directions of
  slack (the zone shrink and the `cos/sin` lower bound) make the check **under**-fire, never over.
* **Distinctness** (`pose_disjoint`, exact): two bins that share a pose may be witnessed by the SAME
  square, and then an overlap statement proves nothing about a packing.  This is part of the leaf's
  hypothesis, exactly as in A111/A112's `octagon.pair_kill`.

## The sampling control

Every fire is confirmed by `≥ 10⁴` sampled pose pairs (`sample_confirm`): centres uniform in the two
centre boxes, tilts uniform in the two tilt intervals, all 64 corner/endpoint combinations forced in
first, each pair checked by a four-axis SAT test.  **Every** sampled pair must overlap strictly; the
worst SAT gap is recorded.  A single non-overlapping pair invalidates the fire.

## Lean (`lean/.../ParamNoFam.lean`, `[C]`)

`TCSupportMin`, `TCCentreDist`, `TCLeaf` and `TCLeaf_of_TCCentreDist` are stated as `Prop`
definitions — **not** axioms, so the project's axiom count is unchanged.  `TCCentreDist` is Lemma TC
itself; `TCLeaf` is its consumer in the shape of `Zones.core_meet_same_square` with the width
function `tcWidth D = |cos D| + |sin D|` in place of the core, and `TCLeaf_of_TCCentreDist` records
that the step between them is only the monotonicity of `D ↦ (1 + cos D + sin D)/2` on `[0, 45°]`
(which is why `D_min`, a minimum, is the right quantity to compute over the bins).

**Why the proof is not written.**  TC's geometric content is "interior-disjoint ⇒ separated on an
edge normal of one of the two squares" — the separating-axis theorem for convex polygons, which
`Band.lean` explicitly records as *not* formalised in this development (it formalises instead the
same argument run with an arbitrary separating direction, at a degraded constant).  Supplying TC
therefore means supplying SAT for two rotated unit squares first; that is a wave of its own, not an
`nlinarith` after a quadrant split.  Until it lands, a TC kill is `[C]`: an exact machine check with
a `10⁴`-sample control and a frozen Lean statement, not a Lean theorem.

## Side-dependence (the caveat that governs how a TC kill transfers)

TC is **side-blind**: it sees only two bins.  But a *bin* need not be side-blind.  A fire between
two branch/conditioned boxes, both anchored at the node's own `s`-independent coordinates, transfers
to the whole window unchanged.  A fire between a bin and a **class pin** does not automatically: a
pin box is `[α + β·s ± h]` with `β ∈ {0,1}`, so it moves with `s`, and the kill must be re-checked
with the pin box widened over the window (or the fire re-run per slab).  Both kinds occur in the
replayed corpus and they are labelled separately in `results/tc_replay.json`.
