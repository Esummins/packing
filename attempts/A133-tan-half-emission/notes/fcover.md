# A133 T3 — the F-COVER fix, specified

**Write only.**  Nothing under `attempts/A112-*`, `attempts/A120-*` or `lean/` is edited by this
attempt on account of this note; the re-emission of A120's NO certificates is queued with the
A120 resume, and this is the specification it should follow.

## Where the rounding is

A120's runner does not round the zone itself.  `a120lib.nofam_of` builds the NO family EXACTLY
(the mapped box's own centre rectangle clamped to `[1/2, s − 1/2]`, and
`octagon.theta_intervals(F.th0, F.th1)` for the tilt) and `noside120.py` records it at full
precision in `results/nodes/<child>.json` (`hyp.nofams`, tilt in degrees).  The rounding happens
one level down, when `a120lib.certify_leaf_capped` shells out to A112's `certify.py`, which calls
**`attempts/A112-dual-branching/code/caselp.py`, `make_certificate`, the `nofams=` clause (lines
404–406)**:

```python
TDEN = 1 << 24                                   # the t = tan(theta/2) grid
XDEN = 10 ** 9                                   # the centre grid
def t_lo(th): return Fr(math.floor(t_of_deg(th) * TDEN) - 1, TDEN) if th > 0 else Fr(0)
def t_hi(th): return Fr(math.ceil (t_of_deg(th) * TDEN) + 1, TDEN) if th < 90 else Fr(1)
def q(x):     return Fr(round(x * XDEN), XDEN)
...
nofams=[dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)), y1=str(q(f.y1)),
             t_intervals=[[str(t_lo(a)), str(t_hi(b))] for a, b in f.thetas]) for f in hyp.nofams]
```

So the NO zone's tilt interval is written `[t_lo(a), t_hi(b)]` — the low end rounded DOWN and the
high end rounded UP, each by a floor/ceil plus one extra unit of `2⁻²⁴ = 5.96·10⁻⁸`, hence up to
`1.19·10⁻⁷` OUTSIDE the recorded interval at each end — and the four centre bounds are written
with `q`, NEAREST at `10⁻⁹`, so an upper bound can also land up to `5·10⁻¹⁰` outside.  Those are
exactly A126's measured numbers (`9.0·10⁻⁸ … 1.10·10⁻⁷` in tilt on every one of the 22 PASSing
certificates, `≤ 4.71·10⁻¹⁰` on 16 of the 22 upper centre bounds, `zonecheck126.py`).

Outward is the RIGHT direction for the verifier — a wider NO zone exempts more boxes and the
hypothesis it is proved under is correspondingly stronger — and the WRONG direction for the
cover, which needs `ZONE ⊆ BOX` as pose sets for `H = YES ∪ ⋃ᵢ NOᵢ` to be a tautology.

## The change

One clause, in the same `nofams=` expression, using the rounding helpers that already exist in
that file (`q_up` is there; `q_dn` is its mirror and is the only new three-line definition):

```python
def t_in_lo(th): return Fr(math.ceil (t_of_deg(th) * TDEN) + 1, TDEN) if th > 0 else Fr(0)
def t_in_hi(th): return Fr(math.floor(t_of_deg(th) * TDEN) - 1, TDEN) if th < 90 else Fr(1)
def q_dn(x):     return Fr(math.floor(x * XDEN) - 1, XDEN)

nofams=[dict(x0=str(q_up(f.x0)), x1=str(q_dn(f.x1)),
             y0=str(q_up(f.y0)), y1=str(q_dn(f.y1)),
             t_intervals=[[str(t_in_lo(a)), str(t_in_hi(b))] for a, b in f.thetas]) for f in hyp.nofams]
```

i.e. **the NO zone rounds INWARD on every bound** (lower bounds up, upper bounds down, each tilt
interval narrowed at both ends), which makes `ZONE ⊆ BOX` true BY CONSTRUCTION.  The YES box —
the `boxes=` clause of the same call, which carries A119's cores — keeps its OUTWARD rounding;
widening it is not an option, because it is `N`'s own box and `N` is what it is.  A tilt interval
that would become empty under the narrowing (width below `2·2⁻²⁴`) must be DROPPED, not emitted
reversed; dropping it only weakens the NO hypothesis further, and it cannot happen at the
resolutions A120 uses — measured over all 56 `t_intervals` of its NO certificates, the narrowest
is `8.75·10⁻²` and the widest `2.11·10⁻¹`, six orders of magnitude above the `2⁻²⁴` grid.

## What it costs

The NO hypothesis becomes strictly WEAKER (a smaller zone exempts fewer boxes), so all 22 PASSing
certificates have to be re-run.  The amounts are `≤ 1.19·10⁻⁷` in `t` and `≤ 1.5·10⁻⁹` in the
centre bounds — three to four orders of magnitude below the resolution at which those
certificates pass (A120's certificates are at depth 56 with `scale_cap 1.4`; A126's replay of the
four `Y0230` children shows the covering margins are set by the LP weights, not by the zone's
last digit).  So the expected outcome is a formality: the same 22 PASSes, at the same depths, for
the same wall (A126's table: 156 s / 324 s / 688 s / 872 s of `native_decide` for `Y0230`'s four,
and 14 – 54 s each for the frozen Python verifier).  It should be run as a re-certification pass
over A120's node records with the `.json.done` cache invalidated, and any child that turns FAIL
or CAP is a genuine result, not a rounding artefact.

## The Lean check that would have caught it, and where to run it

`LocalCompose.yes_or_no` is the tautology:

```lean
theorem yes_or_no (Ls : List Box) (z : Cfg) :
    (∀ i : Fin Ls.length, SomeIn (Ls.get i) z) ∨ ∃ i : Fin Ls.length, NoneIn (Ls.get i) z
```

and `node_dead_of_yes_no` consumes its NO side as `NoneIn (Ls.get i) z` — the box `Ls.get i`
itself.  What A120's certificate proves is `CaseExempt` for the ZONE.  The bridge is the
hypothesis "`NoneIn (Ls.get i) z → the zone is empty of squares`", which holds iff
`ZONE i ⊆ Ls.get i` as pose sets.  That containment is a FINITE RATIONAL TEST on the two
records — four centre-bound comparisons and, per tilt interval of the zone, one containment in
the box's own `t`-interval:

```
zone.x0 ≥ box.x0 ∧ zone.x1 ≤ box.x1 ∧ zone.y0 ≥ box.y0 ∧ zone.y1 ≤ box.y1 ∧
  ∀ (a, b) ∈ zone.tivs, box.t0 ≤ a ∧ b ≤ box.t1
```

decidable on `ℚ`, hence a `decide` in Lean and a two-line assertion in the emitter.  **Run it at
emission**, in `make_certificate`, against the box the same call is writing into `boxes=`: that is
the cheapest place, it fails loudly on the wrong rounding direction, and it is the same predicate
the Lean side will discharge (`ZoneSubBox` in the eventual `LocalCompose` extension, one
`decide` per NO child).  A120's own `A6_nofam_is_the_same_box` check compares the zone to the box
BEFORE the rounding, which is why it passed on all nine nodes while the emitted certificates did
not satisfy the containment — the guard has to be on the WRITTEN rationals, not on the floats
they came from.
