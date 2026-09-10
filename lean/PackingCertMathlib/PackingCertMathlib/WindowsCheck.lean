import PackingCertMathlib.Windows
import PackingCertMathlib.CaseBridge

/-!
# The WINDOWS clause — the checker and its soundness (A192, from A185's `verify_case_v4.py`)

`boxed_windows.md` §5: the certificate gains a field `windows`; per window a list of pieces
(here already the INTEGER boxes of the verifier's grid — the outward rounding
`verify_case_v4.window_boxes` of the rational `(t, c)`-boxes, a superset) and the index of its
attached core.  `checkWindowsI` is `checkCaseI` with

* the budget `n − m + r_c` in place of `n − m` (`r_c` = the number of attached cores, listed
  without repetition in `attList`);
* the FREE walk (`goC` from the root box with ALL cores) run only if `f = n − r − (m − r_c) > 0`;
* one WINDOW walk per piece: `goC` from the piece's box with the cores attached to OTHER windows
  (`otherCores`, `make_verifier 'win'`), the same NO-families.

`checkWindowsI_kill` is Theorem W for a passing certificate: the free clause is
`goC_box_price` on the root box (`CaseBridge.checkCaseI_price`'s argument, with the box a
parameter), the window clause is `goC_box_price` on each piece, and `WindowsW.windowed_dead`
does the counting.  (V3) — an attached core lies in every pose of its window — is a HYPOTHESIS
of the end form here (`hV3`), discharged per certificate by A135's `checkVertexInPBox_sound`
on the four corners (`coreInPiece` below); the verifier re-derives it by `point_in_all_poses`
(HARD REJECT otherwise).  No axiom is introduced.
-/

namespace PackingCert
namespace S11
namespace WindowsW

open Set MeasureI CaseI

/-! ## 1. The data -/

/-- One window: its pieces as integer boxes on the certificate's grid, and its attached core. -/
structure CWindow where
  pieces : List IBox
  core : Option Nat
deriving Repr

/-- A windowed case certificate: a v1 case certificate plus its windows. -/
structure CCertW where
  c : CCertI
  windows : List CWindow
deriving Repr

