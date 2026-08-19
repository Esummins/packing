# A13-case-lp-bnb — LP-based branch-and-bound over the packing structure (I-L6 "case-LP"), pilot

Owner: LP/B&B postdoc. 2026-08-18. Status: **done-negative (pilot; ~5 h): tree not closed at 3.84 within the budget; machinery + one verified node certificate; verdict §7.**

Question. Theorem 1 (measure LP) has ceiling ≈ 3.83 (τ*(3.84) = 11.02–11.05 > 11). The blocking fractional packings
are locally integral (¼/½ weights, corners + sides + interior pinwheel) and A12 showed they are killed by CONDITIONAL
counts (corners fixed + side zones empty ⇒ τ = 5 < 7). Pilot: implement a rigorous case-LP branch-and-bound over
hypotheses about the packing and measure whether it closes at s = 3.84 (⇒ s(11) ≥ 3.84, a NEW bound) and how the tree grows.

## 1. Formulation and bridge (the mathematics)

Fix s and suppose a packing of 11 unit squares in side s' < s exists. Scale by s/s' and shrink each square about its
centre to a unit square (Theorem 1's argument): we get P = 11 pairwise DISJOINT closed unit squares in [0,s]²
(pairwise at positive distance). Every square Q of P is Q(c,θ) with admissible centre c ∈ [w/2, s−w/2]², w = cosθ+sinθ,
θ ∈ [0,90°) (t = tan(θ/2) ∈ [0,1)).

A NODE is a hypothesis set H = (core boxes B₁..B_m ; NO-families F₁..F_k):
* core box B = [x0,x1]×[y0,y1]×[θ0,θ1]: hypothesis "some square Q₀ ∈ P has (c,θ) ∈ B". Its CORE K(B) is a rational
  square provably contained in every Q(c,θ) with (c,θ) ∈ B: centre k = midpoint of the centre box, orientation θ_m with
  t_m = (t0+t1)/2 (t0 ≤ tan(θ0/2), t1 ≥ tan(θ1/2) rational, rounded outward), half-side
  a = (½ − hd)/(1 + (t1−t0)), hd ≥ half diagonal of the centre box. Proof: for p = k + R(θ_m)(u,v), |u|,|v| ≤ a, and
  Q = Q(c,θ) ∈ B: |R(θ)ᵀ(p−c)|_∞ ≤ |c−k|₂ + a(|cos δ|+|sin δ|) ≤ hd + a(1+δ), δ = |θ−θ_m| ≤ 2|arctan t − arctan t_m|
  ≤ |t−t_m|·2 ≤ t1−t0; so ≤ ½ ⇔ a ≤ (½−hd)/(1+(t1−t0)). Every OTHER square of P is disjoint from Q₀ ⊇ K(B), hence
  from K(B) (closed disjointness).
* NO-family F = zone [x0,x1]×[y0,y1] × union of θ-intervals: hypothesis "no square of P has (c,θ) ∈ F".
* budget(H) = 11 − m.

NODE LP: min μ([0,s]²) s.t. μ(Q) ≥ 1 for every admissible closed unit square Q that is not EXEMPT, where Q is exempt iff
(c(Q),θ(Q)) ∈ some Fⱼ or Q ∩ K(Bᵢ) ≠ ∅ for some i. **Lemma (node death).** If a non-negative atomic μ satisfies these
constraints and μ(total) < budget(H), no P satisfies H. Proof: the ≥ 11 − m squares of P other than the Q₀ⁱ (fewer
than m distinct Q₀'s only helps: then more squares are "other") are pairwise disjoint, admissible, not in any Fⱼ and
disjoint from every K(Bᵢ) ⇒ non-exempt ⇒ each has μ-mass ≥ 1 ⇒ μ(total) ≥ 11 − m. ∎
(Note that we do NOT need the Q₀ⁱ to be distinct squares; over-counting cores is harmless. The pairwise-compatibility
prune "max centre distance of two boxes < 1 ⇒ impossible" DOES need distinctness — it is applied only between boxes
from different zones of the fixed 9-zone partition, which are disjoint parameter sets, so the two squares are distinct
and their centres are ≥ 1 apart (each contains its incircle).)

BRANCHING (exhaustive case splits, so if every leaf is dead no P exists ⇒ s(11) ≥ s):
* zone branch on a family F: children H+{NO F} and H+{B} for every box B of a finite cover of F (F ⊂ ∪B; vacuous boxes
  — no admissible placement, w(θ)/2 > x1 etc. — dropped). Exhaustive: either no square of P is in F or some square is
  in F, hence in some B.
* refinement branch on core box Bᵢ: replace Bᵢ by the two halves of a bisection (exhaustive: Q₀ lies in one half; a
  half with no admissible placement is dropped).
* symmetry: only at the ROOT (H = ∅, D4-invariant): "some square in some corner zone" ⇒ WLOG corner 0 (apply the D4
  element of the container mapping that corner to corner 0); the NO-child "no square in ANY corner zone" is D4-invariant
  and its LP is solved with D4 (μ may be averaged over D4 because the constraint set is invariant). All other nodes are
  solved WITHOUT symmetry (C1: atoms are single points, rows over the whole square). Where an alive node's hypothesis
  set is D4-symmetric (only symmetric NO-families) the D4 LP is used (valid for the same reason).
* Closed/open: families and cores are closed sets; P's squares are closed and pairwise disjoint; the case split
  "in F / not in F" is exhaustive for closed F; "disjoint from K" is closed-set disjointness. No open/closed issue arises.

Robust filter margins: the LP drops a row Q only if Q penetrates a core by depth > EPS_CORE = 2·10⁻³ on all four SAT axes
(strict overlap), or its centre is inside the NO-zone by ≥ 2·10⁻³ and θ inside the θ-intervals by ≥ 0.3° (margins only at interior ends: θ = 0/90 and the domain boundary cx,cy ∈ {0.5, s−0.5} are closed). Dropping fewer
rows only raises τ (conservative). The verifier (`verify_case.py`, a copy of `certs/verify_measure.py`) exempts a
(t,cx,cy)-box only if it is PROVABLY inside a family (rational comparisons) or PROVABLY meets a core (rational interval
SAT: on each of the 4 edge-normal axes — the core's two fixed rational axes and Q's two interval axes — sup|proj(c−k)| ≤
a·g + ½·h with g,h the interval lower bounds of |cos(θ−θ_m)|+|sin(θ−θ_m)| resp. 1). The margins guarantee that placements
in the thin shell between "exempt" and "row kept" are covered by μ, so boxes straddling the exempt boundary are discharged.

## 2. Implementation

* `lpbox.py` = A12/A10 `lp_measure_box.py` + symmetry C1 (rows over the whole square), hypothesis filter hook (rows and
  oracle candidates with `hyp.ok(c,θ)` False are dropped; the pattern-search refine stays feasible), log hook.
* `caselp.py`: `Box`, `Core` (rational core + float SAT depth), `NoFam`, `Hyp` (filter), `solve_node` (node LP: HiGHS
  incremental, row generation with A10's exact per-θ arrangement oracle over the whole square [C1: 121 θ values of 0.75°
  in the coarse phase, fine search 0.25°/0.01 only if τ < budget + 0.05], column generation (150 columns/iteration) for ≤ 40 iterations or until
  max coverage < 1.02, no row pruning, warm start = parent's atoms + rows), `make_certificate` (rational atoms 1/10⁶,
  weights ×1.03 rounded up, hypotheses in rational form, budget).
* `bnb.py`: driver. 9 zones partition the centre square [0.5,s−0.5]²: 4 corner zones (0.6×0.6), 4 side zones
  (0.6×(s−2.2)), interior ((s−2.2)²), all θ. Zone-branch initial covers: corner 2×2×3 (θ thirds of 30°), side 2×3×3,
  interior 3×3×3. Heuristic: zone weights y(F) of the node's fractional packing; branch on corners first, then sides,
  then interior (largest y(F) ≥ zmin = 0.4 within the class); if no such family, refine the core box whose 1.15-
  neighbourhood carries the most fractional weight. Best-first by the parent's slack τ − budget. 8 worker processes,
  time limit per node LP 300 s (run 3). Status: `dead` (row-converged and τ < budget), `dead?` (τ < budget − 0.03 with minmass
  ≥ 0.97 but not converged), `alive` (τ ≥ budget: branch), `dead??` (τ < budget but not converged and not robustly).
* `verify_case.py`: exact verifier with exempt tests (see §1); `certify.py`: A07's separation loop (certificate →
  verify → feed witnesses back as rows → re-solve), optional `--eps_geo` re-solve with a larger row shrink margin.

