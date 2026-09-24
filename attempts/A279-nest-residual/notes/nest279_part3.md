# A279 part 3 -- three inequalities every NEST quadruple satisfies  [T]  (the count chase, first half)

Notation of parts 1-2; n_phi := (-sin phi, cos phi) the up-left normal of a line of slope angle phi; w_Q := cos th_Q
+ sin th_Q in [1, sqrt2] the axis extent of a unit square Q of tilt th_Q; m_Q its centre (= centre of its inscribed
disc of radius 1/2, and Q lies in the disc of radius 1/sqrt2 about m_Q).  ell' = a D -> C separator (angle alpha),
ell = a Y -> D separator (angle eta), eta < alpha by (NEST).  Every line below uses only: C, D meet B; Y subset
{x >= 1} touches the floor; Y has a point p (p_x >= 1) with p + tau e_y in D; C subset {x >= 0}.

**3.1 (Sigma) [T] -- the vertical budget.**  Inscribed discs on opposite sides of a separator have centres at
distance >= 1 across it: n_alpha . (m_C - m_D) >= 1 and n_eta . (m_D - m_Y) >= 1.  Adding,
   m_C,y - m_Y,y >= sec alpha + sec eta + (m_C,x - m_D,x) tan alpha + (m_D,x - m_Y,x) tan eta.
C has a point below height 1, so m_C,y < 1 + w_C/2 <= 1 + 1/sqrt2; Y touches the floor, so m_Y,y = w_Y/2 >= 1/2.
Hence   (m_Y,x - m_C,x) tan eta + (m_D,x - m_C,x)(tan alpha - tan eta) > sec alpha + sec eta - 1/2 - 1/sqrt2 >= 0.793.
Reading: the horizontal offsets Y-right-of-C and D-right-of-C, weighted by the separator slopes, must carry 0.793;
with the bounds m_Y,x - m_C,x <= 2.62 and m_D,x - m_C,x <= 1.21 (Y's left vertex under D's extent; D's left vertex
left of 1) this EXCLUDES shallow nests: not both tan eta and tan alpha small.  E.g. tan alpha <= 0.3 is impossible.

**3.2 (Sigma') [T] -- the same with vertices.**  n_alpha . c >= n_alpha . t_D (c = C's box point, t_D = D's top
vertex, height h_v + w_D) and n_eta . b_D >= n_eta . t_Y (b_D = D's bottom vertex (x_b, h_v), t_Y = Y's top vertex,
height w_Y):   w_Y + w_D - 1 < (t_D,x - c_x) tan alpha + (t_Y,x - x_b) tan eta <= (h_u(D) + cos th_D) tan alpha +
(cos a + cos th_D) tan eta.   In particular D's lowest point satisfies
   h_v(D) >= w_Y - (t_Y,x - x_b) tan eta >= 1 - (cos a + cos th_D) tan eta      (D high when eta is shallow),
   h_v(D) < 1 - w_D + (h_u(D) + cos th_D) tan alpha                                (D low when alpha is shallow).

**3.3 (WEDGE) [T] -- the horizontal budget for C.**  C lies in the wedge {x >= 0} ∩ {n_alpha . x >= beta'} whose
right boundary is ell': x_ell'(y) = x_ell'(y0) + (y - y0) cot alpha.  D's left vertex (h_u(D), h_v + cos th_D) is on
or beyond ell', so x_ell'(h_v + cos th_D) <= h_u(D).  C's inscribed disc is inside the wedge: m_C,x >= 1/2 and
x_ell'(m_C,y) >= m_C,x + 1/(2 sin alpha) >= 1/2 + 1/(2 sin alpha) >= 1.  With m_C,y < 1 + w_C/2 <= 1.707:
   h_u(D) >= 1/2 + 1/(2 sin alpha) + (h_v(D) + cos th_D - 1 - w_C/2) cot alpha.        (WEDGE)
Since h_u(D) < 1 (D meets B; sharper: h_u cos th + h_v sin th < cos th + sin th - sin th cos th, open_box_tilted),
   (1 + w_C/2 - h_v(D) - cos th_D) cot alpha > 1/(2 sin alpha) - 1/2 >= 0,   so   h_v(D) + cos th_D < 1 + w_C/2,
and the bracket must pay 1/(2 sin alpha) - 1/2 + (1 - h_u(D)) tan... -- steep alpha is cheap here, shallow alpha
expensive.  (Sigma) is the opposite: shallow angles are impossible there.  The residual, if any, lives where alpha is steep
enough for (Sigma) and yet C -- of horizontal extent w_C inside the wedge -- still reaches below height 1.
**FLAT C, exactly [T].**  If C = [x0, x0+1] x [y0, y0+1] is flat (y0 < 1), C's bottom edge is horizontal, so it is
NOT a D -> C separator (FLOAT-SLOPE); D's box point q has q_y < y0 and q_x < 1 (q is beyond ell', which passes
right of C's lower-right corner at height y0), so D's LEFT vertex L_D = (h_u(D), y_L) pokes under C's bottom edge:
y_L < y0 and D's upper-left edge leaves x < 1 before height y0: (1 - h_u(D)) tan th_D <= y0 - y_L.  With
h_v(D) = y_L - cos th_D >= 0:  h_v(D) < 1 - cos th_D  and  1 - h_u(D) <= (1 - cos th_D) cot th_D <= 0.30, i.e.
h_u(D) >= 0.70.  Against (Sigma'): 1 - (cos a + cos th_D) tan eta <= h_v(D) < 1 - cos th_D gives
tan eta > cos th_D / (cos a + cos th_D) >= cos th_D / (1 + cos th_D): a flat C forces a NON-shallow Y-D separator
(eta > 18 deg for th_D <= 60 deg), and then (NEST) needs alpha > eta with alpha >= th_D as well (the separator
through C's corner (x0 + 1, y0) must clear L_D).  Not a contradiction by itself: the exact chain is part 4's job.
**3.4 What is still needed for a hand proof of "NEST is infeasible".**  A single chain combining (Sigma) [shallow
angles impossible], (WEDGE) [steep alpha needs a flat-ish C], FLAT-C [a flat C forces eta > 18 deg] with quantitative
intermediate cases -- a 3-parameter (th_C, alpha, h_v) sweep at worst.  [C] until part 4.
