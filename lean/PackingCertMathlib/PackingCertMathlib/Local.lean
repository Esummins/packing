/-
# `Local.lean` — Theorem LOCAL as a Lean object (A119 T2, from A116)

The certificate of `docs/proofs/local_certificate.md`: a NEIGHBOURHOOD `N` of a known minimum
`z*`, given by one axis-aligned box per load-bearing square `ℓ ∈ L` and one slack core per class
pin `p ∈ P`, contains no packing of side `≤ s0`.  §8 of that document fixes the Lean shape and
this file follows it:

* **the objects** — `Box`, `Pin`, `LocalHyp` (the hypothesis `N`), `LocalDead` (its conclusion);
* **Lemma SAT** (`sat_selection`) — interior-disjoint unit squares admit one of the eight signed
  separating-axis rows.  Stated here as the file's ONE geometric axiom: `CaseSat.sat_squares`
  gives the closed-square form (four projection overlaps ⇒ the squares MEET), and the passage to
  interiors is the shrink argument of `local_certificate.md` §1 — see the docstring;
* **Lemma COVER** — the finite case split: `cover_bisect` (a tilt interval is the union of its
  two halves), `cover_qsplit` (`le_total` on the q-range), `cover_selection` (the eight
  selections minus the ones excluded by the interval enclosure), all THEOREMS;
* **Lemma RELAX** §3.1 — the affine relaxation over a tilt cell: `axis_decomp` (exact),
  `mccormick_hi` / `mccormick_lo`, `abs_chord`, `chord_of_concave` — all THEOREMS; the two
  trigonometric envelopes `sin_le_sin_abs_le` / `cos_ge_of_abs_le` are proved from Mathlib;
* **Lemma LEAF** — one `linarith` per (cell, leaf) on the relaxed rows.  The generated
  `leaf_*` theorems below are ACTUAL leaves of an ACTUAL certificate
  (`attempts/A119-local-cert-lean/certs/*.cert.json.gz`, re-checked by `check_local.py`), with
  their rows written out as rational-coefficient inequalities and their rational Farkas
  multipliers recorded in the docstring;
* **the composition** — `classKilledAt_of_localDead`: a node whose YES branch is `LocalHyp`
  dies, in the `ClassKilledAt` shape `Composition.lean` consumes.

The file has exactly ONE project axiom, `sat_selection` (Lemma SAT for INTERIORS), and no
`sorry`.  What it does NOT do is derive `LocalDead Ls Ps shat` for a CONCRETE `N` inside Lean:
that step is the recorded finite cover — the bisection tree over the tilt box, the selection case
split per near pair, the impossible selections by interval enclosure, and one `leaf_*` kill per
closed leaf — and it is performed and re-verified, in exact rational arithmetic, by
`attempts/A119-local-cert-lean/code/check_local.py` on the certificate files of
`attempts/A119-local-cert-lean/certs/`.  Status and counts: `notes/lean_status.md`.
-/
import PackingCertMathlib.CaseSat
import PackingCertMathlib.Composition

namespace PackingCert
namespace S11
namespace LocalCert

open Set

noncomputable section

/-! ## 1. The objects -/

/-- One load-bearing square's box: centre in `[cx0, cx1] × [cy0, cy1]`, tilt parameter
`t = tan(θ/2)` in `[t0, t1]`. -/
structure Box where
  cx0 : ℝ
  cx1 : ℝ
  cy0 : ℝ
  cy1 : ℝ
  t0 : ℝ
  t1 : ℝ

/-- A parametrised square lies in a box. -/
def Box.mem (B : Box) (q : PSq) : Prop :=
  q.cx ∈ Icc B.cx0 B.cx1 ∧ q.cy ∈ Icc B.cy0 B.cy1 ∧ q.t ∈ Icc B.t0 B.t1

