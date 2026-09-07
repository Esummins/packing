import PackingCertMathlib.LocalCertS07

/-
A126 T2 — the axiom audit of `PackingCertMathlib/SatInterior.lean`.
Expected: the three standard Lean axioms (propext, Classical.choice, Quot.sound) only.
-/
#print axioms PackingCert.S11.LocalCert.wrel_comm
#print axioms PackingCert.S11.LocalCert.sat_selection_thm
#print axioms PackingCert.S11.LocalCert.cover_pair'
#check @PackingCert.S11.LocalCert.sat_selection_thm

-- A126 T1 — the reflected leaf checker and the S07 (0.1, 40 deg) replay.
#print axioms PackingCert.S11.LocalCert.minL_le
#print axioms PackingCert.S11.LocalCert.accum_le
#print axioms PackingCert.S11.LocalCert.checkLeaf_sound
#print axioms PackingCert.S11.LocalCert.localDead_of_cert
#print axioms PackingCert.S11.LocalCert.check_s07
#print axioms PackingCert.S11.LocalCert.localDead_s07
#print axioms PackingCert.S11.LocalCert.localDead_s07_shat
#check @PackingCert.S11.LocalCert.localDead_s07
#check @PackingCert.S11.LocalCert.CertCover
