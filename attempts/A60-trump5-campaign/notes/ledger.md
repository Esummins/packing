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

---

## 8. D.S6 — the composed containment statement (A60's obligation)

*Ownership confirmed by the advisor relay, 2026-09-01: the written composed containment statement
is A60's, and folds into the joint landings+widening budget document planned for after cover
j = 0.  This section is that document's skeleton; two of its four parts close now, and the other
two are exactly what the cover phase gates.*

**Statement to be written.**  Every packing in a (D) leaf has all **33 coordinates** within
`rBasin = 3/2000` of ẑ in the t-world, mod G — which is what `trump_residual`'s `InBasin`
conclusion needs on paper.  The 33 = 11 squares × 3 coordinates `(cx, cy, t)` split as
**5 pins × 3 = 15** and **6 free × 3 = 18**.

### 8.1 The pin half (15 coordinates) — CLOSED, measured

A60's pins sit at `slots(s0)`; ẑ's five simple squares sit at `slots(s_T)`, and `|s0 − s_T| =
4.100e-7`.  Both families are axis-aligned, so the t-coordinates agree exactly (θ = 0 for all ten;
max |θ| over the five matched ẑ squares is **0.000e+00** rad).  Centre deviations:

| pin | slots(s0) | slots(s_T) | sup-dev |
|---|---|---|---|
| 0, 1, 2 (BL staircase, s-independent) | — | — | **0** |
| 3 (BR), 4 (TR) | 3.3770840 | 3.3770836 | **4.100e-7** |

**Worst pin deviation 4.100e-7 = 0.027 % of rBasin.**  The pin half of D.S6 is discharged with
3.6 orders of magnitude to spare, and it does not depend on any campaign result.  (The matching
also fixes the pin↔ẑ bijection: pins 0..4 ↔ ẑ squares 0, 1, 3, 2, 5, sup-distances ≤ 1.5e-14.)

### 8.2 mod-G bookkeeping — CLOSED in structure

G = D4 × relabelling.  Both factors are pinned, not quantified over:

* **D4.** A59 theory.md §0: the trump5 pin set has **trivial stabiliser in D4** — the x↔y
  reflection fixes the BL staircase (λ = (2,1) is self-conjugate) but maps BR to TL, which is
  empty.  So the frame is rigid: the group element g is *determined* by the pin set, and there is
  no mod-D4 ambiguity to quantify over.  This is the one place A60's stratum is easier than a
  symmetric one.
* **Relabelling.** The pins are labelled by slot (§8.1's bijection), and each free square is
  labelled by the ẑ square its residue box hugs — which is exactly the ladder's `hugs` map,
  already recorded per box in every scan (`results/a60_ladder_j*_scan.json`).  So the bijection is
  *produced* by the tree rather than asserted.

**Consequence:** "mod G" in the written statement is discharged by exhibiting one specific g
(identity in the pin frame) and one specific bijection (§8.1 ∪ the `hugs` map), both of which the
campaign already emits.  No search over G is needed.

### 8.3 The free half (18 coordinates) — the budget, PENDING cover j = 0

This is the quantitative half, and the arithmetic is fixed in form; only the final landings are
missing.  Per free square, the requirement is

    landing(square)  +  dilation displacement  ≤  rBasin = 1.5e-3

with `displacement = (δ/A)·|c|` (centres only — Δ_λ preserves orientation, so t is not displaced).
Current status at the settled operating point δ = 1e-4:

| square | landing (measured) | displacement | sum | vs rBasin | verdict |
|---|---|---|---|---|---|
| 1 | 1.1426e-3 (L24) | 1.269e-4 | 1.2695e-3 | 1.5e-3 | **fits**, 15 % spare |
| 2 | 1.4472e-3 (L26) | 1.269e-4 | 1.5741e-3 | 1.5e-3 | **over by 4.9 %** |
| 3 | 1.4472e-3 (L26) | 1.269e-4 | 1.5741e-3 | 1.5e-3 | **over by 4.9 %** |
| 4, 5, 6 (outer, confinement route) | not yet run | 1.269e-4 | — | — | pending |

**The fix is one more bisection level** on squares 2 and 3: halving the box radius takes the
landing from 1.4472e-3 toward ~7.3e-4, buying ~7e-4 of headroom against a 7.4e-5 shortfall — a
14× margin on the repair.  That must be *run and measured*, not asserted, because a 1.04× margin
is exactly where eyeballing fails.

### 8.4 What closes this document

1. cover j = 0 completes → the ladder phase runs → squares 2, 3 re-land at level 27+;
2. the outer triple's confinement ladders run to their (D) radii (§2's route), giving rows 4–6;
3. drop the measured numbers into §8.3's table and state §8.1 + §8.2 + §8.3 as one lemma.

Nothing in 8.1 or 8.2 can change from campaign results — they are settled.  **D.S6 is therefore
gated only on the free-square landings, i.e. on ladder depth, i.e. on compute.**

---

## 9. A40's raised basin (A76 relay): same object — but A60 does NOT need it

**Question (1): is A40's box the same object A60's (D) leaves land in?  YES.**
Lemma P-B(R) (`docs/proofs/pair_kill.md` §6.8) states both A36 and A40 in the *same* form: a
θ-world ∞-box of radius h around (ẑ, ŝ) on which σ ≥ ŝ, equality iff z = ẑ, with
A36 h = 37/10000 and A40 h = 5794/884563 ≈ 6.55e-3 (2930 certs, 168 774 checks, 0 failures,
5 gates, exact-rational — same Python trust tier as A36 post-A70).  Checked against A60's three
requirements:

* **all 33 coordinates** — the box quantifies over `|c − ĉ|∞ ≤ h` and `|θ − θ̂|∞ ≤ h`, i.e. all 11
  centres and tilts.  Same object. ✓
