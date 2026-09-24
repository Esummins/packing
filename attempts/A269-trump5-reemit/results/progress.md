# A269 progress -- trump5 re-emitted records, window pads (2026-09-24 00:34)

Pads: `window` = pad B, lam = 969271/955000, slab (3.82, s0], records `*_r269b` (delta_pin 9/400);
`tube` = pad A, lam = 969271/958021, slab (3.832084, s0], records `*_r269a` (delta_pin 9/500).
A DEAD at pad B is the full-window statement for its record and implies pad A (HYP_A is inside HYP_B).

| pad | records | CLOSED (DEAD) | open start nodes (latest queue: queue269_pass4.txt) | records with open start nodes | runs | CPU-h |
|---|---|---|---|---|---|---|
| window | 149 | 134 | 110 | 10 | 304 | 42.36 |
| tube | 149 | 10 | 0 | 0 | 10 | 0.67 |

STALLED start nodes (never requeued; ALIVE, not a verdict): 3
* `c0_Y0969_r269b window:R.4.1.3.p1.p1.2`
* `c0_Y0970_r269b window:R.4.1.3.p1.p1.1`
* `c0_Y0970_r269b window:R.4.1.3.p1.p1.2`

Crashed runs (requeued, not a pass): 0; finished runs: 314
