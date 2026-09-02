import Mathlib.Tactic
import PackingCertMathlib.RigidExpr
import PackingCertMathlib.Attain
import PackingCertMathlib.ThetaT

/-!
# Geometry of the θ-frame configuration space (A79)

A configuration vector `z : Fin 34 → ℝ` (11 × `(cx, cy, θ)` + the side `s`) denotes 11
parametrised squares `sqZ z i = ⟨cx, cy, tan(θ/2)⟩` (so that `edir = (cos θ, sin θ)` —
`ThetaT.lean`'s `cosT_eq_cos`).  This file gives the real meaning of the row language:

* `eval_edgeRow` / `eval_tanE` / `eval_wall` / `eval_dist` — the rows as body-frame
  coordinates `u = e·(q − c)`, `v = e⊥·(q − c)` of corners;
* the VALIDITY lemmas of A22 §1 — for a feasible configuration (interior-disjoint unit
  squares inside `[0, s]²`) every wall and dist row is `≥ 0`, and an edge row is `≥ 0`
  whenever its tangential coordinate is `< ½` in magnitude and its depth `> −½`
  (`wall_valid`, `dist_valid`, `edge_valid`);
* the SEPARATION lemmas used for the feasibility of `ẑ` — four nonnegative corner rows
  against an edge of another square separate the interiors (`disjoint_of_rows`), two
  upright squares at unit centre offset are interior-disjoint (`disjoint_upright`), and
  the exact-structure facts: mate wall rows force `θ = 0` (`theta_zero_of_mates`), the
  corner-on-edge / edge-on-corner pair forces equal angles (`theta_eq_of_pair`), and
  equal angles transport a row from one corner to the other (`row_transfer`).
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set

/-! ## Coordinates -/

def cxZ (z : Vec) (i : ℕ) : ℝ := getV z (3 * i)

def cyZ (z : Vec) (i : ℕ) : ℝ := getV z (3 * i + 1)

def thZ (z : Vec) (i : ℕ) : ℝ := getV z (3 * i + 2)

def sZ (z : Vec) : ℝ := getV z S_IDX

/-- The parametrised square of index `i`. -/
noncomputable def sqZ (z : Vec) (i : ℕ) : PSq := ⟨cxZ z i, cyZ z i, Real.tan (thZ z i / 2)⟩

/-- Body coordinates of a plane point relative to square `i`. -/
noncomputable def uZ (z : Vec) (i : ℕ) (p : RP) : ℝ :=
  Real.cos (thZ z i) * (p.1 - cxZ z i) + Real.sin (thZ z i) * (p.2 - cyZ z i)

noncomputable def vZ (z : Vec) (i : ℕ) (p : RP) : ℝ :=
  -Real.sin (thZ z i) * (p.1 - cxZ z i) + Real.cos (thZ z i) * (p.2 - cyZ z i)

/-- Corner `k` of square `i`. -/
noncomputable def cornerP (z : Vec) (i k : ℕ) : RP := (eval z (cornerX i k), eval z (cornerY i k))

/-- Feasibility: the 11 squares form a packing at side `s = z_33`. -/
def Feas (z : Vec) : Prop := IsPacking 11 (sZ z) fun i : Fin 11 => (sqZ z i).set

/-- All tilts are small (the boxes have `|θ| ≤ 1`). -/
def SmallTilt (z : Vec) : Prop := ∀ i, i < 11 → |thZ z i| ≤ 1

theorem thetaOf_tan_half {θ : ℝ} (h : |θ| < Real.pi) : thetaOf (Real.tan (θ / 2)) = θ := by
  unfold thetaOf
  have := abs_lt.mp h
  rw [Real.arctan_tan (by linarith) (by linarith)]
  ring

theorem abs_lt_pi_of_le_one {θ : ℝ} (h : |θ| ≤ 1) : |θ| < Real.pi := by
  linarith [Real.pi_gt_three]

theorem edir_sqZ {z : Vec} {i : ℕ} (h : |thZ z i| < Real.pi) :
    edir (sqZ z i) = (Real.cos (thZ z i), Real.sin (thZ z i)) := by
  simp only [edir, sqZ, cosT_eq_cos, sinT_eq_sin, thetaOf_tan_half h]

theorem rdot_edir_sqZ {z : Vec} {i : ℕ} (h : |thZ z i| < Real.pi) (p : RP) :
    rdot (p.1 - (sqZ z i).cx, p.2 - (sqZ z i).cy) (edir (sqZ z i)) = uZ z i p := by
  rw [edir_sqZ h]; simp [rdot, uZ, sqZ]; ring

theorem rdot_perp_sqZ {z : Vec} {i : ℕ} (h : |thZ z i| < Real.pi) (p : RP) :
    rdot (p.1 - (sqZ z i).cx, p.2 - (sqZ z i).cy) (perpV (edir (sqZ z i))) = vZ z i p := by
  rw [edir_sqZ h]; simp [rdot, vZ, sqZ, perpV]; ring

theorem mem_sqZ_iff {z : Vec} {i : ℕ} (h : |thZ z i| < Real.pi) (p : RP) :
    p ∈ (sqZ z i).set ↔ |uZ z i p| ≤ 1 / 2 ∧ |vZ z i p| ≤ 1 / 2 := by
  rw [mem_set_iff_uv, rdot_edir_sqZ h, rdot_perp_sqZ h]

theorem mem_interior_sqZ_iff {z : Vec} {i : ℕ} (h : |thZ z i| < Real.pi) (p : RP) :
    p ∈ interior (sqZ z i).set ↔ |uZ z i p| < 1 / 2 ∧ |vZ z i p| < 1 / 2 := by
  rw [mem_interior_iff_uv, rdot_edir_sqZ h, rdot_perp_sqZ h]

/-! ## The rows, in body coordinates -/

theorem cornerP_fst (z : Vec) (i k : ℕ) :
    (cornerP z i k).1 = cxZ z i + (hx k : ℝ) * Real.cos (thZ z i) - (hy k : ℝ) * Real.sin (thZ z i) := by
  simp [cornerP, eval, cornerX, cxZ, thZ]; ring

theorem cornerP_snd (z : Vec) (i k : ℕ) :
    (cornerP z i k).2 = cyZ z i + (hx k : ℝ) * Real.sin (thZ z i) + (hy k : ℝ) * Real.cos (thZ z i) := by
  simp [cornerP, eval, cornerY, cyZ, thZ]; ring

theorem uZ_corner (z : Vec) (i k : ℕ) : uZ z i (cornerP z i k) = (hx k : ℝ) := by
  simp only [uZ, cornerP_fst, cornerP_snd]
  linear_combination (hx k : ℝ) * Real.cos_sq_add_sin_sq (thZ z i)

theorem vZ_corner (z : Vec) (i k : ℕ) : vZ z i (cornerP z i k) = (hy k : ℝ) := by
  simp only [vZ, cornerP_fst, cornerP_snd]
  linear_combination (hy k : ℝ) * Real.cos_sq_add_sin_sq (thZ z i)

theorem abs_hx (k : ℕ) : |(hx k : ℝ)| = 1 / 2 := by
  unfold hx; split_ifs <;> norm_num

theorem abs_hy (k : ℕ) : |(hy k : ℝ)| = 1 / 2 := by
  unfold hy; split_ifs <;> norm_num

theorem cornerP_mem {z : Vec} {i : ℕ} (h : |thZ z i| < Real.pi) (k : ℕ) :
    cornerP z i k ∈ (sqZ z i).set := by
  rw [mem_sqZ_iff h, uZ_corner, vZ_corner, abs_hx, abs_hy]
  exact ⟨le_rfl, le_rfl⟩

/-- The normal vector of edge `e` of square `j` (real). -/
noncomputable def normV (z : Vec) (j e : ℕ) : RP := (eval z (normX j e), eval z (normY j e))

theorem normV_eq (z : Vec) (j e : ℕ) :
    normV z j e = ((nhx e : ℝ) * Real.cos (thZ z j) - (nhy e : ℝ) * Real.sin (thZ z j),
      (nhx e : ℝ) * Real.sin (thZ z j) + (nhy e : ℝ) * Real.cos (thZ z j)) := by
  simp only [normV, eval, normX, normY, thZ, Prod.mk.injEq]
  constructor <;> ring

/-- `n·(p − c_j) = nhx·u + nhy·v`. -/
theorem rdot_normV (z : Vec) (j e : ℕ) (p : RP) :
    rdot (p.1 - cxZ z j, p.2 - cyZ z j) (normV z j e)
      = (nhx e : ℝ) * uZ z j p + (nhy e : ℝ) * vZ z j p := by
  rw [normV_eq]; simp only [rdot, uZ, vZ]; ring

theorem eval_depE (z : Vec) (i k j e : ℕ) :
    eval z (depE i k j e)
      = (nhx e : ℝ) * uZ z j (cornerP z i k) + (nhy e : ℝ) * vZ z j (cornerP z i k) := by
  have := rdot_normV z j e (cornerP z i k)
  simp only [rdot, normV] at this
  rw [← this]
  simp only [eval, depE, cornerP, cxZ, cyZ]
  ring

theorem eval_edgeRow (z : Vec) (i k j e : ℕ) :
    eval z (edgeRow i k j e)
      = (nhx e : ℝ) * uZ z j (cornerP z i k) + (nhy e : ℝ) * vZ z j (cornerP z i k) - 1 / 2 := by
  simp only [edgeRow, eval, eval_depE]
  push_cast; ring

theorem eval_tanE (z : Vec) (i k j e : ℕ) :
    eval z (tanE i k j e)
      = (nhx e : ℝ) * vZ z j (cornerP z i k) - (nhy e : ℝ) * uZ z j (cornerP z i k) := by
  simp only [tanE, eval, normX, normY, cornerX, cornerY, uZ, vZ, cornerP_fst, cornerP_snd, cxZ, cyZ, thZ]
  ring

theorem eval_wall (z : Vec) (i k w : ℕ) :
    eval z (rowExpr (.wall i k w))
      = if w = 0 then (cornerP z i k).1 else if w = 1 then (cornerP z i k).2
        else if w = 2 then sZ z - (cornerP z i k).1 else sZ z - (cornerP z i k).2 := by
  simp only [rowExpr, cornerP, sZ]
  split_ifs <;> simp [eval]

theorem eval_dist (z : Vec) (i j : ℕ) :
    eval z (rowExpr (.dist i j)) = (cxZ z i - cxZ z j) ^ 2 + (cyZ z i - cyZ z j) ^ 2 - 1 := by
  simp [rowExpr, eval, cxZ, cyZ]; ring

theorem eval_angeq (z : Vec) (i j : ℕ) : eval z (rowExpr (.angeq i j)) = thZ z i - thZ z j := by
  simp [rowExpr, eval, thZ]

/-- The four axis normals. -/
theorem nh_cases (e : ℕ) (he : e < 4) :
    ((nhx e : ℝ) = 0 ∧ (nhy e : ℝ) = -1) ∨ ((nhx e : ℝ) = 1 ∧ (nhy e : ℝ) = 0) ∨
    ((nhx e : ℝ) = 0 ∧ (nhy e : ℝ) = 1) ∨ ((nhx e : ℝ) = -1 ∧ (nhy e : ℝ) = 0) := by
  interval_cases e <;> simp [nhx, nhy]

/-! ## Validity lemmas (A22 §1) -/

theorem feas_contained {z : Vec} (hf : Feas z) {i : ℕ} (hi : i < 11) :
    (sqZ z i).set ⊆ container (sZ z) := hf.contained ⟨i, hi⟩

theorem feas_disjoint {z : Vec} (hf : Feas z) {i j : ℕ} (hi : i < 11) (hj : j < 11) (hij : i ≠ j) :
    Disjoint (interior (sqZ z i).set) (interior (sqZ z j).set) :=
  hf.interiorDisjoint ⟨i, hi⟩ ⟨j, hj⟩ (fun h => hij (Fin.mk.inj_iff.mp h))

/-- Wall rows of a feasible configuration are nonnegative. -/
theorem wall_valid {z : Vec} (hf : Feas z) {i : ℕ} (hi : i < 11) (hθ : |thZ z i| < Real.pi)
    (k w : ℕ) : 0 ≤ eval z (rowExpr (.wall i k w)) := by
  have hmem := feas_contained hf hi (cornerP_mem hθ k)
  simp only [container, mem_prod, mem_Icc] at hmem
  rw [eval_wall]
  split_ifs <;> linarith [hmem.1.1, hmem.1.2, hmem.2.1, hmem.2.2]

/-- `|u|² + |v|² = |p − c|²` (orthonormal body frame). -/
theorem uZ_sq_add_vZ_sq (z : Vec) (i : ℕ) (p : RP) :
    uZ z i p ^ 2 + vZ z i p ^ 2 = (p.1 - cxZ z i) ^ 2 + (p.2 - cyZ z i) ^ 2 := by
  simp only [uZ, vZ]
  linear_combination ((p.1 - cxZ z i) ^ 2 + (p.2 - cyZ z i) ^ 2) * Real.cos_sq_add_sin_sq (thZ z i)

/-- A point at Euclidean distance `< ½` from the centre is interior. -/
theorem mem_interior_of_close {z : Vec} {i : ℕ} (hθ : |thZ z i| < Real.pi) {p : RP}
    (h : (p.1 - cxZ z i) ^ 2 + (p.2 - cyZ z i) ^ 2 < 1 / 4) : p ∈ interior (sqZ z i).set := by
  rw [mem_interior_sqZ_iff hθ]
  have := uZ_sq_add_vZ_sq z i p
  constructor
  · rw [abs_lt]; constructor <;> nlinarith [sq_nonneg (vZ z i p)]
  · rw [abs_lt]; constructor <;> nlinarith [sq_nonneg (uZ z i p)]

/-- Dist rows of a feasible configuration are nonnegative (interior-disjoint unit squares
have centre distance `≥ 1`: otherwise the midpoint is interior to both). -/
theorem dist_valid {z : Vec} (hf : Feas z) {i j : ℕ} (hi : i < 11) (hj : j < 11) (hij : i ≠ j)
    (hθi : |thZ z i| < Real.pi) (hθj : |thZ z j| < Real.pi) :
    0 ≤ eval z (rowExpr (.dist i j)) := by
  rw [eval_dist]
  by_contra hlt
  push_neg at hlt
  set m : RP := ((cxZ z i + cxZ z j) / 2, (cyZ z i + cyZ z j) / 2) with hm
  have hmi : m ∈ interior (sqZ z i).set := by
    refine mem_interior_of_close hθi ?_
    simp only [hm]; nlinarith
  have hmj : m ∈ interior (sqZ z j).set := by
    refine mem_interior_of_close hθj ?_
    simp only [hm]; nlinarith
  exact Set.disjoint_left.mp (feas_disjoint hf hi hj hij) hmi hmj

/-- `|a·b|² ≤ |a|²|b|²` in the plane. -/
theorem dot_sq_le (a1 a2 b1 b2 : ℝ) : (a1 * b1 + a2 * b2) ^ 2 ≤ (a1 ^ 2 + a2 ^ 2) * (b1 ^ 2 + b2 ^ 2) := by
  nlinarith [sq_nonneg (a1 * b2 - a2 * b1)]

/-- The corner `k` of square `i`, pulled inward by `ε` along the diagonal, is interior to
square `i` and at body-frame distance `≤ ε` from the corner in EVERY other frame. -/
theorem edge_valid {z : Vec} (hf : Feas z) {i j : ℕ} (hi : i < 11) (hj : j < 11) (hij : i ≠ j)
    (hθi : |thZ z i| < Real.pi) (hθj : |thZ z j| < Real.pi) (k e : ℕ) (he : e < 4)
    (htan : |eval z (tanE i k j e)| < 1 / 2) (hdep : -1 / 2 < eval z (depE i k j e)) :
    0 ≤ eval z (edgeRow i k j e) := by
  rw [eval_edgeRow]
  by_contra hlt
  push_neg at hlt
  rw [eval_tanE] at htan
  rw [eval_depE] at hdep
  set q := cornerP z i k with hq
  set u := uZ z j q with hu
  set v := vZ z j q with hv
  -- both body coordinates of the corner relative to `j` are `< ½` in magnitude
  have huv : |u| < 1 / 2 ∧ |v| < 1 / 2 := by
    rcases nh_cases e he with ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
      rw [h1, h2] at hlt hdep htan <;> simp only [zero_mul, one_mul, neg_one_mul,
        zero_add, add_zero, zero_sub, sub_zero, neg_neg] at hlt hdep htan <;>
      have ht := abs_lt.mp htan <;>
      exact ⟨abs_lt.mpr ⟨by linarith, by linarith⟩, abs_lt.mpr ⟨by linarith, by linarith⟩⟩
  -- push the corner inward: `q' = c_i + (1 − ε)·R(θ_i) h_k`
  set δ : ℝ := 1 / 2 - max |u| |v| with hδ
  have hδpos : 0 < δ := by
    rw [hδ]; have := max_lt huv.1 huv.2; linarith
  set ε : ℝ := δ / 2 with hε
  have hε0 : 0 < ε := by positivity
  have hε1 : ε < 1 := by
    have : (0 : ℝ) ≤ max |u| |v| := le_trans (abs_nonneg u) (le_max_left _ _)
    rw [hε, hδ]; linarith
  set q' : RP := (cxZ z i + (1 - ε) * ((hx k : ℝ) * Real.cos (thZ z i) - (hy k : ℝ) * Real.sin (thZ z i)),
    cyZ z i + (1 - ε) * ((hx k : ℝ) * Real.sin (thZ z i) + (hy k : ℝ) * Real.cos (thZ z i))) with hq'
  -- `q'` is interior to square `i`
  have hq'i : q' ∈ interior (sqZ z i).set := by
    rw [mem_interior_sqZ_iff hθi]
    have hu' : uZ z i q' = (1 - ε) * (hx k : ℝ) := by
      simp only [uZ, hq']
      linear_combination (1 - ε) * (hx k : ℝ) * Real.cos_sq_add_sin_sq (thZ z i)
    have hv' : vZ z i q' = (1 - ε) * (hy k : ℝ) := by
      simp only [vZ, hq']
      linear_combination (1 - ε) * (hy k : ℝ) * Real.cos_sq_add_sin_sq (thZ z i)
    rw [hu', hv', abs_mul, abs_mul, abs_hx, abs_hy, abs_of_pos (by linarith : (0 : ℝ) < 1 - ε)]
    constructor <;> nlinarith
  -- `q'` is interior to square `j`: its body coordinates moved by at most `ε`
  have hq'j : q' ∈ interior (sqZ z j).set := by
    rw [mem_interior_sqZ_iff hθj]
    -- `q' − q = −ε·R(θ_i) h_k`, a vector of length `ε/√2`
    have hdx : q'.1 - q.1 = -ε * ((hx k : ℝ) * Real.cos (thZ z i) - (hy k : ℝ) * Real.sin (thZ z i)) := by
      simp only [hq', hq, cornerP_fst]; ring
    have hdy : q'.2 - q.2 = -ε * ((hx k : ℝ) * Real.sin (thZ z i) + (hy k : ℝ) * Real.cos (thZ z i)) := by
      simp only [hq', hq, cornerP_snd]; ring
    have hlen : ((hx k : ℝ) * Real.cos (thZ z i) - (hy k : ℝ) * Real.sin (thZ z i)) ^ 2
        + ((hx k : ℝ) * Real.sin (thZ z i) + (hy k : ℝ) * Real.cos (thZ z i)) ^ 2 = 1 / 2 := by
      have h1 : (hx k : ℝ) ^ 2 = 1 / 4 := by
        have := abs_hx k; rw [← sq_abs, this]; norm_num
      have h2 : (hy k : ℝ) ^ 2 = 1 / 4 := by
        have := abs_hy k; rw [← sq_abs, this]; norm_num
      linear_combination ((hx k : ℝ) ^ 2 + (hy k : ℝ) ^ 2) * Real.cos_sq_add_sin_sq (thZ z i)
        + h1 + h2
    have hcs := Real.cos_sq_add_sin_sq (thZ z j)
    -- `u' − u` and `v' − v` are dot products with a unit vector
    have hdu : uZ z j q' - u = Real.cos (thZ z j) * (q'.1 - q.1) + Real.sin (thZ z j) * (q'.2 - q.2) := by
      simp only [hu, uZ]; ring
    have hdv : vZ z j q' - v = -Real.sin (thZ z j) * (q'.1 - q.1) + Real.cos (thZ z j) * (q'.2 - q.2) := by
      simp only [hv, vZ]; ring
    set A := (hx k : ℝ) * Real.cos (thZ z i) - (hy k : ℝ) * Real.sin (thZ z i) with hA
    set B := (hx k : ℝ) * Real.sin (thZ z i) + (hy k : ℝ) * Real.cos (thZ z i) with hB
    have hbu : |uZ z j q' - u| ≤ ε := by
      rw [hdu, hdx, hdy]
      have h1 := dot_sq_le (Real.cos (thZ z j)) (Real.sin (thZ z j)) A B
      have h2 := mul_le_mul_of_nonneg_left h1 (sq_nonneg ε)
      rw [hcs, hlen] at h2
      have h3 : (Real.cos (thZ z j) * (-ε * A) + Real.sin (thZ z j) * (-ε * B)) ^ 2
          = ε ^ 2 * (Real.cos (thZ z j) * A + Real.sin (thZ z j) * B) ^ 2 := by ring
      have hX : (Real.cos (thZ z j) * (-ε * A) + Real.sin (thZ z j) * (-ε * B)) ^ 2 ≤ ε ^ 2 := by
        rw [h3]; have h4 := sq_nonneg ε; linarith
      exact abs_le.mpr (abs_le_of_sq_le_sq' hX hε0.le)
    have hbv : |vZ z j q' - v| ≤ ε := by
      rw [hdv, hdx, hdy]
      have hcs' : (-Real.sin (thZ z j)) ^ 2 + Real.cos (thZ z j) ^ 2 = 1 := by
        rw [neg_sq]; linarith
      have h1 := dot_sq_le (-Real.sin (thZ z j)) (Real.cos (thZ z j)) A B
      have h2 := mul_le_mul_of_nonneg_left h1 (sq_nonneg ε)
      rw [hcs', hlen] at h2
      have h3 : (-Real.sin (thZ z j) * (-ε * A) + Real.cos (thZ z j) * (-ε * B)) ^ 2
          = ε ^ 2 * (-Real.sin (thZ z j) * A + Real.cos (thZ z j) * B) ^ 2 := by ring
      have hX : (-Real.sin (thZ z j) * (-ε * A) + Real.cos (thZ z j) * (-ε * B)) ^ 2 ≤ ε ^ 2 := by
        rw [h3]; have h4 := sq_nonneg ε; linarith
      exact abs_le.mpr (abs_le_of_sq_le_sq' hX hε0.le)
    have hmu : |u| ≤ max |u| |v| := le_max_left _ _
    have hmv : |v| ≤ max |u| |v| := le_max_right _ _
    have hmax : max |u| |v| < 1 / 2 := max_lt huv.1 huv.2
    constructor
    · calc |uZ z j q'| = |u + (uZ z j q' - u)| := by ring_nf
        _ ≤ |u| + |uZ z j q' - u| := abs_add_le _ _
        _ < 1 / 2 := by linarith [hbu, hmu, hmax, hε, hδ]
    · calc |vZ z j q'| = |v + (vZ z j q' - v)| := by ring_nf
        _ ≤ |v| + |vZ z j q' - v| := abs_add_le _ _
        _ < 1 / 2 := by linarith [hbv, hmv, hmax, hε, hδ]
  exact Set.disjoint_left.mp (feas_disjoint hf hi hj hij) hq'i hq'j

/-! ## Separation lemmas -/

/-- Corners of square `p` in the parametrisation of `sqZ`. -/
theorem cornerP_eq_aff {z : Vec} {p : ℕ} (hθ : |thZ z p| < Real.pi) :
    cornerP z p 0 = aff (baseCorner (sqZ z p)) (edir (sqZ z p)) 0 0 ∧
    cornerP z p 1 = aff (baseCorner (sqZ z p)) (edir (sqZ z p)) 1 0 ∧
    cornerP z p 2 = aff (baseCorner (sqZ z p)) (edir (sqZ z p)) 1 1 ∧
    cornerP z p 3 = aff (baseCorner (sqZ z p)) (edir (sqZ z p)) 0 1 := by
  have he := edir_sqZ hθ
  have hb : baseCorner (sqZ z p) = (cxZ z p - (Real.cos (thZ z p) - Real.sin (thZ z p)) / 2,
      cyZ z p - (Real.cos (thZ z p) + Real.sin (thZ z p)) / 2) := by
    simp only [baseCorner, sqZ, cosT_eq_cos, sinT_eq_sin, thetaOf_tan_half hθ]
  refine ⟨?_, ?_, ?_, ?_⟩ <;>
    (apply Prod.ext <;> simp only [cornerP_fst, cornerP_snd, aff, hb, he, hx, hy] <;> norm_num <;> ring)

/-- If the four corner rows of `p` against edge `e` of `o` are nonnegative, the interiors
of `p` and `o` are disjoint (`p` lies on the outer side of the edge line of `o`). -/
theorem disjoint_of_rows {z : Vec} {p o e : ℕ} (hθp : |thZ z p| < Real.pi) (hθo : |thZ z o| < Real.pi)
    (he : e < 4) (hrows : ∀ k, k < 4 → 0 ≤ eval z (edgeRow p k o e)) :
    Disjoint (interior (sqZ z p).set) (interior (sqZ z o).set) := by
  rw [Set.disjoint_left]
  intro x hxp hxo
  -- lower bound on `n·x` over square `p` (convexity from the corners)
  have hcorner : ∀ k, k < 4 → rdot (cornerP z p k) (normV z o e) ≥ rdot (cxZ z o, cyZ z o) (normV z o e) + 1 / 2 := by
    intro k hk
    have h := hrows k hk
    rw [eval_edgeRow] at h
    have := rdot_normV z o e (cornerP z p k)
    simp only [rdot] at this ⊢
    nlinarith [this]
  obtain ⟨c0, c1, c2, c3⟩ := cornerP_eq_aff hθp
  have hxp' : x ∈ (sqZ z p).set := interior_subset hxp
  have hlow : rdot (cxZ z o, cyZ z o) (normV z o e) + 1 / 2 ≤ rdot x (normV z o e) := by
    refine sqSet_le_dot ?_ ?_ ?_ ?_ hxp'
    · rw [← c0]; exact hcorner 0 (by norm_num)
    · rw [← c1]; exact hcorner 1 (by norm_num)
    · rw [← c2]; exact hcorner 2 (by norm_num)
    · rw [← c3]; exact hcorner 3 (by norm_num)
  -- strict upper bound over the interior of `o`
  rw [mem_interior_sqZ_iff hθo] at hxo
  have hup := rdot_normV z o e x
  have : rdot x (normV z o e) - rdot (cxZ z o, cyZ z o) (normV z o e)
      = (nhx e : ℝ) * uZ z o x + (nhy e : ℝ) * vZ z o x := by
    rw [← hup]; simp only [rdot]; ring
  have hlt : (nhx e : ℝ) * uZ z o x + (nhy e : ℝ) * vZ z o x < 1 / 2 := by
    rcases nh_cases e he with ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ <;> rw [h1, h2] <;>
      linarith [abs_lt.mp hxo.1, abs_lt.mp hxo.2]
  linarith

/-- Two upright squares whose centres differ by exactly `1` along an axis are
interior-disjoint. -/
theorem disjoint_upright {z : Vec} {i j : ℕ} (hi : thZ z i = 0) (hj : thZ z j = 0)
    (h : |cxZ z i - cxZ z j| = 1 ∨ |cyZ z i - cyZ z j| = 1) :
    Disjoint (interior (sqZ z i).set) (interior (sqZ z j).set) := by
  have hpi := Real.pi_pos
  rw [Set.disjoint_left]
  intro x hxi hxj
  rw [mem_interior_sqZ_iff (by rw [hi]; simpa using hpi)] at hxi
  rw [mem_interior_sqZ_iff (by rw [hj]; simpa using hpi)] at hxj
  simp only [uZ, vZ, hi, hj, Real.cos_zero, Real.sin_zero, one_mul, zero_mul, neg_zero, add_zero,
    zero_add] at hxi hxj
  rcases h with h | h
  · have := abs_lt.mp hxi.1; have := abs_lt.mp hxj.1
    rcases abs_eq (by norm_num : (0:ℝ) ≤ 1) |>.mp h with h' | h' <;> linarith
  · have := abs_lt.mp hxi.2; have := abs_lt.mp hxj.2
    rcases abs_eq (by norm_num : (0:ℝ) ≤ 1) |>.mp h with h' | h' <;> linarith

/-! ## Exact-structure lemmas -/

/-- Mates on a wall: two `S` wall rows of square `i` on the same wall at corners `k` and
`mate w k` force `sin θ_i = 0`. -/
theorem sin_zero_of_mates {z : Vec} {i k w : ℕ} (hk : k < 4) (hw : w < 4)
    (h1 : eval z (rowExpr (.wall i k w)) = 0) (h2 : eval z (rowExpr (.wall i (mate w k) w)) = 0) :
    Real.sin (thZ z i) = 0 := by
  rw [eval_wall] at h1 h2
  interval_cases w <;> interval_cases k <;>
    simp only [mate, mateX, mateY, cornerP_fst, cornerP_snd, hx, hy] at h1 h2 <;> norm_num at h1 h2 <;>
    linarith

theorem theta_zero_of_sin {z : Vec} {i : ℕ} (hθ : |thZ z i| ≤ 1) (h : Real.sin (thZ z i) = 0) :
    thZ z i = 0 := by
  have := abs_le.mp hθ
  have hpi := Real.pi_gt_three
  exact (Real.sin_eq_zero_iff_of_lt_of_lt (by linarith) (by linarith)).mp h

/-- A wall row transfers between corners with the same wall coordinate when `θ_i = 0`. -/
theorem wall_transfer {z : Vec} {i k k' w : ℕ} (hθ : thZ z i = 0)
    (hperp : (wnx w : ℝ) * ((hx k : ℝ) - hx k') + (wny w : ℝ) * ((hy k : ℝ) - hy k') = 0) (hw : w < 4)
    (h : eval z (rowExpr (.wall i k' w)) = 0) : eval z (rowExpr (.wall i k w)) = 0 := by
  rw [eval_wall] at h ⊢
  simp only [cornerP_fst, cornerP_snd, hθ, Real.cos_zero, Real.sin_zero, mul_one, mul_zero,
    sub_zero, add_zero] at h ⊢
  interval_cases w <;> simp only [wnx, wny] at hperp <;> norm_num at hperp h ⊢ <;> linarith

/-- An edge row transfers between corners `k`, `k'` of `p` with `h_k − h_{k'} ⊥ NHAT e` when
`θ_p = θ_o`. -/
theorem row_transfer {z : Vec} {p k k' o e : ℕ} (hθ : thZ z p = thZ z o)
    (hperp : (nhx e : ℝ) * ((hx k : ℝ) - hx k') + (nhy e : ℝ) * ((hy k : ℝ) - hy k') = 0)
    (h : eval z (edgeRow p k' o e) = 0) : eval z (edgeRow p k o e) = 0 := by
  rw [eval_edgeRow] at h ⊢
  have hcs := Real.cos_sq_add_sin_sq (thZ z o)
  have key : (nhx e : ℝ) * uZ z o (cornerP z p k) + (nhy e : ℝ) * vZ z o (cornerP z p k)
      = (nhx e : ℝ) * uZ z o (cornerP z p k') + (nhy e : ℝ) * vZ z o (cornerP z p k')
        + ((nhx e : ℝ) * ((hx k : ℝ) - hx k') + (nhy e : ℝ) * ((hy k : ℝ) - hy k')) := by
    simp only [uZ, vZ, cornerP_fst, cornerP_snd, hθ]
    linear_combination ((nhx e : ℝ) * ((hx k : ℝ) - hx k') + (nhy e : ℝ) * ((hy k : ℝ) - hy k')) * hcs
  rw [key, hperp]
  linarith

/-- The two corners of edge `e` have `NHAT e · h_k = ½`. -/
theorem nh_dot_corner {e k : ℕ} (he : e < 4) (hk : edgeHasCorner e k = true) :
    (nhx e : ℝ) * hx k + (nhy e : ℝ) * hy k = 1 / 2 := by
  simp only [edgeHasCorner, Bool.or_eq_true, decide_eq_true_eq] at hk
  interval_cases e <;> rcases hk with rfl | rfl <;> (try norm_num [nhx, nhy, hx, hy])

/-- The tangential coordinate of an edge endpoint has magnitude `½`. -/
theorem tan_corner_abs {e k : ℕ} (he : e < 4) (hk : edgeHasCorner e k = true) :
    |(nhx e : ℝ) * hy k - (nhy e : ℝ) * hx k| = 1 / 2 := by
  simp only [edgeHasCorner, Bool.or_eq_true, decide_eq_true_eq] at hk
  interval_cases e <;> rcases hk with rfl | rfl <;> (try norm_num [nhx, nhy, hx, hy])

/-- **Equal angles from a corner-on-edge pair** (A22 §3, S-only form).  Row A: corner `k`
of `i` on edge `e` of `j`, strictly inside the edge (tangential margin); row B: corner `k2`
of `j` on edge `e2` of `i`; `k` an endpoint of edge `e2`, `k2` an endpoint of edge `e`;
the two body normals parallel (`NHAT e · NHAT e2 ≠ 0`).  Then `θ_i = θ_j`. -/
theorem theta_eq_of_pair {z : Vec} {i j k e k2 e2 : ℕ} (hθi : |thZ z i| ≤ 1) (hθj : |thZ z j| ≤ 1)
    (he : e < 4) (he2 : e2 < 4) (hk : edgeHasCorner e2 k = true) (hk2 : edgeHasCorner e k2 = true)
    (hpar : (nhx e : ℝ) * nhx e2 + (nhy e : ℝ) * nhy e2 ≠ 0)
    (hA : eval z (edgeRow i k j e) = 0) (hB : eval z (edgeRow j k2 i e2) = 0)
    (htan : |eval z (tanE i k j e)| < 1 / 2) : thZ z i = thZ z j := by
  rw [eval_edgeRow] at hA hB
  rw [eval_tanE] at htan
  -- the body coordinates of `P = corner k of i` in the frame of `j`, and of `Q = corner k2 of j`
  -- in the frame of `i`
  set P := cornerP z i k with hP
  set Q := cornerP z j k2 with hQ
  have hcsi := Real.cos_sq_add_sin_sq (thZ z i)
  have hcsj := Real.cos_sq_add_sin_sq (thZ z j)
  -- `n_j·(P − c_j) = ½` and `n_j·(Q − c_j) = ½`, so `n_j·(P − Q) = 0`; likewise for `n_i`
  have hQj : (nhx e : ℝ) * uZ z j Q + (nhy e : ℝ) * vZ z j Q = 1 / 2 := by
    rw [hQ, uZ_corner, vZ_corner]; exact nh_dot_corner he hk2
  have hPi : (nhx e2 : ℝ) * uZ z i P + (nhy e2 : ℝ) * vZ z i P = 1 / 2 := by
    rw [hP, uZ_corner, vZ_corner]; exact nh_dot_corner he2 hk
  -- normals as vectors
  set nj : RP := ((nhx e : ℝ) * Real.cos (thZ z j) - (nhy e : ℝ) * Real.sin (thZ z j),
    (nhx e : ℝ) * Real.sin (thZ z j) + (nhy e : ℝ) * Real.cos (thZ z j)) with hnj
  set ni : RP := ((nhx e2 : ℝ) * Real.cos (thZ z i) - (nhy e2 : ℝ) * Real.sin (thZ z i),
    (nhx e2 : ℝ) * Real.sin (thZ z i) + (nhy e2 : ℝ) * Real.cos (thZ z i)) with hni
  have hdotj : ∀ p : RP, nj.1 * (p.1 - cxZ z j) + nj.2 * (p.2 - cyZ z j)
      = (nhx e : ℝ) * uZ z j p + (nhy e : ℝ) * vZ z j p := by
    intro p; simp only [hnj, uZ, vZ]; ring
  have hdoti : ∀ p : RP, ni.1 * (p.1 - cxZ z i) + ni.2 * (p.2 - cyZ z i)
      = (nhx e2 : ℝ) * uZ z i p + (nhy e2 : ℝ) * vZ z i p := by
    intro p; simp only [hni, uZ, vZ]; ring
  have hvj : nj.1 * (P.1 - Q.1) + nj.2 * (P.2 - Q.2) = 0 := by
    have h1 := hdotj P; have h2 := hdotj Q
    nlinarith [h1, h2, hA, hQj]
  have hvi : ni.1 * (P.1 - Q.1) + ni.2 * (P.2 - Q.2) = 0 := by
    have h1 := hdoti P; have h2 := hdoti Q
    nlinarith [h1, h2, hB, hPi]
  -- the determinant `det(n_i, n_j) = (a·b)·sin(θ_j − θ_i)` for parallel body axes
  have hdet : ni.1 * nj.2 - ni.2 * nj.1
      = ((nhx e : ℝ) * nhx e2 + (nhy e : ℝ) * nhy e2) * Real.sin (thZ z j - thZ z i)
        + ((nhx e2 : ℝ) * nhy e - (nhy e2 : ℝ) * nhx e) * Real.cos (thZ z j - thZ z i) := by
    simp only [hni, hnj, Real.sin_sub, Real.cos_sub]; ring
  have hdet0 : (nhx e2 : ℝ) * nhy e - (nhy e2 : ℝ) * nhx e = 0 := by
    rcases nh_cases e he with ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
    rcases nh_cases e2 he2 with ⟨h3, h4⟩ | ⟨h3, h4⟩ | ⟨h3, h4⟩ | ⟨h3, h4⟩ <;>
    rw [h1, h2, h3, h4] at hpar ⊢ <;> first | (exfalso; norm_num at hpar; done) | norm_num
  by_cases hPQ : P = Q
  · -- coinciding corners: the tangential coordinate of `P` in `j`'s frame is `±½`
    exfalso
    have : (nhx e : ℝ) * vZ z j P - (nhy e : ℝ) * uZ z j P
        = (nhx e : ℝ) * hy k2 - (nhy e : ℝ) * hx k2 := by
      rw [hPQ, hQ, uZ_corner, vZ_corner]
    rw [this, tan_corner_abs he hk2] at htan
    linarith
  · -- distinct corners: `v = P − Q ≠ 0` is orthogonal to both normals, so `det = 0`
    have hv : P.1 - Q.1 ≠ 0 ∨ P.2 - Q.2 ≠ 0 := by
      by_contra hcon
      push_neg at hcon
      exact hPQ (Prod.ext (by linarith [hcon.1]) (by linarith [hcon.2]))
    have hd0 : ni.1 * nj.2 - ni.2 * nj.1 = 0 := by
      rcases hv with hv | hv
      · have : (ni.1 * nj.2 - ni.2 * nj.1) * (P.1 - Q.1) = 0 := by linear_combination nj.2 * hvi - ni.2 * hvj
        exact (mul_eq_zero.mp this).resolve_right hv
      · have : (ni.1 * nj.2 - ni.2 * nj.1) * (P.2 - Q.2) = 0 := by linear_combination (-nj.1) * hvi + ni.1 * hvj
        exact (mul_eq_zero.mp this).resolve_right hv
    rw [hdet, hdet0, zero_mul, add_zero] at hd0
    have hsin : Real.sin (thZ z j - thZ z i) = 0 := (mul_eq_zero.mp hd0).resolve_left hpar
    have hpi := Real.pi_gt_three
    have h1 := abs_le.mp hθi
    have h2 := abs_le.mp hθj
    have := (Real.sin_eq_zero_iff_of_lt_of_lt (by linarith) (by linarith)).mp hsin
    linarith

end PackingCert.Rigid
