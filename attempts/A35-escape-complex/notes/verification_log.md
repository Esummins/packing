# A35 lead verification log (Fable)

## M1 (2026-08-27) — VERIFIED (independent spot checks, scratchpad verify_m1.py, no strata_lib reuse)
- 81 survivors: count, 10-row family containment, |B| in {2..6}, and EVERY survivor contains a
  literal seed {8,9} or {21,22} — PASS.
- Cone LP spot checks: 15/15 random survivors feasible; 25/25 random |B|=7 infeasible; all 128
  one-row supersets of the four k=6 survivors infeasible — PASS (K=6 sharpness corroborated).
- Exhaustive independent re-derivation of cone-alive subsets of the 10-row family: 225 including
  the empty set = 224 nonempty. M1's prose says "223" but its own per-k table sums to
  10+39+74+69+28+4 = 224 and 143 empty + 81 survivors = 224. COSMETIC off-by-one in the report
  prose only; data consistent.
- 28 outside-family singletons all cone-dead — PASS.
- lambda* stored rationals: float residual 6.25e-17, floor 0.047644046808 — PASS (M1's own IV
  bound 9.68e-45 at dps 60 accepted on top).
- Min cuts: {11,19,34} disconnects x, {19,25} disconnects y; brute force: no 2-row x-cut, no
  1-row y-cut exists — PASS (theory.md recon numbers corrected accordingly).
- theory.md updated: cut numbers, M1 UPDATE block in T1, new lemma T1-b' (coordinate sign
  collapse) with proof — the sound form of M1's force-balance cascade, straddle-blocking caveat
  added (M1's implementation at z-hat point gradients is consistent with it since the smallest
  firing coefficient 0.0594 is far from 0).

## M2 (2026-08-27) — VERIFIED
- Re-checker code/m2_check_route.py: 81 (W) certificates, 1053 checks, ALL PASS (h_W = 69/32000
  uniform, max x* = 7.75e-58, max psi/h = 0.9898, min tangential margin 0.01233).
