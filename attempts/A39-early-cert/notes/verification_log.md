# A39 verification log (exact verifier is the sole arbiter)

Every claim below is a machine-checked exact statement. Nothing here rests on a float LP's
convergence flag, minmass, maxcov, or on A27's classification rule.

## V1 — G1 debt: 38/38 certified
`code/g1_debt.py`, results/p2a/g1/g1_debt.json.
Each of A38's 38 uncertified level-1 kill(LP) nodes: ONE `verify_case.py` run at depth 56 on a
certificate built from the CACHED A38 node LP (weights x auto scale <= 1.03, rounded up to 1e-6,
atoms rounded to 1e-6). All 38 PASS. Median 2.1 s, max 13.7 s, total wall 73 s on 2 workers.
No witness-feedback round was needed on any node (all PASS at round 0).

## V2 — independent re-audit at greater depth
Three of the 38 (nodes 50, 93, 132), re-verified with A38's OWN unmodified
`attempts/A38-root-power/code/verify_case.py` at `--depth 64 --jobs 3`:
  node 50  PASS  total 4635001/500000 = 9.270002 < 10   (179712 boxes, 3.9 s)
  node 93  PASS  total 927047/100000  = 9.270470 < 10   (131984 boxes, 3.0 s)
  node 132 PASS  total 927/100        = 9.270000 < 10   ( 22026 boxes, 0.7 s)
Nodes 50 and 93 are exactly the two that A38 reported as FAILING certification. See V3.

## V3 — why A38 lost nodes 50 and 93 (correction to A38 section 5)
A38's `certify.py` path re-solves the node LP at `--eps_geo 0.003` BEFORE certifying. For node 50
that re-solve moved tau from 9.000000 (cached, eps_geo 1e-4) to 9.940083 with minmass 0.379 and
converged=false; the certificate built from THAT re-solve had total 9.989863, i.e. 0.010 of
headroom under the budget, and failed. The cached LP's own certificate has total 9.270002 and
passes. The 2/8 failures are therefore an artefact of the eps_geo re-solve, not evidence that
A27's float classification produced unsound kills at s0. A38's conclusion
"the kills evaporate ... exact-certification-in-the-loop is the only kill accounting" is corrected
to: the kills are real and cheaply certifiable; what A38's certification pipeline could not afford
was its own preparatory re-solve.

## V4 — level-1 all-node probe
`code/l1_probe_all.py`, results/p2a/l1all/l1all_probe.json. One certification attempt on the
cached LP of all 90 processed level-1 nodes that A27 did NOT call dead. 3 PASS (nodes 14, 31, 32
— all A38-"undecided", all with tau = 9.000000); 34 were skipped without a verifier run because
tau >= budget - headroom leaves no room for any scale > 1. Total wall 444 s, median 2.2 s/node.

## V5 — depth-2 and level-1-undecided loop runs
`code/p2a_run.py` stages A/B/C, results/p2a/l2/ledger.json and results/p2a/l1u/ledger.json.
Every kill claimed is a `verify_case.py` PASS; every non-kill is reported as undecided. Node LPs
run at eps_geo = 1e-4 with the W1/W2 row filter OFF (notes/method.md, deviation 1-2).

## V6 — P2b field certificates
Every field produced by `code/reseal_shat.py` is turned into an exact rational certificate by
A33's `t1/make_cert33.py` (unmodified) and decided by `certs/verify_measure.py` (unmodified) at
depth 50, split 3. The final artifact is sealed with A33's `t1/seal_cert.py` and re-verified
STANDALONE with no flags.

## Known trust boundaries
- `verify_case.py` / `verify_measure.py` themselves (repo-standard, unchanged in A39).
- The only A39 edits to the LP driver are `lpbox.run(..., round_hook=)` and its passthrough in
  `caselp.solve_node`; neither touches the LP, the oracles, or `make_certificate`.
- A29 untouched.
