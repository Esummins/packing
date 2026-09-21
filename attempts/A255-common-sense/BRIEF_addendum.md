# A255 addendum (PI, 2026-09-20 evening) -- the guard on "reducible" was TOO STRICT; Lemma SLIDE-NORMAL

## Correction to the brief's guard
The brief said tilt settling / sliding is not a reduction "unless proved side-non-increasing".  Wrong reason: a
motion of squares INSIDE THE FIXED CONTAINER keeps the side by definition.  For the value form the only requirement
is FEASIBILITY (collision-free path, or even just a valid end packing): if a k0 / family-stuck packing P at side s
can be moved to a packing P' at the same side s, then either P' is not family-stuck (so CELLS gives a k >= 1 packing
at side s -- covered by the other classes) or P' is family-stuck and in NORMAL FORM.  Either way WLOG normal form.
So "reducible" = CELLS exchange OR any feasible fixed-container motion (single-square slides, a grain's common
slide, the bare ring's settling of A253).  Caveats to state exactly: (i) the uniqueness form at s = s-hat needs
the end packing's class handled (Trump is swap-rigid for |Y| <= 3; say what a motion ending AT Trump means);
(ii) iterated normalisation must terminate -- give the potential (e.g. sum of heights above the wall + sense
deviations) or normalise in one step; (iii) a normalising motion may strip another cell of its meeter -- that is
the "not family-stuck" horn, fine, but say so.

## The PI's lemma (state, test on the corpus, prove or find the witness)
"A tilted square s1 sits on the bottom wall; left of it we do not care; the unit cell s1 occupies needs a second
meeter C.  C could sit further away, with a gap, or at a non-common tilt -- but whatever we pick, it can be slid
without obstruction to match s1's tilt and touch the wall (adjacent to s1).  If C deviates too far it cannot leave
room for the NEXT cell's second meeter and the chain breaks.  For the slide to be blocked it cannot be from below;
it would take a square ABOVE s1, at its tilt, poking down past s1 -- and such a square can never be a second meeter
of the current cell, and may block the next square from serving."
Lemma SLIDE-NORMAL (candidate): in a family-stuck packing, for a wall toucher s1 and its cell c, choose the second
meeter C of c minimal in a stated order (lowest, then nearest); then C slides feasibly to the wall toucher of
s1's sense adjacent to s1, unless a blocker D exists; classify D: (a) D itself meets c => D precedes C in the
order, contradiction; (b) D is the next wall square => C's target overlaps the next cell -- the ring's mutual
service (m = 4: C IS the facing corner's toucher, already normal); (c) D above s1 poking down past it => show D
cannot meet c and kills the next cell's supply (the PI's claim) or draw the witness.  COMMON-SENSE then follows
from SLIDE-NORMAL by induction along the wall and round the corners.  Where does the CW poker (type-F corner) sit
in this classification -- is the poker C with s1 FLAT (sense 0, so any sense "matches")?
In the local search, ADD to the counter-hypothesis "C is blocked from the normalising slide" -- it shrinks the
feasible set.  Corpus test: for every wall toucher and its cell's second meeter in the 488 + 486 + rings, is the
slide feasible (straight-line / two-phase path check), and if not, which blocker type?
