# A244 -- search for a 12-STUCK four-crowd: 11 unit squares with all four corner boxes AND all eight wall slots
# doubly met (PI, 2026-09-16 19:30: "have you started that search? if you can't construct a ring like that, that's
# a pretty big issue for k0 existence").
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (the search runs
detached, per-row commits, resume block, logs/STOP), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, at most 2
python processes (BelowNormal, affinity 0xFFFF; the k5 frontier workers / loop, A238's sweep and A241's parametric
campaign are running -- never touch them).  Pages to docs/residue_map/campaigns/A244-twelve-stuck/.
Read first: attempts/A243-reach-root/notes/wall_slot243.md (Lemma WALL-SLOT [T]: a wall slot met by <= 1 square swaps
in the slot square; SLOT-MET [S]; the 12 BORDER CELLS = 4 corner boxes + 8 wall slots BL01, BL10, BR01, BR10, TR01,
TR10, TL01, TL10 in each corner's frame; the window ring family and A226's rings are NOT 12-stuck: each tilted
partner's slot is met by it alone), attempts/A217-torque-probe/code/{search217,crowd217,opt217,geom217}.py (the
crowd search: side minimisation with CROWD ROWS forcing the corner boxes to be doubly met, tilt floors, random
restarts, exact SAT verification of results; results in search217_*.jsonl), A226's crowd226 (CROWD-ABOVE
constructions from records with corner dominoes), ring_swap.md (swap_packing; the 12-cell meeting test), the
coordinator's meets-open-cell check (a square meets an open axis cell iff their interiors overlap: separating-axis
gap < 0).

## The question
Does ANY packing of 11 unit squares exist, at any side S, with all 12 border cells doubly met (each cell's interior
overlapped by >= 2 distinct squares)?  If yes, what is the smallest S at which one exists (the 12-STUCK threshold),
and is it above 4 / above s-hat = 3.877084?  A217 found the four-crowd (4 corner boxes) threshold at 4.0013 with crowd
rows and never a free FJ four-crowd; the 12-stuck condition is stronger.  Secondary: among 12-stuck packings found,
is any one LOCKED (every meeter loaded; the FJ LP feasible without artificial rows)?

## Task
1. Extend the crowd search: crowd rows for all 12 cells (each cell must be met by >= 2 distinct squares -- use the
   same penalty / constraint form as A217's corner crowd rows, with the meeting test = interior overlap), minimise
   S over 11 poses, random restarts (>= 2 000), tilt floor OFF (and a variant with the floor at 5, 10, 20 deg to see
   what it does), from random starts and from A226's rings / the window family / CROWD-ABOVE crowds as seeds.
   Verify every candidate exactly (no overlaps, inside the container, each of the 12 cells met by >= 2 squares with
   exact separating-axis tests).  Record per candidate: S, the 12 cells' meeter sets, tilts, whether any wall slot
   is served by an adjacent corner's wall meeter (the mutual wall-grain supply), by a third wall member, or by an
   interior square, and the FJ stress (A217 stress217.analyse: loaded / unloaded meeters, external rows needed).
2. THRESHOLD: the smallest verified S with a 12-stuck packing; a plot of the best S vs restarts; the same for the
   4-stuck (corner-only) condition as the control (should reproduce ~4.0013).  If none is found below some S_0,
   state S_0 with the search effort (restarts, CPU-h) -- evidence, not proof, say so.
3. At S >= 4: construct a 12-stuck packing by hand if the search struggles (e.g. from a 4x4 grid with 16 squares
   remove 5 keeping the 12 border cells doubly met -- is that possible with 11? the border cells need 2 meeters
   each, 24 incidences; a flush square meets at most 2 border cells; count), and report the exact minimum S the
   hand constructions reach.
4. Deliverables: code (search244.py, verify244.py), results/twelve244.md (+jsonl: every verified candidate),
   pages (the best 12-stuck packing found, all 12 cells drawn with their meeters; the threshold plot), registry
   row, LOG entry, ledger s.4 note.  Report once (<= 12 lines: the threshold, the best packing's structure, the
   control, the effort) and EXIT.
