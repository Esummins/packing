# A211 -- the COARSE TREE: cheap internal nodes, the leaf rules at fully named leaves, exactness last (2026-09-12)

The PI (18:20): *"the more coarse we can get away with the better, since we want to reach the leaf kills asap."*  A209's
trees are WALL-limited: every gallery page sits ALIVE at 3,600 s on both pads with undecided branches because a 5-role
exact fixed point costs 400-1,000 s and the hour goes into 10-20 internal nodes (A209 `results/progress.md`), while the
leaf rules (Lemma CORNER-COVER, NO-ROOM + the pocket CN bound, Lemma BASIN, Rule NS) kill in milliseconds to seconds
once a fully named leaf is reached.  So the internal nodes are made CHEAP supersets and exactness is spent only where
a kill is claimed.  Labels: [T] proved, [S] supported, [M] measured, [C] open.  Code: `code/coarse211.py` (the coarse
node), `tree211.py` (the tree with the leaf rules), `leaves211.py` (rule CC on the live node), `run211.py`; A209's
chain copied at 65a4903e (`poly204*`, `tree205*`, `tree206*`, `tree207`, `tree209`, `clip207`, `stage209`, `load211`)
and A210's `cc210` / `leaves210` at 65a4903e, imported unchanged except where named below.

## 1. The setting (A205 Lemma CT, `attempts/A205-clip-tree/notes/clip_tree.md` s.1)  [T]

A node N of the clip tree is a hypothesis about the packing (pins, H's pieces, instantiated roles F_i as pieces, some
pinned to a grid cell, each named at the slots it is hypothesised to meet, Rule-NS miss hypotheses); A204's cascade at
N is a chain of sound clips and sound kills; the branching rule over a forced slot's remaining meeter options is
exhaustive PROVIDED the option table read is that of a round in which no role was instantiated (the fresh-table
proviso); N is DEAD iff every branch is DEAD.  Nothing below changes the branching rule, the apply, or the leaf
lemmas; everything below only WEAKENS the clips at internal nodes (keeps more poses) and reorders the leaf work.

## 2. The soundness points, each a necessary condition on a genuine packing of N  [T]

**S1 (re-binning).**  At a coarse node every non-pin role carrying more than CAP = 96 pieces is replaced by the units
of a 4 x 4 x 6 grid (sub-rects x tilt bins, exact rationals) of its own hull that MEET some piece
(`coarse211.rebin`, open overlap; a degenerate piece counts when it lies inside the unit).  Every piece is covered by
the units it meets, so the union of the units is a SUPERSET of the union of the pieces: the role's true pose (which
lies in some piece) lies in some unit.  Every downstream test (K', reach, rule S, the count, FC, Rule NS's meeting
fraction, rule CC's slack, NO-ROOM's boxes) is monotone in the pose set -- a larger set kills less and claims less --
so a coarse DEAD is a DEAD.  The exact leaf cascade starts from the coarse units (a superset of the exact node).

**S2 (a prefix of the clip chain).**  The coarse fixed point (`coarse211.coarse_fixpoint`) is A204's `poly204.fixpoint`
with the LONELY clip omitted, refine = 1 (A204: 2), at most 2 mutual-clip passes (A204: up to 10), and K' rebuilt in
the COARSE mode of S2'.  Every pass is one of A171/A172/A173's certified clips (container clip, tautologous split,
mutual clip against K'); any PREFIX of a chain of sound clips is sound (A205's cost levers (i)-(v) rest on the same
fact).  Omitting the lonely clip and the basin clip at internal nodes keeps more poses.  The rule-S clip and Lemma HC
on the rows (A205 s.2) are unchanged and cheap.

