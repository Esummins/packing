# A38 design — weapon composition into the A27 tree at s0 = 969271/250000 (Fable)

## AMENDMENT 1 (post-build, pre-campaign — Fable)
Build measurement: W1 as an LP row filter drops 0.28% of oracle-offered rows, delta-tau = 0,
+50% wall (the oracle hunts low-coverage placements = exactly the non-exempt ones). DECISION:
campaign runs with the W1 LP filter OFF; W1/W2 stay as (i) node-kill tests (inflated core box
wholly exempt at thr_cert, or multi-core sum_j c_j > k + eta — strictly stronger than the row
form, ~ms cost) and (ii) W2 thr_node lowering where multi-core (15/216 level-1 cells have
c_j > 1). Attribution sample: ~8 stratified nodes re-run with the filter ON to confirm
delta-tau = 0 (run only if wall budget allows). Ledger note: certified threshold exempts 5.7%
of placement volume vs float threshold 26.8% — A33's reclaimable sealing margin is a ~5x
multiplier on W1's bite (named lever, feeds the extrapolation's optimistic end only as [NUM]).

Read with notes/T0_composition.md. Engineering decisions fixed by the lead; workers implement.

## AMENDMENT 2 (post-harness — Fable)
Harness measurements that adjust the frame: (i) W1 row-filter drop rate is DEPTH-DEPENDENT:
0.28% at level-1 box scale -> 4.45% at 2-core seam scale (~16x) — Amendment 1's filter-OFF
steer holds for levels 1-2 but the filter must be re-tested at depth 3+ and in the cascade
(record in report; the tight-variety threshold bites as boxes shrink). (ii) W2 pair kill fires
0/16 at seam scale: c_j = robust-atom lower bound collapses (~0.03) over wide boxes — W2 is a
POST-REFINEMENT weapon; the S1 cascade schedule must not credit it at first branching.
(iii) census38's D4 acts at single container size s0 (its own orbit test caught a two-size bug;
closure now 7e-15). (iv) seam Probe B enumerates 16 children (theta-wrap split), b2 is read
against 16. (v) Level-1-scale census (3 trump / 35 atlas / 178 unexplained of 216) is a
box-scale artifact, not a survivor statement — the real census is at depth 3.

## Base machinery
- Copy (never edit in place) attempts/A27-close-384/{caselp.py, lpbox.py, kill_tests.py,
  certify.py, verify_case.py} into A38/code. solve_node(s, hyp, budget, ...) is parametric in s;
  s = "969271/250000" (float 3.877084 for the LP, exact Fraction for certification).
- Root zone: Z = [0.5+CW, s0-0.5-CW]^2, CW = 0.6 first (A24's), fallback CW = 0.5.
  Root node: Hyp(nofams = [complement-of-Z all-theta]) — i.e. the A24 root recipe re-run at s0,
  budget 11; kill = certified tau < 11.
- Level-1 cover: fundamental triangle T = {s0/2 <= y <= x <= s0/2 + CW + 0.5 - 0.5} — exactly
  A24's scheme: 8x8 grid on [s0/2, s0/2 + 0.8385421]^2 upper triangle (36 position cells,
  diagonal cells kept whole) x 6 theta windows of 15 deg = 216 nodes, budget 10.
  Cell half-widths: 0.05241 (centre), 7.5 deg.
- Refinement: 8-way (2x2x2 in x, y, theta), A27 semantics. Kill/alive/undecided classification =
  A27 run_l1 rules verbatim (kill needs added_rows == 0 and minmass >= 1 and tau < budget;
  alive(LP) needs tau >= budget and maxcov <= 1 + 1e-3).

## W1 — field domain cut (code/fieldcut.py)
- Load the SEALED cert attempts/A33-tight-variety/t1/certs/A33_measure_feasible_3.877084.json
  (exact atoms/weights; loader semantics in attempts/A33-tight-variety/t2/mapper.py
  load_cert_exact / load_field_atoms). ~1480 atoms after D4 expansion — confirm whether the cert
  stores the D4-expanded atom list or orbits; expand if needed so that coverage of ANY placement
  in [0,s0]^2 is bounded.
