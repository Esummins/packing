# A51 — mid-tilt flush-free basin hunt: closing A49's sampling caveat
(computation postdoc, Opus, 2026-08-31)

Constants: s0 = 969271/250000 = 3.877084. **[NUM] float64 by design** — this is
a hunt/measurement, not a certificate run; the exact stage is wired and
self-tested (§7) but no survivor arose to send through it.

## 1. Question

A49 (results/a49_report.md) reached OUTCOME B on the A48 evasion architecture
and banked an empirical law — *the flush-free evasion never breaks at the
presser; it breaks at the binding chain's WALL TERMINATION* — with an honest
caveat: all 12 A49 seed architectures lived in the near-upright world (tilt
profiles 1-7 deg), every one of the 252 drains landed on the s = 4
axis-aligned grid, and **the mid-tilt non-thin flush-free world was never
sampled**. A51 samples it, with the identical protocol, and asks two things:

1. does a flush-free critical point exist in the mid-tilt regime?
2. does A49's wall-termination law survive there?

## 2. Machinery (no A49 file edited or copied)

`code/a51_run.py` imports `a49_common` (with the FIXED `repair_ok`: lam_hi = 8
plus an explicit feasibility check — the A49-discovered `a37_drain.repair`
cap bug), `hunt_a49`, `stratum_a49`, `audit_a49`, and only **rebinds
`a49_common`'s output directories** to A51's `results/`, `work/`, `logs/`
(every A49 driver resolves them at run time) plus swaps the control-seed set.
Definitions unchanged: tol_f = 0.05 deg, contact/wall-activity tolerance 1e-6,
class distance |a-b| mod 90 folded to [0,45], class-from-axis
min(a mod 90, 90 - a mod 90).

## 3. Seeds (results/seeds.json; notes/seed_design.md) — 19 families, 19 accepted

The tilt comb of `stratum_a49.comb_angles` is used as a **flush OPENER**:
combing the 11 tilt classes apart on R/90deg (axis class pinned) turns every
flush pair contact and every wall-flush of a critical family into a small-gap
corner/edge contact, moving the mid-tilt values by tenths of a degree;
`repair` then restores feasibility by scaling CENTRES only, so the comb — hence
flush-freeness as a stratum property — survives verbatim.

| family | ids | construction | s_repaired | mid-tilt content |
|---|---|---|---|---|
| (i) atlas-opened | M01-M08 | A37 atlas families 0, 1, 6, 13, 26, 31 opened at 0.50 deg; M07/M08 = families 0/13 opened WIDE at 1.75 deg | 3.93-4.13 | 4-5 of 11 |
| (ii) mid-tilt lattice | M09-M12 | compact 11-site blob of the unit-square TILING lattice at base tilt 22/30/38 deg, tilts combed apart 0.6 deg (M12: 1.4 deg) | 4.51-4.78 | 11 of 11 |
| (iii) [45,0,45] fattened | M13-M15 | A47's s* thin chain de-quantized (U given a genuine mid tilt 8/20/32 deg; diamonds combed off 45) and FATTENED: 8 complement squares in 3 rows pressed onto the chain, every chain square H-degree >= 3 | 5.27-5.49 | 10-11 of 11 |
| (iv) random mid-tilt | M16-M19 | rejection-sampled, 11 tilts uniform in [15,45] deg, randomly oriented/permuted/jittered compact site pattern, best of 250 draws | 4.66-4.84 | 11 of 11 |

All 19 accepted: repair-feasible (`repair_ok`), flush-free at tol_f, min tilt
class gap >= 0.30 deg. Two constructor facts recorded in the notes:
all-mid-tilt configurations are intrinsically wide (best compact seed repairs
to s ~ 4.5, versus 4.0 for the trivial grid), and the fattened [45,0,45] chain
**cannot** be compact (a full-width chain band plus 8 complement squares needs
three more rows, s >= ~5.2) — a seed-level shadow of A47's s* no-completion
lemma.

Roles here are **TILT REGIMES**, not A49 decks: UPRIGHT (< 12 deg), MID
(12-30), HIGH (>= 30); `summary_a51.CATMAP` translates every label so A49's
deck names are never printed for A51 data.

## 4. Run census (free descent, 19 seeds x (1 + 20 replicas) = 399 runs)

Producer `code/hunt_a49.py` via `a51_run.py census`, data `results/hunt.json`
(66.0 min wall). Same jitter (centres sigma 0.02, angles sigma 0.3 deg), same
traced `free_descent`, same feasible-path `micro_descent` resolver.

