# A200 notes -- what the composed/quick killer tests, and why each step is sound

Every tag: [T] proved here or in the cited proof file, [S] supported by a cited statement, [M] measured, [C] certificate.

## 1. The objects (per page, per pad)

Node = {pins P_k (the record's slack boxes, tilt 0), H (the record box), instantiated meeters F_k} at s0, normalised by
A171 multibox (container clip + mutual clip to a fixed point; `EmptyBox` = the pair leaf).  Forced slots = Theorem FC's
usable cells of the class (`classes178.forced_cells`; k5_16: BL(1,0), BR(0,1), BR(1,0), TR(0,1), TR(1,0), TL(1,0)),
each with the OPEN widened box B_p+ at the pad of the run:
  * pad `window`: lambda_max = s0/3.82, pi_0 = 0.025509 -- Theorem FC on the whole window [3.82, s0] [T, forced_corners.md];
  * pad `g1`: lambda = s0/3.861637, pi_0 = 0.006829 -- A57's G1 slab (3.861637, s0], the k5_16 pages' OWN window
    [S: forced_corners.md section 2 remark ("a tree that only claims a slab ... could use pi_i(lambda)") and section 5(a);
    slot_crowds.md line 421 (the s0 slack-core tree, delta_pin = 1e-2, Lemma B' slab (3.861637, s0])];
  * pad `zero`: lambda = 1, the unit box -- a statement at side s0 only (the endpoint); a kill here is WINDOW-PENDING
    until the slab chain of corner_seal.md section 5 covers the page's window.
A page is RETIRED by a kill at `g1` (or `window`); a kill at `zero` is recorded as s0-only.

## 2. The anonymous survivors U_p and the three millisecond exclusions

U_p := the union, over the Lemma-A1 grid cells, of A198's per-cell REACH survivors of slot p: pieces (centre rect x tilt
bin) not provably dead against every role's K' (multibox exact dead test), the container, A161's exact miss test on
B_p+ (and Theorem B's lonely clip at corner slots).  [T] Any free square DISTINCT FROM EVERY ROLE (pins, H, F_k) whose
interior meets B_p+ has its pose in U_p -- call such a square ANONYMOUS.  (A square colliding with K'(F_k) cannot be a
square other than F_k, because K'(F_k) lies inside every pose of F_k [A132]; a square at a pose dropped by the miss test
does not meet B_p+.)

cap_p = the number of anonymous meeters of p is at most
  * 0 if U_p is empty;
  * 1 if the Euclidean diameter of the union of U_p's centre rects is < 1 [T, Lemma CN: two interior-disjoint unit
    squares contain disjoint open discs of radius 1/2 about their centres, so their centres are >= 1 apart; A153];
  * 1 if its l-inf diameter is < 1/sqrt2 [T, Lemma A1, sideband.md];
  * 1 if on some guard line L (the pin lines 1/2, 1, 3/2, s/2, s-3/2, s-1, s-1/2, both orientations) the sum of the
    fixed squares' minimum OPEN chords (pins from their boxes, H and F_k over their surviving pieces; A190
    `guardlines_v5.minchord`) plus TWO copies of the minimum open chord over U_p's pieces exceeds s0 [T: the open
    chords of distinct interior-disjoint squares on a line are disjoint open sub-intervals of (0, s0)];
  * 1 if U_p meets at most one closed grid cell of side < 1/sqrt2 [T, A1; A198's rule];
  * otherwise unbounded.
The diameter is exact (rational): the convex hull of the rect corners, all hull pairs.  Borderline unions (diameter
< 1.3, l-inf < 0.95, or chord row within 1/4 of s0) are bisected two levels further (a refinement: sound).

## 3. Theorem FC's forcing (the fixed point across slots)

[T] Theorem FC: B_p+ has two DISTINCT non-pin meeters; non-pin = H, an instantiated F_k, or anonymous.  With
H_p = [H's pieces do not all provably miss B_p+], R_p = {F_k likewise}, avail_p = H_p + |R_p| + cap_p:
  * avail_p < 2 -> the page is DEAD at this pad;
  * avail_p = 2 -> every candidate IS a meeter: H is clipped to its pieces not provably missing B_p+ (and, once forced at
    several slots, to the pieces not provably missing ALL of them -- none left = DEAD); F_k likewise; and when cap_p = 1
    the anonymous meeter EXISTS (2 - H_p - |R_p| = 1 of the meeters is anonymous), meets p, is distinct from H, the pins
    and every F_k by definition, and is INSTANTIATED as a new role F with box = hull(U_p) (a superset of its pose).
The node is re-normalised (the clipped H's K' grows and clips every other reach) and the round repeats until nothing
changes (<= 6 rounds).  Then A198's joint count with the caps (an exact cover search over the (cell, jointly-reached
slot set) options: infeasible = DEAD; infeasible with H barred from p = H forced at p), the no-room leaf at >= 9 boxed
roles (A189), and -- only if all of that leaves the page alive at BOTH pads -- A199's corner SEAL chain with the clipped
H at each pinned corner whose two neighbours are forced (k5_16: BR with BR(0,1)/BR(1,0), TR with TR(0,1)/TR(1,0)),
pins + H only (dropping the F_k is a relaxation).

## 4. What the certificate is

`certs/q200_<page>.json` (g1 pad) and `certs/q200_<page>_pad0.json`: the trace -- every REACH (cell, slot, depth,
surviving fraction, number of exact tests), every UNION record (n pieces, diameter, l-inf, the best chord row and its
line, the cap and the reason), every FC-AVAIL decision, H-CLIP / ROLE-CLIP / INSTANTIATE boxes, the count results, the
SEAL runs' steps, and the seconds per step.  Replay = the same exact tests (A171 / A161 / A190 primitives) in the same
order.  [C: geometry, quick200] -- no LP, no frozen verifier.
