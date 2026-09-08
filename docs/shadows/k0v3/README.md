# The k0 residue gallery, v3 — the twelve converged-alive k0_00 cells

A140 (2026-09-07).  One page per cell, in the two-panel form the PI reviewed for A107's K-gallery (`docs/shadows.md` Part II), redrawn with the drawing rules of 2026-09-07 and carrying two objects the gallery has never shown: the **polygon core K'(B)** (A132) and the cell's **candidate cover**.

The twelve cells are A115 T6's hand-off list (`attempts/A115-k0-corner-rows/notes/t6_report.md`): tau = budget exactly, minmass 1.000, `converged = True` — the case-LP has reached its optimum and it is not below budget, so **no amount of further LP time kills them**.  Every page is drawn from A115's own converged record (`attempts/A115-k0-corner-rows/results/nodes/<nid>.t{4,5}.lp.json`), not from the A38/A99 record the cell was first seen in.

**k0_00 has no pins.**  Every hypothesis core of a k0 node IS a conditioned square, so the T5 pin-vs-box kill has no analogue; the only geometric kills available are column exclusion by K', K' leaving the container, and (where a cell carries more than one conditioned square) K' meeting K'.

## The table

| cell | level | s\* of the right panel | shadow family | polycore status (T1) | in-vitro LP under K' | candidate cover | what the PI's reading would decide |
|---|---|---|---|---|---|---|---|
| **l1_071** | 1 | 4.000000 (+0.122916 vs s-hat) | K01 (panel 2: A107 shadow) | K' meets 26 of 68 support columns (K(a) meets 0), weight 1.800 of 10.0 vs slack +4.0e-12; exact-core part 1.456 | tau 9.8402 < 10 but unconverged at the cap — **kill candidate** | re-branch on the occupied slot (A113) on BL(0,1) | **the polygon core drops tau below budget but the LP has not converged at the 240 s cap** — a warm continuation, not a reading, is the next step (the excluded weight is 1.80, of which 1.46 is inside the frozen schema); the PI's call is which slot to re-branch on — the support leans on BL(0,1), but the load path in panel 2 may name a different one. |
| **l1_104** | 1 | 3.914214 (+0.037130 vs s-hat) | K04 (panel 2: A107 shadow) | K' meets 6 of 17 support columns (K(a) meets 0), weight 3.500 of 10.0 vs slack -2.7e-14; exact-core part 2.500 | tau 9.6143 < 10 but unconverged at the cap — **kill candidate** | re-branch on the occupied slot (A113) on BR(0,0) | **the polygon core drops tau below budget but the LP has not converged at the 240 s cap** — a warm continuation, not a reading, is the next step (the excluded weight is 3.50, of which 2.50 is inside the frozen schema); the PI's call is which slot to re-branch on — the support leans on BR(0,0), but the load path in panel 2 may name a different one. |
| **l1_124** | 1 | 3.942810 (+0.065726 vs s-hat) | **none** (panel 2: A128 near-packing) | K' meets 7 of 17 support columns (K(a) meets 0), weight 4.000 of 10.0 vs slack -4.0e-13; exact-core part 3.000 | tau 10.0000 = budget (no kill) | two-meeter (A118 T4) on TR(0,0) | K' alone does not kill it (the LP replaces the excluded columns), so the reading has to name a structural obstruction, not a column count; the cover is decided by geometry already: TR(0,0) admits at most one non-conditioned meeter, so the PI only has to confirm the 'conditioned square meets it' arm is a real sub-box. |
| **l1_148** | 1 | 4.000000 (+0.122916 vs s-hat) | K01 (panel 2: A128 near-packing) | K' meets 2 of 10 support columns (K(a) meets 0), weight 2.000 of 10.0 vs slack -4.1e-14; exact-core part 2.000 | tau 9.6825 < 10 but unconverged at the cap — **kill candidate** | re-branch on the occupied slot (A113) on BL(0,0) | **the polygon core drops tau below budget but the LP has not converged at the 240 s cap** — a warm continuation, not a reading, is the next step (the excluded weight is 2.00, of which 2.00 is inside the frozen schema); the PI's call is which slot to re-branch on — the support leans on BL(0,0), but the load path in panel 2 may name a different one. |
| **l1_153** *(Trump image)* | 1 | n/a — panel 2 is the raw support at s0, overlap 0.159 | **none** (panel 2: raw support) | K' meets 4 of 10 support columns (K(a) meets 0), weight 4.000 of 10.0 vs slack -4.4e-14; exact-core part 2.000 | tau 10.0000 = budget (no kill) | two-meeter (A118 T4) on TR(0,0) | K' alone does not kill it (the LP replaces the excluded columns), so the reading has to name a structural obstruction, not a column count; the cover is decided by geometry already: TR(0,0) admits at most one non-conditioned meeter, so the PI only has to confirm the 'conditioned square meets it' arm is a real sub-box. |
| **l1_158** | 1 | 3.902674 (+0.025591 vs s-hat) | **none** (panel 2: A128 near-packing) | K' meets 4 of 16 support columns (K(a) meets 0), weight 2.000 of 10.0 vs slack +0.0e+00; exact-core part 1.500 | tau 10.0000 = budget (no kill) | two-meeter (A118 T4) on TR(0,0) | K' alone does not kill it (the LP replaces the excluded columns), so the reading has to name a structural obstruction, not a column count; the cover is decided by geometry already: TR(0,0) admits at most one non-conditioned meeter, so the PI only has to confirm the 'conditioned square meets it' arm is a real sub-box. |
| **l1_159** | 1 | 3.886745 (+0.009662 vs s-hat) | K06 (panel 2: A107 shadow) | K' meets 3 of 15 support columns (K(a) meets 0), weight 2.000 of 10.0 vs slack +2.3e-14; exact-core part 1.500 | tau 10.0000 = budget (no kill) | two-meeter (A118 T4) on TR(0,0) | K' alone does not kill it (the LP replaces the excluded columns), so the reading has to name a structural obstruction, not a column count; the cover is decided by geometry already: TR(0,0) admits at most one non-conditioned meeter, so the PI only has to confirm the 'conditioned square meets it' arm is a real sub-box. |
| **l2_p114_001** | 2 | 3.924402 (+0.047319 vs s-hat) | K20 (panel 2: A107 shadow) | K' meets 3 of 10 support columns (K(a) meets 0), weight 3.000 of 10.0 vs slack +0.0e+00; exact-core part 1.000 | tau 9.9659 < 10 but unconverged at the cap — **kill candidate** | re-branch on the occupied slot (A113) on BR(0,0) | **the polygon core drops tau below budget but the LP has not converged at the 240 s cap** — a warm continuation, not a reading, is the next step (the excluded weight is 3.00, of which 1.00 is inside the frozen schema); the PI's call is which slot to re-branch on — the support leans on BR(0,0), but the load path in panel 2 may name a different one. |
| **l2_p65_101** | 2 | 4.000000 (+0.122916 vs s-hat) | K01 (panel 2: A107 shadow) | K' meets 38 of 83 support columns (K(a) meets 0), weight 3.716 of 10.0 vs slack -3.6e-15; exact-core part 3.315 | tau 8.7763 < 10 but unconverged at the cap — **kill candidate** | re-branch on the occupied slot (A113) on BL(0,0) | **the polygon core drops tau below budget but the LP has not converged at the 240 s cap** — a warm continuation, not a reading, is the next step (the excluded weight is 3.72, of which 3.31 is inside the frozen schema); the PI's call is which slot to re-branch on — the support leans on BL(0,0), but the load path in panel 2 may name a different one. |
| **l2_p65_111** | 2 | 3.925149 (+0.048065 vs s-hat) | K03 (panel 2: A107 shadow) | K' meets 24 of 60 support columns (K(a) meets 0), weight 3.450 of 10.0 vs slack +5.3e-15; exact-core part 2.950 | tau 8.8410 < 10 but unconverged at the cap — **kill candidate** | re-branch on the occupied slot (A113) on BL(0,1) | **the polygon core drops tau below budget but the LP has not converged at the 240 s cap** — a warm continuation, not a reading, is the next step (the excluded weight is 3.45, of which 2.95 is inside the frozen schema); the PI's call is which slot to re-branch on — the support leans on BL(0,1), but the load path in panel 2 may name a different one. |
| **l2_p74_001** | 2 | 3.912232 (+0.035148 vs s-hat) | K05 (panel 2: A107 shadow) | K' meets 2 of 10 support columns (K(a) meets 0), weight 2.000 of 10.0 vs slack +1.6e-14; exact-core part 2.000 | tau 9.9592 < 10 but unconverged at the cap — **kill candidate** | re-branch on the occupied slot (A113) on BR(0,0) | **the polygon core drops tau below budget but the LP has not converged at the 240 s cap** — a warm continuation, not a reading, is the next step (the excluded weight is 2.00, of which 2.00 is inside the frozen schema); the PI's call is which slot to re-branch on — the support leans on BR(0,0), but the load path in panel 2 may name a different one. |
| **s3_far_BL389484_TR018470** | 4 | 3.985467 (+0.108383 vs s-hat) | K26 (panel 2: A107 shadow) | K' meets 9 of 14 support columns (K(a) meets 0), weight 4.333 of 7.0 vs slack +0.0e+00; exact-core part 3.667 | **tau 6.0000, CONVERGED — LP-dead under polygon core, certificate pending** | two-meeter (A118 T4) on BL(0,0) | **the polygon core already kills it in vitro, converged** — the reading needed is whether the K' row filter is worth a verifier change (A135 route: the exact axis core is inside the frozen schema and removes 3.67 of the 4.33 excluded weight); the cover is decided by geometry already: BL(0,0) admits at most one non-conditioned meeter, so the PI only has to confirm the 'conditioned square meets it' arm is a real sub-box. |

