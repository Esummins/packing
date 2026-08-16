# A05 — optimised unavoidable point sets (idea I-L1)

Owner: LB agent (postdoc, computational geometry). Dates: 2026-08-16.
Status: **done-negative** for the goal "beat 3.788854 with a pure 10-point unavoidable set".

## 1. Goal and method

**Claim used.** If P ⊂ [0,s0]² has k points and every closed unit square Q ⊂ [0,s0]² (any orientation)
contains a point of P, then s(k+1) ≥ s0 (scale a hypothetical packing of k+1 squares in side s' < s0 up to
side s0, shrink squares back to unit size about their centres → k+1 pairwise-disjoint closed unit squares
each containing a point of P → pigeonhole).

**Reformulation.** Q(c,θ) ⊂ [0,s0]² ⟺ c ∈ D(θ) = [w/2, s0−w/2]², w = cosθ+sinθ; p ∈ Q(c,θ) ⟺
‖R(−θ)(p−c)‖∞ ≤ 1/2; θ ∈ [0,π/2] suffices. Uncoveredness d(c,θ) = min_p ‖R(−θ)(p−c)‖∞ − 1/2.
P unavoidable ⟺ max_{θ, c∈D(θ)} d ≤ 0. Robust version: d ≤ −m (margin m).

**Code** (all in this directory):
- `unavoid.py` — library.
  - `uncov_grid / worst_configs`: vectorised d on a (θ, cx, cy) grid (default 64×80×80, plus a fine
    grid on the 4 walls of D(θ), 181×200 per wall — holes are almost always wall-adjacent and the 3-D grid
    misses them), 3-D local-maximum filter, batched compass-search refinement of the top-K local maxima,
    optional Nelder–Mead polish. ~10–40 ms per evaluation of a 10-point set.
  - `Param`: linear parametrisations P = A z + b for symmetry families: none (20 params), C2 (180°
    rotation), axes (reflections in x = s/2 and y = s/2, orbit tags g=4 pts, v/h=2 pts on the vertical /
    horizontal midline, c=centre), diag (both diagonal reflections), D4. Note: **no 10-point set is D4-symmetric**
    (orbit sizes 1,4,8 cannot sum to 10) and none is C4-symmetric; the largest possible symmetry of a
    10-point set is Z2×Z2.
  - `slp`: minimises g(z) = max d by sequential linear programming: keep a growing set of critical
    (c,θ) configurations; assign each to its currently nearest point; for that assignment the constraint
    "|u| ≤ 1/2+t, |v| ≤ 1/2+t" is *linear* in the point coordinates, so the model "minimise t" is an LP
    (HiGHS) with a trust region on z; accept/reject on the true g; re-assign every iteration. Converges in
    30–100 iterations. `basin_hop`: kick heuristic — move the least useful orbit onto the worst square and
    re-polish (escapes the "wrong nearest point" local minima that SLP cannot leave).
  - `find_max_s0`: continuation in s0 (rescale P about the centre) + bisection to the largest s0 with
    min_P max d ≤ −m.
- `run_opt.py` — phase A: multi-start (random starts in every family, 4 processes); phase B: continuation
  from the best phase-A sets, with margin m; option to re-parametrise into a less symmetric family.
- `run_sanity.py` — n=5 and n=10 sanity checks. `holes.py` — hole characterisation on a fine grid
  (181×301×301): uncovered volume fraction, connected components, wall adjacency. `plot_set.py`,
  `make_cert.py` (rational rounding + exact verification).
- `../../certs/verify_unavoidable.py` — **exact-rational** interval branch-and-bound verifier (no floats:
  t = tan(θ/2) ∈ [0,1] makes cosθ = (1−t²)/(1+t²), sinθ = 2t/(1+t²) rational and monotone, so all
  enclosures are exact `Fraction`s; boxes outside the centre domain for all θ are discarded via
  w_min = min(w(t1),w(t2)); a box is done when a single point covers it for all parameters). This is exactly
  the rational box-subdivision certificate format wanted by I-C2 (Lean).

## 2. Sanity checks (`log_sanity.txt`)

