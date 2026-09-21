# A260 -- LOCKED WALL: unlock it or bound its room -- plus the two analytic leftovers of NORMAL-ROOM
# (CORNER-NOTCH, GAP-DEPTH-ONE).  The last ROOM obligations of the k0 exclusion (PI theory day, 2026-09-21).
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, A258's run258.sh
side, A259's run259.sh chain / finish259.sh and their certs.  A261 runs in parallel on the STRUCTURE obligations.
Read first: docs/proofs/normal_room.md (A259: every free square in the pocket of a normal ring in D' contains the
centre O; HOLE-ONE tilt form; TOOTH; WEDGE; MISS => corner PAIR -- a free square missing O violates a lemma that
sees only ONE ROW'S END SQUARE and THE NEXT ROW'S START SQUARE, 4 parameters (b, phi; a', phi'), s eliminated by
corner_frame_mono; the box-valid PAIR certificate + verify259.py; open: CORNER-NOTCH [C] on the layer b, a' >
63/64, GAP-DEPTH-ONE [M]), docs/proofs/normal_ring.md + attempts/A258-normal-ring/notes/family258.md VERSION 2
(normal-form theorem P1-P4 with RETREAT; s.6 HELD-POKER; s.7 the LOCKED wall: on 43 of 44 corpus ring + poker rows
the poker's wall is an OPEN PAIR -- its normal cell T is met by W AND the poker -- hybrid family D^h, 8 + 2r
coordinates, open gap e in (0.0005, 0.13)), common_sense.md s.2.2 (NORMAL-CELL = CELLS on a cell of ANY pose),
ring_swap.md (CELLS: a family of disjoint cells of any pose met by <= |Pi| squares exchanges), peel.md (POKE).

## The coordinator's two readings (check both; either closes the locked wall)
(U) UNLOCK BY A TWO-CELL FAMILY.  CELLS takes cells of any pose.  On a locked wall take Pi = {T, Q}, Q = a unit
    square pose in the pocket, interior-disjoint from T and met by no square other than the poker F (e.g. F lifted
    out of the notch).  Then M(Pi) = {W, F}, |M| = 2 = |Pi|: W -> T and F -> Q in ONE exchange -- the wall becomes a
    row of two, so a locked wall never survives in the maximiser UNLESS every such Q is met by a third square,
    i.e. the poker is HELD by other free squares.  State and prove: Lemma UNLOCK (any n), and the exact "held"
    condition it leaves.
(R) THE PAIR LEMMA DOES NOT CARE WHETHER THE WALL IS A ROW.  A259's corner PAIR sees one wall's END square and the
    next wall's START square.  On a locked wall the end square is W with its own (b, phi_W): the same 4-parameter
    object.  What changes is the TOOTH: the open gap e lets a free square dip deeper (POKE: depth <= e/2-type
    bound), enlarging the region R.  Extend TOOTH to the open notch (closed form in e, phi_1, phi_W), redo
    HOLE-ONE's inequality with the enlarged R, and get: every free square in the pocket of ANY all-ADJ ring (normal
    or hybrid, all 17 coordinates) contains O  =>  capacity 1  =>  no holder exists  =>  by (U) no locked wall in
    the maximiser, and RING-POKER-RESIDUAL(11) on the full family falls too.  If the enlarged R breaks the
    inequality on part of the domain, say exactly where, and certify the rest with A259's PAIR tree extended by
    the notch parameters (benchmark first; launch detached if <= 50 CPU-h).

## Task
1. (U) and (R) as above -- proofs, the exact domain, tests on the 44 corpus ring + poker rows (exact region search:
   is the poker the only free square that fits, does it contain O, can it be lifted to a Q as in (U)).
2. CORNER-NOTCH: the layer b > 63/64 and a' > 63/64 at a corner.  At b = a' = 1 a unit square fits the corner gap
   -- but then both squares MISS the corner box (D2 is strict: a, b < 1 means they meet it).  Give the analytic
   argument on the layer: a free square in the corner gap needs width >= 1 in one direction; with b, a' < 1 the
   gap is < 1 wide at the box ... (WEDGE + the capping vertex, as A259 suggests); closed form, s-free, m-free.
3. GAP-DEPTH-ONE: prove it (gap-zone vertices of a free square stay at depth >= 1; measured least 1.0003 over 6,177
   pairs) or replace it by what the proof actually needs; it is s-free and m-free, so it is a lemma for every n.
4. Say plainly what ROOM now is: [T] / [T-computed] / [C], on which family (normal D', hybrid D^h, all-ADJ 17-dim)
   and side range; the chain with A258's P1-P4 and A261's structure lemmas to FAMILY-STUCK-EXIST(11) and k0_00;
   the exact remaining obligations.  Deliverables: docs/proofs/locked_wall.md, Statements/Open/LockedWall.lean
   (theorems where the set description suffices, documented axioms otherwise; chain; build + audit 0 sorry -- check
   that NormalRing.lean and NormalRoom.lean are imported in Statements.lean so the audit is clean; AUDIT.md rows),
   code/, results/, certs/ (+ own verifier), pages in docs/residue_map/campaigns/A260-locked-wall/ (a locked wall
   before / after the two-cell exchange; the open notch with the enlarged region R and O; the corner-notch layer;
   geometry-checked, a note per panel saying what it IS, slivers drawn with a 10x inset, undecided grey stipple
   never green), registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines).  EXIT.
