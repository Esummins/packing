# A98 — the Exchange Lemma: K0-BLOCKED drains to k >= 1 at the SAME side (Fable lead, theory; PI mechanism)

PI mechanism (2026-09-04) and the measurement that motivates it (attempts/A87-drain-flow/notes/exchange87.md):
for a K0-BLOCKED packing at side m, pick a corner c, remove its two intruders A and B, place an exact slot
square at c, and re-fit one unit square anywhere in the free space (any tilt). Measured on all 8 exact
K0-BLOCKED packings we have (sides 3.985-4.107): EVERY packing converts at >= 1 corner (21 of 33 corners),
all successes exactly verified; the slot is never blocked by a third meeter (33/33 have exactly two);
relaxing the other nine squares is NOT the mechanism (the pre-relaxation configuration already has room);
margins are 5-11% at sides 4.08-4.11 but ~1e-8 at side 4.0000 (those packings sit at the 4x4 grid infimum),
and 7 of the 12 failures fit to within 1e-3. Trump (k3, rigid) fails as it must: largest inscribable square
0.9823, and after removing its TL crowd no remaining square has any feasible rigid motion. If the exchange
always succeeds at sides <= s-hat, k0_00 drains to k1 at equal side with no criticality (no H1), no
selection, no tree: k0_00 = EXCHANGE + the k >= 1 kills. That is the PI's original conjecture in its
strongest form, and the sharpness at side 4.0000 says the lemma, if true, is tight — so the proof must use
the k0 structure (all four corners doubly intruded, anchoring) rather than slack.

Read first: docs/proofs/k0_blocked_side.md (SLIDE — the rigid exchange, which costs exactly d2 of side; the
Exchange Lemma is its non-rigid version costing 0), docs/proofs/nocrit_k0_blocked.md (anchoring; Lemma
CLUSTER; W-GEN), docs/proofs/tilt_floor_k0.md (JAM-0, MENU, CEIL, LOCK), docs/proofs/wall_budget.md
(WALL-F chords, FLOAT: a jam's floating pusher strands 0.707(1-L) beside the slot square — that stranded
strip is exactly where the exchange can put the re-fitted square), attempts/A85-k0-route/results/
{cases85.json, charge85.json} (corner-pair taxonomy JAM / BLOCK / WEDGE / OFFSET-UPRIGHT and the exact
stranded-area charges: the stranded region is FREE area adjacent to the slot after the exchange),
attempts/A87-drain-flow/{notes/exchange87.md, results/exchange87.*} (per-case tables and verified
placements), docs/known_results.md 16a.

## T1 — Theorem EXCHANGE (state exactly; prove or find the failure mode)
Statement to aim for: in a K0-BLOCKED packing at side m (m in [3.82, s-hat) — or any m, if the argument is
side-free), there is a corner c such that, with its two intruders removed and the exact slot square placed
at c, a unit square fits in the complement (interior-disjoint from the other nine and the slot square,
inside the container). Consequences: the result has a simple square, so it lies in a k >= 1 class at side
m; with the k >= 1 classes dead on the window, k0_00 is dead on the window. Proof directions, by corner
case (cases85 taxonomy): (a) JAM (slot-ish square A at offset g + nick partner B): remove both, slot
square = A shifted into the corner; re-fit B shifted by its nick depth (needs room of order g^2 above B)
OR into the strip A vacated ([1, 1+g] wide — too narrow) OR into FLOAT's stranded strip beside A (0.707
tall — too short for an upright, but a tilted square?): quantify exactly when B fits and when the jam's
lockers block it; (b) WEDGE / BLOCK (both tilted): after the slot square is placed, the vacated region
(A union B union the stranded region S) minus the slot has area >= 1 + charge(S); show it contains a unit
square — the arm argument: B minus its part inside the slot is a unit square minus a small convex piece
near its inner vertex, so B shifted outward along its own inner-vertex direction by its intrusion depth
d_B fits inside B union (a strip of width d_B on B's outer side) — the strip is occupied only if a
neighbour presses B's outer side, which is exactly the anchoring contact (NOCRIT-SEL at the selected
minimiser; but the lemma should be forall-packings if possible): resolve which; (c) OFFSET-UPRIGHT
(A axis-aligned at offset g > 0.1 flush on a wall, B tilted): the slot square is A slid into the corner
(needs the region between A and the corner free of B: B intrudes it — so A and B swap roles: which of the
two is easier to re-fit). Treat the third-meeter case (a corner whose slot is met by >= 3 squares) — prove
some corner has exactly two, or handle it. Use the counting: the packing has free area m^2 - 11 >= 3.59
plus the two removed squares; the exchange needs one unit square in a region of area >= 1 + charge; the
obstruction is shape, so the proof must be geometric per case. If the lemma fails, exhibit the failure
configuration explicitly (exact, verified with exchange87.py's certifier) — a tight K0-BLOCKED packing
where no corner admits the exchange — and characterise it: that is the true k0 residue.

## T2 — the exchange as a tree leaf (consumer, even if T1 is partial)
"Exchange feasible at corner c" is a LOCAL condition on c's pair box and the boxes of the squares that
border the vacated region. State it as an exact box-level test (C-type leaf): given the pair boxes and
the neighbours' boxes, a certified placement of the re-fitted square that is disjoint from every
placement in the neighbours' boxes (cores/shadows) and from the slot square. Estimate on the realisable
pair census (7,044 pairs; charge85's 200 sampled pairs have the stranded regions) what fraction of pairs
admit a box-uniform exchange placement ignoring neighbours (upper bound on the leaf's yield), and give
the design for A85's tree / A96's emission to consume it.

## T3 — composition
If T1 holds (any form): k0_00 = EXCHANGE + k >= 1 kills; state which TopLevel axiom it discharges, the
hypotheses it adds (none beyond the k >= 1 window kills, if forall-packings), and the Lean obligations
(exact placement certificate per corner case — replay-shaped). If T1 holds only at the selected minimiser
or only above a side, state the residue exactly.

Constraints: theory only (chores <= 1 process, BLAS-pinned, headroom > 6 GB; the box is at its process
cap — coordinate with A96 if you need a slot); A57/A60/A61/A96 untouched; frozen verifiers untouched;
writes in attempts/A98-exchange-lemma/, docs/proofs/exchange_lemma.md, depgraph K0.RESN note (chip ->
A98; fetch + plain merge + push own paths only; NO rebase/autostash/reset), registry row, LOG.md. Report
tersely: EXCHANGE status first (proved / per-case status / failure configuration), the leaf yield second,
composition third, pointers.
