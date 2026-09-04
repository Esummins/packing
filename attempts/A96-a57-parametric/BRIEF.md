# A96 — convert A57's window campaign to parametric certificates + the sigma-symmetric ladder (Opus, engineering)

A95 measured (attempts/A95-a57-shortcuts/notes): parametric re-emission of A57 level-1 leaves with the
frozen 4-D verifier (A56 verify_param.py, window [191/50, s0]) costs 0.062 of four fixed sides (0.024 on
eps_geo-repaired leaves, 0.34 on easy ones); 7/15 cover the full window in one pass; the 6 completed
FAILs still cover 99.2-99.9% of the window, with the uncovered slivers recurring at the SAME two side
values across nodes: [3.82, 3.820056] (11 witnesses) and [3.82708, 3.827135] (13 witnesses) — a fixed-s
boundary degeneracy, not per-node hardness. k5_11's diagonal reflection is unused by tree57.py: a
sigma-symmetric theta ladder (nth = 10, a_min >= the deployed cover's at every side) gives 720 orbits
and removes 1,177 LP children over four sides (861 over sides 2-4), net ~548 s each; the mirrored
certificate is a format rewrite (x<->y, cores swapped, tm -> (1-tm)/(1+tm)) re-verified by the frozen
verifier. A57's true remaining cost is 15.4 wall-days at 5 workers (25.7 at 3), with level 2 (~16,400
children over four sides) the larger, least-measured half.

## Plan (do not disrupt the running G1 shards; sides 4/3/2 have not started)
1. FREEZE the A57 queue before it launches side 4: edit scaleup.ps1 / the queue so sides 4/3/2 do NOT
   start (leave G1 shards running to completion; their fixed-side certificates remain valid fallbacks).
   Record the edit in A57's notes/RESUME.md and LOG.md.
2. PARAMETRIC PASS over every A57 node (both classes; all finished level-1 leaves and every level-2
   child as the trees produce them): emit with A57's to_param.py + verify_param.py at depth 48, margin
   0, one process per verifier run, 1500 s cap. Record per node: PASS (full window) or the exact
   uncovered slivers. Order: eps_geo-repaired leaves first (highest yield), then easy leaves, then
   level-2 children. Skip nodes already killed by logic (recomputed per side by the C-check — keep the
   C-check per side for those).
3. SLIVER CLOSURE: for nodes whose parametric certificate misses only the two recurring slivers —
   (a) [3.82, 3.820056]: check whether the s(11) >= 3.82 certificate (A.LB382, no packing in the
   3.82 container, side <= 3.82 inclusive) already covers side exactly 3.82 and the window is
   (3.82, s0]; if so the first sliver needs only the open-endpoint form — state it exactly; (b) the
   [3.82708, 3.827135] sliver: one fixed-side slack-core certificate at 3.8271 per affected node (tiny),
   or a localised eps_geo/depth repair of the parametric certificate at that cell (A95's diagnosis) —
   measure which is cheaper on the 13 witnesses.
4. SIGMA LADDER for k5_11 on the parametric pass: rebuild the k5_11 cover with the sigma-symmetric
   nth=10 ladder; certify one representative per orbit; produce the mirrored certificate by the
   rewrite and re-verify it with the frozen verifier (verify_param.py for parametric, verify_case.py
   for fixed-side fallbacks); the tree obligation "every square with (centre,t) in sigma B contains
   sigma K" must be checked by the same C-check on the mirrored box, not assumed. k5_16 has trivial
   stabiliser: no ladder change.
5. LEVEL 2: emit the level-2 children parametrically from the start (no per-side fanout); measure the
   descent rate and per-child cost on the first 200 and re-project.
6. Composition: the window-coverage theorem for a class is the disjunction over its nodes of
   (parametric cert on its covered sub-window) OR (fixed-side certs on the slivers) OR (logic kill per
   side) — A86 T4's WindowRows form; write the row list per class for Lean replay (gen_param_lean.py).
Deliverables: attempts/A96-a57-parametric/{code,results,notes}, the A57 queue edit, per-class window
scoreboard (fraction of the window covered, nodes remaining), re-projection of A57's remaining wall
at 3 and 5 workers, registry row, LOG.md, depgraph C.A57 note (chip -> A96). Constraints: BLAS-pinned,
the 6144 MB commit gate with a self-gating launcher and ONE terminal wait (no polling wakeups); at most
2 verifier/LP processes of your own alongside the running G1 shards and A92/A94; frozen verifiers
untouched (copied byte-identical); A60/A61/A92/A93/A94 untouched. Report once, tersely: window coverage
per class first, the re-projection second, sliver verdict third, pointers.
