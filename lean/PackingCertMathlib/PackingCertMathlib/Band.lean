import PackingCertMathlib.Bridge

/-!
# Two unit squares in a small square: a real-geometry band lemma (A26 family)

`attempts/A26-wall-ledger` states, as Lemma E1 / Theorem A26.1, that a square of side
`B < 1/2 + √2` holds at most one unit square, hence at least 10 of 11 squares of a packing in
`[0, 96/25]²` meet the width-1 boundary band.  That proof uses the *hard* direction of the
separating-axis theorem (an interior-disjoint pair of convex polygons is separated by an
**edge normal** of one of them), which is not available here.

What is formalised instead is the same argument run with an *arbitrary* separating direction —
the form in which the separating-hyperplane theorem delivers it.  The constant degrades from
`1/2 + √2 = 1.9142` to `1 + √2/2 = 1.7071`:

* `PackingCert.two_unit_squares_side_ge` — if two unit squares fit in `[lo, lo+B]²` and some
  direction `u` separates them, then `1 + √2/2 ≤ B`.
* `PackingCert.atMostOne_of_side_lt` — contrapositive.
* `PackingCert.band_96_25` — at `s = 96/25 = 3.84` with band width `27/25 = 1.08`
  (`B = 42/25 = 1.68 < 1.7071`), at most one square of a packing avoids the band.

The separating direction is taken as a hypothesis (`hs1`, `hs2`); supplying it for
interior-disjoint squares is exactly the geometric Hahn–Banach step, and is the one input
still assumed here.
-/

namespace PackingCert

noncomputable section

/-- The `ℓ¹` norm on `ℝ²`.  For a unit vector `e`, `nrm1 e / 2` is the half-width of the
axis-aligned bounding box of a unit square with edge direction `e`. -/
def nrm1 (v : RP) : ℝ := |v.1| + |v.2|

/-- The closed unit square with **centre** `c` and unit edge vector `e`. -/
def csqSet (c e : RP) : Set RP :=
  {q | ∃ a b : ℝ, -(1/2) ≤ a ∧ a ≤ 1/2 ∧ -(1/2) ≤ b ∧ b ≤ 1/2 ∧
       q = (c.1 + a * e.1 - b * e.2, c.2 + a * e.2 + b * e.1)}

/-- The centred square is the corner-based square of `Bridge.lean` with base corner
`c - e/2 - e⊥/2`; in particular it is a closed unit square when `rdot e e = 1`. -/
theorem csqSet_eq_sqSet (c e : RP) :
    csqSet c e = sqSet (c.1 - e.1 / 2 + e.2 / 2, c.2 - e.2 / 2 - e.1 / 2) e := by
  ext q
  constructor
  · rintro ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩
    exact ⟨a + 1/2, b + 1/2, by linarith, by linarith, by linarith, by linarith,
      by simp only [aff, Prod.mk.injEq]; constructor <;> ring⟩
  · rintro ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩
    exact ⟨a - 1/2, b - 1/2, by linarith, by linarith, by linarith, by linarith,
      by simp only [aff, Prod.mk.injEq]; constructor <;> ring⟩

theorem isUnitSquare_csqSet {c e : RP} (he : rdot e e = 1) : IsUnitSquare (csqSet c e) :=
  ⟨_, e, he, csqSet_eq_sqSet c e⟩

/-- A sign for `x`: `σ * x = |x|` with `|σ| ≤ 1`. -/
theorem exists_sign (x : ℝ) : ∃ σ : ℝ, |σ| ≤ 1 ∧ σ * x = |x| := by
  rcases abs_cases x with ⟨h1, _⟩ | ⟨h1, _⟩
  · exact ⟨1, by norm_num, by rw [one_mul, h1]⟩
  · exact ⟨-1, by norm_num, by rw [h1]; ring⟩

