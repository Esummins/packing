# A36 — the two levers: L1 discharged, L2 optimised, composed reach 7.56 × r_N

Code: `code/a36_lib.py` (basis v3 + branch axes + the (V′) machinery),
`code/a36_l1.py` (L1 interval checks), `code/a36_reach.py` (L2 bisection +
inner LP + pin-basis search), `code/a36_emit.py` (certificate emitter),
`code/a36_check.py` (**standalone** re-checker, no producer libs).
Data: `results/a36_l1.json`, `a36_basis_v3.json`, `a36_reach.json`,
`a36_certs/` (17 certificates). Reuses A35 (`strata_lib`, `m2_lib`) and A30
`t3lib` read-only via `sys.path`; A29 untouched. Single process, ~12 min wall.
Rigour tags as in A35: `[IV]` mpmath.iv dps 60, `[LP]` float64 HiGHS.

---

## 0. VERDICT

> **h\* = 3779/1 000 000 = 3.779e-3 = 7.558 × r_N  >  r_N = 5e-4.  YES.**
> The composed escape-complex theorem **strictly dominates A22** by a factor
> 7.56 in radius. The hybrid fallback L2(d) was **not run** (not needed).

> **And the decisive lever was neither L1 nor the pin basis.** It is a
> sharpening of the *pinning* step of the (V′) chain — the "max-form" of §3 —
> which alone lifts the radius by **11.4×**. L1 + basis v3 are sound, cheap and
> certified, but they buy only **+2.4 %**: a branch-free barrier supported on
> A22's own rows 0..35 plus the two aux dist rows already reaches
> **3.6935e-3 = 7.39 r_N**. This is reported as the headline because it is the
> honest attribution.

---

## 1. Task 1 — BASIS v3

44 geometric rows + 2 aux + 24 alternative corner rows = **70 extended
positions** (`results/a36_basis_v3.json` has the full table).

| pos | content |
|---|---|
| 0–35 | A22 `krawczyk_cert.json` constraints 0..35, verbatim |
| 36–41 | v2's `F0-1a, F0-1b, F0-3a, F0-3b, C1-3x, C1-3y` |
| **42 `B13x'`** | **NEW** — owner sq3 **right** edge (e=1) vs corner 3 of sq1 |
| **43 `B13y'`** | **NEW** — owner sq1 **top** edge (e=2) vs corner 1 of sq3 |
| 44, 45 | aux dist rows `a0 = d²(c0,c1)−1`, `a1 = d²(c0,c3)−1` (= A22 36, 37) |
| 46–69 | the other three corner rows of each of the 8 branch axes |

All in `t3lib` `sep_row(o, e, p, k)` language. `[IV]` at ẑ:

| row | `\|g(ẑ)\|` |
|---|---|
| `B13x'` (42) | **1.556e-61** |
| `B13y'` (43) | **2.334e-61** |

both **< 1e-59** as required. (For reference the two aux rows are exactly 0 and
the six v2 rows are ≤ 2.34e-61.)

**Per-branch corner-row sets** (`axis_corner_positions` / `axis_rows`, exposed
to the emitter; L1.1 makes all four valid on the branch simultaneously):

| ax | name | (owner o, edge e, other p) | corner→position | active at ẑ |
|---|---|---|---|---|
| 0 | `A01a`  | (0, 1, 1) | 0→46, 1→47, 2→48, **3→36** | k=0, k=3 |
| 1 | `A01b`  | (1, 3, 0) | 0→49, 1→50, **2→37**, 3→51 | k=1, k=2 |
| 2 | `A03a`  | (0, 2, 3) | **0→38**, 1→52, 2→53, 3→54 | k=0, k=1 |
| 3 | `A03b`  | (3, 0, 0) | 0→55, 1→56, 2→57, **3→39** | k=2, k=3 |
| 4 | `B13x`  | (1, 3, 3) | 0→58, **1→40**, 2→59, 3→60 | k=1, k=2 |
| 5 | `B13x'` | (3, 1, 1) | 0→61, 1→62, 2→63, **3→42** | k=0, k=3 |
| 6 | `B13y`  | (3, 0, 1) | 0→64, 1→65, 2→66, **3→41** | k=2, k=3 |
| 7 | `B13y'` | (1, 2, 3) | 0→67, **1→43**, 2→68, 3→69 | k=0, k=1 |

