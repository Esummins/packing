# A197 -- the FORCED-SLOT PAIR PASS at nsub 8 / refine 4

*Opened 2026-09-10.  Successor of A178's per-cell pass (`attempts/A178-gallery-geometry`), which is
imported READ-ONLY.*

## The PI's reading (2026-09-10 10:45)

> "`k5_16_interior_Y0054` is trivially dead: BL(1,0) can't be doubly met in any way.  That's true of
> most of this class: the H box is in front of a slot, so the two slot simple units can't be doubly
> met."

## What is being claimed, precisely

`docs/proofs/forced_corners.md` Theorem FC makes every **usable** cell of `k5_16` / `k5_11` /
`trump5` a FORCED cell: its extension class is FULL on the closed window `[191/50, s0]`, so at the
widened open slot box

    B_p+ = (i, i+1+pi_i) x (j, j+1+pi_j)   in the corner frame,   pi_i = (lam_max - 1)(i + 1 + 1/sqrt2)

**two DISTINCT NON-pin squares** of the page's dilate F have interiors meeting `B_p+`.  The non-pin
squares of a page are the conditioned square(s) H and the free squares (Corollary FC-count).  So at
every forced cell exactly one of

* **(H-meets)** H is one meeter and one FREE square B is the other, or
* **(two-free)** two distinct FREE squares B, B' are the meeters (H is not a meeter),

holds.  Lemma A1 (`docs/proofs/sideband.md` §2) puts the two meeters' centres at l-infinity distance
>= 1/sqrt2 = 0.7071, so on a grid of cell side **0.70 < 1/sqrt2** the two centres never share a
cell.  A page is **DEAD** as soon as ONE forced slot admits no pair at all.

The PI's geometric point is that when H's centre box sits *in front of* a slot, the slot's own
neighbourhood has room for H **or** for a second free square but not for the pair -- which is a
statement the multibox library can settle by clipping, not an LP.

## What A178 did and where it fell short

A178 `code/geo178b.py::slot_pair_test` is the same test.  Its 34-page pass
(`attempts/A178-gallery-geometry/results/geopass178.jsonl`) declared every page ALIVE.  Three
defects, all reproduced on Y0054:

1. **Resolution.**  It ran at `nsub 4 / refine 2`, where slivers of ~1e-5 survive.  The coordinator's
   addendum `attempts/A178-gallery-geometry/results/addenda/pair_BL02_two_free_dead.md` killed
   A178's `c0_Y1033 / BL(0,2) / two-free:1+2` node at `nsub 8 / refine 4` in 5 s.
2. **The H-meets branch is far too weak.**  Y0054's `BL(1,0)` record is *not* empty: `two-free`
   already dies (`n_alive_pairs = 0` of 1 pair) and the slot survives ONLY because the `H-meets`
   sub-case survives.  A178's `H-meets` node is `{pins, H restricted to the meeter window, ONE free
   B in hull(B)}` -- a single node, with **no Lemma A1 cell split between the two meeters**.  That
   is exactly the pair the PI says cannot exist, and A178 never asked it to be a *pair*.
3. **Caps that declare ALIVE.**  `max_cells = 6` ("hull too wide: ALIVE untested") and
   `max_pairs = 40` ("pair budget exhausted: treated as ALIVE") fired on 3 of Y0054's 6 slots
   (`BR(0,1)`, `TR(1,0)`, `TL(1,0)`: 8 cells / 28 pairs each, all untested).

## What A197 does

`code/pair197.py`, a rewritten `slot_pair_test` (A178's modules imported read-only):

* `nsub 8 / refine 4` throughout.
* **H-meets is a PAIR test now**: a common grid of side 0.70 over the cell's meeter window, and a
  node per ORDERED pair `(cell_H, cell_B)` with `cell_H != cell_B` (H and B are distinguishable
  roles, so both orders are separate cases).  A cell pair is skipped only when a role's box misses
  the cell outright.  Alive branches are re-tested with A161's exact miss test (`h_misses`): an H
  hull that provably misses `B_p+` makes the branch vacuous.
* **two-free** over UNORDERED distinct cell pairs of the same grid (Lemma A1 excludes same-cell
  pairs), `max_cells 24`, `max_pairs 400`.
* H carries its own record box with the library's A135 exact core; the pins are obstacles.
* Forced CORNERS additionally get A169 Theorem B's lonely clip (`corners=`), which A178 used only in
  its corner-split branch.
* Per-page wall 900 s, enforced twice: an internal deadline so the row is always written, and the
  launcher killing the process TREE.
* Slots are ordered by their one-free hull area (the most squeezed slot first), so the wall is spent
  where a kill is likely.

Result file `results/slotpair197.jsonl` (one row per page, resumable), certificate
`certs/sp197_<nid>.json` for every DEAD page carrying the library's clip traces and `EmptyBox`
reasons `[C: library geometry; the frozen verifier is NOT involved]`.

## Scope

Every ALIVE `a57v4` page (`docs/shadows/STATUS.md`, 45 alive) EXCEPT `k5_16_interior_Y0491`
(A196/Fable owns it with a fuller pipeline).  `k0v4` is out of scope (its forced corners are
conditional on K0-O1).

## Deliverables

`results/slotpair197.jsonl`; a `(7h)` status-collector block in `docs/shadows/status_gallery.py`
in the style of `(7b)`/`(7c)`, and STATUS.md rerun; one gallery page
`docs/residue_map/slotpair197.svg` (one panel per killed page); `docs/residue_ledger.md` §4
paragraph; `docs/budget.md` §D item; `attempts/REGISTRY.md` row; `LOG.md` entry.

## Rules of the run

<= 2 python processes, BelowNormal, affinity 0xFFFF; lab ceiling 12 excluding "Claude Extensions"
command lines; per-page wall 900 s killing the process tree; read-only on every other attempt; no
recursive deletes; `PYTHONDONTWRITEBYTECODE=1`.
