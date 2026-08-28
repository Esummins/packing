# A39 — certification-in-the-loop (P2a) + s-hat field reseal (P2b): report

Opus lead, 2026-08-28. Numbers from results/a39_summary.json; method in notes/method.md; every
exact claim logged in notes/verification_log.md. A29 untouched.

## 0. What A38 left and what A39 was asked

A38 closed NO-GO at s0 = 969271/250000 = 3.877084 naming the per-node LP DECISION COST as the
assassin (0 decisions in 60 depth-2/3 nodes at 180-485 s/node), and named two levers:
L1 = reclaim A33's sealing margin (eta_cert 0.4254 -> ~0.26), L2 = a decision rule that does not
need row-convergence. A39 measures both, plus A38's G1 certification debt.

## 1. HEADLINE — the three numbers that re-run A38's GO/NO-GO arithmetic

| quantity | A38 | A39 |
|---|---|---|
| **depth-2 decided fraction** | **0/49** | **1/49 = 0.020** (95% CI 0.004-0.107) |
| **depth-2 median time-to-decision** | undefined (0 decisions at 180-485 s/node) | **0.9 s marginal / 194 s total** (n = 1) |
| **new eta_cert of the s-hat guard field** | 0.425400 | **0.402957** (standalone PASS; target 0.30 shown UNREACHABLE) |
| **W1 first-kill depth (measured, median over 120 survivors)** | "projected 5-7" | **5 — UNCHANGED by the reseal** |
| level-1 CERTIFIED kill fraction f1 (over 134 processed) | 0.045 (6/134; 0.328 "optimistic") | 0.351 (47/134), all exact |
| level-1 b_eff = 8(1-f1) | 7.64 certified / 5.37 optimistic | 5.19, certified |
| depth-2 b_eff | 8.00 | 7.84 |
| median depth-2 node cost | 204 s (A38 LP), 0 decisions | 635 s from scratch WITH the loop, 0 decisions |
| cost of one exact node certification | assumed 300-600 s | **0.6-16 s** |
| A38-G1 certification debt | 38 nodes open, 2/8 sampled FAILED | **CLOSED: 38/38 certified in 73 s; the 2 failures refuted** |

Plain language: **the rule change converts level 1 completely and does not crack depth 2, and the
reseal does not move W1.** At level 1 the A39 rule turns A38's optimistic-but-uncertified 0.328
into a fully certified 0.351 for 517 s of extra compute over the entire 216-cell sweep — a clean
win, and it closes A38's G1 debt outright. At depth 2 it buys one node out of 49, and that one
came free from A38's own cached LP rather than from the loop. Both named levers are now measured:
**L2 (the rule) is real but confined to level 1; L1 (the reseal) is worth 0.022 of eta and ZERO
depths of W1 onset, not the ~0.18 and 2 depths A38 assumed. A38's NO-GO at s-hat stands, and its
two named escape routes are closed.**

## 2. G1 — the certification debt is DISCHARGED, and A38's headline certification finding is WRONG

`code/g1_debt.py` -> results/p2a/g1/g1_debt.json; audit V1-V3 in notes/verification_log.md.

**38/38 of A38's uncertified level-1 kill(LP) nodes are exactly certified, in 73 s of wall clock
on 2 workers (median 2.1 s/node, max 13.7 s).** Every one passed at round 0 — no witness feedback
was needed at all. Together with A38's own 6, all 44 level-1 dead(T1) nodes at s0 are now exact
certificates. A38-G1 is CLOSED.

**Correction to A38 section 5 (the "CERTIFICATION FINDING (headline)").** A38 reported that 2 of
its 8 sampled level-1 kills FAILED exact certification and concluded that A27's float
classification rule is insufficient at s0. Both of those nodes (50 and 93) certify here in
5.4 s and 3.4 s, and were independently re-verified with A38's OWN unmodified verifier at
depth 64 (node 50: total 4635001/500000 = 9.270002 < 10, 179712 boxes; node 93: 927047/100000).
The failures were an artefact of `certify.py`'s preparatory re-solve at eps_geo = 0.003, which
moved node 50's tau from 9.000000 to 9.940083 and left the certificate 0.010 under the budget.
The kills were real; what A38 could not afford was its own re-solve. Consequently A38's adopted
policy — "exact-certification-in-the-loop is the only kill accounting (measured cost:
certification becomes a first-class node cost)" — is right about the policy and wrong about the
cost: **exact certification of a node at s0 costs 0.6-14 s, not 300-600 s.**

