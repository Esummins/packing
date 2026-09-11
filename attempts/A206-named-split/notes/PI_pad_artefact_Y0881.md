# PI reading (2026-09-11 14:40), Y0881 leaf R.2.3s (fully hard-named): "trying to tilt F1 around to be a second meeter
# on TR01, but that would make it impossible for H to meet ... any second meeter has to have a center near the top
# edge, in a place that's already dead."

Coordinator grid (role boxes from the A206 cert): F1 [2.351,2.377]x[3.352,3.377] tilt 0-90 (0.0-0.4 in practice),
H [2.451,2.498]x[2.157,2.173] tilt 41.1-46.1.
- WINDOW pad (widened boxes): F1 UPRIGHT meets TL(1,0) (x-widening 0.04), TR(1,0) (its cell) and TR(0,1) (its
  bottom-right corner 0.01 into the pad margin); H meets BR(0,1), TR(0,1), TR(1,0) with three vertices; 42,084 disjoint
  (H, F1) pose pairs, tightest gap 0.002 between H's top vertex (2.8624) and F1's bottom edge (2.8647).  ALIVE by hairs.
- PAD 0 (unit cells): F1 has NO pose meeting all three slots -> the leaf is DEAD at s0.
=> a pad-only survivor, like Y0054 / Y0044's BL(1,0) pairs.  The lever is A199's SLAB plan: certify the named leaf at
pad 0, then the window by slabs (the pad shrinks with lambda; a 0.002 margin dies for every lambda below a threshold
near lambda1).  Record every fully named survivor's pad-0 verdict next to its window verdict on the page.
