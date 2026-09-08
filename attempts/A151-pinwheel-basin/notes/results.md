# A151 — results

## T1. Kill rates by A107 shadow family, from the night (A137) and the day (A149)

Three lanes, kept apart (`notes/method.md` §1). Tables: `results/family_rates.md`,
data `results/family_rates.json`.

### L1 — exact-pin-core RE-SOLVE of the pre-existing ALIVE population (222 nodes)

| family | n | PASS | NO-KILL | LOST-KILL | TOO-TIGHT | FAIL | CAP | **kill rate** | median wall |
|---|---|---|---|---|---|---|---|---|---|
| **S02** | 57 | 21 | 17 | 11 | 6 | 2 | 0 | **36.8 %** | 513 s |
| S01 | 96 | 24 | 65 | 3 | 2 | 0 | 2 | 25.5 % | 386 s |
| other shadows | 42 | 7 | 31 | 2 | 2 | 0 | 0 | 16.7 % | 321 s |
| post-A107 | 27 | 5 | 18 | 4 | 0 | 0 | 0 | 18.5 % | 460 s |
| **all** | 222 | 57 | 131 | 20 | 10 | 2 | 2 | **25.9 %** | 444 s |

(57 PASS = A137's 46 + A149's 11, the two `superseded_by_exactcore_*` ledgers.)

**τ at the exact core, by family and outcome** (budget = 5; a kill needs τ < budget):

| family | PASS τ (min/med/max) | NO-KILL τ (min/med/max) | near-miss band (LOST + TOO-TIGHT) |
|---|---|---|---|
| **S02** | 4.000 / **4.750** / 4.844 | **5.000 / 5.000 / 5.000** | **17 of 57 = 29.8 %**, τ ∈ [4.500, 4.909] |
| S01 | 3.000 / **4.000** / 4.846 | 5.000 / 5.000 / 5.500 | 5 of 96 = 5.2 % |
| post-A107 | 4.000 / 4.000 / 4.529 | 5.000 / 5.000 / 5.143 | 4 of 27 = 14.8 % |

### L2 — first LP of a child emitted that night, exact cores (189 nodes)

| family | n | PASS | decided | **kill rate** | median wall |
|---|---|---|---|---|---|
| **S02** | 22 | 13 | 21 | **61.9 %** | 484 s |
| S01 | 21 | 14 | 21 | 66.7 % | 446 s |
| other shadows | 14 | 11 | 14 | 78.6 % | 227 s |
| fractional | 17 | 17 | 17 | **100.0 %** | 498 s |
| post-A107 | 115 | 94 | 115 | 81.7 % | 82 s |
| **all** | 189 | 149 | 188 | **79.3 %** | 201 s |

### L3 — geometric leaves at emission (2,940 screened, 798 dead)

| family | screened | dead | T5′ exact core | T5‴ clip | T5⁗ polygon | **kill rate** |
|---|---|---|---|---|---|---|
| **S02** | 674 | 185 | 135 | **50** | 0 | **27.4 %** |
| S01 | 859 | 204 | 163 | 41 | 0 | 23.7 % |
| other shadows | 517 | 102 | 70 | 32 | 0 | 19.7 % |
| fractional | 49 | 1 | 1 | 0 | 0 | **2.0 %** |
| post-A107 | 840 | 306 | 270 | 36 | 0 | 36.4 % |
| **all** | 2,940 | 798 | 639 | 159 | **0** | 27.1 % |

Clip enrichment (share of clip kills ÷ share of the screened pool): **S02 1.37**, other shadows
1.14, S01 0.88, post-A107 0.79, fractional 0.00. **T5⁗ (K′ vs the pin core) fired ZERO times** on
all 3,034 children — at emission T5′ at the exact pin core already catches everything the polygon
core would.

### The answer to the PI's question

**Yes, but marginally, and only in the re-solve lane.** With exact cores the pinwheel is the
best-yielding family on the stubborn population — 36.8 % against the population's 25.9 % and
S01's 25.5 % — but *every* S02 kill lands within 0.25 budget units of the threshold (median
τ = 4.75 against S01's 4.00), and **29.8 % of S02 nodes land in the band where the LP sees the
kill at first solve and loses it on witness feedback or rounding**, six times S01's 5.2 %. The S02
nodes that are not killed sit at τ = 5.000000 *exactly* — the relaxation extracts literally nothing
— which is A106's "no open box contains it" in the LP's own numbers. K′ is not what makes the
difference: the polygon leaf never fired, and the geometric lane kills S02 at the population rate
(27.4 % vs 27.1 %), with only the pin-clip mildly S02-preferring (enrichment 1.37).

### The S02 population still alive, and its distance to A116's N

99 S02-family nodes are open (ALIVE or FAIL, no dead ancestor) after the night and A149's day:
k5_11 62, k5_16 37; level 1 = 64, level ≥ 2 = 35. `results/alive_s02.json`.