| check | result |
|---|---|
| n=5, Göbel set (1,1),(1,s−1),(s−1,1),(s−1,s−1) at s = 2+1/√2 | max d = 0.000e0 (tight: corner squares and the 45° centre square); at s+0.001 max d = +0.001, at s+0.01 max d = +0.01005 |
| n=5 blind (4 free points, 6 random starts) | best s0 = **2.70712** (target 2.70711); rediscovers the Göbel set (points ≈ (1,1),(1.707,1.707),(0.909,1.715),(1.715,0.897): the two off-diagonal points are free to slide — the constraint set is flat there) |
| n=10, 3×3 grid of 9 points at s = 3+1/√2 | NOT unavoidable: max d = +0.1036 (45° square at a cell centre) |
| n=10 blind, 9 points, 8 starts across D4/axes/diag/none families | best s0 = **3.41416 ≈ 2+√2** (D4 family x,d,c: 8 points around the centre + centre); far below 3.7071. So Stromquist's s(10) proof is *not* a pure 9-point unavoidable-set argument (indeed his proof uses 10 points that are unavoidable and then a case analysis on which box contains which point). Caveat: only 8 starts, not exhaustive. |
| Stromquist Fig. 13 10-point set at s = 2+2√(4/5) | max d = **+0.02333**; 4 hole components, all wall-adjacent: 45° squares touching the bottom (top) wall centred at x ≈ 1.447 and 2.342 (= 1/2+s/4 and its mirror), θ from 16.5° to 73.5°; total uncovered fraction of (c,θ)-space 3.0e−4. Exactly the "top and bottom rectangles" he treats by a separate case argument. (`stromquist_fig13_eval.json`, `stromquist_fig13_s3.7889.png`) |
| exact verifier on the Göbel-type set (0.996,0.996)… at s0 = 2.6971 | PASS, 46 331 boxes, 5.5 s; and correctly FAILs at s0=2.72 (witnesses at the corner squares) |

## 3. Results for 10 points (n = 11)

Phase A (`resA10_370.jsonl`, 44 random starts × 15 kicks at s0 = 3.70, 9 families): only the axes family
`g v v h` (4 corner-ish points + 4 points on the vertical midline + 2 on the horizontal midline — the
"3-4-3 columns" pattern) and, marginally, C2 (which converges to a distorted copy of it) reach max d < 0 at
s0 = 3.70. Random asymmetric starts (`none`) stall at max d ≈ +0.04…0.10 (20-dim landscape, poor basins);
seeded asymmetric perturbations of the best set did not improve s0 in the runs we could afford (see caveats).

Phase B (continuation, SLP grid 90×100×100 + wall grids, `resB10_m0v2.jsonl`, `resB10_m2e3.jsonl`):

| margin m | best s0 (numerical) | max d re-evaluated on 240³ grid + polish | file |
|---|---|---|---|
| 0 | 3.75119 – 3.75190 | +1.3e−4 … +3.7e−4 (slight overshoot of the SLP grid ⇒ true max ≈ **3.7505 ± 0.0007**) | resB10_m0v2.jsonl |
| 0.002 | **3.74160** | −1.65e−3 (robust) | resB10_m2e3.jsonl |
| 0.002 (2nd start) | 3.74096 | −1.96e−3 | resB10_m2e3.jsonl |

**Best 10-point set (robust, m=0.002, s0 = 3.74160):**
```
(2.76649,0.99799) (0.97510,0.99799) (2.76649,2.74361) (0.97510,2.74361)      # 4 corner-ish points
(1.87080,0.56079) (1.87080,3.18081) (1.87080,1.43409) (1.87080,2.30750)      # 4 on the vertical midline
(0.97487,1.87080) (2.76672,1.87080)                                          # 2 on the horizontal midline
```
i.e. columns of 3, 4, 3 points — Stromquist's Fig. 13 pattern rotated by 90°, with the outer midline points
pushed to y ≈ 0.56 / s−0.56 (Stromquist: 3/2 − s/4 = 0.575 at s = 3.789 — the same formula) and the
corner points at distance ≈ 0.98/1.00 from the walls.

