import PackingCertMathlib.Local

/-
A119 T2 — the axiom audit of `PackingCertMathlib/Local.lean`.

Expected: the three standard Lean axioms (`propext`, `Classical.choice`, `Quot.sound`) on every
RELAX / COVER / LEAF theorem, and exactly ONE project axiom in the file —
`LocalCert.sat_selection` (Lemma SAT for interiors) — reaching only `cover_pair`.
`classKilledAt_of_localDead` additionally inherits the ambient `native_decide` axiom of `shat`
(`Rigid.checkA22_a22`), which is A22's, not A119's.
-/

-- Lemma RELAX (§3.1): all THEOREMS, standard axioms only.
#print axioms PackingCert.S11.LocalCert.axis_decomp
#print axioms PackingCert.S11.LocalCert.mccormick_hi
#print axioms PackingCert.S11.LocalCert.mccormick_lo
#print axioms PackingCert.S11.LocalCert.abs_chord
#print axioms PackingCert.S11.LocalCert.chord_of_concave
#print axioms PackingCert.S11.LocalCert.abs_sin_le_sin
#print axioms PackingCert.S11.LocalCert.cos_ge_of_abs_le

-- Lemma COVER: all THEOREMS.
#print axioms PackingCert.S11.LocalCert.cover_bisect
#print axioms PackingCert.S11.LocalCert.cover_qsplit
#print axioms PackingCert.S11.LocalCert.cover_selection
#print axioms PackingCert.S11.LocalCert.cover_pair
#print axioms PackingCert.S11.LocalCert.localDead_of_contradiction

-- Lemma LEAF: the generated leaves of a real certificate, closed by `linarith`.
#print axioms PackingCert.S11.LocalCert.leaf_S02_k5_11_r0_10_rho10_0
#print axioms PackingCert.S11.LocalCert.leaf_S02_k5_11_r0_10_rho10_1
#print axioms PackingCert.S11.LocalCert.leaf_S02_k5_11_r0_10_rho10_2

-- The composition (these DO use the two project axioms of the file, as stated).
#print axioms PackingCert.S11.LocalCert.classKilledAt_of_localDead
#print axioms PackingCert.S11.LocalCert.localKill_yes

-- The two project axioms, with their exact statements.
#check @PackingCert.S11.LocalCert.sat_selection


-- The frozen statements of the objects.
#check @PackingCert.S11.LocalCert.LocalHyp
#check @PackingCert.S11.LocalCert.LocalDead
#check @PackingCert.S11.LocalCert.gsel
