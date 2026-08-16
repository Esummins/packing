import PackingCert.Checker

/-!
# Hand-made examples (sanity tests for the checker)

`D = 10`.  Container side 3.  Three axis-parallel unit squares and one square
tilted by θ with tan(θ/2) = 1/2, i.e. cos θ = 3/5, sin θ = 4/5, so the edge
vector is `(6, 8)` in integer units (`6² + 8² = 100 = D²`).
-/

namespace PackingCert.Example

open PackingCert

def ex4 : Cert :=
  { denom := 10, sideNum := 3, sideDen := 1
    squares :=
      [ ⟨⟨1, 1⟩,  ⟨11, 1⟩,  ⟨11, 11⟩, ⟨1, 11⟩⟩,      -- [0.1,1.1]²
        ⟨⟨13, 1⟩, ⟨23, 1⟩,  ⟨23, 11⟩, ⟨13, 11⟩⟩,     -- [1.3,2.3]×[0.1,1.1]
        ⟨⟨1, 13⟩, ⟨11, 13⟩, ⟨11, 23⟩, ⟨1, 23⟩⟩,      -- [0.1,1.1]×[1.3,2.3]
        ⟨⟨20, 13⟩, ⟨26, 21⟩, ⟨18, 27⟩, ⟨12, 19⟩⟩ ] } -- tilted, edge (6,8)

theorem ex4_ok : checkPacking ex4 = true := by native_decide

-- The kernel can also do it directly for this small instance.
theorem ex4_ok_decide : checkPacking ex4 = true := by decide

/-- Same but the tilted square is shifted left by 1/10 so that its corner
`(11,19)` touches the edge `x = 11` of the third square: closed squares
intersect, so the check must fail (strict separation impossible). -/
def ex4_touch : Cert :=
  { ex4 with squares :=
      ex4.squares.take 3 ++ [⟨⟨19, 13⟩, ⟨25, 21⟩, ⟨17, 27⟩, ⟨11, 19⟩⟩] }

theorem ex4_touch_fails : checkPacking ex4_touch = false := by native_decide

/-- Not a unit square (edge (6,7)): must fail. -/
def ex_bad_shape : Cert :=
  { ex4 with squares := [⟨⟨20, 13⟩, ⟨26, 20⟩, ⟨19, 26⟩, ⟨13, 19⟩⟩] }

theorem ex_bad_shape_fails : checkPacking ex_bad_shape = false := by native_decide

/-- Corner on the container boundary (x = 0): must fail. -/
def ex_boundary : Cert :=
  { ex4 with squares := [⟨⟨0, 1⟩, ⟨10, 1⟩, ⟨10, 11⟩, ⟨0, 11⟩⟩] }

theorem ex_boundary_fails : checkPacking ex_boundary = false := by native_decide

end PackingCert.Example
