# Stability radii of the minimum's contacts (A116, PI route)

delta = per-square centre box half-width; rho = kappa * delta (kappa = 100 deg/unit: 0.1 <-> 10 deg) or rho = 0.
forced radius = largest delta at which interval bisection proves the minimum's selection on every disjoint
configuration of the pair's box (rigorous); estimate = tangential slack / drift rate (first order).
Pins: A57 slack cores (half-width 0.00707), side in [3.82, s0 + 0.02].

## S07, kappa = 100.0  -- chain min forced radius 0.024 (limiter f0|BL(0,1)), all contacts 0.008, far pairs 0.224

| pair | chain | type | owner/axis/sign | tau | slack to end | dtheta margin | estimate | forced radius | far radius |
|---|---|---|---|---|---|---|---|---|---|
| f0|f2 | yes | flush | f0/e1/+1 | -0.500 | 1.000 | 0.0 | 0.189 | **0.232** | - |
| f0|f4 | yes | flush | f0/e2/-1 | 0.540 | 0.960 | 0.0 | 0.181 | **0.223** | - |
| f0|BL(0,0) |  | non-contact (gap 0.667) |  |  |  |  |  | - | 0.224 |
| f0|BL(1,0) |  | non-contact (gap 0.236) |  |  |  |  |  | - | 0.224 |
| f0|BL(0,1) | yes | vertex-on-edge | BL(0,1)/e1/+1 | 0.443 | 0.057 | 45.0 | 0.026 | **0.024** | - |
| f0|BR(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f0|TR(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f2|f4 |  | flush | f2/e2/-1 | -0.460 | 0.040 | 0.0 | 0.008 | **0.008** | - |
| f2|BL(0,0) |  | non-contact (gap 1.667) |  |  |  |  |  | - | 0.400 |
| f2|BL(1,0) |  | non-contact (gap 0.960) |  |  |  |  |  | - | 0.400 |
| f2|BL(0,1) |  | non-contact (gap 0.960) |  |  |  |  |  | - | 0.400 |
| f2|BR(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f2|TR(0,0) | yes | vertex-on-edge | f2/e1/+1 | -0.167 | 0.333 | 45.0 | 0.126 | **0.178** | - |
| f4|BL(0,0) |  | non-contact (gap 0.736) |  |  |  |  |  | - | 0.400 |
| f4|BL(1,0) |  | vertex-on-edge | f4/e1/-1 | -0.126 | 0.374 | 45.0 | 0.141 | **0.213** | - |
| f4|BL(0,1) |  | non-contact (gap 0.736) |  |  |  |  |  | - | 0.400 |
| f4|BR(0,0) | yes | vertex-on-edge | f4/e2/-1 | 0.126 | 0.374 | 45.0 | 0.141 | **0.198** | - |
| f4|TR(0,0) |  | non-contact (gap 0.960) |  |  |  |  |  | - | 0.400 |
| BL(0,0)|BL(1,0) |  | flush | BL(0,0)/e1/+1 | -0.500 | 1.000 | 0.0 | 0.448 | **inf** | - |
| BL(0,0)|BL(0,1) |  | flush | BL(0,0)/e2/+1 | 0.500 | 1.000 | 0.0 | 0.448 | **inf** | - |
| BL(0,0)|BR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(0,0)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(1,0)|BL(0,1) |  | flush | BL(1,0)/e1/-1 | -0.500 | 0.000 | 0.0 | 0.000 | **inf** | - |
| BL(1,0)|BR(0,0) |  | non-contact (gap 0.886) |  |  |  |  |  | - | 0.400 |
| BL(1,0)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|BR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BR(0,0)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |

## S07, kappa = 0.0  -- chain min forced radius 0.053 (limiter f0|BL(0,1)), all contacts 0.014, far pairs 0.224

| pair | chain | type | owner/axis/sign | tau | slack to end | dtheta margin | estimate | forced radius | far radius |
|---|---|---|---|---|---|---|---|---|---|
| f0|f2 | yes | flush | f0/e1/+1 | -0.500 | 1.000 | 0.0 | 0.354 | **0.353** | - |
| f0|f4 | yes | flush | f0/e2/-1 | 0.540 | 0.960 | 0.0 | 0.339 | **0.338** | - |
| f0|BL(0,0) |  | non-contact (gap 0.667) |  |  |  |  |  | - | 0.400 |
| f0|BL(1,0) |  | non-contact (gap 0.236) |  |  |  |  |  | - | 0.224 |
| f0|BL(0,1) | yes | vertex-on-edge | BL(0,1)/e1/+1 | 0.443 | 0.057 | 45.0 | 0.057 | **0.053** | - |
| f0|BR(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f0|TR(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f2|f4 |  | flush | f2/e2/-1 | -0.460 | 0.040 | 0.0 | 0.014 | **0.014** | - |
| f2|BL(0,0) |  | non-contact (gap 1.667) |  |  |  |  |  | - | 0.400 |
| f2|BL(1,0) |  | non-contact (gap 0.960) |  |  |  |  |  | - | 0.400 |
| f2|BL(0,1) |  | non-contact (gap 0.960) |  |  |  |  |  | - | 0.400 |
| f2|BR(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f2|TR(0,0) | yes | vertex-on-edge | f2/e1/+1 | -0.167 | 0.333 | 45.0 | 0.236 | **0.210** | - |
| f4|BL(0,0) |  | non-contact (gap 0.736) |  |  |  |  |  | - | 0.400 |
| f4|BL(1,0) |  | vertex-on-edge | f4/e1/-1 | -0.126 | 0.374 | 45.0 | 0.264 | **0.262** | - |
| f4|BL(0,1) |  | non-contact (gap 0.736) |  |  |  |  |  | - | 0.400 |
| f4|BR(0,0) | yes | vertex-on-edge | f4/e2/-1 | 0.126 | 0.374 | 45.0 | 0.264 | **0.254** | - |
| f4|TR(0,0) |  | non-contact (gap 0.960) |  |  |  |  |  | - | 0.400 |
| BL(0,0)|BL(1,0) |  | flush | BL(0,0)/e1/+1 | -0.500 | 1.000 | 0.0 | 1.000 | **inf** | - |
| BL(0,0)|BL(0,1) |  | flush | BL(0,0)/e2/+1 | 0.500 | 1.000 | 0.0 | 1.000 | **inf** | - |
| BL(0,0)|BR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(0,0)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(1,0)|BL(0,1) |  | flush | BL(1,0)/e1/-1 | -0.500 | 0.000 | 0.0 | 0.000 | **inf** | - |
| BL(1,0)|BR(0,0) |  | non-contact (gap 0.886) |  |  |  |  |  | - | 0.400 |
| BL(1,0)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|BR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |
| BR(0,0)|TR(0,0) |  | non-contact (gap 1.886) |  |  |  |  |  | - | 0.400 |

## S02, kappa = 100.0  -- chain min forced radius 0.019 (limiter f1|f3), all contacts 0.019, far pairs 0.156

| pair | chain | type | owner/axis/sign | tau | slack to end | dtheta margin | estimate | forced radius | far radius |
|---|---|---|---|---|---|---|---|---|---|
| f1|f2 | yes | flush | f1/e1/+1 | 0.500 | 1.000 | 0.0 | 0.189 | **0.229** | - |
| f1|f3 | yes | flush | f1/e2/-1 | 0.415 | 0.085 | 0.0 | 0.016 | **0.019** | - |
| f1|BR(0,1) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.190 |
| f1|BL(0,0) |  | non-contact (gap 0.748) |  |  |  |  |  | - | 0.400 |
| f1|BL(0,1) | yes | vertex-on-edge | f1/e1/-1 | 0.088 | 0.412 | 41.6 | 0.156 | **0.231** | - |
| f1|TL(0,0) | yes | vertex-on-edge | f1/e2/+1 | -0.163 | 0.337 | 41.6 | 0.127 | **0.179** | - |
| f1|BL(1,0) |  | non-contact (gap 0.727) |  |  |  |  |  | - | 0.400 |
| f1|BR(0,0) |  | non-contact (gap 1.663) |  |  |  |  |  | - | 0.400 |
| f2|f3 | yes | flush | f2/e2/-1 | -0.585 | 0.915 | 0.0 | 0.173 | **0.215** | - |
| f2|BR(0,1) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.156 |
| f2|BL(0,0) |  | non-contact (gap 1.748) |  |  |  |  |  | - | 0.400 |
| f2|BL(0,1) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f2|TL(0,0) |  | non-contact (gap 0.223) |  |  |  |  |  | - | 0.209 |
| f2|BL(1,0) |  | non-contact (gap 1.475) |  |  |  |  |  | - | 0.400 |
| f2|BR(0,0) |  | non-contact (gap 1.663) |  |  |  |  |  | - | 0.400 |
| f3|BR(0,1) | yes | vertex-on-edge | f3/e2/-1 | -0.163 | 0.337 | 41.6 | 0.064 | **0.083** | - |
| f3|BL(0,0) |  | non-contact (gap 1.663) |  |  |  |  |  | - | 0.400 |
| f3|BL(0,1) |  | non-contact (gap 0.915) |  |  |  |  |  | - | 0.400 |
| f3|TL(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f3|BL(1,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f3|BR(0,0) |  | non-contact (gap 0.748) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BL(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BL(0,1) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|TL(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BL(1,0) |  | non-contact (gap 0.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BR(0,0) | yes | flush | BR(0,1)/e2/-1 | 0.500 | 1.000 | 0.0 | 0.448 | **0.400** | - |
| BL(0,0)|BL(0,1) |  | flush | BL(0,0)/e2/+1 | 0.500 | 1.000 | 0.0 | 0.448 | **inf** | - |
| BL(0,0)|TL(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BL(0,0)|BL(1,0) |  | flush | BL(0,0)/e1/+1 | -0.500 | 1.000 | 0.0 | 0.448 | **inf** | - |
| BL(0,0)|BR(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|TL(0,0) |  | non-contact (gap 0.887) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|BL(1,0) |  | flush | BL(0,1)/e1/+1 | -1.500 | 0.000 | 0.0 | 0.000 | **inf** | - |
| BL(0,1)|BR(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| TL(0,0)|BL(1,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| TL(0,0)|BR(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BL(1,0)|BR(0,0) |  | non-contact (gap 0.887) |  |  |  |  |  | - | 0.400 |

## S02, kappa = 0.0  -- chain min forced radius 0.032 (limiter f1|f3), all contacts 0.032, far pairs 0.210

| pair | chain | type | owner/axis/sign | tau | slack to end | dtheta margin | estimate | forced radius | far radius |
|---|---|---|---|---|---|---|---|---|---|
| f1|f2 | yes | flush | f1/e1/+1 | 0.500 | 1.000 | 0.0 | 0.354 | **0.353** | - |
| f1|f3 | yes | flush | f1/e2/-1 | 0.415 | 0.085 | 0.0 | 0.030 | **0.032** | - |
| f1|BR(0,1) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f1|BL(0,0) |  | non-contact (gap 0.748) |  |  |  |  |  | - | 0.400 |
| f1|BL(0,1) | yes | vertex-on-edge | f1/e1/-1 | 0.088 | 0.412 | 41.6 | 0.292 | **0.297** | - |
| f1|TL(0,0) | yes | vertex-on-edge | f1/e2/+1 | -0.163 | 0.337 | 41.6 | 0.238 | **0.227** | - |
| f1|BL(1,0) |  | non-contact (gap 0.727) |  |  |  |  |  | - | 0.400 |
| f1|BR(0,0) |  | non-contact (gap 1.663) |  |  |  |  |  | - | 0.400 |
| f2|f3 | yes | flush | f2/e2/-1 | -0.585 | 0.915 | 0.0 | 0.324 | **0.324** | - |
| f2|BR(0,1) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.350 |
| f2|BL(0,0) |  | non-contact (gap 1.748) |  |  |  |  |  | - | 0.400 |
| f2|BL(0,1) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f2|TL(0,0) |  | non-contact (gap 0.223) |  |  |  |  |  | - | 0.210 |
| f2|BL(1,0) |  | non-contact (gap 1.475) |  |  |  |  |  | - | 0.400 |
| f2|BR(0,0) |  | non-contact (gap 1.663) |  |  |  |  |  | - | 0.400 |
| f3|BR(0,1) | yes | vertex-on-edge | f3/e2/-1 | -0.163 | 0.337 | 41.6 | 0.119 | **0.128** | - |
| f3|BL(0,0) |  | non-contact (gap 1.663) |  |  |  |  |  | - | 0.400 |
| f3|BL(0,1) |  | non-contact (gap 0.915) |  |  |  |  |  | - | 0.400 |
| f3|TL(0,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f3|BL(1,0) |  | non-contact (gap 1.000) |  |  |  |  |  | - | 0.400 |
| f3|BR(0,0) |  | non-contact (gap 0.748) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BL(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BL(0,1) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|TL(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BL(1,0) |  | non-contact (gap 0.887) |  |  |  |  |  | - | 0.400 |
| BR(0,1)|BR(0,0) | yes | flush | BR(0,1)/e2/-1 | 0.500 | 1.000 | 0.0 | 1.000 | **0.400** | - |
| BL(0,0)|BL(0,1) |  | flush | BL(0,0)/e2/+1 | 0.500 | 1.000 | 0.0 | 1.000 | **inf** | - |
| BL(0,0)|TL(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BL(0,0)|BL(1,0) |  | flush | BL(0,0)/e1/+1 | -0.500 | 1.000 | 0.0 | 1.000 | **inf** | - |
| BL(0,0)|BR(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|TL(0,0) |  | non-contact (gap 0.887) |  |  |  |  |  | - | 0.400 |
| BL(0,1)|BL(1,0) |  | flush | BL(0,1)/e1/+1 | -1.500 | 0.000 | 0.0 | 0.000 | **inf** | - |
| BL(0,1)|BR(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| TL(0,0)|BL(1,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| TL(0,0)|BR(0,0) |  | non-contact (gap 1.887) |  |  |  |  |  | - | 0.400 |
| BL(1,0)|BR(0,0) |  | non-contact (gap 0.887) |  |  |  |  |  | - | 0.400 |
