# A52 — breaking the ghost's exact ties: the two-field probe (Fable lead, light)

Goal: the first direct test of the N6/two-field idea against the objects that actually guard the
far field — the knife-edge cells where tau = budget EXACTLY.

Targets: (i) A38's five alive(LP) level-1 cells (idx 61, 65, 74, 95, 100 — tau = 10.000000,
maxcov = 1.000000 exactly; checkpoints in attempts/A38-root-power/results/l1_nodes/), (ii) a
sample of A42's integer-exact conditional saturations (chain nodes k = 1, 2 from
attempts/A42-occupancy-chain/results/chain_nodes/).

Design (theory first, short): the node LP's tau is pinned at budget by the ghost's equality face
for the PRIMARY field/covering structure. Build SECOND certified guard fields with deliberately
different tight structure — A33 t2's perturbed-objective machinery (perturb_loop.py produced p1/p2
with supp Jaccard 0.41-0.50 vs the optimal family) is the generator; also try region-weighted
objectives (extra mass cost in the cell's own zone). Then impose BOTH budgets simultaneously in
the node LP (the second field enters as additional capacity rows: every placement's weight counts
against field-2 coverage too — write the sound formulation carefully: two capacity families, one
packing variable set). Measure: does tau drop strictly below budget on any knife-edge cell? By how
much, and does the exact verifier then certify (A39's cheap-cert rule)? Ablation: 1-field baseline
(must reproduce tau = budget exactly), field-2 alone, both. Honest mechanics if it fails: verify
whether the ghost face satisfies BOTH equality structures (compute the joint tight set — A33 t2
diversity machinery) and report the obstruction quantitatively.

This is a MEASUREMENT (hours), not a campaign. Success = any strict tie-break with a certified
kill on a knife-edge cell (would be the first crack in the equality manifold); failure = the
measured joint-tightness obstruction, quantified. Opus for LP/verifier compute; <= 3 heavy
processes; ONE long-poll waiter; checkpoints; A29 untouched. Registry, LOG, PI-readable report.
