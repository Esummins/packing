# A74 — mixed-depth emission: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [M] measured/computed exact, [F] float evidence, [C] open.
Successor to A73 (v2 verifiers + Lemma W' + the tangency trap).
BRIEF: attempts/A74-mixed-depth/BRIEF.md.  STATUS: IN PROGRESS.

## T1 — the mixed-depth emission loop (corners4, beta=0)

Design (from Lemma W' accounting): rows offered at depth levels
eta in {0.05, 0.02, 0.008, 0.002} simultaneously, each level's own arrangement
(of the eta-shrunk squares); row (c,d,l) priced into the adversary LP at
rhs_l = 1 + mu*(eta_max - eta_l)/(eta_max - eta_min) (deepest free, shallowest
+mu).  The DUAL then minimises the depth-priced covering cost subject to
A^T y >= 1 over every catalog pair, so dual mass sits deep except where
shallow service is forced — the per-level dual mass histogram is the measured
mixed-depth law.  W2_emitted = sum y <= LP value, so LP value < 21 certifies
the restricted measure is under threshold.  Consolidation: rows with dual
weight under a rising floor are dropped and the LP re-solved (duty
redistributes onto fat rows), accepted while value < guard; fewer, fatter
atoms is the objective (A73 fragmentation finding).  Soundness is entirely
delegated to the frozen v2 verifiers; the LP needs only dual feasibility
(automatic at optimality — all catalog pairs are columns).

Machinery: code/pairlp413m.py (imports the frozen A73 pairlp413e for
geometry/catalog; sets its ETA per level), code/emit413m.py (canary inside),
code/loop413m.py (LP -> emit -> Rust survey --jobs 8 -> definitive rows grow
the catalog).  seg_cap raised to 2e6: the 404-square catalog's edge
intersections (~107-127k per level) are now IN the point families
(A71/A73 had skipped=True — their families were vertex+grid only).

(measurements as runs land)

## Canary

Per-run rows in notes/ledger.md; results/canary_trump.json.

## Interim measurements (md1-md3, 2026-09-02)

* [M] Dual seeding works: re-membershipping the A73 uniform-eta duals' binding
  point pairs (eta001/002/005, ~350 rows each) at all 4 levels opens the cut
  loop at value 21.57 (vs 22.2 after 15 fresh rounds) — the binding frontier
  structure transfers across depth semantics.
* [M] Gate identity: the certificate gate is W2 = sum y (unpriced dual mass),
  not the depth-priced LP value; measured gap at mu=0.01 was 0.16 (21.40
  priced vs 21.24 W2, md1).  Emission verdicts now read W2.
* [M] Trajectory (md3, IPM+crossover rounds ~160s each, kOptimal duals):
  W2 = 21.41 (seed-only) -> 21.34 -> 21.30 -> 21.17 over 5 rounds, ~0.06-0.09
  per clean round, decelerating.  The mixed-depth restricted optimum is close
  to 21 from above at this budget; UNDER/OVER not yet resolved.
* [engineering] Two artifact classes fixed in the rig: (i) IPM-no-crossover
  solves at nnz > ~10M time out with NO feasible iterate (kTimeLimit breaks
  the loop) — solved by running IPM+crossover every round (~200s, kOptimal,
  exact duals); (ii) purging can drop a pair's only covering row, the pair's
  z column runs to its bound, and the "dual mass" then undercounts while the
  dual is NOT a covering (uncovered pair) — W2 gates now require n_ub = 0 and
  the final solve rebuilds over the WHOLE row store.

## Results (2026-09-02, runs md5/md7 + hinted surveys)

### [M] The first sub-threshold corners4 measures (restricted, mixed-depth)

| run | depth menu (eta) | mu | exact full-store W2 | atoms (consolidated) | per-level mass 0.05 / 0.02 / 0.008 / 0.002 / 0.0005 |
|---|---|---|---|---|---|
| md5 | 0.05, 0.02, 0.008, 0.002 | 0.01 | **20.98857** | 461 (from 10424 rows) | 0.87 / 7.29 / 7.55 / 5.28 / — |
| md7 | + 0.0005 | 0.01 | **20.95955** | 353 (from ~9k rows) | 0.59 / 6.98 / 7.41 / 5.10 / 0.87 |
| md6 | + 0.0005 | 0.30 | rising 21.31 -> 21.55 (killed r3) | — | strong pricing SPENDS W2 to buy depth |

Both md5 and md7 are P1'-valid (W2 < 21) covering measures on the 404-placement
A71 colgen catalog (+ control columns), every atom >= its level's eta deep in
every square its row serves (tangency trap closed by construction), Trump canary
SAFE at every emission (notes/ledger.md).  Certificates:
certs/pair_k4_13_s0_b0_md5.json, certs/pair_k4_13_s0_b0_md7.json.

### [M] The mixed-depth law on this catalog (W-double-prime, restricted form)

* The restricted covering optimum is pinned to the threshold from below: the
  slack 21 - W2 is 0.011 at floor eta = 0.002 and 0.040 at floor 0.0005; the
  sharp (eta -> 0) A71 value is 20.528.  I.e. of the 0.47 budget between the
  sharp optimum and the threshold, ~0.43 is consumed by requiring every atom to
  be >= 0.0005 deep and ~0.46 by >= 0.002 deep.  The forced profile is NOT
  "bulk deep + a thin shallow stratum": the LP puts ~70% of the mass at
  0.008-0.02 and ~25% at 0.002, only 3-4% at 0.05 — consistent with Lemma W'
  (eta = 0.1 dead, >= 13 forced sub-0.1 units) and with the A73 bracket
  eta* in (0.006, 0.05): at mu = 0.01 pricing the bulk sits just below eta*.
* Depth pricing costs W2 one-for-one: at mu = 0.3 the dual mass RISES above 21
  (21.31 -> 21.55 while rows are added) — there is no slack to buy depth.  The
  same slack budget is what consolidation spends: md5's consolidation was
  accepted down to 470 rows (W2 20.9886) and REJECTED at the next floor
  (398 rows, W2 21.0026); md7's to 355 rows (20.9595), rejected at 271 rows
  (21.0517).  Fewer/fatter atoms and deeper atoms compete for the same
  ~0.01-0.04.
* Consequence for verification (measured, Rust verify_pair2 --jobs 8, depth 34,
  2M nodes, survey): md5 unhinted -> FAIL by cap only, 0 definitive rows, 300
  cap witnesses all at depth 34 with certain mass median 0.845 (min 0.68); the
  verifier's own splitter had driven factor A to widths 2e-4..7e-4 while factor
  B's tilt interval was UNSPLIT ([0,1]) in all 300 — the residue is tilt
  uncertainty in the un-split factor, not the atom margins.

### [M] Hint trees (spec s4) change the search shape — and expose the holes

code/hinttree.py: emitter-side float B&B, cut chosen by max-min lookahead
over the 6 midpoint cuts (the cut whose WORSE child keeps the most
float-certain mass), COVERED leaves where float certain mass >= 1, empty nodes
(verifier fallback) at EXEMPT/NONDISJOINT pre-screens, the per-root cap, or
possible-mass < 1.  Verifier untouched; hints re-proved exactly.

* 30 nodes/root (3.9k nodes, 12 s): Rust accepts (hinted=true, hint_misses 0);
  at 200k nodes the cap witnesses carry 99.8% certain mass (deficit 0.002)
  vs the unhinted 84.5% median.
* 3000 nodes/root (237k hint nodes, 5.9k float-COVERED leaves, 82 MB cert,
  615 s): at 2M nodes, COVERED 106.8k (vs 98.6k), COVERED-F 6.0k (vs 33.7k),
  hint_misses 1493, and DEFICIENT-EARLY fired 7317 times: exact rational
  counterexample rows (admissible, core-free, interior-disjoint placement
  pairs collecting < 1) EXIST for the md5 measure — the continuum between the
  404 catalog placements has holes the unhinted search never probed (0
  definitive rows).  This is the survey loop's row source working as designed;
  the harvest (--faildump 30000) and the grown-catalog re-solve are the next
  iteration (md8).

### [M] Loop iteration 2 (md8 = md7 menu on the catalog grown by the 65 harvested placements)

* LP: W2 = 20.95828 (363 atoms), profile 0.61 / 6.81 / 7.47 / 5.23 / 0.84 — the
  65 exact-hole placements cost ~0.001: catalog growth is not the constraint.
* Hinted harvest (3000 nodes/root tree, 1M nodes, depth 34, jobs 8), same budget
  as the md5 harvest: DEFICIENT-EARLY 220 -> 57, stored definitive rows 67 -> 2,
  shallowest hole 0.948 -> 0.964 collected.  The survey loop converges ~4x per
  iteration at this budget (counts vary with the parallel traversal order:
  the md5 2M-node run reported 7317, its 1M-node harvest 220).  Cap witnesses
  still dominate at depth 34; no PASS.  Per iteration ~1 h wall.
* Hinted certificates (82 MB) are NOT committed; regenerate with
  `python code/hinttree.py certs/pair_k4_13_s0_b0_md8.json OUT --cap 3000 --maxdepth 44`.

## Status at close (2026-09-02)

T1: NO verified corners4 certificate.  Delivered instead: the mixed-depth
emission loop (working end to end against the frozen Rust verifier), the first
sub-threshold restricted measures (md5/md7/md8), Lemma W'' (the measured law:
slack, forced profile, depth-vs-consolidation competition, free catalog growth),
the verification residue diagnosis (un-split factor tilt) and the hint-tree
remedy with a converging hole count.  T2 skipped per BRIEF.  Next: continue the
loop (md8 -> harvest -> md9 ...) until the hinted survey is cap-only, then the
certification run at a node budget set by the cap-witness depth profile;
consider a verifier-side (versioned, both implementations) split heuristic
that never leaves a factor's tilt interval unsplit — an efficiency change, not
a soundness one, so it needs the erratum discipline only if the spec's s6
guidance is changed.
