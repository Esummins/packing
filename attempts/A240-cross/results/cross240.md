# A240 -- Theorem CROSS on the witnesses (1393 witnesses with a bounded FJ stress; 1363 doubly-met corners)

Corner frame (u, v); handedness in the FRAME: + = frame tilt < 45 deg, - = > 45 deg, F flat, D diamond; a pair is "same" / "opposite" by frame handedness, "flat" if a member is F or D.  LOCKED = both meeters carry a loaded wall or pair row and NO external row (tilt bound / crowd pull) is loaded on either; EXT = an external row is loaded on a meeter; UNLOADED = a meeter carries nothing.  Partner type = the loaded contact(s) between the two meeters (flush / VE / VV).

## T1. Lemma OPPOSE's test: every doubly-met corner by lock status and frame-handedness pair

| group | locked/same | locked/opposite | locked/flat | ext/same | ext/opposite | ext/flat | unloaded/same | unloaded/opposite | unloaded/flat | total |
|---|---|---|---|---|---|---|---|---|---|---|
| CROWD | 50 | 1 | 22 | 296 | 9 | 228 | 113 | 13 | 8 | 740 |
| FJ | 44 | 1 | 39 | 0 | 0 | 0 | 64 | 2 | 12 | 162 |
| HELD | 121 | 9 | 6 | 279 | 26 | 2 | 16 | 0 | 0 | 459 |
| RECORD | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| TRUMP | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

## T2. LOCKED corners by pair and partner contact type

| group | flat/None | flat/VE | flat/flush | opposite/VE | same/None | same/VE | same/flush | total |
|---|---|---|---|---|---|---|---|---|
| CROWD | 2 | 20 | 0 | 1 | 0 | 9 | 41 | 73 |
| FJ | 3 | 21 | 15 | 1 | 1 | 7 | 36 | 84 |
| HELD | 0 | 0 | 6 | 9 | 0 | 7 | 114 | 136 |
| RECORD | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| TRUMP | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |

## T3. At LOCKED corners with a loaded partner contact: the partner torque on each meeter is anti-aligning (A, sign chi) or aligning (a, sign -chi); f = flat / diamond meeter

| group | AA | Aa | Af | aa | af | ff | total |
|---|---|---|---|---|---|---|---|
| CROWD | 15 | 36 | 7 | 0 | 13 | 0 | 71 |
| FJ | 21 | 23 | 11 | 0 | 7 | 18 | 80 |
| HELD | 61 | 67 | 0 | 2 | 0 | 6 | 136 |
| RECORD | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| TRUMP | 0 | 0 | 0 | 0 | 1 | 0 | 1 |

Lemma W on the meeters: wall torque of sign -chi (or 0) on 2382 / 2382 tilted meeters; 326 flat / diamond wall-loaded meeters carry a free self-torque (two vertex rows).

## T4. The ring `rand_0_0569|t20` (w364_held, side 4.1099): every corner is a same-handed pair held by a tilt-bound torque

| corner | pair (frame / global) | meeter | h frame / global | tilt (frame) | W | tau wall | tau partner | tau along-wall | tau other | tau ext (tilt bound) |
|---|---|---|---|---|---|---|---|---|---|---|
| BL | same / same | 4 | - / - | 70.0 | 0.000 | +0.000 | +0.014 | +0.286 | +0.000 | -0.300 |
| BL | same / same | 5 | - / - | 70.0 | 0.609 | +0.182 | -0.286 | +0.104 | -0.000 | +0.000 |
| BR | same / same | 6 | - / + | 70.0 | 0.391 | +0.117 | -0.152 | +0.035 | +0.000 | +0.000 |
| BR | same / same | 7 | - / + | 70.0 | 0.609 | +0.182 | -0.132 | -0.031 | +0.000 | -0.018 |
| TR | same / same | 8 | + / + | 20.0 | 0.000 | +0.000 | -0.092 | +0.000 | -0.104 | +0.196 |
| TR | same / same | 10 | + / + | 20.0 | 0.196 | -0.058 | +0.080 | -0.021 | +0.000 | +0.000 |
| TL | same / same | 2 | + / - | 20.0 | 0.000 | +0.000 | -0.104 | +0.000 | +0.031 | +0.073 |
| TL | same / same | 3 | + / - | 20.0 | 0.196 | -0.058 | +0.080 | -0.021 | +0.000 | +0.000 |

