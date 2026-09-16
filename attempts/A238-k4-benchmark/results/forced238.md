# A238 — the forced-cell census of the protected tier

`usable` = the one-slot extensions of the class that are ALREADY CLOSED (A56 scoreboard FULL over
[191/50, 969271/250000]).  Theorem FC's forced roles — and with them rule CC, A208's no-room + Lemma POCKET,
A206's Rule NS, A230's Rule EPS and A224's Rule SNAP — exist only at those cells, so this column IS the
geometry toolkit's traction on the class.

| class | k | Trump images | forced cells | USABLE | the usable extensions | the blocked ones |
|---|---|---|---|---|---|---|
| `trump5` | 5 | 0 | 6 | **6** | BL(0,2)→k6_07, BL(1,1)→k6_19, BR(0,1)→k6_21, TR(0,1)→k6_22, TR(1,0)→k6_24, TL(0,0)→k6_23 | — |
| `k4_03` | 4 | 1 | 5 | **3** | BL(1,1)→k5_09, BL(2,0)→k5_02, TL(1,0)→k5_10 | BR(0,0)→k5_11, TR(0,0)→trump5 |
| `k4_05` | 4 | 0 | 5 | **3** | BR(0,1)→k5_15, BR(1,0)→k5_13, TL(1,0)→k5_12 | BL(1,0)→k5_11, TR(0,0)→k5_16 |
| `k4_06` | 4 | 1 | 5 | **3** | TR(0,1)→k5_17, TR(1,0)→k5_14, TL(1,0)→k5_13 | BL(1,0)→trump5, BR(0,0)→k5_16 |
| `k4_08` | 4 | 2 | 7 | **5** | BL(0,2)→k5_03, BL(1,1)→k5_18, BL(2,0)→k5_03, TR(0,1)→k5_19, TR(1,0)→k5_19 | BR(0,0)→trump5, TL(0,0)→trump5 |
| `k4_11` | 4 | 1 | 7 | **5** | BL(0,2)→k5_07, BR(0,1)→k5_15, BR(1,0)→k5_12, TR(0,1)→k5_17, TR(1,0)→k5_20 | BL(1,0)→trump5, TL(0,0)→k5_16 |
| `corners4` | 4 | 0 | 8 | **0** | — | BL(0,1)→k5_16, BL(1,0)→k5_16, BR(0,1)→k5_16, BR(1,0)→k5_16, TR(0,1)→k5_16, TR(1,0)→k5_16, TL(0,1)→k5_16, TL(1,0)→k5_16 |
| `k3_01` | 3 | 1 | 4 | **0** | — | BL(1,0)→k4_03, BR(0,0)→k4_05, TR(0,0)→k4_06, TL(1,0)→k4_04 |
| `k3_02` | 3 | 2 | 6 | **0** | — | BL(0,2)→k4_00, BL(1,1)→k4_07, BL(2,0)→k4_00, BR(0,0)→k4_03, TR(0,0)→k4_08, TL(0,0)→k4_03 |
| `k3_03` | 3 | 1 | 6 | **0** | — | BL(0,2)→k4_01, BL(1,0)→k4_03, BR(0,1)→k4_10, BR(1,0)→k4_04, TR(0,0)→k4_11, TL(0,0)→k4_05 |
| `k3_04` | 3 | 2 | 6 | **0** | — | BL(0,2)→k4_02, BL(1,0)→k4_08, BR(0,0)→k4_11, TR(0,1)→k4_12, TR(1,0)→k4_09, TL(0,0)→k4_06 |
| `k3_05` | 3 | 2 | 7 | **0** | — | BL(0,1)→k4_05, BL(1,0)→k4_05, BR(0,1)→k4_11, BR(1,0)→k4_06, TR(0,0)→k4_13, TL(0,1)→k4_06, TL(1,0)→k4_11 |
| `k2_00` | 2 | 2 | 5 | **0** | — | BL(0,2)→k3_00, BL(1,0)→k3_02, BR(0,0)→k3_03, TR(0,0)→k3_04, TL(0,0)→k3_01 |
| `k2_01` | 2 | 4 | 6 | **0** | — | BL(0,1)→k3_01, BL(1,0)→k3_03, BR(0,0)→k3_05, TR(0,0)→k3_05, TL(0,1)→k3_01, TL(1,0)→k3_03 |
| `k2_02` | 2 | 4 | 6 | **0** | — | BL(0,1)→k3_04, BL(1,0)→k3_04, BR(0,0)→k3_05, TR(0,1)→k3_04, TR(1,0)→k3_04, TL(0,0)→k3_05 |
| `k1_00` | 1 | 6 | 5 | **0** | — | BL(0,1)→k2_00, BL(1,0)→k2_00, BR(0,0)→k2_01, TR(0,0)→k2_02, TL(0,0)→k2_01 |
| k0_00 | - | - | - | - | (KeyError('k0_00')) | |

## The reading

* **trump5 6/6** — every k6 class is closed, so the toolkit has full traction; that is why A211/A212's
  frontier runs at all.
* **the k4 tier 3–5 usable** — its extensions are the k5 classes, and all but `trump5` (and, for
  `corners4`, `k5_16`) are closed. The four image-bearing k4 classes and `k4_05` therefore get forced
  roles and the geometry bites.
* **`corners4` 0/8** — every one-slot extension is `k5_16`, which is still OPEN. The shadow class has NO
  forced cell, so rule CC / no-room / NS / EPS / SNAP have nothing to act on: the toolkit cannot price it
  until k5_16 closes. (A84 §7.1 reached the same conclusion from the LP side: root τ = 7.25 > 7.)
* **every k ≤ 3 class 0 usable** — their one-slot extensions are the k4 protected classes, which are
  themselves open. The toolkit has no lever on them TODAY, and acquires one the moment the k4 tier closes.

So the geometry price of the protected tier is not flat: it is a **cascade**. Closing k4 hands every k3
class 4–6 forced cells, closing k3 hands k2 its cells, and so on down to k0_00 — the same K1 climb that
A224's Rule SNAP uses inside a single tree, applied to the tier itself.

