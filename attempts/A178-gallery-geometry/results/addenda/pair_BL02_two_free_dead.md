# Coordinator addendum (2026-09-10 00:10): A178's node root/TL(0,0):SW+SE/pair:BL(0,2):two-free:1+2 is DEAD

PI reading of docs/residue_map/c0_Y1033_cascade.svg: "if this diagram is correct about the B_BL02 core, there is no
width-1 gap on either the top or left, and it covers the corner of TL00, so there is no diagonal green in the corner"
-> "that should be a dead node".  A178 recorded it ALIVE with kept B_BL02 = 5e-06, B2_BL02 = 1e-05 (nsub 4 / refine 2).
Re-normalised with the library (multibox at/after 13f23204, mode poly, kmode pieces, strict_container False, lonely
clip at TL for B2): nsub 8 / refine 4 -> EmptyBox(B2_BL02) in 5 s [C: the library's exact clip trace].  Geometry:
both roles have x in [0.5, 1.116] (width 0.62 < 1, so they cannot sit side by side) and B must clear P2 (top at
y = 2), so B's centre is >= 2.5 and B2's would need >= 3.5 > s0 - 1/2: the P2 | B | B2 column needs more height than
the container has (the same column A186 found as the least-overlap configuration).  A178's per-cell pass left
sliver-alive nodes wherever its setting was too coarse; the same twin node (SW+NE) carries identical numbers.
