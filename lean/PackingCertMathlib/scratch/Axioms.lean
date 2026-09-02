import PackingCertMathlib.Trump11
import PackingCertMathlib.Band
import PackingCertMathlib.TopLevel
import PackingCertMathlib.Dilation
import PackingCertMathlib.Skeleton
import PackingCertMathlib.CaseK506
import PackingCertMathlib.MeasurePyBridge
import PackingCertMathlib.ParamK506
import PackingCertMathlib.Selection
import PackingCertMathlib.Zones
import PackingCertMathlib.AliveDataTrump5K
import PackingCertMathlib.CensusCheck
import PackingCertMathlib.CensusSelection
import PackingCertMathlib.D4Wlog
import PackingCertMathlib.UniqueChain
#print axioms PackingCert.disjoint_of_strictlyBelow
#print axioms PackingCert.checkPackingCCW_sound
#print axioms PackingCert.aff_sqdist
#print axioms PackingCert.trump11_ccw_ok
#print axioms PackingCert.trump11_ccw_ok_kernel
#print axioms PackingCert.trump11_ok_of_ccw
#print axioms PackingCert.eleven_unit_squares_in_3877084
#print axioms PackingCert.two_unit_squares_side_ge
#print axioms PackingCert.atMostOne_of_side_lt
#print axioms PackingCert.band_96_25
#print axioms PackingCert.isUnitSquare_csqSet
#print axioms PackingCert.S11.isUnitSquare_exists_psq
#print axioms PackingCert.S11.parametrize
#print axioms PackingCert.S11.checkMeasureI_no_packing
#print axioms PackingCert.S11.check_3_82
#print axioms PackingCert.S11.s_eleven_ge_382
#print axioms PackingCert.S11.s_eleven_ge
#print axioms PackingCert.S11.s_eleven_eq
#print axioms PackingCert.S11.s_eleven_unique
#print axioms PackingCert.S11.attained
#print axioms PackingCert.S11.mem_interior_iff_uv
#print axioms PackingCert.S11.dilation_bridge
#print axioms PackingCert.S11.lemma_B
#print axioms PackingCert.S11.priced_dichotomy
#print axioms PackingCert.S11.hcert_of_priced
#print axioms PackingCert.S11.bprime_containment
#print axioms PackingCert.S11.containsPins_mono
#print axioms PackingCert.S11.monotone_to_exact
#print axioms PackingCert.S11.theta_lipschitz
#print axioms PackingCert.S11.sub_le_theta
#print axioms PackingCert.S11.corner_perturb
#print axioms PackingCert.S11.rBasin_gate_tilt
#print axioms PackingCert.S11.rBasin_gate_slab
#print axioms PackingCert.S11.sat_squares
#print axioms PackingCert.S11.coreExempt_sound
#print axioms PackingCert.S11.exemptB_sound
#print axioms PackingCert.S11.checkCaseI_price
#print axioms PackingCert.S11.priced_dichotomy_scaled
#print axioms PackingCert.S11.checkCaseI_no_family
#print axioms PackingCert.S11.checkCaseI_kill
#print axioms PackingCert.S11.check_k5_06_lo
#print axioms PackingCert.S11.k5_06_lo_kill
#print axioms PackingCert.S11.k5_06_lo_kill_packing
#print axioms PackingCert.S11.checkMeasurePy_no_packing
#print axioms PackingCert.S11.goPy_sound
#print axioms PackingCert.S11.checkParamI_price
#print axioms PackingCert.S11.checkParamI_kill
#print axioms PackingCert.S11.checkParamI_kill_packing
#print axioms PackingCert.S11.check_k5_06_param
#print axioms PackingCert.S11.k5_06_param_kill
#print axioms PackingCert.S11.k5_06_param_kill_packing
#print axioms PackingCert.S11.exists_kmax
#print axioms PackingCert.S11.teleport_packing
#print axioms PackingCert.S11.cc2_stuck
#print axioms PackingCert.S11.centre_separation
#print axioms PackingCert.S11.zone_assign_bijective
#print axioms PackingCert.S11.core_meet_same_square
#print axioms PackingCert.S11.M1_transfer
-- A78 T2 (CIDL-LEAN): the (c-idl) replay and the discharged identity
#print axioms PackingCert.Cidl.cidl_identity
#print axioms PackingCert.Cidl.cidl_octic_canonical
#print axioms PackingCert.Cidl.cidl_gate_e
#print axioms PackingCert.Cidl.cidl_gate_delta
#print axioms PackingCert.Cidl.octic_zero_of_generators
#print axioms PackingCert.S11.shatA22_eq_shat
#print axioms PackingCert.S11.trump_packs_at_shat
-- A78 T1/T4 (census definition, D4, selection interface, chain): all propext/choice/Quot.sound
#print axioms PackingCert.S11.skeleton_mem_census
#print axioms PackingCert.S11.exists_class_skeleton
#print axioms PackingCert.S11.containsPins_skeleton
#print axioms PackingCert.S11.skeleton_card_le
#print axioms PackingCert.S11.d4_packing
#print axioms PackingCert.S11.d4Apply_slotCentre
#print axioms PackingCert.S11.skeleton_d4
#print axioms PackingCert.S11.class_kill
#print axioms PackingCert.S11.trumpPins_isCensusTuple
#print axioms PackingCert.S11.card_lt_teleport
#print axioms PackingCert.S11.exists_kmax_skeleton
#print axioms PackingCert.S11.cc2_stuck_census
#print axioms PackingCert.S11.cc2_two_meeters_census
#print axioms PackingCert.S11.d4_cover_zone
#print axioms PackingCert.S11.d4_wlog
#print axioms PackingCert.S11.exists_stratum
#print axioms PackingCert.S11.stratify
#print axioms PackingCert.S11.unique_transfer
#print axioms PackingCert.S11.isCtrSym_d4Apply
#print axioms PackingCert.S11.unique_via_chain
#print axioms PackingCert.S11.s_eleven_unique_of_chain
-- A78 T1 census counts / A72 cross-check (native_decide each)
#print axioms PackingCert.S11.censusL_length
#print axioms PackingCert.S11.classCodes_length
#print axioms PackingCert.S11.census_eq_corpus
#print axioms PackingCert.S11.census_d4_closed
#print axioms PackingCert.S11.corpus_classes_canon
#print axioms PackingCert.S11.corpus_classes_distinct
#print axioms PackingCert.S11.trumpPins_eq_corpus
#print axioms PackingCert.S11.trumpClassIdx_lt
#print axioms PackingCert.S11.gsq_proj
#print axioms PackingCert.S11.gsq_disjoint_sep
#print axioms PackingCert.S11.gap_disjoint
#print axioms PackingCert.S11.admissible_sound
#print axioms PackingCert.S11.massIn_sum_disjoint_le
#print axioms PackingCert.S11.alive_sound_mono
#print axioms PackingCert.S11.alive_sound
#print axioms PackingCert.AliveData.check_trump5_alive
#print axioms PackingCert.S11.trump5_no_case_certificate
