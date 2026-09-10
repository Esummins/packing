# A202 -- fast30: the closed-form geometric kill layer (stage 0, <= 30 s per page) -- the lemmas, for any n

The layer is the PI's (2026-09-10 16:35: "placing all of its constraints inside of say a 30 second budget, then
printing svgs so I can view where we're at, before chasing longer steps like full branched trees and lp"), as are the
readings it encodes: the DISC reading (the alive hull of a cell is the complement of the two discs -- radius 1 at H's
hull corner, radius 1/2 at the pin's corner; 16:20), the CORNER reading (a square at cell 16 must clear H by >= 1 in x
and sit above P3; 16:00) and the COLUMN reading (the chord limit on the right wall lets cells 21/22/23 hold ONE centre;
15:20, A201's brief).  Every rule below is a NECESSARY condition on a PIECE = (closed centre rectangle) x (closed tilt
sub-bin) of one unit square of the packing, so a piece that fails it holds no pose of that square; the union of the
surviving pieces is a superset of the true pose set, and everything downstream (unions, caps, the count) is A198 /
A200's Theorem COUNT machinery on that superset.  Tags as in `docs/proofs/forced_corners.md`: [T] proved, [M]
measured.  Code: `attempts/A202-fast30/code/rules202.py` (the rules), `fast30.py` (the pieces and the refinement),
`fast30b.py` (unions, caps, FC, count, H forcing, the certificate), `count202.py` (the count with the pair table),
`stage1_202.py` (A200's exact table on the survivors), `fig202.py` (the page), `run202.py` / `run202.sh`.

## 0. Setting

Page = pins P_1..P_k (axis-aligned, centre within delta_pin of the slot, certified core K_i = [kx-a, kx+a]^2 inside
the pin's square at every pose), the conditioned square H (centre box x tilt window) and n - k - 1 FREE squares;
forced slots p with widened open boxes B_p+ (Theorem FC, at the g1 pad lambda = s0/3.861637 or at pad 0).  A pose
is (c, theta), theta in [0, 90] deg, t = tan(theta/2) in [0, 1]; w(theta) = cos theta + sin theta in [1, sqrt2] is the
square's axis-parallel width, so the square lies in the closed l-inf ball of radius w/2 about c, in the closed disc of
radius 1/sqrt2, and contains the open disc of radius 1/2 (its interior contains every point at distance < 1/2).
Over a tilt sub-bin [t0, t1] the exact endpoint (cos, sin) give w_min, w_max (multibox.Bin, [T] w is concave on
[0, 90]).  Pieces: the half-grid cells of fastprop.make_grid (side (s-1)/ceil((s-1)/0.70) < 1/sqrt2, Lemma A1: one
centre per closed cell) split nsub x nsub, times nbins exact t-sub-bins; survivors refined 2 x 2 x 2 for `depth`
levels under a piece budget (children INHERIT the parent's chord bounds -- sound, a child's poses are the parent's).

## 1. The piece rules (each [T]; `rules202.py`; the disc / box rules in floats from outward-rounded rects with an
explicit margin EPS = 1e-9, the chord rule exact in rationals)

* **P (pins).**  If every point of the rect is at Euclidean distance < 1/2 from the closed core K of one pin, the piece
  is dead.  *Proof.*  The open disc of radius 1/2 about c lies in int Q(c, theta); it meets the closed K, hence (an
  open set meeting the closure of the open core) meets the open core, which lies in int P; so int Q meets int P.
  The distance of a point to a box is convex, so its maximum over the rect is at a corner (4 checks per pin).
* **W (walls).**  If every centre of the piece is closer than w_min/2 to a wall, the piece is dead: the square's
  half-width along that axis is >= w_min/2 (A171's container clip at w_min).
* **C (Lemma CN against H).**  Two interior-disjoint unit squares have centres at Euclidean distance >= 1 (A153,
  residue_ledger s.1: the open inscribed discs of radius 1/2 are disjoint).  A free square is distinct from H, so a
  piece is dead if for EVERY alive piece of H every centre pair is < 1 apart; max distance between two rects is at a
  corner pair.  H's alive pieces are grouped (tilt bin x 2 x 2 cell of H's box) into bboxes: testing against a
  group's bbox is a sound weakening (the max distance to the bbox is >= to any piece inside).  The same rule against
  a further conditioned square H_k's whole box.
* **M (the relative-tilt separating-axis bound against H).**  Interior-disjoint convex polygons admit a separating
  line parallel to an edge of one of them (SAT).  For unit squares F (tilt theta_F) and H (theta_H) with centre
  difference d, the projection half-width of F on an axis of H is w(theta_F - theta_H)/2 and H's own is 1/2 (and
  symmetrically on F's axes), so DISJOINT => some axis a in {u_H, v_H, u_F, v_F} has |d . a| >= r := 1/2 +
  w(theta_F - theta_H)/2 >= 1.  Over a piece pair (rect_F x bin_F, rect_H x bin_H): the relative tilt ranges over
  [a_F - b_H, b_F - a_H] and w is 90-periodic and concave between multiples of 90, so r_lo = 1/2 + w_min/2 is a valid
  lower bound (w_min = 1 when the interval contains a multiple of 90); |d| <= dmax (corner of the difference rect
  D = rect_F - rect_H); and |d . a| <= dmax cos(gap) where gap in [0, 45] is the smallest angular distance modulo 90
  between the directions of D (an angular interval, or everything if D contains the origin) and the axis directions
  of the bin.  If dmax cos(gap_H) < r_lo and dmax cos(gap_F) < r_lo the pair is dead.  With both tilts free (w_min =
  1, gaps 0) this is exactly Lemma CN; it exceeds CN only through the coupling of the tilt with the axes (up to
  r = 1/2 + 1/sqrt2 = 1.207 at 45 deg).  Applied to a free piece against every alive H group (dead iff dead against
  all), and in the count's pair table between two option rows (their hulls x their alive bins).
* **L (the open-chord row).**  Lemma LINE-1 (`docs/proofs/guardline_clause.md`, open chords): on an axis-parallel
  line the open chords of the distinct squares of one packing sum to <= s.  With the pins' exact chords (A144 /
  A190 `guardlines_v5.minchord` on the pin boxes), H's min open chord over its alive pieces and the min open chord of
  the piece (all three distinct squares), a row > s kills the piece.  The guard lines are A198's (y, x = 1/2, 1,
  3/2, s/2, s-3/2, s-1, s-1/2).
