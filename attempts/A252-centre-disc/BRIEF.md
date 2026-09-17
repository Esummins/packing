# A252 -- finish CENTRE-DISC: the inscribed disc of a family-stuck ring's pocket has radius < 1/sqrt3 on the window,
# so the pocket holds <= 2 squares (A251's new route, 2026-09-17 20:00).
Fable. LAUNCH-AND-EXIT -- NEVER wait for a detached run (launch with a resume block and logs/STOP, report from what
is finished, exit).  Ops: short responses, files <= 250 lines, no monitors, explicit-pathspec commits,
PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF; the k5 frontier, A238, A241, A244
lanes, A247 triples, A249's finisher, A250's lanes and A251's ladder are running -- never touch them).  Pages to
docs/residue_map/campaigns/A252-centre-disc/.
Read first: docs/proofs/ring_pocket.md (A251: the all-ADJ ring family as a 17-coordinate box; Lemma GAP; box-valid
PIERCE priced out at 5e14 CPU-h; the disc route: INRADIUS [T] -- the centres of interior-disjoint unit squares are
>= 1 apart; THREE-DISC [T] -- three points pairwise >= 1 apart inside a region force an inscribed disc of radius
>= 1/sqrt3 = 0.57735; hence CENTRE-DISC (inscribed radius < 1/sqrt3) => capacity <= 2 (Lean
capacity_le_two_of_centre_disc); Lemma MID-NOTCH [T]: a radius-1/2 disc in a wall's middle notch needs
g(theta) + g(theta') < 2(4 - s) with g(t) = (1 + sin t)/cos t - 2 sin t, min 0.72355 at 26.261 deg, so dead for
every s > 3.27645, robust form dead for s > 3.80342; [C] the CORNER WEDGE (only a one-sided bound so far) and the
VERTEX SECTORS -- the two remaining places a large disc could sit), type_t_chase.md (A249: the ring family,
T-CELLS, the ring at s-hat, its pocket pilot: PIERCE(1)), family250.md (FAMILY-STUCK; at s >= 4 a theorem; the
non-ring / mixed type-F structures that remain -- A249 s.3.4), corner_chase.md (A248: TWO-POKERS for type-F
corners), pocket_waste.md (WEDGE lemma r(alpha), sealed regions), wedged_seal.md, Lemma TWO (ring_capacity.md).

## The statement to finish
CENTRE-DISC(11): for every packing structure of the family-stuck ring family on [3.82, 4) (eight tilted wall
touchers, all-ADJ, T-CELLS), every disc inside the pocket (container minus the eight touchers) has radius <
1/sqrt3.  Then capacity <= 2 and 8 + 2 < 11: no family-stuck 11-packing of the ring family below 4.  A251 killed the
disc in the wall's middle notch (MID-NOTCH); what remains is a disc touching the corner region -- the WEDGE between
a corner's two touchers -- and a disc in a VERTEX SECTOR (around a toucher's inner vertex).  Reduce the disc's
possible centres to those regions (a maximal inscribed disc touches >= 3 boundary pieces: walls / toucher edges /
toucher vertices), enumerate the contact triples, and bound the radius in each case by a closed-form inequality in
the touchers' (theta, delta) and s, using WEDGED-SEAL, T-CELLS, the mutual-service inequalities and Lemma GAP.

## Task
1. Lemma CONTACT-TRIPLES: a maximal disc in the pocket touches three boundary elements; list the types (edge-edge-
   edge, edge-edge-vertex, ...) that can occur for the ring family (walls are NOT boundary of the pocket's interior
   part that matters? -- decide: the pocket includes the wall bands' free parts; a disc touching a wall is bounded
   by MID-NOTCH / the corner wedge).  Prove the list is complete.
2. Lemma CORNER-WEDGE: the largest disc in the wedge between a corner's floor toucher and wall toucher (both
   meeting c00, tilts theta_A, theta_B, offsets) has radius r_c(theta_A, theta_B, delta_A, delta_B) -- closed form
   from the wedge angle and the touchers' inner edges; show r_c < 1/sqrt3 on the family's box (interval or exact
   minimisation over the 4 corner parameters + s; certified), or find the exact sub-box where it fails.
3. Lemma VERTEX-SECTOR: a disc touching a toucher's inner vertex and two other elements; bound its radius by the
   distance between adjacent touchers' inner vertices (Lemma GAP + the extents) -- closed form; certify on the box.
4. Combine: CENTRE-DISC(11) [T] or the exact remaining case (drawn: the ring, the pocket, the maximal disc and its
   three contacts).  Cross-check on A249's exact ring at s-hat and the ladder rings (results of A251's run251
   if landed: joint ring + k free squares, max |q - O|): the true inscribed radius vs the bound.
5. Then the NON-RING structures (A249 s.3.4 / A250): list them exactly; for each say whether CENTRE-DISC's
   argument applies (the pocket is bounded by the same eight touchers plus the free squares serving slots) or what
   replaces it; if a structure escapes, draw it.
6. Say plainly whether FAMILY-STUCK-EXIST(11) is now closed on [3.82, 4) (with A248's TWO-POKERS for type-F
   corners and A250's theorem at s >= 4) -- then k0_00 closes via FamilyStuck.lean's chain with no locks -- or the
   exact remaining obligation.  Lean: Statements/Open/CentreDisc.lean (CORNER-WEDGE / VERTEX-SECTOR as theorems
   where the square's set description suffices, else documented axioms; the consequence chain; build + audit, 0
   sorry).  Deliverables: docs/proofs/centre_disc.md, the Lean file, code/, results/disc252.md (+jsonl,
   certificates), pages, registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
