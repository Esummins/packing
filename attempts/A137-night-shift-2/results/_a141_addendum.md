**A141 (2026-09-08, `polycore lane`, pure geometry, nothing in A57/A96 written).** A118's LANE-COUNT leaf re-run
with A132's POLYGON cores K' -- and, for the pins, A135's EXACT pin core (K' of the pin's own zero-tilt box,
half-side 1/2 - delta/sqrt2 at A57's m-hulled pins, not `pinguard`'s 0.48999997) -- at the USABLE SLOTS (a slot
counts only where its extension class is certified dead on the closed window [191/50, 969271/250000]; all of
k6_18/20/23 for k5_11 and k6_23/27/28/29/30 for k5_16 are, A56/A61/A114 scoreboard). **Sweep COMPLETE over all
1,693 alive A57 records (1,368 A57 + A57box; 1,590 distinct nodes with A60):
188 distinct alive A57 nodes have `LANE_K' + M <= 1` at some usable slot -- 96 k5_11 + 92 k5_16 -- and EVERY ONE
has `LANE_K' = 0` with `M = 1`**, i.e. the slot is met by the conditioned square alone, SLOT-CROWD's two non-pin
meeters are impossible, and the node is DEAD by teleport into the (already dead) extension class. By slot:
k5_11 = BR(0,1) 45, TR(0,0) 27, TL(1,0) 23, BL(1,1) 1; k5_16 = BL(1,0) 54, TL(1,0) 38. 194 of the 244 kills over
A57+A60 are level-1 and 50 level-2. **Overlap with the clip kills is essentially nil: of the 183 nodes in A131's 132 +
A142's 17 A57 + 34 A60 exact-pin-clip lists (all 183 were in the swept corpus), exactly ONE --
`k5_16_interior_Y0281_D03` -- is also an A141 slot kill, so 187 of the 188 A57 nodes are NEW** (`results/t6_overlap.json`).
Each kill carries a replayable `polycore_slot_lane_v1` certificate (`attempts/A141-polycore-lane/certs/slot_*.json`):
a finite cover of the slot-meeting poses whose every leaf is discharged by the container, by a certified separating
axis, or by ONE rational point proved exactly (A132 `vertex_ok` = Lean `checkVertexInPBox`) to lie in every pose of
the leaf box AND of a pin's or the conditioned square's box -- so the Lean consumer is
`shared_point_same_square`, no polygon. The independent checker `code/check141.py` passes **294 of 294** A141
certificates. Sample line per kill: 200,000 poses drawn, ~1.2e5 meeting the slot cell, **0 free**. Caveat A118-O1
stands: a LANE kill excludes class-S packings with EXACT pins, not the delta = 1e-2 slack family. At resume, retire
these 188 (and their descendants) before any LP.
