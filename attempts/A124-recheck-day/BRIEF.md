# A124 — day shift: the alive re-check at low priority, the T5″ touched-vs-emptied control, and the Y0381 hang (Opus)

Context (2026-09-07 08:15). A123's night shift (attempts/A57-shadow-trees/PAUSED.md v2, commit `ad55f884`) ran three
A57 shards plus `recheck96 --trimmed` for seven hours and paused cleanly. Its two results decide today's work:
1. **The re-check outperformed the shards per unit of budget**: 11 certified kills from 23 previously-ALIVE nodes
   (47.8%) in 7.28 CPU-h, against 149 certified kills from 296 fresh emissions across three shards in the same window;
   360 of the 383 queued ALIVE nodes remain. On a contended box, spend there before opening shards.
2. **T5″ at emission touched 6.42% of children (19/296; offline 6.62%) but fully emptied only 1.01% (3/296)** against
   the offline "89 incremental" projection (3.70%); 15 of the 16 trimmed bins still came out ALIVE-at-LP, and 12 of
   16 trims bite at the tilt extremes. Likely reading: the offline count of 159 "empty surviving bins" mixed boxes
   TOUCHED with boxes EMPTIED. T5″ buys LP tractability, not kills — the schedule figure (10–11 wall-days) rests on the
   89 and must be re-derived.
Also: `k5_16` shard s0 hangs deterministically on node `k5_16_interior_Y0381` (single-thread 100% spin, no output for
2 h after the LP cap, reproduced on relaunch); trim_excluded/trim_from are never persisted (MUST-FIX before a full
resume; documented in PAUSED.md v2). The PI is up from ~08:30 and may use the machine: today's compute is LOW
priority and ≤ 2 processes; nothing else of A57 is launched.

Read first: PAUSED.md v2 (all), attempts/A57-shadow-trees/notes/lemmas.md (T5′/T5″, the survivor-count and
emission-nondeterminism notes), attempts/A96-a57-parametric/code/{recheck96,trim57,pausegate}.py, results/recheck96.jsonl
(the night's 23 records), attempts/A96-a57-parametric/notes/ (the trimming measurement `155a3c5b`/`e68d8dbc`: how the
159/70/89 were counted), attempts/A57-shadow-trees/code/{tree57,pinguard}.py, docs/budget.md §A–B.

## T1 — the re-check, all day, low priority
Delete the PAUSE sentinel ONLY for recheck96 (do not launch shards; if recheck96 honours the sentinel, run it with an
explicit override flag or a separate sentinel name — read the code); run `recheck96 --trimmed` at TWO processes at
BelowNormal priority over the 360 remaining ALIVE nodes in the queue's order, cap 20 CPU-h, resumable; a hard per-node
wall of 1,500 s (CAP is never a verdict); orphan reaper hourly; stop if free physical < 3 GB or the PI's foreground
load makes the box sluggish (check load hourly; if the PI is using the machine heavily, drop to one process). Report
certified kills, converged/knife/alive counts, CPU-h, and the kill rate by level.

## T2 — the touched-vs-emptied control (offline, minutes)
Re-run A96's offline trimming control over the same 2,222-box corpus with the two categories separated: boxes whose
surviving bin is EMPTY (a full T5″ kill) vs boxes merely TRIMMED (bin narrowed, node survives). Report the two counts
by level, the incremental full kills after T5′ (the honest "89"), and the corrected effect on the schedule: re-derive
the 13.3 → x wall-days figure with only full kills counted (trimmed-but-alive nodes cost the same LP as before). Compare
with the live 3/296 and 16/296.

## T3 — the Y0381 hang (diagnosis only, no fix in the frozen driver)
Reproduce the hang on a copy: run tree57's node path for `k5_16_interior_Y0381` alone with faulthandler/tracebacks
enabled and a 600 s wall, and report where it spins (solve_node column generation? the certifier? a pinguard loop
on a degenerate bin?) with the stack; say whether it is a T5″-introduced case (a bin trimmed to a degenerate width) or
pre-existing. Recommend the one-line guard for the resume block; do not edit tree57.py.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal, commit gate 6144 MB and > 3 GB free physical; READ-ONLY on
every other attempt and on A57's drivers (no shard launches; A120/A115 continuations are running at ≤ 2 each — count
them); frozen verifiers byte-identical; NO recursive deletes, never delete a pidfile, PYTHONDONTWRITEBYTECODE=1; git =
fetch + plain merge + push own paths (no rebase/autostash/reset). Writes: attempts/A124-recheck-day/{code,results,
notes,logs}, the recheck96 results file (append), registry row, LOG.md, a note in PAUSED.md v2's incident list for
the hang diagnosis. Report ONCE at the cap or by 18:00 local, whichever first: T2's corrected schedule first, T1's
kill table second, T3's stack third, pointers last. No interim messages.