/-- One class pin: centre `(αx + βx s, αy + βy s) + [−h, h]²`, tilt exactly `0`
(A57's slack cores, `h = δ/√2`, `δ = 10⁻²`). -/
structure Pin where
  ax0 : ℝ
  ax1 : ℝ
  ay0 : ℝ
  ay1 : ℝ
  hh : ℝ

/-- A parametrised square sits in a pin's slack core at side `s`. -/
def Pin.mem (P : Pin) (s : ℝ) (q : PSq) : Prop :=
  |q.cx - (P.ax0 + P.ax1 * s)| ≤ P.hh ∧ |q.cy - (P.ay0 + P.ay1 * s)| ≤ P.hh ∧ q.t = 0

/-- **The local hypothesis `N`** (`local_certificate.md` §1): at side `s`, DISTINCT squares of
`z` occupy every box of `L` and every slack core of `P`.  Nothing is said about the remaining
`11 − |L| − |P|` squares — that is Reduction DROP. -/
def LocalHyp (Ls : List Box) (Ps : List Pin) (s : ℝ) (z : Cfg) : Prop :=
  ∃ wL : Fin Ls.length → Fin 11, ∃ wP : Fin Ps.length → Fin 11,
    Function.Injective wL ∧ Function.Injective wP ∧ (∀ i j, wL i ≠ wP j) ∧
    (∀ i, (Ls.get i).mem (z (wL i))) ∧ (∀ j, (Ps.get j).mem s (z (wP j)))

/-- **`Dead(N, s0)`**: no packing of side `≤ s0` satisfies `N`. -/
def LocalDead (Ls : List Box) (Ps : List Pin) (s0 : ℝ) : Prop :=
  ∀ s : ℝ, ∀ z : Cfg, CfgPacking s z → LocalHyp Ls Ps s z → s0 < s

/-! ## 2. The separating-axis rows and Lemma SAT -/

/-- The owner's axis `a_k(θ)`: `k = false` is `(cos θ, sin θ)`, `k = true` is `(−sin θ, cos θ)`. -/
def axk (q : PSq) (k : Bool) : ℝ × ℝ :=
  if k then (-(sinT q.t), cosT q.t) else (cosT q.t, sinT q.t)

/-- The support width `w(Δ) = |cos Δ| + |sin Δ|` of the OTHER square in the owner's frame,
written with the addition formulas so that it is a function of the two tilt parameters. -/
def wrel (qw qo : PSq) : ℝ :=
  |cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t| +
    |cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t|

/-- The signed separating-axis row `g_σ` of the selection `σ = (owner `qw`, axis `k`,
sign `eps`)`: `eps (c_o − c_w)·a_k(θ_w) − 1/2 − w(θ_w − θ_o)/2 ≥ 0` says that the two unit
squares do not overlap along `a_k(θ_w)`. -/
def gsel (qw qo : PSq) (k : Bool) (eps : ℝ) : ℝ :=
  eps * ((qo.cx - qw.cx) * (axk qw k).1 + (qo.cy - qw.cy) * (axk qw k).2)
    - 1 / 2 - wrel qw qo / 2

/-- **Lemma SAT** (`local_certificate.md` §1): two unit squares are interior-disjoint iff some
one of their eight signed selections has `g_σ ≥ 0`.  Only the direction used by Lemma COVER is
stated.

Status: **AXIOM [C]**.  `CaseSat.sat_squares` proves the closed-square contrapositive — if the
four projection overlaps hold (`|d₁| ≤ a + (c+|s|)/2`, `|d₂| ≤ …`, and the two rotated ones with
`a = 1/2`), the squares MEET.  The step from "meet" to "interiors meet" is the shrink argument
of §1: with all eight gaps `< 0` the four overlaps are proper, so both squares may be scaled
about their centres by some `λ < 1` and the scaled picture still satisfies `sat_squares`; a
common point of the scaled squares is an interior point of both originals.  Formalising the
choice of `λ` is the open work. -/
axiom sat_selection (qw qo : PSq)
    (h : Disjoint (interior qw.set) (interior qo.set)) :
    (∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qw qo k eps) ∨
    (∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qo qw k eps)

/-! ## 3. Lemma COVER — the finite case split -/

/-- Bisecting a tilt cell covers it. -/
theorem cover_bisect {t a m b : ℝ} (h : t ∈ Icc a b) : t ∈ Icc a m ∨ t ∈ Icc m b := by
  rcases le_total t m with h1 | h1
  · exact Or.inl ⟨h.1, h1⟩
  · exact Or.inr ⟨h1, h.2⟩

/-- A q-range split is a genuine case distinction. -/
theorem cover_qsplit (q m : ℝ) : q ≤ m ∨ m ≤ q := le_total q m

/-- The selection case split, with the IMPOSSIBLE selections removed: if the interval enclosure
of a selection is strictly negative on the cell (`hex`), that selection cannot be the one Lemma
SAT provides, so the remaining ones cover. -/
theorem cover_selection {P Q : Prop} (h : P ∨ Q) (hex : ¬ Q) : P := h.resolve_right hex

/-! ## 4. Lemma RELAX — the affine relaxation over a tilt cell (§3.1) -/

/-- The exact decomposition of the owner's axis about the cell midpoint:
`ε d·a(θ* + φ) = p cos φ + q sin φ` with `p = ε d·a(θ*)`, `q = ε d·a(θ* + 90°)`.  This is the
identity that makes the relaxation SECOND order in the cell width. -/
theorem axis_decomp (dx dy tm φ : ℝ) :
    dx * Real.cos (tm + φ) + dy * Real.sin (tm + φ)
      = (dx * Real.cos tm + dy * Real.sin tm) * Real.cos φ
        + (-(dx * Real.sin tm) + dy * Real.cos tm) * Real.sin φ := by
  rw [Real.cos_add, Real.sin_add]; ring

/-- McCormick, upper plane 1: `q φ ≤ q_hi φ − h q + q_hi h` for `q ≤ q_hi`, `−h ≤ φ`. -/
theorem mccormick_hi {q φ qh h : ℝ} (hq : q ≤ qh) (hφ : -h ≤ φ) :
    q * φ ≤ qh * φ - h * q + qh * h := by
  nlinarith [mul_nonneg (sub_nonneg.mpr hq) (by linarith : (0 : ℝ) ≤ φ + h)]

/-- McCormick, upper plane 2: `q φ ≤ q_lo φ + h q − q_lo h` for `q_lo ≤ q`, `φ ≤ h`. -/
theorem mccormick_lo {q φ ql h : ℝ} (hq : ql ≤ q) (hφ : φ ≤ h) :
    q * φ ≤ ql * φ + h * q - ql * h := by
  nlinarith [mul_nonneg (sub_nonneg.mpr hq) (sub_nonneg.mpr hφ)]

/-- The chord of `|q|` over `[q_lo, q_hi]` with `q_lo ≤ 0 ≤ q_hi` (denominators cleared):
`(q_hi − q_lo) |q| ≤ (q_hi + q_lo) q − 2 q_lo q_hi`. -/
theorem abs_chord {q ql qh : ℝ} (h1 : ql ≤ q) (h2 : q ≤ qh) (hl : ql ≤ 0) (hh : 0 ≤ qh) :
    (qh - ql) * |q| ≤ (qh + ql) * q - 2 * ql * qh := by
  rcases abs_cases q with ⟨he, _⟩ | ⟨he, _⟩ <;> rw [he] <;> nlinarith

/-- A concave function dominates any affine function that is below it at BOTH ends of an
interval — the chord bound of `w = |cos| + |sin|` on a cell with no interior kink. -/
theorem chord_of_concave {f : ℝ → ℝ} {a b m c u v : ℝ} (hab : a ≤ b)
    (hcv : ConcaveOn ℝ (Icc a b) f) (ha : m * a + c ≤ f a) (hb : m * b + c ≤ f b)
    (hu : 0 ≤ u) (hv : 0 ≤ v) (huv : u + v = 1) :
    m * (u * a + v * b) + c ≤ f (u * a + v * b) := by
  have h := hcv.2 (left_mem_Icc.mpr hab) (right_mem_Icc.mpr hab) hu hv huv
  simp only [smul_eq_mul] at h
  have e1 := mul_le_mul_of_nonneg_left ha hu
  have e2 := mul_le_mul_of_nonneg_left hb hv
  have hc : u * (m * a + c) + v * (m * b + c) = m * (u * a + v * b) + c * (u + v) := by ring
  rw [huv, mul_one] at hc
  linarith

/-- `|sin φ| ≤ sin h` for `|φ| ≤ h ≤ π/2` — the (A) envelope of Lemma RELAX. -/
theorem abs_sin_le_sin {φ h : ℝ} (hh : h ≤ Real.pi / 2) (hφ : |φ| ≤ h) :
    |Real.sin φ| ≤ Real.sin h := by
  have h0 : 0 ≤ h := le_trans (abs_nonneg φ) hφ
  obtain ⟨h1, h2⟩ := abs_le.mp hφ
  have mono : MonotoneOn Real.sin (Icc (-(Real.pi / 2)) (Real.pi / 2)) :=
    Real.strictMonoOn_sin.monotoneOn
  have mφ : φ ∈ Icc (-(Real.pi / 2)) (Real.pi / 2) := ⟨by linarith, by linarith⟩
  have mh : h ∈ Icc (-(Real.pi / 2)) (Real.pi / 2) := ⟨by linarith, hh⟩
  have mnh : -h ∈ Icc (-(Real.pi / 2)) (Real.pi / 2) := ⟨by linarith, by linarith⟩
  have e1 : Real.sin φ ≤ Real.sin h := mono mφ mh h2
  have e2 : Real.sin (-h) ≤ Real.sin φ := mono mnh mφ h1
  rw [Real.sin_neg] at e2
  exact abs_le.mpr ⟨by linarith, e1⟩

/-- `cos h ≤ cos φ` for `|φ| ≤ h ≤ π` — the correction term of Lemma RELAX (A). -/
theorem cos_ge_of_abs_le {φ h : ℝ} (hh : h ≤ Real.pi) (hφ : |φ| ≤ h) :
    Real.cos h ≤ Real.cos φ := by
  rw [← Real.cos_abs φ]
  exact Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg _) hh hφ

