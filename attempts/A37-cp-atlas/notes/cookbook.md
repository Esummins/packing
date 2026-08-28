# A37 cookbook — per-CP audit + universal value certificate (Fable, lead; 2026-08-27)

Target: for each A04 family < 3.95 (31 besides Trump; attempts/A04-upper-search/
families_catalogue.json, field best_x = 34 floats c_i, theta_i, s), emit a corruption-gated,
stratum-blind value certificate "sigma >= V on box(z0, h)" for the far-field atlas. Machinery =
A35/A36 verbatim where possible: max-form pinning + iterated dichotomy (A36 a36_lib/a36_check
chain), aux dist rows, L1 over-estimate principle. Trump (family 0) is done (A22 + A36).

## Step 1 — AUDIT (the A35 lessons, mandatory before anything)
At the float point z0: compute ALL 55 pair SAT gaps and 176 corner-wall clearances (interval,
dps 60). Contact = |gap| <= tol_c (use 1e-7, report the gap spectrum so the tol choice is
auditable; A04 points are ~1e-9-1e-12 converged). For each contact classify: point (corner-edge,
interior tangential coordinate, margin), FLUSH (two contact corners; margin per corner), ENDPOINT
tie (tangential coordinate within tol of +-1/2), CORNER-CORNER (both squares' corners coincide).
Record per contact the chosen sep-row selection(s) (t3lib language) + tangential margins. Rules:
  - flush upright-upright pairs: rows may be taken per A36 (any corner row of a separating axis);
    ALWAYS add the aux dist row d^2 - 1 >= 0 for centre-distance-1 flush pairs (valid globally by
    incircles) — it is the cheap insurance that killed A35's phantom queue;
  - corner-corner and endpoint ties: do NOT trust one selection; either use the A36 branch
    disjunction (variants) or drop that row from omega support entirely (a row with omega = 0
    needs no validity) — dropping is FINE if the multiplier LP still reaches e_s;
  - NEVER use a dist row as a stratification/pin row (surrogate lesson); aux only.

## Step 2 — CLASSIFY (rank at z0, float SVD + [RFP] where rigid)
Build the row set from the audit (walls + selected pair rows; flush = 2 rows). A = Jacobian at z0
over the 34 vars. Classes:
  RIGID: rank 34 ([RFP]-certify a 34x34 minor). -> Step 3R.
  RATTLER-CORE: some squares contact-free or under-contacted; removing them leaves a rank-3k core
    on the loaded coordinates ([RFP] on the core minor). Rattler coords appear in no loaded row.
    -> Step 3R on the core (R1: certificate is rattler-blind; box constrains core coords only;
    "equality iff" dropped).
  VALLEY: loaded rank < full (mechanism directions in the loaded core). -> Step 3S (soft).
Report class + rank + spectral gap in the atlas.

## Step 3R — RIGID/CORE recipe (exact CP + hard certificate)
 (a) Krawczyk-rationalize: choose a square subsystem (rank-34 or core-rank) of contact rows,
     Newton-refine z0 at mpmath dps 60, rationalize (den 1e45), Krawczyk-certify existence +
     uniqueness in box(z_hat, r_N' = 1/2000) [IV]; certified value enclosure [v_lo, v_hi] from
     the s-coordinate enclosure (width target <= 1e-40).
 (b) Multiplier: LP e_s = A^T omega, omega >= 0 on audited valid rows (+ aux); if infeasible at
     the float point -> the point is NOT a local min of s (flag loudly, class = NOT-CP, emit soft
     cert only). Rationalize omega, residual [IV].
 (c) Universal certificate at max-form pinning, A36 chain verbatim: E(x) = eps0 + eps_w x +
     Hbar x^2; case 1 G_omega >= E(h) -> s >= v_lo; case 2 max-form pin psi(h) =
     (kappa_eff E(h) + kappa g_max)/(1-beta) iterated to x*; FINISH (replaces A22's role): any
     feasible z with ||z - z_hat|| <= x* has s(z) >= v_lo - x* (the s-coordinate is one of the
     pinned coordinates; bound |s(z) - s(z_hat)| <= x* directly). Since x* ~ 1e-50, quote
     V = v_lo - 1e-40 (round down). Bisect h to the largest certified radius; also emit at the
     0.96-slack radius. Row validity on box(h): tangential margins > 0 for all omega-loaded rows
     ([IV], per A36 [V]-check); endpoint rows only via branches or omega = 0.
 (d) NOTE: no per-CP analog of A22's local-optimality theorem is needed — the value discharge
     needs no equality clause and no uniqueness beyond the pin.

## Step 3S — SOFT recipe (valleys / anything Step 3R rejects)
No exact CP needed. At float z0 (interval-boxed): omega >= 0 rational on audited valid rows with
r_res = ||A^T omega - e_s||_1 small (LP; if infeasible, flag NOT-CP and skip with reason — such a
family is not a drain and the far field must handle it by other means; report it).
  V_soft(h) = s(z0) - sum omega_r g_r(z0) - r_res sqrt(34) h - Hbar(h) h^2   (all [IV])
Certificate: every feasible z in box(z0, h) has sigma >= V_soft(h). Choose h maximizing
usefulness: report V_soft at h in {5e-4, 1e-3, 2e-3} and pick the largest h with V_soft >
s_min(family) - 5e-3 (still a nontrivial discharge); always also record V_soft at h = 1e-3.
Sound with zero rank assumptions (Taylor + G >= 0 only).

## Step 4 — RE-CHECK + gates
Standalone re-checker (a36_check.py pattern; no producer libs; rebuilds rows from the audited
contact table stored IN the certificate). Gates per CP: omega-sign, h-big, drop-aux (where aux
loaded), value-inflate (raise claimed V by 1e-3 — must FAIL). All gates must fail.

## Step 5 — ATLAS entry (results/atlas.json, one record per family)
{family_id, s_min_float, class (RIGID/RATTLER-CORE/VALLEY/NOT-CP), n_contacts (pairs/walls/rows),
 audit_surprises [list: corner-corner, endpoint ties, contacts absent from catalogue counts,...],
 z_center (rational or float+box), value: {v_lo, v_hi} or V_soft(h) table, h_certified,
 cert_path, checks_passed, gates_failed, notes}.
Dedupe: before working a family, canonicalize (sort squares, D4 orbit) and check against already-
done centers at tolerance 1e-6; record merges.

## Division of labor
Pilot agent: families 1, 6, 4 (rigid-looking, biggest-count rigid, suspected valley) — validates
the cookbook end to end. Production agents (after lead verifies pilot): remaining 28 split by
index parity. Lead: verifies samples, handles audit surprises exceeding the recipe, composes.
Budget: <= 1 desktop-day total, <= 6 processes. A29 untouched.

---

## AMENDMENTS (lead, 2026-08-27, after the pilot — all 8 APPROVED; production agents follow
## the pilot's a37_pipeline.py implementation of these, not the original text above)

A1. [V]-RULE AS DEFINITION (pilot 4.1): a sep row is valid on box(h) iff over the box the
    corner's owner-frame coordinates satisfy sup|t| < 1/2 and inf d > -1/2 (a corner strictly
    inside the open owner square violates disjointness). Branch machinery only for pairs with
    NO [V]-safe row.
A2. V_soft gradient term = r_res * h (l1/linf pairing), not r_res*sqrt(34)*h.
A3. V flooring in EXACT rationals: V = Fraction(v_lo) - Fraction(1,10**40). Never float*1e30.
A4. Radius selection: bisect h to maximize subject to V(h) >= 3.877084 (the incumbent);
    record the fixed {5e-4,1e-3,2e-3} table too. The trivial coordinate bound sigma >= s(z)-h
    is the baseline every certificate must beat.
A5. Tolerance LADDER {1e-7,1e-6,1e-5,1e-4} scored by GN consistency + KKT-LP feasibility;
    smallest passing rung wins; whole ladder recorded. Err loose (extra valid rows only cost
    through W0).
A6. CLASSIFY ONLY AFTER GN REFINEMENT (QR-pivoted maximal independent subset, minimum-norm
    steps); rank claims at raw A04 points are worthless.
A7. NOT-CP is a first-class outcome (fixed-angle optima: e_s infeasible unless theta-rows
    dropped): emit the omega = 0 trivial-bound certificate, tag class NOT-CP in the atlas.
    Variant cap 256; refuse and report beyond.
A8. best_x layout: centres interleaved x[2i],x[2i+1]; thetas blocked x[22+i]; s = x[33]
    (pack11.py unpack). Convert to A22 order at load.

LEAD CORRECTION to the pilot's Trump audit note: the "three corner-corner pairs" are, in A22
labels, the flush pairs (0,1),(0,3) (whose edge-endpoint corners coincide — inevitable for
flush aligned squares) plus (1,3). No contact is missing from the A36 v3 basis. Audit
classifiers must record BOTH labels (family-local ordering AND a canonical geometric signature)
to avoid this ambiguity; production agents: store the contact table with square coordinates,
not just indices.
