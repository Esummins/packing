# A106 — the shadows in A57's alive nodes: remaining box volume vs the slack, and the bottom-up (basin) alternative (Opus chore, read-only measurement)

Context (2026-09-06). A57 (window campaign on k5_11 / k5_16, parametric certificates) has a measured branching structure:
descent 1.44 → 0.91 → 0.76 per level, per-child cost flat (~290 s), and descent is CLUSTERED — four of six level-3
parents produced no alive children, one produced 3 of 8; three of the four alive level-3 children descend from the same
parent (A96 fertility probe running: attempts/A96-a57-parametric/). The PI's reading: a node is fertile because its box
contains a SHADOW — a local minimum of the side function whose side s* sits just above s0 = 3.877084 (or exactly at it,
if it is a Trump image, which these classes do not contain). Branch-and-bound then closes around the shadow taking
smaller and smaller bites: children without the shadow die, the child containing it keeps splitting until its box is
narrower than the slack s* − s0 lets the certificate see. Termination needs a finite-size certified volume around each
shadow — a basin certificate (A63's tube/basin machinery for Trump: rBasin = 3/2000 concrete, InStratum + theta-t
bridges, docs/proofs/ and lean/PackingCertMathlib/) — after which the tree only covers the complement. Measure whether
that switch is worth it.

Read first: attempts/A57-shadow-trees/{README or notes/lemmas.md, code/tree57.py, code/deepen.py} (node/box schema,
witness files), attempts/A96-a57-parametric/notes/ (parametric emission, resolver, the probes; results/tree_*_D2*.jsonl
and the depth-3/fertility probe outputs), attempts/A57-shadow-trees/certs/**/*.witnesses.json (schema: box, tilt range,
witness placements), docs/proofs/ tube/basin documents from A63 (grep "rBasin", "tube", "basin" under docs/proofs and
attempts/A63*), docs/residue_map.md §1 (A57 row) and §7.

## T1 — the boxes
For every ALIVE node at levels 2, 3 and 4 in k5_11 and k5_16 (from the tree jsonl and the probe outputs; read-only):
report the box: which squares are conditioned, each coordinate interval (x, y, tilt) and its width, the box's major
diameter in pose space (max over coordinates, and the Euclidean diameter with tilt in radians), the side window it is
certified/attempted over, and the LP's τ and η. Table + a per-level summary (median and max diameter per level); the
shrink factor per level.

## T2 — the shadows
For each such node, seed a FULL 11-square local minimisation of the side (all squares free; class pins as constraints
of the class, i.e. the simple squares fixed in their cells; A87's SQP or A57's own polish, exact-certified endpoint) from
the node's LP witness placements (and from the box centre if no witnesses). Report the local minimum's side s*, its
slack s* − s0, whether it lies inside the node's box (and inside which child), its tilt pattern, and whether the same
shadow is reached from sibling/cousin nodes (de-duplicate by pose distance 1e-4). Expect a handful of distinct shadows
per class. For each distinct shadow: s*, multiplicity (how many alive nodes contain it), and the number of alive
nodes that contain NO shadow (those are the ones that should die on their own).

## T3 — the switch
For each shadow: compare the containing box's major diameter to the slack s* − s0 through the certificate's sensitivity
(how much box width the parametric verifier tolerates per unit of slack — read it off the resolver's closed cells and
A96's verify caps), and estimate the depth at which the tree would close around it unaided (levels, CPU-h at 290 s/child
and the measured fan-out). Then estimate the basin route: a certified ball around the shadow of radius r where the side
is provably > s0 (second-order/Lipschitz bound as A63 did for Trump; state what r the Trump machinery would give from
the shadow's Hessian, and what it costs to certify); the tree then kills every box inside the ball at once. Report per
shadow: "tree closes unaided in ~N levels / ~C CPU-h" vs "basin of radius r covers the alive boxes / needs M more
levels to reach r", and the recommendation. One-line verdict: is the major diameter of the live boxes already small
enough that a bottom-up basin certificate per shadow beats continued branching, and by how much?

Constraints: READ-ONLY on A57/A96 state (copy what you need into your own tree); ≤ 1 process for the local
minimisations (BLAS-pinned, seconds each; wall cap 2 h), headroom > 6 GB commit and > 3 GB free physical; do not start,
stop or slow any A57/A96 process; frozen verifiers untouched; git = fetch + plain merge + push own paths (no
rebase/autostash/reset). Writes: attempts/A106-shadow-diameter/{code,results,notes,logs}, registry row, LOG.md, a
one-line note on depgraph node K0.TREE or the A57 node (whichever carries A57; owner A106). Report ONCE: T3 verdict
first, the shadow table second, the box table summary third, pointers last. No interim messages.
