import Mathlib.Data.Real.Basic
import Mathlib.Analysis.LocallyConvex.Separation
import Mathlib.Tactic

/-!
# SAT sufficiency for two squares (A70, part of depgraph node V.CASE)

The mathematical core of the `core_exempt_frac` test of `verify_case.py`
(spec `docs/specs/case_lp_certificate_v1.md` §3, discharge rule 2): **non-separation
on all four edge-normal axes implies intersection** for a unit square and a
half-side-`a` square in the plane.

Normalised form (`sat_squares`): work in the core's orthonormal frame, where the core
is the axis box `[-a,a]²` and the unit square has centre `d = (d1, d2)` and edge
direction `u = (c, s)` (`c = cos φ ≥ 0`, `φ` the angle between the squares; `s = sin φ`
of either sign; `c² + s² = 1`).  The four overlap conditions

    |d1| ≤ a + g/2,  |d2| ≤ a + g/2,  |⟨d,u⟩| ≤ 1/2 + a·g,  |⟨d,u⊥⟩| ≤ 1/2 + a·g,

with `g = c + |s| = |cos φ| + |sin φ|`, imply `d = μ + b₁u + b₂u⊥` for some
`μ ∈ [-a,a]²`, `|bᵢ| ≤ 1/2` — i.e. the squares share the point `μ` (in core frame).

Proof: `d` lies in the zonotope `P = [-a,a]² ⊕ [-1/2,1/2]u ⊕ [-1/2,1/2]u⊥` (an
octagon).  If not, geometric Hahn–Banach gives a separating direction `n`; but the
support bound `⟨d,n⟩ ≤ h_P(n)` holds for EVERY `n`, because `h_P − ⟨d,·⟩` is linear on
each of the eight cones between consecutive generators `±(1,0), ±(0,1), ±u, ±u⊥`, and
the four hypotheses are exactly its nonnegativity at those eight directions
(`support_bound`, four cone identities with multiplier `(±n_i/2)·(c²+s²−1)`).
Degenerate angles (`s = 0` or `c = 0`) are handled by clamping.
-/

namespace PackingCert
namespace S11

open Set

/-- Clamping to `[-a, a]`: if `|x| ≤ a + h` then the clamp is within `a` of `0` and
within `h` of `x`. -/
theorem clamp_spec {x a h : ℝ} (ha : 0 ≤ a) (hh : 0 ≤ h) (hx : |x| ≤ a + h) :
    |max (-a) (min a x)| ≤ a ∧ |max (-a) (min a x) - x| ≤ h := by
  rw [abs_le] at hx
  rcases le_total x (-a) with h1 | h1
  · rw [min_eq_right (by linarith), max_eq_left h1]
    constructor
    · rw [abs_le]; constructor <;> linarith
    · rw [abs_le]; constructor <;> linarith
  · rcases le_total a x with h2 | h2
    · rw [min_eq_left h2, max_eq_right (by linarith)]
      constructor
      · rw [abs_le]; constructor <;> linarith
      · rw [abs_le]; constructor <;> linarith
    · rw [min_eq_right h2, max_eq_right h1]
      constructor
      · rw [abs_le]; exact ⟨h1, h2⟩
      · simpa using hh

section SupportBound

variable {c s a d1 d2 : ℝ}

