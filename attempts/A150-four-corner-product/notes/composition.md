# A150 — the four-corner product root for k0_00: the root lemma, the D4 reduction of the product, what the geometry is worth, and the price

Companion files: `docs/proofs/k0_route.md` (Lemmas K0-FREE, K0-WIDEN, K0-BLOCKED, K0-D4),
`attempts/A143-corner-first-k0/notes/composition.md` (the one-corner root this is measured
against — read §1, §1a, §3, §6 first), `attempts/A148-gallery-v4/code/geo148.py` (the feasible
region and the disk bound), `attempts/A144-guard-lines/code/guardline.py`,
`attempts/A132-polygon-core` (K′), `attempts/A135-polycore-verifier` (the exact rational axis
core), `docs/budget.md` §k0 row (the 12 000 CPU-h the interior tree is priced at).

---

## 1. The root lemma as used

Write `F = Δ_λ P` for a packing dilated to `s0 = 969271/250000`, and `B_c^w = ` the **widened**
unit box at corner `c`, side `a_w = 1 + (λ_max − 1)(1 + 1/√2) = 1.0255101` (Lemma K0-WIDEN,
`k0_route.md` §4.1; A143 (R2)).

> **(R1) The dichotomy** (`k0_route.md` §3, Lean `teleport_packing`; consumes k1_00, obligation
> K0-O1, still OPEN). Either some corner box is met by ≤ 1 square of `P` — **K0-FREE**, a (T) leaf:
> `P` does not exist for `m < ŝ` and is a Trump image at `m = ŝ` — or **every** corner box is met by
> ≥ 2 squares (**K0-BLOCKED**).

> **(R6) The four corner lineages are disjoint** (new here, and the reason budget 7 is right).
> The widened corner boxes are pairwise at distance `s0 − 2 a_w = 1.8262 > √2 = diam(unit square)`,
> so **no unit square meets two corner boxes**. Consequently
> (i) the four conditioned squares of a product node are automatically DISTINCT — no `cores_meet`
> side condition is needed, unlike A143's Rule I, and the node's budget is exactly `11 − 4 = 7`;
> (ii) K0-BLOCKED forces **≥ 8 distinct corner meeters** out of the eleven squares, so only three
> squares of an 11-packing are free of the corners, and four of the seven remaining squares at a
> product node are themselves corner meeters (an unexploited row).

**The tilt range is the full `[0°, 90°)`.** A143 §1a is carried over verbatim: Lean's
`OccupiesSlot` is exact (axis-aligned AND exactly on the slot centre), so `skeleton = ∅` removes
only a measure-zero set of poses from the `θ = 0` slice and **no positive-measure tilt exclusion is
available** in the ∀-packings form the k0_00 tree is stated in. Every cover below runs over all six
15° tilt windows at every corner.

## 2. The product cover and its D4 reduction

**Local frames.** Each corner carries the BL frame transported by a **rotation** (never a
reflection), so a level-1 cell index means the same thing at every corner (`code/frames150.py`):

    BL: (u,v) = (x, y)      BR: (y, s−x)      TR: (s−x, s−y)      TL: (s−y, x)

and, because a unit square is invariant under a quarter turn, the local tilt is always `θ mod 90`,
so the tilt window index is frame-independent.

**The state.** `t = (t_BL, t_BR, t_TR, t_TL)`, one band cell per corner. Under K0-BLOCKED each
corner has a meeter, so every K0-BLOCKED packing reaches at least one state — the product is a
COVER of the K0-BLOCKED branch (the K0-FREE branch is the (T) leaf of (R1)), and it is an
*independent* cover, so it composes with the interior tree and with A143 by A143's Rules I–III.
Two amendments to Rule I: (i) inside the product node no `cores_meet` side condition is needed at
all — (R6) makes the four squares distinct for free; (ii) a product node composed with an interior
cell `X` gets budget `11 − 5 = 6` only when `X`'s box is core-disjoint from all four corner boxes,
otherwise the interior square may BE one of the four and the budget stays 7.

**The group.** The container's D4 acts on states by

    r (quarter turn):  BL→BR→TR→TL→BL, local indices UNCHANGED     r(t) = (t_TL, t_BL, t_BR, t_TR)
    m (reflection in y = x): fixes BL, TR; swaps BR, TL; transposes EVERY local index by
        T(ix, iy, it) = (iy, ix, 5 − it)                            m(t) = (T t_BL, T t_TL, T t_TR, T t_BR)

