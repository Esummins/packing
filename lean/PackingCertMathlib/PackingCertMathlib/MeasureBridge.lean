import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.MeasureChecker

/-!
# The measure bridge (A64, depgraph node A.F2)

Soundness of the lower-bound measure checker `checkMeasureI`
(`MeasureChecker.lean`, byte-identical copy of `lean/PackingCert/PackingCert/MeasureInt.lean`):

    `checkMeasureI c = true`  ⟹  every closed unit square `Q ⊆ [0, s]²` has `μ(Q) ≥ 1`
                              ⟹  no `c.n` unit squares pack in any side `< s`,

with `μ = Σ wᵢ δ_{pᵢ}` the certificate's atomic measure and `s = c.sNum / c.sDen`.  This is
the A28 §7 item 4 obligation ("bridge lemma (assumed)" in the `MeasureInt.lean` header),
formalised.  Composed with the `native_decide` evaluation of the checker on
`certs/measure_certificate_3.82.json` (`Measure382.lean`) it yields the end-to-end theorem
`s(11) ≥ 3.82` — discharging the `lb_382` axiom of `TopLevel.lean`.

Structure:

* real semantics: `atomPt`, `massIn` (mass of an atom list inside a set);
* exact interval arithmetic over ℝ with `Int` endpoints (`mul_bounds`, `imul4_bounds`);
* the `t = T/2^K` grid: exact rational values of `cosT`/`sinT` at grid points
  (`cosT_grid`, `sinT_grid`), monotonicity (`cosT_anti`, `sinT_mono`), and the box
  enclosure (`trig_enclosure`);
* soundness of the checker's box predicates: `projI`/`insideAll`/`outsideAll`
  (`projI_sound`), clipping (`clipI_sound`, via `wT_ge_min`), splitting (`splitI_sound`),
  atom sifting (`sift_sound`), and the branch-and-bound recursion (`go_sound`);
* the coverage theorem `checkMeasureI_coverage` and the two-line counting/scaling argument
  `coverage_no_packing` (scale the packing up to side `s`, shrink each square about its
  centre: the shrunk squares are pairwise disjoint closed unit squares in `[0,s]²`, each of
  mass ≥ 1, total ≥ n > Σ wᵢ — contradiction), giving `checkMeasureI_no_packing`.
-/

namespace PackingCert
namespace S11

open Set MeasureI

noncomputable section

/-! ## Real semantics of the certificate data -/

/-- The real point denoted by an integer atom (`px/pd`, `py/pd`). -/
def atomPt (a : IAtom) : RP := ((a.px : ℝ) / (a.pd : ℝ), (a.py : ℝ) / (a.pd : ℝ))

/-- The (scaled, `wd`-denominated) mass an atom list gives to a set: `Σ {w : p ∈ Q}`. -/
def massIn (l : List IAtom) (Q : Set RP) : ℝ :=
  (l.map fun a => Q.indicator (fun _ => (a.w : ℝ)) (atomPt a)).sum

@[simp] theorem massIn_nil (Q : Set RP) : massIn [] Q = 0 := rfl

theorem massIn_cons (a : IAtom) (l : List IAtom) (Q : Set RP) :
    massIn (a :: l) Q = Q.indicator (fun _ => (a.w : ℝ)) (atomPt a) + massIn l Q := by
  simp [massIn]

theorem massIn_nonneg {l : List IAtom} (hl : ∀ a ∈ l, 0 ≤ a.w) (Q : Set RP) :
    0 ≤ massIn l Q := by
  refine List.sum_nonneg ?_
  intro x hx
  simp only [List.mem_map] at hx
  obtain ⟨a, ha, rfl⟩ := hx
  exact Set.indicator_nonneg (fun _ _ => by exact_mod_cast hl a ha) _

/-! ## Interval arithmetic over ℝ with integer endpoints -/