* **t-frame (E.COORD)** — the theorem is θ-world; the transfer is X.1's `|Δθ| ≤ 2|Δt|`, so a
  t-radius of h/2 is what a (D) leaf may use.  P-B(R) writes exactly this ("tilt zones r_t ≤ h/2
  (t-radius)").  A60's landings are already measured in t. ✓
* **mod G** — unchanged by the raise; discharged as in §8.2 by trump5's trivial D4 stabiliser plus
  the ladder's `hugs` map. ✓

**Question (2): should A60 budget against 27/10000?  NO — and A79 should not be retargeted.**

The overshoot is an artefact of collapsing an *anisotropic* box to one uniform radius, not a real
geometric shortfall.  Split per coordinate, A60's landings are:

| square | centre containment | tilt containment (t) |
|---|---|---|
| 1 | 1.1426e-3 | 1.1400e-3 |
| 2, 3 | **1.4472e-3** (binding) | 1.1400e-3 |

The dilation displacement (1.269e-4 at δ = 1e-4) applies to **centres only**.  Against A36's own
per-coordinate radii — *no A40, no new certificate store, same theorem already exact-checked by
A70 and already the one A79 is formalizing*:

| square | centre + widening | vs A36 centre 3.70e-3 | tilt | vs A36 tilt 1.85e-3 |
|---|---|---|---|---|
| 1 | 1.2695e-3 | fits, **66 % spare** | 1.1400e-3 | fits, 38 % spare |
| 2, 3 | 1.5741e-3 | fits, **57 % spare** | 1.1400e-3 | fits, 38 % spare |

**Why the uniform constant was tighter than the theorem it came from.**  A63 X.3 picked
rBasin = 3/2000 under two gates: (a) tilt transfer `2·rBasin ≤ h` → ≤ 1.85e-3, and (b) s-slab
closure `rBasin(1+√2) < h` → < 1.5326e-3.  **Gate (b) is what caps it**, and P-B(R) drops (b)
when the side is separately in the shell.  For A60's (D) leaves the side is *fixed at s0*, with
`|s0 − s_T| = 4.100e-7` = 1.1e-4 of h — trivially in the shell.  So gate (b) is not binding for
A60 and the per-coordinate radii are legitimately available.  (A60's ρ_B is the same 4.1e-7 pin
drift of §8.1, so `√2·ρ_B = 5.8e-7` is negligible against either h.)

**Recommendation.**  Three ways to close the 4.9 % overshoot, cheapest first:

1. **One more bisection level on squares 2–3** (landing 1.4472e-3 → ~7.3e-4).  Pure compute, a few
   hundred extra queue LPs, **touches no formalization at all** — the uniform rBasin = 3/2000 in
   Lean stays exactly as A79 has it.  *This is the recommended route and it is already in the
   phase plan (`notes/resume_plan.md` step 5).*
2. **Per-coordinate form of A36** — free fallback if the extra level proves expensive; needs A79 to
   state the basin anisotropically (centre h, tilt h/2) but from the *same* A36 theorem, with no
   new certificate provenance.
3. **A40's h = 27/10000** — genuinely available and the same object, but buys A60 nothing that (1)
   or (2) does not, while adding a certificate-store retarget.  **Not requested.**

**So: do not retarget A79 on A60's account.**  A60 will close D.S6 against the uniform 3/2000 by
spending one ladder level.  Reported so the decision is on the record rather than implicit.

**Scope caveat, stated explicitly.**  This relief holds because A60's (D) leaves are stated at
**fixed s = s0**.  It does *not* extend to the window form: for a packing at side m ∈ [3.82, ŝ]
the side is not in the shell, gate (b) returns, and that is exactly **D.SLAB** — unchanged, still
open, still A60's (§4).  If D.SLAB is ever discharged by relocating (D) leaves to other sides, the
s-slab gate and this budget must both be re-derived at those sides.

---

## 10. δ_pin = 1e-2 qualification (the tube route) and the re-emission price

**Context (A83 relay, `docs/proofs/contraction_tube.md`).**  In the tube route every node
hypothesis acts on the dilated family F at s0, so **no B.2″ widening enters** and §8.3's 4.9 %
overshoot is void; pins ride the slot ray with w = 0.  Lemma SEAM gives
`δ_basin(trump5) = min(T_tube, T_K(δ_pin))` with
`T_K = ((2/3)·δ_pin·ŝ − (s0 − ŝ))/(1 + (2/3)·δ_pin)` and `T_tube = 0.0457` at A60's landings.

### 10.1 Qualification result — δ_pin = 1e-2 PASSES 2/2

| leaf | ε-fat original | δ_pin = 1e-2 |
|---|---|---|
| `c0_Y0081` | τ = 4.0, η = −1.0, LP 126 s, cert 5.2 s, PASS | τ = 4.112245, η = **−0.887755**, LP **961.1 s**, cert **540.8 s**, **PASS** |
| `c0_Y0083` | τ = 4.0, η = −1.0, LP 144 s, cert 10.1 s, PASS | τ = 4.000000, η = −1.0, LP **319.3 s**, cert **127.1 s**, **PASS** |

A57's G1 experience (whole grid at pin δ = 1e-2, V9/E4 clean) transfers to trump5.

### 10.2 But δ_pin = 1e-2 is NOT cost-neutral, unlike 1e-3/1e-4

This is the correction to my earlier expectation.  At δ = 1e-3 and 1e-4 the slack cores were a
drop-in (LP 66–557 s against originals 126–144 s, cert 3.8–10.0 s).  At δ = 1e-2 both LP and
certification blow up:

| leaf | original LP+cert | δ=1e-2 LP+cert | multiplier |
|---|---|---|---|
| `c0_Y0081` | 131 s | 1502 s | **11.5×** |
| `c0_Y0083` | 154 s | 446 s | **2.9×** |
| combined | 285 s | 1948 s | **6.8×** |

The certification side is the worse half (5.2 → 540.8 s, ×104 on `c0_Y0081`): a 1e-2 pin core
shrinks the exempt region enough that the verifier has to work materially harder.

**Re-emission price for the cover (K) leaves**, from the campaign's own measured costs:

    (K) leaves to re-emit         560 measured, ~599 projected at 767 attemptable
    their original cost           LP 67 532 s + cert 23 650 s = 25.3 CPU-hours
                                  (mean 120.6 s LP + 42.2 s cert; LP p50 58 s, p90 334 s)
    at the 6.8x multiplier        ~172 CPU-hours  ~=  43 h wall at 4 shards  ~=  1.8 desktop-days

**Caveat, stated because I have already been burned twice by small samples in this attempt:**
the 6.8× is from **n = 2**, and those two leaves disagree by 4× (2.9× vs 11.5×).  Treat ~170 CPU-h
as an order-of-magnitude estimate, not a budget.  The honest way to firm it up is to re-emit the
first ~30 leaves at δ = 1e-2 and read the multiplier off that batch; that is cheap and I would
recommend it before committing the full 599.

### 10.3 δ_pin = 2e-2 is worth having and is being qualified

`T_K` crosses `T_tube` at **δ_pin ≥ 0.0179**, so:

| δ_pin | T_K | δ_basin | binding |
|---|---|---|---|
| 1e-4 (A60's earlier plan) | 0.00026 | 0.00026 | slack |
| 1e-3 | 0.00258 | 0.00258 | slack |
| **1e-2** | 0.02568 | **0.0257** | slack |
| **2e-2** | 0.04597 | **0.0457** | **tube** |

Against the near-ŝ extrapolations (1.7e-3 / 5e-3) 0.0257 is already 5–15× clear; against the one
deep point (k4_08, η = −0.38 at ŝ − m = 0.044) it is **not** enough and 0.0457 is.  Since
trump5's own crossover is exactly what A82 has not scanned, qualifying 2e-2 now avoids a
re-qualification later if trump5 turns out k4_08-like.  First leaf already **PASSES** at
δ = 2e-2 (`c0_Y0081`, τ = 4.1875, η = −0.8125, LP 1000.4 s unconverged, cert 8.0 s); second in
flight.  Regime 1 is one plain certificate either way (slab width 0.051 at δ=1e-2 against 0.031
needed).

### 10.4 DECISION: δ_pin = 2e-2 adopted everywhere

δ = 2e-2 qualified **2/2** (`c0_Y0081` τ=4.1875 η=−0.8125 LP 1000.4 s cert 8.0 s; `c0_Y0083`
τ=4.25 η=−0.75 LP 945.5 s cert 5.1 s), combined LP+cert **1959 s = 6.9×** the ε-fat originals —
statistically identical to δ=1e-2's 6.8×, well inside the 1.5× adoption criterion.  Per the
advisor's rule, **2e-2 is adopted everywhere**; the tube binds, δ_basin = **0.0457**, and A84
measures the same T = 0.0457 law across all protected pin sets containing BL(0,1), so this is the
tier-wide standard.

The cost *profile* differs between the two even though the total does not: δ=1e-2 is
certification-heavy (cert 540.8 s on `c0_Y0081`), δ=2e-2 is LP-heavy (LP ~1000 s, cert 5–8 s).
Worth knowing for scheduling — 2e-2's cost sits in the LP, which parallelises across shards,
rather than in the verifier subprocess.

Not-yet-emitted leaves (deepen / ladder / confinement) are set to 2e-2 now, at zero cost.
A **30-leaf pricing batch at 2e-2** is running, **stratified over the original lp_s distribution**
(min 0 / p50 56 / max 582 s) rather than sampled from the cheap end — the bias that produced two
bad small-sample laws in this attempt already.

### 10.5 Shard-3 tail: NOT pathological, and there is no per-child cap

The advisor asked whether the last ~50 cover children are hitting the 600 s LP cap or the cert
cap.  **Neither — and the premise needs correcting: there is no per-child wall-clock cap at all.**
`--lp_time` is the limit handed to each individual LP solve *inside* `solve_node`'s
column-generation loop (`max_iter=900`), not a bound on the child.  Evidence: **161 of 718**
recorded children have `lp_s > 300` with `--lp_time 300` set.

Tail verdicts (last 25 shard-3 children): **18 PASS, 3 refused, 4 cert-FAIL** — a ~72 % kill rate,
i.e. the tail is *productive*, not a pathological residue.  Cert times 0.3–16 s; only 1 of 25 came
near the LP setting.

The night was eaten by exactly **one** child: `c0_Y0790` at **52 699 s (14.6 h)**, against a next-worst
of 582 s — a 90× outlier, and plausibly a symptom of the duplicate-process contention on that
child (§ the duplicate incident) rather than intrinsic hardness.

**So the remaining 49 were NOT routed to deepen.**  Two reasons: they are *unattempted*, not
resisters, and `phase_deepen` operates on resisters (an unattempted child has no box record to
bisect); and at a 72 % kill rate routing them would discard ~35 genuine kills and hand deepen work
it cannot do.  Instead the tail was **de-serialised**: shard `3/4` was split into `3/8` + `7/8`
(which partition `i % 4 == 3`), so a single pathological child can now block at most half the tail.


---

## 11. Lemma PD adopted, and what it does / does not change

**Implemented** (`tree60.pd_logic_kill`, wired into `classify_at` ahead of the slack-core test):
Σ_p is the FULL axis-aligned unit square at slots(s0); d(λ) = (λ−1)·α_p with
α = [(½,½), (3/2,½), (½,3/2), (−½,½), (−½,−½)]; the rule fires iff the child's rational core meets
Σ_p at **both** λ = 1 and λ = λ_max.  λ_max − 1 = (s0 − ŝ + T′)/(ŝ − T′) = **0.01192791** at
T′ = 0.0457, so the drift for max|α| = 3/2 is **0.017892 ≤ δ_pin = 2e-2** ✓ (matches A84's 1.79e-2).

**Canary clean:** PD does **not** fire on any of the three Trump-containing cover boxes (sq7, sq8,
sq9) — as A84 predicts, an image square's core misses Σ_p at λ = 1.  Selftests still 6/6.

**Effect size, measured on A60's own j = 0 cover (1152 boxes):**

| pin cores | logic kills |
|---|---|
| ε-fat (a ≈ ½ − 3.1e-8) — the baseline | **344** |
| slack δ_pin = 2e-2, ordinary test | **298** |
| slack δ_pin = 2e-2, **with Lemma PD** | **344** |

So the slack pocket costs **46 logic kills** at level 0, and **PD recovers exactly those 46**,
restoring the ε-fat baseline.  At ε-fat pins PD is a no-op (it fires on precisely the 344 already
contradictory), which is why the selftest reproductions are unaffected.

**What PD changes in the 30-leaf pricing batch: nothing directly, but it saves 46 jobs in the
full re-emission.**  The batch re-emits leaves that were *attemptable → PASS*; no attemptable box
fires PD (PD's 344 are exactly the contradictory set), so the batch's per-leaf cost is untouched.
The saving is elsewhere: without PD, 46 boxes that are FREE logic kills at ε-fat would become
attemptable at δ_pin = 2e-2 and need LP + certificate — ≈ **46 × ~980 s ≈ 12.5 CPU-hours** added
to re-emission, plus they would seed the residue floor in every ladder below them.  PD is
therefore mandatory for deepen/ladder (it is what prevents A84's 96 → 3862 blow-up) and a
~12.5 CPU-h saving on re-emission.

## 12. The anisotropic tube target is NOT reachable on A60's plan

A84 asks whether the squares 2–3 re-landing reaches the anisotropic tube form
(r_c, r_θ) = (6.5e-4, 2.1e-3) → T = 0.0525.  **Measured (square-2 ladder, stop disabled, to L34,
`results/a60_sq2_deep_ladder.json`): no — and the blocker is the CENTRE, not the tilt.**

| level | boxes | sup-containment (centre-dominated) | θ-containment |
|---|---|---|---|
| 24 | 35 | 1.7202e-3 | 2.4348e-3 |
| **26** | 58 | 1.4472e-3 | **2.0102e-3** ✓ meets r_θ = 2.1e-3 |
| 28 | 73 | 1.1742e-3 | 1.1742e-3 |
| 30 | 70 | 1.0378e-3 | 1.0378e-3 |
| 34 | 176 | **9.6952e-4** | 9.6952e-4 |

The **tilt half is already satisfied from L26**; the centre half is at 9.70e-4 at L34 against a
6.5e-4 target, decaying only ~1.77× per 10 levels, so it needs roughly **L39–L40** — not L29 —
and the residue is 176 boxes at L34 and growing.  So the anisotropic 0.0525 is not cheaply
available to A60: it buys 0.0457 → 0.0525 (+15 %) for ~6 further ladder levels on a growing
residue.  **Recommend staying at the isotropic tube T = 0.0457**, which A60's *current* L26
landings already certify, unless A82's trump5 crossover comes back needing more than 0.0457.

## A142 addendum (2026-09-07, append-only — for the A60 owner): the pin-clip has never been run on A60, and it empties 34 nodes

A131's T5‴ pin-clip (`attempts/A131-pin-clip/code/pinclip.py`) was measured on A57's corpus only. A60's pins are
**exact placements** (`hyp.boxes[i]` has `x0 = x1`), so their guaranteed core is the whole unit square,
`a_pin = 1/2` to the 1/2⁴⁰ grid (A135 `exactcore`, certified). Run at that half-side over the **283 A60 nodes
with an LP support** (A107 `results/shadow_nodes.json`), the clip empties **34** — dead by pin geometry, no LP,
no certificate or verifier change — and narrows **143** more (mean kept volume 0.544). **14 of the 34 are
emptied by the already-deployed T5″ trim alone**: they are open only because the trim was never applied to this
campaign. Replayable certificates in A131's `pin-clip-kill-certificate-v1` format (exact `a_pin`, the A135
`exactcore` certification of every pin box, full per-sub-bin replay trace):
`attempts/A142-a57-review-gallery/certs/a60/<tag>.clipkill.json`, ledger
`attempts/A142-a57-review-gallery/results/exactclip_kills_a60.jsonl`, summary `results/exactclip_kills.json`.
**A131's independent checker `checkclip131.py` passes all 34 unchanged (0 FAIL)**; sampled confirmation 408,000
drawn poses, 0 pin-free hits; 28 single-pin witnesses, 6 two-pin joint. Three of them (`c0_Y0168`, `c0_Y0254`,
`c0_Y0878`) are also drawn in `docs/shadows/a57v3/` and their pages say EMPTY. **Nothing in A60 was written**;
the recommendation is to run `trim57` and `pinclip` over the A60 population before any further LP there.

**A141 (2026-09-08, `polycore lane`).** The K' lane leaf at the usable slots (A118's leaf with A132's polygon cores
and A135's exact pin cores -- for A60 the pins are EXACT placements, so their K' is the FULL unit square and the
leaf is strictly stronger here than on A57's m-hulled pins) has now swept **all 325 alive trump5 nodes**.
**56 of them have `LANE_K' + M <= 1` at a usable slot, every one with `LANE_K' = 0` and `M = 1`** -- by slot
BR(0,1) 45 and TL(0,0) 11 (trump5's share of the 244 kills across A57+A60); **overlap with A142's 34
exact-pin-clip A60 kills: ZERO, so all 56 are new** (`attempts/A141-polycore-lane/results/t6_overlap.json`).
The usable slots read (all extensions FULL on the closed window): BL(0,2)->k6_07, BL(1,1)->k6_19, BR(0,1)->k6_21,
TR(0,1)->k6_22, TR(1,0)->k6_24, TL(0,0)->k6_23. Every kill carries a `polycore_slot_lane_v1` certificate
(`attempts/A141-polycore-lane/certs/slot_c0_*.json`, `slot_*_D*.json`) and the independent checker
`code/check141.py` passes 294 of 294 A141 certificates; sample line 200,000 poses per kill, 0 free.
**Nothing in A60 was written**; the recommendation is to retire these 56 (and their descendants) before any
further LP there. Caveat A118-O1 (exact pins, not the delta = 1e-2 slack family) applies.

**A153 (2026-09-08, `cover number`) — measured on trump5, NO kills, nothing written to A60.** The
cover-number leaf (Lemma CN: interior-disjoint unit squares have centres ≥ 1 apart, so if A148's
certified outer feasible-centre region `F_out` is covered by `k` axis-aligned squares of side
0.699473918 — diameter < 1, exact test `2d² < 1` — then at most `k` more squares fit, and
`k < budget` kills with no LP) was run on the **20 alive trump5 nodes A148 drew**
(`attempts/A153-cover-number/results/cover153_a148.jsonl`, rows with `camp = A60`) as part of a
322-node sweep. Every trump5 node needs **8 to 13** pieces against a budget of 5 (`f1_L10_0003`:
5 against budget 4, the tightest in the whole sweep), so **zero kills**, and each of them already
contains 4–6 points of `F_out` pairwise ≥ 1 apart — always at least its own budget, a floor that no
grid refinement can lower, so the leaf will not bite on trump5 however it is sharpened. The
tilt-coherent refinement (Lemma TC, sound only on a common-tilt branch) gives 4–12 pieces and also
kills nothing over any node's whole
tilt window. Recommendation: none for A60 — the leaf is a free sanity number for the gallery pages
(2–4 pieces tighter than A148's disk bound), not a lever. Statement, Lean shape, certificate format
and independent checker: `attempts/A153-cover-number/notes/lemma.md`.


**A152 (2026-09-08, `slot-lane shrunk`).** The PI's tolerance-shrunk refinement of A141's slot-lane leaf, tested
over the alive trump5 population as part of a 71 %-coverage sweep (229 of the 325 trump5 records; the record order
is a deterministic SHA-256 shuffle, so the covered part is a uniform sample). **Result: zero new kills.** The 20
trump5 nodes A152 certifies at an admissible translate — BR(0,1) and TL(0,0) — are all already A141 kills. Three
things specific to A60 are worth recording. (i) A60's pins are EXACT (`deepen.py` builds `Box(x, x, y, y, 0, 0)`),
so the refinement costs A60 nothing on the obstacle side — unlike A57, where the pin core must shrink to
`½ − h = 0.49293` and 5.9 % of A141's kills are lost; and A60's admissible translate set is the full
`{0, h}²` corner set, `t = 0` included. (ii) It nevertheless buys nothing, because every usable slot of trump5 is
backed on its two predecessor faces by a wall or a pin (BL(0,2), BL(1,1), BR(0,1), TR(0,1), TR(1,0) by a pin on at
least one axis; TL(0,0) by two walls), so the tolerance can only move the slot square towards the two OPEN faces,
which is where anything grazing the cell comes from. (iii) Whatever it did buy would be **conditional on a kill of
the extension class with the sixth pin slack**, which does not exist: k6_07/19/21/22/23/24 carry their closed-window
certificates with degenerate pin cores (`a = 16383999967232/32768001953125`, tolerance 3.08e-8). For A60 the
slack re-certification is the cheaper of the two lanes — only ONE core shrinks per class, the other five pins stay
exact — priced at **1–15 CPU-h** for the six classes (`attempts/A152-slot-lane-shrunk/notes/prereq.md`).
**Nothing in A60 was written.**


**A157 (2026-09-08) -- the UNDECIDED trump5 slot cells, including the PI's `c0_Y0076`, are not
kills (exact-pin form, class-S composition, A118-O1 stands).** Of A141's 196 UNDECIDED
`lane_lb = 0, M <= 1` slot cells, **48 are A60 trump5** (all level 1: BR(0,1) 22, TR(0,1) 12,
BL(0,2) 7, BL(1,1) 6, TL(0,0) 1), on **45 distinct nodes**. Re-screening them at 400,000 poses per
cell instead of A141's 8,000 realises a free pose on **24 of the 48** (24 of the 86 cells retired
corpus-wide are A60), which with their `M` gives `LANE_K' + M >= 2` and proves no kill is
available by this leaf; the other 24 stay kill-possible. **The PI's example resolves
against the kill.** `c0_Y0076` has exactly two non-`LANE>=2` cells, and they are the two named:
`TL(0,0)` draws 400,000 poses, 231,041 meet the slot cell, **14 are free of every core**, the best
clearing every pin core and the hypothesis square's `K'` by **1.1026e-2** at
`c = (1.6807459, 0.6862003)`, `theta = 29.4420 deg`; `BL(0,2)` draws 400,000, 270,606 meet, **3 are
free**, best clearance **5.2398e-3** at `c = (1.6636782, 3.1947477)`, `theta = 61.0252 deg`. In
both the binding core is the conditioned square's, and the clearance is ten orders of magnitude
above float64 geometry noise; the pose lies in the container and meets the closed cell, so it is in
`R'(C)`. So the reading that `TL(0,0)` is singly met -- a second meeter having to be a corner
intrusion that does not fit -- is not what the pose window says: a free square tilted 29.44 deg
reaches the cell while clearing the hypothesis square by 1.1e-2, and `LANE_K'(TL(0,0)) >= 1` with
`M = 1`. Of the 24 A60 cells that survive the screen, the certifying cover (A141's, at
`depth0 = 21, max_open = 4,000`) closed on none of those reached; corpus-wide the pass produced
**0 kills, 1 near-miss, 24 not closed** over 25 covered cells. **Nothing in A60 was written**, no
certificate was emitted, and `attempts/A157-undecided-slots/results/slot_kills157.jsonl` is empty
by construction. Cost ~0.7 CPU-h of a 3 CPU-h cap; the useful lever was the 50x pose draw
(2 s/cell), not a deeper cover (35+ CPU-s/cell).


**A158 (2026-09-08) -- the slot split: the NO child is a real, certified narrowing on `c0_Y0076`;
the YES child does not exist at any radius the LP can feel (exact-pin form, class-S composition,
A118-O1 stands).** The leaf is the tautology `SomeIn S | NoneIn S` on the near-simple slot box
`S(r, tt)` = {centre within `r` of the exact slot centre, tilt within `tt` of 0/90}: YES killed by
A141's lane leaf with `K'(S)` as an EXTRA obstacle (the `find_witness` discharge against `K'(S)`
IDENTIFIES the pose with the S-square, `PolyCoreT5.shared_point_same_square`, so the meeter count
is `1 + LANE_K'(C|S) + M(C|S)`), NO by one `caselp` `NoFam(S)` and an A135 exact-core re-solve.

**`c0_Y0076` `TL(0,0)` (extension `k6_23`, FULL window `[191/50, 969271/250000]` by A114): the NO
child is DEAD, and the kill is the slot box's.** `NoFam(S(0.10, 10 deg))` -- zone
`[0.4, 0.6] x [3.277084, 3.477084] x ([0,10] u [80,90]) deg`, clamped by `centre_in_slab` to
`[1/2, 0.6] x [3.277084, 3.377084]`, a quarter of the nominal box -- takes the node LP from
`tau = 5.000000` to `tau = 4.000000`, `eta = budget - tau = 1.000000` (20.6 s, converged).
**Control**: the identical exact-core re-solve with NO NoFam gives `tau = 5.000000` (3.0 s), so the
drop is not an artefact of the exact cores. Certificate
`attempts/A158-slot-split/certs/no_c0_Y0076__TL0_0__r0.1_tt10.json` (4 atoms, total `103/25` =
4.12 < 5), written through A136's `a136lib.narrow` (NO zone rounded INWARD, intersected with the
written box, `ZONE subset BOX` decided on the written rationals, max inward shift 7.40e-8), and
**PASS on the frozen `verify_case.py` (sha 521cb01f...) in 1.0 s** -- 7,262 boxes, 1,863 exempt
(core 1,861, nofam 2), "node DEAD". (`verify_param.py` rejects it as MALFORMED: it consumes the
PARAMETRIC schema, not a fixed-side `case-measure-certificate-v1`, so the second-verifier
cross-check is unavailable for this certificate kind, exactly as in A136.) **So under `c0_Y0076`'s
hypothesis SOME square must have its pose within 0.10 of the exact `TL(0,0)` slot centre with tilt
within 10 deg of axis-aligned** -- a new structural constraint on the node, and the half of the
PI's reading that holds.

**The YES child is refuted on `c0_Y0076`, and at every radius.** With `K'(S)` among the obstacles a
free pose that meets `int C`, lies in the container and clears every pin core, `K'(H)` AND `K'(S)`
is REALISED at 400,000 draws for every `(r, tt)` tried: at `tt = 10 deg` already at `r = 0` (the
corner-frame pose `(1.6913894, 0.6972960, 33.0398 deg)`), and at `tt = 0` for every
`r > 3.662e-4`. A realised free pose is a sound `LANE_K'(C|S) >= 1`, so this is a refutation, not a
budget failure. `M(C|S)` is the looser half (`H` is blocked out to `r ~ 3.6e-2` at `tt = 0`, but can
meet at `r = 0` once `tt >= 10 deg`).

**`c0_Y0787 BR(0,1)` and `c0_Y0959 TR(0,1)` are NEITHER.** Their NO child does not fire at
`r = 0.10, tt = 10` (`tau = 5.000000` in 4.9 s and 72.7 s), nor at `r = 0.05`, `0.02`, nor at
`tt = 0.4`, nor even at `r = 0.20, tt = 20` -- a 0.4 x 0.4 centre box with 40 deg of tilt: the LP
simply moves the slot square just outside the box. Their YES child is refuted like `c0_Y0076`'s
(`r_yes = 4.88e-5` and `2.92e-6` at `tt = 0`; refuted at `r = 0` for every `tt >= 0.31 deg`). So
the coordinator's reading that forcing `BR(0,1)` doubly met strands the space right of `H` is not
what the LP says.

**Why the two halves cannot meet, and it is arithmetic before it is geometry.** `caselp` exempts an
LP row only if its centre is inside the zone by `EPS_ZONE = 2e-3` and its tilt inside a
`t`-interval by `EPS_TH = 0.3 deg`; the two tilt intervals of `S` are `[0, tt]` and `[90-tt, 90]`,
whose margined forms are empty for `tt <= 0.3 deg`. So **any `S` the YES child could close on
exempts not one row**, and on such an `S` the NO child IS the original LP. Measured on `c0_Y0076`:
NO needs `r in (0.02, 0.03]` at `tt = 10 deg` and `tt in (1.5, 2] deg` at `r = 0.10`; YES closes
only at `r <= 3.66e-4` with the tilt PINNED, and is refuted at `tt = 0.31, 0.40, 0.49 deg` too. The
obstruction is in the TILT variable alone, hence independent of `r`, so no anisotropic box helps.

**The PI's geometry is NOT refuted -- the `K'`-based leaf is.** `pair158.py` looked for an explicit
interior-disjoint pair (a pose IN `S` clearing every node core, and a free second meeter) over the
six PI cells at `(r, tt)` in `{0.10, 0.01} x {10, 0.5} deg`, 600,000 draws each: **none exists in
the sample, the maximum pair gap is negative everywhere** (-6.1e-4 on `c0_Y0959`). `K'(S)` is the
intersection over the WHOLE box, so the intruder clears it while still overlapping every individual
square with a pose in `S`. The repair -- partition `S` and apply the leaf per piece (A141's
`lane_corner_split` shape) -- needs pieces `<= 3.7e-4` in centre and `< 0.5 deg` in tilt, about
1.5e6 pieces for `S(0.10, 10 deg)`, roughly 400 CPU-h per cell.

**A60 population**: 325 of the 1,590 distinct alive nodes are A60 trump5, and **159 of them** have
dual weight >= 0.5 in some usable slot's `S(0.10, 10 deg)` box (`trump5 TL(0,0)` 77, `BR(0,1)` 50,
`BL(0,2)` 49, `TR(0,1)` 13, `BL(1,1)` 11, `TR(1,0)` 3). Nothing in A60 was written; the two
certificates and every record live under `attempts/A158-slot-split/`.


**A158b addendum (2026-09-08) -- the YES child is an LP node, and it lands exactly back on the
knife edge.** `SomeIn S` is an ordinary case-LP hypothesis, so the YES child of the slot split is the
node `pins + H + the slot box S` with `budget = 11 - #cores = 4` (A135 exact cores on all 7 boxes,
`S` an ordinary second core in the frozen schema; `cores_pairwise_disjoint` re-run over ALL 7,
because A135's `ExactHyp` gates only `cores[:n-1]` and an unchecked `K(S)` meeting `K(H)` would make
the budget 5 rather than 4). **On all 12 sub-cases (6 cells x 2 tilt pieces of S), converged,
`tau = 4.000000 = budget`, `eta = 0`** -- `c0_Y0076 TL(0,0)`, `c0_Y0787 BR(0,1)`,
`c0_Y0959 TR(0,1)`, `k5_11_interior_Y0130/Y0147/Y1110 TR(0,0)`. **That is the general obstruction
made exact: the slot square removes exactly ONE unit of dual packing AND exactly ONE unit of budget,
so the YES child returns to the knife edge -- the same 1 the NO child removes from `tau` alone.** The
dual weight in `S` is exactly 1 on 730 of the 1,238 selected records, so on that whole
sub-population the split is structurally neutral and no amount of compute changes it.

The PI's mutual clip (A131 pin-clip with each box's own core in the pin's role, the largest
axis-aligned square inscribed in `K'` handed to A131 so the clip removes less than the truth) does
bite: `H`'s box keeps **0.5003** of its area on `c0_Y0787` and `K'(H)` grows **x1.126**
(0.590298 -> 0.664416); `c0_Y0076` keeps 0.8865 with `K'(H)` x1.027; `c0_Y0959` and
`k5_11_interior_Y0147` lose two whole tilt sub-bins of `S` at `nsub = 4`. But what changed the lane
test was the CLAMP, not the clip: writing `S` in the world frame clamped to `[1/2, s0-1/2]` halves
the centre box at a corner slot (`c0_Y0076`: 0.2x0.2 -> 0.1x0.1) and fattens `K'(S)` from 0.566 to
0.736. With that core `c0_Y0076 TL(0,0)` piece 0 has `lane_lb = 0, M_lb = 0`, but the cover still
only certifies `LANE_K' <= 1` and its open set GROWS with depth (159 -> 270 -> 646 at
`(22, 8k) -> (24, 30k) -> (26, 60k)`), while piece 1 has `M_lb = 1` outright -- so `c0_Y0076` is NOT
dead by the split on either route, and no closure record is written. `c0_Y0787` and `c0_Y0959` stay
refuted on the lane side even after the clip (free meeter realised at clearance 4.37e-2 and 1.23e-1).
The one cell where the hard half closes is A57's `k5_11_interior_Y1110 TR(0,0)`:
`LANE_K'(C | S, H_clipped) = 0` CERTIFIED on both tilt pieces (36 and 35 leaves, 0 open, ~36 s) --
the first empty conditional lane cover obtained anywhere -- but its `M` cover discharges ZERO leaves
(0 leaves / 5,001 open at depth 40; 0 / 40,001 at depth 42), because `box_misses_cell` can never fire
for an interior `H` against a corner cell, and its NO child is alive, so it is YES-only at best.
Cost ~0.7 CPU-h of a +2 CPU-h extension; nothing in A60 was written.

---

## A161 (2026-09-08) — CHORD-LIMITED LANE: 26 alive trump5 nodes dead, 24 of them new

`attempts/A161-chord-lane/` (leaf statement, soundness, certificate format, independent checker and
Lean shape in `notes/leaf.md`; the population table in `notes/t3_table.md`).

The leaf: at a wall-adjacent usable slot cell `C`, A144's chord row on a guard line `l` inside the
wall row of pins caps the number of FREE squares crossing `l` through opposite sides at
`beta = floor(s0 - SUM_j minchord(B_j, l))`; A141's lane cover, with one extra sound prune (`band`,
decided exactly by `max|v| <= (y + 1 - y^2)/2` at `y = cs_max`), bounds the rest by `LANE_out`; with
`M` the conditioned meeters, SLOT-CROWD's `>= 2` is contradicted by `beta + LANE_out + M <= 1`.
Exact-pin form throughout, so A118-O1 is inherited: these kill class-`S` packings with EXACT pins,
which is what A60's cover needs, not the slack family.

