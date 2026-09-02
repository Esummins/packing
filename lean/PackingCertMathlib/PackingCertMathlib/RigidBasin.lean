import PackingCertMathlib.RigidA36

/-!
# The basin theorem for a universal A36 certificate (A79, rung (c), main theorem)

`a36_basin`: `checkA22 c = true`, `checkA36 c a = true`, `a.universal = true` ⟹ for every
feasible `z` with `‖z − ẑ‖_∞ ≤ a.h`: `s(ẑ) ≤ s(z)`, and `s(z) = s(ẑ) → z = ẑ`.
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set Finset

section

variable {c : A22Cert} {a : A36Cert}

/-- `‖z − ẑ‖_∞ ≤ h`. -/
def InBoxZ (zh : Vec) (h : ℚ) (z : Vec) : Prop := ∀ k : Fin NV, |z k - zh k| ≤ (h : ℝ)

theorem inBoxR_of_inBoxZ (hc : checkA22 c = true) {h : ℚ} {z : Vec}
    (hz : InBoxZ (zhatV c hc) h z) : InBoxR c (h + c.r0) z := by
  intro k
  have h1 := hz k
  have h2 := zhatV_inBoxR hc k
  push_cast
  calc |z k - z0R c k| = |(z k - zhatV c hc k) + (zhatV c hc k - z0R c k)| := by ring_nf
    _ ≤ |z k - zhatV c hc k| + |zhatV c hc k - z0R c k| := abs_add_le _ _
    _ ≤ (h : ℝ) + (c.r0 : ℝ) := add_le_add h1 h2

theorem smallTilt_of_anglesSmall {b : Array IV} (hA : anglesSmall (Box.ofArray b) = true) {z : Vec}
    (hz : MemBox b z) : SmallTilt z := by
  intro i hi
  simp only [anglesSmall, List.all_eq_true, rng_eq, List.mem_range, Bool.and_eq_true,
    decide_eq_true_eq] at hA
  obtain ⟨h1, h2⟩ := hA i hi
  obtain ⟨hm1, hm2⟩ := mem_get hz (3 * i + 2)
  have h1' := rabs_le_one_cast h1
  have h2' := rabs_le_one_cast h2
  rw [abs_le] at h1' h2' ⊢
  unfold thZ
  exact ⟨by linarith [h1'.1], by linarith [h2'.2]⟩

/-! ## Fold enclosures -/

theorem foldl_mkV_sound {l : List ℕ} {S : Fin NV → ℝ} {g : ℕ → Fin NV → ℝ} {G : ℕ → Array IV}
    {w : ℕ → ℚ} (hg : ∀ k ∈ l, ∀ j : Fin NV, Mem (g k j) ((G k).getD j IV.zero)) :
    ∀ {acc : Array IV}, (∀ j : Fin NV, Mem (S j) (acc.getD j IV.zero)) →
      ∀ j : Fin NV, Mem (S j + (l.map fun k => ((w k : ℚ) : ℝ) * g k j).sum)
        ((l.foldl (fun acc k => mkV NV fun j => acc.getD j IV.zero + IV.pt (w k) * (G k).getD j IV.zero)
          acc).getD j IV.zero) := by
  induction l generalizing S with
  | nil => intro acc hacc j; simpa using hacc j
  | cons k l ih =>
    intro acc hacc j
    simp only [List.foldl_cons, List.map_cons, List.sum_cons]
    have hstep : ∀ j : Fin NV, Mem (S j + ((w k : ℚ) : ℝ) * g k j)
        ((mkV NV fun j => acc.getD j IV.zero + IV.pt (w k) * (G k).getD j IV.zero).getD j IV.zero) := by
      intro j
      rw [mkV_getD _ j.isLt]
      exact mem_add (hacc j) (mem_mul (mem_pt _) (hg k (List.mem_cons_self ..) j))
    have := ih (S := fun j => S j + ((w k : ℚ) : ℝ) * g k j)
      (fun k' hk' => hg k' (List.mem_cons_of_mem _ hk')) hstep j
    simpa [add_assoc] using this

