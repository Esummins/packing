# A221 -- the pocket cover, and pocket inheritance (n-general)

Notation as everywhere in this repo: `n` unit squares in `[0, s]^2`, a node fixes `k` boxed roles at their A171/A172
multibox fixed point, `m = n - k` squares are free.  `K'(R)` is A132/A172's certified core of role `R`: a convex
polygon contained in EVERY pose of `R`.  A pose `(c, th)` of a unit square is FREE at a node when its interior lies
in the container and misses every `K'(R)`.

## 0. What A189 does, and where its 120 s goes

A189's NO-ROOM leaf is two machines:

1. **the bisection** `bisect_free`: the free square's `(centre, tilt)` space over the whole container
   `[1/2, s-1/2]^2 x [0, 90]`, halved against the roles' obstacles with `multibox._clip_rect_obstacle` (the exact
   convex dead-set clip).  Every dropped piece is certified "every pose in this piece meets some core".
2. **the lane** `Node.lane(P_j)` on each pocket `P_j` of the residue: A141/A161's cover, which answers
   `LANE(P_j) >= #{pairwise interior-disjoint FREE squares meeting int(P_j)}`, and A189's Lemma 1 concludes
   `m <= sum_j LANE(P_j)`.

Measured (results/experiment221.md): on the four k = 10 nodes the bisection costs **3.7 - 9.3 s and EXHAUSTS** (it
stops at its own depth cap, not at the deadline), and the lane then burns **109 - 115 s of the 120 s cap and returns
`None`**.  The lane is the blocker, and it is the blocker for a structural reason:

> `chordlane.lane_out(cell, ...)` roots its cover at `polylane.centre_window(cell, s)` -- the centres of unit squares
> **meeting** `int(cell)`, i.e. the pocket grown by `1/sqrt(2)` on every side.  A pocket of `0.65 x 0.30` (area 0.20)
> becomes a root of `2.06 x 1.71` (area 3.5): **17x the pocket**, and it is exactly the grown collar -- far from the
> roles that made the pocket -- that the cover cannot discharge.

The lane is answering a harder question than the node needs.

## 1. LEMMA POCKET-DEAD  [T]

Let `P_1..P_r` be axis-aligned rectangles whose union contains the CENTRE of every free pose (A189's `pockets_of`
returns such a cover of the bisection residue).  Call `P` **dead** when every pose `(c, th)` with `c in P` and
`th in [0, 180)` meets some `K'(R)`.

> **If every `P_j` is dead, the node has no free unit square at all, hence the node is DEAD for every `m >= 1`.**

*Proof.* A free square's centre lies in some `P_j`; `P_j`'s certificate excludes its pose. []

The certificate for one pocket is the **same exact machine as the bisection, rooted at the pocket**: halve
`P x [0, 90]` (`multibox.split_piece`), drop a piece as soon as `multibox._clip_rect_obstacle` empties its rectangle
against some role's obstacle, and additionally drop by `multibox.container_clip(..., strict=False)` -- a pose whose
tilt sub-bin has `w_min = min(|cos| + |sin|)` has its centre in `[w_min/2, s - w_min/2]^2`, so that clip is sound
(it is the *non-strict* one; the strict `w_max` clip would NOT be sound here).

Cost: the pocket cover buys about `log2(area(meeting window) / area(pocket)) ~ 4` extra halvings per coordinate for
the same piece count, and it never touches the collar the lane chokes on.  It is also *monotone in the node*: a
child with larger cores can only kill more.

Relation to A189: LEMMA POCKET-DEAD is strictly stronger than `LANE(P_j) = 0` **as a node verdict for m = 1** and it
subsumes A209's Lemma CN (`cn_bound`) whenever it fires, but it is NOT a counting bound -- for `m >= 2` a surviving
pocket still needs A189's `LANE` (or A209's CN groups) to be counted.  A221 changes nothing there.

## 2. LEMMA POCKET-INHERIT  [T]

Let a child node arise from its parent by one of the branch rules the trees use:

* **Rule NS** (A206): a role's box is replaced by its meet/miss subset;
* **ROLE-SPLIT** (A211 `rsplit211`): a role's box is replaced by one half;
* **POCKET instantiation** (A209 `apply_pocket`): a NEW role is added, the existing roles untouched;
* any cascade round on top of these (A171 clipping only ever removes poses).

In every case each role of the parent has, in the child, a pose set CONTAINED in its parent pose set.  `K'` is an
intersection over the surviving poses, so shrinking a role's pose set can only **enlarge** its core:

    K'_parent(R)  subset of  K'_child(R)   for every role R of the parent.

Hence a pose excluded by the parent's cores is excluded by the child's, so

    { free poses of the child }  subset of  { free poses of the parent },

and therefore

> **the parent's pockets cover the child's free centres.**

*Consequence* (`noroom221.noroom_child`): a child may skip the container-wide bisection entirely and run the pocket
cover of LEMMA POCKET-DEAD on its **parent's** pocket list with its **own** (larger) cores.  Only when an inherited
pocket survives does it pay for a fresh global bisection.  Sound for every `m`; for `m = 1` no completeness is lost
relative to running the child's own bisection first, because a surviving pocket falls through to the full leaf.

Two cautions that the implementation respects:

* the inherited list must come from an ANCESTOR on the same path, never from a sibling (siblings are incomparable);
* a pocket list recorded *after* A189's `max_pocket_area` early-out, or after a bisection that stopped on its
  DEADLINE, is still a sound cover (the early-out is a budget decision, and a deadline-stopped bisection's open
  pieces are still a superset of the residue) -- but a list recorded when the bisection hit its PIECE CAP is too,
  for the same reason.  Every stop reason of `bisect_free` leaves a cover; only an *empty* pocket list means "no
  residue", which is already a kill.

## 3. What A221 ships

* `code/noroom221.py` -- `cover_rect` (the pocket-rooted exact cover), `pocket_dead`, `pocket_pass`,
  `noroom(roles, ...)` (global bisection then the pocket cover in place of the lane) and
  `noroom_child(roles, parent_pockets, ...)` (LEMMA POCKET-INHERIT).  Wraps A189/A171; edits nothing.
* `code/tree209_integration.diff` -- the flag-gated one-liner (`A221_LANE=1`) that routes `tree209.noroom_at`
  through `noroom221`, handing it the parent node's recorded `noroom.pockets`.  To be applied after A220 lands.
* `code/bench221.py`, `results/experiment221.md`, `results/bench221.md`.

## 4. Reuse at higher n

Nothing above mentions 11.  `noroom` / `noroom_child` take `n` as an argument, and both lemmas are stated for
arbitrary `n`, `k`, `m`.  For larger `n` the pockets are what changes: more free squares means a bigger residue and
more pockets, so LEMMA POCKET-DEAD fires less often on its own and the counting bound (A189 Lemma 1, A209 Lemma CN)
carries more of the weight -- but every pocket the cover kills is one the counting bound no longer has to price,
which is a strict gain at every `n`.
