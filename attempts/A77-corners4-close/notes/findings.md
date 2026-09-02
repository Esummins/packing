# A77 — corners4 loop to PASS or Lemma W‴: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [M] measured/computed exact, [F] float evidence, [C] open.
Successor to A74.  STATUS: done-mixed — NO corners4 PASS; Lemma W‴ measured (the full
statement, tables and the root-order finding are in docs/proofs/pair_kill.md §6.9; this file
is the pointer + the engineering lessons).

## Headline (findings first)

1. [M] A74's "holes 220 -> 57 per iteration" was a `--nodes` HARD-STOP artifact: 283k-393k
   undischarged leaves sat behind the sampled cap witnesses (leaves = examined - split).
2. [M] Lemma W‴: complete spec-s4 hint trees (code/hintbatch.py) have per-level frontier
   retention r(d) = 0.75-0.86, FLAT from depth 8 to 25 on every root and every split rule
   measured; the complete tree is ~1e9-1e11 nodes at the W″ atom-depth scale.  Binding
   resource = tree size (η-fine boundaries of a tight measure), not holes, not the LP.  The
   frozen verifier holds hints in memory at 27 B/node -> the route is closed in this
   certificate form.
3. [M] Loop at equal budget (60k nodes/root): md8 41 holes -> md9 7 holes (~6x), but the 56
   hole placements cost 0.038 of the 0.042 slack (W2 20.95828 -> 20.99646; LP unconverged at
   kTimeLimit) and the open-box count is unchanged (856k -> 853k of 2.7M).
4. [M] C3 gap: reference `roots()` is ix-major, Rust `build_roots` iy-major (spec §3.1/§4
   silent) -> "i,j" hint keys are NOT portable (explains A74's 1493 misses).  With
   `--root_order rust`: 0 misses, and on the identical box-pair tree both implementations
   fire rule for rule: vac 1726 / ex 6449 / nd 14201 / split 22375 / examined 43025
   (results/py_xcheck48.report.json vs results/rs_hbR_prefix.report.json).  Hinted Rust runs
   at 46k nodes/s (vs 1.2-1.5k/s unhinted thrash at depth 60).  Spec erratum owed.
5. A76 relay: no P-B(R) row (corners4 d_min 0.8445; basin row irrelevant).  T3 not reached.

## Per-iteration table

| iter | catalog | atoms | W2 | slack | nodes | cov / open | holes | open cm median | LP / build wall |
|---|---|---|---|---|---|---|---|---|---|
| md8 | 469 | 363 | 20.95828 | 0.0417 | 2.71M | 176k / 856k | 41 | 0.602 | 975 s / 1338 s (6 procs) |
| md9 | 525 | 479 | 20.99646 | 0.0035 | 2.70M | 175k / 853k | 7 | 0.594 | 1200 s / 2671 s (4 procs) |

Growth law (root 2,11, rule certain, 1.59M nodes): r(14..25) = .782 .781 .775 .763 .756
.757 .747 .757 .762 .751 .771 .783; opens at d=26: 475k, certain-mass median 0.915;
3280 holes (d >= 20).  All 78 non-exempt roots: aggregate r(7..14) = 0.85-0.86.

## Engineering lessons

* Level-synchronous numpy B&B: ~1k nodes/s/process with the 12-child lookahead (numpy
  elementwise cost on (boxes x atoms) dominates; per-chunk atom pruning helps deep).
* Hint leaves should be `null`: COVERED leaf hints buy nothing (the Rust re-runs eval_node),
  and the JSON/memory cost is what limits hint size in the frozen verifier.
* The Python reference processes roots in REVERSE order (stack pushed in order, popped from
  the end) and stops after `--faildump` failures even in survey mode; use `--only-root` for
  per-root cross-checks.  Its throughput with 363 atoms is ~100 nodes/s unhinted, 4.5k hinted.
* LP: the A74 seed load (4 dual seeds) alone exceeds the nnz cap (23-24M) so the loop ran one
  round; two seeds (6.9M nnz) allow ~9 rounds at 60-180 s each.  Catalog growth is free only
  while the holes are shallow; deep holes (collecting 0.6-0.8) cost slack one-for-one.
* Never `taskkill /IM python.exe` on this box (campaign processes share the image); kill by
  PID tree.

## Pointers

code/hintbatch.py, code/iter77.py, code/hintcheck.py (exact tree walk), results/hb_md8.json,
results/hb_md9b.json, results/deep_40_2M.json, results/rule_{widest,certain}.json,
results/rs_md8_hb{,R}.report.json, results/rs_hbR_prefix.report.json,
results/py_xcheck{12,48}.report.json, certs/pair_k4_13_s0_b0_md{8,9b}.json (hinted certs
regenerable: `python code/hintbatch.py CERT OUT --cap 60000 --maxdepth 60 --rule certain
[--root_order rust]`), notes/ledger.md (canary SAFE x2), docs/proofs/pair_kill.md §6.9.
