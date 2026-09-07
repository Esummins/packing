# A130 — the flush re-fit residue: T3 table, T1 diagnosis, T2 moves, T4 consequence

Labels [T] proved, [S] routine, [M] measured, [F] finding, [C] open. Code `code/flush130.py` (one process, BLAS
pinned, BelowNormal, mpmath `iv` 64 bits outward-rounded, LPs for the direction search only); results
`results/moves130.jsonl`, table `results/table130.md`, drawing `results/flush130.svg`, shells
`results/shells130_K03_BR.json`; lemmas with proofs and Lean shapes `notes/lemmas130.md`. Sample = A128's
near-packings (`geom130.py` = A128's `coupled128.py` copied with its write paths moved; A128 read-only): the three
window holds K03 (l2_p65_111, 3.925149), K06 (l1_159, 3.886745), cell_l1_124 (3.942810), the control 4.001525, plus
4.000237 and K01 as regression controls and Trump as the canary. Radii 10⁻³, 10⁻⁴, 10⁻⁵, 10⁻⁶ in every pose
coordinate and the side. Every certificate re-sampled (≥ 10⁴ configurations per certificate over its pieces,
≥ 500 per piece; every certified row's derivative — or, for EX2, the whole constructed packing — in floats).

## T3 — the table (hold × move → certified / not, radius, margin)

FIELD = Lemma BOX-FIELD-W over all eleven squares, decided on the tilt-sign sub-boxes of the axis-aligned squares
among the subject and its row partners and, inside each, on the contact-mode pieces of Lemma MODE (certified iff
EVERY piece is; each piece has its own field). ROT-W = the same with the single square. EX2 = Lemma EXCHANGE-2
(A128's re-fit Q₀ + a finite opening motion of the untouched squares; F = the flush blockers of Q₀ on the box).
"held" = no certificate at any radius tried. Point tests on the 10⁻⁸ box: the weak-cone depth rate (the largest
first-order depth decrease with every contact row weak — Lemma ROT-W / FIELD at the point); ISOLATED = the cone
{rows ≥ 0, depth rate ≥ 0} is {0} (Lemma ISOLATED).

| hold | side | corner: subjects (depth) | FIELD box | ROT-W box | EX2 (flush set F, margin of Q₀ vs F at r = 10⁻³) | point: weak-cone rate | Gordan support (single square, point) |
|---|---|---|---|---|---|---|---|
| **K03** | 3.925149 | BL: sq0 slot (1), sq1 = BL(0,1) tangent | held (10⁻³…10⁻⁶; pieces certified at 10⁻⁴: sq0 0/8, sq1 0/8) | held | F = {8 = f4} (−3.3·10⁻³): not certified, 4/4 sub-boxes fail at every r | 2·10⁻⁵, 1·10⁻⁵ (residual) | sq0: flush row vs sq1 0.50 + floor 0.50; sq1: f4's edge 0.41 + wall 0.31 + virtual 0.27 |
| | | BR: sq6 = f2 (0.207), sq7 = BR(0,1) tangent (4·10⁻⁹) | held (sq6: **10 of 32 pieces certified at 10⁻⁴**, rate 1.000 on each; sq7 0/8) | held | F = {9 = f5} (−4.1·10⁻³): not certified (f5 wedged) | **sq6: 1.000 (the exact slide, Lemma FLUSH-SLIDE)**; sq7: 1·10⁻⁵ | sq6: flush row vs f0 0.50 + floor 0.50; sq7: f2's flush row 0.27 + f5's edge 0.41 + wall 0.04 + virtual 0.27 |
| | | TR: sq3 slot (1), sq9 = f5 tangent (48.63°) | held (0/2) | held | F = {4, 7, 10} (−3.5…−4.4·10⁻³): not certified (16/16 fail) | 4·10⁻⁶, 4·10⁻⁶ | sq3: f5's edge 0.41 + walls 0.31 + virtual 0.27; sq9: sq3 0.35, f0 0.36, f3 0.14, f6 0.14 (pinwheel) |
| | | TL: sq2 slot (1), sq8 = f4 tangent (41.37°) | held (0/2) | held | F = {1, 4, 10} (−2.8…−3.7·10⁻³): not certified (32/32 fail) | 4·10⁻⁶, 4·10⁻⁶ | sq2: f4's edge 0.41 + walls; sq8: sq1 0.14, sq2 0.35, f0 0.36, f6 0.14 |
| **K06** | 3.886745 | BL: sq0, sq1 = BL(0,1), sq7 = BL(1,0) (3 meeters) | held | held | n/a (3 possible meeters) | (point tests void: the landing overlaps by 1.1·10⁻⁶) | sq0: flush vs sq1 0.50 + floor 0.50; sq1: sq10's edge 0.41 + wall 0.28 + virtual 0.31 |
| | | BR: sq6 = f1 (0.606), sq2 = BR(0,1) tangent | held (sq6: **4 of 8 pieces at 10⁻⁴**, rate 1.000; sq2 0/8) | held | F = {9 = f4} (−4.1·10⁻³): not certified (2/2 fail) | void | sq6: flush vs sq2 0.50 + floor 0.50; sq2: sq6 0.28 + f4's edge 0.41 + wall 0.04 + virtual 0.28 |
| | | TR: sq4 slot, sq9 = f4 (48.44°) | held (0/2) | held | F = {2, 5, 8, 10}: not certified (16/16) | void | sq4: f4's edge 0.41 + walls |
| | | TL: sq3 slot, sq10 = f5 (48.44°) | held (0/2) | held | F = {1, 8, 9}: not certified (16/16) | void | sq3: no certificate at the 10⁻⁸ bar (the landing's gaps) |
| **cell_l1_124** | 3.942810 | BL: sq10 slot, sq8 (45.01°) | held (0/1, 0/2) | held | F = {4, 7} (−1.7, −2.1·10⁻³): not certified (16/16) | 1.000 (slot slides along the wall) | sq10: none (unheld at the point) |
| | | BR: sq9 slot, sq5 = [2.94, 3.94] × [1, 2], sq7 (3 meeters) | held | held | n/a (3 meeters) | 1.000 | sq9: sq7's flush row 0.50 + virtual 0.50 |
| | | TR: sq2 slot, sq0 (44.99°) | held (0/2, 0/4) | held | F = {4, 5} (−2.7, −3.5·10⁻³): not certified (16/16) | 1.000 | sq2: sq0's edge 0.41 + top wall 0.29 + virtual 0.29 |
| | | TL: sq3 = [0, 1] × [2.925, 3.925] (0.982; 0.0176 below its slot), sq4 = [1, 2] × [1.94, 2.94] tangent | held (sq3: **1 of 4 pieces at 10⁻⁴**; A128's strict ROT at 10⁻⁶ is below this run's pad resolution); sq4 0/64 | held | F = {0, 1, 6, 8} (−1.5…−2.7·10⁻³): not certified (8/8) | sq3: 1.000 (slides down 0.26 to sq1); sq4: — | sq3: none; sq4: flush vs sq6 0.50 + sq8 0.50 |
| **control 4.001525** | 4.001525 | BL {sq1 0.103, sq0 0.062} (83.3°); BR {sq2 0.887, sq3 0.00102}; TR {sq6 0.921, sq7 0.00102}; TL {sq5 0.044, sq4 0.032} | **CERTIFIED at ALL EIGHT intruders on the 10⁻⁴ box** (min strict 0.052–0.319; every square moves; 2.5·10³–5·10³ samples each → 0 hits; not at 10⁻³) | held | BR: r = 10⁻⁵ (F = ∅, = A128's depth-1); BL/TR/TL: no valid re-fit (A128 margins −9.5·10⁻⁴, −1.9·10⁻⁴, −1.6·10⁻²) | 0.11–0.32 at every intruder | as A128 (all eight held under ROT) |
| 4.000237 | 4.000237 | 8 intruders | **CERTIFIED at all eight on 10⁻⁴** (min strict 0.20–1.00; 0 hits) | BR sq2 at 10⁻⁶ (= A128) | BL 10⁻³, BR 10⁻⁵, TR 10⁻⁵ (all F = ∅, = A128) | 0.22–1.00 | as A128 |
| K01 | 4.000000 | | BR sq7 10⁻³, TR sq5 10⁻³ (rattler / slot) | same | TL 10⁻³ (F = ∅, = A128) | 1.000 | — |
| **Trump** (canary) | 3.877084 | 9 subjects (BL sq0/1/3, BR sq2/8, TR sq5/9, TL sq6/4) | **held on every box** (LP t = 0 at every radius, every sub-box, every mode) | held | no re-fit certifies at any r (BR 16/16, TR 4/4, TL 2/2 sub-boxes fail) | **0 and ISOLATED at all nine** (cone {0}) | as A103/A128 (5/5 intruders pushed) — **PASS** |

Sampled confirmations: 18 FIELD certificates + 2 ROT-W + 5 EX2/depth-1 exchanges, 78 000 configurations drawn
in total (K01 TR: 10⁴; the locks' subjects 2.5·10³–5·10³ each over their pieces), **0 hits**.

**Verdict.** The three window holds SURVIVE every move on every box, for two reasons that are now exact:
 (i) at the (slot-like deep meeter + flush tangent) corners the deep meeter's retreat is an exact slide (weak-cone
     rate 1.000 at K03 BR, K06 BR, l1_124 TL/BL/TR/BR), but a fixed field certified by intervals sees it only on
     the tilt-sign × mode pieces where every flush partner leans the same way (K03 BR 10/32, K06 BR 4/8, l1_124 TL
     1/4) — Lemma MODE's accumulation at the flush stratum, closed by hand (Lemma TWO-INTRUDER + SHELL-SCALE +
     FLUSH-SLIDE) but not by the plain leaf;
 (ii) every re-fit's flush blocker is the interior grain (K03's pinwheel f4/f5/f6/f0, K06's 48.4° grain, l1_124's
     45° pair), wedged in every sub-box and mode: EXCHANGE-2 certifies exactly where A128's depth-1 exchange did.
 The control FALLS: the Gordan-certified lock 4.001525 (held under ROT, ROT-W and every rigid cluster screw in
 A128) is drained at every one of its eight intruders by the non-rigid field on the 10⁻⁴ box — the move A128
 named — and so is 4.000237. Trump is held everywhere and is first-order ISOLATED at all nine subjects.

## T1 — the flush geometry at the four points, exactly (`results/flush130.svg`)

Flush contacts = parallel touching edges with positive overlap (`flush_contacts()`, gap < 10⁻⁷, parallel to 10⁻⁶).

**K03** (side 3.925149; f-indices of `docs/shadows.md`, poses sq0–3 = slots BL(0,0), BL(0,1), TL(0,0), TR(0,0),
sq4–10 = f0–f6). Flush: sq0–sq1 (the BL column, length 1), f0–f1 (0.642: the upright f0 on the floor square f1),
f0–f2 (0.330), **f2–f3 (0.207: the floor square f2 = [2.132, 3.132] × [0, 1] under BR(0,1) = f3 = [2.925, 3.925] ×
[1, 2])**; 10 wall-flush contacts. Doubly-met corners on every box: all four, each (slot-like deep meeter, flush
tangent): BL (sq0, sq1), BR (f2 at 0.207, f3 tangent), TR (sq3, f5 at its corner point), TL (sq2, f4). Held by:
f2 — f0's bottom edge on its top edge (0.50) and the floor (0.50) [a wedge for rotations; but its far edge is
FREE: f1 is 0.027 away, so it slides toward f1 at rate 1 — Lemma FLUSH-SLIDE, weak-cone rate 1.000: K03 is not
Ψ^(w)-minimal at its side]; f3 — f2's flush row 0.27, f5's edge on its inner top corner (2.925, 2) 0.41, the right
wall 0.04, the virtual push 0.27 (pushed); the four tangent squares by the pinwheel (f4, f5 each with four
contacts: two slot corners on their edges, f0's corner, f6's edge). **Why the exchange has zero margin:** at BR
the re-fit Q₀ = BR(0,1) is f3 put back: its inner top corner (m − 1, 2) sits ON f5's lower edge (direction
(cos 48.63°, sin 48.63°)), and f5 is wedged by TR(0,0)'s corner on its upper edge (perpendicular: moving f5 off Q₀'s
corner is exactly tangent to that contact), f0's corner on its lower-left edge (also tangent) and f6's edge at its
top vertex (rate −1 along the opening direction) — every opening motion of f5 penetrates f6, which is on the top
wall; the LP finds no field on any sub-box or mode (EX2 BR: 4/4 sub-boxes fail at every r). At BL the re-fit is
BL(0,1) itself, whose inner top corner (1, 2) sits on f4's lower-left edge — the mirror pinwheel. At TR/TL the
re-fit is the tangent square's own pose, flush against three untouched squares (f0, f3, f6 / sq1, f0, f6).
**Diagnosis:** first-order lock? No — for the deep meeter f2 the exact slide exists (rate 1) and for every
piece where f2, f0, f3 lean toward the wall the field certifies (10 of 32); the hold is a mode accumulation at the
flush stratum (T2 §2), not a lock, and not a Ψ-local minimum. The near-packing is not an exact critical point
(KKT residual 3.9·10⁻⁶, gaps −1.4·10⁻⁸), so the weak-cone rates 4·10⁻⁶ … 2·10⁻⁵ at the other subjects are at the
residual and decide nothing; the second-order test (Lemma KINK) has no exact flat direction to act on here.

