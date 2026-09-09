# A57 / A96 — PAUSED v3, 2026-09-08 06:45 PDT (end of the A137 night-shift window)

Nothing of A137's is running. The pause used the **sentinel path**
(`attempts/A137-night-shift-2/PAUSE`, the scoped sentinel of v2 §7a), so every worker finished its
node, wrote its row and exited; nothing in flight was discarded. A57's **own** `PAUSE` was never
touched all night and still carries A123's text — so "the A57 PAUSE is set" still does not mean
"nothing is running": **check pids.**

Supersedes v2 (2026-09-07 08:00), archived verbatim as `PAUSED_v2_archived.md`. v2's §5(e)(f), §6,
§7, §7a and §8 remain the operating text except where §§A–E below amend them, and A141's
2026-09-08 addendum is carried forward at the end of this file. **Read §C first if you are about to
resume: three of the night's findings change what the resume block should say.**

---

## A. What ran (2026-09-07 22:42 → 2026-09-08 06:45)

Owner A137 (Opus). Everything ran through **wrappers**: `tree57.py`, `lpbox.py`, `trim57.py`,
`pinguard.py`, `caselp.py` and both frozen verifiers were imported unchanged and never edited.
Drivers and the one-page method note: `attempts/A137-night-shift-2/code/`, `notes/method.md`.

| lane | driver | procs | what |
|---|---|---|---|
| T1 fold-in | `fold137.py` | 0 (seconds) | the day's kill ledgers folded into A57 and A60 state |
| (a) exact-core re-emission | `run137.py` → `node137.py` → A135's `emit135.certify` | 2 | 163 surviving-ALIVE nodes re-solved with A135's exact cores, frozen `verify_case.py` |
| (b) fresh level-1 emission | `emit137.py` (geometry) + the same LP workers | 1–3 | 893 children of 7 shards through pinguard/T5″/T5‴/T5⁗, then the LP on the clipped box |
| (c) level-2 deepen | `emit137.py --mode deepen` | 0 LP | 2,141 level-2/3 children screened by geometry; their LP queue is untouched |
| scaler | `scaleup137.ps1` | — | adds a worker whenever the box drops to ≤ 14 python processes; hard stop 06:00 |

Box discipline held all night: **≤ 16 python processes** (the scaler refuses to launch above 14 so
the worker and its one node child fit), BLAS pinned to one thread per child,
`PYTHONDONTWRITEBYTECODE=1`, free physical never below **6.9 GB** (gate 3 GB) and free commit never
below **79 GB** (gate 6 GB), 0 memory holds, 0 orphans, no recursive delete, no pidfile or foreign
sentinel touched. **Per-node process wall 1,500 s**, and it fired 3 times — recorded `WALL-CAP`,
**never a verdict**: those nodes keep their prior state and were left unclaimed.

## B. State — v2 → now

