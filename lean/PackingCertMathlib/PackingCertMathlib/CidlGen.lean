import PackingCertMathlib.CidlPoly

/-!
# The 13 (c-idl) generators, rebuilt from the A22 conventions (A78 T2, CIDL-LEAN)

Core Lean only.  This module is the Lean transcription of the *generator construction*
of `certs/verify_cidl.py` (sections "hard-coded geometry" and "the 13 generators, built
from first principles"): `HALF`, `NHAT`, `frame`, `cornerScaled`, `rowWall`, `rowEdge`,
`ROWSPEC`.  NOTHING here is read from the certificate — the certificate supplies only the
cofactors and the univariate factors `e`, `Delta` (`CidlData.lean`).

A22's exact structure (attainment_ub.md §7.1): squares 0–5 axis-parallel with
`c0 = (½,½)`, `c1 = (3/2,½)`, `c2 = (S−½,½)`, `c3 = (½,3/2)`, `c4 = (½, y4)`,
`c5 = (S−½,S−½)`; squares 6–10 share one angle `θ`, entering through the Weierstrass
substitution `t = tan(θ/2)`: `cos θ = (1−t²)/W`, `sin θ = 2t/W` with `W = 1+t²`.  Each
frame is carried as `(cx, cy, cP, sP, w)` with `cos = cP/w`, `sin = sP/w`, and each row
is multiplied by the exact power of `w` it carries, so `1/w` never appears.
-/

namespace PackingCert
namespace Cidl

/-- Corner offsets of the unit square in its own frame (`verify_cidl.py` `HALF`). -/
def HALF : List (Rat × Rat) :=
  [(-1/2, -1/2), (1/2, -1/2), (1/2, 1/2), (-1/2, 1/2)]

/-- Outward edge normals in the square's own frame; edge `k` joins corner `k → k+1`
(`verify_cidl.py` `NHAT`). -/
def NHAT : List (Rat × Rat) := [(0, -1), (1, 0), (0, 1), (-1, 0)]

/-- `t`, variable 0. -/
def T : Poly := pvar 0
/-- `y4`, variable 1. -/
def Y4 : Poly := pvar 1
/-- `S`, variable 12. -/
def SV : Poly := pvar 12
/-- `W = 1 + t²`. -/
def WW : Poly := padd (pconst 1) (pmulRaw T T)
/-- `cos θ · W = 1 − t²`. -/
def CT : Poly := padd (pconst 1) (pscale (-1) (pmulRaw T T))
/-- `sin θ · W = 2t`. -/
def SNT : Poly := pscale 2 T

/-- A square's frame: centre `(cx, cy)` and `cos = cP/w`, `sin = sP/w`. -/
structure Frm where
  cx : Poly
  cy : Poly
  cP : Poly
  sP : Poly
  w : Poly

/-- The frame of square `i` under A22's exact structure. -/
def frame (i : Nat) : Frm :=
  if i = 0 then ⟨pconst (1/2), pconst (1/2), pone, [], pone⟩
  else if i = 1 then ⟨pconst (3/2), pconst (1/2), pone, [], pone⟩
  else if i = 2 then ⟨padd SV (pconst (-1/2)), pconst (1/2), pone, [], pone⟩
  else if i = 3 then ⟨pconst (1/2), pconst (3/2), pone, [], pone⟩
  else if i = 4 then ⟨pconst (1/2), Y4, pone, [], pone⟩
  else if i = 5 then ⟨padd SV (pconst (-1/2)), padd SV (pconst (-1/2)), pone, [], pone⟩
  else ⟨pvar (2 + 2 * (i - 6)), pvar (3 + 2 * (i - 6)), CT, SNT, WW⟩

/-- Corner `k` of square `i`, over the common denominator `w`: the corner is
`(nx, ny)/w` (`verify_cidl.py` `corner_scaled`). -/
def cornerScaled (i k : Nat) : Poly × Poly × Poly :=
  let f := frame i
  let h := HALF.getD k (0, 0)
  let rx := padd (pscale h.1 f.cP) (pscale (-h.2) f.sP)
  let ry := padd (pscale h.1 f.sP) (pscale h.2 f.cP)
  (padd (pmulRaw f.cx f.w) rx, padd (pmulRaw f.cy f.w) ry, f.w)

/-- Wall codes: `0 = x=0`, `1 = y=0`, `2 = x=s`, `3 = y=s`. -/
def rowWall (i k wall : Nat) : Poly :=
  let c := cornerScaled i k
  if wall = 0 then c.1
  else if wall = 1 then c.2.1
  else if wall = 2 then padd (pmulRaw SV c.2.2) (pscale (-1) c.1)
  else padd (pmulRaw SV c.2.2) (pscale (-1) c.2.1)

/-- Edge row: `n·(q − c_j) − ½` with `n = R(θ_j) NHAT[e]`, cleared by `w_i · w_j`
(`verify_cidl.py` `row_edge`). -/
def rowEdge (i k j e : Nat) : Poly :=
  let q := cornerScaled i k
  let qx := q.1
  let qy := q.2.1
  let wi := q.2.2
  let fj := frame j
  let nh := NHAT.getD e (0, 0)
  let nx := padd (pscale nh.1 fj.cP) (pscale (-nh.2) fj.sP)
  let ny := padd (pscale nh.1 fj.sP) (pscale nh.2 fj.cP)
  let dx := padd qx (pscale (-1) (pmulRaw fj.cx wi))
  let dy := padd qy (pscale (-1) (pmulRaw fj.cy wi))
  padd (padd (pmulRaw nx dx) (pmulRaw ny dy)) (pscale (-1/2) (pmulRaw wi fj.w))

/-- The 13 distinct reduced rows, in `verify_cidl.py`'s `ROWSPEC` order:

```
 0  E1c2-8e3     edge (1, 2, 8, 3)
 1  E2c3-8e0     edge (2, 3, 8, 0)
 2  E3c2-7e3     edge (3, 2, 7, 3)
 3  E4c1-7e2     edge (4, 1, 7, 2)
 4  E4c2-6e3     edge (4, 2, 6, 3)
 5  E5c0-9e1     edge (5, 0, 9, 1)
 6  E6c1-9e2     edge (6, 1, 9, 2)
 7  W6c2[y=s]    wall (6, 2, y=s)
 8  E7c1-8e2     edge (7, 1, 8, 2)
 9  E7c2-9e3     edge (7, 2, 9, 3)
10  E8c2-10e3    edge (8, 2, 10, 3)
11  E9c1-10e2    edge (9, 1, 10, 2)
12  W10c1[x=s]   wall (10, 1, x=s)
```
-/
def gens : List Poly :=
  [ pnorm (rowEdge 1 2 8 3),
    pnorm (rowEdge 2 3 8 0),
    pnorm (rowEdge 3 2 7 3),
    pnorm (rowEdge 4 1 7 2),
    pnorm (rowEdge 4 2 6 3),
    pnorm (rowEdge 5 0 9 1),
    pnorm (rowEdge 6 1 9 2),
    pnorm (rowWall 6 2 3),
    pnorm (rowEdge 7 1 8 2),
    pnorm (rowEdge 7 2 9 3),
    pnorm (rowEdge 8 2 10 3),
    pnorm (rowEdge 9 1 10 2),
    pnorm (rowWall 10 1 2) ]

/-- The canonical Trump octic
`x⁸ − 20x⁷ + 178x⁶ − 842x⁵ + 1923x⁴ − 496x³ − 6754x² + 12420x − 6865`,
low-to-high (`TopLevel.trumpOctic`, `certs/octic_root_isolation.json`). -/
def OCTIC : List Int := [-6865, 12420, -6754, -496, 1923, -842, 178, -20, 1]

/-- The gate interval `[3/10, 2/5]` containing `t̂ = tan(θ̂/2)`. -/
def gateA : Rat := 3/10
/-- See `gateA`. -/
def gateB : Rat := 2/5

end Cidl
end PackingCert
