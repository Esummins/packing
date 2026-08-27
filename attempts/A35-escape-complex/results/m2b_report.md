# A35 / M2-delta — the (W′) menu-complete wedge on basis v2

Code: `code/m2b_lib.py` (the (W′) row sets, escape cone, Motzkin barrier),
`code/m2b_value.py` (the (V′) value barrier), `code/m2b_seeds.py`,
`code/m2b_queue.py`, `code/m2b_global.py`, `code/m2b_check.py` (standalone
re-checker). Data: `results/m2b_seeds.json`, `m2b_queue.json`, `m2b_global.json`,
`m2b_certs/` (288 certificates). Rigour tags as in M1/M2, plus `[LP]` = float64
HiGHS. Single process.

---

## 0. Headline

> **Both M1b seeds die at first order, from the two auxiliary dist rows alone.**
> **And the same two rows restore the v2 uniform multiplier floor from 0 to
> 0.0205, which yields a single stratum-INDEPENDENT (V′) certificate per
> (variant, selection): 128 certificates cover the entire 2⁴² break-set lattice.
> M1b's 25 050-element work queue does not need 25 050 certificates — it needs
> 64 (the two meaningful variants).**

The queue never had to be walked. It was an artefact of the basis repair having
dropped two permanently valid, active inequality rows.

---

## 1. Task 1 — seed kills

**The aux rows.** `a0 : d²(c0,c1) − 1 ≥ 0`, `a1 : d²(c0,c3) − 1 ≥ 0`. Valid for
*every* pair of interior-disjoint unit squares (incircles of radius ½ give
`|c_i − c_j| ≥ 1`), and M1b certified both **active** at ẑ (centre distance² =
exactly 1). They are permanent inequality rows, never stratification
coordinates, so every escape direction must satisfy `∇a·v ≥ 0`.

**Verdict: the lead's correction is confirmed. Both seeds die from `A_aux`
alone; the tied dominance rows are not needed.**

Kernel snapshot, `v` oriented so the broken gaps *open* (`[NUM]` kernel,
`[IV]` gradients):

| seed | variant | dof | e_s·v | broken rates | `d²(c0,c1)` rate | `d²(c0,c3)` rate |
|---|---|---|---|---|---|---|
| `{0,2}` | conj/selx/sely | 1 | 9.0e-17 | +0.8165, +0.8165 | **−0.816497** | **−0.816497** |
| `{4}` | selx | 1 | 1.1e-16 | +0.8165 | **−0.816497** | 0 |

Nested row-set sweep, **every** selection in the tie menu, no early stop:

| seed / variant | rows: none | + aux | + aux + dom |
|---|---|---|---|
| `{0,2}` conj | 60/64 dead | **64/64** | 64/64 |
| `{0,2}` selx | 28/32 dead | **32/32** | 32/32 |
| `{0,2}` sely | 28/32 dead | **32/32** | 32/32 |
| `{4}` selx | 28/32 dead | **32/32** | 32/32 |

(The "none" column is not 0/32 because most *selections* already kill the cone;
the base selection — the one M1b used — is among the survivors, which is why
M1b saw the seed as alive.)

**Certificates.** 160 IV-verified Motzkin-dual (W′) certificates, one per
(seed, variant, selection) — the kill must hold for the whole menu, so the
certificate must too.

| | value |
|---|---|
| certificates | **160**, all selections of all four (seed, variant) pairs |
| `α_min` (self-stress floor on B ∪ AUX) | **1.0** (‖ω‖∞ = 1) |
| `h_W` | **7.891e-4 … 1.547e-3** = **1.58 … 3.09 × r_N** |
| `ε_w = ‖A_extᵀω‖₁` | ≤ 2.6e-60 |
| `Hbar_W` | ≤ 56.0 |
| `x*` (pinning radius) | ≤ **2.31e-58** ≪ r_N |
| cost | 29–59 s per (seed, variant) full menu |

**No second-order fallback was required.**

---

## 2. Task 2 — queue re-collapse

### Effect 1 (the queue can GROW): cone-aliveness with the extended generators

Aux and dominance rows are ordinary `g ≥ 0` rows; in FJ stationarity they carry
`λ ≥ 0` and therefore **add generators** to the cone test. Measured on `Z0` (the
rows whose singleton break set stays cone-alive — M1b generates the whole alive
family from `Z0`):

| variant | Z0 without aux/dom | + aux | + aux + dom | rows in variant |
|---|---|---|---|---|
| conj | 20 | 20 | **21** | 42 |
| selx | 17 | 18 | **20** | 41 |
| sely | 18 | 18 | **20** | 41 |

So the alive family really does grow (by roughly a factor 2–8 in the worst
case), exactly as the sign discipline predicts. **This is measured, not
assumed, and it does not matter for the conclusion** — see §3: the (V′)
certificate is stratum-independent, so it covers the enlarged family too.

