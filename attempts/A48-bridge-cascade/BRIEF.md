# A48 — I-L19: bridge-cascade descent (Fable lead)

Goal: the criticality-aware flush-mandatory route (docs/ideas.md I-L19, PI formulation — read
first): prove that a flush-free FJ-critical 11-configuration at s in [3.82, s0] cannot exist,
because sustaining all-near-flush balance requires bridge structures whose requirements are
globally self-defeating. This is the route untouched by all six closed faces: A44 closed
order-conditions-only; A45/A46/A47 budgets never used criticality.

Context (read in order): A46 notes/w1_theory.md (THE toolkit: W1.1 torque identity, W1.2 blocking
dichotomy, W1.3 pencil => codim-2 braces, the bridge mechanism's exact requirements, the wall-lever
collapse lambda ~ 1/sin delta), A47 results/a47_report.md (thin-branch THEOREM — done, compose with
it; the corner primitive table; the epsilon-parking analysis), A44 notes/theory.md (index identity,
L9' lambda0=0 => self-stress), structure_lemmas.md (L1/L2/L6/L7), drain_lemma.md v3, A37 atlas
(canaries — all flush-rich: your statements must be consistent/vacuous on all 36), A26 registry row
(tilt forcing: <= 9 squares within 2.503 deg of axis-parallel at s' — certified, use it).

## The cascade argument to build (or refute)
In a flush-free critical structure, every loaded contact is corner-type. Near-flush loaded contacts
need blockers (W1.2); formalize and prove the recursion: (R1) a blocker of a mismatch-delta contact
must itself be loaded at mismatch/slope STRICTLY greater (quantify from the torque identity —
the g > d inequality in the bridge analysis); (R2) the recursion cannot cycle (strict monotonicity)
and cannot terminate in the interior (L1 + the pencil/brace codim-2 exclusion — handle that branch:
prove braces need their own support or are excludable at s0); (R3) termination at walls: wall
blocking of a near-flush contact costs lambda ~ 1/sin delta — under the FJ normalization this
forces lambda0 -> 0, i.e. the lambda0 = 0 branch, which needs a self-stress (A44 L9'); flush-free
self-stresses: constrain them (do flush-free compression self-stresses exist? attack with the same
toolkit — or show they force mid-tilt structure that the corner/wedge tables CAN charge). (R4) the
mid-tilt anchor: the recursion's strictly-increasing mismatches reach the mid-tilt regime, where
A26's tilt-forcing caps the near-upright population (<= 9 within 2.503 deg) and A47's corner table +
A46's w_WC table have real teeth — compose a criticality-aware budget on the mid-tilt END of the
cascade (charging only what the recursion FORCES to be mid-tilt, with the certified tables).
Compose R1-R4 + the thin-branch theorem => no flush-free critical structure. Or find the honest
gap/counterexample — a globally-embedded flush-free critical configuration would be a discovery.

## Verification discipline
Key inequalities (the g > d recursion step, the wall-lever collapse, brace exclusion) verified in
exact rational arithmetic on parametrized families; the bridge mechanism is the positive control
(your R1 must correctly describe what it needs); atlas canaries all 36; any new certificate class
gets a standalone corruption-gated checker. Opus subagents for verification compute; <= 4 heavy
processes; ONE long-poll waiter per background run; checkpoints; A29 untouched. Honest failure =
success, as always: if a step is unprovable, name the exact gap and what would settle it.
Registry, LOG, ideas.md status, PI-readable report.
