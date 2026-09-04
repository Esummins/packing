import PackingCertMathlib.CaseChecker

/-!
# The atlas-value box checker (A86 T2, core Lean — the trivial-reach / extent form)

`docs/specs/atlas_value_certificate_v1.md` §1 (A37 3R/3S) and `docs/proofs/k0_route.md`
§4.6 (A85's drains, `h = s_g − s0`): a box of configurations with a certified lower
bound on the enclosing side.  This checker is the TRIVIAL form, stated in the
composition's own `(cx, cy, t)` coordinates (no θ↔t caveat): a box is 11 rational
intervals in each of `cx, cy, t ∈ [0, 1]`; the claim is a lower bound `L` on the
axis-parallel EXTENT of every configuration of the box — hence on the side of every
container holding it — obtained from witness corner pairs:

    extent_x(z) ≥ corner_x(i₁, k₁)(z) − corner_x(i₂, k₂)(z) ≥ lo₁ − hi₂

with the corner coordinates enclosed by exact rational interval arithmetic
(`cosT` antitone / `sinT` monotone on `[0, 1]`, `MeasureBridge.lean`).  A37's value
`V` is NOT trusted; the checker recomputes its own `L` from the box alone, so A37's
boxes (and A85's ghost drains) are consumed by re-emitting them in this format with
whatever radius makes `L ≥ s0` (the chore report records the achievable radius).
Soundness: `AtlasBridge.lean` (`atlas_extent`, `atlas_kill`, `atlas_dilated_kill`).
-/

namespace PackingCert.Atlas

open PackingCert.CaseI (rabs rmin rmax)

/-- The box of one square: `cx ∈ [x0, x1]`, `cy ∈ [y0, y1]`, `t ∈ [t0, t1] ⊆ [0, 1]`. -/
structure ABox where
  x0 : Rat
  x1 : Rat
  y0 : Rat
  y1 : Rat
  t0 : Rat
  t1 : Rat
deriving Repr, Inhabited

/-- A witness: corner `k1` of square `i1` minus corner `k2` of square `i2`, along `x`
(`axisX = true`) or `y`; the certificate claims `L ≤ lo(corner1) − hi(corner2)`. -/
structure AWitness where
  i1 : Nat
  k1 : Nat
  i2 : Nat
  k2 : Nat
  axisX : Bool
deriving Repr, Inhabited

/-- An atlas-value box certificate (trivial-reach form). -/
structure AtlasCert where
  name : String
  boxes : Array ABox       -- 11 entries
  L : Rat                  -- the certified extent lower bound
  wits : Array AWitness    -- at least one must certify `L`
deriving Repr, Inhabited

/-- `cosT` as a rational function. -/
def cosQ (t : Rat) : Rat := (1 - t * t) / (1 + t * t)

def sinQ (t : Rat) : Rat := 2 * t / (1 + t * t)

/-- Body-frame offsets of corner `k`: `(hx, hy) ∈ {±½}²` (the `RigidKernel` convention:
`0 = (−½,−½)`, `1 = (½,−½)`, `2 = (½,½)`, `3 = (−½,½)`). -/
def hxA (k : Nat) : Rat := if k = 0 || k = 3 then -1 / 2 else 1 / 2

def hyA (k : Nat) : Rat := if k = 0 || k = 1 then -1 / 2 else 1 / 2

/-- Product of two rational intervals `[a0,a1]·[b0,b1]`. -/
def mulI (a0 a1 b0 b1 : Rat) : Rat × Rat :=
  let p1 := a0 * b0
  let p2 := a0 * b1
  let p3 := a1 * b0
  let p4 := a1 * b1
  (rmin (rmin p1 p2) (rmin p3 p4), rmax (rmax p1 p2) (rmax p3 p4))

/-- Enclosure `[lo, hi]` of the `x`-coordinate `cx + hx·cosT t − hy·sinT t` of corner `k`
over the box (`cosT ∈ [cosT t1, cosT t0]`, `sinT ∈ [sinT t0, sinT t1]` for `0 ≤ t0 ≤ t1 ≤ 1`). -/
def cornerXI (b : ABox) (k : Nat) : Rat × Rat :=
  let c := mulI (hxA k) (hxA k) (cosQ b.t1) (cosQ b.t0)
  let s := mulI (hyA k) (hyA k) (sinQ b.t0) (sinQ b.t1)
  (b.x0 + c.1 - s.2, b.x1 + c.2 - s.1)

/-- Enclosure of the `y`-coordinate `cy + hx·sinT t + hy·cosT t`. -/
def cornerYI (b : ABox) (k : Nat) : Rat × Rat :=
  let s := mulI (hxA k) (hxA k) (sinQ b.t0) (sinQ b.t1)
  let c := mulI (hyA k) (hyA k) (cosQ b.t1) (cosQ b.t0)
  (b.y0 + s.1 + c.1, b.y1 + s.2 + c.2)

def boxOK (b : ABox) : Bool :=
  decide (0 ≤ b.t0) && decide (b.t0 ≤ b.t1) && decide (b.t1 ≤ 1) &&
  decide (b.x0 ≤ b.x1) && decide (b.y0 ≤ b.y1)

/-- The lower bound a witness certifies. -/
def witBound (a : AtlasCert) (w : AWitness) : Rat :=
  let b1 := a.boxes.getD w.i1 default
  let b2 := a.boxes.getD w.i2 default
  if w.axisX then (cornerXI b1 w.k1).1 - (cornerXI b2 w.k2).2
  else (cornerYI b1 w.k1).1 - (cornerYI b2 w.k2).2

def witOK (a : AtlasCert) (w : AWitness) : Bool :=
  decide (w.i1 < 11) && decide (w.i2 < 11) && decide (w.k1 < 4) && decide (w.k2 < 4) &&
  decide (a.L ≤ witBound a w)

/-- **The atlas-value checker**: 11 well-formed boxes and a witness pair certifying `L`. -/
def checkAtlas (a : AtlasCert) : Bool :=
  decide (a.boxes.size = 11) && a.boxes.all boxOK && a.wits.any (witOK a)

end PackingCert.Atlas
