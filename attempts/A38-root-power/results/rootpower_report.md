# A38 — far-field root-power measurement at s-hat: final report (Fable lead, 2026-08-28)

## 1. Question and verdict

Can the conditioned case tree at s0 = 969271/250000 = 3.877084 (just above s-hat), armed with
the composed weapons (tight-sum domain/pair cuts, atlas discharge, Farkas/FJ, the A27 arsenal),
shrink the far field to the certified atlas boxes at desktop node counts?

**VERDICT: NO-GO at every measured configuration. The assassin is the PER-NODE LP DECISION COST
AT s0 — a cost wall, not a geometry wall.** At 3.84 the same pipeline's nodes DECIDE in
150-500 s; at s0 the identical rule produced ZERO decisions in 60 depth-2/3 nodes at
180-485 s/node (tau sits 0.5-1.5 BELOW budget — kills plausibly exist — but minmass stays
pinned at 0-0.5: the row-generation LP never stabilizes, so neither the kill rule nor exact
certification can fire). Meanwhile branching runs at b_eff = 8.00 flat and every composed
weapon is silent until W1's projected first bite at depth 5-7. Frontier to that depth from the
172 level-1 survivors: ~1e5-1e6 nodes x >= 500 s/visit = **1e4-1e5 CPU-h = ~70-700 desktop-days
as a FLOOR that assumes nodes decide at the measured visit cost — and the measurement says they
do not, so the true bracket is open-ended above.** Pre-registered GO criteria: all four FAIL
(f_3 = 0 vs required > 7/8; 13/13 stalls; seam probe A uncertified; bracket floor at/above cap
with no measured decision constant). Plain language: the tree's shape is fine — the guard-LP
engine that decides each case, which is fast at 3.84, does not terminate at the endgame side.
What would change the verdict (named levers, in order of leverage):
 (L1) reclaim A33's sealing margin (eta_cert 0.4254 -> ~0.26, gap A33-G5): a ~5x multiplier on
      W1's excluded volume, pulling W1's kill onset ~2 depths earlier (~64x fewer frontier nodes);
 (L2) a per-node decision rule that does not require full row-convergence — the root itself
      certified from an UNCONVERGED LP (minmass 0.85, exact cert at scale 1.25, total 10.0006
      < 11) because it had 3.0 of tau slack; depth nodes at slack 0.5-1.5 need the float
      oracle's holes fixed at solve time (witness-feedback in the loop), not at certify time;
 (L3) warm-started/inherited row systems parent-to-child so each child pays an increment, not a
      from-scratch convergence.
None of these is measured to suffice; L1 is quantified, L2/L3 are engineering with unknown
constants. Honest close: the far-field tree at s-hat is not purchasable with today's engine.

## 2. T0 — the composed soundness statement

notes/T0_composition.md. One-line form: D1 attainment + root occupancy at s0 + per-cell
disjunction {K1 W1/W2-augmented case-LP kill, K2 atlas discharge, K3 FJ/Farkas, K4 D2 slack} +
BDBFS discovery => s(11) >= s-hat, equality closed by A36's uniqueness clause. Eight named seams
S1-S8; the pilot measures, it does not discharge.

## 3. Build findings (pre-campaign)

- Sealed field at s0: 1480 exact atoms, eta_cert = 0.4254. Certified-threshold W1 exempts 5.7%
  of placement volume; float threshold (eta 0.243, [NUM]) exempts 26.8% — A33's reclaimable
  sealing margin is a ~5x multiplier on W1's bite (named lever for A33-G5 follow-up).
- HONEST NEGATIVE: W1 as an LP row filter is dead — 0.28% of oracle-offered rows dropped,
  delta-tau = 0, +50% wall. The column oracle already concentrates on the tight variety; the
  domain cut's value in THIS tree is node/branch pruning (whole-box exemption), not LP
  acceleration. W2's value is thr_node lowering + the pair node-kill at multi-core nodes.
- Trump canary PASS (all 11 placements + D4 images non-exempt at both thresholds).
- atlas canonical_sig convention: theta in radians (verified by exact pair separations).

## 4. Root at s0 — THEOREM A38.1 (certified, standalone)

Every packing of 11 unit squares in [0, s0]^2, s0 = 969271/250000 = 3.877084, has a square whose
centre lies in the closed interior zone Z = [11/10, 694271/250000]^2. Exact certificate total
2500143/250000 = 10.000572 < 11 (verify_case chain PASS; results/root_s0.json +
certs_l1_sample/root_s0_cert.json). Anchors the interior-first tree AT Trump's own side.
THE NUMBER TO RESPECT: the margin is 0.9994 vs 2.76 for the same zone at 3.84 — the root
occupancy lemma survives at s0 with 36% of its 3.84 margin. The interior-first entry point is
still open at the endgame value, but only just; there is no fat left for stronger root zones.

## 5. Kill matrix (depth x weapon)