`T` has **no fixed cell** (`T(a) = a` needs `ix = iy` and `it = 5 − it`, impossible for an integer
`it ∈ 0..5`), so both DIAGONAL reflections fix no state at all; the orbit count is Burnside over the
eight elements and comes out very close to an exact `/8`. The transport of (K)/(C)/(T)/(D)/(D′)
verdicts across an orbit is `k0_route.md` §2's Lemma K0-D4 proof verbatim with the state set as the
D4-set — **nothing new is needed in Lean beyond the cover check itself**, exactly as in A143 (R4).

## 3. The band (T1)

**(B1) second-meeter room.** K0-BLOCKED demands a SECOND meeter at the same corner, so the
first meeter's cell `A` must have a partner cell `B` (possibly `B = A`) with A143's pair verdict
ALIVE-CORE. A143's `results/pairs143_geom.jsonl` decides this for all 11 772 canonical pairs, and
the verdict is transpose-invariant, so the lookup is exact.

**(B2) L-shaped-remainder room.** With the one conditioned polygon core `K′(A)` removed, A148's
margin-certified feasible-centre region `R` and its disk bound give `budget ≤ n_max =
area((GREEN ∪ UNDECIDED) ⊕ B(1/2) ∩ [0,s0]²)/(π/4)`; (B2) is `n_max ≥ 10`.

