# A03-upper-reconstruct — exact reconstruction + rational certificate of the record 11-square packing

Owner: UB agent (A03). Date: 2026-08-16. Status: **done-success**.

## Goal
Rebuild the best-known packing of 11 unit squares (Trump 1979; s ≈ 3.877084) numerically, extract its
contact graph, solve the tangency system to 60 digits, verify the algebraic claims from `chat_history.txt`
(and A01 / Ellsworth), and emit machine-checkable exact rational certificates + an all-integer version for Lean.

## Files
| file | content |
|---|---|
| `optimize.py` | multi-start optimiser (penalty L-BFGS-B → SLSQP, analytic Jacobians; random + seeded starts; "kicks") |
| `canon.py` | D4 canonicalisation + sorting of a packing |
| `exact_solve.py` | contact detection (tol 1e-7) → mp Gauss–Newton at 70 dps → polynomial checks / PSLQ |
| `make_certificate.py` | builds the rational certificates in `certs/` and verifies them |
| `trump11_float.json` | SLSQP solution (double precision, canonical orientation) |
| `trump11_exact.json` | 60-digit coordinates, contact list (56 equations), Jacobian ranks, polynomial residuals, minimal polynomials of every coordinate |
| `trump11.png` | labelled drawing with all contact points |
| `runs.json`, `runs.log` | raw multi-start output (264 starts × (1 + 3 kicks)) |
| `local_optima.json`, `best_optima.png` | catalogue of the 36 distinct local optima found (34 with s < 4) |
| `../../code/squares.py` | shared geometry (corners, SAT separation with sign, containment, plotting) |
| `../../certs/verify_certificate.py` | stdlib-only exact verifier (Fraction/int; two formats) |
| `../../certs/trump11_certificate*.json` | the certificates (see below) |

## Method and precision
1. **Numerics.** Variables (cx,cy,θ)×11 + s. Constraints: 55 pairwise SAT separations (max over the 4 edge
   normals of the projection gap; analytic piecewise Jacobian) and 44 wall constraints. Pipeline: fixed-s
   penalty stage (s₀ ∈ [3.80,3.95]) → penalty continuation μ=10²…10⁶ (L-BFGS-B) → SLSQP (ftol 1e-16) →
   3 random "kicks" (angles N(0,0.05), positions N(0,0.01)) with re-solve. 264 starts (240 random, 8 each of
   three seed types), 8 workers, 16 min. Best: **s = 3.8770835900228136** (double), constraint violation 2e-15;
   agrees with the octic root 3.877083590022814177… to 1.4e-15 (better than the 1e-9 target).
