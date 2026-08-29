# A44 verification log (Fable lead)

2026-08-29 (setup)
- Read BRIEF, structure_lemmas.md (soundness ledger), drain_lemma.md v3, A37 atlas_final.json
  meta + entries, A43 report + formalization (N4 provenance: CONDITIONAL, worth ~x1e4 if
  proved), A35 m1/m1b reports (Trump v1 38 rows rank 34 sig 4; v2 42 rows rank 34 sig 8;
  no nonneg self-stress => lambda0=0 branch empty at Trump).
- Pre-count from atlas contact tables (lead, quick pass): genuine-CP families near the
  Maxwell frontier: 13/14 (k=10, m~31=3k+1 tight), 27 (k=11, m~33=3k, VALLEY-MARGINAL,
  6-decimal-rounded coords per A43-G5), 31 (k=11, m=33=3k, solid VALLEY, cert h=0.0599),
  NEW-1 (k=10, m~31 tight, MARGINAL), NEW-2 (k=10, m~30=3k), NEW-3 (k=11, m~34 tight).
- Hand-check of fam31 (lead, direct from contact_table): wall edges 10 (8 wall-flush, 18
  wall rows), pair edges 11 (4 flush, 15 pair rows) => m=33, E=21, F=12, chi=-1; all 11
  squares have contacts; rank 30 => sig=3, d=4, chi=sig-d=-1 consistent. Refutation of
  m>=3k+1 stands unless some square is UNLOADED (k_H<11) — delegated to LP analysis.
- theory.md written: L8 index identity, L9 rigid=>Maxwell (+census corollary), L9' lambda0=0,
  L10 s-neutral flexes, L11 non-thin local counts (N4-L0 proved on non-thin lambda0>0 branch),
  refutation frame, C* (m>=3k) and C-rep (max-contact representative) as labeled conjectures,
  census split rigid-possible/flex-only.
- Dispatched Opus eval subagent: per-entry physical Maxwell counts, [NUM] rank + index
  identity check, contact completeness audit (<1e-3 near-misses), FJ multiplier LP
  (loadable/forced rows, H_max, min-support), candidate verdicts B1-B7, Trump v1/v2
  reconciliation.

2026-08-29 (results + lead verification)
- Census re-run landed: regression 510/510 sampled rows exact vs A43 level1.json; baseline
  MAIN' k=11 reproduced to the last bit; C-rep conditional replicates A43's 1.6e26-8.9e26.
  Lead spot-checked census.json (regression.PASS true, column structure sane).
- Atlas eval landed: lead spot-checked candidates.json against my own hand-count of fam31
  (E=21, F=12, m=33, chi=-1: EXACT match), Trump (m=41, min-support 30, FJ feasible), fam27
  (FJ lambda0=1 LP infeasible; note A37's own kkt_lp was also False there — consistent with
  VALLEY-MARGINAL). chi = sig - d identity verified by the eval on all 36 entries; L1 canary
  B5' passes on all 36; rattler alarm empty; verdict fields match the report tables.
- Convention deviation reviewed and APPROVED by lead: eval overrode the brief's literal
  "CORNER-CORNER = 1 row" where the geometric contact set is a segment (coincident-corner
  flush, 2 contact points, the A35/M1b centre-distance-1 pairs) — this is exactly Fact 0's
  intent; the brief-literal shadow table changes no verdict (B1 refuted both ways, B1'
  survives both ways). Documented in eval_report.md sections 5-6.
- theory.md updated: counts pinned to the ACTIVE graph (support-level Maxwell refuted even at
  Trump — min-support 30 < 34; fams 1/2 loaded core k_H=6 with m_H=17 < 3k_H+1); fam31 named
  as primary refutation witness; C* survivor status + B3/B6' margins recorded.
- Final report written: results/a44_report.md. Registry row updated.
