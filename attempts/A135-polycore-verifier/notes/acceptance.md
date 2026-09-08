# T1 — what the frozen verifiers do with a core's half-side

A135, 2026-09-07. Read-only on both frozen files; measurements in `results/t1_cores.json`
(`code/t1probe.py`), the exact core in `code/exactcore.py`.

## The verdict, in one line

**Both frozen verifiers take `a` VERBATIM from the certificate and never recompute it, because
neither is given the parameter box at all.** The only check is `0 ≤ tm ≤ 1 and a > 0`. So a
certificate may carry ANY sound half-side today — no verifier change, no schema change — and the
soundness of `a` is entirely the EMITTER's obligation.

| verifier | sha256 | where `a` enters | what is checked |
|---|---|---|---|
| `verify_case.py` (A57/A53) | `521cb01f…` | `:707` `CoreH(_rat(c["kx"]), _rat(c["ky"]), _rat(c["tm"]), _rat(c["a"]))` | `:708-710` `if not (0 <= c.tm <= 1) or c.a <= 0: raise ValueError("bad core")` |
| `verify_param.py` v1 (A56/A96) | `0c58485c…` | `:539-541` `CoreP(akx, bkx, aky, bky, tm, a)` | `:542-543` the same two comparisons |

`verify_case`'s core entry does carry a `box` field (`caselp.Core.to_json` writes
`box=self.box.to_json()`), but as **floats**, and `load_certificate` never reads it: `grep box`
in the loader returns nothing. `verify_param`'s cores carry no box at all — its schema is
`akx, bkx, aky, bky, tm, a`. Neither verifier can therefore *check* a half-side against a box
even in principle; `core_exempt_frac` uses `a` only as a support half-width.

(The brief quotes v1's sha as `0c48485c…`; the file on disk is `0c58485c1a66…`. Same file, four
identical copies across A56/A96/A99/A100/A112.)

### Consequence, and the discipline A135 adopts

"The verifier trusts `a`" is not a licence, it is a relocation of the obligation. Everything A135
emits therefore certifies its own half-side **before writing it**, by A132's exact rational vertex
test applied to the four corners of `K(a)` (`exactcore.a_ok` → `polycore.vertex_ok`): sixteen
exact quadratic-nonnegativity decisions per box against the box's own OUTWARD-rounded tilt
interval `[t_lo(θ0), t_hi(θ1)]`. `exactcore.exact_a` finds the largest such `a` on a `2⁻⁴⁰` grid
by bisection — the bisection is a heuristic, the corner test is the proof — and it *first* certifies
the deployed `Box.core()` value, so a corpus core that failed the test would be reported rather
than silently repaired (none did). `verify_case_v3.py` re-runs the same test on every polygon and
on the square core it refines, so nothing downstream inherits trust from the emitter.

## (a) The PIN boxes — the exact core is 0.6 % bigger, and it is certifiable today

A pin box is `[x ± h] × [y ± h] × {θ = 0}` with `h = δ/√2 = 0.00707107`, δ = `1e-2`
(`tree57.build_children`, `--pin_delta 1e-2`). For a zero-tilt box the intersection of the unit
squares over the box is **exactly** the axis square of half-side `1/2 − h`. But `Box.core()` uses

    a = (1/2 − hd)/(1 + (t1 − t0)),   hd = q_up(half DIAGONAL of the centre box) = q_up(h√2) = δ,

i.e. it bounds the centre offset by the circumscribed disc radius instead of the actual axis
extent, losing exactly the `√2`:

| | half-side | area vs deployed |
|---|---|---|
| deployed `Box.core()` | **0.489999969** (= 0.49 − 3.1e−8) | 1 |
| `pinguard.tight_a` (float, T5′-only) | 0.492928932 | ×1.011991 |
| **A135 certified maximal, exact rational** | **0.492928902** = `33873816211/68719476736` | **×1.011991** |

