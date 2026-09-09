# A160 — method: what each object is, how it was measured, and what it is NOT

Owner A160 (Opus engineer), 2026-09-08. READ-ONLY on every campaign and prior attempt; every file
written by this attempt is under `attempts/A160-s02-f0-slide/` except the two doc lines the brief
names, the registry row and the LOG entry.

## 0. A correction to the brief's premise, stated first because everything follows from it

**`f0` is not a body of A116's `N` at all.** `a116lib.LOADBEARING["S02"] = ("f1", "f2", "f3")` with
the comment *"f0 is the strut"*, and `a111lib.S02_LOADPATH = ("f1", "f2", "f3")` with *"f0 is the
strut/rattler"*. A116's `N` has four free boxes — `f1, f2, f3, BR(0,1)` — and five pins; `f0` and
`TR(0,0)` are simply absent from the certificate. So `f0` was not "never grown because the
forced-radius ordering put `f1` first": there was no `f0` knob to grow. Growing `f0` means **adding**
a fifth free body, which *strengthens* the theorem (more constraints) and *weakens* the hypothesis
(one more clause a node's support must satisfy) — the two move in opposite directions, and §4
measures both.

## 1. The polished shadow (`code/polish160.py`, `results/polish160.json`)

The gallery's S02 poses are printed to six decimals and have worst pair SAT gap **−2.9e−7**, which is
larger than the object being measured. They are refined in two stages — SLSQP on
`(s, the free centres, the common tilt)` with the seven slots pinned to their slot cells at `s`, then
a Newton (`least_squares`) solve of the ACTIVE contact system — to

* **s\* = 3.886746028606**, common tilt **48.435119375°**, worst pair gap **−3.3e−16**, 14 active
  contacts on eleven squares, 11 on the ten-square core.

Same solve with `f0` deleted: **s\*(core) = 3.886746028606**, identical to 12 digits. `f0` is a
rattler in the strong sense — *it does not set the side*.

## 2. The slide (`code/pocket160.py`, `code/f0slide.py`, `results/slide_exact.json`)

The eight signed separating-axis selections of a pair are AFFINE in the moving square's centre at a
fixed tilt, so the pair's forbidden centre set is an intersection of eight half-planes (a convex
octagon), and relaxing disjointness to `gap ≥ −eps` pushes each of the eight half-planes inward by
exactly `eps`. Hence

    FREE_eps(theta)  =  [h − eps, s − h + eps]^2  \  union_j OCT_j(theta, eps)

is an EXACT polygon, computed with shapely boolean ops on half-plane clips — **no grid, no buffer,
no penetration surrogate**, and the relaxation is in the same gap the certificate uses.

Why the exactness matters: at `eps = 0` the admissible set of `f0` has EMPTY INTERIOR, so an area
computation returns 0 and a grid of poses misses the set entirely (the first draft of `slide160.py`
did exactly that and reported "rigid"). The `eps → 0` ladder is what distinguishes the three
possibilities: a **pocket** (area → positive), a **slide** (area and width → 0 linearly in `eps`,
length → positive) and a **rigid point** (length → 0 as well).

*Not claimed:* an interval-arithmetic certificate of the slide. The slide is a measurement of the
polished float configuration (worst gap 3e−16), reported to the digits it is stable in; the
certificate objects in §3–§4 are the frozen A116/A133 machinery and are independent of it.

## 3. The common-tilt chain (`code/chain160.py`)

`s*(theta)` is recomputed here for the shared tilt of `f1, f2, f3` (the same SLSQP + Newton, tilt
PINNED, warm-started from the neighbouring link), so the chain's spine is this attempt's own data,
not a read of A106's picture. Link `k` is A116's selection tree over

* `f1, f2, f3` centred on their `s*(theta_k)` positions **dilated by `s0/s*(theta_k)`** (A116's
  anchoring rule), half-widths `r_xy`, tilt interval `[theta_k − h, theta_k + h]` — the three moved
  TOGETHER;
* `BR(0,1)` at its slot cell at `s0`, `±r_xy`, `±10°`; the five A57 slack-core pins;
* optionally `f0`'s slide-cover box.

`shadow_selections` is re-derived from the link's OWN configuration, so the tree branches on the
contacts that link actually has. Links are walked outward from `theta*` alternately up and down, and
a step whose tilt window would leave the fundamental domain `[0°, 90°]` is skipped.

Acceptance is A151's: `dead` **and** `capped = False` **and** 0 sampling hits. `capped = True` is
recorded as a wall-clock limit with NO geometric claim; a refusal with LIVE-LOW witnesses is a
geometric limit and the witnesses are kept verbatim.

**A link is not the same object as A116's `N`.** The base `N` fixes the centres at the `theta*`
configuration and lets the tilt run ±10°; a link fixes a narrow tilt and moves the centres with it.
Neither contains the other, which is why the `N_boxes` file is a LIST and the hypothesis a
DISJUNCTION.

## 4. Consumers (`code/consumer160.py`)

A116's test verbatim (A107 `struct_op` into the shadow frame, an injection of the TILTED free boxes
into DISTINCT support squares, tilt compared mod 90° about the box anchor, `BR(0,1)` not matched),
with two extensions: `f0` may be one of the injected boxes, and an entry may be a LIST of box sets
(a node is a consumer of the union if it is a consumer of any link).

Control: A116's symmetric `(0.2, 10°)` returns **72 of 184** k5_11-frame S02 nodes, **32 alive** —
A116's and A151's own numbers, reproduced exactly.

## 5. Process discipline

The box was at **16–19 lab python processes throughout** (A136, A137, A149, A156 and at least one
other attempt). This attempt held **at most two** of its own, both `BelowNormal` with affinity
`0xFFFF`, and started the second only after the count fell back to 17; the analysis runs of §1–§2 are
seconds-to-minutes single processes. Wall, not CPU, was the binding constraint on how much of the
4 CPU-h cap could be spent.
