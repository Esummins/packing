# A92 pilot `pin1crowd92` -- ONE corner PINNED + crowd weights on the other three

Chore: does pinning one corner's blocker pair (A85 cores, stranded region exempt, budget
`11 - 2 = 9`) combine with A92's crowd weights on the other three corners to certify at small
delta, where the PURE four-corner crowd certificate refuses (`crowd92`: delta = 0.1 and 0.05
refused at every e)?

Code `code/pin1crowd92.py`; data `results/pin1crowd92.{jsonl,table.json,nodes.json,fam_d*.json,log}`.
One process, BLAS pinned, 6144 MB commit gate before every LP (it fired for 6 min at node 12),
two driver runs (the first aborted on the canary, see section 2), 100 min of LP wall in run 2.
Nothing outside `attempts/A92-blocked-side/{code,results,notes}/pin1crowd92.*` was written.

## HEADLINE

**No.** Over the 20 sampled nodes the crowd weights on BR/TL/TR are priced at almost exactly
par: the mean tau lift they cost is 0.59-1.58, against the 6e = 0.75 / 1.50 of budget they buy.
They convert 5 node/(delta,e) combinations from refuse to LP-PASS and lose 4 the other way, and
at the *certifiable* threshold (section 4) they are strictly worse than the plain pinned LP in
every column. The pinned pair, not the crowd, is what carries these nodes: 16 of 20 already pass
the plain A85 LP at budget 9.

## 1. The node

* hypothesis `Hyp([B_i, B_j], [])` -- two BL reach-cover boxes of A85's REALISABLE census
  (`realise85.pairs.json`, 7044 surviving pairs over the 644 sound `sigma_closed_7` boxes);
  cores pinned, rows meeting a core exempt; `#cores = 2`, budget `11 - 2 = 9`.
* LP row rhs `mu(Q) >= 1 + e[Q in G_3]`, `G_3 = G_BR u G_TL u G_TR` -- `crowdfam92`'s outer cover
  of `F_c(a_w(delta))` with the BL frame dropped from the membership test (`GTest3`), same
  conservative dilation (0.02 in the centre, 1 deg in theta): more rows at 1+e, never fewer.
* threshold `tau < 9 + 6e` (2 pinned, 6 crowd squares at `1+e`, 3 free at 1).
* sym C1 (a pinned BL pair breaks D4), warm pool = `lp85.warm85` replica (1915 columns),
  otherwise the `solve_node` call of `pilot59.run_child` verbatim.
* delta in {0.1, 0.05} (a_w = 0.924020 / 0.974770), e in {1/8, 1/4}; 20 nodes stratified by
  `d2_ub(i,j) = min(depth_ub_wall(i), depth_ub_wall(j))`: 10 in [0.05,0.2), 5 in [0.2,0.3),
  5 below 0.05 (all five land at 0.0278 -- the sub-0.05 pool is nearly single-valued).

`E_3` (run B's NO-families) = `crowdfam92`'s four-corner complement cover E **plus** the BL
staircase rects dilated by one grid cell, each exactly certified disjoint from `F_c(a_w)` for
c in {BR, TL, TR}: 576 boxes at delta 0.1 (425 + 151), 567 at delta 0.05 (419 + 148). The
dilation is deliberate -- abutting families leave permanently unexemptable seams (the first
`crowd92` campaign's run-B failure mode). NOTE: `results/fam_d0.1.json` / `fam_d0.05.json` in
A92 are still the stale `fam_build = 1` (abutting-strip) caches -- the follow-up rebuilt only
d0.3/d0.2 -- so this chore rebuilt both into `results/pin1crowd92.fam_d*.json`.

## 2. Canaries

* **Trump is not K0-BLOCKED / no image realises the three-corner hypothesis: PASS.** Per-image
  counts `[BL | BR TL TR]` of placements with `f_c <= a_w`, exact, identical at both a_w:
  `g0[1|121] g1[1|112] g2[2|111] g3[1|211] g4[1|211] g5[1|112] g6[2|111] g7[1|121]` -- no image
  reaches 2 at all three unpinned corners (each image has exactly one 2-crowd, Trump's TL pair
  at f = 0.831679 / 0.844500). Checked and refused before any LP, as `crowd92` does.
* **The plain pinned LP reproduces A85's stored tau: PASS.** `s2_near_046_619` (BL pair
  (46, 619), budget 9): `tau = 8.000000000` vs A85's stored `7.999999999991748`,
  `dtau = 3.2e-10`, minmass 1.0, 362 s. Warm-started from A85's own stored node state (98 cols
  + 17577 rows). A COLD 600 s solve of the same node reaches only `tau = 8.027027`
  (unconverged) -- that is what aborted driver run 1, and it measures the LP time cap, not
  node identity.

