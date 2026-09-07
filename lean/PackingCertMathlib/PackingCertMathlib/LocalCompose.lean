import PackingCertMathlib.LocalCert
import PackingCertMathlib.ParamNoFam

/-!
# The region-tree step: `LocalDead` composed with the YES / NO branches — A126 T3

A120's runner (`attempts/A120-no-side-runner/notes/runner.md` §1) covers a node hypothesis `H`
by its YES sub-hypothesis and its `|L|` NO children:

    H  =  YES  ∪  NO_1 ∪ … ∪ NO_{|L|}                       (a tautology, not a partition)
    YES  =  H ∧ (for every ℓ, SOME square of the packing has its pose in the box `B_ℓ`)
    NO_ℓ =  H ∧ (NO square of the packing has its pose in `B_ℓ`)

This file states and proves that split in Lean and composes it with `LocalDead`:

* `yes_or_no` — the tautologous cover (classical, one `by_cases`);
* `localHyp_of_yes` — the YES side supplies `LocalHyp`: A120's soundness clauses **A2** (the
  boxes are pairwise pose-disjoint) and **A3** (each box is pose-disjoint from every pin) are
  exactly what turns "each box is occupied" into "|L| DISTINCT squares, distinct from the pins",
  i.e. into the injectivity `LocalHyp` demands;
* `node_dead_of_yes_no` — `LocalDead N` kills YES, so a node whose `|L|` NO children are all
  dead is dead;
* `classKilledAt_of_yes_no` — the same in the `ClassKilledAt` shape `Composition.lean` consumes;
* `centre_in_slab` — a packed square's centre is at least `1/2` from every wall.  This is the
  fact behind A120's clamp of a NO zone to `[1/2, s − 1/2]`: `noneIn_of_clamped` turns
  "no square in the CLAMPED zone" into `NoneIn` for the unclamped box, so the CLAMP costs
  nothing.  What is NOT free is the ROUNDING with which the zone reaches the certificate file:
  measured on all four of A120's closed nodes it goes OUTWARD by up to `1.1·10⁻⁷` in tilt,
  which is the direction that breaks the tautology — finding F-COVER,
  `attempts/A126-localdead-lean/notes/obligations.md` §4.

The A120 instantiation (`k5_11_interior_Y0230`, its four NO children) is `y0230_dead`, whose
hypotheses are exactly the obligations that remain — see
`attempts/A126-localdead-lean/notes/obligations.md` §3.
-/

namespace PackingCert
namespace S11
namespace LocalCert

open Set

noncomputable section

/-! ## 1. The two branches -/

