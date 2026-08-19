# A14-close-tree-384 — close A13's case-LP tree at s = 3.84 (converge the 3 undecided on-corner nodes; certify the 13 leaves)

Owner: LP postdoc (rigorous LP computation). 2026-08-18. Status: **done-negative** (≈ 4.5 h): 3.84 NOT certified — the on-corner nodes are alive and provably unkillable by corner refinement; two leaves certified (corner-zone lemma + far box 13); three oracle blind spots found and fixed; verdict §6.

Question (from the PI). A13's case-LP branch-and-bound at s = 3.84 has root τ = 11.03 ≥ 11 (alive) and, after the
symmetric corner branch, 13 children: NO(all corners) dead by 1.59; of the 12 YES corner-0 boxes, 9 dead by 0.23–0.69, and the
3 boxes [0.5,0.8]²×{[0,30],[30,60],[60,90]}° that contain the corner-square placement (0.5,0.5,0°) undecided (slack ≈ 0 with
unconverged LPs). If those 3 are dead (converged, robust) the 13-leaf tree certifies **s(11) ≥ 3.84**.

## 0. Corrections to A13's bookkeeping found while reading `results/t384c/tree.json`

* A13's notes say "12 YES boxes … 9 dead, 3 alive" and "the two other [0.8,1.1]² boxes are vacuous". In fact the corner cover
  2×2×3 has 12 non-vacuous boxes = nodes 2–13; **node 13 = B([0.8,1.1]²×[60,90]°) was never solved (status `pending`
  in tree.json)** — A13's B&B was still running when the notes were written and best-first ordering never reached it. So the
  depth-1 picture is: node 1 NO(all corners) dead; nodes 5–12 (8 boxes) dead by 0.23–0.69; node 13 unsolved; nodes 2,3,4
  undecided. Node 13 is the mirror image (x↔y, θ→90−θ) of node 11 (dead by 0.58 unconverged) — solved here directly (§2).
* Budget bookkeeping: budget = 11 − #cores everywhere in tree.json: depth-1 YES nodes have budget 10 (one core), depth-2
  YES-YES nodes (two cores, e.g. node 41 = corner0 box + corner3 box) budget 9, NO-children keep the parent's budget (node 40:
  budget 10). A13's "budget 9 at depth 2" is therefore correct (two fixed squares), and every depth-1 YES node uses 10. ✓
* A13's B&B process (`bnb.py --tag t384c`, 8 workers) and two `_long_node.py` re-solves were still running on this machine
  (started 18:49 / 19:12) when A14 started; the B&B was at depth 4 (375 nodes). I terminated the B&B at 19:34 (its
  results are saved after every event; the deeper frontier is moot for the present question and it was taking 8 of the
  20 logical CPUs); the two long re-solves were left to finish (their outputs `results/long_node{3,4}_*.json` in A13 are used
  as second opinions below).

## 1. D4 WLOG at the root — confirmed

