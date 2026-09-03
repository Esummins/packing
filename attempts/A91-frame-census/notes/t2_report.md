# A91 T2 — the frame census, exactly (Opus chore) — 2026-09-03

Labels: **EXACT** = closed-form product formula in exact integer combinatorics,
evaluated in float64 (relative error < 1e-12; the formula was validated against an
independent 4-fold brute-force enumeration, `logs/validation.log`, 8/8 shapes,
max rel. dev. 2e-11 = float noise). **MC(±)** = Monte-Carlo with its 1σ/95% band.
**EXTRAPOLATED** = MC ratio applied to an EXACT count.

Code `code/{geom91,frame91,census91,real91,ablate91,run_t2t3,canary91,pilot91}.py`.
Raw: `results/{canary91.json,census91_labelled.json,ablation91.json,census91.json,
samples91.jsonl,t3pilot91.json}`. Logs: `logs/`.

## 0. Verdict in one line

The census is **finite and astronomically large**: 5.7e28 L1 frames mod G, ~1e40 at
L2, and the box-level geometry (R6) kills 99.7% of them at 3.8 ms each — but the
0.3% that survive include the archetype, which no box test closes. **A90-G1 is
confirmed numerically: the combinatorics constrain nothing (all filters together
cost less than one order of magnitude at L1), and the frame-census route to
¬RES(4) loses to A85's tree by ~28 orders of magnitude.**

## 1. Canaries (all PASS; run before any counting)

| canary | verdict | detail |
|---|---|---|
| **C1** Trump-with-2-crowds | **PASS** — survives R1, R2, R3, R5 and sign-consistency | see below |
| **C2** Trump itself | **PASS** — absent | open intruders per corner (BL,BR,TR,TL) = (1,1,2,1), not K0-BLOCKED |
| **C3** the 4 exact-K0-BLOCKED endpoints of `k0dir87.polish` | **PASS** — every applicable constraint of `frame_census.md` §2 holds on the real geometry | no violation at any of the four |

