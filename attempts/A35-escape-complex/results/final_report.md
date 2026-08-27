# A35 — escape-complex inflation: final report (Fable, lead; 2026-08-27)

Idea I-L15 (PI): replace A30's metric shells around Trump's jam with SEMANTIC strata — "these
contacts break, the rest hold" — each killed by one dual certificate. Pilot = theory (T0, T1) +
four measurements (M1–M4, Opus subagents, all verified by the lead) + two correction rounds
(M1b/M2b/M3b) forced by defects the pilot itself exposed. Everything below is on the PI's desktop,
single process.

## Plain-language summary

The idea works, and better than proposed — but not for the reason we expected, and only out to a
definite horizon.

1. Trump's jam has NO escape routes at all near the jam: every way of breaking contacts is either
   geometrically empty, or load-refuted (the remaining contacts cannot support the container
   pressure), or wedged (the motion that opens one gap closes another at a healthy rate ~0.58).
   The "cascade of escape routes" the brief planned to follow does not exist: measured branching
   factor 0.18, tree depth 0 under the theory's stopping rule, zero descending directions in
   ~4,700 followed segments. The mountain-pass picture is exact: everything is uphill, and we can
   now certify it wholesale rather than cell-by-cell.
2. The pilot caught the repo's first real modeling bug: A22's 38-row contact list is missing a
   14th contact — squares 1 and 3 touch corner-to-corner at (1,1), exactly (verified in exact
   rational arithmetic). A22's optimality certificate itself is unharmed (it proved optimality
   over a superset), but every enumeration-level statement had to be redone on a repaired 42-row
   basis, which cost one full delta round and taught us the method's two real failure modes
   (incomplete menus, surrogate rows).
3. On the repaired basis the whole 2^42 break-set lattice is covered by 64 universal certificates
   (~10 minutes of compute, independently re-checked, 4,608 checks pass): no configuration near
   the jam beats it, no matter which contacts break. A30 priced this same neighbourhood at
   1e5–5e7 CPU-hours. That assassin is dead.
4. The honest limits: (a) the current universal certificate reaches only ~0.25× A22's radius (a
   normalization artifact — lever L2 below); (b) one geometric lemma about the repaired rows
   remains undischarged (lever L1) — until it is written, the v2 theorem is conditional; (c) the
   method's reach has a hard SEMANTIC CLIFF at travel R* ≈ (smallest non-contact gap)/(Lipschitz
   constant) = 0.0249/4.243 ≈ 0.006: beyond it, new contacts can form, the break-set language
   explodes (82% of sampled break sets escape the truncation at R = 0.01), and per-stratum
   certification stops scaling. The basin can be certified up to the cliff; the ridge and the far
   field belong to other machinery.

## Theory delivered (notes/theory.md)

- T0.1 stratification: closed-cover strata indexed by broken-contact subsets; touching-vs-open
  discharged by closed covers; gained contacts harmless to value certificates, menu rows for FJ.
