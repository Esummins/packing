import PackingCertMathlib.AtlasKernel
import PackingCertMathlib.Dilation
import PackingCertMathlib.CaseHyp
import PackingCertMathlib.Census

/-!
# Soundness of the atlas-value box checker (A86 T2)

`atlas_kill`: `checkAtlas a = true` ⟹ every configuration whose 11 squares lie in the
certificate's boxes needs a container of side `≥ L` — i.e. no packing at ANY side `s < L`
lies in the box.  With `L ≥ s0` this is the (D′) leaf of `docs/proofs/k0_route.md` §4.3:

* `atlas_dilated_kill` (Lemma K0-ATLAS) — no packing at a side `m < s0` has its
  `Δ_{s0/m}`-dilate inside an `L ≥ s0` box: the dilate's extent is `≤ s0 − (λ − 1) < s0`
  (its centres stay `≥ ½` and `≤ m − ½`, so both extreme corners move strictly inward);
  no dilation bookkeeping enters the certificate, and every side `m ∈ [3.82, ŝ]` is
  covered at once (`ŝ < s0`).

The checker's only arithmetic is the corner enclosure `cx + hx·cosT t − hy·sinT t` over the
box (`cosT` antitone, `sinT` monotone on `[0, 1]`, `MeasureBridge.lean`), stated in the
composition's own `(cx, cy, t)` coordinates.
-/

namespace PackingCert.Atlas

open PackingCert PackingCert.S11 Set
open PackingCert.CaseI (rabs rmin rmax)

/-- The square's parameters lie in the box. -/
def InABox (b : ABox) (q : PSq) : Prop :=
  (b.x0 : ℝ) ≤ q.cx ∧ q.cx ≤ (b.x1 : ℝ) ∧ (b.y0 : ℝ) ≤ q.cy ∧ q.cy ≤ (b.y1 : ℝ) ∧
    (b.t0 : ℝ) ≤ q.t ∧ q.t ≤ (b.t1 : ℝ)

/-- The configuration lies in the certificate's 11 boxes. -/
def InAtlas (a : AtlasCert) (z : Fin 11 → PSq) : Prop :=
  ∀ i : Fin 11, InABox (a.boxes.getD i default) (z i)

/-- Corner `k` of a parametrised square (body offsets `(hx, hy) ∈ {±½}²`). -/
noncomputable def cornerPt (q : PSq) (k : ℕ) : RP :=
  (q.cx + (hxA k : ℝ) * cosT q.t - (hyA k : ℝ) * sinT q.t,
   q.cy + (hxA k : ℝ) * sinT q.t + (hyA k : ℝ) * cosT q.t)

theorem hxA_cases (k : ℕ) : (hxA k : ℝ) = -1 / 2 ∨ (hxA k : ℝ) = 1 / 2 := by
  unfold hxA; split_ifs <;> simp

theorem hyA_cases (k : ℕ) : (hyA k : ℝ) = -1 / 2 ∨ (hyA k : ℝ) = 1 / 2 := by
  unfold hyA; split_ifs <;> simp

theorem abs_hxA (k : ℕ) : |(hxA k : ℝ)| ≤ 1 / 2 := by
  rcases hxA_cases k with h | h <;> rw [h] <;> norm_num

theorem abs_hyA (k : ℕ) : |(hyA k : ℝ)| ≤ 1 / 2 := by
  rcases hyA_cases k with h | h <;> rw [h] <;> norm_num

