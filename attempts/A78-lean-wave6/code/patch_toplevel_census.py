#!/usr/bin/env python3
"""A78 T1/T4: replace the opaque census layer of TopLevel.lean (StratumIdx / trumpStratum /
InStratum axioms) by definitions from Census.lean, and discharge `stratify` and
`unique_transfer` (both follow from census exhaustiveness, unique_transfer.md section 1).
Targeted, assert-guarded replacements; safe to re-run only once."""
import os, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
P = os.path.join(REPO, 'lean/PackingCertMathlib/PackingCertMathlib/TopLevel.lean')
s = open(P, encoding='utf-8').read()

def rep(old, new):
    global s
    assert s.count(old) == 1, ('pattern count != 1:', old[:80], s.count(old))
    s = s.replace(old, new)

rep("import PackingCertMathlib.ThetaT\n",
    "import PackingCertMathlib.ThetaT\nimport PackingCertMathlib.Census\n")

rep("""* `StratumIdx / trumpStratum / InStratum` — the Young-form skeleton census (A53) is not yet a
  formal definition; the stratum predicate is opaque here.  NOTE the intended semantics is
  "the selected minimiser's skeleton is EXACTLY this class" (see `stratum_kill` docstring for
  why the certificate-native "contains these pins" reading would make the axiom false).""",
"""* `StratumIdx / trumpStratum / InStratum` — DISCHARGED (A78, `Census.lean`): the Young-form
  skeleton census is a Lean DEFINITION (`skeleton`, `censusL`, `classCodes`, the D4 action);
  `StratumIdx` is the index type of the 163 class representatives, `InStratum i s z` is
  "the skeleton of `z` at side `s` is a D4-image of representative `i`" (EXACT class
  membership, as the `stratum_kill` docstring requires), `trumpStratum` the class of
  `((2,1),(1),(1),∅)`.  Census exhaustiveness (`skeleton_mem_census`, A53 L3) then proves
  `stratify` and `unique_transfer` below (unique_transfer.md §1).""")

rep("""/-- **[census — definitional debt]** Index type of the stratification (intended: the 163
D4 classes of the A53 Young-form census; kept opaque until the census definition is
formalised — checklist H2's independent re-enumeration then gets a formal target). -/
axiom StratumIdx : Type

/-- The distinguished stratum: Trump's `k = 5` skeleton class (`trump5`). -/
axiom trumpStratum : StratumIdx

/-- `InStratum i s z`: the configuration `z`, as a packing at side `s`, has skeleton
EXACTLY of class `i`.  The side parameter is essential: skeleton pins are anchored to the
walls of `[0,s]²`, so the predicate is a different subset of configuration space at every
`s` — this is what makes window transfer (H6) a per-certificate obligation rather than a
bookkeeping step.  Findings F4/F6. -/
axiom InStratum : StratumIdx → ℝ → Cfg → Prop
""",
"""/-- **[census]** Index type of the stratification: the D4 class representatives of the
Young-form census (`Census.lean`: `classCodes`, the distinct canonical codes of the 1110
census tuples — 163 of them, `CensusCheck.lean`).  DISCHARGED (A78): was an opaque axiom;
checklist F11/H2. -/
def StratumIdx : Type := Fin classCodes.length

/-- Trump's tuple lies in the census (kernel `decide`), hence its canonical code is one of
the class codes. -/
theorem trumpCode_mem : canonCode trumpPins ∈ classCodes :=
  List.mem_dedup.mpr (List.mem_map.mpr
    ⟨trumpPins, mem_censusL_of_isCensusTuple trumpPins_isCensusTuple, rfl⟩)

/-- The distinguished stratum: Trump's `k = 5` skeleton class (`trump5`,
`((2,1),(1),(1),∅)` up to D4; `trumpPins`).  DISCHARGED (A78): a definition. -/
def trumpStratum : StratumIdx :=
  ⟨classCodes.idxOf (canonCode trumpPins), List.idxOf_lt_length_of_mem trumpCode_mem⟩

/-- `InStratum i s z`: the configuration `z`, as a packing at side `s`, has skeleton
EXACTLY of class `i` — its Young-form skeleton at side `s` (`skeleton s z`, the largest
Young set of exactly-on-grid axis-aligned squares at each corner, A53 L1) is a D4-image of
the class representative `classRep i`.  DISCHARGED (A78): a definition.  The side
parameter is essential: skeleton pins are anchored to the walls of `[0,s]²`, so the
predicate is a different subset of configuration space at every `s` — this is what makes
window transfer (H6) a per-certificate obligation rather than a bookkeeping step.
Findings F4/F6. -/
def InStratum (i : StratumIdx) (s : ℝ) (z : Cfg) : Prop :=
  InClassOf (skeleton s z) (classRep i)

/-- The window sits inside `(3, 4)`, where the census is one object (A53 L2(iv),
`Census.lean`). -/
theorem wnd_subset_Ioo {m : ℝ} (hm : m ∈ wnd) : 3 < m ∧ m < 4 := by
  obtain ⟨h1, h2⟩ := hm
  have h3 := shat_spec.2.1.2
  norm_num at h1 h3
  exact ⟨by linarith, by linarith⟩

/-- **Census exhaustiveness in composition form** (A53 L3, `skeleton_mem_census` +
`exists_class_skeleton`): every packing at a side in the window lies in some stratum. -/
theorem exists_stratum {m : ℝ} (hm : m ∈ wnd) {z : Cfg} (hz : CfgPacking m z) :
    ∃ i : StratumIdx, InStratum i m z :=
  exists_class_skeleton (wnd_subset_Ioo hm).1 (wnd_subset_Ioo hm).2 hz.2
""")

