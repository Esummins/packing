# A33 / T3 — grain framework: definitions, provable fragments, predictions, gaps

Advisor (Fable), 2026-08-26. Incorporates the PI's slip-line refinement (message of 2026-08-26).
Companion to lemma.md (the pigeonhole) and to the T1/T3(b) measurements. Everything here is
labelled PROVED / DERIVABLE / CONJECTURE / GAP; nothing unlabelled is load-bearing.

## 1. Definitions

Fix a packing P of n unit squares in [0,s]^2. For delta >= 0, a *delta-grain decomposition* is a
partition of the squares into clusters G_1..G_r such that within each cluster all tilts lie in an
interval of width delta (mod 90 deg). The *interface graph* has a node per grain and per container
wall; two grains are adjacent if some pair of their squares is at distance < some contact radius
(we use the A31/A32 support-graph radius conventions); a grain is wall-adjacent if one of its
squares meets the width-1 band (A26: at least n-1 of the squares do, for s < 3.914 scaled
appropriately). The *misorientation* of an interface is the angular distance of the two tilt
intervals mod 90 deg (walls carry tilt 0).

*Slip lines* (PI). The square tiling of the plane has two families of full straight lines
contained in the union of tile boundaries; shearing along any one of them (translating a half-plane
of tiles parallel to the line) yields another zero-waste tiling. Triangles have three families,
rhombi two; the hexagon tiling has NONE (no straight line of the plane lies in the union of the
hexagon edges), i.e. hexagonal crystals are interlocked while square crystals shear freely.

**Lemma G0 (laminarity of zero-waste square tilings; folklore, proof sketch).** In any tiling of an
open region by unit squares of a single orientation, every interior vertex is either a 4-corner or
a T-junction, and every T-junction propagates: the abutting edge extends to a maximal straight
segment of tile boundary that either terminates on the region boundary or is a full slip line.
Hence zero-waste same-tilt regions are laminated by slip segments into rows/columns with free
longitudinal offsets. *Consequence:* the zero-waste ground state at fixed orientation is massively
degenerate (a continuum of slips), and a same-tilt/same-tilt interface, and a tilt-0 grain against
a flat wall, cost EXACTLY zero regardless of translational misfit ("coherent wetting"). This is
the exact reason A26's charged wall functional had a certified zero — recorded there as a failure,
reinterpreted here as correct physics: cost lives on MISORIENTED interfaces only.

## 2. Interface accounting (the conjectural ledger, stated precisely)

