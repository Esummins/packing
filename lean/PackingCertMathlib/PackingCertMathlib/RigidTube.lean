import PackingCertMathlib.RigidBasinMain
import PackingCertMathlib.RigidTubeKernel

/-!
# Soundness of the contraction-tube checker (A86 T1 — A83's obligation)

`tube_basin`: `checkA22 c = true`, `checkTube c tc = true` ⟹ every feasible configuration
`z` in the tube `{ẑ − t·v + w : 0 ≤ t ≤ T, |w_i| ≤ r_i}` has `s(z) ≥ s(ẑ)`, with equality
only at `z = ẑ` (`docs/proofs/contraction_tube.md` Theorem T1, `lean/tube_obligation_A83.md`).

The proof is `a36_basin`'s (V′) chain (`RigidBasinMain.lean`) with three substitutions:

1. **boxes** — the tube is enclosed by the asymmetric hull `tubeArr` (walls) and, for every
   pair row, by the PAIR-RELATIVE box `pairArr`: edge and dist rows depend on the two
   centres only through `c_i − c_j`, for their values AND their symbolic derivatives.
   This is proved semantically: invariance of the row expressions under the simultaneous
   shift `shiftV` of a coordinate pair (closed forms of `RigidGeom.lean`), and
   `shift_inv_D` — an invariant expression has invariant symbolic derivatives, because the
   symbolic derivative IS the derivative along the coordinate segment
   (`hasDerivAt_eval`) and derivatives are unique.  The mean-value points of the chain
   lie on the segment `[ẑ, z]`, which stays in the tube (`inTube_seg`, convexity), and a
   tube point translated into the pair frame lies in the pair box (`mem_pairArr`);
2. **the split remainder** — `d = −t·v + w`, `|dᵀHd| ≤ t²q_vv + t Σ|Hv|·|w| + t Σ|vᵀH|·|w| + Σ|H||w||w|`
   with the per-coordinate bounds `t ≤ t̄(x)`, `|w_i| ≤ w̄_i(x)` (`hess_split_bound`);
