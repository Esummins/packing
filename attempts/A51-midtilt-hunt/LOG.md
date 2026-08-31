# A51 — mid-tilt flush-free basin hunt: log

2026-08-31, computation postdoc (Opus). Goal per BRIEF.md: close A49's sampling
caveat by re-aiming the A49 machinery at the MID-TILT non-thin flush-free world.

## Method / provenance

- No A49 file is edited or copied. `code/a51_run.py` imports `a49_common`
  (with the FIXED `repair_ok`, lam_hi = 8 + explicit feasibility check),
  `hunt_a49`, `stratum_a49`, `audit_a49` and only REBINDS `a49_common`'s
  output directories to A51's `results/`, `work/`, `logs/` (every A49 driver
  resolves them at run time), plus a swapped control-seed set.
- Seeds: `code/seeds_a51.py` -> `results/seeds.json`, 19 families in four
  groups (i)-(iv); see `notes/seed_design.md`.
- Protocol identical to A49: free-descent census with feasible-path
  flush-acquisition tracking; global stratum (eps_s = 0.25 deg, 66 rows) and
  local stratum (eps_l = tol_f = 0.05 deg, rows re-selected each round) with
  full Fritz-John tests at interior minimisers; negative control; A37 audit +
  Krawczyk pipeline for any candidate.
- [NUM] float64 throughout. A29 untouched.

## Timeline

- 09:2x  seeds built, 19/19 accepted.
- 09:28  three background processes launched (<= 3 heavy): census
  (`--reps 20`, 399 runs), global stratum then negative control, local
  stratum (`--reps 5`, 114 runs). One long-poll waiter per run.
- 09:29  global stratum DONE: 399 runs, 394 PRESSED-ON-FLUSH-BOUNDARY, 5
  INTERIOR-NOT-CP (all constructively refuted: nnls 0.65-0.72, LP rate -1.0,
  witness gain 0.61-1.48 — these are stuck starts, not interior minima),
  0 INTERIOR-CANDIDATE. **s_min = 3.889299** (A49's was 4.00173).
- 09:43  local stratum DONE: 114 runs, 113 BLOCKED-BY-FLUSH-BOUNDARY, 1
  PRESSED, 0 interior, 0 candidates. **s_min = 3.8784120 = s0 + 0.00133**
  (A49's was 4.00001). All 114 stopping points flush-free.
- 09:52  negative control DONE: 63/63 landings carry flush contacts (median
  13 violations; 338 wall + 429 pair). All three base runs hold exactly at
  their own s and rematch to themselves.
- 10:07  `krawczyk_a51.py` written and SELF-TESTED on atlas family 0: r_N =
  1/2000, ratio 0.056632, s enclosure width 8.9e-16 — reproduces A37's own
  3R record. The exact stage of the candidate pipeline is live code.
- 10:34  census DONE (66.0 min, 399 runs): 0 candidates, 12 flush-free
  landings (all constructively NOT-CP), 395 flush acquired, 328 drain to
  known. **s_min = 3.8770835900228224 = s0** (15 runs land on the Trump
  packing; 172/399 below s = 4). Landings feasible to <= 5.6e-16.
- 10:40  audits: 0 candidates, 0 survivors. Krawczyk stage: no-op (nothing to
  certify). Side probe: the 26x-hit non-catalogue attractor at s = 3.8853914
  audits GN-consistent (6.8e-71) but is VALLEY rank 33/34 -> no 34-row pin
  basis -> no 3R certificate claimed.

## Headline

OUTCOME B again, in the regime A49 could not reach — and **A49's banked
wall-termination law is falsified as a general statement**: solo flush events
are 95% wall in A49 and 80% in the mixed opened-atlas family, but only 6% wall
(94% interior pair) in the pure mid-tilt world. Replacement regularity, 0
counterexamples in 257 events: flush is acquired WITHIN a tilt regime — 0 of
149 pair events join an upright square to a tilted one.

Budget: ~2.0 CPU-h over 3 concurrent processes (census 66 min, local stratum
15 min, global stratum 2 min, control 12 min, audits/exact stage ~8 min).
A29 untouched. Full write-up: `results/a51_report.md`.
