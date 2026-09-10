# Coordinator note (2026-09-10 12:05): the prototype's "quadrants" are WRONG as a relative-region split

quadprop_y0054.py split the meeter window into four cells around the SLOT CENTRE (1.52, 0.51 for BL(1,0)). The
survivors it reported in every quadrant are poses of a square sitting essentially IN the slot (drawn poses at
(1.51, 0.50), (1.55, 0.51), (1.51, 0.54), (1.71, 0.56)) -- the slot square itself, which no core collides with --
not squares approaching from that side. docs/residue_map/y0054_quadrants.svg shows it.

The relative regions the PI means are, for a slot on the floor: the NEAR-SIMPLE region (centres within reach of the
slot's own pose; a square there is the slot square, handled by the near-simple / NoFam logic and the H-pair case),
and the OUTSIDE approaches: from the right (centre x > slot right edge - overlap), from above-left / above /
above-right (centre y > slot top - overlap), from the left (pinned here). A meeter "from quadrant Q" must have its
centre OUTSIDE the near-simple region on Q's side. Define the cells that way (and for the k0 corners use the
sideband 2x2 grid at c, Lemma A2), then run the exact dead test per cell. The chord-row and forced-clip steps stand.
