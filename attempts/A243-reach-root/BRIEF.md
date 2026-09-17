# A243 -- re-root STUCK-4(11) on the four corners' REACH SUMMARY (A242's recommendation, 2026-09-16 17:00).
Fable (design + soundness first; the cascade code second).  LAUNCH-AND-EXIT. Ops: short responses, files <= 250
lines, no monitors or waiting turns (the cascade runs detached, per-cell commits, resume block, a logs/STOP file),
explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes (BelowNormal, affinity 0xFFFF; the
k5 frontier workers / loop, A238's sweep and A241's parametric campaign are running -- never touch them), frozen
verifiers untouched (own verifier clause), read-only libraries wrapped.
Read first: attempts/A242-crowd-root/{notes/crowd242.md, results/crowd242.md} (the product law: with 8 pose boxes
branched by widest role, roles with non-empty core are 0/3/6 at depth 0/6/12, all eight must reach A60 scale at
once -> ~1.7e17 cells; every survivor's pocket is the whole centre box; L1 killed nothing; Lemma BOX-GORDAN; the
escalated question [Q]: no lab theorem extends FJ infeasibility from a point to a box; the recommendation: branch
on the corners' REACH SUMMARY, ~1e8 cells, A239's inequality as the leaf, capacity as a coordinate; Stuck4.lean),
A239's notes/rings_below_4.md (the reach inequality R(theta, delta) = cos + sin + delta - (delta - sin) tan >= s - 2
for a flat + tilted crowd to span a wall in contact; GEAR-RATIO; LEVER: torque balance of the tilted meeter needs
delta = sin theta + cos^3 theta; a torque-balanced contact ring needs s > 4; WEDGED-SEAL), local_lock.md (A233:
Psi-minimal optimum => every meeter locked; RADIAL / CHAIN: a locked corner's loaded component reaches a far
wall), pocket_waste.md (TILT-MIN binds upward: sin theta <= delta, DEPTH-BUDGET d_A + d_B <= 1; PIERCE), k0_count.md
(PUSH, HOLD), wall_torque.md (TWO-CONTACT), corner_seal.md, sideband.md (B0/B0'), A185 / A211 cell machinery.

## The design question
A242's tree branches on 24 pose coordinates and its leaf (no-room over cores) only fires when every core is
sharp -- the product law.  A243 branches on WHAT THE LEAVES READ: per corner c, a low-dimensional SUMMARY of its
crowd -- e.g. for the floor meeter its offset delta_f and tilt theta_f, for the wall meeter delta_w, theta_w (with
TILT-MIN's sin theta <= delta and DEPTH-BUDGET as the domain), so 4 corners x 4 = 16 bounded coordinates, or fewer
if the leaf needs fewer (the along-wall REACH of each crowd toward each of its two walls, 8 numbers, and the depth
each meeter intrudes toward the centre, 8 numbers).  The leaves are then CLOSED-FORM inequalities in the summary:
  R1 REACH: on each wall, the two crowds' reaches plus the free squares that could bridge the gap must span the
     wall (a corner meeter without an along-wall holder is not locked: HOLD + CHAIN; the bridging squares are
     bounded by the pocket capacity between the crowds) -- A239's inequality with k bridging squares allowed;
  R2 LEVER / GEAR: the locked crowd's torque balance (A239 s.3) as an inequality in (theta, delta);
  R3 CAPACITY: the centre pocket left by the eight meeters at their summaries (the polygon is determined by the
     summary up to the boxes) holds < 3 squares -- A237's PIERCE / A189's lane bound on the summary's polygon.
Hypothesis: a LOCKED four-crowd (A233's Psi-minimal optimum), side in [3.82, s-hat] first, then [3.82, 4).  This
proves LOCKED-CROWD-FREE(11) (Stuck4.lean's stuck4_eleven), which with A233's theorems closes k0_00 for the value.

## Task
1. DESIGN: choose the summary coordinates and PROVE the three leaves as inequalities valid for every packing in a
   summary cell (each leaf's soundness from the cited lemmas; where a lemma is only measured, say so and do not use
   it).  State the map from a locked four-crowd to its summary (well-defined, covers the hypothesis; D4 quotient
   only if provably sound for the branching used).  notes/reach243.md.
2. PRICE by construction before building the cascade: the summary domain's volume, the cells' expected count at
   the resolution the leaves need (from A239's curves: how sharp must theta, delta be for R1 / R2 to decide?), and
   the per-cell cost of the closed-form leaves (microseconds) vs R3 (0.1 s).  If the honest price is not within
   ~500 CPU-h, say so and stop at the design + price.
3. If priced within budget: implement (cell format, the three leaves, certificate + verifier clause verify243.py,
   audit sampling), run the first 200 cells detached, report kills by leaf and the measured price to completion.
4. Deliverables: notes/reach243.md (design, soundness, price), code/, results/reach243.md (+jsonl), certs, pages
   docs/residue_map/campaigns/A243-reach-root/ (the summary domain with the leaves' kill regions shaded; a survivor
   cell drawn as a crowd), registry row, LOG entry, ledger s.4 note; Lean: no new axiom unless a leaf needs a prose
   lemma (then Statements/Open/ with docstring; build + audit, 0 sorry).  Report once (<= 15 lines) and EXIT.

## Addendum (PI, 18:00) -- Lemma WALL-SLOT: the wall slots must be doubly met too
"Look at BL00 and BL01: how can we possibly get a second meeter for BL01?  If we cannot, both A and B teleport to
those two slots."  In a teleport-stuck packing every wall slot adjacent to a corner (8 cells: BL01 above the wall
meeter, BL10 beside the floor meeter, ...) must be met by a second square, else its meeter teleports into the slot
(swap_packing, |X| = 1) and then the corner box is singly met and teleports (K0-FREE): a corner domino, k2.  So
STUCK-4 may assume all 12 cells doubly met.  Ring check: BL01 is met by 5 AND 2 (the TL wall meeter reaches down
to 1.85) -- the adjacent corner's wall meeter; below 4 the two wall slots of adjacent corners OVERLAP (s - 2 < 2)
so the two wall meeters can serve each other iff h > s-2-delta, h' > s-2-delta', h + h' <= s - delta - delta'
(feasible iff s < 4).  Leaf: enumerate the possible second meeters (adjacent wall meeter; third wall member --
juts, empties the pocket; interior vertex through the notch; the floor meeter's tip in the notch -- the ring's 4
misses by 0.12); mutual case => walls fully occupied, pocket = centre + notches, capacity <= 2 => 10 < 11.  Say
whether this covers the domain analytically at n = 11 below 4 (a proof of POCKET(11)?) and the exact remaining case.
