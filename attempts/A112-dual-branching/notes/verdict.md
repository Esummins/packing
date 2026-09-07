# A112 — verdict: what the region tree does, per region and per branching order

All numbers below are `results/t3_m2.json` / `notes/t2_table.md`, produced by
`code/t3_112.py` from the per-node records under `results/rt_m2/` (S02) and `results/rt_m2k0/`
(k0). Every LP ran under the PI's two-stage timeout protocol and **every kill is a certified PASS
of the frozen `verify_case.py`, a free (logic) kill, or nothing** — τ is never a verdict.

## 1. One line per region set

**S02 (A57 levels 2–3, 17 regions).** The region tree with ordering **`loadpath`** terminates in
**77 nodes / 56 LPs / 2 439 s of LP + 631 s of certification** against the old tree's projected
**671 nodes / 671 LPs / 194 602 s**, and **kills 9 old boxes** (of which **6 were already dead by
A96's T5″ trim at the root** and **3 are new**: one free at the root, two by a certified 3-node
region tree). `wastage` and `hybrid` kill the same 9 (`hybrid` 13 certificates, 3 of them FAIL);
`stranded` kills 8. Head to head on the 10 regions where the four orderings differ at all:
**hybrid 4, stranded 3, loadpath 2, wastage 1** — no ordering dominates, and the spread in nodes to
termination is small (73–77 nodes over the whole set).

