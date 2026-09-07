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

## L6 (predictor, advisor's) — the widest slab a certificate can take, from ONE probe

`verify_param` splits the widest axis of a 4-D cell, so a run has to buy two things out of the
same depth budget: enough s-splitting to reach a leaf s-cell narrow enough for the certificate's
margin to absorb the dilation (call that width `w_min`), and enough (t, cx, cy) splitting to
decide a pose (call that `d_pose`). Both are properties of the CERTIFICATE, not of the slab, so a
slab of width `W` passes iff

    log2(W / w_min) + d_pose  <=  depth        (depth = 48 here)      =>  W <= w_min * 2^(depth - d_pose)

and one probe slab measures both, straight out of the report's `stats`:

    w_min   = W_probe / 2^(max_s_depth)          d_pose = max_depth - max_s_depth

**k6_07, the case that paid for the lesson.** Every passing 0.0029 slab reported
`max_depth 46, max_s_depth 7` -> `w_min = 2.285e-5`, `d_pose = 39`, so
`width_max = 2.285e-5 * 2^9 = 0.0117`: **5 pieces would have covered the 0.050 band**, not 18.
The two failing halves of 0.0235 reported `max_s_depth 10` (the same 2.3e-5 leaf cell) and
`max_depth 48` — the cap — with 8 undecided boxes and 0 holes: exactly `log2(0.0235/2.285e-5) +
39 = 49 > 48`. Under-splitting costs a full timeout per slab (1500-1800 s here); over-splitting
costs only the sublinear part of the cost law, so **when in doubt grid at half of `width_max`**.

`max_depth == depth` in a PASSing report is the "no headroom" flag: the formula then returns
`width_max ~ W` and the slab is at the limit, so do not widen. Measured on A114's four sweeps:

| class | w_min    | d_pose | width_max | grid used | headroom |
|-------|----------|--------|-----------|-----------|----------|
| k6_27 | 2.76e-5  | 39     | 0.0141    | 0.00707   | 1 level (and d_pose rises to 40 in [3.8697, 3.8768], which is exactly why that slab FAILed) |
| k6_07 | 2.285e-5 | 39     | 0.0117    | 0.00293   | 2 levels (over-split 4x) |
| k5_02 | 2.78e-5  | 42     | 0.00178   | 0.001777  | none — at the limit (and the earlier 0.0071 slabs, 4x over, FAILed) |
| k5_03 | 2.79e-5  | 42     | 0.00179   | 0.001791  | none — at the limit |

So the three cheap rows differ in `d_pose`, not in `w_min`: 39 for k6_07/k6_27 versus 42 for
k5_02/k5_03 — three extra levels of pose subdivision, which is an 8x narrower slab and (by the
cost law below) roughly an 8x longer sweep for the same band.

**Slab-time trend across a band** (same width throughout, depth 48, jobs 1):

    k6_27  0.00707 slabs:  78.7 -> 121.4 s bottom to top (+54%); the bisected top pieces 85.6, 257.8 s
    k6_07  0.00293 slabs: 167.3 -> 266.4 s bottom to top (+59%)
    k5_02  0.00178 slabs: 150.9 -> ~180 s   (+20%, flat middle)
    k5_03  0.00179 slabs: 640.1 -> 574.7 s over the first six (-10%)

Cost is sublinear in width for a fixed certificate (k5_03: 5.6e-5 -> 34 s, 1.79e-3 -> ~610 s, i.e.
32x the width for 18x the time), so a coarser grid is cheaper as long as it stays under
`width_max` — which is the whole point of measuring `width_max` before gridding.

## L7 (measurement) — verification cost along s, and what it says about the S02 shadow

The advisor's hypothesis was that the k7 pinwheel (S02, s* = s0 + 0.0097) squeezes these classes'
slack near the top of the window, so the s0 certificate should be replaced slab by slab with a
base LP re-solved at each slab's top side. A114 measured the cost profile instead
(results/cost_profile.json, one row per verifier run: s_top, width, seconds, seconds per 1e-3 of
s, max_depth, max_s_depth, d_pose, boxes). Sampled seconds per 1e-3 of s, bottom to top:

| class | 3.821 | 3.83 | 3.845 | 3.859 | 3.8735 | last 1e-4 below s0 |
|-------|-------|------|-------|-------|--------|--------------------|
| k6_27 | 19.9  | 11.1 | 11.6  | 13.0  | 17.1   | 479 -> 2245 (d_pose 39 -> 43-45) |
| k6_07 | --    | 53.3 | 64.8  | 64.9  | 75.5   | (band starts at 3.827) |
| k5_02 | 88.7  | 78.4 | 83.4  | 74.4  | 108.3  | -- |
| k5_03 | 412   | 331  | 822   | 574   | --     | 439 s for the 5e-4 slab at s0 |
| k5_12 | 129   | 137  | 189   | 208   | 408    | 351 s for the 8.4e-5 slab at s0 |

So the cost per unit of s does rise toward s0 — mildly through the bulk (+38% to +59% over the
window for k6_07/k5_02/k6_27) and then sharply in the last ~5e-4, where `w_min` shrinks (k5_12:
width_max 0.00100 at s_top 3.8405 versus 0.00050 at s_top 3.877, with 1.74M boxes versus 12.7M
for the same 5e-4 width) and, for k6_27, `d_pose` itself climbs 39 -> 40 -> 43. That is the
shadow showing up in the arithmetic, and it is the first direct measurement of it.

Completed profile (results/cost_profile.json, 224 verifier runs), seconds per 1e-3 of s at the
bottom of the window versus the slab that ends AT s0:

    k6_27   19.9 -> 1589      k6_07   53.3 -> 91.0       k5_02   88.7 -> 501.6
    k5_03  412.3 -> 1063.6    k5_12  129.2 -> 4181.4     k6_23   (s0 slab only) 2161

The last slab of every class is 2x-32x more expensive per unit of s than the first: the cost
concentrates in the final ~1e-4 to ~5e-4 below s0, which is where the S02 pinwheel's shadow sits.

**But the operational conclusion is the opposite of the hypothesis: the s0 certificate does not
need replacing.** Re-verified on slabs that respect L6's `width_max`, the ORIGINAL A53/A54
certificate (re-expressed parametrically by A56) covers the WHOLE window for k5_02 (35 slabs),
k5_12 (85 slabs), k5_03 (14 + 34 slabs) and k6_27 (14 slabs) — including, in each case, the last
slab that ends exactly at s0 — with the full C2 canary at s_lo, midpoint and s0 every time. What the shadow costs is slab WIDTH near the
top, not certificate validity. Three further reasons the per-slab re-solve was not run:

1. **It needs new tooling, not banked tooling.** `make_param.py` hard-codes S0 and rejects any
   core coordinate that is not a slot of the s0 census (`core_anchor`: "not a slot of the s0
   census"), so a base certificate solved at s_top < s0 cannot be turned into a parametric one
   without editing a frozen builder — exactly what A114's charter forbids.
2. **The cost is prohibitive.** A k5-class base LP is 1200-1900 s per solve (A61 pass 5, and
   A114's own k5_12 run), so ~30-85 slabs of re-solve is 10-45 CPU-h before a single verifier
   run — against a 15 CPU-h cap for the whole continuation.
3. **The premise did not survive the data.** k5_02's earlier bulk FAILs were at the BOTTOM of the
   band as well as the top, and they were 0.0071-wide slabs — 4x over `width_max`. Every one of
   them passes at 0.0018 with the same s0 certificate.

The re-solve route stays available if a class ever fails a slab at a width where `w_min` has
genuinely collapsed; nothing measured here needs it.
