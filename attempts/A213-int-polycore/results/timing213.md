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

---

# A213b -- timing: the RECTANGLE-OBSTACLE CLIP in integer space (per call and per run)

Same machine and protocol (one BelowNormal python per run, BLAS pinned, `PYTHONDONTWRITEBYTECODE=1`, other lab
pythons running), same page `k5_11_interior_Y0202` pad 0, wall 900 s, isolated cert / results dirs, `--no-fig`,
inherited start.  BEFORE = `A213_INTCLIP=0` (A131/A171's clip on Fractions), AFTER = `A213_INTCLIP=1`
(`pinclip_int`).  Both runs carry A213 (integer K' build) and A214's C kernel, so the ONLY difference between the
two columns is the clip.  Code `code/pinclip_int.py`, wiring `code/mbpatch213.install_clip`, note
`notes/int_clip.md`.

## Per call (tests/replay_clip213.py: the recorded clips of a real run, replayed through both paths, no profiler)

1,882 clips recorded by `code/profclip213.py` (a stride-67 sample of the 233,717 library clips of the BEFORE run,
i.e. the clip memo's MISSES), 153 distinct obstacles, 607 distinct tilt bins.  **0 mismatches** (rect, `stats`
delta and trace) and **0 record-vs-replay differences** (the replay reproduces what the run itself computed).

| primitive (per call) | calls | library | integer space | gain |
|---|---|---|---|---|
| `_clip_rect_obstacle` (recorded clips, (obstacle, bin) pair warm as in a run) | 1,882 | 0.787 ms | 0.085 ms | **x9.2** |
| `_clip_rect_obstacle` (same, pair COLD -- one compile per clip, the sampling's artefact) | 1,882 | 0.787 ms | 0.211 ms | x3.7 |
| `dead_poly` -> `dead_int` (the exact test) | 3,284 (fuzz) | 112.2 us | 12.6 us | x8.9 |
| `_dead_poly_f` -> `dead_f` (the search twin, bit-identical) | 3,284 (fuzz) | 13.8 us | 4.1 us | x3.4 |
| the whole clip (fuzz: random obstacles / bins / rects) | 450 | 1.31 ms | 0.16 ms | x8.0 |

`exact_calls` 11,095 and `backoffs` 22 over the replayed clips -- identical on both paths, so the certificates cite
the same counts.  The integer widths reached: VD 30, CW 74-83, G 51, EA 79, EU 109-110 bits, **widest product 229
bits** (`notes/int_clip.md` s.3).

Phase 2 (`A213_CLIPFILTER=1`, the rigorous float filter on family A with exact fallback): 0.090 ms per clip against
0.085 ms for the plain integer path on the same warm data -- **no gain**, 1,498 filtered / 4,689 exact fallbacks,
0 mismatches.  The filter is correct and it stays DEFAULT OFF: once the (obstacle, bin) pair is compiled, a
150-bit integer multiply is not slower than two `float(bigint)` conversions plus the error bound.

## Per run (code/profclip213.py under cProfile; the stage table by code/stages213.py)

| stage / function | BEFORE calls | BEFORE s | AFTER calls | AFTER s |
|---|---|---|---|---|
| run_page (wall; 900 s wall + the last node) | 1 | 944.6 | 1 | 952.1 |
| tree normalise (the coarse fixed point) | 11 | 132.7 | 13 | 96.2 |
| MBox.rebuild (library-level, memo misses) | 471 | 50.9 | 523 | 69.8 |
| **`_clip_rect_obstacle` (library / integer space)** | **214,490** | **417.7** | **273,306** | **65.1** |
| &nbsp;&nbsp;`dead_poly` -> `dead_int` (the exact test) | 1,201,640 | 290.3 | 881,960 | 4.8 |
| &nbsp;&nbsp;`_dead_poly_f` -> `dead_f` (the search twin) | 1,641,230 | 121.1 | 2,231,584 | 11.9 |
| &nbsp;&nbsp;`_m_lt_half` + `_m_lt_half_f` (A131, now inlined) | 22,384,467 | 124.4 | 50 | 0.0 |
| &nbsp;&nbsp;`_bisect_boundary` (A131, reused verbatim) | 22,480 | 161.6 | 30,214 | 14.8 |
| &nbsp;&nbsp;`IPair` (the per (obstacle, bin) compile) | 0 | 0.0 | 24,945 | 36.1 |
| no-room leaf (noroom189; contains the clips) | 11 | 762.7 | 13 | 814.6 |
| role reach depth 0 (fastclip211.reach0) | 321 | 25.7 | 377 | 16.9 |
| Fraction arithmetic (`_mul` + `_add` + `_sub` + `math.gcd`) | 331.6 M | 226.1 | 130.6 M | 84.1 |

**417.7 s -> 65.1 s** on a run that did MORE clips (273 k vs 214 k): per call 1.95 ms -> 0.24 ms, **x8.2** under the
profiler, x9.2 without it.  Fraction arithmetic across the whole run drops from 332 M to 131 M calls.  The clip was
44 % of the BEFORE wall and is 6.8 % of the AFTER wall.

**And it bought work.**  Inside the same 900 s wall the AFTER run expanded 13 nodes (depth 4, 6 role splits, 12 dead
leaves) against 11 (5 role splits, 11 dead leaves).  Of the 17 nodes both runs reached, **16 carry the identical
verdict**; the 17th is `R.1.4.2.2.2.2`, which BEFORE left ALIVE at the wall and AFTER expanded into two children
(one DEAD NOROOM, one ALIVE at the wall).  Every DEAD NOROOM leaf of BEFORE is a DEAD NOROOM leaf of AFTER.

**What is left.**  `IPair` -- compiling one (obstacle, tilt bin) pair to integers -- is now 36.1 of the 65.1 s, i.e.
more than half of the clip, at 1.45 ms per pair over 24,945 pairs (~11 clips per pair; the cache holds 20,000).
The compile is Fraction -> int conversion of the obstacle's vertices, normals and support intervals plus the
library's own `Bin.radii`; it is the obvious next lever (compile the obstacle once instead of once per bin, and
carry the integer form on the `Obstacle` rather than in a side cache).  After that the node is again dominated by
the K' build and the no-room leaf.

Logs: `logs/profile/{b4clip2,afclip}_k5_11_interior_Y0202.{prof,log}` (and `b4clip_*`, the recording run),
`results/run_{b4clip2,afclip}/`, `results/clips_b4clip_k5_11_interior_Y0202.jsonl`, `logs/replay_clip_b4clip.log`,
`logs/fuzz_clip213.log`.  Live differential: `A213_VERIFY=1` on one node ran both clips on every call --
25,930 verified calls (3,193 of them clips), 0 assertion failures.
