# A57 / A96 — PAUSED v2, 2026-09-07 08:00 PDT (end of the A123 night-shift window)

Nothing is running. This pause used the **sentinel path** (`PAUSE` file, drivers stop between
nodes), so unlike the 2026-09-06 pause **no in-flight work was discarded**: every worker
finished its current node, recorded it, and exited. Everything below is resumable.

Supersedes the 2026-09-06 00:40 PAUSED.md. The resume block at the bottom is **unchanged**,
but read the MUST-FIX and the launcher corrections above it first.

---

## 1. What ran tonight (2026-09-07 00:42 → 08:00)

The night was a **live test of T5″ at emission**. The box was already carrying 8 other
campaigns, so the A123 brief's full block (6 shards + 2 deepens + the A96 drivers, ~17 more
python processes) did not fit the ≤ 16-process cap; the run was re-scoped to a mild
oversubscription (~24) agreed with the coordinator.

| ran | detail |
|---|---|
| `tree57` k5_11 s0 | pid 6104, 00:44 → 07:58, exited on sentinel |
| `tree57` k5_11 s1 | pid 34492, 00:44 → 07:58, exited on sentinel |
| `tree57` k5_16 s1 | pid 43216, 00:52 → 08:00, exited on sentinel |
| `tree57` k5_16 s0 | pid 54148 → 9596, **stopped 04:01, wedged — see §5** |
| `recheck96 --trimmed` | pid 46496, one process, BelowNormal, `--cap 900` |

**Deliberately NOT run** (and still not run): both `deepen.py` producers, `select96.py`, the
A96 drivers (`param96`, `resolve96`, `neighbours96`), and `scaleup.ps1`. Levers verified in the
deployed modules at launch: `trim57.TRIM = True`, `pinguard.TIGHT_CORE = True`,
`shadow_sched.ENABLED = False`. Region-tree/A116 option not touched. Sides G4/G3/G2 stay frozen.

Because no A96 driver ran, **the class window fractions are unchanged** from the 2026-09-06
pause (k5_11_G1 0.978027, k5_16_G1 0.991211). They are an A96 parametric quantity; nothing
tonight could move them.

## 2. Row counts: v1 pause → now

| file | 2026-09-06 | now | new |
|---|---|---|---|
| `tree_k5_11_interior_G1_s0` | 18 | **123** | +105 |
| `tree_k5_11_interior_G1_s1` | 207 | **276** | +69 |
| `tree_k5_16_interior_G1_s0` | 161 | **170** | +9 |
| `tree_k5_16_interior_G1_s1` | 192 | **305** | +113 |
| `recheck96.jsonl` (A96) | — | **23** | +23 |

**296 new level-1 children.** All other A57/A96 result files are untouched.

Tree scoreboard now (`code\board.py`):

| class | seen | killed (cert / logic) | alive_lp | cert_fail | open |
|---|---|---|---|---|---|
| `k5_11_interior_G1` | 801 | 615 (362 / 253) | 139 | 47 | 186 |
| `k5_16_interior_G1` | 920 | 671 (471 / 200) | 212 | 37 | 249 |

## 3. Kill table — 296 new children, by leaf

| leaf | count | share |
|---|---|---|
| PASS (certified kill) | 149 | 50.3 % |
| T5′ / logic kill (`pin=contradictory`) | 90 | 30.4 % |
| ALIVE-at-LP → queued for depth 2 | 45 | 15.2 % |
| FAIL → resolver | 9 | 3.0 % |
| **T5″ full kill** (`pin_info=="trim"`) | **3** | **1.0 %** |
| **T5″ trimmed bin** (survives, narrowed) | **16** | **5.4 %** |
| parent-box (unsound at reduced budget) | 0 | — |