**Pre-night A57 corpus, 2,760 rows** (v2's board re-derived per tree, `code/state137.py`):

| tree | n | ALIVE | FAIL | PASS | logic kill | work-owing | now DEAD |
|---|---|---|---|---|---|---|---|
| `k5_11_interior_G1` | 801 | 139 | 47 | 362 | 253 | 186 | **56** |
| `k5_11_interior_G1_D2` | 507 | 55 | 75 | 209 | 168 | 130 | **70** |
| `k5_11_interior_G1_D2_D2` | 42 | 4 | 6 | 29 | 3 | 10 | **6** |
| `k5_11_interior_G1_D2_D2_D2` | 32 | — | 6 | 8 | 18 | 6 | **6** |
| `k5_11_interior_L1` | 196 | 17 | 4 | 103 | 72 | 21 | **5** |
| `k5_11_interior_L1_D2` | 23 | — | 1 | 14 | 8 | 1 | 0 |
| `k5_16_interior_G1` | 920 | 212 | 37 | 471 | 200 | 249 | **68** |
| `k5_16_interior_G1_D2` | 118 | 4 | 10 | 72 | 32 | 14 | **9** |
| `k5_16_interior_L1` | 113 | 7 | 8 | 67 | 31 | 15 | **6** |
| `k5_16_interior_L1_D2` | 8 | — | — | 8 | — | 0 | 0 |
| **total** | **2,760** | **438** | **194** | **1,343** | **785** | **632** | **226** |

> **The work-owing population is 632 → 406** (−35.8 %) after the fold-in and the exact-core
> re-emission. On top of that the trees gained **1,161 new rows** emitted tonight (§C.2), of which
> **947 are already dead**.

## C. The night's three findings, in the order they change decisions

### C.1 The exact pin core is the lever, and it is a POPULATION rate now, not a sample

A135's named chore is done for a third of the population: **163 of the surviving ALIVE nodes
re-solved with exact certified-maximal cores; 46 certified dead by the FROZEN `verify_case.py`
with nothing changed but the half-side written into `cores`.** 15.5 CPU-h, median 426 s per node.

| result | n | note |
|---|---|---|
| **PASS (certified kill)** | **46** | frozen verifier, exact cores; ledger `results/superseded_by_exactcore_A137.jsonl` |
| NO-KILL (τ ≥ budget) | 87 | node unchanged |
| LOST-KILL-ON-RESOLVE | 16 | τ < budget at first solve, ≥ budget after witness feedback |
| TOO-TIGHT | 10 | τ < budget but the rounded measure ≥ budget |
| FAIL (verifier holes) | 2 | the `verify_case_v3` candidates — §D.3 |
| WALL-CAP | 2 | **not a verdict** |
| **kill rate** | **46 / 161 decided = 28.6 %** | |

**A145's `frac_exact` predictor gates at the top and NOT at the bottom.** The queue ran in
`frac_exact` descending order, so the bands below are measured out of sample against A145's n = 12:

| band | kills | rate | A145's reading |
|---|---|---|---|
| ≥ 0.60 | 25 / 66 | **37.9 %** | 4 of 5 — confirmed, and the band to run first |
| 0.45–0.60 | 6 / 30 | 20.0 % | — |
| **0.30–0.45** | **15 / 63** | **23.8 %** | **"0 of 7 below 0.45 moved at all" does NOT survive n = 63** |
| < 0.30 | 0 / 2 | — | untested tonight (2 nodes) |

Keep ranking by `frac_exact` — the top band is ~1.6× the rest — but **do not skip the 0.30–0.45
band**, which is 15 certified kills the A145 rule would have discarded. The `< 0.30` band
(118 nodes) remains untested; "provably gain nothing" is untested, not refuted.

### C.2 Emission through the hooks — geometry kills a quarter before any LP

`emit137.py` runs, at every child: `pinguard.classify` **at the exact pin core**
`33873816211/68719476736` (T5/T5′) → `trim57.trim_box` (T5″, inside `build_children`) →
`pinclip.clip_node` at that same core (T5‴) → the polygon-vs-pin-core kill (T5⁗) → the LP on the
**clipped** box with exact cores. Every field v2 §6 demands is persisted (§D.1).

| level | children screened | T5′ (exact core) | T5‴ clip | T5⁗ polygon | dead by geometry | to LP |
|---|---|---|---|---|---|---|
| 1 (7 shards) | 893 | 218 | 27 | 0 | **245 = 27.4 %** | 648 |
| 2 (deepen of the 305 surviving ALIVE) | 1,690 | 348 | 116 | 0 | **464 = 27.5 %** | 1,226 |
| 3 | 444 | 66 | 16 | 0 | **82 = 18.5 %** | 362 |
| 4 | 7 | 7 | — | 0 | 7 | — |
| **all** | **3,034** | **639** | **159** | **0** | **798 = 26.3 %** | **2,184 queued** |

Of the 648 level-1 children that reached the LP, **189 were solved: 149 PASS (78.8 % of decided),
22 ALIVE, 12 LOST-KILL-ON-RESOLVE, 5 TOO-TIGHT, 1 WALL-CAP**, 14.9 CPU-h, median 201 s.
459 level-1 and all 1,588 level-2/3 LP jobs are queued and untouched;
`code/mkqueue137.py` rebuilds the remainder into `results/queue_bc.json` in priority order.

**The level-2 rate the schedule rests on.** `docs/budget.md` credits level 2 with **13.74 %**, the
offline T5″-EMPTIED rate *incremental over T5′* (A124 `control124.json`). Tonight's level-2
children die by geometry at **27.5 % (464 of 1,690)**; the part directly comparable to 13.74 % —
the clip, incremental over a T5′ now run at the exact core — is **116 / 1,342 = 8.6 %** at
`nsub = 1`. The exact pin core moves boxes out of the incremental bucket and into T5′, so the two
numbers are not the same quantity. The decision-relevant one: **twice the assumed fraction of
level-2 boxes dies before any LP**, measured on the forward-looking population (children of the
nodes that survived tonight's fold-in), which is the least favourable one.

### C.3 An id is not a node — the fold-in is TAG-AWARE, and two of A142's kills are restricted

`k5_11_interior_Y0041_D02` is a node of the **L1** tree (eps-fat pins, core 1/2 − 2.98e-8) *and* a
different node of the **G1** tree (slack pins at δ = 1e-2, core 0.492928902). A kill computed at a
pin core of half-side `a` transfers to a node whose pins guarantee at least `a` — **downward only**.
A `board.py`-style last-wins id map silently attributes a kill to the wrong tree.

`fold137.py` records `applies_to_tags` / `not_applicable_to_tags` and `pin_core_model` on every
ledger row and refuses a tag whose own core is smaller than the model. **Two of A142's 17
exact-clip kills — `k5_11_interior_Y0041_D02` and `k5_16_interior_Y0449` — are written at
`a_pin = 16777215/33554432 = 0.49999997` against the L1 tree's eps-fat pins and do NOT kill the
G1-tree node of the same id**, which is the tree the live campaign is descending. Both certificates
are correct for the node they name; A142's ledger and v2's addendum should be read with that
restriction.

### C.4 What the fold-in bought, by source

`results/superseded_by_backlog_A137.jsonl` (492 A57 rows) + `superseded_by_exactcore_A137.jsonl`
(46 rows); `attempts/A60-trump5-campaign/results/superseded_by_backlog_A137.jsonl` (89 rows).

| source | rows folded | of which NEW (node was ALIVE/FAIL) |
|---|---|---|
| A131 pin-clip backlog | 132 | 111 |
| **A141 slot-lane (final ledger)** | **187** | **7** |
| A142 exact-clip | 17 | 12 (2 restricted to the L1 tree, §C.3) |
| A145 certified resolves | 9 | 7 (2 frozen, 5 v3) |
| A135 polycore + LP kills | 8 | 6 |
| monotone descendants | 139 | 0 (all were already PASS/logic-dead) |
| **A137 exact-core re-emission** | **46** | **46** |
| A144 guard lines | **0 — LP-only, no certificates, deliberately not folded** | — |

**Certificates are scanned directly, not just ledgers** (A148's rule, 2026-09-08 06:50: every
`*.clipkill.json` under `attempts/*/certs/**` is a kill record; `*__exall.json` is NOT, since it
exists on LOST-KILL / TOO-TIGHT / FAIL too). `fold137.py` now walks those files. On this box the
scan added **0 new ids**: all 342 clipkill certificates are accounted for — A131 132, A142 51
(17 A57 + 34 A60, matching its two ledgers exactly, 0 certs without a row and 0 rows without a
cert), A137's own 159 fresh-emission kills (excluded from the fold: they are new children recorded
dead at emission, not supersessions). The scan did surface **3 certificate ids that exist in no A57
or A60 corpus** — `f1_L16_0000`, `f1_L19_0002`, `slack0.02_c0_Y0411` — which belong to other trees
and are listed in `results/foldin137.json` under `unknown`. So the "~150 ids missed" does not
reproduce against these files; whatever list showed it was built from a narrower glob.

**A141's slot-lane kills are, for A57, overwhelmingly cheaper proofs of nodes already certified:
180 of the 187 A57 rows were already `PASS`, and only 7 (5 ALIVE + 2 FAIL) close open work.**
("243 NEW" in A141's report is new *relative to the clip kills*, not relative to the corpus's
existing verdicts.) They are folded with leaf `slot-lane (A141)`, their certificate path and A141's
own checker recorded, and `pin_core_model = null` (the leaf is not a pin-core argument). A141's own
caveat (A118-O1: a LANE kill excludes class-S packings with EXACT pins, not the δ = 1e-2 slack
family) was ruled not a blocker for A57's composition by the coordinator on 2026-09-08; that ruling,
not this fold, is what the 7 new kills rest on.

## D. Amendments to v2

### D.1 §6's MUST-FIX is fixed for everything A137 emitted — and only for that

Every row `emit137.py` writes carries `trim_excluded` (each excluded interval with its witness pin)
and `trim_from`, plus `clip_from`, `clip_kept`, `clip_kept_vol`, `clip_nsub`, `clip_delta`,
`clip_a_pin`, `clip_n_empty`, `clip_refused`/`clip_reason` and `pin_core_exact`. The θ-width
reconstruction trick is not needed for these rows. **`tree57.build_children` is still unpatched**,
so anything emitted by `tree57.py` or `deepen.py` in future still loses the ledger — the fix belongs
in `build_children` (two lines: copy the fields into `rec`). One field is still empty: `clip_pins`
is `[]`, because `pinclip.clip_node` returns the witness pins only inside its per-sub-bin traces;
the certificates (§D.2) carry `witness_pins` in full.

### D.2 Every clip kill tonight has a replayable certificate, independently checked

`code/clipcerts137.py` re-derives each T5‴ kill from its recorded box at `nsub = 8` (emission clips
at `nsub = 1`; the clip is monotone in the sub-bin count) and writes A131's
`pin-clip-kill-certificate-v1` with the full per-sub-bin trace, then runs **A131's own independent
checker**: **159 / 159 PASS, 1,908,000 sampled poses, 0 pin-free hits.** Certificates in
`attempts/A137-night-shift-2/certs/clipkills/`, ledger `results/clipkills137.jsonl`. `a_pin` is
A135's exact core and `pin_delta` the matching `1/2 − a_pin` (what A131's checker tests); the node's
own emission slack is carried separately as `node_pin_delta_actual = 0.01`.

