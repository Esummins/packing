# A87 chore: the deep-corner frontier D*(sigma)

`D = min_c d1(c)`; `d1(c)` / `d2(c)` = depth of the deepest / second deepest intruder at corner c; depth = `1 - f_min_max` in the corner frame (A89 `t2b_depth`, as in `depthdist87`).  K0-BLOCKED = every corner's open unit slot met by >= 2 squares (hence no simple square).  Code `code/deepfront87.py`; the search MAXIMISES D at a grid of side caps and every reported number is an exact-verified enclosure.

## Headline

**The PI conjecture is FALSE as stated for sigma around 4.**  A certified K0-BLOCKED packing exists with

```
    sigma <= 4.089300036      min_c d1 = 0.980000400      n_block = [2, 2, 2, 2]
```

i.e. ALL FOUR corners have their deepest intruder past 0.97, versus `min_c d1 <= 0.0998` over the whole existing A87 corpus -- a factor of ~10.  D* does not decline anywhere in the probed range: it is FLAT at 0.9783-0.9800 from sigma = 4.344 down to sigma = 4.0291, and it is pinned there not by sigma but by the search's own artificial second-intruder floor EPS_KEEP = 1e-4 (see the analytic ceiling below: every certified optimum has d2 = 1.000e-4 exactly and d1 <= 0.9800004 = 1 - 2 sqrt(1e-4)).

**But the search never got below sigma ~ 4.000**, so it says NOTHING about the regime the conjecture is about (sigma <= s_hat = 3.877083590022814).  See "What this does and does not settle".

## Frontier (exact-verified), objective min_c d1

| cap sigma | n ladder pts | best D (float) | certified D enclosure | certified sigma <= | min pair gap >= | n_block | depth iv width <= |
| ---: | ---: | ---: | :--- | ---: | ---: | :--- | ---: |
| 3.877084 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | -- |
| 3.900000 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | -- |
| 3.950000 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | -- |
| 4.000000 | 0 | -- | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | -- |
| 4.050000 | 75 | 0.979644 | [0.979643553, 0.979643553] | 4.029103117 | 4.96e-10 | [2, 2, 2, 2] | 1.2e-39 |
| 4.100000 | 27 | 0.980000 | [0.980000400, 0.980000400] | 4.089300036 | 3.58e-10 | [2, 2, 2, 2] | 2.2e-39 |
| 4.200000 | 26 | 0.979960 | [0.979960223, 0.979960223] | 4.173618380 | 5.00e-10 | [2, 2, 2, 2] | 1.9e-39 |
| 4.400000 | 7 | 0.978349 | [0.978348542, 0.978348542] | 4.344254221 | 4.97e-10 | [2, 2, 2, 2] | 1.5e-39 |

The `3.950 / 3.900 / 3.877` rows are EMPTY because no K0-BLOCKED packing at those sides could be produced at all -- not because D* is small there.  Both search arms stall at sigma ~ 4.000, exactly the barrier k0dir87's own 520-seed campaign hit (its record K0-BLOCKED side is 3.9855).  The corpus arm below does not break the barrier either: the one corpus packing that IS under 4.000 (s0115, sigma = 3.9855) could not be lifted off its 5.3e-9 second-intruder floor, so even it yields no usable start.

## Per-corner detail of the certified optimum

| cap | corner | n_block | d1 | tilt of d1 (deg) | d2 | sq(d1) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 4.050000 | BL | 2 | 0.979643553 | 0.000208 | 1.0000e-04 | 0 |
| 4.050000 | BR | 2 | 0.980000400 | 0.000000 | 1.0000e-04 | 2 |
| 4.050000 | TL | 2 | 0.980000400 | 0.000000 | 1.0000e-04 | 4 |
| 4.050000 | TR | 2 | 0.980000400 | 0.000000 | 1.0000e-04 | 6 |
| 4.100000 | BL | 2 | 0.980000401 | 0.000000 | 1.0000e-04 | 0 |
| 4.100000 | BR | 2 | 0.980000403 | 0.000000 | 1.0000e-04 | 2 |
| 4.100000 | TL | 2 | 0.980000400 | 0.000000 | 1.0000e-04 | 4 |
| 4.100000 | TR | 2 | 0.980000418 | 0.000000 | 1.0000e-04 | 6 |
| 4.200000 | BL | 2 | 0.979960223 | 0.000023 | 1.0000e-04 | 0 |
| 4.200000 | BR | 2 | 0.979960223 | 0.000023 | 1.0000e-04 | 2 |
| 4.200000 | TL | 2 | 0.979960223 | 0.000023 | 1.0000e-04 | 4 |
| 4.200000 | TR | 2 | 0.980000400 | 0.000000 | 1.0000e-04 | 6 |
| 4.400000 | BL | 2 | 0.978348542 | 0.000996 | 1.0000e-04 | 0 |
| 4.400000 | BR | 2 | 0.978348542 | 0.000996 | 1.0000e-04 | 2 |
| 4.400000 | TL | 2 | 0.978348542 | 0.000996 | 1.0000e-04 | 4 |
| 4.400000 | TR | 2 | 0.980000400 | 0.000000 | 1.0000e-04 | 6 |

