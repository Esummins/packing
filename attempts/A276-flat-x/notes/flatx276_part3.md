# A276 part 3 -- the other cases at X flat: A1, A2, W_L under X (B), W_L above X (C)  [T], th <= 30 deg

Notation of parts 1-2; eta := X_low - y1 = D_max - D in [0, w0 tan th).  Recall y1 = L_h + (1 - h_u) tan th is the
height of C's upper-left edge at x = 1, so a point (x, y) with x in [1, T_x], y <= C_top is outside int C iff
y >= y1 + (x - 1) tan th, and LEFT says every point of Q below C_top has x < l_C(y) <= T_x.

## 3.1 A2 (q_y in [X_low, C_top]) dead.  The centre chord (length >= 1) lies in [1, l_C(q_y)) by (1.5) + LEFT, and
l_C(q_y) <= T_x = 1 + w0 < 2.  ∎

## 3.2 A1 (L_h < q_y < X_low) dead for th <= 30 deg.  X_low - q_y < X_low - L_h = s - D < 1/2, so the inscribed disc
D(q, 1/2) ⊂ int Q has a chord at height X_low of half-length rho0 := (1/4 - (X_low - q_y)^2)^{1/2} > 0; by (1.5)
q_x >= 1 + rho0.  The centre chord ⊃ [q_x - 1/2, q_x + 1/2] lies in [0, l_C(q_y)) (LEFT) and l_C(q_y) = 1 +
(q_y - y1) cot th, so q_y - y1 > (q_x - 1/2) tan th >= (1/2 + rho0) tan th, hence X_low - q_y < eta - (1/2 + rho0)
tan th < tan th / 2 (eta < w0 tan th, w0 < 1), rho0 > (1/2) (1 - tan^2 th)^{1/2}, and
        3/2 + (1/2)(1 - tan^2 th)^{1/2} <= q_x + 1/2 < l_C(q_y) < 1 + w0 < 1 + c,
i.e. (1 + (1 - tan^2 th)^{1/2}) / 2 < cos th -- FALSE for th <= 38 deg (0.9981 vs 0.9962 at 5; 0.908 vs 0.866 at
30).  ∎   So from here q_y > C_top: Q has a chord at C_top, V below C_top, and the DROP holds.

## 3.3 The split on W_L = (x_min, y_WL).  By (1.5): y_WL in [X_low, X_top] ⟹ x_min >= 1 ⟹ Lemma A.  Otherwise
(B) y_WL < X_low or (C) y_WL > X_top.  (If x_min >= 1 in either, Lemma A applies; assume x_min < 1 in (B).)