**K06** (side 3.886745, the S02 pinwheel; sq0–4 = slots BL(0,0), BL(0,1), BR(0,1), TL(0,0), TR(0,0), sq5–10 = f0–f5).
Flush: sq0–sq1 (1.0), **f1–BR(0,1) (0.606: f1 = [2.493, 3.493] × [0, 1] on the floor under BR(0,1))**; BL(1,0) = f2
is a third BL meeter on the box. Doubly-met: BR (f1 at 0.606, sq2 tangent), TR (sq4, f4 at 48.44°), TL (sq3, f5).
Held by: f1 — sq2's flush row + floor (a free far edge again: f2 = BL(1,0) is at x ≤ 2, gap 0.49 — the exact slide
exists; the landing's 1.1·10⁻⁶ overlap makes the 10⁻⁸ point tests void, so this is read from the geometry, not the
LP); sq2 — f1's flush row 0.28, f4's edge on its inner top corner 0.41, the wall 0.04, virtual 0.28. Re-fits: BR
Q₀ = BR(0,1) with its corner on f4's edge (F = {f4}), TR/TL the tangents' own poses against four/three grain
squares. Same diagnosis as K03: mode accumulation (4/8 pieces certified for f1) + a wedged grain.

**cell_l1_124** (side 3.942810, K02-type; poses from `nearpack128.json`). Flush: sq1–sq4 (0.720), **sq4–sq6 (0.892:
sq4 = [1, 2] × [1.943, 2.943] under sq6 = [1.108, 2.108] × [2.943, 3.943], which is on the top wall)**, sq5–sq9 (1.0:
the right-wall column). TL: sq3 = [0, 1] × [2.925, 3.925] sits 0.0176 BELOW its slot (depth 0.982, μ = 0.0176), its
bottom-right corner on sq4's left edge x = 1; sq4's top-left corner (1, 2.943) is the TL cell's bottom-right corner
(tangent). Held by: sq3 — nothing at the point (weak-cone rate 1.000: it slides down the wall 0.26 to sq1; A128's
strict ROT at 10⁻⁶ is the same motion); sq4 — sq6's flush row 0.50 + sq8's contact 0.50. **[T] sq4 cannot intrude
TL in any packing of the box:** entering the open cell needs its top-left corner at x < 1, y > 2.943, i.e. a ccw
tilt with an upward shift larger than half the tilt — and any upward motion of sq4 pushes its top-right corner
into sq6 (flush over 0.892, sq6 on the top wall). So TL is K0-FREE for every PACKING of the box although both
squares are "possible meeters" on the pose box (A128's and this run's count): Lemma TWO-INTRUDER's conditioning
in its strongest form — the box needs no certificate at TL at all. BL/TR: the 45° pair sq8/sq0 at the slot's inner
corner point (Trump's BR/TR geometry: Lemma TRUMP-LOCAL's wedge), re-fits flush against sq4/sq7 and sq4/sq5.

