# A60 composition ledger — which leaves are parametric, which are s0-fixed

Requested by the coordinator relaying A63 (`docs/proofs/closed_disjoint_bridge.md`,
`docs/proofs/theta_t_transfer.md`), 2026-09-01.  Everything here is measured from A60's own
certificate corpus (`results/a60_bridge_margins.json`), not inherited.

## 1. The headline: **0 of A60's leaves are parametric; all are s0-fixed, and s0-fixed buys nothing**

| | count |
|---|---|
| A60 PASS certificates on disk | **49** |
| certified at s = s0 = 969271/250000 | **49 (all)** |
| certified parametrically (`parametric_kill_certificate_v1`) | **0** |

A63's Corollary B′ transfers a kill certified at side s″ down to packings at side m whenever
(H′) `(s″/m − 1)·A < ρ(C)`, with `A = 5/2` and the containment margin
`ρ(C) = 1/2 − a·(cos θ_c + sin θ_c)` minimised over the certificate's cores.  Computed exactly
over all 49 A60 certificates:

* the **binding core is the pin core** in every one (a = 16383999967232/32768001953125,
  tm = 1/33554432), giving **ρ = 1.0000009e-9** — *exactly* A63's corpus value, reproduced
  independently here;
* the tilted conditioning cores are NOT binding (ρ_tilt = 1/2 − a = 6.4e-4 … 1.4e-1);
* hence the transfer shell is **ρ/A = 4.0000e-10 relative**: an s0 certificate reaches down only
  to m ≥ 3.877083998, while the window needs m ≥ 3.82.

**So every A60 (K) leaf instantiates `stratum_kill` at no side of [3.82, ŝ] at all.**  The shell
is **264× narrower than the (s0 − ŝ) gap alone**, let alone the window.  A60's leaves are in
exactly A63's "s0-only ⇒ evidence, not proof" bucket, alongside the A57 sub-trees.  This is
G-A59-7 made quantitative, and it is unchanged by anything the campaign has computed so far.

*A false alarm worth recording:* applying B′'s ρ formula to the **tilted** conditioning cores
gives ρ ≈ −0.204 and appears to say Lemma B's hypothesis (H) fails outright for 12 certificates.
That is a misapplication — B′'s `cos θ_c + sin θ_c` is the axis-parallel bounding half-width of a
core being compared against an **axis-aligned** dilated pin square.  A tilted core sits inside a
same-tilt packing square with margin `1/2 − a`, which is positive throughout.  All A60 margins
are positive; the pins bind.

## 2. The four confinement leaves — RESOLVED by Lemma B-NO, with a widening obligation

*Superseded 2026-09-01 by A63's clause B.2″ (`closed_disjoint_bridge.md`), relayed by the
coordinator.*  A60 raised that Lemma B is stated for **empty `nofams`**, while four A60 PASS
certificates carry a NO-family — and those four are exactly the **confinement** leaves, the only
viable route for the outer triple (G-A60-2).  A63's answer: **they do transfer.**  Occupancy
constraints dilate with the zone contracted by 1/λ, with no side condition on core owners.  A60's
tilted-core false alarm (§1) is codified as the owner-frame criterion B.2′, so it will not be
re-derived.

**But the consumer inherits a widening obligation:** to conclude about a target zone, the
certified zone must be wider by `w = (λ_max − 1)·|coordinate|`.  Quantified for A60's confinement
squares (`|c|` = the larger centre coordinate; the dilation preserves orientation, so **t is not
widened — centres only**):

| route | shell λ−1 | w(sq4) | w(sq6), w(sq10) | worst case | as % of rBasin |
|---|---|---|---|---|---|
| fat-pin corpus (ρ = 1.0e-9) | 4.0e-10 | 1.01e-9 | 1.27e-9 | 1.35e-9 | **0.0 %** — absorbed |
| slack-core grid, δ = 1e-3 | 4.0e-4 | 1.01e-3 | **1.27e-3** | 1.35e-3 | **67–90 %** |

**Finding (the coordinator asked me to say so if it does not absorb): at δ = 1e-3 it does not.**
The widening eats 85 % of the whole basin budget for sq6/sq10, leaving only
`rBasin − w = 2.31e-4` for the confinement radius itself — against a *measured* landing of
1.4472e-3 (§5).  That is 6.3× too loose, i.e. **~8 further bisection levels on every ladder**.