| outcome | n / 399 | A49 (n / 252) |
| --- | --- | --- |
| **(a) flush-free landing surviving the CP screen** | **0** | **0** |
| (a-raw) landing flush-free at tol_f | 12 | 17 |
| **(b) flush acquired** | **395** | **252** |
| **(c) drains to a known family** | **328** | **235** |

- **Zero candidates, zero survivors.** All 12 flush-free landings are
  constructively NOT-CP: nnls residual 0.7122-0.7297, LP descent rate -1.0,
  explicit smaller-s witness with gain 2.5e-4 … 1.11, at s = 4.18-5.11 —
  stalls high above s0, exactly the A49 shape.
- **The mid-tilt seeds reach the interesting part of the space.** 172/399
  landings sit below s = 4, and **15 land exactly on the Trump packing**,
  s = 3.8770835900228224 = s0. A49's 252 runs never came within 0.12 of s0.
- Landings spread over 30 catalogue families plus A37-NEW-1, headed by
  catalogue 34 (the s = 4 grid, 115), 13 (43), 6 (23), 1 (20), 0 (15), 31 (15).
- **Regime split in where the seeds drain.** (i) atlas-opened: s_min = s0
  (3.877084), drains to real critical families (0, 1, 6, 13, 31, A37-NEW-1).
  (ii) lattice: s_min 3.9153. (iii) fattened chain: s_min 3.8972.
  (iv) random: s_min 4.0000 — the all-mid-tilt seeds mostly still collapse to
  the s = 4 grid.
- All 399 landings verified feasible to <= **5.6e-16**.

## 5. The MID-TILT flush-acquisition map — and A49's law does NOT hold here

Data: `results/hunt.json` -> per-run `acquisition` (feasible-path micro-descent,
every trace point an exact feasible packing) — 257 events; the solver-iterate
trace fires 395/399 and is recorded alongside.

| first-flushing category (seed-time regimes) | n | share |
| --- | --- | --- |
| WALL, UPRIGHT square | 82 | 32% |
| pair HIGH-HIGH | 60 | 23% |
| pair UPRIGHT-UPRIGHT | 34 | 13% |
| pair MID-HIGH | 31 | 12% |
| pair MID-MID | 24 | 9% |
| WALL, MID square | 13 | 5% |
| WALL, HIGH square | 13 | 5% |
| **pair UPRIGHT-MID / UPRIGHT-HIGH** | **0** | **0%** |

**(5a) The wall-termination law is REGIME-DEPENDENT — and it inverts.**
A49's decisive statistic was the SOLO events (a single contact flushing, as
opposed to a simultaneous collapse): 19 of 20 were wall terminations (95%).
Split by A51 seed family:

| seed family | events | wall | pair | SOLO events | solo wall |
| --- | --- | --- | --- | --- | --- |
| A49 (near-upright) | 97 | 48 (49%) | 49 | 20 | **19 (95%)** |
| (i) atlas-opened (mixed) | 160 | 82 (51%) | 78 | 35 | **28 (80%)** |
| (ii) mid-tilt lattice | 36 | 9 (25%) | 27 | 11 | 1 (9%) |
| (iii) chain fattened | 42 | 13 (31%) | 29 | 3 | 0 (0%) |
| (iv) random mid-tilt | 19 | 4 (21%) | 15 | 2 | 0 (0%) |
| **ALL-MID-TILT (ii)-(iv)** | **97** | **26 (27%)** | **71** | **16** | **1 (6%)** |

In the world A49 sampled, and in the mixed world of opened critical families,
the wall termination is where flush is acquired (80-95% of solo events). In
the **pure** mid-tilt world the statistic **inverts**: 15 of 16 solo events
(94%) are INTERIOR PAIR events, and the wall share of all events falls from
49% to 27%. A49's banked law is therefore *not* a law of flush-free
configurations; it is a law of configurations that **contain near-upright
squares**.

**(5b) The mechanism behind the inversion (and the one clean universal).**
**Zero of 149 pair events are cross-regime UPRIGHT x (MID or HIGH)** — an
upright square never acquires flush with a tilted one. It acquires flush with
a wall (82 events) or with another upright (34). Tilted squares acquire flush
with each other (115 events). So flush acquisition is *within* a tilt regime,
and the "wall termination" of A49 is what an UPRIGHT square's flush event
looks like: with near-upright squares present, the walls are where the axis
class already lives, and they collect the event. Remove the near-upright
squares and the event has nowhere to go but an interior tilted pair.
The wall breakdown is also asymmetric: y=0 (33) and y=s (28) dominate x=0 (7)
and x=s (10), with 30 corner (two-wall) events.

