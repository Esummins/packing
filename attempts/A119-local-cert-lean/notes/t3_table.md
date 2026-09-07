# A119 T3 — the blocking squares as boxes, and the ρ ≥ 20° cap

| shadow/frame | r | ρ | cut | L | boxes | verdict | nodes | LP calls | near pairs | closed | certified min | measured min | sample hits | Trump in N | wall | witness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S02/k5_11 | 0.10 | 5° | — | block_ladder | 6 | **DEAD** | 58447 | 58447 | 16 | 29384 | 3.877101 | 3.886746 | 0 | False | 121 s | — |
| S02/k5_11 | 0.10 | 10° | — | block_ladder | 6 | **CAP** | 419843 | 449840 | 18 | 210933 | 3.877088 | — | — | False | 900 s | — |
| S02/k5_11 | 0.20 | 5° | — | block_ladder | 6 | **CAP** | 454624 | 464764 | 18 | 228586 | 3.877086 | — | — | False | 900 s | — |
| S02/k5_11 | 0.20 | 10° | — | block_f0_TR | 6 | **CAP** | 444615 | 418680 | 18 | 223480 | 3.877084 | — | — | False | 1200 s | — |
| S02/k5_11 | 0.20 | 10° | — | block_ladder (slot 0.05) | 6 | **CAP** | 435941 | 472193 | 18 | 219626 | 3.877084 | — | — | False | 900 s | — |
| S02/k5_11 | 0.20 | 20° | — | block_vs_alive | 6 | **CAP** | 318690 | 428103 | 22 | 161330 | 3.877108 | — | — | False | 900 s | — |
| S02/k5_11 | 0.20 | 20° | — | cap_original_L | 4 | **CAP** | 633660 | 795320 | 12 | 316824 | 3.877086 | — | — | False | 900 s | — |
| S02/k5_11 | 0.20 | 40° | — | block_vs_alive | 6 | **CAP** | 359686 | 493916 | 23 | 116478 | 3.881900 | — | — | False | 900 s | — |
| S02/k5_11 | 0.20 | 40° | — | cap_original_L | 4 | **ALIVE** | 392144 | 656052 | 12 | 86477 | 3.877567 | — | — | False | 559 s | 3.876703 |
| S07/trump5 | 0.10 | 5° | 41.565 | block_ladder | 6 | **CAP** | 444074 | 444074 | 18 | 224141 | 3.877092 | — | — | False | 900 s | — |
| S07/trump5 | 0.10 | 10° | 41.565 | block_ladder | 6 | **CAP** | 414453 | 435606 | 18 | 209124 | 3.877089 | — | — | False | 900 s | — |
| S07/trump5 | 0.20 | 5° | 41.565 | block_ladder | 6 | **CAP** | 447905 | 449849 | 19 | 225414 | 3.877085 | — | — | False | 900 s | — |
| S07/trump5 | 0.20 | 10° | 41.565 | block_f1_f3_BL02 | 6 | **CAP** | 411966 | 373791 | 19 | 206617 | 3.877085 | — | — | False | 1200 s | — |
| S07/trump5 | 0.20 | 10° | 41.565 | block_ladder (slot 0.05) | 6 | **CAP** | 363244 | 409822 | 19 | 183123 | 3.877086 | — | — | False | 900 s | — |
| S07/trump5 | 0.20 | 20° | 41.565 | block_vs_alive | 6 | **CAP** | 449903 | 396413 | 20 | 183028 | 3.877085 | — | — | False | 900 s | — |
| S07/trump5 | 0.20 | 20° | 41.565 | cap_original_L | 3 | **ALIVE** | 917 | 1416 | 10 | 416 | 3.877084 | — | — | False | 2 s | 3.873374 |
| S07/trump5 | 0.20 | 40° | 41.565 | block_vs_alive | 6 | **CAP** | 435927 | 365271 | 23 | 171465 | 3.878031 | — | — | False | 900 s | — |
| S07/trump5 | 0.20 | 40° | 41.565 | cap_original_L | 3 | **ALIVE** | 4769 | 6395 | 10 | 2057 | 3.877086 | — | — | False | 9 s | 3.869626 |

(`wall` is the TREE's wall clock; a DEAD verdict then costs a further 10⁴-sample
check + 30-start SLSQP + the Trump canary.  `L` names the run's label; `boxes` is the
number of FREE bodies, i.e. the number of tilt dimensions the tree must bisect.)

## (a) The blocking squares as boxes do NOT extend the radius