/-- The support function of the centred square: the maximum of `rdot · n` is attained. -/
theorem csq_max_dot (c e n : RP) :
    ∃ q ∈ csqSet c e,
      rdot q n = rdot c n + (|rdot e n| + |rdot (-e.2, e.1) n|) / 2 := by
  obtain ⟨σ, hσ1, hσ2⟩ := exists_sign (rdot e n)
  obtain ⟨τ, hτ1, hτ2⟩ := exists_sign (rdot (-e.2, e.1) n)
  obtain ⟨hσa, hσb⟩ := abs_le.1 hσ1
  obtain ⟨hτa, hτb⟩ := abs_le.1 hτ1
  refine ⟨(c.1 + (σ/2) * e.1 - (τ/2) * e.2, c.2 + (σ/2) * e.2 + (τ/2) * e.1),
    ⟨σ/2, τ/2, by linarith, by linarith, by linarith, by linarith, rfl⟩, ?_⟩
  simp only [rdot] at hσ2 hτ2 ⊢
  linear_combination (1/2 : ℝ) * hσ2 + (1/2 : ℝ) * hτ2

/-- The minimum of `rdot · n` over the centred square is attained. -/
theorem csq_min_dot (c e n : RP) :
    ∃ q ∈ csqSet c e,
      rdot q n = rdot c n - (|rdot e n| + |rdot (-e.2, e.1) n|) / 2 := by
  obtain ⟨σ, hσ1, hσ2⟩ := exists_sign (rdot e n)
  obtain ⟨τ, hτ1, hτ2⟩ := exists_sign (rdot (-e.2, e.1) n)
  obtain ⟨hσa, hσb⟩ := abs_le.1 hσ1
  obtain ⟨hτa, hτb⟩ := abs_le.1 hτ1
  refine ⟨(c.1 - (σ/2) * e.1 + (τ/2) * e.2, c.2 - (σ/2) * e.2 - (τ/2) * e.1),
    ⟨-(σ/2), -(τ/2), by linarith, by linarith, by linarith, by linarith,
      by simp only [Prod.mk.injEq]; constructor <;> ring⟩, ?_⟩
  simp only [rdot] at hσ2 hτ2 ⊢
  linear_combination (-(1:ℝ)/2) * hσ2 + (-(1:ℝ)/2) * hτ2

/-- Bounding-box bounds on the centre, from containment in `[lo, lo+B]²`. -/
theorem csq_centre_bounds {c e : RP} {lo B : ℝ}
    (h : csqSet c e ⊆ Set.Icc lo (lo + B) ×ˢ Set.Icc lo (lo + B)) :
    lo + nrm1 e / 2 ≤ c.1 ∧ c.1 + nrm1 e / 2 ≤ lo + B ∧
    lo + nrm1 e / 2 ≤ c.2 ∧ c.2 + nrm1 e / 2 ≤ lo + B := by
  obtain ⟨q1, hq1, hq1e⟩ := csq_max_dot c e (1, 0)
  obtain ⟨q2, hq2, hq2e⟩ := csq_min_dot c e (1, 0)
  obtain ⟨q3, hq3, hq3e⟩ := csq_max_dot c e (0, 1)
  obtain ⟨q4, hq4, hq4e⟩ := csq_min_dot c e (0, 1)
  have b1 : q1.1 ≤ lo + B := (h hq1).1.2
  have b2 : lo ≤ q2.1 := (h hq2).1.1
  have b3 : q3.2 ≤ lo + B := (h hq3).2.2
  have b4 : lo ≤ q4.2 := (h hq4).2.1
  simp only [rdot, nrm1, mul_one, mul_zero, add_zero, zero_add, abs_neg] at hq1e hq2e hq3e hq4e ⊢
  refine ⟨by linarith, by linarith, by linarith, by linarith⟩

/-- `|u·e| + |u·e⊥| ≥ 1` for unit vectors `u`, `e`: twice the support half-width of a unit
square along a unit direction is at least `1`. -/
theorem one_le_support {u e : RP} (hu : rdot u u = 1) (he : rdot e e = 1) :
    1 ≤ |rdot e u| + |rdot (-e.2, e.1) u| := by
  have hsq : (rdot e u) ^ 2 + (rdot (-e.2, e.1) u) ^ 2 = 1 := by
    simp only [rdot] at hu he ⊢
    nlinarith [hu, he]
  have h1 := abs_nonneg (rdot e u)
  have h2 := abs_nonneg (rdot (-e.2, e.1) u)
  nlinarith [sq_abs (rdot e u), sq_abs (rdot (-e.2, e.1) u), hsq, mul_nonneg h1 h2]

