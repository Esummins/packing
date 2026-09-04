import PackingCertMathlib.Crowd

/-!
# The crowd-zone checker: run B's NO-families avoid the crowd family (A93 T1, K0.CW)

Lemma CW needs `E ∩ F_c(a_w) = ∅` at every corner: no square whose parametrisation lies in a
NO-zone of run B meets the closed corner box `[0, a_w]²`.  The chore certifies this in Python
(exact `Fraction` arithmetic on `corner85.f_min_max`); here it is a Lean checker, so that the
hypothesis `hE` of `crowd_sound` is a certificate-file fact like the two `checkCaseI` PASSes.

`sepTests` — for a pose box `[t0,t1] × [x0,x1] × [y0,y1]` and a rectangle
`[bx0,bx1] × [by0,by1]`, the eight separating-axis tests (the two container axes, the two
edge directions of the square), with the rational trigonometry enclosures of `CaseChecker.lean`
(`ratCosSin`, `rmul4`); `boxMisses` bisects the widest dimension when no test fires;
`crowdZones` runs it for every NO-family, every `t`-interval (clipped to `[0,1]`) and every
corner.  `crowdZones_sound` is the soundness theorem, `crowdKill_of_files` the packaged
Theorem S(δ): four Bool facts about the two files + rational side conditions ⟹ `CrowdKill`.

Axioms: `propext, Classical.choice, Quot.sound`.
-/

namespace PackingCert
namespace S11

open Set MeasureI CaseI

namespace CrowdZ

/-- The rectangle of the corner box `[0,aw]²` at corner `c` of `[0,s]²`, rational. -/
def bx0 (s aw : Rat) (c : Fin 4) : Rat := if cornerR c then s - aw else 0
def bx1 (s aw : Rat) (c : Fin 4) : Rat := if cornerR c then s else aw
def by0 (s aw : Rat) (c : Fin 4) : Rat := if cornerT c then s - aw else 0
def by1 (s aw : Rat) (c : Fin 4) : Rat := if cornerT c then s else aw

/-- The eight separating-axis tests on one pose box. -/
def sepTests (bx0 bx1 by0 by1 t0 t1 x0 x1 y0 y1 : Rat) : Bool :=
  let C0 := (ratCosSin t0).1
  let C1 := (ratCosSin t1).1
  let S0 := (ratCosSin t0).2
  let S1 := (ratCosSin t1).2
  let h := (C0 + S1) / 2
  decide (bx1 < x0 - h) || decide (x1 + h < bx0) ||
  decide (by1 < y0 - h) || decide (y1 + h < by0) ||
  decide (1 / 2 < (rmul4 C1 C0 (x0 - bx1) (x1 - bx1)).1 + (rmul4 S0 S1 (y0 - by1) (y1 - by1)).1) ||
  decide ((rmul4 C1 C0 (x0 - bx0) (x1 - bx0)).2 + (rmul4 S0 S1 (y0 - by0) (y1 - by0)).2 < -1 / 2) ||
  decide (1 / 2 < (rmul4 (-S1) (-S0) (x0 - bx0) (x1 - bx0)).1
    + (rmul4 C1 C0 (y0 - by1) (y1 - by1)).1) ||
  decide ((rmul4 (-S1) (-S0) (x0 - bx1) (x1 - bx1)).2
    + (rmul4 C1 C0 (y0 - by0) (y1 - by0)).2 < -1 / 2)

