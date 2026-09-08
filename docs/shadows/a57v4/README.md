# The A57 / A60 review gallery v4 (60 nodes)

One page per node, in the **v4 three-panel form**.  Every page answers the same question first —
*can the remaining squares fit in the white space?* — and only then shows the LP.

| panel | what it is |
|---|---|
| **G — GEOMETRY: what is still free** (largest) | the container at s0, the hypothesis squares with their certified cores, and the **feasible-centre region**: the set of centres where one further unit square can still be placed at SOME tilt, interior-disjoint from every pin's exact core and from K'(B) of every conditioned square.  Green = certified free, pale = undecided at this resolution, white = certified blocked.  Pockets narrower than 1 are hatched grey with the width printed; A144 guard lines are drawn thin with their chord sum and rhs; each corner/slot carries A141's K' lane verdict; A131's exact pin-clip is the orange box inside the black centre box.  **Nothing in panel G comes from an LP.** |
| **S — the LP support** (medium) | the dual support of the node's latest record, fill = dual weight on one sequential scale (A107 v2), the certified cores outlined, and every column whose square overlaps a core drawn **red dashed**: those are impossible under the hypothesis.  The squares here overlap each other — that is the relaxation's slack, not a packing. |
| **N — nearest real packing** (small) | A107's minimised shadow or A128's polished near-packing, the container at its own s* with s0 overlaid dashed and a banner saying whether it is realisable at s0.  These are the square names used everywhere else. |

**Soundness of the green region.**  The region is computed on a grid of pitch ≤ 0.02 × 36 tilts, and
both verdicts carry the Lipschitz margin `m = pitch·√2/2 + (√2/2)·(Δθ/2)` (SAT depth between convex
sets is 1-Lipschitz in the centre and (√2/2)-Lipschitz in the tilt).  So **GREEN is a certified
inner approximation** — every point of a green cell admits a feasible tilt — and **WHITE a certified
outer one** — no point of a white cell admits any tilt.  Sampled confirmation per page: 10⁴ centres
drawn uniformly in the green cells and 10⁴ in the blocked cells, tested at 360 tilts with an
independent SAT (0 and 0 hits over the whole set).  An independent
re-verification (edge crossing + strict point-in-polygon, no separating axis anywhere in it) is
`attempts/A148-gallery-v4/code/verify148.py`; its result is
`attempts/A148-gallery-v4/results/verify148_a57v4.json`.

**The disk bound — the shortcut this gallery is for.**  A unit square contains the disk of radius
1/2 about its centre, so the centres of the `budget` remaining squares carry pairwise disjoint
half-unit disks inside the container, and each centre lies in (green ∪ undecided).  Hence

>  `budget  ≤  area( (green ∪ undecided) ⊕ B(1/2)  ∩  [0,s0]² ) / (π/4)`

which is a **sound upper bound on how many more squares the node can hold, read straight off the
drawing**.  `n_max < budget` is a geometric kill with no LP at all.  The column is in the table.

**Population and timestamp.**  The campaign records were read at **2026-09-08 06:05 -0700**, while A137's night shift was still running (it pauses at 07:00), so this set is the night's records AS THEY STOOD at that moment.  The base is A142's subtree-cost ranking (`population142.json`); on top of it `data148.night_kills()` removes every node killed since A142 built that file — **1 777 ids**: 798 from A137's own night records (`emit_lp*`, `exact_reemit*`, `clipkills137`), 515 from A57's tree rows now recorded KILL-BY-LOGIC / CERTIFIED, 173 certified dead by A145's and A137's exact-core re-solves (result PASS-V3 / PASS-FROZEN), and 291 by A141's K′ lane and slot-lane leaves — together with their descendants (a geometric kill is inherited).  What remains is re-ranked by A142's formula; this gallery is the **top 40 surviving A57 nodes and the top 20 surviving A60 nodes**.  The frozen population record is `attempts/A148-gallery-v4/results/population148_a57v4.json`.

