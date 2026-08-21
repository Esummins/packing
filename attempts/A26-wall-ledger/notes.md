# A26-wall-ledger — the GLOBAL boundary ledger: band counting, the charged wall functional, and why it does not bite

Owner: geometry agent 3 (discrete geometry + rigorous computation). 2026-08-21.
Status: **done-negative-with-three-theorems** (~6 h). The wall-strip ledger is *not* a viable
shallow-depth killer, and the reason is now exact and quantified; two new certified structure
theorems, one decisive negative about region-rank cuts, and a numerical refutation of the only
cut that would have helped came out of the attempt.

The PI's idea. A23/A25's wastage oracle is a LOCAL, monotone lower bound on a partial configuration:
a lone interior square contributes ~0 and A24 measured T2 firing at **zero** tree nodes. The physics
it ignores is that *a uniformly tilted lattice of unit squares tiles the plane with zero waste*, so
tilt costs nothing in the bulk and waste is produced only where a same-tilt block TERMINATES — at a
wall (wedge) or against a differently oriented block (sliver). So evaluate a boundary/interface
functional GLOBALLY on all 11 squares instead of summing local pockets.

**The verdict in one line.** The counting half of the programme works beautifully and is *exact*
(§1–2: a clean reduction to the small-n square-packing constants, tight against Trump). The charging
half dies on a single hard geometric fact (§3): **a unit square flush against a wall and within a few
degrees of axis-parallel strands certified-zero dead area** — an axis-parallel block terminating on an
axis-parallel wall produces no wedge at all. That zero is not a resolution artefact and not an atlas
gap; it is the same phenomenon as A23's `corners4 = 0.0000`, and it is 6 of Trump's own 11 squares.
Hence min-over-profiles charge = **0.0000** against a budget of 3.7456 (§4), and nothing is killed at
A24's frontier (§7). The binding weak link is exactly what the PI predicted — **quantitative tilt
forcing** — and §5 settles it *negatively and quantitatively*: elementary methods give "at most 9
squares have tilt within 3.33° of axis-parallel", A24's LP probe already gives 10°, and an explicit
numerical witness shows **ten unit squares of tilt ≤ 15° do fit in [0,3.84]²** (true threshold
ε* ≈ 12°). So the provable ceiling is within 2° of the truth, the best statement obtainable is
"at least 2 squares have tilt ≥ 10°", and the ledger's requirement of ~7 charged squares is
**unreachable in principle**, not merely unproved.

---

## 1. The band-counting lemma (task 1) — exact, and it reduces to s(n)

**Setting.** Container `[0,s]²`, s rational; a placement is a closed unit square `Q(c,θ)` with
half-width `h(θ) = (cos θ + sin θ)/2 ∈ [1/2, √2/2]`. `Q(c,θ) ⊆ [a,b]²` iff `c ∈ [a+h, b−h]²`
(the axis-aligned bounding box of Q is `c ± (h,h)`).

**Definition.** Q *avoids the width-w boundary band* iff `Q ⊆ [w, s−w]²`, i.e.
`c ∈ [w+h(θ), s−w−h(θ)]²`. Write `B := s − 2w`.

> **Lemma B0 (the reduction).** The band-avoiding squares of a packing in `[0,s]²` are exactly a
> packing of unit squares in the concentric square of side `B`. Hence
> **m(w) := max # band-avoiding squares = max{ n : s(n) ≤ s − 2w }**, where `s(n)` is the
> square-packing constant. ∎

This is trivial once stated and it is the right formulation: the band-counting lemma is *exactly* as
strong as our knowledge of the small-n constants, no more and no less, and it is EXACT (upper *and*
lower bound) wherever `s(n)` is known.

Three tiers of bound are implemented (`band.py`), and every number is checked in exact rationals:

**TIER E (elementary, self-contained, proved and machine-checked here).**

