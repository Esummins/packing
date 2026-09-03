# A87 chore: how deep do the intruders of a K0-BLOCKED packing get?

## Headline

Packings with `min_c d1(c) >= delta` (over the 5 exact-verified K0-BLOCKED packings A87 has):

| delta | 0.3 | 0.5 | 0.7 | 0.9 |
| --- | ---: | ---: | ---: | ---: |
| count | 0 | 0 | 0 | 0 |

* deepest corner over the corpus: `max_c d1` in [0.796823, 0.999750], median 0.943224
* shallowest corner: `min_c d1` in [0.000351634, 0.0997483], median 0.00929696
* NO packing has all four corners deep at any of the four deltas.
* certified: every depth is an interval enclosure of width <= 2.8e-39

## Per packing (sorted by sigma)

| tag | sigma | d1 BL | d1 BR | d1 TL | d1 TR | max_c d1 | min_c d1 | min_c d2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0115 | 3.985483724948 | 0.226665 | 0.0997483 | 0.99975 | 0.406017 | 0.999750 | 0.099748 | 8.038e-09 |
| s0380 | 4.000000117652 | 0.067889 | 0.943224 | 0.000351634 | 0.817657 | 0.943224 | 0.000352 | 4.643e-07 |
| s0076 | 4.000004058461 | 0.975698 | 0.947723 | 0.00929696 | 0.20144 | 0.975698 | 0.009297 | 0.0001 |
| s0380 | 4.000007451494 | 0.0689421 | 0.940712 | 0.000445151 | 0.818252 | 0.940712 | 0.000445 | 0.0001 |
| s0259 | 4.000011859830 | 0.314327 | 0.796823 | 0.057362 | 0.0627222 | 0.796823 | 0.057362 | 9.057e-05 |

sigma vs min_c d1: Pearson -0.8426, Spearman -0.1; the LOWEST-sigma packing is also the deepest-at-every-corner one.

## Full per-corner detail (d1 / d2 of every corner)

| tag | corner | #blockers | d1 | sq | tilt of d1 (deg) | d2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| s0115 | BL | 2 | 0.226665 | 1 | 18.9334 | 0.0147271 |
| s0115 | BR | 2 | 0.0997483 | 2 | 18.9334 | 0.0145163 |
| s0115 | TL | 2 | 0.99975 | 5 | 0.005911 | 8.03787e-09 |
| s0115 | TR | 2 | 0.406017 | 7 | 5.25256e-07 | 1.73658e-08 |
| s0380 | BL | 2 | 0.067889 | 0 | 3.45024e-05 | 4.64273e-07 |
| s0380 | BR | 2 | 0.943224 | 3 | 0.0201549 | 1.97931e-05 |
| s0380 | TL | 2 | 0.000351634 | 5 | 0.0201549 | 2.98104e-05 |
| s0380 | TR | 2 | 0.817657 | 6 | 0.00207499 | 6.56185e-06 |
| s0076 | BL | 2 | 0.975698 | 0 | 0.466816 | 0.0001 |
| s0076 | BR | 2 | 0.947723 | 2 | 0.116118 | 0.0001 |
| s0076 | TL | 2 | 0.00929696 | 4 | 0.524511 | 0.0019425 |
| s0076 | TR | 2 | 0.20144 | 6 | 16.9978 | 0.0511354 |
| s0380 | BL | 2 | 0.0689421 | 0 | 0.00615424 | 0.0001 |
| s0380 | BR | 2 | 0.940712 | 3 | 0.126064 | 0.000109734 |
| s0380 | TL | 2 | 0.000445151 | 4 | 0.00540534 | 0.0001 |
| s0380 | TR | 2 | 0.818252 | 6 | 0.000525691 | 0.0001 |
| s0259 | BL | 2 | 0.314327 | 0 | 9.23324 | 0.0784934 |
| s0259 | BR | 2 | 0.796823 | 3 | 1.10601 | 0.00342537 |
| s0259 | TL | 2 | 0.057362 | 4 | 0.00522115 | 9.09703e-05 |
| s0259 | TR | 2 | 0.0627222 | 7 | 0.00468779 | 9.05715e-05 |
| trump | BL | 1 | 1 | 0 | 1.88407e-70 | -- |
| trump | BR | 1 | 1 | 2 | 2.11595e-70 | -- |
| trump | TL | 2 | 0.168321 | 6 | 40.1819 | 0.155475 |
| trump | TR | 1 | 1 | 5 | 1.88056e-69 | -- |

## Tilt of the deepest intruder vs its depth

**K0-BLOCKED packings only** (n = 20).  Pearson -0.2866, Spearman 0.06767.  tilt in [5.253e-07, 18.93] deg, depth in [0.0003516, 0.9997].