## The three cells that had no drawing before

A107's gallery was built before A115's last pass, from the A38/A99 records.  Three of the twelve appear in it under **no alias at all** — A38 has no node json for them (they were in A115's `notrun` pool) and A99 never produced a `plain_warm` record for them:

* **`l1_124`** — right panel: A128 near-packing of the converged support (all 11 squares polished free), worst gap -1.8e-11.
* **`l1_153`** — the Trump-image cell (A38 l1 idx 153); it must stay alive — right panel: RAW integral dual support at the certified side s0, plus the conditioned square at the centre of its box and tilt window. This cell has neither a gallery shadow nor a polished near-packing. It is NOT a packing and NOT minimised: the conditioned square OVERLAPS the support (see the min pairwise SAT separation below) -- that overlap is exactly the 'impossible column' effect the left panel draws in red..
* **`l1_158`** — right panel: A128 near-packing of the converged support (all 11 squares polished free), worst gap -1.6e-08.

One correction to the brief: `l1_148` DOES have an A107 entry — its unconverged A99 alias `l1_148_plain_warm` sits in **K01** — while `l1_153` has none.  The cells A128 built near-packings for (`l1_124`, `l1_148`, `l1_158`) and the cells with no gallery entry (`l1_124`, `l1_153`, `l1_158`) are different sets.

## Files

| file | what |
|---|---|
| [`l1_071.svg`](l1_071.svg) | l1_071: LP dual support with K' and 28 impossible column(s); panel 2 at s\* = 4.000000; the re-branch on the occupied slot (A113) cover on BL(0,1) |
| [`l1_104.svg`](l1_104.svg) | l1_104: LP dual support with K' and 6 impossible column(s); panel 2 at s\* = 3.914214; the re-branch on the occupied slot (A113) cover on BR(0,0) |
| [`l1_124.svg`](l1_124.svg) | l1_124: LP dual support with K' and 7 impossible column(s); panel 2 at s\* = 3.942810; the two-meeter (A118 T4) cover on TR(0,0) |
| [`l1_148.svg`](l1_148.svg) | l1_148: LP dual support with K' and 2 impossible column(s); panel 2 at s\* = 4.000000; the re-branch on the occupied slot (A113) cover on BL(0,0) |
| [`l1_153.svg`](l1_153.svg) | l1_153: LP dual support with K' and 4 impossible column(s); panel 2 at s0 (raw support, not a packing); the two-meeter (A118 T4) cover on TR(0,0) |
| [`l1_158.svg`](l1_158.svg) | l1_158: LP dual support with K' and 4 impossible column(s); panel 2 at s\* = 3.902674; the two-meeter (A118 T4) cover on TR(0,0) |
| [`l1_159.svg`](l1_159.svg) | l1_159: LP dual support with K' and 3 impossible column(s); panel 2 at s\* = 3.886745; the two-meeter (A118 T4) cover on TR(0,0) |
| [`l2_p114_001.svg`](l2_p114_001.svg) | l2_p114_001: LP dual support with K' and 3 impossible column(s); panel 2 at s\* = 3.924402; the re-branch on the occupied slot (A113) cover on BR(0,0) |
| [`l2_p65_101.svg`](l2_p65_101.svg) | l2_p65_101: LP dual support with K' and 42 impossible column(s); panel 2 at s\* = 4.000000; the re-branch on the occupied slot (A113) cover on BL(0,0) |
| [`l2_p65_111.svg`](l2_p65_111.svg) | l2_p65_111: LP dual support with K' and 28 impossible column(s); panel 2 at s\* = 3.925149; the re-branch on the occupied slot (A113) cover on BL(0,1) |
| [`l2_p74_001.svg`](l2_p74_001.svg) | l2_p74_001: LP dual support with K' and 3 impossible column(s); panel 2 at s\* = 3.912232; the re-branch on the occupied slot (A113) cover on BR(0,0) |
| [`s3_far_BL389484_TR018470.svg`](s3_far_BL389484_TR018470.svg) | s3_far_BL389484_TR018470: LP dual support with K' and 9 impossible column(s); panel 2 at s\* = 3.985467; the two-meeter (A118 T4) cover on BL(0,0) |
| [`review_k0v3.csv`](review_k0v3.csv) | review.csv's columns plus `polycore_status`, `candidate_cover`, the k0v3 measurements, and empty `PI_*` columns |

## How to read a page

* **LEFT** — the LP dual support of the converged record.  Fill = the dual weight y on one sequential scale (pale yellow y→0, dark orange y=1).  Bright cyan + heavy black outline + **H** = a conditioned square, drawn at the **centre of its box** and the **centre of its tilt window**; the faint cyan outlines are the same square at the two **extremal tilts**.  Purple = the certified **polygon core K'(B)**.  Red dashed = a support column that overlaps a hypothesis square at **every** pose of its box — impossible under the node's own hypothesis, kept by the LP only because the LP prunes against the axis core K(a).

* **RIGHT** — a real packing with the square names the PI labels from: blue = slot square (named corner cell), red = free square (f-index + tilt), green ring = a contact at gap < 1e-6.  Source is stated in the subtitle: A107's minimised shadow, A128's polished near-packing, or the raw integral dual support at s0.

* **THIRD** — the candidate cover.  Amber = the cell to branch on; faint green = the other slots the support occupies, with their weight and multiplicity.

* Under the panels: the box(es), tau / eta / minmass, the T1 polygon-core measurement, the slot census (A113), the lane count (A118), the cover in words with what it needs to be a certified leaf, and the geometry check.

## The two levers, and how they split the twelve

* **Polygon core.**  In vitro, K' drops tau below budget on 8 of 12: `l1_071`, `l1_104`, `l1_148`, `l2_p114_001`, `l2_p65_101`, `l2_p65_111`, `l2_p74_001`, `s3_far_BL389484_TR018470`.  Of those, 1 also CONVERGED below budget (`s3_far_BL389484_TR018470`) and is LP-dead under the polygon core; the rest are `dead_unconverged` kill candidates at the 240 s cap.

* **Lane count.**  5 of 12 carry a corner cell with LANE <= 1: `l1_124` (TR(0,0)), `l1_153` (TR(0,0)), `l1_158` (TR(0,0)), `l1_159` (TR(0,0)), `s3_far_BL389484_TR018470` (BL(0,0)).  Three of these verdicts (`l1_124`, `l1_153`, `l1_158`) are NEW — A118 never saw those cells.

* The two levers **partition the residue almost exactly**: `s3_far_BL389484_TR018470` is in both, and every one of the twelve is in at least one bucket, so none is without a concrete route.

* **The cheapest untried measurement** is an exact-core arm of the in-vitro LP: A135's exact axis core needs no verifier change and already removes 50-100 % of K''s excluded weight on nine of the twelve.  It was not run here (the brief allows one LP per cell).

## Provenance and soundness

* Every K' is A132's **certified** polygon (exact rational vertex test, `polycore.vertex_ok`); the half-side of the exact axis core is A135's `exactcore.exact_a`, certified the same way.

* An in-vitro kill is **not** a certificate: the frozen verifier knows only K(a).  The A135 exact axis core IS a square at the box's own tilt and therefore fits the frozen schema, so the `exact-core part` column is the weight a kill could claim **today**; the rest needs the v3 verifier.

* Every drawn square is containment-checked, and every red-dashed column's overlap is re-verified by an independent SAT implementation at 7³ = 343 poses of its box.

* Read-only on every campaign; the only files written are under `attempts/A140-k0-residue-gallery/` and `docs/shadows/k0v3/`, plus this Part III pointer in `docs/shadows.md`.