**Conjecture G1 (interface accounting).** There is a function f: [0, 45 deg] -> [0, infinity),
f(0) = 0, f(theta) > 0 for theta in (theta_min, 45 deg], increasing near 0, and a constant C
(boundary/junction correction), such that for every packing P with a delta-grain decomposition
(delta small), the uncovered area satisfies

    s^2 - n  >=  sum over interfaces I of  len(I) * f(miso(I))  -  C * (#grains + #junctions).

Status: CONJECTURE as a general lower bound. Two fragments are more accessible:

- **Wall version (partially certified already).** A single tilt-theta square meeting a straight
  wall wedge-strands at least w(theta, depth) of area, and a same-tilt ROW of squares along a wall
  strands ~ (sin 2 theta)/4 per square (corner-contact construction shows this is also achievable,
  so the constant is sharp for rows). The A23/A25 atlas contains certified interval lower bounds
  that are exactly f_wall samples: tilt-near-wall cells 0.19-0.61 per square (mid-tilt), flush
  near-upright cells exactly 0 (coherent case), best floor with tilt+depth constraints 0.1602
  (A26). DERIVABLE (v2 task): assemble the atlas into a certified piecewise-constant lower bound
  f_wall_cert(theta) >= 0 with f_wall_cert = 0 iff theta near 0 mod 90.
- **Junction values.** A25/A23's certified structures are junction samples: the adjacent 33-deg
  pinwheel pair strands 1.88, the 4-cycle pinwheel 6.55 (> the whole 3.84 budget) — a 4-grain
  vortex junction is catastrophically expensive. Consistent with G1's junction term being
  NEGATIVE-signed only for the correction, positive in reality.

**What G1 would give.** Contrapositive use at record wastage: if s^2 - n <= W (record-level), then
the total length of misoriented interface is <= W / f_min. Since a grain of k squares has interface
length >= ~sqrt(k) (isoperimetry) unless it is wall-coherent, small W forces the packing to be a
union of FEW, LARGE, mutually near-aligned grains — near-lattice structure. This is the crystal
statement the PI conjectures; the missing links are the gap list of Section 6.

**Trump as bicrystal (PROVED data, new reading).** Trump's optimum = 6 uprights wetting the walls
(their certified wall charge is 0) + 5 squares at the COMMON tilt theta* = 40.18 deg absorbing the
incommensurability; the certified total wall charge 0.8672 (A26) is carried by the tilted grain's
wall contacts; theta* is then the optimal misorientation of a single internal interface, selected
by minimising total f-cost subject to fitting 11 squares. The campaign's certified numbers are
consistent with this reading at every point we checked (Section 1, Section 2 samples).

**Erdős–Graham as literal grains (literature anchors, verified by T3(a) — docs/literature.md
section F).** The E-G construction (upright bulk + long thin strips of slightly tilted squares
near the boundary, recursively) is exactly a grain packing: interfaces of length ~ x at small
misorientation theta_i, cost per length ~ theta (linear near 0), and the 7/11 exponent is the
optimum of the resulting trade-off. Current state (see F1-F11): W(x) = O(x^{3/5}) is the best
upper bound, but Chung-Graham 2020's proof is flawed (Arslanov-Bui erratum, the W5 term); the
first correct proofs are Bui arXiv:2508.04603 and McClenagan arXiv:2602.01484 (2025-26). Lower
bound still Roth-Vaughan Omega(x^{1/2}); the 1/2-vs-3/5 gap is fully open ($1000 CG bounty).
No LP/fractional/SDP treatment of wastage asymptotics exists in the literature: the eta(n)/rho(n)
measurements of this attempt are virgin territory.

**Bui's near-upright theorem = the asymptotic grain-alignment statement (F: arXiv:2504.09489).**
Bui proves W = Theta(W*) where W* is the minimal wastage over packings with ALL tilts <= 1e-10:
near-upright grains suffice asymptotically up to constants. In the language of this note: the
optimal misorientation budget tends to 0 — asymptotically the incommensurability is absorbed by
COHERENT (slip-degenerate, Lemma G0) near-upright shear, and hard-tilt grains like Trump's
theta* = 40.18 deg block are a SMALL-n phenomenon. This is a rigorous one-sided version of the
crystallization conjecture (G3): it does not say every optimal packing is near-upright, but it
says near-upright ones are within a constant factor of optimal — the f-cost of misoriented
interfaces buys at most O(1) leverage at large x. Consequence for the pigeonhole programme: at
large n the tight varieties should concentrate on the near-upright sheet (prediction P3) not
because tilts are forbidden but because the guard fields need not spend mass guarding against
them beyond a constant.

## 3. The pigeonhole is the LP shadow of the ledger

Lemma A33.1(ii): escaped guard mass <= eta(s). The Lebesgue measure on [0,s]^2 is feasible for
(F1) with total s^2 (every contained unit square has area exactly 1), so ALWAYS

    0 <= eta(s) <= s^2 - n         (eta is at most the geometric wastage),

and eta/(s^2-n) =: rho in [0,1] is the *forcing efficiency* of the measure method at (n,s):
rho = 0 means the LP sees the packing exactly (total forcing: every square covers exactly mass 1,
zero escape); rho = 1 means the LP knows nothing beyond the area bound. Known anchors:
tau*(3.7071) = 10.000 exactly (results.md Thm 1 remark (iii)) gives **eta(10) = 0, rho(10) = 0 at
the true optimal side of n = 10** — the pigeonhole forcing is TOTAL there. The gate question of
A33 is rho(11) at s' = 3.877084; T1 measures it, T3(b) measures the n-trend.

## 4. Predictions (PI, quantified for the compute agents)

P1 (commensurability dips). eta(n) and rho(n), measured at the record/optimal side s_n, dip at
crystal-family n (n = m^2, s = m; also the m^2+m family) and peak at maximally incommensurate n.
CORRECTED (T3b, eta_n_meta.json — the first draft here claimed tau*(m) > m^2 strictly via a
lattice-vertex argument; that argument only rules out the naive ATOMIC lattice field, not all
measures): the near-uniform measure of density (1-2eps)^{-2} is feasible for the eps-shrunk
constraint, so tau_eps(m) = m^2 up to 4 eps m^2 (<= 6.4e-3 at m = 4); measured tau = 4.000000 /
9.000000 / 16.000000 at s = 2 / 3 / 4 — the crystal dip is TOTAL, eta(m^2) = 0. Second
correction (same file): the closed-square tau* is degenerate at commensurate sides (at s = 2 one
atom of mass 1 at (1,1) meets every closed unit square, tau_closed = 1 — still a valid Theorem-1
certificate for s(4) >= 2, but useless as an eta gauge because the packed squares TOUCH and all
share that atom: lemma.md remark (d) in action). All eta values in this attempt therefore use
the eps-shrunk tau; any eps-shrunk-feasible field is closed-feasible, so every pigeonhole
statement remains valid verbatim. Measurement set: n in {4, 9, 16} (crystal)
vs {5, 10, 11, 18, 26, 41, 66} (record sides from the A11/Ellsworth table).

P2 (interface constant). In record packings, wastage per unit interface length converges. Honest
caveat recorded up front: per unit CONTAINER-perimeter length, c_n = (s_n^2 - n)/(4 s_n) -> 0
asymptotically by Erdős–Graham (W = O(x^{7/11}), sublinear), so the PI's "constant" can only be
(a) a finite-n plateau in c_n visible for n <= 100, or (b) constancy per unit length of actual
GRAIN-BOUNDARY (interface) length, which grows slower than the perimeter in the E-G regime. T3(b)
fits c_n for all records n <= 100 (cheap, data-only) and reports which reading survives.

P3 (sheet concentration). At high n the multi-field tight variety T_cap (lemma.md) concentrates on
lattice-aligned sheets: {|t| <= t0} (near-upright) x (near-wall bands) in (t, cx, cy)-space, plus
low-volume tilted components. Testable at n = 18 if T1's machinery converges fast enough; else
recorded as the follow-up experiment.

## 5. What is provable TODAY with the pigeonhole (conditional structure theorem, schema)

Given m certified fields mu_j at side s0 (exact totals 11 + eta_j, feasibility PASSed by the
A08-semantics verifier), and a certified exclusion cover E with min-coverage > 1 + eta_j on each
box of E for the respective field: **every 11-packing at any side s0' < s0 has all 11 scaled
placements in P_{s0} \ E** (Lemma A33.3 + the map semantics of lemma.md). If the uncovered region
is contained in (near-upright sheets) u (wall bands) u (small residue), that IS a machine-checked
Stromquist-Thm-3-type structure theorem at side s0 — obtained from feasibility alone. T2 measures
whether the residue is small at n = 11; the grain conjecture says it shrinks with n.

Composition (new kill test, free to state): at any case-tree / critical-point-program node fixing
k squares in parameter boxes B_1..B_k, if the certified box lower bounds satisfy
sum_i min_{x in B_i} mu(Q(x)) > k + eta, the node is DEAD (Lemma A33.1(i) on the k-subfamily).
This "tight-sum cut" is strictly stronger than killing via any single box and costs k interval
evaluations against an existing field — relevant to the paused A29 tree and the I-L12 cell
program. (Not yet implemented; noted for the registry.)

## 5b. P2 measured (advisor, in-context, from attempts/A11-abinitio-sweep/records.json; full table
in records_wastage.txt)