**Two of the sixty are DEAD.**  `c0_Y0254` and `c0_Y0168` carry a KILLED banner: their T5⁗ verdict fires, because the exact pin core at (0.5, 1.5) and the conditioned square's polygon core K′(B) OVERLAP (by 0.015346 and 0.002429). Both cores sit inside their squares at every admissible pose, so those two squares can never be interior-disjoint and the node hypothesis is unsatisfiable — dead by geometry, no LP. Sampled check: 0 of 10⁵ poses in each box give a square disjoint from the pinned one. Records: `attempts/A148-gallery-v4/results/t5_kills_a148.jsonl`; certificates are NOT emitted here.

## The table

| node | level | s\* of panel N | family | green area | green+undec. | disk bound n\_max (budget) | narrowest pocket | pockets < 1 | lane tags (hot) | tightest guard rhs | leaves run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [`k5_11_interior_Y1104`](k5_11_interior_Y1104.svg) | 1 | 3.902674 | S10 | 0.427 | 1.124 | **9** (5) | `H->wall x=s` 0.8022 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0672`](k5_11_interior_Y0672.svg) | 1 | 4.000261 | S53 | 0.143 | 1.087 | **10** (5) | `P1-P2` 0.8912 | 2 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0083`](k5_16_interior_Y0083.svg) | 1 | 3.886746 | S02 | 1.184 | 1.747 | **10** (5) | `P1-H` 0.4385 | 5 | — | 0.8771 (`pin core x0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0738`](k5_11_interior_Y0738.svg) | 1 | 3.886746 | S02 | 2.213 | 2.694 | **9** (5) | `P1-H` 0.1231 | 8 | — | 0.2811 (`grid v 2/8`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y1110`](k5_11_interior_Y1110.svg) | 1 | 3.924003 | S36 | 0.155 | 1.039 | **10** (5) | `P1-P2` 0.8912 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0662`](k5_11_interior_Y0662.svg) | 1 | 3.877084 | none | 0.391 | 1.092 | **9** (5) | `H->wall y=s` 0.8172 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0130`](k5_11_interior_Y0130.svg) | 1 | 4.000000 | S01 | 0.004 | 0.967 | **10** (5) | `P1-P2` 0.8912 | 2 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0275`](k5_11_interior_Y0275.svg) | 1 | 3.877084 | none | 0.304 | 1.021 | **10** (5) | `P1-H` 0.8419 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0308`](k5_11_interior_Y0308.svg) | 1 | 4.000000 | S01 | 0.360 | 1.068 | **9** (5) | `H->wall y=s` 0.8449 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0985`](k5_11_interior_Y0985.svg) | 1 | 4.000000 | S01 | 0.410 | 1.146 | **9** (5) | `H->wall x=s` 0.8297 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0027`](k5_16_interior_Y0027.svg) | 1 | 4.000000 | S01 | 0.889 | 1.459 | **11** (5) | `P3-H` 0.4544 | 3 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0191`](k5_16_interior_Y0191.svg) | 1 | 3.942809 | S03 | 1.490 | 1.982 | **10** (5) | `P1-H` 0.2712 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0275`](k5_16_interior_Y0275.svg) | 1 | 3.976620 | S11 | 1.000 | 1.542 | **10** (5) | `P4-H` 0.2082 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0839`](k5_16_interior_Y0839.svg) | 1 | 4.000000 | S01 | 1.186 | 1.773 | **10** (5) | `P3-H` 0.2089 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0842`](k5_16_interior_Y0842.svg) | 1 | 3.886746 | S02 | 0.908 | 1.582 | **10** (5) | `P3-H` 0.4325 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0881`](k5_16_interior_Y0881.svg) | 1 | 4.000000 | S01 | 1.010 | 1.485 | **10** (5) | `P4-H` 0.4605 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0941`](k5_16_interior_Y0941.svg) | 1 | 3.886746 | S02 | 1.157 | 1.793 | **10** (5) | `P1-H` 0.3958 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y1056`](k5_16_interior_Y1056.svg) | 1 | 3.914214 | S08 | 1.536 | 2.197 | **10** (5) | `P1-H` 0.2596 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0460`](k5_16_interior_Y0460.svg) | 1 | 3.877084 | none | 1.313 | 1.820 | **10** (5) | `P3-H` 0.4663 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0249`](k5_16_interior_Y0249.svg) | 1 | 3.942809 | S03 | 0.928 | 1.572 | **11** (5) | `P4-H` 0.2868 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0402`](k5_16_interior_Y0402.svg) | 1 | 3.942809 | S03 | 1.530 | 2.069 | **10** (5) | `P1-H` 0.3059 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y1117`](k5_16_interior_Y1117.svg) | 1 | 4.000000 | S01 | 0.993 | 1.749 | **10** (5) | `P4-H` 0.2426 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0500`](k5_16_interior_Y0500.svg) | 1 | 4.000000 | S01 | 0.967 | 1.577 | **10** (5) | `P4-H` 0.3294 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0044`](k5_16_interior_Y0044.svg) | 1 | 4.000000 | S01 | 1.474 | 1.981 | **10** (5) | `P1-H` 0.3059 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0147`](k5_11_interior_Y0147.svg) | 1 | 4.000000 | S01 | 0.567 | 1.215 | **9** (5) | `H->wall y=s` 0.7398 | 3 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_11_interior_Y0202`](k5_11_interior_Y0202.svg) | 1 | 3.912232 | S05 | 1.940 | 2.400 | **9** (5) | `P3-H` 0.1715 | 6 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0054`](k5_16_interior_Y0054.svg) | 1 | 3.886746 | S02 | 1.076 | 1.662 | **10** (5) | `P3-H` 0.5346 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0099`](k5_16_interior_Y0099.svg) | 1 | 3.942809 | S03 | 0.846 | 1.511 | **11** (5) | `P4-H` 0.2301 | 3 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0230`](k5_16_interior_Y0230.svg) | 1 | 4.000000 | S01 | 1.229 | 1.792 | **10** (5) | `P1-H` 0.4110 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0325`](k5_16_interior_Y0325.svg) | 1 | 4.000000 | S01 | 0.916 | 1.528 | **11** (5) | `P4-H` 0.4663 | 3 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0380`](k5_16_interior_Y0380.svg) | 1 | 3.886746 | S02 | 1.104 | 1.679 | **10** (5) | `P1-H` 0.5230 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0436`](k5_16_interior_Y0436.svg) | 1 | 3.877084 | none | 0.891 | 1.528 | **11** (5) | `P4-H` 0.3353 | 3 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0491`](k5_16_interior_Y0491.svg) | 1 | 4.000000 | S01 | 1.189 | 1.735 | **9** (5) | `P3-H` 0.1472 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0565`](k5_16_interior_Y0565.svg) | 1 | 4.000000 | S01 | 0.981 | 1.546 | **11** (5) | `P3-H` 0.5821 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0660`](k5_16_interior_Y0660.svg) | 1 | 3.942809 | S03 | 1.078 | 1.640 | **10** (5) | `P3-H` 0.2156 | 4 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0719`](k5_16_interior_Y0719.svg) | 1 | 4.000000 | S01 | 1.007 | 1.499 | **10** (5) | `P4-H` 0.4626 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0865`](k5_16_interior_Y0865.svg) | 1 | 3.942809 | S03 | 1.194 | 1.678 | **9** (5) | `P3-H` 0.4626 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y0991`](k5_16_interior_Y0991.svg) | 1 | 3.942809 | S03 | 1.132 | 1.675 | **10** (5) | `P3-H` 0.2779 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y1022`](k5_16_interior_Y1022.svg) | 1 | 3.942809 | S03 | 1.291 | 1.814 | **9** (5) | `P3-H` 0.1531 | 6 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`k5_16_interior_Y1039`](k5_16_interior_Y1039.svg) | 1 | 3.886746 | S02 | 0.919 | 1.591 | **10** (5) | `P3-H` 0.4420 | 5 | — | 0.8771 (`pin midline x`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`slack0.02_c0_Y0272`](slack0.02_c0_Y0272.svg) | 1 | 4.000000 | S01 | 1.090 | 1.671 | **10** (5) | `P2-H` 0.2094 | 3 | — | 0.8771 (`pin midline y`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0254`](c0_Y0254.svg) | 1 | 4.000000 | S01 | 1.425 | 2.083 | **10** (5) | `P1-H` 0.6834 | 4 | — | 0.8771 (`pin core y0`) | clip, T5⁗ DEAD, lane no kill, guard no kill |
| [`c0_Y0258`](c0_Y0258.svg) | 1 | 4.000000 | S01 | 1.265 | 1.914 | **9** (5) | `P2-H` 0.1306 | 5 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0787`](c0_Y0787.svg) | 1 | 4.000000 | S01 | 1.878 | 2.453 | **10** (5) | `P1-H` 0.1301 | 6 | — | 0.5156 (`pin core y1`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0939`](c0_Y0939.svg) | 1 | 4.000000 | S01 | 0.942 | 1.703 | **9** (5) | `P4-H` 0.2344 | 5 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0942`](c0_Y0942.svg) | 1 | 4.000000 | S01 | 0.932 | 1.649 | **10** (5) | `P4-H` 0.1439 | 6 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0959`](c0_Y0959.svg) | 1 | 4.000000 | S01 | 1.326 | 1.990 | **10** (5) | `H->wall y=s` 0.7398 | 2 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y1033`](c0_Y1033.svg) | 1 | 4.000000 | S01 | 1.187 | 1.902 | **10** (5) | `P4-H` 0.0792 | 4 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y1038`](c0_Y1038.svg) | 1 | 4.000000 | S01 | 1.185 | 1.756 | **10** (5) | `P4-H` 0.1048 | 5 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`f1_L10_0003`](f1_L10_0003.svg) | 1 | 3.885618 | S07 | 0.527 | 0.937 | **7** (4) | `P1-H` 0.2575 | 6 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0952`](c0_Y0952.svg) | 1 | 4.000000 | S01 | 1.425 | 2.035 | **10** (5) | `P4-H` 0.0623 | 3 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0788`](c0_Y0788.svg) | 1 | 3.942809 | S03 | 1.853 | 2.414 | **9** (5) | `P1-H` 0.1306 | 6 | — | 0.5161 (`pin core y1`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0257`](c0_Y0257.svg) | 1 | 3.914214 | S08 | 1.266 | 1.887 | **10** (5) | `P2-H` 0.1266 | 5 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0878`](c0_Y0878.svg) | 1 | 4.000000 | S01 | 1.998 | 2.593 | **10** (5) | `P3-H` 0.1048 | 6 | — | 0.0087 (`pin core y1`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0695`](c0_Y0695.svg) | 1 | 3.886746 | S02 | 1.897 | 2.430 | **9** (5) | `P3-H` 0.3606 | 4 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0255`](c0_Y0255.svg) | 1 | 3.942809 | S03 | 1.356 | 2.026 | **10** (5) | `P1-H` 0.7181 | 3 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0076`](c0_Y0076.svg) | 1 | 3.886746 | S02 | 1.519 | 1.995 | **9** (5) | `P2-H` 0.0523 | 6 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0168`](c0_Y0168.svg) | 1 | 4.000000 | S01 | 1.210 | 1.863 | **10** (5) | `P1-P3` 0.8771 | 4 | — | 0.8771 (`pin core y0`) | clip, T5⁗ DEAD, lane no kill, guard no kill |
| [`c0_Y0169`](c0_Y0169.svg) | 1 | 3.928915 | S38 | 1.256 | 1.891 | **10** (5) | `P2-H` 0.0690 | 6 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |
| [`c0_Y0171`](c0_Y0171.svg) | 1 | 4.000000 | S01 | 1.279 | 1.810 | **9** (5) | `P2-H` 0.1258 | 6 | — | 0.8771 (`pin core y0`) | clip, T5⁗ alive, lane no kill, guard no kill |

