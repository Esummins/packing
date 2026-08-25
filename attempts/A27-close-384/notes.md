# A27-close-384 — converging and refining A24's interior-first case tree at s = 96/25 = 3.84

Owner: rigorous-computation postdoc. 2026-08-24/25. Status: **done-negative-with-a-real-advance** — 3.84 is
**NOT** certified, but the tree is now much closer, the three boxes A24 left alive are **certified dead**, and
the verification chain is exact end to end for the first time.

Goal (PI): close the interior-first case tree at s = 96/25 ⇒ certified s(11) ≥ 3.84.
(The pure measure LP provably cannot reach 3.84 — A07 τ*(3.83) = 11.000, A19 exhibits an exact rational
fractional packing of value 11 at 3.84 — so a case tree is the only route in this line.)

---

## 0. Headline

1. **All 216 level-1 nodes are solved** (A24 had 106, each at a 150 s time limit). See §2 for the verdicts.
2. **The three level-1 boxes A24 reported ALIVE (idx 89, 95, 101) are now certified dead**, together with
   idx 84 = the diagonal mirror of 89 — see §4. This is the first time a live node of an I-L6 tree has been
   killed by refinement in this programme.
3. **A new exact top-level verifier `verify_tree2.py`** closes a real soundness gap in A24's `verify_tree.py`
   (§5): it checks, in exact rationals, that the certified core square really is contained in *every* unit
   square whose parameters lie in the node's box — the step that converts `verify_case.py`'s theorem about a
   core into a theorem about a parameter box. It also re-parametrises the whole tree by `t = tan(θ/2)`, which
   makes every cut, every tiling and the diagonal symmetry **rational**, so π never enters the verification.
4. **The D4 diagonal symmetry is machine-checked and used**: 31 exact transfers, 29 of which discharge the whole
   sub-tree under cell 84 from the sub-tree under cell 89 (§4.4).
5. **The frontier is now sharp** (§3): 20 level-1 cells are *provably* beyond the reach of the coverage LP at
   level-1 resolution (τ_LP ≥ budget with the column oracle exhausted), and level-2 refinement is what kills
   them — but two of the eight children of cell 89 needed a *third* level. That measured branching factor is
   the whole cost story (§6).

**Honest bottom line: the tree is not closed.** **123 of the 216 level-1 cells are discharged** by an exact,
machine-checked certificate chain (A24 had 15), leaving **93 open**; `verify_tree2.py` re-verifies all 162 leaf
certificates plus the root with 0 failures and prints the verdict. Closing the remaining 93 needs no new
mathematics, only CPU — a measured ~340 CPU-hours (§6).

---

## 1. What was run, and the two deliberate departures from A24's `level1.py`

Same cover, same root, same node LP. `level1.py`, `caselp.py`, `lpbox.py`, `certify.py`, `verify_case.py`,
`kill_tests.py` … are **verbatim copies** of A24's (the one edit to the copy of `caselp.py` is three words:
`solve_node` now keeps `res["hist_tail"] = history[-5:]` before deleting the history, so that the driver can
see `added_rows` of the last iteration — needed for the soundness rule below).

