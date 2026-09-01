# A55 / k3_ext — k3_00 killed: the pin-LP route terminates

Extends `attempts/A55-k4-sweep/` (K7, GAP-A55-6). Everything at s0 = 969271/250000 = 3.877084,
A53 Young-form stratification, A54 semantics (S0: τ_LP bounds τ* in neither direction; the sole
arbiter of a kill is an exact rational measure certificate accepted by `verify_case.py`).
A53/A54/A55 code and results are read, never written, except A55's `results/cap.json`, which is
appended (backed up first: `results/cap.json.bak_pre_k3ext`, and a copy in
`k3_ext/results/cap.json.bak_preA55k3ext`). A29 untouched.

## E1 [T] — the target and why it was the last one

`k3_00` = the full left-wall column {(½,½), (½,3/2), (½,5/2)}, k = 3, budget 11 − 3 = **8**.
A55 K7: every k ≥ 4 class containing it (k4_00, k4_01, k4_02 and their supersets) is certifiably
empty, yet the *stratum* k3_00 is untouched by those kills and — uniquely among the 11 classes
with k ≤ 3 — is **not** a sub-skeleton of any open k = 5 class, so K1 did not protect it.

## E2 [M] — the kill

`certs/k3_00.json`: 3 degenerate cores (the pins, θ = 0), **579 atoms**, total
**399/50 = 7.980000 < budget 8**, scale **1.0412** of the ceiling 8/τ = **1.043806** at
τ = 7.664262. Certification PASSED at **round 0** — no witness feedback needed once the warm
start was merged.

Arbiters:
* in-loop `verify_case.py` (depth 56, 3 jobs): PASS, 2817596 boxes, max depth used 44, 64.9 s.
* **independent re-verification `--depth 60 --jobs 6`: PASS, 2817596 boxes, 0 witnesses,
  covered 1352961, exempt 55869 (core 55869, nofam 0), max depth used 44, 66.6 s**
  → `k3_ext/reverify_d60.report.json`, log `k3_ext/logs/reverify_d60.out`.
* `verify_case.py --selftest`: 3000 random boxes, 0 problems (int vs Fraction predicate
  cross-check, run on this machine before the re-verification).

## E3 [M] — the lever was the merged warm start, exactly as at k = 4

A55's scout ran **cold** (0 atoms, 0 rows): τ = 23/3 = 7.666667, η = −0.3333, cert FAIL after
5 rounds, worst exact holes 1.0324 → 0.9836 → 0.9832 → 0.9571 → 0.9829. Its FAIL was not a
scale problem: at scale 1.0455 a hole of scaled mass 0.9829 carries only 0.940 at unit scale
and would need scale ≥ 1.064 > ceiling 1.044. The fix is more coverage, not more scale (A54 S2).

Two extension passes, row pruning OFF, column-only pruning (`--prune_cols 3 --max_cols_add 350`),
scale cap lifted to 1.4 so the auto-scale reaches the true ceiling:

| pass | warm start | init LP | τ | outcome |
|---|---|---|---|---|
| scout (A55) | cold: 0 atoms / 0 rows | 625 orbits, 1129 rows | 7.666667 | FAIL, 5 rounds, 2644 s |
| e1 | 929 atoms / 56748 rows (scout node + 4 re-solves + witnesses) | 1519 orbits, 29774 rows | 7.664167 @ it 17 | interrupted at 3315 s; **checkpoint kept** |
| **e2** | **2951 atoms / 64297 rows** (e1's recovered checkpoint added) | **2951 orbits, 49628 rows** | **7.664262**, 51773 rows | **PASS at round 0**, 65 s |

The decisive quantity is the **column set**: e1's checkpoint carried 2951 generated orbits versus
929 recoverable from the json artefacts, and folding those back is what took certification from
FAIL-after-5-rounds to PASS-at-round-0. τ barely moved throughout (7.6667 → 7.6643, η ≈ −0.336);
**η is not the progress variable — accumulated atoms are.** This is the k4_00 story (3 passes,
37k rows, 0.9950 → PASS) reproduced one level down.

*Operational note (worth banking):* `ladder_ext.merged_warm` now also reads
`<name>_state*.json` checkpoints (keys `orbits`/`rows`), so an interrupted pass loses nothing.
e1 was killed by the harness, not by the machine; the recovered checkpoint is what made e2 win.

## E4 [T] — CONSEQUENCE: no pin-LP target remains at any k

With k3_00 certified the ledger is **61 certified pin-sets** (1 at k = 3, 8 at k = 4, 19 at
k = 5, 33 at k = 6) and the emptiness map (`code/cap_ext.py`, rebuilt from the PASS files alone
by D4-containment) is

| k | classes | certifiably EMPTY | open |
|---|---|---|---|
| 0 | 1 | 0 | k0_00 |
| 1 | 1 | 0 | k1_00 |
| 2 | 3 | 0 | k2_00, k2_01, k2_02 |
| **3** | **6** | **1 (k3_00)** | k3_01 … k3_05 |
| 4 | 14 | 8 | k4_03, k4_05, k4_06, k4_08, k4_11, k4_13 |
| 5 | 22 | 19 | k5_11, trump5, k5_16 |
| 6–9 | 33/35/30/18 | all | — |

**Theorem (measured, V-k3).** Every open Young class at every k ≤ 4 is contained in one of the
three open k = 5 classes {k5_11, trump5, k5_16}, with no exceptions — verified class by class
against all D4 images:

    k0_00, k1_00, k2_00-02, k3_01, k3_03, k3_05  ⊂ all three
    k3_02 ⊂ {k5_11, trump5}   k3_04 ⊂ {trump5, k5_16}
    k4_03 ⊂ {k5_11, trump5}   k4_05 ⊂ {k5_11, k5_16}   k4_06, k4_11 ⊂ {trump5, k5_16}
    k4_08 ⊂ {trump5}          k4_13 = corners4 ⊂ {k5_16}

By K1 (aliveness propagates downward) **no certificate can ever exist for any of them**. So the
pin-hypothesis route is now *complete*, not merely advanced: A55 K6 showed the k = 4 layer hit
its theoretical maximum, and k3_00 was the single class below it that the argument did not
already cover. Every Young class that any pin-LP could kill has been killed, and the entire
remaining stratification problem is **exactly** the three k = 5 classes k5_11, trump5, k5_16
(GAP-A54-1 / GAP-A55-1), of which trump5 is provably alive.

## E5 — gaps

* **GAP-A55-6 CLOSED.** No successor: there is no k ≤ 4 target left (E4).
* **GAP-A55-4 / G-A53-1 inherited unchanged** — the certificate is at s = s0 only
  (s-parametric transfer is A56's subject).
* GAP-A55-1, GAP-A55-2 (no ALIVE-side verifier), GAP-A55-3 (corners4's 0.200) untouched.