## 3. P2a — certification-in-the-loop

### 3.1 Level 1: 3 free kills the convergence rule threw away
`code/l1_probe_all.py`. One certification attempt on the cached LP of all 90 processed level-1
nodes that A27 did NOT call dead: **3 PASS** (nodes 14, 31, 32 — all A38-"undecided"), 444 s total,
median 2.2 s/node. 34 of the 90 were skipped without a verifier run because tau >= budget leaves no
room for any scale > 1.

Level-1 totals under the A39 rule: 47/134 certified dead (0.351), f1 over all 216 = 0.218,
b_eff = 5.19 — and every one is an exact certificate, so the level-1 row of A38's kill matrix now
needs no certification caveat.

### 3.2 The certification boundary at s0 is tau, not convergence
Of the 134 processed level-1 nodes, 51 have tau = 9.000000 exactly and 41 of those certify;
6 more certify at tau slightly above 9; **no node with tau >= 9.25 certified at any budget we
gave it.** Median tau of the certified set is 9.000, of the uncertified set 9.846.
The certificate needs tau * scale < budget with scale >= 1 and, in practice, scale ~ 1.03 for the
rounding and boundary margin: at budget 10 that is tau <~ 9.7. Certification is therefore a
MARGIN test, and s0's depth nodes sit against the margin.

### 3.3 Depth 2: the loop runs, and the margin closes against it
A38's depth-2 stratified sample (49 processed children of 10 parents; A38: 0/49 decided at a
180 s cap, median 204 s/node).

* Stage A (one verifier run on A38's CACHED LP, marginal cost only): **1/49 certified**
  (l2_p95_000, 0.9 s, 9 atoms, total 9.270005 < 10). A38 never asked this question.
* Stage B (the full loop, warm-started from A38's checkpoints, 180 s cap, certification attempted
  after EVERY row-generation round): 20 nodes completed before the run was cut for machine time;
  **0 decided.** Median 2 certification attempts inside the cap (LP rounds cost 30-90 s, verifier
  attempts 5-15 s), median 178 witness rows fed back.
* Stage C (COLD — from scratch under the A39 rule, no A38 warm start, 480 s cap): 6 nodes,
  **0 decided**, median 635 s/node, **median 13.5 exact certification attempts per node**
  (range 10-18), median 1230 witness rows fed back, and the verifier consumed a median of 23% of
  node wall time. This is also the A38-G7 calibration datum: at s0 a depth-2 node does not decide
  in 500-800 s even when it is offered a dozen and a half exact certification chances.

**Two distinct blockers, neither of which is A38's "cost".** Over the 26 loop nodes the median
delta-tau across a node's attempts is **+0.115 (19 of 26 up, 2 down)**:

  (a) MARGIN. On nodes whose LP optimum is already near the budget, the witness feedback does
      exactly what it should — it repairs the holes the float row oracle missed — and every repair
      RAISES tau, so the headroom budget - tau*scale closes. Trajectory of l2_p114_011:
      tau 9.422 -> 9.526 -> 9.442 -> 9.545 -> 9.590, certificate total 9.705 -> ... -> 9.878
      against budget 10. At level 1 this blocker is already binding for 34 of the 90 non-dead
      nodes, whose tau >= budget leaves no room for ANY scale > 1.
  (b) GENUINE NON-COVERAGE. The other mode is not margin at all: 4 of the 6 cold nodes ended at
      tau = 9.000-9.134 with certificate totals 9.27-9.36 — the SAME numbers as the level-1 nodes
      that certify in 2 s — and still failed, with residual minmass 0.0-0.6. Their measures are
      simply not feasible, and 10-18 rounds of exact witness feedback did not make them so. The
      geometric reason is that a depth-2 core box is 8x smaller than its level-1 parent's, so it
      exempts far less: the SAME budget must now cover a strictly larger admissible set.

So the honest replacement for A38's verdict at depth is: **the level-1 kills were never a cost
problem (they certify in seconds), and the depth-2 failures are not a certification-cost problem
either — they are a margin/feasibility problem that more certification attempts cannot fix.**

### 3.4 The honest new triple for the extrapolation frame

| | A38 | A39 |
|---|---|---|
| f_certified (level 1, over processed) | 0.045 | **0.351** |
| f_certified (depth 2) | 0.0 | **0.020** (95% CI 0.004-0.107) |
| b_eff (level 1) | 7.64 certified / 5.37 optimistic | **5.19 certified** |
| b_eff (depth 2) | 8.00 | **7.84** (pessimistic 7.97) |
| cost/node, depth 2, from scratch, WITH certification | 204 s, 0 decisions | **635 s, 0 decisions** |
| cost of certification per attempt | assumed 300-600 s | **0.6-16 s** (23% of node time at 13.5 attempts) |

The frontier arithmetic barely moves. A38's level-1 survivor count 172 drops to **169** (the 3 new
kills come out of the survivor pool), and at b_eff = 7.84 instead of 8.00 the frontier is
169 * 7.84^2 = 1.04e4 at depth 3 (A38: 1.1e4), 8.1e4 at depth 4 (A38: 8.8e4) and 6.4e5 at depth 5
(A38: 7.0e5) — a 9% saving. Meanwhile the per-node cost went UP, 500 s -> 635 s from scratch,
because the loop pays for certification attempts that do not fire.
**A38's NO-GO stands; L2 is measured and it is not the missing lever.**

