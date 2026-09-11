# PI reading (2026-09-11 12:40), Y0672 leaf R.2.3.1, TL(1,0): the EPSILON-PERTURBED SECOND MEETER
"if I think about a near simple square, you can do an epsilon perturbation to allow a second meeter, but all 4 ways
you can do that (slide x, slide y, CW, CCW) create the second meeter slot near the hard walls of the slot (in this
case next to TL00 and top side). I think as a general rule, in an epsilon perturbed second meeter case, the second
meeter can't be supplied through the outside halves of the sides. In this case, all ways H can be second meeter after
clipping are versions of that, so this leaf should be dead already."

Coordinator's numbers on the leaf: F3 (TL(1,0)) tilt 0-3.6 deg, near-simple, filling the cell to the top wall and the
TL pin; H's corner reaching TL(1,0) sits at (1.87, 2.92), inside F3's cell.  F3 cannot slide up (wall); sliding right
frees the strip next to the pin (outer side, useless for H's corner); CW rotation drops F3's bottom-right end onto the
corner; CCW needs ~6.7 deg to clear it (rise 0.043 at 0.37 from the centre) against F3's 3.6.  => the [H meets TL(1,0)]
branch of Rule NS should be EMPTY after the clip against F3's K'; confirm it exactly and say so on the page.

Candidate Lemma EPS (state, prove, test before any use): if a slot's first meeter lies within eps of the simple pose
(upright, filling the cell), a second meeter's contact with the widened box lies on the INNER halves of the box's
sides (away from the pin / wall corners): each of the four eps-perturbations frees only a gap adjacent to an outer
side, and a unit square entering such a gap reaches depth O(eps) before meeting the pin or the wall.  Caveat for the
statement: the widened box's own pad margin (0.026 outside the cell) lets a square poking a vertex into the margin
from an inner side meet cheaply -- the lemma is about the OUTER halves only.  Test it against the exact H-meets
computation on this leaf; if it holds, it is a stage-0 closed-form rule (A202/A203 style) for every near-simple
named meeter: drop H / role option rows whose only contact with p's box is on an outer half.