**(5c) Flush is acquired well BELOW the grid.** Median s at acquisition
**3.9159** (min 3.8771 = s0, max 5.9969), versus A49's 4.0000000000375 — in
A49 flush was acquired essentially *at* the collapse onto the s = 4 grid, so
the event carried no information about the critical region. Here 61/257 runs
kept descending after the event and the median event sits between s0 and 4.

**(5d) Simultaneity is broader but the collapse is still dominant.** Number of
contacts violating flush at the event: 1 in 51 runs, 2-9 in 27, 10-15 in 149,
16+ in 30 (median 11). A49 saw a rigid 1/10/13 pattern; A51 sees the same
"whole packing goes flush together" phenomenon over a wider spread, spanning
1-6 role categories at once (3 categories in 111 runs).

## 6. Stratum-constrained descent + FJ tests

Producer `code/stratum_a49.py` via `a51_run.py`, exact smooth encoding
g = sin^2(2(th_i - th_j)) - sin^2(2 eps) >= 0 unchanged.

**(2) GLOBAL stratum, eps_s = 0.25 deg, all 55 pair rows + 11 axis rows
(`results/stratum.json`, 399 runs).** Strictly stronger than flush-freeness.

| verdict | n / 399 |
| --- | --- |
| PRESSED-ON-FLUSH-BOUNDARY (>= 1 row active at 1e-6 deg) | **394** |
| INTERIOR, and NOT-CP under the full FJ test | 5 |
| INTERIOR-CANDIDATE | **0** |

3237 pair rows and 550 axis rows active in total. Median landing s = 4.00939,
**min 3.889299** (A49: 4.00173). The 5 interior points are stuck starts, not
interior minima: each has s_final = s_start, nnls residual 0.652-0.718, LP
descent rate -1.0 and a constructive witness of gain 0.61-1.48.

**(2b) LOCAL stratum, eps_l = tol_f = 0.05 deg, rows = only contacting /
near-contacting pairs and wall-touching squares, re-selected every round
(`results/stratum_local.json`, 114 runs = 19 x (1 + 5)).** The sharp test.

| verdict | n / 114 |
| --- | --- |
| BLOCKED-BY-FLUSH-BOUNDARY | **113** |
| PRESSED-ON-FLUSH-BOUNDARY | 1 |
| INTERIOR (any) / INTERIOR-CANDIDATE | **0 / 0** |

All 114 stopping points are flush-free; BLOCKED means every improving step —
the damped SLSQP step at every scale down to 1e-3 of it, and the LP descent
direction of the audited active rows — leaves the flush-free set. Median
s = 4.00119, **min s = 3.8784120** = s0 + 0.00133 (A49: 4.00001).

**So flush-freeness costs about +0.0013 in s here, measured AT the critical
region rather than at the grid** — the same qualitative statement as A49's
"+0.013", but now a genuinely local one: a flush-free descent gets to within
0.0013 of the Trump optimum and is then blocked. Of the 1204 escape rows at
the blocking step, 723 are pair rows and 481 wall rows (again the interior
majority); 16 escapes are solo, 11 of them wall.

**Summary of (2): 0 of 513 stratum minimisers is an interior flush-free local
minimiser.**

## 7. Candidate audits, exact stage, negative control

- **Candidates from (1a) + (2ii): 0. SURVIVORS: 0.** `audit_a49.py` ran with
  the same SURVIVOR criteria (GN convergence <= 1e-30, displacement < 1e-6,
  flush-free after refine, no constructive witness, **Fritz-John stationarity
  numerically satisfied**, class in VALLEY/RIGID/RATTLER-CORE).
- **Exact stage wired and self-tested (new).** `code/krawczyk_a51.py` composes
  A37's 3R chain (audit -> GN refine -> classify -> QR-pivoted 34-row pin set
  -> high-precision Newton -> approximate inverse Y -> interval **Krawczyk**)
  into one entry point for an A51 survivor. Canary on atlas family 0 (the
  Trump packing): contracts at r_N = **1/2000**, ratio **0.056632**, value
  enclosure [3.8770835900228136, 3.8770835900228144] (width 8.9e-16), and the
  flush detector correctly reports it NOT flush-free — reproducing A37's own
  record exactly. With 0 survivors the stage is a no-op, but it is real code
  that has been run, not a promise.
- **Negative control (`results/control.json`, 63 runs = 3 x 21).** Mid-tilt
  atlas families taken UNOPENED at full precision (0 = RIGID Trump, 13 and 31
  = VALLEY), jittered with the same sigmas. **63/63 landings have flush
  contacts** (median 13 violations per landing; 338 wall + 429 pair in total)
  — the detector fires exactly where it should in this regime too. All three
  un-jittered base runs hold *exactly* at their own s and rematch to
  themselves. Rematch: family 13 21/21; family 31 15/21; family 0 11/21 (6
  jitters hop to family 1, 4 to the new attractor below).

