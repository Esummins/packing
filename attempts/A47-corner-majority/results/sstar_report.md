# A47 leg (a) -- the s* exception lemma (A47-G-a1).  Verdict: PROVED (full declared parameter domain)

## Statement certified
s* = 2 sqrt2+1 is (Thm T1 + `results/t1_span_check.json`) the ONLY side in the live window
[3.82, s0] at which a flush-free thin chain can span the container; the chain is then [45,0,45]:
D_L = diamond |x-sqrt2/2|+|y-y0| <= sqrt2/2, U = [sqrt2,sqrt2+1]x[b,b+1], D_R = mirror of D_L.
LEMMA.  For every y0 in [sqrt2/2, sqrt2+1/2] (up-down symmetry half) and every b in
[max(0,y0-1), y0]  (b >= 0 since U lies in the container), there are NO 8 closed unit squares with
pairwise disjoint interiors inside [0,s*]^2 whose interiors all miss C(y0,b) -- so the s* exception
structure admits no 11-packing completion.

## Soundness chain (each link machine-checked or elementary)
1. Suppose 8 such squares exist.  Scale by lambda = 10001/10000 > 1 about the origin and shrink each image
   about its centre back to side 1: two convex sets with disjoint interiors are line-separated and
   the lambda-square has support radius >= 1/2, so the shrunk squares are PAIRWISE DISJOINT CLOSED
   unit squares, lying in [0,lambda s*]^2 subset [0,s']^2, s' = 383/100 (checked: lambda*(2 R2HI+1) <=
   s'), each still missing int(lambda C).
2. Per parameter box B, `sstar_geom.build_obstacle` builds a rational C_shr(B) = P_L u P_U u P_R and
   PROVES exactly (Fractions, no sampling) that every vertex of every piece satisfies every
   half-plane of lambda*C(y0,b) with slack >= delta = 1/256 for EVERY (y0,b) in B: the right-hand
   sides are affine in the parameter and carry sqrt2 with a fixed sign, so the worse endpoint with
   sqrt2 -> R2LO/R2HI (707106781/500000000, 1414213563/1000000000) is a certified rational bound.  So C_shr is inside
   int(lambda C) -- the relaxation only ENLARGES the container and SHRINKS the obstacle.
3. Per box a rational measure mu = sum w_i delta_(p_i) is checked EXACTLY by `verify_measure_obs.py`
   (the audited A08 branch-and-bound, integer core imported verbatim): every placement box is
   COVERED (certified mass >= 1) or EXEMPT -- a rational p with p in P (exact half-plane test) and p
   in Q(c,theta) for EVERY placement of the box (the same exact interval predicate as for atoms), so
   int(Q) meets int(lambda C) and Q is none of the 8.
4. Hence each of the 8 disjoint squares has mu >= 1: 8 <= total mass < 8, contradiction.

## Method (producer; NOT trusted -- only the verifier is)
LP  min sum w  s.t. mass >= 1 on a grid of admissible non-exempt placements (an atom counts only if
inside Q shrunk by eps = 1/128, the robustness margin); cutting plane against a fine float scan;
then a loop against the EXACT verifier -- each failing placement box is patched by ROBUST rows (only
atoms guaranteed inside for the WHOLE cell count) on a lattice ALIGNED with the verifier's own box
tree, so a failing box can never straddle two cells.  Weights rounded UP, safety factor 102/100.
The producer's exemption rule is strictly weaker than the verifier's, so it never drops a row the
verifier cannot discharge.

## Per-y0 summary (50/50 parameter boxes PASS; total mass must be < 8)
| y0 window | b boxes | max total | min total | max LP | verify boxes (max) |
|---|---|---|---|---|---|
| [0.7000, 0.8250] | 4 | 7.8412 | 6.6314 | 7.6834 | 107968 |
| [0.8250, 0.8875] | 1 | 7.1407 | 7.1407 | 7.0000 | 55490 |
| [0.8250, 0.9500] | 4 | 7.6798 | 6.1200 | 7.5260 | 52610 |
| [0.9500, 1.0750] | 5 | 7.4577 | 6.6300 | 7.3077 | 67700 |
| [1.0750, 1.1375] | 1 | 7.1409 | 7.1409 | 7.0000 | 29536 |
| [1.0750, 1.2000] | 5 | 7.1432 | 6.1200 | 7.0000 | 244238 |
| [1.2000, 1.3250] | 5 | 6.2287 | 5.1000 | 6.1053 | 134824 |
| [1.3250, 1.4500] | 5 | 6.1200 | 4.0800 | 6.0000 | 37844 |
| [1.4500, 1.5750] | 5 | 7.1400 | 5.1000 | 7.0000 | 12488 |
| [1.5750, 1.7000] | 5 | 6.6300 | 4.5903 | 6.5000 | 34566 |
| [1.7000, 1.8250] | 5 | 7.1400 | 6.1200 | 7.0000 | 19100 |
| [1.8250, 1.9150] | 5 | 7.1400 | 6.1200 | 7.0000 | 12908 |

Worst margin over all boxes: 8 - 7.8412 = 0.1588.

## Gaps / caveats
None -- the declared parameter domain is fully covered by PASSing boxes.  Final audit: all 50 certificates re-verified in fresh processes (obstacle containment proof re-run from the parameter box) and spot-checked by the independent random-placement test: all_pass = True.