### D.3 `verify_case_v3` was NOT used tonight

The brief allows it only where the frozen verifier FAILs with holes. Two nodes reached that state
(`FAIL`, §C.1) and were left for the v3 lane rather than certified here, because a v3 kill of the
kind A135 and A145 obtained needs the `polycores` field in the LP as well as in the verifier
(A144's finding: the frozen chain cannot even EMIT such a measure). Every kill recorded tonight is
frozen-verifier or pure geometry. The two FAIL ids are in `results/exact_reemit_w*.jsonl`.

### D.4 T5⁗ (polygon vs pin core) fired ZERO times at emission on A57

0 of 3,034 children. It is not dead weight — it is the leaf that kills A135's `Y1038` and, per A148
this morning, `c0_Y0254` and `c0_Y0168` in **A60**, where A137 never ran it. **Run the polygon kill
over A60's population**; on A57's freshly emitted children the clip at the exact core dominates it.

### D.5 `Y0381` is no longer a shard-stopper

v2 §5(a)(e): `k5_16` shard 0 could not advance because it re-picked the wedged node on every
restart. Under a **process** wall the wedge costs 1,500 s once and the shard moves on: shard 0 was
re-emitted tonight (129 children screened, 33 T5′ + 3 clip kills) and three nodes across the night
hit the wall and were recorded `WALL-CAP` with no verdict. The wall — not a fix to `lpbox.py`, which
must not be edited — is the deployable answer.

### D.6 The scaler bug worth not repeating

Between 02:16 and 02:36 the scaler launched three workers onto a queue whose every remaining job was
already **claimed**, because it computed "jobs left" from the queue's out-file rather than from the
claims; each exited in under a second (~30 min of one slot). Fixed by `mkqueue137.py`, which
rebuilds ONE combined queue (fresh level-1 first, then the level-2 deepen children) with recorded
*and claimed* ids dropped, and by the scaler launching only when that count is positive.

### D.7 The shared git index swallowed a checkpoint

At 23:15 a `git add` of A137's 200 files was committed by **another agent's** `git commit` seconds
later (`46b99756`, A148) — the hazard v2's launch note warns about, now observed a third time.
Nothing was lost, but the attribution is wrong. **Use `git commit -m … -- <pathspecs>`**, which
commits the working-tree content of the named paths and ignores whatever else is in the shared
index; never `git add` then `git commit` as two steps on this box.

## E. Resume — what to run first next time

1. **Finish the exact-core re-emission.** 142 of the 305 surviving-ALIVE nodes are un-re-solved;
   the queue `attempts/A137-night-shift-2/results/targets137.json` is already in `frac_exact` order
   and `progress/claims/` marks what is done. ~13 CPU-h for ~40 more certified kills at tonight's
   rate. Do **not** skip the 0.30–0.45 band (§C.1).
2. **Drain the emission LP queue** — 459 level-1 children already screened and clipped, then the
   1,588 level-2/3 ones:
   `python code\run137.py --targets results\queue_bc.json --out results\emit_lp_combined.jsonl --wall 1500 --cap 420 --jobs 1`
   (rebuild the queue with `python code\mkqueue137.py` first). Level-1 children that reach the LP
   are dying at **78.8 %**.
3. **Emit the remaining shards through `emit137.py`, not `tree57.py`** — `k5_11` s1/s2 and `k5_16`
   s1/s2/s3 have not been re-screened at the exact pin core, and the fresh level-1 geometry rate is
   27.4 % before any LP.
4. Then A57's own v2 §8 block, with two corrections: the per-node process wall replaces the `Y0381`
   prohibition (§D.5), and `build_children` should persist the trim ledger (§D.1) before any run
   that is not going through `emit137.py`.

Sides G4/G3/G2 stay frozen (`code\FREEZE_TAGS.txt`). The class window fractions are unchanged
(k5_11_G1 0.978027, k5_16_G1 0.991211) — no A96 driver ran tonight.

---

### Carried forward from v2 — A141's addendum (2026-09-08, append-only)

**A141 (2026-09-08, `polycore lane`, pure geometry, nothing in A57/A96 written).** A118's LANE-COUNT leaf re-run
with A132's POLYGON cores K' -- and, for the pins, A135's EXACT pin core (K' of the pin's own zero-tilt box,
half-side 1/2 - delta/sqrt2 at A57's m-hulled pins, not `pinguard`'s 0.48999997) -- at the USABLE SLOTS (a slot
counts only where its extension class is certified dead on the closed window [191/50, 969271/250000]; all of
k6_18/20/23 for k5_11 and k6_23/27/28/29/30 for k5_16 are, A56/A61/A114 scoreboard). **Sweep COMPLETE over all
1,693 alive A57 records (1,368 A57 + A57box; 1,590 distinct nodes with A60):
188 distinct alive A57 nodes have `LANE_K' + M <= 1` at some usable slot -- 96 k5_11 + 92 k5_16 -- and EVERY ONE
has `LANE_K' = 0` with `M = 1`**, i.e. the slot is met by the conditioned square alone, SLOT-CROWD's two non-pin
meeters are impossible, and the node is DEAD by teleport into the (already dead) extension class. By slot:
k5_11 = BR(0,1) 45, TR(0,0) 27, TL(1,0) 23, BL(1,1) 1; k5_16 = BL(1,0) 54, TL(1,0) 38. 194 of the 244 kills over
A57+A60 are level-1 and 50 level-2. **Overlap with the clip kills is essentially nil: of the 183 nodes in A131's 132 +
A142's 17 A57 + 34 A60 exact-pin-clip lists (all 183 were in the swept corpus), exactly ONE --
`k5_16_interior_Y0281_D03` -- is also an A141 slot kill, so 187 of the 188 A57 nodes are NEW** (`results/t6_overlap.json`).
Each kill carries a replayable `polycore_slot_lane_v1` certificate (`attempts/A141-polycore-lane/certs/slot_*.json`):
a finite cover of the slot-meeting poses whose every leaf is discharged by the container, by a certified separating
axis, or by ONE rational point proved exactly (A132 `vertex_ok` = Lean `checkVertexInPBox`) to lie in every pose of
the leaf box AND of a pin's or the conditioned square's box -- so the Lean consumer is
`shared_point_same_square`, no polygon. The independent checker `code/check141.py` passes **294 of 294** A141
certificates. Sample line per kill: 200,000 poses drawn, ~1.2e5 meeting the slot cell, **0 free**. Caveat A118-O1
stands: a LANE kill excludes class-S packings with EXACT pins, not the delta = 1e-2 slack family. At resume, retire
these 188 (and their descendants) before any LP.

