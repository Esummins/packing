# A241 -- the ROW cascade: one-slot extensions and their window status

`FULL-WINDOW` = the extension class carries a scoreboard row `FULL [191/50, 969271/250000]`, so Lemma SLOT-CROWD
applies at that cell and Theorem FC gives the class a forced cell.  `s0 only` = A55 killed the class
exactly, but at s0 -- and `closed_disjoint_bridge.md` B.2 makes that worth NOTHING on the window
(corpus margin rho ~ 1.0e-9, A = 5/2, so (H') reads s''/m - 1 < 4.0e-10: no side of [3.82, s-hat]
is reached).  Turning those into window rows is A241's campaign (`code/param241.py`).

| class | own row | forced cells | USABLE | extension -> status |
|---|---|---|---|---|
| `trump5` | -- | 6 | **6** | BL(0,2)→k6_07 [FULL-WINDOW], BL(1,1)→k6_19 [FULL-WINDOW], BR(0,1)→k6_21 [FULL-WINDOW], TR(0,1)→k6_22 [FULL-WINDOW], TR(1,0)→k6_24 [FULL-WINDOW], TL(0,0)→k6_23 [FULL-WINDOW] |
| `k4_03` | -- | 5 | **3** | BL(1,1)→k5_09 [FULL-WINDOW], BL(2,0)→k5_02 [FULL-WINDOW], BR(0,0)→k5_11 [OPEN], TR(0,0)→trump5 [OPEN], TL(1,0)→k5_10 [FULL-WINDOW] |
| `k4_05` | -- | 5 | **3** | BL(1,0)→k5_11 [OPEN], BR(0,1)→k5_15 [FULL-WINDOW], BR(1,0)→k5_13 [FULL-WINDOW], TR(0,0)→k5_16 [OPEN], TL(1,0)→k5_12 [FULL-WINDOW] |
| `k4_06` | -- | 5 | **3** | BL(1,0)→trump5 [OPEN], BR(0,0)→k5_16 [OPEN], TR(0,1)→k5_17 [FULL-WINDOW], TR(1,0)→k5_14 [FULL-WINDOW], TL(1,0)→k5_13 [FULL-WINDOW] |
| `k4_08` | -- | 7 | **5** | BL(0,2)→k5_03 [FULL-WINDOW], BL(1,1)→k5_18 [FULL-WINDOW], BL(2,0)→k5_03 [FULL-WINDOW], BR(0,0)→trump5 [OPEN], TR(0,1)→k5_19 [FULL-WINDOW], TR(1,0)→k5_19 [FULL-WINDOW], TL(0,0)→trump5 [OPEN] |
| `k4_11` | -- | 7 | **5** | BL(0,2)→k5_07 [FULL-WINDOW], BL(1,0)→trump5 [OPEN], BR(0,1)→k5_15 [FULL-WINDOW], BR(1,0)→k5_12 [FULL-WINDOW], TR(0,1)→k5_17 [FULL-WINDOW], TR(1,0)→k5_20 [FULL-WINDOW], TL(0,0)→k5_16 [OPEN] |
| `corners4` | -- | 8 | **0** | BL(0,1)→k5_16 [OPEN], BL(1,0)→k5_16 [OPEN], BR(0,1)→k5_16 [OPEN], BR(1,0)→k5_16 [OPEN], TR(0,1)→k5_16 [OPEN], TR(1,0)→k5_16 [OPEN], TL(0,1)→k5_16 [OPEN], TL(1,0)→k5_16 [OPEN] |
| `k3_01` | -- | 4 | **0** | BL(1,0)→k4_03 [OPEN], BR(0,0)→k4_05 [OPEN], TR(0,0)→k4_06 [OPEN], TL(1,0)→k4_04 [s0 only] |
| `k3_02` | -- | 6 | **0** | BL(0,2)→k4_00 [s0 only], BL(1,1)→k4_07 [s0 only], BL(2,0)→k4_00 [s0 only], BR(0,0)→k4_03 [OPEN], TR(0,0)→k4_08 [OPEN], TL(0,0)→k4_03 [OPEN] |
| `k3_03` | -- | 6 | **0** | BL(0,2)→k4_01 [s0 only], BL(1,0)→k4_03 [OPEN], BR(0,1)→k4_10 [s0 only], BR(1,0)→k4_04 [s0 only], TR(0,0)→k4_11 [OPEN], TL(0,0)→k4_05 [OPEN] |
| `k3_04` | -- | 6 | **0** | BL(0,2)→k4_02 [s0 only], BL(1,0)→k4_08 [OPEN], BR(0,0)→k4_11 [OPEN], TR(0,1)→k4_12 [s0 only], TR(1,0)→k4_09 [s0 only], TL(0,0)→k4_06 [OPEN] |
| `k3_05` | -- | 7 | **0** | BL(0,1)→k4_05 [OPEN], BL(1,0)→k4_05 [OPEN], BR(0,1)→k4_11 [OPEN], BR(1,0)→k4_06 [OPEN], TR(0,0)→k4_13 [OPEN], TL(0,1)→k4_06 [OPEN], TL(1,0)→k4_11 [OPEN] |
| `k2_00` | -- | 5 | **0** | BL(0,2)→k3_00 [no row], BL(1,0)→k3_02 [OPEN], BR(0,0)→k3_03 [OPEN], TR(0,0)→k3_04 [OPEN], TL(0,0)→k3_01 [OPEN] |
| `k2_01` | -- | 6 | **0** | BL(0,1)→k3_01 [OPEN], BL(1,0)→k3_03 [OPEN], BR(0,0)→k3_05 [OPEN], TR(0,0)→k3_05 [OPEN], TL(0,1)→k3_01 [OPEN], TL(1,0)→k3_03 [OPEN] |
| `k2_02` | -- | 6 | **0** | BL(0,1)→k3_04 [OPEN], BL(1,0)→k3_04 [OPEN], BR(0,0)→k3_05 [OPEN], TR(0,1)→k3_04 [OPEN], TR(1,0)→k3_04 [OPEN], TL(0,0)→k3_05 [OPEN] |
| `k1_00` | -- | 5 | **0** | BL(0,1)→k2_00 [OPEN], BL(1,0)→k2_00 [OPEN], BR(0,0)→k2_01 [OPEN], TR(0,0)→k2_02 [OPEN], TL(0,0)→k2_01 [OPEN] |
| `k4_00` | -- | 4 | **4** | BL(1,1)→k5_00 [FULL-WINDOW], BL(2,0)→k5_01 [FULL-WINDOW], BR(0,0)→k5_02 [FULL-WINDOW], TR(0,0)→k5_03 [FULL-WINDOW] |
| `k4_01` | -- | 4 | **4** | BL(1,0)→k5_02 [FULL-WINDOW], BR(0,1)→k5_06 [FULL-WINDOW], BR(1,0)→k5_04 [FULL-WINDOW], TR(0,0)→k5_07 [FULL-WINDOW] |
| `k4_02` | -- | 4 | **4** | BL(1,0)→k5_03 [FULL-WINDOW], BR(0,0)→k5_07 [FULL-WINDOW], TR(0,1)→k5_08 [FULL-WINDOW], TR(1,0)→k5_05 [FULL-WINDOW] |
| `k4_04` | -- | 4 | **4** | BL(1,0)→k5_10 [FULL-WINDOW], BR(0,0)→k5_12 [FULL-WINDOW], TR(0,0)→k5_13 [FULL-WINDOW], TL(2,0)→k5_04 [FULL-WINDOW] |
| `k4_07` | -- | 5 | **5** | BL(0,2)→k5_00 [FULL-WINDOW], BL(2,0)→k5_00 [FULL-WINDOW], BR(0,0)→k5_09 [FULL-WINDOW], TR(0,0)→k5_18 [FULL-WINDOW], TL(0,0)→k5_09 [FULL-WINDOW] |
| `k4_09` | -- | 6 | **6** | BL(0,2)→k5_05 [FULL-WINDOW], BL(1,0)→k5_19 [FULL-WINDOW], BR(0,0)→k5_20 [FULL-WINDOW], TR(0,1)→k5_19 [FULL-WINDOW], TR(2,0)→k5_05 [FULL-WINDOW], TL(0,0)→k5_14 [FULL-WINDOW] |
| `k4_10` | -- | 6 | **6** | BL(0,2)→k5_06 [FULL-WINDOW], BL(1,0)→k5_10 [FULL-WINDOW], BR(0,2)→k5_06 [FULL-WINDOW], BR(1,0)→k5_10 [FULL-WINDOW], TR(0,0)→k5_15 [FULL-WINDOW], TL(0,0)→k5_15 [FULL-WINDOW] |
| `k4_12` | -- | 6 | **6** | BL(0,2)→k5_08 [FULL-WINDOW], BL(1,0)→k5_19 [FULL-WINDOW], BR(0,0)→k5_17 [FULL-WINDOW], TR(0,2)→k5_08 [FULL-WINDOW], TR(1,0)→k5_19 [FULL-WINDOW], TL(0,0)→k5_17 [FULL-WINDOW] |
| `k3_00` | -- | 3 | **0** | BL(1,0)→k4_00 [s0 only], BR(0,0)→k4_01 [s0 only], TR(0,0)→k4_02 [s0 only] |