## 4. P2b — the reseal: **eta_cert 0.425400 -> 0.402957, and the 0.30 target is UNREACHABLE**

`code/reseal_shat.py`, `code/seal_scan.py` -> results/p2b/. The artifact is
**results/p2b/certs/A39_measure_feasible_3.877084.json, exact total 71268483/6250000 =
11.402957280, eta_cert(s0) = 0.402957280, STANDALONE PASS at depth 50 with no flags
(9,443,960 boxes, 150 s).** It supersedes A33's 11.4254 field for W1/W2 use.

Where the 0.022 came from, and where the rest did not:

* **The re-solve, not the row loop.** Rebuilding A33's r7 LP (26894 rows, 3349 atom orbits;
  15 min, warm-crashed from A33's own weights) reproduces tau = 11.244816546 EXACTLY (A33 r7:
  11.244816546 — a clean audit of the whole pipeline). That field's certificate seals at
  scale 507/500 = 1.014 (PASS, 145 s) and fails at 253/250 = 1.012 and at 126/125 = 1.008.
  A33's sealed field needed 127/125 = 1.016. So a fresh re-solve + fresh jitter alone is worth
  eta 0.4254 -> 0.4030.
* **The verifier-in-the-loop row generation FAILED, and made things worse.** Five iterations at
  the target scale 251/250 = 1.004 (verify -> harvest -> +D4 rows -> re-solve; 26894 -> 31510
  rows, ~5000 witness rows added):

  | it | tau | total@1 | verify @1.004 | witnesses |
  |---|---|---|---|---|
  | 0 | 11.2448165 | 11.245520 | FAIL (189 s) | 196 |
  | 1 | 11.2448592 | 11.245676 | FAIL (221 s) | 216 |
  | 2 | 11.2448940 | 11.245844 | FAIL (415 s) | 168 |
  | 3 | 11.2449693 | 11.245764 | FAIL (843 s) | 168 |
  | 4 | 11.2449927 | 11.245832 | FAIL (228 s) | 120 |

  tau is essentially frozen (+2.5e-5 over five iterations) and the deficit count wanders
  196 -> 216 -> 168 -> 168 -> 120 rather than collapsing — A33's "the pockets MOVE between cuts"
  at 3.84, reproduced at s0. Worse, the it4 field's certificate seals only at 51/50 = 1.020
  (eta 0.4707): the extra rows push the LP to a different vertex that is tight in more places,
  so its unmodelled holes are DEEPER. **The row loop is not merely ineffective here, it is
  counterproductive**; the best A39 artifact is the it0 (no-extra-rows) field.
* **The 0.30 target is out of reach for this field family, and that is now a measurement, not a
  guess.** Any certificate from this LP has total@1 ~ 11.2455, so eta <= 0.30 requires a sealing
  scale <= 11.30/11.2455 = 1.0049. Scale 1.008 FAILS on the best field we have. Hence
  **eta_cert(s0) >= 0.335 for anything reachable by re-sealing this field**; the target 0.30 and
  the stretch 0.27 are excluded. Getting below 0.335 needs a genuinely different field (more atom
  orbits / column generation at s0), not a better seal. A33-G5/G6 are therefore REFRAMED, not
  closed: the reclaimable margin is ~0.02 by re-sealing, not the ~0.18 A38 assumed.

## 5. P2b(ii) — W1's first-kill depth, measured instead of projected
`code/w1_depth.py` -> results/p2b/w1_depth_baseline.json. From 120 level-1 survivor boxes, a
beam-16 descent over the A38 tree's own 8-way child rule, recording the first depth at which some
descendant box is entirely exempt at threshold 1 + eta (the beam under-explores, so every depth
below is an UPPER bound on the true first-kill depth and every fraction a lower bound):

