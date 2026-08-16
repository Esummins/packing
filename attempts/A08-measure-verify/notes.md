# A08-measure-verify — independent exact verifier for measure certificates (lower bounds)

Owner: verification postdoc. Date: 2026-08-16. Deliverable: `certs/verify_measure.py` (+ `certs/README.md`).
Working files here: `make_tests.py` (synthetic certificates -> `tests/`), `convert_a07.py` (A07 raw LP
results -> certificate format, `a07/`), `witnesses_*.json`, `report_*.json`.

## 1. Goal

Given a measure certificate (atoms p_i, weights w_i >= 0, side s, total < n), decide with exact
arithmetic whether every closed unit square Q inside [0,s]^2 has mu(Q) >= 1. If yes, s(n) >= s.
Written from scratch, sharing no code with A07 (producer) or A05's `verify_unavoidable.py`.

## 2. Mathematics used (all of it)

**Bridge.** If n unit squares with pairwise disjoint interiors fit in a square of side s' < s, scale
by s/s' > 1 (now side s, squares of side s/s' > 1, disjoint interiors) and shrink every square about
its centre to side 1: the closed unit squares are pairwise disjoint and lie in [0,s]^2. Each has
mu >= 1, so mu([0,s]^2) >= n > total: contradiction. Hence s(n) >= s. (Note the conclusion is
`>= s`, not `> s`; a packing of side exactly s is not excluded by the certificate.)

**Orientation.** Q(c,theta) = Q(c,theta+pi/2), so theta in [0,pi/2] covers every unit square.
With t = tan(theta/2) in [0,1]: cos = (1-t^2)/(1+t^2) decreasing, sin = 2t/(1+t^2) increasing on
[0,1] (derivatives -4t/(1+t^2)^2 <= 0 and 2(1-t^2)/(1+t^2)^2 >= 0). So on [t0,t1] the enclosures
cos in [cos(t1), cos(t0)], sin in [sin(t0), sin(t1)] are exact rationals and are tight.

**Admissibility.** Q(c,theta) inside [0,s]^2 iff w/2 <= cx, cy <= s - w/2 with w = cos+sin
(the axis-parallel bounding box of Q has side w). w = sqrt2 sin(theta+pi/4) is concave in theta on
[0,pi/2] and theta = 2 arctan t is monotone, so w(t) is unimodal: min over [t0,t1] at an endpoint,
w_min = min(w(t0), w(t1)) is an exact rational lower bound. Every admissible centre lies in
[1/2, s-1/2]^2 since w >= 1 (root box).

**Containment.** p in Q(c,theta) iff |u| <= 1/2 and |v| <= 1/2, u = cos(px-cx)+sin(py-cy),
v = -sin(px-cx)+cos(py-cy). Interval arithmetic (products of the cos/sin enclosure with the
(px-cx), (py-cy) intervals, sums) over-approximates the range of u, v over the box; if the
over-approximation lies in [-1/2,1/2] the atom is inside for every placement of the box (sound).
Atoms certified for a box are certified for its sub-boxes (inherited by the children).

**Discharge rule.** Box B = [t0,t1]x[x0,x1]x[y0,y1]. (a) clip [x0,x1], [y0,y1] to
[w_min/2, s-w_min/2] (rounded OUTWARD to the integer grid) — the clipped box still contains every
admissible placement of B; empty => vacuous. (b) covered if sum of weights of atoms certified inside
the clipped box >= 1 + margin. Else bisect the widest side (t-width x tscale=2) of the clipped box
and recurse; at depth >= D the box is a FAIL witness. Coverage of the admissible parameter set by
the leaves is by construction (children cover the parent; clipping only removes inadmissible
placements). PASS => mu(Q) >= 1+margin for every admissible Q. FAIL is *not* a disproof (box
methods are incomplete, see §5) unless a witness of kind `hole` is reported: then an explicit
admissible placement with exact mass < 1 is given (rigorous counterexample).

## 3. Implementation

`certs/verify_measure.py`, stdlib only for the exact path (ints / fractions.Fraction); numpy only for
(i) a per-box float shortlist of atoms that *might* be inside (slack 1e-9; a wrong shortlist can only
cause a spurious split/FAIL, never a wrong PASS) and (ii) sample placements in witnesses.

