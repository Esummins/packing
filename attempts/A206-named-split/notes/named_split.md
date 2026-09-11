# A206 -- Rule NS: the NAMED-OR-ANONYMOUS split at the clip tree's "fully named" leaves

The reading is the PI's (2026-09-11 12:20, k5_11 Y0672, A205's leaf R.2.3.1): *"how is this node still alive?  I
don't see how the TR00 meeter box (the one with no core built) is placeable?  With how close the H and F1 cores are to
the possible centers, it seems like there should be an F4 core, and once that tries to cascade the clip, it will
probably die."*  At that leaf H's box is [2.358, 2.389] x [2.381, 2.466] at tilt 0-12 deg and TR(0,0)'s widened box
starts at 2.870 in x and y: H's top-right corner reaches (2.87, 2.92) upright, so A161's exact test cannot certify
that H misses TR(0,0) -- by 0.02 -- and A205's stop rule (`tree205b.candidates`: named_p = {H if not provably missing
p} u {instantiated roles not provably missing p}; |named_p| >= 2 -> the slot is not branched on) counted H + F1 and
stopped: "every forced slot has two named meeters".  The count's own witness placed TR(0,0)'s second meeter in the
anonymous cell 24 instead.  A "name" that rests on a sliver of a role's reach is a DISJUNCTION (the role meets the
slot, or it does not) that A205 counted instead of splitting.  Labels: [T] proved, [S] supported, [M] measured, [C] open.
Code: `code/tree206.py` (the node with a MISS hypothesis, the split, the clips), `tree206b.py` (A205's tree with the
split at the stop), `load206.py` (a node loaded from an A205 certificate), `run206.py` / `run206.sh`, `fig206.py`;
A205's `poly204.py` / `poly204b.py` / `tree205.py` / `tree205b.py` / `fig204.py` / `fig205.py` copied at 2833db8b,
unchanged (the copy is imported, the changes are in the new modules).

## 1. Rule NS (any n)  [T]

Setting = A205 `notes/clip_tree.md` s.1 (Lemma CT): a node N of the clip tree -- pins, H's pieces, instantiated roles
F_1..F_k carried as pieces, each a free square distinct from every other role, some pinned to a grid cell and each
HYPOTHESISED to meet the slots it is named at (H: the slots of `forced_H`; F_i: `role_slots[F_i]`) -- at which A204's
cascade has reached its fixed point and the option table of a round in which no role was instantiated has been read.
For a forced slot p (Theorem FC, `forced_corners.md`: two distinct non-pin squares of every packing of the page meet
the widened open box B_p+) write

* named_p = {r in {H, F_1..F_k} : r is not provably missing B_p+ (A161's exact test on r's pieces)} -- A205's set;
* a pair (p, r) with r in named_p is **HARD** when N hypothesises r at p (p in forced_H for r = H, p in role_slots[r]
  otherwise) and **SOFT** otherwise;
* rows_p = the alive cells of p's anonymous option table (after Lemma HC).

**Rule NS.**  Let N be a node at which every forced slot has |named_p| >= 2 (A205's stop) and let (p, r) be a soft
pair.  N is DEAD iff both of the following nodes are DEAD:

  [r meets p]   N with r hypothesised at p: p joins forced_H (r = H) or role_slots[r]; at a corner slot r takes the
                lonely clip at that corner; A204's apply re-clips r by the exact reach against ALL its slots every
                round (the poses of r not provably missing every slot of the set, bisected two levels -- a superset
                of the poses meeting them all: sound);

  [r misses p]  N with the hypothesis "r's interior does not meet B_p+": (i) every row (g, S) of r with p in S leaves
                the option table, so r is no candidate meeter of p in the count and in Theorem FC's `avail` (H_reach /
                roles_reach exclude p), and (ii) every piece of r ALL of whose poses meet B_p+ is dropped (the kill
                MISS-CLIP when none is left).  The count then needs two meeters of p among named_p \ {r} and the
                anonymous rows: with |named_p \ {r}| = 1 and a cap of 1 Theorem FC's forcing INSTANTIATES the unique
                anonymous meeter from its union (A204), otherwise A205's rule branches on rows_p singly (one other
                name) or in pairs (none), and with |named_p \ {r}| = 1 and rows_p empty the node dies at once by FC.

