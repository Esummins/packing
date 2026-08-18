# A11 — ab-initio sweep of the angle-lattice MILP over open n ≤ 100

Owner: A11 (MIO postdoc). Date: 2026-08-18. Status: DONE (finished 16:40; 39 CP-SAT runs, ~2 h wall clock on 4 slots; one crash of the controlling
session at the very start, restarted from disk).

## 1. Goal
Run A09's angle-lattice MILP finder (CP-SAT, fixed orientations ⇒ disjunctive LP, lattice of angles Θ ⇒ MILP)
over every n ≤ 100 whose s(n) is not proven, competing against the best-known records (Ellsworth's page,
Feb 2026): count exact rediscoveries (|s − record| ≤ 1e-6) and look for beats (s < record − 1e-9, verified with
exact rational arithmetic).

## 2. Files
* `parse_records.py` → `records.json`: record s(n), n ≤ 100, parsed from
  `docs/papers/ellsworth_squares_in_squares__triangular_table.txt` (for n not listed, the next listed n's
  packing minus squares); `proven` from docs/known_results.md; angle hints from closed forms.
* `milp_pack.py`, `make_cert.py`: copies of A09's with small extensions (`--smax` defaults to ceil(√n) so the
  trivial grid is always feasible; `--hint` gives CP-SAT the grid packing as a hint; make_cert's LP box
  widened to ceil(√n)+1).
* `make_jobs.py` → `jobs_phase{1,2,3}.json`; `run_queue.py jobs.json --par 4 --workers 4` runs them with
  4 concurrent CP-SAT processes × 4 workers, appends one line per finished job to `results.jsonl`,
  full solver output in `logs/`, packing JSON in `results/`, PNG in `plots/`. Matches/beats trigger
  `make_cert.py` (rational certificate + `certs/verify_certificate.py`), beats copy to `NEW_RECORD_n<N>.json`.
* Tilt angles for the record packings were read from Ellsworth's SVG sources
  (`https://kingbird.myphotos.cc/packing/square-<n>.svg`, `<!ENTITY a ...>` + rotate()/scale() transforms):
  n=17: a=39.80496°, b=36.62379° used as rotate(−b) ⇒ classes {0, 39.805, 53.376};
  n=18: a=24.29519° with a scale(1 −1) mirror ⇒ {0, 24.295, 65.705};
  n=28: a=30.29141° ⇒ {0, 30.291}; n=29: five angles a=25.2587, b=20.8001, c=17.5063, d=24.9626,
  i=24.3084 with mirrors ⇒ ≥ 9 classes (too many for CP-SAT; sub-lattices used);
  n=37: 45° and a=47.9134° (rotate(−a) + mirrors ⇒ {42.087, 47.913}); n=39: a=43.7156°, b=37.4252° (used
  as −a, −b ⇒ {46.284, 52.575}, mirrors give {43.716, 37.425}); n=41: a=36.4190°, b=31.5658° (as −a, −b);
  n=53: a=24.2952 (both signs), b=26.5982, c=32.0125 (5 classes); n=50: 3-4-5 triple ⇒ atan(3/4)=36.870°.
  Closed forms with only √2 (19, 26, 27, 38, 40, 52, 65, 66, 67, 82, 84, 85, 89) ⇒ {0,45}.
  Heuristic sets used where the SVG was not consulted: {0,45}, {0,θ*=40.1819 (Trump)}, {0,30,45}, {0,20,45}.

Compute: 20 logical CPUs shared with A10 (≤ 6 threads); 4 concurrent CP-SAT processes × 4 workers each
(the orphaned batch at 15:41 briefly ran 8). All times below are wall-clock under that load.

## 3. Plan / time limits
n ≤ 20: 600 s per Θ; 21–30: 900 s; 31–45: 900 s, ≤ 2 Θ; > 45: 600 s, Θ={0,45} only if time remains.
Feasibility mode (`--fix-s record − 1e-4`) for the trivial-record cases (12, 20, 21, 30) and as a second run
where the free run stalls just above the record. Symmetry breaking on, grid hint on.