trump5 result (`m_lo = s0`, so the frame boxes are the exact-pin boxes at `s0` with no hull):
**26 kill pairs over 26 distinct nodes**, all level 1 — BR(0,1) 23, TL(0,0) 2, BL(0,2) 1; TR(0,1)
and TR(1,0) contribute none (TR(1,0)'s wall carries only ONE pin chord, so `beta = 2` there and the
leaf cannot fire). **24 of the 26 are new** (2 were already dead by A131/A142's clip leaves). Of the
26, 23 have `beta = 0` — the CONDITIONED square is itself the one square allowed to cross the wall
line (its `minchord` exceeds `s0 - 3 = 0.877084`), so nothing else reaches the slot and the slot is
singly met by `H` alone; 3 have `beta = 1, M = 0`.
32 trump5 pairs are UNDECIDED inside the 10 s/pair cover budget and are the natural re-run target.

Certificates `attempts/A161-chord-lane/certs/cl_c0_*.json` (SHA-256 in
`results/cert_manifest.json`); all 98 of the attempt's certificates PASS the independent checker
`code/checkcl.py` (D1-D8, which re-derives the cframe boxes, every `minchord`, every separating-axis
margin, the band threshold, cover completeness and the arithmetic; it imports only A132's
`vertex_ok` and A57's `caselp` from the emitter's world). Nothing under
`attempts/A60-trump5-campaign/` was modified.

### A161 continuation (2026-09-08) — CORRECTED count: 23 genuinely new trump5 dead nodes

**CORRECTION.** The entry above says "24 of the 26 are new", compared against A131/A142 only.
Against the full dead set the collector `docs/shadows/status_gallery.py` builds STATUS.md from
(44 sources, 4,994 kills), the trump5 half contributes **23 genuinely new dead nodes** — the A60
campaign is where nearly all of A161's residual value sits, because trump5's alive set has not been
re-solved the way A57's has:

`c0_Y0075, c0_Y0174, c0_Y0475, c0_Y0984, c0_Y0990, c0_Y0991, c0_Y0992, c0_Y1080, c0_Y1083,
c0_Y1084, c0_Y1085, c0_Y1087, c0_Y1088, c0_Y1091, c0_Y1092, c0_Y1093, c0_Y1094, c0_Y1095,
c0_Y1097, c0_Y1098, c0_Y1099, c0_Y1100, f1_L23_0030`

by slot: BR(0,1) 20, TL(0,0) 2, BL(0,2) 1; all level 1. 20 of the 23 have `beta = 0` — the
conditioned square is itself the one square the chord row allows across the wall line, so the slot
is singly met by `H` alone. Certificates in `attempts/A161-chord-lane/certs/cl_c0_*.json` and
`cl_f1_*.json`, 109/109 PASS `code/checkcl.py`; overlap in `results/overlap161.json`.

Also recorded (see `notes/t3_table.md` §T5-T7): the retry of the UNDECIDED pairs at 6 guard lines
each added 13 kills repo-wide; and A141's own leaf re-run with the exact separating-axis test flips
105 `M` values from `>= 1` to 0 across 3,048 early-exit cells but yields **zero** kills on its own —
without the chord row the lane cover never closes. The chord row, not the SAT fix, is what kills.

### A161 T8 (2026-09-08) — the CONDITIONAL form on c0_Y0169 / TL(0,0): half certified, band cover open

The conditional chord-limited lane splits the conditioned square's own box (tautologous, so nothing
escapes) and uses each piece's OWN fatter polygon core `K'(b)`:

    n(b) = beta + LANE_out(b)                          if every pose of b misses int C
         = min(beta, LANE_band(b)) + LANE_out(b) + 1   otherwise;      n(b) <= 1 everywhere => DEAD

with `LANE_out` the cover that discharges BAND boxes (charged to `beta`) and `LANE_band` its mirror,
discharging boxes every pose of which has chord `< 1` — a new exact primitive
`chordlane.not_band_ok`: `min|v| > (y + 1 - y^2)/2` at `y = cs_min`.

On `c0_Y0169 / TL(0,0)` (H at x 1.2398-1.3795, y 2.3578-2.4976, tilt 14.25-28.07 deg): guard line
`x = 364583/500000` on the LEFT wall of the TL frame, `minchord = [1, 0, 1, 0, 0, 0]` — the two pins
below the cell give chord exactly 1 each — `rhs = 469271/250000`, **`beta = 1`**, as the PI said.
Sample line on that offset: 8,174 poses meet `int TL(0,0)`, 58 are free and **all 58 are BAND poses**
(`outside_free = 0` of 4,258 outside poses).

* the PI's first half — nothing from the right reaches TL — is **CERTIFIED**: `LANE_out = 0` on every
  piece reached, including the `m = 1` ones;
* the second half — `H`'s corner leaves under 1 of width so no band square fits — is **OPEN**: the
  `LANE_band` cover did not close at 3,000 boxes (`open budget exhausted`) nor at 60,000 (the time
  budget went on one branch).

So `c0_Y0169` is NOT yet dead; the obstruction is exactly the `LANE_band` cover on the `B_meet`
pieces. Next levers (notes/t3_table.md §T8): rank offsets by `band_free` under `K'(piece)` rather
than by the `LANE_out` criterion; split `B_H` shallowly and give each `m = 1` piece its own line;
restrict the band cover's root to the band slab `|v| <= 1/2` before bisecting (~4x on root volume).
Code `code/condlane.py`, record `results/t8_cond.json`. No certificate emitted; the population pass
over the NO-LINE / `M = 1` cells was not run (budget), and its cost order should start with trump5
BR(0,1) (82 such cells, and 20 of A161's 23 new trump5 kills already sit on that slot).

## A167 (2026-09-09) — the conditional lane RUN over the population; 7 new trump5 nodes dead, and the rest measured

A161 T8 left the conditional chord-limited lane stated but unrun. A167 (`attempts/A167-condlane-pass/`)
ran it over the whole population, built FROM THE COLLECTOR rather than from a campaign snapshot:
**416 alive cells over 258 alive A57/A60 nodes** (every `NO-LINE`/`UNDECIDED` cell with `M = 1` in
A161's T3 tables whose node the collector still records ALIVE), in A161's cost order, at 60 s a cell.
All 416 ran.

**trump5 half.** `BR(0,1)` gives **10 kills of 66 cells**, `TR(0,1)` **1 of 48**, and
`BL(0,2)` / `TL(0,0)` / `TR(1,0)` give **zero**. After a fresh collect at the end of the attempt the
new trump5 dead nodes are **`c0_Y0989, c0_Y0993, c0_Y0995, c0_Y0996, c0_Y0997, c0_Y1002, c0_Y1131`**
(all level 1); `c0_Y0902, c0_Y0913, c0_Y0921, c0_Y0994` were also killed here but A149 had reached
them while A167 ran. Certificates `certs/cond_c0_Y*.json`, kind
`conditional_chord_limited_lane_v1`, **all PASS** the independent checker `checkcond167.py`.

**The two new levers, and which one pays.** Over the 121 pieces of the 15 certificates: 92 pieces
closed because the BAND cover reached `LANE_band = 0` (offsets ranked by the sampled `band_free`
count under `K'(piece)`, and the cover run over the band SLAB `|v| <= 1/2` that every band pose lives
in — a 4× cut of the root volume), and 29 because the PER-PIECE chord row gave `beta = 0` outright
(`minchord` is monotone under box inclusion, so the piece's own box is a legal, longer chord).
`c0_Y1131` is killed by the per-piece `beta` alone on all nine pieces.

**`c0_Y0169` — the PI's node — is a NO-GO, not a budget failure.** At `TL(0,0)` the whole-box picture
A161 reported still holds (`beta = 1` from the two wall pins, `LANE_out = 0` certified, 58 free BAND
poses), but on the pieces of `B_H` where `H` reaches the cell the sample exhibits a free pose meeting
`int C` at EVERY one of the 106 swept offsets — `band_free = 2–6` per 20,000 draws on the good
`x ≈ 0.729` lines even at split depth 5, and `outside_free > 0` on the h-lines — so the leaf's own
counters are `>= 2` and no budget closes it. The same holds at `BL(0,2)` (53 offsets, all screened).
The PI's geometric reading ("`H`'s corner leaves under 1 of width, so no band square fits") is
therefore **false as stated**: a band square does fit beside `H` on part of `H`'s box. No exact
two-crowd pair was found for `c0_Y0169` in 60,000 draws, so the cell is no-go at the depth searched
rather than exactly retired.

**Retirements.** 285 of the 416 cells are NO-GO in this sense; 60 were escalated to an EXACT rational
two-crowd witness and **49 certified** (`certs_nogo/nogo_*.json`, kind `nogo_two_crowd_v1`), which
retires those cells for the whole lane-leaf family. 116 cells remain `UNDECIDED-time` at the 60 s
budget — those are where a longer pass could still find kills.
