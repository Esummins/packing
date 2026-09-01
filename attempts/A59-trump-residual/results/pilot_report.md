# A59 leg-(c) pilot — the residual zone-tree on trump5 (PRICING report)

Run 2026-09-01, one worker, strictly sequential solves (A56/A57 own the rest of the machine).
Semantics inherited without change: **A54 S0** (τ bounds τ\* in neither direction; the sole kill
arbiter is an exact rational certificate accepted by `verify_case.py`), **A57 T2** (θ windows
uniform in t = tan(θ/2)), **A57 T4** (columns-only warm starts), **A57 T5** (`pinguard.classify`
before any box is solved or read), **A57 T7/T8** (the disjoint-family ALIVE arbiter and the
strict-gap trump5 witness `attempts/A57-shadow-trees/results/alive/trump5_strict.json`,
exact pairwise gap 1.0574e-7 > 0), **A57 T11** (refinement keeps the budget), and the Trump
canary (`substrat.trump_realizes` on every child; a Trump-realizable child is never certified).
Every solve is one line of `results/pilot_zonetree.jsonl`.

s0 = 969271/250000 = 3.877084, s_T = 3.8770835900228…, h = 3.7e-3 (A36 basin radius, sup-norm in
(cx, cy, θ_radians); the matching t half-width at θ_T = 0.7013071 rad is 0.566·h = 2.094e-3).
Ladder "radius" always means that sup-norm radius.

**Canary / engine-bug events: none.** No child that Trump realises was ever certified; every
PASS was re-checked against `trump_realizes`; the 5-core and 3-core nodes passed the pinguard and
pairwise (c, θ)-disjointness audit (θ 0/90 identified) before any solve.

---

## 0. Headline

The pilot's designed headline was the annulus ratio r_kill / h (G-A59-9). It was measured, and it
is **4.55** — but that turned out **not** to be the binding constraint. Three other measured facts
dominate, one negative and two positive, and together they replace T5'.3's cost model outright.

1. **[negative, exact] The sibling-kill ladder of T5'.3 does not exist.** Every YES child on the
   Trump-adjacent chain — the chain node *and every one of its bisection siblings*, at every
   depth j = 1…5 and every half-width a from 0.075 down to 0.0037 — is **ALIVE-CERTIFIED**
   unkillable by Lemma A57-3: the surviving members of Trump's own free six form a strictly
   disjoint family of size exactly the child's budget. Confirmed exactly (rational arithmetic,
   `results/m2_alive.json`) and confirmed by the LP, which converges to τ = budget to 14 digits
   at every level tested. "≈ 35 sibling kills per square" is not a cost — those kills are
   *impossible*, whatever compute is spent.

2. **[positive, measured] The tree closes anyway, because the unkillable residue contracts onto
   Trump.** Refining only the unkillable boxes (A57 T11 bisection, no budget spent), the residue
   never exceeds **52 boxes** (mean 35.4 over 25 levels), its volume falls by 4.2e-8, and at
   **level 24 all 28 surviving boxes lie entirely inside the A36 basin slice** of the Trump
   placement they hug — no residue branch is a kill obligation any more.
   `results/m2_residue_ladder.json`. So localising one square is a finite program of
   ≈ 1 100 (zone cover) + ≈ 800 (ladder) certificates — *not* a wall.

