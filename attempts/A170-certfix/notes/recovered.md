# A170 §2 — the RE-CERTIFICATION: what carrying the exact cores actually recovers

Driver `code/recert170.py`, wrapper `code/certwrap170.py`, arbiter the FROZEN `verify_case.py`
(`attempts/A143-corner-first-k0/code/verify_case.py`, sha256
`521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`, asserted before every run; the
five copies of that file across the repo were checked byte-identical, and none was touched). Two modes:

* **`patch`** — take an existing certificate on disk, enlarge its cores to `exactcore.exact_a`, write
  the patched copy under `attempts/A170-certfix/certs/`, verify. Nothing is written outside A170.
* **`k0`** — take A115's **stored** LP record (`results/nodes/<nid>.t{4,5}.lp.json`, which keeps
  `atoms_all` / `rows_all` / `hyp` / `tau` / `budget`), re-emit through
  `certwrap170.make_certificate_exact` with **no re-solve**, verify. Scale rule is A115's own
  (`t4.certify_plain`): `scale = max(1.005, min(1.4, (budget − 0.005)/tau − 0.002))`.

409 records, **2.35 CPU-h of verifier**, zero LPs solved. Results `results/recert170_*.jsonl`, summary
`results/summary170.json`, independent checks `results/check170.json`.

## Headline

| | n |
|---|---|
| certificates re-certified | 409 |
| **recovered PASS** | **59** |
| NO-CHANGE (cores were already exact — nothing to repair) | 118 |
| still FAIL | 222 |
| still FAIL on `total ≥ budget` (no core can repair) | 9 |
| TIMEOUT at 900 s | 1 |

All **59 of 59** recovered PASSes clear the 100 % independent check (below).

## The recovered PASSes, by lane and class

### (a) Genuine victims of the reversion — `ExactHyp` LP, stock cores emitted (25 certificates, 8 nodes)

| lane | node | was | cores enlarged | max `a_exact/a_carried` |
|---|---|---|---|---|
| **A165** | `l1_104_spread_spread00` | FAIL | 5 | 1.0950 |
| **A165** | `l1_104_spread_spread02` | FAIL | 5 | 1.0239 |
| **A165** | `l1_104_spread_spread03` | FAIL | 5 | 1.0950 |
| A150 | `q_402_x4` (+ `_recert`) | FAIL | 4 | 1.0419 |
| A150 | `q_rand_301_000_321_533` (+ `_recert`) | FAIL | 4 | 1.0644 |
| A150 | `r_055_035_044_453` | FAIL | 4 | 1.1523 |
| A166 | `l2_p65_101_b8_005_512` + its 15-certificate scale × denominator ladder | FAIL | 3 | 1.1523 |
| A166 | `l2_p65_101_b8_015_504` | FAIL | 3 | 1.1523 |

**Distinct NEW nodes: 3** — all three of A165's `l1_104` spread tuples. A150's 3 and A166's 2 were
already recovered inside A166; A170 re-derives them through a **separately written** emission path
(`certwrap170`, not `certfix166`/`certaudit166`) and agrees 22/22, which is the cross-check A166 asked
for.

**What the A165 recovery says.** `attempts/A165-cascade-l1_104/notes/cascade.md` §C7 records four
random depth-8 spread tuples on the `l1_104` k0 cell, all four LP-dead at `τ = 5.000000`,
`η = −1.0000`, converged, and reports **1 PASS, 3 cert-FAIL**, adding: *"The three FAILs are the lab's
standard 'LP-dead, certificate pending' — they need the A13/A14 separation loop with more rounds, not a
different core."* That reading is exactly backwards: they needed the cores they were **solved** with.
The spread leaf now certifies **4 of 4** tuples tested. `lp5165.py` imports A150's driver
(`lp5165.py:49`) and states the LP runs on A135's exact cores (`lp5165.py:3`), which is why these three
were victims — the same sentence A166 had to correct in A150 §5.

