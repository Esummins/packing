# A122 — method notes (S33 / S34 / S35 / K19 and S38 certified against Trump and S07)

Read-only on every campaign. A106's `shadow11.py` and A107's `shadowlib` / `minimise` / `analyse`
are imported as libraries; nothing under `attempts/A03-*`, `attempts/A53-*`, `attempts/A56-*`,
`attempts/A57-*`, `attempts/A60-*`, `attempts/A61-*`, `attempts/A106-*`, `attempts/A107-*`,
`attempts/A108-*`, `attempts/A110-*`, `attempts/A114-*`, `attempts/A116-*` or `lean/` is written.
BLAS pinned to one thread (`a122lib` sets the five env vars before numpy), `PYTHONDONTWRITEBYTECODE=1`,
no deletes. This is A108's method applied to a second (and third, and fourth) shadow, deliberately a
near-clone so the two certificates are comparable line for line.

## 0. Conventions

* `s0` = 969271/250000 = 3.877084; `ŝ` = 3.877083590022814 (Trump).
* Square order: `f0 … f4` then the six slot cells. The trump5-boundary entries S33/S34/S35/K19 and
  S07 all use `BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0) TR(0,0)`; **S38 uses a different six —
  `BL(0,0) BL(0,1) BL(1,0) BR(0,0) BR(0,1) TR(0,0)`** — so `a122lib.names_for(sid)` is per entry.
  K19 is a Part-II (k0) entry with a 5 slot + 6 free splitting; its sixth free square sits on the
  `BL(1,0)` cell and is moved into the slot position, so all five entries are compared as ELEVEN
  SQUARE SETS, never by label.
* Two variable orderings, as in A108: A107's `z = [s, (x,y,θ)×n]` and A106's
  `z = [(x,y,θ)×11, s]`. Both engines were run on every entry and agree.
* `a122lib.sigma(u, θ)` is A108's side function: the exact smallest s for a NORMALISED
  configuration, a closed-form max over pairs/walls of a min over the four body axes. Every "what
  is the side of this configuration" question is answered with σ, so no number here can be spoiled
  by a landing that is slightly infeasible.

## 1. Polishing with all eleven squares free (`polish.py`)