/-- The four-corner product bound: if `x ∈ [A0, A1]` and `y ∈ [B0, B1]` then `x·y` lies
between the min and the max of the four corner products. -/
theorem mul_bounds {A0 A1 B0 B1 x y : ℝ} (hx0 : A0 ≤ x) (hx1 : x ≤ A1)
    (hy0 : B0 ≤ y) (hy1 : y ≤ B1) :
    min (min (A0 * B0) (A0 * B1)) (min (A1 * B0) (A1 * B1)) ≤ x * y ∧
      x * y ≤ max (max (A0 * B0) (A0 * B1)) (max (A1 * B0) (A1 * B1)) := by
  constructor
  · rcases le_total 0 y with hy | hy
    · have h1 : A0 * y ≤ x * y := mul_le_mul_of_nonneg_right hx0 hy
      rcases le_total 0 A0 with hA | hA
      · have h2 : A0 * B0 ≤ A0 * y := mul_le_mul_of_nonneg_left hy0 hA
        exact le_trans (le_trans (min_le_left _ _) (min_le_left _ _)) (by linarith)
      · have h2 : A0 * B1 ≤ A0 * y := mul_le_mul_of_nonpos_left hy1 hA
        exact le_trans (le_trans (min_le_left _ _) (min_le_right _ _)) (by linarith)
    · have h1 : A1 * y ≤ x * y := mul_le_mul_of_nonpos_right hx1 hy
      rcases le_total 0 A1 with hA | hA
      · have h2 : A1 * B0 ≤ A1 * y := mul_le_mul_of_nonneg_left hy0 hA
        exact le_trans (le_trans (min_le_right _ _) (min_le_left _ _)) (by linarith)
      · have h2 : A1 * B1 ≤ A1 * y := mul_le_mul_of_nonpos_left hy1 hA
        exact le_trans (le_trans (min_le_right _ _) (min_le_right _ _)) (by linarith)
  · rcases le_total 0 y with hy | hy
    · have h1 : x * y ≤ A1 * y := mul_le_mul_of_nonneg_right hx1 hy
      rcases le_total 0 A1 with hA | hA
      · have h2 : A1 * y ≤ A1 * B1 := mul_le_mul_of_nonneg_left hy1 hA
        exact le_trans (by linarith) (le_trans (le_max_right _ _) (le_max_right _ _))
      · have h2 : A1 * y ≤ A1 * B0 := mul_le_mul_of_nonpos_left hy0 hA
        exact le_trans (by linarith) (le_trans (le_max_left _ _) (le_max_right _ _))
    · have h1 : x * y ≤ A0 * y := mul_le_mul_of_nonpos_right hx0 hy
      rcases le_total 0 A0 with hA | hA
      · have h2 : A0 * y ≤ A0 * B1 := mul_le_mul_of_nonneg_left hy1 hA
        exact le_trans (by linarith) (le_trans (le_max_right _ _) (le_max_left _ _))
      · have h2 : A0 * y ≤ A0 * B0 := mul_le_mul_of_nonpos_left hy0 hA
        exact le_trans (by linarith) (le_trans (le_max_left _ _) (le_max_left _ _))

/-- `imul4` really encloses the product. -/
theorem imul4_bounds {a0 a1 b0 b1 : Int} {x y : ℝ}
    (hx0 : (a0 : ℝ) ≤ x) (hx1 : x ≤ (a1 : ℝ)) (hy0 : (b0 : ℝ) ≤ y) (hy1 : y ≤ (b1 : ℝ)) :
    ((imul4 a0 a1 b0 b1).1 : ℝ) ≤ x * y ∧ x * y ≤ ((imul4 a0 a1 b0 b1).2 : ℝ) := by
  have h := mul_bounds hx0 hx1 hy0 hy1
  simp only [imul4]
  constructor
  · push_cast
    exact h.1
  · push_cast
    exact h.2

/-- `imul4_bounds` with the min/max spelled out (the form appearing after unfolding). -/
theorem imul4_cast_bounds {a0 a1 b0 b1 : Int} {x y : ℝ}
    (hx0 : (a0 : ℝ) ≤ x) (hx1 : x ≤ (a1 : ℝ)) (hy0 : (b0 : ℝ) ≤ y) (hy1 : y ≤ (b1 : ℝ)) :
    ((min (min (a0 * b0) (a0 * b1)) (min (a1 * b0) (a1 * b1)) : Int) : ℝ) ≤ x * y ∧
      x * y ≤ ((max (max (a0 * b0) (a0 * b1)) (max (a1 * b0) (a1 * b1)) : Int) : ℝ) := by
  simpa only [imul4] using imul4_bounds hx0 hx1 hy0 hy1

/-- Integer (Euclidean) division by a positive divisor is a lower bound for real division. -/
theorem cast_ediv_le {A B : Int} (hB : 0 < B) : ((A / B : Int) : ℝ) ≤ (A : ℝ) / (B : ℝ) := by
  have hBR : (0 : ℝ) < (B : ℝ) := by exact_mod_cast hB
  rw [le_div_iff₀ hBR]
  have h1 : A % B = A - B * (A / B) := Int.emod_def A B
  have h2 : 0 ≤ A % B := Int.emod_nonneg A hB.ne'
  have h3 : (A / B) * B ≤ A := by rw [mul_comm]; linarith
  exact_mod_cast h3

/-! ## The `t = T/2^K` grid -/

section CtxFacts

variable {ctx : Ctx}

