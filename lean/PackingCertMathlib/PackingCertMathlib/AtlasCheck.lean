import PackingCertMathlib.AtlasData

/-!
# The atlas-value replays (A86 wave 7) — ISOLATED `native_decide` module

Kept in its own module (the `Measure382Check` / `RigidityCheck` pattern) so that the
evaluation axiom enters exactly here and every other module is cache-hit-only.

`checkAtlas_all` replays the 48 (D′) atlas discharge boxes of `atlasAll`:
A37's 37 critical-point boxes (minus family 0 = Trump, whose side ŝ < s0) re-emitted at
the radius that still certifies `L ≥ s0`, plus A85's 12 k0 ghost drains
(`docs/proofs/k0_route.md` §4.6).  Each box carries its own recomputed extent bound
`L ≥ s0 = 969271/250000`; `checkAtlas` verifies the 11 boxes are well formed and that
some witness corner pair certifies `L` by exact rational interval arithmetic.
-/

namespace PackingCert.Atlas

open PackingCert.Atlas.Data

theorem checkAtlas_all : atlasAll.all checkAtlas = true := by native_decide

/-- Every discharge box's bound really is at or above `s0` (a pure `decide`, no kernel
evaluation of the interval arithmetic). -/
theorem atlasAll_L_ge_s0 :
    atlasAll.all (fun a => decide ((969271 : Rat) / 250000 ≤ a.L)) = true := by native_decide

end PackingCert.Atlas
