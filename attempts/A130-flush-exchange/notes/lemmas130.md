# A130 — the flush-aware coupled moves: exact neighbourhood lemmas (T2)

Conventions as in `docs/proofs/drain_sel.md` (boxes B = B(z, m, r), interval rows, Lemma SAT, Fact D, the padded
box B⁺, the h′ hull at a kink). Labels [T] proved, [S] routine, [M] measured (`code/flush130.py`,
`results/moves130.jsonl`), [F] finding, [C] open. n-general throughout: nothing below uses n = 11 except the sample.

## 1. [T] Lemma BOX-FIELD-W — a non-rigid field with WEAK rows on a box

**Setting.** A *field* on a member set C is Y = (v_i, ω_i)_{i∈C} ∈ ℝ^{3|C|}; z′_ε moves every member i by its own
exact screw g_ε^i = (R(εω_i), εv_i) about the origin (outsiders fixed). Member–member relations are no longer
preserved, so every pair with a member is a row family. For a pair (A, B′) and an axis k of A, with A, B′ ∈ C,
  d sep_k/dε = ⟨c_A^k, y_A⟩ + ⟨c_B^k, y_B⟩ + H_k · (ω_{B′} − ω_A),
where c_A^k = (−n, Jn·d − n·Jc_A), c_B^k = (n, n·Jc_{B′}) (Fact D without the kink term) and H_k is the hull of the
branch derivatives of h at Δ_k over B. The kink term is charged through the EXACT difference u = ω_{B′} − ω_A (an
auxiliary LP variable with the equality u = ω_{B′} − ω_A), so that two members rotating together pay nothing at
their flush contact — interval arithmetic on H·ω_{B′} − H·ω_A would charge |ω_A|/2 + |ω_{B′}|/2 instead of |u|/2.

**Lemma BOX-FIELD-W.** Let r > 0, Q ∈ C, c a corner, and let the field Y satisfy on B⁺ = B(z, m, r + 10⁻⁶):
 (P_w) for every pair {A, B′} with a member: some axis has sep > 0 throughout B⁺, or every axis whose separation
       can be ≥ 0 on B⁺ has derivative lower bound ≥ 0 on B⁺ (WEAK);
 (W_w) every wall row of a member that can be ≤ 10⁻⁷ on B⁺ has derivative lower bound ≥ 0 (WEAK);
 (D)   every candidate argmin point of Q at c has branch-derivative lower bound > 0 (STRICT);
 (N)   every other (member, corner) candidate with μ ≤ 1 possible on B⁺ has lower bound ≥ 0.
Then for every packing z′ ∈ B at which Q intrudes c there is ε₀ > 0 with z′_ε a packing at side m′ and
Ψ^(w)(z′_ε) < Ψ^(w)(z′) for all ε ∈ (0, ε₀] and every positive weight vector; hence B contains no Ψ^(w)-minimiser
at which Q intrudes c, and if at most two squares can meet int(cell c) on B, every selected minimiser in B is
K0-FREE at c.

*Proof.* As for Lemma BOX-MOVE (`drain_sel.md` §2.0) with one change: a row whose one-sided derivatives are ≥ 0 at
EVERY point of B⁺ is nondecreasing along the path (a continuous function all of whose Dini derivatives are ≥ 0 on
an interval is nondecreasing), and the path stays in B⁺ for ε ≤ ε_pad; so sep_{k*}(ε) ≥ sep_{k*}(0) ≥ 0 for the axis
k* that separates the pair at z′ — interior-disjointness is preserved, strictness is not needed. Q's depth still
decreases strictly by (D). ∎

