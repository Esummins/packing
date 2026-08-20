# A19-hybrid-kernel — the hybrid kernel class (Z-sign globally, free block on the mid-tilt region R)

Owner: SDP postdoc (A19). 2026-08-19. Status: **done-negative** (the hybrid class with a
computationally-reachable R-block buys ≈ 0.002–0.005 over the automatic class at both 3.80 and
3.84 — λ < 11 not approached, gate (b) failed; mechanism diagnosis + machine limits in §4/§6;
the class algebra, validation suite, localised-pair machinery, burden quantification and the
τ*(3.84) ≥ 11 pipeline are delivered and reusable).

GOAL. The only kernel route A18's collapse theorem leaves open: φ(x) = (1, a(x)/m(x)) over an
enriched atom set, M = [[1, −wᵀ],[−w, D]] with D_pq unrestricted ONLY for atom pairs p, q both in a
designated region R (mid-tilt sliver-overlap region), Z-sign (S_pq ≤ −w_p w_q) everywhere else.
Target λ < 11 at s = 3.84 (discrete ϑ′ prediction 10.38; automatic-class floor = τ*(3.84) = 11.02).

## 1. The hybrid class algebra

Setting as in A17/A18: atoms p_1..p_m ∈ [0,s]², weights w_p ≥ 0 D4-orbit-constant (base atoms have
w_p > 0; ENRICHMENT atoms may have w_p = 0 — they change the patterns a(x) but not the mass
m(x) = wᵀa(x)), features φ(x) = (1, a(x)/m(x)), a_p(x) = 1[p ∈ Q(x)] (closed square), m(x) > 0
assumed on P_s (A17 item 4).

**Class H (hybrid, "diagonal + R-block" parametrisation).** Let R ⊂ [0,s]² be a D4-closed region and
I_R = {p : p ∈ R} (a union of atom orbits). Members:

    M = [[1, −wᵀ], [−w, D]],   D = diag(g) + F,
    g ∈ R^m (free diagonal),   F symmetric, F_pq = 0 unless p ≠ q and p, q ∈ I_R,   M ⪰ 0.

This sits inside the general hybrid class {M ⪰ 0, S_pq := (D − wwᵀ)_pq ≤ −w_p w_q for p ≠ q not both
in R} at the Z-boundary: our non-R off-diagonal is S_pq = −w_p w_q exactly (D_pq = 0). Motivation:
A18 Prop 2 (pointwise monotonicity) shows off-bound mass is never profitable in the automatic class;
we adopt the boundary as a parametrisation and CHECK the loss numerically (validate.py V3: at small
scale, the full hybrid SDP with free S ⪰ 0 + sign constraints equals the diag+R-block SDP to solver
accuracy — see §4).

**(H1) Diagonal.** wᵀa(x) = m(x) gives (as in A18 §2)

    K(x,x) = 1 − 2 + a(x)ᵀ D a(x)/m(x)² = −1 + ( Σ_{p∈x} g_p + a_R(x)ᵀ F a_R(x) ) / m(x)²,

where a_R(x) = the pattern restricted to I_R. So condition (i), K(x,x) ≤ λ − 1, is LINEAR in
(g, F, λ):  Σ_{p∈x} g_p + a_R(x)ᵀ F a_R(x) ≤ λ·m(x)².

**(H2) Pairs — automaticity.** For x, y with disjoint CLOSED squares the patterns share no atom
(A18 §1(a)), so the diag(g) part contributes nothing to a(x)ᵀDa(y) and

    K(x,y) = −1 + a_R(x)ᵀ F a_R(y) / (m(x) m(y)).

CONSEQUENCE: **K(x,y) = −1 exactly for every disjoint closed pair UNLESS both x and y cover an atom
of I_R.** Condition (ii) is automatic outside the R-meeting pairs; on R-meeting disjoint pairs it is
the LINEAR constraint a_R(x)ᵀ F a_R(y) ≤ 0 (imposed with margin −δ_p·m(x)m(y), δ_p = 1e-3, as A17).

