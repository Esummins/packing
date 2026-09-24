# A279 part 2 -- what (NEST) forces on the four squares  [T], and the candidate landing cells

Notation of part 1.  D has bottom vertex (d_b, h_v) (h_v = h_v(D) is the height of D's lowest point), left vertex
(h_u(D), h_v + cos th_D), tilt th_D in (0, 90 deg); edges of slope angle th_D (lower-right, upper-left) and
th_D + 90 (lower-left, upper-right).  Y as in part 1 (bottom (b, 0), tilt a, left vertex x_L = b - sin a >= 1).

**2.1 [T] Separator arcs are made of edges and bitangents.**  For disjoint convex polygons the arc of separating
directions (A278 part 2 (iii)) is bounded by lines through a vertex of each; an edge line of one polygon is a
separator iff the other polygon lies beyond it.  So eta_+ >= th_D whenever D's lower-right edge line has Y beyond
it, and alpha_- <= th_D whenever D's upper-left edge line has C beyond it (the two lines are parallel).
**2.2 [T] In (NEST) not both of D's parallel edges separate.**  eta_+ < alpha_- with 2.1: if Y is beyond D's
lower-right edge line then C is NOT beyond D's upper-left edge line -- C has a point strictly below-right of the
line through D's upper-left edge, and being upper-left of D (FLOAT-SLOPE) that point is LEFT of D's left vertex:
C sticks out to the left of D below the extension of D's upper-left edge.  Symmetrically if C is beyond the
upper-left edge line then Y is not beyond the lower-right one: Y pokes up past the extension of D's lower-right
edge, right of D's right vertex.  At least one of the two "clean edge separations" fails.
**2.3 [T] Y's top under D's lower-right edge forces D high.**  If Y's top vertex (height cos a + sin a >= 1) lies
under D's lower-right edge at parameter lambda in (0, 1]: cos a + sin a <= h_v + lambda sin th_D, so
      h_v(D) >= 1 - sin th_D          (D's lowest point is within sin th_D of height 1),
and D meets (0,1)^2 (open_box_tilted: h_u cos th + h_v sin th < cos th + sin th - sin th cos th) then needs
h_u(D) < 1 - sin th_D + sin th_D tan th_D: D's left vertex is left of 1 by at least sin th_D (1 - tan th_D).
With x_T(Y) = x_L + cos a >= 1 + cos a on D's lower-right edge: h_u(D) + sin th_D + lambda cos th_D >= 1 + cos a,
compatible with the bound above for every th_D (cos a < sec th_D): the top-vertex poke is consistent with Y
missing B.  [T] the flat floor cells fail iff x_L(Y) < 1 + sup I(C) (A278 part 4 (F1)-(F2) made explicit).
**2.4 [T] X's poke.**  int X meets int T_u(C) and misses int C, so X has a point in the STRIP S_u(C) = T_u(C) \ C
(horizontal width h_u(C), alongside C's two left edges); X a wall toucher missing B puts that point at height >= 1
(X subset {y >= 1}); by BLOCKER-SIDE (mirror) no X -> C separator is horizontal (m_u = 0 would put X within h_u(C)
of the wall).  Consequence: X's LOWEST vertex (sin phi_X, y_X - cos phi_X) lies in S_u(C) or X's lower edges cross
the strip -- either way X_low = y_X - cos phi_X < top(C) < 1 + sqrt2, and X's lower-right edge (angle phi_X) or
C's upper-left edge (angle th_C) bounds the xi arc: xi_- <= min(phi_X, th_C) when both lines separate (2.1).
**2.5 [T] Family-stuck at BL in FLOAT2** (FAMILY-STUCK, family250.md s.1.1; P1+ with Pi = {B, c01}, {B, c10}):
c01 = [0,1] x [1,2] and c10 = [1,2] x [0,1] each need a meeter outside {C, D}.  In the 4-square model these are X
(X meets c01 iff its lowest point is below 2: X_low in [1, 2)) and Y (x_L(Y) < 2).  {B, c01, c10} needs 4 meeters:
{C, D, X, Y} exactly in the model -- so C, D both meet c01 or c10 as well (C at the wall meets c01; D meets c10).

**2.6 Candidate landing cells (all wall-touching, so P1 = CELLS |Pi| = 1 applies; SHADOW-CELL for L):**
 (a) FLAT floor cell F_x, x in [sup I(C), x_L(Y) - 1], meeting D: fails in NEST (x_L(Y) ~ 1)  [T, 2.3].
 (b) SWEEP cells (D's own pose slid at psi in [alpha, eta]): empty by (NEST)  [T, A278 part 6].
 (c) N_Y := Y - sec a . e_x, Y's LEFT NORMAL CELL (normal_ring.md (E1)): touches the floor, interior-disjoint
     from Y, x-extent [x_L - sec a, b - sin a tan a]; inside the container iff x_L(Y) >= sec a.  It is met by D
     when Y's top is under D (D's lower edges continue left over N_Y's top region).  It lands D iff C, X miss it.
     For flat-ish Y, N_Y ~ F_{x_L - 1}, which C meets when x_L ~ 1: N_Y is the flat cell in disguise there.
 (d) N_X := X - sec phi_X . e_y, X's LOWER NORMAL CELL: touches the wall; inside the container iff
     X_low >= sec phi_X.  Met by C (C sits at the wall under X); lands C iff D, Y miss it (Y does: Y is right
     of x = 1 and N_X left of x = 1 + sin phi_X... only if N_X's right vertex is left of Y -- check per case).
 (e) Tilted floor cells hugging C's lower-right edge (tilt th_C) or Y's lower-left edge (tilt a, = N_Y), and
     tilted wall cells hugging X's lower-right edge (tilt phi_X, = N_X) or D's upper-left edge (tilt th_D).
The search nest279 (part 3) says which of (c)-(e) is the free one at the NEST end, and with what margin.
