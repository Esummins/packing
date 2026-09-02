import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.Deriv.Add
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Deriv
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Tactic
import PackingCertMathlib.RigidIV

/-!
# Semantics and soundness of the expression language (A79)

* `eval` — the real value of an `Expr` at a configuration vector `z : Fin 34 → ℝ`;
* `evalIV_sound` — interval evaluation encloses the value on the box;
* `jet_sound` — the order-2 jet encloses the value, the first partials `eval z (e.D j)`
  and the second partials `eval z ((e.D j).D i)` along the local variable list;
* `gradDense_sound` / `hessDense_sound` — the dense scatterings (zero off the declared
  variable list, via `usesOnly`);
* `hasDerivAt_eval` — along a straight segment `t ↦ p + t·v`, `eval e` is differentiable
  with derivative `∑_j eval (e.D j) · v_j` (so the SYMBOLIC derivative is the analytic
  one, which is all the mean-value arguments need);
* `mvt_box` — the mean-value theorem on a box: `eval q e − eval p e = ∑_j ∂_j e(ξ)(q_j − p_j)`
  for some `ξ` in the box.
-/

namespace PackingCert.Rigid

open Finset

/-! ## Values -/

abbrev Vec := Fin NV → ℝ

/-- Coordinate `k` of a configuration (`0` beyond the 34 coordinates). -/
def getV (z : Vec) (k : ℕ) : ℝ := if h : k < NV then z ⟨k, h⟩ else 0

noncomputable def eval (z : Vec) : Expr → ℝ
  | .var k => getV z k
  | .const q => (q : ℝ)
  | .add a b => eval z a + eval z b
  | .sub a b => eval z a - eval z b
  | .mul a b => eval z a * eval z b
  | .neg a => -eval z a
  | .cosv k => Real.cos (getV z k)
  | .sinv k => Real.sin (getV z k)

/-- `z` lies in the box `b` (34 intervals). -/
def MemBox (b : Array IV) (z : Vec) : Prop :=
  b.size = NV ∧ ∀ k : Fin NV, Mem (z k) (b.getD k IV.zero)

/-! ## Array plumbing -/

theorem getD_of_lt {α : Type} (a : Array α) {i : ℕ} (h : i < a.size) (d : α) :
    a.getD i d = a[i] := by
  simp [Array.getD, h]

theorem getD_of_ge {α : Type} (a : Array α) {i : ℕ} (h : ¬ i < a.size) (d : α) :
    a.getD i d = d := by
  simp [Array.getD, h]

theorem mkV_getD {d : ℕ} (f : ℕ → IV) {a : ℕ} (ha : a < d) : (mkV d f).getD a IV.zero = f a := by
  unfold mkV
  rw [getD_of_lt _ (by simpa using ha)]
  simp

theorem mkM_getD_row {d : ℕ} (f : ℕ → ℕ → IV) {a : ℕ} (ha : a < d) :
    (mkM d f).getD a #[] = mkV d (f a) := by
  unfold mkM
  rw [getD_of_lt _ (by simpa using ha)]
  simp

