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
  -- one axis of the clip bound, packaged for both selection branches
  have core : ∀ wn wd : Int, 0 < wd → (wn : ℝ) / (wd : ℝ) ≤ wT q.t →
      ((max b.X0 (wn * ctx.D / (2 * wd)) : Int) : ℝ) ≤ q.cx * ctx.D ∧
      q.cx * ctx.D ≤ ((min b.X1 (-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd))) : Int) : ℝ) ∧
      ((max b.Y0 (wn * ctx.D / (2 * wd)) : Int) : ℝ) ≤ q.cy * ctx.D ∧
      q.cy * ctx.D ≤ ((min b.Y1 (-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd))) : Int) : ℝ) ∧
      max b.X0 (wn * ctx.D / (2 * wd))
        ≤ min b.X1 (-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd))) ∧
      max b.Y0 (wn * ctx.D / (2 * wd))
        ≤ min b.Y1 (-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd))) := by
    intro wn wd hwd hwlo
    obtain ⟨hX0c, hX1c⟩ := clip_core hD hSD hwd hwlo ha1 ha2
    obtain ⟨hY0c, hY1c⟩ := clip_core hD hSD hwd hwlo ha3 ha4
    have p1 : ((max b.X0 (wn * ctx.D / (2 * wd)) : Int) : ℝ) ≤ q.cx * ctx.D := by
      push_cast [Int.cast_max]
      exact max_le hqX0 (by exact_mod_cast hX0c)
    have p2 : q.cx * ctx.D
        ≤ ((min b.X1 (-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd))) : Int) : ℝ) := by
      push_cast [Int.cast_min]
      exact le_min hqX1 (by exact_mod_cast hX1c)
    have p3 : ((max b.Y0 (wn * ctx.D / (2 * wd)) : Int) : ℝ) ≤ q.cy * ctx.D := by
      push_cast [Int.cast_max]
      exact max_le hqY0 (by exact_mod_cast hY0c)
    have p4 : q.cy * ctx.D
        ≤ ((min b.Y1 (-(-(2 * ctx.SD * wd - wn * ctx.D) / (2 * wd))) : Int) : ℝ) := by
      push_cast [Int.cast_min]
      exact le_min hqY1 (by exact_mod_cast hY1c)
    exact ⟨p1, p2, p3, p4, by exact_mod_cast le_trans p1 p2,
      by exact_mod_cast le_trans p3 p4⟩
  -- evaluate `clipI` by case-splitting a hypothesis copy (the checker was compiled
  -- without Mathlib, so goal-side rewriting with Mathlib-elaborated lemmas does not
  -- match syntactically; `split at` + full-unification `exact` does)
  obtain ⟨res, hres⟩ : ∃ r, clipI ctx b = r := ⟨_, rfl⟩
  have hres0 : clipI ctx b = res := hres
  rw [clipI] at hres
  split at hres
  next cn0 sn0 dn0 heq0 =>
  split at hres
  next cn1 sn1 dn1 heq1 =>
  simp only [trig, Prod.mk.injEq] at heq0 heq1
  obtain ⟨e1, e2, e3⟩ := heq0
  obtain ⟨f1, f2, f3⟩ := heq1
  subst e1; subst e2; subst e3; subst f1; subst f2; subst f3
  dsimp only at hres
  split at hres
  · -- selection: min at the left endpoint, (wn, wd) = (wn0, dn0)
    next hsel =>
    dsimp only at hres
    have hle : wT ((b.T0 : ℝ) / (ctx.TROOT : ℝ)) ≤ wT ((b.T1 : ℝ) / (ctx.TROOT : ℝ)) := by
      rw [hw0, hw1, div_le_div_iff₀ hdn0 hdn1]
      exact_mod_cast hsel
    have hwlo : ((ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT : Int) : ℝ)
        / ((ctx.P4 + b.T0 * b.T0 : Int) : ℝ) ≤ wT q.t := by
      rw [← hw0]
      exact le_trans (le_of_eq (min_eq_left hle).symm) hmin
    obtain ⟨p1, p2, p3, p4, pX, pY⟩ :=
      core (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) (ctx.P4 + b.T0 * b.T0) hwd0 hwlo
    split at hres
    · next hcond =>
      exact ⟨_, hres0.trans hres.symm, ⟨hqT0, hqT1, p1, p2, p3, p4⟩, rfl, rfl⟩
    · next hcond =>
      refine absurd ?_ hcond
      rw [Bool.and_eq_true]
      exact ⟨decide_eq_true pX, decide_eq_true pY⟩
  · -- selection: min at the right endpoint, (wn, wd) = (wn1, dn1)
    next hsel =>
    dsimp only at hres
    rw [not_le] at hsel
    have hle : wT ((b.T1 : ℝ) / (ctx.TROOT : ℝ)) ≤ wT ((b.T0 : ℝ) / (ctx.TROOT : ℝ)) := by
      rw [hw0, hw1, div_le_div_iff₀ hdn1 hdn0]
      exact_mod_cast hsel.le
    have hwlo : ((ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT : Int) : ℝ)
        / ((ctx.P4 + b.T1 * b.T1 : Int) : ℝ) ≤ wT q.t := by
      rw [← hw1]
      exact le_trans (le_of_eq (min_eq_right hle).symm) hmin
    obtain ⟨p1, p2, p3, p4, pX, pY⟩ :=
      core (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) (ctx.P4 + b.T1 * b.T1) hwd1 hwlo
    split at hres
    · next hcond =>
      exact ⟨_, hres0.trans hres.symm, ⟨hqT0, hqT1, p1, p2, p3, p4⟩, rfl, rfl⟩
    · next hcond =>
      refine absurd ?_ hcond
      rw [Bool.and_eq_true]
      exact ⟨decide_eq_true pX, decide_eq_true pY⟩

