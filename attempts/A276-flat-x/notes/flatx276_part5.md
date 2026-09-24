# A276 part 5 -- phi > 0, q_y > C_top: cases (beta), (gamma), (delta) are dead in the corner  [T]
Corner: 0 < th <= 5 deg, 0 < phi <= 5 deg (so tan th, sin phi <= 0.0875, w_phi - 1 >= 0.95 sin phi, h_u + s <= 1.09).
Two chord tools (right end of a chord on the edge V W_R, i.e. W_R above the height):
  (T-chord) if W_R is above C_top: x_min + 1/sin om + (C_top - y_WL) cot om <= T_x  (< 2);
  (L-chord) if V_y < L_h <= W_R_y: x_min + 1/sin om + (L_h - y_WL) cot om < l_C(L_h) = h_u;
(from V_x = x_min + sin om, sin om + cos om cot om = 1/sin om).  V is below C_top; by LEFT: V_x < l_C(V_y), so if
V_x >= h_u then V_y >= L_h - (h_u + s - V_x)... in particular V_x >= h_u + s forces V_y >= L_h and V above C's
upper-left line: C_top - V_y <= (T_x - V_x) tan th.

## 5.1 (gamma): y_WL in [X_low, C_top), delta_L := C_top - y_WL in (0, D].  Dead.
W_L is in the cap, x_min >= r_X(y_WL) >= sin phi.  If W_R is above C_top the T-chord gives 1/sin om < 2: om > 30.
If W_R is below C_top, W_R_x = x_min + sin om + cos om >= x_min + 1 > h_u, so W_R is above C's upper-left line:
delta_L + cos om - sin om = C_top - W_R_y <= tan th, whence cos om - sin om <= 0.0875 and om >= 41.4.  So om >= 30.
Pin (R): Q's top is at y_WL + sin om >= X_low + 0.5 > X_low* (regime I or II), so the chord at X_low* exists with
left end on the edge W_L W_T: x_min + (X_low* - y_WL) cot om >= w_phi, and X_low* - y_WL = sin phi - D + delta_L
<= sin phi, so x_min >= w_phi - sin phi cot 30 >= cos phi - 0.732 sin phi >= 0.932.  Then V_x >= 0.932 + 0.5 >
h_u + s, so V is above C's upper-left line: cos om <= delta_L + cos om = C_top - V_y <= (T_x - V_x) tan th <=
(1.996 - 1.432) 0.0875 < 0.05: om > 87.1, and (R) again gives x_min >= w_phi - 0.05 sin phi > 1.  Now W_R is above
C_top (W_R_y = V_y + sin om > C_top - 0.05 + 0.998) and Lemma A's step (2.1)-(ii) (x_min >= 1, chord at C_top)
gives d_V <= cos om, i.e. y_WL >= C_top -- against (gamma).  ∎

## 5.2 (delta): y_WL < X_low.  Dead.
q_y = y_WL + (sin om - cos om)/2 > C_top > y_WL forces om > 45, and W_R_y = y_WL + sin om - cos om > C_top.  Pin (R)
at X_low* (chord exists: X_low* - y_WL < (sin om - cos om)/2 - D + sin phi < sin om): x_min >= w_phi -
(X_low* - y_WL) cot om >= w_phi - (cos om - cos^2 om / sin om)/2 - sin phi >= cos phi - 1/8 >= 0.87 (t - t^2 <= 1/4).
So V_x = x_min + sin om >= 1.58 > h_u + s: V is above C's upper-left line, C_top - V_y <= (T_x - V_x) tan th.  With
V_y = y_WL - cos om and y_WL <= X_low* - (w_phi - x_min) tan om (pin (R) again), V_x = x_min + sin om:
   cos om + (w_phi - x_min) tan om + sin om tan th <= (T_x - x_min) tan th + sin phi - D.                 (5.1)
