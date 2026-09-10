import Mathlib.MeasureTheory.Measure.Lebesgue.Basic
import PackingCertMathlib.Windows

/-!
# The GUARD-LINE clause — Lemma LINE-1 and Theorem G (A192, from A144 / A190)

`docs/proofs/guardline_clause.md` §1 (Lemma LINE-1), §3 (Theorem G), §7 (the Lean shape);
A144 `notes/spec.md` §5.  A guard line `l` is `y = h` or `x = g`; the measure gains a
one-dimensional part `Σ_l z_l · H¹|_l`, so a square's mass is its atoms plus `Σ_l z_l · |l ∩ Q|`.

* `chord_sum_le_side` — **Lemma LINE-1** for STRICT families (closed unit squares, pairwise
  disjoint as closed sets — the families the certificate theorems refute after the dilation):
  the closed chords on any axis-parallel line sum to at most `s`.  One-dimensional Lebesgue
  additivity on the (measurable, pairwise disjoint) preimages under the line's parametrisation,
  all inside `[0, s]`.  [F] Stated for INTERIOR-disjoint squares with CLOSED chords (as the
  document's §1 does) the lemma is FALSE — six axis-aligned unit squares in two rows meeting
  along `y = 1` inside `[0, 3.9]²` have closed chords summing to `6` — and with OPEN chords it is
  true but the verifier's `chord_at` (closed convention at `t ∈ {0, 1}`) would not be a lower
  bound.  On strict families both conventions agree and the verifier's is the sound one; the
  certificate chain only ever applies Theorem G to strict families (`Dilation.lean`).
* `guarded_dead` — **Theorem G** at the set level: Theorem W's counted set
  (`WindowsW.windowed_counted`) with the mass `atoms + Σ_l z_l · chord`, the line part bounded
  by LINE-1 minus the chords of the uncounted squares `own '' J_l` (the re-derived
  `rhs*_l = s − Σ_{j ∈ J_l} chord_lo(j, l)`).

Left [C] (the checker side, `guardline_clause.md` §7): `chordLen_eq` (the exact formula (CH)),
`minchord_of_box` (Lemma MINCHORD's five-point checker), the three distinctness checkers.
The hypothesis `hclo` below is exactly what they must deliver: `chord_lo(j, l) ≤ |l ∩ Q(own j)|`.
No axiom is introduced.
-/

namespace PackingCert
namespace S11
namespace GuardLineW

open Set MeasureTheory MeasureI
open PackingCert.S11.WindowsW

noncomputable section

/-! ## 1. Guard lines and chords -/

/-- An axis-parallel guard line: `y = offset` (`horizontal = true`) or `x = offset`. -/
structure GuardLine where
  horizontal : Bool
  offset : ℝ

/-- The unit-speed parametrisation of the line. -/
def GuardLine.param (l : GuardLine) (u : ℝ) : RP :=
  if l.horizontal then (u, l.offset) else (l.offset, u)

theorem GuardLine.continuous_param (l : GuardLine) : Continuous l.param := by
  unfold GuardLine.param
  split_ifs <;> fun_prop

/-- A parameter whose point lies in the container lies in `[0, s]`. -/
theorem GuardLine.param_mem_container {l : GuardLine} {u s : ℝ}
    (h : l.param u ∈ container s) : u ∈ Icc (0 : ℝ) s := by
  obtain ⟨hor, off⟩ := l
  cases hor
  · have h' : (off, u) ∈ container s := by simpa [GuardLine.param] using h
    unfold container at h'
    exact (mem_prod.mp h').2
  · have h' : (u, off) ∈ container s := by simpa [GuardLine.param] using h
    unfold container at h'
    exact (mem_prod.mp h').1

/-- The chord of a set on the line, as a parameter set. -/
def chordSet (l : GuardLine) (S : Set RP) : Set ℝ := l.param ⁻¹' S

/-- The chord length `|l ∩ S|` (one-dimensional Lebesgue measure). -/
def chordLen (l : GuardLine) (S : Set RP) : ℝ := (volume (chordSet l S)).toReal

theorem chordLen_nonneg (l : GuardLine) (S : Set RP) : 0 ≤ chordLen l S :=
  ENNReal.toReal_nonneg

/-- A closed unit square is a closed set (the continuous image of the compact `[0,1]²`). -/
theorem isClosed_sqSet (p0 e : RP) : IsClosed (sqSet p0 e) := by
  rw [sqSet_eq_image]
  refine (IsCompact.image (isCompact_Icc.prod isCompact_Icc) ?_).isClosed
  unfold aff
  fun_prop

theorem isClosed_of_isUnitSquare {S : Set RP} (h : IsUnitSquare S) : IsClosed S := by
  obtain ⟨p0, e, -, rfl⟩ := h
  exact isClosed_sqSet p0 e

/-! ## 2. Lemma LINE-1 -/

/-- **Lemma LINE-1** (`guardline_clause.md` §1) for strict families: the chords of pairwise
disjoint closed unit squares inside `[0, s]²` on an axis-parallel line sum to at most `s`. -/
theorem chord_sum_le_side {N : ℕ} {s : ℝ} (hs : 0 ≤ s) {Q : Fin N → Set RP}
    (hQ : IsStrictFamily N s Q) (l : GuardLine) :
    ∑ i, chordLen l (Q i) ≤ s := by
  have hmeas : ∀ i, MeasurableSet (chordSet l (Q i)) := fun i =>
    ((isClosed_of_isUnitSquare (hQ.unit i)).preimage l.continuous_param).measurableSet
  have hpd : Pairwise (Function.onFun Disjoint fun i => chordSet l (Q i)) := by
    intro i j hij
    exact (hQ.disjoint i j hij).preimage l.param
  have hunion : (⋃ i, chordSet l (Q i)) ⊆ Icc (0 : ℝ) s := by
    intro u hu
    rw [mem_iUnion] at hu
    obtain ⟨i, hi⟩ := hu
    exact GuardLine.param_mem_container (hQ.contained i hi)
  have hvol : volume (⋃ i, chordSet l (Q i)) = ∑ i, volume (chordSet l (Q i)) := by
    rw [measure_iUnion hpd hmeas, tsum_fintype]
  have hle : volume (⋃ i, chordSet l (Q i)) ≤ ENNReal.ofReal s := by
    calc volume (⋃ i, chordSet l (Q i)) ≤ volume (Icc (0 : ℝ) s) := measure_mono hunion
      _ = ENNReal.ofReal (s - 0) := Real.volume_Icc
      _ = ENNReal.ofReal s := by rw [sub_zero]
  have hfin : ∀ i ∈ Finset.univ, volume (chordSet l (Q i)) ≠ ⊤ := fun i _ =>
    ne_top_of_le_ne_top ENNReal.ofReal_ne_top
      ((measure_mono (subset_iUnion (fun i => chordSet l (Q i)) i)).trans hle)
  have heq : ∑ i, chordLen l (Q i) = (∑ i, volume (chordSet l (Q i))).toReal := by
    rw [ENNReal.toReal_sum hfin]
    rfl
  rw [heq, ← hvol]
  exact ENNReal.toReal_le_of_le_ofReal hs hle

/-! ## 3. Theorem G -/

/-- The line measure's mass of a set: atoms plus `Σ_l z_l · |l ∩ S|`. -/
def lineMass (atoms : List IAtom) {L : ℕ} (lines : Fin L → GuardLine) (z : Fin L → ℝ)
    (S : Set RP) : ℝ :=
  massIn atoms S + ∑ l, z l * chordLen (lines l) S

/-- **Theorem G** (`guardline_clause.md` §3), set level.  Beyond Theorem W's data: guard lines
`lines l` with densities `z l ≥ 0`; per line a set `J l` of UNATTACHED cores (`hJun`) whose
owners are pairwise distinct (`hinj`) and are not windowed squares (`hoff`), with chord lower
bounds `clo l j ≤ |l ∩ Q(own j)|` (`hclo` — what `chord_lo(j, l)` certifies through
`K_j ⊆ Q(own j)` and Lemma MINCHORD); (V4′) the total `Σw + Σ_l z_l · rhs*_l` is below
`b₄ · NEEDR` with `rhs*_l = s − Σ_{j ∈ J_l} clo l j`. -/
theorem guarded_dead {n m r L : ℕ} {s NEEDR : ℝ} (hs : 0 ≤ s) (hN : 0 ≤ NEEDR)
    (atoms : List IAtom) (hw : ∀ a ∈ atoms, 0 ≤ a.w)
    (lines : Fin L → GuardLine) (z : Fin L → ℝ) (hz : ∀ l, 0 ≤ z l)
    (Exempt : Set RP → Prop)
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
        NEEDR ≤ lineMass atoms lines z S)
    (hV2 : ∀ i S, IsUnitSquare S → S ⊆ container s → W i S →
      (∀ i' j, i' ≠ i → κ i' = some j → Disjoint S (K j)) → ¬ Exempt S →
        NEEDR ≤ lineMass atoms lines z S)
    (hV3 : ∀ i j, κ i = some j → ∀ S, W i S → K j ⊆ S)
    (J : Fin L → Finset (Fin m)) (clo : Fin L → Fin m → ℝ)
    (hJun : ∀ l, ∀ j ∈ J l, ∀ i, κ i ≠ some j)
    (hinj : ∀ l, ∀ x ∈ J l, ∀ y ∈ J l, own x = own y → x = y)
    (hoff : ∀ l, ∀ j ∈ J l, ∀ i, own j ≠ σ i)
    (hclo : ∀ l, ∀ j ∈ J l, clo l j ≤ chordLen (lines l) (Q (own j)))
    (hV4 : (atoms.map fun a => (a.w : ℝ)).sum + ∑ l, z l * (s - ∑ j ∈ J l, clo l j)
      < ((n : ℝ) - m + att.length) * NEEDR) : False := by
  classical
  obtain ⟨Cnt, hcard, hone, hmem⟩ := windowed_counted (lineMass atoms lines z) Exempt hQ K own
    W κ att hnd hatt σ hσ hH1 hH2 hV1 hV2 hV3
  refine count_core hN (fun k => lineMass atoms lines z (Q k)) Cnt hcard
    (fun k hk => (hone k hk).resolve_left (hH3 k)) ?_ hV4
  unfold lineMass
  rw [Finset.sum_add_distrib]
  have hA := massIn_finset_sum_le hQ atoms hw Cnt
  have hB : ∑ k ∈ Cnt, ∑ l, z l * chordLen (lines l) (Q k)
      ≤ ∑ l, z l * (s - ∑ j ∈ J l, clo l j) := by
    rw [Finset.sum_comm]
    refine Finset.sum_le_sum fun l _ => ?_
    rw [← Finset.mul_sum]
    refine mul_le_mul_of_nonneg_left ?_ (hz l)
    have h1 := chord_sum_le_side hs hQ (lines l)
    have h2 := Finset.sum_add_sum_compl Cnt (fun k => chordLen (lines l) (Q k))
    have h3 : ∑ j ∈ J l, clo l j ≤ ∑ k ∈ Cntᶜ, chordLen (lines l) (Q k) := by
      calc ∑ j ∈ J l, clo l j
          ≤ ∑ j ∈ J l, chordLen (lines l) (Q (own j)) :=
            Finset.sum_le_sum fun j hj => hclo l j hj
        _ = ∑ k ∈ (J l).image own, chordLen (lines l) (Q k) :=
            (Finset.sum_image (f := fun k => chordLen (lines l) (Q k)) (hinj l)).symm
        _ ≤ ∑ k ∈ Cntᶜ, chordLen (lines l) (Q k) := by
            refine Finset.sum_le_sum_of_subset_of_nonneg ?_
              (fun k _ _ => chordLen_nonneg _ _)
            intro k hk
            rw [Finset.mem_image] at hk
            obtain ⟨j, hj, rfl⟩ := hk
            rw [Finset.mem_compl]
            intro hin
            rcases hmem _ hin with ⟨i, hi⟩ | hno
            · exact hoff l j hj i hi.symm
            · exact hno j (hJun l j hj) rfl
    linarith
  linarith

end

end GuardLineW
end S11
end PackingCert
