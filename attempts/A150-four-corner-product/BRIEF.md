# A150 — the FOUR-CORNER PRODUCT root for k0_00: condition one corner intruder at every corner at once, kill combinations by geometry, and measure whether four cores finally buy LP slack (Opus, ≤ 2 CPU-h of LP)

Restated from the PI's brief of 2026-09-08.

## Context

A143 (`attempts/A143-corner-first-k0/`, `notes/composition.md`, `results/pairs143_geom.jsonl`,
`figs/cover143_pairs.svg`) built the **corner-first k0 root**: a k0 packing is either K0-FREE (some
corner box met by ≤ 1 square — dead by teleport / a Trump image) or **K0-BLOCKED**, every corner box
met by ≥ 2 squares. A143 conditioned at ONE corner (BL). Its findings:

* the level-1 cover of the BL corner-meeting zone is 216 cells = 6 × 6 positions on
  `[0.5, 1.7326162]²` × 6 tilt windows of 15°, over the FULL tilt range `[0°, 90°)` — the k0 root has
  **no simple-square tolerance** (`OccupiesSlot` is exact, so `skeleton = ∅` removes a measure-zero
  set of poses only);
* the doubly-met **pair** geometry at ONE corner kills **81.9 %** of the 11 772 canonical pair cells
  (P2 centre distance, P1 K′-vs-K′, P1s per-sub-bin) for 90 CPU-s;
* but the LP with two conditioned squares at the SAME corner **gains no slack**: η = −0.083, −0.077
  at budget 9, against −0.044 / −0.633 / −0.000 at budget 10 with one — the pair root prices at
  8 000–18 800 CPU-h, no better than the interior tree's 12 000.

**The PI's proposal: condition on ALL FOUR corners at once.** The admissible band for a corner
intruder is narrow — far enough from the corner that a second meeter fits beside it (A143's surviving
pair cells give the admissible first-meeter cells per corner), and close enough that the other ten
squares fit in the L-shaped remainder (A148's certified DISK BOUND,
`attempts/A148-gallery-v4/code/geo148.py`: every unit square contains the disk of radius 1/2 about
its centre, so the free region after removing the cores, dilated by 1/2, caps the number of squares
that fit). Then branch as a PRODUCT: one band cell per corner (D4 reduces the product by 8), and
kill combinations by geometry alone.

## Tasks

1. **The per-corner band.** From A143's data: the set of first-meeter cells with a surviving partner
   cell, then trimmed by the disk/L-shape room condition (state the exact condition; certify by
   sampling drawn → tested → hits). Report the band's cell count and its width in centre distance
   and tilt.
2. **The product cover.** Enumerate the D4-reduced 4-tuples; apply the geometric kills in increasing
   cost order — pairwise interior-disjointness of adjacent corner intruders (exact core-vs-core with
   A132 polygon cores / A135 exactcore), guard lines along each wall (A144 `guardline.py`: the two
   corner intruders on a wall already contribute two chords), the disk bound with four cores removed
   and seven squares to place, and the K′ lane count at each corner with M counting the conditioned
   squares. Report survivor count at each stage and the final survivors (draw the survivors' four
   cores in A148 panel-G style, ≤ 20 pages).
3. **The LP with four conditioned squares**, budget 7 = 11 − 4, exact cores, K′-pruned pool, 240 s
   each, on up to 10 surviving tuples (2 BLAS-pinned BelowNormal processes, cap 2 CPU-h total, honour
   every sentinel, never launch a shard): report τ / η / converged and whether four corners finally
   buy slack, vs A143's one-corner numbers.
4. **`notes/composition.md`**: the root lemma (K0-FREE or all four corners met, the D4 reduction of
   the product, the tilt range being the full `[0°, 90°)` since the k0 root has no simple-square
   tolerance per A143), and the projected cost of the product tree from the survivor count and the LP
   slack, against the interior tree's 12 000 CPU-h in `docs/budget.md`.

## Rules

Pure geometry except (3); read-only on every campaign and prior attempt (new files only under
`attempts/A150-four-corner-product/`); frozen verifiers untouched; no recursive deletes;
`PYTHONDONTWRITEBYTECODE=1`; ≤ 16 python processes on the box (A149 runs 2); git = fetch + plain
merge + `git commit -- <pathspecs>` only. Report ONCE: survivor counts per stage first, the LP slack
table second, the composition and price third, pointers last; no interim messages.