/-- Branch and bound: the tests, else bisect `t` while its width exceeds `1/32` (the trig
enclosure is the loose part), then the wider of `x`, `y`. -/
def boxMisses (bx0 bx1 by0 by1 : Rat) : Nat → Rat → Rat → Rat → Rat → Rat → Rat → Bool
  | 0, t0, t1, x0, x1, y0, y1 => sepTests bx0 bx1 by0 by1 t0 t1 x0 x1 y0 y1
  | fuel + 1, t0, t1, x0, x1, y0, y1 =>
    sepTests bx0 bx1 by0 by1 t0 t1 x0 x1 y0 y1 ||
    (if (1 / 32 : Rat) < t1 - t0 then
        boxMisses bx0 bx1 by0 by1 fuel t0 ((t0 + t1) / 2) x0 x1 y0 y1 &&
        boxMisses bx0 bx1 by0 by1 fuel ((t0 + t1) / 2) t1 x0 x1 y0 y1
      else if y1 - y0 ≤ x1 - x0 then
        boxMisses bx0 bx1 by0 by1 fuel t0 t1 x0 ((x0 + x1) / 2) y0 y1 &&
        boxMisses bx0 bx1 by0 by1 fuel t0 t1 ((x0 + x1) / 2) x1 y0 y1
      else
        boxMisses bx0 bx1 by0 by1 fuel t0 t1 x0 x1 y0 ((y0 + y1) / 2) &&
        boxMisses bx0 bx1 by0 by1 fuel t0 t1 x0 x1 ((y0 + y1) / 2) y1)

/-- One NO-family: every `t`-interval (clipped to `[0,1]`), every corner. -/
def zoneMisses (s aw : Rat) (fuel : Nat) (f : CNoFam) : Bool :=
  f.tivs.all fun iv =>
    decide (min iv.2 1 < max iv.1 0) ||
    (List.finRange 4).all fun c =>
      boxMisses (bx0 s aw c) (bx1 s aw c) (by0 s aw c) (by1 s aw c) fuel
        (max iv.1 0) (min iv.2 1) f.x0 f.x1 f.y0 f.y1

/-- **The crowd-zone check**: every NO-family of run B misses the crowd family at every corner. -/
def crowdZones (sNum sDen : Int) (aw : Rat) (fuel : Nat) (fs : List CNoFam) : Bool :=
  fs.all (zoneMisses ((sNum : Rat) / (sDen : Rat)) aw fuel)

/-! ## Soundness -/

