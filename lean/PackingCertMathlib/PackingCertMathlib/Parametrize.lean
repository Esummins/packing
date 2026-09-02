import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.Bridge

/-!
# The parametrisation lemma (A64, depgraph node A.PARAM)

Every closed unit square in the plane is `PSq.set` of a parametrised square
`(cx, cy, t)` with `t = tan(θ/2) ∈ [0,1]` — the domain every certificate family
(measure checkers, case-LP kills, parametric window certificates) quantifies over.
Prose: `docs/proofs/parametrization.md`.  This file discharges the geometry of the
`parametrize` axiom of `TopLevel.lean` (the packing-level theorem is proved there
from the single-square statement `isUnitSquare_exists_psq` below).

Contents:

* the configuration layer (`cosT`, `sinT`, `PSq`, `edir`, `baseCorner`, `PSq.set`),
  moved here from `TopLevel.lean` unchanged (same namespace, same definitions);
* `sqSet_rot` — the square's own 90° symmetry: `sqSet p0 e` equals the square based
  at the next corner with the perpendicular edge vector.  Up to three applications
  bring any unit edge vector into the closed first quadrant (`exists_nonneg_dir`);
* the half-angle substitution `t = e₂/(1+e₁)`: for a unit vector `e` with
  `e₁, e₂ ≥ 0` one has `t ∈ [0,1]`, `cosT t = e₁` and `sinT t = e₂` — pure algebra,
  no transcendental functions enter (`cosT_halfAngle`, `sinT_halfAngle`);
* `isUnitSquare_exists_psq` — the composed single-square parametrisation;
* membership and containment characterisations of `PSq.set` used by the measure
  bridge (A.F2): `mem_set_iff_uv` (`p ∈ Q ⟺ |u| ≤ ½ ∧ |v| ≤ ½`) and
  `set_subset_container_iff` (`Q ⊆ [0,s]² ⟺ w/2 ≤ c ≤ s − w/2`, `w = cos + sin`),
  plus quasiconcavity of `w` on `[0,1]` (`wT_ge_min`, the clipping step).
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-! ## The packing problem, set level (moved verbatim from `TopLevel.lean`, A64) -/

/-- The closed container `[0,s]²`. -/
def container (s : ℝ) : Set RP := Icc (0 : ℝ) s ×ˢ Icc (0 : ℝ) s

/-- A **packing** of `n` unit squares at side `s`: `n` closed unit squares (`IsUnitSquare`,
from `Bridge.lean`: congruent copies of `[0,1]²`), each contained in the closed container,
with pairwise disjoint **interiors** (contacts allowed — Trump's packing has 56 of them;
`Disjoint (Q i) (Q j)` on the closed sets, as in the A28 upper-bound theorem, would be the
WRONG notion here: it is strictly stronger and does not admit the extremal packing).
Findings F1. -/
structure IsPacking (n : ℕ) (s : ℝ) (Q : Fin n → Set RP) : Prop where
  unit : ∀ i, IsUnitSquare (Q i)
  contained : ∀ i, Q i ⊆ container s
  interiorDisjoint : ∀ i j, i ≠ j → Disjoint (interior (Q i)) (interior (Q j))

/-- `n` unit squares fit in `[0,s]²`. Monotone in `s` by construction of `container`. -/
def Fits (n : ℕ) (s : ℝ) : Prop := ∃ Q : Fin n → Set RP, IsPacking n s Q

/-! ## The configuration layer (moved verbatim from `TopLevel.lean`) -/

/-- `cos θ` as a rational function of `t = tan(θ/2)`. -/
def cosT (t : ℝ) : ℝ := (1 - t ^ 2) / (1 + t ^ 2)

/-- `sin θ` as a rational function of `t = tan(θ/2)`. -/
def sinT (t : ℝ) : ℝ := 2 * t / (1 + t ^ 2)

/-- A parametrised square: centre `(cx, cy)`, orientation `t = tan(θ/2) ∈ [0,1]`
(`θ ∈ [0°, 90°]`; `t = 0` and `t = 1` denote the same square set — findings F8). -/
structure PSq where
  cx : ℝ
  cy : ℝ
  t : ℝ

/-- The unit edge vector `(cos θ, sin θ)` of a parametrised square. -/
def edir (q : PSq) : RP := (cosT q.t, sinT q.t)

/-- The base corner: centre minus `(e + e⊥)/2`. -/
def baseCorner (q : PSq) : RP :=
  (q.cx - (cosT q.t - sinT q.t) / 2, q.cy - (cosT q.t + sinT q.t) / 2)