**k0 (A113's un-killable level-1 cells, 6 regions).** No ordering kills anything:
**0 regions / 0 certificates / 0 logic kills** in 17–28 nodes and 2 854–3 938 s of LP each. The
reason is measured, not a cap artefact: **every one of the 60 k0 LPs lands at η = 0 exactly** (47 of
them to the last digit, none at η ≤ −10⁻³), so the certifier is never even invoked. Removing one
support placement from a k0 cell does not move τ. Head to head: hybrid 3, stranded 2, loadpath 1.

## 2. The two things that actually kill, and the one that does not

| what killed a leaf | S02, all four orderings | cost |
|---|---|---|
| frozen `verify_case.py` PASS | **45** (35 NO children, 10 YES children); 9 FAIL | median 11 s, mean 100 s, max 479 s |
| free pair kill / T5″ trim | **38** (24 root T5″-trim, 14 by Lemma TC) | ~0 s |
| chain LP (A111's GRAIN-LP at s0) | **0** | ~0 s, never fired |
| still open at the node/wall cap | 214 | — |

**The free kill that fires is Lemma TC, not CORE-MEET.** All 10 recorded pair-kill fires are TC;
CORE-MEET fired zero times. Four of them are the *new* object A112 was built to produce — **a
collision between two boxes the region tree itself introduced** (`bin1` vs `bin2`/`bin3` at depths
2–4 of `k5_11_interior_Y0036_D07_D03`, `k5_16_interior_Y0083_D02/D03`, `k5_16_interior_Y0119_D07`).
Four more are `bin0` vs `pin3` at the root of `k5_11_interior_Y0041_D02`, i.e. a whole A57 open box
killed for free by a rule A57 does not apply at emission. Every fire passed dense sampling
(20 000 resampled pose pairs, independent seed, **0 counterexamples**, worst SAT gap −0.0066).

**The chain kill never fired inside a region tree**, although its controls are clean: on A111's own
S02 boxes it fires at r = 0.005 and 0.002 and not at r ≥ 0.0097 (reproducing A111's
`r < s* − s0 = 0.0097` threshold from the other side) and it refuses Trump at every radius. The
region trees simply never got small enough: the deepest processed node is depth 4 (r = 0.00625,
one node), and 79 of the processed nodes sit at depth 3 (r = 0.0125) — just above the threshold.

**The structural asymmetry, measured.** Of 126 YES-child LPs, **116 (92 %) land at η = 0 exactly**:
the branch box sits on the parent's own LP support, so conditioning one more square there usually
costs exactly one unit of budget and buys exactly one unit of τ. Of 104 NO-child LPs, 44 (42 %) go
below budget, down to η = −1.0. **The NO side is where the killing happens and the YES side has to
be killed for free** — which is A111's conclusion, now measured inside a tree rather than at a
single node. The 10 YES children that *did* certify are the exception that makes the branch work at
all: both of A112's genuine kills are (YES certified) ∧ (NO certified).

## 3. The two genuine kills, end to end

```
k5_11_interior_Y0108_D07  (A57 level 2, k5_11, S02-explained, tau0 = 4.3333 unconverged)
  R    root  split on the S02 f3 load-path location (2.6202, 2.4332, 47.25 deg), r = 0.1, rho = 10
  RY   YES   tau 3.500000  eta -0.500000  converged  (34 s)   -> frozen verify_case PASS   (5 s)
  RN   NO    tau 4.285714  eta -0.714286  UNCONVERGED (254 s) -> frozen verify_case PASS (309 s)
  => 3 nodes, 2 LPs, 289 s LP + 314 s certify = 603 s   (old tree: 56.6 children, 16 426 s)
```

`k5_11_interior_Y0084_D03` dies the same way (3 nodes, 2 LPs, 285–304 s LP, 17–275 s certify,
2/2 certificates) under all four orderings. `k5_11_interior_Y0041_D02` dies at the root for free
(Lemma TC, bin vs pin, 0 LPs, 0 certificates) under all four.

Note the second line: **the NO child was still unconverged when it was certified, and the
certificate PASSed.** That is exactly the protocol's premise, and it is where the wall saving comes
from.

## 4. The timeout protocol, priced

| | S02 | k0 |
|---|---|---|
| LP wall under the protocol (240 s stage 1, certify at η ≤ −10⁻³, 900 s only on the knife edge) | **12 609 s** | 14 313 s |
| LP wall the same nodes would have cost under a flat 900 s cap | **28 518 s** | 15 204 s |
| factor | **2.26×** | 1.06× |
| per LP | 55 s vs 124 s (230 LPs) | 239 s vs 253 s (60 LPs) |

Certification adds 631–1 807 s per ordering on S02 (54 certificates, mean 100 s) and 0 s on k0.
So on S02 the protocol's total (LP + certify) is **3 070–5 821 s per ordering against 6 105–8 267 s
of LP alone** under a flat cap — the certifier is cheaper than the LP time it replaces. On k0 the
protocol saves nothing, because no k0 node is ever below budget: there is nothing to certify early
and every node runs the full escalation.

**η does not predict the certificate here.** PASSes span η ∈ [−1.0, −0.25]; FAILs span
[−0.714, −0.160]. A111's rule of thumb ("every child with η ≤ −0.5 passed") does not survive: two
FAILs sit at η = −0.667 and −0.714. The certificate really is the arbiter.

## 5. Pin wastage vs row mass (PI question)

Per branching node, over that node's full candidate list, Spearman's ρ between the **pin-wastage**
score (area of the pockets the candidate box creates against the pins, the walls and the other
conditioned boxes — pure geometry, no LP) and the **row-mass** score (the LP row mass the candidate's
YES core strikes out):

| region set | n nodes | median ρ | mean ρ | range | ρ > 0 |
|---|---|---|---|---|---|
| S02 | 45 | **+0.468** | +0.414 | [−0.408, +0.884] | 84 % |
| k0 | 34 | **+0.425** | +0.340 | [−0.370, +0.831] | 82 % |

They agree in direction on four nodes in five and disagree outright on one in six, so **pin wastage
is a genuinely different ranking, not a proxy for row mass** — which is why it wins some regions
(`k5_11_interior_Y0036_D07_D06`) and loses others. As a branching order it is neither better nor
worse than the other three at this sample size: 1 win of 10 on S02, 0 of 6 on k0, and it kills the
same 9 S02 regions as `loadpath` and `hybrid`.

## 6. Where the region tree stops, and why

Nine of the eleven non-trivial S02 regions and all six k0 cells end **CAP-UNPROCESSED at 8 nodes**
(S02) or 2–6 nodes (k0). The binding constraint is the wall (900 s / 600 s per tree), not the node
cap or the depth cap: at 240 s of stage-1 LP plus a certificate per below-budget node, a tree
affords 2–7 LPs. On the evidence above, a tree that is given depth 5–6 at r ≤ 0.006 would put the
chain kill in range on the YES spine; that is the single most promising extension and it is a wall
question, not a method question.

## 7. Integration into A96's driver

Add a resumable **`--region-tree`** option to A96's scheduler (`shadow_sched.py` / `tree57.py`'s
child loop):

1. **Trigger.** A node that reaches ALIVE-at-LP for the second time, or is still unconverged at the
   900 s re-check, is handed to `regiontree.Runner` instead of being split into 8 children.
2. **Budget.** The runner takes a wall cap `W` and a node cap `N`; the measurement above says
   `W ≈ 900 s, N = 8` reaches depth 3 and kills 2 of 11, and that the interesting setting is larger
   `W` with `depth_cap ≥ 5`. If the runner does not return `transfers = True` inside `W`, the
   scheduler falls through to the ordinary 8-way split and **nothing is lost** — the region tree's
   cost is bounded by `W` and its per-node records stay on disk for a later, deeper retry.
3. **Ordering.** Take `loadpath` where the node has a matched shadow with a known load path (S02 /
   S07 today) and `hybrid` otherwise; the four orderings are within 5 % of each other in nodes to
   termination, so this is a tie-break, not a lever.
4. **Resumability.** Already there: one record file per region-tree node
   (`results/rt/<region>/<ordering>/<key>.json`), atomic writes, and a region skipped if it is
   already in the sink. It resumes at the same granularity as A96's own driver and honours the same
   PAUSE sentinel discipline (a killed run loses at most the node in flight).
5. **What it emits.** Per killed region, the `containment` record — C1 (the root hypothesis is
   byte-identical to the campaign's own), C2 (every split's two children carry the same box F, one
   as a core box at budget − 1 and one as its NO-family), C3 (every leaf dead) — plus one frozen
   certificate per LP-dead leaf. All 9+ killed regions passed **C1 ∧ C2 ∧ C3 with zero failures**.

## 8. Certificate accounting

* **Per kill:** one frozen `verify_case.py` certificate per LP-dead leaf, at the **fixed side** s₀.
  A 3-node kill costs 2 certificates (one YES core-box, one NO-family). Free (logic) kills cost none.
* **The window claim ×4.** `verify_param.py` raises `nofams unsupported` (line 529), so every
  NO-child certificate is a fixed-side object and A57's four-side slack-core grid multiplies it by
  four. The YES-child certificate is an ordinary core-box certificate `verify_param` already
  accepts, so the multiplier applies to **half** the certificates of a 3-node kill.
  Cost to remove it: **≈ 90–120 lines** in one new frozen verifier version (`NoFamP`, a Fraction
  interval containment predicate, one `SCell` field, one hook in `PVerifier.exempt`, the loader, one
  selftest arm) and **one Lean lemma parallel to the existing core-exemption clause** — the clause
  itself is already what the frozen fixed-side verifier discharges. Zero regression surface (no
  emitted certificate contains a nofam today). Full spec in `notes/verify_param_nofams.md`.
* **A new obligation A112 does incur: Lemma TC as a kill rule.** All 14 of A112's free kills at
  non-root nodes are TC (tilt coupling), and the ledger currently keeps TC as "the O(1) pre-screen",
  not as a deployed kill. Deploying the region tree's free kills therefore needs
  `tilt_coupling` (A111 `leaf_shape.md`: two disjoint unit squares with tilt gap D have centres
  ≥ (1 + cos D + sin D)/2 apart) as a certified leaf — a two-line `nlinarith`, but a *named* one.
  CORE-MEET/T5 and T5″ are already in the TCB and need nothing.
* **The chain kill is NOT certified.** `regiontree.chain_kill` is a float LP; it is recorded as
  `DEAD-CHAIN-LP` with `certified: false` and it fired zero times, so nothing in this attempt rests
  on it. Certifying it is A111's leaf O1–O4 (selection census, tilt cover, affine relaxation, one
  Farkas certificate per cell).