Every deepest intruder is essentially AXIS-ALIGNED (tilt 1e-6 to 3e-3 degrees): the deep-corner motif is a slot square pushed off the corner by eps, not a tilted crowder.  This matches `depthdist87`'s observation that tilt does not buy depth (the two corpus corners with tilt > 15 deg have depth 0.0997 and 0.2267).

## Does D* drop below 0.3 / 0.5 / 0.7 as sigma decreases?

| cap sigma | certified sigma | certified D | >= 0.3 | >= 0.5 | >= 0.7 |
| ---: | ---: | ---: | :---: | :---: | :---: |
| 3.877084 | -- | *unprobed* | -- | -- | -- |
| 3.900000 | -- | *unprobed* | -- | -- | -- |
| 3.950000 | -- | *unprobed* | -- | -- | -- |
| 4.000000 | -- | *unprobed* | -- | -- | -- |
| 4.050000 | 4.029103 | 0.979643553 | YES | YES | YES |
| 4.100000 | 4.089300 | 0.980000400 | YES | YES | YES |
| 4.200000 | 4.173618 | 0.979960223 | YES | YES | YES |
| 4.400000 | 4.344254 | 0.978348542 | YES | YES | YES |

**No.**  Over every side the search actually reached, D* clears all three thresholds with room to spare, and there is no downward trend to extrapolate from: the curve is flat.

**EXTRAPOLATED (and NOT to be trusted).**  A naive continuation of a flat curve would put D*(s_hat) ~ 0.98 as well, i.e. the conjecture false. That extrapolation is worthless here, for a reason visible inside A87 itself: the probed range is entirely ABOVE the packing barrier.  As sigma falls to s(11) the set of 11-square packings collapses to a neighbourhood of the optimum, and the four deep-corner motifs (footprint ~1.02 x 2.0 each) provably stop fitting -- at sigma = 4.00 the four gadget footprints plus three more squares already do not fit (the seeder fails outright below 4.05 and only a compressed census packing reaches 4.01).  Against the flat extrapolation stands a SOUND bound in the opposite direction at exactly the side that matters: `depthdist87`'s A85 4-corner gate analysis (boxes from the sigma-CLOSED cover, i.e. the s_hat scale) finds that 0 of 30 attemptable stored 4-corner nodes can host `min_c d1 >= 0.7`, and 0 of 30 can host `min_c d2 >= 0.3`.  Since that is an UPPER bound per box, it EXCLUDES `min_c d1 >= 0.7` on those nodes.

So the honest picture is a CLIFF somewhere in `(s_hat, 4.01)` that this search does not resolve:

```
    sigma in [4.01, 4.40] :  D* ~ 0.98        (certified >= 0.9755 here)
    sigma  =  s_hat       :  D* < 0.7         (A85 box bound, sampled)
```

The load-bearing consequence for the drain-flow argument: **K0-BLOCKED alone does not force a shallow corner.**  Any proof of the PI statement must use the side bound sigma <= s_hat essentially, not merely as a background assumption -- at sigma = 4.01 the same combinatorics admit min_c d1 = 0.977.

## Second objective: min_c d2 (BOTH intruders deep)

