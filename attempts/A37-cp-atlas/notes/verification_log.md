# A37 lead verification log (Fable)

## Pilot (2026-08-27) — VERIFIED, amendments approved
- code/a37_check.py run independently: 4 certificates, 258 checks ALL PASS; value-inflate gate
  fails as required (5/5 per the pilot's own runs).
- Trump self-test accepted as a strong regression: generic pipeline reproduces A22 (Krawczyk
  ratio 0.0566 at r_N) and A36 (kappa_eff 19.316; h 3.759e-3 vs 3.779e-3, -0.5%) from scratch.
- LEAD CORRECTION (exact arithmetic): the pilot's "three corner-corner pairs incl. two absent
  from A35/M4" is a labeling/classification artifact — in A22 labels the coincidences are the
  flush pairs (0,1),(0,3) (edge-endpoint corners, inevitable for flush aligned squares) + the
  known (1,3). NO missing contacts; A36 basis v3 remains the Trump reference. Recorded also in
  A36/notes/verification_log.md. Cookbook amended: audits must store canonical geometric
  signatures, not just family-local indices.
- All 8 amendments approved and appended to cookbook.md (notably: [V]-rule as the definition of
  a safe row — the pointwise form of A36's over-estimate principle; V_soft r_res*h correction;
  exact-Fraction flooring — a float bug the checker caught; bisect-vs-incumbent radius rule;
  GN-refine before classify; tolerance ladder; branch only no-[V]-safe pairs; layout converter).
- Taxonomy accepted: RIGID / VALLEY (rank-deficient loaded core, soft cert) / NOT-CP
  (fixed-angle optimum, e_s infeasible with theta rows — trivial-bound cert + flag). Pilot found
  fam1+fam6 VALLEY (rank 30, 32), fam4 NOT-CP with 5 rattlers. Expectation set: the atlas will
  be mostly soft certificates; that is what far-field discharge needs (values, not rigidity).
- Open issue carried: fam1's z_center is a least-squares point 3.15e-3 from the A04 point with a
  1.4e-19 row inconsistency (one corner-corner row not simultaneously closable) — harmless for
  the soft certificate (enters through W0), flagged in its atlas entry.

## Batch A (2026-08-27) — landed; lead decisions on the coordinator's steers
- 14 families, 532 checks PASS (batch), 790 PASS full-dir. HONESTY NOTE recorded: the pilot's
  "5/5 gates" was carried by fam00's 3R certificate on the drop-aux gate (soft certs without
  loaded aux rows cannot fire it); batch A applied the gate fix so drop-aux is exercised (or
  explicitly N/A) per certificate class.
- Class tally so far (17 non-Trump processed): 12 NOT-CP, 5 VALLEY, 0 RIGID besides Trump.
  TAXONOMY DECISION (lead): NOT-CP value certificates are SOUND far-field discharges (the class
  describes the point's dynamical role, not the bound's validity) — recorded in atlas meta;
  as attractors they are artifacts of A04's angle lattice; drain worker dispatched to
  re-minimize each with free angles and map where they drain (new-family cap 5, then stop for
  PI/advisor review).
- DEDUPE DECISION: adopt (s-value, canonical contact-signature) as the atlas key; batch A's
  finding that index pairs 1&2 and 13&14 are single 6-dim mechanisms (one valley each) to be
  verified at merge time and recorded as stratum-level merges, not four families.
- FAR-FIELD NOTE (A38 brief material): for s_min >= ~3.887 the trivial Lipschitz bound
  sigma >= s(z-hat) - h beats the barrier out to the [V]-margin radius; the barrier buys ~1.4x
  only on the low-s families. The far-field tree should consume trivial-bound boxes for
  high-value CPs and barrier boxes for the low ones.

## Batch B (2026-08-27) — VERIFIED
- Lead re-ran checker on certs_batchB: 14 certs, 921 checks PASS; value-inflate gate bites.
- 12 NOT-CPs constructively confirmed (descent witnesses) — gold standard, cited in report.
- Fam 27 false-NOT-CP accepted; reclassified VALLEY-MARGINAL in the merge; drain worker
  corrected mid-run (excluded 27 from its counts, marked superseded).
- Fam 31 h_probe ceiling: lead patched --hmax into the pipeline, re-ran fam 31 (h 1/20 ->
  490529/8192000 = 0.0599, V-vs-incumbent bound), re-checked (804 checks PASS on certs/).
- Checker N/A fix adopted (no-op corruptions report NOT APPLICABLE).

## Drain worker (2026-08-27) — VERIFIED (accepted as [NUM] taxonomy, no certificates)
- 24/24 drain, 0 stuck; strictly monotone always-feasible descent semantics accepted; the one
  barrier-crossing (smoothed run on 27) correctly quarantined as basin hop, not drain.
- 4 NEW families; lead ran them through the certificate pipeline (--fam 1000..1003 via lead's
  loader patch; drain z layout verified A22-interleaved by containment check): all certified,
  h in [2.56e-2, 4.84e-2], V >= 3.877084. NEW-1 classified VALLEY-MARGINAL by the lead under
  the constructive-witness policy (pipeline binary LP disagrees with drain deep re-descent —
  fam-27 pattern; recorded with both diagnostics).
- Dedupe key adopted (s at 1e-8 primary + geometric corroboration; rattler caveat) in atlas meta.

## CLOSED 2026-08-27. atlas_final.json (36 entries), final_report.md, registry done-success.
Full-dir checker totals at close: certs/ 23 certs 1097 checks PASS; certs_batchB/ 14 certs 921
checks PASS.