> **Lemma E1.** If `(2B−1)² < 8` (i.e. `B < 1/2 + √2 = 1.914213…`) then **at most one** unit square
> fits in a square of side B.
> *Proof.* Let `Q1,Q2 ⊆ [0,B]²` be interior-disjoint unit squares with tilts `θ1,θ2`,
> `h_i = h(θ_i) ≥ 1/2`.
> (a) `Q_i ⊆ [0,B]² ⟺ c_i ∈ [h_i, B−h_i]²`, so `|Δx|, |Δy| ≤ B − h1 − h2 =: D`.
> (b) SAT: interior-disjoint convex polygons are separated by an edge normal `u` of one of them, and
> then `|u·Δ| ≥ hw1(u) + hw2(u)`. If `u` is an edge normal of Q1 then `hw1 = 1/2` and
> `hw2 = (|cos ψ|+|sin ψ|)/2 ≥ 1/2` (`ψ = θ1−θ2`), so `|u·Δ| ≥ 1`.
> (c) `u = (cos α, sin α)` with `α ≡ θ1 (mod 90°)`, so `|cos α|+|sin α| = 2h1` and
> `|u·Δ| ≤ D(|cos α|+|sin α|) = 2h1 D`.
> Combining, `1 ≤ 2h1(B − h1 − h2) ≤ 2h1(B − 1/2 − h1) ≤ (B−1/2)²/2` (unconstrained max over h1).
> Hence `(2B−1)² ≥ 8`. ∎
> (Side effect: this re-proves `s(2) ≥ 1/2+√2 = 1.9142` from scratch.)

> **Lemma E2 (pigeonhole).** Band-avoiding centres lie in a square of side `a = B − 1` (using
> `h ≥ 1/2`) and are pairwise `≥ 1` apart (disjoint incircles of radius 1/2), so any `p × q` grid with
> `a²(p²+q²) < p²q²` (cell diameter < 1) gives `m(w) ≤ pq`.

**TIER P (cited, not re-verified here):** the proven optimal point-spreading constants `d_n`
(n ≤ 9): `n` points pairwise ≥ 1 fit in `[0,a]²` only if `a ≥ 1/d_n`
(`1/d_5 = √2`, `1/d_6 = 6/√13`, `1/d_7 = (2+√3)/2`, `1/d_8 = (√6+√2)/2`, `1/d_9 = 2`).

**TIER S (cited, not re-verified here):** the proven square-packing constants
`s(1)=1, s(2)=s(3)=s(4)=2, s(5)=2+1/√2, s(6)=…=s(9)=3`. With Lemma B0 this tier is **exact**.

### The table (`band.py`, `results/band.json`), s = 96/25 = 3.84

| w | B = s−2w | a = B−1 | E1 | E2 grid | Tier E | Tier P | **m(w)** (exact, Tier S) | ⇒ this many MEET the band |
|---|---|---|---|---|---|---|---|---|
| 0.45 | 2.94 | 1.94 | – | 9 | 9 | 8 | **5** | 6 |
| 0.50 | 2.84 | 1.84 | – | 9 | 9 | 6 | **5** | 6 |
| 0.57 | 2.70 | 1.70 | – | 8 | 8 | 6 | **4** | 7 |
| **0.64** | **2.56** | **1.56** | – | 6 | 6 | 5 | **4** | **7** |
| 0.75 | 2.34 | 1.34 | – | 4 | 4 | 4 | **4** | 7 |
| 0.92 | 2.00 | 1.00 | – | 4 | 4 | 4 | **4** | 7 |
| 0.95 | 1.94 | 0.94 | – | 3 | 3 | 2 | **1** | 10 |
| **1.00** | **1.84** | **0.84** | **Y** | 2 | **1** | 2 | **1** | **10** |
| 1.10 | 1.64 | 0.64 | Y | 1 | 1 | 1 | **1** | 10 |

The PI's own pigeonhole at `w = 1` is verified exactly (`a = 21/25`, `5a²/4 = 2205/2500 = 0.882 < 1`,
so `m ≤ 2`) — but **E1 is strictly stronger and still elementary**: `(2B−1)² = 4489/625 = 7.1824 < 8`.

> **Theorem A26.1 (elementary, exact, self-contained).** In every packing of 11 unit squares in a
> square of side ≤ 96/25 = 3.84, **at most one square avoids the width-1 boundary band**, i.e. **at
> least 10 of the 11 squares meet the width-1 band.** The same holds at
> s′ = 3.877084 (`(2B−1)² = 7.5854 < 8`), and in fact at every s < 1/2 + √2 + 2 = 3.914213…

> **Theorem A26.2 (via the proven s(n), n ≤ 9).** At s = 3.84 (and at s′): at most 4 squares avoid the
> width-0.64 band, so **at least 7 of the 11 squares have centre within
> 0.64 + √2/2 = 1.34711 of a wall**; at most 5 avoid the width-0.45 band; at most 1 avoids the
> width-0.95 band.

