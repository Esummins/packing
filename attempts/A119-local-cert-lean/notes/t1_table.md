# A119 T1 — the exact certificates and the independent checker

Generator `code/exact119.py` (float LP + rational rounding of the multipliers to a
denominator of 2^40, each vector re-verified by weak duality before it is written);
checker `code/check_local.py` (no numpy, no scipy, no tree code — dyadic interval
arithmetic on Python ints at scale 2^-96, `code/exactiv.py`).  `s0 = 969271/250000`.

| certificate | cells (bisections) | selection branches | infeasible cells | dead leaves | multipliers | file | sha256 | gen wall | checker wall | checker's min bound | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `S02_k5_11_r0.02_rho2` | 0 | 7 | 0 | 8 | 128 | 0.0 MB | `d09f94031eca93d1` | 0.0 s | 0.3 s | 3.880152397 | **VALID** |
| `S02_k5_11_r0.05_rho20` | 8512 | 63 | 4420 | 7692 | 82593 | 0.8 MB | `dfedcf40d3d9f46c` | 26.4 s | 125.7 s | 3.877094349 | **VALID** |
| `S02_k5_11_r0.10_rho10` | 6782 | 47 | 1012 | 6878 | 100056 | 1.1 MB | `baa2fe8a9aedd4dc` | 18.3 s | 139.4 s | 3.877094910 | **VALID** |
| `S02_k5_11_r0.20_rho10` | 32426 | 63 | 5782 | 32570 | 504404 | 5.6 MB | `41fa6e5a9da74c76` | 91.0 s | 694.9 s | 3.877084098 | **VALID** |
| `S07_trump5_r0.05_rho10` | 412 | 31 | 48 | 476 | 6186 | 0.0 MB | `825253afaf56aa57` | 1.0 s | 9.6 s | 3.877445286 | **VALID** |
| `S07_trump5_r0.10_rho40` | 2410 | 87 | 1038 | 2302 | 27363 | 0.3 MB | `1b06f5e0dece0fa9` | 7.6 s | 27.7 s | 3.877097589 | **VALID** |
| `S07_trump5_r0.20_rho10` | 3104 | 31 | 272 | 3168 | 48710 | 0.6 MB | `ddef2e30d807122f` | 8.7 s | 74.8 s | 3.877084433 | **VALID** |

## What one certificate contains

* `meta`: the bodies (each free body's centre box and tilt interval, each pin's
  `(alpha, beta, h)` slack core, the LP variable indices), the side window, the tilt
  cut, `s0` as the exact fraction `969271/250000`, and the kill margin `1e-8`.
* `root`: the proof tree.  `bisect` nodes split one body's tilt interval at a recorded
  point (the two children cover it); `branch` nodes list the selections their children
  assume for one near pair (the checker verifies every OTHER selection has
  `sup [g] < 0` on the cell, so Lemma SAT leaves no third case); `qsplit` nodes would
  split a q-range (NONE occurs — see `notes/method.md` finding F1); `imp` / `imp_sel`
  leaves are cells where some pair has no possible selection at all; `dead` leaves
  carry the selections the multipliers use, which of them are FORCED rather than
  supplied by a branch, and the rational Farkas vector — a value `> s0` for a bounded
  leaf, a Farkas RAY (`infeas: true`) for an infeasible cell.
* `certs/manifest.json`: sha256, size, node counts and the generator's own certified
  minimum per file.

## What the checker does (and does not) trust

It trusts the certificate for NOTHING except the shape of the search: it rebuilds every
row of Lemma RELAX itself, from the cell and the boxes, in exact dyadic interval
arithmetic (rigorous `pi`, `cos`, `sin`, and the EXACT range of `|cos| + |sin|`), it
verifies every excluded selection's enclosure itself, and it evaluates the Farkas bound
itself.  A multiplier vector is data; a wrong one simply fails.  The checker shares no
code with the generator and imports neither numpy nor scipy nor any tree module.

