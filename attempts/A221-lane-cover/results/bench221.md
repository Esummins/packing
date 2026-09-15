# A221 benchmark -- A189's no-room leaf vs A221's pocket cover

Every row replays a RECORDED no-room node out of an A211 certificate (`code/nodeload221.py`: the node's
own role boxes, pins included) through `noroom221`.  `A189` is what the certificate recorded; `A221` is
this module.  A REGRESSION is a recorded DEAD that A221 does not kill -- the only unsound direction.
Tags: `four` = the four target k=10 nodes (full leaf), `inherit` = the same through Lemma POCKET-INHERIT
(the nearest recorded ancestor's pockets, no container bisection), `deep` = the budget probe of
`results/experiment221.md` s.3b, `closed` = every recorded no-room node of a CLOSED page (verdict
agreement).

| tag | page | run | node | A189 | s | A221 | s | clip | pockets dead | step |
|---|---|---|---|---|---|---|---|---|---|---|
| alive_page | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.1 | DEAD | 2.2s | DEAD | 3.6s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.2 | DEAD | 2.0s | DEAD | 5.1s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 44.7s | - | 1/2 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 40.7s | - | 0/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2 | UNDECIDED | 120.1s | UNDECIDED | 42.5s | - | 0/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.1 | DEAD | 5.4s | DEAD | 8.2s | NOROOM-POCKET | 1/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.2 | DEAD | 1.9s | DEAD | 5.8s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.2 | UNDECIDED | 121.0s | UNDECIDED | 45.8s | - | 1/2 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.2.1 | DEAD | 6.7s | DEAD | 10.6s | NOROOM-POCKET | 1/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2 | UNDECIDED | 122.6s | UNDECIDED | 47.0s | - | 1/2 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.1 | DEAD | 11.3s | DEAD | 18.0s | NOROOM-POCKET | 1/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.2 | DEAD | 20.6s | DEAD | 10.1s | NOROOM-POCKET | 1/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.2 | DEAD | 1.8s | DEAD | 4.9s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.2.4 | DEAD | 0.1s | DEAD | 0.5s | - | 0/0 | build |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.1 | UNDECIDED | 121.0s | UNDECIDED | 44.7s | - | 0/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1 | UNDECIDED | 120.3s | UNDECIDED | 43.2s | - | 0/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2 | UNDECIDED | 121.7s | DEAD | 3.9s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.1 | DEAD | 1.5s | DEAD | 3.9s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.2 | DEAD | 1.7s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.2 | UNDECIDED | 122.4s | UNDECIDED | 50.3s | - | 0/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.2.1 | UNDECIDED | 121.7s | DEAD | 13.8s | NOROOM-POCKET | 1/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.2.2 | UNDECIDED | 121.1s | DEAD | 18.3s | NOROOM-POCKET | 1/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.4 | UNDECIDED | 120.3s | UNDECIDED | 40.7s | - | 0/1 | bisect+pockets |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.4.1 | DEAD | 2.0s | DEAD | 4.5s | NOROOM | 0/0 | bisect |
| alive_page | 1_k5_16_interior_Y0402 | zero | R.3.1.4.2 | UNDECIDED | 61.6s | UNDECIDED | 49.1s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.1 | UNDECIDED | 122.3s | UNDECIDED | 57.8s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.2 | UNDECIDED | 122.8s | UNDECIDED | 60.0s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.2 | UNDECIDED | 121.1s | UNDECIDED | 55.7s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.2 | DEAD | 0.0s | DEAD | 3.4s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.4 | UNDECIDED | 123.7s | UNDECIDED | 32.7s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.3.4.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.3.4r1 | DEAD | 0.0s | DEAD | 3.5s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.4.2r1 | DEAD | 1.1s | DEAD | 3.5s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.4.3.1 | UNDECIDED | 122.4s | UNDECIDED | 61.4s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.4.3.2 | DEAD | 0.0s | DEAD | 4.1s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.4.3.4 | UNDECIDED | 122.4s | UNDECIDED | 36.9s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.4.3.4.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.4.4r1 | DEAD | 0.0s | DEAD | 3.8s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.5.1 | UNDECIDED | 121.4s | UNDECIDED | 28.2s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0460 | g1_p | R.5.4 | DEAD | 0.1s | DEAD | 0.4s | - | 0/0 | build |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.2.3.13 | UNDECIDED | 122.5s | UNDECIDED | 43.4s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.2.3.13.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.2.3.7 | UNDECIDED | 124.4s | UNDECIDED | 39.4s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.2.3.7.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.1.2 | UNDECIDED | 120.1s | UNDECIDED | 50.3s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.1.5 | UNDECIDED | 121.3s | UNDECIDED | 48.4s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.1.5.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.1.9 | UNDECIDED | 122.7s | UNDECIDED | 48.6s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.2.2 | DEAD | 1.3s | DEAD | 4.9s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.2.5 | DEAD | 0.0s | DEAD | 4.4s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.2.9 | DEAD | 0.7s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.3.2 | UNDECIDED | 122.1s | UNDECIDED | 39.2s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.3.5 | UNDECIDED | 121.9s | UNDECIDED | 39.7s | - | 0/1 | bisect+pockets |
| closed | 1_k5_16_interior_Y0500 | g1_p | R.3.3.9 | UNDECIDED | 120.6s | UNDECIDED | 38.0s | - | 0/1 | bisect+pockets |
| deep | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 260.7s | - | 1/2 | bisect+pockets |
| four | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3 | UNDECIDED | 120.7s | UNDECIDED | 48.8s | - | 0/1 | bisect+pockets |
| four | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2 | UNDECIDED | 122.2s | UNDECIDED | 48.9s | - | 0/1 | bisect+pockets |
| four | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 35.2s | - | 1/2 | bisect+pockets |
| four | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 31.8s | - | 0/1 | bisect+pockets |
| inherit | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3 | UNDECIDED | 120.7s | UNDECIDED | 46.6s | - | 0/1 | bisect+pockets |
| inherit | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2 | UNDECIDED | 122.2s | UNDECIDED | 42.5s | - | 0/1 | bisect+pockets |
| inherit | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 59.7s | - | 0/1 | inherited-pockets -> full |

## Summary

* rows: 65; **REGRESSIONS: 0**
* nodes A221 kills that A189 left UNDECIDED: **3** (_16_interior_Y0402 R.3.1.1.1.2, _16_interior_Y0402 R.3.1.2.1, _16_interior_Y0402 R.3.1.2.2)
* speed-up A189 s / A221 s: median **2.5x**, range 0.2x - 31.2x (52 rows)
