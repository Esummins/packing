# A22-local-rigidity — rigorous strict local optimality of Trump's 11-square packing

Owner: validated-numerics postdoc (A22). Date: 2026-08-20. Status: **done-success**.

## Headline

**Theorem (certified).** Let z0 be the rational 34-dimensional point obtained from A03's
60-digit coordinates of Trump's packing (11 centres + 11 angles + container side s, exact
decimal fractions), and let

    N = { z in R^34 : ||z - z0||_inf <= 5e-4 }.

Call z = (c_1, th_1, ..., c_11, th_11, s) **feasible** iff the 11 closed unit squares
Q_i(c_i, th_i) have pairwise disjoint interiors and are all contained in [0, s]^2.  Then:

1. (existence, uniqueness, rigidity) The 34-equation contact system F (the curated
   subsystem S below) has EXACTLY ONE zero z-hat in N, and ||z-hat - z0||_inf <= 1e-50.
2. (structure) At z-hat: squares 0..5 are exactly axis-parallel with
   c0 = (1/2,1/2), c1 = (3/2,1/2), c3 = (1/2,3/2), c2 = (s-1/2,1/2), c5 = (s-1/2,s-1/2)
   exactly, and the five tilted squares share EXACTLY one common angle theta.
3. (feasibility) z-hat is itself a feasible packing; write s-hat = s(z-hat).
4. (strict local optimality) EVERY feasible z in N has s(z) >= s-hat, with
   **equality if and only if z = z-hat**.
5. (quantitative stability) every feasible z in N with s(z) <= s-hat + delta satisfies
   ||z - z-hat||_inf <= 155.7 * delta   (nu_max/(1-beta) = 57.006/0.3661).

s-hat agrees with the Ellsworth/A03 octic root 3.877083590022814177307897... to 1e-50
(octic(s-hat) is enclosed in +-3.1e-45); the exact algebraic identification is A03's
(PSLQ, not re-proved here — see "gaps").

This is the s -> s'^- endgame theorem of the optimality programme: no packing in an
explicit 34-dimensional neighbourhood of the Trump configuration does better, and
near-optimal packings in N are pinned to within 156*delta of it.

Everything is verified by a standalone interval-arithmetic re-checker
(`recheck.py`, mpmath.iv only) from a single JSON artefact
(`results/krawczyk_cert.json`); four corruption gates fail as required.

## 1. The curated constraint system

Variables z[3i..3i+2] = (cx_i, cy_i, th_i), z[33] = s.  From A03's 56 contact equations
we curate 38 smooth constraints g_k(z) >= 0, ALL active (= 0 to 6e-60) at z0:

* 20 **wall** rows: corner coordinate >= 0 (walls x=0, y=0) or s - corner coordinate >= 0
  (walls x=s, y=s), for the corner-on-wall contacts.
* 16 **edge** rows: for each contact "corner q of square i in the INTERIOR of edge e of
  square j" (A03 at_edge_end = False), g = n.(q - c_j) - 1/2 with n the outward unit
  normal of edge e of square j.
* 2 **dist** rows: g = ||c_i - c_j||^2 - 1 for the flush upright pairs (0,1) and (0,3).

Intentionally NOT used: the 20 degenerate corner-at-edge-end rows of the flush upright
contacts, and the corner-to-corner pair (1,3).  Dropping constraints RELAXES the problem,
which is sound for a lower-bound/optimality statement.

**Validity lemmas** (feasible z in N  =>  g_k(z) >= 0):

* wall: containment, global, no conditions.
* dist: two unit squares with disjoint interiors have centre distance >= 1.
  Proof: separate the interiors by a hyperplane with unit normal u (convexity); the
  projection of a unit square onto u has half-width (|cos phi| + |sin phi|)/2 >= 1/2,
  so (c_j - c_i).u >= 1/2 + 1/2 = 1.  Global.
* edge: LOCAL.  If on ALL of N the corner's tangential coordinate along the edge
  satisfies |t.(q - c_j)| < 1/2 and its depth satisfies n.(q - c_j) > -1/2 (both
  interval-verified; min tangential margin 0.019 at E4c1-7e2, the binding one), then
  g_k(z) < 0 forces both body-frame coordinates of q relative to square j into
  (-1/2, 1/2), i.e. q lies in int(Q_j); since q is a boundary point of Q_i, every
  neighbourhood of q meets int(Q_i), so int(Q_i) and int(Q_j) intersect — infeasible.
  Hence feasible => g_k >= 0.

## 2. KKT, dependencies, strict complementarity

