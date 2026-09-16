# A239 -- rings strictly below side 4 and the gear lemma: intuition pages + Lemma WEDGED-SEAL (PI, 2026-09-16
# 11:00, "thoughts from the shower").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF; k5 frontier workers and
A238 are running -- never touch them).  Pages to docs/residue_map/campaigns/A239-rings-below-4/, drawn under the
lab's rules: exact geometry, every panel with a note saying what it IS and the time per step, hypothesis outlines
only at admissible poses, undecided grey stipple never green, forces as arrows (blue wall, black square-square),
torque signs as arcs, the pocket polygon shaded, sealed triangles hatched.
Read first: corner_seal.md (A199: Lemma SEAL, Lemma WEDGE, Corollary SIDES, Lemma NO-SECOND -- the existing
"no second meeter" statements and their hypotheses), k0_count.md + attempts/A218-k0-count (PUSH, HOLD, the ring
rand_0_0569|t20 and its load-path page ring_loadpath_rand_0_0569_t20.svg -- the drawing style to reuse),
wall_torque.md (RING; the along-wall deficit; Lemma W torque signs; TWO-CONTACT), local_lock.md (RADIAL / CHAIN:
the loaded component reaches a far wall; the PI's gear rule as a theorem: a loaded arm is held in from outside),
one_flush.md + attempts/A226-one-flush/results/ring11_226.jsonl (A226's 8-square crowd rings at S = 3.90 / 3.95 /
3.99, key 'ring'; found3 false: room for ONE more square), ring_capacity.md, pocket_waste.md (TILT-MIN binds upward;
the window pocket page n11_window.svg), two_grains.md (the click), A217's stress code (stress217.analyse: the FJ
multiplier LP on a given contact structure, the deficit rows).

## Thought 1 -- Lemma WEDGED-SEAL (PI): "take a square and push it into the corner so two of its corners touch the
## two adjacent walls: no second meeter of the corner box is geometrically permitted, for any rotation"
State and prove (any n): a unit square with one vertex on each of the two walls of a corner (tilt theta in (0, 90)
deg) leaves the open corner box [0,1)^2 met by no other square.  Sketch: with b = cos theta, l = sin theta the
square's near edge cuts the corner off (a SEALED triangle of area bl/2, enclosed by the walls and the edge), its far
vertices sit at x = b + l >= 1 and y = b + l >= 1, and the only uncovered parts of the box are the two WEDGES between
each wall and the adjacent edge, with apex angles theta and 90 - theta, each bounded by a wall and a unit edge; a
unit square cannot place a vertex inside a wedge of angle < 90 deg without one of its two edges crossing the wall or
the bounding edge (do the crossing calculation with the SEGMENT, not the line, and handle small theta).  Relate it
to A199's WEDGE / NO-SECOND (is it a corollary of NO-SECOND?  If so say so and cite; if not, it is new).  Consequence:
in a doubly-met open corner neither meeter touches both walls -- one touches at most the floor, the other at most
the wall (PUSH's setting), and a corner meeter touching both walls is ALONE (so K0-FREE teleports it).  Lean:
Statements/Open/WedgedSeal.lean (theorem if the wedge argument formalises in a few lines from the square's set
description, else a documented axiom); build + audit, 0 sorry.

## Thought 2 -- rings strictly below 4, and how they meet the gear lemma
"When you built the ring witnesses they kept coming in at s > 4; when you limit s < 4 you have to either put the
squares along a side at a fairly high tilt to get enough reach (or waste a lot of the corner), or use a fourth
square that juts into the middle, which affects the pocket.  Since 4 is the trivial packing we only care about
s < 4.  How does such a ring interact with the gear lemma?"  Build the pictures, exactly:
1. The REACH constraint along a wall at side s < 4: two corner crowds (each meeter inside its corner box, WEDGED-SEAL
   forbids touching both walls) plus k wall-chain squares in contact must span the wall in COMPRESSION: give the
   along-wall reach of a tilted square (cos + sin, and the chord 1/max(cos, sin) of A231) and the inequality that
   forces either high tilts (k = 0: two meeters per wall must bridge s - 2 x intrusion) or a third / fourth member
   that juts inward (k >= 1).  Panel A: the tilt-vs-reach curve with the s = 3.88 / 3.95 / 3.99 thresholds marked.
2. Panel B: A226's 8-square crowd ring at S = 3.90 (key 'ring'): the eight meeters drawn exactly, tilts labelled,
   sealed corner triangles hatched, the centre pocket shaded with its exact polygon and the ONE square that fits
   (grey, schematic); Panel C: the same at S = 3.99.
3. Panel D: the JUTTING variant -- construct (with A226's ring builder or by hand, exactly) a ring at S = 3.95 with
   a third member on two opposite walls jutting inward (pattern 3 2 3 2), the pocket it leaves, how many squares
   fit (region search, A222/A226 code).
4. GEAR LEMMA on each ring (Panels B, C, D): run the FJ multiplier LP with the ring's contact structure fixed (A217
   stress217.analyse on the free problem, no tilt floor, no crowd rows): report feasibility; draw PUSH at each
   corner (the meeters pushing each other out along their walls), the holder chains along the walls (compression
   arrows), Lemma W's aligning torque on every tilted wall square (arc), and where the chain cannot close: the
   deficit rows (A219: an anti-aligning torque or an along-wall force toward the corner from OUTSIDE the ring --
   RADIAL/CHAIN) drawn in red at the squares that need them.  Say in the panel note what the gear lemma says about
   this ring: which square would turn or slide, in which sense, if the missing force is not supplied, and what an
   interior square would have to do to supply it (and whether the pocket has room for that square).
5. Panel E: the CLICK / SWAP of one corner on the S = 3.90 ring (A231's improvement) -- the ring after one corner is
   settled and the fixed-tilt shrink: the side it reaches.
Deliverables: the page(s) (2-3 SVGs, <= 6 panels each, geometry checks printed per panel), docs/proofs/
wedged_seal.md (Thought 1), notes/rings_below_4.md (Thought 2: the reach inequality, the LP results per ring, what
the gear lemma forces, n-general where possible, tags), the Lean file, code/, results (jsonl), registry row, LOG
entry.  Report once (<= 15 lines: WEDGED-SEAL status, the reach inequality, the LP verdicts and the deficit per
ring, the page paths) and EXIT.
