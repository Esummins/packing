# A102 -- the rigidity drain: contact-torque test on the K0-BLOCKED corpus

*Opus chore, 2026-09-05. Code `code/rigid102.py` (+ `code/report102.py`); results
`results/rigid102{,_bar1e-06}.{json,jsonl}`; logs `logs/`. One process, BLAS pinned,
pure geometry, no LP; whole corpus at both meet bars in ~12 min.*

## T3 -- the empirical rule

**The rule the brief guessed is FALSE, and the true one is a dichotomy about ROOM, not about first-order freedom:** *in this corpus a second meeter either retracts entirely out of its corner cell under one rigid-body motion (10 of the 12 strictly K0-BLOCKED packings, retraction fraction 1.000, and the K0-FREE snap then gives k >= 2 at the same side -- k = 7 for both packings below side 4) or it barely moves at all (the two exceptions retract 0.22 and 0.022 of their depth, Trump 0.000); nothing in between.*

Specifically:

* **"every floor-depth (d2 <= 1e-2) second meeter is FREE-ROT or FREE-TRANS" is false**: of the 31 floor-depth second meeters, 21 are PINNED (all torques about the centre opposed AND the normal cone the whole plane), and 12 are RIGID for the *full* first-order motion cone (no rotation about any point, no translation).
* **first-order freedom does not predict the drain either.** Both non-draining packings have screw-free second meeters; their motions are stopped after 1e-4 deg by a square whose gap is just ABOVE the 1e-7 contact bar (1.4e-6 and 3.1e-5), i.e. by a near-contact that the contact set does not see. The obstruction to a theorem is exactly this: the contact set at any fixed tolerance does not determine the finite motion.
* **largest d2 that drained: 1.02e-2** (`floor_1e-02_d1em02_s0076`, TR sq6, a 1.279 deg rotation about its own centre, then 11 simultaneous snaps to k = 5). The deepest second meeters in the corpus (0.155 Trump TL, 0.206 anchored0 TL) do not move at all.
* **both sub-4 packings drain to k = 7 at the same side** (3.98548 `record_s0115`, 3.99075 `floor_1e-03`); at the 1e-6 census bar the record is not K0-BLOCKED at all (TR/TL are 1.6e-8 / 7.0e-9 nicks) and the second meeters of its two genuinely crowded corners (BL sq0 at 0.0147, BR sq3 at 0.0145) are first-order RIGID, so it does not drain there -- the record's drain is a tangency-scale motion, degen87's observation, not a floor-depth one.
* **the pins are square-square, not wall-square**: of the PINNED second meeters, 32 two_or_more_squares, 1 wall+one_square.
* **canary**: Trump's TL crowd {4, 6} at depth 0.155 / 0.168 is first-order RIGID, retraction 0.000, zero moves, k stays 5. **PASS.**

```
{
 "second_meeters": 49,
 "class_census": {
  "deep/FREE-ROT": 4,
  "deep/FREE-TRANS": 2,
  "deep/PINNED": 12,
  "floor/FREE-ROT": 7,
  "floor/FREE-TRANS": 3,
  "floor/PINNED": 21
 },
 "second_meeters_first_order_rigid": 23,
 "pin_kinds": {
  "two_or_more_squares": 32,
  "wall+one_square": 1
 },
 "packings_drained_bar1e-9": 10,
 "packings_drained_bar1e-6": 9,
 "not_drained": [
  "floor_1e-04_d1em04_s0202",
  "polish12_s0380"
 ],
 "sub4_packings": [
  "floor_1e-03_d1em03_s0050",
  "record_s0115"
 ],
 "sub4_drained": [
  "floor_1e-03_d1em03_s0050",
  "record_s0115"
 ],
 "max_depth_retraction_of_a_second_meeter": {
  "floor_1e-02_d1em02_s0076": 1.0,
  "floor_1e-03_d1em03_s0050": 1.0,
  "floor_1e-04_d1em04_s0202": 0.021961,
  "floor_1e-06_d1em06_s0021": 1.0,
  "record_s0115": 1.0,
  "polish12_s0380": 0.220815,
  "polish15_s0076": 1.0,
  "polish21_s0380": 1.0,
  "polish24_s0259": 1.0,
  "anchored0_p140": 1.0,
  "anchored1_p094": 1.0,
  "anchored2_p094": 1.0,
  "TRUMP_canary": 0.0
 }
}
```