* **T2 (the wastage ledger) is not run per node.** A24 §5c measured that a *single* core strands at most
  1.2812 of the 3.7456 area budget anywhere on this cover (A25's atlas over all 216 boxes), i.e. T2 cannot
  kill a one-core node even in principle. A24 ran it anyway at every node and it fired 0 times. Skipping it
  gives the LP the whole time budget. (The auxiliary 4-core T2 certificate `t2_pw4_d030_exact.json` and its
  T1 twin are still carried in the certificate directory and re-checked, as A24's Theorem A24.W.)
* **A sound status rule.** The node LP is `min Σw` over atom measures subject to `μ(Q) ≥ 1` for every legal
  placement `Q`. Restricting the ROWS under-estimates τ, restricting the COLUMNS over-estimates it. Hence
  - a **kill** needs a *feasible* measure of total < budget: no violated row in the last iteration
    (`added_rows == 0` and `minmass ≥ 1`). An unconverged τ < budget is **not** a kill (A24 §8) — this is
    enforced in `run_l1.classify`.
  - **`alive(LP)`** (a rigorous *negative*) is `τ ≥ budget` **and** the column oracle exhausted
    (`maxcov ≤ 1+10⁻³`): the fractional packing is then dual-feasible for the *entire* atom space, so
    `τ_LP(box) ≥ τ(rows_cur, all atoms) = τ_cur ≥ budget`. Adding rows only raises τ. Such a node can
    **never** be killed by the coverage LP at that box size; only refinement can kill it.
  - everything else is `undecided` (the LP hit its time limit).

  In the end the arbiter of every death is the exact verifier `verify_case.py`, not this rule; the rule only
  decides where to spend CPU.

Ordering matters a lot: nodes are attempted **easiest-first** (by A24's τ), which harvests certifiable deaths
early instead of burning the budget on the hopeless tail.

---

## 2. Level 1: all 216 cells solved

| | count | comment |
|---|---|---|
| cells in the cover | **216** | 8x8 grid on the fundamental triangle T (cells j <= i) x 6 tilt bins of 15 deg |
| solved (LP run to convergence or to the 700 s limit) | **216 / 216** | A24: 106, at 150 s each |
| converged deaths `dead(T1)` (feasible measure, tau < 10) | **65** | tau 8.00 ... 9.12, slack -2.00 ... -0.88 |
| `alive(LP)` — LP optimum >= budget with the column oracle exhausted | **20** | see §3; only refinement can kill these |
| `undecided` (LP hit the time limit) | 131 | tau 8.5 ... 10.25; **not** verdicts (A24 §8) |
| **certified dead by the exact verifier** (the only statistic that counts) | **117 / 216** | A24: 15. Certificate totals 8.24 ... 9.9976 < 10 |
| discharged by refinement to level 2/3 | **4** | cells 89, 95, 101 (§4) and 84 |
| discharged by the diagonal symmetry alone | **2** | cells 59, 163 (mirrors of 56, 166) |
| **total discharged** | **123 / 216** | 93 open |

Note the gap between "converged death" (65) and "certified dead" (117): a node whose LP has not converged can
still yield a certifiable measure, because `certify.py` re-solves at the robustness margin EPS_GEO = 3e-3 and
then feeds the exact verifier's witness placements back as rows. **The exact verifier, not the LP status, is
the arbiter of every death.** Three certification attempts failed outright (cells whose LP slack was only
-0.2 ... -0.4, where the 3e-3 margin costs about 0.45 and the certificate total would exceed the budget);
those cells stay open and would need refinement.

Reading: the deep-interior cells (small `i`, near the container centre) die with slack −1.0 … −2.0 in seconds;
the cells towards the corner of the interior zone are the hard ones, and the ones sitting exactly at τ = 10.000
are the ¼-weight structure of A07/A12/A19 re-appearing inside a conditional LP.

---

## 3. The frontier: 20 cells are provably out of reach of the level-1 LP

The 20 cells with `tau >= 10` **and** the column oracle exhausted (`maxcov <= 1 + 1e-3`) are

`72, 78, 79, 83, 84, 95, 100, 101, 105, 106, 107, 110, 111, 112, 114, 115, 147, 159, 201, 202`

of which **84, 95, 101 are now discharged by refinement** (§4) and 89 (tau = 10.25 at the 700 s limit) with
them. The remaining 16 are the genuine level-1 frontier.

For each of these the LP optimum over the *whole* atom space is ≥ 10 = budget, so no amount of extra LP time
at level 1 can kill them — the box has to be cut. This is a strictly stronger statement than A24's "alive"
(which conflated "τ above budget" with "LP not converged").

**The free A26 band pre-filter (task 3) is provably inert on this tree**, and `prefilter.py` records exactly
why. Theorem A26.1 says *at most one* square has band clearance `R ≥ 0.93`; a hypothesis is therefore killed
for free only if it places **two** cores in that band. Every node of the interior-first tree — at every level —
carries exactly **one** core, so the cap is never exceeded. (`prefilter.py` computes `Rlo` for all 216 cells:
range 0.3929 … 1.2051, 24 cells with `Rlo ≥ 0.93`; a synthetic two-core hypothesis is included as a live unit
test showing the filter does fire when it can.) The same holds for the A26.2 caps (4 at 0.5665, 5 at 0.42) and
for the sharpened A28.★ threshold `w* = (s−2)/2 = 0.92` at 3.84. **Cost of this branch: 0 CPU-seconds, and the
honest answer is "no kills".** It would only pay in a tree whose nodes fix two or more squares.

---

## 4. The three live boxes are dead (the main new mathematics)

A24's frontier was "at least three level-1 boxes are alive (τ up to 10.018) so the cover does not close as it
stands". All three, and the mirror of one of them, are now certified dead.

### 4.1 Cell 101 = [2.4325, 2.535] × [2.0225, 2.125] × [75°, 90°] — **closed at level 2**
Refined 2×2×2 (centre half-width 0.0256, tilt half-window 3.75°, core half-side a ≈ 0.41). All eight children
have τ between 8.68 and 9.00 and **all eight are certified** (`leaf_101_000 … leaf_101_111`, exact
`verify_case.py` PASS, totals 9.16 … 9.27 < 10).

### 4.2 Cell 95 = [2.4325, 2.535] × [1.92, 2.0225] × [75°, 90°] — **closed at level 2**
Same split; children τ ∈ [8.61, 9.00]; **all eight certified**.

### 4.3 Cell 89 = [2.33, 2.4325]² × [75°, 90°] — **closed at level 3**, and cell 84 with it
Five of the eight children die at level 2 (`89_000, 89_001, 89_011, 89_100, 89_110`, certified).
The other three do not:

| child | τ | maxcov | verdict |
|---|---|---|---|
| `89_010` (θ ∈ [75°, 82.5°]) | **10.000000** | **1.000000** | `alive(LP)` — LP optimum ≥ budget, refinement is the only option |
| `89_111` (θ ∈ [82.5°, 90°]) | **10.000000** | **1.000000** | `alive(LP)` |
| `89_101` | 9.675 | 1.091 | LP slack only −0.325; certification FAILED (1801 s) — the 3·10⁻³ robustness margin costs ≈ 0.45, so the certificate total would exceed 10 |

All three were split again (centre half-width 0.0128, tilt half-window 1.875°, a ≈ 0.44). **All 24
grandchildren have τ ∈ [7.03, 9.00] and all 24 are certified.** So cell 89 is discharged by a complete depth-3
sub-tree of 5 + 24 = 29 certificates.

That `89_010` and `89_111` are the two children carrying tilt closest to axis-parallel (θ ≡ 0–15° mod 90°) at
centre ≈ (2.38, 2.38) is exactly the near-upright configuration that the pure LP cannot see; it takes a
0.0128-wide box before the conditional LP gets slack.

### 4.4 Cell 84 — free, by the diagonal symmetry, machine-checked
σ(x, y, θ) = (y, x, 90° − θ) is the reflection of [0,s]² in its main diagonal, hence maps packings to packings.
In the `t = tan(θ/2)` coordinate σ(t) = (1−t)/(1+t), a **rational** involution of [0,1], so the whole step is
exactly checkable. Cell 84 = (i,j,k) = (4,4,0) and cell 89 = (4,4,5); σ maps the centre box onto itself
(it is diagonal-symmetric) and the tilt bin [0°,15°] onto [75°,90°].

Naively transferring the certificate fails by ≈ 7·10⁻⁸: the t-endpoints of a box are outward-rounded to
denominator 2²⁴ (`t_lo`, `t_hi`), and σ of one rounding is not inside the other. `verify_tree2.py` avoids this
by checking, for each node under 84, that the *mirror node's certified core is contained in every unit square
whose parameters lie in the σ-image of that node* — the image box, not the mirror's own box. The slack in the
containment is ≈ 4 % (worst projection 0.4864 … 0.4884 against the bound 0.5), so the 10⁻⁷ rounding is
harmless and the transfer is exact. **29 such transfers discharge the entire sub-tree under cell 84**, and two
more discharge cells 59 and 163 outright from their mirrors 56 and 166.

---

## 5. `verify_tree2.py` — what is new, and the gap it closes

A24's `verify_tree.py` checked (i) the root certificate, (ii) that the cover cells exist, (iii) each leaf
certificate through `verify_case.py`, (iv) that the leaf's stored box equals the cover box. But
`verify_case.py` proves a statement about a **core square K**: *no packing of 11 unit squares has a square
containing K*. The step "every unit square with (centre, θ) in the box B contains K(B)" — the whole point of
`caselp.Box.core()` — was **never machine-checked**; it was float arithmetic inside the certificate builder.
`verify_tree2.py` now checks it in exact rational interval arithmetic (`core_in_every_square`): the four
vertices of K are `k ± a·u_m ± a·v_m` and it bounds their projections on Q's two axes over a subdivision of
the box (24 t-slices × 4 × 4 centre slices), rejecting unless every projection is ≤ 1/2. Typical worst
projection at level 1 is 0.468 … 0.489, i.e. the construction has ≈ 2–6 % slack. **All 162
certificates pass it.**

Everything else is exact too:
* the cover is recomputed from scratch in `Fraction`s: `Z = [11/10, 137/50]²`, `m = 48/25`, `h = 41/50`,
  x-cuts `m + h·i/8`, tilt bins `[t_lo(15k), t_hi(15(k+1))]`; the bins' union is checked to be exactly `[0,1]`
  (`t_lo(0) = 0`, `t_hi(90) = 1`, `t_lo(15k) ≤ t_hi(15k)`) and every cell (i,j,k) with j ≤ i is checked to
  match its certificate's box exactly;
* the 8-way refinement tiling is checked exactly (shared x/y cuts at the rational midpoint, overlapping tilt
  cut `t_lo(mid) ≤ t_hi(mid)`);
* the σ-symmetry transfers as in §4.4;
* the closure recursion accepts a node if it has its own certificate, or all eight children are discharged, or
  its σ-mirror is.

`python verify_tree2.py` re-runs `verify_case.py` on the root and on every leaf and prints the verdict.

```
A27 case tree at s = 96/25 = 3.84   (t = tan(theta/2) parametrisation)
(1) ROOT: verifier=PASS shape=True zone==[11/10,137/50]^2 True  total=1030019/125000 < 11
(2) COVER: 216 cells; x-cuts True, t-bins union [0,1] True, count True, cell<->box exact True
(3) CORE CONTAINMENT + (4) LEAF certificates: 162 PASS, 0 FAIL
(6) SYMMETRY: 31 exact sigma-transfers (2 whole cells + the 29-node sub-tree under cell 84)
(7) CLOSURE: 123/216 level-1 cells discharged; 93 open
    ==> the tree is NOT closed: s(11) >= 3.84 is NOT established here.
OVERALL certificate integrity: PASS
```
Breakdown of the 123: 117 by their own leaf certificate, 4 by a complete set of children (cells 84, 89, 95,
101), 2 by the diagonal symmetry alone (cells 59, 163).

---

## 6. Why it did not close, and what closing costs (measured, not guessed)

The measured branching structure at 3.84:

* level 1 (cells 0.1025 × 0.1025 × 15°, core half-side a ≈ 0.35): **117/216 certified dead, 93 open**, of which 16 are provably `alive(LP)` and the rest are cells whose LP did not converge inside the 700 s limit;
* level 2 (0.05125 × 0.05125 × 7.5°, a ≈ 0.41): of the 32 children solved here (cells 89, 95, 101), **30 have
  τ ≤ 9.68** and 29 certify; **2 are `alive(LP)` at τ = 10.000** — a survival rate of ≈ 6 %;
* level 3 (0.0256 × 0.0256 × 3.75°, a ≈ 0.44): of the 24 children solved here, **all 24 have τ ≤ 9.00 and all
  24 certify** — survival rate 0 so far.

Cost per node, measured on this machine (20 cores, but RAM-bound at ≈ 8–9 concurrent LPs of this size):
* node LP to a usable state: 100 s (easy) … 700 s (time limit), median ≈ 300 s;
* certification (`certify.py`: re-solve at EPS_GEO = 3·10⁻³, rational certificate ×1.03, exact `verify_case.py`,
  witness feedback, ≤ 4 rounds): 300 s (easy) … 2400 s (marginal), median ≈ 700 s.

So a *closed* tree needs, on the level-2/3 rates above,
`93 open cells × (1 + 8 + 0.06·64) ≈ 93 × 13 ≈ 1200 nodes × ≈ 1000 s ≈ 340 CPU-hours`,
plus the ≈ 190 CPU-hours already spent here. That is about 2× the budget of this attempt but is **not** a wall: it is a
week of the same machine, or a day on 8 machines, with no new mathematics required. The A24 estimate
(100–300 CPU-hours) was optimistic by roughly a factor of 2–3, because (a) many more level-1 cells survive
than A24's partial run suggested and (b) certification, not the node LP, is the dominant cost at the margin.

Two things would cut it materially:
1. **Skip the level-1 LP on cells that are going to survive and refine immediately.** The `alive(LP)` test is
   cheap (it is decided as soon as the column oracle is exhausted, typically < 250 s), while grinding an
   undecided cell to the 700 s limit buys nothing. Roughly a third of the level-1 CPU here was spent this way.
2. **Certify from the parent's dual.** Every level-2 certificate here was built from scratch; the parent's
   converged measure is an excellent warm start and `certify.py` already accepts one.

The **wastage ledger (T2) remains worthless in this tree**, for the reason A24 identified and this attempt
re-confirms: it needs ≥ 3 simultaneous cores in centre boxes of half-width ≤ 0.05, and by the time a node
fixes three squares that precisely, T1 has killed it many levels earlier. The same is true of the A26 band
counting lemmas (§3). **The only test doing any work in this line is the conditional coverage LP.**

---

## 7. Files / reproduction

```
python run_l1.py --tag l1 --workers 8 --time_limit 700          # all 216 level-1 nodes (resumable)
python certify_a27.py --tag l1 --workers 8 --resolve_time 250   # certify every dead/near-dead cell
python refine.py children --parents 89,95,101 --tag l2          # 8-way split of the live cells
python refine.py solve    --tag l2 --parent_tag l1 --workers 8
python certify_a27.py --tag l2 --workers 8
python prefilter.py                                             # the (inert) A26 band filter + its unit test
python analyze.py                                               # node statistics, certificate inventory
python verify_tree2.py                                          # EXACT end-to-end verification + closure verdict
python make_manifest.py
```

* `run_l1.py` — level-1 driver (warm starts from A24, per-node checkpoints, sound status rule).
* `refine.py` — 8-way refinement; node paths `"<cell>"`, `"<cell>_abc"`, `"<cell>_abc_def"`.
* `certify_a27.py` — parallel certification with a two-stage weight-scale policy (1.03, then the auto scale
  that leaves 0.5 % headroom under the budget — this recovered several marginal cells, e.g. cell 28 at total
  9.975429 and `89_110` at 9.975343).
* `prefilter.py`, `analyze.py`, `verify_tree2.py`, `make_manifest.py` — as above.
* `certs/casetree_3.84/` — root certificate, all leaf certificates, the A24 auxiliary pinwheel certificates,
  `manifest.json`.
* `results/l1/`, `results/l2probe/`, `results/l2probe95/`, `results/l3probe/`, `results/l3b/` — node LP results
  and checkpoints; `results/*_summary.json`, `results/analysis.json`, `results/verify_tree2.json`.

## 8. Gaps / caveats (honest)

* **The tree is not closed**; 3.84 is not certified. The certified statements are the root lemma (A24.1), the
  leaf lemmas, and the four closed cells of §4.
* The D4 WLOG at the root is used exactly as in A24/A14: `check_cover`/`verify_tree2` verify the grid and tilt
  cuts exactly, but "the 8 images of the fundamental triangle T cover the zone Z" is the standard
  fundamental-domain argument, stated in A24 §5b, not machine-checked. (The *diagonal* reflection used inside
  the tree in §4.4 **is** machine-checked.)
* `alive(LP)` rests on the column oracle's numerical maximum `maxcov`; it is a negative statement used only to
  direct CPU, never part of a certificate.
* Certification failures are not deaths and not survivals: a cell whose certificate fails (e.g. `89_101`,
  τ = 9.675) may still be dead — it just needs a smaller box. All such cells here were refined.
* The machine was powered off once mid-run; all node results and certificates are checkpointed to disk and the
  full exact re-verification after the restart passed with 0 failures, so nothing was silently lost.
