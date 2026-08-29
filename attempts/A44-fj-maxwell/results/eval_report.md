# A44 / eval_atlas — candidate Maxwell bounds vs the A37 CP atlas

Generated 2026-08-29T00:35:55.  Seed 20260829.  Runtime 1.5 s, single process.
Code: `attempts/A44-fj-maxwell/code/eval_atlas.py`, `code/a44_geom.py`.  Data: `results/candidates.json`, `logs/eval.log`.

Rigour tags: `[EXACT]` exact combinatorics on the certified contact table; `[NUM]` float64 SVD / HiGHS LP with the numerical cut recorded.

## 0. Verdict summary

| cand | statement | verdict (all 12 genuine) | min margin | refuting genuine entries | tight (margin 0) |
|---|---|---|---|---|---|
| B1 | m >= 3k+1 | **REFUTED-BY-GENUINE** | -1 | 27 (33<34), 31 (33<34) | A37-NEW-3 |
| B1' | m >= 3k | **SURVIVES-GENUINE** | 0 | — | 27, 31 |
| B1'' | m >= 3k-1 | **SURVIVES-GENUINE** | 1 | — | — |
| B2 | m_Hmax >= 3k+1   (m_H = Fact-0 rows over loadable edges) | **REFUTED-BY-GENUINE** | -34 | 1 (17<34), 2 (17<31), 27 (0<34) *vac*, 31 (33<34), A37-NEW-1 (0<31) *vac* | A37-NEW-3 |
| B2' | m_Hmax >= 3k | **REFUTED-BY-GENUINE** | -33 | 1 (17<33), 2 (17<30), 27 (0<33) *vac*, A37-NEW-1 (0<30) *vac* | 31 |
| B2H | m_Hmax >= 3*k_H+1   (Maxwell on the LOADED core only) | **REFUTED-BY-GENUINE** | -2 | 1 (17<19), 2 (17<19), 27 (0<1) *vac*, 31 (33<34), A37-NEW-1 (0<1) *vac* | A37-NEW-3 |
| B2H' | m_Hmax >= 3*k_H | **REFUTED-BY-GENUINE** | -1 | 1 (17<18), 2 (17<18) | 27, 31, A37-NEW-1 |
| B2-rows | #loadable rows >= 3k+1 | **REFUTED-BY-GENUINE** | -34 | 1 (17<34), 2 (17<31), 27 (0<34) *vac*, 31 (33<34), A37-NEW-1 (0<31) *vac* | A37-NEW-3 |
| B2-rows' | #loadable rows >= 3k | **REFUTED-BY-GENUINE** | -33 | 1 (17<33), 2 (17<30), 27 (0<33) *vac*, A37-NEW-1 (0<30) *vac* | 31 |
| B2m | min-support-found size >= 3k+1 | **REFUTED-BY-GENUINE** | -34 | 0 (30<34), 1 (13<34), 2 (13<31), 6 (18<34), 13 (24<31), 14 (24<31), 27 (0<34) *vac*, 31 (27<34), A37-NEW-0 (25<31), A37-NEW-1 (0<31) *vac*, A37-NEW-2 (23<31), A37-NEW-3 (26<34) | — |
| B2m' | min-support-found size >= 3k | **REFUTED-BY-GENUINE** | -33 | 0 (30<33), 1 (13<33), 2 (13<30), 6 (18<33), 13 (24<30), 14 (24<30), 27 (0<33) *vac*, 31 (27<33), A37-NEW-0 (25<30), A37-NEW-1 (0<30) *vac*, A37-NEW-2 (23<30), A37-NEW-3 (26<33) | — |
| B2m-kH | min-support-found size >= 3*k_supp+1 | **REFUTED-BY-GENUINE** | -8 | 0 (30<34), 1 (13<19), 2 (13<19), 6 (18<25), 13 (24<31), 14 (24<31), 27 (0<1) *vac*, 31 (27<34), A37-NEW-0 (25<31), A37-NEW-1 (0<1) *vac*, A37-NEW-2 (23<31), A37-NEW-3 (26<34) | — |
| B2m-kH' | min-support-found size >= 3*k_supp | **REFUTED-BY-GENUINE** | -7 | 0 (30<33), 1 (13<18), 2 (13<18), 6 (18<24), 13 (24<30), 14 (24<30), 31 (27<33), A37-NEW-0 (25<30), A37-NEW-2 (23<30), A37-NEW-3 (26<33) | 27, A37-NEW-1 |
| B3 | 2E >= 3k+1   (census N4-L0) | **SURVIVES-GENUINE** | 8 | — | — |
| B3H | 2*E_H >= 3*k_H+1   (N4-L0 on the loaded core) | **REFUTED-BY-GENUINE** | -1 | 27 (0<1) *vac*, A37-NEW-1 (0<1) *vac* | — |
| B4 | F >= 3k+1-E   (census N4-L1) | **REFUTED-BY-GENUINE** | -1 | 27 (12<13), 31 (12<13) | A37-NEW-3 |
| B4' | F >= 3k-E | **SURVIVES-GENUINE** | 0 | — | 27, 31 |
| B4H | F_H >= 3*k_H+1-E_H   (N4-L1 on the loaded core) | **REFUTED-BY-GENUINE** | -2 | 1 (7<9), 2 (7<9), 27 (0<1) *vac*, 31 (12<13), A37-NEW-1 (0<1) *vac* | A37-NEW-3 |
| B5 | every core square has row degree >= 3 | **REFUTED-BY-GENUINE** | -2 | 1 (1<3), 2 (1<3), A37-NEW-1 (2<3), A37-NEW-2 (2<3) | 6, 13, 14, 27, 31 |
| B5' | every core square with a loadable row has >= 2 loadable edges (L1 CANARY) | **SURVIVES-GENUINE** | 0 | — | 1, 2, 6, 13, 14, 31, A37-NEW-0, A37-NEW-2, A37-NEW-3 |
| B6 | F >= 1 | **SURVIVES-GENUINE** | 11 | — | — |
| B6' | F_pair >= 1 | **SURVIVES-GENUINE** | 2 | — | — |
| B7 | rank_num >= 3k+1  (isostaticity) | **REFUTED-BY-GENUINE** | -5 | 1 (30<34), 2 (28<31), 6 (32<34), 13 (28<31), 14 (28<31), 27 (29<34), 31 (30<34), A37-NEW-0 (29<31), A37-NEW-1 (27<31), A37-NEW-2 (27<31), A37-NEW-3 (30<34) | 0 |

Genuine = class RIGID / VALLEY / VALLEY-MARGINAL (12 entries: 0, 1, 2, 6, 13, 14, 27, 31, A37-NEW-0..3).  NOT-CP entries cannot refute an FJ-conditional bound (they are not FJ-critical under free rotation) — their failures are listed informative-only in the JSON.

