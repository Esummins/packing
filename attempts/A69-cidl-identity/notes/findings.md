# A69 — (c-idl) certificate campaign: findings (Fable lead, 2026-09-01)

Labels: [T] proved, [M] computed exact, [F] finding, [C] open, [E] engineering.

## Headline

**[T/M] CERTIFICATE FOUND AND VERIFIED.** The saturated ideal-membership certificate
closing ŝ_A22 = ŝ_octic (TopLevel axiom `shatA22_eq_shat`) exists, is small (301 KB),
and was found by EXACT LINEAR ELIMINATION — no Gröbner basis, no Macaulay matrix, no
msolve. `certs/cidl_identity.json` + `certs/verify_cidl.py`: PASS in 0.7 s, stdlib
fractions only; corruption gates (qcoeff / e / rowspec / octic) all FAIL loudly.
Full construction + composition: `docs/proofs/attainment_ub.md` §7.

## Why no Gröbner campaign was needed

* [T] A22's certified exact structure (headline item 2: uprights pinned, one common
  tilt angle) + Weierstrass t = tan(θ/2) reduce the 38 curated rows to 13 distinct
  generators that are LINEAR in the 12 remaining unknowns (y4, tilted centres, S)
  over ℚ[t] (coefficient degree ≤ 4). The flush-pair collapse is exact: with equal
  angles the two corner rows of each flush tilted pair are rational multiples.
* [M] 12 of the 13 rows (leave out E1c2-8e3) give a nonsingular A(t): Δ = det A has
  degree 34, gcd(Δ, m) = 1. Cramer/adjugate identities provide all cofactors
  explicitly; the leftover row gives the consistency determinant D(t), degree 35.
* [M] D factors with exactly ONE factor vanishing at t̂:
  m(t) = 5t⁸−10t⁷−2t⁶+14t⁵+12t⁴−6t³+2t²+2t−1 = A03's PSLQ p(−t) — **the tan-half
  minimal polynomial is now DERIVED from the contact system, upgrading A22 §7 gap 2**;
  e := D/m (degree 27), gcd(e, m) = 1.
* [M] **m | G_oct** where G_oct := Σ_k a_k N_S^k Δ^(8−k) (degree 272) — the octic
  membership itself. Telescoping assembles the identity
  e·Δ⁸·octic(S) = Σ_j q_j·G_j with h = e·Δ⁸ the saturation factor,
  cofactors bivariate in (t, S).
* [F] The §6 (attainment_ub) height-bound pessimism ("doubly exponential") priced the
  UNSTRUCTURED a-priori route; the structured slice is a 12×12 univariate Cramer
  computation. Measured sizes: deg Δ 34, deg D 35, deg e 27, deg G_oct 272,
  cofactor t-degrees ≤ ~330, coefficients a few hundred bits. Total search compute:
  ~2 min in plain Python fractions.

## [F] The "degree-7 coordinate" never existed (A53 L4 / (c-alg) obstacle VOID)

Δ(t̂) ≠ 0 forces every coordinate of ẑ into ℚ(t̂) (degree 8). A03's per-square
`minpoly_cx/cy` JSON fields are findpoly artifacts: the recorded degree-7 poly for
cy4 evaluates to −8.0e8 at the true ŷ4 (250 dps) — generic magnitude, not a root;
cx2 = S−1/2 (necessarily degree 8) also carries an 8-coefficient (deg-7) entry.
True minpoly of ŷ4 (derived via Res_t(m, Δ·Y − N_y4), vanishes to 6e-255; untrusted
diagnostic): 256Y⁸−4608Y⁷+37376Y⁶−167040Y⁵+440352Y⁴−674912Y³+437376Y²+327464Y−599659.
A03's 60-digit coordinate STRINGS are fine (all 13 generators vanish to ≤ 6.7e-60 at
the A03 point). Do not use A03's minpoly annotations for anything.

## Composition (stated precisely — which root and why)

G_j(P̂) = 0 (A22 structure + rows vanish at ẑ); t̂ ∈ [3/10, 2/5] (θ̂ enclosure +
elementary tan bounds); identity at P̂ + sign gate ⟹ octic(ŝ_A22) = 0; A22's 1e-50
enclosure puts ŝ_A22 in (3.877083, 3.877084) with 4.1e-7 clearance, where the octic
has exactly one root (`shat_spec`/T1; two real roots total, the other in (−2,−1)):
ŝ_A22 = ŝ = the SECOND real root. TCB: verify_sturm-class (stdlib) + the A22
certificate (mpmath.iv) — no new trust items.

## [C] CIDL-LEAN (named obligation; the only residue of `shatA22_eq_shat`)

(i) native_decide replay of [O]/[I]/[G] (A64 Measure382Check isolation pattern +
cross-toolchain recipe); (ii) replace the opaque `shatA22` axiom pair by axioms
carrying A22's certified content (∃ point: G_j = 0, t̂ ∈ [3/10,2/5], ŝ_A22 ∈
[3.877083, 3.877084], CfgPacking) — then `shatA22_eq_shat` becomes a theorem via
`shat_spec`. Pure engineering, no new mathematics. TopLevel docstring updated to
point here; axiom count unchanged.

## [E] Engineering notes

* `assemble.py` is the operative search script (pure Python fractions +
  interpolation for adjugate/Cramer data; verifies the identity with the checker's
  own machinery before writing the cert). `derive.py` = phase-1 reduction (sympy,
  cheap). `eliminate.py`/`build_cert.py` are the first sympy-Expr attempts: they
  reached deg Δ = 34 / m(t) / deg e = 27 but Expr-level expansion of G_oct blew past
  10 GB RSS and both were killed — **sympy Expr is the wrong tool above degree ~100;
  plain Fraction coefficient lists are ~1000× leaner.** Poly-interpolation with a
  degree-clip guard (verify at an extra point) replaced adjugate symbolics.
* INCIDENT (logged for the PI): during the memory spike, commit headroom dropped to
  0.49 GB and, while triaging, PID 24700 (a ~50 MB transient python, most likely a
  campaign certify worker) was force-killed by mistake before the real culprits
  (the two A69 sympy processes) were identified and killed. A57/A60/A61 main
  processes verified alive afterwards; campaign schedulers requeue killed certify
  workers, but flagging it honestly in LOG.md.
* Checker cost: PASS 0.7 s. Corruption gates: `--corrupt qcoeff|e|rowspec|octic`,
  exits 1 (gate `rowspec` proves the checker really rebuilds the generators itself).