x_min < 1 here (x_min >= 1 with the chord at C_top and W_R above C_top would give y_WL >= C_top by (2.1)-(ii)), so
(w_phi - x_min)(tan om - tan th) >= (w_phi - 1)(tan om - tan th) and (5.1) becomes, with T_x < 1 + c,
   cos om + (w_phi - 1) tan om + (sin om - c) tan th < sin phi - D.                                       (5.2)
 phi > th: (D-low) D > (c - sin phi) tan th, so RHS < sin phi - (c - sin phi) tan th, and moving the tan th terms:
   cos om + (w_phi - 1) tan om < sin phi + (2 sin phi - sin om) tan th < sin phi.  But cos om + (w_phi - 1) tan om
   >= 2 ((w_phi - 1) sin om)^{1/2} >= 1.68 (0.95 sin phi)^{1/2} > sin phi.  ✗
 phi <= th: (D-low) D > (c - sin phi) tan phi, RHS < sin phi (w_phi - c) / cos phi <= 1.01 phi^2 (as w_phi - c <=
   phi + th^2/2 <= 1.01 phi... for phi <= th: w_phi - c <= sin phi + (1 - c) <= 1.05 sin phi).  Write eps := cos om.
   Since sin om >= 0.707: eps + (w_phi - 1) tan om < 1.01 phi^2 + 0.293 tan th <= 0.034, so eps < 0.034 and
   sin om - c = (1 - eps^2)^{1/2} - c >= (1 - c) - 0.51 eps^2 > 0 (1 - c = 2 sin^2(th/2) and eps < 0.034 <
   (2 (1 - c)/0.51)^{1/2} fails only if th < 0.034 (0.51/2)^{1/2}... -- handle: if th >= 2 deg then 1 - c >= 0.00061 >
   0.51 eps^2 = 0.00059 ✓; if th < 2 deg then 0.293 tan th < 0.0103, eps < 0.0103 + 1.01 phi^2 <= 0.0115 and
   0.51 eps^2 < 6.8e-5 < 1 - c = 2 sin^2(th/2) needs th > 0.67 deg; if th <= 0.67 deg: eps < 1.01 phi^2 + 0.0034 <=
   0.0035, 0.51 eps^2 < 6.3e-6 < 1 - c needs th > 0.2 deg; iterate once more: th <= 0.2: eps < 0.00103 + 1.01 phi^2
   <= 0.00104, 0.51 eps^2 < 5.6e-7 < 1 - c for th > 0.06 deg -- the sliver th <= 0.06 deg, phi <= th is left to
   the direct bound below).  With sin om - c > 0 every term of (5.2)'s LHS is positive, so (w_phi - 1) tan om <
   1.01 phi^2, tan om < 1.07 phi < 0.1, om < 6 deg -- against om > 45.  ✗
   Direct bound for the sliver (th <= 0.06 deg, phi <= th): (5.2) gives cos om + (w_phi - 1) tan om < 1.01 phi^2 +
   0.293 tan th <= 0.0011, so cos om < 0.0011 and tan om > 900, (w_phi - 1) tan om > 0.95 sin phi 900 > 1.01 phi^2
   (i.e. 855 > 1.07 phi) -- but the sum must be < 0.0011. ✗
∎

## 5.3 (beta): regime I (D <= sin phi), y_WL in [C_top, X_low*), u := y_WL - C_top in [0, sin phi - D).  Dead.
d_V = cos om - u.  W_L is right of X's lower-right edge: x_min >= sin phi + (D + u) cot phi.
(i) W_R above C_top.  T-chord: x_min + (1 - u cos om)/sin om <= T_x < 2 with u < sin phi gives sin om > 0.456, om >
27.  Pin (R): x_min + (sin phi - D - u) cot om >= w_phi.  If V_x = x_min + sin om >= h_u: V above C's upper-left
line, cos om - u <= (T_x - V_x) tan th <= (T_x - w_phi + sin phi cot om - sin om) tan th <= (1 + 1.96 sin phi) tan th
<= 0.103, so cos om <= 0.19, om >= 79, cot om <= 0.2, and (R) gives x_min >= w_phi - 0.2 sin phi > 1: Lemma A
(x_min >= 1, chord at C_top) -- dead.  If V_x < h_u: x_min < h_u - sin om < 0.546 and (R) needs cot om >=
(w_phi - 0.546)/sin phi >= 5.2, om <= 11 -- against om > 27.  ✗
(ii) W_R below C_top: sin om < cos om - u, om < 45; W_R_x >= x_min + 1 > h_u so W_R is above C's upper-left line:
cos om - u - sin om <= tan th, cos om - sin om <= 0.175, om >= 38.  V_y = C_top - cos om + u < L_h (cos om - u >
0.7 - 0.09 > s), so LEFT at V: x_min + sin om < h_u + s, x_min < 0.48; (R): cot om >= (w_phi - 0.48)/sin phi >= 5.9
-- against om >= 38 (cot <= 1.28).  ✗   ∎
