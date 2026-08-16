# A04 — upper-bound search: try to beat Trump's 11-square packing (s* = 3.877083590022814…)

Status: **done-negative** (no packing below the record found; Trump's packing rediscovered 276 times / 7 of 8
fixed-s basin-hopping chains). Deliverable: catalogue of local optima (`families_catalogue.json`,
`local_optima.json`, `best_optima.png`).

## Correction (from coordinator)
The exact record is s* = 3.877083590022814177… (root of Ellsworth's octic
s⁸−20s⁷+178s⁶−842s⁵+1923s⁴−496s³−6754s²+12420s−6865). My first runs used the rounded threshold 3.877084 and wrote
`CANDIDATE_fsbh_*.json` files with s ≈ 3.87708359224 — that is **2.2e-9 above s***, i.e. re-discoveries of Trump's
packing (the strict-feasibility inflation adds ~1e-9). Files (15 in total, incl. 9 from the `near` workers that still ran the old threshold) were renamed `REDISCOVERY_*.json` (data kept),
threshold in `fsbh.py` set to s* − 1e-9, and `check_candidates.py` re-scans everything with the exact root: **0 records
below s* − 1e-9**; best strict s = 3.877083590026693 (s* + 3.9e-12).

## Model / code (all in this dir)
- `pack11.py`: 11 unit squares, variables (centres, angles, s); separating-axis overlap penalty (pair + wall);
  penalty continuation (mu 10 → 1e8) then SLSQP polish; strict feasibility by inflation (`local_opt` in `driver.py`).
- `verify_exact.py`: exact rational verifier (Fraction arithmetic on a rational approximation of the configuration,
  SAT with rational cos/sin via tan-half-angle) — used on every "candidate".
- `driver.py` (methods rand/biased/bh/diag/bhrec, free-s penalty basin hopping) — from the first (interrupted) session.
- `fsbh.py` (new): **fixed-s basin hopping**. Choose target s_t, minimise the pure overlap penalty at fixed s (BFGS,
  bounded), kick (translate/rotate/swap squares, occasionally re-seed the tilted group), accept by penalty; when the
  penalty reaches ~0 relax with free s to get a strict local optimum, record it, shrink s_t by 0.001–0.005 and
  continue; stop a chain after 120 consecutive non-improving kicks. Option `near`: also relax+record near-feasible
  states (penalty < 3e-4) for catalogue breadth. Start types: mix / rand / biased / diag / record(+kick).
- `catalogue.py`: merges `res_*.jsonl` → `results.jsonl`; clusters (a) by exact s (1e-6) → `local_optima.json`
  (702 entries), (b) by structure (n_upright, tilt multiset folded to [0,45°], 5° bins) → `families_catalogue.json`
  (102 families); draws `best_optima.png`.
- `check_candidates.py`: exact-root threshold scan + exact verification of the best rediscovery (passes at
  s_claim = s+1e-9, margin 1.3e-10).

## Runs (this session, ≤6 processes, ~2 h wall clock total)
| method | procs×min | records | best strict s | comment |
|---|---|---|---|---|
| bh (free-s BH, driver.py) | 1×55 | 131 | 4.0000000 | never leaves the 4×4 grid basin (upright squares dominate free-s penalty landscape) |
| fsbh (fixed-s BH) | 6×(40–55) | 26 | 3.8770836 (=s*+1.3e-9) | 5 of 6 chains reached Trump's packing within 20 min |
| fsbh-near (fixed-s BH + near-feasible relaxations) | 2×38 | 2330 | 3.8770836 (=s*+3.9e-12) | both chains reached the record; produced the catalogue breadth |
| fsbh-rec-relax (start at record + kick) | 1×40 | 1 | 3.8977747 | kicked out of the record basin, did not return |

Rediscovery frequency of Trump's packing: **276 records within 1e-6 of s*** (416 counting the family with slack),
**7 of 8 fixed-s chains** hit it; time-to-hit 5–20 min per chain. Zero records below s*.

