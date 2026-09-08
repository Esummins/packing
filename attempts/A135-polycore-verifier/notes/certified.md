# T2 — A132's three in-vitro kills, certified

A135, 2026-09-07. Records: `results/emit135_s{0,1}.jsonl` (frozen-verifier arms),
`results/emitpoly135.jsonl` (v3 arm), certificates under `certs/`, drivers
`code/emit135.py` / `code/emitpoly135.py`. Nothing was written into any campaign; no shard was
launched; A57's PAUSE sentinel was reported and A135 watched its own (PAUSED.md §7a scoped
sentinel).

## Result — 3 of 3, and two of them need no verifier change

| node | L | A132 axis τ | A132 poly τ | A135 arm that certifies | τ (first solve) | verifier | LP wall | verify wall | rounds |
|---|---|---|---|---|---|---|---|---|---|
| `k5_11_interior_Y0871` | 1 | 5.000 | 4.000 | **`expin`** — exact **pin** cores only | 4.1667 (cap) | **frozen `verify_case.py`** `521cb01f…` | 656 s | 21 + 25 s | 2 |
| `k5_16_interior_Y0281_D03` | 2 | 5.000 | 4.000 | **`exall`** — exact cores on every box | 4.0000 | **frozen `verify_case.py`** | 36 s | 0.5 s | 1 |
| `k5_11_interior_Y1038` | 1 | 5.000 | 4.500 | **`poly`** — exact cores + `polycores` on the conditioned box | 4.5000 | **`verify_case_v3.py`** | 377 s | 20 s | 1 |

**Every one of A132's three "LP-dead under polygon core, certificate pending" nodes now has a
certificate, and two of the three are certified by the FROZEN verifier with nothing changed but
the half-side written into the `cores` field.** 2.6 CPU-h across the six frozen-arm solves plus the
v3 arm and its replay.

`Y0871`'s two arms hit the 600 s LP cap unconverged, so their τ is a lower bound and A124's "CAP
is never a verdict" applies — **to the LP**. It does not apply here, because the verdict is not the
LP's: the emitted rational measure was checked by the frozen verifier, which proves
`mu(Q) ≥ 1` on every non-exempt box exactly, and `total < budget` is an inequality on rationals.
An unconverged LP can only fail to certify; it cannot certify wrongly. (`Y0871` needed one
witness-feedback round in each arm; the second round's re-solve raised the certified total from
4.12 to 4.80667 in `exall` and from 4.29167 to 4.3775 in `expin`, still under budget 5.)

`Y0281_D03` and `Y1038` reproduce A132's polygon-arm τ exactly (4.000 and 4.500), which is the
independent confirmation that the two implementations compute the same thing.

## The arms, and what each one isolates

* **`stock`** — the deployed `Box.core()`. Not re-run: A132's axis arm converged at τ = 5.000 for
  all three, reproducing the campaign's stored verdict.
* **`expin`** — the exact certified core on the five PIN boxes, conditioned box unchanged.
* **`exall`** — the exact certified core on every box.
* **`poly`** — `exall` plus A132's certified 16-gon `K′(B)` on the conditioned box, carried in the
  new `hypotheses.polycores` field.

Full first-solve τ table (`(cap)` = the 600 s cap stopped the LP, so τ is a lower bound;
`NO-KILL` means τ ≥ budget and no certificate was attempted):

| node | `expin` τ | `exall` τ | `poly` τ |
|---|---|---|---|
| `Y0871` | **4.166667 (cap) → PASS** | **4.000000 (cap) → PASS** | — (already certified) |
| `Y0281_D03` | 5.000000000000025 conv, NO-KILL | **4.000000 conv → PASS** | — (already certified) |
| `Y1038` | 5.000000000000003 conv, NO-KILL | 4.999999999999987 conv, NO-KILL | **4.500000 conv → PASS (v3)** |

Read against A132's attribution arm, this sharpens it:

* `Y0871`'s kill lives **entirely in the pin cores**, and entirely in the part of them that is an
  axis square — A132 could not decide this (its `polybox` arm was unconverged at 4.385).
* `Y0281_D03` needs the conditioned box too, but only its **best inscribed square**, not its
  polygon: `exall` kills at 4.000, matching the full polygon arm.
* `Y1038` is the one that genuinely needs the polygon. `exall` lands at
  **τ = 4.999999999999987** — a knife edge, i.e. the axis core gets essentially all the way and
  the last 0.5 comes from the 12 % of area (`K′/K(exact)` = 1.1207) that no square can hold.
  A132 attributed this node's kill to the pins; the finer split is: pins **and** the conditioned
  box's polygon, neither alone.

## The v3 certificate and its clause

`certs/k5_11_interior_Y1038__poly.json` is a `case-measure-certificate-v1` with 6 cores (budget
5 = 11 − 6) and **one `polycores` entry**: a 16-vertex rational polygon on the conditioned box,
area 0.590938 against the exact square's 0.527551 (×1.1201), carrying the box as
`{x0, x1, y0, y1, t0, t1}` in exact rationals.

Box-tree line on the PASS: `boxes = 184584, covered = 54430, vacuous = 0,`
**`exempt = 37894 (core 36354, nofam 0, poly 1540)`**`, split = 92260, exact atom checks = 95535,`
`max depth = 39, time = 19.6 s`. So the new clause discharged **1,540 of 37,894 exempt boxes
(4.1 %)** — those are exactly the boxes the frozen core clause could not take, and they are what
the kill rests on.

