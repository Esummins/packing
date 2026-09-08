# A146 — k5_13 closed. What actually held it open, and what the restart proved.

`attempts/A146-k5_13-restart/`, 2026-09-07 night. Read-only on A56/A61/A114/A124 and on every
running campaign (A136/A141/A144/A145). `lpbox.py`, `resolve61.py` and `campaign61.py` were never
edited and never copied-with-edits; A61's state was written only by A61's own driver, run as a
child of `code/supervise146.py`.

---

## L1 — The hang never recurred, because the two-stage protocol removes its cause

A124 (`attempts/A124-recheck-day/notes/y0381_hang.md`) proved the mechanism: `LPModel.__init__`
sets `output_flag=False` and `threads=1` and **no `time_limit`**, so `h.run()` can spin forever
while `solve_node`'s limit is only checked between iterations. k5_13 lost ~40 CPU-h to it at
stage-A iteration 7 of a `--lp_time 1200` run, at 4,332 orbits × 18,326 rows.

The wall built for this attempt (`supervise146.py`: kill the tree when the driver has emitted no
stdout for 1,500 s **and** has no live descendant process — silence with a descendant is a
certifier or verifier and must not be disturbed) **never tripped in either run.** The reason is
not luck: the hang lives in the large late iterations, and the two-stage protocol's 240 s cap
stops stage A at iteration 1–2, at 3,500 orbits × 15,555 rows. Under the 900 s cap the run
reached 4,341 orbits × 17,468 rows — one iteration short of the wedged geometry — and still
returned. **The protocol is itself the hang mitigation; the wall is the backstop, and it is
cheap to carry.** Keep both: a CAP is a resource event, never a verdict.

## L2 — k5_13 cannot afford the ε_geo = 0.003 shrink, and that is a measurement, not a timeout

Two independent runs, same enriched pool, different LP caps:

| cap | τ₀ (ε_geo 1e−4) | slack₀ | τ at ε_geo 0.003 | budget − τ | dτ/dε | outcome |
|---|---|---|---|---|---|---|
| 240 s | 5.619048 | 0.3810 | 5.963641 | **0.0364** | **118.8** | certify round 0 total 5.99354 (149 atoms) → witness feedback → round 1 τ = 6.00000 → *cannot certify* |
| 900 s | 5.617045 | 0.3830 | **6.000000** | **−0.0000** | **132.1** | post-shrink GATE-FAIL, no certify round burnt |

Every row A61 converted measured **dτ/dε = 57–90** (k5_17 57.5, k6_20 65.3, k6_21 65.6, k5_10
62.7, k6_29 89.8). k5_13 measures **119–132**, i.e. the shrink costs it **0.34–0.38 of budget
against a slack of 0.38**. A61's own L5 says the enriched pool flattens the shrink curve by
supplying alternative atoms for the shrunk square; k5_13 is the row where it does not — the
measure has no slack to re-route. More LP time makes it *worse*, not better (τ rises with the
extra rows a better-solved LP generates): the 900 s stage B lands on τ = 6.000000 exactly.

**So the A61 re-solve route is dead for k5_13 for a stated reason, and the reason is the node's
own dτ/dε, not the LP wall, not the gate, and not the A124 hang.** The 40 CPU-h the campaign
spent here bought nothing because the route it was on could not have converted.

## L3 — The row was never a straggler; it was an over-width slab (A114's law, third confirmation)

`resolve61.py`'s 4-D step verifies **the whole window as ONE slab** (`--slo S_LO --shi S0`,
width 0.057084). A146's probe measures k5_13's constants on the **existing** A56 parametric
certificate (106 atoms, margin 0.037449, no re-solve, no LP):

    probe [3.820000, 3.821000], width 1e−3 → PASS in 74 s
    max s-depth 6, max depth 47  ⇒  w_min = 1.56e−5, d_pose = 41, width_max = 0.002

The whole window is **28× width_max**. A56's single-slab FAIL (max_depth 48, max_s_depth 10,
worst witness `undecided`, **0 holes**) is exactly the signature of a slab over its width_max, and
**no certificate A61 could have produced would have changed it** — a fatter certificate raises
w_min, but not by 28×. The row's file said OPEN; the row was never hard.

Sweep at width 1/1000 (58 slabs, endpoints on the verifier's integer grid): **58/58 PASS, zero
failures, zero bisections, 5,491 verifier-seconds**, exact tile of [191/50, 969271/250000],
C2 canary PASS at s_lo / mid / s0 (3.6 / 4.6 / 85.0 s) under the unmodified A53 `verify_case.py`.

Cost profile along the side, confirming A114's L7 and its cause: 74 s per 10⁻³ at the bottom,
flat to ~80 s through the bulk, then **99 → 108 → 115 → 126 → 182 → 507 s** over the last five
slabs, with **d_pose stepping 41 → 42 and width_max halving to 0.001 in the slab ending at
3.877** — the S02 shadow arriving in the arithmetic exactly where A114 measured it for k5_12.
The final 8.4·10⁻⁵ sliver ending at s0 passed. Width 1/1000 was the right choice by luck as much
as judgement: it is width_max/2 at the bottom and exactly width_max at the top.

## L4 — Operational: the driver's resume is its column pool, and it is monotone

`resolve61.py` has no stage resume. `enriched_warm()` globs
`attempts/{A56,A61}/results/nodes/<name>*.json` and folds every checkpoint the lab ever wrote, so
the *killed* run's `k5_13_A_state.json` (1.4 MB, iteration 6, written by `solve_node`'s own
`checkpoint=`) was the resume: the pool went 3,996 → 4,332 → 4,341 orbits across the three
launches. That is the whole mechanism, and it is why killing a wedged A61 LP is safe. It is also
why a CAP must never be recorded as a verdict: the next launch is strictly better placed.

## L5 — What this says about the remaining window work

Nothing is left: the A56 scoreboard is **52/52 full-window** (4 M1 + 28 TRANSFERRED + 20
TRANSFERRED-resolved, `full_window_rows` 52, no OPEN and no partial row). The transferable
lesson is A114's, now with its third and cleanest confirmation: **when a parametric run FAILs with
0 holes and a depth-limited worst witness, price the slab before you price the certificate.** One
probe slab costs ~75 s and answers it. Re-solving the measure is the expensive branch and, on
this row, the impossible one.
