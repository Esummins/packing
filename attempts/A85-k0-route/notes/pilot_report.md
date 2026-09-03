# A85 pilot report -- k0_00 corner frame (numbers only)

## Object
k0_00: k_S = 0, pins = [], N = 11, images = 8 (G_S = D4), s0 = 969271/250000.
All 8 exact witness families verified (admissible + strictly pairwise disjoint); min pairwise gap 7.4558e-08; every exact witness within 1e-5 of its float image placement.

## R1 reach cover at BL (rect [1/2,7/4]^2 x [0,90), w_box 0.15, a_min 0.34, w = 0.026, a = 1.026)
t-partition sigma-closed: True
| variant | boxes | sound (a=1+w) | sound (w=0) | witnessed | box set sigma-closed | P / M / S / A |
|---|---|---|---|---|---|---|
| sigma_closed_7 | 678 | 644 | 610 | 586 | True | 226 / 226 / 64 / 128 |
| tree57_sigma7 | 597 | 580 | 546 | 522 | False | 145 / 226 / 64 / 145 |
| tree57_uniform8 | 597 | 580 | 563 | 523 | False | 145 / 226 / 64 / 145 |

## R2 pair census at BL (variant sigma_closed_7, 644 sound boxes)
all unordered pairs 207046 -> level0 44516 -> level1 37788 -> level2 33656
| level | AA | AM | AP | AS | MM | MP | MS | PP | PS | SS |
|---|---|---|---|---|---|---|---|---|---|---|
| level0 | 1378 | 6228 | 5707 | 1254 | 6610 | 11262 | 2933 | 6140 | 2616 | 388 |
| level1 | 1330 | 4763 | 4654 | 1014 | 5883 | 9190 | 2400 | 5831 | 2335 | 388 |
| level2 | 1300 | 4197 | 4172 | 814 | 5507 | 7835 | 2082 | 5402 | 1959 | 388 |

## R3 alive gate (exact)
BL pairs at budget 9: attemptable 27702 (0.8231), unkillable 5954 (0.1769)
image-compatible BL pairs per image: {"g0": 12, "g1": 2, "g2": 2, "g3": 2, "g4": 12, "g5": 2, "g6": 2, "g7": 2} -- canary missing: NONE (canary PASSES)
fast gate vs frozen alive84 gate: 200 sampled, 0 disagreements
corner maps (BR/TR/TL): theta bins preserved = {"BL": true, "BR": true, "TR": true, "TL": true}
surviving-pair set sigma-closure: 33290/33656 (0.9891); max |a(b) - a(sigma b)| = 1.8607e-02
2-corner BL+TR (budget 7), n=300: {"attemptable": 0.9733, "unkillable": 0.01, "contradictory": 0.0167}
3-corner BL+BR+TR (budget 5), n=300: {"attemptable": 0.4333, "unkillable": 0.01, "contradictory": 0.5567}
4-corner (budget 3), n=1000: {"attemptable": 0.179, "unkillable": 0.002, "contradictory": 0.819}
D4-canonical 4-tuples: 120/1000 = 0.1200 (1/8 = 0.125); orbit sizes {"8": 1000}

