# A60 — P0 selftests and the G-A59-10 falsifier verdict

Run 2026-09-01.  Everything at s0 = 969271/250000, h = 3.7e-3 (A36 basin radius, sup-norm in
(cx, cy, θ_rad)), HW_TARGET = h/4.55 = 8.13e-4 (the G-A59-9 annulus closure).
All numbers in this note are **exact-arithmetic** (pinguard + Lemma A57-3 alive gate); no LP
verdict is used as an arbiter anywhere (A54 S0).

---

## 0. Verdict

**The falsifier PASSES — but only after correcting the conditioning radius A59's pilot used.**
Read literally, A59's parameter choice (condition each located square in a *basin-radius*
box, hw = h = 3.7e-3) makes the depth-1 and depth-2 residue ladders **diverge**: the residue
grows 18 → 620 boxes over 30 levels, its max containment stalls at 5.7e-3 = 1.55·h, and no level
ever reaches "every residue box inside the A36 basin slice".  On that reading the 1e4–1e5
estimate is dead.

Conditioning instead on the boxes the previous ladder **actually produces** (radius 4.45e-4,
which is what P3/P5 already require the ladder to reach), the depth-1 and depth-2 ladders
terminate exactly like depth 0's: **level 24, 15–35 residue boxes, all inside the basin.**
The extrapolation holds.  Two engine deltas fall out and are banked below.

---

## 1. P0 engine fold-ins (G-A59-11) and their selftests

`code/tree60.py` folds both A59 recommendations into the tree driver:

* **(i) the alive gate.**  `alive59.k(N)` (exact rational, ~1 ms) runs on every child before any
  LP.  `k ≥ budget` ⇒ Lemma A57-3 makes the node provably uncertifiable ⇒ record ALIVE, never
  launch the LP.  This is an efficiency gate on the KILL side only; it can never turn a non-kill
  into a kill.
* **(ii) the zero-atom vacuity arbiter** (`vac59`) for every budget-1 node: no LP, no
  EPS_CORE/EPS_ZONE shell (their 2e-3 floor is the same scale as h).

`code/selftest60.py` — **6/6 groups PASS, 0 failed checks**:

| test | what it reproduces | result |
|---|---|---|
| T1 | A59 `m2_killability_census`: cover 1152 / contradictory 344 / ok 808 / unkillable 41 / attemptable 767 | exact match |
| T2 | A59 `m2_branching_by_depth` at j = 1…4 (1075/59/18, 1118/27/7, 1150/2/0, 1152/0/0) | exact match |
| T3 | canary: the 3 cover boxes holding a Trump free placement (sq7, sq8, sq9) are alive-gated **unkillable** — the driver never launches an LP on them and never certifies them | PASS |
| T4 | gate soundness: on every node A59 actually certified (7 `conf_j*` PASSes + the M3 interior NO child) the gate reports k < budget — **the gate never blocks a kill that exists**; k reproduced exactly on all 8 `conf_ladder` rows; root k = 6 = budget | PASS |
| T5 | vacuity arbiter end-to-end: the pilot's r_kill crossover at hw = 1e-3 — a = 0.00455078 **PASS** (1.2 s), a = 0.00448242 **FAIL** (0.8 s), from fresh zero-atom certificates | PASS |
| T6 | `classify_at` degenerate cases: `shared` and `contradictory` | PASS |

### G-A60-1 — a soundness delta in A59's branching census

A59's level-1 census called `pinguard.classify` with the conditioned cores appended to the PIN
list, so a cover box whose core meets a conditioned core was booked **contradictory** — a free
logic kill — without checking whether **one** square could realise both boxes.  For 1–3 boxes per
conditioning level that is wrong, and they are exactly the boxes that **contain the conditioned
Trump square**: the chain boxes.  `classify_at` separates them as `shared`
(UNSOUND-AT-REDUCED-BUDGET): never certified, carried at the parent budget, refined until the box
lies inside the A36 basin of the square it may share, at which point it is a (D)-chain node.
Counts reproduce A59 exactly once `shared` is added back to `contradictory` (T2), so no A59
measurement changes — but 1–3 leaves per level move from "killed" to "discharged", which is the
difference between a false leaf and a true one.

