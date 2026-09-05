# A87 flood87 -- recursive YOUNG FLOOD at fixed side

Extends `exchange87.py` (its exact certifier and high-resolution fit search are reused verbatim; the INSCRIBED-SQUARE objective, never void area, decides every fit).  Per packing and per starting corner, the flood grows a Young diagram of exact axis-aligned unit cells anchored at the corner, paying for each cell with the squares it displaces.  See the module docstring of `code/flood87.py` for the state, the step rules and the accounting.

## Headline

- (packing, corner) cases run: **33**
- floods that SUCCEED (11 squares at the same side, exactly verified): **30** of 33
- corners exchange87 could NOT convert: **12** (11 of them on real packings, 1 the canary)
- **corners the FLOOD rescues that exchange87 could not: 9** of those 11  -- polish12_s0380/TR (depth 2), polish12_s0380/TL (depth 2), polish15_s0076/TR (depth 3), polish15_s0076/TL (depth 2), polish24_s0259/BL (depth 2), anchored0_p140/BR (depth 2), anchored0_p140/TL (depth 2), anchored1_p094/BR (depth 2), anchored2_p094/BR (depth 2)
- **maximum depth needed: 3**
- corners still not converted by either: record_s0115/BL, record_s0115/BR
- every one of the 8 K0-BLOCKED packings has at least one corner that converts, so all 8 are CONVERTIBLE at their own side.
- CANARY (Trump TL at s-hat): **fails as required** -- status `no_completable_slot`, terminal deficit **2**, depth reached 4, diagram shape [3, 3, 3].  No second packing at s-hat is produced.

## Per (packing, corner)

| packing | side m | corner | exchange87 | flood | depth | terminal deficit | \|R\| | \|D\| | slid | anywhere-fits | diagram shape |
|---|---|---|---|---|---|---|---|---|---|---|---|
| record_s0115 | 3.985483727 | BL | fail | no_completable_slot | 4 | 2 | 6 | 9 | 5 | 0 | [3, 3, 3] |
| record_s0115 | 3.985483727 | BR | fail | no_completable_slot | 2 | 2 | 4 | 9 | 7 | 0 | [3, 3, 3] |
| record_s0115 | 3.985483727 | TR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| record_s0115 | 3.985483727 | TL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish12_s0380 | 4.000000120 | BL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish12_s0380 | 4.000000120 | BR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish12_s0380 | 4.000000120 | TR | fail | SUCCESS | 2 | 0 | 2 | 2 | 0 | 0 | [2] |
| polish12_s0380 | 4.000000120 | TL | fail | SUCCESS | 2 | 0 | 2 | 7 | 5 | 0 | [3, 2, 1, 1] |
| polish15_s0076 | 4.000004060 | BL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish15_s0076 | 4.000004060 | BR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish15_s0076 | 4.000004060 | TR | fail | SUCCESS | 3 | 0 | 4 | 9 | 6 | 1 | [3, 3, 2, 1] |
| polish15_s0076 | 4.000004060 | TL | fail | SUCCESS | 2 | 0 | 2 | 4 | 2 | 0 | [1, 1, 1, 1] |
| polish21_s0380 | 4.000007453 | BL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish21_s0380 | 4.000007453 | BR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish21_s0380 | 4.000007453 | TR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish21_s0380 | 4.000007453 | TL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish24_s0259 | 4.000011862 | BL | fail | SUCCESS | 2 | 0 | 2 | 5 | 3 | 0 | [4, 1] |
| polish24_s0259 | 4.000011862 | BR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish24_s0259 | 4.000011862 | TR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| polish24_s0259 | 4.000011862 | TL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored0_p140 | 4.107107416 | BL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored0_p140 | 4.107107416 | BR | fail | SUCCESS | 2 | 0 | 2 | 3 | 1 | 0 | [3] |
| anchored0_p140 | 4.107107416 | TR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored0_p140 | 4.107107416 | TL | fail | SUCCESS | 2 | 0 | 4 | 5 | 3 | 2 | [4, 1] |
| anchored1_p094 | 4.083735462 | BL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored1_p094 | 4.083735462 | BR | fail | SUCCESS | 2 | 0 | 4 | 5 | 3 | 2 | [2, 1, 1, 1] |
| anchored1_p094 | 4.083735462 | TR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored1_p094 | 4.083735462 | TL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored2_p094 | 4.083735887 | BL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored2_p094 | 4.083735887 | BR | fail | SUCCESS | 2 | 0 | 4 | 5 | 3 | 2 | [2, 1, 1, 1] |
| anchored2_p094 | 4.083735887 | TR | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| anchored2_p094 | 4.083735887 | TL | SUCCESS | SUCCESS | 1 | 0 | 2 | 1 | 0 | 1 | [1] |
| TRUMP_canary | 3.877083590 | TL | fail | no_completable_slot | 4 | 2 | 6 | 9 | 5 | 0 | [3, 3, 3] |

