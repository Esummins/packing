# A166 — the NEAREST-CORNER SUB-TREE per hard k0 node: keep H, force the nearest corner doubly met, and price the 3-box LP

Restated from the PI's brief of 2026-09-08 (Opus engineer), with the coordinator's two mid-attempt
additions folded into T4.

## Context

The interior-first k0_00 tree's hard cells are the **eleven converged-alive cells**
(`docs/shadows/k0v4/`, A140/A141/A159 records): `l1_071`, `l1_104`, `l1_124`, `l1_148`, `l1_153`,
`l1_158`, `l1_159`, `l2_p114_001`, `l2_p65_101`, `l2_p65_111`, `l2_p74_001`. Each conditions ONE
square `H` (a centre box × tilt window) and each is near one of Trump's three interior (tilted)
squares. `l1_153` is a Trump-image cell. A165 is running a hand-built cascade on `l1_104` in
parallel — **read-only on its files**.

A143/A150/A155 measured the corner-first ROOT:

* the corner band is the whole corner-meeting zone when `H` is unknown (A150: 206 of 216 cells,
  A155: 202 at pad 0), and the four-corner PRODUCT is priced out (≥ 4.6·10⁵ CPU-h);
* but conditioning on several corner squares as cores buys real LP slack — A150: four corners at
  budget 7, median `eta = -1.0`, 7 converged kills of 13, 4 verifier PASS; A143: two squares at
  ONE corner without `H` at budget 9, `eta ~ -0.08`, 0 kills.

**The PI's proposal — a SUB-TREE per hard node.** Keep `H` as given, take the corner NEAREST to
`H`, and condition on that corner's two meeters (K0-BLOCKED requires every corner doubly met, with
the widened box per K0-WIDEN; K0-FREE is dead by teleport), i.e. a **3-box node at budget 8**. The
pair cover of that corner is A150's (`attempts/A150-four-corner-product/code/{band150,prod150,
frames150}.py`, A155's `cells155.py` with the pad as a parameter) but now **CLIPPED against
`K'(H)`** (A131's clip with `H`'s exact core as the pin; A158's mutual-clip rule) and **pair-tested
with `H` present** (pair leaf: cores that meet ⇒ same square; A161's exact `box_misses_cell`).

**Prediction.** For a Trump-like `H` whose nearest corner is SIMPLE in Trump (Trump's images have
one non-simple corner, TL in trump5's frame; A143 §4 identified it), forcing that corner doubly met
contradicts the Trump-like packing and the LP dies at once; only the `H` adjacent to the non-simple
corner survives its sub-tree, and there the LP prices the worst component.

## Tasks

1. **Geometry, per cell.** Identify the nearest corner (metric: Euclidean distance from `H`'s box
   centre to the corner point). Build the pair cover of that corner at the window pad (A155's cells
   at `w = 0.0255`; also report `w = 0` for s0-only). Clip each pair cell against `K'(H)` and
   against each other; count survivors per stage (raw pairs, after clip, after pair leaf, after
   A161's chord/lane tests where applicable — k0 has no pins, so only the corner's own walls
   matter).
2. **The 3-box LP** (`H` + the two corner boxes, exact cores, `K'`-pruned pool, budget 8) on the
   surviving pair cells of each cell. Cap 240 s per node and 3 CPU-h total at 2 BLAS-pinned
   BelowNormal processes (affinity `0xFFFF`; box ceiling 16 — count and wait). If a cell has many
   survivors, sample 10 uniformly and report the slack distribution. Certify converged kills with
   the FROZEN `verify_case` (fixed side) and record `window transfer pending`.
3. **CANARY.** `l1_153` must SURVIVE in its nearest-corner sub-tree (if its nearest corner is the
   TL-adjacent one). If every pair cell of `l1_153`'s sub-tree dies, the construction is unsound:
   stop and report which step.
4. **The verdict per cell**: DEAD (all surviving pair cells killed) / ALIVE (some pair cell at
   budget), and the comparison with A143's one-corner numbers. Plus the coordinator's two
   additions: (a) which of Trump's three interior tilted squares each `H` corresponds to (nearest by
   pose in the D4-canonical frame; A22's exact Trump data) and whether `H`'s nearest corner is
   SIMPLE or NON-SIMPLE in Trump; (b) the QUADRANT CENSUS — the centres of each cell's dual-support
   placements per quadrant of the container (split at `s0/2`) beside Trump's own census. The price
   of running this sub-tree on all eleven and on the remaining open k0 cells, and what it would take
   to make the kills window-valid (`K0-WIDEN` pad already in the cover; the certificate at `s0`
   transfers by dilation as in `k0_route.md` §4.1 — state exactly).

Deliverables: notes, a figure per cell in A148's panel style with the three boxes drawn,
`results/subtree166.jsonl`, certificates, an independent checker for the geometric stages, one
paragraph for `docs/residue_ledger.md` §4.

## Rules

Read-only on every campaign and prior attempt (new files only under this attempt plus the doc line);
frozen verifiers untouched; honour every sentinel; never launch a shard; no recursive deletes;
`PYTHONDONTWRITEBYTECODE=1`; git = fetch + plain merge + `git commit -- <pathspecs>` only; registry
row and LOG entry. Report ONCE: the canary first, the per-cell verdict table second, the price
third, pointers last; no interim messages.