- Corruption gate (lead's own): perturbing omega_rational[0] of W_8-9 by 1/1000 -> 5 named check
  FAILURES (eps_w, Hbar, contraction, fixed point, claim) — checker bites.
- Headline accepted: all 81 survivors first-order WEDGED (max |e_s·v| = 7.8e-16 over the escape
  cone probe = zero within tolerance; sigma_min(G) >= 1.1547 no near-degeneracy); wedge verdict
  itself [NUM] but nothing rests on it — the (W) Motzkin-dual certificates are IV+rational and
  use only rank(A)=34 [RFP]. sigma-dip alarms: none. Inflation variant A infeasible at all radii,
  variant B r_1 = 2e-4 < r_N — subsumed by A22, honestly reported (theory.md's caveat confirmed).
- Structural consequence recorded: THE ESCAPE COMPLEX AT THE JAM IS EMPTY at first order; the jam
  is a saddle of sigma on the retained manifold held shut only by the one-sided broken-gap signs
  (descent -0.07 tau^2 along the best saddle direction, blocked at first order). Certificate
  validity is therefore contact-model-rigid (any softening/relaxation of the one-sidedness
  destroys it) — for the PI report.
- Gap M2-a (region T1-a) re-steered onto M3 as 34 minimal-dead-set Farkas certificates over
  box(h_W) + upward closure + gained-menu-empty lemma (SendMessage 2026-08-27).

## M4 (2026-08-27) — VERIFIED (cross-checks green; two real basis defects found)
- Float engine self-consistency vs strata_lib [IV]: rows <= 4.4e-16 at z-hat, gap table exact.
- Independent wedge confirmation: 81/81 escape cones = {0} by LP (min wedge strength 0.577354
  ~ 1/sqrt3, no near-degeneracy) — agrees with M2's rigorous (W) verdict from a different method.
- ALARM CHECK GREEN: 0 sigma dips over 4691 segments, both bases, both passes; two intermediate
  alarms traced to follower bugs (corrector excursion), fixed, and the methodology note recorded
  (value certificates must monitor true SAT gaps, not only maintained-row residuals).
- Cascade: under the theory's stopping rule (margin s-hat + 1e-3) depth 0, zero events — G3
  discharged; with margin disabled, branching factor 0.18 (mostly wedging at first gained contact).
  E1 pairs all within M1's candidate list (0 off-list) — Lipschitz table corroborated.
- 7 re-jams found, all sigma > s-hat, all refuted (e_s not in active cone, full tie menu) — the
  (C)(b) refute branch works; one sigma-coincidence with an A04 family flagged, not claimed.
- DEFECTS (gate the composition): (i) pair (1,3) corner-corner contact at (1,1) MISSING from the
  A22 basis — lead re-verified in EXACT rationals (corners coincide, centre dist^2 = 2 exactly);
  (ii) dist rows 36/37 are surrogates (valid inequalities — incircle argument, lead checked — so
  A22/M2 value certificates remain SOUND) but wrong stratification coordinates: 40% of v1 routes
  died on them spuriously. M1 resumed on repaired basis v2 (~42 rows); M3 notified to scope claims
  to v1 and do a v2 delta.

## M3 (2026-08-27) — VERIFIED (v1-scoped, honestly reported)
- Region T1-a on box(h_W) CLOSED on basis v1: 34/34 minimal-dead-set Farkas certs [IV]; upward
  closure argument checked by the lead independently (one-line cone inclusion); M3's independent
  [EXACT] product-structure generation check (3x5x5x3 = 225 incl. empty) settles M1's 223/224
  off-by-one (correct: 224 nonempty) — agrees with the lead's own verify_m1.py count.
- Protocol finding accepted: point-optimized y + growth FAILS (8/28 zero-radius); robust
  interval LP over the box is the working form. Recorded for the methods section.
- Fragile joint flagged: B={35} needs a 3956-leaf cover, worst margin 2.0e-8 — sound but thin;
  re-derivation queued as a gap.
- Gained-menu-empty lemma at h_W proved two independent ways (Lipschitz margin 0.01573; direct
  IV with 64-fold bisection, worst pair bound 0.00863) — accepted.
- THE CLIFF: menu empty and enumeration exhaustive at R <= 0.005; at R >= 0.01 escaping class
  ~82% of sampled sets, K collapses, only matched-menu Farkas covers it (0 failures on 88 tested
  strata). Composition must be scoped to the semantic-local box; far field is other machinery.
- v2 preview: 9/34 certs revived by the (1,3) repair, exactly the {0,1,3} cluster + the two
  dist rows being replaced — clean signature, delta queued behind M1b.
- lambda_0 = 0 region statement: lead wrote and proved it in theory.md (same y kills both FJ
  branches; e_s.y < 0 unused) — M3 gap G-6 discharged.

## M1b (2026-08-27) — VERIFIED (independent spot checks, scratchpad verify_m1b.py, all PASS)
- v2 rank 34 (sigma_min 0.1282), self-stress dim 8, no nonneg self-stress (LP infeasible) — PASS.
- Rows {0,2} forced lambda = 0 over the polytope; floor on the 40 load-bearing rows = 0.047644047
  exactly as reported — PASS. (theory.md (A) restated on the load-bearing rows.)
- 20 random |B|=14 sets all cone-dead (K = 13 consistent) — PASS.
- Seeds: {0,2} and {4} both dof-1 movable, both first-order FLAT (|e_s.v| ~ 1e-16) — PASS.
- LEAD FINDING (sharpens M1b): BOTH seeds are killed at first order by the auxiliary valid rows
  ((W')-(i)): D0-1 rate along the unit kernel = -0.816497 for seed A AND for seed B (the lead's
  initial hand computation that seed B survives dist was a sign error; the LP kernel refutes it).
  Relayed to M2-delta; expected consequence: the 25,050 queue re-collapses under menu-complete
  first-order tests. IV certification pending (M2b).

## M3b (2026-08-27) — VERIFIED (region T1-a closed on v2; correctness catch accepted)
- Lead spot checks (scratchpad, independent LPs): all 4 minimal dead triples confirmed dead with
  all 2-subsets alive; the 37-set family predicts cone-aliveness on 2000 random break sets with
  0 mismatches. m1b's minimal-dead enumeration bug confirmed real; m1b_enum.py PATCHED at source
  (minimal_dead_sets_complete) + erratum appended to m1b_report.md. Exposure pattern recorded:
  any multi-row-contact basis can have minimal dead sets of size > 2.
- 37/37 IV certs at h_W (36 single-y, 1 subdivided: {35}, 735 leaves, worst margin 2.08e-7 —
  fragile joint, gap); both FJ branches via theory.md's lambda_0=0 region lemma, hypothesis met
  by construction.
- Gained-menu lemma re-DERIVED on v2 (not inherited): non-contact list identical (41 pairs,
  checked from the v2 rows); Lipschitz margins 0.01573 / 0.5419; naive interval SAT enclosure
  does NOT certify (-0.001067) — the 64-sub-box bound 0.007913 is the quotable number.
- 7/9 of M3's v1 revival predictions confirmed; {5}, {14} still minimal dead (pre-caveated,
  superseded by m3b).

## M2b (2026-08-27) — VERIFIED (closes the measurement program)
- Seed kills: lead's prediction (both seeds die from aux dist rows alone, rate -0.8165) confirmed
  and certified: 160 IV Motzkin (W') certs over every selection menu; no second-order needed; the
  M1b base selection is among the few no-aux survivors, explaining its verdict.
- (V') universal certificate accepted: aux rows restore uniform floor 0.0205 over ALL v2 rows,
  64 certs (meaningful variants) cover the whole 2^42 lattice; TRUE SURVIVORS 0; 553 s vs
  12.8 CPU-days per-stratum with 17% uncovered. Honest numbers preserved: (W') alone kills only
  77% of the 25,050 queue; cone-aliveness GROWS with aux/dom generators (measured, immaterial).
- Re-checker independence noted (rebuilds all 50 rows from A22 cert + documented repair table);
  288 certs / 4,608 checks ALL PASS; corruption gates omega-sign/omega-perturb/h-big/drop-aux all
  fail as required. M2b self-caught + fixed a soundness bug (positive omega on dominance rows)
  before publication — gate discipline working as intended.
- Trade-off recorded: (V') reach h_G = 0.25-0.45 x r_N (omega-scale-bound) => composed v2 basin
  currently subsumed by A22 in reach; (W') reaches 1.6-3.1 x r_N. Inherited endpoint-row gap
  (M2b-a) = the conditionality of the v2 theorem; named lever L1 in the final report.

## CLOSED 2026-08-27. Final verdict: results/final_report.md; registry row appended.
