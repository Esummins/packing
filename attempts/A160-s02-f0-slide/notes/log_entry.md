# A160 — the LOG.md entry (staged; appended verbatim)

## 2026-09-08 — A160: S02's f0 slide, and the pinwheel's common-tilt chain (`attempts/A160-s02-f0-slide`)

**The brief's premise needed one correction before anything could be grown.** `f0` is not a body of
A116's `N`: `a116lib.LOADBEARING["S02"] = ("f1", "f2", "f3")` ("f0 is the strut") and A116's `N` has
four free boxes — `f1, f2, f3, BR(0,1)` — plus five pins, with `f0` and `TR(0,0)` absent. So `f0` was
not left ungrown by an ordering accident; there was no `f0` knob. Growing it means ADDING a fifth
free body, which strengthens the theorem and weakens the hypothesis at the same time, and both had to
be measured.

**The slide is real, and exact.** The gallery's S02 poses (six decimals, worst pair gap −2.9e−7) were
polished by SLSQP + a Newton solve of the active contact system to s\* = **3.886746028606**, tilt
**48.435119375°**, worst gap −3.3e−16; the same solve with `f0` deleted returns the SAME s\* to twelve
digits, so `f0` does not set the side. `f0`'s admissible set was then computed EXACTLY as a polygon —
the eight separating-axis selections of a pair are affine in the moving centre at a fixed tilt, so the
forbidden set is an intersection of eight half-planes and relaxing `gap ≥ −eps` pushes each inward by
exactly `eps` — and the `eps → 0` ladder settles the question an area computation and a pose grid both
get wrong (both return "nothing"): **area and width vanish linearly in `eps` (5.97e−10 and 3.22e−9 at
`eps` = 1e−9) while the length converges to 0.298418661.** The slide is a segment, along `f0`'s own
body axis `e2 = (−0.748205, +0.663468)` (agreeing with `(−sin θ*, cos θ*)` to six decimals) at a
**fixed** tilt — the tilt window closes like `sqrt(eps)`, 10.05° at 1e−2 down to 0.03° at 1e−7, a
quadratic tangency at 48.4351° that opens only upward. Ends (2.180910, 1.507845) and
(1.957631, 1.705836); **three contact graphs** — `{BL(1,0), BR(0,1), f3}` at one stop,
`{BL(1,0), f3}` on the entire open interior, `{BL(1,0), f1, f3}` at the other — which is the PI's
diagonal slot exactly, with no wall contact anywhere, and the gallery's own `f0` sitting at u = 0.120
of it rather than at an end. **At s₀ nothing slides at all**: in A116's s₀-anchored frame every one of
the eleven has an empty admissible set at every `eps` down to 1e−9, because the ten-square core alone
needs s\* > s₀ — the slide is an object of the `s = s*` fibre and is what the box must cover, not a
place a packing can be.

**`f3` is not a rattler; it is the shadow's most load-bearing square** (s\* drops 0.118979 without it,
the largest Δs\* of the eleven, against 0.063870 for `f1`, `f2`, `BL(0,1)`, `BR(0,1)`). Two by-products
of the census: **`BR(0,0)` is a second rattler with a longer slide (0.535705)** — a *slot* square that
A116 pins to a 0.00707 slack core — and the four wedged-but-loadless slots (`BL(0,0)`, `BL(1,0)`,
`TL(0,0)`, `TR(0,0)`) make the shadow's true load path `{f1, f2, f3, BL(0,1), BR(0,1)}`.

