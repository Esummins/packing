import PackingCertMathlib.CrowdZone
open PackingCert PackingCert.S11 PackingCert.S11.CrowdZ PackingCert.CaseI PackingCert.MeasureI

-- s0 = 969271/250000, a_w = 0.92402 : a zone in the middle of the container misses every corner box
example : crowdZones 969271 250000 (46201/50000) 8
    [⟨(3/2 : Rat), 2, (3/2 : Rat), 2, [((0 : Rat), 1)]⟩] = true := by native_decide
-- a zone whose square sits at the BL corner slot must NOT pass
example : crowdZones 969271 250000 (46201/50000) 8
    [⟨(1/2 : Rat), 1, (1/2 : Rat), 1, [((0 : Rat), 1/10)]⟩] = false := by native_decide
-- a horizontal band just above the corner boxes: centre y in [1.7, 2.2], any x, tilts up to 90 deg
-- (a unit square with centre height ≥ 1.7 has lowest point ≥ 1.7 - 0.7072 > 0.924)
example : crowdZones 969271 250000 (46201/50000) 10
    [⟨(45/100 : Rat), 969271/250000 - 45/100, (17/10 : Rat), 22/10, [((0 : Rat), 1)]⟩] = true := by native_decide
-- a right-hand band next to the BR/TR boxes: centres x in [2.0, 2.2] cannot reach x >= 2.953
example : crowdZones 969271 250000 (46201/50000) 10
    [⟨(2 : Rat), 22/10, (45/100 : Rat), 969271/250000 - 45/100, [((0 : Rat), 1)]⟩] = true := by native_decide

-- the emitted side-condition script of gen_crowd_lean.py, with the Bool facts as hypotheses
example (cA cB : CCertI) (hA : checkCaseI cA = true) (hAc : cA.cores = []) (hAf : cA.nofams = [])
    (hn : cA.n = 15) (hB : checkCaseI cB = true) (hBc : cB.cores = [])
    (hsA : caseSide cA = (969271 : ℝ) / 250000) (hsB : caseSide cB = (969271 : ℝ) / 250000)
    (hsm : sameMeasure cA cB 1 2 = true)
    (hz : crowdZones cB.sNum cB.sDen ((46201 : Rat) / 50000) 10 cB.nofams = true) :
    CrowdKill ((1 : ℝ) / 10) ((191 : ℝ) / 50) ((969271 : ℝ) / 250000) := by
  rw [← hsA]
  refine crowdKill_of_files (eNum := 1) (eDen := 2) (by norm_num)
    hA hAc hAf ?_ hB hBc (by rw [hsA, hsB]) hsm hz (by norm_num) (by norm_num) ?_ ?_ ?_
  · rw [hn]
    norm_num
  · rw [hsA]
    push_cast
    norm_num
  · rw [hsA]
    push_cast
    norm_num
  · rw [hsA]
    push_cast
    norm_num
-- sameMeasure: weights in ratio 1 + e with e = 1/2 (wd_B = 3 wd_A / 2 pattern: w_B*wd_A*(2+1) = w_A*wd_B*2)
example : sameMeasure
    { n := 15, sNum := 969271, sDen := 250000, wd := 2, depth := 4,
      atoms := [⟨1, 1, 2, 3⟩, ⟨3, 1, 2, 1⟩], cores := [], nofams := [] }
    { n := 1000, sNum := 969271, sDen := 250000, wd := 3, depth := 4,
      atoms := [⟨1, 1, 2, 3⟩, ⟨3, 1, 2, 1⟩], cores := [], nofams := [] } 1 2 = true := by decide
example : sameMeasure
    { n := 15, sNum := 969271, sDen := 250000, wd := 2, depth := 4,
      atoms := [⟨1, 1, 2, 3⟩, ⟨3, 1, 2, 1⟩], cores := [], nofams := [] }
    { n := 1000, sNum := 969271, sDen := 250000, wd := 3, depth := 4,
      atoms := [⟨1, 1, 2, 3⟩, ⟨3, 1, 2, 2⟩], cores := [], nofams := [] } 1 2 = false := by decide