*A137's fold-in reading of that addendum: 187 of the 188 are in the corpus, and 180 of them were
already `PASS`; 7 close open work (§C.4).*

---

## A153 addendum (2026-09-08, cover-number leaf) — MEASURED, ZERO KILLS, do not queue it

**Leaf CN.** Two interior-disjoint unit squares have centres at Euclidean distance ≥ 1 (each
contains the open disk of radius 1/2 about its centre). So the centres a node still has to place
form a 1-separated subset of A148's certified outer feasible-centre region `F_out = GREEN ∪
UNDECIDED`; if `F_out` is covered by `k` sets of diameter < 1 then at most `k` more squares fit, and
`k < budget` is an LP-free kill. Pieces: axis-aligned squares of side `d` with the exact rational
test `2d² < 1` — on A148's grid a 35×35 block of cells, side `6784897/9700000 = 0.699473918`, the
PI's side-0.7 squares. Statement, Lean shape (one `CoverCert` structure + a decidable `check`,
theorems `centre_sep` and `cover_bound`, **zero new axioms** — the analytic input REGION-OUTER is
the one A148's white region already carries), certificate format and independent checker:
`attempts/A153-cover-number/notes/lemma.md`, `code/{cover153,check153,test153}.py`.

**Result over 322 nodes — 60 A57/A60 nodes A148 drew, the 11 k0 residue cells, and all 251 ALIVE
A57 nodes of this file's v3 state (`results/cover153_{a148,k0,a137}.jsonl`): ZERO kills.** Exact
minimum covers proved by branch and bound on 197 of the 322 (the greedy cover matches the
independent-set lower bound); `cover − budget` runs +0 (1 node) to +12, median **+4**. The
obstruction is structural, not a weakness of the covering relaxation: on **322 of 322** nodes
`F_out` itself already contains ≥ budget points pairwise ≥ 1 apart (a *floor* on every cover number,
whatever the piece shape), so no refinement can make the leaf bite. Confirmed directly: 18 of the
tightest nodes re-priced at pitch 0.01 × 72 tilts (4× cells) lose 13–25 % of `F_out` area and at
most **one** piece, and the closest node in the whole population, `k5_11_interior_Y1104_D01`, holds
cover = 5 = budget at 1×, 4× **and 16×** (pitch 0.005 × 144 tilts, area 0.663 → 0.474).

**Lemma TC (tilt-coherent branch, conditional).** Same-tilt interior-disjoint squares need
‖Δ‖_∞ ≥ 1 in the `t`-frame, so pieces may be squares of side < 1 in that frame (side ≈ 0.999 at a
single `t`; `d(1+δ) < 1` for a tilt bin of half-width `δ`). This cuts the number by ~2 but still
kills nothing soundly: 0 of 322 over the node's whole tilt window. The single hit is knife-edge —
`k5_16_interior_Y0083` at exactly `t ≡ 0 (mod 90°)` needs 4 < 5, but a tilt bin of half-width
0.1° already needs 5 (`results/probe153_k5_16_interior_Y0083.json`), so no finite tilt branch makes
it sound.

**At resume: do not queue this leaf.** It is ~5 s/node and kills nothing, and the floor measurement
says it never will. What it *is* good for is a free, sound sanity number on the pages — the
A148 disk bound's combinatorial twin, 2–4 pieces tighter (Y1117: disk bound 10, cover number 8).


---

### Carried forward from v3 — A152's addendum (2026-09-08, append-only)

**A152 (2026-09-08, `slot-lane shrunk`, pure geometry, ~2.8 CPU-h, nothing in A57/A60/A96/A141 written).**
The PI's refinement of A141's slot-lane leaf — *count a square as MEETING the usable slot only if it meets the
cell SHRUNK by the pin tolerance `h = δ/√2 = 7.0711e-3`, because the snap only needs SOME admissible placement
of the extension class's sixth pin* — was stated exactly, tested, and comes out **NEGATIVE on all three
counts**, all of it CONDITIONAL on a prerequisite that does not exist.

1. **The prerequisite is UNMET.** All twelve k6 extension classes (k5_11: k6_18/20/23; k5_16: k6_23/27/28/29/30;
   trump5: k6_07/19/21–24) carry their closed-window kill on a `parametric-kill-certificate-v1` whose six cores are
   uniformly `a = 16383999967232/32768001953125`, `tm = 1/33554432` — a pin POSITION tolerance of **3.08e-8** and a
   tilt tolerance of 3.41e-6°, with **no pin box anywhere in the object** (A96's `pocket96.py` recorded the same
   fact for all 220 k6 cores). They are dead for EXACT-pin class-T packings only. The slack form needs each core
   shrunk to `a = ½ − h = 0.4929289…` (one core for the A60 lane, all six for the A57 lane), the node LP re-solved
   and the whole window re-verified: **1–15 CPU-h for the A60 lane, 2–30 CPU-h for both**, with a real risk that
   k6_20/21/27/29 (τ = 4.60–4.72 against budget 5, three of them unconverged) do not re-solve at δ = 10⁻² at all.
2. **The shrunk-cell step is UNSOUND.** "Every other square misses the shrunk cell ⟹ a free admissible translate
   exists" is true for ONE square (a separating normal `ν` gives the escaping corner `t = −h·sgn ν`) and FALSE from
   four: four pairwise interior-disjoint unit squares entering `C` through its four faces by `h/2` all miss `C_h`,
   yet every `t ∈ [−h,h]²` is blocked by at least two of them, so deleting the one square the leaf may delete does
   not free the slot (machine-checked in exact rationals, `results/t0_counterexample.json`). The corpus realises it:
   **6 cells** (`k5_11_interior_Y0030` TL(1,0), `Y0445` BR(0,1); `k5_16_interior_Y0157`/`Y0428`/`Y0281_D07` BL(1,0),
   `Y0328` TL(1,0)) where the shrunk-cell leaf returns KILL and **no** admissible translate does better than
   NEAR-MISS. The sound form is the TRANSLATED cell at a fixed admissible `t`, certified per node.
3. **The sound form is structurally VACUOUS here, and net negative.** A *completable* slot of a Young down-set has
   both predecessor cells occupied (wall or pin) — checked on all 16 usable (class, slot) pairs — so the admissible
   translate set is always inside `[0, h]²`: the tolerance can only be spent moving the slot square AWAY from its two
   backed sides, i.e. TOWARDS the two open faces where the grazers actually are. Measured over **1 226 of the 1 713
   alive records (71.6 %), 6 170 of 8 694 (node, slot) cells**: 245 certified translated-cell kills on **90 distinct
   cells, ALL 90 of them already A141 kills — ZERO new**; 36 screen-level "upside" candidates, of which the 27 that
   fit the wall were given deep covers and produced **0 kills**. And it COSTS: re-running A141's own kill cells in
   the node's REAL (`δ = 10⁻²` slack) pin regime — which the refinement forces, since the pin obstacle must shrink
   from the full unit square to half-side `½ − h` — **9 of 152 (5.9 %) stop being kills** (8 NEAR-MISS, 1 UNDECIDED);
   the exact-pin control reproduced A141 on 152/152.
4. **One byproduct worth keeping.** In the `δ = 10⁻²` slack family A141's exact snap `t = 0` is INADMISSIBLE at 14
   of the 16 usable slots (a pin displaced by `+h` towards the slot overlaps the exact cell); only the two
   wall-backed corner slots `k5_11 TR(0,0)` and `trump5 TL(0,0)` keep it. So A118-O1 is sharper than "the leaf does
   not prove the slack statement": at 14 of 16 slots the exact snap is not even available there.

90 `polycore_slot_lane_shrunk_v1` certificates (`attempts/A152-slot-lane-shrunk/certs/slotshr_*.json`, SHA-256
manifest `results/cert_manifest.json`), **all 90 PASS the independent checker `code/check152.py`**, which runs
A141's `check141` in full and then rejects any certificate that does not declare itself CONDITIONAL on the
slack-form extension kill. **None of them is a kill today, and none of A57's state changes.** *Every claim in
this addendum that would retire a node is conditional on the slack-form extension kill; the recommendation is
NOT to buy that re-certification for the slot-lane refinement — it should be bought, if at all, to make A141's
existing 244 kills slack-valid (A118 §2 / lemmas.md T23), which is a much better reason.*


**The UNDECIDED slot cells are not a reservoir of kills (A157, 2026-09-08; exact-pin form,
class-S composition, A118-O1 stands).** A141's slot sweep left 1,655 (node, slot) cells UNDECIDED;
196 of them (174 distinct nodes, 179 distinct (node, slot) cells after the L1/G1 shard duplicates)
carry `lane_lb = 0` with a certified `M <= 1` and were read as probable `LANE_K' = 0, M <= 1`
kills. Two things came out of re-running them. First, a correction of record: those cells were
NOT the ones whose covers A141 skipped — `skipped_covers` is set only on the `LANE>=2` /
`NEAR-MISS-OR-WORSE` rows, and every UNDECIDED row already carries `M_exact = true`; what failed
was the LANE cover, which returned `lane = None, reason = "open budget exhausted"` at
`max_open = 1200, depth0 = 20` (that branch also zeroes the reported `cover_open`, which is why
188 of the 196 rows misleadingly show `cover_open = 0`). Second, and decisively, `lane_lb = 0` at
A141's 8,000-pose screen means *no free pose was drawn*, not that none exists: re-screening all
179 cells at **400,000** poses realises a free pose on **86** of them (11 with an explicit
interior-disjoint pair), which with their `M` gives `LANE_K' + M >= 2` and PROVES no kill is
available by this leaf — 62 of the 86 are A57 cells (k5_16 47, k5_11 15; 52 at level 1, 8 at
level 2, 2 at level 3). On
the 93 that survive the screen, A141's certifying cover was re-run at `depth0 = 21,
max_open = 4,000`: **25 cells covered, 0 kills, 1 near-miss** (`k5_16_interior_Y0254 BL(1,0)`,
`LANE_K' <= 1` on 2,296 always-overlapping open boxes with `M = 1`), 24 not closed. The 25 include
**all 16** cells where a kill was structurally reachable at this budget (`M = 0`, needing only
`LANE_K' <= 1`, which a non-empty open set can certify); the 68 unrun cells all have `M = 1` and
need `LANE_K' = 0`, i.e. an EMPTY cover, which nothing measured approached — 21 of the 25 never
finish the DFS phase (the undischarged frontier roughly doubles per depth level: on the largest
clearance in the corpus, `k5_16_interior_Y0410 BL(1,0)` at 1.36e-1, `depth0 = 20 -> 324` leaves and
`depth0 = 21 -> 799` leaves, both budget-cut), and on `k5_16_interior_Y0149_D02/D00 TR(1,0)` the
refinement rounds GROW the open set (43 -> 873, 51 -> 506) because the always-overlap screen keeps
finding genuinely far-apart open pairs. **Zero certificates were emitted and nothing in A57
changes**; `attempts/A157-undecided-slots/results/slot_kills157.jsonl` is empty by construction.
The reading to carry forward is A141 sec 8.2's, extended: the UNDECIDED slot population is a real
2-crowd population like the near-misses, not a budget artefact, and the cheap way to see it is a
50x bigger pose draw, not a deeper cover (2 s/cell against 35 CPU-s/cell).


