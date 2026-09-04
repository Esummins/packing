import PackingCertMathlib.ZoneTree
import PackingCertMathlib.Slide
import PackingCertMathlib.CrowdZone

/-!
# The composition, re-based on the tree/tube conclusions (A86 T3, TopLevel side)

`TopLevel.lean` composes `s_eleven_ge` / `s_eleven_unique` from the two open axioms
`stratum_kill` (every non-Trump class is empty on the window) and `trump_residual`
(every Trump-class packing lands in the basin) + the theorem `basin`.  The residual-tree
route (`docs/proofs/protected_trees.md` Lemma P-TREE, `contraction_tube.md` Lemma SEAM)
proves, per class and per side, the WEAKER and uniform statement

    `ClassKilledAt i m` :  every packing of class `i` at side `m` has `m ≥ ŝ`, and at
                          `m = ŝ` is a `D4`-image of `ẑ` (after relabelling),

which is exactly what the two consumers need.  This file

* proves `s_eleven_ge_of_classes` / `s_eleven_unique_of_classes` — the composition from
  `ClassKilledAt` alone (no `stratum_kill`, no `trump_residual`, no `basin`);
* shows the old axioms IMPLY the new hypotheses (`classKilledAt_of_kill`,
  `classKilledAt_trump_of_residual`), so nothing is lost;
* proves `classKilledAt_of_tree` — a closed tree for a pin set `S ⊆ g·classRep i`
  (Step 1 hypothesis `hroot`, the tube certificate, the D4 normalisation of `class_kill`)
  gives `ClassKilledAt i m` on the tube's slab `[ŝ − T, ŝ]`;
* proves the slab split `classKilledAt_of_slabs` (regime 1 = plain kills below the slab,
  regime 2 = the tree on the slab);
* states the `stratum_kill` RE-SPLIT of `lean/k0_readiness_A85.md` (`StratumKillAll` /
  `StratumKillMin`) and proves both consumers from it (`s_eleven_ge_of_split`,
  `s_eleven_unique_of_split`) — the form needed only if minimality-based (K0-ROT) leaves
  are used.

So the remaining replay obligation per class is: the tree's leaf certificates PASS
(`checkCaseI` / `checkAtlas`), the tube certificate PASSes (`checkTube`), the tree's `cover`
(its branching, from the rule library of `ZoneTree.lean`), and the slot/landing bookkeeping
of Steps 1 and 4 — every one of them a statement about certificate FILES.

## Theorem N (A93 T4): the crowd-certificate chain, `docs/proofs/k0_blocked_side.md` §3.3

The k0_00 plan re-based by A92 composes, for EVERY class at once (it never looks at a
skeleton): **K0-O1** (`K0O1`: k1_00's monotone kill on `[3.82, ŝ)` at each corner slot — from
k1_00's closed tree by `slabKill_of_tree`) + **Lemma SLIDE** (`slide_crowd`, a theorem: every
packing at side `m < ŝ` has two squares at depth `≥ ŝ − m` at every corner) + a **crowd
certificate** `C(δ, m_lo)` (`CrowdKill`, from two `checkCaseI` PASSes + `sameMeasure` +
`crowdZones` by `crowdKill_of_files`) kill every packing at every side `m ∈ [m_lo, ŝ − δ]`
(`theoremN_slab`).  A chain `(δ_k, m_k)`, `m_0 ≤ 3.82`, `m_{k+1} ≤ ŝ − δ_k`, covers
`[3.82, ŝ − δ_K]` (`chain_cover`) and gives `s(11) ≥ ŝ − δ_K` outright
(`s_eleven_ge_of_chain`, modulo K0-O1 and the certificate files).  The residue is the SHELL
`(ŝ − δ_K, ŝ]`: `ShellKill i δ_K` is the named hypothesis RES-N(δinf) for class `i` (a packing
in the shell with two squares at depth `≥ ŝ − m` but not at depth `≥ δ_K` at some corner; at
`ŝ` the non-crowded packings of the class are Trump images), and `classKilledAt_of_chain`
turns chain + shell into `ClassKilledAt i m` on the whole window — the k0_00 instance of
`stratum_kill`, and every other class's as well.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set Rigid

