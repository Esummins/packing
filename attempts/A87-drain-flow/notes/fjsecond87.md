# A87 chore — second-order classification of the 167 certified k0 Fritz-John points

Answers the PI's question: *are any of the 167 tight-certified k0 FJ points genuine LOCAL
MINIMA of the enclosing side, or are they saddles along their flat directions?*

Driver `code/fjsecond87.py` (`selftest|probe|run|report`); log `logs/fjsecond87.log`;
results `results/fjsecond87.jsonl` (per point) and `results/fjsecond87.json` (summary).
Input: the 167 `survivor_tight` records of `results/cp87_fj_polished.jsonl` (FJ at the tight
end of the ladder, tol 1e-6, cone residual ≤ 1e-7). One process, BLAS pinned to 1 thread,
**881 s** (15 min) for 167 points, 4 730 SLSQP re-optimisations. No certificate emitted,
nothing committed; A57/A60/A61/A85/A86/A88/A89 untouched.

## 0. Headline

**Neither. Not one of the 167 is a strict local minimum, and only one is a saddle.**

| class | count |
|---|---|
| STRICT LOCAL MIN | **0** |
| DEGENERATE (flat directions, no descent) | **166** |
| SADDLE (verified descent) | **1** (`o252`) |

* **`o012` (σ = 3.897230787, the lowest certified k0 FJ point) is DEGENERATE.** Its flex space
  has dimension **d_H = 10** (3 rattler + 7 non-rattler) and the restricted Hessian of the
  Lagrangian on it is **identically zero** — `|Hred|_max = 1.0e-16` against `‖∇²L‖ = 0.958`,
  i.e. 16 orders down. Not one of 26 probe directions (10 eigen-directions of Hred, 6 random
  flex directions, 10 critical-cone directions), at ±1e-4 and ±1e-3, re-optimises to a smaller
  side: the largest verified drop is **1.3e-15** (float noise). It is a *flat valley*, not a
  well and not a pass.
* The single saddle **`o252`** sits at σ = 4.242892863 with d_H = 2, no rattlers, and **unique**
  multipliers. Its restricted Hessian has one strictly negative eigenvalue **−3.956e-3**
  (threshold 1.5e-9), and the numerical probe agrees: a step of 1e-3 along that eigenvector
  re-optimises down to **σ = 4.242640687 = 3√2** (drop **2.522e-4**), a verified packing
  (min SAT gap 1.0e-11). The descent **stays in k0** (k_flush_corner = 0) and lands 0.366
  **above** ŝ. It is the *only* point where the second-order test and the numerical descent
  both fire, and they agree.
* **Nothing descends below ŝ or s₀.** Lowest side any descent reached: 4.242640687.
  Saddles exiting k0: **0**.

So A87 §5.4 / `notes/fj_polish.md`'s picture is refined, not overturned: the k0 critical set
A85's census can see is not a set of isolated wells at σ ≥ 3.8972 — it is a set of **flat
strata** (positive-dimensional families of equal-side k0 FJ points), plus one pass leading
down onto one of those strata.

## 1. Method and what makes each verdict sound

**(1) Flex space.** With s = z₃₃ and objective ∇s = e₃₃, a direction with zero first-order
change of the side that holds every active row to first order is exactly
`H_flex = {y : y₃₃ = 0, ∇g_k·y = 0 ∀ k ∈ A}` = `null(A[:, :33])`, so
**d_H = 33 − rank₃₃** — the `flat_dim_33` fjpolish87 already reported. Because `A[:, :33]`
has an identically zero column block at every **rattler** square (one touched by no active
row), the flex space is an exact coordinate direct sum

    H_flex  =  R^{3·n_rattlers}  ⊕  null(A[:, non-rattler coords]),

verified at all 167 points (`n_split_ok = 167`). d_H distribution 2 … 24 (median 16),
2 756 flex dimensions in total, of which **1 383 are rattler** dimensions.

**(2) Second order.** For `min s s.t. g ≥ 0`, `L = λ₀s − Σλ_k g_k` and `∇²L = −Σλ_k ∇²g_k`
(s is linear, so it contributes nothing). `Hred = Zᵀ ∇²L|₃₃ Z` on an orthonormal basis Z of
H_flex; eigenvalues thresholded at 1e-9·‖∇²L‖.

*Multiplier ambiguity is handled, not ignored.* Six of the 167 admit the λ₀ = 0 branch
(a nonnegative self-stress), so the multiplier set is an unbounded polytope and a verdict read
off one NNLS λ would not be safe. Every multiplier differs from λ by an element of ker(Aᵀ)
and Hred is affine in λ, so the sweep evaluates `Zᵀ(Σ d_k ∇²g_k)Z` on a basis of ker(Aᵀ):