theorem one_le_nrm1 {e : RP} (he : rdot e e = 1) : 1 ≤ nrm1 e := by
  simp only [nrm1]
  have h1 := abs_nonneg e.1
  have h2 := abs_nonneg e.2
  simp only [rdot] at he
  nlinarith [sq_abs e.1, sq_abs e.2, mul_nonneg h1 h2]

theorem nrm1_le_sqrt_two {u : RP} (hu : rdot u u = 1) : nrm1 u ≤ Real.sqrt 2 := by
  have hnn : 0 ≤ nrm1 u := by simp only [nrm1]; positivity
  have hsq : nrm1 u ^ 2 ≤ 2 := by
    simp only [nrm1, rdot] at hu ⊢
    nlinarith [sq_abs u.1, sq_abs u.2, abs_nonneg u.1, abs_nonneg u.2,
      sq_nonneg (|u.1| - |u.2|)]
  calc nrm1 u = Real.sqrt (nrm1 u ^ 2) := (Real.sqrt_sq hnn).symm
    _ ≤ Real.sqrt 2 := Real.sqrt_le_sqrt hsq

/-- **Two unit squares in a square of side `B`, separated by some direction `u`, force
`B ≥ 1 + √2/2`.**  (The sharp constant is `2`; A26's edge-normal argument gives `1/2 + √2`.
This proof uses only an arbitrary separating direction.) -/
theorem two_unit_squares_side_ge {lo B t : ℝ} {c1 e1 c2 e2 u : RP}
    (he1 : rdot e1 e1 = 1) (he2 : rdot e2 e2 = 1) (hu : rdot u u = 1)
    (h1 : csqSet c1 e1 ⊆ Set.Icc lo (lo + B) ×ˢ Set.Icc lo (lo + B))
    (h2 : csqSet c2 e2 ⊆ Set.Icc lo (lo + B) ×ˢ Set.Icc lo (lo + B))
    (hs1 : ∀ x ∈ csqSet c1 e1, rdot x u ≤ t)
    (hs2 : ∀ y ∈ csqSet c2 e2, t ≤ rdot y u) :
    1 + Real.sqrt 2 / 2 ≤ B := by
  obtain ⟨b1a, b1b, b1c, b1d⟩ := csq_centre_bounds h1
  obtain ⟨b2a, b2b, b2c, b2d⟩ := csq_centre_bounds h2
  set D := B - nrm1 e1 / 2 - nrm1 e2 / 2 with hD
  have hdx : |c2.1 - c1.1| ≤ D := abs_le.2 ⟨by linarith, by linarith⟩
  have hdy : |c2.2 - c1.2| ≤ D := abs_le.2 ⟨by linarith, by linarith⟩
  have hDnn : 0 ≤ D := le_trans (abs_nonneg _) hdx
  -- the separating direction pushes the centres apart
  obtain ⟨q1, hq1, hq1e⟩ := csq_max_dot c1 e1 u
  obtain ⟨q2, hq2, hq2e⟩ := csq_min_dot c2 e2 u
  have l1 := hs1 q1 hq1
  have l2 := hs2 q2 hq2
  rw [hq1e] at l1
  rw [hq2e] at l2
  have hP1 := one_le_support hu he1
  have hP2 := one_le_support hu he2
  have hcentre : 1 ≤ rdot c2 u - rdot c1 u := by linarith
  -- ... but it is bounded by `nrm1 u * D`
  have hux : (c2.1 - c1.1) * u.1 ≤ D * |u.1| :=
    calc (c2.1 - c1.1) * u.1 ≤ |(c2.1 - c1.1) * u.1| := le_abs_self _
      _ = |c2.1 - c1.1| * |u.1| := abs_mul _ _
      _ ≤ D * |u.1| := mul_le_mul_of_nonneg_right hdx (abs_nonneg _)
  have huy : (c2.2 - c1.2) * u.2 ≤ D * |u.2| :=
    calc (c2.2 - c1.2) * u.2 ≤ |(c2.2 - c1.2) * u.2| := le_abs_self _
      _ = |c2.2 - c1.2| * |u.2| := abs_mul _ _
      _ ≤ D * |u.2| := mul_le_mul_of_nonneg_right hdy (abs_nonneg _)
  have hbound : rdot c2 u - rdot c1 u ≤ D * nrm1 u := by
    simp only [rdot, nrm1]
    have hr1 : c2.1 * u.1 + c2.2 * u.2 - (c1.1 * u.1 + c1.2 * u.2)
        = (c2.1 - c1.1) * u.1 + (c2.2 - c1.2) * u.2 := by ring
    have hr2 : D * (|u.1| + |u.2|) = D * |u.1| + D * |u.2| := by ring
    rw [hr1, hr2]
    linarith
  have hkey : 1 ≤ D * nrm1 u := le_trans hcentre hbound
  have hnu := nrm1_le_sqrt_two hu
  have hsnn : (0:ℝ) ≤ Real.sqrt 2 := Real.sqrt_nonneg 2
  have hDs : 1 ≤ D * Real.sqrt 2 := le_trans hkey (mul_le_mul_of_nonneg_left hnu hDnn)
  have hstep : Real.sqrt 2 * 1 ≤ Real.sqrt 2 * (D * Real.sqrt 2) :=
    mul_le_mul_of_nonneg_left hDs hsnn
  have hmul : Real.sqrt 2 * Real.sqrt 2 = 2 := Real.mul_self_sqrt (by norm_num)
  have hkey2 : Real.sqrt 2 * (D * Real.sqrt 2) = 2 * D := by linear_combination D * hmul
  rw [mul_one, hkey2] at hstep
  have hn1 := one_le_nrm1 he1
  have hn2 := one_le_nrm1 he2
  linarith