rep("""/-- **[H1 + H2 — selection + exhaustiveness]** If the minimum is attained at
`m ∈ [3.82, ŝ]`, then SOME minimiser (the k-maximal slide-stuck selected one) lies in some
stratum.  Note the quantifier: this produces an existential witness, NOT a statement about
every minimiser — the uniqueness clause therefore needs the separate, strictly stronger
`unique_transfer` below (findings F3, the largest hole this file forced).  STATUS: L6/CC-2
selection lemma in attempt notes (A53/A58), census exact but single-implementation;
degenerate slide cases (H1) unwritten. -/
axiom stratify : ∀ m : ℝ, IsLeast {s : ℝ | Fits 11 s} m → m ∈ wnd →
    ∃ (z : Cfg) (i : StratumIdx), CfgPacking m z ∧ InStratum i m z
""",
"""/-- **[H1 + H2 — selection + exhaustiveness]** If the minimum is attained at
`m ∈ [3.82, ŝ]`, then SOME minimiser lies in some stratum.  DISCHARGED (A78): was an
axiom; now a theorem from `parametrize` + census exhaustiveness (`exists_stratum`).  As
STATED the selection content is empty — any minimiser has a skeleton — and the
k-maximal/teleport-stuck selection (`exists_kmax_skeleton`, `cc2_stuck_census` in
`CensusSelection.lean`) is consumed downstream by the H10-stuck route of
`stratum_kill`'s quantifier caveat, not here.  The uniqueness clause needs the separate
`unique_transfer` below (findings F3). -/
theorem stratify : ∀ m : ℝ, IsLeast {s : ℝ | Fits 11 s} m → m ∈ wnd →
    ∃ (z : Cfg) (i : StratumIdx), CfgPacking m z ∧ InStratum i m z := by
  intro m hm hw
  obtain ⟨Q, hQ⟩ := hm.1
  obtain ⟨z, hzt, hzQ⟩ := parametrize Q hQ
  have hz : CfgPacking m z := by
    refine ⟨hzt, ?_⟩
    have hfun : (fun i => (z i).set) = Q := funext fun i => (hzQ i).symm
    rw [hfun]
    exact hQ
  obtain ⟨i, hi⟩ := exists_stratum hw hz
  exact ⟨z, i, hz, hi⟩
""")

rep("""Obligations ledger: U-O1..U-O4 in `unique_transfer.md` §5.  Kept as an axiom until the
prose is independently verified. -/
axiom unique_transfer : ∀ z : Cfg, CfgPacking shat z →
    ∃ (z' : Cfg) (f : RP → RP) (e : Equiv.Perm (Fin 11)) (i : StratumIdx),
      IsCtrSym shat f ∧ CfgPacking shat z' ∧ InStratum i shat z' ∧
        ∀ j, (z (e j)).set = f '' (z' j).set
""",
"""Obligations ledger: U-O1..U-O4 in `unique_transfer.md` §5.
DISCHARGED (A78): was an axiom; now a theorem — exactly §1's re-diagnosis: with
`InStratum` definitional, EVERY packing at `ŝ` lies in some stratum (`exists_stratum`),
with `f = id`, `e = 1`, `z' = z` (the D4 normalisation is absorbed by the class
definition).  The hole is therefore now entirely visible in `stratum_kill`'s
∀-packings quantifier at the K1-protected classes (its docstring), where the
non-circular route is the CC-2 chain + Theorem U collapse (`unique_transfer.md` §2–§4;
the chain/collapse formalisation `unique_via_chain` is in `UniqueChain.lean`). -/
theorem unique_transfer : ∀ z : Cfg, CfgPacking shat z →
    ∃ (z' : Cfg) (f : RP → RP) (e : Equiv.Perm (Fin 11)) (i : StratumIdx),
      IsCtrSym shat f ∧ CfgPacking shat z' ∧ InStratum i shat z' ∧
        ∀ j, (z (e j)).set = f '' (z' j).set := by
  intro z hz
  obtain ⟨i, hi⟩ := exists_stratum shat_mem_wnd hz
  refine ⟨z, id, 1, i, ⟨fun _ _ => rfl, Set.image_id _⟩, hz, hi, fun j => ?_⟩
  simp

/-- Every D4 element is a container symmetry (`Census.lean`: `d4Apply_sqdist`,
`d4Apply_image_container`) — the `f` of `trump_residual`/`unique_transfer` can be taken
to be an explicit signed permutation. -/
theorem isCtrSym_d4Apply (s : ℝ) (g : D4) : IsCtrSym s (d4Apply s g) :=
  ⟨d4Apply_sqdist s g, d4Apply_image_container s g⟩
""")

# shat_mem_wnd is defined later in the file (composition glue) but unique_transfer needs it: move
# the two glue lemmas up.  They currently sit after the axioms; hoist them before `zhat`.
glue = """theorem shat_ge_382 : (191 / 50 : ℝ) ≤ shat := by
  have h := shat_spec.2.1.1
  norm_num at h ⊢
  linarith

theorem shat_mem_wnd : shat ∈ wnd := ⟨shat_ge_382, le_refl _⟩

"""
rep(glue, "")
rep("""/-! ## The named hypotheses (the leaf families of the proof plan) -/
""", """/-! ## The named hypotheses (the leaf families of the proof plan) -/

""" + glue)

open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', P)
