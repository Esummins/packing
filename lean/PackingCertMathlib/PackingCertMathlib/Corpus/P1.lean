import PackingCertMathlib.Corpus.P1.Check_m3_trump5_interior_NO

/-!
# Corpus P1 replayed in Lean (A78 T5)

D.P1 -- `attempts/A59-trump-residual/certs/m3_trump5_interior_NO.json`, the trump5 interior residual: 5 cores + 1 NO-family, budget 6 (B-NO form).

`corpus_P1` is the conjunction of the 1 per-certificate `check_*` facts.
Each conjunct was evaluated ONCE, in its own module (`Corpus/P1/Check_<name>.lean`);
this module only pairs the finished proofs -- it triggers no evaluation.
-/

namespace PackingCert
namespace S11

open CaseI

/-- **Corpus P1**: `checkCaseI` PASSes on all 1 certificates. -/
theorem corpus_P1 :
    checkCaseI Data.m3_trump5_interior_NO = true :=
  ⟨check_m3_trump5_interior_NO⟩

end S11
end PackingCert
