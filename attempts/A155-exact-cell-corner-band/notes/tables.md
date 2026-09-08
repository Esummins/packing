# A155 — tables

All numbers from `results/`; the pads are `cells155.PADS` (a pad `w` is what a tree declared over
the slab `[s0 − T′, s0]` owes under Lemma K0-WIDEN, `w = (T′/(s0 − T′))(1 + √2/2)`).

## 0. Self-test

`results/band155_selftest.json`: the vectorised SAT gap agrees with A148's `geo148.sat_gap` to
6.7·10⁻¹⁶ over 400 random pairs; the float meet test agrees with A143's exact rational
`f_min_max` on 120/120; and `cells155.all_cells(A_W)` reproduces `cells143.all_cells()` box for box
at the full pad. The full-pad row below therefore re-derives A150's band (206) and A143's pair
census (11 772 canonical pairs, 81.9 % killed) from scratch.

## 1. The band vs the pad (T1)

| pad tag | pad w | slab T′ | cells | (B1) band | dead | alive pair cells / 11 772 | (P2) | (P1) | (P1s) | drawn → hits | exact x-checks | secs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `w0` | 0 | fixed side | 216 | **202** | 14 | 1 833 | 8 224 | 1 309 | 406 | 8 000 → 8 000 (0 misses) | 400 | 90 |
| `w5e-4` | 4.404·10⁻⁴ | 1·10⁻³ | 216 | **202** | 14 | 1 834 | 8 224 | 1 309 | 405 | 8 000 → 8 000 (0 misses) | 400 | 94 |
| `w2.6e-3` | 2.204·10⁻³ | 5·10⁻³ | 216 | **202** | 14 | 1 861 | 8 220 | 1 282 | 409 | 8 000 → 8 000 (0 misses) | 400 | 95 |
| `w1.3e-2` | 1.108·10⁻² | 2.5·10⁻² | 216 | **204** | 12 | 1 976 | 8 084 | 1 317 | 395 | 8 000 → 8 000 (0 misses) | 400 | 105 |
| `wmax` | 2.55101·10⁻² | whole window | 216 | **206** | 10 | 2 134 | 7 919 | 1 313 | 406 | 8 000 → 8 000 (0 misses) | 400 | 83 |

Band geometry is unchanged across pads: all six tilt windows present, 35 of 36 position cells at
`wmax`, 35 at pad 0; centre distance from the corner spans [0.7071, 2.4142] at pad 0 and
[0.7071, 2.4503] at `wmax`.

## 2. Pose-level occupancy — what the cover is throwing away (diagnostic, not a proof)

Per cell: 200 sampled realised first meeters × a common pool of 8 000 realised meeter poses;
`p` = fraction of first meeters with a witnessed interior-disjoint partner that also meets the box.

| pad | median p | cells with p = 0 | p < 0.1 | p = 1 | cells with no realised meeter at all |
|---|---|---|---|---|---|
| `w0` | 0.0125 | 90 | 112 | 24 | 16 |
| `w5e-4` | 0.0125 | 89 | 112 | 25 | 16 |
| `w2.6e-3` | 0.0175 | 88 | 112 | 25 | 16 |
| `w1.3e-2` | 0.0475 | 76 | 105 | 28 | 16 |
| `wmax` | 0.1625 | 64 | 93 | 33 | 16 |

**The pad multiplies the pose-level 2-crowd room by 13 (median 1.25 % → 16.25 %) and the sound band
by 1.02.** 42 % of the cells at pad 0 hold no witnessed 2-crowd and (B1) kills 6.5 % of them.

Cross-tabulation at pad 0 (`results/band155_occ_w0.json` against `band155_pairs_w0.json`):

* all **14** cells (B1) kills have p = 0 — the sound test never contradicts the sampler;
* **76** cells with p = 0 survive (B1) — the headroom a sharper rule would take;
* all **16** cells with no realised meeter at all survive (B1) and the container + reach clip:
  at level 1 the clip cannot see that a cell contains no meeter (at 12 × 12 × 6 it empties 92 of
  864 cells, so refinement does recover part of this).

## 3. What a finer cover converts (T1 addendum)

(B1) on a refined cover, same exact chain, same pad. `live` = cells the container + reach clip does
not empty.

| pad | cover | cells | live | band | dead (clip + B1) | branching vs level 1 |
|---|---|---|---|---|---|---|
| `w0` | 6 × 6 × 6 (level 1) | 216 | 216 | 202 | 14 (6.5 %) | ×1 |
| `w0` | 12 × 12 × 6 | 864 | 772 | **646** | 218 (25.2 %) | ×3.20 |
| `wmax` | 6 × 6 × 6 (level 1) | 216 | 216 | 206 | 10 (4.6 %) | ×1 |
| `wmax` | 12 × 12 × 6 | 864 | 772 | **678** | 186 (21.5 %) | ×3.29 |

| `w0` | 12 × 12 × 12 | 1 728 | 1 494 | **1 216** | 512 (29.6 %) | ×6.02 |

