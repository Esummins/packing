# A236 -- RING-CAPACITY: a stable ring needs side strictly above the grid (PI, 2026-09-15 21:00: "show that the
# minimal side required to build a stable ring requires a side length strictly greater than the trivial packing
# at ceil(sqrt n)").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (long runs detached,
resume block), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity
0xFFFF), never touch running workers.  Pages to docs/residue_map/campaigns/A236-ring-capacity/.  Read first:
local_lock.md (A233: at the Psi-minimal optimum nothing retreats, so every meeter of a doubly-met corner is LOCKED
= loaded; residue LOCKED-CROWD-FREE(n); RADIAL / CHAIN: the loaded component reaches a far wall), two_grains.md
(FOUR-WALL <=> STUCK-4; the ring family's side 4.1099 -> 4.0000 as it clicks flush), one_flush.md (A226: ring11 --
the 8-square crowd ring at S = 3.90-3.99 leaves room for ONE further square, not three; CROWD-ABOVE = rattler
crowds, NOT stable rings), realign.md (A231: WALL-EXCESS in chord form: a wall's touchers have disjoint chords
1/max(cos, sin) >= 1 at height 1/sqrt2, sum <= s; sealed pocket area tan(phi)/2), wall_torque.md (RING), the
witness data (the 193 held four-crowds; the ring rand_0_0569|t20), the survey records (survey226).

## The statement, in the lab's terms
"Stable ring" = the loaded structure of a fully locked four-crowd (all eight corner meeters loaded, hence at the
Psi-minimal optimum by A233): a closed load path around the perimeter, possibly anchored by interior holders.
Conjecture RING-CAPACITY(n): every such structure of n unit squares has side >= ceil(sqrt n).  With A233 this is
exactly LOCKED-CROWD-FREE(n), i.e. ONE-FLUSH(n) in value form -- the PI's idea is the missing residue phrased as a
side bound on rings, and it is TRUE on the ring family (side > 4 for every tilt > 0, limit 4 flush) and on A226's
ring11 probe (no 11th-square room below 4).  Rattler crowds are excluded by "stable" (they are unloaded) and are
handled by A233's extremal choice, so the two together would give the theorem.

## The route to test: CAPACITY, not force
A locked ring occupies the perimeter: its meeters sit in the four corner boxes and its wall chains lie within a
BAND along each wall; the tilted members INTRUDE into the interior beyond the flush band.  The interior region left
for the other n - p squares (p = ring members) is then a region of side <= s - 2 - 2*iota with iota the intrusion,
and its capacity (by area, and better by the packing number of the region's inscribed square) must be >= n - p.
For n with s(n) < m = ceil(sqrt n) we have (m-1)^2 < n; so the inequality (s - 2 - 2 iota)^2 >= n - p with s < m
bounds p from below, while the perimeter can hold at most ~ 4 s / (chord >= 1) members.  Make this exact:
1. Lemma BAND (any n): in a locked ring every wall chain member touches its wall or a member that does (define the
   chain from RADIAL / CHAIN), so the chain lies within distance sqrt2 of the wall; the meeters intrude at least
   iota(theta) = (cos theta + sin theta) - 1 beyond the unit band (compute exactly from the meeter's pose in the
   corner box: the inner extent of a square meeting the corner box).
2. Lemma INTERIOR: the free interior is inside a square of side s - 2 - 2 iota_min (or the exact polygon); its
   capacity is <= floor((s-2-2iota)^2) by area and <= N(s - 2 - 2 iota) by the packing numbers where known.
3. The inequality: perimeter members p <= P(s) (from WALL-EXCESS chords and the corner boxes) and n - p <=
   capacity; combine with (m-1)^2 < n and s < m: for which n does it contradict?  Tabulate n = 5..60 with the
   record sides; at n = 11 say whether it closes ANALYTICALLY (not via A226's search).  If it closes only for a
   finite set of n, state the n-general residue exactly (what extra structure a large-n ring would need).
4. Test every step on the ring witness and the 193 held four-crowds (their p, iota, interior capacity vs n - p),
   and on the survey records (they are NOT rings: check the lemma does not fire on them).
5. Deliverables: docs/proofs/ring_capacity.md (statement, lemmas with tags, the table, the residue),
   Statements/Open/RingCapacity.lean (the conjecture as a documented axiom + ONE-FLUSH(n) from it and A233's
   theorem; build + audit, 0 sorry), code/, results/capacity236.md (+jsonl), pages (the ring with its band, the
   intrusion and the interior polygon; the n = 11 case), registry row, LOG entry, ledger s.4 note.  Report once
   (<= 20 lines) and EXIT.