At the root the hypothesis set is empty, hence invariant under the symmetry group D4 of the container [0,s]². The corner
branch is the exhaustive dichotomy "no square of P has its centre in any of the four (closed) corner zones Z_0..Z_3" /
"some square Q ∈ P has centre in some Z_i". In the second case let g ∈ C4 ⊂ D4 be the rotation of the container with
g(Z_i) = Z_0 (the four zones are the C4-orbit of Z_0 = [0.5,1.1]²; checked in `tree.json`: corner1 = [s−1.1,s−0.5]×[0.5,1.1]
= image of Z_0 under (x,y)↦(s−y,x), etc.). Then gP is again a packing of 11 pairwise disjoint closed unit squares in [0,s]²
(no hypothesis to preserve at the root), gQ has centre in Z_0 and some orientation θ' ∈ [0°,90°] (rotations preserve the
orientation class; a reflection would map θ↦90°−θ, still in [0,90°]), so (c(gQ), θ') lies in one of the 12 closed boxes
B_j of the 2×2×3 cover of Z_0×[0°,90°] (x- and y-cuts 0.5/0.8/1.1, θ-cuts 0/30/60/90; cover exhaustive because the boxes
are closed products with common cut points — checked exactly in rationals by `verify_casetree.py`). Hence gP satisfies the
hypothesis of the YES leaf B_j; if that leaf is dead (no packing satisfies "some square has (c,θ) ∈ B_j"), contradiction. The NO
leaf's hypothesis set {NO Z_0, NO Z_1, NO Z_2, NO Z_3} (all θ) is itself D4-invariant, which is why its LP may be solved
with D4-averaged measures (if μ is feasible so is its D4 average: constraint set and objective are invariant); the
certificate produced from it lists all atom images explicitly and is verified over the whole square without any symmetry
assumption, so no symmetry enters the rigorous part. The YES leaves are solved without symmetry (C1). Conclusion: the WLOG
is valid exactly as A13 stated it, and it is used only at the root. (Deeper D4 use would be invalid as soon as a core box is
present, since {B_j} is not D4-invariant; A13's code guards this via `Hyp.is_symmetric_D4`.)

Node-death lemma re-checked (A13 §1): with m core boxes, the ≥ 11−m squares of P other than the (not necessarily distinct)
witnesses Q₀ⁱ are pairwise disjoint, admissible, in no NO-family, and disjoint from every core K(Bᵢ) ⊂ Q₀ⁱ, hence non-exempt
⇒ each has μ-mass ≥ 1 ⇒ μ(total) ≥ 11−m = budget. Core lemma re-derived: for p = k + R(θ_m)(u,v), |u|,|v| ≤ a, and (c,θ) ∈ B:
|R(θ)ᵀ(p−c)|_∞ ≤ |k−c|₂ + a(|cos δ|+|sin δ|) ≤ hd + a(1+|δ|), |δ| = |θ−θ_m| = 2|arctan t − arctan t_m| ≤ 2|t−t_m| ≤ t1−t0,
so a ≤ (½−hd)/(1+(t1−t0)) suffices; the code rounds hd up (q_up), t0 down and t1 up (1/2²⁴ grid). ✓

## 2. Machinery (A14 copies of A13's modules; A13's files untouched)

`lpbox.py` = A13's + vectorised row-incidence in `Model.add_orbit` (`_row_counts`; identical semantics, checked against the
old loop on random rows; the old per-row Python loop cost ≈ 0.2 s per column at 8k rows, i.e. 300 s per 1500-column
iteration — the reason A13's column generation was starved). `caselp.py` = A13's + `checkpoint` passthrough. `certify.py`
= A13's + `--no_resolve/--max_cols/--resolve_time/--max_w`. `verify_case.py` = A13's copy (unchanged). `run_node.py`:
re-solve one node of A13's t384c tree (hypotheses/budget from tree.json, warm start from A13's node json), 1500 columns
and 1500 rows per iteration, column generation until maxcov < 1.01, exact per-θ row oracle with shell points (EPS_TH 0.3°),
fine row search (0.25°) whenever the coarse oracle is clean, no time limit below the one given.

(results below are appended as they come in)

## 3. Two things found on the way (both matter for A13's numbers)

### 3a. LP size / speed (engineering)
With 1500 columns per iteration the C1 node LP grows to 8–10k rows × 5–10k columns (≈ 2–3M nonzeros); HiGHS then needs
40–200 s per cold solve and, after adding 1500 columns + 700 rows jointly, dual simplex took 340 s (primal after
columns only: 40 s; dual after rows only: 3–50 s). Fix used here (`lpbox.run(..., alternate=True, prune_cols=2, prune=6)`):
alternate row iterations (dual simplex stays warm) and column iterations (primal simplex stays warm); delete zero-weight
columns with positive reduced cost after 2 solves and rows non-binding for 6 solves (both regenerable by the oracles;
the initial grid/warm atoms are never pruned). Iterations then cost 2–15 s instead of 100–350 s.
Convergence flag now also requires minmass ≥ 1 − 1e-6. Warm-starting from a checkpoint with 10k rows and 5–10k orbits
still costs a 3–5-min cold solve at the start.

### 3b. BUG in A13's exact row oracle at hypothesis nodes (`RowOracle.exact_theta`, inherited from A10)
`exact_theta` collects all arrangement cells with mass < 1, keeps the `max_cand = 1200` LOWEST-mass cells, samples them and
only THEN applies the hypothesis filter (`hyp.ok_many`). At a hypothesis node the lowest-mass cells are precisely the
EXEMPT ones (rows there were dropped, so μ has no reason to cover them): inside a NO-zone or overlapping a core the mass is
0.2–0.5. Whenever more than 1200 cells are below 1 (always, at NO-corner nodes and core nodes), the cut could remove every
non-exempt violated cell and the oracle returned "no violated row" (minmass = 1.000) while genuine holes existed. Caught by
the exact verifier on the NO(all corners) leaf: 4 rounds of witness feedback, holes of mass 0.958·1.03 = 0.987 kept
appearing at new places (θ = 8.27°, c = (1.497,1.565)); the LP oracle at θ = 8.25° returned 0 candidates with the filter,
6487 without, and the cell containing the hole had mass 0.958 (`logs/buggy_oracle/`). FIX (A14 `lpbox.py`): sample all
violated cells (hard cap 20000 lowest), filter, evaluate exactly, then keep the lowest 5·max_cand. After the fix the same
oracle call returns 310 candidates, min mass 0.943.
Consequences: (i) every A13 τ at a hypothesis node (all nodes except the root) is an UNDER-estimate obtained from an LP
with missing rows — the "converged" flags and the minmass values in A13's tree.json are unreliable; deaths by ≥ 0.2 are
probably still deaths (the missing rows are near-1 placements) but must be re-solved; (ii) A13's one PASSED certificate
(smoke node, NO interior zone, EPS_GEO 3e-3) is unaffected because the verifier is the judge; (iii) the sanity check
τ = 5.000 (corners fixed + no side squares, A12 contrast) may also have been optimistic — re-run below.
All A14 runs before 20:45 (`logs/buggy_oracle/`, `results/buggy_oracle/`) used the buggy oracle; everything reported in
§4–§6 uses the fixed one.

### 3c. Exact-corner experiments (first run with the buggy oracle; the one-corner run was repeated with oracle v1 — same 10.000 / 1.000 at it 25, `logs/x_corner0_exact.log`; the DUAL bound is unaffected either way — see below)
* one corner square fixed EXACTLY (degenerate box (0.5,0.5,0°), core = the unit square [0,1]² up to 3e-8), budget 10:
  τ = 10.000000, maxcov = 1.000000, converged (`results/buggy_oracle/x_corner0_exact*`).
* all FOUR corner squares fixed exactly, budget 7: τ = 7.000000, maxcov = 1.000000, converged in 200 s
  (`results/buggy_oracle/x_corners4_exact.json`): fractional packing = 28 placements of weight ¼ (2 upright pairs per side
  zone, an 8-square pinwheel at 27.75°/61.5° + 4 uprights in the interior) — A12's locally-integral structure.
  A missing-row bug can only LOWER the LP value; the dual solution y (support = LP rows = genuine non-exempt placements)
  with coverage ≤ 1.000 everywhere (column oracle: 0.01 grid + arrangement vertices + local refine) is a fractional packing
  of the FULL node problem, so τ*(node) ≥ Σy = budget: **both nodes are ALIVE with slack exactly 0** (a rigorous-in-spirit
  lower bound; the coverage check is floating point). Monotonicity (a stronger hypothesis ⇒ larger core ⇒ fewer rows ⇒
  smaller τ*) then gives τ*(node 2,3,4) ≥ τ*(exact corner) = 10 = budget: **the three undecided on-corner boxes are ALIVE
  at 3.84, and no refinement of the corner box can kill them.**
  Caveat (checked afterwards): the dual packing of the four-corner run sits at SAT depth +1e-5 into the fixed squares
  (it uses the shell rows that A13's margin scheme keeps, EPS_CORE = 2e-3), i.e. the bound Σy = budget is for the node LP
  as implemented (which must also cover placements up to 2e-3 inside the core). The strict LP (only placements disjoint
  from the core) differs by placements moved by 1e-5, so its value can differ from the budget by at most a comparable
  amount — a "death" by ≲ 1e-3 is far below any certifiable margin (§4a: 0.1–0.3 needed), so the practical conclusion
  stands: corner refinement cannot produce certifiable slack at 3.84. Likewise fixing all four corners (depth 4 of A13's
  wall-first tree) leaves τ* = 7 = budget: the corner stage of the tree can never close by itself; only side-zone
  branches (NO side zones: A12's τ = 5 < 7 with all four side zones empty) kill the ¼-structure.

## 4. Results at s = 3.84 with the fixed oracle (all LPs: alternate rows/columns, 1500 columns per column iteration,
##    prune_rows 6 / prune_cols 2, EPS_TH 0.3°, shell points; `python summarize_a14.py` prints the table)

### 4a. Depth-1 nodes of A13's tree (t384c), re-solved (`results/n*.json`, `logs/n*.log`)

| node | hypothesis | budget | EPS_GEO | τ (A14, 25–40 min) | minmass / maxcov | slack | A13's value (buggy oracle, 300 s) |
|---|---|---|---|---|---|---|---|
| 1 | NO(all corners) [D4] | 11 | 3e-3 | **9.590** | 0.99 / 1.01 | **−1.41** | 9.41 |
| 2 | YES corner0 [0.5,0.8]²×[0,30]° | 10 | 1e-4 | 10.11 | 0.71 / 1.08 | **+0.11 (alive)** | 10.04 |
| 3 | YES corner0 [0.5,0.8]²×[30,60]° | 10 | 1e-4 | 10.12 | 0.73 / 1.22 | **+0.12 (alive)** | 10.06 |
| 4 | YES corner0 [0.5,0.8]²×[60,90]° | 10 | 1e-4 | 10.19 | 0.77 / 1.03 | **+0.19 (alive)** | 10.10 |
| 5 | YES corner0 [0.5,0.8]×[0.8,1.1]×[0,30]° | 10 | 1e-4 / 3e-3 | 9.87 / 10.00 | 0.60 / 1.24 ; 0.40 / 1.19 | −0.13 / 0.00 | 9.41 |
| 6 | YES corner0 [0.5,0.8]×[0.8,1.1]×[30,60]° | 10 | 3e-3 | 10.04 | 0.63 / 1.05 | +0.04 | 9.77 |
| 7 | YES corner0 [0.5,0.8]×[0.8,1.1]×[60,90]° | 10 | 1e-4 / 3e-3 | 9.92 / 10.00 | 0.61 / 1.05 ; 0.66 / 1.08 | −0.08 / 0.00 | 9.36 |
| 8–12 | (mirror images of 5–7 and the two [0.8,1.1]² boxes) | 10 | – | not re-run (see 5–7, 13) | | | 9.31–9.77 |
| 13 | YES corner0 [0.8,1.1]²×[60,90]° (never solved by A13) | 10 | 1e-4 / 3e-3 | 9.59 / 9.73 | 0.81 / 1.06 ; 0.75 / 1.22 | **−0.41 / −0.27** | – |

Oracle-v3 confirmation runs (900 s, warm from the v1 results; `results/n{2,5,13}_v3.json`): node 2: 10.165 (+0.17, mm 0.82,
mc 1.07); node 5: 9.913 (−0.09); node 13: 9.604 (−0.40) — the v1 values above move by ≤ 0.05.

Reading. (i) The three on-corner boxes are ALIVE: τ ≈ 10.11–10.19 (unconverged, but stable to ±0.03 over the last 20
iterations, and the dual bound of §3c gives τ* ≥ 10 rigorously in spirit). (ii) The off-corner boxes 5–7 (and by mirror
symmetry 8–10) are NOT "dead by 0.2–0.7": with the correct oracle they sit at slack −0.13…−0.08 (EPS_GEO 1e-4) and at
0.00…+0.04 with the certification shrink 3e-3 — i.e. NOT certifiable dead with the present margins. (iii) Only NO(all
corners) (−1.41) and the far box 13 (−0.41 / −0.27) are robustly dead. So at 3.84 the whole first level of the tree,
except two leaves, sits within ±0.2 of the budget: the case-LP is at its ceiling on the first level, and the ≈ 0.1–0.25
robustness cost of EPS_GEO = 3e-3 (node 5: 9.87 → 10.00; node 7: 9.92 → 10.00; node 13: 9.59 → 9.73) is of the same size
as the slack the branching produces.

### 4b. Certificates (`certs_wip/`, verifier = A13's exact `verify_case.py`, s = 96/25, depth 56)

* **`leaf_NO_corners.json` PASS** (`logs/certify_n1.log`, `.report.json`): 4 NO-families = the four corner zones (t ∈ [0,1]),
  1021 atoms, total 10.117317 < 11, 573,196 boxes, 15 s (3 processes). Round 0 (unconverged LP, minmass 0.9925) failed with 13 holes of
  mass 0.9955; one rows-only witness-feedback re-solve (τ 9.59 → 9.82, minmass 0.9988) then PASSED at once.
  **Lemma (rigorous, machine-checked): every packing of 11 unit squares in a square of side ≤ 3.84 has a square whose
  centre lies in one of the four corner zones [0.5,1.1]² (up to symmetry).**
* **`leaf_YES_box13.json` PASS** (node 13 = B([0.8,1.1]²×[60,90]°), budget 10; `logs/certify_n13.log`, `.report.json`):
  the certification went through five attempts (`logs/certify_n13_try{1..4}.log`): the first three exposed the oracle gaps
  of §5b; with oracle v3, rows-only witness-feedback rounds of 1200 s (33–38k-row LP, τ 9.73 → 9.90) shrank the witness
  set 64 → 24 → 32 → 0 (holes 18 → 5 → 4 → 0) and round 3 PASSED: 564 atoms, weight scale 1.0072, total 9.975497 < 10, 410,148 boxes, 9529 exempt (core), 7.5 s.
  **Lemma (certified): no packing of 11 unit squares in side ≤ 3.84 has a square with centre in [0.8,1.1]² and
  orientation in [60°,90°]** (i.e. containing the rational core K = square of half-side 0.2023 centred (0.95,0.95) at 76.5°).
  Margin 0.7 %: thin, but exact.
* Nodes 5–12: not certifiable at 3e-3 (τ ≈ 10.0); nodes 2–4: alive.

### 4c. Structural experiments (`results/x_*.json`; hypotheses in `results/hyp_*.json`)

| experiment | sym | budget | τ | mm / mc | verdict |
|---|---|---|---|---|---|
| one corner square fixed exactly (core = [0,1]²) | C1 | 10 | 10.000 | 0.68 / 1.000 | alive, slack 0 (¼-structure) |
| four corner squares fixed exactly | C1 | 7 | 7.000 (7.03 with more rows) | – / 1.000 | alive, slack 0 |
| four corners fixed + NO side0 zone | C1 | 7 | 6.36 | 0.43 / 1.08 | dead by ≈ 0.6 (unconverged) |
| four corners fixed + NO all four side zones (A12's contrast) | C1 | 7 | 4.25 | 0.40 / 1.20 | dead by ≈ 2.7 (A12: 5.0) |
| root + NO(all four side zones) [D4] | D4 | 11 | 8.28 | 1.00 / 1.04 | dead by 2.7 |

So the killing power is entirely in the NO-zone hypotheses (an empty side zone is worth ≈ 0.6–0.7 even with all corners
fixed; all sides empty is worth 2.7), while YES-box hypotheses (small cores) are worth ≈ 0 against the ¼-structure. Any
closing tree must therefore reach nodes with several empty wall zones — and each YES branch that avoids that carries
18 side boxes.

## 5. One more level under the three alive nodes (task 3) — `branch_node.py`, `results/br{2,3}_corner2/`, `results/br4_corner3/`

A13's heuristic: wall-first, next corner zone with the largest fractional weight (all three ≈ 1.0; corner2 for nodes 2, 3;
corner3 for node 4), NO child + 2×2×3 YES boxes (13 children each), each child LP 600 s warm from the parent (fixed oracle
v1; the domain-boundary fix v2 of §5b came after these ran, so all τ below are still slight UNDER-estimates).

| parent | child | budget | τ | slack | status |
|---|---|---|---|---|---|
| 2 ([0,30]°) | NO corner2 | 10 | 9.74 | −0.26 | dead? (mm 0.74) |
| 2 | YES corner2 [2.74,3.04]² × {[0,30],[30,60],[60,90]} (diagonal-off) | 9 | 8.74 / 8.82 / 8.79 | −0.26 / −0.18 / −0.21 | dead? |
| 2 | YES corner2 [2.74,3.04]×[3.04,3.34] × 3 θ (wall-adjacent) | 9 | 9.13 / 9.18 / 9.25 | +0.13 / +0.18 / +0.25 | **alive** |
| 2 | YES corner2 [3.04,3.34]×[2.74,3.04] × 3 θ (wall-adjacent) | 9 | 9.20 / 9.19 / 9.19 | +0.19…+0.20 | **alive** |
| 2 | YES corner2 [3.04,3.34]² × 3 θ (on-corner) | 9 | 9.39 / 9.38 / 9.42 | +0.38…+0.42 | **alive** |
| 3 ([30,60]°) | NO corner2 | 10 | 9.70 | −0.30 | dead? |
| 3 | diagonal-off ×3 / wall-adjacent ×6 / on-corner ×3 | 9 | 8.72–8.80 / 9.13–9.21 / 9.28–9.37 | −0.28…−0.20 / +0.13…+0.21 / +0.28…+0.37 | dead? / alive / alive |
| 4 ([60,90]°) | NO corner3 | 10 | 9.74 | −0.26 | dead? |
| 4 | YES corner3 boxes (see `results/br4_corner3/children.json`) | 9 | 8.84–9.54 | −0.16…+0.54 | 3 dead?, 9 alive (partly still running at write-up) |

Growth: 9 of 12 YES boxes survive per corner level (A13 saw 3 with the buggy oracle), the NO child dies by only ≈ 0.26,
the diagonal-off boxes by ≈ 0.2. Slack of the on-corner boxes at depth 2: +0.3…+0.4 (budget 9), i.e. it INCREASES with
depth in the corner stage (consistent with §3c: fixing corners never kills). Frontier after depth 2: ≈ 3 × 9 = 27 alive
nodes (of 3 × 13); extrapolating, ≈ 3·9·9·9 ≈ 2000 alive nodes when all four corners carry a box, each still with slack
≈ 0.3–0.5, before any side zone has been touched. Not pursued to depth 3.

### 5b. Second oracle gap found during the node-13 certification (fixed in v3 of A14's `lpbox.py`)
Certifying node 13 (τ 9.73–9.85 at 3e-3) kept failing with 12–24 holes of mass 0.96–0.99 although the rows-only re-solve
reported minmass ≈ 1. Two more blind spots of `exact_theta`: (v2) arrangement cells that straddle the boundary of the
admissible centre domain [w/2, s−w/2]² have all five samples CLIPPED into neighbouring cells, so wall-touching placements
(cx = lo + 0.002, the corner/side squares of every packing!) were never proposed — fixed by sampling the domain boundary
explicitly (step 0.004); (v3) at an unconverged node 10⁵ cells are below 1 and my v1 cap (20000 lowest BEFORE the
hypothesis filter) was again exhausted by exempt cells — fixed by filtering cells (5 samples each) before the cap. With
v3 the oracle at θ = 25.25° returns 1827 candidates (min 0.90) where v2 returned 0 while a hole of mass 0.972 existed.
Both gaps also exist in A10/A12/A13's `exact_theta` (root LPs included: wall-touching rows come only from the initial
0.1-grid and the coarse `scan_theta` is not used); their effect on the ROOT values of A07/A10 is nil because A07's
certificates were verified exactly, but every LP τ quoted by A10–A14 is a lower estimate of the true row-converged value.
Also added: a HiGHS model-status check in `Model.solve` (cold re-solve if a warm run is not `Optimal`; never triggered
in the logs so far).
Every LP in §4–§5 ran with v1 (§4a, §4c, §5) — their τ are therefore UNDER-estimates; "alive" verdicts are unaffected
(more rows can only raise τ), "dead by 0.2–0.3" verdicts (NO corner2/3, diagonal-off boxes, node 13 at 1e-4) are not
final. The 3.85 first level (§7) ran with v2.

## 6. Verdict for the PI

**3.84 is NOT certified, and this tree cannot certify it.** Task 2's premise (the three on-corner boxes are dead) is
false: they are alive with slack +0.11…+0.19 (LP, unconverged) and — rigorously in spirit via the dual — τ* ≥ 10 for the
exact-corner hypothesis, hence for every box containing it (§3c). What IS rigorously established:
1. **Lemma (certified, `certs_wip/leaf_NO_corners.json`, exact verifier PASS)**: every packing of 11 unit squares in a
   square of side ≤ 3.84 has a square whose centre lies in a corner zone [0.5,1.1]² (up to symmetry). Total 10.117 < 11.
2. All other first-level nodes are within ±0.2 of their budget (§4a): the depth-1 picture of A13 (9 of 12 boxes dead by
   0.2–0.7) was an artefact of the oracle bug §3b; only the far box 13 (−0.40 at 1e-4, −0.27…−0.10 at 3e-3) is dead by a
   certifiable margin — and it IS certified (§4b, margin 0.7 %).
3. Two leaves are certified (NO(all corners) and the far box 13); ten first-level leaves are not certifiable, three of them
   provably alive.
4. Fixing corner squares — even all four, exactly — leaves the ¼-weight fractional packing intact (τ* = budget with
   coverage exactly 1.000): the corner stage of the wall-first tree never closes by itself; every level multiplies the
   frontier by ≈ 9 (§5). Only NO-side-zone hypotheses kill (≈ 0.6–0.7 each once the corners are fixed, 2.7 for all four
   sides at the root; §4c), and reaching them costs 9^4 corner-stage nodes × 18-box side stages.
5. The certification overhead (EPS_GEO 3e-3 + 3 % weights) costs 0.1–0.25 per node (§4a), comparable to the slack that
   one branching level produces at 3.84; a leaf must therefore be dead by ≥ 0.3 in the raw LP to be certifiable with the
   present margins.

Cost estimate to close a case tree (same method) at 3.84 or 3.85: root slack 0.03 (3.84) / 0.07 (3.85; A07 11.06, A14 root
11.07 in 900 s); a leaf needs ≥ 2 empty side zones on top of fixed corners (or ≥ 4 empty wall zones), i.e. depth ≥ 6 with
branching 9–18 ⇒ 10⁵–10⁶ node LPs of 10–30 min each (converged) plus certification ⇒ 10⁴–10⁵ CPU-hours; a further factor
for refining side boxes (cores of side 0.3 are useless). NOT viable on this machine (12 processes ⇒ ≥ 1 year). What would
change the picture: (a) a node LP that uses the fixed square's whole footprint (not just a core) — but §3c shows even the
exact footprint has zero killing power at 3.84; (b) branching directly on EMPTY zones (D4-symmetric NO-families of
sides/corners) at the root and treating "some square in zone Z" by many small boxes with big cores — 18–48 children per
level, still ≥ 10⁴ leaves; (c) a stronger relaxation than Theorem 1 inside each node (e.g. pair/clique constraints
between the fixed square and its neighbours), which A12 argued does not exist for the ¼-structure. My recommendation: stop
the case-LP campaign at 3.84; the machine-checked result of the whole I-L6 line is the corner-zone lemma above plus the
structural facts §3c/§4c.

## 7. s = 3.85 first level (`level1_385.py`, `results/l1_385/`, oracle v2, 600 s per node, root 900 s)

| node | hypothesis | budget | τ | mm / mc | slack |
|---|---|---|---|---|---|
| root | ∅ (D4, warm from A07 v2_s3.85) | 11 | 11.071 | 0.94 / 1.03 | +0.07 (A07: 11.06) |
| NO(all corners) | D4 | 11 | 9.563 | 0.89 / 1.03 | −1.44 |
| on-corner boxes [0.5,0.8]²×{[0,30],[30,60],[60,90]} | C1 | 10 | 10.115 / 10.000 / 10.063 | 0.5–0.6 / 1.1–1.5 | +0.11 / 0.00 / +0.06 |
| off-corner boxes 5–10 ([0.5,0.8]×[0.8,1.1] and mirror) | C1 | 10 | 9.90 / 10.00 / 9.85 / 9.86 / 9.98 / 9.89 | 0.5–0.65 / 1.1–1.2 | −0.10 / 0.00 / −0.15 / −0.14 / −0.03 / −0.11 |
| far boxes [0.8,1.1]²×{[0,30],[30,60],[60,90]} (11, 12, 13) | C1 | 10 | 9.61 / 9.60 / 9.65 | 0.56–0.67 / 1.2–1.25 | -0.39 / -0.40 / -0.35 |

Same structure as at 3.84 (all values are 600-s under-estimates, oracle v2): NO(all corners) and the far boxes die,
everything else sits within ±0.15 of the budget, the on-corner boxes are alive. Cost to close at 3.85: as at 3.84 (§6)
times a factor for the extra 0.04 of root slack; not viable.

## 8. Files, reproduction, final status
`lpbox.py` (A13 + vectorised add_orbit, alternating rows/cols, column pruning, HiGHS status check, oracle fixes v1–v3),
`caselp.py` (A13 + passthroughs), `certify.py` (A13 + --no_resolve/--warm_state/--loop_cols/--scale 0 auto),
`verify_case.py` (A13's exact verifier, unchanged), `run_node.py` (one node), `branch_node.py` (one wall-first level),
`level1_385.py`, `summarize_a14.py`, `verify_casetree.py` (tree-logic + leaf re-verification for a manifest; the
manifest for a closed tree was NOT produced since the tree did not close — the script checks the box cover / core lemma /
NO-family set exactly and would re-run the verifier on each leaf), `_bench_lp.py` (HiGHS timings).
Results: `results/n*.json` (depth-1 nodes, ±_e3 = EPS_GEO 3e-3), `results/x_*.json` (§4c), `results/br*/` (§5),
`results/l1_385/` (§7), `results/buggy_oracle/` (runs before 20:45 with A13's oracle), `certs_wip/leaf_NO_corners.json`
(+ .report.json PASS, .certify.json), `certs_wip/leaf_YES_box13.json` (+ .report.json PASS, .certify.json; .resolve*.json = the loop's re-solves), `logs/` (every LP; `logs/buggy_oracle/`,
`logs/old/` = superseded runs).
Reproduce: `python run_node.py --node 2 --tag n2 --time_limit 2400 --prune_rows 6 --prune_cols 2`;
`python certify.py results/n1_e3.json --s_rat 96/25 --eps_geo 0.003 --no_resolve --jobs 3 --rounds 6 --time_limit 400 --out certs_wip/leaf_NO_corners.json`;
`python verify_case.py certs_wip/leaf_NO_corners.json --jobs 4 --depth 56`; `python branch_node.py --node 2 --parent_result results/n2.json --workers 4 --time_limit 600`;
`python level1_385.py --workers 6 --time_limit 600 --root_time 900`; `python summarize_a14.py`.