### Effect 2 (the queue SHRINKS): (W′) over the whole 25 050 queue

Full tie-menu sweep, every member, per variant:

| variant | queue | (W′)-dead | (W′)-alive | killed by the C0 fast path | wall time |
|---|---|---|---|---|---|
| conj | 17 625 | 15 600 | **2 025** | 0 | 855 s |
| selx | 12 375 | 9 000 | **3 375** | 0 | 281 s |
| sely | 5 625 | 3 600 | **2 025** | 0 | 147 s |

**Honest number: (W′) alone does NOT collapse the queue to dozens.** It kills
77 %, and 7 425 (variant, break-set) pairs survive it. The `C0` fast path
(selection-independent rows 0..35 plus aux) fires on **0 %** — it drops up to
six equalities, so its kernel is far too big to be pinched by the aux rows
alone. Both facts are reported rather than hidden.

### What actually closes the queue: the (V′) universal certificate

Every (W′) survivor — and every other break set — is covered by §3.

> **New TRUE-survivor count after (W′) + (V′): 0.**

---

## 3. The repaired uniform floor, and the universal (V′) certificate

M1b's §2 headline was that on v2 the uniform multiplier floor collapses to 0,
with rows 0 (`W0c0[x=0]`) and 2 (`W0c1[y=0]`) *forced* to λ = 0 over the whole
polytope — which is exactly why the seeds were first-order flat and unkillable.

**That collapse is an artefact of dropping the two dist rows.** Re-measured
`[LP]`, then certified `[IV]`:

| | conj | selx | sely |
|---|---|---|---|
| uniform floor over ALL rows, **without** aux | 0 | 0 | 0 |
| uniform floor over ALL rows, **with** aux | **0.02046** | **0.02676** | **0.02046** |

uniformly over every selection in every tie menu. theory.md (A)/Consequence 1 is
therefore **repaired on v2** — the constant is 0.0205 rather than v1's 0.047644,
but it is strictly positive on *all* rows, including 0 and 2.

**The certificate.** ω with `A_extᵀω = e_s`, `ω_r ≥ α_min > 0` on every v2 row
of the variant *and* both aux rows, `ω = 0` on rows outside the variant and on
all dominance rows. With `Φ(z) = s − Σ_r ω_r g_r(z)`, for **any** feasible
z ∈ box(ẑ, h) — no break set, no stratum, nothing selected:

* `G(z) ≥ T(h) := (ε₀ + ε_w h + Hbar h²)/α_min` ⟹ `s(z) ≥ ŝ` directly; else
* every row of A22's 34-row Krawczyk system lies in `[0, T(h) + g_max]`, so
  `‖z − ẑ‖∞ ≤ κ(T + g_max)/(1 − β) =: ψ(h)`.

If `ψ(h) < h` the dichotomy **iterates** (case 2 re-enters at the smaller
radius), the radii fall to `x* ≪ r_N`, and A22's theorem finishes.

| | value |
|---|---|
| certificates | **128** (64 conj + 32 selx + 32 sely); **64** for the two meaningful variants |
| all selections certified | yes (128/128) |
| `α_min` | ≥ **0.020457** |
| `h_G` | **1.270e-4 … 2.246e-4** = **0.25 … 0.45 × r_N** |
| `Hbar_W` | ≈ 7.64 |
| `x*` | ≤ 1.07e-56 |
| covers | every break set in the 2⁴² lattice, at once |
| cost | 283 s (conj) + 135 s (selx) + 135 s (sely) |

**Trade-off, stated plainly.** (W′) is per-stratum and reaches 1.6–3.1 × r_N;
(V′) is universal but reaches only 0.25–0.45 × r_N, because `A_extᵀω = e_s`
fixes ω's scale (‖ω‖₁ ≈ 4.4, α_min ≈ 0.02) whereas the (W′) self-stress can be
normalised freely (α_min = 1). The composed basin is `min = 1.27e-4 = 0.25 r_N`
unless one pays per-stratum for the wedged part.

---

## 4. Task 3 — sampled per-stratum re-derivation (the price of NOT using §3)

30 random queue members, full tie menu each (32 selections for selx/sely, 64 for
conj; a stratum is certified only when every selection is).

| | value |
|---|---|
| (W′) certified | **25 / 30** (83 %) — the 5 failures are strata where no self-stress is positive on all of `B ∪ AUX`; they are (V′)-covered |
| (W′) cost per stratum (full menu) | median **44.2 s**, max 91.0 s |
| (V′) floor screen per stratum | median **0.63 s**, positive on **30/30**, floor ≥ **0.0544** |
| `h_W` reached | 6.60e-4 … 1.27e-3 = **1.32 … 2.53 × r_N** |
| reaching v1's radius 69/32000 | **0 / 25** — the v2 constants are strictly worse than v1's |
| `Hbar_W` max | 68.9 |  
| `ε_w` max | 6.2e-46 |

