import PackingCertMathlib.AliveBridge
import PackingCertMathlib.AliveDataTrump5

/-!
# The Trump-5 ALIVE pilot, composed (A78, node `D.ALIVE`)

`AliveDataTrump5.lean` evaluates `checkAlive` on the `trump5` witness family
(`attempts/A57-shadow-trees/results/alive/trump5_strict.json`); here it is composed with
`alive_sound` to the statement the arbiter is FOR:

> the 5-pin Trump node at side `969271/250000 = 3.877084` admits **no** case-LP
> certificate of budget 6 — a case tree must branch there.

This is a completeness-side (search) statement; it is not part of the trusted composition
of the `s(11)` bound.
-/

namespace PackingCert
namespace S11

open CaseI AliveI AliveData

/-- **The Trump 5-pin node is LP-unkillable** (`checkCaseI`'s sense): every case-LP
certificate with those 5 pin cores, side `3.877084`, `n = 11` and no NO-families FAILS
the verifier — the ALIVE witness family of 6 pairwise-disjoint admissible core-free
unit squares forbids it. -/
theorem trump5_no_case_certificate (c : CCertI)
    (hcores : c.cores = trump5.cores)
    (hside : caseSide c = 969271 / 250000)
    (hn : c.n = 11) (hnf : c.nofams = []) : checkCaseI c = false := by
  refine alive_sound check_trump5_alive c hcores ?_ ?_ hnf
  · rw [hside]
    norm_num [trump5]
  · rw [hn]
    rfl

end S11
end PackingCert