theorem foldl_mkM_sound {l : List ℕ} {S : Fin NV → Fin NV → ℝ} {g : ℕ → Fin NV → Fin NV → ℝ}
    {G : ℕ → Array (Array IV)} {w : ℕ → ℚ}
    (hg : ∀ k ∈ l, ∀ i j : Fin NV, Mem (g k i j) (((G k).getD i #[]).getD j IV.zero)) :
    ∀ {acc : Array (Array IV)}, (∀ i j : Fin NV, Mem (S i j) ((acc.getD i #[]).getD j IV.zero)) →
      ∀ i j : Fin NV, Mem (S i j + (l.map fun k => ((w k : ℚ) : ℝ) * g k i j).sum)
        (((l.foldl (fun acc k => mkM NV fun i j =>
            (acc.getD i #[]).getD j IV.zero + IV.pt (w k) * ((G k).getD i #[]).getD j IV.zero)
          acc).getD i #[]).getD j IV.zero) := by
  induction l generalizing S with
  | nil => intro acc hacc i j; simpa using hacc i j
  | cons k l ih =>
    intro acc hacc i j
    simp only [List.foldl_cons, List.map_cons, List.sum_cons]
    have hstep : ∀ i j : Fin NV, Mem (S i j + ((w k : ℚ) : ℝ) * g k i j)
        (((mkM NV fun i j => (acc.getD i #[]).getD j IV.zero
          + IV.pt (w k) * ((G k).getD i #[]).getD j IV.zero).getD i #[]).getD j IV.zero) := by
      intro i j
      rw [mkM_getD _ i.isLt j.isLt]
      exact mem_add (hacc i j) (mem_mul (mem_pt _) (hg k (List.mem_cons_self ..) i j))
    have := ih (S := fun i j => S i j + ((w k : ℚ) : ℝ) * g k i j)
      (fun k' hk' => hg k' (List.mem_cons_of_mem _ hk')) hstep i j
    simpa [add_assoc] using this

theorem loaded_nodup (a : A36Cert) : (loaded a).Nodup := by
  unfold loaded
  rw [rng_eq]
  exact List.Nodup.filter _ List.nodup_range

theorem loaded_lt (a : A36Cert) {k : ℕ} (hk : k ∈ loaded a) : k < NEXT3 := by
  unfold loaded at hk
  rw [rng_eq, List.mem_filter, List.mem_range] at hk
  exact hk.1

theorem loaded_ne (a : A36Cert) {k : ℕ} (hk : k ∈ loaded a) : a.omega.getD k 0 ≠ 0 := by
  unfold loaded at hk
  rw [rng_eq, List.mem_filter] at hk
  simpa using hk.2

theorem mem_loaded (a : A36Cert) {k : ℕ} (hk : k < NEXT3) (hne : a.omega.getD k 0 ≠ 0) : k ∈ loaded a := by
  unfold loaded
  rw [rng_eq, List.mem_filter, List.mem_range]
  exact ⟨hk, by simpa using hne⟩

theorem sum_loaded_toFinset (a : A36Cert) (f : ℕ → ℝ) :
    ((loaded a).map f).sum = ∑ k ∈ (loaded a).toFinset, f k :=
  (List.sum_toFinset f (loaded_nodup a)).symm

theorem sum_loaded_toFinset_rat (a : A36Cert) (f : ℕ → ℚ) :
    ((loaded a).map f).sum = ∑ k ∈ (loaded a).toFinset, f k :=
  (List.sum_toFinset f (loaded_nodup a)).symm

/-- `Wfun` as a sum over the loaded finset. -/
theorem Wfun_eq_loaded (c : A22Cert) (a : A36Cert) (z : Vec) :
    Wfun c a z = ∑ k ∈ (loaded a).toFinset, ωR a k * eval z (e70 c k) := by
  unfold Wfun
  rw [← sum_loaded_toFinset, sum_loaded_eq]
  intro k hk; simp [ωR, hk]

theorem Wgrad_eq_loaded (c : A22Cert) (a : A36Cert) (z : Vec) (j : Fin NV) :
    Wgrad c a z j = ((loaded a).map fun k => ωR a k * eval z ((e70 c k).D j)).sum := by
  unfold Wgrad
  rw [sum_loaded_eq]
  intro k hk; simp [ωR, hk]

theorem Whess_eq_loaded (c : A22Cert) (a : A36Cert) (z : Vec) (i j : Fin NV) :
    Whess c a z i j = ((loaded a).map fun k => ωR a k * eval z (((e70 c k).D j).D i)).sum := by
  unfold Whess
  rw [sum_loaded_eq]
  intro k hk; simp [ωR, hk]

theorem mem_omegaGrad (hr : rows70OK c = true) {b : Array IV} {z : Vec} (hz : MemBox b z) (j : Fin NV) :
    Mem (Wgrad c a z j) ((omegaGrad c a (Box.ofArray b)).getD j IV.zero) := by
  rw [Wgrad_eq_loaded]
  unfold omegaGrad
  have := foldl_mkV_sound (l := loaded a) (S := fun _ => 0)
    (g := fun k j => eval z ((e70 c k).D j)) (G := fun k => gradDense (Box.ofArray b) (row70 c k))
    (w := fun k => a.omega.getD k 0)
    (fun k hk j => gradDense_sound hz (row70 c k) (rows70_parts hr k (loaded_lt a hk)).1 j)
    (acc := mkV NV fun _ => IV.zero) (fun j => by rw [mkV_getD _ j.isLt]; exact mem_zero) j
  simpa [ωR] using this

theorem mem_omegaHess (hr : rows70OK c = true) {b : Array IV} {z : Vec} (hz : MemBox b z) (i j : Fin NV) :
    Mem (Whess c a z i j) (((omegaHess c a (Box.ofArray b)).getD i #[]).getD j IV.zero) := by
  rw [Whess_eq_loaded]
  unfold omegaHess
  have := foldl_mkM_sound (l := loaded a) (S := fun _ _ => 0)
    (g := fun k i j => eval z (((e70 c k).D j).D i))
    (G := fun k => hessDense (Box.ofArray b) (row70 c k))
    (w := fun k => a.omega.getD k 0)
    (fun k hk i j => hessDense_sound hz (row70 c k) (rows70_parts hr k (loaded_lt a hk)).1 i j)
    (acc := mkM NV fun _ _ => IV.zero) (fun i j => by rw [mkM_getD _ i.isLt j.isLt]; exact mem_zero) i j
  simpa [ωR] using this

/-! ## The certificate constants bound the real quantities -/

theorem abs_W_le_eps0 {b : Array IV} {z : Vec} (hz : MemBox b z) :
    |Wfun c a z| ≤ ((eps0 c a (Box.ofArray b) : ℚ) : ℝ) := by
  rw [Wfun_eq_loaded]
  unfold eps0
  rw [foldl_add_list, zero_add, sum_loaded_toFinset_rat]
  push_cast
  refine abs_sum_le _ _ _ fun k _ => ?_
  rw [abs_mul, rabs_cast]
  refine mul_le_mul_of_nonneg_left ?_ (abs_nonneg _)
  exact mem_mag (evalIV_sound hz (e70 c k))

theorem sum_abs_grad_le_epsW (hr : rows70OK c = true) {b : Array IV} {z : Vec} (hz : MemBox b z) :
    ∑ j : Fin NV, |Wgrad c a z j - (if (j : ℕ) = S_IDX then 1 else 0)|
      ≤ ((epsW c a (Box.ofArray b) : ℚ) : ℝ) := by
  unfold epsW
  rw [rng_eq, foldl_add_eq_sum, zero_add]
  push_cast
  rw [sum_range_NV_eq]
  refine sum_le_sum fun j _ => ?_
  have h1 := mem_omegaGrad (a := a) hr hz j
  have h2 : Mem (if (j : ℕ) = S_IDX then (1 : ℝ) else 0) (if (j : ℕ) = S_IDX then IV.one else IV.zero) := by
    split_ifs
    · exact mem_one
    · exact mem_zero
  exact mem_mag (mem_sub h1 h2)

theorem hbar_eq (c : A22Cert) (a : A36Cert) (bx : Box) :
    hbar c a bx = (∑ i ∈ range NV, ∑ j ∈ range NV,
      (((omegaHess c a bx).getD i #[]).getD j IV.zero).mag) / 2 := by
  unfold hbar
  rw [rng_eq]
  have hin : ∀ (s : ℚ) (i : ℕ), (List.range NV).foldl
      (fun s j => s + (((omegaHess c a bx).getD i #[]).getD j IV.zero).mag) s
      = s + ∑ j ∈ range NV, (((omegaHess c a bx).getD i #[]).getD j IV.zero).mag :=
    fun s i => foldl_add_eq_sum s _
  simp only [hin]
  rw [foldl_add_eq_sum, zero_add]

theorem sum_abs_hess_le (hr : rows70OK c = true) {b : Array IV} {z : Vec} (hz : MemBox b z) :
    ∑ i : Fin NV, ∑ j : Fin NV, |Whess c a z i j| ≤ 2 * ((hbar c a (Box.ofArray b) : ℚ) : ℝ) := by
  rw [hbar_eq]
  push_cast
  rw [sum_range_NV_eq]
  simp only [sum_range_NV_eq]
  rw [mul_div_cancel₀ _ (by norm_num : (2 : ℝ) ≠ 0)]
  refine sum_le_sum fun i _ => sum_le_sum fun j _ => ?_
  exact mem_mag (mem_omegaHess (a := a) hr hz i j)

theorem pinPos_mem (hP : a.P.size = NV) (r : Fin NV) : pinPos a r ∈ a.P.toList := by
  unfold pinPos
  have hr : (r : ℕ) < a.P.size := by rw [hP]; exact r.isLt
  rw [getD_of_lt _ hr]
  simp

theorem abs_pin_le_gmax (hP : a.P.size = NV) {b : Array IV} {z : Vec} (hz : MemBox b z) (r : Fin NV) :
    |eval z (e70 c (pinPos a r))| ≤ ((gmax c a (Box.ofArray b) : ℚ) : ℝ) := by
  unfold gmax
  rw [← Array.foldl_toList]
  have := le_foldl_rmax a.P.toList 0 (fun k => (evalIV (Box.ofArray b) (rowExpr (row70 c k))).mag)
    (pinPos a r) (pinPos_mem hP r)
  have hm := mem_mag (evalIV_sound hz (e70 c (pinPos a r)))
  exact le_trans hm (by exact_mod_cast this)

theorem sum_abs_Y_le_kappa (i : Fin NV) :
    ∑ r : Fin NV, |((Ymat c.Y i r : ℚ) : ℝ)| ≤ ((kappa c : ℚ) : ℝ) := by
  unfold kappa
  rw [rng_eq]
  have := le_foldl_rmax (List.range NV) 0
    (fun i => (List.range NV).foldl (fun s r => s + CaseI.rabs (Ymat c.Y i r)) 0) i
    (List.mem_range.mpr i.isLt)
  rw [foldl_add_eq_sum, zero_add] at this
  have h2 : ((∑ r ∈ range NV, CaseI.rabs (Ymat c.Y i r) : ℚ) : ℝ)
      = ∑ r : Fin NV, |((Ymat c.Y i r : ℚ) : ℝ)| := by
    push_cast
    rw [sum_range_NV_eq]
    exact sum_congr rfl fun r _ => rabs_cast _
  rw [← h2]
  exact_mod_cast this

theorem abs_Y_le_cvec (i r : Fin NV) : |((Ymat c.Y i r : ℚ) : ℝ)| ≤ ((cvec c r : ℚ) : ℝ) := by
  unfold cvec
  rw [rng_eq]
  have := le_foldl_rmax (List.range NV) 0 (fun i => CaseI.rabs (Ymat c.Y i r)) i
    (List.mem_range.mpr i.isLt)
  rw [← rabs_cast]
  exact_mod_cast this

theorem cvec_le_keff (hpos : pinsPositive a = true) (r : Fin NV) :
    ((cvec c r : ℚ) : ℝ) ≤ ((kappaEff c a : ℚ) : ℝ) * ωR a (pinPos a r) := by
  simp only [pinsPositive, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hpos
  obtain ⟨hP, hω⟩ := hpos
  have hr : (r : ℕ) < a.P.size := by rw [hP]; exact r.isLt
  have hω' : 0 < a.omega.getD (pinPos a r) 0 := by
    unfold pinPos; rw [getD_of_lt _ hr]; exact hω r hr
  have hle : cvec c r / a.omega.getD (pinPos a r) 0 ≤ kappaEff c a := by
    unfold kappaEff
    rw [rng_eq]
    exact le_foldl_rmax (List.range NV) 0 (fun r => cvec c r / a.omega.getD (a.P.getD r 0) 0) r
      (List.mem_range.mpr r.isLt)
  have hωR : (0 : ℝ) < ((a.omega.getD (pinPos a r) 0 : ℚ) : ℝ) := by exact_mod_cast hω'
  have h1 : ((cvec c r : ℚ) : ℝ) / ((a.omega.getD (pinPos a r) 0 : ℚ) : ℝ)
      ≤ ((kappaEff c a : ℚ) : ℝ) := by
    have := (Rat.cast_le (K := ℝ)).mpr hle
    push_cast at this
    exact this
  rw [div_le_iff₀ hωR] at h1
  unfold ωR
  exact h1

theorem cvec_nonneg (c : A22Cert) (r : ℕ) : (0 : ℚ) ≤ cvec c r := by
  unfold cvec
  rw [rng_eq]
  refine le_trans ?_ (foldl_rmax_ge _ _ _)
  exact le_rfl

theorem betaRow_le_betaA36 (bx : Box) (i : Fin NV) :
    betaRow (Mrow c.Y (pinJ c a bx) i) ≤ betaA36 c a bx := by
  unfold betaA36
  rw [rng_eq]
  exact le_foldl_rmax (List.range NV) 0 (fun i => betaRow (Mrow c.Y (pinJ c a bx) i)) i
    (List.mem_range.mpr i.isLt)

/-- The pin-row Jacobian enclosure. -/
theorem mem_pinJ (hr : rows70OK c = true) (hP : a.P.size = NV) (hlt : ∀ k ∈ a.P, k < NEXT3)
    {b : Array IV} {ξ : Vec} (hξ : MemBox b ξ) (rr j : Fin NV) :
    Mem (eval ξ ((e70 c (pinPos a rr)).D j)) (((pinJ c a (Box.ofArray b)).getD rr #[]).getD j IV.zero) := by
  have hrr : (rr : ℕ) < (pinJ c a (Box.ofArray b)).size := by simp [pinJ, hP]
  rw [getD_of_lt _ hrr]
  simp only [pinJ, Array.getElem_map]
  have hrr' : (rr : ℕ) < a.P.size := by rw [hP]; exact rr.isLt
  have hpos : pinPos a rr = a.P[(rr : ℕ)] := by unfold pinPos; rw [getD_of_lt _ hrr']
  rw [hpos]
  exact gradDense_sound hξ _ (rows70_parts hr _ (hlt _ (Array.getElem_mem hrr'))).1 j

/-- `m_ij(ξ) = δ_ij − Σ_r Y_ir ∂_j g_{P_r}(ξ_r)` is enclosed by `Mrow` (pin-row version). -/
theorem mem_Mrow_pin (hr : rows70OK c = true) (hP : a.P.size = NV) (hlt : ∀ k ∈ a.P, k < NEXT3)
    {b : Array IV} {ξ : Fin NV → Vec} (hξ : ∀ rr, MemBox b (ξ rr)) (i j : Fin NV) :
    Mem ((if i = j then 1 else 0)
        - ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j))
      ((Mrow c.Y (pinJ c a (Box.ofArray b)) i).getD j IV.zero) := by
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
        * eval (ξ ⟨rr % NV, Nat.mod_lt _ (by decide)⟩) ((e70 c (pinPos a rr)).D j))
      (g := fun rr => IV.pt (Ymat c.Y i rr) * ((pinJ c a (Box.ofArray b)).getD rr #[]).getD j IV.zero)
      (fun rr hrr => by
        have hrr' : rr % NV = rr := Nat.mod_eq_of_lt hrr
        have hm := mem_pinJ hr hP hlt (hξ ⟨rr, hrr⟩) ⟨rr, hrr⟩ ⟨j, j.isLt⟩
        simp only [hrr'] at hm ⊢
        exact mem_mul (mem_pt _) hm)
    rw [zero_add, sum_range_NV_eq] at this
    have key : (∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ) * eval (ξ rr) ((e70 c (pinPos a rr)).D j))
        = ∑ rr : Fin NV, ((Ymat c.Y i rr : ℚ) : ℝ)
            * eval (ξ ⟨(rr : ℕ) % NV, Nat.mod_lt _ (by decide)⟩) ((e70 c (pinPos a rr)).D j) := by
      refine sum_congr rfl fun rr _ => ?_
      rw [fin_mod_self]
    rw [key]
    exact this

/-! ## Validity of the loaded rows -/

theorem loaded_row_nonneg (hr : rows70OK c = true) (hu : a.universal = true)
    (hlv : loadedValidOK c a (radBox c.z0 (a.h + c.r0)) = true) {z : Vec}
    (hz : MemBox (boxArr c (a.h + c.r0)) z) (hsm : SmallTilt z) (hf : Feas z) {k : ℕ}
    (hk : k ∈ loaded a) : 0 ≤ eval z (e70 c k) := by
  simp only [loadedValidOK, List.all_eq_true] at hlv
  have hlv' := hlv k hk
  obtain ⟨-, hshape⟩ := rows70_parts hr k (loaded_lt a hk)
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
    rw [radBox_eq] at h1 h2
    have hm1 := mem_mag (evalIV_sound hz (tanE i kc j e))
    have hm2 := (evalIV_sound hz (depE i kc j e)).1
    have h1' : (((evalIV (Box.ofArray (boxArr c (a.h + c.r0))) (tanE i kc j e)).mag : ℚ) : ℝ)
        < ((1 / 2 : ℚ) : ℝ) := by exact_mod_cast h1
    have h2' : (((-1 / 2 : ℚ)) : ℝ)
        < (((evalIV (Box.ofArray (boxArr c (a.h + c.r0))) (depE i kc j e)).lo : ℚ) : ℝ) := by
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

theorem W_nonneg (hr : rows70OK c = true) (hu : a.universal = true) (ho : omegaOK a = true)
    (hlv : loadedValidOK c a (radBox c.z0 (a.h + c.r0)) = true) {z : Vec}
    (hz : MemBox (boxArr c (a.h + c.r0)) z) (hsm : SmallTilt z) (hf : Feas z) :
    0 ≤ Wfun c a z := by
  rw [Wfun_eq_loaded]
  refine Finset.sum_nonneg fun k hk => ?_
  rw [List.mem_toFinset] at hk
  exact mul_nonneg (omega_nonneg ho k) (loaded_row_nonneg hr hu hlv hz hsm hf hk)

/-- The pin sum is bounded by `W` (the pins are distinct loaded rows, all terms `≥ 0`). -/
theorem pin_sum_le_W (hr : rows70OK c = true) (hu : a.universal = true) (ho : omegaOK a = true)
    (hlv : loadedValidOK c a (radBox c.z0 (a.h + c.r0)) = true) (hpos : pinsPositive a = true)
    (hrange : pinsRangeOK a = true) {z : Vec}
    (hz : MemBox (boxArr c (a.h + c.r0)) z) (hsm : SmallTilt z) (hf : Feas z) :
    ∑ r : Fin NV, ωR a (pinPos a r) * eval z (e70 c (pinPos a r)) ≤ Wfun c a z := by
  simp only [pinsPositive, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hpos
  obtain ⟨hP, hω⟩ := hpos
  simp only [pinsRangeOK, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true] at hrange
  obtain ⟨hlt, hnodup⟩ := hrange
  rw [Wfun_eq_loaded]
  -- the pin positions, as a finset image
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
    exact mul_nonneg (omega_nonneg ho k) (loaded_row_nonneg hr hu hlv hz hsm hf hk)

end

end PackingCert.Rigid
