import Mathlib.Data.Real.Basic
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.CidlCheck

/-!
# Soundness of the (c-idl) replay: from `isZero` to a real identity (A78 T2, CIDL-LEAN)

This file gives `CidlPoly`'s syntax its real-valued semantics and turns the four
`native_decide` facts of `CidlCheck.lean` into the composed statement

  `octic_zero_of_generators` — if the 13 A22 contact generators vanish at a real
  13-tuple `(t, y4, x6…y10, S)` with `t ∈ [3/10, 2/5]`, then `octic S = 0`.

Nothing here mentions `TopLevel`; the A22 interface axiom that supplies such a tuple
lives there (`a22_exact_structure`).

Soundness chain (`certs/verify_cidl.py` [I] + [G]):

* `eval_pnorm` — `pnorm` only permutes-and-collapses, so it preserves the value.  The
  comparison function `termLe` is NOT assumed to be an order: a wrong comparison could
  only make `isZero` return `false`.
* `eval_isZero` / `eval_eq_of_isZero_sub` — `isZero (p − q) = true ⇒ eval p = eval q`.
* `uniR_neg_of_gateNeg` — the monomial interval bound `ubound` certifies `e < 0` and
  `Δ < 0` on `[3/10, 2/5]`, which is strictly stronger than the checker's Sturm
  "no root in the gate interval".
-/

namespace PackingCert
namespace Cidl

noncomputable section

/-! ## Semantics -/

/-- Value of a monomial.  Total on ragged input: exponents past the end of the point
list, and point coordinates past the end of the exponent vector, are ignored.  (All
monomials built here have length 13 and all points are `pt13`, so this never bites; it
buys unconditional lemmas — no length hypotheses anywhere.) -/
def evalM : Mono → List ℝ → ℝ
  | [], _ => 1
  | _ :: _, [] => 1
  | e :: es, x :: xs => x ^ e * evalM es xs

/-- Value of a polynomial at a point. -/
def eval : Poly → List ℝ → ℝ
  | [], _ => 0
  | (m, c) :: p, xs => (c : ℝ) * evalM m xs + eval p xs

/-- The 13-tuple `(t, y4, x6, y6, x7, y7, x8, y8, x9, y9, x10, y10, S)` as a point. -/
def pt13 (t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S : ℝ) : List ℝ :=
  [t, y4, x6, y6, x7, y7, x8, y8, x9, y9, x10, y10, S]

@[simp] theorem eval_nil (xs : List ℝ) : eval [] xs = 0 := rfl

@[simp] theorem eval_cons (x : Mono × Rat) (p : Poly) (xs : List ℝ) :
    eval (x :: p) xs = (x.2 : ℝ) * evalM x.1 xs + eval p xs := by
  cases x; rfl

theorem eval_append (p q : Poly) (xs : List ℝ) :
    eval (p ++ q) xs = eval p xs + eval q xs := by
  induction p with
  | nil => simp
  | cons a p ih => simp only [List.cons_append, eval_cons, ih]; ring

theorem eval_padd (p q : Poly) (xs : List ℝ) :
    eval (padd p q) xs = eval p xs + eval q xs := eval_append p q xs

theorem eval_pneg (p : Poly) (xs : List ℝ) : eval (pneg p) xs = -eval p xs := by
  induction p with
  | nil => simp [pneg]
  | cons a p ih => simp only [pneg, List.map_cons, eval_cons, ih] at *; push_cast; ring

theorem evalM_mmul (m₁ m₂ : Mono) (xs : List ℝ) :
    evalM (mmul m₁ m₂) xs = evalM m₁ xs * evalM m₂ xs := by
  induction m₁ generalizing m₂ xs with
  | nil => simp [mmul, evalM]
  | cons a as ih =>
    cases m₂ with
    | nil => simp [mmul, evalM]
    | cons b bs =>
      cases xs with
      | nil => simp [mmul, evalM]
      | cons x xs => simp only [mmul, evalM, ih, pow_add]; ring

theorem eval_mulTerm (m : Mono) (c : Rat) (q : Poly) (xs : List ℝ) :
    eval (q.map (fun y => (mmul m y.1, c * y.2))) xs = (c : ℝ) * evalM m xs * eval q xs := by
  induction q with
  | nil => simp
  | cons y q ih => simp only [List.map_cons, eval_cons, ih, evalM_mmul]; push_cast; ring

theorem eval_pmulRaw (p q : Poly) (xs : List ℝ) :
    eval (pmulRaw p q) xs = eval p xs * eval q xs := by
  induction p with
  | nil => simp [pmulRaw]
  | cons x p ih => simp only [pmulRaw, eval_append, eval_mulTerm, ih, eval_cons]; ring