## 4. Results

### 4.0 Headline
* **Matches (exact ab-initio rediscovery of the record, certificate PASS): n = 11 (Trump) and n = 18
  (7/2 + √7/2).** Count = 2 of the 18 open n attacked (of 60 open n ≤ 100; the 42 others were not attacked:
  n = 30–32, 42–45, 56–61, 72–78, 90–97 have integer records and the rest are large-n SA records where the
  probes at 37–65 show CP-SAT does not leave the grid in 600–900 s).
* **Beats: none.** No NEW_RECORD file.
* Best MILP value per n (best of all runs; full per-run list in 4.3):

| n | record | best MILP s | gap | Θ (best run) | mode | solver status | t_limit | structure |
|---|---|---|---|---|---|---|---|---|
| 11 | 3.8770835900 | 3.8770835900 **MATCH** | +4.44e-15 | {0,40.18} | free | FEASIBLE | 300 | 6x0deg + 5x40.1819deg |
| 12 | 4.0000000000 | none | — | {0,45,40.18} | fix 3.9999 | UNKNOWN | 600 | — |
| 17 | 4.6755300936 | 4.7071067812 | +3.16e-02 | {0,45} | free | FEASIBLE | 600 | 16x0deg + 1x45deg |
| 18 | 4.8228756555 | 4.8228756555 **MATCH** | +5.33e-15 | {0,24.3,65.7} | free | FEASIBLE | 600 | 14x0deg + 4x24.2952deg |
| 19 | 4.8856180832 | 4.9428090416 | +5.72e-02 | {0,45} | free | FEASIBLE | 600 | 16x0deg + 3x45deg |
| 20 | 5.0000000000 | none | — | {0,45} | fix 4.9999 | UNKNOWN | 600 | — |
| 21 | 5.0000000000 | none | — | {0,45,40.18} | fix 4.9999 | UNKNOWN | 600 | — |
| 26 | 5.6213203436 | 5.7071067812 | +8.58e-02 | {0,45} | free | FEASIBLE | 900 | 25x0deg + 1x45deg |
| 27 | 5.7071067812 | 5.8970562748 | +1.90e-01 | {0,45} | free | FEASIBLE | 900 | 22x0deg + 5x45deg |
| 28 | 5.8244446167 | 5.9428090416 | +1.18e-01 | {0,45} | free | FEASIBLE | 900 | 22x0deg + 6x45deg |
| 29 | 5.9338334627 | 6.0000000000 | +6.62e-02 | {0,25.26,64.74} | free | FEASIBLE | 900 | 29x0deg |
| 37 | 6.5986196092 | 6.7475468957 | +1.49e-01 | {0,45,42.09,47.91} | free | FEASIBLE | 900 | 34x0deg + 3x45deg |
| 39 | 6.8107220831 | 7.0000000000 | +1.89e-01 | {0,46.28,52.57} | free | FEASIBLE | 900 | 39x0deg |
| 40 | 6.8284271247 | 7.0000000000 | +1.72e-01 | {0,45} | free | FEASIBLE | 900 | 40x0deg |
| 41 | 6.9266930945 | 7.0000000000 | +7.33e-02 | {0,53.58,58.43} | free | FEASIBLE | 900 | 41x0deg |
| 50 | 7.5714285714 | 7.7142857137 | +1.43e-01 | {0,36.87,53.13} | free | FEASIBLE | 600 | 49x0deg + 1x53.1301deg |
| 52 | 7.7071067812 | 8.0000000000 | +2.93e-01 | {0,45} | free | FEASIBLE | 600 | 52x0deg |
| 65 | 8.5355339059 | 8.7071067812 | +1.72e-01 | {0,45} | free | FEASIBLE | 600 | 63x0deg + 2x45deg |

