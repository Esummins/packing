# A221 -- make the no-room LANE cover decide the k5 pockets (PI, 2026-09-14 21:00: "apply that cover, then run the
# new toolkit against the remainder; we should be able to close out these nodes pretty quick").
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits per shard, PYTHONDONTWRITEBYTECODE=1, <= 2 python processes of your own (BelowNormal, affinity 0xFFFF),
never touch the 6 running run211/run212 workers.  A220 (running) OWNS tree211.py / tree209.py / tree206.py -- do
NOT edit them; deliver a NEW module attempts/A221-lane-cover/code/noroom221.py plus a standalone benchmark; the
one-line integration into tree209.noroom_at is a follow-up after A220 lands (write the patch as a .diff in code/).
multibox.py (A171/A172), noroom189.py, polylane.py (A141), chordlane.py (A161) are READ-ONLY libraries: wrap, never edit.

## The facts (attempts/A211-coarse-tree/certs/coarsetree211_k5_16_interior_Y0402.json, node R.2.1 and R.2.1.1; the
## same on Y0738 / Y1056)
no-room at k = 10 (m = 1): 120.1 s, UNDECIDED, "pocket LANE sum None does not beat 1", cn_bound 2, pockets
[[1.4375, 2.0917, 3.1396, 3.4396], [3.2571, 3.4396, 1.5013, 1.8972]] -- two centre pockets of diameter < 1.  The
child R.2.1.1 (after Rule NS on F2) repeats it: 121.7 s, one pocket [1.4375, 2.0917, 3.1436, 3.4396], UNDECIDED.
So the whole 120 s cap goes to bisect_free + a lane that returns None, at every child.  noroom189.noroom: bisection
(total_deadline) -> pockets_of -> per-pocket Node.lane (lane_depth 48, lane_max_open 1e5, lane_deadline 240 but
capped by the node deadline), lane None => UNDECIDED.  Node.lane = chordlane.lane_out on polylane.build_cond of the
roles' uboxes.  For m = 1 the node is DEAD iff LANE = 0 on every pocket.

## Task
1. EXPERIMENT FIRST (benchmark before estimating): rebuild the no-room node for Y0402 R.2.1 and R.2.1.1 and for two
   undecided k=10 nodes of Y0738 from the certs' role boxes (tree209.noroom_at shows how roles are built from pg;
   startload211 / inherit211 show how to load a node's boxes from a cert snapshot).  Measure: bisect_free seconds vs
   lane seconds inside the 120 s; then run the LANE ALONE on the recorded pockets with 600 s and lane_max_open 1e6:
   does it return 0?  If not, what does it leave open (which poses / tilts)?  Are the A213/A214 kernels active in
   the lane's primitives (mbpatch213 patches polycore.vertex_ok globally -- confirm the lane path hits them; profile
   the top 5 functions of a 120 s lane run)?  Write results/experiment221.md with the numbers before any design.
2. POCKET INHERITANCE (sound; prove it in notes/lane221.md): a child's role boxes are subsets of its parent's (NS
   meets/misses, ROLE-SPLIT halves, POCKET instantiation adds a role), so the child's cores contain the parent's and
   the child's free poses lie inside the parent's; hence the PARENT'S pocket list covers the child's free centres.
   noroom221.noroom_child(roles, parent_pockets, deadline): run the lane on the inherited pockets with the child's
   cores FIRST (no bisection); only if some lane is None run bisect_free restricted to the undecided pockets' centre
   windows (not the whole container).  Record which step decided.
3. MAKE THE LANE DECIDE: whatever the experiment says is the blocker -- kernel (route the lane's exact tests through
   A213 int / A214 C), search order (tilt-first on small pockets; the pocket's diameter < 1 means a single free
   centre: test the K' of the 10 roles against the pocket's pose set directly with the A214 clip = "lonely clip on
   the pocket"), or budget (lane_max_open) -- implement it in noroom221 and re-run the four nodes: report DEAD/None
   and seconds per node.  Target: each of these nodes decided in < 20 s.
4. BENCHMARK on closed pages too (verdict agreement): replay every recorded no-room UNDECIDED-at-cap node of
   Y0500 g1 and Y0460 g1 (their certs) through noroom221 and report verdicts and seconds.
5. Deliverables: code/noroom221.py, code/bench221.py, code/tree209_integration.diff (the flag-gated one-liner:
   A221_LANE=1 routes noroom_at through noroom221 with the parent's pockets from node["noroom"]), notes/lane221.md
   (the inheritance lemma, the design, n-general), results/experiment221.md, results/bench221.md (+jsonl), registry
   row, LOG entry.  Report once (<= 15 lines: the four nodes' before/after, the closed-page check, what the blocker
   was, commits) and EXIT.