| condition | cells killed | survivors |
|---|---|---|
| all level-1 cells (A143's 6 × 6 × 6, none emptied by the container/reach clip) | — | 216 |
| **(B1)** no partner cell survives the pair geometry | **10** | 206 |
| **(B2)** disk bound `n_max ≥ 10` (measured `n_max ∈ [15, 18]`) | **0** | **206** |

A cell that fails (B1) is a **(T) leaf, not a (C) leaf**: no second meeter means the corner is met
by ≤ 1 square, i.e. K0-FREE, which `teleport_packing` discharges as "no packing for `m < ŝ`, a
Trump image at `m = ŝ`". The Trump canary (§4) confirms no Trump meeter is discarded by it.

**The band is not narrow — this is the brief's premise, and it fails.** Measured:

* centre distance from the corner: `[0.7071, 2.4503]`, i.e. the ENTIRE corner-meeting zone
  (`[1/2, a_w+√2/2]²` has corner distances `[√2/2, √2·1.7326]`) — the band removes no distance
  interval at all;
* tilt: the full `[0°, 90°)` — no tilt window is emptied at any position;
* 35 of the 36 position cells survive with all six 15° tilt bins; the 36th, `(3,3)`, dies entirely,
  and `(2,3)`/`(3,2)` lose the two near-axis bins `t0`, `t5`.

So the only content of the band is *"a corner intruder may not sit on the corner diagonal at middle
distance (centre in `[1.1163, 1.3217]²`, ~1.72 from the corner) at any tilt"* — 10 of 216 cells,
4.6 %. The room condition contributes **nothing**: at one core the disk bound gives `n_max` 15–18
against a budget of 10, weak by a factor of 1.6.

**Cover confirmation (drawn → tested → hits).** 20 000 drawn, container-admissible, realised,
interior-disjoint BL 2-crowds (both members meeting the widened box, SAT-disjoint), each member
located in its RAW cell *and* in A143's transpose-canonical cell: **20 000 hits, 0 misses**
(`results/band150_confirm.json`); the float "meets the widened box" test was cross-checked against
A143's exact rational `f_min_max` on the first 400 members, 0 disagreements.

## 4. What the product geometry is worth (T2)

Every kill is a NECESSARY condition on a K0-BLOCKED packing, so discarding a state is sound.
Because (Q2)/(Q1)/(Q1s) are PAIRWISE, the survivor count never needs the product enumerated: the
four corners are a 4-cycle, the count is a transfer-matrix trace, and the D4 quotient is Burnside.

Per adjacent corner pair (BL,BR), of `206² = 42 436` combinations:

| kill | fires | share |
|---|---|---|
| (Q2) max centre distance over the two clipped boxes < 1 | 648 | 1.53 % |
| (Q1) `K′` at one corner meets `K′` at the other | 816 | 1.92 % |
| (Q1s) A131 per-tilt-sub-bin refinement of (Q1) | 266 | 0.63 % |
| **total adjacent** | **1 730** | **4.08 %** |
| **total diagonal (BL,TR)** — 0 (Q2), 6 (Q1), 2 (Q1s) | **8** | **0.019 %** |

and the product counts (`results/prod150_stages.json`):

| stage | 4-tuples | D4 orbits |
|---|---|---|
| 0 raw band product `206⁴` | 1 800 814 096 | 225 117 727 |
| 1 + (Q2) on the four walls | 1 692 641 440 | 211 592 473 |
| 2 + (Q1) | 1 561 731 694 | 195 228 403 |
| 3 + (Q1s) | 1 519 799 378 | 189 986 576 |
| 4 + the two diagonals | **1 519 380 658** | **189 934 236** |

Burnside detail at stage 4: `|Fix| = (1 519 380 658, r 198, r² 39 166, r³ 198, m_diag 0, m_anti 0,
m_horiz 26 834, m_vert 26 834)`.

**(QG) guard lines kill nothing, and cannot.** A144's `rhs(l) = s0 − Σ_j minchord(box_j, l)` needs
a chord sum above `s0 = 3.877`. Over 776 axis lines at pitch 0.01 and 3 000 sampled surviving
states (`results/prod150_guard.json`): `rhs_min = 1.3773`, median 1.7224, **0 lines below 0 and 0
below 0.15**. The tightest line found is vertical at `x = 1.985` with chord vector
`(0, 0.9899, 0.9899, 0.5201)` — at most three of the four conditioned squares are *guaranteed* to
be cut by one line, and a guaranteed unit-square chord is at most `√2`, so the sum can never reach
`s0`. The guard line is a pin-rich weapon; four corner intruders are too far apart to feed it.

**(QD) the disk bound kills nothing, with a factor of 1.4 to spare.** Measured DIRECTLY (all four
cores in one region) on 40 random survivors: `n_max ∈ [10, 14]`, median 12, against budget 7;
0 kills. The *separable* surrogate `area₄ = area₀ − Σ_c δ(t_c)` is **not** a theorem and was
refuted here (errors to 1.73 in area on 6 checks, always in the safe direction); the sound separable
statement is only `area₄ ≤ area₀ − max_c δ_c`, which gives `n_max ≥ 16`.

**(QS) a separation bound is WORSE than the disk bound here (new, negative).** Partitioning the
plane into squares of side `L = 0.70` (`L√2 < 1`, so at most one centre per square) and counting
the squares that meet the non-blocked set gives `n_max ∈ [9, 16]`, median 13, on the same 40
survivors — worse than the disk bound's 12 — because the surviving centre region is a *thin
connected filament* around the container (open area 0.88–2.93) rather than a few blobs. Recorded so
nobody re-derives it.

**Trump canary: PASS.** All eight D4 images of Trump at `s0` have ≥ 2 widened meeters at every
corner (A143 §4), giving 24 four-tuples per image; **192 of 192 lie in band cells and 192 of 192
survive every geometric kill** (`results/canary150.json`). No kill above is unsound against the one
family that is known to exist.

## 5. The LP (T3): four corners DO buy slack — the decisive positive result

See `notes/tables.md` for the full table. Hypothesis cores are A135's certified EXACT axis cores, so
the FROZEN `verify_case.py` (sha256 `521cb01f…`) needs no change; `K′` is an audit column only.

The comparison that matters is against A143 §6 at the SAME cells and the same 240 s cap:

| conditioning | budget | n | η | converged kills | certified |
|---|---|---|---|---|---|
| A143, ONE square at BL | 10 | 3 | −0.0442 / −0.6328 / −0.0000 | **0** | 0 |
| A143, TWO squares at BL (the doubly-met pair) | 9 | 2 | −0.0826 / −0.0769 | **0** | 0 |
| **A150, FOUR squares, one per corner (fine band)** | **7** | **13** | **−6.0 … +1.08, median −1.0** | **7** | **4 PASS** |
| A150, four squares, coarse 3×3×3 cover | 7 | 5 | −0.56 … +1.96 | 0 | 0 |

**The three A143 cells re-run as `(k,k,k,k)` isolate the marginal value of the three extra cores**,
and it is enormous:

| cell | A143, 1 core, budget 10 | A150, 4 cores, budget 7 |
|---|---|---|
| `(1,1,t0)` | τ 9.9558, **η −0.0442** | τ 6.0000, **η −1.0000** (unconverged candidate) |
| `(3,2,t1)` | τ 9.3672, **η −0.6328** | τ **1.0000**, **η −6.0000**, converged, **verifier PASS in 9.4 s** |
| `(4,0,t2)` | τ 10.0000, **η −0.0000** | τ 5.0000, **η −2.0000**, converged kill |

**The Trump canary node is alive, as it must be**: `q_trump_g0` (the four meeters of image `g0`)
gives τ = 8.0787, η = **+1.08**. The corner-hugging extreme `(0,0,t0)⁴` is alive too (η +0.88).
Both are the near-axis, hard-against-the-corner states — the LP is killing the TILTED, mid-distance
states, which is exactly the geometry the k0 tree has never been able to touch.

**Kill rate on random survivors** (the number the price depends on): of **8 uniformly drawn
surviving 4-tuples**, **5 are converged kills** (3 verifier PASS), 1 an unconverged candidate
(η −0.536), 2 alive (τ = 7.0000 exactly and τ = 7.60) — a level-1 kill rate of **63 % (75 % with
the candidate)**, against A143's **0 %** at one and at two corners. Converged kills are also
CHEAP: 8.7, 13.2, 26.9, 43.3, 71.4 CPU-s, versus the 240 s cap the alive nodes all hit.

**Certification.** Of the converged kills, three PASS the FROZEN verifier on the first certificate
(`certs/*.certify.json`). Two FAIL — and the failure is **not** a margin problem: re-running them
with the certificate scale cap raised from A143's 1.03 to 1.30 (`q_402_x4_recert`, τ = 5.0 with
room to scale to 1.397; `q_rand_301_000_321_533_recert`, τ = 6.0) reproduces the same τ and the
same FAIL. They are recorded in the lab's standard language: **LP-dead, certificate pending** —
they need the A13/A14 separation loop with more rounds and a longer `cert_time` than A150's cap
allowed, not a different core or a different scale.