Refinement is a losing trade: the kill fraction rises 6.5 % → 25.2 % → 29.6 % while the cover grows
×4 and ×8, so the per-corner branching factor rises ×3.2 / ×6.0 and the four-corner product rises
×105 / ×1 300.

## 4. The four-corner product (T2)

Same kills, same transfer-matrix trace and Burnside quotient as A150. The `wmax` rows reproduce
`attempts/A150-four-corner-product/results/prod150_stages.json` and `prod150_pairs.json` digit for
digit (adjacent kills 648 / 816 / 266, diagonal 0 / 6 / 2, final 1 519 380 658 tuples and
189 934 236 orbits), which is the pipeline's validation.

| stage | pad 0 tuples | pad 0 orbits | pad 5e-4 tuples | pad 5e-4 orbits | full pad tuples | full pad orbits |
|---|---|---|---|---|---|---|
| 0 raw band product | 1 664 966 416 | 208 136 154 | 1 664 966 416 | 208 136 154 | 1 800 814 096 | 225 117 727 |
| 1 +(Q2) adjacent centre distance | 1 564 577 056 | 195 583 890 | 1 564 577 056 | 195 583 890 | 1 692 641 440 | 211 592 473 |
| 2 +(Q1) adjacent K′-vs-K′ | 1 498 460 040 | 187 319 078 | 1 498 460 040 | 187 319 078 | 1 561 731 694 | 195 228 403 |
| 3 +(Q1s) adjacent per-sub-bin | 1 455 261 840 | 181 919 024 | 1 455 539 308 | 181 953 708 | 1 519 799 378 | 189 986 576 |
| 4 +(Q2/Q1/Q1s) on both diagonals | **1 455 160 816** | **181 906 396** | **1 455 436 972** | **181 940 916** | **1 519 380 658** | **189 934 236** |

Per adjacent corner pair, of `band²`: pad 0 (of 40 804) (Q2) 624, (Q1) 422, (Q1s) 286 → 1 332
killed (3.26 %); full pad (of 42 436) 648 / 816 / 266 → 1 730 (4.08 %). Per diagonal pair: pad 0
2 kills, full pad 8. Vertical-mirror consistency of the adjacency matrix: True at every pad.

**The exact cell removes 4.2 % of the product** (1.519·10⁹ → 1.455·10⁹ tuples; 1.899·10⁸ → 1.819·10⁸
orbits), and the 10⁻³-slab pad is indistinguishable from the fixed side (+0.02 %).

## 5. The LP leg (T3) — gate not met, not run

The brief's gate was "pad-0 survivors < 50 000 orbits". Measured: **181 906 396 orbits**, 3 638×
over the gate, so the four-conditioned-square LP was **not run** and none of the 2 CPU-h LP cap was
spent. A150's measurement stands as the LP datum for this hypothesis: 13 fine-cover nodes at 240 s,
**7 converged kills (4 certified PASS by the frozen verifier), median η = −1.0**, against A143's
one-corner η = −0.044 / −0.633 / −0.000 (budget 10) and −0.083 / −0.077 (budget 9). Nothing in
A155's geometry changes the per-node LP: the cells at pad 0 and at the full pad differ by 2 % in
width, far inside the LP's own noise.

## 6. The slab-wise price (T4)

Window `[3.82, s0]`, width 0.057084. `docs/budget.md` §E's law `width_max = w_min·2^(48 − d_pose)`
has no k0_00 measurement; the measured spread over other classes is 0.0005 (k5_12, top of window) to
0.014 (k6_27).

| assumed width_max | slabs on the window | pad w(T′) each | band | orbits per slab | CPU-h per slab at A150's fine-cover rate | total |
|---|---|---|---|---|---|---|
| 0.057084 (one slab = the whole window, by dilation) | 1 | 2.55·10⁻² | 206 | 1.899·10⁸ | 5.28·10⁶ | **5.3·10⁶** |
| 0.012 (k6_07) | 5 | 5.3·10⁻³ | ~203 | ~1.82·10⁸ | 5.05·10⁶ | 2.5·10⁷ |
| 0.002 (k5_13) | 29 | 8.8·10⁻⁴ | 202 | 1.819·10⁸ | 5.05·10⁶ | 1.5·10⁸ |
| 0.001 | 58 | 4.4·10⁻⁴ | 202 | 1.819·10⁸ | 5.05·10⁶ | 2.9·10⁸ |
| 0.0005 (k5_12 at the top) | 115 | 2.2·10⁻⁴ | 202 | 1.819·10⁸ | 5.05·10⁶ | 5.8·10⁸ |

(CPU-h per slab = orbits × 100 s/node, A150's coarseness-ladder rate at the only cover fine enough
for the LP to decide; the interior tree is 12 000 CPU-h in the k0_00 row of `docs/budget.md`.)
**No slab is removed by A08's root certificate** (§4 of `composition.md`), and the bottom slab is
the same price as every other.