## T2 -- the drain, meet bar 1e-9 (exact: any intrusion is a meeting)

| packing | side | n_meet BL/BR/TR/TL | d2 per corner | moves | final k | class (Young) | drained |
|---|---|---|---|---|---|---|---|
| `floor_1e-02_d1em02_s0076` | 4.0004572 | 2/2/2/2 | 0.01 0.016 0.01 0.01 | TR sq6 rot_centre | 5 | TR[3, 1, 1] | YES |
| `floor_1e-03_d1em03_s0050` | 3.9907485 | 2/2/2/2 | 0.077 0.001 0.001 0.0099 | BR sq3 rot_centre | 7 | BR[3, 1] + TR[3] | YES |
| `floor_1e-04_d1em04_s0202` | 4.0000044 | 2/2/2/2 | 0.0021 0.00013 0.00013 0.062 | - | 0 | empty | no |
| `floor_1e-06_d1em06_s0021` | 4.0000000 | 2/2/2/2 | 2e-06 0.05 0.00012 3.4e-05 | TL sq4 translate | 5 | BL[1, 1] + TL[3] | YES |
| `record_s0115` | 3.9854837 | 2/2/2/2 | 0.015 0.015 1.6e-08 7e-09 | TR sq6 rot_centre_nearest | 7 | TR[1, 1, 1] + TL[2, 1, 1] | YES |
| `polish12_s0380` | 4.0000001 | 2/2/2/2 | 4.6e-07 2e-05 6.6e-06 3e-05 | - | 0 | empty | no |
| `polish15_s0076` | 4.0000041 | 2/2/2/2 | 0.0001 0.0001 0.051 0.0019 | BL sq1 translate | 5 | BL[1, 1, 1] + BR[2] | YES |
| `polish21_s0380` | 4.0000075 | 2/2/2/2 | 0.0001 0.00011 0.0001 0.0001 | TR sq7 rot_centre | 5 | BR[1, 1] + TR[3] | YES |
| `polish24_s0259` | 4.0000119 | 2/2/2/2 | 0.078 0.0034 9.1e-05 9.1e-05 | TR sq6 rot_pivot; TL sq5 rot_pivot | 2 | BR[1, 1] | YES |
| `anchored0_p140` | 4.1071074 | 2/2/2/2 | 0.0001 0.0001 0.02 0.21 | BL sq1 rot_screw | 3 | BR[3] | YES |
| `anchored1_p094` | 4.0837355 | 2/2/2/2 | 0.26 0.26 0.0001 0.0001 | TL sq4 rot_screw | 2 | TL[1, 1] | YES |
| `anchored2_p094` | 4.0837359 | 2/2/2/2 | 0.26 0.26 0.0001 0.0001 | TL sq4 rot_screw | 2 | TL[1, 1] | YES |
| `TRUMP_canary` | 3.8770836 | 1/1/1/2 | - - - 0.16 | - | 5 | BL[2, 1] + BR[1] + TR[1] | no |

## T2 -- the drain, meet bar 1e-6 (strict85 / degen87 census bar)

