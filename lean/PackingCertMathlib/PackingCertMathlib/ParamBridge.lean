import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.MeasureBridge
import PackingCertMathlib.Dilation
import PackingCertMathlib.CaseHyp
import PackingCertMathlib.CaseBridge
import PackingCertMathlib.ParamChecker
import PackingCertMathlib.MeasurePyBridge

/-!
# The parametric (window) bridge (A75, depgraph node V.PARAM)

Soundness of `checkParamI` (`ParamChecker.lean`, the Lean port of `verify_param.py`'s
decision core):

    `checkParamI c ts ss k pick = true`  ⟹  for EVERY real side `s ∈ [s_lo, s_hi]`:
        (P1) `Σ wᵢ < (n − r) · wd`  and
        (P2) every unit square in `[0,s]²` that misses every core `Kⱼ(s)` has
             `μ_s(Q) ≥ wd`
      ⟹  no strict family of `n` closed unit squares at side `s` has designated
          owners containing the cores `Kⱼ(s)`  (`checkParamI_kill`),

for every oracle `pick`, every integer `tscale`/`sscale` and every root split `k`.
This is the soundness theorem [S] of `attempts/A56-sparametric/notes/soundness.md` P3,
in exactly the form `stratum_kill` (`TopLevel.lean`) consumes: the `∀ s ∈ window`
quantifier is over the REALS (the atoms and cores are affine in `s`, so `μ_s` and
`Kⱼ(s)` make sense at every real side), and the conclusion per side is the
`checkCaseI_kill` form of A70 — so Lemma B's λ-dilation (`Dilation.lean`) composes per
side exactly as for a fixed-side certificate (`checkParamI_kill_packing`).

Structure.  The four discharge rules specialise to a fixed `s` of the cell:
* clip (`clipI_sound` at the wall `s_b = SB/D ≥ s`; admissibility is monotone in the side);
* exempt (`coreExemptIV_sound`): `core_exempt_frac_iv` is A70's `coreExempt` for the
  centre-`0` core on the box shifted by the centre INTERVAL, so for the actual centre
  `K(s) ∈ [kx0,kx1] × [ky0,ky1]` it is `coreExempt_sound` applied to the translated
  square — translation invariance of `PSq.set` and `coreSet` (`mem_set_translate`,
  `coreSet_translate`) does the rest;
* covered (`siftP_sound`): `atom_inside_int_iv` is `projI` with the atom point replaced
  by its interval box (`projIV_sound`, the A64 proof with the point bounds weakened to
  interval bounds); the exact cell endpoints over the lcm denominator denote the real
  interval endpoints (`numOver_cast`), and an affine function stays between its endpoint
  values (`affine_between`);
* split (`splitP_sound`): the four-axis rule covers the 4-D box (the s-midpoint is
  integral by construction).

The pricing pigeonhole is A68/A70's, generalised to an abstract mass functional
(`priced_dichotomy_gen`) so that the s-dependent atom measure `massP` can use it.
-/

namespace PackingCert
namespace S11

open Set MeasureI CaseI ParamI

noncomputable section

/-! ## Real semantics of the parametric data -/

/-- The real point of an affine atom at side `s`. -/
def atomPtP (a : PAtom) (s : ℝ) : RP :=
  ((a.alphaX : ℝ) + (a.betaX : ℝ) * s, (a.alphaY : ℝ) + (a.betaY : ℝ) * s)

/-- The (scaled, `wd`-denominated) mass `μ_s` gives to a set. -/
def massP (l : List PAtom) (s : ℝ) (Q : Set RP) : ℝ :=
  (l.map fun a => Q.indicator (fun _ => (a.w : ℝ)) (atomPtP a s)).sum

@[simp] theorem massP_nil (s : ℝ) (Q : Set RP) : massP [] s Q = 0 := rfl

theorem massP_cons (a : PAtom) (l : List PAtom) (s : ℝ) (Q : Set RP) :
    massP (a :: l) s Q = Q.indicator (fun _ => (a.w : ℝ)) (atomPtP a s) + massP l s Q := by
  simp [massP]

theorem massP_nonneg {l : List PAtom} (hl : ∀ a ∈ l, 0 ≤ a.w) (s : ℝ) (Q : Set RP) :
    0 ≤ massP l s Q := by
  refine List.sum_nonneg ?_
  intro x hx
  simp only [List.mem_map] at hx
  obtain ⟨a, ha, rfl⟩ := hx
  exact Set.indicator_nonneg (fun _ _ => by exact_mod_cast hl a ha) _

theorem massP_sum_comm {n : ℕ} (atoms : List PAtom) (s : ℝ) (f : Fin n → Set RP) :
    ∑ i, massP atoms s (f i)
      = (atoms.map fun a =>
          ∑ i, (f i).indicator (fun _ => (a.w : ℝ)) (atomPtP a s)).sum := by
  induction atoms with
  | nil => simp [massP]
  | cons a as ihl =>
    simp only [massP_cons, List.map_cons, List.sum_cons, Finset.sum_add_distrib, ihl]

/-- μ_s-additivity bound over a pairwise-disjoint family: the total is an upper bound. -/
theorem massP_sum_le {n : ℕ} (atoms : List PAtom) (hw : ∀ a ∈ atoms, 0 ≤ a.w) (s : ℝ)
    {f : Fin n → Set RP} (hdis : ∀ i j, i ≠ j → Disjoint (f i) (f j)) :
    ∑ i, massP atoms s (f i) ≤ (atoms.map fun a => (a.w : ℝ)).sum := by
  rw [massP_sum_comm]
  refine List.sum_le_sum fun a ha => ?_
  have hwa : (0 : ℝ) ≤ (a.w : ℝ) := by exact_mod_cast hw a ha
  exact indicator_sum_le hdis hwa (atomPtP a s)

theorem foldlP_add_eq (l : List PAtom) : ∀ i : Int,
    l.foldl (fun acc a => acc + a.w) i = i + (l.map (fun a => a.w)).sum := by
  induction l with
  | nil => intro i; simp
  | cons a as ihl =>
    intro i
    rw [List.foldl_cons, ihl, List.map_cons, List.sum_cons]
    ring

/-- The core square `Kⱼ(s)` at real side `s` (the `coreSet` formula with the affine
centre). -/
def coreSetP (K : PCore) (s : ℝ) : Set RP :=
  {p : RP |
    |(p.1 - ((K.akx : ℝ) + (K.bkx : ℝ) * s)) * cosT (K.tm : ℝ)
        + (p.2 - ((K.aky : ℝ) + (K.bky : ℝ) * s)) * sinT (K.tm : ℝ)| ≤ (K.a : ℝ) ∧
    |(-(p.1 - ((K.akx : ℝ) + (K.bkx : ℝ) * s))) * sinT (K.tm : ℝ)
        + (p.2 - ((K.aky : ℝ) + (K.bky : ℝ) * s)) * cosT (K.tm : ℝ)| ≤ (K.a : ℝ)}

/-! ## Interval widening lemmas -/

/-- An affine function of `s` stays between its values at the cell endpoints. -/
theorem affine_between {α β sa sb : ℚ} {s : ℝ} (hsa : (sa : ℝ) ≤ s) (hsb : s ≤ (sb : ℝ)) :
    (((rminmax (α + β * sa) (α + β * sb)).1 : ℚ) : ℝ) ≤ (α : ℝ) + (β : ℝ) * s ∧
    (α : ℝ) + (β : ℝ) * s ≤ (((rminmax (α + β * sa) (α + β * sb)).2 : ℚ) : ℝ) := by
  have key : ((β : ℝ) * sa ≤ (β : ℝ) * s ∧ (β : ℝ) * s ≤ (β : ℝ) * sb) ∨
      ((β : ℝ) * sb ≤ (β : ℝ) * s ∧ (β : ℝ) * s ≤ (β : ℝ) * sa) := by
    rcases le_or_gt 0 (β : ℝ) with hb | hb
    · exact Or.inl ⟨mul_le_mul_of_nonneg_left hsa hb, mul_le_mul_of_nonneg_left hsb hb⟩
    · exact Or.inr ⟨mul_le_mul_of_nonpos_left hsb hb.le, mul_le_mul_of_nonpos_left hsa hb.le⟩
  unfold rminmax
  split_ifs with h
  · have hR : (α : ℝ) + (β : ℝ) * sa ≤ (α : ℝ) + (β : ℝ) * sb := by exact_mod_cast h
    simp only
    push_cast
    rcases key with ⟨k1, k2⟩ | ⟨k1, k2⟩ <;> constructor <;> linarith
  · have hR : (α : ℝ) + (β : ℝ) * sb < (α : ℝ) + (β : ℝ) * sa := by
      exact_mod_cast (not_le.mp h)
    simp only
    push_cast
    rcases key with ⟨k1, k2⟩ | ⟨k1, k2⟩ <;> constructor <;> linarith