- mlow_box(t0,t1,x0,x1,y0,y1): conservative lower bound on min over the box of mu(Q(x)) = sum of
  weights of atoms ROBUSTLY inside Q(x) for all x in the box. Interval arithmetic on
  u = R(-theta)(p - c), theta = 2*atan(t); atom counts only if max|u|_inf <= 1/2 - SLOP,
  SLOP = 1e-6 (absorbs lambda-scaling 1e-7 + float rounding; direction = conservative undercount).
  Vectorize over atoms with numpy (per-box cost ~1e4 flops).
- Dense grid: resolution (dt = 0.01, dc = 0.02) over t in [0,1], c in [0.5, s0-0.5]:
  precompute per-cell m_low once (vectorize per atom over the cell grid); store as npy + meta.
  Exemption rule with EROSION: a placement (row) at (theta, cx, cy) is W1-exempt at threshold thr
  iff its containing grid cell AND all 3^3 neighbours have m_low > thr. (Erosion covers rows near
  cell boundaries + oracle jitter; strictly conservative.)
- Thresholds: thr_cert = 1 + eta_cert, eta_cert = 44630467/3906250 - 11 = 0.4254 exactly (the
  SOUND one, used for anything labelled a kill); thr_float = 1.243 optional, [NUM] only, for the
  sensitivity column of the kill matrix.
- Wiring into caselp: filter rows AND oracle candidates through the mask (drop iff exempt); also
  drop from the maxcov sweep so alive(LP) is measured on the true admissible set. Keep a node-level
  flag counting rows dropped by W1 (for the kill matrix). A node whose ENTIRE core box B (inflated
  one grid cell) is exempt is killed outright without an LP: record as W1-node-kill.
- CANARY (mandatory, run in selftest): the 11 Trump placements (atlas fam 0 canonical_sig in
  attempts/A37-cp-atlas/results/atlas_final.json — confirm its (cx, cy, angle) convention against
  the known Trump geometry before use) and their D4 images must be non-exempt at BOTH thresholds.

## W2 — conditional tight-sum cut
- For a node with cores B_1..B_k: c_j = mlow_box(B_j inflated by one grid cell). Node threshold
  thr_node = 1 + eta - SUM_j max(0, c_j - 1) (eta = eta_cert). Apply the SAME mask machinery at
  thr_node instead of thr_cert. Record kills/row-drops attributable to the threshold difference
  (i.e. rows exempt at thr_node but not at thr_cert) as W2.
- Expectation (measure, don't assume): at level-1 box size (0.05 x 7.5deg) c_j will often be
  exactly the trivial 1.0 (some placement in B has coverage 1) — W2 bites at depth >= 2.

## W3 / W4 — census + seam only at pilot depths (structural zeros in the kill matrix)
- W3 cannot fire with k <= 3 cores (needs all 11 squares pinned inside an atlas box). Instead:
  survivor census — for each depth-3 survivor, min distance (in (cx, cy, theta), D4-orbit
  minimized) from its witness box to each of the 11 Trump placements and to every atlas entry's
  placements; classify Trump-consistent (box intersects the h-inflated neighbourhood of some
  Trump placement) vs other-attractor-consistent vs unexplained.
- W4: seam probe (separate task, see brief for worker D).

## Measurement protocol (kill matrix discipline)
- Level 1: run all 216 nodes BASELINE (W5 only, no W1) at time_limit 240 s — comparability anchor
  with A24/A27 at 3.84. Then run W1(+W2)-augmented on every baseline non-kill. Matrix columns:
  W1-node-kill (mask containment), W5-kill (baseline LP), W1-marginal-kill (augmented LP kills a
  baseline non-kill), W2-marginal, alive(LP), undecided, with tau values and wall costs.
- Depths 2-3: refine survivors with the FULL stack only (no baseline re-run), stratified sample if
  the count exceeds the time budget (record the sampling frame; kill fractions get binomial CIs).
- Stall flag: alive(LP) at depth d whose ALL 8 children are alive(LP) at depth d+1 with zero
  W1/W2 row-drops = the A14 wall mode; report count and location.
- Checkpoint everything (per-node json, resumable); <= 6 worker processes total on the machine;
  the root LP counts as big (run alone or with <= 1 other).
- A-posteriori LP verification per lab standard: every kill that enters the headline matrix gets
  its LP re-solved feasibility check (minmass >= 1, exact budget compare at rational tau) and a
  10% random sample (min 5 per depth) gets the FULL exact verify_case-style certificate including
  the W1/W2 exemption audit (m_low re-derived in exact rationals via mapper.mlow_exact semantics).
  Non-sampled kills are labelled kill(LP) not kill(certified) in the report.
