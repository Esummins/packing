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

**T18 alone was not sufficient — but the second constraint (COMMIT) is now LIFTED.**
History, kept because it explains the machinery: after the pinning was applied and verified
active (1–4 threads), cover shard 1/2 still died —

    numpy ArrayMemoryError: Unable to allocate 37.9 MiB for an array with shape (150544, 33)
    ... lpbox.py:673 coverage()   <- the column oracle, not BLAS

— because the machine's commit limit was 61.0 GB (31.7 GB RAM + a 30 GB pagefile cap) and the
lab's other attempts sat against it (one `certify.py` reserving 6.7 GB of commit against a 1.75 GB
working set) while A60's own workers were ~50 MB.

**2026-09-01, after the PI's restart:** the pagefile moved to `F:\pagefile.sys`, **25 GB initial /
100 GB maximum**, so the commit limit is 56 GB now and grows on demand to ~130 GB.  The commit
constraint is effectively gone; measured with four A60 shards plus A57/A61 running, headroom was
17.4 GB with the pagefile still at 0 bytes used.  **Keep both mitigations anyway** — they are
cheap and the failure modes are real:

1. **BLAS pinning stays mandatory** (T18 is about thread arenas, not the commit limit, so a bigger
   pagefile does not address it): `code/launch.ps1` and `code/blas1.py`.
2. **`tree60.defer()` stays.**  It catches `MemoryError` (numpy's `_ArrayMemoryError` subclasses
   it) in all three phases, writes the node to `results/a60_deferred_j<J>.jsonl`, sleeps 30 s and
   continues.  A deferred node is deliberately **NOT** added to the phase's done-set, so a later
   pass re-attempts it.  `board` surfaces a `deferred` section; **treat a non-empty
   `still_unresolved` list as outstanding work, never as progress.**

Concurrency: A60's cap is 4 heavy LP shards, and with commit lifted that cap is now the binding
one rather than memory.  Measured at 4 shards: 1–3 threads and 46–148 MB per worker.

Secondary guard — commit, not free physical RAM.  Watch the COMMIT charge:

    $os=Get-CimInstance Win32_OperatingSystem
    "CommitHeadroomGB {0:N2}" -f ($os.FreeVirtualMemory/1MB)

Pinned workers are light, so ~3 GB of headroom is enough for one more; the pre-T18 6 GB rule was
calibrated against 20-thread processes and is now over-cautious.  Dead shards are harmless — every
phase is resumable, so a shard that dies is restarted with the same command line and skips what it
finished.

**Do NOT check liveness from the .pid files alone.**  Two ways that lied, both observed here:

1. *PID recycling across a reboot.*  After the 19:08 crash, `progress/cover_j0_s2-4.pid` still
   held 6300 and `Get-Process -Id 6300` reported alive — 6300 had been reused by `VSSrv.exe`.
   Every A60 process was in fact dead.
2. *Matching the wrong string.*  Filtering `CommandLine -like '*A60-trump5-campaign*'` finds
   nothing, because the launchers pass a RELATIVE script path (`code	ree60.py`) with the
   attempt directory only in `-WorkingDirectory`.

Check by SCRIPT NAME instead, which is immune to both:

    Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
      Where-Object { $_.CommandLine -match 'tree60\.py|slackcore60\.py|confine60\.py' } |
      ForEach-Object {
        $m = if ($_.CommandLine -match '--shard\s+(\S+)') { "cover shard " + $Matches[1] }
             elseif ($_.CommandLine -match 'slackcore60') { 'slackcore' } else { 'other' }
        $pr = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
        "{0,-18} pid {1,-7} threads={2,-3} wsMB={3}" -f $m,$_.ProcessId,$pr.Threads.Count,
          [int]($pr.WorkingSet64/1MB) }

Stale `.pid` files after a reboot are meaningless; the launchers overwrite their own on start.

**Attributing a shared-filename process to an attempt: use the OUTPUT path, not the name and
not the script path.**  A60 got this wrong twice in one session, each time more subtly:

1. *By process name* — `certify.py` is copied into every campaign directory, so "the big
   `certify.py` committers" says nothing about who owns them.  (A57's T27 names this trap.)
2. *By script path* — the fix "attribute by path" is still not enough, because this lab **copies
   code between campaigns**: A54's `certify.py` is what A61 runs, exactly as A59's stack was
   copied into A60.  A command line therefore contains SEVERAL attempt paths, and the first one
   (the script) is the wrong one.

Measured on the two biggest committers here, which resolve differently under each rule:

    pid 26760  8835 MB   script path A54-stragglers   -->  --out A61-window-stragglers/certs/k5_10.json
    pid 31932  5555 MB   script path A54-stragglers   -->  --out A61-window-stragglers/certs/k5_05.json

    by script path:  A54 2 procs 14.05 GB  |  A61 2 procs 0.19 GB     <- wrong
    by output path:  A54 -                 |  A61 4 procs 14.25 GB    <- right (matches A57's audit)

**Rule: attribute by the `--out` target, falling back to the data/node argument; never the script
path and never the process name.**  The `--jobs 3` in those command lines is a second confirming
signal — A57 and A60 both certify at `--jobs 1`/`--jobs 2`.

**After any crash, run the integrity sweep before resuming:**

    python code\integrity60.py          # report
    python code\integrity60.py --fix    # trim torn jsonl tails / quarantine torn json

It checks every `results/*.jsonl` line, every `results/nodes/*.json` (a torn one makes a shard
crash on resume — `run_child` does a bare `json.load`), every `certs/*.json` **and its `.PASS`
marker together** (a torn certificate under a PASS marker is a false claim of proof), and reports
orphan markers.  Quarantines under `crashquarantine/`, never deletes.  After the 19:08 hard crash
it found **zero** damaged artefacts — appends are whole-line and node/cert writes are
dump-to-fresh-file, so power loss left nothing half-written.

Child solves use **columns-only** warm starts (`rows=[]`), per A54 W7 / A57 T4.

## What is running (2026-09-01, end of the P0 + falsifier session)

| job | shard | state |
|---|---|---|
| `tree60.py cover` (j = 0 interior, budget 5, 767 attemptable) | 0/4, 1/4, 2/4, 3/4 | **detached, running, BLAS-pinned + defer-resilient**, `--wall 172800` |

Relaunched through `code\launch.ps1` after the PI's restart; all four shards skipped exactly the
65 children already on disk (`skipped` in each progress file sums to 65) and picked up at four
consecutive unfinished children.  Earlier phases (`falsify60`, `confine60`) are complete and their
records are banked; `sidezones60` measured a dead-end route and is not to be rerun.

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
