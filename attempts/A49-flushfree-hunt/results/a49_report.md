# A49 — the decisive I-L19 experiment: flush-free critical-point hunt on the
# A48 evasion architecture
(Fable lead + one Opus hunt worker, 2026-08-29)

Constants: s0 = 969271/250000 = 3.877084. Float attempt [NUM] by design — this
is a hunt/measurement, not a certificate run; any survivor would get exact
treatment afterwards.

## 1. Question

A48 settled the local theory of the bridge cascade and showed the composed
flush-mandatory theorem cannot be reached by first-order demand reasoning +
certified budgets: a flush-free structure can route every rotational demand
through B1 overhang-press chains (to the top wall) and confined-presser wall
terminations (u = sin^2 d, A48 C5b) — every step locally an exact FJ balance.
The ONLY remaining question is GLOBAL: can that routing close into a critical
configuration of 11 disjoint squares at s <= s0? A49 asks the configuration
space directly:
- Outcome A: a flush-free critical point survives all audits => flush-mandatory
  is FALSE (discovery).
- Outcome B: zero survivors + the flush-acquisition map (where and how descent
  creates flush contacts) = the empirical shape of the missing global lemma.

## 2. Seeds (results/seeds.json; notes/seed_design.md)

Architecture 4B/3M/4T-staggered (evolved from the brief's variants — the
constructor iterations THEMSELVES produced two small geometric facts, recorded
in seed_design.md v2/v3):
- exactly 4 squares in the near-upright binding chain (3 cannot reach the
  walls, 5 cannot fit);
- a STRAIGHT near-upright chain advances ~1.0 per corner contact and spans
  ~4.0 > s0: the binding chain must STAIRCASE — consistent with A48's picture
  that near-flush chains are geometrically cramped;
- presser congestion (presser extent ~1.04 > chain pitch ~0.98) forces the
  A48 architecture exactly: interior chain squares get pressers, the wall-end
  square terminates at the wall (T-a branch).

| id | profile (deg) | press mode | lam-1 | s_rep | min class gap |
|----|---------------|-----------|-------|-------|----------------|
| S01 | uniform 2.0-3.8 | P-CONF | 0.109 | 4.482 | 0.35 deg |
| S02 | uniform 2.0-3.8 | P-B1 | 0.109 | 4.448 | 0.35 |
| S03 | escal 1-4 | P-CONF | 0.108 | 4.452 | 0.35 |
| S04 | escal 1-4 | P-B1 | 0.108 | 4.416 | 0.35 |
| S05 | alt +-2.0-3.8 | P-CONF | 0.106 | 4.473 | 0.35 |
| S06 | alt +-2.0-3.8 | P-B1 | 0.106 | 4.439 | 0.35 |
| S07 | uniform 3.0-4.8 | P-CONF | 0.107 | 4.548 | 0.35 |
| S08 | uniform 3.0-4.8 | P-B1 | 0.107 | 4.516 | 0.35 |
| S09 | uniform 5.0-7.1 | P-CONF | 0.104 | 4.671 | 0.35 |
| S10 | uniform 5.0-7.1 | P-B1 | 0.104 | 4.644 | 0.35 |
| S11 | midtilt 2/8/15/20 | P-B1 | 0.296 | 4.910 | 0.35 |
| S12 | uniform 1.0-2.5 | P-CONF | 0.120 | 4.498 | 0.35 |

Press positions carry the A48 exact calibrations (C5b confined u = sin^2 d for
P-CONF; C1 bridge u = (sin d / sin g) cos(g-d) for P-B1). Seeds are LOOSE
(repair-feasible, flush-free as a stratum property via the 0.35-deg tilt comb);
the descent forms the actual contact staircase — seeds select basins.

## 3. Run census (free descent, 12 seeds x 1 + 20 replicas)

Producer `code/hunt_a49.py`, data `results/hunt.json`. 252 runs = 12 seeds x
(1 base + 20 Gaussian replicas, centres sigma 0.02, angles sigma 0.3 deg, fresh
RNG per replica, `repair`ed before the descent). Descent = A37
`a37_drain.free_descent`, control flow verbatim (the A37 files are never
edited), instrumented with a solver-iterate trace. tol_f = 0.05 deg,
contact/wall-activity tolerance 1e-6.

| outcome | n / 252 |
| --- | --- |
| **(a) flush-free landing that survives the CP screen** | **0** |
| (a-raw) landing flush-free at tol_f, before the screen | 17 |
| **(b) flush acquired** | **252** |
| **(c) drains to a known family** | **235** |

