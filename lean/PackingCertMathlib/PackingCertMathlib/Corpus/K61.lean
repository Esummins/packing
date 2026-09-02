import PackingCertMathlib.Corpus.K61.Check_k3_00
import PackingCertMathlib.Corpus.K61.Check_k4_00
import PackingCertMathlib.Corpus.K61.Check_k4_01
import PackingCertMathlib.Corpus.K61.Check_k4_02
import PackingCertMathlib.Corpus.K61.Check_k4_04
import PackingCertMathlib.Corpus.K61.Check_k4_07
import PackingCertMathlib.Corpus.K61.Check_k4_09
import PackingCertMathlib.Corpus.K61.Check_k4_10
import PackingCertMathlib.Corpus.K61.Check_k4_12
import PackingCertMathlib.Corpus.K61.Check_k5_00
import PackingCertMathlib.Corpus.K61.Check_k5_01
import PackingCertMathlib.Corpus.K61.Check_k5_02
import PackingCertMathlib.Corpus.K61.Check_k5_03
import PackingCertMathlib.Corpus.K61.Check_k5_04
import PackingCertMathlib.Corpus.K61.Check_k5_05
import PackingCertMathlib.Corpus.K61.Check_k5_06
import PackingCertMathlib.Corpus.K61.Check_k5_07
import PackingCertMathlib.Corpus.K61.Check_k5_08
import PackingCertMathlib.Corpus.K61.Check_k5_09
import PackingCertMathlib.Corpus.K61.Check_k5_10
import PackingCertMathlib.Corpus.K61.Check_k5_12
import PackingCertMathlib.Corpus.K61.Check_k5_13
import PackingCertMathlib.Corpus.K61.Check_k5_14
import PackingCertMathlib.Corpus.K61.Check_k5_15
import PackingCertMathlib.Corpus.K61.Check_k5_17
import PackingCertMathlib.Corpus.K61.Check_k5_18
import PackingCertMathlib.Corpus.K61.Check_k5_19
import PackingCertMathlib.Corpus.K61.Check_k5_20
import PackingCertMathlib.Corpus.K61.Check_k6_00
import PackingCertMathlib.Corpus.K61.Check_k6_01
import PackingCertMathlib.Corpus.K61.Check_k6_02
import PackingCertMathlib.Corpus.K61.Check_k6_03
import PackingCertMathlib.Corpus.K61.Check_k6_04
import PackingCertMathlib.Corpus.K61.Check_k6_05
import PackingCertMathlib.Corpus.K61.Check_k6_06
import PackingCertMathlib.Corpus.K61.Check_k6_07
import PackingCertMathlib.Corpus.K61.Check_k6_08
import PackingCertMathlib.Corpus.K61.Check_k6_09
import PackingCertMathlib.Corpus.K61.Check_k6_10
import PackingCertMathlib.Corpus.K61.Check_k6_11
import PackingCertMathlib.Corpus.K61.Check_k6_12
import PackingCertMathlib.Corpus.K61.Check_k6_13
import PackingCertMathlib.Corpus.K61.Check_k6_14
import PackingCertMathlib.Corpus.K61.Check_k6_15
import PackingCertMathlib.Corpus.K61.Check_k6_16
import PackingCertMathlib.Corpus.K61.Check_k6_17
import PackingCertMathlib.Corpus.K61.Check_k6_18
import PackingCertMathlib.Corpus.K61.Check_k6_19
import PackingCertMathlib.Corpus.K61.Check_k6_20
import PackingCertMathlib.Corpus.K61.Check_k6_21
import PackingCertMathlib.Corpus.K61.Check_k6_22
import PackingCertMathlib.Corpus.K61.Check_k6_23
import PackingCertMathlib.Corpus.K61.Check_k6_24
import PackingCertMathlib.Corpus.K61.Check_k6_25
import PackingCertMathlib.Corpus.K61.Check_k6_26
import PackingCertMathlib.Corpus.K61.Check_k6_27
import PackingCertMathlib.Corpus.K61.Check_k6_28
import PackingCertMathlib.Corpus.K61.Check_k6_29
import PackingCertMathlib.Corpus.K61.Check_k6_30
import PackingCertMathlib.Corpus.K61.Check_k6_31
import PackingCertMathlib.Corpus.K61.Check_k6_32

/-!
# Corpus K61 replayed in Lean (A78 T5)

C.K61 -- the 61 pin-set kills of the A53/A54/A55 cap (`attempts/A55-k4-sweep/results/cap.json`, field `certified`), all at `s = 969271/250000`, all with empty `nofams` (kill form).