### 4.3 All runs (from `results.jsonl`; wall = seconds incl. polish under 4-way sharing)
| n | Θ | mode | s | gap | status | bound | wall s | structure | cert |
|---|---|---|---|---|---|---|---|---|---|
| 11 | {0,40.18} | free | 3.8770835900 | +4.44e-15 | FEASIBLE | 3.31663 | 315 | 6x0deg + 5x40.1819deg | PASS |
| 12 | {0,45,40.18} | fix 3.9999 | none | — | UNKNOWN | 3.9999 | 607 | None |  |
| 17 | {0,30,45} | free | 4.7071067812 | +3.16e-02 | FEASIBLE | 4.12311 | 626 | 16x0deg + 1x45deg |  |
| 17 | {0,39.8,53.38} | fix 4.6754 | none | — | MODEL_INVALID | 0.0 | 15 | None |  |
| 17 | {0,39.8,53.38} | fix 4.6754 | none | — | MODEL_INVALID | 0.0 | 5 | None |  |
| 17 | {0,39.8,53.38} | fix 4.6754 | none | — | UNKNOWN | 4.67543 | 605 | None |  |
| 17 | {0,39.8,53.38} | free | 4.7100233874 | +3.45e-02 | FEASIBLE | 4.12311 | 607 | 16x0deg + 1x39.805deg |  |
| 17 | {0,39.8,53.38} | free | 4.7100233874 | +3.45e-02 | FEASIBLE | 4.12311 | 617 | 16x0deg + 1x39.805deg |  |
| 17 | {0,40.18} | free | 4.7096142528 | +3.41e-02 | FEASIBLE | 4.12311 | 606 | 15x0deg + 2x40.1819deg |  |
| 17 | {0,45} | fix 4.6754 | none | — | MODEL_INVALID | 0.0 | 5 | None |  |
| 17 | {0,45} | fix 4.6754 | none | — | MODEL_INVALID | 0.0 | 5 | None |  |
| 17 | {0,45} | fix 4.6754 | none | — | UNKNOWN | 4.67543 | 605 | None |  |
| 17 | {0,45} | free | 4.7071067812 | +3.16e-02 | FEASIBLE | 4.12311 | 612 | 16x0deg + 1x45deg |  |
| 18 | {0,24.3,65.7} | free | 4.8228756555 | +5.33e-15 | FEASIBLE | 4.24265 | 607 | 14x0deg + 4x24.2952deg | PASS |
| 18 | {0,40.18} | fix 4.8228 | none | — | UNKNOWN | 4.82277 | 602 | None |  |
| 18 | {0,40.18} | free | 4.8384570114 | +1.56e-02 | FEASIBLE | 4.24265 | 606 | 13x0deg + 5x40.1819deg |  |
| 18 | {0,45} | free | 4.8970562748 | +7.42e-02 | FEASIBLE | 4.24265 | 606 | 13x0deg + 5x45deg |  |
| 19 | {0,40.18} | free | 4.9439168978 | +5.83e-02 | FEASIBLE | 4.3589 | 925 | 14x0deg + 5x40.1819deg |  |
| 19 | {0,45} | fix 4.8855 | none | — | UNKNOWN | 4.88552 | 612 | None |  |
| 19 | {0,45} | fix 4.8855 | none | — | UNKNOWN | 4.88551 | 602 | None |  |
| 19 | {0,45} | free | 4.9428090416 | +5.72e-02 | FEASIBLE | 4.3589 | 607 | 16x0deg + 3x45deg |  |
| 19 | {0,45} | free | 5.0000000000 | +1.14e-01 | FEASIBLE | 4.3589 | 621 | 19x0deg |  |
| 19 | {0,45} | free | 5.0000000000 | +1.14e-01 | FEASIBLE | 4.3589 | 612 | 19x0deg |  |
| 20 | {0,45} | fix 4.9999 | none | — | UNKNOWN | 4.9999 | 607 | None |  |
| 21 | {0,45,40.18} | fix 4.9999 | none | — | UNKNOWN | 4.9999 | 607 | None |  |
| 26 | {0,45} | free | 5.7071067812 | +8.58e-02 | FEASIBLE | 5.09902 | 907 | 25x0deg + 1x45deg |  |
| 27 | {0,45} | free | 5.8970562748 | +1.90e-01 | FEASIBLE | 5.19616 | 912 | 22x0deg + 5x45deg |  |
| 28 | {0,30.29} | free | 5.9528649541 | +1.28e-01 | FEASIBLE | 5.29151 | 907 | 25x0deg + 3x30.2914deg |  |
| 28 | {0,45} | free | 5.9428090416 | +1.18e-01 | FEASIBLE | 5.29151 | 1207 | 22x0deg + 6x45deg |  |
| 29 | {0,25.26,64.74,24.96,65.04} | free | 6.0000000000 | +6.62e-02 | FEASIBLE | 5.38517 | 907 | 29x0deg |  |
| 29 | {0,25.26,64.74} | free | 6.0000000000 | +6.62e-02 | FEASIBLE | 5.38517 | 912 | 29x0deg |  |
| 29 | {0,45} | free | 6.0000000000 | +6.62e-02 | FEASIBLE | 5.38517 | 931 | 29x0deg |  |
| 37 | {0,45,42.09,47.91} | free | 6.7475468957 | +1.49e-01 | FEASIBLE | 6.08277 | 907 | 34x0deg + 3x45deg |  |
| 39 | {0,46.28,52.57} | free | 7.0000000000 | +1.89e-01 | FEASIBLE | 6.245 | 907 | 39x0deg |  |
| 40 | {0,45} | free | 7.0000000000 | +1.72e-01 | FEASIBLE | 6.32456 | 907 | 40x0deg |  |
| 41 | {0,53.58,58.43} | free | 7.0000000000 | +7.33e-02 | FEASIBLE | 6.40313 | 907 | 41x0deg |  |
| 50 | {0,36.87,53.13} | free | 7.7142857137 | +1.43e-01 | FEASIBLE | 7.07107 | 607 | 49x0deg + 1x53.1301deg |  |
| 52 | {0,45} | free | 8.0000000000 | +2.93e-01 | FEASIBLE | 7.21111 | 607 | 52x0deg |  |
| 65 | {0,45} | free | 8.7071067812 | +1.72e-01 | FEASIBLE | 8.06226 | 610 | 63x0deg + 2x45deg |  |