| cap sigma | n | best min_c d2 (float) | certified enclosure | certified sigma <= | n_block |
| ---: | ---: | ---: | :--- | ---: | :--- |
| 4.000000 | 0 | -- | NOT VERIFIED / NOT REACHED | -- | -- |
| 4.200000 | 29 | 0.125016 | [0.125016384, 0.125016384] | 4.199999999 | [2, 2, 2, 2] |
| 4.400000 | 9 | 0.292893 | [0.292892810, 0.292892810] | 4.380961510 | [2, 2, 2, 2] |
| 4.600000 | 8 | 0.292893 | [0.292893155, 0.292893155] | 4.598975980 | [2, 2, 2, 2] |

Read against the one-corner ceiling `1 - 1/sqrt 2 = 0.29289321881345254` derived below.  Two things happen:

* At the two largest caps the search SATURATES that ceiling: certified `min_c d2 = 0.292893154942` at sigma <= 4.598976 (6.39e-8 under the ceiling) and `0.292892810151` at sigma <= 4.380962 (4.09e-7 under it), with the tilt of every deep intruder certified at 45.000000 degrees. That is the predicted motif, found independently by the optimiser, and it is a sharp check on both the code and the bound.  (Individual `d1` values sit a few 1e-7 ABOVE 1 - 1/sqrt 2 -- consistent, since the bound constrains `min(d1, d2)`, not `d1` alone.)
* Unlike the d1 frontier, the d2 frontier genuinely DECLINES: it falls from 0.2928932 at sigma <= 4.381 to **0.125016** at sigma <= 4.200, a factor of 2.3 over a side interval of 0.18.  The cause is packing, not corner geometry: the four-corner 45-degree 2-crowd gadget needs sigma >= 4.60 to admit three further squares at all (at 4.40 the eight corner squares fit but the three middles do not), so below ~4.4 the four motifs must start giving way to each other.  Cap 4.00 was never reached, by the same sigma ~ 4.000 barrier as the d1 run.

So for the SECOND intruder there IS a visible cliff inside the probed range, and it is already at 0.125 by sigma = 4.2 -- below the 0.3 threshold.  `depthdist87`'s A85 gate analysis says 0 of 30 attemptable 4-corner nodes can host `min_c d2 >= 0.3` at the s_hat scale, which is the same story continued downwards.

## Low-sigma arm: the depth ascent run IN PLACE on A87's own corpus

The five exact K0-BLOCKED packings of `depthdist87` are the only certified material below sigma = 4.000.  Their second intruders sit at or under the old EPS_KEEP floor (min_c d2 down to 8e-9), so each is first LIFTED to the standard 1e-4 floor by a d2 ascent, then the d1 ascent is run at its own side.

The outcome is NEGATIVE and worth recording as such: the ascent barely moves from a corpus point.  Two of the five cannot even be lifted to the 1e-4 floor (their second intruders are at 5.3e-9 and 4.6e-7 and the d2 ascent cannot raise them), and the three that can end at `min_c d1` = 0.0112, 0.00047 and 0.0574 -- essentially where they started.  This is the behaviour k0dir87 already documented for these points: they are BOUNDARY points of the constrained problem, and a local ascent is trapped.  So this arm gives NO evidence that D* is small at sigma ~ 4.000004 -- the census arm reaches D = 0.9796 at sigma <= 4.0291, only 0.029 higher.  It is a statement about the basin, not about the frontier.

| tag | corpus sigma | status | best cap | D (float) | certified D | certified sigma <= | n_block |
| --- | ---: | --- | ---: | ---: | :--- | ---: | :--- |
| s0115 | 3.985483725 | lift to the 1e-4 floor FAILED | -- | -- | -- | -- | -- |
| s0380 | 4.000000118 | lift to the 1e-4 floor FAILED | -- | -- | -- | -- | -- |
| s0076 | 4.000004058 | ok | 4.000004 | 0.011150 | [0.011150237, 0.011150237] | 4.000003893 | [2, 2, 2, 2] |
| s0380 | 4.000007451 | ok | 4.000007 | 0.000471 | [0.000470520, 0.000470520] | 4.000007458 | [2, 2, 2, 2] |
| s0259 | 4.000011860 | ok | 4.000012 | 0.057356 | [0.057355811, 0.057355811] | 4.000011865 | [2, 2, 2, 2] |

## Sensitivity: D* is pinned by the second-intruder floor, not by sigma

