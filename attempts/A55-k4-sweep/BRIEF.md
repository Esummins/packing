# A55 — the k=4 sweep (Opus)

Goal: extend the stratification cap downward — kill (or classify) all 14 k=4 Young classes.
Context: attempts/A53-simple-strata/ (census in code/skeletons2.py, residual-LP machinery,
eta_table conventions; ONE k=4 class was measured alive in A53's spot data — identify it),
attempts/A54-stragglers/ (THE BANKED LEVERS — merged warm start with pruning off, lifted scale
cap = budget/tau, prune COLUMNS only, cheap-cert every round; notes/lemmas.md S0-S5).
Protocol: per class, rung 1+2 of A54's ladder (converged LP + witness-feedback certification at
the true scale ceiling); budget 7 per node (11-4). Expect the corner-dominated classes
(corners4 = the A14 baseline, already known alive-at-LP) to survive — characterize survivors with
the Trump-ghost profile test (A54's interior/side-zone mass fingerprint) and the tight-variety
coverage number; kill the rest with exact certificates. Update the L5 cap statement: with k=4
results, state exactly which strata (by subset containment) are now empty. Canary: trump5 (never
kill), corners4 must reproduce A14/A16's tau -> 7.000 baseline. <= 3 heavy processes; consolidated
completion-only waiters; checkpoints; A29 untouched. Registry, LOG, scoreboard report.
