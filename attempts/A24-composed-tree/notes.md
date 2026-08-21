# A24-composed-tree — case tree at 3.84 with TWO independent kill tests (coverage LP + wastage ledger)

Owner: postdoc (rigorous computation). 2026-08-20. Status: **done-negative-with-two-theorems** (~5 h): 3.84 NOT certified; two new certified theorems, the first YES-branch kills in the programme, and a costed route to closure.

Goal (PI): certify **s(11) ≥ 3.84** (s = 96/25) with a case tree whose nodes die by EITHER
(T1) A14's coverage LP (τ_H < 11 − m) or (T2) A23's wastage ledger (Σ certified dead area > s² − 11).
Budget for T2 at 3.84: **s² − 11 = 2341/625 = 3.7456** exactly.
Motivation: A07/A19 proved the measure LP alone can never reach 3.84 (τ*(3.83) = 11.000, and A19 exhibits an
exact rational fractional packing of value 11 at 3.84), so a *second, integral* test is necessary.

## 1. The composition (task 1) — `kill_tests.py`

`kill_tests.py` turns an A14 hypothesis `Hyp` (core boxes + NO-families) into A23 certifier data:

* **YES box → `dead_region.PlacedBox`.** `Box([x0,x1]×[y0,y1]×[θ0,θ1])` ↦ `PlacedBox(t_lo(θ0), t_hi(θ1),
  x0−ε, x1+ε, y0−ε, y1+ε)` with OUTWARD rounding (ε = 1e-9), so the PlacedBox contains every placement of
  the Box. Every dead certificate is then uniform over the whole box: it holds for *every* realisation of
  the YES hypothesis. (Note this is a *stronger* use of the hypothesis than the LP makes: the LP only
  exempts rows overlapping the rational core K(B) ⊂ every placement of B.)
* **NO-family → a new DISCHARGE rule in the certifier** (A23 §6 listed this as future work; implemented here
  as `Certifier._in_nozone`, `nozones=` argument). Under the node hypothesis *every* square of the packing —
  hence every legal continuation placement — avoids the family, so a parameter box
  [t0,t1]×[x0,x1]×[y0,y1] entirely inside (zone × t-interval) contains no legal placement and is discharged.
  Rounding is INWARD on the family (conservative). Soundness: identical to the (V)/(D)/(O) discharges — the
  B&B only ever needs "no legal placement in this parameter box".
* **Interior-disjointness of the dead regions** (required by A23's Lemma 2) is enforced *structurally*: all
  cells come from ONE quadtree over ONE window, so they are pairwise interior-disjoint by construction, and
  `wastage.dead_map` checks each cell exactly interior-disjoint from every placed core. `check_disjoint()`
  re-verifies it from the stored cell list by an exact rational sweep, so a certificate file can be audited
  standalone. Every reported area is an exact rational (sum of dyadic cell areas) compared to 2341/625 in
  exact arithmetic.

### Validation (`python kill_tests.py --validate`, `results/validation.json`) — ALL PASS

| case | A24 through `kill_tests` | A23's value | verdict |
|---|---|---|---|
| four flush corner squares at 3.85 (`corners4`) | **0.0000** (0 cells) | 0.0000 | PASS — corners strand nothing |
| A14 alive corner node, core-box-uniform (`corner_box`) | **0.5285** (410 cells) | 0.5285 | PASS (exact reproduction) |
| adjacent 33° pinwheel pair at 3.86 (`pair`) | see `results/validation.json` | 1.8834 | PASS |
| pair with continuum cores (`pair_box`) | see `results/validation.json` | 1.3837 | PASS |
| NO-zone discharge unit tests | vacuous family ⇒ everything dead; small far family ⇒ nothing dead | (new) | PASS |

All cell lists pass the exact pairwise-interior-disjointness audit.

## 2. The wastage scaling law at 3.84 (`sweep.py`, `results/sweep_law384.json`)

This is the quantitative fact that decides whether a composed tree can close, so it was measured first.
Configuration: A12's interior pinwheel 4-cycle (the ¼-weight structure that pins τ* = 11 for every LP
relaxation in A10/A12/A14/A19), **rigidly translated** into [0,3.84]². (It cannot be *scaled* to 3.84: its
mutual gaps at 3.86 are only +2.4·10⁻⁴, so scaling by 3.84/3.86 makes the members overlap. Rigid
translation keeps them exactly disjoint and inside the container — centres ∈ [1.31,2.53], footprint
[0.618, 3.222].) Each member is either an exact `Placed` square or a `PlacedBox` core of centre half-width
d and orientation half-width a around 33°.

