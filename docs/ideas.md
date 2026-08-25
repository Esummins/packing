# Idea board (advisor). Status: open / running (→ attempt id) / closed (with reason)

## Lower bound (raise 3.7889)

**I-L1. Optimised unavoidable point sets.** Stromquist's bound comes from a hand-built argument. Ask
directly: what is the largest s admitting 10 points in [0,s]² that meet every closed unit square inside
[0,s]²? Optimise numerically over the 20 point coordinates (coverage test = for every θ, the 10 unit
squares of orientation θ centred at the points must cover the square of centres of side s−cosθ−sinθ);
then certify rigorously by 3-D interval branch-and-bound over (x,y,θ). Status: running → A05.

**I-L2. LP / measure-theoretic ("fractional unavoidable set") bound.** Generalise I-L1: find a
non-negative measure μ on [0,s]² with μ([0,s]²) < 11 and μ(Q) ≥ 1 for every closed unit square
Q ⊂ [0,s]². Then no 11 pairwise-disjoint closed unit squares fit (each has mass ≥1) ⇒ s(11) ≥ s.
Point sets are the integral special case, so this bound is at least Stromquist's if his proof is a
pure unavoidable-set proof. It is an infinite LP (min μ(total) s.t. μ(Q) ≥ 1 ∀Q); its LP dual is
the fractional packing number ν*(s), computable numerically, which also tells us the *ceiling* of every
measure-type argument. Discretise: atoms on a fine grid (or uniform measures on small cells for
continuity), constraints on a fine grid of placements, cutting-plane / row generation. Verify rigorously
with interval arithmetic in (x,y,θ). Status: open → to be assigned (A07).

**I-L3. Understand and tighten Stromquist's actual argument.** Where is the slack? Which lemma is
binding at 2+2√(4/5)? Status: running → A02.

**I-L4. Full computer-assisted proof (33-dim interval branch and bound with symmetry breaking and
combinatorial pre-cases).** Probably out of reach for the full optimum; might be usable to prove a weak
statement like s(11) ≥ 3.80 if combined with I-L2 to kill most of the space. Status: open, deferred.

**I-L5. Combinatorial structure theorems.** E.g. Stromquist's 0°/45° result: any packing in side < 3.8856
must have a square at a "generic" angle. Can we prove strong restrictions on packings in side < 3.877
(e.g. at least k tilted squares, tilt in some interval) and then finish by I-L2/I-L4 on the reduced
family? Status: open.

