# A57 — the shadow trees: rung-3 sub-stratification of k5_11 and k5_16

Everything at s0 = 969271/250000 = 3.877084, A53 Young-form stratification, A54 semantics.
A29, A53, A54, A55, A56 artefacts are read, never written.  trump5 is never a target and is
never certified.

## T0 — semantics inherited (A54 S0), restated because A57 lives or dies by it

Node = pins (degenerate core boxes) + core boxes + NO-families; budget = 11 − (#pins + #cores).
τ = value of the guard LP restricted to the rows AND columns generated so far. **τ bounds the
true residual guard value τ* in NEITHER direction**: dropping rows lowers it, restricting the
column set raises it.  τ < budget is not a kill; τ ≥ budget is not a survival.  The sole
arbiter of a kill is an exact rational measure certificate accepted by `verify_case.py`.
A57 records every non-kill as *alive-at-LP* or *cert-FAIL*, never as "alive".

## T1 — the branch and why it is exhaustive

For a zone Z (rectangle of centres) and a closed cover {B_i} of Z × [0,90]:

    (NO)   no square of the packing has its centre in Z
    (YES_i) some square has (centre, θ) ∈ B_i

is a complete disjunction, so the parent stratum is empty as soon as every child carries an
exact certificate.  Vacuous boxes (no admissible placement) may be dropped; a box with an
empty rational core may not (`tree57.cover` bisects until every kept box has one, and the
driver aborts if any survives).  Children: 1 NO (budget 11−k) + |cover| YES (budget 11−k−1).

## T2 [M] — the θ-cover must be uniform in t = tan(θ/2), not in degrees

caselp's core half-side for a box of centre-width w and θ-window [θ0,θ1] is
`a = (1/2 − hd)/(1 + (t1 − t0))` with `hd ≥ ½·diag(centre box) = w/√2`, i.e. it is controlled
by the **t-width**, not the degree-width.  A54's degree-uniform cover (nx=ny=2, nth=3) gave
a = 0.022–0.043 in the side/interior zones, far below A24 (iii)'s a ≥ 0.35 kill threshold, and
A54 estimated ≈ 6000 interior children to reach it.  Splitting [0,1] ∋ t into `nth` equal
pieces makes a uniform over the whole cover:

| zone | w | nth (t-uniform) | children | a |
|---|---|---|---|---|
| interior [1.1, 2.777]² | 0.15 | 8 | 1 + 1152 | 0.35660 (uniform, max−min = 4e-8) |

`code/tree57.py --plan_only` reproduces this; 0 boxes are uncoverable, 0 children are
Trump-realizable (correct: neither stratum is, A54 S4).

## T3 [M] — KILL: the interior NO-child of both shadow strata

| child | budget | τ | η | cert total | verifier | wall |
|---|---|---|---|---|---|---|
| `k5_11_interior_NO` | 6 | 3.000000 | **−3.000** | 21/5 = 4.2 | PASS, 8568 boxes, max depth 33 | LP 15 s + cert 1.2 s |
| `k5_16_interior_NO` | 6 | 3.000000 | **−3.000** | 21/5 = 4.2 | PASS, 6986 boxes, max depth 27 | LP 4.5 s + cert 1.0 s |

Certificates: `certs/tree/k5_11_interior_L1/k5_11_interior_NO.json` (+ `.PASS`) and the k5_16
analogue.  Both used 3 atoms at scale 1.40.  Consequence, unconditionally:

> **Lemma A57-1.** In any packing of 11 unit squares in [0, s0]² whose skeleton contains the
> k5_11 pin set (resp. the k5_16 pin set), **at least one square has its centre in the interior
> zone [1.1, 2.777]²**.

The η = −3.000 slack is enormous: the interior zone is over-large for the branch, and T5
exploits that.

## T4 [M] — what a child solve costs (operational)

Parent τ: k5_11 = 5.9061, k5_16 = 5.9731, both at budget 6 (η = −0.09 / −0.03).  Warm-start
choice, measured on one interior child of k5_16 (box [1.1,1.24]² × [82.4°,90°], a = 0.3566 —
T5 later shows this box is *contradictory*, so read the table as timings, not verdicts), 120 s LP:

| warm start | init cols / rows | τ @ limit | η | minmass |
|---|---|---|---|---|
| parent positive-weight atoms (496), rows generated | 1110 / 504 | 5.2500 | +0.250 | 0.55 |
| merged column pool (3486), rows generated | 3486 / 504 | 5.1429 | +0.143 | 0.00 |
| cold | 625 / 500 | 5.3333 | +0.333 | 0.00 |

Warm-starting with the parent's
30 k rows costs 44 s per iteration and gains nothing; with `rows=[]` an iteration is 13–18 s
and the row oracle rebuilds the child's own row set, which differs from the parent's anyway
because the new core deletes rows.  A57 uses **columns-only warm starts** for children —
A55/k3_ext E3's "atoms are the progress variable", now also the cheap option.)

## SAMPLED CHECKS: REPORT THE SURVIVOR COUNT, NOT THE DRAW COUNT (A96, 2026-09-06; lab-wide)

Any sampled check with an acceptance filter must report **how many samples survived the filter
and were actually tested**, never how many were drawn. A draw that is rejected before the
predicate is evaluated is not evidence.

How this was found. A96 checked A119's certified neighbourhoods by drawing configurations from
the exported boxes and looking for one that is pairwise-disjoint at a side ≤ s0. The first run
reported **20 000 samples, 0 hits** — and was worthless: the containment filter rejected 99.97 %
of draws, so roughly **30** configurations were ever tested. The number was true and meaningless.
(The filter itself was wrong too: a pin's slack box can push a pinned square a hair outside
`[0,s]²`, and a pinned square is inside the container by assumption, so the slack must be
intersected with containment rather than used to reject the draw.)

Corrected, the same check tested 13 289 configurations across five neighbourhoods with zero hits,
and the neighbourhood actually deployed against was re-run alone to clear the bar on its own:
`S02_k5_11_r0.20_rho10`, **73 642 drawn → 10 500 tested → 0 hits**.

Rules:
* quote `drawn → tested → hits`, all three;
* a per-N (per-case) bar must be met by the case you rely on, not only in aggregate — an
  aggregate that clears 10⁴ can hide a case with 55;
* if the acceptance rate is low, say so: it is a fact about the sampler, and usually a sign the
  filter is mis-modelling the hypothesis;
* this applies retrospectively to any "10⁴-sample confirmed" claim quoted as a draw count.

## EMISSION IS NONDETERMINISTIC; VERIFICATION IS NOT (A112, recorded by A96 2026-09-06)

`certify.py --loop_cols` re-solves the node LP under a **time limit** before emitting, so which
columns are in the LP when the clock runs out depends on wall time, machine load and the number
of concurrent workers. **A certificate's atom set is therefore wall-clock dependent**: emitting
the same node twice can produce two different (both valid) certificates, and an emission that
succeeded once may fail on a loaded box, or vice versa.

The frozen verifiers are the opposite: `verify_case.py` / `verify_param.py` are exact and
deterministic — the same certificate file always yields the same verdict.

**Consequence: reproduce kills by replaying certificates, never by re-emitting.** A kill is
reproduced by running the frozen verifier over the stored certificate. Re-running the emitter is
not a reproduction, and a re-emission that fails is not evidence that the recorded kill was
wrong. Anything comparing two campaigns must compare certificate files, not emitter outcomes —
and any benchmark that varies concurrency (as A96's contention legs did) changes emission
outcomes as a side effect, which is a confound to control for, not a signal.

## T5′ [M] — the TIGHT common-inscribed core (A96, 2026-09-05, deployed)

**The kill certificate is unchanged.** T5 below is the rule, and its Lean form
(`core_meet_same_square`, node C.T5T11) is untouched: if the box's core K_B meets a pin's core
K_P then every square with (centre, tilt) in B overlaps that pinned square and is not it, so the
node is empty by logic. What changed is only **the half-side of the core the rule is applied
to**. No new leaf kind, no new Lean obligation, nothing in the frozen verifier chain.

`caselp.Box.core()` uses

    a_old = (1/2 − hd) / (1 + (t1 − t0)),      hd = centre-box half-DIAGONAL

which is sound but loose twice over. K ⊆ Q(c, θ) for every (c, θ) ∈ B iff every corner of K lies
in Q, i.e. |R(−θ)d + a·R(φ)s|∞ ≤ 1/2 for d = k − c, φ = θ_m − θ and the four sign vectors s.
Bounding the two terms separately gives the tight value

    a_tight = (1/2 − h·M_c) / M_t
        h   = centre-box half-WIDTH
        M_c = max(|cos θ| + |sin θ|) over the box's tilt range
        M_t = max(|cos φ| + |sin φ|) over the tilt range about θ_m

a_old is this bound with hd = h·√2 — i.e. assuming 45° always lies in the tilt range — and with
1 + (t1 − t0) ≥ M_t, since cos x + sin x ≤ 1 + x. On the deployed cover a_tight/a_old runs
1.007–1.109 (median 1.042) and is **never** below 1.

**Why no kill can be lost.** The core's centre (kx, ky) and tilt θ_m are unchanged and only `a`
grows, so the new core *contains* the old one: any box the old rule killed, the new rule kills.
**Control executed, not merely argued: 583/583** known logic-kill boxes still killed, none lost
(`attempts/A96-a57-parametric/results/core96.json`).

**Where it is wired in.** `pinguard.kill_core()`, used by `pinguard.classify()` **only** — the
KILL-BY-LOGIC decision. It is deliberately *not* wired into `Box.core()`, because that core is
the LP's hypothesis and appears in every emitted certificate; changing it would change the
certificate corpus. `TIGHT_CORE = False` restores the old behaviour exactly. The value is shrunk
by `TIGHT_EPS = 1e-9` before use so float slop cannot manufacture a kill; a fully rational
version would round M_c and M_t up and the numerator down.

**Yield on the open set** (1536 open boxes at deployment): 70 new certified kills — L1 20/1096
(1.8%), L2 32/389 (8.2%), L3 7/39 (17.9%), L4 11/12 (91.7%). The rate rises steeply with depth,
the same mechanism that terminates the tree (logic kills 32% at L2 → 60% at L4): deeper boxes are
smaller and clash with the pins. Worth ≈31.4 CPU-days, ~72% of it at level 4.

**Deployment is a pre-filter on newly emitted children only.** Existing verdicts are not
recomputed or overwritten; the 70 boxes whose recorded FAIL/ALIVE verdicts this rule supersedes
are listed in `results/superseded_by_tight_core.jsonl` (and A96's copy), with their prior verdict
retained.

## T5 [M] — SOUNDNESS FIX: a YES box may not be witnessed by a pin (`code/pinguard.py`)

A YES child adds a core box B and drops the budget from 11−k to 11−k−1.  That is sound only if
the square witnessing B is **distinct** from all k pinned squares — the node semantics
"budget = n − #cores" assumes the cores are realised by distinct squares, and nothing in A54's
`substrat.py` checks it.  A57 classifies every box before it is ever solved:

* **parent** — a pin's placement (px, py, 0°) lies in B (θ = 90 is the *same* square as θ = 0,
  so a box touching 90 realises an upright pin).  B can then be witnessed by the pin itself,
  only k squares are accounted for, and **certifying at budget 11−k−1 would certify a false
  statement.**  A57 records `UNSOUND-AT-REDUCED-BUDGET` and never certifies such a child.
* **contradictory** — B's rational core meets a pin's core and no pin placement lies in B.  The
  core is contained in *every* square with (centre, θ) ∈ B, so every such square overlaps that
  pinned square and is not it: the child is **EMPTY by logic**, a kill needing no LP and no
  certificate.
* **ok** — the ordinary case.

A54's single rung-3 probe (k6_23 / side zone, boxes from x = 1.1 outward) happened to avoid both
degenerate cases, which is why the gap never fired there.  It fires at once on any zone that
contains or abuts a pin.  Interior census at the A57 cover resolution:

| stratum | cover | contradictory (free kills) | ok | parent |
|---|---|---|---|---|
| k5_11 | 1152 | **344 (29.9 %)** | 808 | 0 |
| k5_16 | 1152 | **257 (22.3 %)** | 895 | 0 |

No `parent` boxes in the interior (neither stratum pins a slot inside [1.1, 2.777]²), so the
interior measurements below are sound; the free kills are pure profit.

## T6 [M] — the a-curve, done twice, and why the first reading was wrong

**Retracted first reading.**  The natural "easiest-first" head of the interior cover sits at the
zone's inner corner, (1.17, 1.17) — and that box is **contradictory** (its core meets the core of
the pin at (0.5, 1.5) / (1.5, 0.5)).  Driven to convergence there, the child LP gives
τ = 5.000000 = budget exactly at every a from 0.350 to 0.489, which looks like a structural
no-go; it is nothing of the kind, because the node is already empty by logic and the guard LP
simply cannot see a hypothesis contradiction.  Re-run at the most central **pinguard-ok** box,
(2.0084, 2.0084, ~86°):

| location | pinguard | a = 0.3564 | a = 0.4468 | a = 0.4890 |
|---|---|---|---|---|
| (1.17, 1.17) inner corner | contradictory | τ = 5.25 (unconv.) | τ = 5.000000 | τ = 5.000000 |
| **(2.0084, 2.0084) centre** | **ok** | **τ = 3.000000, η = −2.0, 15 s** | **τ = 3.000000, η = −2.0, 1.3 s** | **τ = 3.000000, η = −2.0, 1.2 s** |

All four central runs converged (minmass = 1, maxcov = 1) with **3 atoms**, scale ceiling
5/3 = 1.667.  A central core of half-side a ≥ 0.356 leaves a residual that three point masses
pierce entirely: the YES side of the interior branch is not merely killable, it is *cheap*, and
already at the cover resolution — no refinement needed.  Contrast A54 W5's η = +0.500 at
a = 0.0385: the t-uniform cover (T2), not more compute, is what moved this.

## T6b [M] — the superseded reading (kept because it is the trap)



Recorded because it very nearly became A57's headline.  Driving the *inner-corner* child —
k5_16, core centred at (1.17, 1.17, 86°) — down the whole a range with the LP left to converge
(`code/probe2.py`, `results/acurve_k5_16_a*.json`) gives:

| centre width w | t-window | **a** | τ | η = τ − 5 | converged | minmass | maxcov |
|---|---|---|---|---|---|---|---|
| 0.150 | 0.125 | 0.35016 | 5.25 (900 s limit) | +0.25 | no | 0.71 | 1.31 |
| 0.050 | 0.040 | 0.44677 | **5.000000** | **0.0** | **yes** | 1.000000 | 1.000000 |
| 0.010 | 0.008 | 0.48902 | **5.000000** | **−4.7e-14** | **yes** | 1.000000 | 1.000000 |

At a = 0.489 the core is within 0.011 of a *fully pinned* square, and both oracles are clean
(minmass = 1: no violated row; maxcov = 1: no wanted column), so τ = 5.000000 is τ* to oracle
precision, not a time-out artefact.  **τ*(child) = budget exactly.**  `certify.py` refuses at
`total ≥ budget` (rc = 3) before the verifier ever runs, so:

read naively, "refining the YES cover does not help; the child LP converges to exactly the child
budget, so no resolution, scale headroom or column generation can ever certify it."  The
arithmetic even looks like a mechanism: the parent sits at τ_p = 5.973078 (budget 6,
η_p = −0.026922) and the child comes in at τ_c = τ_p − 0.973078 = 5.000000 — one core buying
back 0.973 of guard while costing a whole unit of budget, 0.027 short, exactly the parent's own
margin.  **All of it is an artefact of a contradictory node** (T5): that box's core meets a pin
core, the node is empty for free, and the guard LP — which never checks hypothesis consistency —
is merely reporting the value of a residual it has no business covering.  The lesson is the
discipline: **run `pinguard.classify` before reading any τ off a YES child**, and pick probe
locations by soundness class, not by the easiest-first ordering (which piles the degenerate
boxes at the head, since the zone's inner corner is farthest from Trump's ghost).

## T7 [M] — an ALIVE-side arbiter (new machinery): the disjoint-family bound

The lab had no way to say "this node can never be killed" except by hand for trump5
(A53 V6 / A54 S4).  `code/alivewitness.py` generalises it.

> **Lemma A57-3 (disjoint-family bound).**  Let N be a node with cores C_1..C_r and budget
> m = 11 − r.  If there are closed unit squares Q_1..Q_m in [0,s0]² that are admissible,
> pairwise disjoint with a strictly positive gap, and strictly disjoint from every C_j, then
> every feasible μ has μ(Q_i) ≥ 1 (each Q_i is a non-exempt row: `verify_case.py` exempts a
> placement only if it provably meets a core) and the Q_i are disjoint, so
> μ(total) ≥ Σ μ(Q_i) ≥ m.  Hence **τ* ≥ budget and no certificate for N can ever exist.**

Strictness is required because μ is atomic: two squares that merely touch could share an atom,
which is why A57's witnesses carry an exact positive gap rather than A53 V6's exact-touch −1e-15.
The search is float (grid + DFS over a candidate pool, tilts allowed); the *verdict* is exact
rational arithmetic throughout (`Fraction`, cos/sin from a rational t = tan(θ/2)).

Measured: `results/alive/quarantine/k5_16_m5.json` (**QUARANTINED — see T28**) — five
pairwise-disjoint admissible squares in the k5_16 residual, exact min gap 0.0017314…> 0, so
τ*(k5_16) ≥ 5 (a lower bound; k5_16's budget is 6, so this is **not** an unkillability proof for
the stratum itself).  *The prose here was right; the JSON artefact's own `claim` string was not,
and asserted LP-unkillability — A78 caught it.  The file is quarantined and must not be cited.*  With the interior core
added as a sixth obstacle no 5-family is found, consistent with T5's τ* = 5 knife edge: the
interior YES children are *critical*, not comfortably alive.

## T8 [M] — CANARY REPAIR: trump5's aliveness is now strict, not exact-touch

A53 V6 / A54 S4 (i) argue τ*(trump5) ≥ 6 from Trump's six free squares being "pairwise disjoint
(min SAT gap −1.0e-15 = exact touch)".  Under A57-3 that argument is **one ε short of rigorous**:
the guard measures this lab builds are atomic, and two squares that only touch can share an atom,
in which case Σ μ(Q_i) ≤ μ(total) fails.  The repair uses the slack the embedding already has —
s0 − s_T = 4.1e-7.  Scaling Trump's centres about the container centre by λ = s0/s_T
(λ − 1 = 1.0574e-7) keeps every square admissible at s0 and opens every contact:

    code/alivewitness.py --name trump5 --placements <scaled free six> --den 1e12
    → ALIVE-CERTIFIED, exact min gap
      144937745660574462730629449381/1370664603569846904878201000000000000 = 1.0574e-7 > 0
    → results/alive/trump5_strict.json

So **τ*(trump5) ≥ 6 = budget holds with a strictly positive exact gap**: trump5 is LP-unkillable,
unconditionally, and the canary is sound.  The checker is conservative in the right direction —
fed Trump's *unscaled* placements it returns NO-WITNESS (two of the six snap to a −2.5e-7 core
gap), i.e. it refuses to certify a touching family.

