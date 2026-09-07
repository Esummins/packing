import PackingCertMathlib.LocalCert

/-!
# The tan-half certificate: the decidable primitives `CertCover` was missing — A133 T2

`LocalCert.lean` (A126) reduced a local certificate to ONE named hypothesis,
`CertCover leaves Ls Ps slo shi`, and `attempts/A126-localdead-lean/notes/obligations.md` named
the single missing ingredient: **a certified rational-interval kernel for `cos`, `sin` and `π`
over a rational tilt cell**, needed by (C2) the selection cover and (C3) Lemma RELAX.  A126's own
recommendation was to remove the need for it by re-emitting the certificate in
`t = tan(θ/2)` — Lean's own tilt parameter (`Parametrize.cosT`, `Parametrize.sinT`) — in which

    cos θ = (1 − t²)/(1 + t²) = cosT t,      sin θ = 2t/(1 + t²) = sinT t

are RATIONAL functions of `t`, so every enclosure a certificate needs is the exact range of a
rational function over a rational cell.  A133 carried that out on the generator side
(`attempts/A133-tan-half-emission/code/{gen_local_t,check_local_t}.py`); this file is the Lean
side of it, and it is deliberately arithmetic-only:

* **§1 the exact enclosures.**  `cosT` is antitone and `sinT` monotone on `[0, 1]`, so the range
  of either over a tilt cell is its pair of ENDPOINT VALUES — exactly, with no enclosure error,
  no `π` and no series.  This is what `attempts/A119-local-cert-lean/code/exactiv.py` computes
  with 96-bit dyadic intervals and a rigorous `π`, and here it is two `nlinarith`s.
* **§2 `w` without the kink.**  `w(Δ) = |cos Δ| + |sin Δ|` is bounded below by its two SMOOTH
  branches `cos Δ ± sin Δ`, on the whole cell and with no case split, and their maximum is `w`.
  A119's affine lower bounds of `w` need the location of the `π/2` kink (`exactiv.kink_in`, the
  one place a rigorous `π` was unavoidable); in `t` the two branches are rational functions and
  the kink never has to be located.
* **§3 the positivity certificate.**  Every affine envelope of Lemma RELAX in `t` — the chord of
  the wall half-width, the two-sided enclosure of `sin(θ(t) − θ(t*))`, the two affine lower
  bounds of `w` — reduces to `p ≥ 0 on [a, b]` for an exact rational polynomial `p`.  `posCheck`
  decides it from a certificate `Σ_k c_k (X − a)^k (b − X)^{n−k}` with `c_k ≥ 0`, and
  `posCheck_sound` is its soundness.  This is the DECIDABLE replacement for the trigonometric
  kernel of `obligations.md`, and it is `native_decide`-able on certificate data.
* **§4 the tilt cover, (C1) of `obligations.md`, discharged.**  A bisection tree over the product
  of the tilt cells with a decidable well-formedness check (`coverOk`) and its soundness
  (`coverOk_sound`): every point of the root cell lies in the cell of one recorded leaf.

What this file does NOT do, and what still stands between it and a hypothesis-free
`localDead_s07_t`, is written out in §5.
-/

namespace PackingCert
namespace S11
namespace LocalCertT

open Set
open PackingCert.S11.LocalCert

/-! ## 1. The exact enclosures of `cosT` and `sinT` over a rational cell

On `t ∈ [0, 1]` (`θ ∈ [0°, 90°]`, the fundamental domain a packed square is normalised to by
`Parametrize.isUnitSquare_exists_psq`) `cosT` decreases and `sinT` increases, so the range of
each over a cell is the pair of its values at the cell's endpoints — RATIONAL numbers when the
endpoints are, and exact. -/

theorem one_add_sq_pos (t : ℝ) : (0 : ℝ) < 1 + t ^ 2 := by positivity

/-- `cosT` is antitone on `[0, ∞)`. -/
theorem cosT_anti {t₁ t₂ : ℝ} (h0 : 0 ≤ t₁) (h : t₁ ≤ t₂) : cosT t₂ ≤ cosT t₁ := by
  have p1 := one_add_sq_pos t₁
  have p2 := one_add_sq_pos t₂
  have key : cosT t₁ - cosT t₂ = (2 * (t₂ ^ 2 - t₁ ^ 2)) / ((1 + t₁ ^ 2) * (1 + t₂ ^ 2)) := by
    rw [cosT, cosT]; field_simp; ring
  have hnum : (0 : ℝ) ≤ 2 * (t₂ ^ 2 - t₁ ^ 2) := by nlinarith
  have : (0 : ℝ) ≤ cosT t₁ - cosT t₂ := by
    rw [key]; exact div_nonneg hnum (by positivity)
  linarith