## Local-optima catalogue (structural families with s_min < 3.95; full data in families_catalogue.json)
`up` = upright squares, tilt = angles of tilted squares folded to [0°,45°], cnt = hits, contacts = pair+wall at 1e-6.
```
s_min      cnt  up  ctc   tilt multiset (best)                comment
3.8770836  416   6  14+11 [40.2 x5]                            Trump/G–R record (5 tilted squares in a diagonal 2-1-2 block, 6 upright)
3.8856181   59   6  13+8  [45,45,45,45,44.8]                   5 squares at exactly 45° (diamond block) — 2nd best structure
3.8856181    5   5  11+8  [45x4,44.7, 0.8]                     same with one square slightly tilted (non-rigid variant)
3.8859033   22   6   6+5  [43.3,43.3,43.3,43.1,42.5]           slack/non-rigid variants between the 40° and 45° families
3.8859826   19   6   5+5  [41.3,42.4,43,43,43]                 "
3.8861964    6   5  10+5  [42.5x4,42.4, 0.6]                   "
3.8867460 1101   7  13+11 [41.6 x4]                            4 tilted at 41.6°, 7 upright — biggest basin in fixed-s BH (3rd best value)
3.8868319    9   6  10+8  [41.6x4, 0.8]                        variant
3.8870450  566   7   8+6  [41.1,41.1,41.1,36.3]                4 tilted, one at 36° — 4th
3.8874155   50   6   8+5  [40.7x3,35.5,0.6]                    variant
3.8879351    1   6   6+6  [40.7x4, 3.5]
3.8880140    1   5   6+6  [35,40,40,40, 0.5,1.3]
3.8914055    1   6  12+11 [10.5,37.2x4]
3.8972308    1   6  11+9  [33.9 x5]                            5 tilted at 34°
3.8974620    3   5  11+9  [33.8x4,33.4,0.5]
3.8976285    7   6  10+9  [33.7x3,31.2,30.8]
3.8977747    1   6  11+9  [33.6x3,33.1,25.1]                   (record + kick relaxation)
3.8982529    3   5  10+9  [30.7,30.8,33.4x3, 1.0]
3.9026885    1   6  11+9  [31.5x3,28.2,18]
3.9030062    1   6  13+9  [11.8,43.1,43.7,43.7,40.6]
3.9030405    5   6  13+9  [42.6,43.7,43.7,40.7,28.3]
3.9030794    1   7  13+9  [43.2,43.7,43.7,40.7]
3.9030980    4   6  13+9  [41.7,43.7,43.7,40.7, 0.5]
3.9031595    1   7  13+9  [40.8,43.8,43.8,40.7]
3.9032320    2   6  13+9  [26,42.1,43.8,43.8,40.8]
3.9125222    2   8  11+9  [22.5,39.4,44.9]                     3 tilted, 8 upright
3.9126578    1   7  11+9  [19.7,22.4,38.3,44.8]
3.9251488    3   8  11+10 [41.4,45,41.4]
3.9251990    1   6  11+9  [5.1,21.9,36,38.1,38.1]
3.9255271    1   7  10+9  [38,33.5,33.5,20.5]
3.9262932    1   8  11+10 [37.3,40.4,44.5]
3.9369642    3   7  11+10 [44.3,42.1,42.1,42.1]
```
Everything else found is ≥ 3.9451 (incl. the 4×4 grid, s=4, which is where free-s methods get stuck).
Caveat: many entries with few contacts (e.g. 6+5) and several distinct s within one family are *not* fully converged
rigid optima — they come from the `near` relaxations (single SLSQP from a near-feasible fixed-s point) and represent
slack configurations sliding towards the family's rigid representative. Family-level s_min values are the reliable
numbers; the 5°-binned tilt multiset is the structural key.

## Honest assessment
- Every method that can escape the upright basin converges to Trump's packing (basin frequency ~7/8 chains, 276
  hits); the next-best structures (45°-diamond 3.88562, 4×41.6° 3.88675, 3.88705) are 0.0085–0.010 above it and are
  found even more often. Nothing between s* and 3.8856 except slack variants of Trump's structure. This is
  consistent with the literature (unimproved since 1979; G–R 2005 and 2024–26 SA searches found the same). The
  landscape below 3.95 is dominated by "5 or 4 tilted squares in a diagonal block + upright rest"; all top-4
  families are of this type. I see no evidence of an unexplored structural class (e.g. two tilted groups, or
  tilts far from 40–45°) that scores below 3.90.
- Not covered: exhaustive contact-graph enumeration; genuinely different topologies were only sampled by random
  kicks. Runs were short (≈2 CPU-hours total). If A04 is continued, the useful direction is *not* more basin
  hopping (it saturates on Trump within minutes) but structured seeds: two separated tilted groups, tilts near
  20–30°, and 6+ tilted squares — those families barely appear in the catalogue (a few hits, all ≥ 3.90).
- Practical value: `families_catalogue.json` gives, for each of the top structures, coordinates (`best_x`) that A03
  / A06 could use as starting points for exact reconstruction, and the rediscovery data supports the claim that
  3.877083590022814 is very likely optimal among the reachable structures.