## 6. Price

Reference: the interior-first k0_00 tree is priced at **12 000 CPU-h** (`docs/budget.md` k0 row,
9 400–10 900 after A141), and A143 priced its corner-first roots at 3 800–8 900 (single) and
8 000–18 800 (pair).

**The cost of a product cover with `N` cells per corner is `(N⁴/8) · t`,** with `t` the per-node LP
time. A150 measures both halves of that trade-off, and they pull against each other: `N` controls
the exact core half-side `a`, and `a` controls whether the node decides at all.

| cover | cells/corner N | core `a` | D4 orbits `N⁴/8` | cost at t = 100 s | cost at t = 250 s |
|---|---|---|---|---|---|
| 2×2 × 2 tilt windows of 45° | 8 | 0.048–0.049 | 538 | 15 CPU-h | 37 |
| 2×2 × 3 of 30° | 12 | 0.060–0.165 | 2 661 | 74 | 185 |
| 3×3 × 3 of 30° | 27 | 0.176–0.279 | 66 771 | 1 855 | 4 637 |
| 3×3 × 4 of 22.5° | 36 | 0.177–0.271 | 210 447 | 5 846 | 14 614 |
| 4×4 × 4 of 22.5° | 64 | 0.238–0.333 | 2 067 939 | 57 400 | 143 600 |
| 6×6 × 3 of 30° | 108 | 0.289–0.393 | 15 266 858 | 424 000 | 1 060 000 |
| **6×6 × 6 of 15° (the band, where the LP decides)** | **206** | **0.312–0.361** | **189 934 236** | **5 275 000** | **13 187 000** |

The break-even against the 12 000 CPU-h row is at **`N ≈ 40`**, i.e. a cover no finer than 3×3
positions × 4 tilt windows — core half-side `a ≈ 0.18–0.27`, roughly *half* the `a ≈ 0.32` at which
the LP was measured to decide. **So the whole question is: does the four-corner LP still decide at
`a ≈ 0.2`?** It does not, and there is a one-second geometric proxy that says why.

**The proxy.** On the ten fine nodes the LP verdict tracks `area_open`, the area of A148's
certified-non-blocked feasible-centre set with all four cores removed: every node with
`area_open ≤ 1.92` gave a converged kill or a `τ = 7.0` boundary, and the two ALIVE nodes are the
two with `area_open ≥ 4.4` (Trump 4.45, the corner-hugging `(0,0,0)⁴` 5.07). The threshold is
`area_open ≈ 2`. Measured along the ladder (`results/ladder150.json`, 6 random states each):

| cover | cells N | `a_exact` median | `area_open` min / median / max | LP verdict |
|---|---|---|---|---|
| 2×2 × 2 | 8 | 0.0482 | 5.09 / 5.42 / 5.60 | (not run — far above threshold) |
| 2×2 × 3 | 12 | 0.0617 | 4.46 / 4.73 / 4.88 | (not run) |
| 3×3 × 3 | 27 | 0.1771 | 2.90 / 3.08 / 4.35 | **5 solved: η +1.88, +1.96, −0.0000, −0.56, +0.21 — 0 converged kills** |
| 3×3 × 4 | 36 | 0.1788 | 2.62 / 3.19 / 3.80 | above threshold |
| 4×4 × 4 | 64 | 0.2461 | 1.49 / 2.42 / 3.96 | straddles |
| 6×6 × 3 | 108 | 0.2913 | 1.55 / 1.86 / 2.68 | below threshold |
| **6×6 × 6 (the band)** | **206** | **0.3192** | **1.34 / 2.00 / 2.57** | **5 converged kills of 10** |

