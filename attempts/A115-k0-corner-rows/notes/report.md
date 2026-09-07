# A115 — Lemma CW corner-crowd rows at the k0_00 NODE level (Opus chore, measurement)

> **VERDICT.  Corner incidence rows at δ ∈ {0, 0.05, 0.1} certify 2 of 11  K01 k0_00 cells they were attempted on, and only **1** of those is attributable to the rows (`l3_pp65_111_000` at δ = 0, a level-3 cell: the plain node certificate FAILS on the same cell at the same LP wall, `results/control.jsonl`); the other reproduces without the rows. Zero cells that were genuinely alive at the LP (η₀ ≥ 0, 0 of 8) died at any δ.**  The A109 failure mode is IMPOSSIBLE here — the four widened corner boxes are s0 − 2a_w = 1.826 > √2 apart, so a unit square carries at most ONE incidence, r_max ∈ {0,1}, B = 8 − Σ r_max ∈ {7,8} is EXACT and no multiplicity re-pricing can happen.  The rows fail for the opposite reason: **the guaranteed budget 8 is below what a packing at s0 achieves for free.**  Exactly: every D4 image of Trump realises **9** corner incidences at a_w(0) = 1.025520 (per-corner counts 3/2/2/2 — its tangent squares sit at μ_c = 1, inside the K0-WIDEN box), so at δ = 0 the achievable crowd mass is ≥ 9 > 8 = B and the ROOT LP can never pass; and at the node level the LP's own fractional packing realises c ≥ B in **100 of 101** measured runs (mean c = 9.60 / 9.23 / 8.68 at δ = 0 / 0.05 / 0.1 against mean B = 7.21), so by the convexity rule (τ(e) is the optimum of an LP affine in e ⇒ c(e) non-decreasing ⇒ a kill needs c(e) < B) **no e can kill them**.  Price 224 s per (cell, δ) + 410 s per certification; net −13 CPU-h against A99's 9,341–21,661 CPU-h frontier.

> The single run in 101 with c < B — `l2_p215_000__d0.1` (c = 6.55 < B = 7) — is an unconverged LP, and its two-run certificate FAILS on BOTH runs in both rounds (796 s).

## T3 — verdict, price, projection

### price (measured)

| item | value |
|---|---|
| corner-row re-solve per (cell, δ), mean / median | 224 / 254 s |
| … max | 1241 s |
| the same cell's ORIGINAL k0 node LP wall, mean / median | 469 / 497 s |
| two-run frozen certification, mean | 410 s |
| certified | 2 of 11 attempted |

### projection onto the k0_00 tree

A115's rows are part of the NODE HYPOTHESIS, so a certified node is an ordinary A92 two-run certificate and the deployment is route (a): one corner-row re-solve on every open cell, harvesting the killed cell AND its whole subtree.

| item | value |
|---|---|
| A99 frontier (STACKED window-valid, `projection99.json`) | 9341–21661 CPU-h |
| level-1 cells of the k0_00 root split | 216 |
| what one CERTIFIED level-1 kill removes | 43.2–100.3 CPU-h |
| cost of one corner-row pass over all 216 level-1 cells (one δ) | 13.44 CPU-h |
| what one CERTIFIED kill removes at level 2 / 3 | 5.41–12.54 / 0.68–1.57 CPU-h |
| certified level-1 kills measured here | 0 |
| certified kills at any level (attributable to the rows) | 2 (1) |
| **net, counting only ATTRIBUTABLE certified kills** | -12.76 / -11.87 CPU-h |

### attribution control (`code/control115.py`, `results/control.jsonl`)

For every cell whose CORNER-ROW certificate passed: does the same cell certify WITHOUT the rows?  `ctrlA` = the campaign's own stored LP result, plain certificate; `ctrlB` = a PLAIN re-solve warm-started from it with the same 240 s cap A115's stage 1 used, then the same plain certificate.

| cell | level | corner-row cert | ctrlA (stored LP) | ctrlB (matched plain re-solve) | attributable to the rows |
|---|---|---|---|---|---|
| `l2_p95_001` | 2 | PASS | FAIL | PASS | **no** |
| `l3_pp65_111_000` | 3 | PASS | FAIL | FAIL | **YES** |

## T2 — corner rows at the node level

