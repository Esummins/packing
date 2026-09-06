# A96 block-first pilot (block96) — is the k5_11 mid-tilt hole Trump's pinwheel?

*Pilot chore under A96. Read-only on the A57/A96 campaign files; all writes under
`attempts/A96-a57-parametric/{code,results/block96,certs/block96,logs,notes}`. No commit.*

## What was tested

**PI hypothesis.** The mid-tilt certification holes of the k5_11 tree (docs/cert_failures.md
categories C, D and the wall-adjacent bulk of H) are Trump's **pinwheel**: a flush 2×2 same-tilt
block of four unit squares behaving as one rigid body with parameters `(cx, cy, theta)`. In
k5_11 five squares are pinned, four would form the block, two remain.

**The added hypothesis.** On top of an A57 level-1 node's own hypothesis (5 slack pin cores at
`pin_delta = 1e-2` + the conditioned interior square's box), block96 adds

> four squares of the packing form a flush 2×2 block whose rigid-body parameters lie in `B`

for `B` on a coarse grid of the block's `(centre, tilt)` space, and derives the four squares'
individual parameter boxes as the exact rigid-body image of `B`

```
square_i box = { (c + R(th) d_i , th) : (c, th) in B },   d_i = (±1/2, ±1/2)
```

outer-approximated by an axis-aligned centre box (exact interval trig on the radius-√2/2 arc)
carrying the **same** tilt interval — so the four block squares share the tilt bin, as a rigid
block must. Those boxes are pinned with the ordinary A57/A85 core machinery
(`caselp.Box.core`, the same object A85's pair machinery pins).

**Grid.** block centre step `g = 0.18`, tilt bins `5°` over `[0, 90)`, block centre restricted to
`[W, s0 − W]²` with `W = max(cos th + sin th)` over the bin (the region where a 2×2 block of unit
squares fits at side s0); `a_min = 0.30`. That yields **1,056 block boxes**, core half-sides
`a ∈ [0.321, 0.346]` (A57's own level-1 cover runs at `a_min = 0.34`).

**Two LP levels** (the 9-core one is node-independent, so it is run once and shared):

| level | cores | budget | meaning |
|---|---|---|---|
| BLOCK-ONLY | 5 pins + 4 block boxes | `11 − 9 = 2` | shared by all nodes |
| NODE+BLOCK | 5 pins + 4 block boxes + node box | `11 − 10 = 1` | only when the node box is parameter-disjoint from all four block boxes |

**Soundness** uses only A57's own two facts. *Distinctness*: two core boxes are realised by
different squares as soon as the parameter boxes are disjoint in `(x, y, theta)` — a square has
one `(centre, theta)` — so `budget = 11 − #cores` is legitimate exactly when the boxes are
pairwise disjoint (checked per box, never assumed) and no box realises a pin placement
(`pinguard.box_realizes_pin`). *Logic kill*: if two cores of **distinct** squares overlap
(`pinguard.cores_meet`) the hypothesis is contradictory and the case is empty with no LP — A57's
KILL-BY-LOGIC. Where the node box is **not** disjoint from a block box the conditioned square may
*be* a block square; that pair is marked SUBSUMED and only the (weaker, 9-core) block-only verdict
applies to it. Arbiter unchanged: A57 `certify.py` → `verify_case.py`,
sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`, byte-identical to the
frozen copy `attempts/A96-a57-parametric/code/verify_case.py`.

**One deviation from the frozen chain, and it is in the driver, not the chain.** A57
`certify.py`'s auto scale (`--scale 0`) computes `(budget − 0.005)/tau`, which raises
`ZeroDivisionError` when `tau = 0` — and a block-first node reaches `tau = 0` routinely (no
admissible placement survives 10 cores). block96 passes a fixed `--scale 1.03` in that case. The
scale only multiplies an empty weight vector; nothing in the verifier changes.

## Files

- `code/block96.py` — enumeration, both LP levels, the pinwheel-signature analysis.
- `code/block96_run.ps1` — detached driver (BLAS pinned, free-physical > 3 GB gate, resumable).
- `code/block96_report.py`, `code/block96_fixup.py`.
- `results/block96/blocks.json` — the 1,056 block boxes with status and the four image boxes.
- `results/block96/selection.json` — the 20 nodes; `node_order.json`, `pair_classes.json`.
- `results/block96/block96_blocklp.jsonl`, `block96_nodelp.jsonl` — one record per case.
- `results/block96/pinwheel.json` — step 3; `canary_Y0049.json` — the canary.
- `results/block96/block96_summary.json` — the aggregate (see the numbers there).
- `certs/block96/*` — the block-first certificates and verifier reports.

## Results (all numbers from `results/block96/block96_summary.json`)

### 1. Block-first pass / certify / wall

20 k5_11 level-1 G1 nodes (8 FAIL, 6 ε_geo-repaired PASS, 6 ALIVE-at-LP; includes the certfail
representatives Y0049 (D), Y0058 (H), Y0101 (C)). Each node sees the same **272 live block
boxes** (of 1,056; the other **784 = 74 %** are killed by logic against the pins before any node
is chosen).

Per node, of those 272:

| | range over the 20 nodes |
|---|---|
| free KILL-BY-LOGIC (node core meets a block core) | 208–267, mean 254 (**93 %**) |
| SUBSUMED (node box meets a block box — block-only level applies) | 0–8 |
| needing a NODE+BLOCK LP | 0–64, mean 14.2, total 284 |

**120 LPs were run** (16 of the 20 nodes are LP-complete; Y0009, Y0025, Y0033, Y0158 are partial —
the sweep was stopped at its wall):

- **79 DEAD-at-LP → 79 certified PASS** by the frozen verifier, 0 certificate failures.
- **41 ALIVE-at-LP.**
- τ is **integral in every single case**: `tau = 0` for all 79 kills, `tau ∈ {1, 2}` for all 41
  survivors. There is no fractional pinwheel at this level — the block-first LP degenerates into
  a pure "does an 11th square still fit" test, and the 24 `tau = 1` survivors are
  `docs/cert_failures.md` **category E (η = 0)** reappearing one level down.
- Wall per block box needing an LP: **mean 16.3 s, median 4.5 s, max 172.6 s**. A kill costs
  5.2 s end to end (LP ~4.4 s + verifier ~0.1 s, PASS with 0 atoms — every box exempt by a core);
  a survivor costs 38.5 s of LP and produces nothing.
- Block-only level (9 cores, budget 2): 8 boxes run, **all ALIVE** (`tau ∈ {2,3}`), 0 certified.
  There is no node-independent shortcut.

**Block-first residue: every one of the 20 nodes stays alive.** Alive block boxes per node:
5–61 overall, and 5–14 (mean 8.3) on the 16 LP-complete nodes. **Zero nodes closed.** The
survivors sit in the near-axis-aligned tilt bins B00 (0–5°) and B17 (85–90°) plus a thin
scattering at 40–60° and 75–85°; the genuinely mid-tilt bins B02–B14 contribute almost nothing,
because a mid-tilt 2×2 block simply does not fit beside the five k5_11 pins and the conditioned
square — those cases are all free logic kills.

### 2. Pinwheel signature on the same nodes' witnesses

14 of the 20 nodes carry witness files (the ALIVE-at-LP ones never reached certification, so they
have none). Criterion: mid-tilt (15–45°) witness placements in groups of ≥ 3 with tilts within 3°
and centres within 1.5.

- **Raw: 13/14 = 93 % "block-shaped".** This is an artefact. `verify_case.py` emits one witness
  per refined sub-box, so a single placement recurs 8–32 times (e.g. Y0049: 40 witness rows,
  **5 distinct placements**).
- **After de-duplicating to distinct placements (0.05 in centre, 0.25° in tilt): 2/14 = 14 %.**
  Distinct mid-tilt placements per node: 0–6, median 1.5. The two surviving groups (Y0059, Y0060)
  are same-tilt **pairs** about 0.97 apart — a plausible flush *pair*, never a triple or a
  quadruple. No node's mid-tilt witness set is a 2×2 block.

### 3. Price

- Measured block-first cost per level-1 node (16 LP-complete nodes): **97.8 s**; modelled over
  all 20 at 14.2 LPs × 16.3 s: **231 s**.
- Whole k5_11 level 1 (594 nodes): **16–38 h, i.e. 0.7–1.6 desktop-days at one process.**
- A57's own measured k5_11 interior level 1: 594 nodes, **95.9 h**, 581 s/node (832 s per
  non-logic node); A96's measured comparators are 399.5 s/node fixed-side and 264.6 s/node
  parametric.

So block-first is **cheap (+12 % to +40 % on A57's per-node cost) and worth nothing**: it closes
0 of 20 nodes, so its whole cost is additive on top of the existing route. Nothing in the A96
projection changes.

**The NON-BLOCK branch is NOT covered by this pilot.** Every statement above is conditioned on
"a flush 2×2 block exists at `B`". Packings with no flush 2×2 block are untouched — block-first
is at best one branch of a two-branch case split whose other branch has neither pilot nor lemma.

### 4. Canaries

- **Trump image**: 0 of the 1,056 block boxes is Trump-realizable (`substrat.trump_realizes` is
  False on every hypothesis), so **no block box was refused as image-realisable**, as required —
  k5_11 carries no image.
- **Y0049's "pinwheel"**: after de-duplication Y0049 has exactly **one** distinct mid-tilt witness
  placement, `(2.6394, 1.4265, 34.50°)` — a single square, not a pinwheel, so there is no block
  fragment to protect. Exactly **one** block box in the whole grid can contain that placement
  (`B06_03_01`, as its 4th square, centre ≈ (2.628, 1.474)); the other three corner assignments
  put the block centre outside the region where a 2×2 block fits at s0. That box is refused
  **before any certificate**, by logic: its 2nd square (centre ≈ (1.249, 1.780), tilt 30–35°) has
  a core overlapping the pin core at slot (0.5, 1.5), and its 1st square (≈ (2.091, 2.316))
  overlaps Y0049's own conditioned-square core. Both are exhibited geometric overlaps, not
  certifier holes — the certifier was never invoked on that box. Detail in
  `results/block96/canary_Y0049.json`.
