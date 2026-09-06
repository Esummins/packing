# A111 — shadow-guided branching: pin the load path, kill the YES side by the chain, let the LP kill the NO side (Opus chore, measurement)

Context (2026-09-06, PI proposal). A110 showed that inside a grain the side is a closed-form function of the
load-path squares' tilts (the chain menu Λ, Y, D, F_T; docs/proofs/grain_flood.md; Lemma GRAIN-LP: at fixed tilts and
a fixed separating-axis selection the side minimum is an LP whose dual is the load path), and that a GLOBAL grain
flood is circular. The PI's refinement: do not make a global statement — take the exact minimum of a region (S02, the
k7 pinwheel at 3.886746; S07 at 2 + 4√2/3), read off its load path, and pin the load-path squares in LP space with
slack: condition on boxes F0, F1, F2 around the load-bearing squares (A57's tree conditions on ONE square; this
conditions on the three that carry the load), so that (YES side) any configuration with squares in all three boxes
realises the chain and has side ≥ the chain minimum over the boxes > s0 — killable by an exact chain computation, no
measure certificate — and (NO side) the parent's LP gains the hypothesis "no square in F_i" for some i (A57's
NO-family machinery, `kind: NO`, `nofams` in the frozen verify_case.py), which removes exactly the support the LP was
using. The question is the radius: how large can F0–F2 be before the YES kill fails, and does the NO hypothesis
actually kill the alive parents or does the LP re-price to another shadow (A109's failure mode)?

Read first: docs/proofs/grain_flood.md (§1 GRAIN-LP, §2 the menu, §3 sweeps: which contacts are loaded on each side
of 48.435° for S02 and of 45° for S07, §4 GRAIN-ROW), docs/shadows.md §S02 (Fritz-John multipliers, f1–top wall
binding, the mirror pair, f3 idle), attempts/A108-s07-certify/results/{contacts,rigidity}.json, docs/residue_map/
gen_pinwheel_k7.py (the direct minimiser — reuse for the YES computation with box constraints), attempts/A57-shadow-
trees/code/tree57.py (how YES/NO cells are built: `kind`, `hyp`, NO-families; the frozen verify_case.py's nofams
support — byte-identical, run only), attempts/A53-simple-strata/code/caselp.py (solve_node; how a NO-family enters the
hypothesis), attempts/A107-shadow-gallery/results/shadow_nodes.json (which alive nodes S02/S07 explain),
attempts/A109-node-crowd/notes/report.md (re-pricing: why rows that do not forbid the support fail; the 28/46
unconverged "alive" nodes), attempts/A57-shadow-trees/results/tree/**/<node>.json (node LP results).

## T1 — the YES side: radius of the chain kill
For S02 (load path f0, f1, f2 + slots BL(0,1), TR(0,0), BR(0,1), top wall) and S07 (load path f0, f1, f2, f4 + the BL
column, BR(0,0), TR(0,0), top wall): take boxes F_i = [pose_i ± r] in (x, y) and [θ_i ± ρ] in tilt around the shadow's
load-bearing squares, for r ∈ {0.02, 0.05, 0.1, 0.2} and ρ ∈ {2°, 5°, 10°, 20°}. For each (r, ρ): (a) is the shadow's
separating-axis selection for the load-path pairs forced throughout the boxes (check the vertex-edge incidences that
define each loaded contact cannot flip sign anywhere in F0×F1×F2 — interval arithmetic over the boxes); (b) the
minimum side over F0×F1×F2 with the class pins fixed and the OTHER squares absent, by GRAIN-LP at fixed tilts on a
tilt grid plus the direct minimiser from many starts (box-constrained; this is a lower bound only if (a) holds — say
so); (c) verdict: YES region dead iff min side > s0 with margin; report the largest (r, ρ) that kills, and whether the
limit is the selection (a) or the chain minimum (b). Expect the tilt radius to be large for the ladder (Λ ≥ 2 + 4√2/3
everywhere) and the position radius to be set by (a).

## T2 — the NO side: does excluding the load path kill the parents?
For the alive nodes S02 explains (A57: 37 level-1 + 19 level-2 whose supports lie in the family per A110's T4; plus
the rest of the 252 for contrast) and the 18 S07 trump5 nodes: build the NO-family for the T1 YES region (the union
over i of "no square in F_i"? — no: the complement of YES is "for some i, no square in F_i", a DISJUNCTION; handle it
as A57 does, one NO node per box, i.e. three children each with one NO-family, each of which must die), re-solve the
node LP with the NO-family added (same warm pool, 300 s cap), and report per child τ, η, converged, and whether the
new dual support is another shadow (which one, by A107's dedup) or dies. Count: nodes where all three NO children die
at the LP; then certify a sample (≥ 8) with the frozen verify_case.py including the nofams (it supports NO-families;
the parametric verify_param.py does not — say what that costs).

## T3 — price and verdict
Per node: the YES computation (seconds) + three NO LPs vs the node's tree cost (A96: ~290 s per child, fan-out 8,
levels measured; the 252 S02 nodes carry 10 of 19 explained L3 and 4 of 9 L4). One line: "load-path branching at
radius (r, ρ) kills X of Y S02 nodes and Z of 18 S07 nodes; the NO side re-prices to shadow … in W cases" or the
failure mode. Also state the sound leaf shape for the YES kill (a Lean-shaped statement: box hypotheses on three
squares + the class pins ⇒ side ≥ c > s0 via the chain LP at fixed selection — what has to be verified exactly).
Canaries: Trump's grain must not be killed (an S07-style YES region must not contain Trump: check the 41.565°
boundary); S02's YES region must be dead at r = 0.

Constraints: READ-ONLY on A57/A60/A61/A96/A107/A109/A110 state (copy node jsons; A61's campaign is running — ≤ 2
processes, BLAS-pinned, 6144 MB commit gate and > 3 GB free physical before every LP); frozen verifiers
byte-identical; git = fetch + plain merge + push own paths (no rebase/autostash/reset). Writes: attempts/A111-
loadpath-branch/{code,results,notes,logs}, registry row, LOG.md, one-line note on the depgraph GRAIN node (owner
A111). Every drawn figure geometry-checked. Report ONCE: T3 verdict first, T1 radius table second, T2 table third,
pointers last. No interim messages.
