import PackingCertMathlib.Corpus.K61.Check_k6_07
import PackingCertMathlib.Corpus.K61.Check_k6_19
import PackingCertMathlib.Corpus.K61.Check_k6_21
import PackingCertMathlib.Corpus.K61.Check_k6_22
import PackingCertMathlib.Corpus.K61.Check_k6_23
import PackingCertMathlib.Corpus.K61.Check_k6_24

/-!
# Corpus TRAP replayed in Lean (A78 T5)

D.TRAP -- the six k6 trapped classes {k6_07, k6_19, k6_21, k6_22, k6_23, k6_24}.  These are members of C.K61: this module re-uses the K61 `check_*` facts, it does NOT re-evaluate them.

`corpus_TRAP` is the conjunction of the 6 per-certificate `check_*` facts.
Each conjunct was evaluated ONCE, in its own module (`Corpus/K61/Check_<name>.lean`);
this module only pairs the finished proofs -- it triggers no evaluation.
-/

namespace PackingCert
namespace S11

open CaseI

/-- **Corpus TRAP**: `checkCaseI` PASSes on all 6 certificates. -/
theorem corpus_TRAP :
    checkCaseI Data.k6_07 = true ∧
    checkCaseI Data.k6_19 = true ∧
    checkCaseI Data.k6_21 = true ∧
    checkCaseI Data.k6_22 = true ∧
    checkCaseI Data.k6_23 = true ∧
    checkCaseI Data.k6_24 = true :=
  ⟨check_k6_07, check_k6_19, check_k6_21, check_k6_22, check_k6_23, check_k6_24⟩

end S11
end PackingCert
