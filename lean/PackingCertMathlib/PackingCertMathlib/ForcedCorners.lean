import PackingCertMathlib.Selection

/-!
# Forced corners — Lemma SLOT-CROWD (Theorem FC, Step 1) as a Lean object (A192, from A178)

`docs/proofs/forced_corners.md` Theorem FC, Step 1 (at side `m`; `slot_crowds.md` §2 Lemma
SLOT-CROWD): a packing at side `m` containing the pins of a class `S`, at an UNCLIPPED cell `p`
not in `S` whose extension class `T = S ∪ {p}` is killed at side `m`, has at least TWO distinct
NON-pin squares whose interiors meet the open slot box `int B_p(m)`.

The proof is the teleport of `Selection.teleport_packing`: with at most one non-pin meeter,
replace the meeter (or, with none, any non-pin square) by the slot square `B_p(m)` itself; the
result is a packing at side `m` — the slot box is in the container and interior-disjoint from
every OTHER square — and it contains the pins of `T` (the old assignment on `S`, `p ↦ the
teleported square`), contradicting the kill.  "Unclipped" is the hypothesis that the pins'
squares miss `int B_p(m)`; the kill is in `Skeleton.ContainsPins`'s monotone form (what a
window certificate delivers through `Dilation.lemma_B` / K1).

* `slot_crowd_key` — the teleport step: a non-pin square all of whose companions miss the box
  cannot exist, so every non-pin square has a companion meeting the box;
* `slot_crowd` — **Lemma SLOT-CROWD / Theorem FC Step 1**: two distinct non-pin meeters.

Left [C]: Step 2 of Theorem FC (the transfer to the dilate `Δ_λ P` with the widened box
`B_p⁺`, an affine computation on `sideband.md` (F1)), and Corollaries FC-corner (Lemma A2,
`Sideband.distinct_cells`, applies verbatim once the two meeters are in the quadrant) and
FC-count.  No axiom is introduced.
-/

namespace PackingCert
namespace S11
namespace ForcedCorners

open Set

noncomputable section

/-- A square index is NON-pin for the assignment `f` of the pin-set `S`. -/
def NonPin (S : PinSet) (f : Slot → Fin 11) (i : Fin 11) : Prop := ∀ a ∈ S, f a ≠ i

/-- **The teleport step.**  If a non-pin square `i` had every other square interior-disjoint
from the slot box, teleporting `i` onto the slot would produce a packing containing the pins of
`insert p S` — so, under the kill of `insert p S`, some OTHER square meets the box. -/
theorem slot_crowd_key {m : ℝ} {z : Cfg} (hz : CfgPacking m z) (S : PinSet) (p : Slot)
    (hp : p ∉ S) (f : Slot → Fin 11) (hinj : Set.InjOn f ↑S)
    (hocc : ∀ a ∈ S, OccupiesSlot (z (f a)) (slotCentre m a))
    (hbox : slotBox (slotCentre m p) ⊆ container m)
    (hkill : ∀ z' : Cfg, CfgPacking m z' → ¬ ContainsPins (insert p S) m z')
    (i : Fin 11) (hi : NonPin S f i) :
    ∃ j, j ≠ i ∧ ¬ Disjoint (interior (slotBox (slotCentre m p))) (interior (z j).set) := by
  by_contra hno
  push Not at hno
  have hfree : ∀ j, j ≠ i →
      Disjoint (interior (slotBox (slotCentre m p))) (interior (z j).set) :=
    fun j hj => hno j hj
  have hz' := teleport_packing hz i (slotCentre m p) hbox hfree
  refine hkill _ hz' ⟨Function.update f p i, ?_, ?_⟩
  · -- injective on `insert p S`
    intro a ha b hb hab
    rw [Finset.coe_insert, Set.mem_insert_iff] at ha hb
    rcases ha with ha | ha <;> rcases hb with hb | hb
    · rw [ha, hb]
    · have hbp : b ≠ p := fun h => hp (h ▸ hb)
      rw [ha, Function.update_self, Function.update_of_ne hbp] at hab
      exact absurd hab.symm (hi b hb)
    · have hap : a ≠ p := fun h => hp (h ▸ ha)
      rw [hb, Function.update_of_ne hap, Function.update_self] at hab
      exact absurd hab (hi a ha)
    · have hap : a ≠ p := fun h => hp (h ▸ ha)
      have hbp : b ≠ p := fun h => hp (h ▸ hb)
      rw [Function.update_of_ne hap, Function.update_of_ne hbp] at hab
      exact hinj ha hb hab
  · -- every pin of `insert p S` is occupied
    intro a ha
    rw [Finset.mem_insert] at ha
    rcases ha with ha | ha
    · rw [ha, Function.update_self, OccupiesSlot, teleport_self]
      rfl
    · have hap : a ≠ p := fun h => hp (h ▸ ha)
      rw [Function.update_of_ne hap, teleport_ne z i _ (hi a ha)]
      exact hocc a ha

/-- **Lemma SLOT-CROWD (Theorem FC, Step 1).**  At side `m`: a packing containing the pins of
`S` (assignment `f`), an unclipped cell `p ∉ S` (the pins' squares miss the open slot box),
at least one non-pin square, and the kill of `insert p S` at side `m` — then two DISTINCT
non-pin squares have interiors meeting the open slot box `int B_p(m)`. -/
theorem slot_crowd {m : ℝ} {z : Cfg} (hz : CfgPacking m z) (S : PinSet) (p : Slot)
    (hp : p ∉ S) (f : Slot → Fin 11) (hinj : Set.InjOn f ↑S)
    (hocc : ∀ a ∈ S, OccupiesSlot (z (f a)) (slotCentre m a))
    (hbox : slotBox (slotCentre m p) ⊆ container m)
    (hunclip : ∀ a ∈ S,
      Disjoint (interior (slotBox (slotCentre m p))) (interior (z (f a)).set))
    (hnonpin : ∃ i, NonPin S f i)
    (hkill : ∀ z' : Cfg, CfgPacking m z' → ¬ ContainsPins (insert p S) m z') :
    ∃ i i', i ≠ i' ∧ NonPin S f i ∧ NonPin S f i' ∧
      ¬ Disjoint (interior (slotBox (slotCentre m p))) (interior (z i).set) ∧
      ¬ Disjoint (interior (slotBox (slotCentre m p))) (interior (z i').set) := by
  -- a meeter is never a pin
  have hnp : ∀ j, ¬ Disjoint (interior (slotBox (slotCentre m p))) (interior (z j).set) →
      NonPin S f j := by
    intro j hj a ha hfa
    exact hj (hfa ▸ hunclip a ha)
  obtain ⟨i0, hi0⟩ := hnonpin
  obtain ⟨j, -, hj⟩ := slot_crowd_key hz S p hp f hinj hocc hbox hkill i0 hi0
  have hjnp := hnp j hj
  obtain ⟨j', hjj', hj'⟩ := slot_crowd_key hz S p hp f hinj hocc hbox hkill j hjnp
  exact ⟨j, j', hjj'.symm, hjnp, hnp j' hj', hj, hj'⟩

end

end ForcedCorners
end S11
end PackingCert
