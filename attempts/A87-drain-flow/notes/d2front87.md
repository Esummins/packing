# A87 chore: the SECOND-intruder frontier D2*(sigma) inside A85's 4-corner cover

`D2 = min_c d2(c)`, `d2(c)` = depth of the SECOND deepest intruder at corner c (depth = `1 - f_min_max` in the corner frame).  The deepest intruder `d1` is uninformative (deepfront87: a near-slot square buys `d1 = 1 - eps` at any side where the four gadgets fit, and the analytic trade is `d2 <~ eps^2/4`), so `d2` is the substantive variable for the PI conjecture.  Seeds here are A85's ENUMERATED corner pairs, not free-space gadgets.  Code `code/d2front87.py`.

## Frontier D2*(sigma) inside the A85 4-corner nodes

| cap sigma | nodes reaching the cap | best D2 (float) | certified D2 enclosure | certified sigma <= | min pair gap >= | n_block | EXTRAPOLATED |
| ---: | ---: | ---: | :--- | ---: | ---: | :--- | :--- |
| 4.600000 | 50 | 0.262173 | [0.262173390, 0.262173390] | 4.354390297132183 | 5.00e-10 | [2, 2, 2, 2] | no (certified) |
| 4.400000 | 49 | 0.292893 | [0.292892955, 0.292892955] | 4.357401801798346 | 5.00e-10 | [2, 2, 2, 2] | no (certified) |
| 4.200000 | 48 | 0.153937 | [0.153937360, 0.153937360] | 4.193714813209461 | 4.94e-10 | [2, 2, 2, 2] | no (certified) |
| 4.100000 | 45 | 0.077756 | [0.077756080, 0.077756080] | 4.09999999899874 | 4.46e-10 | [2, 2, 2, 2] | no (certified) |
| 4.050000 | 44 | 0.034241 | [0.034241000, 0.034241000] | 4.037927708990091 | 5.00e-10 | [2, 2, 2, 2] | no (certified) |
| 4.000000 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | **yes, unprobed** |
| 3.950000 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | **yes, unprobed** |
| 3.900000 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | **yes, unprobed** |
| 3.877084 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | **yes, unprobed** |
| (own side) | 52 | 0.184244 | [0.184243902, 0.184243902] | 5.197732463175858 | 5.00e-10 | [2, 2, 2, 2] | no (certified) |

The `own side` row is the best D2 at whatever side the node's own K0-confined compression actually reached -- the honest low-sigma point of this run.  One-corner ceiling for reference: `1 - 1/sqrt2 = 0.29289321881345`.

### (b) ANCHORED-ONLY frontier

The raw table above measures ghosts.  A near-slot gadget -- one square parked eps off its slot, the partner dipping a single vertex into the sliver -- is a legal K0-BLOCKED packing but not a Psi-minimal minimiser: the partner can rotate back toward flush and lift out at CONSTANT side, so nothing holds its intrusion.  A candidate is ANCHORED here iff (i) EVERY intruder of EVERY corner fails A90's RETREATABLE test (no constant-side cardinal translation of the intruder, or of its retreat cluster, reduces its intrusion -- `t3_90.analyse_square`, verbatim; A90's own `res_of` applies it only to non-deepest intruders, here it is applied to all), and (ii) the SHALLOWER intruder of each corner has no constant-side rotation TOWARD FLUSH about one of its own active contacts (or in place) that reduces its depth while the whole packing stays feasible.  Same exact verification as (a).

| cap sigma | rows scanned | anchored found | best anchored D2 (float) | certified D2 enclosure | certified sigma <= | n_block | EXTRAPOLATED |
| ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |
| 4.600000 | 47 | 2 | 0.000100 | [0.000100471, 0.000100471] | 4.083735886243449 | [2, 2, 2, 2] | no (certified) |
| 4.400000 | 49 | 1 | 0.000100 | [0.000099996, 0.000099996] | 4.083735459840951 | [2, 2, 2, 2] | no (certified) |
| 4.200000 | 48 | 1 | 0.000100 | [0.000099996, 0.000099996] | 4.083735459840951 | [2, 2, 2, 2] | no (certified) |
| 4.100000 | 45 | 1 | 0.000100 | [0.000099996, 0.000099996] | 4.083735459840951 | [2, 2, 2, 2] | no (certified) |
| 4.050000 | 44 | 0 | -- | NO ANCHORED CANDIDATE among the scanned rows | -- | -- | no |
| 4.000000 | 0 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | **yes, unprobed** |
| 3.950000 | 0 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | **yes, unprobed** |
| 3.900000 | 0 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | **yes, unprobed** |
| 3.877084 | 0 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | **yes, unprobed** |
| (own side) | 44 | 2 | 0.000100 | [0.000100000, 0.000100000] | 4.107107414606331 | [2, 2, 2, 2] | no (certified) |

