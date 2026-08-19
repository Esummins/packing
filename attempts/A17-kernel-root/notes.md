# A17-kernel-root — continuum ϑ′-kernel certificate at the root node (float phase)

Owner: SDP postdoc (A17). 2026-08-19. Status: **done-negative on the λ < 11 target** (calibration
PASS; machinery works and is validated; the 1181-atom indicator class stalls at λ ≈ 11.0–11.2 at
s = 3.84; two structural discoveries — the closed-disjointness exemption §1(a) and the C ≤ 0
restricted class §6.1 that needs no pair verification — define the A18 route). Survived two process
deaths via on-disk state (loop.py --resume).

GOAL. Build the continuous ϑ′-kernel certificate at the root: finite feature map φ: P_s → R^{m+1},
M ⪰ 0 D4-invariant with K(x,y) = φ(x)ᵀMφ(y) satisfying
  (i)  K(x,x) ≤ λ − 1  for all admissible placements x ∈ P_s,
  (ii) K(x,y) ≤ −1     for all pairs x,y ∈ P_s of DISJOINT CLOSED squares (see §1(a): touching
       pairs exempt — this is exactly what the bridge needs and what indicator features require),
and λ < 11 at s = 3.84 (stretch 3.85, 3.86), certified in float (the strongest float cutting-plane
oracle finds no violation); the exact/rational phase is A18.

## 1. The bridge argument (kernel certificate ⇒ s(11) ≥ s)

Placement space P_s = {x = (cx, cy, θ) : Q(x) ⊂ [0,s]²} (closed unit square Q(x), any orientation;
θ mod π/2). Suppose K: P_s × P_s → R is of the form K(x,y) = φ(x)ᵀMφ(y) with M ⪰ 0 — then for any
x_1..x_n: Σ_{i,j} K(x_i,x_j) = vᵀMv ≥ 0 with v = Σ_i φ(x_i) — and suppose (i), (ii) hold with some λ.

Claim: any packing of n unit squares with pairwise disjoint interiors in a container of side
s′ < s implies n ≤ λ. Hence λ < 11 ⇒ no 11-packing in any side s′ < s ⇒ s(11) ≥ s.

Proof. Let n closed unit squares with pairwise disjoint interiors fit in [0,s′]², s′ < s. Scale by
σ = s/s′ > 1: the container becomes [0,s]² and the squares become σ-squares (side σ > 1) with
pairwise disjoint interiors. Shrink each σ-square about its centre to a unit square: the shrunk
closed unit square lies in the INTERIOR of its σ-square, so the n closed unit squares are pairwise
DISJOINT (as closed sets: two closed sets contained in the disjoint interiors of the σ-squares) and
each is contained in [0,s]² — i.e. we have x_1, …, x_n ∈ P_s pairwise disjoint in the sense of (ii)
(their interiors are disjoint; in fact the closed squares are disjoint, which is stronger, so the
closed-vs-open bookkeeping of (ii) is safe: (ii) is required for all pairs with disjoint interiors,
and the constructed pairs have disjoint closures).
Now 0 ≤ Σ_{i,j} K(x_i, x_j) = Σ_i K(x_i,x_i) + Σ_{i≠j} K(x_i,x_j) ≤ n(λ−1) + n(n−1)·(−1),
using (i) on the diagonal and (ii) on the n(n−1) ordered disjoint pairs. Hence n² − nλ ≤ 0, n ≤ λ. ∎

