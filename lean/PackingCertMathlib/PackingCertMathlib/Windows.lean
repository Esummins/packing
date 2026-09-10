import Mathlib.Tactic
import PackingCertMathlib.Dilation
import PackingCertMathlib.CaseHyp

/-!
# The WINDOWS clause of the case-measure certificate — Theorem W (A192, from A185)

`docs/proofs/boxed_windows.md` §2 (Theorem W) and §5 (the Lean shape).  A node of the case
tree names `r` of its squares by POSE WINDOWS `W_i` and `m` cores `K_j`, of which `r_c` are
ATTACHED to a window (`κ : [r] ⇀ [m]`, injective).  A finite measure `μ` with total `τ`
certifies the node dead when

* (V1) every admissible square meeting no core (and in no NO-family) carries `μ ≥ 1` — required
  only if the free count `f = n − r − (m − r_c)` is positive;
* (V2) for every window `i`, every admissible square with pose in `W_i` that meets no core
  attached to ANOTHER window (and is in no NO-family) carries `μ ≥ 1`;
* (V3) an attached core lies inside every pose of its window;
* (V4) `τ < b₄ = n − m + r_c`.

This file proves the counting (§2 of the document) at the SET level, in the shape of
`Dilation.priced_dichotomy`: a strict family `Q` (closed unit squares, pairwise disjoint as
closed sets — what the dilation of `closed_disjoint_bridge.md` supplies below the certified
side) with an injective window assignment `σ`, designated owners `own` of the unattached cores,
and an abstract exemption predicate `Exempt` (the NO-families).

* `count_core` — the two-line counting: `b ≤ |Cnt|`, `NEEDR ≤ μ` on `Cnt`, `Σ_{Cnt} μ ≤ τ`,
  `τ < b · NEEDR` is contradictory;
* `windowed_counted` — **Theorem W's bookkeeping**: the counted set `Cnt` (`= (B ∖ A)ᶜ`, or
  `A` when `f ≤ 0`) has `|Cnt| ≥ n − m + r_c`, every member is either NO-exempt or priced, and
  every member is a windowed square or a square containing no unattached core (the clause the
  guard-line theorem of `GuardLine.lean` consumes);
* `windowed_dead` — **Theorem W**, kill form: with no NO-exempt square and a total `< b₄ · NEEDR`,
  no strict family satisfies the node hypothesis;
* `windowed_no_family` — the B-NO form: some square of the family is NO-exempt;
* `massIn_finset_sum_le` — the atomic measure's mass on any sub-family is at most its total.

The attached cores enter through a `Nodup` index list `att` (what the checker of
`WindowsCheck.lean` computes); `r_c = att.length`.  No axiom is introduced.
-/

namespace PackingCert
namespace S11
namespace WindowsW

open Set MeasureI CaseI

noncomputable section

/-! ## 1. The counting core -/

/-- The two-line counting argument at scale `NEEDR ≥ 0`. -/
theorem count_core {n : ℕ} {τ b NEEDR : ℝ} (hN : 0 ≤ NEEDR) (μ : Fin n → ℝ)
    (Cnt : Finset (Fin n)) (hcard : b ≤ (Cnt.card : ℝ))
    (hone : ∀ k ∈ Cnt, NEEDR ≤ μ k) (hsum : ∑ k ∈ Cnt, μ k ≤ τ) (hτ : τ < b * NEEDR) :
    False := by
  have h := Finset.card_nsmul_le_sum Cnt μ NEEDR hone
  rw [nsmul_eq_mul] at h
  have h2 : b * NEEDR ≤ (Cnt.card : ℝ) * NEEDR := mul_le_mul_of_nonneg_right hcard hN
  linarith

/-- The atomic measure's mass on ANY sub-family of a strict family is at most its total: an atom
lies in at most one member (`indicator_sum_le`, padded by `∅`). -/
theorem massIn_finset_sum_le {n : ℕ} {s : ℝ} {Q : Fin n → Set RP}
    (hQ : IsStrictFamily n s Q) (atoms : List IAtom) (hw : ∀ a ∈ atoms, 0 ≤ a.w)
    (G : Finset (Fin n)) :
    ∑ k ∈ G, massIn atoms (Q k) ≤ (atoms.map fun a => (a.w : ℝ)).sum := by
  classical
  have hempty : massIn atoms (∅ : Set RP) = 0 := by simp [massIn]
  have hpad : ∑ k ∈ G, massIn atoms (Q k)
      = ∑ k : Fin n, massIn atoms (if k ∈ G then Q k else ∅) := by
    simp only [apply_ite (massIn atoms), hempty, Finset.sum_ite_mem, Finset.univ_inter]
  rw [hpad, massIn_sum_comm]
  refine List.sum_le_sum fun a ha => ?_
  have hwa : (0 : ℝ) ≤ (a.w : ℝ) := by exact_mod_cast hw a ha
  refine indicator_sum_le ?_ hwa (atomPt a)
  intro i j hij
  by_cases hi : i ∈ G <;> by_cases hj : j ∈ G <;> simp [hi, hj, hQ.disjoint i j hij]

