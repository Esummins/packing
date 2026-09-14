# A57 / A96 — PAUSED v4, 2026-09-08 22:20 PDT (end of the A156 day-shift window)

Nothing of A156's is running. The pause used the **sentinel path**
(`attempts/A156-day-shift/PAUSE`, the scoped sentinel of v2 §7a): the sentinel went in at
**22:11:32**, each worker finished the node it had in flight and wrote its row, and the last one
exited at **22:19:22**. Nothing was killed and nothing in flight was discarded.
**A57's own `PAUSE` was never touched and still carries A123's text; A137's `PAUSE` still carries
A137's.** So "the A57 PAUSE is set" still does not mean "nothing is running": **check pids.**

Supersedes v3 (2026-09-08 06:45, commit `b91a2813`), archived verbatim — with every addendum
appended to it during the day — as `PAUSED_v3_archived.md`. v3's §§C–E and v2's §5(e)(f), §6, §7,
§7a and §8 remain the operating text except where §§A–E below amend them. **Every addendum other
attempts appended to v3 during 2026-09-08 (A141, A152, A153, A157, A158/A158b, A161 + its
correction, A162) is carried forward verbatim at the end of this file, unchanged.**
**Read §C.1 first if you are about to resume: it changes the order the queue should be drained in.**

---

## A. What ran (2026-09-08 11:17 → 22:19 PDT)

Owner A156 (Opus), on the PI's **day** box (PI working over remote desktop). Everything ran through
**wrappers**: `tree57.py`, `lpbox.py`, `pinguard.py`, `pinclip.py`, `trim57.py`, `polycore.py`,
`exactcore.py`, A135's `emit135.certify`, A137's `emit137.py` and `node137.py`, and both frozen
verifiers were imported or executed **unchanged and never edited** (`verify_case.py` sha
`521cb01fe656707c…`, re-hashed at the start of the shift). Drivers and brief:
`attempts/A156-day-shift/code/`, `attempts/A156-day-shift/BRIEF.md`.

| lane | driver | procs | what |
|---|---|---|---|
| LP drain, level-1-first | `run156.py` → A137's `node137.py` → `emit135.certify` | 2 | v3 §E.2's queue: children already screened through the hooks, LP on the **clipped** box with exact cores in the certificate, FROZEN verifier |
| LP drain, level-2/3 only | the same, on `queue156_L23.json` | 1, from 16:06 | the lane that measures the level-2 LP rate v3 leaves blank |
| deepen | `deepen156.py` → A137's `emit137.py --mode deepen` (unmodified) | 1, twice, 27 s of compute | 342 children screened through T5/T5′ → T5″ → T5‴ → T5⁗ |
| scaler | `scale156.ps1` → `launch156.ps1` (pidfile gate) | — | one launch per pass, only with room under the box cap; affinity sweep every pass |

**Box discipline.** The coordinator's 11:20 amendment (P-cores only; ceiling 16 lab python
processes) was applied box-wide: `affinity156.ps1` set `ProcessorAffinity = 0xFFFF` on **every** lab
python process, not only A156's — 6 of the 12 running at 11:17 were still on `0xFFFFF` and were
narrowed — and the sweep re-ran every scaler pass (5–10 min) all day, so the PI's E-cores (16–19)
carried no lab work from 11:18 on. A156 held **2 workers until 16:06 and 3 after**, launching only
through the pidfile-gated launcher, which refuses whenever the box count leaves no room for a worker
**and its node child**. Per-node **process** wall 1,500 s: it fired **twice**, recorded `WALL-CAP`,
**never a verdict** — and, unlike v3's run, a capped node now **releases its claim**, so it returns
to the queue on the next rebuild instead of being stranded. The memory gate (3,072 MB physical /
6,144 MB commit) never held: free physical stayed between **5.2 and 15.2 GB**. BLAS pinned to one
thread per child, `PYTHONDONTWRITEBYTECODE=1`, 0 orphans, no recursive delete, no pidfile and no
foreign sentinel touched.

**Work done:** **352 LP nodes** (28.07 CPU-h) and **342 children screened** by geometry.
`sync156.py` — a re-based copy of `sync137.py`, and the day's **single writer** into A57's canonical
files — appended **428 rows** (358 LP verdicts + 70 geometry verdicts), skipping both `WALL-CAP`s and
adding **zero duplicate ids**.

## B. State — v3 → v4

Re-derived per tree by `attempts/A156-day-shift/code/state156.py`, **after** the day's sync. Two
methodology notes, because v3's §B table is not directly comparable: this one counts **distinct
ids** (the corpus stores 139 ids twice — §D.3) taking the **strongest** verdict per id, and it
counts the whole corpus, where v3's §B counted only the rows that existed before A137's night.

| tree | n | ALIVE | FAIL | PASS | logic kill | work-owing | now DEAD by a ledger |
|---|---|---|---|---|---|---|---|
| `k5_11_interior_G1` | 958 | 137 | 41 | 477 | 303 | 178 | 39 |
| `k5_11_interior_G1_D2` | 869 | 59 | 81 | 292 | 437 | 140 | 70 |
| `k5_11_interior_G1_D2_D2` | 111 | 4 | 6 | 29 | 72 | 10 | 6 |
| `k5_11_interior_G1_D2_D2_D2` | 32 | — | 6 | 8 | 18 | 6 | 6 |
| `k5_11_interior_L1` | 196 | 17 | 4 | 103 | 72 | 21 | 5 |
| `k5_11_interior_L1_D2` | 23 | — | 1 | 14 | 8 | 1 | 0 |
| `k5_16_interior_G1` | 979 | 206 | 27 | 506 | 240 | 233 | 54 |
| `k5_16_interior_G1_D2` | 403 | 4 | 10 | 72 | 317 | 14 | 9 |
| `k5_16_interior_L1` | 113 | 7 | 8 | 67 | 31 | 15 | 6 |
| `k5_16_interior_L1_D2` | 8 | — | — | 8 | — | 0 | 0 |
| **total** | **3,692** | **434** | **184** | **1,576** | **1,498** | **618** | **195** |

