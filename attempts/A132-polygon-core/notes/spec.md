# Spec — the polygon core K′(B): certificate field, verifier v3, Lean lemma

Status: **WRITE ONLY.** Nothing here is deployed. `verify_case.py`, `verify_param.py` and
`verify_param_v2.py` are byte-identical to their frozen versions; this document describes a **v3**
that would live in a *copy* with its own sha. A132, 2026-09-07.

---

## 0. The object

For a parameter box `B = [x0,x1] × [y0,y1] × [θ0,θ1]`,

> **K′(B) = ⋂ over (c, θ) ∈ B of Q(c, θ)**, the intersection of the unit squares over the whole box.

It is convex (an intersection of convex sets) and it **contains** the rational square
`K(a) = Box.core(B)` that A13/A57 use today, because `K(a)` is *one* square inside that
intersection while `K′` is the intersection itself. Measured over 506 alive nodes (T1):
`area(K′)/area(K(a))` has median **1.225**, range 1.01–1.53 — and the gain is concentrated exactly
where the axis core is weakest, i.e. wide tilt bins at level 1.

Implementation: `code/polycore.py` (build + exact certification + SAT), 300 lines, no dependency
on any driver, imports A57's `caselp` read-only.

### 0.1 The three routes, and which one is free

| route | what it buys | verifier change | certificate change | status |
|---|---|---|---|---|
| **(1) T5-polygon logic kill** — `K′(B)` meets a pin's `K′(P)` ⇒ node empty | kills with **no LP and no certificate** | **none** | **none** | ready to deploy (T1: 37 of 506 alive nodes) |
| (2) LP column/row pruning — drop placements meeting `int K′` of ANY hypothesis box | kills the LP does not have today | **yes** (v3, below) | yes (`polycores` field) | 3 of 3 decided pairs killed in vitro (T2, §5) — worth building, after an unselected rate |
| (3) coverage-row exclusion in the certificate | same as (2) | same as (2) | same as (2) | same |

Route (1) needs nothing from the verifier because **a logic kill emits no certificate**. This is
precisely the argument A96 recorded when it deployed T5′ (the tight core): *"the kill certificate
itself is UNCHANGED (T5, Lean `core_meet_same_square`); only the … core the rule is applied to has
grown"*. The polygon core is the same move one step further — the rule is applied to the largest
sound set there is.

**Soundness of routes (2)/(3), stated once.** The certificate's exemption is "`Q` provably meets a
core". Its bridge argument is: the `n − #cores` squares *other than* the core witnesses are
non-exempt, pairwise disjoint, each of mass ≥ 1. A placement meeting `int K` for a hypothesis box's
`K` cannot be one of those others — it overlaps the witness of that box, so it either *is* that
witness or contradicts disjointness. That argument uses only `K ⊆ Q(c,θ) for every pose in the box`,
which is exactly what `K′` satisfies and what the vertex check certifies. **Nothing about the
argument changes; only the set grows.** This applies to the PIN boxes as much as to the conditioned
one — they are boxes with the same hypothesis shape — which is where a good part of T2's effect
turns out to live (§5).

---

## 1. Certification of K′ — exact, in rationals

`K′` is convex, so it suffices to certify **vertices**: if every vertex `v` of a candidate polygon
`P` lies in `Q(c, θ)` for all `(c, θ) ∈ B`, then `conv(P) ⊆ K′(B)`, *however `P` was found*. The
construction (clip on a θ grid, shrink by `1e-6`, delete negligible vertices, round to `1/10⁹`,
exact rational hull) is therefore heuristic and unaudited; the vertex test is the proof.

The vertex test, with `d = v − c` and the corpus's own rational parametrisation `t = tan(θ/2)`
(`cos = (1−t²)/(1+t²)`, `sin = 2t/(1+t²)`):

```
for each of the 4 CORNERS c of the centre rectangle,             (c enters affinely: max at a corner)
and for (u, w) = (dx, dy) and (dy, −dx):                          (the two edge normals of Q)
    P1(t) = (1/2 + u)·t² − 2w·t + (1/2 − u)  ≥ 0   on [t0, t1]
    P2(t) = (1/2 − u)·t² + 2w·t + (1/2 + u)  ≥ 0   on [t0, t1]
```