/-- `sinT` is monotone on `[0, 1]`. -/
theorem sinT_mono {t₁ t₂ : ℝ} (h0 : 0 ≤ t₁) (h : t₁ ≤ t₂) (h1 : t₂ ≤ 1) :
    sinT t₁ ≤ sinT t₂ := by
  have p1 := one_add_sq_pos t₁
  have p2 := one_add_sq_pos t₂
  have key : sinT t₂ - sinT t₁
      = (2 * ((t₂ - t₁) * (1 - t₁ * t₂))) / ((1 + t₁ ^ 2) * (1 + t₂ ^ 2)) := by
    rw [sinT, sinT]; field_simp; ring
  have ht2 : (0 : ℝ) ≤ t₂ := le_trans h0 h
  have ht : t₁ * t₂ ≤ 1 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr (le_trans h h1)) ht2]
  have hnum : (0 : ℝ) ≤ 2 * ((t₂ - t₁) * (1 - t₁ * t₂)) := by
    nlinarith [mul_nonneg (sub_nonneg.mpr h) (sub_nonneg.mpr ht)]
  have : (0 : ℝ) ≤ sinT t₂ - sinT t₁ := by
    rw [key]; exact div_nonneg hnum (by positivity)
  linarith

/-- **The exact `cos` enclosure over a tilt cell.**  No `π`, no series, no interval kernel. -/
theorem cosT_mem {a b t : ℝ} (ha : 0 ≤ a) (h1 : a ≤ t) (h2 : t ≤ b) :
    cosT b ≤ cosT t ∧ cosT t ≤ cosT a :=
  ⟨cosT_anti (le_trans ha h1) h2, cosT_anti ha h1⟩

/-- **The exact `sin` enclosure over a tilt cell.** -/
theorem sinT_mem {a b t : ℝ} (ha : 0 ≤ a) (h1 : a ≤ t) (h2 : t ≤ b) (hb : b ≤ 1) :
    sinT a ≤ sinT t ∧ sinT t ≤ sinT b :=
  ⟨sinT_mono ha h1 (le_trans h2 hb), sinT_mono (le_trans ha h1) h2 hb⟩

/-! ## 2. `w = |cos Δ| + |sin Δ|` without the kink

`LocalCert.wrel` is `|cos Δ| + |sin Δ|` written with the addition formulas, so that it is a
function of the two tilt PARAMETERS.  Its affine lower bounds are what Lemma RELAX needs, and
A119 obtains them from the chord of `w` on a cell with no interior kink and from two "V-lines"
through the kink otherwise — the kink being at a multiple of `π/2`, which is the one place a
rigorous enclosure of `π` was unavoidable.

In `t` there is no case split at all: `w ≥ cos Δ + sin Δ` and `w ≥ cos Δ − sin Δ` hold on the
WHOLE cell, both are rational functions of `(t_w, t_o)`, and their maximum is `w`.  The
generator's two `w` rows per selection are exactly these two branches. -/

/-- The `cos Δ` branch of `wrel`, as a rational function of the two tilt parameters. -/
noncomputable def cosRel (tw tb : ℝ) : ℝ := cosT tw * cosT tb + sinT tw * sinT tb