Level 1 (216 nodes, budget 10, time cap 480 s, 150-min wall cap):
depth | nodes | W1-node | W2-node | W5 dead | alive(LP) | undecided | notrun
1     | 216   | 0       | 0       | 44(LP)  | 5         | 85        | 82
Kill-fraction accounting (THE central honesty issue, see below): f1_certified = 0.045,
f1_discounted = 0.246, f1_optimistic = 0.328 (over the 134 processed; over all 216 the
optimistic figure is 0.204). b_eff(level 1) = 8(1-f): 5.4 (optimistic) to 6.0 (discounted).
tau quartiles 9.00 / 9.58 / 9.99, max 10.50; median node 498 s (3.84 anchor: 9.00/9.00/9.56,
655 s, final 117/216 dead).

**CERTIFICATION FINDING (headline).** The 8-node exact-certification sample FAILED on 2/8:
the float row oracle left 46- and 31-box coverage holes on nodes that PASSED A27's
classification rule (converged, minmass 1.0, added_rows 0), and both repaired to tau = budget
(the kills evaporate). Scoping: A27/A29's 3.84 kills are NOT contaminated — every 3.84 leaf was
individually exact-certified; the gap is float-classification-WITHOUT-certification, which only
A38's level-1 sweep used. Consequence adopted from depth 2 on: exact-certification-in-the-loop
is the only kill accounting (measured cost: certification becomes a first-class node cost).
Weapon columns: W1/W2 node kills are 0 at level-1 box scale, as the build measurements
predicted (whole-box exemption needs boxes comparable to the excluded pockets); c_core > 1 on
15/216 cells, all corner-ward geography. W1-as-LP-row-filter is DEAD at this depth
(0.28% of oracle rows, delta-tau = 0 on n = 1 — the pre-registered n = 8 A/B gate was not met;
honest caveat). W3 atlas discharge and W4 FJ are STRUCTURAL ZEROS at pilot depths (they need
all 11 squares pinned); measured instead via the census and the seam probe.
Depth 2 (stratified sample, 10 parents / 80 children, 41 processed at 240 s cap,
certification-in-the-loop): 0 kills by ANY weapon — 41/41 undecided. Per stratum: alive-parents
29 processed (tau median 9.00, max 10.00; c_core median 0.848), notrun-corner 8 (tau median
8.61 — well below budget, and still no decision; c_core median 1.205), undecided-edge 4.
f2 = 0.0 certified AND optimistic; b_eff = 8.00; binomial 95% upper bounds 0.117 (alive
stratum) to 0.56 (small strata).
Depth 3 (3 parents / 24 children, 11 processed at 180-420 s; 420 s did not move minmass):
0 kills, 11/11 undecided, f3 = 0.0, b_eff = 8.00. tau medians 8.56-9.25, c_core median
1.166-1.214 (55% of depth-3 nodes have c_core > 1 — see the W1 trend below).
Stalls: 13/13 refined survivor-parents are honest stalls (all processed children undecided,
zero weapon contribution) — but NOT the A14 wall mode: tau is BELOW budget nearly everywhere
(the LP is not pinned at tau >= budget; it simply never finishes deciding). The knife-edge
exception: the five level-1 alive(LP) cells sit at tau = 10.000000 / maxcov = 1.000000 EXACTLY
— an equality structure (it smells like the 1/4-ghost's fractional packing pinning the LP at
budget exactly, the same equality manifold A33 found essentially unique at s-hat); their
children stay undecided at tau 9.0-10.0. If the cost wall were removed, these five cells are
the candidate true-wall geography to watch.
W1 trend (the one positive): c_core median climbs 0.658 (depth 1) -> 0.85-1.21 (depth 2) ->
1.17-1.21 (depth 3); W1's whole-box kill fires at c_core > 1.4254, projected onset depth 5-7
at the certified threshold — or ~2 depths earlier at a resealed threshold (~1.26), the
quantified L1 lever. W1-as-row-filter: drop rate 0.28% (depth 1) -> 4.45% (2-core seam scale),
~16x growth — dead shallow, plausibly relevant deep; never delta-tau-tested beyond n = 1.
Survivor geography at level 1: kills concentrate in the interior cells; survivors are the
mid-annulus (undecided at cap) and the whole corner-ward triangle (notrun at wall cap) plus the
five alive(LP) cells {61, 65, 74, 95, 100} at tau = 10.000, maxcov = 1.0 — the A27-style
refine-only class, provably beyond the coverage LP at level-1 resolution.

## 6. Survivor census (level-1 survivors; depth-3 census mooted by 0 decisions)

172 survivors: 3 trump_consistent / 34 atlas_consistent / 135 unexplained (at level-1 box
scale, tol 0.02 / 3 deg; "unexplained" at this scale mostly means the boxes are too big to pin,
not that new attractors lurk — but nothing here rules new attractors out either). The five
alive(LP) cells: 2 atlas_consistent, 3 unexplained, NONE Trump-consistent (dist 0.47-0.60 from
centre). TREE-LEVEL TRUMP CANARY CLEAN: exactly 3 level-1 cells contain D4 images of Trump
placements ({21, ...}), all survivors, none dead — the sound tree correctly refuses to kill
Trump's own cell.

