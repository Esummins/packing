# A62 TCB RAW DATA

Generated from repo `C:\Users\esumm\code\packing`.

    git rev-parse HEAD = c9980bfcda1582d1e1a20126927a8a7d34ca1bb6

Raw data only. No classification, no analysis, no recommendations.

---

## 1. VERIFIER / CHECKER INVENTORY

### 1.1 Located files (line counts via `wc -l`)

```
   808  C:\Users\esumm\code\packing\certs\verify_measure.py
   168  C:\Users\esumm\code\packing\certs\verify_certificate.py
   957  C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\verify_case.py
   793  C:\Users\esumm\code\packing\attempts\A56-sparametric\code\verify_param.py
   381  C:\Users\esumm\code\packing\attempts\A27-close-384\verify_tree2.py
   402  C:\Users\esumm\code\packing\attempts\A29-finish-384\verify_tree2.py
   719  C:\Users\esumm\code\packing\attempts\A37-cp-atlas\code\a37_check.py
   151  C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\skeletons.py
   116  C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\skeletons2.py
   233  C:\Users\esumm\code\packing\attempts\A57-shadow-trees\code\alivewitness.py
   432  C:\Users\esumm\code\packing\attempts\A22-local-rigidity\recheck.py
```

### 1.2 Lean checkers (line counts only)

```
    76  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Checker.lean
   244  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureInt.lean
   195  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Measure.lean
    53  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Geometry.lean
  1091  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntData.lean
  1002  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntData381.lean
  1791  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntData382.lean
    32  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntDataA05.lean
    26  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntDataGoebel.lean
    20  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Kernel.lean
    32  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Data.lean
    32  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\DataTight.lean
    28  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Main.lean
    29  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureData.lean
    23  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntMain.lean
    30  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureMain.lean
    49  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Example.lean
    26  C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureExample.lean
```

### 1.3 verify_case.py -- ALL COPIES FOUND (16)

All 16 copies are BYTE-IDENTICAL: 957 lines, 47054 bytes, sha256 =
`521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`.

```
   957  C:\Users\esumm\code\packing\attempts\A13-case-lp-bnb\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A14-close-tree-384\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A21-structure-388\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A24-composed-tree\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A27-close-384\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A29-finish-384\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A38-root-power\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A39-early-cert\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A42-occupancy-chain\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A52-twofield-probe\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A54-stragglers\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A55-k4-sweep\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A57-shadow-trees\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A59-trump-residual\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
   957  C:\Users\esumm\code\packing\attempts\A60-trump5-campaign\code\verify_case.py   sha256[:16]=521cb01fe656707c  bytes=47054
```

Canonical / most-recent-used copy (referenced by name from A56 code, and the copy
A56 imports rather than re-implements):

    C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\verify_case.py

Raw evidence (grep -n over A53..A57 for `verify_case`):

```
attempts/A56-sparametric/code/sweep.py:10:             s = 191/50 and run the UNMODIFIED A53 verify_case.py.  A certificate that fails
attempts/A56-sparametric/code/sweep.py:16:             on PASS run canary C2 -- the OLD verify_case.py on the specialisations at
attempts/A56-sparametric/code/sweep.py:40:VERIFY_CASE = os.path.join(ATTEMPTS, "A53-simple-strata", "code", "verify_case.py")
attempts/A56-sparametric/code/sweep.py:203:    """canary C2: the OLD verify_case.py on the specialisations at slo, midpoint, s0."""
attempts/A56-sparametric/code/sweep.py:396:        p.add_argument("--depth0", default="44", help="depth for the fixed-s verify_case runs")
attempts/A56-sparametric/code/specialize.py:7:attempts/A53-simple-strata/code/verify_case.py, which is the arbiter for canaries C1 (s = s0
attempts/A53-simple-strata/notes/verification_log.md:25:  measure certificate verified by code/verify_case.py (A38 copy, unmodified) â€” interval B&B over
```

### 1.4 Other verify_*.py / PASS-FAIL deciders under certs/ and attempts/

Full `find` sweep for `verify_*.py` (excluding the 16 verify_case.py copies listed above):

```
   289  C:\Users\esumm\code\packing\certs\verify_unavoidable.py
   108  C:\Users\esumm\code\packing\attempts\A04-upper-search\verify_exact.py
   840  C:\Users\esumm\code\packing\attempts\A10-angle-box-lp\verify_measure_restricted.py
   840  C:\Users\esumm\code\packing\attempts\A12-region-rank-pilot\verify_measure_restricted.py
   199  C:\Users\esumm\code\packing\attempts\A14-close-tree-384\verify_casetree.py
   199  C:\Users\esumm\code\packing\attempts\A24-composed-tree\verify_casetree.py
   131  C:\Users\esumm\code\packing\attempts\A24-composed-tree\verify_tree.py
   199  C:\Users\esumm\code\packing\attempts\A27-close-384\verify_casetree.py
   131  C:\Users\esumm\code\packing\attempts\A27-close-384\verify_tree.py
   199  C:\Users\esumm\code\packing\attempts\A29-finish-384\verify_casetree.py
   131  C:\Users\esumm\code\packing\attempts\A29-finish-384\verify_tree.py
   184  C:\Users\esumm\code\packing\attempts\A34-sos-pilot\certs\verify_sos.py
   331  C:\Users\esumm\code\packing\attempts\A47-corner-majority\code\verify_measure_obs.py
    94  C:\Users\esumm\code\packing\attempts\A48-bridge-cascade\code\verify_b2_chain.py
   115  C:\Users\esumm\code\packing\attempts\A48-bridge-cascade\code\verify_r1_bridge.py
    77  C:\Users\esumm\code\packing\attempts\A48-bridge-cascade\code\verify_r3_wall.py
    82  C:\Users\esumm\code\packing\attempts\A48-bridge-cascade\code\verify_r4_nogo.py
   154  C:\Users\esumm\code\packing\attempts\A52-twofield-probe\code\verify38.py
```

Other named re-checkers / arbiters found by name search:

```
   432  C:\Users\esumm\code\packing\attempts\A22-local-rigidity\recheck.py
    25  C:\Users\esumm\code\packing\attempts\A23-wastage-oracle\recheck.py
   107  C:\Users\esumm\code\packing\attempts\A24-composed-tree\recheck.py
   566  C:\Users\esumm\code\packing\attempts\A36-levers\code\a36_check.py
   719  C:\Users\esumm\code\packing\attempts\A37-cp-atlas\code\a37_check.py
   432  C:\Users\esumm\code\packing\attempts\A35-escape-complex\code\m2_check_inflation.py
   263  C:\Users\esumm\code\packing\attempts\A35-escape-complex\code\m2_check_route.py
   412  C:\Users\esumm\code\packing\attempts\A35-escape-complex\code\m2b_check.py
   576  C:\Users\esumm\code\packing\attempts\A50-wall-termination\code\checker_span.py
   238  C:\Users\esumm\code\packing\attempts\A50-wall-termination\code\canary_span.py
    53  C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\check_trump_feasible.py
    53  C:\Users\esumm\code\packing\attempts\A54-stragglers\code\check_trump_feasible.py
    53  C:\Users\esumm\code\packing\attempts\A55-k4-sweep\code\check_trump_feasible.py
    53  C:\Users\esumm\code\packing\attempts\A57-shadow-trees\code\check_trump_feasible.py
   233  C:\Users\esumm\code\packing\attempts\A57-shadow-trees\code\alivewitness.py
   233  C:\Users\esumm\code\packing\attempts\A59-trump-residual\code\alivewitness.py
   233  C:\Users\esumm\code\packing\attempts\A60-trump5-campaign\code\alivewitness.py
   153  C:\Users\esumm\code\packing\attempts\A59-trump-residual\code\canary.py
   153  C:\Users\esumm\code\packing\attempts\A60-trump5-campaign\code\canary.py
   149  C:\Users\esumm\code\packing\attempts\A60-trump5-campaign\code\selftest60.py
   328  C:\Users\esumm\code\packing\attempts\A52-twofield-probe\code\selftest38.py
```

### 1.5 Header docstrings / comments (first 30 lines, verbatim)

#### `C:\Users\esumm\code\packing\certs\verify_measure.py`  (808 lines) -- measure-certificate verifier (lower bounds)

```python
#!/usr/bin/env python3
"""
verify_measure.py -- exact-arithmetic verifier for MEASURE certificates (lower bounds for the
square-packing problem).  Written independently of the LP code that produces the certificates
(attempt A08-measure-verify); shares no code with attempts/A07-lp-dual or certs/verify_unavoidable.py.

CLAIM CERTIFIED
    Let mu = sum_i w_i * delta_{p_i} be a finite non-negative atomic measure on [0,s]^2 with
    total mass  M = sum_i w_i  <  n  (n = 11 by default; field "n" of the certificate).
    If every CLOSED unit square Q contained in the closed square [0,s]^2 (any orientation)
    satisfies mu(Q) >= 1, then no n pairwise-disjoint closed unit squares fit in [0,s]^2, and
    therefore s(n) >= s.   (Proof: if n unit squares with disjoint interiors fit in side s' < s,
    scale by s/s' > 1 and shrink each square about its centre back to a unit square; the n
    closed unit squares are now pairwise disjoint inside [0,s]^2, so mu([0,s]^2) >= n > M,
    contradiction.  Hence s(n) >= s.)

    The verifier decides the hypothesis "mu(Q) >= 1 for every closed unit square Q in [0,s]^2"
    by exact integer/rational interval branch-and-bound; the two-line argument above and the
    symmetry remark below are the only mathematics taken on trust.

PARAMETRISATION
    Q(c, theta) = closed unit square with centre c = (cx, cy) and edge direction theta.
    Q(c, theta) = Q(c, theta + pi/2), so theta in [0, pi/2] suffices.  Put t = tan(theta/2) in
    [0, 1]:  cos theta = (1 - t^2)/(1 + t^2)  (decreasing on [0,1]),
             sin theta = 2t/(1 + t^2)         (increasing on [0,1]),
    so for a rational t-interval [t0, t1] the enclosures  C = [cos(t1), cos(t0)]  and
    S = [sin(t0), sin(t1)]  are exact rationals.  All decisions are exact (Python ints /
    fractions.Fraction); floating point (numpy) is used ONLY to shortlist atoms and to choose
    sample placements -- every accept decision is re-derived exactly.

```