The 38x34 Jacobian at z0 has rank 34 (smallest kept singular value 0.127; gradients
verified against 1e-30 central differences to 2e-61).  The 4-dimensional left null space
splits into 3 local wall redundancies (squares 0, 2, 5 each carry 4 wall rows of rank 3)
plus ONE genuine self-stress supported on the 8 corner-on-edge rows of the four flush
tilted pairs (7-8, 7-9, 8-10, 9-10) — the "pinwheel" stress.  (Pure support separation
argument: pinwheel rows touch only variables of squares 7..10; wall rows of 0/2/5 touch
only their own squares and s; so the null space decomposes.)  Consequently every
maximal independent subsystem S (34 rows) must omit one wall row for each of squares
0, 2, 5 and exactly ONE pinwheel row.

The Farkas LP over all 38 rows (grad s = sum lambda_k grad g_k, lambda >= 0) is feasible
with max-min multiplier 0.0476 — the curated system is **first-order rigid** ("no
feasible direction decreases s").  Enumerating the 512 admissible drop sets, the best is

    D = { W0c0[y=0], W2c2[x=s], W5c3[y=s], E8c3-7e0 },   S = the other 34 rows,

whose UNIQUE multiplier vector lambda = A_S^{-T} e_s (34x34 solve at 90 dps) is strictly
positive: **min lambda = 0.01754 (W2c0[y=0]), max lambda = 0.32092 (W10c1[x=s])**.
Strict complementarity holds on S; LICQ holds (the interval Jacobian of S is nonsingular
on all of N — implied by the Krawczyk contraction).  Multiplier identity residual
||A_S^T lambda - e_s||_inf <= 6.4e-41 (interval-verified; lambda stored as rationals with
denominator 10^40).

## 3. Krawczyk existence + uniqueness (mpmath.iv, outward rounding)

K(B) = -Y F(c) + (I - Y [J](B)) (B - c), with c = z0 (exact rationals), Y = rational
rounding (denominator 10^30) of the midpoint inverse Jacobian, [J](B) the interval
Jacobian over the box.  K(B) strictly inside int(B) proves F has exactly one zero in B
(Krawczyk/Neumaier).  Results for F = (g_k)_{k in S}:

    radius r     max|K|/r      verdict
    1e-6         0.000118      contracts
    5e-4 (=r_N)  0.0590        contracts   <-- the theorem box
    8e-3         0.9447        contracts   <-- largest certified radius
    1e-2         1.18          fails
    1e-50 (=r_0) 4.9e-10       contracts   <-- tight enclosure of z-hat

So z-hat exists, is unique in N, and ||z-hat - z0||_inf <= 1e-50.  (The 60-digit centre
gives |F(z0)| <= 6e-60; the enclosure radius is limited only by our chosen r_0.)

**Second system F~ (exact structure of z-hat).**  S contains only 9 of the 10 flush
tilted rows, so "the five tilt angles are equal" is NOT part of F's definition.  Define
S2 = 17 wall rows (S's walls) + the 6 upright-tilted edge rows + ONE edge row per flush
tilted pair (6-9, 7-8, 7-9, 8-10, 9-10) + 2 dist rows + the 4 angle-equality rows
th_6 = th_7 = th_8 = th_9 = th_10 (34 rows; the tilted-theta 60-digit strings are
identical, so these rows vanish EXACTLY at z0).  Krawczyk for F~ on N contracts
(max|K|/r = 0.047): unique zero z-tilde in N.  At z-tilde:

* the upright pinning is EXACT: e.g. corner0_x = corner3_x = 0 => sin th_0 = 0 =>
  th_0 = 0 (|th| <= 5e-4 in N) and cx_0 = 1/2; then corner1_y = cy_0 - 1/2 = 0 =>
  cy_0 = 1/2.  Similarly squares 1..5 (using the dist rows for c1, c3: cy_1 = 1/2 and
  (cx_1 - 1/2)^2 = 1 => cx_1 = 3/2 in N; etc.).  In particular the three wall rows
  dropped from S vanish exactly at z-tilde.
* all five tilt angles are exactly equal, so for each flush tilted pair the two edge
  lines are parallel; the S2 contact row says the corner (an endpoint of its own edge)
  lies on the other square's edge line, hence the two lines COINCIDE, hence the second
  corner row of the pair (including the dropped E8c3-7e0) vanishes exactly.

Therefore ALL 38 curated rows vanish at z-tilde; in particular F(z-tilde) = 0, and by
Krawczyk-uniqueness of F on N, **z-tilde = z-hat**.  This upgrades z-hat to the exact
structure in headline item 2.

## 4. Feasibility of z-hat

* flush tilted pairs: equal angles + coinciding edge lines separate the two interiors
  (each interior is strictly on its own side of the common line).  Exact.
* flush upright pairs (0,1), (0,3) and corner pair (1,3): exact coordinates
  ([0,1]^2, [1,2]x[0,1], [0,1]x[1,2], ...), interiors disjoint by inspection.  Exact.
* upright-tilted contact pairs (1-8, 2-8, 3-7, 4-7, 4-6, 5-9): on box(z0, r_0) the
  touching corner realises the STRICT minimum projection of its square on the contact
  axis n (min slack 0.645, interval-verified), so the SAT gap along n equals
  g_k(z-hat) = 0: the open projection intervals are disjoint => interiors disjoint.
* the 41 non-contact pairs: interval SAT separation > 0 on box(z0, r_0)
  (min 0.0249 = the 6-7 / 8-9 strip gaps).
* containment: wall-contact corners lie exactly ON their wall (allowed, closed
  containment); all other corner-wall clearances > 0 by interval (min 0.549).

## 5. The optimality argument (the mathematical heart)

Fix a feasible z in N and set d = z - z-hat (segment [z-hat, z] lies in the box N).

(a) For every k in S:  g_k(z-hat) = 0 and g_k(z) >= 0 (validity lemmas), so by the mean
    value theorem there is xi_k on the segment with  grad g_k(xi_k) . d  =  g_k(z) >= 0.

(b) **Positive-spanning certificates.**  Strict complementarity + nonsingularity give,
    for every sign sigma = +-1 and coordinate i, rational mu^(i,sigma) >= 0 and
    nu^(i,sigma) >= 0 with

        sigma e_i  =  sum_k mu_k grad g_k(z0)  -  nu e_s   (up to a tiny residual).

    Construction: c = A_S^{-T} (sigma e_i) (unique), nu = max(0, max_k(-c_k/lambda_k)),
    mu = c + nu lambda >= 0 — possible precisely because lambda > 0; this nu is optimal.
    Define the interval residual over the whole box,
    rho^(i,sigma) = sigma e_i + nu e_s - sum_k mu_k [grad g_k](N), which contains the
    true residual for ANY choice of evaluation points xi_k in N.  Certified bound:

        beta  :=  max_(i,sigma) || rho^(i,sigma) ||_1  =  0.6339  <  1   (at r_N = 5e-4).

(c) Apply the certificate to d, using (a) and e_s . d = s(z) - s-hat:

        sigma d_i  =  sum_k mu_k (grad g_k(xi_k) . d)  -  nu (s(z) - s-hat)  +  rho . d
                  >=  0  -  nu (s(z) - s-hat)  -  beta ||d||_inf .

    If s(z) <= s-hat this gives sigma d_i >= -beta ||d||_inf for BOTH signs, hence
    ||d||_inf <= beta ||d||_inf, hence d = 0 (beta < 1):  **z = z-hat**.
    So s(z) >= s-hat for every feasible z in N, with equality only at z-hat; and z-hat
    is feasible with s(z-hat) = s-hat, so the minimum is attained there, uniquely.
    If s(z) <= s-hat + delta the same display gives ||d||_inf <= (nu_max delta +
    beta ||d||_inf), i.e. ||d||_inf <= nu_max delta / (1 - beta) = 155.7 delta.

Note the proof needs NO Hessian bounds: the interval-gradient mean-value form absorbs
all second-order remainders, and the case analysis "s <= s-hat => d = 0" replaces the
usual second-order sufficiency argument.  The 68 certificates say exactly that the
gradients of S together with -e_s positively span R^34 — the quantitative form of
"the critical cone is {0}".

## 6. Artefacts

| file | content |
|---|---|
| `a22lib.py` | shared machinery: exact parsing, constraint eval/gradients for mp and iv contexts, interval boxes, interval SAT |
| `phase1_kkt.py` | rank/dependency analysis, FD gradient check, first S, self-stress structure |
| `phase1b_dropsearch.py` | global Farkas LP (max-min multiplier 0.0476) + 512-drop-set search |
| `phase2_certs.py` | 90-dps lambda, 68 closed-form certificates, rational rounding (denominator 1e40) |
| `phase3_krawczyk.py` | Krawczyk radius scan (1e-6 ... 1e-2) |
| `phase4_validity.py` | beta(r), tangential margins, inactive margins |
| `build_cert.py` | assembles `results/krawczyk_cert.json` (284 KB: z0, r_N, r_0, 42 rows, S, S2, Y, Y2, lambda, 68 certificates, pair lists, claims) |
| `recheck.py` | **standalone re-checker** (mpmath.iv + fractions only, no repo imports) |
| `results/krawczyk_cert.json` | the certificate |
| `results/farkas_certs.json`, `results/subsystem_S.json`, `results/krawczyk_scan.json` | intermediates |

Re-verify everything (runs in under 5 s):

    cd attempts/A22-local-rigidity && python recheck.py results/krawczyk_cert.json

Checks: [G] centre residual <= 1e-55 on all 42 rows; [K] Krawczyk contraction for F on
N and on box(z0,1e-50), and for F~ on N; [V] tangential/depth validity margins on N;
[E] multiplier identity + lambda > 0; [B] all 68 certificates: mu, nu >= 0, beta < 1,
completeness; [F] feasibility of z-hat.  Exit 0 iff all pass.

**Corruption gates** (all verified to FAIL loudly):
`--corrupt z0-big` (centre off by 1e-3: G, K x3, E, B all fail), `--corrupt z0-small`
(1e-8: G, K-tight, E, F fail), `--corrupt mu` (sign-flip one weight: B fails,
beta = 15.8), `--corrupt spec` (tamper one edge index: G, K x3, V, E fail).

## 7. Rigorous vs assumed / remaining gaps

Rigorous (machine-verified intervals + the short lemmas of sections 1, 3-5):
existence/uniqueness/structure/feasibility of z-hat, and strict local optimality with
the quantitative constant, on the explicit box N (r_N = 5e-4, 500x the 1e-6 target).
The binding limit on r_N is the certificate residual beta (beta < 1 up to r ~ 7.8e-4);
validity margins would allow ~5e-3 and Krawczyk ~8e-3.

Assumed / not re-proved here:
1. **mpmath.iv** is trusted as a correctly-rounding interval library (same status as
   the A08 verifier's integer-interval scheme; recheck.py is an independent
   implementation of the geometry but not of the arithmetic).
2. **Exact identification s-hat = octic root** (and theta with p(t)): our enclosure
   pins s-hat to 1e-50 and octic(s-hat) to +-3.1e-45, consistent with A03's PSLQ-found
   octic, but equality is not derived symbolically.  (Would follow from a Q(t)-algebra
   verification that A03's exact point solves all 38 rows; the theorem itself does not
   need it — s-hat is intrinsically defined by item 1.)
3. **Symmetry/labelling bookkeeping**: the theorem is about configurations in N, i.e.
   with the canonical labelling and orientation.  "Any packing whose configuration is
   within 5e-4 of SOME relabelling/reflection of Trump's" reduces to this by applying
   the finite group (D4 x S11); standard, stated not formalised.
4. Lemmas of sections 1 and 3-5 are ordinary (short) mathematics, not Lean-formalised.
   A06-style formalisation would need: the MVT/Krawczyk theorems, the three validity
   lemmas, and the interval evaluations — all finite and Lean-friendly in principle
   (the certificate JSON was designed to be replayable by an integer-interval checker).

## 8. How this plugs into the optimality programme

* Combined with a (future) GLOBAL statement "every optimal packing can be brought
  within 5e-4 of z0 (mod D4 x S11)", this theorem immediately yields s(11) = s-hat.
  The global half is exactly what the case-LP / theta-prime / wastage legs are for —
  they must now only exclude packings with s <= s-hat OUTSIDE N, a compact region
  minus an open box, at the true optimum value (no 3.84-style slack needed INSIDE N).
* The stability constant (155.7) converts any future lower bound s(11) >= s-hat - delta
  into "all feasible configurations in N are within 156 delta of Trump" — useful for
  bootstrapping neighbourhood exclusions.
* First rigorous rigidity statement for this packing: infinitesimal rigidity (A03's
  rank check) is upgraded to actual local uniqueness of the contact configuration
  (Krawczyk) AND local optimality with strictness — the 46-year-old missing endgame.

## 9. Numbers

    box radius r_N               5e-4      (inf-norm, all 34 coordinates)
    Krawczyk ratio at r_N        0.0590    (F~ : 0.0471); largest contracting radius 8e-3
    enclosure of z-hat           1e-50
    min multiplier               0.017542  (W2c0[y=0]); max 0.320924; all 34 > 0
    global LP max-min mult       0.047644  (over all 38 rows)
    beta at r_N                  0.6339    (< 1 needed; < 1 up to r ~ 7.8e-4)
    nu_max                       57.006    => stability constant 155.7
    min validity tan margin      0.01900   (E4c1-7e2, |t| = 0.47899 at centre)
    min inactive pair margin     0.018859  on N (pair 8-9; strip gaps 0.0249 at centre)
    min inactive wall margin     0.547     on N (sq9 corner 2 vs y=s)
    centre residual              6.0e-60   (all 42 rows)
    multiplier identity residual 6.4e-41
    octic(s-hat)                 within +-3.1e-45
