# A227 -- Lemma EPS (half-side entry): where a second meeter of a near-simple square's cell can be (PI, 2026-09-15
# 00:40: "this feels almost trivially provable using just geometric arguments").
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (BelowNormal, affinity 0xFFFF), never touch running workers
(pass-5 run211 workers p5a/p5b, run212 w1-w3).  Do NOT edit tree211.py / leaves211.py / tree209.py / fast202 --
deliver the rule as a module + an integration diff.  Pages to docs/residue_map/campaigns/A227-lemma-eps/.
Read first: docs/proofs/snap_rule.md (A224: SNAP is sound but never fires on k5 because H's edge enters the raw cell
by 0.008 -- the sliver), forced_corners.md (Theorem FC: forced cells doubly met by two distinct non-pin meeters),
attempts/A224-snap-rule/notes/snap224.md + results/snapscan224.jsonl (294 candidate nodes, the blockers, 107 of them
H), A202's stage-0 layer (fast30: closed-form rules <= 30 s before anything slower), A203's option table (cell rows:
which squares can meet which cell), sideband.md (Lemma A1), corner_seal.md.

## The lemma to state and prove (n-general, pure geometry)
Setting: a unit cell C = slot cell, a unit square F with pose within (delta, theta0) of C's slot pose S (centre offset
|dc|_inf <= delta, tilt |theta| <= theta0, both small).  Then C \ Q(F) is the union of at most four thin WEDGES, one
along each side of C: along a side, the wedge is the region between F's corresponding edge line and the side,
bounded by the point where F's edge crosses the side; it lies on ONE half of the side (which half is decided by the
sign of theta and the offset: for a pure CCW rotation the pattern is right side upper half, top side left half, left
side lower half, bottom side right half -- a pinwheel), has width <= w(delta, theta0) = O(delta + theta0) at the
cell's corner and tapers to zero at the crossing point.  Consequences: (i) any unit square M interior-disjoint from
F that meets int(C) meets one of these wedges, so M enters C only through the tilt-determined HALF of one side and to
depth <= w; (ii) along a side of C shared with a pin or a wall the wedge is reachable only through its open end at
the cell's corner (a vertex of M poking in from the adjacent open side): the "point" of the PI's SNAP-DIAG; (iii) the
region of poses of M meeting a wedge is a closed-form set (M's centre within a strip of width ~ w + 1/sqrt2 around
the half-side, tilt-dependent) -- give it exactly.
Rule EPS (engine, stage 0): at a node where a role F is near-simple in a forced cell C (Theorem FC hypothesis),
replace the option row "M meets C" by "M meets the wedges of (F, C)": every candidate meeter (named role via its
box reach; anonymous via the option table / Lemma A1) that cannot reach the wedge half-sides is struck; if fewer
than the two distinct non-pin meeters FC demands remain, the node is DEAD by FC+EPS with the wedge computation as
the certificate.  Where the blocker is a single role that CAN reach the wedge (Y0865's H), the rule does not kill --
say so, and give the closed-form wedge so Rule NS can split that role at the wedge instead of the whole cell.

## Task
1. Prove Lemma EPS with the explicit wedge geometry (all four sides, tilt sign and offset cases, pin/wall-shared
   sides), state the constants, n-general.  docs/proofs/lemma_eps.md, tags [T]/[C].
2. Lean: Statements/Open/LemmaEps.lean -- the wedge containment as a theorem if it follows in a few lines from the
   square's set description (try), else a documented axiom; build + audit exit 0, no sorry.
3. Code: attempts/A227-lemma-eps/code/eps227.py (wedges of (F-box, C) as exact rational polygons over the box, the
   meeter-strike test per role box / option row) + a replay over every recorded node of the alive k5 pages' certs
   (as snapscan224 did): how many nodes die by FC+EPS, how many candidates lose a meeter without dying, which
   blockers survive (expect H).  Then one page-run benchmark (isolated cert dir, --no-fig, one process) on Y0402 g1
   with the rule wired through an integration diff (stage 0 or leaf rule (0) beside SNAP), verdict agreement on one
   closed page.  Report kills and seconds.
4. Deliverables: lemma_eps.md, the Lean file, eps227.py + integration diff, results/eps227.md (+jsonl), pages (the
   wedges drawn on the PI's Y0865 case: F1's cell with its four wedges, H's edge entering the right-upper wedge),
   registry row, LOG entry.  Report once (<= 15 lines) and EXIT.