Remarks. (a) CLOSED/STRICT DISJOINTNESS BOOKKEEPING (important). The scale-shrink step converts
"disjoint interiors in side s′ < s" into "pairwise disjoint CLOSED unit squares in [0,s]²". So (ii)
only needs to hold for pairs of DISJOINT CLOSED squares (SAT overlap depth < 0, strictly); TOUCHING
pairs (depth = 0) are EXEMPT. This is not a convenience but a necessity for closed-square indicator
features: a touching pair can share an atom on the common boundary, and then K(x,y) = τ·w_p/(m(x)m(y))
− 1 > −1 — observed directly in the 3.80 calibration (a touching grid pair sharing a boundary atom
had K = −0.706). For strictly disjoint closed squares a shared atom is impossible, and the LP-form
kernel is exactly −1 there. Note the exemption cannot be widened to "depth < −η" for any fixed η > 0:
the shrink produces gaps that go to 0 as s′ → s, so (ii) must hold for every strictly positive gap —
the piecewise-constant structure handles this (the exact phase checks cell pairs whose closures
realise disjoint placements). (b) Only λ < 11 is needed. (c) The LP/measure certificate is the
special case (§2), so this class is at least as strong as Theorem 1 with the same atoms.

## 2. Feature class

Atom set {p_k}_{k=1..m} with weights w_k > 0 (a blocking-measure support; here: the atoms of A07's
LP at the target s — see §3), coverage pattern a_k(x) = 1[p_k ∈ Q(x)] (closed square), coverage
mass m(x) = Σ_k w_k a_k(x). Feature map (NORMALISED indicator variant):

    φ(x) = (1, a_1(x)/m(x), …, a_m(x)/m(x)) ∈ R^{m+1}.

φ is piecewise constant on the cells of the atom arrangement in (cx,cy,θ) — m(x) is a cell-constant
positive rational — so K(x,y) is piecewise constant on cell pairs; verification is a finite cell
problem exactly as in A15 §4 / A16 §3(e). Requirement: m(x) > 0 for every x ∈ P_s (checked by the
diagonal oracle; the rigorous phase needs the exact B&B check "every placement contains an atom").

Why normalised (and not plain 1[p∈Q]): the LP certificate itself is then feasible —
M_LP = (1/τ) Σ_k w_k (τ e_k − e_0)(τ e_k − e_0)ᵀ ⪰ 0 gives K(x,y) = τ·(Σ_k w_k a_k b_k)/(m(x)m(y)) − 1,
which is exactly −1 on every disjoint pair (no shared atom, REGARDLESS of whether the measure is
blocking) and K(x,x) = τ/m(x) − 1 on the diagonal, so λ_LP = 1 + τ/min_x m(x) (= τ when the measure
is blocking with min mass exactly 1). This gives (a) the calibration of §4, (b) a feasible interior
start for every SDP solve, (c) the guarantee that the class is at least as strong as the LP on the
same atoms. With PLAIN indicators the LP form is NOT feasible (K(x,x) = (τ−2)m(x)+1 grows with
m(x)), and the class loses that anchor; both variants are piecewise constant on the same cells, so
verification cost is identical. features.py implements both (--variant plain kept for experiments).

D4-invariance: the container symmetry group D4 permutes atoms (the atom set is D4-symmetric with
orbit-constant weights, so m(gx) = m(x) and φ(gx) = π(g)φ(x) for a permutation rep π on the m+1
features, e_0 fixed). M is constrained to be D4-invariant (π(g)ᵀMπ(g) = M), block-diagonalised by
the isotypic basis of π (A15/A16 machinery, theta_sdp.symmetry_basis reused verbatim): 5 blocks
(A1, A2, B1, B2, E). Constraints then need only one representative per D4-orbit of rows.

## 3. SDP and cutting-plane loop

Variables: X_ρ ⪰ 0 per irrep (M = Σ_ρ Σ_r T_ρ^(r) X_ρ T_ρ^(r)ᵀ), scalar λ. Minimise λ subject to
  diag rows:  φ(x)ᵀMφ(x) − λ ≤ −1            (one per sampled placement-pattern orbit)
  pair rows:  φ(x)ᵀMφ(y) ≤ −1 − δ_p          (one per sampled disjoint-pair pattern orbit; δ_p = 1e-3
                                              robustness margin, cost ≈ δ_p(λ−1) ≈ 0.01 in λ)
