# A42 — the occupancy chain, the tightening sweep, and the far-field verdict

Fable lead, 2026-08-28. Compute by three Opus agents (chain, sweep, zone probe); every number
below verified against the artifacts by the lead (notes/verification_log.md V1-V5); exact
certification (verify_case.py) was the arbiter throughout. A29 untouched.

## 0. One-paragraph summary (plain language)

The far-field plan was: force each of the 11 squares into a small "ball" around its ideal
position (the occupancy chain), use Lemma N1 to conclude each ball holds exactly one square
with no bookkeeping explosion, then shrink the balls (the tightening sweep) until the A40
surgery certificate takes over. A42 measured every stage. The verdict: **Lemma N1 is proved
and the bookkeeping really is free — but the LP family that was supposed to supply the
occupancy facts has exactly zero forcing power at every ball and zone size we could legally
use, for a structural reason, not a cost reason.** The chain dies at its first step by an
exact integer; the sweep is provably vacuous; making the zones 34x bigger buys nothing. The
one occupancy statement that works (A38's central-window root) works because of WHAT it
empties, not how much. The cascade as designed is dead, and the far field now demonstrably
requires new mathematics of the N6 class (the ghost equality manifold), not more compute.

## 1. T1 — Lemma N1: PROVED (docs/proofs/occupancy_collapse.md)

- N1.0 (separation): distinct squares of a packing have centre distance >= 1 (inscribed-disk
  argument); sharp, and Trump attains it — min pairwise centre distance^2 = 1 EXACTLY.
- N1.0.1: any zone of diameter < 1 holds AT MOST ONE centre — pure geometry, no pigeonhole.
- N1 (collapse): m <= 11 pairwise-disjoint zones of diameter < 1, each certified to contain
  >= 1 centre => exactly one each, assignment zones -> squares UNIQUE, labeled hypothesis =
  one S11 orbit (no assignment branching: the 16^10 = 1.1e12 labeled catastrophe is gone);
  at m = 11 the complement is certifiably centre-free.
- Corollary N1.1 (branch-free wrap conditioning): occupancy of a (c,theta)-zone may be imposed
  as full-theta core + window-complement NO-family — removes the 2^6 wall-square wrap split.
- Explicit failure modes stated (overlapping zones / diameter >= 1), per the brief.
- Instance hypotheses machine-checked in exact rationals (code/n1_check.py, exit 0): footprint
  disjointness min sup-gap 0.615966; max diameter^2 = 18/625 = 0.0288 < 1. Valid for every
  radius r' <= 0.06.

N1's status is unconditional: it is correct, short, Lean-friendly — and now waiting for
occupancy premises that the coverage family cannot supply (sections 2-4).

## 2. T2 — the chain: DEAD AT k = 1 BY AN EXACT INTEGER (results/chain.json)

Setup: balls of radius 0.06 (theta +-6 deg) at the 11 Trump e-frame placements, chain order
[6,8,5,3,1,0,4,7,9,10,2] (greedy NN from the A38 witness), step k = cores at balls 1..k
(Cor N1.1 encoding), NO-family target = ball k+1, budget 11-k, A39 cert-in-loop rule.

| k | ball | budget | tau (converged) | slack | status |
|---|---|---|---|---|---|
| 0 | 6 | 11 | 10.9835 (unconv) | -0.016 | undecided (no kill) |
| 1 | 8 | 10 | 10.000000000000 | 0 | alive(LP) |
| 2 | 5 | 9 | 9.000000000032 | 0 | alive(LP) |
| 3 | 3 | 8 | 8.000000000000 | 0 | alive(LP) |
| 4 | 1 | 7 | 7.000000000000 | 0 | alive(LP) |
| 5 | 0 | 6 | 6.000000000000 | 0 | alive(LP) |
| 6-10 | 4,7,9,10,2 | 5,4,3,2,1 | 12-k exactly | +1 | alive(LP) |

Every k >= 1 CONVERGED with minmass 1.0 — these are true LP optima, not timeouts. Facts
measured (notes/structural_facts.md):

- **F2, unit exchange**: each 0.06-ball core lowers tau by EXACTLY the 1.0 budget unit it
  consumes. Net headroom per chain step = 0 identically; no decay constant exists — the
  requested slack-decay curve is the constant 0, k = 1..10 (the wall-clipped corner ball 0
  buys nothing at all: a permanent +1 from k = 6 on).
- **F3, reflow**: the forcing target is worth EXACTLY ZERO — deleting the target NO-family
  changes tau by < 1.2e-12 at every k, and shrinking it (tighten probe, k=2, rho' = 0.045
  down) changes nothing: d(tau)/d(rho') = 0. The coverage measure relocates around any
  ball-sized exemption at no price.
- The A38 probe-A "slack -0.80" was an early-relaxation artifact: the converged union-form
  optimum is 10.000000 (619 s). The brief's "k=0 slack 3.0" datum was the CENTRAL-WINDOW
  root (side-1.68 zone), not a ball; the true k=0 ball node has slack ~ 0.
- Cost was never the issue: 18 chain/control/probe nodes in 33 minutes, all well-behaved.
  The family fails on VALUE.

## 3. T3 — the sweep: STRUCTURALLY VACUOUS, with one keeper (results/sweep.json)

- **F1, the last-square identity** (one-line theorem): at budget 1, tau >= mu(any admissible
  placement) >= 1, so a budget-1 node kills iff the admissible set is EXACTLY EMPTY. The
  coverage LP contributes nothing beyond the verifier's emptiness check. All 111 tightening
  nodes: tau = 1.000000 = budget, at EVERY rho' (0.03 / 0.015 / 0.0065, flat across three
  decades); dying radius = R_j itself; a liveness scan shows collision-based emptiness is
  unreachable at any core quality. **The PI's Gauss-Seidel conjecture is honestly refuted at
  this budget: second-pass gain = exactly 0** (ball 6, target 0.03: tau 1.000 under
  others-at-0.06 AND under others-at-0.03). Retro-explanation: this identity is why the 3.84
  endgame needed full pinning at deep leaves.
- **F5, the keeper**: the N1 assignment step itself is FREE. Given the post-N1 encoding
  (10 cores + window complements + exact complement cover), the 11th square is forced into
  its ball by the exact verifier alone — measure total 1e-6, no LP, 0.9-8.6 s per ball,
  11/11 PASS in 38.1 s. Emptiness certificates are the one family with real margin here —
  but they consume occupancy premises, they cannot create them.
- **F6**: F1 + F2 + F3 compose — there is NO k and NO rho' at which the 0.06 family
  certifies anything. Tightening cannot be rescued by interleaving it into the chain.

## 4. The zone-size lever: DEAD; volume scaling REFUTED (results/zoneprobe.json)

N1 permits zones up to diameter 1; half-width 0.35 zones (side 0.70, ~34x a ball's volume,
pairwise disjoint, min gap 0.036) were the last untested design point.

| node | w | budget | tau | verdict |
|---|---|---|---|---|
| k=0 | 0.35 | 11 | 10.999999999996 | 29 cert attempts, ALL FAIL (best cert: 14 coverage holes) |
| k=0 | 0.25 | 11 | 10.929 (unconv, rising) | 24 attempts, fail |
| k=0 | 0.15 | 11 | 11.087 | 5 attempts, fail |
| k=1 | 0.35 core | 10 | 10.855 | core costs 1.0 budget, buys 0.145 tau: net -0.855 |

Headroom is NOT volume: the side-1.68 central window buys 3.0 of tau; a side-0.70 zone at a
placement buys ~0.000. Medium cores are ANTI-economical. The failure mode is A39's headroom
closure again — repairs raise the certificate total against a budget with no room.

**Conjecture (recorded, not run): occupancy power = ghost mass displaced, not volume.** The
central window works because it empties the region where the 1/4-ghost's pinwheel mass must
live. Testable by profiling the ghost measure's mass distribution against zone kills — future
work, no compute spent.

## 5. T4 — composed verdict: NO-GO, by mechanism

seam_design.md's cost formula asked for the cascade term N1 * F_w * [10 + 10 * sum b_eff^d]
* T_D. A42's answer: **the term is not expensive — it does not exist.** Step 1 of the cascade
(the 10 zone certificates) produces no certificate at any measured design point: balls at
r = 0.06 (slack exactly 0, k = 1..10), medium zones to w = 0.35 (tau = 11 exactly at k = 0),
mid-chain shrunk targets (worth 0), post-assignment budget-1 nodes (vacuous by theorem).

Desktop-days bracket:

| route | status | cost |
|---|---|---|
| S1 cascade (chain + N1 + sweep) | no certificates exist — mechanism, not cost | unbounded (dead) |
| labeled cascade | dead since A38 | 1.1e12 leaves |
| pure refinement | A39: 0 decisions at depth 2, T_D unbounded | no finite bracket |
| surviving finite pieces | root (banked) + N1 (proved) + F5 assignment (given premises) | ~40 s per attractor |

**GO/NO-GO: NO-GO** for the far-field campaign with the coverage-family weapons, and — unlike
A38/A39's cost-shaped NO-GOs — this one is structural: the integer-exact conditional taus mean
the 1/4-ghost fractional packing SATURATES every conditional budget at s0. The five A38
alive(LP) knife-edge cells were not a corner case; under conditioning, the entire far field
behaves like them. N6 is the generic mode, not the residual.

**What survives**: the A38 central-window root certificate (banked); Lemma N1 + Cor N1.1
(proved, zone-size-flexible, Lean-friendly); the F5 free assignment step (38 s per attractor
— machinery-in-waiting for ANY future weapon that supplies eleven >= 1-occupancy statements);
the F1 identity and F4 shield as design filters (they cheaply exclude whole proposal classes);
the A39 cheap-cert rule (re-validated: 0.6-16 s per attempt, correctly gated).

**What is closed**: small-ball occupancy at every k; union-form occupancy; mid-chain target
tightening; budget-1 post-assignment tightening (incl. the second-pass conjecture); medium-
zone occupancy to w = 0.35; anti-economical medium cores; deep cores (A39, upheld).

## 6. Gap list — what the far field genuinely requires (N6-class)

1. **A weapon on the ghost equality manifold itself.** Candidates, with honest caveats:
   (a) the advisor's two-field / guard-field budgets (I-L13, A33): pigeonhole on guard mass in
   [1, 1+eta] — CAVEAT: A33 measured multi-field stacking worth only 4.6% because all
   near-optimal fields share the fractional-packing support (complementary slackness); any
   two-field proposal must first explain why it escapes that obstruction; (b) a NOFAM-AWARE
   non-coverage exclusion — an FJ/Farkas argument that READS emptiness hypotheses (A30's
   menus do not; by the F4 shield, any weapon blind to the target nofam can never force
   occupancy, since Trump realizes the rest of the hypothesis); (c) theta'-type second-order
   rows (A16 killed exactly this node type on grids; the continuum certificate died in
   A17-A20 — reviving it needs a new idea, not a rerun); (d) the ghost-mass profiling
   conjecture of section 4 (diagnostic first step for (a)-(c): FIND where the ghost's mass
   is forced to live).
2. **A40 ceiling levers** (G-A40-2/3, ceiling ~0.02): shrink the endgame window from the
   basin side — real but secondary; a bigger basin does not create occupancy power.
3. **N6 as stated** (seam_design §4) stands, promoted: it is now the whole far field, not
   five cells.
4. Chain order dependence unexplored (one order measured; F2's integer exactness at every k
   makes order-sensitivity implausible, but it is an inference, not a measurement).
5. The ghost-mass conjecture itself (future work, no compute committed).

## 7. Files

- docs/proofs/occupancy_collapse.md (N1 + N1.1, proved); code/n1_check.py (exact H1 check).
- code/: chain42.py, sweep42.py, zoneprobe42.py (drivers; shared modules untouched).
- results/: chain.json + chain_nodes/, tighten_probe.json, sweep.json + sweep_nodes/,
  zoneprobe.json + zone_nodes/, spotverify.json, a42_report.md (this file).
- notes/: structural_facts.md (F1-F6, the named identities), T4_frame.md (pre-registration of
  the composition frame), verification_log.md (V1-V5).
