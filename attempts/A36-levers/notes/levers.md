# A36 — the two levers (Fable, lead; 2026-08-27)

Goal (PI): make the v2 escape-complex theorem STRICTLY DOMINATE A22 — composed radius h > r_N
= 1/2000 — by discharging L1 (endpoint-row validity) and L2 (omega-scale reach). Builds directly
on A35 (attempts/A35-escape-complex/: theory.md, m1b/m2b/m3b reports, certificate stores).

## L1 — the branch-disjunction lemma (endpoint rows made box-valid)

### L1.1 Over-estimate principle (one line, load-bearing)

For an owner edge e of square o with outward unit normal n(theta_o), the TRUE axis gap of pair
(o,p) along e is  gap_e(z) = min_{k=0..3} n.(q_k(p)) - (n.c_o + 1/2)  (the owner's support along
its own outward edge normal is n.c_o + 1/2, exactly). The sep row with ANY corner k satisfies

    g_{e,k}(z) = n.(q_k(p) - c_o) - 1/2  >=  gap_e(z).

CONSEQUENCE: if the axis e SEPARATES the pair at z (gap_e(z) >= 0) then ALL FOUR corner rows of
that axis are >= 0 at z. Dominance rows are needed only for the converse direction (S-feasible =>
disjoint), which barrier certificates never use. So barrier validity of an endpoint row needs
exactly M2b-a's weaker condition — "the owner edge separates the pair on the box" — and nothing
about dominance/ties. This kills the tie-menu dependence of the VALUE layer entirely.

### L1.2 Branch-disjunction lemma (per repaired contact, on box(z-hat, h))

Let z in box(z-hat, h) be FEASIBLE (interior-disjoint packing). By separating-axis completeness
for convex polygons (already used by drain_lemma D3'), some edge normal of one of the two squares
separates each pair. For the three repaired contacts the candidate (axis, side) combinations are 8
each; all but the listed branches are IMPOSSIBLE on box(h) by interval-certified projection
overlap/order (margins ~1, so any h <= 0.1 works; certify at the target h):

- pair (0,1) (flush, side-by-side along x): impossible: separation along either square's y-ish
  axes (y-projections overlap by ~1), and x-separation with sq1 on the LEFT (centre order).
  BRANCHES: A01a = sq0's right edge separates; A01b = sq1's left edge separates.
- pair (0,3) (flush, stacked along y): symmetric. BRANCHES: A03a = sq0's top edge; A03b = sq3's
  bottom edge.
- pair (1,3) (corner-corner, sq3 up-left of sq1): impossible: sq3 right of sq1, sq3 below sq1,
  sq1 left of sq3, sq1 above sq3 (centre order both axes). BRANCHES: B13x = sq1's left edge,
  B13x' = sq3's right edge, B13y = sq3's bottom edge, B13y' = sq1's top edge.

LEMMA L1 (disjunction). On box(z-hat, h) with the above interval checks certified, every feasible
z satisfies: (A01a or A01b) and (A03a or A03b) and (B13x or B13x' or B13y or B13y'), where each
branch condition is "that axis separates", hence by L1.1 all four corner rows of the branch axis
are >= 0 at z. Proof: SAT completeness + elimination of the impossible combinations. QED

### L1.3 Consequences for the certificate architecture

- BASIS v3 = v2's 42 rows + 2 new rows for the (1,3) missing branches (B13x' = owner 3 right
  edge, B13y' = owner 1 top edge) = 44 rows. (Branch rows for the flush pairs: v2's F0-1a/b,
  F0-3a/b are exactly A01a/A01b/A03a/A03b witnesses with specific corners; by L1.1 each branch
  may load ALL FOUR corner rows of its axis — the emitter may use the corner rows it likes.)
