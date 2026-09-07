# A129 — the numbers

All runs: one or two BLAS-pinned (`OMP/OPENBLAS/MKL_NUM_THREADS=1`) BelowNormal Python processes,
`PYTHONDONTWRITEBYTECODE=1`, `--jobs 1` everywhere so that every wall is single-core and comparable.
Read-only on every campaign directory; the frozen verifiers are byte-identical (they were **run**,
never edited). Total ≈ 7.5 CPU-h.

---

## T1 — the verifier and its checker

`code/netverify.py` (≈ 640 lines) and `code/netcheck.py` (≈ 300 lines); the soundness note with
Lemmas N1–N4 is `notes/method.md`. `netverify.py` emits `net-orientation-certificate-v1`;
`netcheck.py` re-decides it by a 2-D branch and bound in pure `Fraction`s with **no numpy, no floats
and no re-implementation of the exemption** (it imports the frozen `verify_case.core_exempt_frac` /
`nofam_exempt`).

End-to-end on a real A57 leaf, `k5_11_interior_NO` (3 atoms, 5 cores, 1 NO-family, s0):

| | verdict | wall | work |
|---|---|---|---|
| frozen `verify_case.py` | PASS | **1.02 s** | 14,206 boxes (4,414 covered, 2,721 exempt) |
| `netverify.py --adaptive 3 26` | PASS | 38.8 s | 364 net orientations (deepest level 11), B_min = 0.98016, 371k arrangement cells, 26,624 bisections |
| `netcheck.py` (all 364 cells) | **CHECKED** | 28.8 s | 133,788 B&B nodes (23,296 covered, 26,967 exempt by the frozen predicates, 16,813 inadmissible), max depth 38 |

Two things this run settles.

* **The exemption clause must be the unit square's, not the shrunk square's** (Lemma N3). With the
  naive Burns–Massaccesi port — exempt when the *shrunk* square meets a core — the same certificate
  fails at **every** level from 1 to 16 with a live minimum of exactly `0`: the shrink strips a rim of
  width `Θ(1-B)` off every core's exempt region, and the LP never put mass inside an exempt region.
  With Lemma N3 the certificate is reproduced. This is the whole difference between "the method
  cannot replay a single A57 kill" and the table below.
* **A pure sweep is not enough for conditional certificates.** The grid the atoms cut is far too
  coarse to resolve a 6-core exempt boundary, so `netverify` bisects undischarged light cells in
  `(U,V)`. Since the mass is constant on a grid cell (Lemma N4), that bisection is purely geometric —
  and it is where the wall goes.

---

## T2 — 60 stratified A57 PASS leaves

**Sample.** 1,066 A57 PASS leaves have their certificate and their frozen `.report.json` on disk.
Stratified into: all 14 at tree level 2; 15 level-1 leaves with ≤ 5 atoms; 15 with 6–30; 16 with > 30
(`results/sample60.json`, seed 129).

*Stratification caveat, stated plainly.* The brief asked for ≥ 15 leaves "whose certificate needed
tilt sub-cells" and ≥ 15 "whose tilt cells are wide". **No A57 PASS leaf has a tilt sub-cell**: all
1,029 with a node record carry `theta_box = [[0, 90, 1.0]]` with a single piece — the case-measure
certificate makes its claim over *all* orientations and never sub-divides tilt. The nearest real
analogue is A96's parametric re-emission, whose `s_cells > 1` counts the sub-cells the 4-D verifier
needed; 33 of the 60 have such a record (all with `s_cells > 1`), 27 do not, and both sub-populations
are reported. The substituted axis (atom count) is the one that actually separates the population:
it separates exemption-dominated leaves from mass-dominated ones.

**Protocol.** `netverify --adaptive 3 26`, 120 s wall budget per leaf, `max_witnesses 3`. Baseline =
the wall recorded in each leaf's own frozen `verify_case` report (`jobs 1`, `depth 48`, `split 3`).