SOLVER NOTE. A sparse-conic (SCS) formulation was built first and abandoned: the patterns are DENSE
(a unit square at 3.84 contains 71–277 of the 1181 atoms, median 132), so one row's coefficient
vector on svec(X) has ~2·10⁵ nonzeros and 2000 rows would need ~4·10⁸ nnz. Instead the SDP is solved
by per-block Burer–Monteiro factorisation X_ρ = Y_ρᵀY_ρ (rank 120 per block; M = ΣTᵀYᵀYT ⪰ 0 EXACTLY
by construction — no PSD projection ever needed) with L-BFGS on the preconditioned hinge² feasibility
loss Σ_i (relu(K_i − rhs_i)/‖φ1_i‖‖φ2_i‖)², wrapped in a λ-descent (walk λ down while the loss can be
driven to ≤ 1e-6; λ floor 10.40 = just below the discrete ϑ′ prediction, so early iterations don't
chase absurd kernels). Validated against cvxpy/Clarabel on small instances (validate_small in sdp.py:
λ_BM = 4.003470 vs λ_Clarabel = 4.003000). Rows enter through per-irrep projections ψ_ρ^(r) = T_ρ^(r)ᵀφ
(dense, Σ_ρ d_ρ m_ρ = nf floats per row side — 19 MB for 2000 rows). One L-BFGS feasibility repair
after adding rows takes 3–10 s; a full λ-descent 20–60 s.

Loop (the A07 row-generation loop with the kernel in place of the mass):
 1. init rows: diagonal = patterns of the A15-style seeded grid (h = 0.2, Δθ = 10°, + A12 ¼-structure
    images + A07 3.84 dual support) + random placements, deduped by D4-canonical pattern; pairs =
    barely-disjoint grid pairs (SAT gap ≤ 0.05) + random tangent pairs.
 2. solve SDP → M (PSD-projected), λ_sdp.
 3. oracles (float attack):
    diag: max K(x,x) over x ∈ P_s — vectorised scan over grid/random/boundary placements
    (admissible-domain boundary cx = w/2 etc. and θ ∈ {0°,45°,90°} included — the A14 oracle-blind-spot
    lesson) + pattern-search polish from the top candidates;
    pair: max K(x,y) over disjoint pairs — full K on a structured node set (disjoint = SAT depth ≤ 0,
    touching included), random tangent-pair sampling (binary search on the contact distance), and
    alternating pattern-search polish from the worst pairs.
 4. add all violated rows (dedup, D4-canonical), goto 2 until max violation ≤ 1e-6 or budget.

Final report: λ_cert = 1 + c·(max diag K found by the strongest attack), c = 1/min(1, −max pair K):
if the pair oracle's max is −1+ε > −1, the scaled kernel cM (still PSD, still in the class) restores
(ii) and inflates the diagonal by c — the reported λ_cert absorbs BOTH oracles' residuals.

## 4. Calibration (run FIRST, at s = 3.80)

M = M_LP from certs/measure_certificate_3.80.json (1069 atoms, τ = 10.801639, certified blocking
with ≈ 3% margin). Machinery must reproduce: pair oracle max = −1 exactly (up to float), diag
oracle max = τ/m_min − 1 with m_min = min coverage ≈ 1.03 (advisor's independent spot check: 1.0300)
⇒ λ ≈ 1 + 10.8016/1.03 ≈ 10.49 (= τ = 10.80 for the unscaled row-converged measure with m_min = 1).
This calibrates: pattern/feature machinery, the LP-form kernel identity, and (critically) whether
the diag oracle FINDS the tight cells.

Results (results/calibration_380.json, 11 s): PASS.
- diag oracle: max K(x,x) = 9.490328 ⇒ min coverage found 1.029676 — slightly SHARPER than the
  advisor's independent spot check (1.0300); λ_LP = 10.4903 = τ/m_min ✓ (equals τ = 10.80 exactly
  after rescaling the certificate weights by 1/m_min, i.e. for a min-mass-1 blocking measure λ = τ).