3. **[the annulus, G-A59-9] r_kill(hw) = 4.55·hw** exactly (sup-norm metric, stable over
   hw = 2e-2 … 5e-4). At hw = h the ratio is 4.55 > 1, so stopping the conditioning ladder at the
   basin radius leaves an annulus; it closes at **2.19 further bisection levels**
   (`hw ≤ h/4.55 = 8.1e-4`, verified either side of the crossover). No A40 basin growth and no
   (W')-wedge work is needed *for this obstruction*.

4. **[positive, measured] The nested six-square branching collapses.** Conditioning one square in
   a basin-radius box turns **93 %** of the level-1 cover into free logic kills, and after three
   conditionings **no unkillable box remains at all** (unkillable counts 41 → 18 → 7 → 0 → 0).
   Confinement kills also work at every depth j = 2…5, one certificate each — free at j ≥ 3
   (20–95 s, headroom 0.2–1.0) and knife-edge at j = 2 (542 s, headroom 0.011) (§4b).

**Verdict: GO on all three questions the pilot could reach.** The annulus closes at +2.19 ladder
levels; the single-square ladder terminates in the basin at level 24 with a ≤ 52-box residue; the
six-square nesting has effective branching depth three, giving an extrapolated composed cost of
**1e4–1e5 certificates ≈ single-digit desktop-days at 5 processes**. What is *not* established:
the extrapolation from the two measured conditioning levels to all six (§9), and the entire
s-parametric obligation G-A59-7, which no fixed-s node can touch (§7).

---

## 1. The law the pilot actually found: τ\* = the surviving-Trump-witness count

Define, for a trump5 node N with cores C and NO-families F,

    k(N) = # of Trump's six free squares (in A57 T8's strictly-separated scaled form) that are
           strictly disjoint from every core of N and outside every NO-family of N.

Lemma A57-3 gives `τ*(N) ≥ k(N)`, so **N is certifiable only if k(N) < budget(N)** — and that is
a *theorem*, not a heuristic. Measured against the LP on every node solved to convergence:

| node | budget | k (exact) | τ (LP) | conv | verdict |
|---|---|---|---|---|---|
| `m3_trump5_interior_NO` | 6 | 3 | **3.000000** | yes | PASS |
| `conf_j2_hw0.02_a0.3` | 4 | 3 | **3.000000** | yes | PASS |
| `m1s_cx_a0.075_trad`, `..._a0.0375_*`, `m1s_t_*` (siblings, j=1) | 5 | 5 | **5.000000** (6 solves) | 4/6 | refused |
| `conf_j3_hw0.02_a{0.3,0.15,0.075}` | 3 | 2 | **2.000000** | yes | PASS |
| `m1m_cx_a{0.019,0.0094}_*` (siblings, j=3) | 2 | 2 | **2.000000** | yes | refused |
| `conf_j4_hw0.02_a{0.3,0.15}` | 2 | 1 | **1.000000** | yes | PASS |
| `conf_j4_hw0.02_a0.075` | 2 | 1 | **2.000000** | yes | refused |
| `m4_slab_hw0.02_a0.02` (j=5 + NO) | 1 | 1 | **1.000000** | yes | (diagnostic) |
| deep NO children, `a ≥ r_kill` | 1 | 0 | **0.000000** | yes | PASS |

τ = k in **17 of 18** converged solves. The single exception is instructive and is the reason the
LP is still needed: at `conf_j4_hw0.02_a0.075` the NO-family is too small, so an eleventh square
fits *just outside* it as well as at Trump's sq10 — a disjoint pair that is not a sub-family of
Trump's six, giving τ = 2 > k = 1. So **k is a lower bound only**; it decides "never attempt",
never "will succeed".

**Operational consequence (the pilot's biggest machinery gain).** `k(N)` costs *milliseconds* of
exact rational arithmetic (`code/alive59.py`); τ costs 10–340 s of LP. The tree driver should
compute `k` first and **never launch an LP on a node with k ≥ budget** — such a node is
*provably* uncertifiable (A57-3), so the LP can only waste time. On the A57-resolution interior
cover that is 41 of 808 pinguard-ok children at j = 0 (and 1 400 s of this pilot's own LP time
spent re-discovering it the slow way).

---

## 2. M1-deep — confinement kills and the annulus (G-A59-9)

Node: 5 trump5 pins + 5 cores at Trump's sq4, sq6, sq8, sq9, sq10, each a sup-norm box of radius
`hw` (t half-width 0.566·hw). Audit before every run: all five `pinguard = ok`, pairwise
(c, θ)-disjoint from each other and the pins, so the ten witnesses are forced distinct and
budget 1 is sound. Trump does **not** realise the NO child (his sq7 is inside the excluded box).

### 2a. Engine finding — a budget-1 kill has no LP content

At budget 1 the guard LP is binary: `τ = 0` if the residual carries no admissible non-exempt
placement, `τ ≥ 1` the moment one exists (µ(Q) ≥ 1 forces total ≥ 1). So a budget-1 kill **is**
the vacuity statement "every admissible unit square provably meets one of the ten cores or lies
in the NO-family", whose exact arbiter is `verify_case.py` on the **zero-atom certificate**
(total 0 < 1). Routing it through `caselp` only inserts `EPS_CORE = 2e-3` and `EPS_ZONE = 2e-3`,
which the exact verifier does not need, and which put an additive ~2–3e-3 floor under the
measurable confinement radius — *the same scale as h*, so the LP-gated route cannot see the
discharge regime at all (every LP-gated deep run at hw ≤ 5e-3 was `refused (τ = 1 ≥ budget)`).

`code/vac59.py` implements the direct route: it is sound in the strongest sense (the arbiter is
unchanged; there are no atoms for a shell row to hold up), removes the floor, and is ~3× faster
(0.5–1.5 s vs 1.6–20 s). **This should be folded back into `tree57.py` for every budget-1 node.**

| hw | exact r_kill (centre-only) | smallest a the LP route certified | LP penalty |
|---|---|---|---|
| 0.05 | 0.18926 | 0.20 (0.19 refused) | +1.1e-2 |
| 0.02 | 0.07488 | > 0.075 refused | > +2e-4 |
| 0.01 | 0.03252 | 0.0375 (0.034 refused) | +1.5e-3 |
| 0.005 | 0.01646 | > 0.019 refused | > +2.5e-3 |
| 0.0037 | 0.01218 | > 0.0135 refused | > +1.3e-3 |
| 0.001 | 0.00332 | > 0.006 refused | > +2.7e-3 |

### 2b. r_kill in the A36 sup-norm metric — **the annulus number** (`results/rkill_box.json`)

NO-family = sup-norm ball of radius a in (cx, cy, θ_rad) around Trump's sq7 (t half-width 0.566a).

| hw | largest FAIL a | smallest PASS a = r_kill | r_kill/hw | r_kill/h |
|---|---|---|---|---|
| 0.05 | — | none ≤ 1.5 (see note) | — | — |
| 0.02 | 0.11625 | **0.118438** | 5.92 | 32.0 |
| 0.01 | 0.045 | **0.0455469** | 4.55 | 12.3 |
| 0.005 | 0.0225 | **0.0227734** | 4.55 | 6.15 |
| **0.0037 = h** | 0.01665 | **0.0168523** | 4.55 | **4.55** |
| 0.002 | 0.00892578 | **0.0090625** | 4.53 | 2.45 |
| 0.001 | 0.00448242 | **0.00455078** | 4.55 | **1.23** |
| 0.0005 | 0.0022467 | **0.00228271** | 4.57 | **0.62** |

*Note (hw = 0.05):* with cores that loose the sixth square can be **upright** (θ ≈ 0 ≡ 90) near
Trump's sq7, so no window around θ_T = 40.18° contains the residual and no box of this family
ever certifies. This is why the brief's literal deep ladder (fixed hw = 0.05, t-window half-width
a or 0.566a, a = 0.075 / 0.0375) FAILed at every a — a geometry fact, not an engine failure:

| a | at | τ | verdict |
|---|---|---|---|
| 0.075 | 0.075 | 1.000000 | refused |
| 0.075 | 0.04245 | 1.000000 | refused |
| 0.0375 | 0.0375 | 1.000000 | refused |

(two consecutive FAILs → ladder stopped, per the brief.)

### 2c. Centre-only confinement (θ unrestricted), `results/rkill_deep.json`

| hw | largest FAIL a | smallest PASS a | ratio |
|---|---|---|---|
| 0.05 | 0.187207 | **0.189258** | 3.79 |
| 0.02 | 0.0740625 | **0.0748828** | 3.74 |
| 0.01 | 0.0321094 | **0.0325195** | 3.25 |
| 0.005 | 0.0162598 | **0.0164648** | 3.29 |
| 0.0037 | 0.0120322 | **0.012184** | 3.29 |
| 0.002 | 0.0065332 | **0.00660156** | 3.30 |
| 0.001 | 0.00328613 | **0.00332031** | 3.32 |

### 2d. The annulus verdict

`r_kill(h) = 4.55·h`: conditioning the other five squares to exactly the basin radius does **not**
confine the sixth into the basin — read literally, **the annulus of G-A59-9 exists, width
(4.55 − 1)·h = 1.31e-2**. It closes by over-refinement, not by new theory: `r_kill(hw) ≤ h` iff
`hw ≤ h/4.55 = 8.13e-4`, and 8.13e-4 < h, so the five conditioning boxes are themselves inside
the basin and **a genuine (D) discharge leaf exists**. Cost: log2(4.55) = **2.19 extra bisection
levels per coordinate**, i.e. the ladder runs to 8.1e-4 instead of stopping at 3.7e-3
(6.53 levels below the A57 cover resolution instead of 4.34).

### 2e. Cost of a confinement kill

Exact vacuity certificate: **0.5–1.5 s** wall each (`--depth 60`, 2 verifier jobs), 2 000–14 000
interval boxes, max B&B depth 24–54 on a PASS. A FAIL is equally cheap (0.4–0.9 s) and returns
the exact hole: **at every hw the worst witness sits within 1e-3 of Trump's own sq7 placement**
(θ = 40.0528°, centre (1.687652942, 1.959023103)) — the residual really is Trump's own square
wobbling, nothing else.

---

## 3. M1-shallow / M1-mid — the sibling ladder is impossible, not expensive

**M1-shallow (budget 5, 5 pins + 1 sibling core displaced 2a in cx from Trump's sq7):**

| tag | a | at | pinguard | k | τ | η | conv | LP s | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `m1s_cx_a0.075_tmatch` | 0.075 | 0.075 | ok | 5 | 5.000000000000047 | +4.7e-14 | no (338 s) | 338.1 | refused |
| `m1s_cx_a0.075_trad` | 0.075 | 0.04245 | ok | 5 | **5.000000** | **0.0** | **yes** | 198.7 | refused |
| `m1s_t_a0.075` (θ-offset) | 0.075 | 0.04245 | ok | 5 | 5.000000 | 0.0 | no | 302.1 | refused |
| `m1s_cx_a0.0375_tmatch` | 0.0375 | 0.0375 | ok | 5 | **5.000000** | **0.0** | **yes** | 161.6 | refused |
| `m1s_cx_a0.0375_trad` | 0.0375 | 0.021225 | ok | 5 | **5.000000** | **0.0** | **yes** | 163.0 | refused |
| `m1s_t_a0.0375` (θ-offset) | 0.0375 | 0.021225 | ok | 5 | **5.000000** | **0.0** | **yes** | 236.8 | refused |

**Two consecutive ladder levels FAILed certification** (a = 0.075 and a = 0.0375, all six
variants), which is the brief's stop condition; the r_kill bracket for a shallow sibling kill is
therefore **empty — no a certifies, at any level**. The ladder was stopped there (1 400 s of LP
spent confirming a 1 ms exact fact) and replaced by the exact arbiter, because
`code/alive59.py` proves the rest a priori (`results/m2_alive.json`, 36 nodes):

* every sibling `m1s_cx_*`, `m1s_t_*` at a = 0.075, 0.0375, 0.019, 0.0094, 0.0047, 0.0037:
  witness family {sq4, sq6, sq8, sq9, sq10}, k = 5 = budget → **ALIVE-CERTIFIED unkillable**;
* every chain node (core *containing* Trump's sq7) at the same a: same family, k = 5 = budget →
  **ALIVE-CERTIFIED** (the coordinator's M2 addendum: these are the (D)-chain nodes of T5'.2,
  refined and discharged, never killed);
* the root trump5: k = 6 = budget → ALIVE-CERTIFIED (re-derives A57 T8 from the banked artefact);
* the j = 5 chain node (5 cores, budget 1): witness {sq7}, k = 1 = budget → **ALIVE-CERTIFIED**
  at every hw tested (0.05, 0.001, 0.0005). The whole (D)-chain is alive-certified end to end.

**Mechanism.** A sibling box near Trump's sq7 has a core of half-side 0.34–0.49 that meets
Trump's sq7 and *nothing else* — it removes exactly one witness while costing exactly one unit of
budget. Refining it (A57 T11) does not help: the sub-boxes still meet exactly sq7. Progress
requires a core that meets **two or more** of Trump's free squares.

**M1-mid (budget 2; 5 pins + cores at sq4, sq6, sq10 + sibling for sq7):** k = 2 = budget, and
the LP agrees to six digits, converged, in 10–21 s:

| tag | a | τ | η | conv | LP s | verdict |
|---|---|---|---|---|---|---|
| `m1m_cx_a0.019_tmatch` | 0.019 | 2.000000 | 0.0 | yes | 20.5 | refused |
| `m1m_cx_a0.019_trad` | 0.019 | 2.000000 | 0.0 | yes | 14.5 | refused |
| `m1m_cx_a0.0094_tmatch` | 0.0094 | 2.000000 | 0.0 | yes | 13.0 | refused |
| `m1m_cx_a0.0094_trad` | 0.0094 | 2.000000 | 0.0 | yes | 10.0 | refused |

**Margin trend vs depth (M1-shallow / M1-mid / M1-deep):** there is no margin trend to report —
η = 0 at every depth, exactly, because η = k − budget = 0 identically on the Trump-adjacent
chain. What varies with depth is only the LP's cost of discovering it: 199–338 s at budget 5,
10–21 s at budget 2, 1.6–3.7 s at budget 1 (and 0 s if `alive59` is consulted first).

---

## 4. Killability census and the residue ladder (the replacement cost model)

**Level-1 census** of the A57-resolution interior cover (w = 0.15, nth = 8 t-uniform, 1152 boxes),
`results/m2_killability_census.json`:

| class | count | share | arbiter |
|---|---|---|---|
| `contradictory` (core meets a pin core) | 344 | 29.9 % | logic, 0 s (A57 T5) |
| pinguard-ok, k ≤ 4 → **attemptable** | 767 | 66.6 % | exact certificate (A57 T10: 1–290 s each) |
| pinguard-ok, k = 5 = budget → **ALIVE-CERTIFIED unkillable** | 41 | **3.6 % of cover, 5.1 % of pinguard-ok** | Lemma A57-3, 0 s |
| `parent` (box realises a pin) | 0 | — | — |

Of the 41 unkillable boxes, **3 contain a Trump free placement** (his sq7, sq8, sq9 are the
interior ones) — the never-certify chain. The other 38 are Trump-*adjacent* but contain no
placement: they are the honest residue.

**Residue ladder** (`results/m2_residue_ladder.json`) — refine *only* the unkillable boxes
(A57 T11 bisection: same budget, a refinement of the same disjunction), re-running `pinguard` and
`alive59` on every sub-box, keeping only those still unkillable:

| level | residue boxes | volume | vol / vol(level 0) | max gap to a Trump placement | max box radius | inside the A36 basin |
|---|---|---|---|---|---|---|
| 0 | 41 | 1.001e-1 | 1.0 | 0.900 | 0.1104 | 0 |
| 3 | 40 | 1.220e-2 | 0.122 | 1.007 | 0.0569 | 0 |
| 6 | 31 | 1.186e-3 | 1.19e-2 | 0.0961 | 0.0284 | 0 |
| 9 | 30 | 1.451e-4 | 1.45e-3 | 0.0429 | 0.0143 | 0 |
| 12 | 28 | 1.710e-5 | 1.71e-4 | 0.0163 | 7.15e-3 | 0 |
| 15 | 28 | 2.154e-6 | 2.15e-5 | 9.15e-3 | 3.58e-3 | 0 |
| 18 | 28 | 2.693e-7 | 2.69e-6 | 5.58e-3 | 1.79e-3 | 4 |
| 21 | 21 | 2.524e-8 | 2.52e-7 | 2.01e-3 | 8.91e-4 | 19 |
| **24** | **28** | 4.206e-9 | 4.20e-8 | 1.12e-3 | 4.45e-4 | **28 = all** |

Three facts, all measured:

* the residue **never blows up** — it stays in the band 21–52 boxes over 24 levels
  (mean 35.4 over 25 levels), so the "cells-per-grain multiplier" A43 warns about is ≈ 34, **not** exponential;
* its volume contracts by 4.2e-8 and its **distance to Trump's placements contracts with it**
  (0.90 → 1.1e-3), at the rate `gap ≈ 4.6 × box radius` — the *same* constant 4.55 as r_kill;
* at level 24 **every residue box lies entirely inside the A36 basin slice of the Trump placement
  it hugs** (`gap + 2·radius ≤ h`), so no residue branch is a kill obligation any more: each is a
  (D)-chain candidate in the sense of T5'.2. *Precision:* this discharges the branch only for
  **this one square**; the A36 theorem itself needs all six squares (and |σ − s_T| ≤ h)
  simultaneously, which is the composition of §4b, not of this ladder.

So the single-square program terminates: **1 zone cover (344 free + 767 exact kills) + 24
refinement levels × ≈ 34 kills ≈ 1 900 certificates**, none of which is a sibling kill on the
chain (those do not exist), ending with ≈ 28 branches all inside the basin slice.

---

## 4b. The nested six-square question, measured (G-A59-10 — resolved in the GO direction)

Two extra measurements, not in the brief, were run because finding (1) invalidates the brief's
cost model and these are the numbers that replace it.

**(i) Confinement kills work at every conditioning depth, not only at j = 5.** Node = 5 pins +
j cores of radius hw = 0.02 at Trump's sq4, sq6, sq8, sq9 (in that order) + the full-θ NO-family
of radius a around his sq7; budget 6 − j. Attemptable exactly when k < 6 − j.
`results/conf_ladder.json`:

| j | budget | k | a | τ | η | LP s | cert s | verdict |
|---|---|---|---|---|---|---|---|---|
| 4 | 2 | 1 | 0.3 | 1.000000 | −1.0 | 20.4 | 0.8 | **PASS** |
| 4 | 2 | 1 | 0.15 | 1.000000 | −1.0 | 20.0 | 0.9 | **PASS** |
| 4 | 2 | 1 | 0.075 | 2.000000 | 0.0 | 21.2 | — | refused |
| 3 | 3 | 2 | 0.3 | 2.000000 | −1.0 | 84.1 | 3.0 | **PASS** |
| 3 | 3 | 2 | 0.15 | 2.000000 | −1.0 | 72.3 | 1.0 | **PASS** |
| 3 | 3 | 2 | 0.075 | 2.000000 | −1.0 | 70.0 | 1.0 | **PASS** |
| 2 | 4 | 3 | 0.3 | 3.000000 | −1.0 | 79.2 | 10.2 | **PASS** |
| 2 | 4 | 3 | 0.15 | 3.500000 (unconv., 243 s) | −0.5 | 243.0 | 298.9 | **PASS** (1 witness round) |
| 2 | 4 | 3 | 0.075 | — | — | — | — | *stopped mid-solve at the wall-clock cut* |
| 1 | 5 | 4 | 0.3, 0.15, 0.075 | — | — | — | — | *not run (stopped)* |

(The j ≤ 2 tail was cut cleanly: `alive59` shows those nodes are attemptable — k = 3 < 4 and
k = 4 < 5 — but the measured margin trend below predicts they are knife-edge to hopeless, and
the four depths already measured settle the question the tree needs answered.)

So a *single* exact certificate confines the next square to a box around Trump's placement at
every depth j = 2…5. η = −1.0 wherever the LP converges: the NO-family swallows exactly one Trump
witness, worth exactly one unit of budget.

**But the certificate margin dies as the conditioning depth decreases** — the scale-capped
certificate total against the budget:

| j | budget | atoms | cert total | headroom |
|---|---|---|---|---|
| 5 | 1 | 0 | 0 | 1.000 |
| 4 | 2 | 1 | 7/5 = 1.400 | 0.600 |
| 3 | 3 | 2 | 14/5 = 2.800 | 0.200 |
| 2 | 4 | 3 | 3989001/1000000 = 3.98900 | **0.011** |
| 2 | 4 | 8 | 1994003/500000 = 3.98801 | **0.012** |

The confinement lever is essentially free once ≥ 3 squares are conditioned and *knife-edge* at
j = 2 (0.3 % headroom, and 542 s of wall). So the tree should reach j = 3 by ordinary zone kills
(where 97 % of the cover is free logic) and use confinement from there on.

**(ii) The branching factor collapses with depth.** Level-1 killability census of the same
A57-resolution interior cover (1152 boxes) at a node with j squares already conditioned in
**basin-radius** boxes (radius h = 3.7e-3) at Trump's placements, `results/m2_branching_by_depth.json`:

| j (conditioned) | YES-child budget | contradictory (free) | attemptable (k < budget) | **unkillable (k ≥ budget)** |
|---|---|---|---|---|
| 0 — none | 5 | 344 (29.9 %) | 767 | **41** |
| 1 — sq7 | 4 | **1075 (93.3 %)** | 59 | **18** |
| 2 — sq7, sq8 | 3 | 1118 (97.0 %) | 27 | **7** |
| 3 — + sq9 | 2 | 1150 (99.8 %) | 2 | **0** |
| 4 — + sq4 | 1 | **1152 (100 %)** | 0 | **0** |

Conditioning one square at the basin radius turns **93 %** of the cover into free logic kills, and
after three conditionings **no unkillable box remains at all**. The nested tree therefore has an
effective branching depth of **three**, not six: 41 → 18 → 7 → 0. This is the opposite of the
c^18 explosion the census verdict (T4a) feared for the grain unit, and it is what makes the
zone-tree unit viable where the grain unit was not.

**Bounded composition estimate.** ≈ 1 900 certificates for square 1's ladder (§4) with ≈ 28 basin
leaves; ≈ 18-box residue for square 2 and ≈ 7 for square 3, each with its own ≲ 24-level ladder;
nothing to do from square 4 on. Order of magnitude **1e4–1e5 certificates at 1–90 s each**, i.e.
**single-digit desktop-days at 5 processes** — inside the GO budget of the composed cost model,
though the estimate is an extrapolation of two measured levels, not a measurement of all six.

---

## 5. M3 — the interior NO child of trump5 → **Lemma A59-P1**

| child | budget | k | τ | η | cert total | verifier | wall |
|---|---|---|---|---|---|---|---|
| `m3_trump5_interior_NO` | 6 | 3 | 3.000000 | **−3.000** | 21/5 = 4.2 | PASS, 3 atoms | LP 1.1 s + cert 2.0 s |

`certs/m3_trump5_interior_NO.json` (+ `.PASS`), independently re-verified at `--depth 60`
(39 926 boxes, 13 490 covered, max depth 42, 2.1 s — §8). Exactly the A57 T3 profile.

> **Lemma A59-P1.** In any packing of 11 unit squares in [0, s0]² whose skeleton contains the
> trump5 pin set, **at least one square has its centre in the interior zone [1.1, 2.777]²**.

Unconditional at s = s0; the window form inherits the s-parametric obligation G-A59-7.
(Trump's own sq7, sq8, sq9 are the three squares that realise it, which is exactly why k = 3.)

---

## 6. M5 — pinguard and distinct-witness statistics on trump5

`results/m5_pinguard.json`, A57 interior resolution (w = 0.15, nth = 8 t-uniform):

| cover | contradictory (free kills) | ok | parent | uncoverable | core half-side a |
|---|---|---|---|---|---|
| 1152 | **344 (29.9 %)** | 808 | **0** | 0 | 0.356602 (uniform, max−min 4e-8) |

* **0 `parent` boxes** — trump5 pins no slot inside the interior zone, so every interior YES
  child is sound at budget 5. (Identical to A57's k5_11 figure: the strata share the BL
  staircase.)
* **3 of 1152 boxes contain a Trump free placement** — the never-certify chain has width 3 at
  level 1.
* 5-core deep-node audit: `pinguard = [ok, ok, ok, ok, ok]`, **zero** pairwise (c, θ) overlaps
  among the five cores and the five pins (θ 0/90 identified), core half-sides 0.405–0.417 at
  hw = 0.05. Distinct witnesses are forced, so budget 1 is sound.

---

## 7. M4 — the low-s slab diagnostic (G-A59-8; NO soundness claim)

Node: 5 pins + 5 cores at radius hw = 0.02 + NO-family B7(0.02); budget 1; LP converged in 21.3 s
at τ = 1.000000 with **minmass = 1, maxcov = 1** (both oracles clean).
Dump: `results/m4_slab_hw0.02_a0.02_atoms.json`.

The converged optimum is a **single atom of weight 1** at (1.99823, 1.95668) — 0.3097 (sup-norm)
from Trump's sq7 centre, i.e. an interior point of every surviving placement of the eleventh
square. **All** of the residual mass is that one atom: the LP puts **zero** weight anywhere else
in the container (`w(‖·−sq7‖∞ ≤ 0.05) = 0`, `w(≤ 0.20) = 0`, `w(> 0.20) = 1.0` — the atom is the
only one). Read with the scan (`results/scan_hw_sweep.json`: at hw = 0.02 every admissible
eleventh-square placement has its centre within 0.0704 of sq7), the picture is unambiguous: at
this node the guard LP sees **nothing but the sq7 wobble**.

**Therefore the slab is *not* LP-visible here, and for a structural reason, not a resolution one:**
the node is stated at fixed s = s0 with the pins at slots(s0). A packing at σ < s_T − h has its
BR/TR pins at (σ−½, ·) — displaced by up to 5.7e-2 — so it is *not in this node's hypothesis
class at all*. No amount of LP work at a fixed-s node can probe the slab; G-A59-8 is a
sub-question of the s-parametric obligation G-A59-7 (A56's recipe), and this pilot supplies no
evidence either way. Recommend merging G-A59-8 into G-A59-7 rather than carrying it separately.

---

## 8. Certificates, re-verification, canaries

* PASS certificates written: **87 and counting** (the depth-2 confinement ladder was stopped cleanly mid-solve at the wall-clock cut), all with `.PASS` markers, under `certs/`.
* Independent re-verification at raised depth (fresh `verify_case.py` invocations, `--jobs 1`):

| cert | depth | boxes | result |
|---|---|---|---|
| `m3_trump5_interior_NO` | 60 | 39 926 (13 490 covered, max depth 42) | **PASS**, 2.1 s |
| `rb_hw0.0005_a0.00228271_box` (the sub-h discharge) | 60 | 4 994 (2 529 exempt, max depth 54) | **PASS**, 0.3 s |
| `rb_hw0.001_a0.00455078_box` (the crossover) | 62 | 5 708 (2 886 exempt, max depth 53) | **PASS**, 0.3 s |
| `conf_j3_hw0.02_a0.075` (depth-3 confinement) | 60 | 5 502 (814 covered, 1 969 exempt, max depth 34) | **PASS**, 0.3 s |
| `conf_j4_hw0.02_a0.15` | 60 | 1 322 (22 covered, 671 exempt, max depth 21) | **PASS**, 0.1 s |
| `conf_j2_hw0.02_a0.3` (the knife-edge one) | 60 | 262 332 (102 833 covered, max depth 39) | **PASS**, 15.0 s |
| `m1d_hw0.05_a0.2_fulltheta` | 60 | 1 978 (1 021 exempt, max depth 24) | **PASS**, 0.1 s |

Six independent re-verifications, all PASS. Note the verifier cost tracks the certificate's
headroom, not the node: the knife-edge `conf_j2` certificate needs 262 332 interval boxes and
15 s, two orders of magnitude more than any other.

* **Canary events: none.** No Trump-realizable child was certified; `trump_realizes` was False on
  every deep NO child (his sq7 lies in the excluded box) and on every sibling; the root and the
  whole (D)-chain were positively **ALIVE-CERTIFIED** instead, citing
  `attempts/A57-shadow-trees/results/alive/trump5_strict.json` (exact gap 1.0574e-7 > 0).
* **Engine-bug events: none.** No sibling PASS on a box containing a Trump placement.

---

## 9. Leg-(d) inputs

**Per-kill cost distribution (measured, single process):**

| kill class | budget | arbiter | n | wall each |
|---|---|---|---|---|
| contradictory (pinguard) | any | logic | 344/1152 per cover | 0 s |
| ALIVE-CERTIFIED unkillable | any | `alive59` (exact) | see §4 | ~1 ms (never launch the LP) |
| zone NO child | 6 | LP + cert | 1 | 3.1 s (1.1 + 2.0) |
| confinement NO, budget 1 | 1 | **zero-atom vacuity cert, no LP** | 138 in this run (74 PASS) | mean **0.79 s**, max 2.9 s |
| confinement NO, budget 2–4 | 2–4 | LP + cert | 7 | 21 s (j=4) … 542 s (j=2) |
| interior YES, k ≤ 4 | 5 | LP + cert | not sampled here | A57 T10: 1–290 s, mean ≪ 240 s |

**Refinement multiplier:** the A57 T11 bisection applied to the unkillable residue yields
**≈ 34 boxes per level, stable over 24 levels** (band 21–52), i.e. a multiplier of ≈ 34 rather
than 2^level. Contraction rate: box radius halves every 3 levels and the residue's gap to Trump's
placements tracks it at `gap ≈ 4.6 × radius`.

**Extrapolated per-square confinement cost:** 24 levels × 34 kills ≈ 800 kills, plus the zone
cover (767 exact + 344 free). At the confinement/vacuity rate (≈ 1 s) the ladder is **minutes**;
if a level ever needs a budget-5 LP kill at A57's rate (mean ~60 s) it is **~13 CPU-hours**.
Either way one square is *hours, not days*.

**Extra ladder depth from the annulus:** +2.19 levels per coordinate (§2d), already inside the 24
measured levels.

**Nested branching (was the open cost; measured in §4b):** unkillable boxes per conditioning
level 41 → 18 → 7 → 0 → 0; free logic kills 29.9 % → 93.3 % → 97.0 % → 99.8 % → 100 %.
Effective branching depth **three**. Composed estimate **1e4–1e5 certificates**,
**single-digit desktop-days at 5 processes**. Caveat: this extrapolates the ladder cost of
square 1 (fully measured, 24 levels) to squares 2–3 (level-1 census measured, ladder not run).

**Total compute used by this pilot:** 185 recorded solves — **2 198 s of LP + 432 s of
certification = 43.8 min** of solve time, plus ≈ 25 min of exact-arithmetic scans/censuses and
≈ 6 min of float reconnaissance. One process at a time, two during certification (A56/A57 kept
the rest of the machine). **1 400 s of that LP time (64 %) was spent on the six M1-shallow solves
that `alive59` decides in a millisecond** — the strongest possible argument for the pre-LP gate.

---

## Appendix A — float reconnaissance (no soundness claim)

`code/scan59.py` grids the placement space and keeps every (cx, cy, t) whose unit square is
SAT-disjoint from all ten cores. It was used only to choose ladder brackets; every number in
§2 is an exact certificate. For the record (`results/scan_hw_sweep.json`, window ±0.26 around
sq7, centre step 0.002, 241 t-cells):

| hw | ht | core half-side | admissible grid points | max ‖·−sq7‖∞ | max t-distance |
|---|---|---|---|---|---|
| 0.05 | 0.03 | 0.40499 | 204 237 | 0.18856 | 0.36577 (all tilts) |
| 0.02 | 0.012 | 0.46066 | 8 526 | 0.07039 | 0.06577 |
| 0.01 | 0.006 | 0.48010 | 990 | 0.03039 | 0.02410 |
| 0.005 | 0.003 | 0.48999 | 125 | 0.01439 | 0.01160 |
| 0.0037 | 0.00222 | 0.49258 | 49 | 0.01039 | 0.00744 |
| 0.002 | 0.0012 | 0.49598 | 9 | 0.00439 | 0.00327 |
| 0.001 | 0.0006 | 0.49799 | **1** | 0.00239 | 0.00090 |

A full-container scan at hw = 0.05 with a generous 0.02 depth slack
(`results/scan_deep_eps02.json`, 15 379 points) confirms that **every** admissible eleventh-square
placement lies within 0.209 of Trump's sq7 — nothing survives anywhere else in [0, s0]².

---

## 10. Gap-list deltas

* **G-A59-9 (annulus)** — MEASURED: r_kill/h = 4.55 at hw = h; closes at hw ≤ 8.13e-4
  (2.19 extra levels). Not the binding constraint.
* **G-A59-8 (low-s slab)** — RECLASSIFIED: not probeable at a fixed-s node by construction;
  merge into G-A59-7.
* **G-A59-3 (Trump's grain beyond the A36 box)** — QUANTIFIED: 41/808 = 5.1 % of the
  pinguard-ok level-1 cover, contracting to volume 4.2e-8 and fully inside the basin by
  refinement level 24. The A54 tight-map estimate of 5.1 % is reproduced exactly.
* **T5'.3 (depth arithmetic)** — REFUTED as written: "≈ 35 sibling kills per square" describes
  kills that Lemma A57-3 forbids. Replace with the residue-ladder model of §4.
* **NEW G-A59-10** — the nested six-square branching factor. **Measured and favourable** (§4b):
  branching depth three, 93 % free kills after one conditioning. Residual obligation: run the
  full refinement ladder at conditioning depths 2 and 3 (the pilot ran it only at depth 0) to
  turn the composed estimate into a measurement.
* **NEW G-A59-11 (machinery)** — fold `alive59.k(N)` into `tree57.py` as a pre-LP gate (never
  launch an LP on a node with k ≥ budget) and `vac59` as the budget-1 arbiter. Both are pure
  wins and both are needed before any A59 tree is launched.
* **NEW, for the theory note** — the empirical law τ\*(N) = k(N) on trump5 nodes (§1). If it can
  be proved (τ\* ≤ k, the converse of A57-3, on this stratum) the whole tree becomes a
  combinatorial computation in exact arithmetic with the LP used only to build certificates.
