# A42 — named structural facts (measured 2026-08-28; sources: results/chain.json,
# results/sweep.json, results/tighten_probe.json; verified against artifacts by the lead)

F1 — THE LAST-SQUARE IDENTITY (budget-1 vacuity; theorem, one line). In any Theorem-1/K1 node
with budget 1, tau >= 1 whenever a single admissible non-exempt placement Q0 exists: the
covering constraint at Q0 alone gives total >= mu(Q0) >= 1. Hence a budget-1 node kills iff
the live placement set is EXACTLY EMPTY, and the LP contributes nothing beyond the verifier's
emptiness check. General form: tau >= nu(live set) (max integral packing of admissible
squares); coverage kills need fractional infeasibility of the whole remaining budget, never
"the last square is hard to place". Retro-explanation: deep leaves at 3.84 needed full pinning
because near-leaf budgets are small and the coverage family goes vacuous exactly there; also
the A38/A27 tau = budget knife-edge cells.

F2 — UNIT EXCHANGE AT BALL SCALE. At s0, conditioning one r = 0.06 ball-occupancy core lowers
the converged tau by EXACTLY 1.000 — the unit of budget the core consumes. Measured k = 1..10:
tau = 11-k exactly (k <= 5), 12-k (k >= 6, after the clipped-corner ball 0 bought 0), integer
to 3e-11, all CONVERGED (true LP optima, not timeouts). Net certificate headroom per chain
step = 0, identically. No decay constant exists; the chain is dead at k = 1 by an exact
integer, not by cost.

F3 — REFLOW: BALL-SIZED EMPTINESS IS WORTH ZERO. Removing the target nofam (control cond_k)
changes tau by < 1.2e-12 at every measured k: the coverage measure relocates around any
0.06-ball exemption at no price. Same at every target radius rho' < 0.06 (tighten probe:
tau identical at rho' = 0.045, 0.03, ...). Headroom scales with EXEMPTED VOLUME: A38 root
zone (side 1.68) bought 3.0 of tau; a 0.06 ball buys 0.016 (~190x, ~area ratio). A38 probe A's
"tau 9.20, slack -0.80" was an unconverged-relaxation artifact: the converged union optimum is
10.000 (A42, 619 s).

F4 — THE TRUMP-CONSISTENCY SHIELD. Any sound weapon that does not READ the target-emptiness
nofam cannot kill an occupancy-chain node: the hypothesis minus the nofam is realized by the
Trump packing itself. So W1/W2, the wastage atlas, and hypothesis-side FJ arguments are
structurally excluded from forcing occupancy; only nofam-aware arguments (the coverage LP —
measured worth zero at ball scale — or a future nofam-aware exclusion) can.

F5 — ASSIGNMENT IS FREE AT EMPTINESS (the T3 keeper). Given the post-N1 encoding (10 cores +
window-complement nofams + exact complement cover), the 11th square is forced into its ball by
the EXACT VERIFIER ALONE: measure total 1e-6, no LP, 0.9-8.6 s per ball, 11/11 PASS in 38.1 s
(forces centre within rect_j + 0.002, theta within window + 0.05 deg). Emptiness kills are the
one certificate family in this regime with real margin — but they need the complement
emptiness as INPUT, i.e. an occupancy result obtained elsewhere.

F6 — BUDGET->=2 TIGHTENING IS ALSO DEAD AT BALL SCALE (closes the interleaving question).
Mid-chain target shrink (k = 2, rho' = 0.045 down) leaves tau = 9.000000000 exactly — F2+F3
compose: there is no k and no rho' at which the 0.06-family certifies anything. The
S11-collapse machinery (N1, F5) is sound and free; the coverage family simply cannot supply
its occupancy premises at ball scale at s0.

OPEN LEVER at the time of writing: zone SIZE. N1 needs only diameter < 1; half-width 0.35
zones (side 0.70, diag 0.98995 < 1) are pairwise disjoint at the Trump placements (min gap
0.0360, pair 3-6) with ~34x a ball's volume — the zoneprobe42 run measures whether occupancy
certifies there and where headroom dies as w shrinks.
