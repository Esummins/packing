# A35 / M3-delta — region T1-a on the repaired basis v2

Code: `code/m3b_certs.py`. Data: `results/m3b_certs.json`, log
`results/m3b_certs.log`. Runtime 2.5 min, single process.
Inputs: `results/m1b_strata.json` (basis v2, alive-row family), `results/m3_certs.json`
(v1 certificates, for the consistency check), A22 `krawczyk_cert.json`, A30 `t3lib.py`.

Rigour tags as in M1/M3: `[IV]` mpmath.iv dps 60 over `box(z-hat,r)`; `[EXACT]`
exact rational/combinatorial; `[NUM]` float64 LP — search and counting only,
every kill re-verified `[IV]`.

---

## 0. HEADLINE

> **On the repaired 42-row basis v2: every cone-dead break set is certified
> FJ-free on `box(z-hat, h_W = 69/32000)` — in BOTH FJ branches — by one of
> **37** `[IV]`-verified rational Farkas directions, and the gained-contact menu
> is certified EMPTY on that box.**

| | |
|---|---|
| certificates needed | **37** (22 singletons + 11 pairs + **4 triples**) |
| certified at `h_W` | **37 / 37** — 36 by a single `y`, 1 by a subdivided cover |
| `[IV]` margin: worst / median / best | **2.08e-7** / 0.02203 / 0.04208 |
| worst margin among the 36 single-`y` certs | **2.55e-3** (`B = {30}`, `E9c0-7e1`) |
| single-`y` max radius: min / median / max | 0.001642 / 0.02032 / 0.03486 |
| certs whose single-`y` radius already exceeds `h_W` | **36 / 37** |
| generation check | **passes** — the 37 generate exactly m1b's 70 499 alive sets |

The cone-**alive** layer (70 499 break sets) is M2-delta's queue and is not
covered here.

### Both FJ branches — `λ₀ = 0` now included

theory.md's *LEMMA (λ₀ = 0 branch, region form)* applies verbatim: if
`∇g_m · y > 0` for every row that can be active on `R`, a `λ₀ = 0` FJ point would
carry `λ ≥ 0`, `λ ≠ 0` with `Σ λ_m ∇g_m = 0`; dotting with `y` gives `0 > 0`. The
`e_s·y < 0` condition is not used. **Every one of the 37 certificates satisfies
that hypothesis by construction**, so each kills both branches. This closes M3
v1's gap G-6, which I had left open.

---

## 1. CORRECTION — m1b's minimal-dead list is incomplete (22 + 11 = 33 → **37**)

**This is the load-bearing finding of the delta, and it is a correctness fix, not
a refinement.**

m1b's `task3` reports minimal *excludable* sets as 22 singletons + 11 pairs. That
enumeration stops at size 2. On v2 there are also **4 minimal dead TRIPLES**:

| triple | rows | structure |
|---|---|---|
| `{4, 38, 39}` | `W1c0[y=0]`, `F0-3a`, `F0-3b` | both rows of flush (0,3) + one wall row |
| `{12, 36, 37}` | `W3c0[x=0]`, `F0-1a`, `F0-1b` | both rows of flush (0,1) + one wall row |
| `{36, 37, 40}` | `F0-1a`, `F0-1b`, `C1-3x` | both rows of flush (0,1) + the (1,3) x-branch |
| `{38, 39, 41}` | `F0-3a`, `F0-3b`, `C1-3y` | both rows of flush (0,3) + the (1,3) y-branch |

Every one is **both rows of a flush contact plus one more row** — a shape that
cannot appear at size ≤ 2, which is exactly why a singleton+pair search misses
them. They are a v2-only phenomenon: v1 had no flush pair rows here (the dist
surrogates were single rows).

**Consequence had this not been caught.** Upward closure with only m1b's 33 sets
covers the break sets containing one of those 33 — that leaves
**91 199 − 70 499 = 20 700 cone-dead break sets uncertified**. The requested
"33 certificates ⟹ all cone-dead v2 break sets are killed" is **false as stated**.
With the 4 triples added the argument is sound.

**How this was established `[EXACT]` + `[NUM]`.** I recomputed the minimal dead
family from scratch by downward-closed apriori over the 20-row alive family: a
candidate all of whose `(k−1)`-subsets are alive but which is itself dead is by
definition minimal. Two independent confirmations:

* my apriori reproduces m1b's alive counts **level by level and exactly** —
  20, 179, 947, 3295, 7936, 13560, 16572, 14423, 8795, 3643, 970, 149, 10,
  total 70 499, `K = 13`. So m1b's *alive* numbers are right; only its *minimal
  dead* list was short.
* the 37 sets regenerate exactly 70 499 (`[EXACT]` independent-set enumeration),
  whereas the 33 give 91 199.

---

## 2. The 37 certificates

Same construction as M3 v1: the **interval-robust** Farkas LP over the box itself
(a direction optimised at z-hat does not survive box growth), with gradient
enclosures tightened by intersecting the direct interval jet with the mean-value
form `∇g(z) ∈ ∇g(z-hat) + H_box·[−r,r]`. One rational `y` per stratum,
denominator 1e12, every `inf_box ∇g_m·y > 0` re-verified `[IV]` at dps 60.

