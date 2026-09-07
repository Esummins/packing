# T1 — the polygon core measured over every alive node (A57 + A60)

A132, 2026-09-07. Data: `results/measure132.jsonl` (506 rows), `results/split132.jsonl`,
`results/check132.json`, `results/control132.json`; tables reproduced by `code/table132.py`.
Read-only on every campaign; the polygons are built and certified by `code/polycore.py`.

## Population

`recheck96.alive_rows()` returns **414** A57 nodes carrying an `ALIVE…` verdict in
`results/tree_*.jsonl` (the "383 queue" of the brief is that list minus what A123/A124's re-check
has since killed: 47 certified kills + 4 trim-kills across `recheck96.jsonl` and
`recheck124.jsonl`). All 414 have a stored node record with `packing`, `rows_all` and `hyp`.
A60's alive population is its **92** `refused (tau … >= budget …)` records with a matching
`results/nodes/<tag>.json` — the record format carries everything needed, so A60 is measured too.

Level = `1 + id.count("_D")`. Every node's hypothesis is `5 pins + 1 conditioned box`
(A60: the same shape at depth j), so **every** box gets a polygon core, pins included.

## What was measured, per node

* `K′(B)` for the conditioned box and for each pin box, **certified vertex by vertex** in exact
  rationals (`polycore.vertex_ok`; the builder's grid/shrink/simplification is unaudited, the
  vertex test is the proof). 506 nodes × 6 boxes, **zero** build failures, 41 s in one process.
* (i) DUAL-SUPPORT columns (`packing`, weight `y`) that meet `K′` but not `K(a)`, at the LP's own
  drop margin `EPS_CORE = 2e-3`, and the weight they carry.
* (ii) the FULL placement pool. **Note on the brief's wording:** the record's `atoms_all` are the
  primal ATOM points (the LP's columns in the primal), not placements; the pool of *placements* —
  which is what a core can exclude, and what the dual's columns are — is `rows_all`. That is what
  is reported.
* (iii) the T5-polygon logic test: `K′(B)` meets a pin's `K′(P)`, with an exact rational witness
  point certified against **both** boxes.

## Result

See `logs/table132.txt` for the class × level table. Headlines:

* `area(K′)/area(K(a))`: median **1.225**, and it rises as the tilt bin widens — level 1 (bins of
  6–14°) median 1.23–1.26, level 3 (bins ≈ 2°) 1.06–1.08. The polygon core is worth most exactly
  where the axis core is weakest.
* **(i)** 7,988 of 35,898 dual-support columns (**22.3%**) meet `K′` but not `K(a)`, carrying
  **35.7%** of τ. Only **17 of 506** nodes have none.
* **(ii)** 1,168,443 of 5,712,598 pooled rows (**20.5%**).
* Crude "would it die": `w⁺ ≥ τ − (budget−1)` on **401/506**, `w⁺ > τ − budget` on **495/506**.
  Read this as an **upper bound on the possible drop**, not a prediction: with the columns removed
  the restricted dual has value in `[τ − w⁺, τ]`, and the LP re-optimises. T2 is the real test.
* **(iii)** T5-polygon fires on **64/506**; 27 of those are already killed by the *deployed* T5′
  tight-core rule (20 of them recorded in `superseded_by_tight_core.jsonl`; the other 7 are A60
  nodes, where T5′ was never applied). **37 are new.**

## Where the excluded columns come from: the conditioned box vs the pins

`measure132` tests a placement against **every** core of the hypothesis. The pins are boxes too
(`th0 = th1 = 0`, centre half-width `hh = 1e-2/√2`), so `K′(P)` is the axis square of half-side
`1/2 − hh = 0.49293` against `K(a) = 0.48999…` — only a 0.6% enlargement, but pinned squares nearly
touch, so it bites. `code/split132.py`:

| | pool `n` | K′-only from the CONDITIONED box | from the PINS |
|---|---|---|---|
| A57 support | 33,917 | 5,410 (15.95%, weight 586.7) | 1,919 (5.66%, weight 157.2) |
| A57 pool | 5,274,902 | 699,916 (13.27%) | 362,277 (6.87%) |
| A60 support | 1,981 | 654 (33.01%, weight 162.0) | 5 (0.25%, weight 3.5) |
| A60 pool | 437,696 | 104,787 (23.94%) | 1,463 (0.33%) |

So on A57 roughly **three quarters** of the excluded weight is the conditioned box's own doing and
a quarter is the pins'; on A60 it is essentially all the conditioned box. This is the split that
reconciles the figure with the PI's count: `k5_11_interior_Y0186_D00_D00` has **2 of 8** support
columns excluded by the conditioned box alone — the PI's "two of the 5–8 support columns" — and
5 of 8 once the pin cores are upgraded too.

## Positive control (A96's discipline)

`code/control132.py`: **854/854** recorded `KILL-BY-LOGIC` boxes across every `tree_*.jsonl` are
still killed by the polygon rule; 0 lost, 0 build errors (`results/control132.json`, `clean: true`).
Argued as well as executed: `K(a_tight)` is a square contained in every pose of `B`, hence contained
in `K′(B)`, so no T5/T5′ kill can be lost — the control checks that the 1e-6 shrink and the vertex
simplification do not eat a marginal one.

## Sampled confirmations — drawn → tested → hits (`results/check132.json`)

* **A, the polygon core itself.** 40 nodes; **drawn** 400,000 poses uniformly in their boxes →
  **tested** 15,760,000 (vertex, pose) pairs → **hits 0** violations of `|R(−θ)(v−c)|∞ ≤ 1/2`
  (max observed 0.499977). The exact rational vertex certification is the proof; this is the control.
* **B, the offending columns.** 449 dual-support columns that meet `K′` but not `K(a)`; **drawn**
  449,000 poses → **tested** 449,000 (column, pose) pairs → **hits 449,000 overlaps = 100.00%**.
  Every such column overlaps the hypothesis square at *every* pose, exactly as the PI read off the
  residue-map SVG.
* **C, the negative control.** 2,307 columns that do *not* meet `K′`; **drawn** 2,307,000 poses →
  **tested** 2,307,000 → **hits 1,805,386 disjoint poses = 78.26%**. The test is not vacuous: a
  column that misses `K′` really does have poses it clears.
* **D, the T5-polygon witnesses.** 64 firing nodes, both boxes; **drawn** 57,000 poses → **tested**
  57,000 → **hits 0** violations. Each witness is additionally certified *exactly* in rationals
  against both boxes (64/64).
