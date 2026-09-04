import PackingCertMathlib.Slide

/-!
# Lemma SWEEP and the pinned joint translation (A94 `slot_crowds.md` §3.1–3.2; A93 T2 addendum)

The slot version of Lemma SLIDE (SLOT-SLIDE, for the pinned classes) moves the non-pin squares
away from a corner while the container grows at that corner's far walls and the PIN BLOCKS
(the Young diagrams of pins at the four corners) translate rigidly with their anchoring walls.
The only new geometry is **Lemma SWEEP**: a Young block never obstructs a motion away from its
own walls — an interior point of a moving object that lands in an open cell of the block would,
before the move, have been in a (closed) cell of the block with smaller indices, which the
down-set contains (`sweep_core`, a floor-function argument).

* `IsYoung` — a finite set of cells `(i, j)` closed downward; `pinCells S c'` the cells of the
  pin set `S` at corner `c'`;
* `pinVec c' τ` — the displacement of corner `c'`'s block: `τ` along each axis whose far wall
  (`x = s` if `c'` is a right corner, `y = s` if a top corner) recedes; `shiftVec c τ` (`Slide.lean`)
  is the displacement of the non-pins; `pinnedShift` moves every square accordingly;
* `interior_notMem_slotBox_of_disjoint` — an interior point of a set interior-disjoint from a
  closed unit cell lies outside the CLOSED cell (the `ε`-ball perturbation);
* `sweep_packing` — SWEEP applied to a square of the packing that is not a pin of corner `c'`,
  moved relative to the block by a vector that points away from `c'`'s walls;