#### `C:\Users\esumm\code\packing\certs\verify_certificate.py`  (168 lines) -- packing upper-bound certificate verifier

```python
#!/usr/bin/env python3
"""
verify_certificate.py -- exact (rational) verifier for "n unit squares inside a square of side s"
upper-bound certificates.  Standard library only; all comparisons in fractions.Fraction /
int arithmetic; no floating point anywhere in the logic.

Two certificate formats are accepted (auto-detected):

(A) centre/tilt format  ("format": "centre-tilt")
    {"side": "p/q",
     "squares": [{"cx": "p/q", "cy": "p/q", "t": "p/q"}, ...]}
    t = tan(theta/2) is rational, hence cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2) are exactly
    rational and cos^2 + sin^2 = 1 holds identically.  Corners: c + R(theta)(+-1/2, +-1/2).

(B) integer-corner format  ("format": "integer-corners")
    {"D": <int>, "side_D": <int>,
     "squares": [{"corners": [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]}, ...]}
    all corner coordinates are integers meaning x/D; the container is [0, side_D/D]^2.
    Each square is checked to be a genuine unit square: with e = P1-P0, f = P2-P1 we require
    f = rot90(e), P3 = P0 + f, and |e|^2 = D^2 exactly.

Checks (both formats):
  1. every corner strictly inside the open container (0 < x < s, 0 < y < s);
  2. for every pair of squares there is a separating axis among the edge normals of the two
     squares (4 candidate axes) whose projections are strictly disjoint.
Prints the minimum containment margin and minimum separation margin (exact rationals, plus a
float rendering for humans) and exits 0 on success, 1 on failure.

Mathematical basis (the only thing taken on trust): two convex polygons whose projections
onto some line are disjoint intervals are disjoint sets, and the projection of a polygon is
```

#### `C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\verify_case.py`  (957 lines) -- case-LP verifier -- CANONICAL COPY (see 1.3)

```python
#!/usr/bin/env python3
"""
verify_case.py -- A13 COPY of certs/verify_measure.py extended to CASE (conditional) measure certificates.

EXTENSION (A13-case-lp-bnb).  The certificate carries hypotheses and a budget:
    "budget": b  (= n - #cores),
    "hypotheses": {"cores":  [{"kx","ky","tm","a", ...}, ...]      rational squares K = centre (kx,ky), orientation
                                                                   theta_m with tan(theta_m/2) = tm, half-side a
                   "nofams": [{"x0","x1","y0","y1","t_intervals":[[t0,t1],...]}, ...]}
CLAIM: mu(total) < budget and mu(Q) >= 1 for every admissible closed unit square Q that is NOT exempt, where Q is
exempt iff (i) its centre lies in a NO-family zone and t = tan(theta/2) in one of the family's t-intervals (closed), or
(ii) Q meets (closed intersection) some core K.  Then no packing of n = 11 pairwise-disjoint closed unit squares in
[0,s]^2 satisfies the hypotheses "for every core K some square Q0 of the packing contains K" and "no square of the
packing lies in a NO-family" (bridge: the >= n - #cores squares other than the Q0's are non-exempt, pairwise disjoint,
each of mass >= 1, so mu(total) >= budget).  A (t,cx,cy)-box is EXEMPT (discharged) iff it is PROVABLY exempt for all
its parameters: box inside a NO-family (rational comparisons), or SAT non-separation from a core on all four axes
proven by rational interval arithmetic (see core_exempt_frac).  Boxes that are not provably exempt must be covered
or split, exactly as before.  Float pre-filter only shortlists; every exemption decision is exact.

Original header follows.
----------------------------------------------------------------------------------------------------------------
verify_measure.py -- exact-arithmetic verifier for MEASURE certificates (lower bounds for the
square-packing problem).  Written independently of the LP code that produces the certificates
(attempt A08-measure-verify); shares no code with attempts/A07-lp-dual or certs/verify_unavoidable.py.

CLAIM CERTIFIED
    Let mu = sum_i w_i * delta_{p_i} be a finite non-negative atomic measure on [0,s]^2 with
    total mass  M = sum_i w_i  <  n  (n = 11 by default; field "n" of the certificate).
    If every CLOSED unit square Q contained in the closed square [0,s]^2 (any orientation)
    satisfies mu(Q) >= 1, then no n pairwise-disjoint closed unit squares fit in [0,s]^2, and
```

#### `C:\Users\esumm\code\packing\attempts\A56-sparametric\code\verify_param.py`  (793 lines) -- A56 4D (t,cx,cy,s) parametric verifier

```python
#!/usr/bin/env python3
"""
verify_param.py -- A56 T2(C).  The 4D (t, cx, cy, s) verifier for parametric-kill-certificate-v1.

WHAT IS PROVED (soundness.md P3, verbatim).  Certificate C declares, for each s, the atomic
measure mu_s = sum_i w_i delta_{p_i(s)} with p_i(s) = (ax_i + bx_i s, ay_i + by_i s) and the
core (pin) squares K_j(s) centred at (akx_j + bkx_j s, aky_j + bky_j s), half-side a_j, tilt tm_j.
A PASS on the root [0,1] x [1/2, s_hi-1/2]^2 x [s_lo, s_hi] certifies

    for every s in [s_lo, s_hi] and every closed unit square Q admissible in [0,s]^2 that meets
    no core K_j(s):   mu_s(Q) >= 1 + margin,

together with the s-free inequality sum_i w_i < budget = n - #cores.  By A13/A53-L5 this is the
kill of the stratum for EVERY s in the window (soundness theorem [S] of notes/soundness.md).

REUSED, UNMODIFIED, FROM attempts/A53-simple-strata/code/verify_case.py (imported, not copied,
so the audited integer core is literally the same code):
    imul4, trig_int, box_trig            interval/trig integer primitives
    vacuous_int, clip_int                admissibility, rule (V) and (CL) -- called with s = b
    cos_sin_t, atom_inside_frac, mass_at_frac, core_exempt_frac      Fraction reference / witnesses
    CoreH, merge_stats, _rat
NEW HERE (the only new exact predicates; each is the A53 one with a POINT replaced by an
outward INTERVAL, so the enclosure can only grow):
    atom_inside_int_iv    atom_inside_int with px in [PXlo,PXhi]/PD, py in [PYlo,PYhi]/PD
    core_exempt_frac_iv   core_exempt_frac with kx in [kxlo,kxhi], ky in [kylo,kyhi]
    core_exempt_float_iv  the float pre-filter for the above (shortlist only; never decides)

DISCHARGE RULES on B = [t0,t1] x [x0,x1] x [y0,y1] x [a,b]  (P3):
  (V)  vacuous: vacuous_int with the wall at s = b (the largest container of the cell);
  (CL) clip:    clip_int with the wall at s = b -- lower bound floor(wmin/2), upper ceil(b-wmin/2);
```

#### `C:\Users\esumm\code\packing\attempts\A27-close-384\verify_tree2.py`  (381 lines) -- A27 end-to-end case-tree verifier

```python
#!/usr/bin/env python3
"""
A27 verify_tree2.py -- END-TO-END EXACT verifier for the interior-first case tree at s = 96/25.

Everything below is checked in exact rational arithmetic (`fractions.Fraction`); no floating
point enters any decision.  The parametrisation of orientation is

        t = tan(theta/2),      theta in [0 deg, 90 deg]  <==>  t in [0, 1]

(monotone), which makes every cut and every symmetry map RATIONAL and removes pi from the
verification entirely.  A parameter box is written  Bq = [X0,X1] x [Y0,Y1] x [T0,T1]  with
X,Y,T rational; the certificate files store the centre box as exact decimals and the core as
exact rationals, and the t-endpoints are the outward-rounded values t_lo(th0) <= tan(th0/2),
t_hi(th1) >= tan(th1/2) that A13/A14's `caselp.Box.core` uses (dyadic, denominator 2^24).

CHECKS
 (1) ROOT  certs/casetree_3.84/root_interior_occupancy.json
     re-verified by the exact verifier verify_case.py, plus: n = 11, s = 96/25, budget = 11,
     total < 11, and its single NO-family is EXACTLY the zone Z = [11/10,137/50]^2 x all theta.
     ==> every packing of 11 unit squares in [0,96/25]^2 has a square centred in Z.
 (2) TREE LOGIC.  The level-1 cells are recomputed from scratch in rationals:
     Z = [A,B]^2 with A = 1/2 + 3/5 = 11/10, B = 96/25 - 1/2 - 3/5 = 137/50, m = 48/25,
     h = 41/50, x-cuts m + h*i/8 (i = 0..8), t-bins [t_lo(15k), t_hi(15(k+1))] (k = 0..5).
     Checked exactly: the x-cuts are strictly increasing with c_0 = m, c_8 = B; the t-bins
     satisfy t_lo(0) = 0, t_hi(90) = 1 and t_lo(15(k+1)) <= t_hi(15k+15), so their union is
     exactly [0,1]; every cell (i,j,k) with j <= i is present; and every stored certificate box
     equals its cell's rational box.
 (3) CORE CONTAINMENT (new in A27; the step A24's verify_tree.py did NOT check).
     verify_case.py proves "no packing of 11 unit squares has a square CONTAINING the rational
     core square K".  To turn that into a statement about the parameter box we verify, in exact
```

#### `C:\Users\esumm\code\packing\attempts\A29-finish-384\verify_tree2.py`  (402 lines) -- A29 descendant of verify_tree2.py

