# Coordinator addendum (2026-09-10 02:20): certificates with NO guard-line term replayed under the FROZEN v1 verifier

After the external review's P0/P1 fixes to verify_case_v5 (f590c4db, 12f8b9c6), every A190 certificate was
replayed under the fixed v5 (scratchpad/replay_v5.log; all guard-line kills PASS). Certificates whose measure has
zero guard-line density are plain v1-format certificates and belong to the FROZEN chain if they pass
attempts/A57-shadow-trees/code/verify_case.py (sha 521cb01f...):

- k5_16_interior_Y0027: FROZEN v1 PASS at depth 64 and 72 (total 927/200 < 5). v5 at depth 40 had left it
  undecided (8 witness boxes, 0 holes) -- depth-limited, not core-limited (the A170 lesson). RELABEL: [C] under
  the frozen v1, not "v5 only".
- k5_11_interior_Y0241 frozen-v1 depth 64: PASS
- k5_11_interior_Y0249 frozen-v1 depth 64: PASS
- k5_16_interior_Y0230 frozen-v1 depth 64: PASS
