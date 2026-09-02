import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.MeasureBridge
import PackingCertMathlib.MeasurePy

/-!
# Soundness of the `verify_measure.py` driver (A75, depgraph node V.MEAS)

`checkMeasurePy` (`MeasurePy.lean`) is the Lean model of the Python verifier's accept
rule — `checkMeasureI` generalised by `tscale`, the `4^k` root grid, the margin
threshold, the no-drop `known`-inheritance of `covered`, an arbitrary shortlist oracle,
and `main`'s `s < 1` shortcut.  This file proves

    `checkMeasurePy c need ts k pick = true`  ⟹  `∀ s, Fits c.n s → c.sNum/c.sDen ≤ s`

for EVERY oracle `pick`, every integer `tscale`, every grid exponent `k` and every
`need ≥ wd`, from the A64 primitives (`clipI_sound`, `trig_enclosure`, `projI_sound`)
and the A64 counting argument (`coverage_no_packing`).  Hence a Python PASS (one
instance of the accept rule, with the float shortlist as the oracle) certifies the
lower bound — modulo only the faithfulness of the model to the Python source, which is
a line-by-line correspondence recorded in `MeasurePy.lean` and
`attempts/A75-lean-wave5/notes/findings.md`.
-/

namespace PackingCert
namespace S11

open Set MeasureI MeasurePy

noncomputable section

section CtxFacts

variable {ctx : Ctx}

