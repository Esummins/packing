import PackingCertMathlib.RigidKrawczyk
import PackingCertMathlib.RigidGeom

/-!
# The A22 theorem from `checkA22 = true` (A79, rung (b))

From a PASS of the A22 checker: the contact system `S` has a unique zero `ẑ` in
`box(z0, r_N)`, enclosed in `box(z0, r_0)`; `ẑ` is a feasible packing at its own side
(`Feas`, i.e. `IsPacking` of the 11 θ-squares) with all tilts in `[0, 1]`
(`zhatV_feas`, `zhatV_tilt`); and `ẑ` is the strict local minimiser of the side over
feasible configurations of `box(z0, r_N)` with small tilts (`a22_optimal`, A22 §5: the
Farkas certificates + the validity lemmas + the mean-value theorem on the box).
-/

namespace PackingCert.Rigid

open PackingCert PackingCert.S11 Set Finset

section

variable {c : A22Cert}

/-! ## Unpacking the checker -/

theorem checkA22_parts (hc : checkA22 c = true) :
    shapeOK c = true ∧ krawczykOK c c.S c.Y c.rN = true ∧ krawczykOK c c.S c.Y c.r0 = true ∧
    validityOK c c.S (radBox c.z0 c.rN) = true ∧ farkasOK c = true ∧ feasibleOK c = true := by
  simp only [checkA22, Bool.and_eq_true] at hc
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨hsh, -⟩, hK1⟩, hK0⟩, -⟩, hV⟩, -⟩, hB⟩, hF⟩ := hc
  exact ⟨hsh, hK1, hK0, hV, hB, hF⟩

/-- The row-shape facts of `shapeOK`. -/
theorem shapeOK_parts (h : shapeOK c = true) :
    c.z0.size = NV ∧ c.S.size = NV ∧ 0 < c.r0 ∧ c.r0 ≤ c.rN ∧
    (∀ rw ∈ c.rows, (rowExpr rw).usesOnly (rowVars rw) = true) ∧
    (∀ k ∈ c.S, k < c.rows.size) ∧
    (∀ rw ∈ c.rows, match rw with
      | .wall i k w => i < 11 ∧ k < 4 ∧ w < 4
      | .edge i k j e => i < 11 ∧ k < 4 ∧ j < 11 ∧ e < 4 ∧ i ≠ j
      | .dist i j => i < 11 ∧ j < 11 ∧ i ≠ j
      | .angeq i j => i < 11 ∧ j < 11) ∧
    (∀ k ∈ c.S, match c.row k with | .angeq _ _ => False | _ => True) := by
  simp only [shapeOK, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true_iff_forall_mem] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hz, hS⟩, -⟩, -⟩, -⟩, -⟩, -⟩, hr0⟩, hr0N⟩, hSr⟩, -⟩, hu⟩, hrows⟩, hang⟩ := h
  refine ⟨hz, hS, hr0, hr0N, hu, hSr, fun rw hrw => ?_, fun k hk => ?_⟩
  · have := hrows rw hrw
    cases rw <;> simp only [Bool.and_eq_true, decide_eq_true_eq] at this <;> simp only [] <;> tauto
  · have := hang k hk
    cases hr : c.row k <;> simp only [hr] at this ⊢ <;> trivial

theorem row_zero_of_any {S : Array ℕ} {z : Vec} (hz : IsZeroSys c S z) (hS : S.size = NV)
    {R : Row} (h : S.any (fun r => c.row r == R) = true) : eval z (rowExpr R) = 0 := by
  rw [Array.any_eq_true] at h
  obtain ⟨idx, hidx, hR⟩ := h
  rw [beq_iff_eq] at hR
  have hidx' : idx < NV := by rw [hS] at hidx; exact hidx
  have := hz ⟨idx, hidx'⟩
  simp only [rowE] at this
  rw [getD_of_lt _ hidx, hR] at this
  exact this

/-! ## The contact solution -/

theorem kraw_r0 (hc : checkA22 c = true) :
    ∃ y : Vec, InBoxR c c.r0 y ∧ (∀ k : Fin NV, |y k - z0R c k| < (c.r0 : ℝ)) ∧
      IsZeroSys c c.S y ∧ ∀ y' : Vec, MemBox (boxArr c c.r0) y' → IsZeroSys c c.S y' → y' = y := by
  obtain ⟨hsh, -, hK0, -⟩ := checkA22_parts hc
  obtain ⟨-, -, hr0, -⟩ := shapeOK_parts hsh
  exact krawczyk_sound (shape_of_shapeOK hsh).1 hr0 hK0

/-- **`ẑ`**: the unique zero of the contact system in `box(z0, r_0)`. -/
noncomputable def zhatV (c : A22Cert) (hc : checkA22 c = true) : Vec := Classical.choose (kraw_r0 hc)

theorem zhatV_spec (hc : checkA22 c = true) :
    InBoxR c c.r0 (zhatV c hc) ∧ (∀ k : Fin NV, |zhatV c hc k - z0R c k| < (c.r0 : ℝ)) ∧
      IsZeroSys c c.S (zhatV c hc) ∧
      ∀ y' : Vec, MemBox (boxArr c c.r0) y' → IsZeroSys c c.S y' → y' = zhatV c hc :=
  Classical.choose_spec (kraw_r0 hc)

theorem zhatV_zero (hc : checkA22 c = true) : IsZeroSys c c.S (zhatV c hc) := (zhatV_spec hc).2.2.1

theorem zhatV_inBoxR (hc : checkA22 c = true) : InBoxR c c.r0 (zhatV c hc) := (zhatV_spec hc).1

theorem inBoxR_mono {r r' : ℚ} (h : r ≤ r') {z : Vec} (hz : InBoxR c r z) : InBoxR c r' z :=
  fun k => le_trans (hz k) (by exact_mod_cast h)

