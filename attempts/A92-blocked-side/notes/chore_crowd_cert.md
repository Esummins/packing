# A92 chore — the CROWD-WEIGHTED root certificate (route 3 of the A92 BRIEF, exact definitions)

Lead: Fable (A92). Executor: Opus (one compute chore). Everything in this file is a DEFINITION or a
RUN ORDER; the soundness lemma (Lemma CW) and the transfer lemma (Lemma B-YES) are proved in
`docs/proofs/k0_blocked_side.md` §2; the chore must implement exactly these objects.

## 0. Why the brief's "K-leaf with 8 non-empty cores" does not exist, and what replaces it

The brief assumed the pose set D_c(delta) := {Q admissible : depth_c(Q) >= delta} has a non-empty
core (a point common to every such Q). It does not, for every delta < 0.134 (two hanging squares:
the left-wall square with tilt 60 deg whose lowest vertex is (1/2, 1-delta) and its bottom-wall
mirror have no common point when 1 - 2 delta > 0.732 — see `k0_blocked_side.md` §2.0), and the
frozen `verify_case.py` semantics (cores = containment hypotheses; NO-families = exemptions) cannot
express "some square lies in D_c(delta)" without branching over a cover of D_c(delta) — the A85 pair
tree, priced dead. The replacement is a WEIGHTED measure certificate, verified by TWO runs of the
frozen verifier on ONE measure (Lemma CW):

  mu(Q) >= 1       for every admissible closed unit square Q in [0,s0]^2            (run A)
  mu(Q) >= 1 + e   for every admissible Q meeting the closed box [0,a_w]^2 at some corner (run B)
  mu(total) < 11 + 8e                                                                (run A's n)

For a packing with two such squares at every corner (8 distinct squares, CC-1(ii)) and 3 others,
sum_i mu(Q_i) >= 8(1+e) + 3 = 11 + 8e > mu(total): contradiction. Run B is the frozen verifier on
the SAME atoms with weights w/(1+e), NO-families = an inner cover of the COMPLEMENT of the crowd
family, and a dummy n (its "total < n" clause is not used; only its coverage clause is).

## 1. Constants and the exact families

* s0 = 969271/250000, lambda_max = s0/3.82 = 969271/955000 (window [3.82, s0), Lemma B-YES).
* For delta in (0, 1): the WIDENED box side (exact rational, rounded UP at the last step)

      a_w(delta) := lambda_max * (1 - delta) + (lambda_max - 1) * 7072/10000

  (7072/10000 >= sqrt2/2). Values: delta 0.3 -> 0.72103; 0.25 -> 0.77178; 0.2 -> 0.82252;
  0.15 -> 0.87327; 0.1 -> 0.92402; 0.05 -> 0.97477. a_w < 1 iff delta > 0.0254: do NOT run
  delta <= 0.03 (the canary would fire: Trump's tangent squares 1, 8, 9 enter the family at a_w >= 1).
* Corner frame of c in {BL, BR, TL, TR}: the D4 map sending c to the origin, exactly as
  `o3run.corner_depth_table` (u = x or s0-x, v = y or s0-y, t -> (1-t)/(1+t) for reflected frames).
* f(cx, cy, t) := min over Q(cx, cy, theta) of max(x, y) in the corner frame = `corner85.f_min_max`
  (exact Fractions). Q meets the CLOSED box [0,a]^2 iff f <= a. Facts (A89 o3fam, proved there):
  f is nondecreasing in cx and in cy; f is (sqrt2/2)-Lipschitz in theta (radians).
* Crowd family at c: F_c(a) := {admissible (cx, cy, theta) at s0 : f_c(cx, cy, t) <= a}.
* OUTER COVER G_c ⊇ F_c(a_w): a finite union of caselp-style boxes R = [x0,x1] x [y0,y1] x
  [T0,T1] (corner-frame centre rect x theta interval, theta edges at multiples of 1/4 deg exactly as
  `o3fam`, bit-exactly D4-closed across the four corners via `o3fam.corner_fams`-style mapping).
  A box R is provably DISJOINT from F_c(a) iff  f(x0, y0, t_i) - (sqrt2/2) * dtheta/2 > a  for
  every t_i of an exact theta grid of step dtheta over [T0,T1] (min of f over the rect is at the
  lower-left corner; the Lipschitz pad covers the grid gaps). Build G_c as: partition the corner
  region [1/2 - 1/20, a_w + 3/4]^2 (centre coordinates; a pose meeting [0,a_w]^2 has centre
  coordinates <= a_w + sqrt2/2 < a_w + 3/4) x [0, 90] deg into cells (suggest 0.02 x 0.02 x 1 deg,
  then merge per 7 theta bins into a staircase of <= 12 rects each, as in o3fam but with the
  test REVERSED: keep every cell NOT provably disjoint). Certify exactly (Fractions) that every
  dropped cell is provably disjoint, and report the coverage overshoot of G_c over F_c(a_w) by
  exact sampling (aim <= 15 %).
* COMPLEMENT COVER E: a finite union of caselp `NoFam` boxes with E ∩ G_c = ∅ for all c (exact
  rational comparisons on every pair; assert), covering everything else in the admissible domain
  [1/2, s0 - 1/2]^2 x [0, 90] deg. (Per theta bin the four corner staircases are disjoint from
  each other; the complement is a rectilinear region — decompose into strips.) Anchor outer edges
  at 0.45 / s0 - 0.45 exactly as o3run does for NO-families (the verifier's domain-edge boxes).

## 2. The LP (a COPY of the A89 stack, modified; nothing under A85/A89 is written)

Copy `attempts/A89-tilt-floor/code/{blas1,caselp,lpbox,certify,verify_case,class85,corner85,
o3fam,alivewitness,pinguard,...}.py` and `results/witnesses_k0_00.json` into
`attempts/A92-blocked-side/code/` (verbatim, as A89 did from A85). Then add `caselp92.py` /
`certify92.py` (copies with the ONE change below) and `crowd92.py` (the driver).

Change: every LP row for a pose Q has right-hand side  rhs(Q) = 1 + e * [Q in G]  where "Q in G"
is decided CONSERVATIVELY for the LP (a pose is treated as in G unless its centre is outside every
G-rect of its corner by EPS_ZONE = 2e-3 or its theta outside the rect's theta interval by EPS_TH =
0.3 deg — i.e. more rows at 1+e, never fewer; cf. caselp's NoFam margins in the opposite sense).
Objective unchanged: min mu(total). D4 quotient (`sym_kind="D4"`) — the hypothesis is
D4-symmetric; assert `Hyp.is_symmetric_D4`-style bit-exact closure of G. The row ORACLE
(RowOracle.scan_theta / exact_theta / refine) must search for poses with coverage < rhs(Q), not
< 1. Warm pool as o3run. The certificate builder (certify92) must use the same rhs in its
witness-feedback re-solves.

PASS criterion of the LP: tau < 11 + 8e (integer n = 11 + 8e: e in {1/4, 1/2, 1, 2} -> n = 13,
15, 19, 27). Report eta := tau - (11 + 8e), minmass, maxcov, rows, LP seconds.

## 3. The certificate = TWO frozen-verifier files from ONE (atoms, weights)

* `runA_<tag>.json`: format `case-lp-certificate-v1`, s = "969271/250000", n = 11 + 8e, budget =
  n, atoms + weights w, symmetry D4, hypotheses = {cores: [], nofams: []}. PASS iff rc = 0.
* `runB_<tag>.json`: same atoms, weights w/(1+e) (exact rationals), n = 1000, budget = 1000,
  hypotheses = {cores: [], nofams: E}. PASS iff rc = 0 (coverage clause: every non-exempt box has
  mass >= 1 in the halved measure, i.e. mu >= 1+e on every pose not provably in E, hence on all of
  G ⊇ F(a_w)). Its "total < 1000" clause is a dummy.
* Both verified with the FROZEN `verify_case.py` (the A89 copy, byte-identical to A85's) at
  --depth 56, --jobs 1. Keep .report.json / .witnesses.json. eps_geo repair 0.002 / 0.004 as A85
  on a FAIL (re-solve with the same weighted rows).
* `<tag>.PASS` written only if BOTH runs pass. Record sha256 of both files in the run record.

## 4. Canaries (refuse before any LP)

* `images_realizing`: an image (the 8 D4 Trump images of `witnesses_k0_00.json`) REALISES the crowd
  hypothesis at a_w iff every corner has >= 2 placements with f_c <= a_w (exact, as
  `o3run.corner_depth_table` computes f per placement). Expected: EMPTY for every a_w < 1 (every
  image has at most one corner with 2 placements below 1: TL's 0.8317/0.8445; the tangent squares
  1/8/9 have f = 1 exactly). Print the per-image per-corner counts; REFUSE if any image realises.
* Post-check: a PASS on a realisable node is an ENGINE BUG (exit 9), as in o3run.
* Not in scope (side > s0): the certified K0-BLOCKED packings of d2front87 at 4.03-4.36 and s0115
  (3.985) — they must not be checked against this certificate at all; note it in the log.

## 5. Run order (one LP process at a time; BLAS pinned; free commit > 6144 MB before every LP and
## every certify, 60-s sleep-and-recheck; at most 2 processes in total incl. this driver)

Phase 1 — (S), the D2^4 pattern: for delta in [0.3, 0.2, 0.1, 0.05] and e in [1, 1/2, 2, 1/4]
(that order; skip the remaining e for a delta once one PASSes the LP), lp_time 900 s, LP-ONLY.
Then certify (cert_time 300 s, two witness rounds, eps_geo repair) the LP-passing nodes in the
order: largest delta first, then the smallest delta that passed. Stop certifying after 2 PASSes
+ 1 FAIL or when the wall budget is gone.

Phase 2 — mixed patterns for (N) (only if Phase 1 produced at least one LP pass; use the smallest
passing delta as delta2 and e2 = its e; delta1 = 0.2 with e1 = e2), LP-only, 900 s each, in this
order; certify only a PASS that the lead asks for:
  P2a  (D1, D2, D2, D2)         : one corner has >= 1 square in F_c(a_w(delta1)) at weight e1,
                                  the other three have >= 2 in F_c(a_w(delta2)) at weight e2;
                                  budget 11 + e1 + 6 e2. Representative TL for D1 (D4 orbit).
  P2b  (D1, D1, D2, D2) adjacent (BL, BR | TL, TR) and P2c diagonal (BL, TR | BR, TL).
  P2d  (D1, D1, D1, D2).
  P2e  (D1, D1, D1, D1) at delta1 = 0.2   [Trump-realised for delta1 <= 0.1683 — assert not here].
  P2f  (S, D2, D2, D2): TL SHALLOW(delta1) as the o3fam NO-family set at a_win(delta1) (exempt),
                                  BL, BR, TR at weight e2; budget 11 + 6 e2.
The general certificate for a pattern: families G_c^(k) with weight e_k and multiplicity m_k per
corner; run A with n = 11 + sum_c m_c e_c; one run B per distinct weight (weights w/(1+e_k),
NO-families = complement of the union of the weight-e_k families); exempt NO-families of S corners
are added to run A as caselp nofams (as o3run) and the LP drops those rows. The canary for every
pattern: no image may have, at every corner, the pattern's counts (S: no placement with
f < a_win(delta1); D1: >= 1 placement with f <= a_w(delta1); D2: >= 2 with f <= a_w(delta2)).

## 6. Outputs

`attempts/A92-blocked-side/{code,results,certs,logs}`; `results/crowd92_runs.jsonl` (one record
per LP: tag, pattern, delta(s), e, a_w (rational string), n_G_boxes per corner, n_E_boxes, overshoot,
canary counts, tau, eta, minmass, maxcov, rows, lp_s, cert verdicts A/B, cert_s, sha256s);
`notes/crowd92_report.md` with: the table of (delta, e) -> tau, eta, verdict; the two-run
certificate paths; the family statistics; the canary table; exact resource discipline used.
Report tersely to the lead: the largest delta with a CERTIFIED PASS first (that is (S)'s boundary
in delta; the side boundary is s0), then the LP-only table, then Phase 2.