```python
#!/usr/bin/env python3
"""
A27 verify_tree2.py -- END-TO-END EXACT verifier for the interior-first case tree at s = 96/25.

Everything below is checked in exact rational arithmetic (`fractions.Fraction`); no floating
point enters any decision.  The parametrisation of orientation is

        t = tan(theta/2),      theta in [0 deg, 90 deg]  <==>  t in [0, 1]

(monotone), which makes every cut and every symmetry map RATIONAL and removes pi from the
verification entirely.  A parameter box is written  Bq = [X0,X1] x [Y0,Y1] x [T0,T1]  with
X,Y,T rational; the certificate files store the centre box as exact decimals and the core as
exact rationals, and the t-endpoints are the outward-rounded values t_lo(th0) <= tan(th0/2),
t_hi(th1) >= tan(th1/2) that A13/A14's `caselp.Box.core` uses (dyadic, denominator 2^24).

CHECKS
 (1) ROOT  certs/casetree_3.84/root_interior_occupancy.json
     re-verified by the exact verifier verify_case.py, plus: n = 11, s = 96/25, budget = 11,
     total < 11, and its single NO-family is EXACTLY the zone Z = [11/10,137/50]^2 x all theta.
     ==> every packing of 11 unit squares in [0,96/25]^2 has a square centred in Z.
 (2) TREE LOGIC.  The level-1 cells are recomputed from scratch in rationals:
     Z = [A,B]^2 with A = 1/2 + 3/5 = 11/10, B = 96/25 - 1/2 - 3/5 = 137/50, m = 48/25,
     h = 41/50, x-cuts m + h*i/8 (i = 0..8), t-bins [t_lo(15k), t_hi(15(k+1))] (k = 0..5).
     Checked exactly: the x-cuts are strictly increasing with c_0 = m, c_8 = B; the t-bins
     satisfy t_lo(0) = 0, t_hi(90) = 1 and t_lo(15(k+1)) <= t_hi(15k+15), so their union is
     exactly [0,1]; every cell (i,j,k) with j <= i is present; and every stored certificate box
     equals its cell's rational box.
 (3) CORE CONTAINMENT (new in A27; the step A24's verify_tree.py did NOT check).
     verify_case.py proves "no packing of 11 unit squares has a square CONTAINING the rational
     core square K".  To turn that into a statement about the parameter box we verify, in exact
```

#### `C:\Users\esumm\code\packing\attempts\A37-cp-atlas\code\a37_check.py`  (719 lines) -- A37 atlas standalone re-checker

```python
#!/usr/bin/env python
"""a37_check.py -- STANDALONE re-checker for A37 certificates
(results/certs/fam*_3R.json, fam*_3S.json).   Cookbook step 4.

Imports ONLY  mpmath.iv + fractions + json + math + glob + os + sys.  It uses
NO producer library: not a37_pipeline, not a36_lib, not strata_lib, not
t3lib, not numpy, not scipy.  The order-2 interval jets and the row language
below are transcribed (with attribution) from A36's own standalone re-checker
attempts/A36-levers/code/a36_check.py, which in turn transcribes A35's
m2_check_inflation.py.

The checker does NOT trust the producer's row list, safety flags, branch sets
or omega support.  From the certificate's CONTACT TABLE alone it

  [R] rebuilds every row and compares with the producer's implied row order;
  [C] re-verifies that every row is ACTIVE at z_center;
  [S] recomputes the [V] safety flag of every sep row from the tangential
      coordinate at z_center (a producer that marked an endpoint row "safe"
      fails here);
  [B] recomputes the branch structure: for every pair carrying a non-[V]-safe
      row it re-runs the kill test on box(z_center, h_probe) and checks that
      the certificate's live-axis set CONTAINS every axis the checker cannot
      kill, and that the certificate enumerates the full product of live axes;
  [O] sign discipline: omega >= 0, omega = 0 on every row not valid in that
      variant (rows outside the variant's chosen axis, or non-safe rows of an
      unbranched pair);
  [W] W0 = sum |omega_r| |g_r(z_center)|;
  [G] r_res = ||A(z_center)^T omega - e_s||_1;
  [H] Hbar(h) = (1/2) sum_ij sup_box |d^2 W / dz_i dz_j|;
  [V] tangential/depth margins of every omega-loaded sep row on box(h);
```

#### `C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\skeletons.py`  (151 lines) -- A53 census leg (a): recursive-BFS skeleton enumeration

```python
"""
A53 leg (a): exact enumeration of simple-square skeletons at s0 = 969271/250000.

Definitions (I-L20, docs/ideas.md; formalized in notes/lemmas.md):
  A square of a packing is SIMPLE (grid-locked) iff it is axis-aligned and belongs to some
  recursively-locked set: each member has an x-support (left/right edge on a wall, or a
  positive-length vertical edge contact with an earlier member at |dx| = 1) AND a y-support
  (bottom/top edge on a wall, or a positive-length horizontal edge contact at |dy| = 1).
  Simp(P) = union of all recursively-locked subsets of P (closed under union => well-defined).

  Consequence (exact grid): both centre coordinates of a simple square lie in
      X = ({1/2 + i} u {s0 - 1/2 - j}) n [1/2, s0 - 1/2],  i, j in Z>=0,
  because wall contact pins a coordinate to 1/2 or s0-1/2 and each locked-locked flush step
  moves it by exactly +-1, and cross-family steps of exactly 1 do not exist at s0
  (s0 - m - n is never an integer for the relevant small m, n; verified below).

  A SKELETON is any possible value of Simp(P): a set of pairwise interior-disjoint slot
  squares that is recursively locked. This script enumerates ALL of them exactly (Fractions),
  reduces by D4, and identifies Trump's k = 5 skeleton.

Output: results/skeletons.json (census + all D4 classes with exact coordinates).
"""
import json, sys, itertools
from fractions import Fraction as Fr

S0 = Fr(969271, 250000)
HALF = Fr(1, 2)

def slot_values():
    L, R = [], []
```

#### `C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\skeletons2.py`  (116 lines) -- A53 census leg (a) PRIMARY: Young-class enumeration

```python
"""
A53 leg (a), PRIMARY (PI's authoritative definition, 2026-08-31):

A square of a packing is SIMPLE iff it sits at integer distance from two perpendicular
container sides and is connected to both by gap-free flush support chains -- i.e., it is
part of a tiling grown in from a corner. Structural form (definitional here, see
notes/lemmas.md L1): the simple set of any packing is a 4-tuple of corner-anchored
Young diagrams (staircases): for corner c, cell (i,j) occupied => all (i',j') <= (i,j)
occupied. At s0 = 969271/250000 < 4 each diagram fits in 3x3 (offset 3 exceeds the
admissible band), and cross-corner compatibility = exact pairwise non-overlap of the
slot squares (this subsumes the shared-wall width constraint w + w' <= 3).

Enumerates all 4-tuples (lambda_BL, lambda_BR, lambda_TR, lambda_TL) of Young diagrams
in 3x3 whose slot-square union is pairwise interior-disjoint (exact Fractions),
D4-reduces, cross-checks against the recursive-BFS census (skeletons.py: the PI
definition is strictly stronger; every Young union is recursively locked, not conversely).

Output: results/skeletons_young.json
"""
import json, sys, os, itertools
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skeletons import S0, HALF, overlap, d4_images, canon, TRUMP, enumerate_skeletons

# Young diagrams inside 3x3: partitions lambda1 >= lambda2 >= lambda3, 0 <= li <= 3
PARTS = [tuple(l) for l in itertools.product(range(4), repeat=3) if l[0] >= l[1] >= l[2]]

CORNERS = {
    "BL": (HALF, HALF, 1, 1),
```

#### `C:\Users\esumm\code\packing\attempts\A57-shadow-trees\code\alivewitness.py`  (233 lines) -- A57 alive-side arbiter

```python
"""
A57 — the ALIVE-side arbiter the lab was missing (GAP-A54-2 / GAP-A55-2), generalised from
A53's `check_trump_feasible.py`.

**Lemma (disjoint-family bound).**  Let N be a node with pins/cores C_1..C_r and budget
m = 11 - r.  Suppose Q_1..Q_m are closed unit squares in [0,s]^2 that are
  (i) admissible (contained in the container),
  (ii) pairwise disjoint with a STRICTLY positive separating gap, and
  (iii) strictly disjoint from every core C_j.
Then every measure mu feasible for the node LP has mu(Q_i) >= 1 for each i (each Q_i is a
non-exempt row: `verify_case.py` exempts a placement only if it provably meets a core), and the
Q_i are disjoint, so mu(total) >= sum_i mu(Q_i) >= m.  Hence tau* >= m = budget and **no
certificate for N can exist** -- N is LP-unkillable, whatever compute is spent on it.
The strict gap matters: mu is atomic, so squares that merely touch could share an atom.

Everything is checked in exact rational arithmetic (Fraction), with cos/sin from a rational
t = tan(theta/2): cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2).  Floats are used only to SEARCH.
"""
import argparse, json, math, os, random, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from caselp import Box, Hyp
from run_skel import S0F

S_RAT = Fr(969271, 250000)

```

#### `C:\Users\esumm\code\packing\attempts\A22-local-rigidity\recheck.py`  (432 lines) -- A22 Krawczyk certificate re-checker

```python
#!/usr/bin/env python
"""Standalone re-checker for results/krawczyk_cert.json (A22-local-rigidity).

Verifies, using ONLY mpmath.iv validated interval arithmetic (+ fractions):

  [G] centre residual: |g_k(z0)| <= claims.centre_residual_max for all k in S
  [K] Krawczyk contraction on N = box(z0, r_N):  K(N) strictly inside N
      => F = (g_k)_{k in S} has EXACTLY ONE zero z-hat in N
  [K0] same on box(z0, r_0)  =>  ||z-hat - z0||_inf <= r_0
  [V] validity margins over N for every edge constraint in S:
      |tangential| <= 1/2 - tan_margin_min,  depth > -1/2
  [E] multiplier identity: || A_S^T lambda - e_s ||_inf <= lambda_residual_max
  [B] all 68 Farkas certificates: residual interval rho over N has
      ||rho||_1 <= beta_max < 1,  and mu >= 0, nu >= 0, nu <= nu_max
  [F] feasibility of z-hat (packing validity on box(z0, r_0)):
      noncontact pairs strictly separated (interval SAT); contact pairs:
      touching corner realises the strict minimum projection on the contact
      axis (so SAT gap = g_k(z-hat) = 0 exactly => interiors disjoint);
      containment: all non-wall-contact corners strictly inside.

Together (see notes.md for the four-line mathematical argument) these verify:
every valid 11-square packing configuration z with ||z - z0||_inf <= r_N has
container side s(z) >= s(z-hat), with equality if and only if z = z-hat.

Usage:  python recheck.py results/krawczyk_cert.json [--corrupt MODE]
        MODE in {z0-big, z0-small, mu, spec}  (each must make the check FAIL)
Exit code 0 = all PASS, 1 = FAIL.
"""
import json
import sys
```