/-! ## Split soundness -/

/-- Bisection covers the box, and preserves the `t`-range invariants. -/
theorem splitI_sound {b : IBox} {q : PSq} (hq : inBox ctx b q) (hT0 : 0 ≤ b.T0)
    (hT1 : b.T1 ≤ ctx.TROOT) :
    (inBox ctx (splitI ctx b).1 q ∧ 0 ≤ (splitI ctx b).1.T0 ∧
        (splitI ctx b).1.T1 ≤ ctx.TROOT) ∨
    (inBox ctx (splitI ctx b).2 q ∧ 0 ≤ (splitI ctx b).2.T0 ∧
        (splitI ctx b).2.T1 ≤ ctx.TROOT) := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := hq
  have hTle : b.T0 ≤ b.T1 := by exact_mod_cast le_trans h1 h2
  have hXle : b.X0 ≤ b.X1 := by exact_mod_cast le_trans h3 h4
  have hYle : b.Y0 ≤ b.Y1 := by exact_mod_cast le_trans h5 h6
  obtain ⟨res, hres⟩ : ∃ r, splitI ctx b = r := ⟨_, rfl⟩
  have hres0 : splitI ctx b = res := hres
  rw [splitI] at hres
  rw [hres0]
  split at hres
  · -- X split
    have hm1 : b.X0 ≤ (b.X0 + b.X1) / 2 := by omega
    have hm2 : (b.X0 + b.X1) / 2 ≤ b.X1 := by omega
    rw [← hres]
    dsimp only
    rcases le_total (q.cx * (ctx.D : ℝ)) (((b.X0 + b.X1) / 2 : Int) : ℝ) with hc | hc
    · exact Or.inl ⟨⟨h1, h2, h3, hc, h5, h6⟩, hT0, hT1⟩
    · exact Or.inr ⟨⟨h1, h2, hc, h4, h5, h6⟩, hT0, hT1⟩
  · split at hres
    · -- Y split
      have hm1 : b.Y0 ≤ (b.Y0 + b.Y1) / 2 := by omega
      have hm2 : (b.Y0 + b.Y1) / 2 ≤ b.Y1 := by omega
      rw [← hres]
      dsimp only
      rcases le_total (q.cy * (ctx.D : ℝ)) (((b.Y0 + b.Y1) / 2 : Int) : ℝ) with hc | hc
      · exact Or.inl ⟨⟨h1, h2, h3, h4, h5, hc⟩, hT0, hT1⟩
      · exact Or.inr ⟨⟨h1, h2, h3, h4, hc, h6⟩, hT0, hT1⟩
    · -- T split
      have hm1 : b.T0 ≤ (b.T0 + b.T1) / 2 := by omega
      have hm2 : (b.T0 + b.T1) / 2 ≤ b.T1 := by omega
      rw [← hres]
      dsimp only
      rcases le_total (q.t * (ctx.TROOT : ℝ)) (((b.T0 + b.T1) / 2 : Int) : ℝ) with hc | hc
      · exact Or.inl ⟨⟨h1, hc, h3, h4, h5, h6⟩, hT0, le_trans hm2 hT1⟩
      · exact Or.inr ⟨⟨hc, h2, h3, h4, h5, h6⟩, le_trans hT0 hm1, hT1⟩

/-! ## Sift soundness -/