- VARIANTS: 2 x 2 x 4 = 16 branch combinations. Every feasible z in the box belongs to >= 1
  variant. A certificate family = one (V') barrier per variant, omega supported on: rows 0..35
  (validity from A22's own tangential margins >= 0.0148, certified per box), the aux dist rows
  a0, a1 (globally valid, active), and the selected branch's corner rows. Union over 16 variants
  covers the box. NO tie menus in the value layer. The composed theorem needs: 16 (V')-style
  certificates + the dichotomy/pinning step + A22's finish.
- The (W')/FJ layer (only needed if L2 leaves reach short and the alive family must be walked
  per-stratum): menus survive there, but L1 removes the undischarged-description caveat: each
  variant's row system is certified valid, and FJ exclusion runs per variant.

### L1.4 What must be interval-certified (cheap, finite list)

Per pair, per box(h): (i) y-projection (resp. x-projection) overlap lower bounds > 0 for the
killed axes; (ii) centre-order bounds for the killed sides; (iii) A22 rows 0..35 tangential
margins > 0 on box(h) (A22 did this at r_N; re-do at the target h); (iv) the aux rows' global
validity is analytic (incircles), activity at z-hat exact (A35/M1b). That is the whole L1
obligation. Note h <= h_valid = 0.0052 remains a separate cap from A22's old-row margins — at
target h ~ 1e-3 it does not bind.

## L2 — reach-maximization of the universal barrier

The (V') dichotomy on box(h), per variant V with multiplier omega >= 0 supported on V's valid
rows R_V (A_ext^T omega = e_s):
  T(h) = (eps0 + eps_w(omega,h) h + Hbar(omega) h^2) / alpha_min(omega)
  case 1: G(z) >= T(h) => s >= s-hat;  case 2: all rows small => Krawczyk pin psi(h) <= r_N ->
  A22 finishes (iterated variant C).
Reach = max h with psi(h) < h chain closing. M2b evaluated this at the Chebyshev omega only
(h_G = 0.25-0.45 r_N). The legitimate freedom:
 (a) omega anywhere in the polytope {omega >= 0 on R_V, A_ext^T omega = e_s} — 8-dim self-stress
     freedom + the inequality slack; alpha_min, eps_w, Hbar are all convex/PWL functionals of
     omega, so "max reach" is a 1-d bisection over h with an inner LP feasibility problem:
       exists omega: alpha_min(omega) >= a, eps_w-bound(omega) <= b(h,a), Hbar-bound(omega) <= c
     with the interval data precomputed per row (Hessian norms ||H_r||, residual slopes). Solve
     the LP at each h; bisect.
 (b) the PIN system choice: the pin need not use A22's 34-row S (kappa = ||Y||_inf large); any
     [RFP]-certified square subsystem of v3 rows works; minimize kappa/(1-beta) over a few
     candidate bases (include the 33x33 load-bearing block from m1b + one aux row).
 (c) ring composition: if case-2's pin lands in [r_N, h] rather than <= r_N, iterate the whole
     dichotomy at the smaller radius (variant C logic, already in m2_check_inflation) — chain
     until <= r_N.
 (d) HYBRID (fallback if (a)-(c) stall below r_N): per-stratum (W') on the cone-alive family
     (free normalization alpha_min = 1 reaches 1.6-3.1 r_N measured) + (V') only as the
     high-codim blanket. Requires enumerating the alive family with aux + branch generators
     (Z0 ~ 20-21 rows) and per-stratum certs WITHOUT tie menus (L1) ~ 1-2 s each. Only if needed.

TARGET: composed h > r_N = 5e-4 strictly; stretch 1.6-3.1 r_N. HONEST FLOOR: if the optimum over
(a)-(c) still lands below r_N, report the number and the binding constant (expected binder:
eps_w's linear growth ~ the box residual slope of A^T omega - e_s, i.e. the Hessian norms of the
loaded rows — heavier omega on low-curvature rows is the main lever).

## Verification duties (lab standard)

Every emitted certificate: rational omega/y, [IV] dps 60 over the box, standalone re-checker
(no producer libs), corruption gates (omega-sign, h-big, drop-aux, drop-branch — a certificate
must FAIL if its branch's disjunction checks are removed while its rows keep omega > 0).
Lead re-verifies: L1 interval checks independently, one variant's barrier end-to-end, the reach
bisection's binding constraint.
