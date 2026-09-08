# A152 T1 — the A118-O1 prerequisite, measured on the certificate objects

**Question.**  Are the twelve k6 extension classes — `k5_11`: k6_18 / k6_20 / k6_23; `k5_16`:
k6_23 / k6_27 / k6_28 / k6_29 / k6_30; `trump5`: k6_07 / k6_19 / k6_21 / k6_22 / k6_23 / k6_24 —
certified dead on the closed window `[191/50, 969271/250000]` **with the sixth pin allowed the
`δ = 10⁻²` slack tolerance**, or only with exact pins?

**Answer: only with EXACT pins.**  Not one of the certificates carries a pin box.

## The measurement

The window claim of each class is carried by a `parametric-kill-certificate-v1` (A56, A61's
`*.gp.param.json`, or A114's re-verification of the same A56 object).  Every one of them has
`hypotheses.cores` = six entries of the shape

```
{"akx": …, "bkx": …, "aky": …, "bky": …, "s0_kx": …, "s0_ky": …,
 "a":  "16383999967232/32768001953125",
 "tm": "1/33554432"}
```

read directly off the twelve files (`certs/resolved/k6_18|19|22|24|28|30.param.json`,
`certs/k6_07|23|27.param.json`, `A61/certs/k6_20|21|29.gp.param.json`).  Uniform, with no
`delta_pin`, `slack`, `pin_delta` or `hw` field anywhere:

| quantity | value | meaning |
|---|---|---|
| core half-side `a` | `16383999967232/32768001953125` | |
| implied pin POSITION tolerance `½ − a` | **3.0802e-8** | the pin centre is fixed to 3e-8 |
| core tilt margin `tm` | `1/33554432` | |
| implied pin TILT tolerance | **3.41e-6 deg** | |
| core centre | `akx + bkx·s`, `aky + bky·s` | a POINT (affine in `s`), not a box |
| `n` / `budget` / `#cores` | 11 / 5 / 6 | `budget = 11 − #cores` |

For comparison, the `δ = 10⁻²` slack family needs core half-side `½ − h = 0.4929289…`
(`h = δ/√2 = 7.0711e-3`) — **229 000 times** the tolerance the certificates actually carry.
A96 recorded exactly this in `attempts/A96-a57-parametric/code/pocket96.py` (`k6_emitted_tolerance`):
*"the k6 window kills were emitted with DEGENERATE pin boxes; the working tolerances below
(0.01/1deg, 0.02/2deg) are A57's and A60's slack-core deltas, i.e. what a re-emission would give"*,
uniform over all 220 k6 cores.

So **A118-O1 stands unrelieved**, and the answer to "do the parametric certificates carry pin
boxes?" is **no**: the pin enters only as a fixed exempt core whose position is an affine function
of `s`.

## What the slack form would need

Two different re-certifications, because the two campaigns pin differently:

| lane | node family | what `T = S ∪ {p}` must survive | which cores shrink |
|---|---|---|---|
| **A60 / trump5** (`deepen.py` pins are `Box(x,x,y,y,0,0)`, EXACT) | 5 exact pins | 5 exact pins + the **sixth** within `h` | **1 of 6** |
| **A57 / A57box** (`tree57.build_children --pin_delta 1e-2`) | 5 pins in `σ + [−h,h]²` | **all six** within `h` | **6 of 6** |

Concretely the re-emission is: rebuild each certificate's core list with
`a := ½ − h = 0.4929289…` (and, for the s-affine positions, hull the centre over the pin box —
i.e. exactly `tree57`'s slack-core construction, which is why A57's own trees already run this
way), re-solve the node LP at `s0`, then re-verify parametrically over the closed window with
`verify_param.py` + C2.  Nothing else in the pipeline changes; `budget = 11 − 6 = 5` is untouched,
and T23's gate is already clean at this `δ` (min slot separation 1.000000, `2h = 1.414e-2 < 1`,
`2a = 0.986 < 1`, no centre in two pin boxes).

**The LP is not obviously feasible.**  Shrinking six cores by `h` per side enlarges the set of
squares that must be given `μ ≥ 1` (a square may now graze a pin and still be "core-free"), and
the surviving margin is thin: the recorded `τ` against `budget = 5` is

| class | τ (A56/A61 resolve) | slack `5 − τ` | LP wall |
|---|---|---|---|
| k6_18 | 4.0000 | 1.000 | 54 s |
| k6_19 | 4.0000 | 1.000 | 45 s |
| k6_22 | 4.5000 | 0.500 | 421 s |
| k6_24 | 4.5000 | 0.500 | 422 s |
| k6_28 | 4.5000 | 0.500 | 50 s |
| k6_30 | 4.5000 | 0.500 | 254 s |
| k6_21 | 4.6000 | 0.400 | 744 s |
| k6_20 | 4.6667 | 0.333 | 434 s |
| k6_27 | 4.6710 | 0.329 | 819 s |
| k6_29 | **4.7181** | **0.282** | 754 s |
| k6_07, k6_23 | (TRANSFERRED, no resolve row) | — | — |

(`attempts/A56-sparametric/results/resolve_k6_*.json`; k6_20/21/27/29 are the A61 stragglers and
are the ones already at the edge — three of them are `converged: false` with `minmass` 0.72–0.93.)

**Price.**  Per class: one LP re-solve (45–820 s, median ≈ 420 s; expect *more* with shrunken
cores, since column generation is what makes the tight ones expensive) plus one parametric window
verification.  The verification is the dominant and the volatile term — A114's window closes cost
`k6_23` 182 s, `k6_27` 1 826 s and `k6_07` **8 295 s** on the same machine.  Taking those three as
the low/median/high of the distribution:

| lane | classes | LP | window verify | total |
|---|---|---|---|---|
| A60 only (one core shrunk) | k6_07, 19, 21, 22, 23, 24 | ≈ 0.7 CPU-h | 0.3 – 14 CPU-h | **1 – 15 CPU-h** |
| A57 too (six cores shrunk) | + k6_18, 20, 27, 28, 29, 30 | ≈ 1.4 CPU-h | 0.6 – 28 CPU-h | **2 – 30 CPU-h** |

with a real risk that **k6_20/21/27/29 do not re-solve at all** at `δ = 10⁻²` — in which case the
slack window would have to be bought at a smaller `δ`, and A57's tree would have to be re-emitted
at that smaller `δ` too (the tree's slab width is `δ/(5/2)`, T23, so a smaller `δ` costs more grid
sides).  Note also the standing rule (`lemmas.md`, A112/A117): *a re-emission is not a
reproduction* — a FAIL here would not impugn the existing exact-pin kills, and a PASS would be a
new certificate to verify and bank, not a patch to an old one.

## Verdict

The prerequisite A118-O1 names is **UNMET**.  Every A152 certificate is therefore emitted with
`conditional: true` and a `prerequisite` field naming the missing slack-form kill, and every
fold-in line is marked *conditional on the slack-form extension kill*.

Given `notes/soundness.md` §4 — the sound form of the refinement is structurally vacuous at a
completable slot, and the sweep confirms it buys zero kills — **this re-certification should not
be bought for the sake of the slot-lane refinement.**  (It would still be worth something on its
own account: it is exactly what A118 §2 says is needed before ANY lane kill can be re-used for
T23's broader slack statement, and it would also make A141's existing 244 kills slack-valid.  That
is a different, and much better, reason to pay for it.)
