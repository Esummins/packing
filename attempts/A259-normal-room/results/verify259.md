# verify259 -- the 9 MISMATCH rows of the first verifier run (2026-09-21) and their resolution

The first run of `verify259.py` on all 81 cells ended `bad = 9`: nine CERT leaves in cells 7_7, 7_8, 8_7, 8_8
(b, a' in [0.875, 0.9375], both tilts in [37.5, 45] deg; tree margins -0.255 .. -0.292) that the independent binning
(0.5-degree bins offset by a quarter degree) reported FAIL with the same margin 0.9496 on every row.  **It was the
verifier's bin, not a hole in the tree, and not the +-45 wrap:** isolating bins shows the single offending bin is the
one centred at psi = 0 (half-width 0.25 deg).  Its kernel is axis-aligned with half-side 0.5/w(0.25 deg) = 0.49783, so
its axis footprint is 0.9957 < 1, whereas the tree's bins [-1, 0] and [0, 1] deg use kernels tilted by 0.5 deg whose
axis extent is exactly 0.5/w(0.5 deg) * w(0.5 deg) = 0.5 (footprint 1.0000).  On these boxes the CORES are shrunk by
about 0.087 per side (large tilts, box radius 0.031 in b and 0.022 rad in phi), so the over-approximated corner gap on
the floor is between 0.9957 and 1.0000 wide: the verifier's slightly smaller axis-aligned kernel slides in against the
floor in the right half (giving (q - O).(-v) - 1/2 = s/2 - 0.4978 - 1/2 = 0.9496, the constant value seen), the tree's
does not.  Both covers are sound over-approximations of the pocket; the verifier's is the weaker one at psi ~ 0.  The
EXACT region search with the true four squares (hard feasibility, `pair259.pair_margin`) at the 16 corners of the
worst box over psi in [-1, 1] deg gives miss-margin **-0.4557**: no free square misses O there, so the tree's CERT is
right.  Fix (in `verify259.py`): a leaf the independent cover fails to re-certify is bisected by the tree's own rule
(depth <= 8) and every piece must be CERT / PRUNE under the independent binning -- still an independent
re-certification, and the only thing that now counts as `bad` is a piece failing at depth 8 (or a tiling failure).
The offending box re-certifies in 0.3 s.  The verifier was rerun on all 81 cells detached (`run259.sh verify`);
`finish259.sh` commits `results/verify259.json` when it lands; the certificate counts only with `bad = 0` there.