| stratum | n | reproduced | frac | MARGIN fails | BLOWUP | med atoms | med level | med net cells | med shrink 1−B | med s(1/B−1) | med \|η\| | med frozen s | med net s | med ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ALL** | 60 | **26** | **43 %** | **0** | 34 | 16 | 10 | 185 | 2.4e−2 | 9.4e−2 | 1.000 | 5.1 | 47.4 | **15×** |
| level 1 | 46 | 22 | 48 % | 0 | 24 | 12 | 10 | 177 | 2.8e−2 | 1.1e−1 | 1.000 | 5.0 | 34.2 | 14× |
| level 2 | 14 | 4 | 29 % | 0 | 10 | 30 | 9 | 234 | 8.4e−3 | 3.3e−2 | 0.583 | 5.6 | 62.8 | 18× |
| A: atoms ≤ 5 | 15 | **14** | **93 %** | 0 | 1 | 4 | 10 | 129 | 2.9e−2 | 1.2e−1 | 1.000 | 2.3 | 19.2 | 11× |
| B: atoms 6–30 | 15 | 8 | 53 % | 0 | 7 | 12 | 12 | 199 | 1.5e−2 | 6.0e−2 | 1.000 | 4.5 | 93.6 | 20× |
| C: atoms > 30 | 16 | **0** | **0 %** | 0 | 16 | 110 | – | – | – | – | 1.000 | 6.6 | – | – |
| param sub-cells (`s_cells>1`) | 33 | 14 | 42 % | 0 | 19 | 15 | 10 | 150 | 2.9e−2 | 1.2e−1 | 1.000 | 3.4 | 22.4 | 14× |
| no param record | 27 | 12 | 44 % | 0 | 15 | 17 | 10 | 248 | 1.5e−2 | 6.0e−2 | 0.667 | 7.3 | 66.0 | 15× |

On the 26 reproduced leaves: net wall 1,302 s against the frozen verifier's 121 s — **10.8× on the
totals**, per-leaf ratio min 1.6×, **median 15.1×**, max 53.7×.

**The failure mode is BLOW-UP, never MARGIN — 0 of 60.** No leaf produced a witness: not one shrunk
problem turned out to be feasible. To turn the 34 BLOWUPs into numbers, a second pass
(`code/pass2.py`) sampled 8 positions in `t` per leaf on 12 BLOWUPs spanning 5–132 atoms and found,
for each sample, the smallest net level at which that cell passes on its own — an exact decision:

* **96 of 96 sample points resolved.** Levels 5–12; per-leaf maximum level 7–12.
* Estimated adaptive net: 88–936 orientations (median 280).
* Estimated wall: 42–1,790 s per leaf against a frozen wall of 0.9–89 s — ratio **5.8× to 234×,
  median 26.7×**, 26.8× on the totals (5,023 s vs 187 s).

So the honest statement is: **the net verifier reproduces every A57 PASS kill it was pointed at — 26
outright, 12 more shown by exact sampling to be within reach — and none of them was refuted; it is
simply 10–30× slower on the easy ones and up to 200× slower on the atom-heavy ones.**

**Margin, measured.** The shrink actually consumed at the level that works is `1−B` between 6e−5 and
5e−2, i.e. `s·(1/B−1)` between 2e−4 and 0.12 in side. The brief's predicted killer — that at a 1°
tilt cell the shrink costs 0.068 in side, more than the whole window 0.057 — is arithmetically right
and *irrelevant here*, because an A57 leaf certificate is a measure, not a box tree: the shrink is
not subtracted from the side at which the kill holds, it is subtracted from the test square, and
what it must not exhaust is the certificate's **mass** slack, not its side slack. Every certificate
tested had enough mass slack.

**Why it is slower — the structural reason, in counts rather than seconds.** The frozen verifier
bisects one 3-D box tree in `(t, c_x, c_y)`; a single `t`-box discharges a whole band of orientations
against the six cores at once. The net verifier re-resolves the *same* exemption geometry once per
net orientation. On the 26 reproduced leaves it performed 3.60 M exempt tests against the frozen
verifier's 2.11 M total boxes — but spread over a median of 185 net cells, each of which rebuilds its
own arrangement from scratch. This gap is architectural, not arithmetic: it does not close by
optimising the predicate. (A profile does show ≈ 55 % of `netverify`'s wall inside the exact
exemption predicate, where the frozen verifier uses scaled integers and A129 uses `Fraction`s, so a
fully integerised prototype would move the ratios by perhaps 2×, not by 10×.)