**The frozen verifier on the SAME certificate** (`emitpoly135` runs it deliberately):
**rc = 1, FAIL** in 10.2 s — `boxes = 170365, exempt = 37390 (core 37390, nofam 0)`,
`8 witness boxes at depth 56: 5 HOLES` (a placement with exact mass < 1). So "this kill needs v3"
is a measurement, not a claim: without the 1,540 polygon exemptions the node's mass is genuinely
short, and the frozen verifier says so with real holes rather than undecided boxes.

**Replay — machine-independent.** `verify_case_v3.py --replay` re-verifies with **no float
pre-filter anywhere** (neither v1's atom shortlist nor the polygon pre-filter) in **one process**,
so every decision is taken by exact integer/Fraction arithmetic and the verdict cannot depend on
the FPU, the numpy build, or the process count. **rc = 0, PASS in 153.3 s**, and the box tree is
*identical* to the float-shortlisted run —

    boxes 184584  covered 54430  vacuous 0  exempt 37894 (core 36354, nofam 0, poly 1540)
    split 92260  max depth 39

— with only `exact atom checks` differing (6,154,178 against 95,535), which is exactly what
removing the shortlist should change and nothing else. 7.8× the wall for a verdict that depends on
no floating-point arithmetic at all.

## v3 is v1 on a `polycores`-free certificate — measured, not asserted

`code/regress135.py`, A117/A96's v2 discipline applied to the third disjunct: **24/24 certificates
identical — verdict AND box-tree statistics** (`boxes`, `covered`, `vacuous`, `exempt`,
`exempt_core`, `exempt_nofam`, `split`, `exact_atom_checks`, `max_depth`, `witnesses`), including
the two rc = 1 cases, where v1 and v3 fail identically. `results/regress135.json`.

That is stronger than a verdict match: it says the box tree is walked in the same order with the
same decisions. It is what one should expect, because **v3 does not copy the frozen file — it
imports it** (`import verify_case as vc`, `class VerifierV3(vc.Verifier)`), so `imul4`,
`trig_int`, `box_trig`, `atom_inside_int`, `vacuous_int`, `clip_int`, `core_exempt_frac`,
`nofam_exempt`, `covered`, `make_witness`, `run` and the mass arithmetic are literally the same
code — the discipline `verify_param.py` states for its own reuse. The frozen files are
byte-identical (`521cb01f…`, `0c58485c…`).

## The trust story of the new clause

The emitter's polygon is untrusted data. Before any box is discharged, `PolyCoreH.__init__`
re-runs, in exact rationals:

* **(P1)** every listed vertex lies in `Q(c, θ)` for every `(c, θ)` in the entry's own rational box
  — the two quadratics of A132 spec §1, at the four corners of the centre rectangle, for both edge
  normals, decided exactly (`point_in_all_poses`, written from scratch in the verifier, not
  imported from `polycore.py`);
* **(P2)** the four corners of the SQUARE core the entry refines (`cores[core]`) pass the same test
  against the same box.

(P2) is the step A132's spec leaves implicit and it is what binds the polygon to a hypothesis the
certificate actually declares: the square core and the polygon are then two cores of the SAME box,
so the polygon inherits the square's bridge verbatim. A failing entry is a **hard reject (exit 2)**,
not a warning. Also checked: convexity and orientation of the vertex list, `3 ≤ |V| ≤ 64`,
`0 ≤ t0 ≤ t1 ≤ 1`, `core` in range.

## Soundness gates re-checked at every emission

* **Half-sides are certified before being written.** `exactcore.exact_a` certifies the *deployed*
  `Box.core()` value first (so a bad corpus core would be reported, never silently repaired), then
  bisects upward on a `2⁻⁴⁰` grid, and asserts the final value against the exact corner test.
* **Pin cores stay pairwise disjoint** (A57's T23 gate for `budget = n − #cores`):
  gap 0.020000 → **0.014142**, positive, `2a = 0.985858 < 1`, minimum L∞ slot separation 1.000000.
  `ExactHyp.__init__` raises rather than emitting a hypothesis that fails it.
* **The LP filter and the certificate read the same core objects.** `caselp.make_certificate`
  rebuilds the `Hyp` from the box json and would have silently discarded the substitution;
  `emit135.make_cert` takes the live `Hyp` instead and is otherwise the frozen emitter character
  for character.

## Sampled controls (`code/check135.py`, `results/check135.json`)

A96/A132's discipline — every exact predicate gets a drawn → tested → hits line. All on the
16-gon that `Y1038`'s certificate actually carries.

* **A, the polygon itself.** 20,000 poses drawn uniformly in the hypothesis box → **320,000
  (vertex, pose) tests → 0 violations** of `|R(−θ)(v − c)|∞ ≤ 1/2`; max observed 0.499543. A hit
  here would mean the exact (P1) test is wrong.
* **B, the exemption clause.** 20,000 random 4-D sub-boxes → `polycore_exempt_frac` accepted
  **10,067** → 20 poses each → **201,340 (pose, polygon) tests by an INDEPENDENT float SAT written
  from scratch in `check135.py` → 0 unsound exemptions.** This is the failure that would break a
  certificate, and it does not occur.
* **C, conservativeness.** Of the 9,933 rejected sub-boxes, **477 (4.8 %)** have every sampled
  pose meeting the polygon — the clause is one-sided, as specified (outward interval arithmetic,
  left sides rounded up and right sides down), and the test is not vacuous.

## The honest limit, restated

A132's caveat stands and A135 does not touch it: **three converged pairs, on nodes selected for the
largest offending weight, is not a rate.** What A135 adds is that the certificate cost of the
lever is now known — the frozen path is free, and the v3 path costs 20 s of verification on a node
whose LP already cost 377 s.