`t0 = caselp.t_lo(θ0)`, `t1 = caselp.t_hi(θ1)` are the corpus's **outward-rounded** tilt bounds, so
the certified statement is about a tilt range *containing* `[θ0, θ1]`. Nonnegativity of a rational
quadratic on a rational interval is decided exactly: both endpoints, plus `4AC − B² ≥ 0` when
`A > 0` and the stationary point `−B/(2A)` is interior. `polycore.vertex_ok`, 12 lines.

Cost: 40 vertices × 4 corners × 2 normals × 2 quadratics = 640 exact quadratic tests per box,
**0.07 s**. Building + certifying all 506 alive nodes and their pins took 41 s in one process.

**Shrink and interiors.** T5 needs `K ⊆ interior(Q)`, not `K ⊆ Q`. The `1e-6` inward offset applied
to every half-plane before clipping is what supplies it: every certified vertex satisfies the four
inequalities with slack, so the polygon is inside the open square. The verifier must re-derive this
(it is a strict inequality in the same test), not inherit it from the builder.

---

## 2. The certificate field

```jsonc
"hypotheses": {
  "cores": [ { "kx": ..., "ky": ..., "tm": ..., "a": ..., "box": {...} }, ... ],   // unchanged
  "polycores": [                       // v3, OPTIONAL: absent ⇒ v1/v2 semantics exactly
    { "core": 4,                       // index into `cores`: which conditioned core this refines
      "box": { "x0": "...", "x1": "...", "y0": "...", "y1": "...",
               "t0": "...", "t1": "..." },        // RATIONAL, and carrying the TILT RANGE
      "verts": [ ["x","y"], ... ] }               // rational, ccw, 3..64 of them
  ]
}
```

Two notes on the box field. (a) The s0 certificate **already** carries `box` next to each core
(`caselp.make_certificate` writes `box=c.box.to_json()`), but as *floats* and with the verifier
ignoring it; v3 must carry it as rationals with `t0/t1` rather than only `tm`. (b) The parametric
certificate (`verify_param`) carries no box at all — its cores are `akx,bkx,aky,bky,tm,a`. A
parametric polygon core needs the vertices to be s-affine too (`av + bv·s`); that is a strictly
bigger job than the s0 one and is **out of scope of this spec**.

**Verifier's first step** (before any box discharge): re-run §1 on every listed polygon. A
`polycores` entry that does not certify is a hard reject, not a warning. That is the whole trust
story: the emitter's polygon is untrusted data, the vertex test is the audit, and everything
downstream uses only the certified vertex list.

---

## 3. The verifier change (v3) — one new exemption clause

`verify_case.Verifier.exempt(T0,T1,X0,X1,Y0,Y1)` today returns True iff the `(t, cx, cy)`-box is
provably inside a NO-family (`nofam_exempt`) or provably meets a core (`core_exempt_frac`).
v3 adds a third disjunct, evaluated after the other two:

```python
def polycore_exempt_frac(poly, t0, t1, x0, x1, y0, y1):
    """True iff for EVERY (t, cx, cy) in the box the closed unit square Q(c, theta(t))
    meets the convex rational polygon `poly` (SAT over the union of both edge-normal
    families, proven by outward interval arithmetic)."""
```

The decision procedure, axis by axis — the same shape and the same helpers as
`core_exempt_frac` (`cos_sin_t`, `imul4`, the `Alo/Babs` lower bound on `|cos| + |sin|`):

* **the polygon's own edge normals** `n_k` (fixed rationals, need not be unit). Let
  `[P_lo(n_k), P_hi(n_k)]` be the exact projection range of the vertices. `Q`'s half-width in that
  direction is `h_Q(n_k, t) = (|n_k·f1| + |n_k·f2|)/2` with `f1 = (C, S)`, `f2 = (−S, C)`; bound it
  **below** over `[t0,t1]` with the existing `Alo/Babs` trick. Require, with `n_k·c` maximised /
  minimised over the four box corners (exact, affine in `c`):
  `max_c n_k·c ≤ P_hi + min_t h_Q` and `min_c n_k·c ≥ P_lo − min_t h_Q`.
* **the square's own two axes** `f1(t), f2(t)`. The polygon's projection range is now `t`-dependent:
  bound `max_v f·v` **below** and `min_v f·v` **above** by `imul4(C0,C1,vx,vx) + imul4(S0,S1,vy,vy)`
  over the vertex list. Require `max_c f·c − 1/2 ≤ (max_v f·v)_lo` and
  `min_c f·c + 1/2 ≥ (min_v f·v)_hi`.

