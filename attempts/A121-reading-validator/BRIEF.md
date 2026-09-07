# A121 — validate the PI's shadow readings and turn them into node cuts (Opus chore, read-only, incremental)

Context (2026-09-07). The PI is reading docs/shadows/*.svg row by row into docs/shadows/review.csv, column
`PI_reading`, in shorthand: `r <sq> <cell>` = room: the named cell is met only by the named square (teleport cut);
`ns <sq> <cell>; ...` = near-snapped: the named squares sit a hair off the named cells (SNAP cut; a `*` on a square
marks the node's own hypothesis square); `i` = incomplete support (< 11 squares; goes to the warm re-solve queue);
`g <description>` = a genuine grain (load path / shared-tilt structure). Names and orientation are those of the
RIGHT panel (the minimised packing in the shadow's canonical frame); the map back to each node's frame is the stored
D4 op (`frame_ops` / `struct_op` in attempts/A107-shadow-gallery/results/{shadow_nodes,shadow_nodes_k0}.json). More
rows will arrive; the chore is incremental and re-runnable (process rows whose reading changed since the last run).

Read first: docs/shadows.md (Part I S01–S53, Part II K01–K30; per-entry poses of the minimised packing, slot sets,
the alive nodes each explains), attempts/A107-shadow-gallery/results/{minima,shadows,shadow_nodes,extract}*.json,
docs/proofs/k0_route.md (K0-FREE: a corner cell met by ≤ 1 square teleports — corners always usable), docs/proofs/
slot_crowds.md + attempts/A118-lane-count/notes/method.md (SLOT-CROWD; the UPDATED usable-slot table: a slot is usable
where its extension class is certified on the window — after A114 all k6 extensions are full-window), docs/proofs/
flood_lemma.md §1 (SNAP destination form: the square snaps into the cell iff no other square meets the open cell),
attempts/A115-k0-corner-rows/notes/t4_report.md (the warm re-solve queue for `i` rows), attempts/A118-lane-count/
code/lanelib.py (μ_p, cell frames, octagon tests — reuse), docs/residue_map/gen_a57_lp.py (drawing conventions).

## T1 — validate each reading against the minimised packing
For each filled row: parse the shorthand; map the named squares/cells to the entry's poses (right-panel frame).
`r`: confirm that in the minimised packing the named cell is met (open interior) by exactly the named square and no
other, report the meeter's depth, and whether the cell is a corner (always usable) or a slot (usable iff its extension
is window-certified — say which extension class). `ns`: for each named square, the L∞ distance of its pose to the
named cell's centre and its tilt mod 90; whether the cell is otherwise unmet (SNAP applies) or met (then it is a crowd
case — say by whom); `*` squares: note that the hypothesis square is the snapper. `i`: confirm the support has < 11
squares and cross-reference the cells to A115's warm re-solve records (which are already certified, which are
queued). `g`: record the description; if it names a load path, check it against A107's Fritz-John multipliers for the
entry and A116's stability radii where the entry is S02/S07. Flag every disagreement between the reading and the data
(e.g. a named cell met by a second square, a named square 0.3 from its cell) as `?` with the number — these are the
rows the PI wants re-drawn.

## T2 — from reading to node cut
For each validated reading, list the alive nodes the entry explains (shadow_nodes*.json) and, per node, the cut in the
NODE's frame: the cell and square mapped back through the node's op, the node's class, and whether the cut is
(a) a teleport of a FREE square into a corner (K0-FREE: kills the configuration; the node needs the LANE-COUNT test
of A118 to become a node kill — run A118's `lanelib` lane test for that cell on that node and report LANE + M),
(b) a teleport into a usable slot of a pinned class (SLOT-CROWD; same lane test), (c) a SNAP of the node's own
hypothesis square (`*`): the node's box vs the cell — if the whole box lies within the SNAP ball of the cell and the
cell is otherwise unmet in every configuration of the node (lane test again), the node is dead; (d) `i`: the warm
re-solve status. Output `results/cuts.jsonl` (one row per (node, cut)) and a summary table: per reading type, nodes
explained, nodes where the lane test makes the cut a node kill, nodes where it does not (the M = 1 case), and the
disagreements.

## T3 — what it is worth
Per class and level: node kills that follow from the readings alone (no LP), against the tree's ~850 s per node; the
CPU-h off the 10–11-day A57 schedule and off A99's k0 frontier (conditional on k1_00 for k0 corner teleports).
One line per batch. Re-run on demand as more rows land (`python code/validate121.py --since <commit>`).

Constraints: READ-ONLY on every campaign and attempt except your own paths; ≤ 1 process, BLAS-pinned, pure geometry
(lane tests reuse A118's code; no LP); headroom gates; NO recursive deletes, PYTHONDONTWRITEBYTECODE=1; git = fetch +
plain merge + push own paths (no rebase/autostash/reset). Writes: attempts/A121-reading-validator/{code,results,notes,
logs}, registry row, LOG.md. Report ONCE per batch: T3 line first, the disagreement list second, the per-type table
third, pointers last. Process the rows currently filled (K01–K21) now.
