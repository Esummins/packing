# A24-composed-tree — case tree at 3.84 with TWO independent kill tests (coverage LP + wastage ledger)

Owner: postdoc (rigorous computation). 2026-08-20. Status: **running** (updated as results land).

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
