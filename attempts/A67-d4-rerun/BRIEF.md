# A67 — D.D4: machine-check the D4 reduction at s0 (Opus, mechanical)

Small, mechanical, unowned-until-now depgraph node (D.D4, checklist H12): the D4/S11 symmetry
reduction was machine-checked at side 3.84 (A27's verify_tree2 semantics); the s0 = 969271/250000
re-run is listed as "mechanical, not done". Do it.

Read first: lean/depgraph.json node D.D4; attempts/A27-close-384/ (the verify_tree2 reduction
semantics and how the 3.84 check was run); docs/proofs/instratum_bridge.md (how the census's D4
reduction is consumed); attempts/A53-simple-strata/code/skeletons2.py (the D4 canonicalization
in the census).

Task: re-run the reduction machine-check at s0 exactly as the 3.84 check ran (same semantics,
same verifier, side changed), plus the census-side check: verify the D4 canonicalization used by
skeletons2.py is a group action consistent with the container symmetries at s0 (exact rationals;
the reduction lemma's hypotheses hold verbatim when the container is [0, s0]^2). Record: the
command lines, PASS output, wall time, and a one-paragraph note of what the check establishes
and what it does not (docs/proofs/ addendum or attempts/A67-d4-rerun/notes/).

Constraints: ONE process, BLAS-pinned (imitate an existing launch pattern), commit headroom
> 6 GB before any launch, never touch A57/A60/A61/A29 state. If the 3.84 harness does not port
mechanically (an assumption bakes in the side), STOP and report the exact blocker rather than
improvising semantics — that would be a finding, not a failure.

Deliverables: the PASS record + notes; depgraph D.D4 label update (open -> certificate+verifier
with source pointers) + re-render via python lean/render_depgraph.py (pull/merge if others
edited); registry row; LOG.md entry. Terse.