| packing | side | n_meet BL/BR/TR/TL | d2 per corner | moves | final k | class (Young) | drained |
|---|---|---|---|---|---|---|---|
| `floor_1e-02_d1em02_s0076` | 4.0004572 | 2/2/2/2 | 0.01 0.016 0.01 0.01 | TR sq6 rot_centre | 5 | TR[3, 1, 1] | YES |
| `floor_1e-03_d1em03_s0050` | 3.9907485 | 2/2/2/2 | 0.077 0.001 0.001 0.0099 | BR sq3 rot_centre | 7 | BR[3, 1] + TR[3] | YES |
| `floor_1e-04_d1em04_s0202` | 4.0000044 | 2/2/2/2 | 0.0021 0.00013 0.00013 0.062 | - | 0 | empty | no |
| `floor_1e-06_d1em06_s0021` | 4.0000000 | 2/2/2/2 | 2e-06 0.05 0.00012 3.4e-05 | TL sq4 translate | 5 | BL[1, 1] + TL[3] | YES |
| `record_s0115` | 3.9854837 | 2/2/1/1 | 0.015 0.015 - - | - | 0 | empty | no |
| `polish12_s0380` | 4.0000001 | 1/2/2/2 | - 2e-05 6.6e-06 3e-05 | - | 0 | empty | no |
| `polish15_s0076` | 4.0000041 | 2/2/2/2 | 0.0001 0.0001 0.051 0.0019 | BL sq1 translate | 5 | BL[1, 1, 1] + BR[2] | YES |
| `polish21_s0380` | 4.0000075 | 2/2/2/2 | 0.0001 0.00011 0.0001 0.0001 | TR sq7 rot_centre | 5 | BR[1, 1] + TR[3] | YES |
| `polish24_s0259` | 4.0000119 | 2/2/2/2 | 0.078 0.0034 9.1e-05 9.1e-05 | TR sq6 rot_pivot; TL sq5 rot_pivot | 2 | BR[1, 1] | YES |
| `anchored0_p140` | 4.1071074 | 2/2/2/2 | 0.0001 0.0001 0.02 0.21 | BL sq1 rot_screw | 3 | BR[3] | YES |
| `anchored1_p094` | 4.0837355 | 2/2/2/2 | 0.26 0.26 0.0001 0.0001 | TL sq4 rot_screw | 2 | TL[1, 1] | YES |
| `anchored2_p094` | 4.0837359 | 2/2/2/2 | 0.26 0.26 0.0001 0.0001 | TL sq4 rot_screw | 2 | TL[1, 1] | YES |
| `TRUMP_canary` | 3.8770836 | 1/1/1/2 | - - - 0.16 | - | 5 | BL[2, 1] + BR[1] + TR[1] | no |

## T1 -- the rigidity test, per corner, per meeter (meet bar 1e-9)

`class` is the brief's trichotomy from the centre torques / normal cone; `rigid` = the FULL first-order motion cone {(v, w) : v.F_k + w*tau_k >= 0} is {0} (rotation about every point and every translation blocked).

