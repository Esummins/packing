# A88 T2 — the k0 FJ-supporting contact-structure census (Opus chore, 2026-09-03)

Object, filters and method are the theory lead's T1 list; the counting method is A59's
(exact Burnside on the factorable filter subset = rigorous UPPER bound; an explicitly and
exhaustively verified sub-family = rigorous LOWER bound; unbiased Monte Carlo for the point
estimate), lifted from `S_6` to **`S_11 x D4`**. Window: **`[S_LO, S_HI] = [3.82, 3.877084]`**
(A31 used 3.80; the only S_LO-sensitive filter is L5(a), and it only gets stronger at 3.82).

Everything is labelled **EXACT / MC(+-) / EXTRAPOLATED**. Code in `code/`, raw numbers in
`results/census88_summary.json`. Wall time ~55 min of single-process CPU.

---

## 0. Headline

| quantity (k_H = 11, orbits under S_11 x D4) | value | class |
|---|---|---|
| Level-0 **upper bound** (factorable subset) | **1 274 648 400 859 932** = 1.2746e15 | EXACT |
| Level-0 **point estimate** | **9.515e10 +- 2.46e9** | MC |
| Level-0 **lower bound** (family P5, every member F0-verified) | **57 232** | EXACT |
| Decorated **upper bound** | 4.38e52 (`log10 = 52.641`) | EXACT (crude) |
| Decorated **point estimate** (F0) | **1.88e36** (`log10 = 36.27`) | MC |
| Decorated **point estimate** (F0 + K0-1 + K0-2 + K0-3) | **1.86e36** (`log10 = 36.27`) | MC |
| Decorated **lower bound** (one explicit graph) | **3.917e26** | EXACT |

**Verdict for T3: the census is ~1e36, not <= 1e6.** H1-by-structure at k_H = 11 does not become
cheap by counting: the graph layer is only ~1e11 and would be affordable, but the DECORATION
FAN-OUT (median 1.3e21 tilt-feasible decorations per graph) is the dominant multiplier by ten
orders of magnitude, and the k0 filters do not touch it (they buy a factor **1.011**).

---

## 1. Validation (every claim reproduced independently)

1. **A31 rows R0 / R2 reproduced exactly** by the new `S_k x D4` Burnside counter:
   k=3 R0 = 1072, R2 = 192; k=4 R0 = 28796, R2 = 2979. **R2 does NOT change** when S_LO moves
   from 3.80 to 3.82 — R2 is L5(b) (wall-mask admissibility) alone, which carries no metric.
2. **Weighted Burnside vs brute force**: the full factorable pair predicate (mask admissibility
   + coexistence + touching window) counted two ways — Burnside over cycle types, and a direct
   orbit enumeration over all `(mask tuple, edge set)` pairs quotiented by `S_k x D4`:
   k=3 -> 95 = 95, k=4 -> 818 = 818. **EXACT match.**
3. **Burnside divisibility** by `k! * 8` asserted at every k (raw k=11 sum
   407 039 082 299 565 869 260 800 = 1.2746e15 * 11! * 8).
4. **Labelled partition function** computed two independent ways — the identity term of the
   Burnside sum, and a closed-form sum over the 11 969 admissible mask COUNT vectors —
   agree exactly: `Z = 394 033 862 250 204 216 950 784` (3.9403e23).
5. **D4-equivariance** of the COEX / TOUCH / DREQ tables verified for all 8 group elements
   (required for the pair-orbit weights to be well defined). PASS.
6. **Structural facts** used by the closed form verified exhaustively: coexistence fails
   *exactly* when two squares carry the SAME corner mask; the touching window fails *exactly*
   when a pair's masks jointly carry two OPPOSITE walls. PASS.
7. **Decoration menu**: exhaustive enumeration on six structures confirms the gauge-fixed menu
   is exactly `20^Ess * 2^Esw`, that the tilt-feasible count agrees with the independent
   A31/A44 exact formula (`mult = 4^nf * 8^(Ess-nf)` x acyclic orientations) in every case,
   and that the decoration -> t3lib-rows map is **injective**.