---

## 2. The falsifier, as A59 parameterised it — DIVERGES

Conditioning square 1 in a **basin-radius** box (hw = h) at Trump's placement, then running the
residue ladder for the next square (`ladder_scan`, exact):

| cond | L0 | L12 | L18 | L24 | L30 | max containment at L30 | inside basin |
|---|---|---|---|---|---|---|---|
| — (j = 0) | 41 | 26 | 28 | **28** | — | 2.01e-3 | **28/28, terminates at L24** |
| sq7 @ h | 18 | 26 | 58 | 172 | **620** | 5.72e-3 = 1.55·h | 407/620, no termination |
| sq7,sq8 @ h | 7 | 9 | 24 | 70 | **244** | 5.68e-3 | 159/244, no termination |

**Diagnosis (exact).**  The stall is *not* an obstruction in the geometry.  A grid census of the
limit (box radius → 0) over the whole shell ‖offset‖∞ ≤ 8e-3 around sq8 with sq7 conditioned
returns **contradictory 4195, attemptable 907, unkillable 1** — the single unkillable limit point
is Trump's sq8 placement itself.  So the residue does contract to Trump; the divergence is a
*rate* effect.  The residue is dominated by boxes straddling the razor-thin surface
{core(B) just touches core(C_sq7)} — razor-thin because Trump's scaled six are in near-contact
(min pairwise gap 1.0574e-7).  A box's core has half-side a = (½ − hd)/(1 + Δt) < ½, so whether it
reaches a second witness flips with the box's own size; with the conditioning core as *loose* as
hw = h (a ≈ 0.4927) the surface sits ~5.7e-3 from sq8 and the ladder chases it at ~2 % per level
while the box count grows like r⁻¹.

**Confirmation that the point is the conditioning radius, not the depth** (same j = 1 ladder,
conditioning core radius varied):