`m(w)` becomes unavailable exactly when `B ≥ 3`, i.e. `w ≤ 0.42` at 3.84, because it then needs the
UNPROVEN `s(10)`. This is a pleasing self-similarity: the band lemma at 3.84 for small w is
equivalent to the open problem one level down.

## 2. The R-profile: a certified structure theorem on wall depths

Define for each packing square `R := dist(centre, nearest wall) − h(θ)` = the largest band width it
avoids. Lemma B0 says `#{i : R_i ≥ w} ≤ m(w)` for every w. At s = 3.84 this gives the exact profile

| statement | proved by |
|---|---|
| at most **1** square has R ≥ 0.93 | E1 (elementary) / s(2) = 2 |
| at most **4** squares have R ≥ 0.5665 | s(5) = 2 + 1/√2 |
| at most **5** squares have R ≥ 0.42 | s(6) = 3 |
| at most **9** squares have R ≥ (3.84 − s(10))/2 | needs s(10) — open |

**Sanity check against Trump's packing** (s′ = 3.8770840, `band.py`): the R-profile is
`0.9840, 0.5676, 0.5486, 0, 0, 0, 0, 0, 0, 0, 0`. So
* **zero** Trump squares avoid the width-1 band (its most interior square needs
  `1 + h(40.18°) = 1.7046` and has D = 1.6886) — consistent with `m(1) = 1`;
* the k = 1 statement is **tight**: at s′ the E1 threshold is `w > (s′ − 1.9142)/2 = 0.98144` and
  Trump has exactly one square with `R = 0.9840` above it. The lemma is *sharp on the optimum*.
* the k = 4 statement has slack 2 (Trump has 2 squares with R ≥ 0.5665, the bound allows 4).

## 3. The charged wall functional (task 2) — and its exact zero

`charge.py` builds the functional on top of A25's atlas, with disjointness handled by construction:

* a **class** is an A25 atlas cell `K = (centre box) × (tilt box)`; `query.lookup` returns a certified
  rational lower bound `dead_lb(K)` and the realising rectangles, already mapped through D4;
* `max_disjoint_charge(groups)` returns the largest sum of values over a subfamily whose *rectangle
  lists are pairwise interior-disjoint* (exact rational rectangle tests, bitmask-exact for ≤ 22
  squares). This is a certified lower bound on the area of the **union**, never a sum of overlapping
  pockets;
* the other side condition of A23's Lemma 2 is free: a region dead for `{P_i}` is automatically
  interior-disjoint from every other packing square `P_j`, because `P_j` is a legal placement for
  `{P_i}` and a dead region meets no legal placement.
* everything is done in A25's fundamental domain (centre in the quadrant, θ ≤ 45°), which is legitimate
  because every statement here is D4-invariant (class = distance to the *nearest* wall × |tilt|).

