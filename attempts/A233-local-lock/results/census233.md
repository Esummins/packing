# A233 -- the local lock census (one arm)

Abstract count of labelled per-meeter row lists (cells x wall rows x depth type x partner rows x holder rows):

| H (holders per meeter) | row lists (2 meeters, one arm) | four independent arms (product / 8, s > 6.243) |
|---|---|---|
| 2 | 135,000 | 4.15e+19 |
| 3 | 375,000 | 2.47e+21 |
| 4 | 843,750 | 6.34e+22 |
| 5 | 1,653,750 | 9.35e+23 |
| 6 | 2,940,000 | 9.34e+24 |

Measured on the witnesses: holders per meeter max 3, rows per meeter (wall + pair rows) max 13; 75 distinct realised signatures (cells | wall bits | partner | holders | cross-crowd holders) on 1227 corners.

Against A219 (`wall_torque.md` s.6): 2.6e11 four-corner structures with cross-corner holders, 2.3e6 CPU-days. The arm list at H = 3 is 375,000 per corner; the four arms are INDEPENDENT lists only for s > 2 + 3 sqrt2 = 6.243 (row partners), and even then the holders' balance couples them through the chains (Corollary CHAIN, NOCRIT-SEL): the local list decides LOCKED, not the residue.

Realised (cell, wall-touching) per meeter: NE:0 6, NW:0 212, NW:1 835, SE:0 186, SE:1 864, SW:0 22, SW:1 329.
Corners with every meeter wall-touching: 899 / 1227; with a meeter touching no wall: 328.
