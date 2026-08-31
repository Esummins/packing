# A49 LOG (Fable lead)

2026-08-29 ~17:05  A49 dispatched (PI directive after A48 close): the decisive
I-L19 experiment — hunt for a flush-free critical point on the A48 evasion
architecture. Registry row added (running). Dirs created.

2026-08-29 ~17:40  Seed design + constructor done (notes/seed_design.md,
code/seeds_a49.py, results/seeds.json): 12 seeds, 4B/3M/4T-staggered
architecture, tilt profiles uniform1/2/3/5, escal, alt2, midtilt; press modes
P-CONF (C5b u = sin^2 d) and P-B1 (C1 bridge u); global tilt comb (pairwise
class gaps >= 0.35 deg). 12/12 accepted (lam-1 0.10-0.30, s_rep 4.42-4.91,
gap 0.35). Constructor iterations surfaced two facts recorded in the notes:
presser congestion (extent > pitch) and the straight-chain span obstruction
(near-upright 4-chain advance ~1.0/contact => must staircase to bind at s0) —
both consistent with A48's picture; seeds are loose basin selectors.
Next: Opus hunt worker (free descent census + stratum-constrained descent +
FJ tests + audits), ONE background agent.

2026-08-29 ~23:50  Hunt worker done. OUTCOME B — zero flush-free critical
candidates, zero survivors. Files: code/{a49_common,hunt_a49,stratum_a49,
audit_a49,summary_a49}.py; results/{hunt,stratum,stratum_local,control,
a49_summary}.json + results/a49_report.md sections 3-6; logs/hunt_log.txt.
- Census 252 runs: (a) 0 candidates (17 flush-free landings, all
  constructively NOT-CP, s 4.10-4.57), (b) 252 flush acquired, (c) 235 drain
  to known — every match is the s = 4.000000000 axis-aligned grid family.
  min s anywhere from A49 seeds = 4.000000000000012.
- Acquisition map (97 feasible-path events): modal B-wall 33 / top T-T 31 /
  chain B-B 18 / T-wall 15, press M-B **0**; median s at acquisition 4.0000;
  acquisition is a SIMULTANEOUS 10-13 contact collapse in 77/97 runs, and of
  the 20 solo events 19 are B-wall (B0 wall termination).
- Stratum: global eps_s 0.25 deg 251/252 PRESSED (1 interior, NOT-CP, 0
  candidates); local eps_l = tol_f 72/72 BLOCKED-BY-FLUSH-BOUNDARY, 0 interior.
  Flush-free stratum costs ~ +0.013 in s over the unconstrained 4.000.
- Negative control 63/63: flush contacts present at every landing; A37-NEW-0
  21/21 rematch to itself, family 31 14/21, family 27 7/21 (VALLEY-MARGINAL,
  drains to catalogue 6 at 3.886746 — consistent with A37).
- METHOD BANK: (i) one pack11.polish call is a whole SLSQP solve, so a
  feasible-path SUBDIVIDED micro-descent is required to resolve any
  acquisition event; (ii) a37_drain.repair caps its scale search at
  lam_hi = 1.10 and can silently return a still-overlapping point — A49 wraps
  it as repair_ok (lam_hi 8 + feasibility check). A first local-stratum sweep
  was invalidated by this and re-run; superseded data kept under
  work/*.SUPERSEDED_repair_cap_bug.json.
