# A38 — far-field root-power pilot at s-hat (Fable lead)

You are the THEORY lead (Fable). Math/design in your own context; Opus subagents for compute, terse
file-pointer briefs, verify their outputs. THIS IS THE GO/NO-GO MEASUREMENT for the s(11) = s-hat
endgame: can the conditioned case tree at s0 = 969271/250000 (just above s-hat) shrink the far
field to the certified atlas boxes at desktop node counts?

Read first: LOG.md 2026-08-27 entries (campaign map), docs/proofs/drain_lemma.md v3,
attempts/A37-cp-atlas/results/atlas_final.json (+final_report.md — the discharge boxes and the
"trivial Lipschitz beats barrier above 3.887" lesson), attempts/A33-tight-variety/ (certified
field at s-hat: t1/certs/A33_measure_feasible_3.877084.json, eta_cert = 0.4254; T2's tight-variety
maps + PAIR-SUM result), attempts/A27-close-384/ (the case-LP pipeline that closed cells at 3.84),
REGISTRY rows A21 (occupancy theorems AT 3.88 — proof that conditioned kills exist above s-hat),
A24 (interior-first, kill thresholds vs core width), A30 (t3lib Farkas engine), A35/A36.

## T0 — the composed soundness statement (yours, first)
Draft the one-page composition: D1 attainment + per-cell disjunction {case-LP kill (no 11-packing
under hypothesis), tight-sum domain/pair kills, Farkas/FJ exclusion (no critical point with value
<= s0), atlas discharge (cell inside a certified box), D2 slack} + the BDBFS discovery loop for
survivors near unknown attractors => s(11) >= s-hat, with the A36 uniqueness clause closing
equality. Name every unproved seam (ridge/cliff handoff G1 included) — the pilot MEASURES; the
statement tells us what a full campaign must still prove.

## The new weapons, composed into the tree (design care, yours)
 W1 tight-sum DOMAIN cut: placements whose certified-field coverage lower bound > 1 + eta cannot
 belong to ANY 11-packing at s0 — prune them from every node's placement domain (T2 measured
 18-48% of placement volume; use the certified field + exact coverage machinery).
 W2 tight-sum PAIR cut: disjoint placements x,y with joint coverage > 2 + eta are incompatible —
 conflict rows / rank cuts in the node LP (T2: kills 51% of surviving pairs).
 W3 atlas discharge: a node whose hypothesis pins the configuration inside an atlas box (mod D4 x
 S11) is discharged by that box's certificate. Includes Trump's box = the target leaf.
 W4 Farkas/FJ exclusion for near-jammed nodes (t3lib) — reserve for nodes the LP cannot kill.
 W5 the classic arsenal: A27 case-LP with column oracle, wastage atlas lookups, band/occupancy.

## The measurement
Root + depths 1-3 of an interior-first tree at s0 (A24's zone scheme adapted; D4 x S11 reduced):
per depth and per weapon, the kill fraction, cost/node, branching factor of survivors, and the
character of survivors (Trump-consistent vs other; distance to nearest atlas box). Then the honest
extrapolation: projected total nodes to close the far field (bracket, not point estimate),
identifying the binding constant. Explicitly test: does the tree stall at some depth with tau
pinned >= 11 and no weapon firing? (That was A14's wall-first failure mode — measure whether
interior-first + W1-W4 escapes it at s0.) Also measure the SEAM: for a sample of near-Trump
surviving cells at depth 3, can W4 + the A36 box close the gap between tree-leaf scale and box
scale (the G1 handoff), or does a scale gap remain?

## Deliverables
results/rootpower_report + json tables (kill matrix depth x weapon, costs, survivor census,
extrapolation bracket, seam verdict); the T0 composition note in notes/; GO/NO-GO with the assassin
constant named if NO; if GO, projected desktop-days for the full far-field campaign. Honest
negatives are successes. Gap list. Registry row.

## Constraints
<= 6 heavy processes, RAM guard (HiGHS OOMs at 3 big LPs — A33's lesson: cap 2 big LPs + workers),
checkpoints, resumable, terse traffic. Budget ~4-6 h wall. A29 state untouched.
