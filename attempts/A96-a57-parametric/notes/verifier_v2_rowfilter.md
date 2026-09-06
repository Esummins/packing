# Spec: verifier v2 — the all-poses row filter (dominated placements)

Status: **SPEC ONLY.** Nothing is deployed and the frozen chain is untouched. This exists so a
verifier-v2 chore can implement it against the frozen verifiers and publish a **new sha**; the
current `verify_case.py` / `verify_param.py` and their Lean soundness theorems keep theirs.

Written by A96, 2026-09-06. Companion levers T5′ (tight core) and T5″ (tilt trimming) need **no**
clause change — this one does, which is exactly why it is separated from them.

## 1. What changes, in one line

The certificate currently claims `μ(Q) ≥ 1` for **every** admissible unit square `Q` in `[0,s]²`
disjoint from all cores. Under the filter it claims it only for those `Q` that are **disjoint
from at least one pose of the conditioned box**. The verifier must check the weaker statement, so
the checker changes and the sha changes.

## 2. The exemption, exactly

Let the node's conditioned box be `B = [x0,x1] × [y0,y1] × [θ0,θ1]` (a YES child's own box, i.e.
the last entry of `hypotheses.cores` in its emitted form, carried with its tilt range). Define

> **(D) dominated.** A unit square `Q_r` at `(p, φ)` is *dominated by B* iff for every
> `(c, θ) ∈ B`, `Q_r ∩ Q(c, θ) ≠ ∅`.

New exemption clause, added alongside the existing core-exempt and NO-family clauses:

> A `(t, cx, cy)`-box is EXEMPT if it is **provably dominated by B** — every square it
> parametrises overlaps every pose of `B`.

Soundness of the exemption is the same argument as T5, one level out: the node hypothesis says
*some* packing square has `(centre, tilt) ∈ B`. A square dominated by `B` overlaps that square
whatever pose it takes, and is not it (distinct squares of a packing are interior-disjoint), so
no packing satisfying the hypothesis contains a square at `(p, φ)`. Such placements therefore
carry no mass obligation.

**Note the direction.** The existing core exemption removes squares that meet a core; this
removes squares that meet *every pose*. Both shrink the set that must be covered, so both make
the LP easier — and both must be mirrored in the checker or the certificate proves less than the
consumer assumes.

## 3. The decision procedure (exact, interval)

Two unit squares are disjoint iff one of four axes separates them (separating-axis theorem for
convex polygons; the candidate axes are the two squares' edge normals). So `Q_r` is dominated by
`B` iff **no** axis separates it from **any** pose, i.e. for each axis family the separation gap
stays negative over the whole box. With `h(ψ, α) = (|cos(ψ−α)| + |sin(ψ−α)|)/2` the support
half-width of a unit square at tilt `ψ` in direction `α`, the four conditions are

```
alpha = phi      :  max over c in box of |(c - p) . n_alpha|  <  1/2 + min over theta of h(theta, alpha)
alpha = phi + 90 :  same
alpha = theta    :  max over (c, theta) of |(c - p) . n_theta| <  1/2 + min over theta of h(phi, theta)
alpha = theta+90 :  same with the +90 offset
```

* the two **fixed** axes: the left side is a maximum over the four box corners (linear in `c`);
* the two **moving** axes: `(c−p)·n_θ = r·cos(θ − ψ_c)`, so the maximum over a `θ`-interval is
  `r` when a critical angle falls inside and the larger endpoint otherwise — the same
  max-projection bound `trim57._max_proj` already uses;
* `min over theta of h(·)` has its extrema at multiples of 90° from the axis, so the minimum is
  an endpoint unless such a multiple is interior.

Accept **only** when all four strict inequalities hold. A deployed version must evaluate these in
exact rationals with **outward** rounding — left sides rounded **up**, right sides **down** — as
`verify_case.core_exempt_frac` already does for the core exemption; float is a shortlist filter
only. Reference implementation (float, `MARGIN = 1e-9`): `A96 code/arms96.py::dominates`.

**Pre-screen.** Lemma TC is exact — for two unit squares at tilt difference `D`, the minimum
centre distance over disjoint placements is `(1 + cos D + sin D)/2`, attained on the first
square's own axis (verified to 2.2e-16). If the centre distance already permits the tilt
difference the square cannot be dominated, so the exact test is skipped. Cheap and O(1); on the
measured corpus it screens out ~45% of rows before any interval work.

## 4. Lean statement (parallel to T5)

T5 is `core_meet_same_square` in `Zones.lean`. The parallel statement:

```
theorem dominated_inadmissible
    {S : PinSet} {B : ParamBox} {p : RP} {phi : ℝ}
    (hdom : ∀ c θ, InBox B c θ → Overlaps (unitSquare p phi) (unitSquare c θ))
    (m : ℝ) (z : Cfg) (hz : CfgPacking m z) (hB : ∃ i, InBox B (z i).centre (z i).tilt) :
    ∀ j, (z j).centre ≠ p ∨ (z j).tilt ≠ phi
```

i.e. under the node hypothesis no packing square sits at `(p, φ)`. The checker-side obligation is
that `checkDominated B p phi = true → hdom`, decidable by the four interval inequalities above —
structurally the same shape as the existing `core_exempt` decision procedure, so it should reuse
its rational trig (`cosT`/`sinT`) and interval helpers rather than introduce new ones.

The consumer change is in the bridge: the measure statement's universally quantified `Q` gains
the side condition `¬ dominated B Q`, and `dominated_inadmissible` discharges it.

## 5. What a verifier-v2 chore must do

1. add `checkDominated` (exact, outward-rounded) to a **copy** of the frozen verifier, publish a
   new sha, and leave the current files and their Lean theorems untouched;
2. carry the conditioned box's **tilt range** in the certificate — today's emitted core keeps
   only the tilt midpoint `tm`, which is not enough to evaluate (D);
3. add the exemption to the box-discharge loop next to the core exemption;
4. re-run the frozen corpus under v2: every certificate that passes v1 must still pass v2 (the
   new clause only *adds* exemptions, so this is a regression check, not a proof);
5. only then may an emitter drop dominated rows.

## 6. Measured value, and the caveat

The row filter removes a large fraction of the LP: a **median 43.8%** of warm rows by the TC
screen alone, **48.2%** on the first node under the exact test. That is the case for doing the
work. But the three-arm test (`arms96.py`, arms A/B/C at a 900 s cap) is what decides whether
smaller LPs actually *kill* — at the 240 s cap only 2 of 29 trimmed re-solves converged, so a
smaller LP that still does not converge buys nothing. **Do not start the verifier-v2 chore until
arm C shows kills that arm B does not.**
