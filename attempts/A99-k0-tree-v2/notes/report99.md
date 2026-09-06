# A99 -- the k0_00 tree, next generation: what R1/R2/R3 actually buy (measured)

Every number here comes from a run made in this attempt. Method and provenance:
`notes/method.md`. Exact branching arithmetic: `notes/branching_cost.md`.
Raw: `results/*.jsonl`, `logs/*`, `certs/`.

**Incomplete legs.** R3(a) (`--jobs 4` vs 1), R3(b) (LP cold vs warm) and the R2 arbiter (the
frozen kill chain on the best-screened cells) were queued behind the R2 screen and never
launched -- the supervisor chain that was to start them died before writing its marker. They are
reported as NOT MEASURED, not as null results. Everything else below ran to completion.

## 0. Stacked projection (`results/projection99.json`)

| scenario | f2 | nodes | branches | window | CPU-h | desktop-days @3 slots |
|---|---|---|---|---|---|---|
| A85 headline: f2 = 0.85, s0 only | 0.85 | 6 290 | 1 | 1 | 3 106 - 7 069 | 43 - 98 |
| A85 headline x 4 fixed sides | 0.85 | 6 290 | 1 | 4 | 11 975 - 27 826 | 166 - 386 |
| A85 first-pass row: f2 = 1/3, s0 | 0.33 | 60 096 | 1 | 1 | 28 395 - 66 256 | 394 - 920 |
| **A99: f2 = 2/3 (A85's measured with-repair rate), s0** | 0.67 | 18 624 | 1 | 1 | **8 903 - 20 636** | 124 - 287 |
| **A99 STACKED, window-valid (R1 + R3c, R2 off)** | 0.67 | 18 624 | 1 | 1.05 | **9 341 - 21 661** | 130 - 301 |
| A99 STACKED, window-valid, with R2 branching | 0.67 | 18 624 | 15 | 1.05 | 138 014 - 322 811 | 1 917 - 4 483 |
| A99 STACKED, window-valid via a 4-side grid instead | 0.67 | 18 624 | 1 | 4 | 35 163 - 82 096 | 488 - 1 140 |

Model = A85 s.8.3 verbatim (N2 = 1728, N3 = 8*N2*(1-f2), N4 = 8*N3*(1-f2), per-node
0.47-1.1 CPU-h, +150 CPU-h for the (D)/(D-prime) side); only f2, the branch count and the window
multiplier are replaced by A99's measurements.

**Read-out.** The PI's ~10x is not there. R1 removes the assumption A85's headline rested on
(f2 ~ 0.85), and the honest window-valid figure is **9 300 - 21 700 CPU-h, i.e. 2.9-3.1x WORSE
than the published 3 200 - 7 000**. The one genuine reduction A99 found is R3(c): window
validity costs about **+5 percent** per node (parametric re-emission) instead of **x4** (a
4-side grid) -- a **3.8x** cut on the window, worth 25 800 - 60 400 CPU-h in the table above.
R2 is a cost multiplier, not a reduction.

## 1. R1 -- 0 of 12. A85's failures do not close by re-verification.

`code/resolve99.py --mode ladder`: every FAILed A85 k0_00 certificate re-run through the frozen
`verify_case.py` at depth 56 (A85's setting), 64, 88 -- same certificate, no new LP.

**Why the A96 shortcut cannot transfer.** resolve96 wins because `verify_param` splits the widest
axis of a 4-D cell: on the full window the s-axis is starved, so restricting the window makes
every s-cell ~1000x finer from the first split and the same certificate passes. The `--depth`
budget of `verify_case` is instead **uniform over the root split** -- the sub-tree below a box
does not depend on what else is in the run -- so "every depth-56 witness box closes with `extra`
more bisections" IS "the global run at depth 56+extra passes". There is no resolution artefact to
harvest; the depth ladder is the exact fixed-side analogue of the resolve96 sub-window re-run.

| certificate | depth 56 | depth 64 | depth 88 |
|---|---|---|---|
| `s1cor_far_b595` | FAIL 61.1 s, 10/40 holes | FAIL 66.7 s, 11/40 | FAIL 71.0 s, 17/40 |
| `s1cor_far_b595_epsgeo0.002` | FAIL 23.9 s, 5/8 | FAIL 24.3 s, 4/8 | FAIL 25.1 s, 3/8 |
| `s1cor_near_b178` | FAIL 27.4 s, 42/64 | FAIL 27.5 s, 45/64 | FAIL 28.7 s, 47/64 |
| `s1cor_near_b178_epsgeo0.002` | rc 2, 0.5 s | rc 2, 0.6 s | rc 2, 0.5 s |
| `s1int_l1_008` | FAIL 11.0 s, 26/64 | FAIL 12.2 s, 26/64 | FAIL 16.9 s, 23/64 |
| `s1int_l1_043` | FAIL 10.6 s, 13/64 | FAIL 11.7 s, 12/64 | FAIL 13.6 s, 16/64 |
| `s1int_l1_053` | FAIL 7.5 s, 42/64 | FAIL 7.5 s, 44/64 | FAIL 7.6 s, 46/64 |
| `s1int_l1_053_epsgeo0.002` | FAIL 9.4 s, 17/64 | FAIL 9.6 s, 20/64 | FAIL 10.3 s, 17/64 |
| `s1int_l2_l2_p210_001` | FAIL 314.6 s, 8/40 | FAIL 316.8 s, 11/40 | FAIL 329.7 s, 19/40 |
| `s1int_l2_l2_p210_001_epsgeo0.002` | FAIL 17.5 s, 2/16 | FAIL 17.6 s, 2/16 | FAIL 17.4 s, 2/16 |
| `s1int_l2_l2_p215_011` | FAIL 104.8 s, 6/32 | FAIL 103.2 s, 1/32 | FAIL 103.5 s, 8/32 |
| `s1int_l2_l2_p215_011_epsgeo0.002` | FAIL 15.3 s, 11/48 | FAIL 15.4 s, 13/48 | FAIL 41.5 s, 10/48 |
| `s1int_l2_l2_p215_011_epsgeo0.004` | FAIL 8.2 s, 5/64 | FAIL 9.6 s, 17/64 | FAIL 10.4 s, 26/64 |

* **0 / 12 close.** No certificate that FAILs at depth 56 passes at 64 or 88.
* **Hole counts do not fall with depth; they mostly rise** (b595 10 -> 11 -> 17; b178 42 -> 45 ->
  47; p210_001 8 -> 11 -> 19; p215_011_eps0.004 5 -> 17 -> 26). A HOLE is an admissible sampled
  placement whose exact covered mass is < 1, i.e. a genuine defect of the measure, so more
  bisection only finds more of them. The A85 k0_00 FAILs are **LP row-generation failures**, not
  verifier-resolution artefacts, and the lever is LP time -- exactly what A89-O3 concluded
  independently for the 3-shallow root node.
* **f2 is therefore unchanged by R1.** The A85 depth-2 sample (n = 3) gives f2 = 1/3 first pass
  and 2/3 with the eps_geo repairs; the f2 ~ 0.85 scenario behind the published 3 200 - 7 000
  CPU-h assumed a certification-side engineering lever that measures **zero**.
* **Artefact defect found in A85.** `s1cor_near_b178_epsgeo0.002.json` on disk has exact total
  10.050003 >= budget 10 (rc = 2, "proves nothing"): it is a later `certify.py` round that
  overwrote the certificate its `.report.json` describes. The R1 denominator is 12, not 13.

## 2. R2 -- the root shallow/deep branching costs x15 in cells, exactly, and killed nothing

### 2.1 Exact, LP-free (`notes/branching_cost.md`, `logs/branching.txt`)

D4 may quotient each branch only by the STABILISER of its corner pattern, and
`1728/|stab| = 216*|orbit|`, so summed over orbit representatives the level-1 cell count is
`216 x 16 = 3456`, or **3240 = 15 x 216** after deleting the 4-shallow class that A89 certified
dead at the root (window-valid, delta = 0.3).

| pattern class | orbit | stabiliser | level-1 cells |
|---|---|---|---|
| all deep | 1 | 8 | 216 |
| 1 shallow | 4 | 2 | 864 |
| 2 adjacent | 4 | 2 | 864 |
| 2 diagonal | 2 | 4 | 432 |
| 3 shallow | 4 | 2 | 864 |
| 4 shallow | 1 | 8 | 216 -- DEAD at the root (A89 `R1_4shallow_d0.3`) |

The **all-deep** branch keeps its 216 cells and gains **no exempt box at all** (Lemma ID fires
only at a shallow corner), so its subtree is the A85 tree verbatim: **R2 cannot price the
frontier below the A85 figure whatever the other branches do.** It is worth something only if the
four surviving classes die above the depth-2 frontier -- and A89-O3 already measured that
3-shallow does NOT die at the root at delta = 0.3 / 0.1 / 0.05 (tau climbs 10.046 -> 10.209 under
witness feedback), with 2-shallow strictly harder (`tau(2) >= tau(3) >= tau(4)`).

### 2.2 The level-1 LP screen (`results/r2_screen.jsonl`, `results/r2_patterns.jsonl`)

20 level-1 cells stratified across `T(s0) x [0,90)` (A38 indices 5, 16, ..., 214), each solved
plain and with the 3-shallow exempt families (delta = 0.3, window-valid `a_win = 0.6896936`,
136 NoFams per corner from the A89 `o3fam` builder), identical engine settings, **300 s LP
each**; plus four cells at 1-shallow / 2-adjacent / 2-diagonal. 52 LP launches, free commit
66.7-79.6 GB at every launch, zero commit waits, zero canary refusals, zero errors.

| quantity | value |
|---|---|
| median tau(plain) - tau(sh3) | **+1.0567** (min 0.0000, max 2.0000) |
| cells reaching the eta <= -1.0 screening threshold | plain **6 / 20**, 3-shallow **19 / 20** |
| median minmass | plain **0.5093**, 3-shallow **0.2396** |
| median LP wall | plain 348.4 s, 3-shallow 369.8 s |

The four-pattern subset:

| cell | plain | 1-shallow | 2-adjacent | 2-diagonal | 3-shallow |
|---|---|---|---|---|---|
| 5 | 8.0000 | 8.0000 | 8.0000 | 8.0000 | 8.0000 |
| 49 | 9.0000 | 8.8333 | 9.0000 | 8.9000 | 8.4441 |
| 137 | 9.0000 | 8.5500 | 8.5000 | 8.0000 | 8.0000 |
| 214 | 9.0775 | 8.7804 | 8.0000 | 8.6463 | 8.0000 |

The eta <= -1.0 threshold is calibrated on the 8 budget-10 A85 rows: 3/4 of the rows with
eta <= -1.0 certified, 0/4 of the rows with eta > -1.0 did.

**This is not evidence of a kill, and A99 claims none.** minmass -- the smallest generated-row
mass, and the quantity A89-O3 identified as the one that must approach 1 before a certificate can
verify -- **halves** when the exempt families are added (0.51 -> 0.24). A larger exempt region
gives the measure more freedom, so the same 300 s of row generation covers proportionally less;
tau falls because the LP is LESS converged, not because the node is closer to dead. The screen
reproduces the A89-O3 delta-sweep signature (tau down, minmass down) at cell level. The arbiter
leg that would have settled it (`code/r2_certify.py`, frozen kill chain at lp_time 900) did not
run.

**R2 verdict: a measured cost multiplier of x15 with no demonstrated kill anywhere -- at the root
(A89) or at level 1 (here). It does not enter the stacked projection as a reduction.**

## 3. R3 -- per-node cost

### 3.1 (a) certification at --jobs 4 vs 1 -- NOT MEASURED (leg never launched)

Incidental, uncontrolled data only (A85 ran --jobs 2 with --max_w 32 or 64 depending on the
phase; the A99 ladder ran --jobs 1 --max-witnesses 64): on the seven tags where the flags happen
to agree, A85 j2 vs A99 j1 is 27.4/61.1, 7.8/27.4, 6.0/11.0, 6.0/10.6, 3.8/7.5, 163.0/314.6,
47.4/104.8 s -- 1.8-3.5x. Note that --jobs buys WALL only: four worker processes, so CPU-seconds
do not fall and the CPU-h column of section 0 is unaffected; it changes desktop-days at a fixed
slot count, nothing else.

### 3.2 (b) LP warm start -- NOT MEASURED (leg never launched)

The pool was built and sized: 1 915 distinct columns from 33 A38 + A85 node files
(`r2_99.warm_pool`, the A57 warm57 pattern, columns only). All 52 R2 LPs used it; no cold
control was run, so no factor is claimed.

### 3.3 (c) parametric emission -- the window is nearly free; the one real reduction

`code/param99.py` = the A96 emitter (`to_param96.convert`, unchanged) + the frozen
`verify_param.py` over `[3.82, s0]`, depth 56, jobs 1, cap 600 s.

**The k0_00 interior cell grid is already inside the A96 (P-aff) family** -- a fact, not an
assumption: the A38/T(s0) column step is exactly `(s0 - 2*c0)/16` with `c0 = 11/10`
(`2.1481775 - 2.04335975 = 419271/4000000 = (969271/250000 - 11/5)/16`), so every cell edge and
core centre is `e_q(s0) = c0 + q*(s0 - 2*c0)` with `12q` dyadic; `core_affine` accepts them with
no new anchoring rule and the exact reconstruction assert `alpha + beta*s0 == c` holds.

| A85 certificate | emitted | fixed-side verifier | parametric over [3.82, s0] | factor | verdict | window covered |
|---|---|---|---|---|---|---|
| `s1int_l2_l2_p210_001_epsgeo0.004` | yes, 241 atoms | 4.44 s | **123.2 s** | x27.7 | **PASS** | **1.00000** |
| `s1int_l2_l2_p114_010` | yes, 53 atoms | 7.76 s | 600.0 s (cap) | >x77 | TIMEOUT | -- |
| `s1cor_far_b595_epsgeo0.004` | no | 1.72 s | -- | -- | EMIT-ERROR | -- |
| `s2_near_046_619` | no | 5.86 s | -- | -- | EMIT-ERROR | -- |
| `s3_near_BL619642_TR023305` | no | 3.51 s | -- | -- | EMIT-ERROR | -- |
| `s4_near_BL357619_BR004483_TR191404` | no | 8.09 s | -- | -- | EMIT-ERROR | -- |

* **A new window-valid kill.** `certs/param/s1int_l2_l2_p210_001_epsgeo0.004.param.json`
  (241 atoms, 1 core, exact total 997707/100000 = 9.97707 < 10) PASSes the frozen 4-D verifier on
  the whole window in 123.2 s: 1 847 066 boxes, 856 042 covered, 67 523 exempt, 255 s-cells, max
  depth 36 / max s-depth 7, **0 witnesses**. The A85 kill of that node was s0-only.
* **The window costs about +5 percent per node, not x4.** The LP (1 000 s) and the certify loop
  (630-860 s) happen once at s0; only the final verification is redone parametrically, and that
  goes 4.44 s -> 123.2 s, i.e. **+119 s on a 1 630-1 860 s node = +6 ... +7 percent** (section 0
  uses x1.05). A 4-side grid instead multiplies everything, LP included, by 4. **That is a 3.8x
  cut on the window and the only reduction A99 measured.**
* **It is not uniform.** The other emitted node (p114_010, a much sparser 53-atom certificate)
  did not finish in 600 s: >= x77, no coverage claim. The +5 percent figure rests on n = 1.
* **The corner-crowd nodes cannot be emitted at all.** Their cores are BL reach-cover box
  centres -- 17/24, 91/72, 37/24, 41/72 -- t-grid quantities, not affine in s0. The corner side
  of the k0 tree has no parametric route until an anchoring rule for them is proved.
* **Open obligation.** The affine reconstruction is asserted exactly at s0; that the A38/T(s0)
  cell at side m really is `e_q(m)` is the cover-invariance hypothesis
  (`docs/proofs/cover_invariance.md` CI-1..CI-3, proved for the A57 12-column cover).
  Transporting it to the A38 cover is the same shape of argument and is **not discharged here**.

## 4. Unmeasured / open

* R3(a), R3(b) and the R2 arbiter (above).
* Whether the 3-shallow / 2-shallow ROOT kills close with 5-10x LP time (the A89-O3 open item).
* The parametric window factor beyond n = 2 emitted nodes, and on any corner-crowd node.
* Certification reliability at eta ~ -1 on a depth-2 sample larger than the A85 3 -- still the
  constant that decides between the 8 900 and the 28 400 rows of section 0.
* The level-2 descent rate at delta_pin = 1e-2 (the A96 2.36x). Untouched.
