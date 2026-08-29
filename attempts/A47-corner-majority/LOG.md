# A47 LOG

2026-08-29 (Fable lead)
- Read BRIEF, ideas I-L18(+expanded), A46 report + w1_theory + composition_report,
  A23 notes (4a/4b), A21 notes (THM1/THM2), structure lemmas L2/L4/L5/L6/L7.
- LEG (a) THEORY RESULT: W1.6(f) corrected. Thin chains have EXACT span o*sqrt2 + r
  (o >= 2 owners at tilt 45, r receivers at tilt 0); the designed G3 [45,0,0,45]
  structure has span 2 + 2 sqrt2 = 4.828 > s0 and cannot exist; the ONLY span in
  [3.82, s0] is 2 sqrt2 + 1 = 3.82843 (structure [45,0,45], 2 params). Thin branch
  EMPTY at s0 and at every s in the window except s* = 2 sqrt2 + 1. notes/theory.md T1.
- Spawning: Agent A (Opus) = exact span checker + s*-exception coverage certificate
  (rational relaxation s' = 383/100, obstacle-aware A08-style measure, param boxes).
  Agent B (Opus) = leg-b primitive tables (corner zone, side zone, pair pilot) exact
  Fractions via A46/A23 harness. A29 untouched. <= 2 heavy processes per agent.
- Course correction to Agent B: A21 zones live in the 3.88-normalized frame; scale-back
  by 969271/970000 => enlarged boxes [49/100,11/10] (corner) and cy down to 109/100
  (side). Applied.
- Composition-level canary recorded (composition_canary_vacuity.json): all 12 atlas
  families + Trump have >= 12 flush contacts => flush-free composition provably vacuous
  on every genuine structure. PASS.
- P1 (small-angle population vacuity) added to notes/theory.md: bridge instantiates per
  contact, no coupling; interiors capped angle-independently (CE 0.0071 / sharpCC 0.0706)
  => majority counting on interiors is MOOT.
- Leg (b) landed (Agent B): corner table 54 entries exact (max 0.8523 delta-indexed,
  0 tile failures), NEAR-FLUSH CELL EXACTLY 0 (Trump-confirmed); feasibility law
  (tilt > 40 deg infeasible within 0.7 of wall); side table inert; pair vacuous at zone
  width; canaries ALL PASS. results/primitives_*.json + primitives_report.md.
- Leg (c) run (compose_c.py): FORCED sum = 0 for every profile (near-flush parking
  evasion); GRANT-ALL 1.77-2.99 = x1.35-2.27 short at forced counts; CE-only ceiling
  with both zones granted = 3.795 = 0.941 B0 (Ceiling-2 survives, largest jump yet);
  sharp-CC fire zone 84 lattice points, all n_WC >= 10 — nothing real close. Composition
  DOES NOT FIRE; sixth face named (activation zeroed by flush-adjacent parking +
  diffuseness caps capture at ~14%). results/composition_a47.json; report drafted.
- Waiting on Agent A (s* exception certificate): partial so far — attempted boxes all
  PASS (worst margin 0.159), coverage of the (y0,b) domain incomplete, agent running.
- Lead verification of leg (b): area sums = exact tile sums (54/54 entries, 2289 tiles),
  tiles pairwise interior-disjoint, adversarial float attack ~974k probes 0 hits. SOUND.
- PI framing correction folded in: the budget compositions price flush-free PACKINGS
  (over-strong); the eps-parking escape is not critical (it drains). Report scoped;
  refined open problem recorded as I-L19 (bridge-cascade descent, attack surface = the
  bridge's structural requirements: blocker slope g > d strictly, blocker itself loaded
  => recursion; presser needs own wall path; wall levers die 1/sin d). ideas.md updated
  (I-L18 closed done-negative into I-L19).
- Agent A LANDED: t1_span_check PASS (unique (o,r)=(2,1)); s* exception lemma PROVED,
  full declared domain, 50/50 parameter boxes, exact coverage audit 0 gaps, worst
  margin 0.1588, A08 core verbatim + two new exact links, independent re-verification
  + negative control. => THIN BRANCH OF FLUSH-MANDATORY CLOSED COMPLETELY (T1 + cert).
  Engineering lesson: robust-row patch lattice must align with the verifier's dyadic
  tree.
- Report finalized (placeholders patched, headline = the completed thin-branch theorem),
  REGISTRY row -> done-mixed, ideas.md I-L18 closed / I-L19 recorded. A47 CLOSED.
  A29 untouched throughout; no prior attempt modified; compute: 2 Opus agents, <= 4
  heavy processes total, all long runs checkpointed.

2026-08-29 (Agent B, leg (b) — I-L18 primitive tables) — DONE
- Harness copied VERBATIM from A46 into code/ (a45_lib, dead_region, wastage, atlas_lib,
  exactify, clip_util, canary, task6_canaries, task2_wc) + new a47_lib/run_corner/run_side/
  assemble/canaries/pair_pilot/report_tables. Nothing outside A47 touched.
- TABLE (i) CORNER: 54 entries (9 cells x 6 tilt bins, theta in [0,45]) in the REAL container
  [0,s0]^2, PlacedBox bin-uniform, window [0,13/8]^2, cell0 1/8 -> min_cell 1/64. All exact
  (7049/7049 tiles pass the Fraction recert, 0 failures). theta-table 0 .. 0.8540; the exactly
  derived delta-table (delta = dist(theta,90Z), intersection of the two theta components under
  sigma:(x,y)->(y,x)) 0 .. 0.8523. 5 entries INFEASIBLE ((40,45] with a [.49,.7] cell:
  w(40)/2 = 0.7047 > 0.7), 31 PARTIAL.
- NEAR-FLUSH ([0,1] deg x [.49,.7]^2) = EXACTLY 0, zero tiles at every radius. Load-bearing
  NEGATIVE for the majority composition: flush-freeness alone does not make primitive (i) fire;
  it fires only off-corner (0.175 at 0 deg) or tilted (0.405 at (30,40]).
- TABLE (ii) SIDE: essentially INERT. The brief's coarse cy cells give exactly 0; refined to 7
  cy cells only 5/63 entries are nonzero (max 0.1253), all at the extreme cy cells next to the
  container corners and at cx in [.9,1.1]. min over cy = 0 for all 9 (cx,bin) pairs.
- PAIR PILOT: float 0.00977 (<< 1.0, no exact recert per brief). At A21-zone width the pair
  primitive is vacuous; A23-4c's 1.38 needs cores ~20x tighter.
- CANARIES: ALL PASS. Trump (exact, s = s0): 8 zone instances fire, every one prices 0
  (his 3 corner-zone squares are wall-flush uprights in C_x0_x0_b0_1 = 0) -> sum 0 <= B0.
  12 atlas families (float, own s, overstating direction): 0.0000-0.5798 vs budgets 4.03-4.50,
  max capture 13.8%.
- Zones ENLARGED per the lead's frame-mapping correction ([49/100,11/10]^2 corner,
  [49/100,11/10]x[109/100,139/50] side); vacuous for the corner table (feasibility clip already
  forces cx,cy >= 1/2), applied for real on the side cy axis.
