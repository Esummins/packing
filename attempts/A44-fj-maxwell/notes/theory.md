# A44 — FJ-Maxwell: definitions, proved lemmas, and the refutation frame (Fable lead, 2026-08-29)

Setting: docs/proofs/drain_lemma.md v3 (D1, D2, D3'), docs/proofs/structure_lemmas.md (Fact 0,
L1-L7, soundness ledger). Minimiser z-hat at side m0 <= s0; consistent selection S; FJ certificate
(lambda0, lambda) >= 0, lambda0 + Sum lambda = 1, rows g >= 0, stationarity
lambda0 * grad(s) = Sum_k lambda_k * grad(g_k).

## Conventions (the physical Maxwell count — Fact 0)

- SUPPORT graph H: edges with a strictly positive multiplier on at least one of their rows;
  loaded squares = squares incident to an H-edge (k_H of them).
- ACTIVE core = the contact-bearing squares (11 minus true rattlers, which carry no contacts);
  k = |active core|. This is the census object (A31/A43 structures are active graphs), and ALL
  counting statements below (m, E, F, chi, C*, C-rep) refer to the ACTIVE graph G on the active
  core. Support-level analogues are all REFUTED by the atlas evaluation (results/eval_report.md
  B2*), including at Trump itself (min FJ-support found: 30 rows < 34), and the loaded set can
  be far smaller than the active core (families 1/2: k_H = 6 of 11, m_H = 17 < 3 k_H + 1). The
  census can only ever price active graphs; H obeys no Maxwell count at all.
- Row counting (Fact 0): a pair contact is ONE edge; FLUSH carries 2 rows (two contact points),
  point contact (incl. corner-corner) 1 row. A (square, wall) contact is one edge; wall-flush
  (two corners on the wall) carries 2 rows. m = total rows on the core-induced G; E = edges;
  F = flush edges; m = E + F.
- Dimension: N = 3k + 1 (three coordinates per core square, plus the container side s).
- A = Jacobian of the m active rows in the N core coordinates at z-hat (far-wall rows x=s, y=s
  carry the ds-column entry +1). d = dim ker(A) (infinitesimal flex space of the core, s
  included as a variable). sig = dim ker(A^T) = m - rank(A) (self-stress space of the row set).

Tied axes at a corner-corner contact are alternative SELECTIONS of the same physical row slot,
not extra rows: each smooth selection NLP activates one of them. All statements below are per
selection; the counts m, E, F are selection-independent (Fact 0), which is what makes them usable
by a census.

## L8 (Maxwell index identity) — PROVED [linear algebra]

m = N + sig - d, i.e. chi := m - (3k+1) = sig - d.
Proof: rank(A) = m - sig = N - d by rank-nullity applied to A and A^T. QED.

## L9 (rigidity => Maxwell) — PROVED, CONDITIONAL ON d = 0

If the core at z-hat is first-order rigid (d = 0: no nonzero infinitesimal motion of core
coordinates and s preserving all active rows to first order), then m >= 3k + 1, with equality
iff the rows are independent (isostatic). Proof: L8 with sig >= 0. QED.
Note: needs no FJ, no criticality — it is a statement about any contact configuration.
Corollary (census form, with L4 planarity giving E <= 3(k+4) - 6): for a first-order-rigid
core, F >= 3k + 1 - E and 2E >= 3k + 1 — exactly the two N4 filter forms (A43 Part 1),
now proved CONDITIONAL on first-order rigidity of the realization.

## L9' (lambda0 = 0 branch) — PROVED, same conditionality structure

If the FJ certificate has lambda0 = 0, then A^T lambda = 0 with lambda >= 0, lambda != 0, so
sig >= 1 and m >= 3k + 2 - d; if moreover d = 0, m >= 3k + 2.
(The lambda0 = 0 branch is thus HARDER to realize with few rows than the lambda0 > 0 branch,
not easier; it needs a nonnegative self-stress on top of everything.)

## L10 (support flexes are s-neutral) — PROVED

If lambda0 > 0, then e_s lies in the row space of A_H (stationarity divided by lambda0), hence
every y in ker(A_H) satisfies e_s . y = 0: infinitesimal flexes of the support structure neither
grow nor shrink the container at first order. (Valley directions are s-flat; a flex is never a
descent direction. This is why flexible minimisers are legitimate and cannot be excluded on
first-order grounds.)

## L11 (non-thin local counts) — PROVED, CONDITIONAL ON THE NON-THIN BRANCH

In the non-thin branch (L2's codim >= 1 degree-2 configurations excluded), every loaded square
has either H-degree >= 3, or exactly two H-edges both flush; in all cases ROW-degree >= 3
(rows at the square, flush counting 2). Proof: L1 gives degree >= 2; L2 makes degree 2 with at
least one point contact thin (common-line-of-action condition, codim >= 1, both the two-point
and point+flush cases); degree 2 with two flush edges carries 4 rows. QED.
Consequences: (i) handshake 2*E_pp + E_pw >= 3k, so 2E >= 3k + E_pw; with lambda0 > 0, L6
gives E_pw >= 2 (a component loaded on BOTH binding walls), hence 2E >= 3k + 2: the N4-L0
census form (2E >= 3k+1) is a THEOREM on the non-thin lambda0 > 0 branch. (A43 already
measured that at L0 this adds nothing beyond non-thinness — the bite was always in the L1
flush form, which needs m >= 3k+1 itself and stays dead.) (ii) row-handshake gives only
m >= 3k/2 — the per-square local counts cannot reach 3k+1; the Maxwell count is genuinely a
global statement, which is why it fails (below).
Scope note: L11 is about LOADED squares. The eval's B5 ("every ACTIVE-core square has row
degree >= 3") is a different, refuted statement (genuine entries have unloaded active squares
of row-degree 1-2); no contradiction — its L1 canary B5' (loaded squares have >= 2 loaded
edges) passes on every entry.