8. **Decoration MC vs exact** on 6 sampled Level-0 survivors with E = 19 (`2^Ess * 2^Esw`
   affordable): exact tilt rates 0.01338 .. 0.02347 vs MC 0.01264 .. 0.02300, all within
   **|z| <= 1.80 sigma**. PASS.
9. **MC estimator cross-check**: two different proposals for the same F0 pass rate —
   plain uniform (2e7 draws) **7.465e-5 +- 1.9e-6** and importance-sampled uniform-edge-count
   (3e5 draws) **6.22e-5 +- 7.1e-6** — agree to 1.8 sigma. The importance estimator's own
   normalisation functional returns 0.989 +- 0.008 against a true value of 1.
10. **CANARY** — section 5, PASS 9/9.

---

## 2. D1 — Level 0 at k_H = 11

### Exact cumulative ablation of the FACTORABLE filters (Burnside, EXACT)

| filter set | orbits |
|---|---|
| F1 mask admissibility L5(b) (9 masks) | 3 583 640 604 893 516 408 = 3.584e18 |
| F2 + pairwise coexistence (max box distance >= 1) | 449 398 584 426 993 952 = 4.494e17 |
| F3 + touching window on edges (min box distance <= sqrt2) | **1 274 648 400 859 932 = 1.2746e15** |

F3 is the rigorous UPPER bound: every F0 structure satisfies all three.
Orbit-weight excess `UB / (Z / (11! * 8)) = 1.0330`, i.e. **+3.3 %** — the size of A59's
"<~2 % orbit-weight caveat" at k = 11; it is carried wherever a labelled rate is applied to an
orbit count.

### MC cumulative ablation of the remaining F0 filters (2e7 uniform draws, MC)

| stage | survivors | cumulative rate |
|---|---|---|
| factorable (target measure) | 20 000 000 | 1.00000 |
| + L1 loaded degree >= 2 | 19 000 956 | 0.95005 |
| + L5(d) degree <= 12 | 19 000 956 | 0.95005 |
| + L4(a) Euler `E <= 3k+2` | 10 912 381 | 0.54562 |
| + N1 per-wall <= 3 | 2 566 662 | 0.12833 |
| + L7 | 2 320 248 | 0.11601 |
| + L5(a) metric broad phase | 2 061 949 | 0.10310 |
| + L3 no floating component | 2 061 949 | 0.10310 |
| + L6 spanning component | 2 059 995 | 0.10300 |
| + **L4(b) planarity of H + wall 4-cycle** | **1 493** | **7.465e-5 +- 1.9e-6** |

**DOMINANT FILTER: L4(b) planarity, x 1 380** (0.10300 -> 7.465e-5). Second is N1 (x 4.25),
third the Euler bound (x 1.83). L3, L5(d) and L7 are essentially inert at k = 11; L5(a), the
strongest filter at k <= 7 in A31, is nearly inert here (x 1.13) because the surviving graphs
are dense enough that all hop distances are small.

### Point estimate and bracket

* labelled: `Z * p = 2.941e19`; orbits `= 9.211e10` (labelled/(11!*8)) or `UB * p = 9.515e10`.
  Reported estimate **9.515e10 +- 2.46e9 orbits [MC]**.
* This lands squarely inside A31's own EXTRAPOLATED k = 11 Level-0 band
  (M1_exp 6.41e10 / M3_ratio_lin 3.43e11 / M2_logquad 5.02e11) — an independent confirmation of
  A31's growth model, now MEASURED rather than fitted.

### Rigorous LOWER bound — family P5 [EXACT]

*Definition.* Square-square graph = the Hamiltonian **path** `0-1-...-10`; wall mask of every
square in `{none, L, B, R, T}` (wall-degree <= 1). Raw size `5^11 = 48 828 125` labelled
members. `Aut(path) = {id, reversal}`, so two members share an `S_11 x D4` orbit iff their mask
sequences agree under `(reversal)^a x D4` (order 16); F0 is invariant under that group, so
keeping the lexicographically minimal sequence of each 16-orbit counts orbits exactly.

3 076 636 canonical representatives -> 132 673 pass the vectorised part of F0 -> **57 232 pass
the FULL `f0_flags` code (all ten filters, planarity included)**, and all 57 232 were
re-verified member by member (0 failures). 223 s.