**The near-simple slot box is a usable NO-family but NOT a usable YES leaf (A158, 2026-09-08;
exact-pin form for the leaf, A118-O1 stands -- and the A57 nodes carry `delta = 10^-2` slack pins,
pin boxes of half-width `7.07e-3`, so their YES branch would additionally owe the A152 caveat).**
A158 ran the PI's tautologous split `SomeIn S | NoneIn S` on the near-simple slot box `S(r, tt)` =
{centre within `r` of the exact slot centre, tilt within `tt` of 0/90} -- YES by A141's lane leaf
with `K'(S)` as an EXTRA obstacle (the discharge against `K'(S)` IDENTIFIES the pose with the
S-square, so the count is `1 + LANE_K'(C|S) + M(C|S)`), NO by one `caselp` `NoFam(S)` plus an A135
exact-core re-solve, A136's inward-rounding wrapper and the frozen `verify_case.py` (sha
`521cb01f...`).

**The population is large.** Of the **1,693 alive A57/A60 records (1,590 distinct nodes: k5_11 713,
k5_16 552, trump5 325)**, **1,238 (73 %)** have LP DUAL support -- the node record's `packing` list,
the maximum fractional packing of core-avoiding admissible squares, whose weight is what keeps
`tau >= budget` -- with weight >= 0.5 inside some usable slot's `S(0.10, 10 deg)` box: A57 1,079
(k5_11 575, k5_16 504) and A60 159, by level L1 962 / L2 243 / L3 19 / L4 14. Commonest:
`k5_11 TR(0,0)` 420, `k5_11 BR(0,1)` 219, `k5_11 TL(1,0)` 205, `k5_16 BR(0,1)` 184,
`k5_16 TL(1,0)` 166, `k5_16 BL(1,0)` 163. So the reading "these nodes are alive because the LP puts
a square in a near-simple slot position" is right for three quarters of the board.

