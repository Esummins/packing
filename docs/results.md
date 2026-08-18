# Results (as of 2026-08-18)

Notation: s(n) = side of the smallest square containing n unit squares with disjoint interiors
(rotations allowed). Everything below refers to n = 11 unless stated.

## Headline

| | before this project | now | status |
|---|---|---|---|
| lower bound | 2 + 2√(4/5) = 3.788854… (Stromquist 2003) | **s(11) ≥ 3.80** (certificate `certs/measure_certificate_3.80.json`) | computer-verified by two independent exact verifiers (A07 float-interval, A08 exact-integer) + Lean checker (A06, in progress: see `lean/README.md`) |
| upper bound | 3.877083590022814… (Trump 1979) | unchanged; now backed by exact rational certificates and an axiom-free Lean kernel proof of the checker (`lean/PackingCert`) | done |
| method ceiling | — | the pure measure/LP method (Theorem 1) cannot exceed ≈ 3.83: τ*(3.83) = 11.000, τ*(3.84) = 11.02 (numerical LP) | see A07 |

The gap 3.80 ≤ s(11) ≤ 3.877084 remains open; the lab did **not** close it. What changed is the lower
bound (+0.011 over a 23-year-old bound, with a possibly larger certified value at 3.82 pending) and the
existence of a machine-checkable, extensible method with a known ceiling and a clear next step (I-L6).

## Theorem 1 (measure / fractional-cover bound)

Let s > 0 and let μ = Σᵢ wᵢ δ_{pᵢ} be a finite non-negative atomic measure on the closed square [0,s]².
Suppose
 (a) μ([0,s]²) = Σ wᵢ < n, and
 (b) every closed unit square Q ⊂ [0,s]² (any orientation) satisfies μ(Q) ≥ 1.
Then s(n) ≥ s.

Proof. Suppose n unit squares with pairwise disjoint interiors fit in a square of side s' < s.
Scale everything by λ = s/s' > 1: the container becomes [0,s]² and the squares become λ-squares
(side λ > 1) with pairwise disjoint interiors. Shrink each λ-square about its centre to a unit square.
A concentric unit square lies in the interior of its λ-square, so the n unit squares are pairwise
disjoint *closed* sets contained in [0,s]². By (b) each has μ-mass ≥ 1, and by disjointness
μ([0,s]²) ≥ n, contradicting (a). Hence no packing exists in any side s' < s, i.e. s(n) ≥ s. ∎

Remarks. (i) Point sets ("unavoidable sets", Friedman DS7 §5) are the case wᵢ = 1, and the bound is
then n−1 points; fractional weights are strictly more powerful (A05: 10 points top out at ≈ 3.7505;
the measure of the 3.80 certificate has 1069 atoms with weights between 3.3e-5 and 0.07 and total 10.80).
(ii) Kearney–Shiu's "duality" proof of s(6) = 3 is a special case with two point sets of weight 1/2… in
spirit; the general LP formulation appears to be new (A01 found no LP/measure bound for finite square
containers in the literature).
(iii) The dual LP is the fractional packing number ν*(s); the largest s with τ*(s) := min μ < n is the
ceiling of every argument of this type. For n = 10 the LP reproduces Stromquist's exact value:
τ*(3.7071) = 10.000.

## Verification of hypothesis (b)

Parametrise placements by centre c = (cx, cy) and t = tan(θ/2) ∈ [0,1] (θ ∈ [0, π/2] suffices because
Q(c,θ) = Q(c,θ+π/2)); cos θ = (1−t²)/(1+t²) is decreasing and sin θ = 2t/(1+t²) increasing on [0,1], so
on a t-interval the enclosures of cos and sin are exact rationals. Q(c,θ) ⊂ [0,s]² ⟺ w/2 ≤ cx, cy ≤ s−w/2
with w = cos θ + sin θ; p ∈ Q(c,θ) ⟺ |cosθ(px−cx)+sinθ(py−cy)| ≤ ½ ∧ |−sinθ(px−cx)+cosθ(py−cy)| ≤ ½.
A box of parameters is discharged when the exact sum of weights of atoms provably inside Q for *all*
parameters of the box is ≥ 1 (or the box contains no admissible placement); otherwise it is bisected.
This is a finite, exact-arithmetic computation. Two independent implementations
(`certs/verify_measure.py`, exact integers; A07's float-interval verifier with outward rounding) both
PASS on `certs/measure_certificate_3.80.json`: 5,836,650 boxes, max depth 45, ~50 s on 6 processes.
The advisor's own float spot-check (200k random + adversarial placements) gives min mass 1.0300 (the
certificate carries a 3% robustness margin).

Lean 4: `lean/PackingCert` contains a decidable checker with the same semantics (`checkMeasure`,
Rat) which already proves A05's 10-point certificate at 3.741594 by `native_decide`; the run on the
3.80 certificate is in progress (see `lean/README.md` for the current theorem list). Not formalised:
the bridge lemma "checker = true ⇒ hypothesis (b)" and Theorem 1 itself (Mathlib was not installable on
this machine for disk reasons; estimated 3–5 days of work).

## Upper bound artefacts

- `certs/trump11_certificate.json` (s_c = 3877084/10⁶) and `_tight.json` (s_c = s* + 1e-9): 11 squares
  with rational centres and rational tan(θ/2) (so all corners are rational), verified by
  `certs/verify_certificate.py` (stdlib Fraction: containment + separating axis with strictly positive
  margins). Integer-corner versions `_int.json` feed Lean.
- Lean: `PackingCert.trump11_ok`, `trump11_ok_kernel` (plain kernel `decide`, `#print axioms` = none),
  same for the tight certificate. Bridge lemma (separating axis ⇒ disjoint convex hulls) not formalised.
- Exact algebra (A03, 60 digits; consistent with Ellsworth 2023 and Gensane–Ryckelynck 2005): s is the
  second real root of s⁸ − 20s⁷ + 178s⁶ − 842s⁵ + 1923s⁴ − 496s³ − 6754s² + 12420s − 6865;
  θ = 40.18193729032971646523…°; the contact system is rigid (rank 33/33).

## Negative / structural results (all documented in attempts/)

- A04: no packing below s* found (2488 local optima, Trump's basin hit 416×; 32 structural families < 3.95).
- A05: pure 10-point unavoidable sets reach at most ≈ 3.7505; the deficit is entirely at the walls.
- A02: Stromquist's proof reconstructed; two small errata (a spurious table root, and a 1e-4 hole left by
  the literal Fig. 14 point G, repaired by G' = (.78, 1.845)); the theorem stands.
- A07: τ*(s) curve for n = 10, 11 (see `attempts/A07-lp-dual/notes.md`, `plots/tau_vs_s.png`).

## Next steps (ordered)

1. Certify s = 3.82 (τ* = 10.716 there) — in progress.
2. I-L6 "case-LP": LP-based branch and bound over the packing structure (case splits on wall regions à la
   Stromquist, each branch an LP with modified right-hand sides). This is the only identified route past
   the pure-LP ceiling ≈ 3.83.
3. Formalise the bridge lemmas in Lean/Mathlib (needs ~10 GB disk).
