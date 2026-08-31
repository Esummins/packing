# A52 formulation note — the sound two-capacity-family node LP

Status: theory settled BEFORE compute (this note is the pre-registration). Author: Fable lead.

## 1. Setting and notation

Fix a node (hyp = cores + nofams, budget B). Admissible placements Q range over all closed unit
squares in [0,s0]^2 not exempt under hyp (caselp semantics, eps-margined). The node LP (A13/A27
covering form):

    tau := min mu(total)  over atomic measures mu >= 0
           s.t. mu(Q) >= 1 for every admissible placement Q.

Kill rule (A27, verbatim): a FEASIBLE mu with mu(total) < B kills the node (B disjoint squares
each of mu-mass >= 1 would need total >= B). Dual: fractional packings z >= 0 on placements with
point capacities sum_{Q ni p} z_Q <= 1; nu = max sum z. Knife-edge cells: tau = nu = B exactly;
the optimal dual z* ("the ghost") saturates every capacity on the optimal field's support.

A CERTIFIED GUARD FIELD F = (A, w, T) is a finite atomic measure (atoms A, rational weights w,
total T = sum w) for which the exact verifier (verify_case) has proved mu_F(Q) >= 1 for every
admissible Q. Its EXCESS is delta_F := T - B >= 0 (delta_F < 0 would already kill the node
single-field; on knife-edge cells delta_F > 0 strictly because the verifier needs slack).

## 2. Formulation J1 — two capacity families, one packing variable set (the brief's design)

One packing variable set z: {admissible placements} -> R+, and TWO independent constraint
families, both valid for any genuine packing of B disjoint admissible squares (z integral 0/1):

  (C1) family-1 point capacities:  sum_{Q ni p} z_Q <= 1        for p in A1   [disjointness]
  (C2a) family-2 point capacities: sum_{Q ni p} z_Q <= 1        for p in A2   [disjointness]
  (C2b) family-2 BUDGET row:       sum_Q mu_2(Q) z_Q <= T2                     [disjointness:
        the union of the packing's squares has mu_2-mass at most mu_2's total]

  nu_J1 := max sum_Q z_Q  subject to (C1), (C2a), (C2b), z >= 0.

SOUND KILL RULE: if field 2 is certified AND nu_J1 < B, the node is dead. (Every genuine
B-packing induces a feasible integral z of value B.) Note (C2b) needs only disjointness to be
VALID; it has BITE only because mu_2(Q) >= 1 (certified): any packing using a placement with
mu_2(Q) = 1 + c > 1 pays 1 + c against budget T2 = B + delta_2, so total strict excess across
the packing is capped by delta_2 — the packing is confined to field 2's near-equality face.

Implementation (what we actually solve — the LP dual of J1, which is the certificate form):

    tau_J1 := min  sum_p y_p + T2 * lam
              s.t. y(Q) + lam * mu_2(Q) >= 1  for every admissible Q;   y >= 0, lam >= 0,

i.e. the ordinary covering LP over free atoms PLUS ONE FIXED COLUMN "buy the whole field mu_2 at
cost T2". Kill iff tau_J1 < B with row-oracle feasibility (A27 classify rule verbatim: kill
needs added_rows = 0, minmass >= 1). Exact certification: the optimal (y, lam) rounds to the
combined atomic measure y + lam*mu_2 — an ORDINARY case-measure certificate (mu_2 is atomic), so
the A39 cheap-cert rule applies unchanged. tau_J1 = nu_J1 by LP duality.

## 3. Proposition 1 (duality collapse) — what exact arithmetic already decides

PROP 1. For ANY certified second field F2 (indeed any finite list of certified fields),
tau_J1 = tau. In particular on a knife-edge cell (tau = B exactly, as the converged LP optimum
over all atomic measures), NO strict drop is possible in exact arithmetic: nu_J1 = B.