*Proof.*  Let P be a packing of N's hypothesis and r's square in P be Q.  Either int Q meets B_p+ or it does not.  In
the first case P is a packing of [r meets p]: the hypothesis "r meets p" holds, so r's pose survives the exact reach
clip at p at every resolution (the reach keeps every piece not provably missing p, and Q's piece is one), and at a
corner slot Q is non-lonely (FC-corner, Theorem B), so the lonely clip keeps it.  In the second case P is a packing
of [r misses p]: (i) the rows of r containing p are the poses of r meeting p, none of which is Q, so dropping them
loses no cover that P realises (the count is exhaustive over the remaining rows: A200's semantics), and Theorem FC's
two meeters of p in P are two non-pin squares other than r, i.e. among the other named roles and the anonymous free
squares -- which is exactly what the count, the cap and A205's branching rule demand; (ii) a piece of r all of whose
poses meet B_p+ does not contain Q.  The two cases are exhaustive, each branch is a node of Lemma CT (a hypothesis on
P implied by N's plus one predicate on Q, closed under A204's sound clips), so N is DEAD iff both are.  []

**The MISS-CLIP test (`tree206.provably_meets`)** [T]: a unit square with centre c at distance < 1/2 from a closed
box K contains the open disc of radius 1/2 about c in its interior, which meets K, hence meets int K (K is the
closure of the open box B_p+, and an open set meeting the closure of an open set meets the open set).  The distance
from c to K is convex in c, so its maximum over a centre rectangle is at a corner: a piece (rect x tilt bin) all of
whose corners are at distance < 1/2 from K -- computed exactly in rationals on the widened box SHRUNK by 10^-6 (a
smaller box: meeting it implies meeting B_p+) -- provably meets B_p+ at every tilt.  A piece that fails the test is
kept.  (At Y0672 R.2.3.1 no piece of H is within 1/2 of TR(0,0)'s box -- the clip is idle there; the content of the
miss branch is the count.)

**Which pair.**  Every soft pair of the node is a candidate; the split is taken on the one with the smallest MEETING
FRACTION (the volume fraction of r's pieces not provably missing p after the two-level reach bisection, A161) among
those that QUALIFY (fraction < 0.5, or rows_p non-empty), then the rest by fraction -- the sliver first, so the
[r meets p] branch is the cheap one (r clipped to a sliver, usually dead in the fixed point) and the [r misses p]
branch is the PI's "there should be an F4 core".  The two branches are run [meets] first.  After the split the pair
is HARD in one child and absent from named_p in the other, so the recursion consumes the finite set of soft pairs;
A205's branching (rows singly / in pairs, bar-anon), its refresh rule (the table read is that of a round with no
instantiation -- inherited: the split is applied only when `candidates()` returned None on a fresh table) and its
sharp leaf (refine 3 / nsub 8, now only at a node with NO soft pair left) are unchanged.

**A node loaded from a certificate (`load206`)** [T]: a node of A205's tree is re-created from its last snapshot --
every role's pieces after that node's last fixed point (7 decimals of the centre rect, 4 of the tilt in degrees) padded
OUTWARD by 10^-6 / 10^-3 deg (a superset of the recorded pieces: sound; a snapshot whose piece list was capped is
refused), with its forced slots, role slots, pinned cells and corners; the run's root is one full cascade at the
loaded node (the refresh: A205's proviso) before any split.  Kept fractions in the run are relative to the loaded node.

This is A182's H-meets / two-free split (`attempts/A182-assignment-resume`, A180 `notes/assignment.md` s.1: the
second meeter of p is an existing role or a new free square -- exhaustive) applied at the leaf to every soft name.

## 2. Runs  [M]

(filled per batch below; every kill `[C: library clip trace]` with branch / clip / round; certificates
`certs/namedsplit206_<nid>.json`, pages `docs/residue_map/campaigns/A206-namedsplit/namedsplit206_<nid>.svg`,
rows `results/namedsplit206.jsonl`.)
