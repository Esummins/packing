# A237 -- POCKET WASTE: the jagged centre pocket of a loaded ring cannot hold n - p squares (PI, 2026-09-16 00:00:
# "given the tilt requirements of the loaded ring, and that they have to have a fairly high angle to all fit, the
# pocket is almost necessarily quite jagged -- use the wastage census on grain boundaries to assert a minimum
# wastage in the centre pocket, then show there isn't room for n - (ring)").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (long runs detached,
resume block), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity
0xFFFF; 5 k5 frontier workers are running), never touch running workers.  Pages to
docs/residue_map/campaigns/A237-pocket-waste/.  Read first: ring_capacity.md (A236: the band/core/straddler COUNT
never closes -- m^2 - 3 >= n for every n with s(n) < m; at n = 11 the count allows 13 squares but A226's region
search finds room for 9; residue POCKET(n): the loaded component's pocket holds < n - p squares), one_flush.md
(ring11: the 8-square crowd ring at S = 3.90-3.99 leaves room for ONE more square), realign.md (A231: WALL-EXCESS
chord form, sealed pocket area tan(phi)/2 between leaning touchers), corner_seal.md + sideband.md (Lemma B0/B0':
the geometry of two squares both meeting an open corner box; Lemma A1), wall_torque.md (ONE-TILTED; TWO-CONTACT),
contact_census.md / grain_flood.md (the lab's wastage / interface census), two_grains.md (TILT-BAND depth), the
193 held four-crowds + A226's crowd rings (their loaded components and pockets), the ring rand_0_0569|t20.

## The route
1. Lemma TILT-MIN (any n, pure geometry): the two meeters of a doubly-met OPEN corner box, interior-disjoint, both
   meeting the box, satisfy a tilt / offset constraint: at least one is tilted (ONE-TILTED), and the tilt of the
   tilted one is bounded BELOW by a function of how far the other reaches into the box (two nearly flush squares
   cannot both meet the box; derive the exact curve from Lemma B0 / B0').  For a LOCKED corner (both meeters
   loaded, PUSH / HOLD) sharpen it: give the minimum tilt theta_min of the tilted meeter(s) and its dependence on
   the corner geometry.  Test on the 193 four-crowds' corners (measured tilts vs the bound).
2. Lemma JAGGED (any n): the centre pocket left by a loaded ring (the loaded component = meeters + wall chains +
   holders, A233's CHAIN) is a polygon whose boundary edges are the ring members' inner edges at tilts >= theta_min
   (or flush segments); classify its boundary features (reflex vertices at leans, tilted edges, flush segments)
   and give a WASTAGE CENSUS for unit squares packed in such a polygon: per tilted boundary edge of length L at
   tilt theta, the unusable strip / triangle area (a unit square cannot approach a tilted edge closer than a
   tilt-dependent margin except near the ends); per reflex vertex, the unusable wedge; per pair of adjacent tilted
   edges, the sealed corner triangle (A231's tan(phi)/2 is the wall version).  Prove each item as an exact
   inequality on the area a packing of unit squares can COVER inside the polygon.
3. Theorem POCKET-CAP: area(pocket) - waste(features) < n - p  =>  the ring is impossible at that side.  At n = 11
   on the window: with p = 8 (+ holders), s <= s-hat, tilts >= theta_min, compute the bound analytically -- does it
   give capacity <= 2 < 3 (A226 found 1)?  If yes, this closes LOCKED-CROWD-FREE(11) analytically (say exactly
   what remains: the extremal route A233 + TILT-MIN + JAGGED + the arithmetic).  Then the n-general form: pocket
   area ~ (s - 2 - 2 iota)^2 vs waste ~ (number of features) x c(theta_min): for which n does the inequality close
   (table n = 5..60), and what is the residue where it does not (say it plainly).
4. Tests: the ring witness and every held four-crowd (their pockets' exact polygons, the census bound vs the true
   packing number found by A226-style search), A226's ring11 pockets at S = 3.90-3.99, and the records (the lemma
   must not fire on cross-braced records -- check what their "pockets" look like).
5. Deliverables: docs/proofs/pocket_waste.md (TILT-MIN, JAGGED, POCKET-CAP with tags, the n = 11 computation, the
   table, the residue), Statements/Open/PocketWaste.lean (the lemmas as documented axioms where prose, the
   consequence theorem chained to A236's / A233's; build + audit, 0 sorry), code/, results/pocket237.md (+jsonl),
   pages (the ring's pocket with its features and unusable regions shaded; the n = 11 window pocket), registry
   row, LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
