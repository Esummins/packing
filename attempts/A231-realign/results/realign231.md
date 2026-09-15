# A231 -- the anchored re-alignment after a corner swap (`realign231.jsonl`, 964 rows)

Per case (witness x corner with a successful CORNER-SWAP): SHRINK = the fixed-tilt side minimum over the centres with the
settled S pinned to its slot (axes re-selected), s_lp0 <= s0; G_comp = the contact component of S among the tilted squares
at the shrunk configuration, g+/g- = its one-handedness parts touching S, all = every tilted square; the anchored path
rotates G toward alignment in 20 steps with S pinned and the side minimised over the centres at every step (A: the
contacts' axes kept, B: re-selected).  HORN: flush-side if the first step lowers the side, kink-side if it raises it,
flat if unchanged (an unloaded grain).  Endpoint: where the minimum along the path sits.

## 1. The ring and the 193 four-crowds (A217 HELD / CROWD; A222 corner swaps)

| item | count |
|---|---|
| witnesses (cases = witness x corner) | 193 (772) |
| corner swap available (A222 / retraction) | 686 / 772 |
| the SHRINK (fixed tilts, S pinned, axes free) lowers the side strictly below s0 | 678 / 686 |
| S touches no tilted square after the shrink (G_comp empty) | 472 / 686 |
| S touches tilted squares of ONE handedness / of BOTH | 208 / 686 / 0 / 686 |
| the leftover L is in G_comp | 58 / 686 |
| size of G_comp | {0: 472, 1: 9, 2: 4, 3: 1, 4: 1, 5: 4, 6: 11, 7: 27, 8: 62, 9: 63, 10: 32} |

| anchored path | cases | horn flush-side / kink-side / flat | endpoint flush / kink / start / blocked | blocked (free axes feasible there) | side < s0 | re-alignment < shrink | non-increasing | L in G / L blocks |
|---|---|---|---|---|---|---|---|---|
| g+A | 99 | 78 / 15 / 6 | 47 / 33 / 19 / 0 | 0 (0) | 99 / 99 | 80 / 99 | 49 / 99 | 19 / 0 |
| g-A | 70 | 53 / 11 / 6 | 33 / 24 / 13 / 0 | 0 (0) | 69 / 70 | 57 / 70 | 32 / 70 | 20 / 0 |
| compA | 214 | 196 / 10 / 8 | 194 / 9 / 11 / 0 | 0 (0) | 213 / 214 | 203 / 214 | 178 / 214 | 58 / 0 |
| compB | 214 | 197 / 9 / 8 | 205 / 2 / 7 / 0 | 0 (0) | 214 / 214 | 207 / 214 | 159 / 214 | 58 / 0 |
| allA | 510 | 485 / 24 / 1 | 508 / 1 / 1 / 0 | 0 (0) | 510 / 510 | 509 / 510 | 456 / 510 | 20 / 0 |
| allB | 510 | 487 / 22 / 1 | 507 / 2 / 1 / 0 | 0 (0) | 510 / 510 | 509 / 510 | 414 / 510 | 20 / 0 |

Largest upticks of compA: 193:w207_crowd:BL 2.5e-02, 193:w220_crowd:BR 1.4e-02, 193:w186_crowd:TL 1.1e-02, 193:w138_crowd:BR 9.4e-03

| per witness | count |
|---|---|
| >= 1 corner swap | 193 / 193 |
| >= 1 corner where swap + shrink lowers the side strictly | 193 / 193 |
| >= 1 corner with a FLUSH-SIDE grain in contact with S whose anchored drain (compA) is unblocked and ends below s0 | 119 / 193 |
| >= 1 corner with ANY strict improvement (shrink or a path) | 193 / 193 |

## 2. The 40 window-over-met four-crowds (A222 raise222, window8 d_min >= 1)

| item | count |
|---|---|
| witnesses (cases = witness x corner) | 30 (120); 10 further witnesses are among the 193 of section 1 (w047_crowd, w050_crowd, w062_crowd, w103_crowd, w115_crowd, w137_crowd, w175_crowd, w287_held, w300_held, w350_held) |
| corner swap available (A222 / retraction) | 74 / 120 |
| the SHRINK (fixed tilts, S pinned, axes free) lowers the side strictly below s0 | 73 / 74 |
| S touches no tilted square after the shrink (G_comp empty) | 62 / 74 |
| S touches tilted squares of ONE handedness / of BOTH | 11 / 74 / 0 / 74 |
| the leftover L is in G_comp | 5 / 74 |
| size of G_comp | {0: 62, 6: 3, 7: 4, 8: 2, 9: 2, 10: 1} |

| anchored path | cases | horn flush-side / kink-side / flat | endpoint flush / kink / start / blocked | blocked (free axes feasible there) | side < s0 | re-alignment < shrink | non-increasing | L in G / L blocks |
|---|---|---|---|---|---|---|---|---|
| g+A | 3 | 3 / 0 / 0 | 1 / 2 / 0 / 0 | 0 (0) | 3 / 3 | 3 / 3 | 2 / 3 | 1 / 0 |
| g-A | 7 | 5 / 1 / 1 | 4 / 1 / 2 / 0 | 0 (0) | 7 / 7 | 5 / 7 | 4 / 7 | 3 / 0 |
| compA | 12 | 10 / 1 / 1 | 10 / 1 / 1 / 0 | 0 (0) | 12 / 12 | 11 / 12 | 9 / 12 | 5 / 0 |
| compB | 12 | 10 / 1 / 1 | 11 / 0 / 1 / 0 | 0 (0) | 12 / 12 | 11 / 12 | 7 / 12 | 5 / 0 |
| allA | 64 | 54 / 10 / 0 | 59 / 2 / 3 / 0 | 0 (0) | 64 / 64 | 61 / 64 | 47 / 64 | 1 / 0 |
| allB | 64 | 55 / 9 / 0 | 63 / 1 / 0 / 0 | 0 (0) | 64 / 64 | 64 / 64 | 40 / 64 | 1 / 0 |

Largest upticks of compA: win40:win_crowd_10_0737_crowd0.05:TR 1.9e-02, win40:win_crowd_10_0925_crowd0.02:BR 1.1e-02, win40:win_crowd_10_0749_crowd0.05:BL 8.7e-03, win40:win_crowd_10_0913_crowd0.02:TR 0.0e+00

| per witness | count |
|---|---|
| >= 1 corner swap | 30 / 30 |
| >= 1 corner where swap + shrink lowers the side strictly | 30 / 30 |
| >= 1 corner with a FLUSH-SIDE grain in contact with S whose anchored drain (compA) is unblocked and ends below s0 | 10 / 30 |
| >= 1 corner with ANY strict improvement (shrink or a path) | 30 / 30 |

## 3. The 8 CROWD-ABOVE crowds of A226 (n = 26 .. 55, retraction swap)

| item | count |
|---|---|
| witnesses (cases = witness x corner) | 8 (32) |
| corner swap available (A222 / retraction) | 32 / 32 |
| the SHRINK (fixed tilts, S pinned, axes free) lowers the side strictly below s0 | 32 / 32 |
| S touches no tilted square after the shrink (G_comp empty) | 32 / 32 |
| S touches tilted squares of ONE handedness / of BOTH | 0 / 32 / 0 / 32 |
| the leftover L is in G_comp | 0 / 32 |
| size of G_comp | {0: 32} |

| anchored path | cases | horn flush-side / kink-side / flat | endpoint flush / kink / start / blocked | blocked (free axes feasible there) | side < s0 | re-alignment < shrink | non-increasing | L in G / L blocks |
|---|---|---|---|---|---|---|---|---|
| allA | 31 | 11 / 20 / 0 | 1 / 11 / 19 / 0 | 0 (0) | 14 / 31 | 3 / 31 | 1 / 31 | 0 / 0 |
| allB | 32 | 6 / 26 / 0 | 0 / 6 / 26 / 0 | 0 (0) | 32 / 32 | 6 / 32 | 0 / 32 | 0 / 0 |

| per witness | count |
|---|---|
| >= 1 corner swap | 8 / 8 |
| >= 1 corner where swap + shrink lowers the side strictly | 8 / 8 |
| >= 1 corner with a FLUSH-SIDE grain in contact with S whose anchored drain (compA) is unblocked and ends below s0 | 0 / 8 |
| >= 1 corner with ANY strict improvement (shrink or a path) | 8 / 8 |

## 4. The ring rand_0_0569|t20

* BL: no swap
* BR: s0 4.10993 -> shrink 4.06368; S touches [6, 10] (hands ['+', 'F']); grains {'g+': [6], 'comp': [6], 'all': [0, 2, 3, 4, 5, 6, 8]}
    compA: flat start s_min 4.06368 at t 0.00 (tilts [20.0]); s = [4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764]
    compB: flat start s_min 4.06368 at t 0.00 (tilts [20.0]); s = [4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764, 4.0636764]
    allA: flush-side flush s_min 4.00000 at t 1.00 (tilts [0.0]); s = [4.0636764, 4.0559729, 4.0487975, 4.0421528, 4.0360391, 4.0304549, 4.0253964, 4.0208572, 4.0168284, 4.0132979, 4.0102505, 4.0076673, 4.0055257, 4.0037987, 4.0027232, 4.0018823, 4.0012016, 4.0006757, 4.000301, 4.0000756, 4.0]
    allB: flush-side flush s_min 4.00000 at t 1.00 (tilts [0.0]); s = [4.0636764, 4.0559729, 4.0487975, 4.0421528, 4.0360391, 4.0304549, 4.0253964, 4.0208572, 4.0168284, 4.0132979, 4.0102505, 4.0076673, 4.0055257, 4.0037987, 4.002455, 4.0017235, 4.0012016, 4.0006757, 4.000301, 4.0000756, 4.0]
* TR: s0 4.10993 -> shrink 4.06476; S touches [8, 10] (hands ['F', 'F']); grains {'comp': [], 'all': [0, 2, 3, 4, 5, 6, 7]}
    allA: flush-side flush s_min 4.00000 at t 1.00 (tilts [0.0]); s = [4.0647564, 4.0601503, 4.0555791, 4.0510535, 4.0465857, 4.0421894, 4.0378799, 4.0336739, 4.0295901, 4.025649, 4.0218732, 4.0182873, 4.0149186, 4.0117967, 4.0089541, 4.0064262, 4.0042518, 4.0024733, 4.0011372, 4.0002942, 4.0]
    allB: flush-side flush s_min 4.00000 at t 1.00 (tilts [0.0]); s = [4.0647564, 4.0601503, 4.0555791, 4.0510535, 4.0465857, 4.0421894, 4.0378799, 4.0336739, 4.0295901, 4.025649, 4.0218732, 4.0182873, 4.0149186, 4.0117967, 4.0089541, 4.0064262, 4.0042518, 4.0024733, 4.0011372, 4.0002942, 4.0]
* TL: s0 4.10993 -> shrink 4.09195; S touches [7, 10] (hands ['F', '-']); grains {'g-': [0, 2, 3, 10], 'comp': [0, 2, 3, 4, 5, 6, 8, 10], 'all': [0, 2, 3, 4, 5, 6, 8, 10]}
    g-A: flush-side kink s_min 4.03833 at t 0.90 (tilts [88.0]); s = [4.0919481, 4.0905362, 4.0890039, 4.0873506, 4.0855744, 4.0836714, 4.081635, 4.0794546, 4.0771151, 4.0745942, 4.0718605, 4.0688699, 4.0655598, 4.0618422, 4.0575911, 4.0526242, 4.0466722, 4.0393364, 4.0383252, 4.038408, 4.0387374]
    g-B: flush-side flush s_min 4.00000 at t 1.00 (tilts [0.0]); s = [4.0919481, 4.0888446, 4.0857761, 4.0827437, 4.0797473, 4.0767844, 4.0738498, 4.0709348, 4.0680259, 4.0651029, 4.0621371, 4.0590879, 4.0558977, 4.0524853, 4.0487349, 4.0444788, 4.0394696, 4.0333326, 4.0254783, 4.0232574, 4.0]
    compA: flush-side flush s_min 4.00000 at t 1.00 (tilts [0.0]); s = [4.0919481, 4.0862288, 4.080477, 4.0747039, 4.0689224, 4.0631472, 4.0573955, 4.0516869, 4.0460442, 4.040494, 4.0350673, 4.0298003, 4.0247354, 4.0199228, 4.0154215, 4.0113016, 4.0076463, 4.0045554, 4.0021487, 4.0005714, 4.0]
    compB: flush-side flush s_min 4.00000 at t 1.00 (tilts [0.0]); s = [4.0919481, 4.0862288, 4.080477, 4.0747039, 4.0689224, 4.0631472, 4.0573955, 4.0516869, 4.0460442, 4.040494, 4.0350673, 4.0298003, 4.0247354, 4.0199228, 4.0154215, 4.0113016, 4.0076463, 4.0045554, 4.0021487, 4.0005714, 4.0]

## 5. A226 crowds: side after swap + shrink against the record

| n | crowd side S | record s(n) | corner | s after swap + shrink | below S | G_comp |
|---|---|---|---|---|---|---|
| 26 | 5.810660 | 5.621320 | BL | 5.666957 | yes | [] |
| 26 | 5.810660 | 5.621320 | BR | 5.644419 | yes | [] |
| 26 | 5.810660 | 5.621320 | TR | 5.666957 | yes | [] |
| 26 | 5.810660 | 5.621320 | TL | 5.644419 | yes | [] |
| 28 | 5.912222 | 5.824445 | BL | 5.839484 | yes | [] |
| 28 | 5.912222 | 5.824445 | BR | 5.839156 | yes | [] |
| 28 | 5.912222 | 5.824445 | TR | 5.839489 | yes | [] |
| 28 | 5.912222 | 5.824445 | TL | 5.839489 | yes | [] |
| 29 | 5.966917 | 5.933833 | BL | 5.938651 | yes | [] |
| 29 | 5.966917 | 5.933833 | BR | 5.939199 | yes | [] |
| 29 | 5.966917 | 5.933833 | TR | 5.939199 | yes | [] |
| 29 | 5.966917 | 5.933833 | TL | 5.937161 | yes | [] |
| 37 | 6.799310 | 6.598620 | BL | 6.646340 | yes | [] |
| 37 | 6.799310 | 6.598620 | BR | 6.622925 | yes | [] |
| 37 | 6.799310 | 6.598620 | TR | 6.646340 | yes | [] |
| 37 | 6.799310 | 6.598620 | TL | 6.624310 | yes | [] |
| 40 | 6.914214 | 6.828427 | BL | 6.849642 | yes | [] |
| 40 | 6.914214 | 6.828427 | BR | 6.849642 | yes | [] |
| 40 | 6.914214 | 6.828427 | TR | 6.849642 | yes | [] |
| 40 | 6.914214 | 6.828427 | TL | 6.849642 | yes | [] |
| 50 | 7.785714 | 7.571429 | BL | 7.630984 | yes | [] |
| 50 | 7.785714 | 7.571429 | BR | 7.601206 | yes | [] |
| 50 | 7.785714 | 7.571429 | TR | 7.630984 | yes | [] |
| 50 | 7.785714 | 7.571429 | TL | 7.601206 | yes | [] |
| 51 | 7.850400 | 7.700799 | BL | 7.715737 | yes | [] |
| 51 | 7.850400 | 7.700799 | BR | 7.715737 | yes | [] |
| 51 | 7.850400 | 7.700799 | TR | 7.707511 | yes | [] |
| 51 | 7.850400 | 7.700799 | TL | 7.715737 | yes | [] |
| 55 | 7.972886 | 7.945771 | BL | 7.951443 | yes | [] |
| 55 | 7.972886 | 7.945771 | BR | 7.948785 | yes | [] |
| 55 | 7.972886 | 7.945771 | TR | 7.950258 | yes | [] |
| 55 | 7.972886 | 7.945771 | TL | 7.950539 | yes | [] |

Resume block:
    cd C:/Users/esumm/code/packing; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
    bash attempts/A231-realign/code/run231.sh     # realign231.py --resume, then summarise231.py, pages231.py, commit
