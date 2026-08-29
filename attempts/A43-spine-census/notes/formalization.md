# A43 formalization — H1 filter soundness ledger + H2 spine-type census (Fable lead, 2026-08-28)

Container side s0 = 969271/250000 = 3.877084 (all filters must be valid for EVERY packing at side
<= s0; monotone/outward interval arithmetic throughout; sqrt2 = 1.41421356... always rounded in the
sound direction per use). Budget B0 = s0^2 - 11 = 4.031780343056 (exact rational available).
Target family: candidate-jammed structures per docs/proofs/drain_lemma.md + structure_lemmas.md.

## Part 1 — H1 filter ledger (each: statement, provenance, class, where it composes)

Class legend: EXACT = certified theorem valid for all packings at side <= s0, may be used as a hard
prune. EXACT-EXISTENTIAL = certified but existential over the 11 squares — VACUOUS on a loaded core
of k < 11 (the witness may be a rattler); bites only at the k = 11 join; report as a column, fold
into the composed count only in the k = 11 projection. CONDITIONAL = rests on an unproven premise;
report-only, both counts. APPROX = kills configurations only in specific certified cells; as a
graph/decoration filter it over-kills (realizability caveat); report-only, both counts, NEVER in
the composed exact count.

| id | filter | class | level |
|----|--------|-------|-------|
| N1 | per-wall <= 3: at most 3 squares touch any one wall. Proof (A31 report, elementary): two same-wall touchers have centres within sqrt2/2 of the wall and >= 1 apart, so along-wall coords differ >= sqrt(1-(sqrt2/2-1/2)^2) = 0.978318; along-wall range is s0-1 = 2.877084 < 3*0.978318 = 2.934954, so at most 3 wall-degree per wall node. | EXACT (promote A31 soft bit 16 to hard; new ablation row) | L0 |
| N2 | A38.1 interior occupancy at s0: every 11-packing at side <= s0 has a square with centre in Z = [11/10, 694271/250000]^2 (exact cert, A38 results/root_s0.json). A wall-touching square has centre within sqrt2/2 = 0.7071 < 1.1 of that wall, hence outside Z. => a k=11 core in which ALL 11 squares touch walls is DEAD. | EXACT-EXISTENTIAL (column: fraction of survivors with all wall masks nonzero, per k; hard only at k=11) | L0 column + k=11 join |
| N3 | A21 THM3 orientation: every 11-packing at side <= 3.88 (a fortiori <= s0) has a square with tilt in [0,18]u[27,63]u[72,90] deg mod 90 (cert thm3_orientation_pm18, PASS, total 10.974832 < 11). Bites only if ALL 11 tilts are forced into (18,27)u(63,72). Necessary condition at L1: no zero-pinned tilt class (any wall-flush edge satisfies THM3 for free). | EXACT-EXISTENTIAL (L1 column: fraction of decorations with no zero-pinned class = the k=11-join-relevant set) | L1 column + k=11 join |
| N4 | flush-mandatory: needs Maxwell row count m >= 3k+1, which the structure_lemmas ledger marks SOFT (NOT a theorem — degenerate structures can jam with fewer independent rows) and which A32-H1 explicitly resolved as NOT usable. NOTE: the A43 brief lists this as certified; provenance check says it is NOT. Applied as labeled CONDITIONAL columns only: L0 `2E >= 3k+1` (flush-possible), L1 `#flush >= 3k+1-E`. | CONDITIONAL | L0+L1 columns |
| N5 | W1 tight-variety (A33.1/A33.2 + sealed guard field): a placement Q with mu(Q) > 1 + eta lies in NO 11-packing at side <= s0 (strict side: lambda-scaling per A33.2 Remark (d); repo s0 > algebraic s-hat so this covers packings at side <= s-hat). Field: prefer A39 resealed (results/p2b, eta_cert = 0.402957280, standalone PASS), else A33 sealed (eta 0.425400). Machinery: A38 code/fieldcut.py mlow_box / mlow_box_exact (one-sided conservative). Kill: square window with certified min coverage > 1 + eta. L0 windows per wall mask (9 boxes x full tilt); L1 wall-flush pins (t=0, wall distance exactly 1/2). | EXACT (expected ~0 bite at these window scales — MEASURE, that is the point) | L0+L1 |
| N6 | W2 pair tight-sum (A33.1(i), |I|=2): two placements Q1, Q2 of one packing satisfy mu(Q1)+mu(Q2) <= 2 + eta. Kill a contact edge if mlowA + mlowB > 2 + eta over the pair's windows. | EXACT (expected ~0 bite; measure) | L0+L1 |
| N7 | wastage motif kills: (a) A23 pinwheel 4-cycle at s' — dead area 2816/625 = 4.5056 > B0, certified for the REALIZED 33-deg 4-cycle placements (A24.W boxed version (c_i +- 0.03) x [30,36] deg is at 3.84 only); (b) A25 k=3 mid-tilt — three squares in [1.20,1.35]^2 x [15,18] deg + its two 90-deg rotations, dead 4.2070 > B0 at s' (exact fractions; single-atlas cells, valid at s'). As graph/decoration filters these OVER-KILL: a 4-cycle subgraph or 3 mid-tilt squares need not sit in the killed cells. Columns: (i) contains any square-square 4-cycle; (ii) 4-cycle whose 4 links are all CE with a tilt-class assignment compatible with a common (18,45) band; both APPROX proxies. A25 pair-atlas values exist at 3.84 only and 54/330 pair cells are realisable:false — do not use pair cells at s0. | APPROX (report both counts; never in composed exact) | L0+L1 columns |
| N8 | band count (A26.1/A28.*): at most ONE square has wall clearance R = d(centre, nearest wall) - h(theta) >= w for any w > (s0-2)/2 = 0.938542. Inert at L0 (mask-0 boxes cannot certify avoidance). 0-cost column, recorded so nobody re-spends on it. | EXACT, inert here | — |

Composed-EXACT count = A31 MAIN ∧ N1 ∧ N5 ∧ N6 (kill columns), with N2/N3 folded in ONLY at the
k = 11 projection (state the join explicitly: a full structure = core of k loaded + (11-k)
rattlers; existential filters see all 11). Conditional/approx variants reported beside it.
Regression duty: with the new filters OFF, every A31 number must reproduce EXACTLY.
Canary duty: Trump's structure (code/check_trump.py extended) must pass every EXACT filter.

## Part 2 — H2 the spine census (formal)

### Definition (spine, spine type)
Setting: minimiser z-hat at side m <= s0, FJ certificate per D3', lambda0 > 0 branch, binding axis
x WLOG (D4). By L6 some H-component touches W_left and W_right. A SPINE is a shortest H-path
q_1..q_k with a loaded left-wall edge at q_1 and loaded right-wall edge at q_k; consecutive pairs
share an active loaded contact. Squares distinct; k >= 2, and k = 2 impossible (below). The
lambda0 = 0 branch (global self-stress) is NOT covered by this census — named residual, same as
A31's lam0 branch.

SPINE TYPE tau = (k; e_L, e_R; t_1..t_{k-1}) up to reversal symmetry (i -> k+1-i, L<->R, CE
direction flip), where
  e_L, e_R in {F (wall-flush), C (wall-corner)};
  t_i in {FL (flush), CEab (corner of q_i on edge of q_{i+1}), CEba (reverse), CC (corner-corner)}.
Tilt-class structure is DERIVED: gauge phi_i = theta_i mod 90 in [0,90);
  F end     => phi = 0 exactly;   C end => phi in (0,90);
  FL        => phi_i = phi_{i+1} (merge classes);
  CEab/CEba => phi_i != phi_{i+1}, sign branch (< or >) enumerated INSIDE feasibility
               (A31 level1 gauge derivation; parallel corner-on-edge degenerates to flush);
  CC        => no tilt coupling; wedge condition below.
Feasibility of the tilt subsystem: strict digraph on classes acyclic, zero class (if any) has
in-degree 0 (A31 level1, exact for the tilt subsystem).

### Certified span arithmetic
h(phi) = (cos phi + sin phi)/2 in [1/2, sqrt2/2] is the axis support half-width at any tilt.
End identities (EXACT): x_1 = h(phi_1), x_k = s0 - h(phi_k), so
   SPAN: sum_i dx_i = x_k - x_1 = s0 - h(phi_1) - h(phi_k),
which is s0 - 1 = 2.877084 for F-F, in [s0 - 1/2 - sqrt2/2, s0 - 1) for F-C, and
in [s0 - sqrt2, s0 - 1) for C-C ends. Containment: x_i, y_i in [h(phi_i), s0 - h(phi_i)].

Per-link certified dx intervals (delta = c_{i+1} - c_i; unit vector u(a) = (cos a, sin a);
enumerate the finite branch choices, take the union interval, outward-rounded; dy identical by
symmetry with cos->sin):
* FL, common tilt phi, edge normal at psi in {phi + 90m : m = 0..3}:
    delta = u(psi) + t*u(psi+90), t in [-1, 1] (closed hull; |t|=1 is the CC-degenerate limit).
    dx = cos psi - t sin psi  => dx in [cos psi - |sin psi|, cos psi + |sin psi|].
* CE (corner of a on edge of b), b's outward edge normal psi in {phi_b + 90m}:
    contact p = c_b + (1/2)u(psi) + u*u(psi+90), u in [-1/2, 1/2];
    c_a = p + (sqrt2/2) u(th_d), th_d = phi_a + 45 + 90j, with support condition
    |th_d - psi| < 45 (mod 360)  [equality = flush degeneracy; th_d = psi => phi_a = phi_b mod 90,
    excluded]. delta = (1/2)u(psi) + u*u(psi+90) + (sqrt2/2)u(th_d) for the a-on-b direction
    (negate for b-on-a). The sign of (th_d - psi) is the CE sign branch and fixes sgn(phi_a - phi_b).
* CC: c_a = p + (sqrt2/2)u(th_a), c_b = p + (sqrt2/2)u(th_b), th_x = phi_x + 45 + 90j;
    delta = (sqrt2/2)(u(th_b) - u(th_a)) ... (sign: delta = c_b - c_a); NECESSARY certified
    relaxation of interior-disjointness: cos(th_a - th_b) <= 0 (equivalently |delta| >= 1).
All consecutive |delta| in [1, sqrt2] (L5a) — implied by the parametrizations above but asserted
as a redundant check.

k range: k >= 3 CERTIFIED (max |dx| per link is sqrt2, span >= s0 - sqrt2 = 2.462870 needs
ceil(2.46287/1.41422) = 2 links... => k-1 >= 2, k >= 3; F-F needs k-1 >= ceil(2.877084/1.41421)
= 3, k >= 4). Upper bound: k <= 11 (trivial, exact). Enumerate k = 3..7 exhaustively with the
full stack; k = 8..11 by DP count under C0-C2 (report; expected span-slack).

### Constraint stack (per type; branch-and-prune; a KILL must hold for EVERY realization in the
branch, a type SURVIVES iff some branch survives at floor resolution)
C0 span + containment + consecutive-distance (EXACT interval arithmetic).
C1 tilt-coupling feasibility (EXACT, A31 level1 semantics).
C2 joint tilt-window x span propagation: branch tilt classes into bins (3 deg, outward-rounded),
   propagate per-link dx interval unions, require sum dx = span identity solvable; plus the
   y-column capacity lemma (EXACT, same proof as N1): any subset S of spine squares whose
   x-realizations ALL lie within a window of width Delta < 1 satisfies
   |S| <= 1 + floor((s0-1)/sqrt(1-Delta^2)); kill a branch only if violated for every realization
   (use interval hulls; conservative).
