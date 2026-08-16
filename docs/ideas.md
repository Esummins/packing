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
