# A90 / T3 — empirical checks for Theorem NOCRIT (Opus chore)

All four tasks ran. One process, BLAS pinned to 1 thread, free commit > 12.8 GB throughout.
A87/A89 code imported, never modified. Writes confined to `attempts/A90-nocrit-blocked/`.

## 0. Headline numbers

| claim | number |
|---|---:|
| k0dir87 exit events re-run and reproduced **bitwise** (`\|Δσ_exit\| = 0`, same corner, same mode) | **520 / 520** |
| sliding blocker was **NON-DEEPEST** at the freed corner | **520 / 520 = 1.0000** |
| sliding blocker **RETREATABLE** (cardinal translation test) | **508 / 520 = 0.9769** |
| retreatable by some e ∈ K(Q) (cardinals or (1,1)) | **511 / 520 = 0.9827** |
| sliding blocker **NOT flush-locked** (Lemma LOCK (b) LP) | **515 / 520 = 0.9904** |
| **MENU-UNLOCKED** among the blockers MENU applies to | **100 / 108 = 0.926** |
| the 4 polished K0-BLOCKED non-FJ endpoints: RES(z) holds | **2 / 4** |
| … Gordan direction decreases some non-deepest intruder's depth | **4 / 4** |
| **Trump: critical, TL 2-crowd locked, not excluded by RETREAT** | confirmed |
| BLIND obstruction found (a K0-BLOCKED FJ point) | **0 / 167** |
| FJ points where Lemma BLIND's budget fails outright (\|U\| < D) | **70 / 167** |

**No obstruction to NOCRIT was found.** Lemma RETREAT is consistent with all 520 exit
events and with 2 of the 4 K0-BLOCKED non-FJ endpoints; the BLIND hunt found no
K0-BLOCKED FJ point.

Files: `code/{t3_90.py,sum1.py,task4_90.py}`,
`results/{t3_exits.jsonl,t3_endpoints.json,t3_trump.json,t4_blind.json}`,
`logs/{task1.log,sum1.txt,task2.log,task3.log,task4.log}`.

## 1. Reproduction of the k0dir87 seed stream (prerequisite)

`k0dir87.run()` uses `random.Random(20260903)`, but the campaign entry point is
`main('run')` = `selftest` → `canary` → `run`, and **`selftest` is what builds the
module-global corner-pair `_POOL`** (it calls `build_seed` with `random.Random(12345)`).
`run()`'s own rng therefore never pays for the pool. Replaying `Random(20260903)` without
first priming the pool the same way gives completely different seeds (checked: σ_exit off by
2e-1 … 8e-1, wrong corner freed). With `k0dir87.selftest()` run first, the replay is exact:

```
s0000 sigma_exit 4.706223098376 vs stored 4.706223098376  |d| 0.00e+00  freed ['TR'] OK
s0001 sigma_exit 4.275833540668 vs stored 4.275833540668  |d| 0.00e+00  freed ['TR'] OK
s0002 sigma_exit 4.400722812927 vs stored 4.400722812927  |d| 0.00e+00  freed ['TR'] OK
```

All **520** seeds were then re-run (free flow A only — flows B/C consume no randomness, so
the stream is unaffected), 177 s, **0 mismatches**. `t3_90.prime_pool()` documents this.
Independent cross-check of the geometry layer: my `corner_state` reproduces A87's corner
census exactly — 668 corners over the 167 FJ points split **{0: 14, 1: 633, 2: 21}**, matching
`k0blocked87`'s "633 one intruder, 21 two, 0 three"; and `all_gaps` agrees with
`fjpolish87.pair_gaps` to 2.2e-16.

## 2. Task 1 — the 520 exit events (`results/t3_exits.jsonl`, `logs/sum1.txt`)

Corners freed BR 232 / TL 190 / TR 68 / BL 30; mode `blocker_slid_away` 520/520; exactly one
sliding blocker per event.

At the last K0-BLOCKED point x_ok (the bisection endpoint before exit):

* **non-deepest: 520/520.** The sliding blocker was *never* the deepest intruder at its
  corner — this is the strongest single confirmation of the mechanism in the brief.
* **depth of the sliding blocker at x_ok:** min 9.23e-10, median 1.000e-09, max 4.26e-03.
  The median sits exactly on `TOL_BLOCK = 1e-9`, i.e. the bisection has driven the blocker's
  intrusion to the tolerance floor; the exit is the crossing of that floor, not a jump.