Exactly **two** corner rows per axis are active at ẑ (the "tie pair" of M1b §7);
the other two read exactly 1 and are excluded from every barrier because a
loaded row with `g(ẑ) = 1` would put `ε₀ ≈ 1` into the dichotomy threshold.
**54 of the 70 positions are active**; the usable set of a variant is
36 + 2 + 6 = **44 rows** — the "44" of the brief, arrived at from the other end.

16 variants = 2 (contact (0,1)) × 2 ((0,3)) × 4 ((1,3)).

---

## 2. Task 2 — L1 interval checks  `[IV]` dps 60

**The check actually run** (it subsumes both L1.4(i) and L1.4(ii)): for each of
the 16 (owner, edge, other) combinations L1.2 declares impossible, exhibit a
**corner k** with `sup_box g_{e,k} < 0`. Since the true axis gap is
`min_k g_{e,k} ≤ g_{e,k}`, one strictly-negative corner kills the axis on the
whole box. Centre-order bounds are reported alongside as diagnostics.

| h | killed-axis min margin | A22 0..35 tangential | A22 depth+½ | all L1 |
|---|---|---|---|---|
| 5.0e-4 | 0.998499 | 0.018996 | 0.997857 | ✔ |
| 8.0e-4 | 0.997598 | 0.017789 | 0.996571 | ✔ |
| 1.0e-3 | 0.996997 | 0.016984 | 0.995713 | ✔ |
| **1.6e-3** | 0.995192 | 0.014571 | 0.993141 | ✔ |
| 2.5e-3 | 0.992481 | 0.010952 | 0.989282 | ✔ |
| 3.689e-3 | 0.988892 | 0.006171 | 0.984183 | ✔ |
| **3.779e-3** (= h\*) | 0.988620 | **0.005809** | 0.983797 | ✔ |

> **h_L1_max = 5.224122e-3 = 10.45 × r_N**, binding constraint = **A22 rows
> 0..35 tangential margin** (exactly the predicted `h_valid ≈ 0.0052`). The
> killed-axis margins are ≈ 0.99 and never bind.

Also certified: the two aux rows are **active** at ẑ (`|g| = 0` exactly), and
the two new v3 rows vanish to 1.6e-61 / 2.3e-61.

**L1 (disjunction) therefore holds on box(ẑ, h) for every h ≤ 5.224e-3**: 16 of
the 24 (axis, side) combinations are refuted, separating-axis completeness
supplies at least one survivor per pair, so every feasible z belongs to at
least one of the 16 variants, and on its variant all 12 branch corner rows are
≥ 0 (L1.1). No tie menu anywhere.

---

## 3. Task 3 — L2, and the constant that actually moved

### 3.1 The exact inequality chain (as coded; verbatim in `a36_lib` §chain)

For a variant V, `R_V = {0..35} ∪ {44,45} ∪ (the 12 branch corner rows)` is
valid on box(ẑ,h) ∩ V. Pin set `P` (34 rows, ⊆ `R_V`), preconditioner `Y`,
`β(h) = sup_box ‖I − Y A_P‖_∞ < 1`, `κ = ‖Y‖_∞`. Take `ω ≥ 0` on `R_V`,
`ω = 0` elsewhere, `ω_r > 0` on `P`; `W = Σ ω_r g_r`, `Φ = s − W`;
`ε₀ = Σ|ω_r||g_r(ẑ)|`, `ε_w = ‖Aᵀω − e_s‖₁`,
`H̄ = ½ Σ_ij sup_box |∂²W|`, `E(x) = ε₀ + ε_w x + H̄ x²`.

