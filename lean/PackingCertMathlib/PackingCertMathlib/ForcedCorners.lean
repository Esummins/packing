import PackingCertMathlib.Selection
import PackingCertMathlib.Sideband

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

* `mem_interior_scaleC_iff`, `fc_transfer` — **Theorem FC Step 2** in the bottom-left corner
  frame: an interior point of a square in the open slot box transfers under the dilation
  `scaleC λ` to an interior point of the dilate inside the WIDENED box `B_p⁺`.

Left [C]: the other three corner frames (the D4 transport of Step 2), and Corollaries
FC-corner (Lemma A2, `Sideband.distinct_cells`, applies verbatim once the two meeters are in the
quadrant) and FC-count.  No axiom is introduced.
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


/-! ## 3. Theorem FC, Step 2 — the transfer to the dilate (bottom-left corner frame) -/

/-- Under the dilation `scaleC λ` (centres scaled, tilt fixed) a square is TRANSLATED by
`(λ − 1)·c`: `p` is an interior point of `q` iff `p + (λ − 1)c` is one of `scaleC λ q`. -/
theorem mem_interior_scaleC_iff (lam : ℝ) (q : PSq) (p : RP) :
    (p.1 + (lam - 1) * q.cx, p.2 + (lam - 1) * q.cy) ∈ interior (scaleC lam q).set ↔
      p ∈ interior q.set := by
  rw [mem_interior_iff_uv, mem_interior_iff_uv]
  simp only [scaleC, rdot, edir, perpV]
  have e1 : (p.1 + (lam - 1) * q.cx - lam * q.cx) * cosT q.t
      + (p.2 + (lam - 1) * q.cy - lam * q.cy) * sinT q.t
      = (p.1 - q.cx) * cosT q.t + (p.2 - q.cy) * sinT q.t := by ring
  have e2 : (p.1 + (lam - 1) * q.cx - lam * q.cx) * -sinT q.t
      + (p.2 + (lam - 1) * q.cy - lam * q.cy) * cosT q.t
      = (p.1 - q.cx) * -sinT q.t + (p.2 - q.cy) * cosT q.t := by ring
  rw [e1, e2]

/-- `d² ≤ 1/2 ⇒ |d| ≤ 1/√2` — the per-coordinate form of `sideband.md` (F1). -/
theorem abs_le_inv_sqrt_two {d : ℝ} (h : d ^ 2 ≤ 1 / 2) : |d| ≤ 1 / Real.sqrt 2 := by
  have h' : d ^ 2 ≤ (2 : ℝ)⁻¹ := by rwa [inv_eq_one_div]
  rw [one_div, ← Real.sqrt_inv, ← Real.sqrt_sq_eq_abs]
  exact Real.sqrt_le_sqrt h'

/-- **Theorem FC, Step 2** (`forced_corners.md` §2, bottom-left corner frame).  An interior point
`p` of `q` inside the open slot box `(i, i+1) × (j, j+1)` transfers, under the dilation by
`λ ∈ [1, λ_max]`, to the interior point `p + (λ − 1)c` of `scaleC λ q` inside the WIDENED box
`(i, i + 1 + π_i) × (j, j + 1 + π_j)`, `π_i = (λ_max − 1)(i + 1 + 1/√2)`; the lower bounds hold
for `i, j ≥ 1` (at `i = 0` the document uses the container margin instead). -/
theorem fc_transfer (q : PSq) (p : RP) (hp : p ∈ interior q.set) (i j lam lmax : ℝ)
    (hi0 : 0 ≤ i) (hj0 : 0 ≤ j) (h1 : 1 ≤ lam) (h2 : lam ≤ lmax)
    (hpx : i < p.1 ∧ p.1 < i + 1) (hpy : j < p.2 ∧ p.2 < j + 1) :
    (p.1 + (lam - 1) * q.cx, p.2 + (lam - 1) * q.cy) ∈ interior (scaleC lam q).set ∧
    p.1 + (lam - 1) * q.cx < i + 1 + (lmax - 1) * (i + 1 + 1 / Real.sqrt 2) ∧
    p.2 + (lam - 1) * q.cy < j + 1 + (lmax - 1) * (j + 1 + 1 / Real.sqrt 2) ∧
    (1 ≤ i → i < p.1 + (lam - 1) * q.cx) ∧ (1 ≤ j → j < p.2 + (lam - 1) * q.cy) := by
  have hd := sqdist_centre_le_half q (interior_subset hp)
  set r : ℝ := 1 / Real.sqrt 2 with hr
  have hr0 : 0 < r := by positivity
  have hr2 : r ^ 2 = 1 / 2 := by
    rw [hr, div_pow, one_pow, Real.sq_sqrt (by norm_num)]
  have hr1 : r ≤ 1 := by nlinarith
  have hx : |p.1 - q.cx| ≤ r := abs_le_inv_sqrt_two (by nlinarith [sq_nonneg (p.2 - q.cy)])
  have hy : |p.2 - q.cy| ≤ r := abs_le_inv_sqrt_two (by nlinarith [sq_nonneg (p.1 - q.cx)])
  obtain ⟨hx0, hx1⟩ := abs_le.mp hx
  obtain ⟨hy0, hy1⟩ := abs_le.mp hy
  have hl : 0 ≤ lam - 1 := by linarith
  have hcx1 : q.cx ≤ i + 1 + r := by linarith [hpx.2]
  have hcy1 : q.cy ≤ j + 1 + r := by linarith [hpy.2]
  have hcx0 : i - r ≤ q.cx := by linarith [hpx.1]
  have hcy0 : j - r ≤ q.cy := by linarith [hpy.1]
  refine ⟨(mem_interior_scaleC_iff lam q p).mpr hp, ?_, ?_, ?_, ?_⟩
  · have m1 : (lam - 1) * q.cx ≤ (lam - 1) * (i + 1 + r) := mul_le_mul_of_nonneg_left hcx1 hl
    have m2 : (lam - 1) * (i + 1 + r) ≤ (lmax - 1) * (i + 1 + r) :=
      mul_le_mul_of_nonneg_right (by linarith) (by linarith [hr0])
    linarith [hpx.2]
  · have m1 : (lam - 1) * q.cy ≤ (lam - 1) * (j + 1 + r) := mul_le_mul_of_nonneg_left hcy1 hl
    have m2 : (lam - 1) * (j + 1 + r) ≤ (lmax - 1) * (j + 1 + r) :=
      mul_le_mul_of_nonneg_right (by linarith) (by linarith [hr0])
    linarith [hpy.2]
  · intro hi
    have m1 : (lam - 1) * (i - r) ≤ (lam - 1) * q.cx := mul_le_mul_of_nonneg_left hcx0 hl
    have m2 : 0 ≤ (lam - 1) * (i - r) := mul_nonneg hl (by linarith [hr1])
    linarith [hpx.1]
  · intro hj
    have m1 : (lam - 1) * (j - r) ≤ (lam - 1) * q.cy := mul_le_mul_of_nonneg_left hcy0 hl
    have m2 : 0 ≤ (lam - 1) * (j - r) := mul_nonneg hl (by linarith [hr1])
    linarith [hpy.1]

end

end ForcedCorners
end S11
end PackingCert