- **Zero candidates.** All 17 flush-free landings are *constructively* NOT-CP:
  nnls residual 0.7406-0.7452, LP descent rate -1.0, and an explicitly produced
  smaller-s packing with gain 2.9e-4 … 5.7e-1. They sit at s = 4.099-4.571 —
  stalls of the descent *above* the trivial grid, not critical points.
- The 235 matched landings are catalogue families 34/38/39/40/41/42/56 — every
  one of them at s = 4.000000000, i.e. the **axis-aligned 4x4-grid packing** in
  different rattler / relabelling encodings (87 land on catalogue 34 alone).
  The remaining 17 are exactly the flush-free non-critical stalls
  (`NEW-FLUSH-FREE`).
- **min s over all 252 A49-seed runs = 4.000000000000012.** Nothing from the
  evasion architecture came within 0.12 of s0 = 3.877084; the seeds sit in the
  basin of the trivial grid, not near any interesting critical point.
- Per press mode: P-CONF 126 runs / 0 candidates, P-B1 126 runs / 0 candidates.
  No profile behaved differently.

## 4. Flush-acquisition map

Data: `results/hunt.json` -> `aggregate.flush_acquisition_map` and the
per-run `acquisition` / `acquisition_fd` records.

**Resolution problem, and what was done about it (method, recorded honestly).**
One `pack11.polish` call is a *complete* SLSQP solve, and from these seeds it
carries the configuration from s ~ 4.5 to the landing in a SINGLE step — and
its intermediate SLSQP iterates are infeasible by O(1e-1). So neither
`free_descent` nor A37's `local_descent` (whose unit step is that same solve)
can say WHERE flush is acquired: both put the event at the landing. Two traces
were therefore recorded:
1. *solver-iterate trace* of `free_descent` (scipy `callback` on every SLSQP
   and L-BFGS-B iterate; instrumentation only, arithmetic untouched) — ~4700
   points/run, event taken only on iterates feasible to 1e-7. Fires 252/252,
   median s at event 4.0000000000 (`acquisition_fd`);
2. *feasible-path micro-descent* (`micro_descent`): the same SLSQP steps, each
   SUBDIVIDED into increments of 0.02 in the sup norm with exact-feasibility
   repair at every increment, so **every trace point is a genuine feasible
   11-square packing** and the flush definition applies verbatim. All 97
   recorded events sit on points feasible to 2.2e-16. This is the primary map.

**The map (97 micro-path events).**

| first-flushing category | n | share |
| --- | --- | --- |
| B-wall (bottom-chain wall termination) | 33 | 34% |
| top T-T (top-deck chain link) | 31 | 32% |
| chain B-B (binding-chain link) | 18 | 19% |
| T-wall (top-deck wall termination) | 15 | 15% |
| **press M-B** | **0** | **0%** |

- **Modal first-flush contact by press mode:** P-CONF -> `top T-T`;
  P-B1 -> `B-wall`. By profile: `B-wall` for uniform1 / escal / midtilt,
  `top T-T` for uniform2 / alt2 / uniform3 / uniform5.
- **Median s at acquisition = 4.0000000000375** (range 4.000000000 - 4.4934);
  20/97 runs kept descending after the event. Flush is acquired essentially
  *at* the collapse onto the grid, not on the way to it.
- **Acquisition is a SIMULTANEOUS collapse, not a sequence.** Distribution of
  the number of contacts violating flush at the event: 1 contact in 20 runs,
  **10 contacts in 67 runs, 13 contacts in 10 runs**. In those 67/10 cases the
  event spans 4 / 6 role categories at once — the whole packing goes
  axis-aligned together.
- **The informative cases are the 20 solo events, and 19 of the 20 are
  `B-wall`** (role pair `B0+wall`, i.e. the bottom chain's wall termination;
  the remaining one is `top T-T`). When flush is acquired one contact at a
  time, it is the **wall termination of the binding chain** that goes first.
- **The press contact never flushes first: 0 of 97 events involve an M-B press
  row**, and M-rows appear at all only inside the 10 largest simultaneous
  collapses. The A48 presser is *not* where the evasion breaks; the wall
  terminations and the top-deck chain are.
- The solver-iterate trace agrees on the mode ordering with the decks swapped
  (top T-T 111, T-wall 78, chain B-B 34, B-wall 27, M-rows 2) — i.e. under the
  aggressive penalty leg it is the *top deck* that flushes first; under the
  feasible path it is the bottom wall termination.

