# A205 -- the CLIP TREE: branch on a forced slot's remaining meeter options, instantiate, cascade, recurse

The campaign is the PI's (2026-09-10 20:35): *"k5_11 Y0202 looks like it'll die if/when clip cascades try to run on
the BR01 meeters."*  A204's cascade only instantiates FORCED meeters (an anonymous cap of 1), so on Y0202 -- where no
slot has a cap and H reaches only BL(1,1) -- nothing is instantiated, the BR(0,1) meeters are never clipped against
anything and the page stays ALIVE at 0.996 of H's box.  The clip tree BRANCHES on the slot's remaining meeter
options, instantiates the meeter as a role in each branch, and runs A204's cascade (memory: geometry-before-LP --
K' grows on the far side and clips the neighbours harder) at every node.  This is A180/A182's assignment tree with
unit propagation and A204's cascade at every node -- NOT an LP tree.  Labels: [T] proved, [S] supported, [M]
measured, [C] open.  Code: `code/tree205.py` (the node), `tree205b.py` (the tree), `run205.py` / `run205.sh`,
`fig205.py` (the page); A204's `poly204.py` / `poly204b.py` / `fig204.py` copied at 57f8d6ae (the copy's only change:
the count is routed through `self.count_search`).

## 1. Lemma CT (the clip tree is sound and exhaustive, any n)  [T]

Setting = A204 `notes/polyclip_cascade.md` s.1: a page (a node of a shadow tree at s0) with pins, the conditioned
square H, the free squares, the forced slots p with widened open boxes B_p+ (Theorem FC, `forced_corners.md`:
two distinct non-pin squares of every packing of the page meet B_p+), and A198/A200's option table -- the cells g of
a grid of side < 1/sqrt2 (Lemma A1: two distinct squares' centres never share a cell), the ROWS (g, S) = the poses of
a free square with centre in g meeting every slot of S that survive the exact tests against every role's K', the
NAMED candidates of p = {H if H is not provably missing B_p+} u {instantiated roles not provably missing B_p+}.

**Node.**  A node N is a hypothesis about the packing: the pins, H's pieces, and a set of instantiated roles
F_1..F_k, each a free square DISTINCT from every other role, carried as pieces, some pinned to a cell (its centre
lies in that cell) and each named at the slots it is hypothesised to meet.  A204's cascade at N (Theorem FC's
forcing, the polygon + lonely clip fixed point on the pieces, the exact reach clips, the caps, the count) is a chain
of sound clips and sound kills of the hypothesis: it returns a node N' with fewer poses whose hypothesis is implied
by N's, or DEAD.