/-- The atom sift is sound: the certified mass plus the mass of the kept atoms never
exceeds the incoming certified mass plus the mass of all processed atoms; a `covered`
verdict means the certified mass alone reaches `NEED`; kept atoms stay valid. -/
theorem sift_sound {Clo Chi Slo Shi E : Int} {b : IBox} {q : PSq}
    (hD : 0 < ctx.D) (hE : 0 < (E : ℝ))
    (hcos1 : (Clo : ℝ) ≤ cosT q.t * E) (hcos2 : cosT q.t * E ≤ (Chi : ℝ))
    (hsin1 : (Slo : ℝ) ≤ sinT q.t * E) (hsin2 : sinT q.t * E ≤ (Shi : ℝ))
    (hX0 : (b.X0 : ℝ) ≤ q.cx * ctx.D) (hX1 : q.cx * ctx.D ≤ (b.X1 : ℝ))
    (hY0 : (b.Y0 : ℝ) ≤ q.cy * ctx.D) (hY1 : q.cy * ctx.D ≤ (b.Y1 : ℝ)) :
    ∀ (l : List IAtom) (sure : Int) (acc : List IAtom) (cov : Bool) (sure' : Int)
      (rest : List IAtom),
      (∀ a ∈ l, 0 < a.pd ∧ 0 ≤ a.w) → (∀ a ∈ acc, 0 < a.pd ∧ 0 ≤ a.w) →
      sift ctx Clo Chi Slo Shi E b l sure acc = (cov, sure', rest) →
      ((sure' : ℝ) + massIn rest q.set
          ≤ (sure : ℝ) + massIn l q.set + massIn acc q.set) ∧
      (cov = true → ctx.NEED ≤ sure') ∧
      (∀ a ∈ rest, 0 < a.pd ∧ 0 ≤ a.w) := by
  intro l
  induction l with
  | nil =>
    intro sure acc cov sure' rest hl hacc hs
    rw [sift] at hs
    simp only [Prod.mk.injEq] at hs
    obtain ⟨hc, hsu, hre⟩ := hs
    subst hsu
    subst hre
    refine ⟨by simp, ?_, hacc⟩
    intro hcov
    rw [← hc] at hcov
    exact of_decide_eq_true hcov
  | cons a as ih =>
    intro sure acc cov sure' rest hl hacc hs
    have hva := hl a (List.mem_cons_self ..)
    have hvas : ∀ x ∈ as, 0 < x.pd ∧ 0 ≤ x.w := fun x hx => hl x (List.mem_cons_of_mem a hx)
    rw [sift] at hs
    split at hs
    · next hstop =>
      simp only [Prod.mk.injEq] at hs
      obtain ⟨hc, hsu, hre⟩ := hs
      subst hsu
      subst hre
      have hnn : 0 ≤ massIn (a :: as) q.set :=
        massIn_nonneg (fun x hx => (hl x hx).2) _
      exact ⟨by linarith, fun _ => hstop, hacc⟩
    · next hstop =>
      rcases hp : projI ctx Clo Chi Slo Shi E b a with ⟨u0, u1, v0, v1, lim⟩
      rw [hp] at hs
      dsimp only at hs
      obtain ⟨hin, hout⟩ :=
        projI_sound hD hE hcos1 hcos2 hsin1 hsin2 hX0 hX1 hY0 hY1 hva.1 hp
      split at hs
      · next hins =>
        obtain ⟨q1, q2, q3⟩ := ih (sure + a.w) acc cov sure' rest hvas hacc hs
        refine ⟨?_, q2, q3⟩
        have hmem := hin hins
        have hml : massIn (a :: as) q.set = (a.w : ℝ) + massIn as q.set := by
          rw [massIn_cons, Set.indicator_of_mem hmem]
        rw [hml]
        push_cast at q1
        linarith
      · split at hs
        · next houts =>
          obtain ⟨q1, q2, q3⟩ := ih sure acc cov sure' rest hvas hacc hs
          refine ⟨?_, q2, q3⟩
          have hnot := hout houts
          have hml : massIn (a :: as) q.set = 0 + massIn as q.set := by
            rw [massIn_cons, Set.indicator_of_notMem hnot]
          rw [hml]
          linarith
        · next houts =>
          have hacc' : ∀ x ∈ a :: acc, 0 < x.pd ∧ 0 ≤ x.w := by
            intro x hx
            rcases List.mem_cons.mp hx with rfl | hx
            · exact hva
            · exact hacc x hx
          obtain ⟨q1, q2, q3⟩ := ih sure (a :: acc) cov sure' rest hvas hacc' hs
          refine ⟨?_, q2, q3⟩
          rw [massIn_cons] at q1
          rw [massIn_cons]
          linarith

/-! ## Branch-and-bound soundness -/

/-- The recursion is sound: if `go` succeeds on a box, then for every admissible
parameter point of that box the certified mass plus the mass of the atoms inside the
denoted square reaches `NEED`. -/
theorem go_sound {sVal : ℝ}
    (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (hD : 0 < ctx.D) (hSD : (ctx.SD : ℝ) = sVal * ctx.D) :
    ∀ (fuel : Nat) (b : IBox) (l : List IAtom) (sure : Int),
      (∀ a ∈ l, 0 < a.pd ∧ 0 ≤ a.w) → 0 ≤ b.T0 → b.T1 ≤ ctx.TROOT →
      go ctx fuel b l sure = true →
      ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 → inBox ctx b q → Adm sVal q →
      (ctx.NEED : ℝ) ≤ (sure : ℝ) + massIn l q.set := by
  intro fuel
  induction fuel with
  | zero =>
    intro b l sure hl hbT0 hbT1 hgo q hq0 hq1 hbox hadm
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ := clipI_sound hP4 hR hD hSD hbT0 hbox hadm
    rw [go, hclip] at hgo
    dsimp only at hgo
    rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
    rw [hbt] at hgo
    dsimp only at hgo
    simp only [boxTrig, trig, Prod.mk.injEq] at hbt
    obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1' : (b'.T1 : ℝ) ≤ (ctx.TROOT : ℝ) := by
      rw [hT1eq]; exact_mod_cast hbT1
    obtain ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩ := hbox'
    have henc := trig_enclosure hP4 hR hT0' hT1' hbt0 hbt1
    have hEpos : 0 < (E : ℝ) := by rw [← hE]; exact_mod_cast henc.1
    have hc1 : (Clo : ℝ) ≤ cosT q.t * E := by
      rw [← hClo, ← hE]; exact_mod_cast henc.2.1
    have hc2 : cosT q.t * E ≤ (Chi : ℝ) := by
      rw [← hChi, ← hE]; exact_mod_cast henc.2.2.1
    have hs1 : (Slo : ℝ) ≤ sinT q.t * E := by
      rw [← hSlo, ← hE]; exact_mod_cast henc.2.2.2.1
    have hs2 : sinT q.t * E ≤ (Shi : ℝ) := by
      rw [← hShi, ← hE]; exact_mod_cast henc.2.2.2.2
    rcases hsift : sift ctx Clo Chi Slo Shi E b' l sure [] with ⟨cov, sure', rest⟩
    obtain ⟨p1, p2, p3⟩ := sift_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
      l sure [] cov sure' rest hl (by simp) hsift
    rw [hsift] at hgo
    dsimp only at hgo
    have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hgo
    have hrest0 : 0 ≤ massIn rest q.set := massIn_nonneg (fun x hx => (p3 x hx).2) _
    have hnil : massIn ([] : List IAtom) q.set = 0 := rfl
    linarith
  | succ f ih =>
    intro b l sure hl hbT0 hbT1 hgo q hq0 hq1 hbox hadm
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ := clipI_sound hP4 hR hD hSD hbT0 hbox hadm
    rw [go, hclip] at hgo
    dsimp only at hgo
    rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
    rw [hbt] at hgo
    dsimp only at hgo
    simp only [boxTrig, trig, Prod.mk.injEq] at hbt
    obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1i : b'.T1 ≤ ctx.TROOT := hT1eq ▸ hbT1
    have hT1' : (b'.T1 : ℝ) ≤ (ctx.TROOT : ℝ) := by exact_mod_cast hT1i
    obtain ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩ := hbox'
    have henc := trig_enclosure hP4 hR hT0' hT1' hbt0 hbt1
    have hEpos : 0 < (E : ℝ) := by rw [← hE]; exact_mod_cast henc.1
    have hc1 : (Clo : ℝ) ≤ cosT q.t * E := by
      rw [← hClo, ← hE]; exact_mod_cast henc.2.1
    have hc2 : cosT q.t * E ≤ (Chi : ℝ) := by
      rw [← hChi, ← hE]; exact_mod_cast henc.2.2.1
    have hs1 : (Slo : ℝ) ≤ sinT q.t * E := by
      rw [← hSlo, ← hE]; exact_mod_cast henc.2.2.2.1
    have hs2 : sinT q.t * E ≤ (Shi : ℝ) := by
      rw [← hShi, ← hE]; exact_mod_cast henc.2.2.2.2
    rcases hsift : sift ctx Clo Chi Slo Shi E b' l sure [] with ⟨cov, sure', rest⟩
    obtain ⟨p1, p2, p3⟩ := sift_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
      l sure [] cov sure' rest hl (by simp) hsift
    rw [hsift] at hgo
    dsimp only at hgo
    have hrest0 : 0 ≤ massIn rest q.set := massIn_nonneg (fun x hx => (p3 x hx).2) _
    have hnil : massIn ([] : List IAtom) q.set = 0 := rfl
    split at hgo
    · next hcov =>
      have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hcov
      linarith
    · next hcov =>
      rw [Bool.and_eq_true] at hgo
      obtain ⟨hg1, hg2⟩ := hgo
      have hbox'' : inBox ctx b' q := ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩
      rcases splitI_sound hbox'' hT0' hT1i with ⟨hin1, hi0, hi1⟩ | ⟨hin2, hi0, hi1⟩
      · have := ih (splitI ctx b').1 rest sure' p3 hi0 hi1 hg1 q hq0 hq1 hin1 hadm
        linarith
      · have := ih (splitI ctx b').2 rest sure' p3 hi0 hi1 hg2 q hq0 hq1 hin2 hadm
        linarith

end CtxFacts

/-! ## The top-level checker gates -/

theorem checkMeasureI_facts {c : MCertI} (h : checkMeasureI c = true) :
    0 < c.sDen ∧ 0 < c.wd ∧ (∀ a ∈ c.atoms, 0 < a.pd ∧ 0 ≤ a.w) ∧
    (c.atoms.foldl (fun acc a => acc + a.w) 0 < (c.n : Int) * c.wd) ∧
    go (mkCtx c) c.depth (rootBox (mkCtx c)) c.atoms 0 = true := by
  rw [checkMeasureI] at h
  rw [Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩ := h
  refine ⟨of_decide_eq_true h1, of_decide_eq_true h2, ?_, of_decide_eq_true h4, h5⟩
  intro a ha
  have hpa := List.all_eq_true.mp h3 a ha
  rw [Bool.and_eq_true] at hpa
  exact ⟨of_decide_eq_true hpa.1, of_decide_eq_true hpa.2⟩

/-- The coverage theorem: a passing checker certifies that EVERY parametrised unit
square inside the container carries mass ≥ `wd` (i.e. `μ(Q) ≥ 1`). -/
theorem checkMeasureI_coverage {c : MCertI} (h : checkMeasureI c = true) :
    ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 →
      q.set ⊆ container ((c.sNum : ℝ) / (c.sDen : ℝ)) →
      (c.wd : ℝ) ≤ massIn c.atoms q.set := by
  obtain ⟨hsd, hwd, hat, htot, hgo⟩ := checkMeasureI_facts h
  intro q hq0 hq1 hsub
  have hTR : (mkCtx c).TROOT = (2 : Int) ^ (c.depth + 1) := rfl
  have hR : (0 : ℝ) < ((mkCtx c).TROOT : ℝ) := by
    rw [hTR]; push_cast; positivity
  have hP4' : (mkCtx c).P4 = (mkCtx c).TROOT * (mkCtx c).TROOT := by
    show (4 : Int) ^ (c.depth + 1) = (2 : Int) ^ (c.depth + 1) * (2 : Int) ^ (c.depth + 1)
    rw [← mul_pow]
    norm_num
  have hP4 : ((mkCtx c).P4 : ℝ) = ((mkCtx c).TROOT : ℝ) ^ 2 := by
    rw [hP4']; push_cast; ring
  have hD : 0 < (mkCtx c).D := by
    show 0 < c.sDen * (2 : Int) ^ (c.depth + 2)
    positivity
  have hDR : (0 : ℝ) < ((mkCtx c).D : ℝ) := by exact_mod_cast hD
  have hsdR : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
  have hSD : ((mkCtx c).SD : ℝ) = ((c.sNum : ℝ) / (c.sDen : ℝ)) * ((mkCtx c).D : ℝ) := by
    show ((c.sNum * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
        = ((c.sNum : ℝ) / (c.sDen : ℝ)) * ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
    push_cast
    field_simp
  obtain ⟨a1, a2, a3, a4⟩ :=
    (set_subset_container_iff hq0 hq1 ((c.sNum : ℝ) / (c.sDen : ℝ))).mp hsub
  have hadm : Adm ((c.sNum : ℝ) / (c.sDen : ℝ)) q := ⟨a1, a2, a3, a4⟩
  have hw1 := wT_ge_one hq0 hq1
  have hlo : (((mkCtx c).D / 2 : Int) : ℝ) ≤ ((mkCtx c).D : ℝ) / 2 :=
    cast_ediv_le (by norm_num)
  have hroot : inBox (mkCtx c) (rootBox (mkCtx c)) q := by
    refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
    · show ((0 : Int) : ℝ) ≤ q.t * ((mkCtx c).TROOT : ℝ)
      push_cast
      exact mul_nonneg hq0 hR.le
    · show q.t * ((mkCtx c).TROOT : ℝ) ≤ (((mkCtx c).TROOT : Int) : ℝ)
      nlinarith
    · show (((mkCtx c).D / 2 : Int) : ℝ) ≤ q.cx * ((mkCtx c).D : ℝ)
      nlinarith [a1, hw1]
    · show q.cx * ((mkCtx c).D : ℝ) ≤ (((mkCtx c).SD - (mkCtx c).D / 2 : Int) : ℝ)
      push_cast
      nlinarith [a2, hw1, hSD, hlo]
    · show (((mkCtx c).D / 2 : Int) : ℝ) ≤ q.cy * ((mkCtx c).D : ℝ)
      nlinarith [a3, hw1]
    · show q.cy * ((mkCtx c).D : ℝ) ≤ (((mkCtx c).SD - (mkCtx c).D / 2 : Int) : ℝ)
      push_cast
      nlinarith [a4, hw1, hSD, hlo]
  have hmain := go_sound (ctx := mkCtx c) hP4 hR hD hSD c.depth (rootBox (mkCtx c))
    c.atoms 0 hat (le_refl _) (le_refl _) hgo q hq0 hq1 hroot hadm
  have hne : ((mkCtx c).NEED : ℝ) = (c.wd : ℝ) := rfl
  rw [hne] at hmain
  simpa using hmain

/-! ## The scaling/shrinking construction and the counting argument -/

/-- Strictly-interior `u/v` coordinates put a point in the interior of the square. -/
theorem strict_uv_mem_interior (q : PSq) (p : RP)
    (hu : |rdot (p.1 - q.cx, p.2 - q.cy) (edir q)| < 1 / 2)
    (hv : |rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q))| < 1 / 2) :
    p ∈ interior q.set := by
  refine mem_interior.mpr
    ⟨{x : RP | |rdot (x.1 - q.cx, x.2 - q.cy) (edir q)| < 1 / 2} ∩
      {x : RP | |rdot (x.1 - q.cx, x.2 - q.cy) (perpV (edir q))| < 1 / 2}, ?_, ?_, hu, hv⟩
  · intro x hx
    rw [mem_set_iff_uv]
    exact ⟨le_of_lt hx.1, le_of_lt hx.2⟩
  · have hf : Continuous fun x : RP => rdot (x.1 - q.cx, x.2 - q.cy) (edir q) := by
      simp only [rdot]
      fun_prop
    have hg : Continuous fun x : RP => rdot (x.1 - q.cx, x.2 - q.cy) (perpV (edir q)) := by
      simp only [rdot]
      fun_prop
    exact IsOpen.inter (isOpen_lt hf.abs continuous_const)
      (isOpen_lt hg.abs continuous_const)

/-- Centre dilation by `lam`, keeping the unit size and the orientation. -/
def scaleC (lam : ℝ) (q : PSq) : PSq := ⟨lam * q.cx, lam * q.cy, q.t⟩

/-- A point of the shrunk square, pulled back by `1/lam`, is strictly inside the
original square (`lam > 1`). -/
theorem scaleC_mem_interior {lam : ℝ} (hlam : 1 < lam) {q : PSq} {p : RP}
    (hp : p ∈ (scaleC lam q).set) : (p.1 / lam, p.2 / lam) ∈ interior q.set := by
  have hl0 : (0 : ℝ) < lam := lt_trans one_pos hlam
  have hlne : lam ≠ 0 := hl0.ne'
  rw [mem_set_iff_uv] at hp
  obtain ⟨hu, hv⟩ := hp
  have hfrac : (0 : ℝ) < 1 / lam := by positivity
  have hfrac2 : (1 / lam) * (1 / 2 : ℝ) < 1 / 2 := by
    have hinv : 1 / lam < 1 := by
      rw [div_lt_one hl0]
      exact hlam
    nlinarith
  apply strict_uv_mem_interior
  · have key : rdot ((p.1 / lam, p.2 / lam).1 - q.cx, (p.1 / lam, p.2 / lam).2 - q.cy)
        (edir q)
        = (1 / lam) * rdot (p.1 - (scaleC lam q).cx, p.2 - (scaleC lam q).cy)
            (edir (scaleC lam q)) := by
      simp only [rdot, scaleC, edir]
      field_simp
    rw [key, abs_mul, abs_of_pos hfrac]
    have h1 : (1 / lam) * |rdot (p.1 - (scaleC lam q).cx, p.2 - (scaleC lam q).cy)
        (edir (scaleC lam q))| ≤ (1 / lam) * (1 / 2) :=
      mul_le_mul_of_nonneg_left hu hfrac.le
    nlinarith
  · have key : rdot ((p.1 / lam, p.2 / lam).1 - q.cx, (p.1 / lam, p.2 / lam).2 - q.cy)
        (perpV (edir q))
        = (1 / lam) * rdot (p.1 - (scaleC lam q).cx, p.2 - (scaleC lam q).cy)
            (perpV (edir (scaleC lam q))) := by
      simp only [rdot, scaleC, edir, perpV]
      field_simp
    rw [key, abs_mul, abs_of_pos hfrac]
    have h1 : (1 / lam) * |rdot (p.1 - (scaleC lam q).cx, p.2 - (scaleC lam q).cy)
        (perpV (edir (scaleC lam q)))| ≤ (1 / lam) * (1 / 2) :=
      mul_le_mul_of_nonneg_left hv hfrac.le
    nlinarith

/-- The shrunk square lives in the enlarged container. -/
theorem scaleC_subset {lam s : ℝ} (hlam : 1 ≤ lam) {q : PSq} (h0 : 0 ≤ q.t)
    (h1 : q.t ≤ 1) (hsub : q.set ⊆ container s) :
    (scaleC lam q).set ⊆ container (lam * s) := by
  obtain ⟨b1, b2, b3, b4⟩ := (set_subset_container_iff h0 h1 s).mp hsub
  have hw1 := wT_ge_one h0 h1
  have hl0 : (0 : ℝ) ≤ lam := le_trans zero_le_one hlam
  have m2 := mul_le_mul_of_nonneg_left b2 hl0
  have m4 := mul_le_mul_of_nonneg_left b4 hl0
  refine (set_subset_container_iff (q := scaleC lam q) h0 h1 (lam * s)).mpr ?_
  simp only [scaleC]
  refine ⟨?_, ?_, ?_, ?_⟩ <;> nlinarith

/-- Swap a `Fin`-sum with the atom-list sum. -/
theorem massIn_sum_comm {n : ℕ} (atoms : List IAtom) (f : Fin n → Set RP) :
    ∑ i, massIn atoms (f i)
      = (atoms.map fun a =>
          ∑ i, (f i).indicator (fun _ => (a.w : ℝ)) (atomPt a)).sum := by
  induction atoms with
  | nil => simp [massIn]
  | cons a as ihl =>
    simp only [massIn_cons, List.map_cons, List.sum_cons, Finset.sum_add_distrib, ihl]

/-- An atom lands in at most one of a pairwise-disjoint family. -/
theorem indicator_sum_le {n : ℕ} {f : Fin n → Set RP}
    (hdis : ∀ i j, i ≠ j → Disjoint (f i) (f j)) {w : ℝ} (hw : 0 ≤ w) (pt : RP) :
    ∑ i, (f i).indicator (fun _ => w) pt ≤ w := by
  by_cases hex : ∃ i, pt ∈ f i
  · obtain ⟨i0, hi0⟩ := hex
    have hle : ∀ i ∈ Finset.univ, (f i).indicator (fun _ => w) pt
        ≤ if i = i0 then w else 0 := by
      intro i _
      by_cases hii : i = i0
      · subst hii
        simp [Set.indicator_of_mem hi0]
      · have hnot : pt ∉ f i := fun hmem =>
          (Set.disjoint_left.mp (hdis i i0 hii)) hmem hi0
        simp [Set.indicator_of_notMem hnot, hii]
    calc ∑ i, (f i).indicator (fun _ => w) pt
        ≤ ∑ i, if i = i0 then w else 0 := Finset.sum_le_sum hle
      _ = w := by simp
  · have hall : ∀ i, pt ∉ f i := fun i hi => hex ⟨i, hi⟩
    have hz : ∀ i ∈ Finset.univ, (f i).indicator (fun _ => w) pt = 0 := fun i _ =>
      Set.indicator_of_notMem (hall i) _
    rw [Finset.sum_congr rfl hz]
    simpa using hw

theorem foldl_add_eq (l : List IAtom) : ∀ i : Int,
    l.foldl (fun acc a => acc + a.w) i = i + (l.map (fun a => a.w)).sum := by
  induction l with
  | nil => intro i; simp
  | cons a as ihl =>
    intro i
    rw [List.foldl_cons, ihl, List.map_cons, List.sum_cons]
    ring

/-- **The counting/scaling argument** (the "two-line proof" of the verifier headers):
coverage at side `S` plus total mass `< n` excludes packings at EVERY side `< S`. -/
theorem coverage_no_packing {n : ℕ} {S NEEDR : ℝ} {atoms : List IAtom}
    (hw : ∀ a ∈ atoms, 0 ≤ a.w)
    (hcover : ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 → q.set ⊆ container S →
      NEEDR ≤ massIn atoms q.set)
    (htot : (atoms.map fun a => ((a.w : ℝ))).sum < n * NEEDR) :
    ∀ s : ℝ, Fits n s → S ≤ s := by
  intro s hFits
  by_contra hcon
  rw [not_le] at hcon
  obtain ⟨Q, hP⟩ := hFits
  obtain ⟨z, hzt, hzQ⟩ := parametrize Q hP
  rcases Nat.eq_zero_or_pos n with hn | hn
  · subst hn
    have h0 : (0 : ℝ) ≤ (atoms.map fun a => ((a.w : ℝ))).sum := by
      refine List.sum_nonneg ?_
      intro x hx
      simp only [List.mem_map] at hx
      obtain ⟨a, ha, rfl⟩ := hx
      exact_mod_cast hw a ha
    simp only [Nat.cast_zero, zero_mul] at htot
    linarith
  · have hzsub : ∀ i, (z i).set ⊆ container s := fun i => (hzQ i) ▸ hP.contained i
    have hi0 : (0 : ℕ) < n := hn
    obtain ⟨b1, b2, b3, b4⟩ :=
      (set_subset_container_iff (hzt ⟨0, hi0⟩).1 (hzt ⟨0, hi0⟩).2 s).mp (hzsub ⟨0, hi0⟩)
    have hwi0 := wT_ge_one (hzt ⟨0, hi0⟩).1 (hzt ⟨0, hi0⟩).2
    have hs1 : (1 : ℝ) ≤ s := by linarith
    have hspos : (0 : ℝ) < s := by linarith
    have hlam1 : 1 < S / s := (one_lt_div hspos).mpr hcon
    have hlamS : (S / s) * s = S := div_mul_cancel₀ S hspos.ne'
    have hcov : ∀ i, NEEDR ≤ massIn atoms ((scaleC (S / s) (z i)).set) := by
      intro i
      refine hcover (scaleC (S / s) (z i)) (hzt i).1 (hzt i).2 ?_
      have hsc := scaleC_subset (le_of_lt hlam1) (hzt i).1 (hzt i).2 (hzsub i)
      rwa [hlamS] at hsc
    have hdis : ∀ i j, i ≠ j →
        Disjoint ((scaleC (S / s) (z i)).set) ((scaleC (S / s) (z j)).set) := by
      intro i j hij
      rw [Set.disjoint_left]
      intro p hpi hpj
      have h1 := scaleC_mem_interior hlam1 hpi
      have h2 := scaleC_mem_interior hlam1 hpj
      have hd := hP.interiorDisjoint i j hij
      rw [hzQ i, hzQ j] at hd
      exact Set.disjoint_left.mp hd h1 h2
    have e1 : (n : ℝ) * NEEDR = ∑ _i : Fin n, NEEDR := by
      rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
    have e2 : ∑ _i : Fin n, NEEDR ≤ ∑ i, massIn atoms ((scaleC (S / s) (z i)).set) :=
      Finset.sum_le_sum (fun i _ => hcov i)
    have e3 := massIn_sum_comm atoms (fun i => (scaleC (S / s) (z i)).set)
    have e4 : (atoms.map fun a => ∑ i, ((scaleC (S / s) (z i)).set).indicator
        (fun _ => (a.w : ℝ)) (atomPt a)).sum ≤ (atoms.map fun a => ((a.w : ℝ))).sum := by
      refine List.sum_le_sum ?_
      intro a ha
      exact indicator_sum_le hdis (by exact_mod_cast hw a ha) (atomPt a)
    have : (n : ℝ) * NEEDR ≤ (atoms.map fun a => ((a.w : ℝ))).sum := by
      rw [e1]
      calc ∑ _i : Fin n, NEEDR ≤ ∑ i, massIn atoms ((scaleC (S / s) (z i)).set) := e2
        _ = _ := e3
        _ ≤ _ := e4
    linarith

/-- **The measure bridge, end form** (A.F2): a passing `checkMeasureI` certificate at
side `s = sNum/sDen` proves `s(n) ≥ s`. -/
theorem checkMeasureI_no_packing {c : MCertI} (h : checkMeasureI c = true) :
    ∀ s : ℝ, Fits c.n s → (c.sNum : ℝ) / (c.sDen : ℝ) ≤ s := by
  obtain ⟨hsd, hwd, hat, htot, hgo⟩ := checkMeasureI_facts h
  refine coverage_no_packing (NEEDR := (c.wd : ℝ)) (fun a ha => (hat a ha).2)
    (fun q h0 h1 hsub => checkMeasureI_coverage h q h0 h1 hsub) ?_
  rw [foldl_add_eq c.atoms 0, zero_add] at htot
  have h2 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ) < (c.n : ℝ) * (c.wd : ℝ) := by
    exact_mod_cast htot
  have h3 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ)
      = (c.atoms.map fun a => ((a.w : ℝ))).sum := by
    push_cast
    rw [List.map_map]
    rfl
  rw [h3] at h2
  exact h2

end

end S11
end PackingCert
