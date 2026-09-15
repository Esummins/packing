# A222 RAISE test on A217's witnesses (4534 packings, 377 s; `raise222.jsonl`)

d(Pi) = |M(Pi)| - |Pi| minimised over every family Pi of pairwise disjoint census cells (offsets <= 2, all four frames) containing a corner; d <= 0 is Lemma CELLS: the packing exchanges into one with all of Pi settled.  "K0FREE-corner": a corner box met by <= 1 square (K0-FREE teleports).  "window8": the 8-cell window-shaped perimeter (one middle per wall) at the witness's own side.

| class | n | sides | SETTLED | K0FREE-corner | RAISE2 | RAISE1 | NONE | smallest under-met family: size 1 / 2 / 3 / >= 4 | window8 sub-family d_min <= 0 / = 1 / >= 2 | window8 sweep succeeds | >= 1 independent pair |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SETTLED | 430 | 3.8867 - 4.5616 | 430 | 0 | 0 | 0 | 0 | 430 / 0 / 0 / 0 | 430 / 0 / 0 | 430 | 420 |
| K0FREE | 417 | 3.8972 - 5.0000 | 0 | 417 | 0 | 0 | 0 | 417 / 0 / 0 / 0 | 417 / 0 / 0 | 417 | 375 |
| BOXK0 | 36 | 4.0000 - 5.0000 | 0 | 36 | 0 | 0 | 0 | 36 / 0 / 0 / 0 | 36 / 0 / 0 | 36 | 5 |
| HELD | 2487 | 3.9072 - 5.2817 | 0 | 2479 | 8 | 0 | 0 | 2479 / 8 / 0 / 0 | 2484 / 3 / 0 | 2487 | 140 |
| CROWD | 1164 | 4.0013 - 5.0255 | 0 | 0 | 1164 | 0 | 0 | 0 / 1164 / 0 / 0 | 1127 / 37 / 0 | 1164 | 0 |

## Four-crowds (n2 = 4, HELD + CROWD): 1172
verdicts: K0FREE-corner 0, RAISE2 1172, RAISE1 0, NONE 0
d_min distribution: -2: 92, -1: 730, 0: 350
window8 full-family d: 0: 45, 1: 439, 2: 589, 3: 99
window8 sub-family d_min: 0: 1132, 1: 40
window8 sweeps succeeding (of 8 starts) per witness: 0: 0, 1: 10, 2: 80, 3: 267, 4: 388, 5: 196, 6: 173, 7: 42, 8: 16
sweeps succeeding (of 8 starts) per witness: 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 1172

## The ring rand_0_0569|t20 (side 4.1099)
corner meeters: {'BL(0,0)': 2, 'BR(0,0)': 2, 'TR(0,0)': 2, 'TL(0,0)': 2}
d_min = 0 at ['BR(0,0)', 'BR(1,0)'] (M = [6, 7]); by size: {'1': 1, '2': 0, '3': 0, '4': 0}
window8: ['BL(0,0)', 'BL(1,0)', 'BR(0,0)', 'BR(0,1)', 'TR(0,0)', 'TR(1,0)', 'TL(0,0)', 'TL(0,1)'], |M| = 10, d = 2
sweep from BR (cw): nothing in hand at step 2
  step 1 BR(0,0): M = [6, 7], pick up [6, 7], place one, in hand 1
  step 2 BR(1,0): M = [], place from hand, in hand 0
window8 sub-family d_min = 0 at ['TL(0,0)', 'TL(0,1)']; by size {'1': 1, '2': 0, '3': 1, '4': 1}; window sweep from BR (cw): nothing in hand at step 2
  step 1 BR(0,0): M = [6, 7], pick up [6, 7], place one, in hand 1
  step 2 BR(1,0): M = [], place from hand, in hand 0