### 4.4 Chronological log (as jobs finished; authoritative data in results.jsonl)
* 14:54 n=11 {0,θ*}: 3.8770835900228144 = Trump (diff 4e-15) in 43 s; cert PASS. (calibration OK)
* 14:59 n=18 {0,24.2952,65.7048} (SVG angles): **MATCH** 4.822875655532295 = 7/2+√7/2 (diff 5e-15),
  structure 14×0° + 4×24.2952° (2×2 tilted block in the middle) — Hämäläinen's packing rediscovered ab initio,
  no contact graph given; rational certificate PASSES (results/n18_a0_24.2952_65.7048_free_svg_cert.json).
* 14:59 n=17 {0,39.805,53.376}: 4.7100 (16×0°+1×39.8°) — stalled 0.034 above the record 4.67553 (Bidwell's
  packing has several tilted squares at two angles; the LNS never left the 1-tilted basin in 600 s).
* 14:59 n=19 {0,45}: 4.9428 (16×0°+3×45°) — stalled 0.057 above the record 3+4√2/3.
  ⇒ phase 1b queued: fix-s (record − 1e-4) for 17 and 19, and free re-runs with seed 7.
* 15:09 n=17 {0,45}: 4.7071067812 = 4+1/√2 (16×0°+1×45°, the pre-1998 record); {0,θ*}: 4.7096 (15+2).
* 15:09 n=18 {0,45}: 4.8971 (13+5×45°); {0,θ*}: 4.8385 (13×0°+5×40.18°, Trump-like pinwheel — 0.0156 above
  the record; a genuinely different near-record structure).
