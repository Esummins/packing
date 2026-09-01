# A58 LOG

2026-09-01 (Fable lead)
* Read BRIEF + context: A21 notes (THM1/THM2 exact statements, corner0 LP history), A47
  theory + primitives report (corner/side tables, feasibility law, near-flush zero), A53
  lemmas (L1-L6, Trump blocked slide), A55 + k3_ext lemmas (E1-E5, ledger, K1), A50
  span_semigroup (theta*), A48/A51 registry rows, drain_lemma v3 (D1).
* Theory session: found the exchange (teleport) selection lemma CC-2/CC-2' — k-maximal
  minimizer selection makes every empty (or singly-non-simply-met) completable slot box a
  contradiction, subsuming A53 L6 and removing the corridor geometry from the selection side.
  CC-3: every kill certificate doubles as an all-packings occupancy theorem one slot down
  (s0 only). CC-4 persistence. CC-1 exact separation/clip census.
* code/a58_analysis.py (exact Fractions + float SAT canary): CC-1 census (12 offset-2 clips,
  only slot value in the A21 zone interval is 1/2, root boxes pairwise unreachable), the full
  occupancy matrix for open classes k <= 4 (clear-corner roots ALL land on OPEN supersets =>
  cert route void at roots, by K1 forever; 11 deeper rows land on EMPTY classes => new s0
  occupancy theorems), Trump canary: all 8 completable boxes of trump5 carry exactly 2
  open-interior meeters (TL root: eps-off +0.1555 + sq6 +0.1683; BL(0,2): eps-off + sq7
  +0.0160 = L4's corridor intruder).
* Checked the brief's "re-examine per-corner occupancy at s0" against Trump BEFORE spending
  the heavy process: Trump's TL corner ZONE contains no square centre — the centre-level
  per-corner statement is false at the only known near-optimal packing; LP run cancelled.
  0 heavy processes used.
* Opus verification subagent (independent re-implementation, own D4/canon/Young/SAT +
  polygon-clip): claims C1-C5, C7 PASS; C6 PASS on content (8 boxes, exact meeter sets,
  margins to 5e-5) with one correction — 7 of 8 boxes have a THIRD square in exact flush
  contact (margin 0 within 2e-15): the 2-counts are knife-edge, open-interior-only. Folded
  into theory.md Sec. 5 + G5 and the report.
* Wrote notes/theory.md (CC-1..CC-4, Theorem A58-1, quantifier resolution, gaps G1-G5),
  results/a58_report.md (T1/T2/T3 with certified numbers incl. the 0.9715 B0 grant-all
  screening), results/occupancy_matrix.json. Registry row appended.