## 3. The LP table (20 nodes x {plain, 4 crowd}, 40 s cap each)

`P` = LP-PASS (`tau < 9 + 6e`), `x` = refused. **Every LP here is TRUNCATED** at 40 s
(`converged = False`, crowd minmass 0.095-0.573, median 0.400); the taus are comparative,
not sound verdicts -- see section 4(b).

| node | d2_ub | plain (thr 9) | d0.1 e=1/8 (9.75) | d0.1 e=1/4 (10.5) | d0.05 e=1/8 (9.75) | d0.05 e=1/4 (10.5) |
|---|---|---|---|---|---|---|
| `p1c_mid_055_601` | 0.0654 | 8.2016 P | 8.6941 P | 9.7500 P | 8.8750 P | 9.7416 P |
| `p1c_mid_059_486` | 0.0654 | 9.0000 x | 9.7500 x | 10.5000 P | 9.5938 P | 10.4000 P |
| `p1c_mid_012_314` | 0.0654 | 8.3810 P | 9.0607 P | 9.8484 P | 9.0992 P | 9.9937 P |
| `p1c_mid_100_286` | 0.0944 | 8.3000 P | 9.0102 P | 9.7406 P | 9.0250 P | 9.9038 P |
| `p1c_mid_231_369` | 0.1143 | 8.2429 P | 8.9318 P | 9.7605 P | 9.0400 P | 9.9098 P |
| `p1c_mid_372_631` | 0.0860 | 9.1248 x | 9.7500 x | 10.5312 x | 9.9232 x | 10.7500 x |
| `p1c_mid_323_512` | 0.0654 | 9.2322 x | 9.6667 P | 10.5862 x | 9.7989 x | 10.8628 x |
| `p1c_mid_095_314` | 0.0654 | 8.7188 P | 9.1307 P | 9.9241 P | 9.3420 P | 10.1071 P |
| `p1c_mid_140_277` | 0.0944 | 8.0000 P | 8.7893 P | 9.5000 P | 9.1000 P | 10.0140 P |
| `p1c_mid_146_513` | 0.1355 | 8.7121 P | 9.0701 P | 10.0714 P | 9.4100 P | 10.2033 P |
| `p1c_hi_285_384` | 0.2187 | 8.1012 P | 8.8258 P | 9.5222 P | 8.8581 P | 9.7500 P |
| `p1c_hi_050_273` | 0.2043 | 8.7903 P | 9.2479 P | 10.1667 P | 9.7875 x | 10.2435 P |
| `p1c_hi_084_275` | 0.2333 | 8.5684 P | 9.2548 P | 10.0348 P | 9.3194 P | 9.9348 P |
| `p1c_hi_094_601` | 0.2251 | 8.5000 P | 9.0391 P | 9.6410 P | 8.9440 P | 10.0519 P |
| `p1c_hi_084_274` | 0.2349 | 8.3109 P | 8.8077 P | 9.8804 P | 9.5000 P | 9.7500 P |
| `p1c_lo_313_354` | 0.0278 | 8.7306 P | 9.3341 P | 10.1374 P | 9.3521 P | 10.2009 P |
| `p1c_lo_366_481` | 0.0278 | 9.0000 P | 9.5424 P | 10.3941 P | 9.8750 x | 10.7500 x |
| `p1c_lo_176_312` | 0.0278 | 9.0000 P | 9.7500 P | 10.3516 P | 9.7500 P | 10.7100 x |
| `p1c_lo_313_383` | 0.0278 | 9.3023 x | 9.7921 x | 10.4202 P | 9.8750 x | 11.0913 x |
| `p1c_lo_487_619` | 0.0278 | 8.3946 P | 8.8655 P | 9.6435 P | 9.1875 P | 9.7931 P |

