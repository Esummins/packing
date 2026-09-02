import PackingCertMathlib.Census
import PackingCertMathlib.Selection

/-!
# The census interface of the selection lemma, discharged (A78, depgraph nodes B.SEL,
C.CC2)

`Selection.lean` (A75) proved CC-2/CC-2′ conditional on `hinc`: "teleporting a non-simple
square onto a completable slot strictly raises `k = |Simp|`".  With `Simp` now the Lean
definition `skeleton` (`Census.lean`) this is a theorem (`card_lt_teleport`): the old
skeleton survives the teleport (its occupiers are not the moved square — it is
non-simple, `skeleton_teleport_mono`), and the target cell joins it (its proper
predecessors are skeleton cells, the moved square now sits on it,
`teleport_completes`).  The composed statements `cc2_stuck_census` /
`cc2_two_meeters_census` are B.SEL/C.CC2 with NO census hypothesis left, and
`exists_kmax_skeleton` is the selection with `k = |skeleton|` (bounded by
`skeleton_card_le`, B6).

Note the degenerate case A75 listed — the teleported square completing a SECOND corner's
diagram (double completion) — needs nothing here: `Finset.card_lt_card` only uses
`old ⊂ new`.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-- Square `i` is **non-simple**: it occupies no skeleton slot. -/
def NonSimple (s : ℝ) (z : Cfg) (i : Fin 11) : Prop :=
  ∀ a ∈ skeleton s z, ¬OccupiesSlot (z i) (slotCentre s a)

/-- Slot `a` is **completable** (Young-ready): a small non-skeleton cell all of whose
proper predecessors are skeleton cells. -/
def Completable (s : ℝ) (z : Cfg) (a : Slot) : Prop :=
  a.small ∧ a ∉ skeleton s z ∧
    ∀ i' ≤ a.cellx, ∀ j' ≤ a.celly, (i', j') ≠ (a.cellx, a.celly) →
      (⟨a.corner, i', j'⟩ : Slot) ∈ skeleton s z

theorem slotBox_eq_slotSet (c : RP) : slotBox c = slotSet c := rfl

/-- Predecessor cells of a skeleton cell are skeleton cells. -/
theorem pred_mem_skeleton {s : ℝ} {z : Cfg} {a : Slot} (ha : a ∈ skeleton s z)
    {i' j' : ℕ} (hi' : i' ≤ a.cellx) (hj' : j' ≤ a.celly) :
    (⟨a.corner, i', j'⟩ : Slot) ∈ skeleton s z := by
  rw [mem_skeleton] at ha ⊢
  obtain ⟨⟨hx, hy⟩, hsk⟩ := ha
  refine ⟨⟨by simp only; omega, by simp only; omega⟩, ?_⟩
  intro i'' hi'' j'' hj''
  exact hsk i'' (le_trans hi'' hi') j'' (le_trans hj'' hj')

/-- An occupier of a skeleton slot is not a non-simple square. -/
theorem occupier_ne {s : ℝ} {z : Cfg} {i : Fin 11} (hi : NonSimple s z i) {a : Slot}
    (ha : a ∈ skeleton s z) {k : Fin 11} (hk : OccupiesSlot (z k) (slotCentre s a)) :
    k ≠ i := by
  rintro rfl
  exact hi a ha hk