theorem zhatV_memBox_r0 (hc : checkA22 c = true) : MemBox (boxArr c c.r0) (zhatV c hc) :=
  memBox_of_inBoxR (shapeOK_parts (checkA22_parts hc).1).1 (zhatV_inBoxR hc)

theorem zhatV_memBox_rN (hc : checkA22 c = true) : MemBox (boxArr c c.rN) (zhatV c hc) :=
  memBox_of_inBoxR (shapeOK_parts (checkA22_parts hc).1).1
    (inBoxR_mono (shapeOK_parts (checkA22_parts hc).1).2.2.2.1 (zhatV_inBoxR hc))

/-- Uniqueness of the zero in the LARGE box `N = box(z0, r_N)`. -/
theorem zhatV_unique_N (hc : checkA22 c = true) {y : Vec} (hy : MemBox (boxArr c c.rN) y)
    (hz : IsZeroSys c c.S y) : y = zhatV c hc := by
  obtain ⟨hsh, hK1, -⟩ := checkA22_parts hc
  obtain ⟨-, -, hr0, hr0N, -⟩ := shapeOK_parts hsh
  obtain ⟨yN, -, -, -, huniq⟩ := krawczyk_sound (shape_of_shapeOK hsh).1 (lt_of_lt_of_le hr0 hr0N) hK1
  rw [huniq y hy hz, huniq (zhatV c hc) (zhatV_memBox_rN hc) (zhatV_zero hc)]

/-- Interval facts at `ẑ` over the two boxes. -/
theorem mem_eval_r0 (hc : checkA22 c = true) (e : Expr) :
    Mem (eval (zhatV c hc) e) (evalIV (radBox c.z0 c.r0) e) := by
  rw [radBox_eq]; exact evalIV_sound (zhatV_memBox_r0 hc) e

theorem mem_eval_rN (hc : checkA22 c = true) (e : Expr) :
    Mem (eval (zhatV c hc) e) (evalIV (radBox c.z0 c.rN) e) := by
  rw [radBox_eq]; exact evalIV_sound (zhatV_memBox_rN hc) e

/-! ## Structure facts -/

theorem feasibleOK_parts (hF : feasibleOK c = true) :
    anglesSmall (radBox c.z0 c.r0) = true ∧ tiltOK c (radBox c.z0 c.r0) = true ∧
    pairsOK c (angRel c) (knownFix c (radBox c.z0 c.r0)) (radBox c.z0 c.r0) = true ∧
    wallsOK c (radBox c.z0 c.r0) = true := by
  simp only [feasibleOK, Bool.and_eq_true] at hF
  exact ⟨hF.1.1.1, hF.1.1.2, hF.1.2, hF.2⟩

theorem zhatV_smallTilt (hc : checkA22 c = true) : SmallTilt (zhatV c hc) := by
  obtain ⟨-, -, -, -, -, hF⟩ := checkA22_parts hc
  obtain ⟨hA, -⟩ := feasibleOK_parts hF
  intro i hi
  simp only [anglesSmall, List.all_eq_true, rng_eq, List.mem_range, Bool.and_eq_true, decide_eq_true_eq] at hA
  obtain ⟨h1, h2⟩ := hA i hi
  have hm := mem_eval_r0 hc (.var (3 * i + 2))
  simp only [evalIV, eval] at hm
  obtain ⟨hm1, hm2⟩ := hm
  have h1' := rabs_le_one_cast h1
  have h2' := rabs_le_one_cast h2
  rw [abs_le] at h1' h2' ⊢
  unfold thZ
  exact ⟨by linarith [h1'.1], by linarith [h2'.2]⟩

theorem zhatV_tilt_lt_pi (hc : checkA22 c = true) {i : ℕ} (hi : i < 11) :
    |thZ (zhatV c hc) i| < Real.pi := abs_lt_pi_of_le_one (zhatV_smallTilt hc i hi)

theorem wall_zero (hc : checkA22 c = true) {i k w : ℕ} (h : wallInS c i k w = true) :
    eval (zhatV c hc) (rowExpr (.wall i k w)) = 0 :=
  row_zero_of_any (zhatV_zero hc) (shapeOK_parts (checkA22_parts hc).1).2.1 h

theorem edge_zero (hc : checkA22 c = true) {i k j e : ℕ} (h : edgeInS c i k j e = true) :
    eval (zhatV c hc) (edgeRow i k j e) = 0 :=
  row_zero_of_any (zhatV_zero hc) (shapeOK_parts (checkA22_parts hc).1).2.1 h

theorem dist_zero (hc : checkA22 c = true) {i j : ℕ} (h : c.S.any (fun r => c.row r == Row.dist i j) = true) :
    eval (zhatV c hc) (rowExpr (.dist i j)) = 0 :=
  row_zero_of_any (zhatV_zero hc) (shapeOK_parts (checkA22_parts hc).1).2.1 h

/-- The validity margins of every `S` edge row hold over `box(z0, r)` (`validityOK`). -/
theorem validity_of_any {S : Array ℕ} {bx : Array IV} (hV : validityOK c S (Box.ofArray bx) = true)
    {z : Vec} (hz : MemBox bx z) {i k j e : ℕ} (h : S.any (fun r => c.row r == Row.edge i k j e) = true) :
    |eval z (tanE i k j e)| < 1 / 2 ∧ -1 / 2 < eval z (depE i k j e) := by
  rw [Array.any_eq_true] at h
  obtain ⟨idx, hidx, hR⟩ := h
  rw [beq_iff_eq] at hR
  simp only [validityOK, Array.all_eq_true] at hV
  have := hV idx hidx
  rw [hR] at this
  simp only [Bool.and_eq_true, decide_eq_true_eq] at this
  obtain ⟨h1, h2⟩ := this
  have hm1 := mem_mag (evalIV_sound hz (tanE i k j e))
  have hm2 := (evalIV_sound hz (depE i k j e)).1
  have h1' : (((evalIV (Box.ofArray bx) (tanE i k j e)).mag : ℚ) : ℝ) < ((1 / 2 : ℚ) : ℝ) := by
    exact_mod_cast h1
  have h2' : (((-1 / 2 : ℚ)) : ℝ) < (((evalIV (Box.ofArray bx) (depE i k j e)).lo : ℚ) : ℝ) := by
    exact_mod_cast h2
  push_cast at h1' h2'
  exact ⟨by linarith, by linarith⟩

