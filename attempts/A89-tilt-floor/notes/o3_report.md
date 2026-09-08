# A89-O3 — shallow-corner root kill certificates for Lemma ID, plus the hole diagnostic (numbers only)

Chore A89-O3 (second Opus compute chore). Everything here is written under
`attempts/A89-tilt-floor/`. The engine is A85's case-LP stack COPIED verbatim into
`attempts/A89-tilt-floor/code/` (26 modules, `class85 tree85 caselp lpbox certify verify_case
alivewitness pinguard blas1 corner85` + their imports, plus `results/witnesses_k0_00.json`);
nothing under A57/A60/A61/A85/A86 was written. New code in this attempt:
`code/o3_holes.py` (diagnostic D), `code/o3fam.py` (the NO-family builder),
`code/o3run.py` (one run), `code/o3_campaign.py` (the ordered campaign).
Log: `logs/o3.log`, `logs/o3_campaign.out`. Runs: `results/o3_runs.jsonl`.

Resource discipline actually used: BLAS pinned to 1 thread (`blas1` imported before numpy in
every entry point), at most one LP process at a time, and `free_commit_mb()`
(MEMORYSTATUSEX.ullAvailPageFile) checked > 6144 MB before every LP and before every
certify/verify launch, with a 60 s sleep-and-recheck loop on a dip.

---

## 0. Constants

| quantity | value |
|---|---|
| s0 | 969271/250000 = 3.877084 |
| window floor m_lo | 3.82 |
| lambda_max = s0/3.82 | 969271/955000 = 1.0149434554 |
| a_win(delta) = (1-delta)/lambda_max | delta 0.3 -> 0.6896932; 0.1 -> 0.8867484; 0.05 -> 0.9360122 |
| a_s0(delta) = 1-delta | 0.7 / 0.9 / 0.95 |
| budget | 11 (no pins, no cores: k0_00 root) |
| wastage budget E(s0) = s0^2 - 11 | 4.031780343056 |
| E(3.82) = 3.82^2 - 11 | 3.5924 |

Area-only check of Lemma ID (no LP): c_sh (1-delta)^2 <= E(m). At s0 four shallow corners
strand 4(1-delta)^2 <= 4 < 4.0318 for every delta >= 0, so **area alone never kills at s0**;
at m = 3.82 it kills 4-shallow only for delta < 0.05226 (4(1-delta)^2 > 3.5924), 3-shallow
never (3 < 3.5924), 2-shallow never. This is why the LP row of section 7 is needed.

---

## 1. The exempt NO-families (`code/o3fam.py`, `results/o3_fams.json`)

`R_c(a) = {(c_Q, theta) : int Q meets the open box (0,a)^2 in c's frame}` is not a box, so the
certificate uses a SOUND INNER union of caselp `NoFam`s (rect x theta-interval) contained in
it. Test used, exact in Fractions: `f(u,v,theta) = min over Q of max(x,y)` is nondecreasing in
u and in v (so the max over a rect is at its outer corner) and (sqrt2/2)-Lipschitz in theta
(so a 257-point theta grid plus the Lipschitz pad bounds the max over a theta bin rigorously).
A family `[0.45, U] x [0.45, V] x [T0, T1]` is accepted iff that rigorous upper bound is < a.
Every rect is anchored BELOW the admissible centre floor 0.5, where caselp's `inside_many`
applies no safety margin and where `verify_case.nofam_exempt`'s containment test is easiest;
only the outer edges U, V pay the EPS_ZONE = 2e-3 erosion. Theta bins have all edges at
multiples of 1/4 deg (so 90 - edge is exact in binary and the family set is bit-exactly
D4-closed) and are widened by 0.5 deg > EPS_TH = 0.3 deg so the ERODED bins still tile [0,90]:
(0,14.75) (13.75,28.75) (27.75,41.75) (40.75,49.25) (48.25,62.25) (61.25,76.25) (75.25,90).