## Per packing: does SOME corner work?

| packing | side m | corners where the FLOOD succeeds | corners where exchange87 succeeded | verdict |
|---|---|---|---|---|
| record_s0115 | 3.985483727 | TR, TL | TR, TL | CONVERTIBLE |
| polish12_s0380 | 4.000000120 | BL, BR, TR, TL | BL, BR | CONVERTIBLE |
| polish15_s0076 | 4.000004060 | BL, BR, TR, TL | BL, BR | CONVERTIBLE |
| polish21_s0380 | 4.000007453 | BL, BR, TR, TL | BL, BR, TR, TL | CONVERTIBLE |
| polish24_s0259 | 4.000011862 | BL, BR, TR, TL | BR, TR, TL | CONVERTIBLE |
| anchored0_p140 | 4.107107416 | BL, BR, TR, TL | BL, TR | CONVERTIBLE |
| anchored1_p094 | 4.083735462 | BL, BR, TR, TL | BL, TR, TL | CONVERTIBLE |
| anchored2_p094 | 4.083735887 | BL, BR, TR, TL | BL, TR, TL | CONVERTIBLE |
| TRUMP_canary | 3.877083590 | - | - | no corner works |

## Deficit trajectories and step statistics

| quantity | count |
|---|---|
| completable slots examined (over all cases and depths) | 57 |
| ... with n = 0 intruders (a FREE cell -- rule (i)) | 10 |
| ... with n = 1 intruder AT THE CENSUS | 0 |
| ... with n = 2 intruders | 47 |
| ... with n >= 3 intruders | 0 |
| slide-in bonus fires (rule (iii), a free placement) | 43 |
| high-resolution anywhere-fit calls | 51 |
| ... that placed a square (lambda >= 1, exactly verified) | 28 |
| cases in which some slot ever had n = 0 | 8 of 33 |
| cases in which the slide-in bonus ever fired | 11 of 33 |
| cases in which some slot ever had n >= 3 | 0 of 33 |

Reading of the census.  A slot with **n = 0** is what actually pays down the deficit -- rule (i) puts a removed square straight into it; those 10 free cells are the whole reason the flood gets past depth 1.  A slot with **n = 1** never survives to be counted, because the bonus runs to a fixpoint first and turns every one of them into a slide-in: the **43 bonus fires are the n = 1 slots**.  What is left over is strikingly uniform -- **every remaining slot the flood ever met had exactly n = 2 intruders (47 of them), and NOT ONE slot in NOT ONE case ever had n >= 3.**  The corner-slot census that A90 ran at depth 1 (n_block = 2 at every corner of every K0-BLOCKED packing) therefore continues to hold at every cell of the staircase, not just the first.

Depth histogram of the successful floods: depth 1: 21, depth 2: 8, depth 3: 1

### deficit trajectory, per case (deficit after each step)

