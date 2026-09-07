# A131 follow-up — the retrospective backlog sweep (pure geometry, no LP)

`code/backlog_certs131.py` → `results/backlog_kills.jsonl` + `certs/backlog/<id>.clipkill.json`;
independently re-verified by `code/checkclip131.py`. **A57/A96 state untouched** — their jsonl,
progress and cert trees were not written to; the only A57 file appended to is `PAUSED.md` (one line
in the resume block, §8), which says the campaign's owner folds these rows in.

## Result

**132 recorded-open nodes killed by T5‴ geometry alone, 4.1 s of CPU.** One
`pin-clip-kill-certificate-v1` per node carrying: the class pins, the recorded box, the rational
outer box, the 8 tilt sub-bins (as exact `t = tan(θ/2)` endpoints and degrees), the **replayable
clip trace** (every slab removal with its pin, side, from/to as exact rationals), the witness pins,
the prior verdict/τ/η, and the sample confirmation.

| | |
|---|---|
| nodes | **132** |
| by level | 63 / 57 / 6 / 6 (L1–L4) |
| by class | 93 k5_11 / 39 k5_16 |
| by prior verdict | 74 ALIVE (51 L1 + 23 depth-2) / 58 FAIL |
| witness | 111 single-pin, **21 two-pin joint** |
| T5″ alone suffices | 112 |
| **needs the clip** | **20** |
| independent check | **132 PASS, 0 FAIL** |
| sampling | **1,584,000 drawn → 1,584,000 tested → 0 hits** (≥ 12,000 tested per node; the whole box × bin is discarded, so drawn = tested) |

## The 20 that need the clip, and the 21 that need two pins

`results/backlog_clip_only.jsonl` (+ `.json`). The two sets nearly coincide and the difference is
informative:

- **20 clip-only** (T5″ does not empty them): 17 L1 + 3 L2; 14 k5_11 / 6 k5_16; 17 prior ALIVE,
  3 prior FAIL. `Y0009`, `Y0025`, `Y0145`, `Y0150`, `Y0360`, `Y0387`, `Y0546`, `Y0580`, `Y0727`,
  `Y0745`, `Y1146`, `Y0546_D07`, `Y1146_D02`, `Y1146_D03` (k5_11) and `Y0009`, `Y0025`, `Y0360`,
  `Y0527`, `Y0546`, `Y0580` (k5_16).
- **21 two-pin joint** = those 20 plus `k5_11_interior_Y0360_D06`. Every clip-only node is a
  two-pin node — T5″ only ever tests whether ONE pin dominates the whole box, so a box carved by
  two pins from opposite sides is invisible to it. The extra node goes the other way:
  `Y0360_D06` needs two pins for the whole-bin clip but T5″ *does* empty it, because T5″ may use
  **different** single pins on different tilt sub-intervals. **Neither rule contains the other in
  general; the clip contains T5″ on this corpus (159/159, plus 21).**

`k5_11_interior_Y0546` is in the clip-only list and is the node the 900 s re-check spent **2,179 s**
on — its most expensive kill.

## The independent checker caught a real discrepancy (and it resolved in the clipper's favour)

`checkclip131.py` re-derives the dead test in the `t` parametrisation rather than the θ-sinusoid
one: `f(t) = (P(1−t²)+2Qt)/(1+t²)` has `f'(t) = −2g(t)/(1+t²)²` with `g(t) = Qt² + 2Pt − Q`. Its
first version treated **every** interior extremum as a maximum and rejected **23 of 132** sound
certificates. A 40,001-point brute-force SAT grid on one of them showed 0 separating tilts — the
clipper was right. The fix is the sign rule that falls out of `f' = −2g/(1+t²)²`: an interior
*maximum* is `g` going **− → +**; `g` going **+ → −** is a minimum and the maximum stays at an
endpoint. Re-validated after the fix: 30,000 random (offset, sub-bin) pairs against both
`pinclip.dead_q` and a 1,201-point grid — **0 disagreements, 0 unsound, 0 missed** on either
implementation (`results/xcheck_checker131.json`).

## eps_geo retry on the three T3 cert-FAIL nodes — NEGATIVE, with a mechanism

`code/epsgeo131.py`, 0.56 CPU-h of the 1 allowed, 2 BelowNormal BLAS-pinned processes.

Which ladder: the **row-shrink (`certify.py --eps_geo`)** one — a plain CLI with `--out`, exactly
what `tree57.run_eps_geo` shells out to on every FAIL, at `tree57.eps_geo_margins`' own choice of
(0.002, 0.004) since all three have scale ceiling ≥ 1.05. The **EPS_CORE ladder
(`epsladder.py`) was SKIPPED**: it hardcodes its certificate directory to A57's `certs/epsladder`
and writes `results/epsladder_<id>.json` into A57's tree with no flag to redirect, so it is a
driver by the test that matters here.

| node | τ (clipped) | ceiling | eps_geo 0.002 | eps_geo 0.004 | verdict |
|---|---|---|---|---|---|
| `Y0036_D03` | 4.000 | 1.250 | τ → 5.000, rc 3 | τ → 5.000, rc 3 | FAIL, retries exhausted |
| `Y0996` | 4.500 | 1.111 | NOT certified, rc 1 | τ → 5.000, rc 3 | FAIL, retries exhausted |
| `Y0636_D04` | 4.500 | 1.111 | τ → 5.000, rc 3 | τ → 5.000, rc 3 | FAIL, retries exhausted |

**All three fail the same way and for one reason: the row-shrink re-solve pushes τ from 4.0 / 4.5
straight back to exactly 5.0 = budget**, at both margins, so there is nothing to certify. On a
*clipped* box the LP's whole slack is the 2·10⁻³ shell around the pinned squares that eps_geo
re-imposes — the clip and the row-shrink are antagonistic, and the clip's gain is exactly the size
of the shell. Consequence for deployment: **do not chain eps_geo after a pin-clip**; a clipped node
whose certificate has holes should go to the resolver or to depth, not to the row-shrink ladder.
