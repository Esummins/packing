import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.Attain
import PackingCertMathlib.Dilation
import PackingCertMathlib.CaseBridge
import PackingCertMathlib.TopLevel

/-!
# Zone lemmas: centre separation, zone-assignment collapse, the logic-kill rules, and
single-corner window transfer (A75, depgraph nodes D.N1, C.T5T11, C.M1)

* **D.N1** (`docs/proofs/occupancy_collapse.md`): Lemma N1.0 (centre separation — distinct
  squares of a packing have centres at distance ≥ 1, via the inscribed disk of radius 1/2)
  → Corollary N1.0.1 (a set of diameter < 1 holds at most one centre) → Lemma N1 (zone
  assignment is injective and unique; bijective for 11 zones).  All proved
  (`centre_separation`, `at_most_one_centre`, `zone_assign_injective`,
  `zone_assign_unique`, `zone_assign_bijective`).
* **C.T5T11** (`attempts/A57-shadow-trees/notes/lemmas.md` T5/T11): the two logic rules of
  the shadow trees.  T5 "contradictory": if the child's core meets a pin's core, the
  child's witnessing square IS the pinned square (`core_meet_same_square`), so a witness
  distinct from the pins cannot exist and the child is empty by logic; the "parent"
  classification (a pin placement inside the box) is precisely the case where this
  identification is consistent, i.e. where the reduced budget would be unsound — recorded
  in the docstring, not a theorem (it is a gate on which children may be certified).
  T11 "refinement": covering a box by closed sub-boxes refines the same disjunction with the
  same witness (`refine_cover`) — no new branch, no budget change.
* **C.M1** (`attempts/A56-sparametric/notes/soundness.md` M1): a kill whose cores are all
  anchored to one container corner (WLOG bottom-left after D4: the cores are then the SAME
  sets at every side) transfers to every side `s ≤ s₀` for free — the identity embedding
  `[0,s]² ⊆ [0,s₀]²` keeps a strict family strict (`strictFamily_mono`), so the s₀ case
  certificate kills at every smaller side (`M1_transfer`, `M1_transfer_packing`).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set CaseI

/-! ## D.N1: centre separation -/

/-- The centre `(cx, cy)` of a parametrised square. -/
def centre (q : PSq) : RP := (q.cx, q.cy)

/-- The `u/v` coordinates of a point relative to the centre are an isometry: `u² + v² =`
squared distance to the centre. -/
theorem uv_sq_add (q : PSq) (p : RP) :
    rdot (p.1 - q.cx, p.2 - q.cy) (edir q) ^ 2
      + rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q)) ^ 2 = sqdist p (centre q) := by
  simp only [rdot, edir, perpV, sqdist, centre]
  linear_combination ((p.1 - q.cx) ^ 2 + (p.2 - q.cy) ^ 2) * cosT_sq_add_sinT_sq q.t

/-- The closed disk of radius `1/2` about the centre lies in the square (inradius). -/
theorem mem_set_of_sqdist_le (q : PSq) {p : RP} (h : sqdist p (centre q) ≤ 1 / 4) :
    p ∈ q.set := by
  rw [mem_set_iff_uv]
  have hid := uv_sq_add q p
  have hu2 : rdot (p.1 - q.cx, p.2 - q.cy) (edir q) ^ 2 ≤ (1 / 2) ^ 2 := by nlinarith
  have hv2 : rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q)) ^ 2 ≤ (1 / 2) ^ 2 := by nlinarith
  exact ⟨abs_le_of_sq_le_sq hu2 (by norm_num), abs_le_of_sq_le_sq hv2 (by norm_num)⟩

/-- The open disk of radius `1/2` about the centre lies in the interior of the square. -/
theorem mem_interior_of_sqdist_lt (q : PSq) {p : RP} (h : sqdist p (centre q) < 1 / 4) :
    p ∈ interior q.set := by
  rw [mem_interior_iff_uv]
  have hid := uv_sq_add q p
  have hu2 : rdot (p.1 - q.cx, p.2 - q.cy) (edir q) ^ 2 < (1 / 2) ^ 2 := by nlinarith
  have hv2 : rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q)) ^ 2 < (1 / 2) ^ 2 := by nlinarith
  exact ⟨abs_lt_of_sq_lt_sq hu2 (by norm_num), abs_lt_of_sq_lt_sq hv2 (by norm_num)⟩

