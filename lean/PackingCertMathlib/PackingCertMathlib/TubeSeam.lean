import PackingCertMathlib.Rigidity
import PackingCertMathlib.RigidTube

/-!
# The tube in the `t`-frame and Lemma SEAM's per-coordinate map (A86 T1, consumer side)

`docs/proofs/contraction_tube.md` §4.1 / `docs/proofs/protected_trees.md` Step 4.

* `tube_tframe` — for a configuration `z` (`Fin 11 → PSq`) that is a packing at side `m`
  and whose θ-frame vector `mkVec z m` lies in a certified tube around `ẑ`:
  `m ≥ ŝ_A22`, and `m = ŝ_A22` forces `z = ẑ` (the D.SLAB-facing form of Theorem T1);
* `inTube_mkVec` — per-coordinate membership: `|cx − (ĉx − t·v)| ≤ r_c`, same for `cy`,
  `|θ(t_i) − θ̂_i| ≤ r_θ`, `|m − (ŝ − t)| ≤ r_s`;
* `seam_inTube` — **Lemma SEAM's map**: a packing at side `m ∈ [ŝ − T, ŝ]` whose PINS
  (a set `I` of squares) sit exactly at their side-`m` slots `α + β·m` and whose FREE
  squares, after the dilation `Δ_λ` (`λ = s0/m`) to the tree side `s0`, land within
  `r_land` of the `λ₀`-dilated `ẑ` (`λ₀ = s0/ŝ`) with tilts within `r_θ`, lies in the tube
  with direction `v = β` on the pins and `v = ẑ/ŝ` on the free squares, at depth
  `t = ŝ − m` exactly — pins contribute `w = 0` up to the slot residual of `ẑ`, free
  squares `|w| ≤ r_land·(m/s0) + T·|v − ẑ/ŝ|`;
* `vfree_bound` / `pin_slot_bound` — the two "certificate-data" residuals (`ẑ` vs the
  rational centre `z0` of the A22 certificate), derived from `‖ẑ − z0‖_∞ ≤ r0`.
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set

/-- The direction's `x`- and `y`-components on square `i`. -/
noncomputable def vcx (tc : TubeCert) (i : ℕ) : ℝ := ((tc.vi (3 * i) : ℚ) : ℝ)

noncomputable def vcy (tc : TubeCert) (i : ℕ) : ℝ := ((tc.vi (3 * i + 1) : ℚ) : ℝ)

theorem rad_cx (tc : TubeCert) (i : ℕ) (hi : i < 11) : tc.rad (3 * i) = tc.rC := by
  unfold TubeCert.rad
  rw [if_neg (by unfold S_IDX; omega), if_neg (by omega)]

theorem rad_cy (tc : TubeCert) (i : ℕ) (hi : i < 11) : tc.rad (3 * i + 1) = tc.rC := by
  unfold TubeCert.rad
  rw [if_neg (by unfold S_IDX; omega), if_neg (by omega)]

theorem rad_th (tc : TubeCert) (i : ℕ) (hi : i < 11) : tc.rad (3 * i + 2) = tc.rT := by
  unfold TubeCert.rad
  rw [if_neg (by unfold S_IDX; omega), if_pos (by omega)]

/-- **The tube theorem, `t`-frame**: a packing at side `m` inside the tube has `m ≥ ŝ_A22`,
and `m = ŝ_A22` only for `ẑ` itself. -/
theorem tube_tframe {tc : TubeCert} (ht : checkTube Data.a22 tc = true) (z : Fin 11 → PSq) (m : ℝ)
    (hz : InTube zhatVec (vR tc) tc.T (radR tc) (mkVec z m))
    (hP : IsPacking 11 m fun i => (z i).set) :
    shatR ≤ m ∧ (m = shatR → z = zhatCfg) := by
  have h := tube_basin hcA22 ht hz (feas_mkVec hP)
  rw [mkVec_s] at h
  refine ⟨h.1, fun hm => ?_⟩
  have := h.2 hm
  funext i
  rw [← sqZ_mkVec z m i, this]
  rfl

