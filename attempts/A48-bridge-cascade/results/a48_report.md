# A48 — I-L19 bridge-cascade descent: the cascade FORMALIZED and its local theory
# settled — R1/R2 proved in corrected form, R3 REFUTED as briefed (exact evasion
# found), R4 arithmetically unreachable (exact no-go) — the composed flush-mandatory
# theorem does NOT follow; I-L19 survives only as a global-realizability conjecture,
# now with the obstruction landscape mapped exactly
(Fable lead + one Opus canary agent, 2026-08-29)

Constants: s0 = 969271/250000 = 3.877084, B0 = s0^2 - 11 = 4.031780343056 (exact).
Full theory: notes/cascade_theory.md (sections cited as sect. N). All key
inequalities exact rational (Fractions, rational points on the unit circle);
certificates in results/*.json, re-verified by the corruption-gated standalone
checker code/checker_cascade.py (5/5 seeded corruptions caught).

## 1. Question and verdict

The brief asked for the cascade R1-R4 (strict blocker-slope recursion, no
interior termination, wall-lever collapse into lambda0 = 0/self-stress,
criticality-aware mid-tilt budget), composed with A47's thin-branch theorem,
=> no flush-free critical structure — or the honest gap/counterexample.

**Verdict in five lines.**
1. **R1 holds in a CORRECTED form and is exact** (Lemma C1): the bridge blocker's
   support edge is strictly steeper (g > d), and the strict inequality is
   EQUIVALENT to the contact being loaded — the positive control is perfect. But
   the naive reading (blocker CONTACT at strictly larger mismatch) is FALSE
   (the blocker contact mismatch is |g - d|, arbitrarily small): the monotone
   variable is the frame-propagated support SLOPE, not the per-contact mismatch.
2. **R2 holds where it matters**: the blocker menu is complete (W1.4), B2-chains
   can never cycle (a HEIGHT functional, unconditional on orientation — Lemma
   C2c), slopes strictly escalate on orientation-consistent segments (C2b), and
   B3 blockers also escalate strictly (C3, new). But the taxonomy contains ONE
   genuinely non-escalating branch: the B1 overhang press, legal at ANY
   (including same-class) mismatch.
3. **R3 is REFUTED as briefed** (sect. 4): (a) the wall-lever arm is sin(t_a) —
   the ABSOLUTE tilt of the corner square, not the mismatch: W1.4b's 1/sin d
   collapse silently assumed an axis-parallel receiving frame; (b) even in that
   worst frame, an exact evasion exists: a single presser at u = sin^2 d from
   the top-left corner balances the wall-blocked near-flush contact with
   BOUNDED multipliers (lambda_e = lambda_ab / cos d). Nothing forces
   lambda0 -> 0; wall termination is locally consistent at every d > 0. What
   survives is a CONFINEMENT lemma: the press position is pinned to O(d^2) of a
   corner — relative-coordinate pinning, unchargeable by the fourth-face law.
4. **R4 is arithmetically unreachable — an exact no-go theorem** (C6): the
   grant-all ceiling of every certified table (12 WC at max bin + 23 interiors
   at the CE cap + both zone maxima) is 242969807/64000000 = 3.7964 = 0.9416 B0
   < B0, robust to doubling the CE cap (3.9592 < B0). Since the cascade forces
   zero CC contacts and nothing near n_WC >= 10, NO criticality-aware budget
   composition on the existing certificate classes can close flush-mandatory —
   decidable a priori, independent of how sharp the forcing lemmas become.
5. **The composed theorem therefore FAILS, honestly**: a flush-free structure
   can route every rotational demand through B1 press chains and confined-
   presser wall terminations without ever generating a forced mid-tilt square,
   and each step of that routing is an exact FJ balance (verified). The ONLY
   remaining kill is global: can such routing close into a critical
   configuration of 11 disjoint squares at s <= s0? That is W1-G2, sharpened
   but open. I-L19's "globally self-defeating" clause is downgraded from
   candidate-theorem to conjecture-with-mapped-obstructions.

## 2. The cascade, step by step (status ledger)

| step | as briefed | status | corrected/actual statement |
|---|---|---|---|
| R1 strict recursion | blocker at mismatch/slope > d | PROVED (corrected) [X] | C1: support-edge slope g > d, IFF loaded; per-contact mismatch does NOT escalate (|g-d| free) |
| R1 for B3 | (not briefed) | PROVED, new [X] | C3: push-back partner class = a's class + psi, psi in (0,45) strict; the "upright neighbour's vertical edge" evasion violates the supporting cone |
| R2 no cycling | strict monotonicity | PROVED (stronger) [X] | C2c: B2-subgraph acyclic by HEIGHT descent, orientation-free; C2b slope monotonicity on orientation-consistent segments only (zig-zag gap A48-G4 — but zig-zags still cannot cycle) |
| R2 no interior termination | L1 + brace exclusion | PROVED as taxonomy | C2a: loaded squares always pass load on; termination only into {wall, B1, B3, B2-cc, pencil, B-bot}; pencil reduced codim >= 2 (W1.3) but NOT excluded (inherited W1-G1) |
| R3 wall-lever collapse | lambda ~ 1/sin d => lambda0 = 0 branch | REFUTED [X] | C5a: lever arm = sin(absolute tilt), collapse only in axis-parallel frames; C5b: presser-confinement evasion, bounded multipliers, u = sin^2 d exactly |
| R3' flush-free self-stress | constrain them | PARTIAL, new | C4: floating flush-free self-stresses are non-thin (loaded degree >= 3 somewhere); full exclusion open (A48-G3) |
| R4 mid-tilt budget | charge what the recursion forces | NO-GO PROVED [X] | C6/C6': ceiling 0.9416 B0 < B0 exact; cascade forces no CC, so the sharp-CC fire zone (needs >= 10 WC + >= 6 sharp-CC) is unreachable; budget route dead a priori |
| compose with T1 | => no flush-free critical structure | FAILS (honest gap) | all flush-free branches are non-thin (T1 + C4); the demand routing through B1 chains + confined-presser wall ends is locally consistent everywhere; only global realizability (W1-G2/A48-G1) can kill it |

## 3. What is genuinely new (banked)

1. **The demand-graph formalism** (sect. 0): cascade = finite directed graph on
   loaded CE/WC rows, demand edges from W1.2, (D-rot)/(D-force) interleaving.
   First precise statement of what "the recursion" IS; makes gaps nameable.
2. **C1 + C3, the two escalation channels, both strict and exact** — and the
   sharp negative that these are the ONLY escalating channels: B1 escalates
   nothing (any-mismatch overhang), wall nodes absorb (C5b), pencil/CC are
   codim branches.
3. **C2c height-acyclicity**: B2 cascades cannot cycle REGARDLESS of
   orientation zig-zags — the right functional is contact-point height, not
   slope; chains are <= 9 composite steps at s0. (I-L19's cycles/divergence
   worry is settled: no cycles, no divergence — termination into the taxonomy
   is the only option.)
4. **C5a generalized wall lever** (tau_wall = sin t_a): W1.4b's scope error
   found and fixed; wall-blocking is CHEAP in tilted frames. Every future use
   of the 1/sin d collapse must carry the axis-parallel-frame hypothesis.
5. **C5b presser confinement**: the first CRITICALITY-DERIVED position-forcing
   fact in the lab — near-flush + wall-blocked forces a press within sin^2 d
   of a specific corner. Relative-coordinate pinning (fourth-face-limited for
   budgets) but a genuine case-tree signature: wall-terminated near-flush
   nodes carry a near-CC degeneracy a node cover can split on.
6. **C4 non-thin self-stresses**: with A47's T1, EVERY branch of the
   flush-free problem (lambda0 > 0 and lambda0 = 0 alike) is non-thin.
7. **C6' the criticality Ceiling** (the R4 screening theorem): no future
   criticality-aware charging proposal is worth attempting unless it ships a
   NEW certificate class or provably forces >= 10 WC + >= 6 sharp-CCs. The
   analogue of A45's Ceiling 2, one level up.

## 4. Verification discipline (what was checked, how)

- Exact certificates (Fractions only, angles as rational points on the unit
  circle via tan-half parametrization): r1_bridge.json (42 (d,g) cases incl.
  adversarial g < d and the g = d flush exclusion; 8 C3 cone cases),
  r3_wall.json (15 C5a frames incl. tilted; 5 C5b evasions with the exact
  u = sin^2 d and the multi-presser weighted-mean identity), b2_chain.json
  (3 explicit 3-level orientation-consistent chains: per-level balance, strict
  slope increase, strict height descent), r4_nogo.json (ceiling read from the
  ACTUAL certified table files, exact maxima: w_WC 453/2048, corner 1749/2048
  over both indexings, side 4008341/32000000; CE cap 29/4096 + x2 robustness).
- Corruption-gated standalone checker (code/checker_cascade.py): independent
  algebra, re-verifies all three algebra certificates from JSON alone; 5/5
  seeded corruptions caught (sign flip, g<d swap, u perturbed 1e-6, height
  raised, multiplier zeroed). Log: logs/checker_gate.txt.
- Positive control (brief requirement): C1's formulas are exactly A46's bridge
  (W1.5) re-derived independently; lambda_ab > 0 iff g > d confirms R1
  describes precisely what the bridge needs.
- Canaries: all 36 atlas entries — 24 NOT-CP out of scope by class; 12 genuine
  entries flush-rich (flush-free hypothesis provably vacuous on every known
  critical structure), plus a REAL dichotomy audit: every loaded CE/WC row of
  every genuine entry checked against W1.2 numerically (blocker exists or
  pencil), with a flipped-sign negative control. Results:
  results/canary_cascade.json (float — the atlas is float; run by the Opus
  canary agent, summary in sect. 6).
- No prior attempt's files modified; A29 untouched; heavy compute: one Opus
  agent, one process.

## 5. Census / campaign value

- No census factor is claimed (the composition does not fire; pre-registered
  A43-H1 condition not met — same protocol as A47).
- Case-tree teeth (the deliverables a future tree can consume):
  (i) escalation rows: inside any node pinning a near-flush loaded CE contact
  and its frame, C1/C3 add certified valid inequalities "exists support edge at
  slope > d" recursively — free LP rows;
  (ii) C5b's near-CC signature at wall-terminated near-flush nodes — a
  codimension split;
  (iii) universal non-thinness (T1 + C4) — one more row class per flush-free
  profile;
  (iv) C6' as a screening test that will save future attempts from budget
  routes (this attempt would have been ~40% shorter had C6' existed first —
  recorded as method).
- The decisive next experiment for I-L19 (named): a targeted numerical hunt
  for a flush-free critical point built exactly on the two evasion branches
  (B1 press chains to the top wall + confined-presser wall terminations).
  Success = flush-mandatory is FALSE (a discovery); failure modes will show
  WHICH global constraint breaks the routing — the missing lemma. This is a
  drain-style compute attempt (A37 machinery), not a theory attempt.

## 6. Canary results (Opus agent) — ALL PASS (results/canary_cascade.json, float)

- Vacuity: all 12 genuine entries (RIGID/VALLEY/VALLEY-MARGINAL) are flush-RICH;
  contact reconstruction matches A46's mismatch audit exactly; the 24 NOT-CP
  entries are out of scope by class. Every A48 flush-free statement is provably
  vacuous on every known critical structure, as required.
- Dichotomy audit (the real canary): W1.2 verified on 65/65 loaded CE/WC rows
  across the 12 genuine entries — 45 blocker cases, 20 pencil cases, 0 failures;
  torque-identity residuals <= 1e-8; two independent tau derivations agree to
  3e-16. My torque conventions are consistent with the genuine data.
- Negative control: flipping the sign convention on received-contact rows makes
  12/65 rows fail the dichotomy — the checker is not vacuous.
- BONUS FINDING (unrequested, banked): all 20 atlas pencil cases are supported
  ENTIRELY by flush rows, and no pencil case occurs below mismatch 22.4 deg.
  Empirically, the pencil branch is a FLUSH ARTIFACT: in a flush-free structure
  the pencil option cannot be realized the way genuine CPs realize it — it must
  fall back to W1.3's codim >= 2 CC-brace signature. This strengthens the
  interior-termination step (T-d is doubly degenerate: codim >= 2 by theorem,
  and unobserved in nature away from flush support) — recorded in
  notes/cascade_theory.md sect. 3 addendum.

## 7. Gap list

- A48-G1 (sharpened W1-G2, THE gap): global realizability of a flush-free
  demand network at s <= s0. All local theory is now settled; any flush-free
  critical point must route demands via T-a/T-c; the hunt above is decisive.
- A48-G2: pencil/CC-brace towers (inherited W1-G1); codimension-growth
  observation unproved.
- A48-G3: flush-free compression self-stresses — non-thin (C4), existence
  open; relevant only to the lambda0 = 0 branch.
- A48-G4: C2b slope monotonicity is per orientation-consistent segment;
  zig-zag chains evade the slope functional (never the height one). An
  oriented functional would upgrade it.
- A48-G5: CE interior cap 29/4096 and CC cap 289/4096 quoted from A46's pilot
  (float provenance); C6 robust to doubling the CE cap, so the no-go verdict
  does not depend on exactification.
- Scope: everything here is per-selection FJ first-order + exact geometry;
  second-order/curvature arguments untouched (A44 showed they cannot force
  counting bounds either); nothing claimed below 3.82 or above s0.

## 8. Files

notes/cascade_theory.md (the theory: sects. 0-8), code/ (exact_trig.py,
verify_r1_bridge.py, verify_r3_wall.py, verify_b2_chain.py, verify_r4_nogo.py,
checker_cascade.py, canary_cascade.py [agent]), results/ (r1_bridge.json,
r3_wall.json, b2_chain.json, r4_nogo.json, canary_cascade.json, this report),
logs/ (checker_gate.txt, canary_run.txt), LOG.md.
