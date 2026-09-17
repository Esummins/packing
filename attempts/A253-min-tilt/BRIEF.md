# A253 -- the MINIMUM-TILT ring: the smallest tilt of the all-ADJ ring that still admits the ninth square in the
# slot-overlap ribbon, and the room in its pocket (PI, 2026-09-18 01:00: "what's the smallest tilt angle the ring
# squares can possibly have that still allows the ninth square to meet the overlap band? ... once you have the
# minimum tilt angle possible in order to maximize the pocket size, you'll be able to run LP on the pocket geometry
# and find that it can't fit more than 1 (maybe two) squares").
Opus. LAUNCH-AND-EXIT -- NEVER wait for a detached run.  Ops: short responses, files <= 250 lines, no monitors,
explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes (BelowNormal, affinity 0xFFFF;
the k5 frontier, A238, A241, A244 lanes, A247 triples, A249 finisher, A250 lanes, A251 ladder and A252's ladder are
running -- never touch them).  Pages to docs/residue_map/campaigns/A253-min-tilt/.
Read first: docs/proofs/centre_disc.md (A252: disc criteria are too weak -- a half-disc fits in the flat-limit corner
notch but no unit square does; the pocket bound needs SQUARE room; the coordinator's addendum verified: the
family-stuck ring structure is RING + POKER with the poker's corner in a wall's slot-overlap ribbon [0,1] x
[s-2, 2], poker margin +0.00166 on A249's exact ring at s-hat, and with the poker in place the residual centre set
is EMPTY -> capacity 1 -> 8 + 1 = 9 < 11; remaining obligation RING-POKER-RESIDUAL(11): over the family the
residual set beside the poker has diameter < 1 / holds no unit square), attempts/A251-ring-pocket/code/family251.py
(the 17-coordinate ring family, poses_of(x, s), ring margins), attempts/A252-centre-disc/code (the poker fit, the
residual centre set, adv252), attempts/A249-type-t-chase (the ring at s-hat, T-CELLS), A226/A237 region-search and
PIERCE code (exact capacity of a pocket), ring_swap.md (CELLS: the 16 eight-cell families the bare ring fails).

## The PI's programme
(a) Every ring square must be tilted enough for the ninth square to poke into the ribbon; below the minimum tilt
the ring's touchers close the ribbon and the ring teleports (CELLS on the 16 families).  (b) The minimum-tilt ring
has the LARGEST pocket, so it is the extremal case for room.  (c) At that ring, the pocket holds <= 1 (maybe 2)
squares -> 8 + 1 (or 2) < 11.  (d) The PI also conjectures this common-tilt ring is the ONLY structure below 4 that
doubly meets all four corners without a trivial slot decomposition -- record as Conjecture ONLY-RING [C] and say
what A249 s.3.4 / A250's ILP say about non-ring structures (do not claim it).

## Task
1. THETA_MIN(s): for s in {3.82, 3.85, s-hat, 3.92, 3.95, 3.99}: the smallest tilt such that the all-ADJ ring
   family (family251) admits a ninth unit square, interior-disjoint from the eight, inside the container, whose
   interior meets the ribbon [0,1] x [s-2, 2] (or a D4 image) -- (i) with a COMMON tilt theta for all eight, (ii)
   minimising the MAXIMUM tilt over the eight (non-uniform).  Bisection on theta with the ring/poker margin
   maximised over the deltas and the poker pose (A251/A252 optimisers, many restarts); certify the found rings and
   pokers exactly (interval or rational, as verify244 / A252 do).  Report theta_min(s) for (i) and (ii), the ring
   and poker at each, and the reason the ribbon closes below it (which toucher blocks: draw it).
2. ROOM at theta_min: for each theta_min ring + poker, compute the pocket's exact capacity (region search for 1, 2,
   3 further squares; PIERCE certificate where it decides; the residual set beside the poker) -- the PI expects
   <= 1.  Also at a few larger tilts (theta_min + 5, + 10 deg, and A249's 14.6 deg ring) to test (b): is the
   pocket's room monotone decreasing in the tilt?  If yes on the samples, state Conjecture MONOTONE-ROOM and what
   a proof would need; if not, show the non-monotone case.
3. The certificate shape: if room is monotone in tilt and theta_min(s) is monotone in s, RING-POKER-RESIDUAL(11)
   reduces to a ONE-parameter (or two-parameter) family: certify capacity <= 2 along theta = theta_min(s) over the
   window by interval arithmetic (cheap), plus the monotonicity lemma [C].  Do the one-parameter certificate;
   state the lemma.
4. Deliverables: code (mintilt253.py, room253.py, cert253.py), results/mintilt253.md (+jsonl: theta_min table,
   rings, pokers, capacities), notes/mintilt253.md (the programme, what is certified, the monotonicity lemma,
   ONLY-RING as [C] with the A249/A250 facts), pages (the min-tilt ring at s-hat with the poker and the pocket; the
   blocking toucher just below theta_min; capacity vs tilt), registry row, LOG entry, ledger s.4 note.  Report
   once (<= 15 lines) and EXIT.
