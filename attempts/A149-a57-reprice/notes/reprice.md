# A149 Task A — A57 re-priced in `docs/budget.md`'s own model

**Answer.** **≈ 1,800 CPU-h central, range 1,150–3,150, ≈ 15 wall-days at 5 workers**
(range 9.6–26). The standing row said ≈ 800 CPU-h / ≈ 7 wall-days.
Code `code/{frontier149.py, reprice149.py}`, output `results/{frontier149.json, reprice149.json}`.

The number is **2.3× the standing one, and the whole increase is one term the standing estimate
never had: the subtree.** The node itself got *cheaper*.

---

## 1. The model

A124's `schedule124.py` shape, made absolute. A124 could only scale a 13.3-wall-day baseline by
`E'/E` because it had no measured node cost; A137's night measured one, so the same recursion is
evaluated in CPU-seconds against a *counted* frontier:

```
E_L = (1 - g_L) * [ c + 8 * d_L * E_{L+1} ]     one EMITTED level-L child, screen not yet run
F_L =              c + 8 * d_L * E_{L+1}        a child already past the geometry screen
E_5 = 0                                          the tree terminates at level 4
```

* `g_L` — the child dies at the geometry screen (T5 / T5′ at the **exact** pin core / T5″ trim /
  T5‴ pin-clip / T5⁗ polygon): no LP, no certificate, ~0 s.
* `d_L` — a child that reaches the LP still owes a split afterwards (NO-KILL +
  LOST-KILL-ON-RESOLVE + TOO-TIGHT; a PASS is closed, a WALL-CAP is not a verdict).
* `c` — one LP + s0 exact certificate + FROZEN `verify_case.py`.

This is the same object as §B's per-level anatomy: §B's rows are `g` (KILL-BY-LOGIC), `1 − d`
(PASS + resolved FAIL) and `d` (ALIVE-at-LP → 8 children), and its "cost per node" is `c`.

## 2. Inputs — every one of them, and where it comes from

| input | value | source | status |
|---|---|---|---|
| `g_1` | **22.5 %** (62/276) | A137 `emit_geo_*.jsonl` + `emitq_*.json`, level-1 children **never previously recorded** | measured |
| `g_2` | **24.8 %** (464/1,869) | same, deepen lane | measured |
| `g_3` | **32.0 %** (82/256) | same | measured |
| `g_4` | **87.5 %** (7/8) | same | measured, n = 8 |
| `d_1` | **23.5 %** (20/85) | A137 `emit_lp_*.jsonl`, new ids only | measured |
| `c` | **283 s** | A137 lane (b): 189 level-1 nodes, 14.85 CPU-h | measured |
| `c` (legacy re-solve) | **342 s** | A137 lane (a): 163 exact-core re-solves, 15.5 CPU-h | measured |
| `D_2` = 8-child descent share of all emitted level-2 nodes | **0.113** | A96 `residue_map.md` line 25, via A124 | **NOT measured under the exact cores** |
| level-1 "ok" children, sides 2–4 | **4,683** | `lemmas.md` T23 (2), the per-side C-check | measured |
| the frontier | **2,052 nodes** | `frontier149.py`, id by id | counted |

### The assumptions, stated

1. **s0 only.** `c = 283 s` is an LP plus an exact certificate at `s0` under the frozen
   `verify_case.py`. It contains **no 4-D window verification** — §B's 545 s/node — because the
   window is covered by the four-side δ = 1e-2 grid (`lemmas.md` T23), not per node. The price
   below is therefore *of the grid*, and the 4-D skip list is upside outside it.