**I-L6. LP-based branch-and-bound over packing structure ("case-LP", from A02 + advisor).** The pure
measure LP saturates where its fractional packing reaches 11 (A07: ≈3.84–3.85). Beyond that, use
integrality by case splits, exactly as Stromquist does by hand: pick a family F of placements (e.g.
squares centred in a wall rectangle R that avoid a chosen point set P'). Branch YES: some square X of the
packing lies in F ⇒ require μ(Q) ≥ 1+β for Q ∈ F, μ(Q) ≥ 1 otherwise; contradiction if total < 11+β.
Branch NO: no square of the packing is in F ⇒ drop the coverage constraint on F entirely; contradiction if
total < 11. Each branch is an LP; recurse (split F further, or split on other regions). This is LP-based
branch and bound on the combinatorial structure of the packing and can in principle go all the way to
3.877 if the tree stays finite; the certificate is a tree of measure certificates. Status: open, next
after I-L2 is certified.

## Upper bound (beat 3.877084)

**I-U1. Massive multi-start continuous optimisation** (penalty / augmented Lagrangian on overlap
areas or separating-axis depths, plus basin hopping over rotations). Status: running → A04.

**I-U2. Contact-graph catalogue.** From every local optimum found by I-U1, extract the contact graph,
solve the tangency system exactly, catalogue distinct rigid structures and their s. Doubles as the
"ab initio" direction: optimal packing = best root over rigid contact structures. Status: open.

**I-U3. Exact reconstruction + rational certificate of the current record** (re-do the prior session's
work inside this repo, keep the artefacts). Status: running → A03.

## Certification

**I-C1. Lean 4 integer-arithmetic checker** for packing certificates (upper bounds) via `decide` /
`native_decide`; bridge lemma (separating axis ⇒ disjoint) proven once. Status: running → A06.

**I-C2. Lean 4 checker for measure/point unavoidable-set certificates** (lower bounds): rational
box subdivision of (x,y,θ) with rational bounds on cos/sin. Status: open, depends on I-L1/I-L2.
Design note (advisor): parametrise θ ∈ [0,π/2) by t = tan(θ/2) ∈ [0,1); cos = (1−t²)/(1+t²) and
sin = 2t/(1+t²) are monotone rational functions on [0,1], so for a rational t-box the enclosures of
cos, sin are exact rationals; "p ∈ Q(c,θ)" ⟺ |cos·(px−cx)+sin·(py−cy)| ≤ 1/2 ∧ |−sin·(px−cx)+cos·(py−cy)| ≤ 1/2
is then checked on a (t,cx,cy)-box by exact rational interval arithmetic. The certificate is a list of
boxes covering [0,1]×[0,s]² each with a witness point (or list of atoms with weights summing ≥ 1);
Lean checks it by `decide`/`native_decide` over ℚ (or scaled ℤ). The bridge lemma (every unit square in
the container is Q(c,θ) for some θ ∈ [0,π/2), and 90° symmetry) is the only real-analysis content.

**Advisor remarks on the LP method (I-L2).** Pairwise overlap constraints are implied by point
constraints (two overlapping squares share a point), so the point-LP can only be beaten by fractional
packings that exploit ≥3-cliques with no common point (pinwheels / odd cycles in the placement
conflict graph). Possible strengthenings if the pure LP saturates below 3.877: (a) clique constraints
for pinwheel triples; (b) "region rank" constraints: at most k(R) centres in region R (e.g. wall bands:
centres pairwise ≥ 1 apart since each square contains its incircle); (c) Lovász-theta-type SDP on a
discretised placement graph (rigorous via shrink-and-snap, but the discretisation must be very fine —
probably infeasible directly). The incircle relaxation alone (11 points pairwise ≥1 apart in a
square of side s−1) gives only s ≥ 1 + 1/d₁₁ ≈ 3.51 (d₁₁ ≈ 0.398 = max-min distance of 11 points in
a unit square), so region constraints must be used together with point/measure constraints.

**I-U4 / I-L7. Angle-lattice MILP and angle-box branch-and-bound (PI + advisor, 2026-08-18).** At fixed
orientations the packing problem is a disjunctive LP (containment linear; each pair separated by one of
≤ 8 axes, each a linear inequality once angles are fixed). Hence for a finite angle set Θ the exact
optimum over packings with angles in Θ is a MILP (angle-choice binaries × axis-choice binaries); Stromquist's
0°/45° theorem is the case Θ = {0°,45°}. Ab-initio discovery = solve the MILP over a fine lattice Θ; rigorous
proof = replace lattice points by angle BOXES with interval coefficients and branch over the angle torus
modulo S₁₁ and the 90° symmetries, pruning each box either by MILP infeasibility (relaxed coefficients) or by
the measure LP restricted to that box (I-L2 with orientation-restricted constraints — strictly stronger per
box than the global τ*). Symmetry helps exactly here (S₁₁ ordering, D₄, 90°), but the optimum itself has
trivial symmetry (Trump's packing is asymmetric; the octic's Galois group is S₈ — verified 2026-08-18 by
cycle-type statistics mod 426 primes), so no symmetric-stratum shortcut exists. Status: running → A09.

**I-L8. Region-rank cuts, recursively certified (advisor, 2026-08-18, after A10).** A10 shows the box LP's
integrality gap is concentrated in 4-fold-symmetric fractional structures (½-weight edge uprights, four ½-weight
rotations of a ~30–35° square, ¼-weight uprights) with centres in a ring/edge region R. Valid inequality for every
real packing: Σ_{Q : c(Q) ∈ R} x_Q ≤ k(R), where k(R) = max number of pairwise-disjoint unit squares (inside the
container) whose centres lie in R. Dual certificate: μ ≥ 0 and λ_R ≥ 0 with μ(Q) + Σ_{R ∋ c(Q)} λ_R ≥ 1 for all Q
and μ(total) + Σ_R λ_R·k(R) < 11 (bridge: sum over the 11 squares). Each k(R) is itself a small packing bound,
provable by the SAME measure LP with n = k(R)+1 restricted to centres in R (recursion). This is the dual form of
Stromquist-style "at most k boxes in region R" lemmas and directly targets the A10 obstruction. Pilot = A12.
Status: **closed (A12, done-negative)** — the mid-tilt fractional packing has integer load on every symmetric region and a
realising packing on every macroscopic region (4+4+3 with 4+4+1 / 4+2+3 / 8+1 all packable); LP-certified k(R) can never yield a
violated cut on integer loads (x*|_R is dual-feasible for the sub-LP); combinatorially certified fine cuts (ρ ≤ 0.05) are escaped by
sliding the support (τ = 11.000, λ = 0 over 25 rounds at 3.85–3.87). Conditional (fixed-square / excluded-zone) LPs DO kill it
(τ = 5 < 7 with corners fixed and side zones empty) ⇒ pursue I-L6 with fix-a-square branches instead.

**I-L9. Lovász–Schrijver ϑ′ kernel bound (advisor, 2026-08-19).** Certificate: PSD kernel K on the placement space
with K(x,x) ≤ λ−1 ∀x and K(x,y) ≤ −1 for all disjoint pairs; then Σᵢⱼ K(xᵢ,xⱼ) ≥ 0 over any packing gives n ≤ λ.
ϑ ≤ fractional clique cover ≤ τ* (Theorem 1), and ϑ sees odd cycles (ϑ(C₅)=√5), i.e. exactly the ¼-weight cheats of
A10–A14. Ansatz K = φᵀMφ (D4-symmetric polynomial/Fourier basis, M ⪰ 0), cutting planes on the pair constraint,
rigor by exact LDLᵀ + 6-D interval check. Pilot: discretised ϑ′ vs LP on the same placement graph at s = 3.85.
Follow-ups: 3-point (Bachoc–Vallentin-type) bound; ϑ′ as node relaxation in the case tree (I-L6). Status: **piloted (A15, 2026-08-19): on the same discretised placement graph ϑ′ ∈ [10.38, 10.48] vs LP 11.000 vs α 10 at s = 3.84–3.85 (mid-tilt graph too) — about half the LP gap removed, gap stable under grid refinement; continuous kernel version recommended, with the kernel class containing the LP's coverage-indicator features (the LP certificate is such a kernel). Next: ϑ′ on an un-seeded fine grid; ϑ′ as node relaxation in the case tree.  A16 (2026-08-19): ϑ′ as the case-tree node certificate — kills every node type the LP cannot (four corners fixed: LP 7.000 = budget vs ϑ′ ≤ 6.51–6.62, tight 6.25–6.46; one corner: 10.000 vs ≤ 9.44–9.49; A14's alive boxes: ≤ 9.52–9.67; corners+NO side: ϑ′ = α); un-seeded grids are integral (uninformative); ϑ′ tree = root + 13 leaves ⇒ build the continuum kernel certificate, root first.**

