import PackingCertMathlib.TubeSeam
import PackingCertMathlib.AtlasBridge
import PackingCertMathlib.Zones
import PackingCertMathlib.UniqueChain

/-!
# The zone-tree composition theorem (A86 T3 — Lemma P-TREE / Lemma SEAM, generic form)

`docs/proofs/protected_trees.md` §2 (Lemma P-TREE), `docs/proofs/contraction_tube.md` §4
(Lemma SEAM), `docs/proofs/k0_route.md` §4.3 (Lemma K0-ATLAS), `docs/proofs/cover_invariance.md`
(CI-1/2/3) — the ONE generic statement every residual-tree campaign instantiates.

## The shape

A tree at the tree side `s0` is consumed through its LEAVES only.  A closed tree
(`ClosedTree s0 tc Root`) is a finite list of leaves, each a `Leaf` kind with a hypothesis on
the dilated family `F = Δ_{s0/m} P`, such that

* `cover`  — every family satisfying the root hypothesis satisfies some leaf hypothesis
  (the complete disjunction: this is where the tree's branching rules live — closed covers
  of zones by boxes (`zone_cover`, `refine_cover`), the T5 identification rule, Lemma PD —
  and it is the producer's per-tree obligation, discharged from the rule library below);
* `(K)`    — a `case-lp-certificate-v1` PASS at side `s0` (`checkCaseI`), whose cores are
  contained in the designated owners and whose NO-families are avoided by every non-owner
  (`NodeHypC`); nonempty `nofams` (the confinement / (N) leaves) are handled by the SAME
  clause — `checkCaseI_no_family` produces an exempt non-owner, which the node hypothesis
  forbids (Lemma B-NO with no widening: the hypothesis is about `F` itself);
* `(C)`    — the hypothesis is empty (a logic kill);
* `(D)`    — the landing: after a container symmetry `g` and a relabelling, the packing
  lies in the tube at depth `ŝ − m` (Lemma SEAM's map, `seam_inTube`; `D.S6`'s mod-`G`
  clause is the commutation `d4_dil_comm`);
* `(D′)`   — an atlas box with `L ≥ s0` contains the tilt-FOLDED `F` (`atlas_dilated_kill_fold`;
  the emitted boxes live at `θ ∈ [0, π/4]`, `AtlasBridge.lean`).

`tree_kill`: for every side `m ∈ [ŝ − T, ŝ]` and every packing `P` at side `m` whose dilate
satisfies the root hypothesis, `m ≥ ŝ`, and at `m = ŝ` the packing is a `D4`-image of `ẑ`
after relabelling (Lemma P-TREE (a) + (b), with `ŝ = ŝ_A22`).  Nothing about EXACT skeletons
enters; the class hypothesis enters only through `Root` (Step 1, `root_of_containsPins`:
the slack pin cores at `slots(s0)` sit inside the dilated pin squares when `(λ − 1)·A < ρ`).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set Rigid Atlas CaseI

/-! ## The dilated family and the node hypotheses -/

/-- The `Δ_{s0/m}`-dilate of a configuration. -/
def dil (s0 m : ℝ) (P : Cfg) : Cfg := fun i => scaleC (s0 / m) (P i)

/-- A set avoids every NO-zone: no parametrisation of it (with `t ∈ [0,1]`) lies in a zone. -/
def NoZoneSet (fs : List CNoFam) (S : Set RP) : Prop :=
  ∀ q : PSq, q.t ∈ Icc (0 : ℝ) 1 → S = q.set → ∀ f ∈ fs, ¬ InZone f q

/-- The node hypothesis carried by a case certificate: designated (not necessarily
distinct) owners contain the cores; every non-owner avoids every NO-family. -/
def NodeHypC (c : CCertI) (F : Cfg) : Prop :=
  ∃ own : Fin c.cores.length → Fin 11,
    (∀ j, coreSet (c.cores.get j) ⊆ (F (own j)).set) ∧
    ∀ i, (∀ j, own j ≠ i) → NoZoneSet c.nofams (F i).set

/-- **The (K)/(N) leaf**: a PASS at side `s0` refutes every strict family at `s0` satisfying
its node hypothesis (`checkCaseI_no_family` + the NO-zone clause). -/
theorem kleaf_kill {c : CCertI} (hn : c.n = 11) (h : checkCaseI c = true) {s0 : ℝ}
    (hs : caseSide c = s0) {F : Cfg} (hF : IsStrictFamily 11 s0 fun i => (F i).set)
    (hnode : NodeHypC c F) : False := by
  obtain ⟨own, hown, hno⟩ := hnode
  rcases c with ⟨n, sNum, sDen, wd, depth, atoms, cores, nofams⟩
  have hn' : n = 11 := hn
  subst hn'
  simp only at hs hown hno ⊢
  rw [← hs] at hF
  obtain ⟨i, hi, hex⟩ := checkCaseI_no_family h hF own hown
  obtain ⟨q, hqt, hqs, f, hf, hz⟩ := hex
  exact hno i hi q hqt hqs f hf hz

/-- The dilate of a packing at side `m < s0` is a strict family at `s0`. -/
theorem dil_strict {s0 m : ℝ} (hm : 0 < m) (hms : m < s0) {P : Cfg} (hP : CfgPacking m P) :
    IsStrictFamily 11 s0 fun i => (dil s0 m P i).set := by
  have hlam : 1 < s0 / m := by rw [lt_div_iff₀ hm]; linarith
  have := dilation_bridge hlam hP.1 hP.2
  have e : s0 / m * m = s0 := by field_simp
  rw [e] at this
  exact this

/-! ## Leaves and closed trees -/

/-- The four leaf kinds. -/
inductive Leaf
  | K (c : CCertI)
  | C
  | D (g : D4)
  | D' (a : AtlasCert)

/-- **A closed zone-tree** over the root hypothesis `Root` (on the `s0` family), consumed
through the tube certificate `tc`. -/
structure ClosedTree (s0 : ℝ) (tc : TubeCert) (Root : Cfg → Prop) where
  leaves : List (Leaf × (Cfg → Prop))
  cover : ∀ F : Cfg, Root F → ∃ ls ∈ leaves, ls.2 F
  kOK : ∀ ls ∈ leaves, ∀ c : CCertI, ls.1 = Leaf.K c →
    checkCaseI c = true ∧ c.n = 11 ∧ caseSide c = s0 ∧ ∀ F, ls.2 F → NodeHypC c F
  cOK : ∀ ls ∈ leaves, ls.1 = Leaf.C → ∀ F, ¬ ls.2 F
  dOK : ∀ ls ∈ leaves, ∀ g : D4, ls.1 = Leaf.D g →
    ∀ (P : Cfg) (m : ℝ), shatR - (tc.T : ℝ) ≤ m → m ≤ shatR → CfgPacking m P →
      ls.2 (dil s0 m P) →
      ∃ (e : Equiv.Perm (Fin 11)) (Q : Cfg),
        (∀ j, (Q j).set = (d4Cfg m g P (e j)).set) ∧ (∀ j, (Q j).t ∈ Icc (0 : ℝ) 1) ∧
        InTube zhatVec (vR tc) tc.T (radR tc) (mkVec Q m)
  d'OK : ∀ ls ∈ leaves, ∀ a : AtlasCert, ls.1 = Leaf.D' a →
    checkAtlas a = true ∧ s0 ≤ (a.L : ℝ) ∧ ∀ F, ls.2 F → InAtlas a fun i => foldSq (F i)

/-- `P` is a `D4`-image of `ẑ` after relabelling, at side `m` (the conclusion of Lemma
P-TREE (b); at `m = ŝ` this is TopLevel's `IsTrumpImage`). -/
def IsImageAt (m : ℝ) (P : Cfg) : Prop :=
  ∃ (f : RP → RP) (e : Equiv.Perm (Fin 11)), IsCtrSym m f ∧ ∀ j, (P (e j)).set = f '' (zhatCfg j).set

/-- A configuration with the same sets as a packing (relabelled) is a packing. -/
theorem packing_of_sets {m : ℝ} {P Q : Cfg} (e : Equiv.Perm (Fin 11)) (hP : CfgPacking m P)
    (hQs : ∀ j, (Q j).set = (P (e j)).set) (hQt : ∀ j, (Q j).t ∈ Icc (0 : ℝ) 1) :
    CfgPacking m Q := by
  refine ⟨hQt, ⟨fun i => psq_isUnitSquare _, fun i => ?_, fun i j hij => ?_⟩⟩
  · rw [hQs]; exact hP.2.contained _
  · rw [hQs, hQs]
    exact hP.2.interiorDisjoint _ _ (fun h => hij (e.injective h))

/-- **The zone-tree composition theorem (Lemma P-TREE (a)+(b), Lemma SEAM).** -/
theorem tree_kill {s0 : ℝ} {tc : TubeCert} {Root : Cfg → Prop} (T : ClosedTree s0 tc Root)
    (ht : checkTube Data.a22 tc = true) (hs0 : shatR < s0)
    {m : ℝ} (hm1 : shatR - (tc.T : ℝ) ≤ m) (hm2 : m ≤ shatR) (hm0 : 0 < m)
    {P : Cfg} (hP : CfgPacking m P) (hroot : Root (dil s0 m P)) :
    shatR ≤ m ∧ (m = shatR → IsImageAt m P) := by
  have hms : m < s0 := lt_of_le_of_lt hm2 hs0
  have hF := dil_strict hm0 hms hP
  obtain ⟨ls, hls, hleaf⟩ := T.cover _ hroot
  rcases hkind : ls.1 with c | _ | g | a
  · -- (K)/(N)
    obtain ⟨hc, hn, hs, hnode⟩ := T.kOK ls hls c hkind
    exact absurd (hnode _ hleaf) (fun hnd => kleaf_kill hn hc hs hF hnd)
  · -- (C)
    exact absurd hleaf (T.cOK ls hls hkind _)
  · -- (D)
    obtain ⟨e, Q, hQs, hQt, hQtube⟩ := T.dOK ls hls g hkind P m hm1 hm2 hP hleaf
    have hgP := d4_packing (s := m) g hP.1 hP.2
    have hQ : CfgPacking m Q := packing_of_sets e ⟨hgP.1, hgP.2⟩ hQs hQt
    obtain ⟨h1, h2⟩ := tube_tframe ht Q m hQtube hQ.2
    refine ⟨h1, fun hm => ?_⟩
    have hQz := h2 hm
    refine ⟨d4Apply m g.inv, e, isCtrSym_d4Apply m g.inv, fun j => ?_⟩
    have := hQs j
    rw [hQz, d4Cfg_set g hP.1] at this
    rw [this, Set.image_image]
    have hid : (fun x => d4Apply m g.inv (d4Apply m g x)) = id := by
      funext x; exact d4Apply_inv_apply m g x
    rw [hid, Set.image_id]
  · -- (D′)
    obtain ⟨ha, hL, hin⟩ := T.d'OK ls hls a hkind
    exact absurd (hin _ hleaf) (fun h => atlas_dilated_kill_fold ha hL hm0 hms hP.1 hP.2 h)

/-! ## Step 1: the class hypothesis feeds the root (slack pin cores inside the dilated pins) -/

/-- A square occupying a slot has that centre and an axis-aligned parametrisation. -/
theorem occupiesSlot_params {q : PSq} {c : RP} (ht : q.t ∈ Icc (0 : ℝ) 1) (h : OccupiesSlot q c) :
    q.cx = c.1 ∧ q.cy = c.2 ∧ (q.t = 0 ∨ q.t = 1) := by
  rw [OccupiesSlot] at h
  -- the inscribed disk of radius ½ lies in the box: the centre is `c`
  have hdisk : ∀ p : RP, sqdist p (centre q) ≤ 1 / 4 →
      c.1 - 1 / 2 ≤ p.1 ∧ p.1 ≤ c.1 + 1 / 2 ∧ c.2 - 1 / 2 ≤ p.2 ∧ p.2 ≤ c.2 + 1 / 2 := by
    intro p hp
    have := mem_set_of_sqdist_le q hp
    rw [h] at this
    simp only [mem_prod, mem_Icc] at this
    exact ⟨this.1.1, this.1.2, this.2.1, this.2.2⟩
  have hx1 := hdisk (q.cx + 1 / 2, q.cy) (by simp [sqdist, centre]; norm_num)
  have hx2 := hdisk (q.cx - 1 / 2, q.cy) (by simp [sqdist, centre]; norm_num)
  have hy1 := hdisk (q.cx, q.cy + 1 / 2) (by simp [sqdist, centre]; norm_num)
  have hy2 := hdisk (q.cx, q.cy - 1 / 2) (by simp [sqdist, centre]; norm_num)
  have hcx : q.cx = c.1 := by linarith [hx1.2.1, hx2.1]
  have hcy : q.cy = c.2 := by linarith [hy1.2.2.2, hy2.2.2.1]
  refine ⟨hcx, hcy, ?_⟩
  -- the corner `c + (½, ½)` lies in the square: `cos + sin ≤ 1`
  have hcorner : (c.1 + 1 / 2, c.2 + 1 / 2) ∈ q.set := by
    rw [h]; simp only [mem_prod, mem_Icc]
    exact ⟨⟨by linarith, le_rfl⟩, by linarith, le_rfl⟩
  rw [mem_set_iff_uv] at hcorner
  obtain ⟨hu, -⟩ := hcorner
  simp only [rdot, edir, hcx, hcy] at hu
  have hu' : (1 / 2 : ℝ) * cosT q.t + 1 / 2 * sinT q.t ≤ 1 / 2 := by
    have := (abs_le.mp hu).2
    linarith
  have hc0 := cosT_nonneg ht.1 ht.2
  have hs0 := sinT_nonneg ht.1
  have hcs := cosT_sq_add_sinT_sq q.t
  have hprod : cosT q.t * sinT q.t = 0 := by nlinarith
  rcases mul_eq_zero.mp hprod with hc | hs
  · right
    have h1 := one_add_sq_pos q.t
    have : 1 - q.t ^ 2 = 0 := by
      unfold cosT at hc
      rcases div_eq_zero_iff.mp hc with h | h
      · exact h
      · exact absurd h h1.ne'
    nlinarith [ht.1]
  · left
    have h1 := one_add_sq_pos q.t
    unfold sinT at hs
    rcases div_eq_zero_iff.mp hs with h | h
    · linarith
    · exact absurd h h1.ne'

/-- The slot's affine data `α + β·s` per axis (`β ∈ {0, 1}`, `A56 P1`). -/
def slotAX (a : Slot) : ℝ := if cornerR a.corner then -((a.cellx : ℝ) + 1 / 2) else (a.cellx : ℝ) + 1 / 2
def slotBX (a : Slot) : ℝ := if cornerR a.corner then 1 else 0
def slotAY (a : Slot) : ℝ := if cornerT a.corner then -((a.celly : ℝ) + 1 / 2) else (a.celly : ℝ) + 1 / 2
def slotBY (a : Slot) : ℝ := if cornerT a.corner then 1 else 0

theorem slotCentre_affine (s : ℝ) (a : Slot) :
    slotCentre s a = (slotAX a + slotBX a * s, slotAY a + slotBY a * s) := by
  rw [slotCentre_eq]
  simp only [slotX, slotAX, slotBX, slotAY, slotBY]
  split_ifs <;> simp only [Prod.mk.injEq] <;> constructor <;> ring

theorem slotBX_cases (a : Slot) : slotBX a = 0 ∨ slotBX a = 1 := by
  unfold slotBX; split_ifs <;> simp

theorem slotBY_cases (a : Slot) : slotBY a = 0 ∨ slotBY a = 1 := by
  unfold slotBY; split_ifs <;> simp

/-- The dilate of a slot-occupying square is the axis-aligned unit square at `λ·c`. -/
theorem dil_slot_set {lam : ℝ} {q : PSq} {c : RP} (ht : q.t ∈ Icc (0 : ℝ) 1)
    (h : OccupiesSlot q c) :
    (scaleC lam q).set = (scaleC lam (⟨c.1, c.2, 0⟩ : PSq)).set := by
  obtain ⟨hx, hy, ht01⟩ := occupiesSlot_params ht h
  rcases ht01 with h0 | h1
  · rw [set_of_t_zero (q := scaleC lam q) h0, set_of_t_zero (q := scaleC lam ⟨c.1, c.2, 0⟩) rfl]
    simp only [scaleC, hx, hy]
  · rw [set_of_t_one (q := scaleC lam q) h1, set_of_t_zero (q := scaleC lam ⟨c.1, c.2, 0⟩) rfl]
    simp only [scaleC, hx, hy]

/-- **Step 1 (Lemma P-TREE / Corollary B′).**  A packing at side `m < s0` containing the pin
set `S` (axis-aligned squares at `slots_S(m)`) has, after dilation to `s0`, every slack pin
core `K a` (inside the axis box of half-side `½ − ρ` about `slots_S(s0)`) in the INTERIOR of a
distinct dilated pin square, provided the drift budget `(λ − 1)·A < ρ` holds
(`A ≥ |α|` over the pin coordinates). -/
theorem root_of_containsPins {S : PinSet} {m s0 A rho : ℝ} (hm0 : 0 < m) (hms : m < s0)
    (hbudget : (s0 / m - 1) * A < rho)
    (hA : ∀ a ∈ S, |slotAX a| ≤ A ∧ |slotAY a| ≤ A)
    {P : Cfg} (hP : CfgPacking m P) (hpins : ContainsPins S m P)
    (K : Slot → Set RP)
    (hK : ∀ a ∈ S, K a ⊆ Icc (slotAX a + slotBX a * s0 - (1 / 2 - rho))
        (slotAX a + slotBX a * s0 + (1 / 2 - rho)) ×ˢ
      Icc (slotAY a + slotBY a * s0 - (1 / 2 - rho)) (slotAY a + slotBY a * s0 + (1 / 2 - rho))) :
    ∃ own : Slot → Fin 11, Set.InjOn own ↑S ∧
      ∀ a ∈ S, K a ⊆ interior ((dil s0 m P (own a)).set) := by
  obtain ⟨f, hinj, hocc⟩ := hpins
  refine ⟨f, hinj, fun a ha => ?_⟩
  have hlam : 1 < s0 / m := by rw [lt_div_iff₀ hm0]; linarith
  have hs : s0 = s0 / m * m := by field_simp
  obtain ⟨hAx, hAy⟩ := hA a ha
  have hbx : (s0 / m - 1) * |slotAX a| < rho :=
    lt_of_le_of_lt (mul_le_mul_of_nonneg_left hAx (by linarith)) hbudget
  have hby : (s0 / m - 1) * |slotAY a| < rho :=
    lt_of_le_of_lt (mul_le_mul_of_nonneg_left hAy (by linarith)) hbudget
  have hocc' := hocc a ha
  rw [slotCentre_affine] at hocc'
  unfold dil
  rw [dil_slot_set (hP.1 _) hocc']
  exact bprime_containment hlam hs hbx hby (hK a ha)

/-! ## `D4` commutes with dilation (D.S6's mod-`G` clause) -/

/-- `Δ_λ ∘ g_m = g_{λm} ∘ Δ_λ` on parametrised squares. -/
theorem d4Sq_scaleC (m lam : ℝ) (g : D4) (q : PSq) :
    scaleC lam (d4Sq m g q) = d4Sq (lam * m) g (scaleC lam q) := by
  obtain ⟨gs, gx, gy⟩ := g
  cases gs <;> cases gx <;> cases gy <;>
    simp only [scaleC, d4Sq, d4Apply, sg, Bool.false_eq_true, ↓reduceIte, PSq.mk.injEq] <;>
    refine ⟨by ring, by ring, ?_⟩ <;> first | trivial | rfl

/-- `Δ_{s0/m} (g·P) = g_{s0}·(Δ_{s0/m} P)`. -/
theorem d4_dil_comm {s0 m : ℝ} (hm : m ≠ 0) (g : D4) (P : Cfg) :
    dil s0 m (d4Cfg m g P) = d4Cfg s0 g (dil s0 m P) := by
  funext i
  simp only [dil, d4Cfg]
  rw [d4Sq_scaleC]
  congr 1
  field_simp

/-! ## The rule library for the cover obligation -/

/-- **Zone dichotomy (A57 T1)**: either no square is centred in the zone, or some square is. -/
theorem zone_dichotomy (F : Cfg) (Z : Set RP) :
    (∀ i, centre (F i) ∉ Z) ∨ ∃ i, centre (F i) ∈ Z := by
  by_cases h : ∃ i, centre (F i) ∈ Z
  · exact Or.inr h
  · left; intro i hi; exact h ⟨i, hi⟩

/-- **CI-1, the grid cover**: `n` equal cells cover `[lo, hi]` at every side (the cells are
affine in the endpoints, so this is the whole `s`-independence of the disjunction). -/
theorem grid_cover (n : ℕ) (hn : 0 < n) {lo hi x : ℝ} (hlo : lo ≤ x) (hhi : x ≤ hi) (hlh : lo < hi) :
    ∃ i : ℕ, i < n ∧ lo + ((i : ℝ) / n) * (hi - lo) ≤ x ∧ x ≤ lo + (((i : ℝ) + 1) / n) * (hi - lo) := by
  set u : ℝ := (x - lo) / (hi - lo) * n with hu
  have hd : 0 < hi - lo := by linarith
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hu0 : 0 ≤ u := by positivity
  have hu1 : u ≤ n := by
    rw [hu]
    have : (x - lo) / (hi - lo) ≤ 1 := by rw [div_le_one hd]; linarith
    nlinarith
  refine ⟨min (Nat.floor u) (n - 1), lt_of_le_of_lt (min_le_right _ _) (Nat.sub_one_lt hn.ne'), ?_, ?_⟩
  · -- lower end
    have hfl : ((min (Nat.floor u) (n - 1) : ℕ) : ℝ) ≤ u := by
      calc ((min (Nat.floor u) (n - 1) : ℕ) : ℝ) ≤ (Nat.floor u : ℝ) := by
            exact_mod_cast min_le_left _ _
        _ ≤ u := Nat.floor_le hu0
    have : ((min (Nat.floor u) (n - 1) : ℕ) : ℝ) / n * (hi - lo) ≤ x - lo := by
      rw [div_mul_eq_mul_div, div_le_iff₀ hn']
      have e : x - lo = u / n * (hi - lo) := by
        rw [hu]; field_simp
      rw [e, div_mul_eq_mul_div, div_mul_cancel₀ _ hn'.ne']
      exact mul_le_mul_of_nonneg_right hfl hd.le
    linarith
  · -- upper end
    have hfl : u ≤ ((min (Nat.floor u) (n - 1) : ℕ) : ℝ) + 1 := by
      rcases le_or_gt (Nat.floor u) (n - 1) with h | h
      · rw [min_eq_left h]; exact (Nat.lt_floor_add_one u).le
      · rw [min_eq_right h.le]
        have : ((n - 1 : ℕ) : ℝ) + 1 = n := by
          rw [Nat.cast_sub (by omega)]; push_cast; ring
        rw [this]; exact hu1
    have : x - lo ≤ (((min (Nat.floor u) (n - 1) : ℕ) : ℝ) + 1) / n * (hi - lo) := by
      rw [div_mul_eq_mul_div, le_div_iff₀ hn']
      have e : x - lo = u / n * (hi - lo) := by
        rw [hu]; field_simp
      rw [e, div_mul_eq_mul_div, div_mul_cancel₀ _ hn'.ne']
      exact mul_le_mul_of_nonneg_right hfl hd.le
    linarith

/-- **CI-3, pinguard-parent-freeness**: a slot with an outermost coordinate (`½` or
`s − ½`) has its centre outside the interior zone `[c0, s − c0]²` whenever `c0 > ½`. -/
theorem slot_outside_zone {s c0 : ℝ} (hc0 : 1 / 2 < c0) (a : Slot)
    (hedge : a.cellx = 0 ∨ a.celly = 0) :
    slotCentre s a ∉ Icc c0 (s - c0) ×ˢ Icc c0 (s - c0) := by
  rw [slotCentre_affine]
  simp only [mem_prod, mem_Icc, not_and, not_le]
  rcases hedge with h | h
  · intro hx _
    exfalso
    obtain ⟨hx1, hx2⟩ := hx
    simp only [slotAX, slotBX, h, Nat.cast_zero, zero_add] at hx1 hx2
    split_ifs at hx1 hx2 <;> linarith
  · intro _ hy1
    simp only [slotAY, slotBY, h, Nat.cast_zero, zero_add] at hy1 ⊢
    split_ifs at hy1 ⊢ <;> linarith

/-- The convexity used by Lemma PD: a segment between two points of a parametrised square
stays in it. -/
theorem psq_set_convex (q : PSq) {p p' : RP} (hp : p ∈ q.set) (hp' : p' ∈ q.set) {θ : ℝ}
    (h0 : 0 ≤ θ) (h1 : θ ≤ 1) :
    ((1 - θ) * p.1 + θ * p'.1, (1 - θ) * p.2 + θ * p'.2) ∈ q.set := by
  rw [mem_set_iff_uv] at hp hp' ⊢
  simp only [rdot, edir, perpV] at hp hp' ⊢
  obtain ⟨hu, hv⟩ := hp
  obtain ⟨hu', hv'⟩ := hp'
  rw [abs_le] at hu hv hu' hv'
  constructor
  · have e : ((1 - θ) * p.1 + θ * p'.1 - q.cx) * cosT q.t + ((1 - θ) * p.2 + θ * p'.2 - q.cy) * sinT q.t
        = (1 - θ) * ((p.1 - q.cx) * cosT q.t + (p.2 - q.cy) * sinT q.t)
          + θ * ((p'.1 - q.cx) * cosT q.t + (p'.2 - q.cy) * sinT q.t) := by ring
    rw [e, abs_le]
    constructor <;> nlinarith [hu.1, hu.2, hu'.1, hu'.2]
  · have e : ((1 - θ) * p.1 + θ * p'.1 - q.cx) * -sinT q.t + ((1 - θ) * p.2 + θ * p'.2 - q.cy) * cosT q.t
        = (1 - θ) * ((p.1 - q.cx) * -sinT q.t + (p.2 - q.cy) * cosT q.t)
          + θ * ((p'.1 - q.cx) * -sinT q.t + (p'.2 - q.cy) * cosT q.t) := by ring
    rw [e, abs_le]
    constructor <;> nlinarith [hv.1, hv.2, hv'.1, hv'.2]

/-- **Lemma PD (the two-endpoint convexity rule)**: if a set `K` meets both `Σ` and
`Σ + d`, and `K` and `Σ` are segment-closed, then `K` meets every `Σ + θ·d`, `θ ∈ [0, 1]`. -/
theorem pd_convex {K Sg : Set RP}
    (hKc : ∀ p ∈ K, ∀ p' ∈ K, ∀ θ : ℝ, 0 ≤ θ → θ ≤ 1 →
      ((1 - θ) * p.1 + θ * p'.1, (1 - θ) * p.2 + θ * p'.2) ∈ K)
    (hSc : ∀ p ∈ Sg, ∀ p' ∈ Sg, ∀ θ : ℝ, 0 ≤ θ → θ ≤ 1 →
      ((1 - θ) * p.1 + θ * p'.1, (1 - θ) * p.2 + θ * p'.2) ∈ Sg)
    {d : RP} (h0 : (K ∩ Sg).Nonempty) (h1 : (K ∩ ((fun p => (p.1 + d.1, p.2 + d.2)) '' Sg)).Nonempty)
    {θ : ℝ} (hθ0 : 0 ≤ θ) (hθ1 : θ ≤ 1) :
    (K ∩ ((fun p => (p.1 + θ * d.1, p.2 + θ * d.2)) '' Sg)).Nonempty := by
  obtain ⟨p0, hp0K, hp0S⟩ := h0
  obtain ⟨p1, hp1K, σ1, hσ1, hσ1e⟩ := h1
  refine ⟨((1 - θ) * p0.1 + θ * p1.1, (1 - θ) * p0.2 + θ * p1.2), hKc p0 hp0K p1 hp1K θ hθ0 hθ1, ?_⟩
  refine ⟨((1 - θ) * p0.1 + θ * σ1.1, (1 - θ) * p0.2 + θ * σ1.2), hSc p0 hp0S σ1 hσ1 θ hθ0 hθ1, ?_⟩
  have e1 : σ1.1 + d.1 = p1.1 := congrArg Prod.fst hσ1e
  have e2 : σ1.2 + d.2 = p1.2 := congrArg Prod.snd hσ1e
  refine Prod.ext ?_ ?_
  · simp only; linear_combination θ * e1
  · simp only; linear_combination θ * e2

/-- **The (C) rule behind Lemma PD**: a non-owner square of a strict family cannot contain a
core that meets an owner's square. -/
theorem pd_rule {s0 : ℝ} {F : Cfg} (hF : IsStrictFamily 11 s0 fun i => (F i).set) {K : Set RP}
    {i p : Fin 11} (hK : K ⊆ (F i).set) (hmeet : (K ∩ (F p).set).Nonempty) : i = p := by
  by_contra hip
  obtain ⟨x, hxK, hxp⟩ := hmeet
  exact Set.disjoint_left.mp (hF.disjoint i p hip) (hK hxK) hxp

end

end S11
end PackingCert