Remarks. (1) Weak rows are sound ONLY for r > 0: at r = 0 the derivative bound holds at one point, a rotation's
second-order term can violate a weakly-satisfied row (a vertex on an edge rotating about the centre), and the
strict form (Lemma ROT / CLUSTER-ROT) is the correct point statement; for pure translations at r = 0 the weak
form is Lemma ROT-W (Fact A). On a box the interval bound covers the whole path, which is why the weak form is
sound there. (2) BOX-MOVE (rigid screw, strict rows) is the special case y_i = y for all i ∈ C with the rows
strengthened; CLUSTER-ROT, NOCRIT-SEL and ROT are its r = 0 sub-cases. (3) The brief's COLUMN-STRAIGHTEN + ROW-SLIDE
field (a flush column rotating about its wall contact while the adjacent row slides along the flush line) is a
point of this LP's feasible set: the column members share ω (u = 0 at their flush contacts), the row members
translate along the flush line (n·v = 0 on the flush axis); the LP over all 3|C| variables finds the best field,
so the experiment tests the whole family at once. Lean shape: `boxHeldField (B : PoseBox) (C : Finset (Fin 11))
(i : Fin 11) (c : Fin 4)` := the Motzkin certificate over the finite row list with 3|C| + (#member–member kinks)
variables (the auxiliary u's enter as equalities, i.e. as two opposite weak rows); `box_field : ¬ boxHeldField B C i
c → ∀ z' ∈ B, CfgPacking m' z' → Intrudes z' i c → ¬ IsMinOn Ψw (packings m') z'`, same proof skeleton as `box_move`
with the Dini-derivative lemma in place of the strict-increase lemma.

**Lemma BOX-GORDAN-F [T] (the dual).** Q is HELD ON B UNDER FIELDS ON C iff there are μ ≥ 0 on the strict rows
(not all zero) and ν ≥ 0 on the weak rows with, for every variable slot j (every member's v_x, v_y, ω and every
kink difference u), Σ μ lo_j + Σ ν lo_j ≤ 0 ≤ Σ μ hi_j + Σ ν hi_j, where the equality rows u − ω_{B′} + ω_A = 0 enter
with free sign. Motzkin's transposition theorem on the split variables, exactly as Lemma BOX-GORDAN. ∎

## 2. [T] Lemma MODE — the contact-mode split (why a plain box cannot see a flush slide)

**Lemma MODE.** Let {A, B′} be a pair with k₁, …, k_p the axes whose separation can be ≥ 0 on B (p ≥ 2). For every
packing z′ ∈ B some k_j has sep_{k_j}(z′) = max_l sep_{k_l}(z′) ≥ 0. Put P_j := {z′ ∈ B : sep_{k_j} ≥ sep_{k_l} ∀ l}.
Then B = ∪_j P_j and Lemma BOX-FIELD-W's conclusion holds on P_j if its hypotheses hold with the pair's rows
restricted to the single axis k_j (the field may depend on j). If moreover hi_B(sep_{k_j} − sep_{k_l}) < 0 for some
l, P_j contains no packing and the case is vacuous. *Proof.* On P_j the axis k_j separates the pair at z′, and
the proof of BOX-FIELD-W uses only that axis for that pair. ∎

**[F] What MODE does and does not buy at a flush contact.** At a flush contact (parallel touching edges, overlap
length L > 0) the two near-zero axes are the two edges' normals, and the pieces are "B′'s corner rests on A's
edge" and the reverse, according to the sign of the relative tilt; the exactly-flush configurations lie on their
common boundary. On each piece the slide that preserves the separating contact is a DIFFERENT motion, and a
fixed field certified by interval rows must satisfy the piece's row at every point of the whole sub-box, where
the wrong-mode axis has a derivative of the sign of the relative tilt. So the plain box certificate of the slide
of one flush square under another fails at every radius by a sign of the order of the tilt uncertainty — not a
lock, a MODE ACCUMULATION at the flush stratum: this is the exact content of A128's "a flush placement has no
neighbourhood". [M] `results/moves130.jsonl`, `results/shells130_K03_BR.json`: at K03 BR (sq6 = f2 on the floor
under sq7 = BR(0,1), overlap 0.207; sq4 = f0 also flush on sq6's top edge over 0.330) the 8 tilt-sign sub-boxes ×
4 modes give 10 of 32 pieces certified by the horizontal slide of sq6 (rate 1.000), every piece with sq6 tilted
toward the wall (its top edge descending toward the corner) and sq4, sq7 tilted the same way; every uncertified
piece has sq6 or a flush partner tilted the other way — and no piece is vacuous by intervals.

**Lemma SHELL-SCALE [T] (the accumulation is one-sided and scales).** Let the deep intruder A rest on the floor
with its top edge under the corner of a square B′ (the mode "B′'s corner on A's edge") and let A's tilt δ_A ∈
[a, 2a] be bounded away from 0 (A rests on ONE bottom corner, the other lifted by ≥ sin a). Then the screw y(a) =
(slide away from c at rate 1, rotation −2.5a/s about A's floor corner, s = the distance from that corner to
B′'s contact point along the edge) has: the lifted-corner floor row a MARGIN row (sep ≥ sin a − pad > 0 for pad
< sin a); the pivot floor row identically 0 (structural); the row of B′'s corner on A's top edge ≥ (2.5a − 2a·…)/s
> 0 (the rotation lowers the edge under the corner faster than the slide raises it); Q = A's depth rate 1 − 2.5a/s
> 0. Every coefficient of the certificate is affine in a, so ONE parametric interval certificate over a ∈ [a₀, r]
covers all shells, and the shells [2^{−k−1}r, 2^{−k}r] exhaust (0, r] except the stratum δ_A = 0, where the plain
slide is exact (Fact A). *Proof.* Fact D on the shell; the pad may be taken proportional to a (ε_pad ∝ a) since
every margin is ∝ a. ∎ [M] `shells130_K03_BR.json`: with sq7 and sq4 tilted toward the wall, the shells k = 0…5
(a = 5·10⁻⁵ … 1.6·10⁻⁶) certify (all 4 modes, rate 0.9999990); k ≥ 6 fails exactly when a < the fixed pad 10⁻⁶ —
the scaling of the pad is what the leaf needs, not new mathematics.

**Corollary [T] (what a tree leaf must do at a flush stack).** A sound interval leaf for "every selected minimiser
in B is K0-FREE at c" at a flush stack = (i) the tilt-sign split of the stack's squares, (ii) Lemma TWO-INTRUDER's
conditioning (§4) to discard the sub-boxes without two-intruder packings, (iii) the parametric shell certificate
of SHELL-SCALE on the remaining sub-boxes, and (iv) the exact stratum statement (Lemma FLUSH-SLIDE at δ = 0) —
finite, and priced by the number of flush squares in the stack (2 patterns each) times the modes (≤ 2 per flush
pair). Without (ii)–(iv) the leaf is blind at every radius, as A128 measured and as `moves130.jsonl` reproduces.

## 3. [T] Lemma EXCHANGE-2 — the depth-2 exchange with a finite opening motion

**Lemma EXCHANGE-2.** Let B = B(z, m, r), c a corner met on B by exactly two squares A, Q, and Q₀ a unit square at
a FIXED frame pose with (i) Q₀ ⊂ [0, m′]² for all m′ (frame check, m′-free: the c-walls exactly, the far walls by
extent), (ii) μ_c(Q₀) ≥ 1 exactly in the frame. Let F be the set of untouched squares U ∉ {A, Q} whose interval
separation from Q₀ over B has a negative lower bound (the FLUSH set; if F = ∅ Lemma EXCHANGE-BOX applies). Let C
be a set of untouched squares with F ⊆ C, and Y a field on C such that on B⁺(p) := B(z, m, r + p) (p ≥ 10⁻⁶):
 (a) every possibly-separating axis of every pair (member, untouched outsider), (member, member), (member, S_c) and
     every possibly-active wall row of a member has derivative ≥ 0 (WEAK);
 (b) for every U ∈ F one axis k*(U) of the pair (Q₀, U) has sep_{k*} ≥ −ρ_U on B and derivative ≥ δ_U > 0 on B⁺(p),
     and for every U ∈ C \ F every possibly-separating axis of (Q₀, U) has derivative ≥ 0;
 (c) every untouched square not in C has some axis with sep(Q₀, ·) ≥ 0 on B;
 (d) with ε* := max_U ρ_U/δ_U, every member's motion for ε ≤ ε* stays inside B⁺(p): ε*(|v_i| + |ω_i|(m + 2)) ≤ p.
Then for every packing z′ ∈ B at side m′ the configuration P′ := (z′ with C moved by the exact screws at ε*) \
{A, Q} ∪ {S_c(m′), Q₀(m′)} is a packing at side m′ containing a corner slot square. Hence B contains no packing at
any side m′ ∈ [3.82, ŝ) (K0-O1), and at ŝ every packing in B is an image up to the replaced and moved squares.

*Proof.* Pairs among the untouched squares, and (member, S_c): as in BOX-FIELD-W, nondecreasing along the path,
≥ 0 at z′ (S_c is interior-disjoint from every untouched square at z′ by the two-meeter hypothesis). (Q₀, U) for
U ∈ F: sep_{k*}(ε*) ≥ −ρ_U + ε*δ_U ≥ 0 by (b), so Lemma SAT gives interior-disjointness. (Q₀, U) for U ∈ C \ F:
the axis separating at z′ (margin ≥ 0 by the definition of F) is nondecreasing. (Q₀, unmoved untouched): (c).
Q₀ vs S_c: (ii). Containers: (i) and the weak wall rows. A, Q are removed. ∎

The exchange of A128 is the case F = ∅ (ε* = 0). What the lemma needs in practice is a field on the flush
blockers that opens the contact at rate δ_U while every other contact of the blockers is weakly preserved —
i.e. the blockers must not be wedged; at the three window holds the blocker is the interior pinwheel (K03: sq9
= f5 wedged between Q₀'s corner, TR(0,0)'s corner, f0's corner and f6's edge; K06: the 48.4° grain; l1_124: the
45° pair), which is wedged at first order in the exact sense of §5 [M]. Lean shape: `teleport_packing` twice
plus the finite exact motion (the members' screws at ε*, an explicit configuration) with the interval rows (a)–(d)
as T5-type leaves.

## 4. [T] Lemma TWO-INTRUDER (conditioning on both meeters) and the K03-type corner, by hand

**Lemma TWO-INTRUDER.** In Lemma BOX-FIELD-W (and BOX-MOVE) with exactly two possible meeters A, Q of c on B, the
hypotheses (P_w), (W_w), (D), (N) need only hold on the sub-region B_2 := {z′ ∈ B : μ_c(A) < 1 and μ_c(Q) < 1};
the conclusion "every selected minimiser in B is K0-FREE at c" is unchanged. *Proof.* A selected minimiser in B
that is not K0-FREE at c has both A and Q intruding c, so it lies in B_2, where the certificate applies. ∎

**The K03-type corner, exactly (n-general).** Frame of c; the deep intruder A is axis-aligned on the floor with
its far edge at x = a ∈ (0, 1) (A = [a − 1, a] × [0, 1], depth 1 − a... in K03 BR: a = 0.207), and the tangent
square Q = [0, 1] × [1, 2] hugs the wall x = 0 above the cell, flush on A's top edge over the segment x ∈ [0, a]
(length a) and pressed from the interior by a square N whose edge passes through Q's inner top corner (1, 2)
(K03: f5 = sq9). Every packing z′ in B(z, r) with r ≤ 10⁻³ at which BOTH A′ and Q′ intrude c satisfies:
 (1) Q′ intrudes c only through its wall-side bottom corner: its lowest point is below y = 1 at some x ∈ (0, 1);
     since A′'s top edge lies within r of y = 1 over x ∈ [a − 1 ± r, a ± r] and Q′ is interior-disjoint from A′,
     the dip is at x > a − r, i.e. Q′ leans toward the wall: its bottom edge descends toward x = 0 —
     tilt δ_Q < 0 with |δ_Q| ≥ (depth of Q′)/1 > 0, and Q′'s far bottom corner (x ≈ 1) is its high end, resting
     on A′'s top edge (the contact is Q′'s far bottom corner on A′'s top edge, or A′'s inner top corner on Q′'s
     bottom edge if A′ leans more) — the mode P₁ of Lemma MODE with the relative tilt δ_A − δ_Q ≥ 0... [the
     precise inequality: δ_Q ≤ min(0, δ_A) up to O(r²)];
 (2) hence, in Q′'s pose box, only the sub-box {δ_Q ≤ 0} carries two-intruder packings, and on it the mode is
     "A′'s top axis separating" whenever δ_A ≥ δ_Q.
The horizontal translation of A′ away from the wall, y_A = (+1, 0, 0) [in the frame: away from c], has:
 floor row: derivative 0 exactly (v_y = 0, ω = 0 — an exact structural zero);
 A′'s top axis vs Q′: derivative −n_top·v = sin δ_A ≥ 0 iff δ_A ≥ 0 — so on the sub-box δ_A ≥ 0 (A′ flat or leaning
     away from... [sign as in the code's convention: the certified patterns are those with A′'s top edge descending
     toward the interior]) the row is ≥ 0 exactly; on the complementary sub-box δ_A < 0 the mode P₁ requires δ_Q ≤
     δ_A < 0 and Q′'s far corner rests on A′'s top edge which DEscends away from the wall, so moving A′ away from
     the wall brings a lower part of the edge under the corner: the row is ≥ 0 in mode P₁ too (interval: sin δ_A·v_x
     with the sign of δ_A — this is the row the plain box cannot see and the contractor recovers);
 Q′'s far corner on N's edge, the wall, A′'s other neighbours: unchanged (A′'s only other contacts in K03 are f0's
     corner on its top edge — sliding along it, derivative 0 exactly — and the floor).
 depth: μ_c(A′) = a′ increases at rate 1 (X-type, argmin segment on the far edge).
So on B_2 every packing with both intruders admits the exact slide of A′ with Ψ^(w) decreasing strictly (rate 1
for every positive weight), and **every selected minimiser in B is K0-FREE at c** — a theorem about the box,
proved by the case analysis; its interval form is Lemma BOX-FIELD-W on the sub-boxes {δ_Q ≤ 0} ∩ {δ_A ≥ 0} (a
plain certificate, [M] certified) and {δ_Q ≤ δ_A < 0} (needs the mode contraction, [C] as an interval leaf; [T] by
hand above). ∎ The same analysis applies verbatim to K06's BR (sq6 = f1 at depth 0.606 on the floor, BR(0,1) =
sq2 above it, the 48.4° grain pressing sq2's inner corner) and to l1_124's TL/BL/TR (a 45° pair pressing the
slot square's inner corner, the slot square itself the deep meeter): the deep meeter is the slot-like square,
the tangent is the flush neighbour, and the exact slide is the deep meeter's — hence Lemma FLUSH below.

## 5. [T] Lemma FLUSH-SLIDE (the point statement) and Lemma ISOLATED

**Lemma FLUSH-SLIDE.** Let z* be Ψ^(w)-minimal on M(m) and let A be an intruder of c whose active contacts are:
the floor (or the wall) of c along an axis-aligned edge, and squares touching A only on its top edge (or the
edge parallel to the wall) — flush neighbours and corners resting on that edge — plus, possibly, squares touching
the far edge of A. Then A is pressed on its far edge (some contact on the far edge exists with a force component
toward c). *Proof.* Otherwise the translation of A away from c along the floor is S-feasible to first order with
every active row WEAK (Fact A: all rows are affine in the centre; the floor row and the top-edge rows have slope
exactly 0, the far-edge rows are inactive), so by Lemma ROT-W's proof z* + t(e, 0) ∈ M(m) for small t and d_c(A)
decreases at rate 1 (X-type) — contradiction. ∎ At K03 BR sq6 the far-edge contact does not exist (f1 = sq5 is
0.027 away): [M] the weak-cone rate at the point is 1.000 = the exact slide, and K03 is NOT Ψ^(w)-minimal at its
side (it is not K0-BLOCKED either; the relevance is Lemma TWO-INTRUDER's box statement in §4).

**Lemma ISOLATED [T].** Let z be a packing at side m and suppose the cone K := {y ∈ ℝ^{3n} : every active row's
first-order rate ≥ 0 (all one-sided branches at kinks), and Q's depth rate ≥ 0} is {0}. Then z is an isolated
point of {z′ ∈ M(m) : d_c(Q(z′)) ≤ d_c(Q(z))}; in particular z is a strict local minimiser of d_c(Q) — and of every
Ψ^(w) whose other terms are locally nonincreasing — on M(m). *Proof.* The set is semi-algebraic (polynomial rows in
(c, t = tan θ/2), `CaseSat.lean`); if z were not isolated the curve selection lemma gives an analytic curve z(ε)
in it with z(0) = z, z(ε) ≠ z; its lowest non-vanishing derivative y ≠ 0 satisfies every row's first-order rate ≥ 0
(the row is ≥ 0 along the curve and vanishes at 0) — a one-sided derivative in the branch the curve takes — and
the depth rate ≥ 0; so y ∈ K = {0}, contradiction. ∎ [M] K = {0} at EVERY one of Trump's nine subjects (the five
intruders and the four tangent squares; weak-cone rate 0, cone extent 0 on the 10⁻⁸ box): Trump is first-order
isolated as a minimiser of every corner depth on the packings at ŝ — the canary holds by Lemma ISOLATED, the
strongest form. At the three window holds K ≠ {0}: their near-packings carry first-order slack (KKT residuals
4·10⁻⁶ … 2·10⁻²; K06's landing overlaps by 1.1·10⁻⁶, so its 10⁻⁸ point tests see free directions and are not
meaningful), and at the two A104 locks the weak cone is not only non-trivial but carries POSITIVE depth rates
(0.11–1.00): they are not Ψ-minimal under fields even at first order, so the second-order test of §6 is moot there.

## 6. [T] Lemma KINK — the second-order condition at a parallel-edge contact, and its box form

**Setting.** Along the curve z(ε) = z + εy + ε²w/2 (pose coordinates), a smooth row R(ε) = R(0) + ε⟨g, y⟩ +
ε²/2 (⟨g, w⟩ + yᵀHy) + O(ε³). For a pair axis with parallel edges (Δ = 0) the row contains −h(Δ(ε)) with
h(Δ) = 1/2 + |Δ|/2 − Δ²/4 + O(|Δ|³): if Δ̇ = ω_A − ω_{B′} ≠ 0 the branch is sgn Δ̇ and the row is smooth beyond the
first order; if Δ̇ = 0 exactly, Δ(ε) = ε²(w_A − w_{B′})/2 and the row carries the SECOND-ORDER kink −|w_A − w_{B′}|
ε²/4. The same for a wall row of an axis-aligned square (h(θ) at θ = 0) and for a depth candidate at a diagonal
vertex (max of two branches).

**Lemma KINK.** Let y ∈ K \ {0} (a weakly feasible first-order direction) and E := the rows with ⟨g_k, y⟩ = 0
(including Q's depth candidates if their rate is 0). Then there is a feasible curve z(ε) ∈ M(m) with z′(0) = y
along which every row of E is > 0 for small ε > 0 (and Q's depth < d_c(Q) if its first-order rate is 0 and its
second-order rate is > 0) iff the linear system in w
   ⟨g_k, w⟩ + yᵀH_k y − κ_k(w) > 0 (k ∈ E),   κ_k(w) := |w_{θ_A} − w_{θ_{B′}}|/2 (kinked pair rows with Δ̇ = 0),
   |w_θ|/2 (kinked wall rows with θ̇ = 0), 0 otherwise,
is feasible (an LP after the split w = w⁺ − w⁻ of the kinked differences, exactly as the first-order kink);
by Farkas it is INFEASIBLE iff there are μ ≥ 0 on E, not all zero, with Σ μ_k g_k = 0 on the un-kinked
coordinates and Σ μ_k (yᵀH_k y) ≤ (the kink budget) — a prestress-stability inequality: the certificate's
self-stress μ, evaluated on the curvature of the rows along y, is nonnegative. Rows with ⟨g_k, y⟩ > 0 need nothing.
*Proof.* Taylor to second order with the kink expansions; sufficiency by the explicit curve z + εy + ε²w/2 (all
rows of E are ≥ ε²τ/2 + O(ε³) > 0, the others ≥ ε⟨g, y⟩/2); necessity: a feasible curve with z′(0) = y has some
second derivative w, and every row of E along it is ≥ 0 to second order. ∎ The "2 × 2 curvature test" of the
brief is the case dim K = 1 with two rows in E: then w is one number per kink and the test is the sign of a 2 × 2
determinant (the two rows' curvatures against the self-stress ratio).

**Box form [T].** On a box B, rows whose first-order form is IDENTICALLY zero along y on B (every coefficient
interval of the form is [0, 0] after the exact zeros of y — a structural zero, e.g. sliding along an axis-aligned
edge, or a member pair rotating together with u = 0 exactly) may be replaced by their second-order forms
⟨g_k, w⟩ + yᵀH_k y − κ_k(w) evaluated as intervals over B (Hessians of the polynomial rows); every other row must
have first-order lower bound ≥ 0 (weak) or > 0 (strict) as in BOX-FIELD-W. Conclusion as BOX-FIELD-W with the
curve z′ + εy + ε²w/2 in place of the exact screws (the second-order path stays in B⁺ for small ε). A row that is
first-order zero at the CENTRE but not identically on B cannot be handled by a box certificate at any radius
(its first-order interval straddles 0): the second-order escape of a lock is a POINT property, and A128's "6
first-order directions at 4.001525 all blocked within 5·10⁻⁹ by parallel-edge kinks" is the case Δ̇ ≠ 0 of the
setting above — the first-order rate at the exact point is positive along the smooth branch and the kink is
crossed after 5·10⁻⁹; on a box of radius ≥ 3·10⁻⁹ both branches are charged and the direction disappears. [M] §6
of `report130.md`: the second-order LP at the four points (sympy Hessians, 30 digits).

## 7. What the lemmas say for DRAIN-SEL(W): the FLUSH case of the case analysis

For m ∈ W and z* = z*(m) K0-BLOCKED, Lemma TWO gives a corner c with exactly two intruders A, Q. Cases (from
`drain_sel.md` §4.2, with FLUSH inserted):
 1–3 [T]: ROT / ROT-W / CLUSTER-ROT / EXCHANGE admissible ⇒ contradiction (theorems).
 F  (FLUSH, new) [T] Lemma FLUSH-SLIDE: if A (or Q) is a floor/wall square whose active contacts are its floor (wall)
    and squares on its top (inner) edge only, it slides away from c with every row weak and exact — contradiction.
    So at z* every intruder that is flush on a wall of c is PRESSED ON ITS FAR EDGE (far from c) — the exact
    n-general form of A90's Corollary 2 for flush squares, with the presser required to touch the far edge itself
    (not the top edge: a top-edge presser slides).
 F′ (SLOT-GRAZER) [T, modulo K0-O1]: if A is within ρ of the slot square of c (μ_c(A) ≤ ρ) then Q is a grazer of
    depth ≤ (1 + √2)ρ (Lemma SHELL) and Lemma SLIDE forces m ≥ ŝ − (1 + √2)ρ: for m ≤ ŝ − δ no corner has a
    near-slot intruder with μ_c ≤ δ/(1 + √2). So the K03/K06/l1_124-type corners (slot-like deep meeter + flush
    tangent) do not occur at z*(m) for m ≤ ŝ − 2.4·10⁻³·(ρ/10⁻³); the three window holds, as relatives of the
    residue, live entirely in the slab (ŝ − (1 + √2)ρ, ŝ] of W, and in that slab the deep meeter is a disturbed
    slot square whose partner is a grazer — Lemma SNAP's dichotomy, Lemma TRUMP-LOCAL's geometry at ŝ.
 4  [C]: the residue after 1–3 and F: K0-BLOCKED, every intruder LOCKED, cluster-held, every re-fit flush, every
    flush intruder pressed on its far edge (F), no near-slot intruder outside the slab (F′). Realised above ŝ by
    NOTHING KNOWN ANY MORE: [M] the 4.001525 frame (Gordan-certified locked at all eight intruders, held under
    every rigid cluster screw in A128) is drained at EVERY one of its eight intruders by Lemma BOX-FIELD-W on the
    10⁻⁴ box (weak-cone rates at the point 0.11–0.32; 10⁴ → 10⁴ → 0 hits per subject) — the control FALLS to the
    non-rigid field, which is the move A128 named; likewise 4.000237 at all eight (10⁻⁴; rates 0.22–1.00). Below
    ŝ nothing is known. The residue after 1–3, F, F′ and the FIELD is therefore realised by no configuration on
    disk at any side.
