## 2026-09-08 — A165-cascade-l1_104 (Opus engineer) — done-negative

**The PI's CASCADE on the k0_00 cell `l1_104`, built as an explicit case tree with a certificate at
every forcing step, and the Trump-image cell `l1_153` as the canary.  The cascade is sound, the
canary survives it, and it does not close the cell — the chain breaks at a named place, and three
reusable things come out.**

### The canary first (`l1_153`, which a real 11-family reaches — image `g4`, square 9)

* K0-BLOCKED holds for `g4` **only because of the K0-WIDEN pad**: widened-corner meeter counts
  BL 3, BR 2, TR 2, TL 2; on the plain unit corner boxes BL 1, BR 2, TR 1, TL 1.
* Every real FREE meeter of every corner is located inside an OPEN box of that corner's cover
  (0 unlocated at all four corners): no cover step discards the real family.
* **`M(TR) = 1` at `l1_153`** — its `H` *is* a TR meeter, penetrating 0.477 / 0.290 past the widened
  cell's corner, and A141's cover and A161's exact SAT agree.  So its TR crowd may be
  `{H, one free meeter}`, the real family lands in that mixed case, and the case survives both pair
  prunes.  This is the discriminating fact of the whole attempt (below).
* All four wall rows accept every real case pair: top 1/1, right 1/1, bottom 3/3, left 3/3.
* The only leaf that kills anything — the five-box spread LP at budget 6 — leaves the canary's own
  real four-tuple **ALIVE at τ = 6.7348, η = +0.7348**, while 4 of 4 random `l1_104` tuples die at
  η = −1.0000.  **CANARY PASS at every step run.**

### `l1_104`: the tree, and where the chain breaks

Root: A115's converged record, τ = 10.000000 against budget 10, zero slack.

* **C1 (structure, certified).** (R6) gap `s0 − 2(1 + w) − √2 = +0.41185029 > 0`; and **`M(c) = 0` at
  all four corners** by A161's exact full separating-axis test over `H`'s parameter box (A141's
  coarse cell-normal test proves it only at BL/BR/TL).  Hence
  **`11 = 8 FREE corner meeters + H + exactly 2 further squares`**.
* **C2 (the PI's step (a), CONFIRMED).**  Complete prefix-code covers at split depth 8 (Kraft sum
  exactly 1, checked): TR **82** open boxes against TL 238, BL 248, BR 191 — `H`'s polygon core
  (area 0.655248, 40 certified vertices) sits on the TR diagonal and removes two thirds of the TR
  approach.  Pairs after A118's always-overlap and A141's shared-rational-point prunes: TR 3 403 →
  522 → **500** cases; TL 7 050, BL 8 194, BR 3 879.
