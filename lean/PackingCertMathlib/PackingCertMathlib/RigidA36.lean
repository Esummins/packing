import PackingCertMathlib.RigidOptimal

/-!
# The A36 basin theorem from `checkA36 = true` (A79, rung (c))

For a UNIVERSAL certificate `a` (the branch-free barrier `G3_UNIVERSAL`, `ω` supported on
A22's rows 0..35 and the two aux dist rows), `checkA36 c a = true` gives, for every
feasible configuration `z` with `‖z − ẑ‖_∞ ≤ a.h`:

    s(z) ≥ s(ẑ), with equality only at `z = ẑ`   (`a36_basin`).

Proof (A36 §3.1, the (V′) chain with the max-form pinning):
* `W = Σ ω_k g_k ≥ 0` at `z` (validity: `ω ≥ 0`, and every loaded row is `≥ 0` at every
  feasible point of the box — walls/dists globally, edges by the checked margins);
* Taylor to second order along the segment `[ẑ, z]` (`taylor2`, two mean-value theorems):
  `s(z) − s(ẑ) ≥ W(z) − E(x)`, `E(x) = ε₀ + ε_w x + H̄ x²`, `x = ‖z − ẑ‖_∞`, with the
  interval Hessian mass `H̄` over the box;
* if `W(z) > E(x)` we are done; otherwise the pinning: the mean-value identity on the pin
  rows and the max-form bound `‖Y F_P(z)‖ ≤ κ_eff W(z)` give `x ≤ ψ(x)`, and the
  quadratic dichotomy (`quad_pin`: `ψ(h) < h`, `ψ(x*) ≤ x*`) forces `x ≤ x*`, so `z` lies
  in A22's box `N` and A22's strict local optimality (`a22_optimal'`) finishes.

The 16 variant certificates are replayed by the same checker but their soundness would
additionally need the L1 axis disjunction (SAT completeness); the composition only
needs the universal one (`rBasin·(1+√2) < 3689/10⁶`, see `Rigidity.lean`).
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set Finset

/-! ## Generic fold / list lemmas -/

theorem foldl_add_list {α : Type} (l : List α) (a : ℚ) (g : α → ℚ) :
    l.foldl (fun s k => s + g k) a = a + (l.map g).sum := by
  induction l generalizing a with
  | nil => simp
  | cons k l ih => simp only [List.foldl_cons, List.map_cons, List.sum_cons]; rw [ih]; ring

theorem foldl_rmax_ge {α : Type} : ∀ (l : List α) (a : ℚ) (g : α → ℚ),
    a ≤ l.foldl (fun m y => CaseI.rmax m (g y)) a
  | [], _, _ => le_rfl
  | k :: l, a, g => by
    simp only [List.foldl_cons]
    refine le_trans ?_ (foldl_rmax_ge l _ g)
    unfold CaseI.rmax; split_ifs <;> linarith

theorem le_foldl_rmax {α : Type} : ∀ (l : List α) (a : ℚ) (g : α → ℚ),
    ∀ x ∈ l, g x ≤ l.foldl (fun m y => CaseI.rmax m (g y)) a
  | [], _, _, x, hx => absurd hx List.not_mem_nil
  | k :: l, a, g, x, hx => by
    simp only [List.foldl_cons]
    rcases List.mem_cons.mp hx with rfl | hx
    · refine le_trans ?_ (foldl_rmax_ge l _ _)
      unfold CaseI.rmax; split_ifs <;> linarith
    · exact le_foldl_rmax l _ g x hx

/-- A sum over the loaded positions equals the sum over all 70 positions for summands
that vanish at unloaded positions. -/
theorem sum_loaded_eq (a : A36Cert) (f : ℕ → ℝ) (hf : ∀ k, a.omega.getD k 0 = 0 → f k = 0) :
    ((loaded a).map f).sum = ∑ k ∈ range NEXT3, f k := by
  unfold loaded
  rw [rng_eq]
  induction NEXT3 with
  | zero => simp
  | succ n ih =>
    rw [List.range_succ, List.filter_append, List.map_append, List.sum_append, sum_range_succ, ih]
    congr 1
    rw [List.filter_singleton]
    by_cases h' : a.omega.getD n 0 ≠ 0
    · rw [decide_eq_true h']; simp
    · rw [decide_eq_false h']
      simp only [cond_false, List.map_nil, List.sum_nil]
      exact (hf n (not_not.mp h')).symm

theorem abs_sum_le {ι : Type} (s : Finset ι) (f g : ι → ℝ) (h : ∀ i ∈ s, |f i| ≤ g i) :
    |∑ i ∈ s, f i| ≤ ∑ i ∈ s, g i :=
  (Finset.abs_sum_le_sum_abs _ _).trans (Finset.sum_le_sum h)

/-! ## Taylor to second order along a segment -/

/-- Two mean-value theorems: `φ(1) = φ(0) + φ'(0) + φ''(η)/2` for some `η ∈ (0, 1)`. -/
theorem taylor2 {φ φ' φ'' : ℝ → ℝ} (h1 : ∀ t, HasDerivAt φ (φ' t) t)
    (h2 : ∀ t, HasDerivAt φ' (φ'' t) t) : ∃ η ∈ Ioo (0 : ℝ) 1, φ 1 = φ 0 + φ' 0 + φ'' η / 2 := by
  set f : ℝ → ℝ := fun t => φ t - φ 0 - φ' 0 * t with hf
  have hf' : ∀ t, HasDerivAt f (φ' t - φ' 0) t := by
    intro t
    have h3 : HasDerivAt (fun y => φ' 0 * y) (φ' 0) t := by
      simpa using (hasDerivAt_id t).const_mul (φ' 0)
    exact ((h1 t).sub_const (φ 0)).sub h3
  have hg' : ∀ t : ℝ, HasDerivAt (fun t => t ^ 2) (2 * t) t := fun t => by
    simpa using hasDerivAt_pow 2 t
  obtain ⟨c, hc, hcauchy⟩ := exists_ratio_hasDerivAt_eq_ratio_slope f (fun t => φ' t - φ' 0)
    (by norm_num : (0 : ℝ) < 1) (fun t _ => (hf' t).continuousAt.continuousWithinAt)
    (fun t _ => hf' t) (fun t => t ^ 2) (fun t => 2 * t)
    (fun t _ => (hg' t).continuousAt.continuousWithinAt) (fun t _ => hg' t)
  obtain ⟨η, hη, hmvt⟩ := exists_hasDerivAt_eq_slope φ' φ'' hc.1
    (fun t _ => (h2 t).continuousAt.continuousWithinAt) (fun t _ => h2 t)
  refine ⟨η, ⟨hη.1, lt_trans hη.2 hc.2⟩, ?_⟩
  simp only [hf] at hcauchy
  rw [sub_zero] at hmvt
  have hc0 : c ≠ 0 := hc.1.ne'
  have hmvt' : φ' c - φ' 0 = φ'' η * c := by
    rw [hmvt]; field_simp
  have key : φ' c - φ' 0 = (φ 1 - φ 0 - φ' 0) * (2 * c) := by
    norm_num at hcauchy
    linarith
  rw [hmvt'] at key
  have h2c : φ'' η = (φ 1 - φ 0 - φ' 0) * 2 := by
    have : φ'' η * c = ((φ 1 - φ 0 - φ' 0) * 2) * c := by linarith
    exact mul_right_cancel₀ hc0 this
  linarith

/-- The quadratic dichotomy: a nonnegative quadratic value at `x ∈ [xs, h]` is impossible
when the quadratic is `≤ 0` at `xs` and `< 0` at `h` (convexity), so `x ≤ xs`. -/
theorem quad_pin {A B C x xs h : ℝ} (hA : 0 ≤ A) (hx : x ≤ h)
    (hq : 0 ≤ A * x ^ 2 + B * x + C) (hqs : A * xs ^ 2 + B * xs + C ≤ 0)
    (hqh : A * h ^ 2 + B * h + C < 0) : x ≤ xs := by
  by_contra hlt
  push_neg at hlt
  have key : (h - xs) * (A * x ^ 2 + B * x + C)
      = (h - x) * (A * xs ^ 2 + B * xs + C) + (x - xs) * (A * h ^ 2 + B * h + C)
        + A * (x - h) * (h - xs) * (x - xs) := by ring
  have h1 : 0 ≤ (h - x) := by linarith
  have h2 : 0 < (x - xs) := by linarith
  have h3 : 0 < (h - xs) := by linarith
  have t1 : (h - x) * (A * xs ^ 2 + B * xs + C) ≤ 0 := mul_nonpos_of_nonneg_of_nonpos h1 hqs
  have t2 : (x - xs) * (A * h ^ 2 + B * h + C) < 0 := mul_neg_of_pos_of_neg h2 hqh
  have t3 : A * (x - h) * (h - xs) * (x - xs) ≤ 0 := by
    have : 0 ≤ A * (h - x) * (h - xs) * (x - xs) := by positivity
    nlinarith
  have : (h - xs) * (A * x ^ 2 + B * x + C) < 0 := by rw [key]; linarith
  have : (h - xs) * (A * x ^ 2 + B * x + C) ≥ 0 := mul_nonneg h3.le hq
  linarith

/-! ## The certificate's quantities, real-valued -/

section

variable (c : A22Cert) (a : A36Cert)

/-- The weight of position `k`. -/
def ωR (k : ℕ) : ℝ := ((a.omega.getD k 0 : ℚ) : ℝ)

/-- Row `k` of the 70-row table. -/
def e70 (k : ℕ) : Expr := rowExpr (row70 c k)

/-- `W(z) = Σ_k ω_k g_k(z)`. -/
noncomputable def Wfun (z : Vec) : ℝ := ∑ k ∈ range NEXT3, ωR a k * eval z (e70 c k)

noncomputable def Wgrad (z : Vec) (j : Fin NV) : ℝ := ∑ k ∈ range NEXT3, ωR a k * eval z ((e70 c k).D j)

noncomputable def Whess (z : Vec) (i j : Fin NV) : ℝ :=
  ∑ k ∈ range NEXT3, ωR a k * eval z (((e70 c k).D j).D i)

/-- Pin position `r`. -/
def pinPos (r : ℕ) : ℕ := a.P.getD r 0

end

section

variable {c : A22Cert} {a : A36Cert}

theorem hasDerivAt_Wfun (p v : Vec) (t : ℝ) :
    HasDerivAt (fun t => Wfun c a (seg p v t))
      (∑ k ∈ range NEXT3, ωR a k * ∑ j : Fin NV, eval (seg p v t) ((e70 c k).D j) * v j) t := by
  have h := HasDerivAt.sum (u := range NEXT3) (x := t)
    (A := fun k t => ωR a k * eval (seg p v t) (e70 c k))
    (A' := fun k => ωR a k * ∑ j : Fin NV, eval (seg p v t) ((e70 c k).D j) * v j)
    (fun k _ => (hasDerivAt_eval p v t (e70 c k)).const_mul _)
  rw [Finset.sum_fn] at h
  exact h

theorem hasDerivAt_Wfun' (p v : Vec) (t : ℝ) :
    HasDerivAt (fun t => ∑ k ∈ range NEXT3, ωR a k * ∑ j : Fin NV, eval (seg p v t) ((e70 c k).D j) * v j)
      (∑ k ∈ range NEXT3, ωR a k * ∑ j : Fin NV,
        (∑ i : Fin NV, eval (seg p v t) (((e70 c k).D j).D i) * v i) * v j) t := by
  have h := HasDerivAt.sum (u := range NEXT3) (x := t)
    (A := fun k t => ωR a k * ∑ j : Fin NV, eval (seg p v t) ((e70 c k).D j) * v j)
    (A' := fun k => ωR a k * ∑ j : Fin NV,
        (∑ i : Fin NV, eval (seg p v t) (((e70 c k).D j).D i) * v i) * v j)
    (fun k _ => by
      refine HasDerivAt.const_mul _ ?_
      have h2 := HasDerivAt.sum (u := (Finset.univ : Finset (Fin NV))) (x := t)
        (A := fun (j : Fin NV) t => eval (seg p v t) ((e70 c k).D j) * v j)
        (A' := fun (j : Fin NV) =>
          (∑ i : Fin NV, eval (seg p v t) (((e70 c k).D j).D i) * v i) * v j)
        (fun j _ => (hasDerivAt_eval p v t ((e70 c k).D j)).mul_const (v j))
      rw [Finset.sum_fn] at h2
      exact h2)
  rw [Finset.sum_fn] at h
  exact h

/-- Second-order Taylor expansion of `W` along `[p, q]`, with the derivatives expressed
through `Wgrad` / `Whess`. -/
theorem Wfun_taylor {b : Array IV} {p q : Vec} (hp : MemBox b p) (hq : MemBox b q) :
    ∃ η : Vec, MemBox b η ∧
      Wfun c a q = Wfun c a p + ∑ j : Fin NV, Wgrad c a p j * (q j - p j)
        + (∑ j : Fin NV, ∑ i : Fin NV, Whess c a η i j * (q i - p i) * (q j - p j)) / 2 := by
  set v : Vec := fun i => q i - p i with hv
  obtain ⟨η, hη, heq⟩ := taylor2 (φ := fun t => Wfun c a (seg p v t))
    (φ' := fun t => ∑ k ∈ range NEXT3, ωR a k * ∑ j : Fin NV, eval (seg p v t) ((e70 c k).D j) * v j)
    (φ'' := fun t => ∑ k ∈ range NEXT3, ωR a k * ∑ j : Fin NV,
        (∑ i : Fin NV, eval (seg p v t) (((e70 c k).D j).D i) * v i) * v j)
    (fun t => hasDerivAt_Wfun p v t) (fun t => hasDerivAt_Wfun' p v t)
  refine ⟨seg p v η, seg_memBox hp hq hη.1.le hη.2.le, ?_⟩
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

/-! ## Unpacking the checker -/

theorem checkA36_parts (ha : checkA36 c a = true) :
    0 < a.h ∧ rows70OK c = true ∧ pinsOK c a = true ∧ omegaOK a = true ∧
    pinningOK c a (a36Stats c a) = true ∧
    (a.universal = true → loadedValidOK c a (radBox c.z0 (a.h + c.r0)) = true) ∧
    pinsRangeOK a = true ∧ anglesSmall (radBox c.z0 (a.h + c.r0)) = true ∧ farWallOK c = true := by
  simp only [checkA36, Bool.and_eq_true, decide_eq_true_eq, Bool.or_eq_true, Bool.not_eq_true'] at ha
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, -⟩, h6⟩, -⟩, -⟩, h9⟩, h10⟩, h11⟩, h12⟩ := ha
  refine ⟨h1, h2, h3, h4, h6, fun hu => ?_, h10, h11, h12⟩
  rcases h9 with h9 | h9
  · rw [hu] at h9; exact absurd h9 (by decide)
  · exact h9

/-- Shape facts of the 70-row table. -/
theorem rows70_parts (h : rows70OK c = true) (k : ℕ) (hk : k < NEXT3) :
    (e70 c k).usesOnly (rowVars (row70 c k)) = true ∧
    (match row70 c k with
      | .wall i kc w => i < 11 ∧ kc < 4 ∧ w < 4
      | .edge i kc j e => i < 11 ∧ kc < 4 ∧ j < 11 ∧ e < 4 ∧ i ≠ j
      | .dist i j => i < 11 ∧ j < 11 ∧ i ≠ j
      | .angeq i j => i < 11 ∧ j < 11) := by
  simp only [rows70OK, List.all_eq_true, rng_eq, List.mem_range, Bool.and_eq_true] at h
  obtain ⟨h1, h2⟩ := h k hk
  refine ⟨h1, ?_⟩
  revert h2
  cases row70 c k <;> simp only [Bool.and_eq_true, decide_eq_true_eq] <;> tauto

/-- `ω ≥ 0` everywhere (on `R_V` by the sign check, zero elsewhere). -/
theorem omega_nonneg (h : omegaOK a = true) (k : ℕ) : 0 ≤ ωR a k := by
  simp only [omegaOK, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, rng_eq,
    List.mem_range, Bool.or_eq_true] at h
  obtain ⟨⟨⟨⟨⟨hsize, -⟩, hRV⟩, hout⟩, -⟩, -⟩ := h
  unfold ωR
  by_cases hk : k < NEXT3
  · rcases hout k hk with hin | hz
    · exact_mod_cast hRV k (by simpa using hin)
    · rw [hz]; simp
  · have : a.omega.getD k 0 = 0 := getD_of_ge _ (by rw [hsize]; exact hk) _
    rw [this]; simp

theorem omega_size (h : omegaOK a = true) : a.omega.size = NEXT3 := by
  simp only [omegaOK, Bool.and_eq_true, decide_eq_true_eq] at h
  exact h.1.1.1.1.1

end

end PackingCert.Rigid