---

## 2. FLOAT AUDIT -- RAW GREP HITS

Patterns (grep -n, ERE, one pass, union):

```
float(    numpy    np\.    math\.    ' 1e-'    .hex(    fsum
```

Cap: 60 hits per file (none of the files below exceeded it; no truncation applied).

### `C:\Users\esumm\code\packing\certs\verify_measure.py`  -- 34 hit(s)

```
28:    fractions.Fraction); floating point (numpy) is used ONLY to shortlist atoms and to choose
91:    import numpy as np
244:    return (np.abs(u) <= 0.5 + tol) & (np.abs(v) <= 0.5 + tol)
272:            pd = px.denominator * py.denominator // math.gcd(px.denominator, py.denominator)
279:            WD = WD * w.denominator // math.gcd(WD, w.denominator)
287:            self.fPX = np.array([float(p[0]) for p in self.atoms])
288:            self.fPY = np.array([float(p[1]) for p in self.atoms])
289:            self.fW = np.array([float(w) for w in self.weights])
290:        self.fneed = float(self.need) - 1e-9
327:        eps = 1e-9
338:        a_hi = np.maximum(C0 * dx1, C1 * dx1)
339:        a_lo = np.minimum(C0 * dx0, C1 * dx0)
340:        b_hi = np.maximum(S0 * dy1, S1 * dy1)
341:        b_lo = np.minimum(S0 * dy0, S1 * dy0)
344:        a_hi = np.maximum(-S1 * dx0, -S0 * dx0)
345:        a_lo = np.minimum(-S1 * dx1, -S0 * dx1)
346:        b_hi = np.maximum(C0 * dy1, C1 * dy1)
347:        b_lo = np.minimum(C0 * dy0, C1 * dy0)
349:        return np.nonzero(ok)[0]
387:            mask = f_mass_mask(self.fPX, self.fPY, float(t), float(cx), float(cy), 1e-9)
388:            idx = np.nonzero(mask)[0].tolist()
431:                # mass of atoms at distance > 1e-9 from the boundary of Q (float): detects tangencies
432:                mi = float(self.fW[f_mass_mask(self.fPX, self.fPY, float(tt), float(fx), float(fy), -1e-9)].sum())
436:        w["placement"] = {"t": str(tt), "cx": str(fx), "cy": str(fy), "t_float": float(tt),
437:                          "theta_deg": math.degrees(2 * math.atan(float(tt))),
438:                          "cx_float": float(fx), "cy_float": float(fy)}
440:        w["float_mass"] = float(m)
446:            w["kind"] = "tight" if min_interior < float(self.need) - 1e-9 else "undecided"
577:              f"(~{float(total):.12f}); using computed", file=sys.stderr)
718:    print(f"s = {s} (~{float(s):.10f}), n = {n}, atoms = {len(atoms)}, "
719:          f"total mass = {total} (~{float(total):.10f}), margin = {margin}")
721:        print(f"FAIL: total mass {float(total):.6f} >= n = {n}: certificate proves nothing")
765:              f"  ==>  s({n}) >= {s} (~{float(s):.10f})")
798:                       "total_float": float(total), "margin": str(margin), "depth": a.depth,
```

### `C:\Users\esumm\code\packing\certs\verify_certificate.py`  -- 3 hit(s)

```
139:        print('squares: %d   side: %s  (= %.15g)' % (n, side, float(side)))
140:        print('min containment margin: %s  (= %.6e)' % (min_margin, float(min_margin)))
142:        print('min pair separation   = %.6e (float rendering of sqrt)' % (float(min_sep) ** 0.5))
```

### `C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\verify_case.py`  -- 38 hit(s)

```
47:    fractions.Fraction); floating point (numpy) is used ONLY to shortlist atoms and to choose
110:    import numpy as np
263:    return (np.abs(u) <= 0.5 + tol) & (np.abs(v) <= 0.5 + tol)
271:        self.fkx, self.fky, self.fcm, self.fsm, self.fa = float(kx), float(ky), float(self.cm), float(self.sm), float(a)
318:def core_exempt_float(core, ft0, ft1, fx0, fx1, fy0, fy1, slack=1e-7):
377:            pd = px.denominator * py.denominator // math.gcd(px.denominator, py.denominator)
384:            WD = WD * w.denominator // math.gcd(WD, w.denominator)
392:            self.fPX = np.array([float(p[0]) for p in self.atoms])
393:            self.fPY = np.array([float(p[1]) for p in self.atoms])
394:            self.fW = np.array([float(w) for w in self.weights])
395:        self.fneed = float(self.need) - 1e-9
435:        eps = 1e-9
446:        a_hi = np.maximum(C0 * dx1, C1 * dx1)
447:        a_lo = np.minimum(C0 * dx0, C1 * dx0)
448:        b_hi = np.maximum(S0 * dy1, S1 * dy1)
449:        b_lo = np.minimum(S0 * dy0, S1 * dy0)
452:        a_hi = np.maximum(-S1 * dx0, -S0 * dx0)
453:        a_lo = np.minimum(-S1 * dx1, -S0 * dx1)
454:        b_hi = np.maximum(C0 * dy1, C1 * dy1)
455:        b_lo = np.minimum(C0 * dy0, C1 * dy0)
457:        return np.nonzero(ok)[0]
473:                if core_exempt_float(core, ft0, ft1, fx0, fx1, fy0, fy1) and core_exempt_frac(core, t0, t1, x0, x1, y0, y1):
514:            mask = f_mass_mask(self.fPX, self.fPY, float(t), float(cx), float(cy), 1e-9)
515:            idx = np.nonzero(mask)[0].tolist()
558:                # mass of atoms at distance > 1e-9 from the boundary of Q (float): detects tangencies
559:                mi = float(self.fW[f_mass_mask(self.fPX, self.fPY, float(tt), float(fx), float(fy), -1e-9)].sum())
563:        w["placement"] = {"t": str(tt), "cx": str(fx), "cy": str(fy), "t_float": float(tt),
564:                          "theta_deg": math.degrees(2 * math.atan(float(tt))),
565:                          "cx_float": float(fx), "cy_float": float(fy)}
567:        w["float_mass"] = float(m)
573:            w["kind"] = "tight" if min_interior < float(self.need) - 1e-9 else "undecided"
719:              f"(~{float(total):.12f}); using computed", file=sys.stderr)
860:    print(f"s = {s} (~{float(s):.10f}), n = {n}, atoms = {len(atoms)}, "
861:          f"total mass = {total} (~{float(total):.10f}), margin = {margin}")
865:        print(f"FAIL: total mass {float(total):.6f} >= budget = {budget}: certificate proves nothing")
911:                  f"  ==>  no packing of {n} unit squares in side <= {s} (~{float(s):.10f}) satisfies the hypotheses (node DEAD)")
914:                  f"  ==>  s({n}) >= {s} (~{float(s):.10f})")
947:                       "total_float": float(total), "margin": str(margin), "depth": a.depth,
```

### `C:\Users\esumm\code\packing\attempts\A56-sparametric\code\verify_param.py`  -- 34 hit(s)

```
41:numpy is used only to shortlist atoms and to pick sample placements for witnesses.
68:    import numpy as np
110:        self.fcm, self.fsm, self.fa = float(self.cm), float(self.sm), float(a)
215:                pd = pd * q.denominator // math.gcd(pd, q.denominator)
222:            self.fPXlo = np.array([a / b for a, b in zip(self.PXlo, self.PD)])
223:            self.fPXhi = np.array([a / b for a, b in zip(self.PXhi, self.PD)])
224:            self.fPYlo = np.array([a / b for a, b in zip(self.PYlo, self.PD)])
225:            self.fPYhi = np.array([a / b for a, b in zip(self.PYhi, self.PD)])
227:        self.fcores_iv = [tuple(float(q) for q in iv) for iv in self.cores_iv]
263:            WD = WD * w.denominator // math.gcd(WD, w.denominator)
270:            self.fW = np.array([float(w) for w in self.weights])
271:        self.fneed = float(self.need) - 1e-9
321:        eps = 1e-9
330:        a_hi = np.maximum(C0 * dx1, C1 * dx1)
331:        a_lo = np.minimum(C0 * dx0, C1 * dx0)
332:        b_hi = np.maximum(S0_ * dy1, S1 * dy1)
333:        b_lo = np.minimum(S0_ * dy0, S1 * dy0)
335:        a_hi = np.maximum(-S1 * dx0, -S0_ * dx0)
336:        a_lo = np.minimum(-S1 * dx1, -S0_ * dx1)
337:        b_hi = np.maximum(C0 * dy1, C1 * dy1)
338:        b_lo = np.minimum(C0 * dy0, C1 * dy0)
340:        return np.nonzero(ok)[0]
396:            fx = np.array([float(p[0]) for p in pts])
397:            fy = np.array([float(p[1]) for p in pts])
398:            idx = np.nonzero(VC.f_mass_mask(fx, fy, float(t), float(cx), float(cy), 1e-9))[0].tolist()
409:             "s_range_float": [float(sa), float(sb)]}
430:                          "s_float": float(ss), "t_float": float(tt),
431:                          "theta_deg": math.degrees(2 * math.atan(float(tt))),
432:                          "cx_float": float(fx), "cy_float": float(fy)}
434:        w["float_mass"] = float(m)
705:        print(f"FAIL: total {float(total):.6f} >= budget {budget}: certificate proves nothing")
710:    print(f"s in [{slo}, {shi}]  (~[{float(slo):.9f}, {float(shi):.9f}], width "
711:          f"{float(shi-slo):.9f}), n = {n}, atoms = {len(aff)}, cores = {len(cores)}, "
712:          f"budget = {budget}, total = {total} (~{float(total):.9f}), margin = {margin}")
```

### `C:\Users\esumm\code\packing\attempts\A27-close-384\verify_tree2.py`  -- 8 hit(s)

