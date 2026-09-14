# A211e -- COARSE CORES at internal nodes (PI, 2026-09-14 11:00: "cut early, memoize, or go coarser, aka do less work").
Opus. LAUNCH-AND-EXIT.
A211d's profile: 67% of a run is MBox.rebuild in kmode "pieces" (the exact intersection of per-piece cores, 810
rebuilds x ~1.2 s, exact rational arithmetic).  The library also has kmode "union" (A171/A132: one certified polygon on
the union hull of the pieces -- sound, forgets the far-side growth), which the coarse tree never uses (KMODE = "pieces"
in coarse211.py).  At a coarse internal node that precision is wasted; per-piece cores belong only to the exact leaf
cascade.
1. KMODE "union" at coarse internal nodes (set_coarse(True)), "pieces" at the exact leaf cascade (set_coarse(False));
   a smaller certification grid at coarse nodes (n_grid 97 -> 33 or whatever the union build accepts; the core only
   gets SMALLER = still sound) -- state the soundness in notes/coarse_tree.md (union-mode K' is a subset of the true
   core: the library's own guarantee; a coarse node's kills stay valid, its ALIVE means "branch further").
2. The coarse cascade: one pass only at internal nodes (confirm); the exact leaf cascade stops after a pass that
   removed < 0.1% (confirm the existing stop) and never starts once the wall is spent (done).
