# A34 T3 subagent brief — n = 11 (terse; dispatch only after T2 verdict)

Spec: notes/formulation.md §7. Model: reuse code/model.jl from T2. Machine shared, <=3 heavy procs,
disk guard 5 GB, checkpoint every solve to results/n11.json.

0. Canary FIRST: results/trump_lift_witness.json (z = (cx,cy,cos,sin), u per pair, all rational
   strings) must satisfy every model constraint at s = 969271/250000 to 1e-9 in float. If not, STOP
   — model bug, report.
1. Min-s form, Tier A (manual pair cliques {z_i, z_j, u_ij, s}), level 2, cuts R1-R3 ON: the bound.
   Note: TSSOS CS="MF" auto-detection yields Tier B (the csp graph is already chordal with maximal
   cliques K_0 = {z,s} and the pair cliques); Tier A requires passing cliques manually.
2. If (1) solves: same at level 3 if projected memory < 24 GB, else skip.
3. Tier B level 2 (auto CS): attempt; record block spectrum; abort if memory > 24 GB or time > 8 h.
4. If nothing solves at n = 11: bisect the wall — largest n' where Tier A L2 / Tier B L2 solve
   (try n' = 8, 9, 10; reuse validation models), record size/time scaling.
5. Fixed-s feasibility runs at s = 3.83 / 3.84 / 3.85 only if the min-s bound lands >= 3.80
   (otherwise pointless). Infeasible status at some s = kill at that s -> flag IMMEDIATELY.
6. Report: bound table rows (n=11, tier, level, cuts, bound, blocks, time, solver status,
   a-posteriori residuals), wall measurements, file paths. No prose beyond that.