| packing | corner | trajectory | terminal |
|---|---|---|---|
| record_s0115 | BL | 1 -> 2 -> 1 -> 2 | 2 |
| record_s0115 | BR | 1 -> 2 | 2 |
| record_s0115 | TR | 0 | 0 |
| record_s0115 | TL | 0 | 0 |
| polish12_s0380 | BL | 0 | 0 |
| polish12_s0380 | BR | 0 | 0 |
| polish12_s0380 | TR | 1 -> 0 | 0 |
| polish12_s0380 | TL | 1 -> 0 | 0 |
| polish15_s0076 | BL | 0 | 0 |
| polish15_s0076 | BR | 0 | 0 |
| polish15_s0076 | TR | 1 -> 2 -> 0 | 0 |
| polish15_s0076 | TL | 1 -> 0 | 0 |
| polish21_s0380 | BL | 0 | 0 |
| polish21_s0380 | BR | 0 | 0 |
| polish21_s0380 | TR | 0 | 0 |
| polish21_s0380 | TL | 0 | 0 |
| polish24_s0259 | BL | 1 -> 0 | 0 |
| polish24_s0259 | BR | 0 | 0 |
| polish24_s0259 | TR | 0 | 0 |
| polish24_s0259 | TL | 0 | 0 |
| anchored0_p140 | BL | 0 | 0 |
| anchored0_p140 | BR | 1 -> 0 | 0 |
| anchored0_p140 | TR | 0 | 0 |
| anchored0_p140 | TL | 1 -> 0 | 0 |
| anchored1_p094 | BL | 0 | 0 |
| anchored1_p094 | BR | 1 -> 0 | 0 |
| anchored1_p094 | TR | 0 | 0 |
| anchored1_p094 | TL | 0 | 0 |
| anchored2_p094 | BL | 0 | 0 |
| anchored2_p094 | BR | 1 -> 0 | 0 |
| anchored2_p094 | TR | 0 | 0 |
| anchored2_p094 | TL | 0 | 0 |
| TRUMP_canary | TL | 1 -> 2 -> 1 -> 2 | 2 |

## Step-by-step traces of the successful floods beyond depth 1

**polish12_s0380 / TR** (side 4.000000120): [2]
- d1 ii_pay_2 cell [0, 0]; removed [6, 7]; deficit 1 -> 1
- d2 i_free_cell cell [1, 0]; deficit 0 -> 0

**polish12_s0380 / TL** (side 4.000000120): [3, 2, 1, 1]
- d1 ii_pay_2 cell [0, 0]; removed [5, 4]; deficit 1 -> 1
- d2 i_free_cell cell [1, 1]; slide-ins: sq8 -> cell [0, 1], sq7 -> cell [1, 0], sq1 -> cell [0, 2], sq6 -> cell [2, 0], sq0 -> cell [0, 3]; deficit 0 -> 0

**polish15_s0076 / TR** (side 4.000004060): [3, 3, 2, 1]
- d1 ii_pay_2 cell [0, 0]; removed [6, 7]; deficit 1 -> 1
- d2 ii_pay_2 cell [1, 0]; removed [5, 9]; slide-ins: sq10 -> cell [0, 1], sq2 -> cell [0, 2], sq3 -> cell [0, 3]; deficit 2 -> 2
- d3 i_free_cell cell [1, 2]; slide-ins: sq8 -> cell [1, 1], sq4 -> cell [2, 0], sq1 -> cell [2, 1]; deficit 1 -> 0

**polish15_s0076 / TL** (side 4.000004060): [1, 1, 1, 1]
- d1 ii_pay_2 cell [0, 0]; removed [4, 5]; deficit 1 -> 1
- d2 i_free_cell cell [0, 3]; slide-ins: sq1 -> cell [0, 1], sq0 -> cell [0, 2]; deficit 0 -> 0

**polish24_s0259 / BL** (side 4.000011862): [4, 1]
- d1 ii_pay_2 cell [0, 0]; removed [0, 1]; deficit 1 -> 1
- d2 i_free_cell cell [0, 1]; slide-ins: sq8 -> cell [1, 0], sq3 -> cell [2, 0], sq2 -> cell [3, 0]; deficit 0 -> 0