## 3. Sanity checks (Task 1)

(i) Root at s = 3.80 (H = ∅): D4 LP warm-started from A07's `v2_s3.80_rowonly.json`: τ = 10.44–10.47 (300 s, joint row/col
    generation oscillating as in A07); C1 LP (no symmetry, whole square, same warm start): τ = 10.495 (240 s, unconverged
    upper bound), consistent with A07's 10.42–10.49 and with the certified bound (dead at the root: 10.5 < 11).
(ii) A12 contrast at s = 3.86, Θ_B = [0,2]∪[32,36], corners fixed as (degenerate) core boxes = the four unit squares
    [0,1]²+images, budget 7: C1 LP τ = 7.000 (converged, 166 s) = A12's 7.000. Corners fixed AND the four side zones
    [0.5,0.75]×[1.2,s−1.2] excluded: **τ = 5.000 (converged, minmass 1.0, maxcov 1.0, 139 s; μ = 5 atoms of weight 1)** =
    A12's 5.000. This check FOUND A BUG in the first version of the NO-family filter (θ-margin also applied at the closed
    ends θ = 0/90 and centre margin at the domain boundary cx = 0.5, so upright rows / wall-touching rows were never
    dropped and the first two B&B runs' NO-branches were void — `NO(all corners)` came out alive with τ = 11.04; after the
    fix (margins only at interior ends) it is dead with τ = 9.41). Runs 1–2 (`results/t384_run{1,2}_aborted/`) are kept
    for the record but their NO-nodes are meaningless; run 3 (`results/t384c/`) is the reported one.
    A second lesson from (ii): from a cold start the C1 LP needs MASSIVE column generation to find the τ = 5 measure
    (with ≤ 200 columns/iteration and ≤ 80 column iterations it stalls at 6.9–7.0 for 12 min; with 1500 columns/iteration
    it converges in 2 min) — see §5 on LP convergence.