**Putting `f0` in `N` costs consumers and does not certify.** The box that just covers the slide is
small (x half-width 0.111, y 0.099, offset −0.098/+0.087 from `f0`'s own anchor) and, as one more
clause in the hypothesis, it cuts A151-B's 96 in-`N` nodes (42 alive) to **15 (8 alive)**; the count
recovers to 96/42 only when `f0`'s box reaches ±0.50 / ±0.47 / ±45°, i.e. only when the clause is
vacuous. Meanwhile the tree with `f0` as a fifth free body **caps**: A116's base `N` plus the
slide-cover box is a WALL CAP at 420 s, and a retry at a 1500 s cap was still running with **0
witnesses and 0 unresolved** at 1024 s of tree time when it was cut to give the tilt slices the CPU
share — certified min 3.8770844 > s₀ throughout — so no `N` containing `f0` was certified inside the
4 CPU-h cap and the ladder never left its first rung. Every `f0` refusal in this attempt is a wall
cap, none is a witness.

**The common-tilt chain works, is cheap, and buys almost nothing.** `s*(θ)` recomputed here on the
shared tilt of `f1, f2, f3` (SLSQP + Newton, tilt pinned, warm-started along the curve, worst gap
≤ 4e−16 everywhere) rises on both sides of 48.435° and is **above s₀ at every tilt** — 3.9968 at 3.4°,
3.8868 at 48.4°, 3.9741 at 88.4° — which is why the links away from θ\* are nearly free. At half-width
1.25° and step 2.5°, **24 of 25 links certify, covering a 60.0°-wide shared-tilt range
[2.185°, 62.185°] at a median 7 s a link** (the whole chain in ≈ 7 minutes of one process), the single
refusal a **wall cap** at Δθ = +15° with 0 witnesses and 0 unresolved — and the same link certified in
12 s from a differently warm-started spine row at the same s\*, so it is a branch-order accident, not
geometry. Sampling found **0 hits in every certified link** and Trump is outside every one. A second
chain at half-width 10° and step 20° certifies Δθ = 0, ±20 at 55–279 s.

**But the chain's own union is 81 of 184 in-`N` nodes / 35 alive, and A151-B ∪ the chain is 104 / 45
against A151-B's 96/42 — plus eight, plus three alive.** The reason is structural and now measured: a chain link forces all three tilts into ONE
window of width 2h, so its ceiling is the number of nodes whose support tilt SPREAD is ≤ 2h —
**63/27 at h = 1.25°, 74/33 at 2.5°, 91/40 at 5°, 124/53 at 10°, 150/56 at 20°** — while of the 20
ALIVE k5_11-frame S02 nodes outside A151-B, **`f2`'s tilt binds 14 and `f3`'s binds 10, and 9 are
blocked by those two tilts ALONE.** Those are INDEPENDENT windows, and no common-tilt chain, at any
tilt range, can open them.

**So the object that reaches them is a product of INDEPENDENT tilt slices — and it works, nearly for
free, but only in one regime.** With `f1` at A116's own box, **all eight axis slices certify with zero
failures in 348 s total**, extending `f2`'s and `f3`'s tilt windows independently over the entire
fundamental domain [−1.56°, 98.44°]; most corners of the 5 × 5 product certify at 2–188 s each, and the
ones that do not are the combinations where two squares are simultaneously near axis-aligned. **But
the growth directions TRADE OFF.** `f2`'s upward slice certifies at `f1`'s base box in 108 s and is
**REFUTED BY A LIVE-LOW WITNESS** together with A151-B's grown `f1` — the witness puts `f1` at 83.44°,
a pose only the ±40° window admits (side 3.869337946 < s₀, re-verified from scratch, worst pair gap
−1.1e−16). Growing all four centre boxes together fails the same way at **r = 0.25 already**:
certified at Δθ = 0 and −10°, witness at +10°; at r = 0.30 witness at 0°; at r = 0.40 witness
everywhere. These are the **first LIVE-LOW witnesses anywhere in the A116 / A151 / A160 line** — A151
saw only wall caps — every one re-verified here (worst pair gap ≈ 1e−16, worst wall 0.0) and drawn.
They bound nine of the eleven squares, so they say nothing about s(11) ≥ s₀; they say the
neighbourhood is too big.

**Therefore A151's "compute-limited, not geometry-limited" holds for single knobs and fails for
compounded ones, and S02's basin is not a growable box but a UNION of differently shaped certified
boxes** — which is exactly what an `N_boxes` list with a disjunctive hypothesis is. A151-B ∪ the
common-tilt chain ∪ the independent tilt slices reaches **114 of 184 in-`N` nodes / 50 alive** (A151-B
96/42, A116 72/32) for **≈ 0.9 CPU-h of tree time across 50+ certified boxes**, with every refusal in
the record labelled wall cap or witness.

**The r_xy wall, in detail.** Growing all four centre boxes together refuses with a LIVE-LOW WITNESS
in under a second: r = 0.25 certifies at Δθ = 0 and −10° but is REFUTED at +10°; r = 0.30 is refuted
at 0° and +10°; r = 0.40 is refuted everywhere tested. This is consistent with A116's own grid, whose
only witnessed failures are at r = 0.30, and it means **r = 0.20 is a geometric limit for growing the
boxes together, not a compute limit** — the asymmetric, one-square-at-a-time growth A151 used is the
only kind that can go further, and even that stops where the compounding does.

**Files.** `attempts/A160-s02-f0-slide/` (`BRIEF.md`; `notes/{method,results,doc_lines,registry_row,
log_entry}.md`; `code/{polish160,pocket160,slide160,f0slide,lib160,grow160,chain160,slice160,
consumer160,needed160,nboxes160,gent160,draw160,drawwit160}.py`; `results/{polish160.json,
slide_exact.json,f0_tilt_window.json,f0_box_price.json,needed160.json,binding160.json,
spine_*.json,chain_*.jsonl,chain_*_summary.json,grow_*.jsonl,consumer160*.json,witnesses160.json,
N_boxes160.json,A160_slide_and_box.svg,A160_witnesses.svg}`; `logs/`), plus the registry row, this
entry, one paragraph in `docs/budget.md` §D and one sentence in `docs/residue_ledger.md` §1b. Two
BLAS-pinned processes at BelowNormal / affinity `0xFFFF` throughout, on a box that ran 16–19 other lab
pythons; wall, not CPU, was binding.
