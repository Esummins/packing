# Results (as of 2026-08-19)

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
- **Local optimality (A22)**: certified strict local optimality — in the box
  ||z − z₀||∞ ≤ 5·10⁻⁴ around the Trump configuration every feasible packing has s ≥ ŝ,
  equality only at the unique contact solution ẑ (Krawczyk + 68 rational Farkas certificates,
  standalone interval re-checker `attempts/A22-local-rigidity/recheck.py`); stability:
  s ≤ ŝ+δ ⇒ ||z−ẑ||∞ ≤ 155.7 δ.
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


## Case-LP branch-and-bound at 3.84 (A13–A14, 2026-08-18)

- **A13** built the rigorous case-LP machinery (I-L6: hypotheses = core boxes "some square has (centre,θ) in B" with a rational
  inner square, and NO-families "no square centred in zone Z"; node LP = Theorem 1 with the exempt placements removed; exact
  verifier with exempt tests) and ran a wall-first tree at s = 3.84 (root τ = 11.03).
- **A14** (attempts/A14-close-tree-384) found and fixed three blind spots of the exact row oracle used since A10 at hypothesis
  nodes (the lowest-cell cap was applied before the hypothesis filter; cells at the admissible-domain boundary were never
  sampled; cap exhaustion at unconverged nodes) — every LP value A10–A13 reported at a hypothesis node is an under-estimate.
  With the fixed oracle: the three "undecided" on-corner boxes at 3.84 are ALIVE (τ ≈ 10.11–10.19 vs budget 10), and the LP
  with one corner square fixed EXACTLY has τ = 10.000 with a fractional packing of coverage exactly 1 (τ = 7.000 = budget with
  all four corners fixed): corner refinement can never kill them; killing power sits only in empty side zones (4 corners +
  no square in side zone 0: 6.36 < 7; + all four side zones empty: ≈ 4.3; root + all side zones empty: 8.28 < 11). One more
  corner level: 9 of 12 boxes survive per level with slack growing (+0.13…+0.54). Certification overhead (3e-3 shrink + 3 %)
  costs 0.1–0.25 per node. Verdict: closing the tree at 3.84 needs 10⁵–10⁶ node LPs — not viable; the case-LP line is stopped.
- **Certified (exact verifier PASS, `attempts/A14-close-tree-384/certs_wip/leaf_NO_corners.json`, total 10.117 < 11):**
  every packing of 11 unit squares in a square of side ≤ 3.84 has a square whose centre lies within 0.6 of a corner of the
  admissible centre square, i.e. in [0.5,1.1]² up to symmetry (Lemma; a Stromquist-style wall lemma obtained by LP). A second
  leaf is certified too (no square with centre in [0.8,1.1]² and orientation in [60°,90°], total 9.9755 < 10); the other ten
  first-level leaves are not certifiable (three are provably alive).


## ϑ′ (Lovász–Schrijver) vs the point-clique LP on a discretised placement graph (A15, 2026-08-19)

- **Question (I-L9).** On one finite placement graph G (grid of (cx,cy,θ), edges = interior overlap, the A12 ¼-structure
  placements injected so that the grid LP shows the cheat), is Schrijver's ϑ′(G) meaningfully below the point-clique LP ν*_G?
  (α ≤ ϑ′ ≤ χ̄_f ≤ ν*_G on the same graph; ϑ′ sees odd cycles.)  A finite induced subgraph says NOTHING about s(11) — this is a
  comparison of relaxations only.
- **Answer: yes.**  Same graph, N ≈ 2150–2340 (h = 0.2, Δθ = 10°, or mid-tilt {0°}∪[30°,36°]):
  s = 3.80: LP 10.000, ϑ′ 10.000, α 10 | s = 3.84: LP 11.000, **ϑ′ ∈ [10.376, 10.392]**, α 10 | s = 3.85: LP 11.000,
  **ϑ′ ∈ [10.43, 10.48]** (mid-tilt graph [10.41, 10.48]; refined N = 3750: [10.40, 10.74]), α 10 | s = 3.87: LP 11.000, ϑ′ ∈ [10.45, 10.64], α 10.
  On the A12 ¼-structure support alone ϑ′ = α (10 / 10 / 9) while the LP is 10.5–10.9.  So ϑ′ removes about half of the LP's
  integrality gap on the discretisation that carries the ¼-cheat, and the gap does not shrink between N = 2229 and N = 3750;
  ϑ′ is still ≈ 0.4 above α (rank-150 optimum: corners 0.93, eight side uprights 0.37, interior 2.5).
