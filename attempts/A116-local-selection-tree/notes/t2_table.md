# A116 T2 -- the measured radius (results/t2_*.jsonl)

* S02/k5_11 [PI_N_single_leaf, cut None, ceil None]: largest certified (r, rho) = (0.019, 1.9 deg); certified min 3.885780, measured 3.886746, 6 s
* S02/k5_11 [canary_r0_exactpins_anchor_sstar, cut None, ceil None]: largest certified (r, rho) = (0.000, 0.0 deg); certified min 3.886745, measured 3.886746, 0 s
* S02/k5_11 [ceil49.80, cut None, ceil 49.8]: largest certified (r, rho) = (0.100, 10.0 deg); certified min 3.877315, measured 3.885618, 40 s
* S02/k5_11 [exactpins, cut None, ceil None]: largest certified (r, rho) = (0.100, 10.0 deg); certified min 3.877285, measured 3.886746, 62 s
* S02/k5_11 [grid, cut None, ceil None]: largest certified (r, rho) = (0.200, 10.0 deg); certified min 3.877105, measured 3.885618, 445 s
* S02/k5_11 [with_f0_TR, cut None, ceil None]: largest certified (r, rho) = (0.100, 5.0 deg); certified min 3.877091, measured 3.886746, 171 s
* S02/k5_16 [k5_16frame, cut None, ceil None]: largest certified (r, rho) = (0.100, 10.0 deg); certified min 3.878207, measured 3.886746, 24 s
* S07/trump5 [PI_N_single_leaf, cut None, ceil None]: largest certified (r, rho) = (0.024, 2.4 deg); certified min 3.884789, measured 3.885618, 1 s
* S07/trump5 [canary_r0_exactpins_anchor_sstar, cut None, ceil None]: largest certified (r, rho) = (0.000, 0.0 deg); certified min 3.885617, measured 3.885618, 0 s
* S07/trump5 [cut41.565, cut 41.565, ceil None]: largest certified (r, rho) = (0.100, 40.0 deg); certified min 3.878622, measured 3.886746, 52 s
* S07/trump5 [cutT, cut 40.202, ceil None]: largest certified (r, rho) = (0.200, 10.0 deg); certified min 3.877086, measured 3.877218, 261 s
* S07/trump5 [exactpins, cut 41.565, ceil None]: largest certified (r, rho) = (0.100, 10.0 deg); certified min 3.878416, measured 3.885618, 16 s
* S07/trump5 [nocut, cut None, ceil None]: largest certified (r, rho) = (0.100, 2.0 deg); certified min 3.884134, measured 3.885618, 12 s
* S07/trump5 [with_f1, cut 41.565, ceil None]: largest certified (r, rho) = (0.100, 10.0 deg); certified min 3.877136, measured 3.885618, 99 s

## S02 / k5_11  label PI_N_single_leaf  cut None  ceil None  pin slack 0.00707  L = ['f1', 'f2', 'f3', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.019 | 1.9 | 10 | 64 | 2375 | 1184 | 7 / 1100 / 76 | DEAD | 3.885780 | 3.886746 | 10000 / 0 | False | 6 | 103 | BL(0,0)|BL(0,1) BR(0,0)|BR(0,1) f1|BL(0,1) f1|f2 f2|f3 f3|BR(0,1) wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:f2/y-hi |

## S02 / k5_11  label canary_r0_exactpins_anchor_sstar  cut None  ceil None  pin slack 0.0  L = ['f1', 'f2', 'f3', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0.0 | 10 | 64 | 1 | 1 | 0 / 0 / 0 | DEAD | 3.886745 | 3.886746 | 10000 / 0 | False | 0 | 74 | wall:f2/y-hi |

## S02 / k5_11  label ceil49.80  cut None  ceil 49.8  pin slack 0.00707  L = ['f1', 'f2', 'f3', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 10.0 | 10 | 128 | 11023 | 5514 | 39 / 5442 / 0 | DEAD | 3.877315 | 3.885618 | 10000 / 0 | False | 40 | 141 | - |
| 0.200 | 20.0 | 11 | 768 | 227506 | 113980 | 254 / 113272 / 0 | CAP | 3.877088 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,0)|BR(0,1) f1|BL(0,1) f2|f1 f3|BR(0,1) f3|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:f2/y-hi |

