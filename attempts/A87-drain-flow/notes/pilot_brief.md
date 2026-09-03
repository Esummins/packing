# A87 H1 pilot — chore brief (Opus). Lead: Fable (A87). 2026-09-03

Goal: MEASURE the global FJ-exclusion test (H1 = drain_lemma.md T3 restricted to k0 configurations)
on k0 configuration cells: per-cell cost, the discharge scale h*(Δ) as a function of the side excess
Δ = σ(z) − s0, the fraction of near-feasible coarse cells killed with no FJ solve (the PI's claim (ii)),
and the FJ degeneracy at the under-contacted k0 optima (claim (iii)). No theory. No LP campaign.

## Hard constraints
- Writes ONLY inside `attempts/A87-drain-flow/` (code/, results/, logs/, notes/pilot_report.md).
- Never touch A57/A60/A61/A85/A86 files or processes. Read-only inputs:
  `attempts/A85-k0-route/results/cp85_k0_search.json`, `attempts/A03-upper-reconstruct/trump11_exact.json`,
  `attempts/A30-t3-pilot/pilot.py` (copy helpers, do not import across attempts).
- ≤ 2 Python processes total, BLAS pinned (`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`
  set at the top of every script BEFORE numpy import). Before launching anything check commit headroom:
  PowerShell `$o=Get-CimInstance Win32_OperatingSystem; ($o.FreeVirtualMemory/1MB)` must be > 6 (GB);
  if not, wait (one background waiter polling every 60 s, exits when headroom > 6 GB), never poll in a loop
  of sleeps. Exactly ONE background waiter at a time.
- Wall cap ≈ 2.5 h. Everything checkpoints to results/*.jsonl so partial runs are usable.

## Engine
`code/t3lib.py` = verbatim copy of A30's engine (A22 layout z[3i]=cx_i, z[3i+1]=cy_i, z[3i+2]=θ_i radians,
z[33]=s; NV=34; mpmath.iv dps 30). FIX its two relative paths (`load_trump`, `load_a22_cert`) to
`HERE/../../A03-upper-reconstruct/...` and `HERE/../../A22-local-rigidity/...`. Run `code/selftest30.py`
after adjusting its import/path lines (it must PASS 7/7 incl. corruption gates) — log to logs/selftest.log.
Copy from A30's pilot.py into `code/pilot87.py`: renormalise, build_cell, cell_report (with the
per-selection sweep), grad_matrix, fj_multipliers, fj_lam0_zero, math_log2. Use s0 = Fraction(969271, 250000)
everywhere ("clip s to s0"): every cell's s-box is [σ_min(cell), s0].

Config conversion: cp85 optima store `x` in A04 layout (cx_0,cy_0,…,cx_10,cy_10, θ_0..θ_10, s). Convert to A22
layout, Fractions via limit_denominator(10**12), then `renormalise(z, pad=1e-9)` (min corner at the origin),
and set z[33] = the exact bounding side of the renormalised point (max corner coordinate, interval upper bound
+ 1e-12). Trump: `t3lib.load_trump()` exact; rotated Trump R_φ ẑ = rotate all centres about (ŝ/2, ŝ/2) by φ,
add φ to every θ, renormalise, side = max extent.

Cell verdict codes (cell_report): `a` (interval infeasible), `a-menu` (empty selection menu),
`a-sigma` (σ_min(cell) > s0, i.e. build_cell returns None), `b` (D2 slack), `c1-union`, `c1-sweep`
(per-selection sweep complete with 0 alive), `alive`. Record per cell: verdict, min_gap, min_clear,
n_wall_straddle, n_pairs_straddle, menu_log2, n_union_rows, farkas_eps, and timings t_ab, t_menu,
t_farkas_lp, t_farkas_verify, sweep cpu_secs_per_selection, t_total.

## J1 — discharge-scale ladder (results/j1_ladder.jsonl)
Reference configs:
 r1 = best k0 optimum (s = 3.887213…, Δ = 0.0101, 4 axis-aligned squares);
 r2 = the smallest-side optimum with n_axis_aligned = 0 (s = 3.905653…, Δ = 0.0286);
 r3 = an optimum with s closest to 3.95; r4 = one closest to 4.00; r5 = one closest to 4.20;
 r6 = Trump rotated by φ = 1e-3 rad (k0, σ ≈ ŝ + 3.9e-3);
 r7 = Trump rotated by φ = 5e-8 rad (a genuine k0 packing at side ≤ s0: the rotational ghost).
Half-widths h ∈ {0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 5e-4, 2e-4, 1e-4}; for r7 additionally
{1e-5, 1e-6, 1e-7, 3e-8, 1e-8}. For each (config, h): cell_report with sweep_cap = 3000 selections
(single process; skip the sweep when menu_log2 > 40 and note it). Report h*(config) = the largest h at which
the cell is excluded, and by which test.

## J2 — near-feasible survey, the PI's claim (ii) (results/j2_survey.jsonl, results/j2_summary.json)
For every one of the 262 optima and h ∈ {0.05, 0.02, 0.01, 0.005, 0.002}: cell centred at the optimum
(cheap path only: (a)/(a-sigma)/(a-menu)/(b)/(c1-union); NO sweeps). Also for the 14 optima with s < 3.9 a
second cell centred at a random offset of ±h/2 per coordinate (seeded, rng 87). Summarise per h and per
Δ-bin (Δ = s − s0 in bins [0.01,0.02), [0.02,0.05), [0.05,0.1), [0.1,0.3), [0.3,∞)): counts by verdict.
Fit: the largest h killed for each optimum vs Δ (report the ratio h*/Δ median/min/max and the reason mix).
Key number: fraction of cells with σ_min(cell) ≤ s0 (i.e. NOT killed by a-sigma) that are killed by
(b) or (c1-union) — that is the "excluded immediately with no FJ solve" rate the PI expects to be high.

