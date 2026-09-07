import PackingCertMathlib.LocalCertS02
import PackingCertMathlib.LocalCompose
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

-- A126 T3 — the YES/NO composition.
#print axioms PackingCert.S11.LocalCert.yes_or_no
#print axioms PackingCert.S11.LocalCert.localHyp_of_yes
#print axioms PackingCert.S11.LocalCert.node_dead_of_yes_no
#print axioms PackingCert.S11.LocalCert.classKilledAt_of_yes_no
#print axioms PackingCert.S11.LocalCert.centre_in_slab
#print axioms PackingCert.S11.LocalCert.noneIn_of_clamped
#print axioms PackingCert.S11.LocalCert.y0230_dead
#check @PackingCert.S11.LocalCert.node_dead_of_yes_no

-- A126 T1 — the second neighbourhood, S02 (0.2, 10 deg): the N of A120's node cover.
#print axioms PackingCert.S11.LocalCert.check_s02
#print axioms PackingCert.S11.LocalCert.localDead_s02
#check @PackingCert.S11.LocalCert.localDead_s02