/-! ## 2. Theorem W — the bookkeeping -/

/-- **Theorem W, the counted set** (`boxed_windows.md` §2, steps (i)–(iii) without the final
sum).  Data: a strict family `Q` at side `s`; cores `K j` with designated owners `own j` (used
for the UNATTACHED ones only, (H2)); windows `W i` as predicates on the square; the attachment
`κ`, with the attached cores listed without repetition in `att` (`r_c = att.length`); the window
assignment `σ`, injective, `pose(Q (σ i)) ∈ W_i` (H1); (V3) an attached core lies in every pose
of its window.  (V1) and (V2) are the two covering clauses, at scale `NEEDR`.

Conclusion: a set `Cnt` of at least `n − m + r_c` squares, each NO-exempt or priced `≥ NEEDR`,
and each either windowed or free of every unattached core. -/
theorem windowed_counted {n m r : ℕ} {s NEEDR : ℝ}
    (μ : Set RP → ℝ) (Exempt : Set RP → Prop)
    {Q : Fin n → Set RP} (hQ : IsStrictFamily n s Q)
    (K : Fin m → Set RP) (own : Fin m → Fin n)
    (W : Fin r → Set RP → Prop) (κ : Fin r → Option (Fin m))
    (att : List ℕ) (hnd : att.Nodup)
    (hatt : ∀ j ∈ att, ∃ jj : Fin m, (jj : ℕ) = j ∧ ∃ i, κ i = some jj)
    (σ : Fin r → Fin n) (hσ : Function.Injective σ)
    (hH1 : ∀ i, W i (Q (σ i)))
    (hH2 : ∀ j, (∀ i, κ i ≠ some j) → K j ⊆ Q (own j))
    (hV1 : 0 < (n : ℝ) - r - ((m : ℝ) - att.length) →
      ∀ S, IsUnitSquare S → S ⊆ container s → (∀ j, Disjoint S (K j)) → ¬ Exempt S →
        NEEDR ≤ μ S)
    (hV2 : ∀ i S, IsUnitSquare S → S ⊆ container s → W i S →
      (∀ i' j, i' ≠ i → κ i' = some j → Disjoint S (K j)) → ¬ Exempt S → NEEDR ≤ μ S)
    (hV3 : ∀ i j, κ i = some j → ∀ S, W i S → K j ⊆ S) :
    ∃ Cnt : Finset (Fin n),
      (n : ℝ) - m + att.length ≤ Cnt.card ∧
      (∀ k ∈ Cnt, Exempt (Q k) ∨ NEEDR ≤ μ (Q k)) ∧
      (∀ k ∈ Cnt, (∃ i, σ i = k) ∨ ∀ j, (∀ i, κ i ≠ some j) → own j ≠ k) := by
  classical
  set A : Finset (Fin n) := Finset.univ.image σ with hA
  set Att : Finset (Fin m) := Finset.univ.filter (fun j : Fin m => ∃ i, κ i = some j) with hAtt
  set B : Finset (Fin n) := Attᶜ.image own with hB
  have hAcard : A.card = r := by
    rw [hA, Finset.card_image_of_injective _ hσ, Finset.card_univ, Fintype.card_fin]
  -- `r_c = att.length ≤ |Att|`
  have hrc : att.length ≤ Att.card := by
    have h1 : att.toFinset ⊆ Att.image (fun j : Fin m => (j : ℕ)) := by
      intro j hj
      rw [List.mem_toFinset] at hj
      obtain ⟨jj, hjj, i, hi⟩ := hatt j hj
      rw [Finset.mem_image]
      exact ⟨jj, by rw [hAtt, Finset.mem_filter]; exact ⟨Finset.mem_univ _, i, hi⟩, hjj⟩
    have h2 := Finset.card_le_card h1
    rw [List.toFinset_card_of_nodup hnd,
      Finset.card_image_of_injective _ Fin.val_injective] at h2
    exact h2
  have hUn : Att.card + Attᶜ.card = m := by
    rw [Finset.card_add_card_compl, Fintype.card_fin]
  have hBcard : B.card ≤ Attᶜ.card := Finset.card_image_le
  have hmemB : ∀ k, k ∈ B ↔ ∃ j, (∀ i, κ i ≠ some j) ∧ own j = k := by
    intro k
    simp only [hB, Finset.mem_image, Finset.mem_compl, hAtt, Finset.mem_filter,
      Finset.mem_univ, true_and, not_exists, ne_eq]
  have hmemA : ∀ k, k ∈ A ↔ ∃ i, σ i = k := by
    intro k
    simp [hA]
  -- (i) the windowed squares
  have hwin : ∀ i, Exempt (Q (σ i)) ∨ NEEDR ≤ μ (Q (σ i)) := by
    intro i
    by_cases hex : Exempt (Q (σ i))
    · exact Or.inl hex
    · right
      refine hV2 i (Q (σ i)) (hQ.unit _) (hQ.contained _) (hH1 i) ?_ hex
      intro i' j hi' hj
      have hsub : K j ⊆ Q (σ i') := hV3 i' j hj _ (hH1 i')
      have hne : σ i ≠ σ i' := fun h => hi' (hσ h).symm
      exact (hQ.disjoint _ _ hne).mono_right hsub
  -- (ii) the free squares
  have hfree : 0 < (n : ℝ) - r - ((m : ℝ) - att.length) → ∀ k, k ∉ A → k ∉ B →
      Exempt (Q k) ∨ NEEDR ≤ μ (Q k) := by
    intro hf k hkA hkB
    by_cases hex : Exempt (Q k)
    · exact Or.inl hex
    · right
      refine hV1 hf (Q k) (hQ.unit _) (hQ.contained _) ?_ hex
      intro j
      by_cases hatt' : ∃ i, κ i = some j
      · obtain ⟨i, hi⟩ := hatt'
        have hsub : K j ⊆ Q (σ i) := hV3 i j hi _ (hH1 i)
        have hne : k ≠ σ i := fun h => hkA ((hmemA k).mpr ⟨i, h.symm⟩)
        exact (hQ.disjoint _ _ hne).mono_right hsub
      · have hun : ∀ i, κ i ≠ some j := fun i hi => hatt' ⟨i, hi⟩
        have hsub : K j ⊆ Q (own j) := hH2 j hun
        have hne : k ≠ own j := fun h => hkB ((hmemB k).mpr ⟨j, hun, h.symm⟩)
        exact (hQ.disjoint _ _ hne).mono_right hsub
  have hUnR : (Att.card : ℝ) + (Attᶜ.card : ℝ) = m := by exact_mod_cast hUn
  have hrcR : (att.length : ℝ) ≤ Att.card := by exact_mod_cast hrc
  -- (iii) the counted set
  by_cases hf : 0 < (n : ℝ) - r - ((m : ℝ) - att.length)
  · refine ⟨(B \ A)ᶜ, ?_, ?_, ?_⟩
    · have h1 := Finset.card_add_card_compl (B \ A)
      rw [Fintype.card_fin] at h1
      have h2 : (B \ A).card ≤ B.card := Finset.card_le_card Finset.sdiff_subset
      have h4 : ((B \ A).card : ℝ) + ((B \ A)ᶜ.card : ℝ) = n := by exact_mod_cast h1
      have h5 : ((B \ A).card : ℝ) ≤ Attᶜ.card := by exact_mod_cast h2.trans hBcard
      linarith
    · intro k hk
      rw [Finset.mem_compl, Finset.mem_sdiff, not_and, not_not] at hk
      by_cases hkA : k ∈ A
      · obtain ⟨i, rfl⟩ := (hmemA k).mp hkA
        exact hwin i
      · exact hfree hf k hkA (fun hkB => hkA (hk hkB))
    · intro k hk
      rw [Finset.mem_compl, Finset.mem_sdiff, not_and, not_not] at hk
      by_cases hkA : k ∈ A
      · exact Or.inl ((hmemA k).mp hkA)
      · right
        intro j hj hjk
        exact hkA (hk ((hmemB k).mpr ⟨j, hj, hjk⟩))
  · refine ⟨A, ?_, ?_, ?_⟩
    · push Not at hf
      rw [hAcard]
      linarith
    · intro k hk
      obtain ⟨i, rfl⟩ := (hmemA k).mp hk
      exact hwin i
    · intro k hk
      exact Or.inl ((hmemA k).mp hk)

/-! ## 3. Theorem W — the two end forms -/

/-- **Theorem W, kill form** (`boxed_windows.md` §2).  With no NO-exempt square in the family
(H3), a total `τ` bounding the mass of every sub-family, and `τ < b₄ · NEEDR` (V4), no strict
family satisfies the node hypothesis (H1)–(H3). -/
theorem windowed_dead {n m r : ℕ} {s NEEDR τ : ℝ} (hN : 0 ≤ NEEDR)
    (μ : Set RP → ℝ) (Exempt : Set RP → Prop)
    {Q : Fin n → Set RP} (hQ : IsStrictFamily n s Q)
    (K : Fin m → Set RP) (own : Fin m → Fin n)
    (W : Fin r → Set RP → Prop) (κ : Fin r → Option (Fin m))
    (att : List ℕ) (hnd : att.Nodup)
    (hatt : ∀ j ∈ att, ∃ jj : Fin m, (jj : ℕ) = j ∧ ∃ i, κ i = some jj)
    (σ : Fin r → Fin n) (hσ : Function.Injective σ)
    (hH1 : ∀ i, W i (Q (σ i)))
    (hH2 : ∀ j, (∀ i, κ i ≠ some j) → K j ⊆ Q (own j))
    (hH3 : ∀ k, ¬ Exempt (Q k))
    (hV1 : 0 < (n : ℝ) - r - ((m : ℝ) - att.length) →
      ∀ S, IsUnitSquare S → S ⊆ container s → (∀ j, Disjoint S (K j)) → ¬ Exempt S →
        NEEDR ≤ μ S)
    (hV2 : ∀ i S, IsUnitSquare S → S ⊆ container s → W i S →
      (∀ i' j, i' ≠ i → κ i' = some j → Disjoint S (K j)) → ¬ Exempt S → NEEDR ≤ μ S)
    (hV3 : ∀ i j, κ i = some j → ∀ S, W i S → K j ⊆ S)
    (hupper : ∀ G : Finset (Fin n), ∑ k ∈ G, μ (Q k) ≤ τ)
    (hV4 : τ < ((n : ℝ) - m + att.length) * NEEDR) : False := by
  obtain ⟨Cnt, hcard, hone, -⟩ :=
    windowed_counted μ Exempt hQ K own W κ att hnd hatt σ hσ hH1 hH2 hV1 hV2 hV3
  refine count_core hN (fun k => μ (Q k)) Cnt hcard ?_ (hupper Cnt) hV4
  intro k hk
  exact (hone k hk).resolve_left (hH3 k)

/-- **Theorem W, B-NO form**: without (H3), some square of the family is NO-exempt (the
occupancy conclusion `Composition.lean` consumes through Lemma B-NO). -/
theorem windowed_no_family {n m r : ℕ} {s NEEDR τ : ℝ} (hN : 0 ≤ NEEDR)
    (μ : Set RP → ℝ) (Exempt : Set RP → Prop)
    {Q : Fin n → Set RP} (hQ : IsStrictFamily n s Q)
    (K : Fin m → Set RP) (own : Fin m → Fin n)
    (W : Fin r → Set RP → Prop) (κ : Fin r → Option (Fin m))
    (att : List ℕ) (hnd : att.Nodup)
    (hatt : ∀ j ∈ att, ∃ jj : Fin m, (jj : ℕ) = j ∧ ∃ i, κ i = some jj)
    (σ : Fin r → Fin n) (hσ : Function.Injective σ)
    (hH1 : ∀ i, W i (Q (σ i)))
    (hH2 : ∀ j, (∀ i, κ i ≠ some j) → K j ⊆ Q (own j))
    (hV1 : 0 < (n : ℝ) - r - ((m : ℝ) - att.length) →
      ∀ S, IsUnitSquare S → S ⊆ container s → (∀ j, Disjoint S (K j)) → ¬ Exempt S →
        NEEDR ≤ μ S)
    (hV2 : ∀ i S, IsUnitSquare S → S ⊆ container s → W i S →
      (∀ i' j, i' ≠ i → κ i' = some j → Disjoint S (K j)) → ¬ Exempt S → NEEDR ≤ μ S)
    (hV3 : ∀ i j, κ i = some j → ∀ S, W i S → K j ⊆ S)
    (hupper : ∀ G : Finset (Fin n), ∑ k ∈ G, μ (Q k) ≤ τ)
    (hV4 : τ < ((n : ℝ) - m + att.length) * NEEDR) : ∃ k, Exempt (Q k) := by
  by_contra hno
  push Not at hno
  exact windowed_dead hN μ Exempt hQ K own W κ att hnd hatt σ hσ hH1 hH2 hno hV1 hV2 hV3
    hupper hV4

end

end WindowsW
end S11
end PackingCert
