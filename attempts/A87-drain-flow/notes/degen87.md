# degen87 — GLOBAL degeneration of the exact K0-BLOCKED packings

*A87 chore, 2026-09-05. Code `code/degen87.py`; results `results/degen87.{json,jsonl,log}`.
One process, `OMP_NUM_THREADS=1`, 525 s wall, ~0.3 GB.*

## Headline

**6 of the 8 exact K0-BLOCKED packings degenerate, at the SAME side, into a class that is dead
on the window** (or into a class every one of whose window-relevant sub-tuples is dead). All 8
degenerate at all (k = 0 → 6..11 simple squares); every final configuration is an 11-square
packing certified exactly (interval SAT, gap ≥ 0, containment in the same container).
**The Trump canary does not move: zero moves from (a)/(b)/(d), and the corner-local flood fails
at all four corners** (terminal deficit 2 each) — it stays at k = 5, class `trump5`.

The PI's scratch route on the 3.985 record is reproduced and **exceeded**: aligning squares
4, 5, 6 (and 0, 3) and teleporting 7 and 10 gives not 5 but **7 simple squares**, and the
PI's `k5_10` is one of its Young sub-tuples.

## What was implemented (and how it differs from flood87)

| move | rule | why flood87 misses it |
|---|---|---|
| (a) **ALIGN** | tilt < 1°, centre within 0.01 (max-norm) of a corner-anchored lattice cell → snap to the cell exactly (θ := 0) | flood87 never perturbs an existing square |
| (b) **WALL-SLIDE** | axis-aligned square touching a wall slides along it to the nearest cell on that wall; full snap first, else the maximal feasible fraction by bisection (≥ 1e-4 to count) | flood87 only slides into a *completable slot of one corner diagram* |
| (c) **FLOOD** | exchange87 + flood87 verbatim, objective = largest inscribed square, on the CURRENT configuration at each corner | — (this IS flood87, reused) |
| (d) **TELEPORT** | K0-FREE at the **cell** level: a cell met by exactly one square receives it. (d0): a cell met by nothing receives the nearest off-cell square | flood87's bonus is restricted to the four corner slots / one corner's Young diagram |

**Intruder with a tangency tolerance.** A square meets a cell only if its *certified* penetration
depth exceeds `TOL_INTRUDER`; the certificate is an mpmath.iv interval on the exact rational
poses, so "certified depth > tol" is `gap_hi < -tol`. Primary 1e-6, sensitivity 1e-4.
This is the PI's first correction: on the record, the TR "nick" by square 6 is a **1.7e-8
tangency**, not a block, so at any tol ≥ 1e-6 the cell is free for square 7.

**Two implementation facts the brief did not anticipate.**

1. **The greedy must be simultaneous.** Aligning square 4 alone overlaps square 5 (gap −1.0e-4)
   and aligning 5 alone overlaps 4 (−7.0e-9); square 6's align is blocked by 7 and 7's teleport
   is blocked by 6 ("unblocked once 6 is aligned"). One-at-a-time greedy stalls at move zero.
   So targets are collected for **all** squares at once (aligns first, then teleports computed
   with already-targeted squares treated as gone, then wall slides), the whole set is applied,
   and members are dropped from the worst offending row until the configuration certifies.
   Nothing here is load-bearing: only the final exact certificate is.
2. **The greedy is path dependent**, so three tie-breaking variants are run and the best kept
   (dead beats alive, then larger k, then fewer moves). `v2` beats `v0` on two rows.

**Termination.** ALIGN, full WALL-SLIDE, TELEPORT and TELEPORT_FREE each strictly increase the
number of squares sitting exactly on a lattice cell (each is forbidden to move a square that is
already on one), which is bounded by 11. Partial slides and flood calls are capped.