**C1, in full.** Built by code from `attempts/A03-upper-reconstruct/trump11_exact.json`
(60 digits, s = 3.877083590022814) with A90's geometry (`t3_90.corner_state /
all_pair_contacts / wall_contacts / cluster / depth_arg`).

Roles / types / masks (argmin type stable across the whole tolerance ladder
1e-11 … 1e-3):

| sq | corner | μ_c | τ | ω |
|---|---|---|---|---|
| 0 | BL | 0 | D | {B,L} |
| 1 | BL | **1.000000000000 (TANGENT)** | **X** | {B} |
| 2 | BR | 0 | D | {B,R} |
| 8 | BR | **1.000000000000 (TANGENT)** | D | {} |
| 5 | TR | 0 | D | {R,T} |
| 9 | TR | **1.000000000000 (TANGENT)** | D | {} |
| 4 | TL | 0.844525275673 | Y | {L} |
| 6 | TL | 0.831679010450 | X | {T} |
| 3, 7, 10 | FREE | — | — | {L}, {}, {R} |

pattern (2,2,2,2; f = 3). Note for the record: the spec lists sq8 among "the exact
open intruders"; it is **tangent** (μ_BR = 1 exactly), as are sq1 and sq9 — i.e.
exactly the three squares `frame_census.md` §6 promotes. sq4 = case (Y) and sq6 =
case (X) agree with A90's stored `t3_trump.json` (`K = {e_y}` resp. `{e_x}`).

13 slots and their minimal columns (BFS from Q over the cluster's pressing edges
to the first admissible terminal):

| slot | e (container) | column | terminal |
|---|---|---|---|
| 0x | (+1,0) | 0–1–8 | 8 (I) |
| 0y | (0,+1) | 0–3–7–4 | 4 (I) |
| 1x | (+1,0) | 1–8 | 8 (I) |
| 2x | (−1,0) | 2–8–1 | 1 (I) |
| 2y | (0,+1) | 2–8–7–9 | 9 (I) |
| 4y | (0,−1) | 4–7–8 | 8 (I) |
| 5x | (−1,0) | 5–9–6 | 6 (I) |
| 5y | (0,−1) | 5–9–7–8 | 8 (I) |
| 6x | (+1,0) | 6–9 | 9 (I) |
| 8x | (−1,0) | 8–1 | 1 (I) |
| 8y | (0,+1) | 8–7–9 | 9 (I) |
| 9x | (−1,0) | 9–6 | 6 (I) |
| 9y | (0,−1) | 9–7–8 | 8 (I) |

R1 PASS, R2 PASS, R3 PASS, R5 PASS, sign-consistency PASS; R4: 13 I-terminals,
**13/13 with the mutual reverse slot present**, 0 PLATEAU-flagged (both ends
D-type, so the Lemma K rates are not both 1). #L1 refinements of C1's L0 =
12 002 256 000; #L2 refinements of C1's L1 = 2 205 000 000.

**C3 detail** (their own side s ≈ 4.000, R5 run at that side):

| tag | s | pattern | slots | anchored (W or I) | columns extracted | R1/R2/R3/R5/signs |
|---|---|---|---|---|---|---|
| s0380 | 4.000000 | (2,2,2,2) | 12 | 11 | 11 | all PASS |
| s0076 | 4.000004 | (2,2,2,2) | 12 | 7 | 7 | all PASS |
| s0380′ | 4.000007 | (2,2,2,2) | 12 | 8 | 8 | all PASS |
| s0259 | 4.000012 | (2,2,2,2) | 12 | 6 | 9 | all PASS |

Unanchored slots (1, 5, 4, 6 of 12) are expected — these are not Ψ-minimal
minimisers. (The extracted-column count can exceed the T90 anchoring count
because `t3_90.intruder_anchored` skips squares at depth ≤ 1e-9, i.e. tangent
I-terminals, while the frame's F3(b) rule admits them.)

## 2. L0 and L1, exactly

Colours: open intruder (corner, τ, ω ⊆ c's two walls) = 48; tangent home square
(corner, τ, ω ⊆ c's walls, |ω| ≤ 1) = 36; free (|ω| ≤ 1) = 5. 89 colours, 11
squares, 165 shapes (o_c ≥ 2, o_c + t_c ≤ 5, Σ = 11), 35 ordered role patterns.

| level | labelled (EXACT) | mod G, exact lower bound labelled/\|G\| | MC(±) orbits |
|---|---|---|---|
| **L0** | **1.040303e19** | 1.248822e16 | 1.877e16 ± 5.2e14 |
| **L1** | **1.557786e32** | **5.725857e28** | 1.275e29 ± 1.3e28 |

with G = (∏_c S_{n_c} × S_f) × D4, |G| = 768 … 7680 by pattern. Trivial-stabiliser
share of the sample: 61% at L0, **97% at L1** — so the true orbit count is within a
few percent of labelled/|G|, and the MC point value's excess over it is
importance-weight variance, not stabiliser mass. **Headline: L1 ≈ 5.7e28 orbits
(exact lower bound), certainly < 1.3e29.**

Without the tangent flag (open intruders + plain free squares only): L0 =
4.684441e17, L1 = 1.259410e32 — tangency costs a factor 22 at L0 and only 1.24 at
L1 (tangent squares are cheap terminals, so they mostly cancel).

Per-pattern table: `results/census91_labelled.json`. The (2,2,2,2) pattern is 41%
of L0 but only 0.6% of L1; the L1 count is dominated by the crowded patterns
(3,3,3,2)-type: 1.26e31 labelled each.

### Ablation (all EXACT)

| filter set | L0 labelled | L1 labelled |
|---|---|---|
| roles only, no mask filter | 3.409746e19 | 4.501938e36 (`frame_census.md` §3's 7-per-slot bound) |
| + ≤1 both-wall home square per corner, ≤5 home squares per corner | 2.394063e19 | 9.295855e32 |
| + per wall ≤3 squares, per wall ≤1 free square (**full R1**) | **1.040303e19** | **1.557786e32** |

so the **whole combinatorial filter buys a factor 3.3 at L0 and 2.9e4 at L1**
(the 2.9e4 is almost entirely R2 folded into the product formula, i.e. the honest
terminal count 5–7 instead of the §3 bound 7). Per-wall ≤3 alone: ×0.43 at L0,
×0.168 at L1. **The dominant constraint is not combinatorial — it is R6 (§4).**

### R3 is VACUOUS at L1 [finding, proved]

Lemma F4's "every W-column has a middle" cannot kill an L1 frame. For a slot at c
with far wall w, the middles are the squares that are not home squares of the two
corners of the wall *opposite* w (= c and CROSS(c,axis)) and do not touch w. The
two corners **of w** carry ≥ 4 home squares (K0-BLOCKED: n ≥ 2 each) while w
carries ≤ 3 squares (F2(iii)), so at least one home square of w's corners misses
w and is an admissible middle. Hence mid_w ≥ 1 always, and the L1 product formula
is exactly A(slot) = W_w + Xh_w with no R3 factor. This is a (small) sharpening of
`frame_census.md` §2 worth recording: **Lemma COL gives no L1 kill; it only bites
at L2/L3.**

## 3. L2 and L3

MC over 400 uniform L0 draws (exact per-shape L0 weights; colours by rejection),
one uniform terminal assignment each, importance-weighted by the exact per-L0 L1
count so the statistics are uniform over L1.

* **L2** (L1 + the first link N₁ per slot, with the R5 box tests on the link):
  E[#L2 per L1] = 2.44e8 ± 2.70e8 → **L2 labelled ≈ 3.8e40, bracket [1e39, 1e41]**
  — MC(±), high variance (the per-frame L2 multiplicity spans 1e5…1e12).
  Mod G that is ≈ 1e37 orbits. Exact enumeration is out of the question (the spec's
  1e7 threshold is exceeded by 30 orders of magnitude), so L2 is a bracket.
* **L3** (full sign-consistent columns): exact upper bound from the MC =
  **1.56e59** chain systems labelled; the sign-consistency filter is the binding
  one — for the median frame **0 of 20** random full chain systems is
  sign-consistent, giving a weighted point estimate 5.4e50 (EXTRAPOLATED, one
  significant figure at best). Bracket: **L3 ∈ (0, 1.6e59]**, with C1 an explicit
  witness that the stratum is non-empty. Capped-DFS fraction: chain enumeration
  hit the 4000-chain cap on 0% of slots (columns are ≤ 5 members by construction).

## 4. R6 realisability, and the corner-sharing distribution

R6 = interval-linear relaxation in A88's `p88_triage` style, rebuilt for A91 frames
(`real91.build_rows`): 23 LP variables (22 centres + s), tilts as bins on [0°,45°],
sound rows for containment, wall masks, corner intrusion (home square meets c's
closed unit box), the Lemma K **argmin-side type rows** — derived and encoded as,
in c's frame, X ⇒ y − x ≤ −cos θ_hi (0 if the bin contains θ = 0), Y ⇒ x − y ≤
−cos θ_hi, D ⇒ |y − x| ≤ cos θ_lo (from the leftmost/lowest vertex of a tilt-θ unit
square) — and Lemma F6 link rows (|c_N − c_M| ≤ √2 on 8 supporting directions,
(c_N − c_M)·e ≥ −1). Margin form, HiGHS; infeasible ⇒ the frame has no realisation.

* **kill rate 315/316 = 0.9968, 95% CI ±0.0062**, at **~4 ms/frame** (one root LP).
* ⇒ **realisable at L2 ≈ 3.8e40 × 0.0032 = 1.2e38** frames labelled
  (EXTRAPOLATED; the R6 CI alone allows 0 … 2.4e38, and the L2 bracket widens it to
  [1e36, 1e39]).
* The **C1 archetype is NOT killed** by R6 (margin +0.1036) — as required.

**Corner sharing (R6 sample, n = 316):** every single frame has **all 6 corner
pairs** sharing a column member (distribution: {6 pairs: 316/316}); mean number of
FREE squares acting as a column middle = **0.33**. So the sharing is not carried by
the three free squares at all — it is carried by the corner crowds themselves
(mean 6 squares lie in the columns of ≥ 2 corners). This is A90-G1 made
quantitative: with 11 squares the four corners' columns *must* interpenetrate, and
the census does not care.

## 5. THEORY ISSUES

1. **[resolved in code, worth a doc line] R5's free-square box.** `t2_spec.md` R5
   says "FREE: outside every c + [1/2, 3/2)² (plus shape) — use the bounding box,
   as A88 did, and flag it". Using the *bounding box* as the forbidden region is
   **not sound**: the true forbidden set {centre : dist(centre, [0,1]²) < 1/2} is
   strictly inside [1/2,3/2)², so forbidding the box over-kills. I implemented the
   sound version (a grid-sound test that some point of the centre box has
   dist ≥ 1/2 from [0,1]² in every corner frame). No count changes materially
   (the free box is large), but the doc should say "plus shape, not its box".
2. **[structural, load-bearing] the archetype is 100% (I)-anchored.** All 13 of
   C1's minimal columns terminate at an (I)-terminal, four of them with only 2
   members (1x, 6x, 8x, 9x), and all 13 have their mutual reverse slot present.
   Lemma COL's ≥3-member clause — the brief's intended counting lever — therefore
   **never applies to the archetype**, and R3 cannot touch it at any level. Any
   ¬RES(4) proof must beat *mutual corner-to-corner anchoring*, i.e. **Lemma
   PLATEAU must be made load-bearing** (it is currently `[C]`, "well-foundedness of
   iterated slides is unproved", and the census deliberately does not use it).
   This is the single most important thing T2 measured.
3. **[bookkeeping] spec role list.** C1's sq8 is described as an open intruder at
   BR; it is tangent (μ = 1 exactly). `frame_census.md` §6's role list (BR{2,8}) is
   right; the `t2_spec.md` phrase "the exact open intruders {…8: BR…}" is not.

No combinatorial filter R1–R5 was found to be wrong, and no canary needed a filter
to be disabled.

## 6. Price (see also `notes/t3_report.md`)

realisable-at-L2 count × per-frame cost = 1.2e38 × 3.8 ms ≈ **1.3e32 CPU-hours**
against A85's measured 3 200–7 000 CPU-h. The frame-census route **loses by ~28
orders of magnitude** at L2, and by more at L3. It could only win if the geometry
were applied at L0 (1.9e16 orbits — still 12 orders too many) or if the census were
quotiented by something far stronger than G. The A90 §6 verdict stands: ¬RES(4) has
to be paid as a **SelForm (C) leaf inside A85's tree**, not as a census.