| thr = 1 + eta | eta | parents ever killed (of 120) | first-kill depth min / median / max |
|---|---|---|---|
| 1.425400 (A33 sealed, current) | 0.4254 | 24 (20.0%) | 4 / **5** / 8 |
| 1.350000 | 0.35 | 39 (32.5%) | 3 / **5** / 9 |
| 1.300000 (P2b target) | 0.30 | 48 (40.0%) | 3 / **4** / 8 |
| 1.270000 (P2b stretch) | 0.27 | 59 (49.2%) | 2 / **4** / 7 |
| 1.244800 (eta_float floor, unreachable) | 0.2448 | 68 (56.7%) | 2 / **4** / 6 |

max c_core over the beam by depth: 1.277 (d2), 1.369 (d3), 1.497 (d4), 1.531 (d5), 1.583 (d6),
1.594 (d7-d9) — it saturates near 1.6, which is why no threshold above ~1.6 can ever fire.

On the **actual resealed field** (results/p2b/w1_depth_resealed.json; both the threshold AND the
m_low grid change, so this is the real answer, not a threshold sensitivity):

| field | eta | parents ever killed (of 120) | first-kill depth min / median / max |
|---|---|---|---|
| A33 sealed (old) | 0.425400 | 23 (19.2%) | 4 / **5** / 7 |
| A39 sealed (new) | 0.402957 | 29 (24.2%) | 4 / **5** / 8 |

**THE NEW W1 FIRST-KILL DEPTH IS 5 — UNCHANGED.** The reseal buys +26% relative coverage
(19.2% -> 24.2% of level-1 survivors ever see a W1 kill) and no depth at all. Getting to depth 4
needs eta <= 0.30, and section 4 shows eta <= 0.335 is unreachable by re-sealing this field.

**Correction to A38's L1 lever estimate.** A38 claimed the resealed threshold would pull W1's kill
onset "~2 depths earlier (~64x fewer frontier nodes)". Measured directly, even the hypothetical
eta = 0.30 buys **ONE depth** (median 5 -> 4, i.e. ~8x, not 64x), the eta_float floor 0.2448 buys
no more, and the eta actually achieved (0.4030) buys **ZERO depths**. What the reseal does buy is
coverage, not onset. L1 as A38 sized it does not exist.

## 6. Honest failures

1. **P2a did not crack depth 2.** 1/49, and the one kill came free from A38's cached LP, not from
   the loop. 26 loop nodes (20 warm + 6 cold), 0 decided, up to 18 exact certification attempts
   each. The pre-registered hope — that early certification would convert A38's 0/60 into a usable
   decided fraction — FAILS.
2. **The per-node cost went up, not down.** From scratch under the A39 rule a depth-2 node costs
   635 s (median) vs A38's ~500 s, because certification attempts are paid whether or not they
   fire (23% of node wall time at 13.5 attempts/node).
3. **A38's L1 lever was over-estimated and A39 says so with a measurement.** The reseal buys ONE
   depth of W1 onset (median 5 -> 4), not two; ~8x, not ~64x.
4. **The loop does not crack level-1 undecided nodes either.** 10 sampled level-1 undecided nodes,
   480 s cap, 9 completed (the 10th was killed after 45 min, three times its cap), median
   527 s/node, median 4.5 certification attempts on the 6 that had any headroom: **0 kills.** One node (l1_075) was decided the OTHER way — its LP converged to alive(LP) in
   34 s. The margin mechanism is visible here too: l1_008's tau rose 9.633 -> 10.000 (= budget)
   under witness feedback, i.e. the loop certified the node OUT of certifiability. Three earlier
   attempts at this population were killed by the machine's shared memory ceiling while the P2b
   LP held ~1.7 GB and had to be re-run.
5. **l2 stage B ran 20 of 48 nodes**, not all 48; the run was cut for machine time after the
   result had been uniform for 20 nodes. The decided fraction is quoted over all 49 (stage A
   covers all of them); the LOOP statistic is 0/26 (20 warm + 6 cold), CI accordingly wider.
6. **The A39 rule is not a strictly better rule.** It is strictly better at level 1 and strictly
   worse in cost at depth. A production tree should gate it on tau: attempt certification only
   when tau*1.005 < budget (34 of 90 level-1 nodes and a growing share at depth fail that test
   before any verifier call).
