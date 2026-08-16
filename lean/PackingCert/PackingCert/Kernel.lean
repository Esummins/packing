import PackingCert.Checker
import PackingCert.Data

/-!
# Kernel-only variant (no `native_decide`, no `ofReduceBool` axiom)

Same statement as `PackingCert.trump11_ok`, proven with `decide` so that
the proof term is checked by the Lean kernel using only its built-in
GMP-accelerated `Nat` arithmetic.  This file is slower to build; if it becomes
infeasible for a certificate it can be dropped from the default target.
-/

namespace PackingCert

open Data

set_option maxRecDepth 100000 in
theorem trump11_ok_kernel : checkPacking trump11 = true := by decide

end PackingCert