**The YES child, however, does not exist.** Over **141 measured cells** -- the top 20 by that weight
(all level 1), a uniform 120-cell sample of the remaining 1,218 (seed 158), and the two cells the
screen did not refute -- a free second meeter of the slot cell that lies in the container, meets
`int C` and clears every pin core, `K'(H)` AND `K'(S)` is REALISED at 400,000 draws on **139**, at
`tt = 10 deg` **already at `r = 0`**; at `tt = 0` the largest closable radius is between `2.9e-6`
and `2.2e-3` per cell, and three cells (`k5_11_interior_Y0130 TR(0,0)`, `Y0147 TR(0,0)`,
`k5_16_interior_Y0881 BR(0,1)`) fail even at `r = 0, tt = 0`. A realised free pose is a sound
`LANE_K'(C|S) >= 1`, so these are refutations, not budget failures -- 5 s per cell, no cover. On the
two cells not refuted the certifying cover was bought and each closes only ONE half:
`k5_11_interior_Y1110 TR(0,0)` certifies `LANE_K'(C|S) = 0` (the first time this cover has ever
closed) but `M(C|S) = 1`; `k5_16_interior_Y1014 TL(1,0)` certifies `M(C|S) = 0` but `LANE = 1`.
Both give `1 + LANE + M = 2`. **0 of 141 cells kill the YES child.**