/-! ## 5. Lemma LEAF — one `linarith` per (cell, leaf), with the rational Farkas multipliers

The theorems below are generated from a certificate file: the variables are the LP's
(`s`, one `(x, y)` per free body, one `(u, v)` per pin, one tilt `t` per free body), the
hypotheses `h0 …` are that leaf's relaxed rows written `row ≤ 0` with rational coefficients, the
hypotheses `bl* / bh*` are the boxes and slack cores, and the conclusion is the kill
`s0 < s`.  `linarith` closes each one; the Farkas vector that certifies it (all multipliers of
the form `k / 2^40`) is listed in the docstring, row by row.
-/

/-- **LEAF 0 of `S02_k5_11_r0.10_rho10`** (Lemma LEAF, `docs/proofs/local_certificate.md` §2).  The
relaxed rows of one (tilt cell, selection) leaf, with the tilt cell
  BR(0,1) in [-0.087266, 0.000000] rad, f1 in [0.670819, 0.692636] rad, f2 in [0.670819, 0.714452] rad, f3 in [0.670819, 0.714452] rad
and the
selections BL(0,0)|BL(0,1) := (0, 1, 1), BR(0,1)|BR(0,0) := (0, 1, -1), f1|BL(0,1) := (0, 0, -1), f1|f2 := (0, 0, 1), f2|f3 := (0, 1, -1), f3|BR(0,1) := (0, 1, -1).  The certified bound of this leaf is 3.880427492 > s0 = 3.877084; the rational
Farkas multipliers (denominator 2^40) that produce it are

  h0    y = 299151032681/1099511627776  row s|BL(0,0)|BL(0,1)|1|1|0|A
  h1    y = 439422293789/1099511627776  row s|BR(0,1)|BR(0,0)|1|-1|0|B2
  h2    y = 234222140561/549755813888  row s|f1|BL(0,1)|0|-1|0|B2
  h3    y = 185695650539/1099511627776  row s|f1|f2|0|1|0|B2
  h4    y = 282748630583/1099511627776  row s|f1|f2|0|1|1|B2
  h5    y = 270420018909/1099511627776  row s|f2|f3|1|-1|0|A
  h6    y = 7633830245/137438953472  row s|f2|f3|1|-1|1|A
  h7    y = 237211954187/1099511627776  row s|f2|f3|1|-1|1|B1
  h8    y = 440759807199/1099511627776  row s|f3|BR(0,1)|1|-1|0|A
  h9    y = 63971403929/549755813888  row s|f3|BR(0,1)|1|-1|0|B1
  h10   y = 299151032681/1099511627776  row w|BL(0,0)|y|lo|0
  h11   y = 90130050341/274877906944  row w|BL(0,1)|x|lo|0
  h12   y = 439840393731/1099511627776  row w|BR(0,0)|y|lo|0
  h13   y = 360532366873/1099511627776  row w|BR(0,1)|x|hi|0
  h14   y = 184747856603/274877906944  row w|f2|y|hi|0
