# T1 — the impossible dual-support weight over the 448 surviving A57 nodes

A145, 2026-09-07. Driver `code/measure145.py`, ledger `results/impossible_weight.jsonl` (448 rows,
one per node, 0 errors, 0 nodes without a stored LP record), controls `code/check145.py` →
`results/check145.json`. Read-only on every campaign and on A132/A135/A142.

## What is measured, and which half of it is a proof

A dual-support column is a placement the node's LP is charging weight `y` to. It is **impossible
under the node's own hypothesis** if the unit square it draws overlaps one of the six hypothesis
squares (five pins + the conditioned box H) at *every* pose of that square's box: two unit squares
of one packing cannot overlap, so no packing satisfying the hypothesis contains that placement and
the weight the LP puts on it is weight it should never have had.

Two tests, and they are one-sided in **opposite** directions — this is the thing to keep straight:

| test | what it is | direction of its error |
|---|---|---|
| **GRID** (the PI's reading; A142 `gap_over_box`, `NPOSE = 7`) | the SAT gap is negative at all 7³ = 343 sampled poses of the box | **necessary-ish, not sufficient**: 343 poses are not all poses, so a flagged column is *not proved* impossible |
| **EXACT** | the column meets `K'(B)` = ⋂ over all poses of `Q(c,θ)` — A132's certified polygon core, and for a PIN box A135's exact axis square of half-side `a_pin = 33873816211/68719476736 = 0.49292890196375083`, which for zero tilt width IS that whole intersection | **sufficient, not necessary**: meeting `K'` proves overlap at every pose, but a column can overlap at every pose without meeting the intersection of the poses |

So EXACT ⊆ GRID always (met `K'` ⟹ negative gap at every sampled pose), and EXACT is the one that
is a proof. EXACT is also **exactly the set of rows A135's `poly` arm prunes**, which is why
`w_imposs_exact / w_total` is a *prediction* about the re-solve of T2 and not just a description.

`w_total` is the sum of the dual weights, i.e. the node's own τ. So the fraction reads directly:
**"this share of the LP objective is sitting on placements the hypothesis forbids."**

## The distribution (448 nodes, 35,799 dual-support columns)

```
frac_exact:  mean 0.4107   median 0.4000   min 0.0000   max 1.0000   zero 14   = 1.0  2
frac_grid :  mean 0.4466   median 0.4146
  [0.0,0.1)   19    [0.5,0.6)   44
  [0.1,0.2)   16    [0.6,0.7)   72
  [0.2,0.3)   83    [0.7,0.8)    7
  [0.3,0.4)   55    [0.8,0.9)   17
  [0.4,0.5)  133    [0.9,1.0]    2
```

**Two nodes carry 100 % of their LP objective on impossible columns** (`k5_11_interior_Y0588_D06`,
`k5_11_interior_Y1110`) and 19 more are above 0.75. Fourteen nodes are at zero — for those the
polygon core and the exact pin cores buy the LP nothing at all, and no amount of re-solving with
them will move τ.

The gap between the two columns is small in the mean (0.4466 vs 0.4107) but it is not noise: it is
the 256-column set measured in control (C) below.

## The population arithmetic

A142's 465 surviving work-owing A57 nodes (607 work-owing − 142 removed) minus A142's own **17**
exact-pin-clip kills (`exactclip_kills_a57.jsonl`, already certified in A131's format and awaiting
fold-in) = **448**. Every one of the 448 has a stored LP record with a hypothesis and a dual
support; nothing was estimated.

## Controls (`code/check145.py`, `results/check145.json`)

* **(A) Regression against A142, a different implementation.** A142's gallery counted the same two
  quantities with a pure-python `sat_poly` over an explicit 7³ loop; A145 vectorises through
  `polycore.poly_square_depth`. Over A142's 40 drawn A57 pages: **`n_support` 40/40 agree,
  grid-impossible 40/40 agree**, exact-impossible **36/40**. All four disagreements go the same way
  (A145 finds MORE: 142 vs 130, 147 vs 126, 4 vs 3, 6 vs 5) and have one cause: A142 tests the
  certified flag only against the box that owns the *minimum grid gap*, while A145 maximises the
  `K'` depth over **all six** boxes. A column can fail `K'` on its grid owner and meet `K'` on a
  different pin. A145's set is a strict superset of A142's by construction, so the direction of
  every disagreement is the prediction, not a surprise.
* **(B) Soundness of the EXACT test.** 1,920 columns called impossible-by-`K'`, 200 poses each drawn
  uniformly in the owning box, checked by an INDEPENDENT float SAT written from scratch in
  `check145.py`: **384,000 tests → 0 unsound.** This is the failure that would invalidate the whole
  measurement and it does not occur.
* **(C) The grid's own error, exhibited.** Of the 256 columns flagged by the 7³ grid but not by
  `K'`, a random search over 4,000 poses of the owning box found a genuinely DISJOINT pose for
  **1** (`k5_16_interior_Y0878` col 23, at pose (2.63493862, 1.65537044, 20.208786°)). So the grid
  is over-claiming on at least one column — the PI's reading is not exact — but the honest reading
  of (C) is the other one: **255 of the 256 grid-only columns are probably impossible and simply not
  provable by `K'`,** because overlapping at every pose is strictly weaker than meeting the
  intersection of the poses. The gap between `frac_grid` and `frac_exact` is mostly the *test's*
  conservatism, not the grid's optimism.

  `k5_11_interior_Y0241` is the worked example: 4 of 5 columns are flagged by the grid (gaps
  0.0153, 0.0231, 0.0351, 0.0530) and 3 of the 4 meet `K'`. The fourth (gap 0.0153) has `K'`-depth
  −1.085e−4, and that number does not move when `K'` is rebuilt at 513 θ-samples and 300 vertices
  (−1.085e−4 at every resolution), so it is the polygon that is right and the intersection really
  does miss that column — it is a genuine "overlaps at all 343 sampled poses, not proved at all
  poses" case.