## 4. Run at s = 3.84 (Task 2) — `results/t384c/` (run 3), 8 workers, 300 s per node LP

Root (D4, warm from A07 `v2_s3.84.json`): τ = 11.033 (367 s; minmass 0.97, maxcov 1.04) — alive by 0.033. Fractional packing
zone weights: each corner zone 0.972, each side zone 1.000, interior 3.147 (the 4+4+3 structure of A07/A12).
Level 1 (branch on the corner family, D4-symmetric): 13 children:
* `NO(all corners)` (D4 LP): **τ = 9.41 < 11, dead by 1.59** (rows 0.98-converged): every packing at s ≤ 3.84 has a square
  with centre in a corner zone [0.5,1.1]² (up to symmetry: in corner 0).
* 12 YES boxes = corner zone [0.5,1.1]² split 2×2 in the centre × 3 in θ ([0,30],[30,60],[60,90]), budget 10, C1 LP:
  the 9 boxes NOT containing the corner-square placement (0.5,0.5,0°) (centre boxes [0.5,0.8]×[0.8,1.1] and
  [0.8,1.1]×[0.5,0.8], all θ, and [0.8,1.1]²×[30,60]; the two other [0.8,1.1]² boxes are vacuous) are DEAD by
  0.23–0.69 (τ = 9.31–9.77; several with unconverged rows, "dead??", but the margins are large);
  the 3 boxes [0.5,0.8]²×{[0,30],[30,60],[60,90]} (they contain the corner square) are ALIVE with slack +0.036, +0.064,
  +0.096 at 300–590 s — but with rows AND columns far from converged (minmass 0.45–0.49, maxcov 1.5–1.75).
  Long re-solves (`_long_node.py`, 900–1500 s, 400 columns/iteration): box [0,30]: τ → 10.07, 10.03, 10.00, 9.98, 9.96
  (rows converged, maxcov 1.07 and still falling), i.e. **at/below the budget 10** — the standard corner box appears to be
  DEAD at 3.84 by ≈ 0.04, but (a) that run predates the shell-row fix of §5 (missing rows ⇒ τ underestimated), and the
  shell-including re-solves of the three boxes were at 10.18–10.24 after 360 s (unconverged, maxcov 1.4–1.5); (b) 0.04 is
  within the LP noise (mirror-image nodes differ by up to 0.1 at 300 s). NOT decided within the pilot.