For all records n = 1..100: W_n = s_n^2 - n, c_n = W_n/(4 s_n). Results:
- Peak envelope of c_n is FLAT: max c_n over n in [5,20]/[21,40]/[41,60]/[61,80]/[81,100] =
  0.2727 / 0.2711 / 0.2695 / 0.2698 / 0.2670. The PI's constant exists in the records:
  c* ~ 0.26-0.27 per unit of container perimeter at incommensurate n, no decay through n = 100 —
  the E-G sublinear regime has not begun (reading (a) of P2 confirmed at these n; reading (b)
  untested, needs per-record interface lengths).
- Commensurability: c(m^2) = 0; W(m^2 - 1) = 1.0000 exactly for every m <= 10 (side-m grid minus
  one square is the record); peaks at m^2 + 1 with W(m^2+1) = 2.33, 3.74, 4.86, 5.60, 6.54, 7.33,
  7.86, 8.93 for m = 2..9, i.e. W ~ 1.1 m = linear in the perimeter: the record mechanism through
  n = 100 is Trump-like (bulk grid + one tilted grain absorbing wall incommensurability), not E-G
  recursive strips. P1's dip/peak structure is confirmed at the level of W and c; the LP-level
  version (eta(n), rho(n)) is T3(b)'s measurement.

## 6. Gap list (honest)

G1. No grain-decomposition existence theorem: "every packing admits a delta-grain decomposition
    with controlled interface graph" is a definition-chase for clustering by tilt, but the
    INTERFACE LENGTH lower bounds need geometric separation lemmas not yet written.
G2. Interface cost f: only wall samples are certified (A23/A25/A26 atlas); the grain-grain version
    with slips quotiented out is unproven. The slip degeneracy (Lemma G0) means any proof must be
    translation-invariant along the interface — the A26 charging failure shows pointwise charging
    cannot work; the charge must be per-interface, not per-square.
G3. Crystallization ("near-optimal => large grains") is the analog of Theil-type crystallization
    theorems for disks, and squares are HARDER in one precise sense: the ground state is
    continuously degenerate (slips, Lemma G0), so energy-rigidity arguments that pin disks to the
    triangular lattice have no direct analog. Any partial result here (even for packings with
    wastage o(x) forcing 1-o(1) of squares into one tilt class) would be new. Related certified
    negative: quantitative tilt forcing at n = 11 is capped at ~2 squares (A26) — at SMALL n the
    crystal statement is genuinely weak; the conjecture's content is asymptotic.
G4. eta(n) at the true optimal side is only measurable where s(n) is known (n <= 10, 4-square
    families); elsewhere we measure at RECORD sides, which upper-bound s(n) — the measured eta(n)
    is then an upper bound for the eta at the true side (tau* is increasing in s). Trend
    conclusions must carry this asymmetry.
