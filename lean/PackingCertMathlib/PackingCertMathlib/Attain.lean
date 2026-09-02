import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Prod
import Mathlib.Order.Interval.Set.Basic
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Tactic
import PackingCertMathlib.Parametrize
import PackingCertMathlib.MeasureBridge

/-!
# Attainment: `s(11)` is a minimum (A68, depgraph node A.D1)

The drain lemma D1 (`docs/proofs/drain_lemma.md`): if any 11-packing exists then
`{s | Fits 11 s}` has a least element.  This discharges the `attained` axiom of
`TopLevel.lean`.

Proof shape (compactness in COORDINATES, no Hausdorff limits): the feasible region

  `Dom ⊆ ((Fin 11 → (ℝ × ℝ) × ℝ) × ℝ)`   (33 square coordinates + the side `s ∈ [0, 11]`)

cut out by the tilt bounds `t ∈ [0,1]`, the containment inequalities
`wT t / 2 ≤ c ≤ s − wT t / 2` (Parametrize's `set_subset_container_iff`), and pairwise
non-overlap, is CLOSED and BOUNDED, hence compact; the side projection is continuous, so its
minimum over `Dom` is attained; `parametrize` (A64) sends every set-level packing into `Dom`.

The one genuinely topological ingredient is that non-overlap is a closed condition on the
coordinates.  That follows from the exact interior formula `mem_interior_iff_uv`
(the interior of a parametrised square is the OPEN `u/v` box — the `⊇` half is A64's
`strict_uv_mem_interior`, the `⊆` half is proved here by a pushout along the edge direction):
overlap of open boxes is witnessed by a point at which four STRICT inequalities hold, each
open in the configuration, so overlap is open and non-overlap closed.

Boundedness of `Dom` needs no extra hypothesis: the containment inequalities themselves pin
the centres into `[0, 11]²` (via `wT ≥ 1`), and the explicit 11-in-a-row packing `rowCfg`
supplies nonemptiness at side 11.
-/

namespace PackingCert
namespace S11

noncomputable section

open Set

/-! ## The interior of a parametrised square, exactly -/

/-- Interior membership forces a STRICT coordinate bound along any unit direction whose
coordinate is `≤ 1/2` everywhere on the square: push `p` by `ε/2` along `±w`; the pushed
point stays in the square, so the coordinate of `p` sits at distance `≥ ε/2` from the
extreme.  Converse companion of `strict_uv_mem_interior` (`MeasureBridge.lean`). -/
theorem interior_coord_lt {q : PSq} {p : RP} {w : RP} (hw : rdot w w = 1)
    (hbound : ∀ x ∈ q.set, |rdot (x.1 - q.cx, x.2 - q.cy) w| ≤ 1 / 2)
    (hp : p ∈ interior q.set) : |rdot (p.1 - q.cx, p.2 - q.cy) w| < 1 / 2 := by
  obtain ⟨eps, heps, hball⟩ := Metric.isOpen_iff.mp isOpen_interior p hp
  have hw' : w.1 * w.1 + w.2 * w.2 = 1 := hw
  have hw1 : |w.1| ≤ 1 := abs_le_one_iff_mul_self_le_one.mpr (by nlinarith [mul_self_nonneg w.2])
  have hw2 : |w.2| ≤ 1 := abs_le_one_iff_mul_self_le_one.mpr (by nlinarith [mul_self_nonneg w.1])
  set u := rdot (p.1 - q.cx, p.2 - q.cy) w with hu
  have key : ∀ d : ℝ, |d| = 1 → |u + eps / 2 * d| ≤ 1 / 2 := by
    intro d hd
    set p' : RP := (p.1 + eps / 2 * d * w.1, p.2 + eps / 2 * d * w.2) with hp'
    have habs : ∀ a : ℝ, |a| ≤ 1 → |eps / 2 * d * a| < eps := by
      intro a ha
      rw [abs_mul, abs_mul, abs_of_pos (by positivity : (0:ℝ) < eps / 2), hd, mul_one]
      nlinarith [abs_nonneg a]
    have hdist : dist p' p < eps := by
      rw [Prod.dist_eq, hp']
      simp only [Real.dist_eq, add_sub_cancel_left]
      exact max_lt (habs _ hw1) (habs _ hw2)
    have hp'mem : p' ∈ q.set := interior_subset (hball (Metric.mem_ball.mpr hdist))
    have hval : rdot (p'.1 - q.cx, p'.2 - q.cy) w = u + eps / 2 * d := by
      simp only [hp', hu, rdot]
      linear_combination (eps / 2 * d) * hw'
    have := hbound p' hp'mem
    rwa [hval] at this
  rcases le_or_gt 0 u with h | h
  · have h1 := key 1 (by norm_num)
    rw [abs_le] at h1
    rw [abs_lt]
    constructor <;> nlinarith
  · have h1 := key (-1) (by norm_num)
    rw [abs_le] at h1
    rw [abs_lt]
    constructor <;> nlinarith

/-- **The interior of a parametrised square is exactly the open `u/v` box.**  The `←`
direction is A64's `strict_uv_mem_interior`; the `→` direction is `interior_coord_lt`
applied along `edir` and its perp. -/
theorem mem_interior_iff_uv (q : PSq) (p : RP) :
    p ∈ interior q.set ↔
      |rdot (p.1 - q.cx, p.2 - q.cy) (edir q)| < 1 / 2 ∧
      |rdot (p.1 - q.cx, p.2 - q.cy) (perpV (edir q))| < 1 / 2 := by
  constructor
  · intro hp
    refine ⟨interior_coord_lt (rdot_edir q)
      (fun x hx => ((mem_set_iff_uv q x).mp hx).1) hp,
      interior_coord_lt ?_ (fun x hx => ((mem_set_iff_uv q x).mp hx).2) hp⟩
    rw [rdot_perpV]
    exact rdot_edir q
  · exact fun ⟨hu, hv⟩ => strict_uv_mem_interior q p hu hv

/-! ## The coordinate feasible region -/

/-- Raw coordinates of one square: `((cx, cy), t)`. -/
abbrev RawSq : Type := (ℝ × ℝ) × ℝ

/-- Raw coordinates of a configuration together with a side. -/
abbrev RawCfg : Type := (Fin 11 → RawSq) × ℝ

/-- The parametrised square denoted by a raw coordinate triple. -/
def toPSq (w : RawSq) : PSq := ⟨w.1.1, w.1.2, w.2⟩

/-- Strict (interior) membership of the plane point `p` in the square of `w`, as a
coordinate predicate (the open `u/v` box of `mem_interior_iff_uv`). -/
def StrictIn (w : RawSq) (p : RP) : Prop :=
  |rdot (p.1 - w.1.1, p.2 - w.1.2) (edir (toPSq w))| < 1 / 2 ∧
  |rdot (p.1 - w.1.1, p.2 - w.1.2) (perpV (edir (toPSq w)))| < 1 / 2

theorem strictIn_iff_interior (w : RawSq) (p : RP) :
    StrictIn w p ↔ p ∈ interior (toPSq w).set :=
  (mem_interior_iff_uv (toPSq w) p).symm

/-- The feasible region: side in `[0, 11]`, tilts in `[0, 1]`, containment inequalities,
pairwise non-overlap — all as coordinate conditions.  `mem_Dom_iff` identifies membership
with `IsPacking`. -/
def Dom : Set RawCfg :=
  {x | x.2 ∈ Icc (0 : ℝ) 11} ∩
  (⋂ i : Fin 11, {x | (x.1 i).2 ∈ Icc (0 : ℝ) 1}) ∩
  (⋂ i : Fin 11,
    ({x | wT ((x.1 i).2) / 2 ≤ (x.1 i).1.1} ∩
     {x | (x.1 i).1.1 ≤ x.2 - wT ((x.1 i).2) / 2} ∩
     ({x | wT ((x.1 i).2) / 2 ≤ (x.1 i).1.2} ∩
      {x | (x.1 i).1.2 ≤ x.2 - wT ((x.1 i).2) / 2}))) ∩
  (⋂ i : Fin 11, ⋂ j : Fin 11, ⋂ _h : i ≠ j,
    {x | ∀ p : RP, ¬(StrictIn (x.1 i) p ∧ StrictIn (x.1 j) p)})

/-- Membership in `Dom` is exactly "a packing at the recorded side, with side in the
compact window `[0, 11]` and tilts in `[0, 1]`". -/
theorem mem_Dom_iff {x : RawCfg} :
    x ∈ Dom ↔ x.2 ∈ Icc (0 : ℝ) 11 ∧ (∀ i, (x.1 i).2 ∈ Icc (0 : ℝ) 1) ∧
      IsPacking 11 x.2 fun i => (toPSq (x.1 i)).set := by
  simp only [Dom, mem_inter_iff, mem_iInter, mem_ofPred_eq]
  constructor
  · rintro ⟨⟨⟨hs, ht⟩, hbox⟩, hno⟩
    refine ⟨hs, ht, ?_, ?_, ?_⟩
    · exact fun i => ⟨_, _, rdot_edir _, rfl⟩
    · intro i
      exact (set_subset_container_iff (ht i).1 (ht i).2 x.2).mpr
        ⟨(hbox i).1.1, (hbox i).1.2, (hbox i).2.1, (hbox i).2.2⟩
    · intro i j hij
      rw [Set.disjoint_left]
      intro p hpi hpj
      exact hno i j hij p
        ⟨(strictIn_iff_interior _ _).mpr hpi, (strictIn_iff_interior _ _).mpr hpj⟩
  · rintro ⟨hs, ht, hP⟩
    refine ⟨⟨⟨hs, ht⟩, fun i => ?_⟩, fun i j hij p hcon => ?_⟩
    · obtain ⟨b1, b2, b3, b4⟩ :=
        (set_subset_container_iff (ht i).1 (ht i).2 x.2).mp (hP.contained i)
      exact ⟨⟨b1, b2⟩, b3, b4⟩
    · exact Set.disjoint_left.mp (hP.interiorDisjoint i j hij)
        ((strictIn_iff_interior _ _).mp hcon.1) ((strictIn_iff_interior _ _).mp hcon.2)

/-! ## Topology: `Dom` is compact -/

@[fun_prop]
theorem continuous_cosT : Continuous cosT := by
  unfold cosT
  exact (continuous_const.sub (continuous_pow 2)).div
    (continuous_const.add (continuous_pow 2)) fun t => (one_add_sq_pos t).ne'

@[fun_prop]
theorem continuous_sinT : Continuous sinT := by
  unfold sinT
  exact (continuous_const.mul continuous_id).div
    (continuous_const.add (continuous_pow 2)) fun t => (one_add_sq_pos t).ne'

@[fun_prop]
theorem continuous_wT : Continuous wT := by
  unfold wT
  exact continuous_cosT.add continuous_sinT

private theorem continuous_uC (i : Fin 11) (p : RP) :
    Continuous fun x : RawCfg =>
      rdot (p.1 - (x.1 i).1.1, p.2 - (x.1 i).1.2) (edir (toPSq (x.1 i))) := by
  simp only [rdot, edir, toPSq]
  fun_prop

private theorem continuous_vC (i : Fin 11) (p : RP) :
    Continuous fun x : RawCfg =>
      rdot (p.1 - (x.1 i).1.1, p.2 - (x.1 i).1.2) (perpV (edir (toPSq (x.1 i)))) := by
  simp only [rdot, edir, perpV, toPSq]
  fun_prop

theorem isClosed_Dom : IsClosed Dom := by
  have hti : ∀ i : Fin 11, Continuous fun x : RawCfg => (x.1 i).2 := by fun_prop
  have hcx : ∀ i : Fin 11, Continuous fun x : RawCfg => (x.1 i).1.1 := by fun_prop
  have hcy : ∀ i : Fin 11, Continuous fun x : RawCfg => (x.1 i).1.2 := by fun_prop
  have hwt : ∀ i : Fin 11, Continuous fun x : RawCfg => wT ((x.1 i).2) :=
    fun i => continuous_wT.comp (hti i)
  refine IsClosed.inter (IsClosed.inter (IsClosed.inter ?_ ?_) ?_) ?_
  · exact isClosed_Icc.preimage continuous_snd
  · exact isClosed_iInter fun i => isClosed_Icc.preimage (hti i)
  · refine isClosed_iInter fun i => ?_
    refine IsClosed.inter (IsClosed.inter ?_ ?_) (IsClosed.inter ?_ ?_)
    · exact isClosed_le ((hwt i).div_const 2) (hcx i)
    · exact isClosed_le (hcx i) (continuous_snd.sub ((hwt i).div_const 2))
    · exact isClosed_le ((hwt i).div_const 2) (hcy i)
    · exact isClosed_le (hcy i) (continuous_snd.sub ((hwt i).div_const 2))
  · refine isClosed_iInter fun i => isClosed_iInter fun j => isClosed_iInter fun _hij => ?_
    have hrw : {x : RawCfg | ∀ p : RP, ¬(StrictIn (x.1 i) p ∧ StrictIn (x.1 j) p)}
        = (⋃ p : RP, {x | StrictIn (x.1 i) p ∧ StrictIn (x.1 j) p})ᶜ := by
      ext x
      simp only [mem_compl_iff, mem_iUnion, mem_ofPred_eq, not_exists]
    rw [hrw]
    refine IsOpen.isClosed_compl (isOpen_iUnion fun p => ?_)
    have hrw2 : {x : RawCfg | StrictIn (x.1 i) p ∧ StrictIn (x.1 j) p}
        = ({x : RawCfg |
              |rdot (p.1 - (x.1 i).1.1, p.2 - (x.1 i).1.2) (edir (toPSq (x.1 i)))| < 1 / 2} ∩
           {x : RawCfg |
              |rdot (p.1 - (x.1 i).1.1, p.2 - (x.1 i).1.2)
                (perpV (edir (toPSq (x.1 i))))| < 1 / 2}) ∩
          ({x : RawCfg |
              |rdot (p.1 - (x.1 j).1.1, p.2 - (x.1 j).1.2) (edir (toPSq (x.1 j)))| < 1 / 2} ∩
           {x : RawCfg |
              |rdot (p.1 - (x.1 j).1.1, p.2 - (x.1 j).1.2)
                (perpV (edir (toPSq (x.1 j))))| < 1 / 2}) := by
      ext x
      simp only [StrictIn, mem_inter_iff, mem_ofPred_eq]
    rw [hrw2]
    exact IsOpen.inter
      ((isOpen_lt (continuous_uC i p).abs continuous_const).inter
        (isOpen_lt (continuous_vC i p).abs continuous_const))
      ((isOpen_lt (continuous_uC j p).abs continuous_const).inter
        (isOpen_lt (continuous_vC j p).abs continuous_const))

theorem isCompact_Dom : IsCompact Dom := by
  have hK : IsCompact ((univ.pi fun _ : Fin 11 =>
      (Icc (0 : ℝ) 11 ×ˢ Icc (0 : ℝ) 11) ×ˢ Icc (0 : ℝ) 1) ×ˢ Icc (0 : ℝ) 11 : Set RawCfg) :=
    (isCompact_univ_pi fun _ =>
      (isCompact_Icc.prod isCompact_Icc).prod isCompact_Icc).prod isCompact_Icc
  refine hK.of_isClosed_subset isClosed_Dom ?_
  intro x hx
  have hx' := hx
  simp only [Dom, mem_inter_iff, mem_iInter, mem_ofPred_eq] at hx'
  obtain ⟨⟨⟨hs, ht⟩, hbox⟩, -⟩ := hx'
  refine Set.mem_prod.mpr ⟨Set.mem_univ_pi.mpr fun i => ?_, hs⟩
  have hw1 := wT_ge_one (ht i).1 (ht i).2
  obtain ⟨⟨b1, b2⟩, b3, b4⟩ := hbox i
  have hcx : (x.1 i).1.1 ∈ Icc (0 : ℝ) 11 :=
    mem_Icc.mpr ⟨by nlinarith [hs.1, hs.2], by nlinarith [hs.1, hs.2]⟩
  have hcy : (x.1 i).1.2 ∈ Icc (0 : ℝ) 11 :=
    mem_Icc.mpr ⟨by nlinarith [hs.1, hs.2], by nlinarith [hs.1, hs.2]⟩
  exact ⟨⟨hcx, hcy⟩, ht i⟩

/-! ## Nonemptiness: eleven squares in a row at side 11 -/

private theorem cosT_zero : cosT 0 = 1 := by norm_num [cosT]

private theorem sinT_zero : sinT 0 = 0 := by norm_num [sinT]

private theorem wT_zero : wT 0 = 1 := by norm_num [wT, cosT, sinT]

/-- The explicit 11-in-a-row packing at side 11, in raw coordinates. -/
def rowCfg : RawCfg := (fun i => (((i : ℕ) + 1 / 2, 1 / 2), 0), 11)

theorem rowCfg_mem : rowCfg ∈ Dom := by
  simp only [Dom, mem_inter_iff, mem_iInter, mem_ofPred_eq, mem_Icc, rowCfg]
  have hival : ∀ i : Fin 11, (0 : ℝ) ≤ (i : ℕ) ∧ ((i : ℕ) : ℝ) ≤ 10 := by
    intro i
    have h10 : (i : ℕ) ≤ 10 := Nat.lt_succ_iff.mp i.isLt
    exact ⟨Nat.cast_nonneg _, by exact_mod_cast h10⟩
  refine ⟨⟨⟨⟨by norm_num, by norm_num⟩, fun i => ⟨le_refl 0, zero_le_one⟩⟩, fun i => ?_⟩,
    fun i j hij p hcon => ?_⟩
  · obtain ⟨h0, h10⟩ := hival i
    refine ⟨⟨?_, ?_⟩, ?_, ?_⟩ <;> rw [wT_zero] <;> linarith
  · -- the two open slabs `((i:ℝ), i+1)` and `((j:ℝ), j+1)` are disjoint
    have hu_i := hcon.1.1
    have hu_j := hcon.2.1
    simp only [toPSq, edir, rdot, cosT_zero, sinT_zero, mul_one, mul_zero,
      add_zero] at hu_i hu_j
    rw [abs_lt] at hu_i hu_j
    have hne : (i : ℕ) ≠ (j : ℕ) := fun h => hij (Fin.ext h)
    rcases Nat.lt_or_ge (i : ℕ) (j : ℕ) with h | h
    · have : ((i : ℕ) : ℝ) + 1 ≤ ((j : ℕ) : ℝ) := by exact_mod_cast Nat.succ_le_of_lt h
      linarith [hu_i.1, hu_i.2, hu_j.1, hu_j.2]
    · have hlt : (j : ℕ) < (i : ℕ) := lt_of_le_of_ne h (Ne.symm hne)
      have : ((j : ℕ) : ℝ) + 1 ≤ ((i : ℕ) : ℝ) := by exact_mod_cast Nat.succ_le_of_lt hlt
      linarith [hu_i.1, hu_i.2, hu_j.1, hu_j.2]

/-! ## Side lower bound and the attainment theorem -/

/-- An 11-packing forces a nonnegative side (the container must contain a point). -/
theorem fits_nonneg {s : ℝ} (h : Fits 11 s) : 0 ≤ s := by
  obtain ⟨Q, hQ⟩ := h
  obtain ⟨p0, e, -, hset⟩ := hQ.unit 0
  have hp0 : p0 ∈ Q 0 := by
    rw [hset]
    exact ⟨0, 0, le_rfl, zero_le_one, le_rfl, zero_le_one, by simp [aff]⟩
  have := hQ.contained 0 hp0
  rw [container, Set.mem_prod] at this
  exact le_trans this.1.1 this.1.2

/-- **[D1 — attainment]** `{s | Fits 11 s}` has a least element (`docs/proofs/drain_lemma.md`
D1, formalised; A68).  Discharges the `attained` axiom of `TopLevel.lean`. -/
theorem attained_thm : ∃ m, IsLeast {s : ℝ | Fits 11 s} m := by
  obtain ⟨x0, hx0, hmin'⟩ := isCompact_Dom.exists_isMinOn ⟨rowCfg, rowCfg_mem⟩
    continuous_snd.continuousOn
  have hmin : ∀ y ∈ Dom, x0.2 ≤ y.2 := isMinOn_iff.mp hmin'
  refine ⟨x0.2, ?_, ?_⟩
  · obtain ⟨-, -, hP⟩ := mem_Dom_iff.mp hx0
    exact ⟨_, hP⟩
  · intro s hs
    rcases le_or_gt 11 s with h11 | h11
    · have h0 : x0.2 ≤ rowCfg.2 := hmin rowCfg rowCfg_mem
      have h1 : rowCfg.2 = 11 := rfl
      linarith
    · have h0 : (0 : ℝ) ≤ s := fits_nonneg hs
      obtain ⟨Q, hQ⟩ := hs
      obtain ⟨z, hzt, hzQ⟩ := parametrize Q hQ
      have hx : ((fun i => (((z i).cx, (z i).cy), (z i).t), s) : RawCfg) ∈ Dom := by
        rw [mem_Dom_iff]
        refine ⟨⟨h0, h11.le⟩, fun i => hzt i, ?_⟩
        have hQeq : (fun i => (toPSq ((((z i).cx, (z i).cy), (z i).t) : RawSq)).set) = Q :=
          funext fun i => (hzQ i).symm
        rw [hQeq]
        exact hQ
      exact hmin _ hx

end

end S11
end PackingCert