/-- The closed unit square denoted by a parametrised square (via `Bridge.sqSet`). -/
def PSq.set (q : PSq) : Set RP := sqSet (baseCorner q) (edir q)

/-! ## Basic algebra of the half-angle functions -/

theorem one_add_sq_pos (t : ℝ) : (0 : ℝ) < 1 + t ^ 2 := by positivity

/-- `cos² + sin² = 1` in the rational parametrisation — for EVERY real `t`. -/
theorem cosT_sq_add_sinT_sq (t : ℝ) : cosT t ^ 2 + sinT t ^ 2 = 1 := by
  have h : (1 + t ^ 2 : ℝ) ≠ 0 := (one_add_sq_pos t).ne'
  unfold cosT sinT
  field_simp
  ring

/-- The edge vector of a parametrised square is a unit vector. -/
theorem rdot_edir (q : PSq) : rdot (edir q) (edir q) = 1 := by
  simp only [rdot, edir]
  linear_combination cosT_sq_add_sinT_sq q.t

theorem cosT_nonneg {t : ℝ} (h0 : 0 ≤ t) (h1 : t ≤ 1) : 0 ≤ cosT t := by
  have h := one_add_sq_pos t
  exact div_nonneg (by nlinarith) (by positivity)

theorem sinT_nonneg {t : ℝ} (h0 : 0 ≤ t) : 0 ≤ sinT t := by
  have h := one_add_sq_pos t
  exact div_nonneg (by nlinarith) (by positivity)

theorem cosT_le_one (t : ℝ) : cosT t ≤ 1 := by
  have h := one_add_sq_pos t
  rw [cosT, div_le_one h]
  nlinarith

theorem sinT_le_one (t : ℝ) : sinT t ≤ 1 := by
  have h := one_add_sq_pos t
  rw [sinT, div_le_one h]
  nlinarith [sq_nonneg (1 - t)]

/-! ## The square's own 90° symmetry -/

/-- Counter-clockwise 90° rotation of a vector: `e ↦ e⊥ = (−e₂, e₁)`. -/
def perpV (e : RP) : RP := (-e.2, e.1)

theorem rdot_perpV (e : RP) : rdot (perpV e) (perpV e) = rdot e e := by
  simp only [rdot, perpV]
  ring

/-- Rotating the description of a square: the square based at the next corner
`p0 + e` with edge vector `e⊥` is the SAME point set.  (Parameter map
`(a, b) ↦ (1 − b, a)`.) -/
theorem sqSet_rot (p0 e : RP) :
    sqSet (p0.1 + e.1, p0.2 + e.2) (perpV e) = sqSet p0 e := by
  ext q
  constructor
  · rintro ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩
    refine ⟨1 - b, a, by linarith, by linarith, ha0, ha1, ?_⟩
    simp only [aff, perpV, Prod.mk.injEq]
    exact ⟨by ring, by ring⟩
  · rintro ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩
    refine ⟨b, 1 - a, hb0, hb1, by linarith, by linarith, ?_⟩
    simp only [aff, perpV, Prod.mk.injEq]
    exact ⟨by ring, by ring⟩

/-- One rotation step, existential form: some base corner works for `e⊥`. -/
theorem rot_step (p0 e : RP) : ∃ p0' : RP, sqSet p0' (perpV e) = sqSet p0 e :=
  ⟨(p0.1 + e.1, p0.2 + e.2), sqSet_rot p0 e⟩

/-- Every unit square has a representation whose edge vector lies in the closed
first quadrant: apply `sqSet_rot` 0–3 times. -/
theorem exists_nonneg_dir {S : Set RP} (h : IsUnitSquare S) :
    ∃ p0 e : RP, rdot e e = 1 ∧ 0 ≤ e.1 ∧ 0 ≤ e.2 ∧ S = sqSet p0 e := by
  obtain ⟨p0, e, he, rfl⟩ := h
  obtain ⟨q1, hq1⟩ := rot_step p0 e
  obtain ⟨q2, hq2⟩ := rot_step q1 (perpV e)
  obtain ⟨q3, hq3⟩ := rot_step q2 (perpV (perpV e))
  rcases le_total 0 e.1 with h1 | h1 <;> rcases le_total 0 e.2 with h2 | h2
  · -- first quadrant: as is
    exact ⟨p0, e, he, h1, h2, rfl⟩
  · -- fourth quadrant (`e₂ ≤ 0`): one rotation, new edge `(−e₂, e₁)`
    exact ⟨q1, perpV e, by rw [rdot_perpV]; exact he,
      by simpa [perpV] using h2, by simpa [perpV] using h1, hq1.symm⟩
  · -- second quadrant (`e₁ ≤ 0`): three rotations, new edge `(e₂, −e₁)`
    exact ⟨q3, perpV (perpV (perpV e)),
      by rw [rdot_perpV, rdot_perpV, rdot_perpV]; exact he,
      by simpa [perpV] using h2, by simpa [perpV] using h1,
      ((hq3.trans hq2).trans hq1).symm⟩
  · -- third quadrant: two rotations, new edge `(−e₁, −e₂)`
    exact ⟨q2, perpV (perpV e), by rw [rdot_perpV, rdot_perpV]; exact he,
      by simpa [perpV] using h1, by simpa [perpV] using h2,
      (hq2.trans hq1).symm⟩

