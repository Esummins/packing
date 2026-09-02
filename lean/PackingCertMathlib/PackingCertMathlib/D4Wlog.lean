import PackingCertMathlib.Census

/-!
# The D4 reduction (WLOG) lemma (A78, depgraph node D.D4 — H12)

`docs/proofs/d4_reduction_s0.md` D4.1: *given the root occupancy lemma at side `s` (every
11-packing in `[0,s]²` has a square whose centre lies in the zone
`Z(s) = [½+cw, s−½−cw]²`), one may assume WLOG that the witness square's centre lies in
the fundamental triangle `T(s) = {s/2 ≤ y ≤ x ≤ s−½−cw}` and its orientation in
`[0°, 90°]`.*  A67 machine-checked the ingredients R1–R8 at `s₀` computationally; here
the reduction is a THEOREM at EVERY side `s` and every zone width `cw`, built on the D4
action of `Census.lean` (`d4Apply`, `d4Cfg`, `d4_packing` = R2/R3/R5):

* `d4_cover_zone` — R4: the eight images of `T` cover `Z` (sign-normalise the centred
  coordinates, then swap if `|dy| > |dx|`);
* `d4_wlog` — the WLOG itself, CONDITIONAL on the root occupancy hypothesis exactly as
  D4.4 records (it exists at `3.84`, not at `s₀`): the transformed configuration is a
  packing at the same side, has a square centred in `T`, and every tilt stays in
  `[0,1]` (`θ ∈ [0°,90°]`).

Not here (and not a theorem anywhere yet): the root occupancy lemma at `s₀` itself, the
`s₀` case tree (D.TREE), and the `S₁₁` half of H12 (seam S6 = D.S6).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-- The zone `Z(s) = [½+cw, s−½−cw]²`. -/
def zoneZ (s cw : ℝ) : Set RP :=
  Icc (1 / 2 + cw) (s - 1 / 2 - cw) ×ˢ Icc (1 / 2 + cw) (s - 1 / 2 - cw)

/-- The fundamental triangle `T(s) = {(x, y) : s/2 ≤ y ≤ x ≤ s − ½ − cw}`. -/
def fundT (s cw : ℝ) : Set RP := {p | s / 2 ≤ p.2 ∧ p.2 ≤ p.1 ∧ p.1 ≤ s - 1 / 2 - cw}

/-- **R4 as a theorem:** the D4 images of the fundamental triangle cover the zone — for
every `p ∈ Z(s)` some `g` sends `p` into `T(s)`. -/
theorem d4_cover_zone {s cw : ℝ} {p : RP} (hp : p ∈ zoneZ s cw) :
    ∃ g : D4, d4Apply s g p ∈ fundT s cw := by
  obtain ⟨px, py⟩ := p
  simp only [zoneZ, mem_prod, mem_Icc] at hp
  obtain ⟨⟨hx0, hx1⟩, hy0, hy1⟩ := hp
  rcases le_total 0 (px - s / 2) with hx | hx <;> rcases le_total 0 (py - s / 2) with hy | hy
  · rcases le_total (py - s / 2) (px - s / 2) with h | h
    · exact ⟨⟨false, false, false⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩
    · exact ⟨⟨true, false, false⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩
  · rcases le_total (s / 2 - py) (px - s / 2) with h | h
    · exact ⟨⟨false, false, true⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩
    · exact ⟨⟨true, true, false⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩
  · rcases le_total (py - s / 2) (s / 2 - px) with h | h
    · exact ⟨⟨false, true, false⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩
    · exact ⟨⟨true, false, true⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩
  · rcases le_total (s / 2 - py) (s / 2 - px) with h | h
    · exact ⟨⟨false, true, true⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩
    · exact ⟨⟨true, true, true⟩, by
        simp only [d4Apply, sg, fundT, mem_setOf_eq, Bool.false_eq_true, ↓reduceIte]
        exact ⟨by linarith, by linarith, by linarith⟩⟩

/-- **The D4 reduction (D.D4), conditional on root occupancy.**  If every packing at side
`s` has a square centred in the zone, then every packing at side `s` has a D4-image that
is a packing at side `s` with a square centred in the fundamental triangle and all tilts
in `[0,1]`.  The symmetry is an explicit container symmetry (`d4Apply_sqdist`,
`d4Apply_image_container`) and the squares are its images (`d4Cfg_set`). -/
theorem d4_wlog {s cw : ℝ}
    (hroot : ∀ z : Fin 11 → PSq, (∀ i, (z i).t ∈ Icc (0 : ℝ) 1) →
      IsPacking 11 s (fun i => (z i).set) → ∃ k, ((z k).cx, (z k).cy) ∈ zoneZ s cw) :
    ∀ z : Fin 11 → PSq, (∀ i, (z i).t ∈ Icc (0 : ℝ) 1) →
      IsPacking 11 s (fun i => (z i).set) →
      ∃ g : D4, (∀ i, (d4Cfg s g z i).t ∈ Icc (0 : ℝ) 1) ∧
        IsPacking 11 s (fun i => (d4Cfg s g z i).set) ∧
        (∃ k, ((d4Cfg s g z k).cx, (d4Cfg s g z k).cy) ∈ fundT s cw) ∧
        ∀ j, (d4Cfg s g z j).set = d4Apply s g '' (z j).set := by
  intro z ht hP
  obtain ⟨k, hk⟩ := hroot z ht hP
  obtain ⟨g, hg⟩ := d4_cover_zone hk
  obtain ⟨ht', hP'⟩ := d4_packing g ht hP
  exact ⟨g, ht', hP', ⟨k, hg⟩, fun j => d4Cfg_set g ht j⟩

end

end S11
end PackingCert
