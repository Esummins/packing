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
