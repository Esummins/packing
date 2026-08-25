# A28-lean-batch — Mathlib installed; the upper-bound bridge lemma is proved over ℝ²

Owner: Lean agent (A28). Date: 2026-08-24. Status: **done-success (items 1–3, 5); item 4 not
attempted, blocker identified.**

## Headline

The repo's biggest stated-but-unformalised gap is closed. `lean/PackingCert` proved only
`checkPacking Data.trump11 = true` (a `Bool` computation); the geometric meaning was an
assumed "bridge lemma" (A06 §5). It is now a Lean theorem:

```
PackingCert.eleven_unit_squares_in_3877084 :
  ∃ Q : List (Set (ℝ × ℝ)),
    Q.length = 11 ∧
    (∀ q ∈ Q, IsUnitSquare q) ∧
    (∀ q ∈ Q, q ⊆ Set.Icc (0:ℝ) (969271/250000) ×ˢ Set.Icc (0:ℝ) (969271/250000)) ∧
    Q.Pairwise Disjoint
```

`#print axioms` → `[propext, Classical.choice, Quot.sound]`. **No `native_decide`**: the
certificate evaluation is done by kernel `decide` (`trump11_ccw_ok_kernel`), so the whole
chain from integer data to the real-plane statement is kernel-checked.

Hence `s(11) ≤ 969271/250000 = 3.877084` is, for the first time in this repo, a statement about
ℝ² rather than about a `Bool`.

## 1. Mathlib (task 1) — installed, used, then removed for disk

`lake exe cache get` in `lean/PackingCertMathlib` **succeeded** this time: 8691 `.ltar` files,
**6 min 15 s** (16:47:38 → 16:53:53), aggregate rate ~50–800 KB/s. Space consumed:
Mathlib `.lake` **6.52 GB**, `~/.cache/mathlib` 0.41 GB, extra toolchain
`leanprover/lean4:v4.34.0-rc1` **3.02 GB** ⇒ ≈ **9.95 GB** total. Free space went 33.5 GB → 13.6 GB
during the fetch (the rest of the drop was the sibling A27 run).