- Integer core: lengths scaled by D = den(s) * 2^(depth+2) so every bisection point is an integer;
  t scaled by 2^K, K = depth+1; for T = t 2^K: cos = (4^K - T^2)/(4^K + T^2), sin = 2T 2^K/(4^K+T^2);
  the four enclosure bounds are brought to the common denominator E = dn(t0) dn(t1); each atom keeps
  its own denominator PD; weights are integers over the lcm WD of their denominators, need =
  ceil((1+margin) WD). One containment test = 16 big-int products + comparisons, ~3-10 us
  (vs ~120 us with Fraction: the gcd normalisation and comparison overhead of Fraction dominated).
- A Fraction reference implementation of the same predicates is kept; `--selftest` cross-checks the
  two on 3000 random boxes and spot-checks soundness at random placements (0 mismatches).
- Children inherit the certified atom list + mass; float-shortlisted atoms are certified exactly even
  in boxes that will be split (18x fewer exact checks on the A07 stress test).
- Root split into 4^k boxes (`--split`, default 3); `--jobs J` (multiprocessing, <= 4 here);
  `--max-witnesses`, `--max-witnesses-per-box` (default 8: gives spatially diverse witnesses instead
  of 200 witnesses from the first hole met by the DFS); `--strict-margin m`; `--scale-weights r`;
  `--report [path]` (JSON with box counts, depth histogram, timings); `--depth D` (default 48 =
  three dimensions x 16 halvings = width 2^-16 of the root); `--n`; `--no-float-prepass`.
- Witnesses: for each failing leaf a few admissible sample placements (box centre/corners; admissibility
  checked exactly) are evaluated EXACTLY (float pre-filter with slack + exact decision on survivors);
  the least mass is reported with the exact rational. Kinds: `hole` (exact mass < need), `tight`
  (mass >= need but < need once atoms within 1e-9 of the boundary of Q are excluded => tangency),
  `undecided`. A coarse cluster summary (theta ~1 deg, centre ~0.05) is printed.

## 4. Tests (all in `tests/`, generated by `make_tests.py`; timings single process unless noted, this
machine, after the clipping + inheritance optimisations)

| certificate | expected | result | boxes | time |
|---|---|---|---|---|
| centre atom (s/2,s/2), w=1, s=1.99, n=2 | PASS (every unit square in [0,s]^2, s<=2, contains the centre: |u| <= w(2-w)/2 <= 1/2) | PASS | 2 462 | 0.1 s |
| same, s=2.01 | FAIL | FAIL, holes at the corner square, mass 0 | 462 | 0.1 s |
| same, s=2 exactly | boundary case: not certifiable (corner square has the atom on its corner) | FAIL, `undecided`/`tight` witnesses at (t=0, c=(1/2,1/2)) | — | 0.0 s |
| Göbel (1,1),(1,s-1),(s-1,1),(s-1,s-1), s=2.70610678 (= 2+1/sqrt2 - 1e-3), n=5 | advisor: PASS | **FAIL (tight)** — see §5: (1,1) lies exactly on the boundary of the admissible corner square [0,1]^2 at every s; a box method cannot certify it | 915 | 0.0 s |
| Göbel robustified: points moved by delta=4e-4 toward the corners, s=2.70610678 (critical becomes 2+1/sqrt2-2delta = 2.70630678) | PASS | **PASS** | 50 962 | 1.7 s |
| same points, s=2.72 | FAIL | **FAIL, 24 holes**, e.g. theta=33.8 deg, centre (1.36,1.36), exact mass 0 | 47 586 | 1.6 s |
| delta=2e-4, s=2.7065 (2e-4 below its critical value) | PASS | PASS | (853 539 before clipping, 36 s) | ~3 s |
| A05's 10-point set, s0=1870797/500000, weights 1, total 10, n=11 | PASS (A05's own verifier passed) | **PASS** — independent confirmation of s(11) >= 3.741594 | 568 220 | 15 s (36 s before clipping) |
| same at s0+0.02 | FAIL | FAIL, 97 holes (e.g. theta 3.3 deg, centre (0.528, 3.218), mass 0) | 159 455 | 9 s |
| frac_pass (two coincident atoms 1/3+2/3 at centre, s=1.9) | PASS | PASS | 1 183 | 0.1 s |
| frac_fail (Göbel with weights 1/2 + centre 1, s=2.5) | FAIL | FAIL, corner square mass 1/2 | 158 | 0.0 s |
| Göbel via `"symmetry": "D4"` (one representative) | = full list | identical result | | |