### (b) A free UPGRADE on stock-core lanes: A59's vacuity ladder (34 certificates)

`A59-trump-residual`'s zero-atom **vacuity** certificates (`total = 0 < budget = 1`, 10 cores, one
NO-family: *no admissible square exists at all outside the cores*) are the residual-rigidity ladder
around Trump's packing, indexed by the box half-width `hw` and the exemption parameter `a`. Their LP was
genuinely stock-cored, so this is not a repair — it is the enlargement paying on its own. **33 A59 rungs
plus A60's `selftest_vac_a0.00448242`** flip FAIL → PASS. What moves is the *minimum* `a` a rung needs:

| kind | scope | `hw` | `a_min` PASS before | after | ratio |
|---|---|---|---|---|---|
| `rb` | box | 0.0005 | 0.002283 | **0.002139** | 1.067× |
| `rb` | box | 0.001 | 0.004551 | **0.004141** | 1.099× |
| `rb` | box | 0.002 | 0.009062 | **0.007969** | 1.137× |
| `rb` | box | 0.0037 | 0.016852 | **0.016650** | 1.012× |
| `rb` | box | 0.005 | 0.022773 | **0.022500** | 1.012× |
| `rb` | box | 0.01 | 0.045547 | **0.045000** | 1.012× |
| `rb` | box | 0.02 | 0.118438 | **0.107500** | 1.102× |
| `rb` | box | 0.05 | none | none | — |
| `rk` | fulltheta | 0.001 | 0.003320 | **0.003047** | 1.090× |
| `rk` | fulltheta | 0.002 | 0.006602 | **0.005781** | 1.142× |
| `rk` | fulltheta | 0.0037 | 0.012184 | **0.011273** | 1.081× |
| `rk` | fulltheta | 0.005 | 0.016465 | **0.015234** | 1.081× |
| `rk` | fulltheta | 0.01 | 0.032519 | **0.030469** | 1.067× |
| `rk` | fulltheta | 0.02 | 0.074883 | **0.067500** | 1.109× |
| `rk` | fulltheta | 0.05 | 0.189258 | 0.189258 | 1.000× |

**The certified `hw` envelope does NOT move** (max-PASS `a` per rung is unchanged; `rb hw = 0.05` still
has no PASS at any `a`), so A59's headline radius is unaltered. What is bought is **8–14 % of the
exemption parameter at every rung** — the ladder is cheaper, not longer. Mechanically: the five exact
pin cores are point boxes (`x0 == x1`, `th0 == th1 == 0`) whose stock `a = 16383999967232/32768001953125`
rises to `16777215/33554432` (one ULP of the `2^-25` grid below `1/2`, ratio 1.000000002), and the five
tilted `hw`-boxes' cores rise by 0.12 %–1.7 %; that last sliver is what covers the remaining
placements. Every patched core is `< 1/2` (checked).

## The 100 % independent check — 59 of 59

`code/check170.py`, three checks sharing no code with the bisection that chose the half-side:

* **C1 core containment, re-derived from scratch.** The four corners of every written core square
  `(kx, ky, tm, a)` tested DIRECTLY with A132's `polycore.vertex_ok(vx, vy, box, t_lo(th0), t_hi(th1))`
  — the exact rational quadratics in `t = tan(θ/2)` — on the **written** rationals, plus A156's
  tripwire `0 < a < 1/2`. **OK on every core of every certificate.**
* **C2 the measure, exactly.** `sum(weights)` recomputed in `Fraction` equals the written `total`;
  `total < budget`; every weight `> 0`; atom count matches; `budget == 11 − #cores`. **OK.**
* **C3 a deeper frozen replay.** The same byte-identical `verify_case.py` re-run at bisection depth
  **64** (against 56 in the recert pass) with a different `--jobs`, so no PASS is an artefact of the
  split schedule. **PASS 59/59.**

## The negative results, which are most of the work