| packing | corner | sq | d | tilt | contacts | class | rigid | pin | best motion | reached | stopped by | frees |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `floor_1e-02_d1em02_s0076` | BL | 0* | 1.01e-02 | 0.5975 | bottom wall+square 1 | FREE-TRANS | screw-free | - | translate | 0.00225 | square 3 |  |
| `floor_1e-02_d1em02_s0076` | BL | 1 | 1.03e-02 | 0.5975 | left wall+square 0+square 10+square 4 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.74e-07 deg | square 0 |  |
| `floor_1e-02_d1em02_s0076` | BR | 3* | 1.60e-02 | 1.4104 | none | FREE-ROT | screw-free | - | translate_screw | 0.0123 | square 9 |  |
| `floor_1e-02_d1em02_s0076` | BR | 2 | 2.73e-01 | 0.1139 | none | FREE-ROT | screw-free | - | rot_centre_nearest | -0.0962 deg | square 3 |  |
| `floor_1e-02_d1em02_s0076` | TR | 6* | 1.02e-02 | 87.4339 | square 5+square 7+top wall | FREE-ROT | screw-free | - | rot_centre | 1.28 deg | square 10 | YES |
| `floor_1e-02_d1em02_s0076` | TR | 7 | 7.28e-01 | 90.0000 | right wall+square 6 | FREE-TRANS | screw-free | - | translate | 2.26e-06 | square 8 |  |
| `floor_1e-02_d1em02_s0076` | TL | 4* | 1.02e-02 | 89.3922 | left wall+square 1+square 10+square 5 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 5.74e-07 deg | square 10 |  |
| `floor_1e-02_d1em02_s0076` | TL | 5 | 3.28e-02 | 89.3922 | square 10+square 4+square 6+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 5.74e-07 deg | square 4 |  |
| `floor_1e-03_d1em03_s0050` | BL | 1* | 7.67e-02 | 90.0000 | bottom wall+square 0+square 10+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1e-09 deg | free |  |
| `floor_1e-03_d1em03_s0050` | BL | 0 | 1.89e-01 | 16.4149 | left wall+square 1+square 10+square 4 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -7.14e-07 deg | square 10 |  |
| `floor_1e-03_d1em03_s0050` | BR | 3* | 1.02e-03 | 88.6908 | right wall+square 2+square 8 | FREE-ROT | screw-free | - | rot_centre | 1.31 deg | free | YES |
| `floor_1e-03_d1em03_s0050` | BR | 2 | 9.33e-01 | 90.0000 | bottom wall+square 3+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.49e-07 deg | free |  |
| `floor_1e-03_d1em03_s0050` | TR | 6* | 1.02e-03 | 89.9057 | square 5+square 7+square 8+top wall | PINNED | screw-free | two_or_more_squares | rot_screw | 0.0943 deg | free | YES |
| `floor_1e-03_d1em03_s0050` | TR | 7 | 3.79e-01 | 90.0000 | right wall+square 6+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.2e-08 deg | free |  |
| `floor_1e-03_d1em03_s0050` | TL | 5* | 9.88e-03 | 90.0000 | square 4+square 6+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 4e-09 deg | free |  |
| `floor_1e-03_d1em03_s0050` | TL | 4 | 9.03e-02 | 16.4149 | left wall+square 0+square 5 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -7.35e-07 deg | square 5 |  |
| `floor_1e-04_d1em04_s0202` | BL | 0* | 2.13e-03 | 0.1233 | left wall+square 1+square 9 | PINNED | screw-free | two_or_more_squares | rot_screw | 2.92e-05 deg | square 9 |  |
| `floor_1e-04_d1em04_s0202` | BL | 1 | 9.49e-03 | 0.1233 | bottom wall+square 0 | PINNED | screw-free | wall+one_square | rot_screw | -8.14e-05 deg | square 3 |  |
| `floor_1e-04_d1em04_s0202` | BR | 3* | 1.31e-04 | 0.5564 | square 2 | FREE-ROT | screw-free | - | translate | 2.01e-06 | square 1 |  |
| `floor_1e-04_d1em04_s0202` | BR | 2 | 9.68e-01 | 0.5565 | right wall+square 3 | FREE-ROT | screw-free | - | translate | 0.00187 | square 8 |  |
| `floor_1e-04_d1em04_s0202` | TR | 6* | 1.30e-04 | 0.1233 | right wall+square 7+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -7.53e-07 deg | square 8 |  |
| `floor_1e-04_d1em04_s0202` | TR | 7 | 9.36e-01 | 0.1230 | square 6+top wall | PINNED | screw-free | wall+one_square | rot_screw | 0.000246 deg | square 6 |  |
| `floor_1e-04_d1em04_s0202` | TL | 5* | 6.23e-02 | 4.0753 | left wall+square 4 | FREE-TRANS | screw-free | - | rot_pivot | -0.0262 deg | square 0 |  |
| `floor_1e-04_d1em04_s0202` | TL | 4 | 2.36e-01 | 23.6955 | square 5 | FREE-ROT | screw-free | - | translate_screw | 0.000249 | square 10 |  |
| `floor_1e-06_d1em06_s0021` | BL | 1* | 2.00e-06 | 0.0071 | left wall+square 0+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.74e-07 deg | square 9 |  |
| `floor_1e-06_d1em06_s0021` | BL | 0 | 9.84e-01 | 0.0071 | bottom wall+square 1+square 10 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.74e-07 deg | square 1 |  |
| `floor_1e-06_d1em06_s0021` | BR | 3* | 4.97e-02 | 89.9992 | square 2 | FREE-ROT | screw-free | - | translate | 0.0109 | square 8 |  |
| `floor_1e-06_d1em06_s0021` | BR | 2 | 2.25e-01 | 20.6877 | bottom wall+square 3 | FREE-TRANS | screw-free | - | rot_pivot | 0.277 deg | square 10 |  |
| `floor_1e-06_d1em06_s0021` | TR | 6* | 1.23e-04 | 0.0071 | right wall+square 7+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.74e-07 deg | square 8 |  |
| `floor_1e-06_d1em06_s0021` | TR | 7 | 8.18e-03 | 0.0070 | square 6+top wall | PINNED | screw-free | wall+one_square | rot_pivot | -0.00703 deg | free |  |
| `floor_1e-06_d1em06_s0021` | TL | 4* | 3.36e-05 | 0.4406 | none | FREE-ROT | screw-free | - | rot_centre_nearest | -0.00621 deg | square 5 | YES |
| `floor_1e-06_d1em06_s0021` | TL | 5 | 9.63e-01 | 0.4427 | none | FREE-ROT | screw-free | - | translate_screw | 0.00702 | square 4 |  |
| `record_s0115` | BL | 0* | 1.47e-02 | 90.0000 | left wall+square 1+square 10 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 9.71e-07 deg | square 1 |  |
| `record_s0115` | BL | 1 | 2.27e-01 | 71.0666 | square 0+square 2 | PINNED | screw-free | two_or_more_squares | translate_screw | 2.15e-07 | square 9 |  |
| `record_s0115` | BR | 3* | 1.45e-02 | 0.0000 | right wall+square 2+square 6 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -1.15e-07 deg | free |  |
| `record_s0115` | BR | 2 | 9.97e-02 | 71.0666 | bottom wall+square 1+square 3 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 9.85e-07 deg | square 9 |  |
| `record_s0115` | TR | 6* | 1.64e-08 | 0.0000 | square 3+square 7 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -1.86e-06 deg | free | YES |
| `record_s0115` | TR | 7 | 4.06e-01 | 0.0000 | square 6+top wall | PINNED | screw-free | wall+one_square | rot_centre_nearest | -5.25e-07 deg | free |  |
| `record_s0115` | TL | 4* | 7.04e-09 | 0.0059 | square 5+top wall | FREE-TRANS | screw-free | - | rot_centre_nearest | -7.81e-07 deg | square 5 | YES |
| `record_s0115` | TL | 5 | 1.00e+00 | 0.0059 | left wall+square 10+square 4 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -7.76e-07 deg | square 4 |  |
| `polish12_s0380` | BL | 1* | 4.63e-07 | 0.0000 | square 0+square 5 | PINNED | screw-free | two_or_more_squares | translate_screw | 7.38e-07 | left wall |  |
| `polish12_s0380` | BL | 0 | 6.79e-02 | 0.0000 | bottom wall+square 1+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -7.13e-07 deg | square 1 |  |
| `polish12_s0380` | BR | 2* | 1.98e-05 | 89.9798 | right wall+square 10+square 3 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 5.87e-07 deg | square 10 |  |
| `polish12_s0380` | BR | 3 | 9.43e-01 | 89.9798 | bottom wall+square 2+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 5.77e-07 deg | square 2 |  |
| `polish12_s0380` | TR | 7* | 6.56e-06 | 89.9979 | square 6 | FREE-ROT | screw-free | - | translate_screw | 0.000351 | top wall |  |
| `polish12_s0380` | TR | 6 | 8.18e-01 | 89.9979 | right wall+square 7 | PINNED | screw-free | wall+one_square | rot_pivot | 0.00207 deg | free |  |
| `polish12_s0380` | TL | 4* | 2.98e-05 | 90.0000 | square 5+square 8+top wall | PINNED | screw-free | two_or_more_squares | rot_screw | 4.81e-05 deg | free |  |
| `polish12_s0380` | TL | 5 | 3.52e-04 | 89.9798 | left wall+square 1+square 4+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 5.87e-07 deg | square 4 |  |
| `polish15_s0076` | BL | 1* | 1.00e-04 | 0.4671 | left wall+square 0 | FREE-ROT | screw-free | - | translate | 0.000473 | square 4 | YES |
| `polish15_s0076` | BL | 0 | 9.76e-01 | 0.4668 | bottom wall+square 1 | FREE-TRANS | screw-free | - | translate | 4.24e-06 | square 8 |  |
| `polish15_s0076` | BR | 3* | 1.00e-04 | 0.1161 | bottom wall+square 2+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.75e-07 deg | square 8 |  |
| `polish15_s0076` | BR | 2 | 9.48e-01 | 0.1161 | right wall+square 10+square 3 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.74e-07 deg | square 3 |  |
| `polish15_s0076` | TR | 7* | 5.11e-02 | 3.2472 | square 6 | FREE-ROT | screw-free | - | translate | 0.000775 | square 5 |  |
| `polish15_s0076` | TR | 6 | 2.01e-01 | 16.9978 | right wall+square 10+square 7 | PINNED | screw-free | two_or_more_squares | rot_screw | 0.0134 deg | square 10 |  |
| `polish15_s0076` | TL | 5* | 1.94e-03 | 0.1149 | square 4+square 9+top wall | PINNED | screw-free | two_or_more_squares | rot_screw | 0.00125 deg | square 9 |  |
| `polish15_s0076` | TL | 4 | 9.30e-03 | 0.5245 | left wall+square 5 | FREE-TRANS | screw-free | - | rot_pivot | -0.41 deg | square 5 |  |
| `polish21_s0380` | BL | 1* | 1.00e-04 | 0.0062 | left wall+square 0+square 5 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.74e-07 deg | square 0 |  |
| `polish21_s0380` | BL | 0 | 6.89e-02 | 0.0062 | bottom wall+square 1 | PINNED | screw-free | wall+one_square | translate_screw | 6.91e-06 | square 9 |  |
| `polish21_s0380` | BR | 2* | 1.10e-04 | 89.8724 | right wall+square 10 | PINNED | screw-free | wall+one_square | rot_screw | 0.00233 deg | square 3 |  |
| `polish21_s0380` | BR | 3 | 9.41e-01 | 89.8739 | bottom wall+square 9 | FREE-TRANS | screw-free | - | rot_screw | 0.126 deg | free |  |
| `polish21_s0380` | TR | 7* | 1.00e-04 | 89.9683 | square 4+square 6 | FREE-ROT | screw-free | - | rot_centre | 0.0317 deg | free | YES |
| `polish21_s0380` | TR | 6 | 8.18e-01 | 89.9995 | right wall+square 7 | PINNED | screw-free | wall+one_square | rot_pivot | -0.0312 deg | square 7 |  |
| `polish21_s0380` | TL | 5* | 1.00e-04 | 89.9943 | left wall+square 1+square 4+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 5.97e-07 deg | square 4 |  |
| `polish21_s0380` | TL | 4 | 4.45e-04 | 89.9946 | square 5+square 7+square 8+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 5.96e-07 deg | square 5 |  |
| `polish24_s0259` | BL | 1* | 7.85e-02 | 8.4348 | left wall+square 0+square 4 | PINNED | screw-free | two_or_more_squares | rot_screw | 0.823 deg | square 0 |  |
| `polish24_s0259` | BL | 0 | 3.14e-01 | 9.2332 | bottom wall+square 1 | FREE-ROT | screw-free | - | rot_centre | -0.802 deg | square 1 |  |
| `polish24_s0259` | BR | 2* | 3.43e-03 | 88.8947 | right wall+square 10 | FREE-TRANS | screw-free | - | rot_pivot | -0.000829 deg | square 3 |  |
| `polish24_s0259` | BR | 3 | 7.97e-01 | 88.8940 | bottom wall | FREE-ROT | screw-free | - | rot_pivot | 0.0957 deg | square 8 |  |
| `polish24_s0259` | TR | 6* | 9.06e-05 | 89.9945 | square 5+square 7 | PINNED | screw-free | two_or_more_squares | rot_pivot | 0.00554 deg | free | YES |
| `polish24_s0259` | TR | 7 | 6.27e-02 | 89.9953 | right wall+square 10+square 6 | PINNED | screw-free | two_or_more_squares | rot_screw | -0.000936 deg | square 6 |  |
| `polish24_s0259` | TL | 5* | 9.10e-05 | 0.0055 | square 4+square 6 | FREE-TRANS | screw-free | - | rot_pivot | -0.00553 deg | free | YES |
| `polish24_s0259` | TL | 4 | 5.74e-02 | 0.0052 | left wall+square 1+square 5+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -1.01e-05 deg | square 5 |  |
| `anchored0_p140` | BL | 1* | 1.00e-04 | 6.5329 | bottom wall+square 0+square 2 | PINNED | screw-free | two_or_more_squares | rot_screw | -6.53 deg | free | YES |
| `anchored0_p140` | BL | 0 | 2.93e-01 | 45.4846 | left wall+square 1+square 4+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.3e-07 deg | square 9 |  |
| `anchored0_p140` | BR | 2* | 1.00e-04 | 0.0140 | bottom wall+square 1+square 3+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -8.16e-07 deg | square 1 |  |
| `anchored0_p140` | BR | 3 | 5.91e-01 | 0.0000 | right wall+square 2+square 8 | PINNED | screw-free | two_or_more_squares | rot_pivot | -8.25e-06 deg | free |  |
| `anchored0_p140` | TR | 7* | 2.03e-02 | 45.4846 | right wall+square 6+square 8 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.31e-07 deg | square 8 |  |
| `anchored0_p140` | TR | 6 | 4.29e-01 | 45.4846 | square 10+square 7+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.31e-07 deg | square 7 |  |
| `anchored0_p140` | TL | 5* | 2.06e-01 | 64.5145 | square 10+square 4+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.31e-07 deg | square 4 |  |
| `anchored0_p140` | TL | 4 | 2.46e-01 | 64.5145 | left wall+square 0+square 5+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.27e-07 deg | square 5 |  |
| `anchored1_p094` | BL | 1* | 2.57e-01 | 54.7969 | left wall+square 0+square 4 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.03e-06 deg | square 0 |  |
| `anchored1_p094` | BL | 0 | 2.63e-01 | 54.7969 | bottom wall+square 1+square 2+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.07e-06 deg | square 1 |  |
| `anchored1_p094` | BR | 3* | 2.62e-01 | 50.7940 | right wall+square 10+square 2 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.06e-06 deg | square 2 |  |
| `anchored1_p094` | BR | 2 | 2.79e-01 | 50.7940 | bottom wall+square 0+square 3+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.05e-06 deg | square 9 |  |
| `anchored1_p094` | TR | 7* | 1.00e-04 | 50.7940 | square 10+square 6+square 8+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.05e-06 deg | square 10 |  |
| `anchored1_p094` | TR | 6 | 4.56e-01 | 50.7940 | right wall+square 10+square 7 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.06e-06 deg | square 10 |  |
| `anchored1_p094` | TL | 4* | 1.00e-04 | 89.9863 | left wall+square 1+square 5+square 8 | PINNED | screw-free | two_or_more_squares | rot_screw | 0.0116 deg | square 1 | YES |
| `anchored1_p094` | TL | 5 | 5.81e-01 | 90.0000 | square 4+square 8+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.08e-07 deg | free |  |
| `anchored2_p094` | BL | 1* | 2.57e-01 | 54.7969 | left wall+square 0+square 4 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.3e-07 deg | square 0 |  |
| `anchored2_p094` | BL | 0 | 2.63e-01 | 54.7969 | bottom wall+square 1+square 2+square 9 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.37e-07 deg | square 1 |  |
| `anchored2_p094` | BR | 3* | 2.62e-01 | 50.7940 | right wall+square 10+square 2 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.05e-07 deg | square 10 |  |
| `anchored2_p094` | BR | 2 | 2.79e-01 | 50.7940 | bottom wall+square 0+square 3 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.3e-07 deg | square 3 |  |
| `anchored2_p094` | TR | 7* | 1.01e-04 | 50.7940 | square 10+square 6+square 8+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 1.09e-06 deg | square 10 |  |
| `anchored2_p094` | TR | 6 | 4.56e-01 | 50.7940 | right wall+square 10+square 7 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.3e-07 deg | square 10 |  |
| `anchored2_p094` | TL | 4* | 1.00e-04 | 89.9862 | left wall+square 1+square 5 | FREE-ROT | screw-free | - | rot_screw | 0.0138 deg | free | YES |
| `anchored2_p094` | TL | 5 | 5.81e-01 | 90.0000 | square 4+square 8+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | 6.3e-07 deg | square 4 |  |
| `TRUMP_canary` | TL | 4* | 1.55e-01 | 0.0000 | left wall+square 6+square 7 | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -0 deg | free |  |
| `TRUMP_canary` | TL | 6 | 1.68e-01 | 40.1819 | square 4+square 9+top wall | PINNED | RIGID | two_or_more_squares | rot_centre_nearest | -5.73e-07 deg | square 9 |  |

