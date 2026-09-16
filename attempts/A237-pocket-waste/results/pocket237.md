# A237 -- POCKET WASTE: TILT-MIN, the JAGGED census and POCKET-CAP, measured

Sources: the ring `rand_0_0569|t20` + the 193 HELD / CROWD four-crowds of A217 (loaded component U from A233), A226's nine crowd rings at n = 11, the 21 records + Trump; the window family ring(S, theta) of `family237.py`.  Waste = the rigorous coverable-set sandwich over 1-degree tilt bins (`geom237.py`); PIERCE(k) = a k-point piercing certificate of capacity <= k.  `bash attempts/A237-pocket-waste/code/run237.sh` reruns everything.

## 1. Lemma TILT-MIN on the doubly-met corners (`tiltmin237.jsonl`)

| check | holds on |
|---|---|
| ONE-TILTED: a tilted meeter at every doubly-met corner | 774 / 774 corners |
| TILT-MIN (b): flat wall meeter at offset delta, tilted partner theta: sin theta <= delta | 258 / 258 flat-tilted pairs |
| TILT-MIN (b'): the partner's lowest point >= 1 - (delta - sin theta) tan theta | 258 / 258 |
| DEPTH-BUDGET: d_A + d_B <= 1 for every pair of meeters | 774 / 774 corners (max 0.9018, median 0.4653) |
| hovering flat meeters (touching no wall) | 0 |
| HELD corners whose least tilt sits AT the imposed floor tmin_deg = 10 | 30 / 32 |

Slack of the tilt bound arcsin(delta) - theta on the flat-tilted pairs: min 1.26 deg, median 40.50 deg; the flat meeters sit at offsets delta = 0.281 .. 0.980.
Trump TR: tilts {'2': 0.0, '10': 40.182}, depths {'2': 0.1555, '10': 0.1683}, pairs [(2, 10, 0.8445, 40.18, 57.62)].
Trump TL: tilts {'4': 0.0, '6': 40.182}, depths {'4': 0.1555, '6': 0.1683}, pairs [(4, 6, 0.8445, 40.18, 57.62)].

## 2. The pockets (`pocket237.jsonl`)

**The ring + 193 four-crowds** (189 with a loaded component; 67 with n - p > 0 rattlers in the pocket):
- soundness (coverable area >= n - p, the rattlers ARE in the coverable set): 189 / 189; the area bound fires on 0 (as it must not: they are packings).
- waste: min 3.10, median 5.46, max 8.58 (pocket area median 6.13); coverable - (n - p) slack: min 0.031, median 2.030.
- PIERCE(n - p) with the rattlers' own centres: certifies 13 / 67 (the rattlers can usually slide).
- features: convex vertices median 22 (acute, i.e. < 90: 185 rows have one), reflex median 29, tilted boundary edges median 37.

**The ring** (side 4.1099, p = 9, rattlers 2): pocket area 7.892, coverable 3.580, waste 4.312 (6 uncoverable components, the largest 2.062 at (0.63, 1.39)); PIERCE(2) with the rattler centres: residual 0.119 (not certified).

**A226's crowd rings** (n = 11, S < 4):

| ring | area | coverable | waste | PIERCE(1) residual (best point) | capacity <= 1 certified | A226 greedy |
|---|---|---|---|---|---|---|
| ring8_S3.90_eps0.02 | 7.210 | 4.129 | 3.081 | 0.0e+00 at (1.950, 1.950) | YES | 1 |
| ring8_S3.90_eps0.05 | 7.210 | 3.988 | 3.222 | 0.0e+00 at (1.907, 1.950) | YES | 1 |
| ring8_S3.90_eps0.10 | 7.210 | 3.767 | 3.443 | 0.0e+00 at (1.907, 1.907) | YES | 1 |
| ring8_S3.95_eps0.02 | 7.603 | 4.441 | 3.162 | 4.2e-03 at (1.975, 1.975) | no | 1 |
| ring8_S3.95_eps0.05 | 7.603 | 4.286 | 3.317 | 2.9e-04 at (1.975, 1.975) | no | 1 |
| ring8_S3.95_eps0.10 | 7.603 | 4.047 | 3.556 | 0.0e+00 at (1.975, 1.975) | YES | 1 |
| ring8_S3.99_eps0.02 | 7.920 | 4.713 | 3.208 | 2.0e-02 at (1.995, 1.995) | no | 1 |
| ring8_S3.99_eps0.05 | 7.920 | 4.542 | 3.378 | 8.7e-03 at (1.995, 1.995) | no | 1 |
| ring8_S3.99_eps0.10 | 7.920 | 4.285 | 3.635 | 2.8e-04 at (1.995, 1.995) | no | 1 |

**The records** (U = the wall touchers; 22): sound 22 / 22, the area bound fires on 0 (it must not); waste min 0.90 median 2.18 max 3.45; PIERCE(n - p) with the interior squares' centres: 1 / 22.

| record | n | s | p | n - p | area | coverable | waste |
|---|---|---|---|---|---|---|---|
| square-5 | 5 | 2.7071 | 4 | 1 | 3.33 | 1.15 | 2.18 |
| square-10 | 10 | 3.7071 | 8 | 2 | 5.74 | 3.56 | 2.18 |
| square-11 | 11 | 3.8771 | 8 | 3 | 7.03 | 3.64 | 3.39 |
| square-17 | 17 | 4.6755 | 11 | 6 | 10.86 | 7.79 | 3.08 |
| square-18 | 18 | 4.8229 | 10 | 8 | 13.26 | 12.17 | 1.09 |
| square-19 | 19 | 4.8856 | 10 | 9 | 13.87 | 12.74 | 1.13 |
| square-26b | 26 | 5.6213 | 15 | 11 | 16.60 | 15.14 | 1.46 |
| square-27 | 27 | 5.7071 | 16 | 11 | 16.57 | 14.39 | 2.18 |
| square-28 | 28 | 5.8244 | 16 | 12 | 17.92 | 15.74 | 2.19 |
| square-29 | 29 | 5.9338 | 15 | 14 | 20.21 | 18.11 | 2.10 |
| square-37 | 37 | 6.5986 | 18 | 19 | 25.54 | 24.64 | 0.90 |
| square-38 | 38 | 6.7071 | 20 | 18 | 24.99 | 22.81 | 2.18 |
| square-39 | 39 | 6.8107 | 20 | 19 | 26.39 | 24.08 | 2.31 |
| square-40 | 40 | 6.8284 | 20 | 20 | 26.63 | 24.43 | 2.19 |
| square-41 | 41 | 6.9267 | 20 | 21 | 27.98 | 24.53 | 3.45 |
| square-50 | 50 | 7.5714 | 24 | 26 | 33.33 | 31.58 | 1.74 |
| square-51 | 51 | 7.7008 | 24 | 27 | 35.30 | 32.81 | 2.49 |
| square-52 | 52 | 7.7071 | 24 | 28 | 35.40 | 33.22 | 2.18 |
| square-53 | 53 | 7.8229 | 24 | 29 | 37.20 | 34.44 | 2.76 |
| square-54 | 54 | 7.8467 | 24 | 30 | 37.57 | 34.50 | 3.07 |
| square-55 | 55 | 7.9458 | 23 | 32 | 40.14 | 37.83 | 2.31 |
| trump_cert | 11 | 3.8771 | 8 | 3 | 7.03 | 3.64 | 3.39 |

## 3. The n = 11 window family ring(S, theta) (`family237.jsonl`)

| S | theta | delta | packing | four-crowd | area | coverable | waste | PIERCE(1) centre | PIERCE(2) | greedy cap | closes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.820 | 1 | 0.037 | True | False | 6.592 | 3.682 | 2.910 | 0.0e+00 | 0.0915 | 1 | PIERCE(1) |
| 3.820 | 2 | 0.055 | True | False | 6.592 | 3.613 | 2.980 | 0.0e+00 | 0.0887 | 1 | PIERCE(1) |
| 3.820 | 5 | 0.107 | True | True | 6.592 | 3.415 | 3.178 | 0.0e+00 | 0.0771 | 1 | PIERCE(1) |
| 3.820 | 10 | 0.194 | True | True | 6.592 | 3.112 | 3.480 | 0.0e+00 | 0.0508 | 1 | PIERCE(1) |
| 3.820 | 15 | 0.279 | True | True | 6.592 | 2.831 | 3.761 | 0.0e+00 | 0.0205 | 1 | PIERCE(1) |
| 3.820 | 20 | 0.362 | True | True | 6.592 | 2.558 | 4.034 | 0.0e+00 | 0.0000 | 1 | PIERCE(1) |
| 3.820 | 25 | 0.443 | True | True | 6.592 | 2.286 | 4.307 | 0.0e+00 | 0.0000 | 1 | PIERCE(1) |
| 3.820 | 30 | 0.520 | False | True | 6.607 | 2.031 | 4.576 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.820 | 35 | 0.594 | False | True | 6.693 | 1.809 | 4.884 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.820 | 40 | 0.663 | False | True | 6.820 | 1.626 | 5.194 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.820 | 45 | 0.727 | False | True | 6.960 | 1.492 | 5.468 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.850 | 1 | 0.037 | True | False | 6.823 | 3.844 | 2.979 | 0.0e+00 | 0.1052 | 1 | PIERCE(1) |
| 3.850 | 2 | 0.055 | True | False | 6.823 | 3.770 | 3.052 | 0.0e+00 | 0.1024 | 1 | PIERCE(1) |
| 3.850 | 5 | 0.107 | True | True | 6.823 | 3.563 | 3.260 | 0.0e+00 | 0.0907 | 1 | PIERCE(1) |
| 3.850 | 10 | 0.194 | True | True | 6.823 | 3.250 | 3.572 | 0.0e+00 | 0.0631 | 1 | PIERCE(1) |
| 3.850 | 15 | 0.279 | True | True | 6.823 | 2.963 | 3.859 | 0.0e+00 | 0.0305 | 1 | PIERCE(1) |
| 3.850 | 20 | 0.362 | True | True | 6.823 | 2.687 | 4.135 | 0.0e+00 | 0.0000 | 1 | PIERCE(1) |
| 3.850 | 25 | 0.443 | True | True | 6.823 | 2.413 | 4.410 | 0.0e+00 | 0.0000 | 1 | PIERCE(1) |
| 3.850 | 30 | 0.520 | False | True | 6.826 | 2.152 | 4.674 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.850 | 35 | 0.594 | False | True | 6.888 | 1.927 | 4.961 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.850 | 40 | 0.663 | False | True | 6.996 | 1.743 | 5.253 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.850 | 45 | 0.727 | False | True | 7.121 | 1.609 | 5.513 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.877 | 1 | 0.037 | True | False | 7.031 | 3.995 | 3.036 | 0.0e+00 | 0.1183 | 1 | PIERCE(1) |
| 3.877 | 2 | 0.055 | True | False | 7.031 | 3.917 | 3.114 | 0.0e+00 | 0.1155 | 1 | PIERCE(1) |
| 3.877 | 5 | 0.107 | True | True | 7.031 | 3.701 | 3.330 | 0.0e+00 | 0.1038 | 1 | PIERCE(1) |
| 3.877 | 10 | 0.194 | True | True | 7.031 | 3.378 | 3.653 | 0.0e+00 | 0.0753 | 1 | PIERCE(1) |
| 3.877 | 15 | 0.279 | True | True | 7.031 | 3.085 | 3.946 | 0.0e+00 | 0.0406 | 1 | PIERCE(1) |
| 3.877 | 20 | 0.362 | True | True | 7.031 | 2.806 | 4.225 | 0.0e+00 | 0.0045 | 1 | PIERCE(1) |
| 3.877 | 25 | 0.443 | True | True | 7.031 | 2.530 | 4.501 | 0.0e+00 | 0.0000 | 1 | PIERCE(1) |
| 3.877 | 30 | 0.520 | True | True | 7.031 | 2.265 | 4.766 | 0.0e+00 | 0.0000 | 1 | PIERCE(1) |
| 3.877 | 35 | 0.594 | False | True | 7.071 | 2.036 | 5.035 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.877 | 40 | 0.663 | False | True | 7.162 | 1.849 | 5.313 | 0.0e+00 | 0.0000 | None | PIERCE(1) |
| 3.877 | 45 | 0.727 | False | True | 7.274 | 1.715 | 5.559 | 0.0e+00 | 0.0000 | None | PIERCE(1) |

## 4. The n-general table (`table237.jsonl`): the area bound 4 w_c(theta) > s(n)^2 - n

One-corner sealed waste w_c(theta) (flat meeter at the least offset sin theta + 0.02, partner at tilt theta, in a side-6 box): 5 deg: 0.194, 10 deg: 0.364, 15 deg: 0.530, 20 deg: 0.689, 30 deg: 0.973, 45 deg: 1.271

| n | m | s(n) | s^2 - n | 4 w_c(10) | 4 w_c(20) | 4 w_c(45) | least tilt floor theta* that closes |
|---|---|---|---|---|---|---|---|
| 5 | 3 | 2.7071 | 2.328 | 1.457 | 2.757 | 5.083 | 17 |
| 10 | 4 | 3.7071 | 3.743 | 1.457 | 2.757 | 5.083 | 29 |
| 11 | 4 | 3.8771 | 4.032 | 1.457 | 2.757 | 5.083 | 32 |
| 17 | 5 | 4.6755 | 4.861 | 1.457 | 2.757 | 5.083 | 42 |
| 18 | 5 | 4.8229 | 5.260 | 1.457 | 2.757 | 5.083 | none |
| 19 | 5 | 4.8856 | 4.869 | 1.457 | 2.757 | 5.083 | 42 |
| 26 | 6 | 5.6213 | 5.599 | 1.457 | 2.757 | 5.083 | none |
| 27 | 6 | 5.7071 | 5.571 | 1.457 | 2.757 | 5.083 | none |
| 28 | 6 | 5.8244 | 5.924 | 1.457 | 2.757 | 5.083 | none |
| 29 | 6 | 5.9338 | 6.210 | 1.457 | 2.757 | 5.083 | none |
| 37 | 7 | 6.5986 | 6.542 | 1.457 | 2.757 | 5.083 | none |
| 38 | 7 | 6.7071 | 6.985 | 1.457 | 2.757 | 5.083 | none |
| 39 | 7 | 6.8107 | 7.386 | 1.457 | 2.757 | 5.083 | none |
| 40 | 7 | 6.8284 | 6.627 | 1.457 | 2.757 | 5.083 | none |
| 41 | 7 | 6.9267 | 6.979 | 1.457 | 2.757 | 5.083 | none |
| 50 | 8 | 7.5714 | 7.327 | 1.457 | 2.757 | 5.083 | none |
| 51 | 8 | 7.7008 | 8.302 | 1.457 | 2.757 | 5.083 | none |
| 52 | 8 | 7.7071 | 7.399 | 1.457 | 2.757 | 5.083 | none |
| 53 | 8 | 7.8229 | 8.197 | 1.457 | 2.757 | 5.083 | none |
| 54 | 8 | 7.8467 | 7.570 | 1.457 | 2.757 | 5.083 | none |
| 55 | 8 | 7.9458 | 8.135 | 1.457 | 2.757 | 5.083 | none |
