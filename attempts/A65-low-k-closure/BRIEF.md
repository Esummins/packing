# A65 — the two biggest open leaves: H10 (k<=4/k<=3 tier) + Theorem U (Fable lead)

You are the THEORY lead (Fable). These are the two largest open mathematical leaves on
lean/depgraph.json (C.K4TIER and A.THMU); the composed theorem cannot close without both. Do the
mathematics yourself; Opus subagents for compute only. The machine runs three campaigns — you may
use AT MOST 2 light LP slots (budget-1 / small case-LPs; BLAS-pinned via an existing launch.ps1
pattern; check commit headroom > 6 GB before launching). Do not touch A57/A60/A61 state.

Read: lean/depgraph.json nodes C.K4TIER + A.THMU, docs/proofs/unique_transfer.md (the H10-stuck
re-base + Theorem U spec), attempts/A58-clear-corner/notes/theory.md (CC-2, 2-crowd, the
successor routes priced: pair primitive, CC-4 -> FJ rows), attempts/A55-k4-sweep/ (K1 sharpness,
which classes are protected and why), attempts/A22-local-rigidity/ + A36 (basin machinery),
docs/proofs/closed_disjoint_bridge.md, attempts/A63-hole-closure/notes/findings.md.

## T1 — Theorem U: execute the spec (the cheaper leaf; do it first)
unique_transfer.md specifies Theorem U (one-square rigidity of z-hat) as 11 re-insertion
certificates: for each square i, remove it, shrink the other 10 cores, case-LP at a rational
side in the Sturm isolating interval with budget 1 and a nofams zone inside the basin box; a
PASS proves square i's slot is forced. Emit and exactly verify all 11 (obligation U-O1). These
are small LPs — well within your 2 slots. Then write the composition: U-O4 (existing D/E nodes)
and how U discharges the uniqueness collapse. U-O2 = H10-stuck is T2; U-O3 (k5_11/16 window
form) is owned by A57's G1 campaign — cite, don't redo.

## T2 — H10: the k<=4/k<=3 tier, re-based on stuckness
The largest open leaf. A63's re-diagnosis: the needed form is H10-STUCK — a SELECTED (teleport-
stuck) minimiser cannot have skeleton in the K1-protected classes ({k4_03,k4_05,k4_06,k4_08,
k4_11,corners4} + ten k<=3). This is strictly weaker than killing the classes outright (which K1
proves impossible), and A58's machinery (every clear corner of a k<=3 minimiser carries >= 2
non-simple squares; Trump teleport-extremal) was built for exactly this hypothesis. Routes to
price and then EXECUTE the best: (a) crowd-pricing: the 2-crowd forces occupancy the budget
cannot pay under stuckness — attempt the counting argument A58 left as "a crowd-pricing
problem"; (b) stuck-kill certificates: add stuckness-derived rows (teleport-blocked = specific
contact/occupancy constraints) to the case-LP and re-run the protected classes with your 2
slots; (c) upward absorption: a stuck minimiser in a protected class forces a completion in a
killed class (K1-style climb with stuckness). A dead route decisively priced is a result;
partial progress with the residue named exactly is a result. Trump's own configuration must
SURVIVE every argument (canary — state where it lives at each step).

## Deliverables
certs for the 11 Theorem U re-insertions + verification log; docs/proofs/theorem_u.md (or an
update to unique_transfer.md) with U-O1/U-O4 discharged; H10: docs/proofs/h10_stuck.md with the
executed route (or the decisive pricing of all three); depgraph labels/notes updated + re-
rendered (coordinate with A64 who is also editing it — pull before push); registry row; LOG.md;
terse traffic.
