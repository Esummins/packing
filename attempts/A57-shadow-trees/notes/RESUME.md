# A57 — how to resume

All A57 code lives in `code/` (A54 code copied unmodified + five A57 files).  Nothing outside
`attempts/A57-shadow-trees/` is ever written.  `trump5` is refused as a certification target by
`ladder57.py`; every child is checked with `substrat.trump_realizes` before certification.

## A57's own files

| file | what |
|---|---|
| `code/tree57.py` | rung-3 tree driver: t-uniform θ cover, easiest-first, sibling column folding, resumable, progress files.  `--plan_only` prints the cover. |
| `code/warm57.py` | merged warm start over A53/A54/A55/A57 artefacts incl. `_state*.json` checkpoints (A55/k3_ext E3).  `atoms_only=True` for column-only warm starts. |
| `code/zonescan.py` | per-zone NO + YES-sample scan (which zone is worth branching on). |
| `code/zoneshrink.py` | how small can the branch zone be and still have a killable NO child. |
| `code/probe2.py` | the a-curve: τ of a YES child vs the core half-side a. |
| `code/alivewitness.py` | **the ALIVE-side arbiter** (A57-3 disjoint-family bound), exact rational. |
| `code/ladder57.py` | rung-1/2 extension pass for one stratum (A54 ladder + A55 E3 folding). |
| `code/board.py` | scoreboard aggregation over all `results/tree_*.jsonl`. |
| `code/launch.ps1` | detached shard launcher (`Start-Process`, pid file, per-shard logs). |

## resumability

* `tree57.py`: every finished child appends one line to `results/tree_<key>_s<i>.jsonl` and its
  node LP to `results/tree/<key>/<id>.json`; `progress/<key>_s<i>.json` is rewritten after each
  child.  Re-running the same `--name/--zone/--tag/--shard` **skips finished children and
  re-folds their columns** into the warm pool.  `--wall_seconds` stops cleanly.
* `zonescan.py`: same discipline, `results/zonescan_<name>_<tag>.jsonl`.
* `ladder57.py`: writes `results/nodes/<name>_state.json` every iteration; the next pass folds it
  back through `warm57.merged_warm`, so an interrupted pass loses no columns (A55 E3).

## restart lines

    powershell -File code\launch.ps1 -Name k5_11 -Shard 0/6 -Tag L1     # tree shard
    python code\zonescan.py  --name k5_16 --tl 300 --tag zs1
    python code\ladder57.py  --name k5_11 --tag e2 --time_limit 3000
    python code\alivewitness.py --name k5_16 --box '<box json>' --tilts "0,40.18194,45,20,60,70"

## process discipline

≤ 3 heavy processes while A56's `final_sweep.py` runs, 5 after.  Check with
`Get-CimInstance Win32_Process -Filter "Name like 'python%'"`.  A54 W7: HiGHS raised
`MemoryError` at 32 k rows × 6 k columns with four such jobs on this 31.7 GB machine — child
solves therefore use **column-only warm starts** (`rows=[]`), which also cut an LP iteration
from 44 s to 13–18 s.

## what is running right now (2026-09-01 ~10:10 PDT)

| pid | job | note |
|---|---|---|
| 3780 | `tree57.py --name k5_11 --zone interior --tag L1 --shard 0/6` | L1 tree, 193 children |
| 42440 | `tree57.py --name k5_16 --zone interior --tag L1 --shard 0/6` | L1 tree, 193 children |
| 10996 | `ladder57.py --name k5_11 --tag e1` | rung-1/2 extension pass (A55 E3 column folding); the direct route on k5_11 was only 1.9 % short at A54 W3 |
| 34460 | `code\scaleup.ps1` | auto-scaler: holds A57 at ≤ 3 heavy processes while A56's `final_sweep.py` lives, then launches shards 1/6 … 5/6 of both strata up to 5 |

## not yet done / next