**(H3) PSD.** M ⪰ 0 ⟺ S = D − wwᵀ ⪰ 0 (Schur on M_00 = 1) ⟺ [[D, w],[wᵀ, 1]] ⪰ 0 (Schur on the
corner 1). Partition atoms into N = non-R and R: D is diag(g_N) ⊕ (diag(g_R) + F). Schur on
diag(g_N) ≻ 0 reduces the m×m condition to the (k+1)×(k+1) condition (k = |I_R|):

    Z_R := [[diag(g_R) + F,  w_R], [w_Rᵀ,  1 − Σ_{p∈N} w_p²/g_p]]  ⪰ 0,    g_N > 0.

Σ_p w_p²/g_p is convex in g (per-orbit t_o ≥ w_o²/g_o, SOC/inv_pos in cvxpy), so the whole
optimisation  min λ  s.t. (H1) rows, (H2) rows, Z_R ⪰ 0  is a CONVEX SDP whose only PSD block has
size k+1 — this is exactly the dispatch's "extra variables ≈ |R-atoms|²/2". No Burer–Monteiro,
"stall" is meaningful; scales to the FULL 1181-atom set as long as k ≲ 400.

**(H4) Recovery of the automatic class.** F ≡ 0 gives D = diag(g), and {g : Σ w_p²/g_p ≤ 1} is
exactly A18's two-measure boundary family (g_p = w_p W/u_p has Σ w²/g = Σ w_p u_p / W = 1;
conversely u_p := w_p/g_p normalised dominates). So the F = 0 SDP optimum on a row set equals A18's
GP optimum on the same rows — calibration gate (a) — and the hybrid can only improve on 11.179 at
3.84 / 10.506 at 3.80 through F.

**(H5) D4.** g orbit-constant, F D4-invariant (F = Σ_o f_o A_o over R-pair orbits); rows canon-
deduped. R must be a union of D4 atom orbits.

**(H6) Verification burden (quantified).** If R ⊆ disc(centre, r), a placement covering an R-atom
has its centre within r + 1/√2 of the container centre; the (ii)-verification set is
{(x,y) : both centres in disc(centre, r + 0.7072), SAT-disjoint, both patterns meet I_R} — a
bounded, localised subset of the 6-D pair space (measured fraction reported in §3). Everywhere else
(ii) holds with equality by (H2) — one line of algebra, rational-exact.

Scaling trick for the final report (as A17): λ_cert = 1 + maxdiag/min(1, −maxpair) absorbs both
oracles' residuals (cM is still a PSD kernel).

## 1b. Is the diag+R-block parametrisation lossy? (No — after a subtle correction.)

The general hybrid class is {S ⪰ 0, S_pq ≤ −w_p w_q for p ≠ q not both in R, R-block free}; ours
fixes the non-R off-diagonal AT the bound (D_pq = 0). Naive small-scale comparison (validate.py V3)
suggested the full class is far stronger (10.55 vs 14.47 on the same rows) — but that experiment
imposed canon-deduped REPRESENTATIVE rows on a NON-D4-invariant S, i.e. it dropped the 7 orbit
images of every constraint: the "gain" was pure symmetry-cheating. Imposing D4-invariance on the
full-S SDP (pair-orbit coordinates, full_sdp.py — sign constraints become variable bounds) gives
**14.4674 = the diag+R-block value 14.4674 to 3e-5** (v3c_layer.py / inline check): on D4-invariant
instances with orbit-representative rows the two formulations coincide numerically. Since the true
continuum problem IS D4-invariant (invariant optimum WLOG by group-averaging, convexity), the cheap
diag+R-block class is the right production object. (full_sdp.py, coarsen_atoms and the layered
class v3c_layer.py are kept as machinery: the "active block" extension A ⊃ R — F ≤ 0 allowed on a
layer around R, PSD cone |A|+1 — is the next knob if the R-block stalls, and the invariant
pair-orbit form is the exactness reference. A coarsened-atom full-S route is a dead end: the
automatic-class value degrades from 11.179 (m = 1181) to 11.84 at m = 377 / 12.50 at m = 305
(autocost.py) — the coarsening penalty dwarfs any conceivable hybrid gain.)

