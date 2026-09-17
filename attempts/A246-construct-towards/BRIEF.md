# A246 -- CONSTRUCT TOWARDS a 12-stuck ring and show it fails below 4 (PI, 2026-09-16 21:30: "is there not a way
# we can try and construct towards a ring, and show that it's not possible with s < 4?").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (any search
detached with a resume block and logs/STOP), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python
process (BelowNormal, affinity 0xFFFF; the k5 frontier, A238, A241, A244's lanes and A245 are running -- never touch
them).  Pages to docs/residue_map/campaigns/A246-construct-towards/.
Read first: attempts/A244-twelve-stuck/{notes/twelve244.md, results/twelve244.md} (12-STUCK four-crowds exist,
282 in the corpus, least certified 4.000022; the descent limit is 4 + c*delta -- the infimum is EXACTLY the trivial
side; nothing below 4 with residual 1.4e-2 at s-hat; [T] CROSS-CORNER-REACH: no square meets a corner box and the
far slot of the same wall once s >= 3 + sqrt2; [M]/[S] a corner is NOT self-sufficient: two disjoint squares cannot
each meet all three cells of one corner to positive depth (O-NO-SELF-SUFFICIENT); one square meets at most 5 of
the 12 cells at s <= s-hat), attempts/A243-reach-root/notes/wall_slot243.md (WALL-SLOT [T], SLOT-MET [S], the
mutual-service inequalities h > s-2-delta, h' > s-2-delta', h + h' <= s - delta - delta'), A239's
notes/rings_below_4.md (reach R(theta, delta); a third wall member juts below 4), pocket_waste.md (TILT-MIN sin
theta <= delta; DEPTH-BUDGET d_A + d_B <= 1), wedged_seal.md, ring_capacity.md (Lemma TWO: side < 2 holds one
square; the band/core count), sideband.md (B0/B0'), corner_seal.md, A244's verify244 (the exact 12-cell test).

## The statement -- pure existence, no locks, no forces
STUCK-EXIST(11): no packing of 11 unit squares at side s < 4 has all 12 border cells (4 corner boxes + 8 wall
slots) doubly met.  A244 measures its infimum at exactly 4, with the obstruction growing like (4 - s).  A proof is
a finite semi-algebraic infeasibility; the PI's route is CONSTRUCTIVE: place the meeters corner by corner and
propagate what the 12-cell constraints force along each wall, until the loop closes and the constraints conflict
for s < 4.  The recent lemmas are exactly the propagation rules:
  (a) per corner: its two meeters supply at most 5 of the corner's 6 incidences (NOT self-sufficient), so every
      corner needs >= 1 incidence from OUTSIDE -- an adjacent corner's wall meeter through the overlapping wall slots
      (mutual service), a third wall member (juts), or an interior square's vertex through a notch;
  (b) per wall: mutual service forces both wall meeters TALL along the wall (reach > s - 2 - delta) and disjoint
      (h + h' <= s - delta - delta'); a jutting third member or an interior supplier costs pocket room;
  (c) per corner again: TILT-MIN and DEPTH-BUDGET bound how deep and how tilted the two meeters can be given
      their reaches; WEDGED-SEAL forbids a meeter on both walls;
  (d) room: the three non-meeter squares must fit in what is left (Lemma TWO on the centre; the notches), and any
      interior supplier of (a) is one of these three.
Compose (a)-(d) around the four corners: the sum of the walls' occupied extents, the corners' depth budgets and
the pocket's capacity must all hold at once; show they cannot for s < 4 (equality structure at s = 4: the grid).

## Task
1. Write the propagation exactly: variables per corner (delta_f, theta_f, delta_w, theta_w) and per wall the
   supplier choice for each of its two slots (mutual / jut / interior / own-tip); for each choice the closed-form
   inequalities from (a)-(d), each PROVED from the cited lemmas (SLOT-MET and NOT-SELF-SUFFICIENT are [S]/[M] --
   prove them or mark the dependence; the along-wall extent cos + sin and the reach R are [T]).
2. Case analysis: enumerate the supplier patterns around the perimeter (mutual on k walls, jut on j, interior on
   i, with i + j bounded by the three free squares and the pocket capacity), and for each pattern derive the
   composed inequality in s.  Target: every pattern forces s >= 4, with equality only at the grid.  Where a pattern
   does not close analytically, reduce it to a bounded search in the few remaining variables and run it
   (rigorous: interval arithmetic or exact rational grid + Lipschitz bound), citing the 1.4e-2 residual at s-hat as
   the margin to certify.
3. Test every inequality on the 282 corpus 12-stuck crowds and the 34 certified candidates (they must satisfy all
   of them, at s >= 4) and on A244's best sub-4 attempts (which inequality is violated, by how much).
4. Say plainly: proved [T] for which patterns, what remains [C], and whether STUCK-EXIST(11) is closed below 4 --
   which with WALL-SLOT and K0-FREE closes k0_00 (no locks, no A233).  n-general: which steps use n = 11 (the
   three free squares) and which are n-free.  Lean: Statements/Open/StuckExist.lean (the theorem or the
   documented axiom + the consequence chain; build + audit, 0 sorry).
5. Deliverables: docs/proofs/construct_towards.md, the Lean file, code/, results/construct246.md (+jsonl), pages
   (the propagation around the perimeter drawn: one corner's forced region, then the next; the tight case),
   registry row, LOG entry, ledger s.4 note.  Report once (<= 20 lines) and EXIT.
