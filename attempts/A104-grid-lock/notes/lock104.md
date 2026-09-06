# A104 — closing the grid, and where fully-held K0-BLOCKED packings actually start — 2026-09-05

**One line (T3).** *Fully-held K0-BLOCKED packings first appear at side* **m_lock = 4.0002374**
(operational bar of `lock103`) *and at* **4.0015246** *with a clean Gordan certificate at every
intruder; below 4 the closing iteration always frees a corner* — 443 descent endpoints at floors
10⁻³ / 10⁻², plus all 12 corpus packings, and not one held-at-all-eight packing below side 4.
**No counterexample to LOCK-FREE(< 4) was found; the conjecture's failure point is NOT the jammed
grid at 4 + ε (T1: the grid drains too), it is a genuinely locked frame just above 4.**

Conventions: `docs/proofs/noroom.md` (Lemma ROT, Lemma ROT-GRAD, the HELD test), the test itself
`attempts/A103-noroom/code/lock103.py` **reused verbatim** (meet bar 10⁻⁹, contact bar 10⁻⁷, LP
strictness 10⁻⁷, finite-motion confirmation at ε = min(10⁻⁶, g_min/10)), the descent
`attempts/A87-drain-flow/code/k0dir2_87.py` (`sqp_flow_d`, confined, verbatim) and A87's exact
certifier (`fjpolish87.verify_exact` + `k0dir2_87.exact_blocked_test_d`). Code
`attempts/A104-grid-lock/code/{close104,report104,gen_lock104}.py`; results
`results/{t1_close.jsonl,t1_close.json,t2_endpoints.jsonl,t2_mlock.json,a104_summary.json,lock104.svg}`;
one process, BLAS pinned, ~90 min wall.

![the closing](../results/lock104.svg)

## 0. The closing iteration (what "close" means here)

Lemma ROT's own step, iterated on ONE intruder at a time (the lemma is a single-square lemma):

1. `lock103` gives the intruder's HELD/UNHELD verdict and, when unheld, the LP direction y that
   strictly opens every active contact row and strictly decreases d_c(Q);