## The residue: PINNED second meeters of the packings that do not drain

### `floor_1e-04_d1em04_s0202` (side 4.000004388)

* **BL sq0**, depth 2.129e-03, tilt 0.1233 deg, PINNED, two_or_more_squares
  * square 1 at (1.002149, 1.000023), edge normal (force on Q) (-0.0022, +1.0000), gap 2.297e-10, torque about centre +0.50000
  * square 1 at (0.990486, 0.999998), edge normal (force on Q) (-0.0022, +1.0000), gap 2.297e-10, torque about centre +0.48834
  * square 9 at (0.999998, 2.000020), edge normal (force on Q) (-1.0000, -0.0022), gap 1.75e-09, torque about centre +0.50000
  * left wall at (0.000000, 1.997869), edge normal (force on Q) (+1.0000, +0.0000), gap 1e-09, torque about centre -0.49892
* **BR sq3**, depth 1.308e-04, tilt 0.5564 deg, FREE-ROT, -
  * square 2 at (2.990425, 1.013199), edge normal (force on Q) (-1.0000, -0.0097), gap 3.303e-08, torque about centre +0.50000
* **TR sq6**, depth 1.300e-04, tilt 0.1233 deg, PINNED, two_or_more_squares
  * square 7 at (3.938505, 3.000007), edge normal (force on Q) (+0.0022, -1.0000), gap 1.593e-09, torque about centre -0.44065
  * square 8 at (3.000007, 1.997985), edge normal (force on Q) (+1.0000, +0.0022), gap 1.559e-09, torque about centre +0.50000
  * square 8 at (2.999951, 2.024077), edge normal (force on Q) (+1.0000, +0.0022), gap 1.559e-09, torque about centre +0.47391
  * right wall at (4.000004, 2.000137), edge normal (force on Q) (-1.0000, +0.0000), gap 1e-09, torque about centre -0.49892
