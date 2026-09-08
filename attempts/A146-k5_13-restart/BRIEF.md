# A146 — restart k5_13, the last OPEN window row (Opus engineer, ≤ 2 BLAS-pinned BelowNormal processes, ≤ 6 CPU-h)

## Context (restated from the coordinator, 2026-09-07)

A61's whole-window straggler campaign (`attempts/A61-window-stragglers/`) left exactly one row
OPEN in the shared scoreboard `attempts/A56-sparametric/results/scoreboard.json`: **k5_13**
(51/52 full window; summary `by_result` = M1 4, TRANSFERRED 27, TRANSFERRED-resolved 20, OPEN 1).

The k5_13 run
(`logs/resolve61_k5_13.log`, `logs/campaign_k5_13.out`; command line
`resolve61.py --name k5_13 --eps_geo 0.003 --gate 0.3 --lp_time 1200 --lp_time_b 900
--cert_time 420.0 --cert_rounds 6 --depth 48 --jobs 3 --param_timeout 900 --max_atoms 3500
--max_cols_add 800`, launched by `campaign61.py --heavy 2 --jobs 3 ...`)
**hung inside an LP at stage-A iteration 7 on 2026-09-06 05:54** and spun on one thread for
~40 CPU-h with no output; the coordinator killed it at 22:05 on 2026-09-07 and the `campaign61`
parent exited with it.

**Root cause (A124, `attempts/A124-recheck-day/notes/y0381_hang.md`)**: `LPModel.__init__` in
`lpbox.py` sets only `output_flag=False` and `threads=1` — **no HiGHS `time_limit` option is ever
set**, so `h.run()` can spin forever, while `solve_node`'s own `time_limit` is checked only
*between* iterations. One thread at 100 %, not a byte of output, no wall.

## Task

1. Read A61's driver / campaign / k5_13 state; establish what was banked.
2. Restart k5_13 **exactly where it left off** (its resumable state) through a **wrapper that
   enforces a hard per-LP-call process wall of 1,500 s** — on trip, kill and record **CAP, never a
   verdict**, then continue with the next step per the driver's own logic.
   **Do NOT edit `lpbox.py`, `resolve61.py` or `campaign61.py`** — a wrapper / subprocess
   supervisor is the tool. 2 BLAS-pinned BelowNormal processes. Honour the two-stage protocol
   (240 s LP, then certify on η ≤ −1e−3; 900 s only at a knife edge) where the driver exposes
   those knobs.
3. **Cap 6 CPU-h.** If k5_13 does not close, report exactly what remains — window fraction
   banked, the failing slabs, and whether **A114's slab-width law** (`docs/budget.md` § E) sizes
   them — rather than spending more.
4. On closure, update the scoreboard's k5_13 entry **the way A114 did** (its
   `code/update_scoreboard114.py`, which folds A61's `resolve61_*.json` records verbatim through
   `fold_a61`, one atomic tmp+`os.replace` write, backup kept) so the scoreboard reads **52/52**;
   then `docs/budget.md`'s stragglers row, `docs/residue_ledger.md` § 2, the registry row,
   `LOG.md`.

**Constraints.** Read-only on every other campaign (A136/A141/A144/A145 are running). A61's own
state files may be appended/updated **only through its driver**. No recursive deletes; never
delete a pidfile. `PYTHONDONTWRITEBYTECODE=1`. ≤ 16 python processes on the box.
git = fetch + plain merge + push own paths and A61's/A56's updated state with explicit pathspecs.
Report ONCE at closure or the cap.

## What "exactly where it left off" means here (established by reading the driver)

`resolve61.py` has **no stage-resume of its own**; its resume mechanism is the **column pool**.
`enriched_warm()` globs `attempts/{A56,A61}/results/nodes/<name>*.json` and folds every checkpoint
this lab ever wrote for the node — which is precisely why A61 exists ("A56's own aborted runs left
4.9k–7.8k generated orbits sitting in checkpoints that were never folded back"). The hung run left

    attempts/A61-window-stragglers/results/nodes/k5_13_A_state.json   1,405,279 B, 2026-09-06 05:54

written by `solve_node(checkpoint=...)` at stage-A iteration 6 (4,332 orbits / 18,326 rows). A
relaunch therefore starts from a **strictly better pool than the hung run did** — that *is* the
resumable state. Nothing else was banked for k5_13: no `certs/k5_13.json`, no
`results/nodes/k5_13.json`, no `stageA.json`, and `results/resolve61_k5_13.json` holds only the
warm-start header (no `stageA`, no verdict), so the campaign progress file has no k5_13 row.

## Plan

**Track 1 (primary) — `code/supervise146.py`.** Launch the unmodified `resolve61.py` as a child
(BelowNormal, BLAS pinned, `PYTHONDONTWRITEBYTECODE=1`), stream its stdout, and run a watchdog:

* the driver prints one line per LP iteration, and it runs `certify.py` / `verify_param.py` as
  **child processes**; so the discriminator for "we are inside `h.run()`" is
  **(no stdout for W seconds) AND (the driver has no live descendant process)**;
* W = 1,500 s. On trip: `taskkill /T /F` the tree, record `{"event": "CAP", ...}` in
  `results/supervisor.json` — **a CAP is never a verdict** — and relaunch, which re-folds the
  checkpoint the killed LP had already written.

Two-stage protocol via the driver's own knobs: `--lp_time 240 --lp_time_b 240`, escalating to 900
only if a stage lands on a knife edge (|η| small against the relevant gate). η = τ − budget;
stage A's gate is η ≤ −0.3, stage B's post-shrink gate is η ≤ −0.03.

**Track 2 (hedge, the second process) — `code/slab146.py`.** Task item 3 asks whether A114's
slab-width law sizes k5_13's failing slabs; answering it needs a *passing* probe slab, and the
probe is cheap and uses **no LP at all**. Run the frozen A56 `verify_param.py` on the **existing**
A56 parametric certificate `attempts/A56-sparametric/certs/k5_13.param.json` (margin 0.037449,
106 atoms) on a narrow slab at the bottom of the window; if it passes, `w_min = width / 2^(max
s-depth)`, `d_pose = max depth − max s-depth`, `width_max = w_min · 2^(48 − d_pose)`, and the
window is swept in slabs of that width — A114's mechanism, sound as the A86 T4 WindowRows
disjunction. Slab endpoints are kept on the verifier's integer grid (denominator `2^a·5^b`,
`b ≤ 6`; multiples of 1/250000 are safe).

Everything is written under `attempts/A146-k5_13-restart/` except A61's own state (written only by
its driver) and the one atomic scoreboard write on closure.
