# A278 part 5 -- CAP-2 at the JAM corner: BL-CAP-2(A, C), the analytic route, the residual and its price

**Statement (float2_room.md s.3, s.5.3).**  JAM corner at BL: A the floor toucher meeting B (offset a < 1, tilt alpha),
C the floater meeting B (h_u, h_v, theta); X the TL-serving wall toucher (X_low >= 1) and A_2 the BR-serving floor
toucher are in S_8 and MAY be used as obstacles; blockers/holders may not.  A BL-SECTOR MISS is a unit square Q in
[0,s]^2, interior-disjoint from the obstacles, with centre q, tilt psi in [-45, 45) deg, u = (cos psi, sin psi),
v = u^perp, and either (floor sector) (q - O).(-v) >= 1/2 and q_x <= s/2, or (wall sector) (q - O).(-u) >= 1/2 and
q_y <= s/2 (A259 s.2.2 turned to BL).  BL-CAP-2(A, C): no two interior-disjoint BL-sector misses.  It is what the
indirect JAM (holder a pocket square) and the middle toucher above X need for n <= 10 (A277 s.3.1, Lean cap2_count_core).

**[T] S1 (half-planes).**  A floor-sector miss lies in H_v := {p : (p - O).v <= 0} (its farthest point in direction v is
(q - O).v + 1/2 <= 0 from O's level) and a wall-sector miss in H_u := {(p - O).u <= 0}.  So every BL-sector miss lies
BELOW a line through O of slope angle psi in [-45, 45) deg, or LEFT of a line through O of slope angle psi + 90 deg.
**[T] S2 (centre bounds).**  Floor sector: (q_y - O_y) cos psi <= -1/2 + (q_x - O_x) sin psi.  For psi >= 0 this gives
q_y <= s/2 - sec(psi)/2 <= 1.4385 (s = s-hat); for psi < 0, q_y <= s/2 - sec(psi)/2 + (s/2 - q_x) tan|psi|, i.e. a
left-leaning miss may sit higher only by moving LEFT of O by the same amount.  Wall sector: the mirror in x.
**[T] S3 (side-by-side floor misses sit in the corner).**  Two floor-sector misses with disjoint x-ranges, Q_1 left:
q_1x + w_1/2 <= q_2x - w_2/2 <= s/2 - w_2/2, so q_1x <= s/2 - (w_1 + w_2)/2 <= s/2 - 1 = 0.9385 and Q_1's x-range lies
in [0, s/2 - 1/2] = [0, 1.4385]; by S2 (psi_1 >= 0) its y-range lies in [0, 2.15].  So Q_1 is a unit square in
[0, 1.4385] x [0, 2.15] interior-disjoint from A and C, both of which meet B = (0,1)^2 with A's left edge at a < 1 and
C's at h_u < 1.  [C] no such square exists (it must thread the gap between A's top and C's bottom, or stand above C
with its centre below 1.4385); psi_1 < 0 lets it sit higher by (s/2 - q_1x) tan|psi_1|.  On every JAM ring measured
(A262) the whole BL sector is empty of misses.
**[T] S4 (side-by-side wall misses: the mirror).**  Two wall-sector misses with disjoint y-ranges force the lower one
into [0, 2.15] x [0, 1.4385]: a unit square with points below height 1, interior-disjoint from A (on the floor over
x in [a, a + w(alpha)], a < 1) and from C.  [C] no such square exists: left of A it is in the START gap of width a < 1
(the WEDGE case of normal_room.md s.2 -- [T] there for a ring with the END square above, [C] here with C floating);
with centre x <= 1.4385 it cannot be entirely right of A, so otherwise it pokes over A's shoulder under C.
**Where the analytic route stops.**  last_two.md s.2.2's stacking argument needs a GAP STRIP (two squares in a strip of
width < 2 cannot be side by side, and the upper one's x-range then contains s/2); here the misses are not confined to a
strip -- S3 is the analogue, and it leaves the near-flat left square [C].  strip_jam.md's LEFT constraint and Lemma
CL speak of squares with a point in S_u(C) (the strip lemma), not of misses; flat_x.md's corner mechanism (the flat
square with its left edge on X's right edge and bottom on C_top) is the extremal FREE square near the JAM corner --
that square has centre (1.5, C_top + 0.5) with C_top = h_v + w(theta) >= 1.0, so q_y >= 1.5 > 1.4385: by S2 it is NOT a
floor-sector miss at psi >= 0 [T]; at psi < 0 it would need to be left of O by >= 0.13 / tan|psi| -- a real sub-case,
not closed.  So BL-CAP-2(A, C) does not close by hand here: [C], with S1-S4 as its structure.

**Residual and price.**  BL-CAP-2(A, C) on the 5-parameter JAM domain (a, alpha; h_u, h_v, theta) at s = s-hat (monotone
in s, A259 s.2.3), obstacles A, C (+ X, A_2 allowed).  Cheapest certificate: cert277 --fam jam (A277's diameter kernel,
imported unchanged): benched 6/6 points CERT at radii 1/32-1/16 (5 CERT-ROOM = the sector region is EMPTY, 1 CERT-CAP2
with diameter 0.01), 0.18 s per point (results/bench277_jam.json); A277's price 3-100 CPU-h for the full tree.  Adding
X (X_low >= 1, serving TL) and A_2 as obstacles is allowed and would turn most leaves into ROOM leaves (A262: pierce
margin <= -0.070 on every JAM ring with the whole ring).  Not launched (mean price above the 20 CPU-h line; the lab is
at its ceiling).  With NO-FLOAT2 [C] (part 4) the two 5d statements stay: BL-CAP-2(C, D) [C, 6 params] and
BL-CAP-2(A, C) [C, 5 params]; the FLOAT2 one would disappear if L (part 3) were certified or proved.
