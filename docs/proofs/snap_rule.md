# Rule SNAP (candidate, [C]) -- near-simple squares with no second meeter are exactly simple -- PI, 2026-09-14

Not built; filed for the descending-k sweep (k4 / k3 / k2), where near-simple squares are common and the trees are
deep.  On the k5 pages the exact cascade kills these leaves in seconds, so the rule is not worth its cost there.

**Observation (k5_16 Y0865, leaf R.2.3.1.1.2.2.1.1.1.1x and the depth-6 page under R.2.3.1.5.p1.1.2.2.1.1).**  F1 is
near-simple in BL(1,0) / BR(1,0) (tilt 0.3 deg in [0, 0.6]).  Theorem FC requires the cells it borders to be doubly
met, but a square that is within epsilon of a simple slot admits a second meeter for the corner boxes up-and-left and
down-and-right of it ONLY at the corner point itself: the near-simple square covers the inner corner (Lemma
CORNER-COVER, CC0) and blocks every other approach.  So the square cannot be anything but simple.

**Rule SNAP (candidate, any n).**  At a node where a role's box lies within epsilon of a simple slot and the two
outward corner boxes admit no second meeter except at the corner, the role IS the slot square; the node belongs to
the class with one more simple square (k+1), which is handled by that class's tree -- a reclassification, not a kill.

**Special case SNAP-DIAG (PI, 23:20).**  Several near-simple squares DIAGONAL to each other (Y0865: F1 in BR(1,0),
F4 in BR(0,1), H up-left) whose only possible meeters are at the "points" -- the shared corner where the diagonal
neighbours touch.  Diagonal neighbours meeting only at their common corner point cannot supply each other's second
meeter, so all of them are exactly simple: the node reclassifies to k+2 (or more).

**Obligations.** (i) the epsilon (how near is near: the pad-0 / G1-slab widths 0.0068 / 0.0108 of the k5 pages, or
the role's box extent); (ii) the "only at the corner" test as an exact clip on the two outward corner boxes (the
existing CC / EmptyBox machinery); (iii) the reclassification's soundness across classes (the k+1 tree's hypothesis
must contain the snapped node -- the class trees are stated on simple slots, so a snapped square lands on a slot of
the k+1 tree exactly when the slot lattice agrees; state this).  Related: `forced_corners.md` (FC), `descent.md`
(Lemma CH, CORNER-COVER), `noroom.md`, A211's Rule NS (named-or-anonymous split).
