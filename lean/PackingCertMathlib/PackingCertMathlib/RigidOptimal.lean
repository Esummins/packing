import PackingCertMathlib.RigidA22

/-!
# A22 §5: strict local optimality of `ẑ` (A79, rung (b), the optimality half)

`a22_optimal`: every feasible small-tilt configuration `z` of the rounded box
`box(z0, r_N)` with side `s(z) ≤ s(ẑ)` IS `ẑ`.  Proof (A22 §5): for every pin row
`g_k(z) ≥ 0` (validity lemmas) and `g_k(ẑ) = 0`, so by the mean-value theorem on the box
`∇g_k(ξ_k)·d ≥ 0` with `d = z − ẑ`.  Each Farkas certificate `(i, σ)` writes
`σ e_i + ν e_s = Σ_k μ_k ∇g_k(ξ_k) + ρ` with `μ, ν ≥ 0` and `‖ρ‖₁ ≤ β < 1` (the checker's
`farkasL1`, an interval enclosure valid for EVERY choice of the intermediate points);
dotting with `d` gives `σ d_i ≥ −ν(s(z) − s(ẑ)) − β‖d‖_∞ ≥ −β‖d‖_∞` for both signs, hence
`‖d‖_∞ ≤ β‖d‖_∞` and `d = 0`.
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set Finset

section

variable {c : A22Cert}

/-- All rows of `S` are nonnegative at a feasible small-tilt configuration of `N`. -/
theorem rows_nonneg (hc : checkA22 c = true) {z : Vec} (hz : MemBox (boxArr c c.rN) z)
    (hsm : SmallTilt z) (hf : Feas z) (rr : Fin NV) : 0 ≤ eval z (rowE c c.S rr) := by
  obtain ⟨hsh, -, -, hV, -⟩ := checkA22_parts hc
  obtain ⟨-, hS, -, -, -, hSr, hrows, hang⟩ := shapeOK_parts hsh
  have hrr : (rr : ℕ) < c.S.size := by rw [hS]; exact rr.isLt
  have hk := hSr _ (Array.getElem_mem hrr)
  have hmem : c.row c.S[(rr : ℕ)] ∈ c.rows := by
    unfold A22Cert.row
    rw [getD_of_lt _ hk]
    exact Array.getElem_mem hk
  have hrowE : rowE c c.S rr = rowExpr (c.row c.S[(rr : ℕ)]) := by
    simp [rowE, getD_of_lt _ hrr]
  rw [hrowE]
  have hshape := hrows _ hmem
  have hnot := hang _ (Array.getElem_mem hrr)
  rcases hR : c.row c.S[(rr : ℕ)] with ⟨i, k, w⟩ | ⟨i, k, j, e⟩ | ⟨i, j⟩ | ⟨i, j⟩
  · rw [hR] at hshape
    have hs' : i < 11 ∧ k < 4 ∧ w < 4 := hshape
    exact wall_valid hf hs'.1 (abs_lt_pi_of_le_one (hsm i hs'.1)) k w
  · rw [hR] at hshape
    have hs' : i < 11 ∧ k < 4 ∧ j < 11 ∧ e < 4 ∧ i ≠ j := hshape
    obtain ⟨hi, -, hj, he, hij⟩ := hs'
    have hany : c.S.any (fun r => c.row r == Row.edge i k j e) = true :=
      Array.any_eq_true.mpr ⟨rr, hrr, by rw [hR]; exact beq_self_eq_true _⟩
    rw [radBox_eq] at hV
    obtain ⟨ht, hd⟩ := validity_of_any hV hz hany
    exact edge_valid hf hi hj hij (abs_lt_pi_of_le_one (hsm i hi)) (abs_lt_pi_of_le_one (hsm j hj))
      k e he ht hd
  · rw [hR] at hshape
    have hs' : i < 11 ∧ j < 11 ∧ i ≠ j := hshape
    obtain ⟨hi, hj, hij⟩ := hs'
    exact dist_valid hf hi hj hij (abs_lt_pi_of_le_one (hsm i hi)) (abs_lt_pi_of_le_one (hsm j hj))
  · rw [hR] at hnot
    exact absurd hnot id

