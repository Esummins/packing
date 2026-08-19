# A12-region-rank-pilot — region-rank cuts (I-L8) against the mid-tilt integrality gap of the box LP

Owner: LP agent 3 (postdoc, LP / combinatorial optimisation). 2026-08-18. Status: **done-negative** (pilot; ~2.5 h).

Question (I-L8, advisor after A10): the orientation-restricted measure LP for the mid-tilt box
Θ_B = [0°,2°] ∪ [32°,36°] is ALIVE at s = 3.85–3.87 with τ*_B = 11.000 exactly, through a 4-fold-symmetric
fractional packing (weights 1, ½, ¼) although no packing with those orientations is known below 3.89.  Do
region-rank cuts  Σ_{Q : c(Q) ∈ R} x_Q ≤ k(R)  (k(R) = max number of pairwise-disjoint unit squares with centres in
R, orientations in Θ_B, inside the container; dual: λ_R ≥ 0, coverage μ(Q) + Σ_{R ∋ c(Q)} λ_R ≥ 1, objective
μ(total) + Σ λ_R k(R)) kill this box?

**TL;DR — NO, and for a structural reason, not for lack of trying.**
(i) The weight-11 fractional packing is "locally integral": every C4-symmetric region has an INTEGER load
(the orbit weights are 4, 2, 1, 1, 1, 1, 1 at 3.85 and 4, 2, 1, 1, 1, 1, 1 at 3.86), and for every macroscopic region
we tried (centre discs r = 0.6–1.0, annulus, side zones, corner zones, tilted-family blobs, and their unions:
corners+disc, sides+disc, blobs+disc, ...) an explicit packing REALISES x*(R) ≤ k(R) — the cut is tight or slack,
never violated (§2, table).  The structure is "4 corners + 4 sides + 3 interior = 11"; integrally 4+4+1 = 9 or
4+2+3 = 9 or 0+8+1 = 9 are all realisable, i.e. every proper sub-union of the zones is fine and only the GLOBAL
count is wrong.  A region cut cannot express "if the corners and the sides are full then the interior holds ≤ 1" —
that is a conditional (case) statement.
(ii) Lemma (§3): if k(R) is certified by the sub-LP (rows restricted to c(Q) ∈ R, the recursion proposed in I-L8),
then a region cut can only be violated by the current fractional packing x* if x*(R) is NON-integer, because x*
restricted to R is dual-feasible for the sub-LP, so τ_R ≥ x*(R) and the sub-LP certifies at best k(R) ≤ ⌈τ_R⌉−1
≥ ⌈x*(R)⌉−1 ≥ x*(R) for integer x*(R).  With integer loads on all symmetric regions, LP-certified region cuts are
dead on arrival for this structure.
(iii) The only violated cuts are the FINE ones: the rank inequality of the conflict graph of the support
(x*(S) = 7 vs α(S) = 6 for the 24–28 fractional placements; 11 vs 10 for the whole support; max violation 1.5 over
sub-families at 3.85), certified combinatorially (k(R) ≤ α(G_robust) for a union of small (c,θ)-boxes with
rigorously-robust pairwise overlaps).  These certify only for boxes of half-width ρ ≤ 0.05 (θ ± 1–2°); at ρ ≥ 0.08
the robust graph loses edges and α jumps to 8 ≥ 7 (§4).  Adding them to the LP: τ stays 11.000000, λ_R = 0 in every
one of 10 + 10 + 3 rounds (s = 3.86 two variants, s = 3.85): the LP simply slides the support by 0.06–0.33 per
round (side uprights slide along the wall or move 0.2 off it, tilted squares move radially/rotate) — a
continuum escape.  Even an UNCERTIFIED test with 28 boxes of half-width 0.3 (k = 6) is escaped (§4).
(iv) Contrast (bonus, §5): the CONDITIONAL LP "the four corner squares [0,1]² are in the packing (rows = placements
disjoint from them, budget 7)" gives τ = 7.000 (alive: 4 sides + 3 interior survive), and "corners fixed AND no
square centred in the four side zones" gives τ = 5.000 < 7 (dead).  So the structure IS killed by case splits of
I-L6 type (fix a square / exclude a zone), not by unconditional region counts.
Verdict for the PI (§6): region-rank cuts do NOT close the mid-tilt gap; the campaign "angle boxes × region cuts"
stays in the 10⁶+ class (per box: hundreds–thousands of rounds of 10–40 s LPs with no sign of termination).  The
right second killer is a case-LP (I-L6) with "fix-a-square in a (c,θ)-box" branches whose YES branch removes the
overlapping placements' rows and lowers the budget to n−1 — the two conditional LPs above (13 s each) show that
this mechanism kills the 8+3 structure at depth ≈ 4–8; a rough count for the mid box is 10³–10⁴ conditional LPs
per angle box (§6).