/-! ## The half-angle substitution -/

/-- `1 + t² = 2/(1+e₁)` at `t = e₂/(1+e₁)` for a unit vector `e`. -/
theorem halfAngle_denom {e : RP} (he : rdot e e = 1) (h1 : 0 ≤ e.1) :
    1 + (e.2 / (1 + e.1)) ^ 2 = 2 / (1 + e.1) := by
  have hd : (0 : ℝ) < 1 + e.1 := by linarith
  have he' : e.1 * e.1 + e.2 * e.2 = 1 := he
  field_simp
  linear_combination he'

/-- `1 − t² = 2e₁/(1+e₁)` at `t = e₂/(1+e₁)` for a unit vector `e`. -/
theorem halfAngle_num {e : RP} (he : rdot e e = 1) (h1 : 0 ≤ e.1) :
    1 - (e.2 / (1 + e.1)) ^ 2 = 2 * e.1 / (1 + e.1) := by
  have hd : (0 : ℝ) < 1 + e.1 := by linarith
  have he' : e.1 * e.1 + e.2 * e.2 = 1 := he
  field_simp
  linear_combination (-1 : ℝ) * he'

/-- For a unit vector in the closed half-plane `e₁ ≥ 0`, `t = e₂/(1+e₁)`
recovers `e₁` as `cosT t`.  Pure algebra from `e₁² + e₂² = 1`. -/
theorem cosT_halfAngle {e : RP} (he : rdot e e = 1) (h1 : 0 ≤ e.1) :
    cosT (e.2 / (1 + e.1)) = e.1 := by
  have hd : (0 : ℝ) < 1 + e.1 := by linarith
  have hd0 : (1 + e.1 : ℝ) ≠ 0 := hd.ne'
  rw [cosT, halfAngle_num he h1, halfAngle_denom he h1]
  rw [div_div_div_comm]
  simp [div_self hd0]

/-- For a unit vector in the closed half-plane `e₁ ≥ 0`, `t = e₂/(1+e₁)`
recovers `e₂` as `sinT t`. -/
theorem sinT_halfAngle {e : RP} (he : rdot e e = 1) (h1 : 0 ≤ e.1) :
    sinT (e.2 / (1 + e.1)) = e.2 := by
  have hd : (0 : ℝ) < 1 + e.1 := by linarith
  have hd0 : (1 + e.1 : ℝ) ≠ 0 := hd.ne'
  rw [sinT, halfAngle_denom he h1]
  rw [← mul_div_assoc, div_div_div_comm]
  simp [div_self hd0]

/-- The half-angle parameter lies in `[0,1]` when the unit vector is in the
closed first quadrant. -/
theorem halfAngle_mem_Icc {e : RP} (he : rdot e e = 1) (h1 : 0 ≤ e.1) (h2 : 0 ≤ e.2) :
    e.2 / (1 + e.1) ∈ Icc (0 : ℝ) 1 := by
  have hd : (0 : ℝ) < 1 + e.1 := by linarith
  have he' : e.1 * e.1 + e.2 * e.2 = 1 := he
  have h2le : e.2 ≤ 1 := by nlinarith
  exact ⟨div_nonneg h2 hd.le, (div_le_one hd).mpr (by linarith)⟩

/-! ## The single-square parametrisation (A.PARAM, square level) -/

