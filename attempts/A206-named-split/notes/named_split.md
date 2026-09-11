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

## 2. Y0672 R.2.3.1, the PI's node  [M]

`certs/namedsplit206_k5_11_interior_Y0672.json` run `g1_R.2.3.1`, page `namedsplit206_k5_11_interior_Y0672.svg`,
log `logs/namedsplit206_k5_11_interior_Y0672_g1_R.2.3.1.log`; **DEAD in 339 s** (commit fbbf86e0).

* The node loaded: H 56 pieces (box [2.358, 2.389] x [2.370, 2.469], tilt 0-14.3 deg), F1 136 (cell 23, TR(0,0)),
  F2 99 (cell 16, BL(1,1)), F3 71 (cell 9, TL(1,0)); H forced at BL(1,1), TL(1,0).
* The refresh cascade (the root, 3 rounds, 282 s): H kept 0.29, F1 0.76, F2 0.59, F3 0.18 of the loaded node; H's
  reach at TR(0,0) is **2 pieces, 1.5 % of its volume** (ROLE-REACH H {BR, TL, TR}: frac 0.0152) -- the sliver the
  PI saw; TR(0,0)'s anonymous table is the single cell 24, its cap 1; named_TR = {H, F1}.
* On the fresh table A205's **bar-anon** (the copy's `anon_needed`, added to A205 after its standard Y0672 run) fires
  first: the count with TR(0,0)'s anonymous cap set to 0 has NO cover (1,248 nodes, 0.07 s) -- H's two TR-meeting
  rows and F1 cannot both be TR(0,0)'s meeters beside the covers of the other three slots -- so an anonymous meeter of
  TR(0,0) is forced and cell 24 is instantiated as **F4** (10 reach pieces, box [3.225, 3.377] x [3.328, 3.377]) by
  unit propagation (branch R.2.3.1u, kind row-anon).  This is Rule NS's [H misses TR(0,0)] branch taken without its
  twin: bar-anon proves the [H meets TR(0,0)] branch has no cover.
