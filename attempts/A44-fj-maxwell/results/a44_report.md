# A44 — the FJ-Maxwell bound: REFUTED unconditionally, proved conditionally, priced honestly
(Fable lead, 2026-08-29)

## 1. Question and verdict

A43 ranked one unproven statement as the single biggest census lever (~x1e4): a Maxwell-type
row-count lower bound m >= 3k+1 for the structures of FJ-critical configurations (N4
"flush-mandatory"). The brief: refutation hunt against the A37 atlas first, prove what
survives at T-quality, measure the composed census factor.

**VERDICT (three lines).**
1. The unconditional bound is **REFUTED by the lab's own atlas**: family 31 — a solid VALLEY
   with a certified value box, FJ-feasible at lambda0 = 1 with all rows loaded — has m = 3k =
   33 < 34. The x1e4 column as A43 measured it silently discarded 99.94% of the census
   (everything with m < 3k+1), and genuine critical points live in the discard.
2. What survives the atlas is the weakened frontier **C\*: m >= 3k** (tight at families 27 and
   31, both conventions) — and it is provably **unreachable by the FJ + counting route**
   (first- and second-order necessity admit sig = 0, d >= 1 curvature-blocked valleys at
   m <= 3k). It stands as a labeled geometric conjecture, not a theorem. The proved content is
   the conditional structure: rigid => m >= 3k+1 (L9), lambda0 = 0 => m >= 3k+2-d (L9'),
   the exact RIGID-POSSIBLE / FLEX-ONLY census split (L9 contraposition), and N4-L0
   (2E >= 3k+1) as a theorem on the non-thin lambda0 > 0 branch (L11 + L6).
3. Measured on the A43-H1 census (regressions exact): the C-rep-conditional column
   (m >= 3k+1) buys x1592, the C\*-conditional column (m >= 3k) buys x354 (x3.0e3-1.5e4
   composed with non-thin) — 80% of the log-kill survives the honest weakening — but the
   composed conditional count is still 6.5e26-4.3e27 at k = 11: **enumerate-then-solve stays
   NO-GO under every threshold**. Both columns remain CONDITIONAL; the sound object is the
   two-branch decomposition, which kills nothing.

Honest refutation = success: the N4 lever is now settled — dead as a theorem, alive only as
two labeled conjectures whose exact price is on the table.

## 2. Candidate table (test bed: 36 atlas entries, 12 genuine RIGID/VALLEY/VALLEY-MARGINAL;
full table + margins in results/eval_report.md, machine-readable results/candidates.json)

| candidate | statement (active graph, Fact-0 rows) | verdict | witnesses / tightness |
|---|---|---|---|
| B1 (= N4 premise) | m >= 3k+1 | **REFUTED** | fam 31 (33 < 34, fully loaded), fam 27 (marginal); tight at NEW-3 |
| B1' (= C*) | m >= 3k | SURVIVES (conjecture) | tight at 27, 31 (+NEW-2 under shadow conv.) |
| B2 family | support-level Maxwell (any form: m_H, loadable rows, min-support, vs k or k_H) | **REFUTED, everywhere** | min-support 30 < 34 at TRUMP itself; fams 1/2: k_H = 6, m_H = 17 < 19 |
| B3 | 2E >= 3k+1 (N4-L0) | SURVIVES, margin +8 | proved on non-thin lambda0>0 branch (L11) |
| B4 | F >= 3k+1-E (N4-L1, the x1e4 form) | **REFUTED** | fams 27, 31 (12 < 13) |
| B4' | F >= 3k-E (C* flush form) | SURVIVES (conjecture) | tight at 27, 31 |
| B5 | every active-core square row-degree >= 3 | REFUTED | fams 1, 2, NEW-1, NEW-2 (unloaded squares) |
| B5' | L1 canary (loaded squares, >= 2 loaded edges) | PASSES all 36 | mapping sound |
| B6/B6' | F >= 1 / F_pair >= 1 | SURVIVE (min F_pair = 3) | weak; unproven |
| B7 | isostaticity rank >= 3k+1 | REFUTED (known) | every valley, rank 27-32 |

Refutation hardening: contact-completeness audit re-computed every pair/wall gap at every
z_center — no missed contact at any genuine entry that could raise the refuting counts (fam
31's nearest non-contact is > 1e-3 clean; fam 13's one borderline wall row at 5.6e-4 would only
RAISE m). Rattler alarm clean (atlas rattlers carry no contacts). Trump reconciles exactly with
A22 v1 (38 rows) and A35 v2 (42 rows) — differences are tie-alternative and dist-surrogate
rows, no contact-set discrepancy.

**New structural fact (beyond the brief):** Maxwell counting fails at the SUPPORT level even
where the configuration is rigid — Trump admits FJ certificates with 30-row support (< 34).
The census can only ever price ACTIVE graphs; support structures obey no row count at all.
And a genuine valley's loaded set can be 6 of 11 squares (fams 1/2) — "loaded core" and
"census core" are different objects, now cleanly separated in theory.md's conventions.

## 3. Proved at T-quality (notes/theory.md; all elementary, self-contained)

- **L8 (index identity):** m = 3k+1 + sig - d on the active core (rank-nullity). Verified
  chi = sig - d on all 36 entries.