**Tight configurations at the optimum** (`best10_s3.751.png`; d within 1e−4 of the max):
- 8 interior squares at θ ≈ 26.0° / 64.0° centred at (1.36,2.23),(2.24,1.82),(2.39,2.23),(2.24,1.93),
  (1.51,1.82),(2.39,1.52),(1.51,1.93),(1.36,1.52) — squares sitting in the triangles formed by a
  corner point, a horizontal-midline point and a vertical-midline point (Stromquist's Lemma 2 triangles
  with sides ≈ 1);
- 4 wall squares at θ = 45° touching the left/right wall centred at (0.707, 1.44), (0.707, 2.31) and
  their mirrors — the analogue of Stromquist's top/bottom rectangles;
- (secondary) squares at 40°/50° touching the walls near the same places.
Both families become tight simultaneously at s0 ≈ 3.7505; the interior triangles want the midline points
closer together, the wall squares want them further apart — this is the obstruction.

**Certified value.** `UNAVOIDABLE_10pt_3.7416.json` (points rounded to multiples of 10⁻⁶, s0 = 1870797/500000
= 3.741594): exact-rational verifier result recorded in `log_cert.txt` and copied to
`../../certs/unavoidable_10pt_3.7416.json` — see §5. **This does not beat 3.788854**; it is a sanity artefact.

### Holes of the best set at s = 3.7889 and 3.80 (`holes_best10.json`, `holes_best10_s3.789.png`, `_s3.800.png`)

The set was re-optimised (SLP) at each s0 to minimise the maximal uncoveredness; see the table appended in §5
(numbers filled from `log_holes.txt`). Qualitatively the holes are the same as Stromquist's: thin, wall-adjacent
slabs of 45°-ish squares touching the left/right walls between the corner points and the horizontal-midline
points, plus (at larger s) the interior 26°/64° triangle squares. The uncovered fraction of (c,θ)-space is of
order 1e−3 — the holes are small and wall-adjacent, so a Stromquist-style case argument (a box in the hole
must contain some point of a *second* point set) is the natural way to use these sets, exactly as in his
Theorem 2 — but that is a 12-point argument, not a pure 10-point unavoidable set.

## 4. Why the pure 10-point method cannot beat 3.788854 (obstruction)

- Numerically the maximum s0 over all 10-point sets we could find is ≈ 3.7505 (families: all Z2×Z2, C2 and
  free 20-dim; every good run converges to the 3-4-3 column pattern). Stromquist's own 10-point set is the
  same pattern; at s = 3.7889 it has holes of depth 0.023 in exactly the two wall rectangles.
- Two constraint families collide: (i) Lemma-2-type triangles between neighbouring points must have sides
  ≤ 1 (interior squares at ≈26°/64°); (ii) the wall strips between two wall-adjacent points at distance
  ≈ 0.9 from the wall must be narrower than what a 45° square (width √2) can slip through. With 10 points
  there are not enough points to keep all triangles small *and* close all wall strips once s0 > 3.75.
- Consistent with A07's LP: even fractional (measure) covers give τ*(3.80) ≈ 10.4 < 11, so no 10-point
  (integral) cover can exist at 3.80 and the covering-number ceiling of the *whole* measure method is
  well below 11 at s ≈ 3.79–3.80.
- Conclusion for the lab: unavoidable-set (and its LP relaxation) alone cannot reproduce, let alone
  improve, Stromquist's bound; his extra ingredient — the case analysis with a second point set on the
  boxes in the wall rectangles — is essential. Improving 3.7889 needs either a stronger combinatorial
  argument of that type (I-L3/I-L5) or a genuinely different method (I-L4).

## 5. Verification and hole-analysis outputs

**Exact verification of the robust set** (`UNAVOIDABLE_10pt_3.7416.json` = `../../certs/unavoidable_10pt_3.7416.json`,
s0 = 1870797/500000 = 3.741594, coordinates multiples of 10⁻⁶, float max d = −1.65e−3):

| mode | result | boxes | time |
|---|---|---|---|
| exact `Fraction` (t = tan θ/2 rationalisation, minsize 1e−6) | **PASS** | 863 953 | 270 s CPU |
| IEEE-double intervals, outward rounding via `nextafter` (`--float`) | **PASS** | 1 149 605 | 46 s |

