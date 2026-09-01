# A53 verification log (exact claims and their arbiters)

- V1 (slot grid closure): no two slot values differ by exactly 1 across L/R families at
  s0 = 969271/250000 — exact Fraction check in code/skeletons.py (assert), rerun 2026-08-31. PASS.
- V2 (census, recursive def): 7204 recursively-locked sets, 944 D4 classes; BFS over exact
  rational slots, dedup by frozenset; Trump's set present and lockable. code/skeletons.py. PASS.
- V3 (census, PI/Young def — PRIMARY): 1110 4-tuples of Young diagrams in 3x3 with exactly
  disjoint slot unions; 163 D4 classes; census by k = {0:1, 1:1, 2:3, 3:6, 4:14, 5:22, 6:33,
  7:35, 8:30, 9:18}; every Young union is recursively locked (inclusion verified set-by-set);
  6094 BFS sets are NOT Young (the definitions are inequivalent — witness in notes/lemmas.md L1).
  code/skeletons2.py. PASS.
- V4 (Trump k = 5): certified from A03's 60-digit exact data (contacts rigid, minpolys):
  uprights 0,1,2,3,5 simple; square 4 epsilon-off with eps = 0.0325583143496147870... (> 1e-2
  margin vs both candidate slots; cy has degree-7 minimal polynomial, hence not rational and not
  at any slot); tilted 6-10 non-simple by orientation. code/trump_k.py -> results/trump_k.json. PASS.
- V5 (blocked slide): square 7's leftmost corner at (0.98404, 2.01903) lies inside square 4's
  landing corridor [0,1] x [2, 2.032558]; intrusion depth 0.01353 below square 4's bottom edge.
  60-digit data, margins > 1e-2. Recorded in lemmas.md L4. PASS.
- V6 (trump5 stratum unkillable): Trump's six free squares, embedded at s0 with BR/TR pins moved
  outward 4.1e-7, are admissible, pairwise disjoint (min SAT gap -1e-15 = exact touch), disjoint
  from all five pins (min gaps +3.3e-2, +6.4e-1, -1.1e-15, 0, +5.8e-7, +2.3e-1), and KEPT by the
  LP row filter => true residual tau* >= 6. code/check_trump_feasible.py. PASS (float with 1e-9
  slack on exact-touch contacts; the underlying contacts are exact by A03 rigidity).
- V7 (LP kill arbiters): every kill claimed in the eta_residual table carries an exact rational
  measure certificate verified by code/verify_case.py (A38 copy, unmodified) — interval B&B over
  (t, cx, cy), witnesses exact; certificates in certs_wip/. Status per node in results/eta_table.md.
  FINAL COUNTS (2026-08-31): k=6: 32/33 PASS (open: k6_23, LP-dead 4.9337, best witness residue
  0.994771 after 8 witness-feedback rounds at scale 1.011); k=5 non-Trump: 18/21 PASS (open:
  k5_11 no-margin 5.9051, k5_13 cert FAIL 5.6774, k5_16 no-margin 5.98951). Trump5 and corners4
  deliberately uncertified (provably/measured alive). Cert cost: 44 of the passes at 1-60 s,
  hard Trump-adjacent ones 76-607 s (witness loops); atom counts 3-93, median ~5.
- V9 (cap closure, measured): every k=7 Young class contains >= 1 CERTIFIED k=6 sub-tuple
  (combinatorial check over the exact census with the 32 certified classes; 0 exceptions),
  and containment is transitive to k=8,9 => all k>=7 strata certifiably empty. PASS.
- V8 (cap logic): killing all k = 6 classes kills every k >= 6 stratum — proof in lemmas.md L5
  (Young-tuple downward closure; removing a maximal cell preserves Young-ness). THEORY, no compute.
