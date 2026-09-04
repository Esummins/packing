import PackingCertMathlib.Crowd

/-!
# Lemma SLIDE and Lemma K0-FREE (A93 T2, depgraph K0.SLIDE / K0.FREE)

`docs/proofs/k0_blocked_side.md` §3.1 (Lemma SLIDE), `docs/proofs/k0_route.md` §3 (Lemma
K0-FREE).  Both are ∀-packings statements whose only external input is **K0-O1**: k1_00's
monotone kill on the window — no packing at any side `m ∈ [3.82, ŝ)` contains an axis-aligned
unit square at a corner slot (`SlabKill {corner slot} 3.82 ŝ` for each of the four corners,
delivered by k1_00's closed tree, `slabKill_of_tree` in `Composition.lean`).

* `k0free_kill` — **Lemma K0-FREE**: if some corner's open unit box is interior-met by at most
  one square, teleport that square into the slot (`teleport_packing`, C.CC2) and apply K0-O1.
* `slide_crowd` — **Lemma SLIDE, ∀-packings form**: every packing at side `m ∈ [3.82, ŝ)` has,
  at EVERY corner, two distinct squares meeting the closed box `[0, 1 − (ŝ − m)]²` — i.e. every
  corner's second intruder has depth `≥ ŝ − m` (`CrowdBox m (1 − (ŝ − m)) z`).

**The proof is simpler than A92's.**  A92 slides the shallow intruders' retreat clusters along
the diagonal (Lemma CLUSTER's affine feasibility, cluster enlargements, ≤ 10 rounds).  None of
that is needed: with the container allowed to grow at the far walls of `c`, translate the WHOLE
packing by `τ` away from corner `c` (`shiftCfg`: by `(τ, τ)` at BL, `(0, τ)` at BR, `(τ, 0)` at
TL, nothing at TR).  The translate is a packing at side `m + τ` outright (rigid motion,
`shiftCfg_packing`), and in `c`'s frame every square moves by exactly `(τ, τ)`
(`cframe_shift`), so its `μ_c` rises by exactly `τ` — the "depth rate `1/√2` per `1/√2` of
side" of the prose, with no cluster bookkeeping.  If some corner had at most one square at
depth `≥ ŝ − m`, the other ten have `μ_c > 1 − (ŝ − m)` (attained minima, `exists_min_gcf`),
so a `τ < ŝ − m` shifts all ten out of the open unit box at side `m + τ < ŝ`; K0-FREE at that
side contradicts K0-O1.  Consequently SLIDE's Step 2 in the prose (sequential cluster slides,
whose honest yield is only `Σ_{i ≥ 1} d_i ≥ ŝ − m`) is replaced by one simultaneous motion,
which is what the stated conclusion `d₂(c) ≥ ŝ − m` needs (see A93 findings).

Axioms: `propext, Classical.choice, Quot.sound`.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-! ## Translating a packing away from a corner, with the container growing -/

/-- The outward shift of corner `c` by `τ`, in container coordinates: the far walls of `c`
move by `τ`, the walls through `c` do not (so that the container `[0, m+τ]²` keeps corner `c`
in place relative to the squares). -/
def shiftVec (c : Fin 4) (τ : ℝ) : RP :=
  (if cornerR c then 0 else τ, if cornerT c then 0 else τ)

/-- Translate a parametrised square by `v` (tilt unchanged). -/
def shiftSq (v : RP) (q : PSq) : PSq := ⟨q.cx + v.1, q.cy + v.2, q.t⟩

/-- Translate every square of a configuration by the outward shift of corner `c`. -/
def shiftCfg (c : Fin 4) (τ : ℝ) (z : Cfg) : Cfg := fun i => shiftSq (shiftVec c τ) (z i)

theorem mem_shiftSq_set_iff (v : RP) (q : PSq) (p : RP) :
    p ∈ (shiftSq v q).set ↔ (p.1 - v.1, p.2 - v.2) ∈ q.set := by
  rw [mem_set_iff_uv, mem_set_iff_uv]
  have e1 : p.1 - (shiftSq v q).cx = p.1 - v.1 - q.cx := by simp only [shiftSq]; ring
  have e2 : p.2 - (shiftSq v q).cy = p.2 - v.2 - q.cy := by simp only [shiftSq]; ring
  have e3 : edir (shiftSq v q) = edir q := rfl
  simp only [e1, e2, e3]

theorem mem_interior_shiftSq_iff (v : RP) (q : PSq) (p : RP) :
    p ∈ interior (shiftSq v q).set ↔ (p.1 - v.1, p.2 - v.2) ∈ interior q.set := by
  rw [mem_interior_iff_uv, mem_interior_iff_uv]
  have e1 : p.1 - (shiftSq v q).cx = p.1 - v.1 - q.cx := by simp only [shiftSq]; ring
  have e2 : p.2 - (shiftSq v q).cy = p.2 - v.2 - q.cy := by simp only [shiftSq]; ring
  have e3 : edir (shiftSq v q) = edir q := rfl
  simp only [e1, e2, e3]

/-- In the frame of corner `c`, the outward shift is exactly `(τ, τ)`: the exact diagonal rate
(`μ_c(Q + τu) = μ_c(Q) + τ`, `k0_blocked_side.md` §3.1). -/
theorem cframe_shift (m τ : ℝ) (c : Fin 4) (p : RP) :
    (cframe (m + τ) c p).1 = (cframe m c (p.1 - (shiftVec c τ).1, p.2 - (shiftVec c τ).2)).1 + τ ∧
    (cframe (m + τ) c p).2 = (cframe m c (p.1 - (shiftVec c τ).1, p.2 - (shiftVec c τ).2)).2 + τ := by
  simp only [cframe, shiftVec]
  split_ifs <;> constructor <;> ring

/-- **The translate is a packing at side `m + τ`** (a rigid motion; the container grows at the
far walls of `c`). -/
theorem shiftCfg_packing {m τ : ℝ} (hτ : 0 ≤ τ) (c : Fin 4) {z : Cfg} (hz : CfgPacking m z) :
    CfgPacking (m + τ) (shiftCfg c τ z) := by
  refine ⟨fun i => hz.1 i, ⟨fun i => psq_isUnitSquare _, fun i p hp => ?_, fun i j hij => ?_⟩⟩
  · have hp' := (mem_shiftSq_set_iff _ _ _).mp hp
    have hc := hz.2.contained i hp'
    simp only [container, mem_prod, mem_Icc, shiftVec] at hc ⊢
    split_ifs at hc ⊢ <;> obtain ⟨⟨h1, h2⟩, h3, h4⟩ := hc <;>
      exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩
  · rw [Set.disjoint_left]
    intro p hp hp'
    have h1 := (mem_interior_shiftSq_iff _ _ _).mp hp
    have h2 := (mem_interior_shiftSq_iff _ _ _).mp hp'
    exact Set.disjoint_left.mp (hz.2.interiorDisjoint i j hij) h1 h2

/-- A shifted square meeting the closed box `[0,a]²` at corner `c` of `[0, m+τ]²` came from a
square meeting `[0, a − τ]²` at corner `c` of `[0,m]²`. -/
theorem shift_meets_cornerBox {m τ a : ℝ} (c : Fin 4) {q : PSq} (hq : q.set ⊆ container m)
    (h : ((shiftSq (shiftVec c τ) q).set ∩ cornerBox (m + τ) a c).Nonempty) :
    (q.set ∩ cornerBox m (a - τ) c).Nonempty := by
  obtain ⟨p, hpq, hpb⟩ := h
  have hp' := (mem_shiftSq_set_iff _ _ _).mp hpq
  refine ⟨_, hp', ?_⟩
  obtain ⟨h1, h2, h3, h4⟩ := hpb
  obtain ⟨e1, e2⟩ := cframe_shift m τ c p
  rw [e1] at h1 h2
  rw [e2] at h3 h4
  obtain ⟨c1, -, c3, -⟩ := cframe_of_mem_container c (hq hp')
  exact ⟨c1, by linarith, c3, by linarith⟩

/-! ## Lemma K0-FREE -/

/-- **Lemma K0-FREE** (`k0_route.md` §3, ∀-packings): if the open unit box at corner `c` of a
packing at side `m ∈ [lo, hi)` is interior-met by at most one square `i₀`, teleporting `i₀`
into the corner slot gives a packing at the same side containing the corner pin — excluded by
K0-O1 (`hK1`, k1_00's monotone kill on `[lo, hi)`). -/
theorem k0free_kill {lo hi : ℝ} (hK1 : ∀ c : Fin 4, SlabKill {⟨c, 0, 0⟩} lo hi)
    {m : ℝ} (hlo : lo ≤ m) (hhi : m < hi) (hm1 : 1 ≤ m) {z : Cfg} (hz : CfgPacking m z)
    (c : Fin 4) (i₀ : Fin 11)
    (hfree : ∀ j, j ≠ i₀ → Disjoint (interior (cornerBox m 1 c)) (interior (z j).set)) :
    False := by
  rw [cornerBox_one_eq_slotBox] at hfree
  have hbox : slotBox (slotCentre m ⟨c, 0, 0⟩) ⊆ container m := by
    rw [← cornerBox_one_eq_slotBox]
    exact cornerBox_subset_container hm1 c
  have hz' := teleport_packing hz i₀ _ hbox hfree
  refine hK1 c m hlo hhi _ hz' ⟨fun _ => i₀, ?_, ?_⟩
  · rw [Finset.coe_singleton]
    exact Set.injOn_singleton _ _
  · intro a ha
    rw [Finset.mem_singleton] at ha
    subst ha
    rw [OccupiesSlot, teleport_self]
    rfl

/-! ## Lemma SLIDE -/

/-- **Lemma SLIDE (∀-packings; the nick floor).**  Under K0-O1 on `[lo, hi)` (`lo ≥ 1`), every
packing at side `m ∈ [lo, hi)` has, at every corner, two distinct squares meeting the closed
box `[0, 1 − (hi − m)]²`: every corner's second intruder has depth `≥ hi − m`.  With
`lo = 3.82`, `hi = ŝ` this is `k0_blocked_side.md` §3.1–3.2, `d₂(c) ≥ ŝ − m` — and it holds for
EVERY packing (K0-FREE is the case of a corner with `≤ 1` square at any positive depth). -/
theorem slide_crowd {lo hi : ℝ} (hK1 : ∀ c : Fin 4, SlabKill {⟨c, 0, 0⟩} lo hi) (hlo1 : 1 ≤ lo)
    {m : ℝ} (hlo : lo ≤ m) (hhi : m < hi) {z : Cfg} (hz : CfgPacking m z) :
    CrowdBox m (1 - (hi - m)) z := by
  intro c
  by_contra hno
  push Not at hno
  -- at most one square meets the box: call it `i₀`
  have hone : ∃ i₀ : Fin 11, ∀ j, j ≠ i₀ →
      ¬ ((z j).set ∩ cornerBox m (1 - (hi - m)) c).Nonempty := by
    by_cases hex : ∃ i, ((z i).set ∩ cornerBox m (1 - (hi - m)) c).Nonempty
    · obtain ⟨i, hi⟩ := hex
      exact ⟨i, fun j hj => Set.not_nonempty_iff_eq_empty.mpr (hno i j (Ne.symm hj) hi)⟩
    · push Not at hex
      exact ⟨0, fun j _ => Set.not_nonempty_iff_eq_empty.mpr (hex j)⟩
  obtain ⟨i₀, hi₀⟩ := hone
  -- the attained corner values `μ_c`
  choose pst hpst hmin using fun j => exists_min_gcf (z j) m c
  have hgt : ∀ j, j ≠ i₀ → 1 - (hi - m) < gcf m c (pst j) := by
    intro j hj
    by_contra hle
    push Not at hle
    exact hi₀ j hj ⟨pst j, hpst j, (mem_cornerBox_iff_gcf (hz.2.contained j (hpst j))).mpr hle⟩
  -- the largest depth among the other squares is `< hi − m`
  have hne : ∃ j₁ : Fin 11, j₁ ≠ i₀ := by
    by_cases h : i₀ = 0
    · exact ⟨1, by simp [h]⟩
    · exact ⟨0, fun h' => h h'.symm⟩
  obtain ⟨j₁, hj₁⟩ := hne
  obtain ⟨jm, hjm, hmax⟩ := Finset.exists_max_image (Finset.univ.erase i₀)
    (fun j => 1 - gcf m c (pst j)) ⟨j₁, Finset.mem_erase.mpr ⟨hj₁, Finset.mem_univ _⟩⟩
  have hM : 1 - gcf m c (pst jm) < hi - m := by
    have := hgt jm (Finset.ne_of_mem_erase hjm)
    linarith
  -- a shift `τ` strictly between that depth and `hi − m`
  obtain ⟨τ, hτ0, hτhi, hτM⟩ : ∃ τ, 0 ≤ τ ∧ τ < hi - m ∧ 1 - gcf m c (pst jm) < τ :=
    ⟨max 0 ((1 - gcf m c (pst jm) + (hi - m)) / 2), le_max_left _ _,
      max_lt (by linarith) (by linarith), lt_of_lt_of_le (by linarith) (le_max_right _ _)⟩
  -- shift the whole packing: a packing at side `m + τ < hi` with corner `c` K0-FREE
  have hz' := shiftCfg_packing hτ0 c hz
  refine k0free_kill hK1 (by linarith) (by linarith) (by linarith) hz' c i₀ fun j hj => ?_
  refine Disjoint.mono interior_subset interior_subset ?_
  rw [Set.disjoint_left]
  intro p hpb hpq
  have hmeet : ((shiftSq (shiftVec c τ) (z j)).set ∩ cornerBox (m + τ) 1 c).Nonempty :=
    ⟨p, hpq, hpb⟩
  obtain ⟨p', hp'q, hp'b⟩ := shift_meets_cornerBox c (hz.2.contained j) hmeet
  rw [mem_cornerBox_iff_gcf (hz.2.contained j hp'q)] at hp'b
  have h1 := hmin j p' hp'q
  have h2 := hmax j (Finset.mem_erase.mpr ⟨hj, Finset.mem_univ _⟩)
  linarith

end

end S11
end PackingCert