## 1. Task 1 — the alive box at s = 3.86 reproduced and dissected

`lp_measure_box.py` (copy of A10) `--s 3.86 --theta_box "0-2,32-36" --fine`: τ*_B = 11.000000, ν = 11.000000,
converged (row AND column oracle empty) in 96 s, 3085 rows, 1614 orbits, 21 atoms > 0, packing support 8 orbits.
Fractional packing (`results/mid_up2_32_36_s3.86.json`, C4 images in `results/analysis_s3.86.json`,
plot `plots/mid_up2_32_36_s3.86.png`; also 3.85 from A10: `plots/mid_up2_32_36_s3.85.png`):

| family | orbit rep (cx, cy, θ) | orbit weight y | images × weight | zone |
|---|---|---|---|---|
| corner uprights | (3.36, 3.36, 0°) | 4 | 4 × 1 | corners |
| side uprights, 2 positions × 2 tilts | (3.36, 2.324, 0°), (3.338, 2.336, 1°), (3.356, 1.603, 0.5°), (3.339, 1.626, 1.5°) [3.85: (3.35, 2.348, 0°) with y = 2 + two ¼ orbits] | 1, 1, 1, 1 | 16 × ¼ | 4 side zones, 1 per side |
| tilted pinwheel | (2.460, 2.541, 33°), (2.476, 2.530, 32°) [3.85: 32.5°, 34°] | 1, 1 | 8 × ¼ | interior, radius ≈ 0.81 from centre |
| interior uprights | (2.355, 2.356, 0.5°) | 1 | 4 × ¼ | interior, radius ≈ 0.6 |

Sum 4 + 4 + 2 + 1 = 11.  Loads: each corner zone 1, each side zone 1 (½ + ¼ + ¼ at 3.85; 4 × ¼ at 3.86), interior
disc (r ≤ 0.85) 3, tilted family 2, interior-upright family 1.  All orbit weights are integers ⇒ every
C4-symmetric region has an integer load.

Cheat / integrality-gap witness (`analyze.py`, exact SAT overlap test + CP-SAT max independent set):
* fractional part S (24 placements at 3.85, 28 at 3.86): Σ x = 7.000, α(S) = 6 (e.g. 4 side uprights + 1 tilted +
  1 interior upright), heaviest overlapping PAIR sums to 0.75 (3.85) / 0.50 (3.86) — no pair or small clique is
  saturated (as in A07 §5);
* whole support: Σ x = 11, α = 10;
* the finest possible (c,θ)-region cut = the most violated rank inequality of the conflict graph: at 3.85 a
  24-placement family T (4 corners + 20 fractional) with x(T) = 9.5, α(T) = 8 → violation 1.5; at 3.86 max
  violation 1.0 (several T).  Robustness: the α(S) = 6 conclusion survives deleting all overlap edges of depth
  ≤ 0.10 (`depth_profile.py`: 90 edges of depth > 0.1, α = 6; at depth > 0.15 α = 8) — the conflict structure is
  robust to ≈ 0.05 displacements, not more.
