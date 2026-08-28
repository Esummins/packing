# A40 — the surgery lemma and basin growth by boundary surgery (Fable, lead; 2026-08-28)

Goal: grow Trump's certified exclusion region from A36's box(z-hat, h0), h0 = 37/10000 · 10^-1
= 3.7e-3, toward h ~ 0.03, crossing ONLY the boundaries that actually bind.  Everything below is
anchored at A22's rational z-hat (34 coordinates: x_i, y_i, theta_i for the 11 squares, s last,
S_IDX = 33) and A22's certified strict local minimality on box(r_N), extended by A36 to
box(3.7e-3).  Rigour tags as in the lab: [IV] mpmath.iv dps 60, [EX] exact rational, [LP]
float64 design only (never load-bearing).

Notation.  For a candidate separating axis a = (o, e, p) (owner square o, owner edge e, other
square p) and corner k of p, the sep row is

    g_{a,k}(z) = n_e(theta_o) . (q_k(p) - c_o) - 1/2 ,

and (t_k, d_k) are corner k's owner-frame coordinates: t_k the tangential coordinate along edge
e, d_k = g_{a,k} the depth beyond the edge line.  The axis gap is gap_a(z) = min_k d_k(z).  A
row is VALID on a set L if g(z) >= 0 for every FEASIBLE z in L (feasible = interiors pairwise
disjoint, all squares inside [0,s]^2).  Wall rows (corner-inside-container) are valid on
everything, [EX] by the definition of feasibility.  The two aux dist rows d^2(c_i,c_j) - 1 >= 0
for the flush pairs are globally valid (incircle argument, A35/M1b).

## S1 (pointwise [V]-validity; the A37 rule, proved)

LEMMA S1.  Fix z with the pair (o, p) interior-disjoint.  If |t_k(z)| < 1/2 and
d_k(z) > -1/2, then d_k(z) >= 0.

Proof.  In owner o's frame the open square o is {(t, d) : |t| < 1/2, -1 < d < 0} (d measured
from edge e's line, depth positive outward).  If -1/2 < d_k < 0 and |t_k| < 1/2 the corner q_k
of p is an interior point of o, so the interiors of o and p meet (q_k is interior to p's closed
square? no: q_k is a BOUNDARY point of p — but a boundary point of p interior to o implies, by
openness of int(o), a neighbourhood of q_k inside int(o), and every neighbourhood of a corner of
p meets int(p); hence int(o) ∩ int(p) != {}) — contradiction.  So d_k >= 0 or d_k <= -1/2; the
hypothesis d_k > -1/2 leaves d_k >= 0.  QED

CONSEQUENCE (the [V]-check).  If over a region L (interval-enclosed) sup_L |t_k| < 1/2 and
inf_L d_k > -1/2, the row is valid on L.  [IV]  This needs no SAT selection, no dominance, and
no information about which axis separates.

## S2 (over-estimate; A36 L1.1 restated)

LEMMA S2.  For every z and every corner k:  g_{a,k}(z) >= gap_a(z).  In particular if axis a
separates the pair at z (gap_a(z) >= 0) then ALL FOUR corner rows of a are >= 0 at z.

Proof.  The owner's support along its own outward edge normal is n . c_o + 1/2 exactly, so
g_{a,k} = n.q_k - (n.c_o + 1/2) and gap_a = min_k over p's corners of the same quantity.  QED

## S3 (axis disjunction with kills, on a region)

LEMMA S3.  Let L be a region and (o, p) a pair.  Call axis a KILLED on L if for some corner k,
sup_L g_{a,k} < 0 ([IV]; then sup_L gap_a < 0 by S2, so a separates nowhere on L).  Let
Alive(L) be the non-killed axes among the 8 of the pair.  Then every feasible z in L satisfies
the disjunction  OR_{a in Alive(L)} (gap_a(z) >= 0),  and on the branch of axis a all four
corner rows of a are valid (S2).

Proof.  Separating-axis completeness for convex polygons (as used by drain lemma D3' and A36
L1.2): two interior-disjoint squares are separated (weakly) by a line parallel to an edge of one
of them, i.e. some axis among the 8 has gap >= 0.  Killed axes cannot.  QED

Note the branches OVERLAP (a z may be separated by two axes); overlapping covers are harmless
for the composition (S6) — every feasible z lies in AT LEAST one branch.

