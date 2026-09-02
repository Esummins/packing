import Mathlib.Analysis.SpecialFunctions.Trigonometric.ArctanDeriv
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Tactic
import PackingCertMathlib.Parametrize

/-!
# The θ ↔ t coordinate transfer (A68, depgraph node E.COORD)

`docs/proofs/theta_t_transfer.md` X.1–X.3, formalised.  The rigidity/basin certificates
(A22 `r_N = 5e-4`, A36 `h = 37/10000`) are ∞-norm boxes in `(c, θ, s)`; the composition's
configuration space uses `t = tan(θ/2) ∈ [0, 1]`.  This file proves the exact transfer
constants that justify the Lean definition `rBasin = 3/2000` (`TopLevel.lean`, discharged
by A63 in prose):

* `cosT_eq_cos` / `sinT_eq_sin` — the rational parametrisation really is the trigonometry
  of the angle `θ(t) = 2·arctan t` (the only place the lab's `t`-world is formally tied to
  the certificates' θ-world);
* X.1: `theta_lipschitz` — `|θ₁ − θ₂| ≤ 2·|t₁ − t₂|` (all reals; `arctan` is 1-Lipschitz),
  and `sub_le_theta` — `|t₁ − t₂| ≤ |θ₁ − θ₂|` on `t ∈ [0, 1]` (`tan` is 2-Lipschitz on
  `[0, π/4]`), i.e. `|Δt| ≤ |Δθ| ≤ 2·|Δt|`;
* `circle_dist_sq_le` / `cossinT_dist_sq_le` — the circle map is 1-Lipschitz (Euclidean),
  so `(ΔcosT)² + (ΔsinT)² ≤ (Δθ)² ≤ 4·(Δt)²`;
* X.2: `corner_perturb` — centre moves ≤ `r_c`, half-angle parameter moves ≤ `r_t` ⟹
  every fixed-body-coordinate point of the square (in particular every corner) moves
  ≤ `r_c + √2·r_t` per coordinate — the SHARP constant (the naive per-component estimate
  gives `r_c + 2·r_t`, which does NOT close gate (b) below);
* X.3: the two rBasin gates, `gate_tilt` (`2·(3/2000) ≤ 37/10000`) and `gate_slab`
  (`(3/2000)·(1+√2) < 37/10000` — the binding one: `3/2000` against the exact threshold
  `(37/10000)/(1+√2) ≈ 1.532e-3`), plus the composed `corner_perturb_rBasin`.

What this does NOT discharge: the `basin` axiom itself (A36's interval computations remain
Python-certified — the mpmath.iv trust item, checklist F6); and the wall-touching step of
X.3(b) (`s ≥ ŝ − r(1+√2)` for containers of perturbed configurations) consumes properties
of the opaque `zhat`, so it lives in the `basin` axiom's docstring justification, now with
its two arithmetic gates machine-checked.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-- The angle denoted by the half-angle parameter: `θ(t) = 2·arctan t`. -/
def thetaOf (t : ℝ) : ℝ := 2 * Real.arctan t

/-- `cosT` is the cosine of the angle: the `t`-world is the θ-world. -/
theorem cosT_eq_cos (t : ℝ) : cosT t = Real.cos (thetaOf t) := by
  rw [thetaOf, Real.cos_two_mul, Real.cos_sq_arctan]
  have h : (0 : ℝ) < 1 + t ^ 2 := one_add_sq_pos t
  unfold cosT
  field_simp
  ring

/-- `sinT` is the sine of the angle. -/
theorem sinT_eq_sin (t : ℝ) : sinT t = Real.sin (thetaOf t) := by
  rw [thetaOf, Real.sin_two_mul, Real.sin_arctan, Real.cos_arctan]
  have h : (0 : ℝ) < 1 + t ^ 2 := one_add_sq_pos t
  have hss : Real.sqrt (1 + t ^ 2) * Real.sqrt (1 + t ^ 2) = 1 + t ^ 2 :=
    Real.mul_self_sqrt h.le
  have hs0 : (0 : ℝ) < Real.sqrt (1 + t ^ 2) := Real.sqrt_pos.mpr h
  unfold sinT
  field_simp [hs0.ne']
  linear_combination t * hss

/-! ## X.1: the two-sided Lipschitz transfer -/

/-- `arctan` is 1-Lipschitz (mean value theorem, `arctan′ = 1/(1+x²) ≤ 1`). -/
theorem abs_arctan_sub_le (a b : ℝ) : |Real.arctan a - Real.arctan b| ≤ |a - b| := by
  have key := Convex.norm_image_sub_le_of_norm_hasDerivWithin_le
    (f := Real.arctan) (f' := fun x => 1 / (1 + x ^ 2)) (s := univ) (C := 1)
    (fun x _ => (Real.hasDerivAt_arctan x).hasDerivWithinAt)
    (fun x _ => by
      rw [Real.norm_eq_abs, abs_of_pos (by positivity), div_le_one (by positivity)]
      nlinarith [sq_nonneg x])
    convex_univ (mem_univ b) (mem_univ a)
  simpa [Real.norm_eq_abs] using key

/-- **X.1, upper transfer**: `|θ₁ − θ₂| ≤ 2·|t₁ − t₂|`, for ALL reals. -/
theorem theta_lipschitz (t₁ t₂ : ℝ) : |thetaOf t₁ - thetaOf t₂| ≤ 2 * |t₁ - t₂| := by
  have h := abs_arctan_sub_le t₁ t₂
  have he : thetaOf t₁ - thetaOf t₂ = 2 * (Real.arctan t₁ - Real.arctan t₂) := by
    rw [thetaOf, thetaOf]; ring
  rw [he, abs_mul, abs_two]
  linarith

/-- `tan` is 2-Lipschitz on `[0, π/4]` (`tan′ = 1/cos² ≤ 2` there). -/
theorem abs_tan_sub_le {a b : ℝ} (ha : a ∈ Icc (0 : ℝ) (Real.pi / 4))
    (hb : b ∈ Icc (0 : ℝ) (Real.pi / 4)) :
    |Real.tan a - Real.tan b| ≤ 2 * |a - b| := by
  have hpi := Real.pi_pos
  have hcos : ∀ x ∈ Icc (0 : ℝ) (Real.pi / 4),
      Real.cos x ≠ 0 ∧ (1 : ℝ) / 2 ≤ Real.cos x ^ 2 := by
    intro x hx
    have h4 : Real.cos (Real.pi / 4) ≤ Real.cos x :=
      Real.strictAntiOn_cos.antitoneOn ⟨hx.1, by linarith [hx.2]⟩
        ⟨by positivity, by linarith⟩ hx.2
    rw [Real.cos_pi_div_four] at h4
    have hs2 : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
    have hs0 : (0 : ℝ) < Real.sqrt 2 := by nlinarith [Real.sqrt_nonneg 2]
    have hpos : (0 : ℝ) < Real.cos x := by nlinarith
    exact ⟨hpos.ne', by nlinarith⟩
  have key := Convex.norm_image_sub_le_of_norm_hasDerivWithin_le
    (f := Real.tan) (f' := fun x => 1 / Real.cos x ^ 2) (s := Icc (0 : ℝ) (Real.pi / 4))
    (C := 2)
    (fun x hx => (Real.hasDerivAt_tan (hcos x hx).1).hasDerivWithinAt)
    (fun x hx => by
      obtain ⟨hne, hge⟩ := hcos x hx
      have h2 : (0 : ℝ) < Real.cos x ^ 2 := by nlinarith
      rw [Real.norm_eq_abs, abs_of_pos (div_pos one_pos h2), div_le_iff₀ h2]
      nlinarith)
    (convex_Icc _ _) hb ha
  simpa [Real.norm_eq_abs] using key

/-- **X.1, lower transfer**: `|t₁ − t₂| ≤ |θ₁ − θ₂|` on `t ∈ [0, 1]`. -/
theorem sub_le_theta {t₁ t₂ : ℝ} (h₁ : t₁ ∈ Icc (0 : ℝ) 1) (h₂ : t₂ ∈ Icc (0 : ℝ) 1) :
    |t₁ - t₂| ≤ |thetaOf t₁ - thetaOf t₂| := by
  have harc : ∀ t : ℝ, t ∈ Icc (0 : ℝ) 1 → Real.arctan t ∈ Icc (0 : ℝ) (Real.pi / 4) := by
    intro t ht
    refine ⟨Real.arctan_nonneg.mpr ht.1, ?_⟩
    rw [← Real.arctan_one]
    exact Real.arctan_le_arctan_iff.mpr ht.2
  have key := abs_tan_sub_le (harc t₁ h₁) (harc t₂ h₂)
  rw [Real.tan_arctan, Real.tan_arctan] at key
  have he : thetaOf t₁ - thetaOf t₂ = 2 * (Real.arctan t₁ - Real.arctan t₂) := by
    rw [thetaOf, thetaOf]; ring
  rw [he, abs_mul, abs_two]
  linarith

/-! ## The circle map is 1-Lipschitz (Euclidean) -/

/-- `(Δcos)² + (Δsin)² = 2 − 2·cos(Δθ) ≤ (Δθ)²`. -/
theorem circle_dist_sq_le (a b : ℝ) :
    (Real.cos a - Real.cos b) ^ 2 + (Real.sin a - Real.sin b) ^ 2 ≤ (a - b) ^ 2 := by
  have hexp : (Real.cos a - Real.cos b) ^ 2 + (Real.sin a - Real.sin b) ^ 2
      = 2 - 2 * Real.cos (a - b) := by
    rw [Real.cos_sub]
    linear_combination Real.sin_sq_add_cos_sq a + Real.sin_sq_add_cos_sq b
  rw [hexp]
  nlinarith [Real.one_sub_sq_div_two_le_cos (x := a - b)]

/-- The `t`-world circle bound: `(ΔcosT)² + (ΔsinT)² ≤ 4·(Δt)²`. -/
theorem cossinT_dist_sq_le (t₁ t₂ : ℝ) :
    (cosT t₁ - cosT t₂) ^ 2 + (sinT t₁ - sinT t₂) ^ 2 ≤ 4 * (t₁ - t₂) ^ 2 := by
  rw [cosT_eq_cos, cosT_eq_cos, sinT_eq_sin, sinT_eq_sin]
  have h1 := circle_dist_sq_le (thetaOf t₁) (thetaOf t₂)
  have h2 := theta_lipschitz t₁ t₂
  have h3 : (thetaOf t₁ - thetaOf t₂) ^ 2 ≤ 4 * (t₁ - t₂) ^ 2 := by
    nlinarith [sq_abs (thetaOf t₁ - thetaOf t₂), sq_abs (t₁ - t₂),
      abs_nonneg (thetaOf t₁ - thetaOf t₂), abs_nonneg (t₁ - t₂)]
  linarith

/-! ## X.2: the corner-perturbation lemma, sharp constant -/

private theorem cs_bound {X Y rt A B : ℝ} (hrt : 0 ≤ rt) (hXY : X ^ 2 + Y ^ 2 ≤ 4 * rt ^ 2)
    (hAB : A ^ 2 + B ^ 2 ≤ 1 / 2) : |A * X + B * Y| ≤ Real.sqrt 2 * rt := by
  have h1 : (A * X + B * Y) ^ 2 ≤ (A ^ 2 + B ^ 2) * (X ^ 2 + Y ^ 2) := by
    nlinarith [sq_nonneg (A * Y - B * X)]
  have h2 : (A ^ 2 + B ^ 2) * (X ^ 2 + Y ^ 2) ≤ 1 / 2 * (4 * rt ^ 2) :=
    mul_le_mul hAB hXY (by positivity) (by norm_num)
  have hsq : (A * X + B * Y) ^ 2 ≤ 2 * rt ^ 2 := by linarith
  have habs : |A * X + B * Y| = Real.sqrt ((A * X + B * Y) ^ 2) :=
    (Real.sqrt_sq_eq_abs _).symm
  rw [habs]
  calc Real.sqrt ((A * X + B * Y) ^ 2) ≤ Real.sqrt (2 * rt ^ 2) := Real.sqrt_le_sqrt hsq
    _ = Real.sqrt 2 * rt := by
        rw [Real.sqrt_mul (by norm_num : (0 : ℝ) ≤ 2), Real.sqrt_sq hrt]

/-- **X.2 (t-world).**  If the centre moves by ≤ `r_c` per coordinate and the half-angle
parameter by ≤ `r_t`, every fixed-body-coordinate point of the square — in particular
every corner (`a, b ∈ {0, 1}`) — moves by at most `r_c + √2·r_t` per coordinate. -/
theorem corner_perturb {q q' : PSq} {rc rt : ℝ}
    (hcx : |q.cx - q'.cx| ≤ rc) (hcy : |q.cy - q'.cy| ≤ rc) (ht : |q.t - q'.t| ≤ rt)
    {a b : ℝ} (ha : a ∈ Icc (0 : ℝ) 1) (hb : b ∈ Icc (0 : ℝ) 1) :
    |(aff (baseCorner q) (edir q) a b).1 - (aff (baseCorner q') (edir q') a b).1|
      ≤ rc + Real.sqrt 2 * rt ∧
    |(aff (baseCorner q) (edir q) a b).2 - (aff (baseCorner q') (edir q') a b).2|
      ≤ rc + Real.sqrt 2 * rt := by
  have hrt : 0 ≤ rt := le_trans (abs_nonneg _) ht
  have hΔt : (q.t - q'.t) ^ 2 ≤ rt ^ 2 := by
    nlinarith [sq_abs (q.t - q'.t), abs_nonneg (q.t - q'.t)]
  have hXY : (cosT q.t - cosT q'.t) ^ 2 + (sinT q.t - sinT q'.t) ^ 2 ≤ 4 * rt ^ 2 := by
    nlinarith [cossinT_dist_sq_le q.t q'.t]
  constructor
  · have hxeq : (aff (baseCorner q) (edir q) a b).1 - (aff (baseCorner q') (edir q') a b).1
        = (q.cx - q'.cx) + ((a - 1 / 2) * (cosT q.t - cosT q'.t)
            + (1 / 2 - b) * (sinT q.t - sinT q'.t)) := by
      simp only [aff, baseCorner, edir]
      ring
    have hAB : (a - 1 / 2) ^ 2 + (1 / 2 - b) ^ 2 ≤ 1 / 2 := by
      nlinarith [ha.1, ha.2, hb.1, hb.2]
    have hcs := cs_bound hrt hXY hAB
    calc |(aff (baseCorner q) (edir q) a b).1 - (aff (baseCorner q') (edir q') a b).1|
        ≤ |q.cx - q'.cx| + |(a - 1 / 2) * (cosT q.t - cosT q'.t)
            + (1 / 2 - b) * (sinT q.t - sinT q'.t)| := by rw [hxeq]; exact abs_add_le _ _
      _ ≤ rc + Real.sqrt 2 * rt := add_le_add hcx hcs
  · have hyeq : (aff (baseCorner q) (edir q) a b).2 - (aff (baseCorner q') (edir q') a b).2
        = (q.cy - q'.cy) + ((b - 1 / 2) * (cosT q.t - cosT q'.t)
            + (a - 1 / 2) * (sinT q.t - sinT q'.t)) := by
      simp only [aff, baseCorner, edir]
      ring
    have hAB : (b - 1 / 2) ^ 2 + (a - 1 / 2) ^ 2 ≤ 1 / 2 := by
      nlinarith [ha.1, ha.2, hb.1, hb.2]
    have hcs := cs_bound hrt hXY hAB
    calc |(aff (baseCorner q) (edir q) a b).2 - (aff (baseCorner q') (edir q') a b).2|
        ≤ |q.cy - q'.cy| + |(b - 1 / 2) * (cosT q.t - cosT q'.t)
            + (a - 1 / 2) * (sinT q.t - sinT q'.t)| := by rw [hyeq]; exact abs_add_le _ _
      _ ≤ rc + Real.sqrt 2 * rt := add_le_add hcy hcs

/-! ## X.3: the rBasin gates -/

/-- `√2 < 22/15` (the gate threshold: `(3/2000)·(1 + 22/15) = 37/10000` exactly). -/
theorem sqrt_two_lt : Real.sqrt 2 < 22 / 15 := by
  nlinarith [Real.sq_sqrt (show (0 : ℝ) ≤ 2 by norm_num), Real.sqrt_nonneg 2]

/-- **X.3(a), tilt gate**: a `t`-deviation ≤ `rBasin = 3/2000` gives a θ-deviation
`≤ 2·rBasin ≤ h_A36 = 37/10000` (compose with `theta_lipschitz`). -/
theorem gate_tilt : 2 * (3 / 2000 : ℝ) ≤ 37 / 10000 := by norm_num

/-- **X.3(b), slab gate** (the binding one): `rBasin·(1+√2) < h_A36 = 37/10000`. -/
theorem gate_slab : (3 / 2000 : ℝ) * (1 + Real.sqrt 2) < 37 / 10000 := by
  nlinarith [sqrt_two_lt]

/-- X.2 + X.3(b) composed: inside the `rBasin`-box (∞-norm, all of `cx, cy, t`) every
corner coordinate moves by less than A36's box radius `37/10000`. -/
theorem corner_perturb_rBasin {q q' : PSq}
    (hcx : |q.cx - q'.cx| ≤ 3 / 2000) (hcy : |q.cy - q'.cy| ≤ 3 / 2000)
    (ht : |q.t - q'.t| ≤ 3 / 2000)
    {a b : ℝ} (ha : a ∈ Icc (0 : ℝ) 1) (hb : b ∈ Icc (0 : ℝ) 1) :
    |(aff (baseCorner q) (edir q) a b).1 - (aff (baseCorner q') (edir q') a b).1| <
      37 / 10000 ∧
    |(aff (baseCorner q) (edir q) a b).2 - (aff (baseCorner q') (edir q') a b).2| <
      37 / 10000 := by
  obtain ⟨h1, h2⟩ := corner_perturb hcx hcy ht ha hb
  have hg := gate_slab
  constructor <;> nlinarith [Real.sqrt_nonneg 2]

end

end S11
end PackingCert
