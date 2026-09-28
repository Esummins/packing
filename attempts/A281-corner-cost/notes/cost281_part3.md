# cost281 part 3 -- F2 HOLDERS: what an F corner's two slots need, who can supply them, and the sense question

F corner c = BL: flat A = [d, 1+d] x [0,1] on the floor (0 < d < 1), poker B on the wall x = 0 (tilt th, sin th <= d,
wall vertex y_L >= 1 + psi(th), top T = (cos th, y_T), y_T >= 2).  Floor neighbour c' = BR, wall neighbour c'' = TL.
FAMILY-STUCK (Lemma CELLS on the dominoes and the triple, A249 s.3.2) [T, any packing on W]: c01 = [0,1] x [1,2] needs a
meeter outside {A, B}; c10 = [1,2] x [0,1] needs a meeter outside {A, B}; the two are DISTINCT squares (the triple).

**H-F1 [T]  the poker's slot c01.**  A misses c01 (A is in {y <= 1}).  Candidates: (a) TL's wall meeter -- a flat: never
(FLAT-ABOVE, its bottom >= y_T >= 2); a poker: never on W (PiPi dead); a T-meeter B': iff it is ADJ, d' + w(th') > s - 2,
interleaved with B as in part 2 (i)/(ii) or continuing B as a common-tilt ROW (B' = B + sec th e_y, then B''s low vertex
at y_V + sec th < 2 iff y_V < 2 - sec th, compatible with B' meeting TL's box iff y_V > s - 1 - w(th) - sec th; at th =
15 deg, s = 3.82 the range is (0.56, 0.965), nonempty).  (b) A FREE square G in the poker's notch: the wedge below B's
lower-right edge V->R at abscissae x < 1 and heights above ... no: c01 minus B is the region at x < 1 between y = 1 and
B's LOWER boundary (above A only for x > 1 + d, i.e. never at x < 1: A's top is at y = 1 and the wedge starts at y = 1),
i.e. G pokes a vertex under B's edge V->R at x in (x_1, 1), x_1 = sin th + (1 - y_V) cot th <= d, heights in
(1, y_V + (x - sin th) tan th); or above B's edge L->T under the flat / T-meeter of TL through the notch at L.
So on W: **the poker's slot is met by a free square, or by an ADJ T-meeter of the wall neighbour** [T]; the second
option makes TL a T corner whose wall meeter reaches below 2 -- its GLOBAL sense is the poker's own when it is the
poker's row-continuation (same tilt) or an interleaver with frame tilt > 45 deg, the opposite when it interleaves with
frame tilt < 45 deg (part 2).  The brief's "a specific sense" is therefore NOT forced by geometry [T]; part 7 exhibits both.

**H-F2 [T]  the flat's slot c10.**  A meets it (own).  Candidates: BR's floor meeter -- a POKER (BR type F, flat on the right
wall): ALWAYS (its far vertex is at x = s - y_T <= s - 2 < 2, height cos th_f < 1, and x > 1 since y_T <= 1 + sqrt 2 <
s - 1); a FLAT [s-1-d', s-d'] x [0,1]: iff d' > s - 3; a T-meeter: iff ADJ (d' + w > s - 2).  Otherwise a free square.
**H-F3 [T]  no sharing inside the corner.**  The two suppliers are distinct (the triple family); part 7 measures whether one
FREE square can meet both c01 and c10 of an F corner while avoiding A and B (F-SLOTS-ONE; expected impossible: A's
corner (1+d, 1) and B's body leave no corridor of width 1).

**H-F4 [T-prose, normal form; chain link 7]  rows or locks.**  In the lexicographic normal form every wall carries a row of
two, a row of three (side > 4 at common tilt [T]; 3.9814 flat [M]) or a LOCKED open pair (both normal cells met by a
free square that has nowhere else to go, P2 + P2').  For the F corner: the floor is a common-tilt row iff BR's floor
meeter is the adjacent flat [1+d, 2+d] x [0,1] (a FLAT ROW; needs d > s - 3 for the second flat to meet BR's box) --
otherwise the floor is a locked pair and costs one lock, a free square meeting A's normal cell (1+d, 2+d) x (0,1) outside
A and BR's meeter; the wall x = 0 is a row iff TL's wall meeter is B + sec th e_y (a T corner of the poker's sense) --
otherwise a lock, a free square meeting B's normal cell B + sec th e_y outside B and TL's meeter.  The lock of the wall
(Phi_BL, Pi_TL) case: A_BL's normal cell [0,1] x [1+d, 2+d] is met by the poker B_TL (its low vertex is in (1+d, s-2])
and by no meeter of BL (BL's floor poker has top w(g) <= 1 + d since cos g <= d), so a free square must poke its leftmost
vertex into the wedge x < 1, y in (1+d, y_lo(B_TL)(x)) -- the wedge exists (height (1 - cos th_f) cot th_f > 0 at x = 1)
and the free square meets BL01 there.  So in normal form **an F corner costs two free squares (one per wall) minus one
for each of its walls that is a ROW**: a flat row (the neighbour is F with its flat on that wall, d > s - 3) or a poker row
(the neighbour is T, same tilt, same sense).  [T-prose]: the dichotomy is chain link 7; the per-wall cell computations are [T].

**Reading against A248.**  A248 s.3.3 counted the poker's notch only and needed SEPARATE-NOTCHES [M] for f = 4; H-F1/H-F4
add the flat's side of the corner: on W a PhiPi wall (the only wall type an all-F pinwheel can use, part 2) is never a
row, so the all-F pinwheel has FOUR locked walls in normal form; part 6 counts what that costs without any [M].