The first cover whose median `area_open` falls under the threshold is **6×6 positions × 3 tilt
windows, N = 108 → 15 266 858 D4 orbits → ≥ 424 000 CPU-h at 100 s a node**. That is 35× the
interior tree even in the product's best configuration, and the true fine cover is 440× worse
again.

**The floor is already two orders too high.** The fastest converged, verifier-PASS kill measured
was **8.7 CPU-s**. Even if EVERY one of the 189 934 236 fine states died at that rate the fine
product would cost `189 934 236 · 8.7 s = 4.6·10⁵ CPU-h`; at the measured 63 % kill rate and the
alive nodes' 240 s cap it is `≈ 5.3·10⁶`. No LP kill rate, however good, brings the fine product
under `docs/budget.md`'s 12 000.

**Adaptive refinement does not rescue it.** The product's parameter space is 4 × 3 = **12-dimensional**
(three degrees of freedom per conditioned square) against the interior root's 3, so each bisection
level multiplies the node count by 8 per corner refined, and reaching `a ≈ 0.32` from `a ≈ 0.05`
takes ~2.6 halvings on each of the 12 axes. That is the whole difference between this root and
A38's: the interior tree pays 216 · 8^(d−1) with d = 2–3; the product pays `N⁴/8` with `N` already
inside the exponent four times.

**What A150 actually buys, then, is not a tree — it is a mechanism.** Four cores at four corners is
the first hypothesis in the k0 lab that moves `η` by a whole unit at level 1 (A143: −0.04 at one
corner, −0.08 at two on the same corner; A150: −1.0 to −6.0 at four, with converged, verifier-PASS
kills at 27–92 CPU-s each). The right consumers are:

1. **(R6) as an LP ROW in every k0 node, interior tree included.** No square meets two corner
   boxes, so the four corner-meeter families are disjoint and
   `Σ_{Q meets some B_c^w} μ(Q) ≥ 8` — a single row of weight 8, not the four separate
   `≥ 2` rows A115 tried (which killed nothing). The row is valid for every packing and needs no
   branching at all.
2. **A partial product**: condition four corners only where the interior tree's own support already
   localises them (A143 Rule III fired on 2 of A115's 12 converged-alive cells with the BL crowd
   alone; with four corners the same test has four times the reach and costs no LP).
3. **The `(3,2,1)⁴` family as a named (C) leaf**: `τ = 1.0` at budget 7 says four intruders sitting
   at ~1.62 from their corners at 15–30° leave room for at most ONE further square — a
   verifier-certified statement that holds for a whole 12-dimensional box and is worth having in
   `k0_route.md` on its own.

**Verdict.** The four-corner product is **sound, canary-clean, and by a wide margin the strongest
level-1 LP in the k0 lab (63 % converged kills against A143's 0 %) — and it is still priced out**,
at ≥ 4.6·10⁵ and realistically 5.3·10⁶ CPU-h at the resolution where it decides, against the
interior tree's 12 000. The PI's premise — a *narrow* admissible band per corner — is what fails:
the band is 206 of 216 cells, the geometry cuts only 15.6 % of the product, and every counting leaf
(guard lines, disk bound, separation bound) fires on nothing. What survives the attempt is the
mechanism, not the tree: **four spread cores buy a whole unit of η where two cores at one corner
bought 0.04**, and that belongs in the existing 3-dimensional trees as (R6)'s row and as the named
`(3,2,1)⁴` (C) leaf, not in a 12-dimensional product cover.

## 7. Files

`code/frames150.py` (frames + D4), `band150.py` (T1), `prod150.py` (T2: pair matrices, transfer-
matrix counting, disk/separation/guard leaves), `coarse150.py` + `ladder150.py` (the coarseness
ladder), `canary150.py` (Trump), `lp150.py` (T3), `pick150.py`, `draw150.py`, `report150.py`,
`verify150.py` (independent re-checks: D4 closure, (R6), transfer-matrix vs brute force, Burnside
vs explicit orbits, the band recomputed, the frames — **ALL_OK**, `results/verify150.json`).
Results in `results/`, certificates in `certs/`, 20 panel-G pages in `figs/`, logs in `logs/`.
No file outside `attempts/A150-four-corner-product/` was written (the brief's read-only rule), so
`REGISTRY.md`, `docs/budget.md` and `LOG.md` still need A150's rows added by whoever owns them.