**Procedure caveat, stated plainly.**  The anchoring test is applied as a FILTER over the ladder rows in descending raw D2 (up to 47 rows per cap), not as a constraint inside the ascent.  So row (b) is a certified LOWER bound on the anchored frontier and the raw row (a) an upper bound on it; an ascent that carried the retreat-blocking as a penalty could land between them.  A cap whose (b) cell says "NO ANCHORED CANDIDATE" is evidence that the raw optimum at that side is a ghost, not evidence that no anchored packing exists there.

### Which contacts block each intruder of the best ANCHORED candidate

**4.600000** (tag p094, certified sigma <= 4.083735886243449):

| corner | sq | depth | tilt (deg) | retreatable | e_x cluster: blocked by | e_y cluster: blocked by | shallower: rotation to flush free? |
| --- | ---: | ---: | ---: | :--- | :--- | :--- | :--- |
| BL | 0 | 0.263053544 | 0.614410 | no | wall [[3, 'x=s'], [6, 'x=s']]; sq [2, 9] | not a retreat direction | -- |
| BL | 1 | 0.257354679 | 0.614410 | no | wall [[3, 'x=s'], [6, 'x=s']]; intruder [{'sq': 7, 'corner': 'TR', 'depth': 0.00010072525003845811, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [0, 0, 4] | wall [[5, 'y=s'], [5, 'y=s']]; intruder [{'sq': 4, 'corner': 'TL', 'depth': 0.00010047149243552767, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [4] | no |
| BR | 2 | 0.279175354 | 0.684274 | no | wall [[1, 'x=0'], [4, 'x=0']]; intruder [{'sq': 0, 'corner': 'BL', 'depth': 0.26305354437154493, 'rate': 1.0, 'fd': 0.9999999994736442}]; sq [0, 9, 9] | wall [[5, 'y=s'], [5, 'y=s'], [7, 'y=s']]; intruder [{'sq': 4, 'corner': 'TL', 'depth': 0.00010047149243552767, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [0, 3, 3, 9, 9] | -- |
| BR | 3 | 0.261520641 | 0.684274 | no | not a retreat direction | wall [[7, 'y=s']]; sq [10, 10] | no |
| TL | 4 | 0.000100471 | 0.000240 | no | not a retreat direction | wall [[0, 'y=0'], [2, 'y=0']]; sq [1, 8] | no |
| TL | 5 | 0.581108763 | 0.000000 | no | wall [[3, 'x=s'], [6, 'x=s']]; intruder [{'sq': 7, 'corner': 'TR', 'depth': 0.00010072525003845811, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [8] | wall [[0, 'y=0'], [2, 'y=0']]; sq [4, 8] | -- |
| TR | 6 | 0.455665861 | 0.684274 | no | wall [[1, 'x=0'], [4, 'x=0']]; intruder [{'sq': 0, 'corner': 'BL', 'depth': 0.26305354437154493, 'rate': 1.0, 'fd': 0.9999999994736442}]; sq [7, 7, 10, 10] | wall [[0, 'y=0'], [2, 'y=0']]; intruder [{'sq': 3, 'corner': 'BR', 'depth': 0.2615206405955748, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [10, 10] | -- |
| TR | 7 | 0.000100725 | 0.684274 | no | wall [[1, 'x=0'], [4, 'x=0']]; sq [8, 8] | not a retreat direction | no |

**4.400000** (tag p094, certified sigma <= 4.083735459840951):

| corner | sq | depth | tilt (deg) | retreatable | e_x cluster: blocked by | e_y cluster: blocked by | shallower: rotation to flush free? |
| --- | ---: | ---: | ---: | :--- | :--- | :--- | :--- |
| BL | 0 | 0.263053358 | 0.614409 | no | wall [[3, 'x=s'], [6, 'x=s']]; sq [2, 9] | not a retreat direction | -- |
| BL | 1 | 0.257354475 | 0.614409 | no | wall [[3, 'x=s'], [6, 'x=s']]; intruder [{'sq': 7, 'corner': 'TR', 'depth': 9.999579197694786e-05, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [0, 0, 4] | wall [[5, 'y=s'], [5, 'y=s']]; intruder [{'sq': 4, 'corner': 'TL', 'depth': 9.999579147379478e-05, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [4] | no |
| BR | 2 | 0.279175232 | 0.684274 | no | wall [[1, 'x=0'], [4, 'x=0']]; intruder [{'sq': 0, 'corner': 'BL', 'depth': 0.2630533575268993, 'rate': 1.0, 'fd': 0.9999999994736442}]; sq [0, 9, 9] | wall [[5, 'y=s'], [5, 'y=s'], [7, 'y=s']]; intruder [{'sq': 4, 'corner': 'TL', 'depth': 9.999579147379478e-05, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [0, 3, 3, 9, 9] | -- |
| BR | 3 | 0.261520658 | 0.684274 | no | not a retreat direction | wall [[7, 'y=s']]; sq [10, 10] | no |
| TL | 4 | 0.000099996 | 0.000239 | no | not a retreat direction | wall [[0, 'y=0'], [2, 'y=0']]; sq [1, 8] | no |
| TL | 5 | 0.581109896 | 0.000000 | no | wall [[3, 'x=s'], [6, 'x=s']]; intruder [{'sq': 7, 'corner': 'TR', 'depth': 9.999579197694786e-05, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [8] | wall [[0, 'y=0'], [2, 'y=0']]; sq [4, 8] | -- |
| TR | 6 | 0.455666445 | 0.684274 | no | wall [[1, 'x=0'], [4, 'x=0']]; intruder [{'sq': 0, 'corner': 'BL', 'depth': 0.2630533575268993, 'rate': 1.0, 'fd': 0.9999999994736442}]; sq [7, 7, 10, 10] | wall [[0, 'y=0'], [2, 'y=0']]; intruder [{'sq': 3, 'corner': 'BR', 'depth': 0.26152065756594434, 'rate': 1.0, 'fd': 0.9999999983634211}]; sq [10, 10] | -- |
| TR | 7 | 0.000099996 | 0.684274 | no | wall [[1, 'x=0'], [4, 'x=0']]; sq [8, 8] | not a retreat direction | no |


## The barrier is upstream of packing: REALIZABILITY of a cover pair

A85's pair prune never saw the CONTAINER WALLS (k0dir87's own note), so a surviving cover pair need not admit an actual pair of disjoint unit squares that both fit inside the corner (`cx, cy >= h(theta)`) and both meet the open unit slot.  On a 11 x 11 x 15 pose grid per box, **856 of 6000** scanned surviving pairs do (>= 0.1427 of the census; a grid verdict, so this is a LOWER bound on the realizable fraction).  Witness d2 over the realizable pairs: min 0.0010, median 0.0683, max 0.2749.

The consequence for the SAMPLED 4-corner nodes is decisive: a node needs all FOUR of its independently drawn pairs realizable, and **0 of the 179 attemptable nodes** clear that.  Realizable-corner histogram over the 179 nodes: 0 corners: 96, 1 corners: 71, 2 corners: 11, 3 corners: 1, 4 corners: 0.

So the ascent is run on a second arm as well (ARM 2): 4-corner nodes SYNTHESISED from the realizable pairs only and then classified by gate85's own fast gate at budget 3.  Of 3864 such draws, {"attemptable": 150, "unkillable": 23, "contradictory": 3691} -- i.e. the binding constraint on a realizable 4-corner node is core CONTRADICTION (two corners' cover cores meeting), not the alive gate.

## The packing barrier

51 of 150 attemptable 4-corner nodes were attempted; 51 yielded a feasible K0-BLOCKED packing at all (seed + compression).  Minimum enclosing side reached, over those: min 4.000002, median 4.000373, max 5.194238.

| side threshold | nodes with a K0-BLOCKED packing at <= that side |
| ---: | ---: |
| 4.600000 | 48 |
| 4.400000 | 48 |
| 4.200000 | 47 |
| 4.100000 | 44 |
| 4.050000 | 42 |
| 4.000000 | 0 |
| 3.950000 | 0 |
| 3.900000 | 0 |
| 3.877084 | 0 |

| min-side bin | nodes |
| --- | ---: |
| [0.00,3.90) | 0 |
| [3.90,3.95) | 0 |
| [3.95,4.00) | 0 |
| [4.00,4.05) | 42 |
| [4.05,4.10) | 2 |
| [4.10,4.20) | 3 |
| [4.20,4.40) | 1 |
| [4.40,99.00) | 3 |

## Per-corner detail of the best certified configuration

| row | corner | n_block | d1 | tilt of d1 (deg) | d2 | tilt of d2 (deg) | still in its cover box? |
| --- | --- | ---: | ---: | ---: | ---: | ---: | :--- |
| 4.600000 | BL | 2 | 0.300929957 | 42.653215 | 0.273145284 | 42.574664 | False / False |
| 4.600000 | BR | 2 | 0.262229662 | 35.972046 | 0.262173390 | 35.972046 | False / False |
| 4.600000 | TL | 2 | 0.301475360 | 44.588985 | 0.268031240 | 44.605487 | False / False |
| 4.600000 | TR | 2 | 0.265353741 | 37.415492 | 0.264861402 | 37.182092 | False / False |
| 4.400000 | BL | 2 | 0.292893322 | 44.999987 | 0.292893084 | 44.999988 | False / False |
| 4.400000 | BR | 2 | 0.292893204 | 44.999985 | 0.292893096 | 44.999996 | False / False |
| 4.400000 | TL | 2 | 0.292892988 | 44.999978 | 0.292892955 | 44.999982 | False / False |
| 4.400000 | TR | 2 | 0.292893187 | 44.999988 | 0.292893163 | 44.999996 | False / False |
| 4.200000 | BL | 2 | 0.345403055 | 32.204838 | 0.154481927 | 32.204838 | False / False |
| 4.200000 | BR | 2 | 0.387293021 | 37.981218 | 0.155385224 | 37.981218 | False / True |
| 4.200000 | TL | 2 | 0.313624418 | 20.705524 | 0.154806335 | 20.705524 | False / False |
| 4.200000 | TR | 2 | 0.155240816 | 1.700245 | 0.153937360 | 14.647316 | False / False |
| 4.100000 | BL | 2 | 0.453486641 | 0.000000 | 0.077756080 | 16.547350 | False / False |
| 4.100000 | BR | 2 | 0.082160816 | 4.114173 | 0.081593268 | 5.532967 | False / False |
| 4.100000 | TL | 2 | 0.251774716 | 23.948936 | 0.177591506 | 24.233980 | False / False |
| 4.100000 | TR | 2 | 0.378625186 | 5.343952 | 0.081219055 | 10.995937 | False / False |
| 4.050000 | BL | 2 | 0.034248518 | 2.255854 | 0.034245224 | 2.255722 | False / False |
| 4.050000 | BR | 2 | 0.440245837 | 0.000000 | 0.037196463 | 4.404052 | False / False |
| 4.050000 | TL | 2 | 0.361898961 | 0.000001 | 0.034241000 | 3.383997 | False / False |
| 4.050000 | TR | 2 | 0.521865820 | 0.002067 | 0.053238312 | 9.821011 | False / False |
| own side | BL | 2 | 0.184411877 | 0.000000 | 0.184243902 | 27.054884 | False / False |
| own side | BR | 2 | 0.277892915 | 25.368454 | 0.193603741 | 25.368012 | False / False |
| own side | TL | 2 | 0.198633479 | 19.237343 | 0.195372323 | 18.613573 | False / False |
| own side | TR | 2 | 0.210176937 | 23.322266 | 0.196033901 | 37.444412 | False / False |

## The pair-census cut: what "d2 < delta at some corner" would buy

Per BOX (the 644 sound BL cover boxes).  `depth_ub(b) = 1 - min_b f_min_max` is a SOUND upper bound on the depth of any square placed in b, hence on `d2` when that square is the shallower of the corner's two intruders -- "the max d2 this box can host".

| statistic | boxes (n = 644) | surviving pairs (n = 33656) | attemptable pairs (n = 1610) |
| --- | ---: | ---: | ---: |
| min | -0.256718 | -0.256718 | -0.256718 |
| median | 0.244336 | 0.027800 | 0.027800 |
| mean | 0.288163 | 0.018570 | 0.015233 |
| max | 1.000000 | 0.499103 | 0.329570 |
| fraction < 0.05 | 0.1879 | 0.5589 | 0.5919 |
| fraction < 0.10 | 0.3028 | 0.8193 | 0.8286 |
| fraction < 0.20 | 0.4130 | 0.9120 | 0.9534 |
| count < 0.05 | 121 | 18809 | 953 |
| count < 0.10 | 195 | 27575 | 1334 |
| count < 0.20 | 266 | 30695 | 1535 |
| fraction <= 0 (cannot meet the slot at all) | 0.1304 | 0.4418 | 0.4311 |
| fraction >= the one-corner ceiling 0.292893 | 0.4503 | 0.0120 | 0.0031 |

`d2_ub(i,j) = min(depth_ub(i), depth_ub(j))` for a pair, because BOTH members must be deep for the SECOND intruder to be.  A pair with `d2_ub < delta` CANNOT host `d2 >= delta`, so a 4-corner node using it at any corner is settled for free by a "d2 < delta at some corner" hypothesis; the residual is the complement.

Restricted to the REALIZABLE pairs (n = 856): `d2_ub` min 0.008127, median 0.094409, max 0.372186, fraction < 0.05 / 0.10 / 0.20 = 0.0350 / 0.6063 / 0.7558; and the grid witness ACHIEVES d2 with median 0.068274, max 0.274924 (never above its box bound -- max excess -2.20e-05), so for these pairs the ceiling and an attained value bracket the truth.

| d2_ub bin | boxes | surviving pairs | attemptable pairs |
| --- | ---: | ---: | ---: |
| -1..0 | 84 | 14869 | 694 |
| 0..0.02 | 10 | 1251 | 68 |
| 0.02..0.05 | 27 | 2689 | 191 |
| 0.05..0.1 | 74 | 8766 | 381 |
| 0.1..0.15 | 36 | 2129 | 145 |
| 0.15..0.2 | 35 | 991 | 56 |
| 0.2..0.25 | 60 | 2299 | 64 |
| 0.25..0.2929 | 28 | 257 | 6 |
| 0.2929..0.4 | 79 | 372 | 5 |
| 0.4..0.6 | 124 | 33 | 0 |
| 0.6..0.8 | 61 | 0 | 0 |
| 0.8..1.01 | 26 | 0 | 0 |

At NODE level (the 179 attemptable 4-corner nodes): `min_c d2_ub` has min -0.256718, median -0.108390, max 0.066923, and the number of nodes that could host `d2 >= delta` at ALL FOUR corners is

| delta | nodes that can host d2 >= delta at all 4 corners | cut by "d2 < delta somewhere" |
| ---: | ---: | ---: |
| 0.05 | 9 / 179 | 170 |
| 0.10 | 0 / 179 | 179 |
| 0.20 | 0 / 179 | 179 |
| 0.30 | 0 / 179 | 179 |

## Node recovery

gate85 stores only 200 of its 1000 sampled 4-corner nodes.  Its RNG stream is replayed here and VERIFIED against those 200 stored records (exact match on every node), so all 1000 nodes were re-classified with gate85's own fast gate: {"attemptable": 179, "unkillable": 2, "contradictory": 819} -- recovering the full attemptable set (the file's own counts: {"attemptable": [179, 0.179], "unkillable": [2, 0.002], "contradictory": [819, 0.819]}).

## Canary

Trump's TL 2-crowd, same code path: `d1 = 0.16832098955` (reference 0.16832098955, |diff| 2.53e-13), `d2 = 0.155474724` (reference 0.155475, |diff| 2.76e-07).  Trump is K0-FREE overall (BL / BR / TR each hold one flush slot square, `d1 = 1`), so it enters only as a per-corner check.

Both TL squares were located in the BL cover: `d2_ub` of the located pair = 0.224845 >= the actual `d2` = 0.155475 (slack 0.069370), so the box bound is SOUND on Trump.  Boxes: [51, 275], [366, 456].

## What this does and does not settle

* **Reached (certified).**  caps 4.600000, 4.400000, 4.200000, 4.100000, 4.050000
* **Unreached (EXTRAPOLATED / unprobed).**  caps 4.000000, 3.950000, 3.900000, 3.877084  Rows marked "**yes, unprobed**" above carry NO evidence: the obstruction is the PACKING barrier measured in the table above, not a depth ceiling, and nothing in this run licenses continuing the D2 curve into them.
* **Sound in the opposite direction, at exactly s_hat.**  The pair-census cut above is an UPPER bound valid over the whole cover box, so every "cannot host" line in it EXCLUDES the corresponding d2, at the s_hat scale, with no search involved.

## Provenance

* 51 nodes attempted of 150 attemptable, seed 20260903, 2542 s search + certification (2556 s total).  0 seed/error failures.
* Every certified row: rational z (`k0dir87.x_to_z` / `zfrac_of`), interval SAT gaps certified > 0 and side an outward interval UPPER bound (`fjpolish87.verify_exact`), blocker counts against the INNER rational slot rectangle (`k0dir87.exact_blocked_test`), depths as outward-rounded interval enclosures (`depthdist87.corner_depths`).
* Files: `results/d2front87.{json,jsonl,nodes.json,census.json,canary.json}`; log `logs/d2front87.run.log`.
* One process, OMP_NUM_THREADS=1.  No A57 / A60 / A61 file or process touched; nothing committed.
