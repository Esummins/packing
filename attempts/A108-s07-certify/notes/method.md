# A108 — method notes (S07 certified against Trump)

Read-only on every campaign. A106's `shadow11.py` and A107's `shadowlib` / `minimise` / `analyse`
are imported as libraries; nothing under `attempts/A22-*`, `attempts/A53-*`, `attempts/A56-*`,
`attempts/A57-*`, `attempts/A60-*`, `attempts/A61-*`, `attempts/A106-*`, `attempts/A107-*` or
`lean/` is written. One BLAS-pinned process.

## 0. Conventions

* `s0` = 969271/250000 = 3.877084; `ŝ` = 3.877083590022814 (Trump).
* Square order (`a108lib.NAMES`): `f0 f1 f2 f3 f4` then
  `BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0)`.
* Two variable orderings are in play and are NOT the same. A107: `z = [s, (x,y,θ)×n]` with slot
  squares affine in s. A106 (`shadow11.Reduction`): `z = [(x,y,θ)×11, s]`. `a108lib.to106/to107`
  convert. A108's problem is the FULL one — all eleven squares free, 34 variables — which A106
  expresses as `Reduction([], pin_hw=0)` (its reduction map is then the identity) and A107 as
  `slots = (), nfree = 11`. Both engines were run and agree.

## 1. The side function σ (`a108lib.sigma`)

For a NORMALISED configuration (u = c/s, θ), σ(u, θ) is the smallest s at which unit squares at
centres s·uᵢ with angles θᵢ are pairwise interior-disjoint and contained in [0,s]². Every
constraint is monotone in s — a pairwise SAT gap along a fixed body axis is s·|Δu·n| − 1/2 −
(support of the other square)/2, a containment gap is s·u − w or s·(1−u) − w — so σ is a closed-form
max over pairs/walls of a min over the four axes, with no optimisation and no local minima.
Validation: σ(Trump) = ŝ to 1.6e-15, σ(exact S07) = s* to 2e-15. σ is what every "what is the side
of this configuration" question in A108 is answered with, including the barrier path, because it
cannot be fooled by a landing that is slightly infeasible (which is what cost A107 2.8e-8 on S07).

## 2. Polishing S07 with all eleven squares free (`polish.py`)

Seeded from A107's S07 landing. Penalty continuation (μ = 10 … 1e8, L-BFGS-B) then frozen-axis
SLSQP polish, A106's pipeline verbatim at zero pins. Result: s = 3.8856180832 with worst pair gap
and worst containment gap both 8.9e-16 (a genuine packing), against A107's 3.8856180554 with a
−9.5e-8 overlap. The A107 engine (plain SLSQP on the SAT gaps, no penalty stage, all eleven free)
lands at 3.8856182708 from the same seed — same structure, less converged. Every tilted square
comes out at 45.000° to 4e-5°, and every coordinate is recognisable in Q(√2).

## 3. Closing the contact system by hand (`exact.py` docstring has the algebra)

Reading the active contacts off that landing gives six equations that close on s (r = √2/2):

    cy₁ = s − r                      f1 on the top wall
    cx₁ + cy₁ = 4 + r                BL(0,2)'s corner (1,3) on f1's lower-left edge
    cx₀ = 1 + r                      f0's vertex on BL(0,1)'s right face (x = 1)
    (cy₁−cx₁) − (cy₀−cx₀) = 2r       f0–f1 flush (adjacent rows of the 45° lattice)
    (cy₀−cx₀) − (cy₄−cx₄) = 2r       f0–f4 flush
    cy₄ − cx₄ = 2 + r − s            BR(0,0)'s corner (s−1, 1) on f4's lower-right edge

⇒ 3s = 6 + 8r ⇒ **s\* = 2 + 4√2/3 = (6+4√2)/3 = 3.885618083164126…**, s* − ŝ = +0.008534493141.
The "4" is 1 (right face of the left column, which is on the left wall) + 3 (the column's stacked
height). `f0–f2` (a full shared edge) and `f2–TR(0,0)` are implied by the first four rows for every
s, so `f2` and `TR(0,0)` are carried, not equations. `f3` is a rattler and `f4` slides; their
canonical positions are the pocket Chebyshev centre and the lower end of the slide (touching
`BL(1,0)` on its slot) — both again in Q(√2).

## 4. Two certificates

* **Exact, in Q(√2)** (`exact.py`). A minimal ordered-field class: a + b√2 with a, b Fractions,
  sign decided by comparing a² with 2b². All eleven centres, all four axes and all supports are in
  the field because every tilt is 0 or 45°, so all 55 SAT gaps and all 44 containment gaps are field
  elements. Zero violations, 24 rows exactly zero. This is a proof that an 11-square packing of
  side exactly (6+4√2)/3 exists — no tolerance anywhere in the decision.
