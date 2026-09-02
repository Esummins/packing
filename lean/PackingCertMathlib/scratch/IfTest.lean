import Mathlib.Tactic

example (a b : Int) (h : a ≤ b) : (if a ≤ b then ((1:Int),(2:Int)) else (3,4)).1 = 1 := by
  simp only [if_pos h]

example (a b : Int) (h : a ≤ b) : (if a ≤ b then ((1:Int),(2:Int)) else (3,4)).1 = 1 := by
  rw [if_pos h]

example (a b : Int) (h : a ≤ b) (x y : Int) (hxy : x ≤ y) :
    (if ((if a ≤ b then ((1:Int),(2:Int)) else (3,4)).1 ≤ 5 && x ≤ y) then (0:Int) else 1) = 0 := by
  simp only [if_pos h]
  sorry

example (a b : Int) (h : a ≤ b) : (if a ≤ b then ((1:Int),(2:Int)) else (3,4)).1 = 1 := by
  split_ifs
  rfl
