import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.Checker

/-!
# The upper-bound bridge lemma, over ℝ²

`lean/PackingCert` proves only the *Bool* statement `checkPacking c = true`.  This file supplies
the missing semantic half: a `checkPackingCCW`-certified `Cert` really does describe a family of
closed unit squares in ℝ², contained in the closed container `[0, side]²` and pairwise disjoint.

Main results

* `PackingCert.disjoint_of_strictlyBelow` — separating axis with *positive margin*:
  if every corner of one square projects strictly below every corner of the other along some
  vector `n`, the two closed squares are `Disjoint`.  No unit-length or edge-direction
  hypothesis on `n` is needed.
* `PackingCert.checkPackingCCW_sound` — the bridge.

A "closed unit square" is `sqSet p0 e` with `rdot e e = 1`: the image of `[0,1]²` under
`(a,b) ↦ p0 + a·e + b·e⊥`.  `aff_sqdist` shows that map preserves Euclidean distance, so the
set really is a congruent copy of `[0,1]²`.  (This parametrisation is used instead of a
`convexHull` precisely because it needs no convexity API.)
-/

namespace PackingCert

noncomputable section

/-! ### The real plane -/

/-- A point of the real plane. -/
abbrev RP := ℝ × ℝ

/-- Euclidean inner product on `ℝ²`. -/
def rdot (a b : RP) : ℝ := a.1 * b.1 + a.2 * b.2

/-- `aff p0 e a b = p0 + a • e + b • e⊥`, where `e⊥ = (-e.2, e.1)`. -/
def aff (p0 e : RP) (a b : ℝ) : RP := (p0.1 + a * e.1 - b * e.2, p0.2 + a * e.2 + b * e.1)

/-- The closed square with base corner `p0` and edge vector `e`. -/
def sqSet (p0 e : RP) : Set RP :=
  {q | ∃ a b : ℝ, 0 ≤ a ∧ a ≤ 1 ∧ 0 ≤ b ∧ b ≤ 1 ∧ q = aff p0 e a b}

/-- The four corners, in cyclic order. -/
def cornerList (p0 e : RP) : List RP := [aff p0 e 0 0, aff p0 e 1 0, aff p0 e 1 1, aff p0 e 0 1]

/-- Squared Euclidean distance. -/
def sqdist (p q : RP) : ℝ := (p.1 - q.1) ^ 2 + (p.2 - q.2) ^ 2

/-- A subset of the plane is a **closed unit square** iff it is the isometric image of `[0,1]²`
under `(a,b) ↦ p0 + a·e + b·e⊥` for a unit vector `e` (see `aff_sqdist`, `sqSet_eq_image`). -/
def IsUnitSquare (S : Set RP) : Prop := ∃ p0 e : RP, rdot e e = 1 ∧ S = sqSet p0 e

/-- The parametrisation is a Euclidean isometry when `e` is a unit vector; hence `sqSet p0 e` is
a congruent copy of the closed unit square `[0,1]²`. -/
theorem aff_sqdist (p0 e : RP) (he : rdot e e = 1) (a b a' b' : ℝ) :
    sqdist (aff p0 e a b) (aff p0 e a' b') = (a - a') ^ 2 + (b - b') ^ 2 := by
  simp only [sqdist, aff, rdot] at *
  linear_combination ((a - a') ^ 2 + (b - b') ^ 2) * he

/-- `sqSet p0 e` is exactly the image of the closed unit square `[0,1]²`. -/
theorem sqSet_eq_image (p0 e : RP) :
    sqSet p0 e = (fun u : ℝ × ℝ => aff p0 e u.1 u.2) '' (Set.Icc (0:ℝ) 1 ×ˢ Set.Icc (0:ℝ) 1) := by
  ext q
  constructor
  · rintro ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩
    exact ⟨(a, b), ⟨⟨ha0, ha1⟩, hb0, hb1⟩, rfl⟩
  · rintro ⟨⟨a, b⟩, ⟨⟨ha0, ha1⟩, hb0, hb1⟩, rfl⟩
    exact ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩

/-! ### Projections of a square: the convex-combination identity -/