/-- **The old skeleton survives a teleport of a non-simple square.** -/
theorem skeleton_teleport_mono {s : ℝ} {z : Cfg} {i : Fin 11} (hi : NonSimple s z i)
    (c : RP) : skeleton s z ⊆ skeleton s (teleport z i c) := by
  intro a ha
  have ha' := ha
  rw [mem_skeleton] at ha' ⊢
  refine ⟨ha'.1, ?_⟩
  intro i' hi' j' hj'
  obtain ⟨k, hk⟩ := ha'.2 i' hi' j' hj'
  have hk' : k ≠ i := occupier_ne hi (pred_mem_skeleton ha hi' hj') hk
  exact ⟨k, by rw [teleport_ne z i c hk']; exact hk⟩

/-- **The completable cell joins the skeleton** after the teleport. -/
theorem teleport_completes {s : ℝ} {z : Cfg} {i : Fin 11} (hi : NonSimple s z i)
    {a : Slot} (ha : Completable s z a) :
    a ∈ skeleton s (teleport z i (slotCentre s a)) := by
  obtain ⟨hsmall, -, hpred⟩ := ha
  rw [mem_skeleton]
  refine ⟨hsmall, ?_⟩
  intro i' hi' j' hj'
  by_cases heq : (i', j') = (a.cellx, a.celly)
  · simp only [Prod.mk.injEq] at heq
    obtain ⟨rfl, rfl⟩ := heq
    refine ⟨i, ?_⟩
    have hself : teleport z i (slotCentre s a) i
        = ⟨(slotCentre s a).1, (slotCentre s a).2, 0⟩ := by
      simp [teleport]
    rw [hself]
    exact occupiesSlot_of_axis (Or.inl rfl) rfl rfl
  · have hb := hpred i' hi' j' hj' heq
    obtain ⟨k, hk⟩ := occupied_self (mem_skeleton.mp hb).2
    have hk' : k ≠ i := occupier_ne hi hb hk
    exact ⟨k, by rw [teleport_ne z i _ hk']; exact hk⟩

/-- **`hinc`, discharged:** teleporting a non-simple square onto a completable slot
strictly increases `k = |skeleton|`. -/
theorem card_lt_teleport {s : ℝ} {z : Cfg} {i : Fin 11} (hi : NonSimple s z i) {a : Slot}
    (ha : Completable s z a) :
    (skeleton s z).card < (skeleton s (teleport z i (slotCentre s a))).card :=
  Finset.card_lt_card ⟨skeleton_teleport_mono hi _,
    fun hsub => ha.2.1 (hsub (teleport_completes hi ha))⟩

/-- **B.SEL — the selection with `k = |skeleton|`:** at any side `m ∈ (3,4)` admitting a
packing, some packing maximises the skeleton size. -/
theorem exists_kmax_skeleton {m : ℝ} (hm3 : 3 < m) (hm4 : m < 4)
    (hne : ∃ z : Cfg, CfgPacking m z) :
    ∃ z : Cfg, CfgPacking m z ∧
      ∀ z' : Cfg, CfgPacking m z' → (skeleton m z').card ≤ (skeleton m z).card :=
  exists_kmax m hne (fun z => (skeleton m z).card) (fun z => skeleton_card_le hm3 hm4 z)

/-- **CC-2 / CC-2′ (C.CC2), census hypothesis discharged.**  At a `k`-maximal packing,
every completable slot box inside the container is interior-met by a square other than
any given non-simple square. -/
theorem cc2_stuck_census {m : ℝ} {z : Cfg} (hz : CfgPacking m z)
    (hmax : ∀ z' : Cfg, CfgPacking m z' → (skeleton m z').card ≤ (skeleton m z).card)
    {a : Slot} (ha : Completable m z a) (hbox : slotBox (slotCentre m a) ⊆ container m)
    {i : Fin 11} (hi : NonSimple m z i) :
    ∃ j, j ≠ i ∧ ¬Disjoint (interior (slotBox (slotCentre m a))) (interior (z j).set) :=
  cc2_stuck hz (fun z' => (skeleton m z').card) hmax (slotCentre m a) hbox i
    (fun _ => card_lt_teleport hi ha)

/-- The two-candidate form (CC-2′, `(R2)`): a third meeter, or both non-simple squares
meet. -/
theorem cc2_two_meeters_census {m : ℝ} {z : Cfg} (hz : CfgPacking m z)
    (hmax : ∀ z' : Cfg, CfgPacking m z' → (skeleton m z').card ≤ (skeleton m z).card)
    {a : Slot} (ha : Completable m z a) (hbox : slotBox (slotCentre m a) ⊆ container m)
    {i i' : Fin 11} (hii : i ≠ i') (hi : NonSimple m z i) (hi' : NonSimple m z i') :
    (∃ j, j ≠ i ∧ j ≠ i' ∧
      ¬Disjoint (interior (slotBox (slotCentre m a))) (interior (z j).set)) ∨
    (¬Disjoint (interior (slotBox (slotCentre m a))) (interior (z i).set) ∧
      ¬Disjoint (interior (slotBox (slotCentre m a))) (interior (z i').set)) :=
  cc2_two_meeters hz (fun z' => (skeleton m z').card) hmax (slotCentre m a) hbox hii
    (fun l hl _ => by
      rcases hl with rfl | rfl
      · exact card_lt_teleport hi ha
      · exact card_lt_teleport hi' ha)

end

end S11
end PackingCert
