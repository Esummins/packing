# A223 -- grains and the click on the ring and the 193 four-crowd witnesses (`grains223.jsonl`, `click223.jsonl`)

Witnesses: A217's HELD (8) and CROWD (185) four-crowds (every corner box met by two squares) at their own sides 4.00-4.47.
Grains: connected components of the geometric contact graph among the LOADED squares (bounded FJ stress, A219 rows) within one
handedness class (theta mod 90 in (0,45) = '+', (45,90) = '-', 45 = diamond, flat).  Click: every tilted square rotates toward
its nearest axis ('+' -> 0, '-' -> 90) along t in [0,1] (20 steps), the side minimised over the centres at each step by the
alternating separating-axis LP; A = the witness's contact axes kept (the lean contacts slide), B = every axis re-selected,
C = A on the loaded squares only, the rattlers re-fitted flat at the end.

## 1. Lemma TWO-GRAIN, measured

| clause | count |
|---|---|
| both handedness classes present among the loaded tilted squares | 121 / 193 |
| a single handedness class only | 68 / 193 |
| some grain meets ALL FOUR corners | 12 / 193 |
| the grains' wall contacts cover all four walls | 140 / 193 |
| >= 1 LEAN boundary (loaded contact between opposite-handed tilted squares) | 114 / 193 |
| >= 1 boundary through a flat square | 147 / 193 |
| number of tilted grains (contact adjacency) | {0: 4, 1: 50, 2: 80, 3: 51, 4: 8} |
| number of tilted grains (loaded-row adjacency) | {0: 4, 1: 21, 2: 63, 3: 68, 4: 27, 5: 9, 6: 1} |
| handedness classes among the corner meeters (all corners pooled) | {'+/-': 39, '+/-/F': 128, '-/F': 9, '+': 4, '+/F': 10, '-': 3} |

## 2. The click

| variant | reaches the flush end | end side = 4.000 | side non-increasing at every step | blocked |
|---|---|---|---|---|
| A click (contact axes kept) | 193 / 193 | 187 / 193 | 172 / 193 | 0 |
| B free (axes re-selected) | 193 / 193 | 193 / 193 | 167 / 193 | 0 |
| C loaded core only (104 witnesses with rattlers) | 104 / 104 | rattlers re-fitted flat at the end: 6 / 104 | -- | 0 |

Largest upticks of variant A (side increase between consecutive steps): w156_crowd 1.3e-01, w139_crowd 9.8e-02, w187_crowd 7.3e-02, w218_crowd 5.6e-02, w219_crowd 4.8e-02

## 3. The ring rand_0_0569|t20

A: side along t = [4.1099276, 4.0998916, 4.0902711, 4.0810739, 4.0723087, 4.0639849, 4.0561126, 4.0487028, 4.0417669, 4.0353168, 4.029365, 4.0239243, 4.0190076, 4.0146279, 4.0107982, 4.0075308, 4.0048376, 4.0027296, 4.001216, 4.0003045, 4.0]

contacts kept at each step: [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15] of 15

B: [4.1099276, 4.0998916, 4.0902711, 4.0810739, 4.0723087, 4.0639849, 4.0561126, 4.0487028, 4.0417669, 4.0353168, 4.029365, 4.0239243, 4.0190076, 4.0146279, 4.0107982, 4.0075308, 4.0048376, 4.0027296, 4.001216, 4.0003045, 4.0]

C (core [2, 3, 4, 5, 6, 7, 8, 9, 10], rattlers [0, 1]): [4.1099276, 4.0998916, 4.0902711, 4.0810739, 4.0723087, 4.0639849, 4.0561126, 4.0487028, 4.0417669, 4.0353168, 4.029365, 4.0239243, 4.0190076, 4.0146279, 4.0107982, 4.0075308, 4.0048376, 4.0027296, 4.001216, 4.0003045, 4.0]; refit {'found': False, 'method': 'greedy+8 restarts', 'k': 2}

Resume block:
    cd C:/Users/esumm/code/packing; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
    python attempts/A223-two-grains/code/click223.py --resume     # rows are appended and committed
    python attempts/A223-two-grains/code/summarise223.py; python attempts/A223-two-grains/code/pages223.py
