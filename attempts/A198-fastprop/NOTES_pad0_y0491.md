# Coordinator note (2026-09-10 13:10): Y0491 dies at s0 with PAD ZERO by the PI's BR(0,1)/BR(1,0) chain (sampled)

k5_16_interior_Y0491. Cheap tests (scratchpad pairslots_y0491.py): BR(0,1)'s only free meeters are a wedge standing on
the floor left of the BR pin (centres x 2.22-2.38, y 0.53-0.75, tilts 67-90 deg), reaching the slot past the pin's
upper-left corner (the PI's diagonal condition: centre above the line through (2.877, 1) with slope 1). Every such F
also meets BR(1,0) and leaves no room for another BR(1,0) meeter (0 partners in the sample). So BR(1,0)'s second meeter
must be H. With the WIDENED boxes (pad w = 0.0255) 2,748 of 160,000 (F, H) pairs coexist -- but only through the
0.026 x 0.026 overlap of the two widened boxes at the pin's corner (F's rightmost point 2.86 < 2.877, H's lowest
vertex in the pad strip): the PI called it "not physically realizable" and at s0 it is not. At PAD ZERO (unit slot
boxes): 0 of 592,500 (F, H) pairs are interior-disjoint. => Y0491 is DEAD at s0 by: FC(BR(0,1)) -> F region (exact
reach) -> CN disc / actual-square disjointness -> H cannot meet BR(1,0) -> BR(1,0) singly met. Exact certification
= the engine chain (A198): exact reach test for F's region, the pair test H vs F with actual pieces, A161's miss test.
ON THE WINDOW the page survives only via the pad: certify at s0 with pad 0, then cover [3.82, s0] by SLABS each with
its own pad (lambda_slab - 1)(1 + sqrt2/2) small enough that the corner strip cannot host the pair (A194's slab plan).
This is likely the pattern for MANY alive a57v4 pages (the pad buys corner-strip phantoms).