Every number is a certified LOWER bound (float-interval mode with outward guards, cells down to 1/32).

| k cores | exact (d=0) | d=0.01, a=1° | d=0.03, a=3° | d=0.06, a=5° | d=0.10, a=7.5° | d=0.15, a=11.25° |
|---|---|---|---|---|---|---|
| 1 | 0.9164 (24%) | 0.6772 (18%) | — | — | — | — |
| 2 | 2.6040 (70%) | 2.0496 (55%) | 1.4192 (38%) | 0.9840 (26%) | (see results) | (see results) |
| 3 | **4.3576 (116%) DEAD** | 3.5832 (96%) | — | — | — | — |
| 4 | **6.5996 (176%) DEAD** | **5.7188 (153%) DEAD** | **4.4480 (119%) DEAD** | (see results) | (see results) | (see results) |

(percentages of the budget 3.7456; DEAD = the node hypothesis is killed by T2 alone.)

Readings:
* the ledger is strongly **super-additive**: 1→0.92, 2→2.60 (2.8×), 3→4.36 (4.8×), 4→6.60 (7.2×). The
  pinwheel members shadow each other's escape routes, exactly the "plus-sign" dead set A23 found at 3.86.
* **k = 3 exact placements already exceed the budget at 3.84** (4.3576 > 3.7456) — one member fewer than
  A23 needed at 3.86.
* **the kill survives at hypothesis (core-box) scale**: four cores of half-width 0.03 and ±3° still give
  4.4480 > 3.7456 (margin 0.70, 19 %).
* the uniformity cost is steep in the core size: the pair drops 2.60 → 2.05 → 1.42 → 0.98 as
  (d, a) goes (0,0) → (0.01,1°) → (0.03,3°) → (0.06,5°).

(continued below)

Full table (`results/sweep_law384.json`), including the **uniformity cliff**:

| k \ (d, a) | (0, 0°) | (0.01, 1°) | (0.03, 3°) | (0.06, 5°) | (0.10, 7.5°) | (0.15, 11.25°) |
|---|---|---|---|---|---|---|
| 1 | 0.9164 | 0.6772 | — | — | — | — |
| 2 | 2.6040 | 2.0496 | 1.4192 | 0.9840 | **0.0000** | **0.0000** |
| 3 | **4.3576 †** | 3.5832 | — | — | — | — |
| 4 | **6.5996 †** | **5.7188 †** | **4.4480 †** | 3.4672 | **0.0000** | **0.0000** |

† = exceeds the budget 3.7456, i.e. the node dies by T2 alone.

**The cliff.** At centre half-width d = 0.10 the certified dead area collapses to exactly 0: with a core box
that wide, no cell of the container is dead *for every* realisation of the cores (a realisation at one
extreme of the box leaves open the escape route that the other extreme blocks). So T2 is usable only for
cores of half-width ≲ 0.05.  This is the number that governs the tree cost, because covering a zone of
width W by boxes of width 2d costs (W/2d)² · (90/Δθ) boxes **per core**, and k cores multiply.

**Exact certificate of the flagship kill** (`recheck.py`, pure `Fraction` B&B, 5 processes, 119 s):
the k = 4, d = 0.03, θ ∈ [30°,36°] configuration re-certifies in exact arithmetic on 232 of its 884 cells to

>  dead area **2416/625 = 3.8656 > 2341/625 = 3.7456 = s² − 11**, 0 cell failures