## What to look for, per node

* **`k5_11_interior_Y1104`** — pockets < 1: `H->wall x=s` 0.802, `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_11_interior_Y0672`** — pockets < 1: `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_16_interior_Y0083`** — pockets < 1: `P1-H` 0.439, `P0-H` 0.491, `P3-H` 0.660
* **`k5_11_interior_Y0738`** — pockets < 1: `P1-H` 0.123, `P2-H` 0.153, `H->wall x=0` 0.802
* **`k5_11_interior_Y1110`** — pockets < 1: `P1-P2` 0.891, `P3-P4` 0.891, `H->wall x=s` 0.933
* **`k5_11_interior_Y0662`** — pockets < 1: `H->wall y=s` 0.817, `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_11_interior_Y0130`** — pockets < 1: `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_11_interior_Y0275`** — pockets < 1: `P1-H` 0.842, `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_11_interior_Y0308`** — pockets < 1: `H->wall y=s` 0.845, `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_11_interior_Y0985`** — pockets < 1: `H->wall x=s` 0.830, `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_16_interior_Y0027`** — pockets < 1: `P3-H` 0.454, `P4-H` 0.646, `P1-P2` 0.891
* **`k5_16_interior_Y0191`** — pockets < 1: `P1-H` 0.271, `P0-H` 0.316, `P3-H` 0.823
* **`k5_16_interior_Y0275`** — pockets < 1: `P4-H` 0.208, `P1-H` 0.842, `P1-P2` 0.891
* **`k5_16_interior_Y0839`** — pockets < 1: `P3-H` 0.209, `H->wall x=s` 0.799, `P1-P2` 0.891
* **`k5_16_interior_Y0842`** — pockets < 1: `P3-H` 0.433, `P1-H` 0.784, `P1-P2` 0.891
* **`k5_16_interior_Y0881`** — pockets < 1: `P4-H` 0.460, `P3-H` 0.774, `P1-P2` 0.891
* **`k5_16_interior_Y0941`** — pockets < 1: `P1-H` 0.396, `P0-H` 0.714, `P3-H` 0.755
* **`k5_16_interior_Y1056`** — pockets < 1: `P1-H` 0.260, `P2-H` 0.440, `P1-P2` 0.891
* **`k5_16_interior_Y0460`** — pockets < 1: `P3-H` 0.466, `P1-H` 0.585, `P0-H` 0.682
* **`k5_16_interior_Y0249`** — pockets < 1: `P4-H` 0.287, `P3-H` 0.846, `P1-P2` 0.891
* **`k5_16_interior_Y0402`** — pockets < 1: `P1-H` 0.306, `P0-H` 0.411, `P3-H` 0.738
* **`k5_16_interior_Y1117`** — pockets < 1: `P4-H` 0.243, `P1-P2` 0.891, `H->wall x=s` 0.942
* **`k5_16_interior_Y0500`** — pockets < 1: `P4-H` 0.329, `P3-H` 0.839, `P1-P2` 0.891
* **`k5_16_interior_Y0044`** — pockets < 1: `P1-H` 0.306, `P0-H` 0.318, `P3-H` 0.784
* **`k5_11_interior_Y0147`** — pockets < 1: `H->wall y=s` 0.740, `P1-P2` 0.891, `P3-P4` 0.891
* **`k5_11_interior_Y0202`** — pockets < 1: `P3-H` 0.172, `P1-H` 0.551, `P4-H` 0.594
* **`k5_16_interior_Y0054`** — pockets < 1: `P3-H` 0.535, `P1-H` 0.585, `P0-H` 0.628
* **`k5_16_interior_Y0099`** — pockets < 1: `P4-H` 0.230, `P3-H` 0.869, `P1-P2` 0.891
* **`k5_16_interior_Y0230`** — pockets < 1: `P1-H` 0.411, `P0-H` 0.510, `P3-H` 0.728
* **`k5_16_interior_Y0325`** — pockets < 1: `P4-H` 0.466, `P3-H` 0.682, `P1-P2` 0.891
* **`k5_16_interior_Y0380`** — pockets < 1: `P1-H` 0.523, `P3-H` 0.642, `P0-H` 0.649
* **`k5_16_interior_Y0436`** — pockets < 1: `P4-H` 0.335, `P3-H` 0.817, `P1-P2` 0.891
* **`k5_16_interior_Y0491`** — pockets < 1: `P3-H` 0.147, `H->wall x=s` 0.817, `P1-P2` 0.891
* **`k5_16_interior_Y0565`** — pockets < 1: `P3-H` 0.582, `P4-H` 0.592, `P1-P2` 0.891
* **`k5_16_interior_Y0660`** — pockets < 1: `P3-H` 0.216, `P1-H` 0.865, `P1-P2` 0.891
* **`k5_16_interior_Y0719`** — pockets < 1: `P4-H` 0.463, `P3-H` 0.727, `P1-P2` 0.891
* **`k5_16_interior_Y0865`** — pockets < 1: `P3-H` 0.463, `P1-H` 0.645, `P0-H` 0.727
* **`k5_16_interior_Y0991`** — pockets < 1: `P3-H` 0.278, `P1-H` 0.815, `P1-P2` 0.891
* **`k5_16_interior_Y1022`** — pockets < 1: `P3-H` 0.153, `H->wall y=0` 0.799, `P1-P2` 0.891
* **`k5_16_interior_Y1039`** — pockets < 1: `P3-H` 0.442, `P1-H` 0.778, `P1-P2` 0.891
* **`slack0.02_c0_Y0272`** — pockets < 1: `P2-H` 0.209, `H->wall y=s` 0.880, `P1-P3` 0.905
* **`c0_Y0254`** — pockets < 1: `P1-H` 0.683, `P0-H` 0.815, `P1-P3` 0.877; **T5⁗ DEAD**
* **`c0_Y0258`** — pockets < 1: `P2-H` 0.131, `P1-H` 0.780, `P0-H` 0.859
* **`c0_Y0787`** — pockets < 1: `P1-H` 0.130, `P3-H` 0.339, `P2-H` 0.771
* **`c0_Y0939`** — pockets < 1: `P4-H` 0.234, `P1-P3` 0.877, `H->wall x=s` 0.933
* **`c0_Y0942`** — pockets < 1: `P4-H` 0.144, `P1-P3` 0.877, `P2-H` 0.972
* **`c0_Y0959`** — pockets < 1: `H->wall y=s` 0.740, `P1-P3` 0.877
* **`c0_Y1033`** — pockets < 1: `P4-H` 0.079, `H->wall x=s` 0.830, `P1-P3` 0.877
* **`c0_Y1038`** — pockets < 1: `P4-H` 0.105, `H->wall x=s` 0.845, `P1-P3` 0.877
* **`f1_L10_0003`** — pockets < 1: `P1-H` 0.258, `H1->wall y=s` 0.558, `P0-H` 0.646
* **`c0_Y0952`** — pockets < 1: `P4-H` 0.062, `H->wall y=s` 0.740, `P1-P3` 0.877
* **`c0_Y0788`** — pockets < 1: `P1-H` 0.131, `P3-H` 0.339, `P2-H` 0.777
* **`c0_Y0257`** — pockets < 1: `P2-H` 0.127, `P1-H` 0.808, `P0-H` 0.845
* **`c0_Y0878`** — pockets < 1: `P3-H` 0.105, `H->wall y=0` 0.845, `P1-P3` 0.877; guard line `pin core y1` chord sum 3.8684 (rhs 0.0087)
* **`c0_Y0695`** — pockets < 1: `P3-H` 0.361, `P2-H` 0.718, `P0-H` 0.723
* **`c0_Y0255`** — pockets < 1: `P1-H` 0.718, `P0-H` 0.776, `P1-P3` 0.877
* **`c0_Y0076`** — pockets < 1: `P2-H` 0.052, `H->wall x=0` 0.659, `P1-P3` 0.877
* **`c0_Y0168`** — pockets < 1: `P1-P3` 0.877, `H->wall x=0` 0.880, `P0-H` 0.998; **T5⁗ DEAD**
* **`c0_Y0169`** — pockets < 1: `P2-H` 0.069, `H->wall x=0` 0.830, `P1-P3` 0.877
* **`c0_Y0171`** — pockets < 1: `P2-H` 0.126, `H->wall x=0` 0.793, `P1-P3` 0.877

## Files

`review_a57v4.csv` is the review sheet (every automatic column filled, the four `PI_*` columns
empty).  The generator is `attempts/A148-gallery-v4/code/{gallery148,geo148,data148}.py`; the
per-page facts are `attempts/A148-gallery-v4/results/gallery148_a57v4.json`.