/-- **The per-class window obligation, P-TREE form.** -/
def ClassKilledAt (i : StratumIdx) (m : ℝ) : Prop :=
  ∀ z : Cfg, CfgPacking m z → InStratum i m z → shat ≤ m ∧ (m = shat → IsTrumpImage z)

/-- A plain kill (no packing of the class at `m`) gives the obligation vacuously. -/
theorem classKilledAt_of_kill {i : StratumIdx} {m : ℝ}
    (h : ∀ z : Cfg, CfgPacking m z → ¬InStratum i m z) : ClassKilledAt i m :=
  fun z hz hi => absurd hi (h z hz)

/-- The old `stratum_kill` axiom gives the obligation for every non-Trump class. -/
theorem classKilledAt_of_stratum_kill {i : StratumIdx} (hi : i ≠ trumpStratum) {m : ℝ}
    (hm : m ∈ wnd) : ClassKilledAt i m :=
  classKilledAt_of_kill fun z hz => stratum_kill i hi m hm z hz

/-- The old `trump_residual` axiom + `basin` give the obligation for the Trump class. -/
theorem classKilledAt_trump_of_residual {m : ℝ} (hm : m ∈ wnd) :
    ClassKilledAt trumpStratum m := by
  intro z hz hstr
  obtain ⟨z', f, e, hsym, hz', hbasin, hrel⟩ := trump_residual m hm z hz hstr
  refine ⟨(basin z' hbasin).1 m hz', fun hms => ?_⟩
  subst hms
  have hzz : z' = zhat := (basin z' hbasin).2 hz'
  exact ⟨f, e, hsym, fun j => by rw [hrel j, hzz]⟩

/-- **The lower bound from the per-class obligations alone.** -/
theorem s_eleven_ge_of_classes (hcls : ∀ i : StratumIdx, ∀ m ∈ wnd, ClassKilledAt i m) :
    ∀ s : ℝ, Fits 11 s → shat ≤ s := by
  intro s hs
  obtain ⟨m, hm⟩ := attained
  have hms : m ≤ s := hm.2 hs
  have h382 : (191 / 50 : ℝ) ≤ m := lb_382 m hm.1
  have hmshat : m ≤ shat := hm.2 fits_shat
  have hwin : m ∈ wnd := ⟨h382, hmshat⟩
  obtain ⟨z, i, hz, hstr⟩ := stratify m hm hwin
  have := (hcls i m hwin z hz hstr).1
  linarith

/-- **The uniqueness clause from the per-class obligations at `ŝ` alone.** -/
theorem s_eleven_unique_of_classes (hcls : ∀ i : StratumIdx, ClassKilledAt i shat) :
    ∀ Q : Fin 11 → Set RP, IsPacking 11 shat Q →
      ∃ (f : RP → RP) (e : Equiv.Perm (Fin 11)),
        IsCtrSym shat f ∧ ∀ i, Q i = f '' (zhat (e i)).set := by
  intro Q hQ
  obtain ⟨z, hzt, hzQ⟩ := parametrize Q hQ
  have hz : CfgPacking shat z := by
    refine ⟨hzt, ?_⟩
    have hfun : (fun i => (z i).set) = Q := funext fun i => (hzQ i).symm
    rw [hfun]
    exact hQ
  obtain ⟨i, hi⟩ := exists_stratum shat_mem_wnd hz
  obtain ⟨f, e, hsym, hrel⟩ := (hcls i z hz hi).2 rfl
  refine ⟨f, e.symm, hsym, fun j => ?_⟩
  have hk := hrel (e.symm j)
  rw [Equiv.apply_symm_apply] at hk
  rw [hzQ j, hk]

/-! ## From a closed tree to the per-class obligation -/