theorem tan_margin (hc : checkA22 c = true) {i k j e : ℕ} (h : edgeInS c i k j e = true) :
    |eval (zhatV c hc) (tanE i k j e)| < 1 / 2 ∧ -1 / 2 < eval (zhatV c hc) (depE i k j e) := by
  obtain ⟨-, -, -, hV, -⟩ := checkA22_parts hc
  rw [radBox_eq] at hV
  exact validity_of_any hV (zhatV_memBox_rN hc) h

/-- Upright witness ⟹ `θ_i = 0`. -/
theorem upright_zero (hc : checkA22 c = true) {i : ℕ} (hi : i < 11) (h : uprightW c i = true) :
    thZ (zhatV c hc) i = 0 := by
  simp only [uprightW, List.any_eq_true, rng_eq, List.mem_range, Bool.and_eq_true] at h
  obtain ⟨w1, hw1, k1, hk1, h1, h2⟩ := h
  exact theta_zero_of_sin (zhatV_smallTilt hc i hi)
    (sin_zero_of_mates hk1 hw1 (wall_zero hc h1) (wall_zero hc h2))

theorem nh_par_cast {e e2 : ℕ} (h : nhx e * nhx e2 + nhy e * nhy e2 ≠ (0 : ℚ)) :
    (nhx e : ℝ) * nhx e2 + (nhy e : ℝ) * nhy e2 ≠ 0 := by
  intro hc
  apply h
  exact_mod_cast hc

/-- Direct equal-angle witness ⟹ `θ_i = θ_j`. -/
theorem angDirect_sound (hc : checkA22 c = true) {i j : ℕ} (hi : i < 11) (hj : j < 11)
    (h : angDirect c i j = true) : thZ (zhatV c hc) i = thZ (zhatV c hc) j := by
  simp only [angDirect, List.any_eq_true, rng_eq, List.mem_range, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨e, he, k, hk, e2, he2, k2, hk2, ⟨⟨⟨hA, hB⟩, hck⟩, hck2⟩, hpar⟩ := h
  exact theta_eq_of_pair (zhatV_smallTilt hc i hi) (zhatV_smallTilt hc j hj) he he2 hck hck2
    (nh_par_cast hpar) (edge_zero hc hA) (edge_zero hc hB) (tan_margin hc hA).1

/-! ### The angle relation -/

theorem relGet_ofFn (g : Fin 11 → Fin 11 → Bool) {i j : ℕ} (hi : i < 11) (hj : j < 11) :
    relGet (Array.ofFn fun i => Array.ofFn fun j => g i j) i j = g ⟨i, hi⟩ ⟨j, hj⟩ := by
  unfold relGet
  have h1 : (Array.ofFn fun i => Array.ofFn fun j => g i j).getD i #[]
      = Array.ofFn fun j => g ⟨i, hi⟩ j := by
    rw [getD_of_lt _ (by simpa using hi)]
    simp
  rw [h1, getD_of_lt _ (by simpa using hj)]
  simp

theorem relGet_ofFn_false (g : Fin 11 → Fin 11 → Bool) {i j : ℕ} (h : ¬ (i < 11 ∧ j < 11)) :
    relGet (Array.ofFn fun i => Array.ofFn fun j => g i j) i j = false := by
  unfold relGet
  by_cases hi : i < 11
  · have hj : ¬ j < 11 := fun hj => h ⟨hi, hj⟩
    have h1 : (Array.ofFn fun i => Array.ofFn fun j => g i j).getD i #[]
        = Array.ofFn fun j => g ⟨i, hi⟩ j := by
      rw [getD_of_lt _ (by simpa using hi)]
      simp
    rw [h1, getD_of_ge _ (by simpa using hj)]
  · have h1 : (Array.ofFn fun i => Array.ofFn fun j => g i j).getD i #[] = #[] :=
      getD_of_ge _ (by simpa using hi) _
    rw [h1]
    simp

/-- Soundness of a relation array: `true` entries are equal angles. -/
def RelSound (z : Vec) (R : Array (Array Bool)) : Prop :=
  ∀ i j, relGet R i j = true → thZ z i = thZ z j

theorem angBase_sound (hc : checkA22 c = true) : RelSound (zhatV c hc) (angBase c) := by
  intro i j h
  by_cases hij : i < 11 ∧ j < 11
  · unfold angBase at h
    rw [relGet_ofFn _ hij.1 hij.2] at h
    simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq, Fin.mk.injEq] at h
    rcases h with ((h | h) | h) | ⟨h1, h2⟩
    · rw [h]
    · exact angDirect_sound hc hij.1 hij.2 h
    · exact (angDirect_sound hc hij.2 hij.1 h).symm
    · rw [upright_zero hc hij.1 h1, upright_zero hc hij.2 h2]
  · unfold angBase at h
    rw [relGet_ofFn_false _ hij] at h
    exact absurd h Bool.false_ne_true

theorem relStep_sound {z : Vec} {R : Array (Array Bool)} (hR : RelSound z R) :
    RelSound z (relStep R) := by
  intro i j h
  by_cases hij : i < 11 ∧ j < 11
  · unfold relStep at h
    rw [relGet_ofFn _ hij.1 hij.2] at h
    simp only [Bool.or_eq_true, List.any_eq_true, rng_eq, List.mem_range, Bool.and_eq_true] at h
    rcases h with h | ⟨m, -, h1, h2⟩
    · exact hR i j h
    · exact (hR i m h1).trans (hR m j h2)
  · unfold relStep at h
    rw [relGet_ofFn_false _ hij] at h
    exact absurd h Bool.false_ne_true

