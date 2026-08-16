# A02 — Stromquist (2003), "Packing 10 or 11 unit squares in a square": full reconstruction and assessment

Source: W. Stromquist, Electronic J. Combin. 10 (2003) #R8. PDF: `docs/papers/stromquist2003.pdf`;
extracted text: `stromquist2003.txt`; figure renders `fig*.png`, `page*.png` (this directory).
Numerical checker (grid, non-rigorous): `check_stromquist.py`.

Notation. s = side of the container S = [0,s]^2. A **box** is the *interior* of a square of side
strictly greater than 1 (Stromquist's convention: proving "n boxes cannot be packed inside S with
side exactly a" is equivalent to s(n) >= a, and the extra margin turns closed/open and equality
issues into strict ones). "Box contains a point" = point in the open box. A box that "touches the
x-axis" (or a wall) is not inside S. Throughout, a **unit-square check** means: for every
orientation theta and every admissible centre, the closed unit square meets the point set — this is
what a computer must verify; the ">1 side" convention only removes measure-zero boundary cases.

Key elementary fact used everywhere: a box with centre c and tilt theta contains the point p iff
c lies in the open unit square of tilt theta centred at p (call it Sq_theta(p)). Hence *every*
"nonavoidance lemma" below is a statement of the form

    for all theta:  R  ⊆  W_theta  ∪  ⋃_{p in P} Sq_theta(p)          (*)

where R is a region of centres, W_theta = {centres whose box crosses a wall} (a half-plane per
wall: distance to wall < (cos theta + sin theta)/2), P a finite point set. Every lemma and both
theorems reduce to finitely many instances of (*), which is a 3-parameter (x, y, theta) coverage
check — exactly what an interval branch-and-bound (I-C2 / A05 verifier) does.

---------------------------------------------------------------------------------------------------
## 1. The nonavoidance lemmas (Section 1 of the paper)

All lemmas are stated for a box whose centre lies in a region touching the x-axis (a wall).