Cone semantics on v2 follow m1b's own "Menu semantics" note: the two `(1,3)`
branches are alternatives for rank/dof, but for the **cone** they are correctly
treated as separate rows with independent `λ ≥ 0`, since
`∂max = conv{branch gradients}` and `cone(conv{a,b}) = cone{a,b}`. All 42 rows
are used.

The 4 new triples certify comfortably — margins 0.0216, 0.0305, 0.0328, 0.0233,
radii 0.0123–0.0286 — so the correction costs nothing in certificate quality.

### The one thin case: `B = {35}` (`E10c3-9e0`)

Unchanged from v1, as expected (v2 keeps rows 0–35 verbatim, so this is literally
the same stratum). Its single-`y` radius is **0.001642**, i.e. 24 % short of
`h_W`; certified instead by tiling the box with **735 adaptively bisected
sub-boxes**, each with its own `[IV]`-verified `y`, worst leaf margin **2.08e-7**.
Sound, and cheaper than v1's 3956 leaves (the extra v2 rows tighten the LP), but
**this remains the fragile joint of the whole construction** and should be
re-derived with a sharper enclosure rather than left at 2e-7. In v1 I checked
that the thinness is interval conservatism and not geometry (cone dead at 0 of
300 sampled points in the box); that check was not repeated on v2.

---

## 3. Gained menu empty at `h_W` on v2 — re-derived, not inherited

> **LEMMA (basis v2).** On `box(z-hat, 69/32000)` no non-contact pair can touch
> and no new corner-wall contact can form, so the gained-contact menu of
> T0.1(ii) is EMPTY and the Part-1 certificates need beat only the retained v2
> rows.

I did not take the "bit-identical to v1" claim on faith. Deriving the non-contact
pair list **from the v2 rows themselves** and comparing with A22's list:
**identical, 41 pairs** — because A22 already classified `(1,3)`, `(0,1)`, `(0,3)`
as *contact* pairs, so v2's new rows describe pairs that were never in the
non-contact list. That is the reason the lemma carries over, and it is now checked
rather than assumed.

* **Lipschitz `[EXACT]`:** pair travel `≤ 3√2 × 0.00215625 = 0.0091482 <
  0.0248745` (smallest non-contact gap, pairs (6,7) and (8,9)); margin 0.01573.
  Wall travel `≤ 0.0067303 < 0.548642`; margin 0.5419.
* **`[IV]` direct, independent:** all 156 non-contact corner-wall clearances have
  a strictly positive lower bound over the box (worst **0.542811**). The *naive*
  SAT pair enclosure is dependency-pessimistic and returns **−0.001067** — it does
  **not** certify at this radius; bisecting the 6 coordinates of the two squares
  (64 sub-boxes) repairs it, worst bound **0.007913**. Reported because the naive
  number looks like a failed lemma.

---

## 4. Consistency with M3 v1

**The `{35}` thin case** is still minimal dead in v2 and still needs subdivision —
735 leaves instead of 3956, margin 2.08e-7 vs 2.0e-8. Slight improvement, same
character.

**The 9 sets my v1 §4 preview predicted `(1,3)` would revive: 7 of 9 confirmed.**

| set | v1 row | v2 verdict |
|---|---|---|
| `{0}`, `{3}`, `{4}`, `{12}`, `{1,2}` | wall rows of sq 0/1/3 | cone-**alive** in v2 — revival confirmed |
| `{36}`, `{37}` | `D0-1`, `D0-3` | rows dropped in v2 (dist surrogates) — n/a |
| **`{5}`** | `W1c1[y=0]` | **still minimal dead** — preview wrong |
| **`{14}`** | `W3c3[x=0]` | **still minimal dead** — preview wrong |

The two misses are explained and were pre-caveated: the v1 preview added *only*
the `(1,3)` rows, whereas v2 additionally **drops** the two dist surrogates and
**adds** four flush rows for `(0,1)` and `(0,3)`. `{5}` and `{14}` are exactly the
sets whose fate is decided by those other changes, which the preview explicitly
did not model. So the preview was directionally right (7/9) but is superseded —
use this file, not v1 §4, for the v2 picture.

---

## 5. Gaps

* **G-1 (thin certificate).** `B = {35}`: 735-leaf cover, worst margin 2.08e-7.
  Sound but fragile; deserves a sharper enclosure. Its single-`y` radius
  (0.001642) is the binding constraint on how far `h_W` could be pushed.
* **G-2 (`[NUM]` counting).** The minimal-dead recomputation and alive counts come
  from float64 HiGHS LPs. The 37 certificates, the drift/menu bounds and the §3
  lemma are `[IV]`. The apriori agrees with m1b level-by-level, which is a strong
  independent check on the `[NUM]` layer but not a proof of it.
* **G-3 (v1 sampling check not repeated).** The "cone dead at 0/300 sampled points"
  control for `{35}` was run on v1 only.
* **G-4 (scope).** Cone-**alive** strata (70 499) are untouched here — M2-delta's
  queue. The composed theorem needs both layers.
* **G-5.** m1b's minimal-excludable enumeration should be fixed at source to
  search beyond size 2, or downstream consumers will repeat this mistake. The
  same risk applies to any future basis change that introduces new multi-row
  contacts.

---

## Files

* `code/m3b_certs.py` — minimal-dead recomputation, 37 region certificates,
  the v2 gained-menu lemma, generation check, v1 consistency check.
* `results/m3b_certs.json` — certificates with rational `y` vectors and margins.
* `results/m3b_certs.log` — run log.
