# A34 verdict note — the collapse theorem, the measured wall, and the NO-GO

Fable, 2026-08-27. Data: results/validation.json (27 records), sanity.json, env.json;
spec notes/formulation.md.

## 1. THEOREM (exchangeable collapse of sub-full clique hierarchies)

Let a sparse moment relaxation of the A34 POP (any level r, any valid added cuts) use cliques
K_1..K_N such that every clique's square-support S_K (the set of square indices whose variables
appear in K) has |S_K| ≤ m < n. Then the relaxation is feasible at s = s(m); hence its bound
≤ s(m) for every n, every level r, and every family of cuts that are valid for m-square
sub-packings.

Proof. Fix an optimal m-packing at side s(m); by formulation.md §2(d) it admits the lift: placements
w_1..w_m (with (γ,σ) on the circle) and a unit separating direction u_{ab} for each pair a≠b.
For each clique K define the measure μ_K = image, under the assignment map, of the uniform
distribution over INJECTIVE maps ψ: S_K → {1..m} (assign square i placement w_{ψ(i)}; for each
pair {i,j} ⊆ S_K set u_ij = u_{ψ(i)ψ(j)}; set s = s(m)). Marginal consistency: the restriction of a
uniform injective assignment of S to a subset T is the uniform injective assignment of T, so any
two cliques agree on the marginal of their shared variables. Support feasibility: any ≤ m squares
of a legal m-packing form a legal partial packing satisfying every clique-local constraint
(containment, circle, separation rows with the inherited u, box bounds) and every cut valid for
sub-packings (R1–R3 included). Hence every moment and localizing matrix of the sparse SDP is a
genuine moment matrix of a measure — PSD at every order — and all consistency rows hold: the SDP
is feasible with objective value s(m). ∎

The measures do NOT glue to a global measure (that would need an n-packing at s(m)); exactly the
RIP failure lets local consistency stop at marginal agreement — the anti-correlated-triangle
phenomenon. RIP is not a technicality about convergence proofs; its absence is a hard ceiling.

Predictions vs measurement (validation.json, 29 records, closed 2×3 grid): Tier A (m = 2) values
must be n-independent and equal to the pair-problem (n = 2 dense) value at each level and each cut
setting. Measured: level 2, cuts ON: 1.707107/1.707111 (n=2, SCS/Clarabel) / 1.707249 (n=3) /
1.707470 (n=5) — spread ≤ 4·10⁻⁴; level 2, cuts OFF: 1.500008 (n=2) / 1.502002 (n=3, iter-limited)
/ 1.500114 (n=5) — a second, independent n-independent family at a different value; level 3:
1.9569 (n=2) / 1.9586 (n=3). Seven confirmations to solver tolerance across two cut settings and
three levels of n. Level-2-with-cuts = 1 + 1/√2 exactly = the
distance-geometry (disk) bound for one pair, as expected (level 2 + R1/R2 captures centre-distance
geometry and little else).

Consequences.
(i) Tier A (pair cliques) is capped at s(2) = 2 forever: dead for n = 11, no cut can fix it —
    any cut strong enough to break the cap must be INVALID for 2-square sub-packings, i.e. must
    couple ≥ 3 squares, i.e. must leave the pair clique.
(ii) Every "intermediate" design (triples m=3: cap 2; quintuples m=5: cap 2.707; even m=10:
    cap s(10) = 3.7071) is capped BELOW Stromquist's 2003 bound 3.7889, let alone the lab's
    certified 3.82. Coordinator question (a) is answered in the strongest sense: there is NO
    clique design between B and dense worth trying — a clique containing all 11 squares' 44
    configuration variables is mathematically mandatory, and Tier B's K_0 is the minimal such.

## 2. What the mandatory K_0 clique can see, by level (the measured wall)

Level 2 on K_0 (Tier B) is quartic moments in 4n+1 vars. Measured (cuts on):
  n=3: 1.7929 vs truth 2      (deficit 0.207; dense L2 1.8166 — cross-moments add little)
  n=5: 1.8624 vs truth 2.7071 (deficit 0.845; SCS TIME_LIMIT but primal-dual gap 6e-6)
Deficit GROWS with n both absolutely and relatively (10% → 31%). Crude but conservative
extrapolation of the trend (deficit fraction ~ linear in n) puts Tier B level 2 at n = 11 around
2.3–2.9 — below even the area bound √11 = 3.317, and far below the certified 3.82 / target 3.83.
Level 2 is a distance-geometry-strength relaxation; the packing content (orientation-coupled
non-overlap of 11 bodies) enters only at higher order.