**Lemma 1** (a, b <= 1). Centre in [0,a]x[0,b] => box meets the x-axis, the y-axis, or contains
(a,b). [Friedman's Lemma 1.] Proof idea: the box contains the disc of radius 1/2 about its centre
and its bounding box has side >= 1; a box avoiding both axes has centre with x, y >= 1/2 (in fact
>= (cos+sin)/2), and then (a,b) with a,b <= 1 is within the box (check: (a,b) - c has both rotated
coordinates in (-1/2, 1/2)). Used with (a,b) = (1,1) for the four corner squares and (1,.9) etc.

**Lemma 2** (unit-triangle lemma). T a triangle with all sides <= 1. Centre in int(T) => box
contains a vertex of T. [Friedman's Lemma 2.] Proof idea: the box is a convex set of "width" >= 1
in every direction and inradius 1/2; if it avoids the three vertices, each vertex lies outside a
strip; a routine argument (or (*) check) shows impossible when all sides <= 1. Note: side length
exactly 1 is allowed because boxes have side > 1. This lemma is *tight*: for a triangle with a
side of length 1 + eps, a box tilted parallel to that side, straddling it, and positioned within
eps along it avoids all three vertices (see Section 3.4).

**Lemma 3** (a, b <= 1, a + 2b <= 2*sqrt2 ≈ 2.828). Centre in [0,a]x[0,b] => box meets the
x-axis, or contains (0,b) or (a,b). Main uses: (a,b) = (2sqrt2-2, 1) = (.828, 1) and (1, .914).
The number 2sqrt2-2 = .828 is D(45°), the length of the chord at height 1 of a unit square tilted
45° with a vertex on the x-axis (see Lemma 6). It is the reason a bottom-row spacing > .828 lets
a 45°-tilted wall-hugging box escape two consecutive row points at height 1.

**Lemma 4** (the workhorse). Define, for 2sqrt2-2 < a < 1,
    f(a) = min over theta in (0°,90°) of  b*(theta) := cos t/(1+cos t) + (1 - a cos t)/sin t.
Let 0 < b < 1, |(a,b) - (0,1)| <= 1, b <= f(a). Then a box with centre in the quadrilateral
Q(a,b) = conv{(0,0), (0,1), (a,0), (a,b)} meets the x-axis, or contains (0,1), or contains (a,b).
Proof (Fig. 5): a box avoiding the x-axis and (0,1) can be slid down to touch the x-axis and left
to pass through (0,1) (both moves keep the centre in Q, which is closed under both); for such an
extremal box with tilt theta and lowest vertex V0 = (z tan t, 0), z = cos t/(1+cos t) (from the two
congruent right triangles in Fig. 5, z + z/cos t = 1), the right edge crosses the line x = a at
height b*(theta); every (a,b) with b <= b*(theta), above the bottom edge and within 1 of (0,1) is
inside the box. Minimising over theta gives f(a). Setting d b*/d theta = 0 and squaring gives
Stromquist's cubic (2): 2c^3 - (2a+2)c^2 + (a^2-2a+3)c - (1-a^2) = 0, c = cos theta*.
  Tabulated in the paper:  a = .8536 (=1/2+1/sqrt8): f = .972, theta* = 39.5°;
                           a = .8944 (=sqrt(4/5)):    f = .926, theta* = 24.1°;
                           a = .96:                   f = .769, theta* = 17.7°.
  **Erratum found (verified numerically, see check below):** the cubic (2) comes from squaring
  (a - c)(1+c)^2 = sin^3 and has a spurious root with c > a. For a = sqrt(4/5) the paper took the
  spurious root (24.1°). The true minimum is f(sqrt(4/5)) = **0.9145** at theta* = **31.46°**
  (brute force over theta agrees). For a = .8536 and .96 the table is right (there the paper
  happened to take the correct root). Consequence: every use of Lemma 4 with (a,b) = (.894, .9)
  in Theorem 2 (the A2–B, B–C, C–D, D–E, E–F quadrilaterals of Fig. 14) is still valid, but with
  margin .0145 instead of .026. Other numerically relevant values: f(.9)=.905, f(.92)=.868,
  f(.939)=.826, f(.945)=.81, f(.95)=.798, f(.96)=.769.

**Lemma 5** (only for s(10)). P = pentagon (1,0),(1,1),(2,1),(2.12,.9),(2.12,0). Centre in int(P)
=> box meets the x-axis, or the segment (1,.788)–(1,1), or the segment (2,1)–(2.12,.9). Proof: by
Lemma 1 (applied to [1,2]x[0,1] shifted) the box reaches left of x=1 and right of x=2; WLOG it
touches the x-axis and passes through (1,.788); with tilt theta: (i) tan theta <= 1.2: the chord
at y=1 has right end x = 1 + .212/tan t + (sin t + cos t - 1)/(sin t cos t) > 1 + .212/1.2 + .828
> 2.004, so (2,1) is inside; (ii) 50.2° < theta <= 64.2° (=asin .9): the chord at y=.9 has right end
1 + .112/tan t + (sin t + cos t - .9)/(sin t cos t) >= 2.1256 (min at 52.6°), so (2.12,.9) is
inside; (iii) theta > 64.2°: the rightmost vertex (x,y) = (1 + (sin t + cos t - .788)/tan t, sin t)
has .9 < y < 1 and (x-2)/(1-y) = (1-cos t)/sin t + .212(1+sin t)/(sin t cos t) > .6 + 1 > 1.2,
so the vertex is right of the critical segment and the box crosses it.

**Lemma 6** (only for s(11)). a = sqrt(4/5). Centre in the pentagon (1,0),(1,1),(1+a/2,1.12),
(1+a,1),(1+a,0) => box meets the x-axis or contains one of the pentagon's vertices (effectively:
(1,1), (1+a,1) or the apex (1+a/2, 1.12), the other two being on the wall). Proof: WLOG the box
touches the x-axis. Its chord at height 1 has length
    D(theta) = 1/sin t + 1/cos t - 1/(sin t cos t) = 2(sqrt(1+sin 2t) - 1)/sin 2t
(minimum D(45°) = 2sqrt2-2 = .828; D -> 1 as t -> 0 or 90°). Let theta0 = (1/2) asin(5-2sqrt5)
≈ 15.9°, so D(theta0) = a. If theta < theta0 or theta > 90°-theta0 then D > a and the box contains
(1,1) or (1+a,1) (a chord longer than the gap between the two points at height 1, and the box
sits between them). Otherwise cos t + sin t > 1.12, the box rises above y = 1.12; WLOG it touches
(1+a,1) with its apex right of x = 1+a/2; the top edge crosses x = 1+a/2 at height
1 + (D(theta) - sqrt(1/5)) tan theta, which equals 1.1277 at theta0 and increases with theta, so
the apex point (1+a/2, 1.12) is inside. (Numbers: 1.12 has slack .0077 at theta0.)

45°-only variants (for Theorem 3):
**Lemma 7**: if every side of triangle T has component <= 1 along each of the four directions
0°, 45°, 90°, 135°, then a 0°/45° box centred in int(T) contains a vertex.
**Lemma 8**: Lemma 4 for 0°/45° boxes with (a,b) = (1,.8) or (2sqrt2/3, 2sqrt2-2) = (.943,.828).
(Proofs omitted in the paper.)

---------------------------------------------------------------------------------------------------
## 2. Theorem 2: s(11) >= 2 + 2 sqrt(4/5) = 3.788854... — complete reconstruction

Fix s = 2 + 4/sqrt5. Useful numbers: s/2 = 1 + 2/sqrt5 = 1.8944, s - 1 = 2.7889,
d := s/2 - 1 = 2/sqrt5 = .8944 (row spacing), d/2 = 1/sqrt5 = .4472.

### 2.1 Stage 1: the 10-point set P1 (Fig. 13) — a 3-4-3 lattice
    bottom row (y = 1):     (1,1), (s/2,1), (s-1,1)                          [x-spacing d]
    middle row (y = s/2):   (3/2 - s/4, s/2) = (1 - 1/sqrt5, s/2) = (.5528, 1.8944),
                            (1/2 + s/4, s/2) = (1 + 1/sqrt5, s/2) = (1.4472, 1.8944),
                            and mirror images x -> s - x: (2.3416, s/2), (3.2361, s/2)   [x-spacing d]
    top row (y = s-1):      (1,s-1), (s/2,s-1), (s-1,s-1)
Symmetry group: reflections in the two mid-lines (Klein group), NOT the 90° rotation.
Every "sloping side" (bottom/top-row point to adjacent middle-row point) is the vector
(±1/sqrt5, 2/sqrt5) of length EXACTLY 1; every triangle of Fig. 13 is isosceles with legs 1 and
base d = .894 (all sides <= 1).

Partition of S (Fig. 13) and the lemma covering each region:
  (R1) 4 corner squares [0,1]^2 etc.:            Lemma 1 (a=b=1) -> wall or corner point (1,1)…
  (R2) 4 side quadrilaterals, e.g. conv{(0,1),(1,1),(.5528,s/2),(0,s/2)} and its 3 images:
       Lemma 4 with the wall x=0 as "x-axis", a = s/2 - 1 = .894 (wall segment (0,1)-(0,s/2)),
       the unit side (0,1)-(1,1), and (a,b) -> (.5528, s/2), b = .5528 <= f(.894) = .9145,
       |(.5528,s/2) - (1,1)| = 1 (tight). -> wall, (1,1) or (.5528, s/2).
  (R3) 12 triangles filling the two strips 1 <= y <= s/2 and s/2 <= y <= s-1 between the quads:
       e.g. (1,1),(.5528,s/2),(1.4472,s/2); (1,1),(1.4472,s/2),(s/2,1); … : Lemma 2 (legs = 1).
  (R4) **4 edge rectangles NOT covered by any lemma**: [1,s/2]x[0,1], [s/2,s-1]x[0,1] and their
       top mirrors. (Lemma 3 would need d <= .828, Lemma 1 would need a wall at x=1.) Indeed a
       45°-box with a vertex on the bottom wall between (1,1) and (s/2,1) has chord .828 < .894 at
       height 1 and avoids all of P1.
So: every box in S whose centre is not in R4 contains a point of P1.
(Grid check, `check_stromquist.py`, 220^2 centres x 91 tilts: no P1-avoiding unit square with
centre outside R4.)

### 2.2 Stage 2: the exceptional box eats three points
Suppose 11 boxes are packed in S. Boxes are disjoint open sets, so a point lies in at most one
box; hence at most 10 boxes contain a P1 point, and some box X avoids P1. By 2.1 its centre is
in R4; by the Klein symmetry WLOG in the bottom-left edge rectangle [1,s/2]x[0,1].
Then X contains all three of
    A1 = (1, .9),   A2 = (s/2, .9) = (1.8944, .9),   A3 = (1 + 1/sqrt5, 1.12) = (1.4472, 1.12).
  * A3 by Lemma 6 (with the x-axis = bottom wall, a = d): X avoids the wall, (1,1) and (s/2,1)
    (both in P1), so it contains the apex (1 + d/2, 1.12) = A3.
  * A1 by Lemma 4 applied to conv{(s/2,0),(s/2,1),(1,0),(1,.9)}: unit side (s/2,0)-(s/2,1),
    wall = bottom wall between x=1 and x=s/2 (a = d), (a,b) -> (1,.9), b = .9 <= f(.894) = .9145,
    |(1,.9)-(s/2,1)| = .9 <= 1. X's centre is in that trapezoid (its centre is at distance >= 1/2
    from (1,1) and (s/2,1), forcing centre y <= 1 - sqrt(1/4 - 1/5) = .776 < .9). X avoids wall
    and (s/2,1), so it contains A1. A2 symmetrically.
  (Grid check: every P1-avoiding unit square found contains A1, A2, A3 up to symmetry.)

