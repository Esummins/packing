# A163 — the 53 A160 box sets, re-framed and re-run

`CERTIFIED` = A116's selection tree closed every leaf inside the cap AND the sampling
survivor rule (drawn → tested → hits) found 0 hits.  `WALL_CAP` = cap reached with
unresolved cells and NO witness (a compute limit).  `WITNESS` = a LIVE-LOW leaf, i.e. a
real partial packing of `L ∪ P` at side ≤ s₀ (a geometry limit).  `tcert` = an exact
t = tan(θ/2) certificate emitted by A133's `gen_local_t.py` and verified by A133's
independent `check_local_t.py` (sha256 in `results/tcerts163.json`).

| # | A160 object | family | k5_11 (A160) | k5_16 | min | s | trump5 | min | s | tcert |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | `chain_BOTH_base_r0.20_h1.25_nof0_+00.00` | chain | CERT 3.8774874 | CERTIFIED | 3.8770971 | 4 | CERTIFIED | 3.8776056 | 9 | k5_16 VALID, trump5 VALID |
| 1 | `chain_BOTH_base_r0.20_h1.25_nof0_+02.50` | chain | CERT 3.8770868 | CERTIFIED | 3.8771693 | 3 | CERTIFIED | 3.8771693 | 6 | k5_16 VALID, trump5 VALID |
| 2 | `chain_BOTH_base_r0.20_h1.25_nof0_-02.50` | chain | CERT 3.8770846 | CERTIFIED | 3.8805499 | 1 | CERTIFIED | 3.8772445 | 12 | k5_16 VALID, trump5 VALID |
| 3 | `chain_BOTH_base_r0.20_h1.25_nof0_+05.00` | chain | CERT 3.8771911 | CERTIFIED | 3.8783358 | 5 | CERTIFIED | 3.8783008 | 4 | k5_16 VALID, trump5 VALID |
| 4 | `chain_BOTH_base_r0.20_h1.25_nof0_-05.00` | chain | CERT 3.8770847 | CERTIFIED | 3.8816435 | 1 | CERTIFIED | 3.8771117 | 11 | k5_16 VALID, trump5 VALID |
| 5 | `chain_BOTH_base_r0.20_h1.25_nof0_+07.50` | chain | CERT 3.8773598 | CERTIFIED | 3.8798609 | 3 | CERTIFIED | 3.8798609 | 3 | k5_16 VALID, trump5 VALID |
| 6 | `chain_BOTH_base_r0.20_h1.25_nof0_-07.50` | chain | CERT 3.8771366 | CERTIFIED | 3.8770855 | 6 | CERTIFIED | 3.8770855 | 23 | k5_16 VALID, trump5 VALID |
| 7 | `chain_BOTH_base_r0.20_h1.25_nof0_+10.00` | chain | CERT 3.8773155 | CERTIFIED | 3.8811372 | 1 | CERTIFIED | 3.8811372 | 1 | k5_16 VALID, trump5 VALID |
| 8 | `chain_BOTH_base_r0.20_h1.25_nof0_-10.00` | chain | CERT 3.8771010 | CERTIFIED | 3.8771010 | 6 | CERTIFIED | 3.8771007 | 24 | k5_16 VALID, trump5 VALID |
| 9 | `chain_BOTH_base_r0.20_h1.25_nof0_+12.50` | chain | CERT 3.8770860 | CERTIFIED | 3.8813411 | 1 | CERTIFIED | 3.8813411 | 1 | k5_16 VALID, trump5 VALID |
| 10 | `chain_BOTH_base_r0.20_h1.25_nof0_-12.50` | chain | CERT 3.8777790 | CERTIFIED | 3.8772896 | 4 | CERTIFIED | 3.8771843 | 12 | k5_16 VALID, trump5 VALID |
| 11 | `chain_BOTH_base_r0.20_h1.25_nof0_-15.00` | chain | CERT 3.8787789 | CERTIFIED | 3.8788385 | 2 | CERTIFIED | 3.8775559 | 6 | k5_16 VALID, trump5 VALID |
| 12 | `chain_BOTH_base_r0.20_h1.25_nof0_-17.50` | chain | CERT 3.8798880 | CERTIFIED | 3.8798880 | 1 | CERTIFIED | 3.8798880 | 3 | k5_16 VALID, trump5 VALID |
| 13 | `chain_BOTH_base_r0.20_h1.25_nof0_-20.00` | chain | CERT 3.8866144 | CERTIFIED | 3.8866769 | 1 | CERTIFIED | 3.8866769 | 2 | k5_16 VALID, trump5 VALID |
| 14 | `chain_BOTH_base_r0.20_h1.25_nof0_-22.50` | chain | CERT 3.8826381 | CERTIFIED | 3.8830396 | 1 | CERTIFIED | 3.8770962 | 28 | k5_16 VALID, trump5 VALID |
| 15 | `chain_BOTH_base_r0.20_h1.25_nof0_-25.00` | chain | CERT 3.8908897 | CERTIFIED | 3.8913181 | 1 | CERTIFIED | 3.8788267 | 7 | k5_16 VALID, trump5 VALID |
| 16 | `chain_BOTH_base_r0.20_h1.25_nof0_-27.50` | chain | CERT 3.8838321 | CERTIFIED | 3.8838321 | 1 | CERTIFIED | 3.8782212 | 3 | k5_16 VALID, trump5 VALID |
| 17 | `chain_BOTH_base_r0.20_h1.25_nof0_-30.00` | chain | CERT 3.8801246 | CERTIFIED | 3.8810037 | 1 | CERTIFIED | 3.8810037 | 3 | k5_16 VALID, trump5 VALID |
| 18 | `chain_BOTH_base_r0.20_h1.25_nof0_-32.50` | chain | CERT 3.8818730 | CERTIFIED | 3.8891191 | 2 | CERTIFIED | 3.8818730 | 5 | k5_16 VALID, trump5 VALID |
| 19 | `chain_BOTH_base_r0.20_h1.25_nof0_-35.00` | chain | CERT 3.8927509 | CERTIFIED | - | 2 | CERTIFIED | 3.8806755 | 6 | k5_16 VALID, trump5 VALID |
| 20 | `chain_BOTH_base_r0.20_h1.25_nof0_-37.50` | chain | CERT 3.8887384 | CERTIFIED | 3.8887384 | 2 | CERTIFIED | 3.8771012 | 30 | k5_16 VALID, trump5 VALID |
| 21 | `chain_BOTH_base_r0.20_h1.25_nof0_-40.00` | chain | CERT 3.8797880 | CERTIFIED | 3.8781406 | 4 | WITNESS | - | 0 | k5_16 VALID |
| 22 | `chain_BOTH_base_r0.20_h1.25_nof0_-42.50` | chain | CERT 3.8869221 | CERTIFIED | 3.8893471 | 4 | WITNESS | - | 0 | k5_16 VALID |
| 23 | `chain_BOTH_base_r0.20_h1.25_nof0_-45.00` | chain | CERT 3.8841088 | CERTIFIED | 3.8841088 | 6 | WITNESS | 3.8924754 | 0 | k5_16 VALID |
| 24 | `chain_BOTH_base_r0.20_h10.00_nof0_+00.00` | chain | CERT 3.8770841 | CERTIFIED | 3.8770903 | 89 | WALL_CAP | 3.8770862 | 240 | k5_16 VALID |
| 25 | `chain_BOTH_base_r0.20_h10.00_nof0_+20.00` | chain | CERT 3.8770857 | CERTIFIED | 3.8771344 | 20 | CERTIFIED | 3.8771344 | 20 | k5_16 VALID, trump5 VALID |
| 26 | `chain_BOTH_base_r0.20_h10.00_nof0_-20.00` | chain | CERT 3.8770893 | CERTIFIED | 3.8770893 | 71 | WALL_CAP | 3.8770848 | 240 | k5_16 VALID |
| 27 | `chain_BOTH_base_r0.20_h10.00_nof0_-40.00` | chain | CERT 3.8770874 | WALL_CAP | 3.8771058 | 240 | WITNESS | 3.8775985 | 7 |  |
| 28 | `chain_RXY_probe_+00.00` | chain | CERT 3.8770881 | CERTIFIED | 3.8770958 | 11 | CERTIFIED | 3.8771161 | 12 | k5_16 VALID, trump5 VALID |
| 29 | `chain_RXY_probe_-10.00` | chain | CERT 3.8772110 | CERTIFIED | 3.8772874 | 10 | WITNESS | 3.8803748 | 0 | k5_16 VALID |
| 30 | `chain_RXY_probe_-10.00` | chain | CERT 3.8771062 | CERTIFIED | 3.8771056 | 26 | WITNESS | 3.8770911 | 3 | k5_16 VALID |
| 31 | `slice_a151B_f2-20.0_f3+00.0` | slice | CERT 3.8770907 | CERTIFIED | 3.8770863 | 127 | WITNESS | 3.8770891 | 8 | k5_16 VALID |
| 32 | `slice_a151B_f2+00.0_f3+20.0` | slice | CERT 3.8770846 | CERTIFIED | 3.8770846 | 160 | CERTIFIED | 3.8771342 | 217 | k5_16 VALID, trump5 VALID |
| 33 | `slice_a151B_f2+00.0_f3-20.0` | slice | CERT 3.8770858 | CERTIFIED | 3.8770911 | 125 | WITNESS | 3.8770846 | 5 | k5_16 VALID |
| 34 | `slice_a151B_f2+00.0_f3+40.0` | slice | CERT 3.8770972 | WALL_CAP | 3.8770935 | 240 | WALL_CAP | 3.8770974 | 240 |  |
| 35 | `slice_f1base_f2+20.0_f3+00.0` | slice | CERT 3.8770918 | CERTIFIED | 3.8772198 | 24 | CERTIFIED | 3.8770914 | 54 | k5_16 VALID, trump5 VALID |
| 36 | `slice_f1base_f2-20.0_f3+00.0` | slice | CERT 3.8770885 | CERTIFIED | 3.8771852 | 18 | CERTIFIED | 3.8771196 | 52 | k5_16 VALID, trump5 VALID |
| 37 | `slice_f1base_f2+00.0_f3+20.0` | slice | CERT 3.8771882 | CERTIFIED | 3.8772523 | 11 | CERTIFIED | 3.8773169 | 28 | k5_16 VALID, trump5 VALID |
| 38 | `slice_f1base_f2+00.0_f3-20.0` | slice | CERT 3.8770860 | CERTIFIED | 3.8772178 | 23 | CERTIFIED | 3.8771140 | 73 | k5_16 VALID, trump5 VALID |
| 39 | `slice_f1base_f2+40.0_f3+00.0` | slice | CERT 3.8770970 | CERTIFIED | 3.8770970 | 22 | CERTIFIED | 3.8771676 | 45 | k5_16 VALID, trump5 VALID |
| 40 | `slice_f1base_f2-40.0_f3+00.0` | slice | CERT 3.8770970 | CERTIFIED | 3.8771126 | 14 | CERTIFIED | 3.8771676 | 40 | k5_16 VALID, trump5 VALID |
| 41 | `slice_f1base_f2+00.0_f3+40.0` | slice | CERT 3.8770919 | CERTIFIED | 3.8772951 | 14 | CERTIFIED | 3.8772710 | 36 | k5_16 VALID, trump5 VALID |
| 42 | `slice_f1base_f2+00.0_f3-40.0` | slice | CERT 3.8770888 | CERTIFIED | 3.8772951 | 15 | CERTIFIED | 3.8772920 | 36 | k5_16 VALID, trump5 VALID |
| 43 | `slice_f1base_f2+20.0_f3+20.0` | slice | CERT 3.8770973 | CERTIFIED | 3.8773196 | 14 | CERTIFIED | 3.8773196 | 35 | k5_16 VALID, trump5 VALID |
| 44 | `slice_f1base_f2+20.0_f3-20.0` | slice | CERT 3.8772292 | CERTIFIED | 3.8773310 | 8 | CERTIFIED | 3.8771848 | 18 | k5_16 VALID, trump5 VALID |
| 45 | `slice_f1base_f2-20.0_f3+20.0` | slice | CERT 3.8775910 | CERTIFIED | 3.8781729 | 2 | CERTIFIED | 3.8781729 | 6 | k5_16 VALID, trump5 VALID |
| 46 | `slice_f1base_f2-20.0_f3-20.0` | slice | CERT 3.8770868 | CERTIFIED | 3.8770900 | 35 | CERTIFIED | 3.8770900 | 177 | k5_16 VALID, trump5 VALID |
| 47 | `slice_f1base_f2+20.0_f3+40.0` | slice | CERT 3.8771187 | CERTIFIED | 3.8771481 | 15 | CERTIFIED | 3.8771069 | 38 | k5_16 VALID, trump5 VALID |
| 48 | `slice_f1base_f2+20.0_f3-40.0` | slice | CERT 3.8771693 | CERTIFIED | 3.8771736 | 21 | CERTIFIED | 3.8777795 | 51 | k5_16 VALID, trump5 VALID |
| 49 | `slice_f1base_f2-20.0_f3+40.0` | slice | CERT 3.8771052 | CERTIFIED | 3.8772531 | 7 | CERTIFIED | 3.8772531 | 19 | k5_16 VALID, trump5 VALID |
| 50 | `slice_f1base_f2-20.0_f3-40.0` | slice | CERT 3.8772930 | CERTIFIED | 3.8771043 | 13 | CERTIFIED | 3.8771411 | 46 | k5_16 VALID, trump5 VALID |
| 51 | `slice_f1base_f2+40.0_f3-20.0` | slice | CERT 3.8770895 | CERTIFIED | 3.8771260 | 24 | CERTIFIED | 3.8771449 | 84 | k5_16 VALID, trump5 VALID |
| 52 | `slice_f1base_f2-40.0_f3-20.0` | slice | CERT 3.8770945 | CERTIFIED | 3.8771667 | 21 | CERTIFIED | 3.8771294 | 101 | k5_16 VALID, trump5 VALID |
| 53 | `S02_k5_11_A151B` | other | CERT 3.8770845 | CERTIFIED | 3.8770840 | 203 | WITNESS | 3.8771273 | 7 | k5_16 VALID |

* **k5_16**: 54 of 54 box sets run, **52 CERTIFIED**, 2 wall cap, 0 witness, 0 other; 1688 s of tree (0.47 CPU-h).
* **trump5**: 54 of 54 box sets run, **42 CERTIFIED**, 3 wall cap, 9 witness, 0 other; 2136 s of tree (0.59 CPU-h).