theorem sepTests_sound {bx0 bx1 by0 by1 t0 t1 x0 x1 y0 y1 : Rat} {q : PSq}
    (ht00 : (0 : ℝ) ≤ (t0 : ℝ)) (ht11 : (t1 : ℝ) ≤ 1)
    (hqt0 : (t0 : ℝ) ≤ q.t) (hqt1 : q.t ≤ (t1 : ℝ))
    (hx0 : (x0 : ℝ) ≤ q.cx) (hx1 : q.cx ≤ (x1 : ℝ))
    (hy0 : (y0 : ℝ) ≤ q.cy) (hy1 : q.cy ≤ (y1 : ℝ))
    (h : sepTests bx0 bx1 by0 by1 t0 t1 x0 x1 y0 y1 = true) :
    ∀ p ∈ q.set, ¬ ((bx0 : ℝ) ≤ p.1 ∧ p.1 ≤ (bx1 : ℝ) ∧ (by0 : ℝ) ≤ p.2 ∧ p.2 ≤ (by1 : ℝ)) := by
  intro p hp ⟨b0, b1, b2, b3⟩
  have hqt00 : 0 ≤ q.t := le_trans ht00 hqt0
  have hqt11 : q.t ≤ 1 := le_trans hqt1 ht11
  have hC0 : 0 ≤ cosT q.t := cosT_nonneg hqt00 hqt11
  have hS0 : 0 ≤ sinT q.t := sinT_nonneg hqt00
  have hCu : cosT q.t ≤ (((ratCosSin t0).1 : ℚ) : ℝ) := by
    rw [ratCosSin_fst]; exact cosT_anti ht00 hqt0
  have hCl : (((ratCosSin t1).1 : ℚ) : ℝ) ≤ cosT q.t := by
    rw [ratCosSin_fst]; exact cosT_anti hqt00 hqt1
  have hSl : (((ratCosSin t0).2 : ℚ) : ℝ) ≤ sinT q.t := by
    rw [ratCosSin_snd]; exact sinT_mono ht00 hqt0 hqt11
  have hSu : sinT q.t ≤ (((ratCosSin t1).2 : ℚ) : ℝ) := by
    rw [ratCosSin_snd]; exact sinT_mono hqt00 hqt1 ht11
  have hnSl : ((-(ratCosSin t1).2 : ℚ) : ℝ) ≤ -(sinT q.t) := by push_cast; linarith
  have hnSu : -(sinT q.t) ≤ ((-(ratCosSin t0).2 : ℚ) : ℝ) := by push_cast; linarith
  obtain ⟨hcx, hcy⟩ := coord_sub_centre_le ⟨hqt00, hqt11⟩ hp
  rw [abs_le] at hcx hcy
  simp only [wT] at hcx hcy
  have huv := (mem_set_iff_uv q p).mp hp
  simp only [rdot, edir, perpV] at huv
  obtain ⟨hu, hv⟩ := huv
  rw [abs_le] at hu hv
  -- centre-offset enclosures
  have hdx1 : ((x0 - bx1 : ℚ) : ℝ) ≤ q.cx - (bx1 : ℝ) := by push_cast; linarith
  have hdx1' : q.cx - (bx1 : ℝ) ≤ ((x1 - bx1 : ℚ) : ℝ) := by push_cast; linarith
  have hdx0 : ((x0 - bx0 : ℚ) : ℝ) ≤ q.cx - (bx0 : ℝ) := by push_cast; linarith
  have hdx0' : q.cx - (bx0 : ℝ) ≤ ((x1 - bx0 : ℚ) : ℝ) := by push_cast; linarith
  have hdy1 : ((y0 - by1 : ℚ) : ℝ) ≤ q.cy - (by1 : ℝ) := by push_cast; linarith
  have hdy1' : q.cy - (by1 : ℝ) ≤ ((y1 - by1 : ℚ) : ℝ) := by push_cast; linarith
  have hdy0 : ((y0 - by0 : ℚ) : ℝ) ≤ q.cy - (by0 : ℝ) := by push_cast; linarith
  have hdy0' : q.cy - (by0 : ℝ) ≤ ((y1 - by0 : ℚ) : ℝ) := by push_cast; linarith
  simp only [sepTests] at h
  simp only [Bool.or_eq_true, decide_eq_true_eq, or_assoc] at h
  rcases h with h | h | h | h | h | h | h | h
  · -- min_Q p_x > bx1
    have h' : ((bx1 : ℚ) : ℝ) < ((x0 - ((ratCosSin t0).1 + (ratCosSin t1).2) / 2 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith
  · have h' : ((x1 + ((ratCosSin t0).1 + (ratCosSin t1).2) / 2 : ℚ) : ℝ) < ((bx0 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith
  · have h' : ((by1 : ℚ) : ℝ) < ((y0 - ((ratCosSin t0).1 + (ratCosSin t1).2) / 2 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith
  · have h' : ((y1 + ((ratCosSin t0).1 + (ratCosSin t1).2) / 2 : ℚ) : ℝ) < ((by0 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith
  · -- edge axis `e`: the box lies strictly below the square
    obtain ⟨ha, -⟩ := rmul4_bounds hCl hCu hdx1 hdx1'
    obtain ⟨hb, -⟩ := rmul4_bounds hSl hSu hdy1 hdy1'
    have h' : ((1 / 2 : ℚ) : ℝ) < (((rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (x0 - bx1) (x1 - bx1)).1
        + (rmul4 (ratCosSin t0).2 (ratCosSin t1).2 (y0 - by1) (y1 - by1)).1 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith [mul_le_mul_of_nonneg_left b1 hC0, mul_le_mul_of_nonneg_left b3 hS0]
  · -- edge axis `e`: the box lies strictly above the square
    obtain ⟨-, ha⟩ := rmul4_bounds hCl hCu hdx0 hdx0'
    obtain ⟨-, hb⟩ := rmul4_bounds hSl hSu hdy0 hdy0'
    have h' : (((rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (x0 - bx0) (x1 - bx0)).2
        + (rmul4 (ratCosSin t0).2 (ratCosSin t1).2 (y0 - by0) (y1 - by0)).2 : ℚ) : ℝ)
        < ((-1 / 2 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith [mul_le_mul_of_nonneg_left b0 hC0, mul_le_mul_of_nonneg_left b2 hS0]
  · -- edge axis `e⊥`
    obtain ⟨ha, -⟩ := rmul4_bounds hnSl hnSu hdx0 hdx0'
    obtain ⟨hb, -⟩ := rmul4_bounds hCl hCu hdy1 hdy1'
    have h' : ((1 / 2 : ℚ) : ℝ) < (((rmul4 (-(ratCosSin t1).2) (-(ratCosSin t0).2) (x0 - bx0) (x1 - bx0)).1
        + (rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (y0 - by1) (y1 - by1)).1 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith [mul_le_mul_of_nonneg_left b0 hS0, mul_le_mul_of_nonneg_left b3 hC0]
  · obtain ⟨-, ha⟩ := rmul4_bounds hnSl hnSu hdx1 hdx1'
    obtain ⟨-, hb⟩ := rmul4_bounds hCl hCu hdy0 hdy0'
    have h' : (((rmul4 (-(ratCosSin t1).2) (-(ratCosSin t0).2) (x0 - bx1) (x1 - bx1)).2
        + (rmul4 (ratCosSin t1).1 (ratCosSin t0).1 (y0 - by0) (y1 - by0)).2 : ℚ) : ℝ)
        < ((-1 / 2 : ℚ) : ℝ) := by
      exact_mod_cast h
    push_cast at h'
    linarith [mul_le_mul_of_nonneg_left b1 hS0, mul_le_mul_of_nonneg_left b2 hC0]

