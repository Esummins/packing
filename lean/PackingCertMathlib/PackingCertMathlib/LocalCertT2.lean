import PackingCertMathlib.LocalCertT
import PackingCertMathlib.SatInterior

/-!
# `CertCover`'s remaining pieces, reflected over ℚ — A134 T2

`LocalCertT.lean` (A133) removed the obstacle A126 named (a certified `cos`/`sin`/`π` interval
kernel: in `t = tan(θ/2)` it is not needed at all) and discharged **(C1)** the tilt cover.  Three
pieces of `LocalCert.CertCover` remained, all of them pure reflection over rational data:

* **(C2) the selection cover** — every near pair's recorded selection list is exhaustive, i.e.
  the selections NOT listed have `g_σ < 0` on the cell;
* **(C3) Lemma RELAX** — each emitted row is implied by the geometry on its cell;
* **(C4) the variable map** — the certificate's LP variables against `Local.Box`'s coordinates.

This file supplies the arithmetic each of them consumes, in the same style as `LocalCertT.lean`:
a decidable check on rational certificate data plus one soundness theorem, no transcendental
content, no `sorry`.

* **§1 subdivided positivity.**  `posCheck` decides `p ≥ 0` on ONE interval; the generator's
  envelope search is sharpened by bisection, so the certificate is a CHAIN of intervals laid end
  to end.  `posChain` / `posChain_sound`.
* **§2 the bivariate positivity certificate.**  `w`'s two smooth branches are bounded below by
  planes in `(t_w, t_o)`, so the residual is a polynomial in TWO variables.  `posAux2` is the same
  recursion as `posAux` with polynomial coefficients, so `posCheck2_sound` needs no new idea.
* **§3 the degenerate side.**  A pin's tilt cell is the single point `t = 0`; substituting it
  (`substX0` / `substY0`) turns the bivariate test into a univariate one.
* **§4 the four envelope polynomials** — the wall chord `h`, the two-sided enclosure of
  `sin(θ(t) − θ(t*))`, and `w`'s two branches — each with the identity that turns its positivity
  certificate into the inequality Lemma RELAX uses.
* **§5 (C3) Lemma RELAX**, row family by row family.
* **§6 (C2) the selection cover**: the exact interval enclosure of `g_σ` over a cell.
* **§7 (C4) the variable map**.
* **§8 what is assembled and what is not** — read this before using the file.
-/

namespace PackingCert
namespace S11
namespace LocalCertT2

open Set
open PackingCert.S11.LocalCert
open PackingCert.S11.LocalCertT

/-! ## 1. Zero padding and the subdivided positivity certificate

`posCheck p c a b` compares LISTS: `posAux a b c (c.length - 1)` must equal `p` on the nose.  In
Lean's `pmul`, only the FIRST argument's `[]` short-circuits, so `posAux` leaves exactly one
trailing zero beyond the degree; every envelope polynomial below is therefore defined through
`padZ`, which pads it to the shape `posAux` produces.  (`attempts/A134-certcover-close/code/
leanpoly.py` mirrors these recursions so the generator emits certificates in this exact shape.) -/

/-- The all-zero polynomial of a given length. -/
def zpad : Nat → Poly
  | 0 => []
  | n + 1 => 0 :: zpad n

theorem peval_zpad (n : Nat) (x : ℝ) : peval (zpad n) x = 0 := by
  induction n with
  | zero => simp [zpad, peval]
  | succ n ih => simp [zpad, peval, ih]

/-- Pad `p` with trailing zeros to length at least `n`. -/
def padZ (n : Nat) (p : Poly) : Poly := padd p (zpad n)

theorem peval_padZ (n : Nat) (p : Poly) (x : ℝ) : peval (padZ n p) x = peval p x := by
  simp [padZ, peval_padd, peval_zpad]

/-- **The subdivided positivity certificate.**  A chain of intervals laid end to end from `a` to
`b`, each with its own `posCheck` certificate for the SAME polynomial. -/
def posChain (p : Poly) : List (ℚ × ℚ × Poly) → ℚ → ℚ → Bool
  | [], _, _ => false
  | (a', b', c) :: t, a, b =>
      (a' == a) && posCheck p c a' b' && ((b' == b) || posChain p t b' b)

