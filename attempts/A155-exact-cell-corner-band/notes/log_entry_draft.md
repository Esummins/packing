# draft of the LOG.md entry (appended verbatim at close; kept here for provenance)

## 2026-09-08 — A155-exact-cell-corner-band (Opus engineer) — done-negative

- **The K0-WIDEN pad is worth 2 % of the corner band and 4.2 % of the four-corner product, not the
  order of magnitude the exact-cell reading predicted.** (B1) re-run at five pads — 0 (fixed side),
  4.4e-4 (1e-3 slab), 2.2e-3 (5e-3 slab), 1.1e-2 (2.5e-2 slab), 2.55e-2 (the whole window, A143/A150)
  — gives band **202 / 202 / 202 / 204 / 206** of 216 cells. The full-pad row reproduces A150's 206
  and A143's 11 772-pair census exactly (`cells155` is `cells143` box-for-box at `A_W`), so the
  comparison is like-for-like.
- **The 2-crowd space at the exact cell IS thin — the level-1 cover just cannot see it.** Pose-level
  occupancy (200 realised first meeters per cell x an 8 000-pose partner pool): median p = 0.0125 at
  pad 0 against 0.1625 at the full pad (x13), **90 of 216 cells hold no witnessed 2-crowd at all**
  (64 at the full pad), and 16 cells hold no realised meeter whatsoever. (B1) kills 14. All 14 sound
  kills have p = 0 (no contradiction with the sampler); 76 p = 0 cells survive the sound test.
- **Refinement converts part of it and loses anyway.** At 12 x 12 positions x 6 tilt windows the clip
  + (B1) kill 25.2 % of 864 cells (21.5 % at the full pad) and 29.6 % of 1 728 at 12 x 12 x 12,
  against 6.5 % at level 1 — but the branching factor rises 202 -> 646 -> 1 216, i.e. the
  four-corner product rises x105 and x1 300.
- **The product at pad 0: 1 455 160 816 tuples / 181 906 396 D4 orbits**, against A150's
  1 519 380 658 / 189 934 236 at the full pad and 1 455 436 972 / 181 940 916 at the 1e-3-slab pad.
  The `wmax` re-run reproduces A150's stage table and pair-kill counts digit for digit.
- Sampled cover confirmation at every pad: 8 000 drawn realised 2-crowds -> 8 000 hits, 0 misses,
  400 exact-rational meet cross-checks each, 0 disagreements.
- **Slabs make the corner-first route worse, not better.** Because the pad is a 6 % effect, a
  slab-wise tree pays essentially the whole-window cost per slab; under `docs/budget.md` §E the slab
  count is 5 (width_max 0.012) to 115 (5e-4). **A08's root certificate does not remove the bottom
  slab**: `certs/measure_certificate_3.82.json` is an atomic measure supported in [0, 3.82]^2 with
  total 10.985474 < 11, so it kills the single side 3.82 and nothing above it (a unit square at the
  far wall of any larger container carries zero measure); A82 measured the k0_00 root LP at 3.833212
  at tau = 11.000000, eta = -0.000000, so nothing above 3.82 is free either.
- **The certificate machinery for a slab-wise corner tree does not exist**, and A99 §3.3 already
  said why: the corner-crowd nodes cannot be emitted parametrically at all (their cores are
  reach-cover box centres, not affine in s). A155 adds that the corner zone's far edge is
  `1 + w + sqrt2/2`, an irrational that MOVES WITH THE PAD, so every slab has a different cover and
  no certificate, cover-invariance argument or warm pool transfers between slabs. What does exist:
  the frozen fixed-side `verify_case` with A135 exact cores (A150 certified 4 of its 7 kills that
  way), the dilation reduction itself (Lemma K0-WIDEN, declared-reach form), and `verify_param` for
  INTERIOR k0 cells only (A99: one window-valid PASS, +5-7 % per node).
- The LP leg was **not run**: its gate was pad-0 survivors < 50 000 orbits and the measured count is
  181 906 396 orbits (1 455 160 816 tuples), 3 638x over. 0 of the 2 CPU-h LP cap spent.
- Files: `attempts/A155-exact-cell-corner-band/` (code `cells155.py` (A143's cover with the pad a
  parameter), `geom155.py`, `band155.py`, `prod155.py`, `draw155.py`; `notes/composition.md`,
  `notes/tables.md`; `figs/band155_pad0_vs_padmax.svg`).
