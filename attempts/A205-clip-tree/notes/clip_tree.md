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

**Order.**  The slot with the fewest alive rows (ties: the one H reaches) -- the smallest fan-out; a slot with two
named candidates is never branched on (its two meeters may both be named).

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
rounds per node, depth cap 4, node cap 200, wall 900 s per pad per page.

## 3. Y0202 (k5_11), the PI's case  [M]

(filled from `results/cliptree205.jsonl` and the certificate; see the report)

## 4. Y0839 (k5_16)  [M]

## 5. The table over A204's survivors, the next lever  [M]
