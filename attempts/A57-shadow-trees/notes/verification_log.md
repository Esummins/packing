# A57 verification log

Every entry is a thing a machine checked, with the command and the artefact.  τ is never an
arbiter (A54 S0); the arbiters are `verify_case.py` (kills) and `alivewitness.py` (unkillability).

## V1 — verifier self-test on this machine

    python code/verify_case.py --selftest
    → selftest: 3000 random boxes, 0 problems      (int vs Fraction predicate cross-check)

## V2 — the two interior NO-children, certified and INDEPENDENTLY re-verified at depth 60

    python code/verify_case.py certs/tree/k5_11_interior_L1/k5_11_interior_NO.json --jobs 2 --depth 60 --report
    python code/verify_case.py certs/tree/k5_16_interior_L1/k5_16_interior_NO.json --jobs 2 --depth 60 --report

| node | atoms | total | budget | boxes | covered | exempt (core/nofam) | max depth | time | result |
|---|---|---|---|---|---|---|---|---|---|
| k5_11_interior_NO | 3 | 21/5 = 4.2 | 6 | 8568 | 3020 | 1296 (1079/217) | 33 | 0.5 s | **PASS** |
| k5_16_interior_NO | 3 | 21/5 = 4.2 | 6 | 6986 | 1813 | 1712 (1565/147) | 27 | 0.5 s | **PASS** |

Reports: `certs/tree/<key>/<id>.report.json`.  Both were produced in-loop by `certify.py` at
scale 1.40 and re-verified afterwards at a deeper bound with a fresh process.

## V3 — Trump canary, twice

1. `substrat.trump_realizes` on every A57 child before certification: 0 children of either
   interior cover are Trump-realizable (correct — neither stratum is; A54 S4).  `ladder57.py`
   hard-refuses `--name trump5` (exit 5).  trump5 was never solved, never certified.
2. **Canary strengthened** (T8): `alivewitness.py` on Trump's six free squares, scaled to s0 by
   λ = s0/s_T, returns ALIVE-CERTIFIED with an exact strictly positive min gap
   `144937745660574462730629449381/1370664603569846904878201000000000000 = 1.0574e-7`
   → `results/alive/trump5_strict.json`.  Fed the *unscaled* placements the same checker returns
   NO-WITNESS (a −2.5e-7 core gap after rational snapping), i.e. it refuses touching families —
   the conservatism is in the safe direction.

## V4 — pinguard census (soundness gate, T5)

    python -c "... build_children(nm,'interior',0.15,8,0.6,0.34) ; classify(...)"

| stratum | cover boxes | contradictory | ok | parent (unsound at reduced budget) |
|---|---|---|---|---|
| k5_11 | 1152 | 344 | 808 | 0 |
| k5_16 | 1152 | 257 | 895 | 0 |

Zero `parent` boxes in the interior, so no A57 interior child is certified at an unsound budget.

## V5 — cover completeness

`tree57.py --plan_only` for both strata: 1153 children, **0 uncoverable boxes** (every kept box
has a non-empty rational core), a uniform over the cover to 4e-8 (0.35660160 … 0.35660165).
The driver exits with code 4 rather than run if any box lacks a rational core.

## V6 — a-curve convergence (T6)

`code/probe2.py`, k5_16, centre (2.0084, 2.0084), θ ≈ 86°:
a = 0.35645 / 0.44677 / 0.48902 → τ = 3.000000 each, **converged** (minmass = 1.000000,
maxcov = 1.000000, 3 atoms), 14.8 s / 1.3 s / 1.2 s.  Artefacts `results/acurve_k5_16_ok*.json`.

## V7 — retraction

The first a-curve (`results/acurve_k5_16_a35/a45/a49.json`, centre (1.17, 1.17)) reported
τ = 5.000000 = budget and was briefly written up as a structural no-go.  V4 shows that box is
**contradictory**; the reading is withdrawn (T6b keeps it as the recorded trap).

## V8 — the level-1 resister and its depth-2 disposal (T11)

`k5_16_interior_Y0017` converged at τ = 5.000000000000014 = budget (minmass = 1, maxcov = 1,
8.7 s, pinguard **ok**) — a genuine level-1 obstruction.

* **EPS_CORE ladder, rejected by measurement.** `code/epsladder.py --eps 5e-4`:
  τ = 4.799999999999993, η = −0.200 → `certify.py` round 0 at scale 1.0386, total 4.98541 < 5 →
  verifier **FAIL**: 32 witness boxes, 19 exact holes, worst mass 415451/1000000 = 0.4155 at
  θ = 9.509991°, centre (1.578909244, 1.454551946); the witness re-solve returns τ = 5.00000.
  Artefact `results/epsladder_k5_16_interior_Y0017.json`.  Conclusion: the 2e-3 shell rows are
  genuinely required at this child, so τ* = budget is real and the lever is off by default.
* **Depth 2, works — 8/8.** `code/deepen.py --key k5_16_interior_L1 --levels 3`: 8 sub-boxes,
  a = 0.4233–0.4249, each at the **same** budget 5, **all eight certified** — four at
  τ = 4.000000 (η = −1.000), three at τ = 3.000000 (η = −2.000), one at τ = 3.500000
  (η = −1.500); LP 14.0–84.2 s each, 322 s total.  Certificates + `.PASS` in
  `certs/tree/k5_16_interior_L1_D2/`, records in `results/tree_k5_16_interior_L1_D2.jsonl`.
  The parent's τ = budget does not survive a single bisection.
* `k5_16_interior_Y0041` (τ = 5.000000, `certify.py` rc = 3) is the same class; `deepen.py` was
  extended to take cert-FAIL records as well as ALIVE-at-LP ones.

## V9 — live scoreboard at hand-off (2026-09-01 10:30 PDT)

| key | exact-cert kills | logic kills | alive-at-LP | cert FAIL | planned |
|---|---|---|---|---|---|
| k5_11_interior_L1 | 4 | 4 | 1 (queued for D2) | 0 | 1153 |
| k5_16_interior_L1 | 5 | 3 | 1 (queued for D2) | 1 (queued for D2) | 1153 |
| k5_16_interior_L1_D2 | 3 | 0 | 0 | 0 | 8 per resister |

No child is unresolved: every non-PASS record is queued for depth 2, which has so far killed
everything it touched.

## V10 — T14: `k5_11_interior_Y0107`, boundary degeneracy

    python code/verify_case.py certs/tree/.../k5_11_interior_Y0107.json --depth 56 / 64 / 72
      -> FAIL each time: 0 HOLES, 8 undecided at this depth, max depth used = the cap;
         boxes 30423 (d64) / 31373 (d72); cluster theta~53 deg centre~(1.80,2.40), min mass 1.246505

    python code/certify.py results/tree/.../k5_11_interior_Y0107.json --s_rat 969271/250000 \
        --eps_geo 0.002 --rounds 3 --jobs 3 --depth 60 --out certs/epsgeo/k5_11_interior_Y0107.json
      -> tau = 4.571429, total 4985907/1000000 = 4.985907 < 5, 99 atoms, PASS at round 0

    python code/verify_case.py certs/epsgeo/k5_11_interior_Y0107.json --jobs 3 --depth 60 --report
      -> PASS, 144246 boxes, covered 47742, exempt 24413 (core), 147256 exact atom checks,
         max depth used 32, 4.1 s

The scoreboard record was superseded by an appended corrected line (board.py keeps the last
record per id); `results/tree_k5_11_interior_L1_s0.jsonl` carries both, with a `note` field.