## 8. Side finding: an attractor the catalogue and the atlas both miss

26 census landings and 4 control landings converge to **s = 3.8853914**, which
`same_family` (D4 x relabel x translation, s-tol 1e-8, geometry 1e-6) matches
to nothing in the A04 catalogue, the A37 atlas, or the A37-NEW list; nearest is
catalogue 1 at ds = 2.27e-4, tilt-multiset distance 3.83 deg, geometric
distance 0.067 (1/11 squares aligned). Put through `krawczyk_a51.certify_z` it
audits to 14 pair + 19 wall contacts with **GN residual 6.8e-71** (a consistent
contact set) and classifies **VALLEY, rank 33/34** — so the 3R/Krawczyk path
does not apply (no 34-row pin basis; valleys need A37's 3S soft path) and no
certificate is claimed. It is above s0 and has flush contacts, so it is
irrelevant to the bound and to flush-mandatory, but it is further evidence for
A37's own finding that the A04 catalogue is not a complete attractor list.
Two smaller clusters (s = 3.9240031 x2, 3.9324206 x2, and singletons at
3.9303606 / 3.9314737 / 3.9372223) are unresolved.

## 9. Verdict

**OUTCOME B again, in the regime A49 could not reach — with the banked law
falsified as stated.**

1. **No flush-free critical point in the mid-tilt world.** 399 free descents:
   0 candidates, 0 survivors, 12 flush-free landings all constructively
   non-critical. 513 stratum minimisers (399 global + 114 local): 0 interior.
   113/114 local-stratum minimisers are BLOCKED — every improving direction
   leaves the flush-free set.
2. **The evidence is much sharper than A49's**, because the mid-tilt seeds
   actually reach the critical region: min s = 3.8770835900228224 = s0 exactly
   (15 runs), 172/399 landings below 4, flush-free descent blocked at
   s0 + 0.00133, median flush acquisition at s = 3.9159. A49's whole census
   lived at s >= 4.
3. **A49's wall-termination law does NOT generalize.** It is a law of
   configurations containing near-upright squares (solo events 95% wall in
   A49, 80% in the mixed opened-atlas family), and it INVERTS in the pure
   mid-tilt world (solo events 6% wall / 94% interior pair; wall share of all
   events 27% vs 49%). A global proof of flush-mandatory cannot be built on
   chain wall-termination instability alone.
4. **What replaces it (the A51 law, 0 counterexamples in 257 events):**
   flush is acquired **WITHIN a tilt regime** — 0 of 149 pair events join an
   upright square to a tilted one. An upright square's flush event is with a
   wall or another upright; a tilted square's is with another tilted square.
   A49's wall termination is the upright case of this; the mid-tilt case is an
   interior tilted pair. This is the shape a global lemma has to have.

I-L19 remains a global-realizability conjecture; nothing here is a theorem.
What A51 removes is A49's sampling caveat and one of its two banked claims.

## 10. Gap list

- **G-A51-1 (supersedes A49's banked law).** "The evasion breaks at the
  binding chain's wall termination" is FALSE as a general statement (§5a).
  The replacement candidate is the within-regime law (§9.4); it is an
  empirical regularity over 257 events, not a lemma, and A50's T2
  wall-termination instability program should be re-scoped accordingly.
- **G-A51-2.** All events are labelled by SEED-time tilt regime. The event
  geometry itself is exact (a wall event means class-from-axis < 0.05 deg at
  the event; a pair event means class distance < 0.05 deg), but "a MID square
  rotated to the wall" is a statement about where the square started. An
  event-time regime histogram would need the tilt vector stored at the event.
- **G-A51-3.** The all-mid-tilt seeds (ii)-(iv) still mostly drain to the
  s = 4 grid (115/399 landings at catalogue 34); only the opened-atlas family
  reaches s0. Whether that is a property of the mid-tilt basin structure or of
  the seed constructor (compact tiling-lattice blobs) is not settled.
- **G-A51-4.** The (iii) fattened [45,0,45] seeds start at s ~ 5.3 because a
  full-width chain plus 8 complement squares needs four rows. The A47 non-thin
  branch near s* is therefore probed only through the descent's own path, not
  from a tight seed; a dedicated near-s* completion search is not done.
- **G-A51-5.** The new attractor at s = 3.8853914 (§8) is VALLEY rank-33 and
  uncertified; the A37 3S soft path would settle it, together with the four
  unresolved singleton clusters.
- **G-A51-6.** Unchanged from A49: [NUM] float64 throughout, tol_f = 0.05 deg
  and contact tolerance 1e-6 are conventions, and a hunt cannot prove
  non-existence.