* 15:19 n=12 fix-s 3.9999 {0,45,θ*}, n=20 fix-s 4.9999 {0,45}, n=21 fix-s 4.9999 {0,45,θ*}: all UNKNOWN after
  600 s (neither a packing nor a refutation), as A09 found for n=12.
* 15:34 n=28 {0,30.2914} (SVG angle): 5.9529 (25×0°+3×30.3°), 0.128 above the record — CP-SAT barely leaves the
  grid at 378 pairs. 15:35 n=29 {0,25.26,64.74}: 6.0 = the 6×6 grid, nothing better in 900 s.
  ⇒ MILP is not competitive at n ≥ 28 with 900 s; phase 2/3 trimmed to 4 + 3 probe jobs (37/39/41 with SVG
  angles, 40 {0,45}; 50 {0,36.87,53.13}, 52, 65 {0,45}) — expected outcome: grid.
* 15:41 phase-1 queue killed after 21 jobs to skip the low-value 28/29/30 heuristic runs (n=28 {0,45}: 5.9428
  (22+6), n=29 {0,45}: 6.0 grid, n=19 {0,θ*}: 4.9439 (14+5), n=17 {0,30,45}: 4.7071 (16+1) were ingested from
  the orphaned processes). Phase 1b (fix-s + reseeded runs for 17, 19) started.
* 15:50 BUG: `--fix-s record − 1e-4` gave MODEL_INVALID for n=17/19 (CP-SAT s-domain [ceil(smin·1e5), round(smax·1e5)]
  is empty when fix_s is off the 1e-5 grid). Fixed in milp_pack.py (fix_s rounded DOWN to the grid) and the
  fix-s runs re-queued as `*_v2` at the head of phase 3.
* 16:03 phase 1b: n=19 {0,45} fix-s 4.88552: UNKNOWN (600 s); n=19 {0,45} seed 7: 5.0 (grid!) — worse than seed 0
  (4.9428): strong seed variance; n=17 SVG lattice seed 7: 4.7100 again (16+1). NOTE: `--counts` is silently
  ignored by the CP-SAT back-end (only the HiGHS rows implement it) — this also affects A09's "counts fixed 6+5,
  s fixed" run, which was therefore a plain feasibility run.
* 16:07 phase 2 (900 s, SVG lattices): n=37 {0,45,42.09,47.91}: 6.7475 (34+3×45°), record 6.5986; n=39, 41
  (3-angle SVG lattices) and n=40 {0,45}: stuck at the 7×7 grid (7.0). Second MODEL_INVALID for the n=17 fix-s
  v2 runs (float noise: ceil(4.67543·1e5) = 467544 > 467543) — fixed again (`ceil(smin·S − 1e-6)`), tested on
  n=5, re-queued as phase 4 (`*_v3`).