* **active contacts:** 398/520 blockers are **rattlers** (0 active contacts at 1e-6) — they
  have already slid clear. Contact-count histogram `{0: 398, 1: 106, 2: 4, 3: 7, 4: 2, 5: 3}`.
* **retreat cone:** (1,1) ∈ K(Q) for 520/520 (as it must be); exactly one cardinal in K for
  493, both cardinals for 27, **no cardinal for 0**.
* **RETREATABLE: 508/520 (0.9769).** For 507 of those 508 the free cluster is the singleton
  {Q} — the blocker retreats *alone*.
* **cluster sizes** (one entry per (blocker, cardinal e ∈ K)): 547 clusters, sizes
  `{1: 534, 3: 2, 4: 11}`; wall-anchored 12, intruder-anchored 5, **free 535**.
  Diagonal clusters C_(1,1): `{1: 506, 2: 4, 3: 2, 4: 6, 5: 2}`.

### Flush-locking (Lemma LOCK (b) LP / Lemma MENU)

* **LOCK (b): 515/520 NOT flush-locked.** The 398 rattlers have no rows at all (m = 0, so (b)
  is vacuously impossible). Of the 122 blockers with ≥ 1 contact, only **5** are locked
  (s0121, s0285, s0435, s0456, s0502).
* **MENU** applies (tilt > 0 **and** a wall contact) to 108 of the 122; **100 are
  MENU-UNLOCKED — no far-side contact available at all**, exactly as the brief predicts.
  8 are MENU-LOCKED (s0121, s0222, s0249, s0285, s0435, s0456, s0470, s0502); 14 have no wall
  contact so Lemma LOCK (b) was used directly.
* **LOCK and RETREATABLE never both hold** (0/520), and only 7 blockers are neither locked
  nor retreatable — the two criteria are close to complementary on this sample.

### The 12 cases NOT retreatable by the cardinal translation test

(`logs/sum1.txt`, full contact structure; tags s0083 s0121 s0243 s0259 s0285 s0302 s0435
s0451 s0456 s0470 s0502 s0518.)

