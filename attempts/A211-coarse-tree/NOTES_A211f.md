# A211f -- loader bug, no-room memo, conditional coarse core (2026-09-14). Opus. LAUNCH-AND-EXIT.
From A211e's report (NOTES_coarse_core.md RESULT):
1. BUG: two start nodes of k5_11_interior_Y0036_D07 fail to load with TypeError('list indices must be integers or
   slices, not str') in both runs (startload211 / inherit211) -- the only reason that page stays ALIVE.  Find it, fix
   it, add a regression test over every page's merge (inherit211 on all certs: 0 load errors), re-run that page.
2. No-room is now 82% of a run: memoise A189's build_node / bisect_free across parent and children (a child's roles are
   the parent's with one changed or one added; the bisection of the free square against unchanged cores is reusable
   -- certificate-identical), and cap its per-leaf cost as A211d did (120 s, once per node).
3. Conditional coarse core: use kmode "union"/n_grid 33 only when the node's cascade round is the expensive part
   (e.g. the parent's round took > 20 s or the role count >= 8); shallow nodes keep the strong per-piece clip (A211e's
   frontier node: +45% wall with the coarse core).  The knob is per call already.
Measure all three on the Y0202 pad-0 900 s run (isolated dirs; baseline = A211e's after-run) and on
k5_11_interior_Y0036_D07; report stage tables, nodes, kills, seconds.  Ops as before (workers untouched, they pick the
code up per node; explicit-pathspec commits; no monitors, no waiting turns).  Report once and EXIT.

## RESULT (A211f, 2026-09-14 11:45).  Commits 380ff7f5, 4cf69f67, 49947875.

A CAVEAT FIRST, because it invalidates half of the obvious comparisons.  Wall seconds on this machine depend on what
else is running: the SAME page, the same tree, the same 26 nodes and the same DEAD verdict took 316.2 s at 10:24
(beside a cProfile'd second run and the lab's own workers) and 106.2 s at 11:31 (two plain processes).  So every
number below that compares two configurations comes from a PAIR launched simultaneously with nothing else of mine
running; the A211d / A211e logs are quoted for shape (nodes, kills, verdicts), not for wall.

### 1. THE BUG: a role split's branch list was read as a list of row indices

`tree211` records a Lemma ROLE-SPLIT node as `branch_slot` = the role and `branch_rows` = `["t<=53.1301",
"t>=53.1301"]` -- one printable LABEL per branch; the exact split lives in the same record's `rsplit` dict (role, dim,
`m` as an exact rational string).  `inherit211.branches_of` had no case for it, so it fell through to the ROW case and
did `list(rows)` on a string: `list("t<=53.1301")` -> ten one-character "rows", `kind: "pair"`.  Two consequences:
  * `startload211.apply_step` sent them to `tree205b.apply_branch`, which does `pg.reach(ci, ...)` and indexes
    `pg.cells` with `"t"` -- `TypeError('list indices must be integers or slices, not str')`.  That is the whole
    reason k5_11_interior_Y0036_D07 stayed ALIVE in BOTH of A211e's runs: start nodes R.1.4.3.1.2 and R.1.4.3.2 never
    loaded.  Nothing geometric.
  * the merged path key of a split child was that tuple of characters, while the live tree's `tree211.step_key` makes
    `("rsplit", role, dim, m, side)` -- so a role split closed by a prior certificate was NEVER recognised as the same
    hypothesis.  Lemma INHERIT silently did not apply to role splits at all.
FIX: `inherit211.rsplit_branch` rebuilds the branch from the parent's own `rsplit` record with exactly `step_key`'s
key, and `startload211.apply_step` applies it with `rsplit211.apply_rsplit` (an empty half raises, and run211 then
leaves that start node undecided rather than guessing -- it cannot happen on a replay, since the loaded pieces are an
outward-padded SUPERSET of the recorded ones).  `inherit211.step_of` (unused) returns None for a child rsplit record
rather than a bogus row key.  notes/coarse_tree.md s.5 records it.

REGRESSION TEST `code/test_inherit211.py` (10 s):

    MERGE   63 pages x 2 pads -> 126 merges, 546 start nodes, 456 replay steps (20 start nodes carry a role split)
    ERRORS  0

and `--load` (149 s) actually runs `startload211.load` on every start node whose path carries a role split:

    LOAD    20 / 20 role-split start nodes loaded

Every replay step is checked against what the appliers accept: row steps must carry integer cell indices, an rsplit
must carry role / dim in {x,y,t} / side in {lo,hi} / an `m` that parses as a rational, a pocket four floats and an
integer row, an ns step a role and a slot, and the kind must be one the appliers know.  Before the fix the test fails
on the two Y0036_D07 start nodes ("row step rows [...] are not cell indices").

### 2. THE NO-ROOM MEMO (`code/noroommemo211.py`; A189 / A208 / A171 wrapped, never edited)

