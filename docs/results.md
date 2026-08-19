# Results (as of 2026-08-18)

Notation: s(n) = side of the smallest square containing n unit squares with disjoint interiors
(rotations allowed). Everything below refers to n = 11 unless stated.

## Headline

| | before this project | now | status |
|---|---|---|---|
| lower bound | 2 + 2√(4/5) = 3.788854… (Stromquist 2003) | **s(11) ≥ 3.82** (certificates `certs/measure_certificate_3.80/3.81/3.82.json`) | each PASSES two independent exact verifiers (A07 float-interval B&B, A08 exact-integer B&B) and the advisor's re-runs; Lean 4 theorems `s11_ge_3_80`, `s11_ge_3_81`, `s11_ge_3_82` (`checkMeasureI cert = true` by `native_decide`, only the native_decide axiom) — see `lean/README.md` |
| upper bound | 3.877083590022814… (Trump 1979) | unchanged; now backed by exact rational certificates and an axiom-free Lean kernel proof of the checker (`lean/PackingCert`) | done |
| method ceiling | — | the pure measure/LP method (Theorem 1) cannot exceed ≈ 3.83: τ*(3.83) = 11.000, τ*(3.84) = 11.02 (numerical LP) | see A07 |

The gap 3.82 ≤ s(11) ≤ 3.877084 remains open; the lab did **not** close it. What changed is the lower
bound (+0.031 over a 23-year-old bound; the gap shrank from 0.088 to 0.057) and the existence of a
machine-checkable, extensible method with a known ceiling (≈ 3.83) and a clear next step (I-L6).

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

Certificates: 3.80 (1069 atoms, mass 10.801639; 5.84M boxes), 3.81 (980 atoms, 10.9852; 5.12M boxes),
3.82 (1769 atoms, 10.985474; 7.64M boxes). Each was built by the LP + rigorous-separation loop
(verifier witnesses fed back as LP rows) and carries a 2.5–4% weight margin.

Lean 4: `lean/PackingCert` contains decidable checkers with the same semantics (`checkMeasure` over Rat,
`checkMeasureI` over scaled Int); theorems `PackingCert.MeasureI.s11_ge_3_80`, `s11_ge_3_81`,
`s11_ge_3_82` (`lake build PackingCertSlow`, `PackingCertSlow381`, `PackingCertSlow382`; 11–15 min each,
`#print axioms` = the native_decide axiom only). Kernel `decide` works for the Int checker on small
certificates (Göbel, no axioms) but not at 5–8M boxes. Not formalised:
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


## Ab-initio discovery (A09, 2026-08-18)

At fixed orientations the packing problem is a disjunctive LP, so for a finite angle set Θ the optimum
over packings with angles in Θ is a MILP (`attempts/A09-angle-lattice-milp/milp_pack.py`, CP-SAT/HiGHS).
Calibration is exact: Θ={0°,45°} gives Göbel's 2.7071 (n=5), Stromquist's 3.7071 (n=10, proven optimal by
CP-SAT in 535 s) and Stromquist's Theorem 3 value 3.8856180832 (n=11). **Ab initio:** Θ={0°,θ*} recovers
Trump's packing (s = 3.8770835900228144, 6 uprights + 5 tilted) in 23–39 s with no contact graph given; the
coarse lattice {0°,30°,35°,40°,45°} finds the same structure at 40° (s = 3.87764). So "coarse angle lattice
→ MILP → contact-graph Newton polish (A03)" is a working ab-initio pipeline. **It is not a certifier:** the
LP relaxation of the big-M disjunctions is void, so solver lower bounds sit at √n; the viable rigorous
route is the angle-box branch-and-bound whose box killer is Theorem 1 restricted to the box's orientations
(Stromquist's 0°/45° theorem is its two-point case) — see `docs/ideas.md` I-U4/I-L7.


## Angle-box sizing, ab-initio sweep, and cut pilots (A10–A12, 2026-08-18)

- **A10 (orientation-restricted LP).** Restricting Theorem 1's coverage rows to orientations in a box Θ_B kills
  the box for all packings whose 11 orientations lie in Θ_B. Sanity: {0°} → crossing exactly at 4; {0°,45°} → (3.885, 3.886]
  = Stromquist's 2+4√2/3. Trump box [0,δ]∪[θ*±δ]: crossing s_B(δ) with s* − s_B(δ) ≈ 0.006·δ (δ=1°: 3.874; δ=2°: 3.865;
  δ=5°: 3.85) — the restricted LP is tight at the optimum as δ→0; a rigorous restricted certificate proves that no
  packing with all orientations in [0°,2°]∪[38.2°,42.2°] has side ≤ 3.85. But boxes "uprights + one tilt in ≈[20°,36°]"
  stay at τ = 11.000 exactly at 3.85–3.87 down to half-width 0.5°, via 4-fold ¼/½-weight fractional structures
  (no packing exists there below 3.89): pure angle-box B&B is not viable (≥10⁶ boxes).
- **A11 (ab-initio sweep, all open n ≤ 100).** The angle-lattice MILP + LP polish rediscovers the n=11 and n=18
  records exactly (rational certificates PASS) but beats nothing; competitive only for n ≲ 20, |Θ| ≤ 3, small tilted
  clusters; CP-SAT stays in the grid basin for n ≥ 26.
- **A12 (region-rank cuts, I-L8).** Cannot kill the mid-tilt cheat: its fractional packing is locally integral
  (corners 1, side zones 4×¼, interior 8 tilted ¼ + 4 upright ¼); every macroscopic region is realisable, and an
  LP-certified k(R) never yields a violated cut (lemma). What kills it is a CONDITIONAL LP: corners fixed + side zones
  empty ⇒ τ = 5 < 7. ⇒ the viable route is the case-LP branch-and-bound (I-L6), piloted as A13.

## Next steps (ordered)

1. (done) s = 3.82 certified. Pushing to 3.83 is not possible with the pure measure method (τ*(3.83) = 11.000).
2. I-L6 "case-LP": LP-based branch and bound over the packing structure (case splits on wall regions à la
   Stromquist, each branch an LP with modified right-hand sides). This is the only identified route past
   the pure-LP ceiling ≈ 3.83.
3. Angle-box B&B with the orientation-restricted measure LP as box killer (first experiment: A07's LP with θ
   restricted to [θ*−δ, θ*+δ] ∪ {0} for δ = 10°, 5°, 2°, to see where τ*_B(3.877) crosses 11).
4. Formalise the bridge lemmas in Lean/Mathlib (needs ~10 GB disk).