2. **Node cost is level-independent** (A124's assumption; §B measures level-2 LP at 1.11×).
3. **The tree terminates at level 4** (A124; §B: level-4 descent 0 of 30).
4. **`d_L` for L ≥ 2 comes from `D_2 = 0.113` via `d_L = D_2/(1 − g_L)`**, held constant below
   level 2. §B says the ALIVE share *falls* with depth (19 % → 10 %), so this is conservative in
   one direction and stale in another — see §5, it is the load-bearing unknown.
5. **Sides 2–4 are full re-runs at `F_1`**: their "ok" children are already past the C-check, and
   CENTRAL credits the exact-core hooks with nothing further there (LOW credits 22.5 %).
6. **Every worker is one core, five workers, 24 h/day** — the file's own convention.
7. Lean replay excluded (the PI's convention).

### The correction to the night's headline rates

PAUSED.md v3 quotes level-1 geometry at 27.4 % and "78.8 % of decided". Those are measured over
**849** level-1 children, of which **573 were re-screens of ids already in the corpus** — the
shard index changed between runs, so `emit137`'s `done` check (one shard file) did not see them
(§`notes/dupwork.md`). Split:

| population | n | dead by geometry | reached LP | decided | PASS |
|---|---|---|---|---|---|
| **never recorded before** | 276 | 62 = **22.5 %** | 214 | 85 | 65 = **76.5 %** |
| re-screened | 573 | 183 = 31.9 % (**152 were already logic kills**) | 390 | 104 | 84 = 80.8 % (**71 were already PASS**) |

The forward-looking rate — the one that prices 325 new cover children and 4,683 children of sides
2–4 — is the first row. It is **lower** than the published 27.4 %, so this correction moves the
price *up*, not down.

## 3. The frontier, counted id by id (side 1, tag G1)

`frontier149.py` gives every id exactly one entry point, because the obvious populations overlap:
129 of the 454 cover children missing from the shard files are sitting in the LP queue, and 286 of
the 415 queued level-1 jobs are re-solves of ids that already carry a verdict.

| class | n | by level | costs |
|---|---|---|---|
| **NEW** — in the cover, never screened | **325** | L1 325 | `E_1` |
| **QUEUED** — screened, LP not run, not dead | **1,432** | L1 214, L2 1,117, L3 101 | `F_L` |
| **ALIVE_D** — recorded ALIVE, 8 children already emitted | **157** | L1 133, L2 24 | the exact-core re-solve only (117 still owed) |
| **ALIVE_U** — recorded ALIVE, children not emitted | **44** | L1 44 | `8 · E_2` |
| **FAILN / FAILD** | **91 / 3** | L1 54, L2 40 | `F_L` / re-solve |
| DEAD (PASS, logic kill, or superseded incl. inherited) | 3,052 | — | 0 |

**Total owing: 2,052 nodes.** PAUSED v3's "406" is the pre-night ALIVE+FAIL count on a per-tree
view; the id-level count of still-open *recorded* nodes here is 295, and the other 1,757 are the
already-emitted queue and the unscreened cover — which is where the money is.

**Finding worth acting on: 563 of the 1,995 unsolved queued LP jobs (28 %) are already dead** —
their node or an ancestor is in the night's supersession ledgers (201 L1, 288 L2, 73 L3, 1 L4).
`mkqueue137.py` drops recorded and claimed ids but does not test ancestry against the fold-in
ledgers, so a worker started on `queue_bc.json` today spends better than a quarter of its wall on
nodes that are already certified dead. CENTRAL drops them; HIGH does not (the difference is
≈ 90 CPU-h).

## 4. The answer, and where it differs from the standing row

| scenario | CPU-h | wall-days at 5 | what changes |
|---|---|---|---|
| **CENTRAL** | **1,777** | **14.8** | the table of §2 as stated |
| LOW | 1,150 | 9.6 | `g_1` at the all-ids rate 28.9 %, `d_1` 20.7 %, `c` = 240 s, sides 2–4 credited with the 22.5 % screen |
| HIGH | 3,125 | 26.0 | `c` = 400 s (top of §B's LP band), `D_2` = 0.16 (§B's ALIVE share, not A96's), the 563 dead queue jobs not dropped |
| *control:* §B's pre-night anatomy on the same frontier | 5,761 | 48.0 | 29 % logic, ALIVE 26.8 % of LP'd, 850 s/node |
| *control:* no geometry screen at all | 1,798 | 15.0 | only 325 children are still unscreened, so this is **not** the hooks' campaign-wide value |

Split of CENTRAL: **side 1 (the live tree) 392 CPU-h**, **sides 2–4 of the grid 1,385 CPU-h**.
Within side 1: queue 244, new cover children 75, ALIVE-not-deepened 41, open FAILs 22, exact-core
re-solves 11.

**Why 1,800 and not 800.** The standing 768 CPU-h is `lemmas.md` T23's grid estimate: 6,418
level-1 "ok" children at 431 s each — **one LP per child and no descent**. Two corrections, in
opposite directions:

* the node got **cheaper**: 431 s assumed → **283 s** measured with exact cores (6,418 × 283 s =
  **504 CPU-h**, a 34 % cut on the same count);
* one "ok" child is not one node but **3.76** of them (`F_1/c` = 1,065 s / 283 s), because at the
  measured level-1 rates an emitted child spawns `8 × 0.235 = 1.88` children that themselves cost
  `E_2 = 415 s`.

504 × 3.5 ≈ 1,780. The whole re-price is the missing subtree term, partly offset by a faster node.

## 5. The one input nobody has measured, and it dominates

`D_2` — what fraction of an emitted level-2 child's LP outcomes still owes a split — has **no
measurement under the exact cores**: all 1,117 level-2 LP jobs in the queue are untouched. A96's
0.113 is from the old tree with the stock cores.

| `D_2` | children per emitted L2 node | CPU-h | wall-days at 5 |
|---|---|---|---|
| 0.05 | 0.40 | 1,386 | 11.6 |
| 0.08 | 0.64 | 1,565 | 13.0 |
| **0.113 (A96, used)** | **0.90** | **1,777** | **14.8** |
| 0.15 | 1.20 | 2,033 | 16.9 |
| 0.20 | 1.60 | 2,412 | 20.1 |
| 0.30 | 2.40 | 3,279 | 27.3 |

**So the cheapest thing anyone can do to this row is drain ~300 level-2 LP jobs.** At the measured
283 s that is **24 CPU-h — a fifth of a wall-day at 5 — and it collapses a factor-2.4 spread in a
1,800 CPU-h estimate.** Nothing else on the A57 list has that return. It is the resume block's
item 2 already; this is the reason to do it *first* and to report the level-2 `d` explicitly.

## 6. What is NOT in the number

* the 4-D window skip list (upside on the grid, `lemmas.md` T24/T25);
* the polygon-core v3 clause (A132/A135) and the guard-line clause (A144) — both need a verifier
  change, both are LP levers whose *rate* on an unselected population is still unmeasured;
* A141's slot-lane and A131's pin-clip backlogs, which are **already folded in** (they are why
  3,052 ids are DEAD);
* the exact-core lever's remaining yield: 117 targets left, all in the `frac_exact < 0.45` bands
  (23.8 % measured in 0.30–0.45, untested below 0.30) — ~11 CPU-h for an expected ~20 kills,
  each of which deletes up to 8 queued level-2 jobs. It is in the number as a cost but its
  *saving* is not credited, so CENTRAL is conservative by roughly the 20 × 8 × `E_2` ≈ 18 CPU-h
  it should return.
