# T5 - the four DONE certificate corpora replayed in Lean by `native_decide`

A78 wave 6, task T5.  Every certificate of **C.K61**, **D.TRAP**, **D.P1** and **A.THMU**
re-decided inside Lean 4.34.0-rc1 + Mathlib by `native_decide` on the A70 checker
`PackingCert.CaseI.checkCaseI` (`CaseChecker.lean`), each PASS then composed with the
`CaseBridge.lean` soundness theorem into the mathematical kill statement.

## Result

| corpus | replayed | Lean wall | max certificate | pending |
|---|---:|---:|---|---|
| K61 | 61/61 | 9.56 h | `k4_12` 2805 s | none |
| TRAP | 6/6 | 1.24 h | `k6_23` 2021 s | none |
| P1 | 1/1 | 0.02 h | `m3_trump5_interior_NO` 84 s | none |
| THMU | 11/11 | 0.21 h | `u_reinsert_00` 166 s | none |

**All 73 certificates replayed, 9.79 h of Lean wall in total.**  All four aggregate
theorems - `corpus_K61`, `corpus_TRAP`, `corpus_P1`, `corpus_THMU` - and the `Corpus.lean`
root elaborate: `lake build PackingCertCorpus` is green (3 189 jobs).

Nine certificates needed a second attempt and two (`k4_09`, `k4_12`) a third with the cap
raised to 90 min.  Every one of those was a **CPU-contention** artifact of a shared
machine, not a hard case: e.g. `k4_09` capped at 40 min on the run where the strictly
larger `k5_12` and `k4_04` both finished under it, then took 1 814 s once the machine was
quiet.  Only `k4_12` (7 439 194 boxes, 2 800 s) genuinely exceeds a 40 min budget.
`results/t5_timings_history.jsonl` keeps every attempt including the capped ones.

## What each module proves

Per certificate, two modules (the isolation unit - verified: rebuilding
`PackingCertMathlib.Corpus.K61.Check_k5_06` after the whole run re-evaluates **nothing**):

* `Corpus/<CORPUS>/Data_<name>.lean` - `PackingCert.CaseI.Data.<name> : CCertI`, emitted
  verbatim by `lean/gen_case_lean.py` at the depth in the certificate's `.report.json`;
