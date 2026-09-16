# A234 -- counting HANDEDNESS across the container (PI, 2026-09-15 19:00): "the fact that we need 'not all four at
# once' plus the gear lemma is why I was thinking of counting handedness across the container, since a convex shape
# can't provide a net torque; that would allow Trump et al. (one or more non-simple corners) AND extend up in n."
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF), never touch running workers.
Pages to docs/residue_map/campaigns/A234-handedness/.  Read first: local_lock.md (A233: the residue is GLOBAL --
"not all four load paths can end in locks at once"; Lemma RADIAL / CHAIN / NO-SELF-STRESS: a loaded arm is held in by
a corner-ward push from outside, RING is a theorem for all n and excludes nothing; Trump's TL is a locked doubly-met
corner), two_grains.md (TORQUE-ID: self-torques + wall-force circulation = 0, "not an obstruction"), torque.md (A217:
Lemma W -- a wall torques a tilted square toward its alignment, sign -chi; C1 the signed sum over the 8 meeters FAILS
at Trump's TL; C2/C3 are identities; total_wall_torque measured per witness), wall_torque.md (A219: RING's deficit is
an anti-aligning torque on the tilted meeters or an along-wall force), k0_count.md, A217's stress data
(torque217.jsonl: per square W, tau_wall, tau_contact, chi; per witness wall_pressure / wall_moment /
total_wall_torque), A226's record coordinates (survey226), Trump / S02 / S07 exact packings.

## The identity and what a count must add
Walls are convex and frictionless: every external force is a wall normal.  At any FJ point, summing each square's
torque balance about the container centre O and cancelling the internal pairs gives TORQUE-ID:
   sum_i tau_i^wall (self-torque of square i's wall forces about its own centre, sign -chi_i by Lemma W)
   = - sum_walls (first moment of that wall's pressure about the wall's midpoint, in the rotational sense) =: -C.
The PI's proposal: read this as a HANDEDNESS COUNT -- the aligning self-torques carry the tilt handedness chi_i of
every wall-touching tilted square, and C is the wall pressure's circulation, bounded by the pressure and the side.
A four-crowd concentrates wall pressure at the eight meeters (two per wall, at the wall's ends); an optimum with
<= 3 doubly-met corners has a flush corner square carrying pressure with NO self-torque.  The count to find is a
NECESSARY inequality on (chi_i, N_i, d_i, positions) that every optimum with a flush corner can satisfy (Trump,
S02, S07, every survey record) and no four-crowd can -- n never appears in it.

## Task
1. State TORQUE-ID exactly (global and PER WALL: each wall's own identity if one exists; and about each CORNER: the
   arm's self-torques vs the arm's wall moments about the corner point -- signs of floor vs wall contributions).
   Prove them (they are Newton; Lean if the FJ predicate allows, else prose [T]).
2. PROBE: on every witness with stress data (the 193 four-crowds, the 883 genuine FJ points, Trump, S02, S07, and
   the survey records where a stress can be computed) tabulate per square chi, N, d, tau^wall; per wall the
   pressure, its first moment, the handedness mix of its tilted touchers; per corner the arm sums.  Then SEARCH
   for a separating inequality: which combination is bounded on all <= 3-crowd optima and violated on all
   four-crowds?  Candidates: (a) per wall, the tilted touchers' aligning torques must cancel up to the wall's
   circulation, so each wall with two crowded ends carries BOTH handednesses with weights -- count the sign
   changes around the perimeter (a closed ring forces an even number of handedness flips; flips cost what?);
   (b) the meeters' anti-aligning torque demand (A219's deficit) vs the supply from along-wall holders, summed
   around the perimeter; (c) the circulation bound |C| <= (pressure) x (half-side) against the self-torque sum of
   eight tilted meeters each >= N_i d_i(theta_i).  Report every candidate with its value on Trump and on the ring.
3. If a candidate separates: prove it n-general as a theorem about FJ points with all four corner boxes doubly met
   (then the k-maximal / Psi-minimal minimiser of A233 has a corner that is not locked -> ONE-FLUSH(n)); Lean
   Statements/Open/Handedness.lean (documented axiom + the consequence), build + audit, 0 sorry.  If none does,
   say exactly which quantity Trump and the ring share that defeats the count.
4. Deliverables: docs/proofs/handedness.md, results/hand234.md (+jsonl), pages (the ring and Trump with chi and
   the wall pressures drawn; the perimeter handedness map), registry row, LOG entry, ledger s.4 note.  Report
   once (<= 20 lines) and EXIT.