/-- The support bound on the upper half-plane of directions (`0 ≤ n2`), `c, s > 0`:
`⟨d, n⟩ ≤ h_P(n)`.  Four cones between consecutive generators; on each, the bound is
a nonnegative combination of two of the hypothesis inequalities. -/
private theorem support_bound_half (hc : 0 < c) (hs : 0 < s)
    (hcs : c ^ 2 + s ^ 2 = 1) (_ha : 0 ≤ a)
    (h1 : |d1| ≤ a + (c + s) / 2) (h2 : |d2| ≤ a + (c + s) / 2)
    (h3 : |c * d1 + s * d2| ≤ 1 / 2 + a * (c + s))
    (h4 : |(-s) * d1 + c * d2| ≤ 1 / 2 + a * (c + s))
    (n1 n2 : ℝ) (hn2 : 0 ≤ n2) :
    d1 * n1 + d2 * n2
      ≤ a * (|n1| + |n2|) + (|c * n1 + s * n2| + |(-s) * n1 + c * n2|) / 2 := by
  obtain ⟨h1l, h1u⟩ := abs_le.mp h1
  obtain ⟨h2l, h2u⟩ := abs_le.mp h2
  obtain ⟨h3l, h3u⟩ := abs_le.mp h3
  obtain ⟨h4l, h4u⟩ := abs_le.mp h4
  rcases le_total (-s * n1 + c * n2) 0 with hw2 | hw2
  · -- cone (f1, u): n1 ≥ 0, w1 ≥ 0, w2 ≤ 0
    have hn1 : 0 ≤ n1 := by nlinarith
    have hw1 : 0 ≤ c * n1 + s * n2 := by positivity
    rw [abs_of_nonneg hn1, abs_of_nonneg hn2, abs_of_nonneg hw1,
      abs_of_nonpos (by linarith : (-s) * n1 + c * n2 ≤ 0)]
    have hp1 : 0 ≤ (s * n1 - c * n2) * ((a + (c + s) / 2) - d1) :=
      mul_nonneg (by nlinarith) (by linarith)
    have hp2 : 0 ≤ n2 * ((1 / 2 + a * (c + s)) - (c * d1 + s * d2)) :=
      mul_nonneg hn2 (by linarith)
    have key : s * ((a * (n1 + n2) + ((c * n1 + s * n2) + -((-s) * n1 + c * n2)) / 2)
          - (d1 * n1 + d2 * n2))
        = (s * n1 - c * n2) * ((a + (c + s) / 2) - d1)
          + n2 * ((1 / 2 + a * (c + s)) - (c * d1 + s * d2)) := by
      linear_combination (n2 / 2) * hcs
    nlinarith [key, hp1, hp2, hs]
  · rcases le_total 0 n1 with hn1 | hn1
    · -- cone (u, f2): n1 ≥ 0, n2 ≥ 0, w1 ≥ 0, w2 ≥ 0
      have hw1 : 0 ≤ c * n1 + s * n2 := by positivity
      rw [abs_of_nonneg hn1, abs_of_nonneg hn2, abs_of_nonneg hw1, abs_of_nonneg hw2]
      have hp1 : 0 ≤ n1 * ((1 / 2 + a * (c + s)) - (c * d1 + s * d2)) :=
        mul_nonneg hn1 (by linarith)
      have hp2 : 0 ≤ (-s * n1 + c * n2) * ((a + (c + s) / 2) - d2) :=
        mul_nonneg hw2 (by linarith)
      have key : c * ((a * (n1 + n2) + ((c * n1 + s * n2) + ((-s) * n1 + c * n2)) / 2)
            - (d1 * n1 + d2 * n2))
          = n1 * ((1 / 2 + a * (c + s)) - (c * d1 + s * d2))
            + (-s * n1 + c * n2) * ((a + (c + s) / 2) - d2) := by
        linear_combination (n1 / 2) * hcs
      nlinarith [key, hp1, hp2, hc]
    · rcases le_total 0 (c * n1 + s * n2) with hw1 | hw1
      · -- cone (f2, u⊥): n1 ≤ 0, n2 ≥ 0, w1 ≥ 0, w2 ≥ 0
        rw [abs_of_nonpos hn1, abs_of_nonneg hn2, abs_of_nonneg hw1, abs_of_nonneg hw2]
        have hp1 : 0 ≤ (c * n1 + s * n2) * ((a + (c + s) / 2) - d2) :=
          mul_nonneg hw1 (by linarith)
        have hp2 : 0 ≤ (-n1) * ((1 / 2 + a * (c + s)) - ((-s) * d1 + c * d2)) :=
          mul_nonneg (by linarith) (by linarith)
        have key : s * ((a * (-n1 + n2) + ((c * n1 + s * n2) + ((-s) * n1 + c * n2)) / 2)
              - (d1 * n1 + d2 * n2))
            = (c * n1 + s * n2) * ((a + (c + s) / 2) - d2)
              + (-n1) * ((1 / 2 + a * (c + s)) - ((-s) * d1 + c * d2)) := by
          linear_combination (-n1 / 2) * hcs
        nlinarith [key, hp1, hp2, hs]
      · -- cone (u⊥, −f1): n1 ≤ 0, n2 ≥ 0, w1 ≤ 0, w2 ≥ 0
        rw [abs_of_nonpos hn1, abs_of_nonneg hn2, abs_of_nonpos hw1, abs_of_nonneg hw2]
        have hp1 : 0 ≤ n2 * ((1 / 2 + a * (c + s)) - ((-s) * d1 + c * d2)) :=
          mul_nonneg hn2 (by linarith)
        have hp2 : 0 ≤ (-(c * n1 + s * n2)) * ((a + (c + s) / 2) + d1) :=
          mul_nonneg (by linarith) (by linarith)
        have key : c * ((a * (-n1 + n2) + (-(c * n1 + s * n2) + ((-s) * n1 + c * n2)) / 2)
              - (d1 * n1 + d2 * n2))
            = n2 * ((1 / 2 + a * (c + s)) - ((-s) * d1 + c * d2))
              + (-(c * n1 + s * n2)) * ((a + (c + s) / 2) + d1) := by
          linear_combination (n2 / 2) * hcs
        nlinarith [key, hp1, hp2, hc]

