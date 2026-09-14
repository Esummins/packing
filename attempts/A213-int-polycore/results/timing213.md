# A213 -- timing: the K' build in integer space (per call and per run)

Machine as always (one BelowNormal python, BLAS pinned, PYTHONDONTWRITEBYTECODE=1, 8 other lab pythons running).
Page `k5_11_interior_Y0202`, pad 0, wall 900 s, isolated cert / results dirs, `--no-fig`, inherited start
(A211d's profile page), the working-copy chain of 2026-09-14 11:30 (A211e's coarse cores ON: kmode union, grid 33 at
internal nodes; per-piece K' at the exact leaf cascade).  BEFORE = the library build; AFTER = A213_INTCORE=1.

## Per call (tests/replay213.py: every library-level MBox.rebuild of the BEFORE run replayed through both builds)

441 rebuilds replayed (181 union-mode, 260 pieces-mode; the K' memo's misses of the BEFORE run; every piece built
fresh, no per-piece cache), 0 mismatches, 0 record-vs-replay differences.  No profiler.

| primitive (per call) | calls | library | integer space (Phase 1) | gain | vectorised (Phase 2) |
|---|---|---|---|---|---|
| MBox.rebuild (whole, library-level) | 441 | 320 ms | 45 ms | x7.0 | -- |
| polycore.build (one piece box / union hull) | 3349 | 22.6 ms | 4.2 ms (polycore_fast) | x5.4 | (the float pipeline is the vectorised part) |
| intersect_frac -> intersect_h | 441 | 23.3 ms | 1.3 ms | x17.6 | -- |
| certify_verts (nv x N pieces, all pass) | 260 | 49.6 ms | 1.7 ms | x29 | float filter 0.63 ms (x79, 0 exact fallbacks of 47,656 pairs); object dtype 1.8 ms (x27) |
| axis_core_pieces | 260 | 13.8 ms | 0.5 ms | x25 | -- |

The fuzz (tests/fuzz213.py 150 213): 150 random piece sets (95 pieces-mode, 55 union-mode) 0 mismatches, library
245 ms -> integer 36 ms per rebuild (x6.7); 2,700 vertex tests (random + exact-boundary points, Fraction = integer =
float-filter = object dtype), 50 exact fallbacks of 2,700 pairs on the boundary points; 75 random polygon
intersections / roundings, 0 mismatches.  Earlier partial passes (60 sets, 40 replays) also 0 mismatches.

## Per run (code/profrun213.py under cProfile; the stage table by code/stages213.py)

Both runs under cProfile (as A211d's), which inflates the Fraction-heavy library path (539 M Fraction calls) more
than the integer path -- the per-call table above is the profiler-free comparison.  `calls | s` = calls, cumulative s.

| stage / function | BEFORE calls | BEFORE s | AFTER calls | AFTER s |
|---|---|---|---|---|
| run_page (wall; 900 s wall + the last node) | 1 | 911.2 | 1 | 954.6 |
| tree normalise (the coarse fixed point) | 8 | 123.2 | 10 | 124.5 |
| MBox.rebuild (library-level, memo misses) | 441 | 245.7 | 466 | 25.2 |
| pieces_poly | 260 | 203.1 | 276 | 20.5 |
| polycore.build (per piece / union hull) | 1941 | 147.7 | 2116 | 20.9 |
| _clip -> _clip_np | 781052 | 44.9 | 857672 | 15.4 |
| _simplify -> _simplify_np | 2335 | 70.8 | 2546 | 2.7 |
| intersect_frac -> intersect_h | 260 | 28.5 | 276 | 0.9 |
| certify_verts (library; the int path certifies inside pieces_poly) | 520 | 48.9 | 0 | 0.0 |
| axis_core_pieces | 260 | 10.6 | 276 | 0.2 |
| exactcore.exact_core (its vertex_ok now integer) | 441 | 23.5 | 466 | 2.6 |
| vertex_ok, all callers (library / int drop-in) | 128439 | 99.0 | 35763 | 0.8 |
| vertex_ok_h (the integer kernel) | 0 | 0.0 | 139699 | 1.7 |
| _clip_rect_obstacle (A131 pin-clip, NOT touched) | 270042 | 592.3 | 338238 | 746.5 |
| no-room leaf (noroom189; contains rebuilds + clips) | 8 | 751.0 | 10 | 783.4 |
| role reach depth 0 (fastclip211.reach0) | 241 | 16.6 | 297 | 21.2 |
| Fraction arithmetic (_mul + _add + _sub + math.gcd) | 538.7 M | 347.6 | 521.0 M | 342.0 |

Per run: the rebuild stage 245.7 s -> 25.2 s (x9.7; 27% of the BEFORE wall -> 2.6% of the AFTER wall), and the
time bought WORK: inside the same 900 s wall the AFTER run expanded 10 nodes (depth 3, 5 role splits) against 8
(4 role splits) -- R.1.4.2.2.2 (ALIVE-at-wall before) was expanded to two children (one ALIVE at the wall, one
untouched).  Verdicts identical on every common node (4 x DEAD NOROOM, the internals, the wall leaves); the two
certificates agree field by field on 13 of the 15 common nodes with the time fields stripped; the other two are
(i) R.1.4.2.2.2 itself (expanded only after) and (ii) R.1.4.2.2's no-room `pockets`, whose extents differ in the 4th
decimal because noroom189's `bisect_free` stops on a wall-clock deadline (131 s vs 180 s of budget at that node; the
verdict UNDECIDED and the pocket count are the same).  `_clip_rect_obstacle` rose 592 -> 747 s because the run did
more of it (338 k vs 270 k calls); per call it is unchanged (2.19 vs 2.21 ms).  Logs: logs/profile/{before,after}_
k5_11_interior_Y0202.{prof,log}, results/run_{before,after}/, results/replay_before_k5_11_interior_Y0202.jsonl,
logs/replay_before_Y0202.log, logs/fuzz213.log.

## Reading

* The rebuild is the ONLY thing that changed, and it is bit-exact (0 mismatches on the replay and the fuzz); what did
  not change is the rest of the node -- `_clip_rect_obstacle` (A131's pin-clip bisection on Fractions, 592 s of the
  911 s BEFORE run, inside no-room and the fixed point) is now ~2/3 of a node and the next lever (the same
  integer-space treatment applies: its `dead_poly` / `_dead_poly_f` tests are signs of low-degree polynomials in the
  rect corners, the obstacle vertices and t).
* Phase 2: the float filter certifies a (vertex, box) pair in ~1 numpy pass over (nv, N, 4) arrays and sends the
  undecided pairs (a few per thousand) to the integer path; the object-dtype route is exact but slower than the scalar
  integer loop (no early exit, one bignum op per element per step).  Two-limb int64 does not fit the 2^183 bound.