**LB = 57 232.** The bracket `[5.7e4, 1.27e15]` is wide, and the limit is exhaustive
verifiability, not the census: the family is a SINGLE graph shape, so its orbit count can never
exceed the number of mask sequences (~3.1e6). Widening to all 9 masks costs `9^11 = 3.1e10`
enumerations and was judged not worth the ~10x it would buy.

### K0-2 (A58 crowding) at Level 0

Implemented as the existential zone-assignment CSP the lead specified (>= 2 squares per corner
zone; a zone-c square may carry only corner c's two walls; zone-shrunk centre boxes
`[1/2, 1+sqrt2/2)` in the corner frame, coexistence on all pairs and the touching window on
edges). **Pass rate on the 1 493 F0 survivors: 1493/1493 = 1.000. COMPLETELY INERT.**
This is A43's law on existential filters, confirmed again at k = 11.

---

## 3. D2 — Level 1 (decorations), 300 uniformly sampled Level-0 survivors, 25 000 draws each

Structure sizes: `E` mean 23.3 (median 23), `Ess` 16.7, `Esw` 6.6.
Tilt-feasible rate off the raw menu: median **1.5e-3**, mean 2.6e-3 (5th pct 1.6e-4, 95th 9.4e-3).
One graph of 300 produced no feasible decoration in 25 000 draws.

**Decorations per graph (MC):** `log10` median **21.13**, mean 20.79, p05 17.01, p95 24.09,
max 27.73; arithmetic mean 1.98e25 (heavy-tailed — the mean is dominated by the top few graphs).
A31's EXTRAPOLATED k = 11 fan-out was 6.48e18: the measurement is **~2.4 orders larger**.

**Exact vs MC** (E <= 22 budget; only E = 19 graphs are affordable at k = 11 because the exact
enumeration is `2^Ess * 2^Esw`): 6 graphs, all within 1.8 sigma (table in
`results/level1_88.json`, key `exact_vs_mc`). The A44 branch code was copied verbatim.

**k0 decoration filters (conditional pass rates on tilt-feasible decorations):**

| filter | unweighted mean | median | **decoration-count-weighted** |
|---|---|---|---|
| K0-1 (no slot square) | 0.767 | 0.778 | **0.98950** |
| K0-3 (A45 Lemma R ruler cap) | 0.991 | 1.000 | **0.99999** |
| K0-1 and K0-3 | 0.760 | 0.775 | **0.98949** |

The weighted column is the one that multiplies the census: high-fan-out graphs are almost all
K0-1-clean (few wall-flush opportunities relative to their menus), so **K0-1 buys x 0.9895 and
K0-3 buys x 0.99999 on the total.** K0-2 buys x 1.000. K0-4 (A50 near-flush / tilt pinning) is
not expressible at Level 1 — tilt classes are symbolic — and was NOT implemented, as instructed.

**RIGID-POSSIBLE vs FLEX-ONLY** (A44 columns, `chi = m - (3k+1) = m - 34`):

| | share of tilt-feasible decorations |
|---|---|
| rigid-possible (`chi >= 0`) | **2.12e-3** unweighted mean / **1.17e-5** decoration-weighted |
| rigid-possible given K0-1 | **5.61e-4** unweighted mean / **9.08e-6** decoration-weighted |
| FLEX-ONLY (`chi < 0`) | **>= 99.79 %** (>= 99.9988 % weighted) |

Pooled `chi` histogram peaks at `chi = -10` (17.6 %) and reaches `chi = 0` with weight 3.0e-4;
under K0-1 the peak shifts to `chi = -10` at 18.8 % and `chi >= -1` collapses to 1.3e-4.
**Essentially the entire k0 FJ-supporting census at k_H = 11 is FLEXIBLE**, i.e. it must be
excluded by Farkas/FJ on a positive-dimensional family, not by Krawczyk on a rigid grain.
Almost no structure carries enough rows to be first-order rigid — the same "every candidate
needs flush contacts" mechanism A31 found at k <= 7, now measured at k = 11 and much stronger.

---

## 4. D3 — the composed decorated bracket at k_H = 11