**36 of the 99 have already been through the exact-core re-solve and all 36 failed it**
(17 NO-KILL, 11 LOST-KILL-ON-RESOLVE, 6 TOO-TIGHT, 2 FAIL) — by construction, since the 21 that
passed are dead. Only the other **63** are re-solvable at all.

Distance to the shadow (dmax = max centre offset under A116's best injection, tmax = max tilt
offset in degrees), cumulative:

| within | r ≤ 0.02, ρ ≤ 2° | 0.05/5° | 0.10/10° | **0.20/10°** | 0.20/20° | 0.30/20° | 0.30/40° |
|---|---|---|---|---|---|---|---|
| nodes | 16 | 27 | 40 | **44** | 62 | 66 | 76 |

median dmax 0.076, median tmax 10.58°. **Of the 55 alive S02 nodes outside A116's certified
(0.2, 10°) N, 29 are excluded by TILT alone and only 2 by position alone** (24 by both). Tilt, not
position, is the coordinate that limits the consumer count — which is what set T2's growth order.

---

## T2. The ASYMMETRIC N

Ladder: `notes/t2_table.md` (every step), data `results/grow_{A,B}.jsonl`, specs
`results/spec_{A,B,combined}.json`, drawings `results/N_s02_{base,asym}.svg`.

**Base control** (`results/grow_smoke.jsonl`): the certified symmetric N at (0.2, 10°) is DEAD with
**32,570** phase-1 leaves, certified minimum **3.8770840979**, 1,000 samples → 0 hits, Trump
outside, **205 s** with phase 2 off. The leaf count is A126's control for S02 exactly.

**Largest certified asymmetric N** — worker B, `results/spec_B.json`:

| body | kind | x | y | θ (deg) |
|---|---|---|---|---|
| **f1** | free | **[0.862501, 1.662501]** | **[2.176658, 2.676658]** | **[8.435, 88.435]** |
| f2 | free | [1.724319, 2.124319] | [2.973003, 3.373003] | [38.435, 58.435] |
| f3 | free | [2.414583, 2.814583] | [2.247941, 2.647941] | [38.435, 58.435] |
| BR(0,1) | free | [3.177084, 3.577084] | [1.300000, 1.700000] | [−10.000, 10.000] |
| BL(0,0), BL(0,1), TL(0,0), BL(1,0), BR(0,0) | pins | A57 slack cores, half-width 0.00707107, tilt 0 | | |

f1's cell is **10× the volume** of A116's (x ±0.40 vs ±0.20, y ±0.25 vs ±0.20, θ ±40° vs ±10°) —
its tilt window is now almost the whole fundamental domain. **72,138** phase-1 dead leaves,
certified minimum **3.8770841** (the phase-1 bound, i.e. "> s₀"; phase 2 is off, so this is not the
chain minimum — the measured chain minimum is 3.885618 below), 615 s.

**Survivor-count rule at that N** (`results/sample151.json`, `code/sample151.py`):
**100,000 drawn → 2,959 tested (all near pairs disjoint) → 0 hits**; the box-constrained SLSQP
minimum over N is **3.885618 > s₀ = 3.877084**; Trump is outside N. Per accepted step during the
search: 2,000 drawn → 34–60 tested → 0 hits, every time.

**Second certified N** — worker A, `results/spec_A.json`: f2's tilt to **±14°** ([34.435°, 62.435°])
with everything else at the base; 105,354 leaves, 837 s.

### The certified asymmetric N in EXACT RATIONAL form (t = tan(θ/2))

The largest certified N was re-emitted through **A133's own generator and independent rational
checker**, imported unchanged with their module-level `BASE` re-pointed into this attempt so that
nothing under `attempts/A133-*` is written (`code/gen_t151.py`, `code/mk_a119_src.py`).

*Control first:* the A119-format source this attempt synthesises for the SYMMETRIC base spec is
**bit-identical** to A119's own `S02_k5_11_r0.20_rho10.cert.json.gz` on every body field
(worst difference 0.0, same `nv` = 23, same variable indices, same pins).

| | |
|---|---|
| certificate | `certs/S02_k5_11_A151asym_f1.tcert.json.gz`, `local-cert-t-v1` |
| sha256 | `a0202e530068cea742c1569f8ccd462daf683205e2d6874733c1e95174ca296d` |
| verdict | **DEAD**, 0 unresolved |
| leaves | **38,590** (11,222 infeasibility rays), 83,495 nodes, 1,491 branches |
| rows | 555,068, **555,068 implied** (independent checker: every row re-derived) |
| certified minimum | `279373377932864214632921675566579953075989 / 72057594037927936000000000000000000000000` = **3.8770844581** > s₀ |
| independent check | **VALID, 0 errors** (`results/check_local_t151.json`), 191 s |
| wall / size | 595 s to emit, 191 s to check, 26.8 MB |

This is the same object and the same format as the YES-leaf citation A136 uses
(`S02_k5_11_r0.20_rho10.tcert.json.gz`), so the asymmetric N is a drop-in replacement for it in the
region tree's YES leaf, subject to the Lean re-emission A133's T2 does for the symmetric one.

