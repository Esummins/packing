import PackingCertMathlib.CaseChecker

/-!
# Rigidity replay kernel (A79, depgraph nodes E.A22 / E.A36)

Core Lean 4 only, no Mathlib.  The decision cores of the two exact-rational re-checkers of
A70 (`attempts/A70-lean-wave4/code/a22_recheck_exact.py`, `a36_check_exact.py`), ported:

* `rdown`/`rup` — outward rounding to the dyadic grid `2^-330` (A70's `PREC`);
* `IV` — rational intervals, every operation outward-rounded;
* `cosPt`/`sinPt`/`cosIV`/`sinIV` — certified alternating-Taylor brackets of `cos`/`sin`
  at rational points with `|x| ≤ 1` (fixed `2·KTAY` terms), lifted to intervals by
  monotonicity (fallback `[-1, 1]` outside `|x| ≤ 1`);
* `Expr` — a deep embedding of the row language (variables, constants, ring operations,
  `cos`/`sin` OF A VARIABLE), with symbolic differentiation `Expr.D`, interval evaluation
  `evalIV`, and order-2 interval jets `jet` over a local variable list (the structure of
  A36's `J` class; A22's hand-coded gradients are the order-1 part of the same jets);
* the A22 row language (`Row`, `rowExpr`, `rowVars`) and the A36 basis-v3 table
  (`AXES`, `row70`);
* `checkA22` — [G] centre residuals, [K] Krawczyk contraction on `N`, on `box(z0, r0)`
  and for the angle-equality system, [V] validity margins, [E] multiplier identity,
  [B] the 68 Farkas certificates, [F] feasibility of `ẑ` (interval SAT + exact-structure
  witnesses searched in `S`: see `pairOK`/`wallOK`);
* `checkA36` — the [S][N][A][O][Z][G][H][K][E][P][V][L] chain of `a36_check_exact.py`.

Faithfulness deviations (all recorded in `attempts/A79-rigidity-lean/notes/findings.md`):
(i) quantities the Python evaluates AT the rational centre `z0` (`ε₀`, `g_max`, `ε_w`,
row activity) are evaluated here over `box(z0, r0) ∋ ẑ`, since the soundness theorems
speak about `ẑ`, not `z0`; the claim comparisons against the certificates' float
`claims` are therefore not reproduced (the Lean evaluation is its own evidence);
(ii) the Krawczyk row sums `β_i < 1` and the fixed-point property `ψ(x*) ≤ x*` are
checked explicitly (the Python infers them); (iii) the basin boxes use radius `h + r0`.
Soundness (`checkA22 = true ⟹ …`, `checkA36 = true ⟹ …`) is proved in
`RigidSound.lean` / `RigidA22.lean` / `RigidA36.lean`.
-/

namespace PackingCert.Rigid

open PackingCert.CaseI (rabs rmin rmax)

/-! ## Dyadic outward rounding -/

/-- Grid exponent (A70: `PREC = 330`). -/
def PREC : Nat := 330

def GRIDZ : Int := (2 : Int) ^ PREC

def GRIDQ : Rat := (GRIDZ : Rat)

/-- Round DOWN to the dyadic grid `2^-PREC`. -/
def rdown (x : Rat) : Rat := (((x * GRIDQ).floor : Int) : Rat) / GRIDQ

/-- Round UP to the dyadic grid. -/
def rup (x : Rat) : Rat := -(rdown (-x))

/-! ## Intervals -/

/-- A rational interval `[lo, hi]`. -/
structure IV where
  lo : Rat
  hi : Rat
deriving Repr, Inhabited, DecidableEq

namespace IV

/-- Outward-rounding constructor. -/
@[inline] def mkR (lo hi : Rat) : IV := ⟨rdown lo, rup hi⟩

@[inline] def pt (x : Rat) : IV := mkR x x

def zero : IV := ⟨0, 0⟩

def one : IV := ⟨1, 1⟩

@[inline] def add (a b : IV) : IV := mkR (a.lo + b.lo) (a.hi + b.hi)

@[inline] def sub (a b : IV) : IV := mkR (a.lo - b.hi) (a.hi - b.lo)

@[inline] def neg (a : IV) : IV := ⟨-a.hi, -a.lo⟩

@[inline] def mul (a b : IV) : IV :=
  let p1 := a.lo * b.lo
  let p2 := a.lo * b.hi
  let p3 := a.hi * b.lo
  let p4 := a.hi * b.hi
  mkR (rmin (rmin p1 p2) (rmin p3 p4)) (rmax (rmax p1 p2) (rmax p3 p4))

/-- `max(|lo|, |hi|)`. -/
@[inline] def mag (a : IV) : Rat := rmax (rabs a.lo) (rabs a.hi)

instance : Add IV := ⟨add⟩
instance : Sub IV := ⟨sub⟩
instance : Neg IV := ⟨neg⟩
instance : Mul IV := ⟨mul⟩

end IV

/-! ## Certified Taylor brackets of `cos` / `sin` -/

/-- `(S_n, t_n)` with `S_n = ∑_{m<n} (-1)^m x^{2m}/(2m)!` and `t_n = x^{2n}/(2n)!`, given
`xx = x²`. -/
def cosPartial (xx : Rat) : Nat → Rat × Rat
  | 0 => (0, 1)
  | n + 1 =>
    let p := cosPartial xx n
    (p.1 + (if n % 2 = 0 then p.2 else -p.2),
      p.2 * xx / (((2 * n + 1) * (2 * n + 2) : Nat) : Rat))

/-- `(S_n, t_n)` with `S_n = ∑_{m<n} (-1)^m x^{2m+1}/(2m+1)!`, `t_n = x^{2n+1}/(2n+1)!`. -/
def sinPartial (x xx : Rat) : Nat → Rat × Rat
  | 0 => (0, x)
  | n + 1 =>
    let p := sinPartial x xx n
    (p.1 + (if n % 2 = 0 then p.2 else -p.2),
      p.2 * xx / (((2 * n + 2) * (2 * n + 3) : Nat) : Rat))

/-- Number of alternating PAIRS: the bracket is `[S_{2K}, S_{2K+1}]`. -/
def KTAY : Nat := 36

/-- Certified bracket of `cos x` at a rational point (`[-1, 1]` unless `|x| ≤ 1`). -/
def cosPt (x : Rat) : Rat × Rat :=
  if rabs x ≤ 1 then
    let p := cosPartial (x * x) (2 * KTAY)
    (rdown p.1, rup (p.1 + p.2))
  else (-1, 1)

/-- Certified bracket of `sin x` at a rational point `x ≥ 0` (`[-1, 1]` unless `x ≤ 1`). -/
def sinPtNN (x : Rat) : Rat × Rat :=
  if x ≤ 1 then
    let p := sinPartial x (x * x) (2 * KTAY)
    (rdown p.1, rup (p.1 + p.2))
  else (-1, 1)

/-- Certified bracket of `sin x` at a rational point (oddness for `x < 0`). -/
def sinPt (x : Rat) : Rat × Rat :=
  if x < 0 then
    let p := sinPtNN (-x)
    (-p.2, -p.1)
  else sinPtNN x

/-- Enclosure of `cos` over an interval (`cos` even, decreasing in `|x|` on `[-1, 1]`). -/
def cosIV (v : IV) : IV :=
  if rabs v.lo ≤ 1 && rabs v.hi ≤ 1 then
    let a := cosPt v.lo
    let b := cosPt v.hi
    ⟨rmin a.1 b.1, if v.lo ≤ 0 && 0 ≤ v.hi then 1 else rmax a.2 b.2⟩
  else ⟨-1, 1⟩

/-- Enclosure of `sin` over an interval (`sin` increasing on `[-1, 1]`). -/
def sinIV (v : IV) : IV :=
  if rabs v.lo ≤ 1 && rabs v.hi ≤ 1 then ⟨(sinPt v.lo).1, (sinPt v.hi).2⟩
  else ⟨-1, 1⟩

/-! ## Boxes with memoised trigonometry -/

/-- A box (one interval per coordinate) with the `cos`/`sin` enclosures of every
coordinate precomputed. -/
structure Box where
  b : Array IV
  cs : Array (IV × IV)

def Box.ofArray (b : Array IV) : Box := ⟨b, b.map fun v => (cosIV v, sinIV v)⟩

def Box.get (bx : Box) (k : Nat) : IV := bx.b.getD k IV.zero

def Box.cos (bx : Box) (k : Nat) : IV := (bx.cs.getD k (⟨-1, 1⟩, ⟨-1, 1⟩)).1

def Box.sin (bx : Box) (k : Nat) : IV := (bx.cs.getD k (⟨-1, 1⟩, ⟨-1, 1⟩)).2

/-! ## The expression language -/

/-- Expressions over the configuration variables `z_k`: `cosv k` / `sinv k` are
`cos (z_k)` / `sin (z_k)` (the row language only takes trigonometry of angle
variables). -/
inductive Expr
  | var (k : Nat)
  | const (q : Rat)
  | add (a b : Expr)
  | sub (a b : Expr)
  | mul (a b : Expr)
  | neg (a : Expr)
  | cosv (k : Nat)
  | sinv (k : Nat)
deriving Repr, Inhabited

namespace Expr

/-- Symbolic partial derivative with respect to `z_j`. -/
def D (j : Nat) : Expr → Expr
  | var k => if j = k then const 1 else const 0
  | const _ => const 0
  | add a b => add (D j a) (D j b)
  | sub a b => sub (D j a) (D j b)
  | mul a b => add (mul (D j a) b) (mul a (D j b))
  | neg a => neg (D j a)
  | cosv k => if j = k then neg (sinv k) else const 0
  | sinv k => if j = k then cosv k else const 0

end Expr

/-- `k` occurs in the local variable list. -/
def inVs (vs : Array Nat) (k : Nat) : Bool := (List.range vs.size).any fun a => decide (vs.getD a 0 = k)

namespace Expr

/-- Every variable of the expression is listed in `vs`. -/
def usesOnly (vs : Array Nat) : Expr → Bool
  | var k => inVs vs k
  | const _ => true
  | add a b => usesOnly vs a && usesOnly vs b
  | sub a b => usesOnly vs a && usesOnly vs b
  | mul a b => usesOnly vs a && usesOnly vs b
  | neg a => usesOnly vs a
  | cosv k => inVs vs k
  | sinv k => inVs vs k

end Expr

/-- Interval evaluation over a box. -/
def evalIV (bx : Box) : Expr → IV
  | .var k => bx.get k
  | .const q => IV.pt q
  | .add a b => evalIV bx a + evalIV bx b
  | .sub a b => evalIV bx a - evalIV bx b
  | .mul a b => evalIV bx a * evalIV bx b
  | .neg a => -(evalIV bx a)
  | .cosv k => bx.cos k
  | .sinv k => bx.sin k

/-! ## Order-2 interval jets over a local variable list -/

/-- Value, gradient (indexed by position in the local variable list) and Hessian. -/
structure Jet where
  v : IV
  g : Array IV
  h : Array (Array IV)

def mkV (d : Nat) (f : Nat → IV) : Array IV := Array.ofFn (n := d) fun a => f a.val

def mkM (d : Nat) (f : Nat → Nat → IV) : Array (Array IV) :=
  Array.ofFn (n := d) fun a => mkV d (f a.val)

def Jet.gg (J : Jet) (a : Nat) : IV := J.g.getD a IV.zero

def Jet.hh (J : Jet) (a b : Nat) : IV := (J.h.getD a #[]).getD b IV.zero

/-- The order-2 jet of an expression over the box `bx`, with derivatives taken along the
local variable list `vs` (`vs[a]` is the global index of local variable `a`). -/
def jet (bx : Box) (vs : Array Nat) : Expr → Jet
  | .var k =>
    ⟨bx.get k, mkV vs.size (fun a => if vs.getD a 0 = k then IV.one else IV.zero),
      mkM vs.size (fun _ _ => IV.zero)⟩
  | .const q => ⟨IV.pt q, mkV vs.size (fun _ => IV.zero), mkM vs.size (fun _ _ => IV.zero)⟩
  | .add a b =>
    let ja := jet bx vs a
    let jb := jet bx vs b
    ⟨ja.v + jb.v, mkV vs.size (fun i => ja.gg i + jb.gg i),
      mkM vs.size (fun i j => ja.hh i j + jb.hh i j)⟩
  | .sub a b =>
    let ja := jet bx vs a
    let jb := jet bx vs b
    ⟨ja.v - jb.v, mkV vs.size (fun i => ja.gg i - jb.gg i),
      mkM vs.size (fun i j => ja.hh i j - jb.hh i j)⟩
  | .mul a b =>
    let ja := jet bx vs a
    let jb := jet bx vs b
    ⟨ja.v * jb.v, mkV vs.size (fun i => ja.gg i * jb.v + ja.v * jb.gg i),
      mkM vs.size (fun i j =>
        ja.hh i j * jb.v + ja.gg i * jb.gg j + ja.gg j * jb.gg i + ja.v * jb.hh i j)⟩
  | .neg a =>
    let ja := jet bx vs a
    ⟨-ja.v, mkV vs.size (fun i => -(ja.gg i)), mkM vs.size (fun i j => -(ja.hh i j))⟩
  | .cosv k =>
    let c := bx.cos k
    let s := bx.sin k
    ⟨c, mkV vs.size (fun a => if vs.getD a 0 = k then -s else IV.zero),
      mkM vs.size (fun a b => if vs.getD a 0 = k && vs.getD b 0 = k then -c else IV.zero)⟩
  | .sinv k =>
    let c := bx.cos k
    let s := bx.sin k
    ⟨s, mkV vs.size (fun a => if vs.getD a 0 = k then c else IV.zero),
      mkM vs.size (fun a b => if vs.getD a 0 = k && vs.getD b 0 = k then -s else IV.zero)⟩

/-- Position of `j` in `vs` (first occurrence). -/
def findPos (vs : Array Nat) (j : Nat) : Option Nat :=
  (List.range vs.size).find? fun a => decide (vs.getD a 0 = j)

/-! ## The row language (A22 §1, A36 basis v3) -/

/-- Number of coordinates: 11 × `(cx, cy, θ)` + the side `s = z_33`. -/
def NV : Nat := 34

def S_IDX : Nat := 33

/-- A constraint row.  Walls: `w = 0: x=0`, `1: y=0`, `2: x=s`, `3: y=s`.  Corners in the
body frame: `0 = (-½,-½)`, `1 = (½,-½)`, `2 = (½,½)`, `3 = (-½,½)`.  Edge `e` of a
square has outward normal `NHAT e = (0,-1), (1,0), (0,1), (-1,0)`. -/
inductive Row
  | wall (i corner w : Nat)
  | edge (i corner j e : Nat)
  | dist (i j : Nat)
  | angeq (i j : Nat)
deriving Repr, Inhabited, DecidableEq

def hx (k : Nat) : Rat := if k = 0 || k = 3 then -1 / 2 else 1 / 2

def hy (k : Nat) : Rat := if k = 0 || k = 1 then -1 / 2 else 1 / 2

def nhx (e : Nat) : Rat := if e = 1 then 1 else if e = 3 then -1 else 0

def nhy (e : Nat) : Rat := if e = 0 then -1 else if e = 2 then 1 else 0

/-- `x`-coordinate of corner `k` of square `i`: `cx + hx·cos θ − hy·sin θ`. -/
def cornerX (i k : Nat) : Expr :=
  .add (.var (3 * i))
    (.sub (.mul (.cosv (3 * i + 2)) (.const (hx k))) (.mul (.sinv (3 * i + 2)) (.const (hy k))))

/-- `y`-coordinate of corner `k` of square `i`: `cy + hx·sin θ + hy·cos θ`. -/
def cornerY (i k : Nat) : Expr :=
  .add (.var (3 * i + 1))
    (.add (.mul (.sinv (3 * i + 2)) (.const (hx k))) (.mul (.cosv (3 * i + 2)) (.const (hy k))))

/-- Outward unit normal of edge `e` of square `j`, `x`-component. -/
def normX (j e : Nat) : Expr :=
  .sub (.mul (.cosv (3 * j + 2)) (.const (nhx e))) (.mul (.sinv (3 * j + 2)) (.const (nhy e)))

def normY (j e : Nat) : Expr :=
  .add (.mul (.sinv (3 * j + 2)) (.const (nhx e))) (.mul (.cosv (3 * j + 2)) (.const (nhy e)))

/-- Depth of corner `k` of square `i` relative to edge `e` of square `j`:
`n·(q − c_j)`. -/
def depE (i k j e : Nat) : Expr :=
  .add (.mul (normX j e) (.sub (cornerX i k) (.var (3 * j))))
    (.mul (normY j e) (.sub (cornerY i k) (.var (3 * j + 1))))

/-- Tangential coordinate: `−n_y·w_x + n_x·w_y`. -/
def tanE (i k j e : Nat) : Expr :=
  .add (.mul (.neg (normY j e)) (.sub (cornerX i k) (.var (3 * j))))
    (.mul (normX j e) (.sub (cornerY i k) (.var (3 * j + 1))))

/-- The edge row `n·(q − c_j) − ½`. -/
def edgeRow (i k j e : Nat) : Expr := .sub (depE i k j e) (.const (1 / 2))

def rowExpr : Row → Expr
  | .wall i k w =>
    if w = 0 then cornerX i k
    else if w = 1 then cornerY i k
    else if w = 2 then .sub (.var S_IDX) (cornerX i k)
    else .sub (.var S_IDX) (cornerY i k)
  | .edge i k j e => edgeRow i k j e
  | .dist i j =>
    let dx : Expr := .sub (.var (3 * i)) (.var (3 * j))
    let dy : Expr := .sub (.var (3 * i + 1)) (.var (3 * j + 1))
    .sub (.add (.mul dx dx) (.mul dy dy)) (.const 1)
  | .angeq i j => .sub (.var (3 * i + 2)) (.var (3 * j + 2))

def rowVars : Row → Array Nat
  | .wall i _ w =>
    if w = 2 || w = 3 then #[3 * i, 3 * i + 1, 3 * i + 2, S_IDX] else #[3 * i, 3 * i + 1, 3 * i + 2]
  | .edge i _ j _ => #[3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
  | .dist i j => #[3 * i, 3 * i + 1, 3 * j, 3 * j + 1]
  | .angeq i j => #[3 * i + 2, 3 * j + 2]

/-- Dense (length `NV`) interval gradient of a row over a box. -/
def gradDense (bx : Box) (r : Row) : Array IV :=
  let vs := rowVars r
  let J := jet bx vs (rowExpr r)
  mkV NV fun j => match findPos vs j with
    | some a => J.gg a
    | none => IV.zero

/-- Dense `NV × NV` interval Hessian of a row over a box. -/
def hessDense (bx : Box) (r : Row) : Array (Array IV) :=
  let vs := rowVars r
  let J := jet bx vs (rowExpr r)
  mkM NV fun i j => match findPos vs i, findPos vs j with
    | some a, some b => J.hh a b
    | _, _ => IV.zero

/-! ## Certificates -/

/-- One positive-spanning (Farkas) certificate: `σ e_i = Σ μ_k ∇g_k − ν e_s + ρ`. -/
structure Farkas where
  i : Nat
  sigma : Int
  nu : Rat
  mu : Array Rat
deriving Repr, Inhabited

/-- A22's `krawczyk_cert.json` (the fields the checks consume). -/
structure A22Cert where
  z0 : Array Rat
  rN : Rat
  r0 : Rat
  rows : Array Row
  S : Array Nat
  S2 : Array Nat
  Y : Array (Array Rat)
  Y2 : Array (Array Rat)
  lam : Array Rat
  farkas : Array Farkas
  contactEdge : Array Nat
  noncontact : Array (Nat × Nat)
deriving Repr, Inhabited

/-- One A36 basin certificate (`G3_*.json`). -/
structure A36Cert where
  name : String
  h : Rat
  omega : Array Rat
  P : Array Nat
  universal : Bool
  variantAxes : Array Nat
  validRows : Array Nat
  branchRows : Array Nat
deriving Repr, Inhabited

def A22Cert.row (c : A22Cert) (k : Nat) : Row := c.rows.getD k default

def pointBox (z0 : Array Rat) : Box := Box.ofArray (z0.map IV.pt)

def radBox (z0 : Array Rat) (r : Rat) : Box :=
  Box.ofArray (z0.map fun x => IV.mkR (x - r) (x + r))

def rng (n : Nat) : List Nat := List.range n

/-! ## [K] Krawczyk -/

/-- `F(c)` enclosures for the rows `S` at the centre. -/
def Fcent (c : A22Cert) (S : Array Nat) : Array IV :=
  let pb := pointBox c.z0
  S.map fun k => evalIV pb (rowExpr (c.row k))

/-- Interval Jacobian rows over `box(z0, r)`. -/
def Jrows (c : A22Cert) (S : Array Nat) (r : Rat) : Array (Array IV) :=
  let bx := radBox c.z0 r
  S.map fun k => gradDense bx (c.row k)

def Ymat (Y : Array (Array Rat)) (i rr : Nat) : Rat := (Y.getD i #[]).getD rr 0

/-- Row `i` of `I − Y·[J]`. -/
def Mrow (Y : Array (Array Rat)) (J : Array (Array IV)) (i : Nat) : Array IV :=
  mkV NV fun j =>
    (if i = j then IV.one else IV.zero) -
      (rng NV).foldl (fun s rr => s + IV.pt (Ymat Y i rr) * (J.getD rr #[]).getD j IV.zero)
        IV.zero

/-- `(Y F(c))_i`. -/
def YFc (Y : Array (Array Rat)) (Fc : Array IV) (i : Nat) : IV :=
  (rng NV).foldl (fun acc rr => acc + IV.pt (Ymat Y i rr) * Fc.getD rr IV.zero) IV.zero

/-- `K_i = −(Y F(c))_i + Σ_j M_ij·[−r, r]`. -/
def Krow (M : Array IV) (yfc : IV) (dbox : IV) : IV :=
  (rng NV).foldl (fun k j => k + M.getD j IV.zero * dbox) (-yfc)

def betaRow (M : Array IV) : Rat := (rng NV).foldl (fun s j => s + (M.getD j IV.zero).mag) 0

/-- The Krawczyk test for rows `S`, preconditioner `Y`, box `box(z0, r)`: every `K_i`
strictly inside `(−r, r)` AND every row sum `β_i < 1`. -/
def krawczykOK (c : A22Cert) (S : Array Nat) (Y : Array (Array Rat)) (r : Rat) : Bool :=
  let Fc := Fcent c S
  let J := Jrows c S r
  let dbox := IV.mkR (-r) r
  (rng NV).all fun i =>
    let M := Mrow Y J i
    let K := Krow M (YFc Y Fc i) dbox
    decide (-r < K.lo) && decide (K.hi < r) && decide (betaRow M < 1)

/-- Diagnostic: `max_i |K_i| / r` and `max_i β_i`. -/
def krawczykStats (c : A22Cert) (S : Array Nat) (Y : Array (Array Rat)) (r : Rat) :
    Rat × Rat :=
  let Fc := Fcent c S
  let J := Jrows c S r
  let dbox := IV.mkR (-r) r
  (rng NV).foldl (fun (w, b) i =>
    let M := Mrow Y J i
    let K := Krow M (YFc Y Fc i) dbox
    (rmax w (K.mag / r), rmax b (betaRow M))) (0, 0)

/-! ## [G] centre residuals, [E] multiplier identity -/

def centreResidual (c : A22Cert) : Rat :=
  let pb := pointBox c.z0
  c.rows.foldl (fun m r => rmax m (evalIV pb (rowExpr r)).mag) 0

def centreOK (c : A22Cert) (tol : Rat) : Bool := decide (centreResidual c ≤ tol)

def lambdaResidual (c : A22Cert) : Rat :=
  let pb := pointBox c.z0
  let acc := (rng c.S.size).foldl (fun (acc : Array IV) idx =>
    let k := c.S.getD idx 0
    let lk := c.lam.getD idx 0
    let g := gradDense pb (c.row k)
    mkV NV fun j => acc.getD j IV.zero + IV.pt lk * g.getD j IV.zero) (mkV NV fun _ => IV.zero)
  (rng NV).foldl (fun m j =>
    rmax m (acc.getD j IV.zero - (if j = S_IDX then IV.one else IV.zero)).mag) 0

def lambdaOK (c : A22Cert) (tol : Rat) : Bool :=
  decide (lambdaResidual c ≤ tol) && c.lam.all (fun l => decide (0 < l)) &&
    decide (c.lam.size = c.S.size)

/-! ## [V] validity margins -/

/-- Every edge row of `S`: tangential magnitude `< ½` and depth `> −½` over the box. -/
def validityOK (c : A22Cert) (S : Array Nat) (bx : Box) : Bool :=
  S.all fun k => match c.row k with
    | .edge i kc j e =>
      decide ((evalIV bx (tanE i kc j e)).mag < 1 / 2) &&
        decide (-1 / 2 < (evalIV bx (depE i kc j e)).lo)
    | _ => true

def validityMargin (c : A22Cert) (S : Array Nat) (bx : Box) : Rat :=
  S.foldl (fun m k => match c.row k with
    | .edge i kc j e => rmin m (1 / 2 - (evalIV bx (tanE i kc j e)).mag)
    | _ => m) 1

/-! ## [B] Farkas certificates -/

/-- `‖ρ‖₁` for one certificate over the Jacobian rows `J` (of `S` over `N`). -/
def farkasL1 (f : Farkas) (J : Array (Array IV)) : Rat :=
  let acc : Array IV := mkV NV fun j =>
    (rng NV).foldl (fun s rr => s + IV.pt (f.mu.getD rr 0) * (J.getD rr #[]).getD j IV.zero)
      IV.zero
  (rng NV).foldl (fun s j =>
    let target : Rat := (if j = f.i then (f.sigma : Rat) else 0) + (if j = S_IDX then f.nu else 0)
    s + (IV.pt target - acc.getD j IV.zero).mag) 0

def farkasOne (f : Farkas) (J : Array (Array IV)) : Bool :=
  decide (0 ≤ f.nu) && f.mu.all (fun m => decide (0 ≤ m)) && decide (f.mu.size = NV) &&
    decide (f.i < NV) && (decide (f.sigma = 1) || decide (f.sigma = -1)) &&
    decide (farkasL1 f J < 1)

/-- All 68 certificates pass and every `(i, σ)` is present. -/
def farkasOK (c : A22Cert) : Bool :=
  let J := Jrows c c.S c.rN
  c.farkas.all (fun f => farkasOne f J) &&
    (rng NV).all (fun i => [(1 : Int), -1].all fun sg =>
      c.farkas.any fun f => decide (f.i = i) && decide (f.sigma = sg))

def farkasBeta (c : A22Cert) : Rat × Rat :=
  let J := Jrows c c.S c.rN
  c.farkas.foldl (fun (b, n) f => (rmax b (farkasL1 f J), rmax n f.nu)) (0, 0)

/-! ## [F] feasibility of `ẑ` on `box(z0, r0)` -/

def wallInS (c : A22Cert) (i k w : Nat) : Bool :=
  c.S.any fun r => c.row r == Row.wall i k w

def edgeInS (c : A22Cert) (i k j e : Nat) : Bool :=
  c.S.any fun r => c.row r == Row.edge i k j e

/-- The corner sharing the `x`-coordinate with `k` at `θ = 0` (`0↔3`, `1↔2`). -/
def mateX (k : Nat) : Nat := if k = 0 then 3 else if k = 3 then 0 else if k = 1 then 2 else 1

/-- The corner sharing the `y`-coordinate with `k` at `θ = 0` (`0↔1`, `2↔3`). -/
def mateY (k : Nat) : Nat := if k = 0 then 1 else if k = 1 then 0 else if k = 2 then 3 else 2

def mate (w k : Nat) : Nat := if w = 0 || w = 2 then mateX k else mateY k

/-- Wall normal components (`(1,0)` for `x`-walls, `(0,1)` for `y`-walls). -/
def wnx (w : Nat) : Rat := if w = 0 || w = 2 then 1 else 0

def wny (w : Nat) : Rat := if w = 0 || w = 2 then 0 else 1

/-- Two `S` wall rows of square `i` on the same wall at mate corners: forces `sin θ_i = 0`. -/
def uprightW (c : A22Cert) (i : Nat) : Bool :=
  (rng 4).any fun w1 => (rng 4).any fun k1 =>
    wallInS c i k1 w1 && wallInS c i (mate w1 k1) w1

/-- The two corners of edge `e` (body frame). -/
def edgeHasCorner (e k : Nat) : Bool := k = e || k = (e + 1) % 4

/-- Direct equal-angle witness: `S` rows `edge i k j e` and `edge j k2 i e2` with `k` an
endpoint of edge `e2`, `k2` an endpoint of edge `e`, and parallel body normals. -/
def angDirect (c : A22Cert) (i j : Nat) : Bool :=
  (rng 4).any fun e => (rng 4).any fun k => (rng 4).any fun e2 => (rng 4).any fun k2 =>
    edgeInS c i k j e && edgeInS c j k2 i e2 && edgeHasCorner e2 k && edgeHasCorner e k2 &&
      decide (nhx e * nhx e2 + nhy e * nhy e2 ≠ 0)

def angBase (c : A22Cert) : Array (Array Bool) :=
  Array.ofFn (n := 11) fun i => Array.ofFn (n := 11) fun j =>
    decide (i = j) || angDirect c i j || angDirect c j i || (uprightW c i && uprightW c j)

def relGet (R : Array (Array Bool)) (i j : Nat) : Bool := (R.getD i #[]).getD j false

def relStep (R : Array (Array Bool)) : Array (Array Bool) :=
  Array.ofFn (n := 11) fun i => Array.ofFn (n := 11) fun j =>
    relGet R i j || (rng 11).any fun m => relGet R i m && relGet R m j

/-- Transitive closure (4 doublings ≥ 11 nodes). -/
def angRel (c : A22Cert) : Array (Array Bool) := relStep (relStep (relStep (relStep (angBase c))))

/-- Corner `k` of square `p` lies on the outer side of edge `e` of square `o` at `ẑ`:
certified by interval, by membership of the row in `S`, or derived from an `S` row at a
corner `k'` with `h_k − h_{k'} ⊥ NHAT e` and equal angles. -/
def cornerRowOK (c : A22Cert) (R : Array (Array Bool)) (bx0 : Box) (p k o e : Nat) : Bool :=
  decide (0 < (evalIV bx0 (edgeRow p k o e)).lo) || edgeInS c p k o e ||
    (relGet R p o && (rng 4).any fun k' =>
      edgeInS c p k' o e && decide (nhx e * (hx k - hx k') + nhy e * (hy k - hy k') = 0))

/-! ### Exact centre coordinates of upright squares (affine in the side, `a + b·s`) -/

abbrev Aff := Rat × Rat

/-- Per square: the exactly known `x`- and `y`-coordinates of the centre, if any. -/
abbrev Known := Array (Option Aff × Option Aff)

/-- From an `S` wall row of an upright square: `c = −h_k` (wall at `0`) or `s − h_k`. -/
def wallKnown (c : A22Cert) (i wa wb : Nat) (hc : Nat → Rat) : Option Aff :=
  match (rng 4).findSome? (fun k => if wallInS c i k wa then some (-hc k, (0 : Rat)) else none) with
  | some v => some v
  | none => (rng 4).findSome? fun k => if wallInS c i k wb then some (-hc k, (1 : Rat)) else none

def knownInit (c : A22Cert) : Known :=
  Array.ofFn (n := 11) fun i =>
    if uprightW c i.val then (wallKnown c i.val 0 2 hx, wallKnown c i.val 1 3 hy) else (none, none)

def kx (K : Known) (i : Nat) : Option Aff := (K.getD i (none, none)).1

def ky (K : Known) (i : Nat) : Option Aff := (K.getD i (none, none)).2

def setKx (K : Known) (j : Nat) (v : Aff) : Known :=
  Array.ofFn (n := 11) fun t =>
    if t.val = j then (some v, ky K t.val) else K.getD t.val (none, none)

def setKy (K : Known) (j : Nat) (v : Aff) : Known :=
  Array.ofFn (n := 11) fun t =>
    if t.val = j then (kx K t.val, some v) else K.getD t.val (none, none)

/-- Interval-certified sign of `z_b − z_a` over the box. -/
def signIV (bx0 : Box) (a b : Nat) : Option Rat :=
  let d := bx0.get b - bx0.get a
  if 0 < d.lo then some 1 else if d.hi < 0 then some (-1) else none

/-- Propagate one `S` dist row `(i, j)` of two upright squares: equal known `y` ⇒ the `x`
coordinates differ by the certified sign (and symmetrically). -/
def propX (bx0 : Box) (K : Known) (i j : Nat) : Known :=
  match ky K i, ky K j, kx K i, kx K j, signIV bx0 (3 * i) (3 * j) with
  | some yi, some yj, some (a, b), none, some σ => if yi = yj then setKx K j (a + σ, b) else K
  | some yi, some yj, none, some (a, b), some σ => if yi = yj then setKx K i (a - σ, b) else K
  | _, _, _, _, _ => K

def propY (bx0 : Box) (K : Known) (i j : Nat) : Known :=
  match kx K i, kx K j, ky K i, ky K j, signIV bx0 (3 * i + 1) (3 * j + 1) with
  | some xi, some xj, some (a, b), none, some σ => if xi = xj then setKy K j (a + σ, b) else K
  | some xi, some xj, none, some (a, b), some σ => if xi = xj then setKy K i (a - σ, b) else K
  | _, _, _, _, _ => K

def propDist (bx0 : Box) (K : Known) (i j : Nat) : Known := propY bx0 (propX bx0 K i j) i j

def knownStep (c : A22Cert) (bx0 : Box) (K : Known) : Known :=
  c.S.foldl (fun K r => match c.row r with
    | .dist i j => if uprightW c i && uprightW c j then propDist bx0 K i j else K
    | _ => K) K

def knownIter (c : A22Cert) (bx0 : Box) : Nat → Known → Known
  | 0, K => K
  | n + 1, K => knownIter c bx0 n (knownStep c bx0 K)

def knownFix (c : A22Cert) (bx0 : Box) : Known := knownIter c bx0 11 (knownInit c)

def affUnit (u v : Option Aff) : Bool :=
  match u, v with
  | some (a, b), some (a', b') => decide (b = b') && decide (rabs (a - a') = 1)
  | _, _ => false

/-- Two upright squares whose centres differ by exactly `1` along an axis. -/
def pairUprightOK (c : A22Cert) (K : Known) (i j : Nat) : Bool :=
  uprightW c i && uprightW c j && (affUnit (kx K i) (kx K j) || affUnit (ky K i) (ky K j))

def pairOK (c : A22Cert) (R : Array (Array Bool)) (K : Known) (bx0 : Box) (i j : Nat) : Bool :=
  ([(i, j), (j, i)].any fun (o, p) => (rng 4).any fun e =>
    (rng 4).all fun k => cornerRowOK c R bx0 p k o e) || pairUprightOK c K i j

def pairsOK (c : A22Cert) (R : Array (Array Bool)) (K : Known) (bx0 : Box) : Bool :=
  (rng 11).all fun i => (rng 11).all fun j => decide (j ≤ i) || pairOK c R K bx0 i j

/-- Corner `k` of square `i` is on the correct side of wall `w`. -/
def wallOK (c : A22Cert) (bx0 : Box) (i k w : Nat) : Bool :=
  decide (0 < (evalIV bx0 (rowExpr (.wall i k w))).lo) || wallInS c i k w ||
    (uprightW c i && (rng 4).any fun k' =>
      wallInS c i k' w && decide (wnx w * (hx k - hx k') + wny w * (hy k - hy k') = 0))

def wallsOK (c : A22Cert) (bx0 : Box) : Bool :=
  (rng 11).all fun i => (rng 4).all fun k => (rng 4).all fun w => wallOK c bx0 i k w

/-- All angle coordinates of the box lie in `[-1, 1]` (needed by the structure lemmas). -/
def anglesSmall (bx : Box) : Bool :=
  (rng 11).all fun i =>
    decide (rabs (bx.get (3 * i + 2)).lo ≤ 1) && decide (rabs (bx.get (3 * i + 2)).hi ≤ 1)

/-- Diagnostics for [F]: min corner clearance among interval-certified corners. -/
def wallMargin (c : A22Cert) (bx0 : Box) : Rat :=
  (rng 11).foldl (fun m i => (rng 4).foldl (fun m k => (rng 4).foldl (fun m w =>
    if wallInS c i k w then m else rmin m (evalIV bx0 (rowExpr (.wall i k w))).lo) m) m) 1

/-- Every tilt is either exactly `0` (upright witness) or certified nonnegative by the box
(so that `t = tan(θ/2) ∈ [0, 1]`). -/
def tiltOK (c : A22Cert) (bx0 : Box) : Bool :=
  (rng 11).all fun i => uprightW c i || decide (0 ≤ (bx0.get (3 * i + 2)).lo)

def feasibleOK (c : A22Cert) : Bool :=
  let bx0 := radBox c.z0 c.r0
  let R := angRel c
  let K := knownFix c bx0
  anglesSmall bx0 && tiltOK c bx0 && pairsOK c R K bx0 && wallsOK c bx0

/-! ## The A22 checker -/

/-- Structural sanity of the certificate data. -/
def shapeOK (c : A22Cert) : Bool :=
  decide (c.z0.size = NV) && decide (c.S.size = NV) && decide (c.S2.size = NV) &&
    decide (c.Y.size = NV) && c.Y.all (fun r => decide (r.size = NV)) &&
    decide (c.Y2.size = NV) && c.Y2.all (fun r => decide (r.size = NV)) &&
    decide (0 < c.r0) && decide (c.r0 ≤ c.rN) &&
    c.S.all (fun k => decide (k < c.rows.size)) && c.S2.all (fun k => decide (k < c.rows.size)) &&
    c.rows.all (fun r => (rowExpr r).usesOnly (rowVars r)) &&
    c.rows.all (fun r => match r with
      | .wall i k w => decide (i < 11) && decide (k < 4) && decide (w < 4)
      | .edge i k j e => decide (i < 11) && decide (k < 4) && decide (j < 11) && decide (e < 4) &&
          decide (i ≠ j)
      | .dist i j => decide (i < 11) && decide (j < 11) && decide (i ≠ j)
      | .angeq i j => decide (i < 11) && decide (j < 11)) &&
    c.S.all (fun k => match c.row k with
      | .angeq _ _ => false
      | _ => true)

/-- The full A22 chain: [G] [K on N] [K on box(z0,r0)] [K for S2 on N] [V] [E] [B] [F]. -/
def checkA22 (c : A22Cert) : Bool :=
  shapeOK c &&
  centreOK c (1 / 10 ^ 55) &&
  krawczykOK c c.S c.Y c.rN &&
  krawczykOK c c.S c.Y c.r0 &&
  krawczykOK c c.S2 c.Y2 c.rN &&
  validityOK c c.S (radBox c.z0 c.rN) &&
  lambdaOK c (1 / 10 ^ 30) &&
  farkasOK c &&
  feasibleOK c

/-! ## A36: basis v3 and the basin chain -/

/-- `(owner o, edge e, other p, kc, base position)` for the 8 branch axes. -/
def AXES : Array (Nat × Nat × Nat × Nat × Nat) :=
  #[(0, 1, 1, 3, 36), (1, 3, 0, 2, 37), (0, 2, 3, 0, 38), (3, 0, 0, 3, 39),
    (1, 3, 3, 1, 40), (3, 1, 1, 3, 42), (3, 0, 1, 3, 41), (1, 2, 3, 1, 43)]

def AUX0 : Nat := 44
def AUX1 : Nat := 45
def EXTRA0 : Nat := 46
def NEXT3 : Nat := 70
def NEW_V3_A : Nat := 42
def NEW_V3_B : Nat := 43

def otherCorners (kc : Nat) : List Nat := (rng 4).filter fun k => k ≠ kc

/-- Corner → position table of axis `ax`. -/
def axisCornerPos (ax : Nat) : List (Nat × Nat) :=
  let (_, _, _, kc, base) := AXES.getD ax (0, 0, 0, 0, 0)
  (kc, base) :: (List.zip (otherCorners kc) (rng 3)).map fun (k, j) => (k, EXTRA0 + 3 * ax + j)

def axisRows (ax : Nat) : List Nat := ((axisCornerPos ax).map (·.2)).mergeSort (· ≤ ·)

/-- The 70-position row table of basis v3. -/
def row70 (c : A22Cert) (pos : Nat) : Row :=
  if pos < 36 then c.row pos
  else if pos = AUX0 then c.row 36
  else if pos = AUX1 then c.row 37
  else
    let hit := (rng 8).findSome? fun ax =>
      let (o, e, p, _, _) := AXES.getD ax (0, 0, 0, 0, 0)
      ((axisCornerPos ax).find? fun (_, q) => q = pos).map fun (k, _) => Row.edge p k o e
    hit.getD default

def mapPos (k : Nat) : Nat := if k = 36 then AUX0 else if k = 37 then AUX1 else k

def universalRows : List Nat := rng 36 ++ [AUX0, AUX1]

def variantRows (axes : Array Nat) : List Nat :=
  (universalRows ++ axes.toList.flatMap axisRows).mergeSort (· ≤ ·)

def KILLED_AXES : List (Nat × Nat × Nat) :=
  [(0, 0, 1), (0, 2, 1), (0, 3, 1), (1, 0, 0), (1, 1, 0), (1, 2, 0),
   (0, 0, 3), (0, 1, 3), (0, 3, 3), (3, 1, 0), (3, 2, 0), (3, 3, 0),
   (1, 0, 3), (1, 1, 3), (3, 2, 1), (3, 3, 1)]

/-- Positions with nonzero `ω`. -/
def loaded (a : A36Cert) : List Nat := (rng NEXT3).filter fun k => a.omega.getD k 0 ≠ 0

/-- `ε₀ = Σ |ω_k| · |g_k|` over the box (Python: at the centre). -/
def eps0 (c : A22Cert) (a : A36Cert) (bx0 : Box) : Rat :=
  (loaded a).foldl (fun s k => s + rabs (a.omega.getD k 0) * (evalIV bx0 (rowExpr (row70 c k))).mag) 0

def gmax (c : A22Cert) (a : A36Cert) (bx0 : Box) : Rat :=
  a.P.foldl (fun m k => rmax m (evalIV bx0 (rowExpr (row70 c k))).mag) 0

/-- `Σ_k ω_k ∇g_k` (dense) over the box. -/
def omegaGrad (c : A22Cert) (a : A36Cert) (bx0 : Box) : Array IV :=
  (loaded a).foldl (fun (acc : Array IV) k =>
    let g := gradDense bx0 (row70 c k)
    mkV NV fun j => acc.getD j IV.zero + IV.pt (a.omega.getD k 0) * g.getD j IV.zero)
    (mkV NV fun _ => IV.zero)

/-- `ε_w = ‖Σ ω_k ∇g_k − e_s‖₁`. -/
def epsW (c : A22Cert) (a : A36Cert) (bx0 : Box) : Rat :=
  let acc := omegaGrad c a bx0
  (rng NV).foldl (fun s j =>
    s + (acc.getD j IV.zero - (if j = S_IDX then IV.one else IV.zero)).mag) 0

/-- `Σ_k ω_k ∇²g_k` (dense) over the box. -/
def omegaHess (c : A22Cert) (a : A36Cert) (bx : Box) : Array (Array IV) :=
  (loaded a).foldl (fun (acc : Array (Array IV)) k =>
    let H := hessDense bx (row70 c k)
    mkM NV fun i j =>
      (acc.getD i #[]).getD j IV.zero + IV.pt (a.omega.getD k 0) * (H.getD i #[]).getD j IV.zero)
    (mkM NV fun _ _ => IV.zero)

/-- `H̄ = ½ Σ_ij |Σ_k ω_k ∂²g_k|`. -/
def hbar (c : A22Cert) (a : A36Cert) (bx : Box) : Rat :=
  let H := omegaHess c a bx
  ((rng NV).foldl (fun s i => (rng NV).foldl (fun s j =>
    s + ((H.getD i #[]).getD j IV.zero).mag) s) 0) / 2

/-- Interval Jacobian rows of the pin set over the box. -/
def pinJ (c : A22Cert) (a : A36Cert) (bx : Box) : Array (Array IV) :=
  a.P.map fun k => gradDense bx (row70 c k)

/-- `β = max_i Σ_j |(I − Y J)_ij|`. -/
def betaA36 (c : A22Cert) (a : A36Cert) (bx : Box) : Rat :=
  let J := pinJ c a bx
  (rng NV).foldl (fun b i => rmax b (betaRow (Mrow c.Y J i))) 0

def kappa (c : A22Cert) : Rat :=
  (rng NV).foldl (fun m i => rmax m ((rng NV).foldl (fun s r => s + rabs (Ymat c.Y i r)) 0)) 0

def cvec (c : A22Cert) (r : Nat) : Rat :=
  (rng NV).foldl (fun m i => rmax m (rabs (Ymat c.Y i r))) 0

/-- `κ_eff = max_r c_r / ω_{P_r}` (all pin weights must be positive). -/
def kappaEff (c : A22Cert) (a : A36Cert) : Rat :=
  (rng NV).foldl (fun m r => rmax m (cvec c r / a.omega.getD (a.P.getD r 0) 0)) 0

def pinsPositive (a : A36Cert) : Bool :=
  decide (a.P.size = NV) && a.P.all fun k => decide (0 < a.omega.getD k 0)

/-- `ψ(x) = (κ_eff (ε₀ + ε_w x + H̄ x²) + κ g_max) / (1 − β)`. -/
def psi (keff e0 ew hb kap gm beta x : Rat) : Rat :=
  (keff * (e0 + ew * x + hb * x * x) + kap * gm) / (1 - beta)

/-- The iterated pinning: `x ↦ rup(ψ(x))`, 800 steps from `h`, early exit above 1. -/
def iterate (keff e0 ew hb kap gm beta : Rat) : Nat → Rat → Rat
  | 0, x => x
  | n + 1, x =>
    let y := rup (psi keff e0 ew hb kap gm beta x)
    if 1 < y then y else iterate keff e0 ew hb kap gm beta n y

/-- The constants of one certificate: `(ε₀, ε_w, H̄, β, κ, κ_eff, g_max, x*)`. -/
structure A36Stats where
  e0 : Rat
  ew : Rat
  hb : Rat
  beta : Rat
  kap : Rat
  keff : Rat
  gm : Rat
  xstar : Rat
  tan : Rat
  kill : Rat
deriving Repr

def a36Stats (c : A22Cert) (a : A36Cert) : A36Stats :=
  let bx0 := radBox c.z0 c.r0
  let bx := radBox c.z0 (a.h + c.r0)
  let e0 := eps0 c a bx0
  let ew := epsW c a bx0
  let hb := hbar c a bx
  let beta := betaA36 c a bx
  let kap := kappa c
  let keff := kappaEff c a
  let gm := gmax c a bx0
  let xs := iterate keff e0 ew hb kap gm beta 800 a.h
  let tan := validityMargin c (Array.ofFn (n := 36) fun i => i.val) bx
  let kill := KILLED_AXES.foldl (fun m (o, e, p) =>
    rmin m ((rng 4).foldl (fun b k => rmax b (-(evalIV bx (edgeRow p k o e)).hi)) (-1))) 1
  ⟨e0, ew, hb, beta, kap, keff, gm, xs, tan, kill⟩

/-- [S] the pin set is A22's `S` mapped. -/
def pinsOK (c : A22Cert) (a : A36Cert) : Bool := a.P == c.S.map mapPos

/-- [O] `valid_rows` is the spec's `R_V`; sign discipline of `ω`. -/
def omegaOK (a : A36Cert) : Bool :=
  let RV := if a.universal then universalRows else variantRows a.variantAxes
  decide (a.omega.size = NEXT3) &&
  (a.validRows.toList == RV) &&
  RV.all (fun k => decide (0 ≤ a.omega.getD k 0)) &&
  (rng NEXT3).all (fun k => RV.contains k || decide (a.omega.getD k 0 = 0)) &&
  pinsPositive a &&
  (a.universal || a.variantAxes.all fun ax => (axisRows ax).any fun k => decide (0 < a.omega.getD k 0))

/-- [N][A] activity at `ẑ` (over `box(z0, r0)`, threshold `1e-40`). -/
def activityOK (c : A22Cert) (a : A36Cert) (bx0 : Box) : Bool :=
  let tol : Rat := 1 / 10 ^ 40
  [NEW_V3_A, NEW_V3_B, AUX0, AUX1].all (fun k => decide ((evalIV bx0 (rowExpr (row70 c k))).mag < tol)) &&
    (loaded a).all fun k => decide ((evalIV bx0 (rowExpr (row70 c k))).mag < tol)

/-- [L] the 16 killed axes are refuted on the box: some corner row is negative. -/
def killedOK (bx : Box) : Bool :=
  KILLED_AXES.all fun (o, e, p) => (rng 4).any fun k =>
    decide ((evalIV bx (edgeRow p k o e)).hi < 0)

/-- [P] the contraction and the fixed point (explicit `ψ(x*) ≤ x*`, `x* + r0 ≤ r_N`). -/
def pinningOK (c : A22Cert) (a : A36Cert) (st : A36Stats) : Bool :=
  decide (st.beta < 1) &&
  decide (psi st.keff st.e0 st.ew st.hb st.kap st.gm st.beta a.h < a.h) &&
  decide (0 ≤ st.xstar) &&
  decide (psi st.keff st.e0 st.ew st.hb st.kap st.gm st.beta st.xstar ≤ st.xstar) &&
  decide (st.xstar + c.r0 ≤ c.rN)

/-- All 70 rows of the v3 table use only their declared variables and are well-shaped. -/
def rows70OK (c : A22Cert) : Bool :=
  (rng NEXT3).all fun k =>
    let r := row70 c k
    (rowExpr r).usesOnly (rowVars r) &&
    (match r with
      | .wall i kc w => decide (i < 11) && decide (kc < 4) && decide (w < 4)
      | .edge i kc j e => decide (i < 11) && decide (kc < 4) && decide (j < 11) && decide (e < 4) &&
          decide (i ≠ j)
      | .dist i j => decide (i < 11) && decide (j < 11) && decide (i ≠ j)
      | .angeq i j => decide (i < 11) && decide (j < 11))

/-- Every loaded row is a wall/edge/dist row, and every loaded EDGE row has its validity
margins over the box (tangential `< ½`, depth `> −½`). -/
def loadedValidOK (c : A22Cert) (a : A36Cert) (bx : Box) : Bool :=
  (loaded a).all fun k => match row70 c k with
    | .edge i kc j e =>
      decide ((evalIV bx (tanE i kc j e)).mag < 1 / 2) &&
        decide (-1 / 2 < (evalIV bx (depE i kc j e)).lo)
    | .angeq _ _ => false
    | _ => true

/-- The pin positions are distinct and within the 70-row table. -/
def pinsRangeOK (a : A36Cert) : Bool :=
  a.P.all (fun k => decide (k < NEXT3)) && decide a.P.toList.Nodup

/-- Some `S` wall row touches the far walls `x = s` or `y = s` (the slab gate of the
θ↔t transfer needs a corner of `ẑ` ON the far wall). -/
def farWallOK (c : A22Cert) : Bool :=
  c.S.any fun r => match c.row r with
    | .wall _ _ w => decide (w = 2) || decide (w = 3)
    | _ => false

/-- The A36 chain for one certificate. -/
def checkA36 (c : A22Cert) (a : A36Cert) : Bool :=
  let bx0 := radBox c.z0 c.r0
  let bx := radBox c.z0 (a.h + c.r0)
  let st := a36Stats c a
  decide (0 < a.h) && rows70OK c &&
  pinsOK c a && omegaOK a && activityOK c a bx0 &&
  pinningOK c a st &&
  validityOK c (Array.ofFn (n := 36) fun i => i.val) bx &&
  killedOK bx &&
  (!a.universal || loadedValidOK c a bx) && pinsRangeOK a && anglesSmall bx && farWallOK c

def checkA36All (c : A22Cert) (as : Array A36Cert) : Bool := as.all fun a => checkA36 c a

end PackingCert.Rigid