Three pure memos: the compiled `Obstacle` of a K' interned process-wide on (role name, mode, exact vertices) instead
of per box (so A211d's clip memo, keyed on `id(obs)`, and A173's `Bin.radii` cache start hitting across nodes);
`build_node` memoised on (the exact role boxes, s0, nsub, refine) with `MB.EmptyBox` -- a KILL -- cached and
re-raised; `bisect_free` memoised on the node's OBSTACLE CONTENT plus (s, tsub, depth, max_pieces), which is all it
reads, never caching a deadline-stopped run.

CERTIFICATE-IDENTITY CHECK (the real one, not an assertion): k5_11_interior_Y0036_D07 pad 0 run twice, simultaneously,
identical except `A211_NOROOM_MEMO=1` / `=0` (`logs/profile/ab_on_Y0036_D07.log`, `ab_off_Y0036_D07.log`, certificates
in `logs/profile/ab_on/`, `ab_off/`).  Both DEAD, 32 node records each, and a field-by-field diff over every node --
verdict, clip, label, depth, slot, kind, rows, leaf, reason, roles, role_slots, forced_H, kept, snapshot, source_*,
verifier, AND the whole `noroom` sub-certificate (bisect depth / stop / n_open / n_dropped / open_volume /
root_volume / dropped_fraction, pockets, lanes, bound, cn_bound, verdict, reason) -- gives **0 differences** outside
the timing fields (`seconds`, `t`, `round_times`).  `A211_NOROOM_VERIFY=1` additionally recomputes every hit with the
library and asserts.

