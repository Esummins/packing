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
with the LONELY clip omitted, refine = 1 (A204: 2), at most 2 mutual-clip passes (A204: up to 10), and K' rebuilt per
piece (A172's certified per-piece intersection; KMODE "union" = A171's union-hull polygon is the box-only fallback,
also certified, weaker).  Every pass is one of A171/A172/A173's certified clips (container clip, tautologous split,
mutual clip against K'); any PREFIX of a chain of sound clips is sound (A205's cost levers (i)-(v) rest on the same
fact).  Omitting the lonely clip and the basin clip at internal nodes keeps more poses.  The rule-S clip and Lemma HC
on the rows (A205 s.2) are unchanged and cheap.

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
list certified exhaustive by (b).  A start node whose snapshot was written at the piece cap is REFUSED (load206's
rule) and the page falls back to the plain root run: never a silent subset.

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
