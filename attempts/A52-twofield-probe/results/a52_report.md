# A52 — two-field probe vs the knife-edge cells: CLOSED (done-negative), Prop 1 banked

Fable lead (theory + report), Opus worker (LP/verifier compute). Total compute 1062 s across 7
nodes; 21/21 node x variant ablations completed; zero certification attempts warranted. A29
untouched. Pre-registration: notes/formulation.md (written before compute; predictions upheld).

## 1. Verdict

The N6/two-field idea, in its coverage/capacity form, is DEAD — not for lack of diversity, cost,
or convergence, but by a theorem. The probe's contribution is that the closure is now exact
mathematics plus a 21/21 machine confirmation, and the obstruction is measured: **the ghost is
not one object tied to one field — the equality manifold regenerates a full-value fractional
packing against EVERY certified field pair**, even when the two fields share not a single atom.

## 2. The theorem (Prop 1, duality collapse) — and its face status

**PROP 1 (notes/formulation.md §3, proof three lines).** Let the node LP have value tau over
atomic covering measures ("every admissible placement covers >= 1"). For ANY finite list of
certified guard fields F_k = (A_k, w_k, T_k), the joint LP — one packing variable set z, family-k
point-capacity rows at A_k, and family-k budget rows sum_Q mu_k(Q) z_Q <= T_k — has value
nu_joint = tau. Proof: the joint dual optimizes total mass over covering measures of the special
form y + sum_k lam_k mu_k, a SUBSET of all covering measures (>= tau), containing the single-field
optimum at lam = 0 (<= tau). QED. On a knife-edge cell (tau = budget exactly) NO strict drop is
possible in exact arithmetic, for any second field whatsoever, in any number.

**Seventh face of the enumeration-certificate mismatch law** — it earns the name; exact
statement: *every constraint family on packings derivable from disjointness plus a certified
guard field (point capacities, budget/confinement rows) is absorbed by the single covering dual:
stacking certified fields is void, term by term, because any Farkas combination of such rows IS
a covering measure and pays full mass for its coverage. The ghost never needs a particular
field's permission — its equality manifold is a property of the NODE, invariant under the choice
of certified field, so no second coverage-type family can thin it. Only constraints that are
false for fractional z (integrality, position/enumeration information from view 2) can.* This is
the view-3 (marginal) face: A45/A46/A47 named why positional charges vanish at strata boundaries;
A52 names why coverage certificates cannot be COMPOSED into more than one. The A33 t2 measurement
("multi-field stacking buys 4.6% where independence predicts 7%", notes.md:66) and the A42
gap-list caveat (complementary slackness, shared ghost support) were the float-level shadow of
this exact statement.

## 3. Machine confirmation (the ablation, 21/21)

Targets: A38 knife-edge level-1 cells n061/n065/n074/n095/n100 (B = 10) + A42 chain nodes k1
(B = 10), k2 (B = 9). Per node, 3 second fields: p1/p2 (perturbed objectives, amp 0.05/0.10,
A33-t2 pattern, atom pool ~3.6k, node n074 6.1k), rw (region-weighted, +25% cost in the inflated
core zone). Every field row-generated to oracle feasibility before use (worst shrunk mass >= 1).

| check | result (21/21) |
|---|---|
| baseline reproduction (1 field) | tau = B, max dev **1.8e-15**, oracle-feasible |
| field-2 real mass T2 | = B, max excess delta2 **2.3e-11** — the perturbed objectives found genuinely different EXACTLY-OPTIMAL fields |
| field-2 diversity | support Jaccard **0.000-0.167** (A33 root-level was 0.41-0.50; here mostly 10 completely fresh atoms) |
| field-2 alone | tau = B |
| J1 both (free atoms + lam column) | tau_J1 = B, max dev **2.48e-09** (n061/rw) — three orders BELOW the 1e-6 kill threshold |
| lam* | degenerate as Prop 1 predicts: {0, 0.5, 1} across runs, optimum indifferent to mixing |
| exact certification | 0 attempts warranted (correctly gated; Cor 1.2 upheld) |
| nu_J2 (exhaustion rows, measured) | = B on every node x variant; **0 of 20-23 exhaustion rows bind** |
| nu on joint tight set | = B on every node x variant |

## 4. The obstruction, quantified (section-5 deliverables; measured, not certified)