* The pairwise-overlapping families: the four rotations of the tilted square form a 4-CYCLE (adjacent images
  overlap by 0.0002 only: du = 0.984 in the square frame — they are almost disjoint and CAN be made disjoint by
  moving 0.02, so k(blobs) = 4 ≥ 2), each tilted image overlaps the two neighbouring side uprights and one interior
  upright; the four interior uprights are pairwise overlapping (a K4 at ¼ = 1, integral); side uprights on one side
  overlap each other (two positions × two tilts, sum 1, integral).  So NO odd cycle at weight ½ — the ¼-weights make
  every local family integral; the deficit is global (11 vs α = 10).

## 2. Task 2 — candidate regions, x*(R) vs k(R)

k(R) methods: (a) incircle bound (points pairwise ≥ 1 apart) — far too weak here (disc r = 0.85 admits ≥ 4 points,
a 2.85 × 0.5 wall strip admits 6, side zone 2); (b) exact k(R) is a small packing problem; we computed rigorous
LOWER bounds k_lb(R) by realising packings (centres on a 0.1 grid in R, θ ∈ {0,1,2,32,…,36}°, exact overlap test,
CP-SAT max independent set, `geom.realise_k`) — a lower bound suffices to show a cut is NOT violated; (c) upper
bounds via robust-overlap graphs (§4) for fine box unions.  s = 3.86 (3.85 identical up to k_lb):

| R | x*(R) | k_lb(R) (realised) | violated? |
|---|---|---|---|
| centre disc r = 0.6 / 0.7 / 0.85 / 0.9 / 1.0 | 0 / 1 / 3 / 3 / 3 | 2 / 3 / 4 / 4 / 5 | no |
| annulus 0.65–0.95 (tilted family) | 2 | 4 | no |
| one side zone [0.5,0.75]×[1.2,s−1.2] | 1 | 2 | no |
| four side zones | 4 | 8 | no |
| four corner zones [s−1,s−0.5]² | 4 | 4 | tight, no |
| corners ∪ disc 0.85 | 7 | 8 | no |
| sides ∪ disc 0.85 | 7 | 9 | no |
| tilted blobs (discs r = 0.12 at the 8 tilted centres) | 2 | 4 (uprights at the pinwheel centres are disjoint) | no |
| blobs ∪ disc 0.85 | 3 | 4 | no |
| corners ∪ 3 sides ∪ disc (by hand) | 10 | ≥ 9 (4 + 3 + 2 uprights); 10 unknown | needs "no 10-packing avoiding one side zone" = full problem |
| everything | 11 | = the packing number itself | circular |

Reading: every region whose load is a proper part of the 4+4+3 structure is realisable; the only candidate cuts are
those containing (almost) everything, whose k(R) is the original question.  This is the precise sense in which the
mid-tilt fractional packing is not a "region" cheat but a global one.

## 3. Lemma: LP-certified region cuts cannot bite on integer loads

Let x* be a fractional packing of weight ≥ 11 feasible for the box LP (what τ*_B = 11 means).  For a region R the
I-L8 recursion certifies k(R) ≤ K by showing τ_R := min{μ(total) : μ(Q) ≥ 1 ∀ Q with c(Q) ∈ R, θ ∈ Θ_B} < K+1.
Since x*|_R is dual-feasible for that LP, τ_R ≥ x*(R).  The best certifiable K is ⌈τ_R⌉ − 1 ≥ ⌈x*(R)⌉ − 1, and the
cut is violated by x* iff K < x*(R).  If x*(R) ∈ ℤ then K ≥ x*(R): never violated.  If x*(R) ∉ ℤ a violation needs
τ_R < ⌈x*(R)⌉, i.e. the sub-LP must be tight within the fractional part of x*(R).  ∎
Consequences: (a) for the mid-tilt structure all C4-symmetric regions have integer loads, so symmetric LP-certified
cuts are useless; (b) asymmetric regions with fractional loads (e.g. R ⊃ 6 of the 8 tilted images: load 1.5) need
k(R) ≤ 1, false (k ≥ 2 trivially).  The lemma is why the recursion "k(R) by the same LP" cannot bootstrap itself.
Combinatorial certificates (robust overlap graphs, incircle) escape the lemma but only for small regions.