* **Interval endpoint** (A106's `certify_endpoint`, mpmath iv, 250 bits, denominator 1e12), run for
  method continuity with A106/A107: PASS at the first rung, **ε = 1e-9**, s_certified =
  971404521041/250000000000, margin 2.20e-10 — from the polished landing and from the exact
  configuration alike.

## 5. Contacts, forces, flexes (`contacts.py`, `rigidity.py`)

`contacts.py` classifies each zero-gap row exactly: the contact normal is the body axis whose gap is
exactly 0; a square's supporting face along it is an EDGE iff the normal is (anti)parallel to an
edge normal and a VERTEX otherwise; edge×edge with positive overlap is flush, vertex×edge is
vertex-on-edge, vertex×vertex is a point kiss. No tolerance is used. (A107's `classify` calls a
FULL shared edge "exactly-opposite", because all four of its incidences are at edge ends — worth
knowing when reading the gallery.)

`rigidity.py` reuses A107's exact analytic incidence rows (derivative of the vertex-to-supporting-
line distance including the edge owner's rotation lever) and its nnls Fritz-John forces. The
rank/flex numbers are quoted at the exact configuration, not at the raw polish: a drifted rattler
adds spurious flexes (8 at the raw landing, 3 at the canonical one).

## 6. Why the first-order test had to fail, and what replaced it (`localmin.py`)

nnls(Jᵀ, e_s) leaves residual 0.152, concentrated on `f1.θ` and `f2.θ`. This is geometry, not
convergence: a unit square at exactly 45° touching a wall has its touching vertex at the top of its
own rotation circle, so d(vertex_y)/dθ = 0 and the containment gap is quadratic in θ. Equivalently
the half-width (|cos θ| + |sin θ|)/2 is maximal at 45°; measured loss 3.54e-7 at dθ = 1e-3 and
3.54e-5 at 1e-2 — a clean t². So first-order Fritz-John is blind in every tilt direction here, and
local minimality has to be established at second order.

Two replacements, both in `localmin.py`:

* **Trust region.** Minimise s subject to feasibility AND ‖pose − pose\*‖∞ ≤ ρ, from the exact
  configuration and 12 random starts inside the region. s\* is returned for every ρ ≤ 3e-2.
* **Pinned-coordinate profiles.** Pin one coordinate at v ± δ, re-minimise the other 32 and s
  inside a trust region. Rise ≥ 0, scaling like δ².

**Trap worth recording.** The naive version of both tests — perturb, then re-minimise with no trust
region (and, worse, with s pre-inflated) — reports a spurious descent to ŝ from perturbations as
small as 0.002, because SLSQP repairs the infeasibility by walking out of the basin entirely. Every
"is this a local minimum" number in this lab needs a trust region or it is measuring the wrong
thing.

## 7. The barrier to Trump (`trump_compare.py`, `refine_barrier.py`)

Correspondence: nearest-centre bijection, minimised over all eight D4 images of Trump; the winner is
the identity (total centre distance 0.178), so the two really are in the same frame. Tilts are
compared modulo 90°.

* **Straight segment** in normalised pose space, σ evaluated on 4001 points — no optimiser, so the
  number cannot be an artefact of a solver. Also run on absolute centres with s interpolated
  linearly; the two agree to 2e-5.
* **Relaxed path**: at each common tilt from 45° down to 40.1819°, pin the five tilted squares'
  tilt and re-minimise all eleven centres, the six upright tilts and s. Warm-started along the sweep
  in both directions (down from S07, up from Trump) plus a linear-interpolation seed and random
  restarts, because a cold start loses the branch at the crest. This is the most generous path
  measured and is the number to quote as the barrier.

## 8. Class and kill (`attempts/A53-simple-strata/results/name_to_slots.json`, A56 scoreboard)

S07 has six simple squares, so k = 6; Young diagram per corner BL (3,1) by columns, BR (1), TR (1),
TL ∅. The slot set matches census class **k6_07** under the identity element of D4. Trump is
**trump5**; k6_07 = trump5 + `BL(0,2)` is exactly the extension class Trump's one disturbed upright
would fall into if it were aligned (A101's cellflood canary already named it). The covering kill is
the A53/A54 k6_07 stratum certificate (PASS at s0, 11 atoms) with A56's parametric transfer PARTIAL:
certified on [191/50, 956767/250000] = [3.82, 3.827068], window coverage 12.38 %, open band
(3.827068, s0] — scoreboard row `partial`, A61's **G-A56-3**. S07 itself lies 0.0085 ABOVE the
window's right endpoint, so it is not what that band has to exclude.