- **Machinery.** D4 block-diagonalised SDP (5 PSD blocks ≈ N/8,…,N/4, one constraint per pair orbit) in SCS with certified
  brackets (dual certificate Z ⪰ 0 ⇒ upper bound; primal-feasible B ⇒ lower bound; exact ϑ′ on the 400–520-node support subgraph).
  SCS needs ≳ 3·10⁴ iterations at N ≈ 2200 (0.25 s each): a better SDP solver / lazy pair constraints are needed to scale to 10⁴ nodes.
- **Consequence for the lower-bound programme.** The LP certificate is itself a kernel certificate with coverage-indicator features
  (φ(x) = (1, 1[p∈Q(x)]/μ(Q(x))), M = Σ_p μ_p (τe_p − e_0)(τe_p − e_0)ᵀ/τ ⪰ 0 gives K = −1 on disjoint pairs, K(x,x) ≤ τ−1), so the
  continuous ϑ′-kernel certificate of I-L9 should be built on "LP atoms + cross terms" (then a smooth basis), verified by the A08-style
  box B&B (K is piecewise constant in the atom-arrangement cells).  Recommended next experiments: ϑ′ on an un-seeded refined grid at
  3.85–3.87, and ϑ′ as the node relaxation inside the A13/A14 case tree (LP = 7.000 = budget with four corners fixed — is ϑ′ < 7?).

## ϑ′ as the node certificate of the case tree (A16, 2026-08-19)

- **Question.** A14 showed the case-LP tree cannot close at 3.84: with corner squares fixed the LP sits exactly at the
  budget (one corner: 10.000 = 10; four corners: 7.000 = 7) and killing power exists only in empty side zones (depth ≥ 6,
  10⁵–10⁶ nodes).  Does ϑ′ (A15) kill exactly those nodes?  Test (`attempts/A16-theta-casetree`): per hypothesis node H one
  finite placement graph (seeded grid h = 0.2, Δθ = 10°; nodes = placements admissible under H with A14's exact exemption
  semantics; budget = 11 − #cores), compare ν*_H (point-clique LP), ϑ′(G_H) (SDP block-diagonalised for the stabiliser of
  the admissible set — D4, Z2 or C1 — with certified dual-certificate upper bounds and support-sub-SDP lower bounds) and
  α(G_H).  Comparison of relaxations on finite induced subgraphs — NOT a bound on s(11) (ϑ′_G ≤ ϑ′_cont).  Un-seeded grids
  (h down to 0.1) are integral (LP = α = 10): no information; seeding as in A15 is what makes the LP show its cheat.
- **Answer: ϑ′ kills every node type the LP cannot.**  Certified ϑ′ upper bounds (tight support values in parens), s = 3.84 / 3.85 / 3.87:
  one corner fixed exactly: LP 10.000 = budget, **ϑ′ ≤ 9.44 / 9.49 / 9.48 (9.38–9.45)**, α = 9; four corners fixed exactly (THE
  stalling node): LP 7.000 = budget, **ϑ′ ≤ 6.62 / 6.59 / 6.51 (6.25–6.46)**, α = 6 — stable under grid refinement (N 2177 → 3152:
  tight 6.44); A14's three alive on-corner boxes: LP 10.03–10.05 grid (10.11–10.19 continuum), **ϑ′ ≤ 9.61–9.67 / 9.52–9.64
  (tight 9.44–9.46)**, α = 9 — richer seeding raises the LP (10.08) but not ϑ′; A14's uncertifiable off-corner boxes (nodes 5, 6):
  LP 9.76 / 9.32, **ϑ′ ≤ 9.41 / 9.14**; four corners + NO side0: LP 6.25–6.33, **ϑ′ = α = 6.000 exactly** (integral).  Pattern on every
  node graph: α = budget − 1, LP = budget, ϑ′ ≈ α + 0.4…0.6 — the same split as A15's root (10 / 10.4 / 11).
