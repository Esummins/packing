# T2/T3 — 18 re-solves, 9 certified kills, and the predictor question

A145, 2026-09-07. Driver `code/resolve145.py`, ledger `results/resolves145.jsonl`, certificates
`certs/`, table `code/table145.py` → `logs/table145.log`. 6,376 s = **1.77 CPU-h** of recorded job
wall; whole attempt ≈ 1.87 CPU-h against the 2 CPU-h cap. Two BLAS-pinned BelowNormal processes,
never more; no shard launched; nothing written outside `attempts/A145-impossible-weight/` except
the four fold-in lines (`REGISTRY.md`, `LOG.md`, A57's `PAUSED.md` resume block).

## The headline — `k5_11_interior_Y0241`, the PI's node

The PI read the pockets below and bottom-right of `H` off the gallery page and said nothing fits
there. The measurement says 4 of the node's 5 dual-support columns overlap `H` at every pose of its
box (grid gaps 0.0153 / 0.0231 / 0.0351 / 0.0530) and 3 of those 4 meet `K'(B)` exactly, i.e.
**60 % of the node's LP objective sits on placements the hypothesis forbids.**

Re-solved with the exact cores in the hypothesis and the pool pruned by `K'`:

| | before | after |
|---|---|---|
| τ | 5.000000000063 (at the budget — alive) | **3.250000** |
| η = τ − budget | +6.3e−11 | **−1.750000** |
| converged | no (240 s cap) | no (240 + 900 s knife-edge cap) |
| verdict | ALIVE-at-LP | **certified DEAD** |

**`verify_case_v3.py` PASS (rc = 0)**, certificate `certs/k5_11_interior_Y0241__poly.json`, total
3.43334 < budget 5, after one witness-feedback round. The frozen `verify_case.py` on the same
measure with the exact square cores alone **FAILs with 32 HOLES** — so "this kill needs the polygon
clause" is a measurement here, not a claim. The v3 box tree:
`boxes = 187914, covered = 65469, vacuous = 0, exempt = 28520 (core 24984, nofam 0, poly 3536),
split = 93925, max depth = 39` — **3,536 boxes discharged by the polygon clause**, and without them
the mass is genuinely short.

τ dropped by 1.75 out of 5. The impossible fraction predicted 0.60 of the objective was removable;
the LP gave up 0.35 of it after re-optimising onto other columns, which is the honest reading of
what the fraction buys.

## The nine certified kills

| node | frac | τ before | τ after | rounds | verifier | frozen on the same measure | poly-exempt boxes |
|---|---|---|---|---|---|---|---|
| `k5_11_interior_Y0241` | 0.600 | 5.000000 | **3.250000** | 2 | **v3** | FAIL, 32 holes | 3,536 |
| `k5_11_interior_Y0588_D06` | 1.000 | 5.000000 | **4.500000** | 1 | **v3** | FAIL, 8 holes | 1,038 |
| `k5_11_interior_Y0186_D05` | 0.800 | 5.000000 | **4.000000** | 1 | **v3** | FAIL, 24 holes | 1,433 |
| `k5_16_interior_Y0017_D04` | 0.857 | 3.500000 | **3.000000** | 1 | **FROZEN** | — (it PASSED) | — |
| `k5_11_interior_Y1056_D01` | 0.525 | 4.769231 | **4.000000** | 1 | **v3** | FAIL, 24 holes | 4,036 |
| `k5_11_interior_Y0164` | 0.524 | 4.666667 | **4.565217** | 2 | **FROZEN** | — (it PASSED) | — |
| `k5_11_interior_Y0041_D03` | 0.523 | 4.333333 | **4.222222** | 2 | **v3** | FAIL, 8 holes | 892 |
| `k5_16_interior_Y1014` | 0.376 | 4.538462 | **4.000000** | 1 | **FROZEN** | — (it PASSED) | — |
| `k5_11_interior_Y0572` | 0.376 | 4.500000 | **4.208262** | 2 | **v3** | FAIL, 24 holes | 168,451 |

**3 of the 9 are certified by the FROZEN verifier**, with nothing changed but the half-side written
into `cores` — A135's T1 finding cashed at scale for the first time. The other 6 need A135's
`polycores` clause. One further node (`k5_11_interior_Y1110`, frac 1.000) killed at the LP
(τ 4.851852) but **lost the kill on the witness-feedback re-solve** and is recorded uncertified;
two more (`Y0186_D01` frac 0.800, `Y0656` frac 0.375) did not kill at all.

**Six of the nine were already LP-dead** — work-owing `FAIL` nodes whose stored τ was below budget
and which were only ever missing a *certificate*. For those A145's contribution is the certificate,
not the kill. **Three are genuinely new kills** (`Y0241`, `Y0588_D06`, `Y0186_D05`), all three at
frac ≥ 0.60, all three v3.

## Is the PI's reading a predictor? — yes, and it has a threshold

Kill rate against the exact impossible fraction, all 18 re-solves:

| band | n | LP kills | certified | frozen | v3 | kill rate | mean drop in τ |
|---|---|---|---|---|---|---|---|
| [0.00, 0.15) | 3 | 0 | 0 | 0 | 0 | **0.00** | 0.000000 |
| [0.15, 0.30) | 3 | 0 | 0 | 0 | 0 | **0.00** | −0.000000 |
| [0.30, 0.45) | 3 | 2 | 2 | 1 | 1 | 0.67 | 0.276733 |
| [0.45, 0.60) | 3 | 3 | 3 | 1 | 2 | **1.00** | 0.327264 |
| [0.60, 0.75) | 1 | 1 | 1 | 0 | 1 | **1.00** | 1.750000 |
| [0.75, 1.01] | 5 | 4 | 3 | 1 | 2 | 0.80 | 0.429630 |
| **total** | **18** | **10** | **9** | **3** | **6** | 0.56 | |

Restricted to the nodes whose stored τ was AT the budget (the clean question — for a `FAIL` node the
kill was never in doubt):

| band | n | LP kills | certified | kill rate |
|---|---|---|---|---|
| [0.00, 0.15) | 3 | 0 | 0 | 0.00 |
| [0.15, 0.30) | 3 | 0 | 0 | 0.00 |
| [0.30, 0.45) | 1 | 0 | 0 | 0.00 |
| [0.60, 0.75) | 1 | 1 | 1 | 1.00 |
| [0.75, 1.01] | 4 | 3 | 2 | 0.75 |

**Zero of the seven alive nodes below frac 0.45 moved τ by so much as 1e−9; four of the five above
frac 0.60 killed.** That is the separation, and it is why the ranking is worth having: it is not a
smooth dose-response, it is a floor. Below ~0.3 the exact cores and the polygon buy the LP nothing
— those nodes' dual support is already living outside every hypothesis square, and the mean drop in
τ is exactly 0. Above ~0.6 the LP has nowhere left to put the weight.

### What the fraction does NOT predict

* **It does not predict the size of the drop.** `Y0588_D06` and `Y1110` both carry frac = 1.000 and
  drop by only 0.500 and 0.148; `Y0241` at 0.600 drops by 1.750. The LP re-optimises onto columns
  the fraction never saw. The fraction is a *gate*, not a dose.
* **It does not predict which verifier.** Frozen-vs-v3 tracks how much of the excluded weight is
  the pins' (frozen suffices) versus the conditioned box's polygon (v3 needed), which is A132's
  attribution axis, not this one. `Y0017_D04` at 0.857 goes frozen; `Y0041_D03` at 0.523 needs v3.
* **18 nodes is not a rate.** A132's caveat transfers verbatim. What 18 nodes with a control arm
  *do* establish is the sign and the location of the threshold, which one node could not.

### The honest caveats

* Six of the nine certified nodes were already LP-dead, so the certified count is not nine new
  kills. It is **three new kills plus six certificates for kills the campaign already had and could
  not close.** Both are worth collecting; they are not the same thing.
* `Y0241`'s LP never converged, at 240 s or at 1140 s. A124's "CAP is never a verdict" applies to
  the LP and not to the verdict, which is the verifier's: `total < budget` is an inequality on
  rationals and the box tree is exact. An unconverged LP can only fail to certify.
* The knife-edge rule fired on 3 of 18 nodes and cost 900 s twice. It earned its keep once
  (`Y0241`: 240 s gave τ = 3.250000000000027 unconverged, 900 s gave τ = 3.2500000000725695
  unconverged — the long cap did not move τ, it confirmed it was not about to climb back).
