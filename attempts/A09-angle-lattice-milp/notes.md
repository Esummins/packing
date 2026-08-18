# A09 — angle-lattice MILP ("symmetries + lattice points")

Owner: A09 (postdoc, MIO / comp. geometry). Date: 2026-08-18. Time used: ~2 h wall clock (one machine
crash in the middle; the first CP-SAT batch's logs survive in `results/crashed/`).

## 1. Goal

Test the PI's idea: at FIXED orientations θ_1..θ_n the packing problem is a disjunctive LP, so for a finite
angle lattice Θ ⊂ [0°,90°) "min s s.t. n unit squares with angles in Θ pack in [0,s]²" is a MILP.
Questions: (i) does it reproduce the known theorems (calibration); (ii) does it find Trump's packing AB INITIO
(no contact graph given) when θ* ∈ Θ; (iii) how does it scale with |Θ|; (iv) can it PROVE optimality
(gap 0), i.e. is it a certifier or only a finder; (v) n = 12 probe; (vi) sketch of the interval (angle-box)
version and of measure-LP-per-box pruning.

## 2. Formulation (`milp_pack.py`)

Variables: s; centres (x_i, y_i); z_{i,k} ∈ {0,1} (square i has angle θ_k, Σ_k z_{ik} = 1); y_{ij,a} ∈ {0,1}
for every pair i<j and every SIGNED axis a of the deduplicated set A = {±(cos φ, sin φ) : φ ∈ {θ_k, θ_k+90°}}
(|A| = 4|Θ|; e.g. 8 for {0°,45°}, 40 for the 10-angle lattice).

* containment: x_i ≥ Σ_k w_k z_ik, x_i ≤ s − Σ_k w_k z_ik (same for y), w_k = (cos θ_k + sin θ_k)/2. No big-M.
* disjointness (SAT): Σ_a y_{ij,a} ≥ 1 and, for each a,
  a·(c_j − c_i) − Σ_k H(a,k)(z_ik + z_jk) ≥ −M_a (1 − y_{ij,a}),  H(a,k) = (|a·e1(k)| + |a·e2(k)|)/2,
  M_a = (s_max − 1)(|a_x|+|a_y|) + 2 max_k H(a,k) (tight per-axis M; s_max = 4).
  Every row is sound (disjoint projections ⇒ disjoint squares) and the family is complete (a separating
  axis can be taken among the edge normals of i or j, all of which are in A). Optional link cut
  y_{ij,a} ≤ z_{i,k(a)} + z_{j,k(a)} (axis must belong to i or j; default on).
* symmetry breaking: angle index non-decreasing in i, x_i ≤ x_{i+1} within an angle class (relabelling), and
  centre of mass in the lower-left quadrant (90° container rotations preserve every angle class). Both
  are valid simultaneously (rotate first, then relabel).
* s ≥ √n (area) as an explicit variable bound.
* Two back-ends: HiGHS (highspy 1.15, MILP) and OR-tools CP-SAT 9.x (scaled integers, scale 1e5, all
  disjunctions as OnlyEnforceIf on (y, z_i, z_j); rhs rounded up so solutions are conservative up to the
  1e-5 rounding of the axis vector). `--fix-s` gives the pure feasibility problem; `--counts` fixes the
  number of squares per angle; `--warm` feeds a MIP start (HiGHS).
* Post-processing ("polish"): the solver's incumbent fixes the combinatorics (angle assignment + the
  separating axis of every pair, chosen as the axis with the largest margin); with those fixed the problem
  is an LP in (s, centres) which is re-solved with HiGHS LP ⇒ exact optimum of that combinatorial structure
  to ~1e-9. `make_cert.py` then rationalises (t = tan(θ/2) to 12 dp, centres to 10 dp, LP re-solved with a
  2e-7 slack) and runs the lab's exact verifier `certs/verify_certificate.py` (Fractions).

Model sizes (n = 11): {0°}: 254 cols / 562 rows; {0°,45°}: 505 / 1073; 5 angles: 1607 / 3277; 10 angles:
2761 / 5587 (HiGHS counts; CP-SAT similar).

## 3. Results

Machine: 20 logical cores, ≤ 4 concurrent solver processes, CP-SAT with 6 workers each (so runs competed for
CPU; single-run times would be somewhat shorter). "bound" = solver's proven lower bound at the end.

### 3.1 Calibration (must match known theorems)