- **Consequence.**  With ϑ′ as node certificate A14's whole first level at 3.84/3.85 is dead on the grids by 0.24–1.0 (honest
  continuum estimate 0.2–0.45, since the grid LP under-shoots the continuum LP by 0.06–0.15 at the N3 boxes): the tree is
  **root + 13 leaves, not 10⁵–10⁶ nodes** — and the root itself (A15: ϑ′ ≈ 10.38–10.64 < 11 up to 3.87) may need no tree at all.
  Cost: 40–60 min per node (SCS; the dual certificate is accurate after ~2000 iterations even where the primal is useless);
  the open risk is that grid ϑ′ only lower-bounds continuum ϑ′ (no upward drift seen under refinement or richer seeding).
  Rigorous version = per-node kernel certificate (I-L9 continuous ϑ′): K PSD, K(x,x) ≤ λ−1 on non-exempt placements,
  K(x,y) ≤ −1 on disjoint non-exempt pairs ⇒ budget ≤ λ; LP-atom indicator features + cross terms (node duals have 30–45
  eigenvalues > 1%), verification = verify_case.py-style cell B&B + pairwise cell table (piecewise-constant kernel), exact
  PSD by rational LDLᵀ; estimate 4–6 weeks to a first certified node (A16 notes §3(e)).  **Recommendation: build the
  continuum ϑ′ kernel certificate at the root first (target: λ < 11 at 3.84); fall back to the 14-node ϑ′ tree only if the
  root kernel stalls above 11.**

## The continuum ϑ′-kernel at the root, float phase (A17, 2026-08-19)