- T0.2 certificate forms, each sound and machine-verified at least once: (E) empty-stratum
  Krawczyk isolation; (V) one-shot dual value bound; (A) ascent identity — every escape is uphill
  at rate ≥ λ_floor per unit of total gap opening (λ_floor = 0.047644 on v1; restated on v2's 40
  load-bearing rows; restored to 0.0205 on ALL rows once the two aux dist rows join) — plus the
  Layer-1 inflation lemma (honestly reported: its certified radius 2e-4 < r_N, subsumed by A22);
  (W′) menu-complete wedge: per-selection escape cones with tied dominance rows AND auxiliary
  valid inequalities (the v1 dist rows d² ≥ 1, valid by incircles, active at ẑ) — the decisive
  repair; (C) validated continuation (spec'd; never needed — no routes exist); (F) Motzkin FJ
  exclusion with the rank-drop branch.
- T0.3 composition theorem (min-attainment on an assembled, inequality-defined N*) + the
  λ₀ = 0 region lemma: the same Farkas direction kills both FJ branches (e_s·y < 0 unused).
- T1 truncation, three proved forms: T1-a cone truncation with UPWARD CLOSURE — the minimal dead
  sets generate all cone-dead sets, so the whole lattice needs only #(minimal dead) region
  certificates (v1: 34; v2: 37, including 4 triples whose existence is itself a lesson — see
  bugs); T1-b′ coordinate sign collapse (proved sound form of M1's force-balance cascade; the
  graph-cut form of L6 measured near-useless, 0% kills to k = 6); T1-c slack/D2 (measured
  irrelevant at high k once gained contacts are allowed — 0 kills in the escaping class).

## Measurements (all independently verified by the lead — notes/verification_log.md)

M1 (enumeration, v1): rank 34, self-stress dim 4, no nonnegative self-stress (λ₀ = 0 empty at ẑ,
IV Farkas floor 0.2297); λ* floor 0.047644 exact (residual 9.7e-45); K = 6 sharp; only 224 of 2^38
break sets cone-alive, ALL within a 10-row family; after all tests 81 survivors = decorations of
two corner-release seeds. 18 s runtime.

M2 (certificates, v1): all 81 survivors WEDGED — escape cone {0}, no continuation routes exist;
81 rigorous Motzkin (W) certificates pin each stratum to ẑ on box(h_W = 69/32000 ≈ 4.3×r_N),
x* ≤ 8e-58; 143 empty strata certified to h ≈ 0.005–0.0085 (capped by selection validity
h_valid = 0.00522); re-checker + corruption gates pass. ~100 s for the 81.

M3 (region truncation + gained menu, v1): region T1-a closed on box(h_W): 34 minimal-dead-set
Farkas certificates, upward closure covers all 2^38−224 cone-dead sets, both FJ branches; gained
menu certified EMPTY at h_W (two independent proofs). Protocol finding: point-optimized directions
fail — the interval-robust LP over the box is the working form. THE CLIFF measured: at R = 0.005
the truncation is exact; at R ≥ 0.01 an "escaping class" (~82% of sampled sets, reaching k = 12)
is covered only by matched-menu per-set certificates (0 failures on 88, but per-set).

M4 (cascade, float): independent wedge confirmation (min wedge strength 0.577); zero σ dips
anywhere (the mountain-pass claim, empirically green); cascade depth 0 / branching 0.18; all
first-contact events within M1's predicted candidate list; 7 rank-34 re-jams found, all σ > ŝ,
all refuted by the full-menu cone test (the bidirectional protocol's refute branch works).
FOUND THE BASIS DEFECTS: the missing (1,3) contact and the dist-row surrogates.

M1b/M2b/M3b (repaired basis v2 = 42 rows): rank 34, self-stress dim 8, still NO nonnegative
self-stress (IV floor 0.2213). First-order kill-tests initially explode (K 6→13, cone-alive
70,499, wedge-surviving queue 25,050, two first-order-FLAT seeds) — all of it an artifact of
dropping the two dist rows, which are valid active inequalities: restoring them as auxiliary rows
((W′)-(i)) kills both seeds at first order (lead predicted and verified the rate −0.8165; M2b
certified 160 IV Motzkin duals over every selection menu) and restores a uniform multiplier floor
0.0205 over ALL rows, giving the (V′) UNIVERSAL certificate: 64 certificates (meaningful
variants) cover the entire 2^42 lattice at once — true survivors: 0, queue never walked (553 s vs
an estimated 12.8 CPU-days per-stratum with 17% uncovered). M3b closed region T1-a on v2 (37/37
certificates at h_W — catching en route that M1b's minimal-dead list missed 4 triples, which
would have left 20,700 sets uncertified; patched at source). 288 v2 certificates, 4,608 checks,
all pass; corruption gates (including drop-aux) fail as required.

## The composed theorem (current status, stated honestly)

- v1 statement (WITHDRAWN as an FJ argument): σ ≥ ŝ on box(ẑ, 4.3×r_N) via 143+81+34
  certificates — unsound as stated because the v1 menus omitted the active (1,3) contact rows
  (9 of 34 kills provably revived). Kept as: sound value-layer components + the method rehearsal.
- v2 statement (CONDITIONAL, one lemma outstanding): σ ≥ ŝ with equality iff ẑ on
  box(ẑ, h_G = 1.27e-4 ≈ 0.25×r_N), for ALL break sets at once, both FJ branches, gained menu
  provably empty, via 64 (V′) certificates + A22's theorem finishing the near-jam tube. The
  outstanding lemma (L1 below) is that the six repaired rows are a valid description of their
  contacts on the box (their contact corners sit at edge ENDPOINTS: dominance margin exactly 0 at
  ẑ, negative on any box — the barrier needs the weaker "owner edge separates the pair", true
  geometrically but not yet discharged). A22's own 34 rows carry certified margins ≥ 0.0148.
- Net: the v2 escape-complex theorem is presently SUBSUMED IN REACH by A22's box (0.25×r_N vs
  r_N) while being vastly superior in structure (FJ-complete, stratification-blind, minutes of
  compute, fully re-checkable). The per-stratum (W′) layer already reaches 1.6–3.1×r_N where it
  applies, so the reach deficit is a normalization artifact, not geometry.

## Two levers to beat A22's reach (next iteration, both bounded)

L1 ENDPOINT-ROW LEMMA: a box-valid form of the six repaired rows (owner-edge-separates statement
   for near-upright flush/corner contacts). Small geometric lemma + IV check; unblocks
   unconditional v2 and probably most of the reach.
L2 ω-SCALE: (V′)'s reach is bound by α_min/‖ω‖ (A_extᵀω = e_s fixes the scale, α_min ≈ 0.02);
   the (W′) self-stress normalizes freely (α_min = 1) and reaches 1.6–3.1×r_N. A hybrid
   (universal barrier + free-normalized wedge on the cone-alive family) should recover ≥ r_N and
   plausibly the v1-style 4×r_N.

## Cost accounting (desktop-days; PI's machine, single process)

| object | cost |
|---|---|
| A30 baseline: exclude the same neighbourhood at s₀ = ŝ (metric shell c^33) | 1.1e5–4.9e7 CPU-h ≈ 4.6e3–2e6 desktop-days (FLOOR, Trump's shell only) |
| A35 v2 composed local theorem (all certs + re-checks, incl. both delta rounds) | ~1 desktop-HOUR total; the load-bearing certificates alone ~15 min |
| A35 steady-state re-run (one critical point, repaired pipeline, no deltas) | ~10–30 desktop-minutes |
| per-stratum alternative (rejected) | 12.8 CPU-days, 17% uncovered |
| all 36 A04 local optima at ~30 min each (if bases curated) | ~1 desktop-day |
| Trump's FULL basin boundary at s₀ = ŝ (the brief's literal ask) | NOT PURCHASABLE by this method beyond the cliff — see NO-GO |

## GO / NO-GO

GO — adopt escape-complex certification as the standard critical-point-neighbourhood tool. It
replaces A30's per-CP shell (the c^33 = 8e8-cell assassin) with ~10²-certificate, minutes-scale,
exactly re-checkable coverage of the full break-set lattice, and the mountain-pass structure it
certifies (everything uphill, no routes, both FJ branches) is strictly stronger than A22's value
statement. Fund one more iteration for levers L1+L2.

NO-GO — as a route to certifying Trump's FULL basin boundary at s₀ = ŝ, and a fortiori as a
standalone endgame. Assassin constants, named:
1. THE SEMANTIC CLIFF R* = (min non-contact gap)/L_pair = 0.024875/4.2426 ≈ 0.00586. Below it the
   jam's contact language is exact (menu empty, truncation K = 6/13 sharp, 224/70,499 alive sets,
   minutes of certificates). Above it the language dissolves: gained rows revive 82% of sampled
   break sets by R = 0.01, K is gone by 13+, and only per-set matched-menu certificates survive —
   the certified basin cannot outgrow ~R* per expansion point. M4 measures the ridge
   (σ ≥ ŝ+1e-3) at travel ≈ 0.005 — AT the cliff, not inside it: the basin boundary is exactly
   where the method's language expires. Growing further means re-centering at new expansion
   points with their own contact sets — cost per center is minutes, but the number of centers
   needed to tile the transverse directions is unbounded a priori (the A30 dimensionality problem
   reappears wherever no contact structure pins the configuration).