WHAT IT IS WORTH (same pair): 108.7 s with, 112.9 s without -- **-3.7 %**, same tree, same kills.  Honestly: the two
memos the note asked for NEVER FIRED.  `build_hits 0 / build_misses 5` and `bisect_hits 0 / bisect_misses 5` on
Y0036_D07, 0 / 8 on Y0202: a child's role boxes and its cores never once coincided exactly with its parent's, so the
"bisection against unchanged cores" the note hoped for does not occur on these pages (Lemma ROLE-SPLIT prefers an
EMPTY-core role, but the cascade at the child moves the other roles' cores too).  The entire -3.7 % is the third
memo, the obstacle interning, feeding A211d's clip memo: on identical call counts (195 059 clips) it takes the clip
memo from 20 228 hits to 41 641 -- **+106 % hit rate**.  It is left ON (it pays, and it is free of risk); the two
dead memos are left in place behind the same flag, since they cost one dict lookup and would pay on a page where a
split does leave the cores alone.

### 3. THE CONDITIONAL COARSE CORE (`coarse211.coarse_core_on`, notes/coarse_tree.md S2'')

The coarse union-hull core at n_grid 33 is used at a node iff the PARENT's cascade took more than
`COARSE_SECONDS` = 20 s, or the node carries `COARSE_ROLES` = 99 roles (i.e. never; the note's "role count >= 8" was
measured and rejected -- on Y0036_D07 every node from depth 1 already carries 8-10 roles, so that clause alone just
restores A211e).  A start node's root has no parent and runs with the exact per-piece core.  Soundness is untouched
(S2': both cores are certified subsets of every pose); the choice is recorded per node (`coarse_core` / `kmode` /
`n_grid` in the round report, a `COARSE-CORE` trace test with the parent's seconds and the rule, and the counts in
`coarse211.grid_rep`).  `A211_COARSE_SECONDS` / `A211_COARSE_ROLES` re-run either extreme.

**k5_11_interior_Y0202, pad 0, wall 900, one pair launched together** (`logs/profile/pair_uncond_Y0202.log`,
`pair_cond_Y0202.log`):

| run                                 | wall  | tree nodes | depth | kills | dead / alive leaves | start nodes closed |
|-------------------------------------|------:|-----------:|------:|------:|---------------------|--------------------|
| unconditional coarse core (= A211e) | 932.1 |         12 |     4 |     4 | 10 / 4              | 0 of 4             |
| conditional (A211f)                 | 903.5 |         17 |     4 |    10 | 15 / 1              | 2 of 4             |

The conditional run CLOSES the whole first start node R.1.4.2.2 (every branch DEAD: R.1.4.2.2.1 by two no-room kills
at depth 2 where the coarse core needs four at depth 3, then all of R.1.4.2.2.2 down to depth 4) and then kills the
second start node R.1.5.2 outright by no-room; only R.2 / R.3 are left, and the coarse run never reached either.
A211e's own after-run on this page, for shape: 8 nodes, depth 3, 4 kills, 1 alive leaf, R.1.4.2.2.2 never started.

**k5_11_interior_Y0036_D07, pad 0, wall 900, one pair launched together** (`pair2_uncond_Y0036.log`,
`pair2_cond_Y0036.log`); both runs already have the loader fix, so both close the page:

| run                                 | wall  | verdict | tree nodes | depth | dead / alive leaves | no-room calls               |
|-------------------------------------|------:|---------|-----------:|------:|---------------------|-----------------------------|
| unconditional coarse core (= A211e) | 528.9 | DEAD    |         57 |     3 | 42 / 0              | 19 (3 UNDECIDED at the cap) |
| conditional (A211f)                 | 106.2 | DEAD    |         26 |     2 | 22 / 0              | 5 (all DEAD)                |

**-80 % wall, 2.2x fewer nodes, and the same verdict** -- A211e's measured "+45 % on a shallow page" is not just
removed, it is inverted: the strong per-piece clip kills at the node (EmptyBox / COUNT / CC / FC) before no-room is
ever reached, and when no-room does run it kills instead of burning the 120 s cap.

THE PAGE ITSELF.  k5_11_interior_Y0036_D07 pad 0 is now **DEAD** -- every branch closed, 0 alive leaves -- where
A211e left it ALIVE in both runs.  The first run after the fix (`a211f_k5_11_interior_Y0036_D07_zero.log`) reads:
the two previously unloadable start nodes load (`RSPLIT F2 t>=53.1301 (29 pieces)`, `RSPLIT F1 t>=53.1301 (28
pieces)`) and BOTH die by no-room on the bisection alone, 11 s and 8 s.  This is a pad-0 kill: s0-only,
WINDOW-PENDING.

### 4. THE STAGE TABLE (cProfile, k5_11_interior_Y0202 pad 0, wall 900, isolated dirs, --no-fig)

`code/profstage211.py <a.prof> <b.prof> ...` prints it; nested wrappers (rebuild / clip / build_node / bisect_free)
take the OUTERMOST, not the sum.  `after_` = A211d's run, `coarse_` = A211e's, `a211f_` = this one (which also
carries A213's integer K' build -- that is why `polycore.build` collapses; it is not an A211f effect).

| stage                        | A211d  |   %  | A211e  |   %  | A211f  |   %  |
|------------------------------|-------:|-----:|-------:|-----:|-------:|-----:|
| TOTAL                        |  902.1 |      |  908.2 |      |  908.6 |      |
| coarse fixed point           |  545.3 | 60.5 |  118.0 | 13.0 |  118.0 | 13.0 |
| no-room leaf (A189)          |  310.9 | 34.5 |  749.2 | 82.5 |  746.1 | 82.1 |
|   ... build_node             |  172.9 | 19.2 |  344.7 | 38.0 |  122.0 | 13.4 |
|   ... bisect_free            |  124.9 | 13.9 |  386.1 | 42.5 |  263.8 | 29.0 |
|   ... lane                   |   13.0 |  1.4 |   18.3 |  2.0 |  360.2 | 39.6 |
| option table                 |   24.4 |  2.7 |   28.1 |  3.1 |   33.8 |  3.7 |
|   ... ROLE-REACH             |   16.8 |  1.9 |   16.2 |  1.8 |   22.2 |  2.4 |
| MBox.rebuild (K')            |  566.6 | 62.8 |  245.2 | 27.0 |   46.6 |  5.1 |
|   ... pieces_poly            |  517.6 | 57.4 |  202.4 | 22.3 |   42.7 |  4.7 |
|   ... polycore build         |  328.8 | 36.4 |  147.5 | 16.2 |   38.6 |  4.2 |
| _clip_rect_obstacle          |  292.5 | 32.4 |  593.3 | 65.3 |  448.9 | 49.4 |

The shape of the budget has moved completely: K' is no longer the cost (5 % -- A213's integer build plus the memos),
the fixed point is 13 %, and the page is now no-room-bound, with the LANE cover (A141/A161's discharge inside
`chordlane`) the single biggest item at 40 %.  The next lever on an expensive page is the lane, not the core.

### 5. THE 120 s CAP

`tree211.NOROOM_CAP` = 120 s, once per node (`node["noroom"]` guards the second call), was already in place from
A211d/A211e and is confirmed working: every UNDECIDED no-room in both Y0202 runs stops at 120-124 s.  The ONE leak is
that the cap is a `total_deadline` passed to A189, and `build_node`'s `normalise` is not deadline-aware -- the first
no-room of a Y0202 run measures 197 s, all of the overshoot inside the node build.  Not taken here (it needs a
deadline hook inside A171's normalise, i.e. a change to a read-only library).  A second, smaller leak: `noroom_at`
computes `max(60.0, min(900.0, wall_left - 30))`, so a node reached with the wall already spent still gets 60 s.

### 6. WHAT IS NOT DONE

(i) build_node / bisect_free memoisation is implemented and certificate-identical but never hits on these two pages;
either a cheaper equivalence (a per-ROLE core memo feeding a re-derived node, rather than the whole-node key) or a
different split heuristic would be needed to make a child share its parent's bisection.  (ii) The lane cover is now
40 % of an expensive page and has never been profiled.  (iii) `COARSE_SECONDS` = 20 s was chosen from A211d/A211e's
per-node seconds (Y0202 89-214 s, Y0036_D07 mean 12.1 s) and not tuned; with the machine idle a Y0202 node now costs
1-9 s, so the threshold is measuring the MACHINE as much as the node -- a load-independent proxy (piece counts, role
widths) would be a better predicate.