* `Corpus/<CORPUS>/Check_<name>.lean` -
  * `check_<name> : checkCaseI Data.<name> = true := by native_decide`,
  * `<name>_side : caseSide Data.<name> = <s>` (the CaseK506 pilot's rewrite lemma),
  * `<name>_kill` (empty `nofams`, via `checkCaseI_kill`): *no strict family of 11 closed
    unit squares in `[0,s]^2` has designated owners containing the certificate's cores*, or
  * `<name>_no_family` (D.P1, A.THMU - `nofams` present, via `checkCaseI_no_family`):
    *every such family has a non-owner member that is `CaseExempt`* (Lemma B-NO occupancy).

Per corpus, `Corpus/<CORPUS>.lean` states one theorem `corpus_<CORPUS>` = the conjunction
of that corpus's `check_*` facts; `Corpus.lean` is the roll-up root.  **D.TRAP re-uses the
K61 check modules for its six k6 classes - there is no second evaluation.**

Built by a SECOND lake library `PackingCertCorpus` (`roots = ["PackingCertMathlib.Corpus"]`),
so the default target and CI are untouched - verified: a default `lake build` builds zero
`PackingCertMathlib.Corpus` modules.

## Axiom audit (`logs/axioms_corpus.log`, `scratch/AxiomsCorpus.lean`)

150 `#print axioms` blocks: 73 `check_*`, 73 `*_kill`/`*_no_family`, 4 `corpus_*`.
**CONFIRMED - every `check_<name>` depends on exactly** `propext`, `Classical.choice`,
`Quot.sound` **and its own single**
`PackingCert.S11.check_<name>._native.native_decide.ax_1_1` **- nothing else.**  The
composed kill / no-family theorems add no axiom beyond those three; and each `corpus_*`
depends on exactly the native_decide axioms of its own members and nothing more
(`corpus_K61` 61, `corpus_TRAP` 6, `corpus_P1` 1, `corpus_THMU` 11).

## Python cross-check - decision neutrality (`results/t5_xcheck.jsonl`)

Frozen verifier `attempts/A53-simple-strata/code/verify_case.py` re-run single-job with
`--no-float-prepass` on the 3 cheapest and the 3 most expensive certificates:

| certificate | result | boxes (no float pre-pass) | boxes (campaign report) | time |
|---|---|---:|---:|---:|
| `u_reinsert_00` | **PASS** | 424 | 424 | 1 s |
| `u_reinsert_05` | **PASS** | 456 | 456 | 2 s |
| `u_reinsert_02` | **PASS** | 462 | 462 | 2 s |
| `k5_12` | **PASS** | 4,416,100 | 4,416,100 | 813 s |
| `k4_04` | **PASS** | 4,582,778 | 4,582,778 | 2269 s |
| `k4_12` | **PASS** | 7,439,194 | 7,439,194 | 689 s |

Box counts are **identical** in every case: the float pre-pass only shortlists, it never
decides - the same finding A70/A75 recorded, now confirmed at the corpus's extremes.

## Disagreements with the Python reports

**NONE.**  Every certificate that Lean evaluated returned `checkCaseI = true`, matching
its `.report.json` PASS.  No `native_decide` produced `false`, and no elaboration failed.

## Cost model (prices the A57/A60 replays)

Lean `native_decide` throughput on the K61 check modules: **min 340, median ~1,480, max
~2,490 boxes/s** (wide spread - the machine was shared with the A57/A60/A61/A76/A77/A79
campaigns throughout).  Fixed cost per check module ~15-20 s.  Against the Python
`time_s` in the reports the Lean wall is roughly **10-40x slower** on the large
certificates and far worse on the tiny ones (fixed cost dominates).

Two structural notes for pricing a future A57/A60 replay:

* the THMU certificates are the outlier - 424 boxes cost 158 s on the first build,
  because their coordinates are rationals with 10^14 denominators and the core-exemption
  test is exact `Rat` arithmetic.  **Box count alone does not price a certificate;
  coordinate size does too.**
* one `lake build` invocation costs ~10 s of trace replay on top, and the shared
  `lakeb.py` lock means a concurrent A78 build can add minutes of pure waiting to the
  wall clock (recorded separately as `lean_wall_s` vs `lake_s` vs `lean_check_s`).

## Corpus manifest note (a trap worth recording)

`k3_00` is **`attempts/A55-k4-sweep/k3_ext/certs/k3_00.json`** (579 atoms, 3 cores, depth
56, report PASS).  The sibling `attempts/A55-k4-sweep/certs/k3_00.json` is a *different,
weaker* certificate (246 atoms) whose report says **FAIL**; it was rejected by the
driver's PASS gate.  All 61 K61 reports, the P1 report and the 11 THMU reports say PASS.

## Files

* `lean/gen_corpus_lean.py` - the driver (`all` / `<CORPUS>` / `--only` / `--manifest`);
* `lean/PackingCertMathlib/PackingCertMathlib/Corpus/{K61,P1,THMU}/{Data,Check}_*.lean`
  (73 + 73 modules), `Corpus/{K61,TRAP,P1,THMU}.lean`, `Corpus.lean`;
* `lean/PackingCertMathlib/lakefile.toml` - the `PackingCertCorpus` library;
* `lean/PackingCertMathlib/scratch/AxiomsCorpus.lean`;
* `attempts/A78-lean-wave6/code/{t5_run,t5_report,t5_axioms,t5_xcheck}.py`;
* `attempts/A78-lean-wave6/results/{t5_order.json, t5_timings.jsonl, t5_timings_history.jsonl, t5_xcheck.jsonl}`;
* `attempts/A78-lean-wave6/logs/{t5_build.log, t5_runner.out, t5_runner2.out, t5_runner3.out, axioms_corpus.log, t5_xcheck.log}`.

`t5_timings.jsonl` holds one row per certificate (last attempt wins);
`t5_timings_history.jsonl` keeps all 84 attempts including the capped first tries.

## Per-certificate timings

`lean_check_s` is lake's own time for the `Check_*` module (the `native_decide` cost);
`lean_wall_s` additionally includes the lake invocation and any wait for the shared lock.

| # | corpus | certificate | atoms | cores | nofams | depth | py boxes | py time_s | Lean wall_s | Lean check_s | status |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | THMU | `u_reinsert_00` | 0 | 10 | 1 | 60 | 424 | 0.0 | 165.8 | 158.0 | OK |
| 2 | THMU | `u_reinsert_05` | 0 | 10 | 1 | 60 | 456 | 0.0 | 126.8 | 21.0 | OK |
| 3 | THMU | `u_reinsert_02` | 0 | 10 | 1 | 60 | 462 | 0.0 | 53.2 | 39.0 | OK |
| 4 | THMU | `u_reinsert_03` | 0 | 10 | 1 | 60 | 750 | 0.1 | 56.3 | 32.0 | OK |
| 5 | THMU | `u_reinsert_01` | 0 | 10 | 1 | 60 | 846 | 0.1 | 84.5 | 25.0 | OK |
| 6 | THMU | `u_reinsert_04` | 0 | 10 | 1 | 60 | 908 | 0.1 | 45.9 | 30.0 | OK |
| 7 | THMU | `u_reinsert_10` | 0 | 10 | 1 | 60 | 1,070 | 0.1 | 44.2 | 25.0 | OK |
| 8 | THMU | `u_reinsert_09` | 0 | 10 | 1 | 60 | 2,208 | 0.2 | 44.2 | 27.0 | OK |
| 9 | THMU | `u_reinsert_06` | 0 | 10 | 1 | 60 | 2,272 | 0.2 | 43.2 | 28.0 | OK |
| 10 | THMU | `u_reinsert_07` | 0 | 10 | 1 | 60 | 2,402 | 0.2 | 42.4 | 27.0 | OK |
| 11 | THMU | `u_reinsert_08` | 0 | 10 | 1 | 60 | 3,048 | 0.2 | 33.0 | 22.0 | OK |
| 12 | K61 | `k6_31` | 3 | 6 | 0 | 56 | 13,660 | 0.8 | 38.4 | 28.0 | OK |
| 13 | K61 | `k6_05` | 4 | 6 | 0 | 56 | 14,954 | 0.6 | 54.6 | 44.0 | OK |
| 14 | K61 | `k6_26` | 4 | 6 | 0 | 56 | 20,668 | 0.8 | 53.8 | 43.0 | OK |
| 15 | K61 | `k6_10` | 4 | 6 | 0 | 56 | 20,794 | 0.7 | 41.4 | 33.0 | OK |
| 16 | K61 | `k6_01` | 4 | 6 | 0 | 56 | 23,150 | 0.7 | 48.3 | 37.0 | OK |
| 17 | K61 | `k5_18` | 5 | 5 | 0 | 56 | 25,170 | 0.8 | 82.4 | 35.0 | OK |
| 18 | K61 | `k6_15` | 4 | 6 | 0 | 56 | 31,556 | 0.9 | 55.7 | 44.0 | OK |
| 19 | K61 | `k6_03` | 6 | 6 | 0 | 56 | 31,744 | 0.8 | 47.3 | 39.0 | OK |
| 20 | K61 | `k5_00` | 5 | 5 | 0 | 56 | 34,382 | 1.1 | 76.0 | 65.0 | OK |
| 21 | K61 | `k6_09` | 4 | 6 | 0 | 56 | 35,536 | 1.3 | 121.4 | 101.0 | OK |
| 22 | K61 | `k6_16` | 7 | 6 | 0 | 56 | 36,248 | 1.1 | 83.2 | 70.0 | OK |
| 23 | K61 | `k6_02` | 4 | 6 | 0 | 56 | 39,218 | 1.2 | 95.4 | 80.0 | OK |
| 24 | P1 | `m3_trump5_interior_NO` | 3 | 5 | 1 | 60 | 39,926 | 2.1 | 84.5 | 71.0 | OK |
| 25 | K61 | `k5_06` | 10 | 5 | 0 | 56 | 42,768 | 1.2 | 103.8 | 87.0 | OK |
| 26 | K61 | `k6_11` | 6 | 6 | 0 | 56 | 46,222 | 1.3 | 108.9 | 94.0 | OK |
| 27 | K61 | `k6_00` | 6 | 6 | 0 | 56 | 46,998 | 1.3 | 107.8 | 90.0 | OK |
| 28 | K61 | `k6_13` | 8 | 6 | 0 | 56 | 56,242 | 1.4 | 100.7 | 84.0 | OK |
| 29 | K61 | `k6_14` | 4 | 6 | 0 | 56 | 66,564 | 1.9 | 136.2 | 120.0 | OK |
| 30 | K61 | `k5_09` | 5 | 5 | 0 | 56 | 69,212 | 1.9 | 100.0 | 88.0 | OK |
| 31 | K61 | `k4_07` | 12 | 4 | 0 | 60 | 80,154 | 1.7 | 53.0 | 47.0 | OK |
| 32 | K61 | `k6_18` | 4 | 6 | 0 | 56 | 84,112 | 2.0 | 67.8 | 62.0 | OK |
| 33 | K61 | `k5_08` | 5 | 5 | 0 | 56 | 84,194 | 2.2 | 63.1 | 57.0 | OK |
| 34 | K61 | `k6_12` | 8 | 6 | 0 | 56 | 117,370 | 2.7 | 88.7 | 82.0 | OK |
| 35 | K61 | `k5_01` | 36 | 5 | 0 | 56 | 125,374 | 2.7 | 76.7 | 71.0 | OK |
| 36 | K61 | `k6_28` | 9 | 6 | 0 | 56 | 155,462 | 4.6 | 112.4 | 107.0 | OK |
| 37 | K61 | `k5_20` | 10 | 5 | 0 | 56 | 192,678 | 5.0 | 134.2 | 129.0 | OK |
| 38 | K61 | `k6_08` | 8 | 6 | 0 | 56 | 343,470 | 9.0 | 747.3 | 723.0 | OK |
| 39 | K61 | `k6_17` | 4 | 6 | 0 | 56 | 349,164 | 11.3 | 357.1 | 303.0 | OK |
| 40 | K61 | `k6_06` | 4 | 6 | 0 | 56 | 374,744 | 8.4 | 267.6 | 256.0 | OK |
| 41 | K61 | `k6_04` | 4 | 6 | 0 | 56 | 377,138 | 8.6 | 217.4 | 212.0 | OK |
| 42 | K61 | `k5_04` | 62 | 5 | 0 | 56 | 412,372 | 11.1 | 216.3 | 211.0 | OK |
| 43 | K61 | `k6_32` | 11 | 6 | 0 | 56 | 452,052 | 12.8 | 278.8 | 273.0 | OK |
| 44 | K61 | `k6_07` | 11 | 6 | 0 | 56 | 454,286 | 11.9 | 272.2 | 267.0 | OK |
| 45 | K61 | `k6_24` | 93 | 6 | 0 | 56 | 482,300 | 11.1 | 310.9 | 305.0 | OK |
| 46 | K61 | `k5_10` | 16 | 5 | 0 | 56 | 510,032 | 12.4 | 242.9 | 238.0 | OK |
| 47 | K61 | `k5_07` | 12 | 5 | 0 | 56 | 570,276 | 21.0 | 273.2 | 268.0 | OK |
| 48 | K61 | `k5_02` | 54 | 5 | 0 | 56 | 630,622 | 13.7 | 314.3 | 309.0 | OK |
| 49 | K61 | `k6_20` | 32 | 6 | 0 | 56 | 664,704 | 14.6 | 372.4 | 367.0 | OK |
| 50 | K61 | `k5_17` | 15 | 5 | 0 | 56 | 683,954 | 18.8 | 324.0 | 318.0 | OK |
| 51 | K61 | `k6_21` | 18 | 6 | 0 | 56 | 732,660 | 15.5 | 408.6 | 403.0 | OK |
| 52 | K61 | `k5_19` | 29 | 5 | 0 | 56 | 759,514 | 14.3 | 413.3 | 407.0 | OK |
| 53 | K61 | `k6_25` | 4 | 6 | 0 | 56 | 769,986 | 13.0 | 435.1 | 429.0 | OK |
| 54 | K61 | `k5_05` | 58 | 5 | 0 | 56 | 809,582 | 21.0 | 383.9 | 378.0 | OK |
| 55 | K61 | `k6_22` | 188 | 6 | 0 | 56 | 887,804 | 25.9 | 613.8 | 607.0 | OK |
| 56 | K61 | `k6_29` | 105 | 6 | 0 | 56 | 1,106,838 | 46.2 | 721.1 | 714.0 | OK |
| 57 | K61 | `k6_19` | 4 | 6 | 0 | 56 | 1,268,998 | 39.2 | 846.4 | 839.0 | OK |
| 58 | K61 | `k6_30` | 16 | 6 | 0 | 56 | 1,385,050 | 31.8 | 886.4 | 879.0 | OK |
| 59 | K61 | `k4_00` | 433 | 4 | 0 | 60 | 1,494,990 | 36.5 | 845.6 | 838.0 | OK |
| 60 | K61 | `k5_03` | 40 | 5 | 0 | 56 | 1,586,604 | 34.5 | 819.0 | 812.0 | OK |
| 61 | K61 | `k5_15` | 33 | 5 | 0 | 56 | 1,592,470 | 35.0 | 868.8 | 862.0 | OK |
| 62 | K61 | `k6_27` | 25 | 6 | 0 | 56 | 1,920,168 | 53.3 | 1537.4 | 1530.0 | OK |
| 63 | K61 | `k5_14` | 129 | 5 | 0 | 56 | 1,932,370 | 75.4 | 1115.7 | 1106.0 | OK |
| 64 | K61 | `k4_01` | 501 | 4 | 0 | 60 | 1,974,776 | 71.5 | 1065.9 | 1056.0 | OK |
| 65 | K61 | `k4_10` | 13 | 4 | 0 | 60 | 2,325,594 | 45.5 | 1035.8 | 1028.0 | OK |
| 66 | K61 | `k6_23` | 501 | 6 | 0 | 56 | 2,449,492 | 43.9 | 2021.1 | 2004.0 | OK |
| 67 | K61 | `k4_02` | 185 | 4 | 0 | 60 | 2,480,066 | 66.3 | 1960.4 | 1951.0 | OK |
| 68 | K61 | `k5_13` | 106 | 5 | 0 | 56 | 2,589,162 | 52.2 | 2066.2 | 1877.0 | OK |
| 69 | K61 | `k3_00` | 579 | 3 | 0 | 56 | 2,817,596 | 64.9 | 1359.8 | 1349.0 | OK |
| 70 | K61 | `k4_09` | 531 | 4 | 0 | 60 | 4,192,860 | 158.7 | 1819.0 | 1814.0 | OK |
| 71 | K61 | `k5_12` | 49 | 5 | 0 | 56 | 4,416,100 | 176.9 | 2278.1 | 2273.0 | OK |
| 72 | K61 | `k4_04` | 205 | 4 | 0 | 60 | 4,582,778 | 146.4 | 1849.8 | 1844.0 | OK |
| 73 | K61 | `k4_12` | 77 | 4 | 0 | 60 | 7,439,194 | 173.6 | 2805.2 | 2800.0 | OK |