* **shards 1/6 … 5/6** of both interior covers — queued in `scaleup.ps1`, no action needed.
* **`zonescan.py` needs a re-run.** It was started before `pinguard.py` existed and stopped;
  its corner/side YES samples were meaningless because those zones contain pins.  It is now
  guarded (it samples only `ok` boxes and prints the pinguard census per zone) but has produced
  no records yet.  Only needed if the interior branch turns out not to close a stratum —
  the interior cover alone is a complete disjunction (T1), so a second zone is a fallback,
  not a requirement.
* **depth 2** is currently unnecessary: the NO child of the interior zone is *killed* at both
  strata, so no child "stays at budget".  If some `ok` YES child resists, branch it on a second
  zone (its budget is 11−k−1 = 5, so the same machinery applies with `--zone` changed).
* **`alivewitness.py` on any resisting child** before spending more compute on it: if a
  strictly-separated 5-family exists in its residual, no certificate can ever exist and the
  child must be split instead.

## depth 2

`code/deepen.py --key <key>` reads every `ALIVE-at-LP` record of a level-1 key, bisects that
child's box `--levels` times (3 → 8 sub-boxes, a: 0.3566 → ~0.424) and solves/certifies each at
the **same** budget — a refinement of the same disjunction, so no further budget is spent.  Run
it after (or alongside) the L1 shards; it is resumable through `results/tree_<key>_D2.jsonl`.
`tree57.py` leaves ALIVE records alone precisely so that `deepen.py` owns them.

`code/epsladder.py` (also `tree57.py --eps_ladder`, default OFF) is the rejected repair — see
notes T11.  Sound, but it cost ~190 s and failed on the one resister it was built for.

## the theta-stratified diagnostic

    python code/tree57.py --name k5_16 --zone interior --tag TS --sample_theta 24

Runs 24 pinguard-**ok** children spread evenly over the eight t-slabs, to estimate the resister
rate without the easiest-first theta bias (notes T12).  Child ids come from the canonical
ghost-distance ordering, so this shares node jsons with the shard runs and never collides with
them; results land in `results/tree_<name>_interior_TS_s0.jsonl` under its own tag.  Worth one
slot once the cap rises, before trusting any interim projection of depth-2 capacity.

## operational note: run exactly ONE scaler

`scaleup.ps1` now carries a single-instance guard (oldest wins, newer instances log and exit).
Two scalers each hold their own queue index and would launch the **same** shard twice, so two
`tree57.py` processes would race on one jsonl and redo each other's children — wasteful rather
than unsound (records are append-only and node jsons are last-wins), but it also breaks the
process cap.  Check with:

    Get-CimInstance Win32_Process -Filter "Name like 'powershell%'" |
      Where-Object { $_.CommandLine -like '*scaleup.ps1*' }

**Match `-File ...scaleup.ps1`, never bare `scaleup.ps1`.**  A `powershell -Command` that merely
MENTIONS the script — i.e. every status check written above — has the string in its own
CommandLine and is counted as a running scaler.  That false positive cost a real outage: status
checks looked like a stream of mysterious restarts, the genuine scaler was killed as a
"duplicate" at 11:07 and nothing replaced it for ~1.5 h, and the single-instance guard would have
made every honest new instance exit on sight.  Both the guard and the checks now filter on
`-File`.

Two more traps from the same episode:
* `Stop-Process` on a scaler from inside a PowerShell tool call can take the tool session down
  with it — the call reports a non-zero exit *after* its `Start-Process` already succeeded, so a
  "failed" restart may still have spawned the new scaler.  Re-check the process list; never
  trust the exit code.
* `Add-Content` loses lines to file-lock contention when two processes log at once, which is why
  `logs/scaleup.log` has "scaleup started" entries but no "launched ..." entries from the
  contended window.  `Note` now retries.  **Missing log lines are not missing launches** —
  confirm against the process list.

## retroactive T14 sweep

    python code/sweepfails.py --dry_run     # list eligible cert-FAIL records
    python code/sweepfails.py               # re-certify each with --eps_geo, append corrected records

