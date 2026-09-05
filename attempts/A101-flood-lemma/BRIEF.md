# A101 — the Flood Lemma, second attempt: degeneration below side 4 and the eta-disturbance drain (Fable lead, theory)

Context (2026-09-05). A98 built the exact framework for the Young flood (docs/proofs/exchange_lemma.md: Lemma TWO, FLOOD-D,
X(D) = overhang - free area, CAP: below side 4 every square meets the 3x3 block so X(3x3) = 2 and a win needs <= 8
cells, EXPOSE, CROSS, RELEASE-CL) and left ONE gap: the stall it called INTERLOCK. Since then: (a) the "interlocks" in
every real example were tolerance artefacts — a 1e-8 TANGENCY counted as a blocker; under the strict convention
(certified depth > 1e-6 into the OPEN cell) the 3.985 record is K0-FREE and NO strictly K0-BLOCKED packing below side
4.000004 is known (attempts/A85-k0-route/results/strict85.json; A87 notes/degen87.md); (b) with a WIDER, SIMULTANEOUS
move set — ALIGN (near-axis square snaps to its cell), cell-level TELEPORT (a cell met by exactly one square: move it
in), WALL-SLIDE (an axis-aligned wall square slides along the wall into a freed cell), the corner exchange with the
inscribed-square objective — 6 of 8 K0-BLOCKED packings reach a DEAD class at the same side and all 8 degenerate
(k 0 -> 6..11); the greedy must be simultaneous (one-at-a-time stalls at move zero); Trump makes zero moves (the
canary). A floor sweep of the directed search (k0dir2_87, running) reports the lowest strictly K0-BLOCKED side per
depth floor. PI theme: the lab keeps meeting eta-DISTURBED simple squares (a square within eta of a lattice cell in
position/tilt: near-flush ghosts, nicks, tangencies), panicking, and then finding they drain; make that a theorem and a
tool, not a rediscovery.

Read first: docs/proofs/exchange_lemma.md, docs/proofs/k0_blocked_side.md (SLIDE, Theorem N), docs/proofs/nocrit_k0_blocked.md
(anchoring, CLUSTER, W-GEN, COL), docs/proofs/tilt_floor_k0.md (JAM-0, MENU, TF-U), docs/proofs/k0_route.md (K0-FREE/CC-2,
its Lean form Slide.lean/Composition.lean), docs/proofs/slot_crowds.md (SLOT-CROWD: every completable cell of a pinned
class is doubly met — the pinned generalisation), attempts/A87-drain-flow/notes/{degen87,flood87,exchange87}.md +
results/degen87.jsonl (exact final configurations and move sequences), attempts/A85-k0-route/results/strict85.json,
attempts/A96-a57-parametric/notes/pocket96.md (A57's certification holes are near-flush against PIN squares — eta-disturbed
stacked cells, not empty slots), docs/residue_map.md (the map; s.8 candidate theorems), docs/known_results.md 16a.

## T1 — Lemma SNAP (the eta-disturbance drain; state and prove first, it is the base case of everything)
For a packing at side m and a completable cell C of its Young diagram (any class, k0 included): if a square Q has
tilt < theta_0 and centre within eta of C's centre, and no OTHER square meets the region Q must sweep to reach C
(the swept region = C union the rotation sweep about Q's centre union the translation strip; give it exactly), then the
packing with Q aligned into C is a valid packing at the same side in the extension class S union {C}. Prove: (i) the
swept region is contained in an explicit box around C of size 1 + O(eta + sin theta_0) — the eta-disturbance ball;
(ii) SIMULTANEOUS snaps: a set of eta-disturbed squares on distinct cells snap together iff their target cells are
pairwise interior-disjoint (they are: distinct lattice cells) and no untouched square meets any swept region — this
is why one-at-a-time greedy fails (degen87) and simultaneous succeeds; (iii) the blocked case: if another square R meets
Q's swept region then R meets the open cell C (or its eta-inflation) — i.e. C is CROWDED in the strict sense; so
"snap or crowded" is a dichotomy, and the residue after SNAP is exactly the strictly crowded cells. Consumer: at any
tree node whose box for some square lies inside the eta-disturbance ball of a completable cell and whose other boxes
provably avoid the swept region, the node is a free logic kill into a dead extension class ((T) leaf, box-checkable).
Estimate on A57's witness holes (pocket96 data: holes near-flush against pin squares) whether this leaf fires where the
pocket exemption did not — the holes are eta-disturbances of STACKED cells (Young extensions), which pocket96 did not
test.

## T2 — Theorem FLOOD (the lemma A98 left open, restated for the strict convention and the simultaneous move set)
Every packing at side m < 4 that is strictly K0-BLOCKED (every corner cell met by >= 2 squares at certified depth
> 0; take the floor from k0dir2_87 when it lands) converts, by finitely many simultaneous moves (SNAP, cell TELEPORT,
WALL-SLIDE, corner exchange) at the same side, into a packing with a simple square — hence into a k >= 1 class at the
same side. Route: the potential X(D) and CAP (X(3x3) = 2 below side 4); RELEASE-CL; the PI's mechanism (removing the
deepest intruder of the least-intruded cell releases every square anchored through it); the pinned generalisation via
SLOT-CROWD so the same theorem holds for every class (degeneration climbs the whole ladder). Characterise the stall
EXACTLY if the theorem does not close: an explicit strictly K0-BLOCKED packing below side 4 on which every move fails
(verify with degen87's certifier), or the exact combinatorial description of such frames. Use the k0dir2_87 floor
sweep (results/k0dir2_87.*) as the empirical boundary: if strictly blocked packings exist below 4 at some floor, the
theorem's side threshold moves to the measured value — say what it is and whether it is above s-hat.

## T3 — composition
If FLOOD holds at some side threshold m* >= s-hat: k0_00 = FLOOD + (k >= 1 kills on the window), no criticality, no
selection, no tree (the plain StratumKill form; hypotheses = K0-O1-ALL). If it holds per class (SLOT-CROWD form),
state what it removes from the protected tier (A100: tier 3,500-4,200 CPU-h, cost concentrated in the top slab where
tau pins to the budget) and from A57. Lean-readiness: SNAP is a finite geometric lemma (sweep boxes + SAT) — state it
in the Skeleton/ThetaT conventions so A93's Crowd/Slide machinery can absorb it.

Constraints: theory (chores <= 1 process, BLAS-pinned, headroom > 6 GB and free physical > 3 GB; the box is loaded —
coordinate with A96 by a note if you need a slot); A57/A60/A61/A96/A99 untouched; frozen verifiers untouched; writes in
attempts/A101-flood-lemma/, docs/proofs/flood_lemma.md, depgraph K0.RESN note (chip -> A101; fetch + plain merge + push
own paths only; NO rebase/autostash/reset), registry row, LOG.md. Report tersely: SNAP status and its leaf yield first,
FLOOD status with the side threshold second, composition third, pointers.
