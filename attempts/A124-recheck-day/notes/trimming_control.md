# T2 — the touched-vs-emptied control, and what it does to the schedule

`code/control124.py`, 2026-09-07, 4.7 s over the 2,418-row corpus (`results/control124.json`).
Read-only on A96/A57: it imports `trim96.rows/surviving` and `pinguard.classify` unmodified.

## The finding in one line

**The offline control never conflated the two categories — PAUSED.md v2 §4's table did.** v1
reported "159 boxes gain an empty surviving bin ... 155 more are partially trimmed"
(`docs/residue_ledger.md` line 46), i.e. 159 = EMPTIED and 155 = TRIMMED, correctly separated.
PAUSED.md v2 §4 then tabulated the 159 as "boxes touched by trimming, 6.62 %" and compared it
against the live **touch** rate of 6.42 %, which made those two look like a match and made the
live full-kill rate of 1.01 % look like a 3.7× shortfall. Both halves of that comparison were
against the wrong figure.

## Three disjoint classes, re-measured

Per box: EMPTIED (surviving fraction 0 — a full T5″ kill, no LP ever runs), TRIMMED
(0 < fraction < 1 — the bin narrows, the node still pays a full LP), UNTOUCHED (fraction 1).
T5′ is **recomputed** with the deployed tight core (`pinguard.classify`, `TIGHT_CORE = True`)
rather than read off the stored `cert`, because much of the corpus predates the tight core.

Positive control: **741 of 741** boxes that T5′ kills come out fully EMPTIED — clean, and a
stronger version of v1's 618/618.

Excluding stored logic kills (the population v1 quoted), n = 1,744:

| level | n | EMPTIED | TRIMMED | UNTOUCHED | emptied | trimmed | touched |
|---|---|---|---|---|---|---|---|
| 1 | 1266 | 51 | 108 | 1107 | 4.03 % | 8.53 % | 12.56 % |
| 2 | 425 | 86 | 55 | 284 | 20.24 % | 12.94 % | 33.18 % |
| 3 | 39 | 10 | 1 | 28 | 25.64 % | 2.56 % | 28.21 % |
| 4 | 14 | 12 | 2 | 0 | 85.71 % | 14.29 % | 100 % |
| **all** | **1744** | **159** | **166** | **1419** | **9.12 %** | **9.52 %** | **18.64 %** |

**EMPTIED = 159 reproduces v1's 159 exactly**, and TRIMMED = 166 is v1's 155 plus the rows added
since. So the corrected offline figures are **9.1 % emptied, 18.6 % touched** — not the
"6.62 % touched" of PAUSED.md v2.

Incremental over T5′ (EMPTIED and not already killed by the tight core — the only class that
changes the schedule), n = 1,677: **92 boxes** (L1 34, L2 54, L3 3, L4 1), i.e. the honest "89"
is now **92**; the level-2 and level-3 counts are v1's 54 and 3 unchanged, L1 grew 31 → 34 with
the night's rows. Rates 2.72 % / 13.74 % / 9.38 % / 33.3 % by level, 5.49 % overall. TRIMMED
incremental is 166 (9.90 %), and those nodes cost exactly what they cost before.

## The live comparison, with denominators that match

A123's 296 level-1 children: 90 die to T5′ first, so the T5″-eligible population is **206**, of
which 3 were emptied and 16 trimmed. The right offline comparator is therefore *level-1,
incremental over T5′*, and — to keep it out of sample — computed on the 1,043 level-1 boxes that
predate the night:

| | live (206) | offline, out of sample (1,043) | Fisher p |
|---|---|---|---|
| EMPTIED | 3 = **1.46 %** [0.30, 4.20] | 31 = **2.97 %** | 0.35 |
| TRIMMED | 16 = **7.77 %** [4.50, 12.31] | 94 = **9.01 %** | 0.69 |

**The live run is consistent with the projection on both categories.** The apparent 3.7 % → 1.0 %
collapse was two artefacts stacked: (i) 3.70 % is the *all-levels* incremental rate and the night
emitted only level-1 children, which is the least favourable level (2.97 % offline, against
13.7 % at level 2); (ii) the live 1.01 % used 296 as its denominator instead of the 206 that T5′
had not already killed. Correct both and the gap is 1.46 % vs 2.97 %, p = 0.35 on three events.

Independent cross-check of the deployed rule: the control classes exactly the 3 night rows with
`pin_info == "trim"` (`k5_11_interior_Y0191`, `Y0251`, `Y0525`) as EMPTIED and no others — 3 of 3
agreement between `trim57.trim_box` in production and `trim96.surviving` offline.

Caveat on the corpus: the 296 night rows are persisted **post-trim** (§6's MUST-FIX — a
single-piece trim leaves no marker and the original extent is gone), so re-running the control
over them measures a bin that has already been trimmed once. That biases the full-corpus rates
*downwards*, which is why the live comparison above is drawn against the pre-night rows only.

## Schedule, counting full kills only

`code/schedule124.py` → `results/schedule124.json`. Model, all inputs measured: expansion factor
0.91 per level (level-2 descent 11.3 % into 8 children), tree terminates at level 4 (descent
0 of 30), node cost level-independent (level-2 LP settled at 1.11×), and

    E_L = (1 − f_L) · (1 + 0.91 · E_{L+1}),   f_L = the incremental full-kill rate at level L.

A TRIMMED node contributes nothing: it pays the same LP as before. Baseline 13.3 wall-days at 5
workers (the tight core alone; 19.6 without it).

| rates used | wall-days | cut |
|---|---|---|
| none (T5″ kills nothing) | 13.3 | 0 |
| offline, all levels | **10.5** | 21.3 % |
| live L1, offline L2–L4 | **10.6** | 20.3 % |
| live L1, L2–L4 discounted by the same live/offline factor 0.535 | **11.7** | 12.0 % |

**The 13.3 → 10–11 figure survives.** It was already a full-kills-only number — the model
reproduces it at 10.47 from the per-level incremental counts — and substituting the live level-1
rate moves it by 0.1 wall-days, because the saving is dominated by level 2, where there is still
no live data at all. The honest range is **10.5–11.7 wall-days**, and the pessimistic end
assumes the live/offline shortfall is real (p = 0.35 says it need not be) and repeats at every
level.

**What to measure next, and it is not level 1.** Every wall-day of this saving rests on the
level-2 incremental rate of 13.7 %, measured offline on 393 boxes and never once observed live.
The first `deepen.py` run after the resume settles it; nothing about level-1 emission will.