/-- **Every closed unit square is a parametrised square with `t ∈ [0,1]`.**
The single-square content of the `parametrize` axiom: rotate the base
representation into the first quadrant (`exists_nonneg_dir`), then substitute the
half-angle parameter.  The centre is read off from the base corner. -/
theorem isUnitSquare_exists_psq {S : Set RP} (h : IsUnitSquare S) :
    ∃ q : PSq, q.t ∈ Icc (0 : ℝ) 1 ∧ S = q.set := by
  obtain ⟨p0, e, he, h1, h2, rfl⟩ := exists_nonneg_dir h
  obtain ⟨p0x, p0y⟩ := p0
  have hcos := cosT_halfAngle he h1
  have hsin := sinT_halfAngle he h1
  refine ⟨⟨p0x + (e.1 - e.2) / 2, p0y + (e.1 + e.2) / 2, e.2 / (1 + e.1)⟩,
    halfAngle_mem_Icc he h1 h2, ?_⟩
  have hbase : baseCorner ⟨p0x + (e.1 - e.2) / 2, p0y + (e.1 + e.2) / 2,
      e.2 / (1 + e.1)⟩ = (p0x, p0y) := by
    simp only [baseCorner, hcos, hsin, Prod.mk.injEq]
    exact ⟨by ring, by ring⟩
  have hedir : edir ⟨p0x + (e.1 - e.2) / 2, p0y + (e.1 + e.2) / 2,
      e.2 / (1 + e.1)⟩ = e := by
    simp only [edir, hcos, hsin]
  simp only [PSq.set, hbase, hedir]

/-! ## Membership and containment characterisations (for the measure bridge A.F2)

With `e = edir q` a unit vector, `{e, e⊥}` is an orthonormal basis; membership in
the square and containment in the container become the `u/v` and `w = cos + sin`
inequalities of the verifiers' headers. -/

/-- Expansion in the orthonormal basis `{e, e⊥}` (unit `e`). -/
theorem eq_aff_of_unit {e : RP} (he : rdot e e = 1) (p0 p : RP) :
    p = aff p0 e (rdot (p.1 - p0.1, p.2 - p0.2) e)
      (rdot (p.1 - p0.1, p.2 - p0.2) (perpV e)) := by
  have he' : e.1 * e.1 + e.2 * e.2 = 1 := he
  obtain ⟨px, py⟩ := p
  simp only [aff, rdot, perpV, Prod.mk.injEq]
  constructor
  · linear_combination (-(px - p0.1)) * he'
  · linear_combination (-(py - p0.2)) * he'

/-- `p ∈ sqSet p0 e ⟺` both `e`- and `e⊥`-coordinates of `p − p0` lie in `[0,1]`
(unit `e`). -/
theorem mem_sqSet_iff_coords {e : RP} (he : rdot e e = 1) (p0 p : RP) :
    p ∈ sqSet p0 e ↔
      rdot (p.1 - p0.1, p.2 - p0.2) e ∈ Icc (0 : ℝ) 1 ∧
      rdot (p.1 - p0.1, p.2 - p0.2) (perpV e) ∈ Icc (0 : ℝ) 1 := by
  have he' : e.1 * e.1 + e.2 * e.2 = 1 := he
  constructor
  · rintro ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩
    have hu : rdot ((aff p0 e a b).1 - p0.1, (aff p0 e a b).2 - p0.2) e = a := by
      simp only [aff, rdot]; linear_combination a * he'
    have hv : rdot ((aff p0 e a b).1 - p0.1, (aff p0 e a b).2 - p0.2) (perpV e) = b := by
      simp only [aff, rdot, perpV]; linear_combination b * he'
    rw [hu, hv]
    exact ⟨⟨ha0, ha1⟩, hb0, hb1⟩
  · rintro ⟨⟨ha0, ha1⟩, hb0, hb1⟩
    exact ⟨_, _, ha0, ha1, hb0, hb1, eq_aff_of_unit he p0 p⟩

/-- The base-corner coordinate is the centred coordinate plus `½` (both axes). -/
theorem coords_center_base (q : PSq) (p : RP) :
    rdot (p.1 - (baseCorner q).1, p.2 - (baseCorner q).2) (edir q)
        = rdot (p.1 - q.cx, p.2 - q.cy) (edir q) + 1 / 2 ∧
      rdot (p.1 - (baseCorner q).1, p.2 - (baseCorner q).2) (perpV (edir q))
        = rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q)) + 1 / 2 := by
  have hc := cosT_sq_add_sinT_sq q.t
  constructor <;>
    · simp only [rdot, baseCorner, edir, perpV]
      linear_combination hc / 2

