# A276 part 4 -- phi > 0: the setting, the three pins, Lemma A* (the clearance lemma, phi-free)  [T]

X tilted by phi in (0, 45 deg): B_X = (sin phi, X_low), R_X = (w_phi, X_low*) with w_phi := cos phi + sin phi,
X_low* := X_low + sin phi; X's right boundary r_X(y) = sin phi + (y - X_low) cot phi on [X_low, X_low*] (the
lower-right edge, a nearly horizontal LINE for small phi) and w_phi - (y - X_low*) tan phi on [X_low*, X_top].
D := C_top - X_low > 0 (H2).  Q, V, om, W_L = (x_min, y_WL), W_R, cap, d_V, d as in part 2.  Corner: th, phi <= 5 deg
unless said otherwise; every inequality below is stated with the range it needs.

## 4.1 What is [T] for all phi (A272 s.2-3, ring_domain.md)
(P0) q_y > L_h.  (P1) LEFT: Q ∩ {h_v < y < C_top} ⊂ {x < l_C(y)}, closure at C_top: chord ⊂ [.., T_x]; no point of Q at
height <= h_v.  (P2) ONE-SIDE + NO-LEFT: Q's chords at heights in [X_low, X_top] are all right of X unless Q is in
case A1-left (q_y < X_low, chords left of X), which needs th >= 11.7 deg (A272 s.3) -- dead in the corner; C-left is
dead by Lemma CL.  So in the corner  **Q ∩ {X_low <= y <= X_top} ⊂ {x >= r_X(y)}**  (4.1)  whenever q_y >= X_low, and
also when q_y < X_low and Q is right of X.  (D-low): D > (c - sin phi) tan(min(th, phi))  (X meets int T_u).
(D-high): D <= s + sin phi - (w_phi - h_u) tan th if T_x > w_phi, else D <= (h_u + c - sin phi) tan phi.
T_u ⊂ {x <= r_Tu(y)} ∩ {x >= l_Tu(y)} ∩ {y <= C_top}, r_Tu(y) = c + (C_top - y) tan th, l_Tu(y) = c - (C_top - y) cot th
(for y in [L_h, C_top]).  S's top part is T_u's top corner at T' = (c, C_top): at depth d < h_u s c it is the whole
T_u chord [c - d cot th, c + d tan th].

## 4.2 The three pins
(R) R_X: by (4.1) at height X_low*, if Q has a chord there it lies in [w_phi, oo), w_phi > 1.
(T) T = (T_x, C_top): LEFT at C_top -- Q's chord at C_top lies in [r_X(C_top), T_x] (r_X part only if C_top <= X_top).
(L) L = (h_u, L_h): LEFT at heights below C_top -- Q's chord at height y in (h_v, C_top) lies in [0, l_C(y)),
    l_C(y) <= h_u + s for y <= L_h and l_C(y) = T_x - (C_top - y) cot th for y in [L_h, C_top].
Two regimes: (I) D <= sin phi (R_X at or above C_top);  (II) D > sin phi (R_X below C_top).

## 4.3 Lemma A* (clearance)  [T]
*Assume q_y > C_top, LEFT, th <= 45 deg, and that Q's left boundary at height C_top is on the edge V W_L (i.e.
y_WL >= C_top) with x_L(C_top) >= x0 >= 1.  Then every point of the cap satisfies*
    x - r_Tu(y) >= x0 - c - (T_x - x0) sin om cos om (tan th - tan om)^+ >= 1 - c - w0 tan^2 th / 4 > 0,
*so Q ∩ T_u = ∅.*   (w0 = T_x - 1 = h_u + c - 1 < c;  1 - c = tan^2 th c^2/(1 + c) and c^2/(1 + c) > 1/4.)
Proof.  (i) W_R is above C_top: otherwise sin om < d_V <= cos om (W_L above C_top), so cos om > 0.707 and W_R_x =
V_x + cos om >= x0 + cos om >= 1.707 > T_x at a height below C_top, against LEFT.  (ii) The chord at C_top has right
end V_x + d_V cot om <= T_x and V_x = x_L(C_top) + d_V tan om >= x0 + d_V tan om, so d_V (tan om + cot om) <= T_x - x0:
d_V <= (T_x - x0) sin om cos om.  (iii) On the cap x_L(d) = x_L(C_top) + d tan om >= x0 + d tan om, hence
x_L(d) - r_Tu(d) >= x0 - c + d (tan om - tan th) >= x0 - c - d_V (tan th - tan om)^+, and sin om cos om (tan th -
tan om)^+ <= max_om sin om cos om (tan th - tan om) = tan^2 th / 4 (the max of t (tan th - t) at t = tan th / 2).  ∎
Lemma A of part 2 is the case x0 = 1 with the sharper constant.  Lemma A* needs nothing about X or phi: only
where Q's left boundary is at height C_top.

## 4.4 How (R) feeds Lemma A*
(a) Regime I, y_WL >= X_low*: Q's chord at X_low* exists (Q's top is > C_top + 1/2 > X_low*) and its left end is
    on V W_L, >= w_phi by (R); going down the edge V W_L moves right: x_L(C_top) >= w_phi + (X_low* - C_top) tan om
    >= 1.  Lemma A* with x0 = w_phi: dead.
(b) Regime II, y_WL >= C_top: the chord at C_top has left end on V W_L, >= r_X(C_top) = w_phi - (D - sin phi) tan phi
    (X's right edge), which is >= 1 iff D <= sin phi + (w_phi - 1) cot phi = sin phi + cos phi (1 - tan(phi/2)), true
    since D < 1 <= that for phi <= 45 deg.  Lemma A* with x0 = r_X(C_top): dead.
So, for q_y > C_top, what remains is **y_WL < C_top** in regime II, and **y_WL < X_low*** in regime I -- and the
centre-low cases A1 (q_y < X_low), A2 (X_low <= q_y <= C_top), which at phi > 0 are not dead by part 3's argument.
Parts 5-6: (beta) regime I, y_WL in [C_top, X_low*); (gamma) y_WL in [X_low, C_top); (delta) y_WL < X_low; A1, A2.
