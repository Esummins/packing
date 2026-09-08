# T1 — what the ALIVE re-check actually bought, and why the headline number was wrong twice

## The correction, first

A131's point is right and it is worse than it looks. `recheck96.py:116` decides

```python
kills=(tau is not None and tau < bud)
```

and **never calls `certify.py`**. So every "kill" the re-check has ever reported — the night's
11 and today's — is an **LP verdict, not a certificate**. Nothing in `recheck96.jsonl` has been
through the frozen verifier.

Second, and larger: `tau < budget` is not a margin. Grading today's and the night's kills by the
campaign's *own* strict criterion (`eta < −0.005·tau`, the rule A96's three-arm study used and
PAUSED.md §5b quotes) against the knife-edge band `|eta| < 1e-9`:

| run | rows with `kills=true` | STRICT | WEAK | KNIFE (`\|eta\| < 1e-9`) |
|---|---|---|---|---|
| A123 night | 11 | **1** | 2 | 8 |
| A124 today | 20 | **2** | 1 | 17 |

The night's celebrated **"11 certified kills from 23 nodes, 47.8 %"** is, read honestly,
**one strict kill** (`Y0054`, eta −2.82e-02), two at eta ≈ −1e-09 where tau prints as 5.000000,
and eight at eta between −1e-10 and −1e-15 — floating-point noise on tau = budget. It was
neither 11, nor certified.

Today's two strict kills are `k5_11_interior_Y1099` (eta −1.000, converged) and
`k5_11_interior_Y1002` (eta −3.45e-02). **Both were already known:** PAUSED.md §5b records that
A96's arm C found strict kills at exactly `{Y1002, Y0817, Y1099}` and that arm B killed all
three. Fifteen CPU-hours of re-solving rediscovered two nodes the three-arm study had already
identified, and found no third.

## The day's actual yield

| item | kills | CPU cost |
|---|---|---|
| `trimsweep124` — T5″ full kills banked from the ALIVE queue | **54** (L1 31, L2 20, L3 3) | **0.0 s** |
| re-check, strict LP kills | **2** (both previously known) | ~15 CPU-h |
| re-check, weak/knife `kills=true` | 18 | (same 15 CPU-h) |
| re-check, wall-capped (not a verdict, still ALIVE) | 7 | 1500 s each |

The 54 are genuine logic kills — T5 with a tilt range, the same epistemic status as
`KILL-BY-LOGIC`, no LP and no certificate required, and the excluded intervals are persisted.
The 2 are LP verdicts awaiting a certificate.

**So the ranking in `docs/budget.md` is backwards.** The re-check is listed as "the best
per-budget item on the board". Measured over a full day it returned 2 strict kills for ~15 CPU-h;
the geometry sweep returned 54 for zero, and the scan of the FAIL queue
(`notes/trim_empty_alive.md` §5) says 55 more resolver items are dead by the same rule. The
retroactive T5″ scan is the best per-budget item by three orders of magnitude, and it was sitting
in the results files the whole time.

## Why no certificates were produced today, and the one-line fix

`certify.py` takes a **node json** — the `solve_node` result — as its first positional argument.
`recheck96` (and `recheck124` as launched this morning) call `solve_node(..., out=None)`, so that
file is never written. Certifying a re-check kill therefore costs a **full re-solve first**
(~900–1500 s) before certify.py's own 240 s, which did not fit today's remaining cap and clock.

Fixed for future runs in `code/recheck124.py`: the LP result is now written to
`results/nodes/<id>.json` (in A124, never into A57), and each record carries `grade`,
`node_json`, and an explicit `certified: null` / `cert_note: "LP verdict only; certify.py not
run"` so the ledger can never again be read as certified. With the node json on disk, certifying
the backlog of re-check kills costs only certify.py — about 240 s each, ~8 CPU-min for the three
non-knife kills of both runs.

**Recommended next step, and it is small:** run
`certify.py <node json> --s_rat 969271/250000 --time_limit 240 --out <A124 certs>` over
`Y0054`, `Y1099`, `Y1002` (and `Y0103`, `Y0402`, `Y0486` if the weak band is wanted), and report
certified / cert-FAIL separately. Do **not** attempt the knife-edge nodes: at eta = −1e-14 the
certifier is being asked to prove a strict inequality that holds by less than its own arithmetic
noise, which is what the campaign's `--scale` margin exists to avoid.

## Skips

A131's `backlog131.jsonl` lists 132 unclosed nodes that clip to EMPTY by pure geometry, 112 of
them under the already-deployed trim — those 112 are the same population as
`notes/trim_empty_alive.md` (57 ALIVE + 55 FAIL), and A124 has banked the 54 ALIVE ones that were
still queued. **Eight of A131's ids are still in the remaining re-check queue** and are not empty
under the *deployed* `trim57.trim_box`; they empty only under A131's extended pin-clip rule.
A124 has therefore **not** recorded them as kills — asserting another attempt's unvalidated rule
is not this chore's call — but they should be skipped rather than solved, and A131 should record
them itself once its rule is controlled the way `trim96`/`trim57` were (741/741 and 674/674).
