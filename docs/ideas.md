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
