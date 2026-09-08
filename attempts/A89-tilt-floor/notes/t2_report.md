# A89 / T2 — corner-blocker tilt census (Opus compute chore)

Repo `C:\Users\esumm\code\packing`. All writes under `attempts/A89-tilt-floor/`.
A57 / A60 / A61 / A86 untouched (not read, not written). Frozen verifiers untouched.
BLAS pinned to 1 thread; 1 python process at a time; peak wall time 47 s (task A).

## 0. Headline

| | |
|---|---|
| min POSITIVE tilt of a **loaded(forced)** corner blocker, A87's 167 certified k0 FJ points | **23.891023311515532 deg** (`o026` sq5 TL) |
| min POSITIVE tilt of a **loaded(loadable)** corner blocker, same 167 | 3.6261485547584e-07 deg (`o075` sq4 TL) — **polish noise**, see §1.4; above 1e-6 deg: **23.891023311515532 deg** (`o026` sq5 TL) |
| min POSITIVE tilt of **any** corner blocker, same 167 | 3.626e-07 deg (`o075` sq4); next 1.675e-04 deg (`o075` sq10 BR) |
| loaded blockers with tilt in (1e-7, theta_0), all theta_0 <= 20 | **forced 0, loadable 1** (the `o075` artifact) |
| loaded blockers with tilt in (1e-7, 30) | forced 2, loadable 3 |
| min POSITIVE tilt of a loaded corner blocker, 12 atlas families | **33.8963139039382 deg** (`fam13` sq5 TR, forced) — matches A46 WC-loaded min |
| loaded blockers in (1e-7, 30), atlas | **0** for every candidate theta_0 |
| near-flush ghosts (T1 (ii) two-square corner jam) found | **1** of 665 (A87 `o170` BR, sigma = 4.0000000000300) — **both members entirely unloaded** |
| Trump canary | **PASS** — 0 corner blockers with tilt in (1e-7, theta_0) for every theta_0 <= 30; the 3 slot squares have tilt < 2.2e-69 deg |
| A85 D1: fraction of FAILED blocker nodes whose box meets Z(theta_0) | **0.0** for every theta_0 in {0.5, 1, 1.7347, 2, 5, 10, 15} |
| A85 D2: sound BL cover boxes meeting Z(theta_0) | 128/644 = **0.19876** for theta_0 <= 7.125; 290/644 = 0.45031 at 10; 452/644 = 0.70186 at 15 |
| A85 D2: tilt volume deleted (deg / t) at theta_0 = 1.7347 | **0.034307 / 0.039971** |
| A85 D2: level-2 pairs with >= 1 member in a zone-touching bin | **10483/33656 = 0.31147** for theta_0 <= 7.125 |
| A85 D2 (e): level-2 pairs killed by the refined level-0 prune | 0 at theta_0 <= 2; **146** at 5; 10483 at 10; 22630 at 15 |

Empirical verdict: **no loaded corner blocker anywhere in the corpus has tilt in
(1e-6, 23.89) deg.** Every positive-tilt corner blocker below 20 deg in the
corpus is a rattler or an unloaded square. theta_0 = 1.7347 (A50) and
theta_0 = 10 are both comfortably clear of the data.

---

## 1. Task A — A87's 167 certified k0 FJ points

Source `attempts/A87-drain-flow/results/cp87_fj_polished.jsonl` (269 lines).
Selection = `final.k0` true AND the ladder entry at tol 1e-6 has
`fj_feasible` true. **Count confirmed = 167** (all 167 carry `z_polished`;
0 error records). Rows: `results/t2_blockers_a87.jsonl` (665 lines).
Summary: `results/t2_summary_a87.json`.

### 1.1 counts

| | |
|---|---|
| corner blockers | 665 (3.982 / point; min 1, max 5) |
| rattler blockers (no active row at tol 1e-6) | 179 |
| blockers with rows but nothing loadable | 101 |
| loaded(loadable) | 385 |
| loaded(forced) | 118 |
| points whose FJ polytope also has lam_0 = 0 solutions | 6 (`o012`, `o092`, `o150`, `o154`, `o157`, `o161`) |
| points with a pair lacking a consistent selection | 0 |
| points with an infeasible multiplier LP | 0 |

Per-corner blocker count over the 167 x 4 = 668 (point, corner) slots:

| blockers at that corner | 0 | 1 | 2 | >= 3 |
|---|---|---|---|---|
| slots | 24 | 623 | 21 | 0 |

**Points violating A58 / K0-2 (every corner box met by >= 2 squares): 167 of 167.**
(Expected — these are FJ points, not k-maximal minimisers. **All 167 sit at
sigma >= 3.897230786656917**, strictly above s-hat = 3.877083590022814, so none of
them bears on H1 directly.)

### 1.2 tilt histogram (bins as specified)

| bin (deg) | all | loaded(forced) | loaded(loadable) | unloaded or rattler |
|---|---|---|---|---|
| 0 exact (< 1e-7) | 353 | 78 | 343 | 10 |
| (1e-7, 0.5) | 70 | 0 | 1 | 69 |
| [0.5, 1) | 24 | 0 | 0 | 24 |
| [1, 1.7347) | 17 | 0 | 0 | 17 |
| [1.7347, 2) | 5 | 0 | 0 | 5 |
| [2, 5) | 20 | 0 | 0 | 20 |
| [5, 10) | 26 | 0 | 0 | 26 |
| [10, 20) | 53 | 0 | 0 | 53 |
| [20, 30) | 42 | 2 | 2 | 40 |
| [30, 40) | 21 | 6 | 7 | 14 |
| [40, 45] | 34 | 32 | 32 | 2 |

353 exact-0 blockers: axis-aligned squares meeting a corner box. These are the
k0-legal case T1 (iii) (tilt 0, offset from the corner slot) — the k0 test used by
A87 excludes only squares that are BOTH axis-aligned AND within 1e-6 of a slot.

### 1.3 count in the deleted zone (1e-7, theta_0)

| theta_0 | loaded(forced) | loaded(loadable) | unloaded/rattler | all |
|---|---|---|---|---|
| 0.5 | 0 | 1 | 69 | 70 |
| 1 | 0 | 1 | 93 | 94 |
| 1.7347 | 0 | 1 | 110 | 111 |
| 2 | 0 | 1 | 115 | 116 |
| 3 | 0 | 1 | 128 | 129 |
| 5 | 0 | 1 | 135 | 136 |
| 10 | 0 | 1 | 161 | 162 |
| 20 | 0 | 1 | 214 | 215 |
| 30 | 2 | 3 | 254 | 257 |

