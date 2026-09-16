# A240 -- Theorem CROSS: the PI's X-sketch -- opposing torques at every corner jam force alternating grains around
# the perimeter, and the two bracing chains through the middle cannot both exist (PI, 2026-09-16 12:00).
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF; k5 frontier workers, A238 and
A239 are running -- never touch them).  Pages to docs/residue_map/campaigns/A240-cross/.
Read first: local_lock.md (A233: the residue is GLOBAL, "not all four load paths can end in locks at once"; RADIAL
/ CHAIN / NO-SELF-STRESS: a loaded arm is held in by a net corner-ward push from OUTSIDE, the loaded component of a
crowd reaches a FAR wall; Trump's TL is a locked corner), wall_torque.md (RING: walls + meeters alone never balance;
CORNER-LOAD: the frame handedness of a loaded corner decides floor- vs wall-loaded; TWO-CONTACT; Lemma W: a wall
torques a tilted square toward its alignment, sign -chi), k0_count.md (PUSH, HOLD), torque.md (chi, the gear rule
as the PI stated it: "a square meeting the wall with some torque sign can only be pinned by another square with the
opposite sign, like meshing gears"), handedness.md (A234: no GLOBAL SUM separates; the flush squares are Trump's
torque-neutral reservoir), no_vv.md, two_grains.md (the ring's two grains: LEFT half 2,3,4,5 at 70 deg, RIGHT half
6,7,8,10 at 20 deg -- note its corner pairs 4|5 and 8|10 are SAME-handed and it is held only by the tilt floor),
A217's stress tables (per square chi, W, tau; per corner the meeters), A219's rows219 / A233's cluster code.

## The PI's sketch (a pencil X on paper)
The two diagonals of the container split it into four sectors: LEFT and RIGHT labelled C, TOP and BOTTOM labelled W
(the two torque senses).  "Using C and W to denote different torques, and the fact that corner jams require
opposing torques, we end up with this cross shape, where the left C grain needs to touch the right C grain to
brace against the opposite wall, but that would prevent the W grains from meeting.  So my intuition is that such a
configuration that is globally locked is not possible."
Reading: (i) Lemma OPPOSE -- at a LOCKED open corner (both meeters loaded, held by wall + partner + along-wall
holders only), the floor meeter and the wall meeter have OPPOSITE handedness; (ii) hence around the perimeter each
wall's two meeters share the wall's handedness and the four wall grains alternate C, W, C, W -- the four sectors;
(iii) RING + RADIAL / CHAIN: a wall grain is not balanced by walls and meeters alone; it needs a corner-ward
along-wall force from outside, i.e. a chain through the interior that braces against the OPPOSITE wall (left grain
to right wall, bottom grain to ceiling); (iv) PLANARITY: a chain of squares in contact from the left wall to the
right wall separates the container; a chain from the floor to the ceiling must cross it; squares cannot cross, so
the two chains SHARE a square at the crossing; (v) the shared square would carry both grains -- both torque senses
-- which the gear rule forbids: so at most one pair of opposite grains can be braced, the other pair is not
locked, and the four-crowd is not globally locked.  With A233 (the Psi-minimal optimum has every meeter locked if
it is a four-crowd) this is LOCKED-CROWD-FREE(n), i.e. ONE-FLUSH(n) in value form, for every n.

## Task
1. Lemma OPPOSE: state and prove (any n) from Lemma W + PUSH + HOLD + the torque balance of each meeter (wall torque
   sign -chi must be cancelled by the partner's push and the holder's push; work out the signs for same-handed vs
   opposite-handed pairs; the ring's same-handed corners needed the tilt floor's torque -- is that the general
   fact?).  Test on every witness corner: locked corners (both meeters loaded, tau_bound = 0 at both) vs their
   handedness pair; the crowd witnesses' corners with tilt-floor torque should be the same-handed ones.
2. Alternation (ii) as a corollary; CORNER-LOAD's floor/wall assignment made consistent with it.
3. The bracing chains (iii): from RADIAL / CHAIN, make exact what "braces against the opposite wall" means -- the
   loaded component of the left grain contains a contact path to the right wall (or to the right grain) -- and
   verify on the 193 four-crowds and the 883 free FJ points' locked corners which far wall each loaded component
   reaches (A233 measured: all but 8 clusters leave the arm; where do they END?).
4. Theorem CROSS (iv)+(v): planarity is a Jordan-curve statement about the union of the squares of a contact
   chain; state it exactly (the chain's squares are closed sets in contact, their union is connected and touches
   both walls, so it separates the floor from the ceiling within the container).  Then the SHARED square: what
   forbids it?  Consider (a) a tilted shared square: it receives loaded contacts from a C chain and a W chain --
   apply the gear rule / Lemma W torque signs to show its torque balance fails, or find the case where it holds;
   (b) a FLUSH (axis-aligned) shared square in the interior: torque-neutral, so the gear rule does not bite --
   A234 found flush squares are exactly Trump's torque reservoir; say whether a floating flush square braced by two
   crossing chains can exist in a k0 packing (it is not a simple square unless it sits at a slot) and what that
   case needs -- this is the likely residue; test: do any witnesses have two crossing bracing chains, and what is
   at the crossing (tilted / flush / a vertex-on-edge junction like the ring's square 9)?
5. Say plainly what is proved, what the shared-square case leaves open, and whether CROSS + A233 closes
   LOCKED-CROWD-FREE(n) for all n or reduces it to the flush-crossing case.  Lean: Statements/Open/Cross.lean (OPPOSE
   and CROSS as documented axioms where prose, the consequence chain as theorems; build + audit, 0 sorry).
6. Deliverables: docs/proofs/cross.md, the Lean file, code/, results/cross240.md (+jsonl), pages (the X-sketch
   made exact on the ring and on a witness with crossing chains; the sector labelling; the shared square), registry
   row, LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
