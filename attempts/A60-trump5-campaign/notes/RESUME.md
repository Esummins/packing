# A60 — how to resume the trump5 campaign

All A60 code lives in `code/` (A59's stack copied unmodified + `tree60.py`, `selftest60.py`,
`falsify60.py`, `launch.ps1`, plus two local edits: `warm57.py` now also reads A57/A59 artefacts).
**Nothing outside `attempts/A60-trump5-campaign/` is ever written.**  A29 untouched.

## The one thing to know before touching anything

**Condition on the boxes the previous ladder produced — never on a basin-radius ball.**
Conditioning square j in a ball of radius h = 3.7e-3 makes the next ladder diverge
(notes/falsifier.md §2).  Conditioning on the located box (radius ~4.4e-4, or a merged bounding
box of radius ≤ 1.5e-3) makes it terminate at level 24.  `ladder_scan`/`census`/`phase_*` all take
`cond_boxes=[...]`; the `basin_box(name)` default is a *diagnostic convenience only*.

## Files

| file | what |
|---|---|
| `code/tree60.py` | the campaign driver.  Sub-commands `census`, `cover`, `ladderscan`, `ladder`, `deepen`, `board`.  Alive gate + zero-atom vacuity arbiter + A57 T14 eps_geo retry folded in. |
| `code/selftest60.py` | P0 selftests T1–T6 (reproductions of A59's measurements).  **Run before any launch.** |
| `code/falsify60.py` | stratified LP pricing of a ladder kill queue. |
| `code/launch.ps1` | detached launcher (pid file + per-job log).  PowerShell drops empty strings, so for the j = 0 (unconditioned) phases call python directly and omit `--cond`. |

## Resumability

Every phase writes one jsonl record per finished child (`results/a60_<phase>_j<J>*.jsonl`), one
node json per LP (`results/nodes/<tag>.json`), and rewrites `progress/<phase>_j<J>_s<i>.json`
after every child.  Re-running the same phase/shard **skips finished children** (the `Sink`
loads the jsonl into a done-set) and re-folds their columns into the warm pool (A57 T4).
`--wall <seconds>` stops cleanly.  Corrected records (eps_geo retries) are APPENDED; `board`
keeps the **last** record per tag, so both lines stay on disk for the audit trail.

    python code\tree60.py board          # consolidated per-phase scoreboard -> results/a60_scoreboard.json

## Restart lines

    python code\selftest60.py                                    # 6/6 must PASS first
    python code\tree60.py cover  --shard 0/2 --wall 172800        # j = 0 interior cover (767 attemptable, budget 5)
    python code\tree60.py ladderscan --cond ""  --levels 26       # exact, no LP: the residue ladder + kill queue
    python code\tree60.py ladder --cond "" --shard 0/2            # kill that queue
    python code\tree60.py deepen --source a60_cover_j0.jsonl --round 1 --shard 0/2
    python code\falsify60.py --cond sq7 --n 12 --shard 0/2

## Process discipline

≤ **4** heavy LP processes for A60.  A57 (`tree57.py` k5_11/k5_16 + `certify.py`) and A61
(`resolve61.py`) own the rest of this 31.7 GB / 20-core machine.

**A57 T18 — pin BLAS to one thread in EVERY worker.  This is the actual root cause.**
numpy/OpenBLAS spawns ~one thread per core (20 here) in every process, each with its own
allocation arenas; concurrent jobs multiply that until an allocation fails against fragmentation
while GBs sit free.  Measured twice on the same day: A57 lost a tree shard *and* a deepen job to
a 76.3 MiB failure at **9.9 GB free**; A60's cover shard 1/2 died on **66.6 MiB at 9.1 GB free**.
A54 W7 is the same failure, worked around by pruning columns — that treated the symptom.  These
jobs are LP + numpy-oracle work, not BLAS-bound, so the parallelism bought nothing.

Adopted at BOTH layers, because the restart lines above invoke python directly and would not
inherit PowerShell environment:

* `code/launch.ps1` sets `OPENBLAS_NUM_THREADS = OMP_NUM_THREADS = MKL_NUM_THREADS =
  NUMEXPR_NUM_THREADS = 1` (child `certify.py` / `verify_case.py` processes inherit them);
* `code/blas1.py` sets the same in-process and is imported **before numpy** by every entry point
  (`tree60`, `falsify60`, `confine60`, `selftest60`, `sidezones60`).  It warns loudly if numpy
  was already imported, and respects pre-existing values so an operator can override.

Verified after adoption: A60 workers run at **1–4 threads / 54–140 MB** against **21–22 threads /
0.3–1.8 GB** for the pre-T18 processes still on the machine.  **Launch nothing that does not go
through one of those two paths.**

**T18 is necessary but NOT sufficient — the second constraint is the machine's COMMIT LIMIT.**
After the pinning was applied and verified active (1–4 threads), cover shard 1/2 died *again*:

    numpy ArrayMemoryError: Unable to allocate 37.9 MiB for an array with shape (150544, 33)
    ... lpbox.py:673 coverage()   <- the column oracle, not BLAS

Measured at the time: commit **57.7 / 61.0 GB**, headroom 3.4 GB, while the pagefile held only
212 MB of its 30 GB allocation and A60's own workers were 52–140 MB.  The committers are the
lab's other attempts — a single `certify.py` reserving **6.7 GB** of commit against a 1.75 GB
working set, plus two `tree57.py` at ~4 GB each.  So this is a **shared-resource** condition, not
an A60 bug, and A60 cannot fix it by shrinking further.

Two responses, both in place:

1. **A60 workers now survive an allocation failure.**  `tree60.defer()` catches `MemoryError`
   (numpy's `_ArrayMemoryError` subclasses it) in all three phases, writes the node to
   `results/a60_deferred_j<J>.jsonl`, sleeps 30 s and continues.  A deferred node is deliberately
   **NOT** added to the phase's done-set, so the next pass re-attempts it — one failed 37.9 MiB
   allocation no longer destroys a shard holding hundreds of queued children.  `board` surfaces a
   `deferred` section listing any tag that is still unresolved; **treat a non-empty
   `still_unresolved` list as outstanding work, never as progress.**
2. The commit headroom check below stays, as a launch gate.

**For the coordinator / machine owner (outside A60's remit):** the commit limit is RAM + pagefile
= 31.7 + 30 ≈ 61 GB, and the pagefile is capped at 30 GB while barely being used (212 MB). Raising
that cap would raise the commit limit directly and is the cheapest global fix. Changing a system
setting is not something this attempt should do on its own.

Secondary guard — commit, not free physical RAM.  Watch the COMMIT charge:

    $os=Get-CimInstance Win32_OperatingSystem
    "CommitHeadroomGB {0:N2}" -f ($os.FreeVirtualMemory/1MB)

Pinned workers are light, so ~3 GB of headroom is enough for one more; the pre-T18 6 GB rule was
calibrated against 20-thread processes and is now over-cautious.  Dead shards are harmless — every
phase is resumable, so a shard that dies is restarted with the same command line and skips what it
finished.  Check liveness with

    foreach ($f in Get-ChildItem progress\*.pid) { $id=(Get-Content $f).Trim()
      "{0,-28} pid {1,-7} alive={2}" -f $f.BaseName,$id,
        ($null -ne (Get-Process -Id $id -ErrorAction SilentlyContinue)) }

Child solves use **columns-only** warm starts (`rows=[]`), per A54 W7 / A57 T4.

## What is running (2026-09-01, end of the P0 + falsifier session)

| job | shard | state |
|---|---|---|
| `tree60.py cover` (j = 0 interior, budget 5, 767 attemptable) | 0/2 | **detached, running, BLAS-pinned**, `--wall 172800`, resumable |
| `tree60.py cover` | 1/2 | **detached, running, BLAS-pinned** (was the T18 casualty; relaunched after the fix) |
| `confine60.py --sq sq10` (j = 3, budget 3) | — | detached, the G-A60-2 route check |
| `falsify60.py --cond sq7` (budget 4 pricing) | 0/2, 1/2 | stopped after 7 samples to free commit; data banked |
| `sidezones60.py` | — | stopped: the route it measures is a dead end (see step 6) |

Also on the machine and NOT to be disturbed: A57 (`tree57.py` k5_11 / k5_16 + `certify.py`) and
A61 (`resolve61.py` ×2).  A29 untouched.

## Next, in order

1. **Let the j = 0 cover finish** (767 attemptable, ~13 CPU-h + the deepen rounds).  Its kill rate
   is the number that sets the whole campaign's price — see G-A60-3.
2. **`deepen --round 1`** on `a60_cover_j0.jsonl`, then round 2 on round 1's output.  This is the
   real cost driver, not the alive gate.
3. **`ladder --cond ""`** (540 queue kills) → the 28 located boxes for square 1
   (`results/a60_located_sq1.json`, already computed).
4. **Merge before branching**: bounding box per hug class, 28 → 3 branches (sq7 and sq8 merge
   cleanly at radius 1.33e-3 / 1.78e-3; **sq9's full merge is too loose — split it 2 ways**).
   Rule: merged conditioning radius ≤ 1.5e-3.
5. Levels 2 and 3 (already scanned exactly: 7–10 residue then 0 — the interior tree closes at
   conditioning depth 3).
6. **The outer triple** (G-A60-2) — **do NOT cover the side zones.**  Measured dead end: side_R
   at j = 3 has 0 attemptable boxes out of 444 and its residue diverges (19 → 1780 by level 12,
   containment frozen at 0.407, kill queue 0 at every level).  Structural: conditioning removes a
   witness *and* a unit of budget, so a box that reaches only one Trump square is always
   ALIVE-CERTIFIED.  Use **confinement** instead (`code/confine60.py`): a NO-family around
   Trump's placement drops a witness while a NO child keeps the parent budget.  That is the
   regime the pilot measured PASS at j = 2…5.
7. Hand every (K) leaf to A56 for the s-parametric window (G-A59-7).  Still the open cost line.

## Canary discipline (non-negotiable)

Trump's configuration is never killed and must land in a (D) leaf.  Three independent guards:
`substrat.trump_realizes` before any certification (`tree60.kill` refuses outright), the alive
gate (Lemma A57-3 — the 3 interior cover boxes holding his sq7/sq8/sq9 are alive-gated
**unkillable**, so no LP is ever launched on them), and selftest T3.  **Zero canary events and
zero engine-bug events so far.**
