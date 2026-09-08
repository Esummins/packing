# A148 — gallery v4: legible pages built around the geometric shortcut question ("can the remaining squares fit in the white space?"), k0 first, A57/A60 from the night's records at 06:00 (Opus, drawing + geometry)

Context (2026-09-07 night). The PI reviewed docs/shadows/k0v3/ and docs/shadows/a57v3/ today and found, by eye,
five geometric kills the code did not have (the Y0036 pin pinch → pin-clip; the Y0186 support columns impossible
under the hypothesis → polygon core; the s3_far corner reachable only by h2 → K′ lane kill; the Y0147 four-chord
line → guard-line rows; the Y0241 pockets and the Y0460 singly-met slot → conditional/slot lane kills). The PI's
brief for the next set: "it's producing a really busy plot, and to my understanding things like the impossible
overlaps shouldn't be possible at all. I do still want most of the info, but there's room to make it more legible,
and add a couple of notes about what the different plots ARE. The main thing I'm looking for is whether there's a
shortcut that can geo-kill the node without running more LP — we need a bunch of those, especially to cut down the
k0 space."

Design (fixed; do not add panels beyond these):
PANEL G — "GEOMETRY: what is still free" (the main panel, largest). The container at s0 with s0 labelled; the pins
as light-blue squares with their EXACT cores as a thin inner outline (one style, no stock core); every conditioned
square H as cyan at box centre and mid-tilt with its polygon core K′ filled (drop the stock and exact axis cores
from the drawing — print their half-sides in the caption only); the FEASIBLE-CENTRE REGION shaded green: the set of
centres c such that SOME tilt gives a unit square Q(c, t) inside the container, interior-disjoint from every pin's
exact core and from K′ of every H (computed on a grid of ≤ 0.02 pitch × 36 tilts, then sampled-confirmed; state
the pitch); pockets narrower than 1 hatched grey with their width printed; the guard lines (A144: the horizontal/
vertical lines through pin edges and K′ extremes whose chord sum is tightest) drawn as thin lines with the chord
sum and RHS printed at the margin when the sum is within 0.15 of s0; each corner and usable slot annotated with its
K′ lane verdict (A141's t2 tables / slot results; else "n/a") in a small tag; the clipped centre box (A131 exact
clip) drawn inside the original box. One-line note under the panel: "green = where another square's centre can
still be; grey = pockets too narrow for any square; tags = how many squares can reach each corner/slot".
PANEL S — "LP support after the exact-core / K′ re-solve" (medium): the dual support of the node's LATEST record —
the exact-core re-solve where one exists (A140 exactcore140 for k0; A137's night records / A145's for A57; A135's
for its 3) — placements by weight (A107 v2 conventions), H's K′ outlined; if the latest record is still the stock
LP, draw it but label the panel "stock LP (pruned against the axis core K(a) — columns overlapping K′ are shown red-
dashed and count as impossible)". Note under the panel: "what the relaxation puts where; overlaps are the
relaxation's slack, not a packing".
PANEL N — "nearest real packing" (small): A107's minimised near-packing or A128's near-packing, container at s* with
s0 overlaid dashed and the banner "s* = … > s0: NOT realisable at s0" / "realisable at s0"; same square names as the
old gallery's right panels (the PI labels from these).
HEADER: node id, class, level, τ/budget/η, the node's family (S01/S02/K01…), the subtree cost (A142's formula), and a
"WHAT TO LOOK FOR" line generated from the geometry: the narrowest pocket, any corner/slot with lane ≤ 1 or NEAR-
MISS, any guard line within 0.15 of s0, the feasible-region area vs (number of remaining squares) × 1, and the
verdict of every geometric leaf already run on the node (clip, T5⁗, lane, conditional lane, guard line) so the
reader never re-derives a kill the code has.
FOOTER: three lines saying what the three panels ARE (fixed text) and the drawing conventions.

## T1 — now: the generator and the k0 set
`gallery148.py` (reuse A140/A142 code for data access; new drawing code), then docs/shadows/k0v4/<cell>.svg for the
eleven remaining converged-alive k0 cells (A140's twelve minus s3_far; if A141's conditional-lane run has killed
more, draw them too with a KILLED banner and the leaf), README.md (one-table summary: cell, level, s*, feasible
area, narrowest pocket, lane tags, leaves run, what to look for), review_k0v4.csv (the PI's columns empty, all
automatic columns filled), docs/shadows.md Part V (append only). Geometry checks as A142's verify142 (independent
implementation); every green region sampled: 10⁴ centres in green each admit a feasible tilt, 10⁴ in the non-green
band admit none (drawn → tested → hits).

## T2 — at 06:00 on 2026-09-08 (one timed wait; no polling loop, no progress messages): the A57/A60 set
docs/shadows/a57v4/: the surviving alive A57 nodes after the night (read A137's records/PAUSED.md v3 draft state and
attempts/A57-shadow-trees/results/*.jsonl at 06:00 — read-only; A137 pauses at 07:00, so draw from the records as
they stand and say the timestamp), ranked by A142's subtree cost, top 40 + the A60 top 20 after A142's clip kills,
Panel S from the exact-core re-emission records where A137 produced them. README, review_a57v4.csv, Part V addendum.
Push by 07:15.

Constraints: drawing and geometry only, no LP; ≤ 2 processes BelowNormal (A137 owns the LP slots tonight; A136/
A141/A144/A145/A146 may still be running — count the box, stay under 16 python processes); READ-ONLY on every
campaign and attempt (new files only under attempts/A148-gallery-v4/ and docs/shadows/{k0v4,a57v4}/; docs/shadows.md
append only); NO recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths with
explicit pathspecs; registry row, LOG.md. Report ONCE at the end (after T2): the k0 README table first, the A57 top-10
second, pointers last. No interim messages.
