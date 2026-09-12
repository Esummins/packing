# Coordinator note (2026-09-12 01:30) -- PI reading of Y0202-style leaf R.1.1.2.1.2s (2,226 s of wall on a pad ghost)
"TR00 has a near simple square, and the regions around the top and left of the simple unit square, where it meets the
wall, are certifiably dead. Since a square pushed into the corner covers the opposite corner under all rotations, that
should imply that there's no way for TR00 to get a second meeter, and that should have been determinable way before
burning 30+ minutes on the node."

Lemma CORNER-COVER (to state and prove before use; closed form): a unit square touching both walls of a corner
(centre (S0-h, S0-h), h = (cos t + sin t)/2) contains the corner cell's inner corner point (S0-1, S0-1) for every tilt
(offset (h-1, h-1) rotates to |u| = 2h(1-h) <= 1/2, v = 0).  So a second meeter of the corner slot can touch the
WIDENED box only (a) in the two wall wedges between the tilted square and the walls (width <= h(t) - 1/2, i.e. 0.03 at
3.6 deg) -- which needs a centre in cells that stage 0 already killed -- or (b) in the PAD MARGIN outside the cell
at the inner corner (width pi_0 = 0.0068 on the G1 pad), which F3's vertex reaches from the diagonal.  (b) is the only
way the node lives: a pad ghost.  At pad 0 the node is dead at once.

Two changes made / requested:
1. run209.py now runs PAD 0 FIRST (--pads default zero,g1): a pad-0 kill is recorded [s0-only, WINDOW-PENDING] and the
   window run follows; the pad ghosts stop costing an hour each on the window before their instant s0 verdict is known.
   (Workers spawn a fresh python per node, so the change applies from the next node.)
2. Stage-0 rule to add (successor): CORNER-COVER + the wedge bound, so that on the window the survivor is reduced to
   "the second meeter's contact lies in the inner-corner pad margin" and the node goes straight to the slab step
   (largest lambda* for which the kill persists, by bisection on the pad) instead of the full tree.