| | plain | d0.1 e=1/8 | d0.1 e=1/4 | d0.05 e=1/8 | d0.05 e=1/4 |
|---|---|---|---|---|---|
| **LP-PASS at `tau < 9 + 6e`** | **16/20** | **17/20** | **18/20** | **15/20** | **15/20** |
| crowd-only (plain refuses) | - | 1 | 2 | 1 | 1 |
| lost vs plain | - | 0 | 0 | 2 | 2 |
| mean tau lift over plain | - | 0.585 | 1.390 | 0.752 | 1.578 |
| 6e (budget bought) | - | 0.750 | 1.500 | 0.750 | 1.500 |
| **certifiable thr `tau < floor(9+6e)`** | **16/20** | **6/20** | **10/20** | **3/20** | **8/20** |

The five crowd-only passes are `p1c_mid_323_512` (d0.1, e=1/8), `p1c_mid_059_486` (d0.1 e=1/4,
d0.05 e=1/8, d0.05 e=1/4) and `p1c_lo_313_383` (d0.1, e=1/4) -- three distinct nodes, all with
plain tau in [9.000, 9.302], i.e. all sitting ON the plain threshold rather than far above it.
Lift / 6e = 0.78, 0.93, 1.00, 1.05: the crowd rhs prices at par, and slightly worse than par at
delta = 0.05, where a_w = 0.97477 pulls nearly every admissible pose into G_3. No signal in
d2_ub: the crowd-only passes come from the mid (2) and lo (1) strata, and the hi stratum
(d2_ub >= 0.20) passes plain in 5/5.

## 4. Certification -- 0 attempts, and the reason is structural, not only the wall clock

**(a) The integer-budget obstruction (a finding, not an engineering gap).** The frozen
`verify_case.py` parses `n = int(...)` and enforces `budget = n - #cores` as an integer
(`load_certificate`, lines 672 and 713-715). With two pinned cores the certifiable clause is
therefore `total < B` with `B = floor(9 + 6e)`:

* e = 1/8: `floor(9.75) = 9` -- **the crowd weights buy nothing at all**; the certificate is
  exactly the plain pinned one, while the LP is strictly harder (rhs raised on all of G_3).
* e = 1/4: `floor(10.5) = 10` -- they buy +1, against a measured mean tau cost of +1.39/+1.58.

Consequently **none of the five crowd-only LP passes is certifiable at its own e**: their taus
are 9.667, 10.500, 10.420, 9.594 and 10.400, every one `>= floor(9 + 6e)`. The
certifiable-threshold row (6 / 10 / 3 / 8 of 20) is strictly below the plain 16/20 in every
column. Only a crowd weight with `9 + 6e` integral (e in {1/6, 1/3, 1/2, ...}) can carry a
frozen-verifier certificate on this node shape; e in {1/8, 1/4} cannot, by construction.

**(b) The LP truncation.** A certificate needs `minmass * scale >= 1` together with
`scale * tau < B` at `scale_cap = 1.40`. The 40 s LPs have minmass 0.095-0.573 (scale 1.75-10.5
would be required), so no certificate can be formed from them at all. A certifiable node needs
a converged solve -- the canary needed A85's 17577 rows to reach minmass 1.0, and A85 prices
such a node at ~900 s LP + 630-860 s certification. The driver reached its certification stage
at 14:09 with the 100 min wall spent (6 min of it inside the commit gate) and skipped its one
candidate for that reason. The two-run certificate builder (`make_cert`, cores + `E_3`) and the
`verify_case.py` invocation are implemented and exercised only as far as family construction.

## 5. Residue -- what would decide it

1. Re-run the three crowd-only nodes (`mid_323_512`, `mid_059_486`, `lo_313_383`) at 900 s with
   e = 1/3, so `9 + 6e = 11` is integral (`n = 13` with 2 cores) -- the smallest e at which the
   frozen verifier can express the gain at all. ~0.5 CPU-h LP + ~0.25 CPU-h certification each.
2. The 40 s truncation is the dominant uncertainty in every pass count above; nothing here is a
   verdict until a 900 s solve reproduces it.
3. Out of scope, logged and unchecked: the certified K0-BLOCKED packings of d2front87 at
   4.03-4.36 and s0115 at 3.985 have side > s0 and are untouched by anything in this chore.
