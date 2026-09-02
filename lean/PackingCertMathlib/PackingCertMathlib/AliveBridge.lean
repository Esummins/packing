import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Tactic
import PackingCertMathlib.CaseBridge
import PackingCertMathlib.AliveChecker

/-!
# The ALIVE bridge (A78, depgraph node D.ALIVE) — the completeness-side arbiter

Soundness of `checkAlive` (`AliveChecker.lean`, the Lean port of the exact core of
`attempts/A57-shadow-trees/code/alivewitness.py`):

    `checkAlive w = true`  ⟹  for EVERY case-LP certificate `c` with the same cores,
                              the same side, budget `c.n − #cores = w.budget` and no
                              NO-families,  `checkCaseI c = false`.

i.e. the node is **LP-unkillable in the verifier's own sense**: no certificate of that
budget for those cores at that side can pass the (Lean-sound) case checker, so no amount
of compute spent on the node can produce one.

**Where this sits.**  This is a COMPLETENESS-side arbiter, not a soundness component.
It never enters the trusted composition of the s(11) proof: the soundness of a kill is
`V.CASE` (`CaseBridge.checkCaseI_kill`), and nothing in the upper/lower-bound chain
consumes `alive_sound`.  What it certifies is a *search decision*: a node with an ALIVE
witness must be BRANCHED (or the enclosing strategy changed), because no certificate of
budget `b` exists for it.  Wasted compute, not unsoundness, is what it prevents.

**The argument** (the Python header lemma, verbatim).  A PASS gives `budget` closed unit
squares that are admissible, pairwise disjoint and disjoint from every core.  If some
certificate `c` passed, `checkCaseI_price` (claim (P2)) would price each of them at
`≥ wd`; being pairwise disjoint, each atom of `c` is counted at most once, so the total
weight is `≥ budget · wd`; but the checker's own budget gate is
`Σ w < (n − r)·wd = budget · wd`.  Contradiction.

Geometry: `gsqSet` is the common closed-square set form (centre, tilt `t`, half-side `h`)
that both `PSq.set` (at `h = 1/2`) and `coreSet` (at `h = a`) are instances of;
`gsq_proj` is the support bound `|n·(p − c)| ≤ h(|n·e| + |n·e⊥|)`, and
`gsq_disjoint_sep` the separating-axis step.  `gap_disjoint` is the four-axis form the
checker decides.
-/

namespace PackingCert
namespace S11

open Set MeasureI CaseI AliveI

noncomputable section

/-! ## A common set form: closed square by centre, tilt and half-side -/

/-- The closed square with centre `(cx, cy)`, edge frame `(cos θ, sin θ)` at
`t = tan(θ/2)` and half-side `h`, in the `u/v` (edge-coordinate) form. -/
def gsqSet (cx cy t h : ℝ) : Set RP :=
  {p : RP | |(p.1 - cx) * cosT t + (p.2 - cy) * sinT t| ≤ h ∧
            |(-(p.1 - cx)) * sinT t + (p.2 - cy) * cosT t| ≤ h}

theorem coreSet_eq_gsqSet (K : CCore) :
    coreSet K = gsqSet (K.kx : ℝ) (K.ky : ℝ) (K.tm : ℝ) (K.a : ℝ) := rfl

theorem psq_set_eq_gsqSet (q : PSq) : q.set = gsqSet q.cx q.cy q.t (1 / 2) := by
  ext p
  rw [mem_set_iff_uv]
  have e1 : rdot (p.1 - q.cx, p.2 - q.cy) (edir q)
      = (p.1 - q.cx) * cosT q.t + (p.2 - q.cy) * sinT q.t := by
    simp only [rdot, edir]
  have e2 : rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q))
      = (-(p.1 - q.cx)) * sinT q.t + (p.2 - q.cy) * cosT q.t := by
    simp only [rdot, edir, perpV]
    ring
  rw [e1, e2]
  exact Iff.rfl

theorem cast_half : (((1 : ℚ) / 2 : ℚ) : ℝ) = 1 / 2 := by norm_num

/-! ## The support bound and the separating axis -/

