# A276 part 6 -- phi > 0: the centre-low cases A1, A2; Theorem CORNER; errata  [T]
Corner as in part 5; q the centre, D(q, 1/2) ⊂ int Q the inscribed disc; its chord at a height within delta < 1/2 of
q_y has half-length rho(delta) := (1/4 - delta^2)^{1/2} centred at q_x.

## 6.1 A2 (X_low <= q_y <= C_top).  Dead.
(a) Upper pin.  If q_y >= X_low*: the centre chord (length >= 1, right of X by (4.1)) has q_x - 1/2 >= r_X(q_y)
>= cos phi only; instead take the disc chord at height X_low* <= q_y: |X_low* - q_y| <= C_top - X_low* =
D - sin phi < D <= s + sin phi <= 0.175 ((D-high)).  If q_y < X_low*: X_low* - q_y <= X_low* - X_low = sin phi <= 0.0875.
Either way the disc's chord at X_low* has half-length >= rho(0.175) = 0.468 and (pin (R)) lies right of w_phi:
q_x >= w_phi + 0.468 >= 1.468.
(b) Lower pin.  The height y' := q_y - 0.45 satisfies h_v < L_h - 0.45 < y' (q_y > L_h) and y' <= C_top - 0.45 < L_h
(s < 0.45), so LEFT there reads x < l_C(y') <= h_u + s <= 1.09; the disc's chord at y' has half-length rho(0.45) =
0.218, so q_x + 0.218 < 1.09, q_x < 0.872.  (a) and (b) contradict.  ∎

## 6.2 A1 (L_h < q_y < X_low), Q right of X (A1-left needs th >= 11.7 deg, A272 s.3).  Dead.
Let delta := X_low* - q_y > 0 and eta := X_low - y1 = D_max - D where y1 = L_h + (1 - h_u) tan th, D_max =
w0 tan th (exact identities; (1, y1) ∉ int X since it is on C's boundary, but only D > 0 is used).  The centre chord
⊃ [q_x - 1/2, q_x + 1/2] lies in [0, l_C(q_y)) with l_C(q_y) = 1 + (q_y - y1) cot th (q_y > L_h), so
   q_y - y1 > (q_x - 1/2) tan th,   and   delta = eta + sin phi - (q_y - y1) < w0 tan th - D + sin phi - (q_x - 1/2) tan th.
If delta >= 1/2 the disc misses X_low*; but delta < tan th + sin phi <= 0.175 < 1/2 (w0 < 1, q_x >= 1/2), so the
disc chord at X_low* exists, is right of w_phi (pin (R)), and q_x >= w_phi + rho(delta).  Feeding q_x back:
   delta < (w0 - w_phi + 1/2 - rho(delta)) tan th + sin phi - D < (1/2 - rho(delta)) tan th + sin phi   (w0 < 1 < w_phi),
and since rho(delta) >= rho(0.175) = 0.468: delta < 0.032 tan th + sin phi =: delta_0 <= 0.0900, rho(delta) >= rho(delta_0).
Finally q_x + 1/2 < l_C(q_y) <= l_C(X_low) = 1 + eta cot th = 1 + w0 - D cot th < 1 + w0 < 1 + c, so
   w_phi - 1 + 1/2 + rho(delta_0) < c,  i.e.  (cos phi + sin phi - 1) + 1/2 + (1/4 - (0.032 tan th + sin phi)^2)^{1/2} < cos th.
On the corner the left side minus the right side is >= 0.25 th^2 (1 - o(1)) + phi (1 - th - 1.6 phi) > 0: at (5, 5)
deg it is 0.0032; at (5, 0) 0.0019; at (0.5, 5) 0.0857; the minimum over [0, 5]^2 is at phi = 0 (part 3's margin
(1 + (1 - tan^2 th)^{1/2})/2 - cos th ~ th^2/4 -- the term 0.032 tan th replaces tan th/2 there, harmless).  [T-computed
in check276b: grid 501 x 501, min 0].  ∎

## 6.3 Theorem CORNER  [T].  *H1-H3, side in [3.82, s^], 0 <= th <= 5 deg, 0 <= phi <= 5 deg (X's tilt), th > 0 or C
axis-parallel with the same statement: no unit square Q of the quadrant with int Q ∩ int C = ∅ = int Q ∩ int X has an
interior point in S = T_u \ C.*  Proof.  phi = 0: Theorem FLAT-X (part 3, valid to 30 deg).  phi > 0: q_y > L_h (P0);
q_y < X_low is A1 (6.2), q_y in [X_low, C_top] is A2 (6.1); q_y > C_top: by the position of W_L, part 4.4 (a)-(b)
(Lemma A*), (beta) 5.3, (gamma) 5.1, (delta) 5.2.  ∎   Every step is a chord/pin inequality with the numeric
slack shown; the mechanism at phi = 0 (part 2) is the flat Q at the corner (1, C_top), clearance (1 - c) c;
for phi > 0 the flat Q is dead outright (its left edge would have to be right of R_X, i.e. x >= w_phi, and then
its width 1 exceeds T_x - w_phi) and no near-miss family is second order -- the measured 0.5 th on the diagonal
is consistent with the pins' first-order slack (e.g. (R) vs (T): T_x - w_phi - 1 < 0 by a first-order amount).

## 6.4 Errata to earlier parts (kept for the record)
* part 5, 5.2, case phi > th: the intermediate line reads "< sin phi + (sin phi - sin om) tan th" (not 2 sin phi);
  conclusion unchanged.  The sliver iteration in 5.2 (phi <= th) is replaced by: eps < 0.293 tan th + 1.01 phi^2 <=
  0.39 tan th, so 0.51 eps^2 < 0.078 tan^2 th < 0.49 tan^2 th <= 1 - c, uniformly on the corner.
* The brief's "sliver of S above C's top line of height h_u tan th" does not exist: T_u ⊂ {y <= C_top}; the
  sliver that matters is Sigma of part 1, of WIDTH O(th^2), and the intruder never touches it.
