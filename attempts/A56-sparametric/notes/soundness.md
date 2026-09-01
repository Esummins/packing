# A56 T1 — parametric soundness of the stratum-kill library (Fable, 2026-08-31)

Window W = [s_lo, s0], s_lo = 191/50 = 3.82, s0 = 969271/250000 = 3.877084, δ_max = s0 − s_lo =
14271/250000 = 0.057084. Labels as in A53: [T] theorem, [S] soundness statement, [C] conjecture.
The library L = the 52 PASS certificates (A53 certs_wip: 32 k=6 + 18 k=5; A54 certs: k6_23,
k5_13), each of format case-measure-certificate-v1 with empty `nofams`.

## P0 [T] — census stability on the CLOSED window (endpoint check)

A53 L2(iv) is stated on the open (3.82, 3.9); the four predicate families it needs are verified
at both endpoints of W: s ∉ Z; frac(s) ∈ (3/4, 1) (frac(191/50) = 41/50 > 3/4); s < 4 (offset-3
exclusion); cross-family conflict predicate i+j ∈ {2,3} (|s−1−(i+j)| < 1 ⟺ i+j ∈ {2,3} needs
s−1 ∈ (1, 2)∪... : at s = 191/50, s−1−2 = 41/50 < 1 and s−1−3 = −9/50, |·| < 1; i+j = 1 gives
91/50 > 1). Hence the slot COMBINATORICS — 6 slot values per axis, anchor uniqueness, the 1110
Young 4-tuples / 163 D4 classes, the k-census, and the downward-closure cap logic of L5 — are
constant on all of W. Only slot POSITIONS move: L-family {1/2, 3/2, 5/2} fixed, R-family
{s−1/2, s−3/2, s−5/2} affine in s. So for every s ∈ W the stratification is THE SAME list of
strata, with per-s pin positions slots_S(s), and the composed target statement is well-formed:

  (KILL_S over W)   for every s ∈ W, no packing of 11 pairwise interior-disjoint closed unit
  squares in [0,s]² contains axis-aligned unit squares centred at ALL k slots of slots_S(s).

Once KILL_S holds over W for the 33 k=6 classes, the cap (L5 corollary — purely combinatorial,
s-free by P0) gives: every packing at every side s ∈ W has k(P) ≤ 5; the transferred k=5 kills
then remove those 19 classes for every s ∈ W as well.

## P1 [T] — enumeration of what depends on s in a kill certificate

| object | s-dependence | form |
|---|---|---|
| container / admissible band | [w/2, s−w/2] per axis | monotone in s |
| budget b = 11 − k, n = 11 | none (P0) | constant |
| core (pin) CENTRES | anchor of the slot's corner | kx(s) = αx + βx·s, βx ∈ {0,1}; αx ∈ {±1/2, ±3/2, ±5/2} |
| core half-side a, tilt tm | none (containment core ⊂ pin is translation-invariant) | constant |
| atom positions | NOT determined by the s0 file — a modelling CHOICE (P3) | p_i(s) = (αx_i + βx_i·s, αy_i + βy_i·s), β ∈ [0,1] ∩ ℚ |
| atom weights, total | kept constant; "total < budget" is then s-free | constant |
| nofams | none in L (all empty) | — |
| relative motion | opposite-anchored objects (pins, atoms, walls) move apart by up to δ_max = 0.057084 as s ↑ | the sole hard part |

The relative motion is the anchored-diagram effect the brief flags: a BL-anchored pin is fixed
while a BR/TR-anchored pin, a wall-anchored atom, and the right wall each translate by
(β_diff)·(s−s_lo); coverage of placements in the corridors BETWEEN differently-anchored
structures is the only thing that can break as s varies.

## P2 — the three candidate formulations, decided

### (b) monotonicity: one honest theorem, the general case REFUTED AS A PROOF ROUTE