/-- The projection along `n` of an arbitrary point of the square is the corresponding convex
combination of the four corner projections. -/
theorem rdot_aff (p0 e n : RP) (a b : ℝ) :
    rdot (aff p0 e a b) n
      = (1 - a) * (1 - b) * rdot (aff p0 e 0 0) n + a * (1 - b) * rdot (aff p0 e 1 0) n
        + a * b * rdot (aff p0 e 1 1) n + (1 - a) * b * rdot (aff p0 e 0 1) n := by
  simp only [rdot, aff]; ring

theorem sqSet_dot_le {p0 e n : RP} {M : ℝ}
    (h0 : rdot (aff p0 e 0 0) n ≤ M) (h1 : rdot (aff p0 e 1 0) n ≤ M)
    (h2 : rdot (aff p0 e 1 1) n ≤ M) (h3 : rdot (aff p0 e 0 1) n ≤ M)
    {q : RP} (hq : q ∈ sqSet p0 e) : rdot q n ≤ M := by
  obtain ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩ := hq
  rw [rdot_aff]
  have l0 : (0:ℝ) ≤ (1 - a) * (1 - b) := mul_nonneg (by linarith) (by linarith)
  have l1 : (0:ℝ) ≤ a * (1 - b) := mul_nonneg (by linarith) (by linarith)
  have l2 : (0:ℝ) ≤ a * b := mul_nonneg (by linarith) (by linarith)
  have l3 : (0:ℝ) ≤ (1 - a) * b := mul_nonneg (by linarith) (by linarith)
  nlinarith [mul_nonneg l0 (sub_nonneg.2 h0), mul_nonneg l1 (sub_nonneg.2 h1),
    mul_nonneg l2 (sub_nonneg.2 h2), mul_nonneg l3 (sub_nonneg.2 h3)]

theorem sqSet_le_dot {p0 e n : RP} {M : ℝ}
    (h0 : M ≤ rdot (aff p0 e 0 0) n) (h1 : M ≤ rdot (aff p0 e 1 0) n)
    (h2 : M ≤ rdot (aff p0 e 1 1) n) (h3 : M ≤ rdot (aff p0 e 0 1) n)
    {q : RP} (hq : q ∈ sqSet p0 e) : M ≤ rdot q n := by
  obtain ⟨a, b, ha0, ha1, hb0, hb1, rfl⟩ := hq
  rw [rdot_aff]
  have l0 : (0:ℝ) ≤ (1 - a) * (1 - b) := mul_nonneg (by linarith) (by linarith)
  have l1 : (0:ℝ) ≤ a * (1 - b) := mul_nonneg (by linarith) (by linarith)
  have l2 : (0:ℝ) ≤ a * b := mul_nonneg (by linarith) (by linarith)
  have l3 : (0:ℝ) ≤ (1 - a) * b := mul_nonneg (by linarith) (by linarith)
  nlinarith [mul_nonneg l0 (sub_nonneg.2 h0), mul_nonneg l1 (sub_nonneg.2 h1),
    mul_nonneg l2 (sub_nonneg.2 h2), mul_nonneg l3 (sub_nonneg.2 h3)]

/-- Coordinate bound from corner coordinate bounds (`n = (1,0)`). -/
theorem sqSet_fst_le {p0 e : RP} {M : ℝ} (h : ∀ z ∈ cornerList p0 e, z.1 ≤ M)
    {q : RP} (hq : q ∈ sqSet p0 e) : q.1 ≤ M := by
  simp only [cornerList, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp,
    forall_eq] at h
  obtain ⟨h0, h1, h2, h3⟩ := h
  have := sqSet_dot_le (n := ((1:ℝ), (0:ℝ))) (M := M)
    (by simpa [rdot] using h0) (by simpa [rdot] using h1)
    (by simpa [rdot] using h2) (by simpa [rdot] using h3) hq
  simpa [rdot] using this