* 16:17 phase 3: n=19 {0,45} fix-s 4.88552 (v2) UNKNOWN again; n=18 {0,θ*} fix-s 4.82277: UNKNOWN (no Trump-like
  18-packing below the record found/refuted); n=50 {0,36.87,53.13}: 7.7142857 = 7 + 5/7 (49 uprights + 1 tilted
  at 53.13°, rational side, exactly 1/7 above Schadt's 7 + 4/7); n=52 {0,45}: 8.0 grid.

* 16:27 n=65 {0,45}: 8.7071 (63+2), record 8.5355. 16:37 phase 4: n=17 fix-s 4.67543 with the SVG lattice and with
  {0,45} (v3, model now valid): UNKNOWN after 600 s — nothing below Bidwell's record found or refuted. END.

## 5. Verdict: where is the angle-lattice MILP competitive?

* **Exact ab-initio rediscoveries (|s − record| ≤ 1e-6, rational certificates PASS `certs/verify_certificate.py`):
  2 of the 12 open n ≤ 30 attacked — n = 11 (Trump, 6+5 at θ*, 43 s) and n = 18 (Hämäläinen/Gustafsson
  7/2 + √7/2, 14 uprights + a 2×2 block tilted 24.295°, < 600 s).** Both need the true tilt on the lattice
  (|Θ| = 2–3). No beats. Two structurally different near-records: n = 18 at 4.8385 (13 + 5 at 40.18°,
  Trump-like pinwheel, +0.0156) and n = 50 at 7 + 5/7 (+1/7 over Schadt's 7 + 4/7).
* **Failures at n ≤ 20**: n = 17 (record needs 5 tilted squares in two classes; every run — SVG lattice, {0,45},
  {0,θ*}, {0,30,45}, seed 7 — stalls at 16 uprights + 1 tilted, s = 4.7071–4.7100, +0.03) and n = 19 (record =
  Stromquist/Hämäläinen 11-packing + 8 uprights, 5 diagonals in a strip; runs stall at 16+3 = 4.9428 or the grid;
  fix-s at record − 1e-4: UNKNOWN twice). The LNS neighbourhoods do not move 4–5 squares between angle classes
  at once; the "one tilted square in the corner gap" basin is a strong attractor.
* **n ≥ 26**: with 900 s and 4 workers CP-SAT does not leave the grid basin (26: 25+1, 27: 22+5 wrong
  arrangement, 28: +0.12, 29/39/40/41/52: exact grid, 37: 34+3, +0.15). MILP is not competitive against the SA
  campaigns there; the number of pair-disjunctions (n²/2 · 4|Θ|) is 2–5 k binaries and every incumbent
  improvement is a 1e-5 step because the LP relaxation is void (A09 §3.3).
* **Trivial-record cases** (12, 20, 21; also 30 was planned but dropped): feasibility at ceil(√n) − 1e-4 is
  UNKNOWN after 600 s in every case — neither found nor refuted, as A09 saw for n = 12.
* Rule of thumb: the finder is competitive for **n ≤ ~20 with |Θ| ≤ 3 when the record's tilt angles are on the
  lattice and the record has ≤ 4 tilted squares in one rigid cluster**; beyond that it needs seeding.

## 6. What a longer campaign would need
1. **Seed with the record structure and ask for feasibility at record − ε** (`--fix-s`, hint = record packing
   snapped to the lattice, plus a *working* `--counts` in the CP-SAT back-end — currently ignored, see §4.1). This
   turns the question into "is there a neighbour of the record on this lattice that is strictly better?" —
   the only form of the question CP-SAT answered quickly for n = 11 (A09/A04 say no for Trump).
2. **Multi-angle lattices near the record tilt** ({0, θ_rec ± δ, 45}) after the structure is found — successive
   refinement, not one fine lattice (A09 §3.4: |Θ| ≥ 5 degrades the primal heuristics).
3. More CP-SAT workers per run (6–8) and longer runs (≥ 1 h) for n = 17/19; run seeds in parallel (variance is
   large: seed 7 vs seed 0 on n = 19 gave 5.0 vs 4.9428).
4. Better objective handling: after every incumbent, fix its combinatorial structure and re-solve the LP
   (our `polish_lp`) *inside* the search (solution callback → AddHint / objective cut), so the solver does not
   spend hundreds of 1e-5 steps on one structure.
5. For n ≥ 26 the honest recommendation is SA/basin hopping (A04's machinery generalised to arbitrary n) with
   the MILP only as a *local* exact re-optimiser of a given angle assignment (the LP polish), not as a finder.

## 7. Files (this directory)
`records.json` (records n ≤ 100 + provenance), `results.jsonl` (one line per run — the table below is generated
from it by `summarize.py`), `results/*.json` (packings), `results/*_cert.json` (verified rational certificates for
n = 11 and n = 18), `plots/*.png`, `logs/*.log` (CP-SAT logs), `jobs_phase*.json`, `run_queue.py`, `ingest.py`,
`chain*.ps1`, `launch_phase.ps1`. No NEW_RECORD file was produced (no beat).