theorem boxMisses_sound {bx0 bx1 by0 by1 : Rat} :
    ∀ (fuel : Nat) {t0 t1 x0 x1 y0 y1 : Rat} {q : PSq},
      (0 : ℝ) ≤ (t0 : ℝ) → (t1 : ℝ) ≤ 1 → (t0 : ℝ) ≤ q.t → q.t ≤ (t1 : ℝ) →
      (x0 : ℝ) ≤ q.cx → q.cx ≤ (x1 : ℝ) → (y0 : ℝ) ≤ q.cy → q.cy ≤ (y1 : ℝ) →
      boxMisses bx0 bx1 by0 by1 fuel t0 t1 x0 x1 y0 y1 = true →
      ∀ p ∈ q.set, ¬ ((bx0 : ℝ) ≤ p.1 ∧ p.1 ≤ (bx1 : ℝ) ∧ (by0 : ℝ) ≤ p.2 ∧ p.2 ≤ (by1 : ℝ)) := by
  intro fuel
  induction fuel with
  | zero =>
    intro t0 t1 x0 x1 y0 y1 q ht00 ht11 hqt0 hqt1 hx0 hx1 hy0 hy1 h
    exact sepTests_sound ht00 ht11 hqt0 hqt1 hx0 hx1 hy0 hy1 h
  | succ n ih =>
    intro t0 t1 x0 x1 y0 y1 q ht00 ht11 hqt0 hqt1 hx0 hx1 hy0 hy1 h
    rw [boxMisses, Bool.or_eq_true] at h
    rcases h with h | h
    · exact sepTests_sound ht00 ht11 hqt0 hqt1 hx0 hx1 hy0 hy1 h
    · split_ifs at h with h1 h2 <;> rw [Bool.and_eq_true] at h <;> obtain ⟨hA, hB⟩ := h
      · -- split in t
        rcases le_total q.t (((t0 + t1) / 2 : ℚ) : ℝ) with hm | hm
        · exact ih ht00 (by push_cast; linarith) hqt0 hm hx0 hx1 hy0 hy1 hA
        · exact ih (by push_cast; linarith) ht11 hm hqt1 hx0 hx1 hy0 hy1 hB
      · rcases le_total q.cx (((x0 + x1) / 2 : ℚ) : ℝ) with hm | hm
        · exact ih ht00 ht11 hqt0 hqt1 hx0 hm hy0 hy1 hA
        · exact ih ht00 ht11 hqt0 hqt1 hm hx1 hy0 hy1 hB
      · rcases le_total q.cy (((y0 + y1) / 2 : ℚ) : ℝ) with hm | hm
        · exact ih ht00 ht11 hqt0 hqt1 hx0 hx1 hy0 hm hA
        · exact ih ht00 ht11 hqt0 hqt1 hx0 hx1 hm hy1 hB

