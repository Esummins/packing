# A166 — THE CANARY: `l1_153` survives, and the step that would have made the construction unsound

`code/canary166.py`, `results/canary166_wmax.json`. Verdict: **CANARY_PASS = True**, and it passes for
a reason that changes the construction.

## 1. `l1_153` is a Trump image, exactly, and A166 pins which one

A140 records `l1_153` as "A38 l1 idx 153 (Trump image)". A166 sharpens that to an exact identification
(`code/trump166.py`, `results/trump166.json`): of the eight D4 images of Trump dilated to `s0`
(`λ = s0/ŝ = 1.0000001057`), **exactly one — `g4` — has a square whose pose lies inside `l1_153`'s
conditioned box `B_H = [2.5674485, 2.67226625] x [2.357813, 2.46263075] x [45°, 60°)`**, namely
`sq9`, one of Trump's THREE interior tilted squares, at `(2.6238, 2.4365, 49.818°)`. The pose distance
is `0.000000` in all three components. So `Δ_λ ẑ` (in the `g4` labelling) satisfies `l1_153`'s
hypothesis and A166 must not kill it.

## 2. What `g4` does at `TR`, exactly

A166's own from-scratch SAT (`check166.sat_depth`, no library) on the widened box
`B_TR^w = [s0 − a_w, s0]^2`, `a_w = 1.0255100742`:

| meeter | pose (global) | penetration of `int B_TR^w` | cover cell (`TR` frame) | A166 verdict of that cell |
|---|---|---|---|---|
| `sq5` | `(3.377084, 3.377084, 0°)` — the axis-aligned corner slot square | `1.000000` | `(0, 0, 0)` | **ALIVE** |
| `sq9` | `(2.623834, 2.436509, 49.818°)` — the interior tilted square, `= H` | `0.035949` | `(3, 4, 3)` | **DEGENERATE_H2** |

`sq9`'s penetration `3.59e-2` at `a_w` against A159's `3.32e-4`-scale figures reflects only that A159
measured its own witness pose rather than the exact image; the sign is the same and both are positive,
so both agree that **`H` itself is a widened `TR` meeter**.

At the **UNWIDENED** box the same computation gives

    sq5:  +0.999999947        sq9 (= H):  **-0.000000202**

so at the exact unit corner box `g4`'s `TR` is met by `sq5` ALONE, by a margin of `2.02e-7` — `H`
grazes it from outside. Three things follow, and they matter for how the two pads are read:

* A143 §4's count (`g0`: `BL 1, BR 1, TR 1, TL 2` at `w = 0`) is reproduced here in the `g4` labelling —
  the exact-box doubly-met corner of `g4` is `BR`, and `TR` is singly met;
* so at pad 0 the K0-BLOCKED hypothesis is simply FALSE of `g4` at `TR`, and Lemma K0-FREE applies:
  the pad-0 branch is vacuous for Trump rather than realised, which is why a pad-0 kill is an s0-only
  statement (A159 §5's point, from the other side);
* the `2.02e-7` graze is the same razor A159 measured as "16 of 44 corners with the joint optimum
  exactly tangent, `|J| < 10^-9`". The canary is therefore run at the WINDOW pad, where the hypothesis
  is genuinely realised — which is also the only pad the tree may use.

## 3. The step that would have been unsound

The brief's sub-tree is "a 3-box node at budget 8: `H` + the corner's two meeters". Enumerated
literally, the pair cover of `l1_153` is **EMPTY**: of the 216 cover cells 193 are DEAD, 3 DEGENERATE
and 20 ALIVE, and every one of the 210 unordered pairs of the 20 ALIVE cells was already killed by
A143's own pair chain (all 20 lie in the corner-hugging block `ix, iy <= 2`, so any two of them are
within centre distance 1 of each other). A tool that reported "all pair cells dead ⇒ `l1_153` DEAD"
would have certified a kill of a cell that a genuine 11-square family realises.

**The step is stage `H2` applied to cell `(3, 4, 3)`.** `maxdist(R_H, R_{(3,4,3)}) < 1`, so every
square with a pose in `(3,4,3)` overlaps every square with a pose in `B_H`. That inference is
CORRECT — what it proves is not "no meeter there" but "any meeter there IS `H`". Because
`(3,4,3) ∩ B_H != ∅` as parameter boxes, the cell is `DEGENERATE`, not `DEAD`, and the node keeps the
**budget-9 branch** in which `H` is one of the two `TR` meeters and the partner is a second square in
an `ALIVE` cell. `g4` lands in exactly that branch: `sq9 = H`, partner `sq5` in cell `(0,0,0)`,
verdict `ALIVE`.

So the canary passes, and the price of passing it is the second branch. Recorded as a rule:

> **K0-BLOCKED says the corner box is met by two DISTINCT squares. It does NOT say that either of
> them is different from the node's conditioned square. Any corner-crowd sub-tree hung under an
> interior node owes the degenerate branch, at budget `11 − 2`, wherever the conditioned box can
> reach the corner box.**

## 4. The same test on all eight images and both pads

`results/canary166_wmax.json` runs the check for every image. Only `g4` realises `l1_153`
(`squares_in_BH = [9]`); the other seven have no square in `B_H` and so impose no obligation on this
node — but their `TR` pairs are reported anyway, and they are instructive: `g0`, `g2`, `g3`, `g6`, `g7`
all have the corner slot square in cell `(0,0,0)` (ALIVE) with the second meeter in a cell that
`l1_153`'s `H` kills, while `g1` and `g5` have BOTH meeters in cells `l1_153`'s `H` kills. That is the
correct behaviour: those images do not satisfy the node's hypothesis, so nothing about them has to
survive it.

## 5. Margins, so the verdict does not rest on float noise

The identification `X ∩ B_H = ∅` is what separates `DEAD` from `DEGENERATE`, so it must not be a
rounding artefact. Measured over all 106–191 `DEAD_H2`/`DEAD_H1`/`DEAD_CLIP` cells of each of the
eleven, the minimum box separation from `B_H` (max over the three axes, degrees for tilt) is

    l1_071 0.0910  l1_104 0.0969  l1_124 0.1127  l1_148 0.0121  l1_153 0.0079
    l1_158 0.0121  l1_159 0.0121  l2_p114_001 0.0079  l2_p65_101 0.2483
    l2_p65_111 0.1958  l2_p74_001 0.1451

i.e. at worst `7.9e-3`, six orders of magnitude above double precision, and the `DEGENERATE` cells are
those with an actual overlap, not a near-miss.