## 7. The seam (G1 handoff) — OPEN, and cost-blocked at its first step

Witness = depth-3-scale box (hw 0.0131 / 1.875 deg) on Trump placement #6 (1.9596, 1.6886,
49.82 deg). Probe A (second-square occupancy, Z2 = r 0.06 neighbourhoods of the other 10 Trump
placements): tau = 9.20, slack -0.80 — the LP LEANS the right way (it wants a second square
near Trump's other placements) — but converged = false at 240 s: NOT certified. Probe B
(16 two-core children): b2 = 16/16 survive (all undecided); W2 pair test fires 0/16 — pair
sums 0.91-1.6 vs threshold 2.4254 because the robust-atom lower bound collapses (c_2 down to
0.034) over r = 0.06 second-core boxes: W2 is strictly a post-refinement weapon. Scale gap
ledger: witness half-width 0.0131 vs A36 box 3.7e-3 (need ~2 more depths in ONE square's
coordinates), times 10 more squares to pin, times a per-square branching never measured below
16 — the S1 cascade is unpriced because its first branching never decided. Seam verdict: a
scale AND dimension gap remains; nothing measured contradicts the cascade design, nothing
supports its affordability.

## 8. Stall test (A14 wall mode)

13/13 refined parents stalled — but the mode DIFFERS from A14's: there tau pinned >= budget
with the oracle exhausted (structural unkillability); here tau < budget with the oracle
unconverged (cost, not structure). The exception is the five tau = 10.000 / maxcov = 1.000
knife-edge cells (section 5 remark). No cell at any depth was decided-and-stalled in A14's
sense; the wall we hit is upstream of A14's.

## 9. Extrapolation bracket

Pre-registered frame applied. Witness-coordinate closure depth D_w ~ 5 (0.0524 -> 3.7e-3);
W1 onset depth 5-7 (certified thr). Frontier from 172 survivors at b_eff = 8.00 and f = 0
measured through depth 3: 172 * 8^2 = 1.1e4 (depth 3) -> 8.8e4 (depth 4) -> 7.0e5 (depth 5)
nodes; at the MEASURED visit cost >= 500 s/node (which decides nothing): 1e4-1e5 CPU-h =
70-700 desktop-days as a floor, open-ended above because no per-node DECISION constant exists
at s0 in our data. The binding constant is therefore not b_eff and not f — it is the per-node
decision time T_decide(s0), which is unmeasured because it exceeded every cap we could afford
(vs T_decide(3.84) ~ 150-500 s, the whole difference driven by eta(s0) ~ 0.24 vs eta(3.84) ~
0.046: a 5x richer near-tight placement family for the oracle to enumerate). Sensitivity: the
[NUM] resealed-eta variant (L1) cuts the frontier ~64x (onset depth -2), landing the floor at
~1-10 desktop-days IF T_decide were ~500 s — every path to GO runs through both L1 and L2/L3.

## 10. Gap list

- A38-G1 (CERTIFICATION DEBT): 38 of the 44 level-1 dead(T1) are kill(LP) only (6 sampled
  certified + root); 2/8 sample failures PROVE the A27 float classification rule insufficient
  at s0. No downstream use of A38's level-1 kills without exact re-certification.
- A38-G2: W1-filter delta-tau = 0 rests on n = 1 (pre-registered n = 8 A/B gate unmet).
- A38-G3: f2 = f3 = 0 carry wide binomial CIs (0.12-0.56 upper bounds); no positive f was
  measured beyond level 1 at any cost we could afford.
- A38-G4: seam Probe A unconverged — the occupancy-cascade question is open, not answered.
- A38-G5: W2 untested at the second-core scale where it could fire.
- A38-G6: 82 level-1 nodes never run (wall cap); the corner geography is unmeasured at s0.
- A38-G7: no long-limit calibration point (e.g. one node at 3600 s) for T_decide(s0) — the
  single most valuable next datum if anyone re-opens this line; cheap, and it would close the
  bracket's open top.
(Carry-ins: T0's S1-S8; A33-G5 eta seal — now quantified as a 5x W1 multiplier; A37 G-1..5.)

## 11. Files

notes/T0_composition.md, notes/design.md (Amendments 1-2), notes/extrapolation_frame.md
(pre-registered), code/ (fieldcut, node38, cover38, census38, seam38, selftest38 + A27
copies), results/ (cover_l1.json, mlow_grid.npz, selftest38.json, root_s0.json, l1_nodes/,
l1_a38.json, l2_nodes/ + l2_a38.json, l3_nodes/ + l3_a38.json, census_l1survivors.json,
seam_trump.json, certs_l1_sample/), logs/.