/-- Contrapositive: a square of side `B < 1 + √2/2` cannot hold two unit squares that some
direction separates. -/
theorem atMostOne_of_side_lt {lo B t : ℝ} {c1 e1 c2 e2 u : RP}
    (hB : B < 1 + Real.sqrt 2 / 2)
    (he1 : rdot e1 e1 = 1) (he2 : rdot e2 e2 = 1) (hu : rdot u u = 1)
    (h1 : csqSet c1 e1 ⊆ Set.Icc lo (lo + B) ×ˢ Set.Icc lo (lo + B))
    (h2 : csqSet c2 e2 ⊆ Set.Icc lo (lo + B) ×ˢ Set.Icc lo (lo + B))
    (hs1 : ∀ x ∈ csqSet c1 e1, rdot x u ≤ t)
    (hs2 : ∀ y ∈ csqSet c2 e2, t ≤ rdot y u) : False :=
  absurd (two_unit_squares_side_ge he1 he2 hu h1 h2 hs1 hs2) (not_le.2 hB)

/-- **Band lemma at `s = 96/25 = 3.84`.**  With band width `w = 27/25 = 1.08` the inner square
is `[27/25, 69/25]²`, of side `B = 42/25 = 1.68 < 1 + √2/2`, so at most one square of a packing
in `[0, 96/25]²` avoids the width-`27/25` boundary band.  (A26's Theorem A26.1 gets `w = 1`;
the gap is the edge-normal refinement of the separating axis.) -/
theorem band_96_25 {t : ℝ} {c1 e1 c2 e2 u : RP}
    (he1 : rdot e1 e1 = 1) (he2 : rdot e2 e2 = 1) (hu : rdot u u = 1)
    (h1 : csqSet c1 e1 ⊆ Set.Icc (27/25 : ℝ) (69/25) ×ˢ Set.Icc (27/25 : ℝ) (69/25))
    (h2 : csqSet c2 e2 ⊆ Set.Icc (27/25 : ℝ) (69/25) ×ˢ Set.Icc (27/25 : ℝ) (69/25))
    (hs1 : ∀ x ∈ csqSet c1 e1, rdot x u ≤ t)
    (hs2 : ∀ y ∈ csqSet c2 e2, t ≤ rdot y u) : False := by
  have hmul : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hnn : (0:ℝ) ≤ Real.sqrt 2 := Real.sqrt_nonneg 2
  have hsq : (1.41 : ℝ) < Real.sqrt 2 := by nlinarith [hmul, hnn]
  have he : (27/25 : ℝ) + 42/25 = 69/25 := by norm_num
  exact atMostOne_of_side_lt (lo := 27/25) (B := 42/25) (t := t) (by linarith) he1 he2 hu
    (by rw [he]; exact h1) (by rw [he]; exact h2) hs1 hs2

end

end PackingCert