Level 2 (children of the alive corner boxes: corner 1/2/3 families, 13 children each): 11 solved: 7 dead by 0.23–0.7
  (the off-corner boxes again), `NO corner1` dead??, the on-corner boxes alive with slack +0.17…+0.45 (unconverged).
Level 3: 2 alive so far. Growth: per corner level ≈ 3 survivors (the three θ-thirds of the on-corner centre box) out of
13 ⇒ 3⁴ ≈ 80 nodes with all corners fixed at depth 4 if nothing changes, then 4 side levels (19 children each) ⇒ 10⁴–10⁵
leaves — UNLESS the deeper nodes die (slack should shrink by ≈ 0.03 per fixed corner: root 0.033 − 4×(1−0.972) ≈ −0.08 at
depth 4 with converged LPs; the pilot's LPs are too noisy to see it). Node LP cost 340–670 s each (8 workers ⇒ ≈ 55 LPs/h).
Final counts of the run: see the table appended in §4b (from `python summarize.py results/t384c/tree.json`).
(3.85/3.86 not run: 3.84 did not close.)

### 4b. Final state of run 3 (`summarize.py results/t384c/tree.json x`, at the end of the pilot; the run may have continued a bit)

```
s=3.84 tag=t384c LPs=32 elapsed=1954s nodes=287
status: {'alive': 14, 'dead?': 10, 'dead??': 8, 'pending': 248, 'running': 7}
  depth 0: {'alive': 1}  solved=1 dead-frac=0.00
  depth 1: {'dead?': 3, 'alive': 3, 'dead??': 6, 'pending': 1}  solved=12 dead-frac=0.75
  depth 2: {'pending': 106, 'dead??': 2, 'dead?': 5, 'alive': 4}  solved=11 dead-frac=0.64
  depth 3: {'pending': 63, 'alive': 6, 'dead?': 2, 'running': 7}  solved=8 dead-frac=0.25
  depth 4: {'pending': 78}  solved=0 dead-frac=0.00
LP time: mean 384s, max 670s, n=32
branch types: Counter({'corner2': 9, 'corner1': 8, 'corner3': 4, 'corners': 1})
by branch kind x status: {('root', 'alive'): 1, ('NO', 'dead?'): 1, ('YES', 'alive'): 11, ('YES', 'dead??'): 7, ('YES', 'dead?'): 9, ('YES', 'pending'): 230, ('NO', 'pending'): 18, ('NO', 'dead??'): 1, ('NO', 'alive'): 2, ('YES', 'running'): 7}
alive (solved) nodes: slack list: [0.453, 0.221, 0.216, 0.193, 0.175, 0.154, 0.127, 0.096, 0.064, 0.063, 0.036, 0.033, 0.026, 0.0]
  budget 11: n=2 dead=1 alive=1 slack min/max -1.586/+0.033
  budget 10: n=12 dead=9 alive=3 slack min/max -0.685/+0.096
  budget 9: n=12 dead=6 alive=6 slack min/max -0.481/+0.453
  budget 8: n=6 dead=2 alive=4 slack min/max -0.083/+0.221
   0 d0 pNone D4 b11 tau=11.0332 slack=+0.0332 alive   conv=False mm=0.97 mc=1.04 t=367 | root
   1 d1 p0 D4 b11 tau=9.4136 slack=-1.5864 dead?   conv=False mm=0.98 mc=1.02 t=342 | NO(all corners) [D4 WLOG]
   2 d1 p0 C1 b10 tau=10.0363 slack=+0.0363 alive   conv=False mm=0.45 mc=1.75 t=536 | YES corner0 B([0.500,0.800]x[0.500,0.800]x[0.00,30.00]deg) [WLOG]
   3 d1 p0 C1 b10 tau=10.0642 slack=+0.0642 alive   conv=False mm=0.49 mc=1.52 t=587 | YES corner0 B([0.500,0.800]x[0.500,0.800]x[30.00,60.00]deg) [WLOG]
   4 d1 p0 C1 b10 tau=10.0962 slack=+0.0962 alive   conv=False mm=0.49 mc=1.64 t=436 | YES corner0 B([0.500,0.800]x[0.500,0.800]x[60.00,90.00]deg) [WLOG]
   5 d1 p0 C1 b10 tau=9.4079 slack=-0.5921 dead??  conv=False mm=0.33 mc=1.19 t=339 | YES corner0 B([0.500,0.800]x[0.800,1.100]x[0.00,30.00]deg) [WLOG]
   6 d1 p0 C1 b10 tau=9.7719 slack=-0.2281 dead??  conv=False mm=0.85 mc=1.35 t=450 | YES corner0 B([0.500,0.800]x[0.800,1.100]x[30.00,60.00]deg) [WLOG]
   7 d1 p0 C1 b10 tau=9.3601 slack=-0.6399 dead?   conv=False mm=1.00 mc=1.29 t=362 | YES corner0 B([0.500,0.800]x[0.800,1.100]x[60.00,90.00]deg) [WLOG]
   8 d1 p0 C1 b10 tau=9.3146 slack=-0.6854 dead??  conv=False mm=0.93 mc=1.19 t=353 | YES corner0 B([0.800,1.100]x[0.500,0.800]x[0.00,30.00]deg) [WLOG]
   9 d1 p0 C1 b10 tau=9.7656 slack=-0.2344 dead?   conv=False mm=1.00 mc=1.38 t=389 | YES corner0 B([0.800,1.100]x[0.500,0.800]x[30.00,60.00]deg) [WLOG]
  10 d1 p0 C1 b10 tau=9.6353 slack=-0.3647 dead??  conv=False mm=0.24 mc=1.25 t=340 | YES corner0 B([0.800,1.100]x[0.500,0.800]x[60.00,90.00]deg) [WLOG]
  11 d1 p0 C1 b10 tau=9.4202 slack=-0.5798 dead??  conv=False mm=0.33 mc=1.50 t=670 | YES corner0 B([0.800,1.100]x[0.800,1.100]x[0.00,30.00]deg) [WLOG]
  12 d1 p0 C1 b10 tau=9.5000 slack=-0.5000 dead??  conv=False mm=0.25 mc=1.37 t=446 | YES corner0 B([0.800,1.100]x[0.800,1.100]x[30.00,60.00]deg) [WLOG]
  40 d2 p4 C1 b10 tau=9.9743 slack=-0.0257 dead??  conv=False mm=0.67 mc=1.33 t=407 | NO corner3
  41 d2 p4 C1 b9 tau=8.9229 slack=-0.0771 dead?   conv=False mm=1.00 mc=1.18 t=362 | YES corner3 B([0.500,0.800]x[2.740,3.040]x[0.00,30.00]deg)
  42 d2 p4 C1 b9 tau=8.9959 slack=-0.0041 dead??  conv=False mm=1.00 mc=1.31 t=363 | YES corner3 B([0.500,0.800]x[2.740,3.040]x[30.00,60.00]deg)
  43 d2 p4 C1 b9 tau=8.9699 slack=-0.0301 dead?   conv=False mm=1.00 mc=1.17 t=341 | YES corner3 B([0.500,0.800]x[2.740,3.040]x[60.00,90.00]deg)
  44 d2 p4 C1 b9 tau=9.2158 slack=+0.2158 alive   conv=False mm=1.00 mc=1.18 t=332 | YES corner3 B([0.500,0.800]x[3.040,3.340]x[0.00,30.00]deg)
  45 d2 p4 C1 b9 tau=9.1752 slack=+0.1752 alive   conv=False mm=1.00 mc=1.16 t=363 | YES corner3 B([0.500,0.800]x[3.040,3.340]x[30.00,60.00]deg)
  46 d2 p4 C1 b9 tau=9.4527 slack=+0.4527 alive   conv=False mm=0.92 mc=1.28 t=344 | YES corner3 B([0.500,0.800]x[3.040,3.340]x[60.00,90.00]deg)
  47 d2 p4 C1 b9 tau=8.6250 slack=-0.3750 dead?   conv=False mm=1.00 mc=1.24 t=390 | YES corner3 B([0.800,1.100]x[2.740,3.040]x[0.00,30.00]deg)
  48 d2 p4 C1 b9 tau=8.5189 slack=-0.4811 dead?   conv=False mm=1.00 mc=1.20 t=359 | YES corner3 B([0.800,1.100]x[2.740,3.040]x[30.00,60.00]deg)
  49 d2 p4 C1 b9 tau=8.7187 slack=-0.2813 dead?   conv=False mm=1.00 mc=1.20 t=363 | YES corner3 B([0.800,1.100]x[2.740,3.040]x[60.00,90.00]deg)
  50 d2 p4 C1 b9 tau=9.1541 slack=+0.1541 alive   conv=False mm=0.50 mc=1.37 t=313 | YES corner3 B([0.800,1.100]x[3.040,3.340]x[0.00,30.00]deg)
 144 d3 p44 C1 b9 tau=9.0256 slack=+0.0256 alive   conv=False mm=1.00 mc=1.13 t=344 | NO corner1
 145 d3 p44 C1 b8 tau=8.2208 slack=+0.2208 alive   conv=False mm=1.00 mc=1.13 t=319 | YES corner1 B([2.740,3.040]x[0.500,0.800]x[0.00,30.00]deg)
 146 d3 p44 C1 b8 tau=8.1931 slack=+0.1931 alive   conv=False mm=1.00 mc=1.10 t=341 | YES corner1 B([2.740,3.040]x[0.500,0.800]x[30.00,60.00]deg)
 183 d3 p46 C1 b9 tau=9.0630 slack=+0.0630 alive   conv=False mm=0.59 mc=1.29 t=345 | NO corner2
 184 d3 p46 C1 b8 tau=8.0000 slack=+0.0000 alive   conv=False mm=0.95 mc=1.40 t=377 | YES corner2 B([2.740,3.040]x[2.740,3.040]x[0.00,30.00]deg)
 185 d3 p46 C1 b8 tau=7.9668 slack=-0.0332 dead?   conv=False mm=1.00 mc=1.25 t=351 | YES corner2 B([2.740,3.040]x[2.740,3.040]x[30.00,60.00]deg)
 186 d3 p46 C1 b8 tau=7.9167 slack=-0.0833 dead?   conv=False mm=1.00 mc=1.11 t=330 | YES corner2 B([2.740,3.040]x[2.740,3.040]x[60.00,90.00]deg)
 187 d3 p46 C1 b8 tau=8.1269 slack=+0.1269 alive   conv=False mm=1.00 mc=1.08 t=319 | YES corner2 B([2.740,3.040]x[3.040,3.340]x[0.00,30.00]deg)
```

## 5. Rigour: certificates and the LP-convergence problem (Task 4)

Pipeline: `certify.py node.json --s_rat p/q [--eps_geo 0.003]` = certificate (weights ×1.03, atoms 1/10⁶, hypotheses
rational) → `verify_case.py` (exact) → witnesses fed back as rows → re-solve → repeat.
* Verifier: `verify_case.py --selftest` PASS (3000 random boxes, int vs Fraction). Exempt tests implemented exactly (§1).
* **Certified (PASS)**: `certs_wip/smoke_node1_eps.json` — s = 96/25, budget 11, one D4-symmetric NO-family (no square
  centred in the interior zone [1.1,2.74]²), 220 atoms, total 10.467 < 11, verified in 2.6 s at max depth 27, 506 boxes
  exempt (nofam). Claim: no packing at side ≤ 3.84 has all centres outside the interior zone. (Weak but the pipeline
  works end to end: NO-family exemption path.) The plain (eps_geo = 1e-4) certificate of the same node FAILED with
  0.96–0.99 sliver holes that moved around under 4 rounds of witness feedback (τ ≪ budget, LP degenerate); the robust
  variant (LP re-solved with rows shrunk by EPS_GEO = 3·10⁻³, so every closed placement contains a nearby row's shrunk
  square) passed at once. Recommendation: certification runs use EPS_GEO ≈ 2–3·10⁻³ (costs ≈ 0.1–0.9 in τ here).
* Core path: `results/core380_node.json` (s = 3.80, one core box [0.5,0.8]²×[0,30], budget 10): converged LP τ = 9.605
  (462 s). Certificate ×1.03 (total 9.893 < 10): verifier FAILED with 37 holes of mass ≈ 0.80–0.82 at placements
  TOUCHING the core (SAT depth 5·10⁻⁶ ∈ (0, EPS_CORE]): the LP keeps these rows (conservative) but its row oracle never
  proposed them — the arrangement-cell sample points near the core all lie in the exempt part (depth > 2·10⁻³) and the
  2·10⁻³-thin kept shell is invisible to cell sampling. FIX (implemented, `Hyp.shell_points`): the oracle adds, per core,
  240 centres on the octagons {c : depth(Q(c,θ),K) = 10⁻⁵} and {= 10⁻³} and, per NO-family, points 10⁻³ inside the zone
  edges; EPS_TH raised to 0.3° (> fine θ step 0.25°) so the θ-margin strips always contain oracle samples. Re-solve of the
  core380 node with shells (`results/core380_node_b.json`): τ = 9.84 at 530 s (maxcov 1.17, not converged) — the shell
  rows are NOT free; whether the +0.24 is convergence or a real cost of covering the touching squares is open (a real
  cost would be an artefact of the exempt-margin scheme; the alternative is a zero-gap scheme with tangencies handled by
  the 3% margin, or exempting in the verifier w.r.t. the core and in the LP w.r.t. a core SHRUNK by 10⁻³ — which is
  what the present margins amount to). Certification of a core node was therefore NOT completed in the pilot; the run-3
  tree (built before the shell fix) has slightly optimistic τ at core nodes.
* LP convergence is the dominant practical problem: a C1 node LP with 8k–12k rows and 2–5k atoms takes 15–80 s per
  iteration (8 workers, BLAS threads pinned to 1), needs 30–100 iterations for ±0.02 accuracy; at 300 s the values are
  ±0.1 (mirror-image nodes 2 vs 4 in run 2: 9.93 vs 10.11). Deaths by ≥ 0.2 are robust; the on-corner nodes at slack
  ±0.05 are undecided by 300-s LPs.

## 6. Files

`lpbox.py` (LP engine, C1 + hyp hook), `caselp.py` (hypotheses, node LP, certificate), `bnb.py` (driver), `summarize.py`,
`certify.py`, `verify_case.py` (exact verifier with exempt tests), `_sanity2.py`, `_core380.py`, `_long_node.py`,
`_patch_*.py` (how lpbox/verify_case were derived from A12/A08 files), `geom.py` (A12 copy, unused).
Results: `results/t384c/` (run 3: `tree.json`, `bnb.log`, `node_<id>.json/.log`), `results/t384_run{1,2}_aborted/`,
`results/smoke384/`, `results/sanity2_*.json`, `results/core380_node*.json`, `results/long_node*.json`,
`results/test_root_380_*.json`; `certs_wip/smoke_node1_eps.json` (+ .report.json, PASS), `certs_wip/core380_node.json`
(FAIL, witnesses); `logs/`.
Reproduce: `python bnb.py --s 3.84 --tag t384c --workers 8 --node_budget 300 --time_limit 300 --root_warm ../A07-lp-dual/results/v2_s3.84.json`;
`python summarize.py results/t384c/tree.json [x]`; `python certify.py results/smoke384/node_1.json --s_rat 96/25 --eps_geo 0.003 --jobs 4`;
`python _sanity2.py noside`.

## 7. Verdict for the PI

1. The machinery exists and is sound in design (§1 bridge; exact verifier with NO-family and core exemption; A12's
   conditional LP reproduced exactly: corners fixed 7.000, + sides empty 5.000). One node certificate PASSED end to end.
2. At s = 3.84 the tree did NOT close within the pilot (≈ 40 LPs of 300–600 s each in ~1 h on 8 workers). What we saw:
   NO(all corners) dies by 1.6; 9 of 12 corner boxes die by 0.2–0.7; the 3 boxes containing the corner square sit at
   slack ≈ 0 (+0.04…+0.10 at 300 s; ≈ −0.04 after 25 min without shell rows; +0.2 with shell rows unconverged) — the
   whole question at 3.84 is decided in the second decimal, i.e. by LP convergence, not by tree size. If the on-corner
   boxes are dead the tree at 3.84 has 13 leaves; if alive, the observed branching (3 survivors per corner level, 19
   children per side level) gives 3⁴·(≈5)⁴ ≈ 10⁴–10⁵ leaves unless slack accumulation kills them earlier.
3. Viability for 3.85/3.86/3.87 on this machine: NOT with the present node LP. Cost model: 300–900 s per C1 node for
   ±0.05, and the deaths needed at 3.85 (root slack 0.06) / 3.86 (0.10) require ±0.01 accuracy ⇒ ≥ 30 min per node;
   with 10³–10⁵ nodes ⇒ weeks–years. Two things must change first: (a) the C1 node LP must converge 10× faster (warm-
   started dual simplex is fine — the bottleneck is column generation: use ≥ 1000 columns/iteration and keep all rows;
   from a cold start 1500 col/it converged the τ = 5 sanity LP in 2 min while 200 col/it stalled at 6.9 for 12 min) and
   (b) the corner/side "families" should be the placements NEAR the fractional packing's support (small boxes with big
   cores) rather than zone partitions — 9 of 12 corner boxes were dead by ≥ 0.2 at once, so coarse boxes are cheap to
   kill, but the surviving on-corner boxes need refinement to grow the core from side 0.45 to ≈ 0.9 to gain the missing
   ≈ 0.05–0.1; each refinement halves a box (2 LPs) so ~4–6 levels ⇒ 16–64 LPs per corner ⇒ 10³ LPs for the corner
   stage alone. Branching heuristic that worked: wall-first (corners, then sides), NO-child + coarse YES boxes, best-first
   by slack; symmetric root branch (WLOG corner 0) — 4× saving at level 1 only.
4. Concrete next step (cheap, decisive for 3.84): converge the three on-corner box LPs at 3.84 with shell rows to
   ±0.01 (≈ 30 min each with 1000+ columns/iteration; refine only if needed), then certify the 13 leaves with
   `certify.py --eps_geo 0.003` ⇒ **s(11) ≥ 3.84** would follow from a 13-node tree. If they are alive, run the
   corner-refinement stage (≈ 10³ LPs) before deciding about 3.85.