`tree57.py` runs the eps_geo retry inline now, but shards launched before that wiring record a
bare `FAIL(rc=1)`.  This sweep covers them without disturbing a running shard (no restart, no
lost LP work).  Only `rc=1` is eligible — `rc=3` is the T11 knife edge and wants `deepen.py`.
Idempotent: a node with a `certs/epsgeo/<id>.json.PASS` marker is skipped.  Corrected records are
APPENDED (board.py keeps the last record per id), so both lines stay on disk for the audit trail.

## pending: re-sweep Y0461 with the right margins

`k5_11_interior_Y0461` (tau 4.916667, ceiling **1.0169**) was written off by the FIRST sweep,
which still used the fixed margins 0.002/0.004 — both far too large for that headroom (T16 would
choose 0.0005/0.001).  Its record now reads "queued for depth 2", so the eligibility filter skips
it.  Re-run it explicitly when a slot is free:

    python code/sweepfails.py --ids k5_11_interior_Y0461 --rounds 1 --jobs 2 --depth 60

This is an optimisation, not a correctness issue — `deepen.py` will kill it at depth 2 either
way, just for ~8 sub-solves instead of ~2 minutes.  General lesson: **a sweep killed mid-flight
leaves records written by the superseded logic**, and the "queued for depth 2" filter then treats
those premature verdicts as final.  `--ids` exists to override that.

## the T14 sweep runs as a daemon

    python code/sweepfails.py --watch 600 --rounds 1 --jobs 2 --depth 60

The shards launched before the T14 wiring keep emitting `FAIL(rc=1)` records, and a one-shot
sweep only ever sees the snapshot it started with — three separate hand-runs were needed before
this was obvious.  `--watch N` re-scans every N seconds, so new failures are picked up without
touching a running shard.  Margins are chosen per node from its scale headroom (T16), and
records already routed to depth 2 are left alone.  One instance is enough; it counts against the
process cap.

## always launch through launch.ps1 / run_job.ps1

Both pin `OPENBLAS_NUM_THREADS / OMP_NUM_THREADS / MKL_NUM_THREADS / NUMEXPR_NUM_THREADS = 1`.
Launching a worker any other way risks the T18 failure: with ~20 BLAS threads per process,
several concurrent jobs exhaust thread arenas and a *76 MiB* numpy allocation fails with ~10 GB
free, killing jobs outright (it took out one tree shard and one deepen job simultaneously).

    powershell -File code\run_job.ps1 -Script deepen.py -JobArgs "--key k5_11_interior_L1 --levels 3" -Tag deepen_k5_11


## memory discipline (T19) — read before launching anything

* **Check commit, not RAM.**  `(Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory / 1MB`
  is commit-available in GB; `TotalVirtualMemorySize` is the commit limit.  A worker reserves
  2-4 GB of commit against a 0.5-1.2 GB working set, so free physical memory badly overstates
  the room available.  `scaleup.ps1` gates at 10.5 GB and will sit idle below it.
* **Every Python process costs ~628 MB of commit before it works** (measured on a bare
  `import numpy`).  That is why `VERIFY_JOBS_CAP = 1`: `verify_case.py --jobs N` spawns an
  `mp.Pool` of N on top of itself and its parent.  Do not raise it to buy verifier speed without
  checking commit headroom first.
* **`A57_ORACLE_CHUNK`** (default 2e6) bounds the oracle's numpy temporaries.  Raising it speeds
  the oracles slightly and raises steady commit permanently (Windows keeps the charge on freed
  blocks).  Result-neutral either way.
* **Deferred nodes**: `results/deferred_<key>.jsonl` lists nodes skipped on a MemoryError.  They
  are deliberately NOT in the summary, so simply re-running the shard picks them up.

## current state after the T19 commit work (2026-09-01 ~16:40)