| delta | frame | a | #families per corner | all sound (exact) | min margin a - fmax | coverage of R_BL(a), eroded / raw |
|---|---|---|---|---|---|---|
| 0.3 | window | 0.6896932 | 108 | yes | 2.05e-4 | 89.1 % / 90.0 % |
| 0.3 | s0 only | 0.7 | 108 | yes | 2.4e-4 | 89.4 % / 90.2 % |
| 0.1 | window | 0.8867484 | 112 | yes | 2.0e-4 | 90.9 % / 91.5 % |
| 0.1 | s0 only | 0.9 | 112 | yes | 2.2e-4 | 91.4 % / 92.0 % |
| 0.05 | window | 0.9360122 | 112 | yes | 2.1e-4 | 92.2 % / 92.7 % |
| 0.05 | s0 only | 0.95 | 112 | yes | 2.3e-4 | 92.3 % / 92.9 % |

Coverage is by uniform sampling of (cx, cy, t) over [0.5, 2.7]^2 x [0,1] with the exact
membership test (20 000 samples per row); "eroded" applies caselp's EPS_ZONE / EPS_TH drop
margins, "raw" does not. The residual ~9 % loss is the theta-binning, not the staircase
(going from 6 to 20 staircase steps moves the figure by < 0.2 points).

Window validity: `a_win = (1-delta)/lambda_max` (A63 Lemma B-NO: "occupancy transfers with
the zone contracted 1/lambda"). This is also sound under the centre-dilation reading of
K0-WIDEN, since a_win <= 1-delta and the dilated centre lambda*c is FURTHER from the corner
than c. Runs marked "s0" use a = 1-delta and are valid at s0 only.

## 2. The canary (`results/o3_image_depths.json`)

Exact per-image, per-corner intrusion DEPTH(c) = 1 - min over the 11 placements of f_c, for
all eight D4 images of Trump in `results/witnesses_k0_00.json`:

| image | BL | BR | TL | TR |
|---|---|---|---|---|
| g0 | 1.000000 | 1.000000 | **0.168300** | 1.000000 |
| g1 | 1.000000 | 1.000000 | 1.000000 | **0.168300** |
| g2 | **0.168300** | 1.000000 | 1.000000 | 1.000000 |
| g3 | 1.000000 | **0.168300** | 1.000000 | 1.000000 |
| g4 | 1.000000 | **0.168300** | 1.000000 | 1.000000 |
| g5 | 1.000000 | 1.000000 | 1.000000 | **0.168300** |
| g6 | **0.168300** | 1.000000 | 1.000000 | 1.000000 |
| g7 | 1.000000 | 1.000000 | **0.168300** | 1.000000 |

Every image has EXACTLY ONE corner of depth 0.168300 (Trump's TL crowd: sq4 at depth 0.1555
and sq6 at 0.1683, so DEPTH = 0.1683, matching the doc's 0.168) and THREE corners of depth
exactly 1.000000 (the slot squares). Consequences, all confirmed by the engine's
`images_realizing` gate:

* **1-SHALLOW(BL) at delta >= 0.1683 is image-realisable** (images g2 and g6) — the engine
  must and does REFUSE. Observed: `R4_1shallow_BL_d0.3 -> REFUSED (CANARY: realised by g2,g6)`,
  no LP run. **CANARY PASS.**
* **Every 2-, 3- and 4-SHALLOW pattern is NOT image-realisable**, because a pattern with >= 2
  corners always contains a corner of depth 1 for every image, and the depth-1 slot pose
  (0.5, 0.5, 0 deg) lies inside a family of the delta = 0.3 set. So those nodes are
  attemptable, exactly as the brief predicted.
* 1-SHALLOW at delta < 0.1683 is not image-realisable and would be attemptable.

---

## A. The runs (`results/o3_runs.jsonl`, `certs/k0_00/`)

Node = the k0_00 ROOT at s0, no pins, no cores, budget 11; the only hypotheses are the
SHALLOW(delta) NO-families of the listed corners. Verdict is the FROZEN chain
`certify.py` -> `verify_case.py` (exact rationals, depth 56, 2 witness-feedback rounds,
eps_geo 0.002/0.004 repair on a FAIL). tau is the LP value and is NOT the arbiter (A54 S0);
the exact certificate total is.

| run | pattern | delta | a (window) | exempt boxes | sym | tau | eta | conv | LP s | cert s | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R4 | BL | 0.3 | 0.6896932 | 108 | C1 | - | - | - | 0 | 0 | **REFUSED (canary: g2, g6)** |
| R1 | BL+BR+TL+TR | 0.3 | 0.6896932 | 432 | D4 | 9.554681 | -1.445319 | no | 1042 | 1008 | **PASS** |
| R2 | BL+BR+TR | 0.3 | 0.6896932 | 324 | C1 | 10.046056 | -0.953944 | no | 994 | 2566 | **FAIL** (holes at eps_geo 0, 0.002, 0.004) |
| R2' | BL+BR+TR | 0.1 | 0.8867484 | 336 | C1 | 9.222755 | -1.777245 | no | 936 | 3202 | **FAIL** (holes at eps_geo 0, 0.002, 0.004) |
| R2" | BL+BR+TR | 0.05 | 0.9360122 | 336 | C1 | 8.726420 | -2.273580 | no | 910 | cut by wall budget | LP only |

**R1 certificate.** `certs/k0_00/R1_4shallow_d0.3.json` (+ `.PASS`, `.certify.json`,
`.report.json`). 732 atoms, 432 NO-families, 0 cores, exact total **1372003/125000 =
10.976024 < 11**; verifier: 220140 boxes, 107574 covered, 2528 exempt by NO-family, 0 holes,
max depth 36, 72.2 s. Claim certified:

> every admissible closed unit square in [0, 969271/250000]^2 that is not in a NO-family has
> mass >= 1, and mu(total) = 10.976024 < 11, hence NO packing of 11 unit squares at side
> <= s0 satisfies the hypotheses (node DEAD).

**Why the 3-shallow runs fail: LP CONVERGENCE under C1, not the geometry.** The decisive
number is `minmass` (the smallest mu(Q) over the generated rows; the certificate can only
verify once the row set is dense enough that minmass is near 1):

| run | sym | orbits | rows | tau | minmass | maxcov | certificate |
|---|---|---|---|---|---|---|---|
| R1 4-shallow d 0.3 | **D4** | 1048 | 5810 | 9.554681 | **0.8139** | 1.0828 | **PASS** |
| R2 3-shallow d 0.3 | C1 | 3199 | 7922 | 10.046056 | 0.6055 | 1.3458 | FAIL |
| R2' 3-shallow d 0.1 | C1 | 3381 | 5684 | 9.222755 | 0.5773 | 1.3587 | FAIL |
| R2" 3-shallow d 0.05 | C1 | 3364 | 5187 | 8.726420 | **0.3767** | 1.5117 | LP only |

The D4 quotient gives R1 a third of the orbits to fill, so 900 s of row generation reaches
minmass 0.81 and the witness-feedback rounds close the rest. The 3-shallow node is NOT
D4-symmetric (its family set is only invariant under the stabiliser of the pattern), so
`certify.py` runs it at C1 with 3x the orbits, and 900 s leaves minmass at 0.58. Note R2' at
delta = 0.1 has eta = -1.777, MORE headroom than R1's -1.445, and still fails - so this is a
budget artefact of the 900 s cap, not evidence that 3-shallow is unkillable.

**The delta sweep settles it.** tau falls monotonically as the exempt box grows, exactly as the
geometry predicts (a = 0.6897 -> 0.8867 -> 0.9360):

| delta | a (window) | tau | eta | minmass |
|---|---|---|---|---|
| 0.3 | 0.6896932 | 10.046056 | -0.953944 | 0.6055 |
| 0.1 | 0.8867484 | 9.222755 | -1.777245 | 0.5773 |
| 0.05 | 0.9360122 | 8.726420 | -2.273580 | **0.3767** |

But minmass DEGRADES along the same sweep. A larger exempt region gives the measure more
freedom, so 900 s of row generation covers proportionally less of it - the certificate needs
minmass near 1, and it is moving the wrong way. So shrinking delta does NOT rescue the
3-shallow kill; only more LP time does. That is the single actionable finding for the re-run. **The 3-shallow
kill is open, and the fix is LP time: re-run `R2_3shallow_d0.1` with lp_time >= 5000 s.**

**R2 (3-shallow) at delta = 0.3 does NOT certify.** The LP gives tau = 10.046056, and the
witness-feedback rounds RAISE it (10.046 -> 10.1665 -> 10.20896) as the row set fills in, so the
auto-scaled certificate total sits at 10.9747-10.9750, only 0.025 under the budget, and the
exact verifier finds holes at every margin: base rounds 7 / 16 / 12 holes, eps_geo 0.002 gives
12 / 5 / 19, eps_geo 0.004 gives 18 / 5 / 24 (of 32 witness boxes each). 2566 s of certification.
This is a genuine near-boundary node, not a convergence artefact: the LP value climbs toward 11
as rows are added, which is what a node whose true tau* is at or above the budget looks like.

Because every family is contained in R_c(a_win) with a_win = (1-delta)/lambda_max, the kill is
WINDOW-VALID: no packing of 11 unit squares at ANY side m in [3.82, s0] has all four corners
SHALLOW(0.3). And since SHALLOW(delta') implies SHALLOW(0.3) for every delta' <= 0.3, the same
certificate discharges delta = 0.1 and delta = 0.05 with no further LP.

---

## D. The k0_00 depth-2 certification coverage HOLES (`results/o3_holes.json`)

Method (`code/o3_holes.py`, LP-free, exact). For every witness box of A85's FAILed depth-2
certificates I compute, in exact Fractions, the corner-frame reach
`g_c(B) = min over poses in B of f_c`, where `f_c(c_Q, theta) = min over Q of max(x_c, y_c)`
(corner85.f_min_max) in corner c's frame; `f_c < 1` is exactly "Q meets the open unit corner
box B_c". `f_c` is nondecreasing in both corner-frame centre coordinates, so the min over the
centre rect is at the rect corner nearest c (an exact witness pose); a Lipschitz pad
(sqrt(2)/2 per radian, 97-point theta grid) makes the "no pose meets" direction rigorous too.
Intrusion depth of the box = 1 - g_c. "Ghost zone" = the theta range meets (0,2) u (88,90) deg.

### D.1 Per certificate

| certificate | verifier | witnesses | holes | undecided | corner poses | ghost-zone | interior/mid-tilt | depth range of the corner poses |
|---|---|---|---|---|---|---|---|---|
| s1int_l2_l2_p215_011 | FAIL | 32 | 6 | 26 | 32 | 0 | 0 | 0.0041 – 0.1727 |
| s1int_l2_l2_p215_011_epsgeo0.002 | FAIL | 32 | 8 | 24 | 24 | 0 | 8 | 0.0016 – 0.1867 |
| s1int_l2_l2_p215_011_epsgeo0.004 | FAIL | 32 | 3 | 29 | 16 | 8 | 16 | 0.1519 – 0.2344 |
| s1int_l2_l2_p210_001 | FAIL | 40 | 8 | 32 | 16 | 8 | 24 | 0.0078 – 0.0577 |
| s1int_l2_l2_p210_001_epsgeo0.002 | FAIL | 16 | 2 | 14 | 16 | 0 | 0 | 0.0944 – 0.2249 |
| s1int_l2_l2_p210_001_epsgeo0.004 | **PASS** | 32 | 0 | 32 | 32 | 0 | 0 | 0.1144 – 0.2473 |

(The brief's "8 exact holes + 24 undecided" and "2 + 14" are the eps_geo 0.002 rows.
`p210_001` is ultimately killed at eps_geo 0.004; `p215_011` is the node that stays FAILed at
every margin.)

### D.2 Summary counts

Over the two BASE certificates (72 witness boxes): 14 holes, 58 undecided;
**48 corner poses (67 %)**, **8 near-flush corner poses (11 %)**, **24 interior/mid-tilt (33 %)**.
Over all six variants (184 witness boxes): 27 holes, 157 undecided;
136 corner poses (74 %), 16 near-flush corner poses (9 %), 48 interior/mid-tilt (26 %).

### D.3 The near-flush ghost-zone holes, explicitly

Only two distinct configurations carry them, and both are **wall-flush uprights**, not tilted
corner jams:

| node | kind | corner | theta range (deg) | tilt (deg) | centre (cx, cy) | intrusion depth | dist. of box to corner point |
|---|---|---|---|---|---|---|---|
| p210_001 (base) | 8 undecided | TL | 89.5386 – 89.5396 | 0.4604 – 0.4614 | (0.5040, 2.3808) | 0.00777 | 1.5788 |
| p215_011 eps_geo 0.004 | 3 holes + 5 undecided | BL | 0.6987 – 0.6992 | 0.6987 – 0.6992 | (0.5061, 1.3541) | 0.15191 | 1.4456 |

Both sit at cx ~ 0.504–0.506, i.e. a unit square pressed flat against the LEFT wall (the
admissible minimum is cx = h(theta) ~ 0.5000), tilted 0.46 deg / 0.70 deg off flush, poking a
corner of itself into the corner box. This is the PI's "near-flush ghost zone" in its purest
form. It is 8/72 = 11 % of the base witnesses (16/184 = 9 % over all variants), and it is a
minority of what makes these nodes FAIL.

### D.4 Reading

The FAILs are **not** dominated by the near-flush ghost zone: two thirds of the witness boxes
are ordinary corner poses at 10–45 deg tilt (depth 0.002–0.25) and a third are interior boxes
with no corner reach at all. The mid-tilt corner poses (tilt 22–44 deg) are the bulk. Both
ghost-zone configurations have intrusion depth 0.0078 and 0.1519; deleting an interval
(0, theta_0) with theta_0 <= 1.73 deg (A50's theta*) removes the 0.699-deg one only if
theta_0 > 0.699, and the 0.461-deg one only if theta_0 > 0.461 — consistent with the doc's
"0 of A85's 5 FAILed LP nodes" re-price. Lemma ID cuts differently: SHALLOW(delta) at
delta = 0.05 would exclude the TL configuration (depth 0.0078 < 0.05) but not the BL one
(depth 0.1519); at delta = 0.3 both are inside the SHALLOW branch.

---

## B. The certified bound on how many corners can be SHALLOW

**Certified (window-valid, m in [3.82, s0]):**

> **No packing of 11 unit squares at any side m in [3.82, s0] has ALL FOUR corners
> SHALLOW(0.3)** - i.e. in every such packing at least one corner c has DEPTH(c) >= 0.3, so
> some square intrudes to within 0.7 of that corner (measured by
> min over Q of max(x_c, y_c) <= 0.7).

Certificate `certs/k0_00/R1_4shallow_d0.3.json` (+ `.PASS`), exact total 1372003/125000 =
10.976024 < 11, verified by the frozen `verify_case.py` at depth 56 with 0 holes.
Re-verified independently after the run (`verify_case.py certs/k0_00/R1_4shallow_d0.3.json
--jobs 1 --depth 56`): PASS, rc = 0, 220140 boxes, 107574 covered, 2528 exempt by NO-family,
0 holes, max depth 36, 85.9 s.

By SHALLOW(delta') => SHALLOW(0.3) for delta' <= 0.3, the same certificate discharges
**delta = 0.1 and delta = 0.05** for the 4-corner pattern with no further computation. This is
the largest delta this chore certified; delta > 0.3 was not attempted (the exempt box shrinks
as delta grows, so it is strictly harder and would need a fresh run).

**Not certified:** 3-SHALLOW at any delta tried (0.3, 0.1, and 0.05 attempted last), and therefore nothing was
attempted for 2-SHALLOW (adjacent or diagonal), which is strictly harder still: dropping a
corner from the pattern removes its exempt families, so tau is nondecreasing and
tau(2-shallow) >= tau(3-shallow) >= tau(4-shallow) at each delta. R3adj/R3diag at delta = 0.3
were dropped from the plan for that reason rather than run to a foregone failure.

**Status of the 3-shallow kill: OPEN, blocked on LP time, not on geometry.** See the minmass
table above - the C1 node needs roughly 5-10x the 900 s row-generation budget used here. The
resume command is in section 4.

## 3. Baselines cited (not re-run)

| statement | value | source |
|---|---|---|
| k0_00 plain root, NO exemption, D4, side 958303/250000 = 3.833212 | tau = 10.9999999998182, eta = -1.8e-10, 9873 rows, 843 s — **unkillable** | `attempts/A82-side-scan/results/scan_k0_00.json` (row 0) |
| same claim at s0 = 3.877084 | tau >= 11 a fortiori (tau is nondecreasing in the side) | A38/A85 |
| unstratified root at side 3.82, row-only, converged | tau = 10.715891376319226 (17709 rows, 3750 orbits) — A08's record root certificate "10.72 at 3.82" | `attempts/A07-lp-dual/results/tau_table.json`, entry `v2_s3.82_rowonly.json`; cited in `docs/proofs/k0_route.md` line 65 and `docs/proofs/protected_trees.md` line 513 |


## 4. Re-running / resuming the campaign

The campaign is fully scripted, gated and resumable. One command:

    cd attempts/A89-tilt-floor
    python code/o3_campaign.py --minutes <wall budget in minutes>

It runs the 13 planned nodes in priority order, ONE LP at a time, BLAS pinned to 1 thread,
polling `free_commit_mb() > 6144` every 60 s before each LP and before each certify launch.
Solved node LPs are cached in `results/nodes/k0_00/<tag>.json` and are reused on a restart, so
an interrupted campaign resumes without repeating LP work; every attempt appends one record to
`results/o3_runs.jsonl`. Certificates land in `certs/k0_00/<tag>.json` (+ `.PASS`,
`.report.json`, `.witnesses.json`), with A85's eps_geo 0.002 / 0.004 repair on a FAIL.

**The one change worth making before a re-run.** Every FAIL in this chore was a C1 node whose
900 s LP left minmass at 0.58 (R1, the only D4 node, reached 0.81 and PASSED). So:

    python code/o3_campaign.py --minutes 400      # with lp_time raised to 5000 in PLAN

for the 3-shallow entries. The node JSONs already written
(`results/nodes/k0_00/R2_3shallow_d0.3.json`, `..._d0.1.json`) are REUSED on restart, so
delete them first if you want a longer LP rather than a re-certify of the same measure.

Ordering exploits monotonicity: `SHALLOW(delta')` implies `SHALLOW(delta)` for delta' <= delta
and the exempt set `R_c(1-delta)` shrinks as delta grows, so tau is nondecreasing in delta and a
certified kill at delta discharges every smaller delta. The plan therefore runs delta = 0.3
first for each pattern and only falls back to 0.1 / 0.05 if 0.3 fails.

Symmetry: the 4-shallow node is bit-exactly D4-symmetric (verified by
`caselp.Hyp.is_symmetric_D4`), so both `solve_node` and the frozen `certify.py` use the D4
quotient (8x cheaper). The 3-shallow and 2-shallow nodes are C1. D4 justification for R2: the
3-subsets of the four corners are the complements of the single corners, and D4 is transitive
on corners, so the 3-subsets form ONE D4 orbit and a single representative (BL, BR, TR)
suffices. The 2-subsets split into two orbits (4 adjacent, 2 diagonal), which is why R3 needs
both (BL, BR) and (BL, TR).
