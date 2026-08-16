import PackingCert.Checker
import PackingCert.Data
import PackingCert.DataTight

/-!
# Kernel-only variants (no `native_decide`, no extra axioms)

Same statements as in `Main.lean`, proven with `decide`, so the proof is
checked by the Lean kernel using only its built-in GMP-accelerated `Nat`
arithmetic.  `#print axioms` reports no axioms for these.
-/

namespace PackingCert

open Data

theorem trump11_ok_kernel : checkPacking trump11 = true := by decide
theorem trump11_tight_ok_kernel : checkPacking trump11_tight = true := by decide

end PackingCert