- Deliverables: results/primitives_{corner,side}.json, pair_pilot.json,
  primitive_canaries.json, primitives_report.md (64 lines, gap list GAP-A47b-1/2).

2026-08-29 (Agent A, leg (a) — T1 span check + s*-exception lemma) — DONE
- TASK 1: code/t1_span_check.py, results/t1_span_check.json. Exact-rational (18-digit sqrt2
  enclosure) enumeration of S(o,r) = o sqrt2 + r for o >= 2, r >= 0, o + r <= 11: the live window
  [3.82, 969271/250000] is met at (o,r) = (2,1) ONLY (every other pair is decided "below" or
  "above" with a certified gap; no undecided pairs). S(2,2) = 4.8284 > s0 and S(3,0) = 4.2426 > s0
  confirmed exactly. So T1a is machine-checked; s* = 2 sqrt2 + 1 is the unique exception.
- TASK 2: the s*-exception lemma, certified by monotone rational relaxation + A08-style exact
  measure certificates with an OBSTACLE EXEMPTION rule. New code: sstar_geom.py (exact obstacle,
  containment proof), sstar_lp.py (LP producer + robust-row cutting plane), verify_measure_obs.py
  (certs/verify_measure.py subclassed; integer core imported verbatim; exemption added),
  run_sstar.py (driver, checkpointed per parameter box), sstar_collect.py, sstar_selfcheck.py.
- LEMMA (statement certified): for every y0 in [sqrt2/2, sqrt2+1/2] (up-down-symmetry half) and
  every b in [max(0,y0-1), y0], no 8 unit squares with pairwise disjoint interiors fit in [0,s*]^2
  while missing the interior of C(y0,b). => the s* structure admits no 11-packing completion, so
  the flush-free THIN branch is dead at EVERY s in [3.82, s0] with no exception left.
- Relaxation: lambda = 10001/10000 (scale-then-shrink, makes the 8 closed squares pairwise
  DISJOINT so point atoms cannot double-count), container s' = 383/100 >= lambda*s*, rational
  obstacle C_shr with inward margin delta = 1/256, containment C_shr subset int(lambda C) proved
  exactly per parameter box (endpoint + signed-sqrt2 bound, all Fractions, no sampling).
- 48 top-level parameter boxes (y0 step 1/8, b step 1/4) + 2 leftover refinements = 50 certificates,
  ALL PASS. Max total mass 7.8412 < 8 (worst box y0 in [0.70,0.825], b in [0,1/4] — the true corner
  y0 = sqrt2/2, b = 0, where the fractional packing number is genuinely ~7.68); margin 0.1588.
  Typical totals 4.08-7.14. Exact-verifier box counts 5.7k-244k, seconds per certificate.
- The verifier's EXEMPTION rule is the new machinery: a placement box is discharged when a rational
  point of C_shr is certified (exact interval predicate) to lie in Q(c,theta) for EVERY placement of
  the box. Producer/verifier loop: the verifier's failing boxes are fed back as ROBUST LP rows on a
  lattice aligned with the verifier's own dyadic box tree (a mis-aligned lattice stalls: failing
  boxes straddle two cells and are never patched — this was the one real engineering obstacle).
- Final audit: all 50 certificates re-verified from scratch in fresh processes (obstacle rebuilt and
  its containment proof re-run) + independent random-placement spot check (mass of every "free"
  placement evaluated exactly): all_pass = True. work/sstar/audit.json.
- Deliverables: results/t1_span_check.json, results/sstar_lemma.json, results/sstar_report.md
  (59 lines, verdict PROVED, no gaps); code/{t1_span_check,sstar_geom,sstar_lp,verify_measure_obs,
  run_sstar,sstar_collect,sstar_selfcheck,sstar_audit}.py; per-box certificates in work/sstar/.
  Nothing outside A47 touched; A29 untouched.
