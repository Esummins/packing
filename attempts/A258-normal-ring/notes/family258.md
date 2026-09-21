# family258 — the NORMAL RING at m = 4: parametrisation and the exact domain D  (A258; for A259)

**VERSION 1 — DRAFT, 2026-09-21.**  Tags: [T] proved here (elementary, closed form), [M] checked numerically
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

## 5. What is NOT in this file yet (VERSION 2 will say)

Mixed senses, rows of three, type-F (flat) rows, a third box meeter as the ninth square: `normal_ring.md` §3–4 and
`results/`.  Whether D should carry the (D3) cut: keep D′ for the room until then.