**Simple squares / class naming.** Per corner, the maximal Young sub-diagram of the occupied
cells; the (corner, cell) set is mapped to A53 slot coordinates at s0 and canonicalised under
D4 (skeletons.py's action), then looked up in A53 `name_to_slots` (56 classes) + A55
`name_to_slots` (k4_00..k4_13, corners4, trump5, k3_00). Verified against the tables:
`{BL:[2,1], TL:[2]} → k5_10`, `{BL:[2,1], BR:[1], TL:[1]} → k5_11`.

**Deadness.** A56 `scoreboard.json` `window_coverage`, overlaid with the A61
`campaign61_progress` verdicts. Not dead: k5_11 / k5_16 (A57/A96 running), trump5, corners4,
every protected k ≤ 4, k0_00, and the 8 A61 stragglers still s0-only
(k5_02, k5_03, k5_05, k5_12, k5_13, k5_14, k6_21, k6_27) plus the two partial rows
(k6_07 cov 0.124, k6_23 cov 0.9985). **Kills climb**, so a class also counts as dead when one
of its Young **sub-tuples** is dead; the witness is reported per row.

## Per packing (tol 1e-6)

| packing | side | k | class reached | dead | why |
|---|---|---|---|---|---|
| `record_s0115` | **3.9854837** | 0 → **7** | TR [1,1,1] + TL [2,1,1] | **YES** | k ≥ 7; explicit witness **k6_06**, window FULL. Sub-tuples include **k5_10** (A61 CONVERTS, margin 0.0163), k5_04, k5_06, k6_09, k6_13 — all window-dead |
| `polish12_s0380` | 4.0000001 | 0 → 6 | BL [2] + BR [2] + TR [1,1] | no | the tuple is **not realisable at s0**: BL(1,0) and BR(1,0) overlap when the side is 3.877, so it is not one of the A53 strata. Its k5 sub-tuples are k5_13 / k5_14, both still A61 s0-only |
| `polish15_s0076` | 4.0000041 | 0 → **10** | BL [3,3,2,2] | **YES** | k ≥ 7 (flood adopted at BL) |
| `polish21_s0380` | 4.0000075 | 0 → 6 | BL [2] + BR [2] + TR [1,1] | no | same as polish12 (it is the same seed s0380 re-polished) |
| `polish24_s0259` | 4.0000119 | 0 → **9** | BL [4,1] + TR [1,1] + TL [1,1] | **YES** | k ≥ 7 |
| `anchored0_p140` | 4.1071074 | 0 → **10** | BL [2,2,1] + BR [2,1] + TL [2] | **YES** | k ≥ 7 |
| `anchored1_p094` | 4.0837355 | 0 → **11** | BL [2,2] + BR [2,1] + TR [1] + TL [2,1] | **YES** | k ≥ 7 (all 11 squares on the lattice) |
| `anchored2_p094` | 4.0837359 | 0 → **11** | same | **YES** | k ≥ 7 |
| `TRUMP_canary` | 3.8770836 | 5 → 5 | **trump5** | n/a | **0 moves**; flood fails at BL/BR/TR/TL, terminal deficit 2 each — **CANARY PASS** |

**Caveat on the seven non-record rows.** Only `record_s0115` is BELOW side 4. The four polish
rows sit at 4.0000001–4.0000119 and the three anchored rows at 4.084–4.107, where a unit
lattice is roomy (16.7–16.9 area for 11 unit squares) and grid-packing is geometrically easy.
Their degeneration is therefore weak evidence about the window [3.82, s0). **The one
substantive result is the record at 3.98548**, which is the packing the residue map calls the
interlock.

### The record's move sequence (variant v0 — the PI's route, verbatim)

```
ALIGN     sq3  -> TR(0,2)   travel 1.70e-08   tilt 0.0000 deg
ALIGN     sq4  -> TL(1,0)   travel 5.16e-05   tilt 0.0059 deg
ALIGN     sq5  -> TL(0,0)   travel 1.99e-04   tilt 0.0059 deg
ALIGN     sq6  -> TR(0,1)   travel 6.08e-06   tilt 0.0000 deg     <- the "nick" was a tangency
TELEPORT  sq7  -> TR(0,0)   travel 5.94e-01                       <- sole intruder of the TR corner cell
ALIGN     sq0  -> TL(0,2)   travel 2.11e-04
TELEPORT  sq10 -> TL(0,1)   travel 3.84e-01                       <- "the cell below TL", PI's 0.38
```
Seven moves, no flood needed, and the result is an 11-square packing in the same container with
certified min pair gap 0 (exact tangencies) and certified containment. The best-scoring variant
(v2) reaches the same class in 6 moves by letting the TL flood contribute one step.

## Sensitivity: the tangency bar at 1e-4

| packing | tol 1e-6 | tol 1e-4 | same? |
|---|---|---|---|
| record_s0115 | k 7, dead | k 7, dead | **yes** |
| polish12/21 | k 6, not dead | k 6, not dead | yes |
| polish15_s0076 | k 10, dead | k 3, not dead | **no** |
| polish24_s0259 | k 9, dead | k 2, not dead | **no** |
| anchored0_p140 | k 10, dead | k 0, **no move at all** | **no** |
| anchored1/2_p094 | k 11, dead | k 11, dead | yes |
| TRUMP_canary | k 5, trump5, 0 moves | k 5, trump5, 0 moves | yes |

Raising the bar to 1e-4 *loses* moves rather than gaining them: a cell whose only obstruction
is 1e-5 deep is then reported free, the move is proposed against a square that is really there,
and it fails the exact validity check. So 1e-4 is too coarse for these packings; **1e-6 is the
right bar and the headline row (the record) is insensitive to the choice**.

## What this does and does not say

* It **does** kill the specific 3.985 interlock as an obstruction: the corner-local flood stalls
  there, but the global move set converts it to k = 7 at the same side, and every relevant
  sub-tuple of that class is window-dead. Two lessons of the PI's note are confirmed
  operationally: a tangency-level intruder must not count as a block, and the degeneration move
  set must act at the **cell** level, not the corner-slot level.
* It **does not** prove the degeneration lemma. Eight sample points are not a theorem, seven of
  them sit at side ≥ 4 where the statement is easy, and two of those seven (`polish12`,
  `polish21`) *fail* to reach a dead class — they stop in a k = 6 tuple that does not even
  exist at s0. The candidate theorem in residue_map §8.1/§8.2 ("an interlocked frame is a
  critical configuration and the only critical frames are Trump's") is untouched.
* The canary behaves exactly as required, which is the only evidence here that the move set is
  not simply "any packing degenerates": on Trump, all four moves are unavailable.

## Files

* `code/degen87.py` — the whole thing (moves, certifier, Young/class naming, deadness table).
* `results/degen87.json` — summary (headline, canary, per-packing, sensitivity).
* `results/degen87.jsonl` — one row per (packing, tolerance): full move list, exact final
  configuration as rationals, certificates, variants tried.
* `results/degen87.log`, `results/degen87.out` — run log.
