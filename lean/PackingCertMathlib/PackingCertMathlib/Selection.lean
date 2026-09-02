import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.Attain
import PackingCertMathlib.Dilation
import PackingCertMathlib.Skeleton
import PackingCertMathlib.TopLevel

/-!
# Selection: the k-maximal minimiser and the CC-2 exchange (teleport) lemma
(A75, depgraph nodes B.SEL and C.CC2)

Prose: A53 `notes/lemmas.md` L6 (grid-completing slides), A58 `notes/theory.md` §2
CC-2/CC-2′ (the exchange = teleport, which subsumes L6), `docs/proofs/unique_transfer.md`
§2 (the selection chain at side ŝ and the H1 degenerate-case list).

What is formal here, and what is the named obligation:

* **`exists_kmax`** — the selection itself: over the (nonempty, by `attained`) packings at
  the minimal side, any ℕ-valued score bounded by 11 (the skeleton size `k = |Simp|`) is
  attained by some packing.  Pure order theory (`Nat.sSup_mem`); no geometry.
* **`teleport_packing`** — the geometric core of CC-2: replacing one square of a packing by
  the axis-aligned unit square on a slot box that lies in the container and is
  interior-disjoint from every OTHER square gives a packing at the SAME side.  This is the
  step the prose calls "P′ is a packing; σ(P′) ≤ m; σ(P′) ≥ m by minimality".  No corridor,
  no slide, no blocking geometry appears — exactly A58 Remark (a).
