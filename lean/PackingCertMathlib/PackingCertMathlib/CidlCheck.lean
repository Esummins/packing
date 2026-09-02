import PackingCertMathlib.CidlGen
import PackingCertMathlib.CidlData

/-!
# The `native_decide` replay of the (c-idl) certificate (A78 T2, CIDL-LEAN)

Isolated in its own module (the `Measure382Check.lean` pattern) so that the kernel-free
evaluation is cached independently of the Mathlib-side composition in `CidlBridge.lean`.
Nothing but `CidlBridge` should import this file.

The four checks mirror `certs/verify_cidl.py` exactly:

* `cidl_octic_canonical` — [O]: the certificate's octic IS the canonical Trump octic;
* `cidl_identity` — [I]: `Σ_j q_j·G_j − e·Δ⁸·octic(S) = 0` in `ℚ[t,y4,x6..y10,S]`,
  with the 13 generators `G_j` REBUILT in `CidlGen.lean` from the A22 corner/edge
  conventions (the certificate cannot alter them);
* `cidl_gate_e`, `cidl_gate_delta` — [G]: `e` and `Δ` are strictly negative on
  `[3/10, 2/5] ∋ t̂`.  `verify_cidl.py` uses Sturm chains; the crude monomial interval
  bound `ubound` already separates both from `0` (`e ≤ −1.83…`, `Δ ≤ −3.45…`), which is
  strictly stronger than "no root" and much cheaper to certify in Lean.
-/

namespace PackingCert
namespace Cidl

/-- The left-hand side of the identity: `Σ_j q_j · G_j`, as a raw term list. -/
def lhsPoly : Poly := (List.zipWith pmulRaw Data.cofs gens).flatten

/-- The right-hand side of the identity: `e(t) · Δ(t)⁸ · octic(S)`. -/
def rhsPoly : Poly :=
  pmul (pmul (tUniToPoly Data.eC) (ppow (tUniToPoly Data.deltaC) 8)) (sUniToPoly OCTIC)

/-- **[O]** The certificate's octic is the canonical Trump octic. -/
theorem cidl_octic_canonical : Data.certOctic = OCTIC := by decide

/-- **[I]** The saturated ideal-membership identity, exactly over `ℚ`. -/
theorem cidl_identity : isZero (padd lhsPoly (pneg rhsPoly)) = true := by native_decide

/-- **[G]** `e(t) < 0` on `[3/10, 2/5]` (monomial interval bound). -/
theorem cidl_gate_e : gateNeg Data.eC gateA gateB = true := by native_decide

/-- **[G]** `Δ(t) < 0` on `[3/10, 2/5]` (monomial interval bound). -/
theorem cidl_gate_delta : gateNeg Data.deltaC gateA gateB = true := by native_decide

end Cidl
end PackingCert