* `pinnedShift_packing` — **Lemma MOVE without clusters**: for every `τ ≥ 0` the pinned shift
  is a packing at side `m + τ` that still contains the pins of `S` (each block exactly at its
  slots of the grown container).  Every pair is either rigid (same displacement), a SWEEP pair
  (a square vs a block whose relative motion points away from the block's walls), or two blocks
  (again a SWEEP pair, the other block being interior-disjoint from every cell of the first).

The composition with SLOT-CROWD (the teleport at the landing side, Lemma CONT) is the named
obligation `slot_slide` (see the A93 findings): it needs the clip census of the class
(`unclipped`: no pin meets the interior of the slot box at any window side) and the slot-frame
version of `shift_meets_cornerBox`, both class-specific data of A94.

Axioms: `propext, Classical.choice, Quot.sound`.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-! ## Young blocks and the pin displacement -/

/-- A finite set of cells closed downward (a Young diagram at a corner). -/
def IsYoung (D : Finset (ℕ × ℕ)) : Prop :=
  ∀ x ∈ D, ∀ i j : ℕ, i ≤ x.1 → j ≤ x.2 → (i, j) ∈ D

/-- The cells of the pin set `S` at corner `c'`. -/
def pinCells (S : PinSet) (c' : Fin 4) : Finset (ℕ × ℕ) :=
  (S.filter fun a => a.corner = c').image fun a => (a.cellx, a.celly)

/-- The displacement of corner `c'`'s pin block when the container grows from `[0,s]²` to
`[0, s+τ]²`: the block moves with its anchoring walls. -/
def pinVec (c' : Fin 4) (τ : ℝ) : RP := (if cornerR c' then τ else 0, if cornerT c' then τ else 0)

/-- The displacement of square `i`: its block's if it is a pin (`pc i = some c'`), the outward
shift of corner `c` otherwise. -/
def disp (c : Fin 4) (τ : ℝ) (pc : Fin 11 → Option (Fin 4)) (i : Fin 11) : RP :=
  match pc i with
  | some c' => pinVec c' τ
  | none => shiftVec c τ

/-- The pinned joint translation. -/
def pinnedShift (c : Fin 4) (τ : ℝ) (pc : Fin 11 → Option (Fin 4)) (z : Cfg) : Cfg :=
  fun i => shiftSq (disp c τ pc i) (z i)

/-- The pin data of a configuration: an injective slot assignment `f`, the pin-corner map `pc`
(`some c'` exactly on the pins of corner `c'`), and the Young property at every corner. -/
structure PinData (S : PinSet) (z : Cfg) (m : ℝ) where
  f : Slot → Fin 11
  pc : Fin 11 → Option (Fin 4)
  inj : Set.InjOn f ↑S
  occ : ∀ a ∈ S, OccupiesSlot (z (f a)) (slotCentre m a)
  pc_pin : ∀ a ∈ S, pc (f a) = some a.corner
  pc_some : ∀ i c', pc i = some c' → ∃ a ∈ S, f a = i ∧ a.corner = c'
  young : ∀ c', IsYoung (pinCells S c')

theorem PinData.containsPins {S : PinSet} {z : Cfg} {m : ℝ} (P : PinData S z m) :
    ContainsPins S m z := ⟨P.f, P.inj, P.occ⟩

/-! ## Cells in the corner frame -/

/-- The closed slot box of `a` at side `s`, in the frame of its corner: `[i, i+1] × [j, j+1]`. -/
theorem mem_slotBox_iff_cframe (s : ℝ) (a : Slot) (p : RP) :
    p ∈ slotBox (slotCentre s a) ↔
      (a.cellx : ℝ) ≤ (cframe s a.corner p).1 ∧ (cframe s a.corner p).1 ≤ a.cellx + 1 ∧
      (a.celly : ℝ) ≤ (cframe s a.corner p).2 ∧ (cframe s a.corner p).2 ≤ a.celly + 1 := by
  rw [slotCentre_affine]
  simp only [slotBox, slotAX, slotBX, slotAY, slotBY, cframe, mem_prod, mem_Icc]
  split_ifs <;> constructor <;> intro h <;> simp only [and_assoc] at h ⊢ <;>
    obtain ⟨h1, h2, h3, h4⟩ := h <;> exact ⟨by linarith, by linarith, by linarith, by linarith⟩

theorem interior_slotBox (c : RP) :
    interior (slotBox c) = Ioo (c.1 - 1 / 2) (c.1 + 1 / 2) ×ˢ Ioo (c.2 - 1 / 2) (c.2 + 1 / 2) := by
  rw [slotBox, interior_prod_eq, interior_Icc, interior_Icc]

theorem mem_interior_slotBox_iff_cframe (s : ℝ) (a : Slot) (p : RP) :
    p ∈ interior (slotBox (slotCentre s a)) ↔
      (a.cellx : ℝ) < (cframe s a.corner p).1 ∧ (cframe s a.corner p).1 < a.cellx + 1 ∧
      (a.celly : ℝ) < (cframe s a.corner p).2 ∧ (cframe s a.corner p).2 < a.celly + 1 := by
  rw [interior_slotBox, slotCentre_affine]
  simp only [slotAX, slotBX, slotAY, slotBY, cframe, mem_prod, mem_Ioo]
  split_ifs <;> constructor <;> intro h <;> simp only [and_assoc] at h ⊢ <;>
    obtain ⟨h1, h2, h3, h4⟩ := h <;> exact ⟨by linarith, by linarith, by linarith, by linarith⟩

/-- The frame image of a container displacement: `(±w.1, ±w.2)` with the corner's signs. -/
theorem cframe_add (s : ℝ) (c' : Fin 4) (p w : RP) :
    cframe s c' (p.1 + w.1, p.2 + w.2)
      = ((cframe s c' p).1 + (if cornerR c' then -w.1 else w.1),
         (cframe s c' p).2 + (if cornerT c' then -w.2 else w.2)) := by
  simp only [cframe]
  split_ifs <;> ext <;> simp <;> ring

/-- An interior point of a set interior-disjoint from a closed unit cell is not in the closed
cell: a small push toward the cell's centre stays in the interior of the set and enters the open
cell. -/
theorem interior_notMem_slotBox_of_disjoint {X : Set RP} {c : RP}
    (hd : Disjoint (interior X) (interior (slotBox c))) {q : RP} (hq : q ∈ interior X) :
    q ∉ slotBox c := by
  intro hqc
  obtain ⟨ε, hε, hball⟩ := Metric.isOpen_iff.mp isOpen_interior q hq
  set δ : ℝ := min (ε / 2) (1 / 4) with hδ
  have hδ0 : 0 < δ := lt_min (by linarith) (by norm_num)
  have hδε : δ ≤ ε / 2 := min_le_left _ _
  have hδ4 : δ ≤ 1 / 4 := min_le_right _ _
  simp only [slotBox, mem_prod, mem_Icc] at hqc
  obtain ⟨⟨h1, h2⟩, h3, h4⟩ := hqc
  set d1 : ℝ := if q.1 < c.1 then δ else -δ with hd1
  set d2 : ℝ := if q.2 < c.2 then δ else -δ with hd2
  have habs1 : |d1| ≤ δ := by
    rw [hd1]; split_ifs <;> simp [abs_of_pos hδ0, abs_neg]
  have habs2 : |d2| ≤ δ := by
    rw [hd2]; split_ifs <;> simp [abs_of_pos hδ0, abs_neg]
  have hmem : (q.1 + d1, q.2 + d2) ∈ Metric.ball q ε := by
    rw [Metric.mem_ball, Prod.dist_eq, Real.dist_eq, Real.dist_eq]
    simp only [add_sub_cancel_left]
    exact max_lt (by linarith [habs1]) (by linarith [habs2])
  have hin : (q.1 + d1, q.2 + d2) ∈ interior (slotBox c) := by
    rw [interior_slotBox]
    simp only [mem_prod, mem_Ioo]
    refine ⟨⟨?_, ?_⟩, ?_, ?_⟩
    · rw [hd1]; split_ifs <;> linarith
    · rw [hd1]; split_ifs <;> linarith
    · rw [hd2]; split_ifs <;> linarith
    · rw [hd2]; split_ifs <;> linarith
  exact Set.disjoint_left.mp hd (hball hmem) hin

/-! ## Lemma SWEEP -/

/-- **SWEEP, frame form.**  If `(x, y) + v` (`v ≥ 0`, `x, y ≥ 0`) lies in the open cell `(i, j)`
of a Young diagram, then `(x, y)` lies in a closed cell of the diagram (the cell of its floors). -/
theorem sweep_core {D : Finset (ℕ × ℕ)} (hD : IsYoung D) {x y vx vy : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y)
    (hvx : 0 ≤ vx) (hvy : 0 ≤ vy) {i j : ℕ} (hij : (i, j) ∈ D)
    (h : x + vx < i + 1 ∧ y + vy < j + 1) :
    ∃ x' ∈ D, (x'.1 : ℝ) ≤ x ∧ x ≤ x'.1 + 1 ∧ (x'.2 : ℝ) ≤ y ∧ y ≤ x'.2 + 1 := by
  refine ⟨(⌊x⌋₊, ⌊y⌋₊), hD _ hij _ _ ?_ ?_, Nat.floor_le hx, (Nat.lt_floor_add_one x).le,
    Nat.floor_le hy, (Nat.lt_floor_add_one y).le⟩
  · have : x < ((i + 1 : ℕ) : ℝ) := by push_cast; linarith
    exact Nat.lt_succ_iff.mp ((Nat.floor_lt hx).mpr this)
  · have : y < ((j + 1 : ℕ) : ℝ) := by push_cast; linarith
    exact Nat.lt_succ_iff.mp ((Nat.floor_lt hy).mpr this)

/-- The slot of a cell of `S` at corner `c'` is in `S`. -/
theorem slot_of_mem_pinCells {S : PinSet} {c' : Fin 4} {ij : ℕ × ℕ} (h : ij ∈ pinCells S c') :
    (⟨c', ij.1, ij.2⟩ : Slot) ∈ S := by
  simp only [pinCells, Finset.mem_image, Finset.mem_filter] at h
  obtain ⟨a, ⟨ha, hac⟩, rfl⟩ := h
  have : a = ⟨c', a.cellx, a.celly⟩ := by
    cases a; simp only at hac; subst hac; rfl
  rw [← this]; exact ha

/-- **SWEEP for a square of the packing.**  Let `j` be a square of a packing containing the pins
of `S` (with pin data `P`) that is NOT a pin of corner `c'`, and `w` a displacement whose frame
image at `c'` is `≥ 0`.  Then the interior of `Q_j + w` misses the interior of every pin square
of corner `c'`. -/
theorem sweep_packing {S : PinSet} {z : Cfg} {m : ℝ} (hz : CfgPacking m z) (P : PinData S z m)
    (c' : Fin 4) {j : Fin 11} (hj : ∀ a ∈ S, a.corner = c' → P.f a ≠ j) {w : RP}
    (hw1 : 0 ≤ (if cornerR c' then -w.1 else w.1)) (hw2 : 0 ≤ (if cornerT c' then -w.2 else w.2))
    {a : Slot} (ha : a ∈ S) (hac : a.corner = c') :
    Disjoint (interior (shiftSq w (z j)).set) (interior (z (P.f a)).set) := by
  rw [Set.disjoint_left]
  intro p hp hpa
  have hp' := (mem_interior_shiftSq_iff _ _ _).mp hp
  -- `p` is in the open cell of `a`; `p − w` is in the interior of `Q_j`, inside the container
  have hocc := P.occ a ha
  rw [OccupiesSlot] at hocc
  have hpa' : p ∈ interior (slotBox (slotCentre m a)) := by
    rw [slotBox, ← hocc]; exact hpa
  rw [mem_interior_slotBox_iff_cframe, hac] at hpa'
  have hcont : (p.1 - w.1, p.2 - w.2) ∈ container m :=
    interior_subset.trans (hz.2.contained j) hp'
  obtain ⟨c1, -, c3, -⟩ := cframe_of_mem_container c' hcont
  -- frame coordinates of `p` = those of `p − w` plus the (nonnegative) frame image of `w`
  have hcf : cframe m c' p
      = ((cframe m c' (p.1 - w.1, p.2 - w.2)).1 + (if cornerR c' then -w.1 else w.1),
         (cframe m c' (p.1 - w.1, p.2 - w.2)).2 + (if cornerT c' then -w.2 else w.2)) := by
    have h := cframe_add m c' (p.1 - w.1, p.2 - w.2) w
    simpa only [sub_add_cancel, Prod.mk.eta] using h
  rw [hcf] at hpa'
  obtain ⟨-, h2, -, h4⟩ := hpa'
  have hij : (a.cellx, a.celly) ∈ pinCells S c' := by
    simp only [pinCells, Finset.mem_image, Finset.mem_filter]
    exact ⟨a, ⟨ha, hac⟩, rfl⟩
  obtain ⟨x', hx'D, hx1, hx2, hx3, hx4⟩ := sweep_core (P.young c') c1 c3 hw1 hw2 hij ⟨h2, h4⟩
  -- `p − w` lies in the closed cell `x'` of a pin of corner `c'`, interior-disjoint from `Q_j`
  have hslot := slot_of_mem_pinCells hx'D
  have hocc' := P.occ _ hslot
  have hne : P.f ⟨c', x'.1, x'.2⟩ ≠ j := hj _ hslot rfl
  have hdis := hz.2.interiorDisjoint j _ hne.symm
  have hmem : (p.1 - w.1, p.2 - w.2) ∈ slotBox (slotCentre m ⟨c', x'.1, x'.2⟩) := by
    rw [mem_slotBox_iff_cframe]
    exact ⟨hx1, hx2, hx3, hx4⟩
  rw [OccupiesSlot] at hocc'
  have hd' : Disjoint (interior (z j).set) (interior (slotBox (slotCentre m ⟨c', x'.1, x'.2⟩))) := by
    rw [slotBox, ← hocc']; exact hdis
  exact interior_notMem_slotBox_of_disjoint hd' hp' hmem

/-! ## The pinned shift is a packing containing the pins -/

theorem shiftSq_set_subset_container {m τ : ℝ} {v : RP} (hv1 : 0 ≤ v.1 ∧ v.1 ≤ τ)
    (hv2 : 0 ≤ v.2 ∧ v.2 ≤ τ) {q : PSq} (hq : q.set ⊆ container m) :
    (shiftSq v q).set ⊆ container (m + τ) := by
  intro p hp
  have hp' := (mem_shiftSq_set_iff _ _ _).mp hp
  have hc := hq hp'
  simp only [container, mem_prod, mem_Icc] at hc ⊢
  obtain ⟨⟨h1, h2⟩, h3, h4⟩ := hc
  exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

theorem disjoint_shift_of_rel {u v : RP} {q q' : PSq}
    (h : Disjoint (interior (shiftSq (u.1 - v.1, u.2 - v.2) q).set) (interior q'.set)) :
    Disjoint (interior (shiftSq u q).set) (interior (shiftSq v q').set) := by
  rw [Set.disjoint_left] at h ⊢
  intro p hp hp'
  have h1 := (mem_interior_shiftSq_iff _ _ _).mp hp
  have h2 := (mem_interior_shiftSq_iff _ _ _).mp hp'
  refine h (a := (p.1 - v.1, p.2 - v.2)) ?_ h2
  rw [mem_interior_shiftSq_iff]
  convert h1 using 2 <;> ring

theorem disp_bounds (c : Fin 4) {τ : ℝ} (hτ : 0 ≤ τ) (pc : Fin 11 → Option (Fin 4)) (i : Fin 11) :
    (0 ≤ (disp c τ pc i).1 ∧ (disp c τ pc i).1 ≤ τ) ∧ (0 ≤ (disp c τ pc i).2 ∧ (disp c τ pc i).2 ≤ τ) := by
  simp only [disp]
  rcases pc i with _ | c' <;> simp only [pinVec, shiftVec] <;> split_ifs <;>
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

/-- The relative displacement of any square w.r.t. the block of corner `c'` points away from
`c'`'s walls (frame image `≥ 0`), for every kind of square. -/
theorem rel_disp_nonneg (c : Fin 4) {τ : ℝ} (hτ : 0 ≤ τ) (pc : Fin 11 → Option (Fin 4)) (j : Fin 11)
    (c' : Fin 4) :
    0 ≤ (if cornerR c' then -((disp c τ pc j).1 - (pinVec c' τ).1) else (disp c τ pc j).1 - (pinVec c' τ).1) ∧
    0 ≤ (if cornerT c' then -((disp c τ pc j).2 - (pinVec c' τ).2) else (disp c τ pc j).2 - (pinVec c' τ).2) := by
  simp only [disp]
  rcases pc j with _ | c'' <;> simp only [pinVec, shiftVec] <;> constructor <;> split_ifs <;> linarith

/-- **Lemma MOVE, cluster-free**: for every `τ ≥ 0` the pinned shift of a packing containing the
pins of `S` is a packing at side `m + τ`, and it contains the pins of `S` (each block exactly at
its slots of the grown container). -/
theorem pinnedShift_packing {S : PinSet} {z : Cfg} {m τ : ℝ} (hτ : 0 ≤ τ) (hz : CfgPacking m z)
    (P : PinData S z m) (c : Fin 4) :
    CfgPacking (m + τ) (pinnedShift c τ P.pc z) ∧ ContainsPins S (m + τ) (pinnedShift c τ P.pc z) := by
  refine ⟨⟨fun i => hz.1 i, ⟨fun i => psq_isUnitSquare _, fun i => ?_, fun i j hij => ?_⟩⟩, ?_⟩
  · obtain ⟨h1, h2⟩ := disp_bounds c hτ P.pc i
    exact shiftSq_set_subset_container h1 h2 (hz.2.contained i)
  · -- interior-disjointness, by the kind of `i`
    show Disjoint (interior (shiftSq (disp c τ P.pc i) (z i)).set)
      (interior (shiftSq (disp c τ P.pc j) (z j)).set)
    rcases hpi : P.pc i with _ | ci
    · rcases hpj : P.pc j with _ | cj
      · -- both non-pins: rigid
        have e : disp c τ P.pc i = disp c τ P.pc j := by simp only [disp, hpi, hpj]
        rw [e]
        exact ((disjoint_shift_of_rel (u := disp c τ P.pc j) (v := disp c τ P.pc j)) (by
          simp only [sub_self]
          have : shiftSq ((0 : ℝ), (0 : ℝ)) (z i) = z i := by simp [shiftSq]
          rw [this]; exact hz.2.interiorDisjoint i j hij))
      · -- `j` a pin of corner `cj`, `i` a non-pin: SWEEP at `cj`
        obtain ⟨a, ha, hfa, hac⟩ := P.pc_some j cj hpj
        have hdj : disp c τ P.pc j = pinVec cj τ := by simp only [disp, hpj]
        rw [hdj]
        refine disjoint_shift_of_rel ?_
        rw [← hfa]
        have hrel := rel_disp_nonneg c hτ P.pc i cj
        refine sweep_packing hz P cj (fun b hb hbc hbi => ?_) hrel.1 hrel.2 ha hac
        have := P.pc_pin b hb
        rw [hbi, hpi] at this
        exact absurd this (by simp)
    · rcases hpj : P.pc j with _ | cj
      · -- `i` a pin of corner `ci`, `j` a non-pin: SWEEP at `ci`, symmetric
        obtain ⟨a, ha, hfa, hac⟩ := P.pc_some i ci hpi
        have hdi : disp c τ P.pc i = pinVec ci τ := by simp only [disp, hpi]
        rw [hdi]
        refine Disjoint.symm (disjoint_shift_of_rel ?_)
        rw [← hfa]
        have hrel := rel_disp_nonneg c hτ P.pc j ci
        refine sweep_packing hz P ci (fun b hb hbc hbj => ?_) hrel.1 hrel.2 ha hac
        have := P.pc_pin b hb
        rw [hbj, hpj] at this
        exact absurd this (by simp)
      · -- two pins
        obtain ⟨a, ha, hfa, hac⟩ := P.pc_some i ci hpi
        obtain ⟨b, hb, hfb, hbc⟩ := P.pc_some j cj hpj
        have hdi : disp c τ P.pc i = pinVec ci τ := by simp only [disp, hpi]
        have hdj : disp c τ P.pc j = pinVec cj τ := by simp only [disp, hpj]
        rw [hdi, hdj]
        by_cases hcc : ci = cj
        · -- the same block: rigid
          subst hcc
          exact disjoint_shift_of_rel (by
            simp only [sub_self]
            have : shiftSq ((0 : ℝ), (0 : ℝ)) (z i) = z i := by simp [shiftSq]
            rw [this]; exact hz.2.interiorDisjoint i j hij)
        · -- different blocks: SWEEP at `ci` (`j` is not a pin of corner `ci`)
          refine Disjoint.symm (disjoint_shift_of_rel ?_)
          rw [← hfa]
          have hrel := rel_disp_nonneg c hτ P.pc j ci
          rw [hdj] at hrel
          refine sweep_packing hz P ci (fun b' hb' hb'c hb'j => hcc ?_) hrel.1 hrel.2 ha hac
          have hpb' := P.pc_pin b' hb'
          rw [hb'j, hpj] at hpb'
          exact hb'c.symm.trans (Option.some.inj hpb').symm
  · -- the pins stay at their slots
    refine ⟨P.f, P.inj, fun a ha => ?_⟩
    have hocc := P.occ a ha
    have hpc := P.pc_pin a ha
    show OccupiesSlot (shiftSq (disp c τ P.pc (P.f a)) (z (P.f a))) (slotCentre (m + τ) a)
    have hd : disp c τ P.pc (P.f a) = pinVec a.corner τ := by simp only [disp, hpc]
    rw [hd, OccupiesSlot]
    ext p
    rw [mem_shiftSq_set_iff]
    rw [OccupiesSlot] at hocc
    rw [hocc]
    rw [slotCentre_affine, slotCentre_affine]
    simp only [slotBX, slotBY, pinVec, mem_prod, mem_Icc]
    split_ifs <;> constructor <;> rintro ⟨⟨h1, h2⟩, h3, h4⟩ <;>
      exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

end

end S11
end PackingCert
