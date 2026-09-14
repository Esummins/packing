# A214 -- timing: the C kernel for the vertex certification (per call and per run)

Machine as always (BelowNormal pythons via A210's fix, BLAS pinned, `PYTHONDONTWRITEBYTECODE=1`, the lab's other
workers running).  clang 22.1.8 (x86_64-pc-windows-msvc), `build/ckernel214.dll` 8,704 bytes, sha256
`c134be3741468ccbba0e609dedf8e7578b2865518b19c09d34240055512d6139`.
BEFORE = `A214_CKERNEL=0` (A213's Python-int path), AFTER = `A214_CKERNEL=1`; `A213_INTCORE=1` in both,
`A213_INTCLIP` unset and its default still OFF at the time the two runs were taken (A213b flipped it ON when it
landed, after these runs), so the clip is the library's Fraction clip in BOTH columns and the only difference
between them is the vertex kernel.

## 1. Differential tests -- 0 mismatches everywhere (`python tests/all214.py`, `logs/all214.log`)

| test | what it compares | samples | mismatches |
|---|---|---|---|
| `diff214` exact layer | `a214_vertex_ok_exact` (the 192-bit path, run on EVERY sample whether or not the filter would have decided it) vs `polycore_int.vertex_ok_h` | 25,200 in-envelope (7,200 grid + 18,000 wide) of 46,800 | **0** |
| `diff214` filter layer | `a214_vertex_filter`, every answer it DECIDES, vs the same reference | 25,200 (601 undecided -> exact) | **0** |
| `diff214` full kernel | the kernel as installed (filter, exact, Python fallback) | 46,800 | **0** |
| `diff214` batch | `a214_cert_batch` on 300 (16 x 2-6) grids vs the reference loop | 300 grids | **0** |
| `diff214` envelope | W ~ 2^61..2^70 (the axis-core shape): the kernel must REFUSE and Python must answer | 200 | **0** |
| A213 `replay213` | all 441 recorded `MBox.rebuild`s of the Y0202 pad-0 run (181 union, 260 pieces) through the library build and the integer build, kernel OFF and kernel ON | 441 x 2 | **0** (and 0 record-vs-replay) |
| A213 `fuzz213` | 150 random piece sets, 2,700 vertex tests (incl. exact-boundary points), 75 polygon cases | -- | **0** |

Coverage inside the kernel on the `diff214` pass (`a214_counters`): 163,307 quadratics decided by the exact
192-bit path, of which 19,061 failed on an endpoint value and 3,315 went through the interior minimum (the
discriminant `4AC - B^2`, the widest arithmetic in the kernel; 21 of them negative), 32 refused by the envelope
guard.  `A214_VERIFY=1` (both paths on every call, asserted equal) was also run clean.

## 2. Per call

`tests/replay213.py` on the 441 recorded rebuilds, no profiler, kernel OFF then ON.  `lib` is A132/A171 on
Fractions; `int` is A213's Python-int path, which is where the kernel is installed.

| primitive (per call) | calls | library | A213 Python-int (kernel OFF) | A214 C kernel (kernel ON) | C vs Python-int |
|---|---|---|---|---|---|
| MBox.rebuild (whole, library-level) | 441 | 361 / 333 ms | 53 ms | 46 ms | x1.15 |
| polycore.build (per piece / union hull) | 3349 | 25.8 / 23.9 ms | 4.8 ms | 4.3 ms | (float pipeline, not in C) |
| intersect_frac -> intersect_h | 441 | 25.9 / 24.5 ms | 1.5 ms | 1.4 ms | (not in C) |
| **certify_verts** (nv x N pieces, all pass) | 260 | 56.0 / 51.9 ms | **2.0 ms** | **0.2 ms** | **x10** (x321 vs the library) |
| the same through `polycore_vec` | 260 | -- | 0.71 ms (numpy float filter) | 0.10 ms (C batch) | **x7** |
| axis_core_pieces | 260 | 15.6 / 14.6 ms | 0.6 ms | 0.6 ms | 1.0 (its corners are outside the envelope -- s.3 of the notes) |

Throughput of the kernel itself (`diff214`, 16 certified vertices x 12 piece boxes = 192 pairs = 3,072 quadratic
tests, all passing, so nothing short-circuits):

| | per call | per (vertex, box) pair | per quadratic test |
|---|---|---|---|
| `a214_cert_batch` (the C call alone) | 50.5 us | 263 ns | **16 ns** |
| + the ctypes / Python wrapper (array marshalling, the row scan) | 89.1 us | 464 ns | 29 ns |
| `polycore_int.vertex_ok_h` loop (Python ints) | 2,015 us | 10.5 us | 655 ns |

16 ns a test is what A213 s.6 predicted for a C loop ("~10-20 ns").  The scalar drop-in is a much smaller win --
1.97 us vs 4.50 us a call (x2.3) -- because a ctypes call costs ~1 us: the batch entry point is the one that matters.

## 3. Per run (`code/profrun214.py`, Y0202 pad 0, wall 900 s, isolated cert / results dirs, `--no-fig`, cProfile)

`calls | s` = calls, cumulative seconds.  Caveat: the AFTER run shared the machine with the differential-test
suite for ~6 minutes of its wall (deliberately -- the bias is against A214), on top of the lab's other workers.

| stage / function | BEFORE calls | BEFORE s | AFTER calls | AFTER s |
|---|---|---|---|---|
| run_page (wall; 900 s wall + the last node) | 1 | 909.9 | 1 | 941.9 |
| tree normalise (the coarse fixed point) | 9 | 122.1 | 11 | 132.9 |
| MBox.rebuild (library-level, memo misses) | 395 | 46.3 | 471 | 51.0 |
| pieces_poly | 343 | 42.6 | 419 | 46.8 |
| polycore.build (per piece / union hull) | 3827 | 38.5 | 4511 | 43.9 |
| _clip -> _clip_np | 1516584 | 28.7 | 1786356 | 33.0 |
| _simplify -> _simplify_np | 3978 | 4.7 | 4669 | 5.6 |
| intersect_frac -> intersect_h | 343 | 2.4 | 419 | 2.8 |
| axis_core_pieces | 343 | 0.6 | 419 | 0.7 |
| exactcore.exact_core | 395 | 2.3 | 471 | 2.7 |
| vertex_ok, all callers | 32864 | 0.8 | 39344 | 0.9 |
| **vertex_ok_h (the Python integer kernel)** | 255366 | **3.5** | 65142 | **0.9** |
| **ckernel214.vertex_ok_h (C, scalar)** | 0 | 0.0 | 105588 | 0.9 |
| **ckernel214.certify_h (C, batch)** | 0 | 0.0 | 838 | 0.7 |
| **ckernel214.cbox_of (the per-box compile)** | 0 | 0.0 | 127002 | 0.4 |
| _clip_rect_obstacle (A131 pin-clip, NOT touched) | 217010 | 444.9 | 214490 | 419.5 |
| dead_poly (its exact test) | 1219442 | 310.1 | 1201640 | 291.4 |
| _bisect_boundary (A131, reused) | 23522 | 170.7 | 22480 | 162.3 |
| no-room leaf (noroom189; contains rebuilds + clips) | 8 | 744.8 | 11 | 760.7 |
| role reach depth 0 (fastclip211.reach0) | 265 | 23.1 | 321 | 25.0 |
| Fraction arithmetic (_mul + _add + _sub + math.gcd) | 335.4 M | 232.1 | 330.9 M | 226.1 |

Per run: the whole vertex-certification stage is 3.5 s BEFORE and 2.9 s AFTER (0.9 + 0.9 + 0.7 + 0.4, the wrapper
included) **while doing 19% more rebuilds** -- 8.9 ms a rebuild -> 6.2 ms a rebuild under the profiler (the
profiler charges per Python call, which is exactly what the batch removes).  Inside the same wall the AFTER run
expanded **11 nodes against 9** (471 vs 395 rebuilds), and the two frontier nodes the BEFORE run left ALIVE at the
wall (R.1.4.2.2.2.1.1.2, R.1.4.2.2.2.1.2) both came back DEAD in the AFTER run.  Verdicts agree on every node both
runs finished: 14 of the 17 recorded nodes are field-identical with the time fields stripped; the three that are
not are the two the BEFORE run never finished and the new wall leaf.  The one shared internal node whose record
differs is R.1.4.2.2's no-room `pockets`, in the 5th decimal of one extent (`2.585622` vs `2.585611`) -- the same
deadline-bounded `bisect_free` A213 recorded, same verdict UNDECIDED, same pocket count.

What the kernel actually did in the AFTER run (`ckernel214.rep()` at the end of `logs/run_on.log`): 419 batch
calls covering **160,580 (vertex, box) pairs, every one decided by the float filter in C** -- 0 exact C tests, 0
pairs handed back; 83,274 scalar C calls; and the fallback firing exactly where s.3 of the notes says it will --
22,314 scalar calls and 419 batches (the axis core's four corners over `den aden Q`) went to Python because their
W is outside the proved envelope.

## 4. Reading

* The kernel is what A213 s.6 asked for and it is 16 ns a quadratic test, ~40x the Python-int path per pair.  But
  the honest per-run number is that the certification was ALREADY only 3.5 s of a 910 s node after A213: this
  buys ~0.6 s a run directly, and the visible effect (11 nodes vs 9) is mostly that a run at the wall is a race
  where every second of rebuild is a second not spent on the clip.
* What a node costs now is `_clip_rect_obstacle` -- 445 s of 910 (and 745 s of the wall sits inside the no-room
  leaf, most of it the same clip).  A213b's integer clip (`A213_INTCLIP`, default OFF while these two runs were taken, flipped ON when A213b
  landed) is the first lever, at x9.2 a clip.  A C kernel for it afterwards is feasible but is a DIFFERENT kernel:
  A213b's measured bound is 229 bits (four limbs, not three) and it GROWS with tree depth, and its float filter
  measured no gain (0.090 vs 0.085 ms a clip) -- so there the integer path is what belongs in C, with a guarded
  envelope and a Python fallback like s.3 of `notes/c_kernel.md`.
* The one structural lesson for the next kernel: the win is in the BATCH entry point, not the scalar one.  A
  ctypes call costs ~1 us, which is a quarter of a Python-int certification; `a214_cert_batch` amortises it over
  192 pairs and pays 16 ns a test.