/-- Membership in a parametrised square via the centred coordinates
`u = e·(p − c)`, `v = e⊥·(p − c)`: exactly `|u| ≤ ½ ∧ |v| ≤ ½`.  This is the
predicate the measure verifiers decide by interval arithmetic. -/
theorem mem_set_iff_uv (q : PSq) (p : RP) :
    p ∈ q.set ↔
      |rdot (p.1 - q.cx, p.2 - q.cy) (edir q)| ≤ 1 / 2 ∧
      |rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q))| ≤ 1 / 2 := by
  rw [PSq.set, mem_sqSet_iff_coords (rdot_edir q)]
  obtain ⟨hu, hv⟩ := coords_center_base q p
  rw [hu, hv, abs_le, abs_le]
  simp only [mem_Icc]
  constructor
  · rintro ⟨⟨ha0, ha1⟩, hb0, hb1⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩
  · rintro ⟨⟨ha0, ha1⟩, hb0, hb1⟩
    exact ⟨⟨by linarith, by linarith⟩, by linarith, by linarith⟩

/-- The container width function `w(t) = cos θ + sin θ`. -/
def wT (t : ℝ) : ℝ := cosT t + sinT t

theorem wT_ge_one {t : ℝ} (h0 : 0 ≤ t) (h1 : t ≤ 1) : 1 ≤ wT t := by
  unfold wT
  have hc0 := cosT_nonneg h0 h1
  have hs0 := sinT_nonneg h0
  have hc1 := cosT_le_one t
  have hs1 := sinT_le_one t
  have hcs := cosT_sq_add_sinT_sq t
  have p1 : 0 ≤ cosT t * (1 - cosT t) := mul_nonneg hc0 (by linarith)
  have p2 : 0 ≤ sinT t * (1 - sinT t) := mul_nonneg hs0 (by linarith)
  nlinarith [p1, p2]

/-- **Quasiconcavity of `w` on `[0,1]`** (the clipping step of the verifiers):
on any sub-interval the minimum of `w` is attained at an endpoint.
Key identity: `w(b) − w(a) = 2(a − b)(a + b + ab − 1) / ((1+b²)(1+a²))`. -/
theorem wT_ge_min {t0 t1 t : ℝ} (h00 : 0 ≤ t0) (h01 : t0 ≤ t) (h11 : t ≤ t1) :
    min (wT t0) (wT t1) ≤ wT t := by
  have key : ∀ a b : ℝ, wT b - wT a =
      2 * (a - b) * (a + b + a * b - 1) / ((1 + b ^ 2) * (1 + a ^ 2)) := by
    intro a b
    have da : (1 + a ^ 2 : ℝ) ≠ 0 := (one_add_sq_pos a).ne'
    have db : (1 + b ^ 2 : ℝ) ≠ 0 := (one_add_sq_pos b).ne'
    unfold wT cosT sinT
    field_simp
    ring
  rcases le_total (t0 + t + t0 * t) 1 with hcase | hcase
  · -- left branch: `w(t) ≥ w(t0)`
    refine le_trans (min_le_left _ _) ?_
    have h := key t0 t
    have hp : (0 : ℝ) ≤ (t - t0) * (1 - (t0 + t + t0 * t)) :=
      mul_nonneg (by linarith) (by linarith)
    have hnum : (0 : ℝ) ≤ 2 * (t0 - t) * (t0 + t + t0 * t - 1) := by nlinarith [hp]
    have hpos : (0 : ℝ) ≤ wT t - wT t0 := by
      rw [h]
      exact div_nonneg hnum (by positivity)
    linarith
  · -- right branch: `w(t) ≥ w(t1)`
    refine le_trans (min_le_right _ _) ?_
    have h := key t1 t
    have hp : (0 : ℝ) ≤ (t1 - t) * ((t1 + t + t1 * t) - 1) := by
      have ht0 : (0 : ℝ) ≤ t := le_trans h00 h01
      have hmono : t0 + t + t0 * t ≤ t1 + t + t1 * t := by nlinarith
      exact mul_nonneg (by linarith) (by linarith)
    have hnum : (0 : ℝ) ≤ 2 * (t1 - t) * (t1 + t + t1 * t - 1) := by nlinarith [hp]
    have hpos : (0 : ℝ) ≤ wT t - wT t1 := by
      rw [h]
      exact div_nonneg hnum (by positivity)
    linarith