/-- The `sin Δ` branch (with `LocalCert.wrel`'s sign). -/
noncomputable def sinRel (tw tb : ℝ) : ℝ := cosT tw * sinT tb - sinT tw * cosT tb

theorem wrel_eq (qw qo : PSq) : wrel qw qo = |cosRel qw.t qo.t| + |sinRel qw.t qo.t| := rfl

/-- **The `+` branch.**  Valid on every cell, with no kink location. -/
theorem wrel_ge_add (qw qo : PSq) :
    cosRel qw.t qo.t + sinRel qw.t qo.t ≤ wrel qw qo := by
  rw [wrel_eq]
  exact add_le_add (le_abs_self _) (le_abs_self _)

/-- **The `−` branch.**  Valid on every cell, with no kink location. -/
theorem wrel_ge_sub (qw qo : PSq) :
    cosRel qw.t qo.t - sinRel qw.t qo.t ≤ wrel qw qo := by
  rw [wrel_eq]
  exact add_le_add (le_abs_self _) (neg_le_abs _)

/-- The two branches are exhaustive: their maximum IS `w`, so nothing is lost by using only
them.  (`|x| = max x (−x)`.) -/
theorem wrel_eq_max_of_cos_nonneg (qw qo : PSq) (h : 0 ≤ cosRel qw.t qo.t) :
    wrel qw qo = max (cosRel qw.t qo.t + sinRel qw.t qo.t)
                     (cosRel qw.t qo.t - sinRel qw.t qo.t) := by
  rw [wrel_eq, abs_of_nonneg h]
  rcases abs_cases (sinRel qw.t qo.t) with ⟨he, hs⟩ | ⟨he, hs⟩ <;> rw [he]
  · rw [max_eq_left (by linarith)]
  · rw [max_eq_right (by linarith)]; ring

/-! ## 3. The positivity certificate — the decidable replacement for the trig kernel

Every affine envelope the `t`-relaxation uses is of the form "this rational polynomial is `≥ 0`
on this rational interval", after clearing the denominator `1 + t²` (or `(1 + t_w²)(1 + t_o²)`),
which is positive.  A positivity certificate is a list of NONNEGATIVE rationals `c` with

    p(X) = Σ_{k} c_k (X − a)^k (b − X)^{n − k},   n = c.length − 1,

which makes `p ≥ 0` on `[a, b]` immediate, because `x − a ≥ 0` and `b − x ≥ 0` there.  The check
is list equality of exact rational coefficients: DECIDABLE, and cheap under `native_decide`. -/

/-- A rational polynomial as its ascending list of monomial coefficients. -/
abbrev Poly := List ℚ

/-- `peval [a₀, a₁, …] x = a₀ + x (a₁ + x (…))`. -/
def peval : Poly → ℝ → ℝ
  | [], _ => 0
  | a :: t, x => (a : ℝ) + x * peval t x

def padd : Poly → Poly → Poly
  | [], q => q
  | p, [] => p
  | a :: p, b :: q => (a + b) :: padd p q

def pscale (c : ℚ) : Poly → Poly
  | [] => []
  | a :: p => c * a :: pscale c p

def pmul : Poly → Poly → Poly
  | [], _ => []
  | a :: p, q => padd (pscale a q) (0 :: pmul p q)

theorem peval_padd (p q : Poly) (x : ℝ) : peval (padd p q) x = peval p x + peval q x := by
  induction p generalizing q with
  | nil => simp [padd, peval]
  | cons a p ih =>
    cases q with
    | nil => simp [padd, peval]
    | cons b q =>
      simp only [padd, peval, ih]
      push_cast
      ring

theorem peval_pscale (c : ℚ) (p : Poly) (x : ℝ) : peval (pscale c p) x = (c : ℝ) * peval p x := by
  induction p with
  | nil => simp [pscale, peval]
  | cons a p ih =>
    simp only [pscale, peval, ih]
    push_cast
    ring

theorem peval_pmul (p q : Poly) (x : ℝ) : peval (pmul p q) x = peval p x * peval q x := by
  induction p with
  | nil => simp [pmul, peval]
  | cons a p ih =>
    simp only [pmul, peval, peval_padd, peval_pscale, ih]
    push_cast
    ring

/-- `X − a`. -/
def linA (a : ℚ) : Poly := [-a, 1]

/-- `b − X`. -/
def linB (b : ℚ) : Poly := [b, -1]

def ppow (p : Poly) : Nat → Poly
  | 0 => [1]
  | n + 1 => pmul p (ppow p n)

theorem peval_ppow (p : Poly) (n : Nat) (x : ℝ) : peval (ppow p n) x = (peval p x) ^ n := by
  induction n with
  | zero => simp [ppow, peval]
  | succ n ih => simp only [ppow, peval_pmul, ih, pow_succ]; ring

theorem peval_linA (a : ℚ) (x : ℝ) : peval (linA a) x = x - (a : ℝ) := by
  simp only [linA, peval]; push_cast; ring

theorem peval_linB (b : ℚ) (x : ℝ) : peval (linB b) x = (b : ℝ) - x := by
  simp only [linB, peval]; push_cast; ring

/-- `Σ_k c_k (X − a)^k (b − X)^{m − k}`, written so that the recursion peels `c₀` off the front:
`c₀ (b − X)^m + (X − a) · (the same with m − 1)`. -/
def posAux (a b : ℚ) : Poly → Nat → Poly
  | [], _ => []
  | v :: cs, m => padd (pscale v (ppow (linB b) m)) (pmul (linA a) (posAux a b cs (m - 1)))

theorem posAux_nonneg (a b : ℚ) (c : Poly) (hc : ∀ v ∈ c, 0 ≤ v) (m : Nat) (x : ℝ)
    (h1 : (a : ℝ) ≤ x) (h2 : x ≤ (b : ℝ)) : 0 ≤ peval (posAux a b c m) x := by
  induction c generalizing m with
  | nil => simp [posAux, peval]
  | cons v cs ih =>
    have hv : (0 : ℝ) ≤ (v : ℝ) := by exact_mod_cast hc v (List.mem_cons_self ..)
    have hrest := ih (fun w hw => hc w (List.mem_cons_of_mem _ hw)) (m - 1)
    have hb : (0 : ℝ) ≤ (b : ℝ) - x := by linarith
    have h1' : (0 : ℝ) ≤ x - (a : ℝ) := by linarith
    simp only [posAux, peval_padd, peval_pscale, peval_pmul, peval_ppow, peval_linA, peval_linB]
    have : (0 : ℝ) ≤ (v : ℝ) * ((b : ℝ) - x) ^ m := mul_nonneg hv (pow_nonneg hb m)
    nlinarith [mul_nonneg h1' hrest]

/-- **The decidable positivity check.**  `p` is `≥ 0` on `[a, b]` if the certificate `c` is
nonnegative coefficientwise and reproduces `p` exactly. -/
def posCheck (p c : Poly) (a b : ℚ) : Bool :=
  c.all (fun v => 0 ≤ v) && (posAux a b c (c.length - 1) == p)

/-- **Soundness of the positivity check.** -/
theorem posCheck_sound {p c : Poly} {a b : ℚ} (h : posCheck p c a b = true) {x : ℝ}
    (h1 : (a : ℝ) ≤ x) (h2 : x ≤ (b : ℝ)) : 0 ≤ peval p x := by
  rw [posCheck, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at h
  obtain ⟨hc, he⟩ := h
  have hc' : ∀ v ∈ c, 0 ≤ v := by
    intro v hv
    have := hc v hv
    simpa using this
  have := posAux_nonneg a b c hc' (c.length - 1) x h1 h2
  rwa [he] at this

/-! ## 4. The tilt cover — (C1) of A126's `obligations.md`, discharged

The certificate's bisection tree splits ONE body's tilt cell at a recorded rational point and its
two children carry `[lo, mid]` and `[mid, hi]`.  `splitOk` is the decidable well-formedness check
of one such node — the two child cells agree with the parent in every coordinate but the split
one, where they are the two halves — and `splitOk_sound` is `le_total`.  `coverOk` walks the whole
tree and checks that every leaf's recorded cell is the cell the walk arrived at; `coverOk_sound`
then says that every point of the ROOT cell lies in the cell of SOME recorded leaf.

The cells are `LocalCert.InBox`-shaped lists of rational bounds, so this is literally the
statement that the recorded leaves cover the tilt product, decidable on rational data. -/

/-- One bisection node's well-formedness: `par` splits at `m` in coordinate `j` into `c1`, `c2`. -/
def splitOk : List (ℚ × ℚ) → List (ℚ × ℚ) → List (ℚ × ℚ) → Nat → ℚ → Bool
  | (a, b) :: p, (c, d) :: q, (e, f) :: r, 0, m =>
      (a ≤ m) && (m ≤ b) && (c == a) && (d == m) && (e == m) && (f == b) && (p == q) && (q == r)
  | u :: p, v :: q, w :: r, n + 1, m => (u == v) && (v == w) && splitOk p q r n m
  | _, _, _, _, _ => false

theorem splitOk_sound : ∀ (par c1 c2 : List (ℚ × ℚ)) (j : Nat) (m : ℚ) (x : Nat → ℝ) (i : Nat),
    splitOk par c1 c2 j m = true → InBox par x i → InBox c1 x i ∨ InBox c2 x i := by
  intro par
  induction par with
  | nil => intro c1 c2 j m x i h _; cases c1 <;> cases c2 <;> cases j <;> simp [splitOk] at h
  | cons ab p ih =>
    intro c1 c2 j m x i h hb
    obtain ⟨a, b⟩ := ab
    cases c1 with
    | nil => cases c2 <;> cases j <;> simp [splitOk] at h
    | cons cd q =>
      cases c2 with
      | nil => cases j <;> simp [splitOk] at h
      | cons ef r =>
        obtain ⟨c, d⟩ := cd
        obtain ⟨e, f⟩ := ef
        obtain ⟨hlo, hhi, hrest⟩ := hb
        cases j with
        | zero =>
          simp only [splitOk, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
          obtain ⟨⟨⟨⟨⟨⟨⟨_, _⟩, hca⟩, hdm⟩, hem⟩, hfb⟩, hpq⟩, hqr⟩ := h
          rcases le_total (x i) ((m : ℝ)) with hx | hx
          · refine Or.inl ⟨?_, ?_, ?_⟩
            · rw [hca]; exact hlo
            · rw [hdm]; exact hx
            · rw [← hpq]; exact hrest
          · refine Or.inr ⟨?_, ?_, ?_⟩
            · rw [hem]; exact hx
            · rw [hfb]; exact hhi
            · rw [← hqr, ← hpq]; exact hrest
        | succ n =>
          simp only [splitOk, Bool.and_eq_true, beq_iff_eq] at h
          obtain ⟨⟨huv, hvw⟩, hs⟩ := h
          have e1 : (c, d) = (a, b) := huv.symm
          have e2 : (e, f) = (c, d) := hvw.symm
          rw [e1] at e2 ⊢
          rw [e2]
          rcases ih q r n m x (i + 1) hs hrest with hL | hR
          · exact Or.inl ⟨hlo, hhi, hL⟩
          · exact Or.inr ⟨hlo, hhi, hR⟩

/-- The certificate's bisection tree.  Each node records the split coordinate, the split point
and BOTH child cells, so that no list surgery is needed to check it. -/
inductive CTree where
  | leaf (i : Nat) : CTree
  | bis (j : Nat) (m : ℚ) (c1 c2 : List (ℚ × ℚ)) (l r : CTree) : CTree
  deriving Inhabited

/-- The decidable cover check: every bisection is well formed and every leaf's recorded cell is
the cell the walk arrived at. -/
def coverOk (cells : List (List (ℚ × ℚ))) : CTree → List (ℚ × ℚ) → Bool
  | .leaf i, cur => cells[i]? == some cur
  | .bis j m c1 c2 l r, cur =>
      splitOk cur c1 c2 j m && coverOk cells l c1 && coverOk cells r c2

/-- **Soundness of the cover check — Lemma COVER's tilt half.**  Every point of the root cell
lies in the recorded cell of some leaf of the tree. -/
theorem coverOk_sound (cells : List (List (ℚ × ℚ))) :
    ∀ (T : CTree) (cur : List (ℚ × ℚ)) (x : Nat → ℝ) (i : Nat),
      coverOk cells T cur = true → InBox cur x i →
      ∃ k : Nat, ∃ cl : List (ℚ × ℚ), cells[k]? = some cl ∧ InBox cl x i := by
  intro T
  induction T with
  | leaf n =>
    intro cur x i h hb
    simp only [coverOk, beq_iff_eq] at h
    exact ⟨n, cur, h, hb⟩
  | bis j m c1 c2 l r ihl ihr =>
    intro cur x i h hb
    simp only [coverOk, Bool.and_eq_true] at h
    obtain ⟨⟨hs, hl⟩, hr⟩ := h
    rcases splitOk_sound cur c1 c2 j m x i hs hb with h1 | h2
    · exact ihl c1 x i hl h1
    · exact ihr c2 x i hr h2

/-! ## 5. What is still missing for a hypothesis-free `localDead_s07_t`

`LocalCert.CertCover` splits into the four pieces A126 named.  With this file:

* **(C1) the tilt cover** — DISCHARGED: `coverOk` / `coverOk_sound`, decidable on the
  certificate's own rational bisection tree.
* **(C2) the selection cover** — the logical half is `SatInterior.sat_selection_thm` +
  `LocalCert.cover_selection`, both theorems; the arithmetic half is `sup_cell g_σ < 0`, which
  in `t` is a rational-interval computation built from §1 (`cosT_mem`, `sinT_mem`) and §2 — every
  ingredient is here, but the reflected enclosure function over a cell and its soundness lemma
  are NOT yet written.
* **(C3) Lemma RELAX** — the affine envelopes are `p ≥ 0 on [a, b]` statements about exact
  rational polynomials, so §3 supplies the decision procedure; what is not yet written is the
  reflected row builder in `t` (the Lean twin of
  `attempts/A133-tan-half-emission/code/gen_local_t.py`'s `RowsT`) together with the proof that
  each row it builds is implied by `0 ≤ gsel` on the cell.  `Local.mccormick_hi` / `mccormick_lo`
  / `abs_chord` / `axis_decomp` are the pieces it consumes and are already theorems.
* **(C4) the variable map** — bookkeeping, not yet written.

So this file removes the OBSTACLE A126 named (the certified `cos`/`sin`/`π` kernel: it is no
longer needed at all, §1–§3 replace it with exact rational arithmetic and one decidable
positivity test) and discharges (C1); (C2)–(C4) remain, and are now pure reflection work with no
transcendental content.  `attempts/A133-tan-half-emission/notes/lean.md` prices them.
-/

end LocalCertT
end S11
end PackingCert
