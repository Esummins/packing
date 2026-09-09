# A165 — the CASCADE case tree on the k0 cell `l1_104` (and the `l1_153` canary)

**Opus engineer, 2026-09-08.  Working directory `attempts/A165-cascade-l1_104/`.**

## The PI's reading (the seed, restated)

`l1_104` is one of the eleven converged-alive `k0_00` cells (`docs/shadows/k0v4/`).  Its single
conditioned square `H` has box `x ∈ [2.4626, 2.5674]`, `y ∈ [2.1482, 2.2530]`, tilt `[30°, 45°]`
(A115 record `l1_104_plain_warm.t4.lp.json`, A140/A141 corpus).  Its LP is exactly at the budget:
`tau = 10.000000` against `budget = 10 = 11 − 1`, converged, `minmass 1.000` — i.e. the plain
one-box LP has **zero** slack.  A141's corner pass records `LANE_K′ ≥ 2` and `M = 0` at all four
widened corners.

The PI reads the page as a **CASCADE of forced boxes**:

* **(a)** `K0-BLOCKED` (`docs/proofs/k0_route.md` §3–§4) requires the TR corner box to be met by
  **two** squares — else `K0-FREE` teleports the packing into `k1_00`'s tree and the cell is dead.
  With `M(TR) = 0` both meeters are FREE squares.  The PI's claim: the only way to seat two
  interior-disjoint meeters is a **deep** meeter `D` up-right of `H` and a **shallow** meeter `S`
  up-left of `H` poking into `TR(0,0)` along the top wall.
* **(b)** That puts two centres in the top strip, so by the **top-wall chord row** (A144's
  guard-line lemma LINE-1/LINE-2: the chords of an interior-disjoint family on an axis-parallel
  line sum to `≤ s0 = 3.877084`; `D` and `S` each carry `≥ 1`) **at most ONE more** square crosses
  the top strip, and it must be at the left end, poking into `TL(0,0)` with a minimum intrusion
  depth.
* **(c)** `TL` doubly met then forces a **second** `TL` meeter along the bottom of `TL(0,0)` / the
  left wall, which with the left-wall chord row (bottom-left band holds one square) limits the
  upper-left meeters.
* **(d)** Six squares end up in narrow forced boxes with large certified wastage, and the
  remaining five cannot fit.

## What A165 builds

An explicit **CASE TREE**.  Each node is a set of named boxes (roles `H`, `D`, `S`, `TL-deep`,
`TL-second`, `BL-band`, …); each branching or forcing step is justified by an **existing leaf with
a certificate**:

| step | leaf | code |
|---|---|---|
| `K0-FREE`/teleport dichotomy, widened boxes | `k0_route.md` §3 (`teleport_packing`), §4.1 Lemma K0-WIDEN | — |
| corner lane cover / `M` | A141's polycore lane leaf | `attempts/A141-polycore-lane/code/polylane.py` |
| exact `box_misses_cell` | A161's full SAT over a parameter box | `attempts/A161-chord-lane/code/chordlane.py` |
| chord row on a wall line | A144's guard row (LINE-1/LINE-2) | `attempts/A144-guard-lines/code/guardline.py` |
| pair leaf (two boxes whose `K′` meet ⇒ same square) | A141 §5 `polycore_pair` | `polylane.pair_incompatible` |
| the multi-box case-LP at reduced budget | A150's k0 case-LP, exact cores, budget `11 − #boxes` | `attempts/A150-four-corner-product/code/lp150.py` |
| uncoverable area (if it lands) | A164 | `attempts/A164-wastage-area/code/geo164.py` |

At every leaf of the tree: **first geometry** (does the forced box set contradict itself — pair
leaf, lane, chord row, uncoverable area), **then** the multi-box LP at the reduced budget (240 s;
900 s at a knife edge; the FROZEN `verify_case.py` certifies fixed-side; `certificate pending`
recorded when the LP kills but the certificate does not land, for later window transfer).

The tree is recorded in full: every case, its boxes, how it was forced (which leaf, which
certificate), its verdict, and the total.

## CANARY (runs FIRST)

The same cascade construction is run on **`l1_153`**, the Trump-image cell (`H` box
`x ∈ [2.5674, 2.6723]`, `y ∈ [2.3578, 2.4626]`, tilt `[45°, 60°]`).  Trump's `TL` corner is its
doubly-met one; the others are singly met on the plain unit cell but doubly met with the
`K0-WIDEN` pad.  `l1_153` **MUST survive**: a real 11-family reaches it.  If the cascade kills it,
stop and report the step that is unsound.

## Deliverables

* `notes/cascade.md` — the tree as a figure in A148's style, one panel per case.
* `results/cascade165.jsonl` — one line per case.
* certificates under `certs/`.
* `code/check165.py` — an **independent** checker for the geometric steps, plus sample lines.
* one paragraph for `docs/residue_ledger.md` §4, and — if `l1_104` dies — the `docs/budget.md` k0
  row clause.

## Rules honoured

≤ 2 BLAS-pinned processes at BelowNormal with affinity `0xFFFF`; box ceiling 16 lab processes
(counted before every launch, wait if at the ceiling); cap **4 CPU-h**; every sentinel honoured
(`PAUSE`/`STOP` at the repo root and in this attempt); **never launch a shard**; READ-ONLY on every
campaign and every prior attempt (new files only under `attempts/A165-cascade-l1_104/**` plus the
named doc lines); the frozen verifiers untouched; no recursive deletes;
`PYTHONDONTWRITEBYTECODE=1`; git = fetch + plain merge + `git commit -- <pathspecs>` only; a
registry row and a `LOG.md` entry at the end.
