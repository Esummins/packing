# A30 — T3 critical-point-exclusion pilot (Opus)

Goal: PILOT (not a campaign) of test T3(c) from docs/proofs/drain_lemma.md (v2, Fritz John form).
Measure per-cell cost and find machinery gaps. Deliverable = numbers + gaps, not a bound.

Context. A29 (3.84 tree) is PAUSED as fallback; this is now the critical path (endgame: local
optimality A22 + global exclusion at s₀ = s* = Trump's side). Read drain_lemma.md v2 first: cells are
excluded by (a) interval infeasibility, (b) D2 uniform slack, or (c) per-selection FJ-system
exclusion via interval Krawczyk. Menus = selections (owner axis, sign, dominant corner per near
pair) whose rows interval-straddle activity on the cell.

Reuse. attempts/A22-local-rigidity (Krawczyk on the 33-var contact system, mpmath.iv, recheck.py) —
this is the per-branch engine. t = tan(θ/2) conventions as in A27 verify_tree2.py for anything new
(polynomial, exact); A22's angle parametrisation is acceptable inside the pilot where reuse is
faster (re-emission in t is a separate queued task).

Three tests, in order:
 P1 positive control. Cell = A22's box (radius 5e-4 around Trump ẑ), s₀ = ŝ + 1e-6. The menu must
    contain Trump's active selection; Krawczyk must ISOLATE the known root there (consistency with
    A22), and every other menu selection should exclude or isolate the same point.
 P2 negative control. Same-radius cell offset from ẑ by ~10× radius (pick a direction keeping
    interval feasibility plausible). Expect: every selection excluded, or the cell killed by (a)/(b).
 P3 generic cell. Cell of half-width ~0.01 (centres) × ~0.01 (t) around a random non-critical
    feasible configuration (e.g. loose packing at s = 3.9, perturbed). Report: menu size after
    interval pruning, per-selection Krawczyk time, whether (b) D2 fires first, λ₀ = 0 obstructions.

Report (results/pilot_report.json + REPORT.md, terse): per-test outcomes, menu sizes, seconds per
selection and per cell, extrapolated cost of a full cover at s₀ = s* (state your cell-count model),
and an explicit list of every soundness gap / heuristic shortcut taken (feeds the advisor's next
draft). Honest negatives welcome; a "this explodes because X" verdict is a success.

Constraints. ≤ 6 heavy workers (the box OOM-crashed at 9 — add a memory guard). All state
checkpointed to disk, detached-resumable. Terse traffic. Do NOT restart A29 processes.
