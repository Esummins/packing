# A18-restricted-kernel — the automatic-(ii) kernel class at s = 3.84

Owner: SDP postdoc (A18). 2026-08-19. Status: **done-negative, with a THEOREM: the goal is
provably unreachable.** The restricted class D2 (and every no-pair-verification variant of it)
collapses to a "two-measure LP" whose optimum equals the plain Theorem-1 LP value τ*(s); hence
λ ≥ τ*(3.84) = 11.02 > 11 for every member, and the ceiling of the whole automatic-(ii) kernel
programme is the LP ceiling ≈ 3.83. Proof in §3, machine validation in §4, full-scale numerics
(calibration at 3.80 + optimised runs) in §5, consequences and what still escapes in §6.

GOAL (as dispatched). Push A17's discovery D2 — M = [[1, −wᵀ], [−w, τ·diag(w) + C]] with
C ≤ 0 entrywise off-diagonal makes condition (ii) automatic — to λ < 11 at s = 3.84.
OUTCOME. The goal fails not numerically but structurally; the failure proof is short, exact,
and closes this entire branch of the programme (no float attack, no cell B&B, no Lean phase
will ever be needed for it). The two useful by-products: (a) a one-vector rational PSD
certificate for every kernel in the class (no LDLᵀ needed — §3d), and (b) a sharp
characterisation of WHERE the pair-side effort must be spent instead (§6).

## 1. Class definition and the automatic-(ii) argument (rigorous)

Setting as in A17 §1–2: placement space P_s (closed unit squares Q(x) ⊂ [0,s]², x = (cx,cy,θ)),
atoms p_1..p_m ∈ [0,s]² with weights w_p > 0 (D4 orbit-constant), coverage pattern
a_p(x) = 1[p ∈ Q(x)] (closed square), mass m(x) = wᵀa(x), assumed > 0 on all of P_s.
Normalised indicator features φ(x) = (1, a(x)/m(x)) ∈ R^{m+1}.

**Class D2 (restricted / automatic-(ii) class).**
  M = [[1, −wᵀ], [−w, D]],  D symmetric with D_pq ≤ 0 for all p ≠ q,  M ⪰ 0.