/-- **Soundness of the chain.**  Every point of `[a, b]` lies in one piece. -/
theorem posChain_sound {p : Poly} :
    ∀ (pcs : List (ℚ × ℚ × Poly)) (a b : ℚ) (x : ℝ),
      posChain p pcs a b = true → (a : ℝ) ≤ x → x ≤ (b : ℝ) → 0 ≤ peval p x := by
  intro pcs
  induction pcs with
  | nil => intro a b x h _ _; simp [posChain] at h
  | cons hd t ih =>
    intro a b x h h1 h2
    obtain ⟨a', b', c⟩ := hd
    simp only [posChain, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq] at h
    obtain ⟨⟨ha, hc⟩, hend⟩ := h
    subst ha
    rcases le_total x ((b' : ℝ)) with hx | hx
    · exact posCheck_sound hc h1 hx
    · rcases hend with hb | hrest
      · subst hb
        exact posCheck_sound hc h1 h2
      · exact ih b' b x hrest hx h2

/-! ## 2. The bivariate positivity certificate

A bivariate polynomial is a `List Poly`: `P[i]` is the coefficient list in `Y` of `X^i`.  The
certificate is `C : List Poly` of NONNEGATIVE rationals with

    P(X, Y) = Σ_i (X − a)^i (b − X)^{m−i} · Q_i(Y),   Q_i(Y) = Σ_j C[i][j] (Y − c)^j (d − Y)^{n−j},

i.e. `posAux`'s recursion run once with polynomial coefficients and once with rational ones.  So
`posCheck2_sound` is `posAux_nonneg` applied inside `posAux_nonneg`'s own induction. -/

def padd2 : List Poly → List Poly → List Poly
  | [], q => q
  | p, [] => p
  | a :: p, b :: q => padd a b :: padd2 p q

def pscale2 (c : ℚ) (P : List Poly) : List Poly := P.map (pscale c)

def pmul2 : List Poly → List Poly → List Poly
  | [], _ => []
  | a :: p, q => padd2 (q.map (pmul a)) ([] :: pmul2 p q)

/-- `peval2 P x y = Σ_i x^i · P[i](y)`. -/
def peval2 : List Poly → ℝ → ℝ → ℝ
  | [], _, _ => 0
  | q :: t, x, y => peval q y + x * peval2 t x y

theorem peval2_padd2 (P R : List Poly) (x y : ℝ) :
    peval2 (padd2 P R) x y = peval2 P x y + peval2 R x y := by
  induction P generalizing R with
  | nil => simp [padd2, peval2]
  | cons a P ih =>
    cases R with
    | nil => simp [padd2, peval2]
    | cons b R => simp only [padd2, peval2, peval_padd, ih]; ring

theorem peval2_map_pscale (c : ℚ) (P : List Poly) (x y : ℝ) :
    peval2 (P.map (pscale c)) x y = (c : ℝ) * peval2 P x y := by
  induction P with
  | nil => simp [peval2]
  | cons a P ih => simp only [List.map_cons, peval2, peval_pscale, ih]; ring

theorem peval2_pscale2 (c : ℚ) (P : List Poly) (x y : ℝ) :
    peval2 (pscale2 c P) x y = (c : ℝ) * peval2 P x y := peval2_map_pscale c P x y

theorem peval2_map_pmul (a : Poly) (R : List Poly) (x y : ℝ) :
    peval2 (R.map (pmul a)) x y = peval a y * peval2 R x y := by
  induction R with
  | nil => simp [peval2]
  | cons b R ih => simp only [List.map_cons, peval2, peval_pmul, ih]; ring

theorem peval2_pmul2 (P R : List Poly) (x y : ℝ) :
    peval2 (pmul2 P R) x y = peval2 P x y * peval2 R x y := by
  induction P with
  | nil => simp [pmul2, peval2]
  | cons a P ih =>
    simp only [pmul2, peval2_padd2, peval2_map_pmul, peval2, peval, ih]
    ring

/-- `e(X) · Q(Y)` for a univariate `e` in `X` and a univariate `Q` in `Y`. -/
def scaleP (e : Poly) (q : Poly) : List Poly := e.map (fun v => pscale v q)

theorem peval2_scaleP (e q : Poly) (x y : ℝ) :
    peval2 (scaleP e q) x y = peval e x * peval q y := by
  induction e with
  | nil => simp [scaleP, peval2, peval]
  | cons v e ih =>
    simp only [scaleP, List.map_cons, peval2, peval_pscale, peval] at *
    rw [ih]
    ring

/-- `(X − a) · R`. -/
def linAmul2 (a : ℚ) (R : List Poly) : List Poly := padd2 (R.map (pscale (-a))) ([] :: R)

theorem peval2_linAmul2 (a : ℚ) (R : List Poly) (x y : ℝ) :
    peval2 (linAmul2 a R) x y = (x - (a : ℝ)) * peval2 R x y := by
  simp only [linAmul2, peval2_padd2, peval2_map_pscale, peval2, peval]
  push_cast
  ring

/-- `posAux` with POLYNOMIAL coefficients: `Σ_i (X − a)^i (b − X)^{m−i} Q_i(Y)`. -/
def posAuxP (a b : ℚ) : List Poly → Nat → List Poly
  | [], _ => []
  | q :: qs, m => padd2 (scaleP (ppow (linB b) m) q) (linAmul2 a (posAuxP a b qs (m - 1)))

theorem posAuxP_nonneg (a b : ℚ) (qs : List Poly) (x y : ℝ)
    (hq : ∀ q ∈ qs, 0 ≤ peval q y) (m : Nat)
    (h1 : (a : ℝ) ≤ x) (h2 : x ≤ (b : ℝ)) : 0 ≤ peval2 (posAuxP a b qs m) x y := by
  induction qs generalizing m with
  | nil => simp [posAuxP, peval2]
  | cons q qs ih =>
    have hq0 : 0 ≤ peval q y := hq q (List.mem_cons_self ..)
    have hrest := ih (fun r hr => hq r (List.mem_cons_of_mem _ hr)) (m - 1)
    have hb : (0 : ℝ) ≤ (b : ℝ) - x := by linarith
    have ha : (0 : ℝ) ≤ x - (a : ℝ) := by linarith
    have hhead : 0 ≤ peval (ppow (linB b) m) x * peval q y := by
      have : peval (ppow (linB b) m) x = ((b : ℝ) - x) ^ m := by
        rw [peval_ppow, peval_linB]
      rw [this]
      exact mul_nonneg (pow_nonneg hb m) hq0
    simp only [posAuxP, peval2_padd2, peval2_scaleP, peval2_linAmul2]
    nlinarith [mul_nonneg ha hrest]

/-- The bivariate certificate, assembled: the outer sum over `X`, each coefficient the inner
`posAux` over `Y`. -/
def posAux2 (a b c d : ℚ) (C : List Poly) : List Poly :=
  posAuxP a b (C.map (fun cs => posAux c d cs (cs.length - 1))) (C.length - 1)

/-- **The decidable bivariate positivity check.** -/
def posCheck2 (P C : List Poly) (a b c d : ℚ) : Bool :=
  C.all (fun cs => cs.all (fun v => 0 ≤ v)) && (posAux2 a b c d C == P)

/-- **Soundness of the bivariate check.** -/
theorem posCheck2_sound {P C : List Poly} {a b c d : ℚ} (h : posCheck2 P C a b c d = true)
    {x y : ℝ} (h1 : (a : ℝ) ≤ x) (h2 : x ≤ (b : ℝ)) (h3 : (c : ℝ) ≤ y) (h4 : y ≤ (d : ℝ)) :
    0 ≤ peval2 P x y := by
  rw [posCheck2, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at h
  obtain ⟨hc, he⟩ := h
  have hq : ∀ q ∈ C.map (fun cs => posAux c d cs (cs.length - 1)), 0 ≤ peval q y := by
    intro q hqm
    obtain ⟨cs, hcs, rfl⟩ := List.mem_map.mp hqm
    have hcs' : ∀ v ∈ cs, 0 ≤ v := by
      intro v hv
      have := hc cs hcs
      rw [List.all_eq_true] at this
      have := this v hv
      simpa using this
    exact posAux_nonneg c d cs hcs' (cs.length - 1) y h3 h4
  have hkey : 0 ≤ peval2 (posAux2 a b c d C) x y :=
    posAuxP_nonneg a b _ x y hq (C.length - 1) h1 h2
  rw [he] at hkey
  exact hkey

/-- The bivariate chain, subdivided in `X` and, inside each `X`-piece, in `Y`. -/
def posGrid (P : List Poly) : List (ℚ × ℚ × List (ℚ × ℚ × List Poly)) → ℚ → ℚ → ℚ → ℚ → Bool
  | [], _, _, _, _ => false
  | (a', b', ys) :: t, a, b, c, d =>
      (a' == a) && posColumn P ys a' b' c d && ((b' == b) || posGrid P t b' b c d)
where
  /-- one `X`-piece's chain in `Y`. -/
  posColumn (P : List Poly) : List (ℚ × ℚ × List Poly) → ℚ → ℚ → ℚ → ℚ → Bool
  | [], _, _, _, _ => false
  | (c', d', C) :: t, a', b', c, d =>
      (c' == c) && posCheck2 P C a' b' c' d' && ((d' == d) || posColumn P t a' b' d' d)

theorem posColumn_sound {P : List Poly} {a' b' : ℚ} :
    ∀ (ys : List (ℚ × ℚ × List Poly)) (c d : ℚ) (x y : ℝ),
      posGrid.posColumn P ys a' b' c d = true →
      (a' : ℝ) ≤ x → x ≤ (b' : ℝ) → (c : ℝ) ≤ y → y ≤ (d : ℝ) → 0 ≤ peval2 P x y := by
  intro ys
  induction ys with
  | nil => intro c d x y h _ _ _ _; simp [posGrid.posColumn] at h
  | cons hd t ih =>
    intro c d x y h hx1 hx2 hy1 hy2
    obtain ⟨c', d', C⟩ := hd
    simp only [posGrid.posColumn, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq] at h
    obtain ⟨⟨hcc, hchk⟩, hend⟩ := h
    subst hcc
    rcases le_total y ((d' : ℝ)) with hy | hy
    · exact posCheck2_sound hchk hx1 hx2 hy1 hy
    · rcases hend with hd' | hrest
      · subst hd'
        exact posCheck2_sound hchk hx1 hx2 hy1 hy2
      · exact ih d' d x y hrest hx1 hx2 hy hy2

theorem posGrid_sound {P : List Poly} :
    ∀ (g : List (ℚ × ℚ × List (ℚ × ℚ × List Poly))) (a b c d : ℚ) (x y : ℝ),
      posGrid P g a b c d = true →
      (a : ℝ) ≤ x → x ≤ (b : ℝ) → (c : ℝ) ≤ y → y ≤ (d : ℝ) → 0 ≤ peval2 P x y := by
  intro g
  induction g with
  | nil => intro a b c d x y h _ _ _ _; simp [posGrid] at h
  | cons hd t ih =>
    intro a b c d x y h hx1 hx2 hy1 hy2
    obtain ⟨a', b', ys⟩ := hd
    simp only [posGrid, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq] at h
    obtain ⟨⟨ha, hcol⟩, hend⟩ := h
    subst ha
    rcases le_total x ((b' : ℝ)) with hx | hx
    · exact posColumn_sound ys c d x y hcol hx1 hx hy1 hy2
    · rcases hend with hb | hrest
      · subst hb
        exact posColumn_sound ys c d x y hcol hx1 hx2 hy1 hy2
      · exact ih b' b c d x y hrest hx hx2 hy1 hy2

/-! ## 3. The degenerate side: a pin's tilt cell is the point `t = 0`

A `w` envelope whose owner (or whose other body) is a class pin is stated on a box with one side
collapsed to `{0}`, where the Bernstein basis is meaningless.  Substituting the fixed value turns
the test into a univariate one, and the substitution is two `List` operations. -/

/-- `P(X, 0)` — the constant terms of the `Y`-polynomials. -/
def substY0 (P : List Poly) : Poly := P.map (fun p => p.headD 0)

/-- `P(0, Y)` — the `X^0` coefficient. -/
def substX0 (P : List Poly) : Poly := P.headD []

theorem peval_at_zero (p : Poly) : peval p 0 = ((p.headD 0 : ℚ) : ℝ) := by
  cases p with
  | nil => simp [peval]
  | cons a p => simp [peval]

theorem peval_substY0 (P : List Poly) (x : ℝ) : peval (substY0 P) x = peval2 P x 0 := by
  induction P with
  | nil => simp [substY0, peval, peval2]
  | cons q P ih =>
    have e : peval (P.map (fun p : Poly => p.headD 0)) x = peval2 P x 0 := ih
    simp only [substY0, List.map_cons, peval, peval2, peval_at_zero, e]

theorem peval_substX0 (P : List Poly) (y : ℝ) : peval (substX0 P) y = peval2 P 0 y := by
  cases P with
  | nil => simp [substX0, peval, peval2]
  | cons q P => simp [substX0, peval2]

/-! ## 4. The four envelope polynomials

Each affine envelope of Lemma RELAX is "this rational polynomial is `≥ 0` on this rational cell"
after clearing the positive denominator `1 + t²` (resp. `(1 + t_w²)(1 + t_o²)`).  The polynomial
is BUILT here from the envelope's rational constants by the same `padd`/`pscale`/`pmul` calls the
generator mirrors, so one identity lemma per family turns a positivity certificate into the
inequality.  No envelope is trusted: only its constants are read. -/

/-- `hPoly m c = (1 + 2X − X²) − 2 (m X + c)(1 + X²)`; `≥ 0` on a cell iff the chord `m t + c`
lies below the wall half-width `h(t) = w_T(t)/2` there. -/
def hPoly (m c : ℚ) : Poly := padZ 5 (padd [1, 2, -1] (pscale (-2) (pmul [c, m] [1, 0, 1])))

theorem peval_hPoly (m c : ℚ) (t : ℝ) :
    peval (hPoly m c) t = (1 + 2 * t - t ^ 2) - 2 * ((m : ℝ) * t + (c : ℝ)) * (1 + t ^ 2) := by
  simp only [hPoly, peval_padZ, peval_padd, peval_pscale, peval_pmul, peval]
  push_cast
  ring

/-- **The wall envelope.**  `h(t) = (cos θ + sin θ)/2 = w_T t / 2` dominates the certified
chord on the cell.  `Parametrize.set_subset_container_iff` is the consumer: a square inside
`[0, s]²` has `w_T(t)/2 ≤ c ≤ s − w_T(t)/2` in each coordinate. -/
theorem wT_ge_aff {m c a b : ℚ} {pcs : List (ℚ × ℚ × Poly)} {t : ℝ}
    (h : posChain (hPoly m c) pcs a b = true) (h1 : (a : ℝ) ≤ t) (h2 : t ≤ (b : ℝ)) :
    (m : ℝ) * t + (c : ℝ) ≤ wT t / 2 := by
  have hp := posChain_sound pcs a b t h h1 h2
  rw [peval_hPoly] at hp
  have hd : (0 : ℝ) < 1 + t ^ 2 := by positivity
  have hw : wT t / 2 - ((m : ℝ) * t + (c : ℝ))
      = ((1 + 2 * t - t ^ 2) - 2 * ((m : ℝ) * t + (c : ℝ)) * (1 + t ^ 2)) / (2 * (1 + t ^ 2)) := by
    unfold wT cosT sinT
    field_simp
    ring
  have : (0 : ℝ) ≤ wT t / 2 - ((m : ℝ) * t + (c : ℝ)) := by
    rw [hw]
    exact div_nonneg hp (by positivity)
  linarith

/-- The numerator of `S(t) = sin(θ(t) − θ*)` over `1 + t²`, with `cos θ* = cm`, `sin θ* = sm`. -/
def sNum (cm sm : ℚ) : Poly := [-sm, 2 * cm, sm]

def sUpPoly (cm sm alpha beta : ℚ) : Poly :=
  padZ 5 (padd (pmul [beta, alpha] [1, 0, 1]) (pscale (-1) (sNum cm sm)))

def sLoPoly (cm sm alpha beta : ℚ) : Poly :=
  padZ 5 (padd (sNum cm sm) (pscale (-1) (pmul [beta, alpha] [1, 0, 1])))

/-- `S(t) = sin(θ(t) − θ*)` written with the addition formula, so that it is a RATIONAL
function of `t` — the step that needs no series remainder. -/
noncomputable def sRel (cm sm : ℝ) (t : ℝ) : ℝ := sinT t * cm - cosT t * sm

theorem sRel_mul (cm sm : ℚ) (t : ℝ) :
    sRel (cm : ℝ) (sm : ℝ) t * (1 + t ^ 2) = peval (sNum cm sm) t := by
  have hd : (1 + t ^ 2 : ℝ) ≠ 0 := by positivity
  unfold sRel sinT cosT
  simp only [sNum, peval]
  push_cast
  field_simp
  ring

theorem peval_sUpPoly (cm sm alpha beta : ℚ) (t : ℝ) :
    peval (sUpPoly cm sm alpha beta) t
      = ((alpha : ℝ) * t + (beta : ℝ)) * (1 + t ^ 2) - peval (sNum cm sm) t := by
  simp only [sUpPoly, peval_padZ, peval_padd, peval_pscale, peval_pmul, peval, sNum]
  push_cast
  ring

theorem peval_sLoPoly (cm sm alpha beta : ℚ) (t : ℝ) :
    peval (sLoPoly cm sm alpha beta) t
      = peval (sNum cm sm) t - ((alpha : ℝ) * t + (beta : ℝ)) * (1 + t ^ 2) := by
  simp only [sLoPoly, peval_padZ, peval_padd, peval_pscale, peval_pmul, peval, sNum]
  push_cast
  ring

/-- **The upper `S` envelope.** -/
theorem sRel_le_aff {cm sm alpha beta a b : ℚ} {pcs : List (ℚ × ℚ × Poly)} {t : ℝ}
    (h : posChain (sUpPoly cm sm alpha beta) pcs a b = true)
    (h1 : (a : ℝ) ≤ t) (h2 : t ≤ (b : ℝ)) :
    sRel (cm : ℝ) (sm : ℝ) t ≤ (alpha : ℝ) * t + (beta : ℝ) := by
  have hp := posChain_sound pcs a b t h h1 h2
  rw [peval_sUpPoly, ← sRel_mul cm sm t] at hp
  have hd : (0 : ℝ) < 1 + t ^ 2 := by positivity
  nlinarith [hp, hd]

/-- **The lower `S` envelope.** -/
theorem sRel_ge_aff {cm sm alpha beta a b : ℚ} {pcs : List (ℚ × ℚ × Poly)} {t : ℝ}
    (h : posChain (sLoPoly cm sm alpha beta) pcs a b = true)
    (h1 : (a : ℝ) ≤ t) (h2 : t ≤ (b : ℝ)) :
    (alpha : ℝ) * t + (beta : ℝ) ≤ sRel (cm : ℝ) (sm : ℝ) t := by
  have hp := posChain_sound pcs a b t h h1 h2
  rw [peval_sLoPoly, ← sRel_mul cm sm t] at hp
  have hd : (0 : ℝ) < 1 + t ^ 2 := by positivity
  nlinarith [hp, hd]

/-! ### `w`'s two smooth branches as planes in `(t_w, t_o)` -/

def oneTT : List Poly := [[1], [0, 1]]
def diffT : List Poly := [[0, -1], [1]]
def denT : List Poly := [[1, 0, 1], [], [1, 0, 1]]

/-- `(1 + XY)² − (X − Y)² + 2 ε (X − Y)(1 + XY)`, the numerator of
`W_ε = cos Δ − ε sin Δ` over `(1 + X²)(1 + Y²)`. -/
def wNumT (eps : ℚ) : List Poly :=
  padd2 (padd2 (pmul2 oneTT oneTT) (pscale2 (-1) (pmul2 diffT diffT)))
    (pscale2 (2 * eps) (pmul2 diffT oneTT))

/-- `wNumT ε − (mw X + mo Y + c)(1 + X²)(1 + Y²)`; `≥ 0` on the cell product iff the plane lies
below `W_ε` there. -/
def wPolyT (eps mw mo c : ℚ) : List Poly :=
  (padd2 (wNumT eps) (pscale2 (-1) (pmul2 [[c, mo], [mw]] denT))).map (padZ 5)

theorem peval2_map_padZ (n : Nat) (P : List Poly) (x y : ℝ) :
    peval2 (P.map (padZ n)) x y = peval2 P x y := by
  induction P with
  | nil => simp [peval2]
  | cons q P ih => simp only [List.map_cons, peval2, peval_padZ, ih]

theorem peval2_wPolyT (eps mw mo c : ℚ) (x y : ℝ) :
    peval2 (wPolyT eps mw mo c) x y
      = ((1 + x * y) ^ 2 - (x - y) ^ 2 + 2 * (eps : ℝ) * (x - y) * (1 + x * y))
        - ((c : ℝ) + (mo : ℝ) * y + (mw : ℝ) * x) * ((1 + x ^ 2) * (1 + y ^ 2)) := by
  simp only [wPolyT, peval2_map_padZ, wNumT, peval2_padd2, peval2_pscale2, peval2_pmul2,
    oneTT, diffT, denT, peval2, peval]
  push_cast
  ring

/-- The two branches of `w` in the `t` parametrisation: `cosRel ∓ sinRel` over the common
denominator is exactly `wNumT (±1)`. -/
theorem wNum_eq (eps : ℚ) (x y : ℝ) :
    ((1 + x * y) ^ 2 - (x - y) ^ 2 + 2 * (eps : ℝ) * (x - y) * (1 + x * y))
      = (cosRel x y - (eps : ℝ) * sinRel x y) * ((1 + x ^ 2) * (1 + y ^ 2)) := by
  have hx : (1 + x ^ 2 : ℝ) ≠ 0 := by positivity
  have hy : (1 + y ^ 2 : ℝ) ≠ 0 := by positivity
  unfold cosRel sinRel cosT sinT
  field_simp
  ring

/-- **The `w` envelope.**  A certified plane below `W_ε` is a plane below `w = |cos Δ| + |sin Δ|`,
because `w ≥ cos Δ ∓ sin Δ` on the WHOLE cell (`LocalCertT.wrel_ge_sub` / `wrel_ge_add`) — the
step that needed the location of the `π/2` kink in the angle and needs nothing here. -/
theorem wrel_ge_plane {eps mw mo c : ℚ} (heps : eps = 1 ∨ eps = -1) (qw qo : PSq)
    (hnn : 0 ≤ peval2 (wPolyT eps mw mo c) qw.t qo.t) :
    (mw : ℝ) * qw.t + (mo : ℝ) * qo.t + (c : ℝ) ≤ wrel qw qo := by
  rw [peval2_wPolyT, wNum_eq] at hnn
  have hd : (0 : ℝ) < (1 + qw.t ^ 2) * (1 + qo.t ^ 2) := by positivity
  have hbr : (mw : ℝ) * qw.t + (mo : ℝ) * qo.t + (c : ℝ)
      ≤ cosRel qw.t qo.t - (eps : ℝ) * sinRel qw.t qo.t := by
    nlinarith [hnn, hd]
  rcases heps with rfl | rfl
  · have := wrel_ge_sub qw qo
    push_cast at hbr
    linarith
  · have := wrel_ge_add qw qo
    push_cast at hbr
    linarith

/-! ## 5. Rational intervals

(C2) is an interval computation: the enclosure of `g_σ` over a cell.  In `t` every ingredient is
EXACT — `cosT` is antitone and `sinT` monotone, so their ranges are the endpoint values
(`LocalCertT.cosT_mem` / `sinT_mem`) — so the only enclosure error is the one interval
multiplication introduces, and the whole computation is decidable over ℚ. -/

/-- A closed interval with rational endpoints. -/
structure IQ where
  lo : ℚ
  hi : ℚ
deriving Inhabited, Repr, DecidableEq

/-- `x` lies in the interval. -/
def IQ.mem (i : IQ) (x : ℝ) : Prop := (i.lo : ℝ) ≤ x ∧ x ≤ (i.hi : ℝ)

def IQ.const (c : ℚ) : IQ := ⟨c, c⟩
def IQ.add (a b : IQ) : IQ := ⟨a.lo + b.lo, a.hi + b.hi⟩
def IQ.sub (a b : IQ) : IQ := ⟨a.lo - b.hi, a.hi - b.lo⟩
def IQ.neg (a : IQ) : IQ := ⟨-a.hi, -a.lo⟩

/-- The four corner products, associated so that the soundness proof is two `max_le_max`s. -/
def IQ.mul (a b : IQ) : IQ :=
  ⟨min (min (a.lo * b.lo) (a.hi * b.lo)) (min (a.lo * b.hi) (a.hi * b.hi)),
   max (max (a.lo * b.lo) (a.hi * b.lo)) (max (a.lo * b.hi) (a.hi * b.hi))⟩

theorem IQ.const_mem (c : ℚ) : (IQ.const c).mem (c : ℝ) := ⟨le_rfl, le_rfl⟩

theorem IQ.add_mem {a b : IQ} {x y : ℝ} (hx : a.mem x) (hy : b.mem y) : (a.add b).mem (x + y) := by
  obtain ⟨h1, h2⟩ := hx; obtain ⟨h3, h4⟩ := hy
  constructor <;> · simp only [IQ.add]; push_cast; linarith

theorem IQ.sub_mem {a b : IQ} {x y : ℝ} (hx : a.mem x) (hy : b.mem y) : (a.sub b).mem (x - y) := by
  obtain ⟨h1, h2⟩ := hx; obtain ⟨h3, h4⟩ := hy
  constructor <;> · simp only [IQ.sub]; push_cast; linarith

theorem IQ.neg_mem {a : IQ} {x : ℝ} (hx : a.mem x) : a.neg.mem (-x) := by
  obtain ⟨h1, h2⟩ := hx
  constructor <;> · simp only [IQ.neg]; push_cast; linarith

private theorem mul_le_max_r {x u v y : ℝ} (h1 : u ≤ y) (h2 : y ≤ v) :
    x * y ≤ max (x * u) (x * v) := by
  rcases le_total 0 x with h | h
  · exact le_trans (by nlinarith) (le_max_right _ _)
  · exact le_trans (by nlinarith) (le_max_left _ _)

private theorem min_le_mul_r {x u v y : ℝ} (h1 : u ≤ y) (h2 : y ≤ v) :
    min (x * u) (x * v) ≤ x * y := by
  rcases le_total 0 x with h | h
  · exact le_trans (min_le_left _ _) (by nlinarith)
  · exact le_trans (min_le_right _ _) (by nlinarith)

private theorem mul_le_max_l {y u v x : ℝ} (h1 : u ≤ x) (h2 : x ≤ v) :
    x * y ≤ max (u * y) (v * y) := by
  have := mul_le_max_r (x := y) h1 h2
  rw [mul_comm x y]
  calc y * x ≤ max (y * u) (y * v) := this
    _ = max (u * y) (v * y) := by rw [mul_comm y u, mul_comm y v]

private theorem min_le_mul_l {y u v x : ℝ} (h1 : u ≤ x) (h2 : x ≤ v) :
    min (u * y) (v * y) ≤ x * y := by
  have := min_le_mul_r (x := y) h1 h2
  rw [mul_comm x y]
  calc min (u * y) (v * y) = min (y * u) (y * v) := by rw [mul_comm y u, mul_comm y v]
    _ ≤ y * x := this

theorem IQ.mul_mem {a b : IQ} {x y : ℝ} (hx : a.mem x) (hy : b.mem y) : (a.mul b).mem (x * y) := by
  obtain ⟨h1, h2⟩ := hx
  obtain ⟨h3, h4⟩ := hy
  constructor
  · simp only [IQ.mul]
    push_cast
    refine le_trans (min_le_min ?_ ?_) (min_le_mul_r h3 h4)
    · exact min_le_mul_l h1 h2
    · exact min_le_mul_l h1 h2
  · simp only [IQ.mul]
    push_cast
    refine le_trans (mul_le_max_r h3 h4) (max_le_max ?_ ?_)
    · exact mul_le_max_l h1 h2
    · exact mul_le_max_l h1 h2

/-! ### `cosT` and `sinT` over a rational cell, exactly -/

def cosTQ (t : ℚ) : ℚ := (1 - t ^ 2) / (1 + t ^ 2)
def sinTQ (t : ℚ) : ℚ := 2 * t / (1 + t ^ 2)

theorem cosTQ_cast (t : ℚ) : ((cosTQ t : ℚ) : ℝ) = cosT (t : ℝ) := by
  unfold cosTQ cosT
  push_cast
  ring

theorem sinTQ_cast (t : ℚ) : ((sinTQ t : ℚ) : ℝ) = sinT (t : ℝ) := by
  unfold sinTQ sinT
  push_cast
  ring

/-- The EXACT range of `cos θ` over a tilt cell: the endpoint values, reversed. -/
def cosI (c : IQ) : IQ := ⟨cosTQ c.hi, cosTQ c.lo⟩

/-- The EXACT range of `sin θ` over a tilt cell: the endpoint values. -/
def sinI (c : IQ) : IQ := ⟨sinTQ c.lo, sinTQ c.hi⟩

theorem cosI_mem {c : IQ} {t : ℝ} (h0 : (0 : ℚ) ≤ c.lo) (h : c.mem t) : (cosI c).mem (cosT t) := by
  obtain ⟨h1, h2⟩ := h
  have h0' : (0 : ℝ) ≤ (c.lo : ℝ) := by exact_mod_cast h0
  obtain ⟨ha, hb⟩ := cosT_mem h0' h1 h2
  exact ⟨by rw [cosI, cosTQ_cast]; exact ha, by rw [cosI, cosTQ_cast]; exact hb⟩

theorem sinI_mem {c : IQ} {t : ℝ} (h0 : (0 : ℚ) ≤ c.lo) (h1 : c.hi ≤ 1) (h : c.mem t) :
    (sinI c).mem (sinT t) := by
  obtain ⟨ha, hb⟩ := h
  have h0' : (0 : ℝ) ≤ (c.lo : ℝ) := by exact_mod_cast h0
  have h1' : ((c.hi : ℚ) : ℝ) ≤ 1 := by exact_mod_cast h1
  obtain ⟨hx, hy⟩ := sinT_mem h0' ha hb h1'
  exact ⟨by rw [sinI, sinTQ_cast]; exact hx, by rw [sinI, sinTQ_cast]; exact hy⟩

/-- The owner's axis `a_k(θ)` over a tilt cell. -/
def axI (c : IQ) (k : Bool) : IQ × IQ :=
  if k then ((sinI c).neg, cosI c) else (cosI c, sinI c)

theorem axI_mem {c : IQ} {q : PSq} (h0 : (0 : ℚ) ≤ c.lo) (h1 : c.hi ≤ 1) (h : c.mem q.t)
    (k : Bool) : (axI c k).1.mem (axk q k).1 ∧ (axI c k).2.mem (axk q k).2 := by
  cases k
  · exact ⟨cosI_mem h0 h, sinI_mem h0 h1 h⟩
  · exact ⟨IQ.neg_mem (sinI_mem h0 h1 h), cosI_mem h0 h⟩

/-! ### The support width from below, without the kink -/

def cosRelI (a b : IQ) : IQ := ((cosI a).mul (cosI b)).add ((sinI a).mul (sinI b))
def sinRelI (a b : IQ) : IQ := ((cosI a).mul (sinI b)).sub ((sinI a).mul (cosI b))

theorem cosRelI_mem {a b : IQ} {x y : ℝ} (ha0 : (0 : ℚ) ≤ a.lo) (ha1 : a.hi ≤ 1)
    (hb0 : (0 : ℚ) ≤ b.lo) (hb1 : b.hi ≤ 1) (hx : a.mem x) (hy : b.mem y) :
    (cosRelI a b).mem (cosRel x y) :=
  IQ.add_mem (IQ.mul_mem (cosI_mem ha0 hx) (cosI_mem hb0 hy))
    (IQ.mul_mem (sinI_mem ha0 ha1 hx) (sinI_mem hb0 hb1 hy))

theorem sinRelI_mem {a b : IQ} {x y : ℝ} (ha0 : (0 : ℚ) ≤ a.lo) (ha1 : a.hi ≤ 1)
    (hb0 : (0 : ℚ) ≤ b.lo) (hb1 : b.hi ≤ 1) (hx : a.mem x) (hy : b.mem y) :
    (sinRelI a b).mem (sinRel x y) :=
  IQ.sub_mem (IQ.mul_mem (cosI_mem ha0 hx) (sinI_mem hb0 hb1 hy))
    (IQ.mul_mem (sinI_mem ha0 ha1 hx) (cosI_mem hb0 hy))

/-- **A rational lower bound of `w = |cos Δ| + |sin Δ|` over a cell product.**  `w` is the MAXIMUM
of its two smooth branches (`LocalCertT.wrel_eq_max_of_cos_nonneg`), so bounding each branch below
by interval arithmetic on `cosRel` and `sinRel` is sharp up to the interval widths — and needs
neither the kink of `w` nor `π`. -/
def wLoQ (a b : IQ) : ℚ :=
  max ((cosRelI a b).lo + (sinRelI a b).lo) ((cosRelI a b).lo - (sinRelI a b).hi)

theorem wLoQ_le {a b : IQ} {qw qo : PSq} (ha0 : (0 : ℚ) ≤ a.lo) (ha1 : a.hi ≤ 1)
    (hb0 : (0 : ℚ) ≤ b.lo) (hb1 : b.hi ≤ 1) (hx : a.mem qw.t) (hy : b.mem qo.t) :
    ((wLoQ a b : ℚ) : ℝ) ≤ wrel qw qo := by
  obtain ⟨hc1, hc2⟩ := cosRelI_mem ha0 ha1 hb0 hb1 hx hy
  obtain ⟨hs1, hs2⟩ := sinRelI_mem ha0 ha1 hb0 hb1 hx hy
  have hadd := wrel_ge_add qw qo
  have hsub := wrel_ge_sub qw qo
  rw [wLoQ]
  push_cast
  rcases le_total (((cosRelI a b).lo : ℝ) + ((sinRelI a b).lo : ℝ))
    (((cosRelI a b).lo : ℝ) - ((sinRelI a b).hi : ℝ)) with h | h
  · rw [max_eq_right h]; linarith
  · rw [max_eq_left h]; linarith

/-! ## 6. (C2) The selection cover

The enclosure of the signed separating-axis row `g_σ` over a cell, and the case split it
justifies.  `gapHi` is a rational UPPER bound of `g_σ`; a selection whose `gapHi` is `< 0` cannot
be the one Lemma SAT provides, so the recorded selections are exhaustive. -/

/-- The certificate data one pair's enclosure is computed from: the two bodies' centre intervals
(for a pin, already widened over the `s` window) and their tilt cells. -/
structure PairBox where
  xw : IQ
  yw : IQ
  tw : IQ
  xo : IQ
  yo : IQ
  tb : IQ

/-- The tilt cells lie in the fundamental domain. -/
def PairBox.ok (pb : PairBox) : Prop :=
  (0 : ℚ) ≤ pb.tw.lo ∧ pb.tw.hi ≤ 1 ∧ (0 : ℚ) ≤ pb.tb.lo ∧ pb.tb.hi ≤ 1

/-- A configuration of the pair inside the box. -/
def PairBox.holds (pb : PairBox) (qw qo : PSq) : Prop :=
  pb.xw.mem qw.cx ∧ pb.yw.mem qw.cy ∧ pb.tw.mem qw.t ∧
    pb.xo.mem qo.cx ∧ pb.yo.mem qo.cy ∧ pb.tb.mem qo.t

/-- **The enclosure of `g_σ` from above.** -/
def gapHi (pb : PairBox) (k : Bool) (eps : ℚ) : ℚ :=
  (((IQ.const eps).mul
      ((((pb.xo.sub pb.xw).mul (axI pb.tw k).1)).add
        ((pb.yo.sub pb.yw).mul (axI pb.tw k).2))).hi)
    - 1 / 2 - wLoQ pb.tw pb.tb / 2

theorem gsel_le_gapHi {pb : PairBox} {qw qo : PSq} (hok : pb.ok) (hh : pb.holds qw qo)
    (k : Bool) (eps : ℚ) : gsel qw qo k (eps : ℝ) ≤ ((gapHi pb k eps : ℚ) : ℝ) := by
  obtain ⟨ha0, ha1, hb0, hb1⟩ := hok
  obtain ⟨hxw, hyw, htw, hxo, hyo, hto⟩ := hh
  obtain ⟨hax, hay⟩ := axI_mem (q := qw) ha0 ha1 htw k
  have hprod :=
    IQ.mul_mem (IQ.const_mem eps)
      (IQ.add_mem (IQ.mul_mem (IQ.sub_mem hxo hxw) hax) (IQ.mul_mem (IQ.sub_mem hyo hyw) hay))
  have hw := wLoQ_le (qw := qw) (qo := qo) ha0 ha1 hb0 hb1 htw hto
  rw [gsel, gapHi]
  push_cast
  push_cast at hprod
  linarith [hprod.2, hw]

/-- **(C2), the logical half.**  If every selection outside the recorded list is impossible on the
cell, an interior-disjoint pair uses one of the recorded ones.  `SatInterior.sat_selection_thm`
is the input; the eight selections are `(swap owner, axis, sign)`. -/
theorem selection_cover (qw qo : PSq) (hd : Disjoint (interior qw.set) (interior qo.set))
    (sels : List (Bool × Bool × ℚ))
    (hexc : ∀ (o k : Bool) (e : ℚ), (e = 1 ∨ e = -1) → (o, k, e) ∉ sels →
      (if o then gsel qo qw k (e : ℝ) else gsel qw qo k (e : ℝ)) < 0) :
    ∃ p ∈ sels, 0 ≤ (if p.1 then gsel qo qw p.2.1 ((p.2.2 : ℚ) : ℝ)
                     else gsel qw qo p.2.1 ((p.2.2 : ℚ) : ℝ)) := by
  have key : ∀ (o : Bool) (k : Bool) (e : ℚ), (e = 1 ∨ e = -1) →
      0 ≤ (if o then gsel qo qw k (e : ℝ) else gsel qw qo k (e : ℝ)) →
      ∃ p ∈ sels, 0 ≤ (if p.1 then gsel qo qw p.2.1 ((p.2.2 : ℚ) : ℝ)
                       else gsel qw qo p.2.1 ((p.2.2 : ℚ) : ℝ)) := by
    intro o k e he hge
    by_cases hm : (o, k, e) ∈ sels
    · exact ⟨(o, k, e), hm, hge⟩
    · exact absurd hge (not_le.mpr (hexc o k e he hm))
  rcases sat_selection_thm qw qo hd with ⟨k, e, he, hg⟩ | ⟨k, e, he, hg⟩
  · rcases he with rfl | rfl
    · exact key false k 1 (Or.inl rfl) (by simpa using hg)
    · exact key false k (-1) (Or.inr rfl) (by push_cast; simpa using hg)
  · rcases he with rfl | rfl
    · exact key true k 1 (Or.inl rfl) (by simpa using hg)
    · exact key true k (-1) (Or.inr rfl) (by push_cast; simpa using hg)

/-- The mirrored `PairBox` (the two bodies swapped), so that one enclosure function serves both
orientations of a selection. -/
def PairBox.swap (pb : PairBox) : PairBox := ⟨pb.xo, pb.yo, pb.tb, pb.xw, pb.yw, pb.tw⟩

theorem PairBox.swap_ok {pb : PairBox} (h : pb.ok) : pb.swap.ok := ⟨h.2.2.1, h.2.2.2, h.1, h.2.1⟩

theorem PairBox.swap_holds {pb : PairBox} {qw qo : PSq} (h : pb.holds qw qo) :
    pb.swap.holds qo qw := ⟨h.2.2.2.1, h.2.2.2.2.1, h.2.2.2.2.2, h.1, h.2.1, h.2.2.1⟩

/-- **The decidable selection check.**  Every one of the eight selections that is NOT recorded has
a strictly negative enclosure on the cell. -/
def selectionOk (pb : PairBox) (sels : List (Bool × Bool × ℚ)) : Bool :=
  ([(false, false, (1 : ℚ)), (false, false, -1), (false, true, 1), (false, true, -1),
    (true, false, 1), (true, false, -1), (true, true, 1), (true, true, -1)] :
      List (Bool × Bool × ℚ)).all
    (fun p => decide (p ∈ sels) ||
      decide (gapHi (if p.1 then pb.swap else pb) p.2.1 p.2.2 < 0))

/-- **(C2) DISCHARGED.**  A passing selection check plus interior-disjointness gives a recorded
selection whose row holds — exactly `Local.cover_selection`'s hypothesis, decided on the
certificate's own rational cell data. -/
theorem selectionOk_sound {pb : PairBox} {qw qo : PSq} {sels : List (Bool × Bool × ℚ)}
    (hok : pb.ok) (hh : pb.holds qw qo)
    (hd : Disjoint (interior qw.set) (interior qo.set))
    (hchk : selectionOk pb sels = true) :
    ∃ p ∈ sels, 0 ≤ (if p.1 then gsel qo qw p.2.1 ((p.2.2 : ℚ) : ℝ)
                     else gsel qw qo p.2.1 ((p.2.2 : ℚ) : ℝ)) := by
  refine selection_cover qw qo hd sels ?_
  intro o k e he hm
  rw [selectionOk, List.all_eq_true] at hchk
  have hmem : (o, k, e) ∈ [(false, false, (1 : ℚ)), (false, false, -1), (false, true, 1),
      (false, true, -1), (true, false, 1), (true, false, -1), (true, true, 1), (true, true, -1)] := by
    rcases he with rfl | rfl <;> cases o <;> cases k <;> simp
  have h := hchk _ hmem
  simp only [Bool.or_eq_true, decide_eq_true_eq] at h
  rcases h with h | h
  · exact absurd h hm
  · have hlt : ((gapHi (if o then pb.swap else pb) k e : ℚ) : ℝ) < 0 := by exact_mod_cast h
    cases o
    · simpa using lt_of_le_of_lt (gsel_le_gapHi (qw := qw) (qo := qo) hok hh k e) (by simpa using hlt)
    · have := gsel_le_gapHi (pb := pb.swap) (qw := qo) (qo := qw) (PairBox.swap_ok hok)
        (PairBox.swap_holds hh) k e
      simp only [if_true] at hlt ⊢
      linarith

/-! ## 7. (C3) Lemma RELAX

Every emitted row belongs to one of two families, and each is IMPLIED by the geometry on its
cell.  The two soundness statements below are Lemma RELAX itself; each ingredient they consume is
either a positivity certificate (§4) or an already-proved lemma of `Local.lean`. -/

/-- **The wall rows.**  A square inside `[0, s]²` has `w_T(t)/2 ≤ c ≤ s − w_T(t)/2` in each
coordinate (`Parametrize.set_subset_container_iff`), and the certified chord lies below
`w_T(t)/2`, so both emitted rows hold. -/
theorem relax_wall {m c a b : ℚ} {pcs : List (ℚ × ℚ × Poly)} {q : PSq} {s : ℝ}
    (hcert : posChain (hPoly m c) pcs a b = true)
    (ha : (a : ℝ) ≤ q.t) (hb : q.t ≤ (b : ℝ)) (h0 : 0 ≤ q.t) (h1 : q.t ≤ 1)
    (hsub : q.set ⊆ container s) :
    (-q.cx + ((m : ℝ) * q.t + (c : ℝ)) ≤ 0 ∧ q.cx - s + ((m : ℝ) * q.t + (c : ℝ)) ≤ 0) ∧
    (-q.cy + ((m : ℝ) * q.t + (c : ℝ)) ≤ 0 ∧ q.cy - s + ((m : ℝ) * q.t + (c : ℝ)) ≤ 0) := by
  have hch := wT_ge_aff hcert ha hb
  obtain ⟨hx0, hx1, hy0, hy1⟩ := (set_subset_container_iff h0 h1 s).mp hsub
  exact ⟨⟨by linarith, by linarith⟩, ⟨by linarith, by linarith⟩⟩

/-- **The exact axis decomposition in `t`** (`Local.axis_decomp` without any angle): with
`C = cos φ`, `S = sin φ` and `φ = θ(t_w) − θ(t*)`, the owner's projection is `P C + Q S` for the
two affine forms `P`, `Q` of the certificate.  `cosRel` / `sRel` ARE `C` and `S`. -/
theorem axis_decomp_t (qw qo : PSq) (tm : ℝ) (k : Bool) (eps dx dy : ℝ)
    (hdx : dx = qo.cx - qw.cx) (hdy : dy = qo.cy - qw.cy) :
    eps * (dx * (axk ⟨0, 0, tm⟩ k).1 + dy * (axk ⟨0, 0, tm⟩ k).2) * cosRel qw.t tm
      + eps * (-(dx * (axk ⟨0, 0, tm⟩ k).2) + dy * (axk ⟨0, 0, tm⟩ k).1)
          * sRel (cosT tm) (sinT tm) qw.t
      = eps * (dx * (axk qw k).1 + dy * (axk qw k).2) := by
  have hm := cosT_sq_add_sinT_sq tm
  have hc : cosRel qw.t tm = cosT qw.t * cosT tm + sinT qw.t * sinT tm := rfl
  have hs : sRel (cosT tm) (sinT tm) qw.t = sinT qw.t * cosT tm - cosT qw.t * sinT tm := rfl
  rw [hc, hs]
  cases k
  · simp only [axk, Bool.false_eq_true, if_false]
    linear_combination (eps * (dx * cosT qw.t + dy * sinT qw.t)) * hm
  · simp only [axk, if_true]
    linear_combination (eps * (dx * -sinT qw.t + dy * cosT qw.t)) * hm

/-- `|cos φ| ≤ 1` in the `t` parametrisation — the bound that makes `1 − C ≥ 0`. -/
theorem cosRel_le_one (x y : ℝ) : cosRel x y ≤ 1 := by
  have hx := cosT_sq_add_sinT_sq x
  have hy := cosT_sq_add_sinT_sq y
  have hc : cosRel x y = cosT x * cosT y + sinT x * sinT y := rfl
  have key : (cosT x * cosT y + sinT x * sinT y) ^ 2 + (cosT x * sinT y - sinT x * cosT y) ^ 2
      = 1 := by
    have e : (cosT x * cosT y + sinT x * sinT y) ^ 2 + (cosT x * sinT y - sinT x * cosT y) ^ 2
        = (cosT x ^ 2 + sinT x ^ 2) * (cosT y ^ 2 + sinT y ^ 2) := by ring
    rw [e, hx, hy]; norm_num
  rw [hc]
  nlinarith [sq_nonneg (cosT x * sinT y - sinT x * cosT y), key]

/-- `(K − 1)(1 + X²) + cm (1 − X²) + 2 sm X`; `≥ 0` on the cell iff `1 − cos φ ≤ K` there. -/
def cPoly (cm sm K : ℚ) : Poly :=
  padZ 5 (padd (pscale (K - 1) [1, 0, 1]) (padd (pscale cm [1, 0, -1]) [0, 2 * sm]))

theorem peval_cPoly (cm sm K : ℚ) (t : ℝ) :
    peval (cPoly cm sm K) t
      = ((K : ℝ) - 1) * (1 + t ^ 2) + (cm : ℝ) * (1 - t ^ 2) + 2 * (sm : ℝ) * t := by
  simp only [cPoly, peval_padZ, peval_padd, peval_pscale, peval]
  push_cast
  ring

/-- **The correction term.**  `1 − cos φ ≤ K` on the cell, certified. -/
theorem one_sub_cosRel_le {cm sm K a b : ℚ} {pcs : List (ℚ × ℚ × Poly)} {t tm : ℝ}
    (hcm : (cm : ℝ) = cosT tm) (hsm : (sm : ℝ) = sinT tm)
    (hcert : posChain (cPoly cm sm K) pcs a b = true)
    (ha : (a : ℝ) ≤ t) (hb : t ≤ (b : ℝ)) :
    1 - cosRel t tm ≤ (K : ℝ) := by
  have hp := posChain_sound pcs a b t hcert ha hb
  rw [peval_cPoly] at hp
  have hd : (0 : ℝ) < 1 + t ^ 2 := by positivity
  have hc : cosRel t tm = ((cm : ℝ) * (1 - t ^ 2) + 2 * (sm : ℝ) * t) / (1 + t ^ 2) := by
    rw [hcm, hsm]
    unfold cosRel cosT sinT
    field_simp
    try ring
  have : (0 : ℝ) ≤ (K : ℝ) - (1 - cosRel t tm) := by
    rw [hc]
    have e : (K : ℝ) - (1 - ((cm : ℝ) * (1 - t ^ 2) + 2 * (sm : ℝ) * t) / (1 + t ^ 2))
        = (((K : ℝ) - 1) * (1 + t ^ 2) + (cm : ℝ) * (1 - t ^ 2) + 2 * (sm : ℝ) * t) / (1 + t ^ 2) := by
      field_simp
      try ring
    rw [e]
    exact div_nonneg hp (by positivity)
  linarith

/-- `P C = P − P (1 − C) ≤ P + corr` with `corr = max 0 (−P_lo) · K`. -/
theorem corr_bound {Pv Plo Cv K : ℝ} (hP : Plo ≤ Pv) (hC0 : Cv ≤ 1) (hCK : 1 - Cv ≤ K)
    (hK0 : 0 ≤ K) : Pv * Cv ≤ Pv + max 0 (-Plo) * K := by
  have h1 : (0 : ℝ) ≤ 1 - Cv := by linarith
  rcases le_total 0 Pv with hp | hp
  · have : Pv * Cv ≤ Pv := by nlinarith
    have h2 : (0 : ℝ) ≤ max 0 (-Plo) * K := mul_nonneg (le_max_left _ _) hK0
    linarith
  · have hb : -Pv ≤ max 0 (-Plo) := le_trans (by linarith) (le_max_right _ _)
    nlinarith [mul_le_mul_of_nonneg_right hb hK0]

/-- The chord of `|Q|` over `[q_lo, q_hi]` with `q_lo < 0 < q_hi`, denominators cleared by
`Local.abs_chord`. -/
theorem absQ_chord {Qv ql qh : ℝ} (h1 : ql ≤ Qv) (h2 : Qv ≤ qh) (hl : ql < 0) (hh : 0 < qh) :
    |Qv| ≤ ((qh + ql) / (qh - ql)) * Qv + (-2 * ql * qh / (qh - ql)) := by
  have hd : (0 : ℝ) < qh - ql := by linarith
  have h := abs_chord h1 h2 hl.le hh.le
  have e : ((qh + ql) / (qh - ql)) * Qv + (-2 * ql * qh / (qh - ql)) - |Qv|
      = ((qh + ql) * Qv - 2 * ql * qh - (qh - ql) * |Qv|) / (qh - ql) := by
    field_simp
    ring
  have hnn : (0 : ℝ) ≤ ((qh + ql) / (qh - ql)) * Qv + (-2 * ql * qh / (qh - ql)) - |Qv| := by
    rw [e]
    exact div_nonneg (by linarith) hd.le
  linarith

/-- **Envelope (A)**: `Q S ≤ |Q| |S| ≤ S_abs (m_q Q + c_q)`. -/
theorem relax_U_A {Qv Sv mq cq Sabs : ℝ} (hs : |Sv| ≤ Sabs)
    (hq : |Qv| ≤ mq * Qv + cq) : Qv * Sv ≤ Sabs * (mq * Qv + cq) := by
  have h0 : 0 ≤ Sabs := le_trans (abs_nonneg Sv) hs
  have h1 : Qv * Sv ≤ |Qv| * |Sv| := by
    rw [← abs_mul]
    exact le_abs_self _
  nlinarith [abs_nonneg Qv, abs_nonneg Sv]

/-- **Envelope (B1)**: McCormick `(Q − q_hi)(S − S_lo) ≤ 0`, with `S` replaced by the affine
envelope on the side the multiplier's sign selects. -/
theorem relax_U_B1 {Qv Sv qh Slo Senv : ℝ} (hQ : Qv ≤ qh) (hS : Slo ≤ Sv)
    (henv : if 0 ≤ qh then Sv ≤ Senv else Senv ≤ Sv) :
    Qv * Sv ≤ qh * Senv + Qv * Slo - qh * Slo := by
  have hmc : Qv * Sv ≤ qh * Sv + Qv * Slo - qh * Slo := by nlinarith
  rcases le_or_gt 0 qh with h | h
  · rw [if_pos h] at henv
    nlinarith
  · rw [if_neg (not_le.mpr h)] at henv
    nlinarith

/-- **Envelope (B2)**: McCormick `(Q − q_lo)(S − S_hi) ≤ 0`. -/
theorem relax_U_B2 {Qv Sv ql Shi Senv : ℝ} (hQ : ql ≤ Qv) (hS : Sv ≤ Shi)
    (henv : if 0 ≤ ql then Sv ≤ Senv else Senv ≤ Sv) :
    Qv * Sv ≤ ql * Senv + Qv * Shi - ql * Shi := by
  have hmc : Qv * Sv ≤ ql * Sv + Qv * Shi - ql * Shi := by nlinarith
  rcases le_or_gt 0 ql with h | h
  · rw [if_pos h] at henv
    nlinarith
  · rw [if_neg (not_le.mpr h)] at henv
    nlinarith

/-- **(C3) Lemma RELAX, the selection row.**  Given the selection's own row `g_σ ≥ 0`, the exact
axis decomposition, the correction bound, one of the three `Q S` envelopes and a certified plane
below `w`, the emitted row `W_lb/2 + 1/2 − corr − P − U ≤ 0` holds.  This is the whole of Lemma
RELAX for the selection family: no other geometric fact enters. -/
theorem relax_selection {qw qo : PSq} {k : Bool} {eps : ℝ}
    {Pv Qv Cv Sv corr Wlb Uv : ℝ}
    (hgs : 0 ≤ gsel qw qo k eps)
    (hdec : Pv * Cv + Qv * Sv
      = eps * ((qo.cx - qw.cx) * (axk qw k).1 + (qo.cy - qw.cy) * (axk qw k).2))
    (hcor : Pv * Cv ≤ Pv + corr)
    (hU : Qv * Sv ≤ Uv)
    (hW : Wlb ≤ wrel qw qo) :
    Wlb / 2 + 1 / 2 - corr - Pv - Uv ≤ 0 := by
  rw [gsel] at hgs
  linarith

/-! ## 8. (C4) The variable map

`LocalHyp` says that DISTINCT squares of the configuration occupy the boxes of `L` and the slack
cores of `P`.  What the certificate's rows need from it is one square per body IN THE
CERTIFICATE'S OWN BODY ORDER, with the box membership, the container containment (for the wall
rows), the tilt range (for the enclosures) and — the part the selection cover consumes — pairwise
INTERIOR-DISJOINTNESS.  In `t` the tilt coordinate needs no map at all: `Box.t0/t1` and the
certificate's cell are the same variable (A133's point, and the reason no `arctan` appears). -/

/-- **(C4), the geometric half.**  One square per body, indexed `0 … |L|+|P|−1` in the
certificate's body order, with every fact the rows and the enclosures consume. -/
theorem localHyp_bodies {Ls : List Box} {Ps : List Pin} {s : ℝ} {z : Cfg}
    (hz : CfgPacking s z) (h : LocalHyp Ls Ps s z) :
    ∃ q : Nat → PSq,
      (∀ i : Nat, ∀ hi : i < Ls.length, (Ls.get ⟨i, hi⟩).mem (q i)) ∧
      (∀ j : Nat, ∀ hj : j < Ps.length, (Ps.get ⟨j, hj⟩).mem s (q (Ls.length + j))) ∧
      (∀ i : Nat, i < Ls.length + Ps.length →
        (0 ≤ (q i).t ∧ (q i).t ≤ 1) ∧ (q i).set ⊆ container s) ∧
      (∀ i j : Nat, i < Ls.length + Ps.length → j < Ls.length + Ps.length → i ≠ j →
        Disjoint (interior (q i).set) (interior (q j).set)) := by
  obtain ⟨wL, wP, hiL, hiP, hne, hL, hP⟩ := h
  classical
  set w : Nat → Fin 11 := fun a =>
    if ha : a < Ls.length then wL ⟨a, ha⟩
    else if hb : a - Ls.length < Ps.length then wP ⟨a - Ls.length, hb⟩ else ⟨0, by norm_num⟩
    with hw
  have hwL : ∀ (i : Nat) (hi : i < Ls.length), w i = wL ⟨i, hi⟩ := by
    intro i hi; simp only [hw, dif_pos hi]
  have hwP : ∀ (j : Nat) (hj : j < Ps.length), w (Ls.length + j) = wP ⟨j, hj⟩ := by
    intro j hj
    have h1 : ¬ (Ls.length + j < Ls.length) := by omega
    have h2 : Ls.length + j - Ls.length = j := by omega
    simp only [hw, dif_neg h1, h2, dif_pos hj]
  have hinj : ∀ i j : Nat, i < Ls.length + Ps.length → j < Ls.length + Ps.length → i ≠ j →
      w i ≠ w j := by
    intro i j hi hj hne'
    by_cases hia : i < Ls.length <;> by_cases hja : j < Ls.length
    · rw [hwL i hia, hwL j hja]
      intro hc
      exact hne' (by simpa using congrArg Fin.val (hiL hc))
    · have hj' : j - Ls.length < Ps.length := by omega
      have : w j = wP ⟨j - Ls.length, hj'⟩ := by
        have := hwP (j - Ls.length) hj'
        rwa [show Ls.length + (j - Ls.length) = j by omega] at this
      rw [hwL i hia, this]
      exact hne _ _
    · have hi' : i - Ls.length < Ps.length := by omega
      have : w i = wP ⟨i - Ls.length, hi'⟩ := by
        have := hwP (i - Ls.length) hi'
        rwa [show Ls.length + (i - Ls.length) = i by omega] at this
      rw [hwL j hja, this]
      exact fun hc => hne _ _ hc.symm
    · have hi' : i - Ls.length < Ps.length := by omega
      have hj' : j - Ls.length < Ps.length := by omega
      have ei : w i = wP ⟨i - Ls.length, hi'⟩ := by
        have := hwP (i - Ls.length) hi'
        rwa [show Ls.length + (i - Ls.length) = i by omega] at this
      have ej : w j = wP ⟨j - Ls.length, hj'⟩ := by
        have := hwP (j - Ls.length) hj'
        rwa [show Ls.length + (j - Ls.length) = j by omega] at this
      rw [ei, ej]
      intro hc
      have := congrArg Fin.val (hiP hc)
      simp only at this
      omega
  refine ⟨fun a => z (w a), ?_, ?_, ?_, ?_⟩
  · intro i hi
    show (Ls.get ⟨i, hi⟩).mem (z (w i))
    rw [hwL i hi]
    exact hL ⟨i, hi⟩
  · intro j hj
    show (Ps.get ⟨j, hj⟩).mem s (z (w (Ls.length + j)))
    rw [hwP j hj]
    exact hP ⟨j, hj⟩
  · intro i _
    show (0 ≤ (z (w i)).t ∧ (z (w i)).t ≤ 1) ∧ (z (w i)).set ⊆ container s
    exact ⟨⟨(hz.1 (w i)).1, (hz.1 (w i)).2⟩, hz.2.contained (w i)⟩
  · intro i j hi hj hij
    show Disjoint (interior (z (w i)).set) (interior (z (w j)).set)
    exact hz.2.interiorDisjoint _ _ (hinj i j hi hj hij)

/-! ## 9. What is discharged and what is not

**Discharged here**, all with the roster `[propext, Classical.choice, Quot.sound]` — no project
axiom (`Local.sat_selection` is NOT used: `SatInterior.sat_selection_thm` proves it), no
`native_decide`, no `sorry` (audit: `lean/PackingCertMathlib/scratch/A134Axioms.lean`):

* **(C2) the selection cover** — `selectionOk` / `selectionOk_sound`, decided on the cell's own
  rational data.  Its two halves are `gsel_le_gapHi` (the enclosure, exact in `t` up to one
  interval multiplication) and `selection_cover` (the case split, from `sat_selection_thm`).
* **(C3) Lemma RELAX**, both row families: `relax_wall` for the wall rows and `relax_selection`
  for the selection rows, together with every ingredient the latter consumes —
  `axis_decomp_t` (the exact decomposition, an algebraic identity in `t` with no angle),
  `one_sub_cosRel_le` + `corr_bound` (the correction term), `relax_U_A` / `relax_U_B1` /
  `relax_U_B2` (the three `Q·S` envelopes, with `absQ_chord` from `Local.abs_chord`), and
  `wrel_ge_plane` (the certified plane below `w`).  Each rational constant these consume is
  certified by §1–§4 from the `pcert` field of a `local-cert-t-v2` certificate
  (`attempts/A134-certcover-close/code/gen_local_t2.py`).
* **(C4) the variable map, geometric half** — `localHyp_bodies`: one square per body in the
  certificate's own body order, with box membership, container containment, the tilt range and
  pairwise interior-disjointness.

**NOT obtained**: `certCover_s07` and hence `localDead_s07_t` / `localDead_s02_t`.  What stands
between this file and them is bookkeeping of four named kinds, and — this is the point of the
audit below — **no missing library lemma**: every mathematical step of (C2), (C3) and (C4) is a
theorem above or in `Local.lean` / `SatInterior.lean` / `LocalCertT.lean` / `Parametrize.lean`.

* **(R1) the reflected certificate tree.**  An inductive mirroring the emitted `root` — `bisect`,
  `branch`, `imp` / `imp_sel`, `dead` — with a decidable `treeOk` that applies
  `LocalCertT.splitOk` at a bisection, `selectionOk` at a branch and at an `imp`, and matches a
  `dead` node against the recorded leaf.  Consumes `LocalCertT.coverOk_sound` (C1) and
  `selectionOk_sound` (C2); ≈ 300 lines, no new mathematics.
* **(R2) the reflected row builder.**  `rowsOf : Cell → Selections → List CRow`, the Lean twin of
  `gen_local_t.RowsT`, with `rowsOf_sound` from §7.  Two parts: the affine-form bookkeeping that
  identifies `evalL row.co x 0 + row.k` with the real quantities `P`, `Q`, `W_lb`, `c_x`, `c_y`;
  and the OUTWARD quantisation of `gen_local_t.quantise_leaf` (coefficients rounded to `1/10¹²`,
  the constant lowered by the box slack, so `emitted ≤ true ≤ 0`), for which `LocalCert.minL_le`
  is the tool.  ≈ 600 lines.
* **(R3) the variable INDEX map.**  §8 supplies the squares; what remains is
  `x (2i+1) = (q i).cx`, `x (2i+2) = (q i).cy − (α + β s)` for a pin, `x (2·|B|+1+f) = (q i).t`,
  from a decidable check that the certificate's layout is that one (it is: A119's numbering, and
  A133 inherits it).  ≈ 120 lines.
* **(R4) the data and the replay.**  `LocalCertT2S07Data` / `…S02Data` for the `t`-certificates
  (2 140 and 16 406 leaves) plus the `pcert` entries, and the `native_decide` replay.

**One gap was found and closed on the CERTIFICATE side, not the library side.**  Lemma RELAX's
selection row consumes three constants that A133's certificate did not record: the two McCormick
corners `S_lo`, `S_hi` (also the chord scale `S_abs` of envelope (A)) and the correction constant
`K = max(1 − cos φ)`.  A133's Python checker recomputes them; Lean cannot.  `gen_local_t2.py` now
emits all three with their own positivity certificates (`pcert.S[…].s_lo/s_hi/K` and the chains
`c_lo`, `c_hi`, `corr`), which is why `sRel_le_aff` / `sRel_ge_aff` (with `alpha = 0`) and
`one_sub_cosRel_le` are stated in the form they are.
-/

end LocalCertT2
end S11
end PackingCert
