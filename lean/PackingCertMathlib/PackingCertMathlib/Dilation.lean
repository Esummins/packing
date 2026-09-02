import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.MeasureBridge
import PackingCertMathlib.Attain

/-!
# The λ-dilation bridge: interior-disjoint packings vs closed-disjoint certificates
(A68, depgraph node A.SBRIDGE)

Lemma B of `docs/proofs/closed_disjoint_bridge.md` (the A63 S4/F9 discharge), formalised in
the shape every `stratum_kill` producer consumes it.  A `case-lp-certificate-v1` PASS talks
about families of pairwise-disjoint CLOSED unit squares; the composition applies kills to
packings that are only INTERIOR-disjoint (contacts allowed — every minimiser has them).
The repair is the centre dilation `Δ_λ` (`scaleC`, `MeasureBridge.lean`), `λ > 1`:

* `B.0(a)` `scaleC_disjoint` — the dilates of an interior-disjoint pair are disjoint as
  closed sets.  A64's pull-back trick (`scaleC_mem_interior`) replaces the prose's
  separating-axis citation: a common point of the dilated squares pulls back by `1/λ` to a
  common INTERIOR point of the originals.
* `B.0(b)` — `scaleC_subset`, already a theorem in `MeasureBridge.lean` (A64).
* `B.0(c)` `slot_tracking` — dilated side-`m` slot vs side-`λm` slot: offset exactly
  `(λ−1)·α` per coordinate, for EVERY affine slot coordinate `α + β·s` (no hypothesis on
  `β` — the identity `λ(α+βm) − (α+βλm) = (λ−1)α` is exact).
* `dilation_bridge` — the packaged Lemma-B geometry: an interior-disjoint packing at side
  `m` with tilts in `[0,1]` dilates to an `IsStrictFamily` at side `λm`; centres `λ·c`,
  tilts unchanged (both definitional in `scaleC`).
* `lemma_B` — Lemma B with the certificate's bridged claim as an abstract hypothesis.
* `bprime_containment` — Corollary B′'s hypothesis (H) from the margin condition (H′)
  `(λ−1)·|α| < ρ` (corpus: `ρ ≈ 1.0000009e-9 > 0` exactly, `|α| ≤ 5/2`, A63 scan of all
  68 kill certificates).
* `pullback_mem_Icc` — Lemma B-NO (B.2″) bookkeeping: a `nofams` zone coordinate pulled
  back by `1/λ` lands in the OUTWARD-WIDENED interval `[x₀ − (λ−1)·x₁, x₁]`.

NOT here: the atom-measure pricing (P1)/(P2) inside a PASS — that is the case-LP verifier
soundness (depgraph V.CASE), which produces `lemma_B`'s `hcert` hypothesis per
certificate.  And dilation transfers KILLS only: the pulled-back basin box of
`trump_residual` misses `InBasin` by `~(λ−1)·|ĉ|` (D.SLAB), unchanged by this file.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set MeasureI

/-- Every parametrised square set is a closed unit square. -/
theorem psq_isUnitSquare (q : PSq) : IsUnitSquare q.set :=
  ⟨_, _, rdot_edir q, rfl⟩

/-- A **strict family**: closed unit squares in the container, pairwise disjoint **as
closed sets** — the object a `case-lp-certificate-v1` PASS quantifies over (spec
`docs/specs/case_lp_certificate_v1.md` §1). -/
structure IsStrictFamily (n : ℕ) (s : ℝ) (Q : Fin n → Set RP) : Prop where
  unit : ∀ i, IsUnitSquare (Q i)
  contained : ∀ i, Q i ⊆ container s
  disjoint : ∀ i j, i ≠ j → Disjoint (Q i) (Q j)

/-- Strict families are in particular packings (closed-disjoint ⟹ interior-disjoint). -/
theorem IsStrictFamily.isPacking {n : ℕ} {s : ℝ} {Q : Fin n → Set RP}
    (h : IsStrictFamily n s Q) : IsPacking n s Q where
  unit := h.unit
  contained := h.contained
  interiorDisjoint i j hij :=
    (h.disjoint i j hij).mono interior_subset interior_subset

/-! ## B.0(a): strict disjointness under dilation -/

