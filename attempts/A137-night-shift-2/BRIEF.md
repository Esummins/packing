# A137 — night shift 2: resume A57 with the day's geometric levers deployed — exact pin cores, pin-clip and the polygon logic kill at emission, the backlog folded in — then pause cleanly (Opus, campaign owner for one night)

DO NOT START until the coordinator confirms the PI has released the machine for the night (the shift is ~8 h).

Context (2026-09-07 evening). A57 has been paused since 2026-09-06 00:45 except for A123's night (3 shards, 296
children). Today produced, in order of value for the resume:
1. **Exact pin cores** (A135 `b65073e7`): the frozen verifiers take the core half-side `a` verbatim (soundness is the
   emitter's obligation); the exact pin core is 1/2 − δ/√2 = 0.492928902 (rational `33873816211/68719476736`) against
   the stock 0.489999969; two of A132's three in-vitro kills certify under the FROZEN verify_case with exact cores
   alone. Next chore named by A135: re-emit the ALIVE population with exact pin cores — 414 LP re-solves at 240 s ≈ 28
   CPU-h, no verifier or Lean change. `code/exactcore.py` certifies every half-side by A132's exact vertex test.
2. **Pin-clip T5‴** (A131 `43da8a3f`): the exact clip of the centre box to the pin-feasible region per tilt sub-bin;
   132 unclosed nodes already killed (certs in attempts/A131-pin-clip/certs/backlog/, ledger results/backlog_kills.jsonl);
   deployment shape in A131's notes/deploy.md (after T5″, before the LP; persist clip_from/clip_kept/clip_nsub/
   clip_pins/clip_delta; NEVER chain eps_geo after a clip — send a holed certificate to the resolver or to depth).
3. **Polygon logic kill T5⁗** (A132 `7d5e9070`, A135): K′(B) meets a pin core ⇒ dead; 64 nodes (37 new) in
   attempts/A135-polycore-verifier/results/polycore_kills.jsonl with certified witness points; single-witness Lean
   leaf `PolyCoreT5.lean`. Different test from T5″ (neither contains the other in general) — deploy both.
4. **verify_case_v3.py** (A135): the `polycores` clause for the conditioned box (Y1038-type kills); regression 24/24
   identical to v1; NOT frozen yet — use it only where the frozen verifier FAILS with holes and record such kills as
   "v3-certified" separately from frozen-certified ones.
5. A124's corrections (`97aa4e9c`): T5″'s projection stands (schedule 10.5–11.7 wall-days full-kills-only); the 900 s
   re-check is not a lever (stop it); Y0381 = `LPModel` sets no LP time limit — the per-node process wall (1,500 s) is
   the guard, CAP never a verdict; `recheck124.py` persists node jsons; the scoped sentinel `pausegate.paused(base=…)`
   (PAUSED.md v2 §7a) — other chores run under their own base while A57's sentinel is up.
6. Standing must-fixes (PAUSED.md v2): trim_excluded/trim_from persisted (A124's recheck124 does; make the shard
   emission do the same), launch.ps1 pidfile gate, stale pidfiles, certifier default rounds 6 / wall 2,600 s.

Read first: PAUSED.md v2 end to end (the resume block, §5(e)(f), §6, §7a, the lines A131/A135 appended), attempts/
A57-shadow-trees/notes/lemmas.md (T5′, T5″, T5‴, T5⁗), A131's notes/deploy.md, A135's notes and code/exactcore.py,
A132's notes/spec.md, A124's notes/y0381_hang.md, attempts/A96-a57-parametric/code/{trim57,pausegate,recheck96}.py,
attempts/A124-recheck-day/code/recheck124.py, attempts/A57-shadow-trees/code/{launch.ps1,scaleup.ps1,tree57.py,
deepen.py,pinguard.py}, docs/budget.md §A–B, and the lab ops laws (≤ 16 python processes on the box, BLAS pinned,
6144 MB commit gate and > 3 GB free physical before every LP, frozen verifiers byte-identical, no recursive deletes,
never delete a pidfile or another chore's sentinel, PYTHONDONTWRITEBYTECODE=1, git = fetch + plain merge + push own
paths with explicit pathspecs — the shared index has swallowed other agents' staged files twice today).

## T1 — fold-in and deployment (first hour; nothing launched until this is done)
1. Fold the day's kills into A57's state through the tree's own record format (you are the owner tonight): the 132
   pin-clip kills, the 64 polygon kills, A135's 3 certified LP kills, A124's 54 trim-empty ALIVE nodes — each as a
   record carrying the certificate path and the leaf type; children of a killed node are dead with it (monotonicity,
   A124: all 24 L4 children of the three Y0036 L3 nodes). Re-derive the state counts vs PAUSED.md v2 and print them.
2. Emission hooks, in this order at every new child: pinguard (T5′ tight core, with the pin cores EXACT via
   exactcore), T5″ trim, T5‴ clip (persisted), T5⁗ polygon-vs-pin-core kill (witness persisted), then the LP on the
   clipped box with EXACT cores in the certificate. Verify on the first 20 children that every record carries the new
   fields and that the frozen verifier passes the exact-core certificates (it did for A135's; confirm on live
   emission). Keep the shadow scheduler and region-tree options OFF. Certifier rounds 6 / wall 2,600 s.
3. Y0381 guard: per-node process wall 1,500 s (never a verdict); do not edit lpbox.py.
4. launch.ps1 pidfile gate and stale pidfiles per PAUSED.md v2; select96 before the A96 drivers.

## T2 — the run (until ~08:00)
Priority order for the LP slots (5 workers if the box allows, else 4): (a) the exact-pin-core re-emission of the
ALIVE population that survives T1's fold-in (A135's 28 CPU-h chore; it is a strict lower bound on what v3 would do and
needs no new verifier), (b) fresh level-1/level-2 emission through the new hooks on the shards, (c) deepen on the
alive L2/L3 nodes (the first live test of the level-2 rate the schedule rests on — A124). Hourly from the logs only:
rows by level, kills by leaf (T5, T5′, T5″, T5‴, T5⁗, PASS-frozen, PASS-v3, FAIL→resolver, ALIVE), verify timeouts,
orphans reaped, free physical. If free physical < 3 GB twice, stop one worker via the sentinel path. Do not change a
lever mid-run.

## T3 — pause and report (08:00–08:30)
PAUSE sentinel at 08:00; wait for in-flight nodes; reap; confirm zero A57 processes; PAUSED.md v3 (state counts vs v2,
the night's rows and kills by level and leaf — exact-core re-emission kills separately, and the level-2 deepen rate vs
the 13.7% the schedule assumes; incidents); commit and push own paths; registry row; LOG.md; docs/budget.md A57 row
(the measured level-2 rate and the exact-core kill rate — the two numbers that move the schedule). Report ONCE at the
pause: the kill table first, the level-2 rate and the exact-core rate second, incidents third, pointers last. Hard
rules: never launch anything after 08:15; if anything looks unsound (a core half-side beyond its certified value, a
bin outside [0, 90], a stored verdict contradicted on replay, a clipped box not inside its parent), PAUSE and report
that first.