2. **Contact graph.** 56 corner-on-line equations at |residual| < 1e-7 (listed in `trump11_exact.json`;
   summary below). All 34 unknowns kept (uprights' θ solved for, comes out 0 to 1e-71).
3. **Exact solve.** Gauss–Newton (least squares via normal equations, mpmath 70 dps; `mp.qr_solve` crashes
   the interpreter on this Python 3.14 build) converges quadratically: |r| = 6e-15 → 9e-30 → 6e-59 → 8e-71.
   Jacobian 56×34 has rank 34; restricted to the 33 position variables (s fixed) rank 33 ⇒ the equality
   system is infinitesimally rigid; all five tilt angles agree to 4.5e-71.
4. **Certificates** in exact rationals, verified by `certs/verify_certificate.py` (also independently
   accepted by A06's `lean/gen_cert_lean.py` pre-check).

## Exact results (60 digits; all in `trump11_exact.json`)
```
s      = 3.877083590022814177307897060100962706376455668463162560763968
theta  = 40.181937290329716465230342368060621542522658496343558387514453 deg   (CCW tilt of squares 6..10)
t      = tan(theta/2) = 0.365769307604677293388545018143311315239104830794924193607064
cos θ  = 0.763890...   sin θ = 0.645157...
```
Verified (residuals at 70 dps):
* octic `s⁸−20s⁷+178s⁶−842s⁵+1923s⁴−496s³−6754s²+12420s−6865` at s: **−3.6e-66** (coefficient size ~1e4 ⇒ consistent with zero);
  `mp.findpoly(s, 8)` independently returns exactly this octic (up to sign).
* `p(t) = 5t⁸+10t⁷−2t⁶−14t⁵+12t⁴+6t³+2t²−2t−1` at **t = −tan(θ/2)**: **1.8e-71**. (At +tan(θ/2) it is −1.04: the
  previous session's sign convention was θ clockwise / the mirror-image packing at 49.82°. Equivalently the
  minimal polynomial of +tan(θ/2) is 5t⁸−10t⁷−2t⁶+14t⁵+12t⁴−6t³+2t²+2t−1.) `findpoly(t,8)` returns it.
* minimal polynomial of cos θ: 5c⁸−12c⁷+8c⁶+2c⁵−c⁴−2c+1 (findpoly), as claimed in chat_history.
* Ellsworth's closed form **s = 2 + (2+sin θ)/(cos θ+sin θ)**: residual 1.9e-60. ✔
* The two small gaps in the tilted strip (pairs 6–7 and 8–9) are **exactly equal**:
  0.0248745350255969539804755091750095224366 (matches Ellsworth's u₁ = 0.0248745350255969539…). ✔
  Third gap (uprights 3–4, i.e. the slid square 4): 0.0325583143496147870626163003147461035156.
  Every coordinate lies in ℚ(t) (degree-8 minimal polynomials for all coordinates are in the JSON).

Canonical orientation (uprights hug bottom/left, tilt < 45°):
```
 i   cx                  cy                  θ
 0   0.5                 0.5                 0        (bottom-left corner)
 1   1.5                 0.5                 0
 2   s−0.5 = 3.3770835…  0.5                 0        (bottom-right corner; gap 0.877 to sq1)
 3   0.5                 1.5                 0
 4   0.5                 2.5325583143…       0        (slid up, gap 0.0326 to sq3)
 5   s−0.5               s−0.5               0        (top-right corner)
 6   1.5362871803…       3.1724754201…       θ
 7   1.6885587003…       1.9596128278…       θ
 8   2.4245254160…       1.2722538960…       θ
 9   2.4365087044…       2.6238338256…       θ
10   3.1724754201…       1.9364748937…       θ
```
(sq6.x = sq10.y and sq6.y = sq10.x: the strip's two wall contacts are congruent — this is the "sq1.y = sq5.x" of the old transcript.)

## Contact graph (physical contacts; 56 scalar equations in the JSON incl. redundant flush/corner ones)
* Uprights: 0 flush on x=0,y=0; 0|1 flush; 0|3 flush; 1 on y=0; 1 and 3 meet corner-to-corner at (1,1);
  2 flush on y=0 and x=s; 3 on x=0; 4 on x=0; 5 flush on x=s and y=s.
* Tangencies (corner → edge): sq1 corner (2,1) → sq8 left edge; sq2 corner (s−1,1) → sq8 bottom edge
  (sq8's lowest corner dips to y≈0.568 into the gap between squares 1 and 2);
  sq3 corner (1,2) → sq7 left edge; sq4 corner (1,2.0326) → sq7 top edge; sq4 corner (1,3.0326) → sq6 left edge;
  sq5 corner (s−1,s−1) → sq9 right edge; sq6 → sq9 top; sq6 corner on wall y=s; sq7 → sq8 top; sq7 → sq9 left;
  sq8 → sq10 left; sq8 → sq7 bottom; sq9 → sq7 right; sq9 → sq10 top; sq9 → sq6 bottom; sq10 → sq8 right;
  sq10 corner on wall x=s; sq10 → sq9 bottom.
  That is 18 independent equations for the 18 unknowns (5×3 tilted, x₂, y₄, s) — rigid.
* Non-contacts of note: sq6|sq7 and sq8|sq9 have parallel edges at distance 1.0248745…; sq3|sq4 gap 0.03256.

## Certificates (all PASS with `python certs/verify_certificate.py <file>`)
Recipe: scale centres by λ = s_c/s* about the origin (opens every contact by ~λ−1), round centres to 10⁻ᵏ with
10⁻ᵏ ≤ (λ−1)/10⁴, replace t by a continued-fraction convergent with error < 10⁻ᵏ; uprights t = 0.
| file | s_c | λ−1 | t | min wall margin | min pair margin |
|---|---|---|---|---|---|
| `certs/trump11_certificate.json` (+ `_int.json`, D = 31919509846100000000000, 23 digits) | 3877084/10⁶ | 1.06e-7 | 194075/530594 | 5287/10¹¹ = 5.29e-8 | 1.057e-7 |
| `certs/trump11_certificate_tight.json` (+ `_tight_int.json`, D 28 digits) | 3877083591023/10¹² (= s*+1e-9 rounded up) | 2.58e-10 | 2731751/7468508 | 12899/10¹⁴ = 1.29e-10 | 2.58e-10 |
| `certs/trump11_certificate_38771.json` | 38771/10⁴ | 4.23e-6 | 34796/95131 | 2.116e-6 | 4.23e-6 |
Verifier: stdlib `fractions.Fraction`/int only; checks unit rotation identity (centre-tilt) or exact unit-square
shape (integer corners: f = rot90 e, |e|² = D²), strict containment, and for every pair a separating axis among the
edge normals with strictly positive gap. Corruption tests: nudging square 8 by 1e-6 → FAIL (pairs 7–8, …); shrinking
the container to 3.877083 → FAIL (containment); editing one integer corner → rejected (not a square); shifting a
square in the int file by 2e-7 → FAIL. All exit code 1. `lean/gen_cert_lean.py certs/trump11_certificate_int.json`
(A06) accepts the int file (Python pre-check passed, D = 75 bits).

## Local optima catalogue (`local_optima.json`)
36 distinct s values from 920 feasible converged points; 34 with s < 4. Top of the list:
3.877083590 (Trump, ×20), 3.885618083 = 2+2√(8/9) (Göbel/Stromquist 0°/45° optimum, ×9), 3.886746029 (4 squares
at 41.565°, a rigid structure, ×35 — the most common non-trivial basin), 3.894321874, 3.897230787, 3.902673974, …
Nothing below 3.877084 was found.

## Surprises / lessons (for A04)
* **The 45° packing is a nonsmooth trap.** From the 2+2√(8/9) configuration SLSQP cannot descend to Trump's
  packing (ties in the SAT axes / corner-corner degeneracies make the linearisation wrong); a random kick of the
  tilt angles by ~0.03 rad immediately leads to 3.877084. Random starts alone hit the Trump basin rarely
  (20 of 1056 converged points, most of them via kicks); the 4×4-lattice basin (s = 4) dominates.
* First-order LP tests (KKT / rigidity) on the max-over-axes SAT constraints are **invalid** at nonsmooth points
  (they report spurious descent directions for uprights flush on walls). Rigidity was therefore established via the
  rank of the smooth corner-on-line contact system (33/33) plus 30 random perturbation re-solves (all return
  to s* or to a worse optimum; none below).
* `mpmath.qr_solve` hard-crashes Python 3.14 here on a 56×34 system; normal equations at 70 dps work fine.
* Many local optima contain rattlers (loose squares) — angle multisets alone do not identify an optimum; s does.

## Next steps
* A04: use `optimize.solve_with_kicks` (kicks are essential) and the seedC start; the catalogue suggests exploring
  the 3.8867 (four-tilted) family and structures with 6–8 tilted squares.
* A06: consume `certs/trump11_certificate_int.json` (format documented in `certs/verify_certificate.py`).
