# A151 T1 -- kill rates by A107 shadow family (A137 night 2026-09-07/08 + A149 day)

Family = A107's shadow attribution of the node itself, or of its nearest ancestor that the gallery classifies. `post-A107` = a child emitted after A107's gallery was built (A107 covers 1,566 of the 3,160 corpus rows), so it has no ancestor in the gallery at all.

### L1 -- exact-pin-core RE-SOLVE of the pre-existing ALIVE population (A137 163 + A149 57 = 222 nodes)

| family | n | PASS | NO-KILL | LOST-KILL-ON-RESOLVE | TOO-TIGHT | FAIL | WALL-CAP | decided | **kill rate** | median wall |
|---|---|---|---|---|---|---|---|---|---|---|
| S02 | 57 | 21 | 17 | 11 | 6 | 2 | 0 | 57 | **36.8 %** | 513 s |
| S01 | 96 | 24 | 65 | 3 | 2 | 0 | 2 | 94 | **25.5 %** | 386 s |
| other-shadow | 42 | 7 | 31 | 2 | 2 | 0 | 0 | 42 | **16.7 %** | 321 s |
| post-A107 (no gallery entry) | 27 | 5 | 18 | 4 | 0 | 0 | 0 | 27 | **18.5 %** | 460 s |
| **all** | 222 | 57 | 131 | 20 | 10 | 2 | 2 | 220 | **25.9 %** | 444 s |

### L2 -- fresh-emission LP with exact cores (first LP of a child emitted that night, 189 nodes)

| family | n | PASS | NO-KILL | LOST-KILL-ON-RESOLVE | TOO-TIGHT | FAIL | WALL-CAP | decided | **kill rate** | median wall |
|---|---|---|---|---|---|---|---|---|---|---|
| S02 | 22 | 13 | 4 | 3 | 1 | 0 | 1 | 21 | **61.9 %** | 484 s |
| S01 | 21 | 14 | 5 | 0 | 2 | 0 | 0 | 21 | **66.7 %** | 446 s |
| other-shadow | 14 | 11 | 1 | 2 | 0 | 0 | 0 | 14 | **78.6 %** | 227 s |
| fractional | 17 | 17 | 0 | 0 | 0 | 0 | 0 | 17 | **100.0 %** | 498 s |
| post-A107 (no gallery entry) | 115 | 94 | 12 | 7 | 2 | 0 | 0 | 115 | **81.7 %** | 82 s |
| **all** | 189 | 149 | 22 | 12 | 5 | 0 | 1 | 188 | **79.3 %** | 201 s |

### L3 -- geometric leaves at emission (kill rate = dead by geometry / screened)

| family | screened | dead | T5' exact core | T5''' clip | T5'''' polygon | other | **kill rate** | L1 | L2 | L3 |
|---|---|---|---|---|---|---|---|---|---|---|
| S02 | 674 | 185 | 135 | 50 | 0 | 0 | **27.4 %** | 16/58 | 102/464 | 60/144 |
| S01 | 859 | 204 | 163 | 41 | 0 | 0 | **23.7 %** | 12/76 | 170/688 | 22/95 |
| S07 | 1 | 0 | 0 | 0 | 0 | 0 | **0.0 %** | 0/1 | 0/0 | 0/0 |
| other-shadow | 517 | 102 | 70 | 32 | 0 | 0 | **19.7 %** | 6/64 | 96/437 | 0/16 |
| fractional | 49 | 1 | 1 | 0 | 0 | 0 | **2.0 %** | 1/49 | 0/0 | 0/0 |
| post-A107 (no gallery entry) | 840 | 306 | 270 | 36 | 0 | 0 | **36.4 %** | 210/560 | 96/280 | 0/0 |
| **all** | 2940 | 798 | 639 | 159 | 0 | 0 | **27.1 %** | 245/808 | 464/1869 | 82/255 |