2. **travel** along y and **pin the new contact rows**: move the square by h, then re-polish by a
   least-norm Gauss–Newton correction *of that square's three coordinates only*, lifting every row
   that fell below the pinned contact gap 10⁻¹¹ back to it (A87's `GAP_FLOOR`). h is adaptive
   (10⁻⁵ initially, ×1.6 on success up to 3·10⁻⁴, ×0.35 on failure); a step is accepted only if the
   configuration is still a packing (worst SAT gap ≥ 0) **and** d_c(Q) strictly decreases;
3. repeat until the intruder is HELD, leaves its cell (d ≤ 10⁻⁹), jams, or the budget runs out;
4. then re-polish the whole configuration at fixed side (A87's `canonical` ∘ `inflate`: the side is
   re-read as the tight enclosing side + 2·10⁻⁹, pinned contacts stay active at the 10⁻⁷ bar) and
   re-run `lock103`. Outcome: **fully_held**, **corner_freed** (some corner drops below two meeters
   → the packing is K0-FREE → the drain), or timeout.

Every step is a single-square rigid motion that keeps the packing at the same side and strictly
decreases Ψ, i.e. exactly a Lemma-ROT step; the iteration is a curve-following descent along the
contact manifold. **Order: shallowest unheld intruder first** — a corner frees exactly when one of
its meeters leaves its cell, and the deep first meeters (a whole square sitting in a corner cell)
would need a retraction of order 1. The verdict itself is order-free.

**Why this differs from A103's "jams at a near-contact".** A103 travelled along the *straight line*
until the first collision and stopped; the near-contacts at 1.2·10⁻⁷…1.4·10⁻⁶ then read as jams.
Following the manifold instead (step + re-polish) the square **rolls past** those near-contacts:
polish12's TR nick, recorded by A103 as "retracts 6 %", retracts **100 %** after a total travel of
10⁻⁵. A near-contact is not an obstruction — it is a new active row to roll on.

## 1. T1 — closing the grid: the grid is LOCK-FREE too

**Answer: no. There is no exact K0-BLOCKED packing at 4 + ε held at all eight intruders in the
corpus — a corner frees instead, in 12 cases out of 12, including both jammed-grid candidates.**
That is the negative half of the T1 question: *even the grid is LOCK-FREE and the conjecture's
failure point is not where A103 put it.*

| packing | side | ROT steps | outcome | corner freed | the intruder that leaves its cell | travel |
|---|---|---|---|---|---|---|
| polish12 | 4.000000120 | 1 | corner_freed | TR | TR sq7, d = 6.6·10⁻⁶, rotation | 1.0·10⁻⁵ |
| floor 1e-4 | 4.000004388 | 167 | corner_freed | BR | BR sq3, d = 1.3·10⁻⁴, translation | 1.0·10⁻⁵ |
| floor 1e-2 | 4.000457175 | 203 | corner_freed | TR | TR sq6, d = 1.0·10⁻², rotation | 7.3·10⁻³ |
| floor 1e-3 | 3.990748517 | 20 | corner_freed | BR **and** TR | TR sq6 screw; BR sq3 rotation, both d = 1.0·10⁻³ | 1.3·10⁻³ |
| floor 1e-6 | 4.000000017 | 176 | corner_freed | TL | TL sq4, d = 3.4·10⁻⁵, rotation | 2.6·10⁻⁵ |
| record 3.98548 | 3.985483727 | 1 | corner_freed | TL | TL sq4, d = 7.0·10⁻⁹, translation | 1.0·10⁻⁵ |
| polish15 | 4.000004060 | 20 | corner_freed | BL | BL sq1, d = 1.0·10⁻⁴, rotation | 9.3·10⁻⁵ |
| polish21 | 4.000007453 | 32 | corner_freed | TR | TR sq7, d = 1.0·10⁻⁴, rotation | 1.6·10⁻⁴ |
| polish24 | 4.000011862 | 167 | corner_freed | TR | TR sq6, d = 9.1·10⁻⁵, screw | 1.6·10⁻⁴ |
| anchored0 | 4.107107416 | 5 | corner_freed | BL | BL sq1, d = 1.0·10⁻⁴, screw | 1.6·10⁻⁴ |
| anchored1 | 4.083735462 | 7 | corner_freed | TL | TL sq4, d = 1.0·10⁻⁴, screw | 4.3·10⁻⁴ |
| anchored2 | 4.083735887 | 7 | corner_freed | TL | TL sq4, d = 1.0·10⁻⁴, rotation | 4.3·10⁻⁴ |

Every endpoint is **exactly certified** (`fjpolish87.verify_exact` on the rational configuration:
`disjoint_certified = true`, minimum pair gap ≥ 10⁻¹¹, side upper bound within 2·10⁻⁹ of the input
side) and the freed corner is certified at the exact meet bar 10⁻⁹ (`exact_blocked_test_d`, zero
unknowns): the freed corner really has **one** meeter. In every case the square that leaves is a
**SECOND meeter** and the travel needed is 10⁻⁵…7·10⁻³ — the retreat is short, it is only invisible
to a straight-line test.

Readings.

1. The jammed 4 × 4 grid at 4 + ε is **not** the realisation of RES-LOCK that `noroom.md` §7
   conjectured. It cannot be: the exact grid at side 4 has one meeter per corner (the corner cell is
   filled exactly; the neighbours touch the slot at depth 0), so the ε-grid is K0-BLOCKED only
   because ε lets the two neighbours poke in by O(ε) — and O(ε) is exactly what Lemma ROT's step
   takes back out. Closing the grid **un-blocks** it.
2. So the sentence in `noroom.md` §7 "*the grid's rigidity makes it plausible that this packing is
   held at all eight intruders — a locked frame at 4 + ε*" is **measured false**. The obstruction is
   real but lives elsewhere (T2).
3. LOCK-FREE(< 4) is now supported at 12/12 rather than at the first-order level only: not merely
   "some intruder is unheld", but "the unheld intruder can be walked all the way out of its cell,
   producing a certified K0-FREE packing at the same side". For the two sub-4 corpus packings
   (3.9855 and 3.9907) this is the drain, exactly.

## 2. T2 — the empirical boundary m_lock

Directed search: `k0dir2_87.sqp_flow_d(·, δ, keep_k0=True, ROUNDS_CONF)` (the confined descent,
verbatim) from 220 fresh census seeds per floor plus the 12 corpus packings (the four floor records,
the 3.985 record, the four A87 polish and the three anchored packings) as seeds; the closing
iteration of §0 at every blocked endpoint, 9 s budget each.

| floor δ | seeds | blocked endpoints | fully held | corner freed | timeout / cap | frac held | frac freed | **m_lock** | lowest endpoint reached |
|---|---|---|---|---|---|---|---|---|---|
| 10⁻³ | 232 | 222 | 25 | 189 | 8 | **0.113** | **0.851** | **4.000237417** | 3.9907484 (freed) |
| 10⁻² | 232 | 221 | 33 | 174 | 14 | **0.149** | **0.787** | **4.003116782** | 4.0004363 (freed) |

(21 further seeds produced no blocked endpoint at all and are excluded from the denominators.)

**m_lock = 4.0002374** overall (floor 10⁻³, tag `rnd0173`), exact-certified: side upper bound
4.000237415, minimum pair gap ≥ 9.9999·10⁻¹², `disjoint_certified = true`, certified meeter counts
(2, 2, 2, 2) with zero unknowns at the 10⁻⁹ bar, `K0_BLOCKED_certified = true`.

**The sound sub-count.** `lock103` calls an intruder HELD either when Gordan's alternative holds
(multipliers exist) *or* when the LP direction exists but the finite motion at ε = min(10⁻⁶,
g_min/10) fails to confirm it — the second-order / near-contact case of `noroom.md` §2.2 remark (2).
Of the 464 intruders of the 58 fully-held packings, **378 (81 %) carry an explicit Gordan
certificate** (non-negative multipliers μ_k, λ_p, not all zero, with Σ μ_k(n_k, τ_k) + Σ λ_p g_p = 0,
residual ≤ 10⁻⁸, on **every** branch of the diagonal disjunctions); **24 of the 58 packings are
certified at all eight**. The lowest of those is

> **m_lock (Gordan-certified) = 4.001524573237** (`rnd0157`, floor 10⁻³) — side upper bound
> 4.001524571, min pair gap ≥ 9.99986·10⁻¹², disjoint certified, certified meeter counts (2,2,2,2),
> zero unknowns, `K0_BLOCKED_certified = true`; contact graph 15 square–square edges + 8 wall
> contacts; poses in `results/a104_summary.json` (`m_lock_certified_record`).
>
> | corner | sq | depth | tilt | contacts (sq / wall) | λ_total |
> |---|---|---|---|---|---|
> | BL | 1 | 1.026·10⁻¹ | 83.296° | 5 (4 / 1) | 0 (wedged) |
> | BL | 0 | 6.218·10⁻² | 83.296° | 4 (3 / 1) | 0 (wedged) |
> | BR | 2 | 8.869·10⁻¹ | 89.408° | 4 (3 / 1) | 0.258 |
> | BR | 3 | 1.020·10⁻³ | 89.408° | 5 (4 / 1) | 0 (wedged) |
> | TR | 6 | 9.206·10⁻¹ | 87.938° | 4 (3 / 1) | 0.491 |
> | TR | 7 | 1.020·10⁻³ | 87.938° | 6 (5 / 1) | 0 (wedged) |
> | TL | 5 | 4.410·10⁻² | 87.294° | 5 (4 / 1) | 0 (wedged) |
> | TL | 4 | 3.230·10⁻² | 87.938° | 4 (3 / 1) | 0 (wedged) |

**Contact structure of the fully-held packings** (464 intruders, 58 packings): 4.25 contacts per
intruder on average (min 0, median 4, max 10), **1524 square–square (77.2 %) against 450 wall
(22.8 %)** — i.e. **3.28 square contacts and 0.97 wall contacts per intruder**. 145 of the 464
intruders are held with **λ = 0**, i.e. WEDGED by their contacts alone (Lemma LOCK (b)'s
self-stress) and not by the virtual corner push; the other 319 need the virtual row. Intruder
depths run from 2.4·10⁻⁴ through a median 0.135 to 0.924, so the held packings are *not* nick
configurations: their second meeters sit at the floor depth and their first meeters nearly fill the
cell.

Caveat, recorded honestly: 7 of the 464 intruders are "held" with fewer than two contact rows (one
with none). Those are tolerance artefacts of the 10⁻⁷ contact bar — a square whose nearest gaps sit
just above the bar has no active rows, so the LP direction exists but the confirming finite motion
collides. They are exactly the cases the Gordan filter removes, which is why the certified figure
4.0015 is the one to quote.

## 3. What this changes

- **`noroom.md` §7's candidate realisation is refuted** (T1) and **replaced** (T2): RES-LOCK is
  realised, by 58 packings, all at side > 4, the lowest Gordan-certified at 4.0015246. The family is
  not the grid; it is a two-crowd configuration with all four corners doubly met at the floor depth
  and every intruder wedged, which the grid at 4 + ε is not.
- **LOCK-FREE(< 4) survives A104 unrefuted and is now supported below 4 in the strong form**: every
  endpoint the descent reached below 4 (lowest 3.9907484) closes to a certified K0-FREE packing at
  the same side. The measured threshold is **m_lock ∈ [4.0002, 4.0016]**, i.e. the conjecture would
  hold with room: the empirical gap between "no locked frame" and "locked frames everywhere" opens
  at 4, not below it.
- **The proof target sharpens.** `noroom.md` §7 asked for a joint statement about the eight
  intruders' contact cones along one wall. A104 says what the wall carries at a locked frame: **one
  wall contact per intruder and 3.3 square contacts** — the lock is carried by the square–square
  rows, not by the walls, so a wall-length budget (WALL-F) alone cannot deliver it. The four
  wall-contact rows per side are the *cheap* part; the missing step is that at side < 4 the crowd
  arms cannot supply 3+ square rows to all eight corner members at once.
- **Canary.** Trump: 5/5 intruders held, K0-FREE, side 3.877083590023 — unchanged, checked before
  and after both campaigns.

## 4. Obligations / limits

- [M] everything here; nothing is [T]. The closing iteration is a *descent*, not a decision
  procedure: `timeout`/`cap` endpoints (22 of 465) are undecided, and a fully-held verdict is only
  "held at `lock103`'s 10⁻⁷ contact bar", exact only in the direction "unheld ⇒ unheld"
  (`noroom.md` §2.2 remark (3)).
- The search is a local descent from census seeds; m_lock is an **upper bound** on the true
  threshold, and the absence of held packings below 4 is evidence, not a proof.
- 21 seeds produced no blocked endpoint; 2 endpoints hit the round cap with unheld intruders still
  rolling.