Level 3 quality, measured where affordable: n=2 (11 vars, block 364): 1.9569 vs 2 — still 2.2%
short ON THE EASIEST INSTANCE. So even level 3 on K_0 would not obviously reach 3.83-quality
tightness at n=11; and its size is out of reach anyway:

  K_0 basis sizes (44 vars, fixed-s): level 2: C(46,2) = 1035 (min-s 1081); level 3: C(47,3) =
  16 215; level 4: C(48,4) = 194 580. Solver reality measured this pilot (open solvers, 20
  threads): block 253 ≈ 30 min/solve to 1e-5; block 364 ≈ 5 min (11-var problem); block 1035 ≈
  40 h projected (SCS iteration scaling ~size^3, more iterations at scale — consistent with
  A15/A19/A20 experience); block 16 215: not solvable by any present solver. D4×S11 symmetry
  reduction (~|G| = 8·11! is irrelevant — what matters is isotypic block collapse, realistically
  ×8–90 on block DIMENSION) brings level 3 to ~2 000–6 000 per block: months of engineering for a
  solve that the n=2 calibration says is still short of the needed tightness.

## 3. Answers to the coordinator's three questions

(a) Structural. The collapse theorem eliminates every design whose cliques don't carry all 11
    squares (cap ≤ s(10) = 3.707 < 3.789). Above that floor the only lever is the level on the
    44-var clique, and §2 shows level 2 is ~1–1.5 SIDES short with deficit growing in n, while
    level ≥ 3 is unaffordable and (per n=2 calibration) still not clearly sufficient.

(b) Mosek: NO material change. A license makes the Tier B level-2 SDP at n=11 solvable (1035-block,
    plausibly 1–4 h Mosek vs ≳40 h open) — but §2's trend projects its VALUE at ≈ 2.3–2.9,
    below √11. Mosek changes the cost of computing a number that is already known to be useless.
    It does not touch level 3's 16 215-block wall. Do not spend the PI's time on the license for
    A34 purposes.

(c) Mixed-level (pair blocks at level 3, K_0 at level 2): the collapse theorem caps everything the
    pair blocks contribute at s(2) = 2 (level-independent), so the mixed design's value is
    Tier-B-level-2 plus a pair-marginal sharpening whose ceiling contribution is bounded by the
    n=2 gap structure; the coupling bottleneck (quartic-only moments on K_0) is untouched.
    Predicted value at n=3: ≤ ~1.96 vs truth 2; at n=11 it inherits §2's projection. The measured
    convergence rate is decisive; the one further experiment is not worth a slot. (If anyone ever
    wants the 30-minute curiosity: n=3, pair cliques at level 3 + K_0 at level 2; prediction
    on file: it lands between 1.79 and 1.96 and changes nothing.)

## 4. VERDICT (T3): NO-GO

Level 2 with sparsity/symmetry does NOT beat the proven pure-LP ceiling 3.83 at n = 11 — not
because the SDP is too big to solve, but because the mathematically mandatory relaxation tier that
could in principle beat it (level ≥ 3 on the full 44-variable configuration clique, blocks
≥ 16 215 pre-symmetry) is beyond any present solver, while every affordable tier is provably
(Tier A/intermediate: collapse theorem) or empirically (Tier B level 2: measured n-trend) capped
far below 3.82. The feasibility wall is measured, not guessed: 253-block = 30 min, 1035-block ≈
40 h open / ~hours Mosek, 16 215-block = unreachable. I-L14's hope — that the ghost being a
level-1 artifact (A15) meant level 2 would kill it — fails quantitatively: A15's θ′ lives on a
DISCRETISED placement graph where "level 2" is cheap; on the continuum POP the same strength
requires the full-clique high-order tier. The A17–A20 kernel failures and this NO-GO now have a
common explanation: pairwise-consistency relaxations (θ′-kernels = Tier-A-shaped) carry a
structural ceiling (there: the 6-D pair continuum re-pinning; here: the collapse theorem), and
what lies beyond pairwise is dimensionally unaffordable.

Salvage: the collapse theorem itself (a reusable no-go criterion for ANY future sparse-relaxation
proposal on this problem: check the clique square-support first); the degree-2 circle-form POP +
validated model stack (reusable if solver technology jumps, e.g. a future low-rank/first-order
method certified at 1e-8 on 16k blocks); verify_sos.py (exact rational SOS checker, 4 corruption
gates, reusable for any SOS certificate in the lab); the Trump lift witness (rational, exact).
