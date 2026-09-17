# A245 results -- STACK sampled, WALL-CLICK and REDUCE on every testbed wall

## 1. Lemma STACK on the mutual wall-pair family (`stack245.py`, exact SAT, 4 000 mutual pairs per side)

| side | pairs | order B < B' | clearance < 4 - s | floating (gap > 0) | max gap | contact keeps cells | table match | H_contact min | H - chords min |
|---|---|---|---|---|---|---|---|---|---|
| 3.82 | 4000 | 4000 | 4000 | 2235 | 0.1742 | 4000 | 4000 | 2.000 | 0.000 |
| 3.877084 | 4000 | 4000 | 4000 | 1863 | 0.1207 | 4000 | 3998 | 2.000 | 0.000 |
| 3.95 | 4000 | 4000 | 4000 | 1004 | 0.0465 | 4000 | 3999 | 2.000 | 0.000 |
| 3.99 | 4000 | 4000 | 4000 | 326 | 0.0096 | 4000 | 4000 | 2.000 | 0.000 |

Handedness pairs and contact types at contact (side 3.82): `{"++ TonV'R'": 539, "++ V'onLT": 426, "++ flush": 243, "+- TonL'V'": 271, "+- V'onLT": 247, "+F TonL'V'": 43, "+F TonV'R'": 53, "-+ TonV'R'": 339, "-+ V'onTR": 330, "-- TonL'V'": 500, "-- V'onTR": 483, "-- flush": 236, "-F TonL'V'": 42, "-F TonV'R'": 33, "F+ V'onLT": 32, "F+ V'onTR": 40, "F- V'onLT": 43, "F- V'onTR": 42, "FF T=V'": 14, "FF flush": 44}`

## 2. Wall pairs in the testbeds (`click245.py`)

| family | walls | pairs found | H-WALL | mutual | mutual & H-WALL | B|B' in contact | order ok (H-WALL) |
|---|---|---|---|---|---|---|---|
| A244's 12-stuck candidates (S >= 4.00001) | 308 | 115 | 102 | 20 | 7 | 25 | 102 |
| A239 / A226 rings (8-9 squares, not 12-stuck) | 84 | 40 | 40 | 0 | 0 | 16 | 40 |
| the 193 four-crowds (S >= 4.0014) | 772 | 550 | 541 | 19 | 10 | 177 | 541 |
- a244: no pair because {"no wall-touching meeter of c and no mutual pair": 122, "no wall-touching meeter of c' and no mutual pair": 71}; handedness of the pairs {"++": 27, "F-": 5, "--": 26, "+-": 36, "-+": 19, "-F": 1, "+F": 1}; contact types (H-WALL pairs) {"none": 82, "T=V'": 11, "TonL'V'": 3, "V'onLT": 1, "TonL'V'+V'onTR": 1, "TonV'R'": 1, "V'onTR": 2, "TonV'R'+V'onLT": 1}.
- ring: no pair because {"no wall-touching meeter of c' and no mutual pair": 44}; handedness of the pairs {"+F": 32, "DF": 4, "-F": 4}; contact types (H-WALL pairs) {"TonV'R'": 16, "none": 24}.
- crowd: no pair because {"no wall-touching meeter of c' and no mutual pair": 92, "no wall-touching meeter of c and no mutual pair": 130}; handedness of the pairs {"F+": 34, "F-": 34, "+-": 113, "+F": 57, "-+": 51, "++": 103, "FF": 34, "-F": 34, "--": 90}; contact types (H-WALL pairs) {"none": 373, "TonV'R'": 24, "V'onTR": 16, "TonL'V'": 55, "V'onLT": 63, "flush:TonV'R'+V'onLT": 5, "flush:TonL'V'+V'onTR": 4, "T=V'": 1}.

- A244's slot supply over the 77 candidates (616 slots): {"OWN": 924, "ADJ": 192, "FREE": 207}; walls whose BOTH slots are supplied by the adjacent corner (the mutual case): 20 of 308.
- corner meeters touching a wall of the container (tol 1e-4): a244 342 / 616, ring 124 / 168, crowd 1339 / 1544

## 3. WALL-CLICK: the pair rotated jointly to flush

| family | pairs | LOCAL feasible at s0 | LOCAL blocked | LOCAL side rises | blockers | GLOBAL blocked | GLOBAL end <= s0 | GLOBAL monotone | max rise above s0 |
|---|---|---|---|---|---|---|---|---|---|
| a244 | 115 | 80 | 21 | 14 | {"A'": 14, "A": 15, "free": 6, "slot-meeter": 8, "pair": 1} | 0 | 108 | 79 | 0.0041 |
| ring | 40 | 35 | 3 | 2 | {"pair": 1, "A'": 1, "free": 1, "A": 2} | 0 | 40 | 40 | -0.3196 |
| crowd | 550 | 177 | 206 | 167 | {"slot-meeter": 148, "A'": 152, "A": 156, "free": 32, "pair": 1} | 0 | 448 | 224 | 0.0487 |

- on the MUTUAL walls: local click feasible at s0 on a244 5 / 20, ring 0 / 0, crowd 2 / 19; global click ends at <= s0 on a244 18 / 20, ring 0 / 0, crowd 8 / 19.
- the pair's along-wall extent H exceeds 2 before the click on a244 115 / 115, ring 40 / 40, crowd 550 / 550 (chord sums 2.000 .. 2.596, exactly 2 after any click).

## 4. REDUCE on the wall column (Lemma CELLS k = 1, 2, 3 and the (k+1)-for-(k+1) exchange)

| family | walls | before: any k | k1 direct | k2 direct | k2 3-for-3 placed | after LOCAL click | after GLOBAL click |
|---|---|---|---|---|---|---|---|
| a244 | 308 | 295 | 0 | 136 | 116 | 70 / 94 | 86 / 115 |
| ring | 84 | 84 | 0 | 40 | 44 | 37 / 37 | 32 / 40 |
| crowd | 772 | 739 | 0 | 414 | 238 | 307 / 344 | 425 / 550 |

Every testbed sits at S >= 3.877 (rings) or S >= 4.0000 (12-stuck, four-crowds): REDUCE succeeding there is room at or above 4, not a kill; the tables test the choreography, not STUCK-4.