**anchored0_p140 / BR** (side 4.107107416): [3]
- d1 ii_pay_2 cell [0, 0]; removed [3, 2]; deficit 1 -> 1
- d2 i_free_cell cell [2, 0]; slide-ins: sq1 -> cell [1, 0]; deficit 0 -> 0

**anchored0_p140 / TL** (side 4.107107416): [4, 1]
- d1 ii_pay_2 cell [0, 0]; removed [5, 4]; deficit 1 -> 1
- d2 ii_pay_2 cell [0, 1]; removed [0, 9]; slide-ins: sq10 -> cell [1, 0], sq6 -> cell [2, 0], sq7 -> cell [3, 0]; deficit 2 -> 0

**anchored1_p094 / BR** (side 4.083735462): [2, 1, 1, 1]
- d1 ii_pay_2 cell [0, 0]; removed [2, 3]; deficit 1 -> 1
- d2 ii_pay_2 cell [1, 0]; removed [9, 0]; slide-ins: sq10 -> cell [0, 1], sq6 -> cell [0, 2], sq7 -> cell [0, 3]; deficit 2 -> 0

**anchored2_p094 / BR** (side 4.083735887): [2, 1, 1, 1]
- d1 ii_pay_2 cell [0, 0]; removed [2, 3]; deficit 1 -> 1
- d2 ii_pay_2 cell [1, 0]; removed [9, 0]; slide-ins: sq10 -> cell [0, 1], sq6 -> cell [0, 2], sq7 -> cell [0, 3]; deficit 2 -> 0

## Exact certificates of the rescued packings

| packing | corner | depth | diagram | squares | min pair gap lb | certified tangencies | exact rational pairs | interior-disjoint | contained |
|---|---|---|---|---|---|---|---|---|---|
| polish12_s0380 | TR | 2 | [2] | 11 | 0.000e+00 | 1 | 1 | True | True |
| polish12_s0380 | TL | 2 | [3, 2, 1, 1] | 11 | 0.000e+00 | 11 | 21 | True | True |
| polish15_s0076 | TR | 3 | [3, 3, 2, 1] | 11 | 0.000e+00 | 19 | 36 | True | True |
| polish15_s0076 | TL | 2 | [1, 1, 1, 1] | 11 | 0.000e+00 | 3 | 6 | True | True |
| polish24_s0259 | BL | 2 | [4, 1] | 11 | 0.000e+00 | 5 | 10 | True | True |
| anchored0_p140 | BR | 2 | [3] | 11 | 0.000e+00 | 2 | 3 | True | True |
| anchored0_p140 | TL | 2 | [4, 1] | 11 | 0.000e+00 | 5 | 15 | True | True |
| anchored1_p094 | BR | 2 | [2, 1, 1, 1] | 11 | 0.000e+00 | 5 | 15 | True | True |
| anchored2_p094 | BR | 2 | [2, 1, 1, 1] | 11 | 0.000e+00 | 5 | 15 | True | True |

Each of these is an 11-square packing at the SAME side as its K0-BLOCKED input, with an exact axis-aligned unit square in the corner (so k >= 1).  Every pair is certified interior-disjoint and every square certified inside the container; the min pair gap is 0 because adjacent cells of the diagram share an edge, and those rows are evaluated in EXACT rational arithmetic.  The configurations are stored verbatim (exact rationals) as `final_config` in `results/flood87.jsonl`, and were re-checked independently by float SAT and float containment: 11 squares, min SAT gap >= 0 and min clearance >= 0 in all 30 successful cases, with the exact corner cell present in each.

## Canary detail

