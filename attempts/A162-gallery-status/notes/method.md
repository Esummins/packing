# A162 method — how a gallery page gets a verdict

The deliverable is `docs/shadows/status_gallery.py`. It solves **no LP**. Every verdict is *read*
from a record that already exists on disk.

## 1. The node key

A gallery page is not an id. It is a **(camp, tree tag, id)** triple:

| gallery / camp | how the tag is read |
|---|---|
| A57 pages | the page's `record` column in `review_a57v4.csv` is `…/results/tree/<TAG>/<id>.json`, so the tag is literally in the path — `k5_11_interior_G1`, `k5_16_interior_L1`, `k5_11_interior_G1_D2`, … |
| A60 pages | one tree, `trump5_j0` |
| k0 cells | one tree, `k0_00` |

The canonical tag authority is A57's own `results/tree_<TAG>_s<shard>.jsonl` (the `_s<n>` shard
marker is stripped). Over the 3,160 distinct ids in that corpus, **300 ids live in more than one
tree** — which is exactly why the bare id is not a key.

## 2. Tag resolution for a record that does not name its tree (A137 §C.3)

In order, first that fires wins:

1. **`applies_to_tags` / `not_applicable_to_tags`** — A137's `fold137.py` writes these, so its
   ledgers are self-describing. This is what correctly restricts A142's two exact-clip kills
   (`k5_11_interior_Y0041_D02`, `k5_16_interior_Y0449`, written at
   `a_pin = 16777215/33554432 = 0.49999997` against the L1 tree's eps-fat pins) to the **L1** tree
   and off the G1 tree the live campaign is descending.
2. **the record's own prior `tau`** (`tau_before` / `prior_tau`) matched against the canonical
   per-`(tag, id)` `tau`, relative tolerance 1e-6, applied when exactly one tree matches. This is
   how A149's day-shift rows are placed: its `k5_11_interior_Y0275` row carries
   `tau_before = 4.999999999999965`, which is the **G1** record's `tau` to the last digit, while the
   L1 record of the same id sits at 3.9999999999999982.
3. **the id occurring in exactly one tree**.
4. otherwise **REFUSED** — listed in `STATUS.md`, never applied. A refusal cannot kill a page.
   All 58 current refusals are *redundant*: the same id is killed with an explicit tag by another
   record, so no node is left unattributed.

## 3. Monotonicity

A killed node kills its descendants:

* A57 — strip trailing `_D<nn>` repeatedly: `…_Y0036_D07_D04` → `…_Y0036_D07` → `…_Y0036`.
* k0 — `l3_ppNNN_a_b` → `l2_pNNN_a` → `l1_0NN` (aliased with `node_NN`, since the k0 corpus writes
  the same cell as `l1_071`, `node_71` and `l1_071_plain_warm`).

The descendant inherits the ancestor's leaf, marked `monotone descendant of <ancestor>`.

## 4. What counts as a kill, and what deliberately does not

| counts | does not count |
|---|---|
| a tree-jsonl `cert` of `PASS` or `KILL-BY-LOGIC …` | `ALIVE-at-LP …`, `FAIL(…)` (any rc, `eps_geo`, `LOST-KILL-ON-RESOLVE`, `TOO-TIGHT`) |
| a supersession-ledger row (A131/A135/A137/A141/A142/A145/A149 fold-ins) | `WALL-CAP` — never a verdict (A137 §D.5) |
| `result == "PASS"` in A149's / A156's re-emission rows | `NO-KILL`, `kill-candidate`, `NOT-RUN` |
| `status == "CLOSED"` in A136's / A96's A120 closures | A96's `NOT-RUN (A120 CPU cap)` rows |
| A140's `exactcore140` row **only** with `kills` **and** `kills_converged` **and** `cert.result == "PASS"` | A140's `l1_148`, `l2_p65_101`, `l2_p65_111`: `kills = true` with `converged = false` — A124: a non-converged `tau` was never a bound |
| A141's `verdict` starting `DEAD BY POLYCORE …` | — |
| every `*.clipkill.json` under `attempts/*/certs/**` (A148's rule) | every `*__exall.json` — it exists on LOST-KILL / TOO-TIGHT / FAIL too |
| — | A158's `yescert158.jsonl` rows: `verdict = "KILL"` with `kill = false`; the conditional lane leaf reached `1 + LANE + M = 2` on every cell, 0 of 141 kill the YES child |
| — | A158's `no158.jsonl` NO-child rows, **`c0_Y0076` included**: A158b ran the YES child as an LP node and it converges at `tau = budget`, `eta = 0`, so the split is structurally neutral, not a kill |

## 5. Safety

* `_guard()` refuses any write or move target outside `docs/shadows/`. The only path that may leave
  that directory is the opt-in `--json PATH` dump, which is off unless asked for.
* DEAD pages are moved with `git mv`; on an untracked page it falls back to `os.replace`. There is
  no `unlink`, no `rmtree`, no recursive delete anywhere in the file.
* An ALIVE page found sitting in `killed/` is moved back out, so a record that is later corrected
  un-kills its page on the next run.
* `sys.dont_write_bytecode = True` and `PYTHONDONTWRITEBYTECODE=1` are set in-process.
* Rerunnable and idempotent: a second run with the same records reports `already in killed/` and
  `README already current`, and rewrites only `STATUS.md` (whose only change is its timestamp).

## 6. Result of the 2026-09-08 run

`k0v4` 11 pages: **11 ALIVE, 0 DEAD**. `a57v4` 60 pages: **57 ALIVE, 3 DEAD** —
`k5_16_interior_Y0083` (tree `k5_16_interior_L1`, A57's own tree certificate `PASS`; the `G1` node
of that id is still alive), `k5_11_interior_Y0275` and `k5_16_interior_Y0275` (both tree `…_G1`,
A149's exact-core kills under the frozen `verify_case.py`).