**Validation** (`python charge.py`) — all PASS against A23/A25's published numbers:
near-corner L-moat `(1.20,1.35)² × [0°,3°] → 1.4648`; fine-grid near-corner
`(1.275,1.35)² × [15°,20°] → 1.5977`; the d = 0.45 headline maximum
`(1.20,1.35)×(0.45,0.60) × [0°,3°] → 0.5078`; the mid-wall flush cell
`(0.45,0.60)×(1.65,1.80) × [0°,3°] → 0.0000`; deep interior `→ 0`; the flush corner cell
`(0.45,0.60)² × [0°,3°] → 0.0000` (= A23's `corners4`); the 90°-rotated D4 image of the corner cell
returns the identical value; the region areas sum exactly to `dead_lb`.

### The zero

Over the **1070 admissible band cells** of the coarse atlas, the minimum certified charge is
**0.0000** (16 cells), and the smallest positive value is **0.0039**. The zeros sit at
`d = min(cx0,cy0) = 0.45`, `θ ∈ [0°,6°]`: *a near-upright unit square flush against a wall*. This is
not an atlas gap — A25 enumerated those cells and got 0 (e.g. `(i,j) = (3,10..12)` are present at
θ ∈ [6°,15°] with values 0.004–0.027 and absent, i.e. 0, at θ ∈ [0°,6°]) — and it is not a resolution
artefact: it is the exact statement that an axis-parallel block terminating on an axis-parallel wall
produces **no wedge**, the same fact as A23's `corners4 = 0.0000`.

Minimum certified charge over admissible band cells, by tilt floor τ and wall-distance floor d0
(coarse 0.15×0.15×3° cells; "fine" = A25's 0.075×0.075×5° atlas, refined by taking the max with the
coarse value on the same box — both are valid lower bounds so the max is too):

| atlas | τ ≥ | d0 ≥ 0.00 | ≥ 0.75 | ≥ 0.90 | ≥ 1.20 |
|---|---|---|---|---|---|
| coarse | 0° | **0.0000** | 0.0742 | 0.1016 | 0.1016 |
| coarse | 6° | 0.0039 | 0.0742 | 0.1016 | 0.1016 |
| coarse | 15° | 0.0312 | 0.0742 | 0.1016 | 0.1016 |
| coarse | 39° | 0.0625 | 0.0742 | 0.1016 | 0.1016 |
| fine | 15° | 0.0430 | 0.1211 | **0.1602** | **0.1602** |
| fine | 40° | 0.1016 | 0.1211 | **0.1602** | **0.1602** |

(For contrast the *maxima* over the same cells are 1.46 coarse / 1.60 fine — A25's near-corner L-moat.
The ledger's problem is entirely in its minimum: the certified charge varies by a factor of ∞ across
the band, and the adversary picks the cheap end.)

**Reality check.** The certified wall charge of **Trump's actual packing** at s′ (each square looked up
as a point placement, then the max pairwise-disjoint subfamily) is **0.8672**, i.e. **21.5 % of the
budget 4.0318**. So even a *perfectly resolved* atlas evaluated on a real near-optimal packing sees
only a fifth of the empty area. That is the calibration the ledger has to beat by a factor of 5 in the
worst case, not the best.

## 4. The composition experiment (task 3) — the number the PI asked for

Constraints available: (i) at most `m(0.64) = 4` band-avoiders ⇒ **≥ 7 squares have D ≤ 1.34711**;
(ii) at most 9 squares have tilt within 3.326° of axis-parallel (§5 — the quantitative version of the
classical `⌊s⌋² = 9` bound for axis-parallel squares, which is itself proved here by the ∞-norm
pigeonhole `‖Δ‖_∞ ≥ 1` + centre square of side `s−1 < 3`); (iii) per-zone capacity by
diameter/pigeonhole (each of the four wall zones holds ≤ 4 centres, the central zone ≤ 4).

**Minimum total certified charge over all admissible profiles = 0.0000, against a budget of 3.7456.**
Explicit cheapest profile: 4 squares deep in the interior (charge 0, allowed by (i), and 2 of them may
carry the tilt required by (ii)) + 7 flush near-upright squares at the middles of the four walls
(charge 0 each, and 9 ≤ 9 near-upright is allowed by (ii)). **No kill, by an infinite margin.**

### Sensitivity — exactly what forcing would close it

The ledger delivers `n × c` where `n` = how many squares the counting lemmas force into a class and
`c` = the *minimum* certified charge of that class. Requirement: `n · c > 3.7456`.