```
99:    through the same 1e-9 decimal map `q` the core construction uses, tilt in t-coordinates."""
200:    print(f"A27 case tree at s = {S} = {float(S)}   (t = tan(theta/2) parametrisation)")
223:    boxes, _ = cover(float(S), NX, NTH)
259:        boxeq = all(float(stored_box.get(kk, 1e9)) == getattr(Bx, kk)
274:                  f"contain={contain} (worst {float(worst):.6f}) verifier={okv} {tail}")
356:                  f"core covers the whole sigma-image (worst projection {float(F(s_['worst_proj'])):.6f} <= 0.5)")
367:        print(f"    ==> the tree is NOT closed: s(11) >= {float(S)} is NOT established here.")
371:        print(f"    ==> THEOREM: s(11) >= {S} = {float(S)}")
```

### `C:\Users\esumm\code\packing\attempts\A29-finish-384\verify_tree2.py`  -- 8 hit(s)

```
100:    through the same 1e-9 decimal map `q` the core construction uses, tilt in t-coordinates."""
192:    boxeq = all(float(stored_box.get(kk, 1e9)) == getattr(Bx, kk)
230:    print(f"A27 case tree at s = {S} = {float(S)}   (t = tan(theta/2) parametrisation)")
253:    boxes, _ = cover(float(S), NX, NTH)
294:                  f"contain={r['containment']} (worst {float(F(r['worst_proj'])):.6f}) "
377:                  f"core covers the whole sigma-image (worst projection {float(F(s_['worst_proj'])):.6f} <= 0.5)")
388:        print(f"    ==> the tree is NOT closed: s(11) >= {float(S)} is NOT established here.")
392:        print(f"    ==> THEOREM: s(11) >= {S} = {float(S)}")
```

### `C:\Users\esumm\code\packing\attempts\A37-cp-atlas\code\a37_check.py`  -- 34 hit(s)

```
5:Imports ONLY  mpmath.iv + fractions + json + math + glob + os + sys.  It uses
7:t3lib, not numpy, not scipy.  The order-2 interval jets and the row language
77:T_INSIDE = 1e-6
78:ACTIVE_TOL = 1e-20
95:    return max(math.nextafter(abs(float(x.a)), math.inf),
96:               math.nextafter(abs(float(x.b)), math.inf))
100:    return math.nextafter(float(iv.mpf(x).b), math.inf)
104:    return -math.nextafter(float((-iv.mpf(x)).b), math.inf)
108:    return sum(xs) * (1.0 + 1e-12) + 1e-300
329:    atol = max(ACTIVE_TOL, float(cert.get('active_tol', ACTIVE_TOL)))
408:    s0 = float(z0[S_IDX])
410:       abs(s0 - cert['claims']['s_center']) < 1e-12)
432:        W0 = sum_up([abs(float(om[k])) * gz[k] for k in range(n)
434:        ck('W %s W0' % tag, W0 <= v['W0'] * 1.0000001 + 1e-300,
447:        ck('G %s r_res' % tag, rres <= v['r_res'] * 1.0000001 + 1e-300,
454:        hf = float(h)
471:           row['V_soft'] <= worst + 1e-13,
478:        hf = float(h)
495:           cert['claims']['V_max'] <= worst + 1e-13,
514:    hf = float(h)
521:    e0 = sum_up([abs(float(om[k])) * gz[k] for k in range(n) if om[k] != 0])
523:    ck('Z %s eps_0' % tag, e0 <= cl['eps_0'] * 1.0000001 + 1e-300)
524:    ck('Z %s g_max' % tag, gmax <= cl['g_max'] * 1.0000001 + 1e-300)
535:    ck('G %s eps_w' % tag, ew <= cl['eps_w'] * 1.0000001 + 1e-300)
555:    kappa = max(sum_up([abs(float(Y[i][r])) for r in range(NV)])
560:    cvec = [max(abs(float(Y[i][r])) for i in range(NV)) for r in range(NV)]
561:    INF = float('inf')
563:            else max(cvec[i] / float(om[P[i]]) for i in range(NV)))
576:            if not math.isfinite(x):
590:       math.isfinite(x) and frac(cl['V']) <= Fraction(cl['v_lo']) - Fraction(x),
591:       'V %.18f vs v_lo - x* = %.6g' % (float(frac(cl['V'])), cl['v_lo'] - x))
595:                                   x, float(frac(cl['V']))))
643:                t['V_soft'] += 1e-3
645:                cert['claims']['V_max'] += 1e-3
```

### `C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\skeletons.py`  -- 2 hit(s)

```
137:             "slots_float": [[float(Fr(x)), float(Fr(y))] for (x, y) in c],
148:    print("Trump canonical:", [(float(x), float(y)) for x, y in trump_canon])
```

### `C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\skeletons2.py`  -- 1 hit(s)

```
101:             "slots_float": [[float(Fr(x)), float(Fr(y))] for (x, y) in cn],
```

### `C:\Users\esumm\code\packing\attempts\A57-shadow-trees\code\alivewitness.py`  -- 11 hit(s)

```
66:        co, si = math.cos(tt), math.sin(tt)
69:            g = oh * (abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot)) +
70:                      abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot)))
82:        obs.append(((float(c.kx), float(c.ky)), math.atan(float(c.tm)) * 2, float(c.a)))
91:        w = (math.cos(th) + math.sin(th)) / 2
145:        t = rat(math.tan(th / 2), tden)
158:                         theta_deg=float(math.degrees(2 * math.atan(float(t)))),
159:                         admissible=bool(adm), min_gap_to_cores=str(og), min_gap_float=float(og)))
194:    tilts = tuple(math.radians(float(x)) for x in a.tilts.split(","))
198:        ch = [((p[0], p[1]), math.radians(p[2])) for p in P]
220:        out.update(result="ALIVE-CERTIFIED", squares=recs, min_gap=str(gmin), min_gap_float=float(gmin),
```

### `C:\Users\esumm\code\packing\attempts\A22-local-rigidity\recheck.py`  -- 15 hit(s)

```
4:Verifies, using ONLY mpmath.iv validated interval arithmetic (+ fractions):
182:    return float(best.a)
205:            mx = max(mx, max(abs(float(g.a)), abs(float(g.b))))
235:            worst = max(worst, max(abs(float(Ki.a)), abs(float(Ki.b))) / float(r))
252:            m = 0.5 - max(abs(float(tan.a)), abs(float(tan.b)))
271:            mx = max(mx, max(abs(float(t.a)), abs(float(t.b))))
291:            numax = max(numax, float(nu))
303:                l1 += max(abs(float(rho.a)), abs(float(rho.b)))
343:                gap = float((projs[corner] - pc).a)
361:                    lo = float(val.a)
371:            wex = max(wex, max(abs(float(g.a)), abs(float(g.b))))
372:        if wex > 1e-40:
382:              % (self.cert['r_N'], float(self.rN), len(self.cert['S']),
405:        if corrupt == 'z0-big':      # centre off by 1e-3 > r_N
408:        elif corrupt == 'z0-small':  # centre off by 1e-8
```

---

## 3. SHA-256 + GIT CLEANLINESS

    git rev-parse HEAD = c9980bfcda1582d1e1a20126927a8a7d34ca1bb6

`porcelain` column = output of `git status --porcelain <file>` (empty = clean).

```
sha256   d568c9bcb5add16adb9077221d6834532d59a6d2d3338f69729702841f9a5ecc
  file   C:\Users\esumm\code\packing\certs\measure_certificate_3.80.json
  bytes  59684
  porcelain  (empty -> clean)

sha256   7d220c710a550174773c2b871c2c260154ac057fbbe23760eb70b2297a277929
  file   C:\Users\esumm\code\packing\certs\measure_certificate_3.81.json
  bytes  53901
  porcelain  (empty -> clean)

sha256   10d434dd63dfd4dfef3655112674c8cc74d3c66b820a6144ce54ecd63586df80
  file   C:\Users\esumm\code\packing\certs\measure_certificate_3.82.json
  bytes  96398
  porcelain  (empty -> clean)

sha256   2a735939d67f3a39a74a4bd0787df7f90d6f08b494e350bc36ae236725fa2121
  file   C:\Users\esumm\code\packing\certs\verify_measure.py
  bytes  38811
  porcelain  (empty -> clean)

sha256   9c81e1807bf0cd1add3ea74a6d402a6bd909c0a60f91e60b609743266de7227f
  file   C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureInt.lean
  bytes  10460
  porcelain  (empty -> clean)

sha256   3401f5d71cfbef469b5f50964675dc72c1647a9969790610724a9a885bafa986
  file   C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntData.lean
  bytes  48304
  porcelain  (empty -> clean)

sha256   7dd386517cf4df9e63e42ada44081d094e885b8ec9b2d3d55feb1b59d675025c
  file   C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntData381.lean
  bytes  44081
  porcelain  (empty -> clean)

sha256   4856650ebbd2df267d97a5545ea706893778fa61b3d9499a1c0af0269654911a
  file   C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\MeasureIntData382.lean
  bytes  77972
  porcelain  (empty -> clean)

sha256   a0d061cec300e988e85da6120efd90a9242e84001062baa12b541d88745ed251
  file   C:\Users\esumm\code\packing\lean\gen_measure_lean.py
  bytes  7924
  porcelain  (empty -> clean)

sha256   6505456ea2bd02c4623e2dd5aab3f2e29a1ca3954d63d4367ed98a4cde98a4d9
  file   C:\Users\esumm\code\packing\certs\trump11_certificate_int.json
  bytes  5398
  porcelain  (empty -> clean)

sha256   3170bd39701455192580d1a9011b16ddbd377cf8966c19bcb975d9ae772815ce
  file   C:\Users\esumm\code\packing\certs\verify_certificate.py
  bytes  6598
  porcelain  (empty -> clean)

sha256   33e3c13deed94d59f96b192254401d2c405054fe038c4b45a29e1368d092c3b2
  file   C:\Users\esumm\code\packing\lean\PackingCert\PackingCert\Checker.lean
  bytes  3014
  porcelain  (empty -> clean)

```

Also (for cross-reference; the canonical case-LP verifier):

