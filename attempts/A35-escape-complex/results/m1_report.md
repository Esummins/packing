# A35 / M1 — stratum enumerator at Trump's jam

Code: `code/strata_lib.py` (shared by M2/M3/M4), `code/m1_enum.py`.
Data: `results/m1_strata.json` (0.98 MB). Runtime 18 s, single process.
Inputs: `attempts/A22-local-rigidity/results/krawczyk_cert.json` (z-hat as 34 exact
rationals, geometric rows = constraints 0..37), row language + interval jets reused
from `attempts/A30-t3-pilot/t3lib.py` via `sys.path` (the 2 `dist` rows are not in
t3lib's language and get a 4-variable jet built on `t3lib.Jet`).

**Rigour tags used throughout.**

| tag | meaning |
|---|---|
| `[IV]` | mpmath.iv at dps 60 over the degenerate point box at z-hat (widths ≤ 1.2e-17 on Jacobian entries, ≤ 6.7e-60 on row values). Rigorous. |
| `[RFP]` | rigorous float64: `‖I − Y·A‖_∞ < 1` with an explicit Rump rounding bound plus the `[IV]` entry radii. Certifies **nonsingularity** only. Rigorous modulo IEEE-754. |
| `[EXACT]` | exact rational / exact combinatorics. |
| `[NUM]` | float64 SVD with the spectral gap recorded. **Not rigorous.** All rank-*deficiency* claims are of this kind — a rank drop is never interval-certifiable at a rational approximation of an algebraic point. |

Consistency check performed: every a22lib point gradient (mp, dps 60) lies inside
the corresponding t3lib interval jet — 0 violations out of 38×34.

---

## 1. Certified constants at z-hat

### 1a. rank and self-stress

* **rank(A) = 34.** `[RFP]` A nonsingular 34×34 minor is exhibited with
  `‖I − Y·A_S‖_∞ = 2.40e-13 < 1`; `rank ≤ 34` is trivial (34 columns).
  Fully rigorous. Smallest singular value of the full 38×34 A: 0.1266
  (no near-degeneracy).
* **self-stress dim = 4.** `[RFP+EXACT]` `dim ker(Aᵀ) = 38 − rank(A) = 4`.
* **self-stress support = 20 of 38 rows** — matches theory.md exactly.
  Support rows: `0,1,2,3,7,8,9,10,20,21,22,23,26,27,28,29,30,31,33,35`.
  Method: row *k* lies in the support of some self-stress **iff** rank(A₋ₖ) = 34;
  all 20 are `[RFP]`-certified individually. The 18 non-support rows are `[NUM]`
  (rank(A₋ₖ) = 33 is a deficiency claim). Note the identity
  **support size = number of "empty" k=1 strata = 20**, which is asserted in the
  self-check.

### 1b. no nonnegative self-stress — strict Farkas witness

Rational `y` (denominator 1e9, stored in the JSON) with

> **min over all 38 rows of the `[IV]`-verified lower bound of `∇g_k · y` = 0.22970**

Fully rigorous. This simultaneously certifies (Gordan):

* no nonzero nonnegative self-stress on the 38 rows → **the λ₀ = 0 FJ branch is
  empty at z-hat** (theory.md G2 item, discharged);
* `cone{∇g_k}` is **pointed**;
* the multiplier polytope `{λ ≥ 0 : Aᵀλ = e_s}` is **bounded** (needed for Task 3).

### 1c. λ* with uniform floor

Chebyshev LP `max t s.t. λ ≥ t, Aᵀλ = e_s`, then the 4 rows outside A22's
invertible subsystem S frozen at rationalised LP values and the 34 S-rows re-solved
at mpmath dps 90, rationalised at denominator 1e45.

| quantity | value | method |
|---|---|---|
| `min_k λ*_k` (exact rational) | **0.047644047…** (argmin rows 8, 9) | `[EXACT]` |
| `Σ λ*` | 4.353502 | `[EXACT]` |
| `‖Aᵀλ* − e_s‖₁` at z-hat | **9.68e-45** (target ≤ 1e-25) | `[IV]` dps 60 |
| all λ*_k > 0 | yes | `[EXACT]` |

theory.md's recon values (floor 0.047644, sum 4.3535) are reproduced to all printed
digits and are now **promoted from float recon to certified**.

---

## 2. Codim-graded classification

dof = 34 − rank(A_M). `[NUM]` for the dof, with the per-stratum spectral gap stored;
**every dof = 0 ("empty") verdict at k ≤ 3 is additionally `[RFP]`-certified**
(20/20, 144/144, 448/448 — 334 distinct nonsingular bases, all certified, worst Rump
bound 3.37e-13).

| k | n | empty | dof 1 movable | dof 1 wedged | dof 2 | dof 3 | dof 4 | dof 5 | dof 6+ |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 38 (all) | 20 | 18 | 0 | – | – | – | – | – |
| 2 | 703 (all) | 144 | 388 | 18 | 153 | – | – | – | – |
| 3 | 8436 (all) | 448 | 2976 | 240 | 3956 | 816 | – | – | – |
| 4 | 2000 of 73 815 | 10 | 250 | 30 | 977 | 650 | 83 | – | – |
| 5 | 2000 of 501 942 | 0 | 40 | 4 | 549 | 936 | 432 | 39 | – |
| 6 | 2000 of 2.76e6 | 0 | 0 | 0 | 127 | 669 | 929 | 261 | 14 |
| 7 | 2000 of 1.26e7 | 0 | 0 | 0 | 0 | 198 | 896 | 744 | 162 |
| 8 | 2000 of 4.89e7 | 0 | 0 | 0 | 0 | 0 | 342 | 955 | 703 |
| 9 | 2000 of 1.63e8 | 0 | 0 | 0 | 0 | 0 | 0 | 459 | 1541 |
| 10 | 2000 of 4.73e8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2000 |

**Exact agreement with theory.md's recon at k = 1, 2, 3**: k=1 → 18 mechanisms /
20 empty; k=2 → 153/406/144 (the 406 one-dof splits 388 movable + 18 wedged);
k=3 → 816/3956/3216/448 (the 3216 one-dof splits 2976 + 240 wedged).

One-sidedness (dof-1 strata):

* **k = 1: all 18 mechanisms are movable, none wedged.** Wedging first appears at
  k = 2 (18 of 406).
* first-order ascent rate `e_s·v` for the movable sign, `‖v‖₂ = 1`:
  k=1 range **[0.04276, 0.12145]**; k=2 range [0.04276, 0.15584].
  The slowest escape at k=1 is row 32 (`E9c3-6e0`), the fastest row 25 (`W6c2[y=s]`).
* consistency: the identity `e_s·v = Σ_{b∈B} λ*_b (∇g_b·v)` holds with residual
  ≤ 7.1e-16 (k=1) and ≤ 2.5e-15 (k=2) — an independent check on λ*.

Kernel bases (float, flagged `[NUM]`) are stored for all k ≤ 2 strata in the JSON.

---

## 3. K = 6 cone truncation — **confirmed, and sharpened a lot**

The multiplier polytope `P = {λ ≥ 0 : Aᵀλ = e_s}` is bounded (1b) and its affine hull
is `λ* + ker(Aᵀ)`, dim 4. Its cap in `u ∈ R⁴` was vertex-enumerated **three
independent ways** — all C(38,4) = 73 815 tight 4-subsets, qhull
`HalfspaceIntersection` (u = 0 is strictly interior since λ* > 0), and 4000
random-objective LPs. **All three return the same 16 vertices** (cross-check stored).

* **min support = 32** ⟹ **max break-set preserving the cone = 6**. theory.md's
  K = 6 is confirmed. Vertex support sizes: 32 (×4), 33 (×8), 34 (×4).
* the 4 minimum-support vertices were re-solved at mpmath dps 60 from their
  32-row systems: residual ≤ 1.4e-61, min multiplier 0.0103 / 0.0221 — genuine
  strictly-positive 32-row multiplier vectors.
* **all 16 maximal surviving break-sets are listed** (< 200), e.g.
  `{1,8,9,21,22,26}`, `{2,10,23,29}`. They have the product structure
  `{1|2} × {8,9 | 10} × {21,22 | 23} × {26|29}`.

**The sharpening.** Every surviving break-set is drawn from just **10 rows**:
`{1, 2, 8, 9, 10, 21, 22, 23, 26, 29}`. Consequently:

* **28 of the 38 rows are singleton cone-killers** — breaking any *one* of them
  already puts `e_s` outside the retained cone. (Minimal excludable sets: 28
  singletons plus exactly 6 pairs `{1,2} {8,10} {9,10} {21,23} {22,23} {26,29}`.)
* exact excludable fractions (`[EXACT]` combinatorics on the vertex set):

| k | 1 | 2 | 3 | 4 | 5 | 6 | ≥7 |
|---|---|---|---|---|---|---|---|
| surviving break sets | 10 | 39 | 74 | 69 | 28 | 4 | **0** |
| fraction excludable | 0.737 | 0.945 | 0.991 | 0.9991 | 0.99994 | 0.9999986 | **1.000** |

So the truncation is not merely "|B| ≥ 7 dies": across **all 2³⁸ break sets only
223 are cone-alive at all**, and they are listed explicitly in the JSON.

Cross-check (b): 20 random |B| = 7 sets, each given a rational Farkas direction
(denominator 1e9) with `y[33] = −1` and every `∇g_m · y` verified `> 0` in
mpmath.iv at dps 60 — **20/20 certified**, `[IV]`, fully rigorous per set.

---

## 4. Candidate new contacts, with an honest travel bound

**Lipschitz constants, derived (this is the "incl. theta" the brief asked for).**
With `q_i = c_i + R(θ_i)h`, `|h| = √2/2 = 1/√2`, and `‖dz‖_∞ ≤ R`:

* corner motion `|dq_i| ≤ |dc_i|₂ + |dθ_i|·|h| ≤ √2 R + R/√2 = (3/√2) R ≈ **2.12132 R**`;
* a square moves at most `(3/√2) R` in **Hausdorff** distance (convex hull of its corners);
* Euclidean separation `dist(K_i,K_j)` is 1-Lipschitz in each body's Hausdorff
  perturbation ⟹ `L_pair = 2·(3/√2) = 3√2 ≈ **4.24264**`. No rotating-axis term is
  needed because the *distance* is used, not a fixed-axis projection; the reported
  SAT max-over-edge-normals gap is a lower bound on `dist` and vanishes exactly at
  contact, so using it in the screen is conservative;
* walls: `x=0 / y=0` → `L = 3/√2 ≈ 2.12132`; `x=s / y=s` also carry `ds` →
  `L = 1 + 3/√2 ≈ **3.12132**`.

The brief's suggested `2√2 R = 2.82843 R` sits *between* the per-square constant and
the pair constant; the larger (conservative) constants above are used.

Gaps at z-hat, `[IV]` dps 60 — theory.md's recon list reproduced exactly:

| pair | (6,7) | (8,9) | (3,4) | (7,10) | (2,10) | (5,10) | (1,7) | rest |
|---|---|---|---|---|---|---|---|---|
| SAT gap | 0.024875 | 0.024875 | 0.032558 | 0.118783 | 0.231867 | 0.236001 | 0.255005 | ≥ 0.636 |

Nearest new **wall** contact: square 9 corner 2 vs `y=s`, gap **0.548642** (recon
0.54864 ✓). 156 non-contact corner-wall combos in total.

Candidate table. Two independent *necessary* conditions are computed — the Lipschitz
screen and a full interval evaluation of the gap over `box(z-hat, R)` — so the sound
candidate set is their **intersection**:

| R | candidate pairs | candidate corner-wall combos |
|---|---|---|
| 0.005 | **none** | none |
| 0.01 | (6,7), (8,9), (3,4) | none |
| 0.02 | (6,7), (8,9), (3,4) | none |
| 0.05 | (6,7), (8,9), (3,4), (7,10) | none |
| 0.1 | (6,7), (8,9), (3,4), (7,10), (2,10), (5,10), (1,7) | none |

At R ≤ 0.1 **no new corner-wall contact is possible at all** (all 156 combos ≥ 0.5486
> 3.12132 × 0.1). theory.md's claim "at travel ≤ 0.05 the only candidates are (6,7),
(8,9), (3,4), (7,10) plus nothing else below gap 0.23" is confirmed exactly.

(The interval scan over the full box is dependency-pessimistic and gives a strictly
larger set at large R — e.g. 17 pairs at R = 0.1 vs 7 from Lipschitz — while at
R = 0.005 it fails to exclude (6,7)/(8,9) that the Lipschitz screen does. Both are
sound, so intersecting them is legitimate and is what the table reports.)

---

## 5. Load-path cuts with force-balance refinement (T1-b)

**Graphs.** x-graph: 11 square nodes + `x=0`, `x=s`; all 13 pair edges plus the
x-wall edges; y-wall edges removed (their normals have no x-component). Analogously
for y. An edge survives while **any** of its rows is retained, so a cut must remove
**all** rows of every cut edge. 24 contact edges total (14 with 2 rows, 10 with 1),
enumerated and stored.

**Force-balance rule implemented (a strict generalisation of theory.md's corner-square
rule).** For square *i* and each coordinate `c ∈ {cx_i, cy_i, θ_i}`, FJ stationarity
gives `Σ_k λ_k A[k,c] = 0` with `λ ≥ 0` — note `∇s = e_s` touches only `z[33]`, so this
holds for **both** the λ₀ > 0 and λ₀ = 0 branches. If all nonzero coefficients in that
column share a sign, those λ_k are 0 and the rows are load-dead. Iterated to a fixed
point. The corner-square rule of T1-b is the special case "two orthogonal wall
normals". Well-conditioned: the smallest |coefficient| that ever fires is **0.0594**,
and the smallest nonzero entry anywhere in A is 0.0594 — no tolerance ambiguity.

At z-hat with all 38 rows retained the rule **never fires** (the jam is fully loaded),
so the pruned and unpruned base graphs coincide.

**Min row-cuts (max-flow and an independent binary MILP agree; each cut verified to
actually disconnect):**

| | theory.md recon | this measurement | cut rows |
|---|---|---|---|
| x-axis | 5 | **3** | `{11, 19, 34}` = `E2c3-8e0`, `E5c0-9e1`, `W10c1[x=s]` |
| y-axis | 3 (`{22,23,25}`) | **2** | `{19, 25}` = `E5c0-9e1`, `W6c2[y=s]` |
| both axes jointly | 8 | **4** | `{11, 19, 25, 34}` |

**Surprise vs theory.md.** `{22,23,25}` *is* a valid y-cut (verified) but it is not
minimal: it isolates the `y=s` wall node directly, whereas cutting `{19,25}` leaves
square 5 attached to `y=s` as a dead-end leaf. Same for x. The recon numbers appear
to have cut wall nodes rather than searching all cuts. Cuts are 40–50 % cheaper than
theory.md records.

**Per-k load-path statistics** (exhaustive k ≤ 2, 2000 samples k ≥ 3):

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| frac. with x-path (pruned) | 1.000 | .970 | .898 | .807 | .686 | .533 | .404 | .325 | .213 | .143 | .096 | .055 |
| frac. dead by load-path (pruned) | .000 | .030 | .102 | .193 | .314 | .467 | .596 | .675 | .787 | .857 | .904 | .945 |
| frac. dead, **raw** L6 graph (no force balance) | .000 | .000 | .000 | .000 | .000 | .000 | .001 | .001 | .003 | .004 | .011 | .024 |
| frac. total multiplier collapse | .000 | .030 | .102 | .193 | .314 | .467 | .596 | .675 | .787 | .857 | .904 | .945 |

Two findings here:

1. **T1-b as literally written (raw wall-to-wall connectivity) is almost useless** at
   these codimensions — it kills 0.0 % of strata up to k = 6 and only 2.4 % at k = 12.
2. **All of the power is in the force-balance refinement, and it always goes all the
   way**: the "dead by load-path" and "total multiplier collapse" columns are
   *identical* at every k. Whenever the sign rule bites, it cascades until **no**
   retained row can carry a multiplier at all. That is strictly stronger than a graph
   cut: such strata are FJ-free outright, λ₀ = 0 branch included, with no graph
   argument needed. Example: `B = {19,25}` — square 5 loses its only pair contact,
   becomes a two-orthogonal-wall corner square, and the collapse propagates through
   squares 6, 9, 10, 4, 7, 8, 1, 2 in 18 firings, killing all 36 remaining rows.

**Not proved / caveats for T1-b** (also in the JSON):

* the sign test is evaluated at z-hat gradients; the min |coefficient| per firing is
  recorded so a neighbourhood statement is available, but no interval extension over
  a region is done here — that is M3's job;
* no torque/magnitude propagation beyond the single-coordinate sign rule;
* square-square edges are kept in **both** axis graphs regardless of normal direction
  (theory.md only removes orthogonal *wall* edges) — conservative, so the cuts are
  valid but possibly not minimal;
* **gained** contacts are not in the graph and are not in the force balance; a stratum
  can reconnect a cut axis or re-feed a killed square by acquiring a new contact
  (Task 4 bounds which, per travel radius).

---

## 6. Synthesis — the complete survivor list

Applying the four kill-tests in order — (1) EMPTY, `[RFP]`; (2) CONE-DEAD (T1-a),
`[EXACT]` from the vertex enumeration; (3) TOTAL COLLAPSE (T1-b refined);
(4) LOAD-PATH (T1-b as written):

| k | n | empty | cone-dead | collapse | load-path | **survives all** |
|---|---|---|---|---|---|---|
| 1 | 38 (all) | 20 | 18 | 0 | 0 | **0** |
| 2 | 703 (all) | 144 | 557 | 0 | 0 | **2** |
| 3 | 8436 (all) | 448 | 7974 | 0 | 0 | **14** |
| 4 | 4000 sampled | 32 | 3966 | 0 | 0 | 2 |
| 5–8 | 4000 sampled each | ~0 | ~4000 | 0 | 0 | ≤ 1 |

Because only the 223 subsets of the 16 maximal Z(v) can be cone-alive, this can be
made **exhaustive over all 2³⁸ break sets in finite time**, and was:

> **223 cone-alive break sets. 143 of them are EMPTY strata (all 143 `[RFP]`-certified).
> 0 die by collapse or load-path (those tests are subsumed here). Exactly **81** break
> sets survive every test.**

All 81 are listed in `results/m1_strata.json`
(`synthesis.global_exhaustive.survivors`). They have |B| ∈ {2,…,6}, are drawn entirely
from the 10-row family `{1,2,8,9,10,21,22,23,26,29}`, and the smallest two are
`{8,9}` = `{W2c1[y=0], W2c1[x=s]}` (square 2's shared corner peeling off the
bottom-right container corner) and `{21,22}` = `{W5c2[x=s], W5c2[y=s]}` (square 5's
shared corner peeling off the top-right corner). Every survivor contains one of these
two seeds or its variants — the escape complex, at the linearization, is exactly the
two "corner-square release" families plus their decorations.

**Note for the cost estimate**: the per-stratum work at the jam is 81 certificates,
not `Σ_k C(38,k)`. That is the M1 headline.

---

## 7. Surprises vs theory.md, and the gap/caveat list

**Reproduced exactly** (recon → certified): rank 34, self-stress dim 4 and support 20,
no nonneg self-stress, λ* floor 0.047644 and sum 4.3535, min support 32 / K = 6,
k=1/2/3 dof tables (18/20; 153/406/144; 816/3956/3216/448), all seven nearest
non-contact pair gaps, nearest new wall contact 0.54864.

**Surprises.**

1. **The cut numbers in theory.md are not minimal.** x = 3 not 5, y = 2 not 3, joint
   = 4 not 8. `{22,23,25}` is valid but suboptimal.
2. **T1-a is far stronger than "K = 6"** at the linearization: 28 of 38 rows are
   singleton cone-killers, only 223 break sets out of 2³⁸ are cone-alive at all, and
   the complete post-all-tests survivor list has **81** elements. The "C(38,7) ≈ 1.3e7
   dead families need a grouped certificate" worry in T1-a caveat (iii) evaporates —
   the *survivors* are the short list, not the dead ones.
3. **T1-b as written contributes essentially nothing** (0 % of strata killed up to
   k = 6), but its force-balance refinement is very strong and always terminal (total
   multiplier collapse rather than a graph cut). The load-path graph is the wrong
   abstraction; the coordinate-sign cascade is the right one.
4. **k = 1 is completely disposed of** with no new machinery: 20 empty + 18 cone-dead
   = 38. Also, all 18 k=1 mechanism rows are exactly the 18 non-support rows of the
   self-stress space, and all 18 are cone-killers — the two classifications are
   perfectly complementary.
5. No wedged mechanism exists at k = 1; wedging starts at k = 2 (18 cases).

**Gaps / caveats (honest list).**

* **G-a (biggest).** Tests 2–4 use **retained rows only**. GAINED contacts can re-feed
  the cone and un-kill a stratum. At travel ≤ 0.05 the menu is only 4 pairs
  ((6,7), (8,9), (3,4), (7,10)) and **no** wall row, so the re-feeding is bounded and
  enumerable — but the 81-survivor count is a *lower* bound on the work until M3
  re-runs the cone test with the gained menu included.
* **G-b.** Everything is at **z-hat only**. Gradients drift along strata; the cone can
  reopen away from the jam (theory.md T1-a caveat (i)). M3 must measure the radius of
  validity of the per-family Farkas directions. Margins are recorded to make that
  cheap (Farkas min lower bound 0.2297; smallest firing coefficient 0.0594).
* **G-c.** Rank-*deficiency* (dof > 0) is `[NUM]`, never rigorous, at a rational
  approximation of an algebraic point. Only dof = 0 verdicts are certified. This is
  intrinsic, not a shortcut: the honest form of a mechanism claim is a Krawczyk
  continuation certificate along the stratum (M2's (C)), not a rank statement at a
  point. Spectral gaps are stored per stratum so the threshold choice is auditable.
* **G-d.** The one-sidedness (movable/wedged) test is first-order only; a "movable"
  direction is not certified to extend to a finite arc — again M2/(C).
* **G-e.** The force-balance rule is not interval-extended and ignores gained rows.
* **G-f.** Sampling at k ≥ 4 in Task 2 is 2000 per k (Task 5: 2000; synthesis: 4000);
  the global 81-survivor statement is exhaustive and does **not** depend on sampling.
* **G-g.** λ* residual is bounded at z-hat, not over a box; theory.md's `r_res` for
  the inflation lemma needs the box version (M2).

---

## Files

* `attempts/A35-escape-complex/code/strata_lib.py` — cert loading, exact z-hat,
  `[IV]` and mp Jacobians, `[RFP]` nonsingularity, per-subset rank/dof/kernel,
  24 contact edges + rows-per-edge map, SAT gaps.
* `attempts/A35-escape-complex/code/m1_enum.py` — tasks 1–5, synthesis, self-check
  block (asserts rank 34, self-stress dim 4 = k1-empty count, Farkas positivity,
  λ* floor and residual recomputed from the stored rationals, min support 32 /
  K = 6, the three vertex enumerations agreeing, every cut verified to disconnect,
  k = 1 fully disposed).
* `attempts/A35-escape-complex/results/m1_strata.json` — all data, each block with a
  `method` note.
* `attempts/A35-escape-complex/results/m1_report.md` — this file.
