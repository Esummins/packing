# A248 -- the corner chase on the 764 twelve-stuck packings and the genuine FJ corners

Code `chase248.py` / `external248.py` / `summarise248.py`; steps S0-S4 in the header of `summarise248.py`; every corner is seen from each of its two walls (a VIEW).

## 1. The 764 corpus packings (764 x 8 views)

* views by corner type (from this wall): {'T': 5536, 'F-floor': 288, 'F-wall': 288}
* poker sense where the PI's picture applies (flat floor meeter + partner): {'CCW on wall': 266, 'CCW off wall': 15, 'CW off wall': 2, 'CW on wall': 5}
* violations of the proved facts (sin t <= delta, TOP-2, FLAT-ABOVE, TILT-MIN, TYPE-F-OWN): {'sin > delta': 0, 'top < 2': 0, 'flat wall square above': 0, 'depth > TILT-MIN bound (1e-5)': 0, 'A meets c01 (depth > 1e-6)': 0}
* c01's second supplier beyond the poker: {'off-wall|tilted|free': 76, "wall|tilted|c'-meeter": 46, "off-wall|tilted|c'-meeter": 5}
* wall pairs (B, B') and the click: {"gain<0 | blocked by c'": 9, 'gain<0 | UNBLOCKED': 26, 'gain<0 | blocked by interior': 7, "gain<0 | blocked by c'+interior": 3, 'gain<0 | blocked by A': 1}
* where the chase fails, ACTUAL: {'S0 not locked (A244: free FJ infeasible on every one)': 6112}
* where it would fail if the corner were locked (the geometric step): {'S1 type T (no flat floor meeter)': 5536, 'S3 c01 singly met beyond touches': 166, 'S1 flat meeter on the wall, not the floor': 288, 'S3 second supplier off the wall (off-wall|tilted|free)': 60, 'consistent through S4': 16, 'S2 poker off the wall': 17, 'S4 click unblocked (a Psi-lowering exchange exists)': 22, 'S2 poker CW (POKE sense fails)': 5, "S3 second supplier off the wall (off-wall|tilted|c'-meeter)": 2}

## 2. The genuine free FJ points (883 packings)

* doubly-met corner views, LOCKED (A240 flag) vs not, by type: {'locked F-floor': 21, 'locked F-wall': 19, 'locked T': 90, 'unlocked T': 118, 'unlocked F-wall': 10, 'unlocked F-floor': 10}
* locked corners: the step of the chase they satisfy / fail: {'S2 poker CW (POKE sense fails)': 7, 'S1 flat meeter on the wall, not the floor': 19, 'S1 type T (no flat floor meeter)': 90, 'S2 poker off the wall': 5, 'S3 c01 singly met beyond touches': 5, 'S3 second supplier off the wall (off-wall|tilted|free)': 4}
* locked corners with the PI's picture: poker sense {'CW': 7, 'CCW': 14}; wall pairs {'UNBLOCKED': 1, "blocked by c'": 1}

## 3. TWO-POKERS, SEPARATE-NOTCHES, the external ring and the pocket

* TWO-POKERS: on the line theta + theta_f = 90 the bound is h(theta) = tan(45 - theta/2) + tan(theta/2) + sec theta, min 1.9342370380 at theta = 15.256253 deg -> s* = 3.9342370380; grid min over the triangle 1.93429148 at [14.90887813670389, 75.0957418550681]; certified lower bound 1.93423604 over the whole triangle: True (146403 boxes)
* SAT sup-margin of the pair (pokers wall-touching or floating, offsets <= 1) by side: {'3.820000': -0.0, '3.877084': -0.0, '3.900000': -0.0, '3.930000': -0.0, '3.934000': -0.0, '3.936000': 0.00013, '3.940000': 0.00059, '3.950000': 0.00214, '3.970000': 0.00526, '4.000000': 0.0097}
* SEPARATE-NOTCHES [M]: sup least margin of one free square serving BL01 and TL10 in the pinwheel: {'3.8200': -0.006275709907007876, '3.8771': -0.003109030511902172, '4.0000': -0.0077613861061478495}
* side 3.8500: ring NOT found (pair gap -4.44e-16, wall gap 0, least second depth -4.44e-16); x = ['0.8491', '1.0000', '0.2241', '0.1412', '1.5708', '0.2327']
* side 3.9700: ring NOT found (pair gap -8.88e-16, wall gap 0, least second depth -1.33e-15); x = ['0.9578', '1.0000', '0.2996', '0.1323', '1.5708', '0.2128']