-/
theorem leaf_S02_k5_11_r0_10_rho10_0 (s v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 v19 v20 v21 v22 : ℝ)
    (bl0 : ((3819999999999999 : ℝ) / 1000000000000000) ≤ s) (bh0 : s ≤ ((974271 : ℝ) / 250000))
    (bl1 : ((1162500738528573 : ℝ) / 1000000000000000) ≤ v1) (bh1 : v1 ≤ ((681250369264287 : ℝ) / 500000000000000))
    (bl2 : ((2326657558641669 : ℝ) / 1000000000000000) ≤ v2) (bh2 : v2 ≤ ((252665755864167 : ℝ) / 100000000000000))
    (bl3 : ((912159714441131 : ℝ) / 500000000000000) ≤ v3) (bh3 : v3 ≤ ((2024319428882263 : ℝ) / 1000000000000000))
    (bl4 : ((3073002601983747 : ℝ) / 1000000000000000) ≤ v4) (bh4 : v4 ≤ ((818250650495937 : ℝ) / 250000000000000))
    (bl5 : ((2514583231546003 : ℝ) / 1000000000000000) ≤ v5) (bh5 : v5 ≤ ((678645807886501 : ℝ) / 250000000000000))
    (bl6 : ((2347940519654689 : ℝ) / 1000000000000000) ≤ v6) (bh6 : v6 ≤ ((254794051965469 : ℝ) / 100000000000000))
    (bl7 : ((3277083999999999 : ℝ) / 1000000000000000) ≤ v7) (bh7 : v7 ≤ ((3477084000000001 : ℝ) / 1000000000000000))
    (bl8 : ((1399999999999999 : ℝ) / 1000000000000000) ≤ v8) (bh8 : v8 ≤ ((1600000000000001 : ℝ) / 1000000000000000))
    (bl9 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v9) (bh9 : v9 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl10 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v10) (bh10 : v10 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl11 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v11) (bh11 : v11 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl12 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v12) (bh12 : v12 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl13 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v13) (bh13 : v13 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl14 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v14) (bh14 : v14 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl15 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v15) (bh15 : v15 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl16 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v16) (bh16 : v16 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl17 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v17) (bh17 : v17 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl18 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v18) (bh18 : v18 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl19 : ((83852380416659 : ℝ) / 125000000000000) ≤ v19) (bh19 : v19 ≤ ((346317829491601 : ℝ) / 500000000000000))
    (bl20 : ((83852380416659 : ℝ) / 125000000000000) ≤ v20) (bh20 : v20 ≤ ((714452274633131 : ℝ) / 1000000000000000))
    (bl21 : ((83852380416659 : ℝ) / 125000000000000) ≤ v21) (bh21 : v21 ≤ ((714452274633131 : ℝ) / 1000000000000000))
    (bl22 : ((-87266462599717 : ℝ) / 1000000000000000) ≤ v22) (bh22 : v22 ≤ (0 : ℝ))
    (h0 : (1 : ℝ) * v10 + (-1 : ℝ) * v12 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h1 : ((27685233343 : ℝ) / 1000000000000000) * s + ((-27685233343 : ℝ) / 1000000000000000) * v7 + ((-125118934549991 : ℝ) / 125000000000000) * v8 + ((27685233343 : ℝ) / 1000000000000000) * v17 + ((125118934549991 : ℝ) / 125000000000000) * v18 + ((-70502606497401 : ℝ) / 200000000000000) * v22 + ((150045946934283 : ℝ) / 100000000000000) ≤ 0)
    (h2 : ((-384805851936897 : ℝ) / 500000000000000) * v1 + ((-127721073662897 : ℝ) / 200000000000000) * v2 + ((384805851936897 : ℝ) / 500000000000000) * v11 + ((127721073662897 : ℝ) / 200000000000000) * v12 + ((-3818871403667 : ℝ) / 250000000000000) * v19 + ((1278680421486577 : ℝ) / 500000000000000) ≤ 0)
    (h3 : ((384805851936897 : ℝ) / 500000000000000) * v1 + ((127721073662897 : ℝ) / 200000000000000) * v2 + ((-384805851936897 : ℝ) / 500000000000000) * v3 + ((-127721073662897 : ℝ) / 200000000000000) * v4 + ((154668679800763 : ℝ) / 250000000000000) * v19 + ((-124960340049001 : ℝ) / 250000000000000) * v20 + ((28662993526703 : ℝ) / 31250000000000) ≤ 0)
    (h4 : ((384805851936897 : ℝ) / 500000000000000) * v1 + ((127721073662897 : ℝ) / 200000000000000) * v2 + ((-384805851936897 : ℝ) / 500000000000000) * v3 + ((-127721073662897 : ℝ) / 200000000000000) * v4 + ((-95252000297239 : ℝ) / 250000000000000) * v19 + ((124960340049001 : ℝ) / 250000000000000) * v20 + ((28662993526703 : ℝ) / 31250000000000) ≤ 0)
    (h5 : ((32131664468133 : ℝ) / 50000000000000) * v3 + ((-766192120158221 : ℝ) / 1000000000000000) * v4 + ((-32131664468133 : ℝ) / 50000000000000) * v5 + ((766192120158221 : ℝ) / 1000000000000000) * v6 + ((124960340049001 : ℝ) / 250000000000000) * v20 + ((-124960340049001 : ℝ) / 250000000000000) * v21 + ((19874815313537 : ℝ) / 20000000000000) ≤ 0)
    (h6 : ((32131664468133 : ℝ) / 50000000000000) * v3 + ((-766192120158221 : ℝ) / 1000000000000000) * v4 + ((-32131664468133 : ℝ) / 50000000000000) * v5 + ((766192120158221 : ℝ) / 1000000000000000) * v6 + ((-124960340049001 : ℝ) / 250000000000000) * v20 + ((124960340049001 : ℝ) / 250000000000000) * v21 + ((19874815313537 : ℝ) / 20000000000000) ≤ 0)
    (h7 : ((621778392586679 : ℝ) / 1000000000000000) * v3 + ((-195874257374269 : ℝ) / 250000000000000) * v4 + ((-621778392586679 : ℝ) / 1000000000000000) * v5 + ((195874257374269 : ℝ) / 250000000000000) * v6 + ((-849670104350849 : ℝ) / 1000000000000000) * v20 + ((124960340049001 : ℝ) / 250000000000000) * v21 + ((1234195288841949 : ℝ) / 1000000000000000) ≤ 0)
    (h8 : ((637463133803381 : ℝ) / 1000000000000000) * v5 + ((-770482195250999 : ℝ) / 1000000000000000) * v6 + ((-637463133803381 : ℝ) / 1000000000000000) * v7 + ((770482195250999 : ℝ) / 1000000000000000) * v8 + ((34700881785303 : ℝ) / 1000000000000000) * v21 + ((-34700881785303 : ℝ) / 1000000000000000) * v22 + ((1173075206125491 : ℝ) / 1000000000000000) ≤ 0)
    (h9 : ((621778392586679 : ℝ) / 1000000000000000) * v5 + ((-195874257374269 : ℝ) / 250000000000000) * v6 + ((-621778392586679 : ℝ) / 1000000000000000) * v7 + ((195874257374269 : ℝ) / 250000000000000) * v8 + ((-9135839039213 : ℝ) / 40000000000000) * v21 + ((-34700881785303 : ℝ) / 1000000000000000) * v22 + ((338920531558219 : ℝ) / 250000000000000) ≤ 0)
    (h10 : (-1 : ℝ) * v10 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h11 : (-1 : ℝ) * v11 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h12 : (-1 : ℝ) * v18 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h13 : (-1 : ℝ) * s + (1 : ℝ) * v7 + ((-477562848065269 : ℝ) / 1000000000000000) * v22 + ((249999999999999 : ℝ) / 500000000000000) ≤ 0)
    (h14 : (-1 : ℝ) * s + (1 : ℝ) * v4 + ((13098754126527 : ℝ) / 200000000000000) * v20 + ((6585358070323 : ℝ) / 10000000000000) ≤ 0) :
    (969271 : ℝ) / 250000 < s := by
  linarith