Accept only when **every** inequality holds, with left sides rounded up and right sides rounded
down. A float pre-filter (`polycore_exempt_float`, `slack = 1e-7`) shortlists; it never decides.
Everything else in the verifier — the box tree, `covered`, the witness machinery, the mass
arithmetic — is untouched.

**How this composes, exactly as v2's NO-family clause did.** A117/A96's v2 added `nofam_exempt_frac_iv`
as a *disjunct in front of* the frozen core clause and changed nothing else: `exempt` became
"NO-family, else core", the corpus was re-run under v2 to check that every v1-passing certificate
still passes (the new clause only *adds* exemptions), and the Lean side gained one exemption lemma
that the bridge discharges alongside the core one. v3 is the identical pattern with a third
disjunct: `exempt` becomes "NO-family, else core, else polygon", old certificates carry no
`polycores` field and take the v1/v2 path byte-for-byte, and the bridge gains one more discharge.
The three clauses are independent — no clause reads another's data — so the composition is
disjunctive and needs no interaction proof.

---

## 4. Lean

The pleasant surprise: `Zones.core_meet_same_square` is **already fully general**. Its statement is

```lean
theorem core_meet_same_square {n : ℕ} {s : ℝ} {Q : Fin n → Set RP} (hP : IsPacking n s Q)
    {i j : Fin n} {K K' : Set RP} (hK : K ⊆ interior (Q i)) (hK' : K' ⊆ interior (Q j))
    (hne : (K ∩ K').Nonempty) : i = j
```

— arbitrary **sets** `K`, `K'`, no squareness anywhere. So the T5-polygon logic kill (route 1)
needs **no new consumer theorem**; it needs only the containment lemma that feeds `hK`. In the
file's own vocabulary (`Parametrize.PSq` = `(cx, cy, t)` with `t = tan(θ/2)`, `PSq.set` the closed
unit square, `mem_set_iff_uv` its `|u| ≤ 1/2 ∧ |v| ≤ 1/2` characterisation, `CaseHyp.coreSet` the
existing square core):

```lean
/-- A parameter box, rational, carrying its TILT RANGE (the certificate's `box` field). -/
structure PBox where
  x0 x1 y0 y1 t0 t1 : ℚ

def InPBox (B : PBox) (q : PSq) : Prop :=
  (B.x0:ℝ) ≤ q.cx ∧ q.cx ≤ (B.x1:ℝ) ∧ (B.y0:ℝ) ≤ q.cy ∧ q.cy ≤ (B.y1:ℝ) ∧
  (B.t0:ℝ) ≤ q.t  ∧ q.t  ≤ (B.t1:ℝ)

/-- The polygon core denoted by a rational vertex list: its convex hull. -/
def polySet (V : List (ℚ × ℚ)) : Set RP :=
  convexHull ℝ {p : RP | ∃ v ∈ V, p = ((v.1 : ℝ), (v.2 : ℝ))}

/-- **The vertex check is the whole content.**  Decidable, rational: the two quadratics of §1
evaluated at `t0`, `t1` and (when `A > 0` and the stationary point is interior) `4AC - B² ≥ 0`,
over the four corners of the centre rectangle and the two edge normals. -/
def checkVertexInPBox (B : PBox) (v : ℚ × ℚ) : Bool := ...

theorem checkVertexInPBox_sound {B : PBox} {v : ℚ × ℚ} (h : checkVertexInPBox B v = true) :
    ∀ q : PSq, InPBox B q → ((v.1 : ℝ), (v.2 : ℝ)) ∈ interior q.set

/-- **The polygon core.**  Every vertex inside every pose ⇒ the hull is inside every pose. -/
theorem polycore_subset_pose {B : PBox} {V : List (ℚ × ℚ)}
    (hV : ∀ v ∈ V, checkVertexInPBox B v = true) :
    ∀ q : PSq, InPBox B q → polySet V ⊆ interior q.set := fun q hq =>
  convexHull_min (by rintro p ⟨v, hv, rfl⟩; exact checkVertexInPBox_sound (hV v hv) q hq)
                 (Convex.interior (convex_PSq_set q))

/-- **T5-polygon.**  The polygon core of a YES child's box meets the polygon core of a pin:
the child's witness IS the pinned square, so the child is empty by logic.  A specialisation of
`core_meet_same_square`, not a new argument. -/
theorem polycore_meet_same_square {n : ℕ} {s : ℝ} {Q : Fin n → Set RP} (hP : IsPacking n s Q)
    {i j : Fin n} {B B' : PBox} {V V' : List (ℚ × ℚ)}
    (hV  : ∀ v ∈ V,  checkVertexInPBox B  v = true)
    (hV' : ∀ v ∈ V', checkVertexInPBox B' v = true)
    (hi : ∃ q : PSq, InPBox B  q ∧ Q i = q.set)
    (hj : ∃ q : PSq, InPBox B' q ∧ Q j = q.set)
    (hne : (polySet V ∩ polySet V').Nonempty) : i = j := by
  obtain ⟨q, hq, rfl⟩ := hi; obtain ⟨q', hq', rfl⟩ := hj
  exact core_meet_same_square hP (polycore_subset_pose hV q hq)
                                 (polycore_subset_pose hV' q' hq') hne
```

