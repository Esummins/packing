import PackingCertMathlib.CaseChecker

/-!
# The ALIVE-side arbiter `checkAlive` — A78, depgraph node D.ALIVE

Core Lean 4 only, no Mathlib.  The exact-arithmetic core of
`attempts/A57-shadow-trees/code/alivewitness.py` (functions `cs`, `gap_exact`,
`admissible_exact`, `snap_and_verify`), which decides the **completeness** side of a
node: it exhibits a *disjoint family* of admissible unit squares avoiding every core,
and thereby proves that **no** case-LP certificate of the node's budget can exist.

The Python header lemma:

> Let `N` be a node with cores `C_1..C_r` and budget `m = 11 − r`.  If `Q_1..Q_m` are
> closed unit squares in `[0,s]²` that are (i) admissible, (ii) pairwise disjoint with
> a strictly positive separating gap and (iii) strictly disjoint from every core, then
> every measure feasible for the node LP has `μ(Q_i) ≥ 1`, and `τ* ≥ m = budget`, so no
> certificate for `N` can exist.

`AliveBridge.lean` proves exactly that, in the form the Lean-side consumer needs:
a PASS makes `checkCaseI` (the Lean port of `verify_case.py`, `CaseChecker.lean`) return
`false` on **every** certificate with these cores, this side, this budget and no
NO-families.  The node is LP-unkillable in the verifier's own sense.

Faithfulness (Python ⟶ Lean, all decision-neutral or strictly stronger):

* `cs(t)` is `CaseI.ratCosSin`, shared verbatim with the case checker;
* `gap_exact` is `gapExact`: the max over the four SAT axes (each square's two edge
  normals) of `separation − h_own − h_other·(|n·e'| + |n·e'⊥|)`, in exact `Rat`;
* `admissible_exact` is `admissible`, with `s` a certificate field rather than the
  Python module constant `S_RAT = 969271/250000`, and half-side `1/2` fixed;