### 2.3 Stage 3: the 12-point set P2 (Fig. 14) and the count
    A1, A2, A3 as above;   B = (s-1, 1);   C = (s-.9, s/2);   D = (s-1, s-1);   E = (s/2, s-.9);
    F = (1, s-1);   G = (.8, 1.85);   H = (1.5, 2.1);   I = (2.1, 2.1);   J = (2.1, 1.5).
(B, D, F are also in P1.) Claim: P2 is unavoidable in S. Partition (read off Fig. 14):
  corners: [0,1]x[0,.9] (Lemma 1, point A1), [s-1,s]x[0,1] (B), [s-1,s]x[s-1,s] (D), [0,1]x[s-1,s] (F);
  bottom-left rectangle [1,s/2]x[0,.9]: Lemma 3 with a=.894, b=.9 (a+2b = 2.694 <= 2.828) -> A1/A2;
  small triangle A1 A3 A2 above it: Lemma 2 (sides .498,.498,.894);
  bottom-right trapezoid (s/2,0),(s/2,.9)=A2,(s-1,1)=B,(s-1,0): Lemma 4, a=.894, b=.9 (margin .0145);
  right side quads B,(s,1),(s,s/2),C and C,(s,s/2),(s,s-1),D: Lemma 4 with a=.894, b=.9;
  top: quads D–E and E–F: Lemma 4 (a=.894,b=.9);
  left side: quad (0,s-1),F,G,(0,1.85): Lemma 4 with a = .939, b = .8 (f(.939)=.826, |FG|=.96);
             quad (0,1.85),G,A1,(0,.9): Lemma 4 with a = .95, b = .8 — **see 2.5**;
  13 interior triangles, all sides <= 1 (Lemma 2): A1A3G(.498,.971,.975), A3GH(.743,.981),
     A3HJ(.849,.756), A3JA2(.634), A2JB(.9,.851), JBC(.9,.882), JCI(.6,.815), HIJ(.6,.849,.6),
     ICD(.9,.974), IDE(.9,.815), HIE(.882), HEF(.9,.851), GHF(.96,.743).
