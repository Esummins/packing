# A236 -- RING-CAPACITY: the band / core / straddler trichotomy, the intrusion and the count, measured

Sources: the ring `rand_0_0569|t20` + the 193 HELD / CROWD four-crowds of A217 (loaded component U from A233's `arm233.jsonl`, union over the four corners), A226's eight-square crowd rings at n = 11 (`ring11_226.jsonl`), the 21 survey records + Trump's certificate (`survey226.jsonl`).  Band width 1: BAND = interior misses the open centre (1, s-1)^2, CORE = inside [1, s-1]^2, STRADDLER = neither.  `python capacity236.py` (25 s).

## 1. The ring and the 193 four-crowds (n = 11, sides 4.0014 .. 4.42: ABOVE m = 4, so the lemma must not fire)

| check ([T] lemma on data) | holds on |
|---|---|
| TILT-BAND: every tilted square (tilt > 1e-3 deg) intrudes into the centre (depth > 0) | 193 / 193 |
| BAND-FLUSH: every band square is flush (tilt < 1e-3 deg) and touches a wall | 193 / 193 |
| WALL-EXCESS: chord sums <= s on all four walls | 193 / 193 |
| touchers per wall <= floor(s) | 193 / 193 |
| BAND-COUNT: B <= 4(floor(s) - 1) (four-crowd, no corner slot) | 193 / 193 |
| CORE-CAP: K <= N_proved(s - 2) | 193 / 193 |
| ONE-TILTED: >= 4 tilted meeters | 193 / 193 |
| B + K + X = 11 | 193 / 193 |

Distributions: B (band) 0: 40, 1: 63, 2: 54, 3: 31, 4: 4, 5: 1; K (core) 0: 79, 1: 90, 2: 23, 3: 1; X (straddlers) 4: 1, 6: 6, 7: 19, 8: 45, 9: 67, 10: 42, 11: 13; tilted meeters 4: 1, 5: 23, 6: 61, 7: 61, 8: 47.
Loaded component U: p = |U| 0: 4, 9: 44, 10: 23, 11: 122 (p = 0: no A233 chain record); n - p 0: 122, 1: 23, 2: 44, 11: 4; U contains core squares on 67 / 193; max depth of a U member into the centre: min 0.000, median 1.016, max 1.338 (a "ring in a band of width 1 + d" needs d = that depth).
The rest (non-U squares): classes band: 5, core: 60, straddle: 90; n - p <= N_record(s - 2) on 189 / 193 (the 4 failures are the p = 0 rows).
Tilted meeters' intrusion iota = cos + sin - 1: min 0.0000, median 0.169, max 0.4142; their depth into the centre: min 0.0000, median 0.162.

**The ring** (side 4.1099): classes ['straddle', 'core', 'straddle', 'straddle', 'straddle', 'straddle', 'straddle', 'straddle', 'straddle', 'band', 'straddle']; B = 1, K = 1, X = 9; U = [2, 3, 4, 5, 6, 7, 8, 9, 10] (p = 9), rest [0, 1] (['straddle', 'core']); walls (flush / tilted touchers, chord sum): {'floor': (0, 2, 2.128), 'right': (0, 1, 1.064), 'ceil': (1, 2, 3.128), 'left': (0, 1, 1.064)}; meeters {'BL': [4, 5], 'BR': [6, 7], 'TR': [8, 10], 'TL': [2, 3]} with depth 0.21 .. 0.30 and iota = 0.2817 (20 deg); N_record(s - 2 = 2.11) = 4 >= n - p = 2.

## 2. A226's eight-square crowd rings at n = 11 (S < 4: the only four-crowd family BELOW m the lab has)

| ring | S | eps | B | K | X | meeter depth (tilted) | pocket: squares placed (greedy) | A226 k_max | inscribed flush square | N_proved(S-2) |
|---|---|---|---|---|---|---|---|---|---|---|
| ring8_S3.90_eps0.02 | 3.90 | 0.02 | 4 | 0 | 4 | 0.015 | 1 | 1 | 1.870 | 1 |
| ring8_S3.90_eps0.05 | 3.90 | 0.05 | 4 | 0 | 4 | 0.037 | 1 | 1 | 1.826 | 1 |
| ring8_S3.90_eps0.10 | 3.90 | 0.10 | 4 | 0 | 4 | 0.073 | 1 | 1 | 1.755 | 1 |
| ring8_S3.95_eps0.02 | 3.95 | 0.02 | 4 | 0 | 4 | 0.015 | 1 | 1 | 1.920 | 1 |
| ring8_S3.95_eps0.05 | 3.95 | 0.05 | 4 | 0 | 4 | 0.037 | 1 | 1 | 1.876 | 1 |
| ring8_S3.95_eps0.10 | 3.95 | 0.10 | 4 | 0 | 4 | 0.073 | 1 | 1 | 1.805 | 1 |
| ring8_S3.99_eps0.02 | 3.99 | 0.02 | 4 | 0 | 4 | 0.015 | 1 | 1 | 1.960 | 1 |
| ring8_S3.99_eps0.05 | 3.99 | 0.05 | 4 | 0 | 4 | 0.037 | 1 | 1 | 1.916 | 1 |
| ring8_S3.99_eps0.10 | 3.99 | 0.10 | 4 | 0 | 4 | 0.073 | 1 | 1 | 1.845 | 1 |

Reading: 8 ring members + 1 = 9 < 11 on every member of the family; the count allows 8 + 1 + 4 = 13.  The closure is the POCKET (a region search), not the count; the tilted members' depth is eps/2-small -- no intrusion floor.

## 3. The 21 records (not rings: 0 or 1 doubly-met corner; the lemma's hypothesis fails)

| record | n | s | m | B | K | X | tilted | doubly met | flush touchers per wall | tilted touchers per wall | N_p(s-2) | N_r(s-2) | 4(floor s - 1) | checks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| square-5 | 5 | 2.7071 | 3 | 4 | 0 | 1 | 1 | 0 | [2, 2, 2, 2] | [0, 0, 0, 0] | 0 | 0 | 4 | ok |
| square-10 | 10 | 3.7071 | 4 | 8 | 0 | 2 | 2 | 0 | [3, 3, 3, 3] | [0, 0, 0, 0] | 1 | 1 | 8 | ok |
| square-11 | 11 | 3.8771 | 4 | 6 | 0 | 5 | 5 | 1 | [3, 3, 1, 2] | [0, 0, 1, 1] | 1 | 1 | 8 | ok |
| square-17 | 17 | 4.6755 | 5 | 10 | 1 | 6 | 7 | 0 | [4, 4, 3, 3] | [0, 0, 0, 1] | 4 | 4 | 12 | ok |
| square-18 | 18 | 4.8229 | 5 | 10 | 2 | 6 | 8 | 0 | [3, 4, 3, 4] | [0, 0, 0, 0] | 5 | 5 | 12 | ok |
| square-19 | 19 | 4.8856 | 5 | 10 | 3 | 6 | 8 | 0 | [4, 4, 3, 3] | [0, 0, 0, 0] | 5 | 5 | 12 | ok |
| square-26b | 26 | 5.6213 | 6 | 15 | 6 | 5 | 9 | 0 | [5, 5, 5, 4] | [0, 0, 0, 0] | 9 | 9 | 16 | ok |
| square-27 | 27 | 5.7071 | 6 | 16 | 9 | 2 | 5 | 0 | [5, 5, 5, 5] | [0, 0, 0, 0] | 10 | 10 | 16 | ok |
| square-28 | 28 | 5.8244 | 6 | 16 | 8 | 4 | 12 | 0 | [5, 5, 5, 5] | [0, 0, 0, 0] | 12 | 10 | 16 | ok |
| square-29 | 29 | 5.9338 | 6 | 14 | 7 | 8 | 14 | 0 | [5, 5, 5, 3] | [0, 0, 0, 1] | 12 | 11 | 16 | ok |
| square-37 | 37 | 6.5986 | 7 | 18 | 11 | 8 | 15 | 0 | [6, 6, 5, 5] | [0, 0, 0, 0] | 21 | 16 | 20 | ok |
| square-38 | 38 | 6.7071 | 7 | 20 | 16 | 2 | 6 | 0 | [6, 6, 6, 6] | [0, 0, 0, 0] | 21 | 17 | 20 | ok |
| square-39 | 39 | 6.8107 | 7 | 20 | 15 | 4 | 15 | 0 | [6, 6, 6, 6] | [0, 0, 0, 0] | 21 | 17 | 20 | ok |
| square-40 | 40 | 6.8284 | 7 | 20 | 16 | 4 | 16 | 0 | [6, 6, 6, 6] | [0, 0, 0, 0] | 21 | 18 | 20 | ok |
| square-41 | 41 | 6.9267 | 7 | 17 | 16 | 8 | 15 | 0 | [6, 6, 4, 5] | [0, 0, 2, 1] | 21 | 19 | 20 | ok |
| square-50 | 50 | 7.5714 | 8 | 24 | 24 | 2 | 16 | 0 | [7, 7, 7, 7] | [0, 0, 0, 0] | 32 | 25 | 24 | ok |
| square-51 | 51 | 7.7008 | 8 | 22 | 21 | 8 | 22 | 0 | [7, 6, 7, 6] | [0, 1, 0, 1] | 32 | 26 | 24 | ok |
| square-52 | 52 | 7.7071 | 8 | 24 | 26 | 2 | 8 | 0 | [7, 7, 7, 7] | [0, 0, 0, 0] | 32 | 27 | 24 | ok |
| square-53 | 53 | 7.8229 | 8 | 23 | 25 | 5 | 14 | 0 | [7, 7, 6, 7] | [0, 0, 1, 0] | 32 | 27 | 24 | ok |
| square-54 | 54 | 7.8467 | 8 | 22 | 26 | 6 | 16 | 0 | [7, 6, 7, 6] | [0, 1, 0, 1] | 32 | 28 | 24 | ok |
| square-55 | 55 | 7.9458 | 8 | 22 | 25 | 8 | 18 | 0 | [7, 7, 7, 5] | [0, 0, 0, 1] | 32 | 29 | 24 | ok |
| trump_cert | 11 | 3.8771 | 4 | 6 | 0 | 5 | 5 | 1 | [3, 2, 1, 3] | [0, 1, 1, 0] | 1 | 1 | 8 | ok |

Reading: every record has X >= 1 straddlers (median 5) -- the tilted grain crosses the band line into the centre (cross-braced), B is at or just below 4(floor s - 1) and K <= N(s - 2) always; no record is a four-crowd, so BAND-COUNT is not invoked, and the count identity n = B + K + X holds on all 22.

## 4. Columns: s = record side (survey226; = m where no record below m is known; **proven** where s(n) is a theorem);
sigma = s - 2 (the centre's side); N_p / N_r = the centre's packing number from the proven / record staircase;
B_max = 4(m - 2) band squares (Lemma BAND-COUNT); K_max = (m - 2)^2 - 3 (Nagamochi, sigma < m - 2);
X_forced = max(4, n - B_max - N) straddlers forced by the count; slack = B_max + K_max + 4 - n = m^2 - 3 - n;
p_min(flat core) = n - (m - 3)^2 ring members if every non-ring square is flat and in the core (Lemma FLUSH),
against the 4(m - 1) toucher slots of the band (WALL-EXCESS); CROWD-ABOVE = four-crowds exist at every side
in (s(n), m) (A226), so no all-four-crowd inequality can close there.  Rows with s(n) = m are out of scope
(no packing below m; shown for completeness).  s > 2 + sqrt2 is the regime of TILT-BAND / distinct meeters.

| n | m | s(n) | below m | sigma | N_p | N_r | B_max | K_max | X_forced (p / r) | slack m^2-3-n | closes? | p_min flat core | toucher slots | CROWD-ABOVE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 3 | 2.7071 (proven) | yes | 0.707 | 0 | 0 | 4 | 0 | 4 / 4 | 3 | NO | 5 | 8 |  |
| 6 | 3 | 3 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 7 | 3 | 3 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 8 | 3 | 3 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 9 | 3 | 3 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 10 | 4 | 3.7071 (proven) | yes | 1.707 | 1 | 1 | 8 | 1 | 4 / 4 | 3 | NO | 9 | 12 |  |
| 11 | 4 | 3.8771 | yes | 1.877 | 1 | 1 | 8 | 1 | 4 / 4 | 2 | NO | 10 | 12 |  |
| 12 | 4 | 4 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 13 | 4 | 4 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 14 | 4 | 4 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 15 | 4 | 4 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 16 | 4 | 4 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 17 | 5 | 4.6755 | yes | 2.676 | 4 | 4 | 12 | 6 | 4 / 4 | 5 | NO | 13 | 16 |  |
| 18 | 5 | 4.8229 | yes | 2.823 | 5 | 5 | 12 | 6 | 4 / 4 | 4 | NO | 14 | 16 |  |
| 19 | 5 | 4.8856 | yes | 2.886 | 5 | 5 | 12 | 6 | 4 / 4 | 3 | NO | 15 | 16 |  |
| 20 | 5 | 5 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 21 | 5 | 5 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 22 | 5 | 5 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 23 | 5 | 5 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 24 | 5 | 5 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 25 | 5 | 5 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 26 | 6 | 5.6213 | yes | 3.621 | 9 | 9 | 16 | 13 | 4 / 4 | 7 | NO | 17 | 20 | yes |
| 27 | 6 | 5.7071 | yes | 3.707 | 10 | 10 | 16 | 13 | 4 / 4 | 6 | NO | 18 | 20 |  |
| 28 | 6 | 5.8244 | yes | 3.824 | 12 | 10 | 16 | 13 | 4 / 4 | 5 | NO | 19 | 20 | yes |
| 29 | 6 | 5.9338 | yes | 3.934 | 12 | 11 | 16 | 13 | 4 / 4 | 4 | NO | 20 | 20 | yes |
| 30 | 6 | 6 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 31 | 6 | 6 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 32 | 6 | 6 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 33 | 6 | 6 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 34 | 6 | 6 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 35 | 6 | 6 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 36 | 6 | 6 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 37 | 7 | 6.5986 | yes | 4.599 | 21 | 16 | 20 | 22 | 4 / 4 | 9 | NO | 21 | 24 | yes |
| 38 | 7 | 6.7071 | yes | 4.707 | 21 | 17 | 20 | 22 | 4 / 4 | 8 | NO | 22 | 24 |  |
| 39 | 7 | 6.8107 | yes | 4.811 | 21 | 17 | 20 | 22 | 4 / 4 | 7 | NO | 23 | 24 |  |
| 40 | 7 | 6.8284 | yes | 4.828 | 21 | 18 | 20 | 22 | 4 / 4 | 6 | NO | 24 | 24 | yes |
| 41 | 7 | 6.9267 | yes | 4.927 | 21 | 19 | 20 | 22 | 4 / 4 | 5 | NO | 25 | 24 |  |
| 42 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 43 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 44 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 45 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 46 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 47 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 48 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 49 | 7 | 7 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 50 | 8 | 7.5714 | yes | 5.571 | 32 | 25 | 24 | 33 | 4 / 4 | 11 | NO | 25 | 28 | yes |
| 51 | 8 | 7.7008 | yes | 5.701 | 32 | 26 | 24 | 33 | 4 / 4 | 10 | NO | 26 | 28 | yes |
| 52 | 8 | 7.7071 | yes | 5.707 | 32 | 27 | 24 | 33 | 4 / 4 | 9 | NO | 27 | 28 |  |
| 53 | 8 | 7.8229 | yes | 5.823 | 32 | 27 | 24 | 33 | 4 / 4 | 8 | NO | 28 | 28 |  |
| 54 | 8 | 7.8467 | yes | 5.847 | 32 | 28 | 24 | 33 | 4 / 4 | 7 | NO | 29 | 28 |  |
| 55 | 8 | 7.9458 | yes | 5.946 | 32 | 29 | 24 | 33 | 4 / 4 | 6 | NO | 30 | 28 | yes |
| 56 | 8 | 8 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 57 | 8 | 8 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 58 | 8 | 8 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 59 | 8 | 8 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |
| 60 | 8 | 8 (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |

**Reading.**  21 of the 56 values n = 5..60 pack below m; the count slack m^2 - 3 - n is >= 2 on every one of them (min at n = 11) and the count closes for none.  X_forced exceeds the trivial 4 (ONE-TILTED) only at n = none (proven staircase) / none (record staircase): elsewhere the band and the core alone have room for n.  The flat-core ring variant (every non-ring square flat and inside the core, every ring member a wall toucher) needs p >= n - (m-3)^2 members against 4(m-1) toucher slots: it closes only at n = 41, 54, 55 (n > m^2 - 2m + 5), under hypotheses no stability argument supplies (rattlers tilt; ring members hover).

