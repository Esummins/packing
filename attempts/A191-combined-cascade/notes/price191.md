# A191 -- the price of the k0 residue under the combined cascade leaf (Fable lead, 2026-09-10)

Every number here is either MEASURED tonight on l1_104 / l1_153 (`results/report191.json`, [M]) or an
ASSUMPTION listed in section 4 and marked as such.  CPU-h = process-seconds / 3600 at one process per core
(BelowNormal, affinity 0-15; the LP is single-threaded HiGHS + numpy row oracles, so a process is one vCPU);
instance-hours at 16 vCPU-h per instance-hour (the brief's AWS envelope).

## 1. What the measurement is

The S2 layer of `l1_104` = the 64 nodes ALIVE after A183's parent-seeded polygon + lonely clip at nsub 8 / refine 3
(111 before; 47 dead by geometry), each run through the combined leaf at its recorded fixed point: (a) the corner
no-room leaf, (b) the v1-style exact-core + guard-line LP (budget n - m = 8, converges), (c) the windows +
guard-line LP (budget 11, cap 150 s, unconverged), (d) v5 certification of a converged kill.  Then the S3 children
of the S2 survivors at the coarse setting (a sample), and the canary `l1_153` (1 alive S2 node).

## 2. The S2 table (filled from `report191.py` when the sweep lands)

%%S2_TABLE%%
| l1_104 S2 (64 alive after A183) | DEAD certified | kill candidates (v1 LP below budget, unconverged at cap) | converged ALIVE | geometry s | v1 LP s | windows LP s (diagnostic) | certificate s | wall s mean / max | total CPU-h |
|---|---|---|---|---|---|---|---|---|---|
| 64 | 17 (27 %) | 19 (30 %) | 26 (41 %) | 29 | 162 | 101 | 14 | 305 / 663 | 5.4 |

| l1_104 S3 coarse sample (children of S2 survivors, nsub 4 / refine 2, parent-seeded) | DEAD by geometry | DEAD by LP | kill candidates | clip s | corner leaf s | v1 LP s | windows LP s | cert s | wall s mean / max |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 60 | 0 | 0 | 0 | 0 | 60 / 60 |

## 3. The price

%%PRICE_TABLE%%
**Scenario: deep kill rate = the S3 sample's (1.00); fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**

| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |
|---|---|---|---|---|
| S2 | 64 | 305 | 0.27 | 5.4 |
| S3 | 5264 | 60 | 1.00 | 87.0 |
| S4 | 0 | 60 | 1.00 | 0.0 |
| S5 | 0 | 60 | 1.00 | 0.0 |
| S6 | 0 | 60 | 1.00 | 0.0 |
| S7 | 0 | 60 | 1.00 | 0.0 |
| S8 | 0 | 60 | 1.00 | 0.0 |
| **total per cell** | | | | **92** (6 instance-h at 16 vCPU) |

**Scenario: deep kill rate 0.90 (what closure at S8 needs); fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**

| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |
|---|---|---|---|---|
| S2 | 64 | 305 | 0.27 | 5.4 |
| S3 | 5264 | 60 | 1.00 | 87.0 |
| S4 | 0 | 60 | 0.90 | 0.0 |
| S5 | 0 | 60 | 0.90 | 0.0 |
| S6 | 0 | 60 | 0.90 | 0.0 |
| S7 | 0 | 60 | 0.90 | 0.0 |
| S8 | 0 | 60 | 0.90 | 0.0 |
| **total per cell** | | | | **92** (6 instance-h at 16 vCPU) |

**Scenario: deep kill rate 0.99; fan-out 112 (first meeter, A168 S3) / 56 (partner, ASSUMED half).**

| layer | nodes entering | CPU-s per node | fraction killed | CPU-h |
|---|---|---|---|---|
| S2 | 64 | 305 | 0.27 | 5.4 |
| S3 | 5264 | 60 | 1.00 | 87.0 |
| S4 | 0 | 60 | 0.99 | 0.0 |
| S5 | 0 | 60 | 0.99 | 0.0 |
| S6 | 0 | 60 | 0.99 | 0.0 |
| S7 | 0 | 60 | 0.99 | 0.0 |
| S8 | 0 | 60 | 0.99 | 0.0 |
| **total per cell** | | | | **92** (6 instance-h at 16 vCPU) |

**Eleven cells:** multiply the per-cell total by <= 11 (l1_104 is the largest S1 layer of the eleven; the canary l1_153 has 1 alive S2 node against 64, so the true multiplier is well below 11).  The S2 layer alone, all eleven cells at l1_104's size: 60 CPU-h = 4 instance-hours.

## 4. Assumptions (each one a lever the PI can move)

A1. **Kill rates**: the S2 rate is the measured one on l1_104's 64 alive S2 nodes; the S3 rate is the measured
    coarse-setting rate on the sample (children of S2 survivors) -- A183's fine-setting S3 sample gave 10 of 47
    DEAD (21 %), A184 E1 gave 3-4 of 64 (5-6 %) on a different sample.  Deeper layers (S4..S8) are ASSUMED to kill
    at the S3 rate per node (no measurement below S3 on l1_104; l1_153's S4..S8 is A183's untouched 571).
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
