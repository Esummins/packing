# cost281 part 2 -- F1 SIDE: the six wall pair types, closed forms, which are dead on W

Wall x = 0, START corner at 0 with flat / poker / T-meeter as in part 1, END corner at (0, s) with the mirror frame
(END's frame offset d' and tilt th' are A249's: END's wall meeter B' has its low vertex at height s - d' - w(th') and
abscissa cos th', its wall vertex at height s - d' - cos th').  Interior-disjointness of the two wall touchers is the
chord condition  y_lo(B') (x) >= y_up(START's toucher)(x) on the common abscissae (TWO-POKERS' argument, A248 s.3.2).

**PiPi [T, dead on W].**  TWO-POKERS: s >= 2 + psi(th) + psi(th_f) + sin th_f + max(cos th_f tan th, sin th -
(cos th - cos th_f) cot th_f) >= s* = 3.9342370 > s-hat.  (A248; Lean `two_pokers_window`.)

**PhiPi [T].**  Flat A = [0,1] x [d, 1+d] at START, poker B' at END (beside END's flat on the ceiling).  B''s low vertex
(cos th_f, y_T') has y_T' <= s - 1 - psi(th_f) - sin th_f (A248 mirrored) and, lying at abscissa < 1, must be >= 1 + d:
    SIDE(PhiPi) :  s >= 2 + d + psi(th_f) + sin th_f = 3 + d + (1 - sin th_f)(sec th_f - 1) >= 3 + d.
So a PhiPi wall exists on W iff the flat sits within s - 3 <= 0.877 of its corner (d < s - 3), and FLAT-ABOVE is the
same inequality read from the poker's side (the flat's bottom is >= its top vertex).  The flat NEVER meets the poker's
slot [0,1] x [s-2, s-1] (1 + d <= s - 2); the poker ALWAYS meets the flat's slot [0,1] x [1,2] (y_T' <= s - 2 < 2).

**PhiPhi [T].**  s >= 2 + d + d'; both flats meet each other's slot iff d, d' > s - 3, compatible with d + d' <= s - 2
iff s < 4.  A common-tilt ROW iff d + d' = s - 2 (the flat row [0,1] x [d, d+2], A258 s.3.4).

**Phi-tau [T].**  Flat at START, T-meeter B' at END:  s >= 1 + d + d' + w(th')  (B''s far point above the flat).  B' meets
the flat's slot (ADJ) iff d' + w(th') > s - 2; the flat meets B''s slot iff d > s - 3.  Both together need
s - 3 < d <= s - 1 - d' - w(th') < 1: a nonempty range on W.  No lower bound above 2 + d.

**Pi-tau [T].**  Poker B (tilt th) at START, T-meeter B' at END, a := cos th (B's top abscissa), b := cos th' (B''s low
vertex abscissa).  (i) b <= a:  s - d' - w(th') >= y_L + b tan th >= 1 + psi(th) + cos th' tan th.  (ii) b >= a:
s - d' - w(th') >= y_T - (b - a) cot th  AND  B's top T below B''s right-rising edge: y_T <= y_lo(B')(a) = (s - d' -
w(th')) + (b - a) cot th'.  In both cases  s >= 1 + psi(th) + d' + w(th') + (a non-negative interleave term) with
infimum, over the T-corner poses with d' -> 0 and th -> 0, equal to 3: **no wall bound above s-hat** -- the mixed F/T
wall is realisable at 3.82 (exact witnesses, part 7).  The interleaving (ii) with th' > 45 deg has B and B' of the SAME
global sense, (i) and (ii) with th' < 45 deg of OPPOSITE senses (frame handedness is swapped at END: `two_grains.md`
s.1.4); so "F beside T on a wall" fixes no sense by itself (part 3 says what the SUPPLY of the poker's slot fixes).

**tau-tau [T-computed, A249].**  The mutual type-T pair has sup SAT margin +0.078 at 3.82: realisable on all of W; the
common-tilt rows of two exist on all of W (least side 1 + sec + cos + sin + tan(phi/2) -> 3).

**Summary F1.**  By SIDE alone, exactly ONE wall type is dead on W: PiPi.  The along-wall costs are
  Phi: 1 + d exclusive, and it forces its poker-neighbour's bottom to >= 1 + d (so the poker's END corner is within
  s - 3 of ... i.e. d < s - 3); Pi: exclusive E(B) >= 1 + min(psi(th), 1 - cos th) and reach y_T >= 2; tau: d' +
  min(cos th', sin th') exclusive, reach d' + w(th').  The brief's "F corner and T corner on one wall: is it > s-hat?"
  -- NO [T]: both Phi-tau and Pi-tau have realisations at 3.82 (part 7).  The flat ROW's 3.9347 is the ROW pinwheel's
  least side [M] (A258) and stays [M]; a flat row inside a HYBRID ring is priced in part 7.
