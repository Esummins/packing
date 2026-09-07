import PackingCertMathlib.SatInterior

/-
A126 T2 — the axiom audit of `PackingCertMathlib/SatInterior.lean`.
Expected: the three standard Lean axioms (propext, Classical.choice, Quot.sound) only.
-/
#print axioms PackingCert.S11.LocalCert.wrel_comm
#print axioms PackingCert.S11.LocalCert.sat_selection_thm
#print axioms PackingCert.S11.LocalCert.cover_pair'
#check @PackingCert.S11.LocalCert.sat_selection_thm