theorem shatR_eq_shat : shatR = shat := shatA22_eq_shat

/-- An image statement transports along a container symmetry. -/
theorem isTrumpImage_of_d4 {z : Cfg} (h : D4) (hz : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (him : IsImageAt shat (d4Cfg shat h z)) : IsTrumpImage z := by
  obtain ⟨f, e, hsym, hrel⟩ := him
  refine ⟨d4Apply shat h.inv ∘ f, e, (isCtrSym_d4Apply shat h.inv).comp hsym, fun j => ?_⟩
  have := hrel j
  rw [d4Cfg_set h hz] at this
  show (z (e j)).set = (d4Apply shat h.inv ∘ f) '' (zhatCfg j).set
  rw [Set.image_comp, ← this, Set.image_image]
  have hid : (fun x => d4Apply shat h.inv (d4Apply shat h x)) = id := by
    funext x; exact d4Apply_inv_apply shat h x
  rw [hid, Set.image_id]

/-- **Lemma P-TREE composed (per class, on the tube's slab).**  A closed tree whose root
hypothesis is fed by the monotone pin hypothesis `ContainsPins S` (`hroot`, Step 1 —
`root_of_containsPins`) for a pin set `S ⊆ g·classRep i` gives `ClassKilledAt i m` for every
`m ∈ [ŝ − T, ŝ]`. -/
theorem classKilledAt_of_tree {i : StratumIdx} {S : PinSet} {g : D4} (hS : S ⊆ d4Pins g (classRep i))
    {s0 : ℝ} {tc : TubeCert} {Root : Cfg → Prop} (T : ClosedTree s0 tc Root)
    (ht : checkTube Data.a22 tc = true) (hs0 : shat < s0)
    (hroot : ∀ m : ℝ, shat - (tc.T : ℝ) ≤ m → m ≤ shat → ∀ z : Cfg, CfgPacking m z →
      ContainsPins S m z → Root (dil s0 m z))
    {m : ℝ} (hm1 : shat - (tc.T : ℝ) ≤ m) (hm2 : m ≤ shat) (hm3 : 3 < m) (hm4 : m < 4) :
    ClassKilledAt i m := by
  intro z hz hcls
  obtain ⟨g', hg'⟩ := hcls
  set h := g.mul g'.inv with hh
  obtain ⟨ht', hP'⟩ := d4_packing (s := m) h hz.1 hz.2
  have hskel : skeleton m (d4Cfg m h z) = d4Pins g (classRep i) := by
    rw [skeleton_d4 _ (fun i => (hz.1 i).1), hg', ← d4Pins_mul, D4.mul_inv_mul]
  have hpins : ContainsPins S m (d4Cfg m h z) :=
    containsPins_mono (hskel ▸ hS) (containsPins_skeleton hm3 hm4)
  have hroot' := hroot m hm1 hm2 _ ⟨ht', hP'⟩ hpins
  have hm0 : 0 < m := by linarith
  have key := tree_kill T ht (by rw [shatR_eq_shat]; exact hs0)
    (by rw [shatR_eq_shat]; exact hm1) (by rw [shatR_eq_shat]; exact hm2) hm0 ⟨ht', hP'⟩ hroot'
  rw [shatR_eq_shat] at key
  refine ⟨key.1, fun hms => ?_⟩
  subst hms
  exact isTrumpImage_of_d4 h hz.1 (key.2 rfl)

/-- **The slab split**: plain kills below `ŝ − T` (regime 1) and the tree on `[ŝ − T, ŝ]`
(regime 2) give the obligation on the whole window. -/
theorem classKilledAt_of_slabs {i : StratumIdx} {T : ℝ}
    (h1 : ∀ m : ℝ, (191 / 50 : ℝ) ≤ m → m < shat - T → ∀ z : Cfg, CfgPacking m z → ¬InStratum i m z)
    (h2 : ∀ m : ℝ, shat - T ≤ m → m ≤ shat → ClassKilledAt i m) :
    ∀ m ∈ wnd, ClassKilledAt i m := by
  intro m hm
  rcases lt_or_ge m (shat - T) with h | h
  · exact classKilledAt_of_kill (h1 m hm.1 h)
  · exact h2 m h hm.2

/-! ## The `stratum_kill` re-split (`lean/k0_readiness_A85.md`, T4) -/

/-- The ∀-packings form on a set of classes. -/
def StratumKillAll (I : Set StratumIdx) : Prop :=
  ∀ i ∈ I, ∀ s ∈ wnd, ∀ z : Cfg, CfgPacking s z → ¬InStratum i s z

/-- The selected form: only global σ-minimisers are excluded. -/
def StratumKillMin (I : Set StratumIdx) : Prop :=
  ∀ i ∈ I, ∀ s ∈ wnd, ∀ z : Cfg, CfgPacking s z →
    (∀ (s' : ℝ) (z' : Cfg), CfgPacking s' z' → s ≤ s') → ¬InStratum i s z

/-- **The lower bound from the split** (the minimiser supplies the selected form's
hypothesis; the Trump class through `trump_residual` + `basin`). -/
theorem s_eleven_ge_of_split {AllForm MinForm : Set StratumIdx}
    (hpart : ∀ i : StratumIdx, i ≠ trumpStratum → i ∈ AllForm ∨ i ∈ MinForm)
    (hall : StratumKillAll AllForm) (hmin : StratumKillMin MinForm) :
    ∀ s : ℝ, Fits 11 s → shat ≤ s := by
  intro s hs
  obtain ⟨m, hm⟩ := attained
  have hms : m ≤ s := hm.2 hs
  have h382 : (191 / 50 : ℝ) ≤ m := lb_382 m hm.1
  have hmshat : m ≤ shat := hm.2 fits_shat
  have hwin : m ∈ wnd := ⟨h382, hmshat⟩
  obtain ⟨z, i, hz, hstr⟩ := stratify m hm hwin
  have hminz : ∀ (s' : ℝ) (z' : Cfg), CfgPacking s' z' → m ≤ s' :=
    fun s' z' hz' => hm.2 ⟨fun i => (z' i).set, hz'.2⟩
  have hshatm : shat ≤ m := by
    by_cases hi : i = trumpStratum
    · subst hi
      obtain ⟨z', f, e, hsym, hz', hbasin, hrel⟩ := trump_residual m hwin z hz hstr
      exact (basin z' hbasin).1 m hz'
    · rcases hpart i hi with hA | hM
      · exact absurd hstr (hall i hA m hwin z hz)
      · exact absurd hstr (hmin i hM m hwin z hz hminz)
  linarith

/-- **The uniqueness clause from the split**: at `ŝ` every packing is a minimiser (by the
bound just proved), so the selected form applies to all of them. -/
theorem s_eleven_unique_of_split {AllForm MinForm : Set StratumIdx}
    (hpart : ∀ i : StratumIdx, i ≠ trumpStratum → i ∈ AllForm ∨ i ∈ MinForm)
    (hall : StratumKillAll AllForm) (hmin : StratumKillMin MinForm) :
    ∀ Q : Fin 11 → Set RP, IsPacking 11 shat Q →
      ∃ (f : RP → RP) (e : Equiv.Perm (Fin 11)),
        IsCtrSym shat f ∧ ∀ i, Q i = f '' (zhat (e i)).set := by
  have hge := s_eleven_ge_of_split hpart hall hmin
  intro Q hQ
  obtain ⟨z, hzt, hzQ⟩ := parametrize Q hQ
  have hz : CfgPacking shat z := by
    refine ⟨hzt, ?_⟩
    have hfun : (fun i => (z i).set) = Q := funext fun i => (hzQ i).symm
    rw [hfun]
    exact hQ
  obtain ⟨i, hi⟩ := exists_stratum shat_mem_wnd hz
  have hminz : ∀ (s' : ℝ) (z' : Cfg), CfgPacking s' z' → shat ≤ s' :=
    fun s' z' hz' => hge s' ⟨fun i => (z' i).set, hz'.2⟩
  have hit : i = trumpStratum := by
    by_contra hne
    rcases hpart i hne with hA | hM
    · exact hall i hA shat shat_mem_wnd z hz hi
    · exact hmin i hM shat shat_mem_wnd z hz hminz hi
  subst hit
  obtain ⟨z'', f2, e2, hsym2, hz'', hbasin, hrel2⟩ := trump_residual shat shat_mem_wnd z hz hi
  have hzz : z'' = zhat := (basin z'' hbasin).2 hz''
  refine ⟨f2, e2.symm, hsym2, fun j => ?_⟩
  have hk := hrel2 (e2.symm j)
  rw [Equiv.apply_symm_apply, hzz] at hk
  rw [hzQ j, hk]

/-! ## Theorem N: the crowd-certificate chain (A93 T4; K0.CW, K0.SLIDE, K0.RESN) -/

/-- **K0-O1** (`k0_route.md` §3): k1_00's monotone kill on the window — no packing at any side
`m ∈ [3.82, ŝ)` contains an axis-aligned unit square at a corner slot.  The dependency both
K0-FREE and SLIDE consume; delivered by k1_00's closed tree (`slabKill_of_tree`) plus its
regime-1 slab kills (`WindowRows.SlabKill`). -/
def K0O1 : Prop := ∀ c : Fin 4, SlabKill {⟨c, 0, 0⟩} (191 / 50) shat

/-- **A closed tree gives the monotone slab kill of its pin set on the tube's slab** — the
form K0-O1 consumes (`classKilledAt_of_tree` without the class bookkeeping: the tree's
conclusion `ŝ ≤ m` is absurd below `ŝ`). -/
theorem slabKill_of_tree {S : PinSet} {s0 : ℝ} {tc : TubeCert} {Root : Cfg → Prop}
    (T : ClosedTree s0 tc Root) (ht : checkTube Data.a22 tc = true) (hs0 : shat < s0)
    (hroot : ∀ m : ℝ, shat - (tc.T : ℝ) ≤ m → m ≤ shat → ∀ z : Cfg, CfgPacking m z →
      ContainsPins S m z → Root (dil s0 m z))
    (hpos : 0 < shat - (tc.T : ℝ)) :
    SlabKill S (shat - (tc.T : ℝ)) shat := by
  intro m hm1 hm2 z hz hS
  have hroot' := hroot m hm1 hm2.le z hz hS
  have key := tree_kill T ht (by rw [shatR_eq_shat]; exact hs0)
    (by rw [shatR_eq_shat]; exact hm1) (by rw [shatR_eq_shat]; exact hm2.le) (by linarith) hz hroot'
  rw [shatR_eq_shat] at key
  linarith [key.1]

/-- **Theorem N (1)** (`k0_blocked_side.md` §3.3): `C(δ, m_lo)` + SLIDE + K0-FREE exclude every
packing at every side `m ∈ [m_lo, ŝ − δ]` (with `m ≥ 3.82`).  A packing at such `m` has, at
every corner, two squares at depth `≥ ŝ − m ≥ δ` (`slide_crowd`, which subsumes the K0-FREE
case), and the certificate forbids exactly that. -/
theorem theoremN_slab (hK1 : K0O1) {δ mlo s0 : ℝ} (hC : CrowdKill δ mlo s0) (hs0 : shat ≤ s0)
    (hδ : 0 < δ) :
    ∀ m, 191 / 50 ≤ m → mlo ≤ m → m ≤ shat - δ → ∀ z : Cfg, ¬ CfgPacking m z := by
  intro m h382 hlo hδm z hz
  have hm : m < shat := by linarith
  have hcr := slide_crowd hK1 (by norm_num) h382 hm hz
  exact hC m hlo (by linarith) z hz (crowdBox_mono (by linarith) hcr)

/-- **The chaining (Theorem N (2)–(3))**: a chain `(δ_k, m_k)`, `k = 0..K`, with `m_0 ≤ 3.82` and
`m_{k+1} ≤ ŝ − δ_k` covers `[3.82, ŝ − δ_K]` by its slabs `[m_k, ŝ − δ_k]`. -/
theorem chain_cover (δ mlo : ℕ → ℝ) (h0 : mlo 0 ≤ 191 / 50) :
    ∀ K : ℕ, (∀ k < K, mlo (k + 1) ≤ shat - δ k) →
      ∀ m, 191 / 50 ≤ m → m ≤ shat - δ K → ∃ k ≤ K, mlo k ≤ m ∧ m ≤ shat - δ k := by
  intro K
  induction K with
  | zero =>
    intro _ m h382 hm
    exact ⟨0, le_rfl, le_trans h0 h382, hm⟩
  | succ K ih =>
    intro hstep m h382 hm
    by_cases hK : m ≤ shat - δ K
    · obtain ⟨k, hk, h1, h2⟩ := ih (fun k hk => hstep k (Nat.lt_succ_of_lt hk)) m h382 hK
      exact ⟨k, Nat.le_succ_of_le hk, h1, h2⟩
    · push Not at hK
      exact ⟨K + 1, le_rfl, le_trans (hstep K (Nat.lt_succ_self K)) hK.le, hm⟩

/-- **`k0_kill_of_chain`, class-blind form**: under K0-O1, a chain of passing crowd
certificates excludes EVERY packing at every side `m ∈ [3.82, ŝ − δ_K]`. -/
theorem no_packing_of_chain (hK1 : K0O1) {s0 : ℝ} (hs0 : shat ≤ s0) {K : ℕ} (δ mlo : ℕ → ℝ)
    (hδ : ∀ k ≤ K, 0 < δ k) (hC : ∀ k ≤ K, CrowdKill (δ k) (mlo k) s0)
    (h0 : mlo 0 ≤ 191 / 50) (hstep : ∀ k < K, mlo (k + 1) ≤ shat - δ k) :
    ∀ m, 191 / 50 ≤ m → m ≤ shat - δ K → ∀ z : Cfg, ¬ CfgPacking m z := by
  intro m h382 hm z hz
  obtain ⟨k, hk, h1, h2⟩ := chain_cover δ mlo h0 K hstep m h382 hm
  exact theoremN_slab hK1 (hC k hk) hs0 (hδ k hk) m h382 h1 h2 z hz

/-- **`s(11) ≥ ŝ − δ_K`** from the chain (Theorem N (2)): no 11-packing at any side below
`ŝ − δ_K`.  Hypotheses: K0-O1 and the `K + 1` certificate conclusions. -/
theorem s_eleven_ge_of_chain (hK1 : K0O1) {s0 : ℝ} (hs0 : shat ≤ s0) {K : ℕ} (δ mlo : ℕ → ℝ)
    (hδ : ∀ k ≤ K, 0 < δ k) (hC : ∀ k ≤ K, CrowdKill (δ k) (mlo k) s0)
    (h0 : mlo 0 ≤ 191 / 50) (hstep : ∀ k < K, mlo (k + 1) ≤ shat - δ k) :
    ∀ s : ℝ, Fits 11 s → shat - δ K ≤ s := by
  intro s hs
  by_contra hlt
  push Not at hlt
  have h382 := lb_382 s hs
  obtain ⟨Q, hQ⟩ := hs
  obtain ⟨z, hzt, hzQ⟩ := parametrize Q hQ
  have hz : CfgPacking s z := by
    refine ⟨hzt, ?_⟩
    have hfun : (fun i => (z i).set) = Q := funext fun i => (hzQ i).symm
    rw [hfun]
    exact hQ
  exact no_packing_of_chain hK1 hs0 δ mlo hδ hC h0 hstep s h382 hlt.le z hz

/-- **`k0_kill_of_chain`, per-class form**: every class (k0_00 included) is killed at every
side `m ∈ [3.82, ŝ − δ_K]` — the chain never looks at the skeleton. -/
theorem classKilledAt_below_of_chain (hK1 : K0O1) {s0 : ℝ} (hs0 : shat ≤ s0) {K : ℕ}
    (δ mlo : ℕ → ℝ) (hδ : ∀ k ≤ K, 0 < δ k) (hC : ∀ k ≤ K, CrowdKill (δ k) (mlo k) s0)
    (h0 : mlo 0 ≤ 191 / 50) (hstep : ∀ k < K, mlo (k + 1) ≤ shat - δ k)
    (i : StratumIdx) {m : ℝ} (h382 : 191 / 50 ≤ m) (hm : m ≤ shat - δ K) :
    ClassKilledAt i m :=
  classKilledAt_of_kill fun z hz _ => no_packing_of_chain hK1 hs0 δ mlo hδ hC h0 hstep m h382 hm z hz

/-- **RES-N(δinf), the named residue for class `i`** (`k0_blocked_side.md` §3.3): in the shell
`(ŝ − δinf, ŝ)`, a packing of the class with two squares at depth `≥ ŝ − m` at every corner
(SLIDE's floor) but not two at depth `≥ δinf` at some corner (the certificate's kill) does not
exist; at `ŝ`, a packing of the class not crowded at depth `δinf` is a Trump image (the
uniqueness clause SLIDE does not reach).  For `i = k0_00` this is exactly A92's RES-N; for the
certified classes it is their own tree/slab kill restricted to the shell. -/
structure ShellKill (i : StratumIdx) (δinf : ℝ) : Prop where
  below : ∀ m, shat - δinf < m → m < shat → ∀ z : Cfg, CfgPacking m z → InStratum i m z →
    CrowdBox m (1 - (shat - m)) z → ¬ CrowdBox m (1 - δinf) z → False
  at_shat : ∀ z : Cfg, CfgPacking shat z → InStratum i shat z → ¬ CrowdBox shat (1 - δinf) z →
    IsTrumpImage z

/-- **The per-class window obligation from the chain + the shell residue** — the k0_00 piece
of `stratum_kill` in `ClassKilledAt` form: below `ŝ − δ_K` the chain, in the shell SLIDE's
floor + the last certificate + `ShellKill`, at `ŝ` the last certificate + `ShellKill`. -/
theorem classKilledAt_of_chain (hK1 : K0O1) {s0 : ℝ} (hs0 : shat < s0) {K : ℕ} (δ mlo : ℕ → ℝ)
    (hδ : ∀ k ≤ K, 0 < δ k) (hC : ∀ k ≤ K, CrowdKill (δ k) (mlo k) s0)
    (h0 : mlo 0 ≤ 191 / 50) (hstep : ∀ k < K, mlo (k + 1) ≤ shat - δ k)
    (hlast : mlo K ≤ shat - δ K) {i : StratumIdx} (hshell : ShellKill i (δ K)) :
    ∀ m ∈ wnd, ClassKilledAt i m := by
  intro m hm z hz hstr
  rcases le_or_gt m (shat - δ K) with hle | hgt
  · exact absurd hz (no_packing_of_chain hK1 hs0.le δ mlo hδ hC h0 hstep m hm.1 hle z)
  · rcases lt_or_eq_of_le hm.2 with hlt | heq
    · exfalso
      have hcr := slide_crowd hK1 (by norm_num) hm.1 hlt hz
      have hno := hC K le_rfl m (by linarith) (by linarith) z hz
      exact hshell.below m hgt hlt z hz hstr hcr hno
    · subst heq
      refine ⟨le_rfl, fun _ => ?_⟩
      have hno := hC K le_rfl shat (by linarith) hs0 z hz
      exact hshell.at_shat z hz hstr hno

end

end S11
end PackingCert
