# A262 -- NO-JAM(11) at ring level: a corner whose box meeter FLOATS (A261's JAM) dies by COUNT + ROOM.
# (PI theory day on k0, 2026-09-21/22.  The last STRUCTURE obligation.)
Fable.  LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors, no
interim messages, explicit-pathspec commits (fetch + plain merge only), PYTHONDONTWRITEBYTECODE=1, ONE heavy python
process at most (BelowNormal, affinity 0xFFFF; sub-minute helpers fine); detached launches call Git Bash by explicit
path.  RUNNING, never touch: the k5 pass loop, A256's loop256, A257's pilot257, the status loop, A259's / A260's /
A261's certificate chains and their certs.  A263 runs in parallel on the open-pair / slab leftovers.
Read first: docs/proofs/box_meeters.md (A261: P1+, BLOCKER-SIDE, STRIP-LANDING, SAME-WALL [T]; meeters_split: a
doubly-met box has <= 1 toucher per wall, every further meeter FLOATS; the JAM witness: floor square A and floater C
both at 13.7 deg meeting the box, C 0.72 off the wall, wall square X at 27.9 deg above C, persists at
ring-compatible offsets a0 <= 0.8 with margin 0.0033; the chain; A261's warning that random-start Nelder-Mead
returned a false "none" -- use hard-feasibility optimisers with many structured starts and exact checks),
normal_room.md (A259: MISS => corner PAIR; every free square in a normal ring's pocket contains O; HOLE-ONE tilt
form; TOOTH; WEDGE), locked_wall.md (A260: PLUG, OPEN-TOOTH, hybrid PAIR certificates), normal_ring.md (P1-P4),
peel.md (BAND-COUNT, core_fits), mintilt253.md (HOLE-ONE).

## The coordinator's reading (check it)
[T, trivial] Below side 4 a unit square that does not meet the unit band lies in [1, s-1]^2, of side < 2, so it
contains O (HOLE-ONE); at most ONE square of a packing contains O.  So >= 10 of the 11 squares meet the band.
A JAM corner spends THREE squares on one corner (A, C, X) where the ring spends two, and its floater C reaches
from 0.72 to ~1.94 -- to the centre.  With j JAM corners the outer structure has >= 8 + j squares (if X is not
another box's meeter) and the pocket is smaller than the ring's.  So: j = 1: 9 + room; need room <= 1 -- the
PAIR-type bound with the JAM corner's squares as the obstacles (C is a bigger obstacle than a toucher).  j >= 2:
need room 0 -- two floaters reaching the centre leave no unit square containing O?  If X IS the adjacent box's
wall meeter the count changes: enumerate.

## Task
1. ENUMERATE the corner types a normal-form family-stuck packing allows beyond the ring's (two touchers): JAM
   (floor toucher + floater + the wall square above), its mirror, the third-meeter corner (two touchers + a
   floater), by meeters_split and P1+; for each the squares it uses and which may be shared with the adjacent
   corners (can X be the next box's meeter?  can C serve a wall slot?).  Table of global structures by (j, shared).
2. ROOM per structure: extend A259's MISS => PAIR reduction to a JAM / third-meeter corner (the obstacles at that
   corner are A, C, X): does every free square still contain O?  Closed forms first (C's far vertex vs O; the
   region left of C); then the box-valid certificate over the JAM corner's parameters (benchmark; launch detached
   if <= 50 CPU-h) with its own verifier.  For j >= 2 (or whenever the count leaves 11 = outer + 1): show NO square
   containing O fits, or draw the 11-square witness -- that would be a family-stuck packing on the window and the
   most important object in the lab; check it exactly (12 cells, every family) before believing it.
3. SEARCH honestly for a family-stuck 11-packing with a JAM corner at s in {3.82, s-hat} and on (s-hat, 4): hard
   feasibility, structured starts from the JAM witness embedded in corpus rings, >= 500 starts, exact verification.
4. Say plainly: NO-JAM(11) [T] / [T-computed] / [C]; with meeters_split => BOX-MEETERS(11); the m-general form
   (JAM is m-free; the count is 4(m-2) + j); the exact remaining obligations.  Deliverables:
   docs/proofs/no_jam.md, Statements/Open/NoJam.lean (build + audit 0 sorry, no "(no output)" rows; AUDIT.md
   rows; keep any Statements.lean edit to one import line after fetch + merge), code/, results/, certs/ (+
   verifier), pages in docs/residue_map/campaigns/A262-no-jam/ (a ring with one JAM corner and its pocket; the
   j = 2 structure; geometry-checked, a note per panel saying what it IS, slivers with a 10x inset, undecided grey
   stipple never green), registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines).  EXIT.
