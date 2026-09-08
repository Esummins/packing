# A151 T2 — the growth ladder (one knob at a time from the certified symmetric (0.2, 10 deg) base)

`DEAD` = the selection tree closed every leaf AND the sampling check found 0 hits; `CAPPED` = the wall cap fired (a compute limit, NOT a geometric one — no claim is made from it); `LIVE-LOW` = a real partial packing of L u P at side <= s0 was found.

| job | square | axis | value | verdict | certified min | leaves | witnesses | unresolved | drawn | tested | hits | wall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | f2 | t | 14.0 | **DEAD** | 3.8770850 | 105354 | 0 | 0 | 2000 | 52 | 0 | 837 s |
| A | f2 | t | 20.0 | **CAPPED** | 3.8770861 | 98366 | 0 | 0 | - | - | - | 900 s |
| A | f2 | x | 0.25 | **CAPPED** | 3.8770849 | 101015 | 0 | 0 | - | - | - | 900 s |
| A | f2 | y | 0.25 | **CAPPED** | 3.8770845 | 104779 | 0 | 0 | - | - | - | 900 s |
| A | BR(0,1) | t | 14.0 | **CAPPED** | 3.8770849 | 87476 | 0 | 0 | - | - | - | 900 s |
| B | f1 | t | 14.0 | **DEAD** | 3.8770843 | 34604 | 0 | 0 | 2000 | 56 | 0 | 282 s |
| B | f1 | t | 20.0 | **DEAD** | 3.8770841 | 37188 | 0 | 0 | 2000 | 60 | 0 | 306 s |
| B | f1 | t | 28.0 | **DEAD** | 3.8770843 | 37104 | 0 | 0 | 2000 | 54 | 0 | 306 s |
| B | f1 | t | 40.0 | **DEAD** | 3.8770841 | 39638 | 0 | 0 | 2000 | 34 | 0 | 374 s |
| B | f1 | x | 0.25 | **DEAD** | 3.8770846 | 44456 | 0 | 0 | 2000 | 37 | 0 | 408 s |
| B | f1 | x | 0.3 | **DEAD** | 3.8770860 | 50374 | 0 | 0 | 2000 | 47 | 0 | 462 s |
| B | f1 | x | 0.4 | **DEAD** | 3.8770864 | 59254 | 0 | 0 | 2000 | 55 | 0 | 507 s |
| B | f1 | y | 0.25 | **DEAD** | 3.8770841 | 72138 | 0 | 0 | 2000 | 53 | 0 | 615 s |
| B | f1 | y | 0.3 | **CAPPED** | 3.8770840 | 90801 | 0 | 0 | - | - | - | 900 s |

**FINAL A** (4439 s): `{"f1": {"x": 0.2, "y": 0.2, "t": 10.0}, "f2": {"x": 0.2, "y": 0.2, "t": 14.0}, "f3": {"x": 0.2, "y": 0.2, "t": 10.0}, "BR(0,1)": {"x": 0.2, "y": 0.2, "t": 10.0}}`

saturated: `{"f2/t": {"first_fail": 20.0, "capped": true, "witnesses": 0, "unresolved": 0}, "f2/x": {"first_fail": 0.25, "capped": true, "witnesses": 0, "unresolved": 0}, "f2/y": {"first_fail": 0.25, "capped": true, "witnesses": 0, "unresolved": 0}, "BR(0,1)/t": {"first_fail": 14.0, "capped": true, "witnesses": 0, "unresolved": 0}, "BR(0,1)/x": "budget", "BR(0,1)/y": "budget"}`

**FINAL B** (4163 s): `{"f1": {"x": 0.4, "y": 0.25, "t": 40.0}, "f2": {"x": 0.2, "y": 0.2, "t": 10.0}, "f3": {"x": 0.2, "y": 0.2, "t": 10.0}, "BR(0,1)": {"x": 0.2, "y": 0.2, "t": 10.0}}`

saturated: `{"f1/y": {"first_fail": 0.3, "capped": true, "witnesses": 0, "unresolved": 0}, "f3/t": "budget", "f3/x": "budget", "f3/y": "budget"}`