* **LOWER bound [EXACT] = 3.9169e26 orbits.** One explicit graph from the uniform survivor pool,
  verified by the full F0 code, with `Ess = 24`, `Esw = 3`, wall mask
  `[0,0,0,0,0,1,0,0,0,4,1]` (squares 5 and 10 on L, square 9 on R), edges listed in
  `results/d3_compose.json`. Its **all-corner
  sub-menu** — every square-square contact corner-on-edge (8 gauge types each) with the strict
  class order given by an ACYCLIC ORIENTATION of the square graph, every square-wall contact
  corner-on-wall — is exactly `8^24 * AO(G) = 8^24 * 165 888 = 7.8338e26` decorations, ALL
  tilt-feasible by construction, all K0-1-clean (no wall-flush -> no slot square) and all
  K0-3-clean (no flush link -> no ruler); K0-2 also passes. Dividing by the exact stabiliser
  `|Aut| = 2` gives 3.9169e26 orbits.
* **UPPER bound [EXACT, crude] = 10^52.641 = 4.38e52.** Level-0 Burnside UB x the largest
  possible gauge-fixed menu `20^27 * 2^8` (`Ess <= 27` by planarity of H alone, then
  `Esw <= 8` by the Euler bound).
* **Point estimate [MC] = 1.881e36** (F0), **1.862e36** (F0 + K0-1 + K0-2 + K0-3); with the
  median rather than the mean fan-out, 1.28e32.

**DOMINANT MULTIPLIER: the decoration fan-out**, by ten orders of magnitude
(9.5e10 graphs x 1.3e21 median decorations, or x 2.0e25 mean). The graph count alone would be
tractable; the fan-out is not, and no k0 filter touches it.

### Report columns (decorated k_H = 11 census, orbits, MC point estimate)

| filter set | estimate | log10 | factor vs F0 |
|---|---|---|---|
| F0 alone | 1.8815e36 | 36.2745 | 1.0000 |
| F0 + K0-1 | 1.8617e36 | 36.2699 | 0.98950 |
| F0 + K0-1 + K0-3 | 1.8617e36 | 36.2699 | 0.98949 |
| F0 + K0-1 + K0-2 + K0-3 | 1.8617e36 | 36.2699 | 0.98949 |
| drop K0-1 | 1.8815e36 | 36.2745 | 0.99999 |
| drop K0-2 | 1.8617e36 | 36.2699 | 0.98949 |
| drop K0-3 | 1.8617e36 | 36.2699 | 0.98950 |

**Every k0 structural filter is inert.** The whole k0 hypothesis buys x 1.011 on the census.

### Sum over k_H = 3..7 and the 8..10 projection

A31 EXACT Level-0 MAIN survivors (S_LO = 3.80): 10, 140, 2 275, 41 951, 842 398 —
**sum(3..7) = 886 774**. Those are upper bounds for the A88 window (only L5(a) is S_LO-sensitive
and it can only strengthen at 3.82). A31 EXTRAPOLATED Level-0 for k = 8, 9, 10 (M1_exp):
1.284e7, 2.194e8, 3.751e9 (M2_logquad: 1.96e7, 5.12e8, 1.51e10). **k_H = 11 dominates by four
orders**, so the sum over all k_H is the k = 11 term to within ~4 %.

---

## 5. D4 — CANARY (mandatory, run first): PASS 9/9

Trump's decorated structure was derived BY CODE from `certs/trump11_certificate.json` in exact
rationals (`cos = (1-t^2)/(1+t^2)`, `sin = 2t/(1+t^2)`). Tolerance **1e-6, not 1e-9**: the
certificate is a rounded rational whose contacts sit at a residual of **1.06e-7 .. 1.27e-7**, so
no 1e-9 test can see them at all. Max absolute residual 1.274e-7.

Derived: 14 square-square contacts, 11 square-wall contacts, wall masks
`[3,2,6,1,1,12,8,0,0,0,4]`, per-wall degrees **L,B,R,T = 3,3,3,2**, two tilt classes
(phi = 0 for squares 0..5, phi = 40.1819 deg for squares 6..10).

