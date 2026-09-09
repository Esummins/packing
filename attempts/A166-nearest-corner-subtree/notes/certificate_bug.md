# A166 — a certificate-emission bug in shared machinery: `make_certificate` silently reverts A135 exact cores to stock cores

**Status: diagnosed, reproduced, fixed in A166's own emission path, and shown to convert 5 of 5 of
A150's previously-FAILing certificates into frozen-verifier PASSes. Nothing frozen was edited.**

## 1. The mechanism

Every attempt that runs an LP node with A135's certified **exact** axis cores uses the `ExactHyp`
pattern (A150 `lp150.py`, A158b `yeslp158.py`, A166 `lp166.py`, and the exact-core re-solves of A140):
build `caselp.Hyp`, then REPLACE `self.cores` with `exactcore.exact_a`'s larger cores. The LP's row
filter is `Hyp.ok_many`, which uses `self.cores`, so **the LP drops every placement that penetrates an
EXACT core** by more than `EPS_CORE = 2e-3`.

But `caselp.make_certificate` (A57 `caselp.py` line 384) does

```python
hyp = Hyp.from_json(res["hyp"])
```

and `Hyp.from_json` is

```python
return Hyp([Box.from_json(b) for b in d["boxes"]], [NoFam.from_json(f) for f in d["nofams"]])
```

whose `__init__` sets `self.cores = [b.core() for b in self.boxes]` — the **STOCK** cores. The `cores`
field that `Hyp.to_json` wrote is never read back. So the emitted certificate exempts a strictly
SMALLER core than the LP was allowed to ignore, and **every placement in the annulus between the exact
and the stock core is a guaranteed hole**.

Measured on A166's node `l2_p65_101_b8_005_512` (budget 8, `τ = 7.000000`, converged):

| core | exact `a` | stock `a` | ratio |
|---|---|---|---|
| 0 (`H`) | 0.441822650 | 0.412227593 | **1.0718** |
| 1 (TR cell) | 0.331609275 | 0.287776787 | **1.1523** |
| 2 (TR cell) | 0.335191811 | 0.328607999 | 1.0200 |

and all **32** of the frozen verifier's holes are the single axis-aligned placement
`(3.35109, 1.49000, 0°)`, whose SAT depth is

* **+0.029594 against the EXACT core of box 0** — so the LP dropped it, correctly;
* **−0.000001 against the STOCK core of box 0** — so the certificate cannot exempt it.

`exact_mass = 0` on every hole, not "just under 1": this is not a robustness-margin failure, and that is
why the A13/A14 separation loop cannot move it — the row it is asked to add is precisely a row the LP is
entitled to drop. Ladder confirming it is neither the scale nor the rational rounding
(`results/cert166_l2_p65_101_b8_005_512.json`): the same 32 holes at scales 1.005, 1.02, 1.05, 1.10,
1.14 and at denominators `1e6`, `1e9`, `1e12`.

**How big is the annulus, in general?** Over all 216 boxes of the corner cover (pulled to global
coordinates at `TR`, pad `w_max`; `results/coreratio166.json`) the ratio `a_exact / a_stock` runs

    min 1.01442   Q1 1.02395   median 1.04190   Q3 1.06443   max 1.15231

so the gap is 1.4 % to 15 % of the core's half-side on **every** box — the bug is structural, not
marginal, and any exact-core certificate whose LP happened to drop a placement in that annulus fails.

## 2. The fix, and why it is sound

Carry the exact cores in the certificate. A135's `exact_a` **certifies** `K(B) ⊆ Q(p)` for every pose
`p ∈ B` by an exact rational vertex test, and a square of the packing distinct from the conditioned one
is interior-disjoint from the conditioned square, hence from its core; so exempting placements that
overlap the EXACT core is legitimate, and the frozen `verify_case.py` validates whatever cores the
certificate carries. Note the direction of the old bug: the emitted certificate made a **stronger**
claim than the LP proved, so an old PASS remains sound — the bug generates spurious FAILs, never
spurious PASSes.

`code/certfix166.py` post-processes the certificate (A166's own file; `caselp.py` is untouched).
Result on A166's kill, over the whole scale x denominator ladder
(`results/certfix166_l2_p65_101_b8_005_512.json`):

> **PASS on the FROZEN `verify_case.py` (sha `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`)
> at every scale 1.005 … 1.14 and every denominator `1e6` / `1e9` / `1e12`** — 15 of 15 certificates.
> (The three scale-1.20 certificates fail correctly: `total = 8.400000 ≥ budget 8`.)

So `l2_p65_101_b8_005_512` is a **CERTIFIED kill** at budget 8, total `7.035000 < 8` at scale 1.005:
*no 11-square packing has a square in `l2_p65_101`'s conditioned box together with two distinct squares
in those two `TR` cover cells.*

## 3. It is not A166's bug — it is the lab's

`code/certaudit166.py` reads A150's FAILed certificates, recomputes the exact core from the box each
certificate itself carries, writes the patched copy under A166 and runs the frozen verifier
(`results/certaudit166.json`). A150 is never written to, and the `l1_104_spread_*` certificates in the
same directory — written today by the LIVE A165 cascade — are excluded by prefix.

| A150 node | was | now | core ratios (exact / carried) |
|---|---|---|---|
| `q_402_x4` | FAIL | **PASS** | 1.0419 ×4 |
| `q_402_x4_recert` | FAIL | **PASS** | 1.0419 ×4 |
| `q_rand_301_000_321_533` | FAIL | **PASS** | 1.0154, 1.0644, 1.0282, 1.0333 |
| `q_rand_301_000_321_533_recert` | FAIL | **PASS** | same |
| `r_055_035_044_453` | FAIL | **PASS** | 1.1013, 1.1523, 1.0575, 1.0333 |

**5 of 5.** So A150's headline changes: its four-corner root has **7 converged kills and 7 certified**
(three distinct nodes recovered — `q_402_x4`, `q_rand_301_000_321_533`, `r_055_035_044_453`), not "4
PASS, 2–3 LP-dead certificate pending", and its §5 sentence "they need the A13/A14 separation loop with
more rounds and a longer `cert_time`" is wrong: they needed the cores they were solved with.

## 4. What should be re-checked

Any record whose verdict is *"LP-dead, certificate pending"* or *"kill-candidate (cert FAIL)"* on a node
solved with A135 exact cores. From `cells140.open_pool`, **127 of the 166 open k0_00 records carry the
verdict `kill-candidate (cert FAIL)`** — if any of those were emitted through an exact-core path, they
are candidates for immediate certification at zero LP cost. The same question applies to A140's
exact-core re-solves, A149's A57/A60 re-prices, A158's `no158` certificates and A165's live cascade.
The repair is one line in the emission path (carry `hyp.cores` instead of rebuilding them), or A166's
post-processing step; `caselp.py` itself is read-only for this attempt, so the fix is not applied there.

A cheap, safe audit exists and is already written: `code/certaudit166.py --dir <certs dir>` re-verifies
any directory's FAILing certificates with the exact cores substituted, writing only under A166.