The gain is `+0.00292893` per side, `δ(1 − 1/√2)`, and it is exactly A132's `0.49293` figure. The
certified value sits `3.0e−8` below the float `tight_a`, which is the outward-rounded tilt interval
`[0, 2⁻²⁴]` (θ ∈ [0, 6.8e−6°]) paying for itself — `Box.core()` widens the pin's tilt outward too,
so the *exact* core of the box as the corpus states it is very slightly under `1/2 − h`.

**The soundness gate is re-checked, not assumed.** `tree57`'s T23 gate is that the pin cores stay
pairwise disjoint, so the `budget = n − #cores` bridge still has `#cores` distinct witnesses.
Minimum L∞ slot separation is **1.000000** on both `k5_11` and `k5_16`; the pin-core disjointness
gap `min_pairs(max(|Δkx|,|Δky|) − 2a)` goes from **0.020000** (deployed) to **0.014142** (exact) —
still positive, gate intact, `2a = 0.985858 < 1`. `code/emit135.py` refuses to build a hypothesis
whose pin cores are not pairwise disjoint.

**Tested, not argued** (T1(a)'s "re-emit and run both frozen verifiers"): see `notes/certified.md`.
Two of the three in-vitro nodes certify TODAY under the frozen `verify_case.py` with exact cores
and nothing else changed, and one of them (`k5_11_interior_Y0871`) certifies with the exact **pin**
cores alone.

## (b) The CONDITIONED box — tight_a is nearly exact, and the polygon is where the rest lives

Same test on the three T2 boxes, at the box's own `(kx, ky, tm)`:

| node | tilt bin | `Box.core()` | `tight_a` (float) | **exact certified** | exact/`tight_a` | exact/`Box.core()` | area `K′`/`K(exact)` | area `K′`/`K(stock)` |
|---|---|---|---|---|---|---|---|---|
| `k5_11_…_Y0871` | tm 21.24° | 0.35660163 | 0.36388385 | **0.36466168** | **1.002138** | 1.022602 | **1.1427** | 1.1949 |
| `k5_11_…_Y1038` | tm 34.71° | 0.35660163 | 0.36199894 | **0.36316349** | **1.003217** | 1.018401 | **1.1207** | 1.1623 |
| `k5_16_…_Y0281_D03` | tm 71.34° | 0.42335785 | 0.43641917 | **0.43641911** | **0.99999984** | 1.030852 | **1.0478** | 1.1135 |

Three readings.

1. **`tight_a` is a good but not exact lower bound of the largest inscribed axis square**: it is
   short by 0.21 % and 0.32 % on the two level-1 boxes and exact to 1.6e−7 on the level-2 one.
   The looseness is the `h·M_c` term (`h` is the max half-WIDTH, but the two half-widths differ,
   and `M_c` is taken over the whole tilt range rather than jointly with the corner sign).
2. **The polygon still adds 5–14 % of area beyond the best axis square** — `K′/K(exact)` 1.048 to
   1.143 against A132's `K′/K(stock)` 1.11 to 1.19. So roughly **half** of A132's headline
   `area(K′)/area(K(a))` median 1.225 is recoverable inside the frozen schema (a bigger square) and
   half genuinely needs the polygon.
3. Certifying an exact core costs **0.08–0.09 s per box** (bisection on a `2⁻⁴⁰` grid, ~40 exact
   corner tests), against A132's 0.07 s for a whole polygon. Neither is a cost.

## What this changes

* The **pin** polygon core needs no verifier and no schema: it IS an axis square, it fits
  `{kx, ky, tm, a}`, and A132's own builder would only return a `1e-6`-shrunk copy of it. The
  channel A132 measured at **21 % of the K′-excluded dual weight on A57** is therefore available
  under the frozen verifiers today.
* The **conditioned box**'s polygon is not expressible as a square and does need the v3 clause —
  but roughly half its area gain is, again, free.
