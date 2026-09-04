# pocket96 — k6 slot-pocket exemption yield on A57 / A96 witnesses (A96 chore, 2026-09-04)

Code `code/pocket96.py`, data `results/pocket96.json`. Read-only on all campaign files; one
process, OMP_NUM_THREADS=1; no commit.

## 0. Verdict — the yield is ~0

| tolerance | source | holes | pocket holes | **usable** pocket holes | undecided | pocket undec. | **usable** | nodes | nodes all-holes-pocket | nodes all-witnesses-pocket |
|---|---|---|---|---|---|---|---|---|---|---|
| δ=0.01, 1° | A57 (tree+epsgeo) | 2809 | 32 (1.14 %) | **8 (0.28 %)** | 4110 | 0 | 0 | 249 | **0** | **0** |
| δ=0.01, 1° | A96 parametric | 0 | – | – | 264 | 0 | 0 | 77 | 0 | 0 |
| δ=0.02, 2° | A57 (tree+epsgeo) | 2809 | 46 (1.64 %) | **16 (0.57 %)** | 4110 | 10 (0.24 %) | 0 | 249 | **1** | **2** |
| δ=0.02, 2° | A96 parametric | 0 | – | – | 264 | 2 (0.76 %) | 2 | 77 | 0 | 0 |

"pocket" = every slot in the coordinator's fallback list; "**usable**" = restricted to slots
whose k6 extension is actually killed over the window (below). The single all-holes-pocket node
and the two all-witnesses-pocket nodes at δ=0.02 are *k5_16* nodes that had ALREADY been
repaired to PASS, and they only qualify against the non-usable slot list — **zero FAIL nodes
would certify with the exemption, at either tolerance, in either class.**

Every pocket box is in **k5_16**. k5_11 contributes **zero** pocket holes and zero pocket
undecided boxes at both tolerances: the closest any k5_11 witness box gets to any completable
slot is L∞ = 0.0889 (holes) / 0.108 (undecided), i.e. ~9× the δ=0.01 pad and ~4.5× δ=0.02.

## 1. Pin tolerance the k6 window kills were emitted with (grep result)

`grep` over `attempts/A61-window-stragglers/certs` and `attempts/A54-stragglers/certs` for
`delta` / `slack` / `pin`: **no `delta_pin`, `pin_delta`, `slack_core` or `core_radius` field
exists anywhere.** What is there is uniform across all 220 k6 cores (33 base certs + 33 A56
parametric certs + the A61 re-solves), position and tilt alike:

    "a":  16383999967232/32768001953125   (= 1/2 − 3.0802320551733e-08)
    "tm": 1/33554432                      (= 2^-25;  θ = 2·atan(tm) = 3.4150946e-06 deg)

and in the fixed-s certs the pin `box` is degenerate (`x0=x1`, `y0=y1`, `th0=th1=0`); in the
A56/A61 `gp.param.json` the pin is the exact affine slot `a + b·s`. So the tolerance the k6
window kills were actually emitted with is:

* **position** 3.0802 · 10⁻⁸ (L∞ half-width, at zero tilt),
* **tilt** 3.4151 · 10⁻⁶ degrees,

identical for every k6 row (k6_18, k6_20, k6_23, k6_27, k6_28, k6_29, k6_30 included). At that
tolerance the yield is exactly zero — the emitted pockets are ~3·10⁻⁸ wide and the A57 witness
boxes are ~10⁻⁵ wide, three orders of magnitude larger, so not one box can be contained in one.
**The working tolerances used above (δ=0.01/1°, δ=0.02/2°) are A57's own slack-core emission
δ_pin = 10⁻² and A60's 2·10⁻²** — i.e. what a *re-emission* of the k6 rows with slack pin cores
would buy. They are therefore an optimistic upper bound on the yield, and it is still ~0.

## 2. Usable slots

The pocket exemption is only sound at a slot whose extension class is dead on the window
(Lemma SLOT-CROWD, `docs/proofs/slot_crowds.md` §1.2 / §2). Per A94 `results/slots94.json` +
the A56/A61 scoreboard:

* k5_11: BL(1,1)→k6_18 FULL, BR(0,1)→k6_20 FULL, TL(1,0)→k6_20 FULL, TR(0,0)→k6_23 PARTIAL
  ([3.82, 3.877] parametric + the A54 fixed-s cert AT s0 — the A57 trees are all at s0, so it
  counts). The other four completable cells are clipped (NOT-A-CLASS).
* k5_16: BL(1,0)→k6_23 (as above), BR(0,1)→k6_29 FULL, TR(0,1)→k6_30 FULL, TR(1,0)→k6_28 FULL.
  **BR(1,0) and TL(1,0) → k6_27, which is OPEN over the whole window — unusable.**