## T9 [M] — why the CONTRADICTORY inner-corner children sit exactly on the knife edge

The dual of the converged a = 0.489 child is integral: five rows of weight 1 each (τ = 5), and
five atoms of weight 1 (`results/acurve_k5_16_a49.json`).  Two of those five rows penetrate a
**pin** core by 1.006e-5 — legal, because caselp keeps a row unless it penetrates by more than
`EPS_CORE = 2e-3`, and that shell is exactly what makes the box-level exact verification work.
So the knife edge is real for this certificate machinery, not a solver artefact: the LP is forced
to cover a 2e-3 shell around each pinned square, and that shell is worth just enough to hold
τ* at 5.  A57 therefore reports the interior YES children as **critical (τ* = budget)** rather
than "alive": `alivewitness` finds no strictly-separated 5-family once the core is an obstacle,
so the disjoint-family bound does not (yet) apply to them.

## T10 [M] — the L1 interior tree: viable, priced, and running

The tree is **not** the ~2-desktop-day grind A54 priced.  Per stratum the 1153 children split
three ways, and only the third costs anything:

| class | k5_11 | k5_16 | cost each | arbiter |
|---|---|---|---|---|
| NO child | 1 | 1 | LP 5–15 s + cert ~1 s | exact certificate (T3) |
| YES, `contradictory` | 344 | 257 | **0 s** | logic (T5) — core meets a pin core |
| YES, `ok` | 808 | 895 | 1–290 s LP + ~6 s cert | exact certificate |

First `ok` children measured end-to-end:

| child | τ | η | LP | cert | verdict |
|---|---|---|---|---|---|
| `k5_11_interior_Y0017` | 4.500000 | −0.500 | 281.8 s | 5.5 s | **PASS** (killed) |
| `k5_16_interior_Y0106` (probe) | 3.000000 | −2.000 | 14.8 s | — | converged, ceiling 1.667 |

η ranges from −2.0 (cores near the middle of the container, where three atoms pierce the whole
residual) to −0.5 (cores just outside the contradictory shell).  Every `ok` child measured so
far is comfortably under budget, so the expected cost of a stratum is ≈ 800–900 LP+cert pairs at
a mean well under the 240 s cap: **hours, not desktop-days, at 5 processes.**

Running detached, resumable, with a per-shard progress file (`progress/<key>_s<i>.json`) and an
auto-scaler (`code/scaleup.ps1`) that holds A57 at ≤ 3 heavy processes while A56's `final_sweep`
is alive and takes the freed slots up to 5 afterwards, launching shards 1/6 … 5/6 of both strata.

**Stratum verdicts as of this writing: both OPEN**, with the whole NO side and 22–30 % of the
YES side already killed, every `ok` child so far certified, and the one resister disposed of at
depth 2 (T11).

## T11 [M] — the one resister, and what actually fixes it

`k5_16_interior_Y0017` (box [2.3578, 2.4976] × [1.9385, 2.0783] × [82.37°, 90°], pinguard **ok**)
**converged** at τ = 5.000000000000014 = budget, minmass = 1, maxcov = 1, in 8.7 s: a genuine
level-1 obstruction, not a time-out.  Two repairs were tried.

**Tried and rejected — the EPS_CORE ladder** (`code/epsladder.py`).  caselp drops a row only if
the placement penetrates a core by more than `EPS_CORE = 2e-3`, while `verify_case.py` exempts a
box only if it is **provably** exempt by exact rational interval arithmetic, no epsilon.  The LP
is therefore strictly more conservative than its own arbiter, and three of the five weight-1
dual rows at this child penetrate a pin core by 2.6e-4 … 2.0e-3 — the whole knife edge looked
like that shell.  Shrinking it is sound in the only sense that matters (fewer rows ⇒ τ can only
fall; the arbiter is unchanged, so a shell that *was* needed merely FAILs the verification).  It
does fall — EPS_CORE = 5e-4 gives τ = 4.800000, η = −0.200 — but the certificate **FAILs**:
19 exact holes, worst mass 415451/1000000 = 0.4155 at (1.578909, 1.454552, 9.51°), and the
witness re-solve pushes τ straight back to 5.000000.  So the shell rows are genuinely required
here and τ* = budget is real.  The lever is kept as an opt-in flag (`tree57.py --eps_ladder`,
default **off**) because it costs ~190 s per resister for a repair that did not work once.

**Works — depth 2 by refinement** (`code/deepen.py`).  Replacing B by a closed cover of B
refines the same disjunction, so every sub-child keeps the **same** budget — a refinement, not a
new branch, which is exactly why depth 2 is affordable where a second zone would not be.  Three
bisections take a from 0.3566 to 0.4233–0.4249:

