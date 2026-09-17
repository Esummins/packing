# A245 -- SNAP-DOWN by directionality: any 12-stuck ring has a wall grain that clicks flush and a subset that
# reduces to simple squares (PI, 2026-09-16 20:00: "is there a way to show that ANY ring that doubly meets all edge
# slots can be snapped down in some way -- something with the DIRECTIONALITY of the meeter tilts, to show a subset
# can always be reduced to simple").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF; the k5 frontier, A238, A241
and A244's search are running -- never touch them).  Pages to docs/residue_map/campaigns/A245-snap-down/.
Read first: attempts/A243-reach-root/notes/wall_slot243.md (Lemma WALL-SLOT [T], SLOT-MET [S], the 12 border cells;
the mutual wall-grain supply below 4: adjacent corners' wall slots overlap, so the two wall meeters of one wall
serve each other's slot iff h > s-2-delta, h' > s-2-delta', h + h' <= s - delta - delta'), two_grains.md (A223: the
click -- joint grain rotation toward alignment, LEAN-SLIDE [T], the ring's wall grains 2,3,4,5 / 6,7,8,10; the
CROSS-CONTAINER chain formula is not monotone toward alignment (Lambda rises), but note: the ALONG-WALL extent of a
wall toucher is cos + sin, monotone toward flush), realign.md (A231: after a corner swap the anchored shrink lowers
the side on 783/792 witnesses, never blocked; WALL-EXCESS chord form), ring_swap.md (SWAP / cells_swap theorems:
exchange a set X for squares disjoint from the rest at the same side; CORNER-SWAP 2-for-2), cross.md (A240:
PARTNER-TORQUE; locked corners are same-handed 215:11 -- directionality facts measured), torque.md (Lemma W: the
wall torques a tilted toucher toward alignment, sign -chi), no_vv.md (NO-VV-IND), wedged_seal.md, A244's brief and
results if landed (12-stuck candidates; else use the window ring family and A226's rings as the testbed even though
they are not 12-stuck), A222/A223/A231 code (swap, click, anchored shrink).

## The idea, made into lemmas to prove
Directionality = the tilt sense (handedness chi) of each meeter, which by Lemma W is the sense in which the wall
wants to turn it.  Target chain:
1. Lemma STACK (any n, s < 4): in a 12-stuck packing the two wall meeters B (of corner c) and B' (of the adjacent
   corner c' on the same wall) overlap in height (the mutual-service inequalities) and are interior-disjoint, so
   one rests on the other: derive the exact contact geometry -- are they necessarily SAME-handed (parallel edge
   contact like the ring's 2|5) or can they be opposite-handed (a lean)?  Prove the dichotomy and what each case
   forces on the tilts and offsets (use TILT-MIN's sin theta <= delta, DEPTH-BUDGET, WEDGED-SEAL).
2. Lemma WALL-CLICK: for a same-handed wall pair, the JOINT rotation toward flush (common tilt to 0 / 90) is
   feasible -- no collision with the wall, with each other (parallel edges stay parallel), with the corner meeters
   A, A' (the floor / ceiling meeters of c, c') and with the interior squares (the pocket is nearly empty: WALL-SLOT +
   capacity) -- and it SHORTENS the wall's occupied extent (each square's along-wall extent cos + sin is monotone
   toward flush), so the packing after the click is a packing at no larger side.  Say exactly where feasibility can
   fail (A or A' in the way; an interior square touching the pair) and what handedness says about it.
3. Lemma REDUCE: after the click the pair is two flush squares on the wall at offsets; show a subset then reduces
   to SIMPLE squares: either translate the lower one into the corner slot (needs A out of the corner box: exchange
   A by SWAP for a square placed in the vacated room -- the room the click freed is >= the pair's extent loss) or
   exchange {A, B, B'} for the corner domino BL00 + BL01 plus one leftover (3-for-3 SWAP: the leftover fits in the
   union of the three minus the domino plus the freed room); conclude a k >= 1 (or k2) packing at no larger side,
   so the 12-stuck ring was not optimal / is not k0's minimiser.  Where the opposite-handed case of STACK occurs,
   do the same with the lean (A223 LEAN-SLIDE) or show it cannot be 12-stuck.
4. TEST every lemma on: A244's 12-stuck candidates if any exist by the time you run (results/twelve244.jsonl), the
   window ring family and A226's rings (not 12-stuck, but the click / reduce choreography can be exercised on their
   wall pairs), the 193 four-crowds' wall pairs (STACK's dichotomy: same- vs opposite-handed, contact type).
5. Say plainly what is proved [T], what the click's feasibility needs [C], and whether STACK + WALL-CLICK + REDUCE
   gives STUCK-4(11) below 4 (or below s-hat) for 12-stuck packings -- and the n-general form (the along-wall
   monotonicity and the click are n-free; the mutual-service geometry needs s < ceil(sqrt n)?).
6. Deliverables: docs/proofs/snap_down.md, Statements/Open/SnapDown.lean (proved lemmas as theorems where the
   packing predicate allows, else documented axioms; the consequence chain; build + audit, 0 sorry), code/,
   results/snapdown245.md (+jsonl), pages (STACK's two cases drawn; the click frames on a wall pair; the reduce),
   registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
