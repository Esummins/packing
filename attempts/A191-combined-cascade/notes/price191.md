# A191 -- the price of the k0 residue under the combined cascade leaf (Fable lead, 2026-09-10)

Every number here is either MEASURED tonight on l1_104 / l1_153 (`results/report191.json`, [M]) or an
ASSUMPTION listed in section 4 and marked as such.  CPU-h = process-seconds / 3600 at one process per core
(BelowNormal, affinity 0-15; the LP is single-threaded HiGHS + numpy row oracles, so a process is one vCPU);
instance-hours at 16 vCPU-h per instance-hour (the brief's AWS envelope).

## 1. What the measurement is

The S2 layer of `l1_104` = the 64 nodes ALIVE after A183's parent-seeded polygon + lonely clip at nsub 8 / refine 3
(111 before; 47 dead by geometry), each run through the combined leaf at its recorded fixed point: (a) the corner
no-room leaf, (b) the v1-style exact-core + guard-line LP (budget n - m = 8, converges), (c) the windows +
guard-line LP (budget 11, cap 150 s, unconverged), (d) v5 certification of a converged kill.  Then the S3 children of the S2 survivors at the coarse setting (a sample of 15: 6 corner-nearest B0 boxes dead at 4/2, 8 interior children dead by the exact-core LP at budget 7, 1 undecided at cap) plus A183's fine S3 records under alive parents (8 of 8 dead by the same LP), and the canary `l1_153` (1 alive S2 node: alive converged at tau = budget).  What the S3 sample says: with FOUR pinned squares the LP value drops to 6.000 < 7 on every converged node -- 22 of 23 dead -- so the S3 layer is where l1_104 closes, and its price is the number below.

## 2. The S2 table (filled from `report191.py` when the sweep lands)

%%S2_TABLE%%
| l1_104 S2 (64 alive after A183) | DEAD certified | kill candidates (v1 LP below budget, unconverged at cap) | converged ALIVE | geometry s | v1 LP s | windows LP s (diagnostic) | certificate s | wall s mean / max | total CPU-h |
|---|---|---|---|---|---|---|---|---|---|
| 64 | 17 (27 %) | 19 (30 %) | 26 (41 %) | 29 | 162 | 101 | 14 | 305 / 663 | 5.4 |

| l1_104 S3 coarse sample (children of S2 survivors, nsub 4 / refine 2, parent-seeded) | DEAD by geometry | DEAD by LP | kill candidates | clip s | corner leaf s | v1 LP s | windows LP s | cert s | wall s mean / max |
|---|---|---|---|---|---|---|---|---|---|
| 15 | 6 | 8 | 1 | 75 | 25 | 68 | 55 | 3 | 172 / 376 |

## 3. The price

%%PRICE_TABLE%%
**Scenario: deep kill rate = the S3 sample's (0.93); fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**

| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |
|---|---|---|---|---|
| S2 | 64 | 305 | 0.27 | 5.4 |
| S3 | 5432 | 249 | 0.93 | 375.8 |
| S4 | 20279 | 249 | 0.93 | 1402.9 |
| S5 | 151420 | 249 | 0.93 | 10474.6 |
| S6 | 565301 | 249 | 0.93 | 39105.2 |
| S7 | 4.22e+06 | 249 | 0.93 | 2.92e+05 |
| S8 | 1.58e+07 | 249 | 0.93 | 1.09e+06 |
| **total per cell** | | | | **1.43e+06** (8.96e+04 instance-h at 16 vCPU) |

**Scenario: deep kill rate 0.90; fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**

| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |
|---|---|---|---|---|
| S2 | 64 | 305 | 0.27 | 5.4 |
| S3 | 5432 | 249 | 0.93 | 375.8 |
| S4 | 20279 | 249 | 0.90 | 1402.9 |
| S5 | 227130 | 249 | 0.90 | 15711.9 |
| S6 | 1.27e+06 | 249 | 0.90 | 87986.8 |
| S7 | 1.42e+07 | 249 | 0.90 | 9.85e+05 |
| S8 | 7.98e+07 | 249 | 0.90 | 5.52e+06 |
| **total per cell** | | | | **6.61e+06** (4.13e+05 instance-h at 16 vCPU) |

**Scenario: deep kill rate 0.99; fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**

| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |
|---|---|---|---|---|
| S2 | 64 | 305 | 0.27 | 5.4 |
| S3 | 5432 | 249 | 0.93 | 375.8 |
| S4 | 20279 | 249 | 0.99 | 1402.9 |
| S5 | 22713 | 249 | 0.99 | 1571.2 |
| S6 | 12719 | 249 | 0.99 | 879.9 |
| S7 | 14246 | 249 | 0.99 | 985.5 |
| S8 | 7978 | 249 | 0.99 | 551.9 |
| **total per cell** | | | | **5772** (361 instance-h at 16 vCPU) |

**Scenario: deep kill rate 1.00 (the S3 layer closes the cell); fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**

| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |
|---|---|---|---|---|
| S2 | 64 | 305 | 0.27 | 5.4 |
| S3 | 5432 | 249 | 0.93 | 375.8 |
| S4 | 20279 | 249 | 1.00 | 1402.9 |
| S5 | 0 | 249 | 1.00 | 0.0 |
| S6 | 0 | 249 | 1.00 | 0.0 |
| S7 | 0 | 249 | 1.00 | 0.0 |
| S8 | 0 | 249 | 1.00 | 0.0 |
| **total per cell** | | | | **1784** (112 instance-h at 16 vCPU) |

**S2 continuation (not in the rows):** the 19 unconverged S2 kill candidates at a 900 s cap = 4.8 CPU-h; if they die, the S3 layer shrinks by their 3420 children (3,420 in A168's tree under the 19).

**Eleven cells:** multiply the per-cell total by <= 11 (l1_104 is the largest S1 layer of the eleven; the canary l1_153 has 1 alive S2 node against 64, so the true multiplier is well below 11).  The S2 layer alone, all eleven cells at l1_104's size: 60 CPU-h = 4 instance-hours.

## 4. Assumptions (each one a lever the PI can move)

A1. **Kill rates**: the S2 rate is the measured one on l1_104's 64 alive S2 nodes (27 % certified + 30 % candidates); the S3
    rate is the sampled one -- 14 of 15 coarse children (6 by geometry, 8 by the exact-core LP) + 8 of 8 fine records,
    1 undecided at cap, 0 alive; the sample is biased to the root/D0 and root/D1 chains.  A183's fine-setting geometry alone
    gave 10 of 47 (21 %) and A184's coarse geometry 3-4 of 64 (5-6 %) -- the difference tonight is the LP with four cores.
    Layers below S3 are ASSUMED to kill at the scenario rate (no measurement below S3 on l1_104); the 1.00 scenario is
    'the S3 layer closes the cell' and its S4 row prices only the undecided residue's children.
A2. **Fan-out**: A168's covers: S1 61 (28 alive), S2 ~4 per alive S1 (111), S3 ~112 per alive S2 (12,446 /
    111); S4..S8 fan-out ASSUMED equal to S3's (the BR partner, TL pair, BL pair windows are the same size as
    the BR window) -- this is the number the price is most sensitive to, and A174's coexistence cut / A178's
    partner-first ordering are the levers on it.
A3. **Per-node cost**: geometry at the coarse setting = A184 E1 (S2 25 s, S3 42 s) and tonight's clip_s; the
    corner leaf = tonight's geo_s; the v1 LP = tonight's v1 lp_s (converged); the windows LP is NOT in the
    price (it does not converge at any cap tried: 300 / 1100 / 1500 s) -- if the PI wants it, every node costs
    >= 1,500 s more with no measured verdict.
A4. **Cells**: eleven k0 cells at l1_104's size (its S1 layer is the largest of the eleven by A168's counts;
    l1_153 has 6 S1 / 1 S2 / 119 S3 -- 100x smaller), so the all-eleven number is an UPPER envelope; the canary's
    own numbers are in the table.
A5. **Closure**: a DEAD node closes its subtree at zero cost (A183.8: the 47 S2 kills closed 5,135 S3 nodes).
A6. **No LP at interior nodes**: the LP has no room at S1/S2 (tau = budget converged on every node tonight),
    so the price runs the LP only at the leaves of the geometry tree; geometry kills are what the layers buy.
