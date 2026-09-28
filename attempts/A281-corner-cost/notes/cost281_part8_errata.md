# cost281 part 8 -- what the brief (and one earlier note) had wrong or imprecise

1. **"an F corner and a T corner on one wall: is the bound > s-hat?"** -- NO [T-computed]: both Phi-tau and Pi-tau walls
   have exact 4-square witnesses at 3.82 and at s-hat (margins 0.089 / 0.066 at 3.82; part 7).  The only wall type dead
   on W is Pi-Pi (TWO-POKERS).  The infimum of the Pi-tau wall side is ~3 (part 2).
2. **"the poker's slot is supplied by the adjacent wall meeter -- then that corner is T with a SPECIFIC sense"** -- the
   corner is T, but its sense is NOT forced: exact witnesses with the T-meeter of the opposite global sense (frame tilt
   18.4 deg, margin 0.051) and of the SAME global sense (frame tilt 45.8-46.2 deg, margin 0.005 at 3.82, 0.012 at s-hat)
   both meet the poker's slot at both ends of W (part 7, page (b1)-(b2)).  The row continuation (same tilt) is the
   same-sense case.
3. **Erratum to A248 (`corner_chase.md` header and s.3.3, k0_knowledge s.2.4 TWO-POKERS line):** "on [3.82, s-hat] every
   type-F corner's wall slot is met by an INTERIOR square" holds only when the wall neighbour is type F (the case A248
   analysed: FLAT-ABOVE, TWO-POKERS, TYPE-F-OWN).  With a type-T wall neighbour the T-meeter supplies the poker's slot
   (item 2).  A248's f = 4 corollary is unaffected (all neighbours are F there).
4. **"mixed senses >= 3.9298 [M -> certified by A261 for tilts >= 0.703 deg + the cube [T]]"** -- the certification omits the
   SLAB (one wall's tilt in (0, 0.703 deg) with the others above it), which is [C] (k0_knowledge s.0.5, s.2.5).  So
   ONE-SENSE on W is [T-computed + T + C(slab)].
5. **"a flat toucher against a wall has no wall torque"** -- imprecise: the wall's EDGE pressure has a free resultant point,
   so the wall supplies ANY torque in [-W/2, W/2]; the flat is never torque-limited (part 4, F3.1).
6. **"LEVER: a torque-balanced CONTACT ring needs s > 4"** used for T3 -- A239's LEVER is a statement about TYPE-F crowds
   (flat + tilted, corner-on-edge contact); for T corners the contact is vertex-on-edge between two tilted squares with a
   free lever arm and A239 tags it [C]; the C2 type-T ring even has loop gain 1 (part 5, T3).
7. **Torque via A233 ("every meeter is LOCKED")** -- LOCKED (kinematic: no retreat) does not give LOADED (positive FJ
   multiplier), which every torque statement needs; rattler crowds are locked and unloaded (61/70).  All torque lines are
   [T-cond] on the k >= 1 rows AND on load (part 4).
8. **"the surviving cases are exactly the ring + one poker (f = 0) ... and whatever else remains (f = 1?)"** -- ten of the
   fifteen D4 orbits survive side + count: f = 0 (1), f = 1 (1), f = 2 (4), f = 3 (2), and f = 4 survives the [T] layer,
   dying only with SEPARATE-NOTCHES [M].  Every survivor but the f = 4 pinwheel has a T corner (Lean `hasT_or_pinwheel`,
   `realised_has_T`).  What closes the survivors is ROOM on the hybrid ring, not any count (part 6).
9. **"F2 HOLDERS: one interior holder per F corner on the window (A248)"** -- by the room count an F corner costs 0, 1 or 2
   free squares depending on its two wall types (Phi-Pi wall: 1 at the poker's end; Phi-Phi / Phi-tau / Pi-tau: 0 with ADJ
   supply); in NORMAL FORM it costs one lock per wall that is not a row, and its flat's wall is a row only as a flat row
   (part 3, H-F4).  The statement "one per F corner" is right only for the all-F pinwheel.
10. **"a flat ROW (two flush squares) costs 3.9347 [M->T?]"** -- stays [M]: 3.9347 is the least side of the pinwheel of four
   ROWS with one flat row (A258 `side258`); with locked open pairs elsewhere (hybrid) the flat row's least side is not
   known and was not certified here (part 7 reports the 8-square searches for the orbits with a Phi-Phi wall).
