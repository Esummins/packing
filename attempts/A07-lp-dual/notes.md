# A07-lp-dual — LP / measure ("fractional unavoidable set") lower bound for s(11)

Owner: LP agent (postdoc, optimisation / LP duality / rigorous numerics). 2026-08-16 … 2026-08-18.
Status: **done-success** — `certs/measure_certificate_3.80.json` PASSES the independent exact verifier
(A08, `certs/verify_measure.py`) ⇒ **s(11) ≥ 3.80** (previous record 2+2√(4/5) = 3.788854, Stromquist 2003).
The s = 3.82 certificate is in the last fix/verify round (see §7 for the final word).

Files: `lp_measure.py` (v1, grid atoms), `lp_measure2.py` (v2, free atoms — the real thing),
`analyze_packing.py`, `analyze2.py`, `pinwheel_check.py`, `plot_tau.py`, `make_cert.py`, `bb_verify.py`
(A07 float-interval verifier), `exact_check.py` (Fraction re-check of leaves, superseded by A08's verifier),
`results/` (JSON, `*_state.json` = full LP checkpoints), `logs/`, `plots/`, `certs_wip/`.

## 1. Formulation

Container S = [0,s]². A non-negative measure μ on S is *blocking* if μ(Q) ≥ 1 for every closed unit
square Q ⊂ S (any orientation). If a blocking μ has μ(S) < n then n pairwise-disjoint closed unit squares
cannot lie in S (each carries mass ≥ 1) and s(n) ≥ s (if n squares with disjoint interiors fit in side
s' < s, scale by s/s' > 1 and shrink each square about its centre back to a unit square: the closed unit
squares are pairwise disjoint in [0,s]²). Define

    τ*(s) = inf { μ(S) : μ blocking }            (semi-infinite LP)
    ν*(s) = sup { total weight of a fractional packing }  = LP dual
            (measure on placements (c,θ) with pointwise coverage ≤ 1 on S)

Point sets (Stromquist/Friedman "unavoidable sets") are the special case μ = Σ Dirac masses, so
τ*(s) < n is at least as strong as any pure unavoidable-set argument, and the largest s with τ*(s) < n
is the CEILING of every measure-type argument. τ* is non-decreasing in s (restriction of a blocking
measure for s' > s to [0,s]² is blocking for s). WLOG μ is D4-symmetric (average over the symmetry
group of S; constraints and objective are invariant), so θ ∈ [0,π/4] and centres in a C4 fundamental
quadrant suffice. Kearney–Shiu's s(6)=3 proof (two unavoidable sets used simultaneously = a weighted
cover) is the only precedent for weighted covers in this problem (A01); no LP/measure bound for finite
square containers exists in the literature, so the τ*(s) curve below is new.

## 2. Discretisation — two versions

**v1 (`lp_measure.py`), atoms on a grid** (spacing h = s/N, variables = D4 orbits, rows = placements
from a heuristic separation oracle, HiGHS dual simplex with warm start). At s = 3.80: h = 0.1 → τ = 11.069,
h = 0.05 → τ = 11.000 exactly. Diagnosis (`analyze_packing.py`, `plots/test_s3.80_N76.png`): the dual
"packing" of weight 11 has true maximum coverage 1.5 — it is a near-packing of 11 squares whose pairwise
overlaps are thin slivers avoiding all grid nodes (coverage is only enforced at nodes). Grid atoms
over-estimate τ* by an O(h) sliver artefact that does not go away quickly. **Refinement study verdict:
grid atoms are the wrong discretisation**; the free-atom value at the same s is 10.42–10.49.