| EPS_KEEP | best D found | gadget prediction 1 - 2 sqrt(eps) |
| ---: | ---: | ---: |
| 1e-03 | 0.928835531 | 0.936754447 |
| 1e-04 | 0.974064060 | 0.980000000 |
| 1e-06 | 0.989827921 | 0.998000000 |
| 1e-08 | 0.996100367 | 0.999800000 |

D rises monotonically as the floor is lowered and tracks `1 - 2 sqrt(EPS_KEEP)` (it lags at 1e-6 / 1e-8 only because the ascent was given 55 rounds, not because anything else binds).  That is the signature of a configuration sitting ON the floor rather than against a geometric obstruction: with only the TOPOLOGICAL requirement `d2 > 0` -- any sliver counts as a blocker, which is what K0-BLOCKED actually asks -- D* -> 1 at these sides.  **The 0.98 in the frontier table is therefore an artefact of the search's own floor, and the honest reading of D*(sigma) for sigma in [4.03, 4.40] is "1, up to the sliver tolerance you insist on".**

## Analytic anchors

**The d1 gadget trade-off (why 0.98 and not 1).**  Take the deepest intruder to be an axis-aligned square whose inner edge sits at `x = eps`, so `f_min_max = eps` and `d1 = 1 - eps`.  The only part of the slot it leaves free is the strip `(0, eps) x (0, 1)`, and nothing can reach that strip from below (`y < 0` is outside the container).  So the second intruder must WRAP the reflex corner `(eps, 1)`: it is separated from the first by a line through `(eps, 1)` of slope `tan phi`, its inner edge runs along that line, and the container wall `x >= 0` forces its inner vertex to `x >= sin phi`.  Its depth is the drop of that line over `[sin phi, eps]`:

```
    d2  <=  max_phi (eps - sin phi) tan phi   ~   eps^2 / 4 ,
    equivalently   d1  <=  1 - 2 sqrt(d2)   (to 5 digits for d2 <= 1e-3).
```

A floor `d2 >= f` therefore caps `min_c d1` at `1 - 2 sqrt f`:

| d2 floor f | eps* | d1 ceiling | 1 - 2 sqrt f |
| ---: | ---: | ---: | ---: |
| 1e-03 | 0.06322974 | 0.93677026 | 0.93675445 |
| 1e-04 | 0.01999950 | 0.98000050 | 0.98000000 |
| 1e-06 | 0.00200000 | 0.99800000 | 0.99800000 |
| 1e-08 | 0.00020000 | 0.99980000 | 0.99980000 |

The certified optima above land on this line exactly: `d2 = 1.000e-4` at every corner and `d1` up to `0.9800004`.

**The one-corner d2 ceiling.**  If the two intruders of a corner are separated by a line through the corner point, each is confined to a sub-wedge of the corner quadrant.  In the wedge `{0 <= y <= x}` one has `max(x,y) = x`, so `f_min_max = c_x - e` with `e = (|cos|+|sin|)/2`, while the two wedge rows `min(x - y) >= 0` and `min y >= 0` read `c_x - c_y >= max(cos th, sin th)` and `c_y >= e`.  Adding them, `f_min_max >= max(cos th, sin th) >= 1/sqrt 2`, so

```
    min(d1, d2)  <=  1 - 1/sqrt(2)  =  0.29289321881345254 ,
```

