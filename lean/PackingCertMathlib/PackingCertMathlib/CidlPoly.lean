/-!
# Sparse multivariate rational polynomials for the (c-idl) replay (A78 T2, CIDL-LEAN)

Core Lean only (no Mathlib): `Rat` and `List` from core suffice, so this module and the
`native_decide` module `CidlCheck.lean` that consumes it are cheap to elaborate.  The
real-valued semantics and every soundness lemma live in `CidlBridge.lean`.

A polynomial is a LIST of `(exponent vector, coefficient)` pairs — a *multiset* of terms,
not a normal form: `padd` is `++`, `pmulRaw` is the pairwise product list.  Only
`pnorm` (mergeSort by the lexicographic exponent order, then collapse adjacent equal
exponents and drop zeros) produces a canonical-ish form, and only ONE property of it is
load-bearing for soundness:

    `pnorm p` is a permutation-then-collapse of `p`, hence has the same value at every
    point (`CidlBridge.eval_pnorm`).

In particular the *sortedness* of `pnorm` is irrelevant to soundness: if `isZero p` is
`true` then `eval p xs = 0` for every `xs`, whatever the comparison function does.  A
wrong comparison could only make the check FAIL, never make it wrongly succeed.

Variable order (13 variables, as `certs/verify_cidl.py`'s `VARS`):

    0:t  1:y4  2:x6  3:y6  4:x7  5:y7  6:x8  7:y8  8:x9  9:y9  10:x10  11:y10  12:S
-/

namespace PackingCert
namespace Cidl

/-- An exponent vector.  All monomials built here have length 13, but no lemma needs
that: `mmul` pads, and `evalM` (in `CidlBridge`) is total on ragged input. -/
abbrev Mono := List Nat

/-- A polynomial: a list of `(monomial, coefficient)` terms, summed. -/
abbrev Poly := List (Mono × Rat)

/-- Monomial product: pointwise addition of exponents, PADDING the shorter vector
(so no length hypothesis is ever needed). -/
def mmul : Mono → Mono → Mono
  | [], m => m
  | a :: as, [] => a :: as
  | a :: as, b :: bs => (a + b) :: mmul as bs

/-- Sum of polynomials = concatenation of term lists. -/
def padd (p q : Poly) : Poly := p ++ q

/-- Negation. -/
def pneg (p : Poly) : Poly := p.map (fun x => (x.1, -x.2))

/-- Scaling by a rational. -/
def pscale (c : Rat) (p : Poly) : Poly := p.map (fun x => (x.1, c * x.2))

/-- The RAW product: every pair of terms, no normalisation. -/
def pmulRaw : Poly → Poly → Poly
  | [], _ => []
  | x :: p, q => q.map (fun y => (mmul x.1 y.1, x.2 * y.2)) ++ pmulRaw p q

/-- Lexicographic strict order on exponent vectors (shorter-is-smaller at the tail). -/
def monoLt : Mono → Mono → Bool
  | [], [] => false
  | [], _ :: _ => true
  | _ :: _, [] => false
  | a :: as, b :: bs => if a < b then true else if b < a then false else monoLt as bs

/-- The `le` used by `mergeSort`: `x ≤ y` iff `¬ (y < x)`. -/
def termLe (x y : Mono × Rat) : Bool := !(monoLt y.1 x.1)

/-- Push one term onto an already-collapsed list, merging with the head if the
exponents agree and dropping zero coefficients. -/
def pcons (m : Mono) (c : Rat) : Poly → Poly
  | [] => if c = 0 then [] else [(m, c)]
  | (m2, c2) :: r =>
      if m = m2 then (if c + c2 = 0 then r else (m, c + c2) :: r)
      else if c = 0 then (m2, c2) :: r
      else (m, c) :: (m2, c2) :: r

/-- Collapse a (sorted) term list: merge adjacent equal exponents, drop zeros. -/
def pcollapse : Poly → Poly
  | [] => []
  | (m, c) :: p => pcons m c (pcollapse p)

/-- Normal form: sort, then collapse. -/
def pnorm (p : Poly) : Poly := pcollapse (p.mergeSort termLe)

/-- The zero test used by the certificate replay. -/
def isZero (p : Poly) : Bool := (pnorm p).isEmpty

/-- Normalised product (used for `Delta ^ 8`, where the raw product would blow up). -/
def pmul (p q : Poly) : Poly := pnorm (pmulRaw p q)

/-- The constant polynomial `1`. -/
def pone : Poly := [(List.replicate 13 0, 1)]

/-- Normalised power. -/
def ppow (p : Poly) : Nat → Poly
  | 0 => pone
  | n + 1 => pmul p (ppow p n)

/-! ## Monomial constructors -/

/-- The all-zero exponent vector of length 13. -/
def monoZero : Mono := List.replicate 13 0

/-- The exponent vector with `k` in slot `i` (length 13). -/
def monoOf (i k : Nat) : Mono :=
  List.replicate i 0 ++ k :: List.replicate (12 - i) 0

/-- `t^kt * S^ks` (variables 0 and 12) — written out so the `evalM` computation in
`CidlBridge` is a 13-step unfold with no `List.replicate` reasoning. -/
def tsMono (kt ks : Nat) : Mono := [kt, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ks]

/-- The constant polynomial `c`. -/
def pconst (c : Rat) : Poly := if c = 0 then [] else [(monoZero, c)]

/-- The variable `i` as a polynomial. -/
def pvar (i : Nat) : Poly := [(monoOf i 1, 1)]

/-! ## Building polynomials from integer coefficient lists

`uniToPoly` mirrors `verify_cidl.py`'s `uni_to_p`; `bivToPoly` mirrors `parse_biv`. -/

/-- `t`-univariate helper: term `k` of `cs` sits at `t^k * S^s`. -/
def bivAux (s : Nat) : Nat → List Int → Poly
  | _, [] => []
  | k, c :: cs =>
      if c = 0 then bivAux s (k + 1) cs
      else (tsMono k s, (c : Rat)) :: bivAux s (k + 1) cs

/-- A univariate polynomial in `t` (variable 0). -/
def tUniToPoly (cs : List Int) : Poly := bivAux 0 0 cs

/-- `S`-univariate helper: term `k` of `cs` sits at `S^k`. -/
def sAux : Nat → List Int → Poly
  | _, [] => []
  | k, c :: cs =>
      if c = 0 then sAux (k + 1) cs
      else (tsMono 0 k, (c : Rat)) :: sAux (k + 1) cs

/-- A univariate polynomial in `S` (variable 12). -/
def sUniToPoly (cs : List Int) : Poly := sAux 0 cs

/-- A bivariate cofactor `q(t, S)`, given as a list of `(S-power, t-coefficients)`. -/
def bivToPoly : List (Nat × List Int) → Poly
  | [] => []
  | (s, cs) :: rest => bivAux s 0 cs ++ bivToPoly rest

/-! ## The sign gate, as a monomial interval bound

For `0 ≤ a ≤ x ≤ b` every term `c·x^k` of a univariate integer polynomial is bounded
above by `c·b^k` (if `c ≥ 0`) or `c·a^k` (if `c < 0`).  `ubound` sums those bounds; if
the sum is `< 0` the polynomial is strictly negative on `[a, b]`.  Both gates of the
certificate ([G] in `certs/verify_cidl.py`) pass this crude test on `[3/10, 2/5]`
(`e` ≤ −1.83…, `Delta` ≤ −3.45…), so no Sturm chain and no Taylor shift is needed
in Lean; soundness is `CidlBridge.uniR_neg_of_gateNeg`. -/

/-- Upper bound for `Σ_k c_k x^k` over `x ∈ [a, b]` with `0 ≤ a`, term by term. -/
def ubAux : Nat → Rat → Rat → List Int → Rat
  | _, _, _, [] => 0
  | k, a, b, c :: cs =>
      (if 0 ≤ c then (c : Rat) * b ^ k else (c : Rat) * a ^ k) + ubAux (k + 1) a b cs

/-- `ubound cs a b ≥ Σ_k c_k x^k` for every `x ∈ [a, b]`, `0 ≤ a`. -/
def ubound (cs : List Int) (a b : Rat) : Rat := ubAux 0 a b cs

/-- The decidable gate: the coefficient list is strictly negative on `[a, b]`. -/
def gateNeg (cs : List Int) (a b : Rat) : Bool := decide (ubound cs a b < 0)

end Cidl
end PackingCert