/-- The support bound for every direction (`c, s > 0`): apply the half-plane bound to
`(d, n)` or `(-d, -n)`. -/
private theorem support_bound (hc : 0 < c) (hs : 0 < s)
    (hcs : c ^ 2 + s ^ 2 = 1) (ha : 0 ≤ a)
    (h1 : |d1| ≤ a + (c + s) / 2) (h2 : |d2| ≤ a + (c + s) / 2)
    (h3 : |c * d1 + s * d2| ≤ 1 / 2 + a * (c + s))
    (h4 : |(-s) * d1 + c * d2| ≤ 1 / 2 + a * (c + s))
    (n1 n2 : ℝ) :
    d1 * n1 + d2 * n2
      ≤ a * (|n1| + |n2|) + (|c * n1 + s * n2| + |(-s) * n1 + c * n2|) / 2 := by
  rcases le_total 0 n2 with hn2 | hn2
  · exact support_bound_half hc hs hcs ha h1 h2 h3 h4 n1 n2 hn2
  · have h1' : |(-d1)| ≤ a + (c + s) / 2 := by rwa [abs_neg]
    have h2' : |(-d2)| ≤ a + (c + s) / 2 := by rwa [abs_neg]
    have h3' : |c * (-d1) + s * (-d2)| ≤ 1 / 2 + a * (c + s) := by
      rw [show c * (-d1) + s * (-d2) = -(c * d1 + s * d2) by ring, abs_neg]; exact h3
    have h4' : |(-s) * (-d1) + c * (-d2)| ≤ 1 / 2 + a * (c + s) := by
      rw [show (-s) * (-d1) + c * (-d2) = -((-s) * d1 + c * d2) by ring, abs_neg]
      exact h4
    have := support_bound_half hc hs hcs ha h1' h2' h3' h4' (-n1) (-n2) (by linarith)
    calc d1 * n1 + d2 * n2 = (-d1) * (-n1) + (-d2) * (-n2) := by ring
      _ ≤ a * (|(-n1)| + |(-n2)|)
          + (|c * (-n1) + s * (-n2)| + |(-s) * (-n1) + c * (-n2)|) / 2 := this
      _ = a * (|n1| + |n2|) + (|c * n1 + s * n2| + |(-s) * n1 + c * n2|) / 2 := by
          rw [abs_neg, abs_neg, show c * (-n1) + s * (-n2) = -(c * n1 + s * n2) by ring,
            show (-s) * (-n1) + c * (-n2) = -((-s) * n1 + c * n2) by ring, abs_neg,
            abs_neg]

end SupportBound

section Octagon

variable {c s a d1 d2 : ℝ}