Per shard: 11s0 105 new (3 T5″-full, 3 T5″-trim, 39 logic, 48 PASS, 5 FAIL, 10 ALIVE);
11s1 69 (5 T5″-trim, 23 logic, 34 PASS, 2 FAIL, 10 ALIVE); 16s0 9 (2 logic, 6 PASS, 1 ALIVE);
16s1 113 (1 T5″-split, 8 T5″-trim, 26 logic, 61 PASS, 2 FAIL, 24 ALIVE).

**Soundness checks clean.** Max core half-side over all 296 rows = **0.398** (red flag at
≥ 1/2); theta stayed strictly inside **[0, 90]**; no certificate verdict disagreed with a
stored one. No Traceback, MemoryError or OpenBLAS allocation failure in any shard log.

## 4. T5″ live fire rate vs the offline projection

**Live: 19 of 296 emitted children = 6.42 %** (3 full kills + 16 trimmed bins, one of which
split into two pieces, `k5_16_interior_Y0652a`).

The offline control (v1) reported *159 boxes gain an empty surviving bin, 89 incremental over
T5′*, against the 2403-row corpus — i.e. a projected **6.62 % touched / 3.70 % incremental**.

| quantity | offline projection | live tonight |
|---|---|---|
| boxes touched by trimming | 6.62 % (159/2403) | **6.42 %** (19/296) |
| bins fully emptied | — | **1.01 %** (3/296) |
| incremental over T5′ | 3.70 % (89/2403) | see caveat |