S02 gets `f0` and `TR(0,0)`, S07 gets `f1`, `f3` and `BL(0,2)` — the squares A116
identified as the ones that would forbid the r = 0.3 rearrangement.  They are the right
objects (see (c)) and they cost two extra tilt dimensions: 16–23 near pairs instead of
10–13, and 6 tilt intervals to bisect instead of 3–4.  **Exactly one blocking-box N
closes: S02 (0.1, 5°), DEAD in 121 s of tree (58 447 nodes, 29 384 closed leaves),
certified 3.877101, measured 3.886746, 0 hits in 10⁴ samples, Trump outside** — and it is
a strictly LARGER N than A116's own six-box run, which had to confine the slot square
`BR(0,1)` to a 0.05 box.  Every other blocking-box cell (r ≥ 0.2, or ρ ≥ 10°, either
shadow) hits the 900–1200 s cap with 320 000–460 000 nodes.  For S07 no blocking-box N
closes at all.  **So A116's (0.2, 10°) and (0.1, 40°) with the ORIGINAL L remain the
largest certified neighbourhoods, and the blocking-box route trades radius for tilt
dimensions at a loss.**

## (b) The ρ ≥ 20° frontier at r = 0.2 is ALIVE, not capped

A116 tabulates CAP at S02 (0.2, 20°) / (0.2, 40°) and S07 (0.2, 20°) / (0.2, 40°) and
reads them as "no witness and no dip were found there, so those cells are open, not
dead" (§5).  That reading is wrong, and for S07 **A116's own results file already
contains the refutation**: `t2_S07.jsonl` records 4 128 witnesses at (0.2, 20°) and
1 733 at (0.2, 40°), the first of each with `witness_valid: true` (worst pair gap
−4.4·10⁻¹⁶, worst wall gap 0) at sides 3.873374 and 3.869626 — checked packings of L ∪ P
below s0 — while the run's verdict field says `capped`.  (Re-running A116's own tree
TODAY with A116's own parameters returns ALIVE with the same witness in 25 s and 4 899
nodes: `code/f1probe.py`, `results/f1_probe.json`.  The stored rows were evidently
produced before `Tree._loop`'s "return on the first checked witness" existed, so the
ALIVE verdict never reached the table.)  The same mislabelling affects A116's
(0.3, 20°) and (0.3, 40°) rows in both shadows.

| N (original L) | A116 as tabulated | what is in A116's data | A119, independently | witness side |
|---|---|---|---|---|
| S07 (0.2, 20°), cut 41.565° | CAP, 107 796 nodes | 4 128 witnesses, first VALID | **ALIVE at node 917, 2 s** | 3.873374 (f0, f2, f4 all at 65°: the ladder shears) |
| S07 (0.2, 40°), cut 41.565° | CAP, 119 048 nodes | 1 733 witnesses, first VALID | **ALIVE, 4 769 nodes, 9 s** | 3.869626 (the same at 68.7°) |
| S02 (0.2, 40°) | CAP, 259 684 nodes | **0 witnesses** | **ALIVE, 392 144 nodes, 559 s** | 3.876703 — NEW (f3 turns to 88.3°, f1 to 12.2°, f2 to 8.4°) |
| S02 (0.2, 20°) | CAP, 138 451 nodes | 0 witnesses | CAP, **633 660 nodes** (4.6× the nodes in the same wall) | still genuinely open |

So **the S07 tilt radius at r = 0.2 is below 20°, and the S02 tilt radius at r = 0.2 is
below 40°** — not for want of budget but because the |L| + |P| squares really do
rearrange there.  The one cell that is merely capped is S02 (0.2, 20°).

## (c) The blocking squares DO kill those rearrangements

Re-running the three ALIVE cells with the blocking squares added as boxes finds NO
witness in 900 s and 320 000–450 000 nodes (verdict CAP, not ALIVE), and on S02
(0.2, 40°) the certified minimum over the CLOSED part of the tree rises from 3.877567 to
**3.881900** — well clear of s0.  The blocking squares are therefore the right objects;
what stops the proof is the tilt-cell count of a six-body tree, not the geometry.

## (d) The consumer count is unchanged

`code/consumer119.py` (a bipartite MATCHING instead of A116's 11 P |L| brute force —
same answer, and it terminates for |L| = 6) reproduces A116's table exactly:
**72 of 184 k5_11 + 23 of 68 k5_16 = 95 of the 252 S02-explained alive nodes** at
A116's (0.2, 10°) / (0.1, 10°), 2 of 18 for S07 at (0.1, 40°).  A119's new certified N,
S02 (0.1, 5°) with the blocking boxes, catches **1 of 184** — the supports do not hold
`f0` and `TR(0,0)` at the shadow's poses, exactly as A116 found for its own six-box run.
The blocking squares are a device for the certificate, not for the node cut.