- status `no_completable_slot`; depth reached 4; terminal deficit **2**; diagram shape [3, 3, 3] (9 cells); 6 squares removed, 5 slid in, 0 anywhere-fits; final configuration holds 9 of the 11 squares.
- d1 ii_pay_2 cell [0, 0]; removed [6, 4]; anywhere-fit lambda_max = 0.982348675 (10 hosts)
- d2 ii_pay_2 cell [0, 1]; removed [3, 7]; slide-ins: sq9 -> cell [1, 0], sq5 -> cell [2, 0]; anywhere-fit lambda_max = 1.167469337 (9 hosts), 0.877083590 (10 hosts)
- d3 i_free_cell cell [1, 1]; slide-ins: sq0 -> cell [0, 2]; anywhere-fit lambda_max = 0.877083590 (10 hosts)
- d4 ii_pay_2 cell [1, 2]; removed [8, 1]; anywhere-fit lambda_max = 0.877083590 (9 hosts)
- d5 none cell None; slide-ins: sq10 -> cell [2, 1], sq2 -> cell [2, 2]

## Method notes

- Cells are EXACT rational axis-aligned unit squares in the corner frame; a cell (i, j) is inside the container iff i + 1 <= m and j + 1 <= m, tested on the exact rational side m.
- Intruders of a cell = untouched squares whose SAT gap against the cell is < -1e-9 (exchange87's TOL_BLOCK: a tangency is not an intrusion).  Ties among equally cheap slots go to the slot nearest the corner, ordered by (i+j, max(i,j), i, j).
- The slide-in bonus is checked at its DESTINATION -- the moved square's final pose is interior-disjoint from everything else present and inside the container -- not along a continuous path.  A packing is a configuration, not a motion.  It fires exactly when a completable cell's only intruder is the square being slid in, so it converts what would have been a paid rule-(ii) step into a free one.
- The anywhere-fit fallback is exchange87_refine's high-resolution search: per-tilt best centre over 90 tilts on the 1/200 grid, then a pattern search in (cx, cy, theta) from the best cell of the top 6 tilts, decided by the largest INSCRIBABLE square lambda, and any lambda >= 1 verified exactly (rational coordinates, interval SAT gaps > 0 against every square, container clearance >= 0).
- That fallback is SPECULATIVE: fitted squares are committed only if they close the whole remaining deficit.  A partial fit is discarded, because a square parked mid-container blocks the very cells the flood still needs (observed on the canary, where committing a partial fit ended the flood two depths early).
- The brief writes the deficit as |R| - |D| and calls the slide-in a free placement.  A slid square is not a removed square, so the cell it takes is not available to a removed one; the quantity that decides whether the result is an 11-square packing is deficit = |R| - (removed squares actually placed) = 11 - (|U| + |D| + |anywhere-fits|), and that is the deficit reported here and the one SUCCESS tests.  |R|, |D| and the slide-in count are tabulated separately, so the |R| - |D| reading is recoverable.
- CERTIFIER.  exchange87's interval certifier is reused, with two corrections the flood forces.  (1) Two exactly axis-aligned rational unit squares have a RATIONAL SAT gap max(|dx| - 1, |dy| - 1); routing it through iv.mpf(num)/iv.mpf(den) rounds the two sides independently and reports -4.6e-41 for two cells that share an edge by construction -- exactly the correction exchange87.clearance_info already applies to the CONTAINER rows of such a square, here extended to the PAIR rows.  (2) A packing asks for INTERIOR-disjointness, so a certified gap >= 0 passes; exchange87.certify_config's `disjoint_certified` demands > 0, a bar the Trump input packing itself fails (its squares touch: min pair gap -6.4e-40).  Both verdicts are reported per case (`interior_disjoint_certified` and `strictly_disjoint_certified`), and `final_cert_exchange87_strict` keeps exchange87's own unmodified verdict alongside.  A gap lower bound of >= 0, exact or interval, is a rigorous certificate that the two OPEN squares are disjoint.
- FAILURE is recorded when no completable slot is inside the container, when the next removal would push |R| past 9, or at the depth cap of 8 steps.

Data: `results/flood87.json` (summary), `results/flood87.jsonl` (full per-case traces incl. every slot census, every slide-in and every fit call), `results/flood87.log`.