**Branching rule.**  At an alive node let p be a forced slot with named candidates C_p (|C_p| <= 1) and alive rows
g_1..g_m (the cells of p's anonymous option table, after Lemma HC below).  Two distinct non-pin squares meet B_p+;
at most |C_p| of them are named, so at least 2 - |C_p| are ANONYMOUS free squares, each with its centre in some
alive cell of p (the table is a superset of the poses of any free square distinct from the roles meeting p, A200's
semantics):

* |C_p| = 0: two anonymous meeters with centres in DISTINCT cells (Lemma A1) -- the branches are the unordered pairs
  {g_i, g_j}, i < j, minus the pairs whose cell hulls are at l-inf distance < 1/sqrt2 (Lemma A1) and the pairs whose
  rows' pieces are pairwise rule-S-dead (Lemma PC, A203 s.1: no interior-disjoint pose pair exists);
* |C_p| = 1: at least one anonymous meeter -- the branches are the rows g_i singly.

The disjunction over the branches is EXHAUSTIVE (every packing of N's hypothesis realises one of them), and each
branch is a node: the chosen row g is instantiated as a new role F with pieces = the row's reach survivors (a
superset of the poses of a free square with centre in g meeting p: sound), pinned to g (Lemma A1: no other centre
in g, so g leaves the anonymous table -- A198's `cell_role`), named at p (the exact reach clip keeps only the poses
meeting B_p+), distinct from every other role (it is a free square, and a second row of the same branch has its
centre in a different cell).  Hence: **N is DEAD iff every branch is DEAD**; an undecided branch (depth cap, node
cap, wall) leaves N ALIVE.  Unit propagation: a slot with ONE branch is applied without a choice.  []

* |C_p| >= 2, **bar-anon** (the analogue of A204's bar-H): if the count has no cover with p's anonymous cap set to 0
  (without and with the chord rows; the search is exhaustive unless capped), an ANONYMOUS free square meets p in
  every packing of N -- the branches are the rows singly.  Otherwise the slot is not branched on.

**Order.**  The slot with the fewest alive rows (ties: the one H reaches) -- the smallest fan-out.  A node with
nothing left to branch on (every slot's two meeters named, or bar-anon silent) is the **sharp leaf**: one more cascade
round at refine 3 / nsub 8 seeded from its own fixed point (A182's rule: sound, never weaker); if it survives it is
an ALIVE leaf whose next lever is the LP on the node.

## 2. The clips added to A204's node  [T]

* **Rule-S clip between roles (`tree205.TreePage.sclip`).**  H, every instantiated role and the branch's rows exist
  in the packing and are pairwise interior-disjoint (distinct squares of one packing).  A piece of role A with no
  rule-S-compatible piece of role B -- B coarsened to its per-tilt-bin hulls, a superset -- contains no pose of A
  (Lemma PC is a necessary condition on an interior-disjoint pair): dropped.  Re-run with the polygon fixed point
  until nothing moves (<= 3 rounds); a role with no piece left is the kill **S-CLIP**.
* **Lemma HC on the rows (`build_options`).**  A free row whose coarsened pieces are all rule-S-dead against H's (or
  an instantiated role's) coarsened pieces holds no pose of a free square interior-disjoint from that role: the row
  is dead, with every superset row at its cell (their poses are a subset), and the cell leaves the slot's alive
  table (so the unions, caps and Theorem FC see it) -- A203's Lemma HC at the node's resolution.
* **The count with the pair table (`tree205.count_search`).**  A200's capped exact cover search with A203's rule:
  two chosen rows must be rule-S compatible on their coarse pieces (Lemma A1 on the hulls kept); a fixed row (H, a
  role) against a free row likewise.  Infeasible => **COUNT**.
* **S-PAIR.**  A slot with no named candidate and no rule-S / A1 compatible pair of alive rows has no two anonymous
  meeters: DEAD.
* **The empty-reach short-cut (`reach`).**  Down the tree K' only grows and obstacles are only added, so a cell x
  slot-set whose reach was empty at the parent is empty at the child without recomputation; a non-empty parent reach
  seeds the child's (A204's rule).

Every kill is one of A204's primitives or one of the four above; the verdict label is **[C: library clip trace]**
(no verifier clause; the certificate `certs/cliptree205_<nid>.json` holds every node's branch, clip, round, seconds
and its last snapshot; the trace's last 4,000 exact tests).  Settings: coarse (nsub 4 / refine 2), <= 3 cascade
rounds per node (2 in the extended runs), depth cap 4, node cap 200, wall 900 s per pad per page (the brief's row;
EXTENDED runs with their own wall are kept apart: `certs/extended/`, `results/cliptree205_extended.jsonl`, pages under
`campaigns/A205-cliptree/extended/`).

**Cost levers (all sound: each skips or truncates a clip chain, never adds a kill).**  (i) A seeded reach is re-clipped
only against the obstacles that CHANGED since the ancestor (a K' grown by a clip, a new role; the pins' never change)
-- the option table of a child node costs 30-80 s instead of 160-180 s; (ii) the fixed-point loop stops when a pass
moves < 0.1 % of the pose volume (10-pass loops at 5-role nodes were 150 s each); (iii) the S clip re-runs the fixed
point at most once per round and only when a role lost >= 5 % of its pieces; (iv) the option table is skipped when
the fixed point did not move and the last apply changed nothing (the node IS at its fixed point); (v) A189's no-room
leaf is off by default (137-333 s at a 10-role node, never fired).  Two runs of Y0202 were killed for these levers
(`logs/kills.log`, every kill with its branch / clip / round): the v1 standard run at R.2 (R.1 had cost 441 s) and
the v1 extended run at the 10-role node R.1.1.4u (1,384 s); the same node costs 539 s after the levers, a depth-2
node 160 s, an EmptyBox leaf 10-60 s.

## 3. Y0202 (k5_11), the PI's case  [M]

Root (A203's start: H 512 units, no slot forced, H reaches only BL(1,1)): one cascade round, H kept 0.996, nothing
instantiated -- A204's fixed point in 200-266 s.  The tree branches on BL(1,1) (3 rows, H reaches it: rows singly
8 / 13 / 18), then on BR(0,1) (4 rows, H misses it: PAIRS of rows, 5 of 6 pairs rule-S / A1 compatible under 8,
3 of 6 under 13), then on TR(0,0) or TL(1,0).

**The brief's row (wall 900 s, 3 rounds a node; `results/cliptree205.jsonl`, page `cliptree205_k5_11_interior_Y0202.svg`).**
g1: ALIVE at the wall after 3 nodes (root 266 s, R.1 = BL(1,1)<-8 264 s, R.1.1 = BR(0,1)<-{18,21} 451 s; 7
undecided leaves); pad 0 the same (913 s).  A node costs 150-450 s at this setting, so the 900 s wall holds three.

**The extended run (wall 3,600 s, 2 rounds a node, bar-anon + the sharp leaf; `certs/extended/cliptree205_k5_11_interior_Y0202_w3600v3.json`,
page `extended/cliptree205_k5_11_interior_Y0202_w3600v3.svg`; the v2 run before those two levers: `_w3600`).**
29 nodes, depth 3, **14 DEAD / 5 ALIVE leaves** in 3,642 s:

| branch | slot <- rows | verdict | clip / round | s |
|---|---|---|---|---|
| R.1 | BL(1,1) <- 8 | internal | branch BR(0,1) over {18,21} {18,22} {18,23} {21,23} {22,23} | 151 |
| R.1.1 | BR(0,1) <- {18,21} | internal | branch TR(0,0) over 14 / 19 / 23 / 24 | 147 |
| R.1.1.1-3 | TR(0,0) <- 14, 19, 23 | **DEAD** | EmptyBox r1 (the pair leaf in the fixed point) | 36-40 each |
| R.1.1.4(s) | TR(0,0) <- 24, then the sharp round | ALIVE (fully named) | H kept 0.47, F1 0.11, F2 0.034, F3 0.11, F4 0.20 | 497 + 185 |
| R.1.2 | BR(0,1) <- {18,22} | internal | **bar-anon**: an anonymous TR(0,0) meeter is forced; rows 23 / 24 | 208 |
| R.1.2.1-2 | TR(0,0) <- 23, 24 | **DEAD** | EmptyBox r1 | 14, 10 |
| R.1.3 | BR(0,1) <- {18,23} | **DEAD** | EmptyBox r1 | 53 |
| R.1.4 | BR(0,1) <- {21,23} | internal | branch TR(0,0) over 14 / 18 / 19 | 145 |
| R.1.4.1-3 | TR(0,0) <- 14, 18, 19 | **DEAD** | EmptyBox r1 | 9-10 each |
| R.1.5(s) | BR(0,1) <- {22,23}, then the sharp round | ALIVE (fully named) | H kept 0.43, F1 0.12, **F2 0.0029, F3 0.0018**, F4 0.18 | 266 + 201 |
| R.2 | BL(1,1) <- 13 | internal | branch TR(0,0) over 18 / 22 / 23 | 126 |
| R.2.1-3 | TR(0,0) <- 18, 22, 23 | **DEAD** | EmptyBox r1 | 8-15 each: **R.2 closed** |
| R.3 | BL(1,1) <- 18 | internal | branch BR(0,1) over 21 / 22 / 23 | 134 |
| R.3.1 | BR(0,1) <- 21 | internal | branch TL(1,0) over 8 / 9 / 14 | 162 |
| R.3.1.1(s) | TL(1,0) <- 8, then the sharp round | ALIVE (fully named) | H kept 0.15, F1 0.0036, F3 0.019, F4 0.012 | 382 + 241 |
| R.3.1.2(s) | TL(1,0) <- 9, then the sharp round | **DEAD** | FC r1 after the 8/3 round (the sharp leaf's kill) | 166 + 119 |
| R.3.1.3 | TL(1,0) <- 14 | **DEAD** | FC r1 | 59 |
| R.3.2, R.3.3 | BR(0,1) <- 22, 23 | undecided | wall | - |

So the PI's reading holds on the tree's evidence: every branch that instantiates the BR(0,1) meeters and one more
row dies in the FIXED POINT (EmptyBox: a role's every piece meets another role's K' at every tilt of its sub-bin) in
10-60 s -- 11 of the 14 kills -- and the survivors are three FULLY NAMED nodes (pins + H + F1..F4 + one anonymous
square) whose roles keep 0.2-3 % of their seeds (R.1.5s: F2 at 0.29 %, F3 at 0.18 %; R.3.1.1s: F1 at 0.36 %), plus
two branches the wall did not reach.  What kills those three is not more branching (nothing is left to branch on):
the LP on the node (A180's `lp180` with the roles' pieces as A191/A183's cores) or one more level of geometry
(refine 4 on the 0.2 % roles), each a few hundred seconds -- the next lever, priced in section 5.

## 4. Y0839 (k5_16)  [M]

Root: A203's start (H forced at BR(0,1), 412 units), one round, 146 s (the option table skipped at round 2: the
fixed point did not move).  Branch on BR(0,1) (3 rows 10 / 15 / 23; H reaches it: rows singly).  **All three DEAD by
FC at BL(1,0) in round 1** (136 / 151 / 92 s): with the BR(0,1) meeter pinned to its cell (F1 at 10 or 15: its K'
grows next to BL(1,0)'s box; at 23: the union's CN cap 1) BL(1,0)'s anonymous table empties and H provably misses
BL(1,0) -- one meeter at most.  **DEAD at the g1 pad in 526 s**, 4 nodes -- the first kill of Y0839 in the lab (A202 /
A203 / A204 all ALIVE at both pads).  Audit by sampling (`scratch/audit205.py`, `logs/audit_Y0839_g1.log`): 300
admissible H poses over A203's units meeting BR(0,1) x 74-1,044 admissible row poses in the branch cell x 20,793
admissible BL(1,0) meeters over the whole window -- **0 pairwise-disjoint (H, F, G) configurations** on all three
leaves (consistent with the kill; the kills are exact, the audit is the kept rule of A202-A204).

## 5. The table over A204's survivors, the next lever  [M]

`results/report205.md` (one row per (page, pad); the shard `run205.sh` over `pages_todo.txt` keeps appending to
`results/cliptree205.jsonl` and commits after every page; the status gallery's block (7n) collects the kills).  At the
time of the report (32 pages queued, 9 done):

| page | pad | verdict | nodes / depth | dead / alive leaves | s | the kills (branch: clip) |
|---|---|---|---|---|---|---|
| k5_16_Y0839 | g1 | **DEAD** | 4 / 1 | 3 / 0 | 526 | BR(0,1)<-10, 15, 23: FC at BL(1,0) r1 |
| k5_11_Y0308 | g1 | **DEAD** | 3 / 1 | 2 / 0 | 203 | TR(0,0)<-23: FC at BR(0,1) (CN cap 1, H misses); TR(0,0)<-24: EmptyBox(F2) r3 (F2 = the FC-instantiated TL(1,0) meeter) -- A204 had it only at pad 0 |
| k5_11_Y0202 | g1 / 0 | ALIVE wall | 3 / 2 | 0 / 7 | 982 / 913 | (extended: 14 dead, 3 fully named leaves, 2 undecided, s.3) |
| k5_11_Y0130 | g1 / 0 | ALIVE wall | 6 / 3, 5 / 2 | 3 / 4, 2 / 3 | 1,062 / 953 | TR(0,0)<-19 then BL(1,1)<-6, 7: FC at BR(0,1); BR(0,1)<-21: FC at BL(1,1) |
| k5_11_Y0662 | g1 / 0 | ALIVE wall | 3 / 1 | 2 / 2 | 1,080 / 967 | BR(0,1)<-{11,21}, {11,22}: FC at BL(1,1) (H misses; 2 of 4 pairs) |
| k5_11_Y0672 | g1 / 0 | ALIVE wall | 10 / 2 | 5 / 5 | 981 / 968 | BR(0,1)<-21, 22, 23: EmptyBox(F3) r2; BL(1,1)<-6, 11: FC at TL(1,0) |
| k5_11_Y0738 | g1 / 0 | ALIVE wall | 7 / 3 | 1 / 6 | 917 / 934 | BR(0,1)<-17: EmptyBox(F2) after the S clip (round1s1) |
| k5_11_Y0985 | g1 / 0 | ALIVE wall | (report) | | 1,953 total | (see the report) |

Every branch the wall let run on the k5_11 pages dies by FC at the NEXT slot or by the pair leaf; no branch has come
back ALIVE except the fully named nodes of Y0202.  The 900 s wall holds 3-10 nodes; at wall 3,600 s a k5_11 page's
tree reaches depth 3 with 25-30 nodes.

**Audits** (`scratch/audit205.py`, batch `scratch/audit_batch.sh`, logs `logs/audit_*.log`): Y0839 g1 R.1-R.3 and
Y0308 g1 R.1-R.2 -- 0 refutations each (the pair leaf audited through the FC-instantiated role's slot window).

**Price.**  A node at the coarse setting: 10-60 s when it dies in the fixed point, 130-270 s when it survives two
rounds at depth 1-2, 400-540 s at a fully named depth-3 node (the fixed point with five roles is 75 % of it), the
sharp round 120-240 s; a k5_11 page at the 900 s wall 15-18 min for both pads, at 3,600 s one pad in an hour.  The
population so far: 15 (page, pad) rows, 3.7 CPU-h, plus 3 x 1 h of extended Y0202 runs.

**The next lever, in order.**  (1) The LP on the fully named leaves (A180's `lp180` on the node with the roles'
pieces as cores, A191/A183's exact-core construction): the three Y0202 leaves and the R.1.1.4-type nodes of the
other k5_11 pages; (2) the extended wall (3,600 s, 2 rounds) as the row for the k5_11 pages, in a second shard --
the standard row leaves 4-7 undecided branches a pad; (3) the fixed point's cost at 4-5 roles (400 s): bisect only
the roles whose K' changed, and A183's parent seeding of the per-piece K' cache across siblings.