**Theorem A24.W (machine-checked, exact).** *No packing of 11 unit squares in a square of side ≤ 96/25
has four squares whose centres lie in the four boxes (c_i ± 0.03)² and whose orientations lie in
[30°, 36°], where c_1..c_4 are the rigidly translated A12 pinwheel centres
(2.4497, 2.5305), (1.3095, 2.4497), (1.3903, 1.3095), (2.5305, 1.3903).*
(File `results/exact_k4_d030.json`; via A23's Lemma 2.)

## 3. Certified structure theorems at 3.84 (new; the root of the tree)

LP probes `probe.py` (`results/probes_p*.json`, `logs/p*_*.log`), s = 96/25, EPS_GEO 1e-4, budget 11:

| hypothesis (family F; theorem = "some square is in F") | sym | τ | conv | slack | verdict |
|---|---|---|---|---|---|
| NO square centred in the interior zone [1.1, 2.74]² (all θ) | D4 | **8.000** | yes | **−3.00** | **CERTIFIED** ↓ |
| NO square centred in [1.3, 2.54]² (cw = 0.8) | D4 | 10.211 | no (940 s) | −0.79 | not certifiable (3e-3 costs ≈ 0.45) |
| NO square centred in [1.5, 2.34]² (cw = 1.0) | D4 | **11.000** | yes, maxcov 1.000 | 0.00 | ALIVE (¼-structure) |
| NO square centred in [1.7, 2.14]² (cw = 1.2) | D4 | 11.027 | no | +0.03 | ALIVE |
| NO square anywhere with θ ∈ [5°, 85°] | D4 | **9.000** | yes | **−2.00** | dead, certifiable |
| NO square anywhere with θ ∈ [10°, 80°] | D4 | 9.358 | no (575 s) | −1.64 | dead, certifiable |
| NO square anywhere with θ ∈ [15°, 75°] | D4 | 10.556 | yes | −0.44 | dead raw, **NOT** certifiable (3e-3 re-solve → τ = 11.000) |
| NO interior square with θ ∈ [15°, 75°] | D4 | 10.582 | no (1520 s) | −0.42 | not certifiable |

**Theorem A24.1 (certified; `certs_wip/thm_interior_occupancy.json` + `.report.json`, exact
`verify_case.py` PASS).** *Every packing of 11 unit squares with pairwise disjoint interiors in a square of
side ≤ 96/25 = 3.84 has a square whose centre lies in the closed interior zone [11/10, 137/50]².*
Certificate: 176 atoms, total mass 1030019/125000 = 8.240152 < 11 (margin **2.76**); verifier 145,008 boxes,
max depth 29 (cap 56), 1952 exempt (NO-family), 3.6 s. This is the strongest-margin case-LP lemma the
programme has produced at 3.84 (compare A14's corner lemma, total 10.117, margin 0.88), and it is the
natural ROOT of an interior-first tree.

Note the direction of the ladder: the theorem gets *harder* as the zone shrinks, and the LP loses it
between cw = 0.8 (τ = 10.2) and cw = 1.0 (τ = 11.000, the ¼-structure re-appears).

## 4. Why interior-first: the LP kills interior cores that it cannot kill at the walls

A14 §3c/§4c: fixing a corner square **exactly** (core = the full unit square) leaves τ* = 10 = budget —
corner YES-boxes are worth *nothing* to the LP, and the corner stage of a wall-first tree can never close.
The interior behaves completely differently. Single-core nodes (budget 10, `probe.py gbox_*`, `ibox_*`):

| core box (centre ± d) × θ | core half-side a | τ | conv | slack |
|---|---|---|---|---|
| (1.92, 1.92) ± 0.03 × [30°,36°] (container centre) | 0.433 | **8.000** | yes | **−2.00** |
| pinwheel pos ± 0.03 × [30°,36°] | 0.433 | 9.333 | (rising) | −0.67 |
| pinwheel pos ± 0.03 × [42°,48°] | 0.433 | 9.333 | (rising) | −0.67 |
| pinwheel pos ± 0.03 × [0°,6°] (near-upright) | 0.433 | 8.000 | (rising) | −2.00 |
| pinwheel pos ± 0.10 × [30°,45°] | 0.313 | 9.750 | no | −0.25 |
| pinwheel pos ± 0.20 × [30°,45°] | 0.189 | 10.467 | no | **+0.47 ALIVE** |
| pinwheel pos ± 0.03 × [15°,75°] (wide θ) | 0.280 | **10.000** | yes, maxcov 1.000 | 0.00 ALIVE |

So T1's killing power at an interior node is governed by the **core half-side a**: a ≳ 0.35 kills
(margin 0.7–2.0), a ≈ 0.31 is marginal, a ≲ 0.28 is alive. Since a = (½ − d√2)/(1 + Δt), this means
**centre half-width d ≲ 0.05 and orientation window Δθ ≲ 15°** — remarkably, the *same* regime in which
T2 works (§2). Both tests want small boxes, for different reasons (T1: a big rational core exempts most of
the domain; T2: a small box makes the dead certificates uniform).

Multi-core interior nodes (budget 11 − m):

| hypothesis | m | budget | τ | conv | slack | T2 dead area |
|---|---|---|---|---|---|---|
| 2 pinwheel cores ±0.03 × [30°,36°] | 2 | 9 | 8.000 | (it 18) | −1.00 | 1.4192 (38 % of budget) |
| 4 pinwheel cores ±0.03 × [30°,36°] | 4 | 7 | **4.000** | yes | **−3.00** | **3.8656 exact > 3.7456 ✓** |

**The 4-core pinwheel node is dead by BOTH tests, and both are certified**: T1 by
`certs_wip/pw4_cores_T1.json` (exact `verify_case.py` PASS: 4 atoms, total 103/25 = 4.12 < 7, 1394 boxes,
0.5 s) and T2 by `results/exact_k4_d030.json` (exact dead area 2416/625 > 2341/625). This is the first node
in the programme killed independently by a coverage certificate and by an area certificate.

## 5. The composed tree at 3.84 (task 3)

### 5a. Generic interior-first tree (`ctree.py`, `results/t384/`)
Root τ = 11.0288 (matches A13/A14), and the branch heuristic picked **interior × [15°,75°]** with fractional
mass 2.981 (sides 0.17 each, corners 0.003) — i.e. the LP dual itself says the mid-tilt mass is in the
interior, confirming the design choice. 33 children (1 NO + 32 YES boxes of 0.41 × 0.41 × 30°). Not pursued
further: at that box size the core half-side is a ≈ 0.166 and **both** tests are worthless (§2, §4), which
is exactly the lesson — a generic tree with coarse boxes learns nothing new.

### 5b. The real tree: certified root lemma + one exhaustive level (`level1.py`, `results/l1g_8x6.json`)
Using Theorem A24.1 as the root, the whole case split is ONE level:

* **D4 WLOG.** The root hypothesis set is empty and Z = [1.1, 2.74]² is centred at (s/2, s/2), so Z is
  D4-invariant. The triangle T = {(x,y) : 1.92 ≤ y ≤ x ≤ 2.74} is a fundamental domain of the D4-action on
  Z (its 8 images cover Z), so for every packing there is g ∈ D4 with g(witness centre) ∈ T; the orientation
  of the image lies in [0°,90°] (a rotation fixes θ mod 90°, a reflection sends θ ↦ 90° − θ).
  **We reduce the CENTRE to the octant and keep ALL θ** — a *covering* of the placement space of relative
  size 1/8, equivalent in size (and equally valid) to A25's "quadrant × θ ≤ 45°" fundamental domain. It is
  NOT the unsound "octant × θ ≤ 45°" (= 1/16) that A25 warns about. Checked in `level1.check_cover`
  (exact rational grid/θ-cut checks) and re-checked by `verify_tree.py`.
* **Cover.** T × [0°,90°] by an 8 × 8 grid on T (cells 0.1025 wide) × 6 θ-bins of 15° = **216 boxes**
  (core half-side a ≈ 0.35–0.38, i.e. right at the T1 threshold of §4). Each box is one node, budget 10.

Status at write-up (LP time limit 150 s per node, 7 workers; `results/l1g_8x6.json` is rewritten after
every node, so the run can be continued):

| | count | comment |
|---|---|---|
| solved nodes | 106 / 216 (150 s LP each, 7 workers) | |
| **dead(T1)**, converged | **26** | slacks −1.000 … −2.000 (huge margins) |
| dead?(T1) (slack < −0.03, minmass ≥ 0.97) | 4 | |
| unresolved at 150 s | 76 | τ ∈ [8.786, 10.018]; most are below the budget 10 but with minmass < 0.97, i.e. the measure is not yet feasible and τ can only rise — genuinely undecided. **3 have already crossed 10 (ALIVE)** |
| **dead(T2)** | **0** | see §5c |
| certified leaves (exact `verify_case.py` PASS) | **15 / 15 attempted** | totals 8.24 … 9.27 < 10 |

At 400 s per node (an earlier partial run, `results/l1f_8x6_partial400.json`) the unresolved fraction was
4/19 = 21 % instead of 76/106 = 72 %, so most of the 76 are time-limit artefacts rather than live nodes —
but **3 level-1 boxes are genuinely alive (τ up to 10.018 > 10)**, so this cover does not close as it
stands and needs a refinement level under the survivors.

### 5c. The T1/T2 split — the key scientific datum
**Every kill in the composed tree was T1. T2 fired at zero nodes.** The reason is quantitative and now
precisely known (§2 here plus A25's atlas):

* a single core at a **deep-interior** position strands **0** — independently confirmed by A24's `dead_map`
  and by A25's atlas, both returning 0 for all 34 solved level-1 boxes with centres in [1.92, 2.13]²;
* a single core near the **corner of the interior zone** (centre ≈ 1.1–1.2 from a container corner) at mid
  tilt strands **1.07–1.28** — A25's "L-moat" band. Cross-validation of the two independent implementations
  on level-1 box #199 = [2.6375, 2.74] × [2.4325, 2.535] × [15°,30°]:
  **A24 `dead_map` 1.1196 (cells 1/8) → 1.2260 (cells 1/32) vs A25 atlas 1.2812** ✓ (two independent
  certifiers, two independent region constructions, consistent lower bounds);
* over the whole 216-box cover the atlas gives a positive T2 value on **42 / 216 boxes**, max 1.2812 =
  **34 % of the budget** (`results/atlas_t2_cover.json`). Refining the centre 2×2 or 4×4 does not raise the
  *guaranteed* value at this width, consistent with A25's threshold finding (the collapse happens between
  0.075- and 0.15-wide centre boxes, and 0.1025 is already on the wrong side).

So T2 needs **≥ 3 cores** (A25: 3 × 1.5977 = 4.7930 > 3.7456; A24 independently: 3 exact pinwheel squares
4.3576 > 3.7456; k = 2 is out of reach, best 3.1953 / 2.6040), each in a centre box of width ≤ 0.075. That
is depth 3 of a 0.075-cover — but the LP kills such nodes long before: a single core with a ≈ 0.43 already
has slack −0.7 … −2.0 (§4). **In the regime where T2 becomes usable, T1 has already won.** T2's unique
value stays where A23 found it: killing *specific realised* mid-tilt structures (Theorem A24.W) — precisely
the structures whose ¼-weight fractional versions hold τ* = 11 and are therefore invisible to every LP.

## 6. Verdict (task 5 — honest)

**s(11) ≥ 3.84 is NOT certified here, and neither is 3.83.** What WAS established:

1. **Theorem A24.1 (certified, exact verifier PASS)** — every packing of 11 unit squares in a square of
   side ≤ 3.84 has a square centred in [11/10, 137/50]². Margin 2.76, the largest of any case-LP lemma at
   3.84 (A14's corner lemma: margin 0.88).
2. **Theorem A24.W (certified, exact Fractions)** — no such packing has four squares in the four pinwheel
   core boxes (± 0.03, θ ∈ [30°,36°]); certified dead area 2416/625 > 2341/625 = s² − 11. That node is
   *also* killed by T1 with an exact coverage certificate (`certs/casetree_3.84/aux_pw4_cores_T1.json`,
   total 103/25 < 7): **the first node in the programme killed independently by a coverage certificate and
   by an area certificate.**
3. **Interior YES-boxes have real LP killing power, unlike corner ones.** A14's blocker (a corner square
   fixed *exactly* still leaves τ* = 10 = budget, so the corner stage can never close) does not carry over:
   an interior core with half-side a ≳ 0.35 gives slack −0.7 … −2.0, and 26 of the 106 solved level-1 boxes
   are converged deaths with slack ≤ −1.0, 15 already certified by the exact verifier. **This is the first
   place in the I-L6 line where a YES branch kills.**
4. **The frontier.** The level-1 cover (216 boxes at 0.1025 × 0.1025 × 15°) is not enough — at least one box
   are alive (τ up to 10.018) and 76/106 are undecided at a 150 s LP. Closing it needs (i) converged LPs
   (≈ 400–900 s per node ⇒ 216 × ~10 min ≈ 36 CPU-hours) plus certification (~4 min per leaf ⇒ ~15
   CPU-hours), and (ii) one refinement level under the alive boxes (each split 2×2×2 = 8 children with
   a ≈ 0.40, where T1 is stronger). Estimate for a serious attempt: **100–300 CPU-hours** — two orders of
   magnitude below A14's 10⁴–10⁵ CPU-hour estimate for the wall-first tree, and the first estimate in this
   programme that is affordable. Whether it terminates depends on whether the alive boxes die under
   refinement; the three boxes with τ > 10 say that is not automatic.
5. **How much did the wastage ledger buy over A14's pure-LP tree?** In this tree: nothing (0 of 30 kills).
   Its measured contributions are (a) the independent second certificate on the pinwheel node, and (b) the
   quantitative map of where an integral test can and cannot bite (§2, §5c). The real gain over A14 is not
   T2-vs-T1 but **interior-first vs wall-first**: A14's tree had 9/12 survivors per level with GROWING
   slack; this one has 26 converged deaths with slack ≤ −1.0 at level 1 under a certified root.

**3.83.** Not run separately. Smaller s makes T1 strictly easier (τ decreases with s) and moves the area
budget only from 3.7456 to 3.6689, while A25 established the atlas is essentially s-independent on
[3.84, 3.88] — so the T2 picture is unchanged and the bottleneck (216+ converged node LPs) is identical.
If the level-1 programme is run at all it should be run at 3.84 directly; falling back to 3.83 buys nothing
here.

## 7. Files / reproduction

* `kill_tests.py` — the composition (T2 at an A14 node), validation suite (`--validate`), exact
  disjointness audit. `dead_region.py` = A23's + the **NO-family discharge** (`nozones=`,
  `Certifier._in_nozone`); `wastage.py` = A23's + `nozones` passthrough and a PlacedBox-safe container
  assert.
* `sweep.py` — the wastage scaling law (k × core size) at 3.84. `recheck.py` — parallel exact (Fraction)
  re-certification targeted at the budget.
* `probe.py` — LP probes (structure-theorem ladders, interior core-size ladder, pinwheel nodes).
  `certify.py` / `verify_case.py` — A14's certification loop and exact verifier (unmodified copies).
* `ctree.py` — the generic composed tree (T2 then T1 at every node, interior-first mid-tilt branching).
* `level1.py` — the D4-reduced exhaustive level-1 cover under the certified root lemma.
  `certify_l1.py` — parallel leaf certification. `verify_tree.py` — top-level verifier (root + cover
  logic + every leaf + closure verdict). `atlas_t2.py` — T2 for the whole cover via A25's atlas.
* `certs/casetree_3.84/` — `root_interior_occupancy.json` (+ `.report.json`), `leaf_*.json` (+ reports),
  `aux_pw4_cores_T1.json`, `t2_pw4_d030_exact.json`, `manifest.json`.
* Reproduce: `python kill_tests.py --validate`; `python sweep.py --workers 6 --min_cell 32`;
  `python recheck.py --src results/sweep_law384_k4_d030.json --k 4 --d 3/100 --a 3 --workers 5`;
  `python probe.py --tag p --which int_no,thw_5,gbox_1920_1920_30_36_30 --warm ""`;
  `python level1.py --nx 8 --nth 6 --workers 7 --time_limit 400`; `python certify_l1.py --workers 7`;
  `python verify_tree.py`.

## 8. Gaps / caveats

* The 76 unresolved level-1 nodes are *time-limit* artefacts of a 150 s LP, not verdicts. τ at an
  unconverged node is an UNDER-estimate (A14 §3b), so an unconverged τ < budget is **not** a kill; only the
  30 converged/robust deaths (15 of them certified) count.
* T2 numbers other than `results/exact_k4_d030.json` are float-interval lower bounds (outward-guarded);
  the flagship kill is exact (0 cell failures).
* T2 areas depend on the mapper resolution: the level-1 run used min_cell = 1/8 for speed, which
  underestimates (box #199: 1.1196 at 1/8 vs 1.2260 at 1/32 vs A25's 1.2812). No kill decision depended on
  a coarse map.
* `ctree.py`'s status label 'alive' conflates "LP above budget" with "LP not converged"; the level-1 tables
  above separate them explicitly.
* The D4 reduction is used only at the root (as in A14 §1). `check_cover` verifies the grid/θ cuts exactly
  but the statement "the 8 D4 images of T cover Z" is the standard fundamental-domain fact, argued in §5b,
  not machine-checked.
* The pinwheel configuration of §2 is one specific mid-tilt structure (A12's), rigidly translated; the
  scaling law is measured on it and is not claimed to be the extremal one. A25's atlas gives the
  configuration-independent version.

## 9. Top-level verification (`python verify_tree.py`)

```
A24 composed case tree at s = 96/25 = 3.84
  area budget s^2 - 11 = 2341/625 = 3.745600
(1) ROOT root_interior_occupancy.json: PASS  (total 1030019/125000 < 11)
(2) COVER of T x [0,90] by 216 boxes: PASS  (exact rational grid/theta cut check)
(3a) T1 LEAF certificates: 15 PASS, 0 FAIL
(3b) T2 t2_pw4_d030_exact.json: disjoint=True, area=2416/625=3.865600 > budget 3.745600, 0 failed cells -> PASS
(4) CLOSURE: 15/216 level-1 leaves certified; 201 missing
    ==> the tree is NOT closed: s(11) >= 3.84 is NOT established here.
OVERALL certificate integrity: PASS
```