## 5. Stratum-constrained descent + FJ tests

Producer `code/stratum_a49.py`. Stratum rows are encoded smoothly and
**exactly**: with Delta = th_i - th_j, `sin^2(2 Delta)` has period pi/2,
vanishes exactly on Delta = 0 mod pi/2 and is strictly increasing in the folded
class distance on [0, pi/4], so

    g_ij = sin^2(2(th_i - th_j)) - sin^2(2 eps) >= 0  <=>  class-dist >= eps

(and `sin^2(2 th_i) - sin^2(2 eps) >= 0` for class-from-axis, the class
distance to angle 0). C-infinity, so a fortiori C1 for SLSQP; gradients
2 sin(4(th_i - th_j)) and 2 sin(4 th_i). Jittered starts are made
stratum-feasible by a *tilt comb* (11 classes + the pinned axis class relaxed
apart on the circle R/90deg). SLSQP steps are accepted damped (walked back
until feasible, stratum-feasible and s-decreasing), with A37's LP-descent
fallback when the fixed-axis linearisation stalls.

**(2) Global stratum, eps_s = 0.25 deg, all 55 pair rows + 11 axis rows
(`results/stratum.json`, 252 runs = 12 seeds x (1 + 20 replicas)).** This is
strictly STRONGER than flush-freeness (it constrains all pairs, not only
contacting ones, and at 0.25 deg rather than tol_f = 0.05 deg) — stated as
intended: interiority here implies interiority of the flush-free set.

| verdict | n / 252 |
| --- | --- |
| PRESSED-ON-FLUSH-BOUNDARY (>= 1 stratum row active at 1e-6 deg) | **251** |
| INTERIOR, and NOT-CP under the full FJ test | 1 |
| INTERIOR-CANDIDATE | **0** |

  Active-row count per minimiser: 11 rows in 123 runs, 10 in 102, 9 in 19; 2289
  pair rows and 291 axis rows active in total. Median landing s = 4.01287, min
  4.00173 — **the flush-free stratum costs about +0.013 in s** relative to the
  unconstrained landing at 4.000000000. The single interior point (S11/r3,
  s = 4.9494) fails Fritz-John outright: nnls residual 0.740, LP descent rate
  -1.0, constructive witness gain 0.949.