theorem bx0_cast (s aw : Rat) (c : Fin 4) :
    ((bx0 s aw c : ℚ) : ℝ) = if cornerR c then (s : ℝ) - aw else 0 := by
  unfold bx0; split_ifs <;> push_cast <;> rfl
theorem bx1_cast (s aw : Rat) (c : Fin 4) :
    ((bx1 s aw c : ℚ) : ℝ) = if cornerR c then (s : ℝ) else aw := by
  unfold bx1; split_ifs <;> push_cast <;> rfl
theorem by0_cast (s aw : Rat) (c : Fin 4) :
    ((by0 s aw c : ℚ) : ℝ) = if cornerT c then (s : ℝ) - aw else 0 := by
  unfold by0; split_ifs <;> push_cast <;> rfl
theorem by1_cast (s aw : Rat) (c : Fin 4) :
    ((by1 s aw c : ℚ) : ℝ) = if cornerT c then (s : ℝ) else aw := by
  unfold by1; split_ifs <;> push_cast <;> rfl

/-- The corner box is the rectangle of the checker. -/
theorem mem_cornerBox_iff_rect (s aw : Rat) (c : Fin 4) (p : RP) :
    p ∈ cornerBox (s : ℝ) (aw : ℝ) c ↔
      ((bx0 s aw c : ℚ) : ℝ) ≤ p.1 ∧ p.1 ≤ ((bx1 s aw c : ℚ) : ℝ) ∧
      ((by0 s aw c : ℚ) : ℝ) ≤ p.2 ∧ p.2 ≤ ((by1 s aw c : ℚ) : ℝ) := by
  rw [bx0_cast, bx1_cast, by0_cast, by1_cast]
  simp only [cornerBox, cframe, mem_setOf_eq]
  split_ifs <;> constructor <;> rintro ⟨h1, h2, h3, h4⟩ <;>
    exact ⟨by linarith, by linarith, by linarith, by linarith⟩

end CrowdZ

open CrowdZ

/-- **Soundness of the crowd-zone check**: every square with `t ∈ [0,1]` meeting the closed box
`[0, a_w]²` at some corner of `[0, s]²` lies in no NO-zone of the list — the hypothesis `hE`
of `crowd_sound` / `crowd_cert_kill`. -/
theorem crowdZones_sound {c : CCertI} {aw : Rat} {fuel : Nat}
    (h : crowdZones c.sNum c.sDen aw fuel c.nofams = true) :
    ∀ q : PSq, q.t ∈ Icc (0 : ℝ) 1 → q.set ⊆ container (caseSide c) →
      (∃ cc : Fin 4, (q.set ∩ cornerBox (caseSide c) (aw : ℝ) cc).Nonempty) →
      ∀ f ∈ c.nofams, ¬ InZone f q := by
  intro q hqt _ ⟨cc, p, hpq, hpb⟩ f hf hz
  obtain ⟨hx0, hx1, hy0, hy1, iv, hiv, ht0, ht1⟩ := hz
  simp only [crowdZones, List.all_eq_true] at h
  have hf' := h f hf
  simp only [zoneMisses, List.all_eq_true, Bool.or_eq_true, decide_eq_true_eq] at hf'
  rcases hf' iv hiv with hlt | hall
  · have h1 : ((max iv.1 0 : ℚ) : ℝ) ≤ q.t := by
      push_cast; exact max_le ht0 hqt.1
    have h2 : q.t ≤ ((min iv.2 1 : ℚ) : ℝ) := by
      push_cast; exact le_min ht1 hqt.2
    have h3 : ((min iv.2 1 : ℚ) : ℝ) < ((max iv.1 0 : ℚ) : ℝ) := by exact_mod_cast hlt
    linarith
  · have hbox := hall cc (List.mem_finRange cc)
    have hside : caseSide c = (((c.sNum : Rat) / (c.sDen : Rat) : ℚ) : ℝ) := by
      simp only [caseSide]; push_cast; rfl
    rw [hside, mem_cornerBox_iff_rect] at hpb
    refine boxMisses_sound fuel ?_ ?_ ?_ ?_ hx0 hx1 hy0 hy1 hbox p hpq hpb
    · push_cast; exact le_max_right _ _
    · push_cast; exact min_le_right _ _
    · push_cast; exact max_le ht0 hqt.1
    · push_cast; exact le_min ht1 hqt.2