```
sha256   521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af
  file   C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\verify_case.py
  bytes  47054
  porcelain  (empty -> clean)
sha256   0c58485c1a662453188af5b0aaf42099cf41c15f82a6647404598a44e8a505ec
  file   C:\Users\esumm\code\packing\attempts\A56-sparametric\code\verify_param.py
  bytes  36998
  porcelain  (empty -> clean)
sha256   f3f48cfecc19e78820d8453fa11a7b0dc7a752b7231356258f8745da63c5fd05
  file   C:\Users\esumm\code\packing\attempts\A37-cp-atlas\code\a37_check.py
  bytes  28827
  porcelain  (empty -> clean)
```

---

## 4. CERTIFICATE JSON FIELD NAMES + USAGE BLOCKS

Extraction regex (deduplicated, sorted):

```
\[(?:'|")([A-Za-z0-9_]+)(?:'|")\]   |   \.get\(\s*(?:'|")([A-Za-z0-9_]+)(?:'|")
```

NOTE: this is a syntactic sweep of ALL string-subscript / .get() accesses in the file;
it includes report/stat dict keys as well as certificate keys. Not classified.

### 4.1 `C:\Users\esumm\code\packing\attempts\A53-simple-strata\code\verify_case.py`

Deduplicated key names:

```
_budget
_cores
_nofams
a
atoms
boxes
budget
cap
cores
covered
cx_float
cy_float
depth_hist_covered
exact_atom_checks
exact_mass
exempt
exempt_core
exempt_nofam
float_mass
float_mass_interior_min
hypotheses
kind
kx
ky
max_depth
n
nofams
placement
s
split
symmetry
t_intervals
theta_deg
tm
total
v
vacuous
w
weights
witnesses
x
x0
x1
y
y0
y1
```

Raw `grep -n` of the key-access lines:

```
548:            w["placement"] = None
549:            w["kind"] = "undecided"
563:        w["placement"] = {"t": str(tt), "cx": str(fx), "cy": str(fy), "t_float": float(tt),
566:        w["exact_mass"] = str(m)
567:        w["float_mass"] = float(m)
569:            w["kind"] = "hole"          # rigorous: this admissible placement has mass < 1 + margin
571:            w["float_mass_interior_min"] = min_interior
573:            w["kind"] = "tight" if min_interior < float(self.need) - 1e-9 else "undecided"
575:            w["kind"] = "undecided"
671:    s = _rat(d["s"])
672:    n = int(n_override if n_override is not None else d.get("n", 11))
673:    raw_atoms = d["atoms"]
677:            atoms.append((_rat(a["x"]), _rat(a["y"])))
678:            weights.append(_rat(a["w"]))
680:        ws = d["weights"]
686:    sym = d.get("symmetry")
706:    hyp = d.get("hypotheses", {}) or {}
707:    cores = [CoreH(_rat(c["kx"]), _rat(c["ky"]), _rat(c["tm"]), _rat(c["a"])) for c in hyp.get("cores", [])]
711:    nofams = [NoFamH(_rat(f["x0"]), _rat(f["x1"]), _rat(f["y0"]), _rat(f["y1"]),
712:                     [(_rat(a), _rat(b)) for a, b in f["t_intervals"]]) for f in hyp.get("nofams", [])]
713:    budget = int(d.get("budget", n))
716:    d["_cores"], d["_nofams"], d["_budget"] = cores, nofams, budget
717:    if "total" in d and _rat(d["total"]) != total:
718:        print(f"WARNING: declared total {d['total']} != computed total {total} "
791:    _G["v"] = Verifier(s, atoms, weights, margin=margin, depth=depth, tscale=tscale,
793:    _G["cap"] = per_box_cap
797:    v = _G["v"]
799:    v.run([box], per_box_cap=_G["cap"])
862:    cores, nofams, budget = d["_cores"], d["_nofams"], d["_budget"]
888:                    print(f"  ... {done}/{len(boxes)} top boxes, {stats['boxes']} boxes, "
897:    stats["witnesses"] = len(witnesses)
901:    print(f"boxes = {stats['boxes']}  covered = {stats['covered']}  vacuous = {stats['vacuous']}  exempt = {stats.get('exempt',0)} "
902:          f"(core {stats.get('exempt_core',0)}, nofam {stats.get('exempt_nofam',0)})  "
903:          f"split = {stats['split']}  exact atom checks = {stats['exact_atom_checks']}  "
904:          f"max depth = {stats['max_depth']}  time = {elapsed:.1f}s")
907:              " ".join(f"{k}:{v}" for k, v in sorted(stats['depth_hist_covered'].items())))
916:        holes = [w for w in witnesses if w.get("kind") == "hole"]
917:        tight = [w for w in witnesses if w.get("kind") == "tight"]
918:        und = [w for w in witnesses if w.get("kind") == "undecided"]
923:        pick = min(witnesses, key=lambda w: w.get("float_mass", 9e9))
924:        if pick.get("placement"):
925:            p = pick["placement"]
926:            print(f"  worst witness: theta = {p['theta_deg']:.6f} deg, centre = ({p['cx_float']:.9f}, {p['cy_float']:.9f}), "
927:                  f"exact mass = {pick['exact_mass']} (~{pick['float_mass']:.12f})")
930:            p = w.get("placement")
933:            key = (round(p["theta_deg"]), round(p["cx_float"] / 0.05) * 0.05, round(p["cy_float"] / 0.05) * 0.05)
934:            cl.setdefault(key, []).append(w["float_mass"])
```

### 4.2 `C:\Users\esumm\code\packing\attempts\A56-sparametric\code\verify_param.py`

Deduplicated key names:

```
a
akx
aky
anchoring
atoms
ax
ay
bkx
bky
boxes
budget
bx
by
cap
cores
covered
cx_float
cy_float
exact_mass
exempt
float_mass
format
hypotheses
kind
max_depth
max_s_depth
n
name
nofams
placement
s
s_cells
s_float
s_range_float
s_splits
split
theta_deg
tm
total
v
vacuous
w
witnesses
```

Raw `grep -n` of the key-access lines:

```
425:            w["placement"] = None
426:            w["kind"] = "undecided"
429:        w["placement"] = {"s": str(ss), "t": str(tt), "cx": str(fx), "cy": str(fy),
433:        w["exact_mass"] = str(m)
434:        w["float_mass"] = float(m)
435:        w["kind"] = "hole" if m < self.need else "undecided"
527:    if p.get("format") != "parametric-kill-certificate-v1":
528:        raise ValueError(f"unexpected format {p.get('format')!r}")
529:    if p["hypotheses"].get("nofams"):
532:    for a in p["atoms"]:
533:        aff.append((_rat(a["ax"]), _rat(a["bx"]), _rat(a["ay"]), _rat(a["by"])))
534:        w = _rat(a["w"])
539:    for c in p["hypotheses"]["cores"]:
540:        cores.append(CoreP(_rat(c["akx"]), _rat(c["bkx"]), _rat(c["aky"]), _rat(c["bky"]),
541:                           _rat(c["tm"]), _rat(c["a"])))
544:    n = int(p.get("n", 11))
545:    budget = int(p["budget"])
549:    if _rat(p["total"]) != total:
550:        print(f"WARNING: declared total {p['total']} != computed {total}", file=sys.stderr)
659:    _G["v"] = PVerifier(aff, weights, cores, slo, shi, margin=margin, depth=depth, tscale=tscale,
661:    _G["cap"] = per_box_cap
665:    v = _G["v"]
667:    v.run([box], per_box_cap=_G["cap"])
709:    print(f"parametric certificate: {a.cert}  ({p.get('name')})")
713:    print(f"anchoring: {p.get('anchoring')}")
733:                    print(f"  ... {done}/{len(boxes)} top boxes, {stats['boxes']} boxes, "
743:    stats["witnesses"] = len(witnesses)
747:    print(f"boxes = {stats['boxes']}  covered = {stats['covered']}  vacuous = {stats['vacuous']}  "
748:          f"exempt = {stats['exempt']}  split = {stats['split']}  s-splits = {stats['s_splits']}  "
749:          f"s-cells = {stats['s_cells']}  max depth = {stats['max_depth']}  "
750:          f"max s-depth = {stats['max_s_depth']}  time = {elapsed:.1f}s")
757:        holes = [w for w in witnesses if w.get("kind") == "hole"]
760:        pick = min(witnesses, key=lambda w: w.get("float_mass", 9e9))
761:        if pick.get("placement"):
762:            q = pick["placement"]
763:            print(f"  worst witness: s = {q['s']} (~{q['s_float']:.9f}), theta = "
764:                  f"{q['theta_deg']:.6f} deg, centre = ({q['cx_float']:.9f}, {q['cy_float']:.9f}), "
765:                  f"exact mass = {pick['exact_mass']} (~{pick['float_mass']:.12f})")
766:        srs = [w["s_range_float"] for w in witnesses if "s_range_float" in w]
777:        srs = [w["s_range_float"] for w in witnesses if "s_range_float" in w]
779:            json.dump({"cert": a.cert, "name": p.get("name"), "slo": str(slo), "shi": str(shi),
783:                       "anchoring": p.get("anchoring"),
```

### 4.3 `verify_case.py` argparse / usage block (verbatim, lines 810-880)

