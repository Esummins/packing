# A87 chore: directed critical-point search INSIDE K0-BLOCKED

## Headline

* Fritz-John points found inside K0-BLOCKED: **0**.
* Lowest sigma of a K0-BLOCKED FJ point: **None (none exists in the sample)**.
* Lowest sigma reached by ANY K0-BLOCKED packing along any flow: **3.985483724948** (tag s0115), exact per-corner n_block [2, 2, 2, 2], pair-disjointness certified True, certified side upper bound 3.985483724948.
* s_hat = 3.877083590023, s0 = 3.877084000000.

## Counts

| quantity | value |
| --- | ---: |
| n_seeds_attempted | 520 |
| n_seeds_built | 520 |
| n_seed_failed | 0 |
| n_exited | 520 |
| n_no_exit | 0 |
| n_constrained_slack | 7 |
| n_critical_in_region | 484 |
| n_polished | 26 |
| n_fj_at_tight_tol | 17 |
| n_polished_still_K0_BLOCKED_exact | 4 |
| n_fj_points_K0_BLOCKED_exact | 0 |
| deep.n | 18 |
| deep.min_sigma | 3.985483724948471 |
| deep.n_k0_rows_slack | 2 |
| deep.n_critical_in_region | 17 |
| deep.min_release_drop | 0.0 |

## Deep re-runs (lowest confined endpoints, K0 rows then released)

| tag | sigma_deep | steps | min k0 row | release drop | rel steps | n_block | depths (m2) |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| s0115 | 3.985483725 | 57 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0147 0.0145 0.0000 0.0000 |
| s0075 | 4.000000000 | 59 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0000 0.0000 0.0000 0.0000 |
| s0200 | 4.000000000 | 89 | -1.00e-04 | 7.01e-11 | 1 | [2, 2, 2, 2] | 0.0000 0.0000 0.0000 0.0631 |
| s0479 | 4.000000000 | 73 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0000 0.0000 0.1147 0.0000 |
| s0191 | 4.000000000 | 51 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0000 0.0000 0.0000 0.0000 |
| s0145 | 4.000000001 | 156 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.1120 0.0000 0.0000 0.0000 |
| s0259 | 4.000000001 | 55 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0825 0.0000 0.0000 0.0000 |
| s0295 | 4.000000001 | 38 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0000 0.0692 0.0000 0.0000 |
| s0461 | 4.000000002 | 37 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0000 0.1718 0.0000 0.0000 |
| s0006 | 4.000000010 | 95 | -1.00e-04 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0000 0.1767 0.0000 0.0000 |
| s0046 | 4.000000064 | 29 | -9.91e-05 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0000 0.0000 0.0000 0.0008 |
| s0038 | 4.000000155 | 0 | 1.95e-09 | 0.00e+00 | 0 | [2, 2, 2, 2] | 0.0124 0.0004 0.0001 0.0001 |

## Exit sigmas

| stat | sigma |
| --- | ---: |
| min | 4.008229780 |
| p10 | 4.233530832 |
| median | 4.738620117 |
| p90 | 5.079817977 |
| max | 5.294980351 |

| bin lo | bin hi | count |
| ---: | ---: | ---: |
| 4.008230 | 4.115459 | 18 |
| 4.115459 | 4.222688 | 28 |
| 4.222688 | 4.329917 | 37 |
| 4.329917 | 4.437147 | 48 |
| 4.437147 | 4.544376 | 34 |
| 4.544376 | 4.651605 | 43 |
| 4.651605 | 4.758834 | 61 |
| 4.758834 | 4.866063 | 74 |
| 4.866063 | 4.973293 | 65 |
| 4.973293 | 5.080522 | 61 |
| 5.080522 | 5.187751 | 31 |
| 5.187751 | 5.294980 | 20 |

## Exit modes / corner

| mode | count |
| --- | ---: |
| blocker_slid_away | 520 |

| corner freed | count |
| --- | ---: |
| BR | 232 |
| TL | 190 |
| TR | 68 |
| BL | 30 |

## Lowest K0-BLOCKED sigma per seed

min 3.987168384, median 4.011680308

| bin lo | bin hi | count |
| ---: | ---: | ---: |
| 3.987168 | 4.029108 | 334 |
| 4.029108 | 4.071048 | 69 |
| 4.071048 | 4.112987 | 34 |
| 4.112987 | 4.154927 | 31 |
| 4.154927 | 4.196867 | 24 |
| 4.196867 | 4.238806 | 11 |
| 4.238806 | 4.280746 | 5 |
| 4.280746 | 4.322686 | 5 |
| 4.322686 | 4.364625 | 1 |
| 4.364625 | 4.406565 | 1 |
| 4.406565 | 4.448505 | 4 |
| 4.448505 | 4.490444 | 1 |

## Polished points: exact min_n_block over the four slots

| min_n_block | count |
| ---: | ---: |
| 0 | 5 |
| 1 | 17 |
| 2 | 4 |


## The two disjoint outcomes of the polish (the mechanism)

Every one of the 26 polished endpoints falls into exactly one of two classes, and the classes do not intersect.

**(a) FJ at tol 1e-6 -> K0-FREE.**  17 of 26.  Every single one has some corner slot met by at most ONE square, so it is K0-FREE by teleport.