/-- `covered` is sound: certified mass plus the mass of the kept atoms never exceeds
the incoming certified mass plus the mass of the processed atoms (nothing is lost: no
atom is dropped); a `covered` verdict means `sure' ≥ NEED`; kept atoms stay valid. -/
theorem siftPy_sound {Clo Chi Slo Shi E : Int} {b : IBox} {q : PSq}
    (hD : 0 < ctx.D) (hE : 0 < (E : ℝ))
    (hcos1 : (Clo : ℝ) ≤ cosT q.t * E) (hcos2 : cosT q.t * E ≤ (Chi : ℝ))
    (hsin1 : (Slo : ℝ) ≤ sinT q.t * E) (hsin2 : sinT q.t * E ≤ (Shi : ℝ))
    (hX0 : (b.X0 : ℝ) ≤ q.cx * ctx.D) (hX1 : q.cx * ctx.D ≤ (b.X1 : ℝ))
    (hY0 : (b.Y0 : ℝ) ≤ q.cy * ctx.D) (hY1 : q.cy * ctx.D ≤ (b.Y1 : ℝ))
    (pick : IAtom → Bool) :
    ∀ (l : List IAtom) (sure : Int) (acc : List IAtom) (cov : Bool) (sure' : Int)
      (rest : List IAtom),
      (∀ a ∈ l, 0 < a.pd ∧ 0 ≤ a.w) → (∀ a ∈ acc, 0 < a.pd ∧ 0 ≤ a.w) →
      siftPy ctx Clo Chi Slo Shi E b pick l sure acc = (cov, sure', rest) →
      ((sure' : ℝ) + massIn rest q.set
          ≤ (sure : ℝ) + massIn l q.set + massIn acc q.set) ∧
      (cov = true → ctx.NEED ≤ sure') ∧
      (∀ a ∈ rest, 0 < a.pd ∧ 0 ≤ a.w) := by
  intro l
  induction l with
  | nil =>
    intro sure acc cov sure' rest hl hacc hs
    rw [siftPy] at hs
    simp only [Prod.mk.injEq] at hs
    obtain ⟨hc, hsu, hre⟩ := hs
    subst hsu
    subst hre
    refine ⟨by simp, ?_, hacc⟩
    intro hcov
    rw [← hc] at hcov
    exact of_decide_eq_true hcov
  | cons a as ih =>
    intro sure acc cov sure' rest hl hacc hs
    have hva := hl a (List.mem_cons_self ..)
    have hvas : ∀ x ∈ as, 0 < x.pd ∧ 0 ≤ x.w := fun x hx => hl x (List.mem_cons_of_mem a hx)
    rw [siftPy] at hs
    split at hs
    · next hstop =>
      simp only [Prod.mk.injEq] at hs
      obtain ⟨hc, hsu, hre⟩ := hs
      subst hsu
      subst hre
      have hnn : 0 ≤ massIn (a :: as) q.set :=
        massIn_nonneg (fun x hx => (hl x hx).2) _
      exact ⟨by linarith, fun _ => hstop, hacc⟩
    · next hstop =>
      rcases hp : projI ctx Clo Chi Slo Shi E b a with ⟨u0, u1, v0, v1, lim⟩
      rw [hp] at hs
      dsimp only at hs
      obtain ⟨hin, -⟩ :=
        projI_sound hD hE hcos1 hcos2 hsin1 hsin2 hX0 hX1 hY0 hY1 hva.1 hp
      split at hs
      · next hins =>
        rw [Bool.and_eq_true] at hins
        obtain ⟨q1, q2, q3⟩ := ih (sure + a.w) acc cov sure' rest hvas hacc hs
        refine ⟨?_, q2, q3⟩
        have hmem := hin hins.2
        have hml : massIn (a :: as) q.set = (a.w : ℝ) + massIn as q.set := by
          rw [massIn_cons, Set.indicator_of_mem hmem]
        rw [hml]
        push_cast at q1
        linarith
      · next _ =>
        have hacc' : ∀ x ∈ a :: acc, 0 < x.pd ∧ 0 ≤ x.w := by
          intro x hx
          rcases List.mem_cons.mp hx with rfl | hx
          · exact hva
          · exact hacc x hx
        obtain ⟨q1, q2, q3⟩ := ih sure (a :: acc) cov sure' rest hvas hacc' hs
        refine ⟨?_, q2, q3⟩
        rw [massIn_cons] at q1
        rw [massIn_cons]
        linarith

/-- The `tscale`-weighted split covers the box (any weight: the proof never looks at
the widths). -/
theorem splitPy_sound (ts : Int) {b : IBox} {q : PSq} (hq : inBox ctx b q) (hT0 : 0 ≤ b.T0)
    (hT1 : b.T1 ≤ ctx.TROOT) :
    (inBox ctx (splitPy ctx ts b).1 q ∧ 0 ≤ (splitPy ctx ts b).1.T0 ∧
        (splitPy ctx ts b).1.T1 ≤ ctx.TROOT) ∨
    (inBox ctx (splitPy ctx ts b).2 q ∧ 0 ≤ (splitPy ctx ts b).2.T0 ∧
        (splitPy ctx ts b).2.T1 ≤ ctx.TROOT) := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := hq
  have hTle : b.T0 ≤ b.T1 := by exact_mod_cast le_trans h1 h2
  have hXle : b.X0 ≤ b.X1 := by exact_mod_cast le_trans h3 h4
  have hYle : b.Y0 ≤ b.Y1 := by exact_mod_cast le_trans h5 h6
  obtain ⟨res, hres⟩ : ∃ r, splitPy ctx ts b = r := ⟨_, rfl⟩
  have hres0 : splitPy ctx ts b = res := hres
  rw [splitPy] at hres
  rw [hres0]
  split at hres
  · -- X split
    have hm1 : b.X0 ≤ (b.X0 + b.X1) / 2 := by omega
    have hm2 : (b.X0 + b.X1) / 2 ≤ b.X1 := by omega
    rw [← hres]
    dsimp only
    rcases le_total (q.cx * (ctx.D : ℝ)) (((b.X0 + b.X1) / 2 : Int) : ℝ) with hc | hc
    · exact Or.inl ⟨⟨h1, h2, h3, hc, h5, h6⟩, hT0, hT1⟩
    · exact Or.inr ⟨⟨h1, h2, hc, h4, h5, h6⟩, hT0, hT1⟩
  · split at hres
    · -- Y split
      have hm1 : b.Y0 ≤ (b.Y0 + b.Y1) / 2 := by omega
      have hm2 : (b.Y0 + b.Y1) / 2 ≤ b.Y1 := by omega
      rw [← hres]
      dsimp only
      rcases le_total (q.cy * (ctx.D : ℝ)) (((b.Y0 + b.Y1) / 2 : Int) : ℝ) with hc | hc
      · exact Or.inl ⟨⟨h1, h2, h3, h4, h5, hc⟩, hT0, hT1⟩
      · exact Or.inr ⟨⟨h1, h2, h3, h4, hc, h6⟩, hT0, hT1⟩
    · -- T split
      have hm1 : b.T0 ≤ (b.T0 + b.T1) / 2 := by omega
      have hm2 : (b.T0 + b.T1) / 2 ≤ b.T1 := by omega
      rw [← hres]
      dsimp only
      rcases le_total (q.t * (ctx.TROOT : ℝ)) (((b.T0 + b.T1) / 2 : Int) : ℝ) with hc | hc
      · exact Or.inl ⟨⟨h1, hc, h3, h4, h5, h6⟩, hT0, le_trans hm2 hT1⟩
      · exact Or.inr ⟨⟨hc, h2, h3, h4, h5, h6⟩, le_trans hT0 hm1, hT1⟩

/-- The driver recursion is sound for every oracle: on a passing box, every admissible
placement in the box carries certified-plus-remaining mass `≥ NEED`. -/
theorem goPy_sound {sVal : ℝ} (ts : Int) (pick : IBox → List IAtom → Int → IAtom → Bool)
    (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (hD : 0 < ctx.D) (hSD : (ctx.SD : ℝ) = sVal * ctx.D) :
    ∀ (fuel : Nat) (b : IBox) (l : List IAtom) (sure : Int),
      (∀ a ∈ l, 0 < a.pd ∧ 0 ≤ a.w) → 0 ≤ b.T0 → b.T1 ≤ ctx.TROOT →
      goPy ctx ts pick fuel b l sure = true →
      ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 → inBox ctx b q → Adm sVal q →
      (ctx.NEED : ℝ) ≤ (sure : ℝ) + massIn l q.set := by
  intro fuel
  induction fuel with
  | zero =>
    intro b l sure hl hbT0 hbT1 hgo q hq0 hq1 hbox hadm
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ := clipI_sound hP4 hR hD hSD hbT0 hbox hadm
    rw [goPy, hclip] at hgo
    dsimp only at hgo
    rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
    rw [hbt] at hgo
    dsimp only at hgo
    simp only [boxTrig, trig, Prod.mk.injEq] at hbt
    obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1' : (b'.T1 : ℝ) ≤ (ctx.TROOT : ℝ) := by
      rw [hT1eq]; exact_mod_cast hbT1
    obtain ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩ := hbox'
    have henc := trig_enclosure hP4 hR hT0' hT1' hbt0 hbt1
    have hEpos : 0 < (E : ℝ) := by rw [← hE]; exact_mod_cast henc.1
    have hc1 : (Clo : ℝ) ≤ cosT q.t * E := by
      rw [← hClo, ← hE]; exact_mod_cast henc.2.1
    have hc2 : cosT q.t * E ≤ (Chi : ℝ) := by
      rw [← hChi, ← hE]; exact_mod_cast henc.2.2.1
    have hs1 : (Slo : ℝ) ≤ sinT q.t * E := by
      rw [← hSlo, ← hE]; exact_mod_cast henc.2.2.2.1
    have hs2 : sinT q.t * E ≤ (Shi : ℝ) := by
      rw [← hShi, ← hE]; exact_mod_cast henc.2.2.2.2
    rcases hsift : siftPy ctx Clo Chi Slo Shi E b' (pick b' l sure) l sure []
      with ⟨cov, sure', rest⟩
    obtain ⟨p1, p2, p3⟩ := siftPy_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
      (pick b' l sure) l sure [] cov sure' rest hl (by simp) hsift
    rw [hsift] at hgo
    dsimp only at hgo
    have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hgo
    have hrest0 : 0 ≤ massIn rest q.set := massIn_nonneg (fun x hx => (p3 x hx).2) _
    have hnil : massIn ([] : List IAtom) q.set = 0 := rfl
    linarith
  | succ f ih =>
    intro b l sure hl hbT0 hbT1 hgo q hq0 hq1 hbox hadm
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ := clipI_sound hP4 hR hD hSD hbT0 hbox hadm
    rw [goPy, hclip] at hgo
    dsimp only at hgo
    rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
    rw [hbt] at hgo
    dsimp only at hgo
    simp only [boxTrig, trig, Prod.mk.injEq] at hbt
    obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1i : b'.T1 ≤ ctx.TROOT := hT1eq ▸ hbT1
    have hT1' : (b'.T1 : ℝ) ≤ (ctx.TROOT : ℝ) := by exact_mod_cast hT1i
    obtain ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩ := hbox'
    have henc := trig_enclosure hP4 hR hT0' hT1' hbt0 hbt1
    have hEpos : 0 < (E : ℝ) := by rw [← hE]; exact_mod_cast henc.1
    have hc1 : (Clo : ℝ) ≤ cosT q.t * E := by
      rw [← hClo, ← hE]; exact_mod_cast henc.2.1
    have hc2 : cosT q.t * E ≤ (Chi : ℝ) := by
      rw [← hChi, ← hE]; exact_mod_cast henc.2.2.1
    have hs1 : (Slo : ℝ) ≤ sinT q.t * E := by
      rw [← hSlo, ← hE]; exact_mod_cast henc.2.2.2.1
    have hs2 : sinT q.t * E ≤ (Shi : ℝ) := by
      rw [← hShi, ← hE]; exact_mod_cast henc.2.2.2.2
    rcases hsift : siftPy ctx Clo Chi Slo Shi E b' (pick b' l sure) l sure []
      with ⟨cov, sure', rest⟩
    obtain ⟨p1, p2, p3⟩ := siftPy_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
      (pick b' l sure) l sure [] cov sure' rest hl (by simp) hsift
    rw [hsift] at hgo
    dsimp only at hgo
    have hrest0 : 0 ≤ massIn rest q.set := massIn_nonneg (fun x hx => (p3 x hx).2) _
    have hnil : massIn ([] : List IAtom) q.set = 0 := rfl
    split at hgo
    · next hcov =>
      have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hcov
      linarith
    · next _ =>
      rw [Bool.and_eq_true] at hgo
      obtain ⟨hg1, hg2⟩ := hgo
      have hbox'' : inBox ctx b' q := ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩
      rcases splitPy_sound ts hbox'' hT0' hT1i with ⟨hin1, hi0, hi1⟩ | ⟨hin2, hi0, hi1⟩
      · have := ih (splitPy ctx ts b').1 rest sure' p3 hi0 hi1 hg1 q hq0 hq1 hin1 hadm
        linarith
      · have := ih (splitPy ctx ts b').2 rest sure' p3 hi0 hi1 hg2 q hq0 hq1 hin2 hadm
        linarith

end CtxFacts

/-! ## The root grid covers the root box -/

/-- One axis of the grid: an exactly divisible interval `[lo, lo + step·m]` is covered by
its `m` cells. -/
theorem grid_cell {lo hi step : Int} {m : Nat} (hm : 0 < m) (hstep : step * (m : Int) = hi - lo)
    {x : ℝ} (h0 : (lo : ℝ) ≤ x) (h1 : x ≤ (hi : ℝ)) :
    ∃ i : Nat, i < m ∧ ((lo + step * (i : Int) : Int) : ℝ) ≤ x ∧
      x ≤ ((lo + step * ((i : Int) + 1) : Int) : ℝ) := by
  have hmR : (0 : ℝ) < (m : ℝ) := by exact_mod_cast hm
  have hstepR : (step : ℝ) * (m : ℝ) = (hi : ℝ) - (lo : ℝ) := by exact_mod_cast hstep
  rcases le_or_gt step 0 with hs | hs
  · -- degenerate: the interval is a point (or empty)
    have hsR : (step : ℝ) ≤ 0 := by exact_mod_cast hs
    have hhl : (hi : ℝ) - (lo : ℝ) ≤ 0 := by nlinarith
    have hxlo : x = (lo : ℝ) := by linarith
    have hstep0 : (step : ℝ) = 0 := by
      have : (hi : ℝ) - (lo : ℝ) = 0 := by linarith
      rw [this] at hstepR
      rcases mul_eq_zero.mp hstepR with h | h
      · exact h
      · exact absurd h hmR.ne'
    refine ⟨0, hm, ?_, ?_⟩
    · push_cast; rw [hstep0, hxlo]; simp
    · push_cast; rw [hstep0, hxlo]; simp
  · have hsR : (0 : ℝ) < (step : ℝ) := by exact_mod_cast hs
    set r : ℝ := (x - (lo : ℝ)) / (step : ℝ) with hr
    have hr0 : 0 ≤ r := by rw [hr]; exact div_nonneg (by linarith) hsR.le
    have hfl : (⌊r⌋ : ℝ) ≤ r := Int.floor_le r
    have hfl1 : r < (⌊r⌋ : ℝ) + 1 := Int.lt_floor_add_one r
    have hfl0 : 0 ≤ ⌊r⌋ := Int.floor_nonneg.mpr hr0
    have hsr : (step : ℝ) * r = x - (lo : ℝ) := by
      rw [hr, mul_div_assoc']
      exact mul_div_cancel_left₀ _ hsR.ne'
    obtain ⟨m', rfl⟩ : ∃ m', m = m' + 1 := ⟨m - 1, by omega⟩
    push_cast at hstepR
    rcases lt_or_ge ⌊r⌋ ((m' + 1 : Nat) : Int) with hlt | hge
    · set i : Nat := ⌊r⌋.toNat with hi
      have hiI : (i : Int) = ⌊r⌋ := Int.toNat_of_nonneg hfl0
      have hiR : (i : ℝ) = (⌊r⌋ : ℝ) := by exact_mod_cast hiI
      refine ⟨i, by omega, ?_, ?_⟩
      · push_cast
        rw [hiR]
        nlinarith
      · push_cast
        rw [hiR]
        nlinarith
    · have hgeR : ((m' : ℝ) + 1) ≤ (⌊r⌋ : ℝ) := by exact_mod_cast hge
      refine ⟨m', by omega, ?_, ?_⟩
      · push_cast
        nlinarith
      · push_cast
        linarith

/-- A placement in the root box lies in some cell of the root grid. -/
theorem rootGrid_cover (ctx : Ctx) (k : Nat) (hok : gridOK ctx k = true) {q : PSq}
    (hT0 : (0 : ℝ) ≤ q.t * (ctx.TROOT : ℝ)) (hT1 : q.t * (ctx.TROOT : ℝ) ≤ (ctx.TROOT : ℝ))
    (hX0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cx * (ctx.D : ℝ))
    (hX1 : q.cx * (ctx.D : ℝ) ≤ ((ctx.SD - ctx.D / 2 : Int) : ℝ))
    (hY0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cy * (ctx.D : ℝ))
    (hY1 : q.cy * (ctx.D : ℝ) ≤ ((ctx.SD - ctx.D / 2 : Int) : ℝ)) :
    ∃ b ∈ rootGrid ctx k, inBox ctx b q ∧ b.T0 = 0 ∧ b.T1 = ctx.TROOT := by
  simp only [gridOK, beq_iff_eq] at hok
  have hm : 0 < 2 ^ k := Nat.two_pow_pos k
  obtain ⟨i, hi, hi0, hi1⟩ :=
    grid_cell (lo := ctx.D / 2) (hi := ctx.SD - ctx.D / 2) hm hok hX0 hX1
  obtain ⟨j, hj, hj0, hj1⟩ :=
    grid_cell (lo := ctx.D / 2) (hi := ctx.SD - ctx.D / 2) hm hok hY0 hY1
  set st : Int := (ctx.SD - ctx.D / 2 - ctx.D / 2) / ((2 ^ k : Nat) : Int) with hst
  refine ⟨⟨0, ctx.TROOT, ctx.D / 2 + st * (i : Int), ctx.D / 2 + st * ((i : Int) + 1),
      ctx.D / 2 + st * (j : Int), ctx.D / 2 + st * ((j : Int) + 1)⟩, ?_, ?_⟩
  · simp only [rootGrid, List.mem_flatMap, List.mem_map, List.mem_range]
    exact ⟨i, hi, j, hj, rfl⟩
  · refine ⟨⟨?_, hT1, hi0, hi1, hj0, hj1⟩, rfl, rfl⟩
    push_cast
    exact hT0

/-! ## The top-level accept rule -/

theorem gatesPy_facts {c : MCertI} {need : Int} (h : gatesPy c need = true) :
    0 < c.sDen ∧ 0 < c.wd ∧ c.wd ≤ need ∧ (∀ a ∈ c.atoms, 0 < a.pd ∧ 0 ≤ a.w) ∧
    (c.atoms.foldl (fun acc a => acc + a.w) 0 < (c.n : Int) * c.wd) := by
  rw [gatesPy] at h
  rw [Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩ := h
  refine ⟨of_decide_eq_true h1, of_decide_eq_true h2, of_decide_eq_true h3, ?_,
    of_decide_eq_true h5⟩
  intro a ha
  have hpa := List.all_eq_true.mp h4 a ha
  rw [Bool.and_eq_true] at hpa
  exact ⟨of_decide_eq_true hpa.1, of_decide_eq_true hpa.2⟩

/-- **Coverage for the Python accept rule**: a PASS certifies that every parametrised
unit square inside the container carries mass `≥ need ≥ wd`, i.e. `μ(Q) ≥ 1`. -/
theorem checkMeasurePy_coverage {c : MCertI} {need ts : Int} {k : Nat}
    {pick : IBox → List IAtom → Int → IAtom → Bool}
    (h : checkMeasurePy c need ts k pick = true) :
    ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 →
      q.set ⊆ container ((c.sNum : ℝ) / (c.sDen : ℝ)) →
      (c.wd : ℝ) ≤ massIn c.atoms q.set := by
  intro q hq0 hq1 hsub
  set ctx : Ctx := { mkCtx c with NEED := need } with hctx
  have hTR : ctx.TROOT = (2 : Int) ^ (c.depth + 1) := rfl
  have hR : (0 : ℝ) < (ctx.TROOT : ℝ) := by
    rw [hTR]; push_cast; positivity
  have hP4' : ctx.P4 = ctx.TROOT * ctx.TROOT := by
    change (4 : Int) ^ (c.depth + 1) = (2 : Int) ^ (c.depth + 1) * (2 : Int) ^ (c.depth + 1)
    rw [← mul_pow]
    norm_num
  have hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2 := by
    rw [hP4']; push_cast; ring
  obtain ⟨a1, a2, a3, a4⟩ :=
    (set_subset_container_iff hq0 hq1 ((c.sNum : ℝ) / (c.sDen : ℝ))).mp hsub
  have hadm : Adm ((c.sNum : ℝ) / (c.sDen : ℝ)) q := ⟨a1, a2, a3, a4⟩
  have hw1 := wT_ge_one hq0 hq1
  rw [checkMeasurePy] at h
  rw [Bool.or_eq_true] at h
  rcases h with hv | h
  · -- `s < 1`: no admissible square exists at all
    rw [vacuousPass, Bool.and_eq_true] at hv
    obtain ⟨hg, hlt⟩ := hv
    obtain ⟨hsd, -, -, -, -⟩ := gatesPy_facts hg
    have hlt' : c.sNum < c.sDen := of_decide_eq_true hlt
    have hsdR : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
    have hS1 : (c.sNum : ℝ) / (c.sDen : ℝ) < 1 := by
      rw [div_lt_one hsdR]; exact_mod_cast hlt'
    exfalso
    linarith
  · rw [Bool.and_eq_true, Bool.and_eq_true] at h
    obtain ⟨⟨hg, hgrid⟩, hall⟩ := h
    obtain ⟨hsd, hwd, hwn, hat, htot⟩ := gatesPy_facts hg
    have hD : 0 < ctx.D := by
      change 0 < c.sDen * (2 : Int) ^ (c.depth + 2)
      positivity
    have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
    have hsdR : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
    have hSD : (ctx.SD : ℝ) = ((c.sNum : ℝ) / (c.sDen : ℝ)) * (ctx.D : ℝ) := by
      change ((c.sNum * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
          = ((c.sNum : ℝ) / (c.sDen : ℝ)) * ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
      push_cast
      field_simp
    have hlo : ((ctx.D / 2 : Int) : ℝ) ≤ (ctx.D : ℝ) / 2 := cast_ediv_le (by norm_num)
    have hX0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cx * (ctx.D : ℝ) := by nlinarith [a1, hw1]
    have hX1 : q.cx * (ctx.D : ℝ) ≤ ((ctx.SD - ctx.D / 2 : Int) : ℝ) := by
      push_cast
      nlinarith [a2, hw1, hSD, hlo]
    have hY0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cy * (ctx.D : ℝ) := by nlinarith [a3, hw1]
    have hY1 : q.cy * (ctx.D : ℝ) ≤ ((ctx.SD - ctx.D / 2 : Int) : ℝ) := by
      push_cast
      nlinarith [a4, hw1, hSD, hlo]
    have hT0 : (0 : ℝ) ≤ q.t * (ctx.TROOT : ℝ) := mul_nonneg hq0 hR.le
    have hT1 : q.t * (ctx.TROOT : ℝ) ≤ (ctx.TROOT : ℝ) := by nlinarith
    obtain ⟨b, hb, hbox, hb0, hb1⟩ := rootGrid_cover ctx k hgrid hT0 hT1 hX0 hX1 hY0 hY1
    have hgo := List.all_eq_true.mp hall b hb
    have hbT0 : 0 ≤ b.T0 := by rw [hb0]
    have hbT1 : b.T1 ≤ ctx.TROOT := by rw [hb1]
    have hmain := goPy_sound (ctx := ctx) ts pick hP4 hR hD hSD (c.depth - 2 * k) b
      c.atoms 0 hat hbT0 hbT1 hgo q hq0 hq1 hbox hadm
    have hne : (ctx.NEED : ℝ) = (need : ℝ) := rfl
    rw [hne] at hmain
    have hwnR : (c.wd : ℝ) ≤ (need : ℝ) := by exact_mod_cast hwn
    simp only [Int.cast_zero, zero_add] at hmain
    linarith

/-- **`verify_measure.py` soundness, end form** (V.MEAS): a PASS of the Python accept
rule at side `s = sNum/sDen` — for ANY shortlist oracle, `tscale`, root split and
margin — proves `s(n) ≥ s`. -/
theorem checkMeasurePy_no_packing {c : MCertI} {need ts : Int} {k : Nat}
    {pick : IBox → List IAtom → Int → IAtom → Bool}
    (h : checkMeasurePy c need ts k pick = true) :
    ∀ s : ℝ, Fits c.n s → (c.sNum : ℝ) / (c.sDen : ℝ) ≤ s := by
  have hg : gatesPy c need = true := by
    rw [checkMeasurePy, Bool.or_eq_true] at h
    rcases h with hv | h
    · rw [vacuousPass, Bool.and_eq_true] at hv; exact hv.1
    · rw [Bool.and_eq_true, Bool.and_eq_true] at h; exact h.1.1
  obtain ⟨hsd, hwd, hwn, hat, htot⟩ := gatesPy_facts hg
  refine coverage_no_packing (NEEDR := (c.wd : ℝ)) (fun a ha => (hat a ha).2)
    (fun q h0 h1 hsub => checkMeasurePy_coverage h q h0 h1 hsub) ?_
  rw [foldl_add_eq c.atoms 0, zero_add] at htot
  have h2 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ) < (c.n : ℝ) * (c.wd : ℝ) := by
    exact_mod_cast htot
  have h3 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ)
      = (c.atoms.map fun a => ((a.w : ℝ))).sum := by
    push_cast
    rw [List.map_map]
    rfl
  rw [h3] at h2
  exact h2

/-- `checkMeasureI` is the instance `tscale = 2`, `k = 0`, `need = wd`, oracle
`pickAll` — up to `sift`'s dropping of `outsideAll` atoms, which the Python driver does
not do; both are sound by the two bridges, and both PASS the 3.82 certificate with the
same box tree (`attempts/A75-lean-wave5/notes/findings.md`).  Recorded here only as a
remark; no theorem relates the two Bool functions. -/
theorem checkMeasurePy_pickAll_no_packing {c : MCertI} {need ts : Int} {k : Nat}
    (h : checkMeasurePy c need ts k pickAll = true) :
    ∀ s : ℝ, Fits c.n s → (c.sNum : ℝ) / (c.sDen : ℝ) ≤ s :=
  checkMeasurePy_no_packing h

end

end S11
end PackingCert
