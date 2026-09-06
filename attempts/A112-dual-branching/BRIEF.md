# A112 — dual-guided branching as a second cover: three orderings on the stalled regions, resumable (Opus chore)

Context (2026-09-06, PI: "brief A112 as soon as A111 lands"). A111 (`4c6ace6e`, attempts/A111-loadpath-branch/notes/
{leaf_shape,method}.md) measured load-path branching on the 286 shadow-explained alive nodes of A57/A60: sound on
146 (51%) at their own level; 35 projected kills at a 2/3 certify rate (n = 3); ≈ +1 wall-day at 5 workers; two nodes
killed end to end (k5_11_interior_Y0054_D00 via S02, k5_16_interior_Y0984 via S07). Facts that shape this attempt:
(i) the chain (Farkas) YES kill certifies only for r < s* − s0 (0.0097 for S02, 0.0085 for S07) — level-4 box widths,
never wider — because the fixed-tilt LP bound is exactly s* − r; (ii) the octagon/TC tests kill nothing between
load-path boxes at side s0 (genuine room: side-blind rules cannot make a side statement) but fire constantly between
a node's OWN conditioned bin and a load-path box — the FREE PAIR KILL: 113/264 S02 nodes at L1 rising to 200/264 at
L4, 19/19 S07 from L2, verified by 57,840 sampled pose pairs with zero counterexamples; (iii) the NO side is a
convergence-time problem (a child dead-unconverged at 80 s converges DEAD at 900 s), not re-pricing: 8 of 22 nodes
had every NO child LP-dead at r = 0.1, ρ = 10°; certification 14 PASS / 4 FAIL, every child with η ≤ −0.5 passed; but
verify_param.py has no nofams support, so NO certificates are fixed-side (one pass per side of the four-side grid);
(iv) S07's load path is Trump's: the S07 branch is UNSOUND at level 1 (Trump enters the YES region at A57's L1 tilt
half-width) and usable from level 2 down; (v) two bugs caught only by dense sampling — a standing rule now: no
LP-free geometric count is reported before ≥ 10⁴ sampled pose pairs confirm it. A113 (`6409396b`) found the same
structure in k0_00: the un-killable k0 cells' supports are 2–6-slot partial skeletons of near-critical shadows, and
the k0 tree has zero logic kills because it never branches on corners.

The PI's design (docs/residue_ledger.md §6, memory): a SECOND tree with a different branching order on the region
where the first stalls, kills transferred to old boxes by containment (a tree is a cover; the Lean composition takes
unions). Three orderings to compare on the same region: (1) load path by Fritz-John multiplier (A111's), (2) STRANDED
SPACE — score each dual-support placement by the LP row mass its YES core strikes out plus the support mass its
NO-family removes (strong branching in rows, no LP solve needed; also report the unusable-area variant), (3) the
hybrid: the load-path member that strands the most. A111's free pair kill is the first check at every YES node;
the chain kill applies at level ≥ 4 widths only.

Read first: A111's notes and results (t3.json, t3_logickills.json, t2_certs.jsonl, leaf_shape.md), attempts/A57-
shadow-trees/code/{tree57,deepen,pinguard}.py + A96's trim57.py/pausegate.py/shadow_sched.py (`d016209b`, the
resumable driver with T5″ and the PAUSE sentinel), attempts/A107-shadow-gallery/results/shadow_nodes.json (+ the k0
extension when it lands), attempts/A113-k0-manifold-distance/results/t2_supports.jsonl, docs/budget.md §B–D.

## T1 — the region tree, implemented resumably
Build `code/regiontree.py`: root = a stalled node's hypothesis (its class pins + its conditioned box), branching by a
pluggable ORDER function over the node's dual support; YES child = root + a box F around the chosen placement (r, ρ
chosen per level from A111's radius table: start at (0.1, 10°) and halve), NO child = root + NO-family F; at every
YES node run the free pair kill (core_meet_kill + tilt_coupling between every pair of conditioned bins, normalised
tilt intervals, a ≤ 1/2 asserted) and the octagon box-vs-pin trim before any LP; LP with the 900 s cap (A111: this is
what decides the NO side); certify LP-dead children with the frozen verify_case.py at s0 (fixed side; note the
four-side cost for the window claim). Per-node record files so the run can be killed and resumed. Kills are recorded
as "old box X dead by region tree Y" with the containment check (the union of the region tree's dead hypotheses
covers the old box's hypothesis) written out explicitly.

## T2 — the comparison
Region: the S02-explained stalled nodes of A57 at levels 2–3 (A107's list; all with a T5″-trimmed bin) — ≥ 12 nodes —
and, for the k0 face, ≥ 6 of A113's un-killable k0 level-1 cells (the S38/S07-matching ones; k0's YES side uses the
slot box and the crowd row at depth 0, since every k ≥ 1 class is dead at s0). For each ordering: nodes to
termination, LP count, LP wall, certify wall, kills achieved, and the old-tree projection for the same region (A96's
model: 290 s/child, fan-out 8, measured descent 0.91/0.76/0). Report which ordering wins per region and by how much,
and whether the free pair kill or the LP does the killing.

## T3 — verdict and integration
One line per region: "region tree with ordering O terminates in N nodes / M LPs / W wall vs the old tree's projected
N′/M′/W′; kills X old boxes". State the integration path into A96's driver as a resumable option (a stalled node —
ALIVE twice or unconverged at 900 s — is handed to the region tree instead of being split) and the certificate
accounting (fixed-side NO certificates need verify_param nofams support for the window claim — say what that costs to
add). Canaries: Trump's grain never killed (the S07 branch only from level 2); every free-kill count confirmed by
dense sampling before it is reported; A111's two end-to-end kills reproduced.

Constraints: ≤ 2 processes, BLAS-pinned, commit gate 6144 MB and > 3 GB free physical before every LP; READ-ONLY on
A57/A96/A60/A61/A107/A111/A113/A114 state (own copies; A57 is paused — do not launch its drivers); frozen verifiers
byte-identical; git = fetch + plain merge + push own paths (no rebase/autostash/reset). Writes: attempts/A112-dual-
branching/{code,results,notes,logs}, registry row, LOG.md, note on the depgraph GRAIN node. Report ONCE: T3 first, T2
table second, T1 pointers last. No interim messages.