| Θ | n | best s (polished) | expected | solver / status | time to incumbent / total | structure |
|---|---|---|---|---|---|---|
| {0°} | 5 | 3.000000000 | 3 | HiGHS OPTIMAL (gap 0); CP-SAT OPTIMAL | 0.1 s / 0.1 s | 5×0° |
| {0°} | 10 | 4.000000000 | 4 | HiGHS OPTIMAL (gap 0) 473 s; CP-SAT OPTIMAL 0.1 s | — | 10×0° |
| {0°} | 11 | 4.000000000 | 4 | HiGHS: NOT finished in 600 s (bound stuck at √11 = 3.3166); CP-SAT OPTIMAL 0.1 s | — | 11×0° |
| {0°,45°} | 5 | 2.7071067812 | 2 + 1/√2 = 2.7071067812 (Göbel) | HiGHS OPTIMAL 1.0 s; CP-SAT OPTIMAL 0.1 s (bound 2.70710 at 1e-5 resolution) | — | 4×0° + 1×45° |
| {0°,45°} | 10 | 3.7071067812 | 3 + 1/√2 = 3.7071067812 (Stromquist) | CP-SAT OPTIMAL, 535 s (single run, 6 workers) | — | 9×0° + 1×45° |
| {0°,45°} | 11 | **3.8856180832** | 2 + (4/3)√2 = 3.8856180832 (Stromquist 2003 Thm 3) | CP-SAT FEASIBLE, bound stuck at 3.31663 (= √11) after 900 s; incumbent found at 46 s (crashed run) / 61 s (seed 7); seeds 0 and 11 stalled at 3.9142 (7×0°+4×45°) for 420–900 s | 46–61 s / 900 s | 6×0° + 5×45° |

Polished values agree with the closed forms to < 1e-12 (e.g. {0,45}, n=11: 3.8856180831641263 vs
2+4√2/3 = 3.885618083164127). Rational certificates written by `make_cert.py` PASS the exact verifier
(`results/n11_0_45_seed7_cert.json`: s(11) ≤ 777123799/200000000 = 3.885619).

HiGHS verdict: usable only for tiny instances; on n = 10/11 uprights it either takes 8 min or does not
finish; its dual bound never leaves √n. All further runs used CP-SAT.

### 3.2 Ab-initio test

| Θ | n | best s (polished) | solver status / bound | time to incumbent | structure |
|---|---|---|---|---|---|
| {0°, θ*}, θ* = 40.18193729032971646523° | 11 | **3.8770835900228144** (Trump: 3.877083590022814; diff 4e-16) | FEASIBLE, bound 3.31663 after 900 s (both runs) | 23 s (crashed run) / 39 s (re-run) | 6×0° + 5×θ* — Trump's arrangement (3 uprights on the left wall, 3 along the bottom, 1 top-right, 1 right-bottom, pinwheel of 5 tilted; `plots/n11_0_trump.png`); exact certificate `results/n11_0_trump_cert.json` PASSES (s(11) ≤ 3.877084509) |
| {0°,30°,35°,40°,45°} | 11 | **3.8776388450** | FEASIBLE, bound 3.31663 after 900 s | 3.888 at 975 s (crashed run); 3.87764 in the re-run (< 900 s) | 6×0° + 5×40° — the SAME Trump structure with the nearest lattice angle (`plots/n11_5ang.png`); certificate PASSES (s(11) ≤ 3.877639744) |
| {0°,5°,…,45°} (10 angles) | 11 | 3.8989273267 | FEASIBLE, bound √11 after 600 s | 3.9142 at 82 s, 3.8989 at 566 s | 6×0° + 3×40° + 2×45° (a Trump-like 6+5 with a mixed tilted cluster; not yet the optimum 3.87764 available on this lattice) |
| {0°, θ*}, counts fixed 6+5, s FIXED = 3.87707 (feasibility: "is there anything strictly below Trump on this lattice?") | 11 | — | UNKNOWN after 900 s (neither a packing nor a refutation) | | |