* **(T1)** `Φ(z) ≥ ŝ − E(h)` (Taylor, interval Hessian).
* **(T2)** `s(z) = Φ(z) + W(z) ≥ Φ(z) + G_ω(z)`, `G_ω = Σ_{r∈P} ω_r g_r ≥ 0`.
* **CASE 1** `G_ω ≥ E(h)` ⟹ `s(z) ≥ ŝ`.
* **CASE 2** `G_ω ≤ E(h)`. **Here is the A36 change.** A35/M2b weakened
  `G_ω ≤ E` to `g_r ≤ E/α` *row by row* and then applied `κ`. Instead, since
  every term `ω_r g_r` is ≥ 0,
  ```
  |Σ_r Y_ir g_r| ≤ Σ_r (|Y_ir|/ω_r)(ω_r g_r) ≤ max_r(|Y_ir|/ω_r) · G_ω ≤ κ_eff E(h),
  κ_eff := max_{r∈P} c_r/ω_r ,   c_r := max_i |Y_ir| .
  ```
  With `‖Y F_P(ẑ)‖_∞ ≤ κ g_max` and the mean-value identity,
  `‖z − ẑ‖_∞ ≤ (κ_eff E(h) + κ g_max)/(1−β) =: ψ(h)`.
* `ψ(h) < h` ⟹ **iterate** (A35 variant C) to the least fixed point `x*` of
  `x ↦ κ_eff E(x)/(1−β) + κ g_max/(1−β)`; `x* ≤ r_N` hands over to A22.

`κ_eff ≤ κ/α` always, but at the jam **`κ_eff = 19.32` while `κ/α = 784`** — the
rows with a large `|Y_ir|` are exactly the rows that carry a large `ω_r`, and
the max-form sees that while the α-form cannot. **Factor 40.5 in ψ, 11.4× in
the certified radius.**

### 3.2 The inner LP (design only; the [IV] evaluation is what is certified)

At fixed h, in the kernel parametrisation `ω = ω_p + Nᵀu` (so `Aᵀω = e_s`
identically), maximise
`t − h/(1−β) · ½ Σ_r w_r ω_r` s.t. `ω_r ≥ 0` on `R_V`, `ω_r = 0` off `R_V`,
`ω_r ≥ c_r t` on `P`, where `w_r = Σ_ij sup_box|∂²g_r|` is the per-row Hessian
mass. At the optimum `t = 1/κ_eff`, so a positive objective certifies
`κ_eff · H̄_bound · h/(1−β) < 1`, i.e. the reach condition, under the triangle
bound `H̄ ≤ ½Σ w_r|ω_r|`. The true `H̄` (with interval cancellation) is smaller —
7.58 vs the bound 10.5 — so the LP is a **heuristic**, and the h-bisection is
closed by the full `[IV]` certificate at every step. `[LP]`

### 3.3 (b) pin bases

| basis | κ | β(h) | κ/(1−β) | κ_eff | H̄ | certified reach |
|---|---|---|---|---|---|---|
| **A22 S + A22 Y** (verbatim) | 20.292 | 0.4464 | 36.66 | 19.316 | 7.575 | **3.7833e-3 = 7.57 r_N** |
| A22 S, Y refitted | 20.292 | 0.4464 | 36.66 | 19.316 | 7.575 | 3.7833e-3 |
| local-search 34-subset of {0..35, aux} | 18.580 | 0.4194 | 31.99 | 19.321 | 7.580 | 3.9643e-3 = 7.93 r_N |
| load-bearing block avoiding rows {0,2} | — | — | — | 42.71 | 7.66 | 2.2769e-3 (κ_eff doubles) |