Count: the other 10 boxes each contain a point of P2, none of them A1,A2,A3 (inside X); nine points
B..J for ten disjoint boxes — contradiction. QED.
(Grid check 220^2 x 91: no P2-avoiding unit square found on the grid; but see 2.5.)

### 2.4 What kind of argument is this?
NOT a pure unavoidable-point-set argument (10 points unavoidable everywhere would give the bound
directly; P1 is not unavoidable at this s). It is a two-level case analysis:
  Case A: every box meets P1 -> <= 10 boxes.
  Case B: some box X avoids P1 -> X is a wall-hugger in an edge rectangle (Lemma 6 shows in fact
          tilt in [15.9°, 74.1°], centre height <= .776) and X ⊇ {A1,A2,A3} -> then P2 (chosen for
          that rectangle) gives <= 1 + 9 boxes.
Is it a fractional (measure) unavoidable set (I-L2)? I tried mu = (2/3) delta_P1 + (1/3) delta_P2
(mass 32/3 < 11): it fails, because P2 is adapted to ONE edge rectangle and the WLOG uses the
symmetry; symmetrising P2 costs too much mass (the four A-triples alone need mass 4 at weight 1/3,
and P1 then needs weight 2/3 -> 10.67 before adding anything that makes P1-hitting boxes reach 1;
grid check confirms mu(Q) = 1/3 for huggers in the other three rectangles). So the argument is
"conditional measures": a case split on the location of a P1-avoiding box, and a different
counting set per case. This is exactly the hybrid the coordinator asks about (LP for the bulk +
case argument at the walls): formally, a family of events E_0, E_1..E_4 covering all packings,
each with its own point set / measure and a "bonus" (X eats 3 points).