`B` = 8 − Σ r_max(B⁺) over the node's conditioned cores = the corner-crowd incidences Lemma CW guarantees among the squares the node LP still pays for; `bonus` = floor(eB) = 1 at e = 1/B; `c` = (τ − τ₀)/e = the incidences the LP's own fractional packing realises. A kill needs `c < B`.

| cfg | δ | a_w | cells | mean B | mean c | c ≥ B | kill-candidates (LP) | knife-edge | alive | certified | mean LP s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `d0` | 0 | 1.025520 | 36 | 7.14 | 9.60 | 34/34 | 20 | 0 | 16 | 1/4 | 199 |
| `d0.05` | 0.05 | 0.974770 | 36 | 7.22 | 9.23 | 34/34 | 20 | 0 | 16 | 0/3 | 200 |
| `d0.1` | 0.1 | 0.924020 | 35 | 7.26 | 8.68 | 32/33 | 23 | 0 | 12 | 1/4 | 274 |

### per cell (η = τ − budget; the CERTIFICATE is the verdict, never η)

| cell | src | lvl | room | budget₀ | τ₀ | η₀ | B | n | τ(d0) | η(d0) | τ(d0.05) | η(d0.05) | τ(d0.1) | η(d0.1) | c(d0) | cert |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `l1_060_plain_warm` | A99 | 1 | BR | 10 | 9.9712 | -0.029 | 8 | 11 | 11.3630 | +0.363 | 11.0752 | +0.075 | 11.1250 | +0.125 | 9.74 | - |
| `l1_082_sh3_warm` | A99 | 1 | TL | 10 | 9.0837 | -0.916 | 7 | 11 | 10.5584 | -0.442 | 10.6648 | -0.335 | 10.5055 | -0.495 | 10.32 | - |
| `l1_148_plain_warm` | A99 | 1 | TL | 10 | 10.0000 | +0.000 | 7 | 11 | 11.2857 | +0.286 | 11.1429 | +0.143 | 11.1429 | +0.143 | 9.00 | - |
| `l1_148_sh3_warm` | A99 | 1 | TR | 10 | 8.3750 | -1.625 | 7 | 11 | 10.1429 | -0.857 | 10.1429 | -0.857 | 10.1429 | -0.857 | 12.37 | - |
| `l1_192_plain_warm` | A99 | 1 | BL | 10 | 10.1522 | +0.152 | 7 | 11 | 11.5757 | +0.576 | 11.4770 | +0.477 | 11.4286 | +0.429 | 9.97 | - |
| `l1_203_plain_warm` | A99 | 1 | BL | 10 | 10.0000 | -0.000 | 7 | 11 | 11.1504 | +0.150 | 11.2383 | +0.238 | 11.1071 | +0.107 | 8.05 | - |
| `l1_214_plain_warm` | A99 | 1 | TL | 10 | 9.0775 | -0.923 | 7 | 11 | 10.2864 | -0.714 | 10.1965 | -0.804 | 10.1501 | -0.850 | 8.46 | - |
| `l1_214_sh2dia_warm` | A99 | 1 | TR | 10 | 8.6463 | -1.354 | 7 | 11 | 9.9963 | -1.004 | 9.8631 | -1.137 | 10.0659 | -0.934 | 9.45 | - |
| `node_020` | A38 | 1 | BR | 10 | 9.7338 | -0.266 | 8 | 11 | 11.0205 | +0.021 | 11.1039 | +0.104 | 10.9925 | -0.007 | 10.29 | - |
| `node_021` | A38 | 1 | - | 10 | 9.7773 | -0.223 | 8 | 11 | 11.1250 | +0.125 | 11.0138 | +0.014 | 10.9192 | -0.081 | 10.78 | - |
| `node_059` | A38 | 1 | TR | 10 | 9.6729 | -0.327 | 7 | 11 | 11.2857 | +0.286 | 11.0947 | +0.095 | 11.1135 | +0.113 | 11.29 | - |
| `node_061` | A38 | 1 | BL | 10 | 10.0000 | -0.000 | 8 | 11 | 11.2857 | +0.286 | 11.1250 | +0.125 | 11.1250 | +0.125 | 9.00 | - |
| `node_083` | A38 | 1 | BR | 10 | 10.0735 | +0.074 | 7 | 11 | 11.5011 | +0.501 | 11.4710 | +0.471 | 11.3564 | +0.356 | 9.99 | - |
| `node_086` | A38 | 1 | BR | 10 | 9.7847 | -0.215 | 7 | 11 | 11.0562 | +0.056 | 11.0800 | +0.080 | 10.9389 | -0.061 | 8.90 | - |
| `node_089` | A38 | 1 | BL | 10 | 10.5000 | +0.500 | 7 | 11 | 12.0855 | +1.085 | 11.8576 | +0.858 | 11.6745 | +0.674 | 11.10 | - |
| `node_095` | A38 | 1 | BL | 10 | 10.0000 | +0.000 | 7 | 11 | 11.2130 | +0.213 | 11.2286 | +0.229 | 11.1250 | +0.125 | 8.49 | - |
| `node_101` | A38 | 1 | BL | 10 | 10.0000 | +0.000 | 7 | 11 | 11.2857 | +0.286 | 11.2857 | +0.286 | 11.1163 | +0.116 | 9.00 | - |
| `node_141` | A38 | 1 | TL | 10 | 9.6891 | -0.311 | 7 | 11 | 11.0357 | +0.036 | 11.0039 | +0.004 | 10.9737 | -0.026 | 9.43 | - |
| `s1cor_far_b595` | A85 | 1 | - | 10 | 8.7549 | -1.245 | 7 | 11 | 10.0209 | -0.979 | 10.0082 | -0.992 | - | - | 8.86 | - |
| `s1cor_near_b178` | A85 | 1 | BR | 10 | 9.5484 | -0.452 | 7 | 11 | 10.9231 | -0.077 | 10.8836 | -0.116 | 10.7412 | -0.259 | 9.62 | - |
| `s1int_l2_l2_p210_001` | A85 | 1 | TL | 10 | 8.7272 | -1.273 | 7 | 11 | 9.9810 | -1.019 | 9.9902 | -1.010 | 9.8237 | -1.176 | 8.78 | - |
| `s1int_l2_l2_p215_011` | A85 | 1 | BR | 10 | 8.8059 | -1.194 | 7 | 11 | 10.0528 | -0.947 | 10.0016 | -0.998 | 9.8636 | -1.136 | 8.73 | - |
| `l2_p100_010` | A38 | 2 | BL | 10 | 8.8889 | -1.111 | 8 | 11 | 10.4336 | -0.566 | 10.4062 | -0.594 | 10.3333 | -0.667 | 12.36 | - |
| `l2_p210_000` | A38 | 2 | BR | 10 | 8.6071 | -1.393 | 7 | 11 | 9.9345 | -1.066 | 9.7662 | -1.234 | 9.6883 | -1.312 | 9.29 | FAIL,FAIL |
| `l2_p210_010` | A38 | 2 | BR | 10 | 8.6124 | -1.388 | 7 | 11 | 9.9221 | -1.078 | 9.7957 | -1.204 | 9.6955 | -1.305 | 9.17 | FAIL |
| `l2_p215_000` | A38 | 2 | TL | 10 | 8.7500 | -1.250 | 7 | 11 | 9.9953 | -1.005 | 9.8208 | -1.179 | 9.6856 | -1.314 | 8.72 | FAIL |
| `l2_p215_010` | A38 | 2 | TL | 10 | 8.7287 | -1.271 | 7 | 11 | 10.1763 | -0.824 | 10.0918 | -0.908 | 9.8060 | -1.194 | 10.13 | - |
| `l2_p215_011` | A38 | 2 | BL | 10 | 8.6224 | -1.378 | 7 | 11 | 9.9759 | -1.024 | 9.9650 | -1.035 | 9.7852 | -1.215 | 9.47 | - |
| `l2_p74_000` | A38 | 2 | TR | 10 | 8.7500 | -1.250 | 8 | 11 | 10.1429 | -0.857 | 9.8621 | -1.138 | 10.0000 | -1.000 | 9.75 | - |
| `l2_p95_001` | A38 | 2 | BL | 10 | 9.0000 | -1.000 | 8 | 11 | 10.1250 | -0.875 | 10.0625 | -0.938 | 10.0000 | -1.000 | 9.00 | PASS |
| `l3_pp215_000_000` | A38 | 3 | TL | 10 | 8.5141 | -1.486 | 7 | 11 | 9.8858 | -1.114 | 9.8874 | -1.113 | 9.6328 | -1.367 | 9.60 | FAIL,FAIL |
| `l3_pp215_000_001` | A38 | 3 | BL | 10 | 8.6250 | -1.375 | 7 | 11 | 9.8754 | -1.125 | 9.8147 | -1.185 | 9.7766 | -1.223 | 8.75 | FAIL,FAIL |
| `l3_pp215_000_011` | A38 | 3 | BR | 10 | 8.5642 | -1.436 | 7 | 11 | 9.9032 | -1.097 | 9.9379 | -1.062 | 9.7079 | -1.292 | 9.37 | FAIL |
| `l3_pp65_111_000` | A38 | 3 | BL | 10 | 9.0000 | -1.000 | 8 | 11 | 10.1250 | -0.875 | 10.1250 | -0.875 | 10.1250 | -0.875 | 9.00 | PASS |
| `node_152` | - | - | - | 10 | - | - | 7 | 11 | 11.2857 | +0.286 | 11.2857 | +0.286 | 11.1099 | +0.110 | - | - |
| `node_153` | - | - | - | 10 | - | - | 7 | 11 | 11.2001 | +0.200 | 11.1429 | +0.143 | 11.1310 | +0.131 | - | - |

