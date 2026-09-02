# pair-certificate-v1 — spec (A66, 2026-09-02; status: PILOT — verifier is NEW trusted code)

**Verifier:** `attempts/A66-corners4-pair/code/verify_pair.py` (reference implementation,
written FROM this spec). **This format's verifier is NOT part of the frozen TCB**: it is a new
trust investment (C3 scale). This document is normative and written for clean-room
reimplementation; a certificate is citable only alongside its verifier version + settings,
and composition-grade use requires a second implementation or a Lean port (as for
`checkMeasureI`). The frozen verifiers (`verify_measure.py`, `verify_case.py`,
`verify_param.py`) are untouched and cannot check this format.

**Mathematical companion:** `docs/proofs/pair_kill.md` (Lemma P, Corollary P0, the
closed-vs-interior bridge for pair rows, the exact stuckness clause, the death-witness
criterion, the A34 non-applicability argument). The lemma consumes ONLY the claim frozen
here.

## 1. The claim a PASS establishes

The certificate declares a side `s`, class data (k axis cores, m axis boxes, integers N, m),
a rational `beta` ≥ 0, and an atomic pair measure: atoms ((p_i, p′_i), w_i ≥ 0) with
W₂ = Σ w_i. A PASS establishes, as one theorem:

> **(P1′)** W₂ < C(N,2) + beta·m, and
> **(P2′)** for every unordered pair {Q, Q′} of closed unit squares in [0,s]² (any
> orientations) such that (i) neither Q nor Q′ meets any core K_j (closed intersection),
> and (ii) int Q ∩ int Q′ = ∅, the collected mass
>   μ₂{Q,Q′} = Σ { w_i : (p_i ∈ Q and p′_i ∈ Q′) or (p_i ∈ Q′ and p′_i ∈ Q) }
> satisfies μ₂{Q,Q′} ≥ 1 + beta·m₂(Q,Q′), where
>   m₂(Q,Q′) = #{ i : int Q ∩ int B̃_i ≠ ∅ and int Q′ ∩ int B̃_i ≠ ∅ }.

Bridge to packings (one paragraph, proved as Lemma P / Corollary P0 in the companion): for a
class-S certificate with slack pin cores (half-side 1/2 − δ) and boxes widened by
ε_box ≥ 3·δ/(5/2 − δ), a PASS kills every teleport-stuck packing with skeleton exactly S at
every side m̃ ∈ (s/(1 + δ/(5/2)), s); with beta = 0 it kills every packing containing the
pins at those sides (emptiness), stuckness unused.

## 2. Certificate fields (JSON)

All numbers are exact rational strings; JSON floats are rejected.

| field | type | meaning |
|---|---|---|
| `format` | `"pair-certificate-v1"` | required |
| `s` | rational string | container side |
| `n` | int (default 11) | family size of the bridged application |
| `k` | int | number of cores; N = n − k |
| `m` | int | number of boxes (may be 0 when `beta` = 0) |
| `beta` | rational string ≥ 0 | boost weight |
| `cores` | `[{"kx","ky","a"},…]` | k closed AXIS-ALIGNED squares, centre (kx,ky), half-side a ≥ 0 |
| `boxes` | `[{"bx","by","h"},…]` | m closed axis squares, centre (bx,by), half-side h |
| `atoms` | `[{"px","py","qx","qy","w"},…]` | atom pairs; w ≥ 0; (px,py) ≠ (qx,qy) recommended (a coincident atom can never be collected) |
| `total` | rational string (opt) | must equal Σw; computed value governs |
| `provenance` | any (opt) | ignored |

The kill thresholds and shell arithmetic (δ, ε_box, λ_max) are NOT verified here; they are
side conditions of Lemma P checked by the composition (as ρ(C) is for case-lp certificates).
The verifier checks exactly (P1′) and (P2′).

## 3. Decision procedure (normative)

Notation: a *factor box* is F = [t0,t1]×[x0,x1]×[y0,y1] (t = tan(θ/2) ∈ [0,1] as in
case-lp-certificate-v1; same width function w(t) = cosθ + sinθ and admissible-centre clip).
A *pair box* is an ordered pair (F, F′) of factor boxes; the search must cover every
unordered pair of placements, which the reference implementation does by enumerating root
pair boxes (F_i, F_j) with i ≤ j over the initial split grid and treating atoms
symmetrically (both orientations of each atom are always summed, per (P2′)).

Root: t ∈ [0,1], centres in [w_min/2, s − w_min/2]² per factor; initial split `--split k`
into 4^k centre boxes per factor (default 2), all pairs (i ≤ j) enqueued. A pair box is
**discharged** iff one of:

1. **VACUOUS** — either factor has no admissible placement: centre ranges clipped to
   [w_lo/2, s − w_lo/2], w_lo = min(w(t0), w(t1)); empty clip ⇒ discharge, else replace the
   factor by its clip (contains every admissible placement).
2. **EXEMPT-core** — for every placement in one factor, Q meets some single core K_j:
   sufficient conditions on the four separating axes with θ_j = 0 (axis cores):
   on the two coordinate axes |c − k|_axis ≤ a + w(t)/2 for ALL t in the factor's t-range
   (use the lower bound of w on the range), and on Q's own axes
   |u-coordinate of (c − k)| ≤ 1/2 + a·g with g a lower bound of |cos θ| + |sin θ| = w(t)
   on the range — all evaluated with outward interval enclosures; grant only when certain
   for the whole factor.
3. **NONDISJOINT** — every pair in the pair box has intersecting interiors, certified by
   the SAT converse: two closed convex polygons have overlapping interiors iff EVERY edge
   normal fails to weakly separate, i.e. |Δc·u| < (w_Q(u) + w_Q′(u))/2 strictly on all four
   normal directions (the two squares' own axes; for a pair of squares, 4 directions up to
   sign). Certified over the pair box when, for each of the four directions, an outward
   interval enclosure gives sup |Δc·u| < inf of the half-width sum over the t-ranges. A fast
   sufficient pre-test: sup ‖Δc‖² < 1 (inscribed open disks of radius 1/2 intersect). Then
   (ii) fails for every pair in the box: no row to check.
4. **COVERED** — CERTAIN collected mass ≥ 1 + beta·U, where:
   * an atom i is *certainly collected* iff (p_i certainly ∈ Q for all placements of F and
     p′_i certainly ∈ Q′ for all of F′) or the swapped condition; certain membership of a
     point in all placements of a factor box uses the exact body-frame test of
     case-lp-certificate-v1 §3.4 (|u|, |v| ≤ 1/2 under outward interval enclosures of the
     rotation over the t-range and centre box);
   * U = #{ i : F possibly-meets B̃_i and F′ possibly-meets B̃_i }, where possibly-meets is
     the negation of certain axis-separation: box B̃ (half-side h) and every placement of F
     are interior-disjoint if on some axis (two coordinate axes with threshold h + w/2, or
     Q's own axes with threshold 1/2 + h·w… evaluated with enclosures) separation is
     certain; if no axis certainly separates, count the box as possible. U is an upper
     bound for m₂ over the pair box, so the test is conservative.
5. Else bisect the widest dimension among the six (t-widths weighted by `--tscale`,
   default 2), preferring the factor with larger weighted width; children inherit certainly
   collected atoms monotonically (may only grow) — the reference implementation recomputes.

A pair box undischarged after `--depth` bisection levels is a FAIL witness (reported with
its six intervals and the deficit). Exit codes: 0 PASS, 1 FAIL, 2 malformed / (P1′) violated
(Σw ≥ C(N,2) + beta·m proves nothing).

**Arithmetic.** v1 decision path: exact `fractions.Fraction` comparisons throughout (no
integerisation; certificates at pilot scale are small). Floats may be used ONLY to shortlist
candidates whose acceptance is then decided exactly; a missed shortlist hit may cause
spurious FAIL, never spurious PASS.

**Conservativity ledger** (a referee checks these four): VACUOUS clips outward; EXEMPT-core
grants only on certain whole-factor overlap; NONDISJOINT discharges only on certain
whole-box interior overlap; COVERED under-counts mass (certain membership) and over-counts
the bonus requirement (possible meeting). Every error direction makes PASS harder.

## 4. Report (C7)

`--report` writes `<cert>.report.json`: `depth`, `tscale`, `split`, `jobs`, counts
{pairs_examined, vacuous, exempt_core, nondisjoint, covered, split, max_depth}, W₂,
threshold, and the verifier file's sha256. A PASS at weaker settings than cited is not that
PASS. Re-verification convention: cold single invocation at the citing depth.

## 5. Known limitations

* Tangency: rows needing an atom exactly on ∂Q are uncertifiable (box methods); atoms must
  collect with positive margin.
* PASS is at the single declared s; window coverage = slack-core grid slabs (Lemma P shell)
  or a future parametric form.
* Axis-aligned cores and boxes only (v1) — sufficient for every slot-pinned class.
* One implementation, new trust. The A62 TCB discipline applies: this format enters the
  composition only with the pair (spec, verifier hash) cited, and the C3 second
  implementation must be written from THIS document.