- pair oracle: max K over disjoint pairs = −1.000000000 exactly ✓ (after the closed/strict
  disjointness fix of §1(a) — the first run with "interior-disjoint" semantics correctly flagged a
  touching pair sharing a boundary atom at K = −0.706, which is exactly why (ii) is stated for
  closed-disjoint pairs).

## 4b. Comparison with the discrete predictions, and s = 3.85/3.86

A15/A16 measured ϑ′ ≈ 10.38 (3.84) and 10.43–10.48 (3.85) on seeded 2200–3750-node graphs — an
ARBITRARY PSD Gram matrix on the node set. The kernel class here is the restriction of that object
to quadratic forms in the 1181-atom coverage patterns: the run shows this restriction costs ≈ +0.7
(11.05–11.13 vs 10.38) at 3.84, i.e. the grid-vs-continuum risk R1 of A16 §3(e) is NOT the (only)
active one; the FEATURE-CLASS risk R2 is, and it binds first. The stretch targets 3.85/3.86 were
therefore not run (λ < 11 already fails at 3.84 in this class).

## 5. Feature set used

s = 3.84: atoms of A07's LP run at 3.84 (results/v2_s3.84.json: 155 D4-orbits, 1181 atoms, total
mass 11.020, min coverage ≈ 0.945 — NOT blocking, which is fine for the normalised class), plus
e_0: m+1 = 1182 features. (Alternative kept in features.py: the 3.82 certificate atoms mapped by
the D4-equivariant piecewise-linear stretch fixing the Stromquist lines x,y ∈ {1, s−1}.)

## 6. Results (filled in as runs finish)

### 6.1 Structural discovery: a subclass that needs NO pair oracle at all

Write M = [[1, −wᵀ], [−w, τ·diag(w) + C]] in the (e_0, atom) coordinates (the LP form is C = 0).
For any x, y whose patterns share no atom: K(x,y) = −1 + a(x)ᵀC a(y)/(m(x)m(y)), where only
OFF-DIAGONAL entries C_pq (p ∈ supp a(x), q ∈ supp a(y), p ≠ q — p = q is impossible) contribute.
Hence if C_pq ≤ 0 for all p ≠ q (diagonal free), then K(x,y) ≤ −1 for EVERY pattern-disjoint pair —
and two strictly disjoint closed squares can never share an atom, so (ii) holds UNIVERSALLY, by
algebra, with no 6-D verification whatsoever. The certificate then needs only (a) M ⪰ 0 (rational
LDLᵀ), (b) the 3-D diagonal check K(x,x) = −1 + τ/m(x) + a(x)ᵀCa(x)/m(x)² ≤ λ−1 — a verify_measure-
style cell B&B with a quadratic form instead of a sum. The price: K is ALSO forced ≤ −1 on
overlapping pairs that share no atom (the class cannot "spend" kernel mass there).
Numerical viability test on the A15 c384 graph (N = 2337, 1.11 M edges) with the 1181-atom set:
80.15 % of the edges share an atom; dropping the 220,820 non-sharing edges (median SAT depth 0.094)
leaves α = 10 UNCHANGED (CP-SAT OPTIMAL) — the integral obstruction survives the restriction.
Not implemented in this attempt (time); recommended as THE structure for A18 (it deletes the
hardest rigorous-verification component, the 6-D pair space).

### 6.2 Cutting-plane run at s = 3.84 (tag k384)

Feature set §5 (1181 atoms + e_0, nf = 1182; blocks A1/A2/B1/B2/E = 156/141/153/142/295); initial
rows: D4-deduped patterns of the seeded structured grid + 900 random placements (diag), 2600
barely-disjoint structured pairs (SAT gap < 0.08) + 500 tangent pairs; δ_p = 1e-3; rank 120/block.

Convergence log (it, λ_sdp on the row set, oracle max K(x,x), oracle max pair K, rows):