So s(11) ≥ 3.741594 is *certified* by this artefact — weaker than Stromquist's 3.788854, kept as a
sanity check of the whole pipeline (and as the first rational box-certificate in the format needed by I-C2).

**Holes of the best 10-point set, minimax re-optimised at each s0** (`holes_best10.json`, `log_holes.txt`;
grid 181 θ × 301² c; "vol frac" = uncovered fraction of {(c,θ): c ∈ D(θ)}, area-weighted):

| s0 | max d | uncovered vol frac | θ-values with a hole | #components | largest components |
|---|---|---|---|---|---|
| 3.7889 | +0.0078 | 2.3e−3 | 78% | 436 (mostly tiny) | 4 interior: 26°/64° squares at (1.57,1.85),(2.22,1.94),… (triangle squares), each 2.1e−4; then wall holes of depth 0.0077 at θ≈0°/90° near (0.5,3.29),(2.41,3.29) (axis-aligned squares touching the top/bottom wall next to the corner) |
| 3.80 | +0.0099 | 3.3e−3 | 83% | 332 | 8 interior components (26°/64° squares in the triangles), each ≈3e−4; wall holes slightly shallower |

The minimax optimiser equalises everything, so its holes are spread out (interior triangles *and* walls). More
useful for a Stromquist-style argument is the constrained variant below.

