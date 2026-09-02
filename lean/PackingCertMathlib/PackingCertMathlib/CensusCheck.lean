import PackingCertMathlib.Census
import PackingCertMathlib.CensusCorpus

/-!
# The census, COUNTED and cross-checked against A72 (A78, depgraph node B.CENSUS)

`native_decide` facts about the Lean census of `Census.lean`.  Nothing in the
composition (`TopLevel.lean`) depends on this file: the exhaustiveness theorem
`skeleton_mem_census` and the class decomposition `exists_class_skeleton` are proved
without computation.  This file is the machine-checked form of the two independent
enumerations (A53 `skeletons2.py`, A72 `enum_census.py`): the Lean definition
reproduces **1110 tuples / 163 D4 classes**, is D4-closed, equals A72's tuple set
exactly, induces exactly A72's orbit partition, and places Trump's skeleton in a
`k = 5` class.

Each `native_decide` theorem below carries exactly the `Lean.ofReduceBool` axiom on top
of `propext, Classical.choice, Quot.sound`; see `scratch/Axioms.lean`.
-/

namespace PackingCert
namespace S11

open CensusCorpus

/-- **1110 census tuples.** -/
theorem censusL_length : censusL.length = 1110 := by native_decide

/-- The list has no repeats (so `censusF.card = 1110`). -/
theorem censusL_nodup : censusL.Nodup := by native_decide

theorem censusF_card : censusF.card = 1110 := by
  rw [censusF, List.toFinset_card_of_nodup censusL_nodup, censusL_length]

/-- **163 D4 classes.** -/
theorem classCodes_length : classCodes.length = 163 := by native_decide

/-- **The Lean census equals A72's clean-room census** as a set of slot-sets (A72's
`sha256 tuple_set f035681a…`, itself equal to A53's). -/
theorem census_eq_corpus : censusF = (corpusTuples.map decodePins).toFinset := by
  native_decide

/-- **D4-closure** (A72 check `B8_d4_closed`): every image of a census tuple is a census
tuple. -/
theorem census_d4_closed : ∀ T ∈ censusL, ∀ g ∈ d4List, d4Pins g T ∈ censusF := by
  native_decide

/-- **A72's orbit partition is the Lean orbit partition**: every member of an A72 class
has the same Lean canonical code as the class head … -/
theorem corpus_classes_canon : ∀ cls ∈ corpusClasses, ∀ T ∈ cls,
    canonCode (decodePins T) = canonCode (decodePins (cls.headD [])) := by
  native_decide

/-- … and distinct A72 classes have distinct Lean canonical codes. -/
theorem corpus_classes_distinct :
    (corpusClasses.map fun cls => canonCode (decodePins (cls.headD []))).Nodup := by
  native_decide

theorem corpus_classes_length : corpusClasses.length = 163 := by native_decide

theorem corpus_classes_flatten_length : corpusClasses.flatten.length = 1110 := by
  native_decide

/-- **Trump canary** (A53 L4 / A72 `trump_tuples_found = 1`): the tuple
`((2,1), (1), (1), ∅)` is A72's Trump tuple, is a census tuple, has `k = 5`. -/
theorem trumpPins_eq_corpus : trumpPins = decodePins corpusTrump := by native_decide

theorem trumpPins_card : trumpPins.card = 5 := by native_decide

theorem trumpPins_isCensusTuple' : IsCensusTuple trumpPins := by native_decide

/-- The index of Trump's class in `classCodes`. -/
def trumpClassIdx : ℕ := classCodes.idxOf (canonCode trumpPins)

theorem trumpClassIdx_lt : trumpClassIdx < classCodes.length := by native_decide

end S11
end PackingCert
