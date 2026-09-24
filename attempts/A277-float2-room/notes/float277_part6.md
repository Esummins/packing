# part 6 -- the certificate: design, bench, price  (code/cert277.py; results/bench277_float2.json, bench277_jam.json)

## 6.1 Kernel (A259's method, room259 / cert259 imported)
Parameters per obstacle: F floater (h_u, h_v, theta), H floor toucher (a, alpha); families 'float2' = F F (6) and
'jam' = H F (5).  Over a box: each obstacle -> its CORE (box-centre pose shrunk to half-side 1/(2 w(r_theta)) - rho,
rho = r_hu + r_hv + r_theta the |.|_1 bound on the centre motion -- inside the true square at every parameter of the
box); the free square's tilt binned in 1-degree bins (A237 kernel); C_bin = container (-) K minus U (core (+) K) contains
every admissible centre for every configuration of the box and every tilt of the bin; the BL-sector part of C_bin is
cut by the half-plane (q - O).n_mid >= 1/2 - D s/sqrt2 (the bin's angular slack D on |q - O| <= s/sqrt2), union over
the 90 bins = R_over.  Verdict: CERT-ROOM if R_over is empty, CERT-CAP2 if diam(conv R_over) < 1 - TOL (part 3.3 +
`cap2_of_diam`), else split.  PRUNE only when an obstacle's OUTER approximation misses the open box or two cores
overlap (both mean: no configuration of the box is a FLOAT2 / JAM corner).  Side SMAX = 3.8771 (monotone, A259 s.2.3).
Soundness direction as A259: the pocket is over-approximated, the diameter is that of a superset.

## 6.2 Bench  [M, 12 points]
| family | points | CERT at the point (ROOM / CAP2) | certifiable box radius (weighted: tilt x2) | s per point |
|---|---|---|---|---|
| float2 (C, D) | 6 (the witness + 5 random FLOAT2 corners) | 6 (4 ROOM, 2 CAP2) | 1/16 median; 1/128, 1/1024 (the witness: diam 0.936, margin 0.064 eaten by 6 shrinking cores) | 0.21 |
| jam (A, C)    | 6 random JAM corners (A and C meet the box) | 6 (5 ROOM, 1 CAP2) | 1/32 median; 1/16 | 0.19 |
About 0.02 s per box.  No point FAILED as a point: on every sampled corner the two box meeters alone leave a BL-sector
centre region of diameter < 1 (mostly empty).  Twelve points prove nothing; they say the statement is not obviously false.

## 6.3 Price
6-parameter tree at the median radius 1/16 (weighted): a leaf covers 2^-4 in each position coordinate and 2^-5 rad in
each tilt: leaves ~ (16)^4 (1.571 x 32)^2 = 1.7 x 10^8 if uniform -- an adaptive tree spends far less on the interior
(ROOM boxes certify at radius 1/8 - 1/4) and far more near the thin places (the witness-type region: radius 1/1024 in
six coordinates is 10^9 leaves by itself).  Honest range, by A262's `jam` experience (7 parameters, 15-500 CPU-h,
heavy tail): **30-1000 CPU-h** for 'float2'; **3-100 CPU-h** for 'jam' (5 parameters, median radius 1/32).  Both
over the 20 CPU-h line: **not launched** (the lab is at its ceiling; ONE heavy python -- the search of part 7 -- runs).
The thin places are exactly the P1-degenerate ones (a floater about to touch: h_v(D) -> 0), where the statement is
still true (the limit is a JAM corner, whose ROOM is [M] -0.06) but the cores vanish; a P1-aware PRUNE (a cell where
some wall cell meeting D is provably free of C -- A261's J as an interval test) would remove them and is the first
thing to add before any launch.
Route (S2) for comparison: BL-CAP-2(T_u(C), T_v(D)) is 4 parameters (b, theta_C, a, theta_D) -- pair3's price class
(~3 CPU-h) -- but it closes only the sub-case of part 4.2 (both blockers serve their far boxes) and still needs the
5b tree's two capped cells and `pair3`.  Not launched either: a certificate of a sub-case is not what 5d lacks.

## 6.4 Verifier (design, not written)
As verify262: re-derive every CERT leaf with an independent 0.5-degree binning offset by a quarter degree, the dyadic
tiling identity per root cell, PRUNE leaves re-checked from the outer approximations, OPEN listed never counted; for a
CERT-CAP2 leaf recompute the hull diameter from the independent binning.  ~30 ms per leaf.