The load-bearing candidate (M1b §2's 33×33 block + an aux row) is **worse**:
dropping the statically dead rows 0, 2 forces `ω` off the rows that carry the
large `|Y_ir|`, doubling `κ_eff`. The local-search basis is 4.8 % better than
A22's, and was **declined**: the emitted certificates use A22's own `S` and `Y`
verbatim so that **no new preconditioner enters the trust chain**. The 4.8 % is
recorded in `a36_reach.json` as available head-room.

The pin basis must be drawn from the **universal** rows `{0..35} ∪ {44,45}`,
otherwise a single Y cannot serve all 16 variants.

### 3.4 (c) the iterated variant-C chain

Always used: `ψ(h)/h = 0.9979` at h\*, so case 2 does not land below `r_N` in
one step; the iteration converges to `x* = 6.11e-58 ≪ r_N = 5e-4`. Verified in
the standalone checker by 800 iterations of the map.

### 3.5 Per-variant certified reach

All 16 variants give the **same** number to 7 digits (the binding constraint is
the universal part of `ω`; the branch rows only shave `H̄`):

| variant (16 of them) | h_V | h_V / r_N | β | H̄ | κ_eff | ψ/h | x\* |
|---|---|---|---|---|---|---|---|
| `A01{a,b}-A03{a,b}-B13{x,x',y,y'}` | **3.783284e-3** | **7.567** | 0.44591 | 7.5753 | 19.3157 | 0.99794 | 6.11e-58 |

`h* = min over the 16 = 3.783284e-3`; certificates emitted at the clean
rational **h\* = 3779/1 000 000 = 3.779e-3 = 7.558 r_N**.

### 3.6 The binding constant, named

```
ψ(h)/h  =  [ κ_eff · H̄(h) · h  +  (ε₀ + ε_w h + κ g_max)/h ] / (1 − β(h))
        =  0.99794     at h*,  of which  99.9999…%  is the  κ_eff·H̄·h/(1−β)  term.
```

* **term:** `κ_eff · H̄ · h / (1 − β)`, i.e. the **second-order (Hessian) term**.
  `ε₀ = 1.05e-59`, `ε_w = 7.78e-45`, `g_max = 6.69e-60` are all numerically
  irrelevant.
* **rows:** the LP *equalises* `c_r/ω_r` over the pin set, so `κ_eff = 19.3157`
  is attained simultaneously on **8 pin rows** — including **both aux rows
  44 `D0-1`, 45 `D0-3`** and rows 7 `W2c0[y=0]`, 35 `E10c3-9e0`. (The slackest
  pin rows are 34 `W10c1[x=s]` and 25 `W6c2[y=s]` at 3.46.) Raising κ_eff's
  binding value would require raising `ω` on all 8 at once against the fixed
  scale `Aᵀω = e_s` — this is the wall.
  `H̄ = 7.575` is dominated by the tilted separation rows: `E1c2-8e3` (2.04),
  `E5c0-9e1` and `E3c2-7e3` (1.84 each), `E4c2-6e3` (1.45), `E4c1-7e2` and
  `E2c3-8e0` (1.23 each) — per-row mass `|ω_r| w_r`.
* **secondary:** `β(h)` climbs from 0.189 (h = 1.6e-3) to 0.446 (h = 3.78e-3);
  it costs the last ~30 % of the radius.

### 3.7 Attribution of the total 29.8× gain over A35/M2b

| step | reach | × |
|---|---|---|
| A35/M2b (V′), α-form, strict set = all 44 variant rows | 1.270e-4 = 0.25 r_N | — |
| strict set restricted to the pin rows only (α: 0.0205 → 0.0564) | ≈ 3.31e-4 = 0.66 r_N | 2.6 |
| **max-form κ_eff instead of κ/α** | **3.6935e-3 = 7.39 r_N** | **11.2** |
| + basis v3 branch rows (needs L1) | 3.7833e-3 = 7.57 r_N | 1.024 |
| (+ local-search pin basis — available, declined) | 3.9643e-3 = 7.93 r_N | 1.048 |

---

## 4. Task 4 — certificates, re-check, corruption gates

`results/a36_certs/` — **17** certificates, rational ω (denominators ≤ 1e45 on
the pin rows, 1e12 on the free rows; the brief's ≤ 1e18 was relaxed to A35's own
`OMEGA_S_DEN` so that `Aᵀω = e_s` holds to 7.8e-45 rather than ~1e-18 — see
gaps):

* `G3_<variant>.json` × 16, at h\* = 3779/1e6, each **loading its branch's
  corner rows with ω ≥ 0.01** (branch floor; it costs 8e-9 of radius) so that
  the drop-branch / wrong-branch gates are not vacuous. Loaded branch rows for
  `A01a-A03a-B13x`: positions 36, 46 (A01a), 38, 52 (A03a), 40, 59 (B13x).
* `G3_UNIVERSAL.json` — the branch-free control at 3689/1e6.

`code/a36_check.py` — standalone: `mpmath.iv + fractions + json + math` only. No
`a36_lib`, no `strata_lib`, no `m2_lib`, no `t3lib`, no `a22lib`, no numpy/scipy.
Order-2 interval jets transcribed with attribution from A35's own
`m2_check_inflation.py`. It rebuilds all 70 rows from A22's `krawczyk_cert.json`
+ its **own** copy of the v3 axis table, rebuilds `P` from A22's `S` and `Y`
from A22's `Y`, recomputes `R_V` from the declared variant, and re-derives every
constant. Checks per certificate: `[S][N][A][O][Z][G][H][K][E][P][V][L]` —
including the **L1 killed-axis refutation at that certificate's own radius**, so
each certificate is self-contained.

> **17 certificates, 339 checks, ALL PASS.**
> min A22 tangential margin 0..35 = **0.005809** (> 0)
> min L1 kill margin = **0.988620** (> 0)
> max ψ/h = 0.99794, max x\* = 6.11e-58.
> Reported by the checker: under A35's α-form the same certificates would give
> ψ/h = **40.5** — i.e. the max-form is exactly what makes these radii possible.

### Corruption gates — all 5 fail as required

| gate | what it does | checks that fired |
|---|---|---|
| `omega-sign` | negate ω on one pin row | 6 — `[O]`×2, `[G]` (ε_w 7.8e-45 → 0.224), `[P]`×2 |
| `h-big` | h × 8 | 5 — `[H]`, `[K]` (β = 3.585), `[P]`×2, **`[V]` tangential −0.110** |
| `drop-aux` | zero ω on rows 44, 45 | 5 — `[O]`, `[G]` (ε_w → 0.210), `[E]` (κ_eff = ∞), `[P]`×2 |
| `drop-branch` | zero ω on the branch corner rows, keep the claim | 4 — `[O]` non-vacuity (all three axes), `[G]` (ε_w → 0.556), `[P]`×2 |
| `wrong-branch` | swap the (1,3) axis for another, keep ω | 2 — `[O]` ω ≠ 0 outside R_V (positions 40, 59), `[O]` non-vacuity |

**5 / 5 gates fail. 0 gates pass.**

---

## 5. VERDICT LINE and the composed theorem

> **h\* = 3.779e-3 = 7.558 × r_N > r_N.  YES.**

**THEOREM (A36, composed).** Let ẑ be A22's jam and ŝ = 3.877083590022814…
Then for every feasible packing configuration `z ∈ box(ẑ, 3779/10⁶)`
(11 interior-disjoint unit squares in the s-square, `‖z − ẑ‖_∞ ≤ 3.779e-3`):

  **σ(z) := s(z) ≥ ŝ, with equality if and only if z = ẑ.**

Proof chain, all pieces certified here or inherited:

1. **All break sets at once.** The (V′) barrier is a statement about *feasible
   z*, not about a stratum: no break set, no active-set selection, no rank
   condition enters. It therefore covers the entire 2⁴⁴ break-set lattice of
   basis v3 (and M1b's 25 050-element queue, and the 70 499 cone-alive family)
   in one shot. **The (V′) barrier is stratum-blind, so no Fritz-John
   enumeration is needed** — neither the λ₀ = 0 branch nor the λ₀ = 1 branch is
   ever entered, because the argument never passes through stationarity.
2. **Both FJ branches, explicitly.** For the same reason, both branches are
   covered: if z were FJ-stationary with λ₀ = 0 or λ₀ = 1, it is still just a
   feasible point of box(ẑ, h\*) and falls under case 1 or case 2.
3. **L1 replaces the M2b-a endpoint caveat.** A35/M2b's standing gap was that
   the six repaired v2 rows 36–41 sit at edge **endpoints**, so their dominance
   margin is negative on every box, and even the weaker "the owner edge
   separates the pair" was undischarged. L1.1 shows the barrier never needed
   dominance: if the axis separates, **all four** of its corner rows are ≥ 0,
   and L1.2 + the 16 certified killed-axis refutations show that on box(ẑ, h\*)
   some listed axis must separate each of the three repaired contacts. So
   basis v3's branch rows are certified valid on their variant, and the 16
   variants cover the box. **M2b-a is discharged, not inherited.**
4. **Case 1 / case 2 dichotomy** (§3.1), certified `[IV]` per variant.
5. **Case 2 iterates** to `x* = 6.11e-58 ≤ r_N = 5e-4`, where **A22's local
   rigidity theorem** gives σ ≥ ŝ with equality only at ẑ.
6. **Rows 0..35 valid on box(h\*)** by the SAT-selection margins
   (tangential 0.005809 > 0, depth + ½ = 0.9838 > 0); aux rows valid globally
   (incircle) and active at ẑ.

**Strictly stronger, and simpler, than needed:** step 3 is not load-bearing.
`G3_UNIVERSAL.json` proves the same theorem on box(ẑ, 3689/10⁶) = 7.378 r_N with
ω supported on A22's rows 0..35 plus the two aux dist rows only — no basis v3,
no branch axes, no L1. The 16-variant family exists to squeeze the last 2.4 %
and to make the branch machinery falsifiable (the gates).

**Hybrid fallback L2(d): NOT RUN** — the verdict is YES, so pricing the
per-stratum walk would be wasted compute.

---

## 6. Gaps / caveats

* **A36-a (scope).** The theorem is local: box(ẑ, 3.779e-3) in the ∞-norm on
  (c, θ, s). It says nothing about σ ≥ ŝ + δ_stop, so theory.md **G1 (the ridge
  handoff) is untouched**, as in A35/M2b-f. What A36 delivers is that the
  escape-complex route now *strictly dominates* A22's own basin instead of
  covering a quarter of it.
* **A36-b (ω denominators).** The brief asked for denominators ≤ 1e18. The
  emitted ω uses A35's recipe: 1e12 on the free rows, **1e45** on the pin rows,
  because ε_w scales with the pin-row rounding and at 1e18 it would be ~1e-18 —
  still harmless here (`ε_w h ≈ 4e-21 ≪ H̄h² ≈ 1e-4`), but there is no reason to
  pay for it. Flagged as a deliberate deviation, not an oversight.
* **A36-c (ψ/h margin).** ψ(h\*)/h\* = 0.99794. The certified inequality is
  strict and re-verified independently, but h\* is within 0.2 % of the
  certificate's own cliff; the reported per-variant reach 3.783284e-3 is the
  bisection limit. Anyone wanting slack should use 3.7e-3 (ψ/h = 0.9607, re-derived).
* **A36-d (pin basis).** 4.8 % of radius is left on the table by using A22's Y
  rather than the local-search basis. Deliberate: trust chain over constant.
  The local-search basis was found by float64 local swaps `[NUM]`; its Y would
  be a new rational matrix needing its own `[RFP]` provenance.
* **A36-e (L1 completeness).** L1's disjunction rests on separating-axis
  completeness for convex polygons applied to *interior-disjoint* pairs (non-
  strict separation, gap ≥ 0). That is the same lemma drain_lemma D3′ already
  uses; it is not re-proved here, only its 16 eliminations are certified `[IV]`.
* **A36-f (what is NOT closed).** The (W′)/FJ layer, M1b's 25 050 queue, the
  four minimal dead triples of the M1b erratum — all still exist as objects,
  but none of them is on the critical path any more, because (V′) covers every
  break set at a radius 7.56 × r_N. The A35 gaps M2b-b, -c, -d, -e are
  untouched and now irrelevant to the composed theorem.
* **A36-g.** `H̄` and `β` are evaluated on box(h\*) and reused for every smaller
  radius in the variant-C iteration — conservative and sound, but it means the
  fixed point x\* is not the sharpest available.

---

## Files

* `attempts/A36-levers/code/a36_lib.py`, `a36_l1.py`, `a36_reach.py`,
  `a36_emit.py`, `a36_check.py`
* `attempts/A36-levers/results/a36_l1.json` — L1 grid + h_L1_max
* `attempts/A36-levers/results/a36_basis_v3.json` — the 70-row v3 table, the 8
  axes with their corner-row positions, the 16 variants, the active set
* `attempts/A36-levers/results/a36_reach.json` — pin-basis table, per-variant
  reach, h\*, emitted-certificate summary, attribution notes
* `attempts/A36-levers/results/a36_certs/` — `G3_*.json` × 16 + `G3_UNIVERSAL.json`
* `attempts/A36-levers/results/a36_report.md` — this file

Re-run: `python code/a36_l1.py && python code/a36_reach.py && python
code/a36_emit.py && python code/a36_check.py`; gates via
`python code/a36_check.py --corrupt {omega-sign,h-big,drop-aux,drop-branch,wrong-branch}`.
