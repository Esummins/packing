# A114 — notes and findings

Scope: docs/residue_ledger.md §2 window fragments and stragglers. Two banked mechanisms only
(A96's resolver, A56's sub-window bisection) plus one gate change on A61's re-solve route.
Frozen verifiers byte-identical; every claim carries a C2 canary against the UNMODIFIED
A53 `verify_case.py`.

## L1 (soundness) — what an enumeration pass has to satisfy before the resolver may be used

The resolver argument is: a FAIL run at depth D DISCHARGED every placement whose `s` lies
outside the union of the witness cells' exact s-intervals, because every box containing such a
placement was decided (covered / exempt / vacuous). Re-verifying the SAME certificate on each
witness s-interval and passing there closes the window as the A86 T4 WindowRows disjunction.

This is sound only if the witness set is COMPLETE (A56 soundness.md P6(iv); A56 V7 recorded the
same restriction for sub-window bisection). `verify_param` truncates the witness set in two
independent ways, and A56's original runs hit both:

  * `--max-witnesses K` stops the whole search (and with `--jobs > 1` *terminates the pool*),
  * `--max-witnesses-per-box k` ABANDONS the rest of a root box's stack after k witnesses
    (`verify_param.py`, `run()`: `if per_box_cap is not None and len(...) - nw0 >= per_box_cap:
    break`) — the abandoned subtree is neither discharged nor recorded.

A56's scoreboard witness files were produced at `--jobs 3 --max-witnesses 20` (24 witnesses
recorded, a multiple of the per-box cap 8), so **they are not usable as gap lists**. Every A114
enumeration pass therefore runs at `--jobs 1 --max-witnesses-per-box 10**6 --max-witnesses 2000`
and records `search_complete = (n_witnesses < max_witnesses)`; nothing is claimed when it is
false. A96's `resolve96.py` is not affected: its gap lists come from A95/A96 runs that carry
`search_complete`, and its own `--max-witnesses-per-box 1` re-verification runs are used only
for their PASS/FAIL exit code.

## L2 (measurement) — the C2 canary depth is not part of the claim

A56's C2 convention is the unmodified A53 verifier at depth 44. On k6_23 — the 501-atom
certificate whose own parametric run needs depth 56 — the depth-44 canary at the slab midpoint
returns FAIL with **2 undecided boxes and 0 holes**, i.e. it ran out of subdivision at exactly
the tangency (theta ~ 49 deg, centre ~ (2.35, 2.15)) that made the certificate hard in the first
place. That is a canary budget, not a discrepancy: an `undecided` witness is "not decided at
this depth", a `hole` would be a genuine uncovered placement. The canary is therefore run at the
depth the certificate needs, and both readings are kept in the record file.

## L3 (arithmetic) — for k5_12 the 0.03 post-shrink gate was not the binding constraint

`certify.py`'s auto scale is `scale = max(1.005, min(scale_cap, (budget - 0.005)/tau - 0.002))`
and it refuses outright (`return 3`, before any verifier round) when `total = tau*scale >=
budget`. With the 1.005 floor a row therefore needs

    budget - tau_eps  >  0.005 * tau_eps          (~0.0299 at tau_eps ~ 5.97, budget 6)

A61 pass 5 measured `budget - tau = 0.02646` for k5_12 — BELOW that floor, so at pass 5's own tau
the 0.02 gate would have bought nothing but a `return 3`. What A114's re-run actually measured is
more interesting: **both LP stages are time-capped and unconverged, so tau varies run to run**.
The A114 pass landed at

    tau0 = 5.625000 (slack0 0.3750)   tau_eps = 5.949587 (slack 0.05041)   dtau/d eps = 111.9

i.e. it would have cleared the ORIGINAL 0.03 gate too. `certify` therefore did build a round-0
certificate (scale 1.0056, total 5.98317 < budget 6, 146 atoms) — and the exact verifier FAILed it
at depth 56; the witness-feedback re-solve then drove tau to exactly the budget (6.000000), so
round 1's total 6.03001 >= 6 and certify aborted (rc 3). Conclusion: for k5_12 at eps_geo 0.003
the obstacle is neither the gate nor the scale floor but the LP itself — there is no certifiable
measure at that shrink with this column pool. Lowering eps_geo (0.0029 keeps the floor satisfied
with headroom and stays far above P6(v)'s 0.0015 threshold) treats the symptom; the round-0 exact
FAIL says the row wants a richer column pool. Cost of the run: 4210 s.

## L4 (measured) — the slab sweep, and why it beats both the resolver and blind bisection

Mechanism (B) needs NO witness completeness: a `verify_param` PASS on a closed sub-window is a
sound partial transfer whatever the witness bookkeeping did (A56 P3), so a set of PASSing slabs
whose union is [3.82, s0] closes the row outright. That makes it strictly safer than the
resolver, and — once the slabs are small enough — it is also cheaper, because the verifier's
cost is superlinear in the slab width while a FAIL is decided almost immediately.

Measured cost per 10^-3 of s at depth 48, `--jobs 1`, from A114's own runs:

| class | atoms | margin   | s / 10^-3 | note                                                |
|-------|-------|----------|-----------|-----------------------------------------------------|
| k6_27 | 25    | 0.078878 | ~11 s     | 14 slabs, whole window, 1826 s                       |
| k6_07 | 11    | 0.193327 | ~65 s     | 18 slabs over the 0.050 band, ~3400 s                |
| k5_03 | 40    | 0.163310 | ~340 s    | 14 slabs = 0.0033 of s, 1660 s                       |
| k5_02 | 54    | 0.000553 | n/a       | 0.0071-wide slabs FAIL at 224 s / 239 s              |

Two rules fall out:

* **Grid, don't bisect from the top.** k6_07's band went 1 slab -> TIMEOUT at 1800 s, then both
  halves FAIL at 1518 s and 1588 s — 4900 s that bought nothing. The same band re-gridded into 16
  pieces of 0.0029 passed slab by slab at ~190 s each, every slab PASS first time. A wide slab is
  where the depth budget is spent on s-splitting instead of (t, cx, cy), which is A96's finding in
  the form it costs money.
* **A bisection slab needs only its exit code**, so cap its witnesses (`--slab_maxw 8`). A COMPLETE
  enumeration (L1) over a wide slab is a full traversal: on k6_07's 0.050 band it was still running
  after 21 minutes, versus 87 s for A56's capped probe of the same window.

## L5 — resolver-first diagnostic on the three OPEN strata (the brief's item 4)

Re-verifying the SAME certificate on each recorded 4-D witness cell, depth 56, sscale 1:

    k6_27   3/3 cells PASS (7.2 s, 53.7 s, 88.9 s)
    k5_02   2/2 cells PASS (76.3 s, 56.2 s)
    k5_03   8/8 cells PASS (31-128 s each)

So every recorded failure of all three is the verifier starving the s-axis, exactly as A96 found
— it is NOT node hardness at those cells. That is a diagnostic, not a claim: those witness files
are truncated (L1), so the complement is not certified by it. Following it up with the slab sweep
separated the three cleanly: k6_27 closed outright, while k5_02's and k5_03's BULK slabs (away
from any recorded witness) fail or time out. The tight cells were never these two rows' problem.