/-- SOME square of `z` has its pose in the box `B` (A120's `A_ℓ`). -/
def SomeIn (B : Box) (z : Cfg) : Prop := ∃ i : Fin 11, B.mem (z i)

/-- NO square of `z` has its pose in the box `B` — A120's NO-family branch `¬A_ℓ`. -/
def NoneIn (B : Box) (z : Cfg) : Prop := ∀ i : Fin 11, ¬ B.mem (z i)

/-- **The YES/NO cover is a tautology.** -/
theorem yes_or_no (Ls : List Box) (z : Cfg) :
    (∀ i : Fin Ls.length, SomeIn (Ls.get i) z) ∨ ∃ i : Fin Ls.length, NoneIn (Ls.get i) z := by
  classical
  by_cases h : ∀ i : Fin Ls.length, SomeIn (Ls.get i) z
  · exact Or.inl h
  · push Not at h
    obtain ⟨i, hi⟩ := h
    exact Or.inr ⟨i, fun j hj => hi ⟨j, hj⟩⟩

/-! ## 2. The YES side is `LocalHyp` -/

/-- **The YES side supplies `N`'s hypothesis.**  `hdisj` is A120's clause **A2** (the `|L|`
boxes are pairwise pose-disjoint — without it two of the `A_ℓ` could be witnessed by the SAME
square and YES would not give `|L|` DISTINCT squares) and `hsep` is its clause **A3** (each box
is pose-disjoint from every pin at the side in question). -/
theorem localHyp_of_yes {Ls : List Box} {Ps : List Pin} {s : ℝ} {z : Cfg}
    (hL : ∀ i : Fin Ls.length, SomeIn (Ls.get i) z)
    (hdisj : ∀ i j : Fin Ls.length, i ≠ j → ∀ q : PSq, (Ls.get i).mem q → ¬ (Ls.get j).mem q)
    (hsep : ∀ (i : Fin Ls.length) (j : Fin Ps.length) (q : PSq),
      (Ls.get i).mem q → ¬ (Ps.get j).mem s q)
    (wP : Fin Ps.length → Fin 11) (hwP : Function.Injective wP)
    (hP : ∀ j : Fin Ps.length, (Ps.get j).mem s (z (wP j))) :
    LocalHyp Ls Ps s z := by
  classical
  choose wL hwL using hL
  refine ⟨wL, wP, ?_, hwP, ?_, hwL, hP⟩
  · intro i j hij
    by_contra hne
    refine hdisj i j hne (z (wL i)) (hwL i) ?_
    rw [hij]
    exact hwL j
  · intro i j hij
    refine hsep i j (z (wL i)) (hwL i) ?_
    rw [hij]
    exact hP j

/-! ## 3. The composition -/

/-- **The region-tree step.**  `H` is covered by its YES sub-hypothesis and its `|L|` NO
children; `LocalDead N` empties the YES leaf at every side `≤ s0`, so if every NO child is
empty, so is `H`. -/
theorem node_dead_of_yes_no {Ls : List Box} {Ps : List Pin} {s0 : ℝ} {H : ℝ → Cfg → Prop}
    (hD : LocalDead Ls Ps s0)
    (hyes : ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z →
      (∀ i : Fin Ls.length, SomeIn (Ls.get i) z) → LocalHyp Ls Ps s z)
    (hno : ∀ (i : Fin Ls.length) (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z →
      ¬ NoneIn (Ls.get i) z) :
    ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → ¬ H s z := by
  intro s z hs hz hH
  rcases yes_or_no Ls z with hy | ⟨i, hi⟩
  · exact absurd (hD s z hz (hyes s z hs hz hH hy)) (not_lt.mpr hs)
  · exact hno i s z hs hz hH hi

/-- **The region-tree step, `ClassKilledAt` form** — the shape `Composition.lean` consumes.
`hH` is "the node's hypothesis holds for every packing of the class at `m`" (Step 1 of the
region tree). -/
theorem classKilledAt_of_yes_no {Ls : List Box} {Ps : List Pin} {s0 : ℝ} {H : ℝ → Cfg → Prop}
    {idx : StratumIdx} {m : ℝ} (hD : LocalDead Ls Ps s0) (hm : m ≤ s0)
    (hyes : ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z →
      (∀ i : Fin Ls.length, SomeIn (Ls.get i) z) → LocalHyp Ls Ps s z)
    (hno : ∀ (i : Fin Ls.length) (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z →
      ¬ NoneIn (Ls.get i) z)
    (hH : ∀ z : Cfg, CfgPacking m z → InStratum idx m z → H m z) :
    ClassKilledAt idx m :=
  classKilledAt_of_kill fun z hz hstr =>
    node_dead_of_yes_no hD hyes hno m z hm hz (hH z hz hstr)

/-! ## 4. The clamp: the YES and NO sides use the same boxes -/

/-- **A packed square's centre is at least `1/2` from every wall.**  `w(t) = cos θ + sin θ ≥ 1`
on `t ∈ [0, 1]` (`wT_ge_one`) and containment is `w/2 ≤ c ≤ s − w/2`
(`set_subset_container_iff`).  This is why A120's clamp of a NO zone to `[1/2, s − 1/2]`
discards no pose a square of a packing could have. -/
theorem centre_in_slab {s : ℝ} {z : Cfg} (hz : CfgPacking s z) (i : Fin 11) :
    1 / 2 ≤ (z i).cx ∧ (z i).cx ≤ s - 1 / 2 ∧
    1 / 2 ≤ (z i).cy ∧ (z i).cy ≤ s - 1 / 2 := by
  obtain ⟨ht, hp⟩ := hz
  obtain ⟨h0, h1⟩ := ht i
  have hsub : (z i).set ⊆ Icc (0 : ℝ) s ×ˢ Icc (0 : ℝ) s := hp.contained i
  have hw := (set_subset_container_iff h0 h1 s).mp hsub
  have hge : (1 : ℝ) ≤ wT (z i).t := wT_ge_one h0 h1
  exact ⟨by linarith [hw.1], by linarith [hw.2.1], by linarith [hw.2.2.1], by linarith [hw.2.2.2]⟩

/-- **The clamp is free.**  If the clamped box `B'` is `B` intersected with the wall slab, then
`NoneIn B' z` implies `NoneIn B z` for every packing `z` — so a NO child certified against the
CLAMPED zone kills the branch of the UNCLAMPED box.  That settles the clamp, which is what A120
flagged; what it does not settle is the ROUNDING with which the zone is written into the
certificate file, and that one goes the wrong way — see finding F-COVER in
`attempts/A126-localdead-lean/notes/obligations.md` §4, and note that the hypotheses below are
stated with `≤` in the direction a zone rounded INWARD satisfies. -/
theorem noneIn_of_clamped {s : ℝ} {z : Cfg} {B B' : Box} (hz : CfgPacking s z)
    (hcx0 : B'.cx0 ≤ max B.cx0 (1 / 2)) (hcx1 : min B.cx1 (s - 1 / 2) ≤ B'.cx1)
    (hcy0 : B'.cy0 ≤ max B.cy0 (1 / 2)) (hcy1 : min B.cy1 (s - 1 / 2) ≤ B'.cy1)
    (ht0 : B'.t0 ≤ B.t0) (ht1 : B.t1 ≤ B'.t1)
    (h : NoneIn B' z) : NoneIn B z := by
  intro i hi
  obtain ⟨hx0, hx1, hy0, hy1⟩ := centre_in_slab hz i
  obtain ⟨⟨hbx0, hbx1⟩, ⟨hby0, hby1⟩, hbt0, hbt1⟩ := hi
  refine h i ⟨⟨?_, ?_⟩, ⟨?_, ?_⟩, ?_, ?_⟩
  · exact le_trans hcx0 (max_le hbx0 hx0)
  · exact le_trans (le_min hbx1 hx1) hcx1
  · exact le_trans hcy0 (max_le hby0 hy0)
  · exact le_trans (le_min hby1 hy1) hcy1
  · exact le_trans ht0 hbt0
  · exact le_trans hbt1 ht1

/-! ## 5. The A120 instantiation — `k5_11_interior_Y0230`

A120 closed four level-1 nodes of the `k5_11` interior tree at `s0 = 3.877084` in the MIXED
sense: the YES leaf by A116/A119's local certificate for `N = S02_k5_11_r0.20_rho10` (four
boxes `f1, f2, f3, BR(0,1)` and five pins, carried into the node frame by a `D4` map), the four
NO children by the frozen `verify_case.py`.  `y0230_dead` is that closure as a Lean statement:
every hypothesis is one of A120's own soundness clauses or one of its four certificates, and
`node_dead_of_yes_no` is the only reasoning step.

What is NOT yet in Lean, per hypothesis:

* `hD` — `LocalDead` for `S02_k5_11_r0.20_rho10`: `LocalCertS02.localDead_s02` supplies it
  modulo the one cover obligation `CertCover` (A126 T1).
* `hdisj` / `hsep` — A120's **A2** / **A3**.  Both are finite rational interval tests on the
  four mapped boxes and the five pins (`octagon.boxes_pose_disjoint`, `pinguard.classify`);
  in Lean they are `decide`-able once the boxes are rational, which they are.
* `wP`, `hwP`, `hP` — the node's own class hypothesis (Step 1): the five pins are occupied by
  five distinct squares.  This is `ContainsPins` transported by A120's clause **A1** (the pins
  of `N` ARE the node's pins in the node frame) and **A4** (the `D4` map is exactly invertible).
* `hno` — the four NO children.  Each is a PASSing `case-measure-certificate-v1` with a
  nonempty NO-family list, so the Lean consumer is `checkCaseI_no_family` (a PASS forces SOME
  non-owner square into a zone, contradicting `NoneIn`), not `checkCaseI_kill`.  Two steps are
  missing between the two: the certificates have to be replayed
  (`lean/gen_case_lean.py` + `native_decide`, the A78 route — `attempts/A126-localdead-lean/
  notes/obligations.md` §3 records the four files and their Python walls), and
  `checkCaseI_no_family` speaks of an `IsStrictFamily` (pairwise disjoint CLOSED squares) while
  `CfgPacking` gives interior-disjointness, so `Dilation.lean`'s Lemma B has to be applied
  first.  Both are pre-existing gaps of the frozen fixed-side route, not new ones.
  A third is NEW and is finding F-COVER: the zone the certificate is proved about is the
  box rounded OUTWARD (by `≤ 1.1·10⁻⁷` in tilt), while the split needs it rounded INWARD,
  so `hno` as certified is about a slightly LARGER zone than `NoneIn (Ls.get i)` names. -/
theorem y0230_dead {Ls : List Box} {Ps : List Pin} {s0 : ℝ} {H : ℝ → Cfg → Prop}
    (hD : LocalDead Ls Ps s0)
    (hdisj : ∀ i j : Fin Ls.length, i ≠ j → ∀ q : PSq, (Ls.get i).mem q → ¬ (Ls.get j).mem q)
    (hsep : ∀ (s : ℝ) (i : Fin Ls.length) (j : Fin Ps.length) (q : PSq),
      (Ls.get i).mem q → ¬ (Ps.get j).mem s q)
    (hpins : ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z →
      ∃ wP : Fin Ps.length → Fin 11, Function.Injective wP ∧
        ∀ j : Fin Ps.length, (Ps.get j).mem s (z (wP j)))
    (hno : ∀ (i : Fin Ls.length) (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → H s z →
      ¬ NoneIn (Ls.get i) z) :
    ∀ (s : ℝ) (z : Cfg), s ≤ s0 → CfgPacking s z → ¬ H s z := by
  refine node_dead_of_yes_no hD (fun s z hs hz hH hy => ?_) hno
  obtain ⟨wP, hwP, hP⟩ := hpins s z hs hz hH
  exact localHyp_of_yes hy hdisj (hsep s) wP hwP hP

end

end LocalCert
end S11
end PackingCert
