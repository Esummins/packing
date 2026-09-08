import PackingCertMathlib.LocalCertS07T
import PackingCertMathlib.LocalCertS02T

/-!
# A139 (R4) — the axiom roster of the replayed local certificates

    python attempts/A78-lean-wave6/code/lakeb.py --env scratch/A139Axioms.lean

`certCover_of_check` and everything under it is `[propext, Classical.choice, Quot.sound]`
(A138's audit).  What (R4) adds is DATA plus two `native_decide` replays per certificate, so the
headline theorems here carry the replays' own axioms and, through `lb_382`, `check_3_82`'s —
exactly where A126 and A138 said they would appear.  No `sorry`, and the project axiom
`Local.sat_selection` appears nowhere (`SatInterior.sat_selection_thm` proves it).
-/

open PackingCert.S11.LocalCertT3.S07T
open PackingCert.S11.LocalCertT3.S02T

#print axioms certOk_s07
#print axioms certCover_s07
#print axioms checkLeaf_s07
#print axioms localDead_s07_t

#print axioms certOk_s02
#print axioms certCover_s02
#print axioms checkLeaf_s02
#print axioms localDead_s02_t