**I-L10. The GLOBAL boundary/interface ledger (PI, 2026-08-20, after A24).** A23/A25's wastage oracle is a LOCAL,
monotone lower bound on a partial configuration, so a lone interior square contributes ~0 and the test only bites at
depth >= 3 (A24: T2 fired at ZERO tree nodes; all 30 kills were the coverage LP). The physics it ignores: a uniformly
tilted lattice of unit squares TILES the plane with zero waste, so tilt costs nothing in the bulk — waste is produced
only where a same-tilt block TERMINATES, at a container wall (wedge) or against a differently oriented block (sliver).
So the right invariant is a boundary/interface functional evaluated GLOBALLY on all 11 squares, which could kill at
shallow depth — exactly A24's bottleneck. Ingredients: (a) a band-counting lemma bounding how many squares can avoid
a width-w boundary band, (b) a charged wall functional = certified dead-area of the UNION over a hypothesis profile,
(c) a combinatorial minimisation over profiles giving min-total-charge vs the budget s^2-11.
Status: **closed as a killer, kept as counting (A26, 2026-08-21, done-negative with three theorems).**
(a) SUCCEEDS and is exact: a square avoids the width-w band iff it lies in the concentric square of side B = s-2w, so
m(w) = max{n : s(n) <= s-2w} — the lemma is exactly as strong as the small-n square-packing constants, and it is
unavailable precisely when B >= 3 (it would then need the OPEN s(10)). Elementary SAT lemma: (2B-1)^2 < 8 => at most
ONE square, giving **>= 10 of the 11 squares meet the width-1 band at 3.84 and at s'** (Thm A26.1), and
**>= 7 have centre within 1.34711 of a wall** (Thm A26.2). TIGHT against Trump (his R_max = 0.9840 vs threshold
0.98144 at s').
(b)+(c) FAIL, for an exact geometric reason: the functional has a ZERO. A unit square flush against a wall and within
a few degrees of axis-parallel strands certified-ZERO dead area (an axis-parallel block terminating on an
axis-parallel wall makes no wedge) — 16 of the 1070 admissible band cells are exactly 0, the smallest positive value
is 0.0039, and that configuration is 6 of Trump's own 11 squares. **min-over-profiles charge = 0.0000 vs budget
3.7456**; 0 kills at A24's three live level-1 boxes and 0 at the root. Requirement is 0.5351 per square with n = 7 or
0.9364 with n = 4; the best certified value with tilt AND depth floors is 0.1602. Trump's own certified wall charge
is 0.8672 = 21.5 % of his budget — the worst-case calibration the route would have to beat.
BY-PRODUCT (Thm A26.3): the band lemma is the boundary-band instantiation of I-L8, and A19's exact value-11
fractional packing satisfies EVERY band / tilt / band x tilt / zone rank cut, several with equality, so
tau_cut(3.84) >= 11 — that instantiation of I-L8 is now closed too.
WHAT WOULD HAVE REVIVED IT - and why it cannot. The route needs quantitative tilt forcing. Elementary methods give
"at most 9 squares have tilt within 3.326 deg of axis-parallel" (2.503 deg at s'); A24's LP probe already gives
10 deg (tau = 9.358, a valid rank bound because a tilt class of a packing is itself a packing); and A26's numerical
search finds TEN unit squares of tilt <= 15 deg that fit in [0,3.84]^2, with the true 9-vs-10 threshold at
eps* ~ 12 deg. So the provable ceiling is within 2 deg of the truth and **at most ~2 squares can ever be forced to be
mid-tilt**, against the ~7 the ledger needs. Conjecture A26.T ("at most 9 within 28.5 deg" - the cheapest cut that
would have cut off A19's value-11 fractional packing) is REFUTED by an explicit 10-square witness of max tilt
23.36 deg. General principle recorded here: **an LP-certified rank bound tau_B(R) can never be violated by a feasible
fractional packing** (y|_R is feasible for the sub-LP), so a useful region-rank cut must come from a COMBINATORIAL
bound strictly below tau_B(R) - and none of the elementary families (bands, tilt classes, A21 zones, small-n s(n)) is.
STILL USABLE TODAY: "two squares both with R >= 0.93" is dead by Thm A26.1 and "five squares with R >= 0.5665" by
Thm A26.2 - LP-free pruning rules for A24's interior-first tree. The only surviving charging direction is a
CORNER-occupancy statement (the charge is 1.40-1.60 only at depth ~1.2 near a CORNER, where 3 squares already exceed
the budget), which is an LP question of the A21.1 type rather than a counting one.

**I-L11. Critical-point (Morse/flow) reduction — the PI's "illusory volume" observation formalised
(2026-08-21).** With t = tan(θ/2) all constraints are polynomial, so the feasible set of 11-packings is
SEMI-ALGEBRAIC: finitely many components, no fractal behaviour (theorem, discharges the PI's hedge).
Compressing the container defines a flow whose drains are critical (jammed) configurations; to exclude
packings at side ≤ s it suffices to exclude CRITICAL packings at ≤ s. Diagnosis of the whole campaign in
this language: measure/coverage certificates cannot express "WLOG critical", so they pay full price for
the non-critical ocean — the ¼-structure ghost lives exactly there; A22's Krawczyk certificate is the
one flow-native tool and it worked. Programme: (1) drain lemma (every component contains a critical
config; gap-squeeze + compactness; rattlers → strata, park them), (2) stress lemma (critical ⇒
wall-to-wall stressed contact structure; Connelly-type jamming for polygons with sliding contacts —
THE missing theorem), (3) enumeration of stressed bridges (≥3 squares spanning 3.84, each tilted hard;
A26 tilt caps make the candidate set small; refute each via MILP → Newton → Krawczyk). Advisor to draft
lemmas 1–2 in-loop; enumeration is Opus work. Status: open — next after A27's verdict.