/-- **LEAF 1 of `S02_k5_11_r0.10_rho10`** (Lemma LEAF, `docs/proofs/local_certificate.md` §2).  The
relaxed rows of one (tilt cell, selection) leaf, with the tilt cell
  BR(0,1) in [-0.087266, 0.000000] rad, f1 in [0.692636, 0.714452] rad, f2 in [0.670819, 0.714452] rad, f3 in [0.670819, 0.714452] rad
and the
selections BL(0,0)|BL(0,1) := (0, 1, 1), BR(0,1)|BR(0,0) := (0, 1, -1), f1|BL(0,1) := (0, 0, -1), f1|f2 := (0, 0, 1), f2|f3 := (0, 1, -1), f3|BR(0,1) := (0, 1, -1).  The certified bound of this leaf is 3.879786047 > s0 = 3.877084; the rational
Farkas multipliers (denominator 2^40) that produce it are

  h0    y = 306513602703/1099511627776  row s|BL(0,0)|BL(0,1)|1|1|0|A
  h1    y = 427515961907/1099511627776  row s|BR(0,1)|BR(0,0)|1|-1|0|B2
  h2    y = 350309125643/1099511627776  row s|f1|BL(0,1)|0|-1|0|B1
  h3    y = 126371679687/1099511627776  row s|f1|BL(0,1)|0|-1|0|B2
  h4    y = 42120761133/274877906944  row s|f1|f2|0|1|0|A
  h5    y = 154098880399/549755813888  row s|f1|f2|0|1|0|B1
  h6    y = 69234113321/274877906944  row s|f2|f3|1|-1|0|A
  h7    y = 66777419281/549755813888  row s|f2|f3|1|-1|0|B2
  h8    y = 151948634843/1099511627776  row s|f2|f3|1|-1|1|B2
  h9    y = 98460039937/549755813888  row s|f3|BR(0,1)|1|-1|0|A
  h10   y = 182759923407/549755813888  row s|f3|BR(0,1)|1|-1|0|B2
  h11   y = 306513602703/1099511627776  row w|BL(0,0)|y|lo|0
  h12   y = 365075291817/1099511627776  row w|BL(0,1)|x|lo|0
  h13   y = 427922733255/1099511627776  row w|BR(0,0)|y|lo|0
  h14   y = 22817945481/68719476736  row w|BR(0,1)|x|hi|0
  h15   y = 734436335959/1099511627776  row w|f2|y|hi|0