### 2.5 The hair-thin gap in Fig. 14 (recorded carefully)
Local checks (grid + Nelder–Mead, `check_stromquist.py` machinery) found a closed unit square with
centre (0.6427, 1.3750), tilt 69.67°, that avoids all 12 points of P2 *as literally listed* and
the wall x=0, each with margin ~1e-4 (A1 and G lie 1e-4 outside its boundary; wall slack 1e-4).
So a box of side 1.0001 avoiding P2 exists: P2 with G = (.8, 1.85) is not quite unavoidable.
Diagnosis: the region is the lower-left quadrilateral (0,.9),(1,.9),G,(0,1.85), which is a Lemma 4
region with (a,b) = (.95,.8), and f(.95) = .7982 < .8 — Lemma 4's hypothesis fails by .002 there.
(Not an error in my reconstruction: the quad and its parameters are forced by the listed
coordinates; the region does not appear in the paper's text, only in Fig. 14, and the paper gives
no parameters for it.) It is NOT a flaw of the method and Stromquist explicitly says "the argument
in Figure 14 is not rigid; any point could be moved by a small amount". Fix: G' = (.78, 1.845):
then the two left quads have (a,b) = (.945,.78) and (.944,.78) with f ≈ .81 > .78, all
G'-triangles keep sides <= 1 (|A1G'| = .970, |FG'| = .969, |G'H| = .764, |A3G'| = .985), and the
local search finds no escaping unit square (best min-margin -0.0000, at a degenerate axis-parallel
wall-touching position). Also the erratum in the f-table (Section 1) is real but harmless.
Moral for the computer-checked version: NEVER trust the tabulated lemma parameters; check (*)
directly for every region.

---------------------------------------------------------------------------------------------------
## 3. Where 2 + 2 sqrt(4/5) comes from; slack; what would have to change

