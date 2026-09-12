# Lemma CORNER-COVER and rule CC -- A210, 2026-09-12 (any n, any side; stated and proved BEFORE use)

The PI's reading (2026-09-12 01:20, on A209's Y0202 leaf R.1.1.2.1.2s, 2,226 s of wall): *"TR00 has a near simple
square, and the regions around the top and left of the simple unit square, where it meets the wall, are certifiably
dead.  Since a square pushed into the corner covers the opposite corner under all rotations, that should imply that
there's no way for TR00 to get a second meeter."*  The second PI note (01:50, `notes/PI_pframe_no_pad_on_the_box.md`)
fixes the frame: **state the lemma in the packing's own frame P and pad the CONTACT REGION, not the slot box.**

Notation.  P is a packing of the container [0, m]^2, m in the tree's window; c is an unpinned container corner and
(u, v) are the distances from c's two walls (`classes178.xy_to_frame`).  A unit square Q of tilt theta in [0, 90)
with centre at frame coordinates (u_c, v_c) has axis-parallel half-width h = h(theta) = (cos theta + sin theta)/2 in
[1/2, 1/sqrt2]; it lies in [0, m]^2 iff u_c, v_c >= h (and symmetrically at the far walls).  Write
d1 = u_c - h >= 0, d2 = v_c - h >= 0 for its distances to the two walls, c = cos theta, s = sin theta.
The corner slot's box at side m is the OPEN unit cell B = (0, 1) x (0, 1) in c's frame (Theorem FC step 1,
`docs/proofs/forced_corners.md`: at side m at least two non-pin squares of P have interiors meeting int B).

## 1. [T] Lemma CORNER-COVER (the covered region, exact)

Let Q be as above with d1, d2 >= 0.  In c's frame Q has vertices

    A = (s + d1, d2),   C = (2h + d1, s + d2),   D = (c + d1, 2h + d2),   B = (d1, c + d2),

and Q = {(u, v) : |p| <= 1/2, |q| <= 1/2} for p = (u - u_c)c + (v - v_c)s, q = -(u - u_c)s + (v - v_c)c, i.e. exactly

    p + 1/2 = c u + s v - c s - (c d1 + s d2)          p - 1/2 = c u + s v - 1 - c s - (c d1 + s d2)
    q + 1/2 = c v - s u + 1 - c^2 + s d1 - c d2        q - 1/2 = c v - s u - c^2 + s d1 - c d2

(using u_c = h + d1, v_c = h + d2, 2h^2 = 1/2 + c s and h(s - c) = (s^2 - c^2)/2 = 1/2 - c^2).  Written out:
**B \ Q = W0 u W1 u W2**, the three explicit open wedges

    W0 (corner wedge, {p < -1/2}) = {(u, v) in B : c u + s v < c s + c d1 + s d2}
    W1 (wall wedge on the v = 0 wall, {q < -1/2}) = {(u, v) in B : v < d2 + s (u - s - d1)/c}
    W2 (wall wedge on the u = 0 wall, {q > 1/2}) = {(u, v) in B : u < d1 + c (v - c - d2)/s}

and the fourth halfplane {p > 1/2} never meets B: on B, c u + s v < c + s = 2h, while the threshold is
1 + c s + c d1 + s d2 >= 1 + c s, and 2h - 1 - c s = -(1 - c)(1 - s) <= 0.  (Divisions by c or s are removals of a
degenerate case: at theta = 0, W1 = {v < d2} and W2 = {}; at theta = 90, W2 = {u < d1} and W1 = {}.)