> **Open work is 423** (work-owing minus the ids a fold-in ledger already kills). The day's own
> contribution: **269 certified kills + 70 logic kills**, against **272 new children** emitted into
> the frontier. The LP queue went **1,995 → 1,786** unclaimed
> (`attempts/A156-day-shift/results/queue156.json`, rebuilt at the pause).

## C. The day's three findings, in the order they change decisions

### C.1 Level 2 is where the cheap kills are — the level-1-first queue order is wrong

Measured today, on the population the schedule actually faces:

| level | PASS | NO-KILL | LOST-KILL | TOO-TIGHT | FAIL | WALL-CAP | **kill rate of decided** | **median wall** |
|---|---|---|---|---|---|---|---|---|
| 1 | 186 | 45 | 17 | 8 | 1 | 2 | **186 / 257 = 72.4 %** | **236 s** |
| 2 | 83 | 4 | 2 | 4 | — | — | **83 / 93 = 89.2 %** | **122 s** |
| **all** | **269** | **49** | **19** | **12** | **1** | **2** | **269 / 350 = 76.9 %** | — |

**A level-2 node is killed far more often (89.2 % vs 72.4 %) and costs about half the wall (122 s vs
236 s median)** — roughly **2.4× the certified kills per CPU-hour**. v3 §E.2's ordering (level-1
children first, because they die at 78.8 %) was set when no level-2 LP rate existed; it does not
survive the measurement. **Drain level 2 first, or keep one dedicated level-2 worker up as this
shift did** (`mkqueue156.py --levels 2,3`; `scale156.ps1` keeps exactly one such worker). The
level-1 number also confirms A137's 78.8 % within sampling error on 4× the sample.

### C.2 The 27.5 % level-2 geometry rate is a property of the PARENT population, not of level 2

Two deepen passes, through the same unmodified hooks, at the same exact pin core
`33873816211/68719476736`, minutes apart:

| pass | parents | children | T5′ | T5‴ clip | T5⁗ | **dead before any LP** |
|---|---|---|---|---|---|---|
| the 24 ALIVE level-2/3 nodes of the corpus | 24 | 166 | 53 | 16 | 0 | **69 = 41.6 %** |
| the 22 nodes A156 recorded ALIVE **at the LP today** (level 1) | 22 | 176 | 0 | 1 | 0 | **1 = 0.6 %** |

Same leaves, same core, same emitter — **41.6 % against 0.6 %**. A node that has just survived an LP
at level 1 is, by construction, one the pin geometry does not touch, and its children inherit that.
So v3 §C.2's 27.5 % (and `docs/budget.md`'s 13.74 %) are **rates attached to a specific frontier**,
not level constants: pricing the remaining tree at a fixed geometry-death fraction per level will
over-credit the geometry lane exactly where the frontier is made of LP survivors. On the deeper
corpus population the level-3 rate came out at **41.6 %**, well above v3's 18.5 %. T5⁗ (polygon vs
pin core) again fired **0 of 342** on A57 — v3 §D.4 stands: run it on A60.

### C.3 Every kill this shift is frozen-verifier or pure geometry; one node is a v3 candidate

`verify_case_v3` was **not** used. One node — `k5_16_interior_Y0785`, level 1, τ = 4.74999999994
against budget 5 — had the FROZEN verifier return FAIL **with witnesses** after all witness-feedback
rounds. It is recorded on its own in `attempts/A156-day-shift/results/v3_candidates156.jsonl` and is
**not** counted as a kill. v3 §D.3's reason still blocks it: a v3 kill of the A135/A145 kind needs
`polycores` in the **LP** as well as in the verifier, which the frozen chain cannot emit (A144).

`audit156.py` replayed the brief's four tripwires at 13:55, 19:40 and at the pause: **2,100 core
half-sides** re-derived against A135's `exactcore` (none exceeded its certified-maximal value, all in
(0, ½)), **2,283 tilt bins** inside [0, 90], **495 clipped boxes** each inside its parent, and **8
stored PASS verdicts re-run through the frozen verifier, all still rc = 0**. No tripwire fired at any
point in the shift.

## D. Amendments and incidents

### D.1 The box ceiling was set by the OTHER chores, not by this lane
The ceiling is 16 lab python processes across all chores. From 11:17 to 16:00 the box sat at
**16–22** on the other campaigns alone (A149's LP workers and their children, A151/A152/A153/A154/
A155, later A136, `split159`, `clip158`), so A156's scaler **held at 2 workers for 4¾ hours** and
logged every refusal (`logs/scale156.log`). The third worker went in at 16:06, the minute the box
fell to 10; the box never had room for a fourth. A156 never launched over the cap and never asked
another chore to yield. Consequence for the schedule: the day bought **28 CPU-h**, not the ~55 that
5 workers would have. **The campaign's throughput is currently limited by how many chores share the
box, not by the queue** — if the next window wants 5 A57 workers, the other lanes have to be
sequenced, not just permitted.

### D.2 A worker is 2 processes, transiently 3
`node137.py` spawns the frozen `verify_case.py` as a subprocess while a certificate is checked, so a
worker reads as 3 python processes for those seconds. It is not extra load — the supervisor and the
node child are both blocked in `wait()` — so the launcher reserves **2** per worker, which is the
box's standing convention (A137's scaler at MaxPy 16) and matches A149's shape.

