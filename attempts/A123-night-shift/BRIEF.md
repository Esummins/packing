# A123 — night shift: resume A57 with the new leaves for ~8 hours, then pause cleanly (Opus, campaign owner for one night)

Context (2026-09-07 00:30). The PI has given the machine to the lab until ~08:30 local time (no games, no interactive
use). A57 (the k5_11/k5_16 window trees) has been paused since 2026-09-06 00:45 with every lever prepared but never
run live: the tight core T5′ and tilt trimming T5″ at emission (on by default at resume), the PAUSE sentinel and orphan
reaper (`pausegate.py`), the 900 s alive re-check (`recheck96.py`, resumable), the shadow-slack scheduler and the
region-tree/A116 option (both OFF — leave them off). A96, the previous owner, is out of working room; you are the
owner for tonight. Everything you need is in `attempts/A57-shadow-trees/PAUSED.md` (the copy-paste resume block, the
lever table, the state counts at the pause), `attempts/A57-shadow-trees/notes/lemmas.md` (T5′, T5″, the emission-
nondeterminism note, the survivor-count rule), `attempts/A96-a57-parametric/code/{regionopt96,shadow_sched,recheck96,
pausegate,trim57}.py`, `attempts/A57-shadow-trees/code/{launch.ps1,scaleup.ps1,tree57.py,deepen.py,pinguard.py}`,
docs/budget.md §B (node anatomy) and the standing ops laws in the lab memory summarised here: at most ~2 processes per
chore, BLAS pinned (OMP/MKL/OPENBLAS = 1), 6144 MB commit gate and > 3 GB free physical before every LP, never touch
other campaigns' state (A61's k5_13 campaign, A114, A115, A119, A120, A121, A122 are running at ≤ 2 processes each —
count them), frozen verifiers byte-identical, no recursive deletes, PYTHONDONTWRITEBYTECODE=1, git = fetch + plain
merge + push own paths (no rebase/autostash/reset). Emission is nondeterministic (certify re-solves under a time
limit): reproduce kills by replaying certificates, never by re-emitting.

## T1 — resume (00:45 → 01:00)
1. Read PAUSED.md end to end. Confirm T5′/T5″ are on by default (`trim57.TRIM`, `pinguard` tight core), shadow
   scheduling and the region-tree option are OFF, `select96.py` must be re-run before the A96 drivers (the corpus grew).
2. Count the box: python processes by owner; free physical and commit. Plan the worker count so the TOTAL stays ≤ 16
   python processes and free physical stays > 3 GB with the six shards + two deepens + the A96 drivers (verify_param
   children count). If the box is tight, run five shards instead of six.
3. Resume exactly with the copy-paste block: shards through `launch.ps1` (pidfile gate; verify each pidfile changed —
   never delete one), both deepens, `select96.py` then the A96 drivers, the scaler only if six shards are wanted. Run
   `pausegate.py --reap` once after launch and hourly.
4. Start `recheck96.py --trimmed` at ONE process over the ALIVE population (resumable), lowest priority.
5. Verify within 30 min that new children carry `trim_excluded` records and T5″ fires appear in the jsonl (the deployed
   module is the one running: `PYTHONDONTWRITEBYTECODE=1` set by the launchers).

## T2 — supervise (01:00 → 08:00)
Hourly, from the logs only (no polling loops that wake the coordinator): rows emitted per level, kills by leaf
(T5, T5′, T5″, PASS, FAIL→resolver, ALIVE), verify timeouts, orphans reaped, free physical, any Traceback/MemoryError.
If a worker dies, relaunch it through `launch.ps1` (never a bare python call). If free physical drops below 3 GB for
two checks, stop one shard through the sentinel-aware path (PAUSE, wait for its in-flight node, restart the others).
Do not change any lever mid-run; the night is a live test of T5″ at emission, so keep the configuration constant.

## T3 — pause and report (08:00 → 08:30)
At 08:00 create the PAUSE sentinel with a reason; wait for every driver to record its in-flight node and exit
(pausegate checks between nodes); reap orphans; confirm zero tree57/deepen/param96/resolve96/verify_param/certify
processes; write `attempts/A57-shadow-trees/PAUSED.md` v2 (timestamp, state counts vs the 2026-09-06 pause, the
night's rows and kills by level and leaf, T5″'s measured live fire rate vs the offline 89-box projection, the
re-check's certified kills, verify timeouts, orphans, anything lost) and the resume block unchanged. Commit and push
own paths; registry row; LOG.md line. Report ONCE at the pause: the night's kill table first (by level and leaf, live
vs projected), the scoreboard delta and the re-check yield second, incidents third, pointers last. No interim messages.

Hard rules: never launch anything after 08:15; if anything looks unsound (a core half-side ≥ 1/2, a bin outside
[0, 90], a certificate verdict disagreeing with a stored one on replay), PAUSE immediately and report that first.