### 1.4 the single loadable blocker in (1e-7, 0.5)

`o075`, square 4, corner TL, sigma = 4.000000001756804.
tilt = 3.6261485547584016e-07 deg (theta mod 90 = 89.99999963738514 deg).
Contacts: two wall rows on `x=0`, both **flush edge on wall** (2 vertices on the
wall, wall gap 1.2330e-09), plus a flush pair contact with square 1
(rel mismatch 3.2364e-07 deg). lam_min = 0 on every incident row (so NOT forced);
lam_max = 0.0762 / 0.1486. This is a numerically flush square whose polished
theta misses pi/2 by 3.6e-7 deg — a Newton-polish residue, not a geometric
near-flush ghost. Nothing else loadable lies below 23.891 deg.

### 1.5 blockers with tilt in (1e-7, 10): wall view — 162 blockers

| corner walls touched | rattler | corner-wall contact loadable | count |
|---|---|---|---|
| 0 | yes | — | 109 |
| 0 | no | — | 18 |
| 1 | no | no | 32 |
| 1 | no | **yes** | 1 (`o075` sq4, §1.4) |
| 2 | no | no | 2 |

161 of 162 have **no loaded corner-wall contact**; 127 of 162 do not touch a
corner wall at all.

### 1.6 near-flush ghost (T1 (ii)): 1 found in 665

`o170`, corner BR, sigma = 4.0000000000300.

| square | tilt (deg) | corner-frame centre | penetration margin | walls touched | rattler | forced | loadable |
|---|---|---|---|---|---|---|---|
| 10 | 0.7593009054921772 | (0.5065820512, 1.5028189814) | 0.0037630698 | `x=s` (corner-on-wall, 1 vertex) | no | no | no |
| 4 | 6.6849257495904740 | (1.4515962512, 0.5548053726) | 0.1032091215 | 1 | no | no | no |

sq10's active rows: wall `x=s` corner-on-wall (gap 1.0001e-09);
`sep(o=10,e=2,p=0,k=1)` = corner-of-P-on-edge-of-Q with sq0 (rel 0.7593 deg);
`sep(o=4,e=1,p=10,k=0)` = corner-of-Q-on-edge-of-P with sq4 (rel 5.9256 deg).
**All three rows have lam_max = 0** — the jam is geometrically present and
carries no load, i.e. criticality says nothing about it (T1 case (i)/(ii)).
sigma = 4.0 is far above s-hat, so it is not a counterexample below s-hat.

---

## 2. Task B — the 12 atlas families

Entries: families 0, 1, 2, 6, 13, 14, 27, 31, A37-NEW-0..3 from
`attempts/A46-balanced-wedge/results/atlas_mismatch_audit.json`; extraction and
loadability LP reused from `attempts/A46-balanced-wedge/code/task1_audit.py`
(-> A44 `eval_atlas.lp_block`, lambda_0 = 1 form, cap 1e6, LP_TOL 1e-7).
Rows: `results/t2_blockers_atlas.jsonl` (51). Summary `results/t2_summary_atlas.json`.

