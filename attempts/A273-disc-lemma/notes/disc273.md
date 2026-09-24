# A273 — the DISC LEMMA is FALSE; the DROP LEMMA replaces it, has a box-valid test, and is being certified outside the corner θ, φ ≤ 5° (2026-09-23)

Tags as A272: [T] proved, [T-computed] finite computation with its own check, [M] measured, [C] conjecture, [F] false.
Code `attempts/A273-disc-lemma/code/`, results `results/`, certificates `certs/`, page
`docs/residue_map/campaigns/A273-disc-lemma/disc_lemma.svg`.

## 0. Verdict

* **[F] A272's DISC LEMMA (strip_jam.md §5, distance form) is false on H1–H3** — `witness273`, every test in
  Fractions: h_u = 17/20, h_v = 199/200, tan(θ/2) = 7/100 (θ = 8.01°), X_low = 211/100, φ = 0, A with lowest vertex
  (11/10, 0) and tan(α/2) = 1/18, side 387/100.  All fourteen H1–H3 tests hold (SAT on edge normals, rational
  squares); q = (2409/1600, 1294051/500000) has q_y > L_h, q_x ≥ ½, dist(q, Ξ)² = 0.25566 ≥ ¼, dist(q, Γ)² = 0.25567 ≥ ¼;
  p = (99221/100000, 21099/10000) lies in int T_u, outside C, Ξ, Γ, with |p − q|² = 0.49227 < ½.  Float slack of the
  disc form up to **+0.0079** on this family (X flat, X_low just under C_top, h_u > ½, θ 1–8°); A272's sup −0.005
  was an optimiser artefact.  The distance form forgets the CONE: the drop conv(D(q, ½) ∪ {p}) crosses X's corner
  (page (a): overlap area 1.1·10⁻³), so no unit square realises (q, p).
* **The corrected statement — the DROP LEMMA** (§1) keeps A272's reduction verbatim (its (P3) already gives the drop
  inside Q) and is what the certificate tests.  [M] at the witness its slack is −0.0016 (`slack273`, exact support-
  function gap), the square's own slack is −0.0049 (`left272`).
* **[T] the lemma is 4-parameter**: invariant under the vertical translation by h_v once X is placed by its dip
  D := C_top − X_low (§2.1); h_v enters only through PRUNE.
* **The box-valid test** (§2) is sound by construction (cores verified vertex-by-vertex with intervals, outer hull of
  interval vertex boxes, strict-separation penumbras, float margins EPS = 10⁻⁹); **benchmark** 200 boxes (§4):
  2–9 ms per box; **differential test** 120 point configurations with PRUNE off: 0 unsound, CERT down to slack
  −0.0029, FAIL already at +0.0007.
