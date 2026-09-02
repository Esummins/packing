# A60 resume plan (2026-09-02, after the overnight session kill)

## What happened
The API-usage-limit kill of the driving session took the detached cover shards with it.
Shards 0/1/2 finished (192/192); shard 3 died mid-LP on `c0_Y0790` at 01:45 (logged the `[LP]`
line, no verdict, clean stderr, no partial node json).  Integrity sweep: 0 damaged artefacts.
Shard 3 relaunched, resumed exactly at Y0790.

## Completed cover j=0 kill rate (695/767 resolved at relaunch)
PASS 543, LP-alive 85, cert-FAIL 67 -> **kill rate 0.781** (PASS / attempted).
The remaining ~72 (shard 3) are finishing; the final rate updates on completion.

## Phase plan, in order

1. **Finish cover j=0** (shard 3, ~72 children).  Gate: all four progress files at 192/191.
2. **deepen round 1** on `a60_cover_j0.jsonl` — the T11 loop, the real cost driver (G-A60-3).
   Input = every LP-alive + cert-FAIL child with a box (~152 at relaunch, ~168 projected).
   Each box is bisected; the two halves are re-gated at the SAME budget 5 (sound: a refinement
   of the same disjunction).  Sub-boxes have larger rational cores (a -> 1/2), which is what makes
   the retry bite.  Shard 4-way; budget-5 LPs, so <= 4 heavy.
   Expected yield: A57's depth-2 pass killed 6/6 resisters; here the sub-boxes that go
   `contradictory`/`unkillable`/`shared` cost 0 (exact), only the still-`attemptable` ones LP.
3. **deepen round 2** on `a60_deepen_j0_r1.jsonl` — same, for round-1 resisters that still resist.
   Stop when a round produces no new attemptable sub-boxes.
4. **residue ladder** (`ladder --cond ""`) — the 540-item exact kill queue that localises square 1
   to its 28 basin boxes (already scanned; `results/a60_ladder_j0_scan.json`).
5. **squares 2-3** — condition on located boxes (NOT basin balls), re-run cover+ladder; interior
   tree closes at conditioning depth 3.  **Re-land at level 27+ to clear the D.S6 budget** (the
   1.04x margin + widening does not fit at level 26 — notes/ledger.md 8.3).
6. **outer triple (sq4/sq6/sq10)** — confinement route only (`confine60.py`); zone covers are
   structurally dead there (G-A60-2).  Drive each to its (D) radius rBasin - widening.
7. **window form** — re-emit every (K) leaf at the delta=1e-4 slack-core grid (371 sides), once
   D.S6's budget is written and the grid is committed.

## Process discipline (unchanged)
<= 4 heavy LP; BLAS-pinned via launch.ps1 / blas1.py; commit-headroom check before launch;
attribute shared-filename processes by --out path; liveness by script name not pid file;
integrity60.py before any resume; defer() catches MemoryError.  See notes/RESUME.md.
