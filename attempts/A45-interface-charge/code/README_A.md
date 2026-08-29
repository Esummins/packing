# A45 agent A — the interface charge table: what is CERTIFIED vs what is FLOAT-ONLY

Spec: `../notes/charging_lemma.md` (§2 Lemmas P/P'/K, §3 moats, §5 certifier spec).
Machinery: A25's `dead_region.py` / `atlas_lib.py` / `wastage.py` / `exactify.py`,
**copied verbatim** into this directory. A25's own files were not touched.

Code: `a45_lib.py` (frames, moat ladder, charge map, Lemma-K keepers, exact recert),
`pilot.py` + `pilot_diag.py`, `sweep.py`, `build_table.py`, `exact_moats.py`, `canary.py`.
Outputs: `../results/{pilot,charge_table,canary_trump}.json`, `../logs/`, `../work/`.

---

## Headline

| | |
|---|---|
| bins swept | 15 WC (phi in (0,45], 3 deg) + 60 CE (d 3 deg x 4 slide bins); CC not swept |
| bins with a moat | **25** (12 WC, 13 CE); 50 dropped (moat fails at 1/16); 0 vacuous |
| `rho_min` | **1/16**, so charges are evaluated on `B(p, 1/32)` |
| largest charge | **41/65536 = 6.26e-4** (WC, phi in [9,12]) |
| Trump canary | **0.001740 <= B0 = 4.031780343056** — PASS |
| capture fraction | **0.00043** (A26's per-square wall calibration is 0.8672) |
| best capture on the frontier | **0.0060** at `rho* = 1/4` (keep only the 6 strongest bins) |

**The scheme is sound and fully certified, and it is ~150x too weak to kill anything.**
The half-moat restriction is what costs the value: at `rho_min = 1/16` the owned box has
area `(1/16)^2 = 0.0039`, so no contact can ever be charged more than that, against a budget
of 4.03. Even the most favourable point on the frontier captures 0.6% of the budget.

## Everything below is CERTIFIED in exact Fraction arithmetic

| object | status |
|---|---|
| charge regions of all 25 entries (`exact_charge`, `exact: true`) | **exact**, 0/270 tiles failed |
| moat certificates of all 25 entries (`moat_exact: true`) | **exact**, 0/25 failed (`exact_moats.py`, 19 s) |
| Lemma P' wall margins (`lemma_P_margin`) | exact, asserted on **every** certifier run |
| Lemma K containment (`lemma_K`) | exact per tile (slab test for WC, conv-hull test for CE) |
| bin realisability (one exactly-touching rational realisation per bin) | exact; no bin was vacuous |
| Trump contact extraction / classification | exact Fractions + a 1e-6 tolerance (below) |

**Float-only (and irrelevant to soundness):** the sweep's *search* — the float charge maps
that proposed the tile lists, the ladder rungs that *failed*, `quick_cover`'s negative
screening, and the `full_map` diagnostics in `pilot.json`. Nothing float enters a shipped
number: every shipped tile and every shipped moat was re-derived in Fractions.

### Certifier modification, and how it was checked

`a45_lib.FastExactCertifier` subclasses A23's `Certifier` and changes **one** thing: in exact
mode the static witness points are pre-screened in floats (generously: `half = 1/2 + 1e-7`
against float errors of order 1e-15, box and trig endpoints widened outward) before the exact
test. The **accept decision is still the exact `_point_in_Q_whole_box`**, and every other
discharge rule is the parent's, untouched — so the screen can only change *which* candidate is
tried, never whether a box is legitimately discharged. It is a 20–30x speedup (the parent
spends ~500 big-Fraction point tests per B&B box, which dominates everything else).

Cross-check (`../logs/plain_certifier_crosscheck.json`): all 12 WC entries plus one full CE
entry (`CE_9_2`, 24 sub-boxes, 299 s) re-run through the **unmodified** `dead_region.Certifier`
reproduce the shipped exact areas **bit for bit**, 0 tile failures.

## Structural result: CC contacts cannot be charged

Two squares meeting at a common corner `p` occupy 90+90 = 180 deg of directions around `p`;
the remaining 180 deg split into two free wedges summing to 180, so **one is always >= 90 deg**
and a legal unit square can put its own corner *at* `p`. Hence `D = B(p, rho)` is met by a
legal square for every `rho > 0`: **no CC contact admits a moat at any radius.** Confirmed on
the pilot bin (delta in [130.5,139.5]: fails at 1/4, 3/16, 1/8, 3/32, 1/16) — and the pilot
also measures 0.0659 of genuinely dead area near that contact which the scheme cannot own.
**CC is not tabulated; every CC contact is charged 0.** Conservative, not a bug.
WC and CE are unaffected: their free wedges are `alpha` and `90 - alpha`, both < 90.

## Deviations from the spec (all recorded, all conservative)

1. **CC sweep dropped** after one pilot bin (mechanism above; the A45 lead independently
   reached the same conclusion mid-run). Freed budget went into `nsub = 6` sub-binning.
2. **Contact point pinned in the frame.** The spec's CE frame lets `p` slide with `u`, which
   makes `B(p, rho)` a moving target. Here `p` is fixed (WC `(10,0)`, CE/CC `(10,10)`) and the
   *other* body moves — CE: `b` upright, top edge on `y = 10`, centre `(10 - u, 9.5)`. Same
   family; the moat box is then a fixed rational box, as Lemma M requires.
3. **Sub-binning.** Each bin is covered by `nsub = 6` tilt sub-boxes (CE additionally
   `nsub_u = 4` slide sub-boxes: 24 sub-boxes per CE bin). A certificate counts for the bin
   only if it holds on every sub-box — sound, and it recovers most of the hull-relaxation loss
   (WC [21,24]: moat 1/8 at nsub=1 vs **3/16** at nsub=6).
4. **Charges computed once on `B(p, 1/8)` and clipped.** The master charge map is built at
   `R = max(ladder)/2 = 1/8`; the charge at any smaller radius is the intersection of the
   certified tiles with the smaller box. Sound because *dead* is a pointwise property (a subset
   of a dead set is dead). This yields the **frontier** — the table at every ladder radius —
   for free; see `frontier` in `charge_table.json` and `frontier_canary` in `canary_trump.json`.
5. **Exact pass caps** `depth_max = 34`, `max_boxes = 50000` (A25's `exactify` settings;
   moats: 34 / 200000). A failure would only drop a tile/entry. 0 failures.
6. **Pilot diagnostic (b) re-run** at the bin's own resolution (`pilot_diag.py`): the first pass
   used `nsub = 1`, a weaker hypothesis that understates the dead area (CE: 0.0037 vs 0.0105).
   Both numbers are kept (`full_map` and `full_map_refined`).
7. **Trump canary tolerance.** Trump's certificate stores coordinates rounded to ~1e-11, so the
   exact SAT gaps at his contacts are tiny but nonzero (5.3e-8 walls, 1.1e-7 square-square).
   Following A43 (`check_trump_h1.py`), a pair counts as a contact iff its **exact rational**
   SAT gap is `< 1e-6`; the same tolerance decides vertex/edge incidence for the
   WF/WC/FL/CE/CC split. Every gap is recorded. The extraction reproduces A43's contact graph
   exactly (same 14 square-square edges, same 11 wall contacts).
8. **Not done (lever, not a gap):** finer CE slide bins. The 1/4-wide `u` bins are what kills
   most CE coverage — a bin's moat is capped by the *guaranteed* extent of `b`'s edge, i.e. by
   `1/2 - max u` on one side and `1/2 + min u` on the other, so the outer `u` bins have moat 0
   by construction. 8 or 16 slide bins would raise coverage (more bins charged) but not
   `rho_min` and not the per-contact magnitude, so it does not change the headline.

## Soundness invariants held throughout

* Every stored number is a **lower** bound valid **uniformly over its bin**: hull relaxations,
  dropped tiles, work budgets, and the `rho_min` clip only ever lose area.
* Lemma P' margin asserted on **every** run; for WC only the three non-hypothesis walls are
  asserted — the bottom wall *is* the hypothesis.
* Lemma K per tile: WC by the exact slab test
  `x in [10 - min sin phi, 10 + min cos phi], 0 <= y <= min(cos+sin)`; CE/CC by
  `tile subset conv(S)` with `S` a set of points certified to lie in `a cup b` for **every**
  realisation of the bin (so `conv(S) subset conv(a cup b)` always). 0 tiles were lost to the
  keeper at `R = 1/8`.
* Realisability checked per bin by exhibiting one exactly-touching rational realisation with
  exactly disjoint interiors.