## S4 (rows valid without branching)

LEMMA S4a (safe axis; gained contacts).  If inf_L gap_a >= 0 ([IV]) then all four corner rows
of a are >= 0 on ALL of L (feasible or not), by S2.  This is how a pair NOT in contact at z-hat
enters the basis while the box is small: its near axis stays separating across the whole box,
its rows are valid inequalities with g(z-hat) = gap > 0, and NO case analysis is introduced.
When the safe margin dies (box big enough that the pair can touch), the pair graduates to S3
like any contact pair.

LEMMA S4b (forced axis).  If ALL axes of the pair except one, say a*, are killed on L, then for
every feasible z in L axis a* separates, and its four corner rows are valid on L — no branch
needed (the disjunction of S3 has a single disjunct).

## S5 (the anchor / exclusion certificate on a shell region)

This is the workhorse that replaces the (V') dichotomy OUTSIDE the already-certified core.  It
needs no pin, no Krawczyk contraction, no beta < 1 — the three quantities that capped A36's
reach at 3.78e-3 simply do not appear.

Setting.  Let h_in < h_out, i in {0..33}, sgn in {+1, -1}, and let the FACE REGION be
    L = { z : ||z - z-hat||_inf <= h_out,  sgn (z_i - zhat_i) >= h_in },
possibly further restricted by finitely many affine TIE CUTS c_m(z) >= 0 with exact rational
coefficients and values v_m := c_m(z-hat) (the FACE cut c_0(z) = sgn (z_i - zhat_i) - h_in has
v_0 = -h_in exactly; a tie cut  +-(l(z) - l(z-hat)) - tau  on a functional l, e.g. the relative
angle theta_a - theta_b of a flush pair, has v = -tau on its anchor side and v = +tau on the
complementary side; the two sides cover).  Every cut is valid on its region BY CONSTRUCTION.

THEOREM S5 (anchor certificate).  Let R be a set of rows valid on L (via wall/S1/S3-branch/
S4/aux/S7-floor), omega_r >= 0 (r in R), omega_m >= 0 on the cuts, all rational.  Put
W(z) = sum_r omega_r g_r(z) + sum_m omega_m c_m(z).  Let, with all bounds [IV] over
box(z-hat, h_out)  (a superset of hull(L ∪ {z-hat})):

    V0    >=  sum_r omega_r g_r(z-hat)                     (signed! interval sup)
    CV    =   sum_m omega_m v_m                            ([EX] exact rational)
    eps_w >=  || A(z-hat)^T omega + sum_m omega_m grad c_m - e_s ||_1
    Hbar  >=  (1/2) [ sum_{a != b} sup |H^W_ab|  +  sum_a max(0, sup H^W_aa) ],
              H^W := Hess(sum_r omega_r g_r)  ACCUMULATED as one interval matrix
    MARGIN := -CV - V0 - eps_w h_out - Hbar h_out^2 .

If MARGIN > 0 then every feasible z in L has  s(z) >= s-hat + MARGIN > s-hat.

Proof.  Phi := s - W.  grad Phi(z-hat) = e_s - A^T omega - sum omega_m grad c_m, so
||grad Phi(z-hat)||_1 <= eps_w.  The cuts are affine, so Hess Phi = -H^W, and Taylor with
integral remainder along the segment z-hat -> z gives
    Phi(z) >= Phi(z-hat) - eps_w h_out - inf-bound of (1/2) d^T H^W(xi) d
with (1/2) d^T H^W d <= (1/2)[ sum_{a != b} sup|H_ab| |d_a||d_b| + sum_a (sup H_aa)^+ d_a^2 ]
<= Hbar h_out^2  (off-diagonal entries bounded by magnitude; a diagonal entry contributes to
an UPPER bound of the quadratic form only through its positive part, since d_a^2 >= 0 -- the
signed-diagonal refinement; accumulating H^W as one interval matrix before taking magnitudes
keeps the cross-row cancellation, ~20-25 % of the mass in practice).  At the anchor,
W(z-hat) = sum_r omega_r g_r(z-hat) + CV <= V0 + CV, so Phi(z-hat) >= s-hat - V0 - CV.  For
feasible z in L every loaded row is >= 0 and every c_m(z) >= 0, so W(z) >= 0 and
    s(z) = Phi(z) + W(z) >= s-hat - CV - V0 - eps_w h_out - Hbar h_out^2 .  QED

THEOREM S5' (leaf emptiness).  Same setting, omega_r >= 0 on rows valid on L, no cuts loaded.
If  V0 + eps'_w h_out + Hbar h_out^2 < 0, where now eps'_w >= ||A(z-hat)^T omega||_1 (no e_s),
then L contains NO feasible point.  Proof: the same Taylor bound applied to U := sum omega_r
g_r gives sup_L U <= V0 + eps'_w h_out + Hbar h_out^2 < 0, while feasibility of z in L forces
U(z) >= 0.  QED  (This is the workhorse for deep branch combinations: several branch-axis rows
with strictly negative anchor values certify the combination's region empty.)

Remarks.  (i) The certificate is STRICT (margin > 0), so composition preserves "equality only
at z-hat".  (ii) Rows with g_r(z-hat) < 0 (branch-axis rows of a non-separating alive axis,
e.g. the second axis of a near-corner-corner pair, g(z-hat) ~ -(1/2 - |t|)) make V0 MORE
negative: they are additional anchors, free of charge — the certificate gets stronger exactly
on the branches that move away from the contact structure.  (iii) A trivially-empty face
(EMPTINESS certificate) is the degenerate case: if some valid row has sup_L g < 0 ([IV]) then
L contains no feasible point at all; used verbatim for the faces that push a wall-touching
square through its wall.  (iv) The s+ face needs nothing: on it s - s-hat = d_s >= h_in > 0.

## S7 (floor-shifted rows)

LEMMA S7.  For any row g and any [IV]-certified lower bound  lb <= inf_{box(h_out)} g,  the
shifted row  g' := g - lb  satisfies g' >= 0 on the WHOLE box — for every z, feasible or not.
So g' may be loaded in S5/S5' unconditionally, with anchor value g'(z-hat) = g(z-hat) - lb
(>= 0), gradient and Hessian equal to those of g.  Proof: immediate.

Use: a selection-conditional row (endpoint corner row, wrong-branch alternate, gained-pair
row) whose true validity would cost a branch can instead be bought outright for the value
premium |lb| ~ (l1 gradient) * h_out.  The LP decides per face which is cheaper; this
collapses most of the branch demand ("branch only binding rows" made literal: a pair is
branched only when the LP finds the floor premium too expensive).

LEMMA S7' (relative floors).  Two corner rows of the same axis a = (o, e, p) differ by an
exact one-dimensional trig function of the relative angle:
    g_{a,ka} - g_{a,kb} = nhat_e . R(theta_p - theta_o) (h_ka - h_kb) =: f(delta).
If the sibling g_{a,kb} is pointwise-[V]-valid on the region (S1), then for every feasible z
    g_{a,ka} >= f(delta) >= lb_rel := inf f over the delta-interval,
where the delta-interval is +-2 h_out around its z-hat value, INTERSECTED with any tie cut of
the leaf on the same angle pair.  The endpoint corner row of a flush pair (the torque-couple
arm, [V]-invalid because |t| ~ 0.83) is thereby loadable at premium -lb_rel ~ sin(2 h_out)
box-wide, and ~ sin(tau) on the tau-side of a tie cut on that pair's relative angle -- an
order of magnitude cheaper than the absolute floor, and the mechanism that keeps the flush
pairs' force couples available across selection switches.  Proof: the identity is exact (the
-1/2 and the owner-support terms cancel in the difference); the rest is S7.  QED

