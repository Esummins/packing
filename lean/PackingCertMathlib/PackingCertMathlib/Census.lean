import Mathlib.Tactic
import Mathlib.Data.List.Lex
import Mathlib.Data.Finset.Sort
import PackingCertMathlib.Parametrize
import PackingCertMathlib.Attain
import PackingCertMathlib.Dilation
import PackingCertMathlib.Skeleton

/-!
# The Young-form skeleton census as a Lean DEFINITION (A78, depgraph nodes B.CENSUS,
B.EXACT, B.SEL, C.CC2 — checklist F11/H2)

This file is the authoritative Young-form definition of A53 L1–L3
(`attempts/A53-simple-strata/notes/lemmas.md`), pinned so that every one of the eight
BINDING choices B1–B8 of `attempts/A72-census-cleanroom/notes/ambiguities.md` is a
line of Lean rather than a reading:

* **the skeleton of a packing** (`skeleton s z`): for each container corner the set of
  Young cells whose whole down-set is occupied by axis-aligned unit squares of the
  packing sitting EXACTLY on the corner grid (`IsSkelCell`).  This is A53 L1's "largest
  Young set at `c`" — the union of all Young sets of occupied cells is the set of
  occupied cells whose down-set is occupied — read as a predicate on cells;
* **the census** (`censusL` / `censusF`): all 4-tuples of Young diagrams in the `3×3`
  box whose slot squares are pairwise interior-disjoint, the B2 predicate decided
  COMBINATORIALLY (`axisFar`) for every side `s ∈ (3, 4)` — it is proved
  (`slotFar_iff`) that the combinatorial predicate equals the real one
  `max (|Δx|, |Δy|) ≥ 1` at every such side, so the census is one object on the whole
  window (A53 L2(iv), sharpened from `(3.82, 3.9)` to `(3, 4)`);
* **exhaustiveness** (`skeleton_mem_census`): every packing at any side `s ∈ (3, 4)`
  has its skeleton in the census — this is A53 L3 as a THEOREM about packings, not a
  count (the count `1110 / 163` and the agreement with A72's corpus are the
  `native_decide` facts of `CensusCheck.lean`, which nothing in the composition uses);
