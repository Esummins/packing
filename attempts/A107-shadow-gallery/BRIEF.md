# A107 — the shadow gallery: draw the LP output at every fertile node and hand the PI the contact graphs (Opus chore, read-only)

Context (2026-09-06). The PI read A57's LP dual support directly ("grab any phase-space point near the dead end of the
LP search — it is definitionally close to the solution being approached; draw it, overlaps and all") and identified
the whole residue of the fertile k5_11 lineage in one look: a k7 packing (BL L-shape 3 + BR stacked 2 + TL 1 + TR 1)
plus a four-square pinwheel at one tilt, side minimum 3.886746 = ŝ + 0.0097 (docs/residue_map/pinwheel_k7_shadow.svg,
gen_pinwheel_k7.py, pinwheel_tilt_curve.svg). The picture gave the mechanism (f1 on the top wall is the binding
constraint; f0/f2 a mirror pair; f3 a strut wedged at exactly width 1) and the reason the tree is slow there (the
0.0097 slack lives in the three-square core; the tree conditions on the loose square). Do the same for every fertile
node the lab has, so the PI can hand back the contact graphs to drain toward.

Read first: docs/residue_map/gen_a57_lp.py (draws a node's LP dual support: pins from the cert hypotheses' cores, the
conditioned box, placements as squares with opacity = dual weight, hue = tilt; prints pairwise SAT gaps), docs/residue_map/
gen_pinwheel_k7.py + gen_pinwheel_k7_svg.py (direct side minimisation of a named contact structure: slot squares fixed
as functions of s, free squares (cx, cy, θ) + s as variables, SLSQP with restarts seeded from the LP support; contact
graph in the naming language: slot squares BL(i,j)/BR/TR/TL, free squares f0..fn), docs/residue_map/gen_pinwheel_tilt.py
(side minimum vs common tilt), docs/residue_map/a57_lp_support.svg, docs/residue_map.md §1 (the layers), attempts/A57-
shadow-trees/results/tree/**/<node>.json (the LP results: 'packing' = dual support with weights y, 'hyp' cores, 'tau',
'budget', 'atoms_all'), attempts/A96-a57-parametric/ (probe outputs, alive lists), attempts/A106-shadow-diameter/ (read
its report if landed: shadows, s*, Hessians — do not duplicate its minimisations, reuse them).

## T1 — the gallery (one entry per DISTINCT shadow, not per node)
Inputs: every ALIVE-at-LP node at every level in A57 (k5_11 and k5_16, all shards, levels 1–4) and — if their LP
results exist on disk in the same format — the alive/resister nodes of A60 (trump5 cover/slackcore), A61 (window
stragglers) and the k0_00 level-1 ALIVE cells of A85/A99. For each node: load the LP dual support; if it is integral
(weights 1), it is a near-packing; if fractional, split into its integral components (group placements that are
pairwise disjoint into candidate packings). De-duplicate shadows across nodes: two supports are the same shadow if,
after mapping the class's symmetry (the stabiliser of the pin set in D4), their placements match within 0.05 in
position and 3° in tilt. Expect a handful of distinct shadows per class.
For each distinct shadow: (a) the drawing (gen_a57_lp.py conventions, plus the snapped version: placements within 0.05
of a slot cell and 3° of axis snapped to the slot and named); (b) the direct side minimisation with the snapped slot
squares fixed and the rest free (gen_pinwheel_k7.py; ≥ 100 restarts incl. the LP seed): s*, s* − ŝ, the free squares'
poses, and whether the free squares share one tilt; (c) the contact graph at s* in the naming language (pairs + walls,
with vertex-on-edge vs flush marked); (d) the tilt-sweep curve (gen_pinwheel_tilt.py) if the free squares share a tilt;
(e) the list of alive nodes this shadow explains (node ids, levels, their box) and its multiplicity; (f) the exact
k-class of the shadow (its simple squares) and the class the alive nodes belong to — state plainly "a k_m packing at
s* sitting on the boundary of class X".
Write docs/shadows.md: a table (shadow id, class, k of the shadow, s*, s* − ŝ, #alive nodes explained, levels) and one
section per shadow with the SVGs, the contact graph, and the mechanism if it is readable from the contacts (which
contact is binding: report the active constraints with nonzero multipliers from the SLSQP solution). Order the sections
by #alive nodes explained, descending. Also list alive nodes NOT explained by any integral shadow (fractional-only).

## T2 — the drain hint per shadow
For each shadow, state what the PI can act on: the load-bearing subgraph (squares whose removal leaves s* unchanged
are rattlers/struts: test by removing each free square and re-minimising), the binding contact, and the flat
directions (rank of the incidence Jacobian with vertex-on-edge constraints — NOT finite differences of SAT gaps, which
lie at flush/opposite contacts; check second order at exactly-opposite point contacts, as the PI corrected on f3).

Constraints: READ-ONLY on every campaign (A57/A60/A61/A85/A96/A99/A104/A105/A106 files and processes untouched; copy
what you need); ≤ 1 process, BLAS-pinned (OMP/MKL/OPENBLAS 1), SLSQP runs are seconds each — wall cap 3 h; headroom
> 6 GB commit and > 3 GB free physical; frozen verifiers untouched; git = fetch + plain merge + push own paths (no
rebase/autostash/reset). Every drawn square geometry-checked (containment; overlaps allowed only in the raw LP panel
and reported as numbers). Writes: attempts/A107-shadow-gallery/{code,results,notes,logs}, docs/shadows.md +
docs/shadows/*.svg, registry row, LOG.md, one-line note on the A57 depgraph node (owner A107). Report ONCE: the table
first, the unexplained-alive count second, pointers last. No interim messages.
