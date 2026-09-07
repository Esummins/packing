# A112 T2 -- the four orderings, measured

### region set `s02` (17 regions)

| ordering | nodes | LPs | LP wall (protocol) | LP wall (flat 900 s) | certify wall | total wall | regions killed | certs P/F | free kills (logic+chain) | leaf kills (logic / chain / cert / cap) |
|---|---|---|---|---|---|---|---|---|---|---|
| wastage | 77 | 59 | 2905 s | 7119 s | 1330 s | 5319 s | 9/17 | 12/1 | 8 | 8 / 0 / 12 / 54 |
| stranded | 77 | 60 | 4014 s | 7027 s | 1807 s | 6920 s | 8/17 | 8/5 | 7 | 7 / 0 / 8 / 64 |
| loadpath | 77 | 56 | 2439 s | 6105 s | 631 s | 4094 s | 9/17 | 12/0 | 11 | 11 / 0 / 12 / 48 |
| hybrid | 73 | 55 | 3252 s | 8267 s | 1638 s | 5959 s | 9/17 | 13/3 | 8 | 8 / 0 / 13 / 48 |
| **old tree (A96 model)** | 671 | 671 | 194602 s | 194602 s | — | 194602 s | — | — | 0 | — |

Timeout protocol (PI, 2026-09-06: stage 1 at 240 s, certify anything with eta <= -1e-3 at once, escalate only the knife edge to 900 s): 12609 s of LP against 28518 s under a flat 900 s cap on the same nodes, a factor **2.26**; per node 55 s vs 124 s over 230 LPs.

Pin wastage vs row mass, Spearman per branching node: n = 45, median 0.468, mean 0.414, range [-0.408, 0.884], positive in 84% of nodes.

Head to head over 17 regions (10 of them informative, i.e. not identical for all four orderings): wins hybrid 4.0, stranded 3.0, loadpath 2.0, wastage 1.0.

| region | L | wastage nodes/LPs/wall | stranded nodes/LPs/wall | loadpath nodes/LPs/wall | hybrid nodes/LPs/wall | winner |
|---|---|---|---|---|---|---|
| `k5_11_interior_Y0036_D02_D05` *(T5″ root kill)* | 3 | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | — |
| `k5_11_interior_Y0036_D03_D04` *(T5″ root kill)* | 3 | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | — |
| `k5_11_interior_Y0036_D07_D01` *(T5″ root kill)* | 3 | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | — |
| `k5_11_interior_Y0036_D07_D03` | 3 | 8 / 6 / 101 s (open) | 8 / 7 / 82 s (open) | 8 / 7 / 111 s (open) | 8 / 7 / 153 s (open) | stranded |
| `k5_11_interior_Y0036_D07_D06` | 3 | 8 / 7 / 78 s (open) | 8 / 7 / 108 s (open) | 8 / 7 / 206 s (open) | 8 / 7 / 103 s (open) | wastage |
| `k5_11_interior_Y0041_D02` | 2 | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | — |
| `k5_11_interior_Y0054_D00` | 2 | 8 / 7 / 246 s (open) | 7 / 6 / 668 s (open) | 8 / 7 / 322 s (open) | 8 / 7 / 256 s (open) | stranded |
| `k5_11_interior_Y0084_D03` | 2 | 3 / 2 / 292 s | 3 / 2 / 304 s | 3 / 2 / 295 s | 3 / 2 / 285 s | hybrid |
| `k5_11_interior_Y0101_D02` *(T5″ root kill)* | 2 | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | — |
| `k5_11_interior_Y0108_D07` | 2 | 3 / 2 / 289 s | 8 / 7 / 340 s (open) | 3 / 2 / 289 s | 5 / 4 / 564 s | loadpath |
| `k5_11_interior_Y0186_D00_D00` | 3 | 8 / 7 / 344 s (open) | 8 / 7 / 734 s (open) | 8 / 7 / 332 s (open) | 8 / 7 / 316 s (open) | hybrid |
| `k5_11_interior_Y0276_D05` *(T5″ root kill)* | 2 | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | — |
| `k5_11_interior_Y0738_D00` | 2 | 8 / 7 / 396 s (open) | 7 / 6 / 603 s (open) | 8 / 7 / 353 s (open) | 3 / 2 / 532 s (open) | hybrid |
| `k5_16_interior_Y0083_D02` | 2 | 8 / 7 / 539 s (open) | 5 / 4 / 851 s (open) | 8 / 6 / 162 s (open) | 8 / 7 / 462 s (open) | stranded |
| `k5_16_interior_Y0083_D03` | 2 | 8 / 7 / 269 s (open) | 8 / 7 / 34 s (open) | 8 / 6 / 33 s (open) | 8 / 6 / 252 s (open) | loadpath |
| `k5_16_interior_Y0119_D07` | 2 | 8 / 7 / 351 s (open) | 8 / 7 / 289 s (open) | 8 / 5 / 336 s (open) | 7 / 6 / 329 s (open) | hybrid |
| `k5_16_interior_Y0155_D03` *(T5″ root kill)* | 2 | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | 1 / 0 / 0 s | — |

