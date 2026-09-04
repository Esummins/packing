# A95 — A57 shortcuts: parametric node certificates and the k5_11 reflection (Opus chore)

Context: A57 runs the k5_11 / k5_16 sub-stratification trees at four grid sides (3.877084, 3.862404,
3.847780, 3.833212) because each fixed-side certificate covers only a slack-core slab ~0.0155 wide
(Lemma B, delta = 1e-2). ~1,150 nodes per class per side, ~7 min/node, 10-15% descend to level 2. Two
possible cuts, both to be MEASURED, not argued:

## T1 — parametric-in-side node certificates
The lab has a Lean-proved 4-D window checker (V.PARAM: verify_param.py, checkParamI_kill; A61 uses it
to convert s0-only rows to full-window kills; see attempts/A61-window-stragglers/code/resolve61.py
and docs/specs/parametric_kill.md). Take 20 finished A57 level-1 nodes of k5_11 at side 1 (G1) from
attempts/A57-shadow-trees/results/tree_k5_11_interior_G1_*.jsonl (10 easy PASS, 5 marginal PASS,
5 that FAILED certification), re-emit each as a PARAMETRIC kill over the whole window [3.82, s0] (or
the widest sub-window it certifies), with the frozen verifier; report per node: fixed-side LP+cert
wall vs parametric LP+cert wall, and whether the parametric certificate covers the full window, a
part (which), or fails. Verdict: the ratio (parametric cost) / (4 x fixed-side cost) and the fraction
of nodes covered — i.e. whether one parametric pass replaces the four sides, and for which nodes.

## T2 — the diagonal reflection of k5_11
k5_11's pin set {(1/2,1/2), (3/2,1/2), (1/2,3/2), (1/2,s-1/2), (s-1/2,1/2)} is invariant under the
reflection x <-> y (the BL staircase (2,1) is self-conjugate; TL and BR corners swap). Check whether
attempts/A57-shadow-trees/code/tree57.py exploits this stabiliser (a fundamental domain / orbit
representatives at the zone level, as A67's D4 reduction does at the root and A85's corner85 does
sigma-equivariantly): if not, state the exact sound reduction (the interior zone T x [0,90) is
reflected; a box and its mirror are both killed by one certificate mirrored — needs the mirrored
certificate to be re-verified or the verifier's symmetry clause), count how many of the 1,150 nodes
per side it removes (pairs of mirror boxes, minus self-mirror boxes), and its price. k5_16's pin set
(four corners + (1/2,3/2)) has trivial stabiliser — confirm.

## T3 — where A57's time goes
From the progress JSONs and logs (attempts/A57-shadow-trees/progress, logs): the wall split per node
between LP, certification, eps_geo retries, and logic kills; the level-2 descent rate per shard; a
projected remaining wall for G1 and for sides 4/3/2 with the skip list, so the coordinator can
re-estimate. Do NOT touch A57's running processes, queue, or files; read only, write under
attempts/A95-a57-shortcuts/{code,results,notes}. One process, BLAS-pinned, the 6144 MB commit gate
(A92 and A94 each hold one LP slot — wait for headroom; no polling wakeups: one self-gating
launcher + one terminal wait). Report once, tersely: T1 ratio and coverage first, T2 node count second,
T3 projection third.
