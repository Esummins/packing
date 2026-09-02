# rigidity-krawczyk-certificate-v1 (A22, extended by A36) — frozen spec (A62, checklist C2)

**Certificate:** `attempts/A22-local-rigidity/results/krawczyk_cert.json`.
**Verifier:** `attempts/A22-local-rigidity/recheck.py` (432 lines), standalone: `mpmath.iv`
validated interval arithmetic + `fractions` only; corruption modes `z0-big / z0-small / mu /
spec` must each FAIL.
**Extension:** A36's composed theorem (radius 3.7e-3, ×7.5 the A22 box) is the same
certificate class with the max-form-pinned universal certificate; its re-checker is
`attempts/A36-levers/code/a36_check.py` (566 lines) with 17 IV certificates, 339 checks,
5 corruption gates. This spec covers the A22 v1 object; A36's additions are the same fields
at different constants plus the branch/variant machinery frozen in
`atlas_value_certificate_v1.md` §3 (the A37 checker re-implements it).
**Status:** written from behaviour + code at commit `c9980bf` (2026-09-01) by A62.

## 1. The mathematical claim a PASS establishes

With z0 the 60-digit floating centre (34 coordinates: 11 × (cx, cy, θ) + s, **θ raw
angles** — coordinate caveat as in the atlas spec §5), r_N = 5e-4, r_0 = 1e-50-scale:

> **(existence/uniqueness)** the curated 34-row contact system F = (g_k)_{k∈S} has EXACTLY
> ONE zero ẑ in the ∞-norm box N = box(z0, r_N), and ‖ẑ − z0‖_∞ ≤ r_0;
> **(feasibility)** ẑ is a valid packing configuration (contact pairs touch exactly with
> interiors disjoint; non-contact pairs strictly separated; containment strict off-wall);
> **(local optimality)** every valid packing configuration z with ‖z − z0‖_∞ ≤ r_N has
> s(z) ≥ s(ẑ), with equality iff z = ẑ.

s(ẑ) = ŝ, the octic root, is **identified numerically to 1e-50** (octic residual ±3.1e-45)
but not symbolically — tying ẑ to the algebraic number is checklist S3, still open.

**Load-bearing note (A62):** this certificate is also the natural carrier of the
**upper-bound-at-ŝ obligation** surfaced by the formal statement (TopLevel.lean axiom
`trump_packs_at_shat`, findings F2): the existence + feasibility halves prove Trump's
packing exists AT ŝ exactly, which no `checkPacking`-family certificate can ever do
(strict margins required there).

## 2. Certificate fields

| field | meaning |
|---|---|
| `variables`, `description` | documentation of the 34-coordinate order |
| `z0` | centre (34 rationals, 60-digit) |
| `r_N`, `r_0` | box radii (rational strings) |
| `S`, `Y` | curated active row set (38 rows → rank-34 subsystem) and the Krawczyk preconditioner; `S2`, `Y2` the angle-equality variant F~ (equal-tilt structure of ẑ) |
| `lambda` | exact multipliers on S (min 0.01754: strict complementarity) |
| `constraints`, `contact_edge_pairs`, `flush_*_pairs`, `noncontact_pairs` | the row language: wall rows, corner-on-edge rows, flush pairs, and the pairs that must stay separated |
| `certificates` | 68 rational positive-spanning (Farkas) certificates: σ·e_i = Σ μ ∇g − ν ∇s with residual interval ρ over N, ‖ρ‖₁ ≤ β_max < 1 |
| `claims` | the numeric bounds the checker verifies against (centre residual, contraction ratios, β_max, ν_max, margins) |
| `exact_rows_sanity` | spot identities tying the row evaluations to exact rational reconstructions |

## 3. What the re-checker verifies (normative)

**[G]** centre residuals |g_k(z0)| within claim; **[K]** Krawczyk operator K(N) strictly
inside N (⇒ exactly one zero in N); **[K0]** same on box(z0, r_0); **[V]** validity margins
of every edge constraint over N (|tangential| ≤ ½ − margin, depth > −½); **[E]** multiplier
identity ‖A_Sᵀλ − e_s‖_∞ within claim; **[B]** all 68 Farkas certificates: ρ-interval
‖ρ‖₁ ≤ β_max < 1, μ ≥ 0, ν ∈ [0, ν_max]; **[F]** feasibility of ẑ (interval SAT for
non-contact pairs; contact pairs: the touching corner realises the strict minimum projection
on the contact axis, so the SAT gap is exactly g_k(ẑ) = 0 ⇒ interiors disjoint; strict
containment for non-wall corners). The four-line composition of [G]–[F] into the claim of
§1 is prose in A22's `notes.md`.

**Trust base:** `mpmath.iv` (cited). No Lean replay exists: blocked on interval
trigonometry because θ is stored as raw angles; re-emitting in t = tan(θ/2) makes every row
rational and a `checkKrawczyk` in `MeasureInt.lean` style a direct port (A28 §4 — checklist
F6, and the same re-emission the composition needs for coordinate consistency, findings F5).

## 4. Settings that MUST appear in a PASS record (C7)

Interval precision (mpmath dps), the box radii r_N / r_0 as checked, β_max, min multiplier,
min inactive margin, and the corruption-gate results (all four must FAIL). A22's
`results/` records these.

## 5. Known caveats

* **Basis completeness:** A35 found the A22 basis misses the exact (1,3) corner-corner
  contact and models two flush contacts by distance surrogates; A22's value theorem is
  unharmed (optimality over a superset of configurations), and the repaired 42-row basis
  is what A36 certifies. Cite A36's composed theorem, not A22's box, in the composition.
* **D4×S11 bookkeeping** around the box is stated, not formalised (checklist H12).
* Single implementation of the re-checker; `a36_check.py`/`a37_check.py` are descendants,
  not independent (C3 applies to this family too).

## 6. Erratum / status update (A79, 2026-09-02)

* Section 3's "No Lean replay exists: blocked on interval trigonometry ... re-emitting in
  `t = tan(theta/2)`" is superseded: the certificate IS replayed in Lean in the THETA frame
  (`lean/PackingCertMathlib/PackingCertMathlib/RigidKernel.lean`, `RigidityCheck.lean`,
  `native_decide`), with cos/sin enclosed by certified alternating-Taylor brackets; no
  `t` re-emission was needed (A70 rung (a) already found this at the Python tier).
* The trust base is no longer `mpmath.iv` at either tier: A70's `a22_recheck_exact.py`
  (stdlib rationals) is the second implementation (C3), and the Lean checker + soundness
  theorems (`krawczyk_sound`, `zhatV_feas`, `a22_optimal`) are the primary.
* Finding: the [F] check of section 3 is not self-contained — the recheck skips the three
  wall rows dropped from `S` and the flush pairs ("exact by inspection", notes.md sections
  3-4).  The Lean port makes the exact-structure argument explicit and shows it is derivable
  from `S` alone (mate wall rows => theta = 0; corner-on-edge / edge-on-corner pairs with
  parallel body normals => equal tilts, using the [V] tangential margin; row transfer across
  a corner; an affine known-centre inference over the dist rows for the flush-upright
  block).  The second system `S2` ([K~]) is replayed but is NOT load-bearing.
* Quantities the recheckers evaluate AT `z0` (`eps_0`, `g_max`, `eps_w`, row activity) are
  evaluated over `box(z0, r_0)` in Lean (the theorem is about z-hat); the float `claims`
  for those are therefore not reproduced (harmless: `x* + r_0 <= r_N` by 46 orders).
