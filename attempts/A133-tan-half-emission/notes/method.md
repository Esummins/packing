# A133 — method: the local certificate re-emitted in `t = tan(θ/2)`

## Discipline

* READ-ONLY on every campaign and on A116/A119/A120/A126.  A119's certificates and A125's are
  READ; A119's `code/fastlp.py` is IMPORTED (the HiGHS binding, never edited).  Everything new
  lives under `attempts/A133-tan-half-emission/` plus the two new Lean files
  `lean/PackingCertMathlib/PackingCertMathlib/LocalCertT.lean` and
  `lean/PackingCertMathlib/scratch/A133Axioms.lean`.  Nothing of A119's, A120's or A126's is
  edited, and `Local.lean` / `LocalCert.lean` are untouched.
* One `lake build` at a time through A119/A78's `lakeb.py` (repo-wide lock, BELOW-NORMAL); at
  most two Python processes; `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes; frozen verifiers
  untouched (this attempt never invokes `verify_case.py` / `verify_param*.py`).
* Every number that reaches a certificate is produced in EXACT rational arithmetic
  (`fractions.Fraction`) and re-verified by a program that shares no code with the producer.

## Why `t` and not `θ`

`Parametrize.cosT t = (1 − t²)/(1 + t²)` and `sinT t = 2t/(1 + t²)`.  In the angle the certificate
needs a certified interval kernel for `cos`, `sin` and `π` — A119's `exactiv.py`, 96-bit dyadic
integers, a rigorous `π`, argument reduction and the location of the `π/2` kink of
`w = |cos| + |sin|`, and A126 named formalising it in Lean as the one obstacle left in front of
`CertCover`.  In `t` there is nothing to formalise: every quantity a local certificate needs is
the exact range of a RATIONAL function of the tilt parameters over a rational cell.

| the certificate needs | in `θ` (A119) | in `t` (A133) |
|---|---|---|
| `cos` / `sin` over a cell | Taylor + remainder, `π` for the critical points | the ENDPOINT VALUES: `cosT` decreasing, `sinT` increasing on `[0, 1]` — exact, zero enclosure error |
| `w = \|cos Δ\| + \|sin Δ\|` over a cell | endpoints plus the multiples of `π/4` inside it | `u = tan(Δ/2) = (t_w − t_o)/(1 + t_w t_o)` is monotone in each argument, and `w` is a function of `\|u\|` alone with one interior maximum `√2` located by the RATIONAL test `(u+1)² ⋛ 2` |
| an affine lower bound of `w` | the chord (no interior kink) or the two V-lines through the kink at `j π/2` — `exactiv.kink_in`, the one place `π` is unavoidable | the two SMOOTH branches `cos Δ ± sin Δ`, valid on the whole cell, whose maximum is `w`: no kink location, no `π`, and one fewer case in the generator AND in Lean |
| an affine lower bound of the wall half-width `h` | chord of `w/2` | `h(t) = (1 + 2t − t²)/(2(1 + t²))` is CONCAVE on `[0, 1]` (`h'' = 2(t−1)(t²+4t+1)/(1+t²)³ ≤ 0`), so the chord through the two exact endpoint values is a lower bound, with no rounding at all |
| the `q sin φ` term of Lemma RELAX | McCormick on `q·φ` with `\|sin φ − φ\| ≤ \|φ\|³/6` | `S(t) = sin(θ(t) − θ(t*))` is the rational function `(2 c* t + s* (t² − 1))/(1 + t²)`; it is enclosed between two affine functions of `t` with the same secant slope, so the McCormick step needs NO series remainder |
| a certificate that an envelope is valid | — (the enclosure was the proof) | a BERNSTEIN positivity test on an exact rational polynomial: decidable, and the same test in Lean |

Finding E3 of A126 disappears twice over: a tilt cell that leaves the fundamental domain is
clipped to its inside part at the DEFINITION of `N` (so the emitted `N` is exactly the `N` the
certificate is about, and it is smaller than A119's — the sound direction), and nothing downstream
ever needs a `Box` to carry two intervals.

## The pieces

| file | what it is |
|---|---|
| `code/a133lib.py` | the exact rational geometry: `cosT`/`sinT` and their exact ranges, `u_of`/`w_range` (the EXACT range of `w`), the Bernstein transform in one and two variables, and the three affine envelopes with their Bernstein certificates |
| `code/gen_local_t.py` | T1: reads `N` out of an A119 (or A125) certificate, re-expresses the tilt cells in `t`, and rebuilds the selection tree, the census, the Farkas leaves and the emitted certificate from scratch.  Emits `certs/<id>.tcert.json.gz`, format `local-cert-t-v1` |
| `code/check_local_t.py` | T1: the INDEPENDENT checker.  Shares no code with the generator, no LP, no floats in any decision path, and **no early return** |
| `code/control133.py` | T1: the control — re-check, nine mutations, and the survivor count |
| `lean/…/LocalCertT.lean` | T2: the exact `t` enclosures, the kink-free `w` branches, the positivity certificate and its soundness, and the tilt cover with its soundness |
| `lean/PackingCertMathlib/scratch/A133Axioms.lean` | T2: the axiom audit |
| `notes/fcover.md` | T3: the F-COVER fix, specified |

## Lemma RELAX in `t`, exactly as emitted

Over a leaf's cell, with `m` the midpoint of the owner's `t`-cell, `a_k(θ(m))` an EXACTLY RATIONAL
unit vector, `P = ε d·a_k(θ(m))` and `Q = ε d·a_{k⊥}(θ(m))` affine forms in the LP variables:

```
Proj  =  P cos φ + Q sin φ                                (axis_decomp, exact)
      ≤  P + max(0, −P_lo)·(1 − cos φ)_max  +  U          (U one of three bounds on Q·sin φ)
