import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.MeasureBridge
import PackingCertMathlib.CaseChecker
import PackingCertMathlib.CaseSat

/-!
# Real semantics of case-LP hypotheses, and exemption-test soundness (A70, V.CASE)

The certificate's hypotheses (`docs/specs/case_lp_certificate_v1.md` §2) as real
objects — `coreSet` (the closed core square, in `u/v` form) and `InZone` (a
parametrised square's `(centre, t)` lying in a NO-family zone) — and the soundness of
the two exemption discharge rules of `verify_case.py` (§3 rules 2 and 3):

* `coreExempt_sound` — a `core_exempt_frac` PASS on a box proves that EVERY placement
  of the box meets the core: the rational interval bounds enclose the real projection
  offsets, and `sat_squares` (`CaseSat.lean`) turns four-axis non-separation into an
  intersection point;
* `nofamExempt_sound` — a `nofam_exempt` PASS proves every placement of the box has
  its `(centre, t)` in the zone (closed comparisons, pointwise);
* `exemptB_sound` — the disjunction, at the integer-box level of the search.

Cast plumbing: the checker computes with core-Lean `Rat`; every checker value is
related to its real meaning through `Rat.cast` lemmas about the checker's own
`ratCosSin` / `rabs` / `rmin` / `rmax` / `rmul4` / `gInf`.
-/

namespace PackingCert
namespace S11

open Set MeasureI CaseI

noncomputable section

/-! ## Real semantics of the hypotheses -/

/-- The closed core square of a `cores` entry: centre `(kx, ky)`, half-side `a`,
edge direction `(cos θ_m, sin θ_m)` with `tan(θ_m/2) = tm` — in the `u/v`
(edge-coordinate) form of `mem_set_iff_uv`. -/
def coreSet (K : CCore) : Set RP :=
  {p : RP |
    |(p.1 - (K.kx : ℝ)) * cosT (K.tm : ℝ) + (p.2 - (K.ky : ℝ)) * sinT (K.tm : ℝ)|
        ≤ (K.a : ℝ) ∧
    |(-(p.1 - (K.kx : ℝ))) * sinT (K.tm : ℝ) + (p.2 - (K.ky : ℝ)) * cosT (K.tm : ℝ)|
        ≤ (K.a : ℝ)}

/-- A parametrised square's `(centre, t)` lies in a NO-family zone (all closed). -/
def InZone (f : CNoFam) (q : PSq) : Prop :=
  (f.x0 : ℝ) ≤ q.cx ∧ q.cx ≤ (f.x1 : ℝ) ∧ (f.y0 : ℝ) ≤ q.cy ∧ q.cy ≤ (f.y1 : ℝ) ∧
  ∃ iv ∈ f.tivs, (iv.1 : ℝ) ≤ q.t ∧ q.t ≤ (iv.2 : ℝ)

/-- NO-exemption of a SET: some parametrisation with `t ∈ [0,1]` lies in some zone of
the certificate. -/
def CaseExempt (c : CCertI) (S : Set RP) : Prop :=
  ∃ q : PSq, q.t ∈ Icc (0 : ℝ) 1 ∧ S = q.set ∧ ∃ f ∈ c.nofams, InZone f q

theorem caseExempt_of_nil {c : CCertI} (h : c.nofams = []) (S : Set RP) :
    ¬ CaseExempt c S := by
  rintro ⟨q, -, -, f, hf, -⟩
  rw [h] at hf
  exact absurd hf List.not_mem_nil

/-! ## Cast lemmas for the checker's rational helpers -/

theorem rabs_cast (x : ℚ) : ((rabs x : ℚ) : ℝ) = |(x : ℝ)| := by
  simp only [rabs]
  split
  · next h =>
    rw [abs_of_neg (by exact_mod_cast h)]
    push_cast
    ring
  · next h =>
    rw [abs_of_nonneg (by exact_mod_cast not_lt.mp h)]

theorem rmin_cast (x y : ℚ) : ((rmin x y : ℚ) : ℝ) = min (x : ℝ) (y : ℝ) := by
  simp only [rmin]
  split
  · next h => rw [min_eq_left (by exact_mod_cast h)]
  · next h => rw [min_eq_right (by exact_mod_cast (le_of_lt (not_le.mp h)))]

theorem rmax_cast (x y : ℚ) : ((rmax x y : ℚ) : ℝ) = max (x : ℝ) (y : ℝ) := by
  simp only [rmax]
  split
  · next h => rw [max_eq_right (by exact_mod_cast h)]
  · next h => rw [max_eq_left (by exact_mod_cast (le_of_lt (not_le.mp h)))]

theorem ratCosSin_fst (t : ℚ) : (((ratCosSin t).1 : ℚ) : ℝ) = cosT (t : ℝ) := by
  have h : (ratCosSin t).1 = (1 - t * t) / (1 + t * t) := rfl
  rw [h, cosT]
  push_cast
  ring_nf

theorem ratCosSin_snd (t : ℚ) : (((ratCosSin t).2 : ℚ) : ℝ) = sinT (t : ℝ) := by
  have h : (ratCosSin t).2 = 2 * t / (1 + t * t) := rfl
  rw [h, sinT]
  push_cast
  ring_nf

/-- `rmul4` really encloses a real product of enclosed factors. -/
theorem rmul4_bounds {a0 a1 b0 b1 : ℚ} {x y : ℝ}
    (hx0 : (a0 : ℝ) ≤ x) (hx1 : x ≤ (a1 : ℝ)) (hy0 : (b0 : ℝ) ≤ y) (hy1 : y ≤ (b1 : ℝ)) :
    (((rmul4 a0 a1 b0 b1).1 : ℚ) : ℝ) ≤ x * y ∧
      x * y ≤ (((rmul4 a0 a1 b0 b1).2 : ℚ) : ℝ) := by
  have h := mul_bounds hx0 hx1 hy0 hy1
  have h1 : (rmul4 a0 a1 b0 b1).1
      = rmin (rmin (a0 * b0) (a0 * b1)) (rmin (a1 * b0) (a1 * b1)) := rfl
  have h2 : (rmul4 a0 a1 b0 b1).2
      = rmax (rmax (a0 * b0) (a0 * b1)) (rmax (a1 * b0) (a1 * b1)) := rfl
  rw [h1, h2, rmin_cast, rmin_cast, rmin_cast, rmax_cast, rmax_cast, rmax_cast]
  push_cast
  exact h

/-- Sound abs bound from a checker `rmax (rabs u) (rabs v) ≤ l` test, for any real
value between the casts of `u` and `v`. -/
theorem abs_le_of_between {u v l : ℚ} {X : ℝ}
    (hle : rmax (rabs u) (rabs v) ≤ l) (h0 : (u : ℝ) ≤ X) (h1 : X ≤ (v : ℝ)) :
    |X| ≤ (l : ℝ) := by
  have hcast : max |(u : ℝ)| |(v : ℝ)| ≤ (l : ℝ) := by
    rw [← rabs_cast, ← rabs_cast, ← rmax_cast]
    exact_mod_cast hle
  rw [max_le_iff] at hcast
  rw [abs_le]
  constructor
  · calc -(l : ℝ) ≤ -|(u : ℝ)| := by linarith [hcast.1]
      _ ≤ (u : ℝ) := neg_abs_le _
      _ ≤ X := h0
  · calc X ≤ (v : ℝ) := h1
      _ ≤ |(v : ℝ)| := le_abs_self _
      _ ≤ (l : ℝ) := hcast.2

/-! ## Soundness of `gInf`: a certified lower bound of `g = cos φ + |sin φ|` -/

/-- `rclamp0` is a nonnegative lower bound of any nonnegative real value that
dominates the cast. -/
theorem rclamp0_bound {x : ℚ} {A : ℝ} (hA : (x : ℝ) ≤ A) (hA0 : 0 ≤ A) :
    0 ≤ ((rclamp0 x : ℚ) : ℝ) ∧ ((rclamp0 x : ℚ) : ℝ) ≤ A := by
  simp only [rclamp0]
  split
  · next h =>
    refine ⟨by norm_num, ?_⟩
    simpa using hA0
  · next h =>
    refine ⟨?_, hA⟩
    have h0 : (0 : ℚ) ≤ x := not_lt.mp h
    exact_mod_cast h0

/-- `rbabs` is a nonnegative lower bound of `|B|` for any real `B` enclosed by the
casts of `blo ≤ bhi`. -/
theorem rbabs_bound {blo bhi : ℚ} {B : ℝ} (h0 : (blo : ℝ) ≤ B) (h1 : B ≤ (bhi : ℝ)) :
    0 ≤ ((rbabs blo bhi : ℚ) : ℝ) ∧ ((rbabs blo bhi : ℚ) : ℝ) ≤ |B| := by
  simp only [rbabs]
  split
  · next h =>
    refine ⟨by norm_num, ?_⟩
    have := abs_nonneg B
    push_cast
    linarith
  · next h =>
    rw [Bool.and_eq_true, decide_eq_true_eq, decide_eq_true_eq] at h
    rw [rmin_cast, rabs_cast, rabs_cast]
    rcases not_and_or.mp h with hb | hb
    · -- blo > 0: B > 0, |B| = B ≥ blo = |blo|
      have hblo : (0 : ℚ) < blo := not_le.mp hb
      have hbloR : (0 : ℝ) < (blo : ℝ) := by exact_mod_cast hblo
      have hBpos : 0 < B := lt_of_lt_of_le hbloR h0
      constructor
      · positivity
      · rw [abs_of_pos hBpos]
        calc min |(blo : ℝ)| |(bhi : ℝ)| ≤ |(blo : ℝ)| := min_le_left _ _
          _ = (blo : ℝ) := abs_of_pos hbloR
          _ ≤ B := h0
    · -- bhi < 0: B < 0, |B| = -B ≥ -bhi = |bhi|
      have hbhi : bhi < 0 := not_le.mp hb
      have hbhiR : (bhi : ℝ) < 0 := by exact_mod_cast hbhi
      have hBneg : B < 0 := lt_of_le_of_lt h1 hbhiR
      constructor
      · positivity
      · rw [abs_of_neg hBneg]
        calc min |(blo : ℝ)| |(bhi : ℝ)| ≤ |(bhi : ℝ)| := min_le_right _ _
          _ = -(bhi : ℝ) := abs_of_neg hbhiR
          _ ≤ -B := by linarith

/-- `gInf` is nonnegative and bounded by `g(t) = cos(θ−θ_m) + |sin(θ−θ_m)|` at every
`t` of the box (via `cos φ = C·cm + S·sm`, `sin(θ_m−θ) = C·sm − S·cm`). -/
theorem gInf_bound {K : CCore} {t0 t1 : ℚ} {q : PSq}
    (htm0 : (0 : ℚ) ≤ K.tm) (htm1 : K.tm ≤ 1)
    (ht00 : (0 : ℝ) ≤ (t0 : ℝ)) (ht11 : (t1 : ℝ) ≤ 1)
    (hqt0 : (t0 : ℝ) ≤ q.t) (hqt1 : q.t ≤ (t1 : ℝ)) :
    0 ≤ ((gInf K t0 t1 : ℚ) : ℝ) ∧
      ((gInf K t0 t1 : ℚ) : ℝ)
        ≤ (cosT q.t * cosT (K.tm : ℝ) + sinT q.t * sinT (K.tm : ℝ))
          + |cosT q.t * sinT (K.tm : ℝ) - sinT q.t * cosT (K.tm : ℝ)| := by
  have htm0R : (0 : ℝ) ≤ (K.tm : ℝ) := by exact_mod_cast htm0
  have htm1R : (K.tm : ℝ) ≤ 1 := by exact_mod_cast htm1
  have hqt00 : 0 ≤ q.t := le_trans ht00 hqt0
  have hqt11 : q.t ≤ 1 := le_trans hqt1 ht11
  have hcm0 : 0 ≤ cosT (K.tm : ℝ) := cosT_nonneg htm0R htm1R
  have hsm0 : 0 ≤ sinT (K.tm : ℝ) := sinT_nonneg htm0R
  have hC0 : 0 ≤ cosT q.t := cosT_nonneg hqt00 hqt11
  have hS0 : 0 ≤ sinT q.t := sinT_nonneg hqt00
  have hCu : cosT q.t ≤ (((ratCosSin t0).1 : ℚ) : ℝ) := by
    rw [ratCosSin_fst]; exact cosT_anti ht00 hqt0
  have hCl : (((ratCosSin t1).1 : ℚ) : ℝ) ≤ cosT q.t := by
    rw [ratCosSin_fst]; exact cosT_anti hqt00 hqt1
  have hSl : (((ratCosSin t0).2 : ℚ) : ℝ) ≤ sinT q.t := by
    rw [ratCosSin_snd]; exact sinT_mono ht00 hqt0 hqt11
  have hSu : sinT q.t ≤ (((ratCosSin t1).2 : ℚ) : ℝ) := by
    rw [ratCosSin_snd]; exact sinT_mono hqt00 hqt1 ht11
  have hcmv := ratCosSin_fst K.tm
  have hsmv := ratCosSin_snd K.tm
  -- lower corner of A = cos φ  (Alo0 = C0·cm + S0·sm; C0 = cos at t1, S0 = sin at t0)
  have hAv : (((ratCosSin t1).1 * (ratCosSin K.tm).1
      + (ratCosSin t0).2 * (ratCosSin K.tm).2 : ℚ) : ℝ)
      ≤ cosT q.t * cosT (K.tm : ℝ) + sinT q.t * sinT (K.tm : ℝ) := by
    push_cast
    rw [hcmv, hsmv]
    have m1 := mul_le_mul_of_nonneg_right hCl hcm0
    have m2 := mul_le_mul_of_nonneg_right hSl hsm0
    linarith
  have hA0 : 0 ≤ cosT q.t * cosT (K.tm : ℝ) + sinT q.t * sinT (K.tm : ℝ) :=
    add_nonneg (mul_nonneg hC0 hcm0) (mul_nonneg hS0 hsm0)
  -- enclosure of B = sin(θ_m − θ) = C·sm − S·cm  (Blo = −S1·cm + C0·sm, both at t1;
  -- Bhi = −S0·cm + C1·sm, both at t0)
  have hBl : ((-(ratCosSin t1).2 * (ratCosSin K.tm).1
      + (ratCosSin t1).1 * (ratCosSin K.tm).2 : ℚ) : ℝ)
      ≤ cosT q.t * sinT (K.tm : ℝ) - sinT q.t * cosT (K.tm : ℝ) := by
    push_cast
    rw [hcmv, hsmv]
    have m1 := mul_le_mul_of_nonneg_right hSu hcm0
    have m2 := mul_le_mul_of_nonneg_right hCl hsm0
    linarith
  have hBu : cosT q.t * sinT (K.tm : ℝ) - sinT q.t * cosT (K.tm : ℝ)
      ≤ ((-(ratCosSin t0).2 * (ratCosSin K.tm).1
      + (ratCosSin t0).1 * (ratCosSin K.tm).2 : ℚ) : ℝ) := by
    push_cast
    rw [hcmv, hsmv]
    have m1 := mul_le_mul_of_nonneg_right hSl hcm0
    have m2 := mul_le_mul_of_nonneg_right hCu hsm0
    linarith
  have hg : gInf K t0 t1
      = rclamp0 ((ratCosSin t1).1 * (ratCosSin K.tm).1
          + (ratCosSin t0).2 * (ratCosSin K.tm).2)
        + rbabs (-(ratCosSin t1).2 * (ratCosSin K.tm).1
            + (ratCosSin t1).1 * (ratCosSin K.tm).2)
          (-(ratCosSin t0).2 * (ratCosSin K.tm).1
            + (ratCosSin t0).1 * (ratCosSin K.tm).2) := rfl
  obtain ⟨ha0, ha1⟩ := rclamp0_bound hAv hA0
  obtain ⟨hb0, hb1⟩ := rbabs_bound hBl hBu
  rw [hg]
  push_cast
  constructor
  · linarith
  · linarith


/-! ## The geometric step: four-axis tests at a placement ⟹ the squares meet -/

/-- From the four point-level projection inequalities (at any certified lower bound
`gR ≤ g = cos φ + |sin φ|`) to an intersection point, via `sat_squares`.
`(dx, dy) = q.centre − k` in world frame; `(C, S)` and `(cm, sm)` the two edge
directions; the returned `(px, py)` is the common point relative to `k`. -/
theorem core_meet {C S cm sm aK gR dx dy : ℝ}
    (hCS : C ^ 2 + S ^ 2 = 1) (hmm : cm ^ 2 + sm ^ 2 = 1) (haK : 0 ≤ aK)
    (hA0 : 0 ≤ C * cm + S * sm)
    (hgle : gR ≤ (C * cm + S * sm) + |C * sm - S * cm|)
    (P1 : |dx * cm + dy * sm| ≤ aK + gR / 2)
    (P2 : |(-dx) * sm + dy * cm| ≤ aK + gR / 2)
    (P3 : |C * dx + S * dy| ≤ 1 / 2 + aK * gR)
    (P4 : |(-S) * dx + C * dy| ≤ 1 / 2 + aK * gR) :
    ∃ px py : ℝ,
      (|px * cm + py * sm| ≤ aK ∧ |(-px) * sm + py * cm| ≤ aK) ∧
      |C * (px - dx) + S * (py - dy)| ≤ 1 / 2 ∧
      |(-S) * (px - dx) + C * (py - dy)| ≤ 1 / 2 := by
  -- the between-frames angle: cos φ = C·cm + S·sm, sin(θ_m − θ) = C·sm − S·cm
  have hcs2 : (C * cm + S * sm) ^ 2 + (S * cm - C * sm) ^ 2 = 1 := by
    linear_combination (cm ^ 2 + sm ^ 2) * hCS + hmm
  have habs : |S * cm - C * sm| = |C * sm - S * cm| := abs_sub_comm _ _
  have hgle' : gR ≤ (C * cm + S * sm) + |S * cm - C * sm| := by rwa [habs]
  have hgmono : aK + gR / 2 ≤ aK + ((C * cm + S * sm) + |S * cm - C * sm|) / 2 := by
    linarith
  have hgmono' : 1 / 2 + aK * gR
      ≤ 1 / 2 + aK * ((C * cm + S * sm) + |S * cm - C * sm|) := by
    nlinarith [hgle', haK]
  -- the K-frame coordinates of the centre offset
  have identC : (C * cm + S * sm) * (dx * cm + dy * sm)
      + (S * cm - C * sm) * ((-dx) * sm + dy * cm) = C * dx + S * dy := by
    linear_combination (C * dx + S * dy) * hmm
  have identD : (-(S * cm - C * sm)) * (dx * cm + dy * sm)
      + (C * cm + S * sm) * ((-dx) * sm + dy * cm) = (-S) * dx + C * dy := by
    linear_combination (C * dy - S * dx) * hmm
  obtain ⟨m1, m2, b1, b2, hm1, hm2, hb1, hb2, he1, he2⟩ :=
    sat_squares (c := C * cm + S * sm) (s := S * cm - C * sm) (a := aK)
      (d1 := dx * cm + dy * sm) (d2 := (-dx) * sm + dy * cm)
      hA0 hcs2 haK
      (le_trans P1 hgmono) (le_trans P2 hgmono)
      (by rw [identC]; exact le_trans P3 hgmono')
      (by rw [identD]; exact le_trans P4 hgmono')
  refine ⟨m1 * cm - m2 * sm, m1 * sm + m2 * cm, ⟨?_, ?_⟩, ?_, ?_⟩
  · have e : (m1 * cm - m2 * sm) * cm + (m1 * sm + m2 * cm) * sm = m1 := by
      linear_combination m1 * hmm
    rwa [e]
  · have e : (-(m1 * cm - m2 * sm)) * sm + (m1 * sm + m2 * cm) * cm = m2 := by
      linear_combination m2 * hmm
    rwa [e]
  · have e : C * ((m1 * cm - m2 * sm) - dx) + S * ((m1 * sm + m2 * cm) - dy)
        = -b1 := by
      linear_combination (-(C * cm) - S * sm) * he1 + (C * sm - S * cm) * he2
        + (C * dx + S * dy - C ^ 2 * b1 - S ^ 2 * b1) * hmm + (-b1) * hCS
    rw [e, abs_neg]
    exact hb1
  · have e : (-S) * ((m1 * cm - m2 * sm) - dx) + C * ((m1 * sm + m2 * cm) - dy)
        = -b2 := by
      linear_combination (-(C * sm) + S * cm) * he1 + (-(C * cm) - S * sm) * he2
        + (C * dy - S * dx - C ^ 2 * b2 - S ^ 2 * b2) * hmm + (-b2) * hCS
    rw [e, abs_neg]
    exact hb2

/-! ## Soundness of the exemption tests -/

/-- **`core_exempt_frac` is sound**: a passing test proves that the placement `q`
(with parameters anywhere in the tested rational box) meets the core square. -/
theorem coreExempt_sound {K : CCore} {t0 t1 x0 x1 y0 y1 : ℚ} {q : PSq}
    (htm0 : (0 : ℚ) ≤ K.tm) (htm1 : K.tm ≤ 1) (haK : (0 : ℚ) ≤ K.a)
    (ht00 : (0 : ℝ) ≤ (t0 : ℝ)) (ht11 : (t1 : ℝ) ≤ 1)
    (hqt0 : (t0 : ℝ) ≤ q.t) (hqt1 : q.t ≤ (t1 : ℝ))
    (hx0 : (x0 : ℝ) ≤ q.cx) (hx1 : q.cx ≤ (x1 : ℝ))
    (hy0 : (y0 : ℝ) ≤ q.cy) (hy1 : q.cy ≤ (y1 : ℝ))
    (h : coreExempt K t0 t1 x0 x1 y0 y1 = true) :
    (q.set ∩ coreSet K).Nonempty := by
  simp only [coreExempt, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨hT1, hT2, hT3, hT4⟩ := h
  have htm0R : (0 : ℝ) ≤ (K.tm : ℝ) := by exact_mod_cast htm0
  have htm1R : (K.tm : ℝ) ≤ 1 := by exact_mod_cast htm1
  have haKR : (0 : ℝ) ≤ (K.a : ℝ) := by exact_mod_cast haK
  have hqt00 : 0 ≤ q.t := le_trans ht00 hqt0
  have hqt11 : q.t ≤ 1 := le_trans hqt1 ht11
  have hcm0 : 0 ≤ cosT (K.tm : ℝ) := cosT_nonneg htm0R htm1R
  have hsm0 : 0 ≤ sinT (K.tm : ℝ) := sinT_nonneg htm0R
  have hCu : cosT q.t ≤ (((ratCosSin t0).1 : ℚ) : ℝ) := by
    rw [ratCosSin_fst]; exact cosT_anti ht00 hqt0
  have hCl : (((ratCosSin t1).1 : ℚ) : ℝ) ≤ cosT q.t := by
    rw [ratCosSin_fst]; exact cosT_anti hqt00 hqt1
  have hSl : (((ratCosSin t0).2 : ℚ) : ℝ) ≤ sinT q.t := by
    rw [ratCosSin_snd]; exact sinT_mono ht00 hqt0 hqt11
  have hSu : sinT q.t ≤ (((ratCosSin t1).2 : ℚ) : ℝ) := by
    rw [ratCosSin_snd]; exact sinT_mono hqt00 hqt1 ht11
  have hcmv := ratCosSin_fst K.tm
  have hsmv := ratCosSin_snd K.tm
  -- centre offset enclosure
  have hdx0 : ((x0 - K.kx : ℚ) : ℝ) ≤ q.cx - (K.kx : ℝ) := by push_cast; linarith
  have hdx1 : q.cx - (K.kx : ℝ) ≤ ((x1 - K.kx : ℚ) : ℝ) := by push_cast; linarith
  have hdy0 : ((y0 - K.ky : ℚ) : ℝ) ≤ q.cy - (K.ky : ℝ) := by push_cast; linarith
  have hdy1 : q.cy - (K.ky : ℝ) ≤ ((y1 - K.ky : ℚ) : ℝ) := by push_cast; linarith
  -- the four point-level projection bounds
  obtain ⟨hg0, hgle⟩ := gInf_bound htm0 htm1 ht00 ht11 hqt0 hqt1 (K := K)
  have P1 : |(q.cx - (K.kx : ℝ)) * cosT (K.tm : ℝ)
      + (q.cy - (K.ky : ℝ)) * sinT (K.tm : ℝ)|
      ≤ (K.a : ℝ) + ((gInf K t0 t1 : ℚ) : ℝ) / 2 := by
    have hu : (((x0 - K.kx) * (ratCosSin K.tm).1 + (y0 - K.ky) * (ratCosSin K.tm).2
        : ℚ) : ℝ) ≤ (q.cx - (K.kx : ℝ)) * cosT (K.tm : ℝ)
        + (q.cy - (K.ky : ℝ)) * sinT (K.tm : ℝ) := by
      push_cast
      rw [hcmv, hsmv]
      have m1 := mul_le_mul_of_nonneg_right hdx0 hcm0
      have m2 := mul_le_mul_of_nonneg_right hdy0 hsm0
      push_cast at m1 m2
      linarith
    have hv : (q.cx - (K.kx : ℝ)) * cosT (K.tm : ℝ)
        + (q.cy - (K.ky : ℝ)) * sinT (K.tm : ℝ)
        ≤ (((x1 - K.kx) * (ratCosSin K.tm).1 + (y1 - K.ky) * (ratCosSin K.tm).2
        : ℚ) : ℝ) := by
      push_cast
      rw [hcmv, hsmv]
      have m1 := mul_le_mul_of_nonneg_right hdx1 hcm0
      have m2 := mul_le_mul_of_nonneg_right hdy1 hsm0
      push_cast at m1 m2
      linarith
    have := abs_le_of_between hT1 hu hv
    calc |(q.cx - (K.kx : ℝ)) * cosT (K.tm : ℝ)
        + (q.cy - (K.ky : ℝ)) * sinT (K.tm : ℝ)|
        ≤ ((K.a + gInf K t0 t1 / 2 : ℚ) : ℝ) := this
      _ = (K.a : ℝ) + ((gInf K t0 t1 : ℚ) : ℝ) / 2 := by push_cast; ring
  have P2 : |(-(q.cx - (K.kx : ℝ))) * sinT (K.tm : ℝ)
      + (q.cy - (K.ky : ℝ)) * cosT (K.tm : ℝ)|
      ≤ (K.a : ℝ) + ((gInf K t0 t1 : ℚ) : ℝ) / 2 := by
    have hu : ((-(x1 - K.kx) * (ratCosSin K.tm).2 + (y0 - K.ky) * (ratCosSin K.tm).1
        : ℚ) : ℝ) ≤ (-(q.cx - (K.kx : ℝ))) * sinT (K.tm : ℝ)
        + (q.cy - (K.ky : ℝ)) * cosT (K.tm : ℝ) := by
      push_cast
      rw [hcmv, hsmv]
      have m1 := mul_le_mul_of_nonneg_right (neg_le_neg hdx1) hsm0
      have m2 := mul_le_mul_of_nonneg_right hdy0 hcm0
      push_cast at m1 m2
      linarith
    have hv : (-(q.cx - (K.kx : ℝ))) * sinT (K.tm : ℝ)
        + (q.cy - (K.ky : ℝ)) * cosT (K.tm : ℝ)
        ≤ ((-(x0 - K.kx) * (ratCosSin K.tm).2 + (y1 - K.ky) * (ratCosSin K.tm).1
        : ℚ) : ℝ) := by
      push_cast
      rw [hcmv, hsmv]
      have m1 := mul_le_mul_of_nonneg_right (neg_le_neg hdx0) hsm0
      have m2 := mul_le_mul_of_nonneg_right hdy1 hcm0
      push_cast at m1 m2
      linarith
    have := abs_le_of_between hT2 hu hv
    calc |(-(q.cx - (K.kx : ℝ))) * sinT (K.tm : ℝ)
        + (q.cy - (K.ky : ℝ)) * cosT (K.tm : ℝ)|
        ≤ ((K.a + gInf K t0 t1 / 2 : ℚ) : ℝ) := this
      _ = (K.a : ℝ) + ((gInf K t0 t1 : ℚ) : ℝ) / 2 := by push_cast; ring
  have P3 : |cosT q.t * (q.cx - (K.kx : ℝ)) + sinT q.t * (q.cy - (K.ky : ℝ))|
      ≤ 1 / 2 + (K.a : ℝ) * ((gInf K t0 t1 : ℚ) : ℝ) := by
    obtain ⟨ha0, ha1⟩ := rmul4_bounds hCl hCu hdx0 hdx1
    obtain ⟨hb0, hb1⟩ := rmul4_bounds hSl hSu hdy0 hdy1
    have hu : (((rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (x0 - K.kx) (x1 - K.kx)).1
        + (rmul4 (ratCosSin t0).2 (ratCosSin t1).2 (y0 - K.ky) (y1 - K.ky)).1 : ℚ) : ℝ)
        ≤ cosT q.t * (q.cx - (K.kx : ℝ)) + sinT q.t * (q.cy - (K.ky : ℝ)) := by
      push_cast
      linarith
    have hv : cosT q.t * (q.cx - (K.kx : ℝ)) + sinT q.t * (q.cy - (K.ky : ℝ))
        ≤ (((rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (x0 - K.kx) (x1 - K.kx)).2
        + (rmul4 (ratCosSin t0).2 (ratCosSin t1).2 (y0 - K.ky) (y1 - K.ky)).2 : ℚ) : ℝ) := by
      push_cast
      linarith
    have := abs_le_of_between hT3 hu hv
    calc |cosT q.t * (q.cx - (K.kx : ℝ)) + sinT q.t * (q.cy - (K.ky : ℝ))|
        ≤ ((1 / 2 + K.a * gInf K t0 t1 : ℚ) : ℝ) := this
      _ = 1 / 2 + (K.a : ℝ) * ((gInf K t0 t1 : ℚ) : ℝ) := by push_cast; ring
  have P4 : |(-(sinT q.t)) * (q.cx - (K.kx : ℝ)) + cosT q.t * (q.cy - (K.ky : ℝ))|
      ≤ 1 / 2 + (K.a : ℝ) * ((gInf K t0 t1 : ℚ) : ℝ) := by
    have hnSl : ((-(ratCosSin t1).2 : ℚ) : ℝ) ≤ -(sinT q.t) := by
      push_cast; linarith
    have hnSu : -(sinT q.t) ≤ ((-(ratCosSin t0).2 : ℚ) : ℝ) := by
      push_cast; linarith
    obtain ⟨ha0, ha1⟩ := rmul4_bounds hnSl hnSu hdx0 hdx1
    obtain ⟨hb0, hb1⟩ := rmul4_bounds hCl hCu hdy0 hdy1
    have hu : (((rmul4 (-(ratCosSin t1).2) (-(ratCosSin t0).2) (x0 - K.kx) (x1 - K.kx)).1
        + (rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (y0 - K.ky) (y1 - K.ky)).1 : ℚ) : ℝ)
        ≤ (-(sinT q.t)) * (q.cx - (K.kx : ℝ)) + cosT q.t * (q.cy - (K.ky : ℝ)) := by
      push_cast
      linarith
    have hv : (-(sinT q.t)) * (q.cx - (K.kx : ℝ)) + cosT q.t * (q.cy - (K.ky : ℝ))
        ≤ (((rmul4 (-(ratCosSin t1).2) (-(ratCosSin t0).2) (x0 - K.kx) (x1 - K.kx)).2
        + (rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (y0 - K.ky) (y1 - K.ky)).2 : ℚ) : ℝ) := by
      push_cast
      linarith
    have := abs_le_of_between hT4 hu hv
    calc |(-(sinT q.t)) * (q.cx - (K.kx : ℝ)) + cosT q.t * (q.cy - (K.ky : ℝ))|
        ≤ ((1 / 2 + K.a * gInf K t0 t1 : ℚ) : ℝ) := this
      _ = 1 / 2 + (K.a : ℝ) * ((gInf K t0 t1 : ℚ) : ℝ) := by push_cast; ring
  -- the geometric step
  obtain ⟨px, py, ⟨hK1, hK2⟩, hQ1, hQ2⟩ :=
    core_meet (C := cosT q.t) (S := sinT q.t) (cm := cosT (K.tm : ℝ))
      (sm := sinT (K.tm : ℝ)) (aK := (K.a : ℝ)) (gR := ((gInf K t0 t1 : ℚ) : ℝ))
      (dx := q.cx - (K.kx : ℝ)) (dy := q.cy - (K.ky : ℝ))
      (cosT_sq_add_sinT_sq q.t) (cosT_sq_add_sinT_sq (K.tm : ℝ)) haKR
      (add_nonneg (mul_nonneg (cosT_nonneg hqt00 hqt11) hcm0)
        (mul_nonneg (sinT_nonneg hqt00) hsm0)) hgle P1 P2 P3 P4
  -- the common point
  refine ⟨((K.kx : ℝ) + px, (K.ky : ℝ) + py), ?_, ?_, ?_⟩
  · -- in the unit square
    rw [mem_set_iff_uv]
    constructor
    · have e : rdot (((K.kx : ℝ) + px) - q.cx, ((K.ky : ℝ) + py) - q.cy) (edir q)
          = cosT q.t * (px - (q.cx - (K.kx : ℝ)))
            + sinT q.t * (py - (q.cy - (K.ky : ℝ))) := by
        simp only [rdot, edir]
        ring
      rw [e]
      exact hQ1
    · have e : rdot (((K.kx : ℝ) + px) - q.cx, ((K.ky : ℝ) + py) - q.cy)
          (perpV (edir q))
          = (-(sinT q.t)) * (px - (q.cx - (K.kx : ℝ)))
            + cosT q.t * (py - (q.cy - (K.ky : ℝ))) := by
        simp only [rdot, edir, perpV]
        ring
      rw [e]
      exact hQ2
  · -- in the core (first axis)
    change |(((K.kx : ℝ) + px) - (K.kx : ℝ)) * cosT (K.tm : ℝ)
        + (((K.ky : ℝ) + py) - (K.ky : ℝ)) * sinT (K.tm : ℝ)| ≤ (K.a : ℝ)
    have e : (((K.kx : ℝ) + px) - (K.kx : ℝ)) * cosT (K.tm : ℝ)
        + (((K.ky : ℝ) + py) - (K.ky : ℝ)) * sinT (K.tm : ℝ)
        = px * cosT (K.tm : ℝ) + py * sinT (K.tm : ℝ) := by ring
    rw [e]
    exact hK1
  · change |(-(((K.kx : ℝ) + px) - (K.kx : ℝ))) * sinT (K.tm : ℝ)
        + (((K.ky : ℝ) + py) - (K.ky : ℝ)) * cosT (K.tm : ℝ)| ≤ (K.a : ℝ)
    have e : (-(((K.kx : ℝ) + px) - (K.kx : ℝ))) * sinT (K.tm : ℝ)
        + (((K.ky : ℝ) + py) - (K.ky : ℝ)) * cosT (K.tm : ℝ)
        = (-px) * sinT (K.tm : ℝ) + py * cosT (K.tm : ℝ) := by ring
    rw [e]
    exact hK2

/-- **`nofam_exempt` is sound**: a passing test proves every placement of the box has
its `(centre, t)` in the zone. -/
theorem nofamExempt_sound {f : CNoFam} {t0 t1 x0 x1 y0 y1 : ℚ} {q : PSq}
    (hqt0 : (t0 : ℝ) ≤ q.t) (hqt1 : q.t ≤ (t1 : ℝ))
    (hx0 : (x0 : ℝ) ≤ q.cx) (hx1 : q.cx ≤ (x1 : ℝ))
    (hy0 : (y0 : ℝ) ≤ q.cy) (hy1 : q.cy ≤ (y1 : ℝ))
    (h : nofamExempt f t0 t1 x0 x1 y0 y1 = true) : InZone f q := by
  simp only [nofamExempt, Bool.and_eq_true, decide_eq_true_eq, List.any_eq_true] at h
  obtain ⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, iv, hiv, h5⟩ := h
  refine ⟨?_, ?_, ?_, ?_, iv, hiv, ?_, ?_⟩
  · calc (f.x0 : ℝ) ≤ (x0 : ℝ) := by exact_mod_cast h1
      _ ≤ q.cx := hx0
  · calc q.cx ≤ (x1 : ℝ) := hx1
      _ ≤ (f.x1 : ℝ) := by exact_mod_cast h2
  · calc (f.y0 : ℝ) ≤ (y0 : ℝ) := by exact_mod_cast h3
      _ ≤ q.cy := hy0
  · calc q.cy ≤ (y1 : ℝ) := hy1
      _ ≤ (f.y1 : ℝ) := by exact_mod_cast h4
  · calc (iv.1 : ℝ) ≤ (t0 : ℝ) := by exact_mod_cast h5.1
      _ ≤ q.t := hqt0
  · calc q.t ≤ (t1 : ℝ) := hqt1
      _ ≤ (iv.2 : ℝ) := by exact_mod_cast h5.2

/-- **The exemption dispatcher is sound** (integer-box level): a passing `exemptB`
proves the placement meets some core or lies in some NO-family zone. -/
theorem exemptB_sound {ctx : Ctx} {cores : List CCore} {nofams : List CNoFam}
    {b : IBox} {q : PSq}
    (hR : 0 < ((ctx.TROOT : Int) : ℝ)) (hD : 0 < ((ctx.D : Int) : ℝ))
    (hT0 : 0 ≤ b.T0) (hT1 : b.T1 ≤ ctx.TROOT)
    (hq : inBox ctx b q)
    (hcores : ∀ K ∈ cores, coreOK K = true)
    (h : exemptB ctx cores nofams b = true) :
    (∃ K ∈ cores, (q.set ∩ coreSet K).Nonempty) ∨ ∃ f ∈ nofams, InZone f q := by
  obtain ⟨hqT0, hqT1, hqX0, hqX1, hqY0, hqY1⟩ := hq
  -- real values of the rational box coordinates
  have et0 : (((b.T0 : ℚ) / (ctx.TROOT : ℚ) : ℚ) : ℝ) = (b.T0 : ℝ) / (ctx.TROOT : ℝ) := by
    push_cast; ring
  have et1 : (((b.T1 : ℚ) / (ctx.TROOT : ℚ) : ℚ) : ℝ) = (b.T1 : ℝ) / (ctx.TROOT : ℝ) := by
    push_cast; ring
  have ex0 : (((b.X0 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.X0 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have ex1 : (((b.X1 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.X1 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have ey0 : (((b.Y0 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.Y0 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have ey1 : (((b.Y1 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.Y1 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have hqt0 : ((b.T0 : ℝ) / (ctx.TROOT : ℝ)) ≤ q.t := by
    rw [div_le_iff₀ hR]; exact hqT0
  have hqt1 : q.t ≤ (b.T1 : ℝ) / (ctx.TROOT : ℝ) := by
    rw [le_div_iff₀ hR]; exact hqT1
  have hx0 : ((b.X0 : ℝ) / (ctx.D : ℝ)) ≤ q.cx := by
    rw [div_le_iff₀ hD]; exact hqX0
  have hx1 : q.cx ≤ (b.X1 : ℝ) / (ctx.D : ℝ) := by
    rw [le_div_iff₀ hD]; exact hqX1
  have hy0 : ((b.Y0 : ℝ) / (ctx.D : ℝ)) ≤ q.cy := by
    rw [div_le_iff₀ hD]; exact hqY0
  have hy1 : q.cy ≤ (b.Y1 : ℝ) / (ctx.D : ℝ) := by
    rw [le_div_iff₀ hD]; exact hqY1
  have ht00 : (0 : ℝ) ≤ (b.T0 : ℝ) / (ctx.TROOT : ℝ) := by
    apply div_nonneg _ hR.le
    exact_mod_cast hT0
  have ht11 : (b.T1 : ℝ) / (ctx.TROOT : ℝ) ≤ 1 := by
    rw [div_le_one hR]
    exact_mod_cast hT1
  simp only [exemptB, Bool.or_eq_true, List.any_eq_true] at h
  rcases h with ⟨f, hf, hex⟩ | ⟨K, hK, hex⟩
  · exact Or.inr ⟨f, hf, nofamExempt_sound (et0 ▸ hqt0) (et1 ▸ hqt1) (ex0 ▸ hx0)
      (ex1 ▸ hx1) (ey0 ▸ hy0) (ey1 ▸ hy1) hex⟩
  · have hOK := hcores K hK
    simp only [coreOK, Bool.and_eq_true, decide_eq_true_eq] at hOK
    obtain ⟨⟨htm0, htm1⟩, ha⟩ := hOK
    exact Or.inl ⟨K, hK, coreExempt_sound htm0 htm1 (le_of_lt ha)
      (et0 ▸ ht00) (et1 ▸ ht11) (et0 ▸ hqt0) (et1 ▸ hqt1)
      (ex0 ▸ hx0) (ex1 ▸ hx1) (ey0 ▸ hy0) (ey1 ▸ hy1) hex⟩

end

end S11
end PackingCert