| sub-box | a | τ | η | LP | verdict |
|---|---|---|---|---|---|
| `..._D00` | 0.4249 | 4.000000 | −1.000 | 14.0 s | **PASS** |
| `..._D01` | 0.4233 | 4.000000 | −1.000 | 15.2 s | **PASS** |
| `..._D02` | 0.4249 | 4.000000 | −1.000 | 84.2 s | **PASS** |
| `..._D03` | 0.4233 | 4.000000 | −1.000 | 56.2 s | **PASS** |
| `..._D04` | 0.4249 | 3.000000 | −2.000 | 37.9 s | **PASS** |
| `..._D05` | 0.4233 | 3.000000 | −2.000 | 51.6 s | **PASS** |
| `..._D06` | 0.4249 | 3.000000 | −2.000 | 22.0 s | **PASS** |
| `..._D07` | 0.4233 | 3.500000 | −1.500 | 41.4 s | **PASS** |

**8/8 — the first level-1 resister is completely dead**, in 322 s of LP plus certification, and
every sub-box cleared the budget by a full unit or more.  Nothing about the parent's
τ = budget survives one bisection.  Each sub-box is re-run through `pinguard.classify` (a
sub-box can be contradictory when its parent was not — more free kills) and the Trump canary.

> **A57 working conclusion.**  A level-1 child that converges at τ = budget is a *coarse box*,
> not an obstruction.  The brief's depth ≤ 2 is the right budget and, so far, a sufficient one:
> refinement costs no budget, raises a from 0.3566 to ≈ 0.424, and buys back 1.0–2.0 of η.

## T12 — a caveat about the early scoreboard: easiest-first makes it θ-biased

The two covers are identical geometry over different pin sets, so ranks are comparable across
strata.  The three level-1 resisters so far are **the same two boxes**, near-upright interior
cores:

| rank | box | k5_11 | k5_16 |
|---|---|---|---|
| Y0017 | [2.3578, 2.4976] × [1.9385, 2.0783] × [82.37°, 90°] | τ = 4.5000 **PASS** | τ = 5.0000 resists |
| Y0041 | [1.5193, 1.6590] × [1.3795, 1.5193] × [82.37°, 90°] | τ = 5.0000 resists | τ = 5.0000 resists |

Tempting to read as "near-upright interior cores are the hard class".  **It is not yet
evidence**: easiest-first orders by distance from Trump's ghost, whose free squares sit at
40.18° (and one upright), so the near-upright slab is exactly what gets served first —
19 of the 22 YES records so far lie in θ ∈ [82.4°, 90°], and all 3 resisters with them.  The
resister *rate* by θ slab cannot be estimated until the ordering has worked past the head.
Two consequences worth keeping:

* do not extrapolate a per-θ cost model from the early scoreboard;
* the shard stride (i mod 6 over a globally sorted list) means **each shard is itself
  easiest-first**, so every shard shares the same bias — running more shards widens the sample
  in centre position but not in θ.

`tree57.py --sample_theta N` answers this without disturbing anything: it keeps the canonical
ghost-distance ordering (so **child ids are unchanged** and a stratified run can never collide
with a shard run) and only changes the *selection*, round-robining over the eight t-slabs and
taking each slab's easiest unseen child.  It is restricted to pinguard-**ok** children on
purpose: within every slab the easiest-first head is the contradictory shell next to the pins,
so a naive stratified sample comes out ~90 % free logic kills (21 of 24, measured) and says
nothing about the resister rate.  The `ok` population is almost perfectly flat across slabs —
111 / 106 / 109 / 108 / 108 / 104 / 114 / 111 for k5_16 — so a stratified sample is directly
comparable slab to slab.  Not launched yet: the process cap is full while A56 runs.


## T13 [M] — the direct route on k5_11 (rung 1/2), for comparison

`ladder57.py --name k5_11 --tag e1` (A54 rung 1 + A55/k3_ext E3 merged warm start: 2593 columns
and 43083 rows folded in from every A53/A54/A57 artefact incl. `_state` checkpoints), row pruning
off, columns pruned at 3 strikes, 3100 s:

| pass | rows | orbits | τ | budget | η | ceiling 6/τ | minmass | maxcov |
|---|---|---|---|---|---|---|---|---|
| A54 W3 | 24133 | — | 5.905058 | 6 | −0.0949 | 1.01608 | — | — |
| **A57 e1** | **39337** | 2593 | **5.910096** | 6 | **−0.0899** | **1.01521** | 0.987375 | 1.099930 |

τ moved **up**, not down — with pruning off the row set grew by 15 k and each new row can only
raise the optimum.  That is the honest shape of the direct route: rung 1 buys coverage
(minmass 0.9874, maxcov 1.0999) at the price of a slightly tighter scale ceiling, and A54 W3's
diagnosis stands — the blocker is convergence, not scale (A54 S2).  Certification (6 rounds,
600 s each, scale cap 1.40 so the auto-scale reaches the true ceiling) is running; the result
lands in `results/k5_11_e1.json`.

This pass is a *hedge*, not the plan: the tree (T3, T10, T11) is the route that is actually
killing children.  It is worth its one process because k5_11's direct certificate was the
closest near-miss in the lab (A54 W3: one hole at exact mass 0.981478, i.e. 1.9 % short) and
because every column it generates is folded back into the tree's warm start by `warm57`.

## T14 [M] — a third failure mode: boundary degeneracy, and the cheap cure

`k5_11_interior_Y0107` (box [2.3578, 2.4976] × [1.5193, 1.6590] × [82.37°, 90°], pinguard ok)
had τ = 4.500000, η = **−0.500**, ceiling 1.111 — comfortable margin — and its certificate
(26 atoms, total 155813/31250 = 4.986016) still **FAILed exact verification**, with a signature
quite unlike the T11 resisters:

    FAIL: 32 witness boxes at depth 56: 0 HOLES, 0 tight, 32 undecided at this depth
      worst witness: theta = 50.200458 deg, centre = (1.481029627, 2.673266088),
                     exact mass = 1038757/1000000  (> 1 !)

**Zero holes.**  The verifier could not *decide* a cluster at θ ≈ 53°, centre ≈ (1.80, 2.40)
whose sampled mass is 1.2465 ≥ 1.  More depth is not the answer — depth 56, 64 and 72 all return
the same 8 undecided boxes (30423 → 31373 boxes, max depth pegged at the cap each time), so the
splitting does not converge: atoms are sitting on placement boundaries.

**A56's row-shrink margin cures it.**  Re-solving the node LP with `EPS_GEO = 0.002` and
certifying (`certify.py --eps_geo`) gives τ = 4.571429 — τ **rises**, as it must, because
shrunk rows make the LP strictly harder — and the certificate

| | |
|---|---|
| atoms | 99 |
| total | 4985907/1000000 = 4.985907 < budget 5 |
| in-loop verifier | **PASS at round 0**, 144246 boxes, max depth used **32**, 3.9 s |
| independent re-verification `--depth 60 --jobs 3` | **PASS**, 144246 boxes, 147256 exact atom checks, max depth used 32, 4.1 s |

Max depth used drops from "pegged at 72 and still undecided" to **32**: the margin removes the
degeneracy outright rather than out-splitting it.  Sound in the usual sense — shrinking rows only
raises τ, and the arbiter is untouched.

`tree57.py` now runs this automatically on any cert FAIL (margins 0.002 then 0.004, ~2 min) before
falling through to depth 2, so the three repair classes are ordered by cost:

| symptom | cause | repair | cost |
|---|---|---|---|
| `rc = 3`, τ = budget | genuinely critical box (T11) | depth 2 refinement (`deepen.py`) | 8 sub-solves |
| `rc = 1`, 0 holes, undecided | atoms on placement boundaries | `--eps_geo` row shrink (T14), **gated on scale headroom (T16)** | ~2 min |
| `rc = 1`, real holes | measure too weak | more witness rounds, then depth 2 | varies |


## T15 [M] — the direct route on k5_11 FAILs, with the T14 signature

`ladder57.py --name k5_11 --tag e1` finished: rung 1 τ = 5.910096 (39337 rows, 2593 orbits,
3101 s), then 7 certification rounds over 4524 s at scale ceiling 1.015212 — **FAIL(rc=1)**,
`results/k5_11_e1.json`.  Every round built a certificate with total ≈ 5.9834 < 6, so the budget
was never the obstacle.  The round-by-round verifier output is the interesting part:

| round | τ | total | boxes | holes | undecided |
|---|---|---|---|---|---|
| 0 | 5.910096 | 5.983534 | 2295572 | **0** | 16 |
| 1 | 5.909134 | 5.983449 | 2301297 | 8 | 8 |
| 2 | 5.906511 | 5.983437 | 2724128 | **0** | 24 |
| 3 | 5.900076 | 5.983407 | 1133700 | 26 | 69 |
| 4 | 5.895315 | 5.983401 | 618367 | 22 | 74 |
| 5 | 5.901164 | 5.983427 | 2352890 | 17 | 63 |
| 6 | 5.895992 | 5.983433 | 1821964 | 8 | 88 |

Rounds 0 and 2 have **zero holes** — the same boundary degeneracy as T14, now on the parent
node, and the witness feedback that follows a zero-hole round is feeding the LP rows it did not
need (rounds 3–6 then manufacture real holes as the measure is dragged around).  Worst witnesses
across the run: exact mass 0.981814 at (1.500019, 1.949778, 0.026°) — note the centre is within
2e-5 of the pin slot (1.5, ...) — then 0.997441 and 0.999337.

**Experiment run — NEGATIVE.** `certify.py --eps_geo` on the k5_11 node.  The margin must be *small*
here, unlike at the child: certification needs τ·1.005 < 6, i.e. τ < 5.970, and τ is at 5.9101 —
**1.0 % of headroom**, whereas eps_geo = 0.002 raised the child's τ by 1.6 % (4.500000 →
4.571429).  So the pass used **eps_geo = 0.0005**.  Result:

| | value |
|---|---|
| re-solve τ (1500 s limit, **not converged**, minmass 0.9388) | 5.952640 → 5.941270 |
| scale / certificate total | 1.0070 / 5.98334 < 6 — budget was never the obstacle |
| round 0 verifier | **FAIL: 23 HOLES + 25 undecided** |

The margin traded *undecided* boxes for **real holes**.  The difference from the child case
(T14) is convergence, not the lever: at the child the eps_geo re-solve converged and the
certificate passed at round 0, whereas here the re-solve was still 6 % short of covering its
rows when the time limit hit (minmass 0.9388), so the shrunk measure genuinely fails to cover.
With only 1 % of τ headroom there is no room to buy that convergence back — more LP time raises
τ toward the 5.970 ceiling as fast as it improves coverage.

**Verdict: the direct route on k5_11 stays blocked, and now for a diagnosed reason** — it is a
*double* bind (boundary degeneracy AND unconverged coverage) on 1 % of headroom, where the cure
for one costs more than the headroom the other needs.  A54 W3's "1.9 % short, blocked by
convergence" was half the story; T15 supplies the other half.  **The tree is the only line**, and
that is now an argued conclusion rather than a preference.


## T16 [M] — the eps_geo retry must be gated on scale headroom

Wiring the T14 lever in unconditionally was wrong, and the cost showed up immediately.
`eps_geo` shrinks rows, so it **only ever raises τ** — measured +1.59 % at margin 0.002
(k5_11_interior_Y0107: 4.500000 → 4.571429) and +0.72 % at 0.0005 on the k5_11 parent — while
certification needs τ·1.005 < budget.  A child sitting *at* the budget (the T11 knife edge,
scale ceiling 1.0000) therefore cannot be helped by any margin at all.