Which slots the pocket boxes actually sit at:

| tolerance | slot | k6 row | usable? | pocket boxes |
|---|---|---|---|---|
| δ=0.01 | k5_16 BR(1,0) | k6_27 | **no (OPEN)** | 24 holes |
| δ=0.01 | k5_16 BL(1,0) | k6_23 | yes | 8 holes |
| δ=0.02 | k5_16 BR(1,0) | k6_27 | **no** | 24 holes |
| δ=0.02 | k5_16 BL(1,1) | not a completable cell of k5_16 | **no** | 6 holes + 10 undecided |
| δ=0.02 | k5_16 BL(1,0) | k6_23 | yes | 16 holes |
| δ=0.02 | A96 param k5_16 BL(1,0) | k6_23 | yes | 2 undecided |

So two thirds of the (already tiny) raw yield is parked at the one slot whose k6 row is OPEN.
If k6_27 ever closes, the usable yield at δ=0.02 would rise from 16 to 40 holes out of 2809
(1.4 %) — still no node flipping to certifiable.

## 3. Per class / per node outcome (δ = 0.01, 1°; `results/pocket96.json` has both)

A57 bookkeeping note, established here: a **FAIL** node's `.witnesses.json` matches its
`.report.json` `stats.witnesses` exactly (94 nodes, live witnesses); a **PASS** node's
`.witnesses.json` is the *stale pre-repair* witness set of the attempt that a deeper /
eps_geo re-run subsequently repaired (155 nodes, `stats.witnesses == 0`, report always newer
than the witness file). Those 155 are exactly the "eps_geo-repaired PASS" population the chore
asks about, and are labelled `repairedPASS` in the JSON.

| class | outcome | nodes | holes | pocket | undecided | pocket |
|---|---|---|---|---|---|---|
| k5_11 | FAIL (incl. epsgeo re-runs) | 68 | 871 | 0 | 1377 | 0 |
| k5_11 | repairedPASS | 88 | 783 | 0 | 1209 | 0 |
| k5_16 | FAIL (incl. epsgeo re-runs) | 26 | 293 | 20 | 419 | 0 |
| k5_16 | repairedPASS | 67 | 862 | 12 | 1105 | 0 |
| k5_11 | A96 parametric FAIL | 33 | 0 | 0 | 110 | 0 |
| k5_16 | A96 parametric FAIL | 44 | 0 | 0 | 154 | 0 |

The A96 parametric certificates emit **no holes at all** — every witness is `undecided` — so the
exemption has nothing to bite on there beyond 2 boxes at δ=0.02.

## 4. Distance census (why the yield is ~0)

Median L∞ distance from a witness box to the nearest completable slot: k5_11 holes 0.81,
k5_11 undecided 0.86, k5_16 holes 0.72, k5_16 undecided 0.72. The 1st percentile is 0.093 /
0.258 / 0.0067 / 0.036. Only 40 of 2809 A57 holes are within 0.01 of any slot, 46 within 0.02,
63 within 0.05. The certification residue is **not** concentrated near the slots: A57's holes
are near-flush against *pin* squares and against each other, not parked at empty Young slots.
This is the continuum-escape story the chore anticipated for the LP, and it turns out to hold
for the certifier as well.

## 5. Canary

* **No k5_11 witness box contains a D4-image-of-Trump pose** at s0 (0 of 4048 boxes; the closest
  is `k5_11_interior_Y0930`, a hole, L∞ 0.0022 in centre but t-gap 0.034 ≈ 2° in tilt). And zero
  k5_11 boxes are classified as pockets at either tolerance. Canary **PASS** (vacuously).
* Correction to the chore's parenthetical: a Trump square **does** sit at a completable slot of
  k5_11 — Trump's upright square at (s−1/2, s−1/2) coincides *exactly* with k5_11's cell
  TR(0,0), at L∞ = 0 and tilt 0. This is not a counterexample: Trump is not a packing of class
  k5_11 (it lacks the k5_11 pin (1/2, s−1/2); its fifth upright is at (1/2, 2.5326)), so
  SLOT-CROWD / the k6_23 kill is never applied to it. But the guard cannot be stated as "no
  Trump square is near a completable slot of k5_11" — it has to be the class-membership
  argument. Recorded in `results/pocket96.json` under `canary_trump_slot_coincidence`.

## 6. Recommendation

Do not build the pocket exemption for A57. At the tolerance the k6 rows were actually emitted
with (3·10⁻⁸) it is exactly worthless; at a hypothetical δ_pin = 2·10⁻² re-emission it exempts
0.6 % of holes, all in k5_16, two thirds of them at the OPEN k6_27 slot, and flips **zero**
FAIL nodes to certifying. The certifier's holes are not near-flush *slot* ghosts.
