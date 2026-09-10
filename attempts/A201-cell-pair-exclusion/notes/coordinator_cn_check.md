# Coordinator check (15:45): Lemma CN alone does not close Y0044 (g1 pad)

Scratch cn_count_y0044.py (FP.a1_compatible := A1 AND CN on the option hulls), run_page(Y0044, g1, no seal):
ALIVE in 217 s, count feasible both rounds. The cover moved off (16,17) to
  H@11 BL(1,0); F1@5 BL(1,0)+BR(1,0); free@16 BR(1,0) [2.659,2.802]x[1.470,1.651];
  free@18 BR(0,1)+TL(1,0) [2.226,2.586]x[2.244,2.597]; free@23 BR(0,1)+TR(0,1)+TR(1,0) [2.802,3.377]x[2.226,2.383];
  free@14 TL(1,0)+TR(0,1)+TR(1,0) [2.163,2.226]x[2.802,3.214].
Every pair passes CN (16-23 max distance 1.16). By hand, 16-23 looks dead only under the EXACT pair test: a square
at 16 must sit at y >= ~1.5 (P3) and reaches x 3.16; a square at 23 is pinned under P4 (top <= 2.877) and then
overlaps the first for every x. That is rule (c) of the brief -- the pairs the search actually reaches.
