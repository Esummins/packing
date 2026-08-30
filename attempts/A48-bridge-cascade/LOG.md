# A48 LOG (Fable lead)

2026-08-29 ~15:40  Context read (BRIEF, I-L19, A46 w1_theory, A47 report, A44 theory,
structure_lemmas, drain_lemma v3, A26 registry row, A37 atlas + A46 mismatch audit,
w_WC table). NOTE: first pass at the theory doc was lost to the output-token cap
(one giant Write — coordinator terminated the turn). Rebuilding in chunks from here.

Plan of record:
1. notes/cascade_theory.md — demand-graph formalism; R1 step lemma (g > d strict,
   equiv to loaded bridge); B2-chain slope monotonicity with frame propagation;
   R2 = menu completeness + no-B2-cycles + branch taxonomy; R3 findings (generalized
   wall lever tau = sin t_a; presser-confinement evasion u = sin^2 d — R3-as-briefed
   looks REFUTED pointwise, to be verified exactly); R4 no-go (grant-all ceiling
   0.941 B0 already < B0 => budget cannot close regardless of forcing).
2. code/: verify_r1_bridge.py, verify_r3_wall.py, verify_b2_chain.py (all exact
   Fractions, rational-angle parametrizations), verify_r4_nogo.py (exact table
   arithmetic), checker_cascade.py (corruption-gated standalone checker for the
   chain-balance certificates).
3. Opus subagent: canary run on all 36 atlas entries (12 genuine: dichotomy W1.2
   satisfied numerically at every loaded CE/WC row; flush-richness => vacuity;
   24 NOT-CP vacuous by class). Reuses A46 task1_audit.py machinery.
4. results/a48_report.md (chunked), registry row, ideas.md I-L19 status.

Key early findings (to verify before banking):
- F1: wall-lever torque arm is sin(t_a) (ABSOLUTE tilt of the corner square), not
  sin(mismatch): W1.4b's 1/sin d collapse only bites when the receiving frame is
  near-axis-parallel.
- F2: even in the axis-parallel frame, a single presser at u = sin^2 d from the
  top-left corner balances a wall-blocked near-flush contact with BOUNDED
  multipliers (lambda_e = lambda_ab / cos d): R3-as-briefed (lambda0 -> 0 forced)
  fails pointwise; what IS forced is O(d^2) position confinement of the presser.
- F3: A47's grant-all ceiling (0.941 B0, exact) upper-bounds ANY criticality-aware
  charge composition on the certified tables => R4-as-budget cannot close. The
  composed theorem as briefed is arithmetically unreachable with current tables;
  value of the cascade = structural (branch taxonomy + forced substructures).

2026-08-29 ~16:20  Theory doc complete (notes/cascade_theory.md, sects. 0-8:
C1-C6' + refutations + taxonomy). All four exact verifiers PASS:
- r1_bridge: 42 (d,g) cases + 8 C3 cases (C1 strict step, cone, flush exclusion,
  exact 3-row stationarity, lam>0 iff g>d; C3 escalation psi in (0,45), vertical
  evasion violates cone).
- r3_wall: 15 C5a (tau_wall = sin(t_a) incl. tilted frames) + 5 C5b (u = sin^2 d
  evasion, bounded multipliers, weighted-mean confinement). R3-as-briefed REFUTED.
- b2_chain: 3 chains x 3 levels (slope monotone, height descent, per-level balance).
- r4_nogo: ceiling = 242969807/64000000 = 3.796403 = 0.94162 B0 < B0 exact;
  doubled-CE variant 3.9592 < B0; all-sharp-CC 5.256 (unreachable fire zone).
Checker: 3 certificates re-verified standalone, 5/5 corruptions caught
(logs/checker_gate.txt). Opus canary agent launched (background, 36 atlas
entries: vacuity + W1.2 dichotomy audit + negative control). Report drafted
(results/a48_report.md), canary section pending agent.

2026-08-29 ~16:45  Canary agent landed: ALL PASS. 12 genuine entries flush-rich
(vacuity; contact reconstruction matches A46 audit exactly); W1.2 dichotomy
65/65 loaded CE/WC rows (45 blocker / 20 pencil / 0 fail; residuals <= 1e-8;
two tau derivations agree to 3e-16); negative control fires (12/65 fail under
sign flip). BONUS: all 20 pencil cases supported entirely by flush rows, none
below 22.4 deg mismatch — pencil branch is empirically a flush artifact
(addendum added to notes/cascade_theory.md sect. 3). Report sect. 6 filled;
ideas.md I-L19 downgraded to global-realizability conjecture; REGISTRY row
updated to done-negative. A48 CLOSED. A29 untouched throughout; no prior
attempt's files modified (docs/ideas.md status edit + REGISTRY row only).
