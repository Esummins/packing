# A278 -- NO-FLOAT2: in a normal-form (Phi1-maximal) family-stuck packing no corner box has two floating meeters;
# and CAP-2 at the JAM corner.  The last two theory items of NO-JAM(11).  (2026-09-24.)
Fable.  TINY STEPS: one tool call per turn, <= 60 lines per Write, derivations on disk in numbered pieces
(notes/nofloat278_partN.md) committed as you go, never a single response over ~10k tokens; first turn = commit a
20-line outline.  LAUNCH-AND-EXIT.  ONE heavy python at most (A277's float277.py search is still running -- never
touch it; nor the status loop, A262/A263/A273 chains, A269/A270 loops, their certs).
READ FIRST: docs/proofs/k0_knowledge.md (s.1 definitions, s.2 theorems incl. the new s.2.3 entries, s.5 FALSE, s.7
DEAD), then docs/proofs/float2_room.md (A277: ONE-DROP [T] -- a square blocks at most one drop of a floater;
MUTUAL [T] -- for two floaters C (upper-left) and D (lower-right) with a positive-slope separator, only C's floor
drop and D's wall drop can be blocked ... check the exact statement; Lemma LOW with a floating D; link 5d = CAP-2
not ROOM; [M] float277: in float262.json D's floor drop is FREE so P1 lands D -- A262's 'JAMMED FLOAT2 EXISTS' was
the coarse-grid J; with a floor toucher Y under D's right vertex all four drops are blocked (exact) yet P1 STILL
lands D (J_D = +0.024) via a flat floor cell; sup 0 attained only where a floater becomes a toucher -- 'no
normal-form FLOAT2 corner exists on disk'), docs/proofs/box_meeters.md (P1+, P1 = the Phi1 maximiser: a
family of disjoint WALL-TOUCHING cells of any pose met by <= |Pi| squares is met by touchers only; BLOCKER-SIDE;
STRIP-LANDING; LIFT), docs/proofs/normal_ring.md (P1-P4), docs/proofs/ring_swap.md (CELLS on cells of any pose),
docs/proofs/no_jam.md (corner types; the count), attempts/A277-float2-room/code (float277: the drop / any-pose
cell tests; cert277 diameter kernel) and results/float277.jsonl (read what has landed).

## Theorem NO-FLOAT2 (to prove)
In a Phi1-maximal family-stuck packing at s in [3.82, s-hat], no corner box is met by two floaters.  Route:
the two floaters C, D meet the open box; by MUTUAL at most two of their four drops (C's floor / wall, D's floor /
wall) can be blocked at all, and by ONE-DROP each blocker blocks one; a free drop is a wall-touching cell met
only by the floater => P1 (CELLS with |Pi| = 1) lands it, contradicting maximality of Phi1.  So both blockable
drops must be blocked by two distinct squares Y (floor, under D) and X (wall, beside C).  Then the [M] fact:
P1 still lands D through a FLAT FLOOR CELL (D dropped and rotated to flat? a different cell than the straight
drop): identify that cell exactly (the any-pose cell of P1+: any wall-touching unit-square pose met by no
square but D -- e.g. the flat cell on the floor between Y and the wall, or between Y and A?), prove it is
always available when Y blocks D's straight drop (Y under D's right vertex leaves the floor left of Y free up
to the wall: width >= ...; a flat unit cell needs width 1 -- is the corner box itself (0,1)^2 that cell?  It is
met by C and D (floaters) but by no toucher -- P1+ says a family {box} met by <= 1 ... no: the box is met by
TWO squares.  Find the right cell), and conclude.  If a configuration resists (all drops and all flat cells
blocked with the packing still family-stuck and Phi1-maximal), draw it: that is the residual.
## Then CAP-2 at the JAM corner (indirect jams)
BL-CAP-2(A, C): no two interior-disjoint free squares in the BL sector both miss O with A, C as obstacles.  A277's
diameter kernel prices it 3-100 CPU-h; first try the analytic route: two misses stack (open_pairs.md / last_two.md:
the upper one contains O horizontally [T]); reuse strip_jam.md's LEFT constraint and flat_x.md's corner
mechanism; if it closes [T] say so, else state the exact residual and the cheapest certificate (do not launch
above 20 CPU-h; the lab is at its ceiling).
## Task
1. Outline (commit).  2. NO-FLOAT2 [T] or its residual drawn.  3. CAP-2(A, C) [T] or residual + price.
4. docs/proofs/no_float2.md (pieces), Statements/Open/NoFloat2.lean (build + audit 0 sorry via
PYTHONIOENCODING=utf-8 python lean/audit.py; one import line after fetch + merge), page in
docs/residue_map/campaigns/A278-no-float2/ (geometry-checked, note per panel, undecided grey stipple), registry
row, LOG entry, ledger s.4 note, k0_route.md s.13 5d, APPEND entries to k0_knowledge.md.  Report once (<= 12
lines).  EXIT.
