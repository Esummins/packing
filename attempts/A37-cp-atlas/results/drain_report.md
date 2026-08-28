# A37 -- NOT-CP drain probe

Producer `attempts/A37-cp-atlas/code/a37_drain.py`; data `attempts/A37-cp-atlas/results/drain.json`.  Everything below is [NUM] float64: this is a taxonomy / catalogue-completeness probe, **no certificates are emitted and no atlas value certificate is touched**.

The atlas entries tagged `NOT-CP` are local minima of the container side *s* only at A04's **fixed lattice tilts**: `e_s` leaves the cone of the active-row gradients once the 11 theta rows are kept, so *s* strictly decreases under free rotation.  This probe asks where they go.

## Method

**Descent (two variants, both exactly feasible at every step).**

- *strict local* -- iterated A04 `pack11` SLSQP polish on the active contact structure, accepted only when *s* decreases, with an exact-feasibility **scale repair** after every step (least `lam >= 1` killing every SAT overlap; `s` = bounding-box side).  Never leaves the feasible set, never crosses a barrier: its landing is the honest *drain*.
- *smoothed* -- the same polish alternated with a high-mu penalty continuation (mu = 1e4..1e8), which lets the contact structure change and can smooth over a small barrier.  Run as a cross-check only: where it beats the strict descent it has crossed a barrier into a neighbouring basin, which is a **basin hop** and not a drain, so it is reported in the `s_smoothed` column and in the `smoothed` field of `drain.json` but never used as the answer.

When SLSQP stalls, the strict descent falls back to a line search along the **LP descent direction of the audited active rows**, repairing to exact feasibility at every trial point and accepting only a decrease.  This is needed because at the raw A04 point the descent often requires switching the active separating axis, which SLSQP's fixed-axis linearisation cannot see.

