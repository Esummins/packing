# A270 -- the k5 lower slabs: what is certified on G1-G4, the pads, and the g4 campaign (2026-09-23)

Labels: **[T]** proved, **[T-computed]** proved modulo an exact certificate on disk, **[M]** measured, **[C]** open.
Code: `code/` (pads270, status270, cover270, pop270, reemit270, load270, run270, queue270, progress270, worker270.sh,
loop270.sh).  Data: `results/` (pads270.json, slabs270.{json,md}, cover270.json, pop270_g4.json, progress270.md,
slabs270_board.md).  Slabs (A57 T23 grid; `docs/proofs/slot_crowds.md` s.5): G1 = (3.861637, s0], G2 = (3.847016,
3.861637], G3 = (3.832450, 3.847016], G4 = [3.82, 3.832450]; s0 = 969271/250000, s-hat = 3.8770835900... lies in G1.

## 0. Headline

* **The coordinator's correction is itself wrong: k5_11 and k5_16 are NOT dead on G1.**  "census 0 alive" (A268) counts
  A57 tree ROWS.  A57's G1 level-1 cover (1,152 boxes + the NO child per class, `tree57.build_children`, rebuilt exactly
  in `code/cover270.py`) has **290 boxes with no row at all** -- k5_11 136, k5_16 154, the unfinished tails of the six
  G1 shards (`progress/k5_1*_interior_G1_s5.json`: "done 18 / total 192" when A57 paused) -- plus 6 T5'' trim pieces
  inside closed untrimmed rows.  No LP, no page run, no A96 row ever touched them [M].  And two k5_16 pages,
  **Y1117** (11 g1 start nodes left) and **Y0436** (1), are "closed" only because the board moved their pages to
  `killed/` on **pad-0 (s0-only) kills**; `load211.dead_ids()` reads `killed/*.svg` as closure, so the census and
  `fold211 --closed` (rc 0 for both) report them closed [M].
* **No record on disk reaches below 3.851408** for k5 (every pin slack <= 1e-2), so nothing certified transfers to
  G2-G4 (s.1).  A57's sides 2-4 never ran (FREEZE_TAGS.txt, A96); A96's parametric pass is a node table, not a class
  statement (s.1).  trump5: all four slabs OPEN (A269 owns them).
* **Launched**: one campaign at pad **g4 = the window** on A57's whole level-1 cover re-emitted at pin slack 9/400
  (1,666 chain pages), never-emitted boxes first.  A g4 DEAD is a statement on (3.82, s0], s-hat included, so the same
  run repairs G1 and covers G2-G4.  Benchmark: g4 costs 1.10x g2 on the same 10 roots, so g2 alone was never the move.

## 1. STATUS, per slab (exact, cited)  -- live copy: `results/slabs270_board.md` (on STATUS.md and A211's progress page)

| class | G1 (incl. s-hat) | G2 | G3 | G4 |
|---|---|---|---|---|
| k5_11 | **OPEN**: 136 unemitted cover boxes (cover270 `MISSING`) | OPEN | OPEN | OPEN |
| k5_16 | **OPEN**: 154 unemitted + Y1117, Y0436 (pad-0 kills only) | OPEN | OPEN | OPEN |
| trump5 | OPEN: A268's g1 verdicts ran on A60's 3.08e-8 records = s0-only (A256 O1) | OPEN | OPEN | OPEN (A269) |

**What IS certified on G1 (and nothing below), per leaf type** (`results/slabs270.md` is the per-page audit):
1. A57 G1 LP PASS rows (477 k5_11 + 506 k5_16 at level 1): `case-lp-certificate-v1`, pin cores a = 49/100 at s0,
   frozen `verify_case.py`; **Lemma B'** (`closed_disjoint_bridge.md` B.2) with **A_S = 3/2** reaches m >= 3.851408.
   With the census A = 5/2 it reaches 3.8616375 -- 5e-7 SHORT of the G1 bottom 3.861637 (grid json `covers_lo`
   3.8616374951): the G1 slab as the lab writes it needs A_S = 3/2 (`slot_crowds.md` s.0: A_S = 3/2 here).  [T-computed]
2. A57 logic rows (T5 / T5' tight core / T5''' pin-clip at a_pin 49/100): core meets pin core; the pin cores lie in
   the dilated pins by the same B' arithmetic.  [T-computed, float SAT test as A57 always ran it]
3. A137 / A149 exact-core LP kills (139 k5 rows) and A190's guard-line v5 kills: pin cores 1/2 - 0.0070711; B' with
   A_S = 3/2 reaches 3.858893 (G1); **with A = 5/2 only 3.866149 -- not G1**.  (A190's v5 clause is a chord-sum row;
   chords of the dilated squares only grow, so it survives the dilation [S].)
