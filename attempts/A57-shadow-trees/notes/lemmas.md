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

Measured: `results/alive/k5_16_m5.json` — five pairwise-disjoint admissible squares in the
k5_16 residual, exact min gap 0.0017314…> 0, so τ*(k5_16) ≥ 5 (a lower bound; k5_16's budget is
6, so this is not yet an unkillability proof for the stratum itself).  With the interior core
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
| `rc = 1`, 0 holes, undecided | atoms on placement boundaries | `--eps_geo` row shrink (T14) | ~2 min |
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

**Experiment running:** `certify.py --eps_geo` on the k5_11 node.  The margin must be *small*
here, unlike at the child: certification needs τ·1.005 < 6, i.e. τ < 5.970, and τ is at 5.9101 —
**1.0 % of headroom**, whereas eps_geo = 0.002 raised the child's τ by 1.6 % (4.500000 →
4.571429).  So the pass uses **eps_geo = 0.0005**, and the re-solved τ is itself the verdict: if
it lands under 5.970 the certificate is worth attempting, if not the margin is unaffordable on
the direct route and the tree remains the only line.  This is the lab's closest near-miss
(A54 W3) and the first time its failure has been *diagnosed* rather than attributed to
convergence.
