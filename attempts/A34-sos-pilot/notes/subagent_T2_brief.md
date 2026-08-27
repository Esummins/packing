# A34 T2 subagent brief — install + validation runs (terse)

Spec: attempts/A34-sos-pilot/notes/formulation.md (READ IT — §1 constraints, §5 sizes, §6 protocol).
Work dir: attempts/A34-sos-pilot/code + results. Machine shared (<=3 heavy procs), disk guard 5 GB.

1. Install Julia (juliaup or portable zip, into a persistent location) + packages: TSSOS, DynamicPolynomials, plus a solver (Mosek if licensed — check; else COSMO and Clarabel; record which). Log versions to results/env.json.
2. code/model.jl: build the POP of formulation.md §1 for given n (min-s form) with corner coordinates EXACTLY as in §2(b); toggles: cuts R1/R2/R3 on/off, Tier A (cs = pair cliques passed manually) vs plain TSSOS CS="MF" vs dense, levels 1/2(/3 small n).
3. Runs (checkpoint each result to results/validation.json as you go: n, s-form, tier, level, cuts, bound, block sizes, iters, time, solver status + a-posteriori residual check):
   - n=2: dense levels 1,2. Expect bound -> 2 at some level.
   - n=3: Tier A and dense, levels 1,2.
   - n=5: Tier A level 2 (cuts on/off), Tier B level 2 if it fits. Target 2.70710678.
4. Sanity: also solve each with the known packing as a feasibility check (plug in the known optimal configuration + separating directions, verify all constraints >= -1e-9 — catches sign/corner bugs BEFORE trusting bounds).
5. Report back (terse): the table, any surprises, file paths. Do NOT start n=11.
