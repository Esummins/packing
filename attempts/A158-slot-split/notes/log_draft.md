# A158 — LOG.md entry draft (tallies in [[…]] filled from results/summary158.json)

## 2026-09-08 — A158-slot-split (Opus engineer) — done-mixed
- **Task**: the PI's tautologous YES/NO split on the near-simple slot box
  `S(r, tt) = {centre within r of the exact slot centre, tilt within tt of 0/90}` — YES: some
  square's pose is in `S`, killed by A141's lane leaf with `K'(S)` as an extra obstacle; NO: no
  square's pose is in `S`, a `caselp` `NoFam(S)` plus an exact-core LP re-solve — on
  `c0_Y0076 TL(0,0)` first, then over the alive A57/A60 nodes whose LP **dual support** puts
  weight ≥ 0.5 into some usable slot's `S` box. Five more cells were named by the coordinator
  mid-run: `c0_Y0787 BR(0,1)`, `c0_Y0959 TR(0,1)`, `k5_11_interior_Y0130 TR(0,0)`,
  `k5_11_interior_Y0147 TR(0,0)`, `k5_11_interior_Y1110 TR(0,0)`. READ-ONLY on every campaign and
  on A112/A118/A132/A135/A136/A141/A157; new files only under this attempt plus three named
  appends.
- **The leaf is right, and it is cheap.** `1 + LANE_K'(C | S) + M(C | S)` bounds the number of
  squares meeting `int C` once some square's pose is in `S`: the `find_witness` discharge against
  `K'(S)` **identifies** the pose with the `S`-square (`PolyCoreT5.shared_point_same_square`)
  rather than contradicting it, so the extra core costs nothing. Every piece is deployed already —
  `yes_or_no` with a one-element list, `noneIn_of_clamped` for the NO bridge, A136's `zone_sub_box`
  on the written rationals, the frozen `verify_case.py`, A141's cover and `M` machinery
  (`notes/leaf.md`, with the Lean shape and the ONE new named obligation
  `slot_singly_met_of_someIn`). A120's clauses A2/A3 are vacuous at `|L| = 1`.
- **`k6_23` verified**: the `trump5 TL(0,0)` extension is FULL-window (`[191/50, 969271/250000]`),
  converted by **A114** (A56 scoreboard `a114.rows_converted_to_full_window`, rule `soundness.md`
  P7 + A86 T4). A118's usable-slot table stands.
- **The population**: **1,238 of the 1,693 alive A57/A60 nodes (73 %)** keep `tau ≥ budget` on a
  dual square sitting in some usable slot's `S(0.10, 10°)` box (A57 1,079 — k5_11 575, k5_16 504;
  A60 159; by level L1 962 / L2 243 / L3 19 / L4 14). Commonest slots: `k5_11 TR(0,0)` 420,
  `k5_11 BR(0,1)` 219, `k5_11 TL(1,0)` 205, `k5_16 BR(0,1)` 184, `k5_16 TL(1,0)` 166.
- **`c0_Y0076 TL(0,0)` — NO child DEAD, YES child refuted.** …
- **The YES child does not exist anywhere measured.** …
- **The NO child is real but needs a box two orders of magnitude bigger.** …
- **Every NO kill is quoted against a control** …
- **Cost** …
- Files: `attempts/A158-slot-split/` …

## REGISTRY.md row draft

| A158-slot-split | 1 Opus engineer, ONE BLAS-pinned process at a time at Normal priority /
affinity `0xFFFF` (box ceiling 16 lab pythons, held throughout; READ-ONLY on every campaign and on
A112/A118/A132/A135/A136/A141/A157) | run the PI's tautologous YES/NO split on the near-simple slot
box `S(r, tt)` — YES killed by A141's lane leaf with `K'(S)` as an extra obstacle, NO by a
`caselp` `NoFam(S)` and an A135 exact-core LP re-solve — on `c0_Y0076 TL(0,0)` and then on the
alive A57/A60 nodes whose LP dual support puts weight ≥ 0.5 into some usable slot's `S` box | … |
done-mixed | … | attempts/A158-slot-split |
