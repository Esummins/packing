# A38 / T0 — the composed soundness statement for s(11) = s-hat (Fable, 2026-08-27)

Care level: docs/results.md theorem style. This is the one-page statement the whole endgame
must instantiate; the A38 pilot MEASURES its cost, it does not discharge it. Every seam that a
full campaign must still prove is named at the end (S1–S8).

## Notation

s-hat = the algebraic Trump value 3.87708359002281… (A22/A36's exact object); s0 = 969271/250000
= 3.877084 > s-hat (rational). D0 = normalized feasible 11-square configurations (drain_lemma v3
setting); sigma = minimal-enclosing-square side; G = D4 x S11. mu = the sealed guard field at s0
(attempts/A33-tight-variety/t1/certs/A33_measure_feasible_3.877084.json): certified (F1) coverage
>= 1 for every closed unit square in [0,s0]^2, exact total 44630467/3906250 = 11 + eta,
eta = eta_cert = 0.4254 exactly. Atlas = attempts/A37-cp-atlas/results/atlas_final.json, 36
entries, each certifying sigma(z) >= V_e >= 3.877084 on box(z_e, h_e) — except entry 0 (Trump),
whose box carries the stronger A36 statement: sigma >= s-hat on ||z − z-hat||_inf <= 3.7e-3 with
equality iff z = z-hat.

## Theorem schema (what a completed far-field campaign proves)

Suppose a finite rooted tree of cells is produced with the properties below. Then
s(11) >= s-hat; combined with Trump's packing (s(11) <= s-hat) and A36's equality clause,
s(11) = s-hat, attained (mod G) only by z-hat.

1. **D1 (attainment; PROVED, drain_lemma v3).** m := s(11) is attained by some minimiser
   z* in D0. Since Trump's packing exists, m <= s-hat < s0; normalize z* corner-anchored, so z*
   is an 11-packing in [0, m]^2 subset [0, s0]^2.

2. **Root (occupancy at s0; case-LP certificate).** A certified occupancy lemma: every 11-packing
   in [0,s0]^2 has a square with centre in the zone Z (D4-invariant). By the machine-checked D4
   reduction (A27's verify_tree2 semantics re-run at s0), WLOG the witness placement lies in the
   fundamental triangle T x [0,90]deg. The tree's level-1 cells C_1..C_N are a closed cover of
   T x [0,90] (cover checked in exact rationals).

3. **Per-cell disjunction.** Every leaf cell C (a hypothesis H: witness cores B_1..B_k, NO-families,
   inherited from the branching) is discharged by AT LEAST ONE of:

   (K1) **case-LP kill, W1/W2-augmented (W5+W1+W2).** An a-posteriori-verified feasible measure
   mu_C with exact total < budget(H) = 11 − k, covering (mu_C(Q) >= 1) every admissible placement
   Q except those provably (i) meeting a core, (ii) inside a NO-family, (iii) **W1-exempt**: field
   coverage lower bound m_low(Q-box, outward-rounded, inflated by eps_lambda = 1e-6) > 1 + eta,
   or (iv) **W2-exempt (conditional)**: m_low(Q-box, same rounding) > 1 + eta − SUM_j max(0, c_j − 1),
   where c_j <= min coverage over core B_j (same certified machinery, INWARD-safe direction:
   c_j is a lower bound so the threshold is only ever raised soundly).
   Justification of (iii)/(iv): Lemma A33.1(i)/Corollary A33.2 applied to mu with the subfamily
   I = {witness cores' squares} ∪ {Q's square}: for any 11-packing at side sigma <= s-hat, the
   lambda-scaled placements (lambda = s0/sigma in (1, 1 + 1.3e-8]) satisfy
   sum_{i in I} mu(S_i) <= |I| + eta; the 1e-6 inflation absorbs the lambda displacement
   (<= (lambda−1)·sqrt2·s0 < 1e-7). Conclusion of K1: **no 11-packing with sigma <= s-hat
   satisfies H** — in particular no minimiser lies in C. (Note: K1 does NOT exclude packings with
   sigma in (s-hat, s0]; the composition never needs that.)

   (K2) **atlas discharge (W3).** Every configuration consistent with H lies (mod G) in box(z_e, h_e)
   for some atlas entry e — this requires H to pin ALL 11 squares (a complete-core hypothesis),
   checked in exact rationals against h_e. Then sigma >= V_e >= 3.877084 > s-hat on C, except
   e = Trump where sigma >= s-hat with equality iff z-hat. So C contains no minimiser other than
   (possibly) z-hat itself.

   (K3) **Fritz-John / Farkas exclusion (W4; drain_lemma v3 T3(c1), t3lib).** C is a full-configuration
   cell (all 44 coordinates boxed) and one interval-verified direction y has grad s · y < 0 and
   grad g · y > 0 for every row possibly active on C: then no FJ point of any consistent selection
   lies in C (lambda0 = 0 branch included, Gordan-complete), hence no minimiser in C.

   (K4) **D2 slack (drain_lemma v3).** Certified uniform pairwise SAT-gap >= delta > 0 on C:
   no minimiser in C.

4. **BDBFS discovery loop (soundness of the atlas's openness).** The atlas is NOT assumed complete.
   Whenever a cell resists K1–K4, the loop runs a compression-flow probe from it: either it finds
   an 11-packing with sigma < s-hat (the conjecture is FALSE and the witness is the disproof), or
   it converges to a critical point, which is audited and certified by the A37 pipeline and ADDED
   to the atlas, after which K2 is retried. Adding certified boxes never weakens the composition;
   the loop's termination is empirical (S3), its soundness is not in question.

5. **Conclusion.** z* lies in some leaf cell (root + cover + D4 reduction). K1/K3/K4 cells cannot
   contain z*; K2 cells force z* = z-hat (mod G) or sigma(z*) >= V > s-hat. Since some leaf must
   contain z*, z* = z-hat (mod G) and m = s-hat. QED (schema).

## Named seams — what is NOT yet proved (the pilot measures; a campaign must prove)

- **S1 (G1 ridge/cliff handoff — the deep seam).** K2/K3 need FULL-configuration cells; the
  interior-first tree branches on ONE witness square (k = 1..3 cores at pilot depths). The missing
  step is the localization cascade: occupancy-conditioning square-by-square until all 11 are cored
  at atlas-box scale (h_Trump = 3.7e-3), i.e. depth ~5 per square in the witness coordinates PLUS
  a measured per-square branching factor for squares 2..11. The pilot's seam probe measures b_2
  (and the stall risk) — nothing here proves the cascade terminates.
- **S2 (lambda bookkeeping).** The 1e-6 inflation + outward rounding of every W1/W2 exemption and
  every c_j must be enforced in the exact verifier (an extended verify_tree2 obligation, not yet
  written; the pilot's sampled certificates implement it ad hoc).
- **S3 (attractor completeness).** BDBFS termination = the global wall (A31/A32), untouched. The
  loop makes the composition sound, not finite.
- **S4 (verifier for W2 budgets).** c_j lower bounds enter the kill threshold; the a-posteriori
  checker must recompute them independently (same field certificate, inward direction).
- **S5 (root + D4 at s0).** A24's root lemma and the machine-checked reduction exist at 3.84 only;
  both must be re-proved at s0 (the pilot does the root; the D4 transfer re-check is mechanical).
- **S6 (equality clause containment).** Near-Trump survivors must end INSIDE A36's box in ALL
  coordinates (mod G) before K2-Trump fires — same cascade as S1.
- **S7 (eta headroom).** All soundness uses eta_cert = 0.4254. The float bracket says the true
  eta(s0) is ~0.24; A33's G5 gap (one tangency cluster) is the route to eta_cert ~ 0.26-0.30.
  Every W1/W2 bite measured at eta_float in the pilot is [NUM] — labelled, never composed.
- **S8 (attainment vs. openness at the boundary).** K1 kills packings with sigma <= s-hat; the
  minimiser satisfies this by D1. No statement is made about sigma in (s-hat, s0] — deliberate.

## The pilot's contract

A38 instantiates: root at s0, levels 1–3 of the witness tree with K1's full weapon stack, K2/K3
as census + seam probes (they cannot fire at pilot depths — recorded honestly as structural
zeros in the kill matrix, not failures), and measures every constant the schema's cost depends
on: per-depth per-weapon kill fractions, effective branching 8·(1 − f), survivor character
(Trump-consistent vs other, distance to atlas), stall incidence (tau pinned >= budget with
maxcov exhausted and no weapon firing), the seam branching b_2, and node costs. GO iff the
extrapolated bracket lands at desktop scale with no structural stall; the assassin, if NO, is
whichever constant binds.
