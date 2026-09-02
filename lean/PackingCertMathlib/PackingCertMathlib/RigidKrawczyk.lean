import Mathlib.Topology.MetricSpace.Contracting
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Tactic
import PackingCertMathlib.RigidExpr

/-!
# Soundness of the Krawczyk test (A79, rung (b) core)

`krawczykOK c S Y r = true` ⟹ the 34-row system `F = (g_k)_{k ∈ S}` has EXACTLY ONE zero
in the (rounded) box `box(z0, r)`, and that zero lies strictly inside the true box.

Proof (A22 §3 / Neumaier): with `G(z) = z − Y·F(z)`, the mean-value theorem on the box
(`mvt_box`, one intermediate point per row) writes `G(z) − G(w) = m(ξ)·(z − w)` with
`m_ij(ξ) = δ_ij − Σ_r Y_ir ∂_j g_r(ξ_r)` enclosed by the checker's `Mrow`; the checked row
sums `β_i < 1` make `G` a contraction in the sup norm and the checked `K_i ⊂ (−r, r)` make
`G` map the box into it.  Banach gives the unique fixed point; `Y` is invertible because
`‖I − Y·J(z0)‖_∞ < 1` (Neumann), so fixed points of `G` are exactly the zeros of `F`.
-/

namespace PackingCert.Rigid

open Finset Set

/-! ## The system -/

/-- Row `rr` of the system `S`. -/
def rowE (c : A22Cert) (S : Array ℕ) (rr : ℕ) : Expr := rowExpr (c.row (S.getD rr 0))

/-- The rational centre as a real vector. -/
def z0R (c : A22Cert) : Vec := fun k => ((c.z0.getD k 0 : ℚ) : ℝ)

/-- The rounded box `box(z0, r)` (the array underlying `radBox`). -/
def boxArr (c : A22Cert) (r : ℚ) : Array IV := c.z0.map fun x => IV.mkR (x - r) (x + r)

def ptArr (c : A22Cert) : Array IV := c.z0.map IV.pt

theorem radBox_eq (c : A22Cert) (r : ℚ) : radBox c.z0 r = Box.ofArray (boxArr c r) := rfl

theorem pointBox_eq (c : A22Cert) : pointBox c.z0 = Box.ofArray (ptArr c) := rfl

/-- The true box `‖z − z0‖_∞ ≤ r`. -/
def InBoxR (c : A22Cert) (r : ℚ) (z : Vec) : Prop := ∀ k : Fin NV, |z k - z0R c k| ≤ (r : ℝ)

/-- `G(z) = z − Y·F(z)`. -/
noncomputable def Gmap (c : A22Cert) (S : Array ℕ) (Y : Array (Array ℚ)) (z : Vec) : Vec :=
  fun i => z i - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval z (rowE c S rr)

/-- `F(z) = 0` on the rows of `S`. -/
def IsZeroSys (c : A22Cert) (S : Array ℕ) (z : Vec) : Prop := ∀ rr : Fin NV, eval z (rowE c S rr) = 0

/-! ## Box facts -/