Lesson recorded (extends A18's pitfall list): with canon-deduped orbit-representative rows, EVERY
matrix variable must be constrained to the D4-invariant subspace, else the SDP under-estimates.

## 2. Machine validation (validate.py, v3b_check.py, v3c_layer.py, sizing_test.py)

- V1 identities: dense M from (w,g,F) vs A17 φᵀMφ machinery on random placements/pairs:
  max err 8.9e-15 (diag), 6.7e-16 (pairs). PASS.
- V1b automaticity: disjoint pairs not both meeting R: max |K+1| = 0.0 exactly. PASS.
- V2 PSD reduction: min eig of the reconstructed (m+1)-dim M = −5e-9 with only the (k+1)-dim Z_R
  cone imposed. PASS.
- V3 (corrected, §1b): D4-invariant full-S hybrid = diag+R-block hybrid to 3e-5. PASS.
- V4 collapse/gate-(a) mechanism: F=0 SDP = A18 two-measure GP on identical rows: tiny 14.4624 vs
  14.4627 (3e-4); production-size m=76 instance 12.66974 vs 12.66993 (2e-4). PASS.

## 3. R definition (explore_R.py + run_hybrid.py phase 1)

Data (explore_R.py): A17's 6976 recorded pair rows at 3.84 have centre-midpoints concentrated
within ~1.1 of the container centre (q90 = 1.089), angles spread over the mid-tilt range; the A12
¼-pinwheel tilted images sit at radius ≈ 0.8 from the centre at 32.5–34°; A18's binding cells at
3.84 are (1.396,1.321,27.7°), (1.344,2.431,24.5°), (1.273,1.399,45°) — the same ring.

Selection is done from the data, not from hand-drawn boxes (run_hybrid.py): the BINDING INVENTORY =
(i) all diag-attack candidates of the automatic-class optimum within 0.30 of its supremum, (ii) the
A12 mid-tilt images stretched to s, (iii) A17 pair-row endpoints with SAT gap < 0.04, mid-tilt angle
(18°–72°), centre within 1.15 of the container centre. R-atoms = the kcap atoms with the highest
binding-cover counts, added D4-orbit by D4-orbit. At 3.84 with kcap = 148: k = 148 atoms, all in
[1.465, 2.375]² (radius 0.455 from the centre; min cover count kept = 379 of 1351 binding
placements). Pair-verification region (H6): both centres within 0.455 + 1/√2 = 1.163 of the centre.

## 3b. LP floor τ*(3.84) ≥ 11 (task 5, lp_floor.py → lp_floor_384.json)

Weak duality: closed unit squares Q_i ⊂ [0,s]² with rational weights l_i ≥ 0 and
Σ l_i·1[p ∈ Q_i] ≤ 1 at EVERY point p give, for every blocking measure ν (ν(Q) ≥ 1 on all closed
unit squares): Σ l_i ≤ Σ l_i ν(Q_i) = ∫ Σ l_i 1[p∈Q_i] dν ≤ ν([0,s]²), so τ*(s) ≥ Σ l_i.
Construction: columns = the A15 c384 grid-LP support (the ¼-structure at 3.84, value 11.000 under
INTERIOR-cover semantics) + centre jitters, snapped to rational centres (den 4096) and rational
tan(θ/2) (⇒ exact rational cos/sin, exactly-unit squares); the raw structure VIOLATES closed-cover
(touching coincidences, e.g. corner-family right edges at x = 1.0 flush against side-slider left
edges: closed cover 1.125 there), so the LP maximises Σl with η-INFLATED (η = 1/4096) closed cover
≤ 1 at an adaptively grown point set — the inflation forces an η-separation of every critical
coincidence, which is also what makes the exact B&B terminate. Weights are rounded DOWN to
denominator 2^15 (rounding down never increases cover). Exact verification: quadtree B&B over
[0,s]² in Fraction arithmetic; a box passes iff Σ l_i over squares SAT-intersecting the closed box
is ≤ 1 (exact rational SAT on 4 axes). (Results below, §5.)

## 4. Runs (run_hybrid.py; logs/h380.log, logs/h384.log)

**Gate (a) — same-rows reproduction of A18 (PASS, both s).** The F=0 hybrid SDP on A18's own saved
row sets reproduces their convex GP optima: 3.80: 10.506170 vs 10.506272 (r380b final; 1e-4);
3.84: 11.144061 vs 11.1438 (r384 last lam_rows; 3e-4). The class equivalence F=0 ⟺ two-measure
family (H4) is thereby confirmed at full production scale (1069/1181 atoms).

Solver engineering (recorded): Clarabel dies (9 GB alloc, silent process death) at k = 308 with
~11.5k rows; with k = 148 and ~11.5k unpruned rows it thrashes at 8 GB. Working recipe: prune the
diag rows to (near-binding for the automatic optimum within 0.9) ∪ (R-covering), cap 3500; cap pair
rows 1600 per round; k ≤ 148 → Clarabel ≈ 7 min/solve; k > 150 falls back to SCS.

(λ trajectories and final attacks below when the loops finish.)

**h384 outcome (s = 3.84, k = 148 central R-atoms).** Trajectory (Clarabel-accurate points):
it 0 λ = 11.1372 (pair side open, maxpair −0.39); it 1 λ = 11.1458 with the diag oracle EXHAUSTED
(viol −3.6e-8) and maxpair −0.67; decisive same-rows comparison (diag_F.py, 4278 diag + 2200
near-active pair rows, Clarabel):
    hybrid (F on)  λ = 11.145789      F = 0  λ = 11.144063      →  **F buys −0.0017 net**
(= exactly the δ_p = 1e-3 pair-margin cost). F is genuinely active at the optimum (49 % of R-block
entries positive, max +0.15, min −0.55) — the positive cross terms exist but pay for themselves
exactly: every unit of central diagonal relief is re-pinned by the automatic optimum's tight cells
OUTSIDE R (walls/corners), and the localised pair constraints eat the rest. **λ < 11 is not
approached at 3.84: the hybrid with a centre-only R converges onto the automatic-class optimum
11.144 (row value) / 11.179 (A18's attacked value).** Attack numbers for the it-1 kernel: maxdiag
10.146 = λ−1 (exhausted), maxpair −0.666 (open ⇒ λ_cert via the scaling trick is worthless, as in
A17; the honest statement is the converged row value + the same-rows F-buys-nothing comparison).

Solver reality check (recorded): SCS at eps 3e-5/30k iters returns garbage on this geometry
(λ = 6.77 with +2.3 diag violation at it 2 — rejected); all quoted numbers are Clarabel.

Mechanistic reading of the h384 iterations: the pair oracle finds a stream of R-meeting disjoint
pairs at K up to −0.39 / −0.67 — A17's interior mid-tilt whack-a-mole, now localised and against a
convex solver — and at it 1 the binding diagonal cell has MOVED TO A WALL cell (3.11, 3.34, 90°):
F relieves the central mid-tilt cells, but the automatic optimum's tight set spans the whole
container (A17 §6.2's coverage-1 continuum: corners, walls, interior), so the supremum is re-pinned
outside R. The tight structure carrying the LP value (see the LP-floor solution: corner squares +
wall/interior ½-slide families) would have to be covered by R in its ENTIRETY.

**h380 outcome (s = 3.80, gate (b)) — FAIL, same shape.** R at 3.80 is data-driven onto the wall
bands (the binding cells there are wall cells; hull spans the container, radius 1.669). Same-rows
comparison (diag_F.py, Clarabel, 3535 diag + 2200 near-active pair rows):
    hybrid (F on) λ = 10.503689      F = 0 λ = 10.506152      →  **F buys +0.0025**
(gross, i.e. ≈ +0.005 before the δ_p margin cost). τ*(3.80) = 10.42 required a gain of 0.086:
the hybrid recovers ~3 % of it. Gate (b) fails: the hybrid cannot beat the LP floor even at 3.80,
where the discrete ϑ′ is 10.0. F is again genuinely active (|F|max 0.36, half positive) but pays
for itself.

Solver-junk caveat recorded: the resumed loop iterations at 3.80/3.84 used SCS (eps 3e-5, 30k
iters) and produced NON-MONOTONE, infeasible λ values (9.28 → 9.45 → 9.48 → 8.52 at 3.80 with
+0.2…+0.7 oracle violations; 6.77 at 3.84 with +2.3): SCS at this accuracy is unusable for this
geometry, and every quoted number above is from Clarabel re-solves on the accumulated rows.

**Bigger-R control (diag_R2, s = 3.84).** R = central disc radius 0.9 (covers the whole ¼-pinwheel
ring; k = 277 — the A07 atoms are centrally dense, no radius gives 150 < k < 250): Clarabel died
again on memory (6.0 GB allocation, cone 278 with 2600+1400 rows). The "enlarge R" hypothesis is
NOT testable in the convex (k+1)-cone form on this machine: the practical envelope is k ≲ 150 with
≲ 4k diag + ≲ 2.5k pair rows. Enlarging R further needs either the D4-block-diagonalised cone (the
R-atom action splits the (k+1)-cone into ~k/8-sized isotypic blocks — engineering exists in
A16/theta_sdp, not done here) or Burer–Monteiro with sign hinges (A17-style; loses "stall is
meaningful").

**Graph-class diagnostic (graph_class.py, running).** Even with ALL cross terms free (R =
everything) and the pair constraints imposed on the exact finite non-edge set of the A15 c384
graph (where true ϑ′ = 10.38), the BM solver maintains feasibility at the λ-floor 10.35 through
27k+ exact pair rows with the max pair violation declining (+0.47 → −0.52 over 18 its; target
≤ −1). (final value below.)

## 5. LP floor at 3.84 (task 5)

(rational fractional packing of value ≥ 11, exact cell B&B feasibility)

## 6. Verdict

1. **λ < 11 at s = 3.84 is NOT reached; the hybrid class as built buys essentially NOTHING over
   the automatic class.** The clean, like-for-like numbers (identical row sets, Clarabel, D4-
   invariant, δ_p = 1e-3): 3.84: hybrid 11.14579 vs F=0 11.14406 (F "buys" −0.0017 = the margin
   cost); 3.80: hybrid 10.50369 vs F=0 10.50615 (+0.0025 gross ≈ +0.005 pre-margin, vs the 0.086
   needed to reach τ*(3.80)). In both runs the optimal F is genuinely nonzero (half its entries
   positive, |F|max 0.36–0.55) — the mechanism EXISTS but the localised pair constraints price it
   at exactly its diagonal benefit. **Gate (b) fails**, and by the gate's own logic the 3.84 target
   was already dead at that point.

2. **Why (mechanism, documented in §4):** the automatic optimum's tight set is a coverage≈1
   continuum spanning the WHOLE container (corners, wall slide-bands, interior mid-tilt — exactly
   the support of the value-11 fractional packing in §5). An R-block with k ≲ 150 atoms covers one
   patch of it; the SDP uses F to relieve that patch and the supremum re-pins on the rest. For F to
   lower λ globally, R must cover essentially the whole tight structure — k ~ 600+, which is out of
   reach for the (k+1)-cone convex form (Clarabel memory death at cone ≳ 250–300; SCS too
   inaccurate at these scales: non-monotone λ, +0.4…+2.3 oracle violations — every SCS "gain" we
   observed was solver junk).

3. **Is the whole kernel-class programme (indicator features on these atoms) capable of 10.38 at
   all?** Partial answer (graph_class.py, exact finite pair oracle on the A15 c384 graph where
   ϑ′ = 10.38, LP = 11.000): with ALL cross terms free, the A17-validated BM solver keeps the
   pattern class FEASIBLE at λ = 10.35–10.4 through ~30k accumulated exact pair rows (max pair
   violation declining +0.47 → −0.40 over 19 iterations, target −1). Not yet oracle-clean at
   write-up, but the trend is that the 1181-atom pattern class on the GRAPH sits near ϑ′ ≈ 10.4,
   NOT near 11 — i.e. the feature basis is NOT intrinsically too weak on the discretisation; what
   kills the continuum runs is the combination of (a) the continuum tight-cell continuum (grid→
   continuum risk R1, which A17 §4b had already implicated) and (b) the D4-invariant convex
   machinery ceasing to scale exactly where the needed cross-term support (most of the container ×
   most of the container) begins.

4. **Honest programme assessment.** After A18 (automatic class ⊨ LP floor, theorem) and A19
   (hybrid R-block buys ~0.002–0.005 at k ≤ 150; bigger k not solvable convexly today), the
   remaining kernel-shaped moves are: (i) block-diagonalise the R-cone (D4 isotypics of the R-atom
   action) to push k to ~600 in the convex form — engineering, no new mathematics, the honest next
   step if the kernel route is to continue; (ii) A17-style BM on the full hybrid with sign hinges
   (scales to k = m = 1181 but reintroduces "is the stall real?"); (iii) leave the pattern class:
   smooth features interpolating the discrete duals (A17 §6.3 route 2), still untested. What A19
   rules out: any expectation that a SMALL sliver-localised unrestricted block turns the automatic
   class into a sub-11 certificate — the ¼-cheat's kernel-killing cross terms are not localised;
   they live wherever the LP's tight structure lives, which at 3.84 is everywhere.

5. **Verification burden (for the record, had λ < 11 worked):** with the k = 148 central R,
   only 9.87 % of random disjoint admissible pairs are R-meeting (both centres provably within
   1.163 of the container centre; measured max 1.146); the (ii)-verification cell-pair table
   shrinks ~10× vs A17's full pair space (46 % of placements meet R; disjointness anti-correlates
   with both being central). One-vector rational PSD certificates do NOT apply to hybrid members
   (M is no longer a Z-matrix); the (k+1)-cone Schur reduction (H3) is the rational-PSD route
   (LDLᵀ of a 149×149 matrix + per-atom scalar checks) — that part of the plan worked and is
   recorded for reuse.

## 5. τ*(3.84) ≥ 11 — **PROVED (exact rational verification PASS)**

**lp_floor_384.json: 18 closed unit squares with rational centres (den 2^20) and exactly-rational
directions (cos, sin from rational tan(θ/2), c² + s² = 1 exactly), weights ∈ {1, ½} summing to
EXACTLY 11; the exact Fraction B&B (quadtree over [0, 96/25]², box passes iff the exact SAT-active
weight sum is ≤ 1) PASSES: 10,009 boxes, max depth 15, 0 undecided (results/lp_floor_verify.json).**
Structure: 4 corner squares (weight 1) + 10 upright ½-slide placements along the walls/interior +
the 4-fold interior pinwheel at 61.5° (weight ½ each) = 4 + 7 = 11. By weak duality (§3b) every
blocking measure at s = 3.84 has total mass ≥ 11: **τ*(3.84) ≥ 11 exactly — A18's collapse
theorem now gives, fully rigorously, λ ≥ 11 for every automatic-class kernel at 3.84** (previously
only the float statement τ*(3.84) = 11.02 was available). What made it work: columns snapped at
den 2^20 (den 4096 destroyed the sliver geometry and created 1.5-cover coincidence lines), η =
2^-16 inflation in the LP (separates every coincidence so the exact B&B terminates at depth 15),
edge-line probes in the float scan, and exact-B&B failures fed back as LP points.

## 5b. build history (task 5)

The LP/verify loop is sound end-to-end (weak-duality statement §3b; exact rational B&B with exact
SAT; feedback of undecided boxes into the LP point set) and caught two real soundness bugs that a
float-only pipeline would have shipped: (i) the closed-cover semantics violation of the raw c384
¼-structure (touching-line cover 1.125 at x = 1.0), (ii) grid-snapped edge coincidences creating
1.5-cover lines invisible to a 0.004 float scan (fixed with explicit edge-line probes). Two full
LP+verify rounds produced rational candidates of total EXACTLY 11 (19 placements: 3 × weight 1 +
16 × weight ½), but at η = 1/4096 the inflated-LP ceiling is ≈ 11.000 exactly (inflation ≈ moving
to s_eff 3.832 where τ* ≈ 11.00), leaving zero rounding headroom; the final run uses η = 1/16384
(s_eff ≈ 3.838, τ* ≈ 11.017, headroom ~0.017 ≫ 2^-18-rounding loss) with the A07 3.84 dual packing
(value 11.02) as columns. A column-pool cap was then diagnosed: every snapped/jittered pool tops out at ν* = 11.000000
EXACTLY (the ¼/½-structures achieve 11 on an open neighbourhood of placements — A10's box
plateau — while the 11.02 excess lives at unsnapped sliver geometry); the final run therefore
banks on a clean dyadic vertex at exactly 11, which round 0 of loop4 delivered and the exact B&B
PASSED (§5).

## 7. Files / reproduce

- hybrid.py — the diag+R-block class (H1–H4): enrichment atoms, Region, HybridSDP (convex,
  (k+1)-cone Schur PSD, D4 orbit variables), HybridKernel (kdiag/u_single/kpair/meets_R shims).
- full_sdp.py — the D4-invariant FULL hybrid in pair-orbit coordinates (sign constraints = variable
  bounds) + mass-preserving atom coarsening; used for V3-corrected validation.
- validate.py, v3b_check.py, v3c_layer.py, sizing_test.py, autocost.py — §2 validation suite
  (identities, automaticity, PSD reduction, D4-invariance pitfall, layered class, coarsening cost).
- explore_R.py, burden.py — §3 R data and H6 quantification.
- run_hybrid.py — driver (gates, R selection, cutting-plane loop, resumable state);
  `python run_hybrid.py --s 3.84 --atoms a07_384 --tag h384 --iters 8 --kcap 148` (+ --resume).
- diag_F.py — the decisive same-rows F-on/F-off comparison from a saved state; logs/diag_R2.log =
  the bigger-R control.
- oracles.py — generalised ratio scan + localised pair oracle (R-meeting tangent sampler, direct
  pattern-search pair polish).
- graph_class.py — the exact-graph pattern-class diagnostic (BM + exact finite pair oracle).
- lp_floor.py — task 5 pipeline; lp_floor_384.json; `python lp_floor.py --loop`.
- results/: h384.json/_state.npz, h380.json/_state.npz, diagF_*.json, validate.json, autocost.json,
  burden.json, gclass384.json, lp_floor_verify.json; logs/: h384.log, h380.log, gclass384.log,
  lp_floor_loop*.log, diag_R2.log.
- Machine lessons recorded: D4-invariance vs representative rows (§1b); Clarabel PSD-cone memory
  wall (~cone 250+ with dense quad rows ⇒ 6–9 GB alloc death, silent exit 0); SCS eps 3e-5
  unusable here; runaway child processes must be killed by PID (TaskStop kills only the shell).