(The dispatch's parametrisation D = τ·diag(w) + C, C ≤ 0 off-diagonal, C diagonal free, is the
same set: D's diagonal is unconstrained, D's off-diagonal is exactly C's.)

**(a) Strictly disjoint closed squares share no atom.** Atoms are points. If Q(x) ∩ Q(y) = ∅
(as closed sets) then no point lies in both, so supp a(x) ∩ supp a(y) = ∅. Touching squares
(SAT depth = 0) CAN share a boundary atom — these are exactly the pairs exempted by A17's
discovery D1 (the bridge's scale-shrink step produces pairwise disjoint CLOSED squares, so (ii)
is only ever needed for strictly disjoint pairs; see A17 §1(a), calibrated there numerically).

**(b) (ii) holds for every disjoint pair, by algebra.** For x, y with pattern-disjoint supports:

  K(x,y) = φ(x)ᵀMφ(y)
         = 1 − wᵀa(y)/m(y) − wᵀa(x)/m(x) + a(x)ᵀD a(y)/(m(x)m(y))
         = 1 − 1 − 1 + Σ_{p∈supp a(x), q∈supp a(y)} D_pq /(m(x)m(y))
         ≤ −1,

because every term in the double sum has p ≠ q (p = q is impossible when the supports are
disjoint) and D_pq ≤ 0. By (a) this covers ALL pairs of strictly disjoint closed squares —
every pair the bridge needs. No pair oracle, no 6-D verification, no geometric analysis:
condition (ii) is a one-line consequence of the sign pattern of M. (Equality K = −1 holds iff
the cross-terms vanish, e.g. whenever D is diagonal.) Machine check: theory_check.py T2
(2460 random strictly disjoint pairs: max |K+1| = 3.3e-16 for diagonal D; K ≤ −1 for generic
Z-sign D with off-diagonal entries strictly below 0).

Note the sign constraint cannot be relaxed for any pair of STRICTLY INTERIOR atoms: call p, q
"separable" if two strictly disjoint admissible closed squares contain p and q respectively —
then D_pq > 0 breaks (ii) at that pair. For p with dist(p, ∂[0,s]²) > 0, every q ≠ p is
separable (tilted separating lines: if q is inward-adjacent, take a line through the gap with a
slope small enough that both slabs admit admissible unit squares; the construction needs only
p, q not exactly on the wall). The exceptional case — atoms EXACTLY on the container boundary,
whose "cap" ∩{Q admissible : p ∈ Q} is an inward unit segment (a 2-D lens at the corners, the
whole corner square [0,1]² for an atom exactly at a corner) — is handled in §3b(iii); none of
the atom sets used here contain boundary atoms (min wall distance 0.485–0.51 across cert380/
cert382/a07_384), so the clean theorem below applies verbatim to every run.

## 2. The diagonal in Schur form

Since M_00 = 1, M ⪰ 0 ⟺ S := D − wwᵀ ⪰ 0 (Schur complement). On the diagonal, using
wᵀa(x) = m(x) and (wwᵀ appearing in D = S + wwᵀ):

  K(x,x) = 1 − 2·wᵀa(x)/m(x) + a(x)ᵀD a(x)/m(x)²
         = −1 + a(x)ᵀS a(x)/m(x)² + (wᵀa(x))²/m(x)²
         = **a(x)ᵀ S a(x) / m(x)²  ≥ 0.**

The class constraint becomes: **S ⪰ 0 with S_pq = D_pq − w_p w_q ≤ −w_p w_q < 0 (p ≠ q)** —
i.e. S is a symmetric positive-semidefinite **Z-matrix** (nonpositive off-diagonal), with an
entrywise margin −w_p w_q. The problem "minimise λ = 1 + sup_x K(x,x)" is now entirely about
PSD Z-matrices.

The LP-form kernel (C = 0) is S_LP = τ·diag(w) − wwᵀ (τ = Σw): a(x)ᵀS_LP a(x) = τm(x) − m(x)²,
so K(x,x) = τ/m(x) − 1 and λ_LP-form = τ / m_min, m_min = inf_x m(x). (At 3.84 with A07's atoms:
τ = 11.020, m_min = 0.9687 ⟹ λ_LP-form = 11.376. A17 §6.2's "λ_LP-form = 12.38" is an
arithmetic slip — it added the 1 twice; the optimized-with-pair-rows A17 kernel at 11.13 beat
the LP form by ≈ 0.25, not 1.25.)

## 3. The collapse theorem: the class optimum equals the LP, always

**Proposition 1 (dominance certificates exhaust the PSD Z-matrices).**
(⇐) If S is a symmetric Z-matrix and there is u > 0 with Su ≥ 0, then S ⪰ 0.
Proof: B := diag(u) S diag(u) has B_pq ≤ 0 (p≠q) and row sums u_p(Su)_p ≥ 0, so B is weakly
diagonally dominant with nonnegative diagonal ⟹ B ⪰ 0 (Gershgorin) ⟹ S ⪰ 0.
(⇒, up to limits) If S is a PSD symmetric Z-matrix then for every ε > 0, S + εI is a positive
definite Z-matrix, hence a nonsingular symmetric M-matrix, hence (S+εI)^{-1} ≥ 0 entrywise with
strictly positive diagonal; u_ε := (S+εI)^{-1}·1 > 0 satisfies (S+εI)u_ε = 1 > 0. So every
feasible S is the ε-limit of dominance-certified feasible matrices, and
K_{S+εI}(x,x) = K_S(x,x) + ε·|supp a(x)|/m(x)² → K_S uniformly (patterns are finite, m ≥ m_min > 0).

**Proposition 2 (pointwise monotonicity).** Let S satisfy Su ≥ 0 for some u > 0 and
S_pq ≤ −w_pw_q (p≠q). Define the boundary matrix S_u by
  (S_u)_pq = −w_p w_q (p ≠ q),  (S_u)_pp = w_p (W − w_p u_p)/u_p,  W := Σ_q w_q u_q.
Then for EVERY 0/1 vector a:  aᵀ S a ≥ aᵀ S_u a.
Proof: with B = diag(u) S diag(u) and ã = a/u (entrywise),
  aᵀSa = ãᵀBã = Σ_{p<q} (−B_pq)(ã_p − ã_q)² + Σ_p u_p(Su)_p ã_p²,
(the standard Laplacian-type decomposition; both identities are entrywise checks). Every
coefficient is bounded below: −B_pq = −u_pu_qS_pq ≥ w_pw_qu_pu_q and u_p(Su)_p ≥ 0; every
quadratic factor is ≥ 0. Replacing the coefficients by their lower bounds gives exactly aᵀS_u a
(same decomposition with slack 0), which also shows S_u ⪰ 0 and S_u feasible (its off-diagonal
sits exactly at the bound). ∎ (Machine check: theory_check.py T3.)

**Proposition 3 (two-measure identity).** For 0/1 patterns,
  aᵀ S_u a = W · ṽ(a) − m(a)²,  where ṽ(a) := Σ_{p∈a} w_p/u_p,
hence  K_u(x,x) = W·ṽ(x)/m(x)² − 1,  and the corresponding M has D = diag(w_p W/u_p):
**the optimal restricted kernel has C ≡ 0 off-diagonal — a purely diagonal generalisation of
the LP form** (u ≡ 1 recovers it exactly). (Machine check: T1/T4, error 7e-15.)

**Theorem (collapse + LP cap).** For every kernel in class D2 (any w > 0, any feasible D):
  λ := 1 + sup_{x∈P_s} K(x,x)  ≥  τ*(s),
where τ*(s) is the optimum of the Theorem-1 covering LP (inf Σν over atomic measures ν with
ν(Q) ≥ 1 for every placement Q). Moreover the bound is tight: w = an (near-)optimal LP measure,
u = 1 gives λ = Σν/inf_x ν(Q(x)) → τ*(s).
Proof: By Props 1–3, inf over the class of sup_x K = inf over u > 0 of sup_x [W·ṽ(x)/m(x)² − 1].
Fix u and set ν_p := w_p u_p ≥ 0 and v_p := w_p/u_p, so w_p = √(ν_p v_p). By Cauchy–Schwarz on
each pattern: m(x) = Σ_p √(ν_p v_p) a_p(x) ≤ √(ν(x) v(x)) with ν(x) = Σν_p a_p, v(x) = ṽ(x).
Hence  1 + K_u(x,x) = W·ṽ(x)/m(x)² ≥ (Σν)·v(x)/(ν(x)v(x)) = Σν/ν(x),  so
  λ ≥ sup_x Σν/ν(x) = Σν / inf_x ν(x) ≥ τ*(s)
(the measure ν/inf_x ν(x) is blocking, so its total mass is ≥ τ*(s)). ∎

**Consequences.**
- λ < 11 at s = 3.84 is impossible in class D2: τ*(3.84) = 11.02 (A07). Even at 3.83,
  τ*(3.83) = 11.000 exactly — no strict margin. **The restricted-kernel ceiling is the LP
  ceiling ≈ 3.83**; the class buys back NOTHING of the LP's integrality gap. (Formally, the
  strict statement "τ*(3.84) ≥ 11" is certified by any rational fractional packing of value 11 —
  the A10/A12 ¼-structures are exactly that; A07's converged LP puts it at 11.02.)
- The intuition in the dispatch ("C < 0 entries reduce K(x,x) wherever a placement covers ≥ 2
  co-occurring atoms") is correct at FIXED diagonal, but the PSD constraint prices the diagonal
  exactly: along every dominance decomposition, a co-occurring pair's gain −2|C_pq| is paid for
  by diagonal increases |C_pq|(u_p/u_q + u_q/u_p) ≥ 2|C_pq|, with equality iff u_p = u_q. Off-
  diagonal mass is never strictly profitable, and against placements covering only ONE endpoint
  it is strictly harmful.

### 3b. The no-pair-verification generalisations are blocked too

(i) **Border scaling M_00 = σ < 1** ((ii) then needs σ ≤ 1): Schur gives S = D − wwᵀ/σ ⪰ 0 with
S_pq ≤ −w_pw_q/σ; K(x,x) = (σ + 1/σ − 2) + aᵀSa/m(x)². Applying the theorem to w′ = w/√σ:
λ ≥ σ − 1 + τ*/σ, which on (0,1] is minimised at σ = 1 (τ* > 1). Blocked.

(ii) **Free border v ≠ w and free normalisation g** (φ = (1, a/g(x)), g(x) = gᵀa(x), border −v):
(ii)-automatic needs 1 − ρ(x) − ρ(y) + (≤ 0) ≤ −1 with ρ(x) = vᵀa(x)/g(x), i.e. the pointwise
3-D-verifiable condition ρ(x) ≥ 1 on all of P_s. Then K(x,x) = (1−ρ(x))² + aᵀSa/g(x)² with
S = D − vvᵀ ⪰ 0, S_pq ≤ −v_pv_q. Two-measure reduction with ν = v∘u: aᵀSa ≥ (Σν)·μ(x) − v(x)²
(μ = v/u), and per-pattern Cauchy–Schwarz μ(x) ≥ v(x)²/ν(x) gives
  K(x,x) ≥ (1−ρ)² + ρ(x)²·(Σν/ν(x) − 1) ≥ Σν/ν(x) − 1   (using ρ ≥ 1),
so again λ ≥ τ*(s). Blocked. (If instead one only requires the pairwise condition
"ρ(x) + ρ(y) ≥ 2 for all disjoint pairs", the pointwise bound degrades to λ ≥ 2 − inf ν/Σν —
but that condition is a genuine 6-D verification again, i.e. outside this class by definition;
and in practice disjoint pairs of low-ν placements exist, forcing ρ ≥ 1 on the tight set anyway.)

(iii) **Positive off-diagonal entries for "inseparable" atom pairs.** Inseparable pairs DO
exist, but only when an atom p lies exactly on the container boundary: then every admissible
square containing p contains p's inward unit segment (mid-wall; a 2-D lens near corners), so
for q on that segment the pair (p,q) never splits across disjoint squares in either order
(a_p(x) ≤ a_q(x) pointwise) and D_pq > 0 is permitted — a genuine escape from the Z-sign class,
of exactly the Stromquist/A05 wall-exemption type. It buys nothing, by a closure argument:
a boundary atom is contained only in squares whose boundary passes through it — a measure-zero,
2-parameter family of placements. Every full-measure placement pattern excludes all boundary
atoms; running the Cauchy–Schwarz chain of the theorem on the interior sub-measure ν_int over
those placements (the dominance decomposition still lower-bounds all separable-pair terms,
and the inseparable-pair discounts touch only patterns containing q with the W-cost
w_p u_p ṽ(x) ≥ discount whenever the pattern contains anything besides q) gives
λ ≥ Σν_int / inf ν_int(x) over a dense full-measure family of placements; since patterns of
wall-touching placements are limits of interior ones (up to further measure-zero atom-on-∂Q
coincidences), ν_int/inf is still blocking in the limit and λ ≥ τ*(s) again. (Sketch-level
rigour: the ε-details of the limit are routine but not written out; irrelevant for every atom
set used here, which has no boundary atoms — §1.)

So: **every kernel whose condition (ii) is discharged by a sign/pointwise argument (anything
verifiable in 3-D) is worth at most the LP.** Passing 11 at 3.84 REQUIRES spending verification
effort on genuine 6-D pair constraints — exactly the part D2 was designed to delete.

### 3c. Where the strength went (reading)

The chain has exactly two inequalities, and both are equalities at u ≡ 1, w = LP measure:
the class CAN place its λ anywhere in [τ*, τ/m_min] but no lower. The LP's integrality gap at
3.84 is carried by the ¼-structure fractional packings (A10/A12): weight-11 mixtures of
pairwise-OVERLAPPING placements. A kernel beats the LP only by going strictly below −1 on...
nothing (pairs at −1 are already tight) — the actual mechanism (visible in A15/A16's discrete
duals Z: non-edge entries mean −1.09, max −1.0000) is K < −1 on most disjoint pairs while the
PSD mass concentrates against the odd-cycle structure of the ¼-cheat, which REQUIRES
K(x,y) > −1 + something on some overlapping non-sharing pairs — i.e. positive cross-terms
between atoms of overlapping squares — i.e. D_pq > 0 somewhere. The Z-sign constraint deletes
precisely the load-bearing entries.

### 3d. By-product: one-vector rational PSD certificates

For every kernel in the class in two-measure form (D = diag(w_p W/u_p)), M itself is a
symmetric Z-matrix (border −w ≤ 0, off-diagonal of D zero) and
  M·(W, u_1, …, u_m)ᵀ = 0  exactly.
So M ⪰ 0 is certified by one rational matrix–vector product and Gershgorin/diagonal-dominance
after scaling — no rational LDLᵀ of an 1182² matrix. (Moot for the dead route, but it also
applies verbatim to the plain LP certificates viewed as kernels, and to any future class member
pinned to the Z-boundary; recorded for A19+.)

## 4. Machine validation of §3 (theory_check.py, medium_check.py, results/*.json)

Tiny instance (theory_check.py: 28 atoms, s = 3.8, 3957 placements, 2460 strictly disjoint
pairs, 130 deduped pattern rows), all PASS:
- T1/T4 identities (K(x,x) = aᵀSa/m² = W·ṽ/m² − 1 vs A17's kdiag): max error 7.1e-15; eig min
  of M = −3.5e-16.
- T2 (ii)-automatic: diagonal D ⟹ K = −1 exactly on all disjoint pairs (3.3e-16); generic
  Z-margin S ⟹ max K over disjoint pairs = −1.263 ≤ −1.
- T3 monotonicity: min over patterns of aᵀ(S_u+G)a − aᵀS_u a = +1.53 ≥ 0.
- T5 collapse: restricted SDP (cvxpy/Clarabel, exact class) λ = 14.755760 vs two-measure
  u-optimum (softmax L-BFGS, GP-convex) λ = 14.755886 — **match 1.3e-4**; row-LP τ* = 14.000000,
  SDP ≥ τ* (+0.756 at the arbitrary fixed w), and with w = ν_LP the SDP value is **14.000002 =
  τ* to 2e-6** — the class optimum IS the LP optimum.

Medium instance (medium_check.py: 96 atoms, 220 pattern rows from real placements, generic
orbit-constant weights, non-symmetrised row sample):
- restricted SDP λ = 17.057096; full-θ two-measure GP λ = 17.057133 (**match 4e-5**);
- constructive check of Prop 1: u_ε = (S* + εI)⁻¹1 from the SDP's own optimal S* plugged into
  the two-measure formula gives 17.079 / 17.059 / 17.0573 / 17.057097 at ε = 1e-2…1e-6 — the
  collapse limit realised numerically (the optimal S* is singular; u_ε's profile converges).
- Two pitfalls documented (both hit live): cvxpy fancy-indexing for the sign constraints
  silently under-constrains (use cp.upper_tri; the bad form gave a fake 16.77 whose M violated
  the signs); and the orbit-constant u parametrisation is only WLOG when the row set is
  D4-closed / canon-deduped orbit representatives — on this arbitrary sample the orbit-
  restricted GP gives 18.04 ≠ 17.06 while the full-θ GP matches. run_opt.py's rows are
  canon-deduped orbit representatives and the continuum problem is D4-invariant, so its
  orbit-constant parametrisation is exact there (group-averaging + convexity in θ = log u).

## 5. Full-scale numerics (run_opt.py, two_measure.py)

Machinery: by §3 the class optimum at fixed (atoms, w) is inf over u of
sup_x [W·ṽ(x)/m(x)²] — a geometric program, solved globally by softmax/L-BFGS in θ = log u
(one variable per D4 atom orbit), with cutting-plane rows generated by A17's diag oracle
(dense scans + admissible-boundary sweeps + polish) plus a two-measure prefix-sum ratio scan
(both measures histogrammed in the rotated frame, A07-style). No pair side exists at all —
(ii) is automatic. λ values below are "certified in float" = strongest-attack suprema.

| run | s | atoms (m, τ) | λ(u=1) LP-form kernel | λ(u*) class opt (float attack) | gain | A07 τ*(s) = class floor |
|---|---|---|---|---|---|---|
| r380b | 3.80 | cert 3.80 (1069, 10.8016) | **10.618** (m_min 1.01733, wall cell) | **10.506** | −0.111 | 10.42 |
| r382  | 3.82 | cert 3.82 (1769, 10.9855) | **10.749** (m_min 1.02202, wall cell) | **10.725** | −0.024 | 10.62–10.72 |
| r384  | 3.84 | A07 LP (1181, 11.0201)   | **11.376** (m_min 0.968742 — reproduces A17's continuum cell exactly) | **11.179** | −0.197 | **11.02** |

Every number is theorem-consistent: τ*(s) ≤ λ(u*) ≤ λ(u=1) = τ/m_min. The u-optimisation
(= optimising C, by the collapse) DOES strictly reduce λ at every s — the dispatch's "key
scientific datum" exists — but the reduction is exactly the certificate-margin slack and stops
at the LP value: **at 3.84 the best kernel in the whole restricted class found in float is
11.179, and no member can be below 11.02.** λ < 11 needs s where τ*(s) < 11, i.e. s < 3.83:
the class crossing of 11 IS the LP crossing. 3.85 not run (pointless by the theorem).

Details/caveats:
- Calibration gate: the LP-form identity λ = τ/m_min is exact (A17's calibration point
  (1.2145, 2.4928, 45°) re-evaluates to coverage 1.029676, K = 9.4903 ✓; the r384 u=1 supremum
  reproduces A17's continuum minimum coverage cell 0.968742 to 6 digits via an independent
  covscan). Our boundary attacks found SHARPER wall cells than A17's calibration at 3.80
  (coverage 1.01733 at (3.1544, 2.3524, 20.92°)-type admissible-boundary placements vs their
  1.0297): A17's reported λ_LP(3.80) = 10.49 was an attack under-estimate, not an identity
  error (A08's exact verifier only asserts ≥ 1; the binding cells at 3.80/3.82 are wall cells).
- Oracle completeness: the diag oracle plays whack-a-mole with narrow 45°-diagonal cells at
  3.84 (a basin at (1.273, 1.399, 45°) was found only by specific random seeds; after feeding
  it back the optimum rebalanced to 11.179 with binding cells at (1.396, 1.321, 27.7°) and
  (1.344, 2.431, 24.5°) — interior mid-tilt, the ¼-structure region again). λ(u*) is therefore
  "best found by the strongest attack" (loop rows + 3-seed final attack + the full A17 hard-cell
  inventory + covscan + polish, crosscheck_384.py); the class optimum for these atoms lies in
  [11.02, 11.179]. For the paper-grade statement only the theorem floor matters.
- The GP solves are globally optimal on their row sets up to softmax/L-BFGS slack ~1e-3
  (validated to 4e-5 against the SDP at medium scale, §4).

## 6. Verdict and what remains

1. **The dispatched goal is impossible**: λ ≥ τ*(3.84) = 11.02 for every kernel in class D2
   and its 3-D-verifiable generalisations (§3, §3b). No atom placement, no weight tuning, no
   C-optimisation changes this. The restricted-kernel programme ends here, permanently.
2. The result is a sharp negative complement to A17: the full kernel class (pair side verified
   in 6-D) demonstrably goes below τ* (A17 row sets at 11.05–11.13 < 11.376 = τ/m_min, and the
   discrete ϑ′ says the true kernel optimum is ≈ 10.4), but EVERYTHING it gains over the LP is
   carried by positive off-diagonal kernel mass on overlapping non-sharing pairs (§3c).
3. **Viable A19 shape (hybrid, quantified pair side):** keep the Z-sign structure globally,
   allow D_pq > 0 ONLY for atom pairs p,q both inside the mid-tilt sliver-overlap region
   (A17 §6.1: the 220k non-sharing edges, median SAT depth 0.094, all interior mid-tilt).
   Then (ii) is automatic for every disjoint pair EXCEPT those whose two squares both meet the
   positive-support region — the 6-D verification shrinks to pairs of mid-tilt squares in a
   small (c,θ)-window, a cell-pair table orders of magnitude smaller than A17's full pair space.
   The class optimum then interpolates between τ* and the full-kernel value; whether it passes
   11 at 3.84 is exactly the question "is the ¼-cheat killable by cross-terms supported on the
   region that carries it" — A16's node duals (30–45 dominant eigenvectors, all mid-tilt) say
   plausibly yes. This is the only kernel-shaped route left; its cost is dominated by the
   REDUCED pair table, not by the diagonal.
4. Alternative fallback stays as before (A16): the 14-node ϑ′ tree with per-node kernels —
   but every node kernel faces the same theorem: node certificates below the node budget also
   need genuine pair verification (the node LPs sit AT the budget). The theorem says the
   pair-free shortcut does not exist at the nodes either.

Honest remaining-gap list (what this attempt does NOT settle):
- The theorem's boundary-atom case (§3b(iii)) is proved at sketch level (closure/measure-zero
  argument); it is vacuous for every atom set in the repo but should be written out if the
  collapse theorem is ever published.
- τ*(3.84) = 11.02 is A07's converged float LP; the strict statement τ*(3.84) ≥ 11 (which makes
  the impossibility fully rigorous) needs one rational fractional packing of value 11 at 3.84 —
  the A10/A12 ¼-structures are exactly that and rounding one is a half-day task, never yet done
  at 3.84 specifically.
- λ(u*) values are strongest-float-attack suprema; the diag oracle demonstrably misses narrow
  45° cells on first pass (§5), so the fixed-w class optima are bracketed, not pinned:
  [10.42, 10.506], [10.62–10.72, 10.725], [11.02, 11.179]. Irrelevant to the impossibility.
- The hybrid class of §6.3 (positive off-diagonal only on mid-tilt sliver pairs + reduced 6-D
  verification) is designed but not built: its value at 3.84 is the open question A19 should
  answer, and nothing in this attempt bounds it away from < 11.

## 7. Files / reproduce

- theory_check.py — machine validation T1–T5, tiny scale (§4); `python theory_check.py`.
- medium_check.py — SDP == GP at 96 atoms + the constructive u_ε check (§4).
- two_measure.py — TwoMeasureKernel (kdiag/u_single shims for A17's diag oracle), convex
  softmax u-optimiser per D4 orbit, exact-reranked two-measure ratio scan, attack wrapper.
- run_opt.py — driver: `python run_opt.py --s 3.84 --atoms a07_384 --tag r384 --iters 14`
  (atoms ∈ {cert380, cert381, cert382, a07_384}); state saved per iteration; `--resume`;
  `--inject file.npy` adds external placements as rows (used for the A17 inventory).
- crosscheck_384.py — post-hoc attack of the r384 kernel (and u=1) on A17's stored diag rows,
  their attack argmax, and a full-strength covscan; logs/crosscheck_384.log.
- results/: theory_check.json, medium_check.json, r380.json (first weak-loop run, superseded),
  r380b.json, r382.json, r384.json, *_state.npz (resumable), *_theta.npy (optimal log-u per
  orbit), inject_384.npy, covscan_anchor.json.
- logs/: r*.out (runs), crosscheck_384.log.
- Survived one methodological near-miss (the medium-check discrepancy) and multiple oracle
  under-estimates; every headline number above is cross-anchored at least two independent ways.