So the MILP finds Trump's packing ab initio in well under a minute when θ* is on the lattice, and finds
Trump's STRUCTURE (with the lattice angle 40°, s = 3.87764, only 5.5e-4 above s*) from a coarse 5-angle
lattice; a final continuous polish (A03's contact-graph Newton solve) would then recover θ* and s* exactly.

### 3.3 Proving optimality — no

In every n = 11 run (HiGHS or CP-SAT, any lattice, even with the angle counts fixed and s fixed just below
Trump) the proven lower bound stayed at √11 = 3.31663 for the whole run. Diagnosis: the LP relaxation of the
disjunctive rows is void — with y_{ij,a} = 1/|A| every big-M row is slack by M_a(1 − 1/|A|) ≥ 2.5, so the
relaxation only sees containment + s ≥ √n; the CP-SAT LP bound is exactly √11·10⁵ = 331663 for the same
reason. Tight per-axis M does not change this (M_a ≥ 3 is forced by the geometry: centres can be up to
s−1 apart). Refuting "s < s*" needs the solver to enumerate the combinatorial structures, and 55 pairs ×
8–40 axes is far too many for either solver in 15 min: even the pure feasibility question at s = 3.87707
with 6+5 counts fixed (`n11_0_trump_feas65`) is UNKNOWN after 900 s. Incircle cuts (|c_i − c_j| ≥ 1) are
themselves disjunctive in a linear model (|dx| + |dy| ≥ 1 needs 4 sign cases; the ∞-norm version needs 4
too) and cannot lift an LP bound that is blind to all pairwise rows; and an external bound s ≥ 3.82 (the
lab's Theorem 1) only raises the floor to 3.82, it does not close the gap to 3.877. n = 10 with {0°,45°}
IS proven (535 s) — the frontier of what CP-SAT can certify on this model is around n = 10 with 2 angles.

**Verdict: heuristic ab-initio finder — yes (Trump in < 1 min); certifier — no.**

### 3.4 Scaling with |Θ| (n = 11, CP-SAT, 6 workers, 900 s / 600 s)

| |Θ| | axes | time to first good incumbent | best after run | remark |
|---|---|---|---|---|---|
| 1 | 4 | 0.1 s (optimal) | 4 | trivial |
| 2 | 8 | 23–61 s | 3.87708 / 3.88562 | seed-dependent (LNS): 2 of 4 seeds on {0,45} stalled at 3.9142 |
| 5 | 20 | ~300 s | 3.87764 (Trump structure at 40°) | crashed run had 3.888 at 975 s; re-run better (randomness) |
| 10 | 40 | 82 s (3.914), 566 s (3.899) | 3.8989 (6×0°+3×40°+2×45°) | did not reach the 5-lattice value 3.87764 that this lattice also contains |

Practical rule: |Θ| ≤ 5 is fine as a finder; the primal heuristics degrade quickly with |Θ| (LNS
neighbourhoods have to guess angle classes AND axes), so a fine lattice must be reached by successive
refinement (coarse lattice → structure → refine angles near the found ones), not in one shot.

### 3.5 n = 12 probe (600 s each, CP-SAT)

| Θ | best s | status |
|---|---|---|
| {0°,45°} | 4.000 (12 uprights… i.e. the trivial 4×4 grid) | no packing < 4 found; bound √12 = 3.4641 |
| {0°,40°,45°} | 4.000 | idem |

Nothing below 4 for n = 12 on these lattices in 10 min; s(12) ≤ 4 is the trivial bound and the literature
(Friedman DS7) also has s(12) = 4 conjectured with no better packing known, so this is expected. Not a proof
of anything.

## 4. Assessment for the PI

(a) **Ab-initio viability.** As a *finder*: yes and cheap — the point-lattice MILP with CP-SAT recovers
Trump's arrangement in 23–39 s from Θ = {0°, θ*} and its structure from a 5-angle lattice (s = 3.87764,
6+5 at 40°) in minutes, with no contact graph given, and the fixed-structure LP polish gives the exact
lattice optimum. Combined with A03's exact contact-solve this is a complete ab-initio pipeline for
"lattice structure → exact rigid packing". As a *certifier* (prove that nothing better exists on the
lattice): no — the LP relaxation is void, the bound stays at √n, and even feasibility refutation at
s = s* − 1e-5 with counts fixed is out of reach in 15 min. For n = 12 nothing < 4 in 10 min on 2–3-angle
lattices; a longer run with a 5-angle lattice {0,30,35,40,45} and s fixed to 3.99 (feasibility mode) is
the cheap next probe (`--fix-s 3.99`), but s(12) = 4 is the conjecture and I would not expect a hit.

(b) **Interval (angle-box) version.** Replace each square by a *core* K_i(B) ⊂ ∩_{θ∈B_i} Q(c,θ): a fixed
convex polygon (translate of a shape depending only on the box) contained in every rotation of the box.
Rigorous construction: K = conv{p_1..p_m} with each p_r verified to lie in Q(0,θ) for ALL θ ∈ B, i.e.
r·max_{θ∈B}|cos(φ_r−θ)| ≤ 1/2 and r·max_{θ∈B}|sin(φ_r−θ)| ≤ 1/2 (1-D interval maxima, exact); good
choices are the intersection points of the edge lines of the two extreme rotations (an octagon; for a
narrow box it is the square shrunk by O(width)). Disjointness of the true squares ⇒ disjointness of the
cores ⇒ SAT disjunction over the FIXED edge normals of the cores (≤ 8 per square, dedupable across squares
of the same class); containment ⇒ x_i ∈ [w_min(B_i), s − w_min(B_i)] with w_min = min over the box of
(cos+sin)/2. Infeasibility of that MILP at s = s_target proves: no packing with angle multiset in the box
has side ≤ s_target. This is a rigorous relaxation and it converges (cores → squares as the boxes shrink,
loss in s is O(box width)). Quotients: order the angle classes (multiset), so a box is a non-decreasing
tuple of intervals; 90° symmetry is already in θ ∈ [0,90); reflections identify θ ↔ 90°−θ when the box
family is symmetric. B&B: bisect the widest interval; kill a box when the core-MILP is infeasible at
s_target; refine otherwise. **Cost estimate from what we measured**: the per-box oracle is exactly the
point-lattice feasibility MILP (cores instead of squares), and that oracle did NOT terminate in 900 s on
the easiest possible box (a point box, 6+5 counts, s = s* − 1e-5). Even at δ = 5° the number of boxes
(multisets of 11 intervals out of 18, ≈ C(28,11) ≈ 2×10⁷ before pruning) times ≥ 10³ s per box is 10¹⁰ s.
The interval B&B is therefore NOT viable with a MILP/CP-SAT feasibility oracle; it would need a *cheap*
box killer — which is exactly (c).

(c) **Measure-LP per box.** Theorem 1 relativised: if μ ≥ 0 on [0,s]² has μ(Q) ≥ 1 for every closed unit
square Q ⊂ [0,s]² whose orientation lies in the angle set Θ_B (union of the box's intervals) and
μ([0,s]²) < n, then no packing with all n orientations in Θ_B has side ≤ s (same shrink-and-scale
proof; note the shrunk squares keep their orientations). With counts: if the box says n_c squares have
orientation in class c, it suffices that μ(Q) ≥ α_c on class c with Σ_c n_c α_c > μ(total) — a weighted
covering LP, still linear. Fewer coverage rows ⇒ smaller τ*_B(s) ⇒ boxes are killable well above the
global ceiling 3.83; for the two-point box {0°}∪{45°} this is precisely Stromquist's Theorem 3
(2 + 4√2/3), which A07's LP would reproduce with placements restricted to θ ∈ {0,45}. This oracle costs
one LP (~seconds with A07's row generation, minutes with rigorous verification) instead of an unfinished
MILP, so the practical B&B is: angle-box tree, kill boxes with the restricted measure LP (rigorous via
`certs/verify_measure.py` restricted to the θ-range — a one-line change: skip t-boxes outside Θ_B), and
only in boxes that survive down to small width switch to structure enumeration (case-LP I-L6 /
core-MILP). The box count is then governed by how far τ*_B(3.877) stays below 11 as boxes shrink; a
quick way to estimate it is to run A07's LP with θ restricted to [θ*−δ, θ*+δ] ∪ {0} for δ = 10°, 5°, 2°
and see where τ* crosses 11 — not done here (out of time), recommended as the first task of the follow-up.

## 5. Files

`milp_pack.py` (builder, HiGHS + CP-SAT, polish), `make_cert.py` (rational certificate + exact verify),
`results/*.json` (packings: centres, angles, s, solver status/bound/time), `results/*_cert.json` (verified
rational certificates), `results/*.log` (solver logs; `results/crashed/` = first batch, machine crash),
`plots/n11_0_45_seed7.png` (Stromquist optimum), `plots/n11_0_trump.png` (Trump), `plots/n11_5ang.png`
(Trump structure at 40°), `plots/n5_0_45.png`, `plots/n12_*.png`.

Reproduce: `python milp_pack.py --n 11 --angles 0,40.18193729032971646523 --solver cpsat --threads 6 --time 900 --out r.json --png r.png`
then `python make_cert.py r.json`.