/-- **Support bound.**  For a point of the square, the projection on ANY vector `n` is
bounded by `h·(|n·e| + |n·e⊥|)`: decompose `p − c = u e + v e⊥` with `|u|, |v| ≤ h`. -/
theorem gsq_proj {cx cy t h nx ny : ℝ} {p : RP} (hp : p ∈ gsqSet cx cy t h) :
    |(p.1 - cx) * nx + (p.2 - cy) * ny|
      ≤ h * (|nx * cosT t + ny * sinT t| + |-nx * sinT t + ny * cosT t|) := by
  obtain ⟨hu, hv⟩ := hp
  have hcs := cosT_sq_add_sinT_sq t
  have key : (p.1 - cx) * nx + (p.2 - cy) * ny
      = ((p.1 - cx) * cosT t + (p.2 - cy) * sinT t) * (nx * cosT t + ny * sinT t)
        + ((-(p.1 - cx)) * sinT t + (p.2 - cy) * cosT t) * (-nx * sinT t + ny * cosT t) := by
    linear_combination (-((p.1 - cx) * nx + (p.2 - cy) * ny)) * hcs
  rw [key, mul_add h (|nx * cosT t + ny * sinT t|) (|-nx * sinT t + ny * cosT t|)]
  have b1 : |((p.1 - cx) * cosT t + (p.2 - cy) * sinT t) * (nx * cosT t + ny * sinT t)|
      ≤ h * |nx * cosT t + ny * sinT t| := by
    rw [abs_mul]
    exact mul_le_mul_of_nonneg_right hu (abs_nonneg _)
  have b2 : |((-(p.1 - cx)) * sinT t + (p.2 - cy) * cosT t) * (-nx * sinT t + ny * cosT t)|
      ≤ h * |-nx * sinT t + ny * cosT t| := by
    rw [abs_mul]
    exact mul_le_mul_of_nonneg_right hv (abs_nonneg _)
  have b3 := abs_add_le
      (((p.1 - cx) * cosT t + (p.2 - cy) * sinT t) * (nx * cosT t + ny * sinT t))
      (((-(p.1 - cx)) * sinT t + (p.2 - cy) * cosT t) * (-nx * sinT t + ny * cosT t))
  linarith

/-- **Separating axis with positive margin.**  If the two support half-widths along `n`
sum to strictly less than the centre separation along `n`, the closed squares are
disjoint. -/
theorem gsq_disjoint_sep {cx1 cy1 t1 h1 cx2 cy2 t2 h2 nx ny : ℝ}
    (hsep : h1 * (|nx * cosT t1 + ny * sinT t1| + |-nx * sinT t1 + ny * cosT t1|)
          + h2 * (|nx * cosT t2 + ny * sinT t2| + |-nx * sinT t2 + ny * cosT t2|)
        < |(cx2 - cx1) * nx + (cy2 - cy1) * ny|) :
    Disjoint (gsqSet cx1 cy1 t1 h1) (gsqSet cx2 cy2 t2 h2) := by
  rw [Set.disjoint_left]
  intro p hp1 hp2
  have b1 := gsq_proj (nx := nx) (ny := ny) hp1
  have b2 := gsq_proj (nx := nx) (ny := ny) hp2
  have e : (cx2 - cx1) * nx + (cy2 - cy1) * ny
      = ((p.1 - cx1) * nx + (p.2 - cy1) * ny)
        + (-((p.1 - cx2) * nx + (p.2 - cy2) * ny)) := by ring
  have b3 := abs_add_le ((p.1 - cx1) * nx + (p.2 - cy1) * ny)
      (-((p.1 - cx2) * nx + (p.2 - cy2) * ny))
  rw [abs_neg] at b3
  rw [e] at hsep
  linarith

/-- Along its OWN edge normal `e`, a square's support multiplier is exactly `1`. -/
theorem own_axis_e (t : ℝ) :
    |cosT t * cosT t + sinT t * sinT t| + |-cosT t * sinT t + sinT t * cosT t| = 1 := by
  have h := cosT_sq_add_sinT_sq t
  have e1 : cosT t * cosT t + sinT t * sinT t = 1 := by linear_combination h
  have e2 : -cosT t * sinT t + sinT t * cosT t = (0 : ℝ) := by ring
  rw [e1, e2, abs_one, abs_zero, add_zero]

/-- Along its own second edge normal `e⊥`, likewise. -/
theorem own_axis_perp (t : ℝ) :
    |-sinT t * cosT t + cosT t * sinT t| + |-(-sinT t) * sinT t + cosT t * cosT t| = 1 := by
  have h := cosT_sq_add_sinT_sq t
  have e1 : -sinT t * cosT t + cosT t * sinT t = (0 : ℝ) := by ring
  have e2 : -(-sinT t) * sinT t + cosT t * cosT t = 1 := by linear_combination h
  rw [e1, e2, abs_one, abs_zero, zero_add]

