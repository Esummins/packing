import PackingCertMathlib.LocalCertY0230N3
import PackingCertMathlib.LocalCertY0230N2
import PackingCertMathlib.LocalCertY0230N1
import PackingCertMathlib.LocalCertY0230N0

/-!
# A120's node `k5_11_interior_Y0230`: the four NO children, replayed — A126 T3

A120 closed `k5_11_interior_Y0230` at `s0 = 3.877084` in the MIXED sense: the YES leaf by the
local certificate of `N = S02_k5_11_r0.20_rho10` (`LocalCertS02.localDead_s02`, modulo
`CertCover`), the four NO children by the frozen `verify_case.py`.  This module gathers the four
replays — one per module, smallest first, so that an interrupted build banks what it finished:

| module | certificate | boxes | Python wall |
|---|---|---|---|
| `LocalCertY0230N3` | `NO3` | 230 914 | 14.3 s |
| `LocalCertY0230N2` | `NO2` | 492 190 | 27.6 s |
| `LocalCertY0230N1` | `NO1_r6` (`NO1` itself FAILs and was re-priced) | 820 808 | 34.5 s |
| `LocalCertY0230N0` | `NO0` | 1 207 184 | 54.4 s |

What still separates these four PASSes from `LocalCompose.y0230_dead`'s `hno` is recorded in
`attempts/A126-localdead-lean/notes/obligations.md` §3 and §4: the `IsStrictFamily`-versus-
interior-disjoint bridge (`Dilation.lean`'s Lemma B), the pose-versus-set step, and finding
F-COVER (the certified zone is the YES box rounded OUTWARD, while the split needs it INWARD).

Not built by the default target.  Build it with

    python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.LocalCertY0230
-/

namespace PackingCert
namespace S11

open CaseI

/-- The four certificates are all at `s0 = 969271/250000`. -/
theorem y0230_side : caseSide Data.y0230_no0 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

end S11
end PackingCert
