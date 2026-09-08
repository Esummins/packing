# A144 T1/T2 — the measurement

## 0. T1: the generator, and the two things it had to get right

`code/guardline.py`. The row of a node is

```
    SUM_p |l n Q_p| x_p  <=  rhs(l)  =  s0 - SUM_pins minchord(P_j, l) - minchord(H, l) ,
```

with every term exact (`notes/spec.md` §1–2). The two primitives were tested against brute force
before anything was measured with them (`code/t1_test.py`, `results/t1_test144.json`):

| test | cases | result |
|---|---|---|
| `chord_float` vs a direct dense measurement of `l n Q` (no shared algebra), horizontal + vertical lines | 600 | worst error **1.42e-05** = the sampler's own resolution (1.5e-05) |
| `minchord_box` vs a dense `(c_y, theta)` grid minimum over the box, on 12 tilt regimes incl. zero-width bins, bins straddling 0/45/90 deg, and `V < a`, `V = a`, `V > a` | 480 | worst **exceedance +5.6e-16** (float noise; the bound is never above the grid minimum), worst slack **5.7e-07** = the grid's resolution |

**Sampled confirmation over the whole population** (`code/confirm144.py`,
`results/confirm144.json`): for all **448** survivors, three lines each (the argmax line and two
drawn from the family), 10⁴ poses of the conditioned square in its box and 10⁴ of each of the five
pins in theirs —

* **drawn 80,640,000 → tested 80,640,000 → hits 0.** No pose anywhere has a chord below the exact
  `minchord`; the minimum slack over all positive bounds is 0.0, i.e. the bound is attained (it is a
  minimum, not an estimate).
* Lemma LINE-1, sampled: 10,000 random interior-disjoint square sets in `[0, s0]²` (42,094 squares
  in total), each tested on a random axis-parallel line — **0 hits**, worst excess −0.508.

Exact rational column coefficients, on Y0147's own pool (`code/coeffs144.py`): **13,216 placements
→ 3,383 non-zero coefficients, computed exactly in 0.67 s**, max |float − exact| = 6.05e-07 (the
cost of snapping `t` to the corpus's 1/2²⁴ grid). The exact right-hand side is `469271/250000` and
the exact violation `1017125138054443209/7920037658624000000 = 0.128424280527`.

`minchord(H, l)` versus the cheap bound `|l n K'(B)|`: on **448 of 448** nodes the row's best line
uses `minchord`, which is what the LP row should carry — on Y0147's line it is `1.000000` against
K′'s `0.831256`.

---

## 1. T2(a): Y0147, the PI's line

The PI's line is `y = s0 − 0.99 = 2.887084`. It is not in the generated family (the family's nearest
member is the container-parallel `grid h 6/8` at `y = 2.907813`), **but the two give the identical
four chords and the identical violation**, so the reading is robust to the exact height: any line in
`[2.884155, 2.940793]` — from pin P2's core edge to the top of H's chord — sees the same four
squares. The generator was run with the PI's line added explicitly.

| term | exact | float |
|---|---|---|
| `s0` | `969271/250000` | 3.877084 |
| pin P2 `(0.5, 3.3770839)`, chord | `1` | 1.000000 |
| pins P0, P1, P3, P4 | `0` each | — |
| `minchord(H, l)` over `B = [2.357813, 2.49757] x [2.637327, 2.777084] x [82.372, 90] deg` | `1` | 1.000000 |
| **`rhs(l)`** | `469271/250000` | **1.877084** |
| LP column `(3.377084, 3.185278)` at 0 deg, `y = 1` | `1` | 1.000000 |
| LP column `(1.575074, 3.327559)` at 84 deg, `y = 1` | `509674460661185/506882410151936` | 1.005508 |
| **`lhs(l)` on the stored dual support** | `1016556870813121/506882410151936` | **2.005508** |
| **violation** | `1017125138054443209/7920037658624000000` | **+0.128424** |

The four chords sum to **4.005508 > 3.877084 = s0**: the PI's "a line crossing opposing sides of
four squares forces side ≥ 4", made exact. Two of the four are the LP's own free columns, one is a
pin and one is the conditioned square — which is exactly the case A121's `st4` reading could not
express, because `st4` requires all four to be pins or conditioned squares.

