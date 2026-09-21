# A254 PEEL -- results

Note: `docs/proofs/peel.md`.  Tags [T] / [T-lit] / [T-computed] / [M] / [C] / [F].

## 1. What is proved (n-general)

* [T] BAND-COUNT (general): at s in (m-1, m), s > 2 + sqrt2, any packing has <= 4(m-2) band squares.
* [T, Lean theorem `core_fits`] PEEL-0: k core squares of a packing at side s pack at side s - 2; s >= 2 + s(k).
  No straddler => s >= 2 + s(n - 4(m-2)).  The tight flush pinwheel (four 1 x (m-2) blocks; hole + four isolated
  1 x (s-m+1) notches, NOTCH-NARROW) is this case.  HOLE-ONE = the case m = 4.
* [T] Lemma POKE (one vertex, depth <= (g/2) sin 2phi into a slot of width g < 1) and FLUSH-PEEL-g:
  on the whole flush stratum of RING(n), m >= 5:  s >= (s(n') + m + 1) / 2   (weaker; the brief's claim is [F] there).
* [T] m = 4: LIMIT-UNIQUE (the flush stratum of the all-ADJ family = the two tight pinwheels) + USC + HOLE-ONE:
  a NON-EFFECTIVE tau_0 > 0 with capacity <= 1 for every all-ADJ ring with all eight tilts < tau_0, all 17 coordinates.
* [T] + [T-computed m = 3..6] the count: FAMILY-STUCK needs n >= 4(m-2) + 1, attained at the incidence level by
  ring + ONE poker in any narrow ribbon (bare ring: Hall minimum 0; wide-overlap poker: 0).  `cells254.json`.

## 2. What is conditional

[C] ONLY-RING(n) + [C] MONOTONE-ROOM(n)  =>  no family-stuck packing below 2 + s(n - 4(m-2))  (Lean `peel_excludes`).
Neither is proved for any n.  MONOTONE-ROOM(n) has a named failure mode for m >= 5 (slack rings).  The missing
quantitative statement is QUANT-ROOM(n) (peel.md s.3).

## 3. The table (`peel254_table.md`, `peel254_table.jsonl`; 36 values n <= 100 below ceil sqrt n)

| verdict on the tight pinwheel | count | n |
|---|---|---|
| THEOREM-WINDOW (2 + proved LB(n') >= m) | 6 | 5, 10, 11, 18, 19, 29 |
| THEOREM-AT-RECORD (rec(n) < 2 + proved LB(n') < m) | 3 | 17, 26, 27 |
| RECORDS-ONLY (needs rec(n') optimal) | 26 | 28, 37-41, 50-55, 65-71, 82, 83, 85-89 |
| EQUALITY (2 + rec(n') = rec(n)) | 1 | 84 |
| NOT-EXCLUDED | 0 | - |

With the lab's certified s(11) >= 3.82 in place of Stromquist's 3.7889 no verdict changes (n = 28 needs s(12) > 3.8244).

## 4. n = 11

PEEL at the tight pinwheel = A253's HOLE-ONE certificate.  New: the neighbourhood theorem (s.1, fourth bullet).
RING-POKER-RESIDUAL(11) NOT closed: the remaining case is {all-ADJ rings with some tilt >= tau_0}, tau_0 not explicit;
ONLY-RING(11) untouched.  k0_00 unchanged.

## 5. Wrong in the brief

1. n = 65 is NOT an equality: rec(65) = 5 + 5/sqrt2 = 8.535534 < 2 + rec(37) = 8.598620.  The equality is n = 84.
2. 28, 37, 38, 50 are excluded only GIVEN records at n' = 12, 17, 18, 26; by theorem: 5, 10, 11, 17, 18, 19, 26, 27, 29.
3. "The flush limit of the general ring is the pinwheel": true at m = 4 only; for m >= 5 the flush stratum has slack.

## 6. search254 [M]

Detached ladder (n = 5, 10, 17; four sides each; 6 starts; basin hopping): `search254.md` / `search254.jsonl` are
written and committed by `run254.sh search` when it ends.  Small budget: a failure to find is not evidence.

## 7. Tests, pages

`test254.py`: POKE 27 822 fitting squares / 0 violations; HOLE-POKE f(w) < 1 on the grid; pinwheel pocket
decomposition m = 4..8 (shapely, 5 components, exact areas).  Pages `docs/residue_map/campaigns/A254-peel/`:
`peel_n17.svg` (17 squares, least SAT gap -4e-16), `peel_n65.svg` (65 squares, -9e-16; record-side hole grey stipple),
`peel_n84.svg` (84 squares, -2e-15): every panel asserted containment and pairwise gap >= -1e-9.
