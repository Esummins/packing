# A34 — sparse SOS / Lasserre pilot on the lifted packing POP (Fable lead)

You are the THEORY lead (Fable). Do the mathematics yourself; dispatch Opus/Sonnet subagents for
coding/installs/solver runs only, terse file-pointer briefs. Idea board: docs/ideas.md I-L14.
Context: REGISTRY rows A15 (theta' killed the 1/4-ghost on samples — evidence the ghost is a
level-1 artifact), A17-A20 (why hand-built continuum kernels failed), A30-A32 (why local search
lost). Conventions: t = tan(theta/2) rational trig; exact rational certificates; two-verifier trust.

## T1 — formulation (math, yours)
Lifted POP: variables z = (c_i, t_i)_{i<=n}, s, and per pair a separating direction u_ij (2 vars);
constraints polynomial after clearing (1+t^2) denominators: containment corner rows; per pair the 8
"all corners of i on one side / all corners of j on the other" rows bilinear in (u_ij, corners) plus
a normalization (pick one: ||u||_2^2 = 1 or affine). CHECK AND WRITE OUT: projection onto z of the
lifted feasible set = exactly the packings (every packing admits u; every feasible (z,u) separates
every pair), so min s over the lift = s(n). Then: correlative sparsity pattern (which variable
cliques the rows induce), D4 x S_n symmetry reduction, expected moment-matrix block sizes at
Lasserre levels 1-2 (with term sparsity, TSSOS-style). Decide the exclusion encoding for the
endgame form (certify s >= s-hat - eps OUTSIDE A22's box: 66-branch disjunction or a single
polynomial cut) — design only, do not run it yet.

## T2 — validation on solved cases (subagent compute)
Install Julia + TSSOS (or SumOfSquares.jl + a rational-friendly SDP path; disk guard — Mathlib
history says watch free space). Targets with KNOWN answers: s(2) = 2, s(3) = 2, s(5) = 2 + 1/sqrt2
(the Gobel packing). Questions per target: does level 1 reproduce the LP-strength bound? does level
2 certify the TRUE value (or how close)? SDP sizes, times. Extract ONE rational certificate (small
case) and verify it exactly (round Gram matrix to rationals + PSD check by LDL^T in exact
arithmetic) to validate the trust chain end-to-end.

## T3 — the n = 11 question
At n = 11: what bound does the highest computable level give at s in {3.83, 3.84, 3.85}? The single
decision number: DOES LEVEL 2 (with sparsity/symmetry) BEAT THE PROVEN PURE-LP CEILING 3.83? If SDP
size is infeasible at n = 11, quantify the wall precisely (block sizes vs solver limits) and
measure the largest n' where level 2 IS feasible — the scaling law is the deliverable then.

## Report
Bound table (n, s, level, bound, SDP blocks, time), the rational-certificate validation, the n=11
verdict or the measured wall, gap list. Honest negatives are successes; quantify everything.

## Constraints
Machine shared with A33: <= 3 heavy processes. Disk guard (>= 5 GB free at all times). Checkpoints,
registry row, terse traffic. Final report plain-language-friendly for the PI.