## S6 (composition: branch tree x rings)

THEOREM S6 (basin growth).  Let h_0 < h_1 < ... < h_K and suppose:
 (i)  sigma >= s-hat on box(z-hat, h_0), with equality iff z = z-hat  [A36 composed theorem];
 (ii) for every ring k (0 <= k < K) and every face (i, sgn) with the face region
      L^k_{i,sgn} = {||d||_inf <= h_{k+1}, sgn d_i >= h_k}  (the s+ face excepted per S5(iv)),
      there is a finite family of pairs with S3 branch disjunctions on L^k_{i,sgn}, and a
      finite binary tree of tie-cut splits (each split's two closed sides cover), such that
      every resulting leaf carries an EMPTINESS certificate (single-row sup < 0, or S5'), or
      an S5 anchor certificate with MARGIN > 0, whose loaded rows are valid on the leaf by
      S1/S3/S4/S7/wall/aux ([IV] checks).
Then sigma >= s-hat on box(z-hat, h_K), with equality iff z = z-hat.

Proof.  Induction on k.  Any z in box(h_{k+1}) \ box(h_k) has ||d||_inf > h_k, so sgn d_i >=
h_k for some coordinate face, i.e. z lies in some face region (closed cover).  If z is
feasible, applying S3 to each of that face's branched pairs yields, for each, a separating
alive axis; the product choice selects a branch combination b containing z.  By the emptiness
or S5 certificate on L ∩ b, s(z) > s-hat (emptiness: z cannot exist).  With the inductive
statement on box(h_k), sigma >= s-hat on box(h_{k+1}) and equality still forces z in box(h_0),
hence z = z-hat.  QED

The certificates compose over an arbitrary DAG of overlapping regions; rings-by-faces is the
shape the loop uses because the cut then has exact rational value -h_k at the anchor and the
branch count stays multiplicative only in the pairs the LP actually loads (the brief's
"branch only binding rows").

## What binds, measured (results/margins.json, ceiling.json)

 - M1: per-row [V]-death of the 16 A22 edge rows: rows 16 (E4c1-7e2, |t| = .479) at h = .0052;
   rows 27/28/30/33 (|t| = .475) at .0057; row 13 at .0061; rows 26/29/31/35 (|t| = .381) at
   .0272; the rest at h > .06.  These are the surgery targets, in order.
 - M2: every contact pair keeps 1-2 alive axes up to h = 0.03 ((1,3): 4): branch factor per
   surgered pair is 2 (4 for (1,3)), and does not grow before 0.03.
 - M3: gained pairs: (6,7) and (8,9) at gap .0249 (safe to h ~ .005-.006), (3,4) at .0326
   (safe to ~ .011), (7,10) at .1188 (safe to ~ .022).  Beyond safety they graduate to S3.
 - M4/ceiling: with the universal rows alone the thin-ring anchor saturates at h ~ .0047
   (binding face sq6.theta-)); with the surgery-enriched arsenal (branch rows + gained rows)
   the design LP ceiling is > 0.2 on every face — the cone is not the obstruction; the honest
   obstructions are per-branch validity and the interval constants, i.e. exactly what the
   growth loop certifies.

## The saturation mechanism (measured; the honest wall)

The anchor certificate sustains ring growth at radius h iff, on every leaf, some multiplier
choice has  omega_b > 2 Hbar_leaf h  (thin-ring limit of MARGIN > 0), where omega_b is the
face-direction growth rate expressible in the leaf's valid cone and Hbar_leaf ~ 4-8 the
accumulated Hessian mass.  Measured rates:
 - the full near cone (all couples available): omega_b ~ 0.16 for the theta faces -> ceiling
   ~ 0.16/(2*8) ~ 0.010-0.020;
 - the WORST leaf (a flush pair in its switched selection with the couple arm lost, e.g. face
   sq6.theta-, all-near branches, (6,9) separated by 9's own edge, relative tilt past the tie
   cut): omega_b ~ 0.052 = 1/kappa_eff(A22) -- the same constant as A36's pin, reappearing as
   the worst-leaf growth rate -- ceiling  0.052/(2*Hbar) ~ 0.0065.
S7' + tie cuts restore the couples on the tau-side regions; the anchor-side slivers (relative
tilt >= tau) keep the 0.052 rate and are the genuine saturation faces of this certificate
form.  Passing them needs either curvature exploitation beyond the |Hessian|-mass Taylor bound
(the remainder is signed; only the diagonal positive-part refinement is currently taken) or a
recentred expansion point inside the sliver -- both left as levers.

## The growth loop (T2 contract)

Per ring [h_k, h_{k+1}] and face: (E) emptiness else (A) anchor-LP over unconditionally valid
rows (wall + [V]-alive + S4-safe/forced + aux) else branch the loaded conditional pairs (S3,
product over alive axes) and emit per-branch anchors.  Every emitted certificate is [IV]-
checked (V0, eps_w, Hbar, kills, [V]/safe margins for every loaded row, margin > 0) and
re-checked by the standalone corruption-gated checker (a40_check.py).  Ring ratio adapts to
the margin; saturation = some face x branch where no admissible omega has MARGIN > 0 at the
smallest acceptable ring ratio — reported with the face, the branch, and the LP dual's
binding rows.
