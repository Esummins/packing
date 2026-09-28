# cost281 part 5 -- class T: T1 SIDE, T2 HOLDERS, T3 TORQUE

**T1 SIDE.**  [T] A T-meeter of frame tilt th and offset d (A249) reaches d + w(th) along its wall and excludes only
d + min(cos th, sin th) (part 1, EXT-tau); two T corners on one wall bound nothing on W (TWO-TILTED [F] as a bound,
mutual pair +0.078 at 3.82 [T-computed]).  At the ring level: a pinwheel of four common-tilt ROWS of two (the normal
ring, family D) has least side 1 + sec phi + cos phi + sin phi + tan(phi/2) [T, A258] (-> 3 as phi -> 0: on all of W,
tilts in (0, ~28 deg) at s-hat).  SIDE(tau, tau) per wall in closed form for a row of sense + and tilt phi:
    s = a + b + sec phi + cos phi + sin phi,   a, b < 1,   a sin phi + b cos phi >= 1 at each corner (D4);
for a locked open pair  s = a + b + sec phi_1 + w(phi_1) + e  with the open gap e > 0 (<= 0.349 with ADJ, <= 1.169
without [M], A263).  Mixed senses: with per-wall tilts + + + - exists from 3.9298 [M]; on W the mixed pinwheels of rows
are excluded by A261's 50/50 closed-LP certificates (tilts >= 0.703 deg) [T-computed] + the near-flat cube (all tilts
<= 0.703 deg) [T] + the slab jobs (one wall's tilt in (0, 0.703 deg)) [C] -- so "the four T corners are ONE-SENSE on W"
is [T-computed + T + C(slab)], not [T].  The brief's "certified by A261 for tilts >= 0.703 deg + the cube [T]" omits
the slab [C].

**T2 HOLDERS.**  [T] The bare one-sense ring of rows is never family-stuck: every one of its 12 cells has exactly two
ring meeters, and the ring family (4 boxes + one slot per wall) has |M| = 8 = |Pi| (A258 "the ninth square"), so a
ninth square meets a box (a third meeter) or both slots of one wall (a RIBBON poker; necessary a + sec phi +
cos phi tan(phi/2) > s - 2 and a + sec phi - sin phi tan(phi/2) < 2 [T]).  [T-computed per ring / M] the seated poker
realises it, must be HELD (P4) and nothing fits beside it.  So **four T corners as rows cost ONE free square in total**
(the ribbon poker), and ROOM [T-computed on D' and the common-tilt hybrid; T-computed* with 20 P2 cells open for
independent tilts] says every free square contains O: capacity 1, 8 + 1 = 9 < 11.  With r locked walls (hybrid D^h)
the cost is r locks + the ninth square (a lock in a ribbon may be it): the count needs r + [ninth] <= 3 -- true for
r <= 2, and for r = 3 iff a lock is the ninth -- and closes nothing; ROOM on D^h closes it (A260, common tilt).
**T2' [T] per corner, any packing:** each slot of a T corner needs a non-own meeter (the domino), the two distinct (the
triple); ADJ supply <= 1 per slot (TWO-FAR) and only by the wall neighbour's shared-wall meeter (T-SLOTS) -- so a T corner
with no ADJ supply costs 2 free squares, with one costs 1, mutual ADJ on both walls costs 0 (A249 s.3.2).

**T3 TORQUE [T-cond].**  A239's LEVER ("a torque-balanced contact ring needs s > 4") is a statement about TYPE-F crowds
(flat + tilted, the TILT-MIN contact structure); for T corners the corner contact is vertex-on-edge between two TILTED
squares with a FREE lever arm, and A239 tags the T case [C].  The GEAR loop gain is not an obstruction either: A249's
C2 all-ADJ ring alternates frame tilts 14.56 / 75.44 deg round the loop, cot . cot = 1.  What is known: [M] the free FJ
LP is infeasible on every ring below 4 the lab built (12 rings, A239 s.2) -- the contacts carry NOTHING, the missing
rows are anti-aligning torques on the tilted meeters and corner-ward along-wall forces -- and RING 193/193 above 4
(A219); [T] RADIAL / CHAIN (a loaded arm is held by a net corner-ward push from outside; the loaded component reaches a
far wall) is satisfied by the walls themselves.  So the torque balance of a LOADED one-sense ring needs, as far as is
PROVED, zero interior contacts (CHAIN is met by the ring) and, as far as is MEASURED, >= 1 interior holder that no ring
below 4 has room for.  T3 adds nothing to T2 as a theorem: where T2 gives "one free square, and it is the whole
pocket", T3 gives [M] "at least one loaded interior square" -- the same square.  (A233: the arm structure decides
LOCKED only; locked 2-crowds exist at the optimum -- Trump's TL -- so no per-corner torque statement can close.)
