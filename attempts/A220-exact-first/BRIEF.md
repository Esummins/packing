# A220 -- exact cascade BEFORE role-split at fully named nodes (PI, 2026-09-14 20:05, from k5_16 Y0865).
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits after every shard, PYTHONDONTWRITEBYTECODE=1, <= 2 python processes (BelowNormal via A210's working fix,
affinity 0xFFFF), never touch the running workers (3 run211 + 3 run212 pages are live), frozen verifiers untouched.

## What the PI saw (attempts/A211-coarse-tree/logs/coarsetree211_k5_16_interior_Y0865.log, g1 pad, ALIVE at 1804 s)
Under R.2.3.1.1.2.2.1 (depth 2, 8.3 s) the tree bisects F1's tilt, then F2's, then F5's / F4's (Lemma ROLE-SPLIT,
extents ~0.08 x 0.05 with the FULL tilt range), and every one of the 8 leaves then dies in the EXACT cascade by
EmptyBox in 0.7-18 s ("R....x d5 DEAD EmptyBox [exact]").  The same shape repeats under R.2.3.1.2.p1 and
R.2.3.4.p1: 43 exact leaf cascades, all kills, each reached only after 3-4 role-split levels of 5-16 s coarse rounds.
The PI: "the position of F1 [near-simple, tilt 0.3 deg, nothing near its upper-left / bottom-right; a second meeter
fits only at the corner] should have killed this node in the parent well before this depth.  There are a ton of
computed nodes, each at a similar depth with similar clips, that all should have probably died at the parent."
Cause: tree211.leaf_rules runs (d') ROLE-SPLIT whenever no-room did not kill and a candidate exists (cap 4 per
role) BEFORE (e) the exact cascade, which is last because it once cost 838 s past a wall (A211d).

## Task
1. Flag A220_EXACT_FIRST (env, default OFF; ON = the change).  At a fully named node, before ROLE-SPLIT, run ONE
   exact cascade round under a BUDGET (A220_BUDGET, default 45 s): give tree206.cascade / the clip loops a
   cooperative deadline (a sub-timer on pg.T checked between obstacles / pieces / rows); on timeout keep the sound
   shrinks already made (every step is a sound deduction), restore coarse mode, and fall through to ROLE-SPLIT as
   today; on DEAD record the kill as "x" at this node.  With the flag OFF the code path must be byte-for-byte the
   old behaviour (test: rerun one closed page with the flag off, same node list and verdicts).
   Variant B (also flag-gated, A220_EXACT_FIRST=small): exact-first only when the widest role box the split would
   bisect has max extent < 0.25 (the Y0865 case).
2. BENCHMARK before any claim (memory rule): one runner, all A211d-h/A213/A214 optimisations on, inheritance OFF,
   pad g1, wall 1800 s, on: k5_16 Y0865 (alive, 1804 s), and the closed pages k5_16 Y0500 (1341 s), Y0460 (1297 s),
   Y0249 (1669 s), k5_11 Y0672 (1005 s).  Verdicts on the closed pages must stay DEAD.  Report per page: old time,
   new time (both variants), nodes, exact cascades, role splits, verdict; geometric-mean ratio.
3. If a variant wins (ratio < 0.8, no verdict regression) set it ON in worker211.sh / launch211.sh (new pages pick
   it up; do not restart running workers), record in notes/coarse_tree.md s.5 (rule order), CURRENT.json unchanged.
   If it loses, say so with the numbers.
4. Deliverables: attempts/A220-exact-first/{notes/exact_first.md, results/bench220.md (+jsonl), code/ (patch is IN
   tree211.py / tree206.py, flag-gated)}, registry row, LOG entry.  Report once (<= 15 lines: the table, the
   decision, commits) and EXIT.  Long benchmark runs detached with a resume block.

## Addendum 1b (20:40) -- the no-room cap is the wall
On the alive k5 pages the wall goes to A189/A208 no-room returning UNDECIDED at its ~120 s cap at EVERY child after a
split: Y0402 g1 14 x ~125 s = 1518 s of 1847 (82 %); Y0738 g1 12 gaps = 1153 s (63 %); Y1056 9 gaps = 1044 s
("no-room (k=10, m=1): UNDECIDED in 122 s (2 pockets; pocket LANE sum None does not beat 1)").  Node rounds are 4-8 s.
The A211f no-room memo has build_hits 0 / bisect_hits 0 (obs-level hits only).  Flag A220_NOROOM_INHERIT: (i) parent
UNDECIDED at cap => child cap A220_NOROOM_CHILD_CAP (25 s) unless a role box shrank > 50 % or the child is a terminal
m=1 pocket; (ii) exact-first precedes no-room in that case; (iii) diagnose the 0 memo hits and, if cheap, resume
bisect_free from the parent's undecided leaves restricted to the child's region.  Benchmark adds Y0402 g1, Y0738 g1;
report the wall BY STAGE before/after.