Common structure — every one of the 12:
* is **non-deepest** (so Lemma RETREAT's hypothesis is met) and has **exactly one** cardinal
  in K; the cluster along it has size 3 or 4 and is **wall-anchored in all 12** (intruder-
  anchored as well in 5);
* has 3–5 active contacts, of which **exactly one is blocking** for that e — a single
  vertex-on-edge contact with a neighbour (normal · e ∈ [−1.00, −0.50]) — while the
  corner-side contacts are the flush kiss with the *kept* blocker at the same corner
  (n · e = +1) plus, in 6 cases, a far-wall contact. The cluster then grows along a chain of
  3 blocking edges to a square touching the far wall;
* 3 of the 12 (s0083, s0302, s0518) **are** retreatable diagonally: C_(1,1) = {Q, one
  neighbour} and is free. **9/520 blockers are retreatable by none of e_x, e_y, (1,1).**
* 5 of the 12 are flush-locked by LOCK (b), 8 are MENU-locked.

**What the flow actually did at those exits.** The exit motion (x_ok → x_bad, the two
bisection endpoints) is a **multi-square SQP motion in all 12** — 9 to 11 squares move,
**Q is the sole mover in 0/12** (and 0/520 overall); Q's own translation is 0.16–0.92 of the
largest displacement; Q's rotation exceeds its translation in 2 of the 12. In 10 of the 12 the
whole displacement is at machine precision (‖Δ‖∞ ≈ 5e-15 – 1e-14) with |Δσ| ≈ 1e-15 — the
bisection has converged onto the depth = 1e-9 threshold, so the "exit" there is the tolerance
crossing of a continuously vanishing depth, not a discrete event. The two genuine ones are
s0435 (‖Δ‖∞ 7.4e-7, Δσ +5.6e-7) and s0451 (‖Δ‖∞ 4.3e-6, Δσ +3.3e-6), both pure translation
of the whole packing (all |Δθ| = 0).

**Reading.** These 12 are not counterexamples to Lemma RETREAT as a mechanism; they are
cases where the *single-square rigid cardinal translation* test is too weak to certify what
the flow achieves by moving the cluster and the container together. If Lemma RETREAT is to be
used as stated, its retreat direction has to be allowed to be (i) diagonal (recovers 3 of 12)
and/or (ii) a coordinated cluster motion (recovers all 12). Over all 520, only 9 blockers
resist every one of e_x, e_y, (1,1).

## 3. Task 3 — Trump canary (`results/t3_trump.json`, `logs/task3.log`)

**Trump: critical, TL 2-crowd locked, not excluded by RETREAT.**

σ = 3.877083590023, n_block = [1, 1, 2, 1] (BL {0}, BR {2}, TL {4, 6}, TR {5}).
TL depths: **sq4 = 0.155475** (axis-aligned, tilt 0.0000°), **sq6 = 0.168321** (tilt 40.1819°)
— matching the brief's 0.1555 / 0.1683. **sq4 is the non-deepest one.**

* **FJ:** `fjpolish87.verdict` at tol 1e-6 gives **cone residual exactly 0.0**, m_active 42,
  support 32, rank 34, rank33 33, 0 rattlers → Trump **is** a Fritz-John point.
* **K(sq4)** = {e_y, (1,1)}; **e_x ∉ K** (argmin set A(sq4) = {(0, 0.844525), (0.844525,
  0.844525)}, so the point with p_x < p_y forces v_y > 0). **K(sq6)** = {e_x, (1,1)}, e_y ∉ K
  (A(sq6) = {(0.831679, 0.645217)}, p_x > p_y).
* **sq4 active contacts** (n = force on sq4): pair 6 n = (−0.763999, −0.645217) at
  (1.000000, 3.032558); pair 7 n = (−0.645217, +0.763999) at (1.000000, 2.032558); wall x=0
  twice, n = (+1, 0) at (0, 2.032558) and (0, 3.032558). All gaps ≤ 6.1e-16.
* **sq6 active contacts:** pair 4 n = (+0.763999, +0.645217) at (1.000000, 3.032558);
  pair 9 (flush kiss, 2 admissible axes) n = (−0.645217, +0.763999) at (2.240895, 3.113084)
  and (1.476896, 2.467867); wall y=s n = (0, −1) at (1.595678, 3.877084). All gaps ≤ 4.4e-16.
* **Clusters — every one wall-anchored, as expected (Trump is rigid):**
  C_e_y(sq4) size 7 = {0,1,2,3,4,7,8}, wall-anchored via 0/1/2 on y=0;
  C_(1,1)(sq4) size 8 = {2,4,5,6,7,8,9,10}, wall-anchored (x=s, y=0) **and**
  intruder-anchored (sq2, BR, depth 1.0);
  C_e_x(sq6) = C_(1,1)(sq6) size 4 = {5,6,9,10}, wall-anchored via 5/10 on x=s.
* **RETREATABLE(sq4) = False, RETREATABLE(sq6) = False.**
  **RES(Trump) = True** (1 non-deepest intruder, 0 retreatable).
* **Locks.** sq4 is axis-aligned so Lemma MENU does not apply; Lemma LOCK (b) gives a
  **self-stress** (μ mass 3.153) → LOCKED. sq6 (tilt 40.18°, touching y=s) is
  **MENU-LOCKED**: rotating clockwise about its wall vertex O = (1.595678, 3.877084) closes
  its far-side contact with sq4 at rate −0.2609; LOCK (b) also gives a self-stress
  (μ mass 2.409) → LOCKED.

So Lemma RETREAT does **not** exclude Trump, and the boundary case the brief demands is
respected: Trump has only three slot corners (it is K0-FREE, not K0-BLOCKED), so it is
"all four corners blocked" — not "a doubly-intruded corner" — that any NOCRIT proof must use.

## 4. Task 2 — the 4 polished K0-BLOCKED non-FJ endpoints (`results/t3_endpoints.json`)

All four are exactly K0-BLOCKED ([2,2,2,2] certified) with exactly one non-deepest intruder
per corner (4 per point). The Gordan direction y is `fjpolish87.cone_nnls`'s NNLS residual;
its certificate is verified here: min over active rows of ∇g·y ≥ −8.4e-16 (all rows
non-decreasing) and y_s < 0 (σ strictly decreasing).

| tag | σ | cone residual | m_active | RES(z) | non-deepest / retreatable | y_s | y decreases a non-deepest depth |
|---|---:|---:|---:|:--:|---:|---:|:--:|
| s0380 | 4.000000118 | 2.095e-04 | 29 | **True** | 4 / 0 | −2e-8 | yes (3 of 4) |
| s0076 | 4.000004058 | 1.208e-02 | 20 | False | 4 / 2 | −1.2e-4 | yes (2 of 4) |
| s0380 | 4.000007451 | 4.293e-02 | 18 | **True** | 4 / 0 | −1.8e-3 | yes (**4 of 4**) |
| s0259 | 4.000011860 | 7.466e-02 | 18 | False | 4 / 2 | −5.6e-3 | yes (3 of 4) |

* **RES(z) holds at 2 of the 4** (both s0380 points); at s0076 and s0259 two of the four
  non-deepest intruders are retreatable (the ones that are: singleton clusters, no anchor —
  s0076 sq1 and sq7, s0259 sq1 and sq2).
* **The certified Gordan direction moves the shallower intruder in all 4 cases.** Example
  rates dd/dt of the non-deepest intruders' depths along y: s0380 (2nd) BL −2.49e-2,
  BR −2.54e-4, TL −1.57e-3, TR −2.08e-3 — all four corners shed their second intruder at
  once. s0380 (1st): BR −1.11e-5, TL −4.90e-5, TR −1.09e-5 (BL exactly 0).
* **The interesting cross-tab:** at both s0380 points *every* non-deepest intruder is
  NOT retreatable by translation, yet the certified descent direction still decreases every
  one of their depths. So Gordan achieves by a coordinated 34-coordinate motion precisely
  what a single-square rigid translation cannot — the same gap that the 12 task-1 cases show.

## 5. Task 4 — the BLIND obstruction hunt (`results/t4_blind.json`, `logs/task4.log`)

167 certified k0 FJ points (`cp87_fj_polished.jsonl`, `survivor_tight`, 34 exact strings),
1924 s. **Data gap:** the 17 FJ endpoints of `k0dir87.polish.jsonl` have **`z_polished = null`**
— `k0dir87.py:902` stores z only when the point came out exactly K0-BLOCKED, and none of the
17 did. Their configurations are not on disk, so they could not be included; recovering them
needs a full replay of the 520-seed run + deep pass + polish (~50 min), which did not fit the
budget.

**Loadable sets.** Per-row LP `max λ_k s.t. Aₙᵀλ = e_s, λ ≥ 0` (feasible at all 167 points).
Median 23 active rows, 20 loadable; all rows loadable at 35/167 points. Loaded-square counts
`{4: 35, 5: 25, 6: 6, 7: 28, 8: 42, 9: 15, 10: 11, 11: 5}` → **unloadable-square counts |U|**
`{0: 5, 1: 11, 2: 15, 3: 42, 4: 28, 5: 6, 6: 25, 7: 35}`.

Note (this is why the certificate check is free): a loadable row makes *both* its squares
loadable, so every row touching an unloadable square carries λ = 0 in every certificate.
Moving only unloadable squares therefore leaves every loaded row's value and gradient
untouched, and the original λ remains an FJ certificate automatically. The binding constraint
is purely geometric.

**Result: 0 successes / 167.**

* **The counting obstruction is decisive on its own.** Deficient corners
  D = #{corners with n_block < 2}: `{3: 21, 4: 146}`. **70 of 167 points have |U| < D** — not
  enough unloadable squares to fill the deficient corners even in principle. Shortfall
  D − |U| histogram: `{−4: 6, −3: 31, −2: 25, −1: 12, 0: 23, 1: 39, 2: 15, 3: 11, 4: 5}`.
* For the 97 countable points (|U| ≥ D) the penalty search (25 random restarts, Powell, other
  squares and the tight bbox frozen) **never produced a valid packing with any corner's
  occupancy increased**: best min_n_block `{0: 1, 1: 96}`, i.e. unchanged from the original.
* Across all 162 points where a repositioning was attempted, only **39** best configurations
  stayed valid packings (pairwise disjoint, contained, bbox not grown) — and in every one of
  those 39 the total corner occupancy Σ n_block was **identical to the original** (the
  optimiser fell back to the original poses). The other 123 "best" configurations reach
  min_n_block ≥ 2 at 2 or 3 corners only by **violating feasibility** (median residual overlap
  2.1e-2, container violation 6.3e-1, bbox grown in all 123) — they are not packings and are
  reported as failures.
* **Closest approaches** are therefore all infeasible: e.g. o043 [1,1,1,1] → [1,2,2,2] and
  o051/o052/o204 → three corners at ≥ 2, each with ≈ 4.7e-2 overlap and σ blown up from
  4.000 to 4.72–4.91. No `blind_obstruction_<tag>.json` was written.
* **Why the last corner fails — the room.** Free area σ² − 11: min 4.19, median 5.00,
  max 14.00 at bbox side σ ∈ [3.897, 5.000]. There is nominally area for extra squares, but
  the unloadable squares are unit squares that must intrude a corner slot *without* growing
  the bbox and *without* overlapping the frozen loaded squares; at σ ≈ 4.00 the loaded
  skeleton already fixes the four corner slots (each with exactly one intruder), and the free
  area is distributed as interior pockets that no unit square can reach into a corner from.

**Caveat.** This is a heuristic search, not a proof: the penalty optimisation is weak (it
teleports squares into corners and often cannot repair the resulting overlap), so the
"0 successes" is only as strong as the search. The **counting** half — 70/167 points where
Lemma BLIND's budget is short outright — is a hard combinatorial fact about the certified
loadable sets and does not depend on the search.

## 6. Conventions used (so the theory lead can audit them)

* **Corner frames are anchored at the TIGHT BOUNDING BOX**, matching `k0dir87.k0_state` and
  `k0dir87.exact_blocked_test`; wall contacts use the container [0, s]² with s = z[33]
  (`fjpolish87.canonical` puts the bbox min at PAD = 1e-9 in both axes, so the bottom/left
  walls always register, and the far wall registers in the binding direction only).
* **Depth** d_c(Q) = max(0, 1 − min_{p ∈ Q} max(p_x, p_y)); minimised over the quadrilateral
  by evaluating the 4 vertices plus each edge's intersection with {p_x = p_y}; A(Q) = points
  within 1e-11 of the minimum. Intruder iff d_c > 1e-9 (a tangency is not a block).
* **K(Q):** e_x ∈ K iff every p* ∈ A(Q) has p*_x ≥ p*_y; e_y ∈ K iff every p*_x ≤ p*_y;
  (1,1) ∈ K always. The container/anchors are held **fixed** when the retreat derivative is
  taken.
* **Contacts:** SAT gap ≤ 1e-6; normal n = force direction on Q along the selected separating
  axis; flush = 2 contact points on one axis, vertex = 1, **kiss** = ≥ 2 admissible axes
  (within 1e-6 of the max). **For a kiss the contact counts as blocking only if EVERY
  admissible axis gives n·e < 0** — this is the conservative choice the brief specifies; it
  matters, since kisses are common here (the flush contact between the two blockers at a
  corner is realised as a 2-axis kiss in most of the 12 task-1 cases, and it is always
  corner-side, n·e = +1).
* **Lemma LOCK (b):** LP `max Σμ s.t. Σμ_k n_k = 0, ±Σμ_k τ_k ≥ 0, 0 ≤ μ ≤ 1`, τ about Q's
  centre; LOCKED = a self-stress exists, or a couple in the away-from-flush sense.
* **Lemma MENU** is implemented as the general rate test behind its table: rotate Q about the
  wall-contact vertex O in the flush-ward sense; a contact is **far-side** iff it closes
  (n · (ω × (x − O)) < 0). MENU-LOCKED = every admissible pivot has a closing contact.

## 7. What this says for T1

1. The mechanism in the brief is confirmed at full strength on the exit data: the square that
   frees a corner is **always** the shallower intruder (520/520), it is **almost always**
   unlocked (515/520 by LOCK (b), 100/108 MENU-unlocked) and **almost always** free to retreat
   (508/520 by cardinal translation, 511/520 including the diagonal).
2. The residue is **not** a locking failure — it is a **motion-class** failure. In the 12
   task-1 exceptions and at both s0380 endpoints, the depth of a non-deepest intruder is driven
   down by a *coordinated* motion (the flow's SQP step, or the certified Gordan direction)
   although no single-square rigid cardinal translation certifies it. A NOCRIT proof that
   routes through "retreat by translation" will have to either widen the retreat direction to
   the cluster (all 12 recovered) or argue at the level of the FJ certificate directly.
3. **RES(z) is not implied by K0-BLOCKED-and-not-FJ**: it fails at 2 of the 4 K0-BLOCKED
   endpoints. RES is therefore a genuine extra hypothesis, not a consequence.
4. Trump behaves exactly as the boundary case must: critical, its TL 2-crowd fully locked,
   RES true, not excluded by RETREAT — the "all four corners blocked" hypothesis is what
   separates it.
5. Lemma BLIND has a **counting budget** that the data says is usually short: at 70 of the 167
   certified FJ points there are fewer unloadable squares than deficient corners. That is a
   promising shape for the pigeonhole argument T1 is aiming at — the loaded skeleton at a k0 FJ
   point already consumes 4–11 squares (median 8), leaving too few blind squares to double up
   all four corners.