* **C3 (the PI's step (b), CONFIRMED as a bound on 37 % of the branching).**  On **185 of the 500** TR
  cases both meeter boxes carry a **certified** `minchord ≥ 1` on the best top-wall line, so
  `rhs(l) = s0 − 2 = 1.8771` and **β = 1**: at most ONE further square of the family fully crosses the
  top strip — exactly the PI's sentence.  Over all 500 cases the top rhs runs 1.6740 / 1.9396 / 2.7963
  (min / median / max) and there are **0** row kills at three boxes.  The PI's picture of the pair is
  right as well: **434 of 500** cases are one meeter up the right wall past `H` plus one along the top
  wall, 66 are two top-wall meeters, and none is diagonal.
* **C4 (the PI's step (c), BREAKS) — and the new leaf it produced.**  A144's row read on each wall
  strip with the two corner crowds that wall can see is a sound predicate on the EDGES of the
  four-corner cycle, so the survivor count is a transfer-matrix contraction (A150 §4) and the product
  is never enumerated.  Measured with 32 exact rational lines per wall: top (TR,TL) kills **4.09 %**,
  right (TR,BR) 0.45 %, bottom (BL,BR) 0.49 %, left (BL,TL) 0.52 %; four-cycle survivors
  **1.0584·10¹⁴ of 1.1204·10¹⁴ (94.5 %)**.  *Why*: by **Lemma (TOP)** (`c_y ≤ s0 − h`, `h ≥ 1/2`, so
  no admissible square lies entirely beyond a guard line within 1 of a wall; at `y_L = s0 − 1 − w`
  the exception needs tilt within **1.4809°** of an axis) a TL meeter must CROSS the top line — but
  its chord there may be arbitrarily small.  So "β = 1" and "TL carries two meeters" are not in
  contradiction: the second TL meeter is a *shallow* crosser and costs the row ≈ 0.
* **C5 (area).**  `|U|` at 3 boxes = 0.189–0.203 against `B0 = 4.031780` — 20× short, and A164 (which
  landed the same day, `done-negative`) shows the charge only starts to bite at 9–10 conditioned
  boxes.  The cascade cannot borrow an area charge to repair step (c).
* **C6/C7 (LP).**  `{H, TR_a, TR_b}` at budget 8: **τ = 8.000000 exactly, η = 0.0000, 3 of 3** — two
  cores stacked at one corner plus an interior core buy *nothing*.  `{H}` + ONE meeter box per corner
  at budget 6: **τ = 5.000000, η = −1.0000, 4 of 4 converged kills, 1 PASS under the FROZEN
  `verify_case.py`** (the other three are the lab's standard "LP-dead, certificate pending").
* **C8 (the price).**  The spread hypothesis is a genuine COVER of K0-BLOCKED, so its cost is the
  product of the cover sizes.  Ladder on `l1_104`: depth 3 (`a ≈ 0.048`, product 3 072) η **+1.0,
  +3.0, +2.5, +2.0**, 0 of 4 kills; depth 4 (`a ≈ 0.054–0.083`, product 49 152) η **+1.0, +2.0**, 0 of
  2; depth 8 (`a ≈ 0.300`, product **9.24·10⁸**) η −1.0, 4 of 4.  So the LP decides only where the
  product is 10⁹ nodes ⇒ **≥ 10⁷ CPU-h** against `docs/budget.md`'s 9 400–12 000 k0 row.  A150's
  crossover, reproduced on a single cell.

**Verdict: `l1_104` SURVIVES.**  The corner-first line stays closed (A143, A150, A154, A155, A159);
the cascade is not a route past it.

### What keeps

1. **The `M(c) = 0` upgrade**, one line: replace A141's `box_misses_cell` by A161's
   `box_misses_cell_exact` in `polylane.cond_can_meet`.  On `l1_104` it turns `M(TR)` from *undecided*
   into a certified 0, which is what licenses corner-pair branching; on `l1_153` it correctly returns
   1.  Re-run corpus-wide.
2. **The four-wall chord-row product** — sound, exact, seconds to run, no cover refinement, and it
   composes with any product cover as a 5 % pre-filter.
3. **Lemma (TOP)**, `n`-general: no admissible unit square lies entirely beyond a wall guard line
   placed within 1 of that wall, so a wall row is a *complete* charge on the strip's occupants — and,
   read negatively, that is exactly why the row is weak (crossing is forced, a chord ≥ 1 is not).
4. **Spread beats stacked.**  1 core at a corner: η −0.044 (A143); 2 cores at the same corner: −0.083
   (A143); 2 cores at one corner + an interior core: **0.0000** (A165); 4 cores at 4 corners: −1.0 to
   −6.0 (A150), and −1.0 uniformly with `H` added (A165).  Rule for every future node: spend the
   conditioning budget on cores that are pairwise far apart, never on a second core at a corner that
   already has one.
5. **The named gap**: the cascade needs a leaf that charges a **shallow** corner meeter — large
   footprint in the corner cell, small chord on the wall line.  It is the same gap that stalls A161's
   Lemma CL on `k5_16_interior_Y0842/BL(1,0)` and the 28-of-44 A141 near-misses with realised
   two-crowd witnesses.  A164 has now ruled out the area charge as the candidate.

### Files and discipline

`attempts/A165-cascade-l1_104/` — `BRIEF.md`; `code/{cas165,cascade165,rowprod165,lp5165,trump165,
tree165,fig165,check165,certs165,probe165}.py`; `results/{cover_*,pairs_*,geom_*,rowprod_*,lp3_*,
lp5_*,probe165_*,cascade165.jsonl,check165_*,cert_manifest_*}`; `certs/` (the `cascade_Mzero_v1`,
`cascade_cover_v1` and `cascade_row_v1` certificates plus the four `case-lp-certificate-v1` files and
their verifier reports); `notes/{cascade.md,doc_lines.md,registry_row.md,log_entry.md}`;
`figs/cascade_l1_104.svg`; `logs/`.  Plus the registry row, this entry and one paragraph in
`docs/residue_ledger.md` §4.  The independent checker `code/check165.py` (C1–C9: the pad and (R6),
cover completeness as a prefix code with the split rule replayed, every discharge reason re-derived
by independently coded exact tests, both pair prunes, `M(c)` by an independent SAT plus 5·10⁴ sampled
poses per corner, every chord-row certificate re-derived in the HARD direction, the (TOP) arithmetic,
and a falsification pass in which every drawn corner-meeting pose outside the cover must land in a
`witness` leaf and contain that leaf's rational point) reports **ALL_OK, 0 failures**.

Discipline: ≤ 2 BelowNormal processes at affinity `0xFFFF`, the 16-process box ceiling polled before
every launch — the box carried 14–19 other lab pythons throughout, so every run was serialised and
two queued runs (a depth-6 rung of the ladder and a depth-7 cover) were **dropped rather than
launched over the ceiling**; this attempt's own `PAUSE` was used once to stop the `lp3` sample
cleanly; `PYTHONDONTWRITEBYTECODE=1`; no recursive deletes; the frozen verifier untouched.
**≈ 1.9 CPU-h of the 4 CPU-h cap.**  One read-only slip was found and repaired inside the attempt:
A150's `lp150.certify` writes into `lp150.BASE/certs`, so the first four LP certificates landed in
`attempts/A150-four-corner-product/certs/`; they were **moved** (never deleted) into
`attempts/A165-cascade-l1_104/certs/`, A150 is byte-identical to its prior state, and both A165
drivers now rebind `lp150.BASE` at import so nothing can be written under a prior attempt again.