```
with `φ = θ(t_w) − θ(m)`, `u = tan(φ/2) = (t_w − m)/(1 + t_w m)`, and

* `(1 − cos φ)_max = 2U²/(1 + U²)`, `U = max |u|` over the cell — exact rational;
* `(A)` `Q sin φ ≤ |Q|·max|sin φ| ≤ S_abs (m_q Q + c_q)`, the chord of `|Q|` over `[Q_lo, Q_hi]`;
* `(B1)/(B2)` McCormick, `(Q − Q_hi)(S − S_lo) ≤ 0` and `(Q − Q_lo)(S − S_hi) ≤ 0`, with `S`
  replaced by its affine upper or lower envelope according to the sign of the multiplier.

The row is `1/2 + W_lb/2 − (P + corr + U) ≤ 0`, implied by the selection's own
`Proj ≥ 1/2 + w/2`, and `W_lb` is one of the two branch bounds of `w`.  Wall rows are
`−c + (m_h t + c_h) ≤ 0` and `c − s + (m_h t + c_h) ≤ 0`.

Measured tightness of the envelopes (random cells, `code/a133lib.py` self-test): the `S` enclosure
is `≤ 0.23 h²` wide and the best of the two `w` branches is within `2.3 h²` of `w`, `h` the cell
half-width — SECOND order, the same order as A119's relaxation in the angle, which is why the
trees come out the same size or smaller.

## Rounding

The emitted rows sit on the denominator `10¹²`: coefficients to the nearest multiple of `1/10¹²`
and the constant LOWERED by the total rounding slack over the leaf's box, so the emitted row is
IMPLIED by the true relaxed row on that box.  The Farkas bound is then RE-EVALUATED from the
emitted integers and required to exceed `s0` before the file is written (`gen_local_t.emit`
raises otherwise); the worst quantised margin per certificate is recorded in the file's `meta`.
`10¹²` is three decades finer than A126's `10⁻⁹` and costs nothing here because the certificate
carries the rows as decimal integers.

## How the checker is independent

`check_local_t.py` imports nothing of the generator's.  It rebuilds Lemma RELAX from its own
implementation of the geometry and it does not re-derive the affine envelopes — it **verifies**
the ones the certificate records, by decision procedures of its own:

* the two univariate families (`h`'s chord, `S`'s two-sided enclosure) **EXACTLY, by Sturm's
  theorem** on the square-free part — a complete decision procedure, and a different algorithm
  from the generator's Bernstein test;
* the bivariate family (`w`'s two branches) by a subdivided tensor-product Bernstein test written
  from the definition in that file and subdivided DEEPER than the generator's.

Then, for every row a Farkas multiplier names, it builds its OWN row out of the verified
envelopes and requires `min over the leaf's box of (own − emitted) ≥ 0`: the emitted row must be
IMPLIED by a row the checker derived.  Only then is the emitted row used in the Farkas bound.
Finally it walks the whole tree — every bisection, every `branch`'s excluded selections, every
`imp`/`imp_sel`, every leaf — with **no early return**: failures are collected and counted and the
verdict is the conjunction at the end, and every emitted leaf must be referenced by the tree
exactly once.

**A126's finding E2 cannot recur.**  In `gen_local_t.py` a leaf is recorded by ONE code path,
`TreeT._close`, taken by a finite side bound and by an infeasibility ray alike; the emitted leaf
count is asserted equal to the tree's own dead-leaf counter before the file is written; and the
checker independently requires every emitted leaf to be referenced exactly once by the tree.

## Results

See `notes/results.md` for the tables (leaf counts, walls, sizes, controls, survivor counts).
