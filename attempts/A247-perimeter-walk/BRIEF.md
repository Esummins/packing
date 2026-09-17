# A247 -- the PERIMETER WALK: set down BL's two meeters, then chase the meeter counts around the twelve cells; the
# admissible walks should be few, and each is a small geometric case (PI, 2026-09-16 23:30).
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (searches detached
with a resume block and logs/STOP), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 2 python processes
(BelowNormal, affinity 0xFFFF; the k5 frontier, A238, A241 and A244's lanes are running -- never touch them).
Pages to docs/residue_map/campaigns/A247-perimeter-walk/.
Read first: attempts/A246-construct-towards/{docs: docs/proofs/construct_towards.md, results/construct246.md,
notes} (the proved rules: SQUARE-IN-TRIANGLE, NOT-SELF-SUFFICIENT [T], TYPE-F-OWN [T], TWO-CORNERS, MAX-FIVE,
ADJ-REACH, CAP-REDUCTION; SLOT-MET(eta) certified to depth 1e-7; the composition to COUNTS is satisfiable; the
smallest open reduction "8 poses + s"), A244 (CROSS-CORNER-REACH [T]; the 282 + 34 twelve-stuck packings and their
per-cell meeter sets -- the empirical catalogue of walks; slot supply OWN 924 : ADJ 192 : FREE 207), A245 (STACK's
true form; the twelve-stuck shape is corner crowds with own tips + free squares in the slots), wedged_seal.md,
wall_slot243.md, pocket_waste.md (TILT-MIN, DEPTH-BUDGET), ring_capacity.md (Lemma TWO), sideband.md (B0/B0').

## The walk
Cells: the 12 border cells in a ring (c00 corner boxes, c01 up the wall, c10 along the floor, in each corner's
frame).  Squares: 8 meeters (two per corner box by hypothesis) + 3 free.  A WALK is an assignment of each of the 12
cells to two distinct squares (its meeters), such that every square's cell-set is REALISABLE: a unit square at
side s <= s-hat (then s < 4) can meet that set of cells simultaneously (with the pose conditions), and the whole
assignment is realisable by 11 interior-disjoint squares.  The lemmas cut the walk down: MAX-FIVE (a square meets
<= 5 cells), NOT-SELF-SUFFICIENT (a corner's two meeters cover <= 5 of its 6 incidences), TYPE-F-OWN (a flat meeter's
corner supplies exactly 4), ADJ-REACH / CROSS-CORNER-REACH (who can reach the neighbour's slot and when),
WEDGED-SEAL (a meeter on both walls is alone -- so not doubly-met-compatible), SLOT-MET, TWO-CORNERS, and the room
for the 3 free squares (a free square in a wall slot is inside the wall band; Lemma TWO on the centre).

## Task
1. CATALOGUE: enumerate every subset of the 12 cells a single unit square can meet at side s <= s-hat (and at
   s < 4): the cells within reach form a small window (a square's footprint has diameter sqrt2), so the candidate
   subsets are few (connected runs of <= 5 cells along the ring plus the corner combinations); for each candidate
   decide realisable / not by a rigorous test (interval branch-and-bound over the pose, or a proof from the
   lemmas), and record the pose conditions (offset / tilt ranges) for the realisable ones.  Check the catalogue
   against every square of the 316 corpus twelve-stuck packings (each must be in it).
2. WALKS: enumerate the assignments (up to the D4 symmetry of the ring) consistent with the catalogue and the
   lemmas; count them; list them with their supplier structure (OWN / ADJ / FREE per slot) and how many free
   squares they consume in slots.  Report the number -- the PI expects it to be surprisingly small.  Check that
   every corpus packing's walk is in the list.
3. GEOMETRY per walk: each walk fixes which square meets which cells, so its realisability is a bounded problem in
   the poses of the involved squares with the meeting depths > 0, disjointness, containment, side s: run a
   rigorous interval branch-and-bound per walk over s in [3.82, s-hat] (then up to 4) to decide infeasible /
   feasible (with a witness, exactly verified); report per walk the verdict, the tight constraint, and the CPU.
   Where a walk is infeasible for a closed-form reason (the composed inequality), state it as a lemma.
4. Say plainly: how many walks exist at s <= s-hat, how many are killed analytically, how many by the bounded
   search, how many remain (with the witness or the tight case drawn) -- and whether STUCK-EXIST(11) is now
   closed on the window (then k0_00 closes via no_packing_of_stuck_exist).  n-general: the catalogue and walks
   depend on n only through the free-square count; note what changes at other n.
5. Deliverables: docs/proofs/perimeter_walk.md, code/ (catalogue247, walks247, bb247, verify247), results/
   walk247.md (+jsonl: the catalogue, the walks, the per-walk verdicts + certificates), pages (the catalogue's
   realisable cell-sets drawn; the walks as ring diagrams; the surviving walk's tight case), Lean: if a walk's
   infeasibility is closed-form, Statements/Open/ with the lemma; registry row, LOG entry, ledger s.4 note.
   Report once (<= 20 lines) and EXIT.