-/
theorem leaf_S02_k5_11_r0_10_rho10_1 (s v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 v19 v20 v21 v22 : ℝ)
    (bl0 : ((3819999999999999 : ℝ) / 1000000000000000) ≤ s) (bh0 : s ≤ ((974271 : ℝ) / 250000))
    (bl1 : ((1162500738528573 : ℝ) / 1000000000000000) ≤ v1) (bh1 : v1 ≤ ((681250369264287 : ℝ) / 500000000000000))
    (bl2 : ((2326657558641669 : ℝ) / 1000000000000000) ≤ v2) (bh2 : v2 ≤ ((252665755864167 : ℝ) / 100000000000000))
    (bl3 : ((912159714441131 : ℝ) / 500000000000000) ≤ v3) (bh3 : v3 ≤ ((2024319428882263 : ℝ) / 1000000000000000))
    (bl4 : ((3073002601983747 : ℝ) / 1000000000000000) ≤ v4) (bh4 : v4 ≤ ((818250650495937 : ℝ) / 250000000000000))
    (bl5 : ((2514583231546003 : ℝ) / 1000000000000000) ≤ v5) (bh5 : v5 ≤ ((678645807886501 : ℝ) / 250000000000000))
    (bl6 : ((2347940519654689 : ℝ) / 1000000000000000) ≤ v6) (bh6 : v6 ≤ ((254794051965469 : ℝ) / 100000000000000))
    (bl7 : ((3277083999999999 : ℝ) / 1000000000000000) ≤ v7) (bh7 : v7 ≤ ((3477084000000001 : ℝ) / 1000000000000000))
    (bl8 : ((1399999999999999 : ℝ) / 1000000000000000) ≤ v8) (bh8 : v8 ≤ ((1600000000000001 : ℝ) / 1000000000000000))
    (bl9 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v9) (bh9 : v9 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl10 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v10) (bh10 : v10 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl11 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v11) (bh11 : v11 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl12 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v12) (bh12 : v12 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl13 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v13) (bh13 : v13 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl14 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v14) (bh14 : v14 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl15 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v15) (bh15 : v15 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl16 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v16) (bh16 : v16 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl17 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v17) (bh17 : v17 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl18 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v18) (bh18 : v18 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl19 : ((692635658983201 : ℝ) / 1000000000000000) ≤ v19) (bh19 : v19 ≤ ((714452274633131 : ℝ) / 1000000000000000))
    (bl20 : ((83852380416659 : ℝ) / 125000000000000) ≤ v20) (bh20 : v20 ≤ ((714452274633131 : ℝ) / 1000000000000000))
    (bl21 : ((83852380416659 : ℝ) / 125000000000000) ≤ v21) (bh21 : v21 ≤ ((714452274633131 : ℝ) / 1000000000000000))
    (bl22 : ((-87266462599717 : ℝ) / 1000000000000000) ≤ v22) (bh22 : v22 ≤ (0 : ℝ))
    (h0 : (1 : ℝ) * v10 + (-1 : ℝ) * v12 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h1 : ((27685233343 : ℝ) / 1000000000000000) * s + ((-27685233343 : ℝ) / 1000000000000000) * v7 + ((-125118934549991 : ℝ) / 125000000000000) * v8 + ((27685233343 : ℝ) / 1000000000000000) * v17 + ((125118934549991 : ℝ) / 125000000000000) * v18 + ((-70502606497401 : ℝ) / 200000000000000) * v22 + ((150045946934283 : ℝ) / 100000000000000) ≤ 0)
    (h2 : ((-769611151309673 : ℝ) / 1000000000000000) * v1 + ((-638606034233473 : ℝ) / 1000000000000000) * v2 + ((769611151309673 : ℝ) / 1000000000000000) * v11 + ((638606034233473 : ℝ) / 1000000000000000) * v12 + ((-153223495050343 : ℝ) / 500000000000000) * v19 + ((2759037337952291 : ℝ) / 1000000000000000) ≤ 0)
    (h3 : ((-755497454437053 : ℝ) / 1000000000000000) * v1 + ((-655242388371461 : ℝ) / 1000000000000000) * v2 + ((755497454437053 : ℝ) / 1000000000000000) * v11 + ((655242388371461 : ℝ) / 1000000000000000) * v12 + ((-461825095931 : ℝ) / 100000000000000) * v19 + ((1284619865656099 : ℝ) / 500000000000000) ≤ 0)
    (h4 : ((94878136441913 : ℝ) / 125000000000000) * v1 + ((651084227645291 : ℝ) / 1000000000000000) * v2 + ((-94878136441913 : ℝ) / 125000000000000) * v3 + ((-651084227645291 : ℝ) / 1000000000000000) * v4 + ((124960340049001 : ℝ) / 250000000000000) * v19 + ((-124960340049001 : ℝ) / 250000000000000) * v20 + ((199443655244907 : ℝ) / 200000000000000) ≤ 0)
    (h5 : ((769611151309673 : ℝ) / 1000000000000000) * v1 + ((638606034233473 : ℝ) / 1000000000000000) * v2 + ((-769611151309673 : ℝ) / 1000000000000000) * v3 + ((-638606034233473 : ℝ) / 1000000000000000) * v4 + ((76963567414421 : ℝ) / 1000000000000000) * v19 + ((-124960340049001 : ℝ) / 250000000000000) * v20 + ((129242425798153 : ℝ) / 100000000000000) ≤ 0)
    (h6 : ((32131664468133 : ℝ) / 50000000000000) * v3 + ((-766192120158221 : ℝ) / 1000000000000000) * v4 + ((-32131664468133 : ℝ) / 50000000000000) * v5 + ((766192120158221 : ℝ) / 1000000000000000) * v6 + ((124960340049001 : ℝ) / 250000000000000) * v20 + ((-124960340049001 : ℝ) / 250000000000000) * v21 + ((19874815313537 : ℝ) / 20000000000000) ≤ 0)
    (h7 : ((40959814268531 : ℝ) / 62500000000000) * v3 + ((-377817128443379 : ℝ) / 500000000000000) * v4 + ((-40959814268531 : ℝ) / 62500000000000) * v5 + ((377817128443379 : ℝ) / 500000000000000) * v6 + ((713265957494561 : ℝ) / 1000000000000000) * v20 + ((-124960340049001 : ℝ) / 250000000000000) * v21 + ((423520908177451 : ℝ) / 500000000000000) ≤ 0)
    (h8 : ((40959814268531 : ℝ) / 62500000000000) * v3 + ((-377817128443379 : ℝ) / 500000000000000) * v4 + ((-40959814268531 : ℝ) / 62500000000000) * v5 + ((377817128443379 : ℝ) / 500000000000000) * v6 + ((-286416762897447 : ℝ) / 1000000000000000) * v20 + ((124960340049001 : ℝ) / 250000000000000) * v21 + ((423520908177451 : ℝ) / 500000000000000) ≤ 0)
    (h9 : ((637463133803381 : ℝ) / 1000000000000000) * v5 + ((-770482195250999 : ℝ) / 1000000000000000) * v6 + ((-637463133803381 : ℝ) / 1000000000000000) * v7 + ((770482195250999 : ℝ) / 1000000000000000) * v8 + ((34700881785303 : ℝ) / 1000000000000000) * v21 + ((-34700881785303 : ℝ) / 1000000000000000) * v22 + ((1173075206125491 : ℝ) / 1000000000000000) ≤ 0)
    (h10 : ((40959814268531 : ℝ) / 62500000000000) * v5 + ((-377817128443379 : ℝ) / 500000000000000) * v6 + ((-40959814268531 : ℝ) / 62500000000000) * v7 + ((377817128443379 : ℝ) / 500000000000000) * v8 + ((334857365473077 : ℝ) / 1000000000000000) * v21 + ((-34700881785303 : ℝ) / 1000000000000000) * v22 + ((482372130642967 : ℝ) / 500000000000000) ≤ 0)
    (h11 : (-1 : ℝ) * v10 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h12 : (-1 : ℝ) * v11 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h13 : (-1 : ℝ) * v18 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h14 : (-1 : ℝ) * s + (1 : ℝ) * v7 + ((-477562848065269 : ℝ) / 1000000000000000) * v22 + ((249999999999999 : ℝ) / 500000000000000) ≤ 0)
    (h15 : (-1 : ℝ) * s + (1 : ℝ) * v4 + ((13098754126527 : ℝ) / 200000000000000) * v20 + ((6585358070323 : ℝ) / 10000000000000) ≤ 0) :
    (969271 : ℝ) / 250000 < s := by
  linarith


/-- **LEAF 2 of `S02_k5_11_r0.10_rho10`** (Lemma LEAF, `docs/proofs/local_certificate.md` §2).  The
relaxed rows of one (tilt cell, selection) leaf, with the tilt cell
  BR(0,1) in [-0.174533, 0.000000] rad, f1 in [0.670819, 0.714452] rad, f2 in [0.670819, 0.714452] rad, f3 in [0.714452, 0.758086] rad