**S2' (the COARSE CORE at internal nodes: a weaker K', still certified).  2026-09-14, A211e.**  A clip against a role's
K' is sound for ANY set K' of points that is certified to lie inside EVERY pose the role still has: a pose of another
square that would overlap such a set is impossible.  The kill power grows with K', the soundness does not -- so at an
internal node, whose only job is to kill cheaply or hand the branch on, K' may be replaced by any certified SUBSET.
A211e does that twice over (`coarse211.KMODE` = "union", `coarse211.NGRID` = 33; both are read from `A211_KMODE` /
`A211_NGRID` so the old node can be re-run for comparison):
  (i) KMODE "union" (A171).  K' is A132's certified polygon of the union hull B_u of the surviving pieces instead of
      A172's exact intersection of the per-piece K'(B_i).  Every piece box B_i is contained in B_u, so the pose set of
      B_u CONTAINS the pose set of B_i, and a point certified inside every pose of B_u is certified inside every pose
      of B_i: K'(B_u) is a subset of every K'(B_i) and hence of their intersection.  The union core is thus the
      weaker of the two -- it forgets the growth the clip made unevenly across the tilt sub-bins, which is exactly
      what an internal node does not need.  The axis core moves the same way: `MBox.rebuild` in kmode "pieces" keeps
      max(per-piece core, union core) and in kmode "union" keeps the union core alone.
  (ii) A coarser tilt grid.  `polycore.build(box, n_grid)` clips a start polygon by the half-planes of n_grid SAMPLED
      tilts, shrinks, rounds to rationals, and then CERTIFIES every vertex with the exact `polycore.vertex_ok` over
      the WHOLE tilt interval [t0, t1], retrying with a larger shrink until every vertex certifies (or raising).  The
      certificate is therefore independent of n_grid: whatever polygon comes back has every vertex proved inside
      every pose, and Q(c, theta) is convex, so the polygon is inside every pose.  n_grid only decides HOW BIG that
      polygon may be -- a coarse grid needs a larger shrink and returns a smaller polygon (measured on six role-shaped
      boxes: n_grid 33 certifies wherever 97 does, agrees on the certified area to 3-5 significant digits, and costs
      0.3-0.6 of the build).  Soundness is untouched at any n_grid.