theorem angRel_sound (hc : checkA22 c = true) : RelSound (zhatV c hc) (angRel c) :=
  relStep_sound (relStep_sound (relStep_sound (relStep_sound (angBase_sound hc))))

/-! ### Known centre coordinates -/

/-- Soundness of a `Known` table at `z`: every recorded affine expression is exact. -/
def KnownSound (z : Vec) (K : Known) : Prop :=
  ∀ i, (∀ a b : ℚ, kx K i = some (a, b) → cxZ z i = (a : ℝ) + (b : ℝ) * sZ z) ∧
       (∀ a b : ℚ, ky K i = some (a, b) → cyZ z i = (a : ℝ) + (b : ℝ) * sZ z)

theorem wallKnown_sound_x (hc : checkA22 c = true) {i : ℕ} (h0 : thZ (zhatV c hc) i = 0)
    {a b : ℚ} (h : wallKnown c i 0 2 hx = some (a, b)) :
    cxZ (zhatV c hc) i = (a : ℝ) + (b : ℝ) * sZ (zhatV c hc) := by
  have key : ∀ (wa : ℕ) (bb : ℚ) (k : ℕ),
      (if wallInS c i k wa then some (-hx k, bb) else none) = some (a, b) →
      wallInS c i k wa = true ∧ a = -hx k ∧ b = bb := by
    intro wa bb k hk
    by_cases hw : wallInS c i k wa = true
    · rw [if_pos hw, Option.some.injEq, Prod.mk.injEq] at hk
      exact ⟨hw, hk.1.symm, hk.2.symm⟩
    · rw [if_neg hw] at hk
      exact absurd hk (by simp)
  unfold wallKnown at h
  split at h
  · next v hv =>
    rw [Option.some.injEq] at h
    subst h
    obtain ⟨k, -, hk⟩ := List.exists_of_findSome?_eq_some hv
    obtain ⟨hw, rfl, rfl⟩ := key 0 0 k hk
    have := wall_zero hc hw
    rw [eval_wall] at this
    simp only [cornerP_fst, h0, Real.cos_zero, Real.sin_zero] at this
    norm_num at this
    push_cast; linarith
  · obtain ⟨k, -, hk⟩ := List.exists_of_findSome?_eq_some h
    obtain ⟨hw, rfl, rfl⟩ := key 2 1 k hk
    have := wall_zero hc hw
    rw [eval_wall] at this
    simp only [cornerP_fst, h0, Real.cos_zero, Real.sin_zero] at this
    norm_num at this
    push_cast; linarith

theorem wallKnown_sound_y (hc : checkA22 c = true) {i : ℕ} (h0 : thZ (zhatV c hc) i = 0)
    {a b : ℚ} (h : wallKnown c i 1 3 hy = some (a, b)) :
    cyZ (zhatV c hc) i = (a : ℝ) + (b : ℝ) * sZ (zhatV c hc) := by
  have key : ∀ (wa : ℕ) (bb : ℚ) (k : ℕ),
      (if wallInS c i k wa then some (-hy k, bb) else none) = some (a, b) →
      wallInS c i k wa = true ∧ a = -hy k ∧ b = bb := by
    intro wa bb k hk
    by_cases hw : wallInS c i k wa = true
    · rw [if_pos hw, Option.some.injEq, Prod.mk.injEq] at hk
      exact ⟨hw, hk.1.symm, hk.2.symm⟩
    · rw [if_neg hw] at hk
      exact absurd hk (by simp)
  unfold wallKnown at h
  split at h
  · next v hv =>
    rw [Option.some.injEq] at h
    subst h
    obtain ⟨k, -, hk⟩ := List.exists_of_findSome?_eq_some hv
    obtain ⟨hw, rfl, rfl⟩ := key 1 0 k hk
    have := wall_zero hc hw
    rw [eval_wall] at this
    simp only [cornerP_snd, h0, Real.cos_zero, Real.sin_zero] at this
    norm_num at this
    push_cast; linarith
  · obtain ⟨k, -, hk⟩ := List.exists_of_findSome?_eq_some h
    obtain ⟨hw, rfl, rfl⟩ := key 3 1 k hk
    have := wall_zero hc hw
    rw [eval_wall] at this
    simp only [cornerP_snd, h0, Real.cos_zero, Real.sin_zero] at this
    norm_num at this
    push_cast; linarith

theorem knownInit_sound (hc : checkA22 c = true) : KnownSound (zhatV c hc) (knownInit c) := by
  intro i
  by_cases hi : i < 11
  · have hget : (knownInit c).getD i (none, none)
        = if uprightW c i then (wallKnown c i 0 2 hx, wallKnown c i 1 3 hy) else (none, none) := by
      unfold knownInit
      rw [getD_of_lt _ (by simpa using hi)]
      simp
    by_cases hu : uprightW c i = true
    · have h0 := upright_zero hc hi hu
      rw [if_pos hu] at hget
      simp only [kx, ky, hget]
      exact ⟨fun a b h => wallKnown_sound_x hc h0 h, fun a b h => wallKnown_sound_y hc h0 h⟩
    · rw [if_neg hu] at hget
      simp only [kx, ky, hget]
      exact ⟨fun a b h => absurd h (by simp), fun a b h => absurd h (by simp)⟩
  · have hget : (knownInit c).getD i (none, none) = (none, none) := by
      unfold knownInit
      exact getD_of_ge _ (by simpa using hi) _
    simp only [kx, ky, hget]
    exact ⟨fun a b h => absurd h (by simp), fun a b h => absurd h (by simp)⟩

