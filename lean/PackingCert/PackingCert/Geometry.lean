/-!
# Integer plane geometry primitives

Everything is over `Int`.  A certificate fixes a common denominator `D > 0`;
an integer point `⟨x, y⟩` denotes the real point `(x/D, y/D)`.  Nothing in this
file depends on `D` — dot products, differences and perpendiculars of scaled
points are just scaled by `D` or `D²`, and all the checks we perform are
homogeneous, so the scaling never matters.

No Mathlib.  Core Lean 4 only.
-/

namespace PackingCert

/-- An integer point / vector in the plane. -/
structure Pt where
  x : Int
  y : Int
deriving Repr, DecidableEq

namespace Pt

@[inline] def add (a b : Pt) : Pt := ⟨a.x + b.x, a.y + b.y⟩
@[inline] def sub (a b : Pt) : Pt := ⟨a.x - b.x, a.y - b.y⟩
@[inline] def dot (a b : Pt) : Int := a.x * b.x + a.y * b.y
/-- Rotation by +90°: `(x, y) ↦ (-y, x)`. -/
@[inline] def perp (a : Pt) : Pt := ⟨-a.y, a.x⟩
@[inline] def neg (a : Pt) : Pt := ⟨-a.x, -a.y⟩

end Pt

/-- A square given by its four corners in cyclic order (p0 → p1 → p2 → p3).
The checker verifies that they really form a square of side `D`. -/
structure Square where
  p0 : Pt
  p1 : Pt
  p2 : Pt
  p3 : Pt
deriving Repr, DecidableEq

namespace Square

def corners (s : Square) : List Pt := [s.p0, s.p1, s.p2, s.p3]

/-- The four edge vectors p1−p0, p2−p1, p3−p2, p0−p3.  Used as candidate
separating axes.  (For a square the edge vectors are already the edge normals
up to rotation, so these four cover all SAT axes of the square.) -/
def edges (s : Square) : List Pt :=
  [s.p1.sub s.p0, s.p2.sub s.p1, s.p3.sub s.p2, s.p0.sub s.p3]

end Square

end PackingCert