## 4. Task 3 — region cuts in the LP (`lp_region.py`), certified k via robust-overlap graphs (`make_regions.py`)

Implementation: `lp_region.py` = A10's LP + region columns λ_R (cost k(R), coefficient 1 in every row whose
placement lies in R; R = union of (c,θ)-boxes [x0,x1]×[y0,y1]×[θ0,θ1], C4-expanded or given explicitly); the row
oracle evaluates μ(Q) + Λ(Q): the exact per-θ arrangement search enumerates cells with μ < 1 (a superset), samples
centre + corners + 3×3 interior points, adds Λ, keeps violated ones; region-box boundary shells are sampled
explicitly (`shell_search`, 12×12 grid at θ0−δ, θ1+δ, θ0, θ1, mid); pattern-search refine uses μ + Λ.  Reports
τ = μ(total) + Σ k λ, μ(total), λ, and the dual loads x(R).
Certification of k(R) for R = ∪ boxes B_i of half-width ρ (centre, ∞-norm) × ±ρ_θ around the fractional support
(`make_regions.py`): boxes B_i, B_j are ROBUSTLY adjacent iff a witness point p lies in the interior of both squares
for ALL parameters in B_i × B_j (interval arithmetic in (cx,cy,θ), margin 1e-6; exact-rational version is a
5-line change of the verifier's box test); each box has centre diameter 2ρ√2 < 1 so it holds ≤ 1 square of any
packing (incircle); hence k(R) ≤ α(G_robust) (CP-SAT).  Results at s = 3.86 (fractional part, 28 boxes):

| ρ (centre) | ρ_θ | robust edges | α(G_robust) = certified k | x*(R) | violated |
|---|---|---|---|---|---|
| 0.01 / 0.02 / 0.03 / 0.04 / 0.05 | 1° | 90 / 90 / 90 / 86 / 82 | 6 | 7 | yes, by 1 |
| 0.03 | 2° | 90 | 6 | 7 | yes |
| 0.03 (all 32 incl. corners) | 1° | 90 | 10 | 11 | yes, by 1 |
| 0.08 / 0.10 | 2° | 64 / 44 | 8 | 7 | no |
| 0.15 / 0.20 | 2° | 20 | 12 | 7 | no |

Iterated cutting (`iterate.py`: box the current fractional support with ρ = 0.05, certify, add as a NEW region
variable, re-solve warm, `--fine`; logs `logs/iterate_386*.log`, `results/it386*_log.json`, `results/it386*_rd*.json`):

| s, variant | rounds | τ after each round | λ (all rounds) | support moved per round (max / mean) | LP time per round |
|---|---|---|---|---|---|
| 3.86, fractional part (24–40 boxes/round, k = 6 or 10) | 10 | 11.000000 ×10 (all converged, maxcov 1.000) | 0 | 0.07–0.27 / 0.01–0.10 | 9–40 s |
| 3.86, whole support (20–88 boxes/round, k = 10) | 9 | 11.000000 ×9 | 0 | 0.06–0.33 / 0.01–0.12 | 10–101 s |
| 3.85, fractional part | 3 | 11.000000 ×3 | 0 | 0.10–0.28 / 0.02–0.12 | 7–22 s |
| 3.87 (A10's non-converged 92-placement support) | — | robust α = 12 ≥ x*(R) = 11: cut not even violated | | | |

What moves: the side uprights slide along the wall (e.g. (0.504, 2.258, 0.5°) → (0.5, 2.324, 0°), 0.067) or move
0.2 OFF the wall ((3.149, 1.525, 0°) at ρ = 0.3), the tilted pinwheel changes radius (0.81 → 0.32–0.9) and tilt
(32°–33°), new ¼-orbits appear; τ = 11 is re-established each round with x(R_new) exactly = k(R_new).  Mechanics
check: an UNCERTIFIED region with 28 boxes of half-width 0.3 and k = 6 (`results/reg_TEST_r0.3.json`) is escaped
too (τ = 11.000, λ = 0, x(R) = 6.0): the family of weight-11 fractional packings fills essentially the whole
"corner + side-band + interior-disc" volume; boxing it means R ≈ everything, where k(R) is the problem itself.
Cost per round: 10–100 s LP + 5–30 s certification; the escape manifold has ≥ 3 free continuous parameters of
extent 0.5–0.8 each vs a certified box size ≈ 0.1 ⇒ ≥ 10²–10³ rounds per angle box even if the process terminated
(it shows no sign of doing so: 10 rounds, τ − 11 = 0 to 1e-9).

Task 4 (certificate) is void: the box never died.  (The verifier extension is straightforward: in
`verify_measure_restricted.py`, a (t, cx, cy)-box is also discharged when it is provably inside a region box and
its rational mass ≥ 1 − λ_R; the k(R) proof would be the robust-graph α with exact-rational witness containment.)

## 5. Bonus — the CONDITIONAL LP kills the structure (what region cuts cannot express)

`lp_fixed.py`: rows only for placements interior-disjoint from fixed squares (and/or with centres outside excluded
zones), remaining budget n_rem (case-LP branch, I-L6 flavour), C4, s = 3.86, Θ_B, warm from the box result:

| hypothesis | budget | τ | verdict |
|---|---|---|---|
| the four corner unit squares [0,1]² (+images) are in the packing | 7 | 7.000 (conv, 13 s; dual = 4 side + 3 interior) | alive (as the lemma predicts: 4+4+3 minus 4) |
| corners fixed AND no square centred in the four side zones [0.5,0.75]×[1.2,s−1.2] | 7 | 5.000 (conv, 12 s) | DEAD by 2 |
| (by hand) corners + four side squares fixed | 3 | 1 (the 1.85² hole is pierced by one atom) | dead |

So the 8+3 structure dies as soon as the count becomes CONDITIONAL on where squares are; the mixed branches
(some sides occupied by a square whose (c,θ) lies in a box, others empty) are asymmetric LPs (need a C1 mode of
the row oracle — not in this pilot) with budgets 4–6 against surviving fractional weight ≈ 3 (interior) + partial
sides — expected dead, but each YES branch must be refined until the "shadow" of the box (placements disjoint from
SOME square of the box) is small: side zone volume ≈ 0.25 × 1.4 × 2° vs boxes 0.05 × 0.05 × 1° ⇒ ~300 boxes per side.

## 6. Verdict for the PI

* Region-rank cuts (I-L8) do NOT close the mid-tilt integrality gap.  Not a resolution problem: the weight-11
  fractional packing has integer load on every symmetric region and a realising packing on every macroscopic
  region tried; the lemma of §3 forbids LP-certified cuts from biting on integer loads; combinatorially certified
  fine cuts (ρ ≤ 0.05) are violated by exactly 1 but the LP escapes by sliding (0.06–0.33 per round), 22 rounds at
  3.85/3.86 with τ = 11.000000 and λ = 0 throughout.
* Cost: LP + cuts converges in 10–100 s per round (fast — the machinery is cheap), but the number of rounds per
  angle box is ≥ 10²–10³ with no termination guarantee ⇒ campaign "angle boxes × region cuts" is 10⁶+ (NOT
  viable), and it does not even reduce the 10⁶–10⁹ multiset count of A10 because the mid-tilt band stays alive.
* What does work on this structure: conditional counts = case-LP (I-L6) with "fix-a-square-in-a-box / exclude-a-zone"
  branches (§5: 13 s per LP, kills at depth ≈ 4–8 for the symmetric prototypes).  Rough size for ONE mid-tilt angle
  box: C4-symmetric root cases (corners occupied or not: 2–5 cases via the corner box) × side cases (0–4 occupied,
  each YES refined to ~10² (c,θ)-boxes with a mixed-symmetry LP) ≈ 10³–10⁴ conditional LPs of 10–60 s ⇒ hours per
  angle box on 6 cores; times the number of alive angle boxes (A10: the mid-tilt band at 2° resolution is ~10² boxes
  after union-monotonicity) ⇒ 10⁵–10⁶ LPs ≈ weeks — borderline; a C1-mode LP and a proper "shadow" (box-of-fixed-
  square) row filter are the prerequisites.  Recommendation: pilot the asymmetric conditional LP (C1 row oracle,
  YES-branch = rows disjoint from SOME square of a (c,θ)-box, budget n−1) on the mid box at 3.86 before any campaign.
* Side products: `geom.py` (vectorised exact SAT overlap, CP-SAT MIS, region realisation), `analyze.py` (support
  dissection, rank-inequality violation search), `depth_profile.py`, `make_regions.py` (robust-overlap certification),
  `lp_region.py` (region dual variables in the box LP), `iterate.py`, `lp_fixed.py` (conditional LP).

## 7. Files

`lp_measure_box.py` (A10 copy), `verify_measure_restricted.py` (A10 copy, unused), `geom.py`, `analyze.py`,
`depth_profile.py`, `make_regions.py`, `lp_region.py`, `iterate.py`, `lp_fixed.py`;
`results/mid_up2_32_36_s3.86.json` (+ `_state`), `results/mid_up2_32_36_s3.87.json` (fresh converged run, see §8),
`results/analysis_s3.85.json`, `results/analysis_s3.86.json` (images, α, rank violation, region table),
`results/regs_386_r*.json` (regions + certified k + witnesses), `results/reg_386_r0.05.json`, `results/reg_386_r0.03_all.json`,
`results/reg_TEST_r0.3.json`, `results/it386*_rd*.json`, `results/it385_rd*.json`, `results/it386_log.json`,
`results/it386all_log.json`, `results/it385_log.json`, `results/cond_corners_s3.86.json`,
`results/cond_corners_noside_s3.86.json`; `plots/mid_up2_32_36_s3.85.png`, `plots/mid_up2_32_36_s3.86.png`,
`plots/reg_386_r0.05.png`, `plots/reg_TEST_r0.3.png`; `logs/`.
Reproduce: `python lp_measure_box.py --s 3.86 --theta_box "0-2,32-36" --fine --out results/mid_up2_32_36_s3.86.json`;
`python analyze.py results/mid_up2_32_36_s3.86.json --regions --plot`; `python make_regions.py results/mid_up2_32_36_s3.86.json --rho 0.05 --out results/regs_386_r0.05.json`;
`python lp_region.py --s 3.86 --theta_box "0-2,32-36" --regions results/regs_386_r0.05.json --warm results/mid_up2_32_36_s3.86.json --fine --out r.json`;
`python iterate.py --s 3.86 --start results/mid_up2_32_36_s3.86.json --rounds 10 --rho 0.05 --tag it386`;
`python lp_fixed.py --s 3.86 --fixed corners --exclude side --n_rem 7 --out results/cond_corners_noside_s3.86.json`.

## 8. Addendum — s = 3.87 (fresh converged run)

`lp_measure_box.py --s 3.87 --theta_box "0-2,32-36" --fine --warm results/mid_up2_32_36_s3.86.json`: τ*_B = 11.000000,
converged in 33 s, support 11 orbits / 44 images, all weights ¼ (the corner squares themselves split into two
¼-orbits (3.36,3.37)/(3.37,3.36); side uprights at (3.34,2.35,1°), (3.37,2.33,0°), (3.21,1.50,0°) [0.16 off the wall],
(0.66,2.37,0°); tilted 32–32.5° at radii 0.44 and 0.87).  Region rounds (`iterate.py --tag it387b`, ρ = 0.05):
round 0: 44 boxes, certified k = 10 vs x* = 11 → after re-solve τ = 11.000000, λ = 0, x(R) = 7.5, support moved
0.24 max; round 1: 24 boxes k = 6 vs 7 → τ = 11.000000, λ = 0, x(R) = 6.0 (moved 0.02: re-weighting inside the
family suffices); round 2: 32 boxes k = 10 vs 11 → τ = 11.000000, λ = 0.  Same escape as at 3.85/3.86.
(A10's earlier non-converged 3.87 solution with a 92-placement support was not even robustly violated: α(G_robust) = 12.)