theorem setKx_sound {z : Vec} {K : Known} (hK : KnownSound z K) {j : ℕ} {v : Aff}
    (hv : cxZ z j = (v.1 : ℝ) + (v.2 : ℝ) * sZ z) : KnownSound z (setKx K j v) := by
  intro t
  by_cases ht : t < 11
  · have hget : (setKx K j v).getD t (none, none)
        = if t = j then (some v, ky K t) else K.getD t (none, none) := by
      unfold setKx
      rw [getD_of_lt _ (by simpa using ht)]
      simp
    by_cases htj : t = j
    · subst htj
      rw [if_pos rfl] at hget
      simp only [kx, ky, hget]
      refine ⟨fun a b h => ?_, fun a b h => (hK t).2 a b h⟩
      rw [Option.some.injEq] at h
      subst h
      simpa using hv
    · rw [if_neg htj] at hget
      simp only [kx, ky, hget]
      exact hK t
  · have hget : (setKx K j v).getD t (none, none) = (none, none) := by
      unfold setKx
      exact getD_of_ge _ (by simpa using ht) _
    simp only [kx, ky, hget]
    exact ⟨fun a b h => absurd h (by simp), fun a b h => absurd h (by simp)⟩

theorem setKy_sound {z : Vec} {K : Known} (hK : KnownSound z K) {j : ℕ} {v : Aff}
    (hv : cyZ z j = (v.1 : ℝ) + (v.2 : ℝ) * sZ z) : KnownSound z (setKy K j v) := by
  intro t
  by_cases ht : t < 11
  · have hget : (setKy K j v).getD t (none, none)
        = if t = j then (kx K t, some v) else K.getD t (none, none) := by
      unfold setKy
      rw [getD_of_lt _ (by simpa using ht)]
      simp
    by_cases htj : t = j
    · subst htj
      rw [if_pos rfl] at hget
      simp only [kx, ky, hget]
      refine ⟨fun a b h => (hK t).1 a b h, fun a b h => ?_⟩
      rw [Option.some.injEq] at h
      subst h
      simpa using hv
    · rw [if_neg htj] at hget
      simp only [kx, ky, hget]
      exact hK t
  · have hget : (setKy K j v).getD t (none, none) = (none, none) := by
      unfold setKy
      exact getD_of_ge _ (by simpa using ht) _
    simp only [kx, ky, hget]
    exact ⟨fun a b h => absurd h (by simp), fun a b h => absurd h (by simp)⟩

/-- The interval sign test is sound on the box. -/
theorem signIV_sound {b : Array IV} {z : Vec} (hz : MemBox b z) {p q : ℕ} {σ : ℚ}
    (h : signIV (Box.ofArray b) p q = some σ) :
    (σ = 1 ∧ 0 < getV z q - getV z p) ∨ (σ = -1 ∧ getV z q - getV z p < 0) := by
  simp only [signIV] at h
  have hm := mem_sub (mem_get hz q) (mem_get hz p)
  split_ifs at h with h1 h2
  · rw [Option.some.injEq] at h
    left
    refine ⟨h.symm, ?_⟩
    have : ((0 : ℚ) : ℝ) < (((Box.ofArray b).get q - (Box.ofArray b).get p).lo : ℝ) := by
      exact_mod_cast h1
    push_cast at this
    linarith [hm.1]
  · rw [Option.some.injEq] at h
    right
    refine ⟨h.symm, ?_⟩
    have : ((((Box.ofArray b).get q - (Box.ofArray b).get p).hi : ℚ) : ℝ) < ((0 : ℚ) : ℝ) := by
      exact_mod_cast h2
    push_cast at this
    linarith [hm.2]

theorem sq_eq_one_cases {x : ℝ} (h : x ^ 2 = 1) : x = 1 ∨ x = -1 := by
  have : (x - 1) * (x + 1) = 0 := by ring_nf; linarith
  rcases mul_eq_zero.mp this with h | h
  · left; linarith
  · right; linarith

