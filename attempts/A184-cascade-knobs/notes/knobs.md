# A184 -- the cascade's knobs: three experiments on l1_104 (Fable lead, 2026-09-09)

Labels: [T] proved, [S] routine given cited items, [M] measured / computed, [F] finding, [C] open.
Numbers: `results/knobs184.json` (every number below), side files `results/nodes184_S1.jsonl`,
`results/nodes184_s{0,1}of2.jsonl` (one line per node: roles, kept, vol, timings, rows),
`results/waste184.jsonl` (+ `results/masks/*.npz`), `results/lp184.jsonl`, `certs/`.  Pages:
`docs/residue_map/knobs184_E1.svg`, `_E2.svg`, `_E3.svg`.

## 0. The sample and the construction [M]

Six S1 chains of l1_104 that A183 had recorded through S2: `root/D0`, `root/D1`, `root/D3`,
`root/D7`, `root/D53`, `root/D55`.  Per chain up to 3 A183-ALIVE S boxes (the tree's S2 children,
A168's clipped S pieces -- a sound subset of the cover box) and 4 B boxes, the same four indices on
every chain (23, 69, 112, 154 of the complete (H, D)-cover of the BR right band built at the chain's
coarse-only S1 node: 180 open boxes, 54 lonely (R3), A141's prefix code -- since the coarse-only S1
roles are WEAKER obstacles than any descendant's, every open box of that cover is a valid hypothesis
box for every experiment [T]); the chosen boxes are the open, non-lonely ones holding the centre of
an A168-ALIVE S3 child, evenly spaced.  16 S boxes, 24 B boxes, 64 final {H, D, S, B} hypotheses
per (order, setting), every one built by A183's own child construction (`common184.make_child` =
`polyclip175.make_node` at nsub 4 / refine 2, then `renorm183.make_node_83` on a survivor when the
setting is 8/3; the inherited roles ARE the parent's recorded fixed point -- A183's seeding by
construction), with the A169 leaves (R3 lonely, R1 cells) tested on the new box first.  The S1
level reproduces A183's records exactly (root/D0: D 0.448 at 4/2, 0.332 at 8/3; root/D1: 0.086 /
0.059) [M].  Timing per node: the library clip (`poly_normalise`) and the tail (outward rounding,
roles168 K' rebuild, invariant, OVL, rows) separately, the 4/2 pass and the 8/3 pass separately.


## 1. E1 -- coarse-only versus A183's 4/2-then-8/3 [M]

**Verdicts.**  S2: 16/16 ALIVE at both settings.  S3: coarse-only 61/64 ALIVE (3 EmptyBox), A183's
setting 60/64 (4 EmptyBox) -- node by node 60 ALIVE/ALIVE, 3 DEAD/DEAD, ONE verdict changed:
`root/D53/S5 + B23` is ALIVE at 4/2 (kept H 0.171 / D 0.003 / S 0.002 / B 0.012) and dies at the
8/3 pass (EmptyBox(H)); every other kill (B23 on the chains root/D0/S7, root/D1/S8, root/D55/S5)
happens at 4/2 in both settings.  **Answer to the PI: the 8/3 pass changed 1 of 64 S3 verdicts
(1.6 %) and 0 of 16 S2 verdicts; what it changes is the kept volume** -- vol1 at 8/3 over vol1 at
4/2 is 0.66 / 0.61 / 0.55 (H / D / S) at S2 and 0.69 / 0.68 / 0.63 / 0.64 (H / D / S / B) at S3,
i.e. the fine pass removes a further third to a half of the surviving pose volume.  Mean kept at
S3: coarse H 0.348 / D 0.058 / S 0.079 / B 0.359, fine 0.284 / 0.046 / 0.065 / 0.300.

**Wall.**  Per node (mean, all nodes): S1 14 s vs 51 s; S2 25.1 s vs 128.5 s; S3 41.7 s vs 263.9 s
-- the fine setting is 5.1x / 6.3x the coarse one at S2 / S3.  Where the fine node's time goes at
S3: 4/2 clip 39 s + 4/2 tail 12 s, 8/3 clip 129 s + 8/3 tail 84 s -- the TAIL (outward rounding,
roles168's per-piece K' rebuild, invariant, OVL) is a third of the fine node, because the 8/3
survivors carry 4-8x the pieces.  Totals on the sample: S2 402 s vs 2,055 s; S3 2,672 s vs 16,892 s.

**The PI's conjecture ("coarse on more squares conditions more than fine on fewer") on volumes
[F]:** the 4th square at 4/2 (S2 -> S3, coarse) shrinks the vol1 of H / D / S by 8 % / 8 % / 15 %;
the 8/3 pass on the same three squares shrinks them by 34 % / 39 % / 45 %.  On VERDICTS neither does
much at S3 (3 kills from the 4th square, +1 from the fine pass, of 64) -- the cascade's kills at
this depth come from the specific B box (index 23, the box nearest H under the right wall), not
from the grain.

## 2. E2 -- D -> B -> S versus D -> S -> B at 4/2 [M]

**Alive at the third step: 61/64 in BOTH orders, the same 61 (verdict pairs 61 ALIVE/ALIVE, 3
DEAD/DEAD, none differing).**  Intermediate step: (H, D, B) 24/24 ALIVE (mean kept H 0.831 / D 0.117 /
B 0.490; 31.6 s per node) against (H, D, S) 16/16 ALIVE (H 0.378 / D 0.063 / S 0.093; 25.1 s).  No
intermediate node dies in either order, so no sub-cover is saved by either.

**Kept per role at the final node -- the order matters, in the OPPOSITE direction to the reading:**
vol1(D,B,S) / vol1(D,S,B) = 1.52 (H) / 1.55 (D) / 1.94 (S) / 0.97 (B): D -> S -> B leaves a fixed
point a third to a half SMALLER on H, D and S, and the same on B.  Mean kept at the final node:
D,S,B H 0.348 / D 0.058 / S 0.079 / B 0.359; D,B,S H 0.381 / D 0.064 / S 0.092 / B 0.353.  The
mechanism [F]: a role is bisected (refine 2, tautologous) at every node it passes through, so the
role added LAST is the coarsest at the final node -- S added last (D,B,S) has half the resolution it
has when added at S2, and a coarser S clips H and D less.  The order sets the GRAIN per role, and
the TR pair {D, S} is what conditions H; B (0.35 kept either way) is nearly indifferent.

**Wall.**  Both steps on the sample: D,S,B 402 + 2,672 = 3,074 s; D,B,S 757 + 2,626 = 3,383 s
(the (H, D, B) intermediate has 24 nodes against 16 -- the B cover fans out more than the S cover,
so putting B first costs more intermediate nodes with no kill to show for it).

**Stranded area (E3's certified U) after each step:** see section 3 (`knobs184.json` E2.*.stranded_U).
The B node does strand more: |U| after (H, D, B) has mean 1.37 (max 1.82, 45 % of B0) against
%%S2U%% after (H, D, S) -- the reading "B strands a lot, S does not" is RIGHT as a statement about
area; it is not a statement about kills, and the final nodes of both orders reach the same U up to
the raster.

**Verdict on the PI's question: no -- B before S is not better.**  Same kills, larger fixed points
on H / D / S, 10 % more wall.  The order that conditions H hardest puts BOTH TR meeters before B.

## 4. E2 -- why both orders are complete covers [T]

A step at a node is A141's deterministic prefix-code cover of the NEW square's window (the TR meeter
window for S, the BR right band for B) with the node's roles as obstacles: every leaf is discharged by
`container` (no pose of the box inside [0, s0]^2), `misses_cell` (A161 exact: no pose meets the corner
cell), or a role-aware `witness` (a rational point in every pose of the box AND of every piece of the
named role -- the box's square would BE that role), or kept open; Kraft sum 1, replayed by the checker.
Every discharge is monotone in the obstacle set: fewer or weaker obstacles discharge fewer boxes, so
the open set of the cover at a node with roles R' ⊆ R (or the same roles with larger pieces) is a
superset cover of the one at R.  Hence (i) the B cover built at the (H, D) node is a complete cover of
the BR right band for the D -> B -> S order, and it remains a complete cover for every descendant
(H, D, S) node of the D -> S -> B order; (ii) the S cover built at the (H, D) node (the tree's S2
cover) is complete for the D -> S -> B order and remains complete at every (H, D, B) node of the other
order.  The labelling prune (S = the TR meeter with the SMALLER centre x: boxes entirely right of D's
bbox are excluded) and the A169 leaves R3 (lonely) and R1 (cells against the first meeter D) are
statements about the new square and D alone, so they hold in either order.  The final hypothesis set
{H, D, S_i, B_j} is therefore the SAME set in both orders; what the order changes is (a) which
intermediate nodes die (and take their whole sub-cover with them without computation), (b) the
seeding of the final nodes (the parent's fixed point), hence the computed final fixed point and its
wall, (c) the stranded area after the intermediate step.  The sample compares the two orders on
identical final hypotheses (`c|S3|X|k` and `b|S3|X|k`).

## 5. E3 -- what is certified, and what the LP can consume [T]

**(b) Leaf WASTE at a cascade node.**  A164's construction with obstacles = the roles' K' polygons
(certified inside every surviving pose, A172) and covers = the union of the roles' poses over their
surviving pieces, merged per tilt sub-bin into a bounding rect (a SUPERSET of the poses: the
complement stays an inner approximation of U).  A free square is admissible iff inside the container
and interior-disjoint from every K' (a square other than the role is disjoint from the role's square,
hence from K' ⊆ it).  U_b = points in no role cover and in no admissible free square; the raster
claims a cell only when no admissible pose MEETS the closed cell (A164's Lipschitz margins).  Every
one of the eleven squares of a packing consistent with the node lies inside its own coverable set,
interiors disjoint, so 11 <= s0^2 - |U_b|: |U_b| > s0^2 - 11 = 4.03178 kills the node LP-free.

**(a) The corner rule.**  The PI's "corner box minus the two meeter roles' poses" is NOT sound by
itself: K0-BLOCKED gives AT LEAST two distinct meeters of the widened box, and three unit squares can
meet it (the axis-aligned [0,1]^2, [1,2]x[0,1], [0,1]x[1,2] all meet (0, 1+w)^2 pairwise disjointly)
[F].  What the corner lemma certifies is A169 Lemma A2: two interior-disjoint meeters of the open
widened box have centres in DIFFERENT cells of the 2x2 grid at c = 1 + w.  So a THIRD meeter X (a
free square covering a point of the corner box) has its centre in a cell different from D's and from
S's whenever that role's surviving pieces lie in one cell.  U_a(corner) = the widened box minus every
role's cover minus the free cover computed with those centre cells EXCLUDED (the exclusion shrunk by
the raster slack: outward-sound).  The NAIVE number (box minus the meeter roles' covers only) is
reported as what the reading would give -- it is an upper bound on any sound corner charge, not a
certified area.  [C] The lonely poses (R3) could also be excluded from the free meeter's centres
inside the corner box; not done here.

**(c) The kill** is |U_b ∪ U_a(TR) ∪ U_a(BR)| > s0^2 - 11.

**(d) The LP forms.**  The case-LP (A13/A57 `caselp`) is min mu(total) over atomic measures with
mu(Q) >= 1 for every admissible non-exempt placement Q; tau < budget = 11 - #roles kills.  U cannot
enter it as "forbidden area for the atoms": an atom in U is inside no admissible free placement, so it
adds mass and covers nothing; and the Lebesgue measure on the coverable set is a feasible measure of
total s0^2 - |U| - sum |K'|, which kills only when |U| > s0^2 - 11 + sum_r (1 - |K'_r|) -- weaker
than Leaf WASTE itself (the roles' squares are charged their whole unit area against the smaller K').
The area argument and the measure LP do not compose beyond Lemma ID [T].  What U CAN feed the LP is
a NO-FAMILY: Z = {c : dist(c, U) <= 1/2} -- a unit square with centre in Z contains a point of U (the
inscribed disc of radius 1/2), and U is a set NO square of the packing contains a point of, so no
square of the packing has its centre in Z, at any tilt.  That is exactly the frozen verifier's
`hypotheses.nofams` clause (zone x t-intervals, bridge "no square of the packing lies in a NO-family"),
so the ZONE form is certifiable by `verify_case.py` (sha 521cb01f...) as it stands: nofams =
Z written as rects (inner: the U cells dilated by floor(h/p) - 1 cells, h = 1/(2 sqrt 2)),
t-interval [0, 1].  The zone drops the rows Q that contain a point of U -- rows the v1 core
exemption keeps (Q meets K' but not the grown square core).  The POLY form ("the roles' pieces as
exemptions": drop Q when it meets K'(role) by more than EPS_CORE) is the superset of both -- a Q
meeting U meets some K' or leaves the container -- and has NO clause under the frozen verifier: it
needs v4's `hypotheses.poly_cores = [{vertices: [[x, y], ...]}]` with the exemption "Q meets the
closed convex polygon" decided by exact SAT over Q's two axes and the polygon's edge normals, the
bridge unchanged (A183.4).  The zone's rows are a strict subset of the poly form's exemptions, so
tau(poly) <= tau(zone) <= tau(plain) [T].