**The combined N** (f1's growth *and* f2's ±14°) is a **CONJECTURE, not certified** — widening two
squares at once is not implied by widening each alone and the verification run did not fit in the
cap. `results/spec_combined.json`.

### Where the growth stopped, and why

| knob | last certified | first refusal | refusal kind |
|---|---|---|---|
| f1 / θ | **±40°** (schedule exhausted) | — | — |
| f1 / x | **±0.40** (schedule exhausted) | — | — |
| f1 / y | ±0.25 | ±0.30 | **wall cap** (900 s, 90,801 leaves) |
| f2 / θ | ±14° | ±20° | **wall cap** |
| f2 / x | ±0.20 (±0.25 certified at the base tilt, in the discarded x-first pass) | ±0.25 | **wall cap** |
| f2 / y | ±0.20 | ±0.25 | **wall cap** |
| BR(0,1) / θ | ±10° | ±14° | **wall cap** |
| BR(0,1) / x, y; f3 / θ, x, y | ±0.20, ±10° | not reached | **budget** |

**No step was refused by geometry.** Every refusal is a wall cap with **0 LIVE-LOW witnesses and 0
unresolved leaves** — so **no real partial packing was found inside any grown N**, and there is
nothing to draw for "the first real partial packing". The 3 CPU-h cap, not the pinwheel, is what
stopped the growth; A116's own grid shows the same signature (its ρ ≥ 20° rows are CAPPED, and its
only witnessed failures are at r = 0.30 with the tilt at ρ ≤ 10°, which this attempt never reached
because it grew tilt first).

The one asymmetry the search did establish is structural: **f1 is the free coordinate and f2 is the
expensive one.** f1 — the square whose contact with the top wall carries Fritz-John multiplier 0.87
(§1b) — takes its whole schedule in tilt and in x at 282–507 s a step, while f2 costs 837 s for one
tilt step and caps on everything after. A116's per-pair forced radii predicted the opposite ranking
(f2 0.215, f1 0.019): the forced radius measures when the minimum's *selection* stops being unique,
not when the neighbourhood stops being dead, and on this evidence it is not a good proxy for the
second.

### Consumer count (A116's test, `code/consumer151.py`; control: it reproduces A116's 72 of 184 on the symmetric N)

| N | k5_11-frame S02 nodes inside | of which ALIVE now |
|---|---|---|
| A116 symmetric (0.2, 10°) | 72 of 184 | 32 |
| A151-A certified (f2 θ ±14°) | 72 | 32 |
| **A151-B certified (f1 grown)** | **96 of 184 (+33 %)** | **42 (+10)** |
| A151 combined (conjecture) | 99 | 43 |

A120's board of **35 targets** is the subset of the symmetric N's 72 that also passes A1–A5; the
asymmetric N raises the pool those targets are drawn from by 24 nodes.

---

## T3. The consequence

`results/t3_consequence.json`.

State of the in-N board (A96 `results/a120_closures.jsonl`, last row per id): **35 targets — 15
CLOSED, 9 OPEN, 11 NOT-RUN.** Of the **32** symmetric-N consumers that are still open in A57's tree,
**21 were never A120 targets at all**, 3 are NOT-RUN, 2 are OPEN and 6 read ALIVE only because
A136's YES/NO closure is a prose+numeric certificate that is deliberately not folded into the tree
(A120 runner.md §2). **So the symmetric N already owes 26 closures before any widening.**

Cost, measured, not modelled: A136 spent **45,102 s on 13 new targets for 9 closures** —
**3,469 s per target attempted, 69 % close rate, 1.39 CPU-h per closure** (its headline 2,932 s
counts only the closed nodes' own wall). The exact-core re-solve on the S02 family is **36.8 % at a
513 s median = 0.39 CPU-h per kill** (T1).

On the **10 new alive consumers** the asymmetric N brings in — none of which has been through the
exact-core re-solve, so both levers are available:

| lever | expected closures/kills | cost | per closure |
|---|---|---|---|
| YES/NO split at A136's price | **6.9 of 10** | **9.6 CPU-h** | 1.39 CPU-h |
| exact-core re-solve | 3.7 of 10 | **1.43 CPU-h** | **0.39 CPU-h** |
| re-solve first, then YES/NO on the ~6 survivors | ~7.7 of 10 | ~7.2 CPU-h | 0.94 CPU-h |

**The exact-core re-solve wins per kill by 3.6×, the YES/NO split wins on coverage, and the two
compose** — run the re-solve first (it is one-shot and cheap), then the split on what survives.
The asymmetric N itself is worth **6.9 closures for 9.6 CPU-h ≈ 0.08 wall-days at 5 workers**, a
38 % enlargement of a backlog that is **already 26 nodes deep at the symmetric N and 25 CPU-h from
being finished**. Widening N is therefore not the binding constraint; pointing the runner at the 21
untargeted in-N nodes is.
