import PackingCertMathlib.ZoneTree
import PackingCertMathlib.ParamBridge
import PackingCertMathlib.ParamK506

/-!
# Window composition for the scoreboard rows (A86 T4, node C.A61 / C.WIN)

A stratum's window row is a DISJUNCTION of certificates, each killing the monotone pin
hypothesis `ContainsPins S` on a slab of sides.  `SlabKill S lo hi` is that slab statement
(`lo ≤ m < hi`; the top is open because Lemma B's dilation needs `λ > 1`), with the three
constructors of the 52-row scoreboard:

* `slabKill_of_param` — a `parametric-kill-certificate-v1` PASS (`checkParamI`, V.PARAM)
  covers its whole `s`-window `[s_lo, s_hi)`: at every real side `m` of it the certificate is
  specialised at a side `s″ ∈ (m, s_hi]` so close to `m` that the drift `(s″/m − 1)·A` stays
  below the core margin `ρ` (Corollary B′), then `checkParamI_kill_packing` + `bprime_containment`;
* `slabKill_of_case` — a fixed-side slack-core PASS at `s″` (`checkCaseI`, V.CASE) covers
  `[lo, s″)` whenever `(s″/lo − 1)·A < ρ` (the slack-core grid of `closed_disjoint_bridge.md` B.4);
* `slabKill_of_M1` — a single-corner certificate (all pins `β = 0`, `Zones.lean` C.M1) covers
  `(0, s″)` outright (the dilation can be chosen arbitrarily close to `1`).

`slabKill_union` glues slabs; `windowKilled_of_slab` turns a slab reaching `[3.82, ŝ]`
(top strictly above `ŝ`, e.g. the census window's `s0`) into the `stratum_kill` instance of
every class whose representative contains `S` up to `D4` (`class_kill`).  `k5_06_slab`
instantiates the parametric constructor on the replayed pilot `k5_06.param` (A75).
The nine converting rows of C.A61 enter as `checkParamI … = true` hypotheses of exactly
this shape once their data modules exist (`lean/gen_param_lean.py`).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set CaseI ParamI

/-- The pin set `S` is killed on the slab `[lo, hi)`. -/
def SlabKill (S : PinSet) (lo hi : ℝ) : Prop :=
  ∀ m : ℝ, lo ≤ m → m < hi → ∀ z : Cfg, CfgPacking m z → ¬ContainsPins S m z

theorem slabKill_union {S : PinSet} {lo mid hi : ℝ} (h1 : SlabKill S lo mid)
    (h2 : SlabKill S mid hi) : SlabKill S lo hi := by
  intro m hlo hhi z hz hS
  rcases lt_or_ge m mid with h | h
  · exact h1 m hlo h z hz hS
  · exact h2 m h hhi z hz hS

theorem slabKill_mono {S : PinSet} {lo hi lo' hi' : ℝ} (h : SlabKill S lo hi) (h1 : lo ≤ lo')
    (h2 : hi' ≤ hi) : SlabKill S lo' hi' :=
  fun m hlo hhi z hz hS => h m (le_trans h1 hlo) (lt_of_lt_of_le hhi h2) z hz hS

/-! ## Cores inside their axis boxes -/

/-- A core of half-side `a` and tilt `tm` lies in the axis box of half-width
`a·(cosT tm + sinT tm)` about its centre. -/
theorem core_box {kx ky tm a : ℝ} (htm0 : 0 ≤ tm) (htm1 : tm ≤ 1) {p : RP}
    (hu : |(p.1 - kx) * cosT tm + (p.2 - ky) * sinT tm| ≤ a)
    (hv : |(-(p.1 - kx)) * sinT tm + (p.2 - ky) * cosT tm| ≤ a) :
    |p.1 - kx| ≤ a * (cosT tm + sinT tm) ∧ |p.2 - ky| ≤ a * (cosT tm + sinT tm) := by
  have hc := cosT_nonneg htm0 htm1
  have hs := sinT_nonneg htm0
  have hcs := cosT_sq_add_sinT_sq tm
  set u := (p.1 - kx) * cosT tm + (p.2 - ky) * sinT tm with hu'
  set v := (-(p.1 - kx)) * sinT tm + (p.2 - ky) * cosT tm with hv'
  have ex : p.1 - kx = u * cosT tm - v * sinT tm := by
    simp only [hu', hv']; linear_combination (-(p.1 - kx)) * hcs
  have ey : p.2 - ky = u * sinT tm + v * cosT tm := by
    simp only [hu', hv']; linear_combination (-(p.2 - ky)) * hcs
  have hu1 := abs_le.mp hu
  have hv1 := abs_le.mp hv
  constructor
  · rw [ex, abs_le]; constructor <;> nlinarith
  · rw [ey, abs_le]; constructor <;> nlinarith

/-- The parametric core at side `s` lies in the axis box of half-width `½ − ρ` about its
centre whenever `ρ ≤ ½ − a·(cosT tm + sinT tm)`. -/
theorem coreSetP_subset_box {K : PCore} {rho : ℝ} (htm0 : (0 : ℝ) ≤ K.tm) (htm1 : (K.tm : ℝ) ≤ 1)
    (hrho : rho ≤ 1 / 2 - (K.a : ℝ) * (cosT K.tm + sinT K.tm)) (s : ℝ) :
    coreSetP K s ⊆
      Icc ((K.akx : ℝ) + K.bkx * s - (1 / 2 - rho)) ((K.akx : ℝ) + K.bkx * s + (1 / 2 - rho)) ×ˢ
      Icc ((K.aky : ℝ) + K.bky * s - (1 / 2 - rho)) ((K.aky : ℝ) + K.bky * s + (1 / 2 - rho)) := by
  intro p hp
  obtain ⟨hu, hv⟩ := hp
  obtain ⟨hx, hy⟩ := core_box htm0 htm1 hu hv
  rw [abs_le] at hx hy
  simp only [mem_prod, mem_Icc]
  exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

/-- The fixed-side core lies in the axis box of half-width `½ − ρ` about its centre. -/
theorem coreSet_subset_box {K : CCore} {rho : ℝ} (htm0 : (0 : ℝ) ≤ K.tm) (htm1 : (K.tm : ℝ) ≤ 1)
    (hrho : rho ≤ 1 / 2 - (K.a : ℝ) * (cosT K.tm + sinT K.tm)) :
    coreSet K ⊆
      Icc ((K.kx : ℝ) - (1 / 2 - rho)) ((K.kx : ℝ) + (1 / 2 - rho)) ×ˢ
      Icc ((K.ky : ℝ) - (1 / 2 - rho)) ((K.ky : ℝ) + (1 / 2 - rho)) := by
  intro p hp
  obtain ⟨hu, hv⟩ := hp
  obtain ⟨hx, hy⟩ := core_box htm0 htm1 hu hv
  rw [abs_le] at hx hy
  simp only [mem_prod, mem_Icc]
  exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

/-- The dilated pin square contains the slack core at the side-`s″` slot (B′). -/
theorem pin_core_interior {m s'' A rho : ℝ} (hm0 : 0 < m) (hms : m < s'')
    (hbudget : (s'' / m - 1) * A < rho) {a : Slot} (hAx : |slotAX a| ≤ A) (hAy : |slotAY a| ≤ A)
    {q : PSq} (ht : q.t ∈ Icc (0 : ℝ) 1) (hocc : OccupiesSlot q (slotCentre m a)) {K : Set RP}
    (hK : K ⊆ Icc (slotAX a + slotBX a * s'' - (1 / 2 - rho)) (slotAX a + slotBX a * s'' + (1 / 2 - rho)) ×ˢ
      Icc (slotAY a + slotBY a * s'' - (1 / 2 - rho)) (slotAY a + slotBY a * s'' + (1 / 2 - rho))) :
    K ⊆ interior ((scaleC (s'' / m) q).set) := by
  have hlam : 1 < s'' / m := by rw [lt_div_iff₀ hm0]; linarith
  have hs : s'' = s'' / m * m := by field_simp
  have hbx : (s'' / m - 1) * |slotAX a| < rho :=
    lt_of_le_of_lt (mul_le_mul_of_nonneg_left hAx (by linarith)) hbudget
  have hby : (s'' / m - 1) * |slotAY a| < rho :=
    lt_of_le_of_lt (mul_le_mul_of_nonneg_left hAy (by linarith)) hbudget
  rw [slotCentre_affine] at hocc
  rw [dil_slot_set ht hocc]
  exact bprime_containment hlam hs hbx hby hK

/-- A side `s″ ∈ (m, hi]` with drift `(s″/m − 1)·A < ρ` exists whenever `m < hi`. -/
theorem exists_side {m hi A rho : ℝ} (hm0 : 0 < m) (hmhi : m < hi) (hA0 : 0 ≤ A) (hrho : 0 < rho) :
    ∃ s'' : ℝ, m < s'' ∧ s'' ≤ hi ∧ (s'' / m - 1) * A < rho := by
  set δ : ℝ := rho / (2 * (A + 1)) with hδ
  have hδ0 : 0 < δ := by positivity
  refine ⟨min hi (m * (1 + δ)), ?_, min_le_left _ _, ?_⟩
  · apply lt_min hmhi
    nlinarith
  · have h1 : min hi (m * (1 + δ)) ≤ m * (1 + δ) := min_le_right _ _
    have h2 : min hi (m * (1 + δ)) / m - 1 ≤ δ := by
      rw [div_sub_one hm0.ne', div_le_iff₀ hm0]
      linarith
    calc (min hi (m * (1 + δ)) / m - 1) * A ≤ δ * A := mul_le_mul_of_nonneg_right h2 hA0
      _ < rho := by
          rw [hδ]
          have : rho / (2 * (A + 1)) * A = rho * (A / (2 * (A + 1))) := by ring
          rw [this]
          have hlt : A / (2 * (A + 1)) < 1 := by
            rw [div_lt_one (by positivity)]; linarith
          nlinarith

/-! ## The three slab constructors -/

/-- **Parametric certificate ⟹ slab kill on its whole window.**  Every core of the
certificate is the slack core of a pin slot of `S` (centre `α + β·s`, tilt `tm`, half-side
`a` with margin `ρ ≤ ½ − a·(cosT tm + sinT tm)`). -/
theorem slabKill_of_param {c : PCertI} (hn : c.n = 11) {ts ss : Int} {k : ℕ}
    {pick : PBox → List PAtom → Int → PAtom → Bool} (h : checkParamI c ts ss k pick = true)
    {S : PinSet} {A rho : ℝ} (hA0 : 0 ≤ A) (hrho : 0 < rho) (hlo0 : 0 < paramLo c)
    (hA : ∀ a ∈ S, |slotAX a| ≤ A ∧ |slotAY a| ≤ A)
    (hcores : ∀ j : Fin c.cores.length, ∃ a ∈ S,
      ((c.cores.get j).akx : ℝ) = slotAX a ∧ ((c.cores.get j).bkx : ℝ) = slotBX a ∧
      ((c.cores.get j).aky : ℝ) = slotAY a ∧ ((c.cores.get j).bky : ℝ) = slotBY a ∧
      (0 : ℝ) ≤ (c.cores.get j).tm ∧ ((c.cores.get j).tm : ℝ) ≤ 1 ∧
      rho ≤ 1 / 2 - ((c.cores.get j).a : ℝ) * (cosT (c.cores.get j).tm + sinT (c.cores.get j).tm)) :
    SlabKill S (paramLo c) (paramHi c) := by
  intro m hlo hhi z hz hS
  have hm0 : 0 < m := lt_of_lt_of_le hlo0 hlo
  obtain ⟨s'', hms, hshi, hbudget⟩ := exists_side hm0 hhi hA0 hrho
  obtain ⟨f, -, hocc⟩ := hS
  choose a haS hmatch using hcores
  have hlam : 1 < s'' / m := by rw [lt_div_iff₀ hm0]; linarith
  have hs : s'' / m * m = s'' := by field_simp
  refine checkParamI_kill_packing hn h hlam (by rw [hs]; linarith) (by rw [hs]; exact hshi) hz.1 hz.2
    (fun j => f (a j)) fun j => ?_
  rw [hs]
  obtain ⟨e1, e2, e3, e4, htm0, htm1, hrhoj⟩ := hmatch j
  obtain ⟨hAx, hAy⟩ := hA _ (haS j)
  refine pin_core_interior hm0 hms hbudget hAx hAy (hz.1 _) (hocc _ (haS j)) ?_
  have := coreSetP_subset_box htm0 htm1 hrhoj s''
  rw [e1, e2, e3, e4] at this
  exact this

/-- **Fixed-side slack-core certificate at `s″` ⟹ slab kill on `[lo, s″)`** whenever
`(s″/lo − 1)·A < ρ` (the slack-core grid). -/
theorem slabKill_of_case {c : CCertI} (hn : c.n = 11) (h : checkCaseI c = true) (hno : c.nofams = [])
    {S : PinSet} {A rho lo : ℝ} (hA0 : 0 ≤ A) (hlo0 : 0 < lo) (hlo : (caseSide c / lo - 1) * A < rho)
    (hA : ∀ a ∈ S, |slotAX a| ≤ A ∧ |slotAY a| ≤ A)
    (hcores : ∀ j : Fin c.cores.length, ∃ a ∈ S,
      ((c.cores.get j).kx : ℝ) = slotAX a + slotBX a * caseSide c ∧
      ((c.cores.get j).ky : ℝ) = slotAY a + slotBY a * caseSide c ∧
      (0 : ℝ) ≤ (c.cores.get j).tm ∧ ((c.cores.get j).tm : ℝ) ≤ 1 ∧
      rho ≤ 1 / 2 - ((c.cores.get j).a : ℝ) * (cosT (c.cores.get j).tm + sinT (c.cores.get j).tm)) :
    SlabKill S lo (caseSide c) := by
  intro m hlom hhi z hz hS
  have hm0 : 0 < m := lt_of_lt_of_le hlo0 hlom
  obtain ⟨f, -, hocc⟩ := hS
  choose a haS hmatch using hcores
  have hlam : 1 < caseSide c / m := by rw [lt_div_iff₀ hm0]; linarith
  have hs : caseSide c / m * m = caseSide c := by field_simp
  have hbudget : (caseSide c / m - 1) * A < rho := by
    refine lt_of_le_of_lt (mul_le_mul_of_nonneg_right ?_ hA0) hlo
    have : caseSide c / m ≤ caseSide c / lo :=
      div_le_div_of_nonneg_left (by linarith) hlo0 hlom
    linarith
  have hH : ∀ j : Fin c.cores.length,
      coreSet (c.cores.get j) ⊆ interior ((scaleC (caseSide c / m) (z (f (a j)))).set) := by
    intro j
    obtain ⟨e1, e2, htm0, htm1, hrhoj⟩ := hmatch j
    obtain ⟨hAx, hAy⟩ := hA _ (haS j)
    refine pin_core_interior hm0 hhi hbudget hAx hAy (hz.1 _) (hocc _ (haS j)) ?_
    have := coreSet_subset_box htm0 htm1 hrhoj
    rw [e1, e2] at this
    exact this
  rcases c with ⟨n, sNum, sDen, wd, depth, atoms, cores, nofams⟩
  have hn' : n = 11 := hn
  subst hn'
  exact lemma_B hlam hs.symm hz.1 hz.2 (fun j => coreSet (cores.get j)) (fun j => f (a j))
    (fun _Q hQ hI => checkCaseI_kill h hno hQ _ (fun j => (hI j).trans interior_subset)) hH

/-- **Single-corner certificate (all pins `β = 0`) ⟹ slab kill on `(0, s″)`** (C.M1: the
dilation is chosen arbitrarily close to `1`, so no drift budget is spent). -/
theorem slabKill_of_M1 {c : CCertI} (hn : c.n = 11) (h : checkCaseI c = true) (hno : c.nofams = [])
    {S : PinSet} {A rho lo : ℝ} (hA0 : 0 ≤ A) (hrho : 0 < rho) (hlo0 : 0 < lo)
    (hA : ∀ a ∈ S, |slotAX a| ≤ A ∧ |slotAY a| ≤ A)
    (hβ : ∀ a ∈ S, slotBX a = 0 ∧ slotBY a = 0)
    (hcores : ∀ j : Fin c.cores.length, ∃ a ∈ S,
      ((c.cores.get j).kx : ℝ) = slotAX a ∧ ((c.cores.get j).ky : ℝ) = slotAY a ∧
      (0 : ℝ) ≤ (c.cores.get j).tm ∧ ((c.cores.get j).tm : ℝ) ≤ 1 ∧
      rho ≤ 1 / 2 - ((c.cores.get j).a : ℝ) * (cosT (c.cores.get j).tm + sinT (c.cores.get j).tm)) :
    SlabKill S lo (caseSide c) := by
  intro m hlom hhi z hz hS
  have hm0 : 0 < m := lt_of_lt_of_le hlo0 hlom
  obtain ⟨s'', hms, hshi, hbudget⟩ := exists_side hm0 hhi hA0 hrho
  obtain ⟨f, -, hocc⟩ := hS
  choose a haS hmatch using hcores
  have hlam : 1 < s'' / m := by rw [lt_div_iff₀ hm0]; linarith
  have hs : s'' / m * m = s'' := by field_simp
  refine M1_transfer_packing hn h hno hlam (by rw [hs]; exact hshi) hz.1 hz.2 (fun j => f (a j))
    fun j => ?_
  obtain ⟨e1, e2, htm0, htm1, hrhoj⟩ := hmatch j
  obtain ⟨hAx, hAy⟩ := hA _ (haS j)
  obtain ⟨hbx, hby⟩ := hβ _ (haS j)
  refine pin_core_interior hm0 hms hbudget hAx hAy (hz.1 _) (hocc _ (haS j)) ?_
  have := coreSet_subset_box htm0 htm1 hrhoj
  rw [e1, e2] at this
  rw [hbx, hby, zero_mul, add_zero, add_zero]
  exact this

/-! ## From a slab reaching the window to the `stratum_kill` instance -/

/-- A slab `[lo, hi)` with `lo ≤ 3.82 < ŝ < hi` kills the class of every representative
containing `S` up to `D4`, at every side of the window (`class_kill`). -/
theorem windowKilled_of_slab {i : StratumIdx} {S : PinSet} {g : D4}
    (hS : S ⊆ d4Pins g (classRep i)) {lo hi : ℝ} (h : SlabKill S lo hi)
    (hlo : lo ≤ 191 / 50) (hhi : shat < hi) :
    ∀ m ∈ wnd, ∀ z : Cfg, CfgPacking m z → ¬InStratum i m z := by
  intro m hm z hz hcls
  have h3 := (wnd_subset_Ioo hm).1
  have h4 := (wnd_subset_Ioo hm).2
  exact class_kill h3 h4 (classRep i) S g hS
    (fun z' ht' hP' => h m (le_trans hlo hm.1) (lt_of_le_of_lt hm.2 hhi) z' ⟨ht', hP'⟩)
    z hz.1 hz.2 hcls

/-! ## The replayed pilot: `k5_06.param` over the whole census window -/

/-- The five pin slots of `k5_06`: `(½,½), (½,3/2), (½,5/2)` at BL and `(s−½,½), (s−½,3/2)` at BR. -/
def k506Pins : PinSet := {⟨0, 0, 0⟩, ⟨0, 0, 1⟩, ⟨0, 0, 2⟩, ⟨1, 0, 0⟩, ⟨1, 0, 1⟩}

theorem k506_A : ∀ a ∈ k506Pins, |slotAX a| ≤ 5 / 2 ∧ |slotAY a| ≤ 5 / 2 := by
  intro a ha
  simp only [k506Pins, Finset.mem_insert, Finset.mem_singleton] at ha
  rcases ha with rfl | rfl | rfl | rfl | rfl <;>
    simp [slotAX, slotAY, cornerR, cornerT] <;> norm_num

/-- The core margin of the k5_06 pilot: `ρ = 10⁻⁹ ≤ ½ − a·(cosT tm + sinT tm)` with
`tm = 2⁻²⁵`, `a = 16383999967232/32768001953125` (the corpus margin ≈ 1.0000009e-9, A63). -/
theorem k506_margin :
    (1 / 10 ^ 9 : ℝ) ≤ 1 / 2 - ((16383999967232 : ℚ) / 32768001953125 : ℝ)
      * (cosT (((1 : ℚ) / 33554432 : ℚ) : ℝ) + sinT (((1 : ℚ) / 33554432 : ℚ) : ℝ)) := by
  unfold cosT sinT
  push_cast
  norm_num

theorem k5_06_cores : ∀ j : Fin Data.k5_06_param.cores.length, ∃ a ∈ k506Pins,
    ((Data.k5_06_param.cores.get j).akx : ℝ) = slotAX a ∧
    ((Data.k5_06_param.cores.get j).bkx : ℝ) = slotBX a ∧
    ((Data.k5_06_param.cores.get j).aky : ℝ) = slotAY a ∧
    ((Data.k5_06_param.cores.get j).bky : ℝ) = slotBY a ∧
    (0 : ℝ) ≤ (Data.k5_06_param.cores.get j).tm ∧ ((Data.k5_06_param.cores.get j).tm : ℝ) ≤ 1 ∧
    (1 / 10 ^ 9 : ℝ) ≤ 1 / 2 - ((Data.k5_06_param.cores.get j).a : ℝ)
      * (cosT (Data.k5_06_param.cores.get j).tm + sinT (Data.k5_06_param.cores.get j).tm) := by
  intro j
  fin_cases j
  · refine ⟨⟨0, 0, 0⟩, by simp [k506Pins], ?_⟩
    simp [Data.k5_06_param, slotAX, slotBX, slotAY, slotBY, cornerR, cornerT] <;>
      norm_num [cosT, sinT]
  · refine ⟨⟨0, 0, 1⟩, by simp [k506Pins], ?_⟩
    simp [Data.k5_06_param, slotAX, slotBX, slotAY, slotBY, cornerR, cornerT] <;>
      norm_num [cosT, sinT]
  · refine ⟨⟨0, 0, 2⟩, by simp [k506Pins], ?_⟩
    simp [Data.k5_06_param, slotAX, slotBX, slotAY, slotBY, cornerR, cornerT] <;>
      norm_num [cosT, sinT]
  · refine ⟨⟨1, 0, 0⟩, by simp [k506Pins], ?_⟩
    simp [Data.k5_06_param, slotAX, slotBX, slotAY, slotBY, cornerR, cornerT] <;>
      norm_num [cosT, sinT]
  · refine ⟨⟨1, 0, 1⟩, by simp [k506Pins], ?_⟩
    simp [Data.k5_06_param, slotAX, slotBX, slotAY, slotBY, cornerR, cornerT] <;>
      norm_num [cosT, sinT]

/-- **The k5_06 window row, composed**: the pin set is killed on `[3.82, s0)`, from the
Lean replay of `k5_06.param` (`ParamK506.lean`). -/
theorem k5_06_slab : SlabKill k506Pins (191 / 50) (969271 / 250000) := by
  have h := slabKill_of_param (c := Data.k5_06_param) rfl check_k5_06_param (S := k506Pins)
    (A := 5 / 2) (rho := 1 / 10 ^ 9) (by norm_num) (by norm_num)
    (by rw [k5_06_param_lo]; norm_num) k506_A k5_06_cores
  rw [k5_06_param_lo, k5_06_param_hi] at h
  exact h

end

end S11
end PackingCert