| cond radius | terminal level | residue boxes | max containment | all inside basin | cumulative kill queue |
|---|---|---|---|---|---|
| 3.70e-3 (= h, A59's choice) | — (>30) | 620 and rising | 5.72e-3 | **no** | 1720 and rising |
| 1.50e-3 | 24 | 81 | 2.99e-3 | yes | 289 |
| 8.13e-4 (= HW_TARGET) | 24 | 50 | 2.44e-3 | yes | 221 |
| 4.00e-4 | 24 | 35 | 2.44e-3 | yes | 183 |
| 1.00e-4 | 24 | 24 | 2.44e-3 | yes | 155 |

---

## 3. The falsifier, as the program actually runs — PASSES

The program does not condition at the basin radius: P3/P5 condition on the **located boxes the
previous ladder produced**.  The j = 0 ladder terminates at level 24 with **28 located boxes**
(radius 4.445e-4, containment ≤ 2.010e-3), split 9 / 9 / 10 over the Trump squares sq7 / sq8 /
sq9 they hug.  Conditioning on those boxes:

| conditioning | zone cover free | att | unk | ladder terminal level | residue | all inside basin | ladder kill queue |
|---|---|---|---|---|---|---|---|
| located sq7 box (2 samples) | 1077 | 58 | 17 | 24 | 34–35 | **yes** | 193–205 |
| located sq8 box (2 samples) | 773 | 348 | 31 | 24 | 23–27 | **yes** | 306–317 |
| located sq9 box (2 samples) | 897 | 220–221 | 34 | 24 | 20–23 | **yes** | 305–310 |
| located sq7 + located sq8 | 1118 | 27 | 7 | 24 | 20 | **yes** | 129 |
| located sq7 + located sq9 | 1120 | 22 | 10 | 24 | 15 | **yes** | 75 |
| any three located boxes | 1150 | **2** | **0** | — (residue empty) | — | — | — |

**The interior-zone tree closes at conditioning depth 3.**  At j = 3 the whole interior cover is
1150 free logic kills + 2 attemptable + 0 unkillable, with the three `shared` boxes being exactly
the three conditioned squares: the interior zone [1.1, 2.777]² holds precisely the three located
squares and nothing else.  This is A59's measured 41 → 18 → 7 → 0 collapse, reproduced with
honest conditioning boxes (17–34 → 7–10 → 0).

### The branch-merging lever (new, and worth ~10× )

The 28 located boxes are a cover, so they may be replaced by the bounding box of each hug class
(a weaker hypothesis — sound).  That collapses the level-1 branching from 28 to 3:

| merged branch | n merged | radius | containment | free | att | unk | terminal level | residue | all inside | queue |
|---|---|---|---|---|---|---|---|---|---|---|
| sq7 | 9 | 1.33e-3 | 1.55e-3 | 1076 | 59 | 17 | 24 | 61 | yes | 255 |
| sq8 | 9 | 1.78e-3 | 2.01e-3 | 772 | 348 | 32 | 24 | 42 | yes | 333 |
| sq9 | 10 | 1.78e-3 | 2.01e-3 | 894 | 224 | 34 | 26 | 124 | **no** (3.79e-3) | 393 |

sq7 and sq8 merge cleanly; sq9's full merge is marginally too loose (radius 1.78e-3) and needs a
2-way partial merge.  Rule of thumb from §2's radius table: **merge only up to conditioning
radius ≤ 1.5e-3.**

---

## 4. Revised cost model for the interior triple

| block | count | budget | unit | subtotal |
|---|---|---|---|---|
| j = 0 zone cover, free logic kills | 344 | — | 0 s | 0 |
| j = 0 zone cover, exact kills | **767** | 5 | 1–290 s | ~13 CPU-h |
| j = 0 residue ladder (24 levels) | **540** | 5 | 1–290 s | ~9 CPU-h |
| level 1: 3–5 merged branches × (cover att + ladder queue) | ~2000 | 4 | measured below | |
| level 2: ~8 branches × (~25 att + ~100 queue) | ~1300 | 3 | mostly free/cheap | |
| level 3: ~16 branches × 2 att | ~32 | 2 | | |
| **interior-triple total** | **≈ 4 600 certificates** | | | **single-digit desktop-days at 3–4 processes** |

That is *better* than A59's 1e4–1e5, because the merging lever and the corrected conditioning
radius both cut branching. Without merging (28 → ~30 → ~18 full product) the same tree is
≈ 1.7e5 certificates, i.e. ~a month — so **the merge is load-bearing, not an optimisation.**

---

## 5. What this note does NOT price (raised to the PI)

**G-A60-2 — the outer three squares: the zone-cover route is STRUCTURALLY dead; use confinement.**
The (D) leaf of T5'.2 needs **six** cores inside the basin.  Every measurement in A59's pilot uses
the **interior** zone, and the interior zone contains exactly three of Trump's free squares
(sq7, sq8, sq9); the other three — sq4 (0.500, 2.533), sq6 (1.536, 3.172), sq10 (3.172, 1.936) —
live in the **side** zones.  No leg of A59 ever covered one.  A60 did
(`results/a60_sidezone_census_j3.json`), at j = 3 with the interior triple located, YES-child
budget 2:

| zone | cover | contradictory | parent | attemptable | unkillable (residue) |
|---|---|---|---|---|---|
| side_L (holds sq4) | 444 | 381 | 2 | 36 | 25 |
| side_T (holds sq6) | 444 | 351 | 0 | 66 | 27 |
| side_R (holds sq10) | 444 | 425 | 0 | **0** | 19 |
| corner_TL (empty) | 173 | 0 | 0 | 172 | 1 |
| corner_BR (empty) | 173 | 171 | 2 | 0 | 0 |

Read naively that looks cheap.  It is not: **side_R has ZERO attemptable boxes**, and its 19-box
residue *diverges* under refinement — 19 → 1780 by level 12, max containment frozen at **0.407**,
kill queue **0 at every level**.  Nothing there can ever be killed, and it is structural, not a
compute shortfall:

> With j squares conditioned, a YES child has budget 6 − j − 1 while only 6 − j Trump witnesses
> survive.  A cover box that knocks out exactly ONE survivor therefore has k = budget and is
> ALIVE-CERTIFIED unkillable (Lemma A57-3).  Conditioning removes a witness **and** a unit of
> budget, so the margin k − budget is invariant: progress needs a box whose core reaches **two**
> of Trump's squares.  In the crowded interior nearly every box does — which is exactly why the
> interior ladder terminates.  In a side zone nearly nothing does.

**The fix is the mechanism A59's P4 already prescribes from j ≥ 2 — confinement, not covering.**
Add a NO-family around Trump's placement instead of a YES core: the NO-family swallows that
witness, so k falls by one while the budget does *not* (a NO child keeps the parent budget).  That
is the margin the cover route can never buy, and it is the regime the pilot measured PASS at
j = 2, 3, 4, 5 (`conf_ladder.json`, η = −1.0, 20–95 s at j ≥ 3, knife-edge 542 s at j = 2).
`code/confine60.py` runs it on the located interior triple, and it **works — every rung**.
At j = 3 with sq7/sq8/sq9 conditioned in their located ladder boxes, the NO-family around sq10
gates as attemptable at every radius tried (k = 2 < budget 3; surviving witnesses sq4 and sq6)
and each rung carries an **exact PASS certificate** (`results/a60_confine_j3.jsonl`):

| a | k | budget | τ | η | LP s | cert s | verdict |
|---|---|---|---|---|---|---|---|
| 0.3 | 2 | 3 | 1.500000 | −1.5 | 300.1 (unconverged) | 23.3 | **PASS** |
| 0.15 | 2 | 3 | 2.000000 | −1.0 | 62.9 | 1.4 | **PASS** |
| 0.075 | 2 | 3 | 2.000000 | −1.0 | 88.2 | 1.3 | **PASS** |

Note the cost runs *backwards* from intuition: the LOOSEST NO-family is the expensive one
(300 s, and its LP never converged), the tighter ones are cheap (63–88 s LP, 1.3–1.4 s cert).
That is the opposite of the zone-cover regime and it is what makes driving the confinement ladder
down to the annulus target hw ≤ 8.13e-4 affordable — exactly the P5 shape, and consistent with the
pilot's budget-1 vacuity rung at 0.5–1.5 s.  **So the outer triple is not a wall, but it is not the cover machinery either — and
the A59 program's phrase "repeat on the next interior square" must not be read as "cover the side
zone".**

**G-A60-3 — τ\* > k at cover resolution: the new binding cost driver.**  The alive gate's
`attemptable` verdict only says the A57-3 obstruction is *absent* (k is a lower bound on τ\*,
never an upper one — A54 S0).  A59's cost model implicitly read attemptable ⇒ killed.  Measured
on trump5, it is not:

| stratum | budget | LP kills | LP-alive | cert-FAIL | kill rate |
|---|---|---|---|---|---|
| A57 k5_11 interior (calibration) | 5 | 38 | 3 | 2 | **0.88** |
| A57 k5_16 interior (calibration) | 5 | 36 | 5 | 4 | **0.80** |
| **A60 trump5 interior cover (j = 0)** | 5 | 6 | 4 | 2 | **0.50** (n = 12, running) |
| A60 trump5 ladder queue (j = 1) | 4 | 1 | 4 | 2 | **0.14** (n = 7) |
| A60 trump5 **confinement** (j = 3) | 3 | 3 | 0 | 0 | **1.00** (n = 3) |

The cover rate climbed 0.29 → 0.50 over the first dozen children as A57 T4 sibling column folding
grew the warm pool (249 → 251+ atoms); it is still well short of the shadow strata's 0.80–0.88 and
should be re-read from the scoreboard, not from this table, once the shard is deep in.

The LP converges to τ = 5.000000 = budget with a **5-atom** optimum that is *not* Trump's six —
a disjoint family the alive gate cannot see.  This is trump5-specific and expected in hindsight
(A54 S1: the hard children are the ones sitting on Trump's squares, and on *his own* stratum
every interior cover box is Trump-adjacent), so the shadow-strata calibration does not transfer.

**Consequence for the cost model.**  The resolution is the A57 T11 deepen loop, now implemented as
`tree60.phase_deepen`: an unresolved box is bisected and re-processed at the *same* budget, and
its sub-boxes have a strictly larger rational core (a → ½), which is what makes the retry bite.
A57's own depth-2 pass is the encouraging calibration: `k5_16_interior_L1_D2` killed **6 of 6**
resisters.  Budgeting ~2 deepen rounds at a ~30 % → high yield puts the j = 0 cover at ≈ 2 250 LP
kills instead of 767, i.e. **≈ 3× the §4 table, ~1.4e4 certificates for the whole tree** — still
inside A59's 1e4–1e5 band and still single-digit desktop-days, but the driver of the cost is the
deepen loop, **not** the alive gate.  The A57 T14 `--eps_geo` retry (which A59's copy of
`tree57.py` predates) is now folded into `tree60.kill` and recovers part of the cert-FAIL column.

**Unchanged and still open:** G-A59-7 (every (K) leaf is certified at s = s0 only; the window and
the low-s slab are A56's s-parametric obligation) and P1's six-class upward trap (A56, in
flight).

---

## 6. Measured per-kill costs on trump5 (first 16 solves, both phases)

| tag | budget | τ | η | LP s | cert s | verdict |
|---|---|---|---|---|---|---|
| `c0_Y0074/76/78/79` | 5 | 5.000000 | 0.0 | 18–50 | 0 | refused (LP-alive) |
| `c0_Y0072`, `c0_Y0075` | 5 | ≈5 (knife edge) | ~0 | 64, 137 | 0.3, 0.4 | FAIL(rc=3) |
| `c0_Y0077/80/81` | 5 | 4.000000 | **−1.0** | 106–175 | 3.3–19.0 | **PASS** |
| `f1_L00_0000` | 4 | 3.000000 | **−1.0** | (cached) | 1.3 | **PASS** |
| `f1_L02/10/15/19` | 4 | 4.000000 | 0.0 | 43–303 | 0 | refused (LP-alive) |
| `f1_L07_0002` | 4 | 3.666667 | −0.33 | 300 | 21.0 | FAIL(rc=3) |
| `f1_L13_0002` | 4 | 3.500000 | −0.50 | 174 | 155.2 | FAIL(rc=1) |

| `conf60_sq10_a0.3_tw` | 3 | 1.500000 | **−1.5** | 300 (unconverged) | 23.3 | **PASS** |

**The law is sharp: a node certifies iff η = τ − budget reaches −1.**  Every η ≤ −1 node PASSed
(including the confinement node at η = −1.5 whose LP never even converged); every η = 0 node was
refused; both fractional-η nodes (−0.33, −0.50) FAILed certification (rc = 3 = the A57 T11 knife
edge, rc = 1 = the A57 T14 `--eps_geo` case).  Cheap and useful as a campaign pre-filter:
**−1 < η ≤ 0 predicts a wasted certification**, so route those straight to `deepen` instead of
`certify` — the two fractional-η nodes above burnt 176 s of certifier time between them for
nothing.  (This is A56's slack gate `budget − τ0 ≥ 0.5` seen from the trump5 side, and it is
sharper here: the threshold is 1, not 0.5.)

Wall-clock per node: **LP 18–303 s** (mean ≈ 120 s at budget 5, ≈ 130 s at budget 4); **cert
1–19 s on a PASS**.  A refused node costs only its LP.  That is why the deepen loop — which turns
refusals into smaller boxes with larger rational cores — is where the campaign's compute goes.

### Operational notes banked for the campaign

* **The RAM guard is the COMMIT charge, not free physical RAM.**  A cover shard died with
  `numpy MemoryError: unable to allocate 66.6 MiB` while `FreePhysicalMemory` still read 9.1 GB —
  commit stood at **57.7 / 61.0 GB** (pagefile capped near 30 GB).  Launch heavy jobs only above
  ~6 GB of commit headroom (`notes/RESUME.md`).  Every phase is resumable, so an OOMed shard
  costs only its in-flight LP.
* `pilot59.run_child` appends its record *before* the driver merges the campaign's own fields, so
  `tree60.kill` now always appends an **enriched** record afterwards (level / k / hugs / cond /
  any eps_geo repair); the scoreboard keeps the **last** record per tag, A57's convention.
* A57 T14 (`certify.py --eps_geo`) is folded into `tree60.kill`; A59's copy of `tree57.py`
  predates it, so A59's pilot never had the repair.
