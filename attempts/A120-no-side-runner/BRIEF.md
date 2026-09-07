# A120 — the NO-side runner: A116's certified neighbourhood as the YES leaf, NO-family children through LP + frozen certifier, on the 35 in-N alive A57 nodes (Opus chore, soundness-adjacent, resumable)

Context (2026-09-07). A96 (the A57/A96 owner, now out of working room — its handoff is in its last report and in
attempts/A57-shadow-trees/PAUSED.md and A57's notes/lemmas.md) wired the region-tree option and verified A119's export of
the certified neighbourhoods; the one piece not written is this runner. It is soundness-adjacent: a wrong conversion of
the neighbourhood into NO-family children would silently under-constrain every LP built on it and nothing downstream
would fail. Build it without hurry, control it, then run.

Inputs (all exist):
* `attempts/A119-local-cert-lean/results/N_boxes.json`, entry `S02_k5_11_r0.20_rho10`: one axis-aligned box (cx, cy,
  θ-interval) per load-path square {f1, f2, f3, BR(0,1)} in the class frame at s0 + the cut, with `d4_ops` and per-node
  `frame_ops` (`diag` 175, `e` 360), and its covering note (the DROP/COVER step: squares in these boxes ⇒ inside N).
  A96's independent check: 73,642 draws → 10,500 tested → 0 hits (drawn → tested → hits; the survivor-count rule).
* `attempts/A96-a57-parametric/results/a116_targets.json`: the 35 alive nodes (all k5_11; L1 13, L2 19, L3 3).
* `attempts/A96-a57-parametric/code/regionopt96.py` (the option's trigger/tagging/ledger — reuse), `attempts/A112-dual-
  branching/code/regiontree.py` (YES/NO tautologous split; NO-family construction via caselp.NoFam; two-stage protocol;
  containment record), `attempts/A53-simple-strata/code/caselp.py` (solve_node, NoFam semantics), the frozen
  `verify_case.py` (byte-identical; sha in FREEZE_TAGS), `attempts/A96-a57-parametric/code/pausegate.py`.

## T1 — the runner
For each target node: map the four N boxes into the node's frame with the node's `struct_op` (from A107's
shadow_nodes.json; `frame_ops` in N_boxes.json), build one NO-family child per box (the node's hypothesis + "no square
in box F_i"), and record the YES side as `dead by local certificate A116 S02_k5_11_r0.20_rho10 (pending A119
rational/Lean form)`. Sound only if the YES and NO sides use the SAME boxes in the SAME frame — write the boxes used
into the record and assert they equal the mapped N boxes. Drive each NO child through the two-stage protocol (240 s LP
→ frozen certification when η ≤ −1e-3, converged or not → 900 s only for |η| < 1e-6) at s0; every NO certificate
tagged `s0-only, pending A117 verify_param_v2`. Per-node records keyed on (cls, id) — never the bare id — and the
pausegate sentinel checked between nodes. No campaign driver is launched; A57 stays paused.

## T2 — control before any run
Replay A112's two end-to-end kills (`k5_11_interior_Y0036_D07_D01`, `k5_11_interior_Y0276_D05`) and its 35 PASSing NO
certificates through the frozen verifier via the runner's own code path: byte-identical verdicts required. Then the
covering assertion on 3 target nodes: draw ≥ 10⁴ SURVIVING configurations with the L squares in the mapped boxes (report
drawn → tested → hits) — none with side ≤ s0.

## T3 — the run and the report
The 35 nodes, ≤ 2 processes, BLAS-pinned, commit gate 6144 MB and > 3 GB free physical before every LP/verifier, cap
15 CPU-h. Report: nodes closed outright (YES free + all NO children certified dead), nodes with NO children still open
(what they re-price to, by A107's dedup), CPU-h, and the subtree cones removed (~20.8 descendants at L1, ~14.1 at L2, 8
at L3 under f₂ = 0.906, f₃ = 0.762, f₄ = 0) as CPU-h off the 10–11-day schedule; drawn → tested → hits for every
sampled check quoted.

Constraints: READ-ONLY on every campaign and attempt except your own paths (A57/A96 paused — do not launch or edit
their drivers; write only under attempts/A120-no-side-runner/ and, for the ledger of closures, a NEW file
attempts/A96-a57-parametric/results/a120_closures.jsonl); frozen verifiers byte-identical; NO recursive deletes;
PYTHONDONTWRITEBYTECODE=1; tilt intervals normalised to [0, 90], core half-sides asserted ≤ 1/2; git = fetch + plain
merge + push own paths (no rebase/autostash/reset). Registry row, LOG.md, depgraph note on the A57 node. Report ONCE:
T3 first, T2 second, pointers last. No interim messages.