- **Tight sets are node property, not field property.** On the final row sets, tight-set Jaccard
  J(T1, T2) = **0.785-0.989** while SUPPORT Jaccard is 0.000-0.167. Two fields sharing zero atoms
  mark out essentially the same equality face of placements (|T1 n T2| = 848-11773 rows).
- **The exhaustion test at full strength.** Because delta2 ~ 1e-11, the J2 system forced coverage
  EXACTLY 1 at all 19-23 atoms of BOTH supports simultaneously, plus capacity <= 1 everywhere,
  plus cardinality >= B — and a full-value fractional packing still exists on every node x
  variant (nu_J2 = B, zero binding exhaustion rows). The joint equality face is not thinned AT
  ALL; its packing value does not move by any measurable amount.
- **The 6/21 leak rows — the one honest sign of life, explained.** Six rows (n061 x3, n074/p2,
  k2/p2, k2/rw) have ghost leakage leak2 = sum_r z*_r max(0, mu2(r) - 1) of 0.4-1.0 with margin
  delta2 - leak2 < 0: the SPECIFIC stored ghost z* routes one unit of weight (0.4 fractional at
  n074) through placements of field-2 mass 2 (max_cap_mu2 = 2.0 — one square covering two field-2
  atoms), so that particular dual vertex IS infeasible for field-2 confinement. But in all six
  cases the atom-side leakage L2 = 0.000 — every field-2 atom is still exactly covered — and
  nu_J2 = B: the LP simply reroutes to a neighbouring vertex of the optimal face in which every
  placement covers exactly one atom of each field. The equality manifold has enough dimensions
  (thousands of joint-tight rows) to absorb any single field's veto. This is the regeneration
  mechanism in miniature: two-field probes can kill a GHOST VERTEX, never the GHOST FACE.

## 5. Deviations from the pre-registered protocol (recorded)

1. The A38 W1/W2 field-cut row filter was NOT reinstalled for oracle-generated rows (worker ran
   with hyp filters only; logged as `row_filter: none (original solver)`). Conservative
   direction — extra admissible rows can only raise tau — and the baselines nevertheless
   reproduced tau = B to 1.8e-15, so the reproduction check is if anything stronger.
2. J2 and all section-4 quantities are measurement grade (finite final row sets, float duals),
   exactly as pre-registered in formulation.md §4; no signed-measure verification exists yet and
   none was needed (nothing to certify).
3. n074 needed 4 baseline oracle rounds and a doubled pool (6144); all others converged in 1.
4. Six leak rows, not five as an early readout suggested; values above.

## 6. What remains for N6, honestly (gap list)

1. **Coverage-type routes are closed with prejudice.** Prop 1 covers every proposal of the shape
   "add capacity/budget rows built from certified fields" — one field, many fields, perturbed,
   region-weighted, all of it. Do not spend compute here again; the screening test is three lines.
2. **The exhaustion/J2 route survives only as mathematics, not as measurement**: its Farkas
   certificates are SIGNED measures, outside the current verifier, and at delta = 0 full strength
   it measurably fails to thin the face (this attempt). A signed-measure weapon would need to
   exploit something the LP does not already saturate — no candidate known.
3. **What can still crack a knife-edge cell** (unchanged, now with sharper reasons): constraints
   false for the fractional ghost — integrality/enumeration information (A53's discrete
   skeletons + residual-region LPs, currently in flight, is exactly this shape), theta'-type
   second-order rows (A16's grid kills; continuum revival still needs a new idea), or the A42
   ghost-mass profiling conjecture as a diagnostic for WHERE integrality must be injected.
4. The five A38 knife-edge cells + A42's saturated chain remain the canonical N6 test set; any
   future weapon should be pointed here first (cheap: 1062 s bought this entire attempt).

## 7. Files

- notes/formulation.md — pre-registered theory note: J1/J2 formulations, Prop 1 + corollaries,
  section-5 obstruction definitions, ablation protocol.
- code/twofield.py (+ A42-code copies) — driver; results/nodes/{n061,n065,n074,n095,n100,k1,k2}.json
  — per-node phase records; results/ablation.json — the 21-row table; logs/ — per-node logs.
- Registry row updated (done-negative); LOG.md entry; docs/ideas.md I-L13 addendum (two-field
  route closed).
