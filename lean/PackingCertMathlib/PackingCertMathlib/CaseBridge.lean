import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.MeasureBridge
import PackingCertMathlib.Dilation
import PackingCertMathlib.CaseHyp

/-!
# The case-LP bridge (A70, depgraph node V.CASE)

Soundness of the case-LP certificate checker `checkCaseI` (`CaseChecker.lean`, the
Lean port of `verify_case.py`'s decision core):

    `checkCaseI c = true`  ⟹  (P1) `Σ wᵢ < (n − r) · wd`  and
                              (P2) every unit square in `[0,s]²` that misses every
                                   core and is not NO-exempt has `μ ≥ wd`
                           ⟹  no strict family of `n` closed unit squares at side
                               `s` realises the pin hypotheses (`checkCaseI_kill`),

with the B-NO form (`checkCaseI_no_family`: some non-owner is NO-exempt) when
`nofams` is nonempty.  This produces, per PASS file, exactly the `hcert` input of
`lemma_B` / the `price` input of the A68 pricing pigeonhole (`Dilation.lean`) — the
"(P2) from a concrete PASS file" residue named by A68.

Structure: `goC_sound` extends A64's `go_sound` with the exemption branch
(`exemptB_sound`, `CaseHyp.lean`); `checkCaseI_price` is the coverage theorem;
`priced_dichotomy_scaled` is A68's pigeonhole at integer-scaled weights
(`NEEDR = wd` instead of `1`); `checkCaseI_no_family` / `checkCaseI_kill` compose.
-/

namespace PackingCert
namespace S11

open Set MeasureI CaseI

noncomputable section

/-- The measure-checker certificate underlying a case certificate (same scales). -/
def toMCert (c : CCertI) : MCertI :=
  { n := c.n, sNum := c.sNum, sDen := c.sDen, wd := c.wd,
    depth := c.depth, atoms := c.atoms }

/-- The side denoted by a certificate. -/
def caseSide (c : CCertI) : ℝ := (c.sNum : ℝ) / (c.sDen : ℝ)

section CtxFacts

variable {ctx : Ctx}

/-- The case branch-and-bound recursion is sound: on a passing box, every admissible
placement in the box that misses every core and lies in no NO-family zone carries
certified-plus-listed mass `≥ NEED`.  (`go_sound` of A64 with the exemption branch.) -/
theorem goC_sound {sVal : ℝ} {cores : List CCore} {nofams : List CNoFam}
    (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (hD : 0 < ctx.D) (hSD : (ctx.SD : ℝ) = sVal * ctx.D)
    (hcoresOK : ∀ K ∈ cores, coreOK K = true) :
    ∀ (fuel : Nat) (b : IBox) (l : List IAtom) (sure : Int),
      (∀ a ∈ l, 0 < a.pd ∧ 0 ≤ a.w) → 0 ≤ b.T0 → b.T1 ≤ ctx.TROOT →
      goC ctx cores nofams fuel b l sure = true →
      ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 → inBox ctx b q → Adm sVal q →
      (∀ K ∈ cores, Disjoint q.set (coreSet K)) →
      (∀ f ∈ nofams, ¬ InZone f q) →
      (ctx.NEED : ℝ) ≤ (sure : ℝ) + massIn l q.set := by
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  intro fuel
  induction fuel with
  | zero =>
    intro b l sure hl hbT0 hbT1 hgo q hq0 hq1 hbox hadm hfree hnoex
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ := clipI_sound hP4 hR hD hSD hbT0 hbox hadm
    rw [goC, hclip] at hgo
    dsimp only at hgo
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1i : b'.T1 ≤ ctx.TROOT := hT1eq ▸ hbT1
    split at hgo
    · next hex =>
      rcases exemptB_sound hR hDR hT0' hT1i hbox' hcoresOK hex with ⟨K, hK, hne⟩ | ⟨f, hf, hz⟩
      · exact absurd (Set.disjoint_iff_inter_eq_empty.mp (hfree K hK)) hne.ne_empty
      · exact absurd hz (hnoex f hf)
    · next hex =>
      rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
      rw [hbt] at hgo
      dsimp only at hgo
      simp only [boxTrig, trig, Prod.mk.injEq] at hbt
      obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
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
      rcases hsift : sift ctx Clo Chi Slo Shi E b' l sure [] with ⟨cov, sure', rest⟩
      obtain ⟨p1, p2, p3⟩ := sift_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
        l sure [] cov sure' rest hl (by simp) hsift
      rw [hsift] at hgo
      dsimp only at hgo
      have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hgo
      have hrest0 : 0 ≤ massIn rest q.set := massIn_nonneg (fun x hx => (p3 x hx).2) _
      have hnil : massIn ([] : List IAtom) q.set = 0 := rfl
      linarith
  | succ f ih =>
    intro b l sure hl hbT0 hbT1 hgo q hq0 hq1 hbox hadm hfree hnoex
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ := clipI_sound hP4 hR hD hSD hbT0 hbox hadm
    rw [goC, hclip] at hgo
    dsimp only at hgo
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1i : b'.T1 ≤ ctx.TROOT := hT1eq ▸ hbT1
    split at hgo
    · next hex =>
      rcases exemptB_sound hR hDR hT0' hT1i hbox' hcoresOK hex with ⟨K, hK, hne⟩ | ⟨f', hf, hz⟩
      · exact absurd (Set.disjoint_iff_inter_eq_empty.mp (hfree K hK)) hne.ne_empty
      · exact absurd hz (hnoex f' hf)
    · next hex =>
      rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
      rw [hbt] at hgo
      dsimp only at hgo
      simp only [boxTrig, trig, Prod.mk.injEq] at hbt
      obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
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
      rcases hsift : sift ctx Clo Chi Slo Shi E b' l sure [] with ⟨cov, sure', rest⟩
      obtain ⟨p1, p2, p3⟩ := sift_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
        l sure [] cov sure' rest hl (by simp) hsift
      rw [hsift] at hgo
      dsimp only at hgo
      have hrest0 : 0 ≤ massIn rest q.set := massIn_nonneg (fun x hx => (p3 x hx).2) _
      have hnil : massIn ([] : List IAtom) q.set = 0 := rfl
      split at hgo
      · next hcov =>
        have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hcov
        linarith
      · next hcov =>
        rw [Bool.and_eq_true] at hgo
        obtain ⟨hg1, hg2⟩ := hgo
        have hbox'' : inBox ctx b' q := ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩
        rcases splitI_sound hbox'' hT0' hT1i with ⟨hin1, hi0, hi1⟩ | ⟨hin2, hi0, hi1⟩
        · have := ih (splitI ctx b').1 rest sure' p3 hi0 hi1 hg1 q hq0 hq1 hin1 hadm
            hfree hnoex
          linarith
        · have := ih (splitI ctx b').2 rest sure' p3 hi0 hi1 hg2 q hq0 hq1 hin2 hadm
            hfree hnoex
          linarith

end CtxFacts

/-! ## The top-level checker gates -/

theorem checkCaseI_facts {c : CCertI} (h : checkCaseI c = true) :
    0 < c.sDen ∧ 0 < c.wd ∧ (∀ a ∈ c.atoms, 0 < a.pd ∧ 0 ≤ a.w) ∧
    (∀ K ∈ c.cores, coreOK K = true) ∧ c.cores.length ≤ c.n ∧
    (c.atoms.foldl (fun acc a => acc + a.w) 0
        < ((c.n : Int) - (c.cores.length : Int)) * c.wd) ∧
    goC (mkCtx (toMCert c)) c.cores c.nofams c.depth (rootBox (mkCtx (toMCert c)))
      c.atoms 0 = true := by
  rw [checkCaseI] at h
  rw [Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true,
    Bool.and_eq_true, Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩ := h
  refine ⟨of_decide_eq_true h1, of_decide_eq_true h2, ?_, ?_,
    of_decide_eq_true h5, of_decide_eq_true h6, h7⟩
  · intro a ha
    have hpa := List.all_eq_true.mp h3 a ha
    rw [Bool.and_eq_true] at hpa
    exact ⟨of_decide_eq_true hpa.1, of_decide_eq_true hpa.2⟩
  · intro K hK
    exact List.all_eq_true.mp h4 K hK

/-- **The coverage/pricing theorem — claim (P2) of the frozen spec, scaled by `wd`.**
A passing case checker certifies that every admissible placement that misses every
core and lies in no NO-family zone carries mass `≥ wd` (i.e. `μ(Q) ≥ 1`). -/
theorem checkCaseI_price {c : CCertI} (h : checkCaseI c = true) :
    ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 → q.set ⊆ container (caseSide c) →
      (∀ K ∈ c.cores, Disjoint q.set (coreSet K)) →
      (∀ f ∈ c.nofams, ¬ InZone f q) →
      (c.wd : ℝ) ≤ massIn c.atoms q.set := by
  obtain ⟨hsd, hwd, hat, hcoresOK, hrn, htot, hgo⟩ := checkCaseI_facts h
  intro q hq0 hq1 hsub hfree hnoex
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
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  have hsdR : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
  have hSD : (ctx.SD : ℝ) = caseSide c * (ctx.D : ℝ) := by
    change ((c.sNum * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
        = ((c.sNum : ℝ) / (c.sDen : ℝ)) * ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
    push_cast
    field_simp
  obtain ⟨a1, a2, a3, a4⟩ := (set_subset_container_iff hq0 hq1 (caseSide c)).mp hsub
  have hadm : Adm (caseSide c) q := ⟨a1, a2, a3, a4⟩
  have hw1 := wT_ge_one hq0 hq1
  have hlo : ((ctx.D / 2 : Int) : ℝ) ≤ (ctx.D : ℝ) / 2 := cast_ediv_le (by norm_num)
  have hroot : inBox ctx (rootBox ctx) q := by
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
  have hmain := goC_sound (ctx := ctx) hP4 hR hD hSD hcoresOK c.depth (rootBox ctx)
    c.atoms 0 hat (le_refl _) (le_refl _) hgo q hq0 hq1 hroot hadm hfree hnoex
  have hne : (ctx.NEED : ℝ) = (c.wd : ℝ) := rfl
  rw [hne] at hmain
  simpa using hmain

/-! ## The pricing pigeonhole at integer scale -/

/-- A68's `priced_dichotomy` (`Dilation.lean`) at integer-scaled weights: `NEEDR`
replaces `1`, the budget bound is `Σw < (n − r)·NEEDR`.  If every admissible
core-free non-exempt placement is priced `≥ NEEDR` and the total is below the scaled
budget, a strict family whose owners contain the cores has an exempt non-owner. -/
theorem priced_dichotomy_scaled {n r : ℕ} {s'' NEEDR : ℝ} (atoms : List IAtom)
    (hw : ∀ a ∈ atoms, 0 ≤ a.w) (hN : 0 ≤ NEEDR)
    {K : Fin r → Set RP} {own : Fin r → Fin n}
    (Exempt : Set RP → Prop)
    (price : ∀ S : Set RP, IsUnitSquare S → S ⊆ container s'' →
      (∀ j, Disjoint S (K j)) → ¬Exempt S → NEEDR ≤ massIn atoms S)
    (hP1 : (atoms.map fun a => (a.w : ℝ)).sum < ((n : ℝ) - (r : ℝ)) * NEEDR)
    {Q : Fin n → Set RP} (hQ : IsStrictFamily n s'' Q)
    (hH : ∀ j, K j ⊆ Q (own j)) :
    ∃ i : Fin n, (∀ j, own j ≠ i) ∧ Exempt (Q i) := by
  by_contra hno
  push Not at hno
  set O : Finset (Fin n) := Finset.image own Finset.univ with hO
  set G : Finset (Fin n) := Oᶜ with hG
  have hGmem : ∀ i : Fin n, i ∈ G ↔ ∀ j, own j ≠ i := by
    intro i
    simp [hG, hO, eq_comm]
  have hprice : ∀ i ∈ G, NEEDR ≤ massIn atoms (Q i) := by
    intro i hi
    have hnotown := (hGmem i).mp hi
    refine price (Q i) (hQ.unit i) (hQ.contained i) (fun j => ?_) (hno i hnotown)
    exact (hQ.disjoint i (own j) fun h => hnotown j h.symm).mono_right (hH j)
  have hdisf : ∀ i j : Fin n, i ≠ j →
      Disjoint (if i ∈ G then Q i else (∅ : Set RP)) (if j ∈ G then Q j else ∅) := by
    intro i j hij
    by_cases hi : i ∈ G <;> by_cases hj : j ∈ G <;>
      simp [hi, hj, hQ.disjoint i j hij]
  have hupper : ∑ i ∈ G, massIn atoms (Q i) ≤ (atoms.map fun a => (a.w : ℝ)).sum := by
    have hempty : massIn atoms (∅ : Set RP) = 0 := by simp [massIn]
    have hpad : ∑ i ∈ G, massIn atoms (Q i)
        = ∑ i : Fin n, massIn atoms (if i ∈ G then Q i else ∅) := by
      simp only [apply_ite (massIn atoms), hempty, Finset.sum_ite_mem, Finset.univ_inter]
    rw [hpad, massIn_sum_comm]
    refine List.sum_le_sum fun a ha => ?_
    have hwa : (0 : ℝ) ≤ (a.w : ℝ) := by exact_mod_cast hw a ha
    exact indicator_sum_le hdisf hwa (atomPt a)
  have hOcard : O.card ≤ r := le_trans Finset.card_image_le (by simp)
  have hcards : O.card + G.card = n := by
    have h := Finset.card_add_card_compl O
    simp only [Fintype.card_fin] at h
    exact h
  have hGcard : (n : ℝ) - (r : ℝ) ≤ (G.card : ℝ) := by
    have h1 : (O.card : ℝ) ≤ (r : ℝ) := by exact_mod_cast hOcard
    have h2 : (O.card : ℝ) + (G.card : ℝ) = (n : ℝ) := by exact_mod_cast hcards
    linarith
  have hlower : (G.card : ℝ) * NEEDR ≤ ∑ i ∈ G, massIn atoms (Q i) := by
    calc (G.card : ℝ) * NEEDR = ∑ _i ∈ G, NEEDR := by
          rw [Finset.sum_const, nsmul_eq_mul]
      _ ≤ ∑ i ∈ G, massIn atoms (Q i) := Finset.sum_le_sum hprice
  have hchain : ((n : ℝ) - (r : ℝ)) * NEEDR ≤ (G.card : ℝ) * NEEDR :=
    mul_le_mul_of_nonneg_right hGcard hN
  linarith

/-! ## The end forms -/

/-- **Case-LP certificate soundness, B-NO form** (V.CASE): a passing `checkCaseI`
refutes every strict family of `n` closed unit squares at the certified side whose
designated owners contain the `r` cores — up to a NO-exempt non-owner (Lemma B-NO's
occupancy conclusion; with empty `nofams` this is a plain contradiction,
`checkCaseI_kill`). -/
theorem checkCaseI_no_family {c : CCertI} (h : checkCaseI c = true)
    {Q : Fin c.n → Set RP} (hQ : IsStrictFamily c.n (caseSide c) Q)
    (own : Fin c.cores.length → Fin c.n)
    (hown : ∀ j : Fin c.cores.length, coreSet (c.cores.get j) ⊆ Q (own j)) :
    ∃ i : Fin c.n, (∀ j, own j ≠ i) ∧ CaseExempt c (Q i) := by
  obtain ⟨hsd, hwd, hat, hcoresOK, hrn, htot, hgo⟩ := checkCaseI_facts h
  have hwdR : (0 : ℝ) ≤ (c.wd : ℝ) := by
    have := le_of_lt hwd
    exact_mod_cast this
  refine priced_dichotomy_scaled (K := fun j => coreSet (c.cores.get j)) (own := own)
    c.atoms (fun a ha => (hat a ha).2) hwdR (CaseExempt c) ?_ ?_ hQ hown
  · -- (P2): the price of a core-free non-exempt unit square
    intro S hS hsub hdis hnex
    obtain ⟨q, hqt, rfl⟩ := isUnitSquare_exists_psq hS
    refine checkCaseI_price h q hqt.1 hqt.2 hsub ?_ ?_
    · intro K hK
      obtain ⟨j, hj⟩ := List.mem_iff_get.mp hK
      exact hj ▸ hdis j
    · intro f hf hz
      exact hnex ⟨q, hqt, rfl, f, hf, hz⟩
  · -- (P1): total below the scaled budget
    rw [foldl_add_eq c.atoms 0, zero_add] at htot
    have h2 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ)
        < ((c.n : ℝ) - (c.cores.length : ℝ)) * (c.wd : ℝ) := by
      have hcast : ((((c.n : Int) - (c.cores.length : Int)) * c.wd : Int) : ℝ)
          = ((c.n : ℝ) - (c.cores.length : ℝ)) * (c.wd : ℝ) := by
        push_cast
        ring
      rw [← hcast]
      exact_mod_cast htot
    have h3 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ)
        = (c.atoms.map fun a => ((a.w : ℝ))).sum := by
      push_cast
      rw [List.map_map]
      rfl
    rw [h3] at h2
    exact h2

/-- **Case-LP certificate soundness, kill form** (empty `nofams`): a passing
`checkCaseI` proves NO strict family of `n` closed unit squares at the certified
side has its designated owners containing the cores — the `hcert` hypothesis of
`lemma_B`, per PASS file. -/
theorem checkCaseI_kill {c : CCertI} (h : checkCaseI c = true) (hno : c.nofams = [])
    {Q : Fin c.n → Set RP} (hQ : IsStrictFamily c.n (caseSide c) Q)
    (own : Fin c.cores.length → Fin c.n)
    (hown : ∀ j : Fin c.cores.length, coreSet (c.cores.get j) ⊆ Q (own j)) :
    False := by
  obtain ⟨i, -, hex⟩ := checkCaseI_no_family h hQ own hown
  exact caseExempt_of_nil hno _ hex

end

end S11
end PackingCert