and the
selections BL(0,0)|BL(0,1) := (0, 1, 1), BR(0,1)|BR(0,0) := (0, 1, -1), f1|BL(0,1) := (0, 0, -1), f1|f2 := (0, 0, 1), f1|f3 := (0, 0, 1), f2|f3 := (0, 1, -1), f3|BR(0,1) := (0, 1, -1).  The certified bound of this leaf is 3.885037323 > s0 = 3.877084; the rational
Farkas multipliers (denominator 2^40) that produce it are

  h0    y = 9866601921/34359738368  row s|BL(0,0)|BL(0,1)|1|1|0|A
  h1    y = 418149393969/1099511627776  row s|BR(0,1)|BR(0,0)|1|-1|0|B2
  h2    y = 120442708887/274877906944  row s|f1|BL(0,1)|0|-1|0|A
  h3    y = 73362643033/549755813888  row s|f1|f2|0|1|0|B2
  h4    y = 335040726129/1099511627776  row s|f1|f2|0|1|1|B2
  h5    y = 3844295/1099511627776   row s|f1|f3|0|1|0|B2
  h6    y = 555481801369/1099511627776  row s|f2|f3|1|-1|0|B2
  h7    y = 277740900691/549755813888  row s|f3|BR(0,1)|1|-1|0|B1
  h8    y = 9866601921/34359738368  row w|BL(0,0)|y|lo|0
  h9    y = 364043079721/1099511627776  row w|BL(0,1)|x|lo|0
  h10   y = 419738558805/1099511627776  row w|BR(0,0)|y|lo|0
  h11   y = 364134367119/1099511627776  row w|BR(0,1)|x|hi|0
  h12   y = 735469820277/1099511627776  row w|f2|y|hi|0
-/
theorem leaf_S02_k5_11_r0_10_rho10_2 (s v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 v19 v20 v21 v22 : ℝ)
    (bl0 : ((3819999999999999 : ℝ) / 1000000000000000) ≤ s) (bh0 : s ≤ ((974271 : ℝ) / 250000))
    (bl1 : ((1162500738528573 : ℝ) / 1000000000000000) ≤ v1) (bh1 : v1 ≤ ((681250369264287 : ℝ) / 500000000000000))
    (bl2 : ((2326657558641669 : ℝ) / 1000000000000000) ≤ v2) (bh2 : v2 ≤ ((252665755864167 : ℝ) / 100000000000000))
    (bl3 : ((912159714441131 : ℝ) / 500000000000000) ≤ v3) (bh3 : v3 ≤ ((2024319428882263 : ℝ) / 1000000000000000))
    (bl4 : ((3073002601983747 : ℝ) / 1000000000000000) ≤ v4) (bh4 : v4 ≤ ((818250650495937 : ℝ) / 250000000000000))
    (bl5 : ((2514583231546003 : ℝ) / 1000000000000000) ≤ v5) (bh5 : v5 ≤ ((678645807886501 : ℝ) / 250000000000000))
    (bl6 : ((2347940519654689 : ℝ) / 1000000000000000) ≤ v6) (bh6 : v6 ≤ ((254794051965469 : ℝ) / 100000000000000))
    (bl7 : ((3277083999999999 : ℝ) / 1000000000000000) ≤ v7) (bh7 : v7 ≤ ((3477084000000001 : ℝ) / 1000000000000000))
    (bl8 : ((1399999999999999 : ℝ) / 1000000000000000) ≤ v8) (bh8 : v8 ≤ ((1600000000000001 : ℝ) / 1000000000000000))
    (bl9 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v9) (bh9 : v9 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl10 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v10) (bh10 : v10 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl11 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v11) (bh11 : v11 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl12 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v12) (bh12 : v12 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl13 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v13) (bh13 : v13 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl14 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v14) (bh14 : v14 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl15 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v15) (bh15 : v15 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl16 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v16) (bh16 : v16 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl17 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v17) (bh17 : v17 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl18 : ((-3535533905933 : ℝ) / 500000000000000) ≤ v18) (bh18 : v18 ≤ ((3535533905933 : ℝ) / 500000000000000))
    (bl19 : ((83852380416659 : ℝ) / 125000000000000) ≤ v19) (bh19 : v19 ≤ ((714452274633131 : ℝ) / 1000000000000000))
    (bl20 : ((83852380416659 : ℝ) / 125000000000000) ≤ v20) (bh20 : v20 ≤ ((714452274633131 : ℝ) / 1000000000000000))
    (bl21 : ((71445227463313 : ℝ) / 100000000000000) ≤ v21) (bh21 : v21 ≤ ((758085505932989 : ℝ) / 1000000000000000))
    (bl22 : ((-174532925199433 : ℝ) / 1000000000000000) ≤ v22) (bh22 : v22 ≤ (0 : ℝ))
    (h0 : (1 : ℝ) * v10 + (-1 : ℝ) * v12 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h1 : ((221355384599 : ℝ) / 1000000000000000) * s + ((-221355384599 : ℝ) / 1000000000000000) * v7 + ((-200760094291317 : ℝ) / 200000000000000) * v8 + ((221355384599 : ℝ) / 1000000000000000) * v17 + ((200760094291317 : ℝ) / 200000000000000) * v18 + ((-368236279423267 : ℝ) / 1000000000000000) * v22 + ((1501764849784629 : ℝ) / 1000000000000000) ≤ 0)
    (h2 : ((-755635362001851 : ℝ) / 1000000000000000) * v1 + ((-655355696474367 : ℝ) / 1000000000000000) * v2 + ((755635362001851 : ℝ) / 1000000000000000) * v11 + ((655355696474367 : ℝ) / 1000000000000000) * v12 + ((13098754126527 : ℝ) / 200000000000000) * v19 + ((314923379093097 : ℝ) / 125000000000000) ≤ 0)
    (h3 : ((377817128443379 : ℝ) / 500000000000000) * v1 + ((40959814268531 : ℝ) / 62500000000000) * v2 + ((-377817128443379 : ℝ) / 500000000000000) * v3 + ((-40959814268531 : ℝ) / 62500000000000) * v4 + ((125944514685333 : ℝ) / 200000000000000) * v19 + ((-124960340049001 : ℝ) / 250000000000000) * v20 + ((181345886509571 : ℝ) / 200000000000000) ≤ 0)
    (h4 : ((377817128443379 : ℝ) / 500000000000000) * v1 + ((40959814268531 : ℝ) / 62500000000000) * v2 + ((-377817128443379 : ℝ) / 500000000000000) * v3 + ((-40959814268531 : ℝ) / 62500000000000) * v4 + ((-369960146965343 : ℝ) / 1000000000000000) * v19 + ((124960340049001 : ℝ) / 250000000000000) * v20 + ((181345886509571 : ℝ) / 200000000000000) ≤ 0)
    (h5 : ((377817128443379 : ℝ) / 500000000000000) * v1 + ((40959814268531 : ℝ) / 62500000000000) * v2 + ((-377817128443379 : ℝ) / 500000000000000) * v5 + ((-40959814268531 : ℝ) / 62500000000000) * v6 + ((651081408974713 : ℝ) / 1000000000000000) * v19 + ((477562848065269 : ℝ) / 1000000000000000) * v21 + ((9681779500529 : ℝ) / 50000000000000) ≤ 0)
    (h6 : ((40959814268531 : ℝ) / 62500000000000) * v3 + ((-377817128443379 : ℝ) / 500000000000000) * v4 + ((-40959814268531 : ℝ) / 62500000000000) * v5 + ((377817128443379 : ℝ) / 500000000000000) * v6 + ((-33017281345839 : ℝ) / 125000000000000) * v20 + ((477562848065269 : ℝ) / 1000000000000000) * v21 + ((847517705563973 : ℝ) / 1000000000000000) ≤ 0)
    (h7 : ((655362257760971 : ℝ) / 1000000000000000) * v5 + ((-94453715171511 : ℝ) / 125000000000000) * v6 + ((-655362257760971 : ℝ) / 1000000000000000) * v7 + ((94453715171511 : ℝ) / 125000000000000) * v8 + ((-237837255576117 : ℝ) / 1000000000000000) * v21 + ((6726773201479 : ℝ) / 250000000000000) * v22 + ((1375250735895693 : ℝ) / 1000000000000000) ≤ 0)
    (h8 : (-1 : ℝ) * v10 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h9 : (-1 : ℝ) * v11 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h10 : (-1 : ℝ) * v18 + ((-1 : ℝ) / 1000000000000000) ≤ 0)
    (h11 : (-1 : ℝ) * s + (1 : ℝ) * v7 + ((-453942803336609 : ℝ) / 1000000000000000) * v22 + ((249999999999999 : ℝ) / 500000000000000) ≤ 0)
    (h12 : (-1 : ℝ) * s + (1 : ℝ) * v4 + ((13098754126527 : ℝ) / 200000000000000) * v20 + ((6585358070323 : ℝ) / 10000000000000) ≤ 0) :
    (969271 : ℝ) / 250000 < s := by
  linarith

