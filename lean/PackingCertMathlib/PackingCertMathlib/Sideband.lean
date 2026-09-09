import Mathlib.Tactic
import PackingCertMathlib.SatInterior
import PackingCertMathlib.Ceil

/-!
# Sideband — the ℓ∞ separation of centres and the corner-cell lemma (A169, `docs/proofs/sideband.md`)

Two unit squares with disjoint interiors have centres at ℓ∞-distance `≥ 1/√2` (`linf_sep`,
from `sat_selection_thm`: the separating axis `a` gives `|Δ·a| ≥ 1` and Cauchy–Schwarz gives
`Δ·a ≤ |Δ|`).  A square meeting the OPEN corner box `(0, c)²` has its centre in
`[1/2, c + 1/√2)²` (`meeter_centre_bounds`), so when `c < 1/2 + 1/√2` every cell of the grid
`{x < c, x ≥ c} × {y < c, y ≥ c}` has ℓ∞-diameter `< 1/√2` and two interior-disjoint meeters
occupy DIFFERENT cells (`distinct_cells`); in particular they are never both in `[c, ∞)²`
(`not_both_ne`, the PI's sideband (a) with its sharp constant `c`).  Square roots are avoided:
`1/√2 ≤ |d|` is written `1/2 ≤ d²`.

No axiom is introduced.  Theorem B of the document (the exact second-meeter criterion) is
stated as `SecondMeeterCriterion` [C] and not proved here.
-/

namespace PackingCert
namespace S11

open Set
open PackingCert.S11.LocalCert

noncomputable section

/-! ## 1. Every point of a parametrised square is within `1/√2` of the centre -/

/-- (F1) of the document: `(p − z)·(p − z) ≤ 1/2` for `p ∈ q.set`. -/
theorem sqdist_centre_le_half (q : PSq) {p : RP} (hp : p ∈ q.set) :
    (p.1 - q.cx) ^ 2 + (p.2 - q.cy) ^ 2 ≤ 1 / 2 := by
  obtain ⟨hu, hv⟩ := (mem_set_iff_uv q p).mp hp
  simp only [rdot, edir, perpV] at hu hv
  have hcs := cosT_sq_add_sinT_sq q.t
  set d1 := p.1 - q.cx
  set d2 := p.2 - q.cy
  set c := cosT q.t
  set s := sinT q.t
  have hu2 : (d1 * c + d2 * s) ^ 2 ≤ 1 / 4 := by
    have := abs_le.mp hu
    nlinarith [this.1, this.2]
  have hv2 : (d1 * (-s) + d2 * c) ^ 2 ≤ 1 / 4 := by
    have := abs_le.mp hv
    nlinarith [this.1, this.2]
  have hid : (d1 * c + d2 * s) ^ 2 + (d1 * (-s) + d2 * c) ^ 2 = (d1 ^ 2 + d2 ^ 2) * (c ^ 2 + s ^ 2) := by
    ring
  rw [hcs, mul_one] at hid
  linarith

/-! ## 2. The ℓ∞ separation of the centres of two interior-disjoint squares -/

/-- `|cos Δ| + |sin Δ| ≥ 1`: the support width of a unit square in any direction is `≥ 1`. -/
theorem wrel_ge_one (qw qo : PSq) : 1 ≤ wrel qw qo := by
  unfold wrel
  set x := cosT qw.t * cosT qo.t + sinT qw.t * sinT qo.t
  set y := cosT qw.t * sinT qo.t - sinT qw.t * cosT qo.t
  have hxy : x ^ 2 + y ^ 2 = 1 := by
    have h1 := cosT_sq_add_sinT_sq qw.t
    have h2 := cosT_sq_add_sinT_sq qo.t
    simp only [x, y]
    nlinarith [h1, h2]
  have hx := abs_nonneg x
  have hy := abs_nonneg y
  have hx2 : |x| ^ 2 = x ^ 2 := sq_abs x
  have hy2 : |y| ^ 2 = y ^ 2 := sq_abs y
  nlinarith [mul_nonneg hx hy]

/-- Along the owner's axis `a_k`: `(Δ·a)² ≤ Δ·Δ` (Cauchy–Schwarz with a unit vector). -/
theorem proj_sq_le (qw : PSq) (k : Bool) (dx dy : ℝ) :
    (dx * (axk qw k).1 + dy * (axk qw k).2) ^ 2 ≤ dx ^ 2 + dy ^ 2 := by
  have hcs := cosT_sq_add_sinT_sq qw.t
  cases k <;> simp only [axk, Bool.false_eq_true, ↓reduceIte] <;> nlinarith [sq_nonneg (dx * sinT qw.t - dy * cosT qw.t), sq_nonneg (dx * cosT qw.t + dy * sinT qw.t), hcs]

/-- From a nonnegative selection row: `Δx² + Δy² ≥ 1`. -/
theorem sep_of_gsel {qw qo : PSq} {k : Bool} {eps : ℝ} (heps : eps = 1 ∨ eps = -1)
    (hg : 0 ≤ gsel qw qo k eps) :
    1 ≤ (qo.cx - qw.cx) ^ 2 + (qo.cy - qw.cy) ^ 2 := by
  unfold gsel at hg
  have hw := wrel_ge_one qw qo
  set P := (qo.cx - qw.cx) * (axk qw k).1 + (qo.cy - qw.cy) * (axk qw k).2
  have hP : 1 ≤ eps * P := by linarith
  have hP2 : 1 ≤ P ^ 2 := by
    rcases heps with h | h <;> subst h <;> nlinarith [hP]
  have := proj_sq_le qw k (qo.cx - qw.cx) (qo.cy - qw.cy)
  linarith

/-- **Lemma A1.**  Interior-disjoint unit squares have centres at ℓ∞-distance `≥ 1/√2`. -/
theorem linf_sep (qw qo : PSq) (h : Disjoint (interior qw.set) (interior qo.set)) :
    1 / 2 ≤ (qo.cx - qw.cx) ^ 2 ∨ 1 / 2 ≤ (qo.cy - qw.cy) ^ 2 := by
  have hsum : 1 ≤ (qo.cx - qw.cx) ^ 2 + (qo.cy - qw.cy) ^ 2 := by
    rcases sat_selection_thm qw qo h with ⟨k, eps, heps, hg⟩ | ⟨k, eps, heps, hg⟩
    · exact sep_of_gsel heps hg
    · have := sep_of_gsel heps hg
      nlinarith [this]
  by_contra hcon
  push Not at hcon
  linarith [hcon.1, hcon.2]

/-- The square-root form of Lemma A1's coordinate bound: `1/√2 ≤ |d|` from `1/2 ≤ d²`. -/
theorem inv_sqrt_two_le_abs {d : ℝ} (h : 1 / 2 ≤ d ^ 2) : 1 / Real.sqrt 2 ≤ |d| := by
  have h' : (2 : ℝ)⁻¹ ≤ d ^ 2 := by rwa [inv_eq_one_div]
  rw [one_div, ← Real.sqrt_inv, ← Real.sqrt_sq_eq_abs]
  exact Real.sqrt_le_sqrt h'

/-- **Lemma A1, square-root form.** -/
theorem linf_sep_sqrt (qw qo : PSq) (h : Disjoint (interior qw.set) (interior qo.set)) :
    1 / Real.sqrt 2 ≤ |qo.cx - qw.cx| ∨ 1 / Real.sqrt 2 ≤ |qo.cy - qw.cy| := by
  rcases linf_sep qw qo h with h1 | h1
  · exact Or.inl (inv_sqrt_two_le_abs h1)
  · exact Or.inr (inv_sqrt_two_le_abs h1)

/-! ## 3. Meeters of the open corner box and their centres -/

/-- `q` MEETS the open corner box `(0, c)²` (BL corner, container coordinates). -/
def Meets (q : PSq) (c : ℝ) : Prop :=
  ∃ p ∈ q.set, 0 < p.1 ∧ p.1 < c ∧ 0 < p.2 ∧ p.2 < c

/-- `q` lies in the closed quadrant `{x ≥ 0, y ≥ 0}`. -/
def InQuadrant (q : PSq) : Prop := ∀ p ∈ q.set, 0 ≤ p.1 ∧ 0 ≤ p.2

/-- The point `z + a e + b e⊥` of the square, `|a|, |b| ≤ 1/2`. -/
theorem vertex_mem (q : PSq) (a b : ℝ) (ha : |a| ≤ 1 / 2) (hb : |b| ≤ 1 / 2) :
    (q.cx + a * cosT q.t - b * sinT q.t, q.cy + a * sinT q.t + b * cosT q.t) ∈ q.set := by
  rw [mem_set_iff_uv]
  simp only [rdot, edir, perpV]
  have hcs := cosT_sq_add_sinT_sq q.t
  have ka : a * (cosT q.t ^ 2 + sinT q.t ^ 2) = a := by rw [hcs, mul_one]
  have kb : b * (cosT q.t ^ 2 + sinT q.t ^ 2) = b := by rw [hcs, mul_one]
  have ha' := abs_le.mp ha
  have hb' := abs_le.mp hb
  constructor
  · rw [abs_le]; constructor <;> nlinarith [ka, ha'.1, ha'.2]
  · rw [abs_le]; constructor <;> nlinarith [kb, hb'.1, hb'.2]

/-- (F2): a square in the quadrant has centre coordinates `≥ 1/2` (`t ∈ [0, 1]`). -/
theorem quad_centre_ge_half (q : PSq) (ht0 : 0 ≤ q.t) (ht1 : q.t ≤ 1) (hq : InQuadrant q) :
    1 / 2 ≤ q.cx ∧ 1 / 2 ≤ q.cy := by
  have hc := cosT_nonneg ht0 ht1
  have hs := sinT_nonneg ht0
  have hcs := cosT_sq_add_sinT_sq q.t
  have hw : 1 ≤ cosT q.t + sinT q.t := by nlinarith [mul_nonneg hc hs]
  have hh : |(-1 / 2 : ℝ)| ≤ 1 / 2 := by rw [abs_le]; constructor <;> norm_num
  have hh' : |(1 / 2 : ℝ)| ≤ 1 / 2 := by rw [abs_le]; constructor <;> norm_num
  have h1 := hq _ (vertex_mem q (-1 / 2) (1 / 2) hh hh')
  have h2 := hq _ (vertex_mem q (-1 / 2) (-1 / 2) hh hh)
  constructor
  · linarith [h1.1]
  · linarith [h2.2]

/-- A meeter's centre lies within `1/√2` beyond the line `x = c` (if it is beyond it at all). -/
theorem meeter_cx (q : PSq) {c : ℝ} (hm : Meets q c) (hc : c ≤ q.cx) :
    (q.cx - c) ^ 2 < 1 / 2 := by
  obtain ⟨p, hp, -, hx, -, -⟩ := hm
  have hd := sqdist_centre_le_half q hp
  have key := mul_pos (sub_pos.mpr hx) (by linarith : (0 : ℝ) < (q.cx - p.1) + (q.cx - c))
  nlinarith [sq_nonneg (p.2 - q.cy)]

theorem meeter_cy (q : PSq) {c : ℝ} (hm : Meets q c) (hc : c ≤ q.cy) :
    (q.cy - c) ^ 2 < 1 / 2 := by
  obtain ⟨p, hp, -, -, -, hy⟩ := hm
  have hd := sqdist_centre_le_half q hp
  have key := mul_pos (sub_pos.mpr hy) (by linarith : (0 : ℝ) < (q.cy - p.2) + (q.cy - c))
  nlinarith [sq_nonneg (p.1 - q.cx)]

/-! ## 4. The cells of the `2 × 2` grid at threshold `c` -/

/-- Two coordinates in the half-open cell `[c, c + 1/√2)` differ by less than `1/√2`. -/
theorem sq_sub_lt_of_ge {c x x' : ℝ} (hx : c ≤ x) (hx' : c ≤ x')
    (a : (x - c) ^ 2 < 1 / 2) (b : (x' - c) ^ 2 < 1 / 2) : (x' - x) ^ 2 < 1 / 2 := by
  rcases le_total x x' with hle | hle
  · have := mul_nonneg (by linarith : (0 : ℝ) ≤ (x' - c) - (x' - x))
      (by linarith : (0 : ℝ) ≤ (x' - c) + (x' - x))
    nlinarith
  · have := mul_nonneg (by linarith : (0 : ℝ) ≤ (x - c) - (x - x'))
      (by linarith : (0 : ℝ) ≤ (x - c) + (x - x'))
    nlinarith

/-- Two coordinates in the cell `[1/2, c)` differ by less than `1/√2` when `c < 1/2 + 1/√2`. -/
theorem sq_sub_lt_of_lt {c x x' : ℝ} (hc : (c - 1 / 2) ^ 2 < 1 / 2)
    (hx : 1 / 2 ≤ x) (hx' : 1 / 2 ≤ x') (h : x < c) (h' : x' < c) : (x' - x) ^ 2 < 1 / 2 := by
  rcases le_total x x' with hle | hle
  · have := mul_nonneg (by linarith : (0 : ℝ) ≤ (c - 1 / 2) - (x' - x))
      (by linarith : (0 : ℝ) ≤ (c - 1 / 2) + (x' - x))
    nlinarith
  · have := mul_nonneg (by linarith : (0 : ℝ) ≤ (c - 1 / 2) - (x - x'))
      (by linarith : (0 : ℝ) ≤ (c - 1 / 2) + (x - x'))
    nlinarith

/-- Same side of `c` (meeter coordinates from the quadrant) ⇒ `Δ² < 1/2`. -/
theorem same_side_sq_lt {c x x' : ℝ} (hc : (c - 1 / 2) ^ 2 < 1 / 2)
    (hx : 1 / 2 ≤ x) (hx' : 1 / 2 ≤ x')
    (hlo : c ≤ x → (x - c) ^ 2 < 1 / 2) (hlo' : c ≤ x' → (x' - c) ^ 2 < 1 / 2)
    (hsame : x < c ↔ x' < c) : (x' - x) ^ 2 < 1 / 2 := by
  by_cases h : x < c
  · exact sq_sub_lt_of_lt hc hx hx' h (hsame.mp h)
  · push Not at h
    have h' : c ≤ x' := by
      by_contra hh
      push Not at hh
      exact absurd (hsame.mpr hh) (not_lt.mpr h)
    exact sq_sub_lt_of_ge h h' (hlo h) (hlo' h')

/-- The hypothesis `(c − 1/2)² < 1/2` from `c < 1/2 + 1/√2`. -/
theorem cell_hyp_of_lt {c : ℝ} (h0 : 1 / 2 ≤ c) (h : c < 1 / 2 + 1 / Real.sqrt 2) :
    (c - 1 / 2) ^ 2 < 1 / 2 := by
  have h2 : (0 : ℝ) < Real.sqrt 2 := by positivity
  have hs : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hy : c - 1 / 2 < 1 / Real.sqrt 2 := by linarith
  rw [lt_div_iff₀ h2] at hy
  have hy0 : 0 ≤ (c - 1 / 2) * Real.sqrt 2 := mul_nonneg (by linarith) h2.le
  have hp := mul_pos (sub_pos.mpr hy) (by linarith : (0 : ℝ) < 1 + (c - 1 / 2) * Real.sqrt 2)
  have hsq : ((c - 1 / 2) * Real.sqrt 2) ^ 2 = 2 * (c - 1 / 2) ^ 2 := by rw [mul_pow, hs]; ring
  nlinarith [hp, hsq]

/-- **Lemma A2 (cells).**  Two interior-disjoint meeters of `(0, c)²` in the quadrant,
`c < 1/2 + 1/√2`, have centres in DIFFERENT cells of the grid `{x < c, x ≥ c} × {y < c, y ≥ c}`. -/
theorem distinct_cells (q q' : PSq) {c : ℝ} (hc : (c - 1 / 2) ^ 2 < 1 / 2)
    (ht0 : 0 ≤ q.t) (ht1 : q.t ≤ 1) (ht0' : 0 ≤ q'.t) (ht1' : q'.t ≤ 1)
    (hq : InQuadrant q) (hq' : InQuadrant q') (hm : Meets q c) (hm' : Meets q' c)
    (hd : Disjoint (interior q.set) (interior q'.set)) :
    ¬ ((q.cx < c ↔ q'.cx < c) ∧ (q.cy < c ↔ q'.cy < c)) := by
  rintro ⟨hx, hy⟩
  have h1 := quad_centre_ge_half q ht0 ht1 hq
  have h2 := quad_centre_ge_half q' ht0' ht1' hq'
  have ex := same_side_sq_lt hc h1.1 h2.1 (meeter_cx q hm) (meeter_cx q' hm') hx
  have ey := same_side_sq_lt hc h1.2 h2.2 (meeter_cy q hm) (meeter_cy q' hm') hy
  rcases linf_sep q q' hd with h | h <;> linarith

/-- **SIDEBAND (a), sharp constant `c`.**  Two interior-disjoint meeters of `(0, c)²` never both
have centres in `[c, ∞)²` — no quadrant hypothesis and no bound on `c` are needed. -/
theorem not_both_ne (q q' : PSq) {c : ℝ} (hm : Meets q c) (hm' : Meets q' c)
    (hd : Disjoint (interior q.set) (interior q'.set)) :
    ¬ (c ≤ q.cx ∧ c ≤ q.cy ∧ c ≤ q'.cx ∧ c ≤ q'.cy) := by
  rintro ⟨h1, h2, h3, h4⟩
  have ex := sq_sub_lt_of_ge h1 h3 (meeter_cx q hm h1) (meeter_cx q' hm' h3)
  have ey := sq_sub_lt_of_ge h2 h4 (meeter_cy q hm h2) (meeter_cy q' hm' h4)
  rcases linf_sep q q' hd with h | h <;> linarith

/-- The band form of SIDEBAND (a): one of the two centres has `x < c` or `y < c`. -/
theorem sideband_a (q q' : PSq) {c : ℝ} (hm : Meets q c) (hm' : Meets q' c)
    (hd : Disjoint (interior q.set) (interior q'.set)) :
    q.cx < c ∨ q.cy < c ∨ q'.cx < c ∨ q'.cy < c := by
  by_contra hcon
  push Not at hcon
  exact not_both_ne q q' hm hm' hd ⟨hcon.1, hcon.2.1, hcon.2.2.1, hcon.2.2.2⟩

end

end S11
end PackingCert
