import PackingCertMathlib.Composition
import PackingCertMathlib.Ceil
import PackingCertMathlib.PinnedSlide
open PackingCert PackingCert.S11 PackingCert.S11.CrowdZ
-- T1: Lemma CW / B-YES / the two-file checks
#print axioms crowd_sound
#print axioms crowd_cert_kill
#print axioms scaleC_meets_cornerBox
#print axioms not_meets_two_corners
#print axioms meets_cornerBox_iff_muC_le
#print axioms sameMeasure_sound
#print axioms crowdZones_sound
#print axioms crowdKill_of_files
#print axioms crowd_sound_incidence
-- T2: Lemma SLIDE / K0-FREE
#print axioms shiftCfg_packing
#print axioms k0free_kill
#print axioms slide_crowd
-- T4: Theorem N
#print axioms slabKill_of_tree
#print axioms theoremN_slab
#print axioms chain_cover
#print axioms no_packing_of_chain
#print axioms s_eleven_ge_of_chain
#print axioms classKilledAt_below_of_chain
#print axioms classKilledAt_of_chain
-- T3: Theorem CEIL
#print axioms exists_sep_line
#print axioms wedge_x
#print axioms wedge_core
#print axioms ceil
#print axioms ceil_packing
-- T2 addendum (A94): SWEEP and the pinned joint translation
#print axioms sweep_core
#print axioms sweep_packing
#print axioms pinnedShift_packing