theorem sqSet_le_fst {p0 e : RP} {M : ℝ} (h : ∀ z ∈ cornerList p0 e, M ≤ z.1)
    {q : RP} (hq : q ∈ sqSet p0 e) : M ≤ q.1 := by
  simp only [cornerList, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp,
    forall_eq] at h
  obtain ⟨h0, h1, h2, h3⟩ := h
  have := sqSet_le_dot (n := ((1:ℝ), (0:ℝ))) (M := M)
    (by simpa [rdot] using h0) (by simpa [rdot] using h1)
    (by simpa [rdot] using h2) (by simpa [rdot] using h3) hq
  simpa [rdot] using this

theorem sqSet_snd_le {p0 e : RP} {M : ℝ} (h : ∀ z ∈ cornerList p0 e, z.2 ≤ M)
    {q : RP} (hq : q ∈ sqSet p0 e) : q.2 ≤ M := by
  simp only [cornerList, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp,
    forall_eq] at h
  obtain ⟨h0, h1, h2, h3⟩ := h
  have := sqSet_dot_le (n := ((0:ℝ), (1:ℝ))) (M := M)
    (by simpa [rdot] using h0) (by simpa [rdot] using h1)
    (by simpa [rdot] using h2) (by simpa [rdot] using h3) hq
  simpa [rdot] using this

theorem sqSet_le_snd {p0 e : RP} {M : ℝ} (h : ∀ z ∈ cornerList p0 e, M ≤ z.2)
    {q : RP} (hq : q ∈ sqSet p0 e) : M ≤ q.2 := by
  simp only [cornerList, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp,
    forall_eq] at h
  obtain ⟨h0, h1, h2, h3⟩ := h
  have := sqSet_le_dot (n := ((0:ℝ), (1:ℝ))) (M := M)
    (by simpa [rdot] using h0) (by simpa [rdot] using h1)
    (by simpa [rdot] using h2) (by simpa [rdot] using h3) hq
  simpa [rdot] using this

/-! ### SAT soundness -/