* **Running:** 2 `tree57.py` shards only, holding 4.39 and 3.86 GB of commit.  They started
  BEFORE the T19 trims, so they still carry `--jobs 2` verifier fan-out and the old 1e7/2e7
  oracle chunks; they were deliberately NOT recycled (coordinator: do not destabilise a running
  shard).  Recycling them is the single biggest immediate saving available and is safe whenever
  wanted — they are resumable and skip finished children.
* **Stopped deliberately:** the `sweepfails.py --watch` daemon, to give commit back to A60.
  Commit-available went 1.42 GB -> 5.71 GB when it went (its in-flight certify subtree went with
  it).  Nothing was lost: the sweep writes no record until it concludes, so its in-flight child
  stays eligible.  **Restart it when commit-available is comfortably above ~10 GB:**

      powershell -File code\run_job.ps1 -Script sweepfails.py -JobArgs "--watch 600 --rounds 1 --jobs 2 --depth 60 --cert_time 300" -Tag sweepfails

  Until then `deepen.py` covers the same children, just more expensively.
* **Scaler:** commit-gated at 10.5 GB, so it will sit idle rather than add workers while the box
  is tight.  It has been logging unreliably (starts silently); confirm what it is doing from the
  process list, not from `logs/scaleup.log`.

## depth-2 backlog (as of 2026-09-01 ~17:00)

**23 children queued for depth 2; 21 depth-2 children already certified; no `deepen.py` running.**
This is by design, not neglect: the brief specifies breadth-first, so level 1 is finished before
the refinement pass, and the backlog grows while L1 runs.  `scaleup.ps1` launches `deepen.py`
once its L1 shard queue is exhausted AND commit-available clears 10.5 GB.

To run it sooner (it is the proven killer — every parent it has touched died, 8/8 on Y0017):

    powershell -File code\run_job.ps1 -Script deepen.py -JobArgs "--key k5_11_interior_L1 --levels 3 --time_limit 240 --cert_time 240" -Tag deepen_k5_11

Check commit-available first; a deepen worker peaks around 4 GB.  Trading one L1 shard for a
deepen worker is commit-neutral if the box is tight.


## after a machine restart

Nothing is lost — all results are on disk and every worker resumes by skipping finished children.
Relaunch in this order, and check the resume header of each shard (`grep '=== A57' logs/<shard>.log
| tail -1` should show a non-zero `done=`):

    powershell -File code\launch.ps1  -Name k5_11 -Shard 0/6 -Tag L1 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
    powershell -File code\launch.ps1  -Name k5_16 -Shard 0/6 -Tag L1 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
    powershell -File codeun_job.ps1 -Script deepen.py     -JobArgs "--key k5_11_interior_L1 --levels 3 --time_limit 240 --cert_time 240" -Tag deepen_k5_11
    powershell -File codeun_job.ps1 -Script sweepfails.py -JobArgs "--watch 600 --rounds 1 --jobs 2 --depth 60 --cert_time 300" -Tag sweepfails
    Start-Process powershell -ArgumentList '-ExecutionPolicy','Bypass','-File','code\scaleup.ps1' -WindowStyle Hidden

Shards 0/6 are NOT in the scaler's queue (it starts at 1/6), so they must be started by hand; the
scaler fills the rest up to the cap.

**Do not trust a command-line scan to tell you whether a scaler is running** — your own status
check contains the script name and will match (this cost a scaler twice).  Check
`logs/scaleup.pid` and confirm that pid is a live `powershell` whose command line lacks
`-NonInteractive`, or just read the tail of `logs/scaleup.log` for a fresh `scaleup started`.

## attributing processes during a resource investigation

    python code/whose.py --certify-only

Do NOT identify a process by its script name or by "some path in the command line".  The lab
copies code between campaigns, so one command line can name three campaigns at once: the script
may be A54's copy, the data and the `--out` target A61's.  Attribute by the **`--out` target**
(fallback: the data/node argument; script path only as a flagged last resort).  Getting this wrong
put 11.5 GB on the wrong campaign in T27, and the error was invisible until a single extra tag was
added to the match list.