### 2a. δ is a free knob, and it trades grid size against basin budget

The widening is `(δ/A)·|c|` while the grid size is `~log(s0/3.82)/log(1+δ/A)`, so δ trades them
directly:

| δ | shell | w (sq6/sq10) | % rBasin | budget left | extra ladder levels | grid sides |
|---|---|---|---|---|---|---|
| 1e-3 | 4.0e-4 | 1.269e-3 | 84.6 % | 2.31e-4 | **7.9** | 38 |
| 5e-4 | 2.0e-4 | 6.345e-4 | 42.3 % | 8.66e-4 | 2.2 | 75 |
| 3e-4 | 1.2e-4 | 3.807e-4 | 25.4 % | 1.12e-3 | 1.1 | 124 |
| **1e-4** | 4.0e-5 | 1.269e-4 | 8.5 % | 1.37e-3 | **0** | 371 |
| 5e-5 | 2.0e-5 | 6.35e-5 | 4.2 % | 1.44e-3 | 0 | 742 |

**Recommendation: δ ≈ 1e-4, not 1e-3.**  It costs ~371 grid sides instead of 38 (×10 in
certificate count) but demands **zero** extra ladder depth, whereas δ = 1e-3 demands ~8 extra
levels on every ladder for every square — and ladder cost grows with the residue, so the ×10 in
grid sides is very likely the cheaper end of that trade.  δ ≈ 3e-4 is the balanced middle
(1.1 extra levels, 124 sides).  Deciding this properly needs the re-emission cost at each δ,
which is what the test in §3 measures.

### 2b. The same widening improves D.SLAB

A63's D.SLAB note says the pulled-back basin box "misses the basin by ~(λ−1)·|ĉ| ≫ rBasin for any
λ reaching s0" — computed for a single s0 certificate spanning the window, λ−1 ≈ 1.5e-2, giving a
miss of ~4.7e-2 = **31× rBasin** (hopeless).  Under the **grid** route the per-certificate λ−1 is
the grid step, not the window: at δ = 1e-3 the miss is 1.27e-3 = **0.85× rBasin**, and at
δ = 1e-4 it is 1.27e-4 = **0.085× rBasin**.  So the grid route does not merely give the (K)
leaves a window form — **it brings D.SLAB from hopeless to marginal-or-comfortable**, which is a
stronger reason to adopt it than the kill transfer alone.  (Still A60's obligation to discharge;
this only re-prices it.)

## 3. The repair route, and why its cost must be re-measured here

A63 B.4's **slack-core grid**: re-emit with pin core half-side `a = 1/2 − δ`, giving `ρ ≈ δ` and
a transfer shell of `δ/A` relative.  At δ = 1e-3 that is 4e-4 relative (~1.55e-3 in s), so
**~37 fixed-side certificates cover [3.82, s0]** — i.e. re-run A60's trees at ~37 grid sides with
slackened pin cores.  A63 calls this "the only currently-visible route for giving … the A60
zone-tree a window form without re-architecting it parametrically", and prices the slack as "the
eps_geo-measured regime, known affordable at ~0.5 budget-slack (A56 P6(v))".

**Caveat A60 must attach to that price.**  A60's own measured certification law is *stricter*
than A56's 0.5-slack gate: on trump5, a node certifies iff **η = τ − budget reaches −1** (every
η ≤ −1 node PASSed; every η = 0 refused; both fractional-η nodes, −0.33 and −0.50, FAILed —
`notes/falsifier.md` §6).  A 0.5 budget-slack is precisely the regime that failed here.  So the
slack-core route's affordability on trump5 is **unmeasured**, and inheriting A56's number would
be unsound.  Cheapest test: re-emit one already-PASSing A60 cover leaf with δ = 1e-3 pin cores
and see whether it still certifies — one LP + one cert, minutes.  Recommended before anyone
budgets the ×37.

## 4. D.SLAB — the exposure the slack-core route does NOT fix

A63 B.4's boundary note, quoted because it names A60 directly:

> The remaining S4 exposure is confined to `trump_residual` (the A60 tree's conclusion is a
> containment, not an emptiness — Δ_λ transfers kills, not containment conclusions; the
> pulled-back basin box shrinks by λ toward the origin and misses the basin by ~(λ−1)·|ĉ| ≫
> rBasin for any λ reaching s0).