* **The k0 YES-side shortcut is NOT taken.** A YES box inside a slot cell does not imply k ≥ 1:
  A53 stratifies by **grid-locked** (doubly flush, wall-anchored) squares, which box containment
  cannot give. 37 such opportunities were recorded across the k0 trees, and only **6 of them even
  have a near-axis ("simple") tilt**, so the sound form — K0-FREE/teleport applied to the LP support,
  which is what `residue_ledger` §4 actually licenses — would be worth at most 6 of 37 free YES
  children even before the grid-lock obligation is discharged.

## 9. Canaries

* **Trump's grain is never killed.** `substrat.trump_realizes` evaluated on **every** hypothesis
  A112 declared dead: **0 violations**. No S07 branch is taken at level 1 (the region set is
  S02-explained A57 nodes at levels 2–3 and k0 cells).
* **Dense sampling.** 10 free-kill fires re-checked with an independent seed at 2 000 pairs each:
  **20 000 sampled pose pairs, 0 counterexamples, worst SAT gap −0.0066** (every sampled pair
  strictly overlapping). No LP-free count in this report was written before that check ran.
* **A111's two end-to-end kills reproduced: 11/11 certificates PASS.** A112's byte-identical frozen
  `verify_case.py` (sha256 `521cb01f…`, `--depth 56 --jobs 1`) was run on A111's own emitted
  certificates: `k5_11_interior_Y0054_D00` **5/5 → node dies**, `k5_16_interior_Y0984` **6/6 → node
  dies**, in 1.7–36 s each (`results/canary_replay.json`).

  **A finding worth banking, from the failed first attempt at this canary.** Re-running the whole
  `certify.py` pipeline (rather than replaying the certificate) gave 4/5 on `Y0054_D00` at a 300 s
  certificate cap and *still* 4/5 at 900 s. The cause is not the verifier: `certify.py --loop_cols`
  **re-solves the node LP under a time limit before emitting the certificate**, so the certificate's
  atom set is wall-clock dependent — A111's PASSing NO1 certificate has 76 atoms, the 900 s re-run
  produced 100 atoms and a different (unverifiable) certificate. **The frozen verifier is
  deterministic; the certificate-emission pipeline is not.** Reproducing a kill therefore means
  replaying its certificate, and a certificate that FAILs on re-emission is not evidence that the
  original kill was wrong. (`logs/canary_retry.out`, `certs/…__retry900.json`.)
