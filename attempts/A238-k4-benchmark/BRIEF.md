# A238 -- the k5 toolkit on a Trump-parent protected class (PI, 2026-09-16 10:30: "the k4- classes that are parents
# of Trump shouldn't be able to get that close to Trump, since a bunch of the geo tests will kill them when they
# try to press the fifth simple square into place").
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns (runs detached with a
resume block, per-node commits), explicit-pathspec commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes
(BelowNormal, affinity 0xFFFF; 5 k5 frontier workers + the frontier loop are running -- never touch them or the
A211 certs/results; use your own attempt dirs), frozen verifiers untouched, read-only libraries wrapped.
Read first: docs/proofs/protected_trees.md (the 16 K1-protected classes = the classes with a compatible Trump image
G_S != {} whose trees must end in (D) tube leaves, plus the two shadow classes k4_05 / corners4 with no image;
Lemma K1; the A100 pilots on k4_11 and k3_02: level 24, 28 / 59 leaves, all_in_tube true, 3,500-4,200 CPU-h per
class under the LP toolkit), attempts/A100-protected-pilot (its roots, trees, timings = the BASELINE), attempts/
A84 (tier84.py: class definitions, pins, G_S), attempts/A212-trump5-tree (the Trump-containment gate + TUBE leaf,
Theorem T1 contraction tube; how a node is declared inside Trump's tube), A211's run211 / startload211 / A203 stage-0
root builder (how a k5 page becomes a root: pins + H + free squares), A224 (Rule SNAP: a near-simple role with no
second meeter snaps to its slot -> hand-off to the k+1 stratum), A227/A230 (EPS), A231 (WALL-EXCESS), the k5
frontier's kill statistics (results/progress.md: median 246 s per node).

## The PI's expectation to test
A protected k4 class is a Trump PARENT: its four pins are four of Trump's five simple squares.  Approaching Trump
inside its tree means the fifth square becomes near-simple with Trump's tilted neighbours around it; the PI expects
the geometric rules (SNAP hand-off to trump5 / the k5 class, EPS, CC, no-room, EmptyBox) to kill or hand off those
nodes long before the LP-priced depth, leaving only genuine tube leaves.  If true, the 14 Trump-parent classes are
cheap and the tier's price collapses from A100's 3,500-4,200 CPU-h each.

## Task
1. ROOTS: build k4_11 and k3_02 as pages for the k5 runner: the class pins as pins, the free squares as anonymous
   roles, the A203 stage-0 root from the class's window (reuse A100's roots / boxes if they load; otherwise the
   stage-0 builder from the pins alone).  Prove the hypothesis key is the class's (the certificate must be a
   certificate FOR the stratum, Lemma K1 / stratum_kill's statement).
2. LEAVES: wire the TUBE leaf (A212's Trump-containment gate: a node whose boxes lie inside Trump's contraction tube
   is a (D) leaf, certified by T1) and the SNAP hand-off (a snapped node goes to the k+1 stratum's queue: trump5 if
   the fifth square is Trump's, else the closed k5 class -> DEAD by K1) into the runner behind flags.
3. RUN both classes from the root with the pass flags (A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1 + tube +
   hand-off), wall 3600 s per pad, start-node shards if the root splits (A229 worker229); record per node the rule
   that killed / handed off / tubed it, depth, seconds.  Compare with A100's pilot on the same class: nodes, depth,
   CPU-h, leaves by type.
4. REPORT the PI's expectation against the numbers: how many nodes died by geometry before reaching A100's level,
   how many reached the tube, how many were handed off, and the price extrapolated to the 14 Trump-parent classes
   and the 2 shadow classes (corners4 / k4_05 have no Trump image: kill-only -- run corners4 the same way if time
   allows, A193's probe reached complete assignments at ~500 nodes).
5. Deliverables: attempts/A238-k4-benchmark/{code,results/bench238.md (+jsonl),notes/k4_238.md,certs,logs}, pages
   docs/residue_map/campaigns/A238-k4-benchmark/ (the class root and the first kills, geometry-checked), registry
   row, LOG entry, ledger s.3 note.  Report once (<= 15 lines) and EXIT.
