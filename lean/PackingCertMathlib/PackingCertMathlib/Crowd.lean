import PackingCertMathlib.ZoneTree
import PackingCertMathlib.Selection
import PackingCertMathlib.WindowRows

/-!
# The crowd-weighted certificate: Lemma B-YES and Lemma CW (A93 T1, depgraph K0.CW)

`docs/proofs/k0_blocked_side.md` §2.3–2.4.  A crowd certificate `C(δ, m_lo)` is ONE atomic
measure on `[0, s0]²` checked by TWO runs of the frozen `verify_case.py` (Lean: `checkCaseI`,
V.CASE):

* run A — the plain certificate with `n = 11 + 8e` (no cores, no NO-families): PASS gives
  `μ(Q) ≥ 1` for every admissible closed unit square and `μ(total) < 11 + 8e`
  (`checkCaseI_price` + `checkCaseI_facts`);
* run B — the same atoms with weights `w/(1+e)` and the exact complement `E` of the crowd
  family as NO-families: PASS gives `μ(Q) ≥ 1 + e` for every admissible `Q` lying in no
  NO-zone (`checkCaseI_price` with the exemption clause).

The hypotheses connecting the two files are decidable and stated as such: `sameMeasure`
(same atom points, weights in the exact ratio `1 + e`) and — in `CrowdZone.lean` — the
zone checker certifying that every NO-zone of run B is disjoint from the crowd family
`F_c(a_w) = {Q : Q meets the closed corner box [0, a_w]²}` at every corner.

* `cframe`, `cornerBox` — the corner frame and the closed corner box `[0,a]²` at corner `c`;
  `muC` is A90's `μ_c(Q) = min_{p ∈ Q} max(p_x, p_y)` (attained, `exists_min_gcf`), and
  `meets_cornerBox_iff_muC_le` is the [T] equivalence "`μ_c(Q) ≤ a` ⟺ `Q` meets `[0,a]²`
  (closed)"; the crowd hypothesis "second intruder at depth `≥ δ`" is exactly
  `CrowdBox m (1 − δ) z` (two distinct squares meeting the closed box `[0, 1−δ]²` at every
  corner).
* `scaleC_meets_cornerBox` — **Lemma B-YES**: the dilate `Δ_λ Q` of a square meeting
  `[0, a]²` at side `m` meets `[0, λa + (λ−1)·r]²` at side `λm`, for any `r ≥ wT/2`
  (`r = 7072/10000 ≥ √2/2` in the emitted certificates, `wT_le_bound`).
* `not_meets_two_corners` — two corner boxes of size `a_w` are `> √2` apart when
  `(s0 − 2a_w)² > 2`, so a unit square meets at most one of them (the "8 distinct crowd
  squares" step).
* `crowd_sound` — **Lemma CW**: the weight arithmetic.  Eight crowd members priced
  `≥ (1+e)·wd` (run B) and three more priced `≥ wd` (run A) sum to `≥ (11 + 8e)·wd`, while
  disjointness bounds the sum by the total `< n·wd ≤ (11 + 8e)·wd`.
* `crowd_cert_kill` — **Theorem S(δ) in window form**: no packing at any side
  `m ∈ [m_lo, s0)` has two distinct squares meeting the closed box `[0, a]²` at every
  corner, when `a_w ≥ (s0/m_lo)·a + (s0/m_lo − 1)·r` (the pad of the window).
* `sameMeasure` / `sameMeasure_sound` — the decidable "one measure, two files" check.

Axioms: `propext, Classical.choice, Quot.sound` (the checker evaluations enter only through
the `checkCaseI … = true` hypotheses, per certificate file).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set MeasureI CaseI

/-! ## Corner frames and corner boxes -/

/-- Corner-frame coordinates: corner `c` of `[0,s]²` is sent to the origin with the container
in the positive quadrant (a coordinatewise reflection; the swap of the D4 frame is not
needed for boxes). -/
def cframe (s : ℝ) (c : Fin 4) (p : RP) : RP :=
  (if cornerR c then s - p.1 else p.1, if cornerT c then s - p.2 else p.2)

/-- The closed box `[0,a]²` at corner `c` of `[0,s]²`, in container coordinates. -/
def cornerBox (s a : ℝ) (c : Fin 4) : Set RP :=
  {p | 0 ≤ (cframe s c p).1 ∧ (cframe s c p).1 ≤ a ∧ 0 ≤ (cframe s c p).2 ∧ (cframe s c p).2 ≤ a}

theorem cornerBox_mono {s a a' : ℝ} (h : a ≤ a') (c : Fin 4) :
    cornerBox s a c ⊆ cornerBox s a' c := by
  intro p hp
  exact ⟨hp.1, le_trans hp.2.1 h, hp.2.2.1, le_trans hp.2.2.2 h⟩

theorem cframe_of_mem_container {s : ℝ} (c : Fin 4) {p : RP} (hp : p ∈ container s) :
    0 ≤ (cframe s c p).1 ∧ (cframe s c p).1 ≤ s ∧ 0 ≤ (cframe s c p).2 ∧ (cframe s c p).2 ≤ s := by
  simp only [container, mem_prod, mem_Icc] at hp
  simp only [cframe]
  split_ifs <;> refine ⟨?_, ?_, ?_, ?_⟩ <;> linarith [hp.1.1, hp.1.2, hp.2.1, hp.2.2]

theorem cornerBox_subset_container {s a : ℝ} (ha : a ≤ s) (c : Fin 4) :
    cornerBox s a c ⊆ container s := by
  intro p hp
  obtain ⟨h1, h2, h3, h4⟩ := hp
  simp only [container, mem_prod, mem_Icc]
  simp only [cframe] at h1 h2 h3 h4
  split_ifs at h1 h2 h3 h4 <;> refine ⟨⟨?_, ?_⟩, ?_, ?_⟩ <;> linarith

/-- The unit corner box is the slot box of the corner slot (`Selection.slotBox`,
`Skeleton.slotCentre` with cell `(0,0)`): the object `teleport_packing` / K0-FREE speak about. -/
theorem cornerBox_one_eq_slotBox (s : ℝ) (c : Fin 4) :
    cornerBox s 1 c = slotBox (slotCentre s ⟨c, 0, 0⟩) := by
  ext p
  simp only [cornerBox, cframe, slotBox, mem_setOf_eq, mem_prod, mem_Icc]
  fin_cases c <;> simp only [slotCentre, cornerR, cornerT, Nat.cast_zero, zero_add] <;>
    simp <;> constructor <;> intro h <;> simp only [and_assoc] at h ⊢ <;>
    obtain ⟨h1, h2, h3, h4⟩ := h <;>
    exact ⟨by linarith, by linarith, by linarith, by linarith⟩

/-! ## Squares: coordinate half-extent, compactness, diameter -/

/-- Every point of a parametrised square is within `wT/2` of the centre in each coordinate. -/
theorem coord_sub_centre_le {q : PSq} (ht : q.t ∈ Icc (0 : ℝ) 1) {p : RP} (hp : p ∈ q.set) :
    |p.1 - q.cx| ≤ wT q.t / 2 ∧ |p.2 - q.cy| ≤ wT q.t / 2 := by
  rw [mem_set_iff_uv] at hp
  obtain ⟨hu, hv⟩ := hp
  have hu' : |(p.1 - q.cx) * cosT q.t + (p.2 - q.cy) * sinT q.t| ≤ 1 / 2 := by
    simpa only [rdot, edir] using hu
  have hv' : |-(p.1 - q.cx) * sinT q.t + (p.2 - q.cy) * cosT q.t| ≤ 1 / 2 := by
    have e : rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q))
        = -(p.1 - q.cx) * sinT q.t + (p.2 - q.cy) * cosT q.t := by
      simp only [rdot, edir, perpV]; ring
    rwa [e] at hv
  have h := core_box ht.1 ht.2 hu' hv'
  simp only [wT]
  constructor <;> linarith [h.1, h.2]

