# The k0 residue gallery v4 (11 converged-alive k0_00 cells)

One page per node, in the **v4 three-panel form**.  Every page answers the same question first —
*can the remaining squares fit in the white space?* — and only then shows the LP.

| panel | what it is |
|---|---|
| **G — GEOMETRY: what is still free** (largest) | the container at s0, the hypothesis squares with their certified cores, and the **feasible-centre region**: the set of centres where one further unit square can still be placed at SOME tilt, interior-disjoint from every pin's exact core and from K'(B) of every conditioned square.  **Green = certified free; grey STIPPLE = undecided (clearance within the Lipschitz margin) and NOT feasible; white = certified blocked.**  Pockets narrower than 1 are a separate object, hatched with grey DIAGONAL lines and the width printed; A144 guard lines are drawn thin with their chord sum and rhs; each corner/slot carries A141's K' lane verdict with BOTH bounds (`ub` certified, `lb` sampled) and `M`, plus the WITNESSED free meeters from A157's screen and A141's two-crowd witness drawn as thin black outlines with how far each reaches into the cell; A131's exact pin-clip is the orange box inside the black centre box.  **Nothing in panel G comes from an LP.** |
| **S — the LP support** (medium) | the dual support of the node's latest record, fill = dual weight on one sequential scale (A107 v2), the certified cores outlined, and every column whose square overlaps a core drawn **red dashed**: those are impossible under the hypothesis, and each is labelled with whether it ALSO overlaps an exact pin core (pin geometry alone excludes it, inside the frozen certificate schema) or only K'(B) (which needs the polygon-core clause).  The squares here overlap each other — that is the relaxation's slack, not a packing. |
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
`attempts/A148-gallery-v4/results/verify148_k0v4.json`.

**The disk bound — the shortcut this gallery is for.**  A unit square contains the disk of radius
1/2 about its centre, so the centres of the `budget` remaining squares carry pairwise disjoint
half-unit disks inside the container, and each centre lies in (green ∪ undecided).  Hence

>  `budget  ≤  area( (green ∪ undecided) ⊕ B(1/2)  ∩  [0,s0]² ) / (π/4)`

which is a **sound upper bound on how many more squares the node can hold, read straight off the
drawing**.  `n_max < budget` is a geometric kill with no LP at all.  The column is in the table.

**Population.**  A140's twelve converged-alive `k0_00` cells minus `s3_far_BL389484_TR018470`, which A141's K' lane leaf killed on BL (`attempts/A141-polycore-lane/results/polycore_lane_kills.jsonl`).  A141's conditional-lane run (T5) closed no further cell of the eleven, so no page here carries a KILLED banner.

## The table

| node | level | s\* of panel N | family | green area | green+undec. | disk bound n\_max (budget) | narrowest pocket | pockets < 1 | lane tags (hot) | tightest guard rhs | leaves run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [`l1_071`](l1_071.svg) | 1 | 4.000000 | K01 | 4.547 | 5.618 | **18** (10) | `H->wall x=s` 1.0193 | 0 | — | 2.8771 (`K' xmid`) | clip vacuous, T5⁗ alive, lane no kill, guard no kill |
| [`l1_104`](l1_104.svg) | 1 | 3.914214 | K04 | 4.743 | 5.687 | **17** (10) | `H->wall x=s` 0.8280 | 1 | — | 2.7224 (`K' xmid`) | clip vacuous, T5⁗ alive, lane no kill, guard no kill |
| [`l1_124`](l1_124.svg) | 1 | 3.942810 | none | 4.843 | 5.634 | **17** (10) | `H->wall x=s` 0.8565 | 2 | `TR(0,0)` NEAR-MISS (LANE ub 1, lb 1, M 1?) | 2.8418 (`K' xmid`) | clip vacuous, T5⁗ alive, lane near-miss, guard no kill |
| [`l1_148`](l1_148.svg) | 1 | 4.000000 | K01 | 4.806 | 5.753 | **17** (10) | `H->wall x=s` 0.7517 | 1 | — | 2.8418 (`K' xmid`) | clip vacuous, T5⁗ alive, lane no kill, guard no kill |
| [`l1_153`](l1_153.svg) | 1 | 3.877084 | none | 4.877 | 5.690 | **17** (10) | `H->wall x=s` 0.7232 | 2 | `TR(0,0)` NEAR-MISS (LANE ub 1, lb 1, M 1?) | 2.7224 (`K' xmid`) | clip vacuous, T5⁗ alive, lane near-miss, guard no kill |
| [`l1_158`](l1_158.svg) | 1 | 3.902674 | none | 5.012 | 5.755 | **17** (10) | `H->wall x=s` 0.7232 | 2 | `TR(0,0)` NEAR-MISS (LANE ub 1, lb 0, M 1) | 2.7224 (`K' xmid`) | clip vacuous, T5⁗ alive, lane near-miss, guard no kill |
| [`l1_159`](l1_159.svg) | 1 | 3.886745 | K06 | 5.011 | 5.746 | **17** (10) | `H->wall x=s` 0.7232 | 2 | `TR(0,0)` NEAR-MISS (LANE ub 1, lb 0, M 1) | 2.7224 (`K' xmid`) | clip vacuous, T5⁗ alive, lane near-miss, guard no kill |
| [`l2_p114_001`](l2_p114_001.svg) | 2 | 3.924402 | K20 | 4.422 | 5.302 | **17** (10) | `H->wall x=s` 0.8682 | 2 | `TR(0,0)` NEAR-MISS (LANE ub 1, lb 1, M 1?) | 2.8685 (`K' xmid`) | clip vacuous, T5⁗ alive, lane near-miss, guard no kill |
| [`l2_p65_101`](l2_p65_101.svg) | 2 | 4.000000 | K01 | 4.283 | 5.278 | **18** (10) | `H->wall x=s` 0.9669 | 1 | — | 2.8771 (`K' xmid`) | clip vacuous, T5⁗ alive, lane no kill, guard no kill |
| [`l2_p65_111`](l2_p65_111.svg) | 2 | 3.925149 | K03 | 4.294 | 5.285 | **18** (10) | `H->wall x=s` 0.9669 | 1 | — | 2.8771 (`K' xmid`) | clip vacuous, T5⁗ alive, lane no kill, guard no kill |
| [`l2_p74_001`](l2_p74_001.svg) | 2 | 3.912232 | K05 | 4.273 | 5.295 | **17** (10) | `H->wall x=s` 0.8784 | 1 | — | 2.6166 (`K' xmid`) | clip vacuous, T5⁗ alive, lane no kill, guard no kill |