**Wall-exempt variant** (`run_walldelta.py`, `wall_delta.jsonl`): only squares whose centre is at distance
≥ δ from the boundary of D(θ) must be hit (WALL_DELTA in `unavoid.py`; a proxy for "squares touching / almost
touching a wall are handled by a separate case argument"). Max s0 of the 3-4-3 family:

| δ | max s0 (interior coverage) |
|---|---|
| 0 | 3.7505 |
| 0.05 | 3.849 |
| 0.10 | 3.940 |
| 0.20 | 4.145 (meaningless: the layer is thicker than any lemma covers) |

**Its holes on the full domain** (`run_wallholes.py`, `wall_holes.json`, `wall_holes_s3.789.png`, `_s3.800.png`;
set re-optimised with δ = 0.05 at each s0):

| s0 | interior max d (δ=0.05) | full-domain max d | uncovered vol frac | components |
|---|---|---|---|---|
| 3.7889 | −0.0116 | +0.0391 | 4.3e−3 | 8, all wall-adjacent: 4 in the *corners* (c≈(0.517,0.517), θ 24°–90°, depth 0.039) and 4 axis-aligned squares touching a wall next to a corner (c≈(0.5,3.29),(2.43,3.29), θ 0°–23°, depth 0.038) |
| 3.80 | −0.0095 | +0.0412 | 4.7e−3 | 4, all in the corners (θ 22°–90°) |

Point set at 3.7889: corners (1.037,1.038)…, vertical midline y = 0.579, 1.506, 2.283, 3.210, horizontal
midline x = 0.998, 2.791. Note the optimiser exploited the exemption by pulling the corner points off (1,1) —
this makes the corner squares the holes. In Stromquist's proof the corner points sit exactly at (1,1) so that
Lemma 1 covers every box centred in [0,1]² (a box inside the container cannot cross a wall). Hence the
variant that matters is: **corners pinned at (1,1), wall squares exempt** — `run_pinned.py`, results in
`pinned_delta0.05.json` / `log_pinned.txt` (see the addendum at the end of this file).

**Reading of these numbers.** With 10 points the interior can be covered comfortably up to s ≈ 3.85; the whole
deficit at 3.79–3.80 is a thin layer of squares that touch (or almost touch) a wall between two wall-adjacent
points ~0.9 apart (Stromquist's rectangles) plus, if the corner points are not at (1,1), the corners. That
is exactly the structure Stromquist exploits with his second (12-point) set: the box in the wall rectangle is
forced to contain three specific points. Any improvement of 3.7889 by point-set methods must therefore
attack the wall layer (case-LP as proposed by A02/A07), not the interior.

## 6. Caveats / not done

- Multi-start budget was small (44 starts at 3.70, ~15 kicks each) because the machine was shared with
  other agents' jobs; the `none` (20-dim) family was only explored from random starts, which do not reach
  the good basin. A larger asymmetric search could conceivably find a set slightly above 3.7505, but the
  LP ceiling from A07 rules out anything near 3.79.
- 11-point sets for n=12 were not run (bonus item), no time.
- SLP grid resolution: the LP only sees sampled configurations; the true max d of the "margin 0" sets is
  +1e−4…+4e−4 (re-evaluated on a 240³ grid + polish), so all quoted "s0 at margin 0" values are upper
  estimates by ~5e−4. The margin-0.002 set is robust (max d = −1.65e−3 on the fine grid) and is the one
  that was certified exactly.

## Addendum: corners pinned at (1,1), wall squares exempt (`run_pinned.py`, `log_pinned.txt`)

Family axes `G v v h` (corner orbit fixed at (1,1),(s−1,1),(1,s−1),(s−1,s−1) so that Stromquist's Lemma 1
covers every box centred in a corner unit square; 3 free parameters), coverage required only for squares
whose centre is ≥ 0.05 from the boundary of D(θ):

    max s0 = 3.80706   with  vertical midline y = 0.8421, 1.4287, 2.3784, 2.9650;  horizontal midline x = 1.0235, 2.7836
    (all points):  (1,1) (2.8071,1) (1,2.8071) (2.8071,2.8071) (1.9035,0.8421) (1.9035,2.9650) (1.9035,1.4287) (1.9035,2.3784) (1.0235,1.9035) (2.7836,1.9035)

So even granting a free pass for the 0.05-layer of wall squares (which is more than any single nonavoidance
lemma gives), corner-pinned 10-point sets only reach ≈ 3.807: the interior triangles (Lemma 2, sides ≤ 1) then
become the binding constraint — consistent with the minimax holes at 3.80 being interior 26°/64° squares.
Together with the LP ceiling of A07 (τ*(3.80) ≈ 10.4) this says: **the honest headroom of "10 points + a
wall case-argument" above Stromquist's 3.7889 is at most ~0.02**, and it requires a *second* point set for the
wall boxes exactly as in his Theorem 2. Hole tables/PNGs for this set at 3.7889 / 3.80 / 3.807:
`pinned_delta0.05.json`, `pinned_holes_s*.png`, `log_pinned_holes.txt` (produced by the resumed run).

Holes of the corner-pinned set (full domain), re-optimised with the 0.05 wall layer exempt at each s0
(`log_pinned_holes.txt`, `pinned_delta0.05.json`, `pinned_holes_s3.789.png`, `_s3.800.png`, `_s3.807.png`):

| s0 | interior max d | full max d | uncovered vol frac | holes (all 4 wall-adjacent, symmetric) |
|---|---|---|---|---|
| 3.7889 | −0.0044 | +0.0308 | 9.6e−4 | squares touching the left/right wall, centres (0.706, 1.451) and (0.706, 2.338) (+ mirrors), θ ∈ [0°, 74.5°] resp. [15.5°, 90°], deepest at 42.5°/47.5°; each 2.4e−4 of (c,θ)-space |
| 3.80 | −0.0017 | +0.0334 | 1.1e−3 | same four, centres (0.703, 1.445)/(0.703, 2.355), θ ∈ [0°, 75.5°] / [14.5°, 90°] |
| 3.807 | −0.00001 | +0.0351 | 1.3e−3 | same four, centres (0.703, 1.447)/(0.703, 2.360) |

Point set at 3.7889: (1,1)-corners; vertical midline y = 0.8146, 1.4272, 2.3617, 2.9743; horizontal midline
x = 1.0203, 2.7686. **These four wall slabs — a unit square leaning on the wall between the corner point (1,1)
and the wall-adjacent midline point (1.02, s/2), i.e. the "rectangle" [0,~1]×[1,s/2] of centres — are the
holes that a Stromquist-style case argument would have to close** (his Theorem 2 closes the analogous top/bottom
rectangles with the 12-point set of Fig. 14). Their depth (0.031) and θ-extent (0°–75°) are larger than in
Stromquist's own set (0.023, 16°–74°) because the interior was optimised harder; the trade-off between the
interior triangles and the wall slabs is continuous.