**(2b) LOCAL stratum, eps_l = tol_f = 0.05 deg, rows = only the contacting /
near-contacting pairs and wall-touching squares, re-selected every round
(`results/stratum_local.json`, 72 runs = 12 seeds x (1 + 5 replicas), the
brief's protocol).** This constrains exactly what flush-freeness requires and
nothing more, so it is the sharp test.

| verdict | n / 72 |
| --- | --- |
| BLOCKED-BY-FLUSH-BOUNDARY | **72** |
| INTERIOR (any) | 0 |
| INTERIOR-CANDIDATE | **0** |

  BLOCKED means: at the stopping point *every* improving step — the damped
  SLSQP step at every scale down to 1e-3 of it, and the LP descent direction of
  the audited active rows — **leaves the flush-free set**. The descent can only
  continue by acquiring flush. Median s = 4.00301, min 4.00001.

**Summary of (2): 0 of 324 stratum minimisers is an interior flush-free local
minimiser.** Every one is pressed against, or blocked by, the flush boundary.

## 6. Candidate audits and verdict

Producer `code/audit_a49.py`; per-candidate JSON would go to
`results/candidates/`. **Candidates from (1a) + (2ii): 0. SURVIVORS: 0.**

SURVIVOR would have required *all* of: GN refine converged (<= 1e-30) and moved
the point < 1e-6; the refined point still flush-free at tol_f; no constructive
descent witness (LP-direction hunt at 1e-4…1e-8 from the refined point **and** a
strict monotone always-feasible A37 `local_descent` probe); **Fritz-John
stationarity numerically satisfied** (nnls residual for e_s in the active-row
cone <= 1e-6 AND LP descent rate >= -1e-6); and a VALLEY / RIGID /
RATTLER-CORE class. The FJ rows are required explicitly because a `VALLEY`
label alone is not evidence — `a37_pipeline.classify` falls back to VALLEY
whenever its rank test is inconclusive, which is exactly what a
few-contact junk point produces.

Two audit-integrity items, recorded:

1. **Machinery self-test.** Run on atlas family 31 the audit reproduces it
   (rematch -> catalogue 31, VALLEY, rank 30, GN residual 7e-71) and the flush
   detector reports its flush contacts, i.e. it is correctly NOT flush-free.
2. **A repair-cap bug found and fixed (worth banking for reuse).**
   `a37_drain.repair` bisects the least scale lam >= 1 that removes every
   overlap, but its search is capped at `lam_hi = 1.10`; handed a badly
   overlapping point it returns a **still-overlapping** configuration with a
   spuriously small s. A37's own use was safe (near-feasible inputs). A first
   local-stratum sweep trusted it and accepted 7/252 infeasible points, 4 of
   which surfaced as spurious "INTERIOR-CANDIDATE"s (all 4 were rejected by
   the audit anyway: nnls 0.74, LP rate -1.0). A49 now wraps it as
   `a49_common.repair_ok` (lam_hi = 8, explicit feasibility check) and
   re-ran both stratum sweeps from scratch. **Verified after the fix:** all 252
   census landings, all 63 negative-control landings and all 252 global-stratum
   minimisers are feasible to <= 6.7e-16; the superseded runs are kept under
   `work/*.SUPERSEDED_repair_cap_bug.json`.

**Negative control (task 4, `results/control.json`, `--control`).** The three
atlas VALLEY entries — families 27, 31 and A37-NEW-0, taken at FULL precision
(the A04 catalogue point and the A37 drain record; `atlas_final`'s
`canonical_sig` is rounded to 6 decimals, which alone fakes a ~2e-6 descent
witness) — jittered with the same sigmas, 21 runs each through the same census
machinery:

- **63/63 landings have flush contacts present** (median 11 flush violations
  per landing; 392 wall + 318 pair violations in total). The flush detector
  fires exactly where it should.
- Rematch: A37-NEW-0 **21/21** to its own family; family 31 14/21 to its own
  (7 jitters hop to a neighbouring basin); family 27 7/21 — it is the
  VALLEY-MARGINAL entry and 11 jitters drain to catalogue family 6 at
  s = 3.886746, consistent with A37's own note that 27 is the shallow one.
  The three un-jittered base runs: 31 and A37-NEW-0 hold *exactly* at their own
  s and rematch to themselves; 27 drains to family 6.

**VERDICT: OUTCOME B.** No flush-free critical point was found. Under free
descent the A48 evasion architecture does not merely fail to be critical — it
is not even close: it drains to the s = 4 axis-aligned grid, acquiring flush
in a simultaneous ~10-contact collapse, and every flush-free stopping point is
constructively non-critical. Under flush-free-constrained descent, 324/324
minimisers are pressed against or blocked by the flush boundary. This is
consistent with flush-mandatory and does not prove it; what it delivers is the
empirical shape of the missing global lemma (section 4): the presser is never
where the evasion breaks, the **wall termination of the binding chain** is.

## 7. Gap list

[PENDING — finalized at close]

## 7. Verdict (advisor close-out; lead terminated by usage limit after compute completed)

OUTCOME B, maximally clean. 252/252 evasion-architecture drains acquire flush (0 candidates, 0
survivors under the strengthened FJ-stationarity audit); 72/72 local-stratum minimisers are
BLOCKED-BY-FLUSH-BOUNDARY (every improving direction leaves the flush-free set; 0 of 324 stratum
minimisers interior); flush-freeness costs +0.013 in s; nothing from the evasion seeds came within
0.12 of s0 (min s = 4.000000000000012 — all drains land on the s = 4 grid families).

BANKED EMPIRICAL LAW (the flush-acquisition map): the evasion never breaks at the presser — it
breaks at the BINDING CHAIN'S WALL TERMINATION (B-wall dominant; 19/20 solo events), and
acquisition is a simultaneous collapse (10-13 contacts at once). A future global proof of
flush-mandatory should formalize chain wall-termination instability.

SAMPLING CAVEAT (honest): 12 seed architectures, all in the near-upright evasion world; every
drain landed on s = 4 grid families. The mid-tilt flush-free world was not sampled directly;
A47's T1 + C4 (universal non-thinness) cover the thin part of it, but mid-tilt non-thin flush-free
basins remain unsampled. I-L19 remains a (now strongly corroborated) global-realizability
conjecture; no theorem is claimed from this experiment.

Also banked: the a37_drain.repair lam_hi bug (silently returning overlapping points) found and
fixed (a49_common.repair_ok); superseded data quarantined; all final data feasibility-verified to
<= 6.7e-16.
