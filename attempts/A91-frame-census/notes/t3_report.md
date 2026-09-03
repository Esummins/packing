# A91 T3 pilot — per-frame exclusion COST (no certificate emitted) — 2026-09-03

Cost measurement only: float intervals, HiGHS LPs, no interval certificate, no FJ
rows (we exclude *packings*, not critical points, per the spec). Code
`code/{real91.py,pilot91.py}`; raw `results/t3pilot91.json`, log `logs/pilot.out`.

## Engine

Per frame: the A88-style **core-box B&B** on tilt bins. Root box = θ_i ∈ [0°,45°]
for all 11 squares, s ∈ [3.82, 3.877084]. At each box the sound interval-linear LP
of `real91.build_rows` (23 variables = 22 centres + s; rows: containment, wall-mask
rows from ω, corner-intrusion rows for home squares, Lemma K argmin-side **type**
rows, Lemma F6 **link** rows for every column link, pressing rows (c_N−c_M)·e ≥ −1).
LP infeasible ⇒ that tilt box holds no realisation. Otherwise bisect the widest
tilt bin. Caps: 20 000 boxes, 600 s, tilt-bin floor 1e-3 rad.

## Measurement (20 frames drawn uniformly from the R1-surviving L0 stratum,
each given a random terminal assignment and a random full column system)

| quantity | value |
|---|---|
| frames piloted | 20 |
| **CLOSED** | **20 / 20 (100%)** |
| boxes per closed frame | **1** (the root LP is already infeasible) |
| **mean cost** | **3.8 ms/frame** (range 3–5 ms) |
| R6 root verdict on those 20 | all "not realisable" (they are the 99.7% of §4 of `t2_report.md`) |

So for the generic frame the certificate is a **single LP**: 3.8 ms, no bisection.
This is the good news and it is the whole of the good news.

## The archetype does NOT close

C1 (Trump-with-2-crowds, the exact archetype) run through the same B&B:

| | |
|---|---|
| verdict | **OPEN** |
| root LP margin | **+0.10355** (feasible; R6 does not kill it) |
| boxes explored | 111 |
| killed leaves | 0 |
| wall-clock | 0.30 s |
| stop reason | tilt-bin floor: **all 11 bins bisected to < 1e-3 rad (bisection depth 10 per square)** and not one leaf became infeasible |

**Answer to the spec's question "at what depth does the archetype close or fail":
it fails, at depth 10 — the box-level relaxation never closes it, at any tilt
resolution the pilot can reach.** The reason is structural, not numerical: C1 is
anchored entirely by 2- and 3-member (I)-columns (see `t2_report.md` §5.2), all of
whose rows are satisfied by Trump's own geometry up to the relaxation; the only
statements that could exclude it are the *rate/plateau* statements (Lemma PLATEAU),
which are not box-level linear rows at all.

## Price

* realisable-at-L2 (EXTRAPOLATED, `t2_report.md` §4): **≈1.2e38** frames labelled
  (bracket [1e36, 1e39]); mod G ≈ 1.6e35.
* cost of the cheap 99.7%: 3.8 ms each ⇒ **1.2e38 × 3.8 ms ≈ 1.3e32 CPU-hours**.
* cost of the expensive 0.3%: unbounded — the pilot cannot close a single one.
* A85's measured tree: **3 200 – 7 000 CPU-h**.

**Verdict: the frame-census route to ¬RES(4) loses by ~28 orders of magnitude, and
it loses twice over** — the census is too big *and* the frames that matter (the
R6 survivors, including the archetype) are exactly the ones the per-frame
certificate cannot close. Even a hypothetical 1 µs/frame test and a further 1e10
quotient would leave 1e25 frames.

## What would have to change for the route to live

1. **Apply the geometry at L0, not L2.** L0 has 1.9e16 orbits (EXACT lower bound
   1.25e16) and the R6 rows for an L0 skeleton (no links) are much weaker; a kill
   at L0 covers all its refinements. 1.9e16 × 3.8 ms = 2e10 CPU-h — still 6–7
   orders too many, so even this is not enough without a further structural
   quotient.
2. **Make Lemma PLATEAU load-bearing.** The measured archetype uses only mutual
   (I)-anchoring; no box-level linear relaxation can exclude it, so ¬RES(4) needs
   the rate-equality/slide argument (`nocrit_k0_blocked.md` §4.3, currently `[C]`)
   to become a theorem, or the (I) case has to be reduced to (W) by the plateau
   slide. That converts the whole census into "wall-anchored frames only", where
   Lemma COL's ≥3-member clause finally has teeth.
3. Otherwise: pay ¬RES(4) as a **SelForm (C) leaf inside A85's tree** (A90 §6(i)),
   whose price A85 already measured as zero-at-depth / silent-at-the-frontier.
