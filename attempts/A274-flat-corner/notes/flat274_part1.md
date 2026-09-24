# A274 part 1 -- OUTLINE: route R1 (ring-domain restricted) at theta, phi <= 5 deg  (2026-09-23)

Notation as strip_jam.md / ring_domain.md: c, s = cos, sin theta; D = C_top - X_low; beta = phi - theta;
a* = 1 - h_u c; r_X(y) X's right boundary; l_C(y) C's left boundary; rho(y) = l_C(y) - r_X(y).
R1 needs (U3), (U4), (U5), (U6), (U8) from H1-H3 + theta, phi <= 5 deg.  First pass, before any computation:

 (U8) X_top > C_top + 1/sqrt2.  [T] A271 s.2: X_top - C_top > 1.82 - w(theta) >= 1.82 - w(5 deg) = 0.7366 > 0.7071.
      TRIVIAL at theta <= 6.5 deg.
 (U6) h_u + c - cos phi < 1.  NOT forced: h_u < 1 is all the box gives at theta -> 0, and h_u in [1 - c + cos phi, 1)
      (a sliver of width <= 1 - cos 5 deg = 0.0038 at theta = 0) violates it.  Needs a witness check.
 (U5) a_R - sin beta+ >= a*.  At theta = 0: a_R - a* = cos phi + sin phi - 1, minus sin beta+ = sin phi gives
      cos phi - 1 < 0 for every phi > 0: FAILS (by O(phi^2), -0.0038 at 5 deg).  The -s D term makes it worse.
 (U4) rho(C_top) < 1.  l_C(C_top) = h_u + c (the top vertex) while r_X(C_top) = sin phi + D cot phi can be ~0.2
      (theta = 0.5 deg, phi = 5 deg, D ~ 0.01 allowed by D-low / D-high): rho ~ h_u + 0.8 > 1 for h_u > 0.2: FAILS
      badly -- but only because rho is evaluated at the single height C_top where C's upper-left edge is nearly flat;
      at C_top - 0.005 the room is already < 1.  A267's proof (s.3.2) uses rho(C_top) < 1 verbatim, so R1 is dead
      as stated; the mechanism survives (a chord of length >= 1 - 2 delta at depth delta below the centre).
 (U3) a_2 - a* > w_max / 2.  Wedge mouth past T_u's top edge by more than half the wedge width; at small angles
      w_max ~ D + O(theta) and a_2 - a* ~ cos phi + sin phi - 1 - s D ~ phi: expected to hold when phi >> D, to
      FAIL when D ~ phi (X flat, D ~ 0.1: a_2 - a* = 0, w_max = D).  Check.
Verdict so far: R1 cannot close the corner (U4, U5 fail as consequences even at small angles) -- confirm with exact
small-angle witnesses (part 2), then R2 (direct slot argument, parts 3+).
