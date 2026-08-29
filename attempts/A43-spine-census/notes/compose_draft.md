# A43 compose frame (lead draft; H1 numbers in, H2 pending)

## H1 verdict (verified against results/h1/, regression PASS, Trump canary 20/20)
Bulk-kill thesis at GRAPH level: NEGATIVE. Composed EXACT k=11: 2.30e29 / 1.51e30 / 1.09e30
(vs A31 4.15e29 / 3.26e30 / 2.22e30) — the whole 2026 library buys ~x2. Only N1 (per-wall <= 3)
hard-prunes (x1.35 at k=7). Failure modes, each different and each INSTRUCTIVE for H2:
  N2/N3 existential -> vacuous below the k=11 join (witness may be a rattler);
  N5/N6 positional -> certified m_low = 0.000000 on every wall-mask window (a graph carries no
    position); yet the same field pointwise exempts 7.13% of grid cells — the kill power exists,
    the window is ~1e6x too coarse;
  N4 unproven (Maxwell) — the single biggest lever (would land ~2e25 = A31's best case) and the
    one that is not a theorem;
  N7 UNSOUND as a motif filter (Trump's graph contains a 4-cycle) — canary-confirmed over-kill.
One positional keeper: wall-flush pinned windows (t=0, wall distance exactly 1/2) get a real W1
cut — 36/2000 along-wall slabs certified exempt (m_low up to 1.437085 vs thr 1.402957, A39
resealed field, eta = 2518483/6250000). This is EXACTLY a spine-end (F-type) constraint: the only
place the field cuts is where two of three placement coordinates are pinned — which is what a
spine does to its members.
SYNTHESIS LINE FOR THE REPORT: H1's per-filter failures all reduce to "contact graphs carry no
position"; spines are positioned, tilt-coupled, wastage-chargeable chains — H1's negative is
consistent with H2's premise, not against it. H1 also hands H2 a concrete refinement: F-end
positions have a certified 1.8% exempt set; deeper W1 cuts appear wherever the chain pins
coordinates.

Trump reference spines (extracted via check_trump.py logic, wall bits L=1,B=2,R=4,T=8):
masks [3,2,6,1,1,12,8,0,0,0,4]; ss-edges (0,1),(0,3),(1,3),(1,8),(2,8),(3,7),(4,6),(4,7),(5,9),
(6,9),(7,8),(7,9),(8,10),(9,10).
x-axis (L->R) shortest chains: k=4 (0-1-8-2, 3-7-8-2, 4-7-8-2, 0-1-8-10, 3-7-9-5, 4-7-9-5, ...).
y-axis (B->T) shortest chains: k=5 (2-8-7-9-5, 1-8-7-9-5, 0-3-7-9-5, 1-8-7-4-6, ...) — the tilted
strip lives here. BOTH k=4 and k=5 realized types must survive H2's stack at s0.

## Composed statement skeleton (T-A43)
D1 + D3' + L6: if s(11) < s-hat then some FJ minimiser z at side m <= s0 satisfies
  [lambda0 = 0 global self-stress branch]  OR  z contains a spine of some type tau in S(s0)
  (H2 survivor list, D4 + reversal reduced).
Far-field program: per tau in S(s0), per floor-branch anchor a (tilt-bin x x-interval assignment),
certify completion-emptiness: no 11-packing at side <= s0 contains a spine realizing (tau, a),
except anchors whose cells meet the certified Trump box (A22/A36/A40) — those are the
endgame cells closed by uniqueness.

## What remains unproved (named)
U1 completion soundness statement (per-anchor analogue of A38 T0: anchor disjunction exhaustive
   over S(s0) x branches + lambda0=0 + thin/self-stress branches; needs writing, not hard).
U2 the lambda0=0 branch (A31 counted it at ~48% of MAIN; no spine guaranteed there).
U3 the H1/H2 join: H2 pins only the chain; the off-spine squares (and free y_i of the chain) are
   unconstrained by the census. The anchor pins contact structure ALONG the chain (A35's regime,
   minutes/anchor) but off-spine completion at s0 is A38/A42 territory where the coverage LP does
   not terminate (T_decide open) and ball-scale occupancy is worth exactly zero (A42 F2/F3).
U4 the y-slide: each spine square keeps a 1-parameter transverse family the anchor language does
   not pin — the A30 dimensional risk reappears transversally unless a second-axis argument
   (both-axes-bind case) or wastage pins it.
U5 non-shortest spines: census enumerates types of SHORTEST wall-to-wall H-paths (sound: a
   shortest path exists whenever L6 fires) — no loss, but record that the completion must not
   assume the spine is unique.

## Cost model shape (fill with measured numbers)
total = sum over survivors tau of N_anchor(tau) x C_anchor, with C_anchor in:
  - A35 semantic regime (spine contacts pinned, FJ/Farkas per stratum): 10-30 desktop-min
    (measured, A35).
  - A38 coverage regime (off-spine emptiness at s0): OPEN-ENDED (T_decide unmeasured at s0).
The program is purchasable iff the spine anchor moves off-spine completion from the second regime
into the first — the single unmeasured constant; A38-G7's 3600-s calibration node remains the
cheapest next datum.