**Control 4.001525.** Flush: sq0–sq1 (the 83.3° BL column), sq4–sq5 (TL column), the 1 + nick crowds at BR/TR, the
frame's columns. All eight intruders pushed (3–5 square rows + 1 wall row, A128). **Diagnosis: first-order
UNLOCKED under fields:** the weak cone has depth rates 0.11–0.32 at every intruder (a first-order weakly-feasible
field of all eleven squares decreases every intruder's depth), and the box certificate holds at 10⁻⁴ (not 10⁻³:
at 10⁻³ the box contains configurations where the frame's near-contacts of A102/A103 close in both senses). It is
NOT a Ψ^(w)-local minimum under coupled motions; its single-square Gordan certificates are the rigid-motion
shadow of a non-rigid drain.

**Trump.** ISOLATED at all nine subjects: the cone {every row ≥ 0, depth rate ≥ 0} is {0} on the 10⁻⁸ box — by
Lemma ISOLATED Trump is an isolated point of {packings at ŝ with d_c(Q) ≤ d_c(Q)(Trump)} for every subject Q, the
strongest first-order form of the canary.

## T2 — the moves (statements, proofs, Lean shapes in `notes/lemmas130.md`)

1. **Lemma BOX-FIELD-W** [T]: BOX-MOVE with a non-rigid field (one exact screw per member of any C), member–
   member rows with the flush kink charged through the exact difference u = ω_{B′} − ω_A, WEAK pair/wall rows
   (sound for r > 0 by the Dini-derivative argument; strict at r = 0), Q's depth strict, other depths weak. Dual
   BOX-GORDAN-F. The column-straighten + row-slide field of the brief is a feasible point of its LP.
2. **Lemma MODE** [T]: the contact-mode split (a pair with ≥ 2 possibly-separating axes is separated at every
   packing by its largest; per piece only that row); vacuous pieces. [F] at a flush contact the pieces accumulate
   at the flush stratum and a fixed field fails at every radius by a sign of the order of r — the exact content of
   "a flush placement has no neighbourhood". **Lemma SHELL-SCALE** [T]: on the shells [a, 2a] of the deep
   meeter's tilt a screw with rotation ∝ a certifies, all coefficients affine in a ⇒ one parametric certificate;
   [M] K03 BR shells 5·10⁻⁵ … 1.6·10⁻⁶ certified, failing only below the fixed pad.
3. **Lemma EXCHANGE-2** [T]: the depth-2 exchange (re-fit + a finite opening motion ε* of the flush blockers'
   cluster, weak rows, one strict axis per blocker, the motion inside the pad) — ∀-packings.
4. **Lemma TWO-INTRUDER** [T]: the certificate need only hold where BOTH meeters intrude; the K03-type corner
   decided by hand (two-intruder packings only with the tangent leaning to the wall; there the deep meeter's slide
   is exact ⇒ every selected minimiser in the box is K0-FREE at that corner); l1_124's TL has NO two-intruder
   packing at all.
5. **Lemma FLUSH-SLIDE** [T, point, n-general]: at the Ψ^(w)-minimiser a floor (wall) intruder whose active
   contacts are its floor and squares on its top edge only slides — every flush intruder at z* is pressed on its
   FAR edge (the flush form of NOCRIT-SEL's Corollary 2). **Lemma ISOLATED** [T] (curve selection). **Lemma
   KINK** [T]: the exact second-order condition at a parallel-edge contact (the kink is second order when Δ̇ = 0;
   Farkas / prestress form; the 2 × 2 determinant for dim K = 1) and its box form (only structurally-zero rows admit
   a second-order box certificate: a second-order escape is a point property). [M] moot on this sample: no exact
   flat direction exists at any of the four points (near-packings carry residual slack; the locks carry POSITIVE
   first-order rates; Trump is isolated).

## T4 — consequence for DRAIN-SEL(W)

The three window holds do not fall to a plain interval leaf, and they do fall to the exact case analysis; the
control falls to the leaf. What remains between the sample and DRAIN-SEL(W), with FLUSH as a case
(`docs/proofs/drain_sel.md` §7.3):
 * cases 1–3 (ROT / ROT-W / CLUSTER-ROT / EXCHANGE) — theorems (A103, A105, A128);
 * case F (FLUSH-SLIDE) — theorem: a flush intruder at z* is pressed on its far edge; case F′ (SLOT-GRAZER) —
   theorem modulo K0-O1: on W at m ≤ ŝ − δ no corner of any packing has a near-slot intruder with μ_c ≤ δ/(1 + √2)
   (SHELL + SLIDE), so the K03/K06/l1_124-type corners live only in the slab (ŝ − 2.4·10⁻³ · ρ/10⁻³, ŝ] of W;
 * case FIELD (BOX-FIELD-W at r = 0 with strict rows = Lemma CLUSTER-ROT for a non-rigid field; the point form is
   [T] by the same proof: a strictly feasible field with Q's depth decreasing contradicts minimality) — theorem;
 * case 4, the residue: K0-BLOCKED, every intruder LOCKED, every cluster screw held, every re-fit flush, every
   flush intruder pressed on its far edge, NO strictly feasible field — **realised by nothing on disk at any
   side**: the two A104 locks (the only fully-held K0-BLOCKED packings known) fall to the field on 10⁻⁴ boxes.
   The obligation is unchanged in kind (a residue statement) but it now has no known member above ŝ either;
   its Lean shape adds one disjunct `¬ fieldHeld z i c` (the Motzkin certificate over 33 + kink variables) to
   `drain_sel`'s conclusion, consumed exactly as `¬ clusterHeld`.
 * The menu certificate over the k0 root cells: the FIELD leaf fires at radius 10⁻⁴ on the locks and 10⁻³ on the
   rattler/slot subjects; the 216 level-1 cells are 0.1 wide, so at the root the leaf is silent (the K0-ROT /
   TF-U / EX verdict, unchanged) and it would fire only ~7 bisection levels down in 33 dimensions — not a route;
   at the flush stacks it additionally needs the mode contractor + parametric shells + the stratum statement
   (lemmas130.md §2, Corollary), i.e. a semi-algebraic leaf, not a box leaf. `budget.md`'s k0 row (12,000 CPU-h
   tree / 0 theorem) is unchanged; the theorem route gained: the residue has no realisation, and the flush case is
   two theorems (F, F′) plus a field case that is a theorem at the point.
 * A hold at a non-packing support (the brief's question): K03, K06, l1_124 are k ≥ 1 packings above ŝ (not
   K0-BLOCKED, not in W); their boxes contain K0-BLOCKED packings only as grazer-blocked slot corners (depth ≤
   (1 + √2)r), and DRAIN-SEL(W) — which quantifies over packings at side m ∈ W — never meets them: on W they are
   SLIDE-excluded outside the slab, and in the slab they are Lemma TRUMP-LOCAL's geometry at ŝ. So a hold there
   costs DRAIN-SEL nothing; what it costs is the TREE leaf, which is blind at every flush stack.

## Pointers

`attempts/A130-flush-exchange/`: `code/flush130.py` (FIELD, EX2, MODE, tilt-sign split, point tests, sympy
Hessians for KINK), `code/geom130.py` (A128's module copied), `code/summarise130.py`, `code/draw130.py`,
`code/depgraph_note130.py`; `results/moves130.jsonl` (everything), `results/table130.md`, `results/flush130.svg`
(four holds + Trump, flush contacts drawn with lengths, held subjects red, re-fits and their flush blockers),
`results/shells130_K03_BR.json`, `results/two_intruder_pieces130.json` (uniform sampling finds no packing in any
box — the packings are a measure-zero stratum; that check is uninformative and is recorded as such);
`logs/run130_all.out`, `logs/run130.log`. `notes/lemmas130.md` (T2). `docs/proofs/drain_sel.md` §7 (addendum).
Discipline: one process at a time for the runs (a second, seconds-long, for the piece counts and shells), BLAS
pinned, BelowNormal, PYTHONDONTWRITEBYTECODE=1; pure geometry / interval arithmetic (3|C|-variable LPs for the
direction search only); read-only on every campaign and attempt (A128 copied, not imported; its results read);
frozen verifiers untouched; nothing deleted; git fetch + plain merge + push of own paths.
