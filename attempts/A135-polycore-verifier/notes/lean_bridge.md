# T3 — the Lean bridge: T5‴ as a single-witness leaf, and the v3 exemption lemma

A135, 2026-09-07. New file `lean/PackingCertMathlib/PackingCertMathlib/PolyCoreT5.lean`
(365 lines). **It compiles clean** — `lake env lean PackingCertMathlib/PolyCoreT5.lean` exits 0,
zero errors, zero warnings, zero `sorry`.

## Roster

| name | kind | axioms |
|---|---|---|
| `PBox`, `InPBox` | definitions — a rational parameter box carrying its tilt range `[t0,t1]`, `t = tan(θ/2)` | — |
| `affine_nonneg_of_endpoints` | **theorem** — 1-D affine, nonneg at the endpoints ⇒ nonneg on the interval | — |
| `biaffine_nonneg` | **theorem** — the 2-D corner reduction | — |
| `biaffine_bound` | **theorem** — `\|K − A·cx − B·cy\| ≤ 1/2` at four corners ⇒ on the rectangle | — |
| `abs_proj_le_half` | **theorem** — the two rational quadratics of A132 spec §1 ARE `\|u cos θ + w sin θ\| ≤ 1/2`, after clearing `1 + t²` | — |
| `cornerPolys`, `allPos`, `checkCorner`, `checkVertexInPBox` | definitions — the decidable rational check | — |
| `allPos_sound` | **theorem** — the positivity certificates transfer | — |
| `corner_proj` | **theorem** — one corner's four quadratics give that corner's two projection bounds | — |
| **`checkVertexInPBox_sound`** | **theorem** — a passing check ⇒ `v ∈ q.set` for EVERY pose in the box | `propext, Classical.choice, Quot.sound` |
| `StrictlyInside` | definition — the interior form | — |
| `InteriorFromMargin` | `[C]` `Prop`, statement only | — |
| **`shared_point_same_square`** | **theorem** — T5‴, the deployable leaf | `propext, Classical.choice, Quot.sound` |
| `polySet`, `PolySetSubsetPose`, `PolycoreExemptSound` | route-(2)/(3) statements, `[C]` | — |

`#print axioms` on both headline theorems returns exactly the three Mathlib standard axioms.
**The project's axiom count is unchanged**; no `axiom` command and no `sorry` appears in the file.

## The T5‴ leaf, and why the polygon vanishes

A132 spec §4.1: `core_meet_same_square`'s `hne` needs ONE point in both cores, and
`polycore.overlap_witness` already produces and certifies it. Taking `K = K' = {w}`:

```lean
theorem shared_point_same_square {n : ℕ} {s : ℝ} {Q : Fin n → Set RP} (hP : IsPacking n s Q)
    {i j : Fin n} {B B' : PBox} {w : ℚ × ℚ}
    (hw : StrictlyInside B w) (hw' : StrictlyInside B' w)
    (hi : ∃ q : PSq, InPBox B  q ∧ Q i = q.set)
    (hj : ∃ q : PSq, InPBox B' q ∧ Q j = q.set) : i = j
```

three lines of proof, because `Zones.core_meet_same_square` is already stated for arbitrary sets.
`polycore.py`'s θ-grid clipping, `1e-6` shrink, vertex simplification and rational hull are the
**search device** that finds `w`; none of it enters the proof.

## What A135 added beyond A132's sketch, and what it did NOT

A132 sized `checkVertexInPBox_sound` at "≈ 1 day for someone fluent in the file" and listed it as
the one remaining obligation. It is **now proved**, and it turned out to have two halves, only one
of which A132's spec names:

1. **the quadratics** — `abs_proj_le_half`. Multiplying by `1 + t² > 0` turns
   `|u cos θ + w sin θ| ≤ 1/2` into the pair `(½ ∓ u) ∓ 2w t + (½ ± u) t² ≥ 0`, and rational
   nonnegativity on `[t0, t1]` is discharged by **`LocalCertT.posCheck`** — A133's Bernstein
   positivity checker, reused verbatim, so no new decision procedure enters the TCB. (The
   certificate list is data: `posAux a b c m` with nonnegative coefficients reproducing the
   polynomial. Degree elevation always supplies one for a strictly positive quadratic.)