C3 per-link tight-variety: kill branch if some square's reachable (t, cx, cy) window W_i has
   certified mlow_box(W_i) > 1 + eta (fieldcut machinery, threshold as exact rational; state field
   used). NOTE y is unconstrained for interior squares — expect ~0 bite; MEASURE and say so.
C4 interface wastage: per branch, per square, A25 atlas_single_3.877084.json lookup over W_i
   (query.py D4 semantics; uncovered => 0); sum over squares whose region lists are pairwise
   disjoint (query.disjoint_regions; drop squares greedily to restore disjointness — conservative);
   kill if certified sum > B0. Also REPORT per-surviving-type the wastage FLOOR (min over branches
   of the certified sum) — composition data even where it does not kill.
C5 A21 THM3 column (existential; report only: types whose every branch forces all k tilts into
   (18,27)u(63,72) — relevant only at the k=11 join).
C6 band-count column (N8 semantics; expected inert, 0-cost).
Ablation order: raw types -> C0 -> +C1 -> +C2 -> +C3 -> +C4 (report per-k table + which
constraint did what).

### Canaries (MANDATORY)
1. Trump at s0: extract the contact graph + wall contacts from certs/trump11_certificate.json
   (check_trump.py logic), identify ALL shortest wall-to-wall paths on both axes, type them; every
   realized type must SURVIVE the full stack at s0. The tilted 5-strip type must be among them and
   survive. Any kill of a realized Trump type = unsound filter, STOP and report.
2. A37 valleys: for each atlas_final.json entry with class RIGID/VALLEY/VALLEY-MARGINAL (the 10
   attractors), extract the spine type(s) from its audited contact table at its own s value; run
   the stack AT THAT s (the code must be parametrized by s). Each must survive at its own s.
   Whether it also survives at s0 is separate INFORMATION (their s > s-hat), reported honestly.

### Per-survivor completion-cost design estimate (NO completion runs)
Anchored A35-style semantic cells: anchor = the spine type + a tilt-bin + x-interval assignment
(the branch cells above at floor resolution). Estimate per survivor: N_anchor = number of
surviving floor branches; per-anchor completion = A35 steady-state cost 10-30 desktop-minutes
(measured, A35 final_report cost table) IF the anchor pins a contact structure; the unpinned
transverse coordinates (free y_i, the 11-k rattlers) are the unpriced dimension — flag with A35's
semantic-cliff constant R* ~ 0.00586 as the honest scale gap. Deliver the formula + per-survivor
numbers, clearly labeled DESIGN ESTIMATE.
