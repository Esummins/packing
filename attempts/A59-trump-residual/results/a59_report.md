# A59 — trump5 as an 18-d anchored grain problem: census, pilot, and the composed finite program

Fable lead, Opus compute workers; 2026-09-01. Everything at s0 = 969271/250000 = 3.877084,
s_T = 3.8770835900228…, h = 3.7e-3 (the A36 basin radius, sup-norm in (cx, cy, theta_rad)).
Authoritative details: notes/theory.md (T1–T5', gap list), results/census_report.md,
results/pilot_report.md. Total new compute this attempt: ~4 hours across two single-process
workers (census 193 s; pilot 43.8 min of solves + ~30 min exact scans). A29 untouched.

---

## Headlines

1. **The Level-0 grain census of the residual polygon is ~4.4e10** (exact bracket
   [2.29e6, 8.22e11]; 91 admissible anchor masks; canary PASS) — the anchored regime does NOT
   make the contact-structure census small, and every census filter is a containment filter
   (the F4/A43 law at Level 0). **The grain is the wrong certificate unit by ten orders of
   magnitude.** The census survives as a map plus banked lemmas (corner capacity 3 proved via
   the pin; the completion list corrected 8 -> 6).

2. **The right unit is the residual zone-tree cell, and its program is GO: ~1e4–1e5 exact
   certificates ~ SINGLE-DIGIT DESKTOP-DAYS at 5 processes** (measured cost model, one
   extrapolation step). The cost product that the brief asked for is therefore NOT
   4.4e10 x anything; it is (zone cover 1.1e3 + residue ladders ~34/level x ~24 levels x 3
   squares + confinement certs) x (0.8–90 s each), plus the A56 s-parametric overhead on the
   kill leaves.

3. **The mechanism is confinement, not killing.** Everything Trump-adjacent is rigorously
   unkillable (Lemma A57-3 alive-certificates: every sibling YES child at every depth and
   half-width has its budget-many surviving Trump witnesses — the T5'.3 sibling-kill ladder is
   IMPOSSIBLE, not expensive). The tree closes anyway: the unkillable residue stays bounded
   (21–52 boxes across 24 measured levels) and contracts onto Trump at gap ≈ 4.6 x box radius
   until, at level 24, every residue box lies inside the A36 basin slice. r_kill = 4.55·hw
   exactly; the G-A59-9 annulus closes at 2.19 extra bisection levels (hw <= 8.13e-4) —
   **genuine (D) discharge leaves exist; no A40 basin growth, no (W')-wedge work needed.**

---

## 1. What A59 delivered, by leg

**(a) THEORY (notes/theory.md).** The stratum-restricted drain, written carefully:
- T1: the trump5 stratum IS the feasible set of a 19-variable NLP (6 free squares + s; pins at
  slots(s) as fixed obstacles); normalization is rigid (the pins touch all four walls — the
  drain lemma's normalization caveat L6(iv) is discharged inside this stratum).
- T2: the UPWARD TRAP. Six one-cell Young completions of trump5 — {k6_07, k6_19, k6_21, k6_22,
  k6_23, k6_24}, matched exactly to A53's certified classes (results/completions.json) — cover
  every strictly-larger skeleton via maximal chains; all six carry PASS kill certificates
  (A53 x5 + A54 W1). Hence, unconditionally at s = s0: the stratum's upward boundary is EMPTY —
  the drain cannot escape up. (The brief's "8 completions" over-counted: two addable cells
  overlap a pin for every s in the window — A53 L2(iii), i+j = 2 — and are vacuously dead.)
- T3: restricted drain theorem — attainment, no upward escape, slide-stuckness AUTOMATIC for
  every point of the stratum (stronger than A53 L6's selection), FJ necessity for the 19-var
  NLP, floor s > 3.82 from the certified measure bound.
- T5': the zone-tree composition theorem — (K) kill leaves / (C) logic leaves / (D) discharge
  leaves into the A36 basin slice, with the s-range clause stated honestly; trump5's own
  liveness is now rigorous (tau* >= 6 = budget with STRICT exact gap 1.0574e-7,
  attempts/A57-shadow-trees/results/alive/trump5_strict.json), so the Trump-containing chain is
  alive-certified and never killed.

**(b) CENSUS (results/census_report.md).** Honest number ~4.4364e10 (MC ±1%), rigorous bracket
[2 290 359, 822 380 205 647], 91 masks, exact ablation (planarity is the dominant filter, x30),
per-anchor caps proved (corner cap 3 via the pin), canary PASS, 193 s. Verdict: grain unit dead
(Headline 1); the explosion is not rattler-driven (84.8% of grains have all six squares
anchored, exact) and Trump's grain has no Level-0 signature (~2e9 grains share its profile).

**(c) PILOT (results/pilot_report.md).** The zone-tree measured on trump5 itself, A54/A57
discipline throughout (exact-cert-only verdicts, pinguard, trump_realizes, t-uniform windows;
87 PASS certificates written, 6 independently re-verified at depth 60, zero canary/engine-bug
events). Results feeding the program: the tau* = k law (17/18, §4 below), the killability
census (344/1152 free logic kills, 41 unkillable at level 1), the residue ladder (bounded at
~34 boxes/level, basin containment at level 24), r_kill = 4.55·hw, confinement kills at every
depth j = 2..5 (zero-atom vacuity at budget 1: 0.5–1.5 s each; knife-edge 0.011 headroom at
j = 2), branching collapse 41 -> 18 -> 7 -> 0 -> 0, and the two engine changes (G-A59-11).
**Lemma A59-P1 banked** (exact certificate, re-verified): every 11-packing whose skeleton
contains the trump5 pins has a square centred in the interior zone [1.1, 2.777]² (at s0).

**(d) THE COMPOSED FINITE PROGRAM** — section 2, with the price in section 3 and the honesty
ledger in section 5.

---

## 2. The finite program, stated precisely

Target theorem: **the trump5 stratum contains only Trump** — every 11-packing with skeleton
trump5 and sigma in (3.82, s0] has sigma >= s_T, with equality iff it is Trump's packing.
By T3 + T5' this reduces to the following finite, machine-checkable list. Arbiters in brackets;
every kill is an exact rational certificate through verify_case.py; no LP value is ever a
verdict (A54 S0).

P0 ENGINE (G-A59-11, both pilot-validated, do first):
   (i) alive-gate: compute k(N) = # surviving strictly-separated Trump witnesses (exact
   rational, ~1 ms) before any solve; k(N) >= budget(N) => provably uncertifiable (Lemma
   A57-3) => never launch the LP. (ii) budget-1 nodes: zero-atom vacuity certificates via
   vac59 (no LP; caselp's EPS_CORE/EPS_ZONE = 2e-3 floors sit at the same scale as h and blind
   the LP-gated route in the discharge regime). Keep pinguard, trump_realizes, t-uniform
   theta windows, columns-only warm starts.

P1 UPWARD TRAP [T2, done at s0; A56 for the window]: the six completion classes
   {k6_07, k6_19, k6_21, k6_22, k6_23, k6_24} certified over s in [3.82, s0] by A56's
   parametric recipe (interval-s verification, the A47 parameter-box pattern). This is the
   priority list already handed to A56.

P2 ROOT DISCIPLINE [done]: trump5 alive-certified with a strict exact gap (A57 T8 artefact);
   the root and every Trump-containing chain node are (D)-chain, refined, never certified.

P3 SQUARE-1 LOCALISATION [measured end-to-end at depth 0]: interior zone cover (Lemma A59-P1
   is the NO side; 1152 YES boxes: 344 contradictory = free, 767 attemptable LP kills at
   1–290 s, 41 alive-gated unkillable); then the residue ladder — bisect only the unkillable
   boxes, re-running pinguard + alive-gate per sub-box (~34 boxes/level, 24 levels), killing
   the newly-attemptable sub-boxes, until every residue box lies inside the A36 basin slice of
   the Trump placement it hugs (measured: level 24, 28 boxes, all inside).

P4 SQUARES 2..6 [level-1 census measured; ladders extrapolated — G-A59-10]: condition the
   located square in a basin-radius box and repeat on the next interior square (order sq7,
   sq8, sq9, then sq4, sq6, sq10). Measured at basin-radius conditioning: 93.3% of the level-1
   cover goes contradictory at j = 1, 97.0% at j = 2, and the unkillable residue is 18 at
   j = 1, 7 at j = 2, **0 from j = 3 on**. From j >= 2 use single confinement NO kills
   (budget 6−j; measured PASS at j = 2, 3, 4, 5; essentially free at j >= 3, knife-edge 0.011
   headroom + 542 s at j = 2 — so prefer zone kills to reach j = 3, confinement after).

P5 LADDER DEPTH [measured]: run every confinement/refinement ladder to hw <= h/4.55 = 8.13e-4
   (the annulus closure, +2.19 levels beyond the basin radius), at which point the six core
   boxes and the confined sixth square are all within h of Trump's placements: a genuine (D)
   leaf. Discharge by the A36 composed theorem restricted to the slice (theory.md T5/T5'.2).

P6 THE s-WINDOW [G-A59-7, the honest conditionality]: every (K) leaf of P3/P4 is certified at
   s = s0 only. The low-s slab (3.82, s_T − h) is STRUCTURALLY invisible at fixed-s nodes
   (pilot M4: a shrunken-Trump packing has its BR/TR pins displaced up to 5.7e-2 — outside the
   hypothesis class), so the window is delivered ONLY by re-running the kill leaves through
   A56's parametric verifier. Price = A56's measured overhead multiplier x the (K)-leaf count
   (~1e4–1e5). A56's cost curve is the one external number the program still needs.

P7 COMPOSITION [T5', pure logic]: P1 (upward) + P2 (root) + P3–P5 (every leaf K, C, or D) +
   P6 (window) + the A36 basin theorem => the target theorem. Together with the k >= 6 tier
   (closed), k = 5 non-Trump (19/21 closed; k5_11, k5_16 in A57's tree now), k = 4 (A55) and
   the k <= 3 program (A58), this is the Trump-stratum leg of s(11) = s_T.

---

## 3. The price (measured -> composed)

| item | count | unit cost (measured) | subtotal |
|---|---|---|---|
| P3 zone cover: free logic kills | 344 | 0 s | 0 |
| P3 zone cover: LP kills (budget 5) | 767 | 1–290 s, A57 mean well under 240 s | ~13 CPU-h |
| P3 residue ladder | ~24 levels x ~34 | 0.8–90 s (mix vacuity/LP) | ~1–13 CPU-h |
| P4 square-2 and square-3 ladders | residues 18, 7; ladders extrapolated | as P3, cheaper (93–97% free) | ~2–15 CPU-h |
| P4 confinement certs, j = 2..5 | O(10) | 0.8 s (j=5) – 542 s (j=2) | < 1 CPU-h |
| P5 annulus extension | +2.19 levels, inside the 24 measured | — | included |
| **tree total** | **~1e4–1e5 certificates** | 0.8–90 s typical | **single-digit desktop-days at 5 processes** |
| P1 upward trap | 6 classes | A56 recipe | A56's ticket (in flight) |
| P6 window transfer of (K) leaves | ~1e4–1e5 | A56 overhead multiplier — **unmeasured** | the open cost line |

The pilot itself: 185 solves, 43.8 min of LP+cert time; 64% of its LP seconds were spent
re-discovering in 200–340 s facts the alive-gate proves in 1 ms — hence P0 before anything.

---

## 4. The tau* = k law (conjecture, with its evidence and its exception)

Define k(N) = the number of Trump's six free squares (A57 T8 strictly-separated scaled form)
strictly disjoint from every core and outside every NO-family of node N. Lemma A57-3 proves
tau*(N) >= k(N) — this direction is load-bearing (the never-attempt gate) and rigorous. The
pilot measured tau_LP = k in **17 of 18** converged solves across budgets 1–6; the documented
exception (conf_j4_hw0.02_a0.075: tau = 2 > k = 1 — an eleventh square fits just outside the
too-small NO-family, a disjoint pair that is NOT a sub-family of Trump's six) shows k is a
lower bound only. CONJECTURE (G-A59-12): tau* = k on trump5 nodes when the NO-family is large
enough to swallow its witness. If proved, the tree becomes an exact combinatorial computation
with the LP demoted to certificate construction. Not assumed anywhere in P0–P7.

---

## 5. Honesty ledger (what is proved, measured, extrapolated, conditional)

PROVED (exact certificates / rational arithmetic): the six-completion upward trap at s0;
Lemma A59-P1; trump5's strict liveness; corner cap 3; the 87 pilot kills (6 re-verified at
depth 60); every ALIVE verdict (Lemma A57-3, exact); r_kill values and the level-24 basin
containment (each a PASS/FAIL pair of exact certificates).
MEASURED (honest numbers, not certificates): the census 4.4e10 (rigorous bracket around an MC
point estimate); the killability censuses; cost tables.
EXTRAPOLATED (G-A59-10): the residue ladders for squares 2 and 3 (level-1 censuses measured,
ladders not run); the 1e4–1e5 total. One clean falsifier: if a depth-2 ladder's residue fails
to contract like depth-0's, the estimate breaks — first thing the campaign should check.
CONDITIONAL: the window form of everything rests on A56 (G-A59-7, now subsuming the slab
question G-A59-8); the six-class list is with them, the (K)-leaf overhead multiplier is not
yet priced. At s = s0 exactly, nothing in P1–P5 is conditional.
REFUTED AND REPLACED: T5'.3's sibling-kill arithmetic (the pilot proved those kills cannot
exist; the residue-ladder model replaces it — theory.md carries both, labelled).

## 6. Verdict

**GO**, on the zone-tree program P0–P7 as stated: the annulus closes (r_kill/h = 4.55, closed
by +2.19 levels), the residue is bounded (~34/level), the nesting collapses (branching depth
three), and the composed cost is single-digit desktop-days at 5 processes — against the ~10
desktop-day GO threshold proposed in notes/pilot_design.md. Conditions attached: P0 engine
changes first; G-A59-10's depth-2 ladder check early (the falsifier); the A56 dependency
carried honestly (P1 small and already queued; P6 priced when A56's cost curve lands).
No FJ-alarm, no canary event, no engine bug in either worker.

## 7. Files

    notes/theory.md          T1–T5' + gap list G-A59-1..12 (the drain, the trap, the tree)
    notes/pilot_design.md    v2 pilot spec (v1 superseded, kept)
    results/census_report.md + census_summary.json + grains_sample.jsonl + completions.json
    results/pilot_report.md  + pilot_zonetree.jsonl + rkill_*.json + m2_*.json + conf_ladder.json
    certs/                   87 PASS certificates + .PASS markers (m3_trump5_interior_NO = A59-P1)
    code/                    census: geomlib/graphlib0/count_exact/canary/census/completions;
                             pilot: alive59/vac59/scan59 + adapted A57 stack