A wide role's union hull may certify NO polygon at all, where its per-piece K' still certifies (A178's `mbpatch178`
turns that failure into an empty K': sound, but the role then clips nothing).  So the coarse rebuild is a LADDER --
union at n_grid 33, else union at 97, else kmode "pieces" at 97 -- and a role that reaches the last rung has exactly
its pre-A211e core: no node is worse off than before, and the count of each rung is reported per run
(`coarse211.grid_rep`, printed by run211).  The exact
leaf cascade (S5 (e), `set_coarse(False)`) is untouched: `poly204.fixpoint` sets kmode "pieces" and the library grid,
and the per-piece K' of A172 is what every certificate-bearing leaf kill is proved against.  Consequence for the
record: an internal node's kills stay valid (each is still a necessary condition), an internal node's ALIVE still
only means "branch further", and the coarse round may now kill LATER (a weaker clip) but each node costs much less --
the trade is measured in NOTES_coarse_core.md, not asserted.

**S2'' (the coarse core is CONDITIONAL).  2026-09-14, A211f.**  S2' makes the coarse core SOUND; it does not make it
profitable.  A211e measured both directions on one page each: where the fixed point dominates (k5_11_interior_Y0202:
89-214 s a node) the coarse core is -86 % a node and buys three extra kills inside the wall, and where the node is
already cheap and its kills come from EmptyBox / COUNT off a strong clip (k5_11_interior_Y0036_D07: mean 12.1 s a
node) the weaker clip kills later, the tree needs 51 nodes where 24 sufficed, and the wall grows 45 %.  So the core is
chosen PER NODE by a predicate over the node's expected cost -- `coarse211.CoarsePage.coarse_core_on`: the coarse core
is used iff the PARENT's cascade took more than `COARSE_SECONDS` (20 s) or the node carries `COARSE_ROLES` roles
(99 = off by default; on a shallow page every node from depth 1 already carries >= 8 roles, so the role count alone
just restores A211e).  A start node's root has no parent and runs with the exact per-piece core.  NOTHING about
soundness depends on the predicate: by S2' both cores are certified subsets of every pose, so either choice gives a
sound clip, a valid kill and the same meaning of ALIVE.  It is a BUDGET decision and is recorded as one -- every
node's round report carries `coarse_core`, `kmode` and `n_grid`, the trace carries a `COARSE-CORE` test with the
parent's seconds and the rule, and `coarse211.grid_rep` counts the nodes that went each way.

**S2''' (the no-room leaf is MEMOISED, not changed).  2026-09-14, A211f.**  A189's no-room leaf
(`noroom189.build_node` / `bisect_free`, A189 Lemma 1) is 82 % of an expensive page and re-derives at every child what
its parent already derived.  `noroommemo211.py` WRAPS it (module-attribute patches; A189, A208 and A171/A132 are
read-only) with three pure memos: the compiled `Obstacle` of a K' is interned process-wide on (role name, mode, exact
vertices) instead of per box, so A211d's clip memo and A173's `Bin.radii` cache hit across nodes; `build_node` is
memoised on (the exact role boxes, s0, nsub, refine), replaying an `MB.EmptyBox` -- A171's pair leaf, a KILL -- rather
than swallowing it; and `bisect_free` is memoised on the node's OBSTACLE CONTENT (plus s, tsub, depth, max_pieces),
which is all it reads, so a child whose cores agree with its parent's reuses the bisection exactly.  This is the
parent/child case Lemma ROLE-SPLIT creates on purpose: rsplit211 prefers to bisect a role whose K' is EMPTY, and such
a role contributes no obstacle at all.  A run stopped by the DEADLINE is never cached (its residue depends on the
clock, not on the content).  Every memoised value is the value the library would return for the same content
(`A211_NOROOM_VERIFY=1` recomputes every hit and asserts), so every certificate field is identical; what the memo
does change is that the 120 s per-node cap (`tree211.NOROOM_CAP`, once per node) now buys more of the leaf.

**S3 (shallow reach).**  The option table's per-cell reach bisects 2 levels per cell and 1 for joint slot sets (A198:
5 / 2; `CoarsePage.set_coarse`), and a role's reach against its slots is clipped in place (depth 0).  A shallower
bisection stops earlier in the same tautologous split-and-test tree, so its survivors are a superset of the deeper
survivors: the rows, unions, caps, Theorem FC's `avail` and the count all see a larger set (fewer kills, never a
wrong one).  A205's seeded reach (the parent's survivors re-clipped in place against the obstacles that changed) is
sound by hypothesis implication: a pose the parent's K' killed is impossible under the child's hypothesis, which
implies the parent's, whatever the child's coarse K' looks like.

**S4 (one round, then branch).**  A coarse node runs ONE cascade round (fixed point, option table, caps, FC, count,
apply) and branches at once on A205's rule (fewest rows; pairs when no named meeter; unit propagation).  The fresh-
table proviso is kept exactly as A205/A206: `candidates()` returns "stale" when the last round instantiated a role and
the tree runs a refresh round (coarse, one round) before any branch.  Depth cap 6, node cap 600.

**S5 (the leaf rules, in order, at a FULLY NAMED node -- every forced slot has two named meeters on a fresh table).**
  (a) rule CC (A210 Lemma CORNER-COVER, Corollaries CC1 / CC') on the live node (`leaves211`): the pose classes are the
      node's current pieces (coarse units at an internal leaf: they over-state the wall slack, and CC1's band grows
      with the slack -- CC'(a) says the page's slack is an upper bound anyway), the candidate second meeters are the
      slot's alive anonymous cells and the other roles' hull boxes (supersets).  DEAD when a role the node
      hypothesises at p cannot reach the band, or when every pose class of the pushed-in role leaves no second meeter.
      The band's formulas hold for every slack d1, d2 >= 0 (the fourth halfplane never meets the cell); NEAR = 0.6 is a
      usefulness gate, not a soundness condition.  lam = 1 at pad 0, the page's lam on the window pad (CC').
  (b) NO-ROOM (A189 Lemma 1) on the roles' hull BOXES with the pocket CN bound at k >= 9 (A208 / A209 `noroom_at`;
      cores from boxes lie inside cores from pieces: sound, weaker); at k = 9 the pockets are BRANCHED on (Lemma
      POCKET, A209 `notes/k5killer.md`: the 10th square's centre lies in some pocket, the disjunction is exhaustive,
      each branch instantiates a superset) with a 120 s cap on A189's search (a shorter search decides less), run once per k along a path (an NS child adds no role and its boxes are subsets of the parent's, where the search was already undecided at the cap).
  (c) the basin clip (A207 Lemma BASIN (ii)) with `results/basin207.jsonl`'s BASIN rows whose window covers the page's,
      applied to every non-pin role's pieces; a role emptied is DEAD by BASIN.
  (d) Rule NS (A206) on the soft name with the smallest meeting fraction below MAX_FRAC = 0.5 (slivers only); the two
      children [r meets p] / [r misses p] are exhaustive (A206 s.1) and are coarse nodes again.
  (e) ONLY THEN the exact cascade at the leaf: `set_coarse(False)` restores A209's node (nsub 4 / refine 2, the lonely
      clip, the basins, reach 5 / 2) and A204's cascade runs 3 rounds from the coarse units (a superset: sound), then
      A205's sharp round (refine 3 / nsub 8).  After it the table is re-read: new branches are coarse children.
  A leaf is DEAD iff one rule proves it; the node is DEAD iff every branch is; undecided (wall / caps) = ALIVE.
  No rule is applied twice to the same state without a change in between (flags `noroom_done`, `basin_done`,
  `sharpened`, `coarse`, reset at every branch).

**S6 (pad 0 first).**  Each page runs pad 0 (lam = 1) first, then the G1 window pad; a pad-0 DEAD is recorded
s0-only, WINDOW-PENDING (A209's rule); a page is killed only by a DEAD window run.  The pad enters only through
Theorem FC's slot pads and CC's lam.

**S7 (certificates and audit).**  Every kill carries branch / rule / round / seconds and the node's last snapshot
(`certs/coarsetree211_<nid>.json`), verdict `[C: closed-form / library clip trace + the leaf lemma]`, no verifier
clause; `code/audit211.py` (A206's audit206b as A209 adapted it: sampling inside the parent's snapshot pieces, exact
meets test, FC and CC kills need TWO meeters of the slot -- the cap-1 two-meeter criterion, NOROOM kills m free
squares, BASIN kills a pose outside the basins) is run by the worker on every DEAD leaf after the node.

## 3. What is measured before the launch (Y0202 at pad 0, `logs/test_Y0202_zero.log`)  [M]

The whole wall-1,200 s run: 13 nodes, depth 5, 5 DEAD / 8 undecided (ALIVE at the wall); per node R 36 / R.1 16 / R.1.1 33 / R.1.1.1 EmptyBox 27 / R.1.1.2 63 + no-room 8 (A189's pair leaf on the role boxes, k = 10) / R.1.1.3 EmptyBox 15 / R.1.1.4 80 / R.1.1.4.1 90 / R.1.1.4.1.1 37 then DEAD by rule CC (F4 a corner square at TR, the hypothesised second meeter of TR(0,0) cannot reach the wall band) at depth 5 / R.1.1.4.1.2r1 EmptyBox 6 / R.1.1.4.2 74 / R.1.1.4.2.1 91 s -- the fully named leaves were reached at depths 3 and 5 (A209's zero run reached depth 4 in 3,718 s), the leaf rules that fired: no-room (EmptyBox on the boxes) at d3, rule CC at d5, Rule NS three times (F2 at BL(1,1) 0.21, F2 at TL(1,0) 0.21); the exact cascade never ran.  One price found and fixed before the launch: A189's no-room at the k = 10 leaves came back UNDECIDED at its 300 s cap three times on one path (665 s of the 1,274 s) -- now capped at 120 s and run once per k along a path (an NS child adds no role).

## 4. Lemma INHERIT -- every page starts from the MERGED state of all prior certificates (2026-09-12, A211b)  [T]

The PI (19:10): *"your new run ignored the prior y0202 work and started the node over."*  A205, A206, A209, A210,
A208 and A207 all ran trees over the SAME pages from the SAME A203 start, and each of their kills is audited and
certified.  A211 must not redo them.

**The path of a node.**  Fix a page and a pad, and the A203 start s0 it was run from.  A node of any of those trees is
the start hypothesis conjoined with the ordered list of the branch steps taken from the root, each step one of
  (i)  a ROW / PAIR step `p <- R`: "the meeters of the forced slot p are the squares of the cells R" (A205 s.1);
  (ii) a Rule-NS step `r meets p` / `r misses p` for an instantiated role r and a slot p (A206 s.1);
  (iii) a Lemma-POCKET step "the remaining free square's centre lies in the pocket P_j" (A209 notes/k5killer.md).
This ordered list is the node's PATH KEY.  A unit-propagation step (the `u` records) is NOT part of the key: it is
DERIVED at the node by the node's own sound clips, so it is implied by the weaker hypothesis and a kill under it kills
the weaker one too.  Two nodes of two different campaigns with the same path key are the SAME hypothesis, because a
step's meaning depends only on the page, the pad and the start -- not on which clips the tree ran to get there.

**Lemma INHERIT.**  Let P be a path key over (page, pad, s0).
  (a) *Kills are final.*  If some certified run proved the node at P DEAD -- by its own clip chain, or because every
      branch of the exhaustive list it recorded at P is DEAD, or by a certified leaf rule applied at P (A210 rule CC,
      A208 NO-ROOM + the pocket CN bound, A207 Lemma BASIN, A206 Rule NS) -- then P is impossible, and so is every
      path extending P.  *Proof.*  Every such rule is a sound necessary condition on a genuine packing satisfying the
      hypothesis P; a refutation of P refutes P conjoined with anything.  The refutation does not depend on the pose
      set the refuting run happened to hold: the hypothesis set is what died.  []
  (b) *Branch lists are reusable.*  If a certified run recorded at P the branch list P.1, ..., P.m (the rows alive at
      the tightest slot on a FRESH option table, A205 Lemma CT's branching rule), then the disjunction of the P.i
      holds under P.  *Proof.*  That is exactly what Lemma CT's branching rule certifies at P, and it is a statement
      about P alone.  The new tree may therefore REPLAY the list rather than re-derive it -- and need not re-run the
      clips that pruned the slot's other rows, since those kills are instances of (a).  []
  (c) *The page verdict.*  Walk the merged trie of every prior tree from the root: at a path P, if (a) closes P,
      record it DEAD (FINAL, with its certificate); else if some prior run recorded a branch list at P, recurse into
      the branches of the list of the most recent such run (each list is exhaustive on its own by (b), so one
      suffices); else P is a START NODE.  Then the page is DEAD iff every start node is DEAD.  *Proof.*  Induction on
      the walk using (a) and (b), then Lemma CT at the start nodes.  []

**How a start node is loaded.**  Its state is the deepest snapshot recorded on its own path chain
(`inherit211.anc_snapshot`), loaded with A206 `load206`'s semantics -- every recorded piece padded OUTWARD by 1e-6 in
the rect and 0.001 deg in tilt, so the loaded pose set is a SUPERSET of the recorded one -- followed by the remaining
branch steps of the path, applied with the tree's own `apply_branch` / `apply_ns` / `apply_pocket`.  An ANCESTOR's
snapshot is a sound over-approximation of the start node's parent (its hypothesis is implied by the start node's), and
a `u` record's snapshot is sound for the weaker path for the same reason as above; each applied step is a child of a
list certified exhaustive by (b).  A snapshot written at the 300-piece cap holds only SOME of the node's pieces: it is
a subset of the node's pose set, so it is never loaded (`inherit211.snap_complete`) -- never a silent subset.

**(d) The climb: the nearest COMPLETE ancestor, the A203 stage-0 root at worst (2026-09-14, A211h).**  Let P be a
start path and let A_0 = P, A_1, ..., A_n = () be its prefixes, innermost first.  Then for EVERY i, the state of A_i
padded outward and carried forward by the recorded branch steps of P beyond A_i is a sound over-approximation of P.
*Proof.*  A_i is a prefix of P's path key, so the hypothesis of A_i is implied by that of P and the pose set recorded
at A_i contains every pose consistent with P (this is the same argument as for the parent above, applied i levels up);
padding outward only enlarges it (load206); and each of the remaining steps is a child of a branch list certified
exhaustive at its own node by (b), so applying them lands on exactly P's hypothesis, over-approximated.  The case
i = n is the page's own A203 stage-0 root, which is the weakest hypothesis of all and is always available -- it needs
no snapshot, only the page and the pad.  []

So the loader (`inherit211.anc_snapshots` / `cands_of`, `startload211.load`) takes the ancestors carrying a COMPLETE
snapshot, DEEPEST FIRST, with the A203 stage-0 root appended last, and loads the first of them that reads back; a
capped snapshot, an ancestor with no snapshot (a refresh record), and a certificate rewritten under the run's feet
(A211 rewrites its own certificate per node, so a candidate found at merge time can be gone at load time) all make the
loader CLIMB one step further instead of refusing the start node.  Every candidate is sound by (d) -- the climb costs
only the replay of the extra steps, never correctness.  What was loaded is recorded in the node's
`start_meta.loaded_from` (mode `snapshot` / `a203_root`, the ancestor, the number of steps replayed, and each refused
candidate with its reason) and in the run row's `start_runs[*].loaded_from`.  A pad left ALIVE by an old loader
refusal is therefore no longer FINAL: `run211.wall_limited` resumes it (A211h).

**What it is worth (measured, `logs/test211b_Y0202_zero.log`; `python code/inherit211.py <nid> <pad>` prints it).**
k5_11_interior_Y0202 pad 0: 3 prior trees merge to 16 paths, 3 branches inherited DEAD (A209's R.1.1, R.1.2, R.1.3,
each citing `attempts/A209-k5-killer/certs/k5killer209_k5_11_interior_Y0202.json`), 4 start nodes (R.1.4 from its own
snapshot; R.1.5, R.2, R.3 from an ancestor snapshot + 1 step) -- the tree no longer spends its wall on the first three
hours A209 already paid for.  The kills stay live DURING the run: every child the coarse tree branches to has its path
key checked against the merged dead set (`tree211.child_path`), so a branch A205's extended tree or A207 / A208 / A210
closed at ANY depth is recorded `INHERIT` with its source certificate instead of being run.

**On the page and in the row.**  Inherited branches are drawn GREY in the tree table with the campaign, the rule and
the certificate path (`fig211.side`, `fig211.node_note`); the result row carries `inherited_dead` / `inherited_alive`,
`inherit_sources` (one entry per inherited kill with its certificate) and `start_nodes` / `start_runs`.

## 5. Lemma ROLE-SPLIT -- bisecting a WIDE named role at an undecided leaf (2026-09-12, A211c)  [T]

The PI (19:40) on the pad-0 leaf `R.1.4.2.2s` of k5_11_interior_Y0202: *"Why does this case list 'next lever' as lp on
the node instead of no-room?  it's got 5 pins and 5 named nodes that cover a huge chunk of the box."*  Two prices were
found.  (i) the tree SKIPPED no-room there by a once-per-k rule -- backwards, since a child's boxes are SMALLER and its
cores therefore LARGER, so an UNDECIDED parent says nothing about the child; no-room now runs at EVERY fully named leaf
(a node-level flag).  (ii) On that leaf no-room is UNDECIDED anyway, and the reason is width, not coverage: F4's box
spans 0.9 in y with tilt 0-90 and F1's 0.4 x 0.35 with tilt 3-66, so their K' (the core, A132) is EMPTY -- the ten
squares cover the container in the UNION sense only, and every core-based test (no-room's bisection, the mutual clip,
rule CC's band) sees nothing.  The lever is to make the boxes narrow enough that the cores reappear.

**Lemma ROLE-SPLIT.**  Let N be a node of the clip tree (Lemma CT) carrying a role r whose current pose set is the union
of its pieces, and let the hull of those pieces be the box (x0, x1) x (y0, y1) x (t0, t1) in (centre, tan(tilt/2)).  Fix
one coordinate u in {x, y, t} and a value m with u0 <= m <= u1, and let
    N_lo = N conjoined with "the pose of r has u(r) <= m",      N_hi = N conjoined with "u(r) >= m".
Then N is DEAD iff N_lo and N_hi are both DEAD.  *Proof.*  Every genuine packing satisfying N gives r a definite pose,
whose coordinate u is a real number, so u <= m or u >= m: the disjunction is exhaustive (the two cases overlap on
u = m, which only makes each child weaker).  Soundness of the child's state: the child's pieces are the parent's pieces
intersected with the halfspace {u <= m} (a position coordinate: the rect clipped, a piece disjoint from the halfspace
dropped; the tilt coordinate: the sub-bin [b0, b1] replaced by [b0, min(b1, m)], the piece dropped when b0 >= m), so
the union of the child's pieces contains every pose of r satisfying the child's hypothesis, i.e. the child's pose set
is a SUPERSET of the truth under its hypothesis -- which is all A204's cascade needs (it only ever clips and kills by
sound necessary conditions).  The union of the two children's pose sets is the parent's, so nothing is lost.  []

**Where it is applied and how it is steered (a heuristic; soundness does not depend on it).**  At a fully named leaf
where no-room ran and did NOT kill (rule (b) of s.2 S5 returned UNDECIDED, or its pockets could not be branched), and
after the cheap rules (a)-(d), the tree picks among the non-pin roles those that are WIDE --
    position extent max(x1 - x0, y1 - y0) > 0.25   or   tilt range > 30 degrees --
preferring a role whose core is EMPTY (`pg.obst[r] is None`, the A178 semantics for a K' that `polycore.build`
refuses), then the widest such role (the extents scored against their own gates, 0.25 and 30 deg), and bisects its
WIDEST dimension at the MIDPOINT (the exact rational midpoint of the t-interval for a tilt split).  Each child is a
coarse node again: the coarse cascade round, then the leaf rules from the top, no-room included.  The recursion stops
when the children decide (DEAD, or a kill by any leaf rule), when the role has already been split
`RSPLIT_CAP = 4` times along the path, or when no role is wide.  Splitting is a BRANCH step like any other: it is
recorded in the node's path key as `("rsplit", role, dim, m, side)`, so Lemma INHERIT (s.4) applies to it unchanged --
a split child whose path a prior certificate closed is inherited DEAD, and a certificate written here can be inherited
later.  The tree's depth cap counts only the row / NS / pocket steps (a split is charged to its own per-role cap), so
splitting cannot be starved by the depth cap nor run away past 4 per role.

**A211f correction (2026-09-14): that inheritance did not actually work, and the failure was loud.**  A role split is
recorded like every other branch -- `branch_slot` = the role, `branch_rows` = one entry per branch -- but its entry is
a printable LABEL (`"t<=53.1301"`), not a list of row indices, and the exact split lives in the parent's `rsplit`
record (role, dim, `m` as an exact rational string) instead.  `inherit211.branches_of` read the label as a list of
rows, so `list("t<=53.1301")` became ten one-character "rows" with `kind: "pair"`, the merged path key of a split
child was a tuple of characters rather than `("rsplit", role, dim, m, side)` -- so a split branch closed by a prior
certificate was NEVER recognised as the same hypothesis -- and `startload211` handed the ten characters to
`tree205b.apply_branch`, which indexed `pg.cells` with a string and raised
`TypeError('list indices must be integers or slices, not str')`.  On k5_11_interior_Y0036_D07 that, and nothing
geometric, is why the page stayed ALIVE: two of its five start nodes (R.1.4.3.1.2, R.1.4.3.2) could not be loaded in
either of A211e's runs.  `inherit211.rsplit_branch` now rebuilds the branch from the parent's `rsplit` record with
exactly `tree211.step_key`'s key, `startload211.apply_step` applies it with `rsplit211.apply_rsplit` (an empty half
raises, and the start node is then left undecided rather than guessed), and `code/test_inherit211.py` pins it: the
merge over every page's certificates on both pads, with every replay step checked against what the appliers accept,
and `--load` loading every start node whose path carries a role split.

**A220 addendum to the RULE ORDER (2026-09-14, flag-gated, OFF by default).**  Rules (d') and (e) can be swapped at a
fully named leaf: with `A220_EXACT_FIRST` set (`1` always, `small` only when the role the split would bisect has max
position extent < 0.25) the tree runs ONE exact cascade round under a cooperative deadline (`A220_BUDGET`, 45 s;
`tree206.budget_cascade`) BEFORE Lemma ROLE-SPLIT, records a kill as this node's `x` record exactly as (e) does, and on
a timeout keeps the shrinks, restores coarse mode and falls through to (d') as today.  With `A220_NOROOM_INHERIT` set,
rule (b)'s cap is shortened to `A220_NOROOM_CHILD_CAP` (25 s) at a child whose nearest ancestor's no-room already ran
out its cap UNDECIDED and whose role boxes have not shrunk by more than 50 % since (a terminal m = 1 pocket child keeps
the full cap), with the budgeted exact round run first.  Soundness: notes/exact_first.md s.2 Lemma BUDGET (a prefix of a
sound clip chain is sound; an interrupted fixed point writes nothing back) and s.4 (a cap is a budget, never a claim) --
both are cost decisions of the same kind as S2'', and nothing about ALIVE or DEAD changes.  With the flags unset this
file's rule order is what runs, unchanged.  The measurement: `attempts/A220-exact-first/results/bench220.md`.
