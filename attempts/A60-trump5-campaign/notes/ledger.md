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

## 3. The repair route — MEASURED (after retracting a harness bug): δ = 1e-3 certifies

A63 B.4's **slack-core grid**: re-emit with pin core half-side `a = 1/2 − δ`, giving `ρ ≈ δ` and a
transfer shell of `δ/A`, so ~38 fixed-side certificates at δ = 1e-3 cover [3.82, s0].  A63 prices
the slack at "~0.5 budget-slack (A56 P6(v))"; A60's law is stricter (η must reach −1), so it had
to be measured here.

### RETRACTED: "δ = 1e-3 fails certification"

The first run reported both test leaves failing to certify, and that was reported upward.  **It
was a bug in A60's own harness, not a property of trump5.**  `slackcore60` passed the slackened
pin boxes as `cond_boxes`, and `tree60.kill` *prepends* the standard `PINS` — so the node carried
**5 fat pins + 5 slack pins + 1 zone core = 11 cores** at budget 5.  The verifier rejected it
correctly:

    MALFORMED certificate: budget 5 != n - #cores = 0

so the "failures" were malformed-input aborts (cert_s 0.7–1.0 s, no verification attempted), and
the fat pins were still present, meaning ρ was still 1e-9 and nothing about slack cores was
exercised at all.  Everything from that run is quarantined under
`crashquarantine/INVALID_11core_*` rather than deleted.

**Guard installed so the mistake cannot recur:** `tree60.kill` takes a `pins=` argument that
*replaces* the pin set, and asserts `11 − #cores == budget` before any solve, raising rather than
emitting a certificate the verifier would reject.  Two prior symptoms are now explained by the
same root cause — the δ = 1e-3 "FAIL(eps_geo retries exhausted)" and the δ = 1e-4 "FAIL(rc=2)"
were the same malformed node at different δ.

**Lesson for the ledger:** a FAIL that arrives *faster* than a real verification (0.7 s against
the 5–19 s a genuine PASS costs on these nodes) is a malformed-input signature, not evidence about
the mathematics.  I read it as the latter and should not have.

### Corrected result: **δ = 1e-3 slack cores CERTIFY on trump5 — the grid route is real**

Re-run with the slack pins *replacing* the standard pins (6 cores at budget 5),
`results/a60_slackcore.json`:

| leaf | original (ε-fat pins) | δ = 1e-3 slack pins (corrected) |
|---|---|---|
| `c0_Y0081` | η = −1.0, LP 126 s, cert 5.2 s → PASS | η = −1.0, LP **66 s**, cert 5.3 s → **PASS** |
| `c0_Y0083` | η = −1.0, LP 144 s, cert 10.1 s → PASS | η = −1.0, LP **557 s**, cert 3.8 s → **PASS** |

**2/2 PASS, with certification cost essentially unchanged** (cert 3.8–5.3 s against 5.2–10.1 s).
The LP cost is noisy rather than systematically worse — one leaf got ~2× faster, the other ~4×
slower — on a sample of two, so no cost multiplier should be quoted from this yet.  A63's
"~0.5 budget-slack, known affordable" survives contact with trump5's stricter η ≤ −1 law: both
slack runs still land exactly at η = −1.

**So the slack-core grid is a live route for giving A60's leaves a window form**, and the earlier
"it fails" report was purely the 11-core harness bug.

### δ = 1e-4 QUALIFIED — the operating point is settled

`results/a60_slackcore_delta1e-4.json` (pin core a = 0.499899968, ρ = 1.000010e-4, shell 4.0e-5,
371 grid sides):

| leaf | ε-fat original | δ = 1e-3 | **δ = 1e-4** |
|---|---|---|---|
| `c0_Y0081` | LP 126 s, cert 5.2 s, PASS | LP 66 s, cert 5.3 s, PASS | LP **128 s**, cert **10.0 s**, **PASS** |
| `c0_Y0083` | LP 144 s, cert 10.1 s, PASS | LP 557 s, cert 3.8 s, PASS | LP **524 s**, cert **8.8 s**, **PASS** |

**4/4 PASS across both δ values, at costs indistinguishable from the ε-fat originals.**  δ = 1e-4
is a drop-in: `c0_Y0081` reproduces its original almost exactly (128 s vs 126 s).  The LP spread on
`c0_Y0083` (144 → 524–557 s at both δ) is the same at either slack level, so it is that leaf's
own variance, not a slack penalty.