Proof. (<=) lam = 0 recovers the single-field LP. (>=) Any J1-dual-feasible (y, lam) yields the
single measure mu' = y + lam*mu_2, which covers every admissible Q with mu'(Q) >= 1 and has
total exactly sum_p y_p + lam*T2 (T2 IS mu_2's total mass). So the J1 dual optimizes over a
SUBSET of the single-field feasible measures; its value is >= tau. QED.

COROLLARY 1.1. The same holds if (C2a)-type point-capacity rows are added for any atom set
whatsoever (they correspond to free covering columns, already available to the single-field
column oracle at convergence). Multi-field stacking of coverage/capacity constraints is
DUAL-ABSORBED. This is the exact-arithmetic form of the A33 t2 observation ("multi-field
stacking worth 4.6%" — a float-level echo) and of the A42 gap-list caveat (complementary
slackness: all near-optimal fields share the ghost's support).

COROLLARY 1.2 (pre-registered prediction). On every target cell the ablation must measure
tau(1-field baseline) = B, tau_J1(both) = B, lam* = 0 optional at the optimum; ANY measured
strict drop is a finite-pool/row-set artifact and the exact verifier will REFUSE the resulting
certificate. A52's measurement therefore quantifies (i) the artifact size and (ii) the joint
tight structure — it cannot, by Prop 1, produce a certified kill through J1. The brief's success
branch lives entirely in formulation J2 below (and in the honest-failure quantification).

## 4. What is NOT absorbed — exhaustion rows (J2), the certificate-excess weapon

Prop 1 exhausts what disjointness + coverage can say through <= rows. The genuinely new,
still-sound constraints come from combining coverage with the CERTIFIED TOTAL, giving >= rows.
For a genuine B-packing z and a certified field F_k = (A_k, w_k, T_k):

    sum_p w_k(p) c_p  =  sum_Q z_Q mu_k(Q)  >=  B          (each square covers >= 1)
    where c_p := sum_{Q ni p} z_Q in {0,1}  (disjointness), so
    sum_p w_k(p) (1 - c_p)  <=  T_k - B  =  delta_k,  hence per atom p in A_k:

  (E_k)   sum_{Q ni p} z_Q  >=  1 - delta_k / w_k(p)          [exhaustion rows]

plus the cardinality row sum_Q z_Q >= B (the node hypothesis: exactly B remaining squares).
(E_k) is valid for genuine packings but is NOT a covering-dual object: Farkas combinations of
(C*) + (E*) + cardinality produce SIGNED measures (negative parts supported on A_1 u A_2), and
Prop 1's absorption argument fails. J2 is where two fields with genuinely different tight
structure could contradict each other: the ghost must SIMULTANEOUSLY (near-)exhaust two supports
with Jaccard ~ 0.4-0.5 while respecting capacity 1 everywhere. Kill rule: the system

    z >= 0,  sum z >= B,  (C1), (C2a), (E_1), (E_2)

infeasible over ALL admissible placements => node dead. Caveats, stated honestly:
  * strength degrades linearly in the certificate excesses delta_k (knife-edge fields cannot be
    certified at delta = 0 — the verifier needs slack; A39 auto_scale floor 1.0008 => delta ~
    0.01 at B = 10, and perturbed fields carry additional real excess);
  * a MEASURED nu_J2 < B on a finite row set is NOT yet sound (restricting z's support
    under-estimates nu): soundness needs the Farkas certificate (a signed measure) verified
    against all placements. A52 runs this at measurement grade (row generation + fine scan),
    labeled measured-not-certified; exact verification of signed measures is future work (the
    current verifier handles nonnegative atomic measures only).

## 5. The measured obstruction quantities (honest-failure deliverables)

Per node and per second field F2, from the converged baseline state (ghost z*, field mu_1):

  * tau2 excess delta_2 = T2 - B (real mass of the perturbed/region-weighted field);
  * support Jaccard J(supp mu_1, supp mu_2) at 5e-3 matching (diversity actually achieved);
  * tight sets on the final row set R: T_k = {r in R : mu_k(r) <= 1 + 1e-6}; report |T_1|,
    |T_2|, |T_1 n T_2|, Jaccard;
  * GHOST LEAKAGE L_2 := sum_p w_2(p) * max(0, 1 - c_p(z*)) and its per-placement dual
    leak_2 := sum_r z*_r max(0, mu_2(r) - 1). If leak_2 <= delta_2 the ghost already satisfies
    field 2's confinement — the obstruction is total, quantified by the margin delta_2 - leak_2;
  * nu on the joint tight set: max sum z s.t. (C1)+(C2a), z supported on T_1 n T_2 — measures
    whether the joint equality face still carries a full-value fractional packing.

## 6. Ablation protocol (pre-registered)

Targets: A38 l1 knife-edge cells idx 61, 65, 74, 95, 100 (budget 10) + A42 chain nodes k1
(budget 10), k2 (budget 9). Per node: (a) 1-FIELD BASELINE: covering LP on the stored converged
row set with the stored atoms, then row-oracle to feasibility — MUST reproduce tau = B to
1e-6; (b) FIELD-2 ALONE: min-mass reweighting on supp(mu_2) only + oracle — reports T2 and
certifies-or-not; (c) BOTH (J1): free atoms + lam column, row generation to feasibility —
Prop 1 predicts tau_J1 = B; (d) J2 feasibility + section 5 quantities. Field-2 generator: A33
t2 perturbed objectives (cost_i = 1 + delta_i, delta ~ U(-amp, amp), amp in {0.05, 0.10},
2 seeds) and region-weighted (cost 1 + 0.25 * [atom in the node's core zone, inflated by 0.15])
— each field row-generated to oracle-feasibility (worst shrunk mass >= 1) before use.

Success = any strict, certified kill (Prop 1 says: only conceivable via J2 — and only at
measurement grade this attempt); failure = the table of section-5 quantities on all 7 nodes.
