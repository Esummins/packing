# A215 -- CLOSED-NODE BENCHMARK: the current runner against nodes with known termination times (PI, 2026-09-14 14:20).
Opus. LAUNCH-AND-EXIT.
PI: "I would assume you would run the new optimized set of tools against an already closed node to confirm the speedup
against a node with a known termination time before using it to estimate anything."
Benchmark set (page, pad g1, the campaign and its root-to-kill seconds):
  k5_11_Y0308 203 s (A205) | k5_16_Y0054 312 s (A205) | k5_16_Y0027 365 s (A205) | k5_16_Y0565 397 s (A205) |
  k5_16_Y0839 526 s (A205) | k5_16_Y0881 879 s (A211 pass 1) | k5_16_Y0719 237 s (A211) | k5_16_Y1110 1,766 s (A209) |
  k5_11_Y0036_D07 pad 0 548 s (A211e before) / 106 s (A211f after) | k5_16_Y0985 2,121 s (A206) | k5_11_Y1104 2,401 s (A206).
Run each with the CURRENT A211 runner (attempts/A211-coarse-tree/code/run211.py, all flags at their defaults: A213
integer core, A213b integer clip, A214 C kernel, A211e/f conditional coarse core, memos; --no-inherit so the run is
root-to-kill; --pads g1 (pad 0 for Y0036_D07); wall 3600; isolated --cert-dir / --results / --no-fig; ONE process at a
time, BelowNormal via A210's working fix, BLAS pinned), record wall seconds to the kill and the verdict, and put the
table (node, old campaign, old seconds, new seconds, ratio, verdict agrees?) in results/benchmark215.md with the
geometric-mean speedup and the spread.  If a node does NOT die under the current runner where it died before, say so
prominently -- that is a regression to chase, not a speedup to report.  Also record the per-run stage table (A211f's
profstage211) for two of them.  No code changes; if a run crashes, record it and move on.  Never touch the running
workers (A211 f1/f2, and A211g's relaunches of p2a/p2b and A212 when they appear) or the k0 cascade.  Explicit-pathspec
commits; no monitors, no waiting turns.  Report once (the table, the geometric mean, regressions if any) and EXIT.

## RESULT (A215, 2026-09-14 14:40).  `results/benchmark215.md` (table, means, caveats, stage table).

All 11 nodes re-run root-to-kill under the current runner, one process at a time, `--no-inherit`, wall 3600, isolated
`--cert-dir` / `--results` / `--no-fig`, BelowNormal + BLAS pinned.  **Every one still DIES and every verdict agrees
with the old campaign's -- 0 regressions.**  Geometric mean 7.22x over all 11 (spread 0.16x -- 43.9x, median 12.0x);
**16.9x over the 6 nodes whose OLD number was itself a root-to-kill wall** (the five A205 clip-tree pages and A209's
Y1110).  The five other old numbers had a head start this run did not: A211 / A211f rows inherited dead branches, and
A206's rows started from A205's leaf certificates -- those ratios (1.33x, 1.48x, 0.16x, 15.2x, 25.6x) are quoted but
are not like-for-like.  The single sub-1 ratio, `k5_11_interior_Y0036_D07` pad 0 at 671 s against A211f's 106.2 s, is
that artefact: A211f started from 6 inherited DEAD branches and 5 start nodes, this run from the A203 root (52 nodes,
0 alive leaves).  Stage table (cProfile, the two cheapest nodes): a page that dies fast is NOT no-room-bound --
option table 52-63 %, coarse fixed point 26-29 %, K' 18-21 %, and no `noroom_at` / lane rows at all, unlike A211f's
Y0202 (no-room 82 %, lane 40 %).  Data: `results/times215.tsv`, `results/bench215.jsonl`, `results/stagetable215.txt`,
`logs/`, `certs/`.  Running workers and the k0 cascade untouched.