/-- **Separating axis with positive margin.**  If along some vector `n` all four corners of the
first square project strictly below all four corners of the second, then the two *closed*
squares are disjoint.  Any `n` works, so the checker's choice of candidate axes affects only
completeness, never soundness. -/
theorem disjoint_of_strictlyBelow (p0 e q0 f n : RP)
    (h : ∀ c ∈ cornerList p0 e, ∀ d ∈ cornerList q0 f, rdot c n < rdot d n) :
    Disjoint (sqSet p0 e) (sqSet q0 f) := by
  simp only [cornerList, List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp,
    forall_eq] at h
  obtain ⟨⟨g00, g01, g02, g03⟩, ⟨g10, g11, g12, g13⟩, ⟨g20, g21, g22, g23⟩,
    g30, g31, g32, g33⟩ := h
  set M := max (max (rdot (aff p0 e 0 0) n) (rdot (aff p0 e 1 0) n))
               (max (rdot (aff p0 e 1 1) n) (rdot (aff p0 e 0 1) n)) with hMdef
  set M' := min (min (rdot (aff q0 f 0 0) n) (rdot (aff q0 f 1 0) n))
                (min (rdot (aff q0 f 1 1) n) (rdot (aff q0 f 0 1) n)) with hM'def
  have hlt : M < M' := by
    simp only [hMdef, hM'def, max_lt_iff, lt_min_iff]
    and_intros <;> assumption
  rw [Set.disjoint_left]
  intro x hx hx'
  have hxA : rdot x n ≤ M :=
    sqSet_dot_le (le_max_of_le_left (le_max_left _ _)) (le_max_of_le_left (le_max_right _ _))
      (le_max_of_le_right (le_max_left _ _)) (le_max_of_le_right (le_max_right _ _)) hx
  have hxB : M' ≤ rdot x n :=
    sqSet_le_dot (min_le_of_left_le (min_le_left _ _)) (min_le_of_left_le (min_le_right _ _))
      (min_le_of_right_le (min_le_left _ _)) (min_le_of_right_le (min_le_right _ _)) hx'
  linarith

/-! ### From the integer certificate to ℝ² -/

/-- The real point denoted by the integer point `p` over the denominator `D`. -/
def toR (D : Int) (p : Pt) : RP := ((p.x : ℝ) / (D : ℝ), (p.y : ℝ) / (D : ℝ))

/-- An integer vector read as a real vector; used as a separating axis (the SAT lemma is
scale-invariant, so no division by `D` is needed). -/
def vecR (p : Pt) : RP := ((p.x : ℝ), (p.y : ℝ))

theorem rdot_toR (D : Int) (p n : Pt) :
    rdot (toR D p) (vecR n) = ((p.dot n : Int) : ℝ) / (D : ℝ) := by
  simp only [rdot, toR, vecR, Pt.dot]
  push_cast
  ring

/-- The real set denoted by an integer `Square` over the denominator `D`
(counter-clockwise reading: base corner `p0`, edge vector `p1 - p0`). -/
def Square.setR (D : Int) (s : Square) : Set RP := sqSet (toR D s.p0) (toR D (s.p1.sub s.p0))

theorem cornerList_setR {c : Cert} {s : Square} (h : isUnitSquareCCW c s = true) :
    cornerList (toR c.denom s.p0) (toR c.denom (s.p1.sub s.p0))
      = s.corners.map (toR c.denom) := by
  obtain ⟨⟨a0, b0⟩, ⟨a1, b1⟩, ⟨a2, b2⟩, ⟨a3, b3⟩⟩ := s
  simp only [isUnitSquareCCW, Pt.sub, Pt.perp, Pt.add, Pt.dot, Bool.and_eq_true, beq_iff_eq,
    Pt.mk.injEq] at h
  obtain ⟨⟨-, h2x, h2y⟩, h3x, h3y⟩ := h
  subst h2x; subst h2y; subst h3x; subst h3y
  simp only [cornerList, Square.corners, List.map, aff, toR, Pt.sub, List.cons.injEq,
    Prod.mk.injEq, and_true]
  push_cast
  refine ⟨⟨by ring, by ring⟩, ⟨by ring, by ring⟩, ⟨by ring, by ring⟩, by ring, by ring⟩

/-! ### List plumbing -/

theorem mem_allPairs {α : Type} : ∀ {l : List α} {p : α × α}, p ∈ allPairs l → p.1 ∈ l ∧ p.2 ∈ l
  | [], p, h => by simp [allPairs] at h
  | x :: xs, p, h => by
      simp only [allPairs, List.mem_append, List.mem_map] at h
      rcases h with ⟨y, hy, hp⟩ | h
      · subst hp; exact ⟨by simp, by simp [hy]⟩
      · obtain ⟨h1, h2⟩ := mem_allPairs h
        exact ⟨by simp [h1], by simp [h2]⟩

theorem allPairs_pairwise {α : Type} {R : α → α → Prop} :
    ∀ l : List α, (∀ p ∈ allPairs l, R p.1 p.2) → l.Pairwise R
  | [], _ => List.Pairwise.nil
  | x :: xs, h => by
      refine List.Pairwise.cons (fun y hy => ?_)
        (allPairs_pairwise xs (fun p hp => h p (by
          simp only [allPairs, List.mem_append]; exact Or.inr hp)))
      refine h (x, y) ?_
      simp only [allPairs, List.mem_append, List.mem_map]
      exact Or.inl ⟨y, hy, rfl⟩

/-! ### The bridge -/

/-- **Bridge lemma (upper bound).**  If the integer checker accepts `c` (counter-clockwise
variant), then the `c.squares.length` sets `Square.setR c.denom s` are closed unit squares,
contained in the closed container `[0, sideNum/sideDen]²`, and pairwise disjoint. -/
theorem checkPackingCCW_sound (c : Cert) (h : checkPackingCCW c = true) :
    ∃ Q : List (Set RP),
      Q.length = c.squares.length ∧
      (∀ q ∈ Q, IsUnitSquare q) ∧
      (∀ q ∈ Q, q ⊆ Set.Icc (0 : ℝ) ((c.sideNum : ℝ) / (c.sideDen : ℝ)) ×ˢ
                  Set.Icc (0 : ℝ) ((c.sideNum : ℝ) / (c.sideDen : ℝ))) ∧
      Q.Pairwise Disjoint := by
  simp only [checkPackingCCW, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at h
  obtain ⟨⟨⟨hD, hSD⟩, hsq⟩, hpair⟩ := h
  have hDR : (0 : ℝ) < (c.denom : ℝ) := by exact_mod_cast hD
  have hSDR : (0 : ℝ) < (c.sideDen : ℝ) := by exact_mod_cast hSD
  have hDne : (c.denom : ℝ) ≠ 0 := ne_of_gt hDR
  -- shape / inside facts, per square
  have hshape : ∀ s ∈ c.squares, isUnitSquareCCW c s = true := fun s hs => (hsq s hs).1
  have hinside : ∀ s ∈ c.squares, ∀ p ∈ s.corners, ptInside c p = true :=
    fun s hs => (hsq s hs).2
  refine ⟨c.squares.map (Square.setR c.denom), by simp, ?_, ?_, ?_⟩
  · -- closed unit squares
    rintro q hq
    simp only [List.mem_map] at hq
    obtain ⟨s, hs, rfl⟩ := hq
    refine ⟨toR c.denom s.p0, toR c.denom (s.p1.sub s.p0), ?_, rfl⟩
    have hu := hshape s hs
    simp only [isUnitSquareCCW, Bool.and_eq_true, beq_iff_eq] at hu
    have hee : (s.p1.sub s.p0).dot (s.p1.sub s.p0) = c.denom * c.denom := hu.1.1
    have key : ((s.p1.sub s.p0).x : ℝ) * ((s.p1.sub s.p0).x : ℝ)
        + ((s.p1.sub s.p0).y : ℝ) * ((s.p1.sub s.p0).y : ℝ) = (c.denom : ℝ) * (c.denom : ℝ) := by
      have := congrArg (fun z : Int => (z : ℝ)) hee
      simpa [Pt.dot] using this
    show ((s.p1.sub s.p0).x : ℝ) / (c.denom : ℝ) * (((s.p1.sub s.p0).x : ℝ) / (c.denom : ℝ))
        + ((s.p1.sub s.p0).y : ℝ) / (c.denom : ℝ) * (((s.p1.sub s.p0).y : ℝ) / (c.denom : ℝ)) = 1
    rw [div_mul_div_comm, div_mul_div_comm, ← add_div, key]
    exact div_self (mul_ne_zero hDne hDne)
  · -- containment
    rintro q hq
    simp only [List.mem_map] at hq
    obtain ⟨s, hs, rfl⟩ := hq
    have hcl := cornerList_setR (c := c) (s := s) (hshape s hs)
    have hcorner : ∀ z ∈ cornerList (toR c.denom s.p0) (toR c.denom (s.p1.sub s.p0)),
        0 ≤ z.1 ∧ z.1 ≤ (c.sideNum : ℝ) / (c.sideDen : ℝ) ∧
        0 ≤ z.2 ∧ z.2 ≤ (c.sideNum : ℝ) / (c.sideDen : ℝ) := by
      intro z hz
      rw [hcl] at hz
      simp only [List.mem_map] at hz
      obtain ⟨p, hp, rfl⟩ := hz
      have hpi := hinside s hs p hp
      simp only [ptInside, Bool.and_eq_true, decide_eq_true_eq] at hpi
      obtain ⟨⟨⟨hx0, hy0⟩, hx1⟩, hy1⟩ := hpi
      have hx0' : (0:ℝ) < (p.x : ℝ) := by exact_mod_cast hx0
      have hy0' : (0:ℝ) < (p.y : ℝ) := by exact_mod_cast hy0
      have hx1' : (p.x : ℝ) * (c.sideDen : ℝ) < (c.sideNum : ℝ) * (c.denom : ℝ) := by
        exact_mod_cast hx1
      have hy1' : (p.y : ℝ) * (c.sideDen : ℝ) < (c.sideNum : ℝ) * (c.denom : ℝ) := by
        exact_mod_cast hy1
      have hxlt : (p.x : ℝ) / (c.denom : ℝ) ≤ (c.sideNum : ℝ) / (c.sideDen : ℝ) := by
        have hexp : (c.sideNum : ℝ) / (c.sideDen : ℝ) - (p.x : ℝ) / (c.denom : ℝ)
            = ((c.sideNum : ℝ) * (c.denom : ℝ) - (p.x : ℝ) * (c.sideDen : ℝ))
              / ((c.sideDen : ℝ) * (c.denom : ℝ)) := by
          field_simp <;> ring
        have hpos : 0 < ((c.sideNum : ℝ) * (c.denom : ℝ) - (p.x : ℝ) * (c.sideDen : ℝ))
              / ((c.sideDen : ℝ) * (c.denom : ℝ)) := div_pos (by linarith) (mul_pos hSDR hDR)
        rw [← hexp] at hpos; linarith
      have hylt : (p.y : ℝ) / (c.denom : ℝ) ≤ (c.sideNum : ℝ) / (c.sideDen : ℝ) := by
        have hexp : (c.sideNum : ℝ) / (c.sideDen : ℝ) - (p.y : ℝ) / (c.denom : ℝ)
            = ((c.sideNum : ℝ) * (c.denom : ℝ) - (p.y : ℝ) * (c.sideDen : ℝ))
              / ((c.sideDen : ℝ) * (c.denom : ℝ)) := by
          field_simp <;> ring
        have hpos : 0 < ((c.sideNum : ℝ) * (c.denom : ℝ) - (p.y : ℝ) * (c.sideDen : ℝ))
              / ((c.sideDen : ℝ) * (c.denom : ℝ)) := div_pos (by linarith) (mul_pos hSDR hDR)
        rw [← hexp] at hpos; linarith
      exact ⟨le_of_lt (div_pos hx0' hDR), hxlt, le_of_lt (div_pos hy0' hDR), hylt⟩
    intro z hz
    refine ⟨⟨?_, ?_⟩, ?_, ?_⟩
    · exact sqSet_le_fst (fun w hw => (hcorner w hw).1) hz
    · exact sqSet_fst_le (fun w hw => (hcorner w hw).2.1) hz
    · exact sqSet_le_snd (fun w hw => (hcorner w hw).2.2.1) hz
    · exact sqSet_snd_le (fun w hw => (hcorner w hw).2.2.2) hz
  · -- pairwise disjointness
    rw [List.pairwise_map]
    refine allPairs_pairwise _ (fun p hp => ?_)
    obtain ⟨s, t⟩ := p
    obtain ⟨hsmem, htmem⟩ := mem_allPairs hp
    have hsep := hpair (s, t) hp
    have hcls := cornerList_setR (c := c) (s := s) (hshape s hsmem)
    have hclt := cornerList_setR (c := c) (s := t) (hshape t htmem)
    simp only [separated, List.any_eq_true, separatedAlong, Bool.or_eq_true] at hsep
    obtain ⟨n, -, hn⟩ := hsep
    have key : ∀ u v : Square,
        cornerList (toR c.denom u.p0) (toR c.denom (u.p1.sub u.p0)) = u.corners.map (toR c.denom) →
        cornerList (toR c.denom v.p0) (toR c.denom (v.p1.sub v.p0)) = v.corners.map (toR c.denom) →
        strictlyBelow n u.corners v.corners = true →
        Disjoint (Square.setR c.denom u) (Square.setR c.denom v) := by
      intro u v hcu hcv hsb
      refine disjoint_of_strictlyBelow _ _ _ _ (vecR n) ?_
      intro z hz w hw
      rw [hcu] at hz
      rw [hcv] at hw
      simp only [List.mem_map] at hz hw
      obtain ⟨pu, hpu, rfl⟩ := hz
      obtain ⟨pv, hpv, rfl⟩ := hw
      simp only [strictlyBelow, List.all_eq_true, decide_eq_true_eq] at hsb
      have hint : pu.dot n < pv.dot n := hsb pu hpu pv hpv
      have hintR : ((pu.dot n : Int) : ℝ) < ((pv.dot n : Int) : ℝ) := by exact_mod_cast hint
      rw [rdot_toR, rdot_toR]
      have hd := div_pos
        (show (0:ℝ) < ((pv.dot n : Int) : ℝ) - ((pu.dot n : Int) : ℝ) by linarith) hDR
      rw [sub_div] at hd
      linarith
    rcases hn with hn | hn
    · exact key s t hcls hclt hn
    · exact (key t s hclt hcls hn).symm

end

end PackingCert
