# A162 — the gallery status board (2026-09-08)

Owner: A162 (Opus engineer). Opened 2026-09-08 on the PI's box.

## Task (as briefed)

The PI reviews `docs/shadows/k0v4/` (11 k0 cells) and `docs/shadows/a57v4/` (60 A57/A60 nodes) and
wants to see **at a glance how much residue is left and where**. Build
`docs/shadows/status_gallery.py` — rerunnable, idempotent, **no LP** — that:

1. **Collects every kill record in the repo into one table** `node -> (dead?, leaf, attempt,
   certificate path, date)`, from:
   * A137's supersession files and its fold-in of A131/A135/A141/A142/A145 —
     `attempts/A137-night-shift-2/results/`, `attempts/A57-shadow-trees/results/superseded_by_*.jsonl`,
     `attempts/A60-trump5-campaign/results/superseded_by_*.jsonl`, and `PAUSED.md` v3 addenda;
   * A149's `superseded_by_exactcore_A149.jsonl` (+ the a60 / v3 ledgers) and the day149 records;
   * A156's records (`attempts/A156-day-shift/results/`) and the tree jsonl it appends;
   * A136's closures (`attempts/A136-a120-resume/results/closures136.jsonl`,
     `attempts/A96-a57-parametric/results/a120_closures.jsonl`);
   * A140's `exactcore140.jsonl` (k0: `s3_far`);
   * A141's `polycore_lane_kills.jsonl` (k0 cells + A57/A60 slots);
   * A158's certs — **`c0_Y0076`'s NO child is NOT a kill**;
   * every `*.clipkill.json` under `attempts/*/certs/**` (A148's rule: clipkill files are kill
     records; `*__exall.json` are **not**).
   Apply A137's **"an id is not a node"** rule (L1 vs G1 trees: match on the record's *tree tag*,
   not the bare id) and **monotonicity** (a killed node kills its descendants).
2. **Decides ALIVE or DEAD per gallery page** (with the killing leaf and attempt); moves DEAD pages
   into `docs/shadows/<gallery>/killed/` (**`git mv`, never delete**), leaves ALIVE pages in place,
   and writes `docs/shadows/STATUS.md`: a checklist per gallery (page, node, class, level, family,
   status, leaf, attempt, date, subtree cost from A142's ranking), counts alive/dead per gallery and
   by family and by leaf, and a one-paragraph **"residue left"** summary with the total alive across
   the tree populations (A57 work-owing from the latest `PAUSED.md`, A60 alive, k0 cells).
   *The PI reads this file first.*
3. **Runs it now** against the current records and reports the counts; documents in the README of
   each gallery that killed pages live in `killed/` and `STATUS.md` is the checklist.
4. **Makes it safe for others to run**: no writes outside `docs/shadows/`, a `--dry-run` flag, and a
   one-line usage note in `attempts/A57-shadow-trees/PAUSED.md` so the shift owners run it at every
   pause.

## Rules (binding)

* **Read-only on every campaign and attempt** except the moves inside `docs/shadows/` and the named
  appends (`docs/shadows/STATUS.md`, the two gallery READMEs, `attempts/A57-shadow-trees/PAUSED.md`
  usage line, `attempts/REGISTRY.md`, `LOG.md`).
* No recursive deletes. `PYTHONDONTWRITEBYTECODE=1` (set in-process as well).
* git = fetch + plain merge + `git commit -- <pathspecs>` only. Never `git add` then `git commit`
  as two steps (A137 §D.7: the shared index).
* No LP is solved. Every verdict is *read* from an existing record.

## Soundness rules the collector enforces (and why)

| rule | why |
|---|---|
| a kill needs a **converged** bound or a certificate `PASS` | A124/A158: `converged = false, dead_unconverged = true` records whose stored `tau < budget` were never a bound (A140's `l1_148`, `l2_p65_101`, `l2_p65_111` are exactly this) |
| `kill-candidate`, `NO-KILL`, `LOST-KILL-ON-RESOLVE`, `TOO-TIGHT`, `WALL-CAP`, `FAIL` are **not** kills | A137 §C.1, §D.5 — `WALL-CAP` is never a verdict |
| A158's `yescert158.jsonl` `verdict = "KILL"` is **not** a kill when `kill = false` | A158: `1 + LANE + M = 2` on every measured cell; 0 of 141 cells kill the YES child |
| `*__exall.json` is never a kill record | A148's rule: it exists on LOST-KILL / TOO-TIGHT / FAIL too |
| a kill applies only to the **tree tag** it was computed at | A137 §C.3 |

## Layout

```
code/                (none — the deliverable lives at docs/shadows/status_gallery.py)
results/status162.json   the machine-readable dump the run writes (a copy of the table)
notes/method.md      the tag-resolution and monotonicity rules as implemented
logs/run.log         the run's stdout
```