`corpus_K61` is the conjunction of the 61 per-certificate `check_*` facts.
Each conjunct was evaluated ONCE, in its own module (`Corpus/K61/Check_<name>.lean`);
this module only pairs the finished proofs -- it triggers no evaluation.
-/

namespace PackingCert
namespace S11

open CaseI

/-- **Corpus K61**: `checkCaseI` PASSes on all 61 certificates. -/
theorem corpus_K61 :
    checkCaseI Data.k3_00 = true ∧
    checkCaseI Data.k4_00 = true ∧
    checkCaseI Data.k4_01 = true ∧
    checkCaseI Data.k4_02 = true ∧
    checkCaseI Data.k4_04 = true ∧
    checkCaseI Data.k4_07 = true ∧
    checkCaseI Data.k4_09 = true ∧
    checkCaseI Data.k4_10 = true ∧
    checkCaseI Data.k4_12 = true ∧
    checkCaseI Data.k5_00 = true ∧
    checkCaseI Data.k5_01 = true ∧
    checkCaseI Data.k5_02 = true ∧
    checkCaseI Data.k5_03 = true ∧
    checkCaseI Data.k5_04 = true ∧
    checkCaseI Data.k5_05 = true ∧
    checkCaseI Data.k5_06 = true ∧
    checkCaseI Data.k5_07 = true ∧
    checkCaseI Data.k5_08 = true ∧
    checkCaseI Data.k5_09 = true ∧
    checkCaseI Data.k5_10 = true ∧
    checkCaseI Data.k5_12 = true ∧
    checkCaseI Data.k5_13 = true ∧
    checkCaseI Data.k5_14 = true ∧
    checkCaseI Data.k5_15 = true ∧
    checkCaseI Data.k5_17 = true ∧
    checkCaseI Data.k5_18 = true ∧
    checkCaseI Data.k5_19 = true ∧
    checkCaseI Data.k5_20 = true ∧
    checkCaseI Data.k6_00 = true ∧
    checkCaseI Data.k6_01 = true ∧
    checkCaseI Data.k6_02 = true ∧
    checkCaseI Data.k6_03 = true ∧
    checkCaseI Data.k6_04 = true ∧
    checkCaseI Data.k6_05 = true ∧
    checkCaseI Data.k6_06 = true ∧
    checkCaseI Data.k6_07 = true ∧
    checkCaseI Data.k6_08 = true ∧
    checkCaseI Data.k6_09 = true ∧
    checkCaseI Data.k6_10 = true ∧
    checkCaseI Data.k6_11 = true ∧
    checkCaseI Data.k6_12 = true ∧
    checkCaseI Data.k6_13 = true ∧
    checkCaseI Data.k6_14 = true ∧
    checkCaseI Data.k6_15 = true ∧
    checkCaseI Data.k6_16 = true ∧
    checkCaseI Data.k6_17 = true ∧
    checkCaseI Data.k6_18 = true ∧
    checkCaseI Data.k6_19 = true ∧
    checkCaseI Data.k6_20 = true ∧
    checkCaseI Data.k6_21 = true ∧
    checkCaseI Data.k6_22 = true ∧
    checkCaseI Data.k6_23 = true ∧
    checkCaseI Data.k6_24 = true ∧
    checkCaseI Data.k6_25 = true ∧
    checkCaseI Data.k6_26 = true ∧
    checkCaseI Data.k6_27 = true ∧
    checkCaseI Data.k6_28 = true ∧
    checkCaseI Data.k6_29 = true ∧
    checkCaseI Data.k6_30 = true ∧
    checkCaseI Data.k6_31 = true ∧
    checkCaseI Data.k6_32 = true :=
  ⟨check_k3_00, check_k4_00, check_k4_01, check_k4_02, check_k4_04, check_k4_07, check_k4_09, check_k4_10, check_k4_12, check_k5_00, check_k5_01, check_k5_02, check_k5_03, check_k5_04, check_k5_05, check_k5_06, check_k5_07, check_k5_08, check_k5_09, check_k5_10, check_k5_12, check_k5_13, check_k5_14, check_k5_15, check_k5_17, check_k5_18, check_k5_19, check_k5_20, check_k6_00, check_k6_01, check_k6_02, check_k6_03, check_k6_04, check_k6_05, check_k6_06, check_k6_07, check_k6_08, check_k6_09, check_k6_10, check_k6_11, check_k6_12, check_k6_13, check_k6_14, check_k6_15, check_k6_16, check_k6_17, check_k6_18, check_k6_19, check_k6_20, check_k6_21, check_k6_22, check_k6_23, check_k6_24, check_k6_25, check_k6_26, check_k6_27, check_k6_28, check_k6_29, check_k6_30, check_k6_31, check_k6_32⟩

end S11
end PackingCert