`k5_11_interior_Y0036` is the receipt: τ = 5.000000, ceiling 1.0000, and the inline retry
dutifully tried margin 0.002 (rc = 3 after 349.8 s) and 0.004 (rc = 3 after 1496.8 s) before
falling through to depth 2 — **1847 s spent to reach the conclusion its own τ already implied.**

`tree57.eps_geo_margins(tau, budget)` now decides from the ceiling, and `sweepfails.py` imports
the same function so both paths agree:

| scale ceiling = budget/τ | margins tried | rationale |
|---|---|---|
| < 1.010 | **none** — straight to depth 2 | a margin costs more headroom than exists |
| 1.010 – 1.050 | 0.0005, 0.001 | thin: only a small shrink is affordable |
| ≥ 1.050 | 0.002, 0.004 | the Y0107 regime, where it works |

The retry is also capped at **one** witness round: a margin either fixes the degeneracy at
round 0 (as at Y0107) or it does not, and extra rounds just drag the measure around — exactly
what happened on the k5_11 parent in T15, where rounds 3–6 manufactured real holes.

Live check of the rule against the four children measured so far:

| child | τ | ceiling | margins chosen | actual outcome |
|---|---|---|---|---|
| Y0036 | 5.000000 | 1.0000 | () | rc = 3 twice, 1847 s wasted — rule would have skipped |
| Y0461 | 4.916667 | 1.0169 | (0.0005, 0.001) | written off by the first sweep at the WRONG margins; re-run pending |
| Y0467 | 4.631579 | 1.0795 | (0.002, 0.004) | **PASS at 0.002** (941.6 s) |
| Y0107 | 4.500000 | 1.1111 | (0.002, 0.004) | **PASS at 0.002** |


## T17 — the T14 lever's hit rate, and why the sweep is a daemon

Boundary-degeneracy failures are **not rare**: `Y0107`, `Y0461`, `Y0467`, `Y0431`, `Y0485` in the
first ~180 children, i.e. roughly 3-5 % of the cover.  The margin cures most but **not all** of
them, and headroom does not predict which:

| child | ceiling | margin | outcome |
|---|---|---|---|
| k5_11_interior_Y0107 | 1.1111 | 0.002 | **PASS** (re-verified independently at depth 60) |
| k5_11_interior_Y0467 | 1.0795 | 0.002 | **PASS** (941.6 s, daemon, unattended) |
| k5_16_interior_Y0431 | 1.1111 | 0.002 | **PASS** (1105.3 s, daemon, unattended) |
| k5_11_interior_Y0041_**D02** | 1.1538 | 0.002 | **PASS** (1294.6 s) — a *depth-2* sub-box |
| k5_16_interior_Y0593 | — | **0.004** | **PASS** — first win on the SECOND margin |
| **k5_11_interior_Y0485** | **1.1111** | 0.002, 0.004 | **FAIL** — both exhausted (873.5 s) → depth 2 |
| **k5_16_interior_Y0461** | 1.0169 | 0.0005, 0.001 | **FAIL** — both exhausted → depth 2 |
| k5_11_interior_Y0461 | 1.0169 | 0.002, 0.004 (**wrong**, T16 wants 0.0005/0.001) | invalid trial; re-run pending |

**5 of 7 at correct margins** (an eighth trial used the wrong margins and does not count).  The
rate has wobbled with every batch — 4/4, 3/4, 3/5, 4/6, now 5/7 — so treat it as "roughly two
thirds" and do not quote it as settled until the cover is done.  Y0593 is the first child cured
by the **second** margin (0.004 after 0.002 failed), which is what justifies trying a pair rather
than a single value.  Y0485 in particular has exactly the ceiling of two that passed, so **good headroom is
NECESSARY for the lever (T16) but nowhere near sufficient**; the gate is not a predictor of
success, it only stops hopeless cases burning 30 minutes.  Depth 2 remains the backstop, and on
current evidence it is the workhorse rather than the exception.

At ~5 % of the ~1700 remaining pinguard-ok children that is on the order of 80 children which
would otherwise each have cost 8 depth-2 sub-solves instead of one margin retry — which is what
makes T14 worth its complexity, and T16 (the headroom gate) worth the care.

All five came from the two shards launched **before** the T14 wiring; every shard started since
carries the inline retry, so the backlog stops growing once those two finish.  `sweepfails.py`
runs as a daemon (`--watch 600`) because a one-shot sweep only ever sees the snapshot it started
with — three hand-runs were needed before that was obvious.


## T18 [M] — BLAS oversubscription, not RAM, is what kills concurrent A57 jobs

Running five top-level jobs at once took down **two of them at the same moment**:

* `deepen.py` — `OpenBLAS error: Memory allocation still failed after 10 retries, giving up.`
* tree shard `k5_11_interior_L1_s0` — `numpy._core._exceptions._ArrayMemoryError: Unable to
  allocate 76.3 MiB for an array with shape (63291, 158)`

**76 MiB failed while 9.9 GB was free**, and A57's own processes held only ~2 GB between them.
So this is not RAM exhaustion: numpy/OpenBLAS spawns roughly one thread per core (20 here) in
*every* process, each thread carrying its own allocation arenas, and several concurrent jobs
multiply that until an allocation fails against fragmentation / arena limits rather than against
free memory.  A54 W7 hit the same class of failure (`MemoryError: bad allocation` at 32k rows
× 6k columns with four jobs) and worked around it by pruning columns; that treated the symptom.

Fix: pin every A57 worker to a single BLAS thread — `OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=
MKL_NUM_THREADS=NUMEXPR_NUM_THREADS=1` — set in `code/launch.ps1` and in the new generic
`code/run_job.ps1` so shards, `deepen`, `sweepfails` and one-off certifies all inherit it.  These
jobs are LP + numpy-oracle work and are not BLAS-bound, so the parallelism was buying nothing;
the contention was pure cost.

**Operational lesson:** the brief's "≤ 3 processes while A56 runs, 5 after" is a *core* budget,
and a core budget is not a memory budget.  Check free memory before adding a job, and do not read
"9.9 GB free" as "safe to launch" — the failure mode here is per-process thread arenas, which a
free-memory check does not see at all.


## T19 [M] — COMMIT, not RAM, is the machine's binding constraint (A60 relay)

A60 measured an A57 `certify.py` reserving **6.7 GB of commit against a 1.75 GB working set**
(~4x) and two `tree57.py` at ~4 GB commit each, and lost its shard 1/2 to a 38 MiB allocation
while A57 held those reservations.  T18's BLAS pinning was necessary but not sufficient.
Confirmed here: **commit limit 61.0 GB, 57.9 GB used, 3.1 GB free** at the time of measurement,
with A57 workers at commit/working-set ratios of 3.25, 4.07, 4.60 and 30.

**Where the overreserve comes from — measured, not guessed.**

    python -c "import numpy"   ->  working set 27 MB,  COMMIT 628 MB   (23x)

Per-process *baseline* dominates.  Two consequences, both fixed:

1. **Process fan-out.**  `verify_case.py` runs `mp.Pool(--jobs)`, so a certify at `--jobs 2` was
   `certify.py` + `verify_case.py` + 2 pool workers = 4 processes, ~2.5 GB of commit in baselines
   before touching a byte of data.  `--jobs 1` takes verify_case's in-process branch and spawns
   nothing.  `VERIFY_JOBS_CAP = 1` now caps the verifier fan-out in `tree57.py`, `deepen.py` and
   `sweepfails.py`.  **Saving ~1.3 GB of commit per concurrent certify.**
2. **Peak numpy temporaries become permanent commit.**  Windows keeps the commit charge on a
   freed heap block, so a process's steady commit tracks its *peak* allocation, not its current
   one.  The two oracle loops in `lpbox.py` were chunked at 1e7 / 2e7 elements — 80 / 160 MB per
   temporary, with several live at once.  `A57_CHUNK` (env `A57_ORACLE_CHUNK`, default 2e6) cuts
   those to 16 / 32 MB.

**The chunk change is result-neutral, bit for bit**, and this was verified rather than asserted:
every output element is a dot product over the full inner dimension and each iteration writes a
disjoint output slice, so only the loop count changes.  Re-running the k5_16 (2.0084, 2.0084, 86 deg)
probe after the change reproduced the earlier run exactly — tau = 3.000000, converged,
minmass 1.000000, maxcov 1.000000, **rows 144, orbits 3486** — identical on every field.
This is the one A57 edit to A54's `lpbox.py`; it is flagged in the file itself.

