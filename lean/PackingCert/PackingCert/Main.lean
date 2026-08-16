import PackingCert.Checker
import PackingCert.Data

/-!
# The main theorem

`checkPacking trump11 = true`, established by evaluating the (all-integer,
decidable) checker on the certificate data.  `native_decide` compiles the
checker to native code and trusts the compiler (`Lean.ofReduceBool` axiom);
`decide` / `decide +kernel` runs it in the kernel.  See `Kernel.lean` for the
kernel-only variant and its timing.
-/

namespace PackingCert

open Data

theorem trump11_ok : checkPacking trump11 = true := by native_decide

theorem trump11_count : trump11.squares.length = 11 := by rfl

end PackingCert