### D.3 The corpus stores 139 ids twice, and 26 of those pairs DISAGREE
`tree_k5_11_interior_G1_D2.jsonl` and `…_D2_s0.jsonl` (plus four other file pairs) overlap; 26 pairs
carry different verdicts, one of them `PASS` against `FAIL(rc=1)`. **This is not unsound** — a FAIL
is the absence of a proof, a PASS is a proof, from different certificates — but any last-wins read
(which is what `board.py` does) can call a certified-dead node ALIVE and then deepen it. Both
`state156.py` and `deepen156.py` take the **strongest** verdict per id; the day's sync added **zero**
new duplicates. De-duplicating the corpus is a standing chore.

### D.4 A capped node now returns to the queue
v3's run left a `WALL-CAP` node claimed-but-unrecorded, which strands it silently (196 such ids were
recovered into this shift's queue by `mkqueue156.py`). `run156.py` deletes the claim when the wall
fires, so the node is re-offered at the next rebuild. The two capped ids today —
`k5_11_interior_Y0907` and `k5_16_interior_Y0499` — **have no verdict** and are back in the queue.

### D.5 Two operational notes
The scaler lost one log line to `Add-Content` contention at 16:06 (the launch itself is in the
worker's own log and pidfile) — A57's `launch.ps1` already retries Add-Content five times for exactly
this reason, and `scale156.ps1` should too. And `emit137.py --mode deepen` writes into **A137's**
results directory (its BASE is fixed): `deepen156.py` moves the outputs into A156 and **refuses** to
run under a tag whose A137 file already exists, so no night file was ever appended to; the alias tag
`…G1a156_D2` is mapped back to the canonical tree file inside `sync156.py`.

### D.6 A162's gallery board was run
`python docs/shadows/status_gallery.py` (A162's addendum) ran at this pause: no page needed moving
(all 7 dead a57v4 pages were already in `killed/`), `docs/shadows/STATUS.md` rewritten. Board:
`k0v4` 11 alive / 0 dead, `a57v4` 53 alive / 7 dead.

## E. Resume — what to run first next time

1. **Drain the queue level-2-first** (§C.1):
   `python code\mkqueue156.py --levels 2,3 --out results\queue156_L23.json`, then
   `powershell -File code\launch156.ps1 -Worker <name> -Levels 2,3`. 1,786 jobs are queued, ~1,400 of
   them level 2/3 at 122 s and 89 % kill of decided. Keep a level-1 lane alongside; `scale156.ps1`
   already keeps exactly one L2 worker up and gates every launch on the box count.
2. **Deepen every node the LP leaves ALIVE, immediately** — `python code\deepen156.py --list` shows
   the population; `--today-only --min-level 1` takes the shift's own survivors, and an
   `--emit-key …a156` alias is required whenever the canonical tag is another attempt's file.
   Screening costs ~0.1 s per child and its children are §C.1's cheap kills.
3. **Finish the exact-core re-emission** (v3 §E.1) — A149 owns that lane; check its progress before
   starting a second lane on the same targets.
4. **Emit the remaining shards through `emit137.py`, not `tree57.py`** (v3 §E.3): `k5_11` s1/s2 and
   `k5_16` s1/s2/s3 have still not been re-screened at the exact pin core.
5. Then A57's own v2 §8 block, with v3 §D.5's correction (the per-node process wall replaces the
   `Y0381` prohibition) and v3 §D.1's (persist the trim ledger in `build_children` before any run
   that does not go through `emit137.py`).

Sides G4/G3/G2 stay frozen (`code\FREEZE_TAGS.txt`). The class window fractions are unchanged
(k5_11_G1 0.978027, k5_16_G1 0.991211) — no A96 driver ran today.

**Box rule in force at the pause** (coordinator, 2026-09-08 11:20): lab work is confined to the 16
P-core threads, `ProcessorAffinity = 0xFFFF`, re-applied hourly to any lab python process without it;
ceiling **16 lab python processes** on the box, counted across all chores.

---

# Addenda carried forward from v3 — unchanged, append-only

*(Everything below this line is v3's own carried-forward material plus every addendum other attempts
appended during 2026-09-08. Nothing in it has been edited; v3 in full, with these addenda in place,
is `PAUSED_v3_archived.md`.)*

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

---

## A161 fold-in (2026-09-08) — the CHORD-LIMITED LANE kills 70 alive k5_16 nodes (66 of them new)

`attempts/A161-chord-lane/` (BRIEF.md, notes/leaf.md, code/{chordlane,run161,checkcl,t4_table}.py,
results/t3_dedup.jsonl, notes/t3_table.md, certs/cl_*.json + results/cert_manifest.json).

**The leaf.** At a WALL-ADJACENT usable slot cell `C` of a pinned class, put a guard line `l` inside
the wall row of pins. A144's chord row gives `rhs(l) = s0 - SUM_j minchord(B_j, l)`; every square
crossing `l` through opposite sides has chord `>= 1`, so at most `beta = floor(rhs(l))` FREE squares
are in that BAND. A141's lane cover, run with one extra sound prune (`band`: every pose of the box
has chord `>= 1`, decided exactly by `max|v| <= (y + 1 - y^2)/2` at `y = cs_max`), bounds the
remaining meeters by `LANE_out`. With `M` the conditioned meeters,
`#{non-pin meeters of int C} <= beta + LANE_out + M`, and SLOT-CROWD forces `>= 2`: **the node is
DEAD when `beta + LANE_out + M <= 1`.** Soundness, certificate format, the independent checker and
the Lean shape (`chord_sum_le_side` + `minchord_of_box` from A144, the A141/A135 lane leaf, two new
`Bool` checkers and ONE new glue theorem, 0 new axioms) are in `notes/leaf.md`. A118-O1 is inherited
verbatim: these are EXACT-PIN class-`S` kills, not slack-family kills.

