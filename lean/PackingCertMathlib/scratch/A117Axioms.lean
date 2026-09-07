import PackingCertMathlib.ParamNoFam

-- A117 T1: the NO-family exemption clause of the parametric checker.
-- Expect the three standard Lean axioms only (propext, Classical.choice, Quot.sound):
-- no project axiom is introduced by A117.
#print axioms PackingCert.S11.affine_le_max
#print axioms PackingCert.S11.min_le_affine
#print axioms PackingCert.S11.exemptPN_nil
#print axioms PackingCert.S11.nofamExemptIV_sound

-- A117 T2: Lemma TC is STATED, not assumed -- these are `Prop` definitions, so they are
-- not theorems and carry no axioms; `#check` records the frozen statements.
#check @PackingCert.S11.TCSupportMin
#check @PackingCert.S11.TCCentreDist
#check @PackingCert.S11.TCLeaf
#check @PackingCert.S11.TCLeaf_of_TCCentreDist
