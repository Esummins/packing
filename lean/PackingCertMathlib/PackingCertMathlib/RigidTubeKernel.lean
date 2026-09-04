import PackingCertMathlib.RigidKernel

/-!
# The contraction-tube checker (A86 T1, core Lean — the port of `certs/verify_tube.py`)

`docs/proofs/contraction_tube.md` Theorem T1 / `lean/tube_obligation_A83.md`.  A tube
certificate (`contraction-tube-certificate-v1`) carries a CENTRE-ONLY direction `v`
(`v_θ = 0`, `v_s = 1`, `v ≥ 0`), a depth `T`, radii `(r_c, r_θ, r_s)`, the universal
barrier `ω` (= `G3_UNIVERSAL`'s) and A22's pin set `P`.  The tube

    Tube_v(T, r) = { ẑ − t·v + w : 0 ≤ t ≤ T, |w_i| ≤ r_i }

is enclosed by the HULL box (`tubeArr`, asymmetric per coordinate) for the wall rows and,
for every pair row (edge / dist), by the PAIR-RELATIVE box (`pairArr`): on the tube the two
centres of a pair move TOGETHER along the ray, and edge/dist rows depend on the centres
only through `c_i − c_j` (translation invariance — the soundness file `RigidTube.lean`
proves it for the rows AND their symbolic derivatives).  The chain is A36's (V′) dichotomy
re-based on the tube (`RigidBasinMain.lean`), with

* the SPLIT Taylor remainder `d = −t·v + w`: `½|dᵀHd| ≤ ½ t̄² q_vv + t̄ Σ_i Hv_i w̄_i + ½ Σ_ab |H_ab| w̄_a w̄_b`
  (`Etube`), `t̄(x) = min(T, x + r_s)`, `w̄_i(x) = min(r_i, x + t̄(x)|v_i|)`;
* the MONOTONE iteration `x_{n+1} = rup ψ(x_n)` from `X_max` down to `r_N` (`iterT`) in
  place of `quad_pin`.

Every quantity is exact rational (dyadic `2^-330` outward rounding, `RigidKernel.lean`).
Load-bearing checks: format of `v`, `[S]` (pins, ω support), `[V]` (edge validity on the
pair boxes), `|θ| ≤ 1` on the hull, `[Z][G]` at the point box, `[H][K][E][P]`.  The
informational checks of the Python ([N] activity, [C] compression, [CANARY], claims) are
NOT part of `checkTube` — they carry no soundness content (A83 §4).
-/

namespace PackingCert.Rigid

open PackingCert.CaseI (rabs rmin rmax)

/-- One contraction-tube certificate (`certs/tube_*.json`, the load-bearing fields). -/
structure TubeCert where
  name : String
  T : Rat
  rC : Rat
  rT : Rat
  rS : Rat
  v : Array Rat
  omega : Array Rat
  P : Array Nat
  strictRows : Array Nat
deriving Repr, Inhabited

/-- The universal A36 certificate shell the tube reuses (`ω`, `P`, universal rows). -/
def TubeCert.a36 (tc : TubeCert) : A36Cert :=
  { name := tc.name, h := rmax tc.rC (rmax tc.rT tc.rS), omega := tc.omega, P := tc.P,
    universal := true, variantAxes := #[], validRows := universalRows.toArray, branchRows := #[] }

/-- Perturbation radius of coordinate `i`: `r_s` on the side, `r_θ` on tilts, `r_c` on centres. -/
def TubeCert.rad (tc : TubeCert) (i : Nat) : Rat :=
  if i = S_IDX then tc.rS else if i % 3 = 2 then tc.rT else tc.rC

/-- Direction component `i` (`0` out of range). -/
def TubeCert.vi (tc : TubeCert) (i : Nat) : Rat := tc.v.getD i 0

/-- The hull of the tube, widened by `r0` (`ẑ ∈ box(z0, r0)`):
`[z0_i − T·max(v_i,0) − r_i − r0, z0_i + T·max(−v_i,0) + r_i + r0]`. -/
def tubeArr (c : A22Cert) (tc : TubeCert) : Array IV :=
  Array.ofFn (n := NV) fun i =>
    let z := c.z0.getD i.val 0
    IV.mkR (z - tc.T * rmax (tc.vi i.val) 0 - tc.rad i.val - c.r0)
      (z + tc.T * rmax (-(tc.vi i.val)) 0 + tc.rad i.val + c.r0)

/-- The pair-relative box of squares `(i, j)`: the centre coordinates of `i` carry the
interval of `c_i − c_j` over the tube, those of `j` the point `0`; everything else is the
hull. -/
def pairArr (c : A22Cert) (tc : TubeCert) (i j : Nat) : Array IV :=
  let hull := tubeArr c tc
  Array.ofFn (n := NV) fun k =>
    if k.val = 3 * i ∨ k.val = 3 * i + 1 then
      let a := k.val
      let b := a - 3 * i + 3 * j
      let dv := tc.vi a - tc.vi b
      IV.mkR (c.z0.getD a 0 - c.z0.getD b 0 - tc.T * rmax dv 0 - tc.rad a - tc.rad b - 2 * c.r0)
        (c.z0.getD a 0 - c.z0.getD b 0 + tc.T * rmax (-dv) 0 + tc.rad a + tc.rad b + 2 * c.r0)
    else if k.val = 3 * j ∨ k.val = 3 * j + 1 then IV.zero
    else hull.getD k.val IV.zero

/-- The box a row is enclosed on: pair rows on their relative box, walls on the hull. -/
def rowArr (c : A22Cert) (tc : TubeCert) : Row → Array IV
  | .edge i _ j _ => pairArr c tc i j
  | .dist i j => pairArr c tc i j
  | _ => tubeArr c tc

def rowBoxT (c : A22Cert) (tc : TubeCert) (r : Row) : Box := Box.ofArray (rowArr c tc r)

/-- `[V]` on the tube: every loaded row is a wall/edge/dist row, and every loaded EDGE row
has its validity margins over ITS box (tangential `< ½`, depth `> −½`). -/
def loadedValidT (c : A22Cert) (tc : TubeCert) : Bool :=
  (loaded tc.a36).all fun k => match row70 c k with
    | .edge i kc j e =>
      let bx := rowBoxT c tc (.edge i kc j e)
      decide ((evalIV bx (tanE i kc j e)).mag < 1 / 2) &&
        decide (-1 / 2 < (evalIV bx (depE i kc j e)).lo)
    | .angeq _ _ => false
    | _ => true

/-- `Σ_k ω_k ∇²g_k` with every row enclosed on its own box. -/
def omegaHessT (c : A22Cert) (tc : TubeCert) : Array (Array IV) :=
  (loaded tc.a36).foldl (fun (acc : Array (Array IV)) k =>
    let r := row70 c k
    let H := hessDense (rowBoxT c tc r) r
    mkM NV fun i j =>
      (acc.getD i #[]).getD j IV.zero + IV.pt (tc.omega.getD k 0) * (H.getD i #[]).getD j IV.zero)
    (mkM NV fun _ _ => IV.zero)

def Hget (H : Array (Array IV)) (a b : Nat) : IV := (H.getD a #[]).getD b IV.zero

/-- `Σ_b v_a v_b H_ab` (interval), row `a`. -/
def vHvRow (tc : TubeCert) (H : Array (Array IV)) (a : Nat) : IV :=
  (rng NV).foldl (fun s b => s + IV.pt (tc.vi a * tc.vi b) * Hget H a b) IV.zero

/-- `q_vv = |Σ_ab v_a v_b H_ab|` (interval SUM first, then magnitude). -/
def qvvT (tc : TubeCert) (H : Array (Array IV)) : Rat :=
  ((rng NV).foldl (fun s a => s + vHvRow tc H a) IV.zero).mag

/-- `|(vᵀH)_b| = |Σ_a v_a H_ab|`. -/
def hvCol (tc : TubeCert) (H : Array (Array IV)) (b : Nat) : Rat :=
  ((rng NV).foldl (fun s a => s + IV.pt (tc.vi a) * Hget H a b) IV.zero).mag

/-- `|(Hv)_a| = |Σ_b H_ab v_b|`. -/
def hvRow (tc : TubeCert) (H : Array (Array IV)) (a : Nat) : Rat :=
  ((rng NV).foldl (fun s b => s + Hget H a b * IV.pt (tc.vi b)) IV.zero).mag

/-- `Hv_i = (|(vᵀH)_i| + |(Hv)_i|)/2` (no symmetry of the interval Hessian assumed). -/
def hvMag (tc : TubeCert) (H : Array (Array IV)) (i : Nat) : Rat := (hvCol tc H i + hvRow tc H i) / 2

def hMag (H : Array (Array IV)) (a b : Nat) : Rat := (Hget H a b).mag

/-- Interval Jacobian rows of the pin set, each on its own box. -/
def pinJT (c : A22Cert) (tc : TubeCert) : Array (Array IV) :=
  tc.P.map fun k => gradDense (rowBoxT c tc (row70 c k)) (row70 c k)

/-- `β = max_i Σ_j |(I − Y J)_ij|` over the tube. -/
def betaT (c : A22Cert) (tc : TubeCert) : Rat :=
  let J := pinJT c tc
  (rng NV).foldl (fun b i => rmax b (betaRow (Mrow c.Y J i))) 0

/-! ## The split remainder and the monotone iteration -/

/-- `t̄(x) = min(T, x + r_s)`. -/
def tbQ (T rS x : Rat) : Rat := rmin T (x + rS)

/-- `w̄_i(x) = min(r_i, x + t̄(x)·|v_i|)`. -/
def wbQ (tc : TubeCert) (x : Rat) (i : Nat) : Rat :=
  rmin (tc.rad i) (x + tbQ tc.T tc.rS x * rabs (tc.vi i))

/-- The tube's constants (all rational). -/
structure TubeStats where
  e0 : Rat
  ew : Rat
  gm : Rat
  qvv : Rat
  hv : Array Rat           -- `Hv_i`, `NV` entries
  hm : Array (Array Rat)   -- `|H_ab|`, `NV × NV`
  beta : Rat
  kap : Rat
  keff : Rat
  xmax : Rat
deriving Repr

def TubeStats.hvi (st : TubeStats) (i : Nat) : Rat := st.hv.getD i 0

def TubeStats.hmab (st : TubeStats) (a b : Nat) : Rat := (st.hm.getD a #[]).getD b 0

/-- `E(x) = ε₀ + ε_w x + ½ t̄² q_vv + t̄ Σ_i Hv_i w̄_i + ½ Σ_ab |H_ab| w̄_a w̄_b`. -/
def Etube (tc : TubeCert) (st : TubeStats) (x : Rat) : Rat :=
  let tb := tbQ tc.T tc.rS x
  st.e0 + st.ew * x + (1 / 2) * tb * tb * st.qvv
    + tb * (rng NV).foldl (fun s i => s + st.hvi i * wbQ tc x i) 0
    + (1 / 2) * (rng NV).foldl (fun s a =>
        s + (rng NV).foldl (fun s b => s + st.hmab a b * wbQ tc x a * wbQ tc x b) 0) 0

/-- `ψ(x) = (κ_eff E(x) + κ g_max)/(1 − β)`. -/
def psiT (tc : TubeCert) (st : TubeStats) (x : Rat) : Rat :=
  (st.keff * Etube tc st x + st.kap * st.gm) / (1 - st.beta)

/-- The monotone iteration: `x ↦ rup ψ(x)`, stop as soon as `x + r0 ≤ r_N`; fail on
stagnation (`ψ(x) ≥ x`) or when the fuel runs out. -/
def iterT (tc : TubeCert) (st : TubeStats) (r0 rN : Rat) : Nat → Rat → Bool
  | 0, _ => false
  | n + 1, x =>
    let y := rup (psiT tc st x)
    if y + r0 ≤ rN then true
    else if x ≤ y then false
    else iterT tc st r0 rN n y

def tubeStats (c : A22Cert) (tc : TubeCert) : TubeStats :=
  let a := tc.a36
  let bx0 := radBox c.z0 c.r0
  let H := omegaHessT c tc
  { e0 := eps0 c a bx0, ew := epsW c a bx0, gm := gmax c a bx0,
    qvv := qvvT tc H,
    hv := Array.ofFn (n := NV) fun i => hvMag tc H i.val,
    hm := Array.ofFn (n := NV) fun a => Array.ofFn (n := NV) fun b => hMag H a.val b.val,
    beta := betaT c tc, kap := kappa c, keff := kappaEff c a,
    xmax := (rng NV).foldl (fun m i => rmax m (tc.T * rabs (tc.vi i) + tc.rad i + 2 * c.r0)) 0 }

/-- `[F]`: `v` is centre-only (`v_θ = 0`, `v_s = 1`, `v ≥ 0`), `T ≥ 0`, radii `> 0`, `r_s ≥ 0`. -/
def tubeShapeOK (tc : TubeCert) : Bool :=
  decide (0 ≤ tc.T) && decide (0 < tc.rC) && decide (0 < tc.rT) && decide (0 ≤ tc.rS) &&
  decide (tc.v.size = NV) && decide (tc.vi S_IDX = 1) &&
  (rng 11).all (fun i => decide (tc.vi (3 * i + 2) = 0)) &&
  tc.v.all (fun x => decide (0 ≤ x))

/-- Maximal number of iteration steps (the Python default `nmax = 4000`). -/
def NMAX_TUBE : Nat := 4000

/-- **The contraction-tube checker.** -/
def checkTube (c : A22Cert) (tc : TubeCert) : Bool :=
  let a := tc.a36
  let hull := Box.ofArray (tubeArr c tc)
  let st := tubeStats c tc
  tubeShapeOK tc && rows70OK c && pinsOK c a && omegaOK a && pinsRangeOK a &&
  anglesSmall hull && loadedValidT c tc &&
  decide (st.beta < 1) && iterT tc st c.r0 c.rN NMAX_TUBE st.xmax

def checkTubeAll (c : A22Cert) (tcs : Array TubeCert) : Bool := tcs.all fun tc => checkTube c tc

end PackingCert.Rigid
