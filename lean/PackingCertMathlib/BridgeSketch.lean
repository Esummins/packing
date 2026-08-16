/-!
# Bridge lemma sketch (NOT BUILT — Mathlib could not be installed on this machine, see
attempts/A06-lean-setup/notes.md).  Intended statements for the upper-bound checker.

The point of the formulation: describe a square as the image of `[0,1]²` under the affine map
`u ↦ p0 + u₁·e + u₂·e⊥` instead of a `convexHull`; then "every point of the square projects
strictly below every point of the other" reduces to a 4-term convex combination of the
corner projections and `nlinarith`/`linarith` finish.
-/
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Tactic

namespace PackingCertBridge

/-- Real point. -/
abbrev P := ℝ × ℝ

def dot (a b : P) : ℝ := a.1 * b.1 + a.2 * b.2
def perp (a : P) : P := (-a.2, a.1)

/-- The closed square with corner `p0`, edge vector `e` (`|e| = 1`), counter-clockwise. -/
def sq (p0 e : P) : Set P :=
  { q | ∃ a b : ℝ, 0 ≤ a ∧ a ≤ 1 ∧ 0 ≤ b ∧ b ≤ 1 ∧
        q = (p0.1 + a * e.1 + b * (perp e).1, p0.2 + a * e.2 + b * (perp e).2) }

def corners (p0 e : P) : Fin 4 → P :=
  ![p0, (p0.1 + e.1, p0.2 + e.2), (p0.1 + e.1 + (perp e).1, p0.2 + e.2 + (perp e).2),
    (p0.1 + (perp e).1, p0.2 + (perp e).2)]

/-- SAT soundness for one pair: if every corner of the first square projects strictly below every
corner of the second along `n`, the closed squares are disjoint.  (Any `n`; no unit-length or
edge-direction hypothesis is needed.) -/
theorem disjoint_of_strictlyBelow (p0 e q0 f n : P)
    (h : ∀ i j, dot (corners p0 e i) n < dot (corners q0 f j) n) :
    Disjoint (sq p0 e) (sq q0 f) := by
  sorry
  /- Proof idea: for x = p0 + a e + b e⊥ ∈ sq p0 e,
       dot x n = (1-a)(1-b)·dot c0 n + a(1-b)·dot c1 n + ab·dot c2 n + (1-a)b·dot c3 n
     (algebraic identity, `ring`), a convex combination, hence dot x n ≤ max_i dot cᵢ n
     < min_j dot dⱼ n ≤ dot y n for y ∈ sq q0 f, so x ≠ y. -/

/-- Containment: corners inside the (convex) container ⇒ square inside. -/
theorem sq_subset_box (p0 e : P) (S : ℝ)
    (h : ∀ i, 0 ≤ (corners p0 e i).1 ∧ (corners p0 e i).1 ≤ S ∧
              0 ≤ (corners p0 e i).2 ∧ (corners p0 e i).2 ≤ S) :
    sq p0 e ⊆ Set.Icc (0:ℝ) S ×ˢ Set.Icc (0:ℝ) S := by
  sorry

/- Then: `checkPacking c = true` (Bool, over Int) ⇒ for each pair the hypothesis of
`disjoint_of_strictlyBelow` holds for the real points `corner / D` (cast the integer inequality
`a·n < b·n` to ℝ and divide by `D² > 0`), and for each square the hypothesis of `sq_subset_box`.
Unfolding `List.all`, `List.any`, `allPairs` on concrete lists is by `simp [checkPacking, ...]`
after `decide`-style evaluation, or by proving general lemmas `List.all_eq_true`, `List.any_eq_true`. -/

end PackingCertBridge