`minchord(H, l) = 1` is not an accident of the mid-tilt: the bin `[82.372, 90]` reaches `theta = 90`,
where the conditioned square is axis-aligned and `V = 0.249757 < 1/2`, so its chord is exactly 1;
at the other end of the bin it is 1.008929, and the two `B`-branch values are 2.373 and `+inf`. The
minimum over the whole box is the `A`-branch at `t = 1`.

**Drawing:** `figs/k5_11_interior_Y0147_guardline.svg` (A142's format) — panel 1 the node at s0 with
the guard line drawn right across and the four chords as thick coloured segments labelled with their
lengths; panel 2 the chord ledger at true positions, showing the two overlaps
(`LP column / H` 0.093, `H / LP column` 0.064) and the cumulative bar against `s0` with the
+0.128424 excess hatched.

---

## 2. T2(b): the offline sweep over all 448 survivors

`code/offline144.py` → `results/offline144.jsonl`, `results/analyse144.json`. 448 nodes, ≤ 40 lines
each, **43.5 s total** — no LP.

* **86 of 448 nodes (19.2 %) have a guard line their stored dual support violates.**
  By class: k5_11 34/233, k5_16 52/215. By level: L1 83/355, L2 3/89, L3 0/4.
  Of the top 40 by A142 subtree cost, **15 violate**.
* **Violation depth** (max over the node's family):

  | depth | (0, 0.01] | (0.01, 0.05] | (0.05, 0.10] | (0.10, 0.15] | (0.15, 0.25] | > 0.25 |
  |---|---|---|---|---|---|---|
  | nodes | 9 | 19 | 19 | 35 | 3 | 1 |

  median **0.0951**, maximum **0.2660** (`k5_11_interior_Y0672_D00`, L2, rank 163).
* **How many lines fire per node:** 1 line 63, 2 lines 15, 3 lines 4, 4 lines 3, 5 lines 1.
* **Which line fires:** the container-parallel eighths carry most of it (`grid _ 4/8` 34,
  `grid _ 6/8` 29, `grid h 2/8` 6), the polygon-core extremes 9, a pin midline 5, a pin core edge 3;
  48 horizontal, 38 vertical.
* **The "four chords" signature.** Counting the LP columns with their dual weight (an unweighted
  count over-reads a fractional support), the number of chords of length ≥ 1 on a node's argmax
  line is 2 on 117 nodes, 3 on 307, and **≥ 4 on 23 — and all 23 of those violate**. So the PI's
  literal reading is realised on 23 of the 448, and the remaining 63 violations are the
  three-full-chords case where the fourth charge is fractional.

The row is therefore not a rarity and not universal: about one node in five is cut by it, and the
cut is deep enough (median 0.095 of a budget unit) to be worth an LP.

---

## 3. T2: the 20 in-vitro re-solves

`code/invitro144.py`, two arms per node with identical settings, identical warm start (30,000
merged rows) and identical **A135-certified exact cores on every box** — the only difference is the
guard columns (the ≤ 8 lines of the node's family with the largest offline violation).  A132's
in-vitro settings verbatim (240 s cap, `alternate`, `prune_cols=3`, `col_stop_cov=1.002`, no fine
row search).  Selection: Y0147 first, then the 13 deepest offline violations, then the 6
highest-ranked violators by A142 subtree cost.  **20 nodes, 8,428 s = 2.34 CPU-h, 0 errors**; the
exact-core pairwise-disjointness gate (A135 `cores_pairwise_disjoint`) passed on all 20.

| node | L | rank | offline viol | tau stored | tau base | tau guard | eta guard | conv b/g | kill b/g | z>0 | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `k5_11_interior_Y0672_D00` | 2 | 163 | +0.266005 | 5.000000 | 4.000000 | 4.000000 | -1.000000 | Y/Y | Y/Y | 0/8 | 37.3 |
| `k5_11_interior_Y0275` | 1 | 16 | +0.172462 | 5.000000 | 4.000000 | 4.000000 | -1.000000 | Y/n | Y/Y | 0/8 | 327.1 |
| `k5_11_interior_Y0241` | 1 | 14 | +0.167536 | 5.000000 | 4.000000 | 4.000000 | -1.000000 | Y/Y | Y/Y | 0/8 | 170.6 |
| `k5_11_interior_Y0376` | 1 | 269 | +0.158351 | 5.000000 | 5.000000 | 5.000000 | +0.000000 | n/n | n/n | 0/8 | 783.5 |
| `k5_16_interior_Y0260` | 1 | 23 | +0.149359 | 5.000000 | 3.000000 | 3.000000 | -2.000000 | Y/Y | Y/Y | 0/8 | 138.8 |
| `k5_11_interior_Y0306` | 1 | 41 | +0.147271 | 5.000000 | 4.000000 | 4.000000 | -1.000000 | n/n | Y/Y | 0/8 | 689.7 |
| `k5_16_interior_Y0309` | 1 | 166 | +0.141714 | 5.250000 | 4.500000 | 4.500000 | -0.500000 | n/n | Y/Y | 0/8 | 883.2 |
| `k5_16_interior_Y0458` | 1 | 87 | +0.139946 | 5.000000 | 5.000000 | 5.000000 | -0.000000 | n/n | n/n | 0/8 | 485.9 |
| `k5_16_interior_Y0286` | 1 | 130 | +0.139803 | 5.500000 | 4.000000 | 4.000000 | -1.000000 | Y/Y | Y/Y | 0/8 | 60.3 |
| `k5_16_interior_Y0101` | 1 | 420 | +0.139778 | 5.000000 | 5.000000 | 4.922603 | -0.077397 | n/n | n/Y | 1/8 | 581.0 |
| `k5_16_interior_Y0027` | 1 | 21 | +0.137586 | 5.000000 | 4.500000 | 4.500000 | -0.500000 | n/n | Y/Y | 0/8 | 634.4 |
| `k5_16_interior_Y0277` | 1 | 165 | +0.137351 | 5.000000 | 4.500000 | 4.500000 | -0.500000 | n/n | Y/Y | 0/8 | 546.8 |
| `k5_16_interior_Y0590` | 1 | 51 | +0.135381 | 5.000000 | 4.900000 | 4.850000 | -0.150000 | n/n | Y/Y | 0/8 | 676.6 |
| `k5_11_interior_Y0147` | 1 | 39 | +0.128424 | 5.000000 | 5.000000 | 4.877459 | -0.122541 | Y/n | n/Y | 1/8 | 493.6 |
| `k5_11_interior_Y0286` | 1 | 6 | +0.113332 | 5.500000 | 4.000000 | 4.000000 | -1.000000 | Y/Y | Y/Y | 0/8 | 34.5 |
| `k5_11_interior_Y0249` | 1 | 15 | +0.109803 | 5.000000 | 4.000000 | 4.000000 | -1.000000 | Y/Y | Y/Y | 0/8 | 54.7 |
| `k5_16_interior_Y0823` | 1 | 25 | +0.085400 | 5.000000 | 4.666667 | 4.666667 | -0.333333 | Y/Y | Y/Y | 0/8 | 120.9 |
| `k5_16_interior_Y0191` | 1 | 22 | +0.053183 | 5.000000 | 5.000000 | 5.000000 | +0.000000 | n/n | n/n | 0/8 | 675.6 |
| `k5_16_interior_Y0058` | 1 | 10 | +0.041162 | 5.000000 | 4.500000 | 4.500000 | -0.500000 | n/Y | Y/Y | 0/8 | 526.1 |
| `k5_16_interior_Y0626` | 1 | 11 | +0.041050 | 5.000000 | 4.500000 | 4.000000 | -1.000000 | n/Y | Y/Y | 0/8 | 507.7 |

### What the table says

* **The guard column is ACTIVE (`z > 0`) on exactly two of the twenty — and those two are exactly
  the two new kills.**  `k5_11_interior_Y0147`: `z = 1.0002` on `grid h 6/8` (rhs 1.877084),
  τ 5.000000 → **4.877459**.  `k5_16_interior_Y0101`: `z = 0.630697` on `grid v 6/8`
  (rhs 0.877084), τ 5.000000 → **4.922603**.  Everywhere else the LP set `z = 0`: on the fifteen
  nodes the exact cores already kill, the line is not needed, and on the three that die to neither
  arm the LP finds cheaper coverage than the line offers.  So the row's effect is not diffuse —
  it is exactly the "the LP is stuck AT the budget and the line is the missing charge" case.
* **A132's caveat, stated up front: the base arm already kills 15 of the 20.**  Those nodes are
  `Y0672_D00, Y0275, Y0241, Y0260, Y0306, Y0309, Y0286(k5_16), Y0027, Y0277, Y0590, Y0286(k5_11),
  Y0249, Y0823, Y0058, Y0626` — every one recorded ALIVE at τ = 5.000 (or 5.25/5.5) and every one
  now at 4.900 or below.  This is **A135's exact-core route**, the chore `docs/budget.md` §D.1
  already prices at ≈ 28 CPU-h for the whole ALIVE population, measured here on a 20-node sample.
  The sample is *selected for guard-line violation*, so 15/20 is emphatically **not** a population
  rate — a node whose support puts four unit chords on one line is a tight node by construction, and
  tight nodes are where a slightly larger core bites.  See §4 for the attribution control.
* **Convergence.**  9 of 20 converged in each arm; 8 converged kills in the base arm, 9 in the
  guard arm.  Neither of the two guard-only kills converged at the 240 s cap, so at stage 1 they are
  **"τ below budget, not yet converged"** — under A57's rule (`dead = converged and τ < budget`)
  that is not a kill claim, and `docs/budget.md` §D.2's caution applies verbatim: *no kill count
  from a re-solve counts before the 900 s re-check*.  §4 does that re-check.
* **Two Δτ that are NOT the guard line.**  `Y0626` (4.500 unconverged → 4.000 converged) and
  `Y0590` (4.900 → 4.850) both have `z = 0`; their Δτ is re-solve/convergence noise, not the row.
  Reading Δτ without reading `z` would have over-credited the lever on both.
* **Three nodes die to neither arm** — `Y0376` (offline violation +0.158, the 4th deepest),
  `Y0458` (+0.140) and `Y0191` (+0.053).  A deep offline violation is therefore **necessary but not
  sufficient**: it says the *stored* dual support is not a chord profile of any packing, not that
  the LP has no other optimum of the same value.  This is the honest limit of the offline number as
  a predictor.

---

## 4. Stage 2 — the 900 s re-check of the two guard-active nodes

`results/invitro144_stage2_s*.jsonl`. Both arms re-run at a 900 s cap (`docs/budget.md` §D.2's rule).

| node | arm | τ @ 240 s | τ @ 900 s | converged | minmass @ 900 s | z |
|---|---|---|---|---|---|---|
| `k5_11_interior_Y0147` | base | 5.000000 (conv) | **5.000000** | **yes** | 1.000000 | — |
| `k5_11_interior_Y0147` | guard | 4.877459 | **4.877459** | no | **0.982120** | 1.0002 on `h = 2.907813` |
| `k5_16_interior_Y0101` | base | 5.000000 | **5.000000** | no | — | — |
| `k5_16_interior_Y0101` | guard | 4.922603 | **4.916965** | no | — | 0.630697 on `v = 2.907813` |

**Y0147 is the clean case and it is stated exactly:** the control CONVERGES at τ = 5.000000 — the
node is genuinely alive without the row — and the guard arm sits at τ = 4.877459, *identical to nine
significant figures at 240 s and at 900 s*, with the separation oracle's worst placement at
`minmass = 0.982` (up from 0.899 at 240 s). So **η = −0.122541 is stable, but the guard arm has not
certified coverage at 900 s**: by A57's rule (`dead = converged and τ < budget`) this is
**"τ below budget, coverage not yet closed"**, not yet an LP kill, and certainly not a certificate.
An unconverged τ is a lower bound on the restricted optimum, so the honest claim is the direction
and the magnitude, not the verdict. Y0101 is weaker still — neither arm converges — but its guard
arm moves −0.083 and its `z` is positive.

**The frozen chain, on Y0147.** `certify.py` was run on the guard arm's node record. It does not
merely fail to verify — **it cannot express the certificate**: its own re-solve loop (`--loop_cols`)
rebuilds the measure from the atoms alone, returns to τ = 5.000000, and refuses with
*"certificate total >= budget: cannot certify"* (35.7 s). The guard column has no field to live in.
This is the sharpest argument for the `guardlines` field in `notes/spec.md` §3: it is needed at
EMISSION as well as at verification, which A135's `polycores` clause was not.

---

## 5. The audit of the injection (`code/audit144.py`, `results/audit144_*.json`)

`guardlp.py` reindexes HiGHS columns (guard columns first, orbit `k` at column `G + k`), so a silent
off-by-`G` would surface only as a wrong τ. Three checks on Y0147, none of which trusts the
wrapper's own bookkeeping:

| check | result |
|---|---|
| **A1 objective identity** — rebuild `obj` from HiGHS's primal solution as `Σ m_k w_k + Σ cost_l z_l`, reading `w` by ORBIT index | `4.877459491897572` vs `4.877459491897570`, **|diff| = 2.7e-15**. The split is **atom part 3.000000 + line part 1.877459** — the LP buys three units of atomic mass and one unit of line, at the line's discounted price. |
| **A2 row identity** — for 300 sampled rows, recompute the row activity from `(w, z)` and the geometry and compare with HiGHS's `row_value` | worst error **1.0e-12**, **0 mismatches** |
| **A3 dual feasibility of the guard rows** — the dual of the guard column IS the cut; check it on the final dual support | all 8 rows satisfied; **the binding one (`grid h 6/8`) has slack exactly 0.0** — the row is TIGHT, which is the direct evidence that this cut and not the re-solve is what moved τ. The same row was violated by **+0.128424** on the stored record. |


---

## 6. The attribution control: A57's DEPLOYED cores, same settings, same warm start

The base arm changes two things against the stored record — A135's exact cores AND a fresh re-solve
— and A132's rule is that a re-solve is not a reproduction. A third arm (`--arms stock`,
`caselp.Hyp` with the deployed `Box.core()` half-sides, everything else identical) was run on six of
the fifteen base-arm kills:

| node | τ stored | τ **stock** cores | τ **exact** cores (base arm) | τ guard arm |
|---|---|---|---|---|
| `k5_11_interior_Y0672_D00` | 5.000000 | **5.000000 (conv)** | **4.000000 (conv, KILL)** | 4.000000 |
| `k5_11_interior_Y0241` | 5.000000 | 5.000000 | **4.000000 (conv, KILL)** | 4.000000 |
| `k5_16_interior_Y0260` | 5.000000 | 5.000000 | **3.000000 (conv, KILL)** | 3.000000 |
| `k5_11_interior_Y0286` | 5.500000 | 5.333333 | **4.000000 (conv, KILL)** | 4.000000 |
| `k5_16_interior_Y0286` | 5.500000 | 5.000000 | **4.000000 (conv, KILL)** | 4.000000 |
| `k5_11_interior_Y0249` | 5.000000 | **5.000000 (conv)** | **4.000000 (conv, KILL)** | 4.000000 |

**Six of six: the re-solve alone kills nothing (τ ≥ 5.000 every time, budget 5), and A135's exact
cores kill all six.** So the base arm's 15/20 is attributable to the exact cores, not to the
re-solve — the same conclusion A132 drew from its own `axis` arm, now measured on this population.
`docs/budget.md` §D.1 already names "re-emit the ALIVE population with exact pin cores, 414 LP
re-solves at 240 s ≈ 28 CPU-h" as the next chore; this is a 20-node datum in its favour, with the
standing caveat that the twenty were selected for guard-line violation and so are tight by
construction.

---

## 7. Cost

| item | CPU-s |
|---|---|
| T1 generator self-tests + unit tests vs brute force | ≈ 45 |
| sampled confirmation over 448 nodes (80.6 M poses) | 25 |
| offline violation sweep, all 448 | 43.5 |
| exact rational coefficients + drawings + plumbing probe | ≈ 180 |
| **20 in-vitro nodes x 2 arms @ 240 s** | **8,428** |
| stage 2: 2 nodes x 2 arms @ 900 s | 3,021 |
| audit of the injection | ≈ 100 |
| attribution control: 6 stock arms @ 240 s | 1,336 |
| **total** | **≈ 13,180 s = 3.66 CPU-h** (cap 4) |

Two BLAS-pinned BelowNormal processes throughout; A57's `PAUSE` untouched; this attempt's own
sentinel `attempts/A144-guard-lines/PAUSE` watched by every driver.
