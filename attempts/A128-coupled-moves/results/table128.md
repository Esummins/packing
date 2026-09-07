# T3 table -- packing x move (A128, results/moves128.jsonl)

Box radius r in every pose coordinate and in the side; certified = exact interval certificate on the box of the stated radius (largest of 1e-3, 3e-4, 1e-4, 1e-5, 1e-6 that certifies); "held" = no certificate at any radius tried (point verdict in brackets: lock103 semantics at r = 0, contact bar 1e-7). Sample = drawn -> tested -> hits for the certified rows.

| packing | side | K0-BLOCKED (point) | corner sq depth | ROT box r [point] | CLUSTER box r, cluster [point] | EXCHANGE at corner | rows sq/wall, mode | sample |
|---|---|---|---|---|---|---|---|---|
| TRUMP_canary | 3.877084 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 10/4 pushed | - |
|  | 0.000000 |  | BL sq1 0 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BL sq3 0 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BR sq2 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -4.4e-16) | 1/4 pushed | - |
|  | 0.000000 |  | BR sq8 0 (tilt 40.18) | - [held] | -  [held] | no (point margin -4.4e-16) | 6/0 pushed | - |
|  | 0.000000 |  | TR sq5 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -3.3e-16) | 1/4 pushed | - |
|  | 0.000000 |  | TR sq9 0 (tilt 40.18) | - [held] | -  [held] | no (point margin -3.3e-16) | 7/0 pushed | - |
|  | 0.000000 |  | TL sq6 0.168 (tilt 40.18) | - [held] | -  [held] | no (point margin -1.0e-02) | 3/1 pushed | - |
|  | 0.000000 |  | TL sq4 0.155 (tilt 0.00) | - [held] | -  [held] | no (point margin -1.0e-02) | 2/2 pushed | - |
| lock_4.000237 | 4.000237 | yes | BL sq0 0.657 (tilt 9.08) | - [held] | -  [unheld [0, 8, 9]] | certified r=0.001 (margin 3.9e-03) | 2/1 pushed | - |
|  | 0.000000 |  | BL sq1 0.0223 (tilt 8.85) | - [held] | -  [held] | certified r=0.001 (margin 3.9e-03) | 2/1 pushed | - |
|  | 0.000000 |  | BR sq2 0.903 (tilt 0.74) | 1e-06 [unheld] | -  [unheld [2, 10]] | certified r=1e-05 (margin 1.2e-05) | 1/1 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | BR sq3 0.00102 (tilt 0.75) | - [unheld] | 1e-06 [3, 8, 9] [unheld [3, 8, 9]] | certified r=1e-05 (margin 1.2e-05) | 2/1 pushed | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq6 0.0882 (tilt 89.94) | - [unheld] | 1e-06 [6, 7, 10] [unheld [6, 10]] | certified r=1e-05 (margin 2.4e-05) | 3/1 pushed | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq7 0.00102 (tilt 89.94) | - [held] | -  [held] | certified r=1e-05 (margin 2.4e-05) | 6/1 pushed | - |
|  | 0.000000 |  | TL sq5 0.119 (tilt 0.07) | - [unheld] | -  [unheld [5, 9]] | no (point margin 5.6e-07) | 3/1 pushed | - |
|  | 0.000000 |  | TL sq4 0.00102 (tilt 0.07) | - [unheld] | -  [held] | no (point margin 5.6e-07) | 6/1 pushed | - |
| lock_4.001525 | 4.001525 | yes | BL sq1 0.103 (tilt 83.30) | - [held] | -  [held] | no (point margin -9.5e-04) | 4/1 pushed | - |
|  | 0.000000 |  | BL sq0 0.0622 (tilt 83.30) | - [held] | -  [held] | no (point margin -9.5e-04) | 3/1 pushed | - |
|  | 0.000000 |  | BR sq2 0.887 (tilt 89.41) | - [held] | -  [held] | certified r=1e-05 (margin 1.5e-04) | 3/1 pushed | - |
|  | 0.000000 |  | BR sq3 0.00102 (tilt 89.41) | - [held] | -  [held] | certified r=1e-05 (margin 1.5e-04) | 4/1 pushed | - |
|  | 0.000000 |  | TR sq6 0.921 (tilt 87.94) | - [held] | -  [held] | no (point margin -1.9e-04) | 3/1 pushed | - |
|  | 0.000000 |  | TR sq7 0.00102 (tilt 87.94) | - [held] | -  [held] | no (point margin -1.9e-04) | 5/1 pushed | - |
|  | 0.000000 |  | TL sq5 0.0441 (tilt 87.29) | - [held] | -  [held] | no (point margin -1.6e-02) | 4/1 pushed | - |
|  | 0.000000 |  | TL sq4 0.0323 (tilt 87.94) | - [held] | -  [held] | no (point margin -1.6e-02) | 3/1 pushed | - |
| K01 | 4.000000 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 10/4 pushed | - |
|  | 0.000000 |  | BL sq1 0 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 12/2 pushed | - |
|  | 0.000000 |  | BL sq3 0 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BR sq7 0.665 (tilt 28.62) | 0.001 [unheld] | 0.001 [7, 8] [unheld [7, 8]] | K0-FREE box | 0/0 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq5 1 (tilt 0.00) | 0.001 [unheld] | -  [held] | K0-FREE box | 0/4 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TL sq4 1 (tilt 0.00) | - [held] | -  [held] | certified r=0.001 (margin 1.4e-02) | 6/4 pushed | - |
|  | 0.000000 |  | TL sq2 0 (tilt 0.00) | - [held] | -  [held] | certified r=0.001 (margin 1.4e-02) | 12/2 pushed | - |
| K02 | 3.942809 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | no (point margin 3.1e-13) | 6/4 pushed | - |
|  | 0.000000 |  | BL sq1 0 (tilt 0.00) | - [held] | -  [held] | no (point margin 3.1e-13) | 8/2 pushed | - |
|  | 0.000000 |  | BR sq2 1 (tilt 0.00) | - [held] | -  [held] | no (point margin 1.5e-14) | 1/4 pushed | - |
|  | 0.000000 |  | BR sq9 0 (tilt 45.00) | - [held] | -  [held] | no (point margin 1.5e-14) | 3/0 pushed | - |
|  | 0.000000 |  | TR sq5 0.801 (tilt 0.00) | - [held] | -  [held] | no (point margin 0.0e+00) | 2/2 pushed | - |
|  | 0.000000 |  | TR sq3 0 (tilt 0.00) | - [held] | -  [held] | no (point margin 0.0e+00) | 3/2 pushed | - |
|  | 0.000000 |  | TL sq7 0.229 (tilt 24.37) | 0.001 [unheld] | 0.001 [6, 7] [unheld [4, 7]] | no (point margin -1.0e-02) | 1/1 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TL sq6 0.0785 (tilt 0.38) | 0.001 [unheld] | -  [held] | no (point margin -1.0e-02) | 0/1 none | 10000 -> 10000 -> 0 |
| K03 | 3.925149 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -7.9e-12) | 6/4 pushed | - |
|  | 0.000000 |  | BL sq1 0 (tilt 0.00) | - [held] | -  [held] | no (point margin -7.9e-12) | 7/2 pushed | - |
|  | 0.000000 |  | BR sq6 0.207 (tilt 90.00) | - [held] | -  [held] | no (point margin -1.5e-09) | 4/2 pushed | - |
|  | 0.000000 |  | BR sq7 5.76e-09 (tilt 90.00) | - [held] | -  [held] | no (point margin -1.5e-09) | 3/2 pushed | - |
|  | 0.000000 |  | TR sq3 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -1.2e-11) | 1/4 pushed | - |
|  | 0.000000 |  | TR sq9 0 (tilt 48.63) | - [held] | -  [held] | no (point margin -1.2e-11) | 4/0 pushed | - |
|  | 0.000000 |  | TL sq2 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -1.2e-11) | 1/4 pushed | - |
|  | 0.000000 |  | TL sq8 0 (tilt 41.37) | - [held] | -  [held] | no (point margin -1.2e-11) | 4/0 pushed | - |
| K04 | 3.914214 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -5.6e-11) | 1/4 pushed | - |
|  | 0.000000 |  | BL sq10 0 (tilt 45.00) | - [held] | -  [held] | no (point margin -5.6e-11) | 4/0 pushed | - |
|  | 0.000000 |  | BR sq1 1 (tilt 0.00) | 0.001 [unheld] | -  [held] | K0-FREE box | 0/4 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq6 1 (tilt 90.00) | - [held] | -  [held] | n/a (3 meeters) | 10/4 pushed | - |
|  | 0.000000 |  | TR sq3 0 (tilt 90.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | TR sq7 0 (tilt 90.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | TL sq8 0.665 (tilt 0.23) | 0.001 [unheld] | -  [held] | K0-FREE box | 0/0 none | 10000 -> 10000 -> 0 |
| K05 | 3.912232 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 10/4 pushed | - |
|  | 0.000000 |  | BL sq1 0 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BL sq6 0 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BR sq2 1 (tilt 0.00) | 0.001 [unheld] | -  [held] | K0-FREE box | 0/4 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq3 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -1.4e-10) | 1/4 pushed | - |
|  | 0.000000 |  | TR sq8 0 (tilt 44.92) | - [held] | -  [held] | no (point margin -1.4e-10) | 4/0 pushed | - |
|  | 0.000000 |  | TL sq5 0.425 (tilt 90.00) | - [held] | -  [held] | no (point margin -8.1e-10) | 2/2 pushed | - |
|  | 0.000000 |  | TL sq9 2.88e-09 (tilt 90.00) | - [held] | -  [held] | no (point margin -8.1e-10) | 3/2 pushed | - |
| K06 | 3.886745 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [unheld [0, 1, 10]] | n/a (3 meeters) | 6/4 pushed | - |
|  | 0.000000 |  | BL sq1 0 (tilt 0.00) | - [held] | -  [unheld [0, 1, 10]] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BL sq7 0 (tilt 90.00) | - [unheld] | -  [unheld [5, 7]] | n/a (3 meeters) | 1/1 none | - |
|  | 0.000000 |  | BR sq6 0.606 (tilt 90.00) | - [unheld] | -  [unheld [2, 6, 9]] | no (point margin -2.1e-13) | 2/2 wedged | - |
|  | 0.000000 |  | BR sq2 0 (tilt 0.00) | - [held] | -  [unheld [2, 6, 9]] | no (point margin -2.1e-13) | 3/2 pushed | - |
|  | 0.000000 |  | TR sq4 1 (tilt 0.00) | - [held] | -  [unheld [4, 9]] | no (point margin -2.3e-07) | 0/4 none | - |
|  | 0.000000 |  | TR sq9 0 (tilt 48.44) | - [unheld] | -  [unheld [2, 9]] | no (point margin -2.3e-07) | 1/0 none | - |
|  | 0.000000 |  | TL sq3 1 (tilt 0.00) | - [unheld] | -  [unheld [3, 10]] | no (point margin -5.6e-07) | 0/4 none | - |
|  | 0.000000 |  | TL sq10 0 (tilt 48.44) | - [unheld] | -  [unheld [0, 1, 10]] | no (point margin -5.6e-07) | 1/0 none | - |
| K20 | 3.924402 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | no (point margin -7.2e-16) | 1/4 pushed | - |
|  | 0.000000 |  | BL sq10 0 (tilt 38.44) | - [held] | -  [held] | no (point margin -7.2e-16) | 5/0 pushed | - |
|  | 0.000000 |  | BR sq4 0.626 (tilt 90.00) | - [held] | -  [held] | no (point margin 1.6e-09) | 2/2 pushed | - |
|  | 0.000000 |  | BR sq6 0 (tilt 90.00) | - [held] | -  [held] | no (point margin 1.6e-09) | 3/2 pushed | - |
|  | 0.000000 |  | TR sq1 1 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 7/4 pushed | - |
|  | 0.000000 |  | TR sq3 0 (tilt 90.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | TR sq9 0 (tilt 38.44) | - [held] | -  [unheld [8, 9]] | n/a (3 meeters) | 3/1 pushed | - |
|  | 0.000000 |  | TL sq5 0.969 (tilt 0.46) | 0.001 [unheld] | -  [held] | K0-FREE box | 0/0 none | 10000 -> 10000 -> 0 |
| K26 | 3.985467 | no | BL sq0 1 (tilt 0.00) | - [held] | -  [held] | no (point margin 9.4e-11) | 6/4 pushed | - |
|  | 0.000000 |  | BL sq1 0 (tilt 0.00) | - [held] | -  [unheld [0, 1, 4]] | no (point margin 9.4e-11) | 7/2 pushed | - |
|  | 0.000000 |  | BR sq5 0.804 (tilt 90.00) | - [held] | -  [held] | no (point margin 2.4e-09) | 2/2 none | - |
|  | 0.000000 |  | BR sq7 0 (tilt 90.00) | - [held] | -  [unheld [5, 7, 10]] | no (point margin 2.4e-09) | 3/2 pushed | - |
|  | 0.000000 |  | TR sq9 0.742 (tilt 69.86) | 0.001 [unheld] | -  [held] | K0-FREE box | 0/0 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TL sq3 0.804 (tilt 90.00) | - [held] | -  [held] | certified r=0.001 (margin 1.3e-02) | 2/2 pushed | - |
|  | 0.000000 |  | TL sq2 0 (tilt 0.00) | - [held] | -  [unheld [2, 4]] | certified r=0.001 (margin 1.3e-02) | 3/2 pushed | - |
| extra_floor1e-3_d1em03_s0050 | 3.990749 | yes | BL sq0 0.189 (tilt 16.41) | - [held] | -  [held] | no (point margin -3.8e-02) | 5/1 pushed | - |
|  | 0.000000 |  | BL sq1 0.0767 (tilt 90.00) | - [held] | -  [held] | no (point margin -3.8e-02) | 4/2 pushed | - |
|  | 0.000000 |  | BR sq2 0.933 (tilt 90.00) | - [held] | -  [held] | certified r=0.001 (margin 4.6e-03) | 3/2 pushed | - |
|  | 0.000000 |  | BR sq3 0.00102 (tilt 88.69) | 0.001 [unheld] | -  [held] | certified r=0.001 (margin 4.6e-03) | 2/1 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq7 0.379 (tilt 90.00) | - [held] | -  [held] | certified r=0.0001 (margin 6.2e-05) | 2/2 pushed | - |
|  | 0.000000 |  | TR sq6 0.00102 (tilt 89.91) | 0.0003 [unheld] | -  [held] | certified r=0.0001 (margin 6.2e-05) | 3/1 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TL sq4 0.0903 (tilt 16.41) | - [held] | -  [held] | no (point margin -4.9e-03) | 3/1 pushed | - |
|  | 0.000000 |  | TL sq5 0.00988 (tilt 90.00) | - [held] | -  [held] | no (point margin -4.9e-03) | 2/2 pushed | - |
| extra_record_s0115 | 3.985484 | yes | BL sq1 0.227 (tilt 71.07) | - [unheld] | -  [unheld [1, 8, 9]] | no (point margin -7.4e-03) | 3/0 none | - |
|  | 0.000000 |  | BL sq0 0.0147 (tilt 90.00) | - [held] | -  [held] | no (point margin -7.4e-03) | 2/2 pushed | - |
|  | 0.000000 |  | BR sq2 0.0997 (tilt 71.07) | - [unheld] | -  [unheld [1, 2]] | no (point margin -7.3e-03) | 3/1 pushed | - |
|  | 0.000000 |  | BR sq3 0.0145 (tilt 0.00) | - [held] | -  [held] | no (point margin -7.3e-03) | 3/2 pushed | - |
|  | 0.000000 |  | TR sq7 0.406 (tilt 0.00) | - [unheld] | -  [held] | no (point margin 8.0e-09) | 2/2 none | - |
|  | 0.000000 |  | TR sq6 1.64e-08 (tilt 0.00) | - [unheld] | -  [unheld [6, 8]] | no (point margin 8.0e-09) | 4/0 pushed | - |
|  | 0.000000 |  | TL sq5 1 (tilt 0.01) | - [held] | -  [unheld [4, 5, 8, 9, 10]] | n/a (3 meeters) | 3/1 pushed | - |
|  | 0.000000 |  | TL sq4 7.04e-09 (tilt 0.01) | 1e-05 [unheld] | -  [unheld [4, 8, 9, 10]] | n/a (3 meeters) | 2/1 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TL sq10 0 (tilt 0.00) | - [unheld] | -  [unheld [8, 9, 10]] | n/a (3 meeters) | 3/0 none | - |
| cell_l1_124 | 3.942810 | no | BL sq10 1 (tilt 90.00) | - [unheld] | -  [held] | no (point margin 6.8e-08) | 1/1 pushed | - |
|  | 0.000000 |  | BL sq8 0 (tilt 45.01) | - [unheld] | -  [unheld [4, 6, 8]] | no (point margin 6.8e-08) | 3/0 pushed | - |
|  | 0.000000 |  | BR sq9 1 (tilt 90.00) | - [held] | -  [held] | n/a (3 meeters) | 2/2 pushed | - |
|  | 0.000000 |  | BR sq5 0 (tilt 90.00) | - [unheld] | -  [unheld [0, 5]] | n/a (3 meeters) | 2/0 none | - |
|  | 0.000000 |  | BR sq7 0 (tilt 0.00) | - [unheld] | -  [unheld [4, 6, 7, 8]] | n/a (3 meeters) | 2/1 none | - |
|  | 0.000000 |  | TR sq2 1 (tilt 90.00) | - [held] | -  [unheld [0, 2]] | no (point margin 3.8e-07) | 1/4 pushed | - |
|  | 0.000000 |  | TR sq0 0 (tilt 44.99) | - [unheld] | -  [unheld [0, 5]] | no (point margin 3.8e-07) | 2/0 none | - |
|  | 0.000000 |  | TL sq3 0.982 (tilt 90.00) | 1e-06 [unheld] | -  [held] | no (point margin 1.5e-08) | 2/1 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TL sq4 0 (tilt 0.00) | - [unheld] | -  [unheld [4, 6]] | no (point margin 1.5e-08) | 6/0 pushed | - |
| cell_l1_148 | 4.000000 | no | BL sq10 0.989 (tilt 90.00) | - [unheld] | -  [unheld [9, 10]] | no (point margin 1.9e-10) | 2/1 none | - |
|  | 0.000000 |  | BL sq8 0 (tilt 90.00) | - [held] | -  [unheld [0, 1, 3, 4, 8]] | no (point margin 1.9e-10) | 3/1 pushed | - |
|  | 0.000000 |  | BR sq5 0.272 (tilt 89.83) | 0.001 [unheld] | -  [held] | no (point margin -1.0e-06) | 1/0 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | BR sq3 0.00225 (tilt 89.82) | 1e-05 [unheld] | -  [unheld [0, 1, 3, 4]] | no (point margin -1.0e-06) | 2/1 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq6 0.93 (tilt 85.66) | 0.0001 [unheld] | -  [held] | no (point margin -1.0e-09) | 0/0 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TR sq0 0 (tilt 89.83) | - [held] | -  [unheld [0, 1, 4]] | no (point margin -1.0e-09) | 4/0 pushed | - |
|  | 0.000000 |  | TL sq2 0.997 (tilt 89.86) | 0.001 [unheld] | 0.0003 [2, 7] [unheld [2, 7]] | certified r=0.001 (margin 8.4e-04) | 0/0 none | 10000 -> 10000 -> 0 |
|  | 0.000000 |  | TL sq7 0 (tilt 26.08) | 0.001 [held] | 0.001 [7, 9] [unheld [0, 1, 4, 7]] | certified r=0.001 (margin 8.4e-04) | 0/0 none | 10000 -> 10000 -> 0 |
| cell_l1_158 | 3.902674 | no | BL sq4 1 (tilt 0.00) | - [held] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BL sq8 9.89e-09 (tilt 90.00) | - [unheld] | -  [held] | n/a (3 meeters) | 3/2 pushed | - |
|  | 0.000000 |  | BL sq6 0 (tilt 90.00) | - [unheld] | -  [held] | n/a (3 meeters) | 7/2 pushed | - |
|  | 0.000000 |  | BR sq3 0.787 (tilt 90.00) | - [unheld] | -  [held] | no (point margin 6.9e-08) | 1/1 none | - |
|  | 0.000000 |  | BR sq2 0 (tilt 90.00) | - [held] | -  [held] | no (point margin 6.9e-08) | 3/1 none | - |
|  | 0.000000 |  | TR sq1 1 (tilt 90.00) | - [held] | -  [held] | no (point margin 7.9e-10) | 1/4 pushed | - |
|  | 0.000000 |  | TR sq0 0 (tilt 46.32) | - [held] | -  [held] | no (point margin 7.9e-10) | 6/0 pushed | - |
|  | 0.000000 |  | TL sq7 0.727 (tilt 22.26) | 0.001 [unheld] | -  [held] | K0-FREE box | 0/0 none | 10000 -> 10000 -> 0 |

## Per-packing summary

| packing | side | K0-BLOCKED | subjects | ROT box >= 1e-3 / any r | CLUSTER box >= 1e-3 / any r | coupled-only | any move >= 1e-3 | EXCHANGE certified corners | K0-FREE corners (box) | held under the whole menu on every box | BOX DEAD at radius | extent bound excludes W | hooks | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRUMP_canary | 3.877084 | no | 9 | 0 / 0 | 0 / 0 | 0 | 0 | 0 | 0 | YES | - {} | no (3.8741) | {'TL': 1} | 9 |
| lock_4.000237 | 4.000237 | yes | 8 | 0 / 1 | 0 / 2 | 2 | 0 | 3 | 0 | no | 0.001 {'BL': '0.001', 'BR': '1e-05', 'TR': '1e-05'} | yes (3.9972) | {} | 15 |
| lock_4.001525 | 4.001525 | yes | 8 | 0 / 0 | 0 / 0 | 0 | 0 | 1 | 0 | YES | 1e-05 {'BR': '1e-05'} | yes (3.9985) | {} | 12 |
| K01 | 4.000000 | no | 7 | 2 / 2 | 1 / 1 | 0 | 2 | 1 | 2 | no | 0.001 {'BR': '0.001', 'TR': '0.001', 'TL': '0.001'} | yes (3.9970) | {} | 7 |
| K02 | 3.942809 | no | 8 | 2 / 2 | 1 / 1 | 0 | 2 | 0 | 0 | no | 0.001 {'TL': '0.001'} | yes (3.9398) | {} | 9 |
| K03 | 3.925149 | no | 8 | 0 / 0 | 0 / 0 | 0 | 0 | 0 | 0 | YES | - {} | yes (3.9221) | {'BR': 2} | 9 |
| K04 | 3.914214 | no | 7 | 2 / 2 | 0 / 0 | 0 | 2 | 0 | 2 | no | 0.001 {'BR': '0.001', 'TL': '0.001'} | yes (3.9112) | {} | 5 |
| K05 | 3.912232 | no | 8 | 1 / 1 | 0 / 0 | 0 | 1 | 0 | 1 | no | 0.001 {'BR': '0.001'} | yes (3.9092) | {'TL': 2} | 6 |
| K06 | 3.886745 | no | 9 | 0 / 0 | 0 / 0 | 0 | 0 | 0 | 0 | YES | - {} | yes (3.8837) | {} | 8 |
| K20 | 3.924402 | no | 8 | 1 / 1 | 0 / 0 | 0 | 1 | 0 | 1 | no | 0.001 {'TL': '0.001'} | yes (3.9214) | {} | 6 |
| K26 | 3.985467 | no | 7 | 1 / 1 | 0 / 0 | 0 | 1 | 1 | 1 | no | 0.001 {'TR': '0.001', 'TL': '0.001'} | yes (3.9825) | {} | 9 |
| extra_floor1e-3_d1em03_s0050 | 3.990749 | yes | 8 | 1 / 2 | 0 / 0 | 0 | 1 | 2 | 0 | no | 0.001 {'BR': '0.001', 'TR': '0.0003'} | yes (3.9877) | {'BL': 1, 'BR': 1, 'TR': 1, 'TL': 1} | 13 |
| extra_record_s0115 | 3.985484 | yes | 9 | 0 / 1 | 0 / 0 | 0 | 0 | 0 | 0 | no | - {} | yes (3.9825) | {'BR': 1} | 9 |
| cell_l1_124 | 3.942810 | no | 9 | 0 / 1 | 0 / 0 | 0 | 0 | 0 | 0 | no | 1e-06 {'TL': '1e-06'} | yes (3.9398) | {} | 9 |
| cell_l1_148 | 4.000000 | no | 8 | 3 / 5 | 1 / 2 | 0 | 3 | 1 | 0 | no | 0.001 {'BR': '0.001', 'TR': '0.0001', 'TL': '0.001'} | yes (3.9970) | {} | 11 |
| cell_l1_158 | 3.902674 | no | 8 | 1 / 1 | 0 / 0 | 0 | 1 | 0 | 1 | no | 0.001 {'TL': '0.001'} | yes (3.8997) | {'BL': 4} | 8 |
