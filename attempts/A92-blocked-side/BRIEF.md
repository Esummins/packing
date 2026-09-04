# A92 — K0-BLOCKED implies side >= s-hat (Fable lead, theory; the PI's target)

Target (PI, 2026-09-03): prove that a K0-BLOCKED packing (every corner's open unit slot met by >= 2
squares; no simple square) has side >= s-hat = 3.877083590022814. If the proof's structure produces a
clear boundary above s-hat, cite that number. This is all the k0_00 class technically needs (with
K0-FREE, K0.FREE on the depgraph, handling the rest).

## The one trap to design around first
K0-BLOCKED is an OPEN condition (strict intrusion). Exact-verified K0-BLOCKED packings exist at side
3.985484 (A87 k0dir87 record s0115, n_block [2,2,2,2]) with second intruders at TL/TR of depth 8e-9 and
1.7e-8 — nicks at the tolerance floor. Any k >= 1 packing with room at its corners can be nicked into
K0-BLOCKED at the same side, so the UNIVERSAL statement over packings is no easier than s(11) >= s-hat
itself. The proof must therefore split:
 (S) SUBSTANTIVE crowding — every corner's second intruder has depth >= delta: prove side >= f(delta)
     with f(delta) > s-hat, and a clear boundary; empirical frontier of D2 = min_c d2 (A87 d2front87,
     raw, certified): 0.293 at side 4.357, 0.154 at 4.194, 0.078 at 4.100, 0.034 at 4.038 — so f(delta)
     looks to be > 4 for any delta above ~0.02 (EXTRAPOLATED); per-corner ceiling min(d1,d2) <= 1-1/sqrt2
     (argued in deepfront87, prove it); two axis-aligned squares cannot both intrude one slot (A89, [T]).
 (N) NICKED corners — some corner's second intruder has depth < delta: handle by SELECTION (the
     Psi-minimal minimiser of A90 NOCRIT-SEL, with the anchored-only frontier collapsing to the search
     floor: d2front87 (b)), by Lemma PD's pin slack when the substantive intruder is within delta_pin =
     0.02 of the slot in position and tilt (the k1 tree covers it), and by the JAM-0 coupling
     (an axis-aligned offset-g intruder pins its partner within arcsin(g) of flush and depth <=
     g^2/sqrt(1-g^2)); say exactly which nicked configurations remain, if any.
Deliver both halves, each at drain-v3 rigor, with the exact residue named if either does not close.

## Facts and tools to build on (read first)
docs/proofs/nocrit_k0_blocked.md (Lemma K retreat trichotomy, CLUSTER, COL: wall-anchoring columns >= 3
squares above 1+2sqrt2, BLIND, W-GEN), docs/proofs/tilt_floor_k0.md (TF-U, LOCK, MENU, JAM-0, ID + the
certified 4-shallow kill: some corner has an intruder at depth >= 0.3), docs/proofs/k0_route.md
(K0-FREE, A58 crowding, K0-D4), docs/proofs/structure_lemmas.md (L1, L6, per-wall <= 3), A50 (tilt 0 or
>= 1.73 deg on spanning chains; rulers <= 5), A25/A47 (wastage atlas and corner charge table, max 0.85
per corner, exact-zero at near-flush), A26 (same-grain terminations waste 0), attempts/A87-drain-flow/
notes/{k0blocked87,k0dir87,depthdist87,deepfront87,d2front87}.md (all the measurements; the packing
barrier at 4.000002 from A85-seeded search vs the 3.985 free-space record — reconcile), attempts/A85-
k0-route/notes/realise85.md (realisable pair census 7,044; boxes 560; reach <= 2.457 so far walls never
bind), docs/known_results.md 16a (active-graph planarity caveat, ruler cap side-dependent).

## Routes for (S), in the order to try
1. WALL-STRIP / CELL COUNTING: each of the four wall strips [0,s]x[0,1] (and rotations) is met by both
   intruders of its two corners (4 squares, disjoint across corners since reach 2.457 < s-1); with
   per-wall <= 3 and substantive depth delta at both intruders, bound the wall length from below (the
   nick is what defeats the naive projection bound — quantify how much room a delta-deep second intruder
   needs along the wall and above it; the goal is s >= 2 + 2 g(delta) or a cell-count that forces the
   4x4 grid). Also the diagonal: opposite corners' crowds vs the 3 free squares.
2. WASTAGE with substantive crowds: the corner charge table (A47) is exactly zero at near-flush but not at
   depth >= delta for BOTH intruders (the pair primitive was never computed at substantive depth: compute
   it — min stranded area over pairs with d1, d2 >= delta, exact, A23/A25 dead-region machinery), then
   4 corners x pair charge + interior vs E(s) = s^2 - 11 <= 4.0318; if the pair charge at delta ~ 0.05
   exceeds ~1.0, area alone closes (S).
3. MEASURE CERTIFICATE with the substantive hypothesis: the 4-shallow certificate (A89-O3) was a root
   measure certificate with exempt boxes; its dual here is a root certificate whose hypothesis is
   "each corner has two squares in depth-capable boxes with d2 >= delta" — the cores of depth-capable
   boxes are NOT empty (a square at depth >= delta occupies a definite region near the corner:
   compute the core of the depth-delta box exactly), so this is a K-leaf with 8 non-empty cores and
   budget 3: run it (A85/A89-O3 engine, one LP slot) for delta in {0.05, 0.1, 0.2, 0.3} at s0 and at
   3.82; if it PASSES at some delta, that delta is (S)'s boundary and the theorem is a certificate +
   the (N) lemma. This is the cheapest complete route if it fires.
4. NOCRIT-SEL anchoring + reach counting (A91 9): only if 1-3 fail; state the residue exactly.

## Canaries
Trump is not K0-BLOCKED (3 slot squares, TL 2-crowd at depths 0.168/0.155) — no lemma may exclude it.
The certified K0-BLOCKED packings at 4.03-4.36 with substantive D2 (d2front87 raw table) must NOT be
excluded by any (S) lemma claiming a boundary above their side. s0115 (3.985, nicked TL/TR) must fall in
(N), not be contradicted by (S).

Constraints: <= 2 processes, BLAS-pinned, headroom > 6 GB; A57/A60/A61/A86 untouched; frozen verifiers
untouched; writes in attempts/A92-blocked-side/, docs/proofs/k0_blocked_side.md, depgraph K0.RES4 /
K0.TREE notes (chip -> A92 on K0.RES4; pull/merge), registry row, LOG.md. Report tersely: (S) status
with its boundary number first, then (N) status with its residue, then pointers.