3. Re-profile on k5_11_interior_Y0202 pad 0 (isolated dirs as A211d did; before = A211d's after-run): per-stage table,
   nodes reached, kills within the 900 s wall, per-node seconds; the certificates MAY differ now (coarser cores at
   internal nodes) -- report what changed (kills lost / gained inside the wall) honestly.  Also time one frontier node.
4. Commit with explicit pathspecs; the workers pick it up per node -- do not restart them; never touch A212 / the k0
   cascade.  Report once and EXIT.

## RESULT (A211e, 2026-09-14 09:45) -- k5_11_interior_Y0202, pad 0, wall 900, isolated cert / results / --no-fig

Profile: `logs/profile/coarse_k5_11_interior_Y0202_zero.{prof,log}`; baseline = A211d's after-run
`logs/profile/after_k5_11_interior_Y0202_zero.{prof,log}` (same page, same wall, same machine settings: one process,
BelowNormal, BLAS pinned).  Code: `coarse211.KMODE` = "union", `coarse211.NGRID` = 33 (both overridable by
`A211_KMODE` / `A211_NGRID`), `coarse211.grid_rebuild` the ladder union-33 -> union-97 -> pieces-97, soundness S2'
in notes/coarse_tree.md.

BY STAGE (cProfile cumulative, the same functions in both runs; before 902.1 s / after 908.2 s):

| stage                                    | before |   %  | after  |   %  |
|------------------------------------------|-------:|-----:|-------:|-----:|
| coarse fixed point (`coarse_fixpoint`)   |  545.3 | 60.5 |  118.0 | 13.0 |
|   ... per coarse round                   |   77.9 |      |    7.9 |      |
| no-room leaf (A189, `noroom_at`)         |  310.9 | 34.5 |  749.2 | 82.5 |
|   ... `build_node` / `bisect_free`       | 172.9 / 124.9 |  | 344.7 / 386.1 |  |
| option table (`build_options`)           |   24.4 |  2.7 |   28.1 |  3.1 |
|   of which ROLE-REACH                    |   16.8 |  1.9 |   16.2 |  1.8 |
| everything else (load, INHERIT, CC, I/O) |   21.5 |  2.4 |   12.9 |  1.4 |
| -- the primitives --                     |        |      |        |      |
| `MBox.rebuild` (K')                      |  566.5 | 62.8 |  244.9 | 27.0 |
|   `pieces_poly` (A172, per-piece)        |  517.6 | 57.4 |  202.4 | 22.3 |
|   `union_pc` (A171, union hull)          |    0.0 |      |   18.1 |  2.0 |
|   `polycore.build`                       |  328.8 | 36.4 |  147.5 | 16.2 |
|   `certify_verts` / `intersect_frac`     | 136.9 / 83.4 |  |  48.7 / 28.3 |  |
| `_clip_rect_obstacle`                    |  291.4 | 32.3 |  591.1 | 65.1 |

The coarse round is 10x cheaper per node (77.9 -> 7.9 s); the 202 s of `pieces_poly` that remain are A189's OWN
`multibox.normalise` inside no-room, which runs in kmode "pieces" and is deliberately untouched (it is a KILL rule and
wants the strongest core).  The budget therefore moves wholesale into no-room and into the clip itself: the weaker K'
removes less per pass, so the fixed point no longer stops on the 0.1 % rule after one mutual pass (passes 1 -> 2) and
270k obstacle clips run where 94k did.  The ladder never had to fall back: `grid_rep` = 650 coarse builds, 0 grid
fallbacks, 0 per-piece fallbacks, 870 exact-mode builds.

NODES AND KILLS INSIDE THE SAME 900 s WALL

| run     | nodes | depth | dead / alive leaves | kills in the tree |
|---------|------:|------:|---------------------|-------------------|
| before  |     4 |     2 | 7 / 2               | 1 (NOROOM at R.1.4.2.2.1.1) |
| after   |     8 |     3 | 10 / 1              | 4 (NOROOM at R.1.4.2.2.1.1.1/.2 and R.1.4.2.2.1.2.1/.2) |

Honestly: one kill was LOST and four gained.  The weaker coarse core cost the kill at R.1.4.2.2.1.1 -- no-room there
is now UNDECIDED (139 s, "pocket LANE sum does not beat 1") where the exact per-piece cores killed it -- but the node
cost 24.6 s instead of 214.2 s, so the tree bisects it (Lemma ROLE-SPLIT on F3) and BOTH children die by NOROOM.  The
sibling R.1.4.2.2.1.2, which the baseline reached only at the wall and left ALIVE, is likewise split and both its
children die.  So the whole R.1.4.2.2.1 subtree is CLOSED inside the wall where the baseline closed half of it, and
the only leaf still alive at the wall is R.1.4.2.2.2, which neither run ever started.  Per node: 12.3 / 17.6 / 24.6 /
23.9 / 20.3 / 18.5 / 23.5 / 15.0 s (before: 89.0 / 133.0 / 214.2 / 153.9).

WHAT CHANGED IN THE CERTIFICATES.  Same schema, same rules, same verifier strings.  (i) `cfg.coarse` now carries
`kmode: "union", n_grid: 33`, and run211 prints `grid_rep` beside A211d's cache report.  (ii) In every INTERNAL node's
snapshot the per-role `kprime` is now the union-hull polygon at n_grid 33 instead of A172's per-piece intersection --
a subset of it (S2'), so the polygons are smaller and the `kept` fractions rise (root node: H 1.048 -> 1.0,
F3 0.999998 -> 3.049, F4 0.994 -> 2.653 of the pre-rebin volume, i.e. the coarse units survive where the exact cores
used to cut them).  (iii) The KILLS' certificates are unchanged in kind: all four are A189 no-room on the role boxes,
and no-room builds its own node in kmode "pieces" -- no kill in this campaign is proved against a coarse core.  The
exact leaf cascade (S5 (e)) is untouched; it did not run on this page (no fully named leaf reached it inside the wall).
A field-by-field diff against A211d's own certificate is not possible: that run wrote to an isolated cert dir that was
not committed, so the baseline here is its LOG (verdicts, per-node seconds, kills) plus its `.prof`.

CONFIRMED, NOT CHANGED.  The coarse round is ONE cascade round (`run211.py --rounds` default 1, `poly204b.run`
max_rounds; the round_times of every internal node show `round: 1`).  The exact leaf cascade keeps A205's early stop
(`poly204.fixpoint`: a mutual pass that moved < 0.1 % of the volume ends the loop -- `coarse_fixpoint` carries the
same test), and `tree211.leaf_rules` still leaves the leaf undecided rather than starting the exact cascade once the
wall is spent (A211d's change, commit 2db5a295).

## ONE FRONTIER NODE -- k5_11_interior_Y0036_D07, pad 0, wall 900 (the same page run both ways)

`logs/profile/coarse_k5_11_interior_Y0036_D07_zero.log` (A211e) against
`logs/profile/base_k5_11_interior_Y0036_D07_zero.log` (the same code with `A211_KMODE=pieces A211_NGRID=97`, i.e. the
pre-A211e node), one process, sequential.

| run    | seconds | nodes | depth | dead leaves | node cascade: sum / mean / max | kills |
|--------|--------:|------:|------:|------------:|-------------------------------:|-------|
| before |   548.4 |    24 |     2 |          20 |      290.8 / 12.1 / 38.3       | 5 EmptyBox, 2 COUNT, 3 NOROOM, 2 CC, 1 FC |
| after  |   797.9 |    51 |     3 |          38 |      221.8 /  4.4 /  8.2       | 14 EmptyBox, 2 COUNT, 8 NOROOM, 2 CC, 1 FC, 3 S-CLIP |

Both runs end at the SAME verdict: the three startable branches (R.1.4.4, R.2, R.3) all close DEAD, no leaf is left
alive, and the page stays ALIVE for an unrelated reason -- two start nodes (R.1.4.3.1.2, R.1.4.3.2) fail to load with
`TypeError('list indices must be integers or slices, not str')` in BOTH runs.  (That loader bug, not the core, is what
keeps this page open; it is pre-existing and outside A211e.)

The honest trade, in one page: the coarse core makes a NODE 2.8x cheaper (mean 12.1 -> 4.4 s, worst 38.3 -> 8.2 s, and
the total cascade time falls 24 %), but the weaker clip kills later, so the tree needs 51 nodes where 24 sufficed, and
each extra fully named leaf pays A189 no-room in FULL (no-room keeps kmode "pieces").  Net on this page: +45 % wall.
Net on Y0202, where a single node cost 89-214 s and the wall ran out at depth 2: -86 % a node and three more kills.
So the lever pays where the fixed point dominates (deep, wide, expensive nodes) and costs where the tree is already
shallow and the kills come from EmptyBox / COUNT off a strong clip.

NEXT LEVERS (not taken).  (i) Make the coarse core CONDITIONAL -- keep it while the node's fixed point is expensive
(pieces above a threshold, or the parent's normalise above N seconds) and fall back to the per-piece core on a cheap
node; the knob is already per-call (`grid_rebuild`), so this is a predicate, not a rewrite.  (ii) A189 no-room is now
82 % of an expensive page and runs at twice as many leaves: its `build_node` (172 -> 345 s here) rebuilds K' per piece
from scratch at every leaf and is the next thing to memoise across a parent and its children.  (iii) n_grid 33 was not
tuned -- 17 also certified on every box tested.
