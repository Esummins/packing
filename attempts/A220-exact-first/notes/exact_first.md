# A220 -- the EXACT cascade BEFORE the blind split, and the SHORT no-room cap under an undecided parent (2026-09-14)

Labels: [T] proved, [S] supported, [M] measured, [C] open.  The whole change is FLAG-GATED and every flag is OFF by
default: with the flags unset `tree211.leaf_rules` runs exactly A211's rule order and A211's caps (s.5 below is the
equivalence argument, s.6 the measured check).  Code: the patch is in `attempts/A211-coarse-tree/code/tree211.py`
(the two call sites + the flags), `tree206.py` (`budget_cascade`) and `tree209.py` (one optional `deadline` argument);
the benchmark harness is `attempts/A220-exact-first/code/` and the pre-A220 code is kept verbatim in
`attempts/A220-exact-first/base211/` so the flag-off run can be diffed against it.

## 1. The two prices the PI named

**(a) The blind split (PI, 2026-09-14 20:05, from `logs/coarsetree211_k5_16_interior_Y0865.log`).**  Under
`R.2.3.1.1.2.2.1` the tree bisects F1's tilt, then F2's, then F5's / F4's by Lemma ROLE-SPLIT (extents ~0.08 x 0.05
with the FULL tilt range), and every one of the 8 leaves then dies in the EXACT cascade by EmptyBox in 0.7-18 s.  The
same shape repeats under `R.2.3.1.2.p1` and `R.2.3.4.p1`: 43 exact leaf cascades, all kills, each reached only after
3-4 role-split levels of 5-16 s coarse rounds.  The PI: *"the position of F1 ... should have killed this node in the
parent well before this depth."*  The cause is the RULE ORDER: (d') ROLE-SPLIT runs before (e) the exact cascade,
because the exact cascade once cost 838 s past a spent wall (A211d) and was therefore put last.

**(b) The capped no-room repeated at every child (coordinator addendum, 2026-09-14 20:40).**  On the ALIVE k5 pages
the wall does not go into the coarse rounds at all: the node lines cost 4-8 s and the GAPS between a split line and
its child's node line are ~125 s each, i.e. A189/A208's no-room returning UNDECIDED at its 120 s cap.  Measured from
the g1 logs: `k5_16_interior_Y0402` 14 gaps = 1,518 s of a 1,847 s wall (82 %), `k5_11_interior_Y0738` 12 gaps =
1,153 s (63 %), `k5_11_interior_Y1056` 9 gaps = 1,044 s.

## 2. Lemma BUDGET -- a cascade stopped by a clock claims nothing  [T]