51 blockers over 12 x 4 = 48 slots: 45 slots with 1 blocker, 3 with 2
(fam0 BR, fam1 TR, fam2 TR). All 12 points violate K0-2 (>= 2 per corner).
5 rattler blockers, 27 forced, 33 loadable, 25 **slot squares**
(tilt < 1e-7 and corner-frame centre = (0.5, 0.5) to 1e-6).
fam27 and famA37-NEW-1 have an infeasible multiplier LP on both the physical
and expanded row sets (A46's own finding): all their contacts are tagged
`unknown` and therefore counted as unloaded here.

| bin (deg) | all | loaded(forced) | loaded(loadable) | unloaded or rattler |
|---|---|---|---|---|
| 0 exact (< 1e-7) | 40 | 23 | 29 | 11 |
| (1e-7, 0.5) | 2 | 0 | 0 | 2 |
| [0.5, 1) | 1 | 0 | 0 | 1 |
| [1, 1.7347) | 0 | 0 | 0 | 0 |
| [1.7347, 2) | 0 | 0 | 0 | 0 |
| [2, 5) | 0 | 0 | 0 | 0 |
| [5, 10) | 1 | 0 | 0 | 1 |
| [10, 20) | 1 | 0 | 0 | 1 |
| [20, 30) | 0 | 0 | 0 | 0 |
| [30, 40) | 3 | 3 | 3 | 0 |
| [40, 45] | 3 | 1 | 1 | 2 |

Exact-0 bin, 40 entries: 23 have theta literally `0`; the other 17 have
theta = pi/2 stored as a 40-digit rational, so tilt ~ 1e-38 deg — the exact-0
branch in substance.

Every positive tilt below 30 deg is a **rattler** touching **zero** corner walls:

| family | corner | sq | tilt (deg) | status |
|---|---|---|---|---|
| fam13 | TL | 1 | 0.02515605490452799 | rattler |
| famA37-NEW-1 | TL | 10 | 0.16877 | rattler (LP infeasible family) |
| fam14 | TL | 1 | 0.51853 | rattler |
| famA37-NEW-2 | TL | 7 | 5.47168 | rattler |
| famA37-NEW-0 | TL | 1 | 11.77029 | rattler |
| fam13 / fam14 | TR | 5 | 33.8963139039382 | **forced** |
| famA37-NEW-2 | BL | 10 | 38.44095 | **forced** |
| fam0 | BR | 0 | 40.18194 | **forced** |
| fam1 / fam2 | TR | 4 / 0 | 45.00000 | unloaded |

theta_0 table: **0 loaded blockers in (1e-7, theta_0) for every candidate up to 30**;
unloaded/rattler counts 3 (theta_0 <= 5), 4 (10), 5 (20 and 30).
Near-flush ghosts: **0**.

---

## 3. Task C — Trump canary

Source of the exact configuration: `attempts/A03-upper-reconstruct/trump11_exact.json`
(the file `t3lib.load_trump()` reads — there is no `certs/trump11_certificate.json`
in this repo). 60-digit decimals; s = 3.87708359002281417730789706010096270637...
Rows `results/t2_blockers_trump.jsonl`, summary `results/t2_summary_trump.json`.

5 corner blockers; per corner BL 1, BR 1, TL **2**, TR 1.

| corner | sq | tilt (deg, 300-dps from the certificate) | corner-frame centre | margin | walls | forced | loadable |
|---|---|---|---|---|---|---|---|
| BL | 0 | -1.8840654013511302e-70 | (0.5, 0.5) | 1.0 | x=0, y=0 | yes | yes |
| BR | 2 | 2.1159460961932019e-70 | (0.5, 0.5) | 1.0 | x=s, y=0 | yes | yes |
| TR | 5 | 1.8805598373768301e-69 | (0.5, 0.5) | 1.0 | x=s, y=s | yes | yes |
| TL | 4 | 1.1456698272889512e-107 | (0.5, 1.3445252757) | 0.1554747243 | x=0 | yes | yes |
| TL | 6 | 40.181937290329716465230342368060621542... | (1.5362871803, 0.7046081699) | 0.1683209895 | y=s | yes | yes |

* Three slot squares (BL sq0, BR sq2, TR sq5) confirmed: **|tilt| < 2.2e-69 deg
  < 1e-12** (the table's signed values carry the sign of the stored theta), so they are in the lemma's exact-0 branch. They are not literally the
  string `0`: the certificate stores theta = O(1e-71) rad, the Gauss-Newton residue
  of an exactly axis-aligned pose (its `t = tan(theta/2)` column is exact only for
  the tilted angle). No rational/exact-0 statement is available from this file;
  the |tilt| < 1e-12 branch of the brief applies.
* **CANARY = PASS**: for every theta_0 in {0.5, 1, 1.7347, 2, 3, 5, 10, 20, 30},
  the number of Trump corner blockers with tilt in (1e-7, theta_0) is **0**.
* TL crowd: sq6 tilt = **40.1819372903297164652...** deg (the octic angle);
  the second TL blocker is sq4, an **axis-aligned upright** (tilt 1.15e-107 deg)
  whose centre sits at (0.5, 2.5325583153) — corner-frame (0.5, 1.3445), i.e.
  0.8445 above the slot centre; it pokes 0.1555 into the TL box. Both are
  loaded(forced).
* **Definition deviation from the brief's A58 paraphrase:** the TL box is met by
  ONE tilted square (sq6, 40.182 deg) and ONE axis-aligned offset upright (sq4),
  not by "two tilted squares". This is the k0-legal exact-0-but-offset case
  T1 (iii), so the lemma's exact-0 branch must (and does) contain it.

---

## 4. Task D — A85's LP rows and the BL blocker-box census

Results: `results/t2_a85_zone.json`. Zone Z(theta_0) = (0, theta_0) u (90 - theta_0, 90)
in raw theta (equivalent to tilt in (0, theta_0)).

### 4.1 D1 — the LP nodes

`a85_lp_samples.jsonl` = 24 records, **12 distinct node tags** (each appears
twice: a pre-record with `group` null and the final group-tagged record).
`a85_lp_plan.json` lists **26** planned nodes; the 14 unrun ones have no boxes
recorded anywhere in the samples file, so their tilt ranges are unknown from
this source. The per-node `nodes/k0_00/*.json` files are tree-node dumps
(atoms / rows / tau) and carry no `boxes` field.

| tag | group | verdict | blocker node? | box theta ranges (deg) |
|---|---|---|---|---|
| s1cor_far_b595 | S1-COR | PASS | yes | [82.8750, 90.0000] |
| s1cor_near_b178 | S1-COR | **FAIL** | yes | [41.1121, 48.8879] |
| s1int_l1_008 | S1-INT | **FAIL** | no — *interior: lemma not applicable* | [30.0000, 45.0000] |
| s1int_l1_043 | S1-INT | **FAIL** | no — *interior: lemma not applicable* | [15.0000, 30.0000] |
| s1int_l1_053 | S1-INT | **FAIL** | no — *interior: lemma not applicable* | [75.0000, 90.0000] |
| s1int_l2_l2_p114_010 | S1-INT | PASS | no — interior | [0.0000, 7.5000] |
| s1int_l2_l2_p210_001 | S1-INT | PASS | no — interior | [7.5000, 15.0000] |
| s1int_l2_l2_p215_011 | S1-INT | **FAIL** | no — *interior: lemma not applicable* | [82.5000, 90.0000] |
| s2_near_046_619 | S2 | PASS | yes | [28.0725, 41.1121], [82.8750, 90.0000] |
| s3_near_BL619642_TR023305 | S3 | PASS | yes | [82.8750, 90.0000], [7.1250, 14.2500], [48.8879, 61.9275] x2 |
| s3_far_BL389484_TR018470 | S3 | **refused** (tau 7.000000 >= budget 7) | yes | [75.7500, 82.8750] x2, [14.2500, 28.0725], **[0.0000, 7.1250]** |
| s4_near_BL357619_BR004483_TR191404 | S4 | PASS | yes | [75.7500, 82.8750] x2, [82.8750, 90.0000] x2, [61.9275, 75.7500], [48.8879, 61.9275] |
| 3 x S2, 4 x S3, 3 x S4, 4 x S5 | | not-run | yes | (no boxes recorded) |

Verdict classes over the 26 planned: PASS 6, FAIL 5, refused 1, not-run 14.

**For every theta_0 in {0.5, 1, 1.7347, 2, 5, 10, 15}:**

| | |
|---|---|
| failed nodes | 5 |
| failed **blocker** nodes | 1 (`s1cor_near_b178`, theta box [41.11, 48.89]) |
| failed blocker nodes whose box meets Z(theta_0) partly | **0** |
| failed blocker nodes whose box lies entirely in Z(theta_0) | **0** |
| fraction of failed blocker nodes touched | **0.0** |
| failed **interior** nodes (lemma not applicable) | 4 (`s1int_l1_008`, `s1int_l1_043`, `s1int_l1_053`, `s1int_l2_l2_p215_011`) |
| **unresolved** (FAIL / refused / not-run) blocker nodes touched | 1 — `s3_far_BL389484_TR018470`, whose TR box is [0, 7.1250] (partly deleted for every candidate; entirely only for theta_0 >= 7.1250) |
| all RUN blocker nodes with a zone-touching box | 5 of 6: `s1cor_far_b595`, `s2_near_046_619`, `s3_far_BL389484_TR018470`, `s3_near_BL619642_TR023305`, `s4_near_BL357619_BR004483_TR191404` |

So on the sampled LP evidence the lemma deletes **none** of the observed FAILs:
the one failing corner node sits at 41-49 deg. The zone-touching blocker boxes
all belong to nodes that PASSed (4) or were refused on budget (1).

### 4.2 D2 — the BL cover / pair census

`a85_reach_BL.json`, variant `sigma_closed_7`: 678 cover boxes, **644 sound**,
sigma-closed box set = True, w_widen = 0.026, a = 1.026, rect (0.5, 1.75)^2,
w_box = 0.15, a_min = 0.34.

Parametrisation confirmed by reading `attempts/A85-k0-route/code/corner85.py`:
`T_EDGES` are edges in t = tan(theta/2), t in {0, 1/8, 1/4, 3/8, 5/11, 3/5, 7/9, 1},
mapped by theta = 2*atan(t) to degrees {0, 14.250033, 28.072487, 41.112090,
48.887910, 61.927513, 75.749967, 90}. `cover_sigma` additionally bisects theta at
the **degree** midpoint when min(a(b), a(sigma b)) < a_min, so the realised cover
has **9** theta bins, not 7:

`[0, 7.125016] [7.125016, 14.250033] [14.250033, 28.072487] [28.072487, 41.112090]
[41.112090, 48.887910] [48.887910, 61.927513] [61.927513, 75.749967]
[75.749967, 82.874984] [82.874984, 90]`
with 64, 81, 81, 64, 64, 64, 81, 81, 64 sound boxes.

`a85_pairs_BL.json` level-2 survivors: **33 656** (streamed count matches the
file's own `n_pair.level2`).

| theta_0 | (a) sound boxes meeting Z | frac | boxes entirely in Z | (b) vol frac deg | (b) vol frac t | (c) pairs >= 1 member | frac | (c) pairs both | frac | (d) >= 1 member entirely in Z | (d) both |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 128 | 0.19876 | 0 | 0.009888 | 0.011602 | 10483 | 0.31147 | 1300 | 0.038626 | 0 | 0 |
| 1 | 128 | 0.19876 | 0 | 0.019777 | 0.023138 | 10483 | 0.31147 | 1300 | 0.038626 | 0 | 0 |
| 1.7347 | 128 | 0.19876 | 0 | **0.034307** | **0.039971** | 10483 | 0.31147 | 1300 | 0.038626 | 0 | 0 |
| 2 | 128 | 0.19876 | 0 | 0.039554 | 0.046015 | 10483 | 0.31147 | 1300 | 0.038626 | 0 | 0 |
| 5 | 128 | 0.19876 | 0 | 0.098884 | 0.113184 | 10483 | 0.31147 | 1300 | 0.038626 | 0 | 0 |
| 10 | 290 | 0.45031 | 128 | 0.212871 | 0.237065 | 22630 | 0.67239 | 7194 | 0.213751 | 10483 | 1300 |
| 15 | 452 | 0.70186 | 290 | 0.338022 | 0.367496 | 30746 | 0.91354 | 18606 | 0.552829 | 22630 | 7194 |

(b) is the (x, y, theta)-volume fraction of the union of the 644 sound boxes that
the deletion removes; the unweighted 1-D tilt-extent fraction agrees to 15 digits
(the boxes tile a uniform 9 x 9 centre grid, so the (x, y) weights are equal).

**(d)** As predicted, no bin lies entirely inside Z(theta_0) for any
theta_0 <= 7.125016: the two end bins are 7.125016 deg wide. Zero for
theta_0 in {0.5, 1, 1.7347, 2, 5}; the counts at 10 and 15 are non-zero
because the end bins (and, at 15, also the second bins) are then swallowed whole.

**(e)** Refinement approximation (as licensed by the brief): clip the end bins to
[theta_0, 7.125016] and [82.874984, 90 - theta_0], drop any sub-bin that ends up
inside Z, then re-run the LEVEL-0 prune `corner85.pruned`
(P1 `pinguard.cores_meet` / P2 max centre distance < 1) on the 33 656 level-2
survivors. Cheap: 0.1-0.3 s per theta_0.

| theta_0 | boxes clipped | boxes emptied | pairs killed | frac | by cores_meet | by emptied box |
|---|---|---|---|---|---|---|
| 0.5 | 128 | 0 | 0 | 0.0000 | 0 | 0 |
| 1 | 128 | 0 | 0 | 0.0000 | 0 | 0 |
| 1.7347 | 128 | 0 | 0 | 0.0000 | 0 | 0 |
| 2 | 128 | 0 | 0 | 0.0000 | 0 | 0 |
| 5 | 128 | 0 | 146 | 0.004338 | 146 | 0 |
| 10 | 162 | 128 | 10483 | 0.311475 | 0 | 10483 |
| 15 | 162 | 290 | 22630 | 0.672391 | 0 | 22630 |

Level 0 is strictly weaker than the level-2 refinement that produced the 33 656
survivors, so these are a **lower bound** on what a re-run census would kill.
Reading: at theta_0 <= 2 the deletion narrows 128 of 644 boxes but kills no pair
by the core test; the whole benefit at small theta_0 is the 1-4 % tilt-volume
shave, not a drop in node count. The census only loses nodes once
theta_0 > 7.125016 (an end bin dies whole), which is far above what T2's data
supports as a *loaded* floor but far below the 23.89 deg the data actually shows.

---

## 5. Definition deviations / caveats

1. **Normalisation.** A87's `z_polished` is `fjpolish87.canonical`-normalised:
   the min corner sits at PAD = 1e-9 and z[33] = side + 2*PAD. Rather than
   re-shift (which makes `t3lib.test_ab` call the exactly-flush point
   infeasible), sigma is taken as the measured enclosing side and the origin as
   the measured min corner; corner boxes are built from those. The wall rows keep
   using z[33], a 2e-9 discrepancy — five orders below the 1e-6 contact tolerance
   and eleven below every reported margin.
2. **Trump rows.** `fjpolish87.classify` maps every coordinate through
   `float()` + `limit_denominator(1e15)`; on the 60-digit Trump certificate that
   1e-16 perturbation makes tangent pairs *certainly overlapping* for the interval
   SAT test. Task C therefore calls `jobs87.active_rows_at_point` directly on the
   exact Fractions (`t2_a87.classify_exact` / `grad_exact`) and applies the same
   PAD = 1e-9 translation exactly. Tasks A and B use A87's / A46's own paths
   unchanged.
3. **Positive tilt threshold.** "tilt in (0, theta_0)" is implemented as
   tilt in (1e-7, theta_0), matching the brief's own first bin
   "[0 exact (< 1e-7 deg)]". Without this, Trump's O(1e-70) and the atlas's
   O(1e-38) representational residues would be counted as positive tilts.
4. **Multiplier LP.** Task A uses the brief's polytope
   {lam >= 0, lam_0 + sum lam = 1, lam_0 grad s = sum lam_k grad g_k} on the RAW
   (non-normalised) gradient rows and reports lam_min / lam_max per row; the A46
   lambda_0 = 1 form (`A^T lam = e_s`, 0 <= lam <= 1e6) is reported alongside in
   every row record (`lam_min_a46`, `lam_max_a46`). The two forms agree on
   forced/loadable for **662 of the 665** blockers; the 3 disagreements are
   `o012` squares 0, 2, 4 (the A46 form calls them forced, the brief's polytope
   only loadable) and are exactly the effect of `o012`'s lam_0 = 0 branch, which
   the normalised polytope admits and the lambda_0 = 1 form cannot see. All 3
   have tilt in the exact-0 bin, so no headline number moves. Task B uses A46's
   own LP verbatim (per-edge, lambda_0 = 1), so its lambda scales differ from
   Task A's by construction.
5. **Atlas loadability gaps.** fam27 and famA37-NEW-1 have an infeasible
   multiplier LP (A46's own result); their contacts are `unknown` and are counted
   as unloaded, which is the conservative direction for the tilt-floor claim
   (it can only add spurious *unloaded* near-flush blockers, never remove a
   loaded one).
6. **Exactness.** theta is stored in radians as a rational in every source, so
   tilt = dist(theta*180/pi, 90Z) is transcendental and no exact rational
   statement is possible except "theta = 0 exactly => tilt = 0 exactly". Trump's
   tilts are computed at 300 decimal digits; A87 / atlas tilts in float64.
7. **A85 not-run nodes.** 14 of the 26 planned LP nodes were never run and carry
   no boxes in `a85_lp_samples.jsonl`, so D1's zone classification covers only
   the 12 nodes with records.

## 6. Files

```
attempts/A89-tilt-floor/
  code/a89lib.py        geometry, corner-box SAT meet, tilt, FJ-polytope LP, summary tables
  code/t2_a87.py        TASK A (+ classify_exact / grad_exact used by task C)
  code/t2_atlas.py      TASK B
  code/t2_trump.py      TASK C
  code/t2_a85.py        TASK D
  code/t2_combine.py    merged summary
  results/t2_blockers_a87.jsonl     665 blocker rows
  results/t2_blockers_atlas.jsonl    51 blocker rows
  results/t2_blockers_trump.jsonl     5 blocker rows
  results/t2_summary_a87.json    results/t2_summary_atlas.json
  results/t2_summary_trump.json  results/t2_a85_zone.json
  results/t2_summary.json        merged headline + all four tasks
  logs/t2.log
  notes/t2_report.md   (this file)

  --- T2 ADDENDUM (reach / self-jamming / depth) ---
  code/t2b_reach.py     reach upper bounds, witnesses, the 190-motion library, H0/H1/H2, canaries
  code/t2b_depth.py     intrusion depth: box census, blocker-row annotation, Trump exact
  results/t2b_reach.json            H0 / H1 / H2 / sanity / theta0 sweep / canaries
  results/t2b_pairs.jsonl           33 656 rows, one per census pair box
  results/t2b_depth.json            depth parts (1)(2)(3)
  (the three t2_blockers_*.jsonl files gained `depth` and
   `f_minmax_corner_frame` fields in place)
```

---

# A89 / T2 ADDENDUM — REACH and SELF-JAMMING of BL corner 2-crowds

Code `code/t2b_reach.py` (+ `code/t2b_depth.py`), results `results/t2b_reach.json`,
`results/t2b_pairs.jsonl` (33 656 rows), `results/t2b_depth.json`.
One process, BLAS pinned; reach census 60.5 s, depth add-on 0.5 s.

Object: pairs (A, B) of unit squares in the quadrant {x >= 0, y >= 0} (BL corner
frame), interior-disjoint, BOTH meeting the open slot (0,1)^2 (A58 blockers,
docs/proofs/k0_route.md 4.4). x-extent(Q) = c_x + (|cos th| + |sin th|)/2
(= max x over Q); X0 = max x-extent over the pair, Y0 likewise,
REACH = max(X0, Y0). Population: A85's level-2 pair census. Pair indices i, j
were CONFIRMED to address the 644-entry SOUND box list of `a85_reach_BL.json`
variant `sigma_closed_7` (checked against the file's own `box_i` / `box_j`).

## A0. Headline

| | |
|---|---|
| max REACH over **library-jammed** pairs (witness, exact) | **2.386035008177613** |
| max REACH over all pairs with a slot witness | 2.3876623371865477 |
| max REACH over all pairs with a witness (slot or widened) | 2.4223845591865474 |
| sound max of the box UPPER bound over the census | 2.4571067811875476 |
| theoretical single-blocker max, slot (1 + sqrt2) | 2.414213562373095 |
| **fraction library-jammed** (of pairs with a witness) | **151 / 7800 = 0.019359**, 95% CI [0.016301, 0.022417] |
| fraction needing a third square / the far structure to be stuck | **0.980641** |
| 2 x max X0 over jammed pairs | **4.772070** >= s-hat = 3.877084, so adjacent-corner reach envelopes CAN overlap |
| Trump canary (TL crowd in the BL frame) | **library-JAMMED**, type stacked-dipping-vertex |
| K0-PAIR 4.4 exhibit canary | SAT gap **+0.0442** (doc says 0.0441), **library-UNJAMMED** as expected |
| near-slot pocket canary | **library-UNJAMMED**: rotating the flush partner back to tilt 0 lifts its dipping vertex out of the slot |
| Trump TL corner DEPTH (exact) | **0.1683209895497443032656420127410328332112518538723066226438** |
| BL boxes that can host a blocker of depth >= 0.5 | 146 / 644; pairs with BOTH deep at 0.5: **0** |

## A1. Sanity checks (all pass)

| witness kind | n | reach min | reach max | bound | violations | reach < 2 |
|---|---|---|---|---|---|---|
| slot, target (0,1)^2 | 4365 | 2.0303785265 | 2.3876623372 | 1 + sqrt2 = 2.4142135624 | **0** | 0 |
| widened, target (0,1.026)^2 | 3435 | 2.0069444440 | 2.4223845592 | 1.026 + sqrt2 = 2.4402135624 | **0** | 0 |

The single-blocker bound is attained by a 45-deg diamond sitting on the wall
(c_y = h) with its left vertex at x < 1: reach = c_x + h < 1 + sqrt2. An
axis-aligned blocker meeting the open slot has reach = a + 1 < 2, and indeed no
witness has reach < 2: **every** realisable 2-crowd in this census reaches
past 2. (K0-PAIR (a) forbids two axis-aligned blockers, so one member is always
pushed out.) Witness exact re-verification (Fractions: SAT gap, both
f_min_max values, quadrant): **0 failures of 7800**.

## A2. H0 — all census pairs

Sound box upper bound `reach_ub = max over the pair of (box.x1 + h_max(box))`:

| bin | [1.8,1.9) | [1.9,2) | [2,2.1) | [2.1,2.2) | [2.2,2.3) | [2.3,2.4) | [2.4,2.42) | >= 2.42 |
|---|---|---|---|---|---|---|---|---|
| pairs | 2 | 20 | 1091 | 3731 | 5284 | 8954 | 0 | 14574 |

max 2.4571068, min 1.8914896, mean 2.3434947. 33 634 of 33 656 have
reach_ub >= 2; 14 574 have reach_ub >= 1 + sqrt2 (the box bound is loose,
sound-outward).

Witnesses: **7800 / 33 656 = 0.231757** (4365 slot + 3435 widened only).

| reach_ub bin | [2,2.1) | [2.1,2.2) | [2.2,2.3) | [2.3,2.4) | >= 2.42 |
|---|---|---|---|---|---|
| witness / pairs | 91/1091 | 868/3731 | 1632/5284 | 1696/8954 | 3513/14574 |

The witness rate is a **grid LOWER bound** (5 x 5 centres x <= 8 t values per
box; a thin 2-crowd sliver can be missed). It is nevertheless the first
pairwise realisability figure for this census: A85's 586/644 "witnessed" count
is per-box and against the widened target. Witness reach: max 2.4223846,
min 2.0069444, mean 2.2666982.

## A3. H1 — self-jamming (library test)

Self-jammed (exact definition used): no continuous motion of the pair (rigid
motions of each square, the other nine squares absent) keeping the pair
interior-disjoint and inside the quadrant with X(t) <= X0 and Y(t) <= Y0
throughout, ending with the open slot met by at most one of the two.

Library (190 motions, applied to the witness pose, first success wins):
8 single translations (+/-x, +/-y, range 2.0), 2 simultaneous translations
(+x, +y), 20 rotations (each square about its centre and its 4 vertices, both
senses, range 90 deg), 160 compositions (rotate-then-translate and
translate-then-rotate, the second leg starting from the end of the first leg's
feasible prefix). Step 1e-3 in translation distance and 0.05 deg in rotation,
**fine steps only** (no coarse pre-pass), so the only soundness caveat is the
finiteness of the library. **LIBRARY-JAMMED is an UPPER BOUND on self-jammed.**

| | |
|---|---|
| pairs with a witness | 7800 |
| library-jammed | **151** (all 151 have a **slot** witness, none widened-only) |
| library-unjammed | 7649 |
| frac jammed | **0.019359**, CI95 [0.016301, 0.022417] |
| max reach jammed | **2.386035008177613**; min 2.1056086304; mean 2.2685065 |
| reach hist (jammed) | [2.1,2.2) 51, [2.2,2.3) 2, [2.3,2.4) 98 |

Top unjamming motions: `T0x-` 3429, `R0c-` 1020, `R0c+` 739, `T0x+` 565,
`R1c+` 405, `T1y+` 351, `R0v2-` 217, `R1v1+` 185, `R1c-` 174, `T1x+` 78,
then compositions (max 51). So a **plain translation or a centre rotation frees
5 of every 6 realisable 2-crowds**; the composition tier accounts for about 4%.

Jam types (definitions verbatim in `results/t2b_reach.json` under
`definitions.jam_types`; priority order near-slot > stacked-dipping-vertex >
side-jam > floating > other):

| type | count | definition sketch |
|---|---|---|
| near-slot | **0** | min over the pair of d_slot(Q) < 0.05, d_slot = max(abs(c_x-0.5), abs(c_y-0.5), tilt/90) |
| stacked-dipping-vertex | **16** | Q1 with tilt < 5 deg on a wall, Q2 beyond it with a vertex dipping into the gap between Q1 and the other wall |
| side-jam | **0** | both within 0.02 of the SAME wall, side by side along it |
| floating | **88** | some square touches no wall (min_x > 0.02 and min_y > 0.02) |
| other | **47** | of which **diamond-wedge 31** (both tilts in [35,45], each on a wall AND at its cap) + 16 unclassified |

### Necessary-condition claim: FALSIFIED as stated

The addendum's claim "if a reach is >= 2 the slot can be freed by sliding a
square out along that axis" does **not** hold under the reach-cap model:

| | |
|---|---|
| library-jammed pairs with X0 < 2 **and** Y0 < 2 | **0** |
| library-jammed pairs with X0 >= 2 **or** Y0 >= 2 (the "exceptions") | **151 of 151** |
| library-jammed pairs with one axis < 2 | 30 |
| min REACH over jammed pairs | 2.1056086304 |
| min X0 over all 7800 witnesses (single axis) | 1.138888889 |

Reason (worked out on `i=47, j=233`, X0 = Y0 = 2.1777017): the caps confine the
pair to [0, X0] x [0, Y0]. The square realising the max extent cannot slide
further out, and the partner sliding out does not leave the slot, because
f_min_max is non-increasing when a square moves in -x or -y: a square can only
leave the slot by moving +x or +y, and both are blocked (by the cap on one
side, by the partner on the other). Rotating toward tilt 0 shrinks the extent
but keeps the centre, and there f_min_max only reaches 0.972 < 1. The pair is a
symmetric diamond wedge: A at tilt 41.11 with left vertex at x = 0.00285 and
top vertex at y = 2.17770, B its x/y mirror; SAT gap 0.0778, both meeting the
slot at their inner vertex (f_min_max = 0.76674). 50 exceptions are listed in
the JSON.

## A4. H2 — under the tilt/depth lemmas, and H1 cap H2

Tilt bins in {0} u [theta_0, 90 - theta_0] u {90}; a box straddling a threshold
counts as consistent (sound direction). The realised partition has 9 theta bins
with end bins [0, 7.125016] and [82.874984, 90], so the filter is a step
function of theta_0:

| theta_0 | pairs consistent | frac of census | with witness | max reach_ub | max witness reach | H1 cap H2 jammed | frac jammed | near-slot | stacked | side | floating | other |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 (= H0) | 33656 | 1.0000 | 7800 | 2.4571068 | 2.4223846 | 151 | 0.01936 | 0 | 16 | 0 | 88 | 47 |
| 0.5 / 1 / **1.7347** / 2 / 5 | 33656 | 1.0000 | 7800 | 2.4571068 | 2.4223846 | **151** | 0.01936 | 0 | **16** | 0 | 88 | 47 |
| 7.2 / 10 | 23173 | 0.6885 | 4726 | — | — | **135** | 0.02856 | 0 | **0** | 0 | 88 | 47 |
| 14.3 / 15 / 20 / **23.891** | 11026 | 0.3276 | 2556 | 2.4571068 | 2.4222169 | **133** | 0.05203 | 0 | 0 | 0 | 86 | 47 |
| 30 | 2910 | 0.0865 | 906 | — | — | 107 | 0.11810 | 0 | 0 | 0 | 76 | 31 |

**The single most useful number here: the tilt floor kills the T1 (ii) jam class
exactly once theta_0 exceeds the end-bin width 7.125016 deg.** At A50's
theta_0 = 1.7347 the bin partition is too coarse to delete anything (all 16
stacked-dipping-vertex jams survive); at theta_0 >= 7.125 all 16 die and the
only jams left are `floating` (88) and `diamond-wedge`/unclassified (47) —
configurations in which no square is near-flush on a wall, so the tilt-floor
lemma has nothing to say about them. Max reach over jammed pairs is
2.386035008 at every theta_0 (the extremal family is a tilt-41.112 pair,
untouched by any candidate floor).

## A5. Headline answers for the PI

1. **max reach over library-jammed pairs = 2.386035008** vs 2.3876623 over all
   slot-witnessed pairs and the theoretical 1 + sqrt2 = 2.4142136. Jamming
   costs essentially nothing in reach: the jammed set reaches 99.93% of the
   realisable slot-witness maximum and 98.83% of the theoretical maximum.
2. **Adjacent-corner blocker contact is NOT excluded by reach arithmetic.**
   BL and BR 2-crowds share the x axis, so their envelopes overlap iff
   X0(BL) + X0(BR) >= s. max X0 over jammed pairs = 2.386035008, so
   2 x max X0 = **4.772070** >= 3.877084 >= 3.82. Moreover **144 of the 151
   jammed pairs (95.36%) have X0 >= s-hat/2 = 1.938542** on their own. Caveat:
   X0(BL) + X0(BR) >= s is NECESSARY for interference, not sufficient (the
   envelopes are axis-aligned bounding constraints, not the squares).
3. **Only 1.94% (151/7800, CI95 [1.63%, 2.24%]) of the realisable census is
   library-jammed; 98.06% needs a third square or the far structure to be
   stuck.** Under the tilt floor the jammed fraction rises (2.86% at
   theta_0 = 7.2, 5.20% at 23.891, 11.81% at 30) purely because the
   denominator shrinks faster than the numerator: the absolute jammed count
   falls only from 151 to 135 to 133 to 107.

## A6. Canaries

| canary | slot A / B | SAT gap | reach | library | jam type |
|---|---|---|---|---|---|
| (a) K0-PAIR 4.4 exhibit (rebuilt from the doc's vertex lists; edge lengths 0.9992 / 0.9996 from the rounded print) | yes / yes | **+0.0442** (doc: 0.0441) | 2.3160 | **unjammed** via `R10->T1x+` (rotate A about vertex 0, then translate A +x) | — |
| (b) near-slot pocket: A axis-aligned at (0.51, 0.5), B flush on top at (0.51, 1.5) rotated 0.3 deg about its BL vertex | yes / yes | -0.0000 (touching) | 2.0052 | **unjammed** via `R1c-` (rotate B about its centre back to tilt 0) | — |
| (c) Trump's TL crowd mapped to the BL frame (y -> s - y): sq6 at theta 49.8181 (tilt 40.1819) + the eps-off upright sq4 | yes / yes | +0.0000 (touching) | 2.2409 | **JAMMED** (all 190 motions fail) | stacked-dipping-vertex |

(a) reproduces the doc's SAT gap to 4 digits, confirming both the exhibit and
this module's closed-form SAT. (b) is the interesting one for T1: the two-square
near-slot pocket jam is **not** self-jammed — rotating the near-flush partner
back to tilt 0 raises its dipping vertex above y = 1 (f_min_max 1.00261 > 1)
within the reach caps, which is exactly the s-nonincreasing motion T1 hoped for.
(c) Trump is a k-positive point, so this is a sanity classification only, but it
shows a real packing's corner 2-crowd IS jammed in the pair-only model, i.e.
the model is not vacuously permissive.

## A7. Intrusion depth (add-on)

depth(Q) := 1 - inf{max(p_x, p_y) : p in int(Q) cap (0,1)^2} = **1 - f_min_max(Q)**
in the corner frame; DEPTH(corner) := max over that corner's blockers.
Checks: axis-aligned [a,a+1] x [b,b+1] gives 1 - max(a,b); a 45-deg diamond with
lowest vertex (v_x, v_y) gives 1 - max(v_x, v_y); the slot square gives 1.

### (1) the 644 sound BL cover boxes

`depth_ub(box) = 1 - min_theta f_min_max(x0, y0, theta) + slack`. Exact in
(c_x, c_y) by monotonicity (f_min_max is nondecreasing in c_x and in c_y
separately, so the minimum over the centre box is at (x0, y0)); theta scanned at
2001 points and slacked outward by sqrt(2)/2 x half-spacing = 2.198e-05.

| depth_ub | < 0 | [0,0.05) | [0.05,0.1) | [0.1,0.2) | [0.2,0.3) | [0.3,0.5) | [0.5,1) | >= 1 |
|---|---|---|---|---|---|---|---|---|
| boxes | 84 | 37 | 74 | 71 | 89 | 143 | 144 | 2 |

max 1.0000220 (the two boxes that can host the slot square itself), min
-0.2567182 (84 boxes cannot reach the open slot at all — they are in reach of
the WIDENED box only), mean 0.2881632.

| delta | deep-capable boxes | frac | pairs with a deep-capable member | frac | pairs with BOTH deep | frac |
|---|---|---|---|---|---|---|
| 0.05 | 523 | 0.812112 | 33132 | 0.984431 | 14847 | 0.441140 |
| 0.1 | 449 | 0.697205 | 30778 | 0.914488 | 6081 | 0.180681 |
| 0.2 | 378 | 0.586957 | 28930 | 0.859579 | 2961 | 0.087978 |
| 0.3 | 289 | 0.448758 | 24662 | 0.732767 | 405 | **0.012034** |
| 0.5 | 146 | 0.226708 | 17228 | 0.511885 | **0** | **0.000000** |

**No census pair can have both members intruding by >= 0.5**, and only 1.2% can
have both >= 0.3 — a depth-based pair prune that is independent of tilt and
cheap to evaluate on the box census.

### (2) depth on the emitted blocker rows

A `depth` and `f_minmax_corner_frame` field was added to every row of
`t2_blockers_a87.jsonl`, `t2_blockers_atlas.jsonl`, `t2_blockers_trump.jsonl`.

| source | blockers | corners with a blocker | blocker depth max / min / mean |
|---|---|---|---|
| A87 167 points | 665 | 644 | 0.9998284 / 0.0006289 / 0.6057794 |
| atlas 12 | 51 | 48 | 1.0 / 0.1143819 / 0.8320847 |
| Trump | 5 | 4 | 1.0 / 0.1554747 / 0.6647591 |

A87 per-corner DEPTH histogram (644 corners):

| DEPTH | [0,0.05) | [0.05,0.1) | [0.1,0.2) | [0.2,0.3) | [0.3,0.5) | [0.5,1) | >= 1 |
|---|---|---|---|---|---|---|---|
| corners | 19 | 21 | 47 | 28 | 91 | 438 | 0 |

Per corner (max / min / mean of DEPTH): BL 0.9998 / 0.0335 / 0.6872,
BR 0.9997 / 0.0020 / 0.6303, TL 0.9992 / 0.0048 / 0.6504,
TR 0.9550 / 0.0031 / 0.5249. A87 blocker-depth histogram over the same bins:
32 / 25 / 50 / 29 / 91 / 438 / 0.

Atlas: 23 blockers at depth exactly 1 (the exactly-at-slot squares), 22 in
[0.5,1), 6 in [0.1,0.2), nothing between 0.2 and 0.5.

**Trump.** BL sq0, BR sq2, TR sq5 have depth = 1 exactly (they ARE the corner
boxes). TL:

| square | tilt (deg) | f_min_max (TL frame) | depth |
|---|---|---|---|
| sq4 (upright, eps-off) | 1.15e-107 | 0.8445252756731993902452807597862166028608246046465752150553 | 0.1554747243268006097547192402137833971391753953534247849446 |
| sq6 (tilted) | 40.1819372903 | 0.8316790104502556967343579872589671667887481461276933773561 | 0.1683209895497443032656420127410328332112518538723066226438 |

**DEPTH(TL) = 0.1683209895497443032656420127410328332112518538723066226438**
(Decimal at 300 dps from the certificate; the upright uses cos = 1,
sin = theta = O(1e-109), exact to the certificate). So Trump's TL corner is a
SHALLOW 2-crowd — neither blocker intrudes by more than 0.17 — while its other
three corners are at depth 1.

### (3) A87 shallow corners (DEPTH < 0.3)

| | |
|---|---|
| corners with a blocker | 644 |
| corners with DEPTH < 0.3 | **115 (17.857%)** |
| blockers at those corners | 132 |
| of which axis-aligned (tilt < 1e-7 deg) | **69 (52.273%)** |
| of which theta exactly 0 as a rational | 34 |
| loaded(loadable) at shallow corners | 66 |
| rattlers at shallow corners | 33 |

Tilt histogram of the 132 shallow-corner blockers: 69 exact-0, 16 in
(1e-7,0.5), 9 in [0.5,1), 5 in [1,1.7347), 0 in [1.7347,2), 7 in [2,5),
5 in [5,10), 8 in [10,20), 9 in [20,30), 3 in [30,40), 1 in [40,45].

So **just over half of the blockers at a shallow corner are axis-aligned** —
the shallow-corner regime is dominated by the k0-legal "tilt 0 but offset from
the slot" case (T1 (iii)), not by tilted near-flush ghosts.

## A8. Addendum caveats

1. **LIBRARY-JAMMED is an upper bound on self-jammed** (the library is finite:
   190 motions, single- and two-leg only; a three-leg or genuinely simultaneous
   rotation escape would not be found). Steps are the specified fine ones
   (1e-3 translation, 0.05 deg rotation) with no coarse pre-pass, so there is
   no step-resolution false-negative channel.
2. **Witness rate 0.2318 is a grid lower bound**, not the realisable fraction.
   All H1 statistics are conditioned on having a witness; a pair box whose
   2-crowd sliver the grid missed is absent from the H1 denominator.
3. **Witness kind.** A85's census is built for the WIDENED box (0, 1.026)^2, not
   the slot. 4365 pairs got a slot witness (the addendum's definition, w = 0);
   for 3435 more only a widened witness was found, labelled
   `witness_kind = "widened"` in `t2b_pairs.jsonl`. Every one of the 151
   library-jammed pairs has a genuine SLOT witness.
4. **The reach caps are the pair-only model** the addendum specifies (the rest
   of the packing modelled as a rigid L-wall at (X0, Y0)); they are what make
   H1 non-vacuous, and they are also why the "reach >= 2 implies unjammable"
   claim fails.
5. A85's stored per-box `witness_pose` values were NOT reused: they target the
   widened box and are not checked pairwise. Witnesses here are recomputed as
   rational grid poses strictly inside each box and re-verified in exact
   Fractions (0 failures of 7800).
6. **Headroom.** Free commit at the launches of this addendum was
   1984 / 1331 / 687 MB — below the 6144 MB gate. Each job is a single
   short-lived process whose peak RSS is well under 300 MB (the 50 MB
   `a85_pairs_BL.json` is regex-STREAMED, never `json.load`-ed), so nothing
   heavy was launched and no campaign was run. `corner85` prints a
   `blas1: numpy was already imported` warning because `a89lib` imports numpy
   first; the BLAS thread variables are set by `a89lib` (and by the shell)
   BEFORE numpy loads, so the pinning is in effect and the warning is spurious
   here.