| it | λ_sdp | maxdiag | maxpair | rows |
|---|---|---|---|---|
| 0 | 10.4000 (floor) | 9.402 | +0.095 | 1994 |
| 2 | 10.6146 | 10.010 | −0.375 | 3094 |
| 4 | 10.9896 | 10.074 | −0.316 | 4092 |
| 6 | 11.0521 | 10.192 | −0.701 | 4862 |
| 8 | 11.0771 | 10.119 | −0.735 | 5894 |
| 10 | 11.0648 | 10.172 | −0.796 | 6931 |
| 12 | 11.1275 | 10.127 (per-iteration oracle exhausted: viol −6e-8) | −0.779 | 8045 |

**Final attack** (loop stopped after it 12; 3 seeds, 190k placements/seed with coverage-scan seeds,
21–22k tangent pairs/seed + node-set scans + polish; logs/k384_attack.out):
maxdiag = 10.428230 at (1.6034, 1.9897, 33.02°) — exactly the min-coverage cell (m = 0.968742;
LP-form value there 10.376, the optimized kernel is +0.05 above it);
maxpair = −0.716331 (interior mid-tilt pair);
⇒ λ_cert (both oracles fully absorbed by the scaling trick, c = 1.396) = **15.56** — the honest
"certified in float" number is worthless as a bound, because the pair side never closed;
λ_sdp (row set, 8044 valid rows) = **11.127**; deep-feasibility check at 10.90: §6.4.
Exported: results/kernel_k384.json + kernel_k384_M.npy (nf = 1182, rank@1e-8 = 720, min eig −3e-16).

Reading. (a) λ_sdp climbs through 11 by iteration ~5 and sits at 11.06–11.13 from then on — the ROW
SET (all rows are valid constraints of the true problem) already places the class optimum at
≥ ~11.05 up to solver slack (§6.4); λ < 11 at 3.84 is NOT reached in the 1181-atom indicator class.
(b) The per-iteration diag oracle (84k placements) was exhausted at it 12 (viol −6e-8), but the
STRONGER final attack (192k placements + the dense coverage-scan seeds) found diagonal cells at
K(x,x) = 10.43 > λ−1 — so even 11.13 is not diagonal-proof; the honest float diagonal supremum is
≥ 10.43 (§ final attack below). The optimized diagonal is ≈ the LP-form diagonal: corr(K(x,x), τ/m(x)) = 0.99 over the
diag rows, binding cells at coverage ≈ 1.000 spread over the WHOLE container (corners (0.52,0.52,0°),
walls, interior tilts 28–70°) — a continuum of tight cells, exactly the LP's tight set. The kernel
improves on the LP-form λ (1 + τ/m_min = 1 + 11.02/0.9687 = 12.38) by ≈ 1.25, but the last 0.13 to
reach 11 would have to come out of the tight-cell continuum, and the pair side refuses: (c) the pair
oracle keeps finding fresh violated cells at K ≈ −0.7…−0.86 (required ≤ −1), all of them
interior mid-tilt (θ ≈ 29–68°) barely-to-moderately disjoint pairs (SAT gap 1e-10…0.4) — the
¼-structure region of A10–A16. Each batch is repaired (L-BFGS restores row feasibility to 1e-8) and
the hot spot moves to a neighbouring cell: whack-a-mole in the 6-D cell space, no convergence of
max-pair toward −1 within 13 iterations (~8000 rows).

## 6.3 Verdict and what to seed A18 with

**λ < 11 at s = 3.84 is NOT reached by the 1181-atom normalised-indicator kernel class.** The float
loop stalls at λ_sdp ≈ 11.05–11.13 with (a) the diagonal oracle-proof and LP-shaped (§6.2b), and
(b) a non-converging stream of pair violations in the interior mid-tilt region. The row set plus
the deep feasibility check (§6.4) locates the CLASS optimum at ≈ 11.0–11.2 — i.e. about +0.7 above
the discrete ϑ′ (10.38): A16's risk R2 (feature class too weak) binds BEFORE the grid-vs-continuum
risk R1. The kernel does beat the pure LP by ≈ 1.2–1.3 on the same atoms (λ_LP-form = 12.38), so
cross terms are worth a full unit — the mechanism works, the basis is short.

