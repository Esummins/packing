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

## 3. The price

%%PRICE_TABLE%%

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
