# family258 — the NORMAL RING at m = 4: parametrisation and the exact domain D  (A258; for A259)

**VERSION 2, 2026-09-21** (v1 = §1–4, unchanged in substance; NEW: §5 verdicts, §6 the HELD POKER — read §6 first,
it changes what the room statement has to say; §7 the locked wall).  Tags: [T] proved here (elementary, closed form), [M] checked numerically
(`code/test258.py`, `code/dom258.py`), [C] conjecture.  What is PROVED is the geometry of the family (a parameter
point in D *is* a ring of eight squares: a packing, every box and slot doubly met).  What is ASSUMED [C] is
NORMAL-RING(11) itself: "every normal-form family-stuck packing on the window contains a member of this family".
A259 should bound the room on **D′ ⊇ D** (below) — it is the safe superset; D and D_tight are the aims.

## 1. Frames and the row

Container [0, s]², 3 < s < 4.  Walls w = 0 floor, 1 right, 2 ceiling, 3 left, each walked COUNTER-CLOCKWISE from its
START corner (floor from BL, right wall from BR, ceiling from TR, left wall from TL).  Wall frame (t, d): t along the
wall from the start corner, d the depth off the wall; to container coordinates
`0: (t, d)   1: (s − d, t)   2: (s − t, s − d)   3: (d, s − t)`  (rotations: the SENSE of a square is frame-free).
Corner k (0 BL, 1 BR, 2 TR, 3 TL) lies between the END of wall k−1 and the START of wall k.

A ROW OF TWO of sense + on wall w: tilt φ ∈ (0°, 45°), start offset a; c = cos φ, g = sin φ, w(φ) = c + g:

    Q1 = (a+g, 0), (a+w, g), (a+c, w), (a, c)          Q2 = Q1 + (sec φ, 0)          (wall-frame vertices)
    end offset  b = s − a − sec φ − cos φ − sin φ =: K(φ, s) − a.

