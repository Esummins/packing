# A221 benchmark -- A189's no-room leaf vs A221's pocket cover

Every row replays a RECORDED no-room node out of an A211 certificate (`code/nodeload221.py`: the node's own role
boxes, the five pins included) through `noroom221`.  `A189` is the verdict and seconds the CERTIFICATE recorded;
`A221` is this module on the replayed boxes.  A REGRESSION is a recorded DEAD that A221 does not kill -- the only
unsound direction.

Lanes are tagged; `table221.py` keeps the LAST row per `(tag, page, run, node)`.  The **SHIPPED** configuration is
tags `final` (the full leaf) and `inherit5` (with Lemma POCKET-INHERIT), both at the measured 5 s pocket cap and
with Lemma CN on the surviving pockets; the earlier tags are kept as the record of how the design got there.

**The replayed boxes are not always the boxes A189 saw.**  A node record's `roles` is the page's live dict, so a
certificate can carry boxes TIGHTER than the ones `tree209.noroom_at` was handed at the leaf.  That is why the
`a189ctl` rows exist: they run A189's OWN leaf (`noroom189.noroom`) on exactly the replayed boxes, so a kill A221
reaches and the certificate did not is attributed to the COVER only when the control also fails to kill it.

Tags: `four` = the four target k=10 nodes (full leaf, 45 s pocket cap) | `inherit` / `inherit5` = the same through
Lemma POCKET-INHERIT (the nearest recorded ancestor's pockets, no container bisection) | `alive_page` = every
recorded no-room node of the ALIVE page Y0402 at the 45 s cap | `cap5` = the same with the MEASURED 5 s pocket cap
(before Lemma CN was in this module) | `closed` = every recorded no-room node of the CLOSED pages Y0500 g1 /
Y0460 g1 (verdict agreement) | `final` = all four pages at the shipped settings | `a189ctl` = the control |
`deep` = the budget probe of `results/experiment221.md` s.3b.

| tag | page | run | node | A189 | s | A221 | s | clip | pockets dead | step |
|---|---|---|---|---|---|---|---|---|---|---|
| a189ctl | 1_k5_11_interior_Y0738 | zero | R.1.3.3.2 | UNDECIDED | 122.0s | UNDECIDED | 131.7s | - | 0/0 | a189-control |
| a189ctl | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 130.5s | - | 0/0 | a189-control |
| a189ctl | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2 | UNDECIDED | 121.7s | DEAD | 3.5s | - | 0/0 | a189-control |
| a189ctl | 1_k5_16_interior_Y0402 | zero | R.3.1.2.1 | UNDECIDED | 121.7s | UNDECIDED | 133.0s | - | 0/0 | a189-control |
| a189ctl | 1_k5_16_interior_Y0402 | zero | R.3.1.2.2 | UNDECIDED | 121.1s | UNDECIDED | 132.6s | - | 0/0 | a189-control |
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
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3 | UNDECIDED | 120.7s | UNDECIDED | 13.3s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4 | UNDECIDED | 6.5s | UNDECIDED | 15.2s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1 | UNDECIDED | 1.1s | UNDECIDED | 15.5s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.2.p2 | UNDECIDED | 123.5s | UNDECIDED | 18.7s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.2.p2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.3 | DEAD | 5.9s | UNDECIDED | 14.1s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.4 | UNDECIDED | 7.8s | UNDECIDED | 20.8s | - | 0/2 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.4.p1 | UNDECIDED | 120.2s | UNDECIDED | 14.1s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.4.p2 | DEAD | 1.8s | DEAD | 4.6s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2 | UNDECIDED | 122.2s | UNDECIDED | 18.3s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.5.3 | UNDECIDED | 122.7s | UNDECIDED | 12.9s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.5.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.5.4 | UNDECIDED | 120.3s | UNDECIDED | 12.9s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.2.5.5 | DEAD | 1.3s | DEAD | 4.9s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.2 | UNDECIDED | 17.4s | UNDECIDED | 28.3s | - | 0/2 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p1 | UNDECIDED | 120.1s | UNDECIDED | 19.1s | - | 1/2 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p1.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p2 | UNDECIDED | 120.7s | UNDECIDED | 17.1s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.3.2 | UNDECIDED | 122.0s | DEAD | 11.5s | NOROOM-POCKET | 2/2 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.3.3 | UNDECIDED | 122.7s | UNDECIDED | 13.7s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.3.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.4 | UNDECIDED | 10.9s | UNDECIDED | 17.8s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1 | UNDECIDED | 9.3s | UNDECIDED | 18.6s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1.p1.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.1 | DEAD | 2.2s | DEAD | 3.3s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.2 | DEAD | 2.0s | DEAD | 4.3s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 21.5s | - | 1/2 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 16.4s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2 | UNDECIDED | 120.1s | UNDECIDED | 19.3s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.1 | DEAD | 5.4s | DEAD | 6.5s | NOROOM-POCKET | 1/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.2 | DEAD | 1.9s | DEAD | 4.6s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2 | UNDECIDED | 121.0s | UNDECIDED | 20.8s | - | 1/2 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.1 | DEAD | 6.7s | DEAD | 9.6s | NOROOM-POCKET | 1/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2 | UNDECIDED | 122.6s | UNDECIDED | 22.2s | - | 1/2 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.1 | DEAD | 11.3s | DEAD | 15.3s | NOROOM-POCKET | 1/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.2 | DEAD | 20.6s | DEAD | 8.6s | NOROOM-POCKET | 1/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.2 | DEAD | 1.8s | DEAD | 4.3s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.2.4 | DEAD | 0.1s | DEAD | 0.4s | - | 0/0 | build |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1 | UNDECIDED | 121.0s | UNDECIDED | 14.7s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1 | UNDECIDED | 120.3s | UNDECIDED | 15.5s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2 | UNDECIDED | 121.7s | DEAD | 3.6s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.1 | DEAD | 1.5s | DEAD | 3.1s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.2 | DEAD | 1.7s | DEAD | 3.8s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.2 | UNDECIDED | 122.4s | UNDECIDED | 20.8s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.2.1 | UNDECIDED | 121.7s | DEAD | 12.1s | NOROOM-POCKET | 1/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.2.2 | UNDECIDED | 121.1s | DEAD | 15.8s | NOROOM-POCKET | 1/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.4 | UNDECIDED | 120.3s | UNDECIDED | 21.3s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.4.1 | DEAD | 2.0s | DEAD | 3.9s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0402 | zero | R.3.1.4.2 | UNDECIDED | 61.6s | UNDECIDED | 17.9s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.1 | UNDECIDED | 122.3s | UNDECIDED | 22.4s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.2 | UNDECIDED | 122.8s | UNDECIDED | 22.1s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.2 | UNDECIDED | 121.1s | UNDECIDED | 20.4s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.2 | DEAD | 0.0s | DEAD | 2.8s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.4 | UNDECIDED | 123.7s | UNDECIDED | 10.7s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.3.4.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.3.4r1 | DEAD | 0.0s | DEAD | 3.1s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.4.2r1 | DEAD | 1.1s | DEAD | 2.9s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.4.3.1 | UNDECIDED | 122.4s | UNDECIDED | 20.6s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.4.3.2 | DEAD | 0.0s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.4.3.4 | UNDECIDED | 122.4s | UNDECIDED | 10.7s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.4.3.4.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.4.4r1 | DEAD | 0.0s | DEAD | 4.0s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.5.1 | UNDECIDED | 121.4s | UNDECIDED | 13.3s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0460 | g1_p | R.5.4 | DEAD | 0.1s | DEAD | 0.4s | - | 0/0 | build |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.2.3.13 | UNDECIDED | 122.5s | UNDECIDED | 11.8s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.2.3.13.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.2.3.7 | UNDECIDED | 124.4s | UNDECIDED | 12.4s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.2.3.7.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.1.2 | UNDECIDED | 120.1s | UNDECIDED | 25.2s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.1.5 | UNDECIDED | 121.3s | UNDECIDED | 25.3s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.1.5.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.1.9 | UNDECIDED | 122.7s | UNDECIDED | 24.6s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.2.2 | DEAD | 1.3s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.2.5 | DEAD | 0.0s | DEAD | 3.9s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.2.9 | DEAD | 0.7s | DEAD | 3.7s | NOROOM | 0/0 | bisect |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.3.2 | UNDECIDED | 122.1s | UNDECIDED | 12.1s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.3.5 | UNDECIDED | 121.9s | UNDECIDED | 11.7s | - | 0/1 | bisect+pockets |
| cap5 | 1_k5_16_interior_Y0500 | g1_p | R.3.3.9 | UNDECIDED | 120.6s | UNDECIDED | 11.1s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3 | UNDECIDED | 120.7s | UNDECIDED | 14.5s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4 | UNDECIDED | 6.5s | UNDECIDED | 16.9s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1 | UNDECIDED | 1.1s | UNDECIDED | 16.0s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.2.p2 | UNDECIDED | 123.5s | UNDECIDED | 19.2s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.2.p2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.3 | DEAD | 5.9s | DEAD | 14.4s | NOROOM-CN | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.4 | UNDECIDED | 7.8s | UNDECIDED | 21.8s | - | 0/2 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.4.p1 | UNDECIDED | 120.2s | UNDECIDED | 14.4s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.4.p2 | DEAD | 1.8s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2 | UNDECIDED | 122.2s | UNDECIDED | 18.7s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.5.3 | UNDECIDED | 122.7s | UNDECIDED | 13.3s | - | 0/1 | bisect+pockets |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.5.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| cap5cn | 1_k5_11_interior_Y0738 | zero | R.1.2.5.4 | UNDECIDED | 120.3s | UNDECIDED | 13.2s | - | 0/1 | bisect+pockets |
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
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3 | UNDECIDED | 120.7s | UNDECIDED | 13.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3.p1.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4 | UNDECIDED | 6.5s | UNDECIDED | 15.3s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1 | UNDECIDED | 1.1s | UNDECIDED | 15.5s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.1.4.p1.p1.2.2.2.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.2.p2 | UNDECIDED | 123.5s | UNDECIDED | 19.3s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.2.p2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.3 | DEAD | 5.9s | DEAD | 10.7s | NOROOM-CN | 0/0 | bisect+cn |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.4 | UNDECIDED | 7.8s | UNDECIDED | 23.8s | - | 0/2 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.4.p1 | UNDECIDED | 120.2s | UNDECIDED | 15.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.4.p2 | DEAD | 1.8s | DEAD | 4.7s | NOROOM | 0/0 | bisect |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2 | UNDECIDED | 122.2s | UNDECIDED | 21.2s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.5.3 | UNDECIDED | 122.7s | UNDECIDED | 14.8s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.5.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.5.4 | UNDECIDED | 120.3s | UNDECIDED | 14.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.2.5.5 | DEAD | 1.3s | DEAD | 4.8s | NOROOM | 0/0 | bisect |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.2 | UNDECIDED | 17.4s | UNDECIDED | 28.0s | - | 0/2 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p1 | UNDECIDED | 120.1s | UNDECIDED | 20.8s | - | 1/2 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p1.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p2 | UNDECIDED | 120.7s | UNDECIDED | 18.9s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.2.p2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.3.2 | UNDECIDED | 122.0s | DEAD | 12.4s | NOROOM-POCKET | 2/2 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.3.3 | UNDECIDED | 122.7s | UNDECIDED | 15.2s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.3.3.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.4 | UNDECIDED | 10.9s | UNDECIDED | 19.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1 | UNDECIDED | 9.3s | UNDECIDED | 19.8s | - | 0/1 | bisect+pockets |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1.p1.1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_11_interior_Y0738 | zero | R.1.3.4.p1.p1.2 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.1 | DEAD | 2.2s | DEAD | 2.8s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.2 | DEAD | 2.0s | DEAD | 4.4s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 22.4s | - | 1/2 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 17.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2 | UNDECIDED | 120.1s | UNDECIDED | 19.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.1 | DEAD | 5.4s | DEAD | 6.8s | NOROOM-POCKET | 1/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.2 | DEAD | 1.9s | DEAD | 4.9s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.2 | UNDECIDED | 121.0s | UNDECIDED | 21.5s | - | 1/2 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.2.1 | DEAD | 6.7s | DEAD | 10.5s | NOROOM-POCKET | 1/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2 | UNDECIDED | 122.6s | UNDECIDED | 24.1s | - | 1/2 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.1 | DEAD | 11.3s | DEAD | 16.7s | NOROOM-POCKET | 1/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.2 | DEAD | 20.6s | DEAD | 9.4s | NOROOM-POCKET | 1/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.2.2 | DEAD | 1.8s | DEAD | 4.7s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.2.4 | DEAD | 0.1s | DEAD | 0.5s | - | 0/0 | build |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.1 | UNDECIDED | 121.0s | UNDECIDED | 15.6s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1 | UNDECIDED | 120.3s | UNDECIDED | 16.6s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2 | UNDECIDED | 121.7s | DEAD | 4.0s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.1 | DEAD | 1.5s | DEAD | 3.7s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.2 | DEAD | 1.7s | DEAD | 4.5s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.2 | UNDECIDED | 122.4s | UNDECIDED | 23.4s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.2.1 | UNDECIDED | 121.7s | DEAD | 12.9s | NOROOM-POCKET | 1/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.2.2 | UNDECIDED | 121.1s | DEAD | 16.9s | NOROOM-POCKET | 1/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.4 | UNDECIDED | 120.3s | UNDECIDED | 22.6s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.4.1 | DEAD | 2.0s | DEAD | 4.5s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0402 | zero | R.3.1.4.2 | UNDECIDED | 61.6s | UNDECIDED | 20.0s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.1 | UNDECIDED | 122.3s | UNDECIDED | 23.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.1.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.2 | UNDECIDED | 122.8s | UNDECIDED | 24.8s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.1.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.2 | UNDECIDED | 121.1s | UNDECIDED | 23.2s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.1.2.2.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.2 | DEAD | 0.0s | DEAD | 3.5s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.4 | UNDECIDED | 123.7s | UNDECIDED | 11.6s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.3.4.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0460 | g1_p | R.3.4r1 | DEAD | 0.0s | DEAD | 3.5s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0460 | g1_p | R.4.2r1 | DEAD | 1.1s | DEAD | 3.8s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0460 | g1_p | R.4.3.1 | UNDECIDED | 122.4s | UNDECIDED | 22.4s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.4.3.2 | DEAD | 0.0s | DEAD | 4.5s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0460 | g1_p | R.4.3.4 | UNDECIDED | 122.4s | UNDECIDED | 11.7s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.4.3.4.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0460 | g1_p | R.4.4r1 | DEAD | 0.0s | DEAD | 4.6s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0460 | g1_p | R.5.1 | UNDECIDED | 121.4s | UNDECIDED | 15.4s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0460 | g1_p | R.5.4 | DEAD | 0.1s | DEAD | 0.7s | - | 0/0 | build |
| final | 1_k5_16_interior_Y0500 | g1_p | R.2.3.13 | UNDECIDED | 122.5s | UNDECIDED | 13.0s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0500 | g1_p | R.2.3.13.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0500 | g1_p | R.2.3.7 | UNDECIDED | 124.4s | UNDECIDED | 13.2s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0500 | g1_p | R.2.3.7.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.1.2 | UNDECIDED | 120.1s | UNDECIDED | 27.2s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.1.5 | UNDECIDED | 121.3s | UNDECIDED | 28.0s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.1.5.p1 | VACUOUS | 0.0s | VACUOUS | 0.0s | - | 0/0 | none |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.1.9 | UNDECIDED | 122.7s | UNDECIDED | 28.5s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.2.2 | DEAD | 1.3s | DEAD | 4.6s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.2.5 | DEAD | 0.0s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.2.9 | DEAD | 0.7s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.3.2 | UNDECIDED | 122.1s | UNDECIDED | 13.1s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.3.5 | UNDECIDED | 121.9s | UNDECIDED | 12.9s | - | 0/1 | bisect+pockets |
| final | 1_k5_16_interior_Y0500 | g1_p | R.3.3.9 | UNDECIDED | 120.6s | UNDECIDED | 12.1s | - | 0/1 | bisect+pockets |
| four | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3 | UNDECIDED | 120.7s | UNDECIDED | 48.8s | - | 0/1 | bisect+pockets |
| four | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2 | UNDECIDED | 122.2s | UNDECIDED | 48.9s | - | 0/1 | bisect+pockets |
| four | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 35.2s | - | 1/2 | bisect+pockets |
| four | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 31.8s | - | 0/1 | bisect+pockets |
| inherit | 1_k5_11_interior_Y0738 | zero | R.1.1.3.3 | UNDECIDED | 120.7s | UNDECIDED | 46.6s | - | 0/1 | bisect+pockets |
| inherit | 1_k5_11_interior_Y0738 | zero | R.1.2.5.2 | UNDECIDED | 122.2s | UNDECIDED | 42.5s | - | 0/1 | bisect+pockets |
| inherit | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 59.7s | - | 0/1 | inherited-pockets -> full |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.1 | DEAD | 2.2s | DEAD | 3.2s | NOROOM | 0/0 | bisect |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.1.4.1.1.2 | DEAD | 2.0s | DEAD | 4.2s | NOROOM | 0/0 | bisect |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1 | UNDECIDED | 120.1s | UNDECIDED | 20.9s | - | 1/2 | bisect+pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1 | UNDECIDED | 121.7s | UNDECIDED | 19.5s | - | 0/1 | inherited-pockets -> full |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2 | UNDECIDED | 120.1s | UNDECIDED | 22.6s | - | 0/1 | inherited-pockets -> full |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.1 | DEAD | 5.4s | DEAD | 3.6s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.1.2.2 | DEAD | 1.9s | DEAD | 4.6s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2 | UNDECIDED | 121.0s | UNDECIDED | 23.8s | - | 1/2 | inherited-pockets -> full |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.1 | DEAD | 6.7s | DEAD | 4.0s | NOROOM-POCKET | 2/2 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2 | UNDECIDED | 122.6s | UNDECIDED | 25.2s | - | 1/2 | inherited-pockets -> full |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.1 | DEAD | 11.3s | DEAD | 3.6s | NOROOM-POCKET | 2/2 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.1.2.2.2 | DEAD | 20.6s | DEAD | 4.0s | NOROOM-POCKET | 2/2 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.2 | DEAD | 1.8s | DEAD | 4.3s | NOROOM | 0/0 | bisect |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.2.4 | DEAD | 0.1s | DEAD | 0.4s | - | 0/0 | build |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1 | UNDECIDED | 121.0s | UNDECIDED | 14.8s | - | 0/1 | bisect+pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1 | UNDECIDED | 120.3s | UNDECIDED | 18.1s | - | 0/1 | inherited-pockets -> full |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2 | UNDECIDED | 121.7s | DEAD | 3.1s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.1 | DEAD | 1.5s | DEAD | 3.0s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.1.1.2.2 | DEAD | 1.7s | DEAD | 3.5s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.2 | UNDECIDED | 122.4s | UNDECIDED | 20.1s | - | 0/1 | bisect+pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.2.1 | UNDECIDED | 121.7s | DEAD | 4.3s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.2.2 | UNDECIDED | 121.1s | DEAD | 4.0s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.4 | UNDECIDED | 120.3s | UNDECIDED | 18.8s | - | 0/1 | bisect+pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.4.1 | DEAD | 2.0s | DEAD | 3.7s | NOROOM-POCKET | 1/1 | inherited-pockets |
| inherit5 | 1_k5_16_interior_Y0402 | zero | R.3.1.4.2 | UNDECIDED | 61.6s | UNDECIDED | 20.8s | - | 0/1 | inherited-pockets -> full |

## Summary

* rows: 314 (5 A189 control, 1 budget probe)
* **REGRESSIONS in the SHIPPED configuration (tags `final`/`inherit5`): 0**
* regressions in superseded lanes: 1 (`cap5`) -- all of them `Y0738 R.1.2.3` (k=9, m=2) under the code BEFORE Lemma CN was added to this module; the `final` lane re-runs that page and kills it in 10.7 s by `bisect+cn`

Nodes A221 kills that the certificate left UNDECIDED, with the control's verdict on the SAME boxes:

  * `R.1.3.3.2` -- A189 on the same replayed boxes: **UNDECIDED**  (so this kill is A221's cover)
  * `R.3.1.1.1.2` -- A189 on the same replayed boxes: **DEAD**  (so this one is the tighter replayed boxes, NOT A221)
  * `R.3.1.2.1` -- A189 on the same replayed boxes: **UNDECIDED**  (so this kill is A221's cover)
  * `R.3.1.2.2` -- A189 on the same replayed boxes: **UNDECIDED**  (so this kill is A221's cover)

Wall, per lane (non-vacuous nodes only):

* `alive_page`: 25 nodes, A189 1573 s -> A221 564 s (**2.79x**); slowest A221 node 50.3 s
* `cap5`: 68 nodes, A189 4685 s -> A221 865 s (**5.42x**); slowest A221 node 28.3 s
* `cap5cn`: 11 nodes, A189 753 s -> A221 167 s (**4.52x**); slowest A221 node 21.8 s
* `closed`: 24 nodes, A189 1835 s -> A221 712 s (**2.58x**); slowest A221 node 61.4 s
* **SHIPPED** `final`: 68 nodes, A189 4685 s -> A221 934 s (**5.01x**); slowest A221 node 28.5 s
* `four`: 4 nodes, A189 485 s -> A221 165 s (**2.94x**); slowest A221 node 48.9 s
* `inherit`: 3 nodes, A189 365 s -> A221 149 s (**2.45x**); slowest A221 node 59.7 s
* **SHIPPED** `inherit5`: 25 nodes, A189 1573 s -> A221 258 s (**6.09x**); slowest A221 node 25.2 s
