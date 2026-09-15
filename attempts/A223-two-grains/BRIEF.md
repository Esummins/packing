# A223 -- TWO GRAINS and the CLICK: a self-supporting k0 structure is two opposite-handed grains with boundaries on
# all four walls, and the grain-level click-down beats it (PI, 2026-09-14 ~21:10).
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (long runs detached,
per-row commits, resume block), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 2 python processes
(BelowNormal, affinity 0xFFFF), never touch running workers.  Pages to docs/residue_map/campaigns/A223-two-grains/
(geometry-checked, notes per panel, times; extremal outlines only at admissible poses).  Read first: grain_flood.md
(Lemma GRAIN, GRAIN-LP: side = wall-to-wall load path length as a chain formula in the tilts; Theorem CONT; INHERIT;
the chain menu), descent.md Theorem D3 (grain-move descent) and descent_grains.md s.4-6 (what a grain is, common-tilt
and slide moves), wall_torque.md (A219: Lemma W, TWO-CONTACT; the ring's single-square modes fail at second order),
k0_count.md s.5 + ring_swap.md (the ring rand_0_0569|t20, its load path page in attempts/A218-k0-count), A217's
witness files (the 193 HELD/CROWD four-crowds; the drains that return to side 4.000).

## The PI's picture (verbatim in substance)
The ring witness is two half-rings of OPPOSING tilt (left half 2,3,4,5 at 70 deg; right half 6,7,8,10 at 20 deg)
balanced against each other at the top middle (3|9|10) and the bottom middle (4|6).  The two squares leaning against
each other at the bottom middle would CLICK DOWN and sit flush on the floor unless something above pins them; that
something must itself be pinned; so a self-supporting k0 structure needs two opposing GRAINS with grain boundaries
running along all four walls and between them.  For any n a grain-boundary MINIMISER lowers the wastage: it
collapses almost all wall / grain boundaries to flush and keeps a single DIAGONAL boundary as the sole wastage between
grains (or a split of boundaries centred on that diagonal).  The proof should use the grain interface theorems.

## Task
1. Lemma TWO-GRAIN [state, prove or tag]: in a teleport-stuck k0 packing (every corner box met by >= 2), partition
   the load-bearing squares into grains by tilt handedness (theta in (0,45) vs (45,90) mod 90, in the frame of the
   wall they touch; 45-deg diamonds and flat squares as their own cases) and contact adjacency; show the corner
   meeters cannot all belong to ONE grain (a wall-to-wall load path of one handedness cannot turn a corner?  use
   Lemma PUSH / TWO-CONTACT / Lemma W), so there are >= 2 opposite-handed grains meeting at internal boundaries, and
   the union of the grains' wall boundaries covers all four walls.  Exact statement, n-general.
2. Lemma CLICK (the grain-level move): the COMMON-TILT move of a grain toward its alignment (Theorem D3's move) is
   side-non-increasing because its chain formula (sum of projected widths cos theta + sin theta along the load path)
   decreases toward alignment; the new content is FEASIBILITY across the internal lean boundary between two
   opposite-handed grains rotating in opposite senses: show the lean contact slides (no penetration) along the joint
   move, i.e. the PI's click.  Say exactly when it can fail (a pin above; a rattler in the way -- and whether a
   rattler can be moved aside first by SWAP/teleport at the same side).
3. Theorem FOUR-WALL (the target): a packing whose grain boundaries run along all four walls clicks down, grain by
   grain, to a fully FLUSH packing at a side no larger than its own; a flush (axis-aligned) packing of n unit squares
   has side >= ceil(sqrt n); hence such a packing has side >= ceil(sqrt n) -- at n = 11: >= 4 > s-hat, so no
   two-grain-four-wall k0 structure exists in the window, with no force argument and no load hypothesis (rattlers
   included if 2 covers them).  Then the refinement the PI names: the minimiser keeps a SINGLE diagonal seam
   (Conjecture SEAM, all n): state it, check it against the known optimal / best-known packings (n = 5, 10 = Goebel,
   11 = Trump, 17, 18, 19: which have one diagonal seam, which do not), and say what it would give and what it needs.
4. TEST: on the ring witness identify the two grains and their chain formulas s_G+(theta+), s_G-(theta-); run the
   joint click-down (both grains toward alignment) with exact feasibility checks; plot the side along the move (does
   it reach 4.000 flush monotonically?).  Then all 193 four-crowds: grains found, click feasible / blocked (by what),
   side at the end; compare with A217's observed drains (to 4.000).  Pages: the ring's two grains coloured by
   handedness with the boundaries drawn; three frames of the click; a failing case if any.
5. Deliverables: docs/proofs/two_grains.md (TWO-GRAIN, CLICK, FOUR-WALL, SEAM; tags [T]/[S]/[M]/[F]/[C]; n-general
   and n = 11), Statements/Open/ files for each stated lemma (build + audit, 0 sorry), code/, results/click223.md
   (+jsonl), pages, registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines: what is proved, what the
   click does on the ring and the 193, the exact remaining obligation, what closes for k0_00, commits) and EXIT.