Three obligations, in decreasing size. (a) `checkVertexInPBox_sound` — the two rational quadratics
of §1, the same shape as the existing `core_exempt` decision procedure; it should reuse
`Parametrize`'s `cosT`/`sinT` and `CaseHyp`'s cast lemmas rather than introduce new ones, and the
*strict* version (interior) is what the `1e-6` shrink pays for. (b) `convex_PSq_set` — `PSq.set` is
convex; via `mem_set_iff_uv` it is an intersection of four half-planes, so this is
`Convex.inter`/`convex_halfspace_le` plumbing. (c) `polycore_meet_same_square` itself, which as
written above is four lines because `core_meet_same_square` does the work.

### 4.1 The collapse: for the LOGIC KILL, Lean never sees a polygon

`hne` only needs *one point* in both hulls. That point is rational and the implementation already
produces and certifies it (`polycore.overlap_witness`: 64/64 on the firing nodes, each verified
exactly against **both** boxes by `vertex_ok`). Take `K = K' = {w}` in `core_meet_same_square` and
the hulls, the convexity lemma and the polygon–polygon SAT all disappear:

```lean
/-- **T5‴, the deployable form.**  One rational point that the vertex check certifies for BOTH
boxes: the two witnesses are the same square, so a child requiring them distinct is empty. -/
theorem shared_point_same_square {n : ℕ} {s : ℝ} {Q : Fin n → Set RP} (hP : IsPacking n s Q)
    {i j : Fin n} {B B' : PBox} {w : ℚ × ℚ}
    (hw  : checkVertexInPBox B  w = true)
    (hw' : checkVertexInPBox B' w = true)
    (hi : ∃ q : PSq, InPBox B  q ∧ Q i = q.set)
    (hj : ∃ q : PSq, InPBox B' q ∧ Q j = q.set) : i = j := by
  obtain ⟨q, hq, rfl⟩ := hi; obtain ⟨q', hq', rfl⟩ := hj
  exact core_meet_same_square hP
    (Set.singleton_subset_iff.mpr (checkVertexInPBox_sound hw  q  hq))
    (Set.singleton_subset_iff.mpr (checkVertexInPBox_sound hw' q' hq'))
    ⟨_, rfl, rfl⟩
```

**So the polygon is a search device, not a proof object.** The kill certificate is *one rational
point plus two vertex checks*; `polycore.py`'s clipping, simplification and hull are the (untrusted)
way that point is found. The only Lean obligation left is `checkVertexInPBox_sound` — one decidable
rational test, ~1 day. `polycore_subset_pose` and `polySet` above stay in the file only for routes
(2)/(3), where the whole polygon does have to be a proof object.

For route (2)/(3) the consumer change is in the bridge, exactly as A96's spec describes for the
dominated clause: the measure statement's universally quantified `Q` gains the side condition
`¬ meetsPolycore B Q`, discharged by `polycore_subset_pose` + `core_meet_same_square`.

**Roster slot.** `docs/known_results.md` line 23 ("logic-kill rules T5/T11") gains T5‴; the theorems
go in `lean/PackingCertMathlib/PackingCertMathlib/Zones.lean` next to `core_meet_same_square`
(not `Composition.lean` — nothing here composes certificates), and the checker-side lemma in
`CaseSat.lean` beside the existing SAT machinery.

---

## 5. Sizing — and why route (2) should NOT be built