7. **Two soundness-neutral deviations** are recorded in notes/method.md: the W1/W2 ROW filter is
   off inside the loop (the certificate would not be checkable by verify_case otherwise; A38-G2
   measured the filter at delta-tau = 0), and eps_geo stays at 1e-4 rather than certify.py's 0.003
   (this is what rescued the two nodes A38 lost, see section 2).

## 7. Gap list

- **A39-G1** (carry from A38-G2/G3): the depth-2 statistic is 0/26 loop nodes; the binomial 95%
  upper bound on the loop's decided fraction is 0.13. No positive decided fraction was measured at
  depth under any rule at s0.
- **A39-G2**: stage B ran 20/48 warm nodes; the remaining 28 are unmeasured under the loop.
- **A39-G3**: the level-1-undecided loop covers 10 of 85 nodes (0 kills, 1 alive(LP)); the other
  75 have only the stage-A probe.
- **A39-G7**: the long-limit calibration (1 depth-2 node at a 1800 s cap) DID NOT TERMINATE — it
  was killed after 105 min having completed exactly ONE certification attempt (cert total
  9.785516 < 10, FAIL, 48 witnesses, 6 s of verifier time). A single row-generation round at
  depth 2 at s0 can exceed an hour once the witness rows are in, which is itself the sharpest
  form of A38-G7's answer: T_decide(s0) at depth 2 is not bounded by anything we could measure.
- **A39-G4**: the machine's shared memory ceiling (~4 GB across sandboxed processes) forced
  serialization; three runs were lost to MemoryError and re-run. Not a mathematical gap, but it
  bounds what a single desktop session can measure.
- **A39-G5**: W1's first-kill depth is measured with a beam-16 descent, which under-explores the
  8^d octree; the reported depths are UPPER bounds and the killed-parent fractions LOWER bounds.
  A full-octree measurement to depth 5 (8^4 = 4096 boxes/parent, ~5e5 m_low evaluations) is cheap
  and would tighten both.
- **A39-G6**: the W1 sensitivity table is computed on the CURRENT field's m_low; a resealed field
  has different atoms, so its c_core values (not just its threshold) change. The table is
  therefore a threshold sensitivity, not a full reseal simulation.
- Carry-ins still open: A38-G4 (seam probe A unconverged), A38-G5 (W2 at second-core scale),
  A38-G6 (82 unmeasured level-1 corner nodes), A33-G5/G6 (REFRAMED, see section 4), A37 G-1..5,
  T0 S1-S8.

## 8. What A39 says about the next move

Two of A38's three named levers are now measured and neither rescues the far field:
* **L1 (reseal)** — worth 0.022 of eta, zero depths of W1 onset, and the 0.30 target is provably
  out of reach for this field. Any further eta gain needs a NEW field at s0 (column generation over
  more atom orbits), not a better seal. Prior: A33's LP already converged in columns.
* **L2 (early certification)** — real, cheap and decisive at level 1, silent at depth. It should be
  adopted as standard practice (it is free: gate it on tau*1.005 < budget and it costs seconds),
  but it does not change the frontier.
* **L3 (warm-started/inherited row systems)** — untested here; A39's warm nodes got 2 attempts and
  its cold nodes 13.5, which suggests inheritance mostly buys ROWS, not decisions, since the cold
  nodes with more attempts still failed.

The measurement that would actually matter next is the one A39 stumbled into: at depth 2 the LP
optimum sits at tau ~ 9.0-10.0 against budget 10, and BOTH failure modes are about that number.
A weapon that lowers the node budget (an occupancy/pigeonhole argument that accounts for a second
square, e.g. A41's S11 zone-assignment collapse) attacks the actual binding quantity; more
certification, more time and a better seal demonstrably do not.

## 9. Files

- code/: `earlycert.py` (the rule), `lpbox.py`/`caselp.py` (the single `round_hook` edit),
  `g1_debt.py`, `l1_probe_all.py`, `p2a_run.py`, `reseal_shat.py`, `seal_scan.py`, `w1_depth.py`,
  `summarize39.py`, `run_p2a_all.sh`, `run_tail.sh`; the rest are A38 copies.
- results/a39_summary.json (every number in this report), results/a39_report.md.
- results/p2a/{g1,l1all,l2,l1u,l2_long}/ — ledgers, per-node records, and every certificate.
- results/p2b/ — five loop fields, their certificates and verifier reports, the two seal scans,
  the W1 depth scans, and **certs/A39_measure_feasible_3.877084.json** (the new sealed field).
- notes/method.md (rule, deviations, honest accounting), notes/verification_log.md (V1-V6).
- logs/.