**The NO child is real, but needs a box two orders of magnitude bigger.** Run at `S(0.10, 10 deg)`
on all 20 top cells (20-440 s each, A135 exact cores, warm-started from the node's own atoms and
rows): `tau` drops below budget on 7, but **6 of those 7 also drop below budget with NO NoFam at
all** -- the control run (`no158.py --radii -1`, the identical exact-core re-solve) -- so they are
artefacts of the exact-core re-solve, not of the slot box. Five of the six
(`k5_16_interior_Y0226/Y0078/Y0539/Y0589/Y0475`) are records with `converged = false,
dead_unconverged = true` whose stored `tau ~ 4` was never a bound; the sixth,
`k5_16_interior_Y1039 BR(0,1)` (stored `tau = 4.999999999`), goes to `tau = 4.000000` on the
exact-core re-solve ALONE -- **that is A149's lane, not A158's, and is recorded here only as an
observation**. The one attributable kill is `c0_Y0076 TL(0,0)` (A60): `tau 5.000000 -> 4.000000`
with the NoFam, `tau = 5.000000` without it.

**Why the two halves cannot meet -- and it is arithmetic before it is geometry.** `caselp` drops a
row only if its centre is inside the zone by `EPS_ZONE = 2e-3` and its tilt inside a `t`-interval by
`EPS_TH = 0.3 deg`; `S`'s tilt intervals `[0, tt]` and `[90-tt, 90]` have empty margined forms for
`tt <= 0.3 deg`. So **an `S` narrow enough for the YES child exempts not one row** and the NO child
is bit-for-bit the original LP. Measured: NO needs `r in (0.02, 0.03]` at `tt = 10 deg` and
`tt in (1.5, 2] deg` at `r = 0.10` on `c0_Y0076`; YES needs `r <= 3.7e-4` with the tilt PINNED and
is refuted at `tt = 0.31, 0.40, 0.49 deg`. The obstruction lives in the TILT variable alone, so it
is independent of `r` and no anisotropic box helps.

**The PI's geometry is not refuted -- the `K'`-based leaf is.** `pair158.py` searched 600,000 draws
per cell for an explicit interior-disjoint pair (a pose IN `S` clearing every node core, and a free
second meeter) on the six PI cells at `(r, tt)` in `{0.10, 0.01} x {10, 0.5} deg`: **none, with the
maximum pair gap NEGATIVE everywhere** (-0.67 on `k5_11_interior_Y1110`). `K'(S)` is the
intersection over the whole box, so the intruder clears it while still overlapping every individual
square with a pose in `S`. The repair is A141's `lane_corner_split` shape -- partition `S`, apply the
leaf per piece -- and it prices out: pieces of `<= 3.7e-4` in centre and `< 0.5 deg` in tilt means
about `1.5e6` pieces for `S(0.10, 10 deg)`, roughly **400 CPU-h per cell**.