2. THE GLOBAL WALL (unchanged): even with every critical point's neighbourhood certified free,
   the campaign still needs either all critical points enumerated (A31/A32: ~1e30 structures,
   measured dead) or the non-critical ocean covered (LP ceiling 3.83, case tree paused at 3.84).
   A35 does not touch this constant; it only removes the per-CP factor.

## Bugs and lessons (for the lab's method book)

1. A22's basis missed an exact corner-corner contact ((1,3)) and modeled two flush contacts by
   centre-distance surrogates. Lesson: certificate bases must be re-derived GEOMETRICALLY (all
   pair gaps + all corner-wall clearances at tolerance) before any enumeration builds on them;
   value certificates survive missing rows, FJ/menu arguments do not.
2. Surrogate rows are two-faced: wrong as stratification coordinates (40% of M4 routes died on
   them spuriously), load-bearing as auxiliary valid inequalities (dropping them created two
   fake first-order-flat escapes and a 25,050-element phantom queue; restoring them collapsed it
   to zero). Rule: valid active inequalities join every cone/wedge test, never the stratification.
3. Minimal-dead-set searches must run past size 2 on any multi-row-contact basis (M3b's 4
   triples; 20,700 sets would have been silently uncovered). Patched at source.
4. Point-optimized Farkas directions do not survive box growth (8/28 certify at zero radius);
   robust interval LPs over the box are the working protocol.
