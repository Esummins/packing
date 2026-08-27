# A35 theory: escape-complex stratification of Trump's jam (Fable, 2026-08-27)

T0 (per-stratum soundness + composition) and T1 (truncation lemma draft) for I-L15.
Builds on: drain_lemma.md v3 (D1, D2, D3', T3), A22's certificate (z-hat, 38 geometric rows,
r_N = 1/2000, multiplier identity, 68 positive-spanning certificates), structure_lemmas.md L1-L7.

Convention. A22 variable layout z = (c_i, theta_i)_{i=0..10}, z[33] = s, NV = 34. The 38
GEOMETRIC rows g_1..g_38 (indices 0..37 of krawczyk_cert.json constraints; 20 wall + 16 edge +
2 dist) are the physical active constraints of the jam, written g_k >= 0, all g_k(z-hat) = 0.
The 4 angeq rows are A22 surrogates and are NOT strata coordinates (a flush contact = its one or
two geometric rows). Distinct contact EDGES: 24 (14 flush with 2 rows, 10 point with 1 row).
"Feasible" = S-feasible for a selection consistent with the region under discussion, in the sense
of D3' (dominance rows make selected rows equal true SAT separation); every statement below is
per-selection, with menu completeness (D3') covering ties exactly as in T3.

Constants measured at z-hat in float recon (scratchpad recon.py/recon2.py, TO BE CERTIFIED by M1/M2;
those that survive exact verification get promoted):
  rank(A) = 34 (A = 38x34 Jacobian of the geometric rows at z-hat); self-stress dim = 4,
    self-stress support = 20 of 38 rows; NO nonnegative nonzero self-stress exists (LP infeasible);
  e_s in cone{grad g_k} with uniform floor: exists lambda* >= 0, A^T lambda* = e_s,
    min_k lambda*_k = 0.047644, sum lambda* = 4.3535 (matches A30's 0.0476 on the 42-row polytope);
  sparsest support of a valid lambda: 32 rows; equivalently max break-set preserving the cone: 6;
  k=1 strata: 18 mechanisms (1 dof), 20 empty; k=2: 153 two-dof, 406 one-dof, 144 empty;
  k=3: 816/3956/3216/448 with dof 3/2/1/0;
  min row-cuts of the contact graph (wall nodes as connectors, L6-legal): x-axis 5 rows, y-axis 3
    rows ({22,23,25}) — CORRECTED BY M1: these are valid cuts but not minimal; true minima are
    x = 3 rows {11,19,34}, y = 2 rows {19,25}, joint = 4 rows {11,19,25,34};
  nearest non-contact pairs at z-hat (SAT gap): (6,7) 0.02487, (8,9) 0.02487, (3,4) 0.03256,
    (7,10) 0.11878, (2,10) 0.23187, (5,10) 0.23600, (1,7) 0.25500, rest >= 0.636;
  nearest new WALL contact 0.54864 (sq9 corner2 to y=s).

BASIS REPAIR (2026-08-27, after M4 — supersedes "38 rows" above where stratification is concerned).
M4 exposed and the lead verified in exact arithmetic: (i) pair (1,3) is a genuine 14th contact —
corner-corner at (1,1), centre distance exactly sqrt2 (the L5(a) extremal case) — ABSENT from
A22's rows; (ii) rows 36/37 (dist) are centre-distance surrogates for the FLUSH contacts (0,1),
(0,3) (centre distance exactly 1): valid inequalities (two disjoint unit squares have centre
distance >= 1 by incircles), so every VALUE certificate that used them (A22, M2's (W)/(E)) remains
sound; but as stratum equalities they do not pin the contact (rotation interpenetrates at d = 1).
STRATIFICATION BASIS v2: rows 0..35 + proper flush sep-row pairs for (0,1), (0,3) + the two
orthogonal separation branches of (1,3) (a broken corner-corner contact = max of the two branch
gaps > 0; each branch is a smooth selection, tie covered by both, per D3'). All enumeration-level
statements (T1-a constants, survivor lists) must be restated on v2 — M1b task. A22's optimality
theorem itself is unaffected (missing constraint = optimality proved over a superset).

## T0.1 Stratification (definitions; exact closed cover)

For B subseteq {1..38} ("broken set", M = complement "maintained") define the CLOSED stratum

  Sbar(B) = { z feasible : g_m(z) = 0 for m in M,  g_b(z) >= 0 for b in B },

and the open stratum S(B) with g_b > 0. Facts (immediate):
 (i)  every feasible z near the jam lies in Sbar(B(z)) with B(z) = {k : g_k(z) > 0} — the closed
      strata COVER; a boundary point of S(B) (some g_b = 0) lies in Sbar(B') for B' subsetneq B, so
      overlaps are consistent (both certificates apply). Touching-vs-open is thereby discharged:
      we only ever certify closed strata.
 (ii) GAINED contacts (a non-contact pair's gap hitting 0, or a new corner-wall touch) do NOT
      change membership in Sbar(B) and do not affect a VALUE certificate (T0.2-V below); they only
      enter (a) critical-point tests, where candidate gained rows must join the possibly-active
      menu (exactly A30's straddling menu), and (b) route-following dynamics (M4). The escape
      complex is therefore indexed by B alone for value bounds, and by (B, gained menu) for FJ
      exclusion.
 (iii) Local dimension: if rank(grad g_M at z-hat) = 34 the closed stratum meets a neighbourhood of
      z-hat in {z-hat} only ("EMPTY stratum": a Krawczyk isolation certificate on a square retained
      subsystem proves Sbar(B) cap box = {z-hat}, where sigma = s-hat). Else the stratum is locally
      a manifold of dim d = 34 - rank ("MECHANISM stratum", d <= |B|). Rank-degenerate points deeper
      in the stratum are handled by the rank-drop branch of T0.2-F.

N* is ASSEMBLED, not assumed: N* := union of the certified reach regions of the stratum
certificates (each given by inequalities: retained equalities, gap caps g_b <= G, validity/dominance
margins, candidate-pair guards). No metric radius appears except inside individual certificates.

## T0.2 Certificate forms (each sound on its own; all interval/exact-verifiable)

(E) EMPTY-STRATUM certificate. A Krawczyk contraction for a 34-row retained square subsystem on
box(z-hat, h) proves the only point of Sbar(B) in the box is z-hat. Sound by the Krawczyk
uniqueness theorem; verified exactly as in A22/recheck.py. Cost: one preconditioned Krawczyk
step per stratum (~0.2 s measured in A30).

(V) VALUE (one-shot dual) certificate. Let R be any closed region, mu in R^M free-signed,
nu in R^B_{>=0}, eta >= 0 on any further feasibility rows (containment, guards). If interval/exact
arithmetic certifies

   inf_R [ s - sum_M mu_m g_m - sum_B nu_b g_b - sum eta_u g_u ] >= s-hat - eps,

then every feasible z in R cap Sbar(B) has s >= s-hat - eps  (on the stratum g_m = 0 kills the mu
terms regardless of sign; the nu, eta terms are >= 0 by feasibility). One line, no CQ. Gained
contacts harmless by T0.1(ii). With mu = 0 allowed the same certificate covers ALL strata in R at
once whenever the multipliers on maintained rows can be taken >= 0.

(A) ASCENT IDENTITY and the INFLATION LEMMA (the quantitative mountain-pass at the jam).
Let lambda* >= 0 be rational with residual rho := A(z-hat)^T lambda* - e_s, ||rho||_1 <= r_res
(A22 achieves 1e-30 for its own lambda; M2 re-emits lambda* with the 0.0476 floor). Define

   Phi(z) = s - sum_{k=1..38} lambda*_k g_k(z).

Then grad Phi(z-hat) = -rho (tiny), Phi(z-hat) = s-hat, and for every FEASIBLE z:

   s(z) >= Phi(z) + lambda_floor * G(z),   G(z) := sum_k g_k(z),  lambda_floor := min_k lambda*_k.

Second-order interval bound on box(z-hat, r): by the mean-value form with the interval Hessian
H_box of Phi (t3lib order-2 jets), Phi(z) >= s-hat - ||rho||_1 r - Hbar r^2, Hbar computable. Hence

   (A1)  s(z) >= s-hat + lambda_floor G(z) - Hbar r^2 - r_res r   on box(r), z feasible.

Consequence 1 (first-order ascent on every stratum): for a mechanism flex v (A_M v = 0, retained),
ds/dtau = e_s.v = sum_{b in B} lambda*_b (grad g_b . v) >= lambda_floor * d/dtau sum g_b — every
escape is uphill at rate >= 0.0476 per unit of total gap opening, on EVERY stratum simultaneously.
Consequence 2 (Layer-1 inflation): combine (A1) with QUANTITATIVE RIGIDITY: if all 38 gaps
g_k(z) <= eps on box(r) and the retained=all system's Krawczyk operator contracts with ratio
beta(r) < 1 and preconditioner norm kappa = ||Y||_inf, then ||z - z-hat||_inf <= kappa eps/(1-beta).
So on box(r): EITHER G(z) >= (Hbar r^2 + r_res r)/lambda_floor (then s >= s-hat by (A1)), OR every
gap is < that bound and z lies within radius kappa(Hbar r^2 + r_res r)/(lambda_floor (1-beta)) of
z-hat; if that radius <= r_N = 1/2000, A22's theorem finishes: s >= s-hat with equality iff
z = z-hat. This proves sigma >= s-hat on the FULL box(r_1) for the largest r_1 satisfying the
consistency inequality — one certificate, no cells, all strata at once. CAVEAT (honest): the
constants make r_1 of the same ORDER as r_N (curvature-limited); float estimate
kappa/(1-beta) ~ 30, Hbar ~ 10 gives r_1 ~ sqrt(r_N lambda_floor/300) ~ 3e-4. M2 computes the
certified r_1; the value of (A) is Consequence 1 (the per-stratum engine) plus re-centering it
ALONG strata (low-dim continuation) rather than in the full 34-dim box — that is the entire point
of I-L15: re-centering cost c^d per e-folding with d = stratum dof <= 6 (T1), not c^33.

(W') MENU-COMPLETE WEDGE (added 2026-08-27 after M1b's two flat seeds; the sound first-order test
on basis v2). The v2 escape-cone tests are incomplete in two ways, both repairable at first order:
 (i) AUXILIARY VALID ROWS: any polynomial inequality valid on ALL packings and ACTIVE at z-hat may
     join the possibly-active set of every cone/wedge/FJ test — in particular v1's dist rows
     d^2(c0,c1) >= 1 and d^2(c0,c3) >= 1 (valid by incircles, active: d = 1 exactly). An escape
     direction v must satisfy grad(row) . v >= 0 for every such active valid row. Seed {0,2} dies
     here: rate = -0.8165 < 0 along its kernel (lead's hand computation, to be IV-certified).
     Soundness: identical to any other g >= 0 row; these rows are never stratification coordinates
     (never "broken"), they are permanent inequality rows.
 (ii) TIED DOMINANCE ROWS: the six repaired rows have their contact corners at edge ENDPOINTS
     (dominance margin 0 to 1e-61 — M1b sec. 7), so per D3' menu completeness every consistent
     selection's dominance rows are active-at-z-hat constraints and join the test per selection;
     a stratum dies if EVERY selection in its tie menu has escape cone {0} (Motzkin dual per
     selection = the (W) certificate, selection-resolved). Structural support: Fact 0 — two
     maintained contact points of one pair + feasibility force flush = zero relative tilt, which
     the pivot flexes violate; expect the dominance rates to encode exactly this at first order.
     A22's ORIGINAL rows are immune (tangential margins >= 0.015: their dominance rows are
     strictly slack near z-hat) — the artifact is confined to the repaired upright-block rows.
If a selection's cone is still nontrivial after (i)+(ii), the residual flex is a genuine sliding
motion and falls to (C)/(V) with a second-order interval bound on the pair subsystem.

(C) CONTINUATION certificate (mechanism strata; the workhorse). On a mechanism stratum of dof d,
parametrize by the broken gaps (or pseudo-arclength): validated boxes N_1..N_L along the stratum,
each carrying (i) a Krawczyk contraction of the retained square system in the 34 - d pinned
directions (the stratum is a certified graph over the d-dim parameter box), and (ii) a LOCAL
ascent/value certificate: rational lambda^(j) >= 0 on the retained rows of segment j with
A(N_j)^T lambda^(j) - e_s residual interval-bounded, giving s >= s(entry) + floor^(j) * (gap
opening) - quad remainder on N_j, chained monotonically from s-hat at the jam end. Sound by (V)
applied per segment; composes because segment j's exit face is segment j+1's entry face and
s-values only ever get lower-bounded. Terminates at: (a) a gained contact (cascade: hand off to
the stratum with the new contact in M — its jam-end value is the exit value, chain continues);
(b) re-jam (rank back to 34: an (E)-type isolation around a NEW critical point — the bidirectional
protocol: refute by Krawczyk/value, or it is a genuine new CP with s > s-hat, certified uphill);
(c) certified margin sigma >= s-hat + delta_stop (route leaves the basin ceiling; handoff to the
global program — the ridge); (d) slack: all 18 pair rows broken with uniform positive gaps on the
segment — interior minima excluded there by D2 directly (see T0.3).

(F) FJ-EXCLUSION certificate (for the composition's interior-minimum case; Motzkin form with
equalities). At an interior local min z* of sigma over N* cap D_0 lying in S(B), FJ holds for the
stratum NLP (min s s.t. g_m = 0 m in M_act, g >= 0 possibly-active others incl. gained candidates):
lambda_0 grad s = sum_M mu_m grad g_m + sum_act lam_a grad g_a, mu free, lam >= 0, not all zero.
KILL TEST: exhibit y with grad s.y < 0, |grad g_m . y| <= tau_m (m in M), grad g_a . y > 0 for all
possibly-active inequality rows, verified in interval arithmetic over the region, TOGETHER WITH a
certified multiplier bound ||mu||_1 <= Mu (from the segment's Krawczyk data: mu solves a
well-conditioned linear system on a mechanism segment) such that Mu * max tau_m < lambda_0-side
slack. Degenerate branch: if rank(grad g_M) drops inside the region, mu-nontrivial FJ points with
lambda_0 = lam = 0 are possible; such points are flagged RANK-DROP and the region is subdivided or
the (V)/(C) value form is used instead (value certificates are immune). The lambda_0 = 0,
lam != 0 branch is a nonnegative self-stress on retained+gained rows: at z-hat NONE EXISTS on the
38 rows (recon LP, to be certified by a strict Farkas witness in M1); over a region it is excluded
by the same y-test (dot stationarity with y). 

LEMMA (lambda_0 = 0 branch, region form; discharges M3 gap G-6). Let y satisfy the interval-
verified Farkas conditions of a cone-dead stratum's certificate on a region R: grad g_m . y > 0
for every row m that can be active on R (retained + gained menu). Then not only is there no FJ
point with lambda_0 > 0 in R (dot stationarity with y), but also no FJ point with lambda_0 = 0:
such a point carries lambda >= 0, lambda != 0, sum_m lambda_m grad g_m = 0 supported on active
rows, and dotting with y gives 0 = sum lambda_m (grad g_m . y) > 0 — contradiction. The e_s . y < 0
condition is not even used. Hence M3's 34 certificates kill BOTH FJ branches on box(z-hat, h_W)
for every cone-dead break set; cone-alive break sets are pinned to {z-hat} by (E)/(W); so the
lambda_0 = 0 branch is empty on the whole box except at z-hat itself, where FJ holds legitimately
(z-hat is the minimiser). One paragraph, no new computation. QED

## T0.3 Composition theorem (assembled-N* mountain pass)

THEOREM (composition; sound given the ingredient certificates). Let K* be a compact region,
K* = union of finitely many certified pieces, such that
 (1) [inner] box(z-hat, r_N) subseteq K* with A22's certificate;
 (2) [strata] every piece P is covered by an (E), (V), (C) certificate concluding "sigma >= s-hat
     on P cap D_0", or by an (F)+D2 pair concluding "no interior local minimum of sigma in P";
 (3) [collar] every point of the topological boundary of K* lies in a piece whose certificate
     gives sigma >= s-hat + delta_stop there (the ridge collar).
Then min over K* cap D_0 of sigma = s-hat, attained only at z-hat.
PROOF. K* cap D_0 cap {sigma <= s-hat} is compact, nonempty (z-hat); a minimiser z* exists (D1
argument verbatim). If z* is in a piece of type (2)-value or the collar, sigma(z*) >= s-hat with
the equality case tracked by the certificates ((E)/A22 give equality only at z-hat). If z* is
interior with an (F)+D2 piece: if all pair gaps at z* are positive, an arbitrarily small D2-shrink
about the container centre stays in the (open) piece and strictly decreases sigma — contradiction
(this needs only eta small, not the full delta/(2 sqrt2 sigma) step: gaps survive for every
eta' <= eta, sigma strictly drops for every eta' > 0); if some pair contact is active, z* is an FJ
point of its stratum system with actives among retained+gained rows — excluded by (F). QED.
Remarks. (a) The lambda_0 = 0 branch is inside (F). (b) Gained contacts are inside (F)'s menu and
harmless to value pieces. (c) The theorem consumes ONLY inequalities; K* is the union of reach
regions — this is the PI's "N* given by inequalities". (d) delta_stop > 0 hands the ridge to the
global campaign; at s_0 = s-hat nothing global exists yet that can absorb it (gap G1 below).

## T1 Truncation lemma (draft; two proved forms + one measured constant)

T1-a (CONE TRUNCATION, the sharp one; proved at the linearization, interval extension is M3's
target). If e_s not in cone{grad g_k(z) : k in retained(z) union gained(z)} — certified by a Farkas
direction y over a region — then no FJ point with lambda_0 > 0 exists there; if additionally no
nonnegative self-stress exists on those rows (same y kills it), no FJ point at all: the stratum
contributes no interior minimum in the region (compose with D2 for the slack case as in T0.3). At
z-hat: the sparsest valid support has 32 of 38 rows, i.e. EVERY break-set with |B| >= 7 kills the
cone; the maximal surviving break-sets have |B| = 6. Hence, at the linearization,

   K = 6:  every stratum with |B| >= 7 is FJ-free near z-hat (and lambda_0 = 0 is empty there).

CAVEATS to discharge: (i) interval extension: the cone can reopen away from z-hat — M3 measures
the radius over which per-family Farkas directions verify; (ii) gained rows can re-feed the cone —
the menu of gained candidates within the working region must be included (at travel <= 0.05 the
only candidates are (6,7), (8,9), (3,4), (7,10) plus nothing else below gap 0.23); (iii) the count
C(38,7) ~ 1.3e7 of maximal dead families is enumerable but a grouped certificate (per min-support
cover) should collapse it — M3 measures the grouping.

M1 UPDATE (2026-08-27, results/m1_report.md — supersedes parts of T1 below). T1-a at the
linearization is far stronger than K = 6: the multiplier polytope has exactly 16 vertices, min
support 32; only 223 break-sets of 2^38 are cone-alive (all within the 10-row family
{1,2,8,9,10,21,22,23,26,29}; 28 of 38 rows are SINGLETON cone-killers); after the empty-stratum
test, exactly 81 break-sets survive all tests at z-hat, |B| in {2..6}, all decorations of the two
corner-release seeds {8,9} (sq2 off the bottom-right container corner) and {21,22} (sq5 off the
top-right). K = 6 is sharp (4 survivors at k=6, 0 at k=7). The lambda_0 = 0 branch is certified
empty at z-hat (rational Farkas witness, IV floor 0.2297). CAVEATS: retained-rows-only (gained
contacts can re-feed the cone — M3) and z-hat-only (no interval extension yet — M2/M3).
T1-b's graph form is refuted as useless (0% kills to k=6); its force-balance SIGN CASCADE
(single-coordinate stationarity sign rule, iterated) is the correct abstraction and is always
terminal when it fires (total multiplier collapse, lambda_0 = 0 included) — fold into T1 as the
proved global form once interval-extended.

T1-b (LOAD-PATH TRUNCATION; proved, cruder, fully global — SEE M1 UPDATE ABOVE: graph form
near-useless as measured; keep only the force-balance cascade). By L6 + L7, an FJ point with
lambda_0 > 0 needs a wall-to-wall loaded component on a binding axis; by force balance a square
whose only contacts are two orthogonal walls carries no load (its two wall normals are +x and +y:
each coordinate stationarity kills its own multiplier), so wall-node relays through corner squares
are load-dead. A stratum whose retained+gained edge set cuts every x-wall-to-wall loadable path
AND every y-path is FJ-free for lambda_0 > 0 REGARDLESS of position in the stratum (the argument
is purely combinatorial-static given the active set); the lambda_0 = 0 branch needs a nonnegative
self-stress among retained+gained rows — at z-hat none exists even on all 38. Min row-cuts at
z-hat: y-axis 3 rows ({22,23,25}), x-axis 5 rows; both-axes cut from 8 well-chosen rows. This
gives a PROVED weak truncation: every stratum with B containing one x-cut and one y-cut is dead;
ALL strata with |B| > 38 - 4 = 34 are dead unconditionally (any loadable path needs >= 4 rows,
refinable). The gap between T1-b (weak, global) and T1-a (K = 6, local) is the price of rigour;
M3 quantifies both.

T1-b' (COORDINATE SIGN COLLAPSE — the proved form of M1's force-balance cascade). Let R be a
region, K a row set (retained plus the gained menu on R), and A[k,c] the interval-certified
gradient coefficient of row k in coordinate c over R. RULE: if for some configuration coordinate
c != z[33] every row k in K with 0 not in A[k,c] has A[k,c] of one strict sign on R, then any FJ
multiplier vector (lambda_0, lambda) at any point of R with active set in K satisfies lambda_k = 0
for all such k (the c-stationarity row reads sum_k lambda_k A[k,c] = 0 with all nonzero terms of
one sign, since (grad s)_c = 0 for c != 33). CAVEAT (soundness condition): rows with 0 in A[k,c]
(interval straddles zero) must be treated as sign-unknown and BLOCK the rule for that coordinate.
Remove the killed rows from K and iterate. If the cascade empties K: the z[33]-stationarity row
gives lambda_0 = sum over far-wall rows of lambda = 0, so (lambda_0, lambda) = 0, contradicting
FJ normalisation — NO FJ point (lambda_0 = 0 branch included) exists in R with actives in K.
PROOF: as stated, each step is one stationarity row plus sign definiteness; iteration is finite. QED
This subsumes T1-b's corner-square rule and, per M1's measurement, when it fires at z-hat it is
always terminal (fires on 3.0%/10.2%/19.3%/31.4%/46.7% of strata at k=2..6, 94.5% at k=12).
Interval extension over R and gained-menu robustness are M3 tasks; M1 records the minimal firing
coefficient 0.0594, so generous sign margins are expected.

T1-c (SLACK TRUNCATION). Strata with all 18 pair rows broken: interior minima die by D2 alone
(T0.3 proof); only wall-contact structure remains and the (F) test is trivial there (grad s has a
strict Farkas direction when no pair row can be active: inflate the container; verified per
region). So |B| >= 18-relevant strata reduce to wall bookkeeping.

## Care points (brief's list, discharged)
- touching vs open: closed-cover T0.1(i).
- lambda_0 = 0: inside (F) and T1; at z-hat provably empty (no nonneg self-stress) — M1 certifies.
- new contacts: T0.1(ii) — free for value certificates, menu rows for FJ, cascade handoff in (C);
  candidate list is finite and short in any modest region (M1 bounds it honestly per travel cap).
- rank degeneracy inside strata: RANK-DROP branch of (F); value forms immune.
- flush contacts: 2 rows, breaking one = peeling rotation (a legitimate k=1 stratum; 4 of the 18
  k=1 mechanisms are single-row flush breaks of this kind — M1 classifies).

## Gap list (theory-side, this doc)
G1 ridge handoff: at s_0 = s-hat the collar (3) has no global partner certificate yet (LP ceiling
   3.83; case tree paused at 3.84). The composed theorem is a BASIN statement, not s(11) = s-hat.
G2 lambda*, K = 6, no-self-stress, cuts: float recon at z-hat; exact/interval promotion pending
   (M1/M2/M3).
G3 (C)-chaining assumes the cascade graph is finite/acyclic enough to terminate; M4 measures
   branching and route lengths (a cycling route would be a theory alarm).
G4 the (F) equality-tolerance test needs certified multiplier bounds Mu per segment; designed but
   not yet exercised.
G5 selection-menu completeness at flush ties along routes (dominance sign flips) — inherited from
   T3; the (C) segments must include tie selections at their faces.
