# A62 findings — every ambiguity/hole the trust-ledger pass forced (2026-09-01)

Context: executing F3 (formal top-level statement), H13+H11 (dependency graph + conjecture
sweep), C1/C2 (TCB + frozen specs), C9 (manifest) from `docs/publication_checklist.md`, at
commit `c9980bf`. Artefacts: `lean/PackingCertMathlib/PackingCertMathlib/TopLevel.lean`,
`results/depgraph.json` + `.svg`, `docs/specs/*`, `docs/manifest_3.8x.md`.

Severity: **HIGH** = a load-bearing obligation with no written proof/certificate route
executed; **MED** = must be done, route known; **LOW** = decision recorded / cosmetic.

---

## F1 — packing = disjoint INTERIORS; the A28 UB theorem uses full disjointness. [LOW, decision recorded]
The formal definition (`IsPacking`) uses pairwise disjoint interiors (contacts allowed —
the extremal packing has 56). A28's `eleven_unit_squares_in_3877084` proves the stronger
pairwise-`Disjoint` family: fine for the upper bound (stronger packing => Fits), but the two
notions must never be conflated in the other direction — see F9.

## F2 — the equality claim's UB half has NO certificate route on file. [HIGH — new obligation]
`s(11) = s-hat` needs Trump's packing AT s-hat (`trump_packs_at_shat`). The strongest
Lean-checked UB is 3.877083591023 = s-hat + 8.8e-10, and `checkPacking` requires strictly
positive margins, so the current UB certificate family can **never** certify the
contact-closed packing at s-hat. Routes: (a) A22's Krawczyk existence + feasibility (proves
the exact contact solution is a packing at s-hat) — requires the F6 t-reparametrised replay
to be citable/formalisable; (b) closedness of `Fits` (D1 machinery) + a sequence of rational
certificates converging down to s-hat. Until one is executed, the honest theorem is
`s-hat <= s(11) <= 3.877083591023`.

## F3 — the uniqueness clause is not implied by any written lemma. [HIGH — new hole]
The selection lemma (L6/CC-2) proves the *bound* by producing **some** k-maximal
slide-stuck minimiser — a *different* packing (slides move squares). The S1 uniqueness
clause quantifies over **every** packing at side s-hat. Writing the composition in Lean
forced the gap into one axiom (`unique_transfer`): every packing at s-hat has a
symmetry-image representative in some stratum. Candidate proof: slides at the optimal side
move through packings at side s-hat; once the slid representative is pinned to z-hat, the
basin equality clause applied along the continuous slide path forces the path constant.
Nothing like this is on file. (Checklist S1's "decide now whether uniqueness is claimed" is
now a theorem-shaped decision: claim it and prove `unique_transfer`, or drop it from S1.)

## F4 — stratum semantics: certificates prove "contains pins", the composition needs "skeleton exactly". [HIGH — is H10 + a missing bridge lemma]
`InStratum i s z` must mean *skeleton exactly of class i* — under the monotone reading the
kill axiom would be **false** (a trump5 packing also "contains" k4_03's pins, and trump5 is
alive). For the 61 killed classes the monotone certificate form is stronger, fine. For the
K1-protected survivors (six k=4 classes + ten k<=3), exactness/maximality is the ONLY
exclusion mechanism — that is checklist H10, the largest open leaf — and even the logical
bridge "monotone kills + census containment lattice + K1 => exact-stratum exclusions for
the killed part" lives as scattered A55 cap-logic, not as a written lemma.