| population | n | outcome |
|---|---|---|
| A137 / A149-a57 / A156 / A145 FAILing certificates | 118 | **NO-CHANGE 118/118** — the cores were already exact; the reversion is not their failure mode and their FAILs are real |
| A149-a60 (`__exH`) FAILing certificates | 8 (+1 TIMEOUT) | FAIL — the pin cores enlarge by < 0.01 %, far too little to close a hole |
| A57's own `certs/` + `certs/epsgeo` FAILs | 7 | FAIL (2 on `total ≥ budget`) |
| A60 own campaign FAILs | 40 | FAIL (1 vacuity self-test recovered, counted above) |
| A59 non-vacuity FAILs | 32 | FAIL |
| A61 / A82 / A54 / A55 / A131 FAILs | 11 | FAIL |
| **k0 pool** — every `kill-candidate (cert FAIL)` record of `cells140.open_pool` (**128** of the 166 open records), re-emitted from A115's stored measure with exact cores | **128** | **0 PASS.** 119 fail with 6–52 genuine holes, 9 on `total ≥ budget`. Cores enlarge by 0.6 %–11.8 % (min 1.0062, median 1.0326, max 1.1179) |

**Why the k0 pool yields nothing, as a property of the population.** All 128 are single-box hypotheses at
`budget = 10` whose LP did **not** converge (`converged: false, dead_unconverged: true`) with
`τ ≈ 9.9767–9.9786` — 0.022 of slack — so the rounded-up measure lands at `total ≈ 9.977` and a 3 % wider
core does not reach placements whose `exact_mass = 0`. A166's hope that "127 of the 166 open k0 records
are candidates for immediate certification at zero LP cost **if any of those were emitted through an
exact-core path**" is answered: **none of them was.** A115's `t4`/`t5` lane
(`caselp92.make_certificate`, `attempts/A115-k0-corner-rows/code/t5.py:36`) carries the same
`Hyp.from_json` reversion, but its LP ran on the stock cores too, so its certificate was consistent with
its LP. These are not spurious FAILs; they need LP work, not a repaired emission path.

## Collector check (`docs/shadows/status_gallery.py --dry-run`)

| | before | after A170's `.certify.json` sidecars |
|---|---|---|
| kill records scanned | 5,818 | **5,831** (+13) |
| kills recognised | 5,332 | **5,344** (+12) |
| refused for an unresolved tree tag | 107 | 107 |
| clipkill certificates | 342 | 342 |
| `k0v4` pages | 11 ALIVE / 0 DEAD | **11 ALIVE / 0 DEAD** |
| `a57v4` pages | 53 ALIVE / 7 DEAD | **53 ALIVE / 7 DEAD** |

**Distinct-new gallery pages killed: 0.** The 12 kills the collector newly recognises are leaf-tuple
hypotheses (A150's four-corner products, A165's spread tuples), A166 sub-tree nodes and A59/A60 vacuity
rungs — none of them is a gallery node, and the recoveries do not move `l1_104` (a spread tuple is one
cell of a cover, not the cell) or any A57 page. The board is unchanged and no page was moved.

## Byproduct worth queueing separately (not A170's fix)

Several FAILs report **0 HOLES** and only "undecided at this depth" — e.g.
`A149-a57-reprice/c0_Y0269__exH`, `c0_Y0335__exH`, `A60-trump5-campaign/c0_Y0317_epsgeo0.002`,
`c0_Y0982`. Those are depth-limited, not core-limited: a depth-64–72 replay (which `check170.py` shows
costs 2–40 s at this certificate size) may close them at zero LP cost. A different lever from A170's,
recorded rather than spent.

## Coverage note

The `patch` sweep over A137/A156/A149's certificate directories was stopped at 126 of 142 targets: the
16 remaining are `attempts/A149-a57-reprice/certs/a60/*__exH.json` certificates that each hit the 900 s
verifier timeout, and the in-scope conclusion (**NO-CHANGE on every already-exact certificate**) was
already complete on 118 of them. The driver is resumable — re-running the same command skips every id
already in the jsonl.