/-- Membership in the octagon, non-degenerate case (`c, s > 0`): by contradiction via
geometric Hahn–Banach and `support_bound`. -/
private theorem mem_octagon (hc : 0 < c) (hs : 0 < s)
    (hcs : c ^ 2 + s ^ 2 = 1) (ha : 0 ≤ a)
    (h1 : |d1| ≤ a + (c + s) / 2) (h2 : |d2| ≤ a + (c + s) / 2)
    (h3 : |c * d1 + s * d2| ≤ 1 / 2 + a * (c + s))
    (h4 : |(-s) * d1 + c * d2| ≤ 1 / 2 + a * (c + s)) :
    ∃ m1 m2 b1 b2 : ℝ, |m1| ≤ a ∧ |m2| ≤ a ∧ |b1| ≤ 1 / 2 ∧ |b2| ≤ 1 / 2 ∧
      d1 = m1 + b1 * c - b2 * s ∧ d2 = m2 + b1 * s + b2 * c := by
  classical
  by_contra hno
  push Not at hno
  -- the octagon as the image of a compact convex box under a linear map
  set B : Set ((ℝ × ℝ) × ℝ × ℝ) :=
    (Icc (-a) a ×ˢ Icc (-a) a) ×ˢ Icc (-(1 / 2) : ℝ) (1 / 2) ×ˢ
      Icc (-(1 / 2) : ℝ) (1 / 2) with hB
  set T : ((ℝ × ℝ) × ℝ × ℝ) → ℝ × ℝ := fun w =>
    (w.1.1 + w.2.1 * c - w.2.2 * s, w.1.2 + w.2.1 * s + w.2.2 * c) with hT
  have hd : (d1, d2) ∉ T '' B := by
    rintro ⟨⟨⟨m1, m2⟩, b1, b2⟩, hmem, heq⟩
    simp only [hB, mem_prod, mem_Icc] at hmem
    obtain ⟨⟨⟨hm1a, hm1b⟩, hm2a, hm2b⟩, ⟨hb1a, hb1b⟩, hb2a, hb2b⟩ := hmem
    simp only [hT, Prod.mk.injEq] at heq
    exact hno m1 m2 b1 b2 (abs_le.mpr ⟨hm1a, hm1b⟩) (abs_le.mpr ⟨hm2a, hm2b⟩)
      (abs_le.mpr ⟨hb1a, hb1b⟩) (abs_le.mpr ⟨hb2a, hb2b⟩) heq.1.symm heq.2.symm
  have hBconv : Convex ℝ B := by
    rw [hB]
    exact (((convex_Icc _ _).prod (convex_Icc _ _)).prod
      ((convex_Icc _ _).prod (convex_Icc _ _)))
  have hconv : Convex ℝ (T '' B) := by
    rintro z ⟨w, hw, rfl⟩ z' ⟨w', hw', rfl⟩ θ θ' hθ hθ' hθθ
    refine ⟨θ • w + θ' • w', hBconv hw hw' hθ hθ' hθθ, ?_⟩
    obtain ⟨⟨w1, w2⟩, w3, w4⟩ := w
    obtain ⟨⟨v1, v2⟩, v3, v4⟩ := w'
    simp only [hT, Prod.smul_mk, Prod.mk_add_mk, smul_eq_mul, Prod.mk.injEq]
    constructor <;> ring
  have hcomp : IsCompact (T '' B) := by
    refine IsCompact.image ?_ ?_
    · exact ((isCompact_Icc.prod isCompact_Icc).prod (isCompact_Icc.prod isCompact_Icc))
    · simp only [hT]
      fun_prop
  obtain ⟨f, u0, hfP, hfd⟩ :=
    geometric_hahn_banach_closed_point (E := ℝ × ℝ) hconv hcomp.isClosed hd
  set n1 : ℝ := f (1, 0) with hn1
  set n2 : ℝ := f (0, 1) with hn2
  have hfval : ∀ z : ℝ × ℝ, f z = z.1 * n1 + z.2 * n2 := by
    intro z
    have hz : (z.1 • ((1 : ℝ), (0 : ℝ)) + z.2 • ((0 : ℝ), (1 : ℝ))) = z := by
      simp
    calc f z = f (z.1 • ((1 : ℝ), (0 : ℝ)) + z.2 • ((0 : ℝ), (1 : ℝ))) := by rw [hz]
      _ = z.1 * n1 + z.2 * n2 := by
          rw [map_add, map_smul, map_smul, smul_eq_mul, smul_eq_mul, hn1, hn2]
  -- the corner of the octagon in the direction n
  set sg : ℝ → ℝ := fun x => if 0 ≤ x then 1 else -1 with hsg
  have hsg_mul : ∀ x : ℝ, sg x * x = |x| := by
    intro x
    simp only [hsg]
    split
    · next hx => rw [one_mul, abs_of_nonneg hx]
    · next hx => rw [abs_of_neg (lt_of_not_ge hx)]; ring
  have hsg_one : ∀ x : ℝ, sg x = 1 ∨ sg x = -1 := by
    intro x
    simp only [hsg]
    split
    · exact Or.inl rfl
    · exact Or.inr rfl
  set zc : ((ℝ × ℝ) × ℝ × ℝ) :=
    ((a * sg n1, a * sg n2),
      (1 / 2) * sg (c * n1 + s * n2), (1 / 2) * sg ((-s) * n1 + c * n2)) with hzc
  have hzcB : zc ∈ B := by
    simp only [hzc, hB, mem_prod, mem_Icc]
    refine ⟨⟨?_, ?_⟩, ?_, ?_⟩
    · rcases hsg_one n1 with h | h <;> rw [h] <;> constructor <;> linarith
    · rcases hsg_one n2 with h | h <;> rw [h] <;> constructor <;> linarith
    · rcases hsg_one (c * n1 + s * n2) with h | h <;> rw [h] <;> constructor <;>
        norm_num
    · rcases hsg_one ((-s) * n1 + c * n2) with h | h <;> rw [h] <;> constructor <;>
        norm_num
  have hcorner : f (T zc)
      = a * (|n1| + |n2|) + (|c * n1 + s * n2| + |(-s) * n1 + c * n2|) / 2 := by
    rw [hfval]
    simp only [hzc, hT]
    have e1 := hsg_mul n1
    have e2 := hsg_mul n2
    have e3 := hsg_mul (c * n1 + s * n2)
    have e4 := hsg_mul ((-s) * n1 + c * n2)
    nlinarith [e1, e2, e3, e4]
  have hsup := support_bound hc hs hcs ha h1 h2 h3 h4 n1 n2
  have hfd' : f (d1, d2) = d1 * n1 + d2 * n2 := hfval _
  have hlt : f (T zc) < u0 := hfP _ (mem_image_of_mem T hzcB)
  rw [hcorner] at hlt
  rw [hfd'] at hfd
  linarith

/-- **SAT sufficiency for two squares** (the `core_exempt_frac` geometry).  In the
core's orthonormal frame: the core is `[-a,a]²`, the unit square has centre
`(d1, d2)` and edge direction `(c, s)`, `c ≥ 0`, `c² + s² = 1`.  If the four
projection-overlap inequalities hold (with `g = c + |s|`), the squares intersect:
`d = μ + b₁·(c,s) + b₂·(-s,c)` with `μ ∈ [-a,a]²`, `|bᵢ| ≤ 1/2`. -/
theorem sat_squares (hc : 0 ≤ c) (hcs : c ^ 2 + s ^ 2 = 1) (ha : 0 ≤ a)
    (h1 : |d1| ≤ a + (c + |s|) / 2) (h2 : |d2| ≤ a + (c + |s|) / 2)
    (h3 : |c * d1 + s * d2| ≤ 1 / 2 + a * (c + |s|))
    (h4 : |(-s) * d1 + c * d2| ≤ 1 / 2 + a * (c + |s|)) :
    ∃ m1 m2 b1 b2 : ℝ, |m1| ≤ a ∧ |m2| ≤ a ∧ |b1| ≤ 1 / 2 ∧ |b2| ≤ 1 / 2 ∧
      d1 = m1 + b1 * c - b2 * s ∧ d2 = m2 + b1 * s + b2 * c := by
  rcases eq_or_lt_of_le hc with hc0 | hcpos
  · -- c = 0: s = ±1, clamp both coordinates
    have hs2 : s ^ 2 = 1 := by
      rw [← hc0] at hcs
      linear_combination hcs
    have hsabs : |s| ^ 2 = 1 := by rw [sq_abs]; exact hs2
    have hs1 : |s| = 1 := by
      have h0 := abs_nonneg s
      have hfac : (|s| - 1) * (|s| + 1) = 0 := by linear_combination hsabs
      rcases mul_eq_zero.mp hfac with h | h
      · linarith
      · linarith
    rw [← hc0] at h1 h2
    rw [hs1] at h1 h2
    have hd1 : |d1| ≤ a + 1 / 2 := by linarith
    have hd2 : |d2| ≤ a + 1 / 2 := by linarith
    obtain ⟨hm1, hb1⟩ := clamp_spec (h := (1 : ℝ) / 2) ha (by norm_num) hd1
    obtain ⟨hm2, hb2⟩ := clamp_spec (h := (1 : ℝ) / 2) ha (by norm_num) hd2
    refine ⟨max (-a) (min a d1), max (-a) (min a d2),
      s * (d2 - max (-a) (min a d2)), -s * (d1 - max (-a) (min a d1)),
      hm1, hm2, ?_, ?_,
      by linear_combination (-(d1 - max (-a) (min a d1))) * hs2
        + (s * (d2 - max (-a) (min a d2))) * hc0,
      by linear_combination (-(d2 - max (-a) (min a d2))) * hs2
        + (-(s * (d1 - max (-a) (min a d1)))) * hc0⟩
    · rw [abs_mul, hs1, one_mul, abs_sub_comm]
      exact hb2
    · rw [abs_mul, abs_neg, hs1, one_mul, abs_sub_comm]
      exact hb1
  · rcases lt_trichotomy s 0 with hsneg | hs0 | hspos
    · -- s < 0: reflect the second coordinate
      have habs : |s| = -s := abs_of_neg hsneg
      have h2' : |(-d2)| ≤ a + (c + -s) / 2 := by rw [abs_neg, ← habs]; exact h2
      have h3' : |c * d1 + (-s) * (-d2)| ≤ 1 / 2 + a * (c + -s) := by
        rw [show c * d1 + (-s) * (-d2) = c * d1 + s * d2 by ring, ← habs]; exact h3
      have h4' : |(-(-s)) * d1 + c * (-d2)| ≤ 1 / 2 + a * (c + -s) := by
        rw [show (-(-s)) * d1 + c * (-d2) = -((-s) * d1 + c * d2) by ring, abs_neg]
        rw [habs] at h4
        exact h4
      obtain ⟨m1, m2', b1, b2', hm1, hm2, hb1, hb2, he1, he2⟩ :=
        mem_octagon hcpos (by linarith : (0:ℝ) < -s) (by linear_combination hcs) ha
          (by rw [← habs]; exact h1) h2' h3' h4'
      exact ⟨m1, -m2', b1, -b2', hm1, by rwa [abs_neg], hb1, by rwa [abs_neg],
        by linear_combination he1, by linear_combination -he2⟩
    · -- s = 0: c = 1, clamp both coordinates
      have hc2 : c ^ 2 = 1 := by rw [hs0] at hcs; linear_combination hcs
      have hc1 : c = 1 := by nlinarith [hc2, sq_nonneg (c - 1), sq_nonneg (c + 1)]
      rw [hs0, abs_zero] at h1 h2
      rw [hc1] at h1 h2
      have hd1 : |d1| ≤ a + 1 / 2 := by linarith
      have hd2 : |d2| ≤ a + 1 / 2 := by linarith
      obtain ⟨hm1, hb1⟩ := clamp_spec (h := (1 : ℝ) / 2) ha (by norm_num) hd1
      obtain ⟨hm2, hb2⟩ := clamp_spec (h := (1 : ℝ) / 2) ha (by norm_num) hd2
      refine ⟨max (-a) (min a d1), max (-a) (min a d2),
        d1 - max (-a) (min a d1), d2 - max (-a) (min a d2), hm1, hm2, ?_, ?_, ?_, ?_⟩
      · rw [abs_sub_comm]; exact hb1
      · rw [abs_sub_comm]; exact hb2
      · rw [hc1, hs0]; ring
      · rw [hc1, hs0]; ring
    · -- s > 0: the generic octagon
      have habs : |s| = s := abs_of_pos hspos
      rw [habs] at h1 h2 h3 h4
      exact mem_octagon hcpos hspos hcs ha h1 h2 h3 h4

end Octagon

end S11
end PackingCert