| check | result |
|---|---|
| C0 F0 passes on the ACTIVE graph G (14 SS edges) | PASS |
| C1 F0 passes on the SUPPORT graph H | PASS |
| C2 per-wall degrees are 3/3/3/2 | PASS |
| C3 decoration tilt-feasible | PASS |
| C4 decoration passes K0-3 (Lemma R; max ruler extent 2 vs cap 2 / 4) | PASS |
| C5 EXCLUDED by K0-1 | PASS |
| C6 slot squares are exactly {0, 2, 5} | PASS |
| C7 INCLUDED with K0-1 dropped (K0-2 A58-general: TL corner met by squares 3 and 4, the other three corners hold slot squares) | PASS |
| C8 `len(rows) = m = E + F` (= 40) | PASS |

### DISCREPANCY FOUND (reported, not "fixed")

Trump's contact **(1, 3)** — the upright squares at (1.5, 0.5) and (0.5, 1.5) — is a
**degenerate CORNER-CORNER kiss between two squares of the SAME tilt class** (two corners of one
lie on the other's edge LINE but the contact set is a single point; tangential overlap 0.0000
against 1.0000 for the genuine flush contacts (0,1) and (0,3)). **This contact type is OUTSIDE
A31's gauge-fixed 20-type menu**, which assumes a non-flush contact strictly orders the two tilt
classes. Consequences:

* It is a real limitation of the Level-1 vocabulary inherited from A31 (and of A43's C1 rule,
  which would kill a CE link between two wall-flush zero classes — Trump has one).
* It is harmless for the census object: the SUPPORT graph H legitimately omits it (a corner kiss
  between two squares already jointly braced by square 0 carries no independent load), and
  A31's `check_trump.py` works with the ACTIVE graph G, which is a superset. F0 passes on BOTH
  G (14 edges) and H (13 edges); the decoration is built on H.
* **The same artefact is the ONLY residual alarm in D6** (section 6).
* A first-pass version of my Lemma-R implementation also mis-read this kiss as flush; the
  corrected classifier requires positive tangential overlap. Reported here because the corrected
  classifier is a change to the DERIVATION code, never to a filter.

---

## 6. D6 — certified-FJ checks against A87's polished points

