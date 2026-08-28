# A39 method notes — certification-in-the-loop (P2a) and the s-hat field reseal (P2b)

## P2a — the rule change

A27/A38 decide a node only after the row-generation LP CONVERGES:

    kill  <=>  added_rows == 0 AND minmass >= 1 AND tau < budget          (A27 run_l1.classify)

A38 measured 0 decisions in 60 depth-2/3 nodes at s0 = 969271/250000 under that rule, at
180-485 s/node, with tau sitting 0.5-1.5 BELOW budget the whole time. The LP never stabilises;
the rule never gets to ask its question.

A39's rule asks a DIFFERENT question, after every row-generation round:

    is the CURRENT (unconverged) atom vector, scaled up and rounded to rationals, an exact
    certificate?  -> verify_case.py (exact interval/rational B&B) says PASS or FAIL.

A PASS is a standalone kill: the certificate is a finite rational measure plus the node's rational
cores; the verifier checks "every non-exempt closed unit square carries mass >= 1" and
"total < budget". Neither statement mentions the LP, its convergence, its row oracle or its float
arithmetic. A FAIL returns witness placements — precisely the holes the float row oracle missed —
which are fed back into the SAME warm model as new rows (plus a +-0.002/+-0.005 neighbourhood in
(cx, cy, theta)), so every failed attempt is paid back as row information.

Implementation: `lpbox.run(..., round_hook=)` (the only edit to the A27/A38 LP driver, mirroring
A38's single `ROW_EXEMPT` edit), `earlycert.EarlyCertifier` as the hook, `earlycert.certify_cached`
for the cheap probe on an already-solved node.

Cost model (measured, A38's own sample): a verifier run on a node certificate costs 0.6-14 s.
A38's certification cost of 300-600 s/node was NOT the verifier — it was `certify.py`'s separate
re-solve at eps_geo = 0.003 before certifying. A39 drops that re-solve.

### Deviations, recorded

1. The W1/W2 field ROW filter is OFF inside the early-cert loop. A certificate built from a
   W1-filtered LP is not checkable by verify_case (which exempts only cores and NO-families);
   certifying one would need W1's soundness argument inside the verifier. A38-G2 measured the row
   filter at 0.28% of rows and delta-tau = 0, so nothing is lost. The W1/W2 whole-box NODE kill
   (no LP at all) stays ON — it is free.
2. eps_geo stays at A38's 1e-4 (not certify.py's 0.003). The 3% weight scale supplies the
   robustness; raising eps_geo raises tau, and at s0 tau headroom (budget - tau = 0.5-1.5) is the
   scarce resource. Evidence: all 38 G1-debt nodes certify from their eps_geo = 1e-4 LP, whereas
   A38's eps_geo = 0.003 re-solve pushed two of them (nodes 50, 93) to tau ~9.9 and lost them.
3. Scale is chosen automatically per attempt: sc = min(1.03, (budget - 0.004)/tau), attempt
   skipped if sc < 1.0008.

### Honest accounting of time-to-decision

Stage A decisions consume only a verifier run on an LP A38 had ALREADY paid for. Two numbers are
reported everywhere:
  * t_marginal — A39 seconds on top of A38's cached LP;
  * t_total    — A38's cached node seconds + t_marginal, i.e. what a from-scratch node costs if
                 you run A38's LP and then A39's rule.
Stage C runs a stratum FROM SCRATCH under the A39 rule with no warm start, which is the
extrapolation frame's honest cost/node.

## P2b — the reseal

The A38 guard field is A33's `A33_measure_feasible_3.877084.json`: exact total 44630467/3906250 =
11.4254, eta_cert = 0.4254, over a float LP field of tau = 11.2448 (eta_float = 0.2448). The whole
0.18 gap is the UNIFORM sealing scale 127/125 = 1.016 that the exact verifier demanded.

Reseal loop (A33 t2/refine_384.py pattern, at s0, from A33's r7 checkpoint: 26894 rows,
3349 atom orbits): verify the current field's certificate AT THE TARGET SCALE -> harvest the
deficit witnesses -> add them and their D4 images as LP rows -> re-solve min sum m_i w_i s.t.
mu(Q_row) >= 1 -> repeat. Adding rows raises tau but removes the exact deficits, so the sealing
scale falls faster than tau rises — that is the whole bet, and it is the bet A33 lost at 3.84
(8 iterations moved eta_cert only 0.3776 -> 0.3229, blocked by a single tangency cluster).

Note on why a uniform RHS margin buys nothing: the LP min{ sum m_i w_i : A w >= 1 } is positively
homogeneous, so requiring mu >= 1 + delta on the rows multiplies the optimum by exactly (1+delta).
Only BETTER ROWS (a smaller true deficit) can shrink the seal.

## P2b(ii) — W1's first-kill depth, measured not projected

A38 projected W1's onset at depth 5-7 by extrapolating the MEDIAN c_core trend. `w1_depth.py`
measures it instead: from each level-1 survivor box it beam-descends the A38 tree's own child rule
(bisect x, y and theta simultaneously = 8 children), keeping the top 8 children by
c_core = m_low(box inflated by one grid cell), and records the first depth at which some box
exceeds thr = 1 + eta. The beam under-explores the octree, so the reported first-kill depth is an
UPPER bound on the true one — one-sided in the honest direction.
