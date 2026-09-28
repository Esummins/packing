# cost281 part 1 -- setting, the two classes, the per-wall ROLES, exclusive extents (F1 closed forms)

## 1.1 Setting [T]
Window W = [3.82, s-hat], s-hat = 3.877083590022814.  On W every corner box of a non-image packing is doubly met
(K0-FREE'), at most one toucher per wall per box (SAME-WALL), a both-wall toucher is alone (WEDGED-SEAL).  The brief's
two classes classify the PAIR corner (touchers A on the floor, B on the wall; THIRD = PAIR + floaters, same touchers):
  class F : one meeter FLAT (sense 0), the other tilted   -- both flat is ONE-TILTED [T]; the flat is [d, 1+d] x [0,1]
            (or its wall mirror) with 0 < d < 1 (d = 0 is the slot square = simple corner); the tilted partner is a
            POKER (A248: cap below height 1 in (0, d], sin th <= d, TILT-MIN d_B <= (d - sin th) tan th, TOP-2 y_T >= 2).
  class T : both meeters tilted (A249: T-CELLS, T-TIP, T-SLOTS).
JAM / FLOAT2 corners have a floater in place of a toucher; the wall-role bookkeeping below applies to their touchers and
their floaters contribute no wall role (they are counted as pocket squares by CAP-2, A277).  Framing: every line is
ROOM [T] (any packing at side s) unless tagged [T-cond] (optimal packing; conditional on the k >= 1 window rows).

## 1.2 Wall ROLES [T]
Each corner puts one meeter on each of its two walls; per wall a corner contributes a role
  Phi (a flat), Pi (the poker of an F corner: tilted, beside a flat on the OTHER wall), tau (a tilted meeter of a T corner).
So a wall is one of six PAIR TYPES {PhiPhi, PhiPi, PiPi, Phi-tau, Pi-tau, tau-tau}; an F corner is (Phi on one wall,
Pi on the other), a T corner is (tau, tau).  Counting roles: 2#PhiPhi + #PhiPi + #Phi-tau = f = 2#PiPi + #PhiPi + #Pi-tau.
Coordinates: wall x = 0, its START corner c at the origin (floor y = 0), END corner c' at (0, s).  A wall toucher Q of
frame tilt th in (0, 90 deg) has wall vertex L = (0, y_L), and (going round) V = L + (sin th, -cos th), R = V +
(cos th, sin th), T = L + (cos th, sin th); w(th) = cos th + sin th; upper boundary y_up(x) = y_L + x tan th on
[0, cos th], = y_T - (x - cos th) cot th on [cos th, w]; lower boundary y_lo(x) = y_L - x cot th on [0, sin th],
= y_V + (x - sin th) tan th on [sin th, w].

## 1.3 Exclusive extent along a wall [T]
Def.  The exclusive extent E(Q) of a wall toucher Q (from the START corner) is the least y such that every OTHER
wall toucher of the same wall with wall vertex above Q's has all its points at height >= y.
Lemma EXT.  (a) flat Q = [0,1] x [d, 1+d]: E = 1 + d.  (b) tilted Q with wall vertex y_L: E = min(y_L, y_R) =
y_L + min(0, sin th - cos th), i.e. E = y_L when th <= 45 deg and E = y_R = y_L - (cos th - sin th) otherwise.
Proof.  Another toucher Q' above Q has its lowest vertex at abscissa sin th' in [0, 1) <= ... and must lie outside Q;
Q's upper boundary is concave on [0, w] with minimum min(y_L, y_R) at an endpoint, so Q' lies above min(y_L, y_R);
the flat case is y_up = 1 + d.  Sharp: Q' nesting on the low end vertex attains it.  QED
Corollary (poker): for the poker B of an F corner (flat A = [d, 1+d] x [0,1] on the floor), y_L = 1 - d_B + cos th
>= 1 + psi(th), psi(t) := (1 - sin t)/cos t, so E(B) >= 1 + psi(th) (th <= 45) and E(B) >= 1 + psi(th) - cos th +
sin th = 1 + sin th - (1 - sin th)(sec th - 1) ... >= 1 + sin th - ... ; in every case E(B) > 1 (psi(th) > 0 for
th < 90).  The full REACH of B along its wall is y_T >= 1 + psi(th) + sin th >= 2 (TOP-2), but only E(B) is
exclusive: a tilted neighbour may nest under B's high vertex (STACK / the mutual pair), a flat neighbour may not
(FLAT-ABOVE: its bottom >= y_T).
Lemma EXT-tau.  A T-meeter B of frame tilt th and offset d_B (its low vertex at distance d_B from the far wall,
A249's frame) has E = d_B + min(cos th, sin th); with d_B -> 0 this tends to min(cos th, sin th) < 1: a T corner's
wall meeter has NO along-wall exclusive cost bounded below by 1 -- the reason no analogue of TWO-POKERS exists (A249).