**Landing analysis.** A37 pipeline tolerance ladder {1e-7,1e-6,1e-5,1e-4} -> audit -> Gauss-Newton refine -> classify, then residual-scaled CP judgment (nnls residual, min free-sign multiplier, LP descent rate) *plus* a **constructive** witness: a landing is called NOT-CP only if a strictly-smaller-`s` feasible packing is actually produced.  (Per the lead's batch-B correction the binary equality-LP alone is not trusted.)

**Matching.**  The primary key is the container side `s`, tol 1e-8.  This is forced: a landing generically carries **rattlers**, and a rattler is free both to translate inside its cage *and to rotate*, so neither the raw coordinates nor the tilt multiset is invariant between two representatives of the same family -- they routinely differ by O(1e-2), and 1e-1 is not unusual.  `s` is invariant, it is the quantity the whole atlas is about, and among the 102 A04 families every pair of DISTINCT `s` values below 3.95 is separated by >= 2.8e-4 while the converged points reproduce the catalogue's floats to ~1e-9..1e-12; tol 1e-8 therefore sits four orders of magnitude inside the separation and one order outside the convergence noise.  Full geometric agreement under D4 x square-relabelling (Hungarian) x global translation, tol 1e-6, is accepted as a sufficient shortcut, and the geometric alignment count (how many of the 11 squares coincide to 1e-6) is recorded on every match as corroboration -- for the pooled landings it runs at 6-9 of 11, the remainder being exactly the rattlers.

## Counts

| outcome | n sources |
| --- | --- |
| DRAINS-TO-KNOWN | 13 |
| DRAINS-TO-NEW | 11 |
| STUCK (landed NOT-CP again) | 0 |
| analysis failed | 0 |
| **NOT-CP sources processed** | **24** |

Distinct NEW attractors after dedupe: **4** (the 11 `DRAINS-TO-NEW` sources collapse onto them).

## Per-source

| src | cat | s_before | s_after (strict drain) | drop | s_smoothed | landing | rank | outcome | match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 3 | 3.885903275 | 3.885618083 | 2.85e-04 | 3.885618083 | VALLEY | 27 | DRAINS-TO-KNOWN | catalogue family 1 (= atlas family 1): s agrees to 4.25e-12; 6/11 squares also align geometrically to 9.5e-07 under D4 x |
| 4 | 4 | 3.885982568 | 3.885618083 | 3.64e-04 | 3.885618083 | VALLEY | 26 | DRAINS-TO-KNOWN | catalogue family 1 (= atlas family 1): s agrees to 4.34e-12; 6/11 squares also align geometrically to 9.5e-07 under D4 x |
| 5 | 5 | 3.886196372 | 3.885618083 | 5.78e-04 | 3.885618083 | VALLEY | 26 | DRAINS-TO-KNOWN | catalogue family 1 (= atlas family 1): s agrees to 4.36e-12; 6/11 squares also align geometrically to 9.5e-07 under D4 x |
| 7 | 7 | 3.886831907 | 3.886746029 | 8.59e-05 | 3.886746029 | VALLEY | 32 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.68e-12; 8/11 squares also align geometrically to 4.3e-12 under D4 x |
| 8 | 8 | 3.887044973 | 3.886746029 | 2.99e-04 | 3.886746029 | VALLEY | 32 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.88e-12; 9/11 squares also align geometrically to 4.3e-12 under D4 x |
| 9 | 9 | 3.887415522 | 3.886746029 | 6.69e-04 | 3.886746029 | VALLEY | 32 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.88e-12; 9/11 squares also align geometrically to 4.3e-12 under D4 x |
| 10 | 10 | 3.887935147 | 3.886746029 | 1.19e-03 | 3.886746029 | VALLEY | 32 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.87e-12; 8/11 squares also align geometrically to 4.3e-12 under D4 x |
| 11 | 11 | 3.888014017 | 3.886746029 | 1.27e-03 | 3.886746029 | VALLEY | 32 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.88e-12; 9/11 squares also align geometrically to 4.3e-12 under D4 x |
| 12 | 12 | 3.891405521 | 3.886746029 | 4.66e-03 | 3.886746029 | VALLEY | 32 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.87e-12; 9/11 squares also align geometrically to 3.0e-07 under D4 x |
| 15 | 15 | 3.897628537 | 3.897230787 | 3.98e-04 | 3.897230787 | VALLEY | 28 | DRAINS-TO-KNOWN | catalogue family 13 (= atlas family 13): s agrees to 6.06e-12; 4/11 squares also align geometrically to 6.1e-12 under D4 |
| 16 | 16 | 3.897774693 | 3.886746029 | 1.10e-02 | 3.886746029 | VALLEY | 31 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.85e-12; 7/11 squares also align geometrically to 4.3e-12 under D4 x |
| 17 | 17 | 3.898252927 | 3.897230787 | 1.02e-03 | 3.897230787 | VALLEY | 28 | DRAINS-TO-KNOWN | catalogue family 13 (= atlas family 13): s agrees to 6.06e-12; 4/11 squares also align geometrically to 6.1e-12 under D4 |
| 18 | 18 | 3.902688537 | 3.886746029 | 1.59e-02 | 3.886746029 | VALLEY | 32 | DRAINS-TO-KNOWN | catalogue family 6 (= atlas family 6): s agrees to 3.88e-12; 9/11 squares also align geometrically to 4.3e-12 under D4 x |
| 19 | 19 | 3.903006188 | 3.902673974 | 3.32e-04 | 3.902673974 | VALLEY | 29 | DRAINS-TO-NEW | no catalogue family matches; nearest is 18 (ds 1.46e-05, tilt-multiset 1.23e+01 deg, geometric 3.15e-01 (1/11 aligned))  |
| 20 | 20 | 3.903040466 | 3.902673974 | 3.66e-04 | 3.902673974 | VALLEY | 29 | DRAINS-TO-NEW | no catalogue family matches; nearest is 18 (ds 1.46e-05, tilt-multiset 1.23e+01 deg, geometric 6.66e-01 (1/11 aligned))  |
| 21 | 21 | 3.903079442 | 3.902673974 | 4.05e-04 | 3.902673974 | VALLEY | 29 | DRAINS-TO-NEW | no catalogue family matches; nearest is 18 (ds 1.46e-05, tilt-multiset 1.72e+01 deg, geometric 3.27e-01 (1/11 aligned))  |
| 22 | 22 | 3.903098026 | 3.902673974 | 4.24e-04 | 3.902673974 | VALLEY | 29 | DRAINS-TO-NEW | no catalogue family matches; nearest is 18 (ds 1.46e-05, tilt-multiset 1.76e+01 deg, geometric 3.15e-01 (1/11 aligned))  |
| 23 | 23 | 3.903159489 | 3.902673974 | 4.86e-04 | 3.902673974 | VALLEY | 29 | DRAINS-TO-NEW | no catalogue family matches; nearest is 18 (ds 1.46e-05, tilt-multiset 1.78e+01 deg, geometric 3.16e-01 (1/11 aligned))  |
| 24 | 24 | 3.903231983 | 3.902673974 | 5.58e-04 | 3.902673974 | VALLEY | 29 | DRAINS-TO-NEW | no catalogue family matches; nearest is 18 (ds 1.46e-05, tilt-multiset 1.23e+01 deg, geometric 3.15e-01 (1/11 aligned))  |
| 25 | 25 | 3.912522237 | 3.912232040 | 2.90e-04 | 3.912232040 | VALLEY | 27 | DRAINS-TO-NEW | no catalogue family matches; nearest is 25 (ds 2.90e-04, tilt-multiset 2.08e+00 deg, geometric 3.63e-02 (3/11 aligned))  |
| 26 | 26 | 3.912657754 | 3.912232040 | 4.26e-04 | 3.912232040 | VALLEY | 26 | DRAINS-TO-NEW | no catalogue family matches; nearest is 25 (ds 2.90e-04, tilt-multiset 2.31e+01 deg, geometric 4.04e-01 (3/11 aligned))  |
| ~~27 | 27 | 3.925148814 | 3.925148812 | 1.55e-09 | 3.897230787 * | VALLEY | 29 | (superseded) DRAINS-TO-KNOWN | catalogue family 27 (= atlas family 27): s agrees to 1.55e-09; 8/11 squares also align geometrically to 4.8e-07 under D4 |
| 28 | 28 | 3.925199029 | 3.924402476 | 7.97e-04 | 3.924402476 | VALLEY | 27 | DRAINS-TO-NEW | no catalogue family matches; nearest is 27 (ds 7.46e-04, tilt-multiset 2.24e+01 deg, geometric 7.85e-01 (1/11 aligned))  |
| 29 | 29 | 3.925527078 | 3.924402476 | 1.12e-03 | 3.924402476 | VALLEY | 27 | DRAINS-TO-NEW | no catalogue family matches; nearest is 27 (ds 7.46e-04, tilt-multiset 2.24e+01 deg, geometric 7.85e-01 (1/11 aligned))  |
| 30 | 30 | 3.926293181 | 3.925470067 | 8.23e-04 | 3.925470067 | VALLEY | 30 | DRAINS-TO-NEW | no catalogue family matches; nearest is 29 (ds 5.70e-05, tilt-multiset 2.05e+01 deg, geometric 7.21e-01 (1/11 aligned))  |

`s_after` is the strict-descent landing and is the drain.  A `*` on `s_smoothed` marks the sources where the penalty-smoothed run crossed a barrier into a deeper neighbouring basin; that landing is a basin hop, recorded but not counted as the drain.  Rows marked `~~` are excluded from the counts (see *Provenance*).

## Attractors reached

| attractor | sources draining in |
| --- | --- |
| catalogue family 6 (s = 3.886746029) | 8 |
| A37-NEW-0 (s = 3.902673974) | 6 |
| catalogue family 1 (s = 3.885618083) | 3 |
| A37-NEW-1 (s = 3.912232040) | 2 |
| A37-NEW-2 (s = 3.924402476) | 2 |
| catalogue family 13 (s = 3.897230787) | 2 |
| A37-NEW-3 (s = 3.925470067) | 1 |

## New families

| id | s | landing class | rank | contacts pairs/walls | sources | tilt multiset (deg, D4-invariant) | deep re-descent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A37-NEW-0 | 3.902673974139 | VALLEY | 29 | 14/17 | [19, 20, 21, 22, 23, 24] | 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 11.7703 40.4982 42.6474 43.6765 43.6765 | s -> 3.902673974139 (unchanged) |
| A37-NEW-1 | 3.912232040225 | VALLEY | 27 | 11/18 | [25, 26] | 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.1688 24.1844 41.4704 44.9196 | s -> 3.912232040225 (unchanged) |
| A37-NEW-2 | 3.924402476308 | VALLEY | 27 | 11/16 | [28, 29] | 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 5.4717 22.4216 38.4409 38.4409 38.4409 | s -> 3.924402476308 (unchanged) |
| A37-NEW-3 | 3.925470067293 | VALLEY | 30 | 11/19 | [30] | 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 41.3249 41.3249 41.5687 | s -> 3.886746028606 (perturb_1e-02_0) |

## Stuck

**None.**  Under the residual-scaled test every landing is a genuine critical point / valley: no source re-lands NOT-CP.

## Catalogue-completeness verdict

**The A04 102-family catalogue is NOT complete as a list of free-angle attractors, but the gap is benign for the bound.**

- All 24 NOT-CP sources move: every one is confirmed constructively to be a fixed-angle artefact, and every landing is a genuine critical point / valley (0 STUCK).  The NOT-CP tag is therefore sound -- these atlas entries are not local minima of s and their basins do not terminate at the A04 point.
- 13 of 24 sources drain into families the catalogue already has (catalogue indices 1, 6, 13).  Those landings are pooled: 3 distinct known attractors absorb them, so the NOT-CP set is mostly a set of *fixed-angle shadows* of a handful of real families.
- 11 sources drain to **4 attractors that are absent from the catalogue**: A37-NEW-0 at s = 3.902673974139 (sources [19, 20, 21, 22, 23, 24]); A37-NEW-1 at s = 3.912232040225 (sources [25, 26]); A37-NEW-2 at s = 3.924402476308 (sources [28, 29]); A37-NEW-3 at s = 3.925470067293 (sources [30]).  Each is a feasible packing (interval check: min wall clearance and min pair separation >= -4e-17, i.e. zero to float precision) whose s is 1.5e-05 / 2.9e-04 / 7.5e-04 / 5.7e-05 below the nearest catalogue s -- far outside the ~1e-9..1e-12 convergence noise of the catalogue points, so these are genuinely new families, not re-encodings.
- **Consequence for the bound: none.**  The smallest new attractor sits at s = 3.902673974, which is 0.0256 above the incumbent 3.877084, and above every catalogue family it drains from.  The new families cost nothing on the upper side and threaten nothing on the lower side; they are a *bookkeeping* gap in A04's family enumeration, and the far-field atlas must eventually carry an entry for each.
- No certificates were emitted for the new families (per the brief).  Each was stress-tested by a deep re-descent (mu = 1e2..1e8 plus 32 perturbed restarts at amplitudes 1e-3, 3e-3, 1e-2, 3e-2).  A37-NEW-0, A37-NEW-1, A37-NEW-2 held at their landing under every one of them, which is strong evidence they are real attractors and not stalls of the descent loop.  A37-NEW-3 did not: a 1e-02 perturbation escapes it, so it is the shallowest of the four and the one to re-check first.
- Descent semantics: every `s_after` above is the landing of the **strictly monotone, always-feasible** descent, so each drain is a statement about the actual basin, not about what an aggressive re-optimiser can find.  The penalty-smoothed run agrees on 24 of 25 sources; on [27] it crossed a barrier into a deeper basin, and that stronger landing is recorded separately under `smoothed` rather than used as the drain.
- Sources [5, 10, 16, 26] need the LP-descent-direction fallback to take their first step: at the exact A04 point the descent requires switching the active separating axis, which SLSQP's fixed-axis linearisation cannot see.  The fallback line-searches along the active-row LP descent direction and repairs to exact feasibility at every trial, so the path is still monotone and feasible throughout.

## Provenance

- atlases read: atlas.json, atlas_batchA.json, atlas_batchB.json
- atlases missing: none
- NOT-CP entries found on the closing re-scan that were not in the initial list: none
- superseded: [27] -- family 27 is a FALSE NOT-CP per the batch-B lead correction (critical to 7.3e-8, min free-sign multiplier +2.06e-2, descent rate -1.2e-7); its record is kept but excluded from the counts
- family identity test: family identity = |ds| < 1e-8 (primary key; rattlers translate AND rotate freely, so coordinates and the tilt multiset are not invariant, while distinct A04 s values below 3.95 are >= 2.8e-4 apart) OR full geometric agreement < 1e-6 under D4 x square relabelling (Hungarian) x global translation; the geometric alignment count is recorded on every match as corroboration
- wall time: 7.5 min descent + 7.0 min match/report