* `snap_and_verify`'s accept condition `ok` is `checkAlive`: every witness admissible,
  every witness–core gap `> 0`, every witness–witness gap `> 0`, and `len(Q) ≥ m`
  (here `=`, since a certificate carries exactly its budget's worth of witnesses).
  The Python *search* layers (`gap_f`, `candidates`, `search`, and the float→rational
  snapping `rat`) are floats and do not appear: they only PROPOSE the family, which is
  then re-decided exactly.  The rational data of a witness is the certificate here.
* the extra gate `0 ≤ t ≤ 1` is NOT in the Python (which snaps `t = tan(θ/2)` from a
  float tilt in `[0°, 90°]` and so always satisfies it); it is required in Lean because
  `PSq` semantics (and `wT = cos + sin ≥ 1`) are stated on `t ∈ [0,1]`.
-/

namespace PackingCert.AliveI

open PackingCert.CaseI

/-- A witness square: centre `(cx, cy)` and `t = tan(θ/2)`; half-side is always `1/2`
(the Python `Q` entries `((cx, cy), t, Fr(1,2))`). -/
abbrev AWSq := Rat × Rat × Rat

@[inline] def awx (q : AWSq) : Rat := q.1
@[inline] def awy (q : AWSq) : Rat := q.2.1
@[inline] def awt (q : AWSq) : Rat := q.2.2

/-- An ALIVE witness certificate for one node: the side `s`, the node's cores
(identical to the `cores` of any case-LP certificate for the node), the budget
`m = n − r`, and the `m` witness squares. -/
structure AliveCert where
  s      : Rat
  cores  : List CCore
  budget : Nat
  sq     : List AWSq
deriving Repr

/-! ## Exact geometry (`gap_exact`) -/

/-- One SAT axis of `gap_exact`: axis `(axx, axy)` is an edge normal of the OWN square
(centre `(cx, cy)`, half-side `hh`, so its own half-width along the axis is exactly
`hh`); the other square has centre `(ocx, ocy)`, half-side `oh` and edge frame
`(oco, osi)`.  Positive value ⟹ this axis separates. -/
def gapOne (cx cy hh axx axy ocx ocy oh oco osi : Rat) : Rat :=
  rabs ((ocx - cx) * axx + (ocy - cy) * axy) - hh
    - oh * (rabs (axx * oco + axy * osi) + rabs (-axx * osi + axy * oco))

/-- `gap_exact(c1, t1, h1, c2, t2, h2)`: the max over the four SAT axes (both edge
normals of both squares).  `> 0` ⟹ the two CLOSED squares are disjoint. -/
def gapExact (cx1 cy1 t1 h1 cx2 cy2 t2 h2 : Rat) : Rat :=
  rmax
    (rmax (gapOne cx1 cy1 h1 (ratCosSin t1).1 (ratCosSin t1).2
              cx2 cy2 h2 (ratCosSin t2).1 (ratCosSin t2).2)
          (gapOne cx1 cy1 h1 (-(ratCosSin t1).2) (ratCosSin t1).1
              cx2 cy2 h2 (ratCosSin t2).1 (ratCosSin t2).2))
    (rmax (gapOne cx2 cy2 h2 (ratCosSin t2).1 (ratCosSin t2).2
              cx1 cy1 h1 (ratCosSin t1).1 (ratCosSin t1).2)
          (gapOne cx2 cy2 h2 (-(ratCosSin t2).2) (ratCosSin t2).1
              cx1 cy1 h1 (ratCosSin t1).1 (ratCosSin t1).2))

/-- The Python `w = h·(|cos| + |sin|)` at `h = 1/2`: half the container width of a
unit square of tilt `t`. -/
def halfWidth (t : Rat) : Rat := (rabs (ratCosSin t).1 + rabs (ratCosSin t).2) / 2

/-- `admissible_exact`: the closed unit square with centre `(cx, cy)` and tilt `t` is
contained in `[0,s]²` — `w ≤ c ≤ s − w` on both axes with `w = (|cos| + |sin|)/2`. -/
def admissible (s cx cy t : Rat) : Bool :=
  halfWidth t ≤ cx && cx ≤ s - halfWidth t &&
  halfWidth t ≤ cy && cy ≤ s - halfWidth t

/-- Per-witness gates: `t ∈ [0,1]` and admissibility at the certificate's side. -/
def witOK (s : Rat) (q : AWSq) : Bool :=
  0 ≤ awt q && awt q ≤ 1 && admissible s (awx q) (awy q) (awt q)

/-- Strict disjointness of a witness from every core (cores carry their own
half-side `a` and tilt `tm` — NOT `1/2`; see the spec note in `AliveBridge.lean`). -/
def coreGapOK (cores : List CCore) (q : AWSq) : Bool :=
  cores.all fun K => 0 < gapExact (awx q) (awy q) (awt q) (1 / 2) K.kx K.ky K.tm K.a

/-- Strict disjointness of two witnesses (both half-side `1/2`). -/
def pairGapOK (p q : AWSq) : Bool :=
  0 < gapExact (awx p) (awy p) (awt p) (1 / 2) (awx q) (awy q) (awt q) (1 / 2)

/-- Every unordered pair of the witness list has a strictly positive gap. -/
def pairsOK : List AWSq → Bool
  | [] => true
  | q :: rest => rest.all (pairGapOK q) && pairsOK rest

/-- **The ALIVE check.**  PASS ⟹ the node carries a disjoint family of `budget`
admissible core-free unit squares ⟹ no case-LP certificate for it can exist
(`AliveBridge.alive_sound`).  The budget arithmetic itself (`m = n − r`) is left to
the consumer: it is the hypothesis `c.n = w.cores.length + w.budget`. -/
def checkAlive (c : AliveCert) : Bool :=
  c.cores.all coreOK &&
  c.sq.all (witOK c.s) &&
  c.sq.all (coreGapOK c.cores) &&
  pairsOK c.sq &&
  decide (c.sq.length = c.budget)

end PackingCert.AliveI