### 3.1 The binding configuration
The 3-4-3 lattice: rows at y = 1, s/2, s-1 (rows at distance 1 from the walls so that Lemma 1
handles the corners), equal x-spacing d = s/2 - 1 in every row, middle row offset d/2. Legs of the
triangles = sqrt(d^2/4 + d^2) = d sqrt5/2 <= 1  <=>  d <= 2/sqrt5  <=>  s <= 2 + 4/sqrt5.
So the bound is exactly "the largest s for which the 3-4-3 lattice has unit legs", i.e. Lemma 2 is
tight on all 12 triangles simultaneously and Lemma 4's hypothesis |(a,b)-(0,1)| <= 1 is tight on
the 4 side quads (same segment). Everything else has slack:
  Lemma 6 apex height 1.12 vs 1.1277 (.008); Lemma 4 at (a,b)=(.894,.9): .0145 (with the corrected
  f); P2 triangle sides <= .985; Lemma 3 in the bottom rectangle: 2.694 vs 2.828; the counting
  itself: 1 + 9 < 11 has no slack, but the "X eats 3" step has slack (X actually contains a whole
  neighbourhood of the A's).
For the 45° theorem the same lattice with the 45°-component condition (dx+dy)/sqrt2 = 1 gives
dy = 2 dx = 2sqrt2/3, s = 2 + 4sqrt2/3 = 3.8856.

### 3.2 Pushing the same skeleton to 3.80 / 3.82 / 3.85
At s = 3.80: d = .9, legs 1.006 > 1. Lemma 2 fails on all 12 triangles: a box tilted parallel to a
leg (26.6° mod 90°), straddling the leg line at perpendicular offset p in (.195,.5) toward the apex,
with its unit window shifted by u in (0,.006) along the leg, has centre inside the triangle and
avoids all three vertices (elementary computation in the triangle (1,1),(1.9,1),(1.45,1.9)). Such
escapes form a 4-parameter family per leg (very thin in u and in tilt: within ~6° of the leg
direction). They are all wall-independent, so the second-stage argument would need many more
"cases" (each escape family must be shown to eat >= 2 points of a modified P2, and the count
|P2| - (#eaten) <= 9 must survive). At 3.82: legs 1.017, u-window .017, tilt window ~10°; at
3.85: legs 1.034, plus the edge rectangles widen to .925 and even P2's own Lemma-4 quads
(a = .925, b = .9 needs f(.925) = .857 < .9) fail — the P2 configuration itself would need
redesign. Also, lowering the bottom row (to catch wall-huggers) lengthens the legs; raising it
does the reverse: for a lattice-like first stage the balance is  hugger-condition
  d <= 2(sqrt2 - h)  vs  leg-condition  d^2/4 + (s/2 - h)^2 <= 1  (h = row height),
whose best simultaneous solution is s ≈ 3.74 (h ≈ .98) — i.e. a *pure* 10-point 3-4-3 set is
worse than 3.7889; Stromquist's second stage buys ≈ .05. Beyond ~3.80 the skeleton needs a
qualitatively different first stage (see Section 5).

---------------------------------------------------------------------------------------------------
## 4. Theorem 1 (s(10) = 3 + 1/sqrt2) and Theorem 3 (45° packings of 11), briefly

### 4.1 s(10) = 3 + 1/sqrt2 = 3.7071 (tight; four optimal packings, Fig. 1: 1,2,3,4 squares on the diagonal)
Ten points (Fig. 8): A=(1,1), G=(s-1,1), C=(1,s-1), E=(s-1,s-1); B=(.97,s/2), F=(s-.97,s/2),
H=(s/2,.97), D=(s/2,s-.97); I=(1.4,s/2), J=(s-1.4,s/2). Regions: corners (Lemma 1); the 8 edge
regions by Lemma 4 with a = s/2 - 1 = 1/2 + 1/sqrt8 = .8536, b = .97 <= f(.8536) = .972 (margin
.002!); interior triangles ABI, AIH, IHJ, HJG, CBI, CID, DIJ, DJE, EJF, FJG (Lemma 2; |IH| = .993).
So the 10 points are unavoidable and 10 boxes each contain EXACTLY one; name the boxes A-box…J-box.
The proof then exploits exclusivity ("named boxes"), which is beyond any measure argument:
 1. {A, B', C..J} with B' = (.75, s-1.96) = (.75,1.747) is still unavoidable (Lemma 4 with
    a=.96, b=.75 on the two left quads (0,s-1)–C–B' and (0,.787)–A'–B' … see Fig. 9) => B' in B-box.
 2. {A', A'', B', C..J} with A' = (1, s-2.92) = (1,.787), A'' = (1.2, 1) unavoidable => A-box
    contains A' or A''.
 3. If A'' in A-box: {A, A'', B', C..G, I, J, (2,1)} unavoidable (Lemma 3 used) => H-box contains
    H' = (2,1) (all other points are in other boxes).
 4. If A' in A-box: by convexity the A-box contains segment A'A ⊇ (1,.788)–(1,1), denied to the
    H-box, as are B..G, I, J; the partition of Fig. 11 + Lemma 5 forces the H-box's centre into
    Lemma 5's pentagon and hence to meet the segment (2,1)–(2.12,.9).
 Either way the H-box contains a point (*) of that short segment; by symmetry 8 asterisks (two on
 each of the B-, D-, F-, H-boxes), each within 1 of the centre and of its two neighbours. The 13
 points {8 asterisks, A, C, E, G, centre} are unavoidable (Lemma 2 triangles); all but the centre
 are in the eight named boxes, so the I- and J-boxes must both contain the centre — impossible.
Reusable pieces: Lemma 4 with (a,b) = (.8536,.97), the "named boxes + convexity denial + iterated
unavoidability" technique (a genuinely stronger tool than measures for tight cases), Lemma 5.

### 4.2 Theorem 3: 0°/45° packings of 11 need s >= 2 + 4sqrt2/3 = 3.8856 (Hämäläinen's packing, Fig. 3)
Same 10 points as Fig. 13 with the new s (rows at 1, s/2, s-1; d = 2sqrt2/3 = .943; legs
sqrt(10/9) = 1.054 but 45°-components exactly 1 => Lemma 7 applies to all triangles). A 0° box
cannot avoid the points; a 45° box avoiding them must sit in an edge rectangle (Fig. 13) and
contains A = (1,s-3)=(1,.886), (s/2,s-3), (1.5,1.3); the 12-point set B=(s-1,1), C=(s-.8,s/2),
D=(s-1,s-1), E=(s/2,s-.8), F=(1,s-1), G=(.8,s-2), H=(1.7,2.2), I=(2.2,2.2), J=(2.2,1.7) + the A's
is unavoidable for 0°/45° boxes (Lemmas 7, 8) => contradiction as in Theorem 2. This proves
Gardner's conjecture (n = 11 is the first n needing a non-45° tilt) since 3.8856 > 3.8772.
Reusable: the *structural* corollary — every 11-packing with side < 3.8856 contains a box tilted
at neither 0° nor 45°. Same skeleton could give "every 11-packing with side < s0 contains a
wall-hugging box tilted in [16°,74°] in the middle third of an edge" for s0 slightly above 3.7889.

---------------------------------------------------------------------------------------------------
## 5. Stromquist's own remarks; his view of the truth
He gives no conjecture on the value of s(11). He calls Trump's 3.8772 packing "the most efficient
known", says the Fig. 14 argument "is not rigid; any point in the figure could be moved by a small
amount in almost any direction without causing the argument to fail. The critical distances are
all in Figure 13" (i.e. he knows the binding constraint is the unit legs of the lattice), and that
the results were first obtained in 1984 memoranda. Nothing about limitations of the method beyond
that; the paper is deliberately a hand proof "with extra margin of size".

---------------------------------------------------------------------------------------------------
## 6. Assessment

### 6.1 Can a pure 10-point unavoidable set beat 3.7889 for n = 11?  My heuristic answer: NO (max ≈ 3.72–3.76).
Constraints on any 10-point unavoidable set P at s ≈ 3.79:
 * Axis-parallel boxes alone force ~9 points into a 3x3 pattern: the nine pairwise disjoint unit
   squares [0,1],[(s-1)/2,(s+1)/2],[s-1,s] (products) each need a point (s > 3), and sliding them
   forces one point in each corner square, one in the middle third of each edge strip, one near
   the centre; with 10 points the only patterns are 3-3-3(+1) or 3-4-3 (a 4-2-4 pattern misses the
   left/right mid-edge axis-parallel squares).
 * Wall-huggers (vertex on a wall, tilt theta): the chord at height y of the corner point coverage
   ends at t = 1.414 (45°) from the corner; the middle t-range (length ≈ .96 per edge) must be
   covered by ONE mid-edge point at height h; 45° huggers need h <= ~.93 (2(sqrt2-h) >= d and the
   asymmetric 30°/60° margins), raised 45° boxes and Lemma-2 coverage of the interior strip need
   h >= 1 (legs <= 1). Explicit escaping box for h = .9: vertex (1.3,.6), tilt 30° avoids (1,.9),
   (1.894,.9), (1,1)-corner, (1.447,1.894), (.553,1.894). Balancing the two conditions
   (Section 3.2) gives s ≈ 3.74. Two free points cannot patch 8 symmetric holes.
 So the pure method is dominated by Stromquist's two-stage argument, and A05 should not expect to
 beat 3.7889 with 10 points (a rigorous 10-point certificate at ~3.74 would still be valuable as
 an interval-arithmetic warm-up).

### 6.2 Can the first stage be re-optimised, with the exceptional rectangles handled by a similar case argument?
Yes in principle, and this is the most promising "Stromquist-style" route beyond 3.7889:
 * First stage: a 10-point set P1' that is unavoidable EXCEPT on a small set of exceptional
   regions R (not necessarily rectangles), at s' > 3.7889. The optimiser's objective is not
   "unavoidable" but "the exceptional region R is small and its boxes are highly constrained"
   (all boxes centred in R must contain >= 3 points of some P2', or >= 2 points of a P2' with
   |P2'| <= 10, or generally: |P2'| - (#forced) <= 9). Since escapes at s = 3.80 with the lattice
   are of two kinds (edge huggers, thin leg-parallel families), one may instead abandon the
   lattice: e.g. bottom row at height h ≈ .95, middle row not horizontal, corners moved inward.
 * Second stage: for each exceptional region R_i, a set P2^{(i)} unavoidable in S with the forced
   points; counting: 1 + (|P2^{(i)}| - k_i) <= 10.
 * This is a finite-dimensional search: parameters = coordinates of P1', P2^{(i)}; constraints =
   coverage statements of the form (*), all checkable by (x,y,theta) branch-and-bound. It is
   strictly more flexible than a single measure (it uses the disjointness of boxes: the eaten
   points are unavailable to the others), but the LP (A07) is more flexible in another direction
   (fractional weights). The natural COMBINATION: for each case E_i, an LP measure mu_i with
   mu_i(Q) >= 1 for all Q and total mass < 11 + (mu_i(X) - 1) where X is the exceptional box —
   i.e. "conditional LP": min mass(mu) s.t. mu(Q) >= 1 for all Q, and mu(Q) >= 1 + beta for all
   Q centred in R_i, with objective mass < 11 + beta. Since a hugger's centre region R_i is small
   and the hugger provably contains three fixed points, beta can be as large as 2 (Stromquist).
   Concretely for A07: add to the LP the constraint family "mu(Q) >= 3 for huggers in R_i" is
   NOT valid in general (it must hold for the packing's exceptional box, not for all boxes); the
   correct formulation is per-case: LP_i: min mass s.t. mu(Q) >= 1 ∀Q, mu(Q) >= 1 + beta ∀Q with
   centre in R_i and Q ∩ P1' = ∅; bound: 11 boxes have mass >= 11 + beta > mass  ⇒ contradiction.
   Case E_0 (no box avoids P1'): needs |P1'| = 10 (or an LP mu_0 with mass < 11 restricted to
   boxes meeting P1' — again a valid LP: mu_0(Q) >= 1 only for Q meeting P1'). This "case-LP" is a
   clean, certifiable generalisation of both A07 and Stromquist and, I think, the best next step.
 * The 45° corollary suggests another cheap structural case split for the LP: tilt-restricted
   LPs (mu(Q) >= 1 only for Q with tilt in a set Theta_j), combined with "every packing has a
   box with tilt in Theta_j" statements proved separately.

### 6.3 Which idea in docs/ideas.md is best positioned
 I-L2 (LP/measure) — already at tau*(3.80) ≈ 10.4 per A07 — is the workhorse; Stromquist's
 argument shows the two ingredients the LP is missing: (i) case splits using symmetry (choose the
 measure after locating an exceptional box), (ii) exclusivity/named-box reasoning (Theorem 1). Both
 can be grafted onto the LP as "case-LPs" (6.2). I-L5 (structure theorems) is the supplier of the
 cases (e.g. "some box hugs an edge with tilt in [16°,74°]", "some box is not at 0°/45°"). I-L1
 (pure points) is dominated. I-L4 (full B&B) only for the last mile.
 New idea (clique constraints): the LP dual allows fractional packings that put weight 1/2 on
 three pairwise-overlapping boxes with no common point; adding clique inequalities
 (sum of y_Q over any family of pairwise-overlapping boxes <= 1) tightens tau*. Cliques not of
 point type exist for rotated squares (e.g. three boxes centred at the vertices of a triangle of
 side .99 whose diagonals avoid the centroid). Primal side: cover elements = cliques, still an LP,
 still certifiable (pairwise overlap is an exact algebraic check). Worth a quick experiment in A07.

### 6.4 What a computer-checked version of Stromquist's Theorem 2 looks like
 Finite exact-arithmetic parts (rational/algebraic, decidable by hand or `decide`):
  - the coordinates (all in Q(sqrt5)); the partition of S into regions (polygons with these
    vertices); the counting arguments (Cases A/B, 1 + 9 < 11); the WLOG symmetry (Klein group).
 Parts needing interval arithmetic in (x, y, theta) — each is an instance of (*):
  - Lemma-1/2/3/4/6 instances: for each region R (polygon) with its point set P and wall(s):
    for all theta in [0, 90°) and all centres in R: box crosses a wall or contains a point of P.
    ~1 + 4 + 12 + (P2: 4 + 8 + 13) ≈ 45 instances for Theorem 2 (or just two global checks:
    "P1 unavoidable outside R4" and "P2 unavoidable", plus "every P1-avoiding box centred in R4
    contains A1,A2,A3" — three 3-D coverage checks over the whole square, no lemmas needed).
  - Recommended: skip the lemmas entirely and certify the three global statements by branch-and-
    bound over boxes (x,y,theta) with rational bounds on cos/sin — this is I-C2 and matches A05's
    verifier. Boundary convention: verify with closed unit squares strictly inside the open
    container ⇒ implies Stromquist's box statement.
  - The G-quad hair (2.5) is a warning: margins in P2 are 1e-4..1e-2, so use G' = (.78,1.845) or
    re-optimise P2 for margin before certifying.
