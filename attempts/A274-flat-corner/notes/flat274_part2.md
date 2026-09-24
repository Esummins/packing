# A274 part 2 -- R1 is DEAD: exact small-angle H1-H3 witnesses violating (U4) and (U5)  [F as consequences]

`code/witness274.py` (Fractions, rational rotations tan(t/2); H1-H3 by exact SAT on edge normals, reusing
witness273's functions; the ring margins from ringdom271.conditions as floats).  `results/witness274.json`.

 W1 (U4):  h_u 1/2, h_v 997/1000, tan(theta/2) = 1/229 (theta 0.500 deg), D = 1/100, tan(phi/2) = 11/252
           (phi 4.997 deg), A: x_min 97/100, tan(alpha/2) = 1/286 (alpha 0.40 deg), side 3.85.
           All 13 exact H1-H3 tests hold.  U4 = -0.2985 (rho(C_top) = 1.30 > 1), U3 +0.044, U5 +0.006, U6 +0.50,
           U8 +0.37.  Mechanism: l_C(C_top) = h_u + c is C's TOP VERTEX while r_X(C_top) = sin phi + D cot phi =
           0.20; the room at the single height C_top is 1.3 although 0.005 lower it is < 1 (cot theta = 115).
 W2 (U5):  h_u 1/5, h_v 99/100, theta = 0 exactly, D = 1/200, phi 4.997 deg, A: x_min 19/20, tan(alpha/2) = 7/15
           (alpha 50.0 deg), side 3.85.  All H1-H3 tests hold.  U5 = cos phi - 1 = -0.0038 (a_R - a* = cos phi +
           sin phi - 1, sin beta+ = sin phi).  U5 fails only in the sliver theta <~ phi^2/2 (0.22 deg at 5 deg).

So (U4) fails on a large part of the corner and (U5) on a sliver: A267's proof cannot be applied verbatim, and
R1 is closed NEGATIVE.  (U8) holds on the whole corner [T] (A271: 1.82 - w(5 deg) = 0.737 > 0.707); (U6) can fail
only for h_u >= 1 - c + cos phi >= 0.996 (not checked further: R1 is dead anyway).

Side fact found while building A [T, elementary]: with C's tilt theta, a floor toucher A sharing the open box with C
must lie below a positive-slope line touching C at B (slope <= tan theta) or at R (slope >= tan theta).
B-line: alpha <= theta and h_v >= cos alpha - tan theta (x_min - u) -- the "h_v -> 1" family (1 - h_v = O(theta)).
R-line: cos alpha (h_v + s - cos alpha) >= (h_u + s + c - x_min) sin alpha, whose left side is <= 0.30 sin alpha
for h_v + s <= 1.01, so h_u <~ 0.30 + O(theta).  At theta = 0 exactly the B-line case is empty (A flat overlaps C).
Not needed for STRIP_2 (h_v-invariant, A273 s.2.1); recorded for the ring question (part 6).
