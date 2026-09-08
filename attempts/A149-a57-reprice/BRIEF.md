# A149 — re-price A57 in the budget's own model, and continue the exact-core re-emission

Owner: A149 (Opus engineer). Opened 2026-09-08 07:00 PDT, immediately after A137's night shift
(`b91a2813`). Two tasks, run in parallel.

## Context handed down

A137's night (`attempts/A57-shadow-trees/PAUSED.md` v3, `attempts/A137-night-shift-2/results/`,
`notes/method.md`) measured, on 3,034 fresh children:

* **26.3 % die by geometry before any LP** (level 2: **27.5 %**), against the **13.7 %** that
  `docs/budget.md`'s 10.5–11.7 wall-day schedule assumed;
* level-1 children that reach the LP are certified dead at **78.8 % of decided**;
* the exact-pin-core re-emission certifies **28.6 % of re-solved ALIVE nodes** under the FROZEN
  verifier (46 of 161 decided, 15.5 CPU-h).

The **work-owing population is 406**: 142 un-re-solved ALIVE nodes in A145's `frac_exact` order,
plus the FAILs, plus 2,184 queued LP jobs (`attempts/A137-night-shift-2/results/queue_bc.json`,
1,988 still unrecorded/unclaimed).

## Task A — RE-PRICE A57 in `docs/budget.md`'s own model

Recompute A57's CPU-h and wall-days at 5 workers from the night's *measured* per-level geometry
rates, LP kill rates and exact-core rate, using §B's per-level cost anatomy and A124's
`control124`/`schedule124` code (`attempts/A124-recheck-day/code/`), with the 406-node population
and the LP queue as the frontier. Give a central figure and a range, **state every assumption**,
and write the A57 row of `docs/budget.md` (central, range, wall-days, provenance, date) plus one
paragraph in section A, and update the two totals rows.

## Task B — DAY RE-EMISSION

Continue the exact-pin-core re-emission over the un-re-solved ALIVE nodes in `frac_exact` order,
through A137's code path (`attempts/A137-night-shift-2/code/node137.py` → A135's `emit135.certify`
→ FROZEN `verify_case.py`), certificates under this attempt. `verify_case_v3` only where the
frozen verifier FAILs with holes, recorded separately.

* **2** BLAS-pinned, `BelowNormal` worker processes (the PI is using the machine from 07:30);
* this attempt's **own** pausegate sentinel base (`attempts/A149-a57-reprice/PAUSE`); A57's own
  PAUSE stays as it is and is never touched; never launch shards;
* cap **12 CPU-h**, resumable;
* supersession rows in A137's ledger format under this attempt, plus one fold-in line in
  `PAUSED.md` v3.

## Rules in force

≤ 16 python processes on the box; read-only on every campaign and prior attempt except the named
appends (`docs/budget.md`, `PAUSED.md` v3); frozen verifiers byte-identical; per-LP process wall
1,500 s and **CAP is never a verdict**; no recursive deletes; never delete a pidfile or a
sentinel; `PYTHONDONTWRITEBYTECODE=1`; git = fetch + plain merge + `git commit -- <pathspecs>`
only (the shared index has swallowed other agents' files four times — never `add` then `commit`
without a pathspec on the commit).