- **Goal.** The I-L9 kernel certificate at the root: φ(x) = (1, 1[p∈Q(x)]/m(x)) over an LP atom set, M ⪰ 0 D4-invariant,
  K = φᵀMφ with K(x,x) ≤ λ−1 on P_s and K(x,y) ≤ −1 on disjoint pairs ⇒ s(11) ≥ s if λ < 11; target λ < 11 at 3.84,
  float cutting-plane phase (exact phase = A18).  Calibration at 3.80 PASSES (the LP certificate is reproduced as a kernel:
  pair oracle −1.000000000 exactly, min coverage 1.0297 vs the advisor's 1.0300).
- **Result: λ < 11 NOT reached in the 1181-atom indicator class** (A07's 3.84 LP atoms). The cutting-plane loop (13
  iterations, 8044 rows, Burer–Monteiro block SDP validated vs Clarabel) stalls at λ_sdp ≈ 11.05–11.13: the diagonal is
  pinned by a continuum of coverage-1 cells (corr(K(x,x), τ/m(x)) = 0.99) and the pair oracle finds a non-converging
  stream of interior mid-tilt (29–68°) barely-disjoint violations — the ¼-structure region. Honest class estimate
  ≈ 11.0–11.2, i.e. ≈ +0.7 above the discrete ϑ′ (10.38): **A16's risk R2 (feature class too short) binds before R1
  (grid→continuum)**. The kernel does beat the pure LP form on the same atoms by ≈ 1.25 (12.38 → ~11.1).
- **Two structural discoveries.** (1) Bridge bookkeeping: condition (ii) is needed only for pairs of disjoint CLOSED
  squares — touching pairs are exempt, and must be (a touching pair can share a boundary atom, forcing K > −1).
  (2) The subclass M = LP-form + C with C ≤ 0 off-diagonal satisfies (ii) for EVERY disjoint pair by pure algebra
  (strictly disjoint closed squares share no atom), eliminating the 6-D pair verification entirely: the rigorous
  certificate reduces to rational LDLᵀ + one verify_measure-style 3-D cell B&B with a quadratic form. On the A15 c384
  graph, 80 % of edges share an atom and deleting the 220k non-sharing edges leaves α = 10 unchanged — the restriction
  is not obviously lossy.  Recommended A18: restricted class + atoms placed inside the mid-tilt sliver-overlap regions
  (the non-sharing edges say where) + ~40 smooth D4 features interpolating the discrete duals' dominant eigenvectors.

## The restricted-kernel collapse is now fully rigorous at 3.84, and the hybrid escape fails (A18–A19, 2026-08-19)

- **A18 (theorem)**: every kernel whose pair condition is discharged by a sign/pointwise argument (the automatic-(ii)
  class and all its no-pair-verification variants) collapses to a two-measure LP-form kernel with λ ≥ τ*(s).
- **A19 (exact certificate)**: **τ*(3.84) ≥ 11 is now PROVED** — `attempts/A19-hybrid-kernel/lp_floor_384.json` holds 18
  closed unit squares (rational centres, exactly-rational directions, weights 4×1 + 14×½ summing to exactly 11) whose
  pointwise closed-cover ≤ 1 is verified by an exact Fraction B&B (10,009 boxes, 0 undecided); weak duality gives
  τ*(3.84) ≥ 11, hence **λ ≥ 11 at 3.84 for the whole automatic class, rigorously** (the ceiling ≈ 3.83 statement no
  longer rests on a float LP).
- **A19 (hybrid, done-negative)**: the one escape A18 left open — unrestricted D_pq on atom pairs inside a region R,
  with (ii)-verification localised to R-meeting pairs (measured: 9.9 % of disjoint pairs at 3.84 with a 148-atom
  central R) — buys ≈ 0.002–0.005 in λ over the automatic class on identical row sets at BOTH 3.80 and 3.84
  (11.14579 vs 11.14406 at 3.84; 10.50369 vs 10.50615 at 3.80, vs the 0.086 needed to reach τ*(3.80)): the LP's tight
  set is a coverage-1 continuum spanning the whole container, so a small R-patch is always re-pinned from outside, and
  covering the whole tight set (k ~ 600+) exceeds the convex (k+1)-cone form's reach (Clarabel memory wall ≈ cone 250).
  An exact-finite-graph diagnostic suggests the 1181-atom indicator basis itself is NOT the obstruction (pattern class
  ≈ 10.35–10.4 on the c384 graph where ϑ′ = 10.38). Remaining kernel moves: D4-block-diagonalised R-cone (k → ~600),
  Burer–Monteiro with sign hinges, or smooth non-indicator features. Details: attempts/A19-hybrid-kernel/notes.md.


## The ϑ′/kernel programme (A15–A20, 2026-08-19): conclusion

Discrete phase (A15–A16): on finite placement graphs, Schrijver's ϑ′ removes about half of the LP's integrality
gap (10.38–10.48 vs LP 11.000 vs α 10 at 3.84–3.85) and kills every hypothesis node that stalls the case-LP tree
(four-corners-fixed: ϑ′ ≤ 6.6 vs budget 7). Continuum phase (A17–A20): the kernel-certificate form of ϑ′ does NOT
reach λ < 11 at 3.84. A17: the LP-atom indicator class stalls at ≈ 11.0–11.2. A18 (theorem, machine-validated):
every kernel class with automatic pair constraints collapses to the LP floor λ ≥ τ*(s); and A19 made that floor
rigorous at 3.84 (exact rational fractional packing of value exactly 11, exact Fraction B&B PASS ⇒ τ*(3.84) ≥ 11).
A19–A20: the hybrid class (localised pair verification) buys ≤ 0.001 at 3.80 and +0.058 at 3.84 over the automatic
class — far short — because the 6-D pair CONTINUUM re-pins every finite kernel: each finite pair-row set leaves
near-tangent mid-tilt cells open, the optimum exploits them, the oracle closes them, λ climbs back (verified with
an exact-feasibility-checked convex solver at k = 480 in D4-isotypic blocks; a silent Clarabel stall in A19's h380
number was found and corrected). The grid→continuum gap (risk R1) is real: graph-ϑ′ ≈ 10.4 does not transfer.
Untested residue: smooth feature classes that change what the pair oracle can find (piecewise-smooth pair bounds),
rather than only enriching the diagonal. Certified bounds unchanged: 3.82 ≤ s(11) ≤ 3.877084.


## The optimality programme (A21–A23, 2026-08-19/20)

Pivot (PI): fixed-s certificates below s' are vacuous if Trump is optimal; optimality statements must live at s'
or above. Three legs, all delivered:
- **A22 (LOCAL, certified):** strict local optimality of Trump's packing — in the box ‖z−z₀‖∞ ≤ 5·10⁻⁴ (34 coords)
  the contact system has a unique solution ẑ (Krawczyk, enclosure 10⁻⁵⁰), ẑ is feasible, and every feasible
  configuration in the box has s ≥ ŝ with equality iff ẑ; stability ‖z−ẑ‖∞ ≤ 155.7·(s−ŝ). Min KKT multiplier
  0.0175 (strict complementarity; one pinwheel self-stress), min inactive margin 0.019. All-rational certificate +
  standalone interval re-checker (attempts/A22-local-rigidity/). First local-optimality certificate for n = 11.
- **A21 (STRUCTURE at 3.88, certified):** every 11-packing at side ≤ 3.88 has a corner-zone square (total 10.5611 < 11)
  and a side-zone square (total 8.7453). Also certified (THM3 orientation exclusion, total 10.9748 < 11): every such packing has a square oriented in [0,18]u[27,63]u[72,90] degrees, i.e. no 11-packing at side <= 3.88 has all squares tilted strictly between 18 and 27 degrees. Per-corner/per-side/wider-orientation-window versions are NOT certifiable at 3.88
  (above the certifiability ceiling / alive via ≈43° near-packings; Trump itself keeps the [0°,5°]∪[40°,50°] window alive).
- **A23 (WASTAGE, the PI's integral constraint):** sound dead-region certifier (witness-point overlap; float-guarded
  and pure-Fraction modes; core-box-uniform "PlacedBox" certificates). Ledger results: single squares strand ≤ 0.6 of
  the s²−11 ≈ 4.03 budget (weak at the root; corner squares strand 0), but the interior mid-tilt structures die:
  adjacent 33° pinwheel pair strands 1.88 at depth 2 (1.38 over a continuum box), the full 4-cycle 6.55 > budget, and
  **exactly at s': dead area 2816/625 = 4.5056 > s'²−11 (pure Fractions, 0 failures) ⇒ no 11-packing at s' contains
  the pinwheel 4-cycle** — the first tool that kills a mid-tilt structure on the optimality side.

Remaining for s(11) = s': the global stage — exclude packings outside the A22 box at s ≤ s' — with the composed
killer (coverage LP + wastage ledger + A21 scaffolding) as the candidate node test; first experiment = A14 node-3
pinwheel children.


## Campaign: composed case tree at 3.84 (A24–A25, 2026-08-20)

Goal: certify s(11) >= 3.84, which the measure LP provably cannot reach (ceiling 3.83; A19's exact value-11
fractional packing at 3.84 makes the impossibility rigorous). Two independent node-kill tests were composed:
T1 = coverage LP (A14), T2 = wastage ledger (A23/A25) against the budget s^2 - 11 = 2341/625 = 3.7456.

**Verdict: NOT certified; the record stays 3.82.** What the campaign did establish:
- **A25 continuum wastage atlas** (`attempts/A25-wastage-atlas/`, query.py): certified dead-area lower bounds
  uniform over (centre-box x tilt-box) hypothesis cells, 2.9 s/cell (A23's exhaustive method: ~1 CPU-day/cell).
  **Minimum k = 3**: three mid-tilt squares strand 4.7930 > 3.7456 at 3.84 and 4.2070 > 4.0318 **at s'** (exact
  Fractions); k = 2 is impossible (best 3.1953). The certified value is a THRESHOLD in centre-box size
  (point 1.74 / 0.075-box 1.49 / 0.15-box 0.32 / cliff to 0 at 0.10-0.15), tilt width nearly free. Strongest
  single-square wastage is a square ~1.2 from a corner (L-moat 1.40-1.60), not the flush-to-wall square.
  Coverage: 35-43% of mid-tilt cells >= 0.3; deep-interior cells are genuinely 0.
- **A24.1 (certified theorem)**: every packing of 11 unit squares in side <= 3.84 has a square centred in the
  interior zone [11/10, 137/50]^2 (measure total 8.240152 < 11, margin 2.76 — the largest case-LP margin at 3.84;
  A14's corner lemma had 0.88). Sharp: widening the zone by 0.2 returns tau = 11.000 and the 1/4-structure.
- **A24.W (certified)**: no such packing has four squares in the four core boxes (c_i +- 0.03) x [30,36] deg of the
  translated A12 pinwheel — certified dead area 2416/625 > 2341/625. The same node is also killed by a coverage
  certificate (total 103/25 < 7): **the first node killed independently by an area certificate and a coverage
  certificate**.
- **T1/T2 split: 30 kills, all T1; T2 fired at no tree node.** Reason quantified: T2 needs >= 3 cores of centre
  half-width <= 0.075, a depth at which T1 has already won; the wastage scaling law at 3.84 is k=1: 0.92,
  k=2: 2.60, k=3: 4.36 (dead), with a cliff to 0 at half-width 0.10.
- **Interior-first beats wall-first**: A14's blocker (a corner square fixed exactly still leaves tau* = budget)
  does not carry over — an interior core of half-side >= 0.35 gives slack -0.7...-2.0. Certified root + one
  exhaustive D4-reduced level (216 boxes, cover checked in rationals): 26 converged deaths, 15/15 attempted leaves
  certified, 3 genuinely alive. Estimated cost to close 3.84 this way: **100-300 CPU-hours**, two orders of
  magnitude below A14's wall-first estimate — the first affordable route, though the 3 alive boxes make
  termination a gamble.

## The global boundary ledger: counting works, charging has an exact zero (A26, 2026-08-21)

The PI's reformulation of the wastage test: a uniformly tilted lattice of unit squares tiles the plane with zero
waste, so waste is made only where a same-tilt block TERMINATES (wall wedge / inter-block sliver) — evaluate a
boundary functional globally on all 11 squares instead of summing local pockets.

- **The band-counting lemma is exact and reduces to the small-n constants.** A unit square avoids the width-w
  boundary band iff its centre is >= w + h(theta) from every wall (h = (cos+sin)/2), i.e. iff it lies in the
  CONCENTRIC square of side B = s-2w. Hence **m(w) = max{ n : s(n) <= s-2w }**, exact for n <= 9 and unavailable
  exactly when B >= 3 (it would need the open s(10)).
- **Theorem A26.1 (elementary, exact, self-contained).** If (2B-1)^2 < 8 then at most ONE unit square fits in a
  square of side B. At s = 96/25 with w = 1: 4489/625 = 7.1824 < 8, so **at least 10 of the 11 squares meet the
  width-1 boundary band** — at 3.84, at s' = 3.877084, and at every s < 3.914213. Proof: SAT gives
  |u.(c1-c2)| >= 1/2 + h(psi) >= 1 for an edge normal u of Q1, while |u.(c1-c2)| <= 2 h1 (B - h1 - h2) <=
  (B-1/2)^2/2. (Side effect: re-proves s(2) >= 1/2 + sqrt2.)
- **Theorem A26.2 / the R-profile.** With R := dist(centre, nearest wall) - h(theta), #{R >= w} <= m(w): at most 1
  square above R = 0.93, at most 4 above 0.5665, at most 5 above 0.42. Hence **at least 7 of the 11 squares have
  centre within 1.34711 of a wall.** TIGHT against Trump: his profile is (0.9840, 0.5676, 0.5486, 0 x 8) and the
  threshold at s' is 0.98144 — exactly one square above it; ZERO Trump squares avoid the width-1 band.
- **The charged wall functional has an EXACT ZERO, and that is the end of the route.** Built on A25's atlas with
  proper unions (exact rational cross-square rectangle disjointness, max-weight independent set) and validated
  against every published A23/A25 number. Over the 1070 admissible band cells the MINIMUM certified charge is
  **0.0000** (smallest positive 0.0039): a unit square flush against a wall and within a few degrees of
  axis-parallel strands nothing, because an axis-parallel block terminating on an axis-parallel wall makes no wedge.
  That configuration is 6 of Trump's own 11 squares. **Minimum total charge over all admissible profiles = 0.0000
  against the budget 3.7456**; 0 kills at A24's three live level-1 boxes and 0 at the root. Requirement:
  0.5351 per square at n = 7, or 0.9364 at n = 4; best certified value with tilt and depth floors is 0.1602.
  Calibration: **Trump's own certified wall charge is 0.8672 = 21.5 % of his budget.**
- **Theorem A26.3 (negative, and it closes the I-L8 boundary-band line).** The band lemma is a family of region-rank
  cuts. A19's EXACT rational value-11 fractional packing at 3.84 satisfies every band, tilt, band x tilt and A21
  zone rank cut, several with equality (weight 1 = m(w) in the deep interior, weight 9 = the near-upright cap,
  weight 1 = each corner-zone rank). So it remains feasible for the cut-strengthened LP: **tau_cut(3.84) >= 11.**
- **The weak link is quantitative tilt forcing, and it is now CLOSED negatively.** Elementary: two squares with tilt
  within eps of axis-parallel have ||Dc||_inf >= 1/(cos eps + sin eps), so an NxN pigeonhole on the centre square of
  side s-1 gives at most N^2 when (s-1)(cos eps + sin eps) < N: at most 9 within 3.326 deg at 3.84 (2.503 deg at s').
  A24's LP probe already does better and IS a valid rank bound (a tilt class of a packing is itself a packing, so its
  size is <= floor(tau_B)): at most 9 within 10 deg (tau = 9.358). And a numerical search with an exact-SAT-verified
  witness shows **ten unit squares of tilt <= 15 deg DO fit in [0,3.84]^2**, the 9-vs-10 threshold being
  eps* ~ 12 deg. **The provable ceiling is within 2 deg of the truth: at most ~2 squares can ever be forced to be
  mid-tilt, against the ~7 the ledger needs.** Conjecture A26.T ("at most 9 within 28.5 deg", the cheapest cut that
  would have cut off A19's value-11 solution) is REFUTED by a 10-square witness of max tilt 23.36 deg. General
  principle: **an LP-certified rank bound tau_B(R) is automatically satisfied by every feasible fractional packing**
  (restrict y to R), so only a combinatorial bound strictly below tau_B(R) can ever cut.


## The global wall-strip ledger (A26, 2026-08-20) — counting works, charging cannot

Motivated by the PI's observation that the per-node wastage test is local and monotone (a lone interior square
strands ~0), hence blind to propagation: a tilted block must terminate, at a wall or against another block.

**Certified counting results (exact, elementary):**
- **Lemma B0.** A square avoids the width-w boundary band iff it lies in the concentric square of side B = s-2w.
  So band-avoiders are themselves a packing one level down: m(w) = max{n : s(n) <= s-2w}. (Exactly known for
  n <= 9; hits the open s(10) for large B.)
- **Theorem A26.1.** If (2B-1)^2 < 8 then at most ONE unit square fits in a square of side B. At s = 3.84, w = 1:
  (2*1.84-1)^2 = 7.1824 < 8, so **at least 10 of the 11 squares meet the width-1 boundary band**; likewise at s'
  (7.5854 < 8) and for every s < 3.9142. Four-line proof (SAT normal + support bound); re-proves s(2) >= 1/2+sqrt2.
- **Theorem A26.2.** At least 7 of the 11 squares have centre within 0.64 + sqrt(2)/2 = 1.34711 of a wall (via s(5)).
- Trump check, tight: his band profile is (0.9840, 0.5676, 0.5486, 0 x8) — zero squares clear the width-1 band and
  exactly one clears the s' threshold.

**Why the ledger nevertheless cannot close: the charge functional has an exact zero.** A flush near-upright square
at a wall strands nothing — an axis-parallel block terminating on an axis-parallel wall makes no wedge (6 of Trump's
own 11 squares are exactly this). Over 1070 admissible band cells the minimum certified charge is 0.0000, so the
minimum total charge over all profiles consistent with the counting lemmas is **0.0000 vs budget 2341/625 = 3.7456**.
Closing would need ~7 wall-meeting squares at substantial tilt (0.5351 each at n = 7, or 0.9364 at n = 4).

**And tilt cannot be forced: a hard ceiling, verified.** Ten unit squares with all tilts <= 23.36 deg fit in
[0,3.84]^2 (witness in `attempts/A26-wall-ledger/results/tiltmax_key.json`; independently re-checked by the advisor:
min containment margin +2.3e-4, min pairwise SAT separation +9.0e-5). Hence "at most 9 squares have tilt <= eps" is
FALSE for eps >= ~12 deg, so at most ~1-2 squares can ever be forced to substantial tilt, against the ~7 the ledger
needs — unreachable in principle, not merely unproved. The specific cut that would have worked ("<= 9 squares within
28.5 deg of axis-parallel") is refuted by the same witness.

**Theorem A26.3 (closes the I-L8 rank-cut line).** A19's exact value-11 fractional packing at 3.84 satisfies EVERY
band / tilt / band-x-tilt / A21-zone rank cut, several with equality, so tau_cut(3.84) >= 11. General principle:
an LP-certified rank bound tau_B(R) can never be violated by a feasible fractional packing (restrict the packing to
R), so only a COMBINATORIAL bound strictly below tau_B can cut. This also explains A12's failure retrospectively.

Residual value: the counting lemmas are free pruning for the case tree ("two squares both with band-clearance
>= 0.93" is dead by A26.1), and B0+A26.1 is the cheapest non-trivial geometry in the repo to formalise in Lean.


## Sharp band lemma via A28.★ (advisor, 2026-08-21)

A28's formalisation left one inequality open: |u·e| + |u·e⊥| + ‖u‖₁‖e‖₁ ≥ 2‖u‖₁ for unit u, e.
Proved (docs/proofs/a28star.md): a two-branch reduction collapses both branches to
(1−sinθ)(1−cosθ) ≥ 0. Consequence: two unit squares need side B ≥ 2 (sharp, = s(2)), so at most one
of the 11 squares avoids the width-w band whenever w > (s−2)/2 — w* = 0.92 at 3.84 / 0.9385 at s′,
valid for every s < 4 (A26.1: w = 1, s < 3.9142). Human proof + numeric check; Lean pending (A28's
Band.lean is wired to accept it).

## Next steps (ordered)

1. (done) s = 3.82 certified. Pushing to 3.83 is not possible with the pure measure method (τ*(3.83) = 11.000).
2. I-L6 "case-LP": piloted (A13) and pushed (A14) at 3.84 — the tree does not close with LP nodes; A16 shows ϑ′ node
   certificates kill the stalling nodes with margin 0.3–0.6 on the same placement graphs ⇒ the viable route is the
   I-L9 kernel certificate. A17 (float phase) shows the plain LP-atom indicator class stalls at λ ≈ 11.0–11.2 at 3.84;
   next: the C ≤ 0 restricted class (no pair verification) with kernel-purposed atoms + smooth features (A17 §6.3),
   and only then the 14-node tree if the enriched root still misses 11.
3. Angle-box B&B with the orientation-restricted measure LP as box killer (first experiment: A07's LP with θ
   restricted to [θ*−δ, θ*+δ] ∪ {0} for δ = 10°, 5°, 2°, to see where τ*_B(3.877) crosses 11).
4. Formalise the bridge lemmas in Lean/Mathlib (needs ~10 GB disk). A26's Lemma B0/E1 is the cheapest non-trivial
   geometric statement in the repo to formalise (SAT + rational arithmetic, a four-line proof) and yields a real
   structure theorem (>= 10 of 11 squares meet the width-1 band).
5. A26 follow-ups: (a) FREE, today - LP-less pruning for A24's interior-first tree: "two squares both with R >= 0.93"
   is dead by Theorem A26.1 and "five squares with R >= 0.5665" by Theorem A26.2; (b) the only surviving charging
   direction is a CORNER-occupancy statement ("how many squares must sit at depth 0.9-1.35 near a corner?", where the
   certified charge is 1.40-1.60 and three squares already exceed the budget) - an LP question of the A21.1 type;
   (c) do NOT refine the wall atlas (its failure is an exact zero, not a resolution problem) and do NOT chase tilt
   forcing past 12 deg (nothing is there).