## What to look for, per node

* **`l1_071`** — nothing free: no pocket under 1, no lane ≤ 1, no tight guard line, disk bound 18 ≥ budget 10
* **`l1_104`** — pockets < 1: `H->wall x=s` 0.828
* **`l1_124`** — pockets < 1: `H->wall x=s` 0.857, `H->wall y=s` 0.857; lane: `TR(0,0)` NEAR-MISS (LANE ub 1, lb 1, M 1?)
* **`l1_148`** — pockets < 1: `H->wall x=s` 0.752
* **`l1_153`** — pockets < 1: `H->wall x=s` 0.723, `H->wall y=s` 0.933; lane: `TR(0,0)` NEAR-MISS (LANE ub 1, lb 1, M 1?)
* **`l1_158`** — pockets < 1: `H->wall x=s` 0.723, `H->wall y=s` 0.828; lane: `TR(0,0)` NEAR-MISS (LANE ub 1, lb 0, M 1)
* **`l1_159`** — pockets < 1: `H->wall x=s` 0.723, `H->wall y=s` 0.828; lane: `TR(0,0)` NEAR-MISS (LANE ub 1, lb 0, M 1)
* **`l2_p114_001`** — pockets < 1: `H->wall x=s` 0.868, `H->wall y=s` 0.973; lane: `TR(0,0)` NEAR-MISS (LANE ub 1, lb 1, M 1?)
* **`l2_p65_101`** — pockets < 1: `H->wall x=s` 0.967
* **`l2_p65_111`** — pockets < 1: `H->wall x=s` 0.967
* **`l2_p74_001`** — pockets < 1: `H->wall x=s` 0.878

## Files

`review_k0v4.csv` is the review sheet (every automatic column filled, the four `PI_*` columns
empty).  The generator is `attempts/A148-gallery-v4/code/{gallery148,geo148,data148}.py`; the
per-page facts are `attempts/A148-gallery-v4/results/gallery148_k0v4.json`.

## Status: killed pages and the checklist

*Maintained by `docs/shadows/status_gallery.py` (A162) — this section is regenerated, do not
hand-edit it.*

* **`../STATUS.md` is the checklist** — page, node, class, level, family, status, killing leaf,
  attempt, date and A142 subtree cost for every page of every gallery, with the alive/dead counts
  per gallery, by family and by leaf, and the "residue left" paragraph. **Read it first.**
* **A page whose node is now DEAD lives in [`killed/`](killed/)**, moved there with `git mv` —
  never deleted. A page still in this directory is ALIVE as of the last run, and the links in the
  tables above are repointed to `killed/` when a page moves.
* **The tables above are the frozen A148 build-time state.** Where they disagree with `STATUS.md`
  — including the "no node in this set is killed" lines, which are statements about the *drawing*,
  not about the campaign records — **`STATUS.md` wins.**
* Regenerate with `python docs/shadows/status_gallery.py` (`--dry-run` prints the plan and writes
  nothing). It solves no LP; it only reads existing kill records, and it writes nothing outside
  `docs/shadows/`.