* **R.2.3.1u DEAD by EmptyBox(F2) at round 1 (56.7 s): the mutual clip's pass 3** -- with F4's K' in the corner H is
  pushed, and F2 (BL(1,1)'s meeter at cell 16) has no pose left against H's K' at any tilt of its sub-bins.  The PI's
  prediction ("there should be an F4 core, and once that tries to cascade the clip, it will probably die") to the
  letter.  `[C: library clip trace]` branch R.2.3.1u, clip EmptyBox, round 1.
* Audit (`scratch/audit206.py`, A205's full-role sampler on the A206 certificate; `logs/audit_Y0672_g1_R.2.3.1u.log`):
  175 admissible H poses over A203's units meeting BL(1,1) + TL(1,0), F1 183 / F2 513 / F3 90 / F4 28 admissible grid
  poses meeting their slots in their cells -- **0 pairwise-disjoint configurations of H + F1..F4** (148 partial tries):
  consistent with the kill.

So A205's leaf R.2.3.1 (TR(0,0)<-23, BL(1,1)<-16, TL(1,0)<-9) of Y0672's g1 tree is closed.

**The whole tree of Y0672 under Rule NS (run `g1_tree`, wall 3,600 s; 19 nodes, depth 4, 2 NS splits, 10 DEAD / 8
undecided, ALIVE at the wall; 3,718 s).**  R.1 = TR(0,0)<-19 closed (BR(0,1)<-21, 22, 23 by EmptyBox r2, 52-57 s
each) and **R.2 = TR(0,0)<-23 closed entirely**: BL(1,1)<-6, 11 by FC r1; under BL(1,1)<-16, TL(1,0)<-9 is the PI's
node again -- here bar-anon is silent on the fresh table and **Rule NS fires: split H at TR(0,0) (meeting fraction
0.063, alive row 24, named {F1, H}); [H meets TR(0,0)] DEAD by EmptyBox r2 (170 s), [H misses TR(0,0)] DEAD by
EmptyBox r2 (159 s)** -- the F4 instantiated by FC in the miss branch kills the fixed point, as the PI said;
TL(1,0)<-14 by FC r2 (399 s), TL(1,0)<-19 by EmptyBox r1 (29 s).  R.3 = TR(0,0)<-24 is open: R.3.1 = BR(0,1)<-16 has
TL(1,0)<-7 DEAD (EmptyBox r2), TL(1,0)<-8 split by Rule NS (H at TR(0,0), fraction 0.64) with its meets branch alive
at the wall, and three rows plus R.3.2-4 behind the wall -- re-run as the path-restricted tree `g1_tree_R.3`.

## 3. The fully named leaves of A205's certificates  [M]

Every fully named ALIVE leaf of A205's certificates (g1 pads first; the extended Y0202 `_w3600v4` leaves; the pad-0
leaves last) loaded from its last snapshot and run under Rule NS (wall 3,600 s a page, split among a page's leaves).
Every kill `[C: library clip trace]` with branch / clip / round; certificates `certs/namedsplit206_<nid>.json`, pages
`docs/residue_map/campaigns/A206-namedsplit/namedsplit206_<nid>.svg`, rows `results/namedsplit206.jsonl`, audits
`logs/audit_*.log` (the auditor `scratch/auditor206.sh` samples every DEAD leaf with A205's full-role sampler plus
the Rule-NS miss hypotheses).

| page (pad) | A205 leaf | verdict | nodes / NS splits | the splits and kills (branch: clip r round, s) | s |
|---|---|---|---|---|---|
| k5_11_Y0672 (g1) | R.2.3.1 | **DEAD** | 2 / 0 | bar-anon on the fresh table instantiates F4 at cell 24: R.2.3.1u EmptyBox(F2) r1, 57 s (s.2; audited, 0 refutations) | 339 |
| k5_16_Y0230 (g1) | R.2.1.2s | **DEAD** | 5 / 2 | root 637 s; NS F1 at BR(0,1) (fraction 0.0088): [meets] REACH r1 192 s, [misses] alive -> NS F4 at BR(1,0) (0.12): [meets] EmptyBox r3 455 s, [misses] EmptyBox r3 382 s | 2,242 |
| k5_11_Y0738 (g1) | R.1.1.2s | ALIVE | 12 / 4 | NS F3 at BL(1,1) (0.034): [meets] REACH r2 159 s; [misses] -> NS F2 at BR(0,1) (0.23, rows 21, 22): [misses] EmptyBox r3 487 s, [meets] -> NS F1 at TR(0,0) (0.43) -> NS F3 at TR(0,0) (0.82): three sharp leaves with every name HARD (2 anonymous rows at TR(0,0) unresolved; next lever: the whole tree / LP) | 3,020 |
| k5_16_Y0083 (g1) | R.3.1s | **DEAD** | 1 / 0 | the loaded sharp leaf dies in its own refresh cascade: FC r2 (297 s) | 297 |
| k5_16_Y0380 (g1) | R.1.1s | **DEAD** | 5 / 2 | root 198 s; NS F2 at TL(1,0) (0.040, rows 9, 14): [meets] COUNT r2 197 s, [misses] -> NS F3 at BR(1,0) (0.30): [meets] EmptyBox r1 48 s, [misses] EmptyBox r1 30 s | 1,077 |
| k5_16_Y0865 (g1) | R.1.3.2s | **DEAD** | 1 / 0 | the loaded sharp leaf (H, F1..F5) dies in its own refresh cascade: EmptyBox r2 (353 s) | 353 |
| k5_16_Y0941 (g1) | R.3s | ALIVE | 8 / 3 | root 160 s; NS F1 at BR(0,1) (0.13): [misses] EmptyBox r3 247 s; [meets] -> NS F3 at BR(0,1) (0.26): [meets] EmptyBox r3 290 s, [misses] -> NS F3 at TL(1,0) (0.40, row 8): [misses] EmptyBox r2 94 s, [meets] alive after the sharp round (every name HARD) | 1,683 |
| k5_16_Y0941 (g1) | R.4s | ALIVE | 2 / 0 | no soft pair at all (every name HARD at the loaded node): the sharp round only; the LP's input | 321 |
| k5_11_Y0202 (g1, ext v4) | R.1.1.4s | ALIVE wall | 2 / 1 | root 702 s (H 276 pieces); NS F2 at TL(1,0) (0.049, row 14): [meets] **FC r2** 219 s; [misses] behind the 900 s wall (a quarter of the page's hour) | 922 |
| k5_11_Y0202 (g1, ext v4) | R.1.2s | **DEAD** | 1 / 0 | the loaded sharp leaf (H 220 pieces, F1..F4) dies in its own refresh cascade: EmptyBox r2 (234 s) -- the third such leaf (Y0083, Y0865) | 234 |
| k5_16_Y0881 (g1) | R.2.3s | ALIVE | 10 / 3 | root 165 s; NS F2 at TR(1,0) (0.24): [meets] -> NS H at TR(1,0) (0.57, old policy) -> NS F1 at TR(1,0) (1.0): [F1 misses] MISS-CLIP r1; three sharp leaves alive (every name HARD) | 2,332 |
| k5_16_Y0402 (g1) | R.1.3.1s | ALIVE | 8 / 3 | root 451 s; NS F2 at BR(1,0) (0.42): [meets] -> NS F1 at BR(1,0) (0.83): [meets] -> NS H at BR(1,0) (0.9999): both FC r1 (153 / 104 s); [F1 misses] **MISS-CLIP r1** (every piece of F1 within 1/2 of the box, 0 s); [F2 misses BR(1,0)] alive after the sharp round (every name HARD) | 2,194 |

## 4. The whole trees under Rule NS (the pages whose 900 s trees were wall-cut)  [M]

The tree from A203's start with Rule NS at every fully named node, wall 3,600 s, g1 pad (window-valid); a run
restricted to a branch path (`--pad g1+R.3`) records the other branches as skipped.  A DEAD whole tree is a kill of the
PAGE (the status gallery's block 7o collects those rows only).

| page | run | verdict | nodes / depth / NS splits | dead / alive | the kills (branch: clip r round, s) | s |
|---|---|---|---|---|---|---|
| k5_11_Y0672 | g1_tree | ALIVE wall | 19 / 4 / 2 | 10 / 8 | R.1 closed (BR(0,1)<-21, 22, 23 EmptyBox r2); R.2 closed (BL(1,1)<-6, 11 FC r1; <-16: TL(1,0)<-9 **NS H at TR(0,0): both EmptyBox r2**, <-14 FC r2, <-19 EmptyBox r1); R.3 open (R.3.1: TL(1,0)<-7 EmptyBox r2; <-8 NS H at TR(0,0) meets alive at the wall) | 3,718 |
| k5_11_Y0672 | g1_tree_R.3 | ALIVE wall | 12 / 6 / 4 | 3 / 11 | under R.3.1.2 = TR(0,0)<-24, BR(0,1)<-16, TL(1,0)<-8: NS H at TR(0,0) (0.64) -> H at TL(1,0) (0.65) -> H at BR(0,1) (0.75): [misses] EmptyBox r3 418 s, [meets] depth cap; -> NS F4 at TR(0,0) (**0.0039**): [meets] EmptyBox r2 193 s; the hour spent on H's large-fraction splits (300-680 s a node): **the split is the lever only for slivers** -- MAX_FRAC 0.5 from here on | 3,636 |
| **k5_11_Y0985** | g1_tree | **DEAD** | 8 / 2 / 0 | 6 / 0 | BR(0,1)<-16 EmptyBox r2 120 s; <-21: TL(1,0) pairs {7,9}, {7,14}, {8,9} FC r1 (270-291 s), {8,14} EmptyBox r2 364 s; <-22 FC r1 198 s -- **the page's first kill in the lab** (A205's 900 s tree was cut at 5 nodes); no split needed, the wall was | 2,121 |
| **k5_11_Y1104** | g1_tree | **DEAD** | 8 / 2 / 0 | 6 / 0 | BR(0,1)<-16 FC r1 182 s; <-21: TL(1,0) pairs {7,9}, {7,14}, {8,9} FC r1 (280-305 s), {8,14} EmptyBox r2 401 s; <-22 FC r1 215 s -- **the page's first kill in the lab** (A205's 900 s tree: 4 nodes, cut); the same shape as Y0985 | 2,401 |