3. **the monotone iteration** — `ψ` is monotone on `[0, ∞)` (all coefficients `≥ 0`,
   `t̄`, `w̄` non-decreasing), so `x ≤ ψ(x)` and `x ≤ X` give `x ≤ rup ψ^n(X)` for every `n`
   (`iterT_sound`); the checker's exit `x_n + r0 ≤ r_N` hands over to `a22_optimal'`.
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set Finset
open PackingCert.CaseI (rabs rmin rmax)

/-! ## The tube -/

/-- The direction as a real vector. -/
def vR (tc : TubeCert) : Vec := fun k => ((tc.vi k : ℚ) : ℝ)

/-- The radii as a real vector. -/
def radR (tc : TubeCert) : Vec := fun k => ((tc.rad k : ℚ) : ℝ)

/-- `z ∈ Tube_v(T, rad)` around `zh`: `z = zh − t·v + w`, `0 ≤ t ≤ T`, `|w_k| ≤ rad_k`. -/
def InTube (zh v : Vec) (T : ℝ) (rad : Vec) (z : Vec) : Prop :=
  ∃ t : ℝ, 0 ≤ t ∧ t ≤ T ∧ ∀ k, |z k - (zh k - t * v k)| ≤ rad k

section
variable {c : A22Cert} {tc : TubeCert}

theorem tubeShape_parts (h : tubeShapeOK tc = true) :
    0 ≤ tc.T ∧ 0 < tc.rC ∧ 0 < tc.rT ∧ 0 ≤ tc.rS ∧ tc.v.size = NV ∧ tc.vi S_IDX = 1 ∧
    (∀ i, i < 11 → tc.vi (3 * i + 2) = 0) ∧ ∀ k, 0 ≤ tc.vi k := by
  simp only [tubeShapeOK, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, rng_eq,
    List.mem_range, Array.all_eq_true_iff_forall_mem] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩ := h
  refine ⟨h1, h2, h3, h4, h5, h6, h7, fun k => ?_⟩
  unfold TubeCert.vi
  by_cases hk : k < tc.v.size
  · rw [getD_of_lt _ hk]; exact h8 _ (Array.getElem_mem hk)
  · rw [getD_of_ge _ hk]

theorem rad_nonneg (h : tubeShapeOK tc = true) (k : ℕ) : 0 ≤ tc.rad k := by
  obtain ⟨-, h2, h3, h4, -⟩ := tubeShape_parts h
  unfold TubeCert.rad
  split_ifs <;> linarith

theorem radR_nonneg (h : tubeShapeOK tc = true) (k : Fin NV) : 0 ≤ radR tc k := by
  unfold radR; exact_mod_cast rad_nonneg h k

theorem vR_nonneg (h : tubeShapeOK tc = true) (k : Fin NV) : 0 ≤ vR tc k := by
  unfold vR; exact_mod_cast (tubeShape_parts h).2.2.2.2.2.2.2 k

/-- `ẑ` itself lies in the tube (`t = 0`, `w = 0`). -/
theorem inTube_self (h : tubeShapeOK tc = true) (zh : Vec) :
    InTube zh (vR tc) tc.T (radR tc) zh :=
  ⟨0, le_rfl, by exact_mod_cast (tubeShape_parts h).1, fun k => by
    simp only [zero_mul, sub_zero, sub_self, abs_zero]; exact radR_nonneg h k⟩

/-- The tube is star-shaped from `ẑ`: the segment `[ẑ, z]` stays in the tube. -/
theorem inTube_seg {zh v : Vec} {T : ℝ} {rad : Vec} (_hrad : ∀ k, 0 ≤ rad k) {z : Vec}
    (hz : InTube zh v T rad z) {θ : ℝ} (h0 : 0 ≤ θ) (h1 : θ ≤ 1) :
    InTube zh v T rad (seg zh (fun i => z i - zh i) θ) := by
  obtain ⟨t, ht0, htT, hw⟩ := hz
  refine ⟨θ * t, by positivity, by nlinarith, fun k => ?_⟩
  simp only [seg]
  have e : zh k + θ * (z k - zh k) - (zh k - θ * t * v k) = θ * (z k - (zh k - t * v k)) := by ring
  rw [e, abs_mul, abs_of_nonneg h0]
  nlinarith [abs_nonneg (z k - (zh k - t * v k)), _hrad k, hw k]

/-! ## The hull box -/

theorem tubeArr_size (c : A22Cert) (tc : TubeCert) : (tubeArr c tc).size = NV := by
  simp [tubeArr]

theorem tubeArr_getD (c : A22Cert) (tc : TubeCert) (k : Fin NV) :
    (tubeArr c tc).getD k IV.zero =
      IV.mkR (c.z0.getD k 0 - tc.T * rmax (tc.vi k) 0 - tc.rad k - c.r0)
        (c.z0.getD k 0 + tc.T * rmax (-(tc.vi k)) 0 + tc.rad k + c.r0) := by
  unfold tubeArr
  rw [getD_of_lt _ (by simp), Array.getElem_ofFn]

theorem tv_le_Tmax (h : tubeShapeOK tc = true) {t : ℝ} (ht0 : 0 ≤ t) (htT : t ≤ (tc.T : ℝ))
    (k : Fin NV) : t * vR tc k ≤ (tc.T : ℝ) * ((rmax (tc.vi k) 0 : ℚ) : ℝ) := by
  rw [rmax_cast]; push_cast
  have hv := vR_nonneg h k
  unfold vR at hv ⊢
  calc t * ((tc.vi k : ℚ) : ℝ) ≤ (tc.T : ℝ) * ((tc.vi k : ℚ) : ℝ) :=
        mul_le_mul_of_nonneg_right htT hv
    _ ≤ (tc.T : ℝ) * max ((tc.vi k : ℚ) : ℝ) 0 :=
        mul_le_mul_of_nonneg_left (le_max_left _ _) (by linarith)

theorem tv_nonneg (h : tubeShapeOK tc = true) {t : ℝ} (ht0 : 0 ≤ t) (k : Fin NV) :
    0 ≤ t * vR tc k := mul_nonneg ht0 (vR_nonneg h k)

theorem Tmax_neg_nonneg (h : tubeShapeOK tc = true) (k : Fin NV) :
    0 ≤ (tc.T : ℝ) * ((rmax (-(tc.vi k)) 0 : ℚ) : ℝ) := by
  rw [rmax_cast]; push_cast
  exact mul_nonneg (by exact_mod_cast (tubeShape_parts h).1) (le_max_right _ _)

/-- A tube point lies in the hull box. -/
theorem mem_tubeArr (h : tubeShapeOK tc = true) {zh : Vec} (hzh : InBoxR c c.r0 zh) {z : Vec}
    (hz : InTube zh (vR tc) tc.T (radR tc) z) : MemBox (tubeArr c tc) z := by
  obtain ⟨t, ht0, htT, hw⟩ := hz
  refine ⟨tubeArr_size c tc, fun k => ?_⟩
  rw [tubeArr_getD]
  have h1 := abs_le.mp (hzh k)
  have h2 := abs_le.mp (hw k)
  have h3 := tv_le_Tmax h ht0 htT k
  have h4 := tv_nonneg h ht0 k
  have h5 := Tmax_neg_nonneg h k
  unfold z0R at h1
  unfold radR at h2
  apply mem_mkR
  · push_cast; linarith [h1.1, h2.1]
  · push_cast; linarith [h1.2, h2.2]

/-! ## Coordinate shifts and translation invariance of the pair rows -/

/-- Shift coordinates `a` and `b` by `δ`. -/
def shiftV (a b : ℕ) (δ : ℝ) (z : Vec) : Vec :=
  fun k => if (k : ℕ) = a ∨ (k : ℕ) = b then z k + δ else z k

theorem getV_shiftV_eq {a b k : ℕ} (hk : k < NV) (h : k = a ∨ k = b) (δ : ℝ) (z : Vec) :
    getV (shiftV a b δ z) k = getV z k + δ := by
  simp only [getV, shiftV, dif_pos hk]
  rw [if_pos h]

theorem getV_shiftV_ne {a b k : ℕ} (h : k ≠ a ∧ k ≠ b) (δ : ℝ) (z : Vec) :
    getV (shiftV a b δ z) k = getV z k := by
  by_cases hk : k < NV
  · simp only [getV, shiftV, dif_pos hk]
    rw [if_neg (by rintro (h1 | h1) <;> [exact h.1 h1; exact h.2 h1])]
  · simp only [getV, dif_neg hk]

theorem seg_shiftV (a b : ℕ) (δ : ℝ) (z v : Vec) (t : ℝ) :
    seg (shiftV a b δ z) v t = shiftV a b δ (seg z v t) := by
  funext k
  simp only [seg, shiftV]
  split_ifs <;> ring

/-- The unit vector `e_k`. -/
def unitV (k : Fin NV) : Vec := fun j => if j = k then 1 else 0

theorem hasDerivAt_eval_unit (z : Vec) (e : Expr) (k : Fin NV) :
    HasDerivAt (fun t : ℝ => eval (seg z (unitV k) t) e) (eval z (e.D k)) 0 := by
  have h := hasDerivAt_eval z (unitV k) 0 e
  rw [seg_zero] at h
  have hs : ∑ j : Fin NV, eval z (e.D j) * unitV k j = eval z (e.D k) := by
    rw [Finset.sum_eq_single k]
    · simp [unitV]
    · intro j _ hj; simp [unitV, hj]
    · intro hc; exact absurd (Finset.mem_univ _) hc
  rw [hs] at h
  exact h

/-- **Invariance propagates to symbolic derivatives.** -/
theorem shift_inv_D {a b : ℕ} {e : Expr}
    (hinv : ∀ (z : Vec) (δ : ℝ), eval (shiftV a b δ z) e = eval z e) (k : Fin NV) :
    ∀ (z : Vec) (δ : ℝ), eval (shiftV a b δ z) (e.D k) = eval z (e.D k) := by
  intro z δ
  have h1 := hasDerivAt_eval_unit z e k
  have h2 := hasDerivAt_eval_unit (shiftV a b δ z) e k
  have hfun : (fun t : ℝ => eval (seg (shiftV a b δ z) (unitV k) t) e)
      = fun t => eval (seg z (unitV k) t) e := by
    funext t
    rw [seg_shiftV, hinv]
  rw [hfun] at h2
  exact h2.unique h1

theorem shift_inv_DD {a b : ℕ} {e : Expr}
    (hinv : ∀ (z : Vec) (δ : ℝ), eval (shiftV a b δ z) e = eval z e) (i j : Fin NV) :
    ∀ (z : Vec) (δ : ℝ), eval (shiftV a b δ z) ((e.D j).D i) = eval z ((e.D j).D i) :=
  shift_inv_D (shift_inv_D hinv j) i

/-! ### The closed forms under the two pair shifts -/

theorem cxZ_shiftX_i {i j : ℕ} (hi : i < 11) (δ : ℝ) (z : Vec) :
    cxZ (shiftV (3 * i) (3 * j) δ z) i = cxZ z i + δ := by
  unfold cxZ
  exact getV_shiftV_eq (by unfold NV; omega) (Or.inl rfl) δ z

theorem cxZ_shiftX_j {i j : ℕ} (hj : j < 11) (δ : ℝ) (z : Vec) :
    cxZ (shiftV (3 * i) (3 * j) δ z) j = cxZ z j + δ := by
  unfold cxZ
  exact getV_shiftV_eq (by unfold NV; omega) (Or.inr rfl) δ z

theorem cyZ_shiftX {i j : ℕ} (δ : ℝ) (z : Vec) (m : ℕ) :
    cyZ (shiftV (3 * i) (3 * j) δ z) m = cyZ z m := by
  unfold cyZ
  exact getV_shiftV_ne ⟨by omega, by omega⟩ δ z

theorem thZ_shiftX {i j : ℕ} (δ : ℝ) (z : Vec) (m : ℕ) :
    thZ (shiftV (3 * i) (3 * j) δ z) m = thZ z m := by
  unfold thZ
  exact getV_shiftV_ne ⟨by omega, by omega⟩ δ z

theorem sZ_shiftX {i j : ℕ} (hi : i < 11) (hj : j < 11) (δ : ℝ) (z : Vec) :
    sZ (shiftV (3 * i) (3 * j) δ z) = sZ z := by
  unfold sZ
  exact getV_shiftV_ne ⟨by unfold S_IDX; omega, by unfold S_IDX; omega⟩ δ z

theorem cyZ_shiftY_i {i j : ℕ} (hi : i < 11) (δ : ℝ) (z : Vec) :
    cyZ (shiftV (3 * i + 1) (3 * j + 1) δ z) i = cyZ z i + δ := by
  unfold cyZ
  exact getV_shiftV_eq (by unfold NV; omega) (Or.inl rfl) δ z

theorem cyZ_shiftY_j {i j : ℕ} (hj : j < 11) (δ : ℝ) (z : Vec) :
    cyZ (shiftV (3 * i + 1) (3 * j + 1) δ z) j = cyZ z j + δ := by
  unfold cyZ
  exact getV_shiftV_eq (by unfold NV; omega) (Or.inr rfl) δ z

theorem cxZ_shiftY {i j : ℕ} (δ : ℝ) (z : Vec) (m : ℕ) :
    cxZ (shiftV (3 * i + 1) (3 * j + 1) δ z) m = cxZ z m := by
  unfold cxZ
  exact getV_shiftV_ne ⟨by omega, by omega⟩ δ z

theorem thZ_shiftY {i j : ℕ} (δ : ℝ) (z : Vec) (m : ℕ) :
    thZ (shiftV (3 * i + 1) (3 * j + 1) δ z) m = thZ z m := by
  unfold thZ
  exact getV_shiftV_ne ⟨by omega, by omega⟩ δ z

theorem sZ_shiftY {i j : ℕ} (δ : ℝ) (z : Vec) :
    sZ (shiftV (3 * i + 1) (3 * j + 1) δ z) = sZ z := by
  unfold sZ
  exact getV_shiftV_ne ⟨by unfold S_IDX; omega, by unfold S_IDX; omega⟩ δ z

/-- The pair-frame image of `z` for squares `(i, j)`: `c_i ↦ c_i − c_j`, `c_j ↦ 0`. -/
def relZ (i j : ℕ) (z : Vec) : Vec :=
  shiftV (3 * i + 1) (3 * j + 1) (-(getV z (3 * j + 1))) (shiftV (3 * i) (3 * j) (-(getV z (3 * j))) z)

/-- A pair-invariant expression: invariant under both pair shifts. -/
def PairInv (i j : ℕ) (e : Expr) : Prop :=
  (∀ (z : Vec) (δ : ℝ), eval (shiftV (3 * i) (3 * j) δ z) e = eval z e) ∧
  (∀ (z : Vec) (δ : ℝ), eval (shiftV (3 * i + 1) (3 * j + 1) δ z) e = eval z e)

theorem PairInv.eval_relZ {i j : ℕ} {e : Expr} (h : PairInv i j e) (z : Vec) :
    eval (relZ i j z) e = eval z e := by
  unfold relZ
  rw [h.2, h.1]

theorem PairInv.D {i j : ℕ} {e : Expr} (h : PairInv i j e) (k : Fin NV) : PairInv i j (e.D k) :=
  ⟨shift_inv_D h.1 k, shift_inv_D h.2 k⟩

theorem PairInv.relZ_DD {i j : ℕ} {e : Expr} (h : PairInv i j e) (a b : Fin NV) (z : Vec) :
    eval (relZ i j z) ((e.D b).D a) = eval z ((e.D b).D a) :=
  ((h.D b).D a).eval_relZ z

theorem pairInv_edge {i j : ℕ} (hi : i < 11) (hj : j < 11) (kc e : ℕ) :
    PairInv i j (rowExpr (.edge i kc j e)) := by
  constructor
  · intro z δ
    simp only [rowExpr, eval_edgeRow, uZ, vZ, cornerP_fst, cornerP_snd, cxZ_shiftX_i hi,
      cxZ_shiftX_j hj, cyZ_shiftX, thZ_shiftX]
    ring
  · intro z δ
    simp only [rowExpr, eval_edgeRow, uZ, vZ, cornerP_fst, cornerP_snd, cyZ_shiftY_i hi,
      cyZ_shiftY_j hj, cxZ_shiftY, thZ_shiftY]
    ring

theorem pairInv_tanE {i j : ℕ} (hi : i < 11) (hj : j < 11) (kc e : ℕ) :
    PairInv i j (tanE i kc j e) := by
  constructor
  · intro z δ
    simp only [eval_tanE, uZ, vZ, cornerP_fst, cornerP_snd, cxZ_shiftX_i hi,
      cxZ_shiftX_j hj, cyZ_shiftX, thZ_shiftX]
    ring
  · intro z δ
    simp only [eval_tanE, uZ, vZ, cornerP_fst, cornerP_snd, cyZ_shiftY_i hi,
      cyZ_shiftY_j hj, cxZ_shiftY, thZ_shiftY]
    ring

theorem pairInv_depE {i j : ℕ} (hi : i < 11) (hj : j < 11) (kc e : ℕ) :
    PairInv i j (depE i kc j e) := by
  constructor
  · intro z δ
    simp only [eval_depE, uZ, vZ, cornerP_fst, cornerP_snd, cxZ_shiftX_i hi,
      cxZ_shiftX_j hj, cyZ_shiftX, thZ_shiftX]
    ring
  · intro z δ
    simp only [eval_depE, uZ, vZ, cornerP_fst, cornerP_snd, cyZ_shiftY_i hi,
      cyZ_shiftY_j hj, cxZ_shiftY, thZ_shiftY]
    ring

theorem pairInv_dist {i j : ℕ} (hi : i < 11) (hj : j < 11) :
    PairInv i j (rowExpr (.dist i j)) := by
  constructor
  · intro z δ
    simp only [eval_dist, cxZ_shiftX_i hi, cxZ_shiftX_j hj, cyZ_shiftX]
    ring
  · intro z δ
    simp only [eval_dist, cyZ_shiftY_i hi, cyZ_shiftY_j hj, cxZ_shiftY]
    ring

/-! ## The pair box -/

theorem pairArr_size (c : A22Cert) (tc : TubeCert) (i j : ℕ) : (pairArr c tc i j).size = NV := by
  simp [pairArr]

theorem pairArr_getD (c : A22Cert) (tc : TubeCert) (i j : ℕ) (k : Fin NV) :
    (pairArr c tc i j).getD k IV.zero =
      if (k : ℕ) = 3 * i ∨ (k : ℕ) = 3 * i + 1 then
        IV.mkR (c.z0.getD k 0 - c.z0.getD ((k : ℕ) - 3 * i + 3 * j) 0
            - tc.T * rmax (tc.vi k - tc.vi ((k : ℕ) - 3 * i + 3 * j)) 0
            - tc.rad k - tc.rad ((k : ℕ) - 3 * i + 3 * j) - 2 * c.r0)
          (c.z0.getD k 0 - c.z0.getD ((k : ℕ) - 3 * i + 3 * j) 0
            + tc.T * rmax (-(tc.vi k - tc.vi ((k : ℕ) - 3 * i + 3 * j))) 0
            + tc.rad k + tc.rad ((k : ℕ) - 3 * i + 3 * j) + 2 * c.r0)
      else if (k : ℕ) = 3 * j ∨ (k : ℕ) = 3 * j + 1 then IV.zero
      else (tubeArr c tc).getD k IV.zero := by
  unfold pairArr
  rw [getD_of_lt _ (by simp), Array.getElem_ofFn]

theorem getV_fin (z : Vec) (k : Fin NV) : getV z k = z k := by
  simp [getV, k.isLt]

theorem getV_nat (z : Vec) {a : ℕ} (ha : a < NV) : getV z a = z ⟨a, ha⟩ := by
  simp [getV, ha]

/-- The relative coordinate of a pair of tube points is enclosed by the pair interval. -/
theorem rel_coord_mem (h : tubeShapeOK tc = true) {zh : Vec} (hzh : InBoxR c c.r0 zh)
    {t : ℝ} (ht0 : 0 ≤ t) (htT : t ≤ (tc.T : ℝ)) {z : Vec}
    (hw : ∀ k, |z k - (zh k - t * vR tc k)| ≤ radR tc k) {a b : ℕ} (ha : a < NV) (hb : b < NV) :
    Mem (getV z a - getV z b)
      (IV.mkR (c.z0.getD a 0 - c.z0.getD b 0 - tc.T * rmax (tc.vi a - tc.vi b) 0
          - tc.rad a - tc.rad b - 2 * c.r0)
        (c.z0.getD a 0 - c.z0.getD b 0 + tc.T * rmax (-(tc.vi a - tc.vi b)) 0
          + tc.rad a + tc.rad b + 2 * c.r0)) := by
  rw [getV_nat z ha, getV_nat z hb]
  have hza := abs_le.mp (hzh ⟨a, ha⟩)
  have hzb := abs_le.mp (hzh ⟨b, hb⟩)
  have hwa := abs_le.mp (hw ⟨a, ha⟩)
  have hwb := abs_le.mp (hw ⟨b, hb⟩)
  simp only [z0R, radR, vR] at hza hzb hwa hwb
  have hT : (0 : ℝ) ≤ tc.T := by exact_mod_cast (tubeShape_parts h).1
  set dv : ℝ := ((tc.vi a : ℚ) : ℝ) - ((tc.vi b : ℚ) : ℝ) with hdv
  have hdv1 : t * dv ≤ (tc.T : ℝ) * ((rmax (tc.vi a - tc.vi b) 0 : ℚ) : ℝ) := by
    rw [rmax_cast]; push_cast
    calc t * dv ≤ t * max dv 0 := mul_le_mul_of_nonneg_left (le_max_left _ _) ht0
      _ ≤ (tc.T : ℝ) * max dv 0 := mul_le_mul_of_nonneg_right htT (le_max_right _ _)
  have hdv2 : -(t * dv) ≤ (tc.T : ℝ) * ((rmax (-(tc.vi a - tc.vi b)) 0 : ℚ) : ℝ) := by
    rw [rmax_cast]; push_cast
    calc -(t * dv) = t * (-dv) := by ring
      _ ≤ t * max (-dv) 0 := mul_le_mul_of_nonneg_left (le_max_left _ _) ht0
      _ ≤ (tc.T : ℝ) * max (-dv) 0 := mul_le_mul_of_nonneg_right htT (le_max_right _ _)
  have key : z ⟨a, ha⟩ - z ⟨b, hb⟩ = (zh ⟨a, ha⟩ - zh ⟨b, hb⟩) - t * dv
      + ((z ⟨a, ha⟩ - (zh ⟨a, ha⟩ - t * ((tc.vi a : ℚ) : ℝ)))
        - (z ⟨b, hb⟩ - (zh ⟨b, hb⟩ - t * ((tc.vi b : ℚ) : ℝ)))) := by
    simp only [hdv]; ring
  apply mem_mkR
  · push_cast; rw [key]; linarith [hza.1, hzb.2, hwa.1, hwb.2]
  · push_cast; rw [key]; linarith [hza.2, hzb.1, hwa.2, hwb.1]

section relZ
variable {i j : ℕ} (hi : i < 11) (hj : j < 11) (hij : i ≠ j) (z : Vec)
include hi hj hij

theorem relZ_getV_i : getV (relZ i j z) (3 * i) = getV z (3 * i) - getV z (3 * j) := by
  unfold relZ
  rw [getV_shiftV_ne ⟨by omega, by omega⟩, getV_shiftV_eq (by unfold NV; omega) (Or.inl rfl)]
  ring

theorem relZ_getV_i1 :
    getV (relZ i j z) (3 * i + 1) = getV z (3 * i + 1) - getV z (3 * j + 1) := by
  unfold relZ
  rw [getV_shiftV_eq (by unfold NV; omega) (Or.inl rfl), getV_shiftV_ne ⟨by omega, by omega⟩]
  ring

theorem relZ_getV_j : getV (relZ i j z) (3 * j) = 0 := by
  unfold relZ
  rw [getV_shiftV_ne ⟨by omega, by omega⟩, getV_shiftV_eq (by unfold NV; omega) (Or.inr rfl)]
  ring

theorem relZ_getV_j1 : getV (relZ i j z) (3 * j + 1) = 0 := by
  unfold relZ
  rw [getV_shiftV_eq (by unfold NV; omega) (Or.inr rfl), getV_shiftV_ne ⟨by omega, by omega⟩]
  ring

end relZ

theorem relZ_getV_other {i j : ℕ} (z : Vec) (k : ℕ)
    (hk : ¬(k = 3 * i ∨ k = 3 * i + 1) ∧ ¬(k = 3 * j ∨ k = 3 * j + 1)) :
    getV (relZ i j z) k = getV z k := by
  unfold relZ
  rw [getV_shiftV_ne ⟨by omega, by omega⟩, getV_shiftV_ne ⟨by omega, by omega⟩]

/-- A tube point, translated into the pair frame, lies in the pair box. -/
theorem mem_pairArr (h : tubeShapeOK tc = true) {zh : Vec} (hzh : InBoxR c c.r0 zh) {z : Vec}
    (hz : InTube zh (vR tc) tc.T (radR tc) z) {i j : ℕ} (hi : i < 11) (hj : j < 11)
    (hij : i ≠ j) : MemBox (pairArr c tc i j) (relZ i j z) := by
  have hhull := mem_tubeArr h hzh hz
  obtain ⟨t, ht0, htT, hw⟩ := hz
  have htT' : t ≤ (tc.T : ℝ) := htT
  refine ⟨pairArr_size c tc i j, fun k => ?_⟩
  rw [pairArr_getD, ← getV_fin (relZ i j z) k]
  by_cases hk1 : (k : ℕ) = 3 * i ∨ (k : ℕ) = 3 * i + 1
  · rw [if_pos hk1]
    rcases hk1 with hk | hk
    · rw [hk]
      have hb : (3 * i - 3 * i + 3 * j : ℕ) = 3 * j := by omega
      rw [hb, relZ_getV_i hi hj hij]
      exact rel_coord_mem h hzh ht0 htT' hw (by unfold NV; omega) (by unfold NV; omega)
    · rw [hk]
      have hb : (3 * i + 1 - 3 * i + 3 * j : ℕ) = 3 * j + 1 := by omega
      rw [hb, relZ_getV_i1 hi hj hij]
      exact rel_coord_mem h hzh ht0 htT' hw (by unfold NV; omega) (by unfold NV; omega)
  · rw [if_neg hk1]
    by_cases hk2 : (k : ℕ) = 3 * j ∨ (k : ℕ) = 3 * j + 1
    · rw [if_pos hk2]
      rcases hk2 with hk | hk
      · rw [hk, relZ_getV_j hi hj hij]; exact mem_zero
      · rw [hk, relZ_getV_j1 hi hj hij]; exact mem_zero
    · rw [if_neg hk2, relZ_getV_other z k ⟨hk1, hk2⟩, getV_fin]
      exact hhull.2 k

/-! ## Enclosures on the tube: every row on its own box -/

theorem rowBoxT_edge (c : A22Cert) (tc : TubeCert) (i kc j e : ℕ) :
    rowBoxT c tc (.edge i kc j e) = Box.ofArray (pairArr c tc i j) := rfl

theorem rowBoxT_dist (c : A22Cert) (tc : TubeCert) (i j : ℕ) :
    rowBoxT c tc (.dist i j) = Box.ofArray (pairArr c tc i j) := rfl

theorem rowBoxT_wall (c : A22Cert) (tc : TubeCert) (i kc w : ℕ) :
    rowBoxT c tc (.wall i kc w) = Box.ofArray (tubeArr c tc) := rfl

theorem rowBoxT_angeq (c : A22Cert) (tc : TubeCert) (i j : ℕ) :
    rowBoxT c tc (.angeq i j) = Box.ofArray (tubeArr c tc) := rfl

/-- Second derivatives of row `k`, enclosed on the row's box, at any tube point. -/
theorem mem_hess_rowT (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η)
    {k : ℕ} (hk : k < NEXT3) (i j : Fin NV) :
    Mem (eval η (((e70 c k).D j).D i))
      (((hessDense (rowBoxT c tc (row70 c k)) (row70 c k)).getD i #[]).getD j IV.zero) := by
  obtain ⟨hu, hshape⟩ := rows70_parts hr k hk
  unfold e70 at hu ⊢
  rcases hR : row70 c k with ⟨i', kc, w⟩ | ⟨i', kc, j', e⟩ | ⟨i', j'⟩ | ⟨i', j'⟩
  · rw [hR] at hu
    rw [rowBoxT_wall]
    exact hessDense_sound (mem_tubeArr hsh hzh hη) _ hu i j
  · rw [hR] at hu hshape
    have hs' : i' < 11 ∧ kc < 4 ∧ j' < 11 ∧ e < 4 ∧ i' ≠ j' := hshape
    obtain ⟨hi', -, hj', -, hij'⟩ := hs'
    rw [rowBoxT_edge, ← (pairInv_edge hi' hj' kc e).relZ_DD i j η]
    exact hessDense_sound (mem_pairArr hsh hzh hη hi' hj' hij') _ hu i j
  · rw [hR] at hu hshape
    have hs' : i' < 11 ∧ j' < 11 ∧ i' ≠ j' := hshape
    obtain ⟨hi', hj', hij'⟩ := hs'
    rw [rowBoxT_dist, ← (pairInv_dist hi' hj').relZ_DD i j η]
    exact hessDense_sound (mem_pairArr hsh hzh hη hi' hj' hij') _ hu i j
  · rw [hR] at hu
    rw [rowBoxT_angeq]
    exact hessDense_sound (mem_tubeArr hsh hzh hη) _ hu i j

/-- First derivatives of row `k`, enclosed on the row's box, at any tube point. -/
theorem mem_grad_rowT (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {ξ : Vec} (hξ : InTube zh (vR tc) tc.T (radR tc) ξ)
    {k : ℕ} (hk : k < NEXT3) (j : Fin NV) :
    Mem (eval ξ ((e70 c k).D j)) ((gradDense (rowBoxT c tc (row70 c k)) (row70 c k)).getD j IV.zero) := by
  obtain ⟨hu, hshape⟩ := rows70_parts hr k hk
  unfold e70 at hu ⊢
  rcases hR : row70 c k with ⟨i', kc, w⟩ | ⟨i', kc, j', e⟩ | ⟨i', j'⟩ | ⟨i', j'⟩
  · rw [hR] at hu
    rw [rowBoxT_wall]
    exact gradDense_sound (mem_tubeArr hsh hzh hξ) _ hu j
  · rw [hR] at hu hshape
    have hs' : i' < 11 ∧ kc < 4 ∧ j' < 11 ∧ e < 4 ∧ i' ≠ j' := hshape
    obtain ⟨hi', -, hj', -, hij'⟩ := hs'
    rw [rowBoxT_edge, ← ((pairInv_edge hi' hj' kc e).D j).eval_relZ ξ]
    exact gradDense_sound (mem_pairArr hsh hzh hξ hi' hj' hij') _ hu j
  · rw [hR] at hu hshape
    have hs' : i' < 11 ∧ j' < 11 ∧ i' ≠ j' := hshape
    obtain ⟨hi', hj', hij'⟩ := hs'
    rw [rowBoxT_dist, ← ((pairInv_dist hi' hj').D j).eval_relZ ξ]
    exact gradDense_sound (mem_pairArr hsh hzh hξ hi' hj' hij') _ hu j
  · rw [hR] at hu
    rw [rowBoxT_angeq]
    exact gradDense_sound (mem_tubeArr hsh hzh hξ) _ hu j

theorem a36_omega (tc : TubeCert) : tc.a36.omega = tc.omega := rfl

theorem a36_P (tc : TubeCert) : tc.a36.P = tc.P := rfl

/-- The Hessian of `W` on the tube is enclosed by `omegaHessT`. -/
theorem mem_omegaHessT (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η)
    (i j : Fin NV) :
    Mem (Whess c tc.a36 η i j) (((omegaHessT c tc).getD i #[]).getD j IV.zero) := by
  rw [Whess_eq_loaded]
  unfold omegaHessT
  have := foldl_mkM_sound (l := loaded tc.a36) (S := fun _ _ => 0)
    (g := fun k i j => eval η (((e70 c k).D j).D i))
    (G := fun k => hessDense (rowBoxT c tc (row70 c k)) (row70 c k))
    (w := fun k => tc.omega.getD k 0)
    (fun k hk i j => mem_hess_rowT hsh hr hzh hη (loaded_lt tc.a36 hk) i j)
    (acc := mkM NV fun _ _ => IV.zero) (fun i j => by rw [mkM_getD _ i.isLt j.isLt]; exact mem_zero) i j
  simpa [ωR, a36_omega] using this

/-- The pin-row Jacobian enclosure on the tube. -/
theorem mem_pinJT (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true) (hP : tc.P.size = NV)
    (hlt : ∀ k ∈ tc.P, k < NEXT3) {zh : Vec} (hzh : InBoxR c c.r0 zh)
    {ξ : Vec} (hξ : InTube zh (vR tc) tc.T (radR tc) ξ) (rr j : Fin NV) :
    Mem (eval ξ ((e70 c (pinPos tc.a36 rr)).D j)) (((pinJT c tc).getD rr #[]).getD j IV.zero) := by
  have hrr : (rr : ℕ) < (pinJT c tc).size := by simp [pinJT, hP]
  rw [getD_of_lt _ hrr]
  simp only [pinJT, Array.getElem_map]
  have hrr' : (rr : ℕ) < tc.P.size := by rw [hP]; exact rr.isLt
  have hpos : pinPos tc.a36 rr = tc.P[(rr : ℕ)] := by
    unfold pinPos; rw [a36_P, getD_of_lt _ hrr']
  rw [hpos]
  exact mem_grad_rowT hsh hr hzh hξ (hlt _ (Array.getElem_mem hrr')) j

/-- `m_ij(ξ) = δ_ij − Σ_r Y_ir ∂_j g_{P_r}(ξ_r)` is enclosed by `Mrow` on the tube. -/
theorem mem_Mrow_pinT (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true) (hP : tc.P.size = NV)
    (hlt : ∀ k ∈ tc.P, k < NEXT3) {zh : Vec} (hzh : InBoxR c c.r0 zh)
    {ξ : Fin NV → Vec} (hξ : ∀ rr, InTube zh (vR tc) tc.T (radR tc) (ξ rr)) (i j : Fin NV) :
    Mem ((if i = j then 1 else 0)
        - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos tc.a36 rr)).D j))
      ((Mrow c.Y (pinJT c tc) i).getD j IV.zero) := by
  unfold Mrow
  rw [mkV_getD _ j.isLt]
  refine mem_sub ?_ ?_
  · by_cases h : i = j
    · have h' : (i : ℕ) = (j : ℕ) := by rw [h]
      rw [if_pos h, if_pos h']; exact mem_one
    · have h' : ¬ (i : ℕ) = (j : ℕ) := fun hc => h (Fin.ext hc)
      rw [if_neg h, if_neg h']; exact mem_zero
  · have := mem_foldl_add (n := NV) (a := 0) mem_zero
      (f := fun rr => ((Ymat c.Y i rr : ℚ) : ℝ)
        * eval (ξ ⟨rr % NV, Nat.mod_lt _ (by decide)⟩) ((e70 c (pinPos tc.a36 rr)).D j))
      (g := fun rr => IV.pt (Ymat c.Y i rr) * ((pinJT c tc).getD rr #[]).getD j IV.zero)
      (fun rr hrr => by
        have hrr' : rr % NV = rr := Nat.mod_eq_of_lt hrr
        have hm := mem_pinJT hsh hr hP hlt hzh (hξ ⟨rr, hrr⟩) ⟨rr, hrr⟩ ⟨j, j.isLt⟩
        simp only [hrr'] at hm ⊢
        exact mem_mul (mem_pt _) hm)
    rw [zero_add, sum_range_NV_eq] at this
    have key : (∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos tc.a36 rr)).D j))
        = ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * eval (ξ ⟨(rr : ℕ) % NV, Nat.mod_lt _ (by decide)⟩) ((e70 c (pinPos tc.a36 rr)).D j) := by
      refine sum_congr rfl fun rr _ => ?_
      rw [fin_mod_self]
    rw [key]
    exact this

theorem betaRow_le_betaT (c : A22Cert) (tc : TubeCert) (i : Fin NV) :
    betaRow (Mrow c.Y (pinJT c tc) i) ≤ betaT c tc := by
  unfold betaT
  rw [rng_eq]
  exact le_foldl_rmax (List.range NV) 0 (fun i => betaRow (Mrow c.Y (pinJT c tc) i)) i
    (List.mem_range.mpr i.isLt)

/-! ## Validity of the loaded rows on the tube -/

theorem loaded_row_nonneg_T (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    (hlv : loadedValidT c tc = true) {zh : Vec} (hzh : InBoxR c c.r0 zh) {z : Vec}
    (hz : InTube zh (vR tc) tc.T (radR tc) z) (hsm : SmallTilt z) (hf : Feas z) {k : ℕ}
    (hk : k ∈ loaded tc.a36) : 0 ≤ eval z (e70 c k) := by
  simp only [loadedValidT, List.all_eq_true] at hlv
  have hlv' := hlv k hk
  obtain ⟨-, hshape⟩ := rows70_parts hr k (loaded_lt tc.a36 hk)
  unfold e70
  rcases hR : row70 c k with ⟨i, kc, w⟩ | ⟨i, kc, j, e⟩ | ⟨i, j⟩ | ⟨i, j⟩
  · rw [hR] at hshape
    have hs' : i < 11 ∧ kc < 4 ∧ w < 4 := hshape
    exact wall_valid hf hs'.1 (abs_lt_pi_of_le_one (hsm i hs'.1)) kc w
  · rw [hR] at hshape hlv'
    have hs' : i < 11 ∧ kc < 4 ∧ j < 11 ∧ e < 4 ∧ i ≠ j := hshape
    obtain ⟨hi, -, hj, he, hij⟩ := hs'
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hlv'
    obtain ⟨h1, h2⟩ := hlv'
    rw [rowBoxT_edge] at h1 h2
    have hm1 := mem_mag (evalIV_sound (mem_pairArr hsh hzh hz hi hj hij) (tanE i kc j e))
    have hm2 := (evalIV_sound (mem_pairArr hsh hzh hz hi hj hij) (depE i kc j e)).1
    rw [(pairInv_tanE hi hj kc e).eval_relZ] at hm1
    rw [(pairInv_depE hi hj kc e).eval_relZ] at hm2
    have h1' : (((evalIV (Box.ofArray (pairArr c tc i j)) (tanE i kc j e)).mag : ℚ) : ℝ)
        < ((1 / 2 : ℚ) : ℝ) := by exact_mod_cast h1
    have h2' : (((-1 / 2 : ℚ)) : ℝ)
        < (((evalIV (Box.ofArray (pairArr c tc i j)) (depE i kc j e)).lo : ℚ) : ℝ) := by
      exact_mod_cast h2
    push_cast at h1' h2'
    exact edge_valid hf hi hj hij (abs_lt_pi_of_le_one (hsm i hi)) (abs_lt_pi_of_le_one (hsm j hj))
      kc e he (by linarith) (by linarith)
  · rw [hR] at hshape
    have hs' : i < 11 ∧ j < 11 ∧ i ≠ j := hshape
    obtain ⟨hi, hj, hij⟩ := hs'
    exact dist_valid hf hi hj hij (abs_lt_pi_of_le_one (hsm i hi)) (abs_lt_pi_of_le_one (hsm j hj))
  · rw [hR] at hlv'
    exact absurd hlv' Bool.false_ne_true

theorem W_nonneg_T (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true) (ho : omegaOK tc.a36 = true)
    (hlv : loadedValidT c tc = true) {zh : Vec} (hzh : InBoxR c c.r0 zh) {z : Vec}
    (hz : InTube zh (vR tc) tc.T (radR tc) z) (hsm : SmallTilt z) (hf : Feas z) :
    0 ≤ Wfun c tc.a36 z := by
  rw [Wfun_eq_loaded]
  refine Finset.sum_nonneg fun k hk => ?_
  rw [List.mem_toFinset] at hk
  exact mul_nonneg (omega_nonneg ho k) (loaded_row_nonneg_T hsh hr hlv hzh hz hsm hf hk)

/-- The pin sum is bounded by `W` on the tube. -/
theorem pin_sum_le_W_T (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    (ho : omegaOK tc.a36 = true) (hlv : loadedValidT c tc = true)
    (hpos : pinsPositive tc.a36 = true) (hrange : pinsRangeOK tc.a36 = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {z : Vec}
    (hz : InTube zh (vR tc) tc.T (radR tc) z) (hsm : SmallTilt z) (hf : Feas z) :
    ∑ r : Fin NV, ωR tc.a36 (pinPos tc.a36 r) * eval z (e70 c (pinPos tc.a36 r)) ≤ Wfun c tc.a36 z := by
  set a := tc.a36 with ha
  simp only [pinsPositive, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hpos
  obtain ⟨hP, hω⟩ := hpos
  simp only [pinsRangeOK, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hrange
  obtain ⟨hlt, hnodup⟩ := hrange
  rw [Wfun_eq_loaded]
  have hinj : Function.Injective (fun r : Fin NV => pinPos a r) := by
    intro r s hrs
    have hr : (r : ℕ) < a.P.size := by rw [hP]; exact r.isLt
    have hs : (s : ℕ) < a.P.size := by rw [hP]; exact s.isLt
    simp only [pinPos, getD_of_lt _ hr, getD_of_lt _ hs] at hrs
    have := (List.nodup_iff_injective_get.mp hnodup)
    have h2 : a.P.toList.get ⟨r, by simpa using hr⟩ = a.P.toList.get ⟨s, by simpa using hs⟩ := by
      simpa using hrs
    have := this h2
    exact Fin.ext (by simpa using congrArg Fin.val this)
  rw [← Finset.sum_image (f := fun k => ωR a k * eval z (e70 c k)) (fun r _ s _ h => hinj h)]
  refine Finset.sum_le_sum_of_subset_of_nonneg ?_ ?_
  · intro k hk
    rw [Finset.mem_image] at hk
    obtain ⟨r, -, rfl⟩ := hk
    rw [List.mem_toFinset]
    have hr : (r : ℕ) < a.P.size := by rw [hP]; exact r.isLt
    refine mem_loaded a ?_ ?_
    · unfold pinPos; rw [getD_of_lt _ hr]; exact hlt r hr
    · unfold pinPos; rw [getD_of_lt _ hr]; exact (hω r hr).ne'
  · intro k hk _
    rw [List.mem_toFinset] at hk
    exact mul_nonneg (omega_nonneg ho k) (loaded_row_nonneg_T hsh hr hlv hzh hz hsm hf hk)

/-! ## Segment forms of the mean-value theorem and the Taylor expansion -/

theorem mvt_seg (p q : Vec) (e : Expr) :
    ∃ θ ∈ Ioo (0 : ℝ) 1,
      eval q e - eval p e = ∑ j : Fin NV, eval (seg p (fun i => q i - p i) θ) (e.D j) * (q j - p j) := by
  have hd : ∀ t, HasDerivAt (fun t => eval (seg p (fun i => q i - p i) t) e)
      (∑ j : Fin NV, eval (seg p (fun i => q i - p i) t) (e.D j) * (q j - p j)) t :=
    fun t => hasDerivAt_eval p (fun i => q i - p i) t e
  obtain ⟨θ, hθ, hderiv⟩ := exists_hasDerivAt_eq_slope
    (fun t => eval (seg p (fun i => q i - p i) t) e)
    (fun t => ∑ j : Fin NV, eval (seg p (fun i => q i - p i) t) (e.D j) * (q j - p j))
    (by norm_num : (0 : ℝ) < 1)
    (fun t _ => (hd t).continuousAt.continuousWithinAt) (fun t _ => hd t)
  refine ⟨θ, hθ, ?_⟩
  rw [seg_one_sub, seg_zero, sub_zero, div_one] at hderiv
  exact hderiv.symm

theorem Wfun_taylor_seg {c : A22Cert} {a : A36Cert} (p q : Vec) :
    ∃ θ ∈ Ioo (0 : ℝ) 1,
      Wfun c a q = Wfun c a p + ∑ j : Fin NV, Wgrad c a p j * (q j - p j)
        + (∑ j : Fin NV, ∑ i : Fin NV,
            Whess c a (seg p (fun i => q i - p i) θ) i j * (q i - p i) * (q j - p j)) / 2 := by
  set v : Vec := fun i => q i - p i with hv
  obtain ⟨θ, hθ, heq⟩ := taylor2 (φ := fun t => Wfun c a (seg p v t))
    (φ' := fun t => ∑ k ∈ range NEXT3, ωR a k * ∑ j : Fin NV, eval (seg p v t) ((e70 c k).D j) * v j)
    (φ'' := fun t => ∑ k ∈ range NEXT3, ωR a k * ∑ j : Fin NV,
        (∑ i : Fin NV, eval (seg p v t) (((e70 c k).D j).D i) * v i) * v j)
    (fun t => hasDerivAt_Wfun p v t) (fun t => hasDerivAt_Wfun' p v t)
  refine ⟨θ, hθ, ?_⟩
  have h1 : seg p v 1 = q := seg_one_sub p q
  have h0 : seg p v 0 = p := seg_zero p v
  rw [h1, h0] at heq
  rw [heq]
  congr 1
  · congr 1
    simp only [Wgrad, Finset.sum_mul, Finset.mul_sum]
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun j _ => Finset.sum_congr rfl fun k _ => by simp only [hv]; ring
  · congr 1
    simp only [Whess, Finset.sum_mul, Finset.mul_sum]
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun k _ => by simp only [hv]; ring

/-! ## The split remainder, real form -/

noncomputable def tbR (T rS x : ℝ) : ℝ := min T (x + rS)

noncomputable def wbR (tc : TubeCert) (x : ℝ) (i : ℕ) : ℝ :=
  min ((tc.rad i : ℚ) : ℝ) (x + tbR tc.T tc.rS x * |((tc.vi i : ℚ) : ℝ)|)

/-- `E(x)` over the reals. -/
noncomputable def EtubeR (tc : TubeCert) (st : TubeStats) (x : ℝ) : ℝ :=
  (st.e0 : ℝ) + (st.ew : ℝ) * x + (1 / 2) * tbR tc.T tc.rS x * tbR tc.T tc.rS x * (st.qvv : ℝ)
    + tbR tc.T tc.rS x * ∑ i ∈ range NV, ((st.hvi i : ℚ) : ℝ) * wbR tc x i
    + (1 / 2) * ∑ a ∈ range NV, ∑ b ∈ range NV, ((st.hmab a b : ℚ) : ℝ) * wbR tc x a * wbR tc x b

/-- `ψ(x)` over the reals. -/
noncomputable def psiR (tc : TubeCert) (st : TubeStats) (x : ℝ) : ℝ :=
  ((st.keff : ℝ) * EtubeR tc st x + (st.kap : ℝ) * (st.gm : ℝ)) / (1 - (st.beta : ℝ))

theorem tbQ_cast (T rS x : ℚ) : ((tbQ T rS x : ℚ) : ℝ) = tbR (T : ℝ) (rS : ℝ) (x : ℝ) := by
  unfold tbQ tbR
  rw [rmin_cast]
  push_cast
  rfl

theorem wbQ_cast (tc : TubeCert) (x : ℚ) (i : ℕ) : ((wbQ tc x i : ℚ) : ℝ) = wbR tc (x : ℝ) i := by
  unfold wbQ wbR
  rw [rmin_cast]
  push_cast
  rw [tbQ_cast, rabs_cast]

theorem Etube_cast (tc : TubeCert) (st : TubeStats) (x : ℚ) :
    ((Etube tc st x : ℚ) : ℝ) = EtubeR tc st (x : ℝ) := by
  unfold Etube EtubeR
  simp only [rng_eq, foldl_add_eq_sum, zero_add]
  push_cast
  simp only [tbQ_cast, wbQ_cast]

theorem psiT_cast (tc : TubeCert) (st : TubeStats) (x : ℚ) :
    ((psiT tc st x : ℚ) : ℝ) = psiR tc st (x : ℝ) := by
  unfold psiT psiR
  push_cast
  rw [Etube_cast]

/-! ### Monotonicity of `E` and `ψ` on `[0, ∞)` -/

theorem tbR_nonneg {T rS x : ℝ} (hT : 0 ≤ T) (hrS : 0 ≤ rS) (hx : 0 ≤ x) : 0 ≤ tbR T rS x :=
  le_min hT (by linarith)

theorem tbR_mono {T rS x y : ℝ} (hxy : x ≤ y) : tbR T rS x ≤ tbR T rS y :=
  min_le_min le_rfl (by linarith)

theorem wbR_nonneg (hsh : tubeShapeOK tc = true) {x : ℝ} (hx : 0 ≤ x) (i : ℕ) : 0 ≤ wbR tc x i := by
  obtain ⟨hT, -, -, hrS, -⟩ := tubeShape_parts hsh
  refine le_min (by exact_mod_cast rad_nonneg hsh i) ?_
  exact add_nonneg hx (mul_nonneg (tbR_nonneg (by exact_mod_cast hT) (by exact_mod_cast hrS) hx)
    (abs_nonneg _))

theorem wbR_mono {x y : ℝ} (hxy : x ≤ y) (i : ℕ) : wbR tc x i ≤ wbR tc y i :=
  min_le_min le_rfl (add_le_add hxy (mul_le_mul_of_nonneg_right (tbR_mono hxy) (abs_nonneg _)))

theorem EtubeR_mono (hsh : tubeShapeOK tc = true) {st : TubeStats} (hew : 0 ≤ st.ew)
    (hq : 0 ≤ st.qvv) (hhv : ∀ i, 0 ≤ st.hvi i) (hhm : ∀ a b, 0 ≤ st.hmab a b)
    {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) : EtubeR tc st x ≤ EtubeR tc st y := by
  obtain ⟨hT, -, -, hrS, -⟩ := tubeShape_parts hsh
  have hT' : (0 : ℝ) ≤ tc.T := by exact_mod_cast hT
  have hrS' : (0 : ℝ) ≤ tc.rS := by exact_mod_cast hrS
  have hy : 0 ≤ y := le_trans hx hxy
  have tb0 := tbR_nonneg (T := (tc.T : ℝ)) (rS := (tc.rS : ℝ)) hT' hrS' hx
  have tb0y := tbR_nonneg (T := (tc.T : ℝ)) (rS := (tc.rS : ℝ)) hT' hrS' hy
  have tbm := tbR_mono (T := (tc.T : ℝ)) (rS := (tc.rS : ℝ)) hxy
  have wb0 := wbR_nonneg (tc := tc) hsh hx
  have wb0y := wbR_nonneg (tc := tc) hsh hy
  have wbm := wbR_mono (tc := tc) hxy
  have hew' : (0 : ℝ) ≤ st.ew := by exact_mod_cast hew
  have hq' : (0 : ℝ) ≤ st.qvv := by exact_mod_cast hq
  have hhv' : ∀ i, (0 : ℝ) ≤ ((st.hvi i : ℚ) : ℝ) := fun i => by exact_mod_cast hhv i
  have hhm' : ∀ a b, (0 : ℝ) ≤ ((st.hmab a b : ℚ) : ℝ) := fun a b => by exact_mod_cast hhm a b
  unfold EtubeR
  have h1 : (st.ew : ℝ) * x ≤ (st.ew : ℝ) * y := mul_le_mul_of_nonneg_left hxy hew'
  have h2 : (1 / 2 : ℝ) * tbR tc.T tc.rS x * tbR tc.T tc.rS x * (st.qvv : ℝ)
      ≤ (1 / 2 : ℝ) * tbR tc.T tc.rS y * tbR tc.T tc.rS y * (st.qvv : ℝ) := by
    have : tbR tc.T tc.rS x * tbR tc.T tc.rS x ≤ tbR tc.T tc.rS y * tbR tc.T tc.rS y :=
      mul_le_mul tbm tbm tb0 tb0y
    nlinarith
  have hS1 : ∑ i ∈ range NV, ((st.hvi i : ℚ) : ℝ) * wbR tc x i
      ≤ ∑ i ∈ range NV, ((st.hvi i : ℚ) : ℝ) * wbR tc y i :=
    Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (wbm i) (hhv' i)
  have hS10 : 0 ≤ ∑ i ∈ range NV, ((st.hvi i : ℚ) : ℝ) * wbR tc x i :=
    Finset.sum_nonneg fun i _ => mul_nonneg (hhv' i) (wb0 i)
  have h3 : tbR tc.T tc.rS x * ∑ i ∈ range NV, ((st.hvi i : ℚ) : ℝ) * wbR tc x i
      ≤ tbR tc.T tc.rS y * ∑ i ∈ range NV, ((st.hvi i : ℚ) : ℝ) * wbR tc y i :=
    mul_le_mul tbm hS1 hS10 tb0y
  have h4 : ∑ a ∈ range NV, ∑ b ∈ range NV, ((st.hmab a b : ℚ) : ℝ) * wbR tc x a * wbR tc x b
      ≤ ∑ a ∈ range NV, ∑ b ∈ range NV, ((st.hmab a b : ℚ) : ℝ) * wbR tc y a * wbR tc y b := by
    refine Finset.sum_le_sum fun a _ => Finset.sum_le_sum fun b _ => ?_
    have : wbR tc x a * wbR tc x b ≤ wbR tc y a * wbR tc y b :=
      mul_le_mul (wbm a) (wbm b) (wb0 b) (wb0y a)
    calc ((st.hmab a b : ℚ) : ℝ) * wbR tc x a * wbR tc x b
        = ((st.hmab a b : ℚ) : ℝ) * (wbR tc x a * wbR tc x b) := by ring
      _ ≤ ((st.hmab a b : ℚ) : ℝ) * (wbR tc y a * wbR tc y b) :=
          mul_le_mul_of_nonneg_left this (hhm' a b)
      _ = ((st.hmab a b : ℚ) : ℝ) * wbR tc y a * wbR tc y b := by ring
  linarith

theorem psiR_mono (hsh : tubeShapeOK tc = true) {st : TubeStats} (hβ : st.beta < 1)
    (hkeff : 0 ≤ st.keff) (hew : 0 ≤ st.ew) (hq : 0 ≤ st.qvv) (hhv : ∀ i, 0 ≤ st.hvi i)
    (hhm : ∀ a b, 0 ≤ st.hmab a b) {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) :
    psiR tc st x ≤ psiR tc st y := by
  unfold psiR
  have h1b : (0 : ℝ) < 1 - (st.beta : ℝ) := by
    have : (st.beta : ℝ) < 1 := by exact_mod_cast hβ
    linarith
  have hkeff' : (0 : ℝ) ≤ st.keff := by exact_mod_cast hkeff
  apply div_le_div_of_nonneg_right _ h1b.le
  exact add_le_add
    (mul_le_mul_of_nonneg_left (EtubeR_mono hsh hew hq hhv hhm hx hxy) hkeff') le_rfl

theorem le_rup_cast (q : ℚ) : (q : ℝ) ≤ ((rup q : ℚ) : ℝ) := by exact_mod_cast le_rup q

/-- **The monotone iteration is sound**: if the true norm `x₀` satisfies `x₀ ≤ ψ(x₀)` and
`x₀ ≤ X`, then a successful run of `iterT` from `X` gives `x₀ + r0 ≤ r_N`. -/
theorem iterT_sound (hsh : tubeShapeOK tc = true) {st : TubeStats} (hβ : st.beta < 1)
    (hkeff : 0 ≤ st.keff) (hew : 0 ≤ st.ew) (hq : 0 ≤ st.qvv) (hhv : ∀ i, 0 ≤ st.hvi i)
    (hhm : ∀ a b, 0 ≤ st.hmab a b) {r0 rN : ℚ} {x0 : ℝ} (hx0 : 0 ≤ x0) (hfix : x0 ≤ psiR tc st x0) :
    ∀ (n : ℕ) (X : ℚ), x0 ≤ (X : ℝ) → iterT tc st r0 rN n X = true → x0 + (r0 : ℝ) ≤ (rN : ℝ) := by
  intro n
  induction n with
  | zero => intro X _ h; simp [iterT] at h
  | succ n ih =>
    intro X hX h
    have hy : x0 ≤ ((rup (psiT tc st X) : ℚ) : ℝ) := by
      calc x0 ≤ psiR tc st x0 := hfix
        _ ≤ psiR tc st (X : ℝ) := psiR_mono hsh hβ hkeff hew hq hhv hhm hx0 hX
        _ = ((psiT tc st X : ℚ) : ℝ) := (psiT_cast tc st X).symm
        _ ≤ _ := le_rup_cast _
    unfold iterT at h
    simp only at h
    split_ifs at h with h1 h2
    · have : ((rup (psiT tc st X) + r0 : ℚ) : ℝ) ≤ (rN : ℝ) := by exact_mod_cast h1
      push_cast at this
      linarith
    · exact ih _ hy h

/-! ### Enclosures of the checker's Hessian statistics -/

/-- `Whess` with natural indices (`0` out of range). -/
noncomputable def WhessN (c : A22Cert) (a : A36Cert) (η : Vec) (i j : ℕ) : ℝ :=
  if h : i < NV ∧ j < NV then Whess c a η ⟨i, h.1⟩ ⟨j, h.2⟩ else 0

theorem WhessN_fin (c : A22Cert) (a : A36Cert) (η : Vec) (i j : Fin NV) :
    WhessN c a η i j = Whess c a η i j := by
  simp [WhessN, i.isLt, j.isLt]

theorem mem_Hget (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η)
    {a b : ℕ} (ha : a < NV) (hb : b < NV) :
    Mem (WhessN c tc.a36 η a b) (Hget (omegaHessT c tc) a b) := by
  simp only [WhessN, dif_pos (And.intro ha hb)]
  exact mem_omegaHessT hsh hr hzh hη ⟨a, ha⟩ ⟨b, hb⟩

theorem abs_qvv (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η) :
    |∑ i : Fin NV, ∑ j : Fin NV, vR tc i * vR tc j * Whess c tc.a36 η i j|
      ≤ ((qvvT tc (omegaHessT c tc) : ℚ) : ℝ) := by
  unfold qvvT
  have hrow : ∀ a, a < NV → Mem (∑ b ∈ range NV, ((tc.vi a * tc.vi b : ℚ) : ℝ) * WhessN c tc.a36 η a b)
      (vHvRow tc (omegaHessT c tc) a) := by
    intro a ha
    unfold vHvRow
    rw [rng_eq]
    have := mem_foldl_add (n := NV) (a := 0) mem_zero
      (f := fun b => ((tc.vi a * tc.vi b : ℚ) : ℝ) * WhessN c tc.a36 η a b)
      (g := fun b => IV.pt (tc.vi a * tc.vi b) * Hget (omegaHessT c tc) a b)
      (fun b hb => mem_mul (mem_pt _) (mem_Hget hsh hr hzh hη ha hb))
    rwa [zero_add] at this
  have := mem_foldl_add (n := NV) (a := 0) mem_zero
    (f := fun a => ∑ b ∈ range NV, ((tc.vi a * tc.vi b : ℚ) : ℝ) * WhessN c tc.a36 η a b)
    (g := fun a => vHvRow tc (omegaHessT c tc) a) hrow
  rw [zero_add] at this
  rw [rng_eq]
  refine le_trans (le_of_eq ?_) (mem_mag this)
  congr 1
  rw [sum_range_NV_eq]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [sum_range_NV_eq]
  refine Finset.sum_congr rfl fun j _ => ?_
  rw [WhessN_fin]
  unfold vR
  push_cast
  ring

theorem abs_hvCol (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η)
    (b : Fin NV) :
    |∑ a : Fin NV, vR tc a * Whess c tc.a36 η a b| ≤ ((hvCol tc (omegaHessT c tc) b : ℚ) : ℝ) := by
  unfold hvCol
  rw [rng_eq]
  have := mem_foldl_add (n := NV) (a := 0) mem_zero
    (f := fun a => ((tc.vi a : ℚ) : ℝ) * WhessN c tc.a36 η a b)
    (g := fun a => IV.pt (tc.vi a) * Hget (omegaHessT c tc) a b)
    (fun a ha => mem_mul (mem_pt _) (mem_Hget hsh hr hzh hη ha b.isLt))
  rw [zero_add] at this
  refine le_trans (le_of_eq ?_) (mem_mag this)
  congr 1
  rw [sum_range_NV_eq]
  refine Finset.sum_congr rfl fun a _ => ?_
  rw [WhessN_fin]
  rfl

theorem abs_hvRow (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η)
    (a : Fin NV) :
    |∑ b : Fin NV, Whess c tc.a36 η a b * vR tc b| ≤ ((hvRow tc (omegaHessT c tc) a : ℚ) : ℝ) := by
  unfold hvRow
  rw [rng_eq]
  have := mem_foldl_add (n := NV) (a := 0) mem_zero
    (f := fun b => WhessN c tc.a36 η a b * ((tc.vi b : ℚ) : ℝ))
    (g := fun b => Hget (omegaHessT c tc) a b * IV.pt (tc.vi b))
    (fun b hb => mem_mul (mem_Hget hsh hr hzh hη a.isLt hb) (mem_pt _))
  rw [zero_add] at this
  refine le_trans (le_of_eq ?_) (mem_mag this)
  congr 1
  rw [sum_range_NV_eq]
  refine Finset.sum_congr rfl fun b _ => ?_
  rw [WhessN_fin]
  rfl

theorem abs_hMag (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η)
    (a b : Fin NV) :
    |Whess c tc.a36 η a b| ≤ ((hMag (omegaHessT c tc) a b : ℚ) : ℝ) :=
  mem_mag (mem_omegaHessT hsh hr hzh hη a b)

/-! ### The abstract split bound -/

theorem split_identity (H : Fin NV → Fin NV → ℝ) (v w : Vec) (t : ℝ) :
    ∑ j, ∑ i, H i j * (-t * v i + w i) * (-t * v j + w j)
      = ∑ j, ∑ i, t ^ 2 * (v i * v j * H i j) - ∑ j, ∑ i, t * (v i * H i j * w j)
        - ∑ j, ∑ i, t * (H i j * v j * w i) + ∑ j, ∑ i, H i j * w i * w j := by
  have e : ∀ i j, H i j * (-t * v i + w i) * (-t * v j + w j)
      = t ^ 2 * (v i * v j * H i j) - t * (v i * H i j * w j) - t * (H i j * v j * w i)
        + H i j * w i * w j := by intros; ring
  simp only [e, Finset.sum_add_distrib, Finset.sum_sub_distrib]

theorem split_bound_abstract (H : Fin NV → Fin NV → ℝ) (v w : Vec) {t : ℝ} (ht0 : 0 ≤ t)
    {Q : ℝ} {HC HR : Fin NV → ℝ} {HM : Fin NV → Fin NV → ℝ}
    (hQ : |∑ i, ∑ j, v i * v j * H i j| ≤ Q)
    (hHC : ∀ b, |∑ a, v a * H a b| ≤ HC b) (hHR : ∀ a, |∑ b, H a b * v b| ≤ HR a)
    (hHM : ∀ a b, |H a b| ≤ HM a b)
    {tb : ℝ} (htb : t ≤ tb) {wb : Fin NV → ℝ} (hwb : ∀ k, |w k| ≤ wb k) (hwb0 : ∀ k, 0 ≤ wb k)
    (hHC0 : ∀ b, 0 ≤ HC b) (hHR0 : ∀ a, 0 ≤ HR a) (hQ0 : 0 ≤ Q) :
    |∑ j, ∑ i, H i j * (-t * v i + w i) * (-t * v j + w j)|
      ≤ tb * tb * Q + tb * ∑ b, HC b * wb b + tb * ∑ a, HR a * wb a
        + ∑ a, ∑ b, HM a b * wb a * wb b := by
  rw [split_identity]
  have htb0 : 0 ≤ tb := le_trans ht0 htb
  -- term A
  have hA : |∑ j, ∑ i, t ^ 2 * (v i * v j * H i j)| ≤ tb * tb * Q := by
    have e : ∑ j, ∑ i, t ^ 2 * (v i * v j * H i j) = t ^ 2 * ∑ i, ∑ j, v i * v j * H i j := by
      rw [Finset.mul_sum]
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl fun i _ => ?_
      rw [Finset.mul_sum]
    rw [e, abs_mul, abs_of_nonneg (by positivity)]
    calc t ^ 2 * |∑ i, ∑ j, v i * v j * H i j| ≤ t ^ 2 * Q :=
          mul_le_mul_of_nonneg_left hQ (by positivity)
      _ ≤ tb * tb * Q := by
          have : t ^ 2 ≤ tb * tb := by nlinarith
          exact mul_le_mul_of_nonneg_right this hQ0
  -- term B
  have hB : |∑ j, ∑ i, t * (v i * H i j * w j)| ≤ tb * ∑ b, HC b * wb b := by
    have e : ∑ j, ∑ i, t * (v i * H i j * w j) = t * ∑ j, (∑ i, v i * H i j) * w j := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun j _ => ?_
      rw [Finset.sum_mul, Finset.mul_sum]
    rw [e, abs_mul, abs_of_nonneg ht0]
    have h1 : |∑ j, (∑ i, v i * H i j) * w j| ≤ ∑ j, HC j * wb j := by
      refine (Finset.abs_sum_le_sum_abs _ _).trans (Finset.sum_le_sum fun j _ => ?_)
      rw [abs_mul]
      exact mul_le_mul (hHC j) (hwb j) (abs_nonneg _) (hHC0 j)
    have h2 : 0 ≤ ∑ j, HC j * wb j := Finset.sum_nonneg fun j _ => mul_nonneg (hHC0 j) (hwb0 j)
    calc t * |∑ j, (∑ i, v i * H i j) * w j| ≤ t * ∑ j, HC j * wb j :=
          mul_le_mul_of_nonneg_left h1 ht0
      _ ≤ tb * ∑ j, HC j * wb j := mul_le_mul_of_nonneg_right htb h2
  -- term C
  have hC : |∑ j, ∑ i, t * (H i j * v j * w i)| ≤ tb * ∑ a, HR a * wb a := by
    have e : ∑ j, ∑ i, t * (H i j * v j * w i) = t * ∑ i, (∑ j, H i j * v j) * w i := by
      rw [Finset.sum_comm, Finset.mul_sum]
      refine Finset.sum_congr rfl fun i _ => ?_
      rw [Finset.sum_mul, Finset.mul_sum]
    rw [e, abs_mul, abs_of_nonneg ht0]
    have h1 : |∑ i, (∑ j, H i j * v j) * w i| ≤ ∑ i, HR i * wb i := by
      refine (Finset.abs_sum_le_sum_abs _ _).trans (Finset.sum_le_sum fun i _ => ?_)
      rw [abs_mul]
      exact mul_le_mul (hHR i) (hwb i) (abs_nonneg _) (hHR0 i)
    have h2 : 0 ≤ ∑ i, HR i * wb i := Finset.sum_nonneg fun i _ => mul_nonneg (hHR0 i) (hwb0 i)
    calc t * |∑ i, (∑ j, H i j * v j) * w i| ≤ t * ∑ i, HR i * wb i :=
          mul_le_mul_of_nonneg_left h1 ht0
      _ ≤ tb * ∑ i, HR i * wb i := mul_le_mul_of_nonneg_right htb h2
  -- term D
  have hD : |∑ j, ∑ i, H i j * w i * w j| ≤ ∑ a, ∑ b, HM a b * wb a * wb b := by
    rw [Finset.sum_comm]
    refine (Finset.abs_sum_le_sum_abs _ _).trans (Finset.sum_le_sum fun a _ => ?_)
    refine (Finset.abs_sum_le_sum_abs _ _).trans (Finset.sum_le_sum fun b _ => ?_)
    rw [abs_mul, abs_mul]
    exact mul_le_mul (mul_le_mul (hHM a b) (hwb a) (abs_nonneg _) (le_trans (abs_nonneg _) (hHM a b)))
      (hwb b) (abs_nonneg _) (mul_nonneg (le_trans (abs_nonneg _) (hHM a b)) (hwb0 a))
  calc |∑ j, ∑ i, t ^ 2 * (v i * v j * H i j) - ∑ j, ∑ i, t * (v i * H i j * w j)
        - ∑ j, ∑ i, t * (H i j * v j * w i) + ∑ j, ∑ i, H i j * w i * w j|
      ≤ |∑ j, ∑ i, t ^ 2 * (v i * v j * H i j)| + |∑ j, ∑ i, t * (v i * H i j * w j)|
        + |∑ j, ∑ i, t * (H i j * v j * w i)| + |∑ j, ∑ i, H i j * w i * w j| := by
          have := abs_add_le (∑ j, ∑ i, t ^ 2 * (v i * v j * H i j) - ∑ j, ∑ i, t * (v i * H i j * w j)
            - ∑ j, ∑ i, t * (H i j * v j * w i)) (∑ j, ∑ i, H i j * w i * w j)
          have h2 := abs_sub (∑ j, ∑ i, t ^ 2 * (v i * v j * H i j) - ∑ j, ∑ i, t * (v i * H i j * w j))
            (∑ j, ∑ i, t * (H i j * v j * w i))
          have h3 := abs_sub (∑ j, ∑ i, t ^ 2 * (v i * v j * H i j)) (∑ j, ∑ i, t * (v i * H i j * w j))
          linarith
    _ ≤ tb * tb * Q + tb * ∑ b, HC b * wb b + tb * ∑ a, HR a * wb a
        + ∑ a, ∑ b, HM a b * wb a * wb b := by linarith

/-! ### The checker's statistics -/

theorem tubeStats_hv (c : A22Cert) (tc : TubeCert) :
    (tubeStats c tc).hv = Array.ofFn (n := NV) fun i => hvMag tc (omegaHessT c tc) i.val := rfl

theorem tubeStats_hm (c : A22Cert) (tc : TubeCert) :
    (tubeStats c tc).hm = Array.ofFn (n := NV) fun a =>
      Array.ofFn (n := NV) fun b => hMag (omegaHessT c tc) a.val b.val := rfl

theorem tubeStats_qvv (c : A22Cert) (tc : TubeCert) :
    (tubeStats c tc).qvv = qvvT tc (omegaHessT c tc) := by
  delta tubeStats
  rfl

theorem getD_ofFn {α : Type} {n : ℕ} (f : Fin n → α) {i : ℕ} (hi : i < n) (d : α) :
    (Array.ofFn f).getD i d = f ⟨i, hi⟩ := by
  have hs : i < (Array.ofFn f).size := by rw [Array.size_ofFn]; exact hi
  rw [getD_of_lt _ hs, Array.getElem_ofFn]

theorem getD_ofFn_ge {α : Type} {n : ℕ} (f : Fin n → α) {i : ℕ} (hi : ¬ i < n) (d : α) :
    (Array.ofFn f).getD i d = d := by
  have hs : ¬ i < (Array.ofFn f).size := by rw [Array.size_ofFn]; exact hi
  rw [getD_of_ge _ hs]

theorem tubeStats_hvi (c : A22Cert) (tc : TubeCert) {i : ℕ} (hi : i < NV) :
    (tubeStats c tc).hvi i = hvMag tc (omegaHessT c tc) i := by
  unfold TubeStats.hvi
  rw [tubeStats_hv, getD_ofFn _ hi]

theorem tubeStats_hmab (c : A22Cert) (tc : TubeCert) {a b : ℕ} (ha : a < NV) (hb : b < NV) :
    (tubeStats c tc).hmab a b = hMag (omegaHessT c tc) a b := by
  unfold TubeStats.hmab
  rw [tubeStats_hm, getD_ofFn _ ha, getD_ofFn _ hb]

theorem tubeStats_hvi_nonneg (c : A22Cert) (tc : TubeCert) (i : ℕ) : 0 ≤ (tubeStats c tc).hvi i := by
  by_cases hi : i < NV
  · rw [tubeStats_hvi c tc hi]
    unfold hvMag hvCol hvRow
    have := mag_nonneg ((rng NV).foldl (fun s a => s + IV.pt (tc.vi a) * Hget (omegaHessT c tc) a i) IV.zero)
    have := mag_nonneg ((rng NV).foldl (fun s b => s + Hget (omegaHessT c tc) i b * IV.pt (tc.vi b)) IV.zero)
    linarith
  · unfold TubeStats.hvi
    rw [tubeStats_hv, getD_ofFn_ge _ hi]

theorem tubeStats_hmab_nonneg (c : A22Cert) (tc : TubeCert) (a b : ℕ) :
    0 ≤ (tubeStats c tc).hmab a b := by
  by_cases ha : a < NV
  · by_cases hb : b < NV
    · rw [tubeStats_hmab c tc ha hb]; exact mag_nonneg _
    · unfold TubeStats.hmab
      rw [tubeStats_hm, getD_ofFn _ ha, getD_ofFn_ge _ hb]
  · unfold TubeStats.hmab
    rw [tubeStats_hm, getD_ofFn_ge _ ha]
    simp

theorem epsW_nonneg (c : A22Cert) (a : A36Cert) (bx : Box) : 0 ≤ epsW c a bx := by
  unfold epsW
  rw [rng_eq, foldl_add_eq_sum, zero_add]
  exact Finset.sum_nonneg fun _ _ => mag_nonneg _

theorem tubeStats_ew_nonneg (c : A22Cert) (tc : TubeCert) : 0 ≤ (tubeStats c tc).ew :=
  epsW_nonneg _ _ _

theorem tubeStats_qvv_nonneg (c : A22Cert) (tc : TubeCert) : 0 ≤ (tubeStats c tc).qvv :=
  mag_nonneg _

theorem tubeStats_keff_nonneg (c : A22Cert) (tc : TubeCert) : 0 ≤ (tubeStats c tc).keff :=
  kappaEff_nonneg c tc.a36

/-- **The split remainder bound on the tube**:
`|Σ_ij H_ij d_i d_j| ≤ 2·(E(x) − ε₀ − ε_w x)` for `d = −t·v + w`, `t ≤ t̄(x)`, `|w| ≤ w̄(x)`. -/
theorem hess_split_bound (hsh : tubeShapeOK tc = true) (hr : rows70OK c = true)
    {zh : Vec} (hzh : InBoxR c c.r0 zh) {η : Vec} (hη : InTube zh (vR tc) tc.T (radR tc) η)
    {t x : ℝ} (ht0 : 0 ≤ t) (hx0 : 0 ≤ x) (htb : t ≤ tbR tc.T tc.rS x) {w : Vec}
    (hwb : ∀ k : Fin NV, |w k| ≤ wbR tc x k) (d : Vec) (hd : ∀ k, d k = -t * vR tc k + w k) :
    |∑ j, ∑ i, Whess c tc.a36 η i j * d i * d j|
      ≤ 2 * (EtubeR tc (tubeStats c tc) x - ((tubeStats c tc).e0 : ℝ)
          - ((tubeStats c tc).ew : ℝ) * x) := by
  have hd' : d = fun k => -t * vR tc k + w k := funext hd
  rw [hd']
  set H := omegaHessT c tc with hH
  have key := split_bound_abstract (fun i j => Whess c tc.a36 η i j) (vR tc) w ht0
    (Q := ((qvvT tc H : ℚ) : ℝ)) (HC := fun b => ((hvCol tc H b : ℚ) : ℝ))
    (HR := fun a => ((hvRow tc H a : ℚ) : ℝ)) (HM := fun a b => ((hMag H a b : ℚ) : ℝ))
    (abs_qvv hsh hr hzh hη) (abs_hvCol hsh hr hzh hη) (abs_hvRow hsh hr hzh hη)
    (abs_hMag hsh hr hzh hη) htb (wb := fun k => wbR tc x k) hwb
    (fun k => wbR_nonneg hsh hx0 k) (fun b => by exact_mod_cast mag_nonneg _)
    (fun a => by exact_mod_cast mag_nonneg _) (by exact_mod_cast mag_nonneg _)
  refine key.trans (le_of_eq ?_)
  unfold EtubeR
  simp only [sum_range_NV_eq]
  have e1 : ∀ i : Fin NV, (((tubeStats c tc).hvi i : ℚ) : ℝ)
      = (((hvCol tc H i : ℚ) : ℝ) + ((hvRow tc H i : ℚ) : ℝ)) / 2 := by
    intro i
    rw [tubeStats_hvi c tc i.isLt]
    unfold hvMag
    push_cast
    rfl
  have e2 : ∀ a b : Fin NV, (((tubeStats c tc).hmab a b : ℚ) : ℝ) = ((hMag H a b : ℚ) : ℝ) := by
    intro a b
    rw [tubeStats_hmab c tc a.isLt b.isLt]
  simp only [e1, e2, tubeStats_qvv]
  have e3 : ∑ i : Fin NV, (((hvCol tc H i : ℚ) : ℝ) + ((hvRow tc H i : ℚ) : ℝ)) / 2 * wbR tc x i
      = (∑ b : Fin NV, ((hvCol tc H b : ℚ) : ℝ) * wbR tc x b
        + ∑ a : Fin NV, ((hvRow tc H a : ℚ) : ℝ) * wbR tc x a) / 2 := by
    rw [← Finset.sum_add_distrib, Finset.sum_div]
    exact Finset.sum_congr rfl fun i _ => by ring
  rw [e3]
  ring

theorem checkTube_parts (h : checkTube c tc = true) :
    tubeShapeOK tc = true ∧ rows70OK c = true ∧ pinsOK c tc.a36 = true ∧ omegaOK tc.a36 = true ∧
    pinsRangeOK tc.a36 = true ∧ anglesSmall (Box.ofArray (tubeArr c tc)) = true ∧
    loadedValidT c tc = true ∧ (tubeStats c tc).beta < 1 ∧
    iterT tc (tubeStats c tc) c.r0 c.rN NMAX_TUBE (tubeStats c tc).xmax = true := by
  simp only [checkTube, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩, h9⟩ := h
  exact ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩

theorem rad_S (tc : TubeCert) : tc.rad S_IDX = tc.rS := by simp [TubeCert.rad]

theorem xmax_bound (c : A22Cert) (tc : TubeCert) (k : Fin NV) :
    tc.T * rabs (tc.vi k) + tc.rad k + 2 * c.r0 ≤ (tubeStats c tc).xmax := by
  simp only [tubeStats]
  rw [rng_eq]
  exact le_foldl_rmax (List.range NV) 0 (fun i => tc.T * rabs (tc.vi i) + tc.rad i + 2 * c.r0) k
    (List.mem_range.mpr k.isLt)

set_option maxHeartbeats 2000000 in
-- one long assembly proof, mirroring `a36_basin` (Taylor + pinning + handover)
/-- **The contraction-tube theorem (A83 T1).** -/
theorem tube_basin (hc : checkA22 c = true) (ht : checkTube c tc = true)
    {z : Vec} (hz : InTube (zhatV c hc) (vR tc) tc.T (radR tc) z) (hf : Feas z) :
    sZ (zhatV c hc) ≤ sZ z ∧ (sZ z = sZ (zhatV c hc) → z = zhatV c hc) := by
  obtain ⟨hsh, hr, hpins, ho, hrange, hang, hlv, hb1, hiter⟩ := checkTube_parts ht
  obtain ⟨hshA, -, -, -, -, -⟩ := checkA22_parts hc
  obtain ⟨hz0, hS, hr0, hr0N, -⟩ := shapeOK_parts hshA
  set a := tc.a36 with ha
  have hP : tc.P.size = NV := pinsOK_size hpins hS
  have hpos : pinsPositive a = true := by
    simp only [omegaOK, Bool.and_eq_true] at ho
    exact ho.1.2
  have hltP : ∀ k ∈ tc.P, k < NEXT3 := by
    simp only [pinsRangeOK, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true_iff_forall_mem] at hrange
    exact hrange.1
  obtain ⟨hT0, -, -, hrS0, -, hvS, -, -⟩ := tubeShape_parts hsh
  -- the objects
  set zh := zhatV c hc with hzh
  have hzhR : InBoxR c c.r0 zh := zhatV_inBoxR hc
  have hzhT : InTube zh (vR tc) tc.T (radR tc) zh := inTube_self hsh zh
  have hzA : MemBox (tubeArr c tc) z := mem_tubeArr hsh hzhR hz
  have hsm : SmallTilt z := smallTilt_of_anglesSmall hang hzA
  have hsmh : SmallTilt zh := zhatV_smallTilt hc
  have hzh0 : MemBox (boxArr c c.r0) zh := zhatV_memBox_r0 hc
  obtain ⟨t, ht0, htT, hw⟩ := id hz
  -- the difference vector, its norm, and the tube decomposition
  set d : Vec := fun k => z k - zh k with hd
  set x : ℝ := dist d 0 with hx
  have hx0 : 0 ≤ x := dist_nonneg
  have hdk : ∀ k, |d k| ≤ x := fun k => by
    have := dist_le_pi_dist d 0 k
    rw [Real.dist_eq, Pi.zero_apply, sub_zero] at this
    exact this
  set w : Vec := fun k => z k - (zh k - t * vR tc k) with hwdef
  have hd_eq : ∀ k, d k = -t * vR tc k + w k := fun k => by simp only [hd, hwdef]; ring
  have hwk : ∀ k, |w k| ≤ radR tc k := hw
  -- `x ≤ X_max`
  have hxmax : x ≤ (((tubeStats c tc).xmax : ℚ) : ℝ) := by
    rw [hx, dist_pi_le_iff (by
      have := xmax_bound c tc sIdx
      have h0 : (0 : ℚ) ≤ tc.T * rabs (tc.vi sIdx) + tc.rad sIdx + 2 * c.r0 := by
        have := rad_nonneg hsh sIdx
        have : (0 : ℚ) ≤ rabs (tc.vi sIdx) := by
          have := rabs_cast (tc.vi sIdx)
          have h := abs_nonneg ((tc.vi sIdx : ℚ) : ℝ)
          rw [← this] at h
          exact_mod_cast h
        nlinarith
      exact_mod_cast le_trans h0 this)]
    intro k
    rw [Real.dist_eq, Pi.zero_apply, sub_zero, hd_eq k]
    have h1 := hwk k
    have h2 : |t * vR tc k| ≤ (tc.T : ℝ) * ((rabs (tc.vi k) : ℚ) : ℝ) := by
      rw [abs_mul, abs_of_nonneg ht0, rabs_cast]
      exact mul_le_mul_of_nonneg_right htT (abs_nonneg _)
    have h3 := xmax_bound c tc k
    have h3' : ((tc.T * rabs (tc.vi k) + tc.rad k + 2 * c.r0 : ℚ) : ℝ) ≤ (((tubeStats c tc).xmax : ℚ) : ℝ) := by
      exact_mod_cast h3
    push_cast at h3'
    have hr0' : (0 : ℝ) < c.r0 := by exact_mod_cast hr0
    unfold radR at h1
    calc |-t * vR tc k + w k| ≤ |-t * vR tc k| + |w k| := abs_add_le _ _
      _ = |t * vR tc k| + |w k| := by rw [neg_mul, abs_neg]
      _ ≤ _ := by linarith
  -- `t ≤ t̄(x)`, `|w_k| ≤ w̄_k(x)`
  have hvS' : vR tc sIdx = 1 := by
    unfold vR
    have : tc.vi sIdx = 1 := hvS
    rw [this]; simp
  have htb : t ≤ tbR tc.T tc.rS x := by
    unfold tbR
    refine le_min htT ?_
    have h1 := abs_le.mp (hdk sIdx)
    have h2 := abs_le.mp (hwk sIdx)
    have e := hd_eq sIdx
    rw [hvS'] at e
    have hrs : radR tc sIdx = (tc.rS : ℝ) := by unfold radR; rw [show (sIdx : ℕ) = S_IDX from rfl, rad_S]
    rw [hrs] at h2
    linarith [h1.1, h1.2, h2.1, h2.2]
  have hwb : ∀ k : Fin NV, |w k| ≤ wbR tc x k := by
    intro k
    unfold wbR
    refine le_min (hwk k) ?_
    have e : w k = d k + t * vR tc k := by rw [hd_eq k]; ring
    rw [e]
    calc |d k + t * vR tc k| ≤ |d k| + |t * vR tc k| := abs_add_le _ _
      _ ≤ x + tbR tc.T tc.rS x * |((tc.vi k : ℚ) : ℝ)| := by
          rw [abs_mul, abs_of_nonneg ht0]
          exact add_le_add (hdk k) (mul_le_mul_of_nonneg_right htb (abs_nonneg _))
  -- W ≥ 0 at z
  have hW0 : 0 ≤ Wfun c a z := W_nonneg_T hsh hr ho hlv hzhR hz hsm hf
  -- the constants
  set st := tubeStats c tc with hst
  set e0 : ℝ := ((st.e0 : ℚ) : ℝ) with he0
  set ew : ℝ := ((st.ew : ℚ) : ℝ) with hew
  set beta : ℝ := ((st.beta : ℚ) : ℝ) with hbeta
  set kap : ℝ := ((st.kap : ℚ) : ℝ) with hkap
  set keff : ℝ := ((st.keff : ℚ) : ℝ) with hkeff
  set gm : ℝ := ((st.gm : ℚ) : ℝ) with hgm
  have he0' : e0 = ((eps0 c a (radBox c.z0 c.r0) : ℚ) : ℝ) := rfl
  have hew' : ew = ((epsW c a (radBox c.z0 c.r0) : ℚ) : ℝ) := rfl
  have hgm' : gm = ((gmax c a (radBox c.z0 c.r0) : ℚ) : ℝ) := rfl
  have hkap' : kap = ((kappa c : ℚ) : ℝ) := rfl
  have hkeff' : keff = ((kappaEff c a : ℚ) : ℝ) := rfl
  have hbeta' : beta = ((betaT c tc : ℚ) : ℝ) := rfl
  have hb1' : beta < 1 := by rw [hbeta]; exact_mod_cast hb1
  have hkeff0 : 0 ≤ keff := by rw [hkeff]; exact_mod_cast tubeStats_keff_nonneg c tc
  have hbeta0 : 0 ≤ beta := by
    rw [hbeta']
    have : (0 : ℚ) ≤ betaT c tc := by
      unfold betaT; rw [rng_eq]; exact foldl_rmax_ge _ _ _
    exact_mod_cast this
  have hkap0 : 0 ≤ kap := by
    rw [hkap']
    have : (0 : ℚ) ≤ kappa c := by
      unfold kappa; rw [rng_eq]; exact foldl_rmax_ge _ _ _
    exact_mod_cast this
  have hgm0 : 0 ≤ gm := by
    rw [hgm']
    have : (0 : ℚ) ≤ gmax c a (radBox c.z0 c.r0) := by
      unfold gmax; rw [← Array.foldl_toList]; exact foldl_rmax_ge _ _ _
    exact_mod_cast this
  have h1b : 0 < 1 - beta := by linarith
  -- Taylor along the segment: `s(z) − s(ẑ) ≥ W(z) − E(x)`
  obtain ⟨θ, hθ, htay⟩ := Wfun_taylor_seg (c := c) (a := a) zh z
  set η := seg zh (fun i => z i - zh i) θ with hη
  have hηT : InTube zh (vR tc) tc.T (radR tc) η := inTube_seg (radR_nonneg hsh) hz hθ.1.le hθ.2.le
  have hWzh : |Wfun c a zh| ≤ e0 := by rw [he0', radBox_eq]; exact abs_W_le_eps0 hzh0
  have hgrad : ∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)| ≤ ew := by
    rw [hew', radBox_eq]; exact sum_abs_grad_le_epsW hr hzh0
  have hds : sZ z - sZ zh = d sIdx := by
    simp only [hd]; rw [sZ_eq, sZ_eq]
  have hgradterm : |∑ j : Fin NV, (Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)) * d j| ≤ ew * x := by
    calc |∑ j : Fin NV, (Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)) * d j|
        ≤ ∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)| * |d j| := by
          refine (Finset.abs_sum_le_sum_abs _ _).trans ?_
          exact sum_le_sum fun j _ => by rw [abs_mul]
      _ ≤ ∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)| * x :=
          sum_le_sum fun j _ => mul_le_mul_of_nonneg_left (hdk j) (abs_nonneg _)
      _ = (∑ j : Fin NV, |Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)|) * x := by
          rw [Finset.sum_mul]
      _ ≤ ew * x := mul_le_mul_of_nonneg_right hgrad hx0
  have hsumgrad : ∑ j : Fin NV, Wgrad c a zh j * d j
      = ∑ j : Fin NV, (Wgrad c a zh j - (if (j : ℕ) = S_IDX then 1 else 0)) * d j + d sIdx := by
    have : ∑ j : Fin NV, (if (j : ℕ) = S_IDX then (1 : ℝ) else 0) * d j = d sIdx := by
      rw [sum_ite_S]; ring
    rw [← this, ← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl fun j _ => by ring
  have hhessterm : |∑ j : Fin NV, ∑ i : Fin NV, Whess c a η i j * d i * d j|
      ≤ 2 * (EtubeR tc st x - e0 - ew * x) :=
    hess_split_bound hsh hr hzhR hηT ht0 hx0 htb hwb d hd_eq
  have hT1 : Wfun c a z - EtubeR tc st x ≤ sZ z - sZ zh := by
    rw [hds]
    have h1 := abs_le.mp hWzh
    have h2 := abs_le.mp hgradterm
    have h3 := abs_le.mp hhessterm
    rw [htay, hsumgrad]
    simp only [hd] at h2 h3 ⊢
    nlinarith [h1.1, h1.2, h2.1, h2.2, h3.1, h3.2]
  -- dichotomy
  by_cases hcase : EtubeR tc st x < Wfun c a z
  · have : sZ zh < sZ z := by linarith
    exact ⟨this.le, fun h => absurd h this.ne'⟩
  · push_neg at hcase
    -- pinning: the mean-value points on the segment, hence in the tube
    choose ξθ hξθ hmvt using fun rr : Fin NV => mvt_seg zh z (e70 c (pinPos a rr))
    set ξ : Fin NV → Vec := fun rr => seg zh (fun i => z i - zh i) (ξθ rr) with hξ
    have hξT : ∀ rr, InTube zh (vR tc) tc.T (radR tc) (ξ rr) := fun rr =>
      inTube_seg (radR_nonneg hsh) hz (hξθ rr).1.le (hξθ rr).2.le
    have hdi : ∀ i : Fin NV, d i
        = ∑ j : Fin NV, ((if i = j then (1 : ℝ) else 0)
            - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j)) * d j
          + ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * (eval z (e70 c (pinPos a rr)) - eval zh (e70 c (pinPos a rr))) := by
      intro i
      have e1 : ∑ j : Fin NV, (if i = j then (1 : ℝ) else 0) * d j = d i := by
        simp [ite_mul, Finset.sum_ite_eq]
      have e2 : ∑ j : Fin NV, (∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * eval (ξ rr) ((e70 c (pinPos a rr)).D j)) * d j
          = ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * (eval z (e70 c (pinPos a rr)) - eval zh (e70 c (pinPos a rr))) := by
        simp only [hmvt, Finset.mul_sum, Finset.sum_mul]
        rw [Finset.sum_comm]
        refine sum_congr rfl fun rr _ => sum_congr rfl fun j _ => by simp only [hd, hξ]; ring
      rw [← e1, ← e2]
      simp only [sub_mul, Finset.sum_sub_distrib]
      ring
    have hrowsum : ∀ i : Fin NV, ∑ j : Fin NV, |(if i = j then (1 : ℝ) else 0)
        - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j)| ≤ beta := by
      intro i
      have h1 := sum_abs_le_betaRow (M := Mrow c.Y (pinJT c tc) i)
        (m := fun j => (if i = j then (1 : ℝ) else 0)
          - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j))
        (fun j => mem_Mrow_pinT hsh hr hP hltP hzhR hξT i j)
      refine h1.trans ?_
      rw [hbeta']
      exact_mod_cast betaRow_le_betaT c tc i
    have hpinz : ∀ rr : Fin NV, 0 ≤ eval z (e70 c (pinPos a rr)) := by
      intro rr
      have hr' : (rr : ℕ) < a.P.size := by rw [ha, a36_P, hP]; exact rr.isLt
      refine loaded_row_nonneg_T hsh hr hlv hzhR hz hsm hf (mem_loaded a ?_ ?_)
      · unfold pinPos; rw [getD_of_lt _ hr']; exact hltP _ (Array.getElem_mem hr')
      · simp only [pinsPositive, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hpos
        unfold pinPos; rw [getD_of_lt _ hr']; exact (hpos.2 rr hr').ne'
    have hYz : ∀ i : Fin NV, |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr))|
        ≤ keff * Wfun c a z := by
      intro i
      calc |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr))|
          ≤ ∑ rr : Fin NV, |((Ymat c.Y i rr : ℚ) : ℝ)| * eval z (e70 c (pinPos a rr)) := by
            refine (Finset.abs_sum_le_sum_abs
              (fun rr : Fin NV => ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr)))
              Finset.univ).trans ?_
            refine sum_le_sum fun rr _ => ?_
            rw [abs_mul, abs_of_nonneg (hpinz rr)]
        _ ≤ ∑ rr : Fin NV, keff * (ωR a (pinPos a rr) * eval z (e70 c (pinPos a rr))) := by
            refine sum_le_sum fun rr _ => ?_
            rw [← mul_assoc]
            refine mul_le_mul_of_nonneg_right ?_ (hpinz rr)
            exact (abs_Y_le_cvec i rr).trans (cvec_le_keff hpos rr)
        _ = keff * ∑ rr : Fin NV, ωR a (pinPos a rr) * eval z (e70 c (pinPos a rr)) := by
            rw [Finset.mul_sum]
        _ ≤ keff * Wfun c a z :=
            mul_le_mul_of_nonneg_left (pin_sum_le_W_T hsh hr ho hlv hpos hrange hzhR hz hsm hf) hkeff0
    have hYzh : ∀ i : Fin NV, |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr))|
        ≤ kap * gm := by
      intro i
      calc |∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr))|
          ≤ ∑ rr : Fin NV, |((Ymat c.Y i rr : ℚ) : ℝ)| * gm := by
            refine (Finset.abs_sum_le_sum_abs
              (fun rr : Fin NV => ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr)))
              Finset.univ).trans ?_
            refine sum_le_sum fun rr _ => ?_
            rw [abs_mul]
            refine mul_le_mul_of_nonneg_left ?_ (abs_nonneg _)
            rw [hgm', radBox_eq]
            exact abs_pin_le_gmax (by rw [ha, a36_P]; exact hP) hzh0 rr
        _ = (∑ rr : Fin NV, |((Ymat c.Y i rr : ℚ) : ℝ)|) * gm := by rw [Finset.sum_mul]
        _ ≤ kap * gm := by
            refine mul_le_mul_of_nonneg_right ?_ hgm0
            rw [hkap']; exact sum_abs_Y_le_kappa i
    -- `x ≤ β x + κ_eff W(z) + κ g_max`
    have hnn : 0 ≤ beta * x + keff * Wfun c a z + kap * gm := by
      have := mul_nonneg hbeta0 hx0
      have := mul_nonneg hkeff0 hW0
      have := mul_nonneg hkap0 hgm0
      linarith
    have hxbound : x ≤ beta * x + keff * Wfun c a z + kap * gm := by
      rw [hx, dist_pi_le_iff hnn]
      intro i
      rw [Real.dist_eq, Pi.zero_apply, sub_zero, hdi i]
      have h1 := abs_le_of_rowsum (hrowsum) d i
      have h2 := hYz i
      have h3 := hYzh i
      have hsplit : ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * (eval z (e70 c (pinPos a rr)) - eval zh (e70 c (pinPos a rr)))
          = ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr))
            - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr)) := by
        rw [← Finset.sum_sub_distrib]; exact sum_congr rfl fun rr _ => by ring
      rw [hsplit]
      set A := ∑ j : Fin NV, ((if i = j then (1 : ℝ) else 0)
        - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j)) * d j
        with hA
      set Bz := ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval z (e70 c (pinPos a rr)) with hBz
      set Bh := ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval zh (e70 c (pinPos a rr)) with hBh
      calc |A + (Bz - Bh)| ≤ |A| + |Bz - Bh| := abs_add_le _ _
        _ ≤ |A| + (|Bz| + |Bh|) := add_le_add le_rfl (abs_sub Bz Bh)
        _ ≤ beta * x + (keff * Wfun c a z + kap * gm) := add_le_add h1 (add_le_add h2 h3)
        _ = beta * x + keff * Wfun c a z + kap * gm := by ring
    -- hence `x ≤ ψ(x)`
    have hxψ : x ≤ psiR tc st x := by
      unfold psiR
      rw [le_div_iff₀ h1b]
      have h5 := mul_le_mul_of_nonneg_left hcase hkeff0
      nlinarith
    -- the monotone iteration hands over to A22
    have hxN : x + (c.r0 : ℝ) ≤ (c.rN : ℝ) :=
      iterT_sound hsh hb1 (tubeStats_keff_nonneg c tc) (tubeStats_ew_nonneg c tc)
        (tubeStats_qvv_nonneg c tc) (tubeStats_hvi_nonneg c tc) (tubeStats_hmab_nonneg c tc)
        hx0 hxψ NMAX_TUBE st.xmax hxmax hiter
    have hzN : MemBox (boxArr c c.rN) z := by
      refine memBox_of_inBoxR hz0 fun k => ?_
      have h1 := hdk k
      have h2 := zhatV_inBoxR hc k
      calc |z k - z0R c k| = |d k + (zh k - z0R c k)| := by simp only [hd]; ring_nf
        _ ≤ |d k| + |zh k - z0R c k| := abs_add_le _ _
        _ ≤ x + (c.r0 : ℝ) := add_le_add h1 h2
        _ ≤ (c.rN : ℝ) := hxN
    exact a22_optimal' hc hzN hsm hf

end

end PackingCert.Rigid