/-- Every corner lies in the square. -/
theorem cornerPt_mem (q : PSq) (k : ℕ) : cornerPt q k ∈ q.set := by
  rw [mem_set_iff_uv]
  have hcs := cosT_sq_add_sinT_sq q.t
  simp only [cornerPt, rdot, edir, perpV]
  have e1 : (q.cx + (hxA k : ℝ) * cosT q.t - (hyA k : ℝ) * sinT q.t - q.cx) * cosT q.t
      + (q.cy + (hxA k : ℝ) * sinT q.t + (hyA k : ℝ) * cosT q.t - q.cy) * sinT q.t = (hxA k : ℝ) := by
    linear_combination (hxA k : ℝ) * hcs
  have e2 : (q.cx + (hxA k : ℝ) * cosT q.t - (hyA k : ℝ) * sinT q.t - q.cx) * -sinT q.t
      + (q.cy + (hxA k : ℝ) * sinT q.t + (hyA k : ℝ) * cosT q.t - q.cy) * cosT q.t = (hyA k : ℝ) := by
    linear_combination (hyA k : ℝ) * hcs
  rw [e1, e2]
  exact ⟨abs_hxA k, abs_hyA k⟩

theorem cosQ_cast (t : ℚ) : ((cosQ t : ℚ) : ℝ) = cosT (t : ℝ) := by
  unfold cosQ cosT; push_cast; ring

theorem sinQ_cast (t : ℚ) : ((sinQ t : ℚ) : ℝ) = sinT (t : ℝ) := by
  unfold sinQ sinT; push_cast; ring

/-- The point-times-interval product enclosure. -/
theorem mulI_pt_sound {h b0 b1 : ℚ} {y : ℝ} (hb0 : (b0 : ℝ) ≤ y) (hb1 : y ≤ (b1 : ℝ)) :
    ((mulI h h b0 b1).1 : ℝ) ≤ (h : ℝ) * y ∧ (h : ℝ) * y ≤ ((mulI h h b0 b1).2 : ℝ) := by
  simp only [mulI, rmin_cast, rmax_cast]
  push_cast
  rcases le_or_gt 0 (h : ℝ) with hh | hh
  · have h1 : (h : ℝ) * b0 ≤ (h : ℝ) * y := mul_le_mul_of_nonneg_left hb0 hh
    have h2 : (h : ℝ) * y ≤ (h : ℝ) * b1 := mul_le_mul_of_nonneg_left hb1 hh
    constructor
    · exact le_trans (min_le_left _ _) (le_trans (min_le_left _ _) h1)
    · exact le_trans h2 (le_trans (le_max_right _ _) (le_max_right _ _))
  · have h1 : (h : ℝ) * y ≤ (h : ℝ) * b0 := mul_le_mul_of_nonpos_left hb0 hh.le
    have h2 : (h : ℝ) * b1 ≤ (h : ℝ) * y := mul_le_mul_of_nonpos_left hb1 hh.le
    constructor
    · exact le_trans (min_le_left _ _) (le_trans (min_le_right _ _) h2)
    · exact le_trans h1 (le_trans (le_max_left _ _) (le_max_right _ _))