```python
810:            acc[k] = max(acc.get(k, 0), val)
811:        else:
812:            acc[k] = acc.get(k, 0) + val
813:    return acc
814:
815:
816:def main(argv=None):
817:    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
818:    ap.add_argument("cert", nargs="?")
819:    ap.add_argument("--depth", type=int, default=48,
820:                    help="max number of bisections per box (default 48 ~ width 2^-16 of the root in each dim)")
821:    ap.add_argument("--strict-margin", type=str, default="0",
822:                    help="require exact covered mass >= 1 + m on every box (rational string)")
823:    ap.add_argument("--report", nargs="?", const="__auto__", default=None,
824:                    help="write a JSON report (default path <cert>.report.json)")
825:    ap.add_argument("--witness-file", type=str, default=None,
826:                    help="where to write witnesses on FAIL (default <cert>.witnesses.json)")
827:    ap.add_argument("--max-witnesses", type=int, default=200, help="stop after this many witness boxes in total")
828:    ap.add_argument("--max-witnesses-per-box", type=int, default=8,
829:                    help="stop exploring one of the 4^k initial boxes after this many witnesses (diversity)")
830:    ap.add_argument("--jobs", type=int, default=1, help="worker processes (each takes initial boxes from the 4^k split)")
831:    ap.add_argument("--split", type=int, default=3, help="k: the root is first split into 4^k boxes in (cx,cy)")
832:    ap.add_argument("--scale-weights", type=str, default="1",
833:                    help="multiply every weight by this rational before verifying (e.g. 1.00000001 to absorb LP rounding)")
834:    ap.add_argument("--tscale", type=str, default="2", help="weight of the t-width when choosing the split axis")
835:    ap.add_argument("--no-float-prepass", action="store_true", help="exact checks on ALL atoms (slow; for auditing)")
836:    ap.add_argument("--n", type=int, default=None, help="override n (default: certificate field or 11)")
837:    ap.add_argument("--selftest", action="store_true", help="random cross-check int vs Fraction predicates")
838:    ap.add_argument("--quiet", action="store_true")
839:    a = ap.parse_args(argv)
840:
841:    if a.selftest:
842:        return 0 if selftest() else 1
843:    if not a.cert:
844:        ap.error("certificate path required")
845:
846:    t_start = time.time()
847:    try:
848:        d, s, n, atoms, weights, total = load_certificate(a.cert, a.n)
849:    except Exception as e:
850:        print(f"MALFORMED certificate: {e}")
851:        return 2
852:    margin = F(a.strict_margin)
853:    scale = F(a.scale_weights)
854:    if scale != 1:
855:        weights = [w * scale for w in weights]
856:        total = sum(weights, ZERO)
857:        print(f"weights scaled by {scale}")
858:    verbose = not a.quiet
859:    print(f"certificate: {a.cert}")
860:    print(f"s = {s} (~{float(s):.10f}), n = {n}, atoms = {len(atoms)}, "
861:          f"total mass = {total} (~{float(total):.10f}), margin = {margin}")
862:    cores, nofams, budget = d["_cores"], d["_nofams"], d["_budget"]
863:    print(f"hypotheses: {len(cores)} cores, {len(nofams)} NO-families, budget = {budget}")
864:    if total >= budget:
865:        print(f"FAIL: total mass {float(total):.6f} >= budget = {budget}: certificate proves nothing")
866:        return 2
867:    if s < 1:
868:        print("s < 1: no unit square fits; vacuous PASS")
869:        return 0
870:
871:    use_float = not a.no_float_prepass
872:    v0 = Verifier(s, atoms, weights, margin=margin, depth=a.depth, tscale=F(a.tscale),
873:                  use_float=use_float, max_witnesses=a.max_witnesses, verbose=verbose, cores=cores, nofams=nofams)
874:    boxes = v0.root_boxes(a.split)
875:    stats = {}
876:    witnesses = []
877:    if a.jobs > 1:
878:        import multiprocessing as mp
879:        with mp.Pool(a.jobs, initializer=_worker_init,
880:                     initargs=(s, atoms, weights, margin, a.depth, F(a.tscale), use_float, a.max_witnesses,
```

### 4.4 `verify_param.py` argparse / usage block (verbatim, lines 665-735)

```python
665:    v = _G["v"]
666:    v.reset_stats()
667:    v.run([box], per_box_cap=_G["cap"])
668:    return v.stats(), v.witnesses
669:
670:
671:def main(argv=None):
672:    ap = argparse.ArgumentParser(description=__doc__,
673:                                 formatter_class=argparse.RawDescriptionHelpFormatter)
674:    ap.add_argument("cert", nargs="?")
675:    ap.add_argument("--slo", default=str(S_LO_WINDOW))
676:    ap.add_argument("--shi", default=str(S0))
677:    ap.add_argument("--depth", type=int, default=48)
678:    ap.add_argument("--sscale", default="8", help="weight of the s-width when choosing the axis")
679:    ap.add_argument("--tscale", default="2")
680:    ap.add_argument("--split", type=int, default=3)
681:    ap.add_argument("--jobs", type=int, default=1)
682:    ap.add_argument("--strict-margin", default="0")
683:    ap.add_argument("--report", nargs="?", const="__auto__", default=None)
684:    ap.add_argument("--witness-file", default=None)
685:    ap.add_argument("--max-witnesses", type=int, default=200)
686:    ap.add_argument("--max-witnesses-per-box", type=int, default=8)
687:    ap.add_argument("--no-float-prepass", action="store_true")
688:    ap.add_argument("--selftest", action="store_true")
689:    ap.add_argument("--quiet", action="store_true")
690:    a = ap.parse_args(argv)
691:
692:    if a.selftest:
693:        return 0 if selftest() else 1
694:    if not a.cert:
695:        ap.error("certificate path required")
696:
697:    t_start = time.time()
698:    try:
699:        p, n, budget, aff, weights, cores, total = load_param(a.cert)
700:        slo, shi = F(a.slo), F(a.shi)
701:    except Exception as e:
702:        print(f"MALFORMED certificate: {e}")
703:        return 2
704:    if total >= budget:
705:        print(f"FAIL: total {float(total):.6f} >= budget {budget}: certificate proves nothing")
706:        return 2
707:    margin = F(a.strict_margin)
708:    verbose = not a.quiet
709:    print(f"parametric certificate: {a.cert}  ({p.get('name')})")
710:    print(f"s in [{slo}, {shi}]  (~[{float(slo):.9f}, {float(shi):.9f}], width "
711:          f"{float(shi-slo):.9f}), n = {n}, atoms = {len(aff)}, cores = {len(cores)}, "
712:          f"budget = {budget}, total = {total} (~{float(total):.9f}), margin = {margin}")
713:    print(f"anchoring: {p.get('anchoring')}")
714:
715:    use_float = not a.no_float_prepass
716:    v0 = PVerifier(aff, weights, cores, slo, shi, margin=margin, depth=a.depth,
717:                   tscale=F(a.tscale), sscale=F(a.sscale), use_float=use_float,
718:                   max_witnesses=a.max_witnesses, verbose=verbose)
719:    boxes = v0.root_boxes(a.split)
720:    stats, witnesses = {}, []
721:    if a.jobs > 1:
722:        import multiprocessing as mp
723:        with mp.Pool(a.jobs, initializer=_worker_init,
724:                     initargs=(aff, weights, cores, slo, shi, margin, a.depth, F(a.tscale),
725:                               F(a.sscale), use_float, a.max_witnesses,
726:                               a.max_witnesses_per_box)) as pool:
727:            done = 0
728:            for st, ws in pool.imap_unordered(_worker, boxes):
729:                merge_stats_p(stats, st)
730:                witnesses.extend(ws)
731:                done += 1
732:                if verbose and (done % max(1, len(boxes) // 16) == 0):
733:                    print(f"  ... {done}/{len(boxes)} top boxes, {stats['boxes']} boxes, "
734:                          f"{len(witnesses)} witnesses, {time.time()-t_start:.0f}s", flush=True)
735:                if len(witnesses) >= a.max_witnesses:
```

---

## 5. ATLAS RE-CHECKER: `a37_check.py`

Path: `C:\Users\esumm\code\packing\attempts\A37-cp-atlas\code\a37_check.py`

Line count (`wc -l`): **719**

sha256: `f3f48cfecc19e78820d8453fa11a7b0dc7a752b7231356258f8745da63c5fd05`

### 5.1 Header (first 40 lines, verbatim)

```python
#!/usr/bin/env python
"""a37_check.py -- STANDALONE re-checker for A37 certificates
(results/certs/fam*_3R.json, fam*_3S.json).   Cookbook step 4.

Imports ONLY  mpmath.iv + fractions + json + math + glob + os + sys.  It uses
NO producer library: not a37_pipeline, not a36_lib, not strata_lib, not
t3lib, not numpy, not scipy.  The order-2 interval jets and the row language
below are transcribed (with attribution) from A36's own standalone re-checker
attempts/A36-levers/code/a36_check.py, which in turn transcribes A35's
m2_check_inflation.py.

The checker does NOT trust the producer's row list, safety flags, branch sets
or omega support.  From the certificate's CONTACT TABLE alone it

  [R] rebuilds every row and compares with the producer's implied row order;
  [C] re-verifies that every row is ACTIVE at z_center;
  [S] recomputes the [V] safety flag of every sep row from the tangential
      coordinate at z_center (a producer that marked an endpoint row "safe"
      fails here);
  [B] recomputes the branch structure: for every pair carrying a non-[V]-safe
      row it re-runs the kill test on box(z_center, h_probe) and checks that
      the certificate's live-axis set CONTAINS every axis the checker cannot
      kill, and that the certificate enumerates the full product of live axes;
  [O] sign discipline: omega >= 0, omega = 0 on every row not valid in that
      variant (rows outside the variant's chosen axis, or non-safe rows of an
      unbranched pair);
  [W] W0 = sum |omega_r| |g_r(z_center)|;
  [G] r_res = ||A(z_center)^T omega - e_s||_1;
  [H] Hbar(h) = (1/2) sum_ij sup_box |d^2 W / dz_i dz_j|;
  [V] tangential/depth margins of every omega-loaded sep row on box(h);
  [X] V_soft(h) = min over variants of  s_center - W0 - r_res h - Hbar h^2
      (with the trivial coordinate bound s_center - h substituted whenever a
      variant's [V] margins fail), and V_claimed <= V_recomputed.

For a 3R certificate it additionally checks the A36 max-form chain
  [K] beta = sup ||I - Y A_P||_inf < 1, kappa = ||Y||_inf;
  [E] kappa_eff = max_{r in P} (max_i |Y_ir|) / omega_r;
  [P] psi(h) = (kappa_eff E(h) + kappa g_max)/(1-beta) < h and the least fixed
      point x* of x -> kappa_eff E(x)/(1-beta) + kappa g_max/(1-beta) is <= h;
  [F] V <= v_lo - x*.
```

### 5.2 Deduplicated JSON / dict key accesses