So the **touch rate matches the projection closely (6.42 % vs 6.62 %)**, but the rate at which
trimming *fully empties* a bin is only 1.01 %; with 3 events the 95 % interval is roughly
[0.2 %, 2.9 %], which sits below the 3.70 % incremental figure. Two honest caveats: the
denominators are not the same population (the offline control swept the whole 2403-row corpus
including D2/D3/D4 levels; tonight's 296 are level-1 children from three shards), and 3 events
is a small sample. **Do not treat the 1.01 % as refuting the projection** — it is a first live
data point that suggests the "empty surviving bin" count may have been counting boxes *touched*
rather than *emptied*. Resolving this needs the v1 control re-run with the two categories
reported separately.

Shape of the effect, which is the more useful finding: **15 of the 16 trimmed bins still came
out ALIVE-at-LP** (only `k5_16_interior_Y0634` reached PASS), and most trims bite at the tilt
extremes — 12 of 16 are anchored at theta 0 or 90 (e.g. `[0, 0.8906]`, `[0, 3.5068]`,
`[86.5137, 90]`). **T5″ is mostly buying LP tractability on hard nodes, not kills.** That is
consistent with the re-check result below, where narrowed bins convert to kills once given time.

LP and certify wall times tonight are **CONTENDED** (the box ran 8 other campaigns at ~70–100 %
CPU) and must **not** be compared with the offline figures. The fire rate above is geometry —
computed in `build_children` before any LP — so contention does not affect it.

## 5. Incidents

**(a) `k5_16` s0 wedged deterministically on `k5_16_interior_Y0381` — shard stopped 04:01.**
At 00:52:53 the node's LP hit its cap and the driver then span at 100 % CPU on a **single
thread**, no children, no log output, for 2 h 08 m. In this shard's history **101 of 102
"time limit" events are followed by a `DONE` line within 758 s**; this one never emitted it.
Relaunched through `launch.ps1` at 03:02 (pid 9596); it re-picked `Y0381` and **reproduced the
hang exactly** — same iteration trace (t≈46 s, 59 s, then the 240 s cap) then silence for 55 min.
Since the shard re-picks `Y0381` on every restart it can never advance, so it was stopped at
04:01 rather than hold a core for four hours. **`Y0381` is a reproducible hang in the
post-time-limit path and needs a debugger before this shard is resumed.** Its pidfile was left
in place (never deleted) and is stale at 9596. Nothing was lost: the node had no recorded result
either way, and the shard's other 170 rows are intact.

**(b) `arms96.py --arm C` was NOT a stray, and was left alone.** It was reported as finished
and shelved, but at 00:33 its log had **31 of 32 rows and no `arm C done` marker**, and the
A96 three-arm report (`37eae961`) covers only **n=26** — five nodes, including the report's own
open caveat `Y1135` ("not yet reached in C"), had landed after it was written. It finished on
its own at **00:44:42 with 32/32 and the done marker**. On the complete arm: C's strict kills
(eta < −0.005·tau) are exactly {`Y1002`, `Y0817`, `Y1099`} and **B kills all three**; the final
node `Y0183` came back C eta = −9.3e-14 (knife) vs B eta = −0.026 (kill). **Zero C-only kills
across all 32 nodes** — the `notes/verifier_v2_rowfilter.md` gate is not met on complete data,
strengthening the n=26 conclusion. Verifier-v2 stays shelved.

**(c) Orphans / timeouts.** The reaper (`pausegate.py --reap`) ran at launch and hourly, eight
times: **no orphaned certify children at any point**. No verify timeouts (no `param96` ran).
Free physical never dropped below **10.4 GB** (gate is 3 GB); the box ran 14–24 python processes.

**(d) Nothing lost.** The sentinel path worked as designed — all three surviving shards
recorded their in-flight node and exited cleanly. The only unrecorded work is `Y0381`'s
(never completable) and whatever node `recheck96` was on at 08:00.

**(e) `Y0381` DIAGNOSED (A124, 2026-09-07) — it is inside HiGHS, and it is not a T5″ artefact.**
Reproduced exactly on a copy (`attempts/A124-recheck-day/code/repro_y0381.py`; same 3,827-atom
folded pool, same `init orbits=3827 rows=16602` line, same iteration trace; nothing written into
A57). All 11 `faulthandler` dumps, including the one at the 600 s wall, give one stack:
`lpbox.py:417 self.h.run()` ← `lpbox.py:846 M.solve()` ← `caselp.py:337 solve_node`. A single
`h.run()` ran 380 s and never returned, and never printed the non-optimal-status diagnostic — so
it is not column generation, not the certifier, not `pinguard`. **Cause:** `LPModel.__init__`
sets `output_flag=False` and `threads=1` and **never sets `time_limit`** (`grep setOptionValue
lpbox.py` returns only those two plus `simplex_strategy`), while `solve_node`'s `time_limit` is
checked only *between* iterations at `:906` — hence one thread at 100 %, zero output, no bound.
The 00:48 run died in the final unconditioned solve at `:908`, the 03:02 run in the in-loop solve
at `:846`; same call, so the post-time-limit path is not special. **Not T5″-introduced:** the bin
width 10.880664 is a canonical cover width and `pin="ok"`, so trimming examined this bin and
removed nothing — the hang is pre-existing. Full diagnosis, the one-line guard and its soundness
caveat, and the recommended per-node process wall:
`attempts/A124-recheck-day/notes/y0381_hang.md`.

**(f) The re-check's "kills" are LP verdicts, not certificates (A131 + A124, 2026-09-07).**
`recheck96.py:116` sets `kills = (tau < budget)` and never calls `certify.py`, and it runs
`solve_node(out=None)` so the node json a certificate would need is not even written. Worse,
graded by the campaign's own strict rule (`eta < −0.005·tau`, PAUSED.md §5b), **§9's "11
certified kills from 23 nodes" is 1 strict kill, 2 weak and 8 knife edges** at |eta| ≤ 1e-9.
A124's own day of re-checking produced 2 strict kills from 43 nodes and ~15 CPU-h, and both
(`Y1002`, `Y1099`) were already in arm C's strict-kill set in §5b. **Read §9 accordingly**, and
see `attempts/A124-recheck-day/notes/recheck_kills.md`. The day's real yield was geometric: 54
zero-cost T5″ full kills banked out of the ALIVE queue, and a scan showing **55 of the 193 FAIL
rows (28.5 %) are dead by the deployed trim** — see `notes/trim_empty_alive.md`.

## 6. MUST-FIX before the next resume — T5″ exclusions are not persisted

`trim_excluded` and `trim_from` are constructed in `tree57.build_children` (lines 177, 184–185)
and **never written to disk**. They are not copied into `rec` (built at :470–472) and appear in
no `.jsonl`, node `.json`, `.report.json` or `.certify.json`. Verified by grep and by inspecting
tonight's emitted rows.

Consequences, in order of importance:

1. **The witness ledger for each excluded tilt interval does not reach disk.** v1 states the
   interval "is carried on the child record ... so the ledger supersedes rather than
   overwrites". That is not what the deployed code does. The node's coverage claim
   (original bin = trimmed child(ren) ∪ excluded intervals) is therefore **not auditable from
   the results**; it is only reconstructible because cover construction is deterministic.
2. **The commonest T5″ outcome is invisible.** A single-piece trim keeps the plain id and
   `pin="ok"`, so it leaves *no marker at all* in any persisted field. Only full kills
   (`pin_info=="trim"`) and multi-piece splits (`…a/…b` ids) are visible. Tonight's 16 trimmed
   bins had to be recovered **geometrically**, by flagging rows whose theta width is not one of
   the eight canonical cover widths (7.628150, 8.632055, 9.729029, 10.880664, 12.018012,
   13.039604, 13.822454, 14.250033). That is how the 6.42 % above was measured.
3. For a partial trim the original bin extent is unrecorded, so how much was removed cannot be
   read back.

**This is not a soundness error** — a trimmed child is a sub-box, its certificate is the
ordinary one, the frozen verifier chain is untouched, and the v1 control was 618/618 with zero
lost. It is an auditability gap. **Fix before the next resume:** persist `trim_excluded` (with
its witness pin) and `trim_from` on the emitted record. Until then, count T5″ full kills by
`pin_info == "trim"`, splits by the `a/b` suffix, and single-piece trims by the theta-width
test above (`scratchpad/a123_killtable2.ps1` implements it; note that the canonical width set
must be built **globally** across all shard files — building it per-file mis-flags ordinary
bands in a file with few prior rows).

## 7. Launcher corrections (inherited errors — do not repeat them)

* **`launch.ps1` has no pidfile gate.** It calls `Start-Process` unconditionally and *then*
  writes the pidfile (:56–59). Calling it twice for the same shard **double-launches**. The
  gate described in v1 lives in `scaleup.ps1` (which skips shards whose pidfile *exists*).
  Launch each shard **exactly once** and verify the pidfile changed and the pid is alive.
* **Every A57 pidfile is stale** (all 21 pointed at dead pids at 00:33, and s0/s1 do again now).
  `launch.ps1` overwrites them, so they do not block a launch — but never delete one, and never
  trust one as evidence a shard is running. Check the pid.
* **`pausegate.py` lives only at `attempts/A57-shadow-trees/code/pausegate.py`**, not under A96
  as the A123 brief's path list implies. It watches both bases, so A57's `PAUSE` also stops the
  A96 drivers (this is how `recheck96` was stopped tonight).
* **A process-name scan matches the checking shell itself.** Match on the *script* in the
  command line, as `run96.ps1` :22 does, or on pids.

## 7a. Running ONE driver under this pause — the scoped-sentinel mechanism (A124, 2026-09-07)

`pausegate.paused()` with no argument checks **both** bases (§7), so A123's `PAUSE` here stops
far more than the A57 shards: it also stopped `recheck96` and A120's runner
(`attempts/A120-no-side-runner`), neither of which is a shard and both of which are the highest
value-per-CPU-hour items on the board. Deleting this file to free them would simultaneously
un-gate six `tree57` shards and two `deepen` producers, and `launch.ps1` has no pidfile gate
(§7), so that is the wrong lever.

**The mechanism to use — scoped sentinel, no edit to `pausegate.py`, no deletion of this file.**
`pausegate.paused(base=...)` already takes a base; a driver that passes **its own attempt
directory** watches only its own sentinel and ignores this one, while every driver that calls the
bare `paused()` — which is all six shards and both deepens — stays paused. So the change is one
line at the *consumer's* call site, inside the consumer's own attempt, and nothing shared moves:

```python
from pausegate import paused, reason
OWN = os.path.dirname(os.path.abspath(__file__ + "/.."))   # this attempt's base
if paused(base=OWN): break                                 # NOT paused() -- that reads A57's
```

A124 used exactly this shape for its re-check driver
(`attempts/A124-recheck-day/code/recheck124.py`, which watches
`attempts/A124-recheck-day/PAUSE`) and left `attempts/A57-shadow-trees/PAUSE` untouched;
`recheck96.py` itself was not modified. **A120 can resume the same way**: give `run_no.py` /
`no_runner.py` the `base=` argument and create `attempts/A120-no-side-runner/PAUSE` as its own
stop button. Do not add an env-var override to `pausegate.py`: a global escape hatch would also
un-gate the shards, which is the thing this pause exists to prevent. Note the corollary — while
scoped drivers run, **"the A57 PAUSE is set" no longer implies "nothing is running"**; check pids.

## 8. Resume commands — UNCHANGED

Set `PYTHONDONTWRITEBYTECODE=1` in the shell first (the launchers `launch.ps1`, `scaleup.ps1`
and `run96.ps1` already set it for their children). Run from `attempts/A57-shadow-trees`. **The tight core (T5′) and tilt trimming (T5″) are both on
by default** — `pinguard.TIGHT_CORE = True`, `trim57.TRIM = True`; nothing needs setting, and
setting either to `False` is the only way to turn it off. Before resuming, clear any sentinel
(`del PAUSE`) and optionally run `python code\pausegate.py --reap --dry-run`.

> **Before using this block:** apply the §6 MUST-FIX, and do not resume `k5_16` shard 0 until
> `k5_16_interior_Y0381` (§5a) is debugged — it will wedge again on the first node it picks.
> Count the whole box against the process cap first; on 2026-09-07 the other campaigns alone
> already filled it.

Six shards, same assignments, through `launch.ps1` so the pidfile gate holds and nothing is
duplicated:

```
powershell -File code\launch.ps1 -Name k5_16 -Shard 0/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_11 -Shard 3/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_11 -Shard 4/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_16 -Shard 4/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_11 -Shard 5/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_16 -Shard 5/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
```

Level-2 producers (one per class):

```
python -u code\deepen.py --key k5_11_interior_G1 --levels 3 --time_limit 240 --cert_time 240 --pin_delta 0.01 --jobs 1
python -u code\deepen.py --key k5_16_interior_G1 --levels 3 --time_limit 240 --cert_time 240 --pin_delta 0.01 --jobs 1
```

A96 workers, from `attempts/A96-a57-parametric` (re-run `code\select96.py` first — the corpus
grew while the shards ran and the drivers load the selection once at startup):

```
python code\select96.py
powershell -ExecutionPolicy Bypass -File code\run96.ps1 -Procs 3 -NodeCap 1500
python -u code\param96.py --groups level2 --tag G1 --out results\param96_level2.jsonl --procs 1 --node-cap 1500 --node-cap-high 3000 --atoms-high 32 --min-free-phys-mb 3072
python -u code\resolve96.py --cap 180
python -u code\neighbours96.py --interval 30 --minutes 240
```

The scaler, **only if six shards are wanted again** (cap 10 = 6 tree shards + certify children +
watcher + deepen; it rebuilds its queue skipping shards whose pidfile exists, so it will not
duplicate the hand-launched six):

```
Start-Process powershell -ArgumentList '-NonInteractive','-ExecutionPolicy','Bypass','-File','code\scaleup.ps1' -WorkingDirectory <A57 base> -RedirectStandardOutput logs\scaleup.out -RedirectStandardError logs\scaleup.err -WindowStyle Hidden
```

Optional levers, only if wanted (both default to off / not-run):

```
# shadow-slack scheduling: edit code\shadow_sched.py, ENABLED = True (inspect first)
python code\shadow_sched.py

# ALIVE re-check at a 900 s cap, from attempts\A96-a57-parametric (add --trimmed to combine
# the longer cap with the T5'' trimmed bin)
python -u code\recheck96.py --cap 900
```

**T5‴ pin-clip backlog, waiting to be folded in at resume (A131, 2026-09-07):** 132 recorded-open nodes (74 ALIVE + 58 FAIL; 63/57/6/6 by level; 93 k5_11 / 39 k5_16) are dead by pin-clip geometry alone — 112 by the already-deployed T5″ and 20 that need the two-pin joint clip — with one `pin-clip-kill-certificate-v1` each under `attempts/A131-pin-clip/certs/backlog/`, all 132 re-verified by an independent checker and sample-confirmed (1 584 000 drawn → tested → 0 hits, ≥ 12 000 per node); A131 wrote NOTHING into A57/A96 state, so the ledger rows in `attempts/A131-pin-clip/results/backlog_kills.jsonl` (clip-only subset: `backlog_clip_only.jsonl`) must be folded in by this campaign's owner, keeping the prior verdict as `superseded_by_tight_core.jsonl` does.

Sides G4/G3/G2 stay frozen (`code\FREEZE_TAGS.txt`); nothing about the pause changes that.

## 9. The re-check is the night's best result — run it first next time

`recheck96 --trimmed` re-solved **23** of the 383 queued ALIVE nodes at a 900 s cap on the
T5″-trimmed bin and **certified 11 kills — a 47.8 % conversion of nodes previously recorded as
ALIVE**, at a mean 1140 s per node (6 of 23 converged, 7.28 CPU-hours total).

| node | eta before → after | trimmed bin | wall |
|---|---|---|---|
| `k5_11_interior_Y0041` | 1.20e-12 → −1.42e-14 | [85.2324, 90] | 933 s |
| `k5_11_interior_Y0054` | −5.68e-14 → −0.02817 | [82.3719, 90] | 1433 s |
| `k5_11_interior_Y0072` | 0.11268 → −2.74e-12 | [86.5137, 90] | 1557 s |
| `k5_11_interior_Y0108` | −8.88e-16 → −1.79e-13 | [86.5137, 90] | 1032 s |
| `k5_11_interior_Y0144` | 7.26e-13 → −1.15e-14 | [82.3719, 90] | 1215 s |
| `k5_11_interior_Y0402` | −4.25e-13 → −1.37e-09 | [0, 3.5068] | 1001 s |
| `k5_11_interior_Y0414` | −5.91e-13 → −4.30e-13 | [64.0108, 73.7398] | 1215 s |
| `k5_11_interior_Y0486` | 0.0 → −1.12e-09 | [64.0108, 73.7398] | 1193 s |
| `k5_11_interior_Y0546` | −5.42e-14 → −1.02e-10 | [35.8657, 41.1121] | 2179 s |
| `k5_11_interior_Y0588` | 1.18e-12 → −1.07e-12 | [64.0108, 73.7398] | 356 s |
| `k5_11_interior_Y0636` | 2.87e-12 → −6.07e-10 | [0, 14.25] | 2263 s |

This is the combination v1 called "worth pricing", and it priced well: **11 kills from 23 nodes
and 7.28 CPU-hours**, against 149 certified kills from 296 fresh emissions across three shards
over the same window. 360 of the 383 queued ALIVE nodes remain un-rechecked. On a box with
limited process budget, **spend it here before opening new shards.**