/-- Containment of a parametrised square in the closed container:
`Q ⊆ [0,s]² ⟺ w/2 ≤ cx ≤ s − w/2 ∧ w/2 ≤ cy ≤ s − w/2` (for `t ∈ [0,1]`). -/
theorem set_subset_container_iff {q : PSq} (h0 : 0 ≤ q.t) (h1 : q.t ≤ 1) (s : ℝ) :
    q.set ⊆ Icc (0 : ℝ) s ×ˢ Icc (0 : ℝ) s ↔
      wT q.t / 2 ≤ q.cx ∧ q.cx ≤ s - wT q.t / 2 ∧
      wT q.t / 2 ≤ q.cy ∧ q.cy ≤ s - wT q.t / 2 := by
  have hc0 := cosT_nonneg h0 h1
  have hs0 := sinT_nonneg h0
  constructor
  · intro hsub
    have hmem : ∀ a b : ℝ, 0 ≤ a → a ≤ 1 → 0 ≤ b → b ≤ 1 →
        aff (baseCorner q) (edir q) a b ∈ Icc (0 : ℝ) s ×ˢ Icc (0 : ℝ) s := by
      intro a b ha0 ha1 hb0 hb1
      exact hsub ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩
    have h00 := hmem 0 0 le_rfl zero_le_one le_rfl zero_le_one
    have h10 := hmem 1 0 zero_le_one le_rfl le_rfl zero_le_one
    have h01 := hmem 0 1 le_rfl zero_le_one zero_le_one le_rfl
    have h11 := hmem 1 1 zero_le_one le_rfl zero_le_one le_rfl
    simp only [aff, baseCorner, edir, mem_prod, mem_Icc] at h00 h10 h01 h11
    obtain ⟨⟨hx00, hx00'⟩, hy00, hy00'⟩ := h00
    obtain ⟨⟨hx10, hx10'⟩, hy10, hy10'⟩ := h10
    obtain ⟨⟨hx01, hx01'⟩, hy01, hy01'⟩ := h01
    obtain ⟨⟨hx11, hx11'⟩, hy11, hy11'⟩ := h11
    refine ⟨?_, ?_, ?_, ?_⟩ <;> simp only [wT] <;> linarith
  · rintro ⟨hx0, hx1, hy0, hy1⟩ p hp
    obtain ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩ := hp
    simp only [wT] at hx0 hx1 hy0 hy1
    simp only [aff, baseCorner, edir, mem_prod, mem_Icc]
    have m1 : (0 : ℝ) ≤ a * cosT q.t := mul_nonneg ha0 hc0
    have m2 : (0 : ℝ) ≤ b * sinT q.t := mul_nonneg hb0 hs0
    have m3 : (0 : ℝ) ≤ a * sinT q.t := mul_nonneg ha0 hs0
    have m4 : (0 : ℝ) ≤ b * cosT q.t := mul_nonneg hb0 hc0
    have m5 : (0 : ℝ) ≤ (1 - a) * cosT q.t := mul_nonneg (by linarith) hc0
    have m6 : (0 : ℝ) ≤ (1 - b) * sinT q.t := mul_nonneg (by linarith) hs0
    have m7 : (0 : ℝ) ≤ (1 - a) * sinT q.t := mul_nonneg (by linarith) hs0
    have m8 : (0 : ℝ) ≤ (1 - b) * cosT q.t := mul_nonneg (by linarith) hc0
    refine ⟨⟨?_, ?_⟩, ?_, ?_⟩ <;> nlinarith

/-! ## The parametrisation lemma, packing form (A.PARAM) -/

/-- **[parametrisation]** Every set-level packing is represented by a configuration: each
unit square is `PSq.set` of some `(cx, cy, t)` with `t ∈ [0,1]`.  Was the `parametrize`
axiom of `TopLevel.lean`; DISCHARGED by A64 (this file).  Only the `unit` field of
`IsPacking` is used.  Prose: `docs/proofs/parametrization.md`. -/
theorem parametrize : ∀ {n : ℕ} {s : ℝ} (Q : Fin n → Set RP), IsPacking n s Q →
    ∃ z : Fin n → PSq, (∀ i, (z i).t ∈ Icc (0 : ℝ) 1) ∧ ∀ i, Q i = (z i).set := by
  intro n s Q hQ
  have h : ∀ i, ∃ q : PSq, q.t ∈ Icc (0 : ℝ) 1 ∧ Q i = q.set :=
    fun i => isUnitSquare_exists_psq (hQ.unit i)
  choose z h1 h2 using h
  exact ⟨z, h1, h2⟩

end

end S11
end PackingCert
