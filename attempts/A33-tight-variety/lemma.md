# A33 — the equality-pigeonhole lemma (formal statement)

Advisor (Fable), 2026-08-26. Statement style and care level: docs/results.md Theorem 1, which this
generalises (Theorem 1 is exactly the case eta < 0, i.e. "no packing at all").

Throughout, a *guard field* on the closed square [0,s0]^2 is a finite non-negative atomic measure
mu = sum_i w_i delta_{p_i}, p_i in [0,s0]^2, w_i >= 0, satisfying

  (F1)  mu(Q) >= 1 for every closed unit square Q subset [0,s0]^2 (any orientation);
  (F2)  mu([0,s0]^2) = M = 11 + eta  for some eta in R.

No optimality is required anywhere below: ANY feasible field gives its own eta = M - 11, and a
smaller total gives a stronger conclusion. The infimum over feasible fields is tau*(s0), so the
best achievable constant is eta(s0) := tau*(s0) - 11; certified fields give certified upper bounds
eta_cert >= eta(s0), and exact fractional packings (A19-style) give lower bounds — the bracket
[tau_lb - 11, M_cert - 11] is the deliverable of task T1.

## Lemma A33.1 (equality pigeonhole)

Let mu satisfy (F1)-(F2) with eta >= 0, and let S_1, ..., S_11 be pairwise disjoint closed unit
squares contained in [0,s0]^2. Then

  (i)  for every non-empty I subset {1,...,11}:   |I| <= sum_{i in I} mu(S_i) <= |I| + eta;
  (ii) mu([0,s0]^2 \ union_i S_i) <= eta.

In particular each mu(S_i) lies in [1, 1+eta], each pair satisfies mu(S_i) + mu(S_j) <= 2 + eta,
and the mass escaping the union ("wastage in guard units") is at most eta.

*Proof.* The S_i are pairwise disjoint mu-measurable sets, so by additivity

  sum_{i=1}^{11} mu(S_i) + mu([0,s0]^2 \ union_i S_i) = mu([0,s0]^2) = 11 + eta.

Each mu(S_i) >= 1 by (F1). Dropping the (non-negative) escape term and the terms outside I,

  sum_{i in I} mu(S_i) = 11 + eta - mu(escape) - sum_{i notin I} mu(S_i)
                      <= 11 + eta - 0 - (11 - |I|) = |I| + eta,

which is (i); taking I = {1,...,11} in the same identity gives mu(escape) = 11 + eta -
sum_i mu(S_i) <= eta, which is (ii). QED

Remarks.
(a) eta < 0 in (F2) makes (i) with I = {1,...,11} read 11 <= 11 + eta < 11, a contradiction: no
    11 disjoint closed unit squares exist, which is Theorem 1. So A33.1 is the equality-case
    refinement of Theorem 1 that the campaign never exploited.
(b) The subfamily bound (i) is strictly stronger than the per-square caps combined: two squares
    jointly cover at most 2 + eta, not 2 + 2 eta. The joint k-family constraint lives on the
    k-fold placement space and shrinks the admissible set faster than the product of the
    single-square varieties (task T2 measures this).
(c) Only feasibility of mu is used. LP optimality, uniqueness, complementary slackness play no role.

## Corollary A33.2 (application to packings; Theorem-1 scaling)

Let mu satisfy (F1)-(F2) with eta >= 0 on [0,s0]^2. Let 0 < s0' < s0 and let T_1, ..., T_11 be
unit squares with pairwise disjoint interiors contained in [0,s0']^2 (an 11-packing at side s0'),
with centres c_i and orientations theta_i. Put lambda = s0/s0' > 1 and let S_i be the unit square
with centre lambda c_i and orientation theta_i. Then the S_i are pairwise disjoint closed unit
squares in [0,s0]^2, and Lemma A33.1 applies to them verbatim:

  mu(S_i) in [1, 1+eta] for each i,   sum_{i in I} mu(S_i) <= |I| + eta,   escape <= eta.

*Proof.* As in Theorem 1: scaling the packing by lambda sends the container into [0,s0]^2 and each
T_i to a closed square of side lambda > 1 with pairwise disjoint interiors; S_i is the concentric
unit square, contained in the OPEN interior of its lambda-square, so the S_i are pairwise disjoint
closed sets and each is a closed unit square in [0,s0]^2. Apply A33.1. QED