theorem mkM_getD {d : ℕ} (f : ℕ → ℕ → IV) {a c : ℕ} (ha : a < d) (hc : c < d) :
    ((mkM d f).getD a #[]).getD c IV.zero = f a c := by
  rw [mkM_getD_row f ha]
  exact mkV_getD _ hc

theorem cos_ofArray (b : Array IV) (k : ℕ) :
    (Box.ofArray b).cos k = if h : k < b.size then cosIV b[k] else ⟨-1, 1⟩ := by
  unfold Box.ofArray Box.cos
  split_ifs with h
  · rw [getD_of_lt _ (by simpa using h)]
    simp
  · rw [getD_of_ge _ (by simpa using h)]

theorem sin_ofArray (b : Array IV) (k : ℕ) :
    (Box.ofArray b).sin k = if h : k < b.size then sinIV b[k] else ⟨-1, 1⟩ := by
  unfold Box.ofArray Box.sin
  split_ifs with h
  · rw [getD_of_lt _ (by simpa using h)]
    simp
  · rw [getD_of_ge _ (by simpa using h)]

theorem mem_get {b : Array IV} {z : Vec} (hb : MemBox b z) (k : ℕ) :
    Mem (getV z k) ((Box.ofArray b).get k) := by
  unfold getV
  change Mem _ (b.getD k IV.zero)
  split_ifs with h
  · exact hb.2 ⟨k, h⟩
  · rw [getD_of_ge _ (by rw [hb.1]; exact h)]
    exact mem_zero

theorem mem_cos {b : Array IV} {z : Vec} (hb : MemBox b z) (k : ℕ) :
    Mem (Real.cos (getV z k)) ((Box.ofArray b).cos k) := by
  rw [cos_ofArray]
  unfold getV
  by_cases hk : k < NV
  · have hk' : k < b.size := by rw [hb.1]; exact hk
    rw [dif_pos hk, dif_pos hk']
    have := hb.2 ⟨k, hk⟩
    rw [getD_of_lt _ hk'] at this
    exact cosIV_sound this
  · have hk' : ¬ k < b.size := by rw [hb.1]; exact hk
    rw [dif_neg hk, dif_neg hk']
    exact ⟨by simp, by simp⟩

theorem mem_sin {b : Array IV} {z : Vec} (hb : MemBox b z) (k : ℕ) :
    Mem (Real.sin (getV z k)) ((Box.ofArray b).sin k) := by
  rw [sin_ofArray]
  unfold getV
  by_cases hk : k < NV
  · have hk' : k < b.size := by rw [hb.1]; exact hk
    rw [dif_pos hk, dif_pos hk']
    have := hb.2 ⟨k, hk⟩
    rw [getD_of_lt _ hk'] at this
    exact sinIV_sound this
  · have hk' : ¬ k < b.size := by rw [hb.1]; exact hk
    rw [dif_neg hk, dif_neg hk']
    exact ⟨by simp, by simp⟩

/-! ## Interval evaluation -/

theorem evalIV_sound {b : Array IV} {z : Vec} (hb : MemBox b z) :
    ∀ e : Expr, Mem (eval z e) (evalIV (Box.ofArray b) e)
  | .var k => mem_get hb k
  | .const q => mem_pt q
  | .add a c => mem_add (evalIV_sound hb a) (evalIV_sound hb c)
  | .sub a c => mem_sub (evalIV_sound hb a) (evalIV_sound hb c)
  | .mul a c => mem_mul (evalIV_sound hb a) (evalIV_sound hb c)
  | .neg a => mem_neg (evalIV_sound hb a)
  | .cosv k => mem_cos hb k
  | .sinv k => mem_sin hb k

/-! ## Symbolic derivatives: algebraic facts -/

theorem eval_D_var (z : Vec) (j k : ℕ) :
    eval z ((Expr.var k).D j) = if j = k then 1 else 0 := by
  unfold Expr.D
  split_ifs <;> simp [eval]

theorem eval_D_const (z : Vec) (j : ℕ) (q : ℚ) : eval z ((Expr.const q).D j) = 0 := by
  simp [Expr.D, eval]

theorem eval_D_add (z : Vec) (j : ℕ) (a b : Expr) :
    eval z ((Expr.add a b).D j) = eval z (a.D j) + eval z (b.D j) := by
  simp [Expr.D, eval]

theorem eval_D_sub (z : Vec) (j : ℕ) (a b : Expr) :
    eval z ((Expr.sub a b).D j) = eval z (a.D j) - eval z (b.D j) := by
  simp [Expr.D, eval]

theorem eval_D_mul (z : Vec) (j : ℕ) (a b : Expr) :
    eval z ((Expr.mul a b).D j) = eval z (a.D j) * eval z b + eval z a * eval z (b.D j) := by
  simp [Expr.D, eval]

theorem eval_D_neg (z : Vec) (j : ℕ) (a : Expr) : eval z ((Expr.neg a).D j) = -eval z (a.D j) := by
  simp [Expr.D, eval]

theorem eval_D_cosv (z : Vec) (j k : ℕ) :
    eval z ((Expr.cosv k).D j) = if j = k then -Real.sin (getV z k) else 0 := by
  unfold Expr.D
  split_ifs <;> simp [eval]

theorem eval_D_sinv (z : Vec) (j k : ℕ) :
    eval z ((Expr.sinv k).D j) = if j = k then Real.cos (getV z k) else 0 := by
  unfold Expr.D
  split_ifs <;> simp [eval]

theorem eval_DD_mul (z : Vec) (i j : ℕ) (a b : Expr) :
    eval z (((Expr.mul a b).D j).D i)
      = eval z ((a.D j).D i) * eval z b + eval z (a.D i) * eval z (b.D j)
        + eval z (a.D j) * eval z (b.D i) + eval z a * eval z ((b.D j).D i) := by
  simp only [Expr.D, eval]
  ring

theorem eval_DD_cosv (z : Vec) (i j k : ℕ) :
    eval z (((Expr.cosv k).D j).D i)
      = if i = k ∧ j = k then -Real.cos (getV z k) else 0 := by
  by_cases hj : j = k
  · have h1 : (Expr.cosv k).D j = Expr.neg (Expr.sinv k) := by simp [Expr.D, hj]
    rw [h1, eval_D_neg, eval_D_sinv]
    by_cases hi : i = k
    · simp [hi, hj]
    · simp [hi]
  · have h1 : (Expr.cosv k).D j = Expr.const 0 := by simp [Expr.D, hj]
    rw [h1, eval_D_const]
    simp [hj]

theorem eval_DD_sinv (z : Vec) (i j k : ℕ) :
    eval z (((Expr.sinv k).D j).D i)
      = if i = k ∧ j = k then -Real.sin (getV z k) else 0 := by
  by_cases hj : j = k
  · have h1 : (Expr.sinv k).D j = Expr.cosv k := by simp [Expr.D, hj]
    rw [h1, eval_D_cosv]
    by_cases hi : i = k
    · simp [hi, hj]
    · simp [hi]
  · have h1 : (Expr.sinv k).D j = Expr.const 0 := by simp [Expr.D, hj]
    rw [h1, eval_D_const]
    simp [hj]

theorem D_const (j : ℕ) (q : ℚ) : (Expr.const q).D j = Expr.const 0 := rfl

theorem D_D_var (i j k : ℕ) : ((Expr.var k).D j).D i = Expr.const 0 := by
  by_cases h : j = k <;> simp [Expr.D, h]

/-! ## Jets -/

/-- The jet `J` is sound for `e` at `z` along the local variable list `vs`. -/
def JetSound (z : Vec) (vs : Array ℕ) (e : Expr) (J : Jet) : Prop :=
  Mem (eval z e) J.v ∧
  (∀ a, a < vs.size → Mem (eval z (e.D (vs.getD a 0))) (J.gg a)) ∧
  (∀ a c, a < vs.size → c < vs.size →
    Mem (eval z ((e.D (vs.getD c 0)).D (vs.getD a 0))) (J.hh a c))

theorem jet_gg_mkV (v : IV) (vs : Array ℕ) (f : ℕ → IV) (h : Array (Array IV)) {a : ℕ}
    (ha : a < vs.size) : (Jet.mk v (mkV vs.size f) h).gg a = f a := by
  unfold Jet.gg
  exact mkV_getD f ha

theorem jet_hh_mkM (v : IV) (vs : Array ℕ) (g : Array IV) (f : ℕ → ℕ → IV) {a c : ℕ}
    (ha : a < vs.size) (hc : c < vs.size) : (Jet.mk v g (mkM vs.size f)).hh a c = f a c := by
  unfold Jet.hh
  exact mkM_getD f ha hc

theorem jet_sound {b : Array IV} {z : Vec} (hb : MemBox b z) (vs : Array ℕ) :
    ∀ e : Expr, JetSound z vs e (jet (Box.ofArray b) vs e)
  | .var k => by
    simp only [JetSound, jet]
    refine ⟨mem_get hb k, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_var]
      by_cases h : vs.getD a 0 = k
      · rw [if_pos h, if_pos h]; exact mem_one
      · rw [if_neg h, if_neg h]; exact mem_zero
    · rw [jet_hh_mkM _ _ _ _ ha hc, D_D_var]
      simpa [eval] using mem_zero
  | .const q => by
    simp only [JetSound, jet]
    refine ⟨mem_pt q, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_const]; exact mem_zero
    · rw [jet_hh_mkM _ _ _ _ ha hc, D_const, D_const]; simpa [eval] using mem_zero
  | .add x y => by
    obtain ⟨hx0, hx1, hx2⟩ := jet_sound hb vs x
    obtain ⟨hy0, hy1, hy2⟩ := jet_sound hb vs y
    simp only [JetSound, jet]
    refine ⟨mem_add hx0 hy0, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_add]
      exact mem_add (hx1 a ha) (hy1 a ha)
    · rw [jet_hh_mkM _ _ _ _ ha hc]
      have : eval z (((Expr.add x y).D (vs.getD c 0)).D (vs.getD a 0))
          = eval z ((x.D (vs.getD c 0)).D (vs.getD a 0)) + eval z ((y.D (vs.getD c 0)).D (vs.getD a 0)) := by
        simp [Expr.D, eval]
      rw [this]
      exact mem_add (hx2 a c ha hc) (hy2 a c ha hc)
  | .sub x y => by
    obtain ⟨hx0, hx1, hx2⟩ := jet_sound hb vs x
    obtain ⟨hy0, hy1, hy2⟩ := jet_sound hb vs y
    simp only [JetSound, jet]
    refine ⟨mem_sub hx0 hy0, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_sub]
      exact mem_sub (hx1 a ha) (hy1 a ha)
    · rw [jet_hh_mkM _ _ _ _ ha hc]
      have : eval z (((Expr.sub x y).D (vs.getD c 0)).D (vs.getD a 0))
          = eval z ((x.D (vs.getD c 0)).D (vs.getD a 0)) - eval z ((y.D (vs.getD c 0)).D (vs.getD a 0)) := by
        simp [Expr.D, eval]
      rw [this]
      exact mem_sub (hx2 a c ha hc) (hy2 a c ha hc)
  | .mul x y => by
    obtain ⟨hx0, hx1, hx2⟩ := jet_sound hb vs x
    obtain ⟨hy0, hy1, hy2⟩ := jet_sound hb vs y
    simp only [JetSound, jet]
    refine ⟨mem_mul hx0 hy0, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_mul]
      exact mem_add (mem_mul (hx1 a ha) hy0) (mem_mul hx0 (hy1 a ha))
    · rw [jet_hh_mkM _ _ _ _ ha hc, eval_DD_mul]
      exact mem_add (mem_add (mem_add (mem_mul (hx2 a c ha hc) hy0)
        (mem_mul (hx1 a ha) (hy1 c hc))) (mem_mul (hx1 c hc) (hy1 a ha)))
        (mem_mul hx0 (hy2 a c ha hc))
  | .neg x => by
    obtain ⟨hx0, hx1, hx2⟩ := jet_sound hb vs x
    simp only [JetSound, jet]
    refine ⟨mem_neg hx0, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_neg]
      exact mem_neg (hx1 a ha)
    · rw [jet_hh_mkM _ _ _ _ ha hc]
      have : eval z (((Expr.neg x).D (vs.getD c 0)).D (vs.getD a 0))
          = -eval z ((x.D (vs.getD c 0)).D (vs.getD a 0)) := by
        simp [Expr.D, eval]
      rw [this]
      exact mem_neg (hx2 a c ha hc)
  | .cosv k => by
    simp only [JetSound, jet]
    refine ⟨mem_cos hb k, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_cosv]
      by_cases h : vs.getD a 0 = k
      · rw [if_pos h, if_pos h]; exact mem_neg (mem_sin hb k)
      · rw [if_neg h, if_neg h]; exact mem_zero
    · rw [jet_hh_mkM _ _ _ _ ha hc, eval_DD_cosv]
      by_cases h : vs.getD a 0 = k ∧ vs.getD c 0 = k
      · rw [if_pos h]
        have hb' : (vs.getD a 0 = k && vs.getD c 0 = k) = true := by
          simp [h.1, h.2]
        rw [if_pos hb']
        exact mem_neg (mem_cos hb k)
      · rw [if_neg h]
        have hb' : ¬ (vs.getD a 0 = k && vs.getD c 0 = k) = true := by
          simpa [Bool.and_eq_true, decide_eq_true_eq] using h
        rw [if_neg hb']
        exact mem_zero
  | .sinv k => by
    simp only [JetSound, jet]
    refine ⟨mem_sin hb k, fun a ha => ?_, fun a c ha hc => ?_⟩
    · rw [jet_gg_mkV _ _ _ _ ha, eval_D_sinv]
      by_cases h : vs.getD a 0 = k
      · rw [if_pos h, if_pos h]; exact mem_cos hb k
      · rw [if_neg h, if_neg h]; exact mem_zero
    · rw [jet_hh_mkM _ _ _ _ ha hc, eval_DD_sinv]
      by_cases h : vs.getD a 0 = k ∧ vs.getD c 0 = k
      · rw [if_pos h]
        have hb' : (vs.getD a 0 = k && vs.getD c 0 = k) = true := by
          simp [h.1, h.2]
        rw [if_pos hb']
        exact mem_neg (mem_sin hb k)
      · rw [if_neg h]
        have hb' : ¬ (vs.getD a 0 = k && vs.getD c 0 = k) = true := by
          simpa [Bool.and_eq_true, decide_eq_true_eq] using h
        rw [if_neg hb']
        exact mem_zero

/-! ## Variables outside the declared list -/

theorem inVs_iff (vs : Array ℕ) (k : ℕ) : inVs vs k = true ↔ ∃ a, a < vs.size ∧ vs.getD a 0 = k := by
  unfold inVs
  simp [List.any_eq_true, List.mem_range]

theorem usesOnly_D {vs : Array ℕ} : ∀ {e : Expr}, e.usesOnly vs = true → ∀ j, (e.D j).usesOnly vs = true
  | .var _, _, j => by unfold Expr.D; split_ifs <;> rfl
  | .const _, _, _ => rfl
  | .add a b, h, j => by
    simp only [Expr.usesOnly, Bool.and_eq_true] at h
    simp only [Expr.D, Expr.usesOnly, Bool.and_eq_true]
    exact ⟨usesOnly_D h.1 j, usesOnly_D h.2 j⟩
  | .sub a b, h, j => by
    simp only [Expr.usesOnly, Bool.and_eq_true] at h
    simp only [Expr.D, Expr.usesOnly, Bool.and_eq_true]
    exact ⟨usesOnly_D h.1 j, usesOnly_D h.2 j⟩
  | .mul a b, h, j => by
    simp only [Expr.usesOnly, Bool.and_eq_true] at h
    simp only [Expr.D, Expr.usesOnly, Bool.and_eq_true]
    exact ⟨⟨usesOnly_D h.1 j, h.2⟩, h.1, usesOnly_D h.2 j⟩
  | .neg a, h, j => by
    simp only [Expr.usesOnly] at h
    simp only [Expr.D, Expr.usesOnly]
    exact usesOnly_D h j
  | .cosv k, h, j => by
    simp only [Expr.usesOnly] at h
    unfold Expr.D
    split_ifs <;> simp [Expr.usesOnly, h]
  | .sinv k, h, j => by
    simp only [Expr.usesOnly] at h
    unfold Expr.D
    split_ifs <;> simp [Expr.usesOnly, h]

/-- Syntactically zero expressions (closed under `D`). -/
def isZeroE : Expr → Bool
  | .const q => decide (q = 0)
  | .add a b => isZeroE a && isZeroE b
  | .sub a b => isZeroE a && isZeroE b
  | .mul a b => isZeroE a || isZeroE b
  | .neg a => isZeroE a
  | _ => false

theorem eval_of_isZero (z : Vec) : ∀ {e : Expr}, isZeroE e = true → eval z e = 0
  | .const q, h => by
    simp only [isZeroE, decide_eq_true_eq] at h
    simp [eval, h]
  | .add a b, h => by
    simp only [isZeroE, Bool.and_eq_true] at h
    simp [eval, eval_of_isZero z h.1, eval_of_isZero z h.2]
  | .sub a b, h => by
    simp only [isZeroE, Bool.and_eq_true] at h
    simp [eval, eval_of_isZero z h.1, eval_of_isZero z h.2]
  | .mul a b, h => by
    simp only [isZeroE, Bool.or_eq_true] at h
    rcases h with h | h
    · simp [eval, eval_of_isZero z h]
    · simp [eval, eval_of_isZero z h]
  | .neg a, h => by
    simp only [isZeroE] at h
    simp [eval, eval_of_isZero z h]

theorem isZero_D (j : ℕ) : ∀ {e : Expr}, isZeroE e = true → isZeroE (e.D j) = true
  | .const _, _ => rfl
  | .add a b, h => by
    simp only [isZeroE, Bool.and_eq_true] at h
    simp only [Expr.D, isZeroE, Bool.and_eq_true]
    exact ⟨isZero_D j h.1, isZero_D j h.2⟩
  | .sub a b, h => by
    simp only [isZeroE, Bool.and_eq_true] at h
    simp only [Expr.D, isZeroE, Bool.and_eq_true]
    exact ⟨isZero_D j h.1, isZero_D j h.2⟩
  | .mul a b, h => by
    simp only [isZeroE, Bool.or_eq_true] at h
    simp only [Expr.D, isZeroE, Bool.and_eq_true, Bool.or_eq_true]
    rcases h with h | h
    · exact ⟨Or.inl (isZero_D j h), Or.inl h⟩
    · exact ⟨Or.inr h, Or.inr (isZero_D j h)⟩
  | .neg a, h => by
    simp only [isZeroE] at h
    simp only [Expr.D, isZeroE]
    exact isZero_D j h

theorem isZero_D_of_not_inVs {vs : Array ℕ} {k : ℕ} (hk : ¬ inVs vs k = true) :
    ∀ {e : Expr}, e.usesOnly vs = true → isZeroE (e.D k) = true
  | .var m, h => by
    simp only [Expr.usesOnly] at h
    unfold Expr.D
    split_ifs with hkm
    · exact absurd (hkm ▸ h) hk
    · rfl
  | .const _, _ => rfl
  | .add a b, h => by
    simp only [Expr.usesOnly, Bool.and_eq_true] at h
    simp only [Expr.D, isZeroE, Bool.and_eq_true]
    exact ⟨isZero_D_of_not_inVs hk h.1, isZero_D_of_not_inVs hk h.2⟩
  | .sub a b, h => by
    simp only [Expr.usesOnly, Bool.and_eq_true] at h
    simp only [Expr.D, isZeroE, Bool.and_eq_true]
    exact ⟨isZero_D_of_not_inVs hk h.1, isZero_D_of_not_inVs hk h.2⟩
  | .mul a b, h => by
    simp only [Expr.usesOnly, Bool.and_eq_true] at h
    simp only [Expr.D, isZeroE, Bool.and_eq_true, Bool.or_eq_true]
    exact ⟨Or.inl (isZero_D_of_not_inVs hk h.1), Or.inr (isZero_D_of_not_inVs hk h.2)⟩
  | .neg a, h => by
    simp only [Expr.usesOnly] at h
    simp only [Expr.D, isZeroE]
    exact isZero_D_of_not_inVs hk h
  | .cosv m, h => by
    simp only [Expr.usesOnly] at h
    unfold Expr.D
    split_ifs with hkm
    · exact absurd (hkm ▸ h) hk
    · rfl
  | .sinv m, h => by
    simp only [Expr.usesOnly] at h
    unfold Expr.D
    split_ifs with hkm
    · exact absurd (hkm ▸ h) hk
    · rfl

theorem eval_D_of_not_inVs {vs : Array ℕ} {k : ℕ} (hk : ¬ inVs vs k = true) (z : Vec)
    {e : Expr} (h : e.usesOnly vs = true) : eval z (e.D k) = 0 :=
  eval_of_isZero z (isZero_D_of_not_inVs hk h)

theorem eval_DD_of_not_inVs {vs : Array ℕ} {k : ℕ} (hk : ¬ inVs vs k = true) (z : Vec)
    {e : Expr} (h : e.usesOnly vs = true) (i : ℕ) : eval z ((e.D k).D i) = 0 :=
  eval_of_isZero z (isZero_D i (isZero_D_of_not_inVs hk h))

theorem findPos_some {vs : Array ℕ} {j a : ℕ} (h : findPos vs j = some a) :
    a < vs.size ∧ vs.getD a 0 = j := by
  unfold findPos at h
  have h1 := List.mem_of_find?_eq_some h
  have h2 := List.find?_some h
  rw [List.mem_range] at h1
  exact ⟨h1, by simpa using h2⟩

theorem findPos_none {vs : Array ℕ} {j : ℕ} (h : findPos vs j = none) : ¬ inVs vs j = true := by
  unfold findPos at h
  rw [List.find?_eq_none] at h
  rw [inVs_iff]
  rintro ⟨a, ha, hj⟩
  exact h a (List.mem_range.mpr ha) (by simpa using hj)

/-! ## Dense gradient and Hessian of a row -/

theorem gradDense_sound {b : Array IV} {z : Vec} (hb : MemBox b z) (r : Row)
    (hu : (rowExpr r).usesOnly (rowVars r) = true) (j : Fin NV) :
    Mem (eval z ((rowExpr r).D j)) ((gradDense (Box.ofArray b) r).getD j IV.zero) := by
  unfold gradDense
  rw [mkV_getD _ j.isLt]
  obtain ⟨-, hg, -⟩ := jet_sound hb (rowVars r) (rowExpr r)
  rcases hpos : findPos (rowVars r) j with _ | a
  · rw [eval_D_of_not_inVs (findPos_none hpos) z hu]
    exact mem_zero
  · obtain ⟨ha, hj⟩ := findPos_some hpos
    have := hg a ha
    rw [hj] at this
    exact this

theorem hessDense_sound {b : Array IV} {z : Vec} (hb : MemBox b z) (r : Row)
    (hu : (rowExpr r).usesOnly (rowVars r) = true) (i j : Fin NV) :
    Mem (eval z (((rowExpr r).D j).D i))
      (((hessDense (Box.ofArray b) r).getD i #[]).getD j IV.zero) := by
  unfold hessDense
  rw [mkM_getD _ i.isLt j.isLt]
  obtain ⟨-, -, hh⟩ := jet_sound hb (rowVars r) (rowExpr r)
  rcases hpi : findPos (rowVars r) i with _ | a
  · rw [eval_D_of_not_inVs (findPos_none hpi) z (usesOnly_D hu j)]
    exact mem_zero
  · rcases hpj : findPos (rowVars r) j with _ | c
    · rw [eval_DD_of_not_inVs (findPos_none hpj) z hu]
      exact mem_zero
    · obtain ⟨ha, hi⟩ := findPos_some hpi
      obtain ⟨hc, hj⟩ := findPos_some hpj
      have := hh a c ha hc
      rw [hi, hj] at this
      exact this

/-! ## Derivatives along segments -/

/-- The straight segment `t ↦ p + t·v`. -/
def seg (p v : Vec) (t : ℝ) : Vec := fun i => p i + t * v i

theorem hasDerivAt_getV (p v : Vec) (t : ℝ) (k : ℕ) :
    HasDerivAt (fun t => getV (seg p v t) k) (getV v k) t := by
  unfold getV seg
  split_ifs with h
  · simpa using ((hasDerivAt_id t).mul_const (v ⟨k, h⟩)).const_add (p ⟨k, h⟩)
  · exact hasDerivAt_const t 0

theorem sum_D_var (z : Vec) (v : Vec) (k : ℕ) :
    ∑ j : Fin NV, eval z ((Expr.var k).D j) * v j = getV v k := by
  simp only [eval_D_var]
  unfold getV
  split_ifs with h
  · rw [Finset.sum_eq_single ⟨k, h⟩]
    · simp
    · intro j _ hj
      have : ¬ (j : ℕ) = k := fun hc => hj (Fin.ext hc)
      simp [this]
    · intro hc; exact absurd (Finset.mem_univ _) hc
  · refine Finset.sum_eq_zero fun j _ => ?_
    have : ¬ (j : ℕ) = k := fun hc => h (hc ▸ j.isLt)
    simp [this]

theorem hasDerivAt_eval (p v : Vec) (t : ℝ) : ∀ e : Expr,
    HasDerivAt (fun t => eval (seg p v t) e) (∑ j : Fin NV, eval (seg p v t) (e.D j) * v j) t
  | .var k => by
    rw [sum_D_var]
    exact hasDerivAt_getV p v t k
  | .const q => by
    simp only [eval_D_const, zero_mul, Finset.sum_const_zero]
    exact hasDerivAt_const t _
  | .add a b => by
    have h := (hasDerivAt_eval p v t a).add (hasDerivAt_eval p v t b)
    simp only [eval_D_add, add_mul, Finset.sum_add_distrib]
    exact h
  | .sub a b => by
    have h := (hasDerivAt_eval p v t a).sub (hasDerivAt_eval p v t b)
    simp only [eval_D_sub, sub_mul, Finset.sum_sub_distrib]
    exact h
  | .mul a b => by
    have h := (hasDerivAt_eval p v t a).mul (hasDerivAt_eval p v t b)
    have heq : (∑ j : Fin NV, eval (seg p v t) ((Expr.mul a b).D j) * v j)
        = (∑ j : Fin NV, eval (seg p v t) (a.D j) * v j) * eval (seg p v t) b
          + eval (seg p v t) a * (∑ j : Fin NV, eval (seg p v t) (b.D j) * v j) := by
      simp only [eval_D_mul, add_mul, Finset.sum_add_distrib, Finset.sum_mul, Finset.mul_sum]
      congr 1 <;> exact Finset.sum_congr rfl (fun j _ => by ring)
    rw [heq]
    exact h
  | .neg a => by
    have h := (hasDerivAt_eval p v t a).neg
    simp only [eval_D_neg, neg_mul, Finset.sum_neg_distrib]
    exact h
  | .cosv k => by
    have h := (hasDerivAt_getV p v t k).cos
    have hs : ∑ j : Fin NV, eval (seg p v t) ((Expr.cosv k).D j) * v j
        = -Real.sin (getV (seg p v t) k) * getV v k := by
      simp only [eval_D_cosv]
      rw [← sum_D_var (seg p v t) v k]
      simp only [eval_D_var, Finset.mul_sum]
      exact Finset.sum_congr rfl fun j _ => by split_ifs <;> ring
    rw [hs]
    exact h
  | .sinv k => by
    have h := (hasDerivAt_getV p v t k).sin
    have hs : ∑ j : Fin NV, eval (seg p v t) ((Expr.sinv k).D j) * v j
        = Real.cos (getV (seg p v t) k) * getV v k := by
      simp only [eval_D_sinv]
      rw [← sum_D_var (seg p v t) v k]
      simp only [eval_D_var, Finset.mul_sum]
      exact Finset.sum_congr rfl fun j _ => by split_ifs <;> ring
    rw [hs]
    exact h

theorem seg_zero (p v : Vec) : seg p v 0 = p := by
  funext i; simp [seg]

theorem seg_one_sub (p q : Vec) : seg p (fun i => q i - p i) 1 = q := by
  funext i; simp [seg]

theorem seg_memBox {b : Array IV} {p q : Vec} (hp : MemBox b p) (hq : MemBox b q) {t : ℝ}
    (h0 : 0 ≤ t) (h1 : t ≤ 1) : MemBox b (seg p (fun i => q i - p i) t) := by
  refine ⟨hp.1, fun k => ?_⟩
  obtain ⟨hp1, hp2⟩ := hp.2 k
  obtain ⟨hq1, hq2⟩ := hq.2 k
  simp only [seg]
  constructor <;> nlinarith

/-- **Mean value theorem on a box**: for `p, q` in the box there is `ξ` in the box with
`eval q e − eval p e = ∑_j ∂_j e(ξ)·(q_j − p_j)`. -/
theorem mvt_box {b : Array IV} {p q : Vec} (hp : MemBox b p) (hq : MemBox b q) (e : Expr) :
    ∃ ξ : Vec, MemBox b ξ ∧ eval q e - eval p e = ∑ j : Fin NV, eval ξ (e.D j) * (q j - p j) := by
  have hd : ∀ t, HasDerivAt (fun t => eval (seg p (fun i => q i - p i) t) e)
      (∑ j : Fin NV, eval (seg p (fun i => q i - p i) t) (e.D j) * (q j - p j)) t :=
    fun t => hasDerivAt_eval p (fun i => q i - p i) t e
  obtain ⟨c, hc, hderiv⟩ := exists_hasDerivAt_eq_slope
    (fun t => eval (seg p (fun i => q i - p i) t) e)
    (fun t => ∑ j : Fin NV, eval (seg p (fun i => q i - p i) t) (e.D j) * (q j - p j))
    (by norm_num : (0 : ℝ) < 1)
    (fun t _ => (hd t).continuousAt.continuousWithinAt) (fun t _ => hd t)
  refine ⟨seg p (fun i => q i - p i) c, seg_memBox hp hq hc.1.le hc.2.le, ?_⟩
  rw [seg_one_sub, seg_zero, sub_zero, div_one] at hderiv
  exact hderiv.symm

end PackingCert.Rigid
