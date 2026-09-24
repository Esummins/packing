# A279 -- THE NEST RESIDUAL of NO-FLOAT2: Y under a high D with C at the wall -- prove the local statement L there,
# or draw the two-floater corner that survives normalisation.  Plus two doc slips.  (2026-09-24.)
Fable.  TINY STEPS: one tool call per turn, <= 60 lines per Write, derivations on disk in numbered pieces
(notes/nest279_partN.md) committed as you go, never a single response over ~10k tokens; first turn = commit a
20-line outline.  LAUNCH-AND-EXIT.  ONE heavy python at most (A278's flat278.py may still be running -- never
touch it; nor the status loop, A262/A263/A273 chains, A269/A270 loops, their certs).
READ FIRST: docs/proofs/k0_knowledge.md (s.1, s.2 incl. s.2.3 and the A278 appends in s.11, s.5, s.7, s.8), then
docs/proofs/no_float2.md (A278: FLOAT-SLOPE [T]; SHADOW-CELL [T]: a wall cell whose part outside D lies in the
shadow of {C, D, X, Y} is met by D alone, so P1 lands D; NO-FLOAT2 <= L (Theorem 3.1), L = the 4-square local
statement; the witness lands D on the flat floor cell between C's low footprint and Y; the RESIDUAL: every point
of the 10-parameter residual satisfies (NEST) eta+ < alpha- <= alpha+ < xi- -- Y UNDER a high D, C at the wall,
the opposite end from the witness; naive certificate > 1e3 CPU-h; flat278 = flat cells only, results in
attempts/A278-no-float2/results/), docs/proofs/float2_room.md (ONE-DROP, MUTUAL corrected by A278, LOW with
floating D), box_meeters.md (P1+, BLOCKER-SIDE, STRIP-LANDING, LIFT), normal_ring.md (P1-P4; Phi2 rows, Phi4
RETREAT -- more potentials are available than Phi1 alone!), ring_swap.md (CELLS on cells of ANY pose -- not
only wall-touching cells: any unit-square pose met by <= 1 square other than the mover is a landing cell),
locked_wall.md (LIFT), wedged_seal.md, no_jam.md (the count; corner types).

## The question
In the NEST residual (Y below a high D, C against the wall, X above C), find the cell that lands D or C:
 (i) SHADOW-CELL with cells of ANY pose (A278 tested flat floor cells and the straight drops): the region under
     D and right of C, between Y and C -- is there a unit-square pose there met only by D (or only by C)?  Use
     CELLS's full generality: the cell need not touch a wall (then Phi1 does not rise -- but Phi4 RETREAT or a
     new potential term 'sum of distances of floaters to their walls' may; VALUE-WLOG allows any potential --
     state the term and prove its exchange step).
 (ii) If D is high (its lowest point near 1) and C at the wall: does C still meet the open box?  (H3-type
     condition: C's lowest point < 1 and its left vertex above 1 by LOW) -- and is Y then forced to meet the box
     too (a third meeter, THIRD type, already covered)?  Chase the count: FLOAT2 needs both floaters meeting
     the box and NO toucher meeting it (else the type changes); with Y under D and C at the wall, show one of
     Y, X meets the box, or the box has a free wall cell (P1 lands), or the packing is not family-stuck.
 (iii) If a configuration survives (i)-(ii): draw it exactly (all four squares + the box + the free cells
     tested), verify family-stuckness of the 12-cell system locally, and state the residual's dimension and
     the cheapest certificate (the flat-cell + shadow test of A278 restricted to the NEST box).
## Slips to fix (cite the correct statement, one-line edits, explicit-pathspec commits)
docs/proofs/k0_knowledge.md s.1 and docs/proofs/no_jam.md s.1: the gloss "X misses the open box iff y_X >= 1 -
cos phi_X" is wrong as written -- the correct statement: X misses the open box (0,1)^2 iff X's LOWEST point is at
height >= 1 (A278's erratum); write it with X's parametrisation named (leftmost vertex (0, y_X), edges (cos phi,
sin phi) and (sin phi, -cos phi): lowest point = y_X - cos phi).
## Task
1. Outline (commit).  2. (i)-(iii).  3. The slips.  4. docs/proofs/nest_residual.md (pieces),
Statements/Open/NestResidual.lean (build + audit 0 sorry via PYTHONIOENCODING=utf-8 python lean/audit.py; one
import line after fetch + merge), page in docs/residue_map/campaigns/A279-nest-residual/ (the NEST configuration
with the tested cells; geometry-checked; note per panel; undecided grey stipple), registry row, LOG entry,
ledger s.4 note, k0_route.md s.13 5d, APPEND entries to k0_knowledge.md.  Report once (<= 12 lines).  EXIT.