## F5 — coordinate mismatch: rigidity boxes in (c, theta), everything else in (c, t). [MED]
A22/A36/A37 certify inf-norm boxes over raw angles; the case/parametric certificates, the
3.84 tree, and the formal statement use t = tan(theta/2). d-theta/d-t = 2/(1+t^2) != 1
(~1.77 at Trump's tilt), so radii do NOT transfer verbatim. `rBasin` is opaque in
`TopLevel.lean` until the basin certificate and the A60 residual-tree landings are expressed
in the SAME box. A28's "re-emit the Krawczyk certificate in t" recommendation is now
load-bearing twice: for the Lean replay (checklist F6) and for coordinate consistency.

## F6 — window transfer cannot be a separate hypothesis; s0-only kills do not instantiate the kill axiom. [MED, campaign-gated]
A56 refuted monotone transfer, so a factorisation "kill at s0" x "transfer principle" would
axiomatise a falsehood. The formal kill/residual axioms therefore quantify over all
s in [3.82, s-hat] directly — which makes today's coverage shortfall formally visible:
12 strata s0-only (A61 running), the two A57 sub-stratification kills (k5_11, k5_16)
s0-only with **no scheduled window form**, 2 sliver bands, and the A59/A60 residual tree
fixed at s0 (G-A59-7, the low-s slab). None of these currently instantiate `stratum_kill` /
`trump_residual` as stated.

## F7 — s-hat is pinned to the octic only by an axiom; the composition never uses it. [LOW-MED]
`#print axioms s_eleven_eq` does NOT list `shat_spec`: the octic tie is a statement-
*identity* obligation (S3), not a proof step — the composed proof pins s-hat only through
`trump_packs_at_shat` + `basin`. A rational sign-change/Sturm certificate for the octic on
[3877083/1000000, 3877084/1000000] discharges `shat_spec` and turns `shat` into a
definition. Ten minutes of certificate work + a day of Lean; until then the theorem's
*name* for its own value is axiomatic.

## F8 — t in [0,1] closed double-covers the axis-parallel square (t=0 == t=1). [LOW]
Harmless for soundness everywhere (all quantifiers are universal over admissible squares);
census D4-counting must quotient, and does.

## F9 — S4 boundary discipline is a REAL missing lemma, applied at every kill. [HIGH]
`verify_case` PASS speaks about families of pairwise-**disjoint closed** squares (its
bridge sums mu over disjoint squares — touching squares could share an atom). The
composition applies kills to a minimiser at its own side m, which is only
interior-disjoint (it has contacts). The repair — scale by lambda = s'/m to a nearby
rational s' in the certified window, where the scaled packing is strictly disjoint and
point/small cores are still contained (pin-containment has slack) — is used implicitly at
EVERY kill application and is written nowhere. This is checklist S4 landing exactly where
it predicted; it also silently requires kills on a *dense set of sides near m*, which only
the parametric (window) form provides — another reason F6's shortfall is load-bearing.
Must become a lemma (with the degenerate case: pins whose containment is tight).

## F10 — quantifier order of stratification: existential over minimisers. [MED = H1]
`stratify` takes the attained minimum and returns SOME stratified minimiser. Correct for
the bound; the degenerate slide cases of the selection lemma (slide creating a contact
mid-way, ties, sigma-changing slides, simple-in-one-normalisation-only) remain unwritten
(H1) — and F3 shows the uniqueness clause needs MORE than any of this.

## F11 — the census/stratum layer is definitional debt in the formal statement. [MED = H2]
`StratumIdx / trumpStratum / InStratum` are opaque axioms: the Young-form skeleton
predicate has no formal definition yet, so certificate families have a formal *shape* but
not yet a concrete formal target. Formalising the definition gives H2's independent
re-enumeration its target and removes three axioms.

## F12 — the residual axiom's window quantifier is the honest form of H7/G-A59-7. [MED, campaign-gated]
`trump_residual` over all s in [3.82, s-hat] packages: A60's zone-tree (running, s0), the
low-s slab, S6 basin containment in all 33 coordinates mod G, and the D4 reduction re-proof
at the working side (H12, machine-checked at 3.84 only). Each named in the axiom docstring.

---

## H11 sweep verdict (from `results/depgraph.json`)

**Zero nodes labelled `conjecture` are load-bearing** in the live composition (walk of
`uses` edges from TOP). Named suspects:
* **G-A59-10** (residue ladders, "extrapolated") — the suspicion was *vindicated*: A60's
  falsifier shows the ladders DIVERGE at the radius A59 extrapolated (18->620 boxes) and
  terminate only at the corrected conditioning radius 4.45e-4. Now measured, not
  extrapolated; the node stays `open` until A60 closes. This is the H11 discipline working.
* **G-A59-12** (tau* = k) — motivation-only; the load-bearing direction (tau* >= budget) is
  witness-certified per node by `alivewitness.py`.
* **I-L19** (flush-mandatory) — off-tree: no live leaf of the stratification composition
  invokes the A46-A51 program. Re-run the sweep if the k<=3 route reaches for its toolkit.
* **Seam S3** (BDBFS termination, "empirical") — off-tree: it belonged to the superseded
  T0/A38 far-field composition. `T0_composition.md` should be marked superseded-as-plan
  (kept as the K1/W1/W2 semantics reference).

**The distance-to-done is 14 `open` nodes, not conjectures** — largest: C.K4TIER (H10);
new this attempt: A.UBshat (F2), A.UNIQ (F3), B.EXACT (F4); the rest: A.PARAM, A.S3,
C.A61, D.TREE/D.LADDER/D.SLAB/D.D4/D.S6, E.COORD, plus prose-to-Lean items (A.F2).

## TCB findings (from `docs/specs/tcb.md`)

* **T1 [HIGH]** No standalone end-to-end verifier exists for the s0-side tree compositions
  (A57 sub-trees, A59/A60 zone-tree) — the 3.84 track has `verify_tree2.py`, the live track
  has in-attempt audits only; the A54 `substrat.py` soundness gap lived exactly in this
  layer. A `verify_tree_s0.py` analogue is owed before the composition is citable.
* **T2 [MED]** `verify_case.py` / `verify_param.py` decide the tree with one implementation
  each (C3); the frozen specs are the clean-room inputs.
* **T3 [MED]** `mpmath.iv` sits in the decision path of the rigidity chain (three
  checkers) — remove via the t-reparametrised Lean replay or an independent interval
  implementation.
* **T4 [LOW]** 16 byte-identical copies of `verify_case.py` verified identical today;
  deduplicate or hash-pin (the spec now pins the canonical hash `521cb01f...`).
* **T5 [LOW]** Existing case certificates carry no `format` field; the spec freezes the
  format by content and recommends `"format": "case-lp-certificate-v1"` for new ones.