| n (what we can force) | c required | best certified c today | short by |
|---|---|---|---|
| **7** (band, Theorem A26.2) | > 0.5351 | 0.0000 (0.1602 with tilt+depth floors) | **∞ (3.3× even optimistically)** |
| 4 (one per wall — disjointness automatic) | > 0.9364 | 0.1602 | 5.8× |
| 3 (A25's certified k = 3 witness, positions PINNED) | > 1.2485 | 1.4023 ✓ | — kills, but only for a pinned node |

So the ledger becomes a killer **iff** one can force, say,

> **Conjecture A26.C (what would close it).** *At s = 3.84, at least 7 of the 11 squares have
> `dist(centre, nearest wall) ∈ [0.90, 1.35]` and tilt ≥ 15°* — then 7 × 0.1602 = 1.12, still short;
> the honest requirement is **≥ 7 squares each certified at ≥ 0.5351, or ≥ 4 each at ≥ 0.9364**, i.e.
> forcing squares into the *near-corner L-moat band* (`d ≈ 1.2`, where the certified value is
> 1.40–1.60) rather than merely "near a wall".

The near-corner L-moat is the only part of the placement space where the charge is large enough, and
it is a *small* part: only 6 % of atlas cells carry ≥ 1.0 (A25 §10). Forcing 4 of 11 squares into it
is a far stronger statement than anything the coverage LP has ever produced (A24.1's interior-occupancy
theorem forces **one** square into a zone of area 2.69).

## 5. Quantitative tilt forcing — the weak link, measured

> **Lemma T (elementary, exact).** If two unit squares both have tilt within ε of axis-parallel then
> `‖c1−c2‖_∞ ≥ 1/(cos ε + sin ε)` (SAT gives `|u·Δ| ≥ 1` for an edge normal u, which lies within ε of
> an axis, and `|u·Δ| ≤ ‖Δ‖_∞(|cos α|+|sin α|)`). All centres lie in `[1/2, s−1/2]²`, side `s−1`;
> partitioning it into `N×N` half-open cells of side `(s−1)/N < ρ` gives **at most N² such squares**,
> i.e. the condition `(s−1)(cos ε + sin ε) < N`.

| s | at most 9 squares have tilt within | at most 16 within |
|---|---|---|
| 3.84 | **3.326°** | 39.83° |
| 3.877084 | **2.503°** | 34.45° |

At ε = 0 this is the classical `⌊s⌋² = 9` bound for axis-parallel unit squares (and the proof above
*is* the clean proof of that classical fact: `‖Δ‖_∞ ≥ 1`, centres in a square of side `s−1 < ⌊s⌋`).
Above ε ≈ 3.3° the pigeonhole jumps straight from 9 to 16 and gives nothing. Closing the gap between
3.3° and the truth is a genuine 30-dimensional packing question.

**Is the strong statement even true?** `tiltmax.py` searches numerically (smooth overlap+containment
penalty, L-BFGS-B, 300 random restarts per ε, 8 workers; a hit is confirmed by the independent exact
float SAT check `code/squares.is_valid`) for **10 unit squares of tilt ≤ ε in [0,3.84]²**:

| ε (tilt bound) | best min-margin found (n = 10) | verdict |
|---|---|---|
| 0° | −0.053333 | no packing (consistent with ⌊3.84⌋² = 9) |
| 3° | −0.024286 | no packing |
| 5° | −0.019391 | no packing |
| 8° | −0.011643 | no packing |
| 10° | −0.006470 | no packing |
| **12°** | **−0.0000000** | exactly tangential — the threshold |
| **15°** | **+0.0000009** | **FITS** (witness, `is_valid(X, 3.84, 0)` = True, max\|tilt\| = 15.000°) |
| 20° | +0.0000445 | FITS |
| 25° | +0.0000525 | FITS |
| 28.5° | +0.0000904 | **FITS** (witness has max\|tilt\| = 23.359°) |
| 35° | +0.0001097 | FITS |
| 45° | +0.0000711 | FITS (of course: s(10) ≤ 3 + 1/√2 = 3.7071) |

(Full 12-point sweep, 300 restarts per ε on 8 workers, 3801 s; the ε = 28.5° and 45° rows were
reproduced independently by a separate 120-restart run, `results/tiltmax_key.json`, to identical
values. Every FITS row is confirmed by `code/squares.is_valid(X, 3.84, tol = 0)`.)

**So ten unit squares of tilt ≤ 15° do fit in a 3.84 square, and the true 9-vs-10 threshold is
ε* ≈ 12°.** Three consequences, and they close the route:

1. **Conjecture A26.T is FALSE.** "At most 9 squares have tilt within 28.5° of axis-parallel" is
   refuted by an explicit 10-square witness with max tilt 23.36° (`results/tiltmax_key.json`). The
   only surviving version is the *cap-10* cut `Σ_{tilt ≤ 28.5°} y ≤ 10`, which is equivalent to
   "no 11-packing at 3.84 has all tilts ≤ 28.5°" — a restricted form of the main conjecture, not a
   lemma one gets on the way to it.
2. **Tilt forcing is already essentially maxed out.** A24's LP probe (`probe.py`, "NO square with
   θ ∈ [10°,80°]", τ = 9.358, certifiable) is a *valid rank bound*: the tilt-≤-10° squares of any
   packing are themselves a packing with all tilts ≤ 10°, so there are at most ⌊τ_B⌋ = 9 of them.
   That LP bound reaches 10°; the truth is 12°. **The provable ceiling is within 2° of the true
   one — there is nothing left to win.** The best statement obtainable is
   *"at least 2 of the 11 squares have tilt ≥ 10°"*, never the "≥ 6 squares with tilt ≥ 10°" the
   ledger would need.
3. **Hence the ledger's requirement (n = 7 squares each charged ≥ 0.5351, or n = 4 each ≥ 0.9364) is
   unreachable in principle, not merely unproved.** Any counting argument can force at most ~2
   mid-tilt squares at 3.84, and A25 already showed 2 mid-tilt squares are worth at most 3.0805 < 3.7456.

**Independent validation of the m(w) tiers** (same searcher, 40 restarts, `results/mcheck_*.json`) —
every cited constant is reproduced:

| test | best margin | verdict | cited constant |
|---|---|---|---|
| 2 squares in side 1.84 | −0.063179 | no | E1 / s(2) = 2 ✓ |
| 2 squares in side 1.95 | −0.017597 | no | s(2) = 2 ✓ (beyond E1's 1.9142) |
| 4 squares in side 2.00 | −0.0000000 | tangential | s(4) = 2 ✓ |
| 5 squares in side 2.56 | −0.104020 | no | s(5) = 2.70711 ✓ |
| 5 squares in side 2.71 | −0.0000000 | tangential | s(5) = 2.70711 ✓ |
| 6 squares in side 2.99 | −0.002790 | no | s(6) = 3 ✓ |

## 6. Region-rank cuts do NOT break the LP ceiling (a decisive by-product)

The band lemma is a family of **region-rank cuts** (idea I-L8):
`Σ_{p : R(p) ≥ w} y_p ≤ m(w)` for every w, plus tilt cuts `Σ_{tilt ≤ ε} y_p ≤ 9`, band×tilt cuts, and
the A21 zone ranks. A07/A19 proved the pure coverage LP can never certify 3.84 by exhibiting an
**exact rational fractional packing of value 11** (`attempts/A19-hybrid-kernel/lp_floor_384.json`,
18 placements, verified by an exact cell B&B). `rankcuts.py` evaluates every cut on it:

```
BAND RANK CUTS       w = 1.006  m=1  weight 0.500   (slack +0.500)
                     w = 1.002  m=1  weight 1.000   (slack  0.000)  TIGHT
                     w = 0.662  m=4  weight 1.500 … w = 0.658  m=4  weight 3.000
TILT CUTS            eps <= 3.326 deg: weight 9.000 <= 9          TIGHT
BAND x TILT          w=0.42, cap 9: weight 1.000  … all ok
ZONE RANKS           each corner zone [1/2,11/10]^2: rank 1, weight 1.000  TIGHT
VIOLATIONS: 0
```

> **Theorem A26.3 (negative).** A19's exact value-11 fractional packing satisfies **every** band,
> tilt, band×tilt and zone rank cut derived here, several of them with equality. Hence it stays
> feasible for the cut-strengthened LP, so `τ_cut(3.84) ≥ 11` and **the region-rank-cut family built
> from boundary bands, tilt classes and A21 zones cannot break the pure-LP ceiling at 3.84.**

This is worth more than it cost (20 minutes). I-L8 has been on the list since A10; the boundary-band
instantiation of it is now closed. The near-misses are informative: the LP optimum puts weight exactly
`1 = m(w)` in the deep interior and exactly `9` on near-upright placements — it *saturates* both
lemmas, which is why they buy nothing. The remaining weight is `2.0` at tilt 28.5°, so the *cheapest*
cut that would bite is

> **Conjecture A26.T.** *At most 9 of the 11 squares have tilt within 28.5° of axis-parallel* (i.e. at
> least 2 squares have tilt in (28.5°, 61.5°)). This cut alone would give `11 > 9` on A19's solution.

**…and §5 REFUTES it**: ten unit squares of tilt ≤ 23.36° fit in [0,3.84]² (explicit witness). Only the
cap-10 version survives, and that is a restricted form of the main conjecture.

**Why no LP-derived rank cut can ever help (and why ours could have).** If `y` is a feasible fractional
packing then `y|_R` is feasible for the sub-LP on region R, so `Σ_{p ∈ R} y_p ≤ τ_B(R)`: **LP-certified
rank bounds are automatically satisfied by every feasible `y` and can never be violated.** (A12 found
the same thing for its region cuts; it is worth stating in this generality.) A useful rank cut must
therefore come from a *combinatorial* bound strictly below `τ_B(R)`. Ours are exactly of that kind —
`m(w)` from the small-n constants, and the ∞-norm tilt bound — and the measurement above is that none
of them beats `τ_B` where it matters: the LP's own tilt bound reaches ε = 10° (τ = 9.358 ⇒ ≤ 9) versus
our elementary 3.33°, and the true threshold is 12°.

## 7. Application to A24's frontier (task 4)

`compose.py`, s = 96/25, budget 3.7456. The three live level-1 boxes (all `θ ∈ [75°,90°]`):

| node | centre box | D = dist to nearest wall | R = D − h | T2 charge (A25 atlas) | counting verdict | kill? |
|---|---|---|---|---|---|---|
| #89 | [2.330,2.4325]² | [1.4075, 1.5100] | [0.7951, 1.0100] | **0.0000** | one square with R ≈ 0.8–1.0 is allowed (m(0.93) = 1) | **no** |
| #95 | [2.4325,2.535]×[1.920,2.0225] | [1.3050, 1.4075] | [0.6926, 0.9075] | **0.0000** | allowed (m(0.5665) = 4) | **no** |
| #101 | [2.4325,2.535]×[2.0225,2.125] | [1.3050, 1.4075] | [0.6926, 0.9075] | **0.0000** | allowed | **no** |

(The charge is 0 because all three boxes sit at `D ≥ 1.305`, past the `d = 1.35` cliff where a covering
square slides into the moat — A25 §5. The PI's estimate "centre 1.356–1.459 from the wall" is the same
region; the exact interval for these boxes is 1.305–1.510.)

**Root** (s = 3.84, no hypothesis): counting gives ≥ 10 squares meeting the width-1 band, ≥ 7 within
1.34711 of a wall, ≥ 2 with tilt ≥ 3.326°; the certified charge of the cheapest such configuration is
**0.0000**. No kill.

**⇒ counting + charge kills nothing the coverage LP could not: 0 of the 3 live boxes, 0 at the root.**
This reproduces A24's finding (T2 fired at zero tree nodes) from the opposite direction — A24 found the
local test too weak at shallow depth; A26 shows the *global* version has the same weakness for a sharper
reason (a genuine zero of the functional, not a resolution problem).

## 8. Verdict (task 5) — honest

**Is the wall-strip ledger a viable shallow-depth killer? No, and the obstruction is structural.**

1. **The counting half is a success and should be kept.** Lemma B0 turns band counting into the
   small-n square-packing constants; E1 gives `m(1) = 1` elementarily and exactly at both 3.84 and s′;
   the R-profile theorem (§2) is a genuine new structure theorem, is *tight against Trump*, and costs
   milliseconds — compare A24.1's 145,008-box exact verification for a single occupancy statement.
   It should go into the case tree as a free branching constraint and into the Lean bridge (it needs
   only SAT + rational arithmetic — Lemma E1's proof is four lines).
2. **The charging half has an exact zero on the flush near-upright wall square.** The PI's physical
   picture is right — waste is made where a block terminates — but it also *predicts* the failure: an
   axis-parallel block terminating on an axis-parallel wall makes no wedge. Trump's packing is 6 flush
   uprights + 5 tilted squares; the ledger charges the uprights nothing. Min-over-profiles charge is
   0.0000 vs a 3.7456 budget.
3. **The binding weak link is quantitative tilt forcing, and §5 closes it — negatively.** Elementary
   methods give "≤ 9 within 3.33°"; A24's LP probe already gives "≤ 9 within 10°" (τ = 9.358, and τ_B
   *is* a valid rank bound by the restriction argument of §6); and an explicit numerical witness shows
   **ten unit squares of tilt ≤ 15° fit in [0,3.84]²**, with the 9-vs-10 threshold at ε* ≈ 12°. So the
   provable ceiling is within 2° of the truth: at most ~2 squares can ever be forced to be mid-tilt.
   The ledger needs 7 charged squares (or 4 near-corner ones); it will never get them. Everything else
   in the ledger (resolution, disjointness, D4 bookkeeping, union-vs-sum) is solved and cheap, and none
   of it matters while `c_min = 0` and `n_forced ≤ 2`.
4. **Region-rank cuts from this family are dead** (Theorem A26.3): all satisfied — several with
   equality — by A19's exact value-11 fractional packing, so the strengthened LP still has τ ≥ 11.
   That closes the boundary-band instantiation of I-L8, and §6 adds the general reason:
   **LP-certified rank bounds `τ_B(R)` are automatically satisfied by every feasible fractional
   packing** (restrict `y` to R), so only a *combinatorial* rank bound strictly below `τ_B(R)` can ever
   cut — and none of the elementary families (bands, tilt classes, A21 zones, small-n `s(n)`) is.
5. **The one cut that would have worked is false.** Conjecture A26.T ("≤ 9 squares within 28.5° of
   axis-parallel", the cheapest statement that cuts off A19's solution) is refuted by a 10-square
   witness of max tilt 23.36°. Only the cap-10 version survives, and it is a restricted form of the
   main conjecture rather than a lemma on the way to it.

**Cheapest next experiment (ranked).**

* **(a) 0 CPU-hours — use the R-profile as a free branching/pruning rule in A24's tree.** Theorem A26.1
   says at most one square has `R ≥ 0.93`, so any node hypothesis placing *two* squares both with
   `R ≥ 0.93` is dead with no LP at all; likewise "five squares with `R ≥ 0.5665`" (Theorem A26.2).
   A24's level-1 cover is 216 boxes at 0.1025 × 0.1025 × 15°, and its live boxes #89/#95/#101 have
   `R ∈ [0.69, 1.01]`, so this rule prunes their *pair* children immediately. Available today.
* **(b) ~1 CPU-hour — formalise Lemma B0 + E1 in Lean (I-C2 line).** Four lines of geometry (SAT +
   `h(θ) = (cos+sin)/2` + one quadratic maximisation), all rational, and it yields a real structure
   theorem ("≥ 10 of the 11 squares meet the width-1 band" at 3.84 *and* at s′). It is by a wide margin
   the cheapest non-trivial geometric statement in the repo to formalise, and it needs no certificate
   file at all.
* **(c) 5–20 CPU-hours — the only surviving ledger direction: force the NEAR-CORNER L-moat.** The
   charge is ≥ 1.40 only for squares at wall-distance ≈ 1.2 *from a corner*; 3 of them already exceed
   the budget (A25's certified k = 3). So the productive question is not "how many squares are near a
   wall" (answered, and worth nothing) but **"how many squares must sit at depth 0.9–1.35 near a
   corner?"** — a corner-zone rank/occupancy statement, which is an LP question (A21.1-style) rather
   than a counting one, and which the interior-first tree of A24 is already set up to ask.
* **(d) don't** spend more CPU on refining the wall atlas (the failure is a zero, not a resolution
   problem — A25 measured refinement at ~7 %), and don't pursue tilt-forcing lemmas past 12°: §5 shows
   there is nothing there.

## 9. Files / reproduction

`band.py` (Lemma B0/E1/E2, the m(w) tables at 3.84 and s′, tilt forcing, the Trump check —
`results/band.json`); `charge.py` (the charged wall functional over A25's atlas: `CellSet`,
`max_disjoint_charge`, validation suite, the sensitivity tables — `results/sensitivity.json`);
`compose.py` (the profile optimisation, the Trump reality check, A24's frontier nodes —
`results/compose.json`); `rankcuts.py` (the band/tilt/zone rank cuts vs A19's exact value-11
fractional packing — `results/rankcuts.json`); `tiltmax.py` (the numerical tilt-threshold search —
`results/tiltmax_n10.json` + `logs/tiltmax_n10.log` for the ε-sweep at n = 10, `results/tiltmax_key.json`
for ε = 28.5°/45°, `results/mcheck_*.json` for the independent validation of the cited `s(n)`);
`explore_atlas.py`, `explore2.py` (atlas coverage diagnostics, used to establish that the zeros are
computed zeros and not gaps).

```
python band.py
python charge.py
python compose.py
python rankcuts.py
python tiltmax.py --n 10 --eps 0 3 5 8 10 12 15 20 25 28.5 35 45 --restarts 300 --workers 8
python tiltmax.py --n 10 --eps 28.5 45 --restarts 120 --workers 2 --out results/tiltmax_key.json
for n s in "2 1.84" "2 1.95" "4 2.0" "5 2.56" "5 2.71" "6 2.99":     python tiltmax.py --n $n --eps 45 --s $s --restarts 40 --workers 2 --out results/mcheck_${n}_${s}.json
```

Dependencies: A25's `query.py` + `results/atlas_single_3.84.json`,
`results/atlas_single_fine_3.84.json`, `results/atlas_single_3.877084.json`;
`certs/trump11_certificate.json`; `attempts/A19-hybrid-kernel/lp_floor_384.json`; `code/squares.py`.
