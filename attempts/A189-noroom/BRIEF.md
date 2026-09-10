# A189 -- the NO-ROOM leaf as a tool, over every recorded assignment node

## Task (restated, from the coordinator's instruction of 2026-09-09)

PI's leaf, discovered on the A182 page and certified by the coordinator on c0_Y1033's STEP 34 node
(`attempts/A182-assignment-resume/results/noroom/step34_verdict.md`, scripts `noroom_bisect.py`,
`noroom_lane.py`): at a node with `k` boxed roles (pins, H, instantiated free squares at their
multibox fixed point) the remaining `11 - k` free unit squares must each fit inside the container
with interiors clear of every boxed role's K' (A132: K'(role) lies inside every pose of the role).
For `k = 10`, if no pose of a unit square clears the ten cores the node is DEAD.

Turn that into a tool and run it over every recorded assignment node.

1. `code/noroom189.py`: `noroom(roles, s0, budget)` -- normalise the roles; bisect the free square's
   clip-only piece set to a SHALLOW depth (the coordinator's run exploded past depth 16: use ~12-14),
   collect the open residue as a few axis-aligned pocket cells with a margin, run A141/A161's exact
   lane cover (`multibox.Node.lane`) per pocket (max_open ~100k, deadline per cell).  Verdict DEAD iff
   the pocket lane values sum to less than `11 - k`.  Record both certificates (dropped-piece
   count/volume, per-pocket lane result).  General `k < 10`: the sound counting bound over a cover of
   the residue, plus the container-partition variant with the meeting multiplicity, plus the `k = 9`
   case.  Reproduce the STEP 34 kill as the regression test.
2. RUN over every recorded node of A182's journals
   (`attempts/A180-forced-first-assignment/results/journal/*.jsonl`, fields `label`, `kind`, `hull`),
   nodes of kind branch/leaf with >= 9 boxed roles first, then >= 8; then over A183's alive S3 nodes
   of l1_104 (`attempts/A168-cascade-fable/results/renorm18*.jsonl`, roles H, D, S, B = 4 boxed,
   7 free: only the counting bound applies -- report whether it ever bites).
   Record `results/noroom189.jsonl` (node, k, verdict, certificates, seconds); every DEAD with its two
   certificates on disk.
3. A status-collector block in `docs/shadows/status_gallery.py` in the style of (7b)/(7c) for pages
   whose EVERY alive assignment node dies (a page dies only if all of its alive leaves die -- check
   A182's tree/journal structure; say exactly what was counted), rerun it, report pages retired;
   `docs/residue_map/noroom_c0_Y1033.svg` in the drawing rules (`docs/residue_map/gen_a57_lp.py`
   style): the STEP 34 node with the ten K' filled, the dropped region hatched, the residual pocket
   and its lane result, a note per panel; `docs/residue_ledger.md` section 4 paragraph;
   `docs/budget.md` section D item; registry row; LOG entry; commit at every milestone.

## Rules

<= 1 python process, BelowNormal, affinity 0xFFFF; box ceiling 12 python processes (A183's shards,
A184, A185, A186, A188 running); read-only on every other attempt; no recursive deletes;
PYTHONDONTWRITEBYTECODE=1.  Every claim tagged [T] theorem / [S] script / [M] measurement /
[F] figure / [C] certificate.