Canaries: Trump's grain killed in 0 nodes (must be 0); 10 free-kill fires checked by 4000 sampled pose pairs, 0 counterexamples, worst SAT gap -0.006609.

### region set `k0` (6 regions)

| ordering | nodes | LPs | LP wall (protocol) | LP wall (flat 900 s) | certify wall | total wall | regions killed | certs P/F | free kills (logic+chain) | leaf kills (logic / chain / cert / cap) |
|---|---|---|---|---|---|---|---|---|---|---|
| wastage | 28 | 22 | 2854 s | 2352 s | 0 s | 3188 s | 0/6 | 0/0 | 0 | 0 / 0 / 0 / 34 |
| stranded | 18 | 12 | 3856 s | 4344 s | 0 s | 4041 s | 0/6 | 0/0 | 0 | 0 / 0 / 0 / 24 |
| loadpath | 17 | 11 | 3938 s | 4563 s | 0 s | 4108 s | 0/6 | 0/0 | 0 | 0 / 0 / 0 / 23 |
| hybrid | 21 | 15 | 3664 s | 3945 s | 0 s | 3896 s | 0/6 | 0/0 | 0 | 0 / 0 / 0 / 27 |
| **old tree (A96 model)** | 2522 | 2522 | 731390 s | 731390 s | — | 731390 s | — | — | 0 | — |

Timeout protocol (PI, 2026-09-06: stage 1 at 240 s, certify anything with eta <= -1e-3 at once, escalate only the knife edge to 900 s): 14313 s of LP against 15204 s under a flat 900 s cap on the same nodes, a factor **1.06**; per node 239 s vs 253 s over 60 LPs.

Pin wastage vs row mass, Spearman per branching node: n = 34, median 0.425, mean 0.340, range [-0.370, 0.831], positive in 82% of nodes.

Head to head over 6 regions (6 of them informative, i.e. not identical for all four orderings): wins hybrid 3.0, stranded 2.0, loadpath 1.0.

| region | L | wastage nodes/LPs/wall | stranded nodes/LPs/wall | loadpath nodes/LPs/wall | hybrid nodes/LPs/wall | winner |
|---|---|---|---|---|---|---|
| `k0_l1_071` | 1 | 6 / 5 / 304 s (open) | 2 / 1 / 618 s (open) | 2 / 1 / 644 s (open) | 3 / 2 / 599 s (open) | stranded |
| `k0_l1_074` | 1 | 6 / 5 / 414 s (open) | 6 / 5 / 703 s (open) | 6 / 5 / 725 s (open) | 5 / 4 / 588 s (open) | hybrid |
| `k0_l1_088` | 1 | 3 / 2 / 591 s (open) | 3 / 2 / 592 s (open) | 2 / 1 / 615 s (open) | 3 / 2 / 583 s (open) | loadpath |
| `k0_l1_100` | 1 | 6 / 5 / 370 s (open) | 2 / 1 / 586 s (open) | 2 / 1 / 595 s (open) | 5 / 4 / 587 s (open) | stranded |
| `k0_l1_105` | 1 | 4 / 3 / 597 s (open) | 3 / 2 / 752 s (open) | 3 / 2 / 716 s (open) | 3 / 2 / 714 s (open) | hybrid |
| `k0_l1_109` | 1 | 3 / 2 / 578 s (open) | 2 / 1 / 606 s (open) | 2 / 1 / 643 s (open) | 2 / 1 / 593 s (open) | hybrid |

Canaries: Trump's grain killed in 0 nodes (must be 0); 0 free-kill fires checked by 0 sampled pose pairs, 0 counterexamples, worst SAT gap None.
