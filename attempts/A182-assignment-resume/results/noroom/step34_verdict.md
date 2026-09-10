# NO-ROOM kill of c0_Y1033 node root/forced:BL(1,1)=F1+F2/b1:BR(0,1)=H+F1/forced:TR(0,1)=H+F1/b2:TL(0,0)=F3+F4@SW+SE (A182 STEP 34)

PI reading (2026-09-09 ~20:10, on the A182 page): "I only see 10 squares placed. 5 simple, H, F1/2/3/4. How does
this admit an 11th square anywhere?"  A182 had recorded the node UNDECIDED (node budget exhausted; lanes off).

Leaf [T]: with ten roles boxed (pins P0..P4, H, F1..F4 at the node's fixed point, `hull` boxes of the journal
record), the eleventh square is a free unit square whose interior must avoid every role's K' (K'(role) lies inside
every pose of the role, A132).  If no pose of a unit square inside the container clears all ten K', the node is DEAD.

Certificate [C, two parts, both exact]:
1. `noroom_bisect.py` (this directory): the free square as a clip-only piece set over the whole container
   ([1/2, s0-1/2]^2 x t in [0,1], 8 t-sub-bins), bisected 20 levels against the ten K' with multibox's exact dead
   test (`_clip_rect_obstacle`, A171/A172 library at or after 13f23204): every dropped piece is a certified
   "every pose meets some core" slab.  Result (step34_bisect.log): all pieces dropped except an open residue of
   centre x t volume 0.002787 with centres in x [3.245, 3.377], y [1.585, 1.840] (the right-wall slot between F1 and
   H; K'(F1) reaches y 1.873, K'(H) starts at y 1.870 -- a graze the piece representation cannot pin).
2. `noroom_lane.py`: A141/A161's exact lane cover (multibox.Node.lane) on the wall strip cell
   (2.877, s0) x (1.0, 2.877), which contains the whole open residue: LANE = 0 (ok, depth 22, 15 s;
   step34_lane.log) -- no unit square meets that strip's interior clear of the ten cores.
Every eleventh-square pose is therefore in a dropped piece (1) or in the strip (2): the node is DEAD by geometry, no LP.

Sampling cross-checks [M]: 0 free poses on a 0.02 x 1 deg container grid; 0 on a 0.002 x 0.25 deg grid of the pocket.
Rule (PI): run the NO-ROOM leaf (LANE >= 11 - k free squares must fit clear of the k boxed roles' cores) at every
assignment node before branching or LP; A182's pass had lanes off.  A189 turns it into a tool over all journaled nodes.
