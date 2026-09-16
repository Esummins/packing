# A236 -- the capacity count for n = 5..60 (four-crowds below m = ceil(sqrt n))

Columns: s = record side (survey226; = m where no record below m is known; **proven** where s(n) is a theorem);
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
