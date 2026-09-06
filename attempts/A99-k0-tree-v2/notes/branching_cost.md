# R2, part 1 — the exact D4 cost of branching the root on the corner shallow/deep pattern

LP-free, exact, and it fixes the ceiling on what R2 can be worth before any LP runs.

## The count

A85's root uses `d4_wlog` (Lemma K0-D4): the 1728 depth-2 cells of `T(s0) x [0,90)` collapse to
216 because the ROOT hypothesis is D4-symmetric. Branching on the per-corner SHALLOW(delta) /
DEEP(delta) dichotomy adds a hypothesis that is *not* D4-symmetric, so each branch may only be
quotiented by the STABILISER of its pattern.

Corners `{BL, BR, TR, TL}`, D4 acting as the symmetries of the square (`code/` computation,
reproduced by `python - <<` in `logs/branching.txt`):

| orbit representative | |orbit| | |stabiliser| | level-1 cells in that branch |
|---|---|---|---|
| (all deep) | 1 | 8 | 1728/8 = **216** |
| BL | 4 | 2 | 1728/2 = **864** |
| BL,BR (adjacent) | 4 | 2 | **864** |
| BL,TR (diagonal) | 2 | 4 | 1728/4 = **432** |
| BL,BR,TR | 4 | 2 | **864** |
| BL,BR,TR,TL | 1 | 8 | **216** — certified DEAD at the root (A89 `R1_4shallow_d0.3`) |

`1728/|stab| = 216 * |orbit|`, so the sum over orbit representatives is `216 * 16 = 3456`, and
after deleting the 4-shallow class (A89's window-valid root kill at delta = 0.3):

> **3240 level-1 cells instead of 216 — the branching costs exactly x15 in cells.**

## What that means for the price

* The **all-deep** branch keeps all 216 cells and gains **no exempt box at all** (Lemma ID only
  fires at a SHALLOW corner). Its subtree is A85's tree verbatim, so R2 cannot price the
  frontier below A85's 3 200-7 000 CPU-h no matter what the other branches do.
* R2 is therefore worth something only if the four surviving non-trivial patterns die
  ABOVE the depth-2 frontier — at the root (as 4-shallow does) or at level 1. If they die at
  level 1, the extra cost is 3 024 level-1 LP nodes (~0.47 CPU-h each = ~1 400 CPU-h) on top of
  A85's tree. If they do not, the whole tree runs 15 times.
* A89-O3 already measured the root: **3-shallow does NOT kill at the root** at delta = 0.3, 0.1
  or 0.05 (tau climbs 10.046 -> 10.209 under witness feedback; the kill is open and blocked on
  LP time, not geometry), and 2-shallow is strictly harder (`tau(2) >= tau(3) >= tau(4)`).
* So the only remaining hope is the level-1 kill, and that is what the LP screen of
  `notes/report99.md` measures.