/-! ## 6. Theorem LOCAL and the composition into `ClassKilledAt` -/

/-- **Lemma COVER, one pair** (the step `sat_selection` is for): if every selection with `qw` as
owner is IMPOSSIBLE on the cell (the interval enclosures the certificate records), an
interior-disjoint pair must use one of the selections with `qo` as owner. -/
theorem cover_pair (qw qo : PSq) (h : Disjoint (interior qw.set) (interior qo.set))
    (hexc : ∀ (k : Bool) (eps : ℝ), (eps = 1 ∨ eps = -1) → gsel qw qo k eps < 0) :
    ∃ k : Bool, ∃ eps : ℝ, (eps = 1 ∨ eps = -1) ∧ 0 ≤ gsel qo qw k eps := by
  rcases sat_selection qw qo h with ⟨k, e, he, hg⟩ | h2
  · exact absurd hg (not_le.mpr (hexc k e he))
  · exact h2

/-- `LocalDead` from the leaf kills in contradiction form: if no packing satisfying `N` has side
`≤ s0`, then every one has side `> s0`.  (`LocalDead` is definitionally the second form; this is
the shape the tree produces, one `False` per closed leaf.) -/
theorem localDead_of_contradiction {Ls : List Box} {Ps : List Pin} {s0 : ℝ}
    (h : ∀ s : ℝ, ∀ z : Cfg, CfgPacking s z → LocalHyp Ls Ps s z → s ≤ s0 → False) :
    LocalDead Ls Ps s0 :=
  fun s z hz hN => not_le.mp fun hle => h s z hz hN hle

/-- **Theorem LOCAL, consumer form** (`local_certificate.md` §8, T3(a)): a node of class `i`
whose YES branch is the box hypothesis `N` — the class pins plus one box per `ℓ ∈ L` plus the
tilt cut — dies, in the shape `Composition.lean` consumes. -/
theorem classKilledAt_of_localDead {Ls : List Box} {Ps : List Pin} {i : StratumIdx} {m : ℝ}
    (hD : LocalDead Ls Ps shat)
    (hyp : ∀ z : Cfg, CfgPacking m z → InStratum i m z → LocalHyp Ls Ps m z) :
    ClassKilledAt i m := by
  intro z hz hi
  have h := hD m z hz (hyp z hz hi)
  refine ⟨h.le, fun he => ?_⟩
  rw [he] at h
  exact absurd h (lt_irrefl _)

/-- The YES leaf of A112's region tree: at any side `m ≤ s0` the hypothesis is contradictory. -/
theorem localKill_yes {Ls : List Box} {Ps : List Pin} {s0 m : ℝ}
    (hD : LocalDead Ls Ps s0) (hm : m ≤ s0) (z : Cfg)
    (hz : CfgPacking m z) (hN : LocalHyp Ls Ps m z) : False := by
  have := hD m z hz hN
  linarith

end

end LocalCert
end S11
end PackingCert