Let N be a node and let the cascade at N be run with a DEADLINE: at prescribed points (between rounds, between the
count's slots, every 64 calls of the mutual clip) the run may stop and return "undecided".  Then

  (i) the pose set the node carries when the run stops CONTAINS every pose consistent with N's hypothesis, and
  (ii) a DEAD reached before the deadline is a DEAD of N in the ordinary sense.

*Proof.*  A204's cascade is a chain of sound clips and sound kills (A205 Lemma CT; notes/coarse_tree.md S2), and any
PREFIX of a chain of sound clips is sound -- this is the same fact A205's cost levers (i)-(v) and A211's coarse node
rest on.  Stopping the chain early therefore only keeps MORE poses, which is (i); nothing about a kill reached before
the stop depends on what would have followed it, which is (ii).  The implementation detail that makes (i) hold
literally rather than approximately: `poly204.PolyPage.normalise` copies the clipped pieces out of the `MB.Node` only
after the fixed point RETURNS, so a round interrupted inside the fixed point writes nothing back and leaves
`pg.pieces` / `pg.obst` / `pg.nd` exactly where the last COMPLETED round put them.  []

**How the deadline is implemented (`tree206.budget_cascade`).**  A SUB-TIMER on the node's own trace: `pg.T.wall` is
pulled in to `now + budget` for the duration and restored in a `finally`, so every `T.out_of_time()` the chain
already checks becomes a deadline check (poly204b's round loop, the bar-H count's per-slot loop, quick200's reach
loops), and `MB._clip_rect_obstacle` -- the innermost mutual-clip call, once per obstacle per piece -- is wrapped for
the duration to raise `tree206.Budget` every 64 calls once the deadline has passed.  The wrapper is removed in the
same `finally`; A171/A172/A173's files are never touched, and outside the budget window the library is the library.
Overshoot is bounded by the longest uninterruptible step (one `count_search`, one K' rebuild): seconds, not minutes.

## 3. Rule EXACT-FIRST (flag `A220_EXACT_FIRST`)  [T for soundness, [S] for the ordering]

At a fully named leaf where (a) rule CC, (b) no-room and (c) the basin clip did not kill and (d) Rule NS has no
sliver, A211 bisects a wide role (Lemma ROLE-SPLIT).  With the flag ON the tree first runs ONE exact cascade round
(`set_coarse(False)`, `budget_cascade`, `A220_BUDGET` = 45 s):
  * DEAD  -> the node is closed here, recorded as its `x` record exactly as rule (e) records the exact cascade, with
    the same clip trace and the same verifier clause.  This is the case the PI pointed at: the kill the 8 leaves of
    3-4 blind bisections were going to produce anyway, produced at the parent.
  * undecided or the budget ran out -> coarse mode is restored and the tree falls through to ROLE-SPLIT as before.
    The shrinks the interrupted cascade made are KEPT (Lemma BUDGET (i)), so the split candidates are re-read from
    the tighter boxes -- a role that stopped being WIDE is no longer split at all.
At most one exact-first round per node (`node["exact_first"]`), so the budget cannot be paid twice at one node.
Soundness is Lemma BUDGET plus Lemma ROLE-SPLIT unchanged: both children of a split still cover the parent, and the
parent's pose set is only smaller than it was.  What the rule changes is WHERE the wall is spent, not what ALIVE and
DEAD mean.

**Variant `small` (`A220_EXACT_FIRST=small`).**  Exact-first only when the role the split would bisect is
positionally small -- `max(extent_x, extent_y) < A220_SMALL_EXT` (0.25), i.e. the split would be a TILT bisection of
an already well-located role.  That is exactly the Y0865 case (extents ~0.08 x 0.05, full tilt range) and exactly the
case where the exact per-piece K' has something to say that the coarse union-hull core does not.

## 4. Rule NOROOM-INHERIT (flag `A220_NOROOM_INHERIT`, the addendum)  [T for soundness]

A189's no-room search is capped (`tree211.NOROOM_CAP` = 120 s) and an UNDECIDED at the cap decides nothing.  A211
re-runs it at EVERY fully named leaf -- rightly, since a child's boxes are smaller and its cores therefore larger
(A211c) -- but after a role split the child's boxes are the parent's with ONE half-space cut, so the same search runs
out the same cap again, at ~125 s a child.  With the flag ON:
  (i)  the child's cap is `A220_NOROOM_CHILD_CAP` (25 s) when the nearest ancestor on the live path ran no-room,
       came back not-DEAD, and used up >= 80 % of its own cap, UNLESS the node is materially different -- some role
       box has lost more than `A220_NOROOM_SHRINK` (50 %) of its (x, y, t) volume since that ancestor, or a role has
       been added, or this node is a TERMINAL m = 1 pocket child (Lemma POCKET instantiates an 11th role there and
       the search is a different search).  Then the full cap is used.
  (ii) in that case ONE budgeted exact round (s.3) runs BEFORE no-room, so that the search that follows reads
       SMALLER boxes -- which is the only thing that makes a capped search terminate.
Soundness: a cap is a BUDGET, never a claim.  A shorter search returns UNDECIDED more often and UNDECIDED prunes
nothing (A211 s.2 S5 (b)); the pockets it does return are still A189's certified pockets, and Lemma POCKET is applied
to them unchanged.  So the flag can only make the tree kill LATER, never wrongly -- it is exactly A211f's S2''
argument (a per-node budget predicate, with nothing about soundness depending on it), one level down.

**(iii) Why the A211f no-room memos never hit (`build_hits` 0 / `bisect_hits` 0 on Y0865).**  [M] Not a bug: both
memos are keyed on CONTENT -- `build_node` on the exact role BOXES, `bisect_free` on the tuple of obstacle vertex
sets -- and a child never reproduces its parent's content, because the child runs its own coarse cascade round BEFORE
the leaf rules and that round's mutual clip moves at least one box of every role it can reach.  (The design note
expected the split role's K' to be EMPTY and the others to be untouched; in practice the cascade touches the others.)
Only the OBSTACLE INTERNING (`obs_hits`) survives that, and it does hit.  Resuming `bisect_free` from the parent's
undecided leaves restricted to the child's region is NOT cheap -- A189 returns a residue of free-square pieces, not a
resumable frontier, and A189/A208 are read-only -- so it is left as [C] for a later attempt; the short cap above buys
the same seconds without touching A189.

## 5. Why the flags OFF are the old behaviour  [T]

Every edit is inside an `if`:
  * `tree209.noroom_at` gains one keyword argument `deadline=None`; the budget expression is unchanged when it is
    None, which is what every existing call site passes.
  * `tree211.leaf_rules`, no-room block: with `A220_NOROOM_INHERIT` unset, `cap` is `NOROOM_CAP` and `short` is None,
    so the call is the old call with `deadline=None`.  The two new bookkeeping writes (`self.nr_state[label]`, the
    extra `cap` / `short_cap` keys in the record) are read only by the flagged branch.
  * `tree211.leaf_rules`, ROLE-SPLIT block: the new code is guarded by `if EXACT_FIRST and ...`, an empty string when
    the flag is unset.  The candidate list, `node["rsplit_candidates"]` and the `RSPLIT` return are untouched.
  * `tree211.pocket_branches` records the label of a terminal pocket child in a set that only the flagged branch
    reads.  `tree206.budget_cascade` is a new function, called only from the flagged branch, and it restores both
    `pg.T.wall` and `MB._clip_rect_obstacle` in a `finally`.
  * `run211.py` records the flag values in the run's `cfg` and prints one extra line.
So with the flags unset the module is A211's module modulo statements with no observable effect -- and the running
run211 / run212 workers, which import these files afresh for every page, keep A211's behaviour exactly.

## 6. The benchmark (`code/bench220.sh`, `code/plan_a.txt` / `plan_b.txt`, `code/analyze220.py`)

One runner per lane, two lanes at most, BelowNormal + affinity 0xFFFF (run211's own fix), gated while the lab holds
>= 9 pythons so the six live run211 / run212 workers are never crowded; each job writes its OWN certificate dir
(`results/certs/<tag>/`) and row file (`results/rows/<tag>.jsonl`), so no A211 state is touched, and `--no-fig` keeps
the gallery out of it.  Configs: `off` (this code, every flag unset -- the control), `ef`
(`A220_EXACT_FIRST=1`), `efs` (`=small`), `nri` (`=small` + `A220_NOROOM_INHERIT=1`), plus the equivalence pair
`eqbase` (the pre-A220 code in `base211/`) and `eqoff` (this code, flags off) on the same page, pad, wall and start.
Pages: the PI's `k5_16_interior_Y0865` and the addendum's `k5_16_interior_Y0402` / `k5_11_interior_Y0738` with
INHERITANCE ON (they are ALIVE, so there is no self-kill to inherit and every config starts from the same merged
state); the closed pages `k5_11_interior_Y0672`, `k5_16_interior_Y0249`, `k5_16_interior_Y0460`,
`k5_16_interior_Y0500` with `--no-inherit`, because their own A211 certificates now record them DEAD and a run with
inheritance ON would inherit its own verdict in seconds and measure nothing.  `analyze220.py` writes
`results/bench220.jsonl` + `results/bench220.md`: per row the verdict, seconds, ratio against that page's `off` row,
the node / kill counters, the A220 counters, and the WALL SPLIT BY STAGE (coarse rounds / no-room / exact cascade /
other), plus the geometric-mean ratio per config and the flag-off equivalence check (node list + verdicts).

RESUME (the lanes are detached and outlive the session):
```
nohup bash attempts/A220-exact-first/code/bench220.sh a attempts/A220-exact-first/code/plan_a.txt \
  > attempts/A220-exact-first/logs/lane_a.out 2>&1 &
nohup bash attempts/A220-exact-first/code/bench220.sh b attempts/A220-exact-first/code/plan_b.txt \
  > attempts/A220-exact-first/logs/lane_b.out 2>&1 &
python attempts/A220-exact-first/code/analyze220.py          # the table at any time
```
A job with a marker in `results/done/` is skipped; delete the marker to redo it; `touch attempts/A220-exact-first/
logs/STOP` stops the lanes after their current job.  THE DECISION RULE (from the brief): a variant is turned ON in
`worker211.sh` / `launch211.sh` only if its geometric-mean ratio is < 0.8 with no verdict regression; otherwise the
numbers are recorded here and the flag stays OFF.

**How a winning variant is turned ON** (only after the rule above is met): add the export to the environment line of
`attempts/A211-coarse-tree/code/worker211.sh` (and `launch211.sh`, which the worker inherits), e.g.
`export ... A220_EXACT_FIRST=small` (or `... A220_EXACT_FIRST=small A220_NOROOM_INHERIT=1`).  Only NEW pages pick it up;
the running workers are not restarted, and `CURRENT.json` does not change -- the flag reorders work, it does not change
what a verdict means.

## 7. Status

[M] the numbers as they stand are in `results/bench220.md` (regenerated after every job).  [C] until the geometric
mean over the seven pages is in, no claim is made and the flags stay OFF in `worker211.sh` / `launch211.sh`.
