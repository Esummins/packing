# A209 -- the k5 killer: one composed chain over every alive non-trump5 node

The directive is the PI's (2026-09-12): *"we had a system to kill every remaining non trump5 node"* -- compose it, do not
reinvent it.  Labels: [T] proved, [S] supported, [M] measured, [C] open.  Every stage is a proven campaign's code COPIED
into `code/` (A206 at df5aebc9: `poly204*`, `tree205*`, `tree206*`, `load206`, `fig204/5/6`; A207 at 7db40795: `tree207`,
`clip207`, `slotmap207`) and imported unchanged; A203's `fast30.Stage0`, A198's `fastprop`, A200's `quick200`, A189's
`noroom189`, A171's `multibox` are imported READ-ONLY.  The new modules: `load209` (the page loader over both populations
and the census), `stage209`, `tree209` (the composition), `run209` (the runner), `worker209.sh`, `fold209`, `progress209`,
`mkqueue209`, `fig209`, `scratch/audit209.py`.

## 1. The chain as run (per node, per pad: g1 = the page's window first, pad 0 second)

0. **Stage 0** = A202's closed-form layer + A203's CSP (`fast30.Stage0`, <= 30 s): cached from A203's / A202's certificate
   when it exists (the gallery pages), else computed on the record and written as `certs/csp209_<nid>_<pad>_s0.json`.
   DEAD here is `[C: closed-form trace]` (A203's label).  The start of the tree = H's clipped box, the forced slots and H's
   alive units (poly204.load_start / stage209.start_of).
1. **A204's polygon-clip cascade** to the fixed point at every node (per-piece K', lonely clip, forced meeters
   instantiated) -- inside every node of the tree.
2. **A205's clip tree** (Lemma CT with the fresh-table proviso, bar-anon, the sharp round) with **A206's Rule NS**
   (MAX_FRAC 0.5) and **A207's basin clip** (`TreePage207`: every non-pin role's pieces and every anonymous row minus
   the basin box of every FULL slot with a certified basin covering the window -- `results/basin207.jsonl`, read-only:
   k5_16 TR(1,0) r_c 0.03 / r_t 3 deg, k5_11 BL(1,1) r_c 0.06 / r_t 3 deg; pad 0 uses no basin: the basins are stated on
   the window), and at every ALIVE leaf with >= 9 roles **A208's no-room leaf** (s.2) -- pockets branched on at k = 9.
   Wall 3,600 s per pad per node, depth cap 5, node cap 300, 3 cascade rounds a node.  The pad-0 tree is skipped when the
   g1 tree is DEAD (the node is killed; pad 0 is s0-only).  The pad-0 verdict is printed beside the window verdict on every
   page.
3. Nothing slower (no LP).  Survivors are listed with their leaves' state and the next lever (results/progress.md, the
   report).

**Inherited kills [T].**  A209's root at (page, pad) is the same hypothesis as A206's whole-tree root there (the same
A203 start file) with MORE clipping (the basin clip), so A209's root state is a subset of A206's.  A depth-1 branch of
A206's run -- the hypothesis "row(s) R at slot p" on the root -- whose whole subtree is DEAD (no ALIVE node under it) is
therefore DEAD as a branch of A209's root with the same (p, R): `tree209.Tree209.on_path / undecided` record it as DEAD with
clip `A206-CLOSED`, naming A206's run, branch and certificate; it is A206's kill (audited by A206), not re-run.  Only the
top level is inherited, and only from runs of mode "tree" on the same pad and start.

## 2. The no-room leaf and Lemma POCKET (any n)  [T]

At an ALIVE leaf with k >= 9 roles (5 pins + H + >= 3 instantiated meeters, all as PIECES) the roles' hull BOXES are
handed to A189's `noroom` (Lemma 1: the free square bisected against the roles' cores K'(box); a core computed from a box
is contained in the core from the box's pieces, so the residue is a SUPERSET of the true one: sound, weaker).