Extrapolated, per-stratum (W′) re-derivation of the 25 050 queue would cost
≈ 25 050 × 44 s ≈ **12.8 CPU-days**, and would still leave ~17 % uncovered.
The universal (V′) route costs **553 s** and covers everything. That is the
whole argument for §3.

---

## 5. Corrections to earlier M2 output

* `m2_inflation.py` gained variants **C** (iterated dichotomy, condition
  `ψ(r) < r`) and **BC** (`B or C`, the full sound condition, now reported as
  `r_1`). **Neither B nor C implies the other**: below r_N, C is *stricter*;
  above r_N it is weaker. Every v1 radius is below r_N, so C buys nothing there
  (refined crossover 2.75e-4 vs B's 3.5e-4) and **`r_1` is unchanged at 2e-4**.
  The iteration is what makes the v2 certificates work at all. `m2_check_inflation.py`
  updated; ALL CHECKS PASS.
* A soundness bug was found **by the new re-checker** and fixed before
  publication: the first draft gave the tied **dominance rows a positive ω**.
  Dominance rows are *selection conditions*, not inequalities valid on all
  packings, so a positive coefficient in a barrier is unsound. They now carry
  **ω = 0 exactly** in both certificate families (asserted by the re-checker)
  and appear only in the *wedge test*, where the menu argument justifies them.

---

## 6. Re-checker

`code/m2b_check.py` — mpmath.iv + fractions + json only (plus the sibling
`m2_check_inflation.py` jet code; no strata_lib / t3lib / a22lib / numpy). It
does **not** trust the producer's row list: it rebuilds all 50 extended rows
from A22's `krawczyk_cert.json` constraints 0..35, the v2 repair table
transcribed from M1b's documented `basis_v2_definition`, A22's constraints
36–37 as the aux rows, and the selection's dominance rows.

> **288 certificates, 4 608 checks, ALL PASS.**

Corruption controls, each must fail and does: `omega-sign`, `omega-perturb`,
`h-big`, **`drop-aux`** (zeroing the two aux weights blows `ε_w` from 9.7e-45 to
0.229 — the aux rows are load-bearing, not decoration).

---

## 7. Gaps / caveats

* **M2b-a (the big one, inherited).** The six repaired v2 rows 36..41 put their
  contact corner at an edge **endpoint**, so their tangential (dominance) margin
  is 0 at ẑ and **negative on every box of positive radius** (measured: −1.5e-3
  at h = r_N, −6.5e-3 at h = 2.16e-3; the C1-3 alternative branch is −1.0065,
  i.e. a full unit off the edge). Those rows are therefore **not certified to be
  the dominant description of their contact on any box**, and the weaker
  condition the barrier actually needs — that the owner edge *separates* the
  pair on the box — **is not discharged either**. This is M1b §7 / theory.md G5,
  **inherited, not introduced**: every v2 result carries the same dependence,
  M1b's included. A22's rows 0..35 *are* certified (tangential margin ≥ 0.0148
  on every certificate's box). The re-checker reports both numbers separately
  and refuses to conflate them.
* **M2b-b.** The (W′) wedge verdict is `[NUM]` (it uses kernels of `A_M`).
  Nothing rests on it: the Motzkin dual barrier is `[IV]` + exact rational and
  uses only `rank(A) = 34`, which M1b certified `[RFP]`.
* **M2b-c.** The union of (W′) survivors across variants is reported per variant
  (2 025 / 3 375 / 2 025, exact); the JSON stores only the first 400 of each, so
  the *distinct* union count is bounded between 3 375 and 7 425 and was not
  computed exactly. It does not affect the conclusion (all are covered by §3).
* **M2b-d.** Everything is at ẑ with a box; no continuation along strata. The
  aux rows are valid globally, but their *activity* is a fact about ẑ only —
  which is all the certificate uses.
* **M2b-e.** `conj` is a reference variant only (M1b): its strata are partly
  geometrically meaningless. The meaningful count is **64 certificates**.
* **M2b-f.** Nothing here produces `σ ≥ ŝ + δ_stop`; theory.md G1 (the ridge
  handoff) is untouched, and the composed basin is still capped at
  `0.25 × r_N` by the (V′) radius.

---

## Files

* `code/m2b_lib.py`, `code/m2b_value.py`, `code/m2b_seeds.py`,
  `code/m2b_queue.py`, `code/m2b_global.py`, `code/m2b_check.py`
* `results/m2b_seeds.json`, `results/m2b_queue.json`, `results/m2b_global.json`
* `results/m2b_certs/` — 160 `Wp_*.json` + 128 `G_*.json`
* `results/m2b_report.md` — this file
