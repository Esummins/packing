import PackingCertMathlib.RigidBasinMain
import PackingCertMathlib.RigidityCheck

/-!
# Rigidity: `ẑ`, its feasibility, and the basin theorem in the `t`-frame (A79)

The certificate replays (`RigidityCheck.lean`, `native_decide`) composed with the
soundness theorems:

* `zhatCfg : Fin 11 → PSq` — Trump's configuration, DEFINED as the unique zero of A22's
  contact system in `box(z0, r_0)`, read in the half-angle parametrisation
  (`t = tan(θ̂/2)`), and `shatR = ŝ_A22`, its side;
* `zhatCfg_packing` — `ẑ` is a packing at its own side with all `t ∈ [0, 1]`
  (the `trump_packs_at_shatA22` obligation);
* `basin_tframe` — for every configuration within `3/2000` of `ẑ` in `(cx, cy, t)`
  (TopLevel's `InBasin`): every packing side is `≥ ŝ_A22`, and a packing at side exactly
  `ŝ_A22` is `ẑ` (the `basin` obligation, with `ŝ_A22` in place of `ŝ`).  The θ↔t transfer
  is `ThetaT.lean`'s (`theta_lipschitz`, `corner_perturb`); the slab gate is closed against
  the UNIVERSAL certificate's own radius `3689/10⁶`: `(3/2000)(1 + √2) < 3689/10⁶`
  (`slab_gate_universal`), sharper than the `37/10000` gate of `TopLevel.lean`, which
  stays untouched.
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set

/-! ## The objects -/

theorem hcA22 : checkA22 Data.a22 = true := checkA22_a22

theorem hcA36U : checkA36 Data.a22 Data.a36_UNIVERSAL = true := checkA36_universal

/-- The contact solution, as a 34-vector. -/
noncomputable def zhatVec : Vec := zhatV Data.a22 hcA22

/-- Trump's configuration in the half-angle parametrisation. -/
noncomputable def zhatCfg : Fin 11 → PSq := fun i => sqZ zhatVec i

/-- `ŝ_A22`, the side of the contact solution. -/
noncomputable def shatR : ℝ := sZ zhatVec

theorem zhatVec_feas : Feas zhatVec := zhatV_feas hcA22

theorem zhatVec_tilt (i : ℕ) (hi : i < 11) : 0 ≤ thZ zhatVec i ∧ thZ zhatVec i ≤ 1 :=
  ⟨zhatV_tilt_nonneg hcA22 hi, (abs_le.mp (zhatV_smallTilt hcA22 i hi)).2⟩

theorem tan_half_mem_Icc {θ : ℝ} (h0 : 0 ≤ θ) (h1 : θ ≤ 1) : Real.tan (θ / 2) ∈ Icc (0 : ℝ) 1 := by
  have hpi := Real.pi_gt_three
  constructor
  · exact Real.tan_nonneg_of_nonneg_of_le_pi_div_two (by linarith) (by linarith)
  · have : Real.tan (θ / 2) < Real.tan (Real.pi / 4) :=
      Real.tan_lt_tan_of_lt_of_lt_pi_div_two (by linarith) (by linarith) (by linarith)
    rw [Real.tan_pi_div_four] at this
    exact this.le

/-- **`ẑ` is a packing at its own side, with all half-angle parameters in `[0, 1]`.** -/
theorem zhatCfg_packing :
    (∀ i, (zhatCfg i).t ∈ Icc (0 : ℝ) 1) ∧ IsPacking 11 shatR fun i => (zhatCfg i).set := by
  refine ⟨fun i => ?_, zhatVec_feas⟩
  obtain ⟨h0, h1⟩ := zhatVec_tilt i i.isLt
  exact tan_half_mem_Icc h0 h1

/-! ## The `t`-frame configuration vector -/

/-- The θ-frame vector of a `t`-frame configuration at side `s`. -/
noncomputable def mkVec (z : Fin 11 → PSq) (s : ℝ) : Vec := fun k =>
  if h : k.val < 33 then
    (if k.val % 3 = 0 then (z ⟨k.val / 3, by omega⟩).cx
      else if k.val % 3 = 1 then (z ⟨k.val / 3, by omega⟩).cy
      else thetaOf (z ⟨k.val / 3, by omega⟩).t)
  else s

theorem mkVec_cx (z : Fin 11 → PSq) (s : ℝ) (i : Fin 11) : cxZ (mkVec z s) i = (z i).cx := by
  have hi := i.isLt
  simp only [cxZ, getV, mkVec, NV]
  rw [dif_pos (by omega), dif_pos (by omega)]
  have h1 : 3 * (i : ℕ) % 3 = 0 := by omega
  have h2 : 3 * (i : ℕ) / 3 = i := by omega
  simp [h1, h2]

theorem mkVec_cy (z : Fin 11 → PSq) (s : ℝ) (i : Fin 11) : cyZ (mkVec z s) i = (z i).cy := by
  have hi := i.isLt
  simp only [cyZ, getV, mkVec, NV]
  rw [dif_pos (by omega), dif_pos (by omega)]
  have h1 : (3 * (i : ℕ) + 1) % 3 = 1 := by omega
  have h2 : (3 * (i : ℕ) + 1) / 3 = i := by omega
  simp [h1, h2]

theorem mkVec_th (z : Fin 11 → PSq) (s : ℝ) (i : Fin 11) : thZ (mkVec z s) i = thetaOf (z i).t := by
  have hi := i.isLt
  simp only [thZ, getV, mkVec, NV]
  rw [dif_pos (by omega), dif_pos (by omega)]
  have h1 : (3 * (i : ℕ) + 2) % 3 = 2 := by omega
  have h2 : (3 * (i : ℕ) + 2) / 3 = i := by omega
  simp [h1, h2]

theorem mkVec_s (z : Fin 11 → PSq) (s : ℝ) : sZ (mkVec z s) = s := by
  simp [sZ, getV, mkVec, S_IDX, NV]

theorem tan_thetaOf_half (t : ℝ) : Real.tan (thetaOf t / 2) = t := by
  unfold thetaOf
  rw [show 2 * Real.arctan t / 2 = Real.arctan t by ring, Real.tan_arctan]

theorem sqZ_mkVec (z : Fin 11 → PSq) (s : ℝ) (i : Fin 11) : sqZ (mkVec z s) i = z i := by
  simp only [sqZ, mkVec_cx, mkVec_cy, mkVec_th, tan_thetaOf_half]

theorem feas_mkVec {z : Fin 11 → PSq} {s : ℝ} (h : IsPacking 11 s fun i => (z i).set) :
    Feas (mkVec z s) := by
  unfold Feas
  rw [mkVec_s]
  have : (fun i : Fin 11 => (sqZ (mkVec z s) i).set) = fun i => (z i).set := by
    funext i; rw [sqZ_mkVec]
  rw [this]
  exact h

/-! ## The slab gate against the universal certificate -/

theorem sqrt_two_lt_1459 : Real.sqrt 2 < 1459 / 1000 := by
  rw [Real.sqrt_lt' (by norm_num)]
  norm_num

theorem hU : Data.a36_UNIVERSAL.h = 3689 / 1000000 := rfl

/-- `(3/2000)(1 + √2) ≤ h_UNIVERSAL = 3689/10⁶` (numerically `0.0036213 < 0.003689`). -/
theorem slab_gate_universal : (3 / 2000 : ℝ) * (1 + Real.sqrt 2) ≤ ((Data.a36_UNIVERSAL.h : ℚ) : ℝ) := by
  rw [hU]
  push_cast
  nlinarith [sqrt_two_lt_1459]

theorem tilt_gate_universal : (2 : ℝ) * (3 / 2000) ≤ ((Data.a36_UNIVERSAL.h : ℚ) : ℝ) := by
  rw [hU]; push_cast; norm_num

theorem rBasin_le_hU : (3 / 2000 : ℝ) ≤ ((Data.a36_UNIVERSAL.h : ℚ) : ℝ) := by
  rw [hU]; push_cast; norm_num

/-- The `InBasin` hypothesis of `TopLevel.lean`, spelled out. -/
def NearZhat (z : Fin 11 → PSq) : Prop := ∀ i,
  |(z i).cx - (zhatCfg i).cx| ≤ 3 / 2000 ∧ |(z i).cy - (zhatCfg i).cy| ≤ 3 / 2000 ∧
    |(z i).t - (zhatCfg i).t| ≤ 3 / 2000

theorem thetaOf_zhat (i : Fin 11) : thetaOf (zhatCfg i).t = thZ zhatVec i := by
  simp only [zhatCfg, sqZ]
  exact thetaOf_tan_half (zhatV_tilt_lt_pi hcA22 i.isLt)

/-- The θ-frame vector of a near configuration lies in the universal certificate's box,
provided the side does. -/
theorem inBoxZ_mkVec {z : Fin 11 → PSq} (hz : NearZhat z) {s : ℝ}
    (hs : |s - shatR| ≤ ((Data.a36_UNIVERSAL.h : ℚ) : ℝ)) :
    InBoxZ zhatVec Data.a36_UNIVERSAL.h (mkVec z s) := by
  intro k
  set h : ℝ := ((Data.a36_UNIVERSAL.h : ℚ) : ℝ) with hh
  have hr := rBasin_le_hU
  have ht := tilt_gate_universal
  by_cases hk : k.val < 33
  · set i : Fin 11 := ⟨k.val / 3, by omega⟩ with hi
    obtain ⟨hx, hy, htt⟩ := hz i
    have hcx : (zhatCfg i).cx = cxZ zhatVec i := rfl
    have hcy : (zhatCfg i).cy = cyZ zhatVec i := rfl
    -- identify the coordinate
    rcases Nat.lt_or_ge (k.val % 3) 1 with h0 | h0
    · have h0' : k.val % 3 = 0 := by omega
      have hk' : k.val = 3 * (i : ℕ) := by simp only [hi]; omega
      have e1 : mkVec z s k = (z i).cx := by
        simp only [mkVec, dif_pos hk, h0', if_true]
        rfl
      have e2 : zhatVec k = cxZ zhatVec i := by
        simp only [cxZ, getV, dif_pos (show 3 * (i : ℕ) < NV by simp [NV]; omega)]
        congr 1; exact Fin.ext hk'
      rw [e1, e2, ← hcx]; linarith
    rcases Nat.lt_or_ge (k.val % 3) 2 with h1 | h1
    · have h1' : k.val % 3 = 1 := by omega
      have hk' : k.val = 3 * (i : ℕ) + 1 := by simp only [hi]; omega
      have e1 : mkVec z s k = (z i).cy := by
        simp only [mkVec, dif_pos hk, h1']
        simp only [Nat.one_ne_zero, if_false, if_true]
        rfl
      have e2 : zhatVec k = cyZ zhatVec i := by
        simp only [cyZ, getV, dif_pos (show 3 * (i : ℕ) + 1 < NV by simp [NV]; omega)]
        congr 1; exact Fin.ext hk'
      rw [e1, e2, ← hcy]; linarith
    · have h2' : k.val % 3 = 2 := by omega
      have hk' : k.val = 3 * (i : ℕ) + 2 := by simp only [hi]; omega
      have e1 : mkVec z s k = thetaOf (z i).t := by
        simp only [mkVec, dif_pos hk, h2']
        simp only [OfNat.ofNat_ne_zero, OfNat.ofNat_ne_one, if_false]
        rfl
      have e2 : zhatVec k = thZ zhatVec i := by
        simp only [thZ, getV, dif_pos (show 3 * (i : ℕ) + 2 < NV by simp [NV]; omega)]
        congr 1; exact Fin.ext hk'
      rw [e1, e2, ← thetaOf_zhat]
      have := theta_lipschitz (z i).t (zhatCfg i).t
      linarith
  · have hk' : k.val = 33 := by have := k.isLt; simp only [NV] at this; omega
    have e1 : mkVec z s k = s := by simp only [mkVec, dif_neg hk]
    have e2 : zhatVec k = shatR := by
      simp only [shatR, sZ, getV, S_IDX, dif_pos (show 33 < NV by decide)]
      congr 1; exact Fin.ext hk'
    rw [e1, e2]; exact hs

/-- A corner of `ẑ` lies on a far wall; after a `3/2000` perturbation the container side
is at least `ŝ − (3/2000)(1 + √2)`. -/
theorem side_lower_bound {z : Fin 11 → PSq} (hz : NearZhat z) {s : ℝ}
    (hp : IsPacking 11 s fun i => (z i).set) :
    shatR - (3 / 2000 : ℝ) * (1 + Real.sqrt 2) ≤ s := by
  show sZ zhatVec - (3 / 2000 : ℝ) * (1 + Real.sqrt 2) ≤ s
  obtain ⟨-, -, -, -, -, -, -, -, hfw⟩ := checkA36_parts hcA36U
  simp only [farWallOK, Array.any_eq_true] at hfw
  obtain ⟨idx, hidx, hrow⟩ := hfw
  obtain ⟨hsh, -⟩ := checkA22_parts hcA22
  obtain ⟨-, hS, -, -, -, hSr, hrows, -⟩ := shapeOK_parts hsh
  have hzero : eval zhatVec (rowExpr (Data.a22.row Data.a22.S[idx])) = 0 :=
    row_zero_of_mem (zhatV_zero hcA22) hS (Array.getElem_mem hidx)
  have hmem : Data.a22.row Data.a22.S[idx] ∈ Data.a22.rows := by
    have hk := hSr _ (Array.getElem_mem hidx)
    unfold A22Cert.row; rw [getD_of_lt _ hk]; exact Array.getElem_mem hk
  have hshape := hrows _ hmem
  rcases hR : Data.a22.row Data.a22.S[idx] with ⟨i, k, w⟩ | _ | _ | _
  · rw [hR] at hrow hzero hshape
    simp only [Bool.or_eq_true, decide_eq_true_eq] at hrow
    have hs' : i < 11 ∧ k < 4 ∧ w < 4 := hshape
    obtain ⟨hi, hk, -⟩ := hs'
    rw [eval_wall] at hzero
    -- the corner of `ẑ` as an `aff` point
    have hθ := zhatV_tilt_lt_pi hcA22 hi
    obtain ⟨c0, c1, c2, c3⟩ := cornerP_eq_aff (z := zhatVec) hθ
    obtain ⟨hcx, hcy, ht⟩ := hz ⟨i, hi⟩
    have hzi : zhatCfg ⟨i, hi⟩ = sqZ zhatVec i := rfl
    -- pick the parameters `(a, b)` of corner `k`
    have hab : ∃ a b : ℝ, a ∈ Icc (0 : ℝ) 1 ∧ b ∈ Icc (0 : ℝ) 1 ∧
        cornerP zhatVec i k = aff (baseCorner (sqZ zhatVec i)) (edir (sqZ zhatVec i)) a b := by
      interval_cases k
      · exact ⟨0, 0, ⟨le_rfl, zero_le_one⟩, ⟨le_rfl, zero_le_one⟩, c0⟩
      · exact ⟨1, 0, ⟨zero_le_one, le_rfl⟩, ⟨le_rfl, zero_le_one⟩, c1⟩
      · exact ⟨1, 1, ⟨zero_le_one, le_rfl⟩, ⟨zero_le_one, le_rfl⟩, c2⟩
      · exact ⟨0, 1, ⟨le_rfl, zero_le_one⟩, ⟨zero_le_one, le_rfl⟩, c3⟩
    obtain ⟨a, b, ha, hb, hcorner⟩ := hab
    have hpert := corner_perturb (q := z ⟨i, hi⟩) (q' := sqZ zhatVec i) (rc := 3 / 2000) (rt := 3 / 2000)
      (by rw [← hzi]; exact hcx) (by rw [← hzi]; exact hcy) (by rw [← hzi]; exact ht) ha hb
    -- the perturbed corner is inside the container
    have hin : aff (baseCorner (z ⟨i, hi⟩)) (edir (z ⟨i, hi⟩)) a b ∈ (z ⟨i, hi⟩).set :=
      ⟨a, b, ha.1, ha.2, hb.1, hb.2, rfl⟩
    have hcont := hp.contained ⟨i, hi⟩ hin
    simp only [container, mem_prod, mem_Icc] at hcont
    rcases hrow with rfl | rfl
    · -- wall `x = s`: `ŝ − corner.x = 0`
      norm_num at hzero
      rw [hcorner] at hzero
      have := (abs_le.mp hpert.1).1
      linarith [hcont.1.2]
    · norm_num at hzero
      rw [hcorner] at hzero
      have := (abs_le.mp hpert.2).1
      linarith [hcont.2.2]
  · rw [hR] at hrow; exact absurd hrow Bool.false_ne_true
  · rw [hR] at hrow; exact absurd hrow Bool.false_ne_true
  · rw [hR] at hrow; exact absurd hrow Bool.false_ne_true

/-! ## The basin theorem in the `t`-frame -/

/-- **The basin theorem** (the `basin` obligation of `TopLevel.lean`, with `ŝ_A22`). -/
theorem basin_tframe (z : Fin 11 → PSq) (hz : NearZhat z) :
    (∀ s : ℝ, ((∀ i, (z i).t ∈ Icc (0 : ℝ) 1) ∧ IsPacking 11 s fun i => (z i).set) → shatR ≤ s) ∧
    (((∀ i, (z i).t ∈ Icc (0 : ℝ) 1) ∧ IsPacking 11 shatR fun i => (z i).set) → z = zhatCfg) := by
  have hg := slab_gate_universal
  constructor
  · rintro s ⟨-, hp⟩
    by_contra hlt
    push_neg at hlt
    have hlow := side_lower_bound hz hp
    have hs : |s - shatR| ≤ ((Data.a36_UNIVERSAL.h : ℚ) : ℝ) := by
      rw [abs_le]; constructor <;> linarith
    have := (a36_basin hcA22 hcA36U rfl (inBoxZ_mkVec hz hs) (feas_mkVec hp)).1
    rw [mkVec_s] at this
    exact absurd this (not_le.mpr hlt)
  · rintro ⟨-, hp⟩
    have hs : |shatR - shatR| ≤ ((Data.a36_UNIVERSAL.h : ℚ) : ℝ) := by
      simp only [sub_self, abs_zero]; exact le_trans (by norm_num) rBasin_le_hU
    have := (a36_basin hcA22 hcA36U rfl (inBoxZ_mkVec hz hs) (feas_mkVec hp)).2 (mkVec_s z shatR)
    funext i
    rw [← sqZ_mkVec z shatR i, this]
    rfl

end PackingCert.Rigid
