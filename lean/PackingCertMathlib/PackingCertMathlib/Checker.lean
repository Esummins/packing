/-!
# The integer packing checker (verbatim copy of `lean/PackingCert/PackingCert/{Geometry,Checker}.lean`)

Core Lean 4 only, no Mathlib.  Duplicated here because the `PackingCert` project is pinned to
Lean 4.33.0 while this project uses the Mathlib toolchain; keeping a byte-identical copy of the
definitions is what makes the bridge theorem of `Bridge.lean` a statement *about the same checker*.

Added on top of the copy: the counter-clockwise variant `isUnitSquareCCW` / `checkPackingCCW`,
which is `checkPacking` with the orientation disjunction replaced by its first branch.  It implies
`checkPacking` (`checkPackingCCW_le`), and the shipped certificates satisfy it.
-/

namespace PackingCert

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

structure Square where
  p0 : Pt
  p1 : Pt
  p2 : Pt
  p3 : Pt
deriving Repr, DecidableEq

namespace Square

def corners (s : Square) : List Pt := [s.p0, s.p1, s.p2, s.p3]

def edges (s : Square) : List Pt :=
  [s.p1.sub s.p0, s.p2.sub s.p1, s.p3.sub s.p2, s.p0.sub s.p3]

end Square

structure Cert where
  denom   : Int
  sideNum : Int
  sideDen : Int
  squares : List Square
deriving Repr

def allPairs {α : Type} : List α → List (α × α)
  | []      => []
  | x :: xs => xs.map (fun y => (x, y)) ++ allPairs xs

def ptInside (c : Cert) (p : Pt) : Bool :=
  0 < p.x && 0 < p.y &&
  p.x * c.sideDen < c.sideNum * c.denom &&
  p.y * c.sideDen < c.sideNum * c.denom

def isUnitSquare (c : Cert) (s : Square) : Bool :=
  let e := s.p1.sub s.p0
  let n := e.perp
  e.dot e == c.denom * c.denom &&
  ((s.p2 == s.p1.add n && s.p3 == s.p0.add n) ||
   (s.p2 == s.p1.sub n && s.p3 == s.p0.sub n))

/-- Counter-clockwise variant of `isUnitSquare`: only the `+n` branch. -/
def isUnitSquareCCW (c : Cert) (s : Square) : Bool :=
  let e := s.p1.sub s.p0
  let n := e.perp
  e.dot e == c.denom * c.denom && s.p2 == s.p1.add n && s.p3 == s.p0.add n

def strictlyBelow (n : Pt) (A B : List Pt) : Bool :=
  A.all fun a => B.all fun b => a.dot n < b.dot n

def separatedAlong (n : Pt) (A B : List Pt) : Bool :=
  strictlyBelow n A B || strictlyBelow n B A

def separated (s t : Square) : Bool :=
  (s.edges ++ t.edges).any fun n => separatedAlong n s.corners t.corners

def checkPacking (c : Cert) : Bool :=
  0 < c.denom && 0 < c.sideDen &&
  c.squares.all (fun s => isUnitSquare c s && s.corners.all (ptInside c)) &&
  (allPairs c.squares).all (fun st => separated st.1 st.2)

/-- `checkPacking` with the counter-clockwise shape test. -/
def checkPackingCCW (c : Cert) : Bool :=
  0 < c.denom && 0 < c.sideDen &&
  c.squares.all (fun s => isUnitSquareCCW c s && s.corners.all (ptInside c)) &&
  (allPairs c.squares).all (fun st => separated st.1 st.2)

theorem isUnitSquareCCW_imp {c : Cert} {s : Square} (h : isUnitSquareCCW c s = true) :
    isUnitSquare c s = true := by
  simp only [isUnitSquareCCW, Bool.and_eq_true] at h
  simp only [isUnitSquare, Bool.and_eq_true, Bool.or_eq_true]
  exact ⟨h.1.1, Or.inl ⟨h.1.2, h.2⟩⟩

/-- The CCW check is stronger than the check verified in `lean/PackingCert`. -/
theorem checkPackingCCW_imp {c : Cert} (h : checkPackingCCW c = true) : checkPacking c = true := by
  simp only [checkPackingCCW, checkPacking, Bool.and_eq_true, List.all_eq_true] at h ⊢
  obtain ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩ := h
  refine ⟨⟨⟨h1, h2⟩, fun s hs => ?_⟩, h4⟩
  obtain ⟨hu, hc⟩ := h3 s hs
  exact ⟨isUnitSquareCCW_imp hu, hc⟩

end PackingCert
