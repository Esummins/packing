# What it costs to teach `verify_param.py` about NO-families

Every NO child of a region tree (and every NO child of A111's load-path branch) carries a
`caselp.NoFam`. `caselp.make_certificate` already writes them:

```
hypotheses.nofams = [ {x0, x1, y0, y1, t_intervals: [[t_lo, t_hi], …]} ]   # all rational strings
```

and the frozen **fixed-side** verifier `verify_case.py` consumes them. The frozen **parametric**
verifier `verify_param.py` (sha256 `0c58485c…`) refuses them outright:

```
verify_param.py:529   if p["hypotheses"].get("nofams"):
verify_param.py:530       raise ValueError("nofams unsupported")
```

So today every NO certificate is a fixed-side object and A57's window claim needs **one certificate
per side of the four-side slack-core grid** instead of one 4-D pass — a 4× multiplier on the NO
side's certification wall, and the single reason the branch cannot be emitted parametrically.

## The change, function by function

`verify_param` already carries the exact shape this needs, for cores: `CoreP` (an s-affine centre),
`core_exempt_frac_iv` (a Fraction interval predicate over the 4-D cell `[t0,t1]×[x0,x1]×[y0,y1]`
with the core centre widened over the s-cell), a float pre-filter, `SCell.cores_iv` (the per-s-cell
centre intervals) and one call site, `PVerifier.exempt`. A NO-family needs the same five pieces and
each is strictly simpler, because a zone test is a **containment of axis-aligned intervals**, not a
separating-axis computation.

| # | piece | mirrors | ~lines | note |
|---|---|---|---|---|
| 1 | `NoFamP` — zone `(ax0 + bx0·s, …)` + rational t-intervals | `CoreP` | 20 | for A112/A111 branch boxes `b* = 0` (the box comes from the node's own support at one side and the YES/NO split is s-independent), so the constant case suffices |
| 2 | `nofam_exempt_frac_iv(nf, zx, zy, t0, t1, x0, x1, y0, y1)` — the whole cell inside the zone **and** `[t0,t1]` inside one t-interval | `core_exempt_frac_iv` | 15 | pure Fraction comparisons; no `imul4`, no trig |
| 3 | `SCell.nofams_iv` — the zone over the s-cell taken at its **worst case** (the smallest zone, i.e. the intersection over `s ∈ [SA, SB]`), including `NoFam.s_hi = s − 0.5`'s upper clamp at `s = SA` | `SCell.cores_iv` | 8 | conservative direction: it exempts *less*, never more |
| 4 | `PVerifier.exempt` — a nofam loop before the core loop | — | 6 | exemption stays monotone under refinement, so no splitting logic changes |
| 5 | `load_param` — parse instead of raise | — | 12 | accept both the scalar (constant) and the `[a, b]` (s-affine) form |
| 6 | `selftest` — a new arm: *exempt-for-box ⇒ `NoFam.contains` at a random sample inside the box* | the (E) arm | 30 | same pattern as the existing core arm |

**≈ 90–120 lines, one new frozen verifier version (`verify_param` v2).** No new geometry enters the
TCB: the clause "a placement whose pose lies in a NO-family is exempt from the covering rows" is
*already* the clause the frozen `verify_case.py` discharges at a fixed side; the parametric version
is the same clause with `s` ranging over a slab and the zone taken at its worst case on that slab.
That is one Lean lemma parallel to the existing core-exemption lemma, not a new theory.

**Regression surface: none.** `verify_param` rejects every nofam certificate today, so no certificate
already emitted contains one; the change cannot alter any existing verdict. The positive control is
therefore the selftest arm plus re-verifying the A111/A112 NO certificates on a slab and checking the
fixed-side verdict at each grid side agrees.

**What it buys.** Four fixed-side certificates per NO child collapse to one window certificate: on
A57's four-side slack-core grid that is a **4× cut of the NO-side certification wall**, and it is the
only thing standing between the dual-guided branch and a *window* claim. Measured against A112's own
numbers, the NO side is where essentially all of the certified killing happens, so this multiplier
applies to essentially all of the branch's certification cost.

**What it does not buy.** The YES side. A YES child is an ordinary core box and `verify_param`
already handles it; the YES side's problem is not the verifier but that the node LP cannot see a
*side* statement at all (see `notes/verdict.md`).