**A refinement to the η law, from this run.**  `slack0.0001_c0_Y0083` certified at
η = −0.9999999999999831, i.e. *fractionally above* −1.  The law is therefore about the **integer**
gap — certification needs τ ≤ budget − 1 up to LP noise, and the certifier's rational scaling
absorbs the 1e-14 — not about η's sign at machine precision.  The genuine failures remain the
honestly-fractional ones (η = −0.33, −0.50).  Stated loosely, "η must reach −1" would wrongly
predict this PASS.

### Which δ, then?

Certification does not discriminate: both δ values pass at equal cost.  **The δ choice is
therefore governed by §2a's widening budget alone**, and that argument is unchanged:

| δ | grid sides | widening as % of rBasin | extra ladder levels |
|---|---|---|---|
| 1e-3 | 38 | 84.6 % | ~8 |
| 3e-4 | 124 | 25.4 % | ~1 |
| **1e-4** | **371** | **8.5 %** | **0** |

The trade is ~333 extra grid sides against ~8 extra bisection levels on *every* ladder for *every*
square — and ladder cost grows with the residue, which grows with depth.  **δ = 1e-4 is now
qualified and is the operating point.**

**Grid commitment is HELD** (coordinator's instruction) until cover j = 0 completes and §5's joint
landings-plus-widening budget is written down.  That interaction is the live risk, and at δ = 1e-4
it does **not** currently close:

    squares 2,3 landing   1.4472e-3   (measured, ladder level 26)
    widening at δ = 1e-4  1.269e-4    (= (δ/A)·|c| for sq6/sq10)
    sum                   1.5741e-3   >  rBasin = 1.5e-3      -- over by 4.9 %

So even at the favourable δ the two obligations do not both fit at the current ladder depth: the
ladders need roughly one more bisection level (a factor 2 in radius buys ~7e-4 of headroom, far
more than the 7.4e-5 shortfall).  **This is the number to settle before any grid is committed**,
and it is why the ×371 should not be budgeted yet.

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

---

## 7. Relay to A57 (PID/liveness lessons) — CHECKED, and A57 is not affected

The coordinator asked me to relay A60's two liveness bugs to A57, whose `RESUME.md` documents a
pidfile-based scaler guard.  I read A57's code before relaying, and **neither bug applies**:

* **PID recycling.**  A57's guard does *not* trust the pidfile.  `scaleup.ps1`'s `$isLiveScaler`
  reads the pid, then verifies via `Win32_Process` that it is a `powershell*` whose CommandLine
  contains `scaleup.ps1` and is not `-NonInteractive`, and is not itself.  A recycled pid fails
  that identity test, so a reboot cannot make the guard see a phantom scaler.  A60's bug was
  precisely the missing identity check — A57 already has it, from a *different* incident (a
  status-check tool session being miscounted as a scaler, which cost them a real 1.5 h outage).
* **Relative script paths.**  A57's `launch.ps1` / `run_job.ps1` build `ArgumentList` from
  `"$base\code\<script>.py"` with `$base` absolute, so `CommandLine -like '*A57-shadow-trees*'`
  matches correctly.  A60's launchers pass `code\tree60.py` relative with the directory only in
  `-WorkingDirectory`, which is why the same filter found nothing here.
* A57's per-job pidfiles (`logs/<stamp>.pid` from `launch.ps1`, `logs/<Tag>.pid` from
  `run_job.ps1`) are **written and never read** for a liveness decision, so they carry no
  exposure either.

So the relay is "no action needed", which is worth stating explicitly — a false alarm forwarded to
another attempt costs someone a re-derivation, exactly the failure mode §1's tilted-core note was
written to prevent.

### What IS worth relaying: nobody had integrity-checked A57 or A61 after the crash

A57 and A61 were both live at 19:08 and neither has an equivalent of `code/integrity60.py`.  I ran
a **read-only** scan of their artefacts (nothing outside A60 was written):

| attempt | artefacts scanned | torn |
|---|---|---|
| A57-shadow-trees | 1161 | **0** |
| A61-window-stragglers | 84 | **0** |

Both are clean, so no recovery action is needed for either — but the check had not been run, and
"clean" is only knowable by running it.  `code/integrity60.py` is attempt-agnostic apart from its
path constants and can be pointed at either tree if this recurs; the one class it is designed to
catch and that would be silent otherwise is **a torn certificate still carrying its `.PASS`
marker**, which reads as a proof that was never verified.