/-! ## The checker's `gap_exact` over the reals -/

/-- The real meaning of one `gapOne` term. -/
def gapOneR (cx cy hh axx axy ocx ocy oh oco osi : ℝ) : ℝ :=
  |(ocx - cx) * axx + (ocy - cy) * axy| - hh
    - oh * (|axx * oco + axy * osi| + |-axx * osi + axy * oco|)

theorem gapOne_cast (cx cy hh axx axy ocx ocy oh oco osi : ℚ) :
    ((gapOne cx cy hh axx axy ocx ocy oh oco osi : ℚ) : ℝ)
      = gapOneR (cx : ℝ) (cy : ℝ) (hh : ℝ) (axx : ℝ) (axy : ℝ)
          (ocx : ℝ) (ocy : ℝ) (oh : ℝ) (oco : ℝ) (osi : ℝ) := by
  simp only [gapOne, gapOneR]
  push_cast [rabs_cast]
  ring

/-- A positive `gapOne` on an own-frame axis separates the two squares. -/
theorem gapOneR_disjoint {cx1 cy1 t1 h1 cx2 cy2 t2 h2 nx ny : ℝ}
    (hn : |nx * cosT t1 + ny * sinT t1| + |-nx * sinT t1 + ny * cosT t1| = 1)
    (hgap : 0 < gapOneR cx1 cy1 h1 nx ny cx2 cy2 h2 (cosT t2) (sinT t2)) :
    Disjoint (gsqSet cx1 cy1 t1 h1) (gsqSet cx2 cy2 t2 h2) := by
  simp only [gapOneR] at hgap
  refine gsq_disjoint_sep (nx := nx) (ny := ny) ?_
  rw [hn]
  linarith

theorem rmax_pos {a b : ℚ} (h : 0 < rmax a b) : 0 < a ∨ 0 < b := by
  simp only [rmax] at h
  split at h
  · exact Or.inr h
  · exact Or.inl h

/-- **`gap_exact > 0` ⟹ the two CLOSED squares are disjoint** (the strict-gap clause of
the Python header lemma; strictness matters because the LP measure is atomic). -/
theorem gap_disjoint {cx1 cy1 t1 h1 cx2 cy2 t2 h2 : ℚ}
    (h : 0 < gapExact cx1 cy1 t1 h1 cx2 cy2 t2 h2) :
    Disjoint (gsqSet (cx1 : ℝ) (cy1 : ℝ) (t1 : ℝ) (h1 : ℝ))
             (gsqSet (cx2 : ℝ) (cy2 : ℝ) (t2 : ℝ) (h2 : ℝ)) := by
  simp only [gapExact] at h
  rcases rmax_pos h with h' | h'
  · rcases rmax_pos h' with h'' | h''
    · have hR : (0 : ℝ) < gapOneR (cx1 : ℝ) (cy1 : ℝ) (h1 : ℝ)
          (((ratCosSin t1).1 : ℚ) : ℝ) (((ratCosSin t1).2 : ℚ) : ℝ)
          (cx2 : ℝ) (cy2 : ℝ) (h2 : ℝ)
          (((ratCosSin t2).1 : ℚ) : ℝ) (((ratCosSin t2).2 : ℚ) : ℝ) := by
        rw [← gapOne_cast]; exact_mod_cast h''
      push_cast [ratCosSin_fst, ratCosSin_snd] at hR
      exact gapOneR_disjoint (own_axis_e _) hR
    · have hR : (0 : ℝ) < gapOneR (cx1 : ℝ) (cy1 : ℝ) (h1 : ℝ)
          ((-(ratCosSin t1).2 : ℚ) : ℝ) (((ratCosSin t1).1 : ℚ) : ℝ)
          (cx2 : ℝ) (cy2 : ℝ) (h2 : ℝ)
          (((ratCosSin t2).1 : ℚ) : ℝ) (((ratCosSin t2).2 : ℚ) : ℝ) := by
        rw [← gapOne_cast]; exact_mod_cast h''
      push_cast [ratCosSin_fst, ratCosSin_snd] at hR
      exact gapOneR_disjoint (own_axis_perp _) hR
  · rcases rmax_pos h' with h'' | h''
    · have hR : (0 : ℝ) < gapOneR (cx2 : ℝ) (cy2 : ℝ) (h2 : ℝ)
          (((ratCosSin t2).1 : ℚ) : ℝ) (((ratCosSin t2).2 : ℚ) : ℝ)
          (cx1 : ℝ) (cy1 : ℝ) (h1 : ℝ)
          (((ratCosSin t1).1 : ℚ) : ℝ) (((ratCosSin t1).2 : ℚ) : ℝ) := by
        rw [← gapOne_cast]; exact_mod_cast h''
      push_cast [ratCosSin_fst, ratCosSin_snd] at hR
      exact (gapOneR_disjoint (own_axis_e _) hR).symm
    · have hR : (0 : ℝ) < gapOneR (cx2 : ℝ) (cy2 : ℝ) (h2 : ℝ)
          ((-(ratCosSin t2).2 : ℚ) : ℝ) (((ratCosSin t2).1 : ℚ) : ℝ)
          (cx1 : ℝ) (cy1 : ℝ) (h1 : ℝ)
          (((ratCosSin t1).1 : ℚ) : ℝ) (((ratCosSin t1).2 : ℚ) : ℝ) := by
        rw [← gapOne_cast]; exact_mod_cast h''
      push_cast [ratCosSin_fst, ratCosSin_snd] at hR
      exact (gapOneR_disjoint (own_axis_perp _) hR).symm

