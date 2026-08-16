import PackingCert.Checker
import PackingCert.Data
import PackingCert.DataTight

/-!
# The main theorems

`checkPacking trump11 = true`, established by evaluating the (all-integer,
decidable) checker on the certificate data.  `native_decide` compiles the
checker to native code and trusts the compiler (adds the `native_decide` axiom);
`decide` runs it in the kernel.  See `Kernel.lean` for the axiom-free variant.

* `Data.trump11`       : certs/trump11_certificate_int.json,       side 969271/250000 = 3.877084
* `Data.trump11_tight` : certs/trump11_certificate_tight_int.json, side 3877083591023/10^12
-/

namespace PackingCert

open Data

theorem trump11_ok : checkPacking trump11 = true := by native_decide
theorem trump11_count : trump11.squares.length = 11 := by rfl
theorem trump11_side : trump11.sideNum = 969271 ∧ trump11.sideDen = 250000 := by decide

theorem trump11_tight_ok : checkPacking trump11_tight = true := by native_decide
theorem trump11_tight_count : trump11_tight.squares.length = 11 := by rfl

end PackingCert