* **TL sq5**, depth 6.233e-02, tilt 4.0753 deg, FREE-TRANS, -
  * square 4 at (0.997472, 3.066592), edge normal (force on Q) (-0.9157, -0.4019), gap 1.891e-09, torque about centre +0.30308
  * left wall at (0.000000, 2.995525), edge normal (force on Q) (+1.0000, +0.0000), gap 1.094e-09, torque about centre -0.46320

### `polish12_s0380` (side 4.000000120)

* **BL sq1**, depth 4.633e-07, tilt 0.0000 deg, PINNED, two_or_more_squares
  * square 0 at (1.000001, 1.000000), edge normal (force on Q) (-0.0000, +1.0000), gap 3.786e-10, torque about centre +0.50000
  * square 0 at (0.932111, 1.000000), edge normal (force on Q) (-0.0000, +1.0000), gap 3.786e-10, torque about centre +0.43211
  * square 5 at (1.000000, 2.000000), edge normal (force on Q) (+0.0000, -1.0000), gap 3.938e-09, torque about centre -0.50000
* **BR sq2**, depth 1.979e-05, tilt 89.9798 deg, PINNED, two_or_more_squares
  * square 3 at (2.999648, 1.000332), edge normal (force on Q) (+0.0004, +1.0000), gap 3.449e-11, torque about centre -0.50000
  * square 3 at (3.943556, 1.000000), edge normal (force on Q) (+0.0004, +1.0000), gap 3.449e-11, torque about centre +0.44391
  * square 10 at (3.000000, 2.000332), edge normal (force on Q) (+1.0000, -0.0004), gap 1.194e-10, torque about centre -0.50000
  * square 10 at (2.999935, 1.816461), edge normal (force on Q) (+1.0000, -0.0004), gap 1.194e-10, torque about centre -0.31613
  * right wall at (4.000000, 1.999980), edge normal (force on Q) (-1.0000, +0.0000), gap 1.196e-09, torque about centre +0.49982
* **TR sq7**, depth 6.561e-06, tilt 89.9979 deg, FREE-ROT, -
  * square 6 at (3.000000, 3.817687), edge normal (force on Q) (-1.0000, +0.0000), gap 5.743e-08, torque about centre +0.31807
* **TL sq4**, depth 2.981e-05, tilt 90.0000 deg, PINNED, two_or_more_squares
  * square 5 at (0.999970, 3.000000), edge normal (force on Q) (+0.0004, +1.0000), gap 1.194e-10, torque about centre -0.49982
  * square 8 at (1.000352, 3.000000), edge normal (force on Q) (+0.0000, +1.0000), gap 4.439e-09, torque about centre -0.49962
  * top wall at (0.999971, 4.000000), edge normal (force on Q) (+0.0000, -1.0000), gap 1e-09, torque about centre +0.50000

### The canary

Trump: TL crowd {4, 6}, both PINNED by two or more squares, every tested motion blocked, 0 moves, k stays 5 (`trump5`). **CANARY PASS.**