## 5. Findings

1. **Tangency: box methods cannot certify certificates with atoms exactly on the boundary of an
   admissible square.** Göbel's set has (1,1) on the corner of the wall-flush corner square
   [0,1]^2 (an admissible placement) *for every s*. Inside the admissible region the point is inside
   Q for all nearby placements (admissible => cx >= w/2 => u = w(1-cx) <= w - w^2/2 <= 1/2 with
   equality only at w=1), but the inequality is tangential (u = 1/2 - (w-1)^2/2 + ...), so any box
   of positive width around (t=0, c=(1/2,1/2)) contains inadmissible placements with the atom
   outside — and interval arithmetic cannot see the cancellation even after clipping (the coupling
   between t and cx is lost). The remedy is on the certificate side: keep atoms at positive distance
   from the boundary of every tight square (A07's `eps_geo` shrink is exactly that, but see 3.).
   A06 found the same independently.
2. **A07's raw LP solutions FAIL** (as anticipated); the reasons are structural and are what A07 needs
   to fix, not tolerance noise:
   - `test_s3.80_N38/N76` (v1, no shrink, tau >= 11 so they prove nothing anyway; run with `--n 12`):
     only `tight`/`undecided` witnesses: grid atoms at (1.0, y), (x, 1.0), (0.9,1.0)... sit exactly on the
     edges of the wall-flush upright squares — same tangency as Göbel. Witness clusters: theta ~ 0 deg,
     centres (0.50, 1.55), (0.50, 2.25), (1.55, 0.50), (0.50,0.50)... (all four walls, by D4).
   - `v2test_s3.80` (v2, eps_geo = 1e-4, unconverged, tau = 10.5448): weights are floats summing to
     0.99999999998 on the corner square (LP tolerance) — cured by `--scale-weights 1.000001` — and then
     **39 genuine holes**: e.g. theta = 0.0017 deg, centre (0.500043, 1.499884): exact mass
     0.96783 (< 1). Cross-checked directly on A07's raw JSON: the upright square [0,1]x[1,2] has float
     mass 0.99999999998, but its atoms at y = 1.9999 (= 2 - eps_geo) fall out as soon as the centre
     moves down by > 1e-4, and no other row of the LP protects that placement. So the shrink margin
     1e-4 is smaller than the spacing of the generated rows/oracle. Other holes: theta ~ 7 deg,
     centre (0.557, 2.25), mass 0.9943 (atom (0.99988, 1.8001) lost). Coordinates of all holes:
     `witnesses_v2test_s3.80.json` (kind = "hole", with exact masses).
   - `certs_wip/test_3.80_scale1.05.json` (2249 atoms, total 10.945 < 11, weights x1.05): see §7.
3. **Cost model / what a passing certificate must look like.** The verifier needs box widths below
   the *robustness margin* delta of the certificate (the distance by which every needed atom is
   inside Q at every tight placement), only in the tight regions; elsewhere it stops early. Leaves
   at width delta cost ~ (volume of tight region)/delta^3 boxes. With delta = 1e-4 (A07's eps_geo)
   that is hopeless in 3-D (~10^12 boxes if the tight region has volume ~1); with delta = 1e-2 it is
   ~10^6 boxes, minutes. Recommendation to A07: (i) shrink margin eps_geo >= 5e-3 (or an explicit
   margin objective), (ii) round weights UP (they now do: `make_cert.py` scales x1.05 and rounds up)
   and check total < 11 after rounding, (iii) enforce constraints on ALL placements, not only rows
   (their oracle must be exhaustive to within eps_geo). Throughput of this verifier: ~40k boxes/s
   per process on 4-atom certificates, ~10-20k boxes/s on 500-2000 atoms (float shortlist ~100 us
   per box dominates after the optimisations); 4 processes scale linearly (`--jobs 4`).
4. **A05's 10-point certificate at s = 3.741594 is independently confirmed** (568k boxes, 15 s;
   A05's own verifier and A06's Lean checker agree). Not an improvement over Stromquist.

## 6. Lean port (for A06) — how the same recursion is a decidable function

A06 has already written `lean/PackingCert/PackingCert/Measure.lean` (style A: recursion in Lean
over `Rat`, `native_decide`; kernel `decide` fails on `Rat` gcd). The integer scheme of this verifier
is the natural fix for kernel `decide` (A06's option (i)); it needs only `Int`/`Nat` +, *, <=:

```
structure MCert where n : Nat; sNum sDen : Nat; atoms : List (Int × Int × Nat)   -- (PXn, PYn, PD)
                      weights : List Nat; WD : Nat; depth : Nat
-- derived constants: K := depth+1; D := sDen * 2^(depth+2); SD := sNum * 2^(depth+2)
def trig (K T : Nat) : Int × Int × Int := (4^K - T^2, 2*T*2^K, 4^K + T^2)          -- (cn, sn, dn)
def boxTrig (K T0 T1) : Int×Int×Int×Int×Int := (cn1*dn0, cn0*dn1, sn0*dn1, sn1*dn0, dn0*dn1) -- Clo Chi Slo Shi E
def imul4 (a0 a1 b0 b1 : Int) : Int × Int := (min of 4 products, max of 4 products)
def insideAll (a : Atom) (D Clo Chi Slo Shi E X0 X1 Y0 Y1 : Int) : Bool :=
  let dxlo := a.PXn*D - X1*a.PD; let dxhi := a.PXn*D - X0*a.PD; (dylo, dyhi likewise)
  let lim := E*a.PD*D
  let (u0,u1) := imul4 Clo Chi dxlo dxhi + imul4 Slo Shi dylo dyhi      -- componentwise
  let (v0,v1) := imul4 (-Shi) (-Slo) dxlo dxhi + imul4 Clo Chi dylo dyhi
  2*u1 <= lim && -lim <= 2*u0 && 2*v1 <= lim && -lim <= 2*v0
def clip (SD D K T0 T1 X0 X1 Y0 Y1) : Option (Int×Int×Int×Int) :=   -- floor/ceil via Int.fdiv / -(-a).fdiv b
  wLo := the smaller of (cn0+sn0)/dn0, (cn1+sn1)/dn1 (compare cross-multiplied); lo := (wn*D).fdiv (2*wd);
  hi := -((-(2*SD*wd - wn*D)).fdiv (2*wd)); clipped := (max X0 lo, min X1 hi, max Y0 lo, min Y1 hi); none if empty
def go (c) : Nat → Box → List Nat (undecided atom indices, or all atoms) → Nat (sure mass) → Bool
  | fuel, b, atoms, sure => match clip .. with
     | none => true
     | some b' => let (sure', rest) := sift b' atoms sure   -- add insideAll atoms; keep others
                  if sure' >= NEED then true else match fuel with
                  | 0 => false
                  | fuel+1 => let (b1,b2) := split b' in go fuel b1 rest sure' && go fuel b2 rest sure'
def check (c) : Bool := (sum weights < n*WD) && go c c.depth root allAtoms 0
```
Split rule identical to the Python (compare (T1-T0)*tscale*D with (X1-X0)*2^K, etc.; midpoints by
`>>> 1`, i.e. floor — the two halves still cover). Everything is `Int` arithmetic with `decide`-friendly
instances; the numbers have ~ (2 K + log2 D + log2 PD) ~ 250 bits, fine for GMP-backed kernel Nat.
Fuel = depth. Bridge lemma (not formalised, same as A06's list): theta in [0,pi/2] suffices;
monotonicity of cos/sin in t and unimodality of cos+sin; interval arithmetic soundness; the leaves
cover the admissible set; then the scaling/shrinking argument of §2.
Style (B) alternative (explicit leaf list with atom indices, linear check) is also easy to emit from
this verifier if needed (`--report` already records the depth histogram; a leaf dump is a 10-line
addition), at the price of ~10^6 boxes x ~40 bytes.

## 7. Status of A07's certificate at s = 3.80

A07 froze `certs/measure_certificate_3.80.json` at ~14:15 (1069 atoms, total 10.801639 < 11, weights
x1.03 rounded up to 1e-6, atoms rounded to 1e-6, eps_geo = 1e-4, source `results/v2_s3.80_rowonly.json`).
Coarse float scan (theta step 0.5 deg, centre step 0.01, closed squares): min mass 1.0218 at
(43.5 deg, (2.567, 1.317)); with a 5e-5 shrink still 1.0218; with a 1e-3 shrink 0.258 at the corner
square (0.5,0.5,0 deg) — i.e. the robustness margin of the certificate is ~1.2e-4 (the eps_geo shrink),
so the exact verifier has to resolve boxes of width ~1e-4 wherever wall-flush squares are tight.
The earlier WIP `certs_wip/test_3.80_scale1.05.json` (2249 atoms, x1.05) has the same margin
structure (min closed mass on the grid 1.016; 2e-3 shrink -> 0.31 at the corner square).

## 8. Run log

- v2test_s3.80 (raw, unconverged, weights x1.000001): depth 45, 4 jobs, caps 200/3: FAIL, 39 holes
  (worst exact mass 0.96783 at theta 0.0017 deg, c = (0.500043, 1.499884)); 873k boxes, 21-31 s.
- test_s3.80_N38 / N76 (raw v1, --n 12): FAIL, tight/undecided only (grid atoms on wall-square edges);
  26k / 28k boxes, ~1.5 s each.
- **certs/measure_certificate_3.80.json (frozen by A07, 1069 atoms, total 10801639/1000000 = 10.801639 < 11):
  PASS.** `python certs/verify_measure.py certs/measure_certificate_3.80.json --depth 48 --jobs 4 --report`:
  5 836 650 boxes (2 918 357 covered leaves, 0 vacuous), 7.65M exact atom checks, max depth reached 45
  (200 leaves at depth 45; deepest boxes ~ the 1e-4 robustness scale), **62.9 s wall with 4 processes**
  (report: `report_measure_certificate_3.80.json`, depth histogram inside).
  => **s(11) >= 19/5 = 3.80**, improving Stromquist's 3.788854 (modulo the bridge argument of §2 and the
  correctness of this verifier + A07's independent one).
  Cross-checks performed on the same file:
  * different box trees: `--tscale 1` PASS (5.45M boxes, 59 s), `--tscale 4 --split 2` PASS (8.31M boxes, 87 s);
  * `--strict-margin 0.02`: 24 undecided leaves at depth 48 with sampled mass 1.0297 (the tight cells sit
    at ~1.0288-1.03 = the x1.03 rescaling of an LP with min mass ~0.9989; certifying an extra 0.02 needs
    boxes finer than 1e-4); `--strict-margin 0.04`: 47 rigorous holes with exact mass 1.028836 (< 1.04),
    e.g. (0 deg, c=(1.499884, 1.550021)) — so the certificate's true minimum mass is ~1.0288, i.e. it has
    ~2.9% slack, all of it coming from A07's x1.03 weight scaling;
  * pure exact arithmetic on all 1069 atoms (`use_float=False`) on three of the 256 (split-4) root
    sub-boxes: identical box trees and counts (35 613 / 1 877 / 305 boxes) to the float-shortlisted run;
  * `--selftest` (3000 random boxes, int vs Fraction predicates, random soundness spot checks): 0 problems;
  * independent float sampling of 300 000 random admissible placements (half of them within 0.02 of a
    wall): min mass 1.030038 (at 84.2 deg, c=(0.559, 0.810)).
  Recommended further checks (not done here): A07's own `bb_verify.py`/`exact_check.py` on the same file;
  A06's Lean `checkMeasure` (regenerate MeasureData.lean from this certificate with fuel >= 48; expected
  ~5.8M boxes, i.e. ~15-30 min native by A06's timings).
