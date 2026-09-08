# A148 — method: what the v4 page computes, and why each claim is sound

## 1. The design, and what changed from v3

The PI's brief: *"it's producing a really busy plot, and to my understanding things like the
impossible overlaps shouldn't be possible at all. I do still want most of the info, but there's room
to make it more legible, and add a couple of notes about what the different plots ARE. The main
thing I'm looking for is whether there's a shortcut that can geo-kill the node without running more
LP."*

Three changes carry that:

1. **Reading order.** The geometry panel is the largest and is first; the LP panel is demoted to
   medium and captioned as a *relaxation*, so the overlaps read as slack rather than as a claim
   about squares; the packing panel is small and exists for the names.
2. **One style per object.** v3 drew three cores inside every H (stock axis, exact axis, polygon).
   v4 draws **one** — the polygon core K'(B), filled — and captions the two half-sides. Bodies are
   filled, cores are filled purple or outlined, schematic regions (centre boxes, the clip, lane
   cells, guard lines) are thin dashed and never filled. The footer says this in four lines.
3. **The question is answered on the drawing.** The feasible-centre region is the new object: the
   set of centres where one further unit square can still go. It is shaded green, its area is
   printed, and it feeds the disk bound below.

## 2. The feasible-centre region, and why GREEN and WHITE are both certified

    R = { c : SOME tilt t gives Q(c,t) inside [0,s0]^2 and interior-disjoint from every
              pin's exact core and from K'(B) of every conditioned square }

Define

    clearance(c,t) = min( container clearance of the centre ,  min_j ( - depth( K_j , Q(c,t) ) ) )

`clearance > 0` is exactly feasibility. Two Lipschitz facts:

* moving the centre by `d` moves every point of `Q` by `d`, and SAT depth between convex sets is
  1-Lipschitz in Hausdorff distance, so `|clearance(c,t) - clearance(c',t)| <= |c - c'|`;
* rotating a unit square about its centre by `δ` moves every boundary point by at most `(√2/2)δ`
  (the circumradius), so `|clearance(c,t) - clearance(c,t')| <= (√2/2)|t - t'|`.

On a grid of pitch `p` and `n` tilts sampled at the midpoints of `[0,90°)` (the square's tilt is
90°-periodic, so this covers everything), with

    m  =  p·√2/2  +  (√2/2)·(Δθ/2),      Δθ = (π/2)/n

a cell is called

* **GREEN** iff `max_k clearance(cell centre, t_k) >= +m` — then *every* point of the cell admits a
  feasible tilt, so green is a certified **inner** approximation of `R`;
* **BLOCKED (white)** iff `max_k clearance(cell centre, t_k) < -m` — then *no* point of the cell
  admits *any* tilt, so white is a certified **outer** approximation of the complement;
* **UNDECIDED (pale)** otherwise: the band the resolution cannot decide.

At `p = 0.01998` and `n = 36`, `m = 0.02956`.

*Drawn → tested → hits.* Per page, 10⁴ centres drawn uniformly inside the green cells must each
admit a feasible tilt and 10⁴ drawn inside the blocked cells must admit none, tested at 360 tilts
(ten times denser) with an independent SAT. Over the eleven k0 pages: 110 000 + 110 000 draws,
**0 hits on either side**. `verify148.py` repeats both with a completely different overlap
predicate (edge crossing + strict point-in-polygon; no separating axis anywhere in that file).

## 3. The disk bound — the shortcut

A unit square contains the disk of radius 1/2 about its centre. So for the `budget` squares the node
still has to place:

* their half-unit disks are pairwise disjoint (the squares are interior-disjoint);
* those disks lie inside the container (the squares do);
* every centre lies in `R`, hence in `GREEN ∪ UNDECIDED`.

Therefore the disks are disjoint subsets of `(GREEN ∪ UNDECIDED) ⊕ B(1/2) ∩ [0,s0]²`, and

    budget  <=  area( (GREEN ∪ UNDECIDED) ⊕ B(1/2) ∩ [0,s0]^2 )  /  (π/4).

The dilation is computed as a shift-OR of the cell mask by a disk of radius `ceil(0.5/p)+1` cells,
i.e. **outward**, so the area is an over-estimate and the bound stays sound. `n_max < budget` is a
geometric kill needing no LP and no certificate machinery beyond the K' vertices.

On the eleven k0 cells `n_max` is 17–18 against a budget of 10: one conditioned square in an
otherwise empty container leaves far too much room. The bound is worth its place because the A57 and
A60 nodes carry five pins *and* a conditioned square, where the free centre region is a fraction of
the container.

## 4. Pockets, guard lines, lane tags, clip

* **Pockets** — exact convex-polygon distance (segment-to-segment, so an upper bound as well as a
  lower one, which a SAT gap is not) between every pair of certified cores and from each core to
  each wall. A gap `< 1` is a pocket no further unit square fits into; it is hatched grey and the
  width is printed. On ten of the eleven k0 cells the narrowest is `H -> wall x=s`.
* **Guard lines** — A144's ≤ 40-line family (pin core edges and midlines, K' extremes and mid, the
  `k/8·s` grid), each evaluated exactly: `rhs(l) = s0 - Σ_j minchord(box_j, l)`, and the **chord
  sum** `s0 - rhs(l)` is what the hypothesis squares alone are guaranteed to occupy on `l`. Lines
  with `rhs <= 0.15` (chord sum within 0.15 of s0) are drawn solid red and labelled at the margin;
  `rhs < 0` is an outright contradiction. `verify148.py` re-runs A144's own sampled confirmation
  (10⁴ poses per box per line: the true chord must be ≥ the minchord) — 330 000 draws, 0 hits.
* **Lane tags** — A141's K' lane verdicts (`t2_table.json` for k0 corners, `t4_slots.jsonl` and
  `t2_a5760_s*.jsonl` for the A57/A60 slots), drawn as a small tag on the corner/slot cell; `n/a`
  where A141 has no row.
* **Clip** — A131's exact pin clip at the A135 exact pin core, 8 tilt sub-bins, drawn orange inside
  the black centre box. **`k0_00` has no pins, so on every k0 page the clip is vacuous** and the page
  says so rather than drawing a fake shrink.

## 5. Provenance and read-only discipline

Data access reuses A140's `cells140` and A142's `gallery142` loaders verbatim; the geometry uses
A132 `polycore`, A135 `exactcore`, A131 `pinclip`, A144 `guardline`; the subtree cost is A142's
`C(L) = pL·850 + pA·(300 + 8·C(L+1))`, residual `8·C(L+1)·kept8`, read out of
`population142.json`. All drawing code is new. Nothing outside `attempts/A148-gallery-v4/`,
`docs/shadows/{k0v4,a57v4}/` and the appended `docs/shadows.md` Part V is written.
