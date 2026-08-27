# A35 / M3 — codim profile with gained contacts, and the region form of T1-a

Code: `code/m3_certs.py` (headline deliverable), `code/m3_gained.py` (travel-cap
screen), both on `code/strata_lib.py` + `A30-t3-pilot/t3lib.py`.
Data: `results/m3_certs.json`, `results/m3_screen.json` (4.7 MB), logs
`results/m3_certs.log`, `results/m3_run.log`. Runtime 25 min + 2 min, single process.

Rigour tags as in M1: `[IV]` mpmath.iv dps 60 over `box(z-hat, r)` — rigorous;
`[RFP]` Rump preconditioned nonsingularity; `[EXACT]` exact rational/combinatorial;
`[NUM]` float64 LP/SVD — used for **search and counting only**, every kill verdict
that carries weight is re-verified `[IV]`.

> **BASIS SCOPE.** Everything here is on the **A22 38-row geometric basis v1**.
> M4 has since found this basis incomplete: pair **(1,3) is a genuine 14th
> contact** with no row in it, and dist rows 36/37 are to be replaced by flush
> sep rows. §4 prices that delta ahead of `m1b_strata.json`. **It is not small.**

---

## 0. HEADLINE — region T1-a on M2's box: **YES (on basis v1)**

`h_W = 69/32000 = 0.00215625` (M2's wedge/empty certificate radius).

> **Every cone-dead break set — all `2^38 − 224` of them — is certified FJ-free
> in the `λ₀ > 0` branch on `box(z-hat, h_W)` by one of 34 `[IV]`-verified
> rational Farkas directions, and the gained-contact menu is certified EMPTY on
> that box, so no gained row can re-feed the cone there.**

| | |
|---|---|
| certificates needed | **34** (28 singletons + 6 pairs) |
| certified at `h_W` | **34 / 34** — 33 by a single `y`, 1 by a subdivided cover |
| worst `[IV]` margin at `h_W` | **1.99e-8** (row 35; see the caveat) |
| worst margin among the other 33 | **4.21e-4** (rows 0 and 3, `W0c0[x=0]`, `W0c3[x=0]`); next 2.63e-3 |
| single-`y` max radius: min / median / max | **0.001642 / 0.02383 / 0.03486** |
| sets whose single-`y` radius already exceeds `h_W` | **33 / 34** |

Combined with M2 (143 empty + 81 wedge certificates on the same box) this closes
the last *local* gap in the composed theorem **as stated on basis v1**.

### 0.1 Why 34 certificates suffice — upward closure `[EXACT]`

Cone-death is **upward closed** in `B`: `B ⊇ B'` ⟹ `retained(B) ⊆ retained(B')`
⟹ the cone shrinks. So a `y` with `∇g_m · y > 0` for every `m ∈ retained(B')`
and `e_s · y < 0` also kills every `B ⊇ B'` — because `λ ≥ 0` with
`A_retained(B)ᵀ λ = e_s` would give `0 > e_s·y = Σ λ_m (∇g_m·y) ≥ 0`.
The minimal dead sets are M1's 28 singleton killers plus the 6 minimal pairs
`{1,2} {8,10} {9,10} {21,23} {22,23} {26,29}`.

**Generation check `[EXACT]`, independent of M1's vertex enumeration.** A break
set is cone-alive iff it lies inside the 10-row family and contains none of the 6
forbidden pairs. The forbidden graph splits into 4 components with the product
structure `{1|2} × {8,9|10} × {21,22|23} × {26|29}`; independent-set counts
`3 × 5 × 5 × 3 = 225` including `∅`, i.e. **224 non-empty**. This is *set-equal*
to M1's stored list. **The M1 report's prose figure "223" is an off-by-one — the
JSON is right, the number is 224.** (M3's own LP enumeration also returns 224.)

### 0.2 Certificate construction — and why a z-hat direction is not enough

The brief's literal protocol (optimise `y` at z-hat, then grow the box) **fails**:
a direction optimised at a point carries no robustness margin, and the gradient
intervals swamp it almost immediately (median certified radius 0.003–0.032, and
8 of 28 singletons certify at **no** positive radius at all). The certificates
above instead solve the **robust** LP over the box itself —

    max t   s.t.  inf_box ∇g_m·y ≥ t  (m retained),   y[33] ≤ −t,

with `y = u − v`, `u,v ≥ 0`, `inf_box ∇g·y = Σ_j (lo_j u_j − hi_j v_j)` (t3lib's
`farkas_lp` formulation) — still **one rational `y` per stratum**, rationalised at
denominator 1e12 and re-verified `[IV]`. Gradient enclosures are tightened by
intersecting the direct interval jet with the mean-value form
`∇g(z) ∈ ∇g(z-hat) + H_box·[−r,r]` (both sound; the intersection is sound), which
buys roughly a factor 2.6 in margin (row 0: 1.6e-4 → 4.2e-4).

**The one hard case: `B = {35}` (`E10c3-9e0`).** Its single-`y` radius is
0.001642 < `h_W`. Certified instead by **tiling** `box(z-hat, h_W)` with **3956
adaptively bisected sub-boxes**, each carrying its own `[IV]`-verified rational
`y` — sound (the leaves cover the box, each leaf is the same rigorous argument),
but the worst leaf margin is **2.0e-8**, i.e. this certificate is *thin*. A
control run confirms the thinness is interval conservatism, not geometry: the
cone is dead at **0 of 300** random points sampled throughout `box(z-hat, h_W)`
for `B = {35}`. Still, this is the fragile joint of the whole construction and it
should be re-derived (higher-order enclosure or a hand-chosen `y`) rather than
left at 2e-8.

---

## 1. LEMMA (gained menu empty at `h_W`) — proved two ways

> On `box(z-hat, 69/32000)` **no non-contact pair can touch and no new
> corner-wall contact can form**, so the gained-contact menu of T0.1(ii) is empty
> and the Part-0 certificates need beat only the retained geometric rows.

**Proof 1 (Lipschitz, M1's constants) `[EXACT]`.** Pair separation is
`L_pair = 3√2 = 4.242641`-Lipschitz in `‖dz‖_∞`, so travel
`≤ 4.242641 × 0.00215625 = 0.0091482 < 0.0248745` = the smallest non-contact pair
gap at z-hat (pairs (6,7) and (8,9)); margin **0.01573**. Corner-wall clearance is
`L_wall = 1 + 3/√2 = 3.121320`-Lipschitz, travel `≤ 0.0067303 < 0.548642` (square 9
corner 2 vs `y=s`); margin **0.5419**.

**Proof 2 (`[IV]`, independent).** All 156 non-contact corner-wall clearances have
a strictly positive interval lower bound over the whole box (worst **0.542811**).
For the pairs the *naive* SAT enclosure is dependency-pessimistic and returns
`−0.001067` for (6,7) — **it does not certify at this radius**. Bisecting the 6
coordinates of the two squares (64 sub-boxes) repairs it: worst lower bound
**0.008630** for (6,7) and **0.007913** for (8,9), both `> 0`. Reported honestly
because the naive number would have looked like a failed lemma.

Note `h_W = 0.00216 < 0.005`, and M1's candidate table already shows an empty
candidate list at travel 0.005 — the lemma is consistent with M1, not a new claim
in tension with it.

---

## 2. The travel cap is the whole story (original Task 1)

Menus are built per travel cap `R` as the **intersection** of two sound necessary
conditions: M1's pair gate (the pair's SAT gap must be able to reach 0 on the box
— legitimate because `sep = 0` with `dom ≥ 0` forces contact) and a per-selection
gate using the `[IV]` mean-value enclosure
`row(z-hat) ± ‖∇row‖_{1,box}·R` on all 4 rows of each of the 32
(owner, edge, corner) selections. Cone-alive is downward closed in `B`, so
level-wise apriori enumeration over the free-row family is **exhaustive over all
`2^38` break sets** when it runs to completion.

| travel cap `R` | candidate pairs | gained sep rows | singleton cone-killers | free rows | cone-alive break sets | `K` |
|---|---|---|---|---|---|---|
| **0.005** | — (none) | **0** | **28** | 10 | **224** (exhaustive) | 6 |
| 0.01 | (6,7) (8,9) (3,4) | 8 | 16 | 22 | **≥ 217 528** (est. 5.7e5) | ≥ 8 |
| 0.02 | (6,7) (8,9) (3,4) | 12 | 13 | 25 | **≥ 157 944** (est. 6.6e5) | ≥ 7 |
| 0.05 | + (7,10) | 24 | **4** | 34 | **≥ 506 673** (est. 2.2e7) | ≥ 6 |

**This is the answer to M1's gap G-a, and it is a cliff, not a slope.** At
`R ≤ 0.005` the menu is empty and M1 stands verbatim (224 alive → 81 survivors).
At `R = 0.01` the work queue is already ~3 orders of magnitude larger, and 12 of
M1's 28 singleton cone-killers are resurrected. At `R = 0.05` only **4** rows
remain singleton killers. **The escape complex is only tractable if per-certificate
travel is capped at `R ≤ 0.005`** — which is exactly where M2's `h_W = 0.00216`
and `h_valid = 0.0052` already sit. The enumeration is a *lower* bound at
`R ≥ 0.01` (apriori truncated at 150 k sets / 420 s); the stratified estimates are
`[NUM]`.

**Which gained rows do the reviving — exactly as predicted.** Attribution over the
first 600 newly-alive sets at `R = 0.05`:

| gained row | pair | sets using | sets where **essential** |
|---|---|---|---|
| `S-8-2-9-1` | (8,9) | 455 | 39 |
| `S-8-2-9-0` | (8,9) | 339 | 0 |
| `S-7-2-6-1` | (6,7) | 243 | **57** |
| `S-6-0-7-2` | (6,7) | 178 | 0 |
| `S-7-2-6-0` | (6,7) | 173 | 0 |
| `S-6-0-7-3` | (6,7) | 141 | 6 |

The (8,9)- and (6,7)-pair bridge rows are the culprits, as the brief anticipated.
(3,4) and (7,10) contribute little. "Essential" = deleting that one row from the
menu makes the set cone-dead again.

Cross-checks at `R = 0.05` (independent of the enumeration): exhaustive `k ≤ 3`
gives 34/38, 507/703, 4479/8436 alive; the 10-row family gives 847/1023; 461 of
5000 random `k ∈ 4..12` sets alive. All consistent.

**Gradient-drift caveat, attached to every number in this table.** Gained-row
gradients are evaluated at z-hat although the contact forms elsewhere. `[IV]` max
entrywise drift over `box(z-hat,R)`:

| `R` | gained rows | the 38 geometric rows | for scale |
|---|---|---|---|
| 0.005 | — | 0.0219 | M1 Farkas margin 0.2297 |
| 0.01 | 0.0529 | 0.0440 | M1 min firing coeff 0.0594 |
| 0.02 | 0.1063 | 0.0886 | |
| 0.05 | **0.2752** | 0.2262 | |

Gained-row drift is the same order as the geometric rows' own drift — no gained
row is unusually ill-placed — but at `R = 0.05` it **exceeds** the Farkas margin
0.2297 and is 4.6× the minimum firing coefficient. So the `R = 0.02` and `R = 0.05`
rows of the table above are **indicative, not certified**; §3's radii are the
drift-free statements.

---

## 3. Interval extension radii (original Tasks 2 and 3)

### 3a. Cone kills (Task 2) — 88 dead strata: 28 singleton killers, 30 random `|B| = 7`, 30 random `|B| ∈ 8..15`

Three row-set modes: `none` = retained only (M1-style); `fixed` = retained + the
whole `R=0.05` menu at every radius; **`matched` = retained + menu(r)**, the rows
that can actually be active on `box(z-hat,r)` — the self-consistent certificate.
Radii doubling 0.001 … 0.128.

**Robust `y` (re-optimised per box):**

| group | none | fixed | matched |
|---|---|---|---|
| singleton killers (28) | 0.001 / **0.018** / 0.032 | 0 / 0 / 0.002 — **24 fail** | 0.001 / **0.005** / 0.020 |
| random `k=7` (30) | 0.02 / **0.128** / 0.128 | 0 / 0.026 / 0.128 — 3 fail | 0.005 / **0.026** / 0.128 |
| random `k∈8..15` (30) | 0.032 / **0.128** / 0.128 | 0.016 / 0.128 / 0.128 | 0.02 / **0.128** / 0.128 |
| **all 88** | 0.001 / **0.128** / 0.128, 0 fail | 0 / 0.026 / 0.128, **27 fail** | 0.001 / **0.026** / 0.128, **0 fail** |

**z-hat `y` (the brief's literal protocol):** all 88 → median 0.010 `none` /
0.004 `matched`, with **8** and **41** zero-radius failures respectively. The
protocol is simply too weak; use the robust LP.

Three readings:

1. **`matched` never fails.** Every one of the 88 dead strata is covered over a
   positive radius by ONE certificate, gained-contact reopening included, and 84
   of 88 reach `r ≥ 0.005`. **Cone-dead strata are coverable by one certificate
   each over the working region** — that was the question, and the answer is yes.
2. The *binding* cases are the **singleton killers** (median 0.005 matched), not
   the high-codimension sets — high-`k` strata are killed easily and far
   (median 0.128, the cap). Which is why the 34-certificate route of §0 is the
   right construction: it is exactly the hard cases, done properly.
3. **`fixed` is a trap.** Forcing a `y` to beat the `R=0.05` menu even on a
   0.001-radius box kills 27 of 88. Matching the menu to the radius is not a
   nicety; it is what makes the scheme work.

### 3b. Force-balance cascade (Task 3, informational — superseded by §0 on the box)

Interval form: on `box(z-hat,r)` a column fires iff **no** retained row can have a
coefficient of the opposite sign there; rows whose coefficient interval merely
contains 0 are neither killed nor blocking; structurally absent entries are
exactly 0. Iterated to a fixed point. `[IV]`, sound on the box.

53 samples of collapse-killed strata, `k = 2..12`:

* max valid radius **min 0 / median 0.128 / max 0.128**; histogram 0.02:1,
  0.032:14, 0.064:1, **0.128:36**, one sample at 0 — the rule is **robust**, valid
  over the whole tested range for 2/3 of samples. Smallest firing coefficient over
  all samples 0.0594 (M1's number, reproduced).
* **Gained rows do break cascades**, badly, at large travel: collapse survives the
  menu at z-hat for **53/53** at `R=0.005`, 48/53 at 0.01, 41/53 at 0.02, but only
  **9/53** at `R=0.05` — a gained row lands in a fired square's column with the
  opposite sign and blocks it. With the matched menu the median valid radius drops
  0.128 → 0.020.
* At `h_W` (< 0.005) the menu is empty, so the cascade is unaffected there.

---

## 4. v2 PREVIEW — the missing (1,3) contact, and it is not benign

M4's finding: pair (1,3) is a genuine 14th contact (corner-corner) with **no row
in basis v1**. Confirmed here independently: A22's cert lists 14 contact pairs but
only 13 carry rows, and (1,3) is absent from the 41 non-contact pairs (so §1's
lemma, which quantifies only over those 41, is unaffected — (1,3) is a contact,
not a gained candidate).

A missing *active* row makes the true FJ cone **larger** than the one my v1
directions beat. Adding the 8 (owner, edge, corner) selections of (1,3) that are
tight at z-hat (`S-1-2-3-0/1`, `S-1-3-3-1/2`, `S-3-0-1-2/3`, `S-3-1-1-0/3`) as
always-available generators:

* **25 / 34** minimal dead sets remain cone-dead at z-hat; **24 / 34** still
  certify on `box(z-hat, h_W)` (the 25th is `{35}`, which needed subdivision in v1
  too).
* **9 / 34 are revived**, and they are exactly the `{0,1,3}` cluster:
  `{0} {3}` (`W0c0[x=0]`, `W0c3[x=0]`), `{4} {5}` (`W1c0[y=0]`, `W1c1[y=0]`),
  `{12} {14}` (`W3c0[x=0]`, `W3c3[x=0]`), `{36} {37}` (`D0-1`, `D0-3`), and the
  pair `{1,2}` (`W0c0[y=0]`, `W0c1[y=0]`).

That is a clean, interpretable signature: the repair touches only squares 0, 1, 3
and the two dist rows that are themselves being replaced — everything else is
untouched. So the §0 headline **as a v2 statement is not yet established**: 9 of
the 34 certificates must be re-derived (or the minimal-dead-set list recomputed)
on the repaired basis. The `[IV]` certificates for the other 25 carry over
verbatim as far as they go. Not rushed into a v2 claim, per the lead's
instruction.

---

## 5. Completeness (Task 4) and the escaping class

Classification of the cone-alive-with-gained family into empty `[RFP]` / total
force-balance collapse (gained rows in the row set) / D2-slack (all 18 pair rows
broken) / survivor:

| `R` | classified | empty | collapse | D2 | **survivors** | **escaping class** | max survivor `k` |
|---|---|---|---|---|---|---|---|
| 0.005 | 224 (exhaustive) | 143 | 0 | 0 | **81** | **0** | 6 |
| 0.01 | 3000 (sample) | 164 | 0 | 0 | 2836 | 2461 | 12 |
| 0.02 | 3000 (sample) | 199 | 0 | 0 | 2801 | 2320 | 12 |
| 0.05 | 3000 (sample) | 228 | 0 | 0 | 2772 | 2466 | 12 |

**Escaping class** = cone-dead *without* the gained menu, cone-**alive** with it,
not empty, not killed by the cascade, not covered by D2 — i.e. exactly what M1
truncated away wrongly.

* At `R = 0.005` the escaping class is **empty** and M1's 81 survivors are
  reproduced exactly. M1's truncation is *correct* at that travel cap.
* At `R ≥ 0.01` the escaping class is **~82 % of the classified sets** and reaches
  `k = 12` (M1's `K = 6` is gone). Neither the cascade (0 kills — a stratum with a
  gained row available almost never collapses) nor D2 (0 — reaching all 18 pair
  rows broken needs `k ≥ 18`, far beyond where the family lives) covers any of it.
  **The slack/D2 and cascade layers contribute nothing at high `k` once gained
  contacts are allowed.** The only thing that covers this class is the matched-menu
  Farkas certificate of §3a — and that works, which is the reason §0 is a clean
  result rather than an open hole.

---

## 6. Gaps and caveats

* **G-1 (basis).** Everything is on basis v1. The v2 delta is measured (§4) and is
  **9 of 34 certificates**, all in the `{0,1,3}` cluster. Re-run against
  `m1b_strata.json` when it lands; the code takes the minimal-dead-set list as
  input, so it is a cheap delta.
* **G-2 (thin certificate).** `B = {35}` is certified at `h_W` only by a 3956-leaf
  subdivision with worst margin **2.0e-8**. Sound, but the fragile joint. Its
  single-`y` radius is 0.001642, i.e. **24 % short of `h_W`**. Sampling says the
  geometry is comfortable (0/300 alive), so a sharper enclosure should fix it.
* **G-3 (counting is `[NUM]`).** Cone-alive/dead *counts* come from float64 LPs.
  The 34 certificates, the drift bounds, the menu gates and the §1 lemma are
  `[IV]`; the tables in §2 and §5 are not.
* **G-4 (enumeration truncated).** At `R ≥ 0.01` the apriori enumeration is cut at
  150 k sets / 420 s, so those counts are **lower bounds**; the totals are
  stratified estimates. The `R = 0.005` row is exhaustive and exact.
* **G-5 (menu conservatism).** The menu is the *union* over admissible selections,
  which lets several selections of one pair carry multipliers simultaneously —
  physically only possible at a degenerate contact. A sharper "at most one row per
  pair" rule would shrink the §2 blow-up but is **not sound** as stated (degenerate
  corner-corner contacts make two selections tight — as (1,3) itself demonstrates).
  A conservative sensitivity that also lets the straddling dominance rows load is
  stored in the JSON.
* **G-6 (λ₀ = 0 branch).** §0 certifies the `λ₀ > 0` branch. The `λ₀ = 0` branch
  needs a nonnegative self-stress on retained+gained rows; M1 certified none exists
  at z-hat on the 38 rows (Farkas floor 0.2297). Its region version on `box(h_W)`
  is **not** done here — the same `y` does kill it whenever `y` beats all retained
  rows (dot stationarity with `y`), which is the case for all 34, so this is
  probably free, but it is not written down as a checked statement.
* **G-7.** Task 3's cascade radii use the point-form firing pattern as the target;
  a stratum could collapse over the box via a *different* firing order. Only
  "still collapses totally" is tested, which is the property that matters.

---

## Files

* `code/m3_certs.py` — the 34 minimal-dead-set region certificates, the
  gained-menu-empty lemma, the exact generation check, the v2 preview.
* `code/m3_gained.py` — travel-cap menus, exhaustive cone-alive enumeration,
  Farkas radius distributions, interval cascade, completeness classification.
* `results/m3_certs.json` — certificates with rational `y` vectors and margins.
* `results/m3_screen.json` — all screen data (4.7 MB).
* `results/m3_report.md` — this file.