## R4 LP samples (lp_time 900 s, cert_time 300 s, <= 3 concurrent, commit gate 6144 MB)
| tag | group | budget | cores | near/far | ghost | A38 tau | tau | eta | conv | lp_s | cert_s | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s1int_l1_043 | S1-INT | 10 | 1 | a38 | 0.3086 | 9.5814 | 9.777909 | -0.222091 | False | 1010.0 | 691.9 | FAIL(eps_geo retries exhausted) -> deepen |
| s1int_l1_008 | S1-INT | 10 | 1 | a38 | 0.0928 | 9.6331 | 9.875505 | -0.124495 | False | 949.3 | 660.9 | FAIL(eps_geo retries exhausted) -> deepen |
| s1int_l1_053 | S1-INT | 10 | 1 | a38 | 0.5704 | 9.5830 | 9.664070 | -0.335930 | False | 1014.1 | 643.8 | FAIL(eps_geo retries exhausted) -> deepen |
| s1int_l2_l2_p114_010 | S1-INT | 10 | 1 | a38 | 0.6359 | 8.5690 | 9.000000 | -1.000000 | False | 1066.0 | 631.6 | PASS |
| s1int_l2_l2_p210_001 | S1-INT | 10 | 1 | a38 | 0.5050 | 8.6000 | 8.727155 | -1.272845 | False | 1042.5 | 859.5 | PASS |
| s1int_l2_l2_p215_011 | S1-INT | 10 | 1 | a38 | 0.6262 | 8.6224 | 8.805928 | -1.194072 | False | 994.7 | 709.0 | FAIL(eps_geo retries exhausted) -> deepen |
| s1cor_near_b178 | S1-COR | 10 | 1 | near | 0.1283 | - | 9.548387 | -0.451613 | False | 952.8 | 685.4 | FAIL(eps_geo retries exhausted) -> deepen |
| s1cor_far_b595 | S1-COR | 10 | 1 | far | 0.6391 | - | 8.754860 | -1.245140 | False | 1023.2 | 742.5 | PASS |
| s2_near_046_473 | S2 | 9 | 2 | near | 0.0694 | - | - | - | None | None | None | not-run |
| s2_near_046_619 | S2 | 9 | 2 | near | 0.0694 | - | 8.000000 | -1.000000 | False | 1112.1 | 175.8 | PASS |
| s2_far_022_631 | S2 | 9 | 2 | far | 0.6391 | - | - | - | None | None | None | not-run |
| s2_far_022_633 | S2 | 9 | 2 | far | 0.6391 | - | - | - | None | None | None | not-run |
| s3_near_BL619642_TR023305 | S3 | 7 | 4 | near | 0.0694 | - | 6.000000 | -1.000000 | True | 63.0 | 4.3 | PASS |
| s3_near_BL368440_TR135473 | S3 | 7 | 4 | near | 0.0694 | - | - | - | None | None | None | not-run |
| s3_near_BL281514_TR528641 | S3 | 7 | 4 | near | 0.0694 | - | - | - | None | None | None | not-run |
| s3_far_BL389484_TR018470 | S3 | 7 | 4 | far | 0.3472 | - | 7.000000 | +0.000000 | True | 127.4 | 0.0 | refused (tau 7.000000 >= budget 7) |
| s3_far_BL066471_TR504617 | S3 | 7 | 4 | far | 0.3472 | - | - | - | None | None | None | not-run |
| s3_far_BL504630_TR486533 | S3 | 7 | 4 | far | 0.3472 | - | - | - | None | None | None | not-run |
| s4_near_BL357619_BR004483_TR191404 | S4 | 5 | 6 | near | 0.0694 | - | 4.333333 | -0.666667 | False | 1007.9 | 8.7 | PASS |
| s4_near_BL283514_BR306371_TR017518 | S4 | 5 | 6 | near | 0.0694 | - | - | - | None | None | None | not-run |
| s4_far_BL485522_BR024614_TR103437 | S4 | 5 | 6 | far | 0.3584 | - | - | - | None | None | None | not-run |
| s4_far_BL000453_BR020628_TR013481 | S4 | 5 | 6 | far | 0.3693 | - | - | - | None | None | None | not-run |
| s5_near_BL514601_BR091318_TR024269_TL022178 | S5 | 3 | 8 | near | 0.0694 | - | - | - | None | None | None | not-run |
| s5_near_BL104223_BR004619_TR108262_TL002330 | S5 | 3 | 8 | near | 0.0694 | - | - | - | None | None | None | not-run |
| s5_far_BL072642_BR376404_TR018301_TL040270 | S5 | 3 | 8 | far | 0.3320 | - | - | - | None | None | None | not-run |
| s5_far_BL003487_BR014571_TR012478_TL016022 | S5 | 3 | 8 | far | 0.3320 | - | - | - | None | None | None | not-run |

scoreboard: {"planned": 26, "run": 12, "PASS": 6, "FAIL": 5, "refused": 1, "eta_le_m015": 10, "lp_seconds_total": 10363.0, "cert_seconds_total": 5813.4}
waits logged: 0 (results/a85_waits.jsonl); deferred: 0

## Run notes
* Commit gate: free commit (tree85.free_commit_mb, Win32 ullAvailPageFile) was ABOVE the 6144 MB floor at each of the three shards' first LP calls -- the gate logged zero waits (results/a85_waits.jsonl is empty), and a reading taken 60 s after the three launches was 6336.7 MB. It fell to ~1049 MB while the three LPs held their working sets and recovered to 12749 MB when they released; no LP or certify was ever started into a dip.
* 3 LP/certify slots max, held for the whole phase (3 shards x 1 in-flight node each; certify.py children count toward the parent's slot). BLAS pinned to 1 thread (blas1 first).
* LP phase wall cap 3 h: shards stopped TAKING new nodes at 10500 s. 12 of 26 planned nodes landed; s2_near_046_473 was still inside its LP at the cap and is left running -- it appends its own record to results/a85_lp_samples.jsonl if it finishes. The other 13 rows are not-run.
* eps_geo repair: 2 of the 6 PASSes needed it (s1cor_far_b595 and s1int_l2_l2_p210_001, both at eps_geo = 0.004); 5 nodes exhausted both margins (0.002, 0.004) and stay FAIL.
* CANARY: no node was refused as image-realizable and no PASS occurred on an image-realizable node (the engine's exit-9 path never fired).
* SIGMA FINDING: tree57.cover's split rule is not equivariant under theta -> 90 - theta (it bisects along the widest dimension measured in t, and mirrored t-bins of a sigma-closed t-partition have different t-widths: 1/8 vs 2/9 here), so its box set is NOT sigma-closed (P 145 vs M 226 above) and the D4 corner maps do not land on cover boxes. corner85.cover_sigma repairs this (refine by bisecting theta at the DEGREE midpoint, refine iff min(a(b), a(sigma b)) < a_min); the repaired box set IS sigma-closed and the corner maps preserve every theta bin. The rational CORE is still t-grid based, so core(sigma b) != sigma core(b) (max |a(b) - a(sigma b)| = 1.86e-2) and the SURVIVING pair set is only 98.91% sigma-closed -- sound either way, but the /8 D4 quotient is exact at the box level and only approximate at the pruned-pair level.
