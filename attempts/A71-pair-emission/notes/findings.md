# A71 — pair emission + stuckness rows + corners4 wall: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [M] measured/computed exact (Fractions), [F] float evidence, [C] open.
Successor to A66 (design + pilot); BRIEF: attempts/A71-pair-emission/BRIEF.md.

## T1 — the emission oracle loop, k4_08, beta = 1: verdict

**Machinery built and exercised** (code/: emitlib.py, emitk408.py [covering LP with proper
column generation over a snapped 1/32 net + adversarial row hunt], mockbb.py [verifier-faithful
float B&B, discharge rules identical to verify_pair.py, outward-padded], etaprobe.py,
wallwit.py/wallwit2.py, calib_verify.py). Frozen verifier untouched
(sha256 d9b7a24a...662d re-verified). Canary per run (below).

**Verdict: NO certificate emitted at the full (P2') quantifier — the failure mechanism is a
quantified three-layer VERIFICATION WALL**, not a design unsoundness and not a restricted
infeasibility:

1. **Restricted feasibility stands** [M/F]: tau_2(beta) = 21 + 6*beta exactly (A66,
   re-confirmed); the covering side has 1.0 of headroom below the threshold 28 at beta = 1.
2. **The margin wall [T + M exact]**: define an atom's collection margin on a row as its
   min depth in the two squares. NEW exact witness (results/wall_witness2_k4_08.json (eta=0.15; the first-found eta=0.18 witness kept in results/wall_witness2_k4_08_eta018.json)):
   K = 11 unit squares at s0 (mixed tilts, exact rationals), each core-free vs the
   delta = 1/1000 slack cores, with PAIRWISE DISJOINT eta-cores at eta = 0.15 (K = 11), realising
   D = 35 interior-disjoint pair rows + Sigma m2 = 4 box incidences: V = 39 >= 28.
   Since eta-deep endpoints lie in the pairwise-disjoint eta-cores, each atom serves at most
   one family row at margin eta, so ANY atomic measure covers the family rows at margin 0.15
   with total >= 39 > W2 for every P1'-valid certificate: **every valid k4_08 beta = 1
   certificate must carry >= 11 units of its row coverage on atoms LESS than 0.15 deep** —
   and the construction perturbs (the exact witness keeps >= 5e-4 slack), spreading such
   rows through the container.
   Fractional strengthening [F]: the restricted adversary value with membership counted
   eta-deep, tau_2^eta(1), is 27.000 at eta = 0.01 (no gain over sharp) and climbs through
   the threshold within eta in (0.03, ~0.1] (etaprobe; the eta = 0.03/0.05 cut loops were
   time-capped while still > 28 and descending — per-eta convergence state recorded in
   results/etaprobe_*.json).
3. **The cost identity [M]**: verify_pair.py's COVERED discharge needs certain membership
   over the whole pair box, i.e. atom margins comparable to the box radius; sub-eta-margin
   coverage forces leaf pair-boxes of centre-scale ~eta/2.5. Leaf-count geometry at s0:
   ~((2.877/r)^2 * n_t)^2/2 pair leaves at centre-scale r. Measured frozen-verifier
   throughput (results/calib_verify.json, 3000-atom synthetic, exact Fractions):
   **57 nodes/s** (17.5 ms/node; the mock replays the same rules at 72k nodes/s, 1250x).
   Even the impossible best case (all margins ~0.15, ruled out by layer 2) needs
   ~6e8 pair leaves ~ 125 days single-core; all-margins-0.10 ~ 7e9 ~ 4 years;
   all-margins-0.05 ~ 4.5e11 ~ 250 years; the forced sub-margin regions of layer 2
   are orders beyond (leaf table exact in the A71 report). The wall is intrinsic to the v1 verifier's uniform certain-membership
   discharge, in exactly the direction A66's spec sect. 5 flagged ("COVERED needs very
   tight boxes"; margin-aware splitting is a v2 concern).

**What the loop DID produce** [M/F]:
* The loop's empirical FIXED POINT: with adversarial row hunting + mock-witness feedback,
  the covering LP climbs from the restricted 27 to W2 = 30.000171 >= 28 (three iterations,
  colgen to stall; certs/pair_k4_08_s0_b1_v1.json, P1' VIOLATED) — the continuum rows price
  the wall on the covering side directly.
* End-to-end frozen-oracle demonstration: the rescaled P1'-valid variant
  (certs/pair_k4_08_s0_b1_v1s.json, W2 = 27.899836) judged by the FROZEN verifier:
  VERDICT FAIL at depth 12 (witness pair boxes with certain mass 0 vs required 2, U = 1;
  certs/pair_k4_08_s0_b1_v1s.report.json) — the oracle interface works end to end and
  fails exactly at the wall. (Interface note, not a soundness bug: the frozen parser
  rejects float literals ANYWHERE in the JSON including the spec-'ignored' provenance
  block; emitters must stringify provenance numbers.)
* Mock volume profile at the fixed point (results/emit_k408_hist_v1.json): at depth cap 24,
  discharge volume ~0.6% per 3M nodes with covered-by-depth peaking at depth 23-24
  (cells ~0.045-0.06, matching the M_LP = 0.02 margin), 20-25% of examined boxes hitting
  the cap — extrapolated full-tree ~1e9+ nodes for THIS candidate before the sub-margin
  regions are even reached.
* Wall-witness landscape (greedy exact miner, results/wall_witness2_*.json): k4_08 beta=1
  V(eta) = 17/19/20/22/39 at eta = 0.10/0.11/0.12/0.13/0.15 (threshold 28; exact witness at
  0.15); corners4 beta=0: V(0.15) = 22 >= 21 EXACT (K = 9, D = 22) with V(0.12) = 14 —
  both walls sit near eta ~ 0.14-0.15 for the exact-integral form (greedy lower bounds;
  the fractional wall is lower).

**Positive scientific content**: (i) the wall is about VERIFICATION COMPLEXITY, not the
mathematical existence of the certificate — the sharp-semantics LP has value 27 < 28 on
every audited catalog with zero fractional excess, and nothing in layers 2-3 obstructs a
measure-existence proof; (ii) the margin wall is a new, exactly-witnessed obstruction CLASS
(shrunk-core families — s(12)-style ghosts one level up) that any future pair-certificate
verifier design must price; (iii) k4_08's pins genuinely obstruct the cheapest (axis-grid)
shrunk families — the axis 4-row band is EMPTY at s0 (wallwit.py: the y-interval a 4-row
needs, [2.499, 2.378], is empty; the pins protect at the exploit level too), which is why
the wall sits near eta ~ 0.15 rather than at the naive (4 - s0)/6 ~ 0.02.

## T2 — stuckness rows: docs/proofs/stuck_rows.md [T]

Lemmas SR-1/SR-2 at drain-v3 rigor: which teleport-blocked configurations yield which LP
rows (unclipped completable census, exact per-class lists; R1 excluded by InStratum-exact;
one pair per box and NOTHING else), the double-counting-safe tally Sigma m2 >= m, the
epsilon_box >= 3(lambda-1) bookkeeping, and the canary identity (Trump saturates the row
family with equality; the only sound v1-external refinement — CC-1(ii) corner-crowd
disjointness — needs a v2 threshold shape). NEW exact P-B scoping: compatible Trump-image
sets G_S = {id, diag} for k4_08 (TWO images — the A66 pilot declared one; a basin emission
must declare its G_S), {id} for k4_11, {diag} for k4_03, {} for corners4.

**Per-class verdict table (restricted strength; margins = value - threshold):**

| class | m | tau_2(beta) [M] | pair+stuck margin | basin reserve | mechanism |
|---|---|---|---|---|---|
| k4_08 | 7 | 21 + 6*beta exactly | -beta (LIVE) | +0.4 at gamma~0.1 (A66) | ghost = crowdfam, TL root deficient |
| k4_11 | 7 | 21 + 6*beta exactly | -beta (LIVE) | scoped: G_S = {id} [C not measured] | identical signature (A71 T2 run) |
| k4_03 | 5 | 21 + 4*beta exactly | -beta (LIVE) | scoped: G_S = {diag} [C not measured] | identical signature (A71 T2 run) |
| corners4 | 8 | beta=0: T3 below | T3 below | none (G_S empty) | no realisable family at all |

All three one-short critical classes show the SAME restricted signature: value = control
(crowdfam ghost), zero fractional excess, margin exactly -beta; adequacy tau_f_cat =
7.000000 converged per class; emptiness (beta = 0) dead per class (product witness >= 21).
The pair+stuckness formalism is kill-shaped at restricted strength across the whole
critical tier — and the full-quantifier residue is the T1 wall for each of them.

## T3 — corners4 solve wall: [T3 agent results below]

**The A66 solve-time wall is BROKEN [M]** (Opus chore; code/pairlp413.py + exactcert413.py,
results/pairlp_k4_13_a71.json, k4_13_cert_lower.json): solver switch (HiGHS options) +
support purging collapses A66's 17k x 10k simplex stall to a ~8-min CONVERGED cut loop:
beta = 0 restricted value = 20.528144, fine/exact Lmax = 1.000000 (the cut loop hit
viol = 0/0 at r40, "relaxation optimum == feasible objective").
**Exact certification [M exact]**: rounded support z (2650 pairs after the exact audit:
50 pairs / 1 square dropped by exact disjointness/core-freeness/containment re-checks,
min SAT gap 439/2372500), exact loads on 1271 cell-representative points: Lmax_exact =
62499/62500 < 1, certified lower bound tau_2(0) >= 4103377/200000 = 20.516885 (conditional
on cell-representative completeness — each load is exact, maximality over the continuum
rests on the representative construction; caveat recorded verbatim in the artifact).
**Adequacy twist [M]**: dual pricing exposed the A66 support catalog as NOT pair-adequate
(40% of the 1.74M enriched pair columns under-priced against the converged dual,
results/k4_13_dual_upper.json) — so the run GROWS the catalog by pricing: grow-0 converged
at 20.528144; grow-1 (304 placements / 20.4k pairs) 20.542 at budget (Lmax 1.12); further
grows in flight at session close. Every measurement sits >= 0.45 BELOW the line 21 with
~1e-2 movement per grow: **A66's bracket [14.89, 21.32] is effectively [20.52, ~20.6]; the
corners4 pair-emptiness route (Corollary P0) is OPEN at restricted strength** — NOT
refuted, NOT yet emitted; the adequacy-clean final value is the T3 artifact set. corners4 also carries the exact margin-wall
witness (V = 22 >= 21 at eta = 0.15, above) but with the SMALLEST shortfall (1 unit) and
0.47 restricted slack, no boxes to price (beta = 0), and a per-node cost without the
U-computation: it is the natural pair-certificate-v2 pilot. A restricted covering primal
(616 atoms, W2 = 20.325) is dumped as the emission seed
(results/pair_primal_k4_13_b0.json).

## Canary ledger (per run)

1. Emission runs: canary_trump.json [M]: the 60-digit Trump free-family, dilated by
   lambda = s0/s-hat, under A71 parameters (delta = 1/1000 slack cores, eps_box = 1/833):
   contained, core-free, pairwise closed-disjoint with min SAT gap 1.06e-7 = lambda - 1
   exactly as Lemma B.0(a) predicts, Sigma m2 = 6 = m: the exact death witness stands —
   no measure satisfying our row semantics can undercut trump5's threshold. SAFE.
2. eta-probes and wall witnesses are ADVERSARY-side statements (lower bounds on W2);
   strengthening the adversary can never kill the canary. SAFE.
3. T2 runs: value_ge_control TRUE at every cell; control families exact. SAFE.
4. stuck_rows.md sect. 5: the row family is saturated by Trump with equality [M]; no
   generic strengthening is sound — written down as a standing design constraint. SAFE.

## Residue (priced)

* Window pricing for a hypothetical k4_08 kill: ~38 sides at delta = 1e-3 (stride
  1 + delta/2.5 over [3.82, s0]); per-side cost = one full emission + verification —
  moot until the wall is broken.
* v2 verifier design requirements, priced by this campaign's measurements: margin-aware
  splitting (split toward the deficit, not the widest dim), one-sided/placement-dependent
  membership accounting, a compiled second implementation (wanted for the TCB anyway;
  1250x is the measured Python-Fractions/float-mock gap), and/or an analytic coverage
  clause (coverage proved by lemma over structured regions, boxes enumerated only near
  critical manifolds). [C]
* The measure-existence question (a PROOF that a W2 < 28 measure exists at full
  quantifier, without atom-by-atom exhibition) is now the mathematically interesting
  half; the canary theorem shapes what any such proof may use. [C]