* **The run** (§4): tree273 + verify273 over 81 (θ, φ) cells of 5° × 5°, detached (`run273.sh`), price ≈ hours, not
  10² CPU-h.  **Boundary layer**: the corner θ ≤ 5° AND φ ≤ 5° is OPEN by design (§5): there the slack of STRIP₂
  ITSELF → 0 (square: −0.0049 at 8°, −0.0003 at 2°, −0.00008 at 1°, X flat) — a limit of zero margin (θ = φ = 0: X's
  bottom and C's top on one line, the channel between them of width 0), not a vacuous boundary.  No box tree closes
  it; it needs a hand proof (§5, [C]).  **h_v → 1 is not a layer** (h_v-invariance).
* No hand proof of the drop lemma (§6).  Lean unchanged (DiscLemma is opaque; its prose content is [F]; AUDIT note).

## 1. The DROP LEMMA (the statement certified)

Setting of A272 §2 (JAM corner, H1–H3, side in [3.82, ŝ]; C, T_u, S = T_u ∖ C, X, Ξ, Ξ′, Γ as there).
**DROP LEMMA.** *(R) There is no pair (q, p) with q_y > L_h, q_x ≥ ½, p ∈ S, |p − q| < 1/√2 and
conv(D(q, ½) ∪ {p}) ∩ int Ξ = ∅ = conv(D(q, ½) ∪ {p}) ∩ int Γ.  (L) The same with q_y < X_low and Ξ′ for Ξ.*
**It implies STRIP₂-IN-JAM** by A272 §2–§3 unchanged: a free strip square Q (centre q, p ∈ int Q ∩ S) has
q_y > L_h (P0), Q ∩ int Γ = ∅ (P1), Q ∩ int Ξ = ∅ when its chords at X's heights are right of X or it has none,
Q ∩ int Ξ′ = ∅ in case A1-left (q_y < X_low), the case q_y > X_top left of X dead by Lemma CL, the case
q_y ∈ [X_low, X_top] left of X dead by NO-LEFT (P2); and conv(D(q, ½) ∪ {p}) ⊂ Q (P3), D(q, ½) ⊂ Q ⊂ quadrant gives
q_x ≥ ½, p ∈ int Q gives |p − q| < 1/√2.  A272's disc lemma kept only dist(q, ·) ≥ ½ of the drop condition.

## 2. The box-valid test (drop273 / drop4273; soundness)

**2.1 Four parameters.**  In the C_top frame y″ = y − h_v − c − s: T_u″ = conv{(s, −c−s), (s+c, −c), (c, 0), (0, −s)},
L_h″ = −s, C″ = T_u″ + h_u e_x, Γ″ = {−(c+s) ≤ y″ ≤ 0, a ≥ 0, b ≤ 0}, X_low″ = −D, X_top″ = −D + sin φ + cos φ.
Every object of the lemma moves with h_v except the wall x = 0, which is vertical — so the lemma at (h_u, h_v, θ,
X_low, φ) is the lemma at (h_u, θ, D, φ).  [T]  The box is B = [h_u] × [θ] × [D] × [φ] (drop4273).
**2.2 Sets per box.**  T_uo = hull of the interval boxes of T_u″'s four vertices (contains every T_u″(b), convexity).
Cores Ξ_c, Ξ′_c, Γ_c: the defining affine constraints (Ξ: y ≥ X_low, y ≤ X_top, x ≥ 0, v ≥ 0, u ≤ 1 in X's frame at
B_X; Ξ′: u ≥ 0, v ≤ 1; Γ: y ≥ h_v, y ≤ C_top, a ≥ 0, b ≤ 0, truncated at x ≤ 6) at the midpoint, each moved inward
by its own offset until the interval lower bound of EVERY constraint over B is ≥ 10⁻¹² at EVERY vertex; the true set
is convex, so core ⊂ true set for every b ∈ B.  [T]
**2.3 q-cells.**  Squares Z (centre z, half-side h, ρ = h√2) from h = 1/8 down to 1/4096 over the box
[max(½, x_min(T_uo) − 1/√2), x_max + 1/√2] × [L_min, y_max + 1/√2]; Z is dead for part R (resp. L) when:
K0 z_x + h < ½; K1 z_y + h ≤ L_min = −sin θ_hi; KL (part L) z_y − h ≥ X_low_max; K4 dist(z, T_uo) ≥ 1/√2 + ρ + EPS;
K2 dist(z, Ξ_c or Γ_c) < ½ − ρ − EPS (the open disc D(q, ½) then meets the core, hence int Ξ(b) — Ξ(b) is the
closure of its interior); **K5** with D′ = D(z, ½ − ρ − 2EPS) ⊂ int D(q, ½) for every q ∈ Z: Π(K) = conv(K ∪ {v − T w})
(v a vertex of K, w one of the two unit directions from v tangent to D′, T = 5) eroded by EPS, and every convex piece
of (T_uo ⊕ EPS) ∖ Π(Ξ_c) ∖ Π(Γ_c) is at distance ≥ 1/√2 + ρ + EPS from z.
**Why K5 is sound.**  Each point v − T w lies on the segment from the tangent point (in D′) through v ∈ K, so
Π(K) ⊂ Π̄(K) := {p : conv(D′ ∪ {p}) ∩ K ≠ ∅}, which is convex (its complement is a union of open half-planes: p ∉ Π̄ iff
a line separates K from D′ ∪ {p}).  A bad (q, p): the drop misses int K, so a line ℓ = {h = 0} has the drop in
{h ≤ 0}, K in {h ≥ 0}; D′ ⊂ int D(q, ½) gives h < 0 on D′, so conv(D′ ∪ {p}) ∩ K ⊂ {p}; and p ∉ K (p ∈ int Q, whose
neighbourhood misses int K, and K is the closure of its interior).  So p ∉ Π̄(Ξ_c) ∪ Π̄(Γ_c) (cores ⊂ true sets), p ∈
T_u ⊂ T_uo and |p − z| < 1/√2 + ρ: p lies in an undischarged piece.  Float: every decision carries EPS = 10⁻⁹, four
orders above the rounding of these O(1) computations; pieces are closed (conservative).  [T]
**2.4 PRUNE** (the box misses the H1–H3 projection; drop4273.prune4): no h_v in (0, 1) with X_top > 2.82 (H1 with
s̄ ≥ 3.82: X_top > s̄ − 1), X_top ≤ ŝ (X in the container), the open-box condition h_u c + h_v s < c + s − sc (A266
`open_box_tilted`, ring_domain.md (F2)); or a point (the centroid of X ∩ C at the midpoint) interval-verified inside
int X(b) ∩ int C(b) for all b (H2 fails).  **Lemma LOW is deliberately NOT used** (its Lean core `lh_gt_one` assumes
cos α ≥ 1/√2 for A's tilt α ∈ [0°, 90°), not checked here).

## 3. The verifier (verify273: independent re-derivation, bisect on disagreement)

It imports none of geom273 / sets273 / drop273 / drop4273.  Per cell: (i) **coverage** — the leaves are replayed
through the deterministic split from the cell box (every leaf is a node of the bisection tree, every node a leaf or
split into two covered children, every leaf used once: no gap, no overlap); (ii) **PRUNE leaves** — the h_v window
and the X-hits-C point re-derived in `mpmath.iv` (directed rounding, 80 bits); (iii) **CERT leaves** — cores re-built
from the midpoint half-planes with per-constraint offsets but verified in `mpmath.iv`, T_uo from `mpmath.iv` vertex
boxes, the q-cells re-run in shapely with the penumbra built from an INSCRIBED 128-gon of D′ (points d + T(v − d): a
subset of Π̄, sound and slightly weaker), q-cells down to h = 1/8192 (the tree stops at 1/4096); (iv) a CERT leaf the
verifier cannot close is **bisected** (the tree's split, depth ≤ 6) and both halves re-verified; still open ⇒
DISAGREE (the cell is reported FAIL, never green).  On the pilot cells c5_3 (61 leaves) and c2_0 (1746 leaves) every
leaf was re-derived without a single bisection (the verifier was at least as strong as the tree on every leaf).
Cost ~30 ms per CERT leaf.

## 4. Benchmark, differential test, price, what is launched

* `bench273` (the 5-parameter kernel, 200 boxes of relative size 1/8 … 1/64 centred at random PRUNE-surviving points):
  all CERT, 2–9 ms per box, 65–90 q-cells per box.  `results/bench273.json`.
* `diff273`: 120 random POINT configurations (tiny boxes), PRUNE off (so many lie outside H1–H3 where the lemma can
  fail), kernel verdict vs the [M] drop slack of `slack273` (exact support-function gap, grid + Nelder–Mead):
  **0 unsound** (no CERT with positive slack); 111 CERT, the tightest at slack −0.0029; 9 FAIL, all with positive
  slack (the smallest +0.0007).  The test is tight to ~10⁻³.
* The 4-parameter form closes where the 5-parameter one ground: c2_0 (θ 10–15°, φ 0–5°) in 20 s / 1746 leaves
  (5-parameter: > 70 000 leaves unfinished after 10 min); c5_3 in 0.4 s.  Sensitivity at the witness: h_u and D
  insensitive (CERT at widths 0.064), θ and φ need ~0.004 rad.  Pilot c1_0 (θ 5–10°, φ 0–5°): 60 000 boxes in 447 s
  covered 89 % of the cell's volume before the pilot cap.
* **Launched** (`run273.sh`, detached, one python at a time): cells θ-bins 1–8 then 0, φ ascending; per cell tree273
  (cap 400 000 boxes; the rest of a capped cell is OPEN) then verify273, one commit + push per cell; the page at the
  end.  Corner layer `A273_CORNER_DEG=5,5`.  **Price** [M, from the pilots]: all cells but the corner-adjacent ones in
  seconds to minutes; c1_0 / c0_1 are the expensive ones (≤ 400 000 boxes ≈ 50 min each at the cap, plus ~30 ms per
  CERT leaf to verify) — a few CPU-h in total, far under the brief's 20 / 100 CPU-h lines.  So the **R-first run is
  unnecessary**: the H1–H3 run (outside the corner) is cheaper than R's would have been, and A271's ring inequalities
  are not used anywhere.
* STOP: `touch attempts/A273-disc-lemma/logs/STOP273` (exits between cells).  RESUME: remove it and relaunch the
  line in `run273.sh`'s header; indexed cells (certs/index273.jsonl) and verified cells (results/verify273_index.jsonl)
  are skipped, an interrupted cell restarts.

## 5. The boundary layer: θ → 0 with φ → 0 (not h_v → 1)

* **h_v → 1** is no layer at all: the drop lemma does not depend on h_v (§2.1); A272's "sup attained only as
  h_v → 1" was the optimiser drifting along a flat direction of the (false) disc form.
* **θ, φ → 0** is the layer.  [M] on the flat-X family (φ = 0, X_low just under C_top, h_u ≈ 0.85–0.95): drop slack
  (slack273) −0.0027 (θ 8°), −0.0016 (8.01°, the witness), −0.0024 (5.9°), −0.00006 (2°); the square itself
  (left272.best_Q) −0.0049 (8°), −0.0027 (5.9°), −0.0012 (4°), −0.0003 (2°), −0.00008 (1°) — roughly 0.15 θ² rad.
  **STRIP₂'s own margin vanishes** there, so no relaxation and no box tree can close the corner.
* The limit θ = φ = 0 [T]: C, T_u and X axis-parallel, X's bottom edge and C's top edge on the line y = C_top over
  x ∈ [h_u, 1], P = [0, h_u] × [h_v, C_top]: a segment from p ∈ P (below C_top, x ≤ h_u) to q (q_x ≥ 3/2 when
  q_y ∈ [X_low, X_top]) crosses y = C_top at some x; if x ≤ 1 it enters int Ξ just above, if x ∈ [h_u, 1] it was in
  int Γ just below — the lemma holds with ZERO margin: the channel between X's bottom and C's top has width 0.  The
  configurations near the limit are H1–H3-feasible (probe273 / witness-type points at θ = 2°, φ = 0), so the layer is
  not vacuous.
* **Handling**: the corner {θ ≤ 5°} × {φ ≤ 5°} (all h_u, D) is left OPEN by the tree (grey stipple on the map);
  cells c1_0 / c0_1 adjacent to it may add capped OPEN leaves (reported per cell in the index).  [C] a hand proof for
  the corner: the drop's apex angle at p exceeds 90° (A272 §5 (i)) while the channel between X's lower boundary and
  C's upper-left edge opens at angle |φ − θ| ≤ 5°; a fan of angle > 90° from p must leave the channel through its
  mouth, which forces p within ~√(ab) of the mouth (a, b the distances to the two walls) — the region of S there is
  a sliver of thickness h_u sin θ.  Not written out; this is the exact open layer.

## 6. Hand proof

None of the drop lemma.  Proved here: the h_v-invariance (§2.1) and the zero-margin limit (§5).  The one-hour budget
went to the counterexample and the corrected statement.

## 7. What the brief (and A272) had wrong

1. The DISC LEMMA is false (§0): the statement to certify is the DROP LEMMA; the per-box test is 2-D in the centre
   q but must carry the cone to the strip point (penumbras), not only distances.
2. The lemma has 4 parameters, not 5 (h_v-invariance); the brief's boundary layer "h_v → 1, X flat" is not where the
   slack vanishes — it vanishes as θ, φ → 0 (X and C both nearly axis-parallel), where STRIP₂ itself has margin → 0.
3. The price: hours, not ~20 / ~10² CPU-h — and R first is unnecessary (the full H1–H3 projection outside the corner
   is cheaper than R was estimated).  The corner, however, cannot be bought at any price.
4. A272's sup slack −0.005 on H1–H3 is wrong (the disc form reaches +0.008); its "attained only as h_v → 1" is an
   artefact.  The ring route (A271's RingIneq) remains the alternative for the corner.
5. Lemma LOW's `lh_gt_one` carries cos α ≥ 1/√2 as a hypothesis (A's tilt in [0°, 90°) in ringdom271) — not used
   here; worth checking before any other certificate leans on it.