**What to carry forward.** The slot split as a KILL is dead. The slot split as a NO-FAMILY is a new,
cheap structural probe: one 20-70 s exact-core LP per node says whether the node FORCES a square
into the near-simple slot box, and `c0_Y0076` is the first node proved to do so (`eta = 1`, frozen
verifier PASS). The sharpest near-miss is `k5_11_interior_Y0130 TR(0,0)`, where `NoFam(S)` takes
`tau` from 5.500000 to exactly 5.000000 -- it consumes the node's entire slack and stops at the
budget, the same value A149's polycore arm reached on that node independently (`poly149.jsonl`,
2026-09-08 13:33, `tau 5.5 -> 5.0`, NO-KILL). Nothing in A57 was written; every record is under
`attempts/A158-slot-split/`.


**A158b addendum (2026-09-08) -- the YES child of the slot split is an LP node, and the split is
STRUCTURALLY neutral on the knife-edge population.** `SomeIn S` is an ordinary case-LP hypothesis, so
the YES child is `pins + H + the slot box S` at `budget = 11 - #cores = 4`. Run with A135 exact cores
on all 7 boxes (and `cores_pairwise_disjoint` re-run over ALL 7 -- A135's `ExactHyp` gates only
`cores[:n-1]`, and an unchecked `K(S)` meeting `K(H)` would make the budget 5, not 4; measured min
gap 0.0141 on A57's `delta = 10^-2` pins, 0.0000 on A60's exact pins): **all 12 sub-cases (6 cells x
2 tilt pieces) converge at `tau = 4.000000 = budget`, `eta = 0`** (`k5_11_interior_Y0130`,
`Y0147`, `Y1110` at `TR(0,0)` among them, `Y0130` from `tau0 = 5.5`). **The slot square removes
exactly ONE unit of dual packing and exactly ONE unit of budget, so the YES child lands back on the
knife edge -- the same 1 the NO child removes from `tau` alone.** The dual weight in `S` is exactly 1
on 730 of the 1,238 selected records, so on that sub-population the split cannot bite from either
side, and the population run is not worth buying.

The PI's mutual clip (A131 `pinclip` with each box's own core in the pin's role; the core handed to
A131 is the largest AXIS-ALIGNED square inscribed in `K'`, strictly smaller, so the clip removes less
than the truth and A131 is imported unchanged) does bite on A57: `k5_11_interior_Y0147`'s `H` box
keeps **0.6273** of its area (0.4601 by volume at `nsub = 4`) and `K'(H)` grows **x1.066**
(0.681579 -> 0.726393), with two whole tilt sub-bins of `S` emptied; `Y0130` and `Y1110` keep 1.0000
(their `H` and `S` are already far apart). What actually moved the lane test, though, was the CLAMP
of `S` to `[1/2, s0-1/2]` that the LP framing forces -- at a corner slot it halves the centre box and
fattens `K'(S)` (0.566 -> 0.736 on the A60 example).

**The first empty conditional lane cover ever obtained is on `k5_11_interior_Y1110 TR(0,0)`:
`LANE_K'(C | S, H_clipped) = 0` CERTIFIED on BOTH tilt pieces, 36 and 35 leaves, 0 open, 36 s and
37 s.** The kill then needs `M(C | S, H_clipped) = 0`, and that is where it stops -- and
STRUCTURALLY, not for budget: the screen finds no meeting pose of the clipped `H` box clear of the
other cores in 100,000 draws, but `cond_can_meet`'s cover discharges **ZERO** leaves (0 leaves /
5,001 open at `max_depth 40`, 21.8 s; 0 / 40,001 at 42, 183.8 s), because `H_clipped` sits at frame
`[1.374, 1.519]^2` with `hmax ~ 0.686`, so `box_misses_cell` needs `x0 >= 1 + hmax = 1.686` and can
never fire, the container prune never fires on an interior box, and the shared-point discharge finds
nothing -- the DFS fills its open budget in one corner. A third rung was stopped at 674 s rather than
bought. `Y1110`'s NO child is alive (`tau = 5`), so even a closed `M` cover gives YES-only.
**The lesson for the leaf: on an interior-`H` cell the `M` half of the conditional leaf has no prune
that can fire, so the conditional lane leaf is only ever deployable where `H` is near enough to a
wall or a pin for `box_misses_cell`/container to bite.** Cost ~0.7 CPU-h of a +2 CPU-h extension;
nothing in A57 was written.

---

### A162 addendum (2026-09-08) — run the gallery status board at every pause

**One line, at every pause, before you write the next `PAUSED.md`:**
`python docs/shadows/status_gallery.py` — it re-reads every kill record in the repo (this file's
supersession ledgers, A136/A140/A141/A149/A156's records, the A57 tree jsonl, and every
`*.clipkill.json` under `attempts/*/certs/**`), applies §C.3's tag rule and monotonicity, `git mv`s
the now-DEAD shadow-gallery pages into `docs/shadows/<gallery>/killed/` (never a delete) and
rewrites `docs/shadows/STATUS.md`, which is the checklist the PI reads first. `--dry-run` prints the
plan and writes nothing; it solves no LP, writes nothing outside `docs/shadows/`, and is idempotent.
First run: `k0v4` 11 alive / 0 dead, `a57v4` 57 alive / 3 dead.