| tilt bin (deg) | n | depth min | depth mean | depth max |
| --- | ---: | ---: | ---: | ---: |
| (0,1e-6] | 1 | 0.406017 | 0.406017 | 0.406017 |
| (1e-6,1e-3] | 2 | 0.067889 | 0.44307 | 0.818252 |
| (1e-3,0.1] | 8 | 0.000351634 | 0.368807 | 0.99975 |
| (0.1,1] | 4 | 0.00929696 | 0.718358 | 0.975698 |
| (1,5] | 1 | 0.796823 | 0.796823 | 0.796823 |
| (5,15] | 1 | 0.314327 | 0.314327 | 0.314327 |
| (15,30] | 3 | 0.0997483 | 0.175951 | 0.226665 |

**all rows incl. the canary** (n = 24).  Pearson -0.3365, Spearman -0.2974.  tilt in [1.884e-70, 40.18] deg, depth in [0.0003516, 1].

| tilt bin (deg) | n | depth min | depth mean | depth max |
| --- | ---: | ---: | ---: | ---: |
| exactly 0 | 3 | 1 | 1 | 1 |
| (0,1e-6] | 1 | 0.406017 | 0.406017 | 0.406017 |
| (1e-6,1e-3] | 2 | 0.067889 | 0.44307 | 0.818252 |
| (1e-3,0.1] | 8 | 0.000351634 | 0.368807 | 0.99975 |
| (0.1,1] | 4 | 0.00929696 | 0.718358 | 0.975698 |
| (1,5] | 1 | 0.796823 | 0.796823 | 0.796823 |
| (5,15] | 1 | 0.314327 | 0.314327 | 0.314327 |
| (15,30] | 3 | 0.0997483 | 0.175951 | 0.226665 |
| (30,45] | 1 | 0.168321 | 0.168321 | 0.168321 |

## A85 4-corner gate samples: can all four boxes host a deep d1?

Box-level UPPER bound (sound over the whole cover box): d1_ub(c) = max over the corner pair of depth_ub(box).  200 stored 4-corner nodes, 30 attemptable.

| delta | attemptable nodes that CAN host d1 >= delta at all 4 corners | fraction | ... and d2 >= delta at all 4 | fraction | all 200 nodes frac |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.3 | 12 / 30 | 0.4000 | 0 / 30 | 0.0000 | 0.2800 |
| 0.5 | 2 / 30 | 0.0667 | 0 / 30 | 0.0000 | 0.0600 |
| 0.7 | 0 / 30 | 0.0000 | 0 / 30 | 0.0000 | 0.0150 |
| 0.9 | 0 / 30 | 0.0000 | 0 / 30 | 0.0000 | 0.0000 |

Per-box depth upper bound over the 644 sound BL cover boxes: min -0.2567, mean 0.2882, max 1; fraction with depth_ub >= delta: 0.3: 0.4488, 0.5: 0.2267, 0.7: 0.0792, 0.9: 0.0155

Marginal over the 1610 attemptable BL pairs of the pair_states census: fraction with a deep-capable member / with both deep-capable: 0.3: 1.0000 / 0.0031, 0.5: 1.0000 / 0.0000, 0.7: 0.7255 / 0.0000, 0.9: 0.2795 / 0.0000

## Reading

* **Every K0-BLOCKED packing A87 has is deep at ONE OR TWO corners and razor-thin at another.**  `max_c d1` never drops below 0.7968 (four of the five have a corner intruded past 0.94, i.e. essentially to the corner point), while `min_c d1` never exceeds 0.09975.  The four counts at delta = 0.3 / 0.5 / 0.7 / 0.9 are all ZERO: there is no deep-at-all-four-corners packing in the corpus, and the corpus misses the FIRST threshold by a factor of 3.
* **The second intruder is what is thin, everywhere.**  `min_c d2` is at most 1e-4 in every packing but s0115, where it is 8e-9 -- i.e. the K0 row sits on (or below) the constrained pass's artificial depth floor EPS_KEEP = 1e-4.  The four stuck endpoints are boundary points of the CONSTRAINED problem, exactly as notes/k0dir87.md reports; s0115 is the only row where the second intruders are held by the packing (BL/BR d2 = 1.47e-2 / 1.45e-2) rather than by the floor -- and even there TL/TR second intruders are at 8e-9 / 1.7e-8.
* **Deep does NOT mean high sigma -- if anything the reverse, on this corpus.**  The lowest-sigma packing (s0115, sigma = 3.9855) is also the one with the largest `min_c d1` and the largest `max_c d1`; Pearson corr(sigma, min_c d1) = -0.8426.  But the correlation is an artefact of the cluster: the other four all sit at sigma = 4.0000000-4.0000119, so the rank correlation is only -0.1.  The honest statement is that the corpus gives NO evidence that four-corner depth costs side, and one data point (s0115) against it.
* **Tilt of the deepest intruder does not predict its depth.**  Over the 20 K0-BLOCKED corners, Pearson -0.2866 / Spearman 0.06767 -- a weak NEGATIVE trend at best: the three deepest-corner rows (0.9757, 0.9432, 0.9407) have tilts 0.47, 0.020 and 0.126 deg, i.e. nearly axis-aligned squares shoved into the corner, while the only two rows with tilt above 15 deg have depth 0.0997 and 0.2267.  Trump's genuine 2-crowd is the extreme of the other kind: tilt 40.18 deg at depth 0.1683.
* **The A85 box bound says the geometry is not the obstruction at 0.3, and is at 0.7.**  40.0% of attemptable 4-corner nodes could host d1 >= 0.3 at all four corners and 6.7% could at 0.5, but NONE could at 0.7 or 0.9 -- and 0% could host the SECOND intruder at 0.3 at all four corners.  Since this is an UPPER bound, "0" is a hard exclusion: no attemptable 4-corner node in the stored sample admits a packing with min_c d1 >= 0.7.  The contrast with the flow corpus (which cannot even reach 0.3) is the size of the gap between what the boxes permit and what a feasible packing achieves.
* **Caveat on n.**  Five packings and 30 attemptable stored nodes.  These are the only A87/A85 rows that carry both a rational z (or a sound box) and an exact verdict; everything else along the 520 flows is float and was NOT counted.