/-- The interval `acc_j` of `farkasL1` encloses `Σ_r μ_r ∂_j g_r(ξ_r)`. -/
theorem mem_farkas_acc (hsh : Shape c c.S c.Y) {ξ : Fin NV → Vec}
    (hξ : ∀ rr, MemBox (boxArr c c.rN) (ξ rr)) (f : Farkas) (j : Fin NV) :
    Mem (∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ) * eval (ξ rr) ((rowE c c.S rr).D j))
      ((rng NV).foldl (fun s rr => s + IV.pt (f.mu.getD rr 0)
        * ((Jrows c c.S c.rN).getD rr #[]).getD j IV.zero) IV.zero) := by
  rw [rng_eq]
  have := mem_foldl_add (n := NV) (a := 0) mem_zero
    (f := fun rr => ((f.mu.getD rr 0 : ℚ) : ℝ)
      * eval (ξ ⟨rr % NV, Nat.mod_lt _ (by decide)⟩) ((rowE c c.S rr).D j))
    (g := fun rr => IV.pt (f.mu.getD rr 0) * ((Jrows c c.S c.rN).getD rr #[]).getD j IV.zero)
    (fun rr hrr => by
      have hrr' : rr % NV = rr := Nat.mod_eq_of_lt hrr
      have hm := mem_Jrows (r := c.rN) hsh.hS hsh.huses hsh.hSr (hξ ⟨rr, hrr⟩) ⟨rr, hrr⟩ ⟨j, j.isLt⟩
      simp only [hrr'] at hm ⊢
      exact mem_mul (mem_pt _) hm)
  rw [zero_add, sum_range_NV_eq] at this
  have key : (∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ) * eval (ξ rr) ((rowE c c.S rr).D j))
      = ∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ)
          * eval (ξ ⟨(rr : ℕ) % NV, Nat.mod_lt _ (by decide)⟩) ((rowE c c.S rr).D j) := by
    refine sum_congr rfl fun rr _ => ?_
    rw [fin_mod_self]
  rw [key]
  exact this

/-- The real target vector of a certificate: `σ e_i + ν e_s`. -/
noncomputable def tgt (f : Farkas) (j : Fin NV) : ℝ :=
  (if (j : ℕ) = f.i then (f.sigma : ℝ) else 0) + (if (j : ℕ) = S_IDX then (f.nu : ℝ) else 0)

theorem tgt_cast (f : Farkas) (j : Fin NV) :
    (((if (j : ℕ) = f.i then (f.sigma : ℚ) else 0) + (if (j : ℕ) = S_IDX then f.nu else 0) : ℚ) : ℝ)
      = tgt f j := by
  unfold tgt
  split_ifs <;> push_cast <;> ring

/-- `‖ρ‖₁ ≤ farkasL1` for the residual `ρ_j = tgt_j − Σ_r μ_r ∂_j g_r(ξ_r)`. -/
theorem sum_abs_rho_le (hsh : Shape c c.S c.Y) {ξ : Fin NV → Vec}
    (hξ : ∀ rr, MemBox (boxArr c c.rN) (ξ rr)) (f : Farkas) :
    ∑ j : Fin NV, |tgt f j - ∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ) * eval (ξ rr) ((rowE c c.S rr).D j)|
      ≤ ((farkasL1 f (Jrows c c.S c.rN) : ℚ) : ℝ) := by
  unfold farkasL1
  rw [rng_eq, foldl_add_eq_sum, zero_add]
  push_cast
  rw [sum_range_NV_eq]
  refine sum_le_sum fun j _ => ?_
  have hacc := mem_farkas_acc hsh hξ f j
  rw [mkV_getD _ j.isLt]
  have := mem_mag (mem_sub (mem_pt ((if (j : ℕ) = f.i then (f.sigma : ℚ) else 0)
    + (if (j : ℕ) = S_IDX then f.nu else 0))) hacc)
  rw [tgt_cast] at this
  exact this

theorem sum_ite_val (i : Fin NV) (a : ℝ) (d : Fin NV → ℝ) :
    ∑ j : Fin NV, (if (j : ℕ) = i then a else 0) * d j = a * d i := by
  rw [Finset.sum_eq_single i]
  · simp
  · intro j _ hj
    have : ¬ (j : ℕ) = i := fun h => hj (Fin.ext h)
    simp [this]
  · intro h; exact absurd (Finset.mem_univ _) h

/-- The side index. -/
def sIdx : Fin NV := ⟨S_IDX, by decide⟩

theorem sZ_eq (z : Vec) : sZ z = z sIdx := by
  simp [sZ, getV, sIdx, S_IDX, NV]

theorem sum_ite_S (a : ℝ) (d : Fin NV → ℝ) :
    ∑ j : Fin NV, (if (j : ℕ) = S_IDX then a else 0) * d j = a * d sIdx :=
  sum_ite_val sIdx a d

/-- **A22 §5, strict local optimality.**  A feasible small-tilt configuration of the box
`N` whose side does not exceed `s(ẑ)` is `ẑ` itself. -/
theorem a22_optimal (hc : checkA22 c = true) {z : Vec} (hz : MemBox (boxArr c c.rN) z)
    (hsm : SmallTilt z) (hf : Feas z) (hs : sZ z ≤ sZ (zhatV c hc)) : z = zhatV c hc := by
  obtain ⟨hsh, -, -, -, hB, -⟩ := checkA22_parts hc
  have hsh' := (shape_of_shapeOK hsh).1
  set zh := zhatV c hc with hzh
  set d : Vec := fun j => z j - zh j with hd
  -- the mean-value decomposition of every pin row
  choose ξ hξ hmvt using fun rr : Fin NV => mvt_box (zhatV_memBox_rN hc) hz (rowE c c.S rr)
  have hrow : ∀ rr : Fin NV, 0 ≤ ∑ j : Fin NV, eval (ξ rr) ((rowE c c.S rr).D j) * d j := by
    intro rr
    have h1 := hmvt rr
    rw [zhatV_zero hc rr, sub_zero] at h1
    rw [← h1]
    exact rows_nonneg hc hz hsm hf rr
  -- the certificates
  simp only [farkasOK, Bool.and_eq_true, Array.all_eq_true, List.all_eq_true, rng_eq,
    List.mem_range, Array.any_eq_true, decide_eq_true_eq, List.mem_cons, List.mem_singleton,
    List.not_mem_nil, or_false] at hB
  obtain ⟨hone, hcomp⟩ := hB
  have hcomp' : ∀ (i : Fin NV) (σ : ℤ), σ = 1 ∨ σ = -1 →
      ∃ (idx : ℕ) (h : idx < c.farkas.size), c.farkas[idx].i = i ∧ c.farkas[idx].sigma = σ := by
    intro i σ hσ
    have := hcomp i i.isLt σ (by rcases hσ with rfl | rfl <;> simp)
    obtain ⟨idx, h, h1, h2⟩ := this
    exact ⟨idx, h, h1, h2⟩
  -- the uniform bound over all certificates
  have hpos : 0 < c.farkas.size := by
    obtain ⟨idx, h, -⟩ := hcomp' ⟨0, by decide⟩ 1 (Or.inl rfl)
    omega
  have hne : (Finset.univ : Finset (Fin c.farkas.size)).Nonempty := ⟨⟨0, hpos⟩, Finset.mem_univ _⟩
  set B : ℝ := Finset.univ.sup' hne
    (fun idx : Fin c.farkas.size => ((farkasL1 c.farkas[idx] (Jrows c c.S c.rN) : ℚ) : ℝ)) with hBdef
  have hB1 : B < 1 := by
    rw [hBdef, Finset.sup'_lt_iff]
    intro idx _
    have := hone idx idx.isLt
    simp only [farkasOne, Bool.and_eq_true, decide_eq_true_eq] at this
    exact_mod_cast this.2
  have hBge : ∀ idx : Fin c.farkas.size,
      ((farkasL1 c.farkas[idx] (Jrows c c.S c.rN) : ℚ) : ℝ) ≤ B := fun idx =>
    Finset.le_sup' (fun idx : Fin c.farkas.size =>
      ((farkasL1 c.farkas[idx] (Jrows c c.S c.rN) : ℚ) : ℝ)) (Finset.mem_univ idx)
  have hBnn : 0 ≤ B := by
    refine le_trans ?_ (hBge ⟨0, hpos⟩)
    have : (0 : ℚ) ≤ farkasL1 c.farkas[0] (Jrows c c.S c.rN) := by
      unfold farkasL1
      rw [rng_eq, foldl_add_eq_sum, zero_add]
      exact Finset.sum_nonneg fun j _ => mag_nonneg _
    exact_mod_cast this
  -- one certificate: `σ d_i ≥ −B ‖d‖`
  have hone' : ∀ (i : Fin NV) (σ : ℤ), σ = 1 ∨ σ = -1 → -(B * dist d 0) ≤ (σ : ℝ) * d i := by
    intro i σ hσ
    obtain ⟨idx, hidx, hfi, hfσ⟩ := hcomp' i σ hσ
    set f := c.farkas[idx] with hf
    have hf1 := hone idx hidx
    rw [← hf] at hf1
    simp only [farkasOne, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hf1
    obtain ⟨⟨⟨⟨⟨hnu, hmu⟩, hmusize⟩, hfi'⟩, -⟩, hl1⟩ := hf1
    have hμ : ∀ rr : Fin NV, (0 : ℝ) ≤ ((f.mu.getD rr 0 : ℚ) : ℝ) := by
      intro rr
      have hrr : (rr : ℕ) < f.mu.size := by rw [hmusize]; exact rr.isLt
      rw [getD_of_lt _ hrr]
      exact_mod_cast hmu rr hrr
    have hν : (0 : ℝ) ≤ (f.nu : ℝ) := by exact_mod_cast hnu
    -- `Σ_j tgt_j d_j = σ d_i + ν d_s`
    have htgt : ∑ j : Fin NV, tgt f j * d j = (σ : ℝ) * d i + (f.nu : ℝ) * d sIdx := by
      simp only [tgt, add_mul, Finset.sum_add_distrib]
      have hi' : (⟨f.i, hfi'⟩ : Fin NV) = i := Fin.ext hfi
      rw [sum_ite_val ⟨f.i, hfi'⟩ (f.sigma : ℝ), sum_ite_S, hi', hfσ]
    -- `Σ_j (Σ_r μ_r ∂_j g_r) d_j ≥ 0`
    have hpos' : 0 ≤ ∑ j : Fin NV, (∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ)
        * eval (ξ rr) ((rowE c c.S rr).D j)) * d j := by
      simp only [Finset.sum_mul]
      rw [Finset.sum_comm]
      refine Finset.sum_nonneg fun rr _ => ?_
      have : ∑ j : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ) * eval (ξ rr) ((rowE c c.S rr).D j) * d j
          = ((f.mu.getD rr 0 : ℚ) : ℝ) * ∑ j : Fin NV, eval (ξ rr) ((rowE c c.S rr).D j) * d j := by
        rw [Finset.mul_sum]
        exact Finset.sum_congr rfl fun j _ => by ring
      rw [this]
      exact mul_nonneg (hμ rr) (hrow rr)
    -- the residual term
    have hρ : -(B * dist d 0) ≤ ∑ j : Fin NV, (tgt f j - ∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ)
        * eval (ξ rr) ((rowE c c.S rr).D j)) * d j := by
      have h1 := abs_le_of_rowsum (m := fun _ j => tgt f j - ∑ rr : Fin NV,
        ((f.mu.getD rr 0 : ℚ) : ℝ) * eval (ξ rr) ((rowE c c.S rr).D j)) (β := B)
        (fun _ => (sum_abs_rho_le hsh' hξ f).trans (hBge ⟨idx, hidx⟩)) d i
      exact (abs_le.mp h1).1
    -- assemble
    have hds : d sIdx ≤ 0 := by
      simp only [hd, hzh]
      rw [← sZ_eq z, ← sZ_eq (zhatV c hc)]
      linarith
    have hsum : ∑ j : Fin NV, tgt f j * d j
        = ∑ j : Fin NV, (tgt f j - ∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ)
            * eval (ξ rr) ((rowE c c.S rr).D j)) * d j
          + ∑ j : Fin NV, (∑ rr : Fin NV, ((f.mu.getD rr 0 : ℚ) : ℝ)
            * eval (ξ rr) ((rowE c c.S rr).D j)) * d j := by
      rw [← Finset.sum_add_distrib]
      exact Finset.sum_congr rfl fun j _ => by ring
    have hνd : (f.nu : ℝ) * d sIdx ≤ 0 := mul_nonpos_of_nonneg_of_nonpos hν hds
    linarith [htgt, hsum, hpos', hρ, hνd]
  -- both signs: `|d_i| ≤ B ‖d‖`
  have hcoord : ∀ i : Fin NV, |d i| ≤ B * dist d 0 := by
    intro i
    have h1 := hone' i 1 (Or.inl rfl)
    have h2 := hone' i (-1) (Or.inr rfl)
    push_cast at h1 h2
    rw [abs_le]
    constructor <;> linarith
  have hdist : dist d 0 ≤ B * dist d 0 := by
    rw [dist_pi_le_iff (by positivity)]
    intro i
    rw [Real.dist_eq, Pi.zero_apply, sub_zero]
    exact hcoord i
  have hd0 := eq_zero_of_dist_le hB1 hdist
  funext j
  have := congrFun hd0 j
  simp only [hd, Pi.zero_apply] at this
  linarith

/-- The operative form: `s(z) ≥ s(ẑ)` on the box, with equality only at `ẑ`. -/
theorem a22_optimal' (hc : checkA22 c = true) {z : Vec} (hz : MemBox (boxArr c c.rN) z)
    (hsm : SmallTilt z) (hf : Feas z) :
    sZ (zhatV c hc) ≤ sZ z ∧ (sZ z = sZ (zhatV c hc) → z = zhatV c hc) := by
  constructor
  · by_contra hlt
    push_neg at hlt
    have := a22_optimal hc hz hsm hf hlt.le
    rw [this] at hlt
    exact lt_irrefl _ hlt
  · intro heq
    exact a22_optimal hc hz hsm hf heq.le

end

end PackingCert.Rigid