**Route (1), the logic kill.** `polycore.py` exists (300 lines). Deployment is a ~25-line change in
a *copy* of `pinguard.classify`: build `K′` for the child box and for each pin box, run the
polygon–polygon SAT, and return `("contradictory", i)` on a strict overlap — plus the existing
`box_realizes_pin` gate ahead of it, unchanged, since the `parent` case is still the case where the
identification is *consistent*. Emission cost measured at 0.07 s per box against ~850 s saved per
kill. Lean: `polycore_subset_pose` + `checkVertexInBox` ≈ **1 day** for someone fluent in the file;
`core_meet_same_square` is reused verbatim. **Re-verification cost of the existing tree: zero.**
Old certificates are untouched, no emitted certificate changes, and any *new* logic kill is a
strengthening of a rule that already exists — the same soundness story A96 wrote for T5′.

**Routes (2) and (3).** Verifier v3 as specced is ~140 lines in a copy of `verify_case.py`
(the clause, the float pre-filter, the `polycores` parse and the mandatory re-certification), ~60
lines of plumbing, a full corpus regression run, and a Lean bridge change: call it **4–6 days**
including the Lean. **Spend it.** The prediction from the file was that this route is worthless, and
the measurement refuted it.

*The prediction.* If a placement `Q_r` meets `int K′(B)` then, since `K′(B) ⊆ Q(c,θ)` for every pose,
`Q_r ∩ Q(c,θ) ≠ ∅` for every pose — `Q_r` is *dominated by B* in the sense of
`attempts/A96-a57-parametric/notes/verifier_v2_rowfilter.md` §2, and the converse fails, so
{rows dropped by `K′(B)`} ⊊ {rows dropped by the all-poses test}. The drop fractions match the
inclusion: the polygon core drops **20.5%** of the pool against the all-poses filter's median
**52.2%** (`arms96_C.jsonl`). A96 measured that stronger filter at a 900 s cap and found
`τ_C − τ_B` median **3.3e−13**, no new kills. So the polygon row filter should have bought nothing.

*The measurement (T2).* Ten alive nodes, both arms, identical warm start, identical oracle
configuration, `recheck96`'s node path. Three pairs reached convergence in **both** arms — the only
pairs that decide anything, since τ rises as rows are added. **All three are LP-dead under the
polygon core and alive under `K(a)`:** `Y0871` 5.000 → 4.000, `Y1038` 5.000 → 4.500,
`Y0281_D03` 5.000 → 4.000, every axis arm converging at exactly the budget and reproducing the
campaign's stored verdict.

*Why the file's prediction failed — the attribution arm.* Re-running the three kills with the
polygon core on the **conditioned box only** (`polybox`; the pins keeping `K(a)`, which is exactly
the scope of A96's spec): `Y1038` converges back to **τ = 5.000 — no kill**; `Y0281_D03` still kills
at 4.000; `Y0871` is inconclusive (unconverged). So at least one of the three kills lives entirely
in the part A96 never tested: **the PIN boxes also have polygon cores.** For a pin box
(`th0 = th1 = 0`, half-width `1e-2/√2`) `K′(P)` is the axis square of half-side `0.49293` against
`K(a) = 0.48999…` — a 0.6% enlargement that bites because pinned squares nearly touch. T1 measures
that channel at 6.9% of the pooled rows and **21% of the excluded dual-support weight** on A57
(`split132.py`). The second reason is selection: T2's six L1/L2 nodes were chosen for the *largest*
offending weight, which A96's 32-node sample was not.

*The honest limit.* Three converged pairs, on nodes selected for the lever, is not a rate. The
number that prices the verifier work is the kill rate over an unselected sample, and nobody has it.

---

## 6. What to do next, in order

1. **Deploy route (1)** — the T5‴ logic kill. Free, no verifier, no certificate, 37 nodes in hand.
2. **Measure the LP rate honestly** before building v3: the same two-arm test on ~30 *unselected*
   alive nodes at a cap generous enough that both arms converge (the three decided pairs here took
   73–815 s per arm; budget ~10 CPU-h). If the converged-pair kill rate holds anywhere near 3/3, v3
   is the cheapest wall-day on the board; if it collapses to A96's zero, route (1) still stands.
3. **Build v3 as specced** — and note that its exemption clause should be written for the *general*
   box, so that A96's strictly stronger all-poses clause can later replace the `K′` test inside the
   same certificate field without another verifier version.