| | count of 167 |
|---|---|
| multiplier unique (dim ker Aᵀ = 0) | 15 |
| **Hred identical for EVERY multiplier** | **152** (all the non-unique ones) |
| Hred multiplier-dependent | 0 |
| second-order sufficient for *some* multiplier | **0** |

So **the second-order verdict is multiplier-free at all 167 points.** (Individual row
Hessians are *not* flat on the flex space — at `o012`, `max_k ‖Zᵀ∇²g_k Z‖ = 0.95` on row
`S-7-3-3-1` — so the vanishing of Hred is a genuine cancellation under the multipliers, not
an artefact of restricting to a small subspace.)

**(3) Direct numerical check** — the decisive test, and multiplier-free. From z* ± t·y
(‖y‖_∞ = 1, t ∈ {1e-4, 1e-3}, plus 1e-2 on any genuinely negative-curvature direction) the
side is re-optimised by SLSQP over the **sound inner model** of the packing problem: 176
smooth wall rows plus, for each of the 55 pairs, one chosen separating axis (owner o, edge e)
with all four corners of the partner on its far side. Any feasible point of that model is a
genuine packing, so any side it reaches is genuinely achievable; the axis choice is refreshed
between outer rounds, so contacts are free to form, break and slide. Every returned
configuration is re-verified independently (`sigma_verified`: canonicalise, then inflate about
the bbox centre until all 55 SAT gaps are ≥ 1e-11 — inflation can only *raise* the side), so a
reported drop is a drop to a **verified feasible packing**, never SLSQP slop.

Direction menu per point (median **28** probes, 4 730 total): the d_H eigen-directions of Hred,
6 random directions in the non-rattler flex subspace ("the flex subspace as a whole"), and the
**critical-cone** directions — the flex *subspace* holds every active row at 0, but the
critical *cone* also lets the zero-multiplier active rows OPEN, and a second-order descent can
hide there. Those are reached by LP (a Gaussian essentially never lands in that thin cone):
one "most interior" direction plus one per zero-multiplier row maximising its opening, plus
nonnegative mixes. 158 of 167 points have such directions; `d_cone_sub` runs 4 … 27
(median 25) against d_H ≤ 24.

**Baseline correction (this mattered).** cp87's polish stops at a finite residual, so a
certified point can sit slightly above its *own* local optimum; that offset appears in **every**
probe direction and would be misread as a descent. Every point is therefore also re-optimised
with **no perturbation at all**, and probes are scored net of that baseline. Exactly one point
has a baseline above the 1e-9 margin: `o075` (σ = 4.000000002, baseline drop **1.727e-9**,
identical to its best probe drop, isotropic across all 25 directions, all |eigenvalues| ≤ 1e-10).
Without the correction `o075` reads as a saddle; it is not one — it is an FJ certificate that
is 1.7e-9 loose. It is classified DEGENERATE. Separation is otherwise total: the largest
|net drop| among the 166 non-saddles is **1.1e-12**, against 2.5e-4 for `o252` — eight orders.

**Self-test 9/9** (`python fjsecond87.py selftest`): Aᵀλ = e_s residual 2.1e-16; flex basis
orthonormal with A₃₃·Z = 2.6e-16 and d_H = rattler + non-rattler; Lagrangian Hessian vs central
finite differences 1.1e-11; SLSQP wall rows vs t3lib's own row evaluation 4.4e-16; constraint
Jacobian vs finite differences 4.0e-9; inner-model pair rows ≤ true SAT gaps (soundness);
re-optimising *from* a certified point finds nothing; re-optimising from a 2 % inflation of it
returns to it (3.955175 → 3.897231, so the solver does descend when there is anything to
descend); centre-centre block of ∇²L exactly 0.

## 2. Why there are no strict local minima — a structural reason, not a numerical one

Every row of the system (wall, separation, dominance) is **linear in the centre coordinates**;
all curvature lives in the angles. Hence the centre-centre block of ∇²L is **exactly zero**
(self-test S9), and any flex direction with no θ component has *exactly* zero second-order
change of the side, for every multiplier.

**All 167 points have at least one pure-translation flex direction** (2 056 of the 2 756 flex
dimensions, 75 %, are translational; 4 points are purely translational). So no certified point
in this census can satisfy the second-order sufficient condition, and the "0 strict local
minima" line is not a threshold artefact — it is forced by the geometry of the rows.