/-- Per-coordinate tube membership of a `t`-frame configuration. -/
theorem inTube_mkVec {tc : TubeCert} (hsh : tubeShapeOK tc = true) {z : Fin 11 → PSq} {m t : ℝ}
    (ht0 : 0 ≤ t) (htT : t ≤ (tc.T : ℝ)) (hs : |m - (shatR - t)| ≤ (tc.rS : ℝ))
    (hc : ∀ i : Fin 11,
      |(z i).cx - (cxZ zhatVec i - t * vcx tc i)| ≤ (tc.rC : ℝ) ∧
      |(z i).cy - (cyZ zhatVec i - t * vcy tc i)| ≤ (tc.rC : ℝ) ∧
      |thetaOf (z i).t - thZ zhatVec i| ≤ (tc.rT : ℝ)) :
    InTube zhatVec (vR tc) tc.T (radR tc) (mkVec z m) := by
  obtain ⟨-, -, -, -, -, -, hvth, -⟩ := tubeShape_parts hsh
  refine ⟨t, ht0, htT, fun k => ?_⟩
  by_cases hk : k.val < 33
  · set i : Fin 11 := ⟨k.val / 3, by omega⟩ with hi
    obtain ⟨hx, hy, htt⟩ := hc i
    rcases Nat.lt_or_ge (k.val % 3) 1 with h0 | h0
    · have h0' : k.val % 3 = 0 := by omega
      have hk' : k.val = 3 * (i : ℕ) := by simp only [hi]; omega
      have e1 : mkVec z m k = (z i).cx := by
        simp only [mkVec, dif_pos hk, h0', if_true]
        rfl
      have e2 : zhatVec k = cxZ zhatVec i := by
        simp only [cxZ, getV, dif_pos (show 3 * (i : ℕ) < NV by simp [NV]; omega)]
        congr 1; exact Fin.ext hk'
      have e3 : vR tc k = vcx tc i := by
        simp only [vR, vcx]; rw [hk']
      have e4 : radR tc k = (tc.rC : ℝ) := by
        simp only [radR]; rw [hk', rad_cx tc i i.isLt]
      rw [e1, e2, e3, e4]; exact hx
    rcases Nat.lt_or_ge (k.val % 3) 2 with h1 | h1
    · have h1' : k.val % 3 = 1 := by omega
      have hk' : k.val = 3 * (i : ℕ) + 1 := by simp only [hi]; omega
      have e1 : mkVec z m k = (z i).cy := by
        simp only [mkVec, dif_pos hk, h1']
        simp only [Nat.one_ne_zero, if_false, if_true]
        rfl
      have e2 : zhatVec k = cyZ zhatVec i := by
        simp only [cyZ, getV, dif_pos (show 3 * (i : ℕ) + 1 < NV by simp [NV]; omega)]
        congr 1; exact Fin.ext hk'
      have e3 : vR tc k = vcy tc i := by
        simp only [vR, vcy]; rw [hk']
      have e4 : radR tc k = (tc.rC : ℝ) := by
        simp only [radR]; rw [hk', rad_cy tc i i.isLt]
      rw [e1, e2, e3, e4]; exact hy
    · have h2' : k.val % 3 = 2 := by omega
      have hk' : k.val = 3 * (i : ℕ) + 2 := by simp only [hi]; omega
      have e1 : mkVec z m k = thetaOf (z i).t := by
        simp only [mkVec, dif_pos hk, h2']
        simp only [OfNat.ofNat_ne_zero, OfNat.ofNat_ne_one, if_false]
        rfl
      have e2 : zhatVec k = thZ zhatVec i := by
        simp only [thZ, getV, dif_pos (show 3 * (i : ℕ) + 2 < NV by simp [NV]; omega)]
        congr 1; exact Fin.ext hk'
      have e3 : vR tc k = 0 := by
        simp only [vR]; rw [hk']
        have := hvth i i.isLt
        rw [this]; simp
      have e4 : radR tc k = (tc.rT : ℝ) := by
        simp only [radR]; rw [hk', rad_th tc i i.isLt]
      rw [e1, e2, e3, e4, mul_zero, sub_zero]; exact htt
  · have hk' : k.val = 33 := by have := k.isLt; simp only [NV] at this; omega
    have e1 : mkVec z m k = m := by simp only [mkVec, dif_neg hk]
    have e2 : zhatVec k = shatR := by
      simp only [shatR, sZ, getV, S_IDX, dif_pos (show 33 < NV by decide)]
      congr 1; exact Fin.ext hk'
    have e3 : vR tc k = 1 := by
      simp only [vR]; rw [hk']
      have := (tubeShape_parts hsh).2.2.2.2.2.1
      rw [show (33 : ℕ) = S_IDX from rfl, this]; simp
    have e4 : radR tc k = (tc.rS : ℝ) := by
      simp only [radR]; rw [hk']
      rw [show (33 : ℕ) = S_IDX from rfl, rad_S]
    rw [e1, e2, e3, e4, mul_one]; exact hs

/-- **Lemma SEAM's per-coordinate map.**  `I` = the pinned squares (slots `α + β·m`,
axis-aligned, `t = 0`), the rest free; `λ = s0/m`, `λ₀ = s0/ŝ`. -/
theorem seam_inTube {tc : TubeCert} (hsh : tubeShapeOK tc = true) {s0 m : ℝ} (hm0 : 0 < m)
    (hms0 : m ≤ s0) (hmT : shatR - m ≤ (tc.T : ℝ)) (hmshat : m ≤ shatR) (hshat0 : 0 < shatR)
    {P : Fin 11 → PSq} (I : Finset (Fin 11)) (αx βx αy βy : Fin 11 → ℝ)
    (hpin : ∀ i ∈ I, (P i).cx = αx i + βx i * m ∧ (P i).cy = αy i + βy i * m ∧ (P i).t = 0)
    (hslot : ∀ i ∈ I, |cxZ zhatVec i - (αx i + βx i * shatR)| ≤ (tc.rC : ℝ) ∧
      |cyZ zhatVec i - (αy i + βy i * shatR)| ≤ (tc.rC : ℝ) ∧ |thZ zhatVec i| ≤ (tc.rT : ℝ))
    (hvpin : ∀ i ∈ I, vcx tc i = βx i ∧ vcy tc i = βy i)
    {rland εv : ℝ} (hrland : 0 ≤ rland) (hεv : 0 ≤ εv)
    (hfree : ∀ i ∉ I,
      |(scaleC (s0 / m) (P i)).cx - (s0 / shatR) * cxZ zhatVec i| ≤ rland ∧
      |(scaleC (s0 / m) (P i)).cy - (s0 / shatR) * cyZ zhatVec i| ≤ rland ∧
      |thetaOf (P i).t - thZ zhatVec i| ≤ (tc.rT : ℝ))
    (hvfree : ∀ i ∉ I, |vcx tc i - cxZ zhatVec i / shatR| ≤ εv ∧
      |vcy tc i - cyZ zhatVec i / shatR| ≤ εv)
    (hbudget : rland + (tc.T : ℝ) * εv ≤ (tc.rC : ℝ)) :
    InTube zhatVec (vR tc) tc.T (radR tc) (mkVec P m) := by
  obtain ⟨hT0, -, -, hrS0, -⟩ := tubeShape_parts hsh
  have hT0' : (0 : ℝ) ≤ tc.T := by exact_mod_cast hT0
  have hrS0' : (0 : ℝ) ≤ tc.rS := by exact_mod_cast hrS0
  set t : ℝ := shatR - m with htdef
  have ht0 : 0 ≤ t := by linarith
  refine inTube_mkVec hsh ht0 hmT (by simp only [htdef, sub_sub_cancel, sub_self, abs_zero]; exact hrS0') fun i => ?_
  have hs0 : 0 < s0 := lt_of_lt_of_le hm0 hms0
  by_cases hi : i ∈ I
  · obtain ⟨hx, hy, ht⟩ := hpin i hi
    obtain ⟨sx, sy, sth⟩ := hslot i hi
    obtain ⟨vx, vy⟩ := hvpin i hi
    refine ⟨?_, ?_, ?_⟩
    · rw [hx, vx]
      have e : αx i + βx i * m - (cxZ zhatVec i - t * βx i) = -(cxZ zhatVec i - (αx i + βx i * shatR)) := by
        simp only [htdef]; ring
      rw [e, abs_neg]; exact sx
    · rw [hy, vy]
      have e : αy i + βy i * m - (cyZ zhatVec i - t * βy i) = -(cyZ zhatVec i - (αy i + βy i * shatR)) := by
        simp only [htdef]; ring
      rw [e, abs_neg]; exact sy
    · rw [ht]
      have : thetaOf 0 = 0 := by simp [thetaOf]
      rw [this, zero_sub, abs_neg]; exact sth
  · obtain ⟨fx, fy, fth⟩ := hfree i hi
    obtain ⟨vx, vy⟩ := hvfree i hi
    have hlam : (0 : ℝ) < s0 / m := div_pos hs0 hm0
    have hms : m / s0 ≤ 1 := by rw [div_le_one hs0]; exact hms0
    have hms' : 0 ≤ m / s0 := div_nonneg hm0.le hs0.le
    -- `(P i).cx = (F i).cx · (m / s0)`
    have ex : (P i).cx = (scaleC (s0 / m) (P i)).cx * (m / s0) := by
      simp only [scaleC]; field_simp
    have ey : (P i).cy = (scaleC (s0 / m) (P i)).cy * (m / s0) := by
      simp only [scaleC]; field_simp
    refine ⟨?_, ?_, fth⟩
    · rw [ex]
      have key : (scaleC (s0 / m) (P i)).cx * (m / s0) - (cxZ zhatVec i - t * vcx tc i)
          = ((scaleC (s0 / m) (P i)).cx - (s0 / shatR) * cxZ zhatVec i) * (m / s0)
            + t * (vcx tc i - cxZ zhatVec i / shatR) := by
        simp only [htdef]; field_simp; ring
      rw [key]
      calc |((scaleC (s0 / m) (P i)).cx - (s0 / shatR) * cxZ zhatVec i) * (m / s0)
            + t * (vcx tc i - cxZ zhatVec i / shatR)|
          ≤ |((scaleC (s0 / m) (P i)).cx - (s0 / shatR) * cxZ zhatVec i) * (m / s0)|
            + |t * (vcx tc i - cxZ zhatVec i / shatR)| := abs_add_le _ _
        _ = |(scaleC (s0 / m) (P i)).cx - (s0 / shatR) * cxZ zhatVec i| * (m / s0)
            + t * |vcx tc i - cxZ zhatVec i / shatR| := by
            rw [abs_mul, abs_mul, abs_of_nonneg hms', abs_of_nonneg ht0]
        _ ≤ rland * 1 + (tc.T : ℝ) * εv := by
            refine add_le_add (mul_le_mul fx hms hms' hrland) (mul_le_mul hmT vx (abs_nonneg _) hT0')
        _ ≤ (tc.rC : ℝ) := by linarith
    · rw [ey]
      have key : (scaleC (s0 / m) (P i)).cy * (m / s0) - (cyZ zhatVec i - t * vcy tc i)
          = ((scaleC (s0 / m) (P i)).cy - (s0 / shatR) * cyZ zhatVec i) * (m / s0)
            + t * (vcy tc i - cyZ zhatVec i / shatR) := by
        simp only [htdef]; field_simp; ring
      rw [key]
      calc |((scaleC (s0 / m) (P i)).cy - (s0 / shatR) * cyZ zhatVec i) * (m / s0)
            + t * (vcy tc i - cyZ zhatVec i / shatR)|
          ≤ |((scaleC (s0 / m) (P i)).cy - (s0 / shatR) * cyZ zhatVec i) * (m / s0)|
            + |t * (vcy tc i - cyZ zhatVec i / shatR)| := abs_add_le _ _
        _ = |(scaleC (s0 / m) (P i)).cy - (s0 / shatR) * cyZ zhatVec i| * (m / s0)
            + t * |vcy tc i - cyZ zhatVec i / shatR| := by
            rw [abs_mul, abs_mul, abs_of_nonneg hms', abs_of_nonneg ht0]
        _ ≤ rland * 1 + (tc.T : ℝ) * εv := by
            refine add_le_add (mul_le_mul fy hms hms' hrland) (mul_le_mul hmT vy (abs_nonneg _) hT0')
        _ ≤ (tc.rC : ℝ) := by linarith

/-! ## The certificate-data residuals (`ẑ` versus the rational centre `z0`) -/

/-- `ẑ` is within `r0` of `z0` coordinatewise (`Data.a22`). -/
theorem zhatVec_near_z0 (k : Fin NV) :
    |zhatVec k - ((Data.a22.z0.getD k 0 : ℚ) : ℝ)| ≤ ((Data.a22.r0 : ℚ) : ℝ) :=
  zhatV_inBoxR hcA22 k

/-- A free-square direction component that is EXACTLY `z0_i / z0_s` (a decidable rational
identity) is within `4·r0` of `ẑ_i / ŝ`, given the crude bounds `z0_s ≥ 3`, `|z0_i| ≤ 5`,
`r0 ≤ 1/10`. -/
theorem vfree_bound {v z0i z0s r0 : ℝ} {zi zs : ℝ} (hv : v = z0i / z0s)
    (hzi : |zi - z0i| ≤ r0) (hzs : |zs - z0s| ≤ r0) (hs3 : 3 ≤ z0s) (hzi5 : |z0i| ≤ 5)
    (hr0 : r0 ≤ 1 / 10) (hr00 : 0 ≤ r0) : |v - zi / zs| ≤ 4 * r0 := by
  have hzs0 : 0 < z0s := by linarith
  have hzs' : 0 < zs := by
    have := (abs_le.mp hzs).1; linarith
  rw [hv]
  have key : z0i / z0s - zi / zs = (z0i * (zs - z0s) + z0s * (z0i - zi)) / (z0s * zs) := by
    field_simp; ring
  rw [key, abs_div, abs_of_pos (mul_pos hzs0 hzs'), div_le_iff₀ (mul_pos hzs0 hzs')]
  have h1 : |z0i * (zs - z0s)| ≤ 5 * r0 := by
    rw [abs_mul]; exact mul_le_mul hzi5 hzs (abs_nonneg _) (by norm_num)
  have h2 : |z0s * (z0i - zi)| ≤ z0s * r0 := by
    rw [abs_mul, abs_of_pos hzs0, abs_sub_comm]; exact mul_le_mul_of_nonneg_left hzi hzs0.le
  have h3 := abs_add_le (z0i * (zs - z0s)) (z0s * (z0i - zi))
  have hzs'' : 29 / 10 ≤ zs := by have := (abs_le.mp hzs).1; linarith
  nlinarith [mul_nonneg hr00 (sub_nonneg.mpr hs3)]

/-- A pin's slot residual: if the rational centre `z0_i` is within `δ` of the rational slot
`α + β·z0_s` (a decidable check) and `β ∈ {0, 1}`, then `ẑ_i` is within `δ + 2·r0` of the
real slot `α + β·ŝ`. -/
theorem pin_slot_bound {zi zs z0i z0s α β r0 δ : ℝ} (hzi : |zi - z0i| ≤ r0) (hzs : |zs - z0s| ≤ r0)
    (hβ : β = 0 ∨ β = 1) (hslot : |z0i - (α + β * z0s)| ≤ δ) :
    |zi - (α + β * zs)| ≤ δ + 2 * r0 := by
  have e : zi - (α + β * zs) = (zi - z0i) + (z0i - (α + β * z0s)) - β * (zs - z0s) := by ring
  rw [e]
  have h3 : |β * (zs - z0s)| ≤ r0 := by
    rcases hβ with h | h <;> rw [h] <;> simp <;> linarith [abs_nonneg (zs - z0s)]
  calc |(zi - z0i) + (z0i - (α + β * z0s)) - β * (zs - z0s)|
      ≤ |(zi - z0i) + (z0i - (α + β * z0s))| + |β * (zs - z0s)| := abs_sub _ _
    _ ≤ |zi - z0i| + |z0i - (α + β * z0s)| + |β * (zs - z0s)| := by
        linarith [abs_add_le (zi - z0i) (z0i - (α + β * z0s))]
    _ ≤ r0 + δ + r0 := by linarith
    _ = δ + 2 * r0 := by ring

end PackingCert.Rigid