Where the +0.13 (to get below 11) has to come from, in order of recommendation:
1. **The §6.1 restricted class (C ≤ 0 off-diagonal) as the OUTER shell + richer atoms.** It removes
   the 6-D pair verification entirely (the item that is both the float leak here and the dominant
   rigorous-phase cost), at a measured discrete price that did not even change α on the A15 graph.
   Build the atom set FOR the kernel (not for the LP): add atoms in the interior mid-tilt overlap
   regions (the 220k non-sharing edges of §6.1 tell exactly where: median depth 0.094 slivers), so
   that "overlapping ⇒ shares an atom" becomes nearly true — then the restricted class ≈ full class.
2. **Smooth/learned features**: interpolate the dominant eigenvectors of A15/A16's discrete dual
   certificates Z (30–45 eigenvalues > 1 %) as explicit smooth D4-functions of (cx,cy,θ) and append
   them to φ — this is what the indicator basis cannot express (it is constant on atom-arrangement
   cells; the discrete Z varies WITHIN the coarse cells of the tight continuum).
3. More indicator atoms alone (e.g. + the 3.82-certificate set, nf ≈ 2950) — cheapest to run with
   this code base (features.py supports unions with w = 0 normalisation weights), but by §6.2b the
   diagonal is pinned by a 2-D continuum of coverage-1 cells, which more atoms refine only linearly.

## 6.4 Deep feasibility check (solver vs class)

`python check_feas.py k384 10.90 4200` — the full it-12 row set (1069 diag + 6430 pair rows), warm
start from the λ = 11.1275-feasible factor, target λ = 10.90, 6 × 700 L-BFGS iterations:
round 0 (700 it, 1056 s): max diag-row violation +1.07e-1, max pair-row violation +2.6e-2;
rounds 1–5 (up to 4200 it): +7.6e-2 / +1.9e-2 → +6.2e-2 / +1.7e-2 → +5.5e-2 / +1.6e-2 →
+4.8e-2 / +1.5e-2 → FINAL +4.48e-2 / +1.36e-2 — the decay ratio per 700 iterations worsens
monotonically (0.71 → 0.81 → 0.89 → 0.88 → 0.92): the residuals plateau at ≈ 0.045, they do not
collapse (vs 1e-8 reached in 10 iterations at 11.1275); the row set is infeasible at λ = 10.90 to
the best of this solver's ability. The violated/binding diag rows at 10.90 are the same tight-cell
continuum as §6.2(b): (0.520, 1.520, 0°) cov 1.0000 (worst, +4.5e-2), (0.520, 0.520, 0°),
(2.447, 2.506, 28.5°), (1.399, 2.468, 69.6°), … — wall/corner uprights and interior tilts, all at
coverage ≈ 1.000 (full list: logs/check1090.out). Not a proof of infeasibility (nonconvex, finite iterations,
rank-120 blocks),
but strong evidence that the ROW SET is infeasible at 10.90, i.e. the class optimum on these rows
lies in ≈ (10.9, 11.13]. Combined with the diag attack value 10.428 (⇒ true λ ≥ 11.43 for THIS M;
the class could trade some of that back), the honest class estimate is ≈ 11.0–11.2. (Later rounds,
if they moved, are in logs/check1090.out.)

## 7. Honest gap to a rigorous certificate (what "certified in float" does NOT give)

1. **M ⪰ 0**: exact by construction here (M = Σ TᵀYᵀYT with float Y, so M is a float Gram matrix —
   exactly PSD as the rational matrix it denotes, once Y is read as exact rationals). Rational LDLᵀ
   is then trivial; this item is essentially free for A18.