Geometrically the flat directions are, per point: **rattlers** (a square touched by no active
row floats inside its cage — 152 of 167 have at least one, 1–7 rattlers, 3 flat dimensions
each), and **sliding squares** (a square translating along its contact line; 0–10 sliding
squares per point, median 5). The remaining flat directions **tilt** squares (0–11 tilting
squares, median 3) and are flat by cancellation rather than by structure. `o012` for instance:
square 5 rattles, squares 0/4/9 slide, squares 3/5/7 tilt, squares 1/2/6/8/10 are rigid.

## 3. Curvature census

| Hred on the flex space | count of 167 |
|---|---|
| **identically zero** (`\|Hred\|_max / ‖∇²L‖ < 1e-12`) | **148** |
| one positive eigenvalue, rest zero | **18** |
| one negative eigenvalue, rest zero | **1** (`o252`) |
| positive definite | **0** |

The 18 with a positive direction are the σ = 3√2 = 4.242640687 family (`o237`–`o251`, 15
points, `Hred/‖∇²L‖` 0.037–0.169, d_H 10–22) and `o025`/`o026` at σ = 3.982843051 (d_H 6 and 4).
All still carry 3–21 zero directions, so all are DEGENERATE.

`n_neg_curv > 0`: 1 of 167. Most negative relative eigenvalue anywhere: −2.6e-3 (`o252`).

## 4. The one saddle, in full

| | |
|---|---|
| tag | `o252` (A85 optimum idx 252) |
| σ at the FJ point | 4.242892863457930 (ŝ + 0.3658) |
| m_active / d_H / rattlers | 32 / **2** / 0 |
| multipliers | **unique** (dim ker Aᵀ = 0), cone residual 1.4e-13 |
| Hred eigenvalues | **−3.955999e-3**, +6.9e-17 |
| descent direction | `eig00` (the negative eigenvector), sign −1, step t = 1e-3, "mixed" (translation + tilt) |
| σ reached | **4.242640687147571 = 3√2** (drop 2.522e-4) |
| landing verified | min SAT gap 1.0e-11 > 0, feasible packing |
| stratum landed in | **k0** (k_flush_corner = 0) |
| below ŝ / s₀ | **no / no** |

Its descent lands exactly on the σ = 3√2 plateau occupied by 15 other tight survivors
(`o237`–`o251`) — i.e. the pass leads onto the flat stratum, as one would expect. 7 of its 8
flex/cone probe directions found the same drop (`descent_isotropic` 0.875), consistent with a
2-dimensional flex space one of whose directions is downhill.

## 5. Caveats

1. **"No descent found" is evidence, not proof.** The probes are a finite direction menu at
   two step sizes with a local solver. What *is* rigorous in the other direction: every drop
   reported is to an independently verified feasible packing, so `o252`'s saddle verdict is
   solid, as is the fact that nothing reached ŝ.
2. **The second-order verdict is only as good as the active set.** Classification uses
   `active_rows_at_point` at tol 1e-6 and the *first* consistent selection per contact pair —
   `notes/fj_polish.md` §6.3's caveat carries over verbatim. A different tie selection could
   change the active row list and hence Hred.
3. **DEGENERATE is not "local min".** A flat valley may descend at third order or beyond;
   166 points are certified only as "no negative second-order curvature for any multiplier and
   no descent found by 4 730 probes". Proving any of them a local minimum needs a higher-order
   or exact argument, which nothing in the lab currently wants.
4. `o075`'s certificate is 1.7e-9 loose (§1). Its side is 4.000000002 rather than 4 exactly;
   cosmetic here, but it is the one place where cp87's polish visibly did not finish.

## 6. Bearing on DF-K0 / H1

Nothing changes for **DF-K0** (which quantifies over the true global minimiser) and nothing
changes for the **H1 price** (§6 of `docs/proofs/drain_flow_k0.md`): the cover cost is set by
the 33-dimensional volume at the discharge scale, not by the shape of the critical set.

What does change is the picture of that critical set, and one line of it is mildly useful:
the k0 FJ points A85's census reaches are **flat strata, positive-dimensional and degenerate**
(d_H 2–24, Hred ≡ 0 at 148 of 167, second-order sufficiency nowhere), not isolated
non-degenerate minima. That is the *un*favourable case for any Krawczyk-on-FJ scheme — it
confirms `drain_flow_k0.md` §6.4 ("their FJ Jacobian in the complementarity form is singular")
from the second-order side as well, and it means an FJ certificate near one of these points
cannot be closed by a nondegeneracy/isolation argument. It also means the one visible saddle
does not open a route downward: `o252`'s descent stops on the 3√2 plateau, 0.366 above ŝ, and
stays in k0.
