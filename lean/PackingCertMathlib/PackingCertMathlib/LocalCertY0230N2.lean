import PackingCertMathlib.LocalCertY0230Data
import PackingCertMathlib.CaseBridge
-- deliberately NOT importing `LocalCompose`: the `native_decide` below is the most expensive
-- thing in this attempt, and coupling it to the checker would mean re-running it whenever
-- `LocalCert.lean` changes.  The composition that consumes these PASSes is
-- `LocalCompose.y0230_dead`, which takes the NO side as a hypothesis.

/-!
# `k5_11_interior_Y0230`, NO child N2, replayed — A126 T3

One of the four PASSing `case-measure-certificate-v1` files of A120's closed node, converted by
`lean/gen_case_lean.py` (the A78 route) and re-run by `native_decide` inside the kernel.
Depth 56, `n = 11`, `s = 969271/250000`, **6 cores** (the node's five class pins plus its own
conditioned square) and **one NO-family zone**.  Python wall of the frozen `verify_case.py` on
this one: **27.6 s on 492 190 boxes**.

ONE certificate per module, deliberately: a `native_decide` is not cached until its module
finishes, so four in one file means an interrupted build banks nothing.  Smallest first
(`N3` → `N2` → `N1` → `N0`).

Because the zone list is NONEMPTY the consumer is `checkCaseI_no_family` — a PASS forces SOME
non-owner square of the family into the zone, which is exactly what the NO child denies — and
not `checkCaseI_kill`, which needs `nofams = []`.

Not built by the default target.  Build it with

    python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.LocalCertY0230N2
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The `N2` certificate PASSes `checkCaseI` (native_decide evaluation). -/
theorem check_y0230_no2 : checkCaseI Data.y0230_no2 = true := by native_decide

/-- **A PASSing NO certificate forces a square into its zone.**  For a strict family of 11
closed unit squares in `[0, s0]²` whose designated members contain the six cores, SOME
non-owner square lies in the certificate's NO-family zone — precisely what the NO child
denies. -/
theorem y0230_no2_forces {Q : Fin Data.y0230_no2.n → Set RP}
    (hQ : IsStrictFamily Data.y0230_no2.n (caseSide Data.y0230_no2) Q)
    (own : Fin Data.y0230_no2.cores.length → Fin Data.y0230_no2.n)
    (hown : ∀ j, coreSet (Data.y0230_no2.cores.get j) ⊆ Q (own j)) :
    ∃ i, (∀ j, own j ≠ i) ∧ CaseExempt Data.y0230_no2 (Q i) :=
  checkCaseI_no_family check_y0230_no2 hQ own hown

end S11
end PackingCert
