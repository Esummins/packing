# A37 — the critical-point atlas: final report (Fable, lead; 2026-08-27)

Task (PI): extend the A35/A36 machinery to the full A04 critical-point catalogue — per-CP contact
audit, exact rationalization where possible, stratum-blind value certificates at max-form
pinning, corruption-gated re-checkers, and a machine-readable atlas for the far-field tree.

## Headline

**The atlas is done, and it is much smaller than the catalogue: the 32 A04 families below 3.95
collapse to 10 distinct attractor structures** — Trump (the only RIGID point) plus 9 valley
mechanisms: {1~2} (one 6-dim mechanism, two catalogue entries), 6, {13~14} (ditto), 27
(marginal), 31, and four families A04 MISSED (A37-NEW-0..3, found by draining A04's own
fixed-angle artifacts). The other 24 catalogue entries are NOT-CP: local minima of s only at
A04's lattice tilts, each constructively confirmed (explicit smaller-s packings) to drain into
the 10. Every one of the 36 atlas entries carries a certified value-discharge box regardless of
class.

## Deliverables

- results/atlas_final.json — 36 entries (32 catalogue + 4 new). Each entry: class
  (RIGID / VALLEY / VALLEY-MARGINAL / NOT-CP), rank + spectral data, audited contact table with
  coordinates + canonical signature, tolerance ladder, certified radius h and value V as exact
  rationals, cert path, dedupe/stratum-merge links. Claim semantics (meta): every feasible
  configuration z with ||z − z_center||_inf ≤ h has sigma(z) ≥ V.
- results/certs/ (23) + results/certs_batchB/ (14): 37 certificates, standalone re-checker
  code/a37_check.py (rebuilds rows from the certificate's own contact table; no producer libs),
  **2018 checks ALL PASS**; corruption gates omega-sign / h-big / drop-aux / drop-branch /
  value-inflate all fail as required (no-op corruptions honestly reported NOT APPLICABLE per
  class — the drop-aux gate is only exercisable where aux rows carry omega).
- results/drain.json + drain_report.md — the NOT-CP drain probe (float, [NUM], no certificates):
  24/24 sources drain to genuine attractors, 0 stuck; 13 to known valleys (1, 6, 13), 11 to the
  4 new families; strictly monotone always-feasible descent, so each drain is a statement about
  the actual basin.

## Numbers that matter

| item | value |
|---|---|
| families processed | 32 catalogue (< 3.95) + 4 discovered = 36 |
| distinct attractor structures | **10** (1 rigid + 9 mechanisms; stratum merges {1~2}, {13~14}) |
| NOT-CP (fixed-angle shadows) | 24, all constructively witnessed and drained |
| certified radius h range | 3.76e-3 (Trump, barrier) … 6.0e-2 (high-s families, trivial-bound regime) |
| all V | ≥ 3.877084 (the incumbent) by construction of the h-maximization |
| value enclosure, Trump | sigma ≥ 3.877083590022813997 on box(h = 3.759e-3), generic pipeline, reproducing A22+A36 |
| checks / gates | 2018 PASS / 5 gate types, all fail as required |
| wall time, everything | pilot 51 s + batch A ~25 min + batch B ~30 min + drain 15 min + 4 new fams 80 s + re-checks ≈ **well under 2 desktop-hours** (budget was a day) |

## Findings beyond the deliverable

1. **A04's catalogue is NOT complete as an attractor list.** Draining its own NOT-CP points
   found 4 valley families it lacks (s = 3.9027, 3.9122, 3.9244, 3.9255; all exactly feasible;
   nearest catalogue s off by 1.5e-5..7.5e-4, far outside convergence noise). Benign for the
   bound (all ≥ 0.0256 above the incumbent) — but it makes the discovery loop (the PI's
   bidirectional protocol) LOAD-BEARING for the far-field campaign: certificates only discharge
   neighbourhoods of CPs someone has found. NEW-3 is shallow (1e-2 perturbation escapes to
   family 6); NEW-1 is marginal (fam-27 pattern: binary equality-LP says NOT-CP, deep re-descent
   finds no witness — classified VALLEY-MARGINAL under the constructive-witness policy).
2. **Classification needs residual scales, not binary LPs.** Family 27 (and NEW-1) are critical
   to ~1e-7 with clean positive multipliers at 1e-2 scale; a binary equality-LP at the contact
   tolerance misclassifies them. Adopted policy: NOT-CP requires a constructive smaller-s
   witness. (Both certificates were always sound — value bounds are class-independent.)
3. **The trivial bound owns the high ground.** For s_min ≥ ~3.887 the Lipschitz-trivial
   discharge sigma ≥ s(ẑ) − h beats the barrier out to the [V]-margin radius; the barrier
   machinery earns its keep only on the low-s families (1.3–2x radius there). Far-field design
   should consume trivial boxes for high CPs, barrier boxes near the incumbent.
4. **Dedupe must be s-primary.** Rattlers translate AND rotate freely, so coordinate/tilt
   metrics false-negative on rattler-bearing families; s at 1e-8 (four orders inside the
   inter-family separation) + partial geometric alignment as corroboration is the working key.
   Conversely the 3.903x cluster (19..24) is SIX distinct configurations sharing s to 2e-4 —
   never merge by s-value alone across that scale.
5. **The audit lessons from A35 held everywhere**: every family has 2–5 corner-corner pairs
   (one with 4 tied axes); the [V]-rule + branch disjunction handled all of them; the A04
   points' convergence varies by 6 orders of magnitude (tolerance ladder essential); one
   false NOT-CP caught by batch B's residual analysis.

## Honest failures / gaps

- G-A37-1: NEW-family certificates are built at drain landing points refined by the pipeline's
  GN step; their z_centers are float-rationalized, not exact algebraic points (fine for soft
  value certificates; a future 3R pass could harden the rigid-looking ones).
- G-A37-2: NEW-1 and fam-27's marginal status is unresolved at the 1e-7/1e-2 scale — deciding
  whether they are true valleys needs second-order or exact-algebraic work; their boxes are
  certified either way.
- G-A37-3: the drain probe is [NUM] float; its taxonomy (not its certificates — there are none)
  would need interval hardening if the far field ever leans on "drains-to" claims rather than
  the value boxes.
- G-A37-4: completeness beyond 3.95 unexamined; and completeness below 3.95 is only "as of
  today's catalogue + 4": nothing here proves no further attractors exist — that is exactly the
  global wall (A31/A32), unchanged.
- G-A37-5: certs_batchB/fam31_3S.json is superseded by certs/fam31_3S.json (ceiling raised
  1/20 → 1/10; h now 0.0599, V-vs-incumbent-bound). Both verify; the atlas points at the
  superseding one.

## Files

notes/cookbook.md (+ approved amendments), notes/verification_log.md, code/a37_pipeline.py,
a37_check.py, a37_drain.py, a37_merge.py, results/atlas_final.json, atlas*.json, certs/,
certs_batchB/, drain.json, drain_report.md, a37_pilot_report.md, pipeline/check/gate logs.