---

## T3 — the two whole-problem certificates

Both are `measure-certificate-v1` with **no hypotheses**, which is exactly the shape
Burns–Massaccesi's verifier consumes. So neither had to be estimated: **both were run to completion
and both PASS.** Nothing in either certificate needs replacing — the net method replaces the
*verifier*, not the certificate; there are no "tilt-integrated rows" to substitute, because the
verifier's job is precisely to decide the tilt-integrated claim, and it does so orientation by
orientation.

| | s(11) ≥ 3.82 (`certs/measure_certificate_3.82.json`) | s(12) ≥ 3.90 (`attempts/A33-tight-variety/t3b/certs/A33_s12_3.90_v2.json`) |
|---|---|---|
| atoms / total / budget | 1,769 / 10.985474 / 11 | 1,652 / 11.824128 / 12 |
| **net verifier** | **PASS** | **PASS** |
| net (adaptive, `L0=8`) | **1,950 orientations**, deepest level 14 | **987 orientations**, deepest level 14 |
| cells by level | 8:21 9:106 10:297 11:398 12:736 13:376 14:16 | 8:9 9:231 10:442 11:107 12:68 13:86 14:44 |
| shrink at the coarsest cell used | 1−B = 3.81e−3 (`B = 17837537785/17905787897`) | 1−B = 3.57e−3 (`B = 1272709721/1277267929`) |
| margin consumed, `s(1/B−1)` | 1.46e−2 | 1.40e−2 |
| arrangement cells examined | 3.96e10 | 1.72e10 |
| **net wall** | **2,147.8 s** | **802.0 s** |
| frozen `verify_case` wall / boxes | 586.7 s / 7,639,706 | 232.3 s / 3,258,450 |
| **wall ratio** | **3.66×** | **3.45×** |
| independent `netcheck` (exact, `Fraction`s) | CHECKED on 16/1,950 cells, 563 s (92,012 B&B nodes) → full ≈ 19 h | CHECKED on 16/987 cells, 557 s (103,832 nodes) → full ≈ 9.5 h |

**The refinement profile** (`code/ladder.py`, 24 sample positions across `[0,1]` in `t`, each an
exact per-cell decision):

* 3.82: smallest passing level 8–13, median 10; the hardest sample is `t = 0.0625`
  (θ ≈ 7.15°) at level 13. At level 8 there the live minimum is **0.999757** — the certificate misses
  by 2.4e−4 of mass under a 3.9e−3 shrink. That single number is the margin of the whole 3.82
  certificate against this method.
* 3.90: smallest passing level 9–11, median 9.5; hardest sample `t = 0.6042` (θ ≈ 62.3°) at level 11.
* The sampled estimate (1,845 orientations, 994 s for 3.82; 853, 436 s for 3.90) predicted the
  completed runs to within 6 % on the net size and a factor 2 on the wall (the difference is the
  intermediate failing cells the adaptive net pays for on the way down).

**Against the brief's estimate.** The brief predicted `δ < 0.0150` rad ≈ 0.86°, ≈ 105 net
orientations per square, from `3.82·(cos δ + sin δ) < ŝ`. That inequality is a *rescaling* argument
and does not apply to a measure certificate: nothing here is rescaled, and the binding constraint is
the certificate's own mass robustness. The measured binding half-width is a median of 7.4e−4 rad
(0.042°), and the net needs **1,950 orientations, ≈ 19× the estimate**.

**Verdict for T3.** Yes — both headline certificates get a genuinely structurally independent
cross-check from this route, at bounded and modest cost: **36 min and 13 min of single-core wall**
respectively, against 10 min and 4 min for the frozen verifier. That is a real second opinion on
`s(11) ≥ 3.82` and `s(12) ≥ 3.90` from a verifier that shares no code, no data structure and no
search order with `verify_measure`/`verify_case` — the third independent check of 3.82 after A07's
float-interval B&B and A08's exact-integer B&B, and the second of 3.90. Making it a *fully exact*
second opinion (the `netcheck` pass over all net cells) costs 19 h and 9.5 h and has not been run to
completion; 16 cells of each were, and both CHECKED.
