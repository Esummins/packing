# A120 — the NO-side runner: construction, soundness, and what it is not

`code/noside120.py` (T1), `code/control120.py` (T2), `code/report120.py` (T3), all on
`code/a120lib.py`. A112's `regiontree.py` / `caselp.py` / `octagon.py` / `pinguard.py` /
`trim57.py` / `certify.py` / `verify_case.py` are **imported, never copied**, and A112's writable
directories (`RES`, `NODES`, `CERTS`, `RT`, `LOGS`) are redirected into this attempt before
anything runs. A53/A57/A96/A107/A112/A116/A119 are read-only; every campaign node json is copied
into `results/nodes/<nid>.src.json` before it is opened.

## 1. The cover

For a target node whose support lies inside A116's certified neighbourhood
`N = S02_k5_11_r0.20_rho10` (A119's export), with `F_1..F_4` N's four per-square boxes carried
into the node's own frame:

```
node  =  YES  ∪  NO_1 ∪ NO_2 ∪ NO_3 ∪ NO_4                            (a tautology)
YES   =  node ∧ (for every i, some square of the packing has its pose in F_i)
NO_i  =  node ∧ (no square of the packing has its pose in F_i)
```

The right-hand side is the negation-normal form of `¬(A_1 ∧ A_2 ∧ A_3 ∧ A_4) ∨ (A_1 ∧ … ∧ A_4)`
with `A_i` = "some square's pose is in `F_i`". It is a **cover**, not a partition — the `NO_i`
overlap each other — which is exactly what the Lean composition takes unions of. No box is
consumed as a core, no budget is dropped, and nothing about the node's own hypothesis changes on
either side.

## 2. Why the YES leaf is free

`YES ⊆ N`'s hypothesis, so Theorem LOCAL kills it with no LP. The containment needs four things,
all asserted per node in the record's `soundness` block:

* **A1** the node's five pin boxes ARE N's pins carried into the node frame — same centres to
  1e-9, tilt exactly 0, half-width exactly A57's slack `PIN_SLACK = 10⁻²/√2`. (For `k5_11` the pin
  set is its own image under `diag`, which is why A107's `struct_op` for every in-N node is `e` or
  `diag` and why the pins map onto themselves.)
* **A2** the four mapped boxes are pairwise **pose-disjoint** (`octagon.boxes_pose_disjoint`, tilt
  compared mod 90). Without this, two of the `A_i` could be witnessed by the *same* square and
  YES would not give the |L| **distinct** squares N's hypothesis names.
