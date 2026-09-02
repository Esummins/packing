# A65 — low-k closure (Fable lead) — LOG

2026-09-01/02. Hard constraints honoured: <= 2 light LP slots (BLAS-pinned, headroom checked
> 6 GB before each launch), A57/A60/A61 state untouched, writes confined to
attempts/A65-low-k-closure/, docs/proofs/, lean/depgraph.json (labels/notes), REGISTRY, this file.

## T1 — Theorem U (U-O1): DONE
* Read-in: unique_transfer.md spec; anchors chosen: s'' = 3877083591023/10^12 (the A03 tight
  certificate side — rational, above the A22 enclosure of s-hat, in the T1 isolating interval,
  realised by a verified packing) and A22 krawczyk z0 (||z-hat − z0||_inf <= 1e-50).
* `code/emit_u.py`: emitted certs/u_reinsert_00..10.json (10 slack cores a = 4999/10000,
  budget 1, one pocket nofams zone half-width 1e-3; atoms EMPTY, Sigma w = 0) + exact
  side-condition ledger results/u_ledger.json (min core containment margin 9.9997e-5 > 0;
  max nofam-to-basin deviation 1.0000010e-3 < rBasin = 3/2000; lambda − 1 = 2.580e-10).
* Verified: all 11 PASS, cold `verify_case.py --depth 60` (audited copy, byte-identical),
  sub-second each, zero atoms consulted (logs/u00..u10.log, certs/*.report.json).
* Falsifier control: certs/u_control_00_nonofam.json (exemption removed) FAILs with every
  witness a mass-0 HOLE at Trump's own pocket (theta ~ 0, centre ~ (0.5000014, 0.5000014)) —
  the PASSes are non-vacuous and the zone is load-bearing exactly at the true pocket.
* Composition written: docs/proofs/theorem_u.md (U-O1 discharged; U-O4 assembled — Theorem U
  consumes only `basin`'s equality clause, so it does not wait on A60's open D-nodes);
  unique_transfer.md section 5 ledger updated.
* Canary: Theorem U CONFIRMS z-hat (conclusion is P = z-hat); control run shows the only hole
  is Trump's pocket. Safe.

## T2 — H10-stuck: routes priced, boosted-kill program executed at pilot strength
* docs/proofs/h10_stuck.md: (1) H10-I incidence lemma (stuckness => >= 2m incidences on the m
  unclipped completable boxes); (2) critical-ratio table R/N per protected class — corners4
  is the unique supercritical class (2.29), k4_08/k4_11 critical (2.00), and TRUMP SATURATES
  HIS OWN CLASS AT EXACTLY 2.00 (I = 12 = R, sq8 at incidence 4) — the canary sits exactly on
  the pricing threshold; (3) route (a) decoupled counting DEAD [T] (ties the threshold
  exactly; every unclipped box admits a local 2-crowd); (4) route (b)-as-scoped DEAD on cost
  (pair-conditioning = zone-tree-squared per box) and on the decoupling objection;
  (5) route (c) upward absorption DEAD [T] (occupancy-matrix closure: no killed target at any
  root); (6) THE surviving executable form = the boosted-kill LP (per-placement RHS
  1 + beta*m(Q)), certifiable through the FROZEN verifier as L+1 invocations on one atom list
  (level-l exemption zones + strict-margin l*beta), kill condition
  Sigma w < (11−k) + 2m*beta; death criterion = crowd-saturated disjoint family (I >= 2m).
* results/h10_boxspec.json: exact per-class unclipped box lists (from the A58 matrix).
* Death-witness search (Opus chore): code/crowdfam.py, results/crowdfam.json — see report.
* Boosted-LP pilot (LP slot 1, detached, BLAS-pinned, headroom 11.8 GB at launch):
  code/boostlp.py (monkey-patched RHS in A65 copies of lpbox/caselp; float pricing only)
  on k4_13 = corners4, beta scan 0/0.25/0.5/1.0 — results/boost_k4_13.json.

## T2 results
* crowdfam (Opus chore, exact re-verified at D=1e8, independent second-script check): NO
  protected class saturates its revenue threshold. I_exact vs R: k4_08 13/14, k4_11 13/14,
  k4_03 9/10 (each short by ONE, deficient box = a clear-corner root), k3_05 12/14,
  k3_02 10/12, k2_01 11/12, k1_00 8/10, k0_00 5/8; corners4: NO feasible pins+7-family
  found at s0 at all (blind search min-gap −2.5e-2; template side-study feasible only ~4.0).
  Structural: pins+family = 11 disjoint squares at s0 = a near-optimal packing configuration;
  all realisable families are Trump-image perturbations. Caveat: search maxima are evidence
  (A55 K5 undercount lesson), not proofs.
* boosted LP pilots (slots 1+2, 600 s caps): k4_13 tau(0)=7.2545; at beta=0.25 restricted
  tau 12.62 > threshold 11.0 => kill refuted (slope ~21.5 vs revenue 16). k4_08
  tau(0)=7.000000 exactly (tau*=k alive pattern, canary-coherent); at beta=0.25 restricted
  tau 11.25 > 10.5 (slope ~17 vs 14). Convexity => dead at every beta. Bonus function
  unit-tested (incl. the overlapping-box subtlety at s<4: adjacent-corner offset-1 boxes
  overlap in x in (1.877, 2)).
* Universal law: fractional duals collect ~N*L_eff per unit beta at box-cluster junctions;
  2m <= N*L_eff − 3 in every protected class (results/clique_caps.json). The crowd's value
  is pairwise; single-square measures cannot monetise it. Full synthesis + ranked residue:
  docs/proofs/h10_stuck.md sect. 8.
* Deliverables: depgraph A.THMU -> certificate+verifier, C.K4TIER note re-priced, SVG
  re-rendered; registry row appended; A57/A60/A61 untouched throughout.
* Hand analysis banked: corners4 4-clique is pairwise-co-meetable but jointly UNREALISABLE
  (chord half-length 0.6203 vs pin-corner clearance 0.613: the tilt window (80.4, 81.3) deg
  needed for the pin dodge vs (>= 81.3 or <= 8.7) for the reach — empty by 0.9 deg);
  L_eff = 3 for certification levels.
* (beta = 0.5 / 1.0 confirmation tails: see results/boost_k4_13.json, boost_k4_08.json —
  verdict already fixed by the beta = 0.25 refutation + convexity.)