/-! ## The packaged crowd certificate -/

/-- **`C(δ, m_lo)`'s conclusion**: no packing at any side `m ∈ [m_lo, s0)` has two distinct
squares at depth `≥ δ` (meeting the closed box `[0, 1−δ]²`) at every corner. -/
def CrowdKill (δ mlo s0 : ℝ) : Prop :=
  ∀ m, mlo ≤ m → m < s0 → ∀ z : Cfg, CfgPacking m z → ¬ CrowdBox m (1 - δ) z

theorem crowdKill_mono {δ δ' mlo mlo' s0 : ℝ} (h : CrowdKill δ mlo s0) (hδ : δ ≤ δ')
    (hm : mlo ≤ mlo') : CrowdKill δ' mlo' s0 := by
  intro m hlo hhi z hz hcr
  exact h m (le_trans hm hlo) hhi z hz (crowdBox_mono (by linarith) hcr)

/-- **Theorem S(δ) from the certificate files.**  Run A (`hA`, plain, `n ≤ 11 + 8e`), run B
(`hB`, no cores), `sameMeasure` (one measure), `crowdZones` (run B's NO-families avoid the
crowd family of box size `a_w` at every corner), and the rational side conditions: the pad
`a_w ≥ (s0/m_lo)(1 − δ) + (s0/m_lo − 1)·0.7072` and the corner separation
`(s0 − 2a_w)² > 2`.  Conclusion: `CrowdKill δ m_lo s0`. -/
theorem crowdKill_of_files {cA cB : CCertI} {eNum eDen : ℕ} (hd : 0 < eDen)
    (hA : checkCaseI cA = true) (hAc : cA.cores = []) (hAf : cA.nofams = [])
    (hAn : (cA.n : ℝ) ≤ 11 + 8 * ((eNum : ℝ) / eDen))
    (hB : checkCaseI cB = true) (hBc : cB.cores = []) (hBs : caseSide cB = caseSide cA)
    (hsm : sameMeasure cA cB eNum eDen = true)
    {aw : Rat} {fuel : ℕ} (hz : crowdZones cB.sNum cB.sDen aw fuel cB.nofams = true)
    {mlo δ : ℝ} (hmlo : 0 < mlo) (hδ : δ ≤ 1)
    (haw : caseSide cA / mlo * (1 - δ) + (caseSide cA / mlo - 1) * (7072 / 10000) ≤ (aw : ℝ))
    (hsep : 2 < (caseSide cA - 2 * (aw : ℝ)) ^ 2) (hsa : 2 * (aw : ℝ) ≤ caseSide cA) :
    CrowdKill δ mlo (caseSide cA) := by
  have hE := crowdZones_sound hz
  rw [hBs] at hE
  exact crowd_cert_kill (by positivity) hA hAc hAf hAn hB hBc hBs (sameMeasure_sound hd hsm)
    hmlo (by norm_num) (fun t ht => wT_le_bound ht.1 ht.2) (by linarith) haw hE hsep hsa

end S11
end PackingCert