`*vac*` marks a **vacuous** failure: at the two VALLEY-MARGINAL entries (27, A37-NEW-1) the λ₀ = 1 FJ system is itself infeasible (A44 reproduces A37's own `kkt.lp_all_rows = false` there), so the loadable-row set is empty and every H- or support-based LHS is 0 by definition.  Those are not refutations.  The table below re-runs the H/support candidates over only the **10 genuine entries where the λ₀ = 1 FJ system is feasible** (0, 1, 2, 6, 13, 14, 31, A37-NEW-0, A37-NEW-2, A37-NEW-3):

| cand | verdict (10 FJ-feasible genuine) | min margin | refuting entries | tight |
|---|---|---|---|---|
| B2 | **REFUTED-BY-GENUINE** | -17 | 1 (17<34), 2 (17<31), 31 (33<34) | A37-NEW-3 |
| B2' | **REFUTED-BY-GENUINE** | -16 | 1 (17<33), 2 (17<30) | 31 |
| B2H | **REFUTED-BY-GENUINE** | -2 | 1 (17<19), 2 (17<19), 31 (33<34) | A37-NEW-3 |
| B2H' | **REFUTED-BY-GENUINE** | -1 | 1 (17<18), 2 (17<18) | 31 |
| B2-rows | **REFUTED-BY-GENUINE** | -17 | 1 (17<34), 2 (17<31), 31 (33<34) | A37-NEW-3 |
| B2-rows' | **REFUTED-BY-GENUINE** | -16 | 1 (17<33), 2 (17<30) | 31 |
| B2m | **REFUTED-BY-GENUINE** | -21 | 0 (30<34), 1 (13<34), 2 (13<31), 6 (18<34), 13 (24<31), 14 (24<31), 31 (27<34), A37-NEW-0 (25<31), A37-NEW-2 (23<31), A37-NEW-3 (26<34) | — |
| B2m' | **REFUTED-BY-GENUINE** | -20 | 0 (30<33), 1 (13<33), 2 (13<30), 6 (18<33), 13 (24<30), 14 (24<30), 31 (27<33), A37-NEW-0 (25<30), A37-NEW-2 (23<30), A37-NEW-3 (26<33) | — |
| B2m-kH | **REFUTED-BY-GENUINE** | -8 | 0 (30<34), 1 (13<19), 2 (13<19), 6 (18<25), 13 (24<31), 14 (24<31), 31 (27<34), A37-NEW-0 (25<31), A37-NEW-2 (23<31), A37-NEW-3 (26<34) | — |
| B2m-kH' | **REFUTED-BY-GENUINE** | -7 | 0 (30<33), 1 (13<18), 2 (13<18), 6 (18<24), 13 (24<30), 14 (24<30), 31 (27<33), A37-NEW-0 (25<30), A37-NEW-2 (23<30), A37-NEW-3 (26<33) | — |
| B3H | **SURVIVES-GENUINE** | 1 | — | — |
| B4H | **REFUTED-BY-GENUINE** | -2 | 1 (7<9), 2 (7<9), 31 (12<13) | A37-NEW-3 |
| B5' | **SURVIVES-GENUINE** | 0 | — | 1, 2, 6, 13, 14, 31, A37-NEW-0, A37-NEW-2, A37-NEW-3 |

### Headline

- **B1 (`m >= 3k+1`, the naive Maxwell bound) is REFUTED.**  Family **31** (VALLEY, s = 3.936964) has k = 11 loaded squares, 21 contact edges, **m = 33 = 3k** rows — one short — and its λ₀ = 1 FJ system is feasible with **every one of its 21 edges loadable and all 11 squares loaded** (k_H = 11, E_H = 21, m_H = 33).  There is no rattler to blame and no convention that rescues it: under the brief's literal CORNER-CORNER = 1 convention family 31 has no corner-corner contact at all, so the count is identical.  Family **27** (VALLEY-MARGINAL, m = 33, k = 11) refutes it a second time, and A37-NEW-3 sits exactly on the boundary (m = 34 = 3k+1).
  *Robustness of the B1 refutation.*  It is combinatorial — it depends only on the contact table, not on any LP or SVD.  At family 31 every kept row evaluates to |g| < 2.8e-16 at `z_center`, and the nearest NON-contact is a pair gap of 6.48e-03 and a corner-wall clearance of 7.34e-02 — five orders of magnitude above any plausible error in the critical point, so no additional contact can appear and m cannot rise above 33.  Same picture at 27 (1.51e-02 / 8.71e-02).
- **B1' (`m >= 3k`) survives all 12 genuine entries with margin 0** at families 27 and 31.  It is the strongest surviving total-row bound and it is *tight*: two independent genuine critical points sit exactly on it.
- **B4 (`F >= 3k+1-E`) is refuted by the same two entries**; `B4' (F >= 3k-E)` survives, tight at 27 and 31.  (B4/B4' and B1/B1' are the same inequality rewritten: `m = E + F`.)
- **B7 (isostaticity, `rank >= 3k+1`) is refuted by 11 of the 12 genuine entries** — every non-Trump one.  Only family 0 (Trump, the unique RIGID entry) attains rank 34 = 3k+1.  This confirms the A37 valley finding: naive isostaticity is false at genuine critical points.
- **B5 (`row degree >= 3` at every core square) is refuted** by families 1, 2 (a core square with a SINGLE incident row), A37-NEW-1 and A37-NEW-2 (degree 2).  Cause: A37's rattler test is "no row touches this square at all", so a square with one or two contacts but zero load stays in the core.  Any degree bound must be stated on the **loaded** core, not on the contact core.
- **B5' (L1, `>= 2 loadable edges at every loaded square`) PASSES everywhere** — the canary is green on all 36 entries, tight (exactly 2) at 9 of the 10 FJ-feasible genuine entries.
- **The loaded-core Maxwell bound B2H (`m_H >= 3*k_H+1`) is also refuted** — families 1 and 2 have a 6-square loaded core carrying 10 edges and only 17 rows against 3·6+1 = 19, and family 31 fails at 33 vs 34.  Restricting to the loaded core does **not** repair the Maxwell count.  `B2H' (m_H >= 3*k_H)` also fails (1, 2: 17 < 18).
- **Survivors over all 12 genuine entries:** `B1'`, `B1''`, `B3`, `B4'`, `B5'`, `B6`, `B6'`.
- **Additional survivors once the 2 VALLEY-MARGINAL entries are excluded** (λ₀ = 1 FJ infeasible there, so the H/support LHS is vacuously 0): `B3H`.

## 1. Per-entry structural table  `[EXACT]` counts, `[NUM]` rank

| fam | class | s_min | k | E | E_p | E_w | F | F_p | F_w | m | N=3k+1 | chi | rank_num | rank_atlas | s_stress | d_flex | m_H | E_H | F_H | k_H | supp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | RIGID | 3.877084 | 11 | 25 | 14 | 11 | 16 | 7 | 9 | 41 | 34 | +7 | 34 | 34 | 7 | 0 | 41 | 25 | 16 | 11 | 30 |
| 1 | VALLEY | 3.885618 | 11 | 23 | 13 | 10 | 15 | 7 | 8 | 38 | 34 | +4 | 30 | 30 | 8 | 4 | 17 | 10 | 7 | 6 | 13 |
| 2 | VALLEY | 3.885618 | 10 | 21 | 12 | 9 | 15 | 7 | 8 | 36 | 31 | +5 | 28 | 28 | 8 | 3 | 17 | 10 | 7 | 6 | 13 |
| 3 | NOT-CP | 3.885903 | 6 | 10 | 5 | 5 | 6 | 2 | 4 | 16 | 19 | -3 | 14 | 14 | 2 | 5 | 0 | 0 | 0 | 0 | 0 |
| 4 | NOT-CP | 3.885983 | 6 | 10 | 5 | 5 | 7 | 2 | 5 | 17 | 19 | -2 | 15 | 15 | 2 | 4 | 0 | 0 | 0 | 0 | 0 |
| 5 | NOT-CP | 3.886196 | 10 | 15 | 10 | 5 | 8 | 3 | 5 | 23 | 31 | -8 | 20 | 20 | 3 | 11 | 0 | 0 | 0 | 0 | 0 |
| 6 | VALLEY | 3.886746 | 11 | 24 | 13 | 11 | 17 | 7 | 10 | 41 | 34 | +7 | 32 | 32 | 9 | 2 | 41 | 24 | 17 | 11 | 18 |
| 7 | NOT-CP | 3.886832 | 11 | 24 | 13 | 11 | 14 | 6 | 8 | 38 | 34 | +4 | 32 | 32 | 6 | 2 | 0 | 0 | 0 | 0 | 0 |
| 8 | NOT-CP | 3.887045 | 10 | 20 | 12 | 8 | 14 | 7 | 7 | 34 | 31 | +3 | 27 | 27 | 7 | 4 | 0 | 0 | 0 | 0 | 0 |
| 9 | NOT-CP | 3.887416 | 11 | 17 | 9 | 8 | 10 | 5 | 5 | 27 | 34 | -7 | 23 | 23 | 4 | 11 | 0 | 0 | 0 | 0 | 0 |
| 10 | NOT-CP | 3.887935 | 7 | 12 | 6 | 6 | 6 | 2 | 4 | 18 | 22 | -4 | 16 | 16 | 2 | 6 | 0 | 0 | 0 | 0 | 0 |
| 11 | NOT-CP | 3.888014 | 11 | 18 | 11 | 7 | 10 | 5 | 5 | 28 | 34 | -6 | 24 | 24 | 4 | 10 | 0 | 0 | 0 | 0 | 0 |
| 12 | NOT-CP | 3.891406 | 11 | 23 | 12 | 11 | 15 | 6 | 9 | 38 | 34 | +4 | 32 | 32 | 6 | 2 | 0 | 0 | 0 | 0 | 0 |
| 13 | VALLEY | 3.897231 | 10 | 20 | 11 | 9 | 13 | 7 | 6 | 33 | 31 | +2 | 28 | 28 | 5 | 3 | 33 | 20 | 13 | 10 | 24 |
| 14 | VALLEY | 3.897462 | 10 | 20 | 11 | 9 | 13 | 7 | 6 | 33 | 31 | +2 | 28 | 28 | 5 | 3 | 33 | 20 | 13 | 10 | 24 |
| 15 | NOT-CP | 3.897629 | 10 | 19 | 10 | 9 | 11 | 4 | 7 | 30 | 31 | -1 | 26 | 26 | 4 | 5 | 0 | 0 | 0 | 0 | 0 |
| 16 | NOT-CP | 3.897775 | 10 | 20 | 11 | 9 | 11 | 4 | 7 | 31 | 31 | +0 | 27 | 27 | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| 17 | NOT-CP | 3.898253 | 10 | 20 | 11 | 9 | 12 | 5 | 7 | 32 | 31 | +1 | 27 | 27 | 5 | 4 | 0 | 0 | 0 | 0 | 0 |
| 18 | NOT-CP | 3.902689 | 10 | 19 | 10 | 9 | 9 | 5 | 4 | 28 | 31 | -3 | 25 | 25 | 3 | 6 | 0 | 0 | 0 | 0 | 0 |
| 19 | NOT-CP | 3.903006 | 10 | 22 | 13 | 9 | 12 | 4 | 8 | 34 | 31 | +3 | 28 | 28 | 6 | 3 | 0 | 0 | 0 | 0 | 0 |
| 20 | NOT-CP | 3.903040 | 10 | 22 | 13 | 9 | 12 | 4 | 8 | 34 | 31 | +3 | 28 | 28 | 6 | 3 | 0 | 0 | 0 | 0 | 0 |
| 21 | NOT-CP | 3.903079 | 10 | 22 | 13 | 9 | 12 | 4 | 8 | 34 | 31 | +3 | 28 | 28 | 6 | 3 | 0 | 0 | 0 | 0 | 0 |
| 22 | NOT-CP | 3.903098 | 10 | 22 | 13 | 9 | 12 | 4 | 8 | 34 | 31 | +3 | 28 | 28 | 6 | 3 | 0 | 0 | 0 | 0 | 0 |
| 23 | NOT-CP | 3.903159 | 10 | 22 | 13 | 9 | 12 | 4 | 8 | 34 | 31 | +3 | 28 | 28 | 6 | 3 | 0 | 0 | 0 | 0 | 0 |
| 24 | NOT-CP | 3.903232 | 10 | 22 | 13 | 9 | 12 | 4 | 8 | 34 | 31 | +3 | 28 | 28 | 6 | 3 | 0 | 0 | 0 | 0 | 0 |
| 25 | NOT-CP | 3.912522 | 10 | 20 | 11 | 9 | 12 | 3 | 9 | 32 | 31 | +1 | 26 | 26 | 6 | 5 | 0 | 0 | 0 | 0 | 0 |
| 26 | NOT-CP | 3.912658 | 10 | 20 | 11 | 9 | 12 | 3 | 9 | 32 | 31 | +1 | 26 | 26 | 6 | 5 | 0 | 0 | 0 | 0 | 0 |
| 27 | VALLEY-MARGINAL | 3.925149 | 11 | 21 | 11 | 10 | 12 | 3 | 9 | 33 | 34 | -1 | 29 | 29 | 4 | 5 | 0 | 0 | 0 | 0 | 0 |
| 28 | NOT-CP | 3.925199 | 10 | 20 | 11 | 9 | 11 | 4 | 7 | 31 | 31 | +0 | 26 | 26 | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| 29 | NOT-CP | 3.925527 | 10 | 19 | 10 | 9 | 11 | 3 | 8 | 30 | 31 | -1 | 26 | 26 | 4 | 5 | 0 | 0 | 0 | 0 | 0 |
| 30 | NOT-CP | 3.926293 | 11 | 21 | 11 | 10 | 12 | 3 | 9 | 33 | 34 | -1 | 29 | 29 | 4 | 5 | 0 | 0 | 0 | 0 | 0 |
| 31 | VALLEY | 3.936964 | 11 | 21 | 11 | 10 | 12 | 4 | 8 | 33 | 34 | -1 | 30 | 30 | 3 | 4 | 33 | 21 | 12 | 11 | 27 |
| A37-NEW-0 | VALLEY | 3.902674 | 10 | 23 | 14 | 9 | 12 | 4 | 8 | 35 | 31 | +4 | 29 | 29 | 6 | 2 | 35 | 23 | 12 | 10 | 25 |
| A37-NEW-1 | VALLEY-MARGINAL | 3.912232 | 10 | 21 | 12 | 9 | 12 | 3 | 9 | 33 | 31 | +2 | 27 | 27 | 6 | 4 | 0 | 0 | 0 | 0 | 0 |
| A37-NEW-2 | VALLEY | 3.924402 | 10 | 20 | 11 | 9 | 12 | 5 | 7 | 32 | 31 | +1 | 27 | 27 | 5 | 4 | 32 | 20 | 12 | 10 | 23 |
| A37-NEW-3 | VALLEY | 3.925470 | 11 | 21 | 11 | 10 | 13 | 4 | 9 | 34 | 34 | +0 | 30 | 30 | 4 | 4 | 34 | 21 | 13 | 11 | 26 |

`chi = m - N = s_stress - d_flex` verified on every entry: all OK.

### rank_num vs the atlas `rank` field

They measure different things and are NOT expected to agree.  The atlas `rank` is the rank of A37's FULL row list — all wall rows, **every rowspec of every tied separating axis** (including the [V]-unsafe ones), **and the aux `dist` rows** — over all **34** coordinates including the rattler squares'.  A44's `rank_num` is the rank of the **Fact-0 physical** row set (one row per contact point, no aux, rattler-incident contacts dropped) over the **3k+1** core coordinates.  Per-entry both numbers are in the table; the rank of the A44 tie-expanded row set over the core columns is in the JSON as `rank_expanded_rowset`.

**Result: `rank_num == rank_atlas` on all 36 entries** — despite the two very different row sets and column sets.  That is a strong independent confirmation that (i) the tie-alternative rows and the aux `dist` rows add nothing to the rank, and (ii) the rattler coordinates are genuinely free.  The rank is numerically unambiguous everywhere: the smallest ratio sigma_min_kept / sigma_max_dropped over the 36 entries is 7.8e+13, and the rank is identical at cuts 1e-11, 1e-9 and 1e-7 on every entry.

| fam | rank_num (physical, 3k+1 cols) | rank(expanded rows, 3k+1 cols) | rank_atlas (all rows, 34 cols) | sigma_min kept | sigma_max dropped |
|---|---|---|---|---|---|
| 0 | 34 | 34 | 34 | 1.275e-01 | 0.000e+00 |
| 1 | 30 | 30 | 30 | 1.103e-01 | 2.427e-16 |
| 2 | 28 | 28 | 28 | 1.129e-01 | 2.077e-16 |
| 3 | 14 | 14 | 14 | 3.002e-01 | 1.962e-16 |
| 4 | 15 | 15 | 15 | 2.991e-01 | 2.257e-16 |
| 5 | 20 | 20 | 20 | 3.372e-01 | 2.441e-16 |
| 6 | 32 | 32 | 32 | 1.462e-01 | 9.008e-17 |
| 7 | 32 | 32 | 32 | 1.932e-02 | 2.482e-16 |
| 8 | 27 | 27 | 27 | 2.565e-01 | 2.739e-16 |
| 9 | 23 | 23 | 23 | 2.544e-01 | 3.207e-16 |
| 10 | 16 | 16 | 16 | 4.111e-01 | 3.835e-16 |
| 11 | 24 | 24 | 24 | 3.152e-01 | 2.416e-16 |
| 12 | 32 | 32 | 32 | 3.718e-02 | 2.658e-16 |
| 13 | 28 | 28 | 28 | 9.864e-02 | 2.971e-16 |
| 14 | 28 | 28 | 28 | 9.902e-02 | 2.405e-16 |
| 15 | 26 | 26 | 26 | 1.169e-01 | 2.784e-16 |
| 16 | 27 | 27 | 27 | 1.271e-01 | 2.692e-16 |
| 17 | 27 | 27 | 27 | 1.256e-01 | 2.575e-16 |
| 18 | 25 | 25 | 25 | 1.455e-01 | 2.615e-16 |
| 19 | 28 | 28 | 28 | 2.032e-01 | 1.517e-16 |
| 20 | 28 | 28 | 28 | 2.047e-01 | 2.600e-16 |
| 21 | 28 | 28 | 28 | 2.036e-01 | 1.882e-16 |
| 22 | 28 | 28 | 28 | 2.051e-01 | 3.493e-16 |
| 23 | 28 | 28 | 28 | 2.035e-01 | 1.906e-16 |
| 24 | 28 | 28 | 28 | 2.081e-01 | 1.961e-16 |
| 25 | 26 | 26 | 26 | 2.207e-01 | 2.632e-16 |
| 26 | 26 | 26 | 26 | 2.133e-01 | 2.579e-16 |
| 27 | 29 | 29 | 29 | 2.909e-01 | 2.567e-16 |
| 28 | 26 | 26 | 26 | 1.794e-01 | 3.193e-16 |
| 29 | 26 | 26 | 26 | 1.945e-01 | 2.721e-16 |
| 30 | 29 | 29 | 29 | 2.784e-01 | 1.960e-16 |
| 31 | 30 | 30 | 30 | 2.355e-01 | 3.910e-16 |
| A37-NEW-0 | 29 | 29 | 29 | 1.975e-01 | 1.755e-16 |
| A37-NEW-1 | 27 | 27 | 27 | 2.214e-01 | 3.112e-16 |
| A37-NEW-2 | 27 | 27 | 27 | 1.437e-01 | 3.082e-16 |
| A37-NEW-3 | 30 | 30 | 30 | 2.621e-01 | 1.889e-16 |

## 2. Contact-completeness audit  `[NUM]`

At every entry's `z_center` all 55 pair SAT gaps and all 176 corner-wall clearances were recomputed from scratch.  Listed below: every gap < 1e-3 that is NOT in the atlas contact table.  (A missed contact could only RAISE m, so these are the borderline cases the theory lead must judge before trusting a refutation.)

**2** (VALLEY): min non-contact pair gap 1.265e-03, min non-contact wall gap 6.854e-05
  - wall sq 2 corner 3 x=0 gap 2.235e-04
  - wall sq 7 corner 0 y=0 gap 6.854e-05
**3** (NOT-CP): min non-contact pair gap 6.791e-07, min non-contact wall gap 1.589e-07
  - pair (0,4) gap 3.203e-04
  - pair (0,10) gap 6.262e-06
  - pair (3,5) gap 7.079e-06
  - pair (9,10) gap 6.791e-07
  - wall sq 1 corner 3 y=0 gap 1.589e-07
  - wall sq 9 corner 0 y=0 gap 1.677e-05
  - wall sq 9 corner 2 x=0 gap 1.991e-04
  - wall sq 9 corner 3 x=0 gap 7.332e-05
  - wall sq 9 corner 3 y=0 gap 1.426e-04
  - wall sq 10 corner 2 x=0 gap 3.780e-04
  - wall sq 10 corner 3 x=0 gap 2.612e-04
**4** (NOT-CP): min non-contact pair gap 1.998e-06, min non-contact wall gap 4.846e-06
  - pair (0,4) gap 6.941e-05
  - pair (0,10) gap 3.329e-05
  - pair (1,5) gap 3.078e-05
  - pair (1,7) gap 2.619e-05
  - pair (6,10) gap 1.998e-06
  - wall sq 4 corner 1 x=s gap 9.527e-04
  - wall sq 6 corner 0 x=0 gap 2.362e-04
  - wall sq 6 corner 0 y=0 gap 1.272e-04
  - wall sq 6 corner 1 y=0 gap 3.586e-04
  - wall sq 6 corner 3 x=0 gap 4.846e-06
  - wall sq 10 corner 0 y=0 gap 8.452e-06
  - wall sq 10 corner 1 y=0 gap 2.264e-04
**5** (NOT-CP): min non-contact pair gap 1.577e-05, min non-contact wall gap 5.879e-06
  - pair (5,8) gap 7.107e-04
  - pair (7,8) gap 1.577e-05
  - wall sq 2 corner 3 x=0 gap 5.879e-06
  - wall sq 7 corner 0 y=0 gap 1.092e-04
  - wall sq 7 corner 1 y=0 gap 1.866e-04
  - wall sq 8 corner 0 y=0 gap 3.454e-04
  - wall sq 8 corner 1 y=0 gap 5.691e-04
**8** (NOT-CP): min non-contact pair gap 3.442e-03, min non-contact wall gap 3.291e-04
  - wall sq 0 corner 0 x=s gap 3.438e-04
  - wall sq 0 corner 1 x=s gap 3.438e-04
  - wall sq 7 corner 0 y=0 gap 3.291e-04
  - wall sq 7 corner 1 y=0 gap 4.756e-04
**9** (NOT-CP): min non-contact pair gap 1.055e-05, min non-contact wall gap 4.605e-04
  - pair (0,4) gap 5.661e-05
  - pair (1,2) gap 1.943e-05
  - pair (2,6) gap 1.920e-05
  - pair (4,9) gap 1.055e-05
  - wall sq 0 corner 0 x=0 gap 4.605e-04
**10** (NOT-CP): min non-contact pair gap 6.602e-06, min non-contact wall gap 4.216e-06
  - pair (1,7) gap 4.477e-05
  - pair (1,8) gap 6.602e-06
  - pair (2,5) gap 4.223e-05
  - pair (2,8) gap 1.161e-05
  - pair (4,5) gap 2.361e-04
  - pair (6,7) gap 7.356e-06
  - wall sq 4 corner 0 x=s gap 3.890e-04
  - wall sq 4 corner 1 x=s gap 1.904e-04
  - wall sq 5 corner 2 y=s gap 1.150e-04
  - wall sq 5 corner 3 y=s gap 1.455e-04
  - wall sq 6 corner 0 x=s gap 2.942e-05
  - wall sq 6 corner 1 x=s gap 2.521e-05
  - wall sq 6 corner 3 y=0 gap 4.216e-06
  - wall sq 7 corner 0 y=0 gap 3.767e-04
  - wall sq 7 corner 1 y=0 gap 4.837e-04
  - wall sq 8 corner 3 x=0 gap 1.170e-05
**11** (NOT-CP): min non-contact pair gap 4.668e-03, min non-contact wall gap 5.200e-04
  - wall sq 0 corner 2 y=s gap 8.059e-04
  - wall sq 2 corner 1 x=s gap 6.883e-04
  - wall sq 10 corner 2 x=0 gap 9.442e-04
  - wall sq 10 corner 3 x=0 gap 5.200e-04
**13** (VALLEY): min non-contact pair gap 2.697e-03, min non-contact wall gap 5.618e-04
  - wall sq 1 corner 3 x=0 gap 5.618e-04
**15** (NOT-CP): min non-contact pair gap 3.430e-06, min non-contact wall gap 4.069e-04
  - pair (1,10) gap 3.430e-06
  - wall sq 8 corner 0 y=0 gap 4.069e-04
**16** (NOT-CP): min non-contact pair gap 5.672e-04, min non-contact wall gap 1.719e-04
  - pair (5,9) gap 5.672e-04
  - wall sq 9 corner 0 x=0 gap 3.449e-04
  - wall sq 9 corner 3 x=0 gap 1.719e-04
**18** (NOT-CP): min non-contact pair gap 1.804e-07, min non-contact wall gap 2.463e-07
  - pair (0,1) gap 1.804e-07
  - pair (1,5) gap 1.121e-04
  - wall sq 3 corner 2 x=0 gap 2.463e-07
  - wall sq 3 corner 3 y=0 gap 2.463e-07
**19** (NOT-CP): min non-contact pair gap 8.271e-04, min non-contact wall gap 5.705e-02
  - pair (1,2) gap 8.271e-04
**25** (NOT-CP): min non-contact pair gap 1.102e-03, min non-contact wall gap 6.291e-04
  - wall sq 10 corner 3 x=0 gap 6.291e-04
**26** (NOT-CP): min non-contact pair gap 5.030e-05, min non-contact wall gap 1.114e-06
  - pair (2,7) gap 5.030e-05
  - wall sq 7 corner 3 x=0 gap 1.114e-06
**28** (NOT-CP): min non-contact pair gap 3.604e-04, min non-contact wall gap 7.080e-03
  - pair (2,8) gap 3.604e-04
**29** (NOT-CP): min non-contact pair gap 8.026e-03, min non-contact wall gap 9.309e-04
  - wall sq 3 corner 0 y=0 gap 9.309e-04
**A37-NEW-1** (VALLEY-MARGINAL): min non-contact pair gap 4.943e-04, min non-contact wall gap 4.736e-03
  - pair (5,10) gap 4.943e-04

## 3. FJ multiplier diagnostics  `[NUM]`

| fam | rowset used | feasible | ||A^T λ − e_s||_inf | Σλ | Σλ far-wall | #loadable | #forced | min-support found | support edges |
|---|---|---|---|---|---|---|---|---|---|
| 0 | physical | yes | 3.89e-16 | 4.5188 | 1.000000 | 41 | 21 | 30 | 23 |
| 1 | physical | yes | 3.33e-16 | 4.5523 | 1.000000 | 17 | 9 | 13 | 10 |
| 2 | physical | yes | 1.11e-16 | 4.5523 | 1.000000 | 17 | 9 | 13 | 10 |
| 3 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 4 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 5 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 6 | physical | yes | 1.11e-16 | 4.5583 | 1.000000 | 40 | 10 | 18 | 15 |
| 7 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 8 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 9 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 10 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 11 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 12 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 13 | physical | yes | 2.22e-16 | 4.5760 | 1.000000 | 33 | 17 | 24 | 19 |
| 14 | physical | yes | 8.33e-17 | 4.5760 | 1.000000 | 33 | 17 | 24 | 19 |
| 15 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 16 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 17 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 18 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 19 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 20 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 21 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 22 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 23 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 24 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 25 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 26 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 27 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 28 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 29 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 30 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| 31 | physical | yes | 6.87e-09 | 4.5517 | 1.000000 | 33 | 23 | 27 | 21 |
| A37-NEW-0 | physical | yes | 1.41e-08 | 4.5741 | 1.000000 | 34 | 18 | 25 | 21 |
| A37-NEW-1 | physical | NO | nan | nan | nan | 0 | 0 | 0 | 0 |
| A37-NEW-2 | physical | yes | 2.24e-12 | 4.6038 | 1.000000 | 32 | 18 | 23 | 19 |
| A37-NEW-3 | physical | yes | 1.36e-10 | 4.5509 | 1.000000 | 34 | 20 | 26 | 21 |

`Σλ far-wall = 1` on every feasible entry is the built-in check that the LP really solved `A^T λ = e_s` (only the `x=s` / `y=s` rows carry a ∂s coefficient, and it is +1).

**Independent cross-check against the atlas.**  A44's λ₀ = 1 feasibility verdict on the Fact-0 physical row set agrees with A37's own `kkt.lp_all_rows` field on **36 of 36** entries.  In particular the 10 RIGID/VALLEY entries are feasible, and the 2 VALLEY-MARGINAL entries (27, A37-NEW-1) plus all 24 NOT-CP entries are infeasible — so "VALLEY-MARGINAL" is precisely "λ₀ = 1 FJ infeasible, λ₀ = 0 branch only".  This is a genuine independent reproduction: A37 solved over its full 34-column row list, A44 over the physical rows in the 3k+1 core columns.

The physical row set was feasible directly on all 10; the tie-expanded row set (every tied separating axis as a separate row) was never needed.  Note A37's `lp_safe_rows` is false at 1, 2, 6 and A37-NEW-2 — the [V]-safe rows alone do not carry e_s there, but the Fact-0 physical rows (which include the [V]-unsafe endpoint rows at coincident-corner contacts) do.

### Rattler / dropped-contact alarm

36 rattler squares are declared across the 36 entries.  **The total number of dropped contacts is 0** — 0 of 36 entries have any contact incident to a declared rattler.  This is by construction: A37's rattler test (`classify()`) is "no row touches this square's coordinates at all", so a rattler square carries no wall contact, no pair contact and no aux row.  The alarm condition ("a dropped contact carries a positive multiplier") is therefore vacuous, and the check was run anyway and reported nothing.

**Consequence worth flagging to the theory lead:** because A37's rattler set is the *zero-contact* set and not the *zero-load* set, the "core" of an atlas entry can still contain squares that carry contacts but no load.  Families 1 and 2 each have a core square with a single incident row (squares 10 and 7 respectively) — a rattler with one incidental touch.  That is what kills B5, and it means any per-square degree hypothesis must be stated over the **loaded** core (the k_H column), not over the contact core.

**No alarms of any kind fired on any of the 36 entries.**

## 4. Trump reconciliation (family 0)

A44 physical (Fact 0) count at Trump: **k = 11, E = 25 (E_pair 14 + E_wall 11), F = 16 (F_pair 7 + F_wall 9), m = 41 (m_pair 21 + m_wall 20)**, N = 34, chi = +7.

| basis | rows | rank | self-stress | itemisation |
|---|---|---|---|---|
| A22 v1 | 38 | 34 | 4 | 20 wall rows + 16 pair sep rows (12 pair contacts) + 2 `dist` centre-distance surrogate rows |
| A35 v2 | 42 | 34 | 8 | A22 rows 0..35 (20 wall + 16 sep) + 4 flush rows for the two centre-distance-1 contacts + 2 corner-corner tie-alternative rows for (1,3); the 2 `dist` rows dropped |
| **A44 physical** | **41** | 34 | 7 | 20 wall rows (11 wall edges, 9 of them 2-corner flush) + 19 pair rows (14 pair edges: 7 segment contacts x 2 rows + 7 point contacts x 1 row) |

The A44 physical row set decomposes as

| block | rows | content |
|---|---|---|
| W | 20 | 11 wall edges: 9 two-corner (wall-flush) + 2 one-corner |
| S | 16 | the 11 "ordinary" pair contacts: 5 segment x 2 rows + 6 point x 1 row |
| C | 4 | the 2 coincident-corner segment contacts (A37 labels them CORNER-CORNER, n_axes_tied = 2; centre distance exactly 1; A35/M1b calls them flush) — 2 endpoint rows each |
| X | 1 | the (1,3) genuine corner-to-corner POINT contact (n_axes_tied = 4, 8 rowspecs, all at one point) — 1 selected branch |
| **total** | **41** | |

Row-by-row reconciliation (all three bases share the same W and S blocks — 36 rows — which are A22 `krawczyk_cert.json` constraints 0..35 verbatim):

```
A44 physical   = W(20) + S(16) + C(4) + X(1)                  = 41
A35 v2         = W(20) + S(16) + C(4) + X(2)                  = 42
                 (v2 rows 36-39 = C; rows 40,41 = BOTH (1,3) branches)
A22 v1         = W(20) + S(16) +   0  +  0  + dist(2)         = 38
                 (C replaced by the 2 centre-distance surrogates
                  D0-1, D0-3; the (1,3) contact missed entirely)
```

- **A44 → A35 v2: +1 row.**  v2 keeps *both* corner-corner branches of the (1,3) point contact; A44 keeps one (Fact 0: a point contact is one row).  The extra row is an *alternative selection at the same contact point*, not an extra contact — which is exactly why v2's self-stress dimension is 8 = 42 − 34 while A44's is 7 = 41 − 34 and the rank is 34 in both.
- **A44 → A22 v1: −3 rows.**  v1 drops all 4 C rows (−4), misses the (1,3) contact entirely (−1), and adds 2 `dist` centre-distance surrogate rows (+2): 41 − 4 − 1 + 2 = 38.  Its self-stress dimension 4 = 38 − 34 follows.  A35/M1b confirmed both defects in exact rational arithmetic (SAT gap at (1,3) is 0 within ±4.7e-61; centre distance² at the two C contacts is exactly 1).

So the three counts differ **only** in (i) tie-alternative rows at the corner-corner contact and (ii) `dist` surrogate rows standing in for real segment-contact rows — no discrepancy in the underlying contact set.  A37, A35/v2 and A44 all agree on **14 pair contacts** and **11 wall edges** at Trump.  Under the brief's literal CORNER-CORNER = 1 convention the A44 count would be m = 39 (the 2 C contacts each lose their second endpoint row), which is exactly the count that would *disagree* with A35 v2 by 4 instead of 1 — a further reason the Fact-0 geometric split is the right one.

### Hot-spot entries — hand check of the wall-row grouping

| fam | wall edges (square, wall) → corners | E_wall | F_wall | m_wall |
|---|---|---|---|---|
| 13 | (2,x=0)->[2, 3] (2,y=0)->[0, 3] (3,y=0)->[0, 3] (5,x=s)->[1] (5,y=s)->[2] (7,x=s)->[0, 1] (8,y=s)->[2] (9,x=0)->[2, 3] (10,y=0)->[0, 3] | 9 | 6 | 15 |
| 14 | (2,x=0)->[2, 3] (2,y=0)->[0, 3] (3,y=0)->[0, 3] (5,x=s)->[1] (5,y=s)->[2] (7,x=s)->[1, 2] (8,y=s)->[2] (9,x=0)->[0, 3] (10,y=0)->[0, 3] | 9 | 6 | 15 |
| 27 | (0,y=s)->[2] (1,y=0)->[0, 1] (2,x=s)->[1, 2] (4,y=0)->[0, 1] (5,x=0)->[2, 3] (5,y=s)->[1, 2] (7,x=s)->[1, 2] (7,y=s)->[2, 3] (9,y=0)->[0, 3] (10,x=0)->[0, 3] | 10 | 9 | 19 |
| 31 | (0,y=s)->[2] (1,y=0)->[0, 1] (2,x=s)->[1] (4,y=0)->[0, 1] (5,x=0)->[0, 3] (5,y=s)->[2, 3] (7,x=s)->[0, 1] (7,y=s)->[1, 2] (9,y=0)->[0, 3] (10,x=0)->[2, 3] | 10 | 8 | 18 |
| A37-NEW-1 | (0,x=0)->[2, 3] (0,y=0)->[0, 3] (2,x=s)->[1, 2] (3,x=0)->[0, 3] (4,x=s)->[0, 1] (4,y=s)->[1, 2] (6,y=0)->[0, 1] (7,y=s)->[2, 3] (8,x=s)->[1, 2] | 9 | 9 | 18 |
| A37-NEW-2 | (1,y=s)->[2, 3] (3,x=s)->[0, 1] (4,x=s)->[1, 2] (4,y=s)->[2, 3] (5,y=0)->[0, 1] (6,x=s)->[0, 1] (9,x=0)->[0, 3] (10,x=0)->[3] (10,y=0)->[0] | 9 | 7 | 16 |
| A37-NEW-3 | (0,y=s)->[2] (1,y=0)->[0, 3] (2,x=s)->[1, 2] (4,y=0)->[0, 1] (5,x=0)->[0, 3] (5,y=s)->[2, 3] (7,x=s)->[1, 2] (7,y=s)->[2, 3] (9,y=0)->[0, 3] (10,x=0)->[0, 3] | 10 | 9 | 19 |

| fam | pair edges (i,j) A37class/geom/rows |
|---|---|
| 13 | (0,3)PO/POI/1 (0,6)FL/SEG/2 (2,3)CO/SEG/2 (2,9)CO/SEG/2 (3,9)CO/POI/1 (4,8)FL/SEG/2 (4,9)PO/POI/1 (5,6)FL/SEG/2 (6,7)PO/POI/1 (6,8)FL/SEG/2 (7,10)FL/SEG/2 |
| 14 | (0,3)PO/POI/1 (0,6)FL/SEG/2 (2,3)CO/SEG/2 (2,9)CO/SEG/2 (3,9)CO/POI/1 (4,8)FL/SEG/2 (4,9)PO/POI/1 (5,6)FL/SEG/2 (6,7)PO/POI/1 (6,8)FL/SEG/2 (7,10)FL/SEG/2 |
| 27 | (0,6)PO/POI/1 (0,8)PO/POI/1 (1,2)FL/SEG/2 (2,8)PO/POI/1 (3,4)FL/SEG/2 (3,6)PO/POI/1 (3,8)PO/POI/1 (5,6)PO/POI/1 (6,10)PO/POI/1 (7,8)PO/POI/1 (9,10)FL/SEG/2 |
| 31 | (0,6)PO/POI/1 (0,8)FL/SEG/2 (1,2)PO/POI/1 (2,8)FL/SEG/2 (3,4)FL/SEG/2 (3,6)PO/POI/1 (3,8)PO/POI/1 (5,6)PO/POI/1 (6,10)PO/POI/1 (7,8)PO/POI/1 (9,10)FL/SEG/2 |
| A37-NEW-1 | (0,9)PO/POI/1 (1,8)PO/POI/1 (1,9)PO/POI/1 (2,6)FL/SEG/2 (3,5)PO/POI/1 (3,9)PO/POI/1 (4,7)CO/SEG/2 (4,8)CO/SEG/2 (5,7)PO/POI/1 (5,9)PO/POI/1 (6,9)PO/POI/1 (7,8)CO/POI/1 |
| A37-NEW-2 | (0,6)PO/POI/1 (0,8)FL/SEG/2 (1,2)PO/POI/1 (1,4)CO/SEG/2 (1,6)CO/POI/1 (2,9)PO/POI/1 (3,5)FL/SEG/2 (4,6)CO/SEG/2 (5,8)PO/POI/1 (8,9)PO/POI/1 (8,10)FL/SEG/2 |
| A37-NEW-3 | (0,6)FL/SEG/2 (0,8)PO/POI/1 (1,2)FL/SEG/2 (2,8)PO/POI/1 (3,4)FL/SEG/2 (3,6)PO/POI/1 (3,8)PO/POI/1 (5,6)PO/POI/1 (6,10)PO/POI/1 (7,8)PO/POI/1 (9,10)FL/SEG/2 |

## 5. Shadow evaluation under the brief's literal convention

The brief prescribed `CORNER-CORNER = 1 row`.  Taken literally against the A37 *label*, that undercounts every coincident-corner flush contact by 1 row (see conventions).  Verdicts under that convention:

| cand | verdict (brief conv.) | min margin | refuting genuine |
|---|---|---|---|
| B1 | REFUTED-BY-GENUINE | -1 | 27, 31, A37-NEW-2 |
| B1' | SURVIVES-GENUINE | 0 | — |
| B1'' | SURVIVES-GENUINE | 1 | — |
| B4 | REFUTED-BY-GENUINE | -1 | 27, 31, A37-NEW-2 |
| B4' | SURVIVES-GENUINE | 0 | — |
| B6 | SURVIVES-GENUINE | 9 | — |
| B6' | SURVIVES-GENUINE | 0 | — |

## 6. Conventions decided (every one of them)

1. Coordinates: z[3i]=cx_i, z[3i+1]=cy_i, z[3i+2]=theta_i in RADIANS, z[33]=s.  (The A44 brief's 't = tan(theta/2)' is wrong: A37/A22 store the angle itself; verified by evaluating every contact row at z_center, residual < 1e-15.)
2. Loaded core = 11 squares minus atlas rattler_squares.  Every contact incident to a rattler is dropped; the drop count is recorded and the dropped rows are separately LP-tested for loadability (alarm test).
3. Fact 0 (PRIMARY convention, docs/proofs/structure_lemmas.md): the contact set of a pair is a point or a segment.  Segment -> 1 edge, 2 rows; point -> 1 edge, 1 row.  Segment/point is decided GEOMETRICALLY, not from the A37 class label: the contact points are the rowspec corners with |t| <= 1/2 + 1e-6 (i.e. lying on the owner's edge segment), clustered at 1e-6.  1 cluster = point contact, 2 clusters = segment contact.
4. A37 class labels are NOT used for the row count because A37's CORNER-CORNER label conflates two geometries: (a) n_axes_tied = 4, 8 rowspecs, 1 contact point -- a genuine corner-to-corner POINT touch (1 row); (b) n_axes_tied = 2, 4 rowspecs, 2 contact points -- a FLUSH segment contact whose two endpoints are corners of both squares (2 rows; these are exactly the centre-distance-1 pairs that A35/M1b identified as flush).  Across the atlas: 105 A37-FLUSH (2 pts), 56 CC-2axes (2 pts), 16 CC-4axes (1 pt), 224 POINT (1 pt) -- the split is perfectly clean.
5. The literal brief convention (FLUSH=2, POINT=1, CORNER-CORNER=1 from the A37 label) is reported as a SHADOW count (counts_brief_convention / brief_convention_shadow).
6. Wall contacts: grouped by (square i, wall w); 1 edge per group, rows = number of distinct corners in the group (2 corners = wall-flush edge, counted in F).
7. aux (centre-distance) rows are EXCLUDED from the physical count: they are |c_a-c_b|^2 >= 1 incircle surrogates, not contacts, and Fact 0 counts contacts.  They are listed per entry for the Trump reconciliation.
8. Jacobian row representative: for each contact point, the rowspec branch preferring [V]-safe, then min |t|, then lexicographic (owner, other, edge, corner).  Deterministic.
9. Jacobian columns = 3 per core square + s (N = 3k+1).  Far-wall rows (x=s, y=s) carry ds coefficient +1; all other rows have zero s-entry.  Analytic float64 gradients, cross-checked against a37_pipeline.jac_at (mpmath interval jets, dps 60): max entrywise difference 5.6e-16.
10. rank_num [NUM]: float64 SVD, absolute cut sigma > 1e-9 (same cut as A37 classify()).  rank at 1e-11 and 1e-7 also recorded, together with the singular values straddling the cut.  Rank deficiency is never interval-certifiable at a rational approximation of an algebraic point.
11. FJ LP (lambda0 = 1): A^T lambda = e_s, 0 <= lambda <= 1e6, HiGHS.  e_s is the unit vector in the s column; equivalently the 3k stationarity sums vanish and the far-wall multipliers sum to 1.  loadable iff max lambda_r > 1e-7; forced iff min lambda_r > 1e-7.

## 7. Caveats

- `rank_num` is `[NUM]`: a float64 SVD with an absolute cut at 1e-9. Rank *deficiency* is never interval-certifiable at a rational approximation of an algebraic point (A35 M1 makes the same disclaimer). The singular values straddling the cut are tabulated; where the gap ratio is small the rank is not trustworthy and B7 verdicts on that entry should be read as indicative.
- LP tolerances: HiGHS default, multipliers boxed in [0, 1e6], loadable/forced threshold 1e-7, support threshold 1e-9. A row whose true max multiplier is between 1e-9 and 1e-7 would be called non-loadable. Rows hitting the 1e6 cap are flagged (`unbounded_rows`).
- `min_support_found` is an UPPER bound on the true minimum support: it is the best of 21 weighted LPs (all-ones + 20 seeded random positive objectives) plus 10 reweighted-L1 refinements. Exact minimum support is NP-hard and was not attempted. B2m verdicts are therefore only sound in the direction "the bound already fails at this support size"; a PASS at B2m is not a proof that no smaller support exists.
- Entry 27 (VALLEY-MARGINAL): A43-G5 flags family 27's coordinates as 6-decimal rounded. A44 reads `z_center` from the A37 certificate, which is a 43-significant-digit exact rational, and every physical row of entry 27 evaluates to |g| < 1e-15 there, so the structural counts are not affected by that flag. The flag remains relevant to anything that consumed the rounded coordinates upstream.
- The Fact-0 segment/point split is decided at float tolerance (|t| <= 1/2 + 1e-6, cluster radius 1e-6). The split it produces is perfectly clean on the atlas (105 + 56 segment contacts vs 16 + 224 point contacts, with no ambiguous case), but it is a numerical decision, not a certificate.
- Row semantics decided by A44 (each is a judgement call, all listed in §6): (i) aux `dist` rows excluded from the physical count; (ii) A37's CORNER-CORNER label overridden by the geometric contact set; (iii) one Jacobian row per contact point, branch chosen [V]-safe-first / min|t| / lexicographic; (iv) for a coincident-corner flush contact BOTH endpoint rows are taken, from the two different owner frames.
- The λ₀ = 1 FJ LP residual ‖A^T λ − e_s‖_inf is at machine precision on families 0, 1, 2, 6, 13, 14 but only 6.9e-9 (family 31), 1.4e-8 (A37-NEW-0), 1.4e-10 (A37-NEW-3), 2.2e-12 (A37-NEW-2) — these z_center points are themselves only ~1e-9 converged (A37 kkt.ls_res agrees). The feasibility verdict there is [NUM] and matches A37's independent one. It does NOT affect the B1 refutation at family 31, which is purely combinatorial.
- B2/B2-rows/B2m failures at the two VALLEY-MARGINAL entries are VACUOUS (empty loadable set because the λ₀ = 1 FJ system is infeasible there) and are flagged as such; the restricted 10-entry verdict column is the one to read for those candidates. The λ₀ = 0 branch at 27 and A37-NEW-1 was NOT analysed here — a bound conditioned on λ₀ > 0 simply says nothing at those two points, which is itself a gap for the census application.
- NOT-CP entries are evaluated and reported but never used to refute: they are minima of s only at A04's fixed lattice angles and are not FJ-critical under free rotation, so an FJ-conditional bound is not required to hold there.
- The candidate bounds are evaluated at the 36 atlas points only. A SURVIVES-GENUINE verdict is evidence, not a proof: the atlas is not a certified-complete list of FJ-critical points (A37 itself found 4 families missing from the A04 catalogue).