**M1 [T] (single-corner transfer is free).** Let S be a pin-set whose slots all anchor to ONE
container corner (WLOG BL after D4). If KILL_S holds at s0 then it holds at every s ≤ s0 (in
particular on all of W). Proof: a packing P at side s with pins at slots_S(s) = slots_S (BL
slots are s-independent), embedded by the identity into [0,s0]² (BL corners flush), is a packing
of 11 unit squares in [0,s0]² with axis-aligned squares at all slots of slots_S(s0). The kill
hypothesis is containment-priced (A53 L5: the LP prices "contains the pins", never "and no
further simple square"), so the s0 certificate applies; contradiction. ∎
Applicability in L: exactly the classes whose 4-tuple has one nonempty diagram — k=6 shapes
{(3,3), (3,2,1), (2,2,2)} and k=5 shapes {(3,2), (3,1,1), (2,2,1)}, i.e. ≤ 2+2 D4 classes.
M1 is a checkable tag per class; everything else needs (a).

**M2 [C, refuted as a route] (general monotone transfer).** The natural proofs fail:
(i) *Rigid embedding* fails — pins anchor to all four corners; any placement of [0,s]² inside
[0,s0]² leaves at least two pin groups off their s0 slots.
(ii) *Corner-wise translation* (move each pinned square with its corner: BL by 0, BR by (δ,0),
TL by (0,δ), TR by (δ,δ); assign each free square a translation v(Q) ∈ [0,δ]²) reduces to a
feasibility problem: for every touching (or slack < motion) pair separated along SAT axis u with
Q' on the positive side, ((v(Q′) − v(Q))·u ≥ −gap(Q,Q′). For AXIS-SEPARATED pairs a monotone
field solves it, and a direct slot-arithmetic check (BR-pin right edges ≤ s−2, BL-pin left
edges ≤ 2, 2 − (s−2) = 4 − s < 1) shows no free square can be x-squeezed or y-squeezed directly
between opposite-anchored pins with sub-δ slack. But for TILTED free squares the separation
axes mix coordinates: a chain of tilted touching squares imposes constraints
(Δv)·u ≥ 0 with sign(u_x) ≠ sign(Δx) possible, and a monotone field only guarantees
(Δv)·u ≥ −2δ. A cycle of such contacts linking two differently-anchored pin groups can make
the constraint system infeasible; nothing in the stratum hypotheses excludes such chains (they
are exactly the A46/A48 bridge geometry, present in Trump's own packing, A53 L4). So M2 is
unproved, and no proof by these means exists; whether an actual counterexample PACKING exists
is open — for A56 the finding is: the transfer must NOT be assumed.
(iii) *τ\*-monotonicity* (G-A53-1's stated conjecture, τ\*_S(s) nondecreasing): the per-s
constraint families are incomparable (the exemption regions move with s: a placement exempt at
s1 can be non-exempt at s2 and vice versa), so no inclusion argument applies; and by A54 S0
(τ_LP bounds τ\* in neither direction) a measured τ curve could neither prove nor refute it.
Left as a conjecture, NOT used anywhere in A56.

### (a) + (c) merged: adaptive interval-s verification (the adopted route)

(a) with s as a live interval parameter and (c) finite s-subdivision are operationally one
scheme: the B&B branches on s exactly where uniform discharge fails; a PASS is a finite cover
of W by closed s-cells, each carrying a uniform certificate. This is A47's parameter-box
pattern (verify_measure_obs.py verifies over exact (y0, b) boxes by rebuilding the geometry
from the box and discharging with outward interval arithmetic) with parameter = s itself.

## P3 [S] — the parametric certificate and its soundness statement

**Format (parametric-kill-certificate-v1).** A base v1 certificate plus, per atom, anchor
rationals (βx_i, βy_i) ∈ [0,1]², and per core (βx, βy) ∈ {0,1}² matching the slot's corner;
offsets are DERIVED: α = coord_s0 − β·s0, so the s0 specialization reproduces the base
certificate EXACTLY (canary C1 is an identity by construction, then re-verified by the old
code). Validity conditions checked by the verifier, per s-cell [a,b] ⊆ W: weights ≥ 0,
Σw < b_budget (s-free); atoms inside: for β = 0 need 0 ≤ α ≤ a(−0), for β > 0 need
α + β·a ≥ 0 and α + β·b ≤ b(+0) — with the measured library max coordinate 3.553994 < 3.82
every β ∈ [0,1] keeps every atom admissible on all of W; cores: (α, β) must equal the declared
slot of the class (read from A53 results/name_to_slots.json, R-coordinates recognised as
s0 − 1/2 etc.), tm, a copied from the base certificate.

**Anchor choice is completeness, never soundness.** For each s the claim quantifies over ONE
measure μ_s = Σ w_i δ_{p_i(s)}; ANY declared anchor family gives a legitimate μ_s (a
certificate-existence statement per s). A bad anchoring can only make the verification FAIL,
never make a PASS unsound. Default (T2 correction, the GAP-ANCHORING LESSON): put the L/R
threshold in the widest gap of the certificate's OWN coordinates within a mid band (implemented
[19/10, 27/10]) rather than at the blind midpoint s0/2 — an atom sitting exactly at a
nearest-wall threshold splits a coherent covering cluster and manufactures spurious relative
motion; anchoring by the certificate's own empty band keeps every cluster on one side. Ladder
on failure: gap → nearest-wall → mid-band (β = 1/2 in the band); per-atom overrides recorded.

**Discharge rules (4D box B = [t0,t1] × [x0,x1] × [y0,y1] × [a,b], all dyadic rationals over
integer scales; T2 correction to the grid remark: ONE unified grid for x, y AND s,
D = 250000·2^(depth+2) — den(s_lo) = 50 divides den(s0) = 250000, s_lo ↦ 955000·2^(depth+2),
s0 ↦ 969271·2^(depth+2), so the odd window span 14271 is exactly bisectable depth+2 times).**
  (V) vacuous: no placement of B is admissible for ANY s ∈ [a,b] — the A08 test with the wall
      at s = b (the largest container of the cell);
  (CL) clip: centre ranges clipped to [w_min/2 (floor), b − w_min/2 (ceil)] — outward, so the
      clipped box contains every placement admissible at any s ∈ [a,b];
  (E) exempt: for EVERY (t, c, s) ∈ B the closed square Q(c, θ(t)) meets core K(s) — the A13
      SAT test core_exempt_frac with kx, ky widened to their exact s-intervals
      [α+β·a, α+β·b] (outward interval arithmetic);
  (C) covered: Σ{ w_i : p_i(s) ∈ Q(c,θ(t)) for EVERY (t,c,s) ∈ B } ≥ 1 — atom_inside with
      atom positions widened to their exact s-intervals (membership decided uniformly over the
      cell: an under-approximation of each fixed-s mass, hence sound);
  otherwise split along the widest of the four axes (t, x, y, s; s-width weighted, tunable) and
  recurse; an undischarged box at max depth is a FAIL witness (report its s-range).

**Soundness theorem [S].** If the parametric verifier PASSes certificate C on the root
[0,1] × [1/2, s0−1/2]² × W, then KILL_S holds over W. Proof: fix s ∈ W. Every 4D discharged box
whose s-range contains s specializes to a discharged 3D statement at side s: (V) at s = b ⊇
admissibility at s ≤ b... precisely, a placement (t,c) admissible at side s that would lie in B
lies in the clipped box (CL is outward in s), and is then either exempt at s (E specializes:
the ∀-s statement includes s, and K(s) ⊂ pin(s) since core containment in the pin is preserved
under the slot translation) or has μ_s(Q) ≥ 1 (C specializes). The 3D boxes with s in their
range cover the root of the fixed-s problem, Σw_i < b_budget, so the A13/A53-L5 kill argument
applies verbatim at side s: the 11 − k squares other than the pin-containing ones are
admissible, pairwise disjoint, non-exempt, each of μ_s-mass ≥ 1, forcing μ_s total ≥ budget —
contradiction. This holds for every s ∈ W separately; no relation between the μ_s beyond the
declared affine family is used. ∎

**Composed claim after a full sweep.** For every s ∈ [191/50, 969271/250000]: every packing of
11 unit squares in [0,s]² has k(P) ≤ 5, and if k(P) = 5 its skeleton class is not one of the 19
killed classes. (33 k=6 kills + P0 cap + 19 k=5 kills, each transferred by the theorem above or
by M1.) Partial sweeps compose the same way per-class; un-swept classes stay s0-only.

## P4 — canaries and cross-checks (binding on T2)

C1 endpoint identity: specializing the parametric certificate at s = s0 must reproduce the base
   certificate's atoms/cores exactly (α + β·s0 = coord_s0, an identity; asserted numerically),
   and the UNMODIFIED A53 verify_case.py must PASS it (it is the original file's content).
C2 sampled-s cross-check (independent code path): for each parametric PASS on cell [a,b], the
   old verify_case.py must PASS the specialized certificate at s = a, s = b, and one interior
   sample (cores and atoms evaluated at that s; budget unchanged). Any discrepancy is a bug in
   the new code (the old verifier is the audited arbiter).
C3 census window: the verifier asserts [a,b] ⊆ [191/50, s0] and the P0 endpoint predicates.
C4 trump5 is not in L and is never certified; k5_11 and k5_16 are open at s0 and are NOT swept
   (nothing to transfer).
C5 A29 untouched; A55's running processes respected (≤ 3 heavy processes for A56 in total).

## P5 — expected cost structure (for the T2 cost curve)

Fixed-s verification of the library costs 3–50 s per certificate (A53/A54 reports). The 4D run
pays extra only where structures move relative to the placement: boxes glued to R-anchored
pins/atoms need s-splitting at granularity ≈ the certificate's local positional slack. Coarse
model: cost ≈ (fixed-s cost) × (W width / tolerable s-cell width) on the moving fraction of the
volume. Certificates with margin ≥ 0.3 and few atoms (the 4-atom "4.12" family, 30 of 52)
should verify in one or few s-cells; the thin ones (k6_23@A54 margin 0.0146, k5_02 margin
0.00055 in TOTAL — note the total-margin is s-free, only coverage slack matters; k5_13@A54,
k5_10/15, k6_20/27) are the priced representatives. If a certificate FAILs on a sub-cell, the
recorded outcome is "transferred on [a', s0], open below a'" — sound partial transfer, plus the
witness geometry for a future re-optimization at the failing side.

## P6 — T2 corrections, artifacts, and lessons banked (worker runs of 2026-09-01, final)

(i) Unified integer grid and gap anchoring folded into P3 above. (ii) Measured cost law
(results/stage1_pricing.json): t_4D ≈ 261 μs × (#s-splits), Spearman 0.978 ON THE PASSES;
neither LP margin (−0.35) nor atom count (0.45) predicts cost — the driver is how close the
tightest covering atom sits to the boundary of Q, i.e. how many s-subdivisions the coverage
demands. (iii) **Artifact 1 (witness-cap FAIL times).** A FAIL time is NOT a cost measurement:
the search stops at --max-witnesses(-per-box), so a 0.7 s depth-48 FAIL (k6_32) says nothing
about the completed search — the same cert ran > 900 s at depth 56 and > 600 s at depth 60
without finishing. The early "+8 depth ≈ 2.5×" law fitted on k5_15 holds ONLY for runs that
CONVERGE; lifting depth on the OPEN set converted 0/5 (implied ≥ 33×–1300× blowups). Depth 48
is the operating point; depth 56 pays only when the tangency sits just past the 48-horizon
(k5_15, k6_23). (iv) **Artifact 2 (witness_s_range is a truncation sample).** The recorded
witness s-range localises the failing set ONLY when the search completed, i.e. when the witness
count is NOT a multiple of the per-box cap (8). Exactly one campaign run satisfied this —
k6_23's full-window run (9 witnesses) — and it is exactly the one whose sub-window bisection
PASSed; the other sub-window attempts (truncated witness sets) failed 6 of 7. (v) **The
eps_geo lemma (the repair lever).** When a 4D run is open at a weak placement whose mass ≥ 1
rests on ONE atom, weight scaling is inert — the deficit is the atom's POSITION, not its mass.
Re-solving the guard LP with a row-shrink robustness margin eps_geo (every covering atom must
sit ≥ eps_geo inside Q) buys exactly the positional slack the 4D verifier needs against the
atom's s-interval. Measured threshold: eps_geo ≥ 0.0015 converted 13/16 OPEN rows, eps_geo <
0.0015 converted 0/5 — the positional deficit across this library is of order 1.5e-3. Cost of
the shrink: dτ/d(eps_geo) ≈ 1.1–1.7 × 10², so eps_geo = 0.003 costs ≈ 0.5 of budget; the
**budget-slack rule**: a certificate is repairable iff budget − τ0 ≥ ~0.5 (schedule used:
eps_geo = clamp(0.003·min(1, (budget−τ0)/1.0), 0.0002, 0.003)). **Abort-early lesson**: gate on
the slack inequality BEFORE attempting — failed rows cost MORE than successes (certify burns
its full witness-feedback rounds, ~1500 s, on sub-threshold rows). (vi) merge_stats trap:
A53's merge_stats special-cases only max_depth, so any NEW max_* statistic merged across
workers is SUMMED, not maxed — verify_param.py carries merge_stats_p; latent bug for future
extensions of verify_case.py stats. (vii) Empirical, campaign-wide: ZERO coverage holes
anywhere in the window across every A56 run — all non-PASS boxes are depth-limited undecided;
stage 0 shows all 48 multi-corner certificates valid at the far endpoint s = 191/50 under gap
anchoring. Cost truth: cumulative verifier time 34584 s ≈ 9.6 h; after the eps_geo recipe the
4D verification is a rounding error (median 45 s) and the LP dominates (median 433 s).

## P7 [S] — ledger rule (certificate substitution; advisor ruling, 2026-09-01)

The composed claim of P0/P3 is per-STRATUM ("stratum S is empty for every s in the range"), a
statement about the stratum, not about any particular certificate. Any exactly-verified
certificate family proving it is therefore fungible: a row converted by an eps_geo re-solve
kills its stratum over the window via a NEW base certificate, while the original A53/A54
certificate remains the s0-endpoint witness. Both are kept in the ledger with provenance
(scoreboard rows record original cert + parametric cert + resolve parameters); neither
supersedes the other's verified claim.
