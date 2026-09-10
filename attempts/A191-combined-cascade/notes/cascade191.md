# A191 -- the combined k0 cascade leaf on the S2 layer of l1_104 (Fable lead, 2026-09-10 00:45 ->)

Successor of A183 (`attempts/A168-cascade-fable/notes/cascade.md` A174-A183); brief `BRIEF.md`.  Labels: [T] proved,
[S] routine given cited items, [M] measured, [F] finding, [C] certificate (every LP kill here is [C under v5 ONLY]:
`verify_case_v5` imports A185's v4, A135's v3 and the frozen v1 with their shas asserted; the frozen chain is untouched).
Records: `results/run191_<cell>_<STEP>.jsonl` (one line per node and leg; the LP result of every node in
`results/lpres_<tag>.json` for warm-started legs), certificates `certs/`, figures `figs/steps_<cell>_<STEP>.svg`,
tables `results/report191.json` (`code/report191.py`).  Agent messaging is broken: everything is on disk.

## 1. The leaf at a node (`code/node191.py`), in the order it runs

**(a) The corner NO-ROOM leaf on every not-yet-placed corner [T].**  At an S2 node the placed corner is TR (D, S);
BR, TL, BL are open.  K0-BLOCKED gives at every corner two DISTINCT interior-disjoint meeters of the open widened box
`B_c^w` (`c = 1 + w`, `w = W0 = 0.0255092`, `cas168.corner_cell`), and no unit square meets two widened boxes (R6:
`s0 - 2(1 + w) - sqrt2 > 0`), so the two meeters of an open corner are not D or S; H is excluded by A161's exact
separating-axis test on its bounding box (`box_misses_cell_exact`: every pose of the box misses the closed cell) --
the leaf is run at a corner only when EVERY role provably misses it, so both meeters are FREE squares (inside the
container, interior-disjoint from every K').  A141's deterministic prefix-code cover of the meeter window (root =
the closed cell dilated by 0.7072 > sqrt2/2 in x and y, tilt [0, 90]: a square meeting the cell has its centre
within sqrt2/2 of it) with the node's roles as obstacles (`roles168.cover`: container / misses_cell (exact) /
witness (a rational point in every pose of the box and of every piece of a role: the box's square IS that role,
which misses the cell) / open at depth 10) and A118's pair test on the open set give LANE(cell) in {0, 1, None}
with LANE >= #{pairwise interior-disjoint free squares meeting int(cell)} (the diagonal of
`pairs_always_overlap_matrix` is the same-box statement).  LANE <= 1 contradicts the two meeters: DEAD.  This is
A189's Lemma 1 with the pocket = the widened corner box and `m = 2` per corner, i.e. the anonymous meeter roles of
the brief consumed where they bite -- in the geometry, not in the LP:

**[T] The anonymous corner windows cannot change the LP.**  Theorem W's window row for a window WITHOUT a core is
(V2): `mu(Q(pi)) >= 1` for every admissible `pi` in the window not meeting a core attached to ANOTHER window.  When
every core is attached (H, D, S here) `E_i = E_0`, and `f = n - r - (m - r_c) = 11 - 9 - 0 = 2 > 0` keeps the free
clause (V1), which already requires `mu >= 1` on every admissible non-exempt pose -- a superset of every window's
poses.  So (V2) for the six anonymous windows is implied by (V1), the covering LP is unchanged, and the budget
`b4 = n - m + r_c = 11` is unchanged.  A window row gains over the free clause only when it is a strict subset of
the non-exempt poses AND the free clause is dropped (`f <= 0`), which needs eleven windows; the two remaining free
squares have no window smaller than the container.  (The distinctness "sqrt2 rule" of FC-count is what makes the
two meeters distinct squares; it is used by the leaf above, not by the LP.)

**(b) The v1-style guarded LP, budget `n - m` [S] (A190's emitter on a cascade node).**  A57's node LP with A135's
exact cores on the roles' UNION boxes (`emit190.ExactHyp`; T23 pairwise-disjointness gate), no windows: the roles
are UNCOUNTED squares (the frozen bridge "some square contains the core"; the certificate binds each core to its
`pbox` = the union box, `point_in_all_poses` on the four corners), A144's guard-line columns on the 8 lines of
largest offline violation on the dual support of a line-free first leg (`lines191`: container sixteenths, each
role's bbox centre / edges +- 1/2, K'(role)'s extreme and mid x / y; `rhs* = s - SUM_j minchord(box_j, l)` exact,
re-derived by the verifier).  It CONVERGES (A183.5 measured 98 s at this budget on root/D0/S1); a converged
`tau < n - m` is certified by A190's certificate under v5.

**(c) The windows LP, budget 11 [S] (A185's WindowsHyp on the recorded pieces: every role windowed, its grown
core attached; `rhs* = s` for every line since no core is unattached) with the same line family re-selected on
(b)'s support, warm-started from (b); a converged kill is certified by the COMBINED certificate (`cert191`:
A185's windows fields + A190's guardlines; the loader of v5 accepts it, `certs/smoke191.json`).  On the S2 layer
this LP sits at `tau = 10.000` unconverged (A185 at caps 300 / 1100; here at cap 150 s on every node), so it is
the DIAGNOSTIC of the sweep, not its verdict: the per-node numbers below say what the cap buys.

**(d) The coarse S3 children (`code/s3_191.py`).**  Child = the parent's recorded fixed point (H, D, S) + B =
A168's cover box (`src`, a sound superset of the clipped pieces), `polyclip175.make_node(refine=2)` = nsub 4 /
refine 2 only (A184 E1: the 8/3 pass changed 1 of 64 S3 verdicts), then (a)-(c) at the fixed point.

## 2. Measurements [M]  (filled as the records land; the tables are `report191.py`'s)

(see section 3 of `notes/price191.md` for the tables and the price)
