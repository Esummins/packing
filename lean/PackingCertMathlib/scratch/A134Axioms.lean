import PackingCertMathlib.LocalCertT2

open PackingCert.S11.LocalCertT2

-- §1 subdivided positivity
#print axioms peval_padZ
#print axioms posChain_sound
-- §2 the bivariate positivity certificate
#print axioms peval2_pmul2
#print axioms posAuxP_nonneg
#print axioms posCheck2_sound
#print axioms posColumn_sound
#print axioms posGrid_sound
-- §3 the degenerate side
#print axioms peval_substY0
#print axioms peval_substX0
-- §4 the envelope polynomials
#print axioms peval_hPoly
#print axioms wT_ge_aff
#print axioms sRel_mul
#print axioms sRel_le_aff
#print axioms sRel_ge_aff
#print axioms peval2_wPolyT
#print axioms wNum_eq
#print axioms wrel_ge_plane
-- §5 rational intervals
#print axioms IQ.mul_mem
#print axioms cosI_mem
#print axioms sinI_mem
#print axioms axI_mem
#print axioms wLoQ_le
-- §6 (C2) the selection cover
#print axioms gsel_le_gapHi
#print axioms selection_cover
#print axioms selectionOk_sound
-- §7 (C3) Lemma RELAX
#print axioms relax_wall
#print axioms axis_decomp_t
#print axioms cosRel_le_one
#print axioms one_sub_cosRel_le
#print axioms corr_bound
#print axioms absQ_chord
#print axioms relax_U_A
#print axioms relax_U_B1
#print axioms relax_U_B2
#print axioms relax_selection
-- §8 (C4) the variable map
#print axioms localHyp_bodies