theorem dn_pos (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (T : Int) : 0 < ((ctx.P4 + T * T : Int) : ℝ) := by
  push_cast
  rw [hP4]
  nlinarith [mul_self_nonneg (T : ℝ)]

/-- Exact value of `cosT` at a grid point. -/
theorem cosT_grid (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (T : Int) :
    cosT ((T : ℝ) / (ctx.TROOT : ℝ))
      = ((ctx.P4 - T * T : Int) : ℝ) / ((ctx.P4 + T * T : Int) : ℝ) := by
  have hRne : (ctx.TROOT : ℝ) ≠ 0 := hR.ne'
  rw [cosT, div_eq_div_iff (one_add_sq_pos _).ne' (dn_pos hP4 hR T).ne']
  push_cast
  rw [hP4]
  field_simp

/-- Exact value of `sinT` at a grid point. -/
theorem sinT_grid (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (T : Int) :
    sinT ((T : ℝ) / (ctx.TROOT : ℝ))
      = ((2 * T * ctx.TROOT : Int) : ℝ) / ((ctx.P4 + T * T : Int) : ℝ) := by
  have hRne : (ctx.TROOT : ℝ) ≠ 0 := hR.ne'
  rw [sinT, div_eq_div_iff (one_add_sq_pos _).ne' (dn_pos hP4 hR T).ne']
  push_cast
  rw [hP4]
  field_simp

/-- `cosT` is antitone on `[0, ∞)` — pure algebra. -/
theorem cosT_anti {a b : ℝ} (ha : 0 ≤ a) (hab : a ≤ b) : cosT b ≤ cosT a := by
  have key : cosT a - cosT b = 2 * (b ^ 2 - a ^ 2) / ((1 + a ^ 2) * (1 + b ^ 2)) := by
    have h1 : (1 + a ^ 2 : ℝ) ≠ 0 := (one_add_sq_pos a).ne'
    have h2 : (1 + b ^ 2 : ℝ) ≠ 0 := (one_add_sq_pos b).ne'
    unfold cosT
    field_simp
    ring
  have h3 : 0 ≤ cosT a - cosT b := by
    rw [key]
    exact div_nonneg (by nlinarith) (by positivity)
  linarith

/-- `sinT` is monotone on `[0, 1]` — pure algebra. -/
theorem sinT_mono {a b : ℝ} (ha : 0 ≤ a) (hab : a ≤ b) (hb : b ≤ 1) : sinT a ≤ sinT b := by
  have key : sinT b - sinT a = 2 * (b - a) * (1 - a * b) / ((1 + a ^ 2) * (1 + b ^ 2)) := by
    have h1 : (1 + a ^ 2 : ℝ) ≠ 0 := (one_add_sq_pos a).ne'
    have h2 : (1 + b ^ 2 : ℝ) ≠ 0 := (one_add_sq_pos b).ne'
    unfold sinT
    field_simp
    ring
  have hab1 : a * b ≤ 1 := by nlinarith
  have h3 : 0 ≤ sinT b - sinT a := by
    rw [key]
    exact div_nonneg (by nlinarith) (by positivity)
  linarith

/-- The box trig enclosure, stated on the literal components of
`boxTrig ctx T0 T1 = (cn1·dn0, cn0·dn1, sn0·dn1, sn1·dn0, dn0·dn1)`:
for `t` with `T0 ≤ t·2^K ≤ T1` (and `0 ≤ T0`, `T1 ≤ 2^K`),

    Clo ≤ cosT t · E ≤ Chi   and   Slo ≤ sinT t · E ≤ Shi,   E > 0. -/
theorem trig_enclosure (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2)
    (hR : 0 < (ctx.TROOT : ℝ)) {T0 T1 : Int} (hT0 : 0 ≤ T0) (hT1 : (T1 : ℝ) ≤ ctx.TROOT)
    {t : ℝ} (h0 : (T0 : ℝ) ≤ t * ctx.TROOT) (h1 : t * ctx.TROOT ≤ (T1 : ℝ)) :
    0 < (((ctx.P4 + T0 * T0) * (ctx.P4 + T1 * T1) : Int) : ℝ) ∧
    (((ctx.P4 - T1 * T1) * (ctx.P4 + T0 * T0) : Int) : ℝ)
        ≤ cosT t * (((ctx.P4 + T0 * T0) * (ctx.P4 + T1 * T1) : Int) : ℝ) ∧
    cosT t * (((ctx.P4 + T0 * T0) * (ctx.P4 + T1 * T1) : Int) : ℝ)
        ≤ (((ctx.P4 - T0 * T0) * (ctx.P4 + T1 * T1) : Int) : ℝ) ∧
    ((2 * T0 * ctx.TROOT * (ctx.P4 + T1 * T1) : Int) : ℝ)
        ≤ sinT t * (((ctx.P4 + T0 * T0) * (ctx.P4 + T1 * T1) : Int) : ℝ) ∧
    sinT t * (((ctx.P4 + T0 * T0) * (ctx.P4 + T1 * T1) : Int) : ℝ)
        ≤ ((2 * T1 * ctx.TROOT * (ctx.P4 + T0 * T0) : Int) : ℝ) := by
  have hRne : (ctx.TROOT : ℝ) ≠ 0 := hR.ne'
  have hdn0 : (0 : ℝ) < ((ctx.P4 + T0 * T0 : Int) : ℝ) := dn_pos hP4 hR T0
  have hdn1 : (0 : ℝ) < ((ctx.P4 + T1 * T1 : Int) : ℝ) := dn_pos hP4 hR T1
  have ht0 : (T0 : ℝ) / (ctx.TROOT : ℝ) ≤ t := by
    rw [div_le_iff₀ hR]; exact h0
  have ht1 : t ≤ (T1 : ℝ) / (ctx.TROOT : ℝ) := by
    rw [le_div_iff₀ hR]; exact h1
  have htt0 : (0 : ℝ) ≤ (T0 : ℝ) / (ctx.TROOT : ℝ) :=
    div_nonneg (by exact_mod_cast hT0) hR.le
  have htt1 : (T1 : ℝ) / (ctx.TROOT : ℝ) ≤ 1 := (div_le_one hR).mpr hT1
  have htnn : 0 ≤ t := le_trans htt0 ht0
  have ht1' : t ≤ 1 := le_trans ht1 htt1
  have hcu : cosT t ≤ cosT ((T0 : ℝ) / (ctx.TROOT : ℝ)) := cosT_anti htt0 ht0
  have hcl : cosT ((T1 : ℝ) / (ctx.TROOT : ℝ)) ≤ cosT t := cosT_anti htnn ht1
  have hsl : sinT ((T0 : ℝ) / (ctx.TROOT : ℝ)) ≤ sinT t := sinT_mono htt0 ht0 ht1'
  have hsu : sinT t ≤ sinT ((T1 : ℝ) / (ctx.TROOT : ℝ)) := sinT_mono htnn ht1 htt1
  rw [cosT_grid hP4 hR T0] at hcu
  rw [cosT_grid hP4 hR T1] at hcl
  rw [sinT_grid hP4 hR T0] at hsl
  rw [sinT_grid hP4 hR T1] at hsu
  have hE : (0 : ℝ) < ((ctx.P4 + T0 * T0 : Int) : ℝ) * ((ctx.P4 + T1 * T1 : Int) : ℝ) :=
    mul_pos hdn0 hdn1
  refine ⟨by exact_mod_cast hE, ?_, ?_, ?_, ?_⟩
  · -- Clo ≤ cos · E
    have h := mul_le_mul_of_nonneg_right hcl hE.le
    have heq : ((ctx.P4 - T1 * T1 : Int) : ℝ) / ((ctx.P4 + T1 * T1 : Int) : ℝ)
          * (((ctx.P4 + T0 * T0 : Int) : ℝ) * ((ctx.P4 + T1 * T1 : Int) : ℝ))
        = ((ctx.P4 - T1 * T1 : Int) : ℝ) * ((ctx.P4 + T0 * T0 : Int) : ℝ) := by
      field_simp
    rw [heq] at h
    exact_mod_cast h
  · -- cos · E ≤ Chi
    have h := mul_le_mul_of_nonneg_right hcu hE.le
    have heq : ((ctx.P4 - T0 * T0 : Int) : ℝ) / ((ctx.P4 + T0 * T0 : Int) : ℝ)
          * (((ctx.P4 + T0 * T0 : Int) : ℝ) * ((ctx.P4 + T1 * T1 : Int) : ℝ))
        = ((ctx.P4 - T0 * T0 : Int) : ℝ) * ((ctx.P4 + T1 * T1 : Int) : ℝ) := by
      field_simp
    rw [heq] at h
    exact_mod_cast h
  · -- Slo ≤ sin · E
    have h := mul_le_mul_of_nonneg_right hsl hE.le
    have heq : ((2 * T0 * ctx.TROOT : Int) : ℝ) / ((ctx.P4 + T0 * T0 : Int) : ℝ)
          * (((ctx.P4 + T0 * T0 : Int) : ℝ) * ((ctx.P4 + T1 * T1 : Int) : ℝ))
        = ((2 * T0 * ctx.TROOT : Int) : ℝ) * ((ctx.P4 + T1 * T1 : Int) : ℝ) := by
      field_simp
    rw [heq] at h
    exact_mod_cast h
  · -- sin · E ≤ Shi
    have h := mul_le_mul_of_nonneg_right hsu hE.le
    have heq : ((2 * T1 * ctx.TROOT : Int) : ℝ) / ((ctx.P4 + T1 * T1 : Int) : ℝ)
          * (((ctx.P4 + T0 * T0 : Int) : ℝ) * ((ctx.P4 + T1 * T1 : Int) : ℝ))
        = ((2 * T1 * ctx.TROOT : Int) : ℝ) * ((ctx.P4 + T0 * T0 : Int) : ℝ) := by
      field_simp
    rw [heq] at h
    exact_mod_cast h

/-! ## Real semantics of boxes -/

/-- The real parameter block a scaled integer box denotes:
`t·2^K ∈ [T0, T1]`, `cx·D ∈ [X0, X1]`, `cy·D ∈ [Y0, Y1]`. -/
def inBox (ctx : Ctx) (b : IBox) (q : PSq) : Prop :=
  (b.T0 : ℝ) ≤ q.t * (ctx.TROOT : ℝ) ∧ q.t * (ctx.TROOT : ℝ) ≤ (b.T1 : ℝ) ∧
  (b.X0 : ℝ) ≤ q.cx * (ctx.D : ℝ) ∧ q.cx * (ctx.D : ℝ) ≤ (b.X1 : ℝ) ∧
  (b.Y0 : ℝ) ≤ q.cy * (ctx.D : ℝ) ∧ q.cy * (ctx.D : ℝ) ≤ (b.Y1 : ℝ)

/-- Admissibility at side `s`: the centre bounds equivalent (for `t ∈ [0,1]`) to
`q.set ⊆ [0,s]²` (`set_subset_container_iff`). -/
def Adm (s : ℝ) (q : PSq) : Prop :=
  wT q.t / 2 ≤ q.cx ∧ q.cx ≤ s - wT q.t / 2 ∧ wT q.t / 2 ≤ q.cy ∧ q.cy ≤ s - wT q.t / 2

/-! ## `projI` / `insideAll` / `outsideAll` soundness -/

set_option maxHeartbeats 2000000 in
theorem projI_sound {Clo Chi Slo Shi E : Int} {b : IBox} {q : PSq}
    (hD : 0 < ctx.D) (hE : 0 < (E : ℝ))
    (hcos1 : (Clo : ℝ) ≤ cosT q.t * E) (hcos2 : cosT q.t * E ≤ (Chi : ℝ))
    (hsin1 : (Slo : ℝ) ≤ sinT q.t * E) (hsin2 : sinT q.t * E ≤ (Shi : ℝ))
    (hX0 : (b.X0 : ℝ) ≤ q.cx * ctx.D) (hX1 : q.cx * ctx.D ≤ (b.X1 : ℝ))
    (hY0 : (b.Y0 : ℝ) ≤ q.cy * ctx.D) (hY1 : q.cy * ctx.D ≤ (b.Y1 : ℝ))
    {a : IAtom} (hpd : 0 < a.pd)
    {u0 u1 v0 v1 lim : Int}
    (hp : projI ctx Clo Chi Slo Shi E b a = (u0, u1, v0, v1, lim)) :
    (insideAll u0 u1 v0 v1 lim = true → atomPt a ∈ q.set) ∧
    (outsideAll u0 u1 v0 v1 lim = true → atomPt a ∉ q.set) := by
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  have hpdR : (0 : ℝ) < (a.pd : ℝ) := by exact_mod_cast hpd
  have hL : (0 : ℝ) < (E : ℝ) * (a.pd : ℝ) * (ctx.D : ℝ) := by positivity
  simp only [projI, imul4, Prod.mk.injEq] at hp
  obtain ⟨h1, h2, h3, h4, h5⟩ := hp
  -- the real scaled offsets
  set ydx : ℝ := (a.px : ℝ) * ctx.D - q.cx * ctx.D * a.pd with hydx
  set ydy : ℝ := (a.py : ℝ) * ctx.D - q.cy * ctx.D * a.pd with hydy
  have hdx0 : ((a.px * ctx.D - b.X1 * a.pd : Int) : ℝ) ≤ ydx := by
    rw [hydx]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hX1 hpdR.le]
  have hdx1 : ydx ≤ ((a.px * ctx.D - b.X0 * a.pd : Int) : ℝ) := by
    rw [hydx]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hX0 hpdR.le]
  have hdy0 : ((a.py * ctx.D - b.Y1 * a.pd : Int) : ℝ) ≤ ydy := by
    rw [hydy]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hY1 hpdR.le]
  have hdy1 : ydy ≤ ((a.py * ctx.D - b.Y0 * a.pd : Int) : ℝ) := by
    rw [hydy]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hY0 hpdR.le]
  -- interval products
  have hpdne : (a.pd : ℝ) ≠ 0 := hpdR.ne'
  have hCneg1 : ((-Shi : Int) : ℝ) ≤ -(sinT q.t * E) := by push_cast; linarith
  have hCneg2 : -(sinT q.t * E) ≤ ((-Slo : Int) : ℝ) := by push_cast; linarith
  have hA := imul4_cast_bounds hcos1 hcos2 hdx0 hdx1
  have hB := imul4_cast_bounds hsin1 hsin2 hdy0 hdy1
  have hC := imul4_cast_bounds hCneg1 hCneg2 hdx0 hdx1
  have hD' := imul4_cast_bounds hcos1 hcos2 hdy0 hdy1
  push_cast at hA hB hC hD'
  -- the real u/v coordinates of the atom relative to the square's centre
  set uR : ℝ := rdot ((atomPt a).1 - q.cx, (atomPt a).2 - q.cy) (edir q) with huR
  set vR : ℝ := rdot ((atomPt a).1 - q.cx, (atomPt a).2 - q.cy) (perpV (edir q)) with hvR
  have huval : (cosT q.t * E) * ydx + (sinT q.t * E) * ydy
      = uR * ((E : ℝ) * (a.pd : ℝ) * (ctx.D : ℝ)) := by
    rw [huR]
    simp only [rdot, edir, atomPt, hydx, hydy]
    field_simp
  have hvval : (-(sinT q.t * E)) * ydx + (cosT q.t * E) * ydy
      = vR * ((E : ℝ) * (a.pd : ℝ) * (ctx.D : ℝ)) := by
    rw [hvR]
    simp only [rdot, edir, perpV, atomPt, hydx, hydy]
    field_simp
  -- bounds on 2·L·uR and 2·L·vR
  have hu0 : (u0 : ℝ) ≤ 2 * (uR * ((E : ℝ) * a.pd * ctx.D)) := by
    rw [← h1, ← huval]
    push_cast
    linarith [hA.1, hB.1]
  have hu1 : 2 * (uR * ((E : ℝ) * a.pd * ctx.D)) ≤ (u1 : ℝ) := by
    rw [← h2, ← huval]
    push_cast
    linarith [hA.2, hB.2]
  have hv0 : (v0 : ℝ) ≤ 2 * (vR * ((E : ℝ) * a.pd * ctx.D)) := by
    rw [← h3, ← hvval]
    push_cast
    linarith [hC.1, hD'.1]
  have hv1 : 2 * (vR * ((E : ℝ) * a.pd * ctx.D)) ≤ (v1 : ℝ) := by
    rw [← h4, ← hvval]
    push_cast
    linarith [hC.2, hD'.2]
  have hlim : (lim : ℝ) = (E : ℝ) * a.pd * ctx.D := by rw [← h5]; push_cast; ring
  constructor
  · -- insideAll ⇒ membership
    intro hin
    simp only [insideAll, Bool.and_eq_true, decide_eq_true_eq] at hin
    obtain ⟨⟨⟨hiu1, hiu0⟩, hiv1⟩, hiv0⟩ := hin
    have hiu1' : (u1 : ℝ) ≤ (lim : ℝ) := by exact_mod_cast hiu1
    have hiu0' : (-(lim : ℝ)) ≤ (u0 : ℝ) := by exact_mod_cast hiu0
    have hiv1' : (v1 : ℝ) ≤ (lim : ℝ) := by exact_mod_cast hiv1
    have hiv0' : (-(lim : ℝ)) ≤ (v0 : ℝ) := by exact_mod_cast hiv0
    rw [hlim] at hiu1' hiu0' hiv1' hiv0'
    have hu : |uR| ≤ 1 / 2 := by
      rw [abs_le]
      constructor <;> nlinarith
    have hv : |vR| ≤ 1 / 2 := by
      rw [abs_le]
      constructor <;> nlinarith
    rw [mem_set_iff_uv, ← huR, ← hvR]
    exact ⟨hu, hv⟩
  · -- outsideAll ⇒ non-membership
    intro hout hmem
    rw [mem_set_iff_uv, ← huR, ← hvR] at hmem
    obtain ⟨hu, hv⟩ := hmem
    rw [abs_le] at hu hv
    simp only [outsideAll, Bool.or_eq_true, decide_eq_true_eq] at hout
    rcases hout with ((h | h) | h) | h
    · have h' : (lim : ℝ) < (u0 : ℝ) := by exact_mod_cast h
      rw [hlim] at h'
      nlinarith [hu.2]
    · have h' : (u1 : ℝ) < (-(lim : ℝ)) := by exact_mod_cast h
      rw [hlim] at h'
      nlinarith [hu.1]
    · have h' : (lim : ℝ) < (v0 : ℝ) := by exact_mod_cast h
      rw [hlim] at h'
      nlinarith [hv.2]
    · have h' : (v1 : ℝ) < (-(lim : ℝ)) := by exact_mod_cast h
      rw [hlim] at h'
      nlinarith [hv.1]

/-! ## Clipping soundness -/

/-- Core of the clip bound, one axis: if `wLo = wn/wd ≤ w(t)` then the outward-rounded
clip interval `[⌊wn·D/(2wd)⌋, ⌈(2·SD·wd − wn·D)/(2wd)⌉]` contains `c·D` for every
admissible centre coordinate `c`. -/
theorem clip_core {sVal : ℝ} {q : PSq} (hD : 0 < ctx.D)
    (hSD : (ctx.SD : ℝ) = sVal * ctx.D) {wn wd : Int} (hwd : 0 < wd)
    (hwlo : (wn : ℝ) / (wd : ℝ) ≤ wT q.t) {cc : ℝ}
    (h1 : wT q.t / 2 ≤ cc) (h2 : cc ≤ sVal - wT q.t / 2) :
    ((wn * ctx.D / (2 * wd) : Int) : ℝ) ≤ cc * ctx.D ∧
    cc * ctx.D ≤ ((-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd)) : Int) : ℝ) := by
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  have hwdR : (0 : ℝ) < (wd : ℝ) := by exact_mod_cast hwd
  have h2wd : (0 : Int) < 2 * wd := by omega
  have h2wdR : (0 : ℝ) < ((2 * wd : Int) : ℝ) := by exact_mod_cast h2wd
  constructor
  · have hc1 := cast_ediv_le (A := wn * ctx.D) h2wd
    have e1 : ((wn * ctx.D : Int) : ℝ) / ((2 * wd : Int) : ℝ)
        = ((wn : ℝ) / (wd : ℝ)) * ((ctx.D : ℝ) / 2) := by
      push_cast
      field_simp
    have e2 : ((wn : ℝ) / (wd : ℝ)) * ((ctx.D : ℝ) / 2) ≤ wT q.t * ((ctx.D : ℝ) / 2) :=
      mul_le_mul_of_nonneg_right hwlo (by positivity)
    have e3 : wT q.t * ((ctx.D : ℝ) / 2) ≤ cc * ctx.D := by nlinarith
    calc ((wn * ctx.D / (2 * wd) : Int) : ℝ)
        ≤ ((wn * ctx.D : Int) : ℝ) / ((2 * wd : Int) : ℝ) := hc1
      _ = ((wn : ℝ) / (wd : ℝ)) * ((ctx.D : ℝ) / 2) := e1
      _ ≤ wT q.t * ((ctx.D : ℝ) / 2) := e2
      _ ≤ cc * ctx.D := e3
  · have hc1 := cast_ediv_le (A := -(2 * ctx.SD * wd - wn * ctx.D)) h2wd
    have e4 : ((2 * ctx.SD * wd - wn * ctx.D : Int) : ℝ) / ((2 * wd : Int) : ℝ)
        = sVal * ctx.D - ((wn : ℝ) / (wd : ℝ)) * ((ctx.D : ℝ) / 2) := by
      push_cast
      rw [hSD]
      field_simp
    have e5 : cc * ctx.D ≤ sVal * ctx.D - wT q.t * ((ctx.D : ℝ) / 2) := by nlinarith
    have e6 : sVal * ctx.D - wT q.t * ((ctx.D : ℝ) / 2)
        ≤ sVal * ctx.D - ((wn : ℝ) / (wd : ℝ)) * ((ctx.D : ℝ) / 2) := by
      have := mul_le_mul_of_nonneg_right hwlo (by positivity : (0:ℝ) ≤ (ctx.D : ℝ) / 2)
      linarith
    have e7 : cc * ctx.D ≤ ((2 * ctx.SD * wd - wn * ctx.D : Int) : ℝ) / ((2 * wd : Int) : ℝ) := by
      rw [e4]; linarith
    have e8 : ((-(2 * ctx.SD * wd - wn * ctx.D) : Int) : ℝ)
        = -(((2 * ctx.SD * wd - wn * ctx.D) : Int) : ℝ) := by push_cast; ring
    have e9 : ((-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd)) : Int) : ℝ)
        = -((-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd) : Int) : ℝ) := by push_cast; ring
    rw [e9]
    rw [e8] at hc1
    -- hc1 : cast(ediv) ≤ (−A)/(2wd); so −cast(ediv) ≥ A/(2wd) ≥ cc·D
    have hdiv : -(((2 * ctx.SD * wd - wn * ctx.D) : Int) : ℝ) / ((2 * wd : Int) : ℝ)
        = -((((2 * ctx.SD * wd - wn * ctx.D) : Int) : ℝ) / ((2 * wd : Int) : ℝ)) := by
      ring
    rw [hdiv] at hc1
    linarith