* **`cc2_stuck`** — CC-2/CC-2′ with the census interface explicit: IF teleporting a
  non-simple square onto a completable slot strictly increases `k` (hypothesis `hinc` — the
  census facts "simplicity is monotone in the occupied-slot pattern" + "a completable cell
  completes a Young diagram", A58's proof paragraph), THEN at a k-maximal packing every
  completable slot box in the container is interior-met by a square OTHER than any given
  non-simple square.  With two non-simple candidates this is (R2) "≥ 2 non-simple meeters
  or a simple meeter" of CC-2′.

**Named obligation (unchanged, F11/H2):** `hinc` is a property of the Young-form census
(`Simp`, the skeleton-of-a-packing function), which is not yet a Lean definition — the same
debt as `hface` in `Skeleton.lean`.  Everything else in CC-2 is proved.

**Degenerate-case audit (the H1 checklist of B.SEL), as the Lean statement sees it.**  The
slide formulation (L6) needs corridors; its degenerate cases (a slide creating a contact
mid-way, ties, σ-changing slides, a square simple in one normalisation only) are the
reason B.SEL was flagged.  In the teleport formulation every one of them is absent BY THE
SHAPE OF THE STATEMENT: `teleport_packing` has no corridor hypothesis (only the endpoint
box matters); the side is fixed (`CfgPacking m`), so σ-changing moves never arise; ties
need no canonical choice (`exists_kmax` picks any maximiser); double completion (the
teleported square completing a second corner's diagram) only strengthens `hinc`; and the
frame is `[0,m]²` itself, so "simple in one normalisation only" is the D4 quotient handled
by the census (E.2, `Skeleton.lean`).  The one genuine residue is the census interface
`hinc`, recorded above.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-- The axis-aligned closed unit square centred at `c` (a slot box). -/
def slotBox (c : RP) : Set RP :=
  Icc (c.1 - 1 / 2) (c.1 + 1 / 2) ×ˢ Icc (c.2 - 1 / 2) (c.2 + 1 / 2)

theorem slotBox_eq_set (c : RP) : slotBox c = (⟨c.1, c.2, 0⟩ : PSq).set := by
  rw [set_of_t_zero rfl]
  rfl

theorem isUnitSquare_slotBox (c : RP) : IsUnitSquare (slotBox c) := by
  rw [slotBox_eq_set]
  exact psq_isUnitSquare _

/-- The exchange (teleport): square `i` is replaced by the axis-aligned unit square at
`c` (tilt `t = 0`). -/
def teleport (z : Cfg) (i : Fin 11) (c : RP) : Cfg :=
  Function.update z i ⟨c.1, c.2, 0⟩

theorem teleport_self (z : Cfg) (i : Fin 11) (c : RP) :
    (teleport z i c i).set = slotBox c := by
  simp only [teleport, Function.update_self]
  rw [slotBox_eq_set]

theorem teleport_ne (z : Cfg) (i : Fin 11) (c : RP) {j : Fin 11} (hj : j ≠ i) :
    teleport z i c j = z j := by
  simp only [teleport, Function.update_of_ne hj]

/-! ## The selection -/

/-- **Selection (B.SEL, the choice step).**  Among the packings at side `m` (nonempty), a
score `k : Cfg → ℕ` bounded by 11 is maximised by some packing.  Applied with `k = |Simp|`
(the skeleton size) at the attained minimum `m` (`attained`, A68), this is "WLOG the
minimiser is k-maximal" of A53 L6 / A58 CC-2. -/
theorem exists_kmax (m : ℝ) (hne : ∃ z : Cfg, CfgPacking m z) (k : Cfg → ℕ)
    (hk : ∀ z, k z ≤ 11) :
    ∃ z : Cfg, CfgPacking m z ∧ ∀ z' : Cfg, CfgPacking m z' → k z' ≤ k z := by
  set S : Set ℕ := {n | ∃ z : Cfg, CfgPacking m z ∧ k z = n} with hS
  have hSne : S.Nonempty := by
    obtain ⟨z, hz⟩ := hne
    exact ⟨k z, z, hz, rfl⟩
  have hSbdd : BddAbove S := by
    refine ⟨11, ?_⟩
    rintro n ⟨z, -, rfl⟩
    exact hk z
  obtain ⟨z, hz, hkz⟩ := Nat.sSup_mem hSne hSbdd
  refine ⟨z, hz, fun z' hz' => ?_⟩
  rw [hkz]
  exact le_csSup hSbdd ⟨z', hz', rfl⟩

/-! ## The teleport step -/

/-- **The exchange preserves the packing property at the same side** (CC-2's geometric
content).  Hypotheses: the slot box lies in the container, and its interior misses the
interior of every OTHER square (the moved square itself may meet it — CC-2′). -/
theorem teleport_packing {m : ℝ} {z : Cfg} (hz : CfgPacking m z) (i : Fin 11) (c : RP)
    (hbox : slotBox c ⊆ container m)
    (hfree : ∀ j, j ≠ i → Disjoint (interior (slotBox c)) (interior (z j).set)) :
    CfgPacking m (teleport z i c) := by
  obtain ⟨ht, hP⟩ := hz
  refine ⟨?_, ?_⟩
  · intro j
    by_cases hj : j = i
    · subst hj
      simp only [teleport, Function.update_self]
      exact ⟨le_refl _, by norm_num⟩
    · rw [teleport_ne z i c hj]
      exact ht j
  · refine ⟨?_, ?_, ?_⟩
    · intro j
      by_cases hj : j = i
      · subst hj
        rw [teleport_self]
        exact isUnitSquare_slotBox c
      · rw [teleport_ne z i c hj]
        exact hP.unit j
    · intro j
      by_cases hj : j = i
      · subst hj
        rw [teleport_self]
        exact hbox
      · rw [teleport_ne z i c hj]
        exact hP.contained j
    · intro j l hjl
      by_cases hj : j = i
      · subst hj
        have hl : l ≠ j := fun h => hjl h.symm
        rw [teleport_self, teleport_ne z j c hl]
        exact hfree l hl
      · by_cases hl : l = i
        · subst hl
          rw [teleport_self, teleport_ne z l c hj]
          exact (hfree j hj).symm
        · rw [teleport_ne z i c hj, teleport_ne z i c hl]
          exact hP.interiorDisjoint j l hjl

/-! ## CC-2 / CC-2′: k-maximal packings are teleport-stuck -/

/-- **Lemma CC-2 / CC-2′ (teleport-stuckness), census interface explicit.**
At a k-maximal packing `z` at side `m`: for every slot box `B = slotBox c` in the
container and every "non-simple" index `i` such that teleporting `i` onto `c` would
strictly raise `k` whenever `B` is interior-free of the other squares (`hinc` — the census
property, A58's proof paragraph: completability + monotonicity of simplicity), SOME square
other than `i` interior-meets `B`.  CC-2 is the instance "no square meets `B`" (then any
non-simple `i` teleports); CC-2′ is "the only meeter is the non-simple `i`" (then `i`
itself teleports).  Consequence (R1)/(R2): every completable box carries a simple meeter or
at least two non-simple meeters. -/
theorem cc2_stuck {m : ℝ} {z : Cfg} (hz : CfgPacking m z) (k : Cfg → ℕ)
    (hmax : ∀ z' : Cfg, CfgPacking m z' → k z' ≤ k z)
    (c : RP) (hbox : slotBox c ⊆ container m) (i : Fin 11)
    (hinc : (∀ j, j ≠ i → Disjoint (interior (slotBox c)) (interior (z j).set)) →
      k z < k (teleport z i c)) :
    ∃ j, j ≠ i ∧ ¬ Disjoint (interior (slotBox c)) (interior (z j).set) := by
  by_contra hno
  push Not at hno
  have hfree : ∀ j, j ≠ i → Disjoint (interior (slotBox c)) (interior (z j).set) :=
    fun j hj => hno j hj
  have h1 := hinc hfree
  have h2 := hmax _ (teleport_packing hz i c hbox hfree)
  omega

/-- The two-candidate form of CC-2′: with two distinct non-simple squares `i ≠ i'`, either
some third square interior-meets the box, or both `i` and `i'` do (≥ 2 non-simple meeters). -/
theorem cc2_two_meeters {m : ℝ} {z : Cfg} (hz : CfgPacking m z) (k : Cfg → ℕ)
    (hmax : ∀ z' : Cfg, CfgPacking m z' → k z' ≤ k z)
    (c : RP) (hbox : slotBox c ⊆ container m) {i i' : Fin 11} (hii : i ≠ i')
    (hinc : ∀ l, l = i ∨ l = i' →
      (∀ j, j ≠ l → Disjoint (interior (slotBox c)) (interior (z j).set)) →
      k z < k (teleport z l c)) :
    (∃ j, j ≠ i ∧ j ≠ i' ∧ ¬ Disjoint (interior (slotBox c)) (interior (z j).set)) ∨
    (¬ Disjoint (interior (slotBox c)) (interior (z i).set) ∧
      ¬ Disjoint (interior (slotBox c)) (interior (z i').set)) := by
  obtain ⟨j, hji, hj⟩ := cc2_stuck hz k hmax c hbox i (hinc i (Or.inl rfl))
  obtain ⟨j', hji', hj'⟩ := cc2_stuck hz k hmax c hbox i' (hinc i' (Or.inr rfl))
  by_cases hjj : j = i'
  · subst hjj
    by_cases hj'i : j' = i
    · subst hj'i
      exact Or.inr ⟨hj', hj⟩
    · exact Or.inl ⟨j', hj'i, hji', hj'⟩
  · exact Or.inl ⟨j, hji, hjj, hj⟩

end

end S11
end PackingCert