**Defer instead of dying.**  Adopted A60's `tree60.defer()`.  `tree57.py` and `deepen.py` now
catch `MemoryError` (numpy's `_ArrayMemoryError` subclasses it) around the node solve, append the
node to `results/deferred_<key>.jsonl`, sleep 30 s and continue — **without** writing a summary
record, so the node stays out of `done` and is retried on the next pass.  Deferring can only
postpone work, never assert a verdict, so it is safe by construction.  Previously a transient
spike killed the worker and took its whole remaining queue with it (T18: one tree shard and one
deepen job lost together).

**The scaler is now commit-aware.**  Process count was never the right budget: `scaleup.ps1`
reads `Win32_OperatingSystem.FreeVirtualMemory` (which on Windows *is* commit-available;
`TotalVirtualMemorySize` is the commit limit) and refuses to launch below **10.5 GB** — roughly
4.5 GB for the new worker plus a 6 GB cushion that belongs to the other campaigns, not to A57.
Measured immediately after: limit 58.4 GB, used 52.2 GB, **available 6.19 GB**, so the gate is
correctly holding launches off right now.

**Standing rule:** free *physical* memory is not the number to check before launching an A57
worker.  Check commit-available.  T18's crash looked like a RAM problem and was not; this one
looked like a per-job problem and was per-process.


## T19b [M] — the recycle, measured per shard

Both level-1 shards were started before the T19 trims, so they still carried `--jobs 2` verifier
fan-out and the 1e7/2e7 oracle chunks.  Recycled **one at a time** (coordinator's call), so at
most one in-flight child is lost at a time and each shard gives a clean before/after:

| shard | commit before | commit after | peak before | peak after | resumed at |
|---|---|---|---|---|---|
| 1/6 | 4.89 GB | 4.27 GB | **5.86 GB** | **4.66 GB** (−20 %) | done = 50 |
| 0/6 | 3.86 GB | 3.82 GB | **4.43 GB** | **3.98 GB** (−10 %) | done = 106 |

Peak commit across the pair: **10.29 -> 8.64 GB (−1.65 GB)**.  Commit-available over the whole
operation went 4.32 GB -> 10.61 GB, most of it simply from stopping the two old processes
(4.87 GB and 3.69 GB released respectively) and the rest from the trimmed relaunch.

**Caveat on the headline number.**  Shard 1/6 measured 3.69 GB commit / 3.96 GB peak 45 s after
relaunch, which would have read as −1.90 GB peak; by the time it had warmed up it settled at
4.27 / 4.66, i.e. −1.20 GB.  A freshly launched worker has not yet hit its peak, so **do not
quote a commit figure from a process that has not been through several children.**  The table
above uses settled figures.

The verifier fan-out saving (~1.3 GB per concurrent certify, from `VERIFY_JOBS_CAP = 1`) is
*not* in these numbers: it is per-certify and neither shard was in a certify when measured.
Both shards resumed correctly — finished children skipped, column pool re-folded (3860 and 4471
atoms).  Note 0/6's jsonl has 110 lines but resumed at done = 106: `done` is keyed by child id
and four lines are superseded records (e.g. Y0107's T14 correction), which is the intended
behaviour of the last-record-wins convention.

The `sweepfails` daemon was restarted once commit-available cleared 10 GB, as agreed.


## T20 — relaunch after the pagefile restart, and a guard bug that hid a dead scaler

The PI restarted the machine to move the pagefile to `F:\pagefile.sys` at **25 GB initial /
100 GB maximum**, so the commit limit now grows on demand toward ~130 GB.  **Commit is no longer
the binding constraint** (it was: 61 GB limit, 57.9 GB used, A60 losing a shard to a 38 MiB
allocation).  `scaleup.ps1`'s gate drops 10.5 GB -> 6 GB, kept only as a safety net because a
growing pagefile still takes time to extend.  T18 pinning and the T19 trims stay: they were never
about the pagefile.

**All state survived** (results are on disk): 110 / 67 / 104 level-1 records, 15 + 8 depth-2, and
**168 PASS certificates**.  Every worker resumed at the right place:

| worker | resumed at |
|---|---|
| k5_11 shard 0/6 | done = 106 of 193 |
| k5_16 shard 0/6 | done = 101 of 193 |
| k5_11 shard 1/6 | relaunched by the scaler |
| deepen k5_11 | parents = 22 (the current backlog) |
| sweepfails | eligible = 0 (nothing outstanding) |

**The guard bug.**  The single-instance guard matched `-File*scaleup.ps1*` on command lines, and
a *status check* — `powershell -NonInteractive -Command '... -File ...\scaleup.ps1 ...'` — carries
both tokens in its own command line.  So the guard saw a tool session as a running scaler and
made the genuine one exit: `another scaler (pid 7368) is older; this one (14584) exits`, where
7368 was a transient tool session that had already gone.  This is the **third** appearance of the
same false positive (T19 documented it for *counting* scalers; it then bit the *guard* itself),
which is the lesson: **a process's own command line is not a usable identity when the thing you
are searching for is the script's name — every observer mentions it.**  Fixed with a pidfile as
the primary record (`logs/scaleup.pid`), plus a command-line scan that now excludes
`-NonInteractive` and self.  Verified: the scaler starts, logs `scaleup started; A57=4`, and
writes its pid.

Also fixed while relaunching: the scaler's `deepen.py` launch was a direct `Start-Process` and so
ran **unpinned** — `launch.ps1` sets the BLAS variables in its own process, but that path bypassed
it.  The pinning is now set at the top of `scaleup.ps1`, where every child inherits it.

## T21 [M] — A63 window assessment: which repair is cheaper for A57's leaves

A63's Lemma B/B' (`docs/proofs/closed_disjoint_bridge.md`): a fixed-side PASS transfers to sides
m with (s"/m - 1)*A < rho(C), rho(C) = min_j (1/2 - a_j*(cos th_j + sin th_j)), A <= 5/2.

**Which core binds, for A57.**  A leaf carries SIX cores: the 5 pins at slots (eps-fat,
a = 16383999967232/32768001953125, rho ~ 1e-9) and the YES cover box at an interior centre
(a ~ 0.3566, th_m ~ 87 deg, rho ~ 0.127).  rho(C) is a MINIMUM, so **the pins bind and the cover
box is irrelevant** — the knob is `hyp_from_slots`'s pin boxes, not the branch geometry.  caselp
derives a from the box: a square pin box of half-width h gives a = 1/2 - h*sqrt(2), so
h = delta/sqrt(2) yields rho = delta exactly.  Fattening the pin box also WEAKENS the hypothesis
(the pinned square need only lie within h of the slot), enlarging the stratum — sound, and a
strictly stronger kill.

### (a) parametric re-emission — BLOCKED, and not by a format detail

`make_param.core_anchor()` raises `ValueError` unless a core coordinate is exactly in
{1/2, 3/2, 5/2} u {s0-1/2, s0-3/2, s0-5/2}.  Every A57 leaf has a sixth core at an arbitrary
interior centre (measured: kx = 4855383/2000000 = 2.427692, ky = 4016841/2000000 = 2.008421), so
**make_param rejects every A57 tree leaf outright**.  This is structural: the forced anchoring
encodes A56 P1 (slot coordinates are affine with beta in {0,1}).  `verify_param.py` itself is more
general — it widens core centres to [alpha+beta*a, alpha+beta*b] for rational beta — so the
VERIFIER could take an interior core; the blockers are (i) the emitter's anchor rule and (ii) a
missing lemma that the interior cover REMAINS A COVER of the zone across the s-family (the zone is
[c0, s-c0], c0 = 1.1, subdivided into 12 columns, so each box edge is affine in s with
beta = i/12 not in {0,1}).  So this is an A56 tool change + a new soundness argument + 4D
re-verification of ~2300 leaves — not the advertised "post-pass, no LP redo".

### (b) slack cores — measured cost, and it is NOT flat

`code/slackprobe.py`, three representative children, tau at the same box with slackened pins:

| delta | sides to cover [3.82, s0] | eta = -2.0 child | Y0107 (eta = -0.500) | knife edge (eta = 0) |
|---|---|---|---|---|
| 0 | 1 203 879 | 3.000000 | 4.500000 | 5.000000 |
| 1e-3 | **38** | 3.000000 (+0) | 4.538462 (**+0.038**, eta -0.462) | 5.000000 (+0) |
| 1e-2 | **4** | 3.000000 (+0) | 4.666667 (**+0.167**, eta -0.333) | 5.000000 (+0) |
| 3e-2 | **2** | 3.000000 (+0) | **5.000000 (+0.500, eta = 0 — KILLABLE NO MORE)** | 5.000000 |

So the cost is zero on slack children and on the knife edge, but **scales with delta on thin
ones**: 8 % of margin at 1e-3, 33 % at 1e-2, and 100 % at 3e-2.  **delta = 3e-2 (2 sides) is
excluded** — it turns the thinnest killable class (tau = 4.5, the commonest non-trivial leaf
value) into an unkillable one.  delta = 1e-2 is affordable with ~2x headroom on that class.

### (b') re-emission as a free post-pass — mostly a dead end

Shrinking the pin cores of an EXISTING PASS certificate and re-verifying (no LP at all) works
only where the measure already covered the shell:

| leaf | delta = 1e-3 | delta = 1e-2 | delta = 3e-2 |
|---|---|---|---|
| `k5_11_interior_NO` (eta = -3.0) | PASS | PASS | FAIL (16 holes) |
| `k5_11_interior_Y0023` | PASS | FAIL | — |
| `k5_11_interior_Y0024` | PASS | FAIL | — |
| `k5_11_interior_Y0017` | FAIL | FAIL | — |

The first result (the NO child, PASS at 1e-2) was **not representative** — that child has eta = -3
and enormous slack.  On real YES leaves it is ~2/3 free at 1e-3 and ~0/3 free at 1e-2.  Since
1e-3 needs 38 sides anyway, the free post-pass does not by itself buy a window.

### Cost estimate

| route | sides | LP work | estimate |
|---|---|---|---|
| (b) delta = 1e-3 | 38 | ~1/3 of leaves per side + 37 full re-runs | ~76 desktop-days — not viable |
| **(b) delta = 1e-2** | **4** | 4 full tree re-runs (re-emission does not carry at this delta) | **~8 desktop-days = 4x the current campaign** |
| (b) delta = 3e-2 | 2 | — | EXCLUDED: kills the tau = 4.5 class |
| (a) parametric | 1 | A56 emitter change + cover-invariance lemma + 4D verify of ~2300 leaves | unbounded until the lemma exists; 4D cost per leaf unmeasured |

**Recommendation for A57: the slack-core grid at delta = 1e-2, four fixed sides, ~4x the current
campaign, needing no new theory beyond B' which is already proved.**  Two caveats for the
advisor: (i) at delta = 1e-2 the pin box half-width is 7.07e-3, so the pin hypothesis weakens —
slot spacing is 1.0 so no slots overlap, but A53 V9 / A55 E4 class-containment relations assume
exact slots and should be re-checked before the census is reused; (ii) any child found at
eta > -0.167 would flip to alive at this delta — the natural remedy is depth-2 refinement, which
empirically returns eta <= -0.667 (T11), so the tree already has the tool.

## T22 [M] — route (a) 4D cost probe (soundness-conditional)

Requested by the coordinator to price route (a) against T21's 8 desktop-days for the slack-core
grid.  `code/to_param.py` converts an A57 leaf to `parametric-kill-certificate-v1`, bypassing
`make_param`'s forced anchor rule.  The interior cover core gets the affine centre the cover
actually implies, and the reconstruction is **exact**:

    zone [c0, s - c0], c0 = 11/10, 12 columns
    centre_x(s) = alpha + beta s,  beta = (i + 1/2)/12,  alpha = c0 (1 - 2 beta)
    verified as Fractions: beta = 19/24, alpha = -77/120 reproduces kx = 4855383/2000000 exactly
                           beta = 13/24, alpha = -11/120 reproduces ky = 4016841/2000000 exactly

Pins keep their slot anchors; atoms use make_param's default nearest-wall rule.  **This is a cost
probe, not a kill**: the cover-invariance lemma (that the cover stays a cover for every s) is with
the theory lead, and a PASS here would still be conditional on it.

| leaf | atoms | eta | 4D result, s in [3.82, s0], depth 48, margin 0 | wall |
|---|---|---|---|---|
| `k5_11_interior_Y0275` | 4 | -1.000 | **FAIL** — 205550 boxes, 479 s-cells, **0 HOLES**, 8 undecided | **14 s** |
| `k5_11_interior_Y0377` | 159 | -2.000 | **NO VERDICT** at the 2400 s cap | **> 2400 s** |
| `k5_16_interior_Y0593` | 363 | -0.250 | **PASS**, 2348522 boxes, 0 witnesses | **276 s** |

**Two findings already decisive.**

1. **RETRACTED: cost is not monotone in the atom count.**  With only the first two leaves in hand
   this looked like an atom-count explosion (4 atoms 14 s, 159 atoms no verdict in 2400 s).  The
   third leaf refutes it: **363 atoms PASSED in 276 s** with 2348522 boxes and zero witnesses.
   See T24 for what actually predicts the cost.  A57's leaves are mostly small (the NO children carry
   3 atoms, many YES leaves 4-30), but the eps_geo-repaired ones carry 99-363.  A blanket 4D pass
   over ~2300 leaves is therefore dominated by the fat tail, not the median.

2. **The failure is at the BOTTOM of the window and is the T14 signature.**  Witnesses cluster at
   s in [3.822397, 3.823066] — the far end from s0 — with **0 holes** and worst mass 1.2468 >= 1,
   i.e. undecided boxes, not uncovered ones.  That is the anchoring being wrong far from s0, not
   the geometry failing: the measure is tuned at s0 and the nearest-wall rule drags atoms badly
   over a 1.5 % change in s.  A56 ships `--beta-mid` and `--overrides` precisely because anchoring
   choice decides completeness (soundness.md P3: "a bad anchoring can only make the verification
   FAIL").

**So route (a) is not "convert and verify" — it is "convert, verify, and SEARCH ANCHORINGS until
PASS", per leaf, over ~2300 leaves**, with each attempt costing seconds to many minutes.  Even
before the pending two leaves land, that is a materially worse profile than T21's slack-core grid,
whose cost is four ordinary tree runs of already-proven machinery.

## T23 [M] — the hybrid window route: gate, grid, emission switch

### (1) GATE PASSED — V9/E4 survive a fattened pin

At delta = 1e-2 the pin box half-width is h = 7.0711e-3 and the pin core half-side is a = 0.49.

| check | value | verdict |
|---|---|---|
| min Chebyshev separation between distinct slots, over the whole census | **1.000000** (k6_00) | — |
| h-balls around distinct slots disjoint? | 2h = 1.4142e-2 < 1.0 | **yes** |
| fattened pin CORES pairwise disjoint? | 2a = 0.98 < 1.0 | **yes** |
| can one centre lie in two pin boxes (the pinguard "parent" failure)? | needs 2h >= 1.0 | **no** |
| A55 E4: every open k <= 4 class inside one of {k5_11, trump5, k5_16} | re-checked class by class | **holds** |

The containment argument is monotone and so survives fattening for free: if S subset T as slot
sets then a packing with a square within h of every slot of T also has one within h of every slot
of S, i.e. stratum_h(T) subset stratum_h(S).  Nothing in V9/E4 depends on the pin radius, and the
separation numbers show the fattening is three orders of magnitude away from making distinct
slots interfere.  **Gate clean.**

### (2) The grid, and the switch

rho = 1125896618508387/112589990684262500 = 9.99997079e-3, slab relative width rho/(5/2) =
3.999988e-3.  Sides on the 1/250000 grid, stepped at 95 % of a slab so consecutive slabs OVERLAP:

| side | s | covers |
|---|---|---|
| 1 | 969271/250000 = 3.877084 | (3.861637, 3.877084] |
| 2 | 965601/250000 = 3.862404 | (3.847016, 3.862404] |
| 3 | 192389/50000 = 3.847780 | (3.832450, 3.847780] |
| 4 | 958303/250000 = 3.833212 | (3.817940, 3.833212] |

Four sides cover down to 3.81794 < 3.82.  **Emission switched**: `tree57.py` and `deepen.py` take
`--pin_delta` (default **1e-2**), every record carries `pin_delta` and `side`, and the campaign
now runs under tag **G1** = grid side 1 so that delta = 0 and delta = 1e-2 records can never be
mixed (a delta = 0 logic kill is not valid at delta = 1e-2 -- the pin core is smaller, so 331 of
k5_11's 344 contradictory boxes survive and 13 become ordinary `ok` children).

**Per-side C-check** (A63's per-box C-check, pure geometry, seconds per side).  The cover shrinks
at the lower sides because the zone [c0, s - c0] does:

| side | k5_11 free / ok | k5_16 free / ok |
|---|---|---|
| 1 | 331 / 821 | 238 / 914 |
| 2 | 336 / 816 | 245 / 907 |
| 3 | 264 / 704 | 184 / 784 |
| 4 | 273 / 695 | 191 / 777 |

### (3) Revised estimate

Across four sides and both strata: **6418 `ok` children needing an LP, 2062 free logic kills, 8 NO
children.**  Side 1 alone is 1735, so the grid is **3.70x a single side, not 4x**.

| scenario | children | estimate |
|---|---|---|
| no skip list, 3 workers | 6418 | 10.7 desktop-days |
| no skip list, 5 workers | 6418 | **6.4 desktop-days** |
| skip list exempts 20 % of sides 2-4 | 5481 | 5.4 days |
| skip list exempts 30 % | 5013 | 5.0 days |
| skip list exempts 50 % | 4076 | 4.0 days |

So it lands **under** the naive 8 days even with no skip list at all, and the skip list is what
takes it toward 4-5.  Honest caveat: side 1 is NOT free -- the ~300 children already emitted at
delta = 0 carry certificates whose cores are eps-fat, so they must be re-emitted; what carries
over for free is the accumulated warm-start column pool (G1 started warm at 3522 atoms) and,
after the C-check, the logic kills.


## T24 [M] — 4D cost, final, and what it bounds the skip list to

| leaf | atoms | 4D result, s in [3.82, s0], depth 48, margin 0 | wall |
|---|---|---|---|
| `k5_11_interior_Y0275` | 4 | FAIL (0 holes, 8 undecided at s ~ 3.8224) | **14 s** |
| `k5_11_interior_Y0377` | 159 | **no verdict at the cap** | **> 2400 s** |

So 40x the atoms costs **> 170x** the time.  4D verification is usable only on genuinely small
leaves, which is exactly why the advisor's "parametric as a skip-list generator, <= 30 atoms, one
attempt each" is the right shape -- a blanket parametric pass over the corpus was never on.

**What the skip list can reach.**  Over the 198 PASS leaves emitted so far:

    atoms: min 3, median 7, mean 47.2, p90 157, max 602
    <= 10 atoms: 133 (67 %)   <= 30: 150 (76 %)   <= 50: 157 (79 %)   <= 100: 169 (85 %)

The distribution is strongly bimodal -- a median of 7 against a mean of 47 -- because the
eps_geo-repaired leaves (T14) carry 99-363 atoms while ordinary ones carry 3-10.  So the <= 30
cut covers **76 %** of leaves at a cost of seconds each, and the expensive tail is precisely the
minority that the grid has to do anyway.

**Yield is still unmeasured.**  The single completed 4D run FAILed, and on the naive nearest-wall
anchoring -- so the fraction of small leaves that PASS in one `--beta-mid` attempt is unknown, and
the T23 estimate table deliberately brackets it (20 / 30 / 50 %) rather than assuming one.  The
skip list is upside on a 6.4-desktop-day grid, not a load-bearing part of it.

## T25 [M] — CORRECTION: atom count does not predict 4D cost; ROBUSTNESS does

The third cost-probe leaf refutes T24's first reading, and the refutation is more useful than the
claim it replaces.

| leaf | atoms | origin | eta | 4D over [3.82, s0] | wall |
|---|---|---|---|---|---|
| `k5_11_interior_Y0275` | 4 | ordinary | -1.000 | FAIL (0 holes, 8 undecided at s ~ 3.8224) | 14 s |
| `k5_11_interior_Y0377` | 159 | ordinary | -2.000 | no verdict at the cap | > 2400 s |
| `k5_16_interior_Y0593` | **363** | **eps_geo-repaired** | -0.250 | **PASS**, 2348522 boxes, **0 witnesses** | **276 s** |

The **largest** certificate is the one that passed, and it passed comfortably.  So "cost explodes
with atoms" was an artefact of n = 2 -- I should not have stated it before the third leaf landed.

**Hypothesis (n = 1, stated as a hypothesis).**  What separates Y0593 is not its size but that it
was repaired with `--eps_geo 0.004` (T14).  eps_geo re-solves with shrunken rows precisely to make
the measure ROBUST to boundary effects; a robust measure discharges 4D boxes instead of leaving
them undecided.  Both failures are the undecided-not-uncovered signature (Y0275: 0 holes, 8
undecided), which is exactly what a non-robust measure produces.  If this holds up, then:

* the right skip-list filter is **"was this leaf eps_geo-repaired?"**, not "does it have <= 30
  atoms" -- and those are nearly ANTI-correlated, since eps_geo leaves are the fat-atom tail
  (99-363 atoms) while ordinary leaves are the 3-10 atom bulk;
* the T24 recommendation to restrict the skip list to <= 30 atoms would have selected almost
  exactly the wrong subset;
* a cheap way to manufacture skip-list candidates is to run `--eps_geo` on a leaf *before* the 4D
  attempt, even when its 3D certificate already passed.

**This is also A57's first 4D PASS over the whole window** -- soundness-conditional on the
cover-invariance lemma (still with the theory lead), but it demonstrates route (a) is not merely
affordable on some leaves, it is achievable, and that the skip list has real yield.

**Next measurement to settle it** (cheap, and it decides the skip-list filter): run the 4D pass on
3-4 more leaves split by origin -- 2 eps_geo-repaired, 2 ordinary of similar atom count -- and see
whether the PASS/FAIL split tracks origin rather than size.  Until that is done the skip-list
yield stays bracketed in the T23 estimate rather than assumed.

## T26 — the 19:08 hard stop: no data damage (incident closed)

Kernel-Power 41, BugcheckCode 0, no dump.  PI attributed it to two games running alongside the
campaigns; **not** a hardware or software fault of A57's, and no cooling investigation followed.
The 5-worker cap therefore stands.

**Integrity check** (`code/fsck.py`, written for this and kept for the next one).  A hard stop can
leave a partially written last line in an append-only jsonl or a truncated whole-json.  Result
across 9 jsonl files and every progress / node / certificate json:

    jsonl_files 9 | jsonl_trimmed 0 | jsonl_would_trim 0 | jsonl_midfile_bad 1 | json_corrupt 0

**Zero crash damage.**  The single malformed line was **my own emitter bug, not the crash**:
`code/param_cost.sh` substituted an empty `boxes` field on the timeout path, writing
`...,"verdict":"TIMEOUT/ERR(rc=0)",""}`.  Repaired in place (original in `quarantine/`), the
emitter fixed, and `fsck` now reports the corpus fully clean.

Why nothing was lost: every writer appends a complete record only after the work it describes is
finished, so an interrupted child leaves NO record and is simply redone — the same property that
makes `defer()` safe (T19).  `fsck.py` will only ever trim a malformed **last** line, and copies
both the file and the offending text to `quarantine/` first; a malformed line anywhere else is
reported and left for a human, since that is corruption of a different kind.

**The T19 commit gate demonstrably worked during the incident window**, refusing to add load while
the box was starved:

    19:22:38 commit headroom 3.9 GB < 6 GB: NOT launching (running=3 cap=3)

Resumed cleanly at 19:37 with G1 intact: k5_11 shard 0/6 at done = 4, k5_16 shard 0/6 at done = 9,
five workers, 28.6 GB commit available.

## T27 [M] — the big committers are NOT A57's; the trims are live

A60 relayed that commit headroom dipped to 2.57 GB with `certify.py` processes at 8.5 and 5.6 GB
commit, and asked whether A57's T19 trims had been bypassed on the G1 path.  Attributed by
campaign directory rather than by process name:

| campaign | procs | total commit | biggest certify |
|---|---|---|---|
| **A61-window-stragglers** | 4 | **14.24 GB** | **8.63 GB at `--jobs 3`**, 5.42 GB at `--jobs 3` |
| A57-shadow-trees | 6 | 4.86 GB | **0.84 GB at `--jobs 1`** |
| other | 12 | 3.13 GB | — |
| A60-trump5-campaign | 3 | 1.33 GB | 0.49 GB at `--jobs 2` |

**The trims are active and working.**  A57's certify processes run at `--jobs 1` and 0.52-0.84 GB
of commit; the two multi-gigabyte ones are A61's, at `--jobs 3`.  `A57_CHUNK` is 2e6 by default
with no env var needed, so it is live in every A57 path including G1's.  A57 is not the dominant
committer — A61 is, by roughly 3x.

**Why the misattribution was easy — and my first fix was ALSO wrong.**  `certify.py` is copied
into every campaign directory, so a scan keyed on the *process name* identifies nothing.  My
repair was "attribute by the path in the command line" — which A60 correctly points out is still
ambiguous, because **a command line contains several paths naming different campaigns**:

    python ...attempts\A54-stragglers\code\certify.py                 <- SCRIPT (A54's copy)
           ...attempts\A61-window-stragglers
esults
odes\k5_05.json  <- DATA   (A61's)
           --out ...attempts\A61-window-stragglers\certs\k5_05.json     <- OUTPUT (A61's)

The two big committers run **A54's** copy of `certify.py` and write **A61's** certificates.  My
T27 number (A61 11.5 GB) was right **only by luck**: 'A54-stragglers' was not in my tag list, so
the script path was invisible to the scan and it fell through to the data argument.  Demonstrated:

    T27's scan, A54 not in the tag list  ->  {A61: 11.50, A60: 1.72, A57: 0.78}
    the SAME scan with 'A54' added       ->  {A54: 11.50, A60: 1.72, A57: 0.78}   <- WRONG

One tag added to a list flips 11.5 GB onto the wrong campaign.

> **Refined rule (A60).  Attribute by the `--out` target; fall back to the data/node argument;
> use the script path only as a last resort and flag it unreliable.  Never the process name.**

Implemented as `code/whose.py`, verified against the live process table:

    campaign attributed by            commit GB    WS GB
    A61     --out                         6.08     2.01
    A61     --out                         5.42     1.97
    A60     --out                         0.89     0.29
    A57     --out                         0.52     0.19
    total: A61 11.50 GB | A60 1.18 GB | A57 0.87 GB

**Fourth instance of one trap class this session** (A60's count), and the shape is always the
same — *matching on an identifier that is not unique to the thing identified*:

| # | identifier matched | what it actually matched | cost |
|---|---|---|---|
| 1 | `scaleup.ps1` in a command line | my own status checks, which mention the script | killed the real scaler; ~1.5 h with no auto-scaling |
| 2 | same string, inside the single-instance guard | a transient tool session | made genuine scalers exit on sight |
| 3 | a PID reported as "already running" | a recycled/dead PID | a scaler believed alive was not |
| 4 | `certify.py`, then *any* path in its command line | a shared filename; then the script's own copy | 11.5 GB attributable to the wrong campaign |

The general remedy: identify a process by **what it is acting on**, not by what it is or where its
code lives.  For certifiers that is the `--out` target, because a certificate belongs to whoever
it is written for.

**The lever, for whoever wants it.**  Both trims are one-line changes in a campaign's own copies:
`--jobs 1` on the certify invocation (verify_case takes its in-process branch and spawns no pool —
worth ~1.3 GB per concurrent certify at `--jobs 3`), and the `A57_CHUNK` bound on the two oracle
loops in `lpbox.py` (peak numpy temporaries 80/160 MB -> 16/32 MB; bit-for-bit result-neutral,
verified in T19).  A61 would gain the most.

Hygiene done here: `ladder57.py` and `epsladder.py` — not currently in the campaign but able to be
run later — now carry `VERIFY_JOBS_CAP` too.  `ladder.py` and `substrat.py` are unmodified A54
copies kept for provenance and are never invoked by A57.


## T28 — a FALSE artefact, caught by A78's Lean formalization (bug-ledger)

**`results/alive/k5_16_m5.json` carried a false LP-UNKILLABLE claim.**  Found by A78 while
formalizing `alivewitness.py` in Lean; independently re-audited here over all 11 files in
`results/alive/` before acting.  The file records `budget = 6`, `m = 5`, `ALIVE-CERTIFIED`, and

    tau*(k5_16) >= 5 = budget => NO certificate can exist for this node (LP-unkillable)

"5 = budget" is false — k5_16's budget is **6**.  A57-3 gives `tau* >= m`, and unkillability needs
`m >= budget`; at m = 5 < 6 the bound is a real lower bound that says nothing about killability.

**Provenance: an A57 bug, and a specific kind.**  The probe ran with `--m 5` *before*
`alivewitness.py` gained its `unkillable = bool(m >= budget)` guard, while the claim f-string
still hard-coded the words "= budget".  I noticed and fixed the tool the same session — but
**fixed the code and left the already-written artefact on disk**.  That is the lesson worth
keeping: *a guard added to an emitter does not retroactively correct output it has already
produced.*  When a claim-emitting tool is fixed, its existing artefacts must be re-audited or
regenerated, not assumed to inherit the fix.

**Scope: exactly one file.**  Audit of `results/alive/`:

| verdict | files | sound? |
|---|---|---|
| `NO-WITNESS` (asserts nothing) | 9 | n/a |
| `ALIVE-CERTIFIED`, m = 6 >= budget 6 | `trump5_strict.json` | **yes** — the only sound witness |
| `ALIVE-CERTIFIED`, m = 5 < budget 6 | `k5_16_m5.json` | **NO — quarantined** |

**Nothing depends on it.**  G1 kills k5_16 children by exact certificate (`verify_case.py`);
`alivewitness.py` is only ever consulted to decide whether to *stop* spending compute on a node,
and no A57 kill has ever been gated on an aliveness claim.  Verified: no A57 code path imports or
reads `results/alive/`, and no campaign record cites it.  The T7 prose already described the file
correctly as a lower bound — the error was confined to the artefact's own claim string, so there
is nothing to retract in the notes, only a pointer to add.

**A78 for the ledger:** `alive_sound` proved in Lean in core-monotone form; Python's obstacles are
full pin squares rather than certificate cores, admissibility is hard-wired at s0, and
`nofams = []` is implicit — **no soundness bug in the tool**, just the one bad artefact.


## T29 — grid sides run BOTTOM-UP: each one is a standalone record bound

Advisor/PI ordering change.  After side 1, run the remaining sides **4, 3, 2** rather than
2, 3, 4.

**Why the order matters** (it is not cosmetic).  A side's PASS rules out every packing in the
slab *below* it, and the standing lower bound is s(11) >= 3.82 (the measure certificate).  So:

| completed | rules out | new bound |
|---|---|---|
| side 1 = 3.877084 | (3.861637, 3.877084] | **none** — the gap [3.82, 3.861637] is untouched |
| side 4 = 3.833212 | (3.817940, 3.833212] | **s(11) > 3.833212** |
| then side 3 = 3.847780 | (3.832450, 3.847780] | **s(11) > 3.847780** |
| then side 2 = 3.862404 | (3.847016, 3.862404] | **s(11) > 3.862404** |

Bottom-up therefore yields a publishable record bound after each side and a hedge if the s-hat
seam runs long; top-down yields nothing until all four land.  Zero extra cost — all four sides
are needed either way.  (Each bound is conditional on the protected classes and trump5 being
killed at the same side; A82 is being extended to emit those.)

**`tree57.py --side` implemented.**  Slots are affine with beta in {0,1}, so `slots_at()` moves a
class from s0 to any side: L-anchored coordinates (1/2, 3/2, 5/2) are fixed, R-anchored ones track
s.  It refuses rather than guesses on a coordinate that is neither.  Verified at side 4:

    k5_11 at s0 : (0.5,0.5) (0.5,1.5) (0.5,3.377084) (1.5,0.5) (3.377084,0.5)
    k5_11 at s4 : (0.5,0.5) (0.5,1.5) (0.5,3.333212) (1.5,0.5) (3.333212,0.5)   [s4 - 1/2 = 3.333212]

and the cover rebuilds correctly — 969 children (11x11x8, a = 0.35112, still above a_min) against
1153 at s0 (12x12x8, a = 0.35660), the zone shrinking with s.  **Cross-validation:** the pinguard
census at side 4 computed through `tree57.build_children` gives 273 contradictory / 695 ok,
matching `grid.py`'s independent C-check for that side exactly.

**Queue order confirmed** in `scaleup.ps1`: 46 entries, `G1 -> G4 -> G3 -> G2`, each carrying its
own `--side`; `launch.ps1` gained `-Side`.  Side 1 shard 0/6 of each stratum stays hand-launched
(it is deliberately not in the queue).

**Warm-start folding across sides is kept, and is sound.**  `warm57.merged_warm` globs by class
name, not by side, so columns generated at s0 seed the LPs at 3.833212.  That is a completeness
choice and never a soundness one: atoms are only *candidate* support points for the measure, and
a badly placed candidate can only make the LP worse, never make a certificate wrong — the arbiter
is `verify_case.py` on the emitted measure at that side.  Logic kills do NOT carry across sides
automatically; they are recomputed per side by the C-check (T23), which is why the free counts
differ side to side (331/336/264/273 for k5_11).


---

## FROZEN VERIFIER v2 -- NO-families in the 4-D parametric verifier (A117, 2026-09-06)

`attempts/A96-a57-parametric/code/verify_param_v2.py`, sha256
`153029baddfcb77a2fa5049fc29c4ed8042dc847262e3ecefd5636c77fce1806`.  A NEW file: the frozen v1
(`verify_param.py`, sha256 `0c58485c1a662453188af5b0aaf42099cf41c15f82a6647404598a44e8a505ec`) is
UNCHANGED and was hashed before and after.  Full note:
`attempts/A117-verifier-v2/notes/frozen_verifier_v2.md`.

**What v2 adds.**  One discharge rule (N).  A NO-family is the hypothesis "no square of the packing
has its pose in the zone `Z(s) x T`", `Z(s)` a rectangle whose four edges are affine in `s` and `T`
a finite list of closed rational `t`-intervals.  A PASS now certifies the covering inequality for
every admissible `Q` that neither meets a core nor lies in a NO-family -- EXACTLY the clause the
frozen fixed-side `verify_case.py` (sha256 `521cb01f...`) has discharged since A13, with `s` ranging
over a slab.  On an s-cell the zone is taken at its WORST CASE, the intersection over the cell (each
edge is affine, so its extremes are at the endpoints): the shrunken zone exempts LESS than the true
zone at any single side, never more.  No new geometry enters the TCB -- rule (N) is a containment of
axis-aligned rational intervals, no `imul4`, no trigonometry.

**Equivalence with v1: 30/30 byte-identical** -- verdict AND every statistic v1 reports, on 30
existing certificates spanning both classes, A57 sides G1 and L1, levels 1-3, PASS and FAIL, A96's
resolver cells, A100's protected classes, A99's level-3 k0 nodes and A57/A95/A61's own certificates
(`attempts/A117-verifier-v2/results/equivalence.json`).  Regression surface is nil by construction:
v1 RAISES on a NO-family, so no certificate emitted before A117 contains one.

**Lean.**  `lean/PackingCertMathlib/PackingCertMathlib/ParamNoFam.lean`: `nofamExemptIV_sound` is
PROVED, parallel to `CaseHyp.nofamExempt_sound`, with the one new inequality being "an affine
function on a cell lies between its endpoint values"; `exemptPN_nil` is the Lean form of the
equivalence claim.  Axioms: `propext / Classical.choice / Quot.sound` only.  `lake build` clean.

**Measured cost, against the projection.**  A112's `verify_param_nofams.md` inferred a 4x cut of the
NO-side certification wall from A95's `0.062`-of-four-sides measurement on a level-1 A57 leaf.  That
does NOT hold on the NO-side corpus: over 48 re-verified NO certificates the window pass costs about
**10x the four fixed-side runs it replaces**, and 32 of 48 do not finish inside a 240 s cap (16
window PASSes, 0 fixed-side PASS turning into a window FAIL).  A NO certificate is tiny at a fixed
side because the NO-family exempts most of the container outright, while the 4-D pass must still
resolve the whole `s`-slab.  **v2 buys window-VALIDITY, not wall.**

**Still s0-only: the YES side.**  A branch box enters the YES child's certificate as a CORE, and
A96's `core_affine` refuses a branch-box coordinate -- it is neither a slot nor a `Q_dy` cover
coordinate (3 of 77 NO-side certificates are refused for exactly this reason).  Until a YES-core
anchoring exists, no (YES, NO) region-tree pair can be claimed window-valid.

**THE FROZEN VERIFIER IS DETERMINISTIC; THE EMISSION IS NOT.**  `certify.py --loop_cols` re-solves
the node LP under a time limit before emitting, so a certificate's atom set is wall-clock dependent.
Reproduce a kill by REPLAYING its certificate, never by re-emitting it.

## T5‴ [M] — the PIN-CLIP: shrink the centre box, not just the tilt bin (A131, 2026-09-07, MEASURED, NOT DEPLOYED)

`attempts/A131-pin-clip/{code/pinclip.py, notes/measurement.md, notes/deploy.md}`. Recorded here
as A96 recorded T5″, and by the same rule: nothing in A57 is edited, the clipper lives in A131.

**The rule.** T5″ kills a tilt sub-interval when the WHOLE centre box lies inside ONE pin's
octagon for every tilt in it. Applied POINTWISE instead of box-wise, the same geometry shrinks the
box:

> For pin `i` and a tilt sub-bin, let `D_i` be the set of centres `c` at which the unit square
> `Q(c, θ)` meets the interior of the pin's guaranteed core `K_i` at EVERY `θ` in the sub-bin.
> A centre in `⋃_i D_i` admits no tilt in the sub-bin, so it carries no packing under the node's
> hypothesis and may be discarded. The child carries (clipped centre box, tilt sub-bin) — the same
> object T5″ produces, with the centre box narrowed too.

Sound for exactly T5's reason, and with exactly T5's one exception: the discarded square must not
BE the pin, so **`pinguard.classify`'s `parent` case must be excluded first**. `pinclip.clip_node`
carries its own `realizes_pin` guard and refuses such a node; A57's interior census has zero parent
boxes, the protected tier will not.

**The intersection over tilts is EXACT, and rational.** Writing `a = a_P = 1/2 − δ`,
`w = cos θ + sin θ` (both non-negative on [0, 90]), the four separating axes fail simultaneously iff

    |d_x| < w/2 + a,  |d_y| < w/2 + a,  |d·u| < 1/2 + a w,  |d·v| < 1/2 + a w

and each of the last two splits into two branches that are SINGLE SINUSOIDS in θ:

    (±d_x − a) cos θ + (±d_y − a) sin θ < 1/2        (u-axis)
    (±d_y − a) cos θ + (∓d_x − a) sin θ < 1/2        (v-axis)

whose maximum over a sub-bin is at an endpoint or at the interior critical point (value
`√(P²+Q²)`, compared as `P²+Q² < 1/4`); the two axis-aligned tests use `w_min`, which on [0, 90]
is at an endpoint. Carrying tilts as `t = tan(θ/2)` — how the cover is built, T2 above — makes
`cos θ` and `sin θ` exact rationals, so the whole decision is exact Fraction arithmetic with **no
epsilon**, unlike T5′ (`TIGHT_EPS`) and T5″ (`MARGIN`). This matters: the conservative
sub-bin-worst-case form (trim57's envelope: `A`, `B` at `w_min` against `max |d·n|`) fails to empty
**34 of the 674** boxes the tree already kills by "core meets pin core"; the exact form empties
**674 of 674**.

**Controls executed.**
* 674/674 existing `KILL-BY-LOGIC (core meets pin core)` boxes clip to EMPTY at `nsub = 1`.
* Sampled, 12 nodes at `nsub = 8`, quoted per the SAMPLED CHECKS rule: discarded region
  **480 000 drawn → 287 017 tested → 0 hits** (per-node tested 22 319 – 40 000, so each node
  relied on clears 10⁴ on its own); kept region 480 000 → 415 075 → 352 898 feasible (85 %).
* 99 991 stored LP support columns over 1 745 solved nodes are pin-free at their own tilt up to
  **max depth 2.0000·10⁻³ = `caselp.EPS_CORE` exactly, 0 beyond it**. (`lpbox` stores row tilts in
  RADIANS; reading them as degrees manufactures 31 316 false violations.)

**Yield, on the 1 744 open boxes of the current corpus** (2 418 rows = A96's 2 222 grown by A123's
296; T5″ recomputed here empties exactly A96's 159 on A96's frozen 1 604, so the corpus
reconstruction is right):

| nsub | EMPTIED | touched, alive | untouched | mean kept | free levels (½ log₂), touched: med / mean |
|---|---|---|---|---|---|
| 1 | 179 (10.26 %) | 349 (20.0 %) | 1216 | 0.780 | 0.63 / 1.09 |
| 8 | 180 (10.32 %) | 455 (26.1 %) | 1109 | 0.747 | 0.71 / 1.26 |

By level at `nsub = 8`: L1 68/1266 (5.4 %) emptied, L2 90/425 (21.2 %), L3 10/39 (25.6 %),
**L4 12/14 (85.7 %)** — the same steep rise with depth as T5′, and the two L4 survivors keep 1 % of
their area. By class: k5_11 13.5 % emptied vs k5_16 6.6 %, because k5_11 pins the interior-adjacent
slot `(1.5, 0.5)` where k5_16 pins the far corner `(3.377084, 3.377084)`.

**Relation to T5″: strict domination.** T5″ empties 159 open boxes and touches 166; the pin-clip
empties **all 159 plus 21 more** (17 at L1, 4 at L2) and touches 455. Refining the sub-bin buys
touch, not kills (179 → 180 empties from `nsub` 1 → 8, 349 → 455 touched), because the exact
intersection is already maximal against a single pin over the whole bin. The two are complementary
and both should run — T5″ narrows the tilt bin, which the clip does not.

**Schedule (assumption stated, not measured).** If the LP's kill rate on a clipped box equals the
tree's rate at the corresponding smaller level, the §B per-level logic-kill share (29 % → 60 %)
gives a total logic-kill gain of 12.10 % (`nsub` 1) / 12.96 % (`nsub` 8) of open nodes, of which
only **1.20 % is new outright killing over deployed T5′+T5″** plus ~2.6 % of modelled promotion
— ≈ 50 CPU-h, ≈ 0.4 wall-days of the A57 row's 11–13. The larger prize, if it is real, is the same
one T5″ turned out to hold: LP tractability on the 26 % of nodes that are narrowed, realised
through the 900 s re-check rather than at emission.

**In vitro: does narrowing the box move the LP, or only the columns?  BOTH.**  Ten nodes (Y0036's
four depth-2 children plus six more with a kept fraction < 0.5, mixed levels) re-solved on the
clipped box over their OWN tilt bin, two-stage 240 s / 900 s, kills claimed only by replaying a
certificate through the frozen verifier; 2.85 CPU-h, A57's PAUSE left in place (A124's scoped
sentinel).  **Five of ten go from eta ~ 0 (tau pinned at the budget) to eta = -0.5 or -1.0**, and
**two carry a certificate**: `k5_11_interior_Y0036_D02` (L2, eta -1.0, PASS in 11.2 s) and
`k5_11_interior_Y0186_D00_D00` (L3, eta -0.5, PASS in 219 s), both previously ALIVE.  The other
three decisive ones FAIL certification with **real holes** (D03: 5 holes at depth 56, 0 tight) --
the ordinary FAIL -> resolver path, not a refutation.  On the remaining five the clip moves only
the COLUMNS, and hard: support 107 -> 5 (`Y0036_D07`), 1041 -> 5 (`Y1128`), 82 -> 16 (`Y0996`);
`k5_16_interior_Y0674` converges at minmass 1 on a box 92% smaller and stays alive at eta -2.5e-13.
**Which of the two happens is NOT predicted by how much is clipped** -- the five decisive nodes keep
0.09-0.42 of their area and the five inert ones keep 0.08-0.42.  Caveat on the count: this protocol
certifies only at eta <= -1e-3, whereas `recheck96` records a "kill" as tau < budget at eta as small
as -1.4e-14 and never runs `certify.py`, so its 11/23 and 27/63 are LP verdicts, not verified
certificates, and are not comparable with the 2 of 10 here.  Details:
`attempts/A131-pin-clip/notes/lp_effect.md`.

**Deployment (not done).** After T5″, before the LP; persist `clip_from`, `clip_kept`, `clip_nsub`,
`clip_pins`, `clip_delta` on the emitted record — the T5″ ledger gap of PAUSED.md v2 §6 must not be
repeated. Frozen verifiers unchanged: a clipped child is an ordinary smaller box. Lean shape: a
T5-type logic leaf carrying a tilt range and a centre sub-box, decidable over ℚ, needing none of
A117's Taylor/π machinery because `t = tan(θ/2)` keeps the trigonometry rational.

**n-general.** The pin-clip is the class-pin analogue of the container clip: the container clip
discards centres at which the square leaves `[0,s]²` at every admissible tilt, the pin-clip
discards centres at which it hits a fixed occupied obstacle at every admissible tilt. The obstacle
need only be a set contained in every admissible pose, so the rule applies verbatim to every
conditioning tree in the protected tier, to trump5's residual tree, and — with `a_P` replaced by
the other box's core half-side — to a second conditioned square, which is budget.md §D item 1's
box-vs-forced-neighbour kill.

## T5⁗ [M] — the POLYGON core (A132, 2026-09-07; measured, not deployed)

**The kill certificate is unchanged, again.** T5's Lean form `core_meet_same_square` takes two
arbitrary SETS `K ⊆ int Q_i`, `K' ⊆ int Q_j` and concludes `i = j` — nothing in it is about
squares. T5′ grew the half-side of the square the rule is applied to; T5⁗ drops squareness
altogether and applies the rule to the largest sound set there is:

    K′(B) = ⋂ over (c, θ) ∈ B of Q(c, θ),

the intersection of the unit square over the whole parameter box. It is convex; it contains
`K(a_old)` and `K(a_tight)` by definition (both are squares lying in that intersection); for a
narrow tilt bin it is nearly the whole tilted square. Measured over the 506 alive nodes:
`area(K′)/area(K(a))` median **1.225**, up to 1.53, and the gain is largest where the tilt bin is
widest, i.e. at level 1 where the axis core is weakest.

**Certification is by VERTEX, exactly, in rationals.** `K′` is convex, so if every vertex `v` of a
candidate polygon lies in `Q(c,θ)` for all `(c,θ) ∈ B` then the hull is inside `K′` — *however the
polygon was found*. With `d = v − c` and `t = tan(θ/2)`, that is

    for each of the 4 corners c of the centre rectangle, and (u,w) = (dx,dy) and (dy,−dx):
      (1/2 + u)t² − 2wt + (1/2 − u) ≥ 0   and   (1/2 − u)t² + 2wt + (1/2 + u) ≥ 0   on [t0,t1]

— two rational quadratics, decided exactly by their endpoints plus `4AC − B² ≥ 0` when `A > 0` and
the stationary point is interior. `t0 = t_lo(θ0)`, `t1 = t_hi(θ1)` are the corpus's own
outward-rounded bounds, so the certified tilt range CONTAINS the box's. Cost 0.07 s per box.
`attempts/A132-polygon-core/code/polycore.py`; the clipping / shrink / hull that *finds* the
polygon is unaudited, the vertex test is the proof.

**And for the logic kill Lean never sees a polygon.** The `Nonempty` hypothesis needs one point in
both cores. That point is rational, and the same vertex test certifies it against BOTH boxes; take
`K = K' = {w}` in `core_meet_same_square` and the hull, the convexity lemma and the polygon–polygon
SAT all vanish. The kill certificate is **one rational point and two vertex checks**; the polygon is
only the search device that finds the point. One new Lean obligation (`checkVertexInPBox_sound`),
≈1 day. Witness found and exactly certified for **64/64** firing nodes.

**Why no kill can be lost.** `K(a_tight)` is a square contained in every pose of `B`, hence
contained in `K′(B)`: every T5/T5′ kill is a T5⁗ kill. Control executed, not merely argued:
**854/854** recorded `KILL-BY-LOGIC` boxes still killed, 0 lost, 0 build errors
(`attempts/A132-polygon-core/results/control132.json`).

**Yield on the alive population** (506 nodes = A57's 414 ALIVE + A60's 92 refused): fires on **64**,
of which the deployed T5′ already kills 27 (20 of them recorded in
`results/superseded_by_tight_core.jsonl`; the other **7 are A60 nodes, where T5′ has never been
applied at all**) — so **37 new**. Against T5″: 28 of the 34 new A57 kills are boxes whose T5″
surviving bin is empty in `trim96.json`, 6 are not, and 29 trim96-empties are not T5⁗ kills. The two
rules are different tests (T5″ subdivides the tilt bin, T5⁗ enlarges the core) and a deployment
should run both.

**It also moves the LP — which the file predicted it would not.** A placement meeting `int K′(B)`
overlaps every pose of `B`, i.e. it is *dominated* in A96's sense, so `K′`-pruning of the
CONDITIONED box is a strict special case of the all-poses row filter A96 measured at zero kills
(`τ_C − τ_B` median 3.3e−13). But the polygon core also upgrades the **PIN** cores, which that
filter never covered: for a pin box `K′(P)` is the axis square of half-side 0.49293 against
`K(a) = 0.48999…`, and pinned squares nearly touch. In vitro (10 alive nodes, both arms, identical
warm start and oracle, `recheck96`'s node path), **three pairs converged in both arms and all three
are LP-dead under the polygon core and alive under `K(a)`**: `Y0871` 5.000 → 4.000, `Y1038`
5.000 → 4.500, `k5_16 Y0281_D03` 5.000 → 4.000. Re-running with the polygon core on the conditioned
box ONLY, `Y1038` converges back to 5.000 — **that kill lives entirely in the pin cores.** These are
"LP-dead under polygon core, CERTIFICATE PENDING": the frozen verifier knows only `K(a)`, and the v3
clause that would close them is specified in `attempts/A132-polygon-core/notes/spec.md`. Caveat of
record: three converged pairs on nodes selected for the largest offending weight is not a rate.