Disk was the whole story again: while A28's Lean work proceeded, free space fell to **0.29 GB**
(A27 output, not Lean — Lean's own incremental builds cost ~10 MB each). Everything was
therefore torn down at the end, in this order: `~/.cache/mathlib` (+0.4 GB),
`PackingCertMathlib/.lake` (+6.5 GB), toolchain v4.34.0-rc1 (+3.0 GB) ⇒ **10.55 GB free**
when A28 finished. A monitoring watchdog (scratch PowerShell loop, 20 s poll, kill lake/lean
below 8 GB) fired once at 16:59:43 during a transient dip to 4.31 GB; the build in flight had
already completed, so nothing was lost.

**Reproduction** (the `.lean` sources are committed; only build artefacts were deleted):

```
cd lean/PackingCertMathlib
lake exe cache get     # ~6 min, ~7 GB (+3 GB toolchain that elan re-installs automatically)
lake build             # ~1 min for the five modules below
lake env lean scratch/Axioms.lean
```

Build times of *our* modules once Mathlib is cached (Lean 4.34.0-rc1, this machine):

| module | time |
|---|---|
| `PackingCertMathlib/Checker.lean` | 1.3 s |
| `PackingCertMathlib/Data.lean` | 1.3 s |
| `PackingCertMathlib/Bridge.lean` | 15 s |
| `PackingCertMathlib/Band.lean` | 22 s |
| `PackingCertMathlib/Trump11.lean` | 18 s (incl. kernel `decide` on the 11-square certificate) |

## 2. The upper-bound bridge lemma (task 2) — `PackingCertMathlib/Bridge.lean`

Files added to `lean/PackingCertMathlib/PackingCertMathlib/`:

* `Checker.lean` — **byte-identical copy** of `lean/PackingCert/PackingCert/{Geometry,Checker}.lean`
  (core Lean, no Mathlib). Duplicated because `PackingCert` is pinned to Lean 4.33.0 and the
  Mathlib project needs 4.34.0-rc1; keeping the copy verbatim is what makes the bridge a
  statement *about the same checker*. Adds only
  `isUnitSquareCCW` / `checkPackingCCW` (the shape test with the orientation disjunction
  replaced by its `+n` branch) and `checkPackingCCW_imp : checkPackingCCW c = true → checkPacking c = true`.
  All 11 squares of `certs/trump11_certificate_int.json` are counter-clockwise (checked), so
  nothing is lost.
* `Data.lean` — copy of the generated `Data.lean` (import line rewritten).
* `Bridge.lean` — the real geometry.
* `Trump11.lean` — the instance.

### Definitions

```
RP := ℝ × ℝ                       rdot a b := a.1*b.1 + a.2*b.2
aff p0 e a b := (p0.1 + a*e.1 - b*e.2, p0.2 + a*e.2 + b*e.1)          -- p0 + a·e + b·e⊥
sqSet p0 e   := { q | ∃ a b, 0 ≤ a ≤ 1 ∧ 0 ≤ b ≤ 1 ∧ q = aff p0 e a b }
IsUnitSquare S := ∃ p0 e, rdot e e = 1 ∧ S = sqSet p0 e
```

The parametrisation (A06's suggestion) instead of `convexHull`: it needs **no** convexity API.
That "a set of this form really is a unit square" is not a definition-by-fiat is proved:

* `aff_sqdist : rdot e e = 1 → sqdist (aff p0 e a b) (aff p0 e a' b') = (a-a')² + (b-b')²`
  — the parametrisation is a Euclidean isometry, so `sqSet p0 e` is a congruent copy of `[0,1]²`;
* `sqSet_eq_image : sqSet p0 e = (fun u => aff p0 e u.1 u.2) '' (Icc 0 1 ×ˢ Icc 0 1)`.

(`sqdist` is the explicit squared Euclidean distance — deliberately *not* the `Prod` norm, which
in Mathlib is the sup norm.)

### Theorems

| name | statement |
|---|---|
| `rdot_aff` | `rdot (aff p0 e a b) n` = the convex combination `(1-a)(1-b)·d₀ + a(1-b)·d₁ + ab·d₂ + (1-a)b·d₃` of the four corner projections (pure `ring`) |
| `sqSet_dot_le`, `sqSet_le_dot` | corner bounds on `rdot · n` propagate to the whole square |
| `sqSet_fst_le`, `sqSet_le_fst`, `sqSet_snd_le`, `sqSet_le_snd` | the same for coordinates (`n = (1,0)`, `(0,1)`) |
| **`disjoint_of_strictlyBelow`** | **the SAT lemma:** `(∀ c ∈ cornerList p0 e, ∀ d ∈ cornerList q0 f, rdot c n < rdot d n) → Disjoint (sqSet p0 e) (sqSet q0 f)`. Any `n` whatsoever — no unit-length, no edge-direction hypothesis. This is exactly the "positive margin ⇒ disjoint" statement the dispatch asked for |
| `cornerList_setR` | the four `aff`-corners of a CCW integer square are the four stored corners, divided by `D` |
| `mem_allPairs`, `allPairs_pairwise` | `(∀ p ∈ allPairs l, R p.1 p.2) → l.Pairwise R` |
| **`checkPackingCCW_sound`** | **the bridge:** `checkPackingCCW c = true` ⇒ `∃ Q, Q.length = c.squares.length ∧ (∀ q ∈ Q, IsUnitSquare q) ∧ (∀ q ∈ Q, q ⊆ Icc 0 (sideNum/sideDen) ×ˢ Icc 0 (sideNum/sideDen)) ∧ Q.Pairwise Disjoint` |

Proof shape, for the record: strict separation is transferred from `Int` to `ℝ` through
`rdot (toR D p) (vecR n) = (p.dot n : ℝ)/D` (the axis is used **unscaled**, so the SAT lemma's
scale invariance does the work); containment comes from the same
`sqSet_dot_le` machinery with `n = (1,0)`, `(0,1)`; `Disjoint` is `Set.disjoint_left` plus
`max` of the four A-projections `<` `min` of the four B-projections.

### Instance (`Trump11.lean`)

```
trump11_ccw_ok        : checkPackingCCW Data.trump11 = true   -- native_decide
trump11_ccw_ok_kernel : checkPackingCCW Data.trump11 = true   -- decide, NO axioms
trump11_ok_of_ccw     : checkPacking    Data.trump11 = true   -- via checkPackingCCW_imp
eleven_unit_squares_in_3877084                                -- the headline
```

`set_option maxRecDepth 10000` is needed for the kernel `decide` (75-bit denominators);
the whole module compiles in 18 s.

## 3. The A26 band lemma (task 3) — `PackingCertMathlib/Band.lean`, with an honest constant loss

A26's Theorem A26.1 is *"(2B−1)² < 8 ⇒ at most one unit square in a square of side B"*, i.e.
`B < 1/2 + √2 = 1.9142`; its corollary at `s = 96/25` uses `B = 1.84`. The proof needs the
**hard** direction of SAT: interior-disjoint convex polygons are separated by an **edge normal
of one of them** (that is what makes `|u·Δ| ≤ 2h₁D` available). Mathlib has geometric
Hahn–Banach, which gives *some* separating direction, not an edge normal. Formalising
"edge normal suffices" for two squares means computing the H-representation of the Minkowski
sum of two squares (an octagon) — a multi-day job, not attempted.

What is proved instead is the same argument with an **arbitrary** separating direction:

```
PackingCert.two_unit_squares_side_ge :
  rdot e₁ e₁ = 1 → rdot e₂ e₂ = 1 → rdot u u = 1 →
  csqSet c₁ e₁ ⊆ Icc lo (lo+B) ×ˢ Icc lo (lo+B) →
  csqSet c₂ e₂ ⊆ Icc lo (lo+B) ×ˢ Icc lo (lo+B) →
  (∀ x ∈ csqSet c₁ e₁, rdot x u ≤ t) → (∀ y ∈ csqSet c₂ e₂, t ≤ rdot y u) →
  1 + √2/2 ≤ B
```

with `csqSet c e` the unit square of **centre** `c`, `csqSet_eq_sqSet` linking it to `Bridge`'s
`sqSet` and `isUnitSquare_csqSet` certifying it is a unit square. Supporting lemmas, all proved:
`csq_max_dot` / `csq_min_dot` (the support function of a unit square is attained at a corner),
`csq_centre_bounds` (`Q ⊆ [lo,lo+B]² ⇒ lo + ‖e‖₁/2 ≤ c ≤ lo+B − ‖e‖₁/2` in both coordinates),
`one_le_support` (`|u·e| + |u·e⊥| ≥ 1` for unit `u,e`), `one_le_nrm1` (`‖e‖₁ ≥ 1`),
`nrm1_le_sqrt_two` (`‖u‖₁ ≤ √2`).

Constants: **1.7071 formalised** vs **1.9142** in A26 vs **2 (sharp, = s(2))**. Corollaries:

* `atMostOne_of_side_lt` — contrapositive.
* `band_96_25` — at `s = 96/25 = 3.84` and band width `w = 27/25 = 1.08` (inner square
  `[27/25, 69/25]²`, side `42/25 = 1.68 < 1.7071`) at most one square of a packing avoids the
  band, i.e. **at least 10 of the 11 squares meet the width-1.08 boundary band**.
  A26 gets width **1**; the difference is exactly the edge-normal refinement.

### A by-product worth recording: the sharp constant is 2, not 1/2+√2

A26's E1 relaxes `1 ≤ 2h₁(B − ½ − h₁) ≤ (B−½)²/2` and lands on `1/2+√2 = 1.9142`. Running the
*same* inequality chain **without** that relaxation, and minimising over the separating
direction α and the two tilts θ₁,θ₂ (numerically, `python` grid 361×361×721), gives

```
min over θ₁,θ₂  [ min over α ((g(α−θ₁)+g(α−θ₂)) / (2 g(α))) + (g(θ₁)+g(θ₂))/2 ]  =  2.0000
        g(x) := |cos x| + |sin x|,  minimiser θ₁ = 0, θ₂ = 90° (i.e. two axis-parallel squares)
```

— i.e. even the *weak* (arbitrary-direction) form of SAT already implies `B ≥ 2`, which is
**sharp** (`s(2) = 2`) and strictly better than A26's E1. It decouples: the whole statement
follows from the single two-vector inequality

> **(A28.★)** for unit `u, e ∈ ℝ²`:  `|u·e| + |u·e⊥| + ‖u‖₁‖e‖₁ ≥ 2‖u‖₁`

(verified numerically to `−4.4e−16`, equality at `θ ∈ {0°, 90°}`). Summing (A28.★) over the two
squares and dividing by `2‖u‖₁` is exactly the chain above. **(A28.★) is not formalised**: it
needs a 6-fold sign case split with two quadratic constraints, and the tight cases
(`e = (1,0)` and `e = (0,1)`) are not reachable by a single `nlinarith` call — each branch wants
its own factorisation (e.g. in the all-positive branch, `u₁e₁+u₂e₂+u₂e₁ ≥ u₁+u₂` needs
`e₁+e₂−1 = 2e₁e₂/(e₁+e₂+1)` and `1−e₁ = e₂²/(1+e₁)`). Whoever picks this up gets
**`B ≥ 2`, hence A26.1 with band width `w = (s−2)/2` — at `s = 96/25` that is `w = 0.92`, and
the statement holds for every `s < 4`** (A26's E1 only reaches `s < 3.9142`). That is the
single highest-value follow-up in this file.

## 4. A22 Krawczyk replay (task 4) — NOT attempted; the blocker is interval trigonometry

`results/krawczyk_cert.json` is replayable by an *interval* checker, but not by an *integer*
one as it stands. Reason, from the artefact itself: the 34 variables are
`(cx_i, cy_i, θ_i)_{i<11}, s` with `θ_i` stored as **exact rational angles** (60-digit
decimals), and all 20 wall rows and 16 edge rows evaluate corner positions
`c_i + R(θ_i)(±½,±½)`. A decidable Lean checker therefore needs certified rational enclosures
of `cos`/`sin` on 11 intervals of radius `5e-4` — i.e. Taylor series with rigorous remainder
bounds, from scratch in core Lean. That is a project in its own right and dwarfs the checker.

**The fix is on the A22 side, not the Lean side**, and it is cheap: re-emit the certificate in
the half-angle parametrisation `t_i = tan(θ_i/2)` that `certs/`, `gen_cert_lean.py` and
`MeasureInt.lean` already use (`cos = (1−t²)/(1+t²)`, `sin = 2t/(1+t²)`). Every constraint row
then becomes a *rational function* of rational data, the interval Jacobian becomes rational
interval arithmetic, and a `checkKrawczyk` in the existing `MeasureInt` style (all-`Int`,
outward-rounded, `native_decide`-able) is a direct port of `recheck.py`'s `[K]`, `[E]`, `[B]`
gates. Estimated effort after that change: 1–2 days. Recommended, but out of scope here.

## 5. Files

```
lean/PackingCertMathlib/PackingCertMathlib/Checker.lean   copy of the integer checker + CCW variant
lean/PackingCertMathlib/PackingCertMathlib/Data.lean      copy of the generated trump11 data
lean/PackingCertMathlib/PackingCertMathlib/Bridge.lean    real geometry + the bridge lemma
lean/PackingCertMathlib/PackingCertMathlib/Band.lean      A26-family band lemma over ℝ²
lean/PackingCertMathlib/PackingCertMathlib/Trump11.lean   the s(11) ≤ 3.877084 real theorem
lean/PackingCertMathlib/scratch/Axioms.lean               #print axioms for all of the above
lean/PackingCertMathlib/BridgeSketch.lean                 A06's sketch — now superseded by Bridge.lean
lean/README.md                                            theorem table updated
```

## 6. Axioms (verbatim, `lake env lean scratch/Axioms.lean`)

```
disjoint_of_strictlyBelow      [propext, Classical.choice, Quot.sound]
checkPackingCCW_sound          [propext, Classical.choice, Quot.sound]
aff_sqdist                     [propext, Classical.choice, Quot.sound]
trump11_ccw_ok                 [PackingCert.trump11_ccw_ok._native.native_decide.ax_1_1]
trump11_ccw_ok_kernel          does not depend on any axioms
trump11_ok_of_ccw              [propext, Quot.sound]
eleven_unit_squares_in_3877084 [propext, Classical.choice, Quot.sound]
two_unit_squares_side_ge       [propext, Classical.choice, Quot.sound]
atMostOne_of_side_lt           [propext, Classical.choice, Quot.sound]
band_96_25                     [propext, Classical.choice, Quot.sound]
isUnitSquare_csqSet            [propext, Classical.choice, Quot.sound]
```

`Classical.choice` enters only through Mathlib's `Real`; the packing-specific reasoning is
constructive, and the certificate evaluation is kernel `decide`.

## 7. What remains unformalised after A28

1. **(A28.★)** the two-vector inequality above ⇒ sharp `B ≥ 2` ⇒ A26.1 for all `s < 4`. Small,
   self-contained, high value.
2. **Edge-normal SAT** (Minkowski octagon) — would give A26.1 as literally stated; superseded
   in value by (1), which is both easier and stronger.
3. **Hahn–Banach step**: `Disjoint (interior Q₁) (interior Q₂) → ∃ u t, separating`. Needs
   `Convex (sqSet p0 e)` (easy: affine image of a box) plus `geometric_hahn_banach_open` and a
   Riesz identification of the functional with a vector. Then `Band.lean`'s hypotheses `hs1/hs2`
   become derivable and the band lemma applies to genuine packings, not to separated pairs.
4. **The lower-bound (measure) bridge lemma** — `checkMeasureI c = true ⇒ every closed unit
   square in [0,s]² has μ(Q) ≥ 1 ⇒ s(11) ≥ s`. Untouched; A06's 3–5 day estimate stands (the
   half-angle substitution and the branch-and-bound induction).
5. **A22 Krawczyk replay** — see §4; blocked on the parametrisation, not on Lean.