* **A3** each mapped box is pose-disjoint from every pin box, and `pinguard.classify` does not
  return `parent` — so the four squares are distinct from the pins as well ("a DISTINCT **other**
  square").
* **A4** the D4 map is exactly invertible (mapping the boxes back by `struct_op` reproduces
  A119's numbers to 0.0), plus a dense pose sample that round-trips into the class boxes.
* **A5** the node's own A107 configuration lies in the mapped boxes — A116's `consumer116.inside`
  test recomputed in the node frame, reproducing its `dmax`/`tmax` exactly (e.g. `Y0230`:
  0.0099 / 1.815°, as in `A116/results/t3_consumer.json`).

The node's own conditioned bin is an **extra** constraint on top of N's hypothesis, so it can only
shrink the set: `node ∧ YES ⊆ YES(N) = ∅`. It never has to be pose-disjoint from the `F_i` — the
witness of `A_i` is allowed to be the conditioned square, since N only asks the |L| squares to be
distinct from *each other* and from the pins.

The YES kill is recorded as
`dead by local certificate A116 S02_k5_11_r0.20_rho10 (pending A119 rational/Lean form)`
and is **never counted with the frozen-verifier kills**: today it is a prose+numeric certificate,
not a replayable one.

## 3. Why the NO side uses the same boxes in the same frame

The soundness-adjacent failure this attempt exists to prevent is a YES side and a NO side built
from *different* boxes: the cover would then not be a tautology and every NO LP would be
under-constrained, with nothing downstream failing. Two guards:

* the mapped boxes are written into the record as `boxes_used`, and the YES claim's own box list
  (`yes.boxes`) is that same list;
* every NO child carries `box_identical_to_yes`, re-derived at the moment the `NoFam` is built,
  and the runner **asserts** it before the LP: same tilt intervals mod 90
  (`octagon.theta_intervals`), and a zone that is the box's centre rectangle clamped to
  `[1/2, s−1/2]`. The clamp is the only difference and it discards no pose a unit square could
  have — a unit square's centre is at least `w(θ)/2 ≥ 1/2` from every wall — so
  "some square's pose in `F`" and "some square's pose in `clamp(F)`" are the same statement and
  the two children still cover the parent exactly. (`BR(0,1)`'s box is the one that clamps: its
  `x1 = 3.577084 > s₀ − 1/2`.)

**A7** additionally asserts what A111's bug B5 cost: every tilt interval fed to a kill is inside
`[0, 90]` (a reflection produces negative tilts, and `pinguard.tight_a` / `trim57.dead_by_pin` are
stated only on `[0, 90]`), and every core half-side is `≤ 1/2`.

## 4. The NO side itself

A112's protocol, run by calling A112's own code (`regiontree.Runner.lp`,
`regiontree.certify_leaf`), unmodified:

* stage 1 `caselp.solve_node` at 240 s, warm-started from the node's own campaign LP result;
* `η ≤ −10⁻³` goes straight to the frozen certifier, converged or not — the certificate is the
  verdict, never `τ`;
* only a child that is not clearly below budget escalates to the 900 s cap, and only one still on
  the knife edge (`|η| < 10⁻⁶`) afterwards counts ALIVE;
* the kill is `certify.py --jobs 1 --rounds 1 --depth 56` → the frozen `verify_case.py`
  (sha256 `521cb01f…`, the FREEZE_TAGS value). A **FAILing certificate leaves the child ALIVE**.

Every NO certificate is a **fixed-side** certificate at `s₀` and is tagged
`s0-only, pending window re-verification (v2 available)`. A117's `verify_param_v2.py`
(sha `153029ba…`) would discharge a NO family over the whole window, but a 4-D NO re-verification
costs ~10× the four fixed sides it replaces, which does not fit this attempt's 15 CPU-h cap.

## 5. What this is not

* It is **not** a window kill. Both sides are `s₀`-only: the YES side because A116's N is anchored
  at `s₀` (its window `[3.82, 3.897084]` is the hypothesis' `s` range, but Theorem LOCAL's
  conclusion is "no packing at side ≤ s₀"), the NO side because `verify_case.py` is a fixed-side
  verifier.
* It is **not** a frozen-verifier kill on the YES side. A node is CLOSED only in the mixed sense:
  YES by local certificate, all four NO children by `verify_case.py`.
* It launches **no campaign driver**. A57/A96 stay paused; `pausegate.paused()` is checked between
  nodes so a sentinel stops the run cleanly with every finished node recorded.

## 6. What the run measured (2026-09-07, 14.4 CPU-h against a 15 CPU-h cap)

`results/t3_report.json`, `results/t2_controls.json`, ledger
`attempts/A96-a57-parametric/results/a120_closures.jsonl` (35 rows, one per target).

**Nodes.** 9 of the 35 targets processed (all level 1, cone-value order); **4 CLOSED**
(`Y0230`, `Y0637`, `Y0709`, `Y0997`), 5 OPEN, 26 not run — the CPU cap, not a verdict. A closed
node is dead at s₀ in the mixed sense: YES leaf by A116's local certificate, all four NO children
by the frozen `verify_case.py`. Trump's grain satisfies **none** of the 19 hypotheses declared
dead (`trump_realizes = False` on every one; the canary must be 0 and is).

**Children — and the two very different reasons a NO child stays alive.** 36 NO children:

| | count |
|---|---|
| LP puts the child clearly below budget (η ≤ −10⁻³) | **31 / 36** |
| certified dead by the frozen verifier | 19 |
| **genuine survivors** (converged LP, η = 0, τ = 5 = budget) | **5** |
| certifier shortfall (η ≤ −10⁻³, certificate FAIL or CAP) | 12 |

The NO side is strong at the LP: only 5 of 36 children survive the node LP at all, and 4 of those
5 are the one node `Y0345`, whose four NO children each converge at exactly τ = budget. **The
binding constraint is certification, not the LP.**

**Why certification is the constraint, quantitatively.** `certify.py`'s auto-scale is
`max(1.005, min(1.4, (budget − 0.005)/τ − 0.002))`, which for these children is 1.03–1.11, so the
emitted measure covers the LP's own rows only where the LP's `minmass` ≥ 1/scale ≈ 0.90–0.97.
Measured `minmass` on the NO children is 0.43–1.00, median ≈ 0.70: the 240 s stage-1 LP is far
from converged and its measure is not coverable as emitted. Every kill therefore has to come out
of `certify.py`'s witness-feedback loop, and **A112's `--rounds 1` is not enough here**: of 11
first-attempt PASSes the times were 4–680 s, while 6 children that FAILed at rounds 1–3 PASSed at
rounds 6 (690 s, 855 s, 963 s, 1207 s, 1273 s, 1788 s, 1832 s, 2470 s). All four closures needed
the rounds-6 pass. This is a real limit on A111/A112's datum "waiting for column generation buys
nothing": it holds when η is deeply below budget, and fails here, where η ≈ −0.25 leaves a
certificate margin of only 0.3 % (total ≈ 4.9855 against budget 5).

**Operational note (recorded because it cost a promotion).** Two processes must never write the
same node record. A re-certification pass running against a node a worker was still inside had its
promotion clobbered by the worker's next save (`Y0637/NO0`, 00:54). `recert120.candidates()` now
takes only records whose status is already `OPEN`, and the pass is sharded by node, never by
candidate.

**Certifier wall.** `a120lib.certify_leaf_capped` is `regiontree.certify_leaf` plus a hard wall on
the subprocess (A112's call, argument for argument, and the whole tree is killed on the wall so no
`verify_case.py` is orphaned). A capped run is recorded as `CAP` and is treated exactly like FAIL
— A117's rule that a verification cap must sit where it can only abort, never decide. Measured:
without a wall one child burned 1895 s and another 3600 s without certifying.

## 7. The controls (T2), all green, run BEFORE the run

`results/t2_controls.json`, `logs/control.log`. Total 730 s.

* **C1 — A112's two end-to-end kills.** `k5_11_interior_Y0036_D07_D01` and
  `k5_11_interior_Y0276_D05` are T5″ root kills (`TRIM-EMPTY`, no LP, no certificate). Replayed
  through this runner's own `regiontree.logic_kill`, in all four of A112's orderings: **8 of 8
  `logic` records byte-identical** to A112's stored ones (SHA-256 of the canonical JSON compared).
* **C2 — A112's 35 PASSing NO certificates.** Replayed, never re-emitted (`certify.py --loop_cols`
  re-solves before emitting, so emission is wall-clock dependent while the verifier is
  deterministic — A57 `code/FREEZE_TAGS.txt`). Each stored certificate was copied here and driven
  through `certify.run_verifier(cert, jobs=1, depth=56, max_w=64)` → `verify_case.py`
  (sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`, the FREEZE_TAGS
  value). **35/35 PASS; every report field identical** except the certificate's own path and
  `time_s` — 9 819 930 boxes re-verified in 545.2 s.
* **C3 — the covering assertion, in the NODE frame, on the mapped boxes.** Three targets
  (`Y0230` op `e`, `Y0637` op `diag`, `Y0036_D07_D00` op `e`), A116's `sample_check` procedure:
  poses uniform in the four mapped boxes, pin offsets uniform in the slack cores, each survivor
  tested at 30 sides spanning `[3.82, s₀]`.

  | node | op | drawn | tested (survivors) | hits |
  |---|---|---|---|---|
  | `k5_11_interior_Y0230` | e | 2 996 097 | 100 000 | **0** |
  | `k5_11_interior_Y0637` | diag | 3 003 131 | 100 000 | **0** |
  | `k5_11_interior_Y0036_D07_D00` | e | 2 988 914 | 100 000 | **0** |

  (An earlier pass at the brief's 10⁴ bar: 302 460 / 301 445 / 297 951 drawn → 10 000 tested → 0
  hits each.) Best packing margin over all survivors and all sides: −0.0508 to −0.0674, i.e. every
  survivor misses being a packing at `s₀` by ≥ 0.05 — nowhere near a boundary case.

  The A4 frame round-trip sample, run per node inside the runner, adds **18 000 drawn → 18 000
  tested → 18 000 inside the class boxes** across the 9 processed nodes (a miss would mean the
  mapped box is not the image of A119's box).

## 8. The frame map is established for the whole target set, not just the run

`results/soundness_all35.json` runs A1–A7 on **all 35 in-N alive targets** (1.6 s, no LP), whether
or not the CPU cap let the node be solved: **35/35 ok**, YES/NO boxes identical in the same frame
on every one, and the frame round-trip sample totals **70 000 drawn → 70 000 tested → 70 000
inside the class boxes** (0 misses, max round-trip error 0.0). A107's `struct_op` over the 35 is
`e` × 15 and `diag` × 20, matching `N_boxes.json`'s `frame_ops` (the stabiliser of the `k5_11` pin
set), and A5 reproduces A116's `t3_consumer` `dmax`/`tmax` per node exactly. So the construction —
the soundness-adjacent half of this attempt — is settled for all 35; only the LP/certifier half is
capped at 9.

## 9. Continuation (2026-09-07 07:05–08:09): stopped by the sentinel, not by the cap

Coordinator's continuation: the 26 unprocessed targets in cone-value order with **certification at
rounds 6 from the start**, then the open NO children of the partial nodes at rounds 6; fresh
15 CPU-h cap, controls not repeated, same tags, ledger appended.

**It ran for 2.06 CPU-h and then stopped itself.** At 07:57 the owner of A123 wrote
`attempts/A57-shadow-trees/PAUSE` ("A123 night shift ended 2026-09-07 08:00 PDT … scheduled end of
the night's compute window"). `pausegate.paused()` checks **both** A57's and A96's sentinels, so
both A120 workers stopped **between nodes** with every finished node recorded — the sentinel path
working exactly as designed, not a kill. The sentinel is another owner's control file: it was left
in place, nothing was deleted or bypassed, and the second phase (the open NO children at rounds 6)
was **not launched**, because it would stop on the same check.

Net: 2 more targets (`Y1099`, `Y1116`, both level 1) → **11 of 35 processed, still 4 CLOSED, 7
OPEN, 24 not run**, all resumable on `(cls, id)`. Ledger `a120_closures.jsonl` is now
append-with-revision (rev 2 added the two changed rows; a re-run that changes nothing appends
nothing; **the reader takes the last row for each id**).

**The rounds-6-from-the-start change paid, and here is the distribution the next owner needs.**
`certify.py` returns on the FIRST PASS, so extra rounds are free on a child that certifies at once
and are the only thing that converts one whose first emission is not coverable. Over all 43
certification attempts (21 PASS, 9 FAIL, 13 CAP), the **round the certificate actually came out at**
(0-based, 0 = the very first emission):

| passing round | 0 | 1 | 2 | 3 | 4 | 5 | 6+ |
|---|---|---|---|---|---|---|---|
| passes | 5 | 6 | 4 | 2 | 3 | 1 | **0** |
| cumulative fraction | 0.24 | 0.52 | 0.71 | 0.81 | 0.95 | 1.00 | 1.00 |

Wall seconds: PASS n = 21, min 3.6, p50 568, p75 1207, p90 1832, **max 2470**, total 15 646 s;
FAIL n = 9, p50 375, max 3385; CAP n = 13, p50 420, max 3600 (right-censored, never a verdict).

**Recommended default:** `--rounds 6` with a hard wall of **2600 s** and `--time_limit 420`.
Nothing observed passed later than round 5 or later than 2470 s, so that wall censors nothing seen;
`--rounds 1` would have taken only 52 % of the passes and `--rounds 3` 81 %. The cost of the
generosity is bounded by the wall, and every capped attempt is recorded as CAP.

**A negative worth recording: survivor count does not track distance from the S02 minimum.**
Across the 11 processed nodes, `Y0345` at `dmax = 0.0116` has all four NO children as genuine
survivors (converged, η = 0) while `Y0637`, `Y0997` and `Y0709` at `dmax = 0.0127` have none and
close outright. 11 of 44 children are now genuine survivors, concentrated in three nodes
(`Y0345` 4, `Y1116` 4, `Y1099` 2, `Y0973` 1) — those nodes cannot be closed by this cover at s₀ at
any certifier budget, and `Y1116/NO1` is the first child with η **positive** (+0.1176).