**One new primitive, and it is the reason `M` moves.** A141's `box_misses_cell` separates only along
the CELL's normals, so for a conditioned box at 50-65 deg whose square clears the cell along one of
its OWN edge normals it can never fire at any depth — every `M = 1` of that shape in A141's `t2`
pass is a budget failure, not geometry. `chordlane.box_misses_cell_exact` runs the full
separating-axis test over the parameter box (8 axis/sign pairs, every bound an exact Fraction by a
two-endpoint rule). On `k5_16_interior_Y0842 / BL(1,0)` it excludes `H` at the ROOT box, in ONE leaf:
`M` goes 1 -> 0.

**The PI's node.** `k5_16_interior_Y0842 / BL(1,0)`: guard line `y = 770833/1000000`, the two
bottom-row pins give chord exactly 1 each, `rhs = 469271/250000 = 1.877084`, `beta = 1`,
`LANE_out = 0` (166 cover leaves: 44 `band`, 106 `witness`, 16 `container`; 0 open), `M = 0`,
total `1 <= 1` — **DEAD**. Sample line: 60,000 poses drawn, 40,696 meet `int C`, 20,125 are BAND
(min chord 1.0000000000453) and 20,571 are OUTSIDE, of which **zero** are free.
Cert `attempts/A161-chord-lane/certs/cl_k5_16_interior_Y0842__BL1_0.json`, sha256 `bb2406ba727fc782...`.

**Population (A57 half).** 2,377 (alive node, wall-adjacent usable slot) pairs run.
k5_16 kills: **72 pairs / 70 nodes** — BL(1,0) 45, TL(1,0) 26, BR(1,0) 1; **66 of the 70 nodes are
new** (3 were already dead by A131's pin-clip, 1 by A142's exact-clip; A141's own lane kills were
excluded from the population by construction). All 70 are level 1 except one level-2 node. k5_11
contributes **zero**: both of its wall-adjacent usable slots (BR(0,1), TL(1,0)) sit on a wall
carrying only ONE pin chord, so `beta = 2` on every swept offset and the leaf cannot fire — a
structural gate worth remembering (the leaf needs TWO pins on the wall of the slot).
124 pairs are UNDECIDED (the outside cover did not close inside a 10 s/pair budget) over 88 nodes;
one NEAR-MISS (`k5_16_interior_Y0143_D01 / BL(1,0)`, `beta = 1`, `LANE_out = 1`, `M = 0`).
Nothing under `attempts/A57-shadow-trees/` was modified: these are records, not re-solves.

### A161 continuation (2026-09-08, +3 CPU-h) — retry, A141's leaf, and a CORRECTION to the count above

