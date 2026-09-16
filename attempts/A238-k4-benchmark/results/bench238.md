# A238 -- the k5 toolkit on the Trump-parent protected classes: geometry against A100's LP

Every row is ONE node of a protected class's tree at s0 with the SAME hypothesis A100 priced: M_S & YES(H),
delta_pin = 2e-2, H the A100/A84 level-1 cover cell (`attempts/A238-k4-benchmark/code/load238.py`).
A238's verdict is the k5 toolkit's (A211 coarse tree, A212 gate + Lemma TUBE-LEAF/S in the class direction,
A224 Rule SNAP with the k+1 hand-off, A230 Rule EPS, A220/A221); A100's is the case-LP's.

## k3_02

| set | n | A238 DEAD | TUBE | ALIVE | A238 mean s | A100 PASS | A100 mean s | speed-up |
|---|---|---|---|---|---|---|---|---|
| A100 head-to-head | 20 | 0 | 0 | 20 | 4.3 | 15 | 388.5 | 90.3x |
| + extrapolation set | 21 | 0 | 0 | 21 | 4.0 | - | - | - |
| all cover nodes | 41 | 0 | 0 | 41 | 4.2 | 15 | 189.5 | - |

root (A84-P1 node, H = the whole interior zone): {'verdict': 'ALIVE', 'seconds': 2.3, 'n_nodes': 1, 'gate': True}

kills by rule: `{}`; gate hits 7; TRUMP-TUBE leaves 0; SNAP kills 0, hand-offs 0; max depth {"0": 42}

price: 864 cover cells x 4.2 s = **1.0 CPU-h** of geometry; the 100 % geometry leaves over (at A100's 485 s/node LP) 116.4 CPU-h; total **117.4 CPU-h** against A100's measured 290.2 CPU-h (per node 115.43 x cheaper).

## k4_11

| set | n | A238 DEAD | TUBE | ALIVE | A238 mean s | A100 PASS | A100 mean s | speed-up |
|---|---|---|---|---|---|---|---|---|
| A100 head-to-head | 1 | 1 | 0 | 0 | 16.3 | 0 | 184.3 | 11.3x |
| + extrapolation set | 0 | 0 | 0 | 0 | None | - | - | - |
| all cover nodes | 1 | 1 | 0 | 0 | 16.3 | 0 | 184.3 | - |

root (A84-P1 node, H = the whole interior zone): {'verdict': 'ALIVE', 'seconds': 337.0, 'n_nodes': 50, 'gate': True}

kills by rule: `{"EmptyBox": 17, "COUNT": 2, "FC": 1, "REACH": 6, "NOROOM-CN": 6, "NOROOM-POCKET": 1, "S-CLIP": 1}`; gate hits 2; TRUMP-TUBE leaves 0; SNAP kills 0, hand-offs 0; max depth {"0": 1, "6": 1}

price: 923 cover cells x 16.3 s = **4.2 CPU-h** of geometry; the 0 % geometry leaves over (at A100's 559 s/node LP) 0.0 CPU-h; total **4.2 CPU-h** against A100's measured 203.1 CPU-h (per node 34.28 x cheaper).

## Tier extrapolation

The measured per-class numbers are the two pilots; the extrapolation carries them by the ONE number that
predicts traction -- the class's USABLE forced cells (`results/forced238.md`), i.e. how many of its one-slot
extensions are closed on the window.

| block | classes | usable forced cells | geometry CPU-h | LP residue CPU-h | total (A238) | A100's price |
|---|---|---|---|---|---|---|
| k4 with traction (k4_03, k4_05, k4_06, k4_08, k4_11) | 5 | k4_03 3/5, k4_05 3/5, k4_06 3/5, k4_08 5/7, k4_11 5/7 | 21 | 0 | **21** | 203.1 each |
| k <= 3 (k3_01, k3_02, k3_03, k3_04, k3_05, k2_*, k1_00) | 9 | 0 for every one | 9 | 1048 | **1057** | 290.2 each |
| corners4 (shadow, no image) | 1 | 0/8 -- every extension is the OPEN k5_16 | 0 | not priced | - | not priced |

`corners4` is not run: with no usable forced cell the toolkit's rules have nothing to act on (A193 and
A84 s.7.1 independently), so a run would cost the stage-0 seconds and decide nothing -- exactly what the
k3_02 rows above measure.  For the same reason the k <= 3 row is NOT a saving: the geometry is cheap there
because it is blind, and the LP residue is A100's whole price.

**The lever the numbers point at**: five of the nine blocked k <= 3 extensions are k4 classes A55 already
killed exactly (k4_00 / 01 / 02 / 04 / 07 / 09 / 10 / 12) that simply have no full-window scoreboard row.
Emitting those rows would give each k3 class 2-5 usable forced cells and move it into the k4 row of this
table.

