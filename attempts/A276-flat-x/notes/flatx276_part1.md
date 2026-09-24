# A276 part 1 -- setting at X FLAT (phi = 0) and the exact shape of S near its top  [T]

Notation as A267/A271/A272 (corner frame, C floater: L = (h_u, L_h), T = (h_u + c, C_top), c = cos th, s = sin th,
L_h = h_v + c, C_top = L_h + s; T_u = C - h_u e_x with top vertex T' = (c, C_top); S = T_u \ C).  X FLAT:
X = [0, 1] x [X_low, X_low + 1], D := C_top - X_low.  Theta in (0, 45 deg]; the brief's domain is th <= 5 deg.

## 1.1 The dip window  [T]
(a) X misses int C.  C's upper-left edge is y = L_h + (x - h_u) tan th on x in [h_u, h_u + c].  If h_u + c <= 1, X's
    bottom edge on [0,1] passes at or above T, so X_low >= C_top, D <= 0, and X cannot meet int T_u (subset of
    {y < C_top}): contradiction with H2.  So **h_u + c > 1** and X_low >= y1 := L_h + (1 - h_u) tan th, i.e.
        0 < D <= (h_u + c - 1) tan th =: D_max.                                   (1.1)
    (D > 0 is H2: X meets int T_u only below C_top.)  A272's (D-high) at phi = 0.
(b) T' = (c, C_top) is inside X's closed footprint (c < 1, C_top > X_low): T_u's top vertex is UNDER X.

## 1.2 S at heights in [L_h, C_top]  [T]
S(y) := S ∩ {height y} = { l_Tu(y) <= x < min(l_C(y), r_Tu(y)) } with
    l_Tu(y) = (y - L_h) cot th  (T_u's upper-left edge),  l_C(y) = h_u + (y - L_h) cot th,
    r_Tu(y) = c + (C_top - y) tan th  (T_u's upper-right edge, nearly vertical for small th).
Two exact heights: l_C(y) = 1 at y = y1 (above); r_Tu(y) = 1 at y = y2 := C_top - c tan(th/2) = L_h + tan(th/2)
(since (1 - c) cot th = c tan(th/2) and s - c tan(th/2) = s/(1 + c) = tan(th/2)).
So the part of S RIGHT of the line x = 1 is the triangle
    Sigma := { y1 < y < y2, 1 <= x < r_Tu(y) },   height y2 - y1 = s (h_u (1 + c) - 1) / (c (1 + c)),
    width at height y:  r_Tu(y) - 1 = (C_top - y) tan th - (1 - c) <= tan^2 th (h_u - c/(1 + c)).       (1.2)
Sigma is empty iff h_u <= 1/(1 + c).  Its width is O(th^2), its height O(th).  X covers Sigma ∩ {y >= X_low}.
The part of S LEFT of x = 1 at heights y in (y1, X_low) -- UNDER X -- is the channel piece
    Kappa := { y1 < y < X_low, l_Tu(y) <= x < 1 },   1 - l_Tu(y) >= 1 - c + D cot th >= 1 - c > 0;   (1.3)
its mouth on x = 1 has height eta := X_low - y1 = D_max - D in [0, D_max), D_max < tan th.  Kappa's floor (C's
upper-left edge) rises to the RIGHT at slope tan th; its roof y = X_low is flat; it WIDENS to the left.

## 1.3 The distance from X's bottom-right corner to T_u  [T]
The point (1, C_top) (X's right edge at C's top height) is outside T_u.  T_u's upper-right edge through T' has
direction (s, -c); the foot of the perpendicular from (1, C_top) has parameter (1 - c) s > 0 (on the edge), so
    dist((1, C_top), T_u) = (1 - c) c = 2 c sin^2(th/2)  (T_u convex).                                   (1.4)
For th = 15 deg: 0.0329; 5 deg: 0.00379; 2 deg: 0.000609; 1 deg: 0.000152.  A third of these: 0.0110, 0.00126,
0.000203, 0.0000507 -- compare A272's sup -0.0168 (th 15, three terms with weights 1, 1, c + s) and A274's 0.00190,
0.000306, 0.000078 (phi = 0).  See part 2 for the exact three-term split (1 - c) c / (2 + c + s ...).

## 1.4 What is [T] from A272 that survives at phi = 0
(P0) q_y > L_h.  (P1) LEFT: Q ∩ {h_v < y < C_top} ⊂ {x < l_C(y)}; int Q ∩ int Γ = ∅.  (P2) at phi = 0 the room left
of X is ZERO at every height in (X_low, X_top), so a non-degenerate chord there is right of X:
    **Q ∩ {X_low <= y <= X_top} ⊂ {x >= 1}**  (closure).                                                 (1.5)
(P3) the DROP.  Case A2 (q_y in [X_low, C_top]) is DEAD at phi = 0: the centre chord (length >= 1) lies in
[1, l_C(q_y)) and l_C(q_y) <= l_C(C_top) = h_u + c < 2.  Case C-left dead (room zero).  Live: A1 (q_y < X_low),
M ∪ C-right (q_y > C_top, Q right of X).