* k = 10 (m = 1): A189's full budget (the bisection, then the pocket LANE cover): DEAD when every pose of a free unit
  square meets some core, or when the pocket LANE sum is 0 -- clip `NOROOM`.
* k = 9 (m = 2): the bisection and the pocket cover P_1..P_r of the residue's CENTRES (A189 `pockets_of`, a union of
  axis-aligned rectangles with margin containing every open piece's centre rectangle), no lane cover.  **Lemma CN** (A200):
  two distinct unit squares' centres are >= 1 apart in l-inf, so a group of pockets whose union has l-inf diameter < 1
  holds at most ONE centre.  With the pockets grouped greedily into such groups (`tree209.cn_groups`; the bound is
  claimed only when every group has diameter < 1), #groups < m is DEAD -- clip `NOROOM-CN`.

**Lemma POCKET.**  Let N be a node (pins, H, roles F_1..F_k as pieces, all distinct squares of the packing) with m >= 1
free squares left, and let P_1..P_r be axis-aligned rectangles whose union contains the centre of every FREE pose (a
pose inside the container whose interior misses every role's core).  Then N is DEAD iff every node N_j = N + "a free
square G, distinct from every role, has its centre in P_j" (j = 1..r) is DEAD.
*Proof.*  Every packing of N has a free square G (m >= 1) distinct from the roles; its interior misses every role's
core (A132: a role's core lies inside every pose of the role, and G is interior-disjoint from the role's square), so its
pose is FREE and its centre lies in some P_j: the packing is a packing of N_j.  Conversely each N_j's hypothesis implies
N's.  []  Branch j instantiates G as a role with pieces P_j (clipped to the container's centre range) x [0, 90] in four
tilt sub-bins -- a superset of G's poses (sound), not cell-bound (`role_cell` -1: the anonymous count loses one square,
exactly as A204's FC-instantiated roles), named at no slot (its option rows include the empty row) -- then A204's cascade,
and the tree recurses (`expand`): the leaf reached has k = 10 and the no-room leaf with the full budget runs there.  The
pocket branches are taken only at a FULLY NAMED leaf (A205's stop with no soft pair left), under the depth / node caps.

## 3. Populations, order, bookkeeping

* The 22 alive k5 gallery pages (docs/shadows/STATUS.md), k5_11 first: `code/queue_gallery.txt`.
* The k5 frontier: `load209.census()` = A156 `state156`'s rule over A57's `tree_k5_*.jsonl` (ALIVE / FAIL rows, the
  STRONGEST verdict per id) minus every id a supersession ledger (A137 / A96 / A149 / A209's own) or an ancestor's kill
  closes (Lemma K1) and minus the killed gallery pages; nid = the id (G1 family) or id`__L1` (the L1 family: the same id is
  a different node there, A137 C.3); a row without a record file is rebuilt from its jsonl row (H = its box, the pins =
  the family's NO record's).  Deepest-first within a tree: `code/queue_frontier.txt` (303 nodes at the start).  The
  worker re-checks closure before every node.  Price: after the first 20 frontier nodes `progress209` writes the mean /
  median seconds per node and the projection over the remaining census into results/progress.md and `logs/STOP` when the
  projection exceeds 400 CPU-h (the workers exit).
* Every g1-pad kill is folded by `fold209` into `results/superseded_by_k5killer_A209.jsonl` (the ledger format of A137 /
  A149: id, applies_to_tags = the tree, prior verdict retained, `closes_subtree` = the alive descendants Lemma K1 closes);
  A57's own files are never written.  The status gallery's block (7q) collects the kills.
* Audits: `scratch/auditor209.sh` samples every DEAD leaf (not the inherited ones) with `scratch/audit209.py` = A206's
  audit206b (poses inside the parent's snapshot pieces, the exact meets test, FC kills need two meeters, the cap-1
  two-meeter criterion) extended to NOROOM kills (a refutation needs m mutually disjoint free squares beside the
  configuration) and BASIN kills (a refutation needs a configuration with every role outside the basin boxes).
