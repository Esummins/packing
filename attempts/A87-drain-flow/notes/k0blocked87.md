# A87 chore: K0-FREE vs K0-BLOCKED at the 167 certified k0 FJ points

## Headline

* **0 of the 167 are genuinely K0-BLOCKED** (no free corner slot after removing at most one square, and no translational plateau exit that reaches a k >= 1 or K0-FREE endpoint).
* Lowest sigma among the genuine K0-BLOCKED: **None** (None).
* Lowest sigma over all 167 (o012, the PI's example): 3.897230786656917.
* Every K0-FREE verdict was **rebuilt and re-verified exactly**: 179 teleported packings, 167 certified strictly (interval SAT gap >= 0), 179 certified up to an exact touch, worst side excess over the original sigma = 0.0.

## Table

| test | count |
| --- | ---: |
| K0_FREE_by_teleport | 167 |
|   of which slot free with NO removal (K0_FREE_0) | 12 |
|   of which free after removing one blocker | 155 |
| NEAR_SIMPLE_within_1e-2 (any point) | 69 |
|   near-simple AND not K0-FREE | 0 |
| plateau_end_has_k>=1 (not already K0-FREE) | 0 |
| plateau_end_K0_FREE (not already K0-FREE) | 0 |
| genuinely_K0_BLOCKED (no teleport, no plateau exit) | 0 |
|   of which also near-simple within 1e-2 | 0 |

## K0-BLOCKED survivors

| tag | sigma | DEPTH BL | BR | TL | TR | d_H | d_transl | rattlers | eps_simple | min blockers/corner |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| (none) | | | | | | | | | | |

No point survives, so the closest approaches are listed instead: the highest `min_n_block` (a point is K0-BLOCKED only if every corner slot is hit by >= 2 squares) and, within that, the largest distance to a simple placement.

| tag | sigma | n_block BL/BR/TL/TR | DEPTH BL | BR | TL | TR | d_H | d_transl | eps_simple |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| o132 | 4.000000000 | 1/1/1/1 | 0.0335 | 0.0031 | 0.0549 | 0.0032 | 7 | 7 | 9.45e-01 |
| o123 | 4.000000000 | 1/1/1/1 | 0.3118 | 0.0774 | 0.1075 | 0.0132 | 12 | 10 | 7.52e-01 |
| o249 | 4.242640687 | 1/1/1/1 | 0.4677 | 0.6464 | 0.6464 | 0.4693 | 10 | 3 | 6.93e-01 |
| o258 | 5.000000000 | 1/1/1/1 | 0.3718 | 0.3801 | - | - | 22 | 16 | 6.39e-01 |
| o252 | 4.242892863 | 1/1/1/1 | 0.5329 | 0.6466 | 0.6466 | 0.5329 | 2 | 1 | 5.75e-01 |
| o239 | 4.242640687 | 1/1/1/1 | 0.6230 | 0.6464 | 0.6464 | 0.5401 | 22 | 15 | 4.94e-01 |
| o241 | 4.242640687 | 1/1/1/1 | 0.6342 | 0.6464 | 0.6464 | 0.5162 | 20 | 13 | 4.86e-01 |
| o108 | 4.000000000 | 1/1/1/1 | 0.7000 | 0.3565 | 0.3783 | 0.1724 | 15 | 12 | 4.68e-01 |
| o233 | 4.000000000 | 1/1/1/1 | 0.6768 | 0.5587 | 0.4071 | 0.2821 | 16 | 13 | 4.64e-01 |
| o097 | 4.000000000 | 1/1/1/1 | 0.7018 | 0.4621 | 0.3458 | 0.2385 | 15 | 12 | 4.61e-01 |
| o110 | 4.000000000 | 1/1/1/1 | 0.7027 | 0.4612 | 0.3463 | 0.2385 | 16 | 13 | 4.60e-01 |
| o150 | 4.000000000 | 1/1/1/1 | 0.7129 | 0.3301 | 0.3311 | 0.0031 | 9 | 8 | 4.33e-01 |
| o129 | 4.000000000 | 1/1/2/1 | 0.4990 | 0.5127 | 0.0937 | 0.1417 | 12 | 11 | 4.19e-01 |
| o099 | 4.000000000 | 1/1/1/1 | 0.3808 | 0.0243 | 0.7034 | 0.3329 | 11 | 10 | 3.70e-01 |
| o156 | 4.000000000 | 1/1/1/1 | 0.3819 | 0.0215 | 0.7040 | 0.3306 | 11 | 10 | 3.68e-01 |

## Atlas (12 A46/A37 families)

| tag | class | sigma | K0-FREE | k_num | eps_simple | plateau | K0-BLOCKED |
| --- | --- | ---: | --- | ---: | ---: | --- | --- |
| fam0 | RIGID | 3.877083590 | True | 3 | 0.00e+00 | no_translational_flex | False |
| fam1 | VALLEY | 3.885618083 | True | 3 | 0.00e+00 | no_end | False |
| fam2 | VALLEY | 3.885618083 | True | 3 | 0.00e+00 | no_end | False |
| fam6 | VALLEY | 3.886746029 | True | 3 | 0.00e+00 | no_end | False |
| fam13 | VALLEY | 3.897230787 | True | 1 | 0.00e+00 | no_end | False |
| fam14 | VALLEY | 3.897230787 | True | 1 | 0.00e+00 | no_end | False |
| famA37-NEW-0 | VALLEY | 3.902673974 | True | 2 | 0.00e+00 | no_end | False |
| famA37-NEW-1 | VALLEY-MARGINAL | 3.912232040 | True | 2 | 0.00e+00 | no_end | False |
| famA37-NEW-2 | VALLEY | 3.924402476 | True | 1 | 0.00e+00 | no_end | False |
| fam27 | VALLEY-MARGINAL | 3.925148812 | True | 2 | 0.00e+00 | no_end | False |
| famA37-NEW-3 | VALLEY | 3.925470067 | True | 2 | 0.00e+00 | no_end | False |
| fam31 | VALLEY | 3.936964160 | True | 2 | 0.00e+00 | no_end | False |

## Cross-check against A89

The per-corner blocker SETS were compared against A89's independent census (`A89/results/t2_blockers_a87.jsonl`) on all 668 (point, corner) pairs: **658 agree exactly, 10 differ**, and all 10 are sigma = 5 points whose bounding box is NOT square (e.g. 3.75 x 5.00).  A89 anchors the container at `[origin, origin + sigma]^2`, so its right-hand slots sit beyond the occupied region and see no blocker; this analysis anchors each slot at the TIGHT bounding box, which is the conservative choice (the slot is pushed further into the interior, so more squares can block it, and the teleported packing is guaranteed to have side <= sigma).  Every disagreement therefore makes this test strictly harder, never easier.

## Method

A87 chore: is the "certified k0" label of the 167 FJ points real, or are they
k >= 1 points in disguise?

MOTIVATION (PI).  o012, the lowest certified k0 FJ point (sigma 3.897231), is a
k >= 1 point in disguise: square 0 is axis-aligned 4e-4 above the BL corner slot,
and square 5 is a rattler whose removal leaves the TR unit slot [s-1,s]^2
completely free -- so the teleport lemma (K0-FREE / CC-2) makes it a k1 point at
the SAME side.  The 167 points of results/cp87_fj_polished.jsonl were labelled
k0 by the EXACT SIMPLE-SQUARE COUNT only; the residue the proof actually needs is
K0-BLOCKED.

THE FOUR TESTS, per configuration z (34 exact rationals, theta in radians):

(1) TELEPORT.  origin/extent from the tight bounding box of the 44 corners;
    the four closed unit corner slots are anchored at the bbox corners and
    pushed INWARD by the interval width (the conservative choice: an inward
    slot overlaps more of the interior, so a certified-free verdict is sound
    for the true slot too, and the inward slot is still inside the container).
    For every corner c and every square j, the slot/square interior-disjointness
    is decided by SAT on the 4 candidate axes (2 slot axes + 2 edge normals of
    j) in outward-rounded interval arithmetic: gap.a >= 0 certifies disjoint,
    gap.b < 0 certifies overlap, otherwise UNKNOWN (dps is raised and retried).

      n_block(c) := #{ j : not certified disjoint from slot c }
      n_block(c) = 0  ->  the slot is free with NO square removed  (K0-FREE-0)
      n_block(c) = 1  ->  removing the unique blocker j and teleporting it into
                          the slot gives a packing of 11 unit squares at a side
                          <= sigma with an axis-aligned corner-slot square,
                          i.e. k >= 1 at the same side.        (K0-FREE)

    Soundness of the teleport: the slot is inside the tight bbox, the other 10
    squares are unmoved, so the new configuration's enclosing side is <= sigma.

(2) NEAR-SIMPLE.  For each square i, tilt_i = dist(theta_i, (pi/2) Z), and for
    each corner slot the sup-norm centre offset.  eps_simple(i) =
    min_c max(|dc|_inf, tilt_i); the point is NEAR-SIMPLE at 1e-2 if some
    square has eps_simple < 1e-2 (an epsilon-lift: the point is a perturbation
    of a k >= 1 configuration).

(3) PLATEAU-END.  Along a TRANSLATIONAL flex direction (flex space of
    fjsecond87 intersected with {all theta components 0}) every SAT gap and
    every wall gap is EXACTLY AFFINE in the step t, because the normals do not
    move:  g(t) = g(0) + t * n.(dc_p - dc_o).  So the first-new-contact step
    t* is available in closed form (per pair, the sup of the connected
    component of the union of the 4 axis half-lines that contains t = 0; per
    wall, the usual ratio), no line search slop.  The endpoint z(t*) is
    re-verified exactly (rational step, interval SAT) and re-classified by
    tests (1) and (2).

(4) DEPTH.  A89's corner intrusion depth, DEPTH(c) = max over the blockers of
    c of (1 - f_min_max), read from A89 results/t2_blockers_a87.jsonl (already
    annotated by A89 code/t2b_depth.py), reported for the K0-BLOCKED survivors
    together with d_H (flat_dim_33) from results/fjsecond87.jsonl.

Also run on the 12 A46/A37 atlas families (z_center of each family's cert).

Usage: python k0blocked87.py {selftest|run|atlas|report|all}
One process, BLAS pinned.  Writes only results/k0blocked87.{jsonl,atlas.jsonl,
json} and notes/k0blocked87.md.
