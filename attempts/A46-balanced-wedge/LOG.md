# A46 LOG (Fable lead)

2026-08-29 (session start)
- Read BRIEF, I-L17, A44/A45 reports + theory, structure_lemmas, drain_lemma v3, A35 theory,
  A23 notes, A45 README_A. Key imported facts: A45 Ceilings 1-3 (why raw charging is inert),
  A44 L8-L11 + C*/C-rep status, A23 certifier semantics + wall table 4a (0.19-0.36 at
  theta 20-35), L1/L2/L6/L11.
- W2 Opus agent launched (background): atlas mismatch audit, certified w_WC(phi) full-window
  table with radial profiles, composition verdict, CE/CC pilot, wall disjointness scheme,
  canaries. Constraints: <= 3 python processes, exact Fractions for shipped numbers, A29 and
  all prior attempt dirs untouched.
- W1 theory done first-pass -> notes/w1_theory.md. Headlines:
  * W1.0 taxonomy: interior corner-on-edge at mismatch 0 mod 90 IS flush; no T-contact
    loophole; zero-charge flush-free type = aligned CC only.
  * W1.1/W1.2 torque identity + blocking dichotomy [T]: loaded corner contact => pencil
    through q, or loaded blockers AND closers (two-signed torques) on the corner square.
  * W1.3 pencil => codim >= 2 double-brace signature (CC at q+e2a AND CC at q+e1a or
    exact-45 far-corner CE) [T, reduction; exclusion open = W1-G1].
  * W1.4 blocker taxonomy at small d; wall-lever collapse (wall blocking needs lambda ~
    1/sin d) [T].
  * W1.5 BRIDGE mechanism [MECH]: explicit exact FJ balance of the corner square at EVERY
    mismatch d > 0 with generic neighbours and bounded multipliers => W1 as stated is
    locally FALSE; survives only as an atlas-testable conjecture (W1-G2).
  * W1.6 thin-branch 45/0 QUANTIZATION [T]: flush-free degree-2 load chains force owners to
    tilt exactly 45 and receivers exactly 0; 3-chains impossible at s0 (2 sqrt2 + 1 =
    3.8284 < 3.877084); minimal thin profile = [45,0,0,45] with 2 WC(45) + 2 CE(45) +
    1 aligned-CC. Near-flush escape CLOSED on the thin branch without any delta_0.
  * W1.7 route (b) obituary: bounded multipliers, smooth limit onto flush stratum; no
    global delta_0 from compactness.
- Verdict shaping: I-L17 composed theorem will NOT close; deliverable = the dichotomy +
  certified tables + named gaps (W1-G1..G4 + W2's). Awaiting W2 numbers.
- code/w1_checks.py (exact Fractions, rational trig via tan-half): C1 bridge stationarity
  rows vanish EXACTLY with all multipliers > 0 at (d,g) tan-half pairs incl. (1/1000, 1/9)
  and the near-degenerate (7/100, 2/25); C2 full torque sign table of w1_theory par.4
  reproduced exactly; C3 ((s0-1)/2)^2 = 517350771441/250000000000 > 2 exactly => 2 sqrt2 + 1
  < s0 (3-chain impossibility). ALL PASS.

2026-08-29 (W2 landed; session close)
- W2 delivered: atlas mismatch audit (W1 REFUTED BY MEASUREMENT: loaded CE at 1.029 deg
  forced in A37-NEW-0, 2.272 in fam 31; all atlas CC aligned = 0), w_WC table 11/11 bins
  EXACT (869/869 tiles, max 453/2048 = 0.2212 at (40,45], radial profiles), CE <= 0.00708 /
  CC <= 0.0706 exact pilots + CC sharp-wedge convention correction (19x within a mismatch
  class), composition verdict (honest minima 4-6 contacts; NO delta_0 fires, shortfall
  x2.0-6.9 even at delta_0 = 45; CE-only ceiling 0.699*B0 table-independent; fire zone = 5
  fantasy count-points), canaries ALL PASS (Trump 0.4849 <= 4.0318, capture 12%).
- Final report written: results/a46_report.md. Registry updated (done-negative with
  theorems banked: W1.6 quantization, w_WC table, torque toolkit, CC convention, I-L18
  candidate = multi-square corner hypotheses, recorded NOT pursued). Post-measurement
  addendum added to w1_theory.md. No census run (theorem not proved — factor N/A).
- Constraints honoured: <= 4 heavy processes total (W2 used <= 3 python + this session),
  exact certification the arbiter, A29 and all prior attempts untouched.