[T] Q1, Q2 touch the wall, are interior-disjoint and share a segment of length 1 − tan φ (NORMAL-CELL (a)); under
them a SEALED right triangle (legs 1, tan φ; no unit square meets its interior without meeting Q1, Q2 or leaving the
container); above them the TOOTH: a right-angled notch with apex Q2's vertex (a + sec φ, cos φ), sides along Q1's edge
(length tan φ, up to Q1's top vertex (a + c, w)) and Q2's edge (length 1).  The next cell Q2 + (sec φ, 0) leaves the
container (b < 1 < sec φ), and so does Q1 − (sec φ, 0): **a row of two with a, b < 1 is ROW-NORMAL.**
Sense − is the mirror image (every statement below with all senses flipped is the reflected family D⁻).

## 2. The family: 8 coordinates + s

Parameters: (a_w, φ_w), w = 0..3, and s.  `code/geo258.ring(s, a, phi)` builds the eight squares.  Write
b_w := K(φ_w, s) − a_w.  At corner k the pair is the **A-type** Q1 of wall k (offset a = a_k, tilt α = φ_k) and the
**B-type** Q2 of wall k−1 (offset b = b_{k−1}, tilt β = φ_{k−1}).

**D** := the set of (a, φ, s) with

* (D1) 0 < φ_w < 45°;
* (D2) a_w < 1 and b_w < 1      [T: ⟺ Q1 meets the start box and Q2 the end box — T-CELLS];
* (D3) a_w + sec φ_w < 2 and b_w + sec φ_w < 2      [T: ⟺ slot L = [1,2] is met by Q2 too, slot R = [s−2, s−1] by Q1
  too; with (D2) every one of the 12 border cells is then met by exactly two ring squares];
* (D4) at every corner k:  **max(E_A, E_B) ≥ 0**, where with κ := max(0, sin(α − β))

      E_A = a sin α + b cos α − cos²α − sin α sin β − κ        (separation along the A-type's edge normal)
      E_B = a sin β + b cos β − sin²β − cos α cos β − κ        (separation along the B-type's edge normal)

  [T] each is the exact signed separation along that axis; [T] the B-type's other axis never separates when a < 1;
  [M] the A-type's other axis never decides (0 sign mismatches between max(E_A, E_B) ≥ 0 and the SAT gap ≥ 0 on
  60 000 random (a, b, α, β) ∈ [0,1]² × (0°,45°)²).  **Common tilt α = β = φ: E_A = E_B = a sin φ + b cos φ − 1.**
  (a_w > 0, b_w > 0 — containment — follow: (D4) with b < 1 gives a > tan(φ/2).)

**D′** := D without (D3) (a slot may be doubly met with the help of a free square instead).  D ⊆ D′.
[M] every sampled point of D is a packing of eight squares inside the container (least pair gap ≥ −10⁻¹⁵, the
row-internal contacts; all 28 pairs checked) with all twelve cells doubly met, and its Hall minimum is 0, attained
ONLY by the 16 maximal families (4 boxes + one slot per wall): **the bare normal ring is not family-stuck; one ninth
square that meets every maximal family makes it so** ([T], the count of `normal_ring.md` §3).

**For fixed tilts D is a union of ≤ 16 convex polytopes in (a_0..a_3)** — every condition is linear in the offsets
(`dom258.sup_margin`: one LP per choice of separating axis at each corner).

## 3. Size of D (first numbers, [M], `dom258.py`)

Common tilt, C4 slice: D ≠ ∅ iff s > 1 + sec φ + cos φ + sin φ + tan(φ/2) (take b → 1) and the (D3) cut; sup-margin
t*(s, φ) (least of 1 − a, 1 − b, the slot and the corner margins):

| φ | 3.82 | ŝ | 3.95 | 3.99 |
|---|---|---|---|---|
| 2° | +0.0133 | +0.0144 | +0.0157 | +0.0164 |
| 8° | +0.0414 | +0.0457 | +0.0512 | +0.0542 |
| 14.545° | +0.0506 | +0.0589 | +0.0696 | +0.0754 |
| 25° | +0.0136 | +0.0298 | +0.0506 | +0.0620 |
| 30° | −0.0300 | −0.0091 | +0.0176 | +0.0322 |

so on the window the common tilt lives in (0°, ≈ 28°) and the offsets in a band of width ≤ 0.12 around
a ≈ 0.65–0.85, b ≈ 0.85–0.97.  (The per-wall tilt spread allowed by D: §3 of `normal_ring.md`, scan pending.)

## 4. Sub-families A259 may use

* **D_tight** [T as a description; that the maximiser lies in it is P3 of `normal_ring.md`, needs "no free square
  blocks the slide"]: all four corners in contact, max(E_A, E_B) = 0.  Common tilt ⟹ C4-symmetric and explicit:

      a = (K cos φ − 1)/(cos φ − sin φ),   b = (1 − K sin φ)/(cos φ − sin φ),   K = s − sec φ − cos φ − sin φ

  (the cyclic linear system a_w sin φ + (K − a_{w−1}) cos φ = 1 has slope (cot φ)⁴ ≠ 1: unique solution).  At ŝ:
  φ = 8°: (0.847, 0.891); 14.545°: (0.799, 0.826); 25°: (0.640, 0.805).  **Two coordinates (φ, s).**
* **The poker's wall** [T necessary]: a ninth square that is not a box meeter must have interior points in a wall's
  RIBBON [s−2, 2] × [0, 1]; inside the ribbon the band is covered by Q1 ∪ Q2 ∪ the sealed triangle except for the
  TOOTH (and the thin wedge under Q2, which belongs to the sealed corner pocket).  So on SOME wall

      a_w + sec φ_w + cos φ_w · tan(φ_w/2) > s − 2     and     a_w + sec φ_w − sin φ_w · tan(φ_w/2) < 2,

  and the poker has a vertex in that tooth (depth below d = 1 at most 1 − cos φ_w: 0.032 at 14.5°).

## 5. Verdicts on the other structures (details: `docs/proofs/normal_ring.md` §3)

Least side of a pinwheel of ROWS (rows of 2 or 3, any senses, per-wall tilts incl. flat; exact LP per tilt vector,
grid 11⁴ + polish, `results/side258.jsonl`) [M]: one sense, rows of two (this family) **→ 3**; mixed + + + −
**3.9298**; + − + − 3.9484; + + − − 3.9767; a FLAT row of two (type F) **3.9347**; a row of three 3.9814 (flat) /
4.0126 (tilts ≥ 3°); two rows of three ≥ 4.0004.  **On [3.82, ŝ] the family D′ is the only pinwheel of rows [M,
margin 0.053 in s].  On the stretch window the room must also face the mixed ring + + + − (from 3.9298; exact
rational witness at s = 3.95, `results/exact258.json` W2) and flat rows (from 3.9347).**  Third box meeter as the
ninth square: none found on the C4 slice [M].  Extent of D at 3.82: per-wall tilts 1.5° … 29° with spread up to 24°
(equal tilts are NOT forced); `results/scan258.jsonl`.

## 6. The HELD POKER — what the room statement needs (coordinator's addendum; `normal_ring.md` P4, §2.1)

The normal form now carries the RETREAT potential Φ₄ = −#{(border cell, non-toucher) incidences}.  Consequences for
a normal-form family-stuck packing = ring (this family) + three free squares F, G, H:

* [T] **P4.**  No re-posing of F, G, H (singly or jointly, by teleport — Lemma CELLS — hence also by any motion)
  inside the ring's pocket lowers the number of border cells they meet.  If EVERY packing at side s is family-stuck
  (the second horn), then EVERY placement of three unit squares in the pocket contains a tooth poker.
* [T] the seated poker F (tilt φ_w, lowest vertex at the tooth apex (a_w + sec φ_w, cos φ_w)) is free, relative to
  Q1 and Q2, to translate in the closed cone of the row's edge directions u = (cos φ, sin φ), v = (−sin φ, cos φ);
  along v it leaves the band d < 1 after **τ_v = sec φ − 1**, along u after tan(φ/2); then it meets no border cell.
  A general tooth poker (any tilt, a vertex in tooth ∩ ribbon ∩ {d < 1}) has depth ≤ 1 − cos φ_w below d = 1.
* [M] the ring never obstructs the v-slide (tight C4 rings, 5 tilts × 4 sides: sliding contact only), and ring +
  retreated F has Hall minimum 0 (`results/retreat258.jsonl`; exact at s = 3.877: `exact258.json` W1).
* **HELD-POKER(11) — the statement for A259.**  *For a ring in D′ (and the locked walls of §7) and a tooth poker F on
  wall w, the pocket holds no unit square G, interior-disjoint from the ring and from F, that meets the sweep
  {F + τd : 0 ≤ τ ≤ τ_d}, d in F's free cone.*  It is IMPLIED by NORMAL-ROOM ≤ 1, and it is all the chain needs:
  with it P4 fails, so no normal-form family-stuck packing contains the ring.  It is a TWO-square statement in a
  pocket where F is nearly pinned (3 coordinates confined to the tooth: ≈ 0.03 × 0.15 × a few degrees).
  [M] much more is true on the samples: NO tenth unit square fits anywhere beside the seated poker — sup gap
  −0.10 … −0.17 at 3.82, −0.07 … −0.15 at ŝ, **−0.006 … −0.07 at 3.99** (13 rings, 12 starts, hard containment;
  the margin dies as s → 4, as HOLE-ONE's does).
* The blocker chain: G must itself be unable to retreat JOINTLY with F (E5 with j = 2), so either the ring holds G
  from the far side (G spans from F's upper edge to the opposite row: the hole is s − 2(cos + sin) ≈ 1.44 across at
  14.5°, F's top is at depth cos + w ≈ 2.19 of 2.66 — no unit square fits above F) or H holds G.  So the room needed
  is: F in the tooth + G beside / above it in F's retreat sweep + possibly H — inside a pocket measured at capacity 1.

## 7. The LOCKED wall (hybrid family D^h) — `normal_ring.md` §3.5

On 43 of 44 corpus ring + poker rows the poker's wall is NOT a row: its normal cell T is met by W and by the poker.
Parameters of a locked wall: (a, φ₁) for s₁, (b, φ_W) for W, open gap e = s − a − b − sec φ₁ − w(φ₁) > 0 (measured
0.0005 … 0.13 when φ_W = φ₁), and a free square with a vertex in the open notch between them; corner conditions as
(D4) with the wall's own tilts.  D^h = D′ with r ∈ {0..3} walls replaced by locked walls: 8 + 2r coordinates + s.
With the poker lifted every corpus ring normalises into D (46/46), so D′ is the right FIRST target; r ≥ 1 is what
remains if NORMAL-ROOM is proved on D′ only (then r ≥ 2 by counting: `normal_ring.md` §5).