**CORRECTION.** The fold-in above says "66 of the 70 k5_16 nodes are new". That compared against
A131/A141/A142 only. Against the full dead set the collector `docs/shadows/status_gallery.py` builds
STATUS.md from (44 sources, 4,994 kills, 3,173 distinct node ids dead), **A161's A57 half contributes
4 genuinely new dead k5_16 nodes, not 66**: `k5_16_interior_Y0150`, `k5_16_interior_Y0727`,
`k5_16_interior_Y0842` (the PI's node) and `k5_16_interior_Y1146`. The other 68 were already
recorded dead — 62 of them in A57's own tree jsonl (A149's and A156's re-solves landed after the
A141 `t2_a5760` snapshot A161's population was built from). Lesson for the next pass: build the
population from the collector, not from a campaign snapshot. Numbers: `results/overlap161.json`,
`notes/t3_table.md` §T7.

**Retry of the 126 UNDECIDED pairs (T5).** A longer budget alone buys nothing — at 60 s/pair with a
30,000-box budget every one of the first 12 still ended `time budget exhausted`. What matters is
WHICH guard line is tried: on Y0842 the cover blows a 40,000-box budget at `y_L = 0.9167` and closes
in 163 leaves at `y_L = 0.7917`. Trying the top 6 ranked offsets: **127 pairs re-run, 13 new KILLs**
(`results/t5_retry.jsonl`, certificates in `certs/`, all PASS `checkcl.py` — 109/109 overall), 22
pairs closed as no-go by an exact free OUTSIDE pose, 92 still UNDECIDED.

**A141's own leaf with the exact separating-axis test (T6), the useful negative.** Over 3,048 of the
3,103 A141 early-exit cells (all usable slots), `box_misses_cell_exact` gives `M = 0` on 1,169 and
**flips 105** cells where A141 had recorded `M >= 1` — including Y0842's, which is what made it
close. But run WITHOUT the chord row and the band prune, the lane cover closed on **none** of 220
`M = 0` cells tried (open sets 600-800 boxes, spread): **zero new kills under A141's leaf alone.**
The exact SAT test is necessary but not sufficient — the chord row does the essential work.
`code/{run141x,check141x}.py`, `results/{t6_mpass,t6_a141x}.jsonl`; `check141x.py` is A141's own
`check_lane_cert` with `leaf_misses` widened for the new `axis` reason code, validated 2/2 against
A141's own certificates.


### A161 T8 (2026-09-08) — the CONDITIONAL form: stated and implemented, not yet closing

The conditional chord-limited lane (split the conditioned square's box, use each piece's fatter
`K'(b)`: `n(b) = beta + LANE_out(b)` when the piece misses the cell, `min(beta, LANE_band(b)) +
LANE_out(b) + 1` when it does not; `<= 1` everywhere kills) is stated and implemented in
`attempts/A161-chord-lane/code/condlane.py`, with the new exact mirror primitive
`chordlane.not_band_ok` (every pose has chord `< 1` iff `min|v| > (y + 1 - y^2)/2` at `y = cs_min`).
Tested on the PI's trump5 case `c0_Y0169 / TL(0,0)`: `beta = 1` with the two wall pins giving chord
exactly 1, `LANE_out = 0` certified on every piece reached — but the `LANE_band` cover on the pieces
where `H` reaches the cell did not close in any budget tried, so no kill and no certificate. It has
not been run on the k5_16 NO-LINE / `M = 1` cells (94 at BL(1,0), 81 at TL(1,0), 84 at BR(1,0)) —
that is the queued work, with the three levers listed in `notes/t3_table.md` §T8.

### A167 fold-in (2026-09-09) — the CONDITIONAL chord-limited lane, POPULATION PASS (A161's queued work)

`attempts/A167-condlane-pass/` (BRIEF.md, notes/{leaf.md,table.md,doc_lines.md},
code/{pop167,condlane2,runcond167,checkcond167,witness167,diag167,whydead,table167,recheck167,
summarise167}.py). A161 T8's conditional leaf was stated but never run over the population; this is
that run, with A161's three queued levers and two more the measurement forced.

**Population built FROM THE COLLECTOR, not from a snapshot** (A161's own lesson): a fresh
`docs/shadows/status_gallery.py` collect (5,742 records / 5,258 kills / 46 sources / 3,214 dead ids
at the start) intersected with A161's T3 rows gives **416 cells over 258 ALIVE A57/A60 nodes** — all
of them `NO-LINE (beta + M >= 2 on every swept offset)` or `UNDECIDED` with `M = 1`, i.e. precisely
the cells where `H` reaches the slot and the unconditional form can never fire. **All 416 were run**
(2 × ~4,000 CPU-s at 60 s a cell, ~21 s a cell actual).

| verdict | cells |
|---|---|
| `KILL` | **15** |
| `NO-GO-witness` (every swept offset screened out by a sampled free meeter) | **285** |
| `UNDECIDED-time` (60 s cell budget) | 116 |

**Kills, by class × slot:** trump5 BR(0,1) 10, k5_16 BL(1,0) 4, trump5 TR(0,1) 1. Zero on k5_16
BR(1,0)/BR(0,1)/TL(1,0)/TR(0,1)/TR(1,0), trump5 BL(0,2)/TL(0,0)/TR(1,0), k5_11 (both slots).
**Re-checked against a FRESH collect at the end (5,800 / 5,314 / 46 / 3,238): 11 of the 15 are still
NEW dead nodes** — `c0_Y0989, c0_Y0993, c0_Y0995, c0_Y0996, c0_Y0997, c0_Y1002, c0_Y1131,
k5_16_interior_Y0191, k5_16_interior_Y0281, k5_16_interior_Y0635, k5_16_interior_Y0663` (7 trump5,
4 k5_16, all level 1); the other four (`c0_Y0902, c0_Y0913, c0_Y0921, c0_Y0994`) were killed by
**A149 while A167 was running**. **15/15 certificates PASS the independent checker**
(`checkcond167.py`, which delegates a `chord_limited_lane_v1` certificate to A161's `checkcl.py`
unchanged and adds E1–E9 for the conditional kind). Example cert
`attempts/A167-condlane-pass/certs/cond_k5_16_interior_Y0663__BL1_0.json`, sha256 `8f7b3e1ad7c3e166…`.

**Two additions to A161's leaf, both sound, both load-bearing** (piece accounting over the 15
certificates, 121 pieces): the **per-piece guard row** — `minchord` is monotone under box inclusion,
so putting the PIECE's box in the chord row is legitimate and often gives `beta = 0`, which kills the
band with no cover at all (29 pieces, and all nine pieces of `c0_Y1131`) — and the **band-slab root**,
`chord >= 1 => |v| <= f(1) = 1/2`, so the `LANE_band` cover runs over `centre_window ∩ {|v| <= 1/2}`
(92 pieces closed `LANE_band = 0`). Every kill piece has `m = 1`.

**The negative half is the bigger result.** 285 of 416 cells are NO-GO: on some piece of `B_H`,
EVERY one of the ~106 swept offsets is screened out because the sample exhibits a FREE pose (avoiding
every `K'`, the fattened piece core included) that meets `int C` — so the leaf's own counters are
`>= 2` there and no budget can change it. Escalated on 60 cells with an EXACT rational two-crowd
witness (`witness167.py`, `nogo_two_crowd_v1`: two unit squares on a `1/10^6` grid, both inside
`[0, s0]^2`, both meeting `int C`, interiors disjoint by an exact separating axis, both clear of the
five pins, one a legal pose of `H`): **49 of 60 certified**, which retires those cells for the WHOLE
lane-leaf family (A159 C8 in exact arithmetic), by slot k5_16 BR(1,0) 16, trump5 BR(0,1) 14, k5_16
TL(1,0) 13, k5_16 BL(1,0) 3, trump5 TR(0,1) 3.

**Scheduling fact worth keeping** (`logs/diag_y0169_d*.log`): a lane cover that CLOSES closes in
0.6–1.2 s and one that does not grinds for as long as it is given, so breadth over offsets at a
2 s hard slice plus ONE 12 s retry on the offset that got closest beats any long single budget — and
the viability screen (which costs one pose pool per piece, ~0.3 s, and removes 50–100 of the 106
offsets) is what makes the deep split affordable at all.

**One checker correction worth propagating:** in the conditional form a `witness` leaf citing the
conditioned index must be verified against **the piece's box**, not `B_H` — on that branch the piece
IS the hypothesis, and it is the strictly stronger obstacle. Checking against `B_H` rejects every
genuine certificate (15/15 FAIL before the fix, 15/15 PASS after).


---

## A170 addendum (2026-09-09) — the certificate-EMISSION audit closes A166's question NEGATIVE for this tree

`caselp.make_certificate` (`attempts/A57-shadow-trees/code/caselp.py:384`) ends with
`hyp = Hyp.from_json(res["hyp"])`, and `Hyp.__init__` recomputes `self.cores = [b.core() for b in
boxes]` — the STOCK cores — discarding the `cores` field `Hyp.to_json` wrote. An `ExactHyp` LP therefore
emits a certificate exempting a strictly SMALLER core than its row filter dropped rows against, and
every LP-dropped placement in the 1.4–15 % annulus between the two cores is a guaranteed hole
(A166 `bc8b5dd5`, `attempts/A166-nearest-corner-subtree/notes/certificate_bug.md`).

**A170 audited every certificate on disk empirically** (3,378 files: the exact core recomputed from the
box each certificate itself carries, compared with the `a` it wrote — `attempts/A170-certfix/notes/audit.md`,
`results/scan170.json`). **This tree's lanes are CLEAN:**

| lane | cores written | FAILing certs re-certified with the cores enlarged |
|---|---|---|
| A137 night re-emission (`node137.py:50` → `emit135.make_cert`) | exact **241/241** | 44 → **NO-CHANGE 44/44** |
| A149 a57 (`run149.py:259` → A137's `node137.py` verbatim) | exact **137/137** | 43 → **NO-CHANGE 43/43** |
| A149 a60 (`node_a60.py:123`, scope `exH`) | H exact **95/95**, pins the corpus core by design (`node_a60.py:10-14`) | 14 → FAIL (pin cores enlarge < 0.01 %) |
| A156 day shift (`run156.py:212` → `node137.py`) | exact **302/302** | 31 (+ the one `v3_candidates156.jsonl` row, the same node) → **NO-CHANGE 31/31** |
| A145 | exact 18/18 | 9 → NO-CHANGE |

The reason is structural, not luck: **A135's `emit135.make_cert` (`emit135.py:93`) is a copy of
`caselp.make_certificate` that takes the LIVE `Hyp` instead of round-tripping it**, written for exactly
this bug (`emit135.py:94-100`). Everything this tree emits goes through it.

**Consequences for this file.** (i) §C.3's kills and the exact-core kill rate **46/161 = 28.6 %** stand
unchanged — no A137/A149/A156 FAIL is spurious. (ii) A156's `v3_candidates156.jsonl` row
(`k5_16_interior_Y0785`, 8 holes) is **not** a core-staleness failure and its own note already said so.
(iii) One **cosmetic** defect found: `node_a60.py:64` mutates `hyp.cores` on a plain `caselp.Hyp`, which
has no `.scope` / `.a_report`, so `emit135.make_cert`'s `getattr` defaults write
`provenance.core_scope = "stock"` and `cores_exact = null` on all 95 `certs/a60/*__exH.json` — the H core
in them IS exact and the true `a_report` survives in the lane's jsonl and in
`results/superseded_by_exactcore_a60_A149.jsonl`. No certificate is wrong; only its provenance line is.
Fix it at resume by giving `build_hyp` the two attributes, or by emitting through the A170 wrapper.

**Final numbers (409 certificates re-certified, 2.35 CPU-h of verifier, no LP solved).** 59 recovered PASSes, 59/59 clearing a 100 % independent check (A132 `polycore.vertex_ok` re-run on the WRITTEN rationals, the measure recomputed exactly in `Fraction`, a depth-64 frozen replay): 25 repairs in A150/A165/A166 (3 new nodes, all A165 `l1_104` spread tuples) and 34 free upgrades, all of them A59/A60 zero-atom VACUITY certificates. **Nothing in this tree moved**, and the shadow board did not either -- `docs/shadows/status_gallery.py --dry-run` goes 5,332 -> 5,344 kills with **0 new distinct pages** (k0v4 11 ALIVE, a57v4 53 ALIVE / 7 DEAD, unchanged). The k0 side is closed negative: all 128 `kill-candidate (cert FAIL)` records of `cells140.open_pool`, re-emitted from A115's STORED measure with exact cores at zero LP cost, give **0 PASS**.

### Resume-block note (one line, §E)

**6. New lanes MUST emit through `attempts/A170-certfix/code/certwrap170.py`
(`make_certificate_exact(res, S_RAT, scale=scale, hyp=H)`), never `caselp.make_certificate` — which
silently reverts A135's exact cores to the stock ones via `Hyp.from_json`; `caselp.py` stays frozen and
the regression guard is `attempts/A170-certfix/code/test_cores170.py` (50 boxes, 50/50).**

### Resume-block note (one line, §E) — A171

**7. Any MULTI-BOX construction (case tree, cascade, sub-tree, forced-box node) MUST call
`attempts/A171-multibox-invariant/code/multibox.py` — `Node(boxes).normalise(s, nsub=4, refine=2)`
then `assert_invariant()` — BEFORE any chord row, lane cover, figure or LP, and treat `EmptyBox` as
the pair-leaf kill; `chord_rows` and `lane` refuse to run on an un-normalised node, and the guard is
`attempts/A171-multibox-invariant/tests/test_multibox.py` (A168's own S2 node `BR139/TRH-25` fails
the invariant as recorded — D's poses leave `[0,s]²` by 0.087938 — and passes after normalise).**

---

**A149 fold-in (2026-09-08/09, day lane after A137's night; append-only).** **The A57 ALIVE + FAIL
population is DRAINED: 240 nodes re-solved with A135's exact certified-maximal cores under the
FROZEN `verify_case.py`, 93 certified kills, 29.7 CPU-h, 0 WALL-CAP, 0 ERROR and NOT ONE node
reaching FAIL-with-holes — so `verify_case_v3` was never invoked and its ledger is empty by
construction.** Ledger `attempts/A149-a57-reprice/results/superseded_by_exactcore_A149.jsonl` in
A137's format (plus `box_source`, `frac_exact`, `frac_exact_band`, `verifier`); nothing in A57 was
rewritten. **§C.1 is superseded on its central question: the lever pays on the FAIL population,
not the ALIVE one — recorded FAIL 62.5 % (70/112) at 0.220 CPU-h per kill against recorded ALIVE
16.0 % (20/125) at 0.693**, because a FAIL is a node whose LP is already below budget and whose
certificate merely has holes a larger core closes, while an ALIVE node needs τ itself to fall. Run
the chore FAIL-FIRST; `targets137.py` defaults `--include_fail 0`. A145's `frac_exact` on n = 237
is monotone on ALIVE (100 / 50 / 28.2 / **7.3 %** by band, so §C.1's untested `< 0.30` band is 4×
weaker but not worthless) and nearly FLAT on FAIL (73.9 / 74.1 / 50 / 60 %), so rank an ALIVE queue
by it and simply run a FAIL queue. **§C.3's "an id is not a node" has a third and costlier
instance: 19 open G1-tree nodes are masked by a dead L1-tree row of the same id** and had never
been offered by any queue, because `targets137.py` — and anything that walks `tree_*.jsonl` into a
dict keyed by id — builds a LAST-WINS map. Run as their own lane they gave **14 kills of 19**, the
highest-yield population of the day, including the coordinator's priority node
`k5_11_interior_Y0275` (τ 4.999999999999965 → 3.999999999999985, frozen PASS in 33.7 s). **Key the
corpus by (tag, id).** Two further bookkeeping cuts, neither touching soundness: **728 of the 1,995
unsolved queued LP jobs (37 %) are already dead** by a supersession of the node or an ancestor
(`mkqueue137.py` tests recorded and claimed ids but not ancestry), and **`emit137.py`'s `done` set
reads one shard file instead of globbing `_s*`**, which is why 573 of §C.2's 849 level-1 children
were re-screens of ids already in the corpus — on the 276 genuinely new ones the geometry rate is
**22.5 %, not 27.4 %**, and the LP certifies **76.5 % of decided, not 78.8 %**, both of which move
the schedule the unfavourable way. `k5_11_interior_Y0130` is alive under BOTH cores: the exact
square core takes η from +0.500 to −4e-14 and stalls exactly at the budget, and A135's K′-pruned
polygon core (16 vertices, area 0.681528 against the square's 0.624994, +9.0 %) CONVERGES at
exactly 5.000000 — the node needs a different leaf, not a bigger core. Every certificate this lane
wrote carries the EXACT cores on every box (137/137 audited against A166's stock-core reversion,
`results/certaudit149.json`), because both node paths emit through A135's `make_cert` and never
through `caselp.make_certificate`; re-verifying all 55 stored non-PASS certificates with no
re-solve recovered **0** (40 LOST-KILL-ON-RESOLVE re-FAIL deterministically on real holes, 15
TOO-TIGHT have total ≥ budget and cannot PASS). The re-price of this campaign in `docs/budget.md`'s
own model is `attempts/A149-a57-reprice/notes/{reprice.md, dupwork.md, reemission.md}`.

*A149 addendum, operational (2026-09-09).* **The per-node process wall kills the node but not its
verifier grandchild.** `run137.py`/`run149.py` enforce the 1,500 s wall with `p.kill()` on the node
process; that node's own `emit135.run_case` child — the frozen `verify_case.py` — survives and runs
on with nobody to read it. Observed at the close of A149's A60 lane: one orphan on
`c0_Y1099` (a WALL-CAP row) had held a core for **2,914 CPU-seconds** before it was reaped. §D.5
made the process wall the deployable answer to the `Y0381` wedge, and it still is — but it must
kill the process TREE (Windows: `CREATE_NEW_PROCESS_GROUP` + `taskkill /T /F`, or a job object),
otherwise every WALL-CAP leaves an invisible worker behind and the box-count gate under-counts.
The verdict is unaffected: CAP is never a verdict and the node keeps its prior state.

*A183 addendum (2026-09-09 19:05, the k0 cascade re-normalised top-down with parent seeding, resumed
after the 15:46 crash; `attempts/A168-cascade-fable/notes/cascade.md` §A183).* **The record's fixed
points now nest.** A176 re-merged more than 16 parent-intersected pieces into one bounding box per
sub-bin, so a child could settle LOOSER than its parent (root/D0/S0 vol1 D 0.136 → children 0.159);
A181/A183 seed every child with the parent's fixed-point pieces exactly and `vol1 ≤ parent` holds on
every recorded node of both cells (0 violations, `renorm181b report`). The coordinator's refinement
lever (nsub 8 / refine 3 on every 4/2 survivor, seeded from its own 4/2 fixed point — sound, never
weaker, not idempotent) buys pose volume more than kills: l1_104 S1 28 → 28 ALIVE but vol1 D −18 %;
S2 111 → 64 ALIVE / 47 DEAD (ancestor 20, EmptyBox 23 of which **4 die only at 8/3**, inheritance 4),
vol1 H/D/S −16/−20/−17 % on the survivors; S3 partial (47 of 12,381: 37 ALIVE / 10 EmptyBox, 300 s a
node — ~17 CPU-days for the layer on two processes, a campaign). l1_153 (the Trump-image canary):
S1 6 → 6, S2 1 → 1 (its sliver-era wall cap was stale: 299 s at the full setting), S3 21 of 119 done,
all ALIVE. **The LP cannot consume the pieces as a list** under the frozen v1 verifier (one square
core per packed square; a union-of-cores exemption would break the bridge); it consumes them through
one square grown inside K′(role) (`lp183.py`), which on root/D0/S1 grows the union-box core by
0/0.9/2.7 % and leaves τ = 8.000 converged ALIVE — the geometry, not the LP, is the lever. Both cells
stay ALIVE; the open count is the S3 layer (l1_104 7,235 open S3 nodes under 64 live S2 parents -- the 47 S2 kills close 5,135 by ancestry; l1_153 97
S3 + 571 deeper). The v4 clause the polygon core would need: `hypotheses.poly_cores` with the exemption
"Q meets the closed convex polygon" by exact SAT over Q's axes and the polygon's edge normals.

### A205 fold-in (2026-09-10 night) — the CLIP TREE on the k5_11 / k5_16 survivors; what stays ALIVE and its next lever

`attempts/A205-clip-tree` (the PI's Y0202 reading; `notes/clip_tree.md`): branch on a forced slot's remaining meeter rows,
instantiate, A204's cascade + A203's rule S at every node.  **Retired at the window pad:** `k5_16_interior_Y0839` (526 s;
every BR(0,1) row dies by FC at BL(1,0)), `k5_11_interior_Y0308` (203 s), `k5_16_interior_Y0027` (365 s), `k5_16_interior_Y0054`
(312 s); `k5_16_interior_Y0491` (319 s, re-run with the fix after its first kill was retracted as a stale-table branch), `k5_16_interior_Y0565` (397 s).  **Survivors at the brief's 900 s wall** (both
pads, 1–5 kills each, 2–6 undecided branches): `k5_11_interior_Y0130 / Y0202 / Y0662 / Y0672 / Y0738 / Y0985` and the pages
the shard has not reached (`pages_todo.txt`; `results/cliptree205.jsonl` is the live row list).  **Y0202 at wall 3,600 s**
(`certs/extended/cliptree205_k5_11_interior_Y0202_w3600v3.json`): the sound re-run `_w3600v4`: 5 branches DEAD (BL(1,1)<-13 closed by the refresh round), FIVE fully named sharp leaves alive
(R.1.1.4s, R.1.5s, R.3.1.1s: pins + H + F1..F4 + one anonymous square, kept H 0.15–0.47, roles at 0.18–3 % of their seeds)
and two branches behind the wall (R.3.2, R.3.3 = BL(1,1)<-18 with BR(0,1)<-22 / 23).  **Next lever, named:** the LP on the
fully named leaves (A180's `lp180` with the roles' pieces as A191/A183's exact cores — the geometry has already collapsed the
roles to slivers), then the extended wall (3,600 s, 2 rounds a node) as the k5_11 row in a second shard, then the cost of
the 5-role fixed point (400 s a node: bisect only the roles whose K' changed).  Resume block: `bash
attempts/A205-clip-tree/code/run205.sh <pages>` (skips done pages), `bash code/ext205.sh <nid> <pad> <wall> <rounds> <tag>`.

### A206 fold-in (2026-09-11 afternoon) — Rule NS at the clip tree's fully named leaves; what stays ALIVE and its next lever

`attempts/A206-named-split` (the PI's Y0672 reading; `notes/named_split.md`): at a fully named node a SOFT name (a role not
provably missing a slot the node does not hypothesise it at) is SPLIT into [meets] / [misses]; the sliver first.  **Retired
at the window pad as whole trees (wall 3,600 s):** `k5_11_interior_Y0985` (2,121 s) and `k5_11_interior_Y1104` (2,401 s) —
no split needed, A205's 900 s wall was the limit.  **A205's fully named leaves closed:** Y0672 R.2.3.1 (the PI's node, 339 s:
F4 instantiated at cell 24, EmptyBox at round 1), Y0230 R.2.1.2s (2 splits, 2,242 s), Y0380 R.1.1s (2 splits, 1,077 s),
Y0083 R.3.1s / Y0865 R.1.3.2s / Y0202 R.1.2s / Y0202 R.3.1.1s (die in their own refresh cascade, 234-353 s).  **What
survives:** (i) Y0672's R.3 = TR(0,0)<-24 subtree (R.1, R.2 closed; R.3.1.2's H splits at fractions 0.64-0.75 undecided at the
depth cap, R.3.1.3-5 and R.3.2-4 behind the wall); (ii) sharp leaves with EVERY name HARD after 1-4 splits — Y0738
R.1.1.2s (3 leaves, 2 anonymous TR(0,0) rows), Y0402 R.1.3.1s (1), Y0941 R.3s (1) and R.4s (1, no soft name), Y0881 R.2.3s
(3), Y0202 R.1.5s (1, no soft name) and R.1.1.4s's miss branch (its 900 s quarter-wall); (iii) the pages the queues have
not reached (`code/queue_a.txt`: the pad-0 leaves; `code/queue_d.txt`: the whole trees of Y0202, Y0130, Y0662, Y0738 and
the k5_16 pages).  **Next lever, named:** the LP on the HARD-named sharp leaves (A180's `lp180` with the roles' pieces as
A191/A183's exact cores — every name is now a hypothesis, not a reach count, so the LP's cores are the roles' pieces at
their slots), then the 5-role fixed point's cost (300-700 s a node: bisect only the roles whose K' changed, A183's parent
seeding of the per-piece K' cache), then the whole trees at 3,600 s for the remaining k5_16 pages.  Resume block: `bash
attempts/A206-named-split/code/queue206.sh <queue file>` (one worker per file; `run206.sh` skips cached runs; `leaf <nid> <pad>
<leaf> [standard|extended|a206 <tag> <wall>]`, `tree <nid> <pad>[+<branch>] [wall]`), `bash scratch/auditor206.sh` (the
auditor, one at a time within the 3-process cap).

**A211 fold-in (2026-09-12 evening):** the coarse tree's window-pad (g1) kills of A57 tree ids land in `attempts/A211-coarse-tree/results/superseded_by_coarsetree_A211.jsonl` (the A137 / A149 / A209 ledger format: id, applies_to_tags = the tree, prior verdict RETAINED, closes_subtree by Lemma K1; `[C: closed-form / library clip trace + the leaf lemma]`, no verifier clause) — fold it like A209's `superseded_by_k5killer_A209.jsonl` before any A57 resume; A57's own files are never written by A211.

**A212 fold-in (2026-09-14):** the trump5 tree's pad-0 (s0-only, lam = 1) kills of A60 nodes are folded into `attempts/A212-trump5-tree/results/superseded_by_trump5tree_A212.jsonl` (camp A60, applies_to_tags [trump5_j0], the currency of A60's own s0 certificates); TRUMP-TUBE verdicts are uniqueness leaves, not kills, and are not folded.  The gate is false on every alive trump5 record (the Trump-containing residue was A60's ladder, discharged by A60/A83).