## S02 / k5_11  label exactpins  cut None  ceil None  pin slack 0.0  L = ['f1', 'f2', 'f3', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.050 | 5.0 | 10 | 64 | 5551 | 2793 | 31 / 2693 / 36 | DEAD | 3.877144 | 3.885852 | 10000 / 0 | False | 17 | 91 | - |
| 0.100 | 10.0 | 10 | 192 | 17591 | 8770 | 47 / 8674 / 0 | DEAD | 3.877285 | 3.886746 | 10000 / 0 | False | 62 | 143 | - |

## S02 / k5_11  label grid  cut None  ceil None  pin slack 0.00707  L = ['f1', 'f2', 'f3', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.020 | 2.0 | 10 | 64 | 2255 | 1124 | 7 / 1076 / 40 | DEAD | 3.885781 | 3.886746 | 10000 / 0 | False | 7 | 140 | BL(0,0)|BL(0,1) BR(0,1)|BR(0,0) f1|BL(0,1) f1|TL(0,0) f1|f2 f2|f3 f3|BR(0,1) wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:f2/y-hi |
| 0.050 | 2.0 | 10 | 64 | 4175 | 2084 | 31 / 1993 / 27 | DEAD | 3.879681 | 3.886746 | 10000 / 0 | False | 13 | 138 | - |
| 0.100 | 2.0 | 10 | 64 | 4743 | 2365 | 31 / 2301 / 0 | DEAD | 3.877836 | 3.885815 | 10000 / 0 | False | 16 | 130 | - |
| 0.200 | 2.0 | 10 | 192 | 7035 | 3538 | 47 / 3442 / 0 | DEAD | 3.877131 | 3.885815 | 10000 / 0 | False | 27 | 129 | - |
| 0.300 | 2.0 | 11 | 2304 | 27535 | 13755 | 323 / 13158 / 113 | ALIVE (witness 3.873295) | 3.877091 | - | - | False | 116 | 116 | witness: f1|f2[1, 0, -1], f1|BL(0,1)[0, 0, -1], f1|TL(0,0)[1, 1, -1], f2|f3[1, 1, 1], f3|BR(0,1)[1, 1, 1], f1|f3[1, 0, -1], f2|TL(0,0)[1, 0, 1] |
| 0.020 | 5.0 | 10 | 64 | 4671 | 2195 | 31 / 2195 / 0 | DEAD | 3.879768 | 3.886746 | 10000 / 0 | False | 15 | 134 | - |
| 0.050 | 5.0 | 10 | 64 | 5651 | 2845 | 31 / 2753 / 28 | DEAD | 3.877085 | 3.885852 | 10000 / 0 | False | 21 | 141 | - |
| 0.100 | 5.0 | 10 | 128 | 8523 | 4232 | 39 / 4160 / 0 | DEAD | 3.877381 | 3.886746 | 10000 / 0 | False | 30 | 154 | - |
| 0.200 | 5.0 | 10 | 192 | 24091 | 12044 | 55 / 11924 / 0 | DEAD | 3.877152 | 3.885618 | 10000 / 0 | False | 97 | 206 | - |
| 0.300 | 5.0 | 11 | 4608 | 159865 | 79959 | 345 / 79369 / 0 | ALIVE (witness 3.875307) | 3.877084 | - | - | False | 900 | 900 | witness: f1|f2[1, 0, -1], f1|BL(0,1)[0, 0, -1], f1|TL(0,0)[1, 1, -1], f3|BR(0,1)[1, 1, 1], f1|f3[1, 0, -1], f2|f3[1, 1, 1], f2|TL(0,0)[1, 0, 1] |
| 0.020 | 10.0 | 10 | 64 | 7775 | 3094 | 31 / 3664 / 0 | DEAD | 3.879720 | 3.886746 | 10000 / 0 | False | 39 | 204 | - |
| 0.050 | 10.0 | 10 | 128 | 10043 | 5024 | 35 / 4924 / 32 | DEAD | 3.877176 | 3.885618 | 10000 / 0 | False | 61 | 226 | - |
| 0.100 | 10.0 | 10 | 192 | 17707 | 8827 | 47 / 8731 / 0 | DEAD | 3.877303 | 3.885618 | 10000 / 0 | False | 109 | 282 | - |
| 0.200 | 10.0 | 10 | 192 | 69059 | 34557 | 63 / 34413 / 0 | DEAD | 3.877105 | 3.885618 | 10000 / 0 | False | 445 | 602 | - |
| 0.300 | 10.0 | 12 | 49152 | 170160 | 85599 | 699 / 83784 / 0 | ALIVE (witness 3.875307) | 3.877084 | - | - | False | 900 | 900 | witness: f1|BL(0,1)[0, 0, -1], f1|TL(0,0)[1, 1, -1], f1|f2[1, 0, -1], f1|f3[1, 0, -1], f2|f3[1, 1, 1], f3|BR(0,1)[1, 1, 1], f2|TL(0,0)[1, 0, 1], f2|BR(0,1)[1, 1, 1] |
| 0.020 | 20.0 | 10 | 192 | 12603 | 4837 | 63 / 6052 / 0 | DEAD | 3.878424 | 3.886746 | 10000 / 0 | False | 62 | 212 | - |
| 0.050 | 20.0 | 10 | 192 | 21231 | 9659 | 63 / 10487 / 0 | DEAD | 3.877148 | 3.885624 | 10000 / 0 | False | 119 | 268 | - |
| 0.100 | 20.0 | 11 | 768 | 144682 | 70942 | 271 / 71825 / 0 | CAP | 3.877085 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,1)|BR(0,0) f1|BL(0,1) f1|f2 f1|f3 f2|f3 f3|BR(0,1) wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:f2/y-hi |
| 0.200 | 20.0 | 12 | 10240 | 138451 | 69308 | 69 / 68786 / 288 | CAP | 3.877086 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,0)|BR(0,1) BR(0,1)|f3 f1|BL(0,1) f2|f1 f3|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:f2/y-hi |
| 0.300 | 20.0 | 13 | 691200 | 248857 | 126803 | 10148 / 100670 / 0 | CAP | 3.877178 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,0)|BR(0,1) BR(0,1)|f3 TL(0,0)|f1 f1|BL(0,1) f1|f2 f3|f1 f3|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/y-hi wall:f2/y-hi |
| 0.020 | 40.0 | 12 | 3840 | 223705 | 69216 | 633 / 110377 / 0 | CAP | 3.877104 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,1)|BR(0,0) f1|BL(0,1) f1|TL(0,0) f1|f3 f2|f1 f3|BR(0,1) f3|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:f2/y-hi |
| 0.050 | 40.0 | 12 | 10240 | 238886 | 83781 | 463 / 118362 / 0 | CAP | 3.877113 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,0)|BR(0,1) f1|BL(0,1) f1|TL(0,0) f2|f1 f3|BR(0,1) f3|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:f2/y-hi |
| 0.100 | 40.0 | 12 | 38400 | 232058 | 93614 | 1422 / 112551 / 0 | CAP | 3.877112 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,1)|BR(0,0) f1|BL(0,1) f1|TL(0,0) f2|f1 f3|BR(0,1) f3|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:f2/y-hi |
| 0.200 | 40.0 | 12 | 1555200 | 259684 | 71559 | 7899 / 106810 / 0 | CAP | 3.881186 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BL(0,1)|f1 f1|TL(0,0) f1|f2 f1|f3 f2|BR(0,1) f2|f3 wall:BL(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:f2/y-hi |
| 0.300 | 40.0 | 13 | 10368000 | 134245 | 36364 | 11 / 66327 / 800 | ALIVE (witness 3.828298) | 3.877084 | - | - | False | 900 | 900 | witness: f1|f3[1, 1, 1], f1|TL(0,0)[1, 1, -1], f1|BL(0,1)[1, 0, 1], f3|BR(0,1)[1, 1, 1], f1|f2[1, 1, -1], f2|f3[1, 1, 1], f2|TL(0,0)[1, 0, 1], f2|BR(0,1)[1, 1, 1] |

## S02 / k5_11  label slot_r0.05  cut None  ceil None  pin slack 0.00707  L = ['f1', 'f2', 'f3', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.300 | 2.0 | 11 | 1536 | 14 | 3 | 10 / 0 / 0 | ALIVE (witness 3.875307) | - | - | - | False | 0 | 0 | witness: f1|f2[1, 0, -1], f1|BL(0,1)[0, 0, -1], f1|TL(0,0)[1, 1, -1], f2|f3[1, 1, 1], f3|BR(0,1)[1, 1, 1], f1|f3[1, 0, -1], f2|TL(0,0)[1, 0, 1] |
| 0.300 | 5.0 | 11 | 4608 | 14 | 3 | 10 / 0 / 0 | ALIVE (witness 3.875307) | - | - | - | False | 0 | 0 | witness: f1|f2[1, 0, -1], f1|BL(0,1)[0, 0, -1], f1|TL(0,0)[1, 1, -1], f3|BR(0,1)[1, 1, 1], f1|f3[1, 0, -1], f2|f3[1, 1, 1], f2|TL(0,0)[1, 0, 1] |
| 0.300 | 10.0 | 11 | 9216 | 1681 | 987 | 245 / 416 / 0 | ALIVE (witness 3.875307) | 3.886270 | - | - | False | 6 | 6 | witness: f1|BL(0,1)[0, 0, -1], f1|TL(0,0)[1, 1, -1], f3|BR(0,1)[1, 1, 1], f1|f2[1, 0, -1], f1|f3[1, 0, -1], f2|f3[1, 1, 1], f2|TL(0,0)[1, 0, 1] |

## S02 / k5_11  label with_f0_TR  cut None  ceil None  pin slack 0.00707  L = ['f1', 'f2', 'f3', 'f0', 'TR(0,0)', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5.0 | 16 | 2048 | 42527 | 21408 | 383 / 20704 / 0 | DEAD | 3.877091 | 3.886746 | 10000 / 0 | False | 171 | 346 | - |
| 0.100 | 10.0 | 17 | 24576 | 227144 | 111258 | 426 / 112876 / 0 | CAP | 3.877084 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BL(0,0)|BL(1,0) BR(0,0)|BR(0,1) f0|BL(1,0) f0|f3 f1|BL(0,1) f1|TL(0,0) f2|f1 f3|BR(0,1) f3|TR(0,0) f3|f1 f3|f2 wall:BL(0,0)/x-lo wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BL(1,0)/y-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi wall:f2/y-hi |

## S02 / k5_16  label k5_16frame  cut None  ceil None  pin slack 0.00707  L = ['f1', 'f2', 'f3', 'BR(0,1)']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.050 | 5.0 | 9 | 32 | 4001 | 1907 | 15 / 1875 / 0 | DEAD | 3.885789 | 3.886746 | 10000 / 0 | False | 10 | 99 | BL(0,0)|BL(0,1) BR(0,1)|BR(0,0) f1|BL(0,1) f1|TL(0,0) f2|f1 f2|f3 f3|BR(0,1) wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:f2/y-hi |
| 0.100 | 10.0 | 9 | 96 | 7817 | 3840 | 23 / 3792 / 0 | DEAD | 3.878207 | 3.886746 | 10000 / 0 | False | 24 | 120 | - |
| 0.200 | 20.0 | 12 | 30720 | 223358 | 112218 | 417 / 110723 / 0 | CAP | 3.877086 | - | - | False | 900 | 900 | BL(0,0)|BL(0,1) BR(0,0)|BR(0,1) f1|BL(0,1) f1|TL(0,0) f1|f3 f2|TR(0,0) f2|f1 f3|BR(0,1) f3|TR(0,0) f3|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/y-lo wall:BR(0,1)/x-hi wall:TL(0,0)/x-lo wall:TL(0,0)/y-hi wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi wall:f2/y-hi |

## S07 / trump5  label PI_N_single_leaf  cut None  ceil None  pin slack 0.00707  L = ['f0', 'f2', 'f4']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.024 | 2.4 | 10 | 64 | 287 | 142 | 7 / 134 / 0 | DEAD | 3.884789 | 3.885618 | 10000 / 0 | False | 1 | 62 | BL(0,1)|f0 f0|f2 f2|TR(0,0) f4|BR(0,0) f4|f0 wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |

## S07 / trump5  label canary_r0_exactpins_anchor_sstar  cut None  ceil None  pin slack 0.0  L = ['f0', 'f2', 'f4']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0.0 | 10 | 96 | 31 | 16 | 15 / 0 / 0 | DEAD | 3.885617 | 3.885618 | 10000 / 0 | False | 0 | 13 | BL(0,1)|f0 f0|f2 f4|BR(0,0) f4|f0 f4|f2 |

## S07 / trump5  label cut41.565  cut 41.565  ceil None  pin slack 0.00707  L = ['f0', 'f2', 'f4']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.020 | 2.0 | 10 | 64 | 235 | 116 | 7 / 108 / 0 | DEAD | 3.884785 | 3.885618 | 10000 / 0 | False | 1 | 63 | BL(0,0)|BL(1,0) BL(0,1)|f0 f0|f2 f0|f4 f2|TR(0,0) f4|BL(1,0) f4|BR(0,0) wall:BL(0,0)/x-lo wall:BL(0,1)/x-lo wall:BL(1,0)/y-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.050 | 2.0 | 10 | 64 | 1695 | 836 | 19 / 800 / 0 | DEAD | 3.884781 | 3.885621 | 10000 / 0 | False | 5 | 77 | BL(0,1)|f0 f2|TR(0,0) f2|f0 f4|BR(0,0) f4|f0 f4|f2 wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.100 | 2.0 | 10 | 64 | 4223 | 2075 | 19 / 2039 / 0 | DEAD | 3.884134 | 3.885618 | 10000 / 0 | False | 12 | 52 | - |
| 0.200 | 2.0 | 10 | 64 | 4599 | 2293 | 19 / 2257 / 0 | DEAD | 3.877522 | 3.885635 | 10000 / 0 | False | 16 | 55 | - |
| 0.300 | 2.0 | 11 | 1536 | 152197 | 74045 | 157 / 63219 / 12656 | ALIVE (witness 3.856379) | 3.877084 | - | - | False | 900 | 900 | witness: f0|f2[1, 0, -1], f0|f4[1, 1, 1], f0|BL(0,1)[1, 0, 1], f2|TR(0,0)[1, 0, -1], f4|BL(1,0)[1, 0, 1], f4|BR(0,0)[0, 1, -1], f2|f4[1, 1, 1], f0|BL(1,0)[1, 1, 1] |
| 0.020 | 5.0 | 10 | 64 | 2431 | 1140 | 31 / 1100 / 0 | DEAD | 3.884765 | 3.885618 | 10000 / 0 | False | 7 | 77 | BL(0,1)|f0 f2|TR(0,0) f2|f0 f4|BR(0,0) f4|f0 wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.050 | 5.0 | 10 | 64 | 4197 | 2014 | 31 / 1938 / 12 | DEAD | 3.884770 | 3.885618 | 10000 / 0 | False | 11 | 63 | BL(0,1)|f0 f0|f2 f2|TR(0,0) f4|BR(0,0) f4|f0 wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.100 | 5.0 | 10 | 64 | 5031 | 2468 | 31 / 2404 / 0 | DEAD | 3.879308 | 3.885620 | 10000 / 0 | False | 15 | 74 | - |
| 0.200 | 5.0 | 10 | 64 | 7335 | 3653 | 31 / 3589 / 0 | DEAD | 3.877410 | 3.885618 | 10000 / 0 | False | 39 | 93 | - |
| 0.300 | 5.0 | 11 | 1536 | 71575 | 35824 | 439 / 33796 / 1348 | ALIVE (witness 3.858296) | 3.877085 | - | - | False | 445 | 445 | witness: f0|f2[1, 0, -1], f0|f4[1, 1, 1], f0|BL(0,1)[1, 0, 1], f2|TR(0,0)[1, 0, -1], f4|BL(1,0)[1, 0, 1], f4|BR(0,0)[0, 1, -1], f2|f4[1, 1, 1], f0|BL(1,0)[1, 1, 1] |
| 0.020 | 10.0 | 10 | 64 | 3243 | 1506 | 31 / 1426 / 32 | DEAD | 3.884768 | 3.885618 | 10000 / 0 | False | 13 | 135 | BL(0,1)|f0 f0|f2 f2|TR(0,0) f4|BR(0,0) f4|f0 wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.050 | 10.0 | 10 | 64 | 4919 | 2332 | 31 / 2155 / 144 | DEAD | 3.881568 | 3.886746 | 10000 / 0 | False | 22 | 132 | - |
| 0.100 | 10.0 | 10 | 64 | 5703 | 2810 | 31 / 2746 / 0 | DEAD | 3.878273 | 3.885619 | 10000 / 0 | False | 27 | 137 | - |
| 0.200 | 10.0 | 10 | 64 | 10303 | 5120 | 31 / 5056 / 0 | DEAD | 3.877380 | 3.885644 | 10000 / 0 | False | 58 | 146 | - |
| 0.300 | 10.0 | 11 | 3072 | 122143 | 61128 | 427 / 60396 / 0 | ALIVE (witness 3.875193) | 3.877084 | - | - | False | 875 | 875 | witness: f0|f4[1, 1, 1], f0|BL(0,1)[1, 0, 1], f2|TR(0,0)[1, 0, -1], f4|BL(1,0)[1, 0, 1], f4|BR(0,0)[0, 1, -1], f0|f2[1, 0, -1], f2|f4[1, 1, 1], f0|BL(1,0)[1, 1, 1] |
| 0.020 | 20.0 | 10 | 64 | 3163 | 1414 | 31 / 1430 / 0 | DEAD | 3.884765 | 3.886746 | 10000 / 0 | False | 15 | 133 | BL(0,0)|BL(1,0) BL(0,1)|f0 f0|f4 f2|TR(0,0) f2|f0 f4|BL(1,0) f4|BR(0,0) wall:BL(0,0)/x-lo wall:BL(0,1)/x-lo wall:BL(1,0)/y-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.050 | 20.0 | 10 | 64 | 5703 | 2721 | 31 / 2569 / 88 | DEAD | 3.882167 | 3.886746 | 10000 / 0 | False | 26 | 129 | - |
| 0.100 | 20.0 | 10 | 64 | 6979 | 3398 | 31 / 3334 / 0 | DEAD | 3.878828 | 3.886746 | 10000 / 0 | False | 34 | 139 | - |
| 0.200 | 20.0 | 10 | 384 | 107796 | 39328 | 59 / 53148 / 672 | ALIVE (witness 3.873374) | 3.877084 | - | - | False | 900 | 900 | witness: f4|BL(1,0)[0, 0, -1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f2|TR(0,0)[1, 0, -1], f4|BR(0,0)[0, 1, -1], f0|BL(0,1)[1, 0, 1], f2|f4[1, 0, 1] |
| 0.300 | 20.0 | 12 | 27648 | 111899 | 49707 | 37 / 40983 / 14926 | ALIVE (witness 3.869558) | 3.877084 | - | - | False | 900 | 900 | witness: f2|TR(0,0)[1, 0, -1], f4|BL(1,0)[1, 0, 1], f4|BR(0,0)[0, 1, -1], f0|BL(0,1)[1, 0, 1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f2|f4[1, 1, 1], f0|BL(1,0)[1, 1, 1] |
| 0.020 | 40.0 | 10 | 96 | 3959 | 1698 | 35 / 1788 / 0 | DEAD | 3.884770 | 3.886746 | 10000 / 0 | False | 17 | 110 | f2|TR(0,0) f4|BR(0,0) f4|f2 wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.050 | 40.0 | 10 | 192 | 6403 | 2940 | 43 / 2878 / 72 | DEAD | 3.882465 | 3.885618 | 10000 / 0 | False | 30 | 117 | - |
| 0.100 | 40.0 | 10 | 768 | 9091 | 4190 | 87 / 4298 / 0 | DEAD | 3.878622 | 3.886746 | 10000 / 0 | False | 52 | 142 | - |
| 0.200 | 40.0 | 10 | 6912 | 119048 | 49527 | 382 / 56472 / 2322 | ALIVE (witness 3.869626) | 3.877084 | - | - | False | 900 | 900 | witness: f4|BR(0,0)[0, 1, -1], f0|BL(0,1)[1, 0, 1], f2|TR(0,0)[1, 0, -1], f4|BL(1,0)[0, 0, -1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f2|f4[1, 0, 1] |
| 0.300 | 40.0 | 12 | 221184 | 167700 | 62093 | 247 / 65998 / 17405 | ALIVE (witness 3.820000) | 3.877084 | - | - | False | 900 | 900 | witness: f0|BL(0,1)[1, 0, 1], f4|BR(0,0)[1, 1, 1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f2|f4[1, 0, 1], f2|TR(0,0)[1, 0, -1], f4|BL(1,0)[1, 1, 1], f0|BL(1,0)[1, 1, 1], f0|BL(0,0)[1, 1, 1] |

## S07 / trump5  label cutT  cut 40.202  ceil None  pin slack 0.00707  L = ['f0', 'f2', 'f4']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.050 | 5.0 | 10 | 64 | 5567 | 2802 | 31 / 2738 / 0 | DEAD | 3.877163 | 3.877218 | 10000 / 0 | False | 21 | 68 | - |
| 0.100 | 5.0 | 10 | 64 | 9251 | 4642 | 31 / 4578 / 0 | DEAD | 3.877086 | 3.877218 | 10000 / 0 | False | 34 | 87 | - |
| 0.200 | 5.0 | 10 | 64 | 35247 | 14226 | 31 / 17250 / 0 | UNRESOLVED | 3.877084 | - | - | False | 176 | 176 | BL(0,0)|BL(0,1) f0|BL(0,1) f0|f2 f2|TR(0,0) f4|BR(0,0) f4|f2 wall:BL(0,0)/y-lo wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.050 | 10.0 | 10 | 64 | 5791 | 2918 | 31 / 2854 / 0 | DEAD | 3.877093 | 3.877218 | 10000 / 0 | False | 21 | 84 | - |
| 0.100 | 10.0 | 10 | 64 | 10395 | 5215 | 31 / 5151 / 0 | DEAD | 3.877084 | 3.877218 | 10000 / 0 | False | 42 | 111 | - |
| 0.200 | 10.0 | 10 | 64 | 54803 | 27326 | 31 / 27262 / 0 | DEAD | 3.877086 | 3.877218 | 10000 / 0 | False | 261 | 316 | - |
| 0.050 | 20.0 | 10 | 64 | 6763 | 3402 | 31 / 3338 / 0 | DEAD | 3.877130 | 3.877218 | 10000 / 0 | False | 26 | 100 | - |
| 0.100 | 20.0 | 10 | 64 | 14059 | 7042 | 31 / 6978 / 0 | DEAD | 3.877086 | 3.877218 | 10000 / 0 | False | 55 | 125 | - |
| 0.200 | 20.0 | 10 | 384 | 170397 | 75812 | 51 / 72421 / 12703 | ALIVE (witness 3.873374) | 3.877084 | - | - | False | 900 | 900 | witness: f4|BL(1,0)[0, 0, -1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f2|TR(0,0)[1, 0, -1], f4|BR(0,0)[0, 1, -1], f0|BL(0,1)[1, 0, 1], f2|f4[1, 0, 1] |

## S07 / trump5  label exactpins  cut 41.565  ceil None  pin slack 0.0  L = ['f0', 'f2', 'f4']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.050 | 5.0 | 10 | 64 | 4087 | 1960 | 31 / 1896 / 0 | DEAD | 3.884776 | 3.885618 | 10000 / 0 | False | 11 | 50 | BL(0,1)|f0 f2|TR(0,0) f2|f0 f4|BR(0,0) f4|f0 |
| 0.100 | 10.0 | 10 | 64 | 5635 | 2763 | 31 / 2699 / 0 | DEAD | 3.878416 | 3.885618 | 10000 / 0 | False | 16 | 63 | - |

## S07 / trump5  label nocut  cut None  ceil None  pin slack 0.00707  L = ['f0', 'f2', 'f4']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.020 | 2.0 | 10 | 64 | 235 | 116 | 7 / 108 / 0 | DEAD | 3.884785 | 3.885618 | 10000 / 0 | False | 1 | 62 | BL(0,0)|BL(1,0) BL(0,1)|f0 f0|f2 f0|f4 f2|TR(0,0) f4|BL(1,0) f4|BR(0,0) wall:BL(0,0)/x-lo wall:BL(0,1)/x-lo wall:BL(1,0)/y-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.050 | 2.0 | 10 | 64 | 1695 | 836 | 19 / 800 / 0 | DEAD | 3.884781 | 3.885621 | 10000 / 0 | False | 5 | 75 | BL(0,1)|f0 f2|TR(0,0) f2|f0 f4|BR(0,0) f4|f0 f4|f2 wall:BL(0,1)/x-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
| 0.100 | 2.0 | 10 | 64 | 4223 | 2075 | 19 / 2039 / 0 | DEAD | 3.884134 | 3.885618 | 10000 / 0 | False | 12 | 52 | - |
| 0.020 | 5.0 | 10 | 64 | 4671 | 2358 | 31 / 2293 / 1 | DEAD | 3.877357 | 3.878731 | 10000 / 0 | False | 19 | 92 | - |
| 0.050 | 5.0 | 10 | 64 | 4633 | 2170 | 31 / 2058 / 64 | ALIVE (witness 3.875871) | 3.884765 | - | - | True | 14 | 16 | witness: f2|TR(0,0)[0, 0, 1], f4|BL(1,0)[0, 0, -1], f4|BR(0,0)[0, 1, -1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f0|BL(0,1)[0, 0, -1], f2|f4[1, 1, 1] |
| 0.100 | 5.0 | 10 | 64 | 5347 | 2614 | 31 / 2566 / 0 | ALIVE (witness 3.875871) | 3.879343 | - | - | True | 17 | 20 | witness: f2|TR(0,0)[0, 0, 1], f4|BL(1,0)[0, 0, -1], f4|BR(0,0)[0, 1, -1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f0|BL(0,1)[0, 0, -1], f2|f4[1, 1, 1] |
| 0.020 | 10.0 | 10 | 64 | 7559 | 3754 | 31 / 3690 / 40 | DEAD | 3.877123 | 3.877787 | 10000 / 0 | False | 29 | 103 | - |
| 0.050 | 10.0 | 10 | 64 | 5763 | 2759 | 31 / 2647 / 64 | ALIVE (witness 3.865807) | 3.879808 | - | - | True | 17 | 19 | witness: f2|TR(0,0)[0, 0, 1], f4|BL(1,0)[0, 0, -1], f4|BR(0,0)[0, 1, -1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f0|BL(0,1)[0, 0, -1], f2|f4[1, 1, 1] |
| 0.100 | 10.0 | 10 | 64 | 13255 | 5378 | 31 / 6568 / 0 | ALIVE (witness 3.847867) | 3.877084 | - | - | True | 65 | 67 | witness: f2|TR(0,0)[0, 0, 1], f4|BL(1,0)[0, 0, -1], f4|BR(0,0)[0, 1, -1], f0|f2[1, 0, -1], f0|f4[1, 1, 1], f0|BL(0,1)[0, 0, -1], f2|f4[1, 1, 1] |

## S07 / trump5  label with_f1  cut 41.565  ceil None  pin slack 0.00707  L = ['f0', 'f1', 'f2', 'f4']

| r | rho | near pairs | leaves (interval) | nodes | closed leaves | branch / bisect / qsplit | verdict | certified min | measured min (SLSQP) | samples / hits | Trump in N | tree s | total s | chain of the lowest leaf / witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 10.0 | 12 | 512 | 26903 | 13565 | 159 / 13149 / 0 | DEAD | 3.877136 | 3.885618 | 10000 / 0 | False | 99 | 199 | - |
| 0.200 | 20.0 | 13 | 12288 | 239642 | 119217 | 236 / 119373 / 0 | CAP | 3.877086 | - | - | False | 900 | 900 | BL(0,0)|BL(1,0) BL(0,1)|f0 f2|TR(0,0) f2|f0 f2|f4 f4|BL(1,0) f4|BR(0,0) f4|f0 wall:BL(0,0)/x-lo wall:BL(0,1)/x-lo wall:BL(1,0)/y-lo wall:BR(0,0)/x-hi wall:BR(0,0)/y-lo wall:TR(0,0)/x-hi wall:TR(0,0)/y-hi |
