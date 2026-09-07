# T3 — `k5_16_interior_Y0381`: where the shard spins, and why

`code/repro_y0381.py`, 2026-09-07. Read-only on A57 (`tree57` and `lpbox` imported, not edited,
not copied-with-edits); `solve_node` runs with `out=None`, so no node json, no certificate and no
`.jsonl` row was written anywhere in A57. Stacks: `logs/y0381_stacks.txt`; console:
`logs/repro_y0381.out`.

## The node, and that it is NOT a T5″ artefact

    k5_16_interior_Y0381   YES   budget 5   a = 0.356601629768687
    centre box  x [1.659028, 1.798785]   y [1.100000, 1.239757]
    tilt bin    [53.13010235415598, 64.01076641616699]   width 10.880664
    pinguard: pin = "ok", pin_info = None

**The tilt width 10.880664 is one of the eight canonical cover widths** (7.628150, 8.632055,
9.729029, **10.880664**, 12.018012, 13.039604, 13.822454, 14.250033), so by the width test of
PAUSED.md §6 this bin was never trimmed: T5″ examined it and removed nothing. The hang is
**pre-existing**, not a degenerate bin manufactured by trimming, and it is not a `pinguard` loop
either — `classify` returns before any LP.

The reproduction is exact rather than approximate: `build_children` puts the node on shard 0/6 as
it did in production, `merged_warm` returns the same 3,486 atoms / 30,000 rows from the same four
files, the sibling fold gives **3,827 atoms — the number the wedged shard logged twice** — and the
LP opens with `init orbits=3827 points=3827 rows=16602 (rejected 12951)`, character for character
the shard's line.

## Where it spins

Iteration trace (repro, uncontended box) against the shard's two wedged runs:

| it | repro | shard 00:48 | shard 03:02 |
|---|---|---|---|
| 0 | t = 44 s, +1102 rows | 50 s | 46 s |
| 1 | t = 55 s, +400 cols | 65 s | 59 s |
| 2 | t = 217 s, +946 rows, **lp 126 s** | 261 s (lp 150 s) → `time limit` | 240 s (lp 137 s) |
| 3 | **never returns** | — (broke out, then never returned) | never returns |

`faulthandler.dump_traceback_later` every 60 s gives the same stack on every dump from the moment
iteration 3 begins:

```
Thread 0x0000bcd0 (most recent call first):
  File "...\A57-shadow-trees\code\lpbox.py", line 417 in solve      # self.h.run()
  File "...\A57-shadow-trees\code\lpbox.py", line 846 in run        # obj = M.solve(), top of the iteration
  File "...\A57-shadow-trees\code\caselp.py", line 337 in solve_node
```

**It is inside HiGHS.** Not column generation (`RowOracle.search` costs 14–19 s and is off-stack),
not the certifier (never reached — `certify.py` is a child process and none was ever spawned; the
reaper confirmed zero orphans all night), not `pinguard`.

The two shard runs differ only in *which* `M.solve()` they died in, and both are the same call:

* **00:48** printed `  time limit`, so it broke out of the loop and died in the **final,
  unconditioned** `obj = M.solve()` at `lpbox.py:908`;
* **03:02** printed no `time limit` line — iteration 2 ended at t = 239.x, just under the 240 s
  cap — so it went round again and died in the **in-loop** `M.solve()` at `lpbox.py:846`.

The repro reproduces the 03:02 variant. That the two entry points behave identically is the
point: the hang is a property of the LP handed to HiGHS after iteration 2's 946-row addition
(18,650 rows × 4,227 columns), not of the post-time-limit code path.

## Why it can spin forever, and why it is silent and single-threaded

`LPModel.__init__` sets exactly two HiGHS options (`lpbox.py:265-266`):

```python
self.h.setOptionValue("output_flag", False)
self.h.setOptionValue("threads", 1)
```

**No `time_limit` option is ever set on the `Highs` object** — `grep setOptionValue lpbox.py`
returns those two lines and `simplex_strategy` at :414, nothing else. `solve_node`'s
`time_limit` is checked only **between** iterations (`lpbox.py:906`), so it can never interrupt a
call already inside `h.run()`. That explains all three observed symptoms at once: `threads = 1`
→ one thread at 100 %; `output_flag = False` → not a byte of progress output; no `time_limit` →
unbounded.

`M.solve()` also has a retry (`lpbox.py:419-425`): a non-optimal status clears the solver and
re-runs from cold. Its diagnostic goes to **stdout**, and `logs/k5_16_interior_G1_s0.out` is
**0 bytes** — so HiGHS never returned a status at all on either wedged run. It is stuck in the
first `run()`, not looping the retry.

## Recommendation for the resume block

**Do not resume `k5_16` shard 0 as it stands** — it re-picks `Y0381` on every start (it is absent
from `done`) and re-wedges, exactly as PAUSED.md §5a says.

1. **The one-line guard** (`lpbox.py`, beside the two options at :266):

   ```python
   self.h.setOptionValue("time_limit", float(os.environ.get("LPBOX_HIGHS_TIME_LIMIT", 900)))
   ```

   This bounds every `h.run()` and turns an infinite spin into a status the code already
   notices. **It is one line but it is not the whole fix**, and the next owner must decide the
   second half before shipping it: on a time-limited exit HiGHS returns the incumbent objective,
   `lpbox.py:419` re-solves cold (another 900 s), and `res["tau"]` is then set from a
   **non-optimal** LP. A `tau` below the true optimum would manufacture a kill, so a
   `kHighsModelStatus.kTimeLimit` exit must be propagated as CAP-not-a-verdict rather than
   flowing into `rec["tau"]`. Until that is written, prefer (2).

2. **The zero-code unblock, and what A124 actually recommends for the resume:** run each shard
   under a per-node process wall, the way `code/recheck124.py` does here — a watchdog thread that
   records the node as `WALL-CAP` (**in the driver's own ledger only**, never in the campaign's,
   so the node stays re-checkable) and calls `os._exit`, with a supervisor that restarts the
   worker. It needs no edit to any frozen driver, it bounds *every* node rather than only this
   one, and it ran all day here without incident.

3. If shard 0 must move before either lands: `tree57` skips a node iff its id appears in
   `results/tree_k5_16_interior_G1_s0.jsonl` (`tree57.py:419-425`), and it has no skip list —
   `defer()` writes `deferred_*.jsonl` but nothing ever reads it. So the minimal manual step is
   to append **one** row for `Y0381` carrying an explicit non-verdict cert (`CAP`, `tau: null`),
   and to record the node as owing a re-solve. That is a campaign bookkeeping decision, so A124
   has **not** written it — no A124 process wrote anything into A57's results.

## Open question worth one measurement

Iteration 2's own solve already cost 126–150 s against 1 s and 9 s for iterations 0 and 1, on a
matrix that grew by 946 rows. The blow-up looks like degeneracy in the dual simplex after a large
row addition (`set_strategy(1)` is selected at `lpbox.py:883` whenever rows were added and columns
were not). Re-running this node once with `simplex_strategy` forced to 4 (primal), or with
`max_rows_add` cut from 2000 to ~200, would say whether the node is intrinsically hard or whether
the strategy heuristic picks the wrong side on a large row batch. That is a one-node experiment
and it may be worth more than the guard, because the same heuristic runs on every node.