attained at tilt 45 deg by the two 45-degree squares that share a whole edge on the corner diagonal and each touch one wall.  **Scope of this bound:** the derivation above is complete only when the separating line passes THROUGH the corner point.  For a line that misses it, the argument offered here is only that shifting the line off the corner enlarges one sub-wedge past 45 deg while shrinking the other below it, so the MINIMUM of the two depths falls -- checked for lines near the diagonal, not proved in general.  It is therefore a conjectured one-corner optimum, and the certified numbers above are consistent with it (they approach it from below, by 6.4e-8, and never cross it).  (Trump's genuine TL 2-crowd sits at tilt 40.18 deg with d1 = 0.1683, d2 = 0.1555 -- the motif, well short of the one-corner ceiling because the rest of the packing is in the way.)

## Canary

With the K0-BLOCKED constraint DROPPED and simple squares allowed, the optimum is four flush slot squares and D = 1.  The same `ascend` code, from the same gadget seeds, returns

```
    cap 4.05 :  D = 1.000000000 exactly,  per-corner d1 = [1, 1, 1, 1],
                n_block = [1, 1, 1, 1]  (four SIMPLE squares),  s = 4.03523
```

At sigma = 4.00 exactly D = 1 is only an INFIMUM, not attained: four corner slot squares plus seven more fill the 16-cell unit grid of `[0,4]^2` with zero slack, so a STRICTLY feasible D = 1 packing needs sigma > 4 -- the smallest side at which the search realises it is 4.0352.  The canary passes at cap 4.05.

## What this does and does not settle

* **Settled (certified).**  K0-BLOCKED does NOT by itself force a shallow corner.  At sigma <= 4.029103 there is a K0-BLOCKED packing with all four `d1 > 0.97`.  The PI statement, read as a claim about K0-BLOCKED packings at ANY side near 4, is false.
* **Settled (analytic).**  The deep-corner motif costs quadratically: `d1 = 1 - eps` forces `d2 <~ eps^2/4`.  So "both intruders deep" is a completely different question from "one intruder deep", and the one-corner ceiling for the former is `1 - 1/sqrt 2 = 0.2929`.
* **NOT settled.**  Everything at `sigma <= s_hat`, which is the only regime the conjecture is about.  No K0-BLOCKED packing below sigma ~ 4.000 was produced by this search (k0dir87 has the same barrier; its record is 3.9855).  The grid points 3.95, 3.90 and s_hat are EMPTY.
* **Cheapest next step.**  The gap to close is `(s_hat, 4.01)`, and the obstruction is a PACKING barrier, not a depth one: what is missing is a supply of K0-BLOCKED packings at sigma in [3.877, 4.00].  A85's sigma-closed cover already enumerates the corner pairs at that side, so the direct attack is to run this depth ascent inside the A85 4-corner nodes rather than from free-space seeds.

## Provenance

* d1 campaign: 98 seeds run, 0 seed failures, 2211 s search + certification, RNG seed 20260903; caps [4.4, 4.2, 4.1, 4.05, 4.0, 3.95, 3.9, 3.877083590022814].
* ladder points reached per cap: {'4.400000': 7, '4.200000': 26, '4.100000': 27, '4.050000': 75, '4.000000': 0, '3.950000': 0, '3.900000': 0, '3.877084': 0}
* d2 campaign: 31 seeds run, caps [4.6, 4.4, 4.2, 4.0].
* Every certified row: rational z (denominators <= 1e15), interval SAT gaps certified > 0, blocker counts certified against the INNER rational slot rectangle (`k0dir87.exact_blocked_test`), depths as outward-rounded interval enclosures (`depthdist87.corner_depths`), side an outward interval UPPER bound (`fjpolish87.verify_exact`).
* Files: `results/deepfront87.{json,jsonl}`, `.d2.json`, `.corpus.json`, `.floors.json`, `.pilot.json`; log `logs/deepfront87.run.log`.
* Selftest: depth_table vs the exact interval depth of `depthdist87` on Trump, 44 rows, max |diff| 3.3e-16; analytic vs finite-difference gradients, max rel err 3.2e-9; the smooth objective verified to be an UPPER bound on `f_min_max` (0 violations); the 8-candidate set verified complete against a 401-point-per-edge brute-force boundary scan.


## Coordinator note (2026-09-03, after PI review)

The "PI conjecture is false as stated" verdict above is a statement about PACKINGS, not about the
proof residue. The maximisers found are the near-slot gadget (square parked eps off its slot, partner
dipping a vertex into the sliver). That gadget is not a Psi-minimal sigma-minimiser: the partner can
rotate back to flush and lift out of the slot at constant side (A89 near-slot canary), and at
sigma ~ 4.03 the near-slot square has slack to retreat, so NOCRIT-SEL's anchoring fails and the
selection discards it. The measurement asked the wrong set: the objective omitted the selection /
anchoring condition. Four eps-off corner squares are the ghost of corners4 (still open), covered by
Lemma PD's pin slack once the class is killed and drained into k >= 1 along flats (A87 plateau ends).
The conjecture in the residue-relevant form is: at a Psi-minimal K0-BLOCKED minimiser at side <= s-hat,
some corner has its SECOND intruder shallower than delta. Re-measured with the anchoring/retreat filter
in d2front87.