theorem memBox_of_inBoxR {c : A22Cert} {r : ℚ} (hz : c.z0.size = NV) {z : Vec}
    (h : InBoxR c r z) : MemBox (boxArr c r) z := by
  refine ⟨by simp [boxArr, hz], fun k => ?_⟩
  have hk : (k : ℕ) < (boxArr c r).size := by simp [boxArr, hz]
  rw [getD_of_lt _ hk]
  simp only [boxArr, Array.getElem_map]
  have hk' : (k : ℕ) < c.z0.size := by rw [hz]; exact k.isLt
  have hz0 : z0R c k = ((c.z0[(k : ℕ)] : ℚ) : ℝ) := by
    simp [z0R, getD_of_lt _ hk']
  have := abs_le.mp (h k)
  rw [hz0] at this
  exact mem_mkR (by push_cast; linarith) (by push_cast; linarith)

theorem inBoxR_z0 {c : A22Cert} {r : ℚ} (hr : 0 ≤ r) : InBoxR c r (z0R c) := by
  intro k
  simp only [sub_self, abs_zero]
  exact_mod_cast hr

theorem memBox_pt {c : A22Cert} (hz : c.z0.size = NV) : MemBox (ptArr c) (z0R c) := by
  refine ⟨by simp [ptArr, hz], fun k => ?_⟩
  have hk : (k : ℕ) < (ptArr c).size := by simp [ptArr, hz]
  rw [getD_of_lt _ hk]
  simp only [ptArr, Array.getElem_map]
  have hk' : (k : ℕ) < c.z0.size := by rw [hz]; exact k.isLt
  have hz0 : z0R c k = ((c.z0[(k : ℕ)] : ℚ) : ℝ) := by
    simp [z0R, getD_of_lt _ hk']
  rw [hz0]
  exact mem_pt _

/-- The box as a set: a product of closed intervals. -/
def boxSet (b : Array IV) : Set Vec :=
  Set.pi Set.univ fun k : Fin NV => Icc (((b.getD k IV.zero).lo : ℚ) : ℝ) (((b.getD k IV.zero).hi : ℚ) : ℝ)

theorem mem_boxSet_iff {b : Array IV} (hb : b.size = NV) (z : Vec) :
    z ∈ boxSet b ↔ MemBox b z := by
  simp only [boxSet, Set.mem_pi, Set.mem_univ, true_implies, Set.mem_Icc, MemBox, Mem]
  exact ⟨fun h => ⟨hb, h⟩, fun h => h.2⟩

theorem isClosed_boxSet (b : Array IV) : IsClosed (boxSet b) :=
  isClosed_set_pi fun _ _ => isClosed_Icc

/-! ## Fold lemmas -/

theorem mem_foldl_add {n : ℕ} {a : ℝ} {A : IV} (ha : Mem a A) {f : ℕ → ℝ} {g : ℕ → IV}
    (hf : ∀ i, i < n → Mem (f i) (g i)) :
    Mem (a + ∑ i ∈ range n, f i) ((List.range n).foldl (fun s i => s + g i) A) := by
  induction n with
  | zero => simpa using ha
  | succ n ih =>
    rw [List.range_succ, List.foldl_append, sum_range_succ]
    simp only [List.foldl_cons, List.foldl_nil]
    rw [← add_assoc]
    exact mem_add (ih fun i hi => hf i (by omega)) (hf n (by omega))

theorem foldl_add_eq_sum {n : ℕ} (a : ℚ) (g : ℕ → ℚ) :
    (List.range n).foldl (fun s i => s + g i) a = a + ∑ i ∈ range n, g i := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [List.range_succ, List.foldl_append, sum_range_succ]
    simp only [List.foldl_cons, List.foldl_nil]
    rw [ih, add_assoc]

/-- The rational sum over `rng NV` as a real sum over `Fin NV`. -/
theorem sum_range_NV_eq (f : ℕ → ℝ) : ∑ i ∈ range NV, f i = ∑ i : Fin NV, f i :=
  (Fin.sum_univ_eq_sum_range f NV).symm

theorem rng_eq (n : ℕ) : rng n = List.range n := rfl

theorem finNV_nonempty : (Finset.univ : Finset (Fin NV)).Nonempty :=
  ⟨⟨0, by decide⟩, Finset.mem_univ _⟩

/-- Reindexing trick: `⟨rr % NV, _⟩ = rr` for `rr : Fin NV`. -/
theorem fin_mod_self (rr : Fin NV) : (⟨(rr : ℕ) % NV, Nat.mod_lt _ (by decide)⟩ : Fin NV) = rr :=
  Fin.ext (Nat.mod_eq_of_lt rr.isLt)

/-! ## Enclosures of the checker's intermediate quantities -/

section

variable {c : A22Cert} {S : Array ℕ} {Y : Array (Array ℚ)} {r : ℚ}

theorem mem_Fcent (hz : c.z0.size = NV) (hS : S.size = NV) (rr : Fin NV) :
    Mem (eval (z0R c) (rowE c S rr)) ((Fcent c S).getD rr IV.zero) := by
  have hrr : (rr : ℕ) < (Fcent c S).size := by simp [Fcent, hS]
  rw [getD_of_lt _ hrr]
  simp only [Fcent, Array.getElem_map, pointBox_eq]
  have hrr' : (rr : ℕ) < S.size := by rw [hS]; exact rr.isLt
  have : rowE c S rr = rowExpr (c.row S[(rr : ℕ)]) := by
    simp [rowE, getD_of_lt _ hrr']
  rw [this]
  exact evalIV_sound (memBox_pt hz) _

theorem mem_Jrows (hS : S.size = NV) (hu : ∀ rw ∈ c.rows, (rowExpr rw).usesOnly (rowVars rw) = true)
    (hSr : ∀ k ∈ S, k < c.rows.size) {ξ : Vec} (hξ : MemBox (boxArr c r) ξ) (rr j : Fin NV) :
    Mem (eval ξ ((rowE c S rr).D j)) (((Jrows c S r).getD rr #[]).getD j IV.zero) := by
  have hrr : (rr : ℕ) < (Jrows c S r).size := by simp [Jrows, hS]
  rw [getD_of_lt _ hrr]
  simp only [Jrows, Array.getElem_map, radBox_eq]
  have hrr' : (rr : ℕ) < S.size := by rw [hS]; exact rr.isLt
  have hrow : rowE c S rr = rowExpr (c.row S[(rr : ℕ)]) := by
    simp [rowE, getD_of_lt _ hrr']
  rw [hrow]
  have hmem : c.row S[(rr : ℕ)] ∈ c.rows := by
    have hk := hSr S[(rr : ℕ)] (Array.getElem_mem hrr')
    unfold A22Cert.row
    rw [getD_of_lt _ hk]
    exact Array.getElem_mem hk
  exact gradDense_sound hξ _ (hu _ hmem) j

/-- The real entry `m_ij(ξ) = δ_ij − Σ_r Y_ir ∂_j g_r(ξ_r)` is enclosed by `Mrow`. -/
theorem mem_Mrow (hS : S.size = NV) (hu : ∀ rw ∈ c.rows, (rowExpr rw).usesOnly (rowVars rw) = true)
    (hSr : ∀ k ∈ S, k < c.rows.size) {ξ : Fin NV → Vec} (hξ : ∀ rr, MemBox (boxArr c r) (ξ rr))
    (i j : Fin NV) :
    Mem ((if i = j then 1 else 0) - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (ξ rr) ((rowE c S rr).D j))
      ((Mrow Y (Jrows c S r) i).getD j IV.zero) := by
  unfold Mrow
  rw [mkV_getD _ j.isLt]
  refine mem_sub ?_ ?_
  · by_cases h : i = j
    · have h' : (i : ℕ) = (j : ℕ) := by rw [h]
      rw [if_pos h, if_pos h']; exact mem_one
    · have h' : ¬ (i : ℕ) = (j : ℕ) := fun hc => h (Fin.ext hc)
      rw [if_neg h, if_neg h']; exact mem_zero
  · have := mem_foldl_add (n := NV) (a := 0) mem_zero
      (f := fun rr => ((Ymat Y i rr : ℚ) : ℝ)
        * eval (ξ ⟨rr % NV, Nat.mod_lt _ (by decide)⟩) ((rowE c S rr).D j))
      (g := fun rr => IV.pt (Ymat Y i rr) * ((Jrows c S r).getD rr #[]).getD j IV.zero)
      (fun rr hrr => by
        have hrr' : rr % NV = rr := Nat.mod_eq_of_lt hrr
        have hm := mem_Jrows (r := r) hS hu hSr (hξ ⟨rr, hrr⟩) ⟨rr, hrr⟩ ⟨j, j.isLt⟩
        simp only [hrr'] at hm ⊢
        exact mem_mul (mem_pt _) hm)
    rw [zero_add, sum_range_NV_eq] at this
    have key : (∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (ξ rr) ((rowE c S rr).D j))
        = ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ)
            * eval (ξ ⟨(rr : ℕ) % NV, Nat.mod_lt _ (by decide)⟩) ((rowE c S rr).D j) := by
      refine sum_congr rfl fun rr _ => ?_
      rw [fin_mod_self]
    rw [key]
    exact this

theorem mem_YFc (hz : c.z0.size = NV) (hS : S.size = NV) (i : Fin NV) :
    Mem (∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (z0R c) (rowE c S rr)) (YFc Y (Fcent c S) i) := by
  unfold YFc
  have := mem_foldl_add (n := NV) (a := 0) mem_zero
    (f := fun rr => ((Ymat Y i rr : ℚ) : ℝ) * eval (z0R c) (rowE c S rr))
    (g := fun rr => IV.pt (Ymat Y i rr) * (Fcent c S).getD rr IV.zero)
    (fun rr hrr => mem_mul (mem_pt _) (mem_Fcent hz hS ⟨rr, hrr⟩))
  rw [zero_add, sum_range_NV_eq] at this
  exact this

theorem mem_Krow {M : Array IV} {m : Fin NV → ℝ} (hm : ∀ j, Mem (m j) (M.getD j IV.zero))
    {yfc : ℝ} {YF : IV} (hy : Mem yfc YF) {d : Fin NV → ℝ} {dbox : IV} (hd : ∀ j, Mem (d j) dbox) :
    Mem (-yfc + ∑ j : Fin NV, m j * d j) (Krow M YF dbox) := by
  unfold Krow
  have := mem_foldl_add (n := NV) (a := -yfc) (mem_neg hy)
    (f := fun j => m ⟨j % NV, Nat.mod_lt _ (by decide)⟩ * d ⟨j % NV, Nat.mod_lt _ (by decide)⟩)
    (g := fun j => M.getD j IV.zero * dbox)
    (fun j hj => by
      have hj' : j % NV = j := Nat.mod_eq_of_lt hj
      simp only [hj']
      exact mem_mul (hm ⟨j, hj⟩) (hd ⟨j, hj⟩))
  rw [sum_range_NV_eq] at this
  have key : (∑ j : Fin NV, m j * d j)
      = ∑ j : Fin NV, m ⟨(j : ℕ) % NV, Nat.mod_lt _ (by decide)⟩
          * d ⟨(j : ℕ) % NV, Nat.mod_lt _ (by decide)⟩ := by
    refine sum_congr rfl fun j _ => ?_
    rw [fin_mod_self]
  rw [key]
  exact this

/-- `Σ_j |m_ij| ≤ β_i` for enclosed entries. -/
theorem sum_abs_le_betaRow {M : Array IV} {m : Fin NV → ℝ} (hm : ∀ j, Mem (m j) (M.getD j IV.zero)) :
    ∑ j : Fin NV, |m j| ≤ ((betaRow M : ℚ) : ℝ) := by
  unfold betaRow
  rw [rng_eq, foldl_add_eq_sum, zero_add]
  push_cast
  rw [sum_range_NV_eq]
  exact sum_le_sum fun j _ => mem_mag (hm j)

end

/-! ## The mean-value decomposition of `G` -/

section

variable {c : A22Cert} {S : Array ℕ} {Y : Array (Array ℚ)} {r : ℚ}

theorem Gmap_sub {z w : Vec} (hz : MemBox (boxArr c r) z) (hw : MemBox (boxArr c r) w) :
    ∃ ξ : Fin NV → Vec, (∀ rr, MemBox (boxArr c r) (ξ rr)) ∧
      ∀ i : Fin NV, Gmap c S Y z i - Gmap c S Y w i
        = ∑ j : Fin NV, ((if i = j then 1 else 0)
            - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (ξ rr) ((rowE c S rr).D j)) * (z j - w j) := by
  choose ξ hξ hmvt using fun rr : Fin NV => mvt_box hw hz (rowE c S rr)
  refine ⟨ξ, hξ, fun i => ?_⟩
  have e1 : ∑ j : Fin NV, (if i = j then (1 : ℝ) else 0) * (z j - w j) = z i - w i := by
    simp [ite_mul, Finset.sum_ite_eq]
  have hmvt' : ∀ rr : Fin NV, ∑ j : Fin NV, eval (ξ rr) ((rowE c S rr).D j) * (z j - w j)
      = eval z (rowE c S rr) - eval w (rowE c S rr) := fun rr => (hmvt rr).symm
  have e2 : ∑ j : Fin NV, (∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ)
        * eval (ξ rr) ((rowE c S rr).D j)) * (z j - w j)
      = ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * (eval z (rowE c S rr) - eval w (rowE c S rr)) := by
    simp only [← hmvt', Finset.mul_sum, Finset.sum_mul]
    rw [Finset.sum_comm]
    refine sum_congr rfl fun rr _ => sum_congr rfl fun j _ => by ring
  simp only [Gmap]
  have e3 : (∑ j : Fin NV, ((if i = j then (1 : ℝ) else 0)
        - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (ξ rr) ((rowE c S rr).D j)) * (z j - w j))
      = (∑ j : Fin NV, (if i = j then (1 : ℝ) else 0) * (z j - w j))
        - ∑ j : Fin NV, (∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ)
            * eval (ξ rr) ((rowE c S rr).D j)) * (z j - w j) := by
    rw [← Finset.sum_sub_distrib]
    exact sum_congr rfl fun j _ => by ring
  rw [e3, e1, e2]
  simp only [mul_sub, Finset.sum_sub_distrib]
  ring

end

/-! ## The main theorem -/

/-- Everything `krawczyk_sound` needs from `shapeOK`. -/
structure Shape (c : A22Cert) (S : Array ℕ) (Y : Array (Array ℚ)) : Prop where
  hz0 : c.z0.size = NV
  hS : S.size = NV
  huses : ∀ rw ∈ c.rows, (rowExpr rw).usesOnly (rowVars rw) = true
  hSr : ∀ k ∈ S, k < c.rows.size

theorem shape_of_shapeOK {c : A22Cert} (h : shapeOK c = true) :
    Shape c c.S c.Y ∧ Shape c c.S2 c.Y2 := by
  simp only [shapeOK, Bool.and_eq_true, decide_eq_true_eq,
    Array.all_eq_true_iff_forall_mem] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hz, hS⟩, hS2⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, hSr⟩, hS2r⟩, hu⟩, -⟩, -⟩ := h
  exact ⟨⟨hz, hS, hu, hSr⟩, ⟨hz, hS2, hu, hS2r⟩⟩

/-- The true box `‖z − z0‖_∞ ≤ r` as a set. -/
def trueBox (c : A22Cert) (r : ℚ) : Set Vec :=
  Set.pi Set.univ fun k : Fin NV => Icc (z0R c k - (r : ℝ)) (z0R c k + (r : ℝ))

theorem mem_trueBox_iff (c : A22Cert) (r : ℚ) (z : Vec) : z ∈ trueBox c r ↔ InBoxR c r z := by
  simp only [trueBox, Set.mem_pi, Set.mem_univ, true_implies, Set.mem_Icc, InBoxR, abs_le]
  constructor
  · intro h k; obtain ⟨h1, h2⟩ := h k; exact ⟨by linarith, by linarith⟩
  · intro h k; obtain ⟨h1, h2⟩ := h k; exact ⟨by linarith, by linarith⟩

theorem isClosed_trueBox (c : A22Cert) (r : ℚ) : IsClosed (trueBox c r) :=
  isClosed_set_pi fun _ _ => isClosed_Icc

theorem betaRow_nonneg (M : Array IV) : (0 : ℚ) ≤ betaRow M := by
  unfold betaRow
  rw [rng_eq, foldl_add_eq_sum, zero_add]
  exact Finset.sum_nonneg fun j _ => mag_nonneg _

/-- Sup-norm contraction from a row-sum bound on the enclosed coefficient matrix. -/
theorem abs_le_of_rowsum {m : Fin NV → Fin NV → ℝ} {β : ℝ} (hrow : ∀ i, ∑ j, |m i j| ≤ β)
    (d : Vec) (i : Fin NV) : |∑ j, m i j * d j| ≤ β * dist d 0 := by
  calc |∑ j, m i j * d j| ≤ ∑ j, |m i j| * |d j| := by
        refine (Finset.abs_sum_le_sum_abs _ _).trans ?_
        exact sum_le_sum fun j _ => by rw [abs_mul]
    _ ≤ ∑ j, |m i j| * dist d 0 := by
        refine sum_le_sum fun j _ => mul_le_mul_of_nonneg_left ?_ (abs_nonneg _)
        have := dist_le_pi_dist d 0 j
        simpa [Real.dist_eq] using this
    _ = (∑ j, |m i j|) * dist d 0 := by rw [Finset.sum_mul]
    _ ≤ β * dist d 0 := mul_le_mul_of_nonneg_right (hrow i) dist_nonneg

/-- A vector with `‖v‖ ≤ β‖v‖`, `β < 1`, vanishes. -/
theorem eq_zero_of_dist_le {v : Vec} {β : ℝ} (hβ : β < 1) (h : dist v 0 ≤ β * dist v 0) : v = 0 := by
  have h2 : dist v 0 * (1 - β) ≤ 0 := by nlinarith
  have h3 : dist v 0 ≤ 0 := by
    have : 0 < 1 - β := by linarith
    nlinarith [dist_nonneg (x := v) (y := (0 : Vec))]
  exact dist_le_zero.mp h3

theorem krawczyk_sound {c : A22Cert} {S : Array ℕ} {Y : Array (Array ℚ)} {r : ℚ}
    (hsh : Shape c S Y) (hr : 0 < r) (hK : krawczykOK c S Y r = true) :
    ∃ y : Vec, InBoxR c r y ∧ (∀ k : Fin NV, |y k - z0R c k| < (r : ℝ)) ∧ IsZeroSys c S y ∧
      ∀ y' : Vec, MemBox (boxArr c r) y' → IsZeroSys c S y' → y' = y := by
  -- unpack the check
  have hchk : ∀ i : Fin NV,
      -r < (Krow (Mrow Y (Jrows c S r) i) (YFc Y (Fcent c S) i) (IV.mkR (-r) r)).lo ∧
      (Krow (Mrow Y (Jrows c S r) i) (YFc Y (Fcent c S) i) (IV.mkR (-r) r)).hi < r ∧
      betaRow (Mrow Y (Jrows c S r) i) < 1 := by
    intro i
    simp only [krawczykOK, List.all_eq_true, Bool.and_eq_true, decide_eq_true_eq] at hK
    have := hK i (List.mem_range.mpr i.isLt)
    exact ⟨this.1.1, this.1.2, this.2⟩
  have hrR : (0 : ℝ) < (r : ℝ) := by exact_mod_cast hr
  -- the contraction constant
  set β : ℝ := Finset.univ.sup' finNV_nonempty
    (fun i : Fin NV => ((betaRow (Mrow Y (Jrows c S r) i) : ℚ) : ℝ)) with hβ
  have hβ_lt : β < 1 := by
    rw [hβ, Finset.sup'_lt_iff]
    intro i _
    exact_mod_cast (hchk i).2.2
  have hβ_ge : ∀ i : Fin NV, ((betaRow (Mrow Y (Jrows c S r) i) : ℚ) : ℝ) ≤ β := fun i =>
    Finset.le_sup' (fun i : Fin NV => ((betaRow (Mrow Y (Jrows c S r) i) : ℚ) : ℝ)) (Finset.mem_univ i)
  have hβ_nn : 0 ≤ β := le_trans (by exact_mod_cast betaRow_nonneg _) (hβ_ge ⟨0, by decide⟩)
  -- the row-sum bound for any enclosed coefficient matrix
  have hrowsum : ∀ (ξ : Fin NV → Vec), (∀ rr, MemBox (boxArr c r) (ξ rr)) → ∀ i : Fin NV,
      ∑ j : Fin NV, |(if i = j then (1 : ℝ) else 0)
        - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (ξ rr) ((rowE c S rr).D j)| ≤ β := by
    intro ξ hξ i
    exact (sum_abs_le_betaRow fun j => mem_Mrow (Y := Y) hsh.hS hsh.huses hsh.hSr hξ i j).trans (hβ_ge i)
  -- Lipschitz estimate on the rounded box
  have hlip : ∀ z w : Vec, MemBox (boxArr c r) z → MemBox (boxArr c r) w →
      dist (Gmap c S Y z) (Gmap c S Y w) ≤ β * dist z w := by
    intro z w hz hw
    obtain ⟨ξ, hξ, hG⟩ := Gmap_sub (c := c) (S := S) (Y := Y) hz hw
    rw [dist_pi_le_iff (by positivity)]
    intro i
    rw [Real.dist_eq, hG i]
    have := abs_le_of_rowsum (hrowsum ξ hξ) (fun j => z j - w j) i
    have hd : dist (fun j => z j - w j) (0 : Vec) = dist z w := by
      rw [dist_eq_norm, dist_eq_norm, sub_zero]
      rfl
    rw [hd] at this
    exact this
  -- mapping property: `G` maps the true box strictly inside itself
  have hmaps : ∀ z : Vec, InBoxR c r z → ∀ i : Fin NV, |Gmap c S Y z i - z0R c i| < (r : ℝ) := by
    intro z hz i
    have hzB := memBox_of_inBoxR hsh.hz0 hz
    have hz0B : MemBox (boxArr c r) (z0R c) := memBox_of_inBoxR hsh.hz0 (inBoxR_z0 hr.le)
    obtain ⟨ξ, hξ, hG⟩ := Gmap_sub (c := c) (S := S) (Y := Y) hzB hz0B
    have hGz0 : Gmap c S Y (z0R c) i
        = z0R c i - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (z0R c) (rowE c S rr) := rfl
    have hd : ∀ j : Fin NV, Mem (z j - z0R c j) (IV.mkR (-r) r) := by
      intro j
      have := abs_le.mp (hz j)
      exact mem_mkR (by push_cast; linarith) (by linarith)
    have hmem := mem_Krow (fun j => mem_Mrow (Y := Y) hsh.hS hsh.huses hsh.hSr hξ i j)
      (mem_YFc (Y := Y) hsh.hz0 hsh.hS i) hd
    have heq : Gmap c S Y z i - z0R c i
        = -(∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (z0R c) (rowE c S rr))
          + ∑ j : Fin NV, ((if i = j then (1 : ℝ) else 0)
            - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (ξ rr) ((rowE c S rr).D j)) * (z j - z0R c j) := by
      have := hG i
      rw [hGz0] at this
      linarith
    rw [heq, abs_lt]
    obtain ⟨hlo, hhi⟩ := hmem
    obtain ⟨h1, h2, -⟩ := hchk i
    set KK := Krow (Mrow Y (Jrows c S r) i) (YFc Y (Fcent c S) i) (IV.mkR (-r) r) with hKK
    have h1' : ((-r : ℚ) : ℝ) < ((KK.lo : ℚ) : ℝ) := by exact_mod_cast h1
    have h2' : ((KK.hi : ℚ) : ℝ) < ((r : ℚ) : ℝ) := by exact_mod_cast h2
    push_cast at h1'
    constructor
    · linarith
    · linarith
  -- Banach on the true box
  have hXc : IsComplete (trueBox c r) := (isClosed_trueBox c r).isComplete
  have hsf : MapsTo (Gmap c S Y) (trueBox c r) (trueBox c r) := by
    intro z hz
    rw [mem_trueBox_iff] at hz ⊢
    intro k
    exact (hmaps z hz k).le
  set K : NNReal := ⟨β, hβ_nn⟩ with hKdef
  have hcontr : ContractingWith K (hsf.restrict (Gmap c S Y) (trueBox c r) (trueBox c r)) := by
    refine ⟨?_, ?_⟩
    · rw [← NNReal.coe_lt_coe]; exact hβ_lt
    · refine LipschitzWith.of_dist_le_mul fun x y => ?_
      rw [Subtype.dist_eq, Subtype.dist_eq]
      simp only [MapsTo.val_restrict_apply, hKdef, NNReal.coe_mk]
      exact hlip x y (memBox_of_inBoxR hsh.hz0 ((mem_trueBox_iff c r x).mp x.2))
        (memBox_of_inBoxR hsh.hz0 ((mem_trueBox_iff c r y).mp y.2))
  have hz0X : z0R c ∈ trueBox c r := (mem_trueBox_iff c r _).mpr (inBoxR_z0 hr.le)
  obtain ⟨y, hyX, hyfix, -, -⟩ :=
    hcontr.exists_fixedPoint' hXc hsf hz0X (edist_ne_top _ _)
  have hyR : InBoxR c r y := (mem_trueBox_iff c r y).mp hyX
  have hyB : MemBox (boxArr c r) y := memBox_of_inBoxR hsh.hz0 hyR
  -- fixed points are zeros: `Y` is invertible
  have hYF : ∀ i : Fin NV, ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval y (rowE c S rr) = 0 := by
    intro i
    have := congrFun hyfix i
    simp only [Gmap] at this
    linarith
  have hzero : IsZeroSys c S y := by
    set Ym : Matrix (Fin NV) (Fin NV) ℝ := Matrix.of fun i rr => ((Ymat Y i rr : ℚ) : ℝ) with hYm
    set Jm : Matrix (Fin NV) (Fin NV) ℝ :=
      Matrix.of fun rr j => eval (z0R c) ((rowE c S rr).D j) with hJm
    have hz0B : MemBox (boxArr c r) (z0R c) := memBox_of_inBoxR hsh.hz0 (inBoxR_z0 hr.le)
    -- `Y·J` is injective (Neumann series argument)
    have hYJzero : ∀ v : Vec, (Ym * Jm).mulVec v = 0 → v = 0 := by
      intro v hv
      have hrow := hrowsum (fun _ => z0R c) (fun _ => hz0B)
      have hv' : ∀ i : Fin NV, v i = ∑ j : Fin NV, ((if i = j then (1 : ℝ) else 0)
          - ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval (z0R c) ((rowE c S rr).D j)) * v j := by
        intro i
        have h0 : ∑ j : Fin NV, (∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ)
            * eval (z0R c) ((rowE c S rr).D j)) * v j = 0 := by
          have := congrFun hv i
          simp only [Matrix.mulVec, dotProduct, Matrix.mul_apply, hYm, hJm, Matrix.of_apply,
            Pi.zero_apply] at this
          exact this
        have h1 : ∑ j : Fin NV, (if i = j then (1 : ℝ) else 0) * v j = v i := by
          simp [ite_mul, Finset.sum_ite_eq]
        calc v i = (∑ j : Fin NV, (if i = j then (1 : ℝ) else 0) * v j)
              - ∑ j : Fin NV, (∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ)
                  * eval (z0R c) ((rowE c S rr).D j)) * v j := by rw [h1, h0, sub_zero]
          _ = _ := by
              rw [← Finset.sum_sub_distrib]
              exact Finset.sum_congr rfl fun j _ => by ring
      have hb : dist v 0 ≤ β * dist v 0 := by
        rw [dist_pi_le_iff (by positivity)]
        intro i
        rw [Real.dist_eq, Pi.zero_apply, sub_zero, hv' i]
        exact abs_le_of_rowsum hrow v i
      exact eq_zero_of_dist_le hβ_lt hb
    have hYJ : Function.Injective (Ym * Jm).mulVec := by
      intro v w hvw
      have : (Ym * Jm).mulVec (v - w) = 0 := by rw [Matrix.mulVec_sub, hvw, sub_self]
      exact sub_eq_zero.mp (hYJzero _ this)
    have hunit : IsUnit Ym := by
      have h1 : IsUnit (Ym * Jm) := Matrix.mulVec_injective_iff_isUnit.mp hYJ
      rw [Matrix.isUnit_iff_isUnit_det, Matrix.det_mul, isUnit_iff_ne_zero] at h1
      rw [Matrix.isUnit_iff_isUnit_det, isUnit_iff_ne_zero]
      exact left_ne_zero_of_mul h1
    have hinj : Function.Injective Ym.mulVec := Matrix.mulVec_injective_iff_isUnit.mpr hunit
    have hu : Ym.mulVec (fun rr => eval y (rowE c S rr)) = 0 := by
      funext i
      simp only [Matrix.mulVec, dotProduct, hYm, Matrix.of_apply, Pi.zero_apply]
      exact hYF i
    have := hinj (hu.trans (Matrix.mulVec_zero Ym).symm)
    intro rr
    exact congrFun this rr
  refine ⟨y, hyR, fun k => ?_, hzero, fun y' hy' hz' => ?_⟩
  · have := hmaps y hyR k
    rwa [show Gmap c S Y y = y from hyfix] at this
  -- uniqueness: two fixed points of a contraction on the rounded box
  have hfix' : Gmap c S Y y' = y' := by
    funext i
    simp only [Gmap]
    have : ∑ rr : Fin NV, ((Ymat Y i rr : ℚ) : ℝ) * eval y' (rowE c S rr) = 0 :=
      Finset.sum_eq_zero fun rr _ => by rw [hz' rr, mul_zero]
    rw [this, sub_zero]
  have hfixy : Gmap c S Y y = y := hyfix
  have h1 := hlip y' y hy' hyB
  rw [hfix', hfixy] at h1
  have h2 : dist (fun j => y' j - y j) (0 : Vec) ≤ β * dist (fun j => y' j - y j) (0 : Vec) := by
    have hd : dist (fun j => y' j - y j) (0 : Vec) = dist y' y := by
      rw [dist_eq_norm, dist_eq_norm, sub_zero]
      rfl
    rw [hd]; exact h1
  have := eq_zero_of_dist_le hβ_lt h2
  funext j
  have := congrFun this j
  simp only [Pi.zero_apply] at this
  linarith

end PackingCert.Rigid
