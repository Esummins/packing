# A33 — equality pigeonhole / tight-variety collapse (Fable lead)

You are the THEORY lead (Fable). Do the mathematics yourself; dispatch Opus/Sonnet subagents for
coding/compute only, with terse file-pointer briefs. Idea board entry: docs/ideas.md I-L13.
Context: docs/proofs/drain_lemma.md v3 + structure_lemmas.md + REGISTRY rows A30-A32 (why local
certificates lost: any complete search over local kills pays the 33-dim product; we need GLOBAL,
family-killing certificates). Machinery to reuse: A19/A20 LP row generation (exact rational duals),
certs/verify_measure.py-style interval coverage maps, A08 exact B&B verifier.

## The core statement (formalize first — short)
If a measure mu on [0,s0]^2 has total mass M = 11 + eta and mu(Q) >= 1 for every closed unit square
Q in the box, then for ANY 11-packing at side s0: each square covers mu-mass in [1, 1+eta] and
mu(box \ union) <= eta. Multi-field version: holds simultaneously for every such field => squares
pinned to the INTERSECTION of near-tight varieties. Write it with the same care as Theorem 1
(docs/results.md); note it needs no LP optimality, only feasibility of each field.

## T1 — measure eta(s)
Compute eta(s) = (minimal feasible guard total) - 11 at s in {3.84, 3.85, 3.86, 3.87, 3.877084}
via row generation (subagent; warm-start across s; a-posteriori feasibility verification per the
lab standard — A19's stall taught us to verify every solve from (g,F)). Exact-rationalize at least
s = 3.877084 (outward-rounded feasible field, certified total). This single table gates the idea.

## T2 — map the tight variety
At s = 3.877084 (or 3.85 if eta there is much smaller), take the near-optimal field(s) and map
T_eta = {placements (x,y,t): coverage upper bound <= 1 + eta} with the interval coverage machinery:
thickness, number of components, dimension estimate; where Trump's own 11 placements sit in it
(they MUST be inside — canary). Then intersect over >= 3 diverse near-optimal fields (perturbed
objectives in row generation) and measure the shrinkage. Deliverable: maps + measured volumes.

## T3 — the PI's grain conjecture (high-n leverage)
PI observation: large-n optimal packings are crystal-like — grains of aligned squares, wastage
confined to grain boundaries; interface wastage per unit length should tend to a constant, so eta
should FALL with n and n = 11 is near this method's WORST case. Investigate: (a) literature (web):
Erdos-Graham 1975 wastage O(s^{7/11}) for unit squares in a large square, Chung-Graham
improvements, Roth-Vaughan lower bound — get the exact current asymptotics and cite into
docs/literature.md conventions; (b) measure eta(n) at the conjectured-optimal side for a spread of
n (e.g. n in {5, 10, 11, 18, 26, 41, 66, ~100}, using known best packings from the records
literature/A11 sweep for the target sides) — does eta(n) fall as PI predicts? (c) THEORY: can the
equality pigeonhole + grain analysis force structure for large n (e.g. prove near-lattice structure
of any optimal packing for n large)? Even a partial result here is a new theorem in the field.
Honest verdicts welcome; quantify.

## Constraints
Machine shared with A34: <= 3 heavy processes for your compute. Checkpoint everything; registry row;
terse traffic. The PI reads results — keep the final report structured and plain-language-friendly.