### certification of the kill candidates (frozen `verify_case.py`, A92's two-run form)

| tag | result | rounds | run A | run B | wall s |
|---|---|---|---|---|---|
| `l2_p210_000__d0.05__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 330 |
| `l2_p210_000__d0.1__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 641 |
| `l2_p210_010__d0.05__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 415 |
| `l2_p215_000__d0.1__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 796 |
| `l2_p95_001__d0.1__e1o8` | PASS | 1 | PASS | PASS | 44 |
| `l3_pp215_000_000__d0.1__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 499 |
| `l3_pp215_000_000__d0__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 397 |
| `l3_pp215_000_001__d0.05__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 370 |
| `l3_pp215_000_001__d0__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 329 |
| `l3_pp215_000_011__d0__e1o7` | FAIL | 2 | FAIL(?) | FAIL(?) | 455 |
| `l3_pp65_111_000__d0__e1o8` | PASS | 1 | PASS | PASS | 229 |

### Trump canary

* `d0` (a_w = 1.025520): images realising the corner-crowd hypothesis: **g0,g1,g2,g3,g4,g5,g6,g7** — per-image corner counts g0[3222];g1[2322];g2[2232];g3[2223];g4[3222];g5[2232];g6[2322];g7[2223]
* `d0.05` (a_w = 0.974770): images realising the corner-crowd hypothesis: **NONE** — per-image corner counts g0[1121];g1[1112];g2[2111];g3[1211];g4[1211];g5[1112];g6[2111];g7[1121]
* `d0.1` (a_w = 0.924020): images realising the corner-crowd hypothesis: **NONE** — per-image corner counts g0[1121];g1[1112];g2[2111];g3[1211];g4[1211];g5[1112];g6[2111];g7[1121]