5. M2b's re-checker caught a soundness bug pre-publication (positive ω on dominance rows —
   selection conditions, not valid inequalities). Independent re-checkers with corruption gates
   remain non-negotiable.

## Gap list (composed; carried into the registry)

G1 ridge handoff (inherited from theory): nothing at s₀ = ŝ absorbs the collar; the composed
   theorem is a neighbourhood statement, not a basin-boundary one.
G2 L1 endpoint-row lemma undischarged — v2 theorem conditional until written.
G3 (V′) reach 0.25×r_N (ω-scale, lever L2).
G4 the {35} region certificate is thin (735-leaf cover, worst margin 2.08e-7); wants a sharper
   enclosure; its single-y radius (0.00164) is what caps any future h_W push.
G5 tie-alternative gradients at the six repaired rows should be added to the 37 region
   certificates' row sets (cheap re-run; same protocol) for full menu completeness.
G6 counting layers ([NUM] float LPs) are cross-checked but not certified; every kill that carries
   weight is [IV], the tallies are not.
G7 wedge/dof verdicts are [NUM] (rank-deficiency is not interval-certifiable at a rational
   point); nothing load-bearing rests on them (Motzkin duals are [IV] + rank-34 [RFP]).
G8 M4's 7 re-jam refutations are float-level; if any is ever needed as a theorem, redo per A22.
G9 basis curation for other critical points (A04's 36) not attempted; each needs its own
   geometric contact audit (lesson 1) before the pipeline applies.

## Files

theory: notes/theory.md; verification: notes/verification_log.md. Measurements: results/m1_*,
m2_*, m3_*, m4_*, m1b_*, m2b_*, m3b_* (+ code/ per-task, re-checkers m2_check_route.py,
m2_check_inflation.py, m2b_check.py; certificate stores results/m2_certs/ 224, results/m2b_certs/
288, results/m3_certs.json, results/m3b_certs.json). Registry row: attempts/REGISTRY.md A35.
