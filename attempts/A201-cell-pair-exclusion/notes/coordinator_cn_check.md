# Coordinator check (15:45): Lemma CN alone does not close Y0044 (g1 pad)

Scratch cn_count_y0044.py (FP.a1_compatible := A1 AND CN on the option hulls), run_page(Y0044, g1, no seal):
ALIVE in 217 s, count feasible both rounds. The cover moved off (16,17) to
  H@11 BL(1,0); F1@5 BL(1,0)+BR(1,0); free@16 BR(1,0) [2.659,2.802]x[1.470,1.651];
  free@18 BR(0,1)+TL(1,0) [2.226,2.586]x[2.244,2.597]; free@23 BR(0,1)+TR(0,1)+TR(1,0) [2.802,3.377]x[2.226,2.383];
  free@14 TL(1,0)+TR(0,1)+TR(1,0) [2.163,2.226]x[2.802,3.214].
Every pair passes CN (16-23 max distance 1.16). By hand, 16-23 looks dead only under the EXACT pair test: a square
at 16 must sit at y >= ~1.5 (P3) and reaches x 3.16; a square at 23 is pinned under P4 (top <= 2.877) and then
overlaps the first for every x. That is rule (c) of the brief -- the pairs the search actually reaches.

## PI (16:00): "Does cell 16 even clear H? are they more than 1 apart in x?"
H hull [1.659,1.799]x[1.380,1.519], tilt 82.4-90 (half-width <= 0.565); cell-16 hull [2.659,2.802]x[1.470,1.651]:
dx in [0.86, 1.143], side by side (dy <= 0.27) => the pair needs dx >= 1.0 (both upright) to 1.13 (16 at 45 deg).
Feasible only with H at its LEFTMOST pose and the cell-16 square at its RIGHTMOST pose, both upright (slack 0.14).
Then the cell-16 square (x ~2.80, y in [1.5,1.65] to clear P3) tops out at 2.15 and the cell-23 square (hull y in
[2.23,2.38]) cannot clear it (needs centre >= 2.65 or x >= 3.8). So the cover H/16/23 dies as a CHAIN of exact pair
tests, including a FIXED role (H) against a free cell -- the table must cover fixed roles' options (brief item 1).
