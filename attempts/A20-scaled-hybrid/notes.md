# A20-scaled-hybrid — the hybrid kernel with R = the full tight structure (D4-block-diagonalised R-cone)

Owner: SDP postdoc (A20). 2026-08-19. Status: **done-negative on the lambda < 11 target**
(step-1 engineering delivered and validated; gate (b) fails with the localisation hypothesis
refuted; an A19 solver artefact found and corrected en route; see Verdict SS3).

GOAL (dispatch). Execute A19's recommended steps 1–2: scale the hybrid kernel class
(Z-sign globally, free block on R) so that R covers the FULL tight structure (k ≈ 600 R-atoms),
by D4-block-diagonalising the (k+1)-cone Schur form (isotypic blocks ≈ k/8, E ≈ k/4 — inside
Clarabel's envelope). Gates: (a) A19's k = 148 values reproduced by the block form on identical
rows to 1e-5; (b) λ(3.80) < τ*(3.80) = 10.42 with the full-tight-set R (the signal the class
escapes the LP floor; A19's k = 148 got +0.0025 of the needed 0.086 — if full-tight R still gets
< 0.02, the LOCALISATION is not the obstruction: stop and say so). Then 3.84 (target λ < 11;
discrete prediction 10.38), optionally + ~40 smooth D4 features from the discrete duals.

## 1. Engineering: the block-diagonalised (k+1)-cone (block_sdp.py)

Setting = A19 §1 (class H, (H1)–(H6)). The Schur cone
Z = [[diag(g_R)+F, w_R],[w_Rᵀ, 1−Σ_N w²/g]] is D4-invariant BY CONSTRUCTION (g orbit-constant,
F = Σ_o f_o A_o over D4 pair orbits, w orbit-constant, border node fixed), so with the extended
permutation action of D4 on {R-atoms} ∪ {border} (border = fixed point, hence A1-only):

    Z ⪰ 0  ⟺  Z_ρ := (1/d_ρ) Σ_r T_ρ^(r)ᵀ Z T_ρ^(r) ⪰ 0  for each irrep ρ ∈ {A1,A2,B1,B2,E},

with T from A16's `theta_sdp.symmetry_basis` (isotypic projectors, orbit-wise). Block sizes
m_ρ ≈ k/8 (m_A1 gets +1 for the border), E ≈ k/4 with multiplicity 2. Implementation:
precomputed sparse affine maps per irrep — gmap (m_ρ² × n_orb): coefficient of each atom-orbit
g in vec(Z_ρ); fmap (m_ρ² × n_forb): coefficient of each F-pair-orbit (each row of T has ≤ d_ρ
nonzeros, so T ρᵀA_oT ρ has ≤ 4 entries per member pair — the maps stay sparse); tailmat
(A1 only) and the constant border block. cvxpy constraint = reshape(map @ var) symmetrised ⪰ 0.

Extras: vectorised row-coefficient extraction (`_quad_forb_counts`/`_cross_forb_counts` via
`pair_oid[np.ix_]` + bincount — A19's per-row Python pair loops are O(|R∩x|²) per row and die
at k ~ 600), vectorised `rpair_orbits_fast`, and an optional F-support distance cutoff
`fdist` (√2 = the co-occurrence bound: atom pairs further than √2 apart never appear in any
diagonal row, so zeroing F there only removes pair-row/PSD freedom, not diagonal relief).

Validation (validate_a20.py):
- V0: `rpair_orbits_fast` partition == A19's `rpair_orbits` at k = 148 (1416 orbits). PASS.
- V1: eigenvalues of the dense (k+1) Z of a random class member == union of isotypic-block
  eigenvalues (E doubled): max err 1.9e-14. PASS.
- V2 (gate a): block-form solve on A19's saved h384/h380 rows vs A19's Clarabel numbers:
  h384 hybrid 11.145824 vs 11.145789 (+3.5e-5), F=0 11.144093 vs 11.144063 (+3.0e-5);
  h380 F=0 10.506136 vs 10.506152 (-1.6e-5). PASS (solver-tolerance level).
  **ANOMALY: h380 hybrid (F on) = 10.344876 vs A19's 10.503689 — the block form finds a value
  0.159 LOWER on identical rows, already below tau*(3.80) = 10.42.** One of the two solves is a
  solver failure; feasibility of the returned (g,F) is being verified directly (check_feas_h380.py:
  dense Z eigmin + exact row residuals). If it verifies, A19's "F buys nothing at 3.80" was a
  full-cone Clarabel artefact, not a property of the class.
- V2b (fdist = sqrt2): at h384 the cutoff is vacuous (R radius 0.455, all pairs < sqrt2) — same
  value, same n_forb. At h380 (wall-band R, radius 1.669) the cutoff removes 76 % of the F-orbits
  (1406 -> 342) and costs +0.147 (10.492 vs 10.345): distant F entries are NOT dispensable for a
  spread-out R => run the big-R production solves with FULL F support.

## 2. The A19 h380 gate ANOMALY (found during gate (a), verified)

The block form reproduces A19's h384 numbers, but on A19's own h380 rows (k = 148 wall-band R,
3544 diag + 2200 near-binding pair rows) it returns **lam = 10.344876**, 0.159 BELOW A19's
Clarabel value 10.503689 — and the returned point is a GENUINE class member, verified directly
from (g, f) (check_feas_h380.py): dense Z min eig +8.1e-8, max diag-row residual -1.1e-7, max
pair-row residual -4.2e-8, g_N > 0. Conclusion: **A19's full-cone Clarabel solve at h380 was a
silent solver failure (premature stall accepted as optimal); the hybrid class with even a k=148
wall-band R already achieves <= 10.3449 on those rows — below tau*(3.80) = 10.42.** A19's
"F buys +0.0025 at 3.80" is retracted; what F buys on rows is >= 0.161. (SCS at eps 2e-6 on the
same block problem returns 8.94 with +3e-2 violations — unusable, consistent with A19's lesson.)
The open question moves to the ORACLES: does the value survive the diag + localised-pair attack,
or is the row set simply unconverged (A19's h380 loop iterations were SCS junk, so it never saw
a real attack)? -> the b380 loop below.

## 2b. Runs

- b380 (s = 3.80, cert380 atoms, k = 308 R by binding-cover, radius 1.669 — hull spans the
  container, full F, n_forb = 6006, blocks {40,38,38,39,77}): cutting-plane trajectory
  (Clarabel block form, all solves optimal_inaccurate but solutions verified feasible):
  it0 10.4914 -> it1 10.4908 (viol d +0.91 / p +0.60) -> it2 10.4935 (+0.41/+0.63) ->
  it3 10.4961 (+0.27/+0.29) -> it4 10.5052 (+0.33/+0.33), rows 3089d/4799p.
  **The hybrid RE-PINS onto the automatic optimum at 3.80: lam climbs monotonically back to the
  F=0 value 10.5062 as the localised pair oracle feeds violations; the residual gain at it 4 is
  ~0.001 (still with open oracle violations, so the true equilibrium gain is smaller still).
  GATE (b) FAILS: nowhere near tau*(3.80) = 10.42 (needed gain 0.086).** Same-rows at the it-4
  final state (3089d/4799p): F=0 10.506131; F-on = 10.505163 on a subset of those rows (the it-4
  solve), so on identical rows **F buys <= 0.001 at 3.80 at the oracle equilibrium** — A19's
  conclusion stands once the rows are oracle-adapted; the 10.34 anomaly was a real value of an
  UNCONVERGED row set (A19's h380 rows were never attacked by a working solver+oracle loop),
  not of the class. The re-pinning mechanism, watched live: after F relieves the wall bands the
  binding diag cells move (it-1 attack max at 10.40, it-4 at 9.84 with fresh violations each
  round) and the localised pair oracle keeps finding R-meeting disjoint pairs at K = -0.37...-0.67
  (need <= -1); each batch prices F's relief away.
- b384 (s = 3.84, a07_384 atoms, kcap 600): inventory 6967 placements (4000 attack cands within
  0.5 + 925 near-binding A18 rows + A12/A17 + 265 LP-floor pts incl. jitters — the LP-floor
  structure alone touches ALL 1181 atoms); k = 597, n_forb = 22457, blocks {81,70,78,71,149}.
  **Clarabel memory death** ("memory allocation of 5.26 GB failed") at 4127 diag + 4949 pair rows:
  the k~600 envelope is NOT reachable even block-diagonalised with this row load on 32 GB.
  Solver envelope so far: k=308/5.9k f-vars/5.9k rows OK (~3 GB, 906 s); k=480/14.5k f-vars/5.2k
  rows OK (670 s); k=597/22.5k f-vars/9.1k rows dead.
- c384 (s = 3.84, kcap 480, row_cap 2200, pair_cap up to 4200): k = 480 of 1181 covering the
  full-tight-set inventory (incl. the exact LP-floor structure), n_forb = 14530, blocks
  {64,57,62,58,120}, R hull [0.51,3.33]^2 (radius 1.686 — the whole container). it-0 row value
  lam = 8.568290 (670 s) — VERIFIED a genuine class member on its rows (Zmin -6.1e-7, residuals
  <= 2.1e-7): with only 1800 pair rows the R-meeting pair space is barely constrained and the
  row value starts far below the continuum equilibrium. Cutting-plane trajectory:
  it1 8.5683 (viol d +12.2 / p +6.3!) -> it2 11.0764 (+3.0/+2.4) -> it3 11.0777 (+1.11/+1.09),
  it4 11.0838 (+1.13/+0.98) -> it5 11.0860 (+0.41/+0.78), rows 3701d/7066p (total 4121 s).
  lam crossed 11 the moment ~3000 genuine pair rows were in and was still climbing at stop.
  **Final same-rows comparison (identical 3701d/7066p rows): hybrid 11.085959 vs F=0 11.144051
  -> F buys +0.058092** — 34x the k = 148 gain (0.0017), so enlarging R DOES buy something at
  3.84, but the row value already exceeds 11 with both oracles still violated (the true value of
  the stopped kernel is higher still), and the trajectory is monotone towards the automatic
  value. For calibration: A17's full-class BM (R = all 1181 atoms in effect) equilibrated at
  11.05–11.13 — exactly the band our k = 480 row value sits in.

## Files

- block_sdp.py — BlockHybridSDP (subclass of A19's HybridSDP; isotypic PSD blocks, vectorised
  rows, fdist cutoff), rpair_orbits_fast.
- validate_a20.py — V0/V1/V2 gates.
- run_a20.py — driver: full-tight-set R selection (binding inventory = F=0 attack cands within
  0.5 + A12 images + A17 pair endpoints (no radius filter) + LP-floor placements w/ jitters at
  3.84), block solve, A17/A19-seeded cutting-plane loop, same-rows F on/off comparison.

## 3. Verdict

1. **Engineering delivered (step 1).** The D4-block-diagonalised (k+1)-cone works and is exact
   (V0/V1: partition identity, eig match 1.9e-14; V2: A19's h384 values reproduced to 3.5e-5 on
   identical rows). Solver envelope measured on this 32 GB machine (Clarabel, full F support):
   k = 308 / 6.0k f-vars / 5.9k rows: OK (906 s); k = 480 / 14.5k f-vars / up to 9.7k rows: OK
   (670–1400 s); k = 597 / 22.5k f-vars / 9.1k rows: memory death (5.26 GB alloc failure). So the
   block form buys roughly k <= ~500 in production (vs A19's k <= 150) — the "k ~ 600" of the
   dispatch is reachable only with fewer rows or more RAM. All quoted solves are
   "optimal_inaccurate" but every headline solution was verified feasible a posteriori from
   (g, f) to <= 2e-7 row residuals and Z eigmin >= -6e-7 (check_feas.py) — the values are real.

2. **A19 correction (found by gate (a)).** A19's h380 hybrid number 10.503689 was a SILENT
   full-cone Clarabel stall: on A19's own h380 row set the true class value is <= 10.344876
   (verified member), i.e. F buys >= 0.161 on those rows — BELOW tau*(3.80) = 10.42. A19's
   "F buys +0.0025 at 3.80" is retracted as a solver artefact. Lesson recorded: every full-cone
   k ~ 148 Clarabel number needs a posteriori feasibility + a block-form cross-check.

3. **But gate (b) still FAILS — and now for the right reason.** With accurate solves and R
   spanning the whole container the cutting-plane loop re-pins onto the automatic class at BOTH s:
   the low fixed-row values (10.34 at 3.80 / 8.57 at 3.84) are values of UNCONVERGED row sets;
   each oracle round streams fresh R-meeting disjoint pairs at K in (-0.7, +1.4) (need <= -1)
   plus migrating diagonal cells, and lambda climbs monotonically back:
   3.80 (k=308): 10.4914 -> 10.5052 over 5 its, F=0 on the final rows 10.5061 => F buys <= 0.001
   (needed 0.086). 3.84 (k=480): 8.5683 -> 11.0764 -> 11.0777 -> 11.0838 -> 11.0860 with
   violations still ~ +0.4/+0.8 at stop => lambda > 11 already on rows and still rising; final
   same-rows: hybrid 11.085959 vs F=0 11.144051 (F buys +0.058 — real but insufficient, and the
   equilibrium is above it). **lambda < 11 at 3.84 is NOT approached; the
   "localisation is the obstruction" hypothesis is REFUTED: scaling R from 148 to 480 atoms
   (hull = the whole container, atoms = the top binding-cover half of the full atom set,
   inventory includes the exact LP-floor tight structure) does not unlock the class.**

4. **Programme reading.** A19's graph diagnostic (pattern class feasible at ~10.4 on the c384
   graph) is now confronted with an ACCURATE convex continuum solver on a container-spanning R —
   and the continuum still wins: the re-pinning is caused by the 6-D pair CONTINUUM (a
   never-exhausted stream of near-tangent mid-tilt pairs — each finite pair row set leaves a
   neighbouring cell open, and the SDP exploits it until the next oracle round), not by solver
   reach, not by R's extent, and (per the graph diagnostic) not by the feature basis on any
   finite subset. This is grid->continuum risk R1 in its sharpest observed form: the class
   optimum on every FINITE row set sits far below the continuum equilibrium, and the equilibrium
   is the automatic value. Step 3 (smooth features) was NOT triggered per the dispatch (gate-3.80
   failed with gain <= 0.001 < 0.02).


## 5. Reported values (dispatch item 4)

No kernel worth a dedicated 3-seed final attack exists: at both s the loop-stop kernels carry
OPEN oracle violations (3.80: +0.33 diag / +0.33 pair at it 4; 3.84: +0.41 / +0.78 at it 5), so
their true lambda values exceed the row values and the scaling-trick lambda_cert is worthless
(as in A17/A19). The honest numbers, all Clarabel block-form on oracle-adapted rows:

| s | class row value (hybrid) | F = 0 same rows | F buys | tau*(s) / target |
|---|---|---|---|---|
| 3.80 (k=308) | 10.5052 (viols open, rising) | 10.5061 | <= 0.001 | 10.42 — MISSED by 0.085 |
| 3.82 | not run (pointless after both gates) | — | — | 10.62–10.72 |
| 3.84 (k=480) | 11.0860 (viols open, rising) | 11.1441 | +0.058 | 11 (exact) — row value already ABOVE 11 |

## 6. Files / reproduce

- block_sdp.py — BlockHybridSDP: D4-isotypic PSD blocks for the (k+1)-cone (sparse affine maps
  per irrep), vectorised row extraction, rpair_orbits_fast, fdist cutoff, check_blocks.
- validate_a20.py — V0/V1/V2/V2b gates (`python validate_a20.py both`); results/validate.json.
- check_feas_h380.py / check_feas.py — a-posteriori feasibility verification of solver output
  (the tool that exposed the A19 artefact and validated every headline value here).
- samerows.py — same-rows F on/off from a saved state.
- run_a20.py — driver (widened full-tight-set inventory, LP-floor placements, block solves,
  resumable): `python run_a20.py --s 3.84 --atoms a07_384 --tag c384 --iters 8 --kcap 480
  --row_cap 2200 --pair_cap 4200 [--resume|--solve_only]`.
- results/: b380*.json/_state.npz (3.80, k=308, it 4), c384*.json/_state.npz (3.84, k=480, it 5),
  b384_state.npz (the k=597 death), samerows_b380.json, validate.json;
  logs/: b380.log, b384.log, c384.log, validate.log, samerows_b380.log.
- Machine lessons: (i) Clarabel "optimal_inaccurate" solutions here are feasible to ~1e-7 (always
  verify a posteriori — cheap); (ii) full-cone Clarabel can stall SILENTLY at a suboptimal point
  even at cone 149 (the A19 h380 artefact) — cross-check any full-cone number against the block
  form; (iii) memory envelope on 32 GB: (f-vars x rows) ~ 14.5k x 9.7k OK, 22.5k x 9.1k dead;
  (iv) background solves die silently on OOM with exit 0 — keep per-iteration state.
