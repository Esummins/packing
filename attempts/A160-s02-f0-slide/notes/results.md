# A160 — results

Owner A160 (Opus engineer), 2026-09-08. Read `notes/method.md` §0 first: **`f0` is not a body of
A116's `N`**, so "growing `f0`" means adding a fifth free body, and that moves the theorem and the
hypothesis in opposite directions.

---

## T1. f0's slide

### The polished shadow (`results/polish160.json`)

| | |
|---|---|
| s\* (eleven squares) | **3.886746028606** |
| s\* (ten-square core, `f0` deleted) | **3.886746028606** — identical to 12 digits |
| common tilt | **48.435119375°** |
| worst pair SAT gap | −3.3e−16 (the gallery's six-decimal poses: −2.9e−7) |
| active contacts | 14 on eleven squares, 11 on the core |

**`f0` does not set the side.** That is the first of the two independent rattler tests.

### The slide itself (`results/slide_exact.json`, `code/pocket160.py`)

The exact `eps → 0` ladder of the admissible set of `f0` at the pinwheel tilt, others frozen:

| eps | area | length | width |
|---|---|---|---|
| 1e−2 | 6.520e−3 | 0.330839 | 3.223e−2 |
| 1e−3 | 6.024e−4 | 0.301644 | 3.223e−3 |
| 1e−4 | 5.974e−5 | 0.298741 | 3.223e−4 |
| 1e−5 | 5.969e−6 | 0.298451 | 3.223e−5 |
| 1e−6 | 5.968e−7 | 0.298422 | 3.223e−6 |
| 1e−7 | 5.968e−8 | 0.298419 | 3.223e−7 |
| 1e−8 | 5.968e−9 | 0.2984187 | 3.223e−8 |
| **1e−9** | **5.97e−10** | **0.298418661** | **3.223e−9** |

Area and width vanish **linearly** in `eps` while the length converges: the admissible set of `f0` is
a **one-parameter SLIDE**, a segment, not a pocket and not a rigid point. (An area computation
returns 0 and a pose grid finds nothing — a curve has measure zero in both.)

**Extent in (x, y, θ).**

| | |
|---|---|
| length | **0.298418661** |
| direction | **(−0.748205, +0.663468)** = `f0`'s own second body axis `e2 = (−sin θ*, cos θ*)` to 6 decimals — `f0` slides parallel to its own faces, diagonally up-left / down-right at **41.565° below the horizontal** |
| end A | (2.180910, 1.507845) |
| end B | (1.957631, 1.705836) |
| Δx, Δy | **0.223279, 0.197991** (the box that just covers it: `x` half-width 0.1114, `y` half-width 0.0987, centred 0.098 left and 0.087 above `f0`'s own gallery pose) |
| tilt | **FIXED**. The tilt window closes like `sqrt(eps)`: 10.05° at 1e−2, 4.01° at 1e−3, 1.17° at 1e−4, 0.36° at 1e−5, 0.11° at 1e−6, 0.03° at 1e−7 — a quadratic tangency at θ\* = 48.4351°, opening only UPWARD (the low end never moves off 48.435) |
| where the shadow's own `f0` sits | at **u = 0.120** of the slide, not at an end — the gallery pose is an arbitrary point of the family |

**The three contact graphs the slide passes through** (`contact_graph_sequence`, tol 1e−5):

| u | contacts of `f0` |
|---|---|
| 0.00 (end A) | `BL(1,0)`, `BR(0,1)`, `f3` |
| 0.02 – 0.98 (the open interior) | `BL(1,0)`, `f3` |
| 1.00 (end B) | `BL(1,0)`, `f1`, `f3` |

Exactly the PI's reading: the slot is diagonal and its stops are `BR(0,1)` at one end and `f1` at the
other, with `BL(1,0)` and `f3` the two rails held throughout. `f0` touches no wall anywhere on it.

**At s₀ there is no slide, and no pose of any square at all.** In A116's `s0`-anchored frame the
eleven-square configuration has worst pair gap **−6.6e−3** and every square's admissible set is
EMPTY at every `eps` tested down to 1e−9 — because the ten-square core alone needs
s\* = 3.886746 > s₀ = 3.877084. That is the content of the certificate, restated: the slide is an
object of the s = s\* fibre, and it is what the box has to cover, not a place a packing can be.

### Is `f3` a rattler with a slot of its own? **No — it is the most load-bearing square in the shadow.**

`results/slide_exact.json` `rattler_census`, both tests for all eleven squares:

| square | slides (eps → 0) | slide length | s\* without it | Δs\* | load-bearing for s\* |
|---|---|---|---|---|---|
| **f0** | **YES** | **0.298419** | 3.886746029 | 0 | **NO** |
| f1 | no | 0 | 3.822876 | 0.063870 | yes |
| f2 | no | 0 | 3.822876 | 0.063870 | yes |
| **f3** | **no** | **0** | **3.767767** | **0.118979** | **yes — the largest Δs\* of any square** |
| BL(0,1) | no | 0 | 3.822876 | 0.063870 | yes |
| BR(0,1) | no | 0 | 3.822876 | 0.063870 | yes |
| BL(0,0) | no | 0 | 3.886746 | 0 | no |
| BL(1,0) | no | 0 | 3.886746 | 0 | no |
| TL(0,0) | no | 0 | 3.886746 | 0 | no |
| TR(0,0) | no | 0 | 3.886746 | 0 | no |
| **BR(0,0)** | **YES** | **0.535705** | 3.886746 | 0 | no |

Two findings beyond the question asked: **`BR(0,0)` also slides, and further than `f0` (0.5357)** —
S02 has two rattlers, not one, and the second is a *slot* square that A116 pins to a 0.00707 slack
core; and the four "no Δs\*" slot squares (`BL(0,0)`, `BL(1,0)`, `TL(0,0)`, `TR(0,0)`) are wedged but
carry no load, so the shadow's load path is exactly `{f1, f2, f3, BL(0,1), BR(0,1)}` — A116's four
plus `BL(0,1)`, which A116 pins.

---

## T4 (coordinator). The common-tilt chain

### The spine, `s*(θ)` recomputed here (`results/spine_*.json`)

Minimum side with the shared tilt of `f1, f2, f3` PINNED, slots at their slot cells, SLSQP + a Newton
polish of the active set (worst gap ≤ 4e−16 at every tilt):

| Δθ | −45 | −40 | −30 | −20 | −10 | −5 | **0** | +5 | +10 | +20 | +30 | +40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| θ | 3.44 | 8.44 | 18.44 | 28.44 | 38.44 | 43.44 | **48.435** | 53.44 | 58.44 | 68.44 | 78.44 | 88.44 |
| s\*(θ) | 3.99681 | 3.98388 | 3.94602 | 3.91091 | 3.88972 | 3.90108 | **3.886746** | 3.89237 | 3.90248 | 3.93402 | 3.97287 | 3.97413 |

Rising on both sides of 48.435°, and **above s₀ = 3.877084 everywhere** — which is why the links away
from θ\* are cheap.

### The chain, `h = 1.25°`, `Δθ = 2.5°`, centres ±0.20, `f0` not in the boxes

**24 of 25 links CERTIFIED; the covered shared-tilt range is [2.185°, 62.185°] — 60.0° wide —
and the single refusal is a WALL CAP.**

`results/chain_BOTH_base_r0.20_h1.25_nof0.jsonl`, `..._summary.json`:

| | |
|---|---|
| certified offsets | 0, ±2.5 … −45 (every step down to the fundamental-domain edge) and +2.5 … +12.5 |
| first failure UP | Δθ = +15.0° (θ = 63.435°, s\* = 3.916630) — **wall cap** at 240 s, 0 witnesses, 0 unresolved, certified min 3.8770840 |
| first failure DOWN | none: the chain reached θ = 3.435°, where the next window would leave [0°, 90°] |
| cost | **3–36 s a link** (median 7 s); the whole 24-link chain in **≈ 7 minutes of one process** |
| certified minima | 3.8770846 … 3.8927509, all > s₀ |
| sampling | 1 000 draws a link, **0 hits** every time; Trump outside every link |

The wall cap at +15° is not a geometric limit: the same link certified in **12 s** in this attempt's
own smoke test from a differently warm-started spine row at the same s\*, so it is a
branch-order/relaxation-cost accident, and a retry at a 900 s cap is recorded in
`results/chain_*.jsonl`.

### The chain at `h = 10°`, `Δθ = 20°` (`results/chain_BOTH_base_r0.20_h10.00_nof0.jsonl`)

The same span in **5 links instead of 24**, and the first GEOMETRIC refusal:

| Δθ | θ | s\*(θ) | verdict | certified min | wall |
|---|---|---|---|---|---|
| 0 | 48.4351 | 3.886746 | **CERTIFIED** | 3.8770841 | 279 s |
| +20 | 68.4351 | 3.934015 | **CERTIFIED** | 3.8770857 | 110 s |
| −20 | 28.4351 | 3.910909 | **CERTIFIED** | 3.8770893 | 55 s |
| −40 | 8.4351 | 3.983878 | **CERTIFIED** | 3.8770874 | 285 s |
| **+40** | **88.4351** | 3.974134 | **REFUSED — LIVE-LOW WITNESS** | — | 4 s |

Covered shared tilt **[−1.565°, 78.435°] — 80.0° wide**, 0 sampling hits in every certified link.
The +40° link's tilt window is [78.44°, 98.44°], i.e. it straddles the axis-aligned direction, and the
witness is a **real partial packing of the nine squares of L ∪ P at side 3.864533665 < s₀** —
re-verified from scratch here (worst pair SAT gap −2.2e−16, worst wall gap 0.0,
`results/witnesses160.json`, drawn in `results/A160_witnesses.svg`). It bounds nine squares, not
eleven, so it says nothing about s(11) ≥ s₀; it says that neighbourhood is too big.

### Every witness, re-verified from scratch (`results/witnesses160.json`, `results/A160_witnesses.svg`)

**10 LIVE-LOW witnesses**, all re-verified here by an independent SAT + containment pass: worst pair
gap between −3.3e−16 and 0.0, worst wall gap 0.0, every side ≤ s₀ (3.820000000 to 3.875307252).
Sources: 1 from the h = 10° chain (Δθ = +40°), 6 from the r_xy probe, 3 from the tilt slices. Each is a
real partial packing of the nine squares of **L ∪ P**, not of all eleven, so **none of them touches
s(11) ≥ s₀** — they say the box that contains them is too big, and no amount of wall time closes it.

### The simultaneous-growth wall is GEOMETRIC at r_xy ≈ 0.25 (`results/chain_RXY_probe.jsonl`)

Growing all four centre boxes at once, tilt half-width 1.25°:

| r_xy | Δθ = −10° | Δθ = 0° | Δθ = +10° |
|---|---|---|---|
| 0.25 | CERTIFIED (7 s) | **CERTIFIED (72 s)** | **WITNESS (0 s)** |
| 0.30 | CERTIFIED (21 s) | **WITNESS (0 s)** | **WITNESS (0 s)** |
| 0.40 | WITNESS (1 s) | WITNESS (1 s) | WITNESS (1 s) |

These are the **first LIVE-LOW witnesses anywhere in the A116 / A151 / A160 line** (A151's every
refusal was a wall cap). They agree with A116's own grid, whose only witnessed failures are at
r = 0.30, and they settle a question A151 left open: **r = 0.20 is a geometric limit for growing the
boxes together, not a compute limit.** One square at a time (A151's ladder) is the only kind of growth
that can go further.

---

## T2. Growing along f0's slide

### What the slide's covering box is

In the s₀-anchored frame (`f0`'s anchor dilated by s₀/s\*), the box that just covers the dilated slide
is `dx = −0.098242`, `dy = +0.087115`, `x` half-width **0.1114**, `y` half-width **0.0987** — a box
0.223 × 0.198, offset diagonally from `f0`'s own anchor because the shadow's `f0` sits at u = 0.120 of
the slide, not at its midpoint. A160's `lib160` gives every free body an OFFSET asymmetric box for
exactly this reason (A151's `bodies_for` is symmetric about the anchor and cannot express it).

### The price of the f0 clause (`results/f0_box_price.json`) — measured BEFORE spending tree time

`f0` in `N` is one more clause in the hypothesis, so it can only ever REMOVE consumers:

| f0's box | in-N nodes | alive |
|---|---|---|
| A151-B, no f0 | **96** | **42** |
| + slide cover, tilt ±10° | 15 | 8 |
| + slide cover, tilt ±20° | 20 | 9 |
| + slide cover, tilt ±40° | 25 | 13 |
| + slide + 0.20 length, perp 0.05, tilt ±40° | 79 | 37 |
| + slide + 0.50 length, perp 0.20, tilt ±45° (x hw 0.502, y 0.468) | **96** | **42** |
| bigger still | 96 | 42 |

So the f0 clause is free only when it is vacuous, and it never adds a consumer.

### The ladder (`results/grow_F0.jsonl`, `logs/grow_F0*.log`)

| rung | box | verdict | reason | witnesses | unresolved | certified min | wall |
|---|---|---|---|---|---|---|---|
| START | A116 base + f0's slide cover (±10°) | **REFUSED** | **wall cap** | **0** | **0** | 3.8770844 > s₀ | 420 s |
| START (retry, larger cap) | same | see `logs/grow_F0b.out` | wall cap | 0 | 0 | — | 1500 s |

**No `N` containing `f0` was certified inside the cap, and no refusal was a witness.** Adding a fifth
free body roughly doubles the tree's cost (A116's base alone is 205 s), and since the consumer table
above says the clause is worth nothing until the box is ±0.5 — which is far more expensive again —
this direction is measured and closed, not merely unfinished.

---

## T3. Consumers and the N for A136's YES leaf

`results/consumer160.json` (control row reproduces A116's own 72 of 184 / 32 alive exactly):

| N | in-N k5_11-frame S02 nodes | of which ALIVE |
|---|---|---|
| A116 symmetric (0.2, 10°) — CONTROL, reproduces A116 exactly | 72 of 184 | 32 |
| A151-B certified (f1 grown) | 96 | 42 |
| A116 symmetric **+ f0's slide box** | 4 | 3 |
| A151-B **+ f0's slide box** | **15** | **8** |
| A160 common-tilt chain alone (union of 31 certified links) | 81 | 35 |
| UNION A151-B + the chain | 104 | 45 |
| A160 independent tilt slices alone (union of 22 certified slices) | 11 | 5 |
| UNION A151-B + the slices | 107 | 47 |
| **UNION A151-B + chain + slices — 54 certified box sets, THE YES LEAF** | **114** | **50** |
| *(reference ceiling)* A151-B with `f2`, `f3` tilt ±45° independently, as one box | 123 | 53 |

The 8 nodes the chain adds over A151-B: `Y0036_D03_D04`, `Y0231`, `Y0588`, `Y0642`, `Y0738_D02`,
`Y0738_D07`, `Y0930_D04`, `Y0930_D06`. The union is **+18 nodes / +8 alive over A151-B** and
**+42 / +18 over A116's symmetric N**, for ≈ 0.9 CPU-h of recorded tree time.

### Why the chain adds so little, and what does (`results/needed160.json`, `results/binding160.json`)

A chain link puts all three tilts in ONE window of width 2h, so its ceiling is the number of nodes
whose support tilt SPREAD is ≤ 2h:

| h | nodes with spread ≤ 2h | alive | …and also within ±0.20 in x, y of the θ\* anchors | alive |
|---|---|---|---|---|
| 1.25° | 63 | 27 | 63 | 27 |
| 2.5° | 74 | 33 | 73 | 32 |
| 5° | 91 | 40 | 87 | 39 |
| 10° | 124 | 53 | 109 | 50 |
| 20° | 150 | 56 | 118 | 52 |
| 45° | 184 | 62 | 121 | 53 |

Independent-tilt ceiling (position only, any tilt): r = 0.20 → 121/53, r = 0.30 → 140/57,
r = 0.40 → 167/62.

Binding coordinates over the **20 ALIVE nodes outside A151-B**: **`f2`/tilt 14, `f1`/y 11,
`f3`/tilt 10, `f1`/x 8, `f1`/tilt 8, `f2`/x 8, `f2`/y 6, `f3`/y 1** — and **9 of the 20 are blocked by
`f2`'s and `f3`'s tilts ALONE** (binding sets `{f3/t}` 3, `{f2/t}` 3, `{f2/t, f3/t}` 3). Those are
INDEPENDENT windows; a common-tilt chain cannot open them at any tilt range.

## T4(b). The INDEPENDENT tilt slices — and the finding that reframes everything

Since `f2`'s and `f3`'s tilts bind INDEPENDENTLY, the object that reaches those nodes is a product of
independent tilt slices, not a common-tilt chain: `f2`'s tilt in `[θ* + 20i ± 10]°`, `f3`'s in
`[θ* + 20j ± 10]°`, centres fixed at the θ\* anchors. The union over `(i, j)` IS the box with both
windows independently widened — a wide window the tree cannot close in one run is the union of narrow
ones it can.

`results/slice160.jsonl` (`f1` at A151-B's grown box) and `results/slice160_f1base.jsonl` (`f1` at
A116's own box — the control):

| slice | `f1` window | `f2` window | `f3` window | verdict | wall |
|---|---|---|---|---|---|
| d2 = +20 | **[8.44, 88.44]** (A151-B) | [58.44, 78.44] | [38.44, 58.44] | **REFUSED — WITNESS** | 100 s |
| d2 = −20 | [8.44, 88.44] (A151-B) | [18.44, 38.44] | [38.44, 58.44] | **CERTIFIED** | 184 s |
| d2 = +20 | [38.44, 58.44] (base) | [58.44, 78.44] | [38.44, 58.44] | **CERTIFIED** | 108 s |
| d2 = −20 | [38.44, 58.44] (base) | [18.44, 38.44] | [38.44, 58.44] | **CERTIFIED** | 17 s |
| d3 = +20 | [38.44, 58.44] (base) | [38.44, 58.44] | [58.44, 78.44] | **CERTIFIED** | 39 s |
| d3 = −20 | [38.44, 58.44] (base) | [38.44, 58.44] | [18.44, 38.44] | **CERTIFIED** | 48 s |

**The growth directions TRADE OFF against each other.** `f2`'s upward tilt slice is certifiable — but
NOT together with A151-B's grown `f1`: the witness that refutes the combination puts `f1` at 83.44°, a
pose only A151-B's ±40° window admits (`results/witnesses160.json`, side 3.869337946, re-verified,
worst pair gap −1.1e−16). With `f1` back at A116's own box, the same slice closes in 108 s.

**With `f1` at A116's own box, ALL EIGHT axis slices certify, with ZERO failures:**

| slice | `f2` window | `f3` window | verdict | wall |
|---|---|---|---|---|
| d2 = +20 | [58.44, 78.44] | [38.44, 58.44] | CERTIFIED | 108 s |
| d2 = −20 | [18.44, 38.44] | [38.44, 58.44] | CERTIFIED | 17 s |
| d2 = +40 | [78.44, 98.44] | [38.44, 58.44] | CERTIFIED | 58 s |
| d2 = −40 | [−1.56, 18.44] | [38.44, 58.44] | CERTIFIED | 38 s |
| d3 = +20 | [38.44, 58.44] | [58.44, 78.44] | CERTIFIED | 39 s |
| d3 = −20 | [38.44, 58.44] | [18.44, 38.44] | CERTIFIED | 48 s |
| d3 = +40 | [38.44, 58.44] | [78.44, 98.44] | CERTIFIED | 20 s |
| d3 = −40 | [38.44, 58.44] | [−1.56, 18.44] | CERTIFIED | 20 s |

so at `f1`'s own box **`f2`'s and `f3`'s tilt windows each extend over the WHOLE fundamental domain
[−1.56°, 98.44°] in eight links totalling 348 s** — the independent-tilt widening A151's single-knob
ladder capped on at ±20° is not hard at all once it is sliced.

**The whole slice record — 27 runs, 22 certified, 5 refused by witnesses, none capped:**

| f1's box | d2 | d3 | verdict | wall |
|---|---|---|---|---|
| A151-B grown | −40 | 0 | REFUSED (witness) | 146 s |
| A151-B grown | −20 | 0 | CERTIFIED | 184 s |
| A151-B grown | 0 | −20 | CERTIFIED | 188 s |
| A151-B grown | 0 | +20 | CERTIFIED | 211 s |
| A151-B grown | 0 | +40 | CERTIFIED | 137 s |
| A151-B grown | +20 | 0 | REFUSED (witness) | 100 s |
| A151-B grown | +40 | 0 | REFUSED (witness) | 185 s |
| A116 base | −40 | −20 / 0 | CERTIFIED | 88 / 38 s |
| A116 base | −40 | +20 | REFUSED (witness) | 5 s |
| A116 base | −20 | −40 / −20 / 0 / +20 / +40 | CERTIFIED | 7 / 40 / 17 / 2 / 4 s |
| A116 base | 0 | −40 / −20 / +20 / +40 | CERTIFIED | 20 / 48 / 39 / 20 s |
| A116 base | +20 | −40 / −20 / 0 / +20 / +40 | CERTIFIED | 24 / 22 / 108 / 188 / 36 s |
| A116 base | +40 | −20 / 0 | CERTIFIED | 102 / 58 s |
| A116 base | +40 | +20 | REFUSED (witness) | 5 s |

Two clean patterns. **With A151-B's grown `f1`, `f2`'s tilt may only move DOWN by 20°** — every other
`f2` slice is refuted — while `f3`'s may move ±20° and +40°; that is A151's own observation that `f2`
is the expensive square, now with a geometric reason instead of a wall clock. **At `f1`'s base box the
only refusals are the two corners where two squares are simultaneously near axis-aligned**
(`f2` −40 with `f3` +20, and `f2` +40 with `f3` +20), which is the same phenomenon as the +40° chain
link. The remaining corners of the 5 × 5 product were not run inside the cap; the record is resumable
(`slice160.py --skip-done`).

So the neighbourhood is **not** one growable box: it is a **union of differently shaped boxes**, each
certifiable in its own regime, and the union is exactly what the `N_boxes` disjunction is for. That is
the concrete correction to A151's "compute-limited, not geometry-limited" reading — single knobs from
the base were compute-limited; **compounding two grown knobs is geometry-limited**, and the witnesses
prove it in seconds.

### `N_boxes` format

`results/N_boxes160.json` is A119/A125's `N_boxes` layout with one entry per certified object and the
note that the file is a **LIST whose hypothesis is a DISJUNCTION** — a node inside ANY entry is killed
by the YES leaf. Each entry carries its own `tree_verdict` (certified min, sampling hits, Trump-inside,
seconds) and, for a chain link, its `offset_deg / tilt_deg / s_star / tilt_window / half_deg / r_xy`.
`code/gent160.py` re-emits any one entry through A133's `gen_local_t.py` + its independent rational
checker, imported unchanged with `BASE` re-pointed into this attempt (A151's technique), so the
moved-anchor objects are in the same frozen format A136 cites.
