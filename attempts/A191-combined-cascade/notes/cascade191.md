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

## 2. Measurements [M]  (`results/report191.json`, `results/price191.json`; per node `results/run191_l1_104_S2.jsonl`)

**The S2 sweep of l1_104 (64 alive S2 nodes, 01:17 -> 04:21, two processes, cap 300 s; `figs/steps_l1_104_S2.svg`).**
*Verdicts:* **17 DEAD (27 %)**, every one by the v1-style exact-core LP at budget 8 CONVERGED at `tau = 7.000`
(root/D0/S7, S12, S13; D1/S8; D3/S9; D4/S10; D52/S4, S7, S8; D53/S5; D54/S12, S13, S14; D55/S5; D58/S7; D6/S15; D7/S13),
each certified by `verify_case_v5` (PASS) -- and, since NO guard line carried density on any S2 node (`n_active = 0`
on 64 of 64, in both LPs) the v5 certificate is a v1 certificate verbatim (the frozen loader ignores `pbox` /
`guardlines`): root/D0/S12 and root/D0/S13 re-verified PASS under the FROZEN `verify_case.py` (A143, sha
`521cb01f...`; `certs/*_v1.frozen.certify.json`; the rest queued in `logs/frozen191_all.log`) -- so these are
[C] under the frozen chain, conditional on the cascade node's hypothesis (K0-BLOCKED + the tree's case = the roles'
squares have poses in the recorded pieces, hence contain A135's exact cores of their union boxes [T]).  **26 nodes
(41 %) converged ALIVE at `tau = 8.000` = budget exactly** (no slack, as A183.5 found on root/D0/S1); **19 nodes
(30 %) are LP-dead UNCONVERGED kill candidates** (`tau` 7.19-7.58 at the ~240 s v1 cap; minmass ~0.5); 2 sit at
8.000 unconverged.  The v1 `tau` is QUANTISED on this layer: {7.000 x 20, 7.19-7.58 x 16, 8.000 x 28}.
*What kills [F]:* the dead nodes are those whose A183 fixed point has COLLAPSED H -- kept(H) <= 0.022 on 14 of the
17 (6e-7 on root/D0/S12), 0.07 / 0.21 / 0.23 on the other three -- against kept(H) 0.02-0.50 on the survivors:
the polygon + lonely clip pins the three squares, A135's exact core of the union box is then nearly the unit
square (`a` 0.47-0.50), and the LP finds no room for eight more.  The kill is the CASCADE's (the geometry), the LP
is its witness; the guard lines added nothing at S2 (rhs* = s - 3 chords leaves no violated line on the supports).
*The corner no-room leaf:* LANE = None at BR, TL and BL on 64 of 64 nodes (330-433 open boxes at depth 10; every
role provably misses every open corner) -- 0 kills, 29 s per node; the anonymous meeters do not bite at S2.
*The windows LP (budget 11):* `tau` 9.6-10.6, converged on 3 of 64 (root/D0/S7, S12, D54/S12 -- all already dead
by v1; their combined windows + guard-line certificates PASS under v5 too), unconverged at every cap on the rest
(A185: 300 / 1100 / 1526 s on root/D0/S1 -> 10.000; here 75-200 s -> 10.0-10.6); it is the diagnostic, not the verdict.
*Cost per node:* geometry 29 s (max 51), v1 LP 162 s (max 356; the converged ones ~100 s), windows LP 101 s (the
diagnostic; 75 s at wfrac 0.25), certificate 46 s per kill (max 244), wall 305 s mean / 663 s max; the layer 5.4
CPU-h (2.9 CPU-h of it the v1 LP, 1.8 the windows diagnostic, 0.5 geometry, 0.25 certificates).
*root/D0/S1 (the PI's "first kill if it converges"):* NOT a kill -- the v1-style guarded LP converges at
`tau = 8.000` = budget in 136 s (ALIVE, converged); the windows LP is at 10.03 unconverged (A185's leg 3 at cap
1100 s still running at 04:30); corner lanes None.  The first k0 S2 node kills are root/D0/S12 and root/D0/S13.

**The S3 layer [M] (`results/run191_l1_104_S3coarse.jsonl`, `run191_l1_104_S3.jsonl`; `figs/steps_l1_104_S3coarse.svg`, `steps_l1_104_S3fine.svg`; from 04:28, one process each).**  *Coarse, parent-seeded children of the S2 survivors* (H, D, S = the parent's recorded 8/3 fixed point, B = A168's cover box, `polyclip175.make_node(refine=2)` = nsub 4 / refine 2 only): the first cover box B0 (nearest the corner) dies at 4/2 by EmptyBox(B) on 6 of 6 parents tried (37-75 s); the interior children (B95 / B96 of root/D0/S0, S1, S11, S15, S16, S17, S9, root/D1/S0, S9, ...) survive the clip with kept H 0.29-0.64 / D 0.20-0.30 / S 0.11-0.32 / B 0.63 (clip 67-124 s), the corner lanes at TL / BL are None (17-33 s), and the v1-style exact-core LP at budget 7 (FOUR cores) CONVERGES at **tau = 6.000 < 7** on every one that converged within the 240 s cap: 8 DEAD by the LP (v5 PASS; re-verified PASS under the FROZEN verifier, `certs/*_B*_v1.frozen.certify.json`), 1 undecided at cap (root/D0/S16/B96).  *A183's fine (8/3) S3 records* under alive parents (root/D0/S0/B10, B100, B101, B102, ...): 8 of 8 DEAD by the same LP at tau = 6.000 (139-247 s each, v5 PASS, frozen PASS).  Pooled: **22 of 23 S3 nodes DEAD, 1 undecided at cap, 0 alive** -- against A183's 21 % (fine geometry alone) and A184's 5 % (coarse geometry alone): at S3 the exact-core LP with four cores kills where the geometry does not, and the kill is again the cascade's -- tau drops by exactly one unit per pinned square (8.000 -> 7.000 at S2 on the collapsed nodes, 7 -> 6 at S3 on every node tried).  The sample is small and biased to the root/D0 and root/D1 chains (the first parents alphabetically); the per-node cost at S3 is **249 s** mean over the LP-run children (clip 75 + lanes 25 + LP 68 + certificate 3; the windows diagnostic at wfrac 0.2 is 55 s of it).  [F] The S3 layer of l1_104 = the 5,432 A168-alive children of the 47 S2 survivors (8,460 children, 3,028 already dead by A168's own clip): at 249 s each it is **376 CPU-h (23 instance-hours at 16 vCPU)**, and if the sampled rate holds it closes the cell but for the undecided fraction (`notes/price191.md` section 3).