- **L9 (rigid => Maxwell):** d = 0 => m >= 3k+1. Corollary (with L4 planarity): the two N4
  filter forms hold for first-order-rigid realizations. Contrapositive, the census-usable
  EXACT statement: a structure with m < 3k+1 can NEVER be first-order rigid — the census
  splits exactly into RIGID-POSSIBLE (m >= 3k+1) and FLEX-ONLY branches; the split labels,
  it does not kill.
- **L9' (lambda0 = 0 branch):** needs a nonnegative self-stress, so m >= 3k+2-d; harder, not
  easier, to realize with few rows.
- **L10:** support flexes are s-neutral (why flexible minimisers are legitimate and
  first-order unkillable).
- **L11 (non-thin local counts):** non-thin => every loaded square has row-degree >= 3;
  with L6, 2E >= 3k+2 on the non-thin lambda0 > 0 branch — N4-L0 is a theorem there (A43
  already measured its marginal bite as ~0 beyond non-thinness; the money was always in the
  refuted L1 flush form).
- **Impossibility frame:** second-order FJ necessity admits configurations with independent
  rows (sig = 0), d >= 1 s-neutral flexes, blocked purely by geometric stiffness — legitimate
  isolated minimisers at m = 3k+1-d <= 3k. Hence NO unconditional bound below 3k+1 follows
  from first/second-order necessity; C* is genuinely geometric. C* refutation would need a
  critical point with sig <= d-2 (chi <= -2) — the atlas has never populated that layer;
  a targeted search there is the cheapest decisive follow-up.

Conjectures, labeled: **C\*** (m >= 3k; atlas-tight) and **C-rep** (every component of the
minimiser set contains a point with m >= 3k+1; not refuted by the atlas — drain endpoints are
arbitrary points on flat bottoms — but blocked by the loop-flex and curvature-blocked-flex
loopholes, A44-G1).

## 4. Measured census factors (A43-H1 re-run; results/census_report.md, census.json;
regression vs A43: 510/510 sampled rows exact, baseline and conditional k=11 numbers to 2e-16)

| column | soundness | k=11 (3 models) | kill |
|---|---|---|---|
| MAIN' baseline | EXACT | 2.30e29 / 1.51e30 / 1.09e30 | 1 |
| RIGID-POSSIBLE m>=3k+1 | EXACT split | 6.3e-4 of count | — |
| FLEX-ONLY m<3k+1 | EXACT split, carried | **99.94% of count** | x1.0006 |
| C-rep column (kill m<3k+1) | CONDITIONAL | 1.45e26 / 9.46e26 / 6.83e26 | **x1592** (x1.3e4-6.9e4 w/ non-thin) |
| C* column (kill m<3k) | CONDITIONAL | 6.51e26 / 4.26e27 / 3.07e27 | **x354** (x3.0e3-1.5e4 w/ non-thin) |
| chi = -1 slice (where valleys live) | EXACT slice | 2.2e-3 of flex branch | — |

Reading: (i) dropping from the refuted threshold to the atlas-consistent one costs x4.5
(retains 80% of the log-kill) — C* is still a three-orders instrument IF ever proved; (ii) the
chi profile mode is -4 at k = 7 and 99.8% of C*'s bite is at chi <= -2, exactly the layer no
known critical point inhabits and no FJ argument can exclude; (iii) the Maxwell columns are
near-disjoint from N3/THM3 (1.2% overlap — high row counts are bought with wall-flush edges,
which satisfy THM3 for free): NOT composable for a product; (iv) neither threshold rescues
enumerate-then-solve — A31/A43's NO-GO stands unconditionally.

## 5. Gap list

- **A44-G1:** C-rep unproven (loop flexes; curvature-blocked flexes). If proved, N4 returns in
  full for a max-contact-representative census.
- **A44-G2:** C* unproven and provably out of reach of the FJ+counting route; decisive
  experiment: hunt a critical point with chi <= -2 (sig <= d-2) — refute-or-strengthen.
- **A44-G3:** the refutation witnesses' criticality is [NUM] (A37 G-A37-3: taxonomy is float);
  fam 31's FJ LP residual is 6.9e-9 at the exact-rational z_center. Exact-algebraic hardening
  of fam 31 criticality is the upgrade path if the refutation is ever load-bearing.
- **A44-G4:** fams 27 / NEW-1 (VALLEY-MARGINAL) have infeasible lambda0 = 1 LPs at tolerance
  (consistent with A37-G-A37-2); their lambda0 = 0 branch untested; no verdict rests on them.
- **A44-G5:** census k=8..11 numbers are 3-stacked-fit extrapolations (A43-G2 inherited);
  conditional columns must never enter a certified count.
- **A44-G6:** row-counting convention judgment calls (eval_report.md section 6, all listed);
  the shadow (brief-literal) convention changes no verdict.
- **A44-G7:** SURVIVES-GENUINE = evidence, not proof: the atlas is not a certified-complete
  CP list (A37 itself found 4 missing families).

## 6. Files

notes/theory.md (L8-L11, impossibility frame, C*/C-rep, conventions), notes/verification_log.md,
code/eval_atlas.py + code/a44_geom.py, code/census/, results/eval_report.md +
candidates.json (atlas evaluation), results/census_report.md + census.json + census_l1.json
(census re-run), logs/.