theorem eval_perm {p q : Poly} (h : p.Perm q) (xs : List ℝ) : eval p xs = eval q xs := by
  induction h with
  | nil => rfl
  | cons a _ ih => simp [ih]
  | swap a b l => simp; ring
  | trans _ _ ih₁ ih₂ => rw [ih₁, ih₂]

theorem pcons_nil (m : Mono) (c : Rat) : pcons m c [] = if c = 0 then [] else [(m, c)] := rfl

theorem pcons_cons (m : Mono) (c : Rat) (m₂ : Mono) (c₂ : Rat) (r : Poly) :
    pcons m c ((m₂, c₂) :: r) =
      (if m = m₂ then (if c + c₂ = 0 then r else (m, c + c₂) :: r)
        else if c = 0 then (m₂, c₂) :: r else (m, c) :: (m₂, c₂) :: r) := rfl

theorem eval_pcons (m : Mono) (c : Rat) (p : Poly) (xs : List ℝ) :
    eval (pcons m c p) xs = (c : ℝ) * evalM m xs + eval p xs := by
  match p with
  | [] =>
      rw [pcons_nil]
      split_ifs with hc
      · subst hc; simp
      · simp
  | (m₂, c₂) :: r =>
      rw [pcons_cons]
      split_ifs with hm hc hc₀
      · subst hm
        have hc₂ : c₂ = -c := by linarith
        subst hc₂
        simp only [eval_cons]
        push_cast
        ring
      · subst hm
        simp only [eval_cons]
        push_cast
        ring
      · subst hc₀
        simp only [eval_cons]
        push_cast
        ring
      · simp only [eval_cons]

theorem eval_pcollapse (p : Poly) (xs : List ℝ) : eval (pcollapse p) xs = eval p xs := by
  induction p with
  | nil => rfl
  | cons x p ih =>
    obtain ⟨m, c⟩ := x
    simp only [pcollapse, eval_pcons, ih, eval_cons]

theorem eval_pnorm (p : Poly) (xs : List ℝ) : eval (pnorm p) xs = eval p xs := by
  rw [pnorm, eval_pcollapse]
  exact eval_perm (List.mergeSort_perm p termLe) xs

theorem eval_pmul (p q : Poly) (xs : List ℝ) :
    eval (pmul p q) xs = eval p xs * eval q xs := by
  rw [pmul, eval_pnorm, eval_pmulRaw]

theorem evalM_replicate_zero (n : Nat) (xs : List ℝ) :
    evalM (List.replicate n 0) xs = 1 := by
  induction n generalizing xs with
  | zero => simp [evalM]
  | succ n ih =>
    cases xs with
    | nil => simp [List.replicate_succ, evalM]
    | cons x xs => simp [List.replicate_succ, evalM, ih]

@[simp] theorem eval_pone (xs : List ℝ) : eval pone xs = 1 := by
  simp only [pone, eval_cons, eval_nil, monoZero, evalM_replicate_zero]
  norm_num

theorem eval_ppow (p : Poly) (n : Nat) (xs : List ℝ) :
    eval (ppow p n) xs = (eval p xs) ^ n := by
  induction n with
  | zero => simp [ppow]
  | succ n ih => simp [ppow, eval_pmul, ih]; ring

theorem eval_isZero {p : Poly} (h : isZero p = true) (xs : List ℝ) : eval p xs = 0 := by
  have hp : pnorm p = [] := by simpa [isZero] using h
  rw [← eval_pnorm, hp, eval_nil]

/-- The workhorse: a `native_decide`-checked `isZero (p − q)` gives a REAL identity. -/
theorem eval_eq_of_isZero_sub {p q : Poly} (h : isZero (padd p (pneg q)) = true)
    (xs : List ℝ) : eval p xs = eval q xs := by
  have h0 := eval_isZero h xs
  rw [eval_padd, eval_pneg] at h0
  linarith

theorem eval_flatten (L : List Poly) (xs : List ℝ) :
    eval L.flatten xs = (L.map fun p => eval p xs).sum := by
  induction L with
  | nil => simp
  | cons p L ih => simp [eval_append, ih]