So even with every (K) leaf given a window form, A60's **(D) leaves** — whose conclusion is that
six cores sit inside the basin — are not carried across sides by Lemma B.  **§2b re-prices this:**
under the grid route the per-certificate λ−1 is the grid step rather than the whole window, which
moves the miss from 31× rBasin (hopeless) to 0.85× at δ = 1e-3 or 0.085× at δ = 1e-4.  That is depgraph node
D.SLAB and it is A60's, not A63's, to answer.  It is the same object as the T5'.2 s-range clause
(σ ≥ ŝ − h must be delivered by the tree) and as G-A59-7's absorbed G-A59-8.  **No A60 work so
far touches it.**

## 5. rBasin: the discharge test was wrong in BOTH the radius and the coordinates

A63 X.3 makes the Lean basin radius concrete: **rBasin = 3/2000 = 1.5e-3**, and the obligation
D.S6 is stated in the **t-world** (t = tan(θ/2)), not θ-radians.  A60's ladder was testing
containment ≤ h = 3.7e-3 **in θ-radians**.  Both were wrong, in opposite directions.  Measured on
A60's own level-24 located boxes (28 boxes, the square-1 discharge candidates):

| metric | value | target | verdict |
|---|---|---|---|
| max box radius | 4.4450e-4 | — | = 0.30·rBasin (matches A63's note) |
| max containment, **θ-radians** | 2.0102e-3 | rBasin 1.5e-3 | **FAILS** |
| max containment, **t-world** | **1.1426e-3** | rBasin 1.5e-3 | **passes, margin 1.24×** |

The t-world is the more favourable metric (|dt| ≤ |dθ|, A63 X.1), and it is the one the statement
actually uses — so the boxes do land, but only by 24 %, and the old θ/h test would have
manufactured false (D) leaves at deeper levels.  `tree60.py` now computes `contain_t` against
`RBASIN` as **the** discharge test and keeps the θ/h number as a diagnostic only
(`max_containment_t` vs `max_containment_theta` in every ladder scan).  Re-verified after the
change: the j = 0 ladder still terminates at **level 24, 28 boxes, all inside**, cumulative kill
queue unchanged at 540 — the correction costs no extra levels for square 1.

**Squares 2 and 3 re-checked (done, not assumed)** — `results/a60_recheck_sq23_rbasin.json`,
ladders re-run under the corrected test:

| square | terminal level | boxes | contain_t | contain_θ | inside rBasin | margin |
|---|---|---|---|---|---|---|
| 1 | 24 | 28 | 1.1426e-3 | 2.0102e-3 | yes | 1.24× |
| 2 | **26** | 58 | **1.4472e-3** | 2.0102e-3 | yes | **1.04×** |
| 3 | **26** | 32 | **1.4472e-3** | 2.0102e-3 | yes | **1.04×** |

Two things follow.  (i) Squares 2 and 3 need **two more ladder levels than square 1** (26 vs 24)
and still land at only a **4 % margin** — in θ-radians they read 2.0102e-3 and would FAIL rBasin
outright, so the coordinate correction was load-bearing for them, not merely tidy.  (ii) A 1.04×
margin has no room for the §2 widening obligation: 1.4472e-3 + 1.269e-3 ≫ 1.5e-3.  **The landings
and the dilation displacement have to be budgeted together, and currently are not.**

## 6. Ledger summary

| A60 artefact | side | bridge status |
|---|---|---|
| 45 zone-cover / ladder (K) leaves, empty nofams | s0 | ρ = 1.0e-9 ⇒ shell 4e-10 ⇒ **no window instance**; slack-core grid is the route |
| 3 confinement (K) leaves + 1 selftest, nofams ≠ ∅ | s0 | **transfer OK via Lemma B-NO (B.2″)**, but carry a widening obligation w = (λ−1)·\|c\|: absorbed in the fat-pin shell (1.3e-9), **NOT absorbed at grid δ = 1e-3 (1.27e-3 = 85 % of rBasin)** |
| 28 / 58 / 32 located boxes (squares 1 / 2 / 3 (D) candidates) | s0 | inside rBasin in the t-world by 1.24× / **1.04×** / **1.04×**; **D.SLAB unresolved**, and the §2 widening does not fit alongside these landings at δ = 1e-3 |
| Lemma A59-P1 (interior NO child) | s0 | inherited from A59; same s0-only status |