2. **the corner reduction** — `biaffine_bound`. `polycore.vertex_ok` states in a comment that
   "`c` enters affinely, so its max over the rectangle is at a corner"; in Lean that is a lemma,
   and it is the half A132's sketch left implicit. Two applications of a 1-D affine lemma
   (`(b−x)·f(a) + (x−a)·f(b) = (b−a)·f(x)`), fixing `cy` then `cx`.

Not done, and named: **`InteriorFromMargin`**. `core_meet_same_square` consumes
`K ⊆ interior (Q i)` while the check certifies the CLOSED square; the emitter's `1e-6` inward
shrink is what supplies the strictness (A132 spec §1, "Shrink and interiors"), and running the
same sixteen quadratics with `≥ m > 0` is the step. This is **not a new hole**: it is the
closed-vs-interior bridge A62 recorded as a HIGH gap "at every kill" and A63 closed for the square
core. `code/fold135.py` discharges its *arithmetic* side for every witness in the ledger — each of
the 64 is re-certified against both boxes GROWN by `1e-7` in `x` and `y`, which forces distance
`≥ 1e-7` from the boundary of every pose (64/64 pass, see `notes/certified.md`).

## The v3 exemption lemma, and what remains

```lean
def PolycoreExemptSound : Prop :=
  ∀ (n : ℕ) (s : ℝ) (Q : Fin n → Set RP) (i j : Fin n) (B : PBox) (V : List (ℚ × ℚ)) (qj : PSq),
    IsPacking n s Q → (∀ v ∈ V, StrictlyInside B v) →
    (∃ q : PSq, InPBox B q ∧ Q i = q.set) →
    Q j = qj.set → (interior qj.set ∩ polySet V).Nonempty → i = j
```

— "a placement meeting int `K′` meets the conditioned square at every pose, hence is not a
competitor", in `ParamNoFam.lean`'s `[C]` style. Three obligations remain, in increasing novelty:

* **(a) `PolySetSubsetPose`** — every vertex inside every pose ⇒ the hull is. Needs only
  `Convex ℝ (PSq.set q)`, which via `mem_set_iff_uv` is `Convex.inter` of two half-plane-style
  sets, then `convexHull_min`. Half a day; `checkVertexInPBox_sound` supplies the generators.
* **(b) the vertex-in-all-poses step over `t`** — **done** (`checkVertexInPBox_sound`). A133's
  `LocalCertT` monotone bounds (`cosT_anti`, `sinT_mono`, `cosT_mem`, `sinT_mem`) are the
  ingredients the brief points at; in the event `posCheck` subsumed them, because clearing
  `1 + t²` turns the whole question into rational polynomial positivity and no cos/sin enclosure
  is needed at all. That is the cheapest surprise of T3.
* **(c) the separating-axis step** — "no separating axis on the union of both edge-normal families
  ⇒ the convex polygon and the square meet", which is what
  `verify_case_v3.polycore_exempt_frac` decides. This is the **only genuinely new** obligation, and
  it is the same one `ParamNoFam.TCLeaf` and `Band.lean` are already blocked on (SAT for two
  interior-disjoint convex polygons, recorded as not formalised in this development). Closing it
  discharges three leaves at once, which is the reason to do it rather than three separate
  work-arounds.

`CaseSat.sat_squares` (`CaseSat.lean:265`) is the square-vs-square instance already proved in the
file, so (c) is the polygon generalisation of an argument the development owns, not a new one.

## Roster slot

`docs/known_results.md` line 23 ("logic-kill rules T5/T11") gains **T5‴ (shared witness point)**;
the theorems live in `PolyCoreT5.lean` (imported by nothing yet — a new leaf file, so
`PackingCertMathlib.lean`'s import list is untouched and CI is unchanged until the owner adds it).
