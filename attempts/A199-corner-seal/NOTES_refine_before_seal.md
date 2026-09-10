# Coordinator note (2026-09-10 16:20): SEAL is microseconds per piece; it fails only on COARSE TILT BINS

seal199.seal_piece is interval arithmetic (q_y, phi, x_r, the deep-regime margin, the chord) over one piece: microseconds.
On Y0491 at pad 0 A199's reach pieces carry tilt bins [0, 90] deg (phi in [0, 90]), so the deep-regime margin is
vacuously negative (-0.129) and SEAL never fires -> fallback to the pair test (36-38 s per piece). Refining ONLY the
tilt (32 sub-bins per reach piece, exact dead test per sub-piece, A161 miss test against B): 894 sub-pieces in 9 s,
deep regime on 892; x_r max 0.019 (the corner sliver). The 2 remaining sub-pieces are t in [0, 0.001] = AXIS-PARALLEL
poses (phi 89.99-90 deg) with the right edge ON the pin's side: they "meet" B only as a closed-set graze at the corner
(A161's box test is not an interior-meet test); Lemma SEAL (b) excludes axis-parallel F outright (it cannot poke past
the corner), so they are discharged by the lemma, not by refinement. RULE for the engine: bisect reach pieces in tilt
until each piece's phi interval is narrow (< ~6 deg) BEFORE evaluating SEAL; discharge t = 0 slivers by (b) with an
interior-meet test. Script: scratchpad seal_refine_y0491.py.
