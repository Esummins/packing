---
name: present-problems-spatially
description: "PI's leverage is spatial/physical intuition; present open problems as enumerated classes with exact-geometry examples (SVGs), not as abstractions"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8b20e315-017a-445b-9327-302e5359887a
  modified: 2026-09-05T23:26:32.283Z
---

The PI (recreational mathematician, mech-E background) contributes most where spatial/physical intuition applies â€”
the places the AI is comparatively blind: e.g. "square 6 is a tangency, not a block; 7 can slide right into the corner"
(the 3.985 interlock), the wall-length budget, the corner-crowd taxonomy, the eta-disturbance drain theme.

**Why:** Every breakthrough of the k0 week came from the PI looking at a concrete configuration or a concrete
enumeration of cases and seeing a move or a constraint the certificates and censuses could not express. Abstract
residue statements ("wall-anchored frames", "1e28 objects") produced no traction; pictures and case lists did.

**How to apply:** When reporting remaining problems, residues, or failure modes: (1) enumerate the classes
explicitly (with counts and wall share), (2) give one exact, geometry-checked example per class as an SVG
(docs/residue_map/gen.py and docs/cert_failures/gen.py patterns: every square checked for containment/disjointness/
depth), (3) state per class what drain/lemma exists or is missing, and (4) ask the PI to look at the pictures before
proposing theory. Prefer real corpus configurations over schematic ones. See [[square-packing-n11-lab]].

Addendum 2026-09-07 (PI): when drawing alive placements, draw the example hypothesis square at the CENTRE of the
box and the CENTRE of the tilt window being checked (cyan H, tilt printed). The A107 gallery already did this via
core_squares() (mid-tilt of the core's box); docs/residue_map/gen_a57_lp.py drew only the box outline and now draws
the H square too. Any new drawing generator must follow the same rule.

Addendum 2026-09-07 (PI confusion on l1_153 panel 3): never draw schematic objects (slot-census bins, cover
cells, branch boxes) in the same visual language as bodies. Bins = thin dashed outlines, no fill, labelled
"slot bin: w= n=", with an explicit legend line on the panel; each support column assigned to exactly one bin
(totals must sum to the support weight); the conditioned square's own columns marked (H). Panels 1-2 are the
geometry; panel 3 is a statement, and must look like one.

Addendum 2026-09-07 (PI): inside each hypothesis square draw THREE cores with distinct styles + legend: the stock
axis-aligned core K(a) the LP pruned against, A135's exact axis-aligned core, and the polygon core K'; caption the
half-sides/areas; label impossible columns with which core they clear and which they meet. Pins: stock and exact
pin cores as inner outlines.

Addendum 2026-09-07 (PI on c0_Y0171): a near-packing panel drawn at its own s* > s0 reads as an illegal packing.
Always draw the container at s* with s0's container overlaid dashed, and a large banner when s* > s0 ("NOT
realisable at s0"); rows with s* >= 4 are st4 automatically.

Addendum 2026-09-08 (three PI slot readings refuted by grazers): the next gallery must DRAW, per usable slot and
corner, the witnessed free meeters (the sampled disjoint pair, thin outlines, with their depth into the cell
printed) so that hairline meeters are visible; and print the slot's lane verdict with lane_lb/M next to it.

Addendum 2026-09-08 (Y0275): A148 painted the UNDECIDED band pale green and the PI read it as feasible. Rule:
undecided = light grey stipple, never a green tint; only certified-feasible is green; say so in the legend.

Addendum 2026-09-08 (PI): keep the galleries LIVE — docs/shadows/status_gallery.py (A162) collects every kill
record, moves killed pages to <gallery>/killed/ (git mv, never delete) and writes docs/shadows/STATUS.md (the
checklist + counts + residue-left paragraph). Rerun after every campaign report / at every pause.

Addendum 2026-09-09 (PI, for cascades / multi-box constructions): emit the FULL step-by-step visualisation (one
page per step: known before, forcing applied, boxes after; a final tree of cases with verdicts) and draw each
valid "pin family" BY GEOMETRY as a filled region of admissible centres (tilt window stated) with the forced
box's K' overlaid solid, pose unions thin, guard lines with chords printed, every region labelled with the leaf
that produced it. The PI wants to check the construction against the reading, not just the verdicts.
