# A280 results -- the DROP LEMMA at steep C (theta >= 25 deg)

Notes: `../notes/drop280.md`.  Page: `docs/residue_map/campaigns/A280-drop-steep/drop_steep.svg` (checks in
`pages280.json`).

## Diagnosis of A273's OPEN leaves (`diag280`, [M] slack by slack273 -- exact support-function gap, optimised)

| cell (theta x phi) | A273 OPEN leaves | pruned by DLOW (X misses int T_u) | left (big capped boxes) | slack at DLOW slivers | slack at the big boxes' centres |
|---|---|---|---|---|---|
| c6_2 (30-35 x 10-15), not capped | 10 | 10 | 0 | -0.00013 .. -0.00015 | -- |
| c7_6 (35-40 x 30-35), capped | 191 732 | 191 729 | 3 | -0.00006 | -0.060, -0.060, -0.324 |
| c8_3 (40-45 x 15-20), capped | 189 949 | 189 943 | 6 | -0.00018 .. -0.00020 | -0.017 .. -0.056 |

Every sampled OPEN-leaf midpoint: exact area X n T_u = 0, D <= 0.004 < D-low bound 0.136-0.184 (H2 fails).  No
positive slack anywhere: **weak relaxation (missing H2 / LOW prune), not a genuine miss.**

## The h_u -> 1 near-miss (theta 40, phi 32.88, D = D-low + delta) [M]

| h_u | delta 3e-2 | 1e-2 | 1e-3 | 1e-4 |
|---|---|---|---|---|
| 0.9 | -0.0487 | -0.0487 | -0.0487 | -0.0487 |
| 0.99 | -0.0157 | -0.0057 | -0.0050 | -0.0050 |
| 0.9999 | -0.0157 | -0.0057 | -0.0012 | -0.0008 |

Excluded by LOWF: at theta 40, LOW + open box force h_u <= 0.854.

## Benchmark of the strengthened tree (tree280 = A273's test + DLOW / SEP / LOWF) and verify280

| cell | boxes | leaves CERT / PRUNE | seconds | verify280 | A273 (same cell) |
|---|---|---|---|---|---|
| c6_2 | 179 | 37 / 53 | 0.5 | PASS (0 bisected) | 4 761 boxes, 10 OPEN |
| c7_6 | 69 | 21 / 14 | 0.2 | PASS (0) | 400 023 boxes, 1 223 s, OPEN |
| c8_6 | 223 | 42 / 70 | 0.7 | PASS (8) | not run yet |
| c8_3 | 327 | 78 / 86 | 1.0 | PASS (8) | 400 025 boxes, 1 690 s, OPEN |
| c5_4 | 51 | 15 / 11 | 0.2 | PASS (0) | 400 015 boxes, 2 451 s, OPEN |

Files: `certs/tree280_<cell>_bench.jsonl.gz`, `results/verify280_<cell>_bench.json`, `results/verify280_index.jsonl`.

## Launched

`code/run280.sh` (gated on the end of A273's chain; then 29 cells, one commit each; page at the end).  Price [M]:
~0.1-0.3 CPU-h.  STOP: `touch attempts/A280-drop-steep/logs/STOP280`; RESUME: remove it and relaunch the header line.