theorem boxOK_parts {b : ABox} (h : boxOK b = true) :
    0 ≤ b.t0 ∧ b.t0 ≤ b.t1 ∧ b.t1 ≤ 1 ∧ b.x0 ≤ b.x1 ∧ b.y0 ≤ b.y1 := by
  simp only [boxOK, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩ := h
  exact ⟨h1, h2, h3, h4, h5⟩

/-- Trigonometric enclosures over the box's tilt interval. -/
theorem trig_box {b : ABox} (hb : boxOK b = true) {q : PSq} (hq : InABox b q) :
    ((cosQ b.t1 : ℚ) : ℝ) ≤ cosT q.t ∧ cosT q.t ≤ ((cosQ b.t0 : ℚ) : ℝ) ∧
    ((sinQ b.t0 : ℚ) : ℝ) ≤ sinT q.t ∧ sinT q.t ≤ ((sinQ b.t1 : ℚ) : ℝ) := by
  obtain ⟨ht0, ht01, ht1, -, -⟩ := boxOK_parts hb
  obtain ⟨-, -, -, -, hq0, hq1⟩ := hq
  have ht0' : (0 : ℝ) ≤ b.t0 := by exact_mod_cast ht0
  have ht1' : (b.t1 : ℝ) ≤ 1 := by exact_mod_cast ht1
  rw [cosQ_cast, cosQ_cast, sinQ_cast, sinQ_cast]
  exact ⟨cosT_anti (by linarith) hq1, cosT_anti ht0' hq0, sinT_mono ht0' hq0 (by linarith),
    sinT_mono (by linarith) hq1 ht1'⟩

/-- The `x`-coordinate of corner `k` is enclosed by `cornerXI`. -/
theorem cornerXI_sound {b : ABox} (hb : boxOK b = true) {q : PSq} (hq : InABox b q) (k : ℕ) :
    ((cornerXI b k).1 : ℝ) ≤ (cornerPt q k).1 ∧ (cornerPt q k).1 ≤ ((cornerXI b k).2 : ℝ) := by
  obtain ⟨c1, c2, s1, s2⟩ := trig_box hb hq
  obtain ⟨hx0, hx1, -, -, -, -⟩ := hq
  have hc := mulI_pt_sound (h := hxA k) c1 c2
  have hs := mulI_pt_sound (h := hyA k) s1 s2
  simp only [cornerXI, cornerPt]
  push_cast
  constructor <;> linarith [hc.1, hc.2, hs.1, hs.2]

/-- The `y`-coordinate of corner `k` is enclosed by `cornerYI`. -/
theorem cornerYI_sound {b : ABox} (hb : boxOK b = true) {q : PSq} (hq : InABox b q) (k : ℕ) :
    ((cornerYI b k).1 : ℝ) ≤ (cornerPt q k).2 ∧ (cornerPt q k).2 ≤ ((cornerYI b k).2 : ℝ) := by
  obtain ⟨c1, c2, s1, s2⟩ := trig_box hb hq
  obtain ⟨-, -, hy0, hy1, -, -⟩ := hq
  have hs := mulI_pt_sound (h := hxA k) s1 s2
  have hc := mulI_pt_sound (h := hyA k) c1 c2
  simp only [cornerYI, cornerPt]
  push_cast
  constructor <;> linarith [hc.1, hc.2, hs.1, hs.2]

theorem checkAtlas_parts {a : AtlasCert} (h : checkAtlas a = true) :
    a.boxes.size = 11 ∧ (∀ b ∈ a.boxes, boxOK b = true) ∧ ∃ w ∈ a.wits, witOK a w = true := by
  simp only [checkAtlas, Bool.and_eq_true, decide_eq_true_eq, Array.all_eq_true_iff_forall_mem,
    Array.any_eq_true] at h
  obtain ⟨⟨h1, h2⟩, h3⟩ := h
  refine ⟨h1, h2, ?_⟩
  obtain ⟨i, hi, hw⟩ := h3
  exact ⟨a.wits[i], Array.getElem_mem hi, hw⟩

theorem box_of_mem {a : AtlasCert} (h : checkAtlas a = true) (i : Fin 11) :
    boxOK (a.boxes.getD i default) = true := by
  obtain ⟨hs, hb, -⟩ := checkAtlas_parts h
  have hi : (i : ℕ) < a.boxes.size := by rw [hs]; exact i.isLt
  have e : a.boxes.getD i default = a.boxes[(i : ℕ)] := by simp [Array.getD, hi]
  rw [e]
  exact hb _ (Array.getElem_mem hi)

/-- **The extent theorem**: a witnessed lower bound on a corner difference. -/
theorem atlas_extent {a : AtlasCert} (h : checkAtlas a = true) {z : Fin 11 → PSq}
    (hz : InAtlas a z) :
    ∃ (i1 i2 : Fin 11) (k1 k2 : ℕ) (ax : Bool),
      (a.L : ℝ) ≤ (if ax then (cornerPt (z i1) k1).1 - (cornerPt (z i2) k2).1
        else (cornerPt (z i1) k1).2 - (cornerPt (z i2) k2).2) := by
  obtain ⟨hs, -, w, -, hw⟩ := checkAtlas_parts h
  simp only [witOK, Bool.and_eq_true, decide_eq_true_eq] at hw
  obtain ⟨⟨⟨⟨hi1, hi2⟩, -⟩, -⟩, hL⟩ := hw
  refine ⟨⟨w.i1, hi1⟩, ⟨w.i2, hi2⟩, w.k1, w.k2, w.axisX, ?_⟩
  have hL' : (a.L : ℝ) ≤ ((witBound a w : ℚ) : ℝ) := by exact_mod_cast hL
  have hb1 := box_of_mem h ⟨w.i1, hi1⟩
  have hb2 := box_of_mem h ⟨w.i2, hi2⟩
  have hz1 := hz ⟨w.i1, hi1⟩
  have hz2 := hz ⟨w.i2, hi2⟩
  unfold witBound at hL'
  split_ifs at hL' ⊢ with hax
  · have e1 := (cornerXI_sound hb1 hz1 w.k1).1
    have e2 := (cornerXI_sound hb2 hz2 w.k2).2
    push_cast at hL'
    linarith
  · have e1 := (cornerYI_sound hb1 hz1 w.k1).1
    have e2 := (cornerYI_sound hb2 hz2 w.k2).2
    push_cast at hL'
    linarith

/-- **Atlas soundness, packing form**: no packing at a side `s < L` lies in the box. -/
theorem atlas_kill {a : AtlasCert} (h : checkAtlas a = true) {z : Fin 11 → PSq} (hz : InAtlas a z)
    {s : ℝ} (hP : IsPacking 11 s fun i => (z i).set) : (a.L : ℝ) ≤ s := by
  obtain ⟨i1, i2, k1, k2, ax, hL⟩ := atlas_extent h hz
  have h1 := hP.contained i1 (cornerPt_mem (z i1) k1)
  have h2 := hP.contained i2 (cornerPt_mem (z i2) k2)
  simp only [container, mem_prod, mem_Icc] at h1 h2
  split_ifs at hL <;> linarith [h1.1.1, h1.1.2, h1.2.1, h1.2.2, h2.1.1, h2.1.2, h2.2.1, h2.2.2]

/-- **Lemma K0-ATLAS (the (D′) leaf)**: with `L ≥ s0`, no packing at a side `m < s0` has its
`Δ_{s0/m}`-dilate inside the box.  The dilate's corners satisfy
`corner = λ·c + off` with `c ∈ [½, m − ½]` and `c + off ∈ [0, m]`, so its extent is at most
`s0 − (λ − 1) < s0 ≤ L`. -/
theorem atlas_dilated_kill {a : AtlasCert} (h : checkAtlas a = true) {s0 : ℝ}
    (hL : s0 ≤ (a.L : ℝ)) {P : Fin 11 → PSq} {m : ℝ} (hm : 0 < m) (hms : m < s0)
    (ht : ∀ i, (P i).t ∈ Icc (0 : ℝ) 1) (hP : IsPacking 11 m fun i => (P i).set)
    (hz : InAtlas a fun i => scaleC (s0 / m) (P i)) : False := by
  obtain ⟨i1, i2, k1, k2, ax, hLw⟩ := atlas_extent h hz
  set lam : ℝ := s0 / m with hlam
  have hlam1 : 1 < lam := by rw [hlam, lt_div_iff₀ hm]; linarith
  have hlm : lam * m = s0 := by rw [hlam]; field_simp
  -- the centres of `P` are at least `½` from the walls, the corners inside
  have hcen : ∀ i : Fin 11, 1 / 2 ≤ (P i).cx ∧ (P i).cx ≤ m - 1 / 2 ∧
      1 / 2 ≤ (P i).cy ∧ (P i).cy ≤ m - 1 / 2 := by
    intro i
    obtain ⟨b1, b2, b3, b4⟩ := (set_subset_container_iff (ht i).1 (ht i).2 m).mp (hP.contained i)
    have hw := wT_ge_one (ht i).1 (ht i).2
    exact ⟨by linarith, by linarith, by linarith, by linarith⟩
  have hcor : ∀ (i : Fin 11) (k : ℕ), 0 ≤ (cornerPt (P i) k).1 ∧ (cornerPt (P i) k).1 ≤ m ∧
      0 ≤ (cornerPt (P i) k).2 ∧ (cornerPt (P i) k).2 ≤ m := by
    intro i k
    have := hP.contained i (cornerPt_mem (P i) k)
    simp only [container, mem_prod, mem_Icc] at this
    exact ⟨this.1.1, this.1.2, this.2.1, this.2.2⟩
  -- dilated corners in terms of the original ones
  have hdx : ∀ (i : Fin 11) (k : ℕ), (cornerPt (scaleC lam (P i)) k).1
      = (lam - 1) * (P i).cx + (cornerPt (P i) k).1 := by
    intro i k; simp only [cornerPt, scaleC]; ring
  have hdy : ∀ (i : Fin 11) (k : ℕ), (cornerPt (scaleC lam (P i)) k).2
      = (lam - 1) * (P i).cy + (cornerPt (P i) k).2 := by
    intro i k; simp only [cornerPt, scaleC]; ring
  have hl1 : 0 < lam - 1 := by linarith
  obtain ⟨c11, c12, c13, c14⟩ := hcen i1
  obtain ⟨c21, c22, c23, c24⟩ := hcen i2
  obtain ⟨d11, d12, d13, d14⟩ := hcor i1 k1
  obtain ⟨d21, d22, d23, d24⟩ := hcor i2 k2
  split_ifs at hLw with hax
  · rw [hdx, hdx] at hLw
    nlinarith [mul_le_mul_of_nonneg_left c12 hl1.le, mul_le_mul_of_nonneg_left c21 hl1.le]
  · rw [hdy, hdy] at hLw
    nlinarith [mul_le_mul_of_nonneg_left c14 hl1.le, mul_le_mul_of_nonneg_left c23 hl1.le]

/-! ## The tilt fold (the emitted boxes live at `θ ∈ [0, π/4]`)

The A37/A85 boxes are re-emitted with every square's tilt folded into `[0, π/4]`
(`attempts/A86-lean-wave7/notes/t2_atlas.md` §2): `θ ↦ π/2 − θ` (`t ↦ tRefl t`) swaps
`cos` and `sin`, which permutes the set of corner `x`-coordinates (and the set of corner
`y`-coordinates) of the square without changing either set.  The folded configuration is
NOT a packing in general (the squares are mirrored), but the extent bound only reads
corner coordinates, so a box containing the FOLDED configuration still bounds the side. -/

/-- The fold `t ↦ min t (tRefl t)` (`θ ↦ min θ (π/2 − θ)`). -/
noncomputable def foldT (t : ℝ) : ℝ := min t (tRefl t)

/-- The square with its tilt folded. -/
noncomputable def foldSq (q : PSq) : PSq := ⟨q.cx, q.cy, foldT q.t⟩

theorem foldT_cases (t : ℝ) : foldT t = t ∨ foldT t = tRefl t := by
  unfold foldT
  rcases le_total t (tRefl t) with h | h
  · left; exact min_eq_left h
  · right; exact min_eq_right h

/-- Every corner `x`-coordinate of the folded square is a corner `x`-coordinate of the
square. -/
theorem cornerPt_fold_x (q : PSq) (ht : 0 ≤ q.t) (k : ℕ) :
    ∃ k' : ℕ, (cornerPt (foldSq q) k).1 = (cornerPt q k').1 := by
  rcases foldT_cases q.t with h | h
  · exact ⟨k, by simp only [cornerPt, foldSq, h]⟩
  · simp only [cornerPt, foldSq, h, cosT_tRefl ht, sinT_tRefl ht]
    -- `cx + hx·sin − hy·cos = cx + hx'·cos − hy'·sin` with `(hx', hy') = (−hy, −hx)`
    have hk : ∀ k : ℕ, ∃ k' : ℕ, (hxA k' : ℝ) = -(hyA k) ∧ (hyA k' : ℝ) = -(hxA k) := by
      intro k
      by_cases h0 : k = 0 ∨ k = 3
      · by_cases h1 : k = 0 ∨ k = 1
        · -- k = 0 : (−,−) ↦ (+,+) = 2
          refine ⟨2, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
        · -- k = 3 : (−,+) ↦ (−,+) = 3
          refine ⟨3, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
      · by_cases h1 : k = 0 ∨ k = 1
        · -- k = 1 : (+,−) ↦ (+,−) = 1
          refine ⟨1, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
        · -- k = 2 : (+,+) ↦ (−,−) = 0
          refine ⟨0, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
    obtain ⟨k', e1, e2⟩ := hk k
    refine ⟨k', ?_⟩
    rw [e1, e2]; ring

/-- Every corner `y`-coordinate of the folded square is a corner `y`-coordinate of the
square. -/
theorem cornerPt_fold_y (q : PSq) (ht : 0 ≤ q.t) (k : ℕ) :
    ∃ k' : ℕ, (cornerPt (foldSq q) k).2 = (cornerPt q k').2 := by
  rcases foldT_cases q.t with h | h
  · exact ⟨k, by simp only [cornerPt, foldSq, h]⟩
  · simp only [cornerPt, foldSq, h, cosT_tRefl ht, sinT_tRefl ht]
    -- `cy + hx·cos + hy·sin = cy + hx'·sin + hy'·cos` with `(hx', hy') = (hy, hx)`
    have hk : ∀ k : ℕ, ∃ k' : ℕ, (hxA k' : ℝ) = hyA k ∧ (hyA k' : ℝ) = hxA k := by
      intro k
      by_cases h0 : k = 0 ∨ k = 3
      · by_cases h1 : k = 0 ∨ k = 1
        · refine ⟨0, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
        · refine ⟨1, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
      · by_cases h1 : k = 0 ∨ k = 1
        · refine ⟨3, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
        · refine ⟨2, ?_, ?_⟩ <;> simp [hxA, hyA, h0, h1] <;> norm_num
    obtain ⟨k', e1, e2⟩ := hk k
    refine ⟨k', ?_⟩
    rw [e1, e2]; ring

/-- **Atlas soundness, folded form**: a box containing the folded configuration of a packing
at side `s` forces `L ≤ s`. -/
theorem atlas_kill_fold {a : AtlasCert} (h : checkAtlas a = true) {z : Fin 11 → PSq}
    (ht : ∀ i, 0 ≤ (z i).t) (hz : InAtlas a fun i => foldSq (z i))
    {s : ℝ} (hP : IsPacking 11 s fun i => (z i).set) : (a.L : ℝ) ≤ s := by
  obtain ⟨i1, i2, k1, k2, ax, hL⟩ := atlas_extent h hz
  split_ifs at hL with hax
  · obtain ⟨k1', e1⟩ := cornerPt_fold_x (z i1) (ht i1) k1
    obtain ⟨k2', e2⟩ := cornerPt_fold_x (z i2) (ht i2) k2
    rw [e1, e2] at hL
    have h1 := hP.contained i1 (cornerPt_mem (z i1) k1')
    have h2 := hP.contained i2 (cornerPt_mem (z i2) k2')
    simp only [container, mem_prod, mem_Icc] at h1 h2
    linarith [h1.1.2, h2.1.1]
  · obtain ⟨k1', e1⟩ := cornerPt_fold_y (z i1) (ht i1) k1
    obtain ⟨k2', e2⟩ := cornerPt_fold_y (z i2) (ht i2) k2
    rw [e1, e2] at hL
    have h1 := hP.contained i1 (cornerPt_mem (z i1) k1')
    have h2 := hP.contained i2 (cornerPt_mem (z i2) k2')
    simp only [container, mem_prod, mem_Icc] at h1 h2
    linarith [h1.2.2, h2.2.1]

/-- **Lemma K0-ATLAS, folded form** (the (D′) leaf as emitted): no packing at a side
`m < s0` has the FOLDED `Δ_{s0/m}`-dilate inside an `L ≥ s0` box. -/
theorem atlas_dilated_kill_fold {a : AtlasCert} (h : checkAtlas a = true) {s0 : ℝ}
    (hL : s0 ≤ (a.L : ℝ)) {P : Fin 11 → PSq} {m : ℝ} (hm : 0 < m) (hms : m < s0)
    (ht : ∀ i, (P i).t ∈ Icc (0 : ℝ) 1) (hP : IsPacking 11 m fun i => (P i).set)
    (hz : InAtlas a fun i => foldSq (scaleC (s0 / m) (P i))) : False := by
  obtain ⟨i1, i2, k1, k2, ax, hLw⟩ := atlas_extent h hz
  set lam : ℝ := s0 / m with hlam
  have hlam1 : 1 < lam := by rw [hlam, lt_div_iff₀ hm]; linarith
  have hcen : ∀ i : Fin 11, 1 / 2 ≤ (P i).cx ∧ (P i).cx ≤ m - 1 / 2 ∧
      1 / 2 ≤ (P i).cy ∧ (P i).cy ≤ m - 1 / 2 := by
    intro i
    obtain ⟨b1, b2, b3, b4⟩ := (set_subset_container_iff (ht i).1 (ht i).2 m).mp (hP.contained i)
    have hw := wT_ge_one (ht i).1 (ht i).2
    exact ⟨by linarith, by linarith, by linarith, by linarith⟩
  have hcor : ∀ (i : Fin 11) (k : ℕ), 0 ≤ (cornerPt (P i) k).1 ∧ (cornerPt (P i) k).1 ≤ m ∧
      0 ≤ (cornerPt (P i) k).2 ∧ (cornerPt (P i) k).2 ≤ m := by
    intro i k
    have := hP.contained i (cornerPt_mem (P i) k)
    simp only [container, mem_prod, mem_Icc] at this
    exact ⟨this.1.1, this.1.2, this.2.1, this.2.2⟩
  have hdx : ∀ (i : Fin 11) (k : ℕ), (cornerPt (scaleC lam (P i)) k).1
      = (lam - 1) * (P i).cx + (cornerPt (P i) k).1 := by
    intro i k; simp only [cornerPt, scaleC]; ring
  have hdy : ∀ (i : Fin 11) (k : ℕ), (cornerPt (scaleC lam (P i)) k).2
      = (lam - 1) * (P i).cy + (cornerPt (P i) k).2 := by
    intro i k; simp only [cornerPt, scaleC]; ring
  have hl1 : 0 < lam - 1 := by linarith
  have hlm : lam * m = s0 := by rw [hlam]; field_simp
  have hts : ∀ i, 0 ≤ (scaleC lam (P i)).t := fun i => (ht i).1
  obtain ⟨c11, c12, c13, c14⟩ := hcen i1
  obtain ⟨c21, c22, c23, c24⟩ := hcen i2
  split_ifs at hLw with hax
  · obtain ⟨k1', e1⟩ := cornerPt_fold_x (scaleC lam (P i1)) (hts i1) k1
    obtain ⟨k2', e2⟩ := cornerPt_fold_x (scaleC lam (P i2)) (hts i2) k2
    rw [e1, e2, hdx, hdx] at hLw
    obtain ⟨d11, d12, d13, d14⟩ := hcor i1 k1'
    obtain ⟨d21, d22, d23, d24⟩ := hcor i2 k2'
    nlinarith [mul_le_mul_of_nonneg_left c12 hl1.le, mul_le_mul_of_nonneg_left c21 hl1.le]
  · obtain ⟨k1', e1⟩ := cornerPt_fold_y (scaleC lam (P i1)) (hts i1) k1
    obtain ⟨k2', e2⟩ := cornerPt_fold_y (scaleC lam (P i2)) (hts i2) k2
    rw [e1, e2, hdy, hdy] at hLw
    obtain ⟨d11, d12, d13, d14⟩ := hcor i1 k1'
    obtain ⟨d21, d22, d23, d24⟩ := hcor i2 k2'
    nlinarith [mul_le_mul_of_nonneg_left c14 hl1.le, mul_le_mul_of_nonneg_left c23 hl1.le]

end PackingCert.Atlas