## 3.4 Case (C): y_WL > X_top = X_low + 1.  Then cos om = y_WL - V_y > X_top - C_top = 1 - D, so om is tiny and the
edge V W_L is the left boundary of Q up to X_top; (1.5) at height X_top: V_x - (X_top - V_y) tan om >= 1, i.e.
V_x >= 1 + (1 - D + d_V) tan om.  W_R is right of T_x: V_x + cos om >= 1 + (1 - D) tan om + cos om > 1 + w0 (since
cos om + (1 - D) tan om >= cos om + (1 - w0 tan th) tan om > 1 > w0 on om in [0, 45 deg], th <= 30), so LEFT at
C_top (W_R below C_top would violate it; else the chord's right end is on V W_R) gives V_y + (T_x - V_x) tan om
>= C_top: d_V <= (T_x - V_x) tan om <= w0 tan om.  On the cap, x_L(d) - r_Tu(d) = V_x - (d_V - d) tan om - c -
d tan th >= 1 - c + (1 - D) tan om + d (tan om - tan th) >= 1 - c + tan om (1 - D - w0 tan th) >= 1 - c +
tan om (1 - 2 w0 tan th) >= 1 - c  (D <= w0 tan th, tan th <= 1/2).  As in Lemma A: Q ∩ T_u = ∅.  ∎

## 3.5 Case (B): y_WL < X_low, x_min < 1.  Q's top vertex is above X_low (else Q ⊂ {y < X_low}: q_y < X_low, 3.2),
so the upper-left edge W_L W_T (slope dx/dy = cot om) is Q's left boundary at height X_low and (1.5) gives
        (1 - x_min) tan om <= X_low - y_WL.                                                                (3.1)
V = (x_min + sin om, y_WL - cos om) is below C_top; by LEFT V_x < l_C(V_y) <= T_x.
(B1) x_min >= h_u.  W_L is outside int C, so y_WL >= L_h + (x_min - h_u) tan th.  V_y >= L_h: otherwise V_x <
l_C(V_y) <= h_u + s gives sin om < s, and X_low - y_WL = (s - D) + (L_h - V_y) - cos om with L_h - V_y < 0.7071 - s
(q_y > C_top: V_y > C_top - (sin om + cos om)/2) gives X_low - y_WL < 0.7071 - D - cos om < 0.7071 - c < 0 for
th < 45.  So V, at height in [L_h, C_top] with V_x in [h_u, T_x), is above C's upper-left line:
y_WL - cos om >= L_h + (x_min + sin om - h_u) tan th.  Insert y_WL <= X_low - (1 - x_min) tan om from (3.1) and
X_low - L_h = s - D = D_max + (1 - h_u) tan th - D:
        eta >= cos om + sin om tan th + (1 - x_min)(tan om - tan th).                                      (3.2)
  om >= th: eta >= cos om + sin om tan th = cos(om - th) / c >= min(1, s) / c = tan th > w0 tan th > eta.  ✗
  om < th:  eta >= cos om - (1 - h_u)(tan th - tan om) > c - (1 - h_u) tan th; with eta < (h_u + c - 1) tan th this
            needs c < c tan th, i.e. th > 45.  ✗
(B2) x_min < h_u.  From q_y > C_top and y_WL < X_low: V_y > C_top - (sin om + cos om)/2 and V_y + cos om < C_top - D,
so cos om < sin om - 2 D: om > 45 deg, and X_low - y_WL < (sin om - cos om)/2 - D.  By (3.1), 1 - x_min <=
((sin om - cos om)/2 - D) cot om <= (cos om - cos^2 om) / 2 <= 1/8, so x_min > 7/8 and V_x = x_min + sin om >
7/8 + 0.7071 > 1.58 > h_u.  V is below C_top, right of x = 1: V_y >= L_h (else V_x < h_u + s < 1.58), so V is above
C's upper-left line: V_y >= y1 + (V_x - 1) tan th, and V_y = y_WL - cos om < X_low - cos om gives
        eta > cos om + (V_x - 1) tan th >= cos om + (sin om - cos om / 2) tan th
(V_x - 1 = sin om - (1 - x_min) >= sin om - cos om / 2).  With eta < w0 tan th < c tan th = s:
        cos om (1 - tan th / 2) < tan th (c - sin om),  so sin om < c and cos om > s,  so  c - sin om > (1 - tan th/2) c,
i.e. sin om < s / 2 < 1/2 -- against om > 45 deg.  ✗   ∎

## 3.6 Theorem FLAT-X [T].  *H1-H3, side in [3.82, s^], phi = 0 (X flat), 0 < th <= 30 deg: no unit square Q of the
quadrant with int Q ∩ int C = ∅ = int Q ∩ int X has an interior point in S = T_u \ C; in the only non-dead case
(x_min >= 1, or W_L above X) every point of Q below C_top is >= 1 - c = 2 sin^2(th/2) right of T_u's upper-right
edge line.*  Proof: 3.1-3.5 + Lemma A.  ∎   (Uses of H1-H3: H2 for (1.1) and the room-zero form of (P2); H3/(F4)
for L_h > 1 in (P0)-(P1); nothing about A beyond A272's (P0).)