* node_021 d0 survives (Trump realises: must not die) -- OK
* node_152 d0 survives (Trump realises: must not die) -- OK
* node_153 d0 survives (Trump realises: must not die) -- OK
* node_021 d0.05: Trump does NOT realise the hypothesis at this a_w, so a kill here would be sound (verdict alive)
* node_152 d0.05: Trump does NOT realise the hypothesis at this a_w, so a kill here would be sound (verdict alive)
* node_153 d0.05: Trump does NOT realise the hypothesis at this a_w, so a kill here would be sound (verdict alive)
* node_021 d0.1: Trump does NOT realise the hypothesis at this a_w, so a kill here would be sound (verdict kill-candidate)
* node_152 d0.1: Trump does NOT realise the hypothesis at this a_w, so a kill here would be sound (verdict alive)
* node_153 d0.1: Trump does NOT realise the hypothesis at this a_w, so a kill here would be sound (verdict alive)

* **canary verdict: PASS**

## T1 — which corner, how deep


`closed` = meets [0,1]^2 (mu_c <= 1, the s0 convention); `wide` = meets the K0-WIDEN box [0, 1.025520]^2.  84 K01 cells.

## corner-cell occupancy of the shadow (11 placements), by corner

| corner | 0 meeters | 1 meeter | 2 meeters | >=3 |
|---|---|---|---|---|
| BL | 0 | 57 | 21 | 6 |
| BR | 0 | 35 | 38 | 11 |
| TL | 0 | 70 | 11 | 3 |
| TR | 0 | 50 | 28 | 6 |