## The refuted candidate (data: results/eval_report.md)

NAIVE MAXWELL (N4's premise): "every FJ-critical configuration has m >= 3k + 1."
Status: REFUTED. Primary witness: family 31 (solid VALLEY, cert h = 0.0599): k = 11, m = 33 =
3k < 34, FJ LP feasible at lambda0 = 1 with residual 6.9e-9, ALL 33 rows loadable, all 11
squares loaded (k_H = 11) — a fully-loaded genuine valley one row short of Maxwell. Secondary:
family 27 (VALLEY-MARGINAL, same counts; its lambda0 = 1 LP is infeasible at tolerance,
consistent with A37-G-A37-2's marginal status — the refutation does not rest on it). The structure-lemmas ledger's SOFT
marking is upgraded to a definite refutation: no theorem of the form m >= 3k+1 unconditional
over FJ-critical points is true in this geometry.
Also refuted long since (A37): isostaticity rank >= 3k+1 (valleys at rank 28-32).
Scope honesty: the atlas counterexamples live at values 3.885-3.94 > s0. The bound restricted
to "FJ-critical AND sigma <= s0" is not literally refuted by them — but no known proof route
distinguishes the value, and a census cannot lean on an accident of what happens to exist below
s0. It is dead as a theorem target.

## Why no unconditional bound below 3k+1 is forced by first/second-order necessity

Second-order FJ necessity at a minimiser: for every critical direction y there exist FJ
multipliers with y^T (Sum_k lambda_k grad2(g_k)) y <= 0 (Lagrangian L = lambda0 s - Sum lambda g,
grad2 L >= 0 on the critical cone; s is linear). Now take a hypothetical configuration with
INDEPENDENT rows (sig = 0) and d >= 1: the flexes are s-neutral (L10), the active set is locally
a smooth manifold W of dimension d (independence + implicit function theorem), s restricted to W
is critical; if s|W has a strict local minimum at z-hat (geometric stiffness
-Sum lambda_k y^T grad2(g_k) y > 0 on ker A — a curvature condition, no stress needed), z-hat is
an isolated genuine minimiser with m = 3k + 1 - d <= 3k. First- and second-order conditions are
all satisfiable; nothing in the FJ calculus forbids it. Hence any row bound below 3k+1 that
survives the atlas (see C* below) is a genuinely GEOMETRIC conjecture about squares — it cannot
be proved by the FJ + counting route, and we do not claim it.

## C* (the empirical frontier) — CONJECTURE, measured, NOT proved

C*: every FJ-critical configuration has m >= 3k on the active graph, equivalently
sig >= d - 1.
Status: SURVIVES the full atlas under both counting conventions (eval B1'/B4': tight at
families 27 and 31 at chi = -1; the shadow convention adds A37-NEW-2 tight; no genuine entry
below 3k). Also surviving, and stronger than expected: B3 (2E >= 3k+1, min margin +8 — beyond
what L11 proves), B6' (every genuine CP has >= 3 pair-flush edges; only F_pair >= 1 was asked). Equivalent form by L8: the flex space never exceeds the stress space by more than one.
We record it as a conjecture with the atlas as evidence; the previous paragraph shows the
obvious proof routes are closed (a sig = 0, d >= 2 curvature-blocked valley would violate it and
is not excluded by first/second-order necessity).

## C-rep (max-contact representative form) — CONJECTURE, not refuted by the atlas

For the exclusion program one may restrict attention to one representative per connected
component V of the minimiser set; choosing z* in V with inclusion-MAXIMAL active set is sound
(finitely many active sets; census completeness then only needs the representative's structure).
C-rep: every component of the minimiser set contains a point with m >= 3k + 1.
The atlas does NOT refute this: each valley entry is a single drain endpoint somewhere on a flat
bottom; its component may contain higher-contact points. Two loopholes block a proof:
(i) loop flexes — a flat valley closed into a loop never creates a new contact;
(ii) curvature-blocked flexes — d >= 1 with s|W strictly minimal (previous section): the
component is the single point, m < 3k + 1 stands.
Named gap A44-G1. If C-rep were proved, N4 at 3k+1 would return in full for a census of
max-contact representatives.

## What the census may soundly use (the deliverable split)

Per enumerated structure (graph + flush decoration), m = E + F is known at the graph level.
1. EXACT, from L9 by contraposition: a structure with m < 3k + 1 has rank <= m < N at every
   realization — it can NEVER be first-order rigid; any critical realization carries
   d >= 3k + 1 - m independent flexes. So the census splits EXACTLY into
   RIGID-POSSIBLE (m >= 3k+1) and FLEX-ONLY (m < 3k+1) branches. N4's kill set is precisely the
   FLEX-ONLY branch — and the atlas proves that branch is inhabited by genuine critical points.
   N4 is therefore NOT a sound filter; the sound object is the two-branch decomposition with the
   FLEX-ONLY branch counted, labeled, and carried.
2. CONDITIONAL on C* (labeled): kill m < 3k (chi <= -2). Atlas-consistent, unproven.
3. CONDITIONAL on C-rep (labeled): kill m < 3k+1, valid only for a census of max-contact
   representatives. Unproven (A44-G1).
4. lambda0 = 0 branch (L9'): within the FLEX-ONLY branch, the lambda0 = 0 sub-branch needs
   sig >= 1, i.e. m >= N - d + 1 at the realization; at graph level this kills nothing beyond
   (1) but is recorded for the per-structure algebraic stage.
Census re-run measures: sizes of the two branches at k = 3..7 + extrapolation, and the
conditional columns (2) and (3), against A43's R11 baseline.