Wall grains of the ring (meeters touching each wall, global handedness): y=0: [4, 6] ['-', '+']; x=s: [7] ['+']; y=s: [10, 3] ['+', '-']; x=0: [5] ['-']
Chains: LR [5, 4, 6, 7], TB [6, 0, 1, 10], shared [6] ([{'i': 6, 'h': '+', 'meeter_of': ['BR'], 'ext_load': 0.0, 'walls_loaded': ['y=0'], 'edges': ['VV', 'flush', 'VV']}]).

## T5. Wall grains on the 193 four-crowds: the loaded handednesses of the meeters touching each wall (772 walls)

| group | one-handed | mixed +- | tilted + flat | flat only | none loaded | total |
|---|---|---|---|---|---|---|
| FOUR (193) | 373 | 144 | 146 | 75 | 34 | 772 |

Four-crowds with at least one mixed wall: 110 / 193; with the PI's alternation (left = right handed, top = bottom handed, left != top, every wall one-handed): 0.

## T6. Loaded bracing chains on the four-crowds: a left-right chain (loaded contact path from a loaded left-wall row to a loaded right-wall row) and a floor-ceiling chain

| group | LR+TB | LR only | TB only | neither | total |
|---|---|---|---|---|---|
| FOUR | 126 | 19 | 21 | 27 | 193 |

## T7. What sits at the crossing (the squares shared by the shortest LR and TB chains; 126 four-crowds)

| group | flush/diamond meeter, ext-loaded | flush/diamond meeter, no ext | flush/diamond non-meeter, no ext | tilted meeter, ext-loaded | tilted meeter, no ext | tilted non-meeter, no ext | total |
|---|---|---|---|---|---|---|---|
| FOUR | 4 | 18 | 6 | 64 | 38 | 90 | 220 |

Shared-square counts per four-crowd: {1: 49, 2: 66, 3: 6, 4: 4, 5: 1}.  Interior chains (both chains avoiding every corner meeter): 0 / 193.  Four-crowds whose crossing squares are ALL tilted and externally unloaded: 47.

## T8. Where the loaded component of a loaded crowd ENDS (Corollary CHAIN): far walls reached and other corners' meeters contained

| group | both far walls, adjacent corner | both far walls, opposite corner | no far wall, adjacent corner | no far wall, no other corner | one far wall, adjacent corner | one far wall, opposite corner | total |
|---|---|---|---|---|---|---|---|
| FJ | 13 | 55 | 1 | 8 | 3 | 4 | 84 |
| FOUR | 39 | 486 | 1 | 13 | 78 | 1 | 618 |
| HELD | 19 | 388 | 0 | 4 | 0 | 0 | 411 |
| RECORD | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| TRUMP | 0 | 1 | 0 | 0 | 0 | 0 | 1 |

CROSS-PLANAR on all 589 witnesses with both loaded chains: a shared square on 586, only an UNLOADED contact between the chains on 3 (four-crowds among them: 0; e.g. square-26b [[2, 1], [18, 17], [18, 21], [20, 17], [20, 21]], fj_cp85_188_free [[3, 8], [6, 2], [6, 5], [6, 8], [7, 2], [7, 8], [7, 9]], fj_rand_0_0543_free [[1, 7], [3, 4], [3, 7], [3, 10], [6, 7], [6, 10]]), neither on 0.

Trump: TL flat pair (sq4 flat, sq6 at 49.82 deg frame), locked; chains LR [3, 1, 8, 2], TB [0, 3, 7, 9, 5], shared [3] = the FLUSH square 3 on the left wall (['flush', 'flush', 'VE']).

## Examples (for the pages)

```
{"same_VE_FJ": [["fj_cp85_170_free", "BR"], ["fj_rand_0_0055_free", "BR"], ["fj_rand_0_0067_free", "TR"], ["fj_rand_0_0073_free", "TR"], ["fj_rand_0_0167_free", "TL"], ["fj_rand_0_0401_free", "TR"], ["fj_rand_0_0424_free", "BR"]], "opposite_HELD": [["w300_held", "BR"], ["w333_held", "BL"], ["w350_held", "BR"], ["w353_held", "TR"], ["w370_held", "BL"], ["w376_held", "TL"], ["w386_held", "TR"], ["w394_held", "TR"]], "tilted_crossing_no_ext": ["w037_crowd", "w039_crowd", "w050_crowd", "w052_crowd", "w053_crowd", "w059_crowd", "w060_crowd", "w061_crowd"]}
```