set_option maxHeartbeats 800000 in
-- the 5-way match with nested option/pair patterns is elaboration-heavy
/-- The `x`-propagation of a dist row is sound when the row vanishes. -/
theorem propX_sound {b : Array IV} {z : Vec} (hz : MemBox b z) {K : Known} (hK : KnownSound z K)
    {i j : ℕ} (hd : (cxZ z i - cxZ z j) ^ 2 + (cyZ z i - cyZ z j) ^ 2 - 1 = 0) :
    KnownSound z (propX (Box.ofArray b) K i j) := by
  unfold propX
  split
  · next yi yj a b σ hyi hyj hxi hxj hσ =>
    split_ifs with hyy
    · refine setKx_sound hK ?_
      subst hyy
      have hyi' := (hK i).2 yi.1 yi.2 hyi
      have hyj' := (hK j).2 yi.1 yi.2 hyj
      have hxi' := (hK i).1 a b hxi
      have hcy : cyZ z i - cyZ z j = 0 := by rw [hyi', hyj']; ring
      rw [hcy] at hd
      have hcx := sq_eq_one_cases (x := cxZ z i - cxZ z j) (by linarith)
      rcases signIV_sound hz hσ with ⟨rfl, hs⟩ | ⟨rfl, hs⟩
      · change cxZ z j = ((a + 1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change 0 < cxZ z j - cxZ z i at hs
        push_cast
        rcases hcx with h | h <;> linarith
      · change cxZ z j = ((a + -1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change cxZ z j - cxZ z i < 0 at hs
        push_cast
        rcases hcx with h | h <;> linarith
    · exact hK
  · next yi yj a b σ hyi hyj hxi hxj hσ =>
    split_ifs with hyy
    · refine setKx_sound hK ?_
      subst hyy
      have hyi' := (hK i).2 yi.1 yi.2 hyi
      have hyj' := (hK j).2 yi.1 yi.2 hyj
      have hxj' := (hK j).1 a b hxj
      have hcy : cyZ z i - cyZ z j = 0 := by rw [hyi', hyj']; ring
      rw [hcy] at hd
      have hcx := sq_eq_one_cases (x := cxZ z i - cxZ z j) (by linarith)
      rcases signIV_sound hz hσ with ⟨rfl, hs⟩ | ⟨rfl, hs⟩
      · change cxZ z i = ((a - 1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change 0 < cxZ z j - cxZ z i at hs
        push_cast
        rcases hcx with h | h <;> linarith
      · change cxZ z i = ((a - -1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change cxZ z j - cxZ z i < 0 at hs
        push_cast
        rcases hcx with h | h <;> linarith
    · exact hK
  · exact hK

set_option maxHeartbeats 800000 in
-- the 5-way match with nested option/pair patterns is elaboration-heavy
/-- The `y`-propagation of a dist row is sound when the row vanishes. -/
theorem propY_sound {b : Array IV} {z : Vec} (hz : MemBox b z) {K : Known} (hK : KnownSound z K)
    {i j : ℕ} (hd : (cxZ z i - cxZ z j) ^ 2 + (cyZ z i - cyZ z j) ^ 2 - 1 = 0) :
    KnownSound z (propY (Box.ofArray b) K i j) := by
  unfold propY
  split
  · next xi xj a b σ hxi hxj hyi hyj hσ =>
    split_ifs with hxx
    · refine setKy_sound hK ?_
      subst hxx
      have hxi' := (hK i).1 xi.1 xi.2 hxi
      have hxj' := (hK j).1 xi.1 xi.2 hxj
      have hyi' := (hK i).2 a b hyi
      have hcx : cxZ z i - cxZ z j = 0 := by rw [hxi', hxj']; ring
      rw [hcx] at hd
      have hcy := sq_eq_one_cases (x := cyZ z i - cyZ z j) (by linarith)
      rcases signIV_sound hz hσ with ⟨rfl, hs⟩ | ⟨rfl, hs⟩
      · change cyZ z j = ((a + 1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change 0 < cyZ z j - cyZ z i at hs
        push_cast
        rcases hcy with h | h <;> linarith
      · change cyZ z j = ((a + -1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change cyZ z j - cyZ z i < 0 at hs
        push_cast
        rcases hcy with h | h <;> linarith
    · exact hK
  · next xi xj a b σ hxi hxj hyi hyj hσ =>
    split_ifs with hxx
    · refine setKy_sound hK ?_
      subst hxx
      have hxi' := (hK i).1 xi.1 xi.2 hxi
      have hxj' := (hK j).1 xi.1 xi.2 hxj
      have hyj' := (hK j).2 a b hyj
      have hcx : cxZ z i - cxZ z j = 0 := by rw [hxi', hxj']; ring
      rw [hcx] at hd
      have hcy := sq_eq_one_cases (x := cyZ z i - cyZ z j) (by linarith)
      rcases signIV_sound hz hσ with ⟨rfl, hs⟩ | ⟨rfl, hs⟩
      · change cyZ z i = ((a - 1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change 0 < cyZ z j - cyZ z i at hs
        push_cast
        rcases hcy with h | h <;> linarith
      · change cyZ z i = ((a - -1 : ℚ) : ℝ) + (b : ℝ) * sZ z
        change cyZ z j - cyZ z i < 0 at hs
        push_cast
        rcases hcy with h | h <;> linarith
    · exact hK
  · exact hK

/-- One dist propagation is sound when the dist row vanishes. -/
theorem propDist_sound {b : Array IV} {z : Vec} (hz : MemBox b z) {K : Known} (hK : KnownSound z K)
    {i j : ℕ} (hd : eval z (rowExpr (.dist i j)) = 0) :
    KnownSound z (propDist (Box.ofArray b) K i j) := by
  rw [eval_dist] at hd
  unfold propDist
  exact propY_sound hz (propX_sound hz hK hd) hd

theorem foldl_preserve_mem {α β : Type} {P : β → Prop} {f : β → α → β} :
    ∀ (l : List α), (∀ a ∈ l, ∀ b, P b → P (f b a)) → ∀ {b : β}, P b → P (l.foldl f b)
  | [], _, _, hb => hb
  | a :: l, hf, b, hb =>
    foldl_preserve_mem l (fun x hx => hf x (List.mem_cons_of_mem a hx))
      (hf a (List.mem_cons_self ..) b hb)

theorem row_zero_of_mem {S : Array ℕ} {z : Vec} (hz : IsZeroSys c S z) (hS : S.size = NV)
    {r : ℕ} (hr : r ∈ S) : eval z (rowExpr (c.row r)) = 0 := by
  obtain ⟨idx, hidx, rfl⟩ := Array.mem_iff_getElem.mp hr
  have hidx' : idx < NV := by rw [hS] at hidx; exact hidx
  have := hz ⟨idx, hidx'⟩
  simp only [rowE] at this
  rw [getD_of_lt _ hidx] at this
  exact this

theorem knownStep_sound (hc : checkA22 c = true) {K : Known} (hK : KnownSound (zhatV c hc) K) :
    KnownSound (zhatV c hc) (knownStep c (radBox c.z0 c.r0) K) := by
  unfold knownStep
  rw [← Array.foldl_toList]
  refine foldl_preserve_mem (P := KnownSound (zhatV c hc)) c.S.toList ?_ hK
  intro r hr K hKr
  have hmem : r ∈ c.S := by simpa using hr
  split
  · next i j hrow =>
    split_ifs with hu
    · rw [radBox_eq]
      refine propDist_sound (zhatV_memBox_r0 hc) hKr ?_
      have := row_zero_of_mem (zhatV_zero hc) (shapeOK_parts (checkA22_parts hc).1).2.1 hmem
      rw [hrow] at this
      exact this
    · exact hKr
  · exact hKr

theorem knownIter_sound (hc : checkA22 c = true) :
    ∀ (n : ℕ) (K : Known), KnownSound (zhatV c hc) K →
      KnownSound (zhatV c hc) (knownIter c (radBox c.z0 c.r0) n K)
  | 0, _, h => h
  | n + 1, K, h => knownIter_sound hc n _ (knownStep_sound hc h)

theorem knownFix_sound (hc : checkA22 c = true) :
    KnownSound (zhatV c hc) (knownFix c (radBox c.z0 c.r0)) :=
  knownIter_sound hc 11 _ (knownInit_sound hc)

theorem affUnit_sound {u v : Option Aff} {x y s : ℝ}
    (hu : ∀ a b : ℚ, u = some (a, b) → x = (a : ℝ) + (b : ℝ) * s)
    (hv : ∀ a b : ℚ, v = some (a, b) → y = (a : ℝ) + (b : ℝ) * s)
    (h : affUnit u v = true) : |x - y| = 1 := by
  unfold affUnit at h
  split at h
  · next a b a' b' =>
    simp only [Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨hb, hab⟩ := h
    rw [hu a b rfl, hv a' b' rfl, hb]
    have : ((CaseI.rabs (a - a') : ℚ) : ℝ) = ((1 : ℚ) : ℝ) := by rw [hab]
    rw [rabs_cast] at this
    push_cast at this
    rw [← this]
    congr 1
    ring
  · exact absurd h Bool.false_ne_true

theorem pairUpright_sound (hc : checkA22 c = true) {i j : ℕ} (hi : i < 11) (hj : j < 11)
    (h : pairUprightOK c (knownFix c (radBox c.z0 c.r0)) i j = true) :
    Disjoint (interior (sqZ (zhatV c hc) i).set) (interior (sqZ (zhatV c hc) j).set) := by
  simp only [pairUprightOK, Bool.and_eq_true, Bool.or_eq_true] at h
  obtain ⟨⟨hui, huj⟩, hx | hy⟩ := h
  · exact disjoint_upright (upright_zero hc hi hui) (upright_zero hc hj huj)
      (Or.inl (affUnit_sound ((knownFix_sound hc) i).1 ((knownFix_sound hc) j).1 hx))
  · exact disjoint_upright (upright_zero hc hi hui) (upright_zero hc hj huj)
      (Or.inr (affUnit_sound ((knownFix_sound hc) i).2 ((knownFix_sound hc) j).2 hy))

theorem perp_cast {e k k' : ℕ} (h : nhx e * (hx k - hx k') + nhy e * (hy k - hy k') = (0 : ℚ)) :
    (nhx e : ℝ) * ((hx k : ℝ) - hx k') + (nhy e : ℝ) * ((hy k : ℝ) - hy k') = 0 := by
  exact_mod_cast h

theorem cornerRowOK_sound (hc : checkA22 c = true) {p k o e : ℕ}
    (h : cornerRowOK c (angRel c) (radBox c.z0 c.r0) p k o e = true) :
    0 ≤ eval (zhatV c hc) (edgeRow p k o e) := by
  simp only [cornerRowOK, Bool.or_eq_true, decide_eq_true_eq, Bool.and_eq_true, List.any_eq_true,
    rng_eq, List.mem_range] at h
  rcases h with (hlo | hS) | ⟨hrel, k', -, hS', hperp⟩
  · have hm := (mem_eval_r0 hc (edgeRow p k o e)).1
    have : ((0 : ℚ) : ℝ) < (((evalIV (radBox c.z0 c.r0) (edgeRow p k o e)).lo : ℚ) : ℝ) := by
      exact_mod_cast hlo
    push_cast at this
    linarith
  · exact le_of_eq (edge_zero hc hS).symm
  · have hθ := angRel_sound hc p o hrel
    exact le_of_eq (row_transfer hθ (perp_cast hperp) (edge_zero hc hS')).symm

theorem pairOK_sound (hc : checkA22 c = true) {i j : ℕ} (hi : i < 11) (hj : j < 11)
    (h : pairOK c (angRel c) (knownFix c (radBox c.z0 c.r0)) (radBox c.z0 c.r0) i j = true) :
    Disjoint (interior (sqZ (zhatV c hc) i).set) (interior (sqZ (zhatV c hc) j).set) := by
  simp only [pairOK, Bool.or_eq_true] at h
  rcases h with h | h
  · simp only [List.any_eq_true, List.mem_cons, List.mem_singleton, List.not_mem_nil, or_false,
      rng_eq, List.mem_range, List.all_eq_true] at h
    obtain ⟨⟨o, p⟩, hop, e, he, hk⟩ := h
    have hrows : ∀ k, k < 4 → 0 ≤ eval (zhatV c hc) (edgeRow p k o e) :=
      fun k hk' => cornerRowOK_sound hc (hk k hk')
    rcases hop with hop | hop <;> simp only [Prod.mk.injEq] at hop <;> obtain ⟨rfl, rfl⟩ := hop
    · exact (disjoint_of_rows (zhatV_tilt_lt_pi hc hj) (zhatV_tilt_lt_pi hc hi) he hrows).symm
    · exact disjoint_of_rows (zhatV_tilt_lt_pi hc hi) (zhatV_tilt_lt_pi hc hj) he hrows
  · exact pairUpright_sound hc hi hj h

theorem wperp_cast {w k k' : ℕ} (h : wnx w * (hx k - hx k') + wny w * (hy k - hy k') = (0 : ℚ)) :
    (wnx w : ℝ) * ((hx k : ℝ) - hx k') + (wny w : ℝ) * ((hy k : ℝ) - hy k') = 0 := by
  exact_mod_cast h

theorem wallOK_sound (hc : checkA22 c = true) {i k w : ℕ} (hi : i < 11) (hw : w < 4)
    (h : wallOK c (radBox c.z0 c.r0) i k w = true) :
    0 ≤ eval (zhatV c hc) (rowExpr (.wall i k w)) := by
  simp only [wallOK, Bool.or_eq_true, decide_eq_true_eq, Bool.and_eq_true, List.any_eq_true,
    rng_eq, List.mem_range] at h
  rcases h with (hlo | hS) | ⟨hu, k', -, hS', hperp⟩
  · have hm := (mem_eval_r0 hc (rowExpr (.wall i k w))).1
    have : ((0 : ℚ) : ℝ) < (((evalIV (radBox c.z0 c.r0) (rowExpr (.wall i k w))).lo : ℚ) : ℝ) := by
      exact_mod_cast hlo
    push_cast at this
    linarith
  · exact le_of_eq (wall_zero hc hS).symm
  · exact le_of_eq (wall_transfer (upright_zero hc hi hu) (wperp_cast hperp) hw (wall_zero hc hS')).symm

theorem mem_cornerList {z : Vec} {i : ℕ} (hθ : |thZ z i| < Real.pi) {q : RP}
    (hq : q ∈ cornerList (baseCorner (sqZ z i)) (edir (sqZ z i))) :
    ∃ k, k < 4 ∧ q = cornerP z i k := by
  obtain ⟨c0, c1, c2, c3⟩ := cornerP_eq_aff hθ
  simp only [cornerList, List.mem_cons, List.not_mem_nil, or_false] at hq
  rcases hq with rfl | rfl | rfl | rfl
  · exact ⟨0, by norm_num, c0.symm⟩
  · exact ⟨1, by norm_num, c1.symm⟩
  · exact ⟨2, by norm_num, c2.symm⟩
  · exact ⟨3, by norm_num, c3.symm⟩

theorem zhatV_contained (hc : checkA22 c = true) {i : ℕ} (hi : i < 11) :
    (sqZ (zhatV c hc) i).set ⊆ container (sZ (zhatV c hc)) := by
  obtain ⟨-, -, -, -, -, hF⟩ := checkA22_parts hc
  obtain ⟨-, -, -, hW⟩ := feasibleOK_parts hF
  simp only [wallsOK, List.all_eq_true, rng_eq, List.mem_range] at hW
  have hwall : ∀ k w, k < 4 → w < 4 → 0 ≤ eval (zhatV c hc) (rowExpr (.wall i k w)) :=
    fun k w hk hw => wallOK_sound hc hi hw (hW i hi k hk w hw)
  have hθ := zhatV_tilt_lt_pi hc hi
  have hcorner : ∀ q ∈ cornerList (baseCorner (sqZ (zhatV c hc) i)) (edir (sqZ (zhatV c hc) i)),
      0 ≤ q.1 ∧ q.1 ≤ sZ (zhatV c hc) ∧ 0 ≤ q.2 ∧ q.2 ≤ sZ (zhatV c hc) := by
    intro q hq
    obtain ⟨k, hk, rfl⟩ := mem_cornerList hθ hq
    have h0 := hwall k 0 hk (by norm_num)
    have h1 := hwall k 1 hk (by norm_num)
    have h2 := hwall k 2 hk (by norm_num)
    have h3 := hwall k 3 hk (by norm_num)
    rw [eval_wall] at h0 h1 h2 h3
    norm_num at h0 h1 h2 h3
    exact ⟨h0, by linarith, h1, by linarith⟩
  intro q hq
  refine ⟨⟨?_, ?_⟩, ?_, ?_⟩
  · exact sqSet_le_fst (fun w hw => (hcorner w hw).1) hq
  · exact sqSet_fst_le (fun w hw => (hcorner w hw).2.1) hq
  · exact sqSet_le_snd (fun w hw => (hcorner w hw).2.2.1) hq
  · exact sqSet_snd_le (fun w hw => (hcorner w hw).2.2.2) hq

/-- **`ẑ` is a feasible packing at its own side.** -/
theorem zhatV_feas (hc : checkA22 c = true) : Feas (zhatV c hc) := by
  obtain ⟨-, -, -, -, -, hF⟩ := checkA22_parts hc
  obtain ⟨-, -, hP, -⟩ := feasibleOK_parts hF
  refine ⟨fun i => ⟨_, _, rdot_edir _, rfl⟩, fun i => zhatV_contained hc i.isLt, fun i j hij => ?_⟩
  simp only [pairsOK, List.all_eq_true, rng_eq, List.mem_range, Bool.or_eq_true, decide_eq_true_eq] at hP
  rcases lt_or_gt_of_ne (fun h => hij (Fin.ext h)) with hlt | hlt
  · exact pairOK_sound hc i.isLt j.isLt ((hP i i.isLt j j.isLt).resolve_left (not_le.mpr hlt))
  · exact (pairOK_sound hc j.isLt i.isLt ((hP j j.isLt i i.isLt).resolve_left (not_le.mpr hlt))).symm

/-- Every tilt of `ẑ` is nonnegative. -/
theorem zhatV_tilt_nonneg (hc : checkA22 c = true) {i : ℕ} (hi : i < 11) : 0 ≤ thZ (zhatV c hc) i := by
  obtain ⟨-, -, -, -, -, hF⟩ := checkA22_parts hc
  obtain ⟨-, hT, -⟩ := feasibleOK_parts hF
  simp only [tiltOK, List.all_eq_true, rng_eq, List.mem_range, Bool.or_eq_true, decide_eq_true_eq] at hT
  rcases hT i hi with hu | hlo
  · exact le_of_eq (upright_zero hc hi hu).symm
  · have hm := (mem_eval_r0 hc (.var (3 * i + 2))).1
    simp only [evalIV, eval] at hm
    have : ((0 : ℚ) : ℝ) ≤ (((radBox c.z0 c.r0).get (3 * i + 2)).lo : ℝ) := by exact_mod_cast hlo
    push_cast at this
    exact le_trans this hm

end

end PackingCert.Rigid