/-- `r.num · (pd / r.den)` over `pd` IS `r` when `r.den ∣ pd`. -/
theorem numOver_cast (r : ℚ) {pd : ℕ} (hdvd : r.den ∣ pd) (hpd : 0 < pd) :
    ((numOver r pd : Int) : ℝ) / (pd : ℝ) = (r : ℝ) := by
  obtain ⟨c, hc⟩ := hdvd
  have hden : (0 : ℤ) < (r.den : ℤ) := by exact_mod_cast r.den_pos
  have hq : (pd : Int) / (r.den : Int) = (c : Int) := by
    rw [hc]
    push_cast
    exact Int.mul_ediv_cancel_left _ hden.ne'
  have hcpos : (0 : ℝ) < (c : ℝ) := by
    have : 0 < c := by
      rcases Nat.eq_zero_or_pos c with h | h
      · subst h; simp at hc; omega
      · exact h
    exact_mod_cast this
  have hdenR : (0 : ℝ) < (r.den : ℝ) := by exact_mod_cast r.den_pos
  rw [numOver, hq]
  have hpdR : (pd : ℝ) = (r.den : ℝ) * (c : ℝ) := by rw [hc]; push_cast; ring
  rw [hpdR, Rat.cast_def]
  push_cast
  field_simp

/-- The exact cell endpoints of an atom bound its real position at every side of the
cell, in the integer-scaled form the checker uses. -/
theorem cellAtom_sound (a : PAtom) {sa sb : ℚ} {s : ℝ} (hsa : (sa : ℝ) ≤ s)
    (hsb : s ≤ (sb : ℝ)) :
    0 < (cellAtom a sa sb).pd ∧ (cellAtom a sa sb).w = a.w ∧
    ((cellAtom a sa sb).pxlo : ℝ) ≤ (atomPtP a s).1 * ((cellAtom a sa sb).pd : ℝ) ∧
    (atomPtP a s).1 * ((cellAtom a sa sb).pd : ℝ) ≤ ((cellAtom a sa sb).pxhi : ℝ) ∧
    ((cellAtom a sa sb).pylo : ℝ) ≤ (atomPtP a s).2 * ((cellAtom a sa sb).pd : ℝ) ∧
    (atomPtP a s).2 * ((cellAtom a sa sb).pd : ℝ) ≤ ((cellAtom a sa sb).pyhi : ℝ) := by
  have hpd : 0 < cellPd a sa sb := by
    unfold cellPd
    exact Nat.lcm_pos (Nat.lcm_pos (Rat.den_pos _) (Rat.den_pos _))
      (Nat.lcm_pos (Rat.den_pos _) (Rat.den_pos _))
  have hpdR : (0 : ℝ) < ((cellPd a sa sb : Nat) : ℝ) := by exact_mod_cast hpd
  have hx0 : (cellX a sa sb).1.den ∣ cellPd a sa sb :=
    (Nat.dvd_lcm_left _ _).trans (Nat.dvd_lcm_left _ _)
  have hx1 : (cellX a sa sb).2.den ∣ cellPd a sa sb :=
    (Nat.dvd_lcm_right _ _).trans (Nat.dvd_lcm_left _ _)
  have hy0 : (cellY a sa sb).1.den ∣ cellPd a sa sb :=
    (Nat.dvd_lcm_left _ _).trans (Nat.dvd_lcm_right _ _)
  have hy1 : (cellY a sa sb).2.den ∣ cellPd a sa sb :=
    (Nat.dvd_lcm_right _ _).trans (Nat.dvd_lcm_right _ _)
  have ex0 := numOver_cast (cellX a sa sb).1 hx0 hpd
  have ex1 := numOver_cast (cellX a sa sb).2 hx1 hpd
  have ey0 := numOver_cast (cellY a sa sb).1 hy0 hpd
  have ey1 := numOver_cast (cellY a sa sb).2 hy1 hpd
  obtain ⟨bx0, bx1⟩ := affine_between (α := a.alphaX) (β := a.betaX) hsa hsb
  obtain ⟨by0, by1⟩ := affine_between (α := a.alphaY) (β := a.betaY) hsa hsb
  have hcx : cellX a sa sb = rminmax (a.alphaX + a.betaX * sa) (a.alphaX + a.betaX * sb) := rfl
  have hcy : cellY a sa sb = rminmax (a.alphaY + a.betaY * sa) (a.alphaY + a.betaY * sb) := rfl
  rw [← hcx] at bx0 bx1
  rw [← hcy] at by0 by1
  have hA : cellAtom a sa sb = ⟨numOver (cellX a sa sb).1 (cellPd a sa sb),
      numOver (cellX a sa sb).2 (cellPd a sa sb), numOver (cellY a sa sb).1 (cellPd a sa sb),
      numOver (cellY a sa sb).2 (cellPd a sa sb), ((cellPd a sa sb : Nat) : Int), a.w⟩ := rfl
  rw [hA]
  dsimp only [atomPtP]
  refine ⟨by exact_mod_cast hpd, rfl, ?_, ?_, ?_, ?_⟩
  · have e := (div_eq_iff hpdR.ne').mp ex0
    push_cast
    rw [e]
    exact mul_le_mul_of_nonneg_right bx0 hpdR.le
  · have e := (div_eq_iff hpdR.ne').mp ex1
    push_cast
    rw [e]
    exact mul_le_mul_of_nonneg_right bx1 hpdR.le
  · have e := (div_eq_iff hpdR.ne').mp ey0
    push_cast
    rw [e]
    exact mul_le_mul_of_nonneg_right by0 hpdR.le
  · have e := (div_eq_iff hpdR.ne').mp ey1
    push_cast
    rw [e]
    exact mul_le_mul_of_nonneg_right by1 hpdR.le

section CtxFacts

variable {ctx : Ctx}

set_option maxHeartbeats 2000000 in
-- the four-corner interval products (as in A64's `projI_sound`)
/-- `atom_inside_int_iv` is sound: a point whose scaled coordinates lie in the atom's
interval box is inside the square for every parameter of the box, if `insideAll`. -/
theorem projIV_sound {Clo Chi Slo Shi E : Int} {b : IBox} {q : PSq}
    (hD : 0 < ctx.D) (hE : 0 < (E : ℝ))
    (hcos1 : (Clo : ℝ) ≤ cosT q.t * E) (hcos2 : cosT q.t * E ≤ (Chi : ℝ))
    (hsin1 : (Slo : ℝ) ≤ sinT q.t * E) (hsin2 : sinT q.t * E ≤ (Shi : ℝ))
    (hX0 : (b.X0 : ℝ) ≤ q.cx * ctx.D) (hX1 : q.cx * ctx.D ≤ (b.X1 : ℝ))
    (hY0 : (b.Y0 : ℝ) ≤ q.cy * ctx.D) (hY1 : q.cy * ctx.D ≤ (b.Y1 : ℝ))
    {a : IAtomIV} (hpd : 0 < a.pd) {p : RP}
    (hpx0 : (a.pxlo : ℝ) ≤ p.1 * a.pd) (hpx1 : p.1 * a.pd ≤ (a.pxhi : ℝ))
    (hpy0 : (a.pylo : ℝ) ≤ p.2 * a.pd) (hpy1 : p.2 * a.pd ≤ (a.pyhi : ℝ))
    {u0 u1 v0 v1 lim : Int}
    (hp : projIV ctx Clo Chi Slo Shi E b a = (u0, u1, v0, v1, lim)) :
    insideAll u0 u1 v0 v1 lim = true → p ∈ q.set := by
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  have hpdR : (0 : ℝ) < (a.pd : ℝ) := by exact_mod_cast hpd
  have hL : (0 : ℝ) < (E : ℝ) * (a.pd : ℝ) * (ctx.D : ℝ) := by positivity
  simp only [projIV, imul4, Prod.mk.injEq] at hp
  obtain ⟨h1, h2, h3, h4, h5⟩ := hp
  set ydx : ℝ := p.1 * a.pd * ctx.D - q.cx * ctx.D * a.pd with hydx
  set ydy : ℝ := p.2 * a.pd * ctx.D - q.cy * ctx.D * a.pd with hydy
  have hdx0 : ((a.pxlo * ctx.D - b.X1 * a.pd : Int) : ℝ) ≤ ydx := by
    rw [hydx]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hX1 hpdR.le, mul_le_mul_of_nonneg_right hpx0 hDR.le]
  have hdx1 : ydx ≤ ((a.pxhi * ctx.D - b.X0 * a.pd : Int) : ℝ) := by
    rw [hydx]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hX0 hpdR.le, mul_le_mul_of_nonneg_right hpx1 hDR.le]
  have hdy0 : ((a.pylo * ctx.D - b.Y1 * a.pd : Int) : ℝ) ≤ ydy := by
    rw [hydy]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hY1 hpdR.le, mul_le_mul_of_nonneg_right hpy0 hDR.le]
  have hdy1 : ydy ≤ ((a.pyhi * ctx.D - b.Y0 * a.pd : Int) : ℝ) := by
    rw [hydy]
    push_cast
    nlinarith [mul_le_mul_of_nonneg_right hY0 hpdR.le, mul_le_mul_of_nonneg_right hpy1 hDR.le]
  have hCneg1 : ((-Shi : Int) : ℝ) ≤ -(sinT q.t * E) := by push_cast; linarith
  have hCneg2 : -(sinT q.t * E) ≤ ((-Slo : Int) : ℝ) := by push_cast; linarith
  have hA := imul4_cast_bounds hcos1 hcos2 hdx0 hdx1
  have hB := imul4_cast_bounds hsin1 hsin2 hdy0 hdy1
  have hC := imul4_cast_bounds hCneg1 hCneg2 hdx0 hdx1
  have hD' := imul4_cast_bounds hcos1 hcos2 hdy0 hdy1
  push_cast at hA hB hC hD'
  set uR : ℝ := rdot (p.1 - q.cx, p.2 - q.cy) (edir q) with huR
  set vR : ℝ := rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q)) with hvR
  have huval : (cosT q.t * E) * ydx + (sinT q.t * E) * ydy
      = uR * ((E : ℝ) * (a.pd : ℝ) * (ctx.D : ℝ)) := by
    rw [huR]
    simp only [rdot, edir, hydx, hydy]
    ring
  have hvval : (-(sinT q.t * E)) * ydx + (cosT q.t * E) * ydy
      = vR * ((E : ℝ) * (a.pd : ℝ) * (ctx.D : ℝ)) := by
    rw [hvR]
    simp only [rdot, edir, perpV, hydx, hydy]
    ring
  have hu0 : (u0 : ℝ) ≤ 2 * (uR * ((E : ℝ) * a.pd * ctx.D)) := by
    rw [← h1, ← huval]
    push_cast
    linarith [hA.1, hB.1]
  have hu1 : 2 * (uR * ((E : ℝ) * a.pd * ctx.D)) ≤ (u1 : ℝ) := by
    rw [← h2, ← huval]
    push_cast
    linarith [hA.2, hB.2]
  have hv0 : (v0 : ℝ) ≤ 2 * (vR * ((E : ℝ) * a.pd * ctx.D)) := by
    rw [← h3, ← hvval]
    push_cast
    linarith [hC.1, hD'.1]
  have hv1 : 2 * (vR * ((E : ℝ) * a.pd * ctx.D)) ≤ (v1 : ℝ) := by
    rw [← h4, ← hvval]
    push_cast
    linarith [hC.2, hD'.2]
  have hlim : (lim : ℝ) = (E : ℝ) * a.pd * ctx.D := by rw [← h5]; push_cast; ring
  intro hin
  simp only [insideAll, Bool.and_eq_true, decide_eq_true_eq] at hin
  obtain ⟨⟨⟨hiu1, hiu0⟩, hiv1⟩, hiv0⟩ := hin
  have hiu1' : (u1 : ℝ) ≤ (lim : ℝ) := by exact_mod_cast hiu1
  have hiu0' : (-(lim : ℝ)) ≤ (u0 : ℝ) := by exact_mod_cast hiu0
  have hiv1' : (v1 : ℝ) ≤ (lim : ℝ) := by exact_mod_cast hiv1
  have hiv0' : (-(lim : ℝ)) ≤ (v0 : ℝ) := by exact_mod_cast hiv0
  rw [hlim] at hiu1' hiu0' hiv1' hiv0'
  have hu : |uR| ≤ 1 / 2 := by
    rw [abs_le]
    constructor <;> nlinarith
  have hv : |vR| ≤ 1 / 2 := by
    rw [abs_le]
    constructor <;> nlinarith
  rw [mem_set_iff_uv, ← huR, ← hvR]
  exact ⟨hu, hv⟩

/-- `PVerifier.covered` on an s-cell is sound at every side `s` of the cell. -/
theorem siftP_sound {Clo Chi Slo Shi E : Int} {b : IBox} {q : PSq} {sa sb : ℚ} {s : ℝ}
    (hD : 0 < ctx.D) (hE : 0 < (E : ℝ))
    (hcos1 : (Clo : ℝ) ≤ cosT q.t * E) (hcos2 : cosT q.t * E ≤ (Chi : ℝ))
    (hsin1 : (Slo : ℝ) ≤ sinT q.t * E) (hsin2 : sinT q.t * E ≤ (Shi : ℝ))
    (hX0 : (b.X0 : ℝ) ≤ q.cx * ctx.D) (hX1 : q.cx * ctx.D ≤ (b.X1 : ℝ))
    (hY0 : (b.Y0 : ℝ) ≤ q.cy * ctx.D) (hY1 : q.cy * ctx.D ≤ (b.Y1 : ℝ))
    (hsa : (sa : ℝ) ≤ s) (hsb : s ≤ (sb : ℝ)) (pick : PAtom → Bool) :
    ∀ (l : List PAtom) (sure : Int) (acc : List PAtom) (cov : Bool) (sure' : Int)
      (rest : List PAtom),
      (∀ a ∈ l, 0 ≤ a.w) → (∀ a ∈ acc, 0 ≤ a.w) →
      siftP ctx Clo Chi Slo Shi E b sa sb pick l sure acc = (cov, sure', rest) →
      ((sure' : ℝ) + massP rest s q.set
          ≤ (sure : ℝ) + massP l s q.set + massP acc s q.set) ∧
      (cov = true → ctx.NEED ≤ sure') ∧
      (∀ a ∈ rest, 0 ≤ a.w) := by
  intro l
  induction l with
  | nil =>
    intro sure acc cov sure' rest hl hacc hs
    rw [siftP] at hs
    simp only [Prod.mk.injEq] at hs
    obtain ⟨hc, hsu, hre⟩ := hs
    subst hsu
    subst hre
    refine ⟨by simp, ?_, hacc⟩
    intro hcov
    rw [← hc] at hcov
    exact of_decide_eq_true hcov
  | cons a as ih =>
    intro sure acc cov sure' rest hl hacc hs
    have hva := hl a (List.mem_cons_self ..)
    have hvas : ∀ x ∈ as, 0 ≤ x.w := fun x hx => hl x (List.mem_cons_of_mem a hx)
    rw [siftP] at hs
    split at hs
    · next hstop =>
      simp only [Prod.mk.injEq] at hs
      obtain ⟨hc, hsu, hre⟩ := hs
      subst hsu
      subst hre
      have hnn : 0 ≤ massP (a :: as) s q.set := massP_nonneg hl _ _
      exact ⟨by linarith, fun _ => hstop, hacc⟩
    · next hstop =>
      rcases hp : projIV ctx Clo Chi Slo Shi E b (cellAtom a sa sb) with ⟨u0, u1, v0, v1, lim⟩
      rw [hp] at hs
      dsimp only at hs
      obtain ⟨hpd, hw, hpx0, hpx1, hpy0, hpy1⟩ := cellAtom_sound a hsa hsb
      have hin := projIV_sound hD hE hcos1 hcos2 hsin1 hsin2 hX0 hX1 hY0 hY1 hpd
        hpx0 hpx1 hpy0 hpy1 hp
      split at hs
      · next hins =>
        rw [Bool.and_eq_true] at hins
        obtain ⟨q1, q2, q3⟩ := ih (sure + a.w) acc cov sure' rest hvas hacc hs
        refine ⟨?_, q2, q3⟩
        have hmem := hin hins.2
        have hml : massP (a :: as) s q.set = (a.w : ℝ) + massP as s q.set := by
          rw [massP_cons, Set.indicator_of_mem hmem]
        rw [hml]
        push_cast at q1
        linarith
      · next _ =>
        have hacc' : ∀ x ∈ a :: acc, 0 ≤ x.w := by
          intro x hx
          rcases List.mem_cons.mp hx with rfl | hx
          · exact hva
          · exact hacc x hx
        obtain ⟨q1, q2, q3⟩ := ih sure (a :: acc) cov sure' rest hvas hacc' hs
        refine ⟨?_, q2, q3⟩
        rw [massP_cons] at q1
        rw [massP_cons]
        linarith

end CtxFacts

/-! ## Exemption at a moving core: translation invariance -/

/-- Membership in a parametrised square is translation-invariant. -/
theorem mem_set_translate (q : PSq) (v : RP) (p : RP) :
    p ∈ q.set ↔ (p.1 - v.1, p.2 - v.2) ∈ (⟨q.cx - v.1, q.cy - v.2, q.t⟩ : PSq).set := by
  rw [mem_set_iff_uv, mem_set_iff_uv]
  simp only [rdot, edir, perpV]
  have e1 : p.1 - v.1 - (q.cx - v.1) = p.1 - q.cx := by ring
  have e2 : p.2 - v.2 - (q.cy - v.2) = p.2 - q.cy := by ring
  rw [e1, e2]

/-- The core at side `s` is the centre-`0` core translated by its centre. -/
theorem coreSetP_iff (K : PCore) (s : ℝ) (p : RP) :
    p ∈ coreSetP K s ↔
      (p.1 - ((K.akx : ℝ) + (K.bkx : ℝ) * s), p.2 - ((K.aky : ℝ) + (K.bky : ℝ) * s))
        ∈ coreSet ⟨0, 0, K.tm, K.a⟩ := by
  simp only [coreSetP, coreSet, Set.mem_ofPred_eq, Rat.cast_zero, sub_zero]

/-- `core_exempt_frac_iv` is sound for every core centre in the declared interval:
the square meets the core `K(s)`. -/
theorem coreExemptIV_sound {K : PCore} {kx0 kx1 ky0 ky1 t0 t1 x0 x1 y0 y1 : ℚ} {q : PSq}
    {s : ℝ}
    (htm0 : (0 : ℚ) ≤ K.tm) (htm1 : K.tm ≤ 1) (haK : (0 : ℚ) ≤ K.a)
    (ht00 : (0 : ℝ) ≤ (t0 : ℝ)) (ht11 : (t1 : ℝ) ≤ 1)
    (hqt0 : (t0 : ℝ) ≤ q.t) (hqt1 : q.t ≤ (t1 : ℝ))
    (hx0 : (x0 : ℝ) ≤ q.cx) (hx1 : q.cx ≤ (x1 : ℝ))
    (hy0 : (y0 : ℝ) ≤ q.cy) (hy1 : q.cy ≤ (y1 : ℝ))
    (hkx0 : (kx0 : ℝ) ≤ (K.akx : ℝ) + (K.bkx : ℝ) * s)
    (hkx1 : (K.akx : ℝ) + (K.bkx : ℝ) * s ≤ (kx1 : ℝ))
    (hky0 : (ky0 : ℝ) ≤ (K.aky : ℝ) + (K.bky : ℝ) * s)
    (hky1 : (K.aky : ℝ) + (K.bky : ℝ) * s ≤ (ky1 : ℝ))
    (h : coreExemptIV K kx0 kx1 ky0 ky1 t0 t1 x0 x1 y0 y1 = true) :
    (q.set ∩ coreSetP K s).Nonempty := by
  set kx : ℝ := (K.akx : ℝ) + (K.bkx : ℝ) * s with hkx
  set ky : ℝ := (K.aky : ℝ) + (K.bky : ℝ) * s with hky
  set q' : PSq := ⟨q.cx - kx, q.cy - ky, q.t⟩ with hq'
  have hx0' : (((x0 - kx1 : ℚ)) : ℝ) ≤ q'.cx := by
    simp only [hq']; push_cast; linarith
  have hx1' : q'.cx ≤ (((x1 - kx0 : ℚ)) : ℝ) := by
    simp only [hq']; push_cast; linarith
  have hy0' : (((y0 - ky1 : ℚ)) : ℝ) ≤ q'.cy := by
    simp only [hq']; push_cast; linarith
  have hy1' : q'.cy ≤ (((y1 - ky0 : ℚ)) : ℝ) := by
    simp only [hq']; push_cast; linarith
  have hqt0' : (t0 : ℝ) ≤ q'.t := hqt0
  have hqt1' : q'.t ≤ (t1 : ℝ) := hqt1
  rw [coreExemptIV] at h
  obtain ⟨p', hp'q, hp'K⟩ := coreExempt_sound (K := ⟨0, 0, K.tm, K.a⟩) htm0 htm1 haK
    ht00 ht11 hqt0' hqt1' hx0' hx1' hy0' hy1' h
  refine ⟨(p'.1 + kx, p'.2 + ky), ?_, ?_⟩
  · rw [mem_set_translate q (kx, ky)]
    have e : ((p'.1 + kx, p'.2 + ky).1 - (kx, ky).1, (p'.1 + kx, p'.2 + ky).2 - (kx, ky).2)
        = p' := by
      ext <;> simp
    rw [e]
    exact hp'q
  · rw [coreSetP_iff]
    have e : ((p'.1 + kx, p'.2 + ky).1 - kx, (p'.1 + kx, p'.2 + ky).2 - ky) = p' := by
      ext <;> simp
    simp only [← hkx, ← hky]
    rw [e]
    exact hp'K

section CtxFacts

variable {ctx : Ctx}

/-- `PVerifier.exempt` is sound at every side of the cell: some core `K(s)` is met. -/
theorem exemptP_sound {cores : List PCore} {sa sb : ℚ} {s : ℝ} {b : IBox} {q : PSq}
    (hR : 0 < ((ctx.TROOT : Int) : ℝ)) (hD : 0 < ((ctx.D : Int) : ℝ))
    (hT0 : 0 ≤ b.T0) (hT1 : b.T1 ≤ ctx.TROOT)
    (hq : inBox ctx b q) (hsa : (sa : ℝ) ≤ s) (hsb : s ≤ (sb : ℝ))
    (hcores : ∀ K ∈ cores, coreOKP K = true)
    (h : exemptP ctx cores sa sb b = true) :
    ∃ K ∈ cores, (q.set ∩ coreSetP K s).Nonempty := by
  obtain ⟨hqT0, hqT1, hqX0, hqX1, hqY0, hqY1⟩ := hq
  have et0 : (((b.T0 : ℚ) / (ctx.TROOT : ℚ) : ℚ) : ℝ) = (b.T0 : ℝ) / (ctx.TROOT : ℝ) := by
    push_cast; ring
  have et1 : (((b.T1 : ℚ) / (ctx.TROOT : ℚ) : ℚ) : ℝ) = (b.T1 : ℝ) / (ctx.TROOT : ℝ) := by
    push_cast; ring
  have ex0 : (((b.X0 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.X0 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have ex1 : (((b.X1 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.X1 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have ey0 : (((b.Y0 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.Y0 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have ey1 : (((b.Y1 : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) = (b.Y1 : ℝ) / (ctx.D : ℝ) := by
    push_cast; ring
  have hqt0 : ((b.T0 : ℝ) / (ctx.TROOT : ℝ)) ≤ q.t := by
    rw [div_le_iff₀ hR]; exact hqT0
  have hqt1 : q.t ≤ (b.T1 : ℝ) / (ctx.TROOT : ℝ) := by
    rw [le_div_iff₀ hR]; exact hqT1
  have hx0 : ((b.X0 : ℝ) / (ctx.D : ℝ)) ≤ q.cx := by
    rw [div_le_iff₀ hD]; exact hqX0
  have hx1 : q.cx ≤ (b.X1 : ℝ) / (ctx.D : ℝ) := by
    rw [le_div_iff₀ hD]; exact hqX1
  have hy0 : ((b.Y0 : ℝ) / (ctx.D : ℝ)) ≤ q.cy := by
    rw [div_le_iff₀ hD]; exact hqY0
  have hy1 : q.cy ≤ (b.Y1 : ℝ) / (ctx.D : ℝ) := by
    rw [le_div_iff₀ hD]; exact hqY1
  have ht00 : (0 : ℝ) ≤ (b.T0 : ℝ) / (ctx.TROOT : ℝ) := by
    apply div_nonneg _ hR.le
    exact_mod_cast hT0
  have ht11 : (b.T1 : ℝ) / (ctx.TROOT : ℝ) ≤ 1 := by
    rw [div_le_one hR]
    exact_mod_cast hT1
  simp only [exemptP, List.any_eq_true] at h
  obtain ⟨K, hK, hex⟩ := h
  have hOK := hcores K hK
  simp only [coreOKP, Bool.and_eq_true, decide_eq_true_eq] at hOK
  obtain ⟨⟨htm0, htm1⟩, ha⟩ := hOK
  obtain ⟨bx0, bx1⟩ := affine_between (α := K.akx) (β := K.bkx) hsa hsb
  obtain ⟨by0, by1⟩ := affine_between (α := K.aky) (β := K.bky) hsa hsb
  have hcc : cellCore K sa sb = ((cellKx K sa sb).1, (cellKx K sa sb).2,
      (cellKy K sa sb).1, (cellKy K sa sb).2) := rfl
  rw [hcc] at hex
  dsimp only at hex
  have hkx : cellKx K sa sb = rminmax (K.akx + K.bkx * sa) (K.akx + K.bkx * sb) := rfl
  have hky : cellKy K sa sb = rminmax (K.aky + K.bky * sa) (K.aky + K.bky * sb) := rfl
  rw [← hkx] at bx0 bx1
  rw [← hky] at by0 by1
  exact ⟨K, hK, coreExemptIV_sound htm0 htm1 (le_of_lt ha)
    (et0 ▸ ht00) (et1 ▸ ht11) (et0 ▸ hqt0) (et1 ▸ hqt1)
    (ex0 ▸ hx0) (ex1 ▸ hx1) (ey0 ▸ hy0) (ey1 ▸ hy1) bx0 bx1 by0 by1 hex⟩

/-! ## The 4-D split and recursion -/

/-- The point `(q, s)` lies in the 4-D box. -/
def inPBox (ctx : Ctx) (p : PBox) (q : PSq) (s : ℝ) : Prop :=
  inBox ctx p.toIBox q ∧ (p.SA : ℝ) ≤ s * (ctx.D : ℝ) ∧ s * (ctx.D : ℝ) ≤ (p.SB : ℝ)

theorem inPBox_withIBox {p : PBox} {b : IBox} {q : PSq} {s : ℝ}
    (hb : inBox ctx b q) (hSA : (p.SA : ℝ) ≤ s * (ctx.D : ℝ))
    (hSB : s * (ctx.D : ℝ) ≤ (p.SB : ℝ)) : inPBox ctx (p.withIBox b) q s :=
  ⟨hb, hSA, hSB⟩

/-- The four-axis split covers the 4-D box. -/
theorem splitP_sound (ts ss : Int) {p : PBox} {q : PSq} {s : ℝ} (hq : inPBox ctx p q s)
    (hT0 : 0 ≤ p.T0) (hT1 : p.T1 ≤ ctx.TROOT) :
    (inPBox ctx (splitP ctx ts ss p).1 q s ∧ 0 ≤ (splitP ctx ts ss p).1.T0 ∧
        (splitP ctx ts ss p).1.T1 ≤ ctx.TROOT) ∨
    (inPBox ctx (splitP ctx ts ss p).2 q s ∧ 0 ≤ (splitP ctx ts ss p).2.T0 ∧
        (splitP ctx ts ss p).2.T1 ≤ ctx.TROOT) := by
  obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, hs1, hs2⟩ := hq
  have hTle : p.T0 ≤ p.T1 := by exact_mod_cast le_trans h1 h2
  have hXle : p.X0 ≤ p.X1 := by exact_mod_cast le_trans h3 h4
  have hYle : p.Y0 ≤ p.Y1 := by exact_mod_cast le_trans h5 h6
  have hSle : p.SA ≤ p.SB := by exact_mod_cast le_trans hs1 hs2
  obtain ⟨res, hres⟩ : ∃ r, splitP ctx ts ss p = r := ⟨_, rfl⟩
  have hres0 : splitP ctx ts ss p = res := hres
  rw [splitP] at hres
  rw [hres0]
  split at hres
  · -- X split
    have hm1 : p.X0 ≤ (p.X0 + p.X1) / 2 := by omega
    have hm2 : (p.X0 + p.X1) / 2 ≤ p.X1 := by omega
    rw [← hres]
    dsimp only
    rcases le_total (q.cx * (ctx.D : ℝ)) (((p.X0 + p.X1) / 2 : Int) : ℝ) with hc | hc
    · exact Or.inl ⟨⟨⟨h1, h2, h3, hc, h5, h6⟩, hs1, hs2⟩, hT0, hT1⟩
    · exact Or.inr ⟨⟨⟨h1, h2, hc, h4, h5, h6⟩, hs1, hs2⟩, hT0, hT1⟩
  · split at hres
    · -- Y split
      have hm1 : p.Y0 ≤ (p.Y0 + p.Y1) / 2 := by omega
      have hm2 : (p.Y0 + p.Y1) / 2 ≤ p.Y1 := by omega
      rw [← hres]
      dsimp only
      rcases le_total (q.cy * (ctx.D : ℝ)) (((p.Y0 + p.Y1) / 2 : Int) : ℝ) with hc | hc
      · exact Or.inl ⟨⟨⟨h1, h2, h3, h4, h5, hc⟩, hs1, hs2⟩, hT0, hT1⟩
      · exact Or.inr ⟨⟨⟨h1, h2, h3, h4, hc, h6⟩, hs1, hs2⟩, hT0, hT1⟩
    · split at hres
      · -- T split
        have hm1 : p.T0 ≤ (p.T0 + p.T1) / 2 := by omega
        have hm2 : (p.T0 + p.T1) / 2 ≤ p.T1 := by omega
        rw [← hres]
        dsimp only
        rcases le_total (q.t * (ctx.TROOT : ℝ)) (((p.T0 + p.T1) / 2 : Int) : ℝ) with hc | hc
        · exact Or.inl ⟨⟨⟨h1, hc, h3, h4, h5, h6⟩, hs1, hs2⟩, hT0, le_trans hm2 hT1⟩
        · exact Or.inr ⟨⟨⟨hc, h2, h3, h4, h5, h6⟩, hs1, hs2⟩, le_trans hT0 hm1, hT1⟩
      · -- S split
        have hm1 : p.SA ≤ (p.SA + p.SB) / 2 := by omega
        have hm2 : (p.SA + p.SB) / 2 ≤ p.SB := by omega
        rw [← hres]
        dsimp only
        rcases le_total (s * (ctx.D : ℝ)) (((p.SA + p.SB) / 2 : Int) : ℝ) with hc | hc
        · exact Or.inr ⟨⟨⟨h1, h2, h3, h4, h5, h6⟩, hs1, hc⟩, hT0, hT1⟩
        · exact Or.inl ⟨⟨⟨h1, h2, h3, h4, h5, h6⟩, hc, hs2⟩, hT0, hT1⟩

/-- The 4-D branch-and-bound recursion is sound at every side of every cell: on a
passing box, every placement in the box admissible at side `s` that misses every core
`K(s)` carries certified-plus-remaining mass `≥ NEED`. -/
theorem goP_sound (ts ss : Int) {cores : List PCore}
    (pick : PBox → List PAtom → Int → PAtom → Bool)
    (hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2) (hR : 0 < (ctx.TROOT : ℝ))
    (hD : 0 < ctx.D)
    (hcoresOK : ∀ K ∈ cores, coreOKP K = true) :
    ∀ (fuel : Nat) (p : PBox) (l : List PAtom) (sure : Int),
      (∀ a ∈ l, 0 ≤ a.w) → 0 ≤ p.T0 → p.T1 ≤ ctx.TROOT →
      goP ctx ts ss cores pick fuel p l sure = true →
      ∀ (s : ℝ) (q : PSq), 0 ≤ q.t → q.t ≤ 1 → inPBox ctx p q s → Adm s q →
      (∀ K ∈ cores, Disjoint q.set (coreSetP K s)) →
      (ctx.NEED : ℝ) ≤ (sure : ℝ) + massP l s q.set := by
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  intro fuel
  induction fuel with
  | zero =>
    intro p l sure hl hbT0 hbT1 hgo s q hq0 hq1 hpbox hadm hfree
    obtain ⟨hbox, hSA, hSB⟩ := hpbox
    -- admissibility at the cell's wall
    have hsb : s ≤ (p.SB : ℝ) / (ctx.D : ℝ) := by rw [le_div_iff₀ hDR]; exact hSB
    have hadm' : Adm ((p.SB : ℝ) / (ctx.D : ℝ)) q := by
      obtain ⟨a1, a2, a3, a4⟩ := hadm
      exact ⟨a1, by linarith, a3, by linarith⟩
    have hSD' : ((ctxAt ctx p.SB).SD : ℝ)
        = ((p.SB : ℝ) / (ctx.D : ℝ)) * ((ctxAt ctx p.SB).D : ℝ) := by
      change (p.SB : ℝ) = ((p.SB : ℝ) / (ctx.D : ℝ)) * (ctx.D : ℝ)
      field_simp
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ :=
      clipI_sound (ctx := ctxAt ctx p.SB) hP4 hR hD hSD' hbT0 hbox hadm'
    rw [goP, hclip] at hgo
    dsimp only at hgo
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1i : b'.T1 ≤ ctx.TROOT := hT1eq ▸ hbT1
    have hbox'' : inBox ctx b' q := hbox'
    have hsaR : (((p.SA : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) ≤ s := by
      push_cast
      rw [div_le_iff₀ hDR]; exact hSA
    have hsbR : s ≤ (((p.SB : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) := by
      push_cast
      rw [le_div_iff₀ hDR]; exact hSB
    split at hgo
    · next hex =>
      obtain ⟨K, hK, hne⟩ := exemptP_sound hR hDR hT0' hT1i hbox'' hsaR hsbR hcoresOK hex
      exact absurd (Set.disjoint_iff_inter_eq_empty.mp (hfree K hK)) hne.ne_empty
    · next _ =>
      rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
      rw [hbt] at hgo
      dsimp only at hgo
      simp only [boxTrig, trig, Prod.mk.injEq] at hbt
      obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
      have hT1' : (b'.T1 : ℝ) ≤ (ctx.TROOT : ℝ) := by exact_mod_cast hT1i
      obtain ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩ := hbox''
      have henc := trig_enclosure hP4 hR hT0' hT1' hbt0 hbt1
      have hEpos : 0 < (E : ℝ) := by rw [← hE]; exact_mod_cast henc.1
      have hc1 : (Clo : ℝ) ≤ cosT q.t * E := by
        rw [← hClo, ← hE]; exact_mod_cast henc.2.1
      have hc2 : cosT q.t * E ≤ (Chi : ℝ) := by
        rw [← hChi, ← hE]; exact_mod_cast henc.2.2.1
      have hs1 : (Slo : ℝ) ≤ sinT q.t * E := by
        rw [← hSlo, ← hE]; exact_mod_cast henc.2.2.2.1
      have hs2 : sinT q.t * E ≤ (Shi : ℝ) := by
        rw [← hShi, ← hE]; exact_mod_cast henc.2.2.2.2
      rcases hsift : siftP ctx Clo Chi Slo Shi E b' ((p.SA : ℚ) / (ctx.D : ℚ))
        ((p.SB : ℚ) / (ctx.D : ℚ)) (pick (p.withIBox b') l sure) l sure []
        with ⟨cov, sure', rest⟩
      obtain ⟨p1, p2, p3⟩ := siftP_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
        hsaR hsbR (pick (p.withIBox b') l sure) l sure [] cov sure' rest hl (by simp) hsift
      rw [hsift] at hgo
      dsimp only at hgo
      have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hgo
      have hrest0 : 0 ≤ massP rest s q.set := massP_nonneg p3 _ _
      have hnil : massP ([] : List PAtom) s q.set = 0 := rfl
      linarith
  | succ f ih =>
    intro p l sure hl hbT0 hbT1 hgo s q hq0 hq1 hpbox hadm hfree
    obtain ⟨hbox, hSA, hSB⟩ := hpbox
    have hsb : s ≤ (p.SB : ℝ) / (ctx.D : ℝ) := by rw [le_div_iff₀ hDR]; exact hSB
    have hadm' : Adm ((p.SB : ℝ) / (ctx.D : ℝ)) q := by
      obtain ⟨a1, a2, a3, a4⟩ := hadm
      exact ⟨a1, by linarith, a3, by linarith⟩
    have hSD' : ((ctxAt ctx p.SB).SD : ℝ)
        = ((p.SB : ℝ) / (ctx.D : ℝ)) * ((ctxAt ctx p.SB).D : ℝ) := by
      change (p.SB : ℝ) = ((p.SB : ℝ) / (ctx.D : ℝ)) * (ctx.D : ℝ)
      field_simp
    obtain ⟨b', hclip, hbox', hT0eq, hT1eq⟩ :=
      clipI_sound (ctx := ctxAt ctx p.SB) hP4 hR hD hSD' hbT0 hbox hadm'
    rw [goP, hclip] at hgo
    dsimp only at hgo
    have hT0' : 0 ≤ b'.T0 := hT0eq ▸ hbT0
    have hT1i : b'.T1 ≤ ctx.TROOT := hT1eq ▸ hbT1
    have hbox'' : inBox ctx b' q := hbox'
    have hsaR : (((p.SA : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) ≤ s := by
      push_cast
      rw [div_le_iff₀ hDR]; exact hSA
    have hsbR : s ≤ (((p.SB : ℚ) / (ctx.D : ℚ) : ℚ) : ℝ) := by
      push_cast
      rw [le_div_iff₀ hDR]; exact hSB
    split at hgo
    · next hex =>
      obtain ⟨K, hK, hne⟩ := exemptP_sound hR hDR hT0' hT1i hbox'' hsaR hsbR hcoresOK hex
      exact absurd (Set.disjoint_iff_inter_eq_empty.mp (hfree K hK)) hne.ne_empty
    · next _ =>
      rcases hbt : boxTrig ctx b'.T0 b'.T1 with ⟨Clo, Chi, Slo, Shi, E⟩
      rw [hbt] at hgo
      dsimp only at hgo
      simp only [boxTrig, trig, Prod.mk.injEq] at hbt
      obtain ⟨hClo, hChi, hSlo, hShi, hE⟩ := hbt
      have hT1' : (b'.T1 : ℝ) ≤ (ctx.TROOT : ℝ) := by exact_mod_cast hT1i
      obtain ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩ := hbox''
      have henc := trig_enclosure hP4 hR hT0' hT1' hbt0 hbt1
      have hEpos : 0 < (E : ℝ) := by rw [← hE]; exact_mod_cast henc.1
      have hc1 : (Clo : ℝ) ≤ cosT q.t * E := by
        rw [← hClo, ← hE]; exact_mod_cast henc.2.1
      have hc2 : cosT q.t * E ≤ (Chi : ℝ) := by
        rw [← hChi, ← hE]; exact_mod_cast henc.2.2.1
      have hs1 : (Slo : ℝ) ≤ sinT q.t * E := by
        rw [← hSlo, ← hE]; exact_mod_cast henc.2.2.2.1
      have hs2 : sinT q.t * E ≤ (Shi : ℝ) := by
        rw [← hShi, ← hE]; exact_mod_cast henc.2.2.2.2
      rcases hsift : siftP ctx Clo Chi Slo Shi E b' ((p.SA : ℚ) / (ctx.D : ℚ))
        ((p.SB : ℚ) / (ctx.D : ℚ)) (pick (p.withIBox b') l sure) l sure []
        with ⟨cov, sure', rest⟩
      obtain ⟨p1, p2, p3⟩ := siftP_sound hD hEpos hc1 hc2 hs1 hs2 hbx0 hbx1 hby0 hby1
        hsaR hsbR (pick (p.withIBox b') l sure) l sure [] cov sure' rest hl (by simp) hsift
      rw [hsift] at hgo
      dsimp only at hgo
      have hrest0 : 0 ≤ massP rest s q.set := massP_nonneg p3 _ _
      have hnil : massP ([] : List PAtom) s q.set = 0 := rfl
      split at hgo
      · next hcov =>
        have hneed : (ctx.NEED : ℝ) ≤ (sure' : ℝ) := by exact_mod_cast p2 hcov
        linarith
      · next _ =>
        rw [Bool.and_eq_true] at hgo
        obtain ⟨hg1, hg2⟩ := hgo
        have hpb : inPBox ctx (p.withIBox b') q s :=
          inPBox_withIBox ⟨hbt0, hbt1, hbx0, hbx1, hby0, hby1⟩ hSA hSB
        have hwT0 : 0 ≤ (p.withIBox b').T0 := hT0'
        have hwT1 : (p.withIBox b').T1 ≤ ctx.TROOT := hT1i
        rcases splitP_sound ts ss hpb hwT0 hwT1 with ⟨hin1, hi0, hi1⟩ | ⟨hin2, hi0, hi1⟩
        · have := ih (splitP ctx ts ss (p.withIBox b')).1 rest sure' p3 hi0 hi1 hg1 s q hq0 hq1
            hin1 hadm hfree
          linarith
        · have := ih (splitP ctx ts ss (p.withIBox b')).2 rest sure' p3 hi0 hi1 hg2 s q hq0 hq1
            hin2 hadm hfree
          linarith

end CtxFacts

/-! ## The root grid -/

/-- A placement admissible at some side of the window lies in some root cell. -/
theorem rootGridP_cover (ctx : Ctx) (SA SB : Int) (k : Nat)
    (hok : gridOK ctx SB k = true) {q : PSq} {s : ℝ}
    (hT0 : (0 : ℝ) ≤ q.t * (ctx.TROOT : ℝ)) (hT1 : q.t * (ctx.TROOT : ℝ) ≤ (ctx.TROOT : ℝ))
    (hX0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cx * (ctx.D : ℝ))
    (hX1 : q.cx * (ctx.D : ℝ) ≤ ((SB - ctx.D / 2 : Int) : ℝ))
    (hY0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cy * (ctx.D : ℝ))
    (hY1 : q.cy * (ctx.D : ℝ) ≤ ((SB - ctx.D / 2 : Int) : ℝ))
    (hSA : (SA : ℝ) ≤ s * (ctx.D : ℝ)) (hSB : s * (ctx.D : ℝ) ≤ (SB : ℝ)) :
    ∃ p ∈ rootGridP ctx SA SB k, inPBox ctx p q s ∧ p.T0 = 0 ∧ p.T1 = ctx.TROOT := by
  simp only [gridOK, beq_iff_eq] at hok
  have hm : 0 < 2 ^ k := Nat.two_pow_pos k
  obtain ⟨i, hi, hi0, hi1⟩ :=
    grid_cell (lo := ctx.D / 2) (hi := SB - ctx.D / 2) hm hok hX0 hX1
  obtain ⟨j, hj, hj0, hj1⟩ :=
    grid_cell (lo := ctx.D / 2) (hi := SB - ctx.D / 2) hm hok hY0 hY1
  set st : Int := (SB - ctx.D / 2 - ctx.D / 2) / ((2 ^ k : Nat) : Int) with hst
  refine ⟨⟨0, ctx.TROOT, ctx.D / 2 + st * (i : Int), ctx.D / 2 + st * ((i : Int) + 1),
      ctx.D / 2 + st * (j : Int), ctx.D / 2 + st * ((j : Int) + 1), SA, SB⟩, ?_, ?_⟩
  · simp only [rootGridP, List.mem_flatMap, List.mem_map, List.mem_range]
    exact ⟨i, hi, j, hj, rfl⟩
  · refine ⟨⟨⟨?_, hT1, hi0, hi1, hj0, hj1⟩, hSA, hSB⟩, rfl, rfl⟩
    change ((0 : Int) : ℝ) ≤ q.t * (ctx.TROOT : ℝ)
    push_cast
    exact hT0

/-! ## The top-level checker gates -/

/-- The window `[s_lo, s_hi]` as reals. -/
def paramLo (c : PCertI) : ℝ := (c.saNum : ℝ) / (c.sDen : ℝ)
def paramHi (c : PCertI) : ℝ := (c.sbNum : ℝ) / (c.sDen : ℝ)

theorem checkParamI_facts {c : PCertI} {ts ss : Int} {k : Nat}
    {pick : PBox → List PAtom → Int → PAtom → Bool}
    (h : checkParamI c ts ss k pick = true) :
    0 < c.sDen ∧ 0 < c.wd ∧ c.wd ≤ c.need ∧ (∀ a ∈ c.atoms, 0 ≤ a.w) ∧
    (∀ K ∈ c.cores, coreOKP K = true) ∧ c.cores.length ≤ c.n ∧
    (c.atoms.foldl (fun acc a => acc + a.w) 0
        < ((c.n : Int) - (c.cores.length : Int)) * c.wd) ∧
    c.saNum ≤ c.sbNum ∧
    gridOK (mkCtxP c) (sbRoot c) k = true ∧
    (∀ p ∈ rootGridP (mkCtxP c) (saRoot c) (sbRoot c) k,
      goP (mkCtxP c) ts ss c.cores pick (c.depth - 2 * k) p c.atoms 0 = true) := by
  rw [checkParamI] at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩, -⟩, h10⟩, h11⟩ := h
  refine ⟨of_decide_eq_true h1, of_decide_eq_true h2, of_decide_eq_true h3, ?_, ?_,
    of_decide_eq_true h6, of_decide_eq_true h7, of_decide_eq_true h8, h10, ?_⟩
  · intro a ha
    exact of_decide_eq_true (List.all_eq_true.mp h4 a ha)
  · intro K hK
    exact List.all_eq_true.mp h5 K hK
  · intro p hp
    exact List.all_eq_true.mp h11 p hp

/-- **The window coverage/pricing theorem — claim (P2) at every side of the window,
scaled by `wd`.**  A passing parametric checker certifies that, for every real
`s ∈ [s_lo, s_hi]`, every admissible placement at side `s` that misses every core
`K(s)` carries `μ_s`-mass `≥ wd` (i.e. `μ_s(Q) ≥ 1`). -/
theorem checkParamI_price {c : PCertI} {ts ss : Int} {k : Nat}
    {pick : PBox → List PAtom → Int → PAtom → Bool}
    (h : checkParamI c ts ss k pick = true) :
    ∀ s : ℝ, paramLo c ≤ s → s ≤ paramHi c →
    ∀ q : PSq, 0 ≤ q.t → q.t ≤ 1 → q.set ⊆ container s →
      (∀ K ∈ c.cores, Disjoint q.set (coreSetP K s)) →
      (c.wd : ℝ) ≤ massP c.atoms s q.set := by
  obtain ⟨hsd, hwd, hwn, hat, hcoresOK, hrn, htot, hab, hgrid, hall⟩ := checkParamI_facts h
  intro s hslo hshi q hq0 hq1 hsub hfree
  set ctx := mkCtxP c with hctx
  have hTR : ctx.TROOT = (2 : Int) ^ (c.depth + 1) := rfl
  have hR : (0 : ℝ) < (ctx.TROOT : ℝ) := by
    rw [hTR]; push_cast; positivity
  have hP4' : ctx.P4 = ctx.TROOT * ctx.TROOT := by
    change (4 : Int) ^ (c.depth + 1) = (2 : Int) ^ (c.depth + 1) * (2 : Int) ^ (c.depth + 1)
    rw [← mul_pow]
    norm_num
  have hP4 : (ctx.P4 : ℝ) = (ctx.TROOT : ℝ) ^ 2 := by
    rw [hP4']; push_cast; ring
  have hD : 0 < ctx.D := by
    change 0 < c.sDen * (2 : Int) ^ (c.depth + 2)
    positivity
  have hDR : (0 : ℝ) < (ctx.D : ℝ) := by exact_mod_cast hD
  have hsdR : (0 : ℝ) < (c.sDen : ℝ) := by exact_mod_cast hsd
  have hpow : (0 : ℝ) < ((2 : Int) ^ (c.depth + 2) : Int) := by positivity
  have hSAR : ((saRoot c : Int) : ℝ) = paramLo c * (ctx.D : ℝ) := by
    change ((c.saNum * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
        = ((c.saNum : ℝ) / (c.sDen : ℝ)) * ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
    push_cast
    field_simp
  have hSBR : ((sbRoot c : Int) : ℝ) = paramHi c * (ctx.D : ℝ) := by
    change ((c.sbNum * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
        = ((c.sbNum : ℝ) / (c.sDen : ℝ)) * ((c.sDen * (2 : Int) ^ (c.depth + 2) : Int) : ℝ)
    push_cast
    field_simp
  obtain ⟨a1, a2, a3, a4⟩ := (set_subset_container_iff hq0 hq1 s).mp hsub
  have hadm : Adm s q := ⟨a1, a2, a3, a4⟩
  have hw1 := wT_ge_one hq0 hq1
  have hlo : ((ctx.D / 2 : Int) : ℝ) ≤ (ctx.D : ℝ) / 2 := cast_ediv_le (by norm_num)
  have hSA : ((saRoot c : Int) : ℝ) ≤ s * (ctx.D : ℝ) := by
    rw [hSAR]; exact mul_le_mul_of_nonneg_right hslo hDR.le
  have hSB : s * (ctx.D : ℝ) ≤ ((sbRoot c : Int) : ℝ) := by
    rw [hSBR]; exact mul_le_mul_of_nonneg_right hshi hDR.le
  have hX0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cx * (ctx.D : ℝ) := by nlinarith [a1, hw1]
  have hX1 : q.cx * (ctx.D : ℝ) ≤ ((sbRoot c - ctx.D / 2 : Int) : ℝ) := by
    push_cast
    nlinarith [a2, hw1, hSBR, hlo]
  have hY0 : ((ctx.D / 2 : Int) : ℝ) ≤ q.cy * (ctx.D : ℝ) := by nlinarith [a3, hw1]
  have hY1 : q.cy * (ctx.D : ℝ) ≤ ((sbRoot c - ctx.D / 2 : Int) : ℝ) := by
    push_cast
    nlinarith [a4, hw1, hSBR, hlo]
  have hT0 : (0 : ℝ) ≤ q.t * (ctx.TROOT : ℝ) := mul_nonneg hq0 hR.le
  have hT1 : q.t * (ctx.TROOT : ℝ) ≤ (ctx.TROOT : ℝ) := by nlinarith
  obtain ⟨p, hp, hpbox, hp0, hp1⟩ :=
    rootGridP_cover ctx (saRoot c) (sbRoot c) k hgrid hT0 hT1 hX0 hX1 hY0 hY1 hSA hSB
  have hgo := hall p hp
  have hbT0 : 0 ≤ p.T0 := by rw [hp0]
  have hbT1 : p.T1 ≤ ctx.TROOT := by rw [hp1]
  have hmain := goP_sound (ctx := ctx) ts ss pick hP4 hR hD hcoresOK (c.depth - 2 * k) p
    c.atoms 0 hat hbT0 hbT1 hgo s q hq0 hq1 hpbox hadm hfree
  have hne : (ctx.NEED : ℝ) = (c.need : ℝ) := rfl
  rw [hne] at hmain
  have hwnR : (c.wd : ℝ) ≤ (c.need : ℝ) := by exact_mod_cast hwn
  simp only [Int.cast_zero, zero_add] at hmain
  linarith

/-! ## The pricing pigeonhole, abstract mass -/

/-- A68/A70's pricing dichotomy for an ABSTRACT mass functional: it needs only
`mass ∅ = 0` and sub-additivity over pairwise-disjoint families (`hsum`). -/
theorem priced_dichotomy_gen {n r : ℕ} {s'' NEEDR total : ℝ} (mass : Set RP → ℝ)
    (hempty : mass ∅ = 0)
    (hsum : ∀ f : Fin n → Set RP, (∀ i j, i ≠ j → Disjoint (f i) (f j)) →
      ∑ i, mass (f i) ≤ total)
    (hN : 0 ≤ NEEDR)
    {K : Fin r → Set RP} {own : Fin r → Fin n}
    (Exempt : Set RP → Prop)
    (price : ∀ S : Set RP, IsUnitSquare S → S ⊆ container s'' →
      (∀ j, Disjoint S (K j)) → ¬Exempt S → NEEDR ≤ mass S)
    (hP1 : total < ((n : ℝ) - (r : ℝ)) * NEEDR)
    {Q : Fin n → Set RP} (hQ : IsStrictFamily n s'' Q)
    (hH : ∀ j, K j ⊆ Q (own j)) :
    ∃ i : Fin n, (∀ j, own j ≠ i) ∧ Exempt (Q i) := by
  by_contra hno
  push Not at hno
  set O : Finset (Fin n) := Finset.image own Finset.univ with hO
  set G : Finset (Fin n) := Oᶜ with hG
  have hGmem : ∀ i : Fin n, i ∈ G ↔ ∀ j, own j ≠ i := by
    intro i
    simp [hG, hO, eq_comm]
  have hprice : ∀ i ∈ G, NEEDR ≤ mass (Q i) := by
    intro i hi
    have hnotown := (hGmem i).mp hi
    refine price (Q i) (hQ.unit i) (hQ.contained i) (fun j => ?_) (hno i hnotown)
    exact (hQ.disjoint i (own j) fun h => hnotown j h.symm).mono_right (hH j)
  have hdisf : ∀ i j : Fin n, i ≠ j →
      Disjoint (if i ∈ G then Q i else (∅ : Set RP)) (if j ∈ G then Q j else ∅) := by
    intro i j hij
    by_cases hi : i ∈ G <;> by_cases hj : j ∈ G <;>
      simp [hi, hj, hQ.disjoint i j hij]
  have hupper : ∑ i ∈ G, mass (Q i) ≤ total := by
    have hpad : ∑ i ∈ G, mass (Q i)
        = ∑ i : Fin n, mass (if i ∈ G then Q i else ∅) := by
      simp only [apply_ite mass, hempty, Finset.sum_ite_mem, Finset.univ_inter]
    rw [hpad]
    exact hsum _ hdisf
  have hOcard : O.card ≤ r := le_trans Finset.card_image_le (by simp)
  have hcards : O.card + G.card = n := by
    have h := Finset.card_add_card_compl O
    simp only [Fintype.card_fin] at h
    exact h
  have hGcard : (n : ℝ) - (r : ℝ) ≤ (G.card : ℝ) := by
    have h1 : (O.card : ℝ) ≤ (r : ℝ) := by exact_mod_cast hOcard
    have h2 : (O.card : ℝ) + (G.card : ℝ) = (n : ℝ) := by exact_mod_cast hcards
    linarith
  have hlower : (G.card : ℝ) * NEEDR ≤ ∑ i ∈ G, mass (Q i) := by
    calc (G.card : ℝ) * NEEDR = ∑ _i ∈ G, NEEDR := by
          rw [Finset.sum_const, nsmul_eq_mul]
      _ ≤ ∑ i ∈ G, mass (Q i) := Finset.sum_le_sum hprice
  have hchain : ((n : ℝ) - (r : ℝ)) * NEEDR ≤ (G.card : ℝ) * NEEDR :=
    mul_le_mul_of_nonneg_right hGcard hN
  linarith

/-! ## The end forms -/

/-- **Parametric certificate soundness, kill form** (V.PARAM): a passing `checkParamI`
proves that at EVERY real side `s` of the window, NO strict family of `n` closed unit
squares has designated owners containing the cores `Kⱼ(s)` — the per-side `hcert`
hypothesis of `lemma_B`, produced for the whole window by one PASS file.  This is the
statement `stratum_kill` (`TopLevel.lean`) consumes for the covered classes. -/
theorem checkParamI_kill {c : PCertI} {ts ss : Int} {k : Nat}
    {pick : PBox → List PAtom → Int → PAtom → Bool}
    (h : checkParamI c ts ss k pick = true)
    {s : ℝ} (hslo : paramLo c ≤ s) (hshi : s ≤ paramHi c)
    {Q : Fin c.n → Set RP} (hQ : IsStrictFamily c.n s Q)
    (own : Fin c.cores.length → Fin c.n)
    (hown : ∀ j : Fin c.cores.length, coreSetP (c.cores.get j) s ⊆ Q (own j)) :
    False := by
  obtain ⟨hsd, hwd, hwn, hat, hcoresOK, hrn, htot, hab, hgrid, hall⟩ := checkParamI_facts h
  have hwdR : (0 : ℝ) ≤ (c.wd : ℝ) := by
    have := le_of_lt hwd
    exact_mod_cast this
  have hP2 : ∀ S : Set RP, IsUnitSquare S → S ⊆ container s →
      (∀ j : Fin c.cores.length, Disjoint S (coreSetP (c.cores.get j) s)) → ¬False →
      (c.wd : ℝ) ≤ massP c.atoms s S := by
    intro S hS hsub hdis _
    obtain ⟨q, hqt, rfl⟩ := isUnitSquare_exists_psq hS
    refine checkParamI_price h s hslo hshi q hqt.1 hqt.2 hsub ?_
    intro K hK
    obtain ⟨j, hj⟩ := List.mem_iff_get.mp hK
    exact hj ▸ hdis j
  have hP1 : (c.atoms.map fun a => (a.w : ℝ)).sum
      < ((c.n : ℝ) - (c.cores.length : ℝ)) * (c.wd : ℝ) := by
    rw [foldlP_add_eq c.atoms 0, zero_add] at htot
    have h2 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ)
        < ((c.n : ℝ) - (c.cores.length : ℝ)) * (c.wd : ℝ) := by
      have hcast : ((((c.n : Int) - (c.cores.length : Int)) * c.wd : Int) : ℝ)
          = ((c.n : ℝ) - (c.cores.length : ℝ)) * (c.wd : ℝ) := by
        push_cast
        ring
      rw [← hcast]
      exact_mod_cast htot
    have h3 : (((c.atoms.map fun a => a.w).sum : Int) : ℝ)
        = (c.atoms.map fun a => ((a.w : ℝ))).sum := by
      push_cast
      rw [List.map_map]
      rfl
    rw [h3] at h2
    exact h2
  obtain ⟨i, -, hex⟩ := priced_dichotomy_gen (K := fun j => coreSetP (c.cores.get j) s)
    (own := own) (massP c.atoms s) (by simp [massP])
    (fun f hdis => massP_sum_le c.atoms hat s hdis) hwdR (fun _ => False) hP2 hP1 hQ hown
  exact hex

/-- **Parametric certificate soundness, packing form**: composed with Lemma B's
λ-dilation (A68 `Dilation.lean`) at any side `s = λ·m` of the window — no
interior-disjoint 11-packing at side `m` realises the dilated core-containment
hypothesis (H) for the cores `Kⱼ(λ·m)`. -/
theorem checkParamI_kill_packing {c : PCertI} (hn : c.n = 11) {ts ss : Int} {k : Nat}
    {pick : PBox → List PAtom → Int → PAtom → Bool}
    (h : checkParamI c ts ss k pick = true)
    {m lam : ℝ} (hlam : 1 < lam)
    (hslo : paramLo c ≤ lam * m) (hshi : lam * m ≤ paramHi c)
    {z : Fin 11 → PSq} (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (hP : IsPacking 11 m fun i => (z i).set)
    (own : Fin c.cores.length → Fin 11)
    (hH : ∀ j : Fin c.cores.length, coreSetP (c.cores.get j) (lam * m)
        ⊆ interior ((scaleC lam (z (own j))).set)) : False := by
  rcases c with ⟨n, sDen, saNum, sbNum, wd, need, depth, atoms, cores⟩
  have hn' : n = 11 := hn
  subst hn'
  exact lemma_B hlam rfl ht hP (fun j => coreSetP (cores.get j) (lam * m)) own
    (fun _Q hQ hI => checkParamI_kill h hslo hshi hQ own
      (fun j => (hI j).trans interior_subset)) hH

end

end S11
end PackingCert