/-! ## `admissible_exact` is containment -/

theorem admissible_sound {s cx cy t : ℚ} (h0 : (0 : ℚ) ≤ t) (h1 : t ≤ 1)
    (h : admissible s cx cy t = true) :
    (⟨(cx : ℝ), (cy : ℝ), (t : ℝ)⟩ : PSq).set ⊆ container (s : ℝ) := by
  have ht0 : (0 : ℝ) ≤ (t : ℝ) := by exact_mod_cast h0
  have ht1 : (t : ℝ) ≤ 1 := by exact_mod_cast h1
  have hw : ((halfWidth t : ℚ) : ℝ) = wT (t : ℝ) / 2 := by
    simp only [halfWidth]
    push_cast [rabs_cast, ratCosSin_fst, ratCosSin_snd]
    rw [abs_of_nonneg (cosT_nonneg ht0 ht1), abs_of_nonneg (sinT_nonneg ht0), wT]
  simp only [admissible, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨ha, hb⟩, hc⟩, hd⟩ := h
  refine (set_subset_container_iff (q := (⟨(cx : ℝ), (cy : ℝ), (t : ℝ)⟩ : PSq))
    ht0 ht1 (s : ℝ)).mpr ⟨?_, ?_, ?_, ?_⟩
  · have hx : ((halfWidth t : ℚ) : ℝ) ≤ (cx : ℝ) := by exact_mod_cast ha
    rwa [hw] at hx
  · have hx : (cx : ℝ) ≤ ((s - halfWidth t : ℚ) : ℝ) := by exact_mod_cast hb
    push_cast at hx
    rwa [hw] at hx
  · have hx : ((halfWidth t : ℚ) : ℝ) ≤ (cy : ℝ) := by exact_mod_cast hc
    rwa [hw] at hx
  · have hx : (cy : ℝ) ≤ ((s - halfWidth t : ℚ) : ℝ) := by exact_mod_cast hd
    push_cast at hx
    rwa [hw] at hx

/-! ## The disjoint-family mass bound -/

/-- **Each atom is counted at most once by a pairwise-disjoint family**, so the summed
mass of the family is at most the total weight.  (The `hupper` step of
`priced_dichotomy_scaled`, isolated.) -/
theorem massIn_sum_disjoint_le {n : ℕ} {atoms : List IAtom} (hw : ∀ a ∈ atoms, 0 ≤ a.w)
    {Q : Fin n → Set RP} (hdis : ∀ i j, i ≠ j → Disjoint (Q i) (Q j)) :
    ∑ i, massIn atoms (Q i) ≤ (atoms.map fun a => (a.w : ℝ)).sum := by
  rw [massIn_sum_comm]
  refine List.sum_le_sum fun a ha => ?_
  exact indicator_sum_le hdis (by exact_mod_cast hw a ha) (atomPt a)

/-! ## Unpacking `checkAlive` -/

theorem pairsOK_pairwise : ∀ {l : List AWSq}, pairsOK l = true →
    l.Pairwise fun p q => 0 < gapExact (awx p) (awy p) (awt p) (1 / 2)
        (awx q) (awy q) (awt q) (1 / 2) := by
  intro l
  induction l with
  | nil => intro _; exact List.Pairwise.nil
  | cons q rest ih =>
    intro h
    rw [pairsOK, Bool.and_eq_true] at h
    refine List.Pairwise.cons ?_ (ih h.2)
    intro p hp
    have hpg := List.all_eq_true.mp h.1 p hp
    simp only [pairGapOK, decide_eq_true_eq] at hpg
    exact hpg

/-- The witness family as parametrised squares. -/
def aliveFam (w : AliveCert) (i : Fin w.sq.length) : PSq :=
  ⟨((awx (w.sq.get i) : ℚ) : ℝ), ((awy (w.sq.get i) : ℚ) : ℝ), ((awt (w.sq.get i) : ℚ) : ℝ)⟩

/-! ## The soundness theorem -/

/-- **The ALIVE arbiter is sound, core-monotone form.**  The witnesses need only avoid
obstacles that CONTAIN the certificate's cores — which is what `alivewitness.py` actually
produces: it uses the full pin unit square (`a = 1/2`, `tm = 0`) where an A53-lineage
case certificate carries a slightly shrunk, slightly tilted pin core.  Only the CARDINALITY
of `c.cores` matters for the budget. -/
theorem alive_sound_mono {w : AliveCert} (hw : checkAlive w = true) :
    ∀ c : CCertI, c.cores.length = w.cores.length →
      (∀ K ∈ c.cores, ∃ K' ∈ w.cores, coreSet K ⊆ coreSet K') →
      caseSide c = (w.s : ℝ) → c.n = w.cores.length + w.budget → c.nofams = [] →
      checkCaseI c = false := by
  intro c hr hcores hside hn hnf
  by_contra hcontra
  have hcc : checkCaseI c = true := by
    cases hb : checkCaseI c
    · exact absurd hb hcontra
    · rfl
  obtain ⟨hsd, hwd, hat, hcoresOK, hrn, htot, hgo⟩ := checkCaseI_facts hcc
  simp only [checkAlive, Bool.and_eq_true] at hw
  obtain ⟨⟨⟨⟨hwc, hwit⟩, hwcore⟩, hwpair⟩, hwlen⟩ := hw
  have hlen : w.sq.length = w.budget := of_decide_eq_true hwlen
  have hgetmem : ∀ i : Fin w.sq.length, w.sq.get i ∈ w.sq :=
    fun i => List.mem_iff_get.mpr ⟨i, rfl⟩
  -- per-witness gates
  have hwit' : ∀ i : Fin w.sq.length,
      (0 : ℚ) ≤ awt (w.sq.get i) ∧ awt (w.sq.get i) ≤ 1 ∧
      admissible w.s (awx (w.sq.get i)) (awy (w.sq.get i)) (awt (w.sq.get i)) = true := by
    intro i
    have hb := List.all_eq_true.mp hwit _ (hgetmem i)
    simp only [witOK, Bool.and_eq_true, decide_eq_true_eq] at hb
    exact ⟨hb.1.1, hb.1.2, hb.2⟩
  -- each witness is priced ≥ wd
  have hprice : ∀ i : Fin w.sq.length, (c.wd : ℝ) ≤ massIn c.atoms (aliveFam w i).set := by
    intro i
    obtain ⟨ht0, ht1, hadm⟩ := hwit' i
    have hA : (0 : ℝ) ≤ ((awt (w.sq.get i) : ℚ) : ℝ) := by exact_mod_cast ht0
    have hB : ((awt (w.sq.get i) : ℚ) : ℝ) ≤ 1 := by exact_mod_cast ht1
    refine checkCaseI_price hcc (aliveFam w i) hA hB ?_ ?_ ?_
    · rw [hside]
      exact admissible_sound ht0 ht1 hadm
    · intro K hK
      obtain ⟨K', hK', hsub⟩ := hcores K hK
      have hcg := List.all_eq_true.mp hwcore _ (hgetmem i)
      simp only [coreGapOK, List.all_eq_true, decide_eq_true_eq] at hcg
      have hd := gap_disjoint (hcg K' hK')
      rw [cast_half] at hd
      rw [show (aliveFam w i).set
          = gsqSet ((awx (w.sq.get i) : ℚ) : ℝ) ((awy (w.sq.get i) : ℚ) : ℝ)
              ((awt (w.sq.get i) : ℚ) : ℝ) (1 / 2) from psq_set_eq_gsqSet _]
      exact Disjoint.mono_right (hsub.trans_eq (coreSet_eq_gsqSet K')) hd
    · intro f hf
      rw [hnf] at hf
      exact absurd hf List.not_mem_nil
  -- the witnesses are pairwise disjoint
  have hpw := List.pairwise_iff_get.mp (pairsOK_pairwise hwpair)
  have hdisQ : ∀ i j : Fin w.sq.length, i ≠ j →
      Disjoint (aliveFam w i).set (aliveFam w j).set := by
    have hmain : ∀ i j : Fin w.sq.length, i < j →
        Disjoint (aliveFam w i).set (aliveFam w j).set := by
      intro i j hij
      have hd := gap_disjoint (hpw i j hij)
      rw [show (aliveFam w i).set
          = gsqSet ((awx (w.sq.get i) : ℚ) : ℝ) ((awy (w.sq.get i) : ℚ) : ℝ)
              ((awt (w.sq.get i) : ℚ) : ℝ) (1 / 2) from psq_set_eq_gsqSet _,
        show (aliveFam w j).set
          = gsqSet ((awx (w.sq.get j) : ℚ) : ℝ) ((awy (w.sq.get j) : ℚ) : ℝ)
              ((awt (w.sq.get j) : ℚ) : ℝ) (1 / 2) from psq_set_eq_gsqSet _]
      rwa [cast_half] at hd
    intro i j hij
    rcases lt_or_gt_of_ne hij with hlt | hgt
    · exact hmain i j hlt
    · exact (hmain j i hgt).symm
  -- counting
  have hlow : (w.sq.length : ℝ) * (c.wd : ℝ)
      ≤ ∑ i, massIn c.atoms (aliveFam w i).set := by
    have hconst : ∑ _i : Fin w.sq.length, (c.wd : ℝ) = (w.sq.length : ℝ) * (c.wd : ℝ) := by
      simp [Finset.sum_const, nsmul_eq_mul]
    calc (w.sq.length : ℝ) * (c.wd : ℝ) = ∑ _i : Fin w.sq.length, (c.wd : ℝ) := hconst.symm
      _ ≤ ∑ i, massIn c.atoms (aliveFam w i).set :=
          Finset.sum_le_sum fun i _ => hprice i
  have hupper := massIn_sum_disjoint_le (atoms := c.atoms) (fun a ha => (hat a ha).2) hdisQ
  -- the budget gate
  rw [foldl_add_eq c.atoms 0, zero_add] at htot
  have hbudget : ((c.n : ℤ) - (c.cores.length : ℤ)) = (w.budget : ℤ) := by
    rw [hn, hr]; push_cast; ring
  rw [hbudget] at htot
  have h2 : (((c.atoms.map fun a => a.w).sum : ℤ) : ℝ) < (w.budget : ℝ) * (c.wd : ℝ) := by
    exact_mod_cast htot
  have h3 : (((c.atoms.map fun a => a.w).sum : ℤ) : ℝ)
      = (c.atoms.map fun a => ((a.w : ℝ))).sum := by
    push_cast
    rw [List.map_map]
    rfl
  rw [h3] at h2
  have hlenR : (w.sq.length : ℝ) = (w.budget : ℝ) := by exact_mod_cast hlen
  rw [hlenR] at hlow
  linarith

/-- **The ALIVE arbiter is sound (node `D.ALIVE`).**

`checkAlive w = true` ⟹ NO case-LP certificate with these cores, this side, this budget
and no NO-families passes the Lean case checker: the node is **LP-unkillable in
`checkCaseI`'s own sense** — no certificate of budget `w.budget` for these cores at this
side exists, whatever compute is spent on the node.

Consumer reading (the depgraph corollary): *no certificate of budget `b` exists for this
node, so any case tree must BRANCH here.*  This is a completeness-side statement about the
SEARCH; it never enters the trusted composition of the s(11) proof (the soundness of a
kill is `V.CASE`, `checkCaseI_kill`).  It certifies the arbiter that DECIDES branching. -/
theorem alive_sound {w : AliveCert} (hw : checkAlive w = true) :
    ∀ c : CCertI, c.cores = w.cores → caseSide c = (w.s : ℝ) →
      c.n = w.cores.length + w.budget → c.nofams = [] → checkCaseI c = false := by
  intro c hcores hside hn hnf
  refine alive_sound_mono hw c (by rw [hcores]) ?_ hside hn hnf
  intro K hK
  exact ⟨K, hcores ▸ hK, subset_rfl⟩

end

end S11
end PackingCert