## J3 — FJ degeneracy at the under-contacted optima (results/j3_degeneracy.json)
For the 14 optima with s < 3.9 and r6: at the exact point (thin box), collect the active rows
(|value| ≤ 1e-6: wall rows + for each straddling pair the selections consistent at the point, take the
first consistent selection's straddling rows), then: grad_matrix rank, fj_multipliers (feasible?, max-min λ,
support, poly_dim), fj_lam0_zero, number of squares with NO active row (rattlers), dimension of the null space of
the active gradient matrix restricted to the 33 configuration coordinates (the flat directions), and one
Krawczyk 'compl' probe on a box of half-width 1e-4 with λ-radius 1e-3 (report singular/cond/excluded).
Also on the h = 1e-3 cell around each: is the per-selection sweep (cap 3000) 0-alive, partial, or all alive.

## J4 — projection (results/j4_projection.json, computed, no runs)
Using the measured per-cell costs and h*: (i) uniform 33-dim cover count of D0 (ranges: centres [0, s0]²
per square, θ ∈ [0, π/2)) at h = h*_median from J2, divided by 8·11! (symmetry) — quote as 10^x;
(ii) cells needed to cover ONE landing box of A85's tree (radius 1.6e-3 in every coordinate) at h*;
(iii) cells to cover one ghost drain box (radius 5e-3) at h*; (iv) CPU-h for (ii) and (iii) at the measured
cheap-path cost and at the sweep cost; (v) the ratio of the per-cell cheap-path cost to A85's measured LP
node cost (≈ 1 700 s). Quote A30's numbers alongside (cell_count_model in
attempts/A30-t3-pilot/results/pilot_report.json).

## Report
`notes/pilot_report.md`, terse, tables only + 5 lines of findings: per-cell costs; h*(Δ) table; the J2 kill-rate
table (by verdict); J3 degeneracy table; J4 projections. Final message to the lead = the same tables, nothing
else. No theory, no recommendations.