* **the D4 action** (`d4Apply`, `d4Sq`, `d4Slot`, `d4Pins`): the eight signed
  permutations about the container centre, acting on points, on parametrised squares
  (tilt `t ↦ (1−t)/(1+t)` for the reflections, R5 of `d4_reduction_s0.md`), on slots
  (R8's `λ / λᵀ` rule, now a THEOREM `d4Apply_slotCentre`) and on pin-sets; the action
  preserves packings (`d4_packing`) and the skeleton is equivariant
  (`skeleton_d4`) — the E.2 bookkeeping of `instratum_bridge.md`, machine-checked;
* **classes and the bridge**: `InClass T s z` = "the skeleton is a D4-image of `T`";
  `containsPins_skeleton` (the `hface` of `Skeleton.lean`: exact ⟹ contains, by
  reflexivity) and `class_kill` (Lemma M→E, E.2: a monotone kill of `S ≤ g·T` at side
  `s` empties the exact class of `T`); `skeleton_card_le` (B6: `k ≤ 11`, a theorem);
* the **teleport interface** `hinc` of `Selection.lean` is discharged in
  `CensusSelection.lean` (teleporting a non-simple square onto a completable slot
  raises `k`).

## The B1–B8 resolutions (each cited at its definition)

* **B1** "inside 3×3" is DERIVED: `skelCell_lt_three` — at `s < 4` an occupied slot has
  offsets `< 3` (the square would leave the container); the census enumerates the
  `3×3` box and the theorem says nothing is lost.
* **B2** interior-disjointness of two axis-aligned unit squares at centres `p, q` is
  `max(|Δx|,|Δy|) ≥ 1` (`slotBox_interior_disjoint_iff`), flush contact allowed.
* **B3** one square cannot occupy two slots of different corners: `slotCentre_injective`
  at `s ∉ ℤ` (here `s ∈ (3,4)`), so the four corner diagrams partition the skeleton.
* **B4** NO maximality/realizability filter: `IsCensusTuple` is Young + disjoint only.
* **B5** the Young condition is per corner (`IsSkelCell` quantifies inside one corner).
* **B6** no cardinality cap is imposed; `skeleton_card_le : k ≤ 11` is a theorem.
* **B7** the empty diagram is a Young diagram (`∅` passes `IsYoungCells`).
* **B8** D4 acts on PLANE POINTS (`d4Apply`); the slot-level rule is the theorem
  `d4Apply_slotCentre`, never an input.
-/

namespace PackingCert
namespace S11

open Set

/-! ## Part A — the combinatorial layer (computable) -/

/-- Corner bits: is the corner on the right wall (`x = s`)?  Corner order of
`Skeleton.lean`: `0` = BL, `1` = BR, `2` = TR, `3` = TL. -/
def cornerR (c : Fin 4) : Bool := c = 1 ∨ c = 2

/-- Corner bits: is the corner on the top wall (`y = s`)? -/
def cornerT (c : Fin 4) : Bool := c = 2 ∨ c = 3

/-- The corner with the given bits. -/
def mkCorner (r t : Bool) : Fin 4 :=
  match r, t with
  | false, false => 0
  | true,  false => 1
  | true,  true  => 2
  | false, true  => 3

theorem mkCorner_cornerR (r t : Bool) : cornerR (mkCorner r t) = r := by
  cases r <;> cases t <;> decide

theorem mkCorner_cornerT (r t : Bool) : cornerT (mkCorner r t) = t := by
  cases r <;> cases t <;> decide

theorem mkCorner_bits (c : Fin 4) : mkCorner (cornerR c) (cornerT c) = c := by
  fin_cases c <;> decide

/-- **B2, combinatorial form.**  Two slot coordinates along one axis, given as (from-far-
wall bit, offset): their real values differ by `≥ 1` for EVERY side `s ∈ (3, 4)` iff
`axisFar` — same family: distinct offsets; opposite families: `i + j ≤ 1 ∨ 4 ≤ i + j`
(the real difference is `s − (i + j + 1)`).  Proved equivalent to the real predicate in
`axisFar_iff`. -/
def axisFar (r1 : Bool) (i1 : ℕ) (r2 : Bool) (i2 : ℕ) : Bool :=
  if r1 = r2 then decide (i1 ≠ i2) else decide (i1 + i2 ≤ 1 ∨ 4 ≤ i1 + i2)

/-- Two slots are far (their unit squares interior-disjoint at every side in `(3,4)`). -/
def slotFar (a b : Slot) : Bool :=
  axisFar (cornerR a.corner) a.cellx (cornerR b.corner) b.cellx ||
  axisFar (cornerT a.corner) a.celly (cornerT b.corner) b.celly

/-- The 36 slots of the `3×3` corner boxes, by code `corner*9 + cellx*3 + celly`. -/
def slotOfCode (n : ℕ) : Slot := ⟨⟨n / 9 % 4, Nat.mod_lt _ (by norm_num)⟩, n / 3 % 3, n % 3⟩

def Slot.code (a : Slot) : ℕ := a.corner.val * 9 + a.cellx * 3 + a.celly

/-- A slot of the `3×3` boxes. -/
def Slot.small (a : Slot) : Prop := a.cellx < 3 ∧ a.celly < 3

instance : DecidablePred Slot.small := fun a => inferInstanceAs (Decidable (_ ∧ _))

theorem slotOfCode_code (a : Slot) (h : a.small) : slotOfCode a.code = a := by
  obtain ⟨⟨c, hc⟩, i, j⟩ := a
  simp only [Slot.small] at h
  obtain ⟨hi, hj⟩ := h
  simp only [Slot.code, slotOfCode, Slot.mk.injEq, Fin.mk.injEq]
  omega

theorem code_lt (a : Slot) (h : a.small) : a.code < 36 := by
  obtain ⟨⟨c, hc⟩, i, j⟩ := a
  simp only [Slot.small] at h
  obtain ⟨hi, hj⟩ := h
  simp only [Slot.code]
  omega

/-- The 36 small slots. -/
def allSlots : List Slot := (List.range 36).map slotOfCode

theorem mem_allSlots_of_small {a : Slot} (h : a.small) : a ∈ allSlots :=
  List.mem_map.mpr ⟨a.code, List.mem_range.mpr (code_lt a h), slotOfCode_code a h⟩

theorem small_of_mem_allSlots {a : Slot} (h : a ∈ allSlots) : a.small := by
  obtain ⟨n, -, rfl⟩ := List.mem_map.mp h
  exact ⟨Nat.mod_lt _ (by norm_num), Nat.mod_lt _ (by norm_num)⟩

/-- **B5/B7** A set of cells is a Young diagram: closed under the componentwise order
(the empty set qualifies). -/
def IsYoungCells (D : Finset (ℕ × ℕ)) : Prop :=
  ∀ c ∈ D, ∀ i' ≤ c.1, ∀ j' ≤ c.2, (i', j') ∈ D

instance : DecidablePred IsYoungCells := fun D =>
  inferInstanceAs (Decidable (∀ c ∈ D, ∀ i' ≤ c.1, ∀ j' ≤ c.2, (i', j') ∈ D))

/-- The `3×3` cell box. -/
def box3 : Finset (ℕ × ℕ) := (Finset.range 3) ×ˢ (Finset.range 3)

def cellOfCode (n : ℕ) : ℕ × ℕ := (n / 3 % 3, n % 3)

/-- All subsets of the `3×3` box, as a list (`512` entries). -/
def subsets3 : List (Finset (ℕ × ℕ)) :=
  (List.range 9).sublists.map fun l => (l.map cellOfCode).toFinset

/-- The Young diagrams in the `3×3` box (`20` of them). -/
def youngL : List (Finset (ℕ × ℕ)) := subsets3.filter fun D => decide (IsYoungCells D)

theorem mem_subsets3 {D : Finset (ℕ × ℕ)} (hD : D ⊆ box3) : D ∈ subsets3 := by
  refine List.mem_map.mpr ⟨(List.range 9).filter (fun n => decide (cellOfCode n ∈ D)), ?_, ?_⟩
  · exact List.mem_sublists.mpr List.filter_sublist
  · ext c
    simp only [List.mem_toFinset, List.mem_map, List.mem_filter, List.mem_range,
      decide_eq_true_eq]
    constructor
    · rintro ⟨n, ⟨-, hn⟩, rfl⟩
      exact hn
    · intro hc
      have hb := hD hc
      simp only [box3, Finset.mem_product, Finset.mem_range] at hb
      refine ⟨c.1 * 3 + c.2, ⟨by omega, ?_⟩, ?_⟩
      · have : cellOfCode (c.1 * 3 + c.2) = c := by
          simp only [cellOfCode]
          ext <;> simp <;> omega
        rw [this]; exact hc
      · simp only [cellOfCode]
        ext <;> simp <;> omega

theorem mem_youngL {D : Finset (ℕ × ℕ)} (hD : D ⊆ box3) (hY : IsYoungCells D) :
    D ∈ youngL :=
  List.mem_filter.mpr ⟨mem_subsets3 hD, decide_eq_true hY⟩

/-- The pin-set of a corner diagram. -/
def cornerPins (c : Fin 4) (D : Finset (ℕ × ℕ)) : PinSet :=
  D.image fun ij => ⟨c, ij.1, ij.2⟩

/-- Assemble a 4-tuple of corner diagrams into one pin-set. -/
def assemble (D0 D1 D2 D3 : Finset (ℕ × ℕ)) : PinSet :=
  cornerPins 0 D0 ∪ cornerPins 1 D1 ∪ cornerPins 2 D2 ∪ cornerPins 3 D3

/-- The cells of a pin-set at a corner. -/
def cellsAt (c : Fin 4) (T : PinSet) : Finset (ℕ × ℕ) :=
  (T.filter fun a => a.corner = c).image fun a => (a.cellx, a.celly)

theorem mem_cellsAt {c : Fin 4} {T : PinSet} {ij : ℕ × ℕ} :
    ij ∈ cellsAt c T ↔ (⟨c, ij.1, ij.2⟩ : Slot) ∈ T := by
  simp only [cellsAt, Finset.mem_image, Finset.mem_filter]
  constructor
  · rintro ⟨a, ⟨ha, hc⟩, rfl⟩
    obtain ⟨ac, ai, aj⟩ := a
    simp only at hc
    subst hc
    exact ha
  · intro h
    exact ⟨_, ⟨h, rfl⟩, rfl⟩

theorem mem_cornerPins {c : Fin 4} {D : Finset (ℕ × ℕ)} {a : Slot} :
    a ∈ cornerPins c D ↔ a.corner = c ∧ (a.cellx, a.celly) ∈ D := by
  simp only [cornerPins, Finset.mem_image]
  constructor
  · rintro ⟨ij, hij, rfl⟩
    exact ⟨rfl, hij⟩
  · rintro ⟨hc, hij⟩
    obtain ⟨ac, ai, aj⟩ := a
    simp only at hc hij
    subst hc
    exact ⟨_, hij, rfl⟩

theorem assemble_cellsAt (T : PinSet) :
    assemble (cellsAt 0 T) (cellsAt 1 T) (cellsAt 2 T) (cellsAt 3 T) = T := by
  ext a
  simp only [assemble, Finset.mem_union, mem_cornerPins, mem_cellsAt]
  obtain ⟨c, i, j⟩ := a
  simp only
  constructor
  · rintro (((⟨rfl, h⟩ | ⟨rfl, h⟩) | ⟨rfl, h⟩) | ⟨rfl, h⟩) <;> exact h
  · intro h
    fin_cases c
    · exact Or.inl (Or.inl (Or.inl ⟨rfl, h⟩))
    · exact Or.inl (Or.inl (Or.inr ⟨rfl, h⟩))
    · exact Or.inl (Or.inr ⟨rfl, h⟩)
    · exact Or.inr ⟨rfl, h⟩

/-- **B4** A census tuple: a pin-set whose corner diagrams are Young diagrams in the
`3×3` box and whose slots are pairwise far.  NO maximality or realizability filter. -/
def IsCensusTuple (T : PinSet) : Prop :=
  (∀ a ∈ T, a.small) ∧
  (∀ a ∈ T, ∀ i' ≤ a.cellx, ∀ j' ≤ a.celly, (⟨a.corner, i', j'⟩ : Slot) ∈ T) ∧
  (∀ a ∈ T, ∀ b ∈ T, a ≠ b → slotFar a b = true)

instance : DecidablePred IsCensusTuple := fun T =>
  inferInstanceAs (Decidable ((∀ a ∈ T, a.small) ∧
    (∀ a ∈ T, ∀ i' ≤ a.cellx, ∀ j' ≤ a.celly, (⟨a.corner, i', j'⟩ : Slot) ∈ T) ∧
    (∀ a ∈ T, ∀ b ∈ T, a ≠ b → slotFar a b = true)))

/-- The pairwise-far test, Boolean. -/
def pairsFar (T : PinSet) : Bool :=
  decide (∀ a ∈ T, ∀ b ∈ T, a ≠ b → slotFar a b = true)

/-- **The census, as a list**: all assembled 4-tuples of Young diagrams with pairwise-far
slots.  `1110` entries (`CensusCheck.lean`). -/
def censusL : List PinSet :=
  (youngL.flatMap fun D0 => youngL.flatMap fun D1 => youngL.flatMap fun D2 =>
    youngL.map fun D3 => assemble D0 D1 D2 D3).filter pairsFar

/-- The census as a finset. -/
def censusF : Finset PinSet := censusL.toFinset

theorem youngCells_cellsAt {T : PinSet} (hT : IsCensusTuple T) (c : Fin 4) :
    IsYoungCells (cellsAt c T) := by
  intro ij hij i' hi' j' hj'
  rw [mem_cellsAt] at hij ⊢
  exact hT.2.1 _ hij i' hi' j' hj'

theorem cellsAt_subset_box3 {T : PinSet} (hT : IsCensusTuple T) (c : Fin 4) :
    cellsAt c T ⊆ box3 := by
  intro ij hij
  rw [mem_cellsAt] at hij
  have := hT.1 _ hij
  simp only [box3, Finset.mem_product, Finset.mem_range]
  exact this

/-- **Enumeration completeness**: every census tuple is in the list. -/
theorem mem_censusL_of_isCensusTuple {T : PinSet} (hT : IsCensusTuple T) : T ∈ censusL := by
  refine List.mem_filter.mpr ⟨?_, decide_eq_true hT.2.2⟩
  rw [← assemble_cellsAt T]
  simp only [List.mem_flatMap, List.mem_map]
  exact ⟨_, mem_youngL (cellsAt_subset_box3 hT 0) (youngCells_cellsAt hT 0),
    _, mem_youngL (cellsAt_subset_box3 hT 1) (youngCells_cellsAt hT 1),
    _, mem_youngL (cellsAt_subset_box3 hT 2) (youngCells_cellsAt hT 2),
    _, mem_youngL (cellsAt_subset_box3 hT 3) (youngCells_cellsAt hT 3), rfl⟩

theorem mem_censusF_of_isCensusTuple {T : PinSet} (hT : IsCensusTuple T) : T ∈ censusF :=
  List.mem_toFinset.mpr (mem_censusL_of_isCensusTuple hT)

/-! ### The D4 group and its action on slots -/

/-- An element of the container symmetry group `D4`: optionally swap the two centred
coordinates, then optionally negate each.  The eight signed permutation matrices about
the container centre (`d4_reduction_s0.md` R2). -/
structure D4 where
  swap : Bool
  nx : Bool
  ny : Bool
deriving DecidableEq, Repr

/-- The eight elements. -/
def d4List : List D4 :=
  [⟨false, false, false⟩, ⟨false, false, true⟩, ⟨false, true, false⟩, ⟨false, true, true⟩,
   ⟨true, false, false⟩, ⟨true, false, true⟩, ⟨true, true, false⟩, ⟨true, true, true⟩]

theorem mem_d4List (g : D4) : g ∈ d4List := by
  obtain ⟨a, b, c⟩ := g
  cases a <;> cases b <;> cases c <;> decide

/-- The identity. -/
def D4.one : D4 := ⟨false, false, false⟩

/-- Composition `g * h` = "first `h`, then `g`" (as maps).  Derived from the action on
centred coordinates: with `h(d) = (a₂·d_{σ₂1}, b₂·d_{σ₂2})` and `g` swapping iff `σ₁`,
`g(h(d)) = (a₁·[h d]_{σ₁ 1}, b₁·[h d]_{σ₁ 2})`. -/
def D4.mul (g h : D4) : D4 :=
  if g.swap then ⟨!h.swap, xor g.nx h.ny, xor g.ny h.nx⟩
  else ⟨h.swap, xor g.nx h.nx, xor g.ny h.ny⟩

/-- The inverse. -/
def D4.inv (g : D4) : D4 :=
  if g.swap then ⟨true, g.ny, g.nx⟩ else g

/-- Determinant `−1` iff an odd number of the three bits is set. -/
def D4.refl (g : D4) : Bool := xor g.swap (xor g.nx g.ny)

/-- The action on slots (R8): swap exchanges the two inward offsets and the two corner
bits; a sign flip toggles the corresponding corner bit. -/
def d4Slot (g : D4) (a : Slot) : Slot :=
  let r := cornerR a.corner
  let t := cornerT a.corner
  if g.swap then ⟨mkCorner (xor t g.nx) (xor r g.ny), a.celly, a.cellx⟩
  else ⟨mkCorner (xor r g.nx) (xor t g.ny), a.cellx, a.celly⟩

theorem d4Slot_mul (g h : D4) (a : Slot) : d4Slot (g.mul h) a = d4Slot g (d4Slot h a) := by
  obtain ⟨gs, gx, gy⟩ := g
  obtain ⟨hs, hx, hy⟩ := h
  obtain ⟨c, i, j⟩ := a
  cases gs <;> cases gx <;> cases gy <;> cases hs <;> cases hx <;> cases hy <;> fin_cases c <;>
    rfl

theorem d4Slot_one (a : Slot) : d4Slot D4.one a = a := by
  obtain ⟨c, i, j⟩ := a
  fin_cases c <;> rfl

theorem D4.inv_mul (g : D4) : g.inv.mul g = D4.one := by
  obtain ⟨gs, gx, gy⟩ := g
  cases gs <;> cases gx <;> cases gy <;> rfl

theorem D4.mul_inv (g : D4) : g.mul g.inv = D4.one := by
  obtain ⟨gs, gx, gy⟩ := g
  cases gs <;> cases gx <;> cases gy <;> rfl

theorem d4Slot_inv_d4Slot (g : D4) (a : Slot) : d4Slot g.inv (d4Slot g a) = a := by
  rw [← d4Slot_mul, D4.inv_mul, d4Slot_one]

theorem d4Slot_d4Slot_inv (g : D4) (a : Slot) : d4Slot g (d4Slot g.inv a) = a := by
  rw [← d4Slot_mul, D4.mul_inv, d4Slot_one]

theorem d4Slot_injective (g : D4) : Function.Injective (d4Slot g) := by
  intro a b h
  have := congrArg (d4Slot g.inv) h
  rwa [d4Slot_inv_d4Slot, d4Slot_inv_d4Slot] at this

theorem d4Slot_small (g : D4) {a : Slot} (h : a.small) : (d4Slot g a).small := by
  obtain ⟨gs, gx, gy⟩ := g
  obtain ⟨c, i, j⟩ := a
  obtain ⟨hi, hj⟩ := h
  cases gs <;> simp only [d4Slot, Slot.small] <;> exact ⟨by assumption, by assumption⟩

/-- The action on pin-sets. -/
def d4Pins (g : D4) (T : PinSet) : PinSet := T.image (d4Slot g)

theorem mem_d4Pins {g : D4} {T : PinSet} {a : Slot} : a ∈ d4Pins g T ↔ d4Slot g.inv a ∈ T := by
  simp only [d4Pins, Finset.mem_image]
  constructor
  · rintro ⟨b, hb, rfl⟩
    rwa [d4Slot_inv_d4Slot]
  · intro h
    exact ⟨_, h, d4Slot_d4Slot_inv g a⟩

theorem d4Pins_mul (g h : D4) (T : PinSet) : d4Pins (g.mul h) T = d4Pins g (d4Pins h T) := by
  simp only [d4Pins, Finset.image_image]
  congr 1
  funext a
  exact d4Slot_mul g h a

theorem d4Pins_one (T : PinSet) : d4Pins D4.one T = T := by
  simp only [d4Pins]
  conv_rhs => rw [← Finset.image_id (s := T)]
  exact Finset.image_congr (fun a _ => d4Slot_one a)

theorem d4Pins_mono {g : D4} {S T : PinSet} (h : S ⊆ T) : d4Pins g S ⊆ d4Pins g T :=
  Finset.image_subset_image h

/-! ### Canonical representatives and the class list -/

/-- Sorted slot codes of a pin-set: the encoding of `A72` (corner-major, cells by `(i,j)`). -/
def encodePins (T : PinSet) : List ℕ := (T.image Slot.code).sort (· ≤ ·)

/-- Decoding. -/
def decodePins (l : List ℕ) : PinSet := (l.map slotOfCode).toFinset

theorem decode_encode {T : PinSet} (hT : ∀ a ∈ T, a.small) : decodePins (encodePins T) = T := by
  ext a
  simp only [decodePins, encodePins, List.mem_toFinset, List.mem_map, Finset.mem_sort,
    Finset.mem_image]
  constructor
  · rintro ⟨n, ⟨b, hb, rfl⟩, rfl⟩
    rwa [slotOfCode_code b (hT b hb)]
  · intro ha
    exact ⟨a.code, ⟨a, ha, rfl⟩, slotOfCode_code a (hT a ha)⟩

/-- The canonical code of a class: the lexicographic minimum over the eight images
(`A72` convention L4c). -/
def canonCode (T : PinSet) : List ℕ :=
  (d4List.map fun g => encodePins (d4Pins g T)).foldl min (encodePins T)

theorem foldl_min_mem {α : Type*} [LinearOrder α] :
    ∀ (l : List α) (a : α), (l.foldl min a = a ∨ l.foldl min a ∈ l)
  | [], a => Or.inl rfl
  | b :: l, a => by
    simp only [List.foldl_cons, List.mem_cons]
    rcases foldl_min_mem l (min a b) with h | h
    · rw [h]
      rcases min_choice a b with h' | h'
      · exact Or.inl h'
      · exact Or.inr (Or.inl h')
    · exact Or.inr (Or.inr h)

/-- The canonical code is the code of some D4 image. -/
theorem canonCode_eq (T : PinSet) : ∃ g : D4, canonCode T = encodePins (d4Pins g T) := by
  rcases foldl_min_mem (d4List.map fun g => encodePins (d4Pins g T)) (encodePins T) with h | h
  · exact ⟨D4.one, by rw [canonCode, h, d4Pins_one]⟩
  · obtain ⟨g, -, hg⟩ := List.mem_map.mp h
    exact ⟨g, by rw [canonCode, ← hg]⟩

/-- The class representatives: the distinct canonical codes of the census
(`163` of them, `CensusCheck.lean`). -/
def classCodes : List (List ℕ) := (censusL.map canonCode).dedup

/-- The class representative pin-set of index `i`. -/
def classRep (i : Fin classCodes.length) : PinSet := decodePins (classCodes.get i)

/-- **Trump's skeleton** (A53 L3/L4): `(λ_BL, λ_BR, λ_TR, λ_TL) = ((2,1), (1), (1), ∅)`, i.e.
BL cells `{(0,0), (0,1), (1,0)}`, one corner cell at BR and TR, nothing at TL; `k = 5`. -/
def trumpPins : PinSet := assemble {(0, 0), (0, 1), (1, 0)} {(0, 0)} {(0, 0)} ∅

/-- Trump's tuple is a census tuple (kernel `decide`: 5 cells, 20 far-checks). -/
theorem trumpPins_isCensusTuple : IsCensusTuple trumpPins := by decide

/-- `InClassOf skel T`: the skeleton `skel` is a D4-image of `T`. -/
def InClassOf (skel : PinSet) (T : PinSet) : Prop := ∃ g : D4, skel = d4Pins g T

/-- **Every census tuple is in the class of some representative.** -/
theorem exists_classRep {T : PinSet} (hT : IsCensusTuple T) :
    ∃ i : Fin classCodes.length, InClassOf T (classRep i) := by
  obtain ⟨g, hg⟩ := canonCode_eq T
  have hmem : canonCode T ∈ classCodes :=
    List.mem_dedup.mpr (List.mem_map.mpr ⟨T, mem_censusL_of_isCensusTuple hT, rfl⟩)
  obtain ⟨i, hi⟩ := List.mem_iff_get.mp hmem
  refine ⟨i, g.inv, ?_⟩
  have hsmall : ∀ a ∈ d4Pins g T, a.small := by
    intro a ha
    rw [mem_d4Pins] at ha
    have := hT.1 _ ha
    have h2 := d4Slot_small g this
    rwa [d4Slot_d4Slot_inv] at h2
  rw [classRep, hi, hg, decode_encode hsmall, ← d4Pins_mul, D4.inv_mul, d4Pins_one]

/-! ## Part B — geometry: slots at a real side, occupancy, the skeleton of a packing -/

noncomputable section

open scoped Classical

/-- The coordinate of a slot along one axis from its bits: from the far wall (`r`) or
the near wall. -/
def slotX (s : ℝ) (r : Bool) (i : ℕ) : ℝ := if r then s - ((i : ℝ) + 1 / 2) else (i : ℝ) + 1 / 2

theorem slotCentre_eq (s : ℝ) (a : Slot) :
    slotCentre s a = (slotX s (cornerR a.corner) a.cellx, slotX s (cornerT a.corner) a.celly) := by
  obtain ⟨c, i, j⟩ := a
  fin_cases c <;> simp [slotCentre, slotX, cornerR, cornerT]

/-- An integer-valued real strictly between `3` and `4` does not exist. -/
theorem no_nat_between {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) (n : ℕ) : s ≠ (n : ℝ) := by
  intro h
  have h1 : (3 : ℝ) < n := by rw [← h]; exact hs3
  have h2 : (n : ℝ) < 4 := by rw [← h]; exact hs4
  have h1' : 3 < n := by exact_mod_cast h1
  have h2' : n < 4 := by exact_mod_cast h2
  omega

/-- **B2, real form = combinatorial form** at every side `s ∈ (3, 4)`. -/
theorem axisFar_iff {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) (r1 : Bool) (i1 : ℕ) (r2 : Bool)
    (i2 : ℕ) : axisFar r1 i1 r2 i2 = true ↔ 1 ≤ |slotX s r1 i1 - slotX s r2 i2| := by
  have key : ∀ i j : ℕ, i ≠ j ↔ 1 ≤ |(i : ℝ) - (j : ℝ)| := by
    intro i j
    constructor
    · intro hne
      rcases lt_or_gt_of_ne hne with h | h
      · have : (i : ℝ) + 1 ≤ j := by exact_mod_cast h
        rw [le_abs]; right; linarith
      · have : (j : ℝ) + 1 ≤ i := by exact_mod_cast h
        rw [le_abs]; left; linarith
    · intro h hij
      subst hij
      norm_num at h
  have key2 : ∀ i j : ℕ, (i + j ≤ 1 ∨ 4 ≤ i + j) ↔
      1 ≤ |((i : ℝ) + 1 / 2) - (s - ((j : ℝ) + 1 / 2))| := by
    intro i j
    constructor
    · rintro (h | h)
      · have : (i : ℝ) + j ≤ 1 := by exact_mod_cast h
        rw [le_abs]; right; linarith
      · have : (4 : ℝ) ≤ i + j := by exact_mod_cast h
        rw [le_abs]; left; linarith
    · intro h
      rw [le_abs] at h
      rcases h with h | h
      · right
        have : (3 : ℝ) < i + j := by linarith
        have : 3 < i + j := by exact_mod_cast this
        omega
      · left
        have : ((i : ℝ) + j) < 2 := by linarith
        have : i + j < 2 := by exact_mod_cast this
        omega
  cases r1 <;> cases r2 <;> simp only [axisFar, slotX, Bool.false_eq_true, ↓reduceIte,
    decide_eq_true_eq, Bool.true_eq_false]
  · rw [key]; congr! 2; ring
  · rw [key2]
  · rw [add_comm i1 i2, key2, abs_sub_comm]
  · rw [key, abs_sub_comm]; congr! 2; ring

theorem slotFar_iff {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) (a b : Slot) :
    slotFar a b = true ↔
      1 ≤ |(slotCentre s a).1 - (slotCentre s b).1| ∨
        1 ≤ |(slotCentre s a).2 - (slotCentre s b).2| := by
  rw [slotFar, Bool.or_eq_true, axisFar_iff hs3 hs4, axisFar_iff hs3 hs4, slotCentre_eq,
    slotCentre_eq]

/-- **B3** slot centres are distinct for distinct slots at every side `s ∈ (3, 4)`. -/
theorem slotCentre_injective {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) {a b : Slot}
    (h : slotCentre s a = slotCentre s b) : a = b := by
  have hx : ∀ (r1 : Bool) (i1 : ℕ) (r2 : Bool) (i2 : ℕ), slotX s r1 i1 = slotX s r2 i2 →
      r1 = r2 ∧ i1 = i2 := by
    intro r1 i1 r2 i2 h
    cases r1 <;> cases r2 <;> simp only [slotX, Bool.false_eq_true, ↓reduceIte] at h
    · exact ⟨rfl, by exact_mod_cast (show (i1 : ℝ) = i2 by linarith)⟩
    · exact absurd (show s = ((i1 + i2 + 1 : ℕ) : ℝ) by push_cast; linarith)
        (no_nat_between hs3 hs4 _)
    · exact absurd (show s = ((i1 + i2 + 1 : ℕ) : ℝ) by push_cast; linarith)
        (no_nat_between hs3 hs4 _)
    · exact ⟨rfl, by exact_mod_cast (show (i1 : ℝ) = i2 by linarith)⟩
  rw [slotCentre_eq, slotCentre_eq, Prod.mk.injEq] at h
  obtain ⟨hr, hi⟩ := hx _ _ _ _ h.1
  obtain ⟨ht, hj⟩ := hx _ _ _ _ h.2
  obtain ⟨ca, ia, ja⟩ := a
  obtain ⟨cb, ib, jb⟩ := b
  simp only at hr hi ht hj
  subst hi hj
  have : ca = cb := by rw [← mkCorner_bits ca, ← mkCorner_bits cb, hr, ht]
  rw [this]

/-- The axis-aligned closed unit square centred at `c` (the slot box; identical to
`Selection.slotBox`). -/
def slotSet (c : RP) : Set RP :=
  Icc (c.1 - 1 / 2) (c.1 + 1 / 2) ×ˢ Icc (c.2 - 1 / 2) (c.2 + 1 / 2)

theorem mem_slotSet_iff (c p : RP) : p ∈ slotSet c ↔ |p.1 - c.1| ≤ 1 / 2 ∧ |p.2 - c.2| ≤ 1 / 2 := by
  simp only [slotSet, mem_prod, mem_Icc, abs_le]
  constructor
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

theorem mem_interior_slotSet_iff (c p : RP) :
    p ∈ interior (slotSet c) ↔ |p.1 - c.1| < 1 / 2 ∧ |p.2 - c.2| < 1 / 2 := by
  simp only [slotSet, interior_prod_eq, interior_Icc, mem_prod, mem_Ioo, abs_lt]
  constructor
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

theorem occupiesSlot_iff (q : PSq) (c : RP) : OccupiesSlot q c ↔ q.set = slotSet c := Iff.rfl

/-- **B2** (the direction exhaustiveness needs): interior-disjoint slot boxes are far. -/
theorem far_of_interior_disjoint {c d : RP}
    (h : Disjoint (interior (slotSet c)) (interior (slotSet d))) :
    1 ≤ |c.1 - d.1| ∨ 1 ≤ |c.2 - d.2| := by
  by_contra hno
  push Not at hno
  obtain ⟨h1, h2⟩ := hno
  have hm : ((c.1 + d.1) / 2, (c.2 + d.2) / 2) ∈ interior (slotSet c) ∩ interior (slotSet d) := by
    constructor <;> rw [mem_interior_slotSet_iff] <;>
      simp only [abs_lt] at h1 h2 ⊢ <;> constructor <;> constructor <;> linarith
  exact Set.disjoint_left.mp h hm.1 hm.2

/-- A square occupies at most one slot box: the box determines the centre. -/
theorem occupiesSlot_unique {q : PSq} {c d : RP} (hc : OccupiesSlot q c) (hd : OccupiesSlot q d) :
    c = d := by
  rw [occupiesSlot_iff] at hc hd
  have hcorner : ∀ e : RP, (e.1 - 1 / 2, e.2 - 1 / 2) ∈ slotSet e := by
    intro e
    simp only [slotSet, mem_prod, mem_Icc]
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩
  have h1 : (c.1 - 1 / 2, c.2 - 1 / 2) ∈ slotSet d := by
    rw [← hd, hc]; exact hcorner c
  have h2 : (d.1 - 1 / 2, d.2 - 1 / 2) ∈ slotSet c := by
    rw [← hc, hd]; exact hcorner d
  simp only [slotSet, mem_prod, mem_Icc] at h1 h2
  ext <;> linarith [h1.1.1, h2.1.1, h1.2.1, h2.2.1]

/-- A slot box inside the container has its centre in `[½, s − ½]²`. -/
theorem occupiesSlot_centre_bounds {q : PSq} {c : RP} {s : ℝ} (hc : OccupiesSlot q c)
    (hsub : q.set ⊆ container s) :
    1 / 2 ≤ c.1 ∧ c.1 + 1 / 2 ≤ s ∧ 1 / 2 ≤ c.2 ∧ c.2 + 1 / 2 ≤ s := by
  rw [occupiesSlot_iff] at hc
  rw [hc] at hsub
  have h1 : (c.1 - 1 / 2, c.2 - 1 / 2) ∈ container s := hsub (by
    simp only [slotSet, mem_prod, mem_Icc]
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩)
  have h2 : (c.1 + 1 / 2, c.2 + 1 / 2) ∈ container s := hsub (by
    simp only [slotSet, mem_prod, mem_Icc]
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩)
  simp only [container, mem_prod, mem_Icc] at h1 h2
  exact ⟨by linarith [h1.1.1], by linarith [h2.1.2], by linarith [h1.2.1], by linarith [h2.2.2]⟩

/-- Slot `a` is occupied by some square of `z` at side `s`. -/
def Occupied (s : ℝ) (z : Fin 11 → PSq) (a : Slot) : Prop :=
  ∃ k, OccupiesSlot (z k) (slotCentre s a)

/-- **The skeleton cell predicate (A53 L1, Young form):** cell `a` of its corner is a
skeleton cell iff its whole down-set (inside that corner, B5) is occupied by squares of
the packing sitting exactly on the corner grid.  The set of such cells at a corner is
the largest Young diagram of occupied cells — `S_c(P)` of L1. -/
def IsSkelCell (s : ℝ) (z : Fin 11 → PSq) (a : Slot) : Prop :=
  ∀ i' ≤ a.cellx, ∀ j' ≤ a.celly, Occupied s z ⟨a.corner, i', j'⟩

/-- **The skeleton of a packing**, `Simp(P)` as a pin-set: the skeleton cells among the
36 small slots (B1: no other slot can be occupied when `s < 4`, `skelCell_small`). -/
def skeleton (s : ℝ) (z : Fin 11 → PSq) : PinSet :=
  allSlots.toFinset.filter fun a => IsSkelCell s z a

theorem mem_skeleton {s : ℝ} {z : Fin 11 → PSq} {a : Slot} :
    a ∈ skeleton s z ↔ a.small ∧ IsSkelCell s z a := by
  simp only [skeleton, Finset.mem_filter, List.mem_toFinset]
  exact and_congr_left fun _ => ⟨small_of_mem_allSlots, mem_allSlots_of_small⟩

theorem occupied_self {s : ℝ} {z : Fin 11 → PSq} {a : Slot} (h : IsSkelCell s z a) :
    Occupied s z a :=
  h a.cellx le_rfl a.celly le_rfl

/-- **B1 (derived):** at `s < 4` an occupied slot has both offsets `< 3`. -/
theorem occupied_small {s : ℝ} (hs4 : s < 4) {z : Fin 11 → PSq}
    (hP : IsPacking 11 s fun i => (z i).set) {a : Slot} (h : Occupied s z a) : a.small := by
  obtain ⟨k, hk⟩ := h
  obtain ⟨h1, h2, h3, h4⟩ := occupiesSlot_centre_bounds hk (hP.contained k)
  rw [slotCentre_eq] at h1 h2 h3 h4
  simp only at h1 h2 h3 h4
  generalize cornerR a.corner = r at h1 h2
  generalize cornerT a.corner = t at h3 h4
  constructor
  · by_contra hx
    push Not at hx
    have hx' : (3 : ℝ) ≤ a.cellx := by exact_mod_cast hx
    cases r <;> simp only [slotX, Bool.false_eq_true, ↓reduceIte] at h1 h2 <;> linarith
  · by_contra hy
    push Not at hy
    have hy' : (3 : ℝ) ≤ a.celly := by exact_mod_cast hy
    cases t <;> simp only [slotX, Bool.false_eq_true, ↓reduceIte] at h3 h4 <;> linarith

theorem skelCell_small {s : ℝ} (hs4 : s < 4) {z : Fin 11 → PSq}
    (hP : IsPacking 11 s fun i => (z i).set) {a : Slot} (h : IsSkelCell s z a) : a.small :=
  occupied_small hs4 hP (occupied_self h)

/-- At `s < 4` the skeleton is exactly the set of ALL skeleton cells (nothing is cut off
by the `3×3` enumeration box). -/
theorem mem_skeleton_iff {s : ℝ} (hs4 : s < 4) {z : Fin 11 → PSq}
    (hP : IsPacking 11 s fun i => (z i).set) {a : Slot} :
    a ∈ skeleton s z ↔ IsSkelCell s z a :=
  mem_skeleton.trans ⟨fun h => h.2, fun h => ⟨skelCell_small hs4 hP h, h⟩⟩

/-- Two skeleton slots occupied by the same square coincide. -/
theorem slot_eq_of_same_square {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) {q : PSq} {a b : Slot}
    (ha : OccupiesSlot q (slotCentre s a)) (hb : OccupiesSlot q (slotCentre s b)) : a = b :=
  slotCentre_injective hs3 hs4 (occupiesSlot_unique ha hb)

/-- **Exhaustiveness, structural half (A53 L3):** the skeleton of a packing at any side
`s ∈ (3, 4)` is a census tuple. -/
theorem isCensusTuple_skeleton {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) {z : Fin 11 → PSq}
    (hP : IsPacking 11 s fun i => (z i).set) : IsCensusTuple (skeleton s z) := by
  refine ⟨fun a ha => (mem_skeleton.mp ha).1, ?_, ?_⟩
  · intro a ha i' hi' j' hj'
    rw [mem_skeleton_iff hs4 hP] at ha ⊢
    intro i'' hi'' j'' hj''
    exact ha i'' (le_trans hi'' hi') j'' (le_trans hj'' hj')
  · intro a ha b hb hab
    rw [mem_skeleton_iff hs4 hP] at ha hb
    obtain ⟨k, hk⟩ := occupied_self ha
    obtain ⟨l, hl⟩ := occupied_self hb
    have hkl : k ≠ l := by
      rintro rfl
      exact hab (slot_eq_of_same_square hs3 hs4 hk hl)
    have hd := hP.interiorDisjoint k l hkl
    rw [occupiesSlot_iff] at hk hl
    rw [hk, hl] at hd
    rw [slotFar_iff hs3 hs4]
    exact far_of_interior_disjoint hd

/-- **A53 L3 — census exhaustiveness as a theorem about packings:** every packing at any
side `s ∈ (3, 4)` has its skeleton in the census. -/
theorem skeleton_mem_census {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) {z : Fin 11 → PSq}
    (hP : IsPacking 11 s fun i => (z i).set) : skeleton s z ∈ censusF :=
  mem_censusF_of_isCensusTuple (isCensusTuple_skeleton hs3 hs4 hP)

/-- Every packing lies in the class of some representative. -/
theorem exists_class_skeleton {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) {z : Fin 11 → PSq}
    (hP : IsPacking 11 s fun i => (z i).set) :
    ∃ i : Fin classCodes.length, InClassOf (skeleton s z) (classRep i) :=
  exists_classRep (isCensusTuple_skeleton hs3 hs4 hP)

/-- An occupier of each skeleton slot (classical choice; `0` off the skeleton). -/
def occupier (s : ℝ) (z : Fin 11 → PSq) (a : Slot) : Fin 11 :=
  if h : Occupied s z a then Classical.choose h else 0

theorem occupier_spec {s : ℝ} {z : Fin 11 → PSq} {a : Slot} (h : Occupied s z a) :
    OccupiesSlot (z (occupier s z a)) (slotCentre s a) := by
  rw [occupier, dif_pos h]
  exact Classical.choose_spec h

/-- **`hface`, discharged (Skeleton.lean's census interface): exact ⟹ contains.**  A
packing's skeleton is contained in the packing — reflexivity of the slot assignment,
injective on the skeleton at every side `s ∈ (3, 4)` (B3). -/
theorem containsPins_skeleton {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) {z : Fin 11 → PSq} :
    ContainsPins (skeleton s z) s z := by
  refine ⟨occupier s z, ?_, ?_⟩
  · intro a ha b hb hab
    have ha' := occupier_spec (occupied_self (mem_skeleton.mp ha).2)
    have hb' := occupier_spec (occupied_self (mem_skeleton.mp hb).2)
    rw [hab] at ha'
    exact slot_eq_of_same_square hs3 hs4 ha' hb'
  · intro a ha
    exact occupier_spec (occupied_self (mem_skeleton.mp ha).2)

/-- **B6 (a theorem, not a cap):** `k = |Simp(P)| ≤ 11`. -/
theorem skeleton_card_le {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) (z : Fin 11 → PSq) :
    (skeleton s z).card ≤ 11 := by
  obtain ⟨f, hinj, -⟩ := containsPins_skeleton (z := z) hs3 hs4
  have := Finset.card_le_card_of_injOn f (fun a _ => Finset.mem_univ (f a)) hinj
  simpa using this

/-! ## Part C — the D4 action on the plane, on squares, on configurations -/

/-- Sign of a bit. -/
def sg (b : Bool) : ℝ := if b then -1 else 1

/-- **B8** The D4 action on plane points about the container centre `(s/2, s/2)`. -/
def d4Apply (s : ℝ) (g : D4) (p : RP) : RP :=
  if g.swap then (s / 2 + sg g.nx * (p.2 - s / 2), s / 2 + sg g.ny * (p.1 - s / 2))
  else (s / 2 + sg g.nx * (p.1 - s / 2), s / 2 + sg g.ny * (p.2 - s / 2))

theorem d4Apply_mul (s : ℝ) (g h : D4) (p : RP) :
    d4Apply s (g.mul h) p = d4Apply s g (d4Apply s h p) := by
  obtain ⟨gs, gx, gy⟩ := g
  obtain ⟨hs, hx, hy⟩ := h
  cases gs <;> cases gx <;> cases gy <;> cases hs <;> cases hx <;> cases hy <;>
    refine Prod.ext ?_ ?_ <;> simp [D4.mul, d4Apply, sg]

theorem d4Apply_one (s : ℝ) (p : RP) : d4Apply s D4.one p = p := by
  simp [d4Apply, D4.one, sg]

theorem d4Apply_inv_apply (s : ℝ) (g : D4) (p : RP) :
    d4Apply s g.inv (d4Apply s g p) = p := by
  rw [← d4Apply_mul, D4.inv_mul, d4Apply_one]

theorem d4Apply_apply_inv (s : ℝ) (g : D4) (p : RP) :
    d4Apply s g (d4Apply s g.inv p) = p := by
  rw [← d4Apply_mul, D4.mul_inv, d4Apply_one]

theorem d4Apply_image_eq_preimage (s : ℝ) (g : D4) (A : Set RP) :
    d4Apply s g '' A = d4Apply s g.inv ⁻¹' A :=
  congrFun (Set.image_eq_preimage_of_inverse (d4Apply_inv_apply s g)
    (d4Apply_apply_inv s g)) A

/-- **R8 as a theorem:** the plane action sends slot centres to slot centres, by the
slot action `d4Slot` (`λ` or `λᵀ`). -/
theorem d4Apply_slotCentre (s : ℝ) (g : D4) (a : Slot) :
    d4Apply s g (slotCentre s a) = slotCentre s (d4Slot g a) := by
  obtain ⟨gs, gx, gy⟩ := g
  rw [slotCentre_eq, slotCentre_eq]
  simp only [d4Slot]
  generalize cornerR a.corner = r
  generalize cornerT a.corner = t
  cases gs <;> cases gx <;> cases gy <;> cases r <;> cases t <;>
    simp only [d4Apply, slotX, sg, mkCorner_cornerR, mkCorner_cornerT, Bool.false_eq_true,
      ↓reduceIte, Bool.xor_false, Bool.xor_true, Bool.false_xor,
      Bool.true_xor, Bool.not_false, Bool.not_true, Prod.mk.injEq] <;> constructor <;> ring

theorem d4Apply_sqdist (s : ℝ) (g : D4) (p q : RP) :
    sqdist (d4Apply s g p) (d4Apply s g q) = sqdist p q := by
  obtain ⟨gs, gx, gy⟩ := g
  cases gs <;> cases gx <;> cases gy <;>
    simp only [d4Apply, sqdist, sg, Bool.false_eq_true, ↓reduceIte] <;> ring

theorem d4Apply_mem_container (s : ℝ) (g : D4) (p : RP) :
    d4Apply s g p ∈ container s ↔ p ∈ container s := by
  obtain ⟨gs, gx, gy⟩ := g
  cases gs <;> cases gx <;> cases gy <;>
    simp only [d4Apply, container, sg, mem_prod, mem_Icc, Bool.false_eq_true, ↓reduceIte] <;>
    constructor <;> rintro ⟨⟨h1, h2⟩, h3, h4⟩ <;> refine ⟨⟨?_, ?_⟩, ?_, ?_⟩ <;> linarith

theorem d4Apply_image_container (s : ℝ) (g : D4) :
    d4Apply s g '' container s = container s := by
  rw [d4Apply_image_eq_preimage]
  ext p
  simp only [mem_preimage]
  rw [d4Apply_mem_container]

/-- Tilt transport under a reflection: `θ ↦ 90° − θ`, i.e. `t ↦ (1 − t)/(1 + t)`. -/
def tRefl (t : ℝ) : ℝ := (1 - t) / (1 + t)

theorem cosT_tRefl {t : ℝ} (ht : 0 ≤ t) : cosT (tRefl t) = sinT t := by
  have h1 : (1 + t : ℝ) ≠ 0 := by positivity
  have h2 : (1 + t ^ 2 : ℝ) ≠ 0 := by positivity
  unfold cosT sinT tRefl
  field_simp
  ring

theorem sinT_tRefl {t : ℝ} (ht : 0 ≤ t) : sinT (tRefl t) = cosT t := by
  have h1 : (1 + t : ℝ) ≠ 0 := by positivity
  have h2 : (1 + t ^ 2 : ℝ) ≠ 0 := by positivity
  unfold cosT sinT tRefl
  field_simp
  ring

theorem tRefl_mem_Icc {t : ℝ} (ht : t ∈ Icc (0 : ℝ) 1) : tRefl t ∈ Icc (0 : ℝ) 1 := by
  obtain ⟨h0, h1⟩ := ht
  have hp : (0 : ℝ) < 1 + t := by linarith
  constructor
  · exact div_nonneg (by linarith) hp.le
  · rw [tRefl, div_le_one hp]; linarith

/-- **R5** The D4 action on parametrised squares: centre moved, tilt reflected iff the
element has determinant `−1`. -/
def d4Sq (s : ℝ) (g : D4) (q : PSq) : PSq :=
  ⟨(d4Apply s g (q.cx, q.cy)).1, (d4Apply s g (q.cx, q.cy)).2,
    if g.refl then tRefl q.t else q.t⟩

theorem d4Sq_t_mem {s : ℝ} (g : D4) {q : PSq} (hq : q.t ∈ Icc (0 : ℝ) 1) :
    (d4Sq s g q).t ∈ Icc (0 : ℝ) 1 := by
  simp only [d4Sq]
  split_ifs
  · exact tRefl_mem_Icc hq
  · exact hq

/-- Abs-transport lemma: two coordinate pairs with the same multiset of absolute values
satisfy the same box conditions. -/
theorem box_iff_of_abs {a b a' b' r : ℝ}
    (h : (|a'| = |a| ∧ |b'| = |b|) ∨ (|a'| = |b| ∧ |b'| = |a|)) :
    (|a'| ≤ r ∧ |b'| ≤ r ↔ |a| ≤ r ∧ |b| ≤ r) ∧
      (|a'| < r ∧ |b'| < r ↔ |a| < r ∧ |b| < r) := by
  rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩ <;> rw [h1, h2]
  · exact ⟨Iff.rfl, Iff.rfl⟩
  · exact ⟨and_comm, and_comm⟩

/-- The `u/v` coordinates of `p` w.r.t. the transformed square are (up to sign and
order) the `u/v` coordinates of `g⁻¹ p` w.r.t. the original square. -/
theorem d4Sq_uv (s : ℝ) (g : D4) {q : PSq} (hq : 0 ≤ q.t) (p : RP) :
    (|rdot (p.1 - (d4Sq s g q).cx, p.2 - (d4Sq s g q).cy) (edir (d4Sq s g q))| =
        |rdot ((d4Apply s g.inv p).1 - q.cx, (d4Apply s g.inv p).2 - q.cy) (edir q)| ∧
      |rdot (p.1 - (d4Sq s g q).cx, p.2 - (d4Sq s g q).cy) (perpV (edir (d4Sq s g q)))| =
        |rdot ((d4Apply s g.inv p).1 - q.cx, (d4Apply s g.inv p).2 - q.cy)
          (perpV (edir q))|) ∨
    (|rdot (p.1 - (d4Sq s g q).cx, p.2 - (d4Sq s g q).cy) (edir (d4Sq s g q))| =
        |rdot ((d4Apply s g.inv p).1 - q.cx, (d4Apply s g.inv p).2 - q.cy)
          (perpV (edir q))| ∧
      |rdot (p.1 - (d4Sq s g q).cx, p.2 - (d4Sq s g q).cy) (perpV (edir (d4Sq s g q)))| =
        |rdot ((d4Apply s g.inv p).1 - q.cx, (d4Apply s g.inv p).2 - q.cy) (edir q)|) := by
  obtain ⟨gs, gx, gy⟩ := g
  cases gs <;> cases gx <;> cases gy <;>
    simp only [d4Sq, d4Apply, D4.inv, D4.refl, edir, perpV, rdot, sg, Bool.false_eq_true,
      ↓reduceIte, Bool.xor_false, Bool.xor_true, Bool.false_xor,
      Bool.true_xor, Bool.not_false, Bool.not_true, cosT_tRefl hq, sinT_tRefl hq] <;>
    first
    | (left; constructor <;> rw [abs_eq_abs] <;> first | (left; ring1) | (right; ring1))
    | (right; constructor <;> rw [abs_eq_abs] <;> first | (left; ring1) | (right; ring1))

theorem mem_d4Sq_set_iff {s : ℝ} (g : D4) {q : PSq} (hq : 0 ≤ q.t) (p : RP) :
    p ∈ (d4Sq s g q).set ↔ d4Apply s g.inv p ∈ q.set := by
  rw [mem_set_iff_uv, mem_set_iff_uv]
  exact (box_iff_of_abs (d4Sq_uv s g hq p)).1

theorem mem_interior_d4Sq_set_iff {s : ℝ} (g : D4) {q : PSq} (hq : 0 ≤ q.t) (p : RP) :
    p ∈ interior (d4Sq s g q).set ↔ d4Apply s g.inv p ∈ interior q.set := by
  rw [mem_interior_iff_uv, mem_interior_iff_uv]
  exact (box_iff_of_abs (d4Sq_uv s g hq p)).2

theorem d4Sq_set_eq_preimage {s : ℝ} (g : D4) {q : PSq} (hq : 0 ≤ q.t) :
    (d4Sq s g q).set = d4Apply s g.inv ⁻¹' q.set := by
  ext p
  exact mem_d4Sq_set_iff g hq p

/-- **R5, set form:** the transformed square is the image of the square. -/
theorem d4Sq_set {s : ℝ} (g : D4) {q : PSq} (hq : 0 ≤ q.t) :
    (d4Sq s g q).set = d4Apply s g '' q.set := by
  rw [d4Sq_set_eq_preimage g hq, d4Apply_image_eq_preimage]

theorem interior_d4Sq_set {s : ℝ} (g : D4) {q : PSq} (hq : 0 ≤ q.t) :
    interior (d4Sq s g q).set = d4Apply s g.inv ⁻¹' interior q.set := by
  ext p
  exact mem_interior_d4Sq_set_iff g hq p

/-- The D4 action on configurations. -/
def d4Cfg (s : ℝ) (g : D4) (z : Fin 11 → PSq) : Fin 11 → PSq := fun k => d4Sq s g (z k)

/-- **The D4 action preserves packings at the same side** (E.2's "preserves the packing
property and side"). -/
theorem d4_packing {s : ℝ} (g : D4) {z : Fin 11 → PSq} (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (hP : IsPacking 11 s fun i => (z i).set) :
    (∀ i, (d4Cfg s g z i).t ∈ Icc (0 : ℝ) 1) ∧
      IsPacking 11 s fun i => (d4Cfg s g z i).set := by
  refine ⟨fun i => d4Sq_t_mem g (ht i), ?_⟩
  refine ⟨fun i => psq_isUnitSquare _, ?_, ?_⟩
  · intro i p hp
    rw [d4Cfg, mem_d4Sq_set_iff g (ht i).1] at hp
    have := hP.contained i hp
    rwa [d4Apply_mem_container] at this
  · intro i j hij
    simp only [d4Cfg]
    rw [interior_d4Sq_set g (ht i).1, interior_d4Sq_set g (ht j).1]
    exact (hP.interiorDisjoint i j hij).preimage _

/-- The set-level relabelling `(g·z) j = g '' (z j)`. -/
theorem d4Cfg_set {s : ℝ} (g : D4) {z : Fin 11 → PSq} (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (j : Fin 11) : (d4Cfg s g z j).set = d4Apply s g '' (z j).set :=
  d4Sq_set g (ht j).1

/-! ### Skeleton equivariance -/

theorem slotSet_d4 (s : ℝ) (g : D4) (c : RP) :
    slotSet (d4Apply s g c) = d4Apply s g.inv ⁻¹' slotSet c := by
  ext p
  simp only [mem_preimage]
  rw [mem_slotSet_iff, mem_slotSet_iff]
  refine (box_iff_of_abs ?_).1
  obtain ⟨gs, gx, gy⟩ := g
  cases gs <;> cases gx <;> cases gy <;>
    simp only [d4Apply, D4.inv, sg, Bool.false_eq_true, ↓reduceIte] <;>
    first
    | (left; constructor <;> rw [abs_eq_abs] <;> first | (left; ring1) | (right; ring1))
    | (right; constructor <;> rw [abs_eq_abs] <;> first | (left; ring1) | (right; ring1))

theorem occupiesSlot_d4 {s : ℝ} (g : D4) {q : PSq} (hq : 0 ≤ q.t) (c : RP) :
    OccupiesSlot (d4Sq s g q) (d4Apply s g c) ↔ OccupiesSlot q c := by
  rw [occupiesSlot_iff, occupiesSlot_iff, d4Sq_set_eq_preimage g hq, slotSet_d4]
  constructor
  · intro h
    exact Set.preimage_injective.mpr (fun p => ⟨d4Apply s g p, d4Apply_inv_apply s g p⟩) h
  · intro h
    rw [h]

theorem occupied_d4 {s : ℝ} (g : D4) {z : Fin 11 → PSq} (ht : ∀ i, 0 ≤ (z i).t) (a : Slot) :
    Occupied s (d4Cfg s g z) (d4Slot g a) ↔ Occupied s z a := by
  simp only [Occupied, d4Cfg]
  rw [← d4Apply_slotCentre]
  exact exists_congr fun k => occupiesSlot_d4 g (ht k) _

theorem isSkelCell_d4 {s : ℝ} (g : D4) {z : Fin 11 → PSq} (ht : ∀ i, 0 ≤ (z i).t) (a : Slot) :
    IsSkelCell s (d4Cfg s g z) (d4Slot g a) ↔ IsSkelCell s z a := by
  obtain ⟨c, i, j⟩ := a
  obtain ⟨gs, gx, gy⟩ := g
  cases gs
  · have hc : ∀ i' j', d4Slot ⟨false, gx, gy⟩ ⟨c, i', j'⟩
        = ⟨mkCorner (xor (cornerR c) gx) (xor (cornerT c) gy), i', j'⟩ := fun i' j' => rfl
    rw [hc]
    simp only [IsSkelCell]
    refine forall_congr' fun i' => imp_congr_right fun _ => forall_congr' fun j' =>
      imp_congr_right fun _ => ?_
    rw [← hc i' j', occupied_d4 _ ht]
  · have hc : ∀ i' j', d4Slot ⟨true, gx, gy⟩ ⟨c, i', j'⟩
        = ⟨mkCorner (xor (cornerT c) gx) (xor (cornerR c) gy), j', i'⟩ := fun i' j' => rfl
    rw [hc]
    simp only [IsSkelCell]
    constructor
    · intro h i' hi' j' hj'
      have := h j' hj' i' hi'
      rwa [← hc i' j', occupied_d4 _ ht] at this
    · intro h j' hj' i' hi'
      rw [← hc i' j', occupied_d4 _ ht]
      exact h i' hi' j' hj'

/-- **Skeleton equivariance (E.2's D4 bookkeeping, machine-checked):**
`Simp(g·P) = g·Simp(P)`. -/
theorem skeleton_d4 {s : ℝ} (g : D4) {z : Fin 11 → PSq} (ht : ∀ i, 0 ≤ (z i).t) :
    skeleton s (d4Cfg s g z) = d4Pins g (skeleton s z) := by
  ext a
  rw [mem_d4Pins, mem_skeleton, mem_skeleton]
  have hsm : a.small ↔ (d4Slot g.inv a).small :=
    ⟨d4Slot_small g.inv, fun h => by
      have := d4Slot_small g h
      rwa [d4Slot_d4Slot_inv] at this⟩
  rw [hsm]
  refine and_congr Iff.rfl ?_
  conv_lhs => rw [← d4Slot_d4Slot_inv g a]
  exact isSkelCell_d4 g ht _

/-! ## Part D — Lemma M→E (E.2): a monotone kill of `S ≤ g·T` empties the class of `T` -/

theorem D4.mul_inv_mul (g g' : D4) : (g.mul g'.inv).mul g' = g := by
  obtain ⟨a, b, c⟩ := g
  obtain ⟨a', b', c'⟩ := g'
  cases a <;> cases b <;> cases c <;> cases a' <;> cases b' <;> cases c' <;> rfl

/-- **Lemma M→E (`instratum_bridge.md` E.2), fully formal.**  If some pin-set `S`
contained in a D4-image of the class tuple `T` carries a monotone kill at side `s`
(no packing at `s` contains `S`), then no packing at side `s ∈ (3, 4)` has skeleton in the
class of `T`.  Proof: normalise the packing by `h = g·g'⁻¹` (`d4_packing`,
`skeleton_d4`), then `containsPins_skeleton` + K1(i). -/
theorem class_kill {s : ℝ} (hs3 : 3 < s) (hs4 : s < 4) (T S : PinSet) (g : D4)
    (hS : S ⊆ d4Pins g T)
    (kill : ∀ z : Fin 11 → PSq, (∀ i, (z i).t ∈ Icc (0 : ℝ) 1) →
      IsPacking 11 s (fun i => (z i).set) → ¬ContainsPins S s z) :
    ∀ z : Fin 11 → PSq, (∀ i, (z i).t ∈ Icc (0 : ℝ) 1) →
      IsPacking 11 s (fun i => (z i).set) → ¬InClassOf (skeleton s z) T := by
  intro z ht hP hcls
  obtain ⟨g', hg'⟩ := hcls
  obtain ⟨ht', hP'⟩ := d4_packing (g.mul g'.inv) ht hP
  have hskel : skeleton s (d4Cfg s (g.mul g'.inv) z) = d4Pins g T := by
    rw [skeleton_d4 _ (fun i => (ht i).1), hg', ← d4Pins_mul, D4.mul_inv_mul]
  refine kill _ ht' hP' ?_
  refine containsPins_mono (hskel ▸ hS) ?_
  exact containsPins_skeleton hs3 hs4

end

end S11
end PackingCert
