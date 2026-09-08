# A134 — method

## Discipline

* READ-ONLY on every campaign and on A116/A119/A120/A126/A133.  A133's `gen_local_t.py`,
  `a133lib.py` and `check_local_t.py` are IMPORTED, never edited; A119's certificates are read.
  Everything new lives under `attempts/A134-certcover-close/` plus three new Lean files
  (`lean/PackingCertMathlib/PackingCertMathlib/LocalCertT2.lean` and the scratch files
  `scratch/A134Axioms.lean`, `scratch/A134PCert{S07,S02,Tiny}.lean`).
* One `lake build` at a time through A78's `lakeb.py` (repo-wide lock, BELOW-NORMAL); at most two
  Python processes; `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes; frozen verifiers untouched.
* Every number that reaches a certificate is exact rational arithmetic and is re-verified by a
  program that shares no code with the producer.

## T1 — what the generator had to add, and why it is exactly this

A133's `.tcert` records the affine envelope CONSTANTS; its Python checker re-derives their
validity by decision procedures of its own (Sturm for the two univariate families, a deeper
subdivided Bernstein test for the bivariate one).  Lean cannot re-derive: `LocalCertT.posCheck`
decides `p ≥ 0` on `[a, b]` from a certificate

    p(X) = Σ_k c_k (X − a)^k (b − X)^{n−k},   c_k ≥ 0,   n = len(c) − 1,

which is the list of SCALED BERNSTEIN COEFFICIENTS `c_k = β_k C(n,k)/(b−a)^n`, and its check is
`c_k ≥ 0` plus one EXACT LIST equality.  So `gen_local_t2.py` emits, per envelope entry, the
chain of pieces and their coefficient lists.

Three details decided the shape of the field.

1. **List shapes are load-bearing.**  In Lean's `pmul`, only the FIRST argument's `[]`
   short-circuits, so `pmul p []` is a list of zeros, and `posAux a b c (len c − 1)` carries
   exactly ONE trailing zero beyond the degree.  `posCheck` compares lists with `==`, so a
   certificate that reproduces the polynomial only up to trailing zeros is REJECTED by the
   kernel.  `code/leanpoly.py` therefore transcribes `padd`/`pscale`/`pmul`/`ppow`/`posAux` (and
   the bivariate `posAuxP`/`posAux2`) with the same recursion and the same truncated `Nat`
   subtraction, and every envelope polynomial is defined through `padZ` on both sides.
2. **Subdivision.**  A single-interval Bernstein test is only sufficient, and the generator's own
   envelope search subdivides (`a133lib.DEPTH1 = 2`, `DEPTH2 = 1`).  The emitted certificate is a
   CHAIN of pieces laid end to end from `a` to `b` (`LocalCertT2.posChain`), and for the bivariate
   family a chain in `t_w` each of whose pieces carries a chain in `t_o` (`posGrid`).  **Measured
   cost: zero** — every envelope of all four families certifies at DEPTH 0, one piece, on both
   re-emitted certificates.  The reason is structural: `a133lib.chord_h` verifies its chord with
   the Bernstein test already, and `aff_bounds_S` / `aff_lower_w` choose the offset as the extreme
   Bernstein RATIO over the subdivided cell, which is exactly the offset that makes the residual
   Bernstein-nonnegative on every subbox — and, it turns out, on the whole cell.
3. **The degenerate side.**  A class pin's tilt cell is the single point `t = 0`, so a `w`
   envelope with a pin on one side is stated on a box with one side collapsed, where the Bernstein
   basis is meaningless (`(b−a)^n = 0`).  The honest reduction is to SUBSTITUTE the fixed value:
   `pcert.w[…].mode` is `"xy"`, `"x"` (`t_o = 0`) or `"y"` (`t_w = 0`), and Lean's `substY0` /
   `substX0` do the same substitution in two `List` operations.

**Why replacing the checker's Sturm argument by the same Bernstein form is sound.**  Sturm is a
COMPLETE decision procedure; Bernstein positivity is only SUFFICIENT.  So the substitution can
only make the generator emit fewer envelopes (a cell that does not close is bisected instead),
never a wrong one — the direction that keeps the certificate sound.  Nothing about the emitted
certificate's meaning changes, and the independent checker still runs Sturm on the same entries
(`check_local_t2.py` half (a)); the Bernstein certificate is an ADDITIONAL artefact for the
kernel, checked against the same constants.

**One gap found and closed.**  Lemma RELAX's selection row consumes three constants A133 did not
record — the two McCormick corners `S_lo`, `S_hi` (also the chord scale `S_abs` of envelope (A))
and the correction constant `K = max(1 − cos φ)` on the cell.  A133's Python checker recomputes
them from the cell; Lean cannot.  They are now emitted with their own positivity certificates
(`pcert.S[…].s_lo/s_hi/K` and the chains `c_lo`, `c_hi`, `corr`), the first two as the `alpha = 0`
case of the same `sUpPoly`/`sLoPoly` and the third as a new `cPoly`.

## T1 — how the checker is independent

`check_local_t2.py` has three halves:

* **(a)** A133's `check_local_t.Checker` imported and run UNCHANGED (`local-cert-t-v2` is a
  superset of `v1`): the envelope table decided by Sturm and by the deeper Bernstein test, every
  row named by a Farkas multiplier verified IMPLIED by a row the checker built itself, every
  `branch` node's excluded selections, every `imp`/`imp_sel`, every leaf referenced exactly once,
  no early return.
* **(b)** the `pcert` field, with the polynomial layer written FROM THE LEAN SOURCE (not from the
  generator's `leanpoly.py`): the chain tiles the cell exactly (the same condition `posChain`
  decides), every coefficient is `≥ 0`, `posAux` reproduces the polynomial as an exact list, and —
  the check an internally consistent forgery would fail — the polynomial MEANS what it should, by
  comparing its value at random rational points of the cell with the geometric expression computed
  from this file's own `cT`/`sT`.  `env` and `pcert` must have exactly the same keys.
* **(c)** a mutation control: bumping one certificate coefficient, deleting one piece of a chain
  and shrinking one piece's interval must each be REJECTED.

## T2 — the shape of the Lean side

`LocalCertT2.lean` imports `LocalCertT` (A133) and `SatInterior` (A126) and adds, in the same
style, a decidable check plus one soundness theorem per piece.  What made each piece work:

* **(C2)** is an interval computation, and in `t` every ingredient is exact: `cosT` antitone and
  `sinT` monotone give the endpoint values (`LocalCertT.cosT_mem` / `sinT_mem`), so the ONLY
  enclosure error is the one interval multiplication introduces.  The support width is bounded
  BELOW without the kink and without `π` by `w = max(cos Δ + sin Δ, cos Δ − sin Δ)`, each branch
  bounded by interval arithmetic on `cosRel` / `sinRel` — sharp up to the interval widths.
* **(C3)** decomposes into one 3-line assembly (`relax_selection`) and five ingredient lemmas.
  The assembly is the whole of Lemma RELAX for the selection family: given the selection's own
  `g_σ ≥ 0`, the exact axis decomposition, the correction bound, one of the three `Q·S` envelopes
  and a certified plane below `w`, the emitted row follows by `linarith`.  The axis decomposition
  (`Local.axis_decomp` in the angle) is in `t` an ALGEBRAIC IDENTITY — one `linear_combination`
  against `cos² + sin² = 1`, with no angle anywhere.
* **(C4)**'s load-bearing half is not the index arithmetic but the passage from `LocalHyp` to one
  square per body WITH pairwise interior-disjointness, which is what the selection cover consumes.

## T3 — the elaborator wall

`gen_pcert_lean.py` writes the emitted `pcert` out as a Lean scratch file and asserts
`posChain`/`posGrid` on all of it by `native_decide` — the loop generator → checker → kernel,
closed on real data.  A126's finding recurs exactly: a single list literal of a few thousand
rationals dies in the ELABORATOR (`(deterministic) timeout at isDefEq` at 200 000 heartbeats),
and A126's remedy works — batches of 32 entries per `private def`, concatenated linearly, plus
`set_option maxHeartbeats 2000000`.  Walls in `notes/results.md`.
