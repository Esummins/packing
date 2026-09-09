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