4. A205 / A206 / A209 / A211 page kills at **pad g1** (census 300/303 frontier DEAD rows + 3 by ancestor; gallery):
   the chain's pin box slot +- 1e-2 (geo178 dpin) holds F's pins iff (lam - 1)*3/2 <= 1e-2, true at lam_g1 (drift
   0.0060) -- **A211 S6 + B'**: a statement on G1 only (FC pads / CC lam are at lam_g1).  Y0384 via COUNT268 (verify268).
5. A136 / A120 composition (Y0941): YES leaf = the S02 local certificate (its own window), NO children at pin cores
   0.49 (B', G1).  [S]
6. **Not** G1: every pad-0 (zero pad, lam = 1) kill -- s0 only (A209 WINDOW-PENDING rule).  Y1117, Y0436 have nothing else.

**A57's four sides.**  Only G1 ever ran (T23; 958 / 979 level-1 rows); G2, G3, G4 are frozen since 2026-09-04
(`A57 code/FREEZE_TAGS.txt`, A96) with **zero rows**.  **A96's parametric pass** (`param96*.jsonl`): k5_11 164
full-window / 178 partial / 39 timeout-or-crash node rows, k5_16 212 / 131 / 20 -- per NODE; the class composition
(A96 item 6, a per-side cover) was never assembled, and none of the 290 unemitted boxes has an A96 row.  It closes
no slab for either class.  **Do the g1 kills transfer down?  No** [T]: Lemma INHERIT (a) needs the child hypothesis
inside the parent's; a lower pad is a WIDER family (larger lam: weaker FC pads and CC), and the 1e-2 pin boxes stop
at m = 3.851408 whatever the pad.  A g2-pad run on the 1e-2 records would be a statement on [3.851408, s0] only.

**A268's question (rowcascade241).**  A "class tree closed at g1" row is a G1 row, not a full-window row, and
rowcascade241's consumers (the K1 climb, window statements) need the full window -- a per-slab row type would force
every consumer to carry a slab.  Not cheap, not added; `rows241` untouched.  The honest source is a full-window one:
the A270 g4 campaign + the NO-child LP (s.4) would give "(C) A57's cover dead at pad g4" -- to be admitted then.

## 2. The pads (exact; `code/pads270.py`, `results/pads270.json`)

A node at pad lam is a statement about F = Delta_{s0/m} P for m in (s0/lam, s0]; the pad enters only via Theorem FC's
slot pads (lam-1)(i+1+1/sqrt2) and CC's lam (A211 S6).  Pins: F's pin k is centred at slot_k(s0) + (lam-1)alpha_k.

| pad | lam | FC pad i = 0 / 1 / 2 | drift (lam-1)*3/2 | pin slack of the records | covered by the 1e-2 records? |
|---|---|---|---|---|---|
| g1 | 3877084/3861637 | 0.006829 / 0.010829 / 0.014829 | 0.0060002 | 1e-2 (A57's, on disk) | yes |
| g2 | 969271/961754 | 0.013343 / 0.021159 / 0.028974 | 0.0117239 | 3/250 (margin 2.8e-4) | **no** (0.0117 > 0.01) |
| g3 | 1938542/1916225 | 0.019882 / 0.031528 / 0.043174 | 0.0174695 | 9/500 (margin 5.3e-4) | no |
| g4 | 969271/955000 (= 'window') | 0.025510 / 0.040454 / 0.055397 | 0.0224152 | 9/400 (margin 8.5e-5; A269's) | no |

**The brief's arithmetic.**  T_K(1e-2) = 0.0257 is trump5's Lemma SEAM number (depth from s-hat); the k5 analogue is
the drift column.  Either way the 1e-2 records do NOT cover G2 (depth 0.0300 > 0.0257; drift 0.0117 > 0.01): G2, G3
and G4 all need re-emission.  Hypothesis of a re-emitted record (`reemit270.py`): HYP(nid, delta, lam) = "P at a
side m in (s0/lam, s0] with the class pins upright at slots(m); F's pin k within delta of slot_k(s0); F's H in the
record's box" -- (i) is implied by the class for every m of the slab.  **Price of re-emission**: rewriting records is
seconds (1,666 in < 1 min); nothing inherits (wider pins), so every page kill is re-proved; LP leaves are the cost.

**Corollary B'' (sharp slot form) [T].**  B''s proof puts the core's bounding box (half-width 1/2 - rho) inside the
dilated pin, which has half-width lam/2, not 1/2: the exact condition is (lam-1)|alpha| + 1/2 - rho < lam/2, i.e.
**(lam - 1)(A_S - 1/2) < rho**.  With A_S = 3/2: lam - 1 < rho.  So A57's LP PASS and T5 leaves (rho = 1e-2) reach
m > s0/1.01 = 3.838697: **G2, not G3** (the exact-core rho = 0.0070711 reaches 3.849862: not G2).  The chain keeps the
conservative box form (its pins are role boxes, not cores).  B'' is used ONLY to spare A57's PASS / T5 leaves on G2.

## 3. The g4 campaign (the run)

**Population** (`pop270.py`): A57's cover rebuilt at pin slack 9/400: per class 1 NO child + 1,156 / 1,157 YES boxes;
366 (k5_11) / 281 (k5_16) are T5 logic kills at 9/400 cores (window-valid by B'); **1,666 chain pages** re-emitted as
`<id>_r270w4` (box from the 9/400 cover, pins +- 9/400).  Priority: **1** no G1 row or s0-only (k5_11 137, k5_16 161),
**2** G1 ALIVE/FAIL rows closed by a page kill or ledger (163 / 209), **3** G1 PASS rows (476 / 500), **4** G1 logic
rows that are not logic at 9/400 (14 / 6).  What each slab then needs (progress270): **G1** = tier 1 DEAD; **G2** =
tiers 1-2 DEAD + B'' for PASS / T5 leaves + the NO child (rho 1e-2, B''); **G3, G4** = every tier DEAD + the 9/400
logic kills + the **NO-child LP at pin cores <= 1/2 - 0.01495** (B''; 1/2 - 9/400 by B') -- one LP per class, NOT run.

**Benchmark [M]** (A268 levers on: count268, leaf268; wall 480 s; `logs/bench/`):
* 10 k5_16 frontier roots, pad **g2**, records 3/250: 9 DEAD in 27-304 s, Y0355 ALIVE at the wall; 1,621 s in all.
* the same 10, pad **g4**, records 9/400: 9 DEAD in 49-343 s, Y0355 ALIVE; 1,789 s = **1.10x g2**.
* cover sample at g4: 4 never-emitted boxes DEAD in 13-451 s (+ Y0371 50 s through the worker path); PASS rows 3/4 DEAD
  in 37-281 s, Y0979 ALIVE; T5-logic boxes crash the stage-0 certificate writer (cert203 KeyError) -- they are logic
  kills at 9/400 and are NOT in the population.  COUNT268: 38 INFEASIBLE dumps, 38 VERIFIED.
* 19 chain pages: mean 182 s, 17/19 DEAD inside 480 s.  (At g1 without the levers the same frontier cost mean 2,714 s.)

**Price.**  303-node frontier at g2: ~14 CPU-h + tail -- but not a slab statement.  The g4 campaign: 1,666 pages,
pass 1 at wall 1800 s ~ 1,666 x (0.9 x 150 + 0.1 x 1800) s = **~146 CPU-h upper**, tiers 1-2 (670 pages) ~35-60 CPU-h.
Launched with a hard **150 CPU-h cap** (progress270 writes STOP + STOP_LOOP past it).

**Launch.**  `loop270.sh 4 1800` (4 workers, BelowNormal, affinity 0xFFFF inside run211, BLAS 1, 3072 MB gate, lab
ceiling 12), queue270 (Lemma INHERIT over A270's certs only; STALLED invariant -> results/stalled270.txt; a start node
that crashes twice -> results/crashed_out270.txt), per-shard commits, results/progress270.md.  **STOP**: touch
`attempts/A270-k5-lower-slabs/logs/STOP_LOOP` (after the pass) or `logs/STOP` (after each start node).  **RESUME**:
remove both, relaunch the same line; the pass number continues from results/ran270.txt.

## 4. Obligations, fixes, and what was wrong in the brief

* **O-NO**: the NO child per class at pin cores 1/2 - 0.015 (B'') or 1/2 - 9/400 (B'): `tree57.py --name k5_1x
  --pin_delta 0.0225 --max_children 1 --tag W4` writes into A57's tree dirs -- the coordinator's call (A57 is paused).
* **Census fix (flag-gate on the shared chain, not done here)**: `load211.dead_ids()` should not count a `killed/`
  page whose only kills are pad-0; `load211.census()` should enumerate the cover, not the rows.  Until then the census
  line on A211's progress page carries A270's caveat (progress211.py patched, installed by rename).
* Board: `status_gallery.py` gained a "slab (A270)" column (the displayed kill's slab: G1 / s0 only / ?) and the
  per-slab block; display only -- no verdict, no page move changed.
* COUNT268 dumps of the benchmark first landed in A268's certs (count268's default dump dir); moved to
  `certs/count268/` (map: MOVED_FROM_A268_certs.json), references rewritten in A270's own files; run270 now sets
  A268_DUMP_DIR.  One other `count268_page_*.json` in A268's certs is not A270's (left alone).
* **Wrong in the brief**: (i) "dead on G1 (incl. s-hat)" -- open (290 + 2); (ii) "T_K(1e-2) covers G2?" -- no, and T_K
  is trump5's constant (A = 3/2 via Lemma SEAM), the k5 test is the drift; (iii) the A57 G1 slab (3.861637, s0] needs
  A_S = 3/2, not the census 5/2 it was derived with (5e-7 short); (iv) "launch g2": g2 on the current records is a
  statement on [3.851408, s0] only, and g4 costs 1.10x g2 -- the campaign runs g4.