**v2 (`lp_measure2.py`), free atoms = simultaneous row and column generation** (double cutting plane for
the semi-infinite LP):
- Variables: D4-orbits of atoms at arbitrary positions (weight per point, objective = #points).
- Rows: placements (cx,cy,θ), coefficient = number of orbit points inside the ε-shrunk closed square
  |R(−θ)(p−c)|∞ ≤ 1/2 − EPS_GEO, EPS_GEO = 1e-4 (robustness margin so that the interval verifier never
  has to certify an atom exactly on a boundary). Centres in the admissible region c ∈ [w/2, s−w/2]²,
  w = cosθ+sinθ.
- Row oracle: for each θ on a grid (91 → 181 → 361 values on [0,π/4]) rotate the atoms, 2-D histogram
  (bin 0.002) with prefix sums → lower bound of μ(Q) on a c-grid (step 0.02 → 0.01 → 0.005), exact
  evaluation of candidates, pattern search in (c,θ); optionally 26 neighbourhood rows around each
  violated placement (`--neigh_rows`).
- Column oracle: expand the dual (weight y_i/8 on each D4 image of row i), find points of maximum
  coverage (grid 0.005 on the fundamental triangle + arrangement vertices of the placement squares
  perturbed by 2e-5 into neighbouring cells + pattern search); add the D4 orbit of each over-covered
  point. This is exactly the missing dual separation and it kills the sliver artefact.
- Loop: solve; add ≤1200 rows; add ≤60 orbits; stop adding columns when maxcov < 1.003 (or
  `--col_stop_iter 0` for a row-only run) and run rows to convergence, ending with a fine row search.
  A row-converged run gives a primal-feasible μ (up to oracle resolution) = certificate basis;
  its value is an upper bound on τ*(s) for that atom set. Checkpoints `results/*_state.json` every
  iteration (`--state` resumes with all rows/orbits; `--extra_rows` injects verifier witnesses).
- Cost: ~30–90 s per iteration (LP up to 18k rows × 4k orbits, oracles ~15 s); 40–90 iterations per s.

## 3. Results: τ*(s) table (one function of s; threshold 10 for n=10, 11 for n=11)

| s | τ (joint, best) | row-converged (cert. basis) | notes |
|---|---|---|---|
| 3.6500 | 9.364 | – | n=10: 9.36 < 10 |
| 3.7071 = 3+1/√2 = s(10) | **10.000** (stable from it. 10, `logs/v2_s3.7071.log`) | – | LP tight at s(10): 10-packing exists ⇒ ν* ≥ 10; LP finds blocking mass exactly 10 |
| 3.8000 | 10.423 | **10.4865** (137 orbits, 1069 atoms) | **certified** ×1.03 → 10.8016 < 11 |
| 3.8200 | 10.621 | **10.7159** (237 orbits, 1793 atoms) | ×1.025 → 10.985; fix/verify round in progress (§7) |
| 3.8300 | 11.000 (not conv., minmass 1.0) | – | at/above threshold |
| 3.8400 | 11.020 | – | > 11 |
| 3.8500 | 11.061 | – | > 11 |
| grid v1, 3.80 | h=0.1: 11.069, h=0.05: 11.000 | – | sliver artefact |

Slope ≈ 18–20 per unit s near 3.8. **Crossing of 11 at s ≈ 3.83** (10.72 at 3.82 → 11.00 at 3.83): this
is the ceiling of the pure measure/LP method for n = 11 (best packing 3.877). Crossing of 10 for n = 10 is
in (3.65, 3.7071] and the LP is exactly tight at s(10) = 3.7071 (calibration: the measure method
reproduces Stromquist's exact s(10) with zero slack; whether τ*(3.70) < 10 was not run — no long LP runs
allowed at the end). Plot: `plots/tau_vs_s.png`; table: `results/tau_table.json` (`plot_tau.py`).
Note: joint-run values are not fully converged (minmass 0.95–0.99, maxcov 1.002–1.02), so the true
τ*(s) is within ≈ ±0.05 of the table; row-converged values are rigorous upper bounds for their atom sets.

## 4. Structure of the optimal μ (s = 3.80, `plots/v2_s3.80_rowonly_structure.png`)

Very diffuse: 1069 atoms, max weight 0.068. Mass by distance d to the container boundary:
d < 0.9: 3.22, 0.9 ≤ d < 1.1: **5.58**, 1.1–1.5: 1.15, 1.5–1.9: 0.49, centre: 0.05. I.e. μ lives on the four
lines x,y ∈ {1, s−1} ("Stromquist lines"), smeared into segments/clusters: L-shaped clusters at
(1,1)-type corners (mass ≈ 1 each), T-shaped clusters at (s/2, 1)-type mid-edge points, plus segments on
y = 1 towards the corners (heaviest orbit: (0.694, 1.000), orbit mass 0.50), and V/X-shaped clusters
around (1.9, 1.4), (1.9, 1.9), (1.43, 1.9). Nothing at the container corners or on its boundary. It looks
like a continuous measure supported on 1-D curves (segments of the unit-offset lines) plus a few
concentrated clusters — a genuinely fractional object, not a perturbed 10-point set.

## 5. Structure of the blocking fractional packing (s = 3.83–3.85, `analyze2.py`, `pinwheel_check.py`)

At 3.84 (weight 11.02): corner upright squares (3.34,3.34,0°) carry orbit weight 3.59 (≈0.9 per corner),
mid-edge upright squares (2.34,3.34,0°) + (2.32,3.33,1°) + … ≈ 2.4, tilted squares near the centre at
28–33° ≈ 1.5, and 40° squares next to the corners — Trump-like (corners + edges upright, tilted middle),
but spread over ~160 image placements. Angle histogram (orbit weight): [0,5°): 6.76, [30,35°): 1.95,
[40,45°): 0.48, rest small.
**Pinwheel verdict**: 3-cliques of pairwise-overlapping squares with empty common intersection exist in
the support (1408 triples among the 80 images with weight > 0.02 at 3.84) but the largest weight sum of
such a triple is **0.24** (0.31 at 3.85, 0.16 at 3.83); the heaviest overlapping *pair* sums to 0.90–0.93.
So the LP dual is NOT exploiting small odd cliques: clique cuts on triples (or pairs) would cut nothing.
The fractional packing beats integrality by spreading weight thinly over a continuum of slightly different
configurations (many placements with weight 0.01–0.2 in cyclic overlap patterns), i.e. by long
odd-cycle/continuum structure. Consequence: "LP + clique cuts" is not the next step; the case-LP
branching of `docs/ideas.md` I-L6 (branch on where a square of the packing lies, drop/strengthen coverage
accordingly) is. Also worth trying: restricting μ(Q) ≥ 1 to squares whose centres avoid a small
neighbourhood of the container centre changed nothing at 3.80 (mass there is 0.05).

## 6. Rigorous certification pipeline

Certificate JSON format (**frozen 2026-08-16**; A08's `certs/verify_measure.py` reads it):
```
{"format": "measure-certificate-v1", "n": 11, "s": "19/5",
 "atoms": [["x","y"], ...],   # ALL atoms, exact rational strings, D4 images expanded (no symmetry assumed)
 "weights": ["p/q", ...],     # same length, positive rationals
 "total": "p/q",              # exact sum, must be < n
 "claim": "...", "provenance": {...}}
```
Recipe (`make_cert.py result.json s_rational scale out.json`): take the row-converged LP solution
(EPS_GEO = 1e-4 shrunk squares), round atom orbit representatives to 1/10⁶, expand D4 images, multiply
weights by `scale` (1.03 at 3.80, 1.025 at 3.82) and round UP to 1/10⁶, sum exactly. The scale absorbs
oracle misses (violated pockets with mass in [1/scale, 1)) and rounding. Statement verified: every closed
unit square Q ⊂ [0,s]² has Σ_{p∈Q} w_p ≥ 1.

A07 verifier (`bb_verify.py cert --mw 1e-5 --nproc k --fails_out f.json`): B&B over (t,cx,cy),
t = tan(θ/2) ∈ [0,1] (θ ∈ [0,π/2]), cos = (1−t²)/(1+t²) decreasing, sin = 2t/(1+t²) increasing ⇒ exact
enclosures; dyadic boxes t ∈ [i,i+1]/2^lt, cx ∈ s[j,j+1]/2^lx, cy ∈ s[k,k+1]/2^ly; a box passes if it
contains no admissible placement (x2 < w_lo/2 or x1 > s−w_lo/2, same for y) or the atoms provably inside
Q for all parameters (interval arithmetic on ux,uy) weigh ≥ 1; else bisect the widest dimension (θ-width
≈ 2dt); boxes < 1e-5 in every dimension are failures; early hole detection by exact point evaluation at
the box centre. Float intervals widened by 1e-12 after each operation (rigorous modulo IEEE-754);
region-parallel (t split 8, c 16×16, per-region atom pruning by dist(p, c-box) ≤ √2/2).
A08 verifier (`certs/verify_measure.py`, independent code, exact integers) is the one that counts.

**s = 3.80** (`certs/measure_certificate_3.80.json`, 1069 atoms, total 10801639/1000000 = 10.801639):
- A07 float-interval B&B: PASS, 12,008,360 boxes, 0 fails, 224 s (2 procs).
- A08 exact: `PASS: every closed unit square in [0,19/5]^2 has mass >= 1 ; total 10801639/1000000 < 11
  ==> s(11) >= 19/5 (~3.8000000000)`, 5,836,650 boxes (covered 2,918,357, split 2,918,293), 7,649,291
  exact atom checks, max depth 45, 115 s (2 jobs; advisor reproduced in 51 s).
- ⇒ **s(11) ≥ 3.80.**

**s = 3.82** (`certs/measure_certificate_3.82.json`, 1793 atoms, total 274617/25000 = 10.98468, ×1.025):
- first version: A08 FAIL — 17 holes (exact mass 0.988–0.998 at θ ≈ 44.5–45.2° centres (1.21,1.50)-type,
  and at θ ≈ 34°/56° centres (0.694, 2.28)-type = squares touching the container edge), 79 undecided at
  depth 48; A07 verifier: same two hole families (385 witness boxes, min mass 0.9868, 21.7M boxes).
  Both are oracle misses at the edge of the search domain (θ = π/4 boundary of the θ-grid; c = w/2
  admissible boundary), unscaled mass 0.963–0.974 (< 1/1.025).
- rigorous separation loop: witnesses → `--extra_rows` (+ 26 neighbourhood rows each) → row-only
  re-solve from the checkpoint (`results/v2_s3.82_fix1*`) → new certificate → re-verify. See §7.

## 7. Final status / log
(see bottom entries)