```
Hbar
P
V
V_max
V_soft
V_target
W0
Y
active_tol
axes
beta
branched
choice
claims
contact_table
corner
edge
eps_0
eps_w
family_id
g_max
h
h_max
h_probe
i
j
kappa
kappa_eff
kind
mode
omega_rational
other
owner
pair
r_res
rowspecs
s_center
safe
table
type
v_lo
variants
wall
z_center
```

### 5.3 Raw `grep -n` of the key-access lines

```
181:    if c['kind'] == 'wall':
182:        i = c['i']
184:        if c['wall'] in ('x=s', 'y=s'):
187:    if c['kind'] == 'edge':
188:        i, j = c['i'], c['j']
190:    if c['kind'] == 'dist':
191:        i, j = c['i'], c['j']
193:    raise ValueError(c['kind'])
201:    if c['kind'] == 'wall':
203:        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
207:        w = c['wall']
214:    if c['kind'] == 'edge':
216:        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
220:        nhx, nhy = NHAT[c['edge']]
225:    if c['kind'] == 'dist':
229:    raise ValueError(c['kind'])
242:    i, j, k, e = c['i'], c['j'], c['corner'], c['edge']
273:        if e['type'] == 'wall':
274:            rows.append({'kind': 'wall', 'i': e['i'], 'corner': e['corner'],
275:                         'wall': e['wall']})
278:        if e['type'] == 'pair':
279:            for s in e['rowspecs']:
280:                rows.append({'kind': 'edge', 'i': s['other'],
281:                             'corner': s['corner'], 'j': s['owner'],
282:                             'edge': s['edge']})
283:                kind.append(('pair', (e['i'], e['j']),
284:                             (s['owner'], s['edge'])))
286:        if e['type'] == 'aux':
287:            rows.append({'kind': 'dist', 'i': e['i'], 'j': e['j']})
320:    z0 = [frac(x) for x in cert['z_center']]
322:    tab = cert['contact_table']
325:    tag = 'fam%02d/%s' % (cert['family_id'], cert['mode'])
329:    atol = max(ACTIVE_TOL, float(cert.get('active_tol', ACTIVE_TOL)))
336:        if c['kind'] != 'edge':
343:        if e['type'] == 'pair':
344:            declared += [bool(s['safe']) for s in e['rowspecs']]
351:    hprobe = frac(cert['h_probe']) if 'h_probe' in cert else None
352:    branched = {tuple(b['pair']): [tuple(a) for a in b['axes']]
353:                for b in cert.get('branched', [])}
357:    if cert['mode'] == '3S':
358:        omsets = [[frac(x) for x in v['omega_rational']]
359:                  for v in cert['variants']]
361:        omsets = [[frac(x) for x in cert['omega_rational']]]
376:                for c in itertools.product(*[branched[tuple(b['pair'])]
377:                                             for b in cert['branched']])]
378:        got_v = [tuple(tuple(a) for a in v['choice'])
379:                 for v in cert['variants']]
384:    if cert['mode'] == '3S':
410:       abs(s0 - cert['claims']['s_center']) < 1e-12)
411:    order = [tuple(tuple(a) for a in b['axes']) for b in cert['branched']]
412:    prs = [tuple(b['pair']) for b in cert['branched']]
414:    for v in cert['variants']:
415:        om = [frac(x) for x in v['omega_rational']]
417:        sel = dict(zip(prs, [tuple(a) for a in v['choice']]))
434:        ck('W %s W0' % tag, W0 <= v['W0'] * 1.0000001 + 1e-300,
435:           'recomputed %.3e vs claimed %.3e' % (W0, v['W0']))
447:        ck('G %s r_res' % tag, rres <= v['r_res'] * 1.0000001 + 1e-300,
448:           'recomputed %.3e vs claimed %.3e' % (rres, v['r_res']))
452:    for row in cert['claims']['table']:
453:        h = frac(row['h'])
461:                if om[k] == 0 or rows[k]['kind'] != 'edge' or not safe[k]:
470:        ck('X %s V_soft(h=%s)' % (tag, row['h']),
471:           row['V_soft'] <= worst + 1e-13,
472:           'claimed %.15f vs recomputed %.15f' % (row['V_soft'], worst))
474:            print('  [ok] %s h=%-12s V_soft >= %.12f' % (tag, row['h'], worst))
475:    hm = cert['claims'].get('h_max')
485:                if om[k] == 0 or rows[k]['kind'] != 'edge' or not safe[k]:
495:           cert['claims']['V_max'] <= worst + 1e-13,
496:           'claimed %.15f vs recomputed %.15f' % (cert['claims']['V_max'],
499:                                                       cert['claims']['V_target']),
500:           worst >= cert['claims']['V_target'],
510:    P = list(cert['P'])
511:    Y = [[frac(v) for v in r] for r in cert['Y']]
512:    om = [frac(x) for x in cert['omega_rational']]
513:    h = frac(cert['h'])
515:    cl = cert['claims']
523:    ck('Z %s eps_0' % tag, e0 <= cl['eps_0'] * 1.0000001 + 1e-300)
524:    ck('Z %s g_max' % tag, gmax <= cl['g_max'] * 1.0000001 + 1e-300)
535:    ck('G %s eps_w' % tag, ew <= cl['eps_w'] * 1.0000001 + 1e-300)
537:    ck('H %s Hbar' % tag, Hbar <= cl['Hbar'] * 1.0000001,
538:       'recomputed %.6f vs claimed %.6f' % (Hbar, cl['Hbar']))
557:    ck('K %s beta < 1' % tag, beta < 1.0 and beta <= cl['beta'] * 1.0000001,
558:       'recomputed %.8f vs claimed %.8f' % (beta, cl['beta']))
559:    ck('K %s kappa' % tag, kappa <= cl['kappa'] * 1.0000001)
564:    ck('E %s kappa_eff' % tag, keff <= cl['kappa_eff'] * 1.0000001,
582:        if om[k] == 0 or rows[k]['kind'] != 'edge':
590:       math.isfinite(x) and frac(cl['V']) <= Fraction(cl['v_lo']) - Fraction(x),
591:       'V %.18f vs v_lo - x* = %.6g' % (float(frac(cl['V'])), cl['v_lo'] - x))
594:              'x*=%.2e V=%.12f' % (tag, cert['h'], beta, Hbar, keff, psi / hf,
595:                                   x, float(frac(cl['V']))))
600:    if cert['mode'] == '3S':
601:        vs = cert['variants']
604:                for k, x in enumerate(v['omega_rational']):
606:                        v['omega_rational'][k] = '-' + x
609:            for t in cert['claims']['table']:
610:                g = frac(t['h']) * 8
611:                t['h'] = '%d/%d' % (g.numerator, g.denominator)
612:            if cert['claims'].get('h_max'):
613:                g = frac(cert['claims']['h_max']) * 8
614:                cert['claims']['h_max'] = '%d/%d' % (g.numerator, g.denominator)
616:            idx = [k for k, e in enumerate(cert['contact_table'])
617:                   if e['type'] == 'aux']
618:            rows, kind = rebuild(cert['contact_table'])
625:            if not any(frac(v['omega_rational'][k]) != 0
630:                    v['omega_rational'][k] = '0/1'
632:            rows, kind = rebuild(cert['contact_table'])
633:            prs = set(tuple(b['pair']) for b in cert['branched'])
640:                    v['omega_rational'][k] = '0/1'
642:            for t in cert['claims']['table']:
643:                t['V_soft'] += 1e-3
644:            if cert['claims'].get('V_max') is not None:
645:                cert['claims']['V_max'] += 1e-3
651:        cert['omega_rational'][cert['P'][0]] = \
652:            '-' + cert['omega_rational'][cert['P'][0]]
654:        g = frac(cert['h']) * 8
655:        cert['h'] = '%d/%d' % (g.numerator, g.denominator)
657:        rows, kind = rebuild(cert['contact_table'])
659:        if not any(frac(cert['omega_rational'][k]) != 0 for k in pos):
662:            cert['omega_rational'][k] = '0/1'
666:        v = Fraction(round(Fraction(frac(cert['claims']['V']) + Fraction(1,
668:        cert['claims']['V'] = '%d/%d' % (v.numerator, v.denominator)
```

### 5.4 Entry point / usage block (verbatim, lines 668-719)

```python
668:        cert['claims']['V'] = '%d/%d' % (v.numerator, v.denominator)
669:    else:
670:        raise SystemExit('unknown corruption mode %s' % mode)
671:    return True
672:
673:
674:def main():
675:    here = os.path.dirname(os.path.abspath(__file__))
676:    args = list(sys.argv[1:])
677:    corrupt = None
678:    if '--corrupt' in args:
679:        i = args.index('--corrupt')
680:        corrupt = args[i + 1]
681:        del args[i:i + 2]
682:    cdir = args[0] if args else os.path.join(here, '..', 'results', 'certs')
683:    files = sorted(glob.glob(os.path.join(cdir, 'fam*.json')))
684:    if not files:
685:        print('no certificates in %s' % os.path.abspath(cdir))
686:        return 1
687:    if corrupt:
688:        print('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
689:    print('re-checking %d certificates in %s'
690:          % (len(files), os.path.abspath(cdir)))
691:    ck = Check()
692:    applied = 0
693:    for f in files:
694:        cert = json.load(open(f))
695:        if corrupt:
696:            if not corrupt_cert(cert, corrupt):
697:                print('  (%s: corruption %s not applicable)'
698:                      % (os.path.basename(f), corrupt))
699:                continue
700:            applied += 1
701:        check_cert(cert, ck, verbose=True)
702:    if corrupt:
703:        if applied == 0:
704:            print('corruption test %s: NOT APPLICABLE to any certificate'
705:                  % corrupt)
706:            return 3
707:        bad = bool(ck.fails)
708:        print('corruption test %s: %s' % (
709:            corrupt, 'OK (checker failed as required)' if bad
710:            else 'PROBLEM: checker still passes!'))
711:        return 0 if bad else 2
712:    print('  %d certificates, %d checks' % (len(files), ck.n))
713:    print('=> %s' % ('ALL CHECKS PASS' if not ck.fails
714:                     else 'FAILURES: %s' % sorted(set(ck.fails))[:8]))
715:    return 0 if not ck.fails else 1
716:
717:
718:if __name__ == '__main__':
719:    sys.exit(main())
```

---

END OF RAW DATA.