/-- **Lemma B.0(a).**  The `λ`-dilates (`λ > 1`) of two interior-disjoint parametrised
squares are disjoint as CLOSED sets: a common point pulls back by `1/λ` to a common
interior point (`scaleC_mem_interior`, A64). -/
theorem scaleC_disjoint {lam : ℝ} (hlam : 1 < lam) {q q' : PSq}
    (hd : Disjoint (interior q.set) (interior q'.set)) :
    Disjoint ((scaleC lam q).set) ((scaleC lam q').set) := by
  rw [Set.disjoint_left]
  intro p hp hp'
  exact Set.disjoint_left.mp hd (scaleC_mem_interior hlam hp) (scaleC_mem_interior hlam hp')

/-! ## B.0(c): pin tracking -/

/-- **Lemma B.0(c).**  Slot coordinates are affine in the side, `k(s) = α + β·s`; the
`λ`-dilated side-`m` slot differs from the side-`λm` slot by exactly `(λ−1)·α`. -/
theorem slot_tracking (lam m alpha beta : ℝ) :
    lam * (alpha + beta * m) - (alpha + beta * (lam * m)) = (lam - 1) * alpha := by
  ring

/-! ## The bridge -/

/-- **The λ-dilation bridge** (Lemma B's geometric content, packaged).  An
interior-disjoint packing at side `m` with tilts in `[0,1]` dilates, for any `λ > 1`, to
a strict family at side `λ·m`. -/
theorem dilation_bridge {n : ℕ} {m lam : ℝ} (hlam : 1 < lam) {z : Fin n → PSq}
    (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (hP : IsPacking n m fun i => (z i).set) :
    IsStrictFamily n (lam * m) fun i => (scaleC lam (z i)).set where
  unit _ := psq_isUnitSquare _
  contained i := scaleC_subset hlam.le (ht i).1 (ht i).2 (hP.contained i)
  disjoint i j hij := scaleC_disjoint hlam (hP.interiorDisjoint i j hij)

/-- **Lemma B** (`closed_disjoint_bridge.md` B.1), certificate claim abstracted.
`hcert` is the bridged PASS claim at the certified side `s″`: no strict family at side
`s″` has all `r` cores inside the interiors of its designated owner members — for a kill
certificate this is what (P1) + (P2) + the counting argument prove, and producing it per
certificate is the case-LP verifier soundness (depgraph V.CASE).  Conclusion: no
interior-disjoint packing at side `m = s″/λ` realises the dilated core-containment
hypothesis (H). -/
theorem lemma_B {m lam s'' : ℝ} (hlam : 1 < lam) (hs : s'' = lam * m)
    {z : Fin 11 → PSq} (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (hP : IsPacking 11 m fun i => (z i).set)
    {r : ℕ} (K : Fin r → Set RP) (own : Fin r → Fin 11)
    (hcert : ∀ Q : Fin 11 → Set RP, IsStrictFamily 11 s'' Q →
      (∀ j, K j ⊆ interior (Q (own j))) → False)
    (hH : ∀ j, K j ⊆ interior ((scaleC lam (z (own j))).set)) : False := by
  subst hs
  exact hcert _ (dilation_bridge hlam ht hP) hH

/-! ## The pricing dichotomy: (P1) + (P2) ⟹ the bridged claim

The remaining content of Lemma B's prose proof — μ-additivity over the disjoint
non-owners plus the pigeonhole against the budget — using A64's atom machinery
(`massIn`, `massIn_sum_comm`, `indicator_sum_le` from `MeasureBridge.lean`).  The
`price` hypothesis below IS claim (P2) of the frozen spec
(`docs/specs/case_lp_certificate_v1.md`): every admissible, core-free, non-exempt
placement has `μ ≥ 1`; `hP1` is (P1): `Σw < b = n − r`.  Establishing (P2) for a
concrete PASS file is the case-LP verifier soundness (V.CASE). -/

/-- **The pricing dichotomy** (Lemma B / B-NO common core).  If every admissible
core-free non-exempt placement is priced `μ ≥ 1` (P2) and the total mass is below the
budget `n − r` (P1), then a strict family whose designated owners contain the cores has
a non-owner member that is EXEMPT.  With no exemption (`Exempt = False`, empty `nofams`)
this is Lemma B's contradiction; with `nofams` it is Lemma B-NO's occupancy conclusion.
-/
theorem priced_dichotomy {n r : ℕ} {s'' : ℝ} (atoms : List IAtom)
    (hw : ∀ a ∈ atoms, 0 ≤ a.w)
    {K : Fin r → Set RP} {own : Fin r → Fin n}
    (Exempt : Set RP → Prop)
    (price : ∀ S : Set RP, IsUnitSquare S → S ⊆ container s'' →
      (∀ j, Disjoint S (K j)) → ¬Exempt S → 1 ≤ massIn atoms S)
    (hP1 : (atoms.map fun a => (a.w : ℝ)).sum < (n : ℝ) - (r : ℝ))
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
  -- each non-owner is priced
  have hprice : ∀ i ∈ G, (1 : ℝ) ≤ massIn atoms (Q i) := by
    intro i hi
    have hnotown := (hGmem i).mp hi
    refine price (Q i) (hQ.unit i) (hQ.contained i) (fun j => ?_) (hno i hnotown)
    exact (hQ.disjoint i (own j) fun h => hnotown j h.symm).mono_right (hH j)
  -- the sub-family of non-owners, padded by ∅, is pairwise disjoint
  have hdisf : ∀ i j : Fin n, i ≠ j →
      Disjoint (if i ∈ G then Q i else (∅ : Set RP)) (if j ∈ G then Q j else ∅) := by
    intro i j hij
    by_cases hi : i ∈ G <;> by_cases hj : j ∈ G <;>
      simp [hi, hj, hQ.disjoint i j hij]
  -- upper bound: the priced mass cannot exceed the total mass
  have hupper : ∑ i ∈ G, massIn atoms (Q i) ≤ (atoms.map fun a => (a.w : ℝ)).sum := by
    have hempty : massIn atoms (∅ : Set RP) = 0 := by simp [massIn]
    have hpad : ∑ i ∈ G, massIn atoms (Q i)
        = ∑ i : Fin n, massIn atoms (if i ∈ G then Q i else ∅) := by
      simp only [apply_ite (massIn atoms), hempty, Finset.sum_ite_mem, Finset.univ_inter]
    rw [hpad, massIn_sum_comm]
    refine List.sum_le_sum fun a ha => ?_
    have hwa : (0 : ℝ) ≤ (a.w : ℝ) := by exact_mod_cast hw a ha
    exact indicator_sum_le hdisf hwa (atomPt a)
  -- lower bound: at least n − r non-owners, each priced ≥ 1
  have hOcard : O.card ≤ r := le_trans Finset.card_image_le (by simp)
  have hcards : O.card + G.card = n := by
    have h := Finset.card_add_card_compl O
    simp only [Fintype.card_fin] at h
    exact h
  have hGcard : (n : ℝ) - (r : ℝ) ≤ (G.card : ℝ) := by
    have h1 : (O.card : ℝ) ≤ (r : ℝ) := by exact_mod_cast hOcard
    have h2 : (O.card : ℝ) + (G.card : ℝ) = (n : ℝ) := by exact_mod_cast hcards
    linarith
  have hlower : (G.card : ℝ) ≤ ∑ i ∈ G, massIn atoms (Q i) := by
    calc (G.card : ℝ) = ∑ _i ∈ G, (1 : ℝ) := by simp
      _ ≤ ∑ i ∈ G, massIn atoms (Q i) := Finset.sum_le_sum hprice
  linarith

/-- **Lemma B, priced form** (empty `nofams`): (P1) + (P2) refute every strict family
realising the core-containment hypothesis — the `hcert` input of `lemma_B`, now derived
inside Lean from the frozen certificate claims. -/
theorem hcert_of_priced {n r : ℕ} {s'' : ℝ} (atoms : List IAtom)
    (hw : ∀ a ∈ atoms, 0 ≤ a.w)
    {K : Fin r → Set RP} {own : Fin r → Fin n}
    (price : ∀ S : Set RP, IsUnitSquare S → S ⊆ container s'' →
      (∀ j, Disjoint S (K j)) → 1 ≤ massIn atoms S)
    (hP1 : (atoms.map fun a => (a.w : ℝ)).sum < (n : ℝ) - (r : ℝ))
    {Q : Fin n → Set RP} (hQ : IsStrictFamily n s'' Q)
    (hH : ∀ j, K j ⊆ Q (own j)) : False := by
  obtain ⟨i, -, hfalse⟩ := priced_dichotomy atoms hw (fun _ => False)
    (fun S h1 h2 h3 _ => price S h1 h2 h3) hP1 hQ hH
  exact hfalse

/-! ## Axis-aligned squares -/

private theorem cosT_zero' : cosT 0 = 1 := by norm_num [cosT]

private theorem sinT_zero' : sinT 0 = 0 := by norm_num [sinT]

private theorem cosT_one' : cosT 1 = 0 := by norm_num [cosT]

private theorem sinT_one' : sinT 1 = 1 := by norm_num [sinT]

/-- At `t = 0` the square is the closed axis-aligned box of half-side `1/2` about the
centre. -/
theorem set_of_t_zero {q : PSq} (h : q.t = 0) :
    q.set = Icc (q.cx - 1 / 2) (q.cx + 1 / 2) ×ˢ Icc (q.cy - 1 / 2) (q.cy + 1 / 2) := by
  ext p
  rw [mem_set_iff_uv]
  simp only [edir, perpV, rdot, h, cosT_zero', sinT_zero', mul_one, mul_zero, add_zero,
    neg_zero, zero_add, mem_prod, mem_Icc, abs_le]
  constructor
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

/-- At `t = 1`, the same box (findings F8: `t = 0` and `t = 1` denote the same set). -/
theorem set_of_t_one {q : PSq} (h : q.t = 1) :
    q.set = Icc (q.cx - 1 / 2) (q.cx + 1 / 2) ×ˢ Icc (q.cy - 1 / 2) (q.cy + 1 / 2) := by
  ext p
  rw [mem_set_iff_uv]
  simp only [edir, perpV, rdot, h, cosT_one', sinT_one', mul_one, mul_zero, add_zero,
    zero_add, mul_neg, mem_prod, mem_Icc, abs_le, abs_neg]
  constructor
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩
  · rintro ⟨⟨h1, h2⟩, h3, h4⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

/-- Strict coordinate bounds put a point in the interior of an axis-aligned square. -/
theorem strict_mem_interior_of_t_zero {q : PSq} (h : q.t = 0) {p : RP}
    (hx : |p.1 - q.cx| < 1 / 2) (hy : |p.2 - q.cy| < 1 / 2) : p ∈ interior q.set := by
  apply strict_uv_mem_interior
  · simpa only [edir, rdot, h, cosT_zero', sinT_zero', mul_one, mul_zero, add_zero] using hx
  · simpa only [edir, perpV, rdot, h, cosT_zero', sinT_zero', mul_one, mul_zero, add_zero,
      neg_zero, zero_add] using hy

/-! ## Corollary B′: hypothesis (H) from the margin condition (H′) -/

/-- **Corollary B′, containment step** (`closed_disjoint_bridge.md` B.2).  Slot
coordinates `α_x + β_x·s`, `α_y + β_y·s`; pin square axis-aligned at the side-`m` slot;
core `K` inside the closed axis box of half-side `1/2 − ρ` centred at the side-`s″` slot
(the core's axis-parallel bounding box, `ρ` the containment margin).  If (H′)
`(λ−1)·|α| < ρ` holds on both axes, `K` lies in the INTERIOR of the dilated pin square —
hypothesis (H) of `lemma_B`. -/
theorem bprime_containment {lam m s'' ax bx ay by' rho : ℝ} {K : Set RP}
    (hlam : 1 < lam) (hs : s'' = lam * m)
    (hax : (lam - 1) * |ax| < rho) (hay : (lam - 1) * |ay| < rho)
    (hK : K ⊆ Icc (ax + bx * s'' - (1 / 2 - rho)) (ax + bx * s'' + (1 / 2 - rho)) ×ˢ
      Icc (ay + by' * s'' - (1 / 2 - rho)) (ay + by' * s'' + (1 / 2 - rho))) :
    K ⊆ interior ((scaleC lam (⟨ax + bx * m, ay + by' * m, 0⟩ : PSq)).set) := by
  have hl1 : (0 : ℝ) < lam - 1 := by linarith
  have hdx : |(lam - 1) * ax| < rho := by
    rwa [abs_mul, abs_of_pos hl1]
  have hdy : |(lam - 1) * ay| < rho := by
    rwa [abs_mul, abs_of_pos hl1]
  rw [abs_lt] at hdx hdy
  intro p hp
  obtain ⟨⟨hx1, hx2⟩, hy1, hy2⟩ := hK hp
  have hex : lam * (ax + bx * m) = ax + bx * s'' + (lam - 1) * ax := by
    rw [hs]; ring
  have hey : lam * (ay + by' * m) = ay + by' * s'' + (lam - 1) * ay := by
    rw [hs]; ring
  have hbx : |p.1 - lam * (ax + bx * m)| < 1 / 2 := by
    rw [hex, abs_lt]
    constructor <;> linarith
  have hby : |p.2 - lam * (ay + by' * m)| < 1 / 2 := by
    rw [hey, abs_lt]
    constructor <;> linarith
  exact strict_mem_interior_of_t_zero rfl hbx hby

/-! ## Lemma B-NO bookkeeping (B.2″): the pulled-back `nofams` zone -/

/-- A zone coordinate of the dilated family, pulled back by `1/λ`, lands in the
outward-widened interval `[x₀ − (λ−1)·x₁, x₁]` (for `0 ≤ x₀ ≤ x₁`, `λ ≥ 1`).  Downstream
consumers of a confinement conclusion must hypothesise this widening
(`closed_disjoint_bridge.md` B.2″). -/
theorem pullback_mem_Icc {lam x0 x1 c : ℝ} (hlam : 1 ≤ lam) (h0 : 0 ≤ x0) (h01 : x0 ≤ x1)
    (hc : lam * c ∈ Icc x0 x1) : c ∈ Icc (x0 - (lam - 1) * x1) x1 := by
  obtain ⟨hc1, hc2⟩ := hc
  have hx1 : (0 : ℝ) ≤ x1 := le_trans h0 h01
  have hup : c ≤ x1 := by
    rcases le_or_gt 0 c with h | h
    · nlinarith [mul_nonneg (sub_nonneg.mpr hlam) h]
    · linarith
  refine ⟨?_, hup⟩
  nlinarith [mul_le_mul_of_nonneg_left hup (sub_nonneg.mpr hlam)]

end

end S11
end PackingCert