/-- If every generator vanishes at `xs`, so does `Σ_j q_j · G_j`, whatever the
cofactors are. -/
theorem eval_zipWith_pmulRaw_eq_zero (C G : List Poly) (xs : List ℝ)
    (hg : ∀ g ∈ G, eval g xs = 0) : eval (List.zipWith pmulRaw C G).flatten xs = 0 := by
  induction C generalizing G with
  | nil => simp
  | cons c C ih =>
    cases G with
    | nil => simp
    | cons g G =>
      have hgg : eval g xs = 0 := hg g (by simp)
      have hrest : ∀ x ∈ G, eval x xs = 0 := fun x hx => hg x (by simp [hx])
      simp only [List.zipWith_cons_cons, List.flatten_cons, eval_append, eval_pmulRaw,
        hgg, ih G hrest, mul_zero, add_zero]

/-! ## Univariate real polynomials -/

/-- `Σ_{i} cs[i] · x^(k+i)`. -/
def uniRAux : List Int → Nat → ℝ → ℝ
  | [], _, _ => 0
  | c :: cs, k, x => (c : ℝ) * x ^ k + uniRAux cs (k + 1) x

/-- The real polynomial with integer coefficient list `cs` (low to high). -/
def uniR (cs : List Int) (x : ℝ) : ℝ := uniRAux cs 0 x

/-- The canonical Trump octic, as a coefficient list evaluation. -/
def octicR (x : ℝ) : ℝ := uniR OCTIC x

theorem octicR_eq (x : ℝ) :
    octicR x = x ^ 8 - 20 * x ^ 7 + 178 * x ^ 6 - 842 * x ^ 5 + 1923 * x ^ 4
      - 496 * x ^ 3 - 6754 * x ^ 2 + 12420 * x - 6865 := by
  simp only [octicR, uniR, OCTIC, uniRAux]
  norm_num
  ring

/-! ## Evaluating the built polynomials -/

variable (t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S : ℝ)

theorem evalM_tsMono (kt ks : Nat) :
    evalM (tsMono kt ks) (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S) = t ^ kt * S ^ ks := by
  simp [tsMono, pt13, evalM]

theorem bivAux_cons (s k : Nat) (c : Int) (cs : List Int) :
    bivAux s k (c :: cs) =
      if c = 0 then bivAux s (k + 1) cs
      else (tsMono k s, (c : Rat)) :: bivAux s (k + 1) cs := rfl

theorem uniRAux_cons (c : Int) (cs : List Int) (k : Nat) (x : ℝ) :
    uniRAux (c :: cs) k x = (c : ℝ) * x ^ k + uniRAux cs (k + 1) x := rfl

theorem eval_bivAux (s : Nat) : ∀ (cs : List Int) (k : Nat),
    eval (bivAux s k cs) (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S)
      = uniRAux cs k t * S ^ s := by
  intro cs
  induction cs with
  | nil => intro k; simp [bivAux, uniRAux]
  | cons c cs ih =>
    intro k
    rw [bivAux_cons, uniRAux_cons]
    split_ifs with hc
    · rw [ih (k + 1), hc]
      push_cast
      ring
    · simp only [eval_cons, evalM_tsMono, ih (k + 1)]
      push_cast
      ring

theorem eval_tUniToPoly (cs : List Int) :
    eval (tUniToPoly cs) (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S) = uniR cs t := by
  simp [tUniToPoly, eval_bivAux, uniR]

theorem sAux_cons (k : Nat) (c : Int) (cs : List Int) :
    sAux k (c :: cs) =
      if c = 0 then sAux (k + 1) cs
      else (tsMono 0 k, (c : Rat)) :: sAux (k + 1) cs := rfl

theorem eval_sAux : ∀ (cs : List Int) (k : Nat),
    eval (sAux k cs) (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S) = uniRAux cs k S := by
  intro cs
  induction cs with
  | nil => intro k; simp [sAux, uniRAux]
  | cons c cs ih =>
    intro k
    rw [sAux_cons, uniRAux_cons]
    split_ifs with hc
    · rw [ih (k + 1), hc]
      push_cast
      ring
    · simp only [eval_cons, evalM_tsMono, ih (k + 1)]
      push_cast
      ring

theorem eval_sUniToPoly (cs : List Int) :
    eval (sUniToPoly cs) (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S) = uniR cs S := by
  simp [sUniToPoly, eval_sAux, uniR]

/-! ## The sign gate -/

