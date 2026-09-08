# A144 — guard lines: the cut, the certificate field, the v3 clause, the Lean statements

Written 2026-09-07 (A144, Opus). Nothing here is deployed: the frozen verifiers are untouched,
and the LP measurements of T2 are recorded as **"LP-dead under guard lines, certificate pending
v3"** exactly as A132 recorded its polygon-core kills.

---

## 0. Notation

* `s` — the container side; the node LP runs at `s0 = 969271/250000 = 3.877084`.
* A **parameter box** `B = [x0,x1] x [y0,y1] x [th0,th1]` carries the hypothesis "some square `Q0`
  of the packing has (centre, tilt) in `B`". `t0 = caselp.t_lo(th0)`, `t1 = caselp.t_hi(th1)` are
  the corpus's OUTWARD-rounded rational bounds on `t = tan(theta/2)`, so every statement below is
  about a tilt range that CONTAINS `[th0,th1]` (A132's rule, inherited verbatim).
* A **guard line** `l` is axis-parallel and inside the container: `y = h` or `x = g`, with the
  offset an exact rational in `(0, s)`.
* `chord(a, theta, v)` — the length of `l n Q` for a square of half-side `a` at tilt `theta` whose
  centre is at signed distance `-v` from `l` (the chord does not depend on the coordinate ALONG
  `l`, only on `v` and `theta`).

---

## 1. The cut

### Lemma LINE-1 (chord sum). *`code/guardline.py` header; Lean `chord_sum_le_side` below.*

Let `Q_1, ..., Q_N` be closed unit squares with pairwise disjoint interiors, all contained in
`[0,s]^2`, and let `l` be an axis-parallel line meeting the container. Then

```
    SUM_i |l n Q_i|  <=  |l n [0,s]^2|  =  s .
```

*Proof.* `Q_i` is convex, so `l n Q_i` is a closed sub-interval of `l`. If two of these intervals
shared an interior point `p`, then `p` would be an interior point of both squares (a point of `l`
interior to the chord and interior to no square would have to lie on the boundary of one of them,
and the boundary meets `l` in the two chord endpoints), contradicting disjointness. A finite family
of intervals with pairwise disjoint interiors inside an interval of length `s` has total length at
most `s` by additivity of 1-dimensional Lebesgue measure. For an axis-parallel `l` inside the
container `|l n [0,s]^2| = s` exactly. ∎

### Lemma LINE-2 (the node row). 

At a node with hypothesis boxes `B_1, ..., B_m` (the `m = #cores` pins and conditioned squares) and
`budget = n - m`, every packing of `n` unit squares in `[0,s]^2` satisfying the hypothesis has, for
each guard line `l`,

```
    SUM over the budget non-hypothesis squares Q of |l n Q|
        <=  rhs(l)  :=  s  -  SUM_j minchord(B_j, l) ,                                     (GL)
```

where `minchord(B, l) := inf over (c, theta) in B of |l n Q(c, theta)|`.

*Proof.* The hypothesis names `m` DISTINCT squares of the packing (A57's T23 pairwise-disjoint-cores
gate is what makes them distinct), each with its pose in its own box, so `|l n Q_j| >= minchord(B_j, l)`.
Apply LINE-1 to all `n` squares and move the `m` hypothesis terms to the right. ∎

### Lemma LINE-3 (the LP column). 

A57's node LP is the covering LP `tau = min mu([0,s]^2)` subject to `mu(Q) >= 1` for every
admissible non-exempt placement `Q`. Extend the admissible measures from "atomic" to
"atomic + a non-negative density `z_l` on each guard line":

```
    mu  =  SUM_k w_k delta_{p_k}  +  SUM_l z_l * H^1 restricted to l ,
    objective  :=  SUM_k m_k w_k  +  SUM_l z_l * rhs(l)          <-- rhs(l), NOT s
```

If the LP's optimum `tau < budget` the node is DEAD, exactly as before:

```
   budget  <=  SUM_i mu(Q_i)                                    (one row per packed square)
            =  SUM_k w_k * #{i : p_k in Q_i}  +  SUM_l z_l SUM_i |l n Q_i|
           <=  SUM_k m_k w_k                +  SUM_l z_l * rhs(l)     (disjointness; (GL))
            =  objective .
```

Two remarks that say what is and is not new.

* The objective coefficient is `rhs(l)`, which is SHORTER than the line. The part of the discount
  coming from the pins is not new information: a measure supported on `l` minus the pins' chords is
  a genuine measure, so an ideal column generator could already have built it out of atoms. The
  part coming from `- minchord(H, l)` **cannot** be built that way, because `H`'s position inside
  its box is unknown; that term is the whole content of the row.
* Adding columns can only LOWER `tau`, so a guard line never invalidates an existing kill and never
  needs a control for soundness — only for attribution (T2 runs one anyway).

### Which half-side to use

The LP rows are the squares shrunk by `lpbox.EPS_GEO = 1e-4`. The implementation uses the SHRUNK
half-side in the column coefficients `|l n Q_p|` and the FULL half-side `1/2` in `minchord(B_j, l)`.
Both directions are conservative: `SUM_i |l n Q_i^shrunk| <= SUM_i |l n Q_i| <= rhs(l)`, and a
smaller coefficient only makes the line cover less.

---

## 2. `minchord(B, l)` in closed form (what the verifier recomputes)

With `C = |cos theta|`, `S = |sin theta|`, `V = |v|`, the chord is the intersection of two intervals
of half-lengths `a/C` and `a/S` whose centres are `V/(CS)` apart:

```
    chord(a, theta, v) = max(0, min( A , B )),    A = 2a / max(C,S),
                                                  B = (a (C+S) - V) / (C S) .          (CH)
```

Two structural facts make the minimum over a box a FIVE-POINT evaluation.

* `chord` is non-increasing in `V`, and `V` is affine in the centre, so over the centre rectangle
  the minimum is at `V = max |offset|`, i.e. at a corner. **The chord does not depend on the
  coordinate along `l` at all**, so only one of the two centre ranges matters.
* Put `y := C + S = sqrt2 cos(theta - 45deg) in [1, sqrt2]`, so `C S = (y^2 - 1)/2` and
  `max(C,S) = (y + sqrt(2 - y^2))/2`. Then
  * `A(y) = 4a / (y + sqrt(2 - y^2))` is **increasing** on `[1, sqrt2]`;
  * `dB/dy` has the sign of `q(y) = -a y^2 + 2V y - a`, whose two roots multiply to `1`. Hence on
    `[1, sqrt2]` either `q < 0` throughout (`V < a`: `B` strictly decreasing) or `q >= 0` on
    `[1, y+]` and `q < 0` after (`V >= a`: `B` increasing then decreasing). **In both cases the
    minimum of `B` over a `y`-interval is attained at an endpoint of that interval.**

Therefore, writing `y(t)` for the value of `y` at `t = tan(theta/2)`,

```
 minchord(B, l) = max( 0, min( A(t0), A(t1), B(y(t0)), B(y(t1)),
                               B(sqrt2) if 45deg lies in the (outward-rounded) tilt bin ) )
```

with `B(sqrt2) = 2(sqrt2 a - V)` rounded DOWN to a rational (conservative). Everything else is an
exact rational expression in `t`, `V`, `a`.

Special cases, both handled explicitly:

* **zero-width tilt bin** (the pins, `th0 = th1 = 0`): `(CH)` is evaluated at that single `t`, where
  `chord = 2a` for every `V <= a`. So a pin's chord is **exactly 1** whenever the line runs through
  the pin core's height range at every position of the pin's centre box — which is the reading the
  PI made, and it is exact, not an estimate.
* **a bin of positive width touching `theta = 0` or `90deg`**: the chord is discontinuous there when
  `V = a` exactly (`2a` at the endpoint, `a` in the limit). The formula returns the LIMIT, i.e. the
  infimum, which is what `minchord` is defined to be and is a lower bound either way.

The cheap alternative `|l n K'(B)|` — the chord of A132's certified polygon core — is also computed
and reported. It is valid (`K' subset Q` at every pose) but strictly weaker; on Y0147's line it is
`0.8313` against `minchord = 1.0`, so the row uses `minchord` and `K'` is only a cross-check.

---

## 3. The certificate field `guardlines`

Added to `hypotheses`, alongside `cores`, `nofams` and A135's `polycores`:

```jsonc
"hypotheses": {
  "cores":    [ ... ],            // unchanged
  "nofams":   [ ... ],            // unchanged
  "polycores":[ ... ],            // A135, unchanged
  "guardlines": [
    { "orient": "h",                       // "h" (y = off) or "v" (x = off)
      "off":    "721771/250000",           // exact rational, 0 < off < s
      "z":      "1000200001/1000000000",   // the density, exact rational >= 0
      "rhs":    "469271/250000"            // the emitter's claim; RECOMPUTED, never trusted
    }
  ]
}
```

Nothing else in the certificate changes: `atoms`, `weights` and `total` keep their meaning, and a
certificate with no `guardlines` field is byte-for-byte v1/v3 in behaviour (the `--regress` corpus
check A135 already runs covers this).

**Emitter rule (rounding direction).** `z_l` enters the coverage check with a `+` sign and the total
with a `+` sign, exactly like an atom weight. So it is scaled and rounded **UP** on the same grid
and by the same `--scale_cap` factor as the atom weights (`certify.py`'s existing loop), and the
slack it costs is absorbed by the `total < budget` test — the same trade the atoms already make.
`rhs` is emitted rounded **DOWN**.

---

## 4. The v3 clause (`verify_case_v4.py`: a NEW file that IMPORTS v1 and A135's v3)

Discipline as A135: v1 (`verify_case.py`, sha `521cb01f...`) and `verify_case_v3.py` are frozen and
imported, never copied; the class below subclasses `VerifierV3`, so the box tree, `exempt`,
`covered`'s atom arithmetic, `make_witness`, `run` and `stats` are literally the audited code.

Four changes, all exact:

**(G1) Re-derive every right-hand side.** For each `guardlines` entry: reject unless
`0 < off < s`; then recompute
`rhs*(l) = s - SUM_j minchord(box_j, l)` over **every** declared `cores[j]`, using that core's own
declared rational box `(x0,x1,y0,y1,t0,t1)` and the five-point evaluation of Sec. 2, in Fractions.
**HARD REJECT (exit 2)** if `rhs > rhs*(l)`. A DECLARED value smaller than `rhs*` is accepted (it is
conservative and lets an emitter be sloppy in the safe direction) but the verifier uses
`min(rhs, rhs*)`. This is the analogue of A135's (P1)/(P2): the emitter's arithmetic is data.

Note what (G1) uses and what it does not: it needs only the `cores[j].box` fields — the same boxes
the bridge argument already names — and nothing about `a`, `kx`, `ky`, `tm`. So the guard clause is
independent of A135's exact-core question and of the polygon clause.

**(G2) The total.** v1 checks `total = SUM_i w_i < budget`. It becomes

```
    total  =  SUM_i w_i  +  SUM_l z_l * min(rhs_l, rhs*_l)   <   budget .
```

**(G3) The mass of a box.** v1's `covered(T0,T1,X0,X1,Y0,Y1)` decides `mu(Q) >= 1 + margin` for
every `Q` in the sub-box by bounding the atom mass from below. It gains one term:

```
    mass_lo(sub-box)  =  atom_mass_lo(sub-box)  +  SUM_l z_l * minchord(sub-box, l)
```

using the SAME five-point primitive as (G1), on the verifier's own `(t, x, y)` sub-box, with
`a = 1/2` (the verifier reasons about full closed unit squares). This is a lower bound of
`|l n Q|` valid for EVERY `Q` in the sub-box, which is exactly what `covered` requires. As the tree
bisects, `minchord` of a sub-box increases monotonically, so the clause strengthens with depth
exactly as the atom mass does — no new source of non-termination.

**(G4) Nothing else.** Exemption is decided before mass, so an exempt box never reaches (G3) and the
guard clause is orthogonal to both the core/NO-family disjuncts of v1 and A135's `polycores`
disjunct. The three compose by conjunction of independent re-checks: `polycores` grows the exempting
set, `guardlines` grows the mass and the total, and neither reads the other's fields. A certificate
may carry both.

**Machine independence.** Every guard decision is a Fraction comparison; the only irrational is
`sqrt2` and it enters only through a fixed rational under-approximation (`floor(sqrt2 * 10^24)/10^24`),
so `--replay` is bit-identical across machines. Cost: `O(#guardlines)` Fraction evaluations per box,
with `#guardlines <= 8` in practice against a median 185 atom checks — under 5% on A135's profile.

**What a PASS then certifies.** Unchanged in shape:

> every admissible closed unit square `Q` in `[0,s]^2` that is not EXEMPT has
> `mu(Q) >= 1 + margin`, where `mu` is the declared atomic measure PLUS the declared guard-line
> densities, and `SUM_i w_i + SUM_l z_l rhs_l < budget`;

together with LINE-2 and LINE-3 this kills the node by the same bridge as v1.

**Estimated size.** ~120 lines (the five-point primitive ~60, (G1)–(G3) ~40, the loader ~20) plus the
`--regress` run against the frozen verifier on A135's corpus. Comparable to A135's polygon clause.

---

## 5. Lean

Two new statements, in the style of A135's `checkVertexInPBox_sound` (a `Bool`-valued exact checker
plus a soundness theorem, so the numeric work is `decide`/`native_decide` and the mathematics is a
short proof).

```lean
/-- LINE-1.  Chords of an interior-disjoint family of squares inside `[0,s]^2`, on an
    axis-parallel line, have total length at most `s`. -/
theorem chord_sum_le_side
    {N : ℕ} (s : ℝ) (hs : 0 ≤ s)
    (Q : Fin N → Set (ℝ × ℝ))
    (hsq   : ∀ i, IsUnitSquare (Q i))
    (hsub  : ∀ i, Q i ⊆ Set.Icc (0:ℝ) s ×ˢ Set.Icc (0:ℝ) s)
    (hdisj : Pairwise fun i j => interior (Q i) ∩ interior (Q j) = ∅)
    (l : GuardLine) (hl : l.offset ∈ Set.Icc (0:ℝ) s) :
    (∑ i, (MeasureTheory.volume (l.param ⁻¹' Q i)).toReal) ≤ s

/-- LINE-2's per-box ingredient.  If the exact five-point checker accepts `(a, B, l, m)`
    then `m` is a lower bound of the chord at EVERY pose in the box. -/
def checkMinChordBox (a : ℚ) (B : ParamBox) (l : GuardLine) (m : ℚ) : Bool := ...

theorem minchord_of_box
    (a : ℚ) (B : ParamBox) (l : GuardLine) (m : ℚ)
    (h : checkMinChordBox a B l m = true) :
    ∀ c θ, InBox B c θ → (m : ℝ) ≤ chordLen a c θ l
```

`GuardLine` is a structure `(horizontal : Bool) (offset : ℚ)` with `param : ℝ → ℝ × ℝ` its unit-speed
parametrisation; `chordLen a c θ l = (volume (l.param ⁻¹' Q a c θ)).toReal`.

Supporting lemmas (all elementary, no new axioms):

| lemma | statement | route |
|---|---|---|
| `chordLen_eq` | `chordLen a c θ l = max 0 (min (2a/max ‖cos θ‖ ‖sin θ‖) ((a(‖cos θ‖+‖sin θ‖) − ‖v‖)/(‖cos θ‖‖sin θ‖)))` | the preimage is the intersection of two intervals; `Set.Icc_inter_Icc`, `Real.volume_Icc` |
| `chordLen_antitone_offset` | `chordLen` is antitone in `‖v‖` | from `chordLen_eq`, both branches |
| `chord_A_mono` | `A(y) = 4a/(y + sqrt(2−y²))` is monotone on `[1,√2]` | `y + sqrt(2−y²)` has derivative `1 − y/sqrt(2−y²) ≤ 0` |
| `chord_B_endpoint_min` | `min` of `B(y) = 2(a y − V)/(y²−1)` over `[y₀,y₁] ⊆ (1,√2]` is at an endpoint | `q(y) = −a y² + 2V y − a` has root product `1`, so `B` is antitone, or monotone-then-antitone |
| `y_range_of_tilt` | the range of `cos θ + sin θ` over `[θ₀,θ₁] ⊆ [0,π/2]` is `[min endpoints, √2]` if `π/4 ∈ [θ₀,θ₁]`, else `[min, max]` of the endpoints | unimodality of `√2 cos(θ − π/4)` |
| `interval_disjoint_sum_le` | intervals with pairwise disjoint interiors inside one of length `s` sum to `≤ s` | `MeasureTheory.measure_iUnion₀` with a.e.-disjointness (interiors disjoint ⇒ pairwise a.e. disjoint, since a nondegenerate interval's boundary is null) |
| `chord_interior_disjoint` | interiors of `Q i` disjoint ⇒ interiors of the chords disjoint | a point of `l` interior to two chords is interior to both squares |

**Roster expected:** 2 theorems, 1 `Bool` checker, 7 supporting lemmas, **0 new axioms** — the whole
clause is `Real`/`Rat` algebra plus one-dimensional Lebesgue additivity, all in Mathlib. It does not
touch `core_meet_same_square` or the T5 leaf, and it does not need A133's monotone `cos`/`sin`
bounds (the checker works with `t = tan(θ/2)` rationals throughout, and the only transcendental step
is `chordLen_eq`, proved once). Contrast with A135's polygon clause, which needed the vertex-in-all-
poses lemma over `t`: here the box quantifier is discharged by `chordLen_antitone_offset` +
`chord_B_endpoint_min` rather than by a corner enumeration.

---

## 6. The n-general form

Nothing above mentions `n = 11`, `s0`, or the `k5` slot structure. For any `n`, any container side
`s`, and any class with `k` simple (pinned, near-axis-aligned) squares, the family is: the lines
through every simple square's core edges and midlines, through the conditioned box's polygon-core
extremes, and the container-parallel eighths. For a class whose pins sit on a lattice, a horizontal
line placed inside a row of pin cores collects `chord = 1` from every pin in that row for free,
which is why the family is cheap: `<= 40` lines, each an `O(#placements)` row.

The row family subsumes A121's `st4` reading and generalises it: a stack of `ceil(sqrt n)`
axis-aligned unit squares flush against one wall gives `ceil(sqrt n)` chords of length `>= 1` on the
line through that wall's strip, hence `s >= ceil(sqrt n)` — for `n = 11`, `s >= 4 > 3.877084`. Where
A121 had to recognise the configuration and turn it into a case kill, the guard row states it as a
linear inequality over placements, so the LP finds it by itself and, crucially, **fires when only
SOME of the four squares are pinned**: on `k5_11_interior_Y0147` two of the four chords are the
LP's own free columns, one is a pin and one is the conditioned square, which is precisely the case
`st4` could not express. The same row family is what would kill the "stack of `ceil(sqrt n)`"
configurations at every `n`, and, as a counting row, it is the LENGTH-charging sibling of A94/A109's
SLOT-CROWD rows, which charge slot occupancy; the two are independent and compose additively in the
LP.