/-- The attached-core index list (`κ`'s image, as a list). -/
def attList (ws : List CWindow) : List Nat := ws.filterMap (fun w => w.core)

/-- The cores attached to windows OTHER than `w` (`verify_case_v4.make_verifier 'win'`). -/
def otherCores (c : CCertI) (ws : List CWindow) (w : CWindow) : List CCore :=
  (ws.filterMap (fun w' => if w'.core = w.core then none else w'.core)).filterMap
    (fun j => c.cores[j]?)

/-- **The windowed checker.** -/
def checkWindowsI (C : CCertW) : Bool :=
  let c := C.c
  let ctx := mkCtx (toMCert c)
  let m := c.cores.length
  let att := attList C.windows
  0 < c.sDen && 0 < c.wd &&
  c.atoms.all (fun a => 0 < a.pd && 0 ≤ a.w) &&
  c.cores.all coreOK &&
  C.windows.all (fun w => w.core.all (fun j => decide (j < m))) &&
  decide att.Nodup &&
  (c.atoms.foldl (fun acc a => acc + a.w) 0
      < ((c.n : Int) - (m : Int) + (att.length : Int)) * c.wd) &&
  (if 0 < (c.n : Int) - (C.windows.length : Int) - ((m : Int) - (att.length : Int)) then
      goC ctx c.cores c.nofams c.depth (rootBox ctx) c.atoms 0
    else true) &&
  C.windows.all (fun w => w.pieces.all (fun b =>
    0 ≤ b.T0 && b.T1 ≤ ctx.TROOT &&
      goC ctx (otherCores c C.windows w) c.nofams c.depth b c.atoms 0))

/-! ## 2. Real semantics -/

/-- A pose lies in one of the window's boxes. -/
def InWindow (ctx : Ctx) (w : CWindow) (q : PSq) : Prop := ∃ b ∈ w.pieces, inBox ctx b q

/-- The window predicate on SETS: some parametrisation with `t ∈ [0,1]` lies in the window. -/
def WinSet (ctx : Ctx) (w : CWindow) (S : Set RP) : Prop :=
  ∃ q : PSq, q.t ∈ Icc (0 : ℝ) 1 ∧ S = q.set ∧ InWindow ctx w q

/-- The attachment `κ : [r] ⇀ [m]` read off the certificate. -/
def kappa (C : CCertW) (i : Fin C.windows.length) : Option (Fin C.c.cores.length) :=
  match (C.windows.get i).core with
  | none => none
  | some j => if h : j < C.c.cores.length then some ⟨j, h⟩ else none

theorem kappa_eq_some_iff (C : CCertW) (i : Fin C.windows.length)
    (jj : Fin C.c.cores.length) :
    kappa C i = some jj ↔ (C.windows.get i).core = some (jj : ℕ) := by
  unfold kappa
  rcases hc : (C.windows.get i).core with _ | j
  · simp
  · by_cases h : j < C.c.cores.length
    · simp only [h, dite_true, Option.some.injEq, Fin.ext_iff]
    · simp only [h, dite_false, reduceCtorEq, Option.some.injEq, false_iff]
      intro hj
      exact h (hj ▸ jj.isLt)

/-! ## 3. The facts a passing checker delivers -/

theorem checkWindowsI_facts {C : CCertW} (h : checkWindowsI C = true) :
    0 < C.c.sDen ∧ 0 < C.c.wd ∧ (∀ a ∈ C.c.atoms, 0 < a.pd ∧ 0 ≤ a.w) ∧
    (∀ K ∈ C.c.cores, coreOK K = true) ∧
    (∀ w ∈ C.windows, ∀ j, w.core = some j → j < C.c.cores.length) ∧
    (attList C.windows).Nodup ∧
    (C.c.atoms.foldl (fun acc a => acc + a.w) 0
        < ((C.c.n : Int) - (C.c.cores.length : Int) + ((attList C.windows).length : Int))
          * C.c.wd) ∧
    (0 < (C.c.n : Int) - (C.windows.length : Int)
        - ((C.c.cores.length : Int) - ((attList C.windows).length : Int)) →
      goC (mkCtx (toMCert C.c)) C.c.cores C.c.nofams C.c.depth (rootBox (mkCtx (toMCert C.c)))
        C.c.atoms 0 = true) ∧
    (∀ w ∈ C.windows, ∀ b ∈ w.pieces, 0 ≤ b.T0 ∧ b.T1 ≤ (mkCtx (toMCert C.c)).TROOT ∧
      goC (mkCtx (toMCert C.c)) (otherCores C.c C.windows w) C.c.nofams C.c.depth b
        C.c.atoms 0 = true) := by
  rw [checkWindowsI] at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩, h9⟩ := h
  refine ⟨of_decide_eq_true h1, of_decide_eq_true h2, ?_, ?_, ?_, of_decide_eq_true h6,
    of_decide_eq_true h7, ?_, ?_⟩
  · intro a ha
    have hpa := List.all_eq_true.mp h3 a ha
    rw [Bool.and_eq_true] at hpa
    exact ⟨of_decide_eq_true hpa.1, of_decide_eq_true hpa.2⟩
  · intro K hK
    exact List.all_eq_true.mp h4 K hK
  · intro w hw j hj
    have hpw := List.all_eq_true.mp h5 w hw
    rw [hj] at hpw
    exact of_decide_eq_true hpw
  · intro hf
    rw [if_pos hf] at h8
    exact h8
  · intro w hw b hb
    have hpw := List.all_eq_true.mp h9 w hw
    have hpb := List.all_eq_true.mp hpw b hb
    rw [Bool.and_eq_true, Bool.and_eq_true] at hpb
    exact ⟨of_decide_eq_true hpb.1.1, of_decide_eq_true hpb.1.2, hpb.2⟩


/-! ## 4. The walk soundness with the starting box a parameter -/

/-- `CaseBridge.checkCaseI_price`'s argument with the starting box a parameter: a passing `goC`
from a box `b` prices every admissible placement in `b` that misses every listed core and lies
in no NO-family zone at `≥ wd`. -/
theorem goC_box_price {c : CCertI} (hsd : 0 < c.sDen)
    (hat : ∀ a ∈ c.atoms, 0 < a.pd ∧ 0 ≤ a.w)
    {cores : List CCore} (hcoresOK : ∀ K ∈ cores, coreOK K = true) {b : IBox}
    (hT0 : 0 ≤ b.T0) (hT1 : b.T1 ≤ (mkCtx (toMCert c)).TROOT)
    (hgo : goC (mkCtx (toMCert c)) cores c.nofams c.depth b c.atoms 0 = true)
    (q : PSq) (hq0 : 0 ≤ q.t) (hq1 : q.t ≤ 1) (hsub : q.set ⊆ container (caseSide c))
    (hbox : inBox (mkCtx (toMCert c)) b q)
    (hfree : ∀ K ∈ cores, Disjoint q.set (coreSet K))
    (hnoex : ∀ f ∈ c.nofams, ¬ InZone f q) :
    (c.wd : ℝ) ≤ massIn c.atoms q.set := by
  set ctx := mkCtx (toMCert c) with hctx
  have hTR : ctx.TROOT = (2 : Int) ^ (c.depth + 1) := rfl
  have hR : (0 : ℝ) < (ctx.TROOT : ℝ) := by
    rw [hTR]; push_cast; positivity
  have hP4' : ctx.P4 = ctx.TROOT * ctx.TROOT := by
    change (4 : Int) ^ (c.depth + 1) = (2 : Int) ^ (c.depth + 1) * (2 : Int) ^ (c.depth + 1)
    rw [← mul_pow]
    norm_num
  have hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2 := by
    rw [hP4']; push_cast; ring
  have hD : 0 < ctx.D := by
    change 0 < c.sDen * (2 : Int) ^ (c.depth + 2)
    positivity
  have hSD : (ctx.SD : ℝ) = caseSide c * (ctx.D : ℝ) := by
    have hsdR : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
    change ((c.sNum * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
        = ((c.sNum : ℝ) / (c.sDen : ℝ)) * ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
    push_cast
    field_simp
  obtain ⟨a1, a2, a3, a4⟩ := (set_subset_container_iff hq0 hq1 (caseSide c)).mp hsub
  have hadm : Adm (caseSide c) q := ⟨a1, a2, a3, a4⟩
  have hmain := goC_sound (ctx := ctx) hP4 hR hD hSD hcoresOK c.depth b c.atoms 0 hat hT0 hT1
    hgo q hq0 hq1 hbox hadm hfree hnoex
  have hne : (ctx.NEED : ℝ) = (c.wd : ℝ) := rfl
  rw [hne] at hmain
  simpa using hmain

/-- Every admissible placement lies in the root box (`checkCaseI_price`, the `hroot` step). -/
theorem inBox_root {c : CCertI} (hsd : 0 < c.sDen) (q : PSq) (hq0 : 0 ≤ q.t) (hq1 : q.t ≤ 1)
    (hsub : q.set ⊆ container (caseSide c)) :
    inBox (mkCtx (toMCert c)) (rootBox (mkCtx (toMCert c))) q := by
  set ctx := mkCtx (toMCert c) with hctx
  have hTR : ctx.TROOT = (2 : Int) ^ (c.depth + 1) := rfl
  have hR : (0 : ℝ) < (ctx.TROOT : ℝ) := by
    rw [hTR]; push_cast; positivity
  have hD : 0 < ctx.D := by
    change 0 < c.sDen * (2 : Int) ^ (c.depth + 2)
    positivity
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  have hSD : (ctx.SD : ℝ) = caseSide c * (ctx.D : ℝ) := by
    have hsdR : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
    change ((c.sNum * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
        = ((c.sNum : ℝ) / (c.sDen : ℝ)) * ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
    push_cast
    field_simp
  obtain ⟨a1, a2, a3, a4⟩ := (set_subset_container_iff hq0 hq1 (caseSide c)).mp hsub
  have hw1 := wT_ge_one hq0 hq1
  have hlo : ((ctx.D / 2 : Int) : ℝ) ≤ (ctx.D : ℝ) / 2 := cast_ediv_le (by norm_num)
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · change ((0 : Int) : ℝ) ≤ q.t * (ctx.TROOT : ℝ)
    push_cast
    exact mul_nonneg hq0 hR.le
  · change q.t * (ctx.TROOT : ℝ) ≤ ((ctx.TROOT : Int) : ℝ)
    nlinarith
  · change ((ctx.D / 2 : Int) : ℝ) ≤ q.cx * (ctx.D : ℝ)
    nlinarith [a1, hw1]
  · change q.cx * (ctx.D : ℝ) ≤ ((ctx.SD - ctx.D / 2 : Int) : ℝ)
    push_cast
    nlinarith [a2, hw1, hSD, hlo]
  · change ((ctx.D / 2 : Int) : ℝ) ≤ q.cy * (ctx.D : ℝ)
    nlinarith [a3, hw1]
  · change q.cy * (ctx.D : ℝ) ≤ ((ctx.SD - ctx.D / 2 : Int) : ℝ)
    push_cast
    nlinarith [a4, hw1, hSD, hlo]

/-! ## 5. The core lists -/

theorem otherCores_sub {c : CCertI} {ws : List CWindow} {w : CWindow} {K : CCore}
    (hK : K ∈ otherCores c ws w) : K ∈ c.cores := by
  unfold otherCores at hK
  rw [List.mem_filterMap] at hK
  obtain ⟨j, -, hjK⟩ := hK
  obtain ⟨hlt, rfl⟩ := List.getElem?_eq_some_iff.mp hjK
  exact List.getElem_mem hlt

/-- A core in window `i`'s exemption list is attached to a DIFFERENT window. -/
theorem mem_otherCores {C : CCertW} {i : Fin C.windows.length} {K : CCore}
    (hK : K ∈ otherCores C.c C.windows (C.windows.get i)) :
    ∃ i' : Fin C.windows.length, ∃ jj : Fin C.c.cores.length,
      i' ≠ i ∧ kappa C i' = some jj ∧ K = C.c.cores.get jj := by
  unfold otherCores at hK
  rw [List.mem_filterMap] at hK
  obtain ⟨j, hj, hjK⟩ := hK
  rw [List.mem_filterMap] at hj
  obtain ⟨w', hw', hw'j⟩ := hj
  have hne : w'.core ≠ (C.windows.get i).core := by
    intro h
    rw [if_pos h] at hw'j
    simp at hw'j
  rw [if_neg hne] at hw'j
  obtain ⟨i', hi'⟩ := List.mem_iff_get.mp hw'
  obtain ⟨hjlt, hjK'⟩ := List.getElem?_eq_some_iff.mp hjK
  refine ⟨i', ⟨j, hjlt⟩, ?_, ?_, ?_⟩
  · rintro rfl
    exact hne (by rw [← hi'])
  · rw [kappa_eq_some_iff, hi']
    exact hw'j
  · rw [List.get_eq_getElem]
    exact hjK'.symm


/-! ## 6. Theorem W for a passing certificate -/

/-- **The windows clause, end form** (`boxed_windows.md` Theorem W for a PASS of the checker).
A passing `checkWindowsI` refutes every strict family of `n` closed unit squares at the certified
side that satisfies the node hypothesis: (H1) an injective assignment `σ` of the windows to
squares whose poses lie in the window's boxes, (H2) designated owners `own` containing the
UNATTACHED cores, (H3) no NO-exempt square — given (V3), that every attached core lies in every
pose of its window (`hV3`, the verifier's `point_in_all_poses` re-derivation). -/
theorem checkWindowsI_kill {C : CCertW} (h : checkWindowsI C = true)
    {Q : Fin C.c.n → Set RP} (hQ : IsStrictFamily C.c.n (caseSide C.c) Q)
    (σ : Fin C.windows.length → Fin C.c.n) (hσ : Function.Injective σ)
    (hH1 : ∀ i, WinSet (mkCtx (toMCert C.c)) (C.windows.get i) (Q (σ i)))
    (own : Fin C.c.cores.length → Fin C.c.n)
    (hH2 : ∀ j : Fin C.c.cores.length, (∀ i, (C.windows.get i).core ≠ some (j : ℕ)) →
      coreSet (C.c.cores.get j) ⊆ Q (own j))
    (hH3 : ∀ k, ¬ CaseExempt C.c (Q k))
    (hV3 : ∀ i (j : Fin C.c.cores.length), (C.windows.get i).core = some (j : ℕ) →
      ∀ q : PSq, InWindow (mkCtx (toMCert C.c)) (C.windows.get i) q →
        coreSet (C.c.cores.get j) ⊆ q.set) :
    False := by
  obtain ⟨hsd, hwd, hat, hcoresOK, hrange, hnd, htot, hroot, hwalk⟩ := checkWindowsI_facts h
  have hwdR : (0 : ℝ) ≤ (C.c.wd : ℝ) := by exact_mod_cast hwd.le
  refine windowed_dead (n := C.c.n) (m := C.c.cores.length) (r := C.windows.length)
    (s := caseSide C.c) (NEEDR := (C.c.wd : ℝ))
    (τ := (C.c.atoms.map fun a => ((a.w : ℝ))).sum) hwdR
    (massIn C.c.atoms) (CaseExempt C.c) hQ (fun j => coreSet (C.c.cores.get j)) own
    (fun i => WinSet (mkCtx (toMCert C.c)) (C.windows.get i)) (kappa C)
    (attList C.windows) hnd ?_ σ hσ hH1 ?_ hH3 ?_ ?_ ?_
    (fun G => massIn_finset_sum_le hQ C.c.atoms (fun a ha => (hat a ha).2) G) ?_
  · -- the attached list names attached cores
    intro j hj
    unfold attList at hj
    rw [List.mem_filterMap] at hj
    obtain ⟨w, hw, hwj⟩ := hj
    have hjlt := hrange w hw j hwj
    obtain ⟨i, hi⟩ := List.mem_iff_get.mp hw
    refine ⟨⟨j, hjlt⟩, rfl, i, (kappa_eq_some_iff C i ⟨j, hjlt⟩).mpr ?_⟩
    rw [hi]
    exact hwj
  · -- (H2) in the `κ` form
    intro j hk
    refine hH2 j ?_
    intro i hc
    exact hk i ((kappa_eq_some_iff C i j).mpr hc)
  · -- (V1): the free walk
    intro hf S hS hsub hdis hnex
    obtain ⟨q, hqt, rfl⟩ := isUnitSquare_exists_psq hS
    have hfI : 0 < (C.c.n : Int) - (C.windows.length : Int)
        - ((C.c.cores.length : Int) - ((attList C.windows).length : Int)) := by
      exact_mod_cast hf
    refine goC_box_price hsd hat hcoresOK (le_refl _) (le_refl _) (hroot hfI) q hqt.1 hqt.2
      hsub (inBox_root hsd q hqt.1 hqt.2 hsub) ?_ ?_
    · intro K hK
      obtain ⟨j, hj⟩ := List.mem_iff_get.mp hK
      exact hj ▸ hdis j
    · intro f hf' hz
      exact hnex ⟨q, hqt, rfl, f, hf', hz⟩
  · -- (V2): the window walks
    intro i S hS hsub hW hdis hnex
    obtain ⟨q, hqt, rfl, b, hb, hbox⟩ := hW
    obtain ⟨hT0, hT1, hgo⟩ := hwalk (C.windows.get i) (List.get_mem _ _) b hb
    refine goC_box_price hsd hat (fun K hK => hcoresOK K (otherCores_sub hK)) hT0 hT1 hgo q
      hqt.1 hqt.2 hsub hbox ?_ ?_
    · intro K hK
      obtain ⟨i', jj, hi', hκ, rfl⟩ := mem_otherCores hK
      exact hdis i' jj hi' hκ
    · intro f hf hz
      exact hnex ⟨q, hqt, rfl, f, hf, hz⟩
  · -- (V3) in the `κ` form
    intro i jj hκ S hW
    obtain ⟨q, -, rfl, hin⟩ := hW
    exact hV3 i jj ((kappa_eq_some_iff C i jj).mp hκ) q hin
  · -- (V4): the total below the scaled budget
    rw [foldl_add_eq C.c.atoms 0, zero_add] at htot
    have h2 : (((C.c.atoms.map fun a => a.w).sum : Int) : ℝ)
        < ((C.c.n : ℝ) - (C.c.cores.length : ℝ) + ((attList C.windows).length : ℝ))
          * (C.c.wd : ℝ) := by
      have hcast : ((((C.c.n : Int) - (C.c.cores.length : Int)
            + ((attList C.windows).length : Int)) * C.c.wd : Int) : ℝ)
          = ((C.c.n : ℝ) - (C.c.cores.length : ℝ) + ((attList C.windows).length : ℝ))
            * (C.c.wd : ℝ) := by
        push_cast
        ring
      rw [← hcast]
      exact_mod_cast htot
    have h3 : (((C.c.atoms.map fun a => a.w).sum : Int) : ℝ)
        = (C.c.atoms.map fun a => ((a.w : ℝ))).sum := by
      push_cast
      rw [List.map_map]
      rfl
    rw [h3] at h2
    exact h2

end WindowsW
end S11
end PackingCert