theorem uniRAux_le_ubAux {a b : Rat} {x : ℝ} (ha : (0 : ℝ) ≤ (a : ℝ))
    (hax : (a : ℝ) ≤ x) (hxb : x ≤ (b : ℝ)) :
    ∀ (cs : List Int) (k : Nat), uniRAux cs k x ≤ ((ubAux k a b cs : Rat) : ℝ) := by
  have hx0 : (0 : ℝ) ≤ x := le_trans ha hax
  intro cs
  induction cs with
  | nil => intro k; simp [uniRAux, ubAux]
  | cons c cs ih =>
    intro k
    have hterm : (c : ℝ) * x ^ k ≤
        ((if 0 ≤ c then (c : Rat) * b ^ k else (c : Rat) * a ^ k : Rat) : ℝ) := by
      by_cases hc : 0 ≤ c
      · have hcR : (0 : ℝ) ≤ (c : ℝ) := by exact_mod_cast hc
        have hpow : x ^ k ≤ (b : ℝ) ^ k := pow_le_pow_left₀ hx0 hxb k
        simp only [if_pos hc]
        push_cast
        exact mul_le_mul_of_nonneg_left hpow hcR
      · have hcR : (c : ℝ) ≤ 0 := by
          have : c ≤ 0 := le_of_lt (lt_of_not_ge hc)
          exact_mod_cast this
        have hpow : (a : ℝ) ^ k ≤ x ^ k := pow_le_pow_left₀ ha hax k
        simp only [if_neg hc]
        push_cast
        exact mul_le_mul_of_nonpos_left hpow hcR
    have hrest := ih (k + 1)
    simp only [uniRAux, ubAux]
    push_cast
    push_cast at hterm
    linarith

theorem uniR_neg_of_gateNeg {cs : List Int} {a b : Rat} (h : gateNeg cs a b = true)
    (ha : (0 : ℝ) ≤ (a : ℝ)) {x : ℝ} (hax : (a : ℝ) ≤ x) (hxb : x ≤ (b : ℝ)) :
    uniR cs x < 0 := by
  have h2 : ubound cs a b < 0 := of_decide_eq_true (by simpa [gateNeg] using h)
  have h3 : ((ubound cs a b : Rat) : ℝ) < 0 := by exact_mod_cast h2
  have h1 := uniRAux_le_ubAux ha hax hxb cs 0
  rw [uniR]
  rw [ubound] at h3
  linarith

/-! ## The composed statement -/

/-- The certificate identity, over ℝ, at an arbitrary 13-tuple. -/
theorem identity_real :
    eval lhsPoly (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S)
      = eval rhsPoly (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S) :=
  eval_eq_of_isZero_sub cidl_identity _

theorem eval_rhsPoly :
    eval rhsPoly (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S)
      = uniR Data.eC t * (uniR Data.deltaC t) ^ 8 * octicR S := by
  rw [rhsPoly, eval_pmul, eval_pmul, eval_ppow, eval_tUniToPoly, eval_tUniToPoly,
    eval_sUniToPoly, octicR]

/-- **CIDL-LEAN, composed.**  If the 13 A22 contact generators (rebuilt in `CidlGen`
from the A22 corner/edge conventions) all vanish at a real tuple whose tilt parameter
lies in the gate interval `[3/10, 2/5]`, then the canonical Trump octic vanishes at the
tuple's side coordinate.  This is `certs/verify_cidl.py`'s "What a PASS proves". -/
theorem octic_zero_of_generators
    (hg : ∀ g ∈ gens, eval g (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S) = 0)
    (ht₀ : (3 / 10 : ℝ) ≤ t) (ht₁ : t ≤ 2 / 5) : octicR S = 0 := by
  have hlhs : eval lhsPoly (pt13 t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S) = 0 := by
    rw [lhsPoly]
    exact eval_zipWith_pmulRaw_eq_zero _ _ _ hg
  have hid := identity_real t y4 x6 y6 x7 y7 x8 y8 x9 y9 x10 y10 S
  rw [hlhs, eval_rhsPoly] at hid
  have hga : (0 : ℝ) ≤ ((gateA : Rat) : ℝ) := by rw [gateA]; norm_num
  have hat : ((gateA : Rat) : ℝ) ≤ t := by rw [gateA]; push_cast; linarith
  have htb : t ≤ ((gateB : Rat) : ℝ) := by rw [gateB]; push_cast; linarith
  have he : uniR Data.eC t < 0 := uniR_neg_of_gateNeg cidl_gate_e hga hat htb
  have hd : uniR Data.deltaC t < 0 := uniR_neg_of_gateNeg cidl_gate_delta hga hat htb
  have hd8 : (uniR Data.deltaC t) ^ 8 ≠ 0 := pow_ne_zero 8 (ne_of_lt hd)
  rcases mul_eq_zero.mp hid.symm with h | h
  · rcases mul_eq_zero.mp h with h' | h'
    · exact absurd h' (ne_of_lt he)
    · exact absurd h' hd8
  · exact h

end

end Cidl
end PackingCert