2. **Oracle completeness, diagonal (3-D)**: the float diag oracle = dense scans (structured grid,
   80k+ random with admissible-boundary and axis-θ emphasis, boundary sweeps at 0.25–0.5°/0.01–0.02,
   A07-style rotated-frame prefix-sum coverage scan at 0.25°/0.005 + coverage descent) + pattern-
   search polish. The rigorous replacement is verify_measure.py's exact cell B&B with the quadratic
   form φᵀMφ in place of the mass sum (piecewise constant on the same arrangement cells; interval
   enclosures only for deciding cell membership, exactly as now). Structurally understood, not done.
3. **Oracle completeness, pairs (6-D)**: the float pair oracle = full K on structured node sets
   (~3000 nodes, all strictly-disjoint pairs), 40–120k random tangent pairs (contact-distance binary
   search), alternating pattern-search polish with re-contacting. This is the weakest link: the
   rigorous replacement is the cell-pair table over the atom arrangement (A15 §4 / A16 §3(e)) —
   finite but large; OR the §6.1 restricted class, which removes this item ENTIRELY (recommended).
4. **m(x) > 0 for all x** (normalised features well defined): float evidence min m(x) ≈ 0.97 ≫ 0 at
   3.84 (dense coverage scan + descent); exact check = one verify_measure run with need = tiny.
5. **Float arithmetic in K evaluations**: patterns are decided by float sign tests; cells are
   correct except within ~1e-15 of atom boundaries. The rigorous phase re-derives every binding
   decision in exact arithmetic (the machinery exists: verify_measure's integer predicates).
6. **The margin bookkeeping**: pair rows are imposed at ≤ −1 − δ_p (δ_p = 1e-3) and the final λ_cert
   absorbs residuals via the scaling trick (λ_cert = 1 + maxdiag/min(1, −maxpair)); a rational
   version of the same one-line argument transfers to A18 unchanged.
7. **Lean**: the bridge lemma of §1 (five lines of algebra given a PSD-kernel evaluation) + a cell
   checker; comparable to the measure-checker formalisation already done (lean/PackingCert).

## 8. Files / reproduce

- `features.py` — atom sets (A07 3.84 LP atoms; 3.82 certificate + D4-equivariant stretch), pattern/
  coverage/feature computation (normalised indicators), D4 action on atoms/features, isotypic basis
  (reuses A16 theta_sdp.symmetry_basis), LP-form kernel M_LP, D4-canonical row keys.
  `python features.py` = smoke test.
- `sdp.py` — KernelSDP: row projections per irrep, Burer–Monteiro blocks + L-BFGS hinge² feasibility,
  λ-descent with margin-aware acceptance (pair residual ≤ δ_p/2; diag residual folded into λ).
  `python sdp.py` = validation vs cvxpy/Clarabel.
- `oracle_diag.py` — diag oracle (scans + polish), boundary sweeps, A07-style dense coverage scan
  (`low_coverage_placements`) and coverage descent.
- `oracle_pair.py` — SAT geometry (depth, strictly-disjoint semantics), tangent-pair sampler,
  pair oracle (node-set scan + tangent pairs + alternating polish with re-contact), KernelEval.
- `calibrate.py` — the 3.80 calibration (§4). `check_feas.py` — deep feasibility of a saved row set
  at a given λ (solver-vs-class diagnosis). `loop.py` — the cutting-plane driver (state saved every
  iteration; `--resume`). `export_cert.py` — writes results/kernel_<tag>.json + _M.npy.
- results/: calibration_380.json, k384.json (history), k384_state.npz (Y + all row placements),
  kernel_k384.json + kernel_k384_M.npy (final export).
- Reproduce: `python calibrate.py`; `python loop.py --s 3.84 --tag k384 --iters 120 --maxiter 300
  --sdp_time 420 --rank 120 --lam_floor 10.40 --row_cap 4200` (resume with `--resume`);
  `python check_feas.py k384 10.90 4200`; `python export_cert.py k384 3.84`.