/-- **Lemma N1.0 (centre separation).**  Interior-disjoint unit squares have centres at
squared distance `≥ 1`: otherwise the midpoint of the centres lies in both open inscribed
disks. -/
theorem centre_separation {q q' : PSq}
    (hd : Disjoint (interior q.set) (interior q'.set)) :
    1 ≤ sqdist (centre q) (centre q') := by
  by_contra hlt
  rw [not_le] at hlt
  set p : RP := ((q.cx + q'.cx) / 2, (q.cy + q'.cy) / 2) with hp
  have h1 : sqdist p (centre q) < 1 / 4 := by
    simp only [sqdist, centre, hp] at hlt ⊢
    nlinarith
  have h2 : sqdist p (centre q') < 1 / 4 := by
    simp only [sqdist, centre, hp] at hlt ⊢
    nlinarith
  exact Set.disjoint_left.mp hd (mem_interior_of_sqdist_lt q h1)
    (mem_interior_of_sqdist_lt q' h2)

/-- **Corollary N1.0.1 (at most one).**  A set of squared diameter `< 1` contains the
centre of at most one square of a packing. -/
theorem at_most_one_centre {s : ℝ} {z : Cfg} (hz : CfgPacking s z) {Z : Set RP}
    (hZ : ∀ p ∈ Z, ∀ p' ∈ Z, sqdist p p' < 1) {i j : Fin 11}
    (hi : centre (z i) ∈ Z) (hj : centre (z j) ∈ Z) : i = j := by
  by_contra hij
  have hd := hz.2.interiorDisjoint i j hij
  have := centre_separation hd
  have := hZ _ hi _ hj
  linarith

/-! ## D.N1: zone-assignment collapse -/

/-- **Lemma N1 (ii), injectivity.**  Zones with pairwise-disjoint footprints of squared
diameter `< 1`, each holding the centre of the square it is assigned: the assignment is
injective. -/
theorem zone_assign_injective {s : ℝ} {z : Cfg} (hz : CfgPacking s z) {m : ℕ}
    (R : Fin m → Set RP) (hdis : ∀ j j', j ≠ j' → Disjoint (R j) (R j'))
    (σ : Fin m → Fin 11) (hσ : ∀ j, centre (z (σ j)) ∈ R j) :
    Function.Injective σ := by
  intro j j' h
  by_contra hjj
  have h1 := hσ j
  have h2 := hσ j'
  rw [h] at h1
  exact Set.disjoint_left.mp (hdis j j' hjj) h1 h2

/-- **Lemma N1 (i)+(ii), uniqueness.**  Any two assignments compatible with small-diameter
footprints agree: the labelled hypothesis "square `j` lies in zone `j`" has a unique
representative.  (No pigeonhole, no disjointness of the footprints needed here — pure
centre separation.) -/
theorem zone_assign_unique {s : ℝ} {z : Cfg} (hz : CfgPacking s z) {m : ℕ}
    (R : Fin m → Set RP) (hsmall : ∀ j, ∀ p ∈ R j, ∀ p' ∈ R j, sqdist p p' < 1)
    (σ σ' : Fin m → Fin 11) (hσ : ∀ j, centre (z (σ j)) ∈ R j)
    (hσ' : ∀ j, centre (z (σ' j)) ∈ R j) : σ = σ' := by
  funext j
  exact at_most_one_centre hz (hsmall j) (hσ j) (hσ' j)

/-- **Lemma N1 (iii).**  Eleven pairwise-disjoint zones: the assignment is a bijection —
every square of the packing is the unique witness of exactly one zone. -/
theorem zone_assign_bijective {s : ℝ} {z : Cfg} (hz : CfgPacking s z)
    (R : Fin 11 → Set RP) (hdis : ∀ j j', j ≠ j' → Disjoint (R j) (R j'))
    (σ : Fin 11 → Fin 11) (hσ : ∀ j, centre (z (σ j)) ∈ R j) :
    Function.Bijective σ :=
  Finite.injective_iff_bijective.mp (zone_assign_injective hz R hdis σ hσ)

/-! ## C.T5T11: the logic-kill rules of the shadow trees -/

/-- **T5 (`contradictory` boxes).**  Cores realised in the interiors of two members of a
packing that meet each other force the two members to be the SAME square.  In the tree
semantics a YES child's core `K_B` is contained in every square with parameters in the
child box `B`; if `K_B` meets a pin's core `K_pin ⊆ interior (Q_pin)`, every witness of
the child IS the pinned square — so a witness distinct from the `k` pins (what the
reduced budget `11 − k − 1` accounts for) cannot exist: the child is empty by logic.
(The `parent` classification — a pin placement inside `B` — is the case in which this
identification is consistent and the reduced-budget certification would be UNSOUND;
`pinguard.py` refuses to certify such children.  That is a gate, not a lemma.) -/
theorem core_meet_same_square {n : ℕ} {s : ℝ} {Q : Fin n → Set RP} (hP : IsPacking n s Q)
    {i j : Fin n} {K K' : Set RP} (hK : K ⊆ interior (Q i)) (hK' : K' ⊆ interior (Q j))
    (hne : (K ∩ K').Nonempty) : i = j := by
  by_contra hij
  obtain ⟨p, hpK, hpK'⟩ := hne
  exact Set.disjoint_left.mp (hP.interiorDisjoint i j hij) (hK hpK) (hK' hpK')

/-- **T11 (refinement).**  Replacing a box `B` by a closed cover `⋃ C_l ⊇ B` refines the
disjunction "some square has parameters in `B`" into "some square has parameters in some
`C_l`" with the SAME witness — hence the same budget, no new branch. -/
theorem refine_cover {α ι : Type*} {B : Set α} {C : ι → Set α} (hcov : B ⊆ ⋃ l, C l)
    {W : Type*} (param : W → α) (P : W → Prop)
    (h : ∃ w, P w ∧ param w ∈ B) : ∃ l, ∃ w, P w ∧ param w ∈ C l := by
  obtain ⟨w, hw, hB⟩ := h
  obtain ⟨l, hl⟩ := Set.mem_iUnion.mp (hcov hB)
  exact ⟨l, w, hw, hl⟩

/-! ## C.M1: single-corner transfer down the window -/

theorem container_mono {s s' : ℝ} (h : s ≤ s') : container s ⊆ container s' := by
  intro p hp
  simp only [container, mem_prod, mem_Icc] at hp ⊢
  exact ⟨⟨hp.1.1, le_trans hp.1.2 h⟩, hp.2.1, le_trans hp.2.2 h⟩

/-- A strict family at side `s` is a strict family at every side `s' ≥ s` (identity
embedding, bottom-left corners flush). -/
theorem strictFamily_mono {n : ℕ} {s s' : ℝ} (h : s ≤ s') {Q : Fin n → Set RP}
    (hQ : IsStrictFamily n s Q) : IsStrictFamily n s' Q where
  unit := hQ.unit
  contained i := (hQ.contained i).trans (container_mono h)
  disjoint := hQ.disjoint

/-- **M1 (single-corner transfer is free).**  A case certificate at side `s₀` whose cores
are all anchored to the bottom-left corner — so that the pin squares of the class are the
SAME sets `coreSet K` at every side (the `β = 0` slots; any other single corner reduces to
this by D4) — kills the class at every side `s ≤ s₀`: a strict family at side `s` with
owners containing the cores is one at side `s₀`. -/
theorem M1_transfer {c : CCertI} (h : checkCaseI c = true) (hno : c.nofams = [])
    {s : ℝ} (hs : s ≤ caseSide c)
    {Q : Fin c.n → Set RP} (hQ : IsStrictFamily c.n s Q)
    (own : Fin c.cores.length → Fin c.n)
    (hown : ∀ j : Fin c.cores.length, coreSet (c.cores.get j) ⊆ Q (own j)) : False :=
  checkCaseI_kill h hno (strictFamily_mono hs hQ) own hown

/-- M1 in the λ-dilated packing form: an interior-disjoint packing at any side
`m < s₀/λ`… precisely, at side `m` with `λ·m ≤ s₀`, cannot realise the dilated
core-containment hypothesis. -/
theorem M1_transfer_packing {c : CCertI} (hn : c.n = 11) (h : checkCaseI c = true)
    (hno : c.nofams = []) {m lam : ℝ} (hlam : 1 < lam) (hs : lam * m ≤ caseSide c)
    {z : Fin 11 → PSq} (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (hP : IsPacking 11 m fun i => (z i).set)
    (own : Fin c.cores.length → Fin 11)
    (hH : ∀ j : Fin c.cores.length, coreSet (c.cores.get j)
        ⊆ interior ((scaleC lam (z (own j))).set)) : False := by
  rcases c with ⟨n, sNum, sDen, wd, depth, atoms, cores, nofams⟩
  have hn' : n = 11 := hn
  subst hn'
  exact lemma_B hlam rfl ht hP (fun j => coreSet (cores.get j)) own
    (fun _Q hQ hI => M1_transfer h hno hs hQ own (fun j => (hI j).trans interior_subset)) hH

end

end S11
end PackingCert