/-- Clip soundness: an admissible parameter point of a box survives clipping (in
particular the clip cannot be vacuous), and clipping leaves the `t`-range unchanged. -/
theorem clipI_sound {sVal : ℝ} {b : IBox} {q : PSq}
    (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (hD : 0 < ctx.D) (hSD : (ctx.SD : ℝ) = sVal * ctx.D)
    (hT0 : 0 ≤ b.T0) (hq : inBox ctx b q) (hadm : Adm sVal q) :
    ∃ b', clipI ctx b = some b' ∧ inBox ctx b' q ∧ b'.T0 = b.T0 ∧ b'.T1 = b.T1 := by
  obtain ⟨hqT0, hqT1, hqX0, hqX1, hqY0, hqY1⟩ := hq
  obtain ⟨ha1, ha2, ha3, ha4⟩ := hadm
  have hdn0 := dn_pos hP4 hR b.T0
  have hdn1 := dn_pos hP4 hR b.T1
  -- endpoints of the t-interval as reals
  have ht00 : (0 : ℝ) ≤ (b.T0 : ℝ) / (ctx.TROOT : ℝ) :=
    div_nonneg (by exact_mod_cast hT0) hR.le
  have ht01 : (b.T0 : ℝ) / (ctx.TROOT : ℝ) ≤ q.t := by rw [div_le_iff₀ hR]; exact hqT0
  have ht11 : q.t ≤ (b.T1 : ℝ) / (ctx.TROOT : ℝ) := by rw [le_div_iff₀ hR]; exact hqT1
  have hmin := wT_ge_min ht00 ht01 ht11
  -- grid values of w at the endpoints
  have hw0 : wT ((b.T0 : ℝ) / (ctx.TROOT : ℝ))
      = ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT : Int) : ℝ)
        / ((ctx.P4 + b.T0 * b.T0 : Int) : ℝ) := by
    rw [wT, cosT_grid hP4 hR, sinT_grid hP4 hR]
    push_cast
    ring
  have hw1 : wT ((b.T1 : ℝ) / (ctx.TROOT : ℝ))
      = ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT : Int) : ℝ)
        / ((ctx.P4 + b.T1 * b.T1 : Int) : ℝ) := by
    rw [wT, cosT_grid hP4 hR, sinT_grid hP4 hR]
    push_cast
    ring
  have hwd0 : (0 : Int) < ctx.P4 + b.T0 * b.T0 := by exact_mod_cast hdn0
  have hwd1 : (0 : Int) < ctx.P4 + b.T1 * b.T1 := by exact_mod_cast hdn1
  by_cases hsel : (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * (ctx.P4 + b.T1 * b.T1)
      ≤ (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * (ctx.P4 + b.T0 * b.T0)
  · -- min at the left endpoint: wLo = wn0/dn0
    have hle : wT ((b.T0 : ℝ) / (ctx.TROOT : ℝ)) ≤ wT ((b.T1 : ℝ) / (ctx.TROOT : ℝ)) := by
      rw [hw0, hw1, div_le_div_iff₀ hdn0 hdn1]
      exact_mod_cast hsel
    have hwlo : ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT : Int) : ℝ)
        / ((ctx.P4 + b.T0 * b.T0 : Int) : ℝ) ≤ wT q.t := by
      rw [← hw0]
      exact le_trans (le_of_eq (min_eq_left hle).symm) hmin
    obtain ⟨hX0c, hX1c⟩ := clip_core hD hSD hwd0 hwlo ha1 ha2
    obtain ⟨hY0c, hY1c⟩ := clip_core hD hSD hwd0 hwlo ha3 ha4
    have hXlo : ((max b.X0 ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T0 * b.T0))) : Int) : ℝ) ≤ q.cx * ctx.D := by
      push_cast [Int.cast_max]
      exact max_le hqX0 (by exact_mod_cast hX0c)
    have hXhi : q.cx * ctx.D ≤ ((min b.X1
        (-(-(2 * ctx.SD * (ctx.P4 + b.T0 * b.T0)
          - (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T0 * b.T0)))) : Int) : ℝ) := by
      push_cast [Int.cast_min]
      exact le_min hqX1 (by exact_mod_cast hX1c)
    have hYlo : ((max b.Y0 ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T0 * b.T0))) : Int) : ℝ) ≤ q.cy * ctx.D := by
      push_cast [Int.cast_max]
      exact max_le hqY0 (by exact_mod_cast hY0c)
    have hYhi : q.cy * ctx.D ≤ ((min b.Y1
        (-(-(2 * ctx.SD * (ctx.P4 + b.T0 * b.T0)
          - (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T0 * b.T0)))) : Int) : ℝ) := by
      push_cast [Int.cast_min]
      exact le_min hqY1 (by exact_mod_cast hY1c)
    have hXint : max b.X0 ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T0 * b.T0)))
        ≤ min b.X1 (-(-(2 * ctx.SD * (ctx.P4 + b.T0 * b.T0)
          - (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T0 * b.T0)))) := by
      exact_mod_cast le_trans hXlo hXhi
    have hYint : max b.Y0 ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T0 * b.T0)))
        ≤ min b.Y1 (-(-(2 * ctx.SD * (ctx.P4 + b.T0 * b.T0)
          - (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T0 * b.T0)))) := by
      exact_mod_cast le_trans hYlo hYhi
    refine ⟨⟨b.T0, b.T1,
      max b.X0 ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T0 * b.T0))),
      min b.X1 (-(-(2 * ctx.SD * (ctx.P4 + b.T0 * b.T0)
          - (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T0 * b.T0)))),
      max b.Y0 ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T0 * b.T0))),
      min b.Y1 (-(-(2 * ctx.SD * (ctx.P4 + b.T0 * b.T0)
          - (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T0 * b.T0))))⟩,
      ?_, ⟨hqT0, hqT1, hXlo, hXhi, hYlo, hYhi⟩, rfl, rfl⟩
    simp only [clipI, trig]
    split_ifs with hs1 hs2
    · rfl
    · refine absurd ?_ hs2
      simp only [Bool.and_eq_true, decide_eq_true_eq]
      exact ⟨hXint, hYint⟩
    · exact absurd hsel hs1
  · -- min at the right endpoint: wLo = wn1/dn1
    rw [not_le] at hsel
    have hle : wT ((b.T1 : ℝ) / (ctx.TROOT : ℝ)) ≤ wT ((b.T0 : ℝ) / (ctx.TROOT : ℝ)) := by
      rw [hw0, hw1, div_le_div_iff₀ hdn1 hdn0]
      exact_mod_cast hsel.le
    have hwlo : ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT : Int) : ℝ)
        / ((ctx.P4 + b.T1 * b.T1 : Int) : ℝ) ≤ wT q.t := by
      rw [← hw1]
      exact le_trans (le_of_eq (min_eq_right hle).symm) hmin
    obtain ⟨hX0c, hX1c⟩ := clip_core hD hSD hwd1 hwlo ha1 ha2
    obtain ⟨hY0c, hY1c⟩ := clip_core hD hSD hwd1 hwlo ha3 ha4
    have hXlo : ((max b.X0 ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T1 * b.T1))) : Int) : ℝ) ≤ q.cx * ctx.D := by
      push_cast [Int.cast_max]
      exact max_le hqX0 (by exact_mod_cast hX0c)
    have hXhi : q.cx * ctx.D ≤ ((min b.X1
        (-(-(2 * ctx.SD * (ctx.P4 + b.T1 * b.T1)
          - (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T1 * b.T1)))) : Int) : ℝ) := by
      push_cast [Int.cast_min]
      exact le_min hqX1 (by exact_mod_cast hX1c)
    have hYlo : ((max b.Y0 ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T1 * b.T1))) : Int) : ℝ) ≤ q.cy * ctx.D := by
      push_cast [Int.cast_max]
      exact max_le hqY0 (by exact_mod_cast hY0c)
    have hYhi : q.cy * ctx.D ≤ ((min b.Y1
        (-(-(2 * ctx.SD * (ctx.P4 + b.T1 * b.T1)
          - (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T1 * b.T1)))) : Int) : ℝ) := by
      push_cast [Int.cast_min]
      exact le_min hqY1 (by exact_mod_cast hY1c)
    have hXint : max b.X0 ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T1 * b.T1)))
        ≤ min b.X1 (-(-(2 * ctx.SD * (ctx.P4 + b.T1 * b.T1)
          - (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T1 * b.T1)))) := by
      exact_mod_cast le_trans hXlo hXhi
    have hYint : max b.Y0 ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T1 * b.T1)))
        ≤ min b.Y1 (-(-(2 * ctx.SD * (ctx.P4 + b.T1 * b.T1)
          - (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T1 * b.T1)))) := by
      exact_mod_cast le_trans hYlo hYhi
    refine ⟨⟨b.T0, b.T1,
      max b.X0 ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T1 * b.T1))),
      min b.X1 (-(-(2 * ctx.SD * (ctx.P4 + b.T1 * b.T1)
          - (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T1 * b.T1)))),
      max b.Y0 ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D
        / (2 * (ctx.P4 + b.T1 * b.T1))),
      min b.Y1 (-(-(2 * ctx.SD * (ctx.P4 + b.T1 * b.T1)
          - (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * ctx.D)
            / (2 * (ctx.P4 + b.T1 * b.T1))))⟩,
      ?_, ⟨hqT0, hqT1, hXlo, hXhi, hYlo, hYhi⟩, rfl, rfl⟩
    simp only [clipI, trig]
    split_ifs with hs1 hs2
    · exact absurd hs1 (not_le.mpr hsel)
    · rfl
    · refine absurd ?_ hs2
      simp only [Bool.and_eq_true, decide_eq_true_eq]
      exact ⟨hXint, hYint⟩

end CtxFacts

end

end S11
end PackingCert
