# A156 — day shift on the A57 tree's queued LP jobs (2026-09-08)

Owner: A156 (Opus campaign owner). Opened 2026-09-08 11:15 PDT, on the PI's day-shift box
(PI at work over remote desktop; the box's threads are mostly released to the lab).

## Task (as briefed)

1. **Drain the A57 emission LP queue** — `attempts/A137-night-shift-2/results/queue_bc.json`
   (2,184 jobs at emission; 1,988 unclaimed/unrecorded at hand-over). These are *fresh level-1/2/3
   children already emitted through the deployed hooks*: `pinguard.classify` at the **exact** pin
   cores (T5/T5′) → `trim57.trim_box` (T5″, persisted) → `pinclip.clip_node` at the same exact core
   (T5‴, persisted) → polygon-vs-pin-core kill (T5⁗, persisted) → **the LP on the clipped box with
   the exact cores in the certificate and the FROZEN `verify_case.py` (sha 521cb01f) as arbiter**.
   `verify_case_v3` only where the frozen verifier FAILs with holes, recorded separately.
2. **Deepen** on alive level-2/3 nodes, per PAUSED.md v3 §E's resume order.
3. At the end of the window (PI instruction, or 23:00 local, whichever comes first): pause via the
   sentinel, drain, reap, zero A57 processes, write `attempts/A57-shadow-trees/PAUSED.md` **v4**,
   commit and push with explicit pathspecs.

## Box discipline (binding, in force from the coordinator's 11:20 amendment)

* **≤ 16 lab python processes on the box, total** — A156's workers + A149's 4 LP processes +
  A151/A152/A153/A154/A155's light geometry. Counted from the command line (processes under
  `C:\Users\esumm\code\packing`), re-counted before every launch and hourly.
* **ProcessorAffinity = 0xFFFF** (logical CPUs 0–15, the P-cores) on every lab python process,
  workers and the children they spawn. CPUs 16–19 (the E-cores) belong to the PI's remote session.
  Children inherit the parent's mask on Windows; `code/affinity156.ps1` re-applies it hourly over
  *every* lab python process, including the other chores'.
* 5 A156 workers is the ceiling, not the target: the scaler adds one at a time, only when the box
  count leaves room for the worker **and its one node child**.
* Normal priority (A149's re-emission runs BelowNormal; this lane is the campaign's critical path).
* Per-node **process** wall 1,500 s. `WALL-CAP` is **never a verdict** — the node keeps its prior
  state and is left unclaimed.
* Memory gate before every LP: free physical > 3,072 MB **and** free commit > 6,144 MB, else hold.
* BLAS pinned to one thread per child; `PYTHONDONTWRITEBYTECODE=1`.

## What A156 may and may not touch

* `tree57.py`, `lpbox.py`, both frozen verifiers, `emit135.py`, `pinguard.py`, `pinclip.py`,
  `trim57.py`, `polycore.py`, `exactcore.py`: **imported unchanged, never edited**. A156's code is
  wrappers only.
* A137's `node137.py` is the LP child and is used **unmodified**; `run156.py` is a re-based copy of
  `run137.py` (A137's own `PAUSE` sentinel is set and must not be deleted, so this attempt needs
  its own sentinel base, its own claims and its own progress).
* Sentinel: `attempts/A156-day-shift/PAUSE` (scoped, PAUSED.md v2 §7a). **A57's own PAUSE and
  A137's PAUSE are reported and never touched**; no pidfile of any other chore is deleted.
* Certificates go to `attempts/A156-day-shift/certs/`; result rows to
  `attempts/A156-day-shift/results/lp156_*.jsonl`. Nothing is written into A57's canonical
  `tree_*.jsonl` (`sync137.py` remains the only writer, and A156 does not run it).

## Soundness tripwires — PAUSE IMMEDIATELY and report first

A core half-side beyond its certified value; a tilt bin outside [0, 90]; a stored verdict
contradicted on replay; a clipped box not inside its parent. (`emit137.py` raises `SystemExit` on
the first three at emission; `code/audit156.py` re-checks the day's rows.)

## Layout

```
code/run156.py        supervisor: claims, memory gate, 1,500 s process wall, own sentinel
code/mkqueue156.py    rebuilds results/queue156.json from A137's emitq_*.json minus recorded/claimed
code/launch156.ps1    pidfile-gated launcher (refuses on a live pidfile, refuses over the box cap)
code/scale156.ps1     one launch per pass up to 5 workers; hourly affinity sweep; deadline-aware
code/affinity156.ps1  ProcessorAffinity = 0xFFFF over every lab python process
code/parents156.py    builds the deepen parent list from alive level-2/3 nodes
code/status156.py     live kill table by level and leaf, and the measured level-2 geometry rate
code/audit156.py      replays the day's tripwires over every row A156 wrote
```
