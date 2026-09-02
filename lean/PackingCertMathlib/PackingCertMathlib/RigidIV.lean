import Mathlib.Analysis.SpecialFunctions.Trigonometric.Series
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.Real.Pi.Bounds
import Mathlib.Tactic
import PackingCertMathlib.RigidKernel
import PackingCertMathlib.CaseHyp

/-!
# Soundness of the rigidity interval kernel (A79)

`RigidKernel.lean`'s arithmetic really encloses: dyadic rounding only widens
(`rdown_le`, `le_rup`), every `IV` operation encloses the real operation on enclosed
operands (`mem_add`, …, `mem_mul`, `mem_mag`), and the alternating-Taylor brackets
enclose `cos`/`sin` at rational points with `|x| ≤ 1` (`cosPt_sound`, `sinPt_sound`;
Mathlib's `Real.hasSum_cos`/`Real.hasSum_sin` + the antitone alternating-series bounds),
lifted to intervals by the monotonicity of `cos` on `[0, π]` and of `sin` on
`[-π/2, π/2]` (`cosIV_sound`, `sinIV_sound`).
-/

namespace PackingCert.Rigid

open PackingCert.CaseI PackingCert.S11 Finset Filter Topology

/-! ## Rounding -/

theorem GRIDQ_pos : (0 : ℚ) < GRIDQ := by
  unfold GRIDQ GRIDZ
  exact_mod_cast (by positivity : (0 : ℤ) < 2 ^ PREC)

theorem ratFloor_eq (q : ℚ) : q.floor = ⌊q⌋ := rfl

theorem rdown_le (x : ℚ) : rdown x ≤ x := by
  unfold rdown
  rw [ratFloor_eq, div_le_iff₀ GRIDQ_pos]
  exact Int.floor_le _

theorem le_rup (x : ℚ) : x ≤ rup x := by
  unfold rup
  have := rdown_le (-x)
  linarith

/-! ## Interval membership -/

/-- `x` lies in the rational interval `a`. -/
def Mem (x : ℝ) (a : IV) : Prop := (a.lo : ℝ) ≤ x ∧ x ≤ (a.hi : ℝ)

theorem mem_mkR {lo hi : ℚ} {x : ℝ} (h1 : (lo : ℝ) ≤ x) (h2 : x ≤ (hi : ℝ)) :
    Mem x (IV.mkR lo hi) := by
  refine ⟨?_, ?_⟩
  · calc ((IV.mkR lo hi).lo : ℝ) = ((rdown lo : ℚ) : ℝ) := rfl
      _ ≤ (lo : ℝ) := by exact_mod_cast rdown_le lo
      _ ≤ x := h1
  · calc x ≤ (hi : ℝ) := h2
      _ ≤ ((rup hi : ℚ) : ℝ) := by exact_mod_cast le_rup hi
      _ = ((IV.mkR lo hi).hi : ℝ) := rfl

theorem mem_pt (q : ℚ) : Mem (q : ℝ) (IV.pt q) := mem_mkR le_rfl le_rfl

theorem mem_zero : Mem 0 IV.zero := by simp [Mem, IV.zero]

theorem mem_one : Mem 1 IV.one := by simp [Mem, IV.one]

theorem mem_add {x y : ℝ} {a b : IV} (ha : Mem x a) (hb : Mem y b) : Mem (x + y) (a + b) := by
  change Mem (x + y) (IV.mkR (a.lo + b.lo) (a.hi + b.hi))
  exact mem_mkR (by push_cast; linarith [ha.1, hb.1]) (by push_cast; linarith [ha.2, hb.2])

theorem mem_sub {x y : ℝ} {a b : IV} (ha : Mem x a) (hb : Mem y b) : Mem (x - y) (a - b) := by
  change Mem (x - y) (IV.mkR (a.lo - b.hi) (a.hi - b.lo))
  exact mem_mkR (by push_cast; linarith [ha.1, hb.2]) (by push_cast; linarith [ha.2, hb.1])

theorem mem_neg {x : ℝ} {a : IV} (ha : Mem x a) : Mem (-x) (-a) := by
  change Mem (-x) ⟨-a.hi, -a.lo⟩
  exact ⟨by push_cast; linarith [ha.2], by push_cast; linarith [ha.1]⟩

theorem mem_mul {x y : ℝ} {a b : IV} (ha : Mem x a) (hb : Mem y b) : Mem (x * y) (a * b) := by
  change Mem (x * y) (IV.mkR
    (rmin (rmin (a.lo * b.lo) (a.lo * b.hi)) (rmin (a.hi * b.lo) (a.hi * b.hi)))
    (rmax (rmax (a.lo * b.lo) (a.lo * b.hi)) (rmax (a.hi * b.lo) (a.hi * b.hi))))
  obtain ⟨h1, h2⟩ := mul_bounds ha.1 ha.2 hb.1 hb.2
  refine mem_mkR ?_ ?_
  · rw [rmin_cast, rmin_cast, rmin_cast]; push_cast; exact h1
  · rw [rmax_cast, rmax_cast, rmax_cast]; push_cast; exact h2

theorem mem_mag {x : ℝ} {a : IV} (ha : Mem x a) : |x| ≤ (a.mag : ℝ) := by
  change |x| ≤ ((rmax (rabs a.lo) (rabs a.hi) : ℚ) : ℝ)
  rw [rmax_cast, rabs_cast, rabs_cast]
  rw [abs_le]
  constructor
  · have := neg_abs_le (a.lo : ℝ)
    have := le_max_left |(a.lo : ℝ)| |(a.hi : ℝ)|
    linarith [ha.1]
  · have := le_abs_self (a.hi : ℝ)
    have := le_max_right |(a.lo : ℝ)| |(a.hi : ℝ)|
    linarith [ha.2]

theorem mag_nonneg (a : IV) : (0 : ℚ) ≤ a.mag := by
  have : ((0 : ℚ) : ℝ) ≤ (a.mag : ℝ) := by
    change ((0 : ℚ) : ℝ) ≤ ((rmax (rabs a.lo) (rabs a.hi) : ℚ) : ℝ)
    rw [rmax_cast, rabs_cast, rabs_cast]
    push_cast
    exact le_trans (abs_nonneg _) (le_max_left _ _)
  exact_mod_cast this

theorem mem_lo_le_hi {x : ℝ} {a : IV} (ha : Mem x a) : (a.lo : ℝ) ≤ (a.hi : ℝ) :=
  le_trans ha.1 ha.2

/-! ## Taylor brackets -/

theorem neg_one_pow_of_mod (n : ℕ) :
    ((-1 : ℝ) ^ n) = if n % 2 = 0 then 1 else -1 := by
  split_ifs with h
  · exact (Nat.even_iff.mpr h).neg_one_pow
  · exact (Nat.odd_iff.mpr (Nat.mod_two_ne_zero.mp h)).neg_one_pow

theorem cosPartial_spec (x : ℚ) : ∀ n : ℕ,
    (((cosPartial (x * x) n).1 : ℚ) : ℝ)
        = ∑ m ∈ range n, (-1 : ℝ) ^ m * ((x : ℝ) ^ (2 * m) / ((2 * m).factorial : ℝ)) ∧
      (((cosPartial (x * x) n).2 : ℚ) : ℝ) = (x : ℝ) ^ (2 * n) / ((2 * n).factorial : ℝ)
  | 0 => by simp [cosPartial]
  | n + 1 => by
    obtain ⟨ih1, ih2⟩ := cosPartial_spec x n
    have hf : ((2 * (n + 1)).factorial : ℝ) = (2 * n + 2) * (2 * n + 1) * ((2 * n).factorial : ℝ) := by
      rw [show 2 * (n + 1) = 2 * n + 1 + 1 by ring, Nat.factorial_succ, Nat.factorial_succ]
      push_cast; ring
    have hfpos : (0 : ℝ) < ((2 * n).factorial : ℝ) := by positivity
    constructor
    · rw [sum_range_succ, ← ih1]
      simp only [cosPartial]
      split_ifs with h
      · push_cast; rw [ih2, neg_one_pow_of_mod, if_pos h]; ring
      · push_cast; rw [ih2, neg_one_pow_of_mod, if_neg h]; ring
    · simp only [cosPartial]
      push_cast
      rw [ih2, hf]
      field_simp
      ring

theorem sinPartial_spec (x : ℚ) : ∀ n : ℕ,
    (((sinPartial x (x * x) n).1 : ℚ) : ℝ)
        = ∑ m ∈ range n, (-1 : ℝ) ^ m * ((x : ℝ) ^ (2 * m + 1) / ((2 * m + 1).factorial : ℝ)) ∧
      (((sinPartial x (x * x) n).2 : ℚ) : ℝ) = (x : ℝ) ^ (2 * n + 1) / ((2 * n + 1).factorial : ℝ)
  | 0 => by simp [sinPartial]
  | n + 1 => by
    obtain ⟨ih1, ih2⟩ := sinPartial_spec x n
    have hf : ((2 * (n + 1) + 1).factorial : ℝ)
        = (2 * n + 3) * (2 * n + 2) * ((2 * n + 1).factorial : ℝ) := by
      rw [show 2 * (n + 1) + 1 = 2 * n + 1 + 1 + 1 by ring, Nat.factorial_succ, Nat.factorial_succ]
      push_cast; ring
    have hfpos : (0 : ℝ) < ((2 * n + 1).factorial : ℝ) := by positivity
    constructor
    · rw [sum_range_succ, ← ih1]
      simp only [sinPartial]
      split_ifs with h
      · push_cast; rw [ih2, neg_one_pow_of_mod, if_pos h]; ring
      · push_cast; rw [ih2, neg_one_pow_of_mod, if_neg h]; ring
    · simp only [sinPartial]
      push_cast
      rw [ih2, hf]
      field_simp
      ring

theorem sq_le_one_of_abs_le_one {x : ℝ} (hx : |x| ≤ 1) : x ^ 2 ≤ 1 := by
  have := abs_nonneg x
  nlinarith [sq_abs x]

/-- The alternating cosine series brackets `cos x` for `|x| ≤ 1`. -/
theorem cos_bracket {x : ℝ} (hx : |x| ≤ 1) (k : ℕ) :
    ∑ i ∈ range (2 * k), (-1 : ℝ) ^ i * (x ^ (2 * i) / ((2 * i).factorial : ℝ)) ≤ Real.cos x ∧
      Real.cos x ≤ ∑ i ∈ range (2 * k + 1), (-1 : ℝ) ^ i * (x ^ (2 * i) / ((2 * i).factorial : ℝ)) := by
  set f : ℕ → ℝ := fun i => x ^ (2 * i) / ((2 * i).factorial : ℝ) with hf
  have hfl : Tendsto (fun n => ∑ i ∈ range n, (-1 : ℝ) ^ i * f i) atTop (𝓝 (Real.cos x)) := by
    have := (Real.hasSum_cos x).tendsto_sum_nat
    refine this.congr fun n => ?_
    refine sum_congr rfl fun i _ => ?_
    simp only [hf]; ring
  have hfa : Antitone f := by
    refine antitone_nat_of_succ_le fun n => ?_
    simp only [hf]
    have hx2 : x ^ 2 ≤ 1 := sq_le_one_of_abs_le_one hx
    have hp : 0 ≤ x ^ (2 * n) := by
      rw [pow_mul]; exact pow_nonneg (sq_nonneg x) n
    have hnum : x ^ (2 * (n + 1)) ≤ x ^ (2 * n) := by
      rw [show 2 * (n + 1) = 2 * n + 2 by ring, pow_add]
      nlinarith
    have hden : ((2 * n).factorial : ℝ) ≤ ((2 * (n + 1)).factorial : ℝ) := by
      exact_mod_cast Nat.factorial_le (by omega)
    have hdpos : (0 : ℝ) < ((2 * n).factorial : ℝ) := by positivity
    exact div_le_div₀ hp hnum hdpos hden
  exact ⟨hfa.alternating_series_le_tendsto hfl k, hfa.tendsto_le_alternating_series hfl k⟩

/-- The alternating sine series brackets `sin x` for `0 ≤ x ≤ 1`. -/
theorem sin_bracket {x : ℝ} (hx0 : 0 ≤ x) (hx1 : x ≤ 1) (k : ℕ) :
    ∑ i ∈ range (2 * k), (-1 : ℝ) ^ i * (x ^ (2 * i + 1) / ((2 * i + 1).factorial : ℝ)) ≤ Real.sin x ∧
      Real.sin x ≤ ∑ i ∈ range (2 * k + 1),
        (-1 : ℝ) ^ i * (x ^ (2 * i + 1) / ((2 * i + 1).factorial : ℝ)) := by
  set f : ℕ → ℝ := fun i => x ^ (2 * i + 1) / ((2 * i + 1).factorial : ℝ) with hf
  have hfl : Tendsto (fun n => ∑ i ∈ range n, (-1 : ℝ) ^ i * f i) atTop (𝓝 (Real.sin x)) := by
    have := (Real.hasSum_sin x).tendsto_sum_nat
    refine this.congr fun n => ?_
    refine sum_congr rfl fun i _ => ?_
    simp only [hf]; ring
  have hfa : Antitone f := by
    refine antitone_nat_of_succ_le fun n => ?_
    simp only [hf]
    have hx2 : x ^ 2 ≤ 1 := by nlinarith
    have hp : 0 ≤ x ^ (2 * n + 1) := pow_nonneg hx0 _
    have hnum : x ^ (2 * (n + 1) + 1) ≤ x ^ (2 * n + 1) := by
      rw [show 2 * (n + 1) + 1 = 2 * n + 1 + 2 by ring, pow_add]
      nlinarith
    have hden : ((2 * n + 1).factorial : ℝ) ≤ ((2 * (n + 1) + 1).factorial : ℝ) := by
      exact_mod_cast Nat.factorial_le (by omega)
    have hdpos : (0 : ℝ) < ((2 * n + 1).factorial : ℝ) := by positivity
    exact div_le_div₀ hp hnum hdpos hden
  exact ⟨hfa.alternating_series_le_tendsto hfl k, hfa.tendsto_le_alternating_series hfl k⟩

theorem rabs_le_one_cast {x : ℚ} (h : rabs x ≤ 1) : |(x : ℝ)| ≤ 1 := by
  have : ((rabs x : ℚ) : ℝ) ≤ ((1 : ℚ) : ℝ) := by exact_mod_cast h
  rw [rabs_cast] at this
  simpa using this

theorem cosPt_sound (x : ℚ) :
    (((cosPt x).1 : ℚ) : ℝ) ≤ Real.cos (x : ℝ) ∧ Real.cos (x : ℝ) ≤ (((cosPt x).2 : ℚ) : ℝ) := by
  unfold cosPt
  split_ifs with h
  · have hx := rabs_le_one_cast h
    obtain ⟨h1, h2⟩ := cosPartial_spec x (2 * KTAY)
    obtain ⟨hlo, hhi⟩ := cos_bracket hx KTAY
    constructor
    · calc (((rdown (cosPartial (x * x) (2 * KTAY)).1 : ℚ)) : ℝ)
          ≤ (((cosPartial (x * x) (2 * KTAY)).1 : ℚ) : ℝ) := by exact_mod_cast rdown_le _
        _ = _ := h1
        _ ≤ Real.cos x := hlo
    · have hsum : ∑ i ∈ range (2 * KTAY + 1), (-1 : ℝ) ^ i * ((x : ℝ) ^ (2 * i) / ((2 * i).factorial : ℝ))
          = (((cosPartial (x * x) (2 * KTAY)).1 : ℚ) : ℝ)
            + (((cosPartial (x * x) (2 * KTAY)).2 : ℚ) : ℝ) := by
        rw [sum_range_succ, h1, h2, (even_two_mul KTAY).neg_one_pow, one_mul]
      calc Real.cos x ≤ _ := hhi
        _ = _ := hsum
        _ = (((cosPartial (x * x) (2 * KTAY)).1 + (cosPartial (x * x) (2 * KTAY)).2 : ℚ) : ℝ) := by
          push_cast; ring
        _ ≤ _ := by exact_mod_cast le_rup _
  · exact ⟨by simpa using Real.neg_one_le_cos (x : ℝ), by simpa using Real.cos_le_one (x : ℝ)⟩

theorem sinPtNN_sound {x : ℚ} (hx : 0 ≤ x) :
    (((sinPtNN x).1 : ℚ) : ℝ) ≤ Real.sin (x : ℝ) ∧ Real.sin (x : ℝ) ≤ (((sinPtNN x).2 : ℚ) : ℝ) := by
  unfold sinPtNN
  split_ifs with h
  · have hx0 : (0 : ℝ) ≤ (x : ℝ) := by exact_mod_cast hx
    have hx1 : (x : ℝ) ≤ 1 := by exact_mod_cast h
    obtain ⟨h1, h2⟩ := sinPartial_spec x (2 * KTAY)
    obtain ⟨hlo, hhi⟩ := sin_bracket hx0 hx1 KTAY
    constructor
    · calc (((rdown (sinPartial x (x * x) (2 * KTAY)).1 : ℚ)) : ℝ)
          ≤ (((sinPartial x (x * x) (2 * KTAY)).1 : ℚ) : ℝ) := by exact_mod_cast rdown_le _
        _ = _ := h1
        _ ≤ Real.sin x := hlo
    · have hsum : ∑ i ∈ range (2 * KTAY + 1),
            (-1 : ℝ) ^ i * ((x : ℝ) ^ (2 * i + 1) / ((2 * i + 1).factorial : ℝ))
          = (((sinPartial x (x * x) (2 * KTAY)).1 : ℚ) : ℝ)
            + (((sinPartial x (x * x) (2 * KTAY)).2 : ℚ) : ℝ) := by
        rw [sum_range_succ, h1, h2, (even_two_mul KTAY).neg_one_pow, one_mul]
      calc Real.sin x ≤ _ := hhi
        _ = _ := hsum
        _ = (((sinPartial x (x * x) (2 * KTAY)).1 + (sinPartial x (x * x) (2 * KTAY)).2 : ℚ) : ℝ) := by
          push_cast; ring
        _ ≤ _ := by exact_mod_cast le_rup _
  · exact ⟨by simpa using Real.neg_one_le_sin (x : ℝ), by simpa using Real.sin_le_one (x : ℝ)⟩

theorem sinPt_sound (x : ℚ) :
    (((sinPt x).1 : ℚ) : ℝ) ≤ Real.sin (x : ℝ) ∧ Real.sin (x : ℝ) ≤ (((sinPt x).2 : ℚ) : ℝ) := by
  unfold sinPt
  split_ifs with h
  · obtain ⟨h1, h2⟩ := sinPtNN_sound (x := -x) (by linarith)
    push_cast at h1 h2
    rw [Real.sin_neg] at h1 h2
    constructor
    · push_cast; linarith
    · push_cast; linarith
  · exact sinPtNN_sound (not_lt.mp h)

/-! ## Interval trigonometry -/

theorem one_lt_pi_div_two : (1 : ℝ) < Real.pi / 2 := by linarith [Real.pi_gt_three]

theorem cosIV_sound {θ : ℝ} {v : IV} (hθ : Mem θ v) : Mem (Real.cos θ) (cosIV v) := by
  unfold cosIV
  by_cases hc : (rabs v.lo ≤ 1 && rabs v.hi ≤ 1) = true
  · rw [if_pos hc]
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
    have hlo := rabs_le_one_cast hc.1
    have hhi := rabs_le_one_cast hc.2
    obtain ⟨a1, a2⟩ := cosPt_sound v.lo
    obtain ⟨b1, b2⟩ := cosPt_sound v.hi
    have hpi := Real.pi_gt_three
    have hθ1 : |θ| ≤ 1 := by
      rw [abs_le] at hlo hhi ⊢
      exact ⟨by linarith [hθ.1], by linarith [hθ.2]⟩
    constructor
    · -- lower bound: `cos θ ≥ cos (max |lo| |hi|)`
      change ((rmin (cosPt v.lo).1 (cosPt v.hi).1 : ℚ) : ℝ) ≤ Real.cos θ
      rw [rmin_cast]
      have key : ∀ y : ℝ, |y| ≤ 1 → |θ| ≤ |y| → Real.cos y ≤ Real.cos θ := by
        intro y hy hθy
        rw [← Real.cos_abs θ, ← Real.cos_abs y]
        exact Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg θ) (by linarith) hθy
      rcases le_total |(v.lo : ℝ)| |(v.hi : ℝ)| with hab | hab
      · -- `|hi|` is the larger endpoint magnitude
        have h1 : |θ| ≤ |(v.hi : ℝ)| := by
          rw [abs_le]
          constructor
          · linarith [hθ.1, neg_abs_le (v.lo : ℝ), hab]
          · linarith [hθ.2, le_abs_self (v.hi : ℝ)]
        exact le_trans (min_le_right _ _) (le_trans b1 (key _ hhi h1))
      · have h1 : |θ| ≤ |(v.lo : ℝ)| := by
          rw [abs_le]
          constructor
          · linarith [hθ.1, neg_abs_le (v.lo : ℝ)]
          · linarith [hθ.2, le_abs_self (v.hi : ℝ), hab]
        exact le_trans (min_le_left _ _) (le_trans a1 (key _ hlo h1))
    · change Real.cos θ ≤ ((if (v.lo ≤ 0 && 0 ≤ v.hi) = true then (1 : ℚ)
          else rmax (cosPt v.lo).2 (cosPt v.hi).2 : ℚ) : ℝ)
      by_cases hz : (v.lo ≤ 0 && 0 ≤ v.hi) = true
      · rw [if_pos hz]
        simpa using Real.cos_le_one θ
      · rw [if_neg hz, rmax_cast]
        simp only [Bool.and_eq_true, decide_eq_true_eq, not_and_or, not_le] at hz
        rcases hz with hz | hz
        · -- `0 < lo ≤ θ`
          have hlo' : (0 : ℝ) < (v.lo : ℝ) := by exact_mod_cast hz
          have : Real.cos θ ≤ Real.cos (v.lo : ℝ) :=
            Real.cos_le_cos_of_nonneg_of_le_pi hlo'.le (by linarith [abs_le.mp hθ1]) hθ.1
          exact le_trans this (le_trans a2 (le_max_left _ _))
        · -- `θ ≤ hi < 0`
          have hhi' : (v.hi : ℝ) < 0 := by exact_mod_cast hz
          have : Real.cos θ ≤ Real.cos (v.hi : ℝ) := by
            rw [← Real.cos_neg θ, ← Real.cos_neg (v.hi : ℝ)]
            exact Real.cos_le_cos_of_nonneg_of_le_pi (by linarith) (by linarith [abs_le.mp hθ1])
              (by linarith [hθ.2])
          exact le_trans this (le_trans b2 (le_max_right _ _))
  · rw [if_neg hc]
    exact ⟨by simpa using Real.neg_one_le_cos θ, by simpa using Real.cos_le_one θ⟩

theorem sinIV_sound {θ : ℝ} {v : IV} (hθ : Mem θ v) : Mem (Real.sin θ) (sinIV v) := by
  unfold sinIV
  by_cases hc : (rabs v.lo ≤ 1 && rabs v.hi ≤ 1) = true
  · rw [if_pos hc]
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
    have hlo := abs_le.mp (rabs_le_one_cast hc.1)
    have hhi := abs_le.mp (rabs_le_one_cast hc.2)
    have hp := one_lt_pi_div_two
    obtain ⟨a1, -⟩ := sinPt_sound v.lo
    obtain ⟨-, b2⟩ := sinPt_sound v.hi
    constructor
    · exact le_trans a1
        (Real.sin_le_sin_of_le_of_le_pi_div_two (by linarith) (by linarith [hθ.2]) hθ.1)
    · exact le_trans
        (Real.sin_le_sin_of_le_of_le_pi_div_two (by linarith [hθ.1]) (by linarith) hθ.2) b2
  · rw [if_neg hc]
    exact ⟨by simpa using Real.neg_one_le_sin θ, by simpa using Real.sin_le_one θ⟩

end PackingCert.Rigid