167 TIGHT survivors of `attempts/A87-drain-flow/results/cp87_fj_polished.jsonl`
(`survivor_tight`), `z_polished` read as exact rationals. A87's `t3lib` imported READ-ONLY;
`active_rows_at_point`, `grad_matrix` and `cone_nnls` COPIED verbatim. Nothing under A87 written.
sigma range **[3.897231, 5.000000]**; **139 of the 167 sit at sigma = 4.000000 exactly**
(A85's degenerate loose-configuration seeds).

### (1) T1 floor check — **0 violations in 167**

Support `H` = rows with `lambda > 1e-9` of ONE NNLS certificate (multipliers are non-unique).

* `k_H`: 4 (99), 5 (40), 6 (11), 7 (10), 8 (2), 9 (3), 11 (2) — **all >= 3**.
* `m_H`: 7..32, **all >= 4**.
* L1 (every loaded square has H-degree >= 2 counting wall edges): **holds on all 167**.
* L3 (no floating loaded component) and L6 (some H-component touches two opposite walls,
  lambda_0 > 0 branch — the NNLS system IS the lambda_0 = 1 branch): **hold on all 167**.
* Identity `m_H = 3k_H + 1 + sigma_H - d_H`: holds on all 167 (tautology, logged as asked).
* `d_H`: 2 (1), 4 (74), 5 (50), 6 (14), 7 (14), 8 (10), 9 (4) — **never 0**.
* `chi = m_H - 3k_H - 1`: -9 .. -2, **`n_rigid_possible` = 0 of 167**. Every certified FJ point
  in the corpus is FLEXIBLE, exactly matching the census's own >= 99.79 % FLEX-ONLY share.

### (2) Census membership

* Decoration **tilt-feasible on 167/167**; **K0-1 holds on 167/167** (as it must — these points
  are k0 by A85's 1e-6 rule).
* **K0-3 holds on 167/167 with the correct cap**, but only on **20/167 with the census-window
  cap**. **CORRECTION TO THE ADDENDUM: K0-3 is WINDOW-DEPENDENT, not window-independent.**
  Lemma R's bound is `extent <= s(|cos psi| + |sin psi|) - 1`, i.e. `<= 2` (zero class) / `<= 4`
  at `s = 3.877084` but `<= 4 / <= 6` at `s = 5`. Running the narrow cap on out-of-window points
  produces 147 spurious kills. `a88lib.Decoration.k0_3` now takes an explicit `s_hi`.
* **L5(a) and N1: 0 failures**, with the narrow window as well as the widened one.
* **2 residual alarms**, both `L4b planarity of G + wall cycle` (tags `o124`, `o154`, both at
  sigma = 4.000000). **Both resolve completely once the degenerate corner-corner kisses are
  removed** (`n_planar_G_fail_no_degenerate = 0`): at tolerance 1e-6 the ACTIVE graph of a
  degenerate grid packing acquires corner kisses that are not menu-typed contacts. This is the
  Trump (1,3) artefact again, and L4 is NOT violated on the true contact graph.
* 4 of 167 points carry such degenerate kisses at all.
* Two bugs in MY analysis code were found and fixed by this audit, both in the gauge
  re-indexing and neither in a filter: (a) the gauge index shift is `e' = (e + o) mod 4`, not
  `e - o` (`theta = phi + 90 o`, and `R(90)` sends `NHAT[e] -> NHAT[e+1]`); (b) a square with
  `theta` a hair BELOW a multiple of 90 deg must snap to `phi = 0` in the next quarter, not
  `phi = 90 - eps`. Before (a), 21 spurious Lemma-R kills; before (b), 1 spurious
  tilt-infeasibility. After both: the numbers above.

---

## 7. D5 — the uniform sample for the T3 cost pilot

`results/census88_sample.jsonl`, **720 records**: **620** drawn under `F0 + K0-1 + K0-3`
(Level 0 uniform over labelled survivors, decoration uniform among tilt-feasible ones satisfying
K0-1 and K0-3 by rejection from the raw menu) plus **100** with K0-1 DROPPED (26 of which carry
slot squares). Each record carries a `K0_2` flag (all 620 pass). Format and gauge fully
documented in `notes/sample_format.md`; `len(rows) == m == E + F` on all 720.

Sampling cost: median 605 rejection draws per record, mean 2568; **0 structures had to be
skipped** for want of an admissible decoration, so the Level-0 marginal of the sample is
unbiased. Distribution of the main block: `E` 17..29 (mode 24), `m` 18..36 (mode 26),
`chi` -16..+2 (mode -8), `n_classes` 4..11 (mode 9), zero class pinned in 319/620,
**rigid-possible in 2/620**.

---

## 8. Gaps and caveats

* **G-A88-1** The `<= 2 %` orbit-weight caveat is measured at **+3.3 %** at k = 11; every
  labelled-rate-times-orbit-count figure carries it.
* **G-A88-2** The Level-0 lower bound is 10 orders below the estimate. It is limited by what can
  be verified exhaustively in ~30 min, not by the census. A factorable-and-provably-planar family
  would fix this; planarity is not factorable, which is the obstruction.
* **G-A88-3** The decorated point estimate uses the ARITHMETIC mean fan-out over 299 graphs; the
  distribution is heavy-tailed (p05 1e17, p95 1.2e24, max 5.4e27), so 1.88e36 is good to about
  half an order, no better. The median-fan-out figure 1.28e32 brackets it from below.
* **G-A88-4** **The gauge-fixed 20-type menu does not contain the degenerate corner-corner kiss
  between two same-class squares.** Trump has one; 4 of A87's 167 certified points have some.
  Inherited from A31/A43/A44; recorded here with two independent witnesses.
* **G-A88-5** K0-4 (A50 near-flush / tilt pinning) is not expressible at Level 1 and was not
  implemented, as instructed. A45 Lemma Q was skipped: its census form ("wall-flush anchoring
  forces class 0, and Lemma R at phi = 0 kills every ruler with k >= 4") is already subsumed by
  K0-3's zero-class cap `extent <= 2`.
* **G-A88-6** The exact A44 decoration count is `2^Ess * 2^Esw`, which at k = 11 is affordable
  only up to E ~ 19-20; the exact-vs-MC validation therefore runs at E = 19, not at the census's
  median E = 23.
* **G-A88-7** L5(a) is A31's relaxation (certified centre boxes from wall membership, universal
  separation >= 1, the hop bound); the factorable model drops the hop bound entirely for
  non-edges, which is why the exact Burnside count is an UPPER bound and not the census.
