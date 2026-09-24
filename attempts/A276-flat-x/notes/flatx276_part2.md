# A276 part 2 -- the mechanism at X flat, and Lemma A (the cap right of x = 1)  [T]

Q: unit square, lowest vertex V = (V_x, V_y), tilt om in [0, 90 deg): edges from V are e1 = (cos om, sin om) to the
right vertex W_R and e2 = (-sin om, cos om) to the left vertex W_L = (x_min, y_WL), x_min = V_x - sin om,
y_WL = V_y + cos om; om = 0 is the flat square (V, W_L its bottom-left / top-left corners).  Cap := Q ∩ {y <= C_top},
d_V := C_top - V_y (the cap is empty iff d_V <= 0), depth d := C_top - y in [0, d_V].  w0 := h_u + c - 1 in (0, c).
Standing facts (A272 [T], part 1): q_y > L_h; LEFT; (1.5) Q ∩ {X_low <= y <= X_top} ⊂ {x >= 1}; T_u ⊂ {a <= a*} =
{x <= r_Tu(y)} with r_Tu(y) = c + (C_top - y) tan th the upper-right edge line of T_u.

## 2.1 The mechanism (what the probe found, A272 (f), A274 phi = 0)  [M -> explained]
The near-miss is the FLAT Q with left edge on x = 1 (X's right edge) and bottom edge on y = C_top (touching C at
its top vertex T only).  Its bottom-left corner (1, C_top) is at distance (1 - c) c from T_u (1.4); the probe's
three-way split (penetrate X by delta, penetrate C by delta, stop delta short of T_u) gives delta ~ (1 - c) c / 2 =
c sin^2(th/2): 0.001895 (5 deg), 0.000304 (2), 0.0000761 (1) against A274's 0.00190, 0.000306, 0.000078.  The brief's
"sliver above C's top line" does not exist (T_u ⊂ {y <= C_top}); the thing Q reaches for is T_u's upper-right edge
just below T', at horizontal distance 1 - c right of x = 1 -- second order because T' = (c, C_top) is only
1 - c = 2 sin^2(th/2) left of X's right edge.  Tilting Q does not help (Lemma A): its left vertex must clear x = 1
up to X_top, which costs sin om, while the vertex V can go at most (w0 - sin om) tan om below C_top.

## 2.2 Lemma A (Q entirely right of x = 1)  [T]
*If x_min >= 1 and Q has a chord at height C_top, then every point of the cap has x - r_Tu(y) >= 1 - c + sin om -
(w0 - sin om) tan om tan th >= 1 - c > 0.  In particular Q ∩ T_u = ∅.*
Proof.  (i) The cap is non-empty only if d_V > 0; the chord at C_top exists, and by LEFT (closure) its right end
is <= T_x = 1 + w0.  If W_R were below C_top (sin om < d_V) it would have x = V_x + cos om >= 1 + sin om + cos om
>= 2 > T_x at a height < C_top, against LEFT.  So sin om >= d_V, the chord's right end at C_top is on the edge
V W_R: V_x + d_V cot om <= 1 + w0, and with V_x = x_min + sin om >= 1 + sin om:
        d_V <= (w0 - sin om) tan om   (so sin om <= w0, and om = 0 forces d_V = 0: the flat square has no cap).  (2.1)
(ii) (w0 - sin om) tan om <= cos om (⟸ w0 sin om <= 1), so d_V <= cos om: W_L is at or above C_top, and on the whole
cap the left boundary is the edge V W_L: x_L(y) = V_x - (d_V - d) tan om >= 1 + sin om - (d_V - d) tan om.
(iii) x_L(y) - r_Tu(y) >= 1 - c + sin om - d_V tan om + d (tan om - tan th) =: G(d), affine in d on [0, d_V].
  If om >= th: G(0) = 1 - c + sin om - d_V tan om >= 1 - c + sin om - (w0 - sin om) tan^2 om >= 1 - c, since
  sin om cos^2 om >= (w0 - sin om) sin^2 om ⟸ cos^2 om + sin^2 om >= w0 sin om.
  If om < th: G(d_V) = 1 - c + sin om - d_V tan th >= 1 - c + sin om (1 - (w0 - sin om) tan th / cos om) >= 1 - c,
  since (w0 - sin om) tan th / cos om < w0 tan th / c = w0 s / c^2 <= s / c^2 < 1 for th <= 30 deg (0.667 at 30).
Every point of the cap at depth d has x >= x_L(y) >= r_Tu(y) + G >= r_Tu(y) + (1 - c); T_u lies in {x <= r_Tu(y)}
(it is {a <= a*}); and T_u ⊂ {y <= C_top}.  So Q ∩ T_u = ∅.  ∎   (Domain used: th <= 30 deg for the om < th
branch; w0 < 1; nothing about phi, D, or X beyond x_min >= 1.)

## 2.3 The clearance, exactly  [T]
Min over om of the bound: at om = 0 it is 1 - c (flat Q, corner at (1, C_top)); the horizontal clearance 1 - c is
the perpendicular clearance (1 - c) c of (1.4) divided by c.  The measured 0.25 th^2 is the half of (1 - c) c that
the probe's equal-penetration split leaves: [T] clearance (1 - c) c >= 2 c sin^2(th/2); [M] probe = half of it.
