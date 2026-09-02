import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_00
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_01
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_02
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_03
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_04
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_05
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_06
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_07
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_08
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_09
import PackingCertMathlib.Corpus.THMU.Check_u_reinsert_10

/-!
# Corpus THMU replayed in Lean (A78 T5)

A.THMU -- the 11 Theorem-U re-insertion certificates `attempts/A65-low-k-closure/certs/u_reinsert_{00..10}.json` at `s = 3877083591023/1000000000000`: 10 cores, 1 NO-family, budget 1, 0 atoms (B-NO form).

`corpus_THMU` is the conjunction of the 11 per-certificate `check_*` facts.
Each conjunct was evaluated ONCE, in its own module (`Corpus/THMU/Check_<name>.lean`);
this module only pairs the finished proofs -- it triggers no evaluation.
-/

namespace PackingCert
namespace S11

open CaseI

/-- **Corpus THMU**: `checkCaseI` PASSes on all 11 certificates. -/
theorem corpus_THMU :
    checkCaseI Data.u_reinsert_00 = true ∧
    checkCaseI Data.u_reinsert_01 = true ∧
    checkCaseI Data.u_reinsert_02 = true ∧
    checkCaseI Data.u_reinsert_03 = true ∧
    checkCaseI Data.u_reinsert_04 = true ∧
    checkCaseI Data.u_reinsert_05 = true ∧
    checkCaseI Data.u_reinsert_06 = true ∧
    checkCaseI Data.u_reinsert_07 = true ∧
    checkCaseI Data.u_reinsert_08 = true ∧
    checkCaseI Data.u_reinsert_09 = true ∧
    checkCaseI Data.u_reinsert_10 = true :=
  ⟨check_u_reinsert_00, check_u_reinsert_01, check_u_reinsert_02, check_u_reinsert_03, check_u_reinsert_04, check_u_reinsert_05, check_u_reinsert_06, check_u_reinsert_07, check_u_reinsert_08, check_u_reinsert_09, check_u_reinsert_10⟩

end S11
end PackingCert