*Proof.*  Q is the intersection of the four halfplanes |p| <= 1/2, |q| <= 1/2 (p, q are the coordinates of the
offset from the centre in Q's own frame, an isometry).  The displayed identities are the substitution above; a point
of B fails one of them exactly when it lies in W0, W1 or W2 (the fourth is empty on B by the computation above).
The four vertices are centre +- e1/2 +- e2/2 with e1 = (c, s), e2 = (-s, c). []

**Corollary CC0 (the PI's sentence, sharp).**  With d1 = d2 = 0 (Q touching both walls) the inner corner (1, 1) of
the cell lies in Q for EVERY tilt: its offset from the centre is (1 - h, 1 - h), whose Q-frame coordinates are
u' = 2h(1 - h) and v' = (1 - h)(c - s); 2h(1-h) <= 1/2 is (2h - 1)^2 >= 0, and with d = |c - s| = sqrt(2 - 4h^2),
v'^2 = (1-h)^2 (2 - 4h^2) <= 1/4 because f(h) = 2(1-h)^2(1 - 2h^2) has f(1/2) = 1/4 and
f'(h) = -4(1-h)(1 + h - 3h^2) < 0 on [1/2, 1/sqrt2] (the root (1 + sqrt13)/6 = 0.7676 > 1/sqrt2).  Equality only at
theta in {0, 90}, where (1, 1) is a vertex of Q. []

**Corollary CC1 (the band, closed form).**  Over a tilt interval [theta0, theta1] and slacks d1 in [0, D1],
d2 in [0, D2], W0 u W1 u W2 is contained in the union of three axis-parallel rectangles of the cell [0, 1]^2:

    R0 = [0, min(1, s1 + D1 + (s1/c0) D2)] x [0, min(1, c1 + D2 + (c1/s0) D1)]         (corner wedge)
    R1 = [0, 1] x [0, min(1, D2 + c1 s1/(1 + s0))]                                     (v = 0 wall band)
    R2 = [0, min(1, D1 + c1 s1/(1 + c0))] x [0, 1]                                     (u = 0 wall band)

with c0 = min cos = cos theta1, c1 = max cos = cos theta0, s0 = min sin = sin theta0, s1 = max sin = sin theta1
(cos decreasing, sin increasing on [0, 90]), and the convention x/0 = +infinity (then the factor is clamped by the
cell).  *Proof.*  W0 lies under both intercepts of its bounding line, (c s + c d1 + s d2)/c = s + d1 + (s/c) d2 and
(.)/s = c + d2 + (c/s) d1, each increasing in d1, d2 and bounded by the stated monotone envelopes.  For W1, u <= 1
gives v < d2 + s(1 - s - d1)/c <= d2 + s(1 - s)/c = d2 + s c/(1 + s) (using 1 - s^2 = c^2), which is <= D2 +
c1 s1/(1 + s0) since the numerator increases and the denominator decreases; symmetrically for W2 with
c(1 - c)/s = c s/(1 + c).  All three are intersected with the cell. []

For a NEAR-SIMPLE Q (theta in [0, theta1] small) and D1, D2 <= delta this is a thin L along the two walls:
R0 u R2 has width <= sin theta1 + delta + O(delta sin theta1) in u and R1 height <= delta + sin theta1 cos theta1 in
v -- at theta1 = 5 deg, delta = 0.05: u <= 0.142, v <= 0.131.  At theta = 45 deg the band is the whole cell and the
rule says nothing: **CC only bites on a near-simple corner square** (the PI's "near simple square").

## 2. [T] Corollary CC' -- the transfer to the page (F), no pad on the box

The page's record is F = the image of P under the dilation of `forced_corners.md` section 2: every square is
TRANSLATED, Q' = Q + (lambda - 1) c_Q, the container side going m -> s0 = lambda m, lambda in [1, lambda_page]
(lambda_page = 1 at pad 0 -- the page IS the packing; lambda_page = s0/3.861637 = 1.0040001 on the G1 slab).  In a
corner frame a point of Q' has frame coordinate q'_u = q_u + (lambda - 1) u_c and the CENTRE has u'_c = lambda u_c
(`forced_corners.md` section 2, step 2).  Hence:

 (a) **the slack read on the page is an upper bound for the slack in P**: d1(P) = u_c - h = u'_c/lambda - h <=
     u'_c - h = d1(F) (since u'_c >= 0 and lambda >= 1).  So CC1's band computed from the page's box is valid.
 (b) **the second meeter.**  Let Q1 be a square of P whose page image is within delta of both walls of c (so
     d1(P), d2(P) <= delta), and let Q2 be ANY other non-pin square of P whose interior meets int B.  Q2's interior
     is disjoint from Q1's, so a point x in int Q2 ∩ int B lies in B \ Q1 = W0 u W1 u W2 (Lemma CORNER-COVER), and
     |x - c_{Q2}| <= 1/sqrt2 in Euclid and <= w_max/2 per axis (sideband (F1)).  Therefore in P
         dist(c_{Q2}, W) <= 1/sqrt2,   W = W0 u W1 u W2 contained in R0 u R1 u R2,
     and on the page c'_{Q2} = lambda c_{Q2}, so with W+ := W grown by (lambda - 1) on its far sides (W lies in the
     unit cell, so lambda w lies in the segment [w, lambda w] contained in w + [0, lambda - 1]^2)
         **dist(c'_{Q2}, W+) <= lambda/sqrt2   and   |c'_{Q2} - W+|_inf <= lambda w_max/2.**
     There is NO inner-corner margin disc and NO far-side strip of width pi_i: the slot box is padded only because
     the page's coordinates are the translated ones, and the contact region W is padded by the same translation,
     which is <= lambda - 1 = 0.004 at the corner -- not by the box pad pi_0 = 0.0068 and not by 1/sqrt2 + pi_0.
     At pad 0, lambda = 1 and the statement is exactly dist(c_{Q2}, W) <= 1/sqrt2. []

**Rule CC (stage 0, closed form, microseconds).**  For every corner slot p = c(0, 0) (c unpinned) of a page:
 1. find a PUSHED-IN square: a named role (H, a further H_k, or an instantiated role F_j at a tree leaf) ALL of whose
    alive pieces satisfy d1, d2 <= delta = 0.05 in c's frame; or, failing that, the case where every alive anonymous
    piece of p lies in ONE grid cell and all of them are pushed in (then the unique anonymous meeter is the pushed-in
    square).  Such a square is automatically a meeter of p (it covers the cell minus W, which has interior).
 2. build the band W+ = union over that square's alive pieces of CC1's three rectangles (each piece contributes its
    own (theta0, theta1, D1, D2)), grown by (lambda - 1) on the far sides and mapped back to container coordinates.
 3. every OTHER meeter of p must satisfy CC'(b).  A piece (or option row, or role box) failing it for every
    rectangle of the band is DEAD for p (letter **Q**); H's reach at p is removed the same way when the pushed-in
    square is not H.  If no second meeter survives, Theorem FC's demand 2 fails and the page/leaf is DEAD.
Soundness: every step is a necessary condition on a genuine pose pair, so the surviving set is a superset of the
true one -- the stage-0 discipline of `attempts/A202-fast30/notes/fast30.md` section 0.  Verdicts are
`[C: closed-form trace; Lemma CORNER-COVER]`; no verifier clause exists for these rules yet.

## 3. What CC cannot do

* Nothing when the pushed-in square's tilt interval is wide (the band is the whole cell near 45 deg), and nothing
  when no square is pushed into the corner -- at a page ROOT the conditioned square H is usually a mid-container box,
  so CC is a LEAF rule (A209's instantiated roles) far more than a page rule.
* It restricts only the meeters of the CORNER slot of the corner the square is pushed into (i = j = 0); the wedge
  bound degenerates for offset cells (the square does not cover them).
* It is a NECESSARY condition on the second meeter's centre, not a packing argument: it never decides a node whose
  second meeter genuinely sits in the wall band (the cells along the two walls next to the corner cell).  Those
  cells have to die by the other stage-0 rules (P/W/C/M/L/R/X, the CSP) -- as they do on the PI's Y0202 leaf.
* The G1-pad and pad-0 statements differ only by lambda - 1 = 0.004 in the band and 0.0029 in the radius, so a CC
  kill at pad 0 that fails on the window is a numerical near-miss, not a pad ghost.