## m1 / m2 in k0dir87 are a proxy for d1 / d2, not equal to them

k0dir87 m1/m2 = -(SAT gap) = the smallest separating translation along one of the 4 candidate axes; the A89 depth is 1 - f_min_max, the reach towards the corner POINT.  They coincide whenever the binding SAT axis is an axis of the slot and the binding vertex is the one nearest the corner, which is most but not all of the time -- so the m1/m2 columns of k0dir87.deep.jsonl are a good PROXY for d1/d2 but not equal to them.

| tag | corner | A89 d1 | stored m1 | A89 d2 | stored m2 |
| --- | --- | ---: | ---: | ---: | ---: |
| s0115 | BL | 0.226665 | 0.226665 | 0.0147271 | 0.0147271 |
| s0115 | BR | 0.0997483 | 0.115406 | 0.0145163 | 0.0145163 |
| s0115 | TL | 0.99975 | 0.999853 | 8.03787e-09 | 8.03787e-09 |
| s0115 | TR | 0.406017 | 0.406017 | 1.73658e-08 | 1.73658e-08 |
| s0380 | BL | 0.067889 | -- | 4.64273e-07 | 4.64273e-07 |
| s0380 | BR | 0.943224 | -- | 1.97931e-05 | 1.97931e-05 |
| s0380 | TL | 0.000351634 | -- | 2.98104e-05 | 2.98104e-05 |
| s0380 | TR | 0.817657 | -- | 6.56185e-06 | 6.56185e-06 |
| s0076 | BL | 0.975698 | -- | 0.0001 | 0.0001 |
| s0076 | BR | 0.947723 | -- | 0.0001 | 0.0001 |
| s0076 | TL | 0.00929696 | -- | 0.0019425 | 0.0019425 |
| s0076 | TR | 0.20144 | -- | 0.0511354 | 0.0539455 |
| s0380 | BL | 0.0689421 | -- | 0.0001 | 0.0001 |
| s0380 | BR | 0.940712 | -- | 0.000109734 | 0.000109734 |
| s0380 | TL | 0.000445151 | -- | 0.0001 | 0.0001 |
| s0380 | TR | 0.818252 | -- | 0.0001 | 0.0001 |
| s0259 | BL | 0.314327 | -- | 0.0784934 | 0.0784934 |
| s0259 | BR | 0.796823 | -- | 0.00342537 | 0.00342537 |
| s0259 | TL | 0.057362 | -- | 9.09703e-05 | 9.09703e-05 |
| s0259 | TR | 0.0627222 | -- | 9.05715e-05 | 9.05715e-05 |

largest |d1 - m1| over the rows that store m1: 0.01566; largest |d2 - m2|: 0.00281; 16 of the 20 m2 columns agree to 1e-12.

## Canary

Trump at sigma 3.877083590023, certified n_block [1, 1, 2, 1]: 

* BL: blockers [0], d1 = 1 (square 0, tilt 1.88407e-70 deg), d2 = --
* BR: blockers [2], d1 = 1 (square 2, tilt 2.11595e-70 deg), d2 = --
* TL: blockers [4, 6], d1 = 0.16832098955 (square 6, tilt 40.1819 deg), d2 = 0.155475
* TR: blockers [5], d1 = 1 (square 5, tilt 1.88056e-69 deg), d2 = --

Handled by exactly the same code path: the three 1-crowd corners come out at depth 1 (a flush slot square reaches the corner point, f_min_max = 0) and TL at 0.168321, matching A89 t2b_depth's exact Decimal value.  Trump is K0-FREE, so it has no min_c d1 and is excluded from every count above.
