# The zero-cost T5″ kills sitting in the ALIVE queue (coordinator's check, confirmed)

## 1. Does `recheck96 --trimmed` spend LP time on a node whose bin T5″ empties? No.

`recheck96.py:91-97` (and this attempt's `recheck124.py`, same shape) calls
`trim57.trim_box` **before** `solve_node`, and on `not subs` writes a `TRIM-KILL` row with
`wall_s = 0.0` and `continue`s. Verified live as well as by reading: `k5_11_interior_Y0619` was
recorded today at `wall_s 0.0`. So no LP time was ever at risk.

**But they were queued behind the LP work.** The queue is walked in order, so 54 free kills sat
behind ~13 CPU-h of 900–1500 s solves. `code/trimsweep124.py` banks them directly.

## 2. The count, against the deployed rule

`trim57.trim_box` (deployed, `TRIM = True`) over the 414 currently-ALIVE rows: **57 empty**, and
the split reproduces the coordinator's reading of `trim96.json` exactly —

| class | L1 | L2 | L3 | total |
|---|---|---|---|---|
| `k5_11_G1` | 13 | 18 | 3 | 34 |
| `k5_16_G1` | 21 | 2 | — | 23 |
| **total** | **34** | **20** | **3** | **57** |

Two independent implementations agreeing on all 57 (`trim57.trim_box`, the deployed rule at
emission, and `trim96.surviving`, the offline scan at nsub = 256) is a second positive control on
top of the 741/741 of `control124`.

**54 of the 57 were still in the queue** (3 had already been consumed by the day's re-check).
All 54 are now recorded, at a total cost of **0.0 s of LP**: L1 31, L2 20, L3 3.

## 3. The auditability gap, fixed for these rows

PAUSED.md v2 §6's MUST-FIX is that `trim_excluded` / `trim_from` never reach disk. The sweep
writes, for every row, `excluded_intervals` (the actual `[lo, hi]` tilt intervals, not just a
count) and `original_bin`, so the coverage claim *original bin = surviving pieces ∪ excluded
intervals* is checkable from the results file. Every one of the 54 has exactly one excluded
interval equal to the whole original bin, which is what "empty surviving bin" means. The three
TRIM-KILLs recorded earlier today by the re-check workers carry only `excluded` (the count); they
are reconstructible because cover construction is deterministic, but the sweep's shape is the one
to adopt when the MUST-FIX is applied to `tree57.build_children`.

## 4. Do the `Y0036` L4 children inherit the empty bin? Yes — and it is a theorem, not a coincidence

The three L3 nodes `k5_11_interior_Y0036_D07_D00 / _D04 / _D05` are trim-empty (bins
[86.1859, 88.0930], [86.1859, 88.0930], [88.0930, 90] respectively, each fully excluded).

**Monotonicity.** T5″ excludes a tilt sub-interval when the *whole centre box* lies inside one
pin's octagon for every theta in it. A child's centre box is a sub-box of its parent's and its
tilt bin is a sub-interval of the parent's, so the same pin's octagon still contains it at every
tilt: **emptiness is inherited by every descendant, at every depth.** The test is over the box's
four corners against the worst case on the interval, and both shrink.

Checked rather than assumed: all **24** L4 children of those three parents are present in
`tree_k5_11_interior_G1_D2_D2_D2.jsonl`, and `trim57.trim_box` returns an empty surviving bin for
**24 of 24**.

**The useful consequence.** Those 24 nodes were emitted and solved *before* T5″ existed, and
their recorded verdicts are **14 KILL-BY-LOGIC, 4 PASS, 6 FAIL** — including the coordinator's
three: `Y0036_D07_D04_D06` FAIL, `Y0036_D07_D05_D02` PASS, `Y0036_D07_D05_D03` FAIL. The whole
subtree is dead at its L3 root, so:

* the **6 FAIL rows need no resolver work at all** — they are queued against nodes that carry no
  configuration;
* the 4 PASS certificates are sound but redundant;
* on a resume, the descent below these three L3 nodes should not be re-generated.

This is the first concrete instance of the more general point: **T5″ should be applied to the
existing open population, not only at emission.**

## 5. So we scanned the whole population — and the resolver queue is 28.5 % dead

`trim57.trim_box` over all 2,418 corpus rows, by recorded verdict (seconds of geometry, no LP):

| recorded verdict | rows | trim-empty | share |
|---|---|---|---|
| PASS | 1137 | 47 | 4.1 % |
| KILL-BY-LOGIC | 674 | 674 | **100 %** |
| ALIVE | 414 | 57 | 13.8 % |
| **FAIL → resolver** | **193** | **55** | **28.5 %** |
| work-owing (ALIVE + FAIL) | **607** | **112** | **18.5 %** |

Two readings.

**The positive control gets stronger again:** all 674 stored KILL-BY-LOGIC rows come out empty,
100 %, alongside `control124`'s 741/741 on the recomputed T5′ and the 57/57 agreement between
`trim57` and `trim96` above. Nothing in the trimming rule has ever disagreed with the existing
kills, on any population, in any implementation.

**Almost a fifth of the remaining work is already dead.** 112 of the 607 work-owing nodes carry
no configuration at all, and the FAIL queue is the worst of it — **55 of 193 resolver items,
28.5 %, are nodes T5″ empties outright**, and the resolver is the expensive tail (LOG.md: FAIL
p50 375 s, max 3,385 s; ε_geo retries run to minutes). A124 has recorded the 54 ALIVE ones it
owns; the 55 FAIL rows sit in A57's results and this attempt is read-only there, so they are a
**recommendation, not a change**: run the same three-line scan over
`tree_*.jsonl` before the resolver is restarted, and retire them.

That, and not the level-1 emission rate, is the actionable T5″ finding of the day: applied
retroactively to the population that already exists, trimming retires ~18 % of the outstanding
node count for the cost of a geometry scan — where applied prospectively at emission it buys the
21 % schedule cut of section T2, which is a different and additive saving.
