# A153 — the COVER NUMBER leaf: pricing a node by "how many pieces of diameter < 1 does the free centre region need?"

Owner: Opus engineer, 2026-09-08.  Read-only on every campaign and on every prior attempt; new files
only under `attempts/A153-cover-number/` plus the four named appends of T4.

## Where this comes from

A148 (`attempts/A148-gallery-v4/code/geo148.py`, `results/gallery148_*.json`,
`docs/shadows/{k0v4,a57v4}/`) computes, per node, a certified three-valued map of the
**feasible-centre region**

    F = { c : SOME tilt t gives a unit square Q(c,t) inside the container, interior-disjoint from
              every exact pin core and from K'(H) of every conditioned square }

on a grid of pitch ~0.02 x 36 tilts with a Lipschitz margin: GREEN = certified feasible, BLOCKED =
certified infeasible, UNDECIDED = the band between.  `F_outer = GREEN u UNDECIDED = ~BLOCKED` is a
certified OUTER approximation of F.  A148's own **disk bound** (area of `F_outer` dilated by 1/2,
over pi/4) does not bite: it gives 9-10 against budgets of 4-5.

The PI, looking at `k5_16_interior_Y1117` (green 0.993 + undecided 0.756 = 1.749 of area against 5
remaining squares), asked for a cheap way to price a pinwheel / same-tilt grain.

## The leaf (T1)

Any two interior-disjoint unit squares have centres at Euclidean distance >= 1 (each contains the
open disk of radius 1/2 about its centre; centres closer than 1 make those two open disks meet).
So the centres of the squares the node still has to place form a **1-separated subset of `F_outer`**.
If `F_outer` can be COVERED by k sets of diameter < 1, each piece holds at most one centre, hence

    (number of further unit squares the node can place)  <=  k .

`k < budget` (budget = the number of not-yet-conditioned squares) is a **KILL, LP-free**.

Pieces used: axis-aligned squares of side d with `2 d^2 < 1` (diameter `d sqrt2 < 1`) — the PI's
side-0.7 squares.  `F_outer` is a union of grid cells, so "the pieces cover `F_outer`" is a finite
rational check.

Conditional refinement (**Lemma TC**, the tilt-coherent branch): if all remaining squares share a
tilt t, interior-disjointness forces the centre difference to have L-infinity norm >= 1 **in the
frame rotated by t**, so the pieces may be squares of side < 1 in that frame — nearly twice the
side, so roughly a quarter of the pieces.  Sound only under the common-tilt hypothesis; labelled a
conditional leaf.

## Tasks

- **T1** the lemma exactly, its Lean shape, the certificate format, an independent checker.
- **T2** Y1117 first: minimum-cardinality cover of `F_outer` by side-0.7 squares (exact by branch
  and bound, and a heuristic with a matching lower bound — both reported) vs budget 5; then the
  same-tilt refinement over the H tilt window.
- **T3** the whole population: the 60 alive A57/A60 nodes A148 drew, the 11 k0 residue cells
  (budget 10), and every alive node in A57/A96 `PAUSED.md` v3 state.  Cover number vs budget, the
  distribution of (cover number - budget), kills with certificates + checker + sample line.
- **T4** fold-in lines: `attempts/A57-shadow-trees/PAUSED.md` addendum,
  `attempts/A60-trump5-campaign/notes/ledger.md`, one paragraph for `docs/residue_ledger.md`
  section 1 and `docs/budget.md` section D.

## Rules held

Read-only on every campaign and prior attempt; no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`;
<= 2 BelowNormal python processes and the box under 16 (A149/A150/A151/A152 run 2 each); no LP;
cap 3 CPU-h; git = fetch + plain merge + `git commit -- <pathspecs>` only.