| tag | sigma | exact per-corner n_block (BL BR TL TR) | min |
| --- | ---: | --- | ---: |
| s0075 | 4.000000000060 | [1, 0, 2, 1] | 0 |
| s0200 | 4.000000000030 | [0, 1, 1, 2] | 0 |
| s0479 | 4.000000000030 | [1, 0, 2, 1] | 0 |
| s0191 | 4.000000000030 | [2, 1, 1, 1] | 1 |
| s0145 | 4.000000000060 | [2, 1, 1, 0] | 0 |
| s0259 | 4.000000000030 | [2, 1, 1, 1] | 1 |
| s0295 | 4.000000000060 | [1, 2, 1, 1] | 1 |
| s0461 | 4.000000000030 | [1, 2, 0, 1] | 0 |
| s0006 | 4.000000000030 | [1, 2, 1, 1] | 1 |
| s0038 | 4.000000000030 | [2, 1, 1, 2] | 1 |
| s0088 | 4.000000000060 | [2, 1, 1, 1] | 1 |
| s0029 | 4.000000000030 | [2, 1, 1, 2] | 1 |
| s0237 | 4.000000000061 | [1, 1, 2, 1] | 1 |
| s0115 | 3.985466720909 | [2, 2, 1, 1] | 1 |
| s0029 | 4.000000000032 | [2, 1, 1, 2] | 1 |
| s0191 | 4.000000000030 | [2, 1, 2, 1] | 1 |
| s0479 | 4.000000000030 | [1, 1, 2, 2] | 1 |

**(b) still K0-BLOCKED -> NOT FJ.**  4 of 26.  Every one has a strictly positive cone residual, and its shallowest second intruder sits on the artificial depth floor EPS_KEEP = 1e-4 (or below): these are boundary points of the CONSTRAINED problem, held up by the K0 row and not by the packing.

| tag | sigma | cone residual (1e-6) | m_active | rank33 | d_H | rattlers | second-blocker depths BL BR TL TR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| s0380 | 4.000000117652 | 2.095e-04 | 29 | 29 | 4 | 0 | 4.643e-07 1.979e-05 2.981e-05 6.562e-06 |
| s0076 | 4.000004058461 | 1.208e-02 | 20 | 20 | 13 | 0 | 1.000e-04 1.000e-04 1.942e-03 5.395e-02 |
| s0380 | 4.000007451494 | 4.293e-02 | 18 | 18 | 15 | 0 | 1.000e-04 1.097e-04 1.000e-04 1.000e-04 |
| s0259 | 4.000011859830 | 7.466e-02 | 18 | 18 | 15 | 0 | 7.849e-02 3.425e-03 9.097e-05 9.057e-05 |

## Reading

* **No Fritz-John point of the enclosing-side function was found inside K0-BLOCKED, at any side.**  The search was seeded 520 times STRICTLY inside the region (two intruders per corner by construction) and the descent was run both free (with the region as a monitor) and confined to the region by constraint.

* The obstruction is uniform and structural: the last increment of side always has to come from one corner giving up its second intruder.  All 520 free flows left the region, all 520 by the same mode -- a blocker SLIDING AWAY, never by the slot squares rearranging -- and the confined flows all converge onto the K0-BLOCKED boundary with the shallowest intrusion depth driven to the floor.

* Walking the depth floor down 1e-4 -> 1e-8 in the deep pass pushes 17 of 18 endpoints onto sigma = 4.000000000 exactly, with the second-blocker depth going to 0 -- i.e. sigma = 4 is the infimum of the side over the K0-BLOCKED region for that whole basin, and it is attained only in the CLOSURE, where the corner drops to one blocker and the point becomes K0-FREE.

* One basin (s0115) does better: a genuinely K0-BLOCKED, exactly verified packing at sigma = 3.985483724948 with all four slots doubly met (BL/BR intrusion depths 1.47e-2 / 1.45e-2, TL/TR 8.0e-9 / 1.7e-8).  Its own FJ polish leaves the region (n_block [2, 2, 1, 1] at sigma 3.985466720909), again by TL/TR shedding their second intruder.

* Everything found is comfortably above s_hat = 3.877083590023: the lowest K0-BLOCKED packing seen anywhere is 3.9854837, a gap of 1.08e-1 above s_hat.

* Caveat on scope: this is a numerical SEARCH, not a proof of non-existence.  It is 520 independent seeds drawn from A85 BL pair census placements carried to the four corners, all of which behave the same way.

## Canary

Trump (sigma 3.877083590023): TL is the genuine 2-crowd, blockers {4, 6} at intrusion depths 0.168321 / 0.155475; BL, BR, TR each hold exactly ONE square (blockers {0}, {2}, {5}), so Trump is K0-FREE, not K0-BLOCKED.  The float test and the exact interval test agree exactly ([1, 1, 2, 1], no UNKNOWN rows).  Nicking the three flush slot squares 0/2/5 at amplitudes 3e-3 ... 1e-1 and repairing to feasibility keeps [1, 1, 2, 1] (TL keeps its 2-crowd up to 3e-2 and loses it at 1e-1); undoing the perturbation restores the verdict exactly.

Two tolerance points were forced by this canary and are load bearing:

1. A TANGENCY is not a block.  Trump square 3 rests exactly on the top edge of the BL slot (the float catalogue realises it at -1.3e-15); counting it would have called BL a 2-crowd.  Both the float and the exact test therefore require a certified intrusion DEPTH > 1e-9.

2. k0blocked87's slot convention is conservative for K0-FREE and is the wrong way round for K0-BLOCKED (it pushes the slot inward by the interval width and counts UNKNOWN rows as blockers, which turns that same tangency into a certified overlap).  The blocked direction gets its own INNER slot here -- the rational rectangle contained in the true slot for every realisation of the interval bounding box -- so a certified overlap with it is a certified overlap with the true slot.