* **R (reach).**  A square whose interior meets the open box B_p+ has its centre within 1/sqrt2 (Euclid) of the
  closed box (int Q lies in the open disc of radius 1/sqrt2) and within w_max/2 of it per axis (the l-inf ball);
  a piece violating either for slot p holds no meeter of p.
* **X (A161's exact miss).**  `chordlane.box_misses_cell_exact` on the piece's outward-rounded pose box (A161 / A198:
  every pose of the box gives a square whose interior misses the open widened box) -- closed form (a separating-
  axis minimum over the box), run at the coarse level and at the last refinement level.
* **H's own clip and reach.**  H's pieces die under P and W; a piece of H MAY MEET a slot only if c is within w_max/2
  (l-inf, strict) of the open box (the square lies in that ball) AND A161's exact separating-axis miss test on the
  piece's pose box does not prove every pose misses (rule X on H); H "provably misses" p when no alive piece may
  meet it.  When H is FORCED at a slot set (below) only the pieces that may meet every forced box survive.  H's box
  := the hull of its surviving pieces (never grown).

## 2. What is built on the survivors (A198 / A200, unchanged in substance)

* **Unions and caps.**  U_p = the surviving pieces of slot p (all cells).  cap_p = 1 when U_p's Euclidean diameter
  < 1 (Lemma CN: two anonymous meeters would be two distinct squares with centres in U_p), or its l-inf diameter
  < 1/sqrt2 (Lemma A1), or pins + H + 2 x min open chord over U_p > s on a guard line (LINE-1); cap_p = 0 when U_p
  is empty; cap_p = 1 when only one cell survives (A1).  Theorem FC demands two distinct non-pin meeters of B_p+
  from {H} u {anonymous}: H_p + cap_p < 2 => DEAD; = 2 with H_p => H forced at p.
* **The count (Theorem COUNT, A198 notes/fastprop.md).**  Option rows (cell, S): for a free square, per cell the
  slots with a surviving piece there, closed upward: the joint row (cell, S) has hull = the intersection of the
  per-slot hulls (a pose meeting every slot of S lies in every slot's alive set), alive tilt intervals = the
  overlaps of the per-slot interval lists, chords = the maximum of the per-slot minima -- sound over-approximations;
  for H, per grid cell the pieces meeting the cell, S = the slot sets some piece may meet, the empty set included.
  Pair table (`count202.PairTable`, the sound direction only): rows are compatible unless Lemma A1 (some centre
  pair at l-inf >= 1/sqrt2 is impossible), Lemma CN (max distance of the hulls < 1) or rule M over every pair of
  alive tilt intervals excludes them; chord rows <= s per line; n_free anonymous squares at most one row each,
  pairwise distinct cells (A1); infeasible => DEAD; infeasible with H barred from p => H forced at p.
* **Iteration.**  H forced => H's pieces clipped by the meet test => the H-dependent rules (C, M, L) re-run on the
  surviving pieces => new unions => ... to a fixed point (at most 6 rounds; every round is milliseconds).
* **Verdicts.**  DEAD is `[C: closed-form trace]` -- no verifier clause exists for these rules yet (the certificate
  is the JSON trace: every rule's kills and milliseconds, the unions with their statistics, the caps, the count's
  nodes and the pair exclusions it used); ALIVE = not killed by these tests, with the alive-piece table, the count's
  witness cover (a counting witness, not a packing) and the page.  A kill at the g1 pad is valid on the page's
  window; at pad 0 it is s0-only (WINDOW-PENDING), as for A200.

## 3. Stage 1 (`stage1_202.py`)

A200's `QPage` (A198's exact option table: A171's dead test against every role's K', A161's miss test, depth 5 /
joint 2; the union caps with the refine; Theorem FC; the count; the forcing; multibox re-normalisation) run with
`reach(cell, S)` := empty whenever stage 0 killed the cell for some p in S (sound: every piece of the cell failed a
necessary condition for a meeter of p), and with stage 0's clipped H box as the record's H (sound: the hull of the
poses that may meet the slots H was proved forced at).  Stops after the propagation: SEAL, the pair tests and the LP
are stages 2-3 (A200 / A201).  Verdict label `[C: exact-test trace (A171 / A161 / CN / A1 / chord rows / FC) on
stage 0's alive cells]`.

## 4. Soundness checks run before the population (2026-09-10)

* Fuzz (`scratch fuzz202.py`, 4000 / 3000 random piece pairs and pieces, 200-300 sampled poses each, an exact
  float SAT): every piece pair rule M or C declared dead admitted NO interior-disjoint pose pair (938 dead cases);
  every P-dead piece met the pin core at every sampled pose (236); every R-dead piece missed the open box (1917);
  every may_meet-False piece missed it (1816); every W-dead piece left the container (574).  0 refutations.
* The joint rows' tilt intervals were first intersected as SETS of interval tuples (an artefact when the two slots'
  refinements differ): Y0044 then "died" by the count.  Corrected to interval overlaps; Y0044 is ALIVE at stage 0,
  as A200's exact table says.  Rule kept for readers: a stage-0 kill of a page that A200's exact tests leave alive
  is a bug until proved otherwise.