/-- `wT t = cos θ + sin θ ≤ 1.4144 ≥ √2`: the rational pad constant of the emitted certificates. -/
theorem wT_le_bound {t : ℝ} (h0 : 0 ≤ t) (h1 : t ≤ 1) : wT t ≤ 2 * (7072 / 10000) := by
  have hc := cosT_nonneg h0 h1
  have hs := sinT_nonneg h0
  have hcs := cosT_sq_add_sinT_sq t
  have h2 : (cosT t + sinT t) ^ 2 ≤ (2 * (7072 / 10000 : ℝ)) ^ 2 := by
    nlinarith [sq_nonneg (cosT t - sinT t)]
  unfold wT
  exact (pow_le_pow_iff_left₀ (add_nonneg hc hs) (by norm_num) two_ne_zero).mp h2

theorem isCompact_psq_set (q : PSq) : IsCompact q.set := by
  rw [PSq.set, sqSet_eq_image]
  exact (isCompact_Icc.prod isCompact_Icc).image (by unfold aff; fun_prop)

theorem psq_set_nonempty (q : PSq) : q.set.Nonempty :=
  ⟨centre q, mem_set_of_sqdist_le q (by simp [sqdist, centre])⟩

/-- Two points of a unit square are at squared distance `≤ 2`. -/
theorem sqdist_le_two_of_mem (q : PSq) {p p' : RP} (hp : p ∈ q.set) (hp' : p' ∈ q.set) :
    sqdist p p' ≤ 2 := by
  rw [PSq.set] at hp hp'
  obtain ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩ := hp
  obtain ⟨a', b', ha0', ha1', hb0', hb1', rfl⟩ := hp'
  rw [aff_sqdist _ _ (rdot_edir q)]
  have h1 : (a - a') ^ 2 ≤ 1 := by nlinarith
  have h2 : (b - b') ^ 2 ≤ 1 := by nlinarith
  linarith

/-! ## `μ_c`: the corner value of a square, attained -/

/-- `max(p_x, p_y)` in the frame of corner `c`. -/
def gcf (s : ℝ) (c : Fin 4) (p : RP) : ℝ := max (cframe s c p).1 (cframe s c p).2

theorem continuous_gcf (s : ℝ) (c : Fin 4) : Continuous (gcf s c) := by
  unfold gcf cframe
  apply Continuous.max <;> split_ifs <;> fun_prop

/-- The minimum of `gcf` over a square is attained (the square is compact). -/
theorem exists_min_gcf (q : PSq) (s : ℝ) (c : Fin 4) :
    ∃ p ∈ q.set, ∀ p' ∈ q.set, gcf s c p ≤ gcf s c p' := by
  obtain ⟨p, hp, hmin⟩ := (isCompact_psq_set q).exists_isMinOn (psq_set_nonempty q)
    (continuous_gcf s c).continuousOn
  exact ⟨p, hp, fun p' hp' => isMinOn_iff.mp hmin p' hp'⟩

/-- **`μ_c(Q)`** (A90 §1, `k0_blocked_side.md` §1): `min_{p ∈ Q} max(p_x, p_y)` in the frame
of corner `c` — the value attained by the minimiser of `exists_min_gcf`. -/
def muC (s : ℝ) (c : Fin 4) (q : PSq) : ℝ := gcf s c (exists_min_gcf q s c).choose

theorem muC_spec (s : ℝ) (c : Fin 4) (q : PSq) :
    (∃ p ∈ q.set, gcf s c p = muC s c q) ∧ ∀ p ∈ q.set, muC s c q ≤ gcf s c p := by
  obtain ⟨hp, hmin⟩ := (exists_min_gcf q s c).choose_spec
  exact ⟨⟨_, hp, rfl⟩, hmin⟩

theorem mem_cornerBox_iff_gcf {s a : ℝ} {c : Fin 4} {p : RP} (hp : p ∈ container s) :
    p ∈ cornerBox s a c ↔ gcf s c p ≤ a := by
  obtain ⟨h1, -, h3, -⟩ := cframe_of_mem_container c hp
  simp only [cornerBox, mem_setOf_eq, gcf, max_le_iff]
  constructor
  · rintro ⟨-, h2, -, h4⟩; exact ⟨h2, h4⟩
  · rintro ⟨h2, h4⟩; exact ⟨h1, h2, h3, h4⟩

/-- **[T] `μ_c(Q) ≤ a ⟺ Q ∩ [0,a]² ≠ ∅`** (closed meeting; the depth-`δ` hypothesis
`d_c(Q) ≥ δ` IS "`Q` meets the closed box `[0, 1−δ]²`"). -/
theorem meets_cornerBox_iff_muC_le {s a : ℝ} {c : Fin 4} {q : PSq} (hq : q.set ⊆ container s) :
    (q.set ∩ cornerBox s a c).Nonempty ↔ muC s c q ≤ a := by
  obtain ⟨⟨p0, hp0, hp0v⟩, hmin⟩ := muC_spec s c q
  constructor
  · rintro ⟨p, hpq, hpb⟩
    rw [mem_cornerBox_iff_gcf (hq hpq)] at hpb
    exact le_trans (hmin p hpq) hpb
  · intro h
    exact ⟨p0, hp0, (mem_cornerBox_iff_gcf (hq hp0)).mpr (hp0v ▸ h)⟩

/-! ## The crowd hypothesis -/

/-- **The crowd hypothesis at box size `a`**: at every corner two DISTINCT squares of `z` meet
the closed box `[0, a]²`.  With `a = 1 − δ` this is "every corner's second intruder has depth
`≥ δ`" (`meets_cornerBox_iff_muC_le`), the hypothesis `min_c d₂(c) ≥ δ` of Theorem S(δ). -/
def CrowdBox (s a : ℝ) (z : Cfg) : Prop :=
  ∀ c : Fin 4, ∃ i j : Fin 11, i ≠ j ∧
    ((z i).set ∩ cornerBox s a c).Nonempty ∧ ((z j).set ∩ cornerBox s a c).Nonempty

theorem crowdBox_mono {s a a' : ℝ} (h : a ≤ a') {z : Cfg} (hz : CrowdBox s a z) :
    CrowdBox s a' z := by
  intro c
  obtain ⟨i, j, hij, hi, hj⟩ := hz c
  exact ⟨i, j, hij, hi.mono (inter_subset_inter_right _ (cornerBox_mono h c)),
    hj.mono (inter_subset_inter_right _ (cornerBox_mono h c))⟩

/-! ## Lemma B-YES: the crowd hypothesis transfers to the dilated family -/

/-- A point of the dilate, in the form `p + (λ − 1)·c_Q` (`Δ_λ Q = Q + (λ − 1)·c_Q`). -/
theorem mem_scaleC_set_iff (lam : ℝ) (q : PSq) (p : RP) :
    (p.1 + (lam - 1) * q.cx, p.2 + (lam - 1) * q.cy) ∈ (scaleC lam q).set ↔ p ∈ q.set := by
  rw [mem_set_iff_uv, mem_set_iff_uv]
  have e1 : p.1 + (lam - 1) * q.cx - (scaleC lam q).cx = p.1 - q.cx := by
    simp only [scaleC]; ring
  have e2 : p.2 + (lam - 1) * q.cy - (scaleC lam q).cy = p.2 - q.cy := by
    simp only [scaleC]; ring
  have e3 : edir (scaleC lam q) = edir q := rfl
  simp only [e1, e2, e3]

private theorem dil_coord {lam m a r x cx : ℝ} (hlam : 1 ≤ lam) (hw : |x - cx| ≤ r) (b : Bool)
    (hx0 : 0 ≤ (if b then m - x else x)) (hxa : (if b then m - x else x) ≤ a) :
    (if b then lam * m - (x + (lam - 1) * cx) else x + (lam - 1) * cx)
      ≤ lam * a + (lam - 1) * r := by
  rw [abs_le] at hw
  have hl0 : (0 : ℝ) ≤ lam - 1 := by linarith
  cases b <;> simp only [Bool.false_eq_true, ↓reduceIte] at hx0 hxa ⊢
  · nlinarith [mul_nonneg hl0 (by linarith [hw.1] : (0 : ℝ) ≤ x + r - cx),
      mul_nonneg (by linarith : (0 : ℝ) ≤ lam) (by linarith : (0 : ℝ) ≤ a - x)]
  · nlinarith [mul_nonneg hl0 (by linarith [hw.2] : (0 : ℝ) ≤ cx - x + r),
      mul_nonneg (by linarith : (0 : ℝ) ≤ lam) (by linarith : (0 : ℝ) ≤ a - (m - x))]

/-- **Lemma B-YES** (`k0_blocked_side.md` §2.3, one square).  If `Q ⊆ [0,m]²` meets the closed
box `[0,a]²` at corner `c`, then `Δ_λ Q` (`λ ≥ 1`) meets `[0, λa + (λ−1)·r]²` at the same corner
of `[0, λm]²`, for any `r ≥ wT(t_Q)/2` (`≥ √2/2` suffices). -/
theorem scaleC_meets_cornerBox {lam m a r : ℝ} (hlam : 1 ≤ lam)
    {q : PSq} (ht : q.t ∈ Icc (0 : ℝ) 1) (hq : q.set ⊆ container m) (hw : wT q.t ≤ 2 * r)
    (c : Fin 4) (h : (q.set ∩ cornerBox m a c).Nonempty) :
    ((scaleC lam q).set ∩ cornerBox (lam * m) (lam * a + (lam - 1) * r) c).Nonempty := by
  obtain ⟨p, hpq, hp⟩ := h
  have hp'q := (mem_scaleC_set_iff lam q p).mpr hpq
  refine ⟨_, hp'q, ?_⟩
  have hcont := scaleC_subset hlam ht.1 ht.2 hq hp'q
  obtain ⟨c1, -, c3, -⟩ := cframe_of_mem_container c hcont
  obtain ⟨hx, hy⟩ := coord_sub_centre_le ht hpq
  have hx' : |p.1 - q.cx| ≤ r := by linarith
  have hy' : |p.2 - q.cy| ≤ r := by linarith
  obtain ⟨b1, b2, b3, b4⟩ := hp
  refine ⟨c1, ?_, c3, ?_⟩
  · have := dil_coord (m := m) (a := a) hlam hx' (cornerR c) (by simpa [cframe] using b1)
      (by simpa [cframe] using b2)
    simpa [cframe] using this
  · have := dil_coord (m := m) (a := a) hlam hy' (cornerT c) (by simpa [cframe] using b3)
      (by simpa [cframe] using b4)
    simpa [cframe] using this

/-! ## Distinctness: a unit square meets at most one corner box -/

private theorem gap_contra {s a x x' d : ℝ} (hsep : 2 < (s - 2 * a) ^ 2) (hsa : 2 * a ≤ s)
    (h1 : s - x ≤ a) (h2 : x' ≤ a) (hd : (x - x') ^ 2 + d ≤ 2) (hd0 : 0 ≤ d) : False := by
  have hx : s - 2 * a ≤ x - x' := by linarith
  have hx2 : (s - 2 * a) ^ 2 ≤ (x - x') ^ 2 := pow_le_pow_left₀ (by linarith) hx 2
  linarith

private theorem bits_differ {c c' : Fin 4} (h : c ≠ c') :
    cornerR c ≠ cornerR c' ∨ cornerT c ≠ cornerT c' := by
  fin_cases c <;> fin_cases c' <;> first | exact absurd rfl h | decide

/-- Corner boxes of size `a` are `> √2` apart when `(s − 2a)² > 2`: a unit square meets at most
one of them (the "eight distinct crowd squares", CC-1(ii) with the widening). -/
theorem not_meets_two_corners {s a : ℝ} (hsep : 2 < (s - 2 * a) ^ 2) (hsa : 2 * a ≤ s)
    {q : PSq} {c c' : Fin 4} (hcc : c ≠ c')
    (h : (q.set ∩ cornerBox s a c).Nonempty) (h' : (q.set ∩ cornerBox s a c').Nonempty) :
    False := by
  obtain ⟨p, hpq, hp⟩ := h
  obtain ⟨p', hpq', hp'⟩ := h'
  have hd := sqdist_le_two_of_mem q hpq hpq'
  simp only [sqdist] at hd
  simp only [cornerBox, cframe, mem_setOf_eq] at hp hp'
  have hd' : (p'.1 - p.1) ^ 2 + (p'.2 - p.2) ^ 2 ≤ 2 := by nlinarith
  rcases bits_differ hcc with hb | hb
  · rcases Bool.eq_false_or_eq_true (cornerR c) with h1 | h1 <;>
      rcases Bool.eq_false_or_eq_true (cornerR c') with h2 | h2 <;>
      simp only [h1, h2, ↓reduceIte, Bool.false_eq_true, ne_eq, not_true_eq_false] at hb hp hp'
    · exact gap_contra hsep hsa hp.2.1 hp'.2.1 hd (sq_nonneg _)
    · exact gap_contra hsep hsa hp'.2.1 hp.2.1 hd' (sq_nonneg _)
  · rcases Bool.eq_false_or_eq_true (cornerT c) with h1 | h1 <;>
      rcases Bool.eq_false_or_eq_true (cornerT c') with h2 | h2 <;>
      simp only [h1, h2, ↓reduceIte, Bool.false_eq_true, ne_eq, not_true_eq_false] at hb hp hp'
    · exact gap_contra hsep hsa hp.2.2.2 hp'.2.2.2 (by linarith [hd]) (sq_nonneg (p.1 - p'.1))
    · exact gap_contra hsep hsa hp'.2.2.2 hp.2.2.2 (by linarith [hd']) (sq_nonneg (p'.1 - p.1))

/-! ## Lemma CW: the weight arithmetic of the two runs -/

/-- **Lemma CW** (`k0_blocked_side.md` §2.4).  Run A (`checkCaseI cA`, no cores, no NO-families,
`n ≤ 11 + 8e`) and run B (`checkCaseI cB`, no cores, NO-families avoided by every square that
meets a corner box `[0,a]²`), on ONE measure (`hsame`): no strict family of 11 closed unit
squares at the certified side has two distinct members meeting the corner box at every corner.
The eight crowd members carry mass `≥ (1+e)·wd_A` each, the other three `≥ wd_A`; the sum
`≥ (11 + 8e)·wd_A` exceeds the total `< n·wd_A`. -/
theorem crowd_sound {cA cB : CCertI} {e : ℝ} (he : 0 ≤ e)
    (hA : checkCaseI cA = true) (hAc : cA.cores = []) (hAf : cA.nofams = [])
    (hAn : (cA.n : ℝ) ≤ 11 + 8 * e)
    (hB : checkCaseI cB = true) (hBc : cB.cores = []) (hBs : caseSide cB = caseSide cA)
    (hsame : ∀ S : Set RP,
      massIn cB.atoms S * (cA.wd : ℝ) * (1 + e) = massIn cA.atoms S * (cB.wd : ℝ))
    {a : ℝ}
    (hE : ∀ q : PSq, q.t ∈ Icc (0 : ℝ) 1 → q.set ⊆ container (caseSide cA) →
      (∃ c : Fin 4, (q.set ∩ cornerBox (caseSide cA) a c).Nonempty) →
      ∀ f ∈ cB.nofams, ¬ InZone f q)
    (hsep : 2 < (caseSide cA - 2 * a) ^ 2) (hsa : 2 * a ≤ caseSide cA)
    {Q : Fin 11 → Set RP} (hQ : IsStrictFamily 11 (caseSide cA) Q)
    (hcrowd : ∀ c : Fin 4, ∃ i j : Fin 11, i ≠ j ∧
      (Q i ∩ cornerBox (caseSide cA) a c).Nonempty ∧ (Q j ∩ cornerBox (caseSide cA) a c).Nonempty) :
    False := by
  classical
  obtain ⟨-, hwdA, hatA, -, -, htotA, -⟩ := checkCaseI_facts hA
  obtain ⟨-, hwdB, -, -, -, -, -⟩ := checkCaseI_facts hB
  have hwdAR : (0 : ℝ) < cA.wd := by exact_mod_cast hwdA
  have hwdBR : (0 : ℝ) < cB.wd := by exact_mod_cast hwdB
  -- the crowd index set
  set G : Finset (Fin 11) :=
    Finset.univ.filter fun i => ∃ c : Fin 4, (Q i ∩ cornerBox (caseSide cA) a c).Nonempty with hG
  -- (P2) of run A: every member is priced `≥ wd_A`
  have hpriceA : ∀ i, (cA.wd : ℝ) ≤ massIn cA.atoms (Q i) := by
    intro i
    obtain ⟨q, hqt, hqs⟩ := isUnitSquare_exists_psq (hQ.unit i)
    rw [hqs]
    refine checkCaseI_price hA q hqt.1 hqt.2 (hqs ▸ hQ.contained i) ?_ ?_
    · intro K hK; rw [hAc] at hK; exact absurd hK List.not_mem_nil
    · intro f hf; rw [hAf] at hf; exact absurd hf List.not_mem_nil
  -- (P2) of run B on the crowd members: priced `≥ (1+e)·wd_A`
  have hpriceB : ∀ i ∈ G, (cA.wd : ℝ) * (1 + e) ≤ massIn cA.atoms (Q i) := by
    intro i hi
    rw [hG, Finset.mem_filter] at hi
    obtain ⟨-, hc⟩ := hi
    obtain ⟨q, hqt, hqs⟩ := isUnitSquare_exists_psq (hQ.unit i)
    have hsub : q.set ⊆ container (caseSide cA) := hqs ▸ hQ.contained i
    have hB' : (cB.wd : ℝ) ≤ massIn cB.atoms (Q i) := by
      rw [hqs]
      refine checkCaseI_price hB q hqt.1 hqt.2 (by rw [hBs]; exact hsub) ?_ ?_
      · intro K hK; rw [hBc] at hK; exact absurd hK List.not_mem_nil
      · intro f hf
        rw [hqs] at hc
        exact hE q hqt hsub hc f hf
    have h1 := hsame (Q i)
    have h2 := mul_le_mul_of_nonneg_right hB' (by positivity : (0 : ℝ) ≤ (cA.wd : ℝ) * (1 + e))
    have h3 : (cB.wd : ℝ) * ((cA.wd : ℝ) * (1 + e)) ≤ (cB.wd : ℝ) * massIn cA.atoms (Q i) := by
      nlinarith [h1, h2]
    exact le_of_mul_le_mul_left h3 hwdBR
  -- at least eight crowd members
  have hcard : 8 ≤ G.card := by
    choose ic jc hij hic hjc using hcrowd
    let f : Fin 4 × Fin 2 → Fin 11 := fun x => if x.2 = 0 then ic x.1 else jc x.1
    have hmeet : ∀ x : Fin 4 × Fin 2, (Q (f x) ∩ cornerBox (caseSide cA) a x.1).Nonempty := by
      intro x
      simp only [f]
      split_ifs
      · exact hic x.1
      · exact hjc x.1
    have hmaps : ∀ x : Fin 4 × Fin 2, f x ∈ G := by
      intro x
      rw [hG, Finset.mem_filter]
      exact ⟨Finset.mem_univ _, x.1, hmeet x⟩
    have hsq : ∀ i (c c' : Fin 4), c ≠ c' → (Q i ∩ cornerBox (caseSide cA) a c).Nonempty →
        (Q i ∩ cornerBox (caseSide cA) a c').Nonempty → False := by
      intro i c c' hcc h h'
      obtain ⟨q, -, hqs⟩ := isUnitSquare_exists_psq (hQ.unit i)
      rw [hqs] at h h'
      exact not_meets_two_corners hsep hsa hcc h h'
    have hinj : Set.InjOn f (↑(Finset.univ : Finset (Fin 4 × Fin 2))) := by
      intro x _ y _ hxy
      by_cases hc : x.1 = y.1
      · obtain ⟨cx, kx⟩ := x
        obtain ⟨cy, ky⟩ := y
        simp only at hc
        subst hc
        simp only [f] at hxy
        fin_cases kx <;> fin_cases ky <;> simp at hxy ⊢
        · exact hij _ hxy
        · exact hij _ hxy.symm
      · exfalso
        have h1 := hmeet x
        have h2 := hmeet y
        rw [← hxy] at h2
        exact hsq _ _ _ hc h1 h2
    have := Finset.card_le_card_of_injOn f (fun x _ => hmaps x) hinj
    simpa using this
  -- lower bound on the summed mass
  have hlow : ∑ i : Fin 11, ((cA.wd : ℝ) + if i ∈ G then e * (cA.wd : ℝ) else 0)
      ≤ ∑ i, massIn cA.atoms (Q i) := by
    refine Finset.sum_le_sum fun i _ => ?_
    by_cases hi : i ∈ G
    · rw [if_pos hi]; have := hpriceB i hi; linarith
    · rw [if_neg hi]; have := hpriceA i; linarith
  have hlow' : ∑ i : Fin 11, ((cA.wd : ℝ) + if i ∈ G then e * (cA.wd : ℝ) else 0)
      = 11 * (cA.wd : ℝ) + (G.card : ℝ) * (e * (cA.wd : ℝ)) := by
    rw [Finset.sum_add_distrib, Finset.sum_ite_mem, Finset.univ_inter, Finset.sum_const,
      Finset.sum_const, nsmul_eq_mul, nsmul_eq_mul]
    simp
  -- upper bound: disjointness
  have hup : ∑ i, massIn cA.atoms (Q i) ≤ (cA.atoms.map fun a => (a.w : ℝ)).sum := by
    rw [massIn_sum_comm]
    refine List.sum_le_sum fun a ha => ?_
    have hwa : (0 : ℝ) ≤ (a.w : ℝ) := by exact_mod_cast (hatA a ha).2
    exact indicator_sum_le hQ.disjoint hwa (atomPt a)
  have htot : (cA.atoms.map fun a => (a.w : ℝ)).sum < (cA.n : ℝ) * (cA.wd : ℝ) := by
    rw [foldl_add_eq cA.atoms 0, zero_add, hAc] at htotA
    simp only [List.length_nil, Nat.cast_zero, sub_zero] at htotA
    have h2 : (((cA.atoms.map fun a => a.w).sum : Int) : ℝ) < ((cA.n : Int) : ℝ) * (cA.wd : ℝ) := by
      exact_mod_cast htotA
    have h3 : (((cA.atoms.map fun a => a.w).sum : Int) : ℝ) = (cA.atoms.map fun a => ((a.w : ℝ))).sum := by
      push_cast
      rw [List.map_map]
      rfl
    rw [h3] at h2
    simpa using h2
  have hG8 : (8 : ℝ) ≤ G.card := by exact_mod_cast hcard
  nlinarith [hlow, hlow', hup, htot, hAn, hwdAR, he,
    mul_le_mul_of_nonneg_right hG8 (mul_nonneg he hwdAR.le),
    mul_le_mul_of_nonneg_right hAn hwdAR.le]

/-! ## Lemma CW-S: the incidence form (A94 `slot_crowds.md` §4.2, `1 + r_max` runs) -/

open Classical in
/-- **Lemma CW-S (incidence counting).**  One atom list, `1 + r_max` runs: run A with the pin
cores and budget `n ≤ 11 + 2·m_u·e`, and for each `ρ = 1..r_max` a run `B_ρ` with the same cores,
weights `w/(1 + ρe)` (`hsame`), whose NO-families avoid every admissible square meeting at least
`ρ` of the `m_u` slot families `Fam p` (`hE`).  If every square's incidence is `≤ r_max` (`hcap`)
and every slot family has two distinct NON-OWNER members (`hcrowd`), no strict family at the
certified side has its owners containing the cores.  Counting INCIDENCES: a non-owner meeting
`r` families is priced `≥ (1 + re)·wd_A` by run `B_r`, the others `≥ wd_A` by run A;
`Σ_i r_i = Σ_p #meeters(p) ≥ 2 m_u`; the total is `< (n − k)·wd_A ≤ (11 − k + 2 m_u e)·wd_A`
while at least `11 − k` non-owners exist.  The corner certificate (`crowd_sound`) is the case
`m_u = 4`, `r_max = 1`, no cores, `Fam p S = S meets the corner box p`. -/
theorem crowd_sound_incidence {cA : CCertI} {e : ℝ} (he : 0 ≤ e) {mU rmax : ℕ}
    (hA : checkCaseI cA = true) (hAf : cA.nofams = [])
    (hAn : (cA.n : ℝ) ≤ 11 + 2 * (mU : ℝ) * e)
    (cB : ℕ → CCertI)
    (hB : ∀ ρ, 1 ≤ ρ → ρ ≤ rmax →
      checkCaseI (cB ρ) = true ∧ (cB ρ).cores = cA.cores ∧ caseSide (cB ρ) = caseSide cA)
    (hsame : ∀ ρ, 1 ≤ ρ → ρ ≤ rmax → ∀ S : Set RP,
      massIn (cB ρ).atoms S * (cA.wd : ℝ) * (1 + (ρ : ℝ) * e) = massIn cA.atoms S * ((cB ρ).wd : ℝ))
    (Fam : Fin mU → Set RP → Prop)
    (hE : ∀ ρ, 1 ≤ ρ → ρ ≤ rmax → ∀ q : PSq, q.t ∈ Icc (0 : ℝ) 1 →
      q.set ⊆ container (caseSide cA) →
      ρ ≤ (Finset.univ.filter fun p => Fam p q.set).card → ∀ f ∈ (cB ρ).nofams, ¬ InZone f q)
    {Q : Fin 11 → Set RP} (hQ : IsStrictFamily 11 (caseSide cA) Q)
    (own : Fin cA.cores.length → Fin 11)
    (hown : ∀ j, coreSet (cA.cores.get j) ⊆ Q (own j))
    (hcap : ∀ i, (Finset.univ.filter fun p => Fam p (Q i)).card ≤ rmax)
    (hcrowd : ∀ p : Fin mU, ∃ i j : Fin 11, i ≠ j ∧ (∀ l, own l ≠ i) ∧ (∀ l, own l ≠ j) ∧
      Fam p (Q i) ∧ Fam p (Q j)) :
    False := by
  classical
  obtain ⟨-, hwdA, hatA, -, -, htotA, -⟩ := checkCaseI_facts hA
  have hwdAR : (0 : ℝ) < cA.wd := by exact_mod_cast hwdA
  -- the non-owners
  set O : Finset (Fin 11) := Finset.image own Finset.univ with hO
  set G : Finset (Fin 11) := Oᶜ with hG
  have hGmem : ∀ i : Fin 11, i ∈ G ↔ ∀ l, own l ≠ i := by
    intro i
    simp [hG, hO, eq_comm]
  -- incidence of a square
  set r : Fin 11 → ℕ := fun i => (Finset.univ.filter fun p => Fam p (Q i)).card with hr
  -- core-freeness of a non-owner
  have hfree : ∀ i ∈ G, ∀ K ∈ cA.cores, Disjoint (Q i) (coreSet K) := by
    intro i hi K hK
    obtain ⟨j, hj⟩ := List.mem_iff_get.mp hK
    have hnot := (hGmem i).mp hi j
    exact (hQ.disjoint i (own j) fun h => hnot h.symm).mono_right (hj ▸ hown j)
  -- pricing of a non-owner: `≥ (1 + r_i e)·wd_A`
  have hprice : ∀ i ∈ G, (cA.wd : ℝ) * (1 + (r i : ℝ) * e) ≤ massIn cA.atoms (Q i) := by
    intro i hi
    obtain ⟨q, hqt, hqs⟩ := isUnitSquare_exists_psq (hQ.unit i)
    have hsub : q.set ⊆ container (caseSide cA) := hqs ▸ hQ.contained i
    have hfree' : ∀ K ∈ cA.cores, Disjoint q.set (coreSet K) := fun K hK => hqs ▸ hfree i hi K hK
    rcases Nat.eq_zero_or_pos (r i) with h0 | hpos
    · -- run A
      rw [h0]
      simp only [Nat.cast_zero, zero_mul, add_zero, mul_one]
      rw [hqs]
      refine checkCaseI_price hA q hqt.1 hqt.2 hsub hfree' ?_
      intro f hf; rw [hAf] at hf; exact absurd hf List.not_mem_nil
    · -- run B_{r i}
      obtain ⟨hBρ, hBc, hBs⟩ := hB (r i) hpos (hcap i)
      obtain ⟨-, hwdB, -, -, -, -, -⟩ := checkCaseI_facts hBρ
      have hwdBR : (0 : ℝ) < (cB (r i)).wd := by exact_mod_cast hwdB
      have hB' : ((cB (r i)).wd : ℝ) ≤ massIn (cB (r i)).atoms (Q i) := by
        rw [hqs]
        refine checkCaseI_price hBρ q hqt.1 hqt.2 (by rw [hBs]; exact hsub) ?_ ?_
        · intro K hK; rw [hBc] at hK; exact hfree' K hK
        · intro f hf
          refine hE (r i) hpos (hcap i) q hqt hsub ?_ f hf
          rw [hr]; simp only [hqs]; exact le_rfl
      have h1 := hsame (r i) hpos (hcap i) (Q i)
      have h2 := mul_le_mul_of_nonneg_right hB'
        (by positivity : (0 : ℝ) ≤ (cA.wd : ℝ) * (1 + (r i : ℝ) * e))
      have h3 : ((cB (r i)).wd : ℝ) * ((cA.wd : ℝ) * (1 + (r i : ℝ) * e))
          ≤ ((cB (r i)).wd : ℝ) * massIn cA.atoms (Q i) := by
        nlinarith [h1, h2]
      exact le_of_mul_le_mul_left h3 hwdBR
  -- the double count: `Σ_{i ∈ G} r_i ≥ 2 m_u`
  have hcount : 2 * mU ≤ ∑ i ∈ G, r i := by
    have e1 : ∑ i ∈ G, r i = ∑ p : Fin mU, (G.filter fun i => Fam p (Q i)).card := by
      simp only [hr, Finset.card_filter]
      rw [Finset.sum_comm]
    rw [e1]
    have h2 : ∀ p : Fin mU, 2 ≤ (G.filter fun i => Fam p (Q i)).card := by
      intro p
      obtain ⟨i, j, hij, hi, hj, hFi, hFj⟩ := hcrowd p
      have hsub : ({i, j} : Finset (Fin 11)) ⊆ G.filter fun i => Fam p (Q i) := by
        intro x hx
        simp only [Finset.mem_insert, Finset.mem_singleton] at hx
        rw [Finset.mem_filter]
        rcases hx with rfl | rfl
        · exact ⟨(hGmem x).mpr hi, hFi⟩
        · exact ⟨(hGmem x).mpr hj, hFj⟩
      have := Finset.card_le_card hsub
      rwa [Finset.card_pair hij] at this
    calc 2 * mU = ∑ _p : Fin mU, 2 := by simp [mul_comm]
      _ ≤ ∑ p : Fin mU, (G.filter fun i => Fam p (Q i)).card := Finset.sum_le_sum fun p _ => h2 p
  -- lower bound on the summed mass of the non-owners
  have hlow : ∑ i ∈ G, (cA.wd : ℝ) * (1 + (r i : ℝ) * e) ≤ ∑ i ∈ G, massIn cA.atoms (Q i) :=
    Finset.sum_le_sum fun i hi => hprice i hi
  have hlow' : ∑ i ∈ G, (cA.wd : ℝ) * (1 + (r i : ℝ) * e)
      = (G.card : ℝ) * (cA.wd : ℝ) + (cA.wd : ℝ) * e * ((∑ i ∈ G, r i : ℕ) : ℝ) := by
    push_cast
    simp only [Finset.mul_sum, mul_add, mul_one, Finset.sum_add_distrib, Finset.sum_const,
      nsmul_eq_mul]
    congr 1
    refine Finset.sum_congr rfl fun i _ => ?_
    ring
  -- upper bound: disjointness of the non-owners
  have hup : ∑ i ∈ G, massIn cA.atoms (Q i) ≤ (cA.atoms.map fun a => (a.w : ℝ)).sum := by
    have hempty : massIn cA.atoms (∅ : Set RP) = 0 := by simp [massIn]
    have hpad : ∑ i ∈ G, massIn cA.atoms (Q i)
        = ∑ i : Fin 11, massIn cA.atoms (if i ∈ G then Q i else ∅) := by
      simp only [apply_ite (massIn cA.atoms), hempty, Finset.sum_ite_mem, Finset.univ_inter]
    have hdisf : ∀ i j : Fin 11, i ≠ j →
        Disjoint (if i ∈ G then Q i else (∅ : Set RP)) (if j ∈ G then Q j else ∅) := by
      intro i j hij
      by_cases hi : i ∈ G <;> by_cases hj : j ∈ G <;> simp [hi, hj, hQ.disjoint i j hij]
    rw [hpad, massIn_sum_comm]
    refine List.sum_le_sum fun a ha => ?_
    have hwa : (0 : ℝ) ≤ (a.w : ℝ) := by exact_mod_cast (hatA a ha).2
    exact indicator_sum_le hdisf hwa (atomPt a)
  have htot : (cA.atoms.map fun a => (a.w : ℝ)).sum
      < ((cA.n : ℝ) - (cA.cores.length : ℝ)) * (cA.wd : ℝ) := by
    rw [foldl_add_eq cA.atoms 0, zero_add] at htotA
    have h2 : (((cA.atoms.map fun a => a.w).sum : Int) : ℝ)
        < ((((cA.n : Int) - (cA.cores.length : Int)) * cA.wd : Int) : ℝ) := by exact_mod_cast htotA
    have h3 : (((cA.atoms.map fun a => a.w).sum : Int) : ℝ)
        = (cA.atoms.map fun a => ((a.w : ℝ))).sum := by
      push_cast
      rw [List.map_map]
      rfl
    rw [h3] at h2
    push_cast at h2
    exact h2
  -- at least `11 − k` non-owners
  have hOcard : O.card ≤ cA.cores.length := le_trans Finset.card_image_le (by simp)
  have hcards : O.card + G.card = 11 := by
    have h := Finset.card_add_card_compl O
    simp only [Fintype.card_fin] at h
    exact h
  have hGcard : (11 : ℝ) - (cA.cores.length : ℝ) ≤ (G.card : ℝ) := by
    have h1 : (O.card : ℝ) ≤ (cA.cores.length : ℝ) := by exact_mod_cast hOcard
    have h2 : (O.card : ℝ) + (G.card : ℝ) = 11 := by exact_mod_cast hcards
    linarith
  have hcountR : (2 : ℝ) * mU ≤ ((∑ i ∈ G, r i : ℕ) : ℝ) := by exact_mod_cast hcount
  nlinarith [hlow, hlow', hup, htot, hAn, hwdAR, he, hGcard, hcountR,
    mul_le_mul_of_nonneg_left hcountR (mul_nonneg hwdAR.le he),
    mul_le_mul_of_nonneg_right hGcard hwdAR.le,
    mul_le_mul_of_nonneg_right hAn hwdAR.le]

/-! ## Theorem S(δ) in window form -/

/-- **Theorem S(δ), window form** (`k0_blocked_side.md` §2.4–2.5): a two-run crowd certificate
at side `s0 = caseSide cA` with box size `a_w ≥ (s0/m_lo)·a + (s0/m_lo − 1)·r` kills, at every
side `m ∈ [m_lo, s0)`, every packing with two distinct squares meeting the closed box `[0,a]²`
at every corner (`a = 1 − δ`: every corner's second intruder at depth `≥ δ`).  Lemma B-YES per
crowd square, Lemma B (`dil_strict`) for the family, Lemma CW at `s0`. -/
theorem crowd_cert_kill {cA cB : CCertI} {e : ℝ} (he : 0 ≤ e)
    (hA : checkCaseI cA = true) (hAc : cA.cores = []) (hAf : cA.nofams = [])
    (hAn : (cA.n : ℝ) ≤ 11 + 8 * e)
    (hB : checkCaseI cB = true) (hBc : cB.cores = []) (hBs : caseSide cB = caseSide cA)
    (hsame : ∀ S : Set RP,
      massIn cB.atoms S * (cA.wd : ℝ) * (1 + e) = massIn cA.atoms S * (cB.wd : ℝ))
    {mlo r a aw : ℝ} (hmlo : 0 < mlo) (hr : 0 ≤ r)
    (hwr : ∀ t ∈ Icc (0 : ℝ) 1, wT t ≤ 2 * r) (ha : 0 ≤ a)
    (haw : caseSide cA / mlo * a + (caseSide cA / mlo - 1) * r ≤ aw)
    (hE : ∀ q : PSq, q.t ∈ Icc (0 : ℝ) 1 → q.set ⊆ container (caseSide cA) →
      (∃ c : Fin 4, (q.set ∩ cornerBox (caseSide cA) aw c).Nonempty) →
      ∀ f ∈ cB.nofams, ¬ InZone f q)
    (hsep : 2 < (caseSide cA - 2 * aw) ^ 2) (hsa : 2 * aw ≤ caseSide cA) :
    ∀ m, mlo ≤ m → m < caseSide cA → ∀ z : Cfg, CfgPacking m z → ¬ CrowdBox m a z := by
  intro m hlo hhi z hz hcr
  have hm0 : 0 < m := lt_of_lt_of_le hmlo hlo
  have hlam : 1 < caseSide cA / m := by rw [lt_div_iff₀ hm0]; linarith
  have hF := dil_strict hm0 hhi hz
  have hlamle : caseSide cA / m ≤ caseSide cA / mlo :=
    div_le_div_of_nonneg_left (by linarith) hmlo hlo
  have hs : caseSide cA / m * m = caseSide cA := by field_simp
  have hmono : caseSide cA / m * a + (caseSide cA / m - 1) * r ≤ aw := by
    nlinarith [mul_le_mul_of_nonneg_right hlamle ha, mul_le_mul_of_nonneg_right hlamle hr]
  refine crowd_sound he hA hAc hAf hAn hB hBc hBs hsame hE hsep hsa hF fun c => ?_
  obtain ⟨i, j, hij, hi, hj⟩ := hcr c
  refine ⟨i, j, hij, ?_, ?_⟩
  · have := scaleC_meets_cornerBox hlam.le (hz.1 i) (hz.2.contained i) (hwr _ (hz.1 i)) c hi
    rw [hs] at this
    exact this.mono (inter_subset_inter_right _ (cornerBox_mono hmono c))
  · have := scaleC_meets_cornerBox hlam.le (hz.1 j) (hz.2.contained j) (hwr _ (hz.1 j)) c hj
    rw [hs] at this
    exact this.mono (inter_subset_inter_right _ (cornerBox_mono hmono c))

/-! ## The decidable "one measure, two files" check -/

/-- Run B is run A with the weights divided by `1 + e`, `e = eNum/eDen`: same atom points in the
same order, `w_B · wd_A · (eDen + eNum) = w_A · wd_B · eDen` per atom (exact integers). -/
def sameMeasure (cA cB : CCertI) (eNum eDen : Nat) : Bool :=
  decide (cA.atoms.length = cB.atoms.length) &&
  (cA.atoms.zip cB.atoms).all fun ab =>
    decide (ab.1.px = ab.2.px) && decide (ab.1.py = ab.2.py) && decide (ab.1.pd = ab.2.pd) &&
    decide (ab.2.w * cA.wd * ((eDen : Int) + (eNum : Int)) = ab.1.w * cB.wd * (eDen : Int))

private theorem sameMeasure_key {wdA wdB : Int} {eNum eDen : ℕ} (hd : 0 < eDen) :
    ∀ (la lb : List IAtom), la.length = lb.length →
      (∀ ab ∈ la.zip lb, ab.1.px = ab.2.px ∧ ab.1.py = ab.2.py ∧ ab.1.pd = ab.2.pd ∧
        ab.2.w * wdA * ((eDen : Int) + (eNum : Int)) = ab.1.w * wdB * (eDen : Int)) →
      ∀ S : Set RP, massIn lb S * (wdA : ℝ) * (1 + (eNum : ℝ) / eDen) = massIn la S * (wdB : ℝ) := by
  intro la
  induction la with
  | nil =>
    intro lb hlen _ S
    cases lb with
    | nil => simp [massIn]
    | cons b lb => simp at hlen
  | cons a la ih =>
    intro lb hlen hz S
    cases lb with
    | nil => simp at hlen
    | cons b lb =>
      simp only [List.length_cons, Nat.add_right_cancel_iff] at hlen
      simp only [List.zip_cons_cons, List.mem_cons, forall_eq_or_imp] at hz
      obtain ⟨⟨hpx, hpy, hpd, hw⟩, hrest⟩ := hz
      have ih' := ih lb hlen hrest S
      rw [massIn_cons, massIn_cons]
      have hpt : atomPt b = atomPt a := by simp [atomPt, hpx, hpy, hpd]
      rw [hpt]
      have hdR : (0 : ℝ) < eDen := by exact_mod_cast hd
      have hwR : (b.w : ℝ) * (wdA : ℝ) * (1 + (eNum : ℝ) / eDen) = (a.w : ℝ) * (wdB : ℝ) := by
        have h1 : ((b.w * wdA * ((eDen : Int) + (eNum : Int)) : Int) : ℝ)
            = ((a.w * wdB * (eDen : Int) : Int) : ℝ) := by exact_mod_cast hw
        push_cast at h1
        have e : (1 + (eNum : ℝ) / eDen) = ((eDen : ℝ) + eNum) / eDen := by
          field_simp
        rw [e, mul_div_assoc', div_eq_iff hdR.ne']
        exact h1
      by_cases hmem : atomPt a ∈ S
      · simp only [Set.indicator_of_mem hmem]
        linear_combination hwR + ih'
      · simp only [Set.indicator_of_notMem hmem, zero_add]
        exact ih'

/-- `sameMeasure = true` gives the real-mass identity Lemma CW consumes. -/
theorem sameMeasure_sound {cA cB : CCertI} {eNum eDen : ℕ} (hd : 0 < eDen)
    (h : sameMeasure cA cB eNum eDen = true) :
    ∀ S : Set RP,
      massIn cB.atoms S * (cA.wd : ℝ) * (1 + (eNum : ℝ) / eDen) = massIn cA.atoms S * (cB.wd : ℝ) := by
  simp only [sameMeasure, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at h
  obtain ⟨hlen, hall⟩ := h
  refine sameMeasure_key hd cA.atoms cB.atoms hlen fun ab hab => ?_
  have := hall ab hab
  tauto

end

end S11
end PackingCert