Each gallery landing was re-minimised at ZERO pins (A106 `Reduction([], pin_hw=0)`, 34 variables),
three ways: polish only, penalty continuation + polish, and A107's plain SLSQP with `slots=(),
nfree=11`. σ of the best landing is the number quoted.

| entry | gallery s* | all-free s* | verdict |
|---|---|---|---|
| S33 | 3.9169308671 | **3.9169308657** | the minimum |
| S34 | 3.9173601043 | **3.9169308657** | falls into S33's basin (max centre gap 1.5e-8, max tilt 0.0000°) |
| K19 | 3.9169312292 | **3.9169308657** | the same point (max centre gap 4.3e-8) |
| S35 | 3.9174326666 | **3.9174176578** | a DIFFERENT point, +4.868e-4, 0.069 away in centre, 6.92° in tilt |
| S38 | 3.9289147425 | **3.9289146852** | its own point |

So the answer to "one minimum or three" is **two**: S33 = S34 = K19 is one local minimum and S35
is a second one that the gallery's restricted (slot-affine) minimisation could not tell apart
because it sits only 4.9e-4 above.

## 2. Why there is no closed form (`system.py`, `exact.py`, `minpoly.py`)

A108 closed S07 by hand because every tilt there is 0 or 45°, so the sixteen active rows eliminate
rationally and s* = 2 + 4√2/3 ∈ Q(√2). That does not happen here. Writing the active incidences as
sixteen equations in the sixteen unknowns (five free poses + s, the six slot squares on their exact
cells), the system is **rank-deficient**: rank 14 at S33min, 15 at S35min and at S38min. The contact
graph alone therefore leaves a 2- (resp. 1-) parameter family of packings, and the minimum is an
interior critical point of s on that family. The exact characterisation is the Lagrange system

    g(x) = 0                (16 incidence equations)
    J(x)^T λ = e_s          (ds vanishes on the tangent of the family)

— 32 equations in 32 unknowns, solved by pseudo-inverse Gauss–Newton in mpmath with an analytic
forward-mode Jacobian. It converges quadratically (|F|∞ 4e-9 → 1e-15 → 5e-31 → 1e-61 → 6e-81 in
five steps) and the solution is verified to be a genuine packing: worst SAT gap and worst
containment gap are ±1e-61.

PSLQ, with the honest acceptance rule `degree × log10(maxcoeff) ≤ 100` and residual < 1e-150 at 170
correct digits (a loose PSLQ "finds" a quadratic for any number at all), then says:

* **S38min: s\* is an algebraic number of degree 9**, root of
  `x⁹ − 16x⁸ + 105x⁷ − 360x⁶ + 663x⁵ − 518x⁴ − 297x³ + 1064x² − 992x + 358 = 0`
  (residual 1.4e-165 at 170 digits).
* **S33min and S35min: no relation inside the budget.** Neither is in a quadratic field, and
  neither has a low-degree minimal polynomial with small coefficients — the honest statement is
  that these are high-degree algebraic numbers, quoted to 50 digits, not closed forms.

## 3. Certificates

* **Interval endpoint** (A106 `certify_endpoint`, mpmath iv, 250 bits, denominator 1e12; re-run at
  400 bits with denominator 1e15): all three points **PASS at the first rung, ε = 1e-9**, margin
  2.2e-10 — the same rung A108's S07 certificate reached.
* **The 50-digit value**, from the Lagrange system above, with the packing obligation checked in
  mpmath at 60 digits.

## 4. Contacts, forces, rigidity (`contacts.py`, `rigidity.py`)

All eleven squares free; A107's exact analytic incidence rows and nnls Fritz-John forces; the
contact classification is done at the 80-digit Lagrange solution, not at a 1e-7 threshold.

**S33min is first-order Fritz-John stationary** (residual 8.3e-9 — contrast S07's 0.152, which had
to be replaced by a second-order argument because a 45° square touching a wall has zero first-order
torque). S35min 4.6e-12, S38min 9.6e-15.

## 5. Local minimality (`localmin.py`)

A108's trap is respected: every number comes from a minimisation inside an L∞ TRUST REGION.

* **S33min**: min s inside the trust region returns s* for every ρ from 1e-5 to 1e-1 (rises
  +1.5e-8 … +2.5e-8, SLSQP noise). Pinned-coordinate profiles rise quadratically in every tilt and
  in `f4.y` (1e-3 → 2e-7, 1e-2 → 2e-5, 3e-2 → 1.7e-4). A strict local minimum with a basin of
  L∞ radius ≥ 0.1 in pose.
* **S35min**: returns s* for ρ ≤ 3e-2; at ρ = 1e-1 it escapes DOWN to 3.9169708, i.e. into S33min's
  basin. A strict local minimum with a small basin (~0.03–0.1).
* **S38min**: returns s* for ρ ≤ 3e-2; escapes at ρ = 1e-1 to 3.909.

## 5b. S33min against Trump and S07, square by square (`trump_compare.py`, `contacts.py`)

Nearest-centre bijection; tilts modulo 90°. The frame is the identity in both comparisons.

**vs S07** (total centre distance 0.5021). **All four BL cells are identical to 0** — including
`BL(0,2)`, which Trump lifts and S07 does not. `BR(0,0)` and `TR(0,0)` differ only by the side
(0.031 / 0.044). What differs is the free block:

| | f0 | f1 | f2 | f3 | f4 |
|---|---|---|---|---|---|
| S33min | (1.5000, 1.9540) **0.000°** | (2.4351, 2.7133) 40.000° | (1.4744, 3.2125) 40.000° | (2.4814, 1.2557) 51.449° | (3.2103, 1.9934) 47.089° |
| S07 | (1.7071, 1.9428) 45° | (2.4142, 2.6499) 45° | (1.5286, 3.1785) 45° | (2.4428, 1.2643) 45° | (3.1667, 1.9714) 45° |
| Δ tilt | **45.000°** | 5.000° | 5.000° | 6.449° | 2.089° |

**vs Trump** (total centre distance 0.6081): `BL(0,0)`, `BL(0,1)`, `BL(1,0)` identical to 0;
`BL(0,2)` differs by 0.0326 (Trump's lift); f1 and f2 are within 0.181° of Trump's tilt, f3 by
11.267°, f4 by 6.907°, and **f0 by 40.182°** — S33's f0 is upright.

**One square is the whole story.** S33min is what S07/Trump become when the keystone rotates to
0° and jams flush against the BL column's right face x = 1: that flush contact pins `cx_{f0} = 3/2`
and `θ_{f0} = 0` exactly, and the two diagonal chains it then supports — `f0 → f1 → TR(0,0)` upward
and `f0 → f3 → BR(0,0)` downward — carry the load (Fritz-John 0.462/0.444 and 0.478/0.465). The
price is +0.031313 of side over S07 and +0.039847 over ŝ.

**They are three separate local minima on one skeleton.** Along the straight segment in normalised
pose space σ rises to 4.141346 (vs Trump) and 4.144859 (vs S07) — the 40°/45° rotation of f0 makes
the straight line grossly infeasible. The relaxed tilt path (five tilts pinned to the linear
interpolation, all eleven centres + the six upright tilts + s re-minimised, warm-started both ways)
still crests at **3.955149 (+0.038218 over S33min, +0.078065 over Trump)** and **3.957754 (+0.040824
over S33min, +0.072136 over S07)**; inside an L∞ trust region of 0.15 around the interpolated seed
the crests are higher still (3.978558 / 3.986556). For contrast A108 measured only **+0.001105**
between S07 and Trump: S33min is a far deeper and better-separated minimum than S07 is.

**Corrections of record to the A107 gallery** (`docs/shadows.md` itself untouched):
S34's row is not a separate minimum — with all eleven free it falls into S33's basin;
S35's s\* is 1.5e-5 high (3.9174327 → 3.9174177); S33's "1 flat direction" is 2 with all eleven
free (both blocked at second order, curvatures −0.180 and −0.507); the "KKT residual 1.2e-3 / 1.8e-3
convergence caveat" on S33/S35 clears to 8.3e-9 / 4.6e-12 at the polished point; and S38's row lists
`f1`-`f3` and `f4`-`BR(0,1)` as near-zero-force struts, which the polished analysis confirms
(0.076 and 0.078).

## 6. The common-tilt family through S38 and its crest (`crest.py`, `crest_tube.py`, `crest_refine.py`)

S38's five free squares are one flush grain at a common tilt: a column `{f2, f0, f1}` and a column
`{f4, f3}` (v-spacing 1 each), joined by the two u-steps `f2–f4` and `f1–f3`. In strip coordinates
the six wall/corner rows are (a) f1's left vertex on the left wall, (b) f1's top vertex on the top
wall, (c) f3's top vertex on the top wall, (d) f2's bottom vertex on BL(1,0)'s top face,
(e) BR(0,1)'s corner (S−1, 2) on f4's lower edge, (f) TR(0,0)'s corner (S−1, S−1) on f4's upper
edge. That is **six equations in five unknowns** (u1, u2, v2, v4, S): overdetermined by one, so the
structure exists at exactly ONE tilt — a kink minimum, like S07 (Λ ∧ Y) and S02 (Λ ∧ A).

Dropping one row at a time (sympy) gives four distinct closed forms, and — this is the point — ALL
FOUR cross at one tilt. Which two are the ACTIVE branches is decided by a tube-tracked sweep
(`crest_tube.py`, `crest_refine.py`: at each 0.02–0.05° tilt step every pose coordinate is confined
to ‖z − z_prev‖∞ ≤ ρ of the SOLUTION AT THE PREVIOUS TILT, ρ ∈ {0.01, 0.03}, the two agreeing to
1e-8). The answer:

    below θ*:  C₃(θ) = (1 + 3cos θ + 3sin θ + cos θ sin θ + sin²θ − sin³θ)/(1 + cos θ sin θ)
               [row (c) released — f3 leaves the top wall; row (e) gives the SAME closed form,
                the two are dependent given the others]                      matched to 5e-8
    above θ*:  C₂(θ) = (2 + 2cos θ + 2sin θ + cos θ sin θ + cos θ sin²θ − 3cos²θ sin²θ)
                       / (1 + cos θ sin θ − cos²θ sin²θ)
               [row (b) released — f1 leaves the top wall]                    matched to 2e-7

**Neither is Λ, Y, D nor F_T: the A110 menu gains two members here.** C₃ has Λ's and Y's very
denominator 1 + sin θ cos θ, so it belongs to the same column-chain family; C₂ is new in kind
(denominator 1 + sc − c²s²). Both RISE away from θ*, and they cross where

    **G(θ) := (sin θ − 1)(2sin²θ − 1) cos θ + sin⁵θ − sin⁴θ − 4sin³θ + 2sin²θ + 2sin θ − 1 = 0**

(the same irreducible factor divides every pairwise difference of the four branch formulas), i.e. at
**θ\* = 41.754062677271°**, where C₂ = C₃ = **3.928914685223** = the polished s* to 6e-15. `sin θ*`
is the unique root in (0,1) of the irreducible **s⁹ − 2s⁸ − 3s⁷ + 4s⁶ + 12s⁵ − 6s⁴ − 13s³ + 6s² +
4s − 2**, and `tan θ*` of **x⁹ + 2x⁸ − 3x⁵ − 4x⁴ − x³ + 2x + 2** — all five free squares carry that
tilt to 170 digits.

**There is no crest between S38 and Trump.** On the tube-tracked branch the side rises MONOTONICALLY
as θ decreases from θ* — 3.928915 at 41.754°, 3.930704 at Trump's 40.182°, 3.932819 at 38.50°, and
on down to **3.956679 at 25.25°**, matching C₃ to 3e-9 at EVERY step of the 330-point sweep — and
`s − F_T` GROWS from +0.0408 to +0.1336 along the way: the descent is **not** the gap chain. (What
the branch does shed on the way down is `f3` and the `BR(0,0)`/`BR(0,1)` pair: below θ* the loaded
chain is the left+top wall – `f1` – `f0` – `f2` – `BL(1,0)`'s top face column together with
`f2` – `f4` – `TR(0,0)`'s corner, which is exactly what the drop-(c)/(e) derivation says.) It
cannot be — F_T's chain runs through BL(0,1)'s corner (1,2) and a lifted `BL(0,2)`, and **S38's
frame has no BL(0,2) cell at all** (its sixth slot is `BR(0,1)`), so the gap chain is not realisable
inside S38's grain. Getting from S38 to Trump is a SLOT change, not a tilt motion.

The crest the gallery's coarse tilt-sweep row shows (its 42.75° entry, 3.934169) is on the FAR side
from Trump: it is where the C₂ branch dies, at **42.7941°, s = 3.934377915** (C₂ there =
3.934377910, |s − C₂| = 5.1e-9), i.e. **+0.005463 over S38 and +0.057294 over ŝ**.

The no-trust-region version of the same sweep (`crest.py`'s `relaxed_path`) is kept in the results
as a counter-example: it reports 3.902308 at S38's OWN tilt, 0.0266 BELOW s*, because SLSQP leaves
the basin at the very first grid point. That is A108's trap in its path form and its numbers are the
tilt-pinned floor of the corridor, not a barrier.

## 6a. The two crests as points on Trump's basin boundary (data for the tube)

| family | crest tilt | crest side | over its own minimum | over ŝ | is it on Trump's basin boundary? |
|---|---|---|---|---|---|
| **S07** (k6_07 frame, Λ ∧ F_T) | **41.564880625°** | **3.886746028606** | +0.001128 | **+0.009662** | **YES** — the exact crossing `sin θ cos θ = 2 cos θ − 1`; below it the branch is F_T and falls monotonically to ŝ at θ_T = 40.181937° (A110 §3.3; A108's 0.05°-grid 3.886723 at 41.60° is this point). Trump's basin, entered along this family, is the tilt interval (θ_T-side of θ_c) and the wall height is 0.009662. |
| **S38** (k6_21 frame, C₃ ∧ C₂) | **42.7941°** (the C₂ branch dies) | **3.934377915** | +0.005463 | +0.057294 | **NO** — it is on the side AWAY from Trump. Toward Trump the branch RISES monotonically (3.928915 at 41.754° → 3.930704 at θ_T → 3.932819 at 38.50°) and `s − F_T` grows from +0.0408 to +0.0646. Trump's basin is not reachable from S38 by any common-tilt motion. |

The structural reason is the slot skeleton, not the tilt: F_T's chain needs BL(0,1)'s corner (1,2)
under a LIFTED `BL(0,2)`, and S38's frame (k6_21) has no `BL(0,2)` cell at all. Λ ∧ F_T is a
boundary of Trump's basin; C₃ ∧ C₂ is a boundary of a basin that never meets it. So for the tube
around Trump, S07 contributes a wall of height 0.009662 at 41.5649°, and S38 contributes nothing —
it is 0.0518 above ŝ and separated by a slot change, not by a tilt ridge.

## 6b. The cut inequality S38's local certificate would use

A116's N must be cut wherever a leaf's chain can dip below s0. For S07 that cut is A110's
`sin θ cos θ = 2 cos θ − 1` (θ_c = 41.564881°, Λ = F_T = 3.886746029), because below it the leaf's
selection realises the gap chain and F_T falls to ŝ. **S38's own grain needs no such cut**: both
branch formulas exceed s0 by a wide margin on the whole tilt range — min over (1°, 89°) of the
family value is 3.9289147 at θ*, i.e. **margin 0.051965 over s0**, six times S07's Λ margin of
0.008534. The single inequality a leaf certificate would carry is therefore the branch-selection cut

    **G(θ) ≥ 0  ⟺  θ ≤ θ\* = 41.754062677271°   (C₃ branch), G(θ) ≤ 0 ⟹ C₂ branch**,

with the numeric floors `C₃(θ) ≥ 3.9289147` on (0°, θ*] and `C₂(θ) ≥ 3.9289147` on [θ*, 90°). The
Trump canary is satisfied for free: no D4 image of Trump has a square in `BR(0,1)`'s cell with the
BL column open, and the tilt distance is 1.572°, so the tilt box must still be cut below ~40.2° —
the honest statement is that S38's tilt cut is `θ > θ_T`, not a grain boundary.

## 7. Class and kill

The slot cells decide the class (A53's `name_to_slots.json`, at s0):

* **S33 / S34 / S35 / K19** — cells (0.5,0.5) (0.5,1.5) (0.5,2.5) (1.5,0.5) (s0−0.5,0.5)
  (s0−0.5,s0−0.5) = census class **k6_07** under the identity of D4. That is exactly S07's class
  (A108 §8), i.e. trump5 + `BL(0,2)`.
* **S38** — cells (0.5,0.5) (0.5,1.5) (1.5,0.5) (s0−0.5,0.5) (s0−0.5,1.5) (s0−0.5,s0−0.5) =
  census class **k6_21** under the D4 element `diag`.

The covering kills, from A56's scoreboard as it stands AFTER A114 (A108's note recorded k6_07 as
PARTIAL with an open band; A114 closed it):

* **k6_07**: status **FULL** on [191/50, 969271/250000] = [3.82, s0] — the A53/A54 s0 certificate
  plus A56's parametric certificate re-verified by A114's sub-window bisection on
  [956767/250000, 969271/250000] with a full C2 canary.
* **k6_21**: status **FULL** on [3.82, s0] via A61's re-solved base certificate (enriched column
  pool, τ0 4.5, eps_geo 0.003, anchoring `gap`), also A114-touched.

All four points lie 0.040–0.052 ABOVE s0, so none of them is what those windows have to exclude —
the same reading as A108 §8 for S07.

## 8. Does A116's local certificate apply? (`a116_input.py`)

A116's N is a product of pose boxes around the load-bearing squares L, anchored in the class frame
AT s0 (poses dilated by s0/s*), plus the class pins P with their δ-slack cores; the soundness canary
is that no D4 image of Trump satisfies N's hypothesis, i.e. **some box of L must contain no Trump
square**. The largest centre radius at which that still holds is `r_max = max_{n∈L} min_j |c_n − c_j|`:

| shadow | L (free, load-bearing) | box that excludes Trump | r_max (position only) | its tilt distance to Trump |
|---|---|---|---|---|
| **S07** (A116's own run) | f0, f2, f4 | f2 | **0.0342** | 4.818° |
| **S33min / S35min** | f0…f4 | **f0** | **0.2054** | **40.182°** |
| **S38min** | f0…f4 (+ BR(0,1)) | **f1** | **0.6771** | **41.754°** |

So **yes, A116's machinery applies, and far more comfortably than at S07**. A116's S07 run needed
the Trump-boundary cut `sin θ cos θ = 2 cos θ − 1` as soon as r ≥ 0.033 / ρ ≥ 4.82°, because Trump
sits inside every S07 box beyond that. At S33min the keystone `f0` is **upright** while Trump's
corresponding square is at 40.182°, so f0's box excludes Trump for any r < 0.205 **or** any
ρ < 40.18° — an N of A116's headline size (r = 0.1, ρ = 40°) needs **no cut at all**. At S38min the
whole grain has moved: the tightest free box is 0.2947 from any Trump square and f1's is 0.6771.

Candidate leaf cuts, if one is wanted anyway:

* **S33min**: `θ_{f0} ∈ [−ρ, ρ]` with ρ < 40.182° (equivalently `|c_{f0} − (1.4847, 1.9341)|∞ < 0.205`).
  The load path L to hand A116 is the keystone plus its two diagonal partners, `{f0, f1, f3}` —
  the binding contacts are f0–f3 (0.478), f3–BR(0,0) (0.465), f0–f1 (0.462), f1–TR(0,0) (0.444),
  f0–BL(0,1) (0.394) — with `{f2, f4}` and the six cells as pins.
* **S38min**: the branch cut `G(θ) ≥ 0` of §6b plus the numeric floors C₃ ≥ 3.9289147 (θ ≤ θ*) and
  C₂ ≥ 3.9289147 (θ ≥ θ*), which beat s0 by 0.051965 — no grain-boundary cut is needed because
  F_T is not realisable in a frame without `BL(0,2)`.
