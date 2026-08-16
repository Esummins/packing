import PackingCert.Geometry

/-!
# The packing certificate checker

`checkPacking : Cert → Bool` is a decidable, all-integer check that a list of
squares (given by integer corner coordinates over a common denominator `D`)

1. are genuine squares of side exactly `1` (= `D` in integer units),
2. lie strictly inside the open container `(0, side)²`, `side = sideNum/sideDen`,
3. are pairwise strictly separated by the separating-axis theorem (SAT):
   for every pair there is a candidate axis `n` (one of the 8 edge vectors of the
   two squares) such that every corner of one square projects strictly below every
   corner of the other.

Soundness of the SAT step does **not** depend on which axes are tried: for *any*
vector `n`, "all of A projects strictly below all of B along `n`" implies that
the convex hulls of A and B are disjoint (a linear functional separates them).
Trying edge vectors only matters for *completeness* (a valid packing will be
accepted), which is not part of the proof obligation.

Everything is `Bool`-valued so that `decide` / `native_decide` can evaluate it.
-/

namespace PackingCert

/-- A packing certificate.  All coordinates are integers meaning `coord / denom`.
The container is `[0, sideNum/sideDen]²`. -/
structure Cert where
  denom   : Int
  sideNum : Int
  sideDen : Int
  squares : List Square
deriving Repr

/-- All unordered pairs `(xs[i], xs[j])`, `i < j`. -/
def allPairs {α : Type} : List α → List (α × α)
  | []      => []
  | x :: xs => xs.map (fun y => (x, y)) ++ allPairs xs

/-- `0 < p/D` and `p/D < sideNum/sideDen` for both coordinates.
Requires `denom > 0` and `sideDen > 0` (checked in `checkPacking`). -/
def ptInside (c : Cert) (p : Pt) : Bool :=
  0 < p.x && 0 < p.y &&
  p.x * c.sideDen < c.sideNum * c.denom &&
  p.y * c.sideDen < c.sideNum * c.denom

/-- `s` is a square of side exactly `D`: with `e = p1 − p0` and `n = perp e`,
`e·e = D²`, `p2 = p1 + n`, `p3 = p0 + n` (counter-clockwise), or the same with
`−n` (clockwise). -/
def isUnitSquare (c : Cert) (s : Square) : Bool :=
  let e := s.p1.sub s.p0
  let n := e.perp
  e.dot e == c.denom * c.denom &&
  ((s.p2 == s.p1.add n && s.p3 == s.p0.add n) ||
   (s.p2 == s.p1.sub n && s.p3 == s.p0.sub n))

/-- Every point of `A` projects strictly below every point of `B` along `n`. -/
def strictlyBelow (n : Pt) (A B : List Pt) : Bool :=
  A.all fun a => B.all fun b => a.dot n < b.dot n

/-- Axis `n` strictly separates the point sets `A` and `B`. -/
def separatedAlong (n : Pt) (A B : List Pt) : Bool :=
  strictlyBelow n A B || strictlyBelow n B A

/-- Some edge vector of `s` or `t` strictly separates the corner sets. -/
def separated (s t : Square) : Bool :=
  (s.edges ++ t.edges).any fun n => separatedAlong n s.corners t.corners

/-- The full check. -/
def checkPacking (c : Cert) : Bool :=
  0 < c.denom && 0 < c.sideDen &&
  c.squares.all (fun s => isUnitSquare c s && s.corners.all (ptInside c)) &&
  (allPairs c.squares).all (fun st => separated st.1 st.2)

end PackingCert