## which corners are 'room' (met by <= 1), as a set

| room set (closed) | cells | room set (widened) | cells |
|---|---|---|---|
| BL+TL | 16 | BL | 20 |
| BL+BR+TL+TR | 14 | (none) | 18 |
| BL+TL+TR | 12 | TL | 11 |
| TL+TR | 10 | TR | 10 |
| BL+BR+TL | 7 | TL+TR | 7 |
| BR+TL+TR | 6 | BL+TL | 6 |
| TR | 4 | BR+TR | 3 |
| BR+TL | 3 | BR | 3 |
| BL+BR | 3 | BL+BR | 2 |
| BL+TR | 3 | BL+TR | 2 |
| BL | 2 | BR+TL+TR | 2 |
| TL | 2 |  |  |
| BR+TR | 1 |  |  |
| BR | 1 |  |  |

## depth of the meeters that ARE there, by corner (shadow placements with mu_c <= 1)

| corner | 0 (touch/none) | (0,0.05) | [0.05,0.10) | [0.10,0.155) | [0.155,0.30) | >=0.30 | total |
|---|---|---|---|---|---|---|---|
| BL | 0 | 25 | 2 | 2 | 9 | 79 | 117 |
| BR | 0 | 36 | 0 | 16 | 20 | 72 | 144 |
| TL | 0 | 11 | 0 | 2 | 6 | 82 | 101 |
| TR | 0 | 16 | 4 | 14 | 27 | 63 | 124 |

## the SECOND meeter's depth d2 (the quantity Lemma CW conditions on), by corner

| corner | no 2nd meeter | d2 = 0 | d2 in (0,.05) | [.05,.10) | [.10,.155) | [.155,.30) | >= .30 |
|---|---|---|---|---|---|---|---|
| BL | 57 | 0 | 19 | 1 | 2 | 5 | 0 |
| BR | 35 | 0 | 28 | 0 | 11 | 10 | 0 |
| TL | 70 | 0 | 10 | 0 | 1 | 3 | 0 |
| TR | 50 | 0 | 14 | 3 | 10 | 7 | 0 |

## fractional crowd weight of the LP dual support (what the rows charge)

| level | cells | mean budget | mean total LP weight | mean weight in U_c F_c(widened) | mean weight per corner |
|---|---|---|---|---|---|
| 1 | 65 | 9.92 | 9.597 | 7.315 | BL 1.70 / BR 2.06 / TL 1.75 / TR 1.80 |
| 2 | 15 | 10.00 | 9.016 | 6.588 | BL 1.78 / BR 2.01 / TL 1.73 / TR 1.07 |
| 3 | 4 | 10.00 | 8.676 | 5.962 | BL 1.69 / BR 1.88 / TL 1.89 / TR 0.50 |


## Pointers

* method, the licensing table for δ = 0 / 0.05 / 0.1 and the exact node incidence budget: `attempts/A115-k0-corner-rows/notes/method.md`
* code: `attempts/A115-k0-corner-rows/code/` (the A92 engine copied verbatim + `a115lib.py`, `t1.py`, `plan115.py`, `t2.py`, `certify115.py`, `canary115.py`, `t3.py`, `report115.py`)
* results: `results/t1_corners.json`, `results/t1_table.md`, `results/t2_plan.json`, `results/t2_runs.jsonl`, `results/rec/<tag>.json` (one resumable record per cell x δ x e), `results/nodes/<nid>.src.json` (every campaign node json, copied) and `results/nodes/<tag>.lp.json`, `results/fams/fam_d*.json`, `results/t2_certs.jsonl`, `results/t3.json`, `results/canary115.json`, `results/trump_family_counts.json`
* certificates: `certs/runA_*.json`, `certs/runB_*.json` (frozen verifier sha256 `521cb01f…`)
* logs: `logs/t1.log`, `logs/t2_s0.log`, `logs/t2_s1.log`, `logs/certify_s0.log`, `logs/canary.log`