Remarks.
(d) At side exactly s0 the closed squares of a packing may touch, and an atom on a shared boundary
    is counted in every square containing it, so the UPPER bounds in (i) can fail as literally
    stated (the lower bounds mu(S_i) >= 1 always hold). The scaled form above is what we use:
    since the repo's s' = 3.877084 is strictly larger than the true algebraic s-hat =
    3.87708359002281..., a field at s0 = 3.877084 constrains every packing at side <= s-hat,
    including Trump's own, through Corollary A33.2 with lambda = s0/s-hat > 1. Alternatively the
    conclusions hold at side exactly s0 whenever no atom of mu lies on the boundary of two packing
    squares simultaneously (checkable for a given field; true generically).

## Corollary A33.4 (small eta kills n+1; the s(12) by-product)

Let mu satisfy (F1)-(F2) on [0,s0]^2 with eta < 1. Then no 12 pairwise disjoint closed unit
squares fit in [0,s0]^2, i.e. (by the Theorem-1 scaling argument verbatim with n = 12)
s(12) >= s0. More generally eta < k gives s(11+k) >= s0.

*Proof.* Twelve disjoint closed unit squares would have total mass >= 12 > 11 + eta = mu(total). QED

Remark (f). "eta(s) < 1" is exactly the statement that the guard field excludes 12-packings at
side s. Since eta(3.877084) <= 0.4254 is CERTIFIED (T1's sealed field, exact total
44630467/3906250 = 11.4254 < 12, feasibility PASS by certs/verify_measure.py, independently
re-verified), we have, unconditionally and machine-checked: **s(12) >= 3.877084**, improving the
previously recorded s(12) >= 3.7889 (Stromquist + monotonicity) by +0.088. The pure measure
method's ceiling for this statement is the crossing tau*(s) = 12, located by T3b.

## Definition (tight varieties)

Fix mu satisfying (F1)-(F2) on [0,s0]^2 and write P_{s0} for the admissible placement space
{x = (c, theta) : Q(x) subset [0,s0]^2} (parametrised as always by t = tan(theta/2), C4/D4 reduced).

  T_eta(mu)   := { x in P_{s0} : mu(Q(x)) <= 1 + eta }          (single-square tight variety)
  T^k_eta(mu) := { (x_1..x_k) : Q(x_i) pairwise disjoint, sum_i mu(Q(x_i)) <= k + eta }.

By A33.2, every square of every 11-packing at side < s0 lies (after lambda-scaling) in T_eta(mu),
and every k-subset of its squares lies in T^k_eta(mu). Note T^k_eta is strictly smaller than the
disjoint-pairs subset of T_eta^{x k} by Remark (b).

## Lemma A33.3 (multi-field intersection)

Let mu^(1), ..., mu^(m) each satisfy (F1) on [0,s0]^2 with totals 11 + eta_j, eta_j >= 0. Then for
every 11-packing at side s0' < s0, the scaled squares S_i of Corollary A33.2 satisfy the
conclusions of A33.1 SIMULTANEOUSLY for every j; in particular every S_i lies in

  T_cap := intersection_{j=1..m} T_{eta_j}(mu^(j)),

and every k-subset lies in intersection_j T^k_{eta_j}(mu^(j)).

*Proof.* A33.1/A33.2 applied to each field separately; the packing is the same. QED

Remark (e). The fields need share nothing (different supports, different objectives, perturbed row
generation): each is only required to be individually feasible. This is what makes the statement
stack: m near-optimal fields with distinct tight sets pin the packing to the intersection, which
task T2 measures. The verification burden is m independent runs of the standard feasibility
verifier (certs/verify_measure.py semantics) plus exact totals.

## How the varieties are certified (for T2)

The coverage function x -> mu(Q(x)) is piecewise constant on the arrangement cells of the atom
membership surfaces. The interval machinery of certs/verify_measure.py certifies, on a parameter
box B in (t, cx, cy), a lower bound m_low(B) <= min_{x in B} mu(Q(x)) by exact rational
arithmetic. Any box with m_low(B) > 1 + eta is EXCLUDED: no square of any 11-packing at side
< s0 has its scaled placement in B. The certified object is therefore an exclusion cover E
with T_eta(mu) subset P_{s0} \ E; the reported "volume of the tight variety" is the outer
measure of the uncovered region (an upper bound on the true variety's volume). Canary: the
lambda-scaled Trump placements must land in the uncovered region of every field.
